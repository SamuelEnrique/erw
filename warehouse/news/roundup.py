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


def missed_week_line(start, folder=None):
    """Session 2702 (rulings item 10, the default of 24 October 2026): one line under the title when the previous ISO week
    has no Roundup (week 42 has none), pointing to that week's Digests; "" when it has one."""
    prev = previous_week(start)
    if os.path.exists(os.path.join(folder or ROUNDUP_DIR, f"{prev}.md")):
        return ""
    mon = start - pd.Timedelta(days=7)
    return (f"No Roundup was written for {prev}; that week's stories are in the Digests of {mon:%Y-%m-%d} to "
            f"{mon + pd.Timedelta(days=4):%Y-%m-%d} ([the archive](/digest)).")


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


def chart_relevance(m, stories, log):
    """Session 806 (docs/reviews/periodicals-plan-2026-10-23.md, Roundup change 2): the measure most related to the week's
    top stories among the rule's pick and the measures that also moved (the week's chart record, also_moved), by
    daily_chart.relevance (session 805). Returns (the most related {template, title, finding, score, story, shared} or
    None when none is related, whether it is the rendered pick). The rendered picture is the rule's (run.py draws one a
    week on the data machine); when the stories point elsewhere the section says so and names the measure."""
    if not stories:
        return None, True
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import daily_chart
    except Exception as exc:
        log(f"  chart of the week: relevance not computed ({type(exc).__name__}: {str(exc)[:100]})")
        return None, True
    cands = [{"template": m.get("template", ""), "title": m.get("title", ""), "finding": m.get("finding") or m.get("caption") or ""}]
    cands += [{"template": a.get("template", ""), "title": a.get("title", ""), "finding": a.get("finding", "")} for a in m.get("also_moved") or []]
    best = None
    for c in cands:
        score, story, shared = daily_chart.relevance({"fact": f"{c['title']}: {c['finding']}", "table": c["template"], "series_key": ""}, stories)
        if score and (best is None or score > best["score"]):
            best = dict(c, score=score, story=story, shared=shared)
    if best is None:
        log("  chart of the week: none of the measures that moved is related to the week's top stories")
        return None, True
    log(f"  chart of the week: the most related to the week's stories is {best['template']} (relevance {best['score']})")
    return best, best["template"] == m.get("template", "")


def chart_of_the_week(label, log, stories=None):
    """Session 23: the chart of the week from docs/analysis/<label>/ (warehouse/analysis/run.py): the
    email-size PNG, the title, the two-sentence note and the source line, as markdown. The note passed
    the literal-number check when the engine wrote it and is copied here as written. Session 806: with the week's top
    stories, the section says which measure the stories point to (chart_relevance)."""
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
    h = m.get("headline") or {}
    if h.get("label") and h.get("value") is not None:   # session 2704: one sentence on what the picture shows
        L += [f"Reading: the chart shows {h['label']} at {chart_figure(h['value'])} {h.get('unit', '')} in {h.get('period', 'its latest period')}.".replace("  ", " "), ""]
    L.append(f"{m['source_line']} Template `{m['template']}`; every template's latest run is on "
             "[/research](/research).")
    best, same = chart_relevance(m, stories, log)
    if best is not None and same:
        L.append(f"It is also the measure most related to the week's top stories: it shares "
                 f"{', '.join(best['shared']) if best['shared'] else 'its sector'} with {best['story'][:80]!r}.")
    elif best is not None:
        L.append(f"The week's stories point elsewhere: {best['title']} ({brief.why_line(best['finding'])}) is the measure that "
                 f"moved this week most related to the week's top stories (it shares "
                 f"{', '.join(best['shared']) if best['shared'] else 'its sector'} with {best['story'][:80]!r}); its chart is on "
                 f"[/research](/research) (template `{best['template']}`).")
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


def interval_words(freq):
    """'PT15M' as 'a 15-minute interval', 'PT1H' as 'an hourly interval', 'PT5M' as 'a 5-minute interval'."""
    f = str(freq or "")
    m = re.fullmatch(r"PT(\d+)M", f)
    if m:
        return f"a {m.group(1)}-minute interval"
    if f == "PT1H":
        return "an hourly interval"
    return f"an interval of {f}" if f else "an interval of unstated length"


