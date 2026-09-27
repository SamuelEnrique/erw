#!/usr/bin/env python3
"""Write "Energy Week", the weekly brief: docs/weekly/YYYY-Www.md and docs/weekly/latest.md.

Energy Research Warehouse (ERW), platform tool 14, session 17.

    python warehouse/news/weekly.py                    # the ISO week that contains yesterday (UTC)
    python warehouse/news/weekly.py --week 2026-W39

The week is an ISO week, Monday 00:00 to Monday 00:00 UTC, cut at the time of the run. The
scheduled run (Mondays 13:00 UTC, .github/workflows/weekly-brief.yml) therefore writes the
week that ended the night before; a run on any other day writes the week so far and says so.

Sections:
  1. The five stories of the week: the five clusters (score.py's cluster_id) with the highest
     significance among the week's scored stories, as in the daily digest.
  2. The week's deals: every row of energy_deals whose event_date falls in the week.
  3. The week's datacenter announcements: every row of datacenter_projects first reported in
     the week (first_story_at).
  4. Numbers of the week, read from the warehouse through the erw package, each with its table:
     the day-ahead average per ISO main hub over the ISO's local week and the change from the
     week before (both weeks must be complete); the week's highest real-time price and where;
     Henry Hub, WTI and Brent: the last close of the week, the last close before it, and the
     change; US48 peak demand of the week with its hour.

Who writes what, as in the daily digest (warehouse/news/brief.py): the model writes only the
five headlines (one call, JSON schema). The one-line whys are the stories' own scored why
lines. Every number is the warehouse's, or a difference or mean of the warehouse's numbers
computed here and labeled; a number the warehouse does not hold is reported as missing.
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import anthropic
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brief  # noqa: E402  (the daily digest: clusters, headlines, citations, hubs, fuels)
from brief import FUELS, MAIN_HUBS, RT_TZ, ROOT, cite_short, erw, ip, link_text, NAME, NEWS_COLS  # noqa: E402
from score import PRICES, pick_model  # noqa: E402

WEEKLY_DIR = os.path.join(ROOT, "docs", "weekly")


def read_table(name):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def week_bounds(week, now):
    """(label, start, end of the ISO week, cut: min(end, now)) in UTC."""
    if week:
        y, w = week.split("-W")
        start = pd.Timestamp(dt.date.fromisocalendar(int(y), int(w), 1), tz="UTC")
    else:
        ref = (now - pd.Timedelta(days=1)).date()
        y, w, _ = ref.isocalendar()
        start = pd.Timestamp(dt.date.fromisocalendar(y, w, 1), tz="UTC")
    y, w, _ = start.date().isocalendar()
    end = start + pd.Timedelta(days=7)
    return f"{y}-W{w:02d}", start, end, min(end, now)


def local_week(start, tz):
    """The ISO's local week with the same dates as the UTC week: (start, end) local midnights."""
    s = pd.Timestamp(start.date()).tz_localize(tz)
    e = pd.Timestamp((start + pd.Timedelta(days=7)).date()).tz_localize(tz)
    return s, e


def dam_week(label, table, node, tz, start, log):
    """(mean, n, expected) of the hub's day-ahead prices over the local week, or None if absent."""
    s, e = local_week(start, tz)
    try:
        df = erw.fetch(table, start=s, end=e, node=node)
    except Exception as exc:
        log(f"  numbers: {table} unavailable: {exc!r}")
        return None, 0, int((e - s) / pd.Timedelta(hours=1))
    return (df["value"].mean() if len(df) else None), len(df), int((e - s) / pd.Timedelta(hours=1))


