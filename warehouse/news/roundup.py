#!/usr/bin/env python3
"""Write the Energy Roundup, the weekly brief: docs/roundup/YYYY-Www.md and docs/roundup/latest.md.

Energy Research Warehouse (ERW), platform tool 14. Session 17 built it as "Energy Week"
(warehouse/news/weekly.py, docs/weekly/, Mondays 13:00 UTC); session 23 renamed it the Energy
Roundup and moved it to Sundays at 23:00 UTC (4 PM Pacific), when it is written and sent.
The Energy Week files already in docs/weekly/ stay there as they were written.

    python warehouse/news/roundup.py                    # the ISO week that contains yesterday (UTC)
    python warehouse/news/roundup.py --week 2026-W39

The week is an ISO week, Monday 00:00 to Monday 00:00 UTC, cut at the time of the run. The
scheduled run (Sundays 23:00 UTC, .github/workflows/roundup.yml) therefore writes the week
from Monday to that Sunday evening and says where it was cut; a run on Monday writes the week
that ended the night before.

Sections:
  0. Weekend (session 23): the daily digest is written Monday to Friday only, so the Roundup
     opens with the top three clusters among the stories published on the week's Saturday and
     Sunday (UTC), ranked as in the digest.
  1. The five stories of the week: the five clusters (score.py's cluster_id) with the highest
     significance among the week's scored stories, as in the daily digest, leaving out the
     clusters already shown under Weekend (each section takes only clusters not shown above it,
     as in the digest, session 21 ruling 5).
  2. The week's deals: every row of energy_deals whose event_date falls in the week.
  3. The week's datacenter announcements: every row of datacenter_projects first reported in
     the week (first_story_at).
  4. Numbers of the week, read from the warehouse through the erw package, each with its table:
     the day-ahead average per ISO main hub over the ISO's local week and the change from the
     week before (both weeks must be complete); the week's highest real-time price and where;
     Henry Hub, WTI and Brent: the last close of the week, the last close before it, and the
     change; US48 peak demand of the week with its hour.
  4b. Policy of the week (session 24, platform tool 12): the week's most significant policy action from
     policy_actions (scored with the news rubric), with its impact read from policy_reads, and the next two.
  5. Chart of the week (session 23, platform tool 26): the chart warehouse/analysis/run.py picked
     for the week, with its two-sentence note, read from docs/analysis/YYYY-Www/. When the engine
     has not written one for the week, the section says so.

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
from brief import FUELS, HUB_MARKET, MAIN_HUBS, RT_TZ, ROOT, cite_short, erw, ip, link_text, mean2, NAME, NEWS_COLS  # noqa: E402
from score import PRICES, pick_model  # noqa: E402

ROUNDUP_DIR = os.path.join(ROOT, "docs", "roundup")
ANALYSIS_DIR = os.path.join(ROOT, "docs", "analysis")
WEEKEND_N = 3  # clusters under Weekend


TYPE_RANK = {"rule": 0, "proposed_rule": 1, "notice": 2, "press_release": 3}
TYPE_LABEL = {"rule": "final rule", "proposed_rule": "proposed rule", "notice": "notice", "press_release": "news release"}
# Session 470 (roundup audit fix 10): the deal types of warehouse/deals/extract.py (DEAL_TYPES) as words, not codes
DEAL_LABEL = {"ppa": "power purchase agreement", "offtake": "offtake", "m_and_a": "acquisition",
              "project_finance": "project finance", "tax_equity": "tax equity", "debt": "debt", "equity_raise": "equity raise",
              "joint_venture": "joint venture", "lease": "lease", "behind_the_meter": "behind the meter",
              "nuclear_restart": "nuclear restart", "smr": "small modular reactor", "fuel_supply": "fuel supply",
              "other": "other"}
TITLE_MAX = 160


def previous_week(start):
    """The ISO week label (YYYY-Www) of the week before the one starting at `start`."""
    y, w, _ = (start - pd.Timedelta(days=7)).date().isocalendar()
    return f"{y}-W{w:02d}"


def policy_title(title):
    """Session 470 (roundup audit fix 9): a Federal Register title over 160 characters ("Parties; Subject") is written as
    its subject, with the parties when they are short; the full title is on /policy."""
    t = str(title).strip()
    if len(t) <= TITLE_MAX or ";" not in t:
        return t
    parts = [p.strip() for p in t.split(";") if p.strip()]
    subject, who = parts[-1], "; ".join(parts[:-1])
    return f"{subject} ({who})" if len(who) <= 60 else subject


def dockets(d):
    """'Docket No. CP24-75-001;Docket No. CP25-505-000' to 'dockets CP24-75-001, CP25-505-000' (W40 printed "docket
    Docket No.")."""
    ids = [re.sub(r"^(?:docket\s+)?(?:no\.?\s*)?", "", x.strip(), flags=re.I) for x in str(d).split(";") if x.strip()]
    return (("dockets " if len(ids) > 1 else "docket ") + ", ".join(ids)) if ids else ""


def dated(r):
    """One date, said for what it is: a Federal Register document is published, an agency's release released."""
    return f"{'released' if r['action_type'] == 'press_release' else 'published'} {str(r['event_date'])[:10]}"


def policy_of_the_week(start, cut, log):
    """Session 24: the week's most significant policy action (policy_actions, scored with the news rubric by
    warehouse/policy/score.py; ties go to a final rule over a proposed rule, a notice and a news release), with its
    impact read (policy_reads) where one was kept, and the next two."""
    acts = read_table("policy_actions")
    if acts is None:
        return ["- policy_actions is not in the warehouse on this machine."]
    reads = read_table("policy_reads")
    rd = {} if reads is None else {r["action_event_id"]: r for r in reads.to_dict("records")}
    d = pd.to_datetime(acts["event_date"], utc=True, format="ISO8601")
    w = acts[(d >= start) & (d < cut) & (acts["significance"] != "")].copy()
    if w.empty:
        return ["- no scored policy action is dated this week."]
    w["sig"] = w["significance"].astype(int)
    w["rank"] = w["action_type"].map(TYPE_RANK).fillna(9)
    w = w.sort_values(["sig", "rank", "event_date"], ascending=[False, True, True])
    top = w.iloc[0]
    r = rd.get(top["event_id"], {})
    # session 470 (roundup audit fix 9): a long title as its subject, "docket" once, one date said for what it is
    L = [f"**{policy_title(top['title'])}** ({top['agency']} {TYPE_LABEL.get(top['action_type'], top['action_type'])}, "
         f"{dated(top)}" + (f"; {dockets(top['docket'])}" if top["docket"] else "") + ")", ""]
    # session 577: brief.why_line, so a read without a final stop does not run into its link
    L.append(brief.why_line(r.get("plain_read") or top["why"], top["title"]) + f" [Source]({top['source_url']})")
    if r.get("timeline"):
        L += ["", f"Timeline: {r['timeline']}"]
    also = w.iloc[1:3]
    if len(also):
        L += ["", "Also this week:", ""]
        for x in also.to_dict("records"):
            L.append(f"- {policy_title(x['title'])} ({x['agency']} {TYPE_LABEL.get(x['action_type'], x['action_type'])}, "
                     f"{dated(x)}): {brief.why_line(x['why'], x['title'])} [source]({x['source_url']})")
    L += ["", "Table: `policy_actions` (scored with the news rubric) and `policy_reads` (impact reads, each field kept only "
          "when its words are in the action's own text); every action is on [/policy](/policy)."]
    log(f"  policy of the week: {top['event_id']} (significance {top['sig']})")
    return L


def policy_section(lines, above, log):
    """Session 192: the policy section without a repeat of an item above. An agency's release the feeds carry is both
    a scored story and a policy action; listed under "Also this week" beside the same story in the week's five, it
    was a repeat the hard check (brief.assert_unique) refused, so the whole Roundup was not written (the dry run of
    week 2026-W41). The later line is dropped and named, as the daily digest does since session 176
    (brief.without_repeats). "Also this week:" goes with its last line."""
    L = brief.without_repeats(lines, above, log)
    if "Also this week:" in L:
        i = L.index("Also this week:")
        rest = L[i + 1:]
        j = next((k for k, ln in enumerate(rest) if ln.strip()), len(rest))
        if j == len(rest) or not rest[j].startswith("- "):
            L = L[:i] + rest[j:]
    return L


def chart_of_the_week(label, log):
    """Session 23: the chart of the week from docs/analysis/<label>/ (warehouse/analysis/run.py): the
    email-size PNG, the title, the two-sentence note and the source line, as markdown. The note passed
    the literal-number check when the engine wrote it and is copied here as written."""
    import json
    # Session 170: a finding chosen on /analysis ("Use in Roundup") for this week comes first; none chosen, or nothing
    # readable, the rule's chart of the week stands and is labeled as the rule's pick. Never stops the Roundup.
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import roundup_pick
        got = roundup_pick.chosen(label, log)
    except Exception as exc:
        log(f"  roundup pick: {type(exc).__name__}: {str(exc)[:150]}; the rule's chart stands")
        got = None
    if got:
        return got[1]
    meta = os.path.join(ANALYSIS_DIR, label, "chart_of_the_week.json")
    if not os.path.exists(meta):
        log(f"  chart of the week: none in docs/analysis/{label}/")
        return ["- no chart of the week was picked for this week (warehouse/analysis/run.py has not run for it)."]
    m = json.load(open(meta, encoding="utf-8"))
    L = [f"**{m['title']}** (the rule's pick; no finding was chosen for this week)", "", f"![{m['title']}](../analysis/{label}/{m['files']['email']})", ""]
    if m.get("note"):
        L += [m["note"], ""]
    L.append(f"{m['source_line']} Template `{m['template']}`; every template's latest run is on "
             "[/research](/research).")
    return L


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
        df = erw.fetch(table, start=s, end=e, node=node, market=HUB_MARKET.get(label))
    except Exception as exc:
        log(f"  numbers: {table} unavailable: {exc!r}")
        return None, 0, int((e - s) / pd.Timedelta(hours=1))
    return (mean2(df["value"]) if len(df) else None), len(df), int((e - s) / pd.Timedelta(hours=1))


def numbers(start, cut, log):
    # session 21: no provenance sentence; each number keeps its table in the footnotes at the end
    notes = brief.Notes()
    prior = start - pd.Timedelta(days=7)
    L = ["**Day-ahead average, main hub, over the ISO's local week, and the change from the week before**", "",
          "| ISO | Hub or zone | This week USD/MWh | Week before USD/MWh | Change | Table |", "|---|---|---|---|---|---|"]
    for label, table, node, tz in MAIN_HUBS:
        m1, n1, x1 = dam_week(label, table, node, tz, start, log)
        m0, n0, x0 = dam_week(label, table, node, tz, prior, log)
        pause = brief.paused_row(label)  # session 470: a paused publisher's grid says so
        gap = (lambda n, x: f"not requested: paused by the ERW since {pause['paused_on']}") if pause else (
            lambda n, x: f"not in the warehouse ({n} of {x} hours)")
        this = f"{m1}" if n1 == x1 else gap(n1, x1)
        last = f"{m0}" if n0 == x0 else gap(n0, x0)
        # the change of the two rounded means, as the table shows them
        chg = f"{m1 - m0:+}" if n1 == x1 and n0 == x0 else "not computed"
        L.append(f"| {label} | {node} | {this} | {last} | {chg} | {notes.ref(table)} |")
    L.append("| PJM | | | | | no PJM price table (no API key) |")

    # the week's highest real-time price, over UTC bounds, from the interval price tables
    best, covered = None, []
    # session 30: the consolidated iso_rtm_hub_prices is read one ISO (market) at a time (brief.rt_parts)
    for iso, table, market in brief.rt_parts():
        try:
            df = erw.fetch(table, start=start, end=cut, market=market)
        except Exception as exc:
            log(f"  numbers: {table} unavailable: {exc!r}")
            continue
        if df.empty:
            continue
        covered.append(f"{table}{f' ({market})' if market else ''} to {df['ts_utc'].max():%Y-%m-%d %H:%M} UTC")
        top = df.loc[df["value"].idxmax()]
        if best is None or top["value"] > best[0]["value"]:
            best = (top, table, iso)
    L += ["", "**Highest real-time price of the week:** "]
    if best:
        top, table, iso = best
        tz = RT_TZ.get(iso, "UTC")
        L[-1] += (f"{top['value']:.2f} USD/MWh at {top['node']} ({iso.upper()}), interval starting "
                  f"{top['ts_utc'].tz_convert(tz):%Y-%m-%d %H:%M} local ({top['ts_utc']:%Y-%m-%d %H:%M} UTC), "
                  f"{top['variable']} {notes.ref(table, 'real-time tables read, and how far each reaches this week: ' + ', '.join(covered))}"
                  f", {brief.rt_label(iso, top['variable'])}.")  # session 470: the variable named for a reader
    else:
        L[-1] += "no real-time table covers this week."

    # Session 470 (roundup audit fix 2): EIA's closes come days late, so "the last close of the week against the last close
    # before it" was a change of two trading days on W40 (WTI +12.8 percent from one outlying close). The change is now the
    # newest close held against the newest close a week or more before it, both dated, and a close that moved over 8
    # percent in a day while the other crude moved under 5 is flagged for a person to confirm against EIA's page.
    L += ["", "**Fuel spot prices, change over a week** (EIA, trading dates; the newest close held and the newest close a "
          "week or more before it):", "", "| Price | Newest close | Close a week before | Change | Table |",
          "|---|---|---|---|---|"]
    try:
        fuel = erw.fetch("eia_fuel_spot_prices")
        series = {entity: fuel[fuel["entity"] == entity].sort_values("ts_utc") for _, entity in FUELS}
        for label, entity in FUELS:
            got = fuel_change(series, entity, cut)
            if got is None:
                s = series[entity]
                L.append(f"| {label} | not in the warehouse (no close a week apart; newest "
                         f"{s['ts_utc'].max():%Y-%m-%d}) | | | {notes.ref('eia_fuel_spot_prices')} |" if len(s) else
                         f"| {label} | not in the warehouse | | | {notes.ref('eia_fuel_spot_prices')} |")
                continue
            a, b, flags = got
            L.append(f"| {label} | {a['value']:.2f} {a['unit']} on {a['ts_utc']:%Y-%m-%d} | {b['value']:.2f} on "
                     f"{b['ts_utc']:%Y-%m-%d} | {a['value'] - b['value']:+.2f} ({100 * (a['value'] / b['value'] - 1):+.1f}%)"
                     + "".join(f"; {f}" for f in flags) + f" | {notes.ref('eia_fuel_spot_prices')} |")
    except Exception as exc:
        log(f"  numbers: fuel prices unavailable: {exc!r}")
        L.append("| fuel prices | not in the warehouse | | | |")

    L += ["", "**US48 peak demand of the week:** "]
    try:
        d = erw.fetch("eia930_all_demand", start=start, end=cut, ba="us48")  # session 30: the consolidated table
        d = d[d["variable"] == "demand_mw"]
        if d.empty:
            L[-1] += "not in the warehouse for this week."
        else:
            top = d.loc[d["value"].idxmax()]
            L[-1] += (f"{top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC "
                      f"({top['ts_utc'].tz_convert('America/New_York'):%A %Y-%m-%d, %H:%M} Eastern), from "
                      f"{d['ts_utc'].nunique()} hours of the week to {d['ts_utc'].max():%Y-%m-%d %H:%M} UTC "
                      f"{notes.ref('eia930_all_demand', 'balancing authority us48')}.")
    except Exception as exc:
        log(f"  numbers: US48 demand unavailable: {exc!r}")
        L[-1] += "not in the warehouse."
    return L + notes.lines()


OTHER_CRUDE = {"eia:wti_cushing": "eia:brent", "eia:brent": "eia:wti_cushing"}
CRUDE_NAME = {"eia:wti_cushing": "WTI", "eia:brent": "Brent"}
JUMP, CALM = 0.08, 0.05


def day_move(s, ts):
    """The move of the close at ts against the close before it, or None."""
    i = s.index[s["ts_utc"] == ts]
    if not len(i):
        return None
    pos = s.index.get_loc(i[0])
    if pos == 0:
        return None
    return s.iloc[pos]["value"] / s.iloc[pos - 1]["value"] - 1


def fuel_change(series, entity, cut):
    """Session 470: (a, b, flags): the newest close before the cut, the newest close at least seven days before it, and
    the flags of either close that moved over 8 percent in a day while the other crude moved under 5 percent the same
    day. None when no two closes a week apart are held."""
    s = series[entity]
    held = s[s["ts_utc"] < cut]
    if held.empty:
        return None
    a = held.iloc[-1]
    base = held[held["ts_utc"] <= a["ts_utc"] - pd.Timedelta(days=7)]
    if base.empty:
        return None
    b = base.iloc[-1]
    flags, other = [], OTHER_CRUDE.get(entity)
    for row in (a, b):
        m = day_move(held.reset_index(drop=True), row["ts_utc"])
        if other is None or m is None or abs(m) <= JUMP:
            continue
        o = day_move(series[other].reset_index(drop=True), row["ts_utc"])
        if o is not None and abs(o) < CALM:
            flags.append(f"the close of {row['ts_utc']:%Y-%m-%d} moved {100 * m:+.1f}% in a day while "
                         f"{CRUDE_NAME[other]} moved {100 * o:+.1f}%: to be confirmed against EIA's page")
    return a, b, flags


def num(v, fmt="{:,.0f}"):
    return fmt.format(float(v)) if v not in ("", None) else "not stated"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW weekly brief, the Energy Roundup")
    ap.add_argument("--week", help="ISO week YYYY-Www (default: the week that contains yesterday, UTC)")
    # session 30: the shadow Roundup (warehouse/news/shadow.py) reads the shadow's view and writes only to --out
    ap.add_argument("--stories", help="read the scored stories from this file instead of news_stories")
    ap.add_argument("--out", help="write the Roundup to this path only (not docs/roundup/<week>.md, not latest.md)")
    ap.add_argument("--no-model", action="store_true", help="session 176: no model call (the daily model cap is reached): "
                    "the publishers' own titles as headlines, no written summary of the numbers; the Roundup still publishes")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_roundup_{run_id}.log"))
    status = dict(table="roundup", market="brief", status="ok", detail="")
    try:
        now = pd.Timestamp.now(tz="UTC")
        label, start, end, cut = week_bounds(args.week, now)
        partial = cut < end
        df = ip.read_series(args.stories or os.path.join(ip.OUT_DIR, NAME + ".csv"), NEWS_COLS)
        when = pd.to_datetime(df["event_date"], utc=True, format="ISO8601")
        s = df[(df["scored_at"] != "") & (when >= start) & (when < cut)].copy()
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        s = s[s["sig"] > 0]
        log(f"week {label}: [{ip.utc_iso(start)}, {ip.utc_iso(cut)}), {len(s)} scored energy stories")
        if s.empty:
            raise RuntimeError("no scored stories in the week; not writing an empty brief")
        # session 470 (roundup audit fix 1): one event once (W40 showed 8 items for 6 events), and not the previous
        # Roundup's story again (W41 repeated W40's Amazon and Constellation agreement)
        prev = [os.path.join(ROUNDUP_DIR, f"{previous_week(start)}.md")]
        clusters = brief.one_per_event(brief.not_shown_before(brief.build_clusters(s), prev, log, "the previous Roundup"), log)
        # session 23: the weekend's top clusters first (Saturday 00:00 UTC to the cut), then the five
        # stories of the week from the clusters not shown under Weekend
        wk_start = start + pd.Timedelta(days=5)
        wk_s = s[pd.to_datetime(s["event_date"], utc=True, format="ISO8601") >= wk_start]
        weekend = (brief.one_per_event(brief.not_shown_before(brief.build_clusters(wk_s), prev, log, "the previous Roundup"),
                                       log).head(WEEKEND_N) if len(wk_s) else clusters.head(0))
        top5 = clusters[~clusters["cluster_id"].isin(set(weekend["cluster_id"]))].head(5)
        shown = pd.concat([weekend, top5]).drop_duplicates("cluster_id")
        if args.no_model:
            client, model = None, brief.NO_MODEL
            heads, u, calls = brief.own_titles(shown), brief.SimpleNamespace(input_tokens=0, output_tokens=0), 0
            log(f"  --no-model: {len(heads)} headlines are the publishers' own titles; no model call")
        else:
            client = brief.llm.client("roundup", log)
            model = pick_model(client, log)
            heads, u, calls = brief.headlines(client, model, shown, log)
        if set(shown["cluster_id"]) - set(heads):
            raise RuntimeError("headlines missing for some clusters")
        secs = brief.unique_items({"weekend": weekend, "top": top5}, heads, log)
        weekend, top5 = secs["weekend"], secs["top"]
        cost = (f"USD {(u.input_tokens * PRICES[model][0] + u.output_tokens * PRICES[model][1]) / 1e6:.4f}"
                if model in PRICES else "unknown")
        log(f"  headlines from {model}: tokens in {u.input_tokens} out {u.output_tokens}; cost {cost}")

        span = (f"{start:%Y-%m-%d} to {(end - pd.Timedelta(days=1)):%Y-%m-%d}" +
                (f", to {cut:%Y-%m-%d %H:%M} UTC" if partial else ""))
        L = [f"# ERW's Roundup, {label}", "",
             # session 21: one sentence (what, the period, the story count); the method is on /about#digest
             f"ERW's weekly roundup of energy news for {span}, from {len(s)} scored stories.", "",
             *([brief.NO_MODEL_LINE.replace("Today's", "This week's"), ""] if args.no_model else []),
             "## Weekend", ""]
        if weekend.empty:
            L.append(f"- no scored story was published on {wk_start:%Y-%m-%d} or "
                     f"{wk_start + pd.Timedelta(days=1):%Y-%m-%d} (UTC).")
        for i, r in enumerate(weekend.to_dict("records"), 1):
            L.append(f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')}, {r['n']} "
                     f"{'story' if r['n'] == 1 else 'stories'})  ")
            L.append(f"   {brief.why_line(r['why'], heads[r['cluster_id']])} Sources: {link_text(r['links'])}")  # 470: plain; 577: why_line; 801: the headline
        L += ["", "## The five stories of the week", ""]
        for i, r in enumerate(top5.to_dict("records"), 1):
            # session 21, ruling 4: the sector label, never the significance score
            L.append(f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')}, {r['n']} "
                     f"{'story' if r['n'] == 1 else 'stories'})  ")
            L.append(f"   {brief.why_line(r['why'], heads[r['cluster_id']])} Sources: {link_text(r['links'])}")

        L += ["", "## Deals of the week", ""]
        deals = read_table("energy_deals")
        if deals is None:
            L.append("- energy_deals is not in the warehouse on this machine.")
        else:
            dw = deals[(pd.to_datetime(deals["event_date"], utc=True, format="ISO8601") >= start)
                       & (pd.to_datetime(deals["event_date"], utc=True, format="ISO8601") < cut)].sort_values("event_date")
            if dw.empty:
                L.append("- no deal in `energy_deals` is dated this week.")
            else:
                L += ["| Date | Type | Buyer | Seller | Asset | MW | US dollars | Status | Story |",
                      "|---|---|---|---|---|---|---|---|---|"]
                for r in dw.to_dict("records"):
                    first = r["story_urls"].split(";")[0]
                    L.append(f"| {r['event_date'][:10]} | {DEAL_LABEL.get(r['deal_type'], r['deal_type'].replace('_', ' '))} | "
                             f"{r['buyer'] or 'not stated'} | "
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
            t = pd.to_datetime(dc["first_story_at"], utc=True, format="ISO8601")
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

        L += ["", "## ERW's Policy of the Week", ""] + policy_section(policy_of_the_week(start, cut, log), L, log)
        nums = numbers(start, cut, log)
        summary, su = (None, []) if args.no_model else brief.numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        L += ["", "## ERW's Numbers This Week", ""] + ([summary, ""] if summary else []) + nums
        L += ["", "## ERW's Chart of the Week", ""] + chart_of_the_week(label, log)
        L += ["", "ERW", "", "---", "", "[How this is made.](/about#digest)", "",  # session 25: signed ERW
              f"<!-- Generated by warehouse/news/roundup.py at {now:%Y-%m-%d %H:%M} UTC; run log "
              f"warehouse/output/logs/news_roundup_{run_id}.log; model {model}. -->"]
        path = os.path.abspath(args.out) if args.out else os.path.join(ROUNDUP_DIR, f"{label}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        L = brief.drop_repeated_items(L, log)  # session 470: a repeat is dropped and named, not the Roundup
        brief.assert_unique(L)  # ruling 5: no two items share a normalized headline or a source URL
        text = "\n".join(L) + "\n"
        for p in ((path,) if args.out else (path, os.path.join(ROUNDUP_DIR, "latest.md"))):
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        status["detail"] = (f"{label}: {len(s)} stories, {len(clusters)} clusters, {len(weekend)} weekend, "
                            f"headline cost {cost}")
        log(f"wrote {os.path.relpath(path, ROOT)} and latest.md; {status['detail']}")
        print(f"roundup: {os.path.relpath(path, ROOT)}; {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"news_roundup FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("news_roundup", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