def numbers(start, cut, log, facts=None):
    """The numbers section. facts (session 806): a dict the function fills with what it computed (the hubs' weekly means
    and the change, the fuel closes a week apart, the US48 peak, the real-time maximum), for the week in five numbers."""
    # session 21: no provenance sentence; each number keeps its table in the footnotes at the end
    notes = brief.Notes()
    prior = start - pd.Timedelta(days=7)
    held = brief.held_grids()   # session 806: a held grid's price is not the price move of the week (the board's rule)
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
        if facts is not None and n1 == x1 and n0 == x0 and not pause and label not in held:
            facts.setdefault("dam", []).append(dict(label=label, node=node, table=table, m1=m1, m0=m0, ref=notes.ref(table)))
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
                  f", {brief.rt_label(iso, top['variable'])}, {interval_words(top.get('freq', ''))}."  # 470: the variable named; 806: the interval
                  " The grids' real-time series differ in interval length (a 15-minute mean beside an hourly value), so this is the "
                  "highest interval value held, not one measure across grids.")
        if facts is not None:
            facts["rt"] = top
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
            if facts is not None and not flags:
                facts.setdefault("fuel", []).append(dict(label=label, a=a, b=b, ref=notes.ref("eia_fuel_spot_prices")))
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
            if facts is not None:
                facts["us48"] = dict(top=top, ref=notes.ref("eia930_all_demand", "balancing authority us48"))
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


# Session 2702 (rulings item 11, the default of 24 October 2026): the deals and datacenter tables print a row with
# confidence ROW_CONFIDENCE or more and at least one of operator, site or MW (for a deal: a buyer or a seller, an asset,
# or MW), US rows first, at most ROW_MAX a section, with a count of the rest and a link to the whole table
ROW_CONFIDENCE = 0.7
ROW_MAX = 15
US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND "
                "OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
US_NAMES = {"us", "usa", "u.s.", "united states", "united states of america"}
ROW_FIELDS = {"energy_deals": ("buyer", "seller", "asset", "mw"), "datacenter_projects": ("operator", "site_name", "mw")}


def row_is_us(r):
    """A row is of the United States: its country says so, or its state is a US state's code."""
    return (str(r.get("country", "")).strip().lower() in US_NAMES) or (str(r.get("state", "")).strip().upper() in US_STATES)


def row_passes(r, table):
    """The floor: confidence ROW_CONFIDENCE or more and one of the table's ROW_FIELDS stated."""
    try:
        conf = float(r.get("confidence") or 0)
    except ValueError:
        conf = 0.0
    return conf >= ROW_CONFIDENCE and any(str(r.get(f, "")).strip() for f in ROW_FIELDS[table])


def floor_rows(df, table, n=ROW_MAX):
    """(rows to print, how many more pass the floor, how many fall under it): the rows that pass, US rows first, each
    group in the frame's own order, at most n."""
    recs = df.to_dict("records")
    ok = [r for r in recs if row_passes(r, table)]
    ok = [r for r in ok if row_is_us(r)] + [r for r in ok if not row_is_us(r)]
    return ok[:n], max(0, len(ok) - n), len(recs) - len(ok)


def floor_note(table, what, shown, rest, under):
    """The line under a floored table: what is shown, the rest, and the link to the whole table."""
    return (f"Table: `{table}` ({len(shown)} {what} shown: confidence {ROW_CONFIDENCE} or more and "
            f"{'a party, an asset or MW' if table == 'energy_deals' else 'an operator, a site or MW'} stated, US first, at "
            f"most {ROW_MAX}; {rest} more pass, {under} fall under the floor; [the whole table](/data#{table})).")


def num(v, fmt="{:,.0f}"):
    return fmt.format(float(v)) if v not in ("", None) else "not stated"