def numbers(start, cut, log):
    L = ["Every number below is read from the warehouse through the `erw` package, with its table; "
         "a change is this week's number minus last week's, computed here. Intervals are interval starts."]
    prior = start - pd.Timedelta(days=7)
    L += ["", "**Day-ahead average, main hub, over the ISO's local week, and the change from the week before**", "",
          "| ISO | Hub or zone | This week USD/MWh | Week before USD/MWh | Change | Table |", "|---|---|---|---|---|---|"]
    for label, table, node, tz in MAIN_HUBS:
        m1, n1, x1 = dam_week(label, table, node, tz, start, log)
        m0, n0, x0 = dam_week(label, table, node, tz, prior, log)
        this = f"{m1:.2f}" if n1 == x1 else f"not in the warehouse ({n1} of {x1} hours)"
        last = f"{m0:.2f}" if n0 == x0 else f"not in the warehouse ({n0} of {x0} hours)"
        chg = f"{m1 - m0:+.2f}" if n1 == x1 and n0 == x0 else "not computed"
        L.append(f"| {label} | {node} | {this} | {last} | {chg} | {cite_short(table) if n1 or n0 else f'`{table}`'} |")
    L.append("| PJM | | | | | no PJM price table (no API key) |")

    # the week's highest real-time price, over UTC bounds, from the interval price tables
    best, covered = None, []
    rt = [t for t in erw.filter(market="rtm") if re.fullmatch(r"[a-z]+_rtm_(hub|zone)_prices(_hourly)?", t)]
    for table in rt:
        try:
            df = erw.fetch(table, start=start, end=cut)
        except Exception as exc:
            log(f"  numbers: {table} unavailable: {exc!r}")
            continue
        if df.empty:
            continue
        covered.append(f"{table} to {df['ts_utc'].max():%Y-%m-%d %H:%M} UTC")
        top = df.loc[df["value"].idxmax()]
        if best is None or top["value"] > best[0]["value"]:
            best = (top, table)
    L += ["", "**Highest real-time price of the week:** "]
    if best:
        top, table = best
        tz = RT_TZ.get(table.split("_")[0], "UTC")
        L[-1] += (f"{top['value']:.2f} USD/MWh at {top['node']} ({table.split('_')[0].upper()}), interval starting "
                  f"{top['ts_utc'].tz_convert(tz):%Y-%m-%d %H:%M} local ({top['ts_utc']:%Y-%m-%d %H:%M} UTC), "
                  f"`{top['variable']}`; {cite_short(table)}. Tables read, and how far each reaches this week: "
                  + "; ".join(covered) + ".")
    else:
        L[-1] += "no real-time table covers this week."

    L += ["", "**Fuel spot prices, weekly change** (EIA, trading dates; the last close of the week and the last "
          "close before it):", "", "| Price | Last close this week | Last close before | Change | Table |",
          "|---|---|---|---|---|"]
    try:
        fuel = erw.fetch("eia_fuel_spot_prices")
        for label, entity in FUELS:
            s = fuel[fuel["entity"] == entity].sort_values("ts_utc")
            wk = s[(s["ts_utc"] >= start) & (s["ts_utc"] < cut)]
            before = s[s["ts_utc"] < start]
            if wk.empty or before.empty:
                L.append(f"| {label} | not in the warehouse (no close this week yet; newest "
                         f"{s['ts_utc'].max():%Y-%m-%d}) | | | `eia_fuel_spot_prices` |")
                continue
            a, b = wk.iloc[-1], before.iloc[-1]
            L.append(f"| {label} | {a['value']:.2f} {a['unit']} on {a['ts_utc']:%Y-%m-%d} | {b['value']:.2f} on "
                     f"{b['ts_utc']:%Y-%m-%d} | {a['value'] - b['value']:+.2f} ({100 * (a['value'] / b['value'] - 1):+.1f}%) "
                     f"| {cite_short('eia_fuel_spot_prices')} |")
    except Exception as exc:
        log(f"  numbers: fuel prices unavailable: {exc!r}")
        L.append("| fuel prices | not in the warehouse | | | |")

    L += ["", "**US48 peak demand of the week:** "]
    try:
        d = erw.fetch("eia930_us48_demand", start=start, end=cut)
        d = d[d["variable"] == "demand_mw"]
        if d.empty:
            L[-1] += "not in the warehouse for this week."
        else:
            top = d.loc[d["value"].idxmax()]
            L[-1] += (f"{top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC "
                      f"({top['ts_utc'].tz_convert('America/New_York'):%A %Y-%m-%d, %H:%M} Eastern), from "
                      f"{d['ts_utc'].nunique()} hours of the week to {d['ts_utc'].max():%Y-%m-%d %H:%M} UTC; "
                      f"{cite_short('eia930_us48_demand')}.")
    except Exception as exc:
        log(f"  numbers: US48 demand unavailable: {exc!r}")
        L[-1] += "not in the warehouse."
    return L