def usd_words(d):
    """A sum of US dollars in the voice's form: 'USD 12 billion', 'USD 4.3 billion', 'USD 834 million', 'USD 250,000'."""
    from decimal import Decimal, ROUND_HALF_UP
    v = float(d)
    for scale, word in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million")):
        if abs(v) >= scale:
            x = (Decimal(repr(v)) / Decimal(int(scale))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # half up, as mean2
            s = f"{x:.2f}".rstrip("0").rstrip(".")
            return f"USD {s} {word}"
    return f"USD {v:,.0f}"


def chart_figure(v):
    """The chart's headline value as the five numbers print it: a whole number as it is, else whole above 100, else to
    the cent."""
    v = float(v)
    if v == int(v):
        return f"{int(v):,}"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.2f}"


FIVE_HEADING = "## The week in five numbers"


def five_numbers(label, start, cut, facts, log, picked=None):
    """Session 806 (docs/reviews/periodicals-plan-2026-10-23.md, Roundup change 1): the week in five numbers, each
    traced (scripts/check_roundup.py): the week's biggest price move among the main hubs' weekly means (both weeks
    complete, not held, not paused) and EIA's closes a week apart, in percent; the US48 peak with its hour; the week's
    largest deal by US dollars (by MW when no deal states dollars) from energy_deals; the largest new datacenter load first
    reported in the week (datacenter_projects, capacity_mw: the policy actions of the week carry no MW or price); and the
    headline figure of the week's chart (docs/analysis/<week>/chart_of_the_week.json). A number the warehouse does not
    hold is said missing, never filled."""
    L = []
    # 1. the price move of the week
    moves = []
    for h in facts.get("dam", []):
        mv = brief.day_move(h["m1"], start, h["m0"], start - pd.Timedelta(days=7))
        if mv["pct"] is not None:
            moves.append(dict(mv, label=f"{h['label']} {h['node']} day-ahead", text=f"{h['label']} {h['node']} day-ahead averaged {h['m1']} USD/MWh over the week, against {h['m0']} USD/MWh "
                                       f"the week before ({mv['ch']:+.2f} USD/MWh, {mv['pct']:+.1f}%) {h['ref']}"))
    for f in facts.get("fuel", []):
        mv = brief.day_move(f["a"]["value"], f["a"]["ts_utc"], f["b"]["value"], f["b"]["ts_utc"])
        if mv["pct"] is not None:
            moves.append(dict(mv, label=f["label"], text=f"{f['label']} closed at {f['a']['value']:.2f} {f['a']['unit']} on {f['a']['ts_utc']:%Y-%m-%d}, against "
                                       f"{f['b']['value']:.2f} {f['a']['unit']} on {f['b']['ts_utc']:%Y-%m-%d} ({mv['ch']:+.2f} {f['a']['unit']}, "
                                       f"{mv['pct']:+.1f}%) {f['ref']}"))
    picked = {} if picked is None else picked   # session 2704: what the opening number chooses from
    if moves:
        best = max(moves, key=lambda m: abs(m["pct"]))
        picked["move"] = best
        L.append(f"- **Price move of the week:** {best['text']}.")
    else:
        L.append("- **Price move of the week:** no price with a complete week and a week before it is held.")
    # 2. the US48 peak
    if facts.get("us48"):
        top = facts["us48"]["top"]
        L.append(f"- **US48 peak demand:** {top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC {facts['us48']['ref']}.")
        picked["us48"] = {"text": f"US48 demand peaked at {top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC"}
    else:
        L.append("- **US48 peak demand:** not in the warehouse for this week.")
    # 3. the deal of the week
    deals = read_table("energy_deals")
    if deals is None:
        L.append("- **Deal of the week:** energy_deals is not in the warehouse on this machine.")
    else:
        when = pd.to_datetime(deals["event_date"], utc=True, format="ISO8601")
        dw = deals[(when >= start) & (when < cut)].copy()
        dw["_d"] = pd.to_numeric(dw["dollars"], errors="coerce")
        dw["_m"] = pd.to_numeric(dw["mw"], errors="coerce")
        if dw["_d"].notna().any():
            r = dw.sort_values(["_d", "event_date"], ascending=[False, True]).iloc[0]
            who = " and ".join(x for x in (r["buyer"], r["seller"]) if x) or "parties not stated"
            L.append(f"- **Deal of the week, by US dollars:** {usd_words(r['_d'])}, {who}, {r['asset'] or 'asset not stated'} "
                     f"({DEAL_LABEL.get(r['deal_type'], r['deal_type'].replace('_', ' '))}, {r['event_date'][:10]}; `energy_deals` {r['event_id']}).")
            picked["deal"] = {"usd": float(r["_d"]), "text": L[-1].split(":** ", 1)[1].rstrip(".")}
        elif dw["_m"].notna().any():
            r = dw.sort_values(["_m", "event_date"], ascending=[False, True]).iloc[0]
            who = " and ".join(x for x in (r["buyer"], r["seller"]) if x) or "parties not stated"
            L.append(f"- **Deal of the week, by MW (no deal of the week states dollars):** {float(r['_m']):,.0f} MW, {who}, "
                     f"{r['asset'] or 'asset not stated'} ({DEAL_LABEL.get(r['deal_type'], r['deal_type'].replace('_', ' '))}, "
                     f"{r['event_date'][:10]}; `energy_deals` {r['event_id']}).")
        else:
            L.append("- **Deal of the week:** no deal in `energy_deals` is dated this week.")
    # 4. the largest new datacenter load
    dc = read_table("datacenter_projects")
    if dc is None:
        L.append("- **Largest new datacenter load first reported this week:** datacenter_projects is not in the warehouse on this machine.")
    else:
        t = pd.to_datetime(dc["first_story_at"], utc=True, format="ISO8601")
        cw = dc[(t >= start) & (t < cut)].copy()
        cw["_m"] = pd.to_numeric(cw["capacity_mw"] if "capacity_mw" in cw.columns else cw["mw"], errors="coerce")
        if cw["_m"].notna().any():
            r = cw.sort_values(["_m", "first_story_at"], ascending=[False, True]).iloc[0]
            place = ", ".join(x for x in (r.get("city", ""), r.get("state", "")) if x) or "place not stated"
            L.append(f"- **Largest new datacenter load first reported this week:** {float(r['_m']):,.0f} MW, {r['operator'] or 'operator not stated'}, "
                     f"{r['site_name'] or 'site not stated'}, {place} (`datacenter_projects` {r['entity_id']}).")
            picked["dc"] = {"mw": float(r["_m"]), "text": L[-1].split(":** ", 1)[1].rstrip(".")}
        else:
            L.append("- **Largest new datacenter load first reported this week:** no facility first reported this week states its MW.")
    # 5. the chart's figure
    meta = os.path.join(ANALYSIS_DIR, label, "chart_of_the_week.json")
    try:
        import json
        m = json.load(open(meta, encoding="utf-8"))
        h = m["headline"]
        L.append(f"- **From the chart of the week:** {h['label']}: {chart_figure(h['value'])} {h['unit']} in {h['period']} "
                 f"(template `{m['template']}`, `docs/analysis/{label}/chart_of_the_week.json`).")
    except (OSError, KeyError, ValueError):
        L.append("- **From the chart of the week:** no chart of the week was picked for this week, so no figure.")
    log(f"  five numbers: {len(L)} lines")
    return L


# ---------------------------------------------------------------------------------------------------------------------
# Session 2704: the Roundup in the brandbook's v2 shape (the owner's rulings of 24 October 2026, queue file 131). The
# promise: a one-page executive read on the week's most consequential changes, the evidence behind them, and what merits
# attention next week. The order is fixed: the masthead (with the missed-week line); the opening number; the week in five
# numbers (session 806, kept); what mattered (three developments); "More" (the weekend's and the week's other stories,
# the deals and datacenter tables, the policy of the week, the numbers in full); the chart of the week with its reading;
# next week; the fun fact; the footer.
# ---------------------------------------------------------------------------------------------------------------------
V2_TITLE = "ERW Weekly Roundup"
WHAT_MATTERED_N = 3
WEEK_MOVE_PCT = 10.0        # a weekly mean (or a close a week apart) that moved this much in percent opens the Roundup
DEAL_USD_MIN = 1e9          # else a deal of the week of at least USD 1 billion
DC_MW_MIN = 500             # else a datacenter load first reported this week of at least 500 MW
NEXT_WEEK_N = 3
DATE_WORDS = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})")


def opening_number(picked):
    """The Roundup's opening number: the number that best explains the week, chosen by rule among the week in five
    numbers (`picked`, as five_numbers fills it), in this order:
      1. the price move of the week, when it is WEEK_MOVE_PCT percent or more: a move held over a whole week is persistent,
         market-wide and drawn from the warehouse's own tables (calculated from observed prices);
      2. else the deal of the week, when it is DEAL_USD_MIN or more: relevance to capital decisions (reported: extracted
         from the week's stories, every number checked against its story);
      3. else the largest datacenter load first reported this week, when it is DC_MW_MIN MW or more: relevance to
         infrastructure (reported, as its stories state it);
      4. else the US48 peak of the week: system scale (observed, EIA-930).
    Returns {key, text, status} or None when the week holds none of them."""
    move, deal, dc, us48 = (picked.get(k) for k in ("move", "deal", "dc", "us48"))
    if move and abs(float(move["pct"])) >= WEEK_MOVE_PCT:
        return {"key": "move", "text": move["text"], "status": "calculated from observed prices (the warehouse's tables)", "move": move}
    if deal and deal.get("usd") and float(deal["usd"]) >= DEAL_USD_MIN:
        return {"key": "deal", "text": deal["text"], "status": "reported: extracted from the week's stories, every number checked against its story"}
    if dc and dc.get("mw") and float(dc["mw"]) >= DC_MW_MIN:
        return {"key": "datacenter", "text": dc["text"], "status": "reported, as its stories state it"}
    if us48:
        return {"key": "us48", "text": us48["text"], "status": "observed (EIA-930 hourly demand)"}
    return None