def num(v, fmt="{:,.0f}"):
    return fmt.format(float(v)) if v not in ("", None) else "not stated"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW weekly brief, Energy Week")
    ap.add_argument("--week", help="ISO week YYYY-Www (default: the week that contains yesterday, UTC)")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_weekly_{run_id}.log"))
    status = dict(table="weekly", market="brief", status="ok", detail="")
    try:
        now = pd.Timestamp.now(tz="UTC")
        label, start, end, cut = week_bounds(args.week, now)
        partial = cut < end
        df = ip.read_series(os.path.join(ip.OUT_DIR, NAME + ".csv"), NEWS_COLS)
        when = pd.to_datetime(df["event_date"], utc=True)
        s = df[(df["scored_at"] != "") & (when >= start) & (when < cut)].copy()
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        s = s[s["sig"] > 0]
        log(f"week {label}: [{ip.utc_iso(start)}, {ip.utc_iso(cut)}), {len(s)} scored energy stories")
        if s.empty:
            raise RuntimeError("no scored stories in the week; not writing an empty brief")
        clusters = brief.build_clusters(s)
        top5 = clusters.head(5)
        client = anthropic.Anthropic(api_key=ip.load_key("ANTHROPIC_API_KEY", log))
        model = pick_model(client, log)
        heads, u, calls = brief.headlines(client, model, top5, log)
        if set(top5["cluster_id"]) - set(heads):
            raise RuntimeError("headlines missing for some clusters")
        cost = (f"USD {(u.input_tokens * PRICES[model][0] + u.output_tokens * PRICES[model][1]) / 1e6:.4f}"
                if model in PRICES else "unknown")
        log(f"  headlines from {model}: tokens in {u.input_tokens} out {u.output_tokens}; cost {cost}")

        span = (f"{start:%Y-%m-%d} to {(end - pd.Timedelta(days=1)):%Y-%m-%d}" +
                (f", so far (to {cut:%Y-%m-%d %H:%M} UTC)" if partial else ""))
        L = [f"# Energy Week, {label}", "",
             f"The Energy Research Warehouse (ERW) weekly brief for {span}: {len(s)} scored stories in "
             f"{len(clusters)} clusters. Headlines are written by the model ({model}); the why lines are the "
             "stories' scored fields; deals and datacenters come from the ERW's extracted tables; every number "
             "under Numbers of the week comes from the warehouse.", "", "## The five stories of the week", ""]
        for i, r in enumerate(top5.to_dict("records"), 1):
            L.append(f"{i}. **{heads[r['cluster_id']]}** (significance {r['sig']}, {r['sector']}, {r['n']} "
                     f"{'story' if r['n'] == 1 else 'stories'})  ")
            L.append(f"   {r['why']} Sources: {link_text(r['links'])}")

        L += ["", "## Deals of the week", ""]
        deals = read_table("energy_deals")
        if deals is None:
            L.append("- energy_deals is not in the warehouse on this machine.")
        else:
            dw = deals[(pd.to_datetime(deals["event_date"], utc=True) >= start)
                       & (pd.to_datetime(deals["event_date"], utc=True) < cut)].sort_values("event_date")
            if dw.empty:
                L.append("- no deal in `energy_deals` is dated this week.")
            else:
                L += ["| Date | Type | Buyer | Seller | Asset | MW | US dollars | Status | Story |",
                      "|---|---|---|---|---|---|---|---|---|"]
                for r in dw.to_dict("records"):
                    first = r["story_urls"].split(";")[0]
                    L.append(f"| {r['event_date'][:10]} | {r['deal_type']} | {r['buyer'] or 'not stated'} | "
                             f"{r['seller'] or 'not stated'} | {r['asset'] or 'not stated'} | {num(r['mw'])} | "
                             f"{num(r['dollars'])} | {r['status'] or 'not stated'} | [1]({first}) |")
                L.append("")
                L.append(f"Table: `energy_deals` ({len(dw)} deals; extracted from the scored stories by "
                         "`warehouse/deals/extract.py`, every number checked against its story).")

        L += ["", "## Datacenter announcements of the week", ""]
        dc = read_table("datacenter_projects")
        if dc is None:
            L.append("- datacenter_projects is not in the warehouse on this machine.")
        else:
            t = pd.to_datetime(dc["first_story_at"], utc=True)
            cw = dc[(t >= start) & (t < cut)].sort_values("first_story_at")
            if cw.empty:
                L.append("- no datacenter facility in `datacenter_projects` was first reported this week.")
            else:
                L += ["| First reported | Operator | Site | Place | MW | Status | Story |", "|---|---|---|---|---|---|---|"]
                for r in cw.to_dict("records"):
                    place = ", ".join(x for x in (r["city"], r["county"], r["state"]) if x) or "not stated"
                    L.append(f"| {r['first_story_at'][:10]} | {r['operator'] or 'not stated'} | "
                             f"{r['site_name'] or 'not stated'} | {place} | {num(r['mw'])} | "
                             f"{(r['project_status'] or 'not stated').replace('_', ' ')} | "
                             f"[1]({r['story_urls'].split(';')[0]}) |")
                L.append("")
                L.append(f"Table: `datacenter_projects` ({len(cw)} facilities; `warehouse/datacenters/extract.py`, "
                         "every field only as its story states it).")

        L += ["", "## Numbers of the week", ""] + numbers(start, cut, log)
        L += ["", "---", "", f"Generated by `warehouse/news/weekly.py` at {now:%Y-%m-%d %H:%M} UTC; run log "
              f"`warehouse/output/logs/news_weekly_{run_id}.log`."]
        os.makedirs(WEEKLY_DIR, exist_ok=True)
        path = os.path.join(WEEKLY_DIR, f"{label}.md")
        text = "\n".join(L) + "\n"
        for p in (path, os.path.join(WEEKLY_DIR, "latest.md")):
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        status["detail"] = f"{label}: {len(s)} stories, {len(clusters)} clusters, headline cost {cost}"
        log(f"wrote {os.path.relpath(path, ROOT)} and latest.md; {status['detail']}")
        print(f"weekly: {os.path.relpath(path, ROOT)}; {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"news_weekly FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("news_weekly", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