def opening_lines(op):
    L = ["## The opening number", ""]
    if op is None:
        return L + ["The week holds none of the five numbers this section reads.", ""]
    return L + [f"**{op['text'].rstrip('.')}.** Status: {op['status']}.", ""]


def subject_line(op, first_head):
    """ERW Weekly | <plain description of the week>, with a second clause of one verified metric and unit when the
    opening number is a warehouse figure (the price move of the week)."""
    head = brief.nodash(str(first_head or "the week's energy news")).rstrip(".")
    mv = (op or {}).get("move")
    return f"ERW Weekly | {head}" + (f"; {mv['label']} {float(mv['pct']):+.1f}% on the week" if mv and mv.get("label") else "")


def masthead_lines(label, end, cut, op, first_head, missed):
    return ([f"# {V2_TITLE}, {label}", "", f"**Week ending {brief.day_words(end - pd.Timedelta(days=1))}.** "
             f"{brief.cutoff_words(cut).replace('Data through', 'Sources through')}", ""]
            + ([missed, ""] if missed else [])
            + [f"<!-- subject: {subject_line(op, first_head)} -->", "", f"<!-- opening: {(op or {}).get('key', '')} -->", ""])


def evidence_gap(r, head=""):
    """What the evidence does not establish, from the record alone: the figure is the outlet's (a scored MW or sum; else
    any figure the headline or the why line states), or the stories give none; one outlet so far, or an analysis piece."""
    fig = brief.story_figure(r)
    if fig:
        words = [f"The {fig} is the outlet's figure, not a warehouse table's."]
    elif brief.figures_of(f"{head} {r.get('why') or ''}"):
        words = ["Its figures are the outlets', not a warehouse table's."]
    else:
        words = ["The stories give no figure for it."]
    lim = brief.limitation(r)
    if lim:
        words.append(lim)
    text = " ".join(words)
    return "What the evidence does not establish: " + text[0].lower() + text[1:]


def next_week(end, log, n=NEXT_WEEK_N):
    """Dated items of the week after the Roundup's (Monday to Sunday) that the policy monitor holds with a date: the
    deadlines and next steps its reads quote from the agencies' own text (policy_reads.timeline), most significant first,
    one line each; [] when none is held. What is scheduled, never a prediction."""
    reads = read_table("policy_reads")
    if reads is None:
        log("  next week: policy_reads is not on this machine")
        return []
    lo, hi = end.tz_convert(None).normalize(), end.tz_convert(None).normalize() + pd.Timedelta(days=7)
    items = []
    for r in reads.to_dict("records"):
        text = str(r.get("timeline") or "")
        for sent in re.split(r"(?<=[a-z0-9]{2}[.;])\s+(?=[A-Z])", text):   # "5:00 p.m. Eastern" is one sentence
            m = DATE_WORDS.search(sent)
            if not m:
                continue
            day = pd.Timestamp(f"{m.group(1)} {m.group(2)} {m.group(3)}")
            if lo <= day < hi:
                try:
                    sig = int(r.get("significance") or 0)
                except ValueError:
                    sig = 0
                items.append((day, -sig, brief.nodash(str(r.get("title") or "")), str(r.get("agency") or ""), brief.nodash(sent.strip()),
                              str(r.get("source_url") or "")))
                break
    items.sort(key=lambda x: (x[1], x[0], x[2]))
    out, seen = [], set()
    for day, _sig, title, agency, sent, url in items:
        if title in seen:
            continue
        seen.add(title)
        src = f" ([source]({url}))" if url.startswith("http") else ""
        out.append(f"- **{brief.day_words(day)}**: {title[:TITLE_MAX].rstrip('.')} ({agency}). {sent.rstrip('.')}.{src}")
        if len(out) >= n:
            break
    log(f"  next week: {len(out)} dated item(s) of {len(items)} found in policy_reads")
    return sorted(out, key=lambda x: pd.Timestamp(re.search(r"\*\*(.+?)\*\*", x).group(1)))


NO_NEXT_WEEK = ("No dated events held this week: the warehouse and the policy monitor hold no filing, auction, hearing, data "
                "release or project milestone dated in the week ahead.")


def week_fun_fact(start, cut, log):
    """The week's fun fact, as the Digest's (session 23): the newest of the week's stored items, re-verified against its
    stored sources; none when no Digest of the week carried one or it fails."""
    try:
        import funfact
        days = [d for d in pd.date_range(start.tz_convert(None).normalize(), cut.tz_convert(None).normalize(), freq="D")][::-1]
        for d in days:
            item = funfact.load_item(f"{d:%Y-%m-%d}")
            if item is None:
                continue
            problems = funfact.verify_item(item)
            if problems:
                log(f"  fun fact: {item['fact_id']} failed re-verification ({problems}); the week's next one is tried")
                continue
            return ["", "## ERW's Fun Fact", ""] + funfact.item_markdown(item)
    except Exception as exc:
        log(f"  fun fact: omitted ({ip.redact(repr(exc))[:200]})")
    log("  fun fact: none of the week's items passed; section omitted")
    return []


def footer_lines(now, run_id, model):
    return ["", "ERW", "", "---", "", "[How this is made.](/about#digest)", "",
            "Corrections: [open an issue](https://github.com/SamuelEnrique/erw/issues). Preferences and topics: [subscribe](/subscribe). "
            "Every email carries its own unsubscribe link.", "",
            f"<!-- Generated by warehouse/news/roundup.py at {now:%Y-%m-%d %H:%M} UTC; run log "
            f"warehouse/output/logs/news_roundup_{run_id}.log; model {model}. -->"]


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
        # session 802: one topic, one item, the rest folded under it, for the weekend's three and the five of the week
        # session 2704 (the v2 order): what mattered first, the week's three most consequential developments (the scorer's
        # significance, one topic one item); the weekend's three and the week's five are the others, under More
        mattered, m_folded = brief.one_per_topic(clusters, WHAT_MATTERED_N, log, "what mattered")
        taken = set(mattered["cluster_id"]) | m_folded
        wk_c = (brief.one_per_event(brief.not_shown_before(brief.build_clusters(wk_s), prev, log, "the previous Roundup"), log)
                if len(wk_s) else clusters.head(0))
        wk_c = wk_c[~wk_c["cluster_id"].isin(taken)]
        weekend, wk_folded = brief.one_per_topic(wk_c, WEEKEND_N, log, "the weekend")
        rest = clusters[~clusters["cluster_id"].isin(taken | set(weekend["cluster_id"]) | wk_folded)]
        top5, _ = brief.one_per_topic(rest, 5, log, "the five of the week")
        shown = pd.concat([mattered, weekend, top5]).drop_duplicates("cluster_id")
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
        secs = brief.unique_items({"mattered": mattered, "weekend": weekend, "top": top5}, heads, log)
        mattered, weekend, top5 = secs["mattered"], secs["weekend"], secs["top"]
        cost = (f"USD {(u.input_tokens * PRICES[model][0] + u.output_tokens * PRICES[model][1]) / 1e6:.4f}"
                if model in PRICES else "unknown")
        log(f"  headlines from {model}: tokens in {u.input_tokens} out {u.output_tokens}; cost {cost}")

        span = (f"{start:%Y-%m-%d} to {(end - pd.Timedelta(days=1)):%Y-%m-%d}" +
                (f", to {cut:%Y-%m-%d %H:%M} UTC" if partial else ""))
        missed = missed_week_line(start)   # session 2702, rulings item 10
        intro = [  # session 21: one sentence (what, the period, the story count); the method is on /about#digest
             f"ERW's weekly roundup of energy news for {span}, from {len(s)} scored stories.", "",
             *([brief.NO_MODEL_LINE.replace("Today's", "This week's"), ""] if args.no_model else [])]
        # session 2704: the lines below are the fold ("More"); the page's order is assembled after the numbers
        L = ["### Weekend", ""]
        if weekend.empty:
            L.append(f"- no scored story was published on {wk_start:%Y-%m-%d} or "
                     f"{wk_start + pd.Timedelta(days=1):%Y-%m-%d} (UTC).")
        for i, r in enumerate(weekend.to_dict("records"), 1):
            L += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')}, {r['n']} "
                                  f"{'story' if r['n'] == 1 else 'stories'})  ",
                                  brief.why_line(r['why'], heads[r['cluster_id']]), f"Sources: {link_text(r['links'])}")  # 470, 577, 801, 802
        L += ["", "### The five stories of the week", ""]
        for i, r in enumerate(top5.to_dict("records"), 1):
            # session 21, ruling 4: the sector label, never the significance score
            L += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')}, {r['n']} "
                                  f"{'story' if r['n'] == 1 else 'stories'})  ",
                                  brief.why_line(r['why'], heads[r['cluster_id']]), f"Sources: {link_text(r['links'])}")

        L += ["", "### Deals of the week", ""]
        deals = read_table("energy_deals")
        if deals is None:
            L.append("- energy_deals is not in the warehouse on this machine.")
        else:
            dw = deals[(pd.to_datetime(deals["event_date"], utc=True, format="ISO8601") >= start)
                       & (pd.to_datetime(deals["event_date"], utc=True, format="ISO8601") < cut)].sort_values("event_date")
            shown_d, rest_d, under_d = floor_rows(dw, "energy_deals")   # session 2702, rulings item 11
            if dw.empty:
                L.append("- no deal in `energy_deals` is dated this week.")
            elif not shown_d:
                L.append(f"- none of the {len(dw)} deals dated this week passes the floor (confidence {ROW_CONFIDENCE} or more and a "
                         f"party, an asset or MW stated); [the whole table](/data#energy_deals).")
            else:
                L += ["| Date | Type | Buyer | Seller | Asset | MW | US dollars | Status | Story |",
                      "|---|---|---|---|---|---|---|---|---|"]
                for r in shown_d:
                    first = r["story_urls"].split(";")[0]
                    L.append(f"| {r['event_date'][:10]} | {DEAL_LABEL.get(r['deal_type'], r['deal_type'].replace('_', ' '))} | "
                             f"{r['buyer'] or 'not stated'} | "
                             f"{r['seller'] or 'not stated'} | {r['asset'] or 'not stated'} | {num(r['mw'])} | "
                             f"{num(r['dollars'])} | {r['status'] or 'not stated'} | [1]({first}) |")
                L.append("")
                L.append(floor_note("energy_deals", "deals", shown_d, rest_d, under_d) + " Extracted from the scored stories by "
                         "`warehouse/deals/extract.py`, every number checked against its story.")

        L += ["", "### Datacenter announcements of the week", ""]
        dc = read_table("datacenter_projects")
        if dc is None:
            L.append("- datacenter_projects is not in the warehouse on this machine.")
        else:
            t = pd.to_datetime(dc["first_story_at"], utc=True, format="ISO8601")
            cw = dc[(t >= start) & (t < cut)].sort_values("first_story_at")
            shown_c, rest_c, under_c = floor_rows(cw, "datacenter_projects")   # session 2702, rulings item 11
            if cw.empty:
                L.append("- no datacenter facility in `datacenter_projects` was first reported this week.")
            elif not shown_c:
                L.append(f"- none of the {len(cw)} facilities first reported this week passes the floor (confidence {ROW_CONFIDENCE} or "
                         "more and an operator, a site or MW stated); [the whole table](/data#datacenter_projects).")
            else:
                L += ["| First reported | Operator | Site | Place | MW | Status | Story |", "|---|---|---|---|---|---|---|"]
                for r in shown_c:
                    place = ", ".join(x for x in (r["city"], r["county"], r["state"]) if x) or "not stated"
                    L.append(f"| {r['first_story_at'][:10]} | {r['operator'] or 'not stated'} | "
                             f"{r['site_name'] or 'not stated'} | {place} | {num(r['mw'])} | "
                             f"{(r['project_status'] or 'not stated').replace('_', ' ')} | "
                             f"[1]({r['story_urls'].split(';')[0]}) |")
                L.append("")
                L.append(floor_note("datacenter_projects", "facilities", shown_c, rest_c, under_c)
                         + " `warehouse/datacenters/extract.py`, every field only as its story states it.")

        L += ["", "### ERW's Policy of the Week", ""] + policy_section(policy_of_the_week(start, cut, log), L, log)
        facts, picked = {}, {}
        nums = numbers(start, cut, log, facts)
        five = five_numbers(label, start, cut, facts, log, picked)   # session 806, kept; session 2704: what the opening reads
        summary, su = (None, []) if args.no_model else brief.numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        L += ["", "### ERW's Numbers This Week", ""] + ([summary, ""] if summary else []) + nums
        # session 2704: the v2 order. The masthead (with the missed week), the opening number, the week in five numbers,
        # what mattered, the fold, the chart of the week, next week, the fun fact, the footer
        op = opening_number(picked)
        log(f"  opening number: {(op or {}).get('key', 'none')}")
        recs = mattered.to_dict("records")
        W = ["## What mattered", ""]
        if not recs:
            W.append("- no scored story of the week to rank.")
        for i, r in enumerate(recs, 1):
            W += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')}, {r['n']} "
                                  f"{'story' if r['n'] == 1 else 'stories'})  ",
                                  " ".join(x for x in (brief.why_line(r['why'], heads[r['cluster_id']]), evidence_gap(r, heads[r['cluster_id']])) if x),
                                  f"Sources: {link_text(r['links'])}")
        nxt = next_week(end, log)
        L = (masthead_lines(label, end, cut, op, heads[recs[0]["cluster_id"]] if recs else "", missed) + intro + opening_lines(op)
             + [FIVE_HEADING, ""] + five + [""] + W + ["", brief.FOLD_HEADING, ""] + L
             + ["", "## ERW's Chart of the Week", ""] + chart_of_the_week(label, log, stories=shown.to_dict("records"))  # 806: the week's stories
             + ["", "## Next week", ""] + (nxt or [NO_NEXT_WEEK])
             + week_fun_fact(start, cut, log)
             + footer_lines(now, run_id, model))   # session 25: signed ERW; session 2704: corrections, preferences, unsubscribe
        log(f"  words of prose above the fold: {brief.above_fold_words(chr(10).join(L))}")
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
