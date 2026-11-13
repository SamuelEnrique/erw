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


def week_policy(acts, start, cut):
    """The week's scored policy actions, most significant first (ties: a final rule over a proposed rule, a notice and a
    news release, then the earlier date). Session 1907: policy_of_the_week and the five's policy stand-in read one order."""
    d = pd.to_datetime(acts["event_date"], utc=True, format="ISO8601")
    w = acts[(d >= start) & (d < cut) & (acts["significance"] != "")].copy()
    if w.empty:
        return w
    w["sig"] = w["significance"].astype(int)
    w["rank"] = w["action_type"].map(TYPE_RANK).fillna(9)
    return w.sort_values(["sig", "rank", "event_date"], ascending=[False, True, True])


def policy_pick(start, cut):
    """Session 1907 (faults file row 68, its second choice): the week's policy of the week as a row (a dict), the five's
    stand-in after capacity and before a second price; None when policy_actions is not on the machine or holds no scored
    action dated in the week."""
    acts = read_table("policy_actions")
    if acts is None or not len(acts):
        return None
    w = week_policy(acts, start, cut)
    return None if w.empty else w.iloc[0].to_dict()


def policy_words(top):
    """The policy stand-in in words: the title as policy_of_the_week writes it, the agency, the kind and the date."""
    return (f"{brief.money_style(tidy_title(policy_title(top['title'])))} ({top['agency']} "   # 3480, row 178
            f"{TYPE_LABEL.get(top['action_type'], top['action_type'])}, {dated(top)}), the Policy of the Week below")


def policy_of_the_week(start, cut, log):
    """Session 24: the week's most significant policy action (policy_actions, scored with the news rubric by
    warehouse/policy/score.py; ties go to a final rule over a proposed rule, a notice and a news release), with its
    impact read (policy_reads) where one was kept, and the next two."""
    acts = read_table("policy_actions")
    if acts is None:
        return ["- policy_actions is not in the warehouse on this machine."]
    reads = read_table("policy_reads")
    rd = {} if reads is None else {r["action_event_id"]: r for r in reads.to_dict("records")}
    w = week_policy(acts, start, cut)
    if w.empty:
        return ["- no scored policy action is dated this week."]
    top = w.iloc[0]
    r = rd.get(top["event_id"], {})
    # session 470 (roundup audit fix 9): a long title as its subject, "docket" once, one date said for what it is
    # session 3480 (faults file row 178): the title's sums in the issue's money style, as the Digest's policy lines (row 86)
    L = [f"**{brief.money_style(policy_title(top['title']))}** ({top['agency']} {TYPE_LABEL.get(top['action_type'], top['action_type'])}, "
         f"{dated(top)}" + (f"; {dockets(top['docket'])}" if top["docket"] else "") + ")", ""]
    # session 577: brief.why_line, so a read without a final stop does not run into its link
    L.append(brief.why_line(r.get("plain_read") or top["why"], top["title"]) + f" [Source]({top['source_url']})")
    if r.get("timeline"):
        L += ["", f"Timeline: {r['timeline']}"]
    also = w.iloc[1:3]
    if len(also):
        L += ["", "Also this week:", ""]
        for x in also.to_dict("records"):
            L.append(also_policy_line(x))
    L += ["", "Table: `policy_actions` (scored with the news rubric) and `policy_reads` (impact reads, each field kept only "
          "when its words are in the action's own text); every action is on [/policy](/policy)."]
    log(f"  policy of the week: {top['event_id']} (significance {top['sig']})")
    return L


def tidy_title(t):
    """Session 1882 (row 72): a Federal Register title's company suffix with its stop ("Last Energy, Inc;" to "Last Energy,
    Inc.;")."""
    return re.sub(r"\b(Inc|Corp|Ltd|Co)(?=[;,\s]|$)(?!\.)", r"\1.", str(t))


def also_policy_line(x):
    """One line under "Also this week": the title, the agency, the kind and the date, then the why line when it passes
    (brief.why_line) and the source. Session 1882 (faults file row 72, row 46's fault in the policy section): a why line
    that failed left "(...):  [source](...)", a colon introducing nothing and a double space; the line now closes on its
    bracket with a stop and the source follows as its own sentence."""
    head = (f"- {brief.money_style(tidy_title(policy_title(x['title'])))} ({x['agency']} {TYPE_LABEL.get(x['action_type'], x['action_type'])}, "   # 3480, row 178
            f"{dated(x)})")
    why = brief.why_line(x.get("why", ""), x["title"]).strip()
    return f"{head}: {why} [source]({x['source_url']})" if why else f"{head}. [Source]({x['source_url']})"


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


# Session 1896 (row 75): what a measure counts, as a story would say it. A story names a measure when it says the measure's
# quantity (the first of these its title or series name holds) and one more word of its title (the commodity, the
# grid, the place): a price series of the commodity the story names, a flow or a capacity of the place it names (the
# Digest's fault 14 rule, docs/reviews/periodicals-faults-2026-11-05.md row 14), never a shared token alone.
MEASURE_QUANTITY = (r"\bexport", r"\bimport", r"\bstocks?\b|\binventor", r"\bdischarg", r"\bsales\b|\bsold\b", r"\bcurtail",
                    r"\bheld (?:back|below)\b|\bhigh sustained limit\b", r"\bshoulder hours?\b", r"\bregulation\b",
                    r"\bin operation\b|\bcapacity\b|\bbuild-?out\b", r"\bdemand\b|\bpeak load\b", r"\boutput\b|\bgeneration\b",
                    r"\bprices?\b")


def measure_named(c, stories):
    """Session 1896 (row 75): the first story of the week that names the measure c ({title, finding}), or None. The measure's
    quantity is the first MEASURE_QUANTITY pattern its title or its series name (the finding before ": ") holds; a story
    names it when its titles or why line hold that pattern and, where the title has other content words, one of them
    (compared on their first six letters, so "Batteries" meets "battery"). No quantity known: no story names it."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        from daily_chart import GENERIC
    except Exception:
        GENERIC = set()
    title = str(c.get("title") or "")
    name = f"{title} {str(c.get('finding') or '').split(': ')[0]}".lower()
    q = next((p for p in MEASURE_QUANTITY if re.search(p, name)), None)
    if q is None:
        return None
    others = {w[:6] for w in re.findall(r"[a-z0-9]+", title.lower())
              if len(w) >= 3 and not w.isdigit() and w not in GENERIC and w not in ("lower",) and not re.search(q, w)}
    for s in stories or []:
        titles = s.get("titles") if isinstance(s.get("titles"), list) else [s.get("title", "")]
        text = " ".join(str(t) for t in titles + [s.get("why", "")]).lower()
        if not re.search(q, text):
            continue
        if not others or others & {w[:6] for w in re.findall(r"[a-z0-9]+", text) if len(w) >= 3}:
            return str(titles[0] if titles else "")
    return None


def measure_figure(c):
    """Session 1896 (row 75): the measure's figure as its chart record states it: the finding's first sentence after the
    series name ("3,675 kbbl/d in the week of 2026-10-26 to 2026-11-01, down 1,179 from 4,854 the week before"), styled as
    the note is (note_style); "" when the record holds none."""
    f = str(c.get("finding") or "")
    if ": " not in f:
        return ""
    first = re.split(r"(?<=[^\d])\.\s|(?<=\d)\.\s(?=[A-Z])", f.split(": ", 1)[1])[0].strip().rstrip(".")
    return note_style(first) if re.search(r"\d", first) else ""


NOTE_NUMBER = re.compile(r"(?<![\w.,/-])(-?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?![\w,/-]|\.\d)")


def note_style(text):
    """Session 1882 (faults file row 73, row 16's fault in the chart's note): the note's numbers as the issue prints them.
    A figure of 100 or more with a fraction is rounded half up to the whole number with its separator (53,999.71 to 54,000;
    9188.86 to 9,189: the five print "47,682"), a whole number of 10,000 or more gains its separator, and a year, a date
    (2024-11-04), a count under 100 and a figure under 100 are left as written. The engine's note passed its literal-number
    check on the record's own figures; this styles it for the reader only, every figure still the record's rounded."""
    from decimal import Decimal, ROUND_HALF_UP

    def one(m):
        sign, whole, frac = m.group(1), m.group(2), m.group(3) or ""
        w = int(whole.replace(",", ""))
        if frac:
            if w < 100:
                return m.group(0)
            v = (Decimal(whole.replace(",", "") + frac)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            return f"{sign}{int(v):,}"
        if "," in whole or w < 10000:
            return m.group(0)
        return f"{sign}{w:,}"
    return NOTE_NUMBER.sub(one, str(text or ""))


ERW_FULL = "Energy Research Warehouse (ERW)"


def watch_spec(template):
    """The watch list's entry of a template (warehouse/analysis/watch.py, WATCH): its table, entity and variable; None
    for a template that is not a watch line."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
        import watch
    except Exception:
        return None
    return next((s for s in watch.WATCH if s.get("name") == template), None)


def derived_inputs(df):
    """The tables a fetched table says it is built from: its header note "Derived from: a; b" (the derived builders
    write it), in their order."""
    out = []
    for n in (df.attrs.get("erw") or {}).get("notes") or []:
        mt = re.match(r"\s*derived from\s*:(.*)", str(n), re.I)
        if mt:
            out += [t.strip() for t in re.split(r"[;,]", mt.group(1)) if re.fullmatch(r"[a-z0-9_]+", t.strip())]
    return out


def report_name(r):
    """A source report as the line names it: the report's own words (a leading "Form " and a closing parenthesis of
    paths taken off, its colon read as a comma), the publisher's short name first when the report does not hold it."""
    pub = str(r.get("publisher") or "").strip()
    short = pub.split(" (")[1].rstrip(")") if " (" in pub and len(pub.split(" (")[1]) < 12 else pub
    rep = re.sub(r"\s*\([^()]*\)\s*$", "", str(r.get("report") or "").strip())
    rep = re.sub(r"^Form\s+", "", rep).replace(": ", ", ")
    if not rep:
        return short
    return rep if (not short or short in rep) else f"{short}, {rep}"


def series_reports(table, entity, variable, fetch, sources):
    """The source reports of one series of a table: the reports of the source ids its rows carry."""
    df = fetch(table)
    rows = df[df["entity"] == entity]
    if variable and "variable" in rows:
        rows = rows[rows["variable"].isin([variable] if isinstance(variable, str) else list(variable))]
    sids = sorted(set(rows["source"].dropna().astype(str)))
    reps = {r["source"]: r for r in sources(table)["reports"]}
    return df, [reps.get(s, {"source": s}) for s in sids]


def chart_source_line(m, log, fetch=None, sources=None):
    """Session 1896 (docs/reviews/periodicals-faults-2026-11-05.md, row 74): the chart's source line names the publisher
    of the series charted, not every publisher of its table, and the ERW once. The stored line (common.source_line, on
    the data machine) lists every publisher of the table: W45's Lower 48 battery series (entity eia930:US48, EIA-930)
    read "Source: Energy Research Warehouse (ERW), derived, Energy Research Warehouse (ERW), derived from California ISO
    via the Energy Research Warehouse (ERW), table storage_daily_cycle". Here the rows of the charted entity give their
    source ids; when they are the ERW's own (a derived table), the table its header says it is built from and that holds
    the same entity gives the publisher. The retrieval date stays the stored line's (the record's run). Anything not
    found: the stored line as written, and the log says why."""
    stored = str(m.get("source_line") or "")
    fetch = fetch or erw.fetch
    sources = sources or erw.sources
    spec = watch_spec(m.get("template", ""))
    if not spec or not spec.get("table") or not spec.get("entity"):
        log(f"  chart of the week: source line as stored ({m.get('template', '')} is not a watch line)")
        return stored
    table, entity, variable = spec["table"], spec["entity"], spec.get("variable")
    try:
        df, reps = series_reports(table, entity, variable, fetch, sources)
        derived = bool(reps) and all(str(r.get("publisher") or "").startswith(ERW_FULL) or str(r.get("source", "")).startswith("erw:")
                                     for r in reps)
        if derived:
            reps = []
            for up in derived_inputs(df):
                try:
                    udf, ureps = series_reports(up, entity, None, fetch, sources)
                except Exception:
                    continue
                if len(udf[udf["entity"] == entity]) and ureps:
                    reps = ureps
                    break
        names = []
        for r in reps:
            n = report_name(r)
            if n and n not in names:
                names.append(n)
    except Exception as exc:
        log(f"  chart of the week: source line as stored ({type(exc).__name__}: {str(exc)[:100]})")
        return stored
    if not names:
        log(f"  chart of the week: source line as stored (no publisher found for {entity} in {table})")
        return stored
    when = re.search(r"data retrieved to (\d{4}-\d{2}-\d{2})", stored)
    when = f"; data retrieved to {when.group(1)}" if when else ""
    via = f"via the ERW's derived table {table}" if derived else f"via the {ERW_FULL}, table {table}"
    return f"Source: {'; '.join(names)}, {via}{when}."


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
        L += [note_style(m["note"]), ""]   # session 1882 (row 73): one number style, as the five print the figure
    h = m.get("headline") or {}
    if h.get("label") and h.get("value") is not None and not m.get("note"):   # session 2704: one sentence on what the picture shows
        # session 1446 (fault 35): the note the engine wrote says the move against the weeks held; this line only when
        # there is no note, so the caption is not read twice
        L += [f"Reading: the chart shows {h['label']} at {chart_figure(h['value'])} {h.get('unit', '')} in {h.get('period', 'its latest period')}.".replace("  ", " "), ""]
    L.append(f"{chart_source_line(m, log)} Template `{m['template']}`; every template's latest run is on "   # session 1896 (row 74)
             "[/research](/research).")
    best, same = chart_relevance(m, stories, log)
    if best is not None and same:
        L.append(f"It is also the measure most related to the week's top stories: it shares "
                 f"{', '.join(best['shared']) if best['shared'] else 'its sector'} with {best['story'][:80]!r}.")
    elif best is not None:
        # session 1446 (fault 35): one sentence; the related measure's chart is the data machine's to render (item 17)
        # session 1896 (row 75): only when a story of the week names the measure, and then with its figure from the record
        named, fig = measure_named(best, stories), measure_figure(best)
        if named and fig:
            L.append(f"The week's stories point to {best['title']}, whose chart is on [/research](/research) (template "
                     f"`{best['template']}`): {fig}.")
        else:
            log(f"  chart of the week: no pointer to {best['template']} ("
                + ("no story of the week names the measure" if not named else "its record holds no figure") + ")")
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


# Session 1895 (faults file row 71): the zone a grid's local time is written in, the interval in words, and the Tables
# line's words for the week's highest real-time price's variable (scripts/check_roundup.py and site/scripts/check-values.mjs
# read it there). Session 3457 (row 152): the helpers live in brief.py now, which writes the Digest's line the same way.
interval_words = brief.interval_words
ZONE_WORDS = brief.ZONE_WORDS
RT_VARIABLE = "; the week's highest real-time price is variable `"
rt_when = brief.rt_when


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
        if label in held:
            # session 1988 (faults file row 93): a grid held for license (its publisher asks for written permission) prints
            # no mean, as the Digest's table; its weekly means were printed here in W44 and W45. A paused one says its pause
            pz = brief.paused_row(label)
            words = f"not requested: paused by the ERW since {pz['paused_on']}" if pz else brief.LICENSED_NOTE
            L.append(f"| {label} | {node} | {words} | {words} | not computed | {notes.ref(table)} |")
            continue
        m1, n1, x1 = dam_week(label, table, node, tz, start, log)
        m0, n0, x0 = dam_week(label, table, node, tz, prior, log)
        pause = brief.paused_row(label)  # session 470: a paused publisher's grid says so
        gap = (lambda n, x: f"not requested: paused by the ERW since {pause['paused_on']}") if pause else (
            lambda n, x: f"{n} of {x} hours held, no weekly mean")   # session 1882 (row 71): what is held, said so
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
    parts = brief.rt_parts()
    held_parts = brief.held_rt(parts)   # session 1988 (row 93): a held grid's real-time table is not read, as in the Digest
    for iso, table, market in parts:
        if (iso, table) in held_parts:
            continue
        try:
            df = erw.fetch(table, start=start, end=cut, market=market)
        except Exception as exc:
            log(f"  numbers: {table} unavailable: {exc!r}")
            continue
        if df.empty:
            continue
        covered.append(f"{table}{f' ({market})' if market else ''} to {df['ts_utc'].max():%Y-%m-%d %H:%M} UTC")
        if facts is not None:   # session 1882 (row 59): how far the week's tables reach, for the masthead
            facts.setdefault("reach", []).append(df["ts_utc"].max())
        top = df.loc[df["value"].idxmax()]
        if best is None or top["value"] > best[0]["value"]:
            best = (top, table, iso)
    L += ["", "**Highest real-time price of the week:** "]
    if best:
        top, table, iso = best
        tz = RT_TZ.get(iso, "UTC")
        # session 1895 (faults file row 71): the source id ("spp_rtm", read as SPP in an ERCOT line) and "local" left the
        # line: it names the interval in the grid's zone and in UTC; the variable is on the Tables line, with the tables
        the_interval = re.sub(r"^an? ", "the ", interval_words(top.get('freq', '')))   # 806: the interval
        L[-1] += (f"{top['value']:.2f} USD/MWh at {top['node']} ({iso.upper()}), {the_interval} starting "
                  f"{rt_when(top['ts_utc'], tz)} "
                  f"{notes.ref(table, 'real-time tables read, and how far each reaches this week: ' + ', '.join(covered) + RT_VARIABLE + top['variable'] + '`')}"
                  f", {brief.rt_label(iso, top['variable'])}."  # 470: the variable named, in words
                  " The grids' real-time series differ in interval length (a 15-minute mean beside an hourly value), so this is the "
                  "highest interval value held, not one measure across grids.")
        if facts is not None:
            facts["rt"] = top
    else:
        L[-1] += "no real-time table covers this week."
    if held_parts:   # session 1988 (row 93): the grids not read, said as the Digest says them
        L[-1] += (" Not read: " + ", ".join(sorted({brief.RT_GRID.get(i, i.upper()) for i, _t in held_parts}))
                  + f" ({brief.LICENSED_NOTE}).")

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
            # session 3442 (faults file row 147): a newest close dated before the week began is not the week's move (with
            # this machine's copy of EIA's closes nine days old, W46 opened on W45's Brent close of 3 November, -13.1%)
            before_week = a["ts_utc"] < start
            L.append(f"| {label} | {a['value']:.2f} {a['unit']} on {a['ts_utc']:%Y-%m-%d} | {b['value']:.2f} on "
                     f"{b['ts_utc']:%Y-%m-%d} | {a['value'] - b['value']:+.2f} ({100 * (a['value'] / b['value'] - 1):+.1f}%)"
                     + "".join(f"; {f}" for f in flags)
                     + ("; EIA's newest close is from before this week, so this is no move of the week" if before_week else "")
                     + f" | {notes.ref('eia_fuel_spot_prices')} |")
            if facts is not None and not flags and not before_week:
                # session 3473 (row 174): the closes to the cut too, for the close of a story's own day (bench_words)
                s = series[entity]
                facts.setdefault("fuel", []).append(dict(label=label, a=a, b=b, ref=notes.ref("eia_fuel_spot_prices"),
                                                         s=s[s["ts_utc"] <= cut]))
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
                facts["us48"] = dict(top=top, ref=notes.ref("eia930_all_demand", "balancing authority us48"),
                                     hours=int(d["ts_utc"].nunique()), to=d["ts_utc"].max())
                facts.setdefault("reach", []).append(d["ts_utc"].max())
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


def dc_place(r):
    """Session 3445 (faults file row 150): a facility's place as the table holds it, its country named when it is not
    the United States ("Kemps Creek, Australia", not "Kemps Creek" in a table read as US first)."""
    country = str(r.get("country") or "").strip()
    parts = [str(r.get(k) or "").strip() for k in ("city", "county", "state")]
    if country and country.lower() not in US_NAMES:
        parts.append(country)
    return ", ".join(x for x in parts if x and x.lower() != "nan") or "not stated"


def dc_operator(r):
    """Session 3445 (faults file row 150): the operator; with none held, the developer the table holds, said to be one
    ("CDC (developer)", not "not stated" beside a row that names CDC)."""
    op = str(r.get("operator") or "").strip()
    dev = str(r.get("developer") or "").strip()
    if op and op.lower() != "nan":
        return op
    return f"{dev} (developer)" if dev and dev.lower() != "nan" else "not stated"


def row_passes(r, table):
    """The floor: confidence ROW_CONFIDENCE or more and one of the table's ROW_FIELDS stated."""
    try:
        conf = float(r.get("confidence") or 0)
    except ValueError:
        conf = 0.0
    return conf >= ROW_CONFIDENCE and any(str(r.get(f, "")).strip() for f in ROW_FIELDS[table])


def floor_rows(df, table, n=ROW_MAX, keep=None):
    """(rows to print, how many more pass the floor, how many fall under it): the rows that pass, US rows first, each
    group in the frame's own order, at most n. Session 3462 (faults file row 161): the row whose `event_id` is `keep`
    (the five's deal of the week) is always among them, in place of the last row otherwise shown."""
    recs = df.to_dict("records")
    ok = [r for r in recs if row_passes(r, table)]
    ok = [r for r in ok if row_is_us(r)] + [r for r in ok if not row_is_us(r)]
    shown = ok[:n]
    if keep and n and not any(r.get("event_id") == keep for r in shown):
        pinned = [r for r in ok[n:] if r.get("event_id") == keep]
        shown = shown[:n - len(pinned)] + pinned
    return shown, max(0, len(ok) - len(shown)), len(recs) - len(ok)


def deal_of_week_id(dw):
    """Session 3462 (row 161): the event id of the five's deal of the week among the week's deals `dw`, by the five's own
    rule (the Deals table's floor, then the most US dollars, else the most MW, the earlier on a tie); None when none."""
    ok = dw[[row_passes(r, "energy_deals") for r in dw.to_dict("records")]] if len(dw) else dw
    if ok.empty:
        return None
    for col in ("dollars", "mw"):
        v = pd.to_numeric(ok[col], errors="coerce")
        if v.notna().any():
            return ok.assign(_v=v).sort_values(["_v", "event_date"], ascending=[False, True]).iloc[0]["event_id"]
    return None


def floor_note(table, what, shown, rest, under):
    """The line under a floored table: what is shown, the rest, and the link to the whole table."""
    return (f"Table: `{table}` ({len(shown)} {what} shown: confidence {ROW_CONFIDENCE} or more and "
            f"{'a party, an asset or MW' if table == 'energy_deals' else 'an operator, a site or MW'} stated, US first, at "
            f"most {ROW_MAX}; {rest} more pass, {under} fall under the floor; [the whole table](/data#{table})).")


def num(v, fmt="{:,.0f}"):
    return fmt.format(float(v)) if v not in ("", None) else "not stated"


def usd_cell(v):
    """Session 1476 (chain 154, fault 54): a Deals table's US dollars cell in the issue's style ("938,000,000" was the W45
    dry run's; "USD 938 million" is the five numbers'), "not stated" when the row states none."""
    return usd_words(v) if str(v or "").strip() not in ("", "nan") else "not stated"


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


# Session 1882 (faults file rows 66 and 67): in a financing the extract writes the company raising the money as the seller
# and the lenders or investors as the buyer (warehouse/deals/extract.py's prompt); the issue names them by their roles
FINANCE_ROLES = {"project_finance": ("borrower", "lender", "financing"), "debt": ("borrower", "lender", "loan"),
                 "tax_equity": ("company raising", "investor", "tax equity investment"),
                 "equity_raise": ("company raising", "investor", "investment")}
FINANCE_PREP = {"financing": "of", "loan": "for", "tax equity investment": "in", "investment": "in"}   # row 103
ASSET_WORDS = [(re.compile(r"\bBESS\b"), "battery storage"), (re.compile(r"\bPPA\b"), "power purchase agreement"),
               (re.compile(r"\bSMRs?\b"), "small modular reactor")]


def asset_words(asset):
    """An asset's abbreviations said (row 66: "Germany BESS portfolio" to "Germany battery storage portfolio")."""
    t = str(asset or "").strip()
    for rx, word in ASSET_WORDS:
        t = rx.sub(word, t)
    return t


def names_of(r, side):
    """A party cell's names: the extract's split names (buyer_name "Deutsche Bank; Rabobank") when held, else the party as
    written; a list."""
    split = str(r.get(f"{side}_name") or "").strip()
    if ";" in split:
        return [x.strip() for x in split.split(";") if x.strip()]
    one = str(r.get(side) or "").strip()
    return [one] if one else []


def finance_words(r):
    """Row 66: a financing as the reader reads it: "Deutsche Bank and Rabobank's financing of Return's Germany battery
    storage portfolio (2026-11-05)". None when the row is not a financing or names neither side."""
    roles = FINANCE_ROLES.get(str(r.get("deal_type") or ""))
    if not roles:
        return None
    money, raising = str(r.get("buyer") or "").strip(), str(r.get("seller") or "").strip()
    asset = asset_words(r.get("asset"))
    if not money and not raising:
        return None
    what = asset if asset else ""
    if raising and raising.lower() not in asset.lower():
        what = f"{raising}'s {asset}" if asset else raising
    when = str(r.get("event_date") or "")[:10]
    prep = FINANCE_PREP.get(roles[2], "of")   # session 3312 (faults file row 103): "investment in", "loan for"
    head = f"{money}'s {roles[2]} {prep} {what}" if money and what else (f"{money}'s {roles[2]}" if money else f"{an(roles[2])} {prep} {what}")   # session 3336 (row 121): "an investment"
    return head + (f" ({when})" if when else "")


def deal_cells(r):
    """Row 67: the deals table's type, buyer and seller cells. The type "other" prints no word; a financing prints the
    company raising the money under Buyer and the lenders or investors under Seller, each with its role."""
    kind = r.get("deal_type") or ""
    label = "" if kind == "other" else DEAL_LABEL.get(kind, str(kind).replace("_", " "))
    roles = FINANCE_ROLES.get(kind)
    if not roles:
        return label, r.get("buyer") or "not stated", r.get("seller") or "not stated"
    money, raising = names_of(r, "buyer"), names_of(r, "seller")
    buyer = f"{', '.join(raising)} ({roles[0]})" if raising else "not stated"
    seller = f"{', '.join(money)} ({roles[1]}{'s' if len(money) > 1 or ' and ' in money[0] else ''})" if money else "not stated"
    return label, buyer, seller


def deal_words(r, what=""):
    """Session 1472 (chain 150's faults file, row 50): the deal of the week after its sum: the parties, the asset, and in
    brackets the deal's kind and date. A party the asset already names is not printed again ("TeraWulf, TeraWulf data
    center in Kentucky" was the W45 dry run's), and the kind "other" is not printed ("(other, 2026-11-05)"); with neither
    a party nor an asset the row says "parties not stated", as before. Session 1991 (faults file row 96): with `what`
    ("sum", "MW"), the brackets end on the outlet the figure was read from ("; the sum as Hart Energy reported it"), since
    another outlet's figure for the same deal can stand in the issue (JPT's "$2.1 Billion" beside Hart Energy's "$2B")."""
    base = deal_words_base(r)
    src = brief.outlet_name(r.get("source")) if str(r.get("source") or "").strip() else ""
    if not (what and src):
        return base
    note = f"the {what} as {src} reported it"
    return base[:-1] + f"; {note})" if base.endswith(")") else f"{base} ({note})"


def deal_words_base(r):
    fin = finance_words(r)   # session 1882 (row 66): a financing by its roles
    if fin:
        return fin
    asset = asset_words(r.get("asset"))
    parties = [str(x).strip() for x in (r.get("buyer"), r.get("seller")) if str(x or "").strip()]
    parties = [x for i, x in enumerate(parties) if x not in parties[:i] and x.lower() not in asset.lower()]
    words = ", ".join(x for x in (" and ".join(parties), asset) if x) or "parties not stated"
    kind = DEAL_LABEL.get(r.get("deal_type"), str(r.get("deal_type") or "").replace("_", " "))
    when = str(r.get("event_date") or "")[:10]
    inside = ", ".join(x for x in (kind if kind and kind != "other" else "", when) if x)
    return words + (f" ({inside})" if inside else "")


MARK_PUBLISHER = {"eia_fuel_spot_prices": "EIA", "eia930_all_demand": "EIA-930"}
MARK_RE = re.compile(r"\[(\d+)\]")


def five_marks(lines, facts):
    """Session 1882 (faults file row 70): the marks the five's rows print ("[5]", "[6]"), each named with its table, for
    the five's own Tables line. W45's email printed [5] and [6] and named no table: the Tables line that defines them is
    under ERW's Numbers This Week, folded out of the email. ["[5] `eia_fuel_spot_prices` (EIA)", ...] in the order of
    the marks."""
    tables = {}
    for h in facts.get("dam", []):
        if h.get("ref") and h.get("table"):
            tables[h["ref"]] = h["table"]
    for f in facts.get("fuel", []):
        tables[f["ref"]] = "eia_fuel_spot_prices"
    if facts.get("us48"):
        tables[facts["us48"]["ref"]] = "eia930_all_demand"
    seen = []
    for ln in lines:
        for m in MARK_RE.findall(ln):
            if f"[{m}]" in tables and f"[{m}]" not in seen:
                seen.append(f"[{m}]")
    out = []
    for ref in sorted(seen, key=lambda x: int(x[1:-1])):
        t = tables[ref]
        out.append(f"{ref} `{t}`" + (f" ({MARK_PUBLISHER[t]})" if t in MARK_PUBLISHER else ""))
    return out


def us48_period(u, start, cut):
    """Session 1882 (faults file row 69): the five's US48 row carries its period and status, as chain 131 asks of each of
    the five: ", the highest of the 72 hours held (to 2026-11-04 23:00 UTC)" when the week is not whole, ", the highest
    of the week's 168 hours" when it is. "" when the facts do not say how many hours were read."""
    n, to = u.get("hours"), u.get("to")
    if not n:
        return ""
    whole = int((cut - start) / pd.Timedelta(hours=1))
    if n >= whole:
        return f", the highest of the week's {whole} hours"
    return f", the highest of the {n} hours held" + (f" (to {pd.Timestamp(to):%Y-%m-%d %H:%M} UTC)" if to is not None else "")


def five_numbers(label, start, cut, facts, log, picked=None, capacity=None):
    """Session 806 (docs/reviews/periodicals-plan-2026-10-23.md, Roundup change 1): the week in five numbers, each
    traced (scripts/check_roundup.py): the week's biggest price move among the main hubs' weekly means (both weeks
    complete, not held, not paused) and EIA's closes a week apart, in percent; the US48 peak with its hour; the week's
    largest deal by US dollars (by MW when no deal states dollars) from energy_deals; the largest new datacenter load first
    reported in the week (datacenter_projects, capacity_mw: the policy actions of the week carry no MW or price); and the
    headline figure of the week's chart (docs/analysis/<week>/chart_of_the_week.json). A number the warehouse does not
    hold is said missing, never filled.

    Session 1895 (row 68): capacity, {"plant": planned_plant's plant, "rec": its story}, is the first stand-in for a
    category with no new observation, before a second price: a part of the system not yet among the five."""
    L = []
    # session 1460 (chain 150, faults 28 and 29): a row's table key (the row id, the chart's template and path) is the
    # tracer's, not the reader's: it goes to one Tables line under the five (small and grey in the email, closed under
    # Sources on the page), and scripts/check_roundup.py reads it there
    keys = []
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
    capacity = capacity if capacity is not None else picked.get("capacity")   # session 1895 (row 68), as main passes it
    policy = picked.get("policy")   # session 1907 (row 68, its second choice): the policy stand-in, after capacity
    moves.sort(key=lambda m: -abs(m["pct"]))
    picked["moves"] = moves   # session 1446: every move, for the opening number's choice and the stand-ins below
    if moves:
        best = moves[0]
        picked["move"] = best
        L.append(f"- **Price move of the week:** {best['text']}.")
    else:
        L.append("- **Price move of the week:** no price with a complete week and a week before it is held.")

    cap_used = []
    pol_used = []   # session 1907
    moves_used = set()   # session 1992 (row 97): the moves a stand-in has printed

    def stand_in(k, why):
        """Session 1446 (fault 27): a category with no new observation is replaced by the next price move that
        mattered, said so (the brand: replaced by one that mattered, said so). Session 1895 (row 68): a capacity line from
        the look-up of a plant the week's stories name comes first, once; a second price only when none is held."""
        if capacity and not cap_used:
            cap_used.append(capacity)
            ids = capacity["plant"].get("ids") or [f"plant {capacity['plant']['plant_id']}"]
            keys.append(f"the capacity, `eia860m_planned_generators` {', '.join(ids)}")
            return f"{why}; in its place, capacity: {capacity_words(capacity)}."
        # session 1907 (row 68, its second choice): then policy, a part not yet among the five, once; a second price only
        # when neither capacity nor policy is held
        if policy and not pol_used:
            pol_used.append(policy)
            keys.append(f"the policy, `policy_actions` {policy['event_id']}")
            return f"{why}; in its place, policy: {policy_words(policy)}."
        if len(moves) > 1:
            # session 1992 (faults file row 97): the next move not yet in the five that passes the opening's own bar
            # (brief.MATERIAL_PCT: 3% for a benchmark's close, 10% for a hub's mean) stands in; W46's "+0.3%" of Brent was
            # offered as a week's number. Until then the k-th move stood in, a smaller one passing over a larger unused one
            for m in moves[1:]:
                bar = brief.MATERIAL_PCT["hub" if str(m["label"]).endswith("day-ahead") else "fuel"]
                if id(m) not in moves_used and abs(float(m["pct"])) >= bar:
                    moves_used.add(id(m))
                    return f"{why}; in its place, the week's next price move: {m['text']}."
            # session 3375 (faults file row 145): the bar in words: "3%" and "10%" here are the rule's, not figures a
            # table holds, and the counts read them as figures with no key
            return (f"{why}; no other price passed the opening's bar for a move on the week (three percent for a benchmark's "
                    "close, ten for a hub's weekly mean).")
        return f"{why}."
    # 2. the US48 peak
    if facts.get("us48"):
        top = facts["us48"]["top"]
        L.append(f"- **US48 peak demand:** {top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC"
                 f"{us48_period(facts['us48'], start, cut)} {facts['us48']['ref']}.")   # session 1882 (row 69): its period
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
        # session 1474 (fault 52): the deal of the week is read with the Deals table's own floor (row_passes), so the five
        # never state a deal the table below refuses (W45: USD 19 billion at confidence 0.55, not in the table)
        under = len(dw)
        dw = dw[[row_passes(r, "energy_deals") for r in dw.to_dict("records")]] if len(dw) else dw
        under -= len(dw)
        dw["_d"] = pd.to_numeric(dw["dollars"], errors="coerce")
        dw["_m"] = pd.to_numeric(dw["mw"], errors="coerce")
        if dw["_d"].notna().any():
            r = dw.sort_values(["_d", "event_date"], ascending=[False, True]).iloc[0]
            L.append(f"- **Deal of the week, by US dollars:** {usd_words(r['_d'])}, {deal_words(r, 'sum')}.")   # session 1472
            keys.append(f"the deal of the week, `energy_deals` {r['event_id']}")
            picked["deal"] = {"usd": float(r["_d"]), "text": L[-1].split(":** ", 1)[1].rstrip(".")}
        elif dw["_m"].notna().any():
            r = dw.sort_values(["_m", "event_date"], ascending=[False, True]).iloc[0]
            L.append(f"- **Deal of the week, by MW (no deal of the week states dollars):** {float(r['_m']):,.0f} MW, {deal_words(r, 'MW')}.")
            keys.append(f"the deal of the week, `energy_deals` {r['event_id']}")
        else:
            L.append("- **Deal of the week:** " + stand_in(1, "no deal in `energy_deals` is dated this week" if not under else
                                                       f"no deal of the week passes the Deals table's floor ({under} under it)"))
    # 4. the largest new datacenter load
    dc = read_table("datacenter_projects")
    if dc is None:
        L.append("- **Largest new datacenter load first reported this week:** datacenter_projects is not in the warehouse on this machine.")
    else:
        t = pd.to_datetime(dc["first_story_at"], utc=True, format="ISO8601")
        cw = dc[(t >= start) & (t < cut)].copy()
        cw["_m"] = pd.to_numeric(cw["capacity_mw"] if "capacity_mw" in cw.columns else cw["mw"], errors="coerce")
        # session 1446 (fault 29): the week's largest load is a row with an operator or a site; a row with neither is
        # a figure with no subject ("1,000 MW, operator not stated, site not stated, Newport")
        # session 3462 (faults file row 162): a developer names the facility as the table below names it (row 150: "CDC
        # (developer)"); W46's five passed over a 1,400 MW load the table showed with its developer
        dev = cw["developer"].astype(str).str.strip().replace("nan", "") if "developer" in cw.columns else pd.Series("", index=cw.index)
        named = cw["operator"].astype(str).str.strip().ne("") | cw["site_name"].astype(str).str.strip().ne("") | dev.ne("")
        unnamed = cw[~named]   # session 3334 (faults file row 118): kept to say how many larger ones the row leaves out
        cw = cw[named]
        # session 1474 (fault 52): and with the datacenter table's own floor (W45: 702 MW at confidence 0.55, "not stated"
        # in the table below)
        dc_under = len(cw)
        cw = cw[[row_passes(r, "datacenter_projects") for r in cw.to_dict("records")]] if len(cw) else cw
        dc_under -= len(cw)
        if cw["_m"].notna().any():
            r = cw.sort_values(["_m", "first_story_at"], ascending=[False, True]).iloc[0]
            # session 1473 (fault 51): a part the row does not state is left out of the sentence ("702 MW, Google, site not
            # stated, Cheyenne" was the W45 dry run's); the row has an operator or a site (session 1446)
            parts = [str(r.get(k) or "").strip() for k in ("operator", "site_name")]
            if not parts[0]:   # session 3462 (row 162): the developer stands in, said to be one, as in the table
                parts[0] = dc_operator(r) if dc_operator(r) != "not stated" else ""
            country = str(r.get("country") or "").strip()
            place = ", ".join(x for x in (str(r.get("city") or "").strip(), str(r.get("state") or "").strip(),
                                          country if country.lower() not in US_NAMES | {"nan"} else "") if x)
            words = ", ".join(x for x in (*parts, place) if x)
            # session 3334 (faults file row 118): W44's row said 52 MW above a table of 10,400, 700 and 520 MW loads that
            # name no operator or site; the row says how many larger ones it leaves out, and why
            big = unnamed[unnamed["_m"] > float(r["_m"])]
            big = big[[row_passes(x, "datacenter_projects") for x in big.to_dict("records")]] if len(big) else big
            if len(big):
                words += (f" ({len(big)} larger {'load' if len(big) == 1 else 'loads'} of the week "
                          f"{'names' if len(big) == 1 else 'name'} no operator, developer or site; "   # 3462, row 162
                          f"{'it is' if len(big) == 1 else 'they are'} in the table below)")
            L.append(f"- **Largest new datacenter load first reported this week:** {float(r['_m']):,.0f} MW, {words}.")
            keys.append(f"the datacenter load, `datacenter_projects` {r['entity_id']}")
            picked["dc"] = {"mw": float(r["_m"]), "text": L[-1].split(":** ", 1)[1].rstrip(".")}
        else:
            L.append("- **Largest new datacenter load first reported this week:** "
                     + stand_in(2, "no facility with an operator or a site first reported this week states its MW" if not dc_under else
                                f"no facility first reported this week with its MW passes the datacenter table's floor ({dc_under} under it)"))
    # 5. the chart's figure
    meta = os.path.join(ANALYSIS_DIR, label, "chart_of_the_week.json")
    try:
        import json
        m = json.load(open(meta, encoding="utf-8"))
        h = m["headline"]
        # session 1446 (fault 28): the chart's latest period is often the week before (the run draws it before the
        # week's closes are held); the row says whose week the figure is
        whose = ""
        ends = re.findall(r"\d{4}-\d{2}-\d{2}", str(h.get("period", "")))
        if ends and pd.Timestamp(ends[-1], tz="UTC") < start:
            whose = " (the week before: the chart's latest period ends before this week)"
        L.append(f"- **From the chart of the week:** {h['label']}: {chart_figure(h['value'])} {h['unit']} in {h['period']}{whose}.")
        keys.append(f"the chart's figure, template `{m['template']}`, `docs/analysis/{label}/chart_of_the_week.json`")
    except (OSError, KeyError, ValueError):
        L.append("- **From the chart of the week:** no chart of the week was picked for this week, so no figure.")
    keys = five_marks(L, facts) + keys   # session 1882 (row 70): every mark the five print is named on their Tables line
    log(f"  five numbers: {len(L)} lines")
    return L + (["", "Tables: " + "; ".join(keys) + "."] if keys else [])


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


WEEK_FUEL_PCT = 3.0         # session 1446: a benchmark's close a week apart that moved this much, named by a story, opens
UNNAMED_FACTOR = 1.5        # a benchmark move no story names needs this much more (4.5 percent)


def is_hub(m):
    return "day-ahead" in str(m.get("label", ""))


def opening_number(picked, stories=None):
    """The Roundup's opening number: the number that best explains the week, by the brand's tests (system scale,
    persistence, relevance to capital or infrastructure decisions, source strength), chosen by rule among the week in
    five numbers (`picked`, as five_numbers fills it) and the top story's figure, in this order (session 1446, fault 25;
    the largest percentage move is never the choice by default, and a single hub's weekly mean is the last resort):
      1. a benchmark's close a week apart (Henry Hub, WTI, Brent) that moved WEEK_FUEL_PCT or more and that a story of the
         week names (brief.price_reason over `stories`): persistent, market-wide, named by the week, the warehouse's own;
      2. else the deal of the week, when it is DEAL_USD_MIN or more: relevance to capital decisions;
      3. else the largest datacenter load first reported this week, when it is DC_MW_MIN MW or more: infrastructure;
      4. else the top story's structural figure (a MW, a sum: picked["story"], as main fills it), the outlet's;
      5. else a benchmark move no story names, at UNNAMED_FACTOR times the bar;
      6. else a hub's weekly mean move of WEEK_MOVE_PCT or more (a story naming the grid first);
      7. else the US48 peak of the week: system scale (observed, EIA-930).
    Returns {key, text, status} or None when the week holds none of them."""
    deal, dc, us48, story = (picked.get(k) for k in ("deal", "dc", "us48", "story"))
    moves = picked.get("moves") or ([picked["move"]] if picked.get("move") else [])
    named = {m["label"]: brief.price_named(m["label"], stories, m.get("pct")) if stories is not None and len(stories) else False for m in moves}
    fuel = [m for m in moves if not is_hub(m)]
    hubs = [m for m in moves if is_hub(m)]

    def mover(m):
        # session 3312 (faults file row 101): the move carries the naming story's line, as the Digest's mover does
        why = brief.price_reason(m["label"], stories, m.get("pct")) if stories is not None and len(stories) else ""
        if not why and stories is not None and len(stories):   # row 101: the naming story's title when no line passes
            why = brief.price_story(m["label"], stories, m.get("pct"))
        return {"key": "move", "text": m["text"], "status": "calculated from observed prices (the warehouse's tables)", "move": m,
                "reason": why.replace("from the day's stories", "from the week's stories")}
    for m in fuel:
        if named[m["label"]] and abs(float(m["pct"])) >= WEEK_FUEL_PCT:
            return mover(m)
    if deal and deal.get("usd") and float(deal["usd"]) >= DEAL_USD_MIN:
        return {"key": "deal", "text": deal["text"], "status": "reported, extracted from the week's stories, every number checked against its story"}
    if dc and dc.get("mw") and float(dc["mw"]) >= DC_MW_MIN:
        return {"key": "datacenter", "text": dc["text"], "status": "reported, as its stories state it"}
    if story and story.get("text"):
        return {"key": "story", "text": story["text"], "status": "reported by the outlet, not a warehouse table's figure"}
    for m in fuel:
        if abs(float(m["pct"])) >= WEEK_FUEL_PCT * UNNAMED_FACTOR:
            return mover(m)
    for m in sorted(hubs, key=lambda m: (not named[m["label"]], -abs(float(m["pct"])))):
        if abs(float(m["pct"])) >= WEEK_MOVE_PCT:
            return mover(m)
    if us48:
        return {"key": "us48", "text": us48["text"], "status": "observed (EIA-930 hourly demand)"}
    return None


def opening_lines(op):
    L = ["## The opening number", ""]
    if op is None:
        return L + ["The week holds none of the five numbers this section reads.", ""]
    return L + [f"**{op['text'].rstrip('.')}.** Status: {op['status']}.{op.get('reason') or ''}", ""]   # row 101: the reason


SUBJECT_HEAD_MAX = 70


def short_head(head, n=SUBJECT_HEAD_MAX):
    """A headline cut at a word to n characters, with an ellipsis of three stops."""
    head = " ".join(str(head or "").split())
    if len(head) <= n:
        return head
    cut = head[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "..."


def subject_line(op, first_head):
    """ERW Weekly | <plain description of the week>, with a second clause of one verified metric and unit when the
    opening number is a warehouse figure (the price move of the week). Session 1446 (fault 34): the headline is cut at a
    word to SUBJECT_HEAD_MAX characters, the move said in plain words ("Brent down 6.4% on the week")."""
    # session 1475 (chain 154, fault 53): the headline's sums in the issue's money style ("$4 Billion" to "USD 4 billion"),
    # and when the opening number is the week's move, the move leads ("ERW Weekly | Brent down 13.1% on the week; AEP and
    # Google advance ..."): the subject opens on what the issue opens on
    head = short_head(brief.money_style(brief.nodash(str(first_head or "the week's energy news"))).rstrip("."))
    mv = (op or {}).get("move")
    if mv and mv.get("label"):
        label = str(mv["label"]).replace(" day-ahead", " day-ahead power").replace("WTI Cushing crude", "WTI").replace("Brent crude", "Brent").replace("Henry Hub natural gas", "Henry Hub gas")
        pct = float(mv["pct"])
        lead = f"ERW Weekly | {label} {'up' if pct >= 0 else 'down'} {abs(pct):.1f}% on the week"
        # session 1882 (faults file row 62): the whole subject at most SUBJECT_MAX, the headline clause with no figure (the
        # move is the subject's one verified metric, chain 131) and cut at a word with no "..."
        clause = head_clause(brief.money_style(brief.plain(brief.nodash(str(first_head or "")))).rstrip("."), SUBJECT_MAX - len(lead) - 2)   # row 131
        return f"{lead}; {clause}" if clause else lead
    # session 1990 (faults file row 95): with no move to lead, the headline's clause still carries no figure (chain 131: a
    # figure in the subject only when it is a warehouse table's), as the Digest's subject since row 89
    clause = brief.subject_clause(first_head) if first_head else ""
    return f"ERW Weekly | {clause or 'the week' + chr(39) + 's energy news'}"


SUBJECT_MAX = 90
CLAUSE_TAIL = re.compile(r"(?:\s+(?:a|an|the|of|to|in|on|for|with|from|by|at|and|or|its|their|as|into|over))+$", re.I)
# session 3464 (faults file row 165): a quantity's words before the figure go with it ("Taiwan Commits Up to to Alaska LNG
# Megaproject", the stack's subject of 14 October, of "Taiwan Commits Up to $4.4 Billion to Alaska LNG Megaproject")
QUANTITY_WORDS = r"(?:\b(?:up to|more than|less than|at least|as much as|about|around|nearly|almost|roughly|some|over|under)\s+)?"
# and (row 165) a capacity's "of" goes with it ("adds 2 GW of solar" to "adds solar"), and a percent sign is matched with no
# word boundary after it ("with 30% of output" kept its figure in the subject before)
FIGURE_IN_HEAD = re.compile(r"(?:\b(?:a|an)\s+)?" + QUANTITY_WORDS + r"(?:USD|CAD|AUD|EUR|GBP)\s\d[\d,.]*(?:\s(?:billion|million|trillion|thousand))?,?\s*|"
                            r"(?:\b(?:a|an)\s+)?" + QUANTITY_WORDS + r"\d[\d,.]*[\s-]?(?:(?:MW|GW|kW|MWh|GWh|TWh|kV|bcf/d|bcf|mtpa|percent)\b|%)"
                            r"(?:\s+of\b)?,?\s*", re.I)   # 3352: "3.6-GW"


# Session 3460 (faults file row 157): a cut inside a phrase leaves it without its noun ("ERW Daily | Centrus and Oklo
# finalise fuel agreements for up to five Aurora", 13 November 2026, of "... for up to five Aurora powerhouses at Ohio
# campus"). Such a cut goes back to before the phrase's preposition; a quantity's "up to", "more than", "at least" is no
# phrase of its own.
PHRASE_START = re.compile(r"\s(?:for|at|in|with|to|of|on|from|by|after|over|into|near|across|amid|under|as|via)\b", re.I)
QUANTITY = re.compile(r"\b(?:up to|more than|less than|fewer than|as many as|as much as|at least|at most)\b", re.I)
PHRASE_MIN_WORDS = 4


def phrase_back(t, full):
    """t, a cut of full at a word: when the first word cut off is a lower-case word inside a phrase (not a preposition,
    which would begin the next phrase), t back to before its last preposition, if PHRASE_MIN_WORDS words or more are left;
    else t as it is. A cut before a name is the caller's (subject_clause)."""
    rest = full[len(t):].split()
    first = rest[0].strip(",;:") if rest else ""
    if not first or not first[:1].islower() or PHRASE_START.fullmatch(" " + first):
        return t
    masked = QUANTITY.sub(lambda m: "#" * len(m.group(0)), t)
    starts = [m.start() for m in PHRASE_START.finditer(masked)]
    if not starts:
        return t
    back = t[:starts[-1]].rstrip(" ,;:")
    return back if len(back.split()) >= PHRASE_MIN_WORDS else t


def head_clause(head, n):
    """Session 1882 (row 62): a headline as the subject's second clause: its figures taken out (a sum, a capacity; the
    article before the first figure kept as "a"), then cut at a word to n characters with no ellipsis, a trailing article,
    preposition or conjunction dropped. "" when nothing readable is left."""
    t = " ".join(str(head or "").split())
    # session 3365 (faults file row 140): a headline's kicker before a colon ("Azerbaijan: TotalEnergies Announces ...",
    # "Exclusive: ...") is no part of the clause, and it took the space the clause needs
    t = re.sub(r"^[A-Z][\w.'&-]*(?: [A-Z][\w.'&-]*)?\s*[:|]\s+(?=[A-Z])", "", t)
    had = bool(FIGURE_IN_HEAD.search(t))
    t = FIGURE_IN_HEAD.sub(lambda m: "a " if re.match(r"(?:a|an)\s", m.group(0), re.I) else "", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" ,;:")
    if had:
        t = brief.fix_article(t)
        if str(head or "")[:1].isupper():   # session 3464 (row 165): "A 500 MW deal ..." reads "A deal ...", not "a deal ..."
            t = t[:1].upper() + t[1:]
    if len(t) > n:
        full = t
        t = t[:n + 1].rsplit(" ", 1)[0].rstrip(",;:")
        # session 3334 (faults file row 116): a cut that leaves a clause's first word or two after a comma ("EQT to Buy
        # Range Resources, Creating", W44) goes back to the comma
        if ", " in t and len(t.rsplit(", ", 1)[1].split()) <= 2:
            t = t.rsplit(", ", 1)[0]
        t = phrase_back(t, full)
    t = CLAUSE_TAIL.sub("", t).strip(" ,;:")
    return t if len(re.findall(r"[A-Za-z]+", t)) >= 2 else ""


def utc_ts(t):
    """A timestamp in UTC (a naive one read as UTC), or None."""
    if t is None or (not isinstance(t, pd.Timestamp) and pd.isna(t)):
        return None
    t = pd.Timestamp(t)
    if pd.isna(t):
        return None
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def day_month(t):
    """A day as '5 November' (no year: the masthead's week names it)."""
    return f"{t.day} {t:%B}"


def stories_short(cut, newest):
    """Session 1882 (faults file row 59): the newest story held, in UTC, when it is more than brief.STORIES_SHORT_HOURS
    before the cut (the ingest or the scorer stopped short of it); else None."""
    newest = utc_ts(newest)
    if newest is None or utc_ts(cut) - newest <= pd.Timedelta(hours=brief.STORIES_SHORT_HOURS):
        return None
    return newest


def cutoff_line(cut, newest=None, tables_to=None):
    """The masthead's cutoff. As the Digest's rule (brief.masthead_lines, session 1444): when the newest story held is more
    than STORIES_SHORT_HOURS before the cut, the line says where the stories stop, with its date when that is another day
    than the cut's (Eastern), and how far the week's tables reach (`tables_to`, the newest hour the numbers read) when they
    stop on an earlier day than the cut. Session 1882 (row 59): W45 claimed "Sources through 18:26 ET, 23:26 UTC" on 8
    November with no story after 5 November."""
    cut = utc_ts(cut)
    short = stories_short(cut, newest)
    if short is None:
        return brief.cutoff_words(cut).replace("Data through", "Sources through")
    et, cet = short.tz_convert(brief.EASTERN), cut.tz_convert(brief.EASTERN)
    day = f"{day_month(et)}, " if et.date() != cet.date() else ""
    line = f"Stories through {day}{et:%H:%M} ET, {short:%H:%M} UTC"
    tables_to = utc_ts(tables_to)
    if tables_to is not None and tables_to.tz_convert(brief.EASTERN).date() < cet.date():
        # session 3312 (faults file row 100): the reach is the real-time tables' (facts["reach"]); EIA's closes, the opening
        # number's table, can reach a day further, so "the week's tables" contradicted the first figure under it
        line += (f"; the real-time price tables reach {day_month(tables_to.tz_convert(brief.EASTERN))} (each table's reach is under "
                 "ERW's Numbers This Week).")
    else:
        line += f"; cut at {cet:%H:%M} ET, {cut:%H:%M} UTC."
    return line


def intro_span(start, end, cut, newest=None):
    """The intro's span: the week's dates, then where the stories stop when they stop on a day before the cut's (row 59:
    "(no story after 2026-11-05 is held)"), else the cut when the week is cut short. Never "to ... to"."""
    span = f"{start:%Y-%m-%d} to {(end - pd.Timedelta(days=1)):%Y-%m-%d}"
    short = stories_short(cut, newest)
    if short is not None and short.date() < (utc_ts(cut) - pd.Timedelta(microseconds=1)).date():
        return span + f" (no story after {short:%Y-%m-%d} is held)"
    if cut < end:
        return span + f", cut at {cut:%Y-%m-%d %H:%M} UTC"
    return span


def weekend_empty_line(wk_start, newest=None):
    """Session 1882 (row 60): the Weekend's line when it has no item. The warehouse holding no story of the weekend is not
    "no story was published": the line says what is held, and when the newest story is before the weekend, its time."""
    sat, sun = wk_start, wk_start + pd.Timedelta(days=1)
    days = (f"{sat.day} or {sun.day} {sun:%B}" if sat.month == sun.month else f"{day_month(sat)} or {day_month(sun)}")
    newest = utc_ts(newest)
    if newest is not None and newest < utc_ts(wk_start):
        return (f"- No story of {days} is held: the newest story the warehouse holds is of {day_month(newest)}, "
                f"{newest:%H:%M} UTC.")
    return f"- No other story of {days} is held."


def masthead_lines(label, end, cut, op, first_head, missed, newest=None, tables_to=None):
    return ([f"# {V2_TITLE}, {label}", "", f"**Week ending {brief.day_words(end - pd.Timedelta(days=1))}.** "
             f"{cutoff_line(cut, newest, tables_to)}", ""]
            + ([missed, ""] if missed else [])
            + [f"<!-- subject: {subject_line(op, first_head)} -->", "", f"<!-- opening: {(op or {}).get('key', '')} -->", ""])


# Session 1894 (faults file row 63): a story of the week that is a step in a deal energy_deals already holds. W45's first
# item, "AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell project in Cheyenne", was told "the 702 MW is
# the outlet's figure, not a warehouse table's; one outlet has reported it so far", while energy_deals has held the deal
# (Google and AEP, 702 MW, USD 4 billion, a 20-year PPA) since 2026-10-14, from five stories.
PARTY_LEGAL = {"inc", "corp", "corporation", "co", "company", "llc", "lp", "ltd", "plc", "sa", "ag", "nv", "se", "the"}
DEAL_PARTY_COLS = ("parties", "buyer", "seller", "other_parties", "buyer_name", "seller_name", "buyer_parent", "seller_parent")
MONEY_VALUE = re.compile(r"(?:US\$|\$|USD ?)\s?([\d][\d,]*(?:\.\d+)?)\s?(trillion|billion|million|bn|mn|tn|b|m)?\b", re.I)
MONEY_SCALE = {"trillion": 1e12, "tn": 1e12, "billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "mn": 1e6, "m": 1e6}


def party_key(name):
    """A party's name for matching: lower case, letters and digits, the legal suffixes left out ("AEP, Inc." and "aep" are
    one)."""
    t = re.sub(r"[^a-z0-9 ]+", " ", str(name or "").lower().replace("&", " and "))
    return " ".join(w for w in t.split() if w not in PARTY_LEGAL)


def money_value(text):
    """A sum of money a scored field states, in US dollars ("$4 Billion" is 4e9); None when it states none."""
    m = MONEY_VALUE.search(str(text or ""))
    if not m:
        return None
    try:
        v = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    return v * MONEY_SCALE.get((m.group(2) or "").lower(), 1.0)


def as_float(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x else None   # NaN is no figure


def deal_index(deals):
    """energy_deals as the look-up of prior_deal reads it, built once: (date, party keys, MW, US dollars, row) of every row
    that passes the Deals table's floor and states a MW or a sum. [] when the table is not on the machine."""
    if deals is None or not len(deals) or "event_date" not in deals.columns:
        return []
    out = []
    for d in deals.to_dict("records"):
        if not row_passes(d, "energy_deals"):
            continue
        mw, usd = as_float(d.get("mw")), as_float(d.get("dollars"))
        if mw is None and usd is None:
            continue
        try:
            when = pd.Timestamp(str(d["event_date"]))
        except (ValueError, TypeError):
            continue
        when = when.tz_localize("UTC") if when.tzinfo is None else when.tz_convert("UTC")
        keys = {party_key(x) for c in DEAL_PARTY_COLS for x in str(d.get(c) or "").split(";")} - {""}
        out.append((when, keys, mw, usd, d))
    return out


def prior_deal(r, index, before):
    """The energy_deals row a story of the week is a step in: the same parties (two or more of the story's scored parties
    among the row's), the same quantity (the story's MW, else its sum of money, equal to the row's) and a date before
    `before` (the week's start). The earliest such row, or None."""
    mine = {party_key(x) for x in str(r.get("parties") or "").split(";")} - {""}
    if len(mine) < 2 or not index:
        return None
    mw, usd = as_float(r.get("mw")), money_value(r.get("price"))
    if mw is not None and mw <= 0:
        mw = None
    if mw is None and not usd:
        return None
    best = None
    for when, keys, dmw, dusd, d in index:
        if when >= before or len(mine & keys) < 2:
            continue
        same = ((mw is not None and dmw is not None and abs(mw - dmw) < 0.5)
                or (mw is None and usd and dusd and abs(usd / dusd - 1) < 0.005))
        if same and (best is None or when < best[0]):
            best = (when, d)
    return best[1] if best else None


# Session 1908 (faults file row 63, its open part): the fix asked that the step be found in energy_deals "and the earlier
# issues' items". A deal the table does not hold may still have been an earlier Digest's item: the Digest prints each item's
# scored fields under its headline ("702 MW; $4 billion; parties: Google; AEP; Bloom Energy."), so the same parties and the
# same quantity name the item. The table is read first; an item only where no row matches.
DIGEST_DIR = os.path.join(ROOT, "docs", "digest")
ISSUE_HEAD = re.compile(r"^(\d+)\. \*\*(.+?)\*\*")
ISSUE_FIELDS = re.compile(r"^\s+(.*?); [Pp]arties: (.+?)\. Sources:")   # session 3350 (row 130): either case
ISSUE_MW = re.compile(r"^([\d,]+(?:\.\d+)?) MW$")
ISSUE_SUM = re.compile(r"(?:US\$|\$|USD ?)\s?[\d][\d,]*(?:\.\d+)?\s?(?:trillion|billion|million|bn|mn|tn)?$", re.I)


def issue_items(text):
    """The items of one stored Digest that print their scored fields: (number, headline, party keys, MW, US dollars)."""
    out, lines = [], str(text).splitlines()
    for i, ln in enumerate(lines[:-1]):
        h, f = ISSUE_HEAD.match(ln), ISSUE_FIELDS.match(lines[i + 1])
        if not h or not f:
            continue
        pieces = f.group(1).split("; ")
        pieces[0] = pieces[0].rsplit(". ", 1)[-1]   # the why line runs into the first field
        mw = next((float(m.group(1).replace(",", "")) for m in map(ISSUE_MW.match, pieces) if m), None)
        # a sum ends its field (the why line may run into it: "... supply agreement $4.4 Billion"); a price per unit
        # ("$106.37") is no deal's sum, so a sum under a million is not one
        sums = [money_value(m.group(0)) for m in map(ISSUE_SUM.search, pieces) if m]
        usd = next((v for v in sums if v and v >= 1e6), None)
        keys = {party_key(x) for x in f.group(2).split(";")} - {""}
        if mw is None and usd is None:
            continue
        out.append((int(h.group(1)), h.group(2), keys, mw, usd))
    return out


def issue_index(folder=None):
    """Every stored Digest's items with scored fields, as prior_item reads them: (date, party keys, MW, US dollars, item),
    the item {"issue": "Digest", "date", "n", "head"}. [] when the folder is absent."""
    folder = folder or DIGEST_DIR
    if not os.path.isdir(folder):
        return []
    out = []
    for name in sorted(os.listdir(folder)):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.md", name)
        if not m:
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as fh:
            text = fh.read()
        when = pd.Timestamp(m.group(1), tz="UTC")
        for n, head, keys, mw, usd in issue_items(text):
            out.append((when, keys, mw, usd, {"issue": "Digest", "date": m.group(1), "n": n, "head": head}))
    return out


def prior_item(r, index, before):
    """The earlier Digest item a story of the week is a step in, by prior_deal's rule (two of the story's parties, the same
    MW, else the same sum, an issue dated before `before`): the earliest, or None."""
    return prior_deal(r, index, before)


def first_reports_first(clusters, steps):
    """Row 63: What mattered ranks the week's first reports above a step in a deal first reported before the week (the
    clusters keep their order otherwise). steps: {cluster_id: energy_deals row}."""
    if not steps or clusters.empty:
        return clusters
    k = clusters["cluster_id"].isin(set(steps)).astype(int)
    return clusters.assign(_step=k).sort_values("_step", kind="stable").drop(columns="_step").reset_index(drop=True)


def an(word):
    return f"an {word}" if str(word)[:1].lower() in "aeiou" else f"a {word}"


def deal_summary(d):
    """A held deal in words: "Google and AEP, Wyoming fuel cell project, 702 MW, USD 4 billion, a 20-year power purchase
    agreement"."""
    fin = finance_words(d)
    if fin:
        head = re.sub(r" \(\d{4}-\d{2}-\d{2}\)$", "", fin)
    else:
        asset = asset_words(d.get("asset"))
        parties = [str(x).strip() for x in (d.get("buyer"), d.get("seller")) if str(x or "").strip()]
        parties = [x for i, x in enumerate(parties) if x not in parties[:i] and x.lower() not in asset.lower()]
        head = ", ".join(x for x in (" and ".join(parties), asset) if x)
    parts = [head] if head else []
    mw, usd = as_float(d.get("mw")), as_float(d.get("dollars"))
    if mw is not None:
        parts.append(f"{mw:,.0f} MW")
    if usd is not None:
        parts.append(usd_words(usd))
    kind = str(d.get("deal_type") or "")
    label = "" if kind in ("other", "") or fin else DEAL_LABEL.get(kind, kind.replace("_", " "))
    term = as_float(d.get("term_years"))
    if term and label:
        parts.append(f"a {term:g}-year {label}")
    elif label:
        parts.append(an(label))
    return ", ".join(parts)


def step_line(d):
    """Row 63: the sentence that says a story is a step in a held deal, with the row's date and figures. Session 1908: or
    in a story an earlier Digest carried, with the issue's date, the item's number and its headline."""
    if d.get("issue"):
        return (f"A step in a story first carried before this week: the {d['issue']} of {d['date']}, item {d['n']} "
                f"(\"{d['head']}\").")
    return (f"A step in a deal first reported before this week: in `energy_deals` since {str(d.get('event_date') or '')[:10]} "
            f"({deal_summary(d)}).")


# Session 1895 (faults file rows 64 and 68): a plant a story names, looked up in eia860m_planned_generators (the data
# machine's table; a code machine may hold a restored copy, or none). W45's third item, "Orsted completes Revolution Wind, a
# 704 MW offshore wind farm", was told "the 704 MW is the outlet's figure, not a warehouse table's" while the table lists
# Revolution Wind (plant 65500) at 715 MW nameplate, planned for 2026-11-01 (EIA-860M, September 2026).
PLANT_TAIL = {"llc", "inc", "lp", "llp", "ltd", "project", "facility", "plant"}
PLANT_GENERIC = {"solar", "wind", "energy", "storage", "battery", "bess", "project", "farm", "power", "center", "centre", "plant",
                 "station", "generating", "generation", "hybrid", "pv", "park", "gas", "hydroelectric", "hydro", "facility",
                 "offshore", "onshore", "renewable", "renewables", "clean", "and", "the", "of", "at", "llc", "inc", "lp", "phase",
                 "unit", "units", "expansion", "north", "south", "east", "west", "new", "county", "city", "creek", "road",
                 "lake", "river", "ranch", "hills", "valley", "landfill", "nuclear", "steam", "turbine", "fuel", "cell", "cells",
                 "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "sr", "csg"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]


def plant_text(text):
    """A text in the look-up's form: lower case, '&' as 'and', every other sign a space, one space between words."""
    t = re.sub(r"[^a-z0-9]+", " ", str(text or "").lower().replace("&", " and "))
    return " ".join(t.split())


def plant_key(name):
    """A plant's EIA name as the look-up matches it, or "" when it is too plain to name one plant in a headline: the
    bracketed part and a legal or "project" tail left out; two words or more, one of them not a generic word ("Revolution
    Wind" passes, "Solar Project" and "Kalmar" do not)."""
    words = plant_text(re.sub(r"\([^)]*\)", " ", str(name or ""))).split()
    while words and words[-1] in PLANT_TAIL:
        words = words[:-1]
    if len(words) < 2 or not any(w not in PLANT_GENERIC and not w.isdigit() and len(w) >= 3 for w in words):
        return ""
    return " ".join(words)


def vintage_words(v):
    """'2026-09' as 'September 2026'; "" when the vintage is not a month."""
    m = re.fullmatch(r"(\d{4})-(\d{2})", str(v or "").strip())
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m and 1 <= int(m.group(2)) <= 12 else ""


def plant_index(gens):
    """eia860m_planned_generators as the look-up reads it, built once: {plant key: [plant, ...]}, each plant its EIA name,
    nameplate MW summed over its generators, planned dates, vintage, technology, state and entity ids. {} when the table
    is not on the machine or lacks the columns the look-up needs."""
    need = {"name", "plant_id", "planned_operation_date", "vintage"}
    if gens is None or not len(gens) or not need <= set(gens.columns) or not ({"nameplate_mw", "capacity_mw"} & set(gens.columns)):
        return {}
    plants = {}
    for g in gens.to_dict("records"):
        key = plant_key(g.get("name"))
        pid = str(g.get("plant_id") or "").strip()
        mw = as_float(g.get("nameplate_mw")) if "nameplate_mw" in g else None
        if mw is None:
            mw = as_float(g.get("capacity_mw"))
        if not key or not pid or mw is None:
            continue
        p = plants.setdefault(pid, dict(key=key, name=str(g["name"]).strip(), plant_id=pid, mw=0.0, dates=set(), ids=[],
                                        vintage=str(g.get("vintage") or "").strip(), technology=str(g.get("technology") or "").strip(),
                                        state=str(g.get("state") or "").strip()))
        p["mw"] += mw
        if str(g.get("planned_operation_date") or "").strip():
            p["dates"].add(str(g["planned_operation_date"]).strip()[:10])
        if str(g.get("entity_id") or "").strip():
            p["ids"].append(str(g["entity_id"]).strip())
    out = {}
    for p in plants.values():
        p["dates"] = sorted(p["dates"])
        out.setdefault(p["key"], []).append(p)
    return out


def planned_plant(r, head, index):
    """The plant of eia860m_planned_generators a story names in its headline or its titles: the longest plant key found
    whole in them, when it is one plant's (a name two plants share names neither). None when no plant is named or the
    table is not on the machine."""
    if not index:
        return None
    text = f" {plant_text(' '.join([str(head or '')] + [str(t) for t in (r.get('titles') or [])]))} "
    found = [k for k in index if f" {k} " in text]
    if not found:
        return None
    best = max(found, key=len)
    if len(index[best]) != 1 or sum(1 for k in found if len(k) == len(best)) > 1:
        return None
    return index[best][0]


def mw_words(v):
    return f"{v:,.0f}" if float(v) == int(v) else f"{v:,.1f}"


def plant_words(p, fig=""):
    """Row 64: what EIA-860M lists for the plant, against the story's MW: "EIA-860M (September 2026) lists Revolution Wind at
    715 MW nameplate, planned for 2026-11-01; the 704 MW is the outlet's, and EIA has not yet listed the plant as
    operating". The table is of planned generators, so a plant in it is not yet listed as operating."""
    d = p["dates"]
    when = (f"planned for {d[0]}" if len(d) == 1 else f"planned for {d[0]} to {d[-1]}") if d else "with no planned date stated"
    vin = vintage_words(p.get("vintage"))
    s = f"EIA-860M{f' ({vin})' if vin else ''} lists {p['name']} at {mw_words(p['mw'])} MW nameplate, {when}"
    fmw = None
    m = re.fullmatch(r"([\d,.]+) MW", str(fig or ""))
    if m:
        fmw = as_float(m.group(1).replace(",", ""))
    if fmw is not None and abs(fmw - p["mw"]) >= 0.5:
        return s + f"; the {fig} is the outlet's, and EIA has not yet listed the plant as operating"
    if fmw is not None:
        return s + ", as the outlet reports; EIA has not yet listed the plant as operating"
    return s + "; EIA has not yet listed the plant as operating"


def capacity_words(cap):
    """Row 68: the five's capacity stand-in from the look-up: "Revolution Wind (offshore wind turbine, RI), named in the
    week's stories (POWER Magazine): EIA-860M (September 2026) lists it at 715 MW nameplate, planned for 2026-11-01"."""
    p, r = cap["plant"], cap["rec"]
    what = ", ".join(x for x in (p.get("technology", "").lower(), p.get("state", "")) if x)
    d = p["dates"]
    when = (f"planned for {d[0]}" if len(d) == 1 else f"planned for {d[0]} to {d[-1]}") if d else "with no planned date stated"
    vin = vintage_words(p.get("vintage"))
    return (f"{p['name']}{f' ({what})' if what else ''}, named in the week's stories ({brief.outlet_of(r)}): "
            f"EIA-860M{f' ({vin})' if vin else ''} lists it at {mw_words(p['mw'])} MW nameplate, {when}")


def more_why(r, heads, steps):
    """Row 63: an item under More (the weekend's, the week's five) keeps its why line, and a step in a held deal says so."""
    why = brief.why_line(r['why'], heads[r['cluster_id']], r.get('mw'))   # the form tests/test_session801.py counts; 3465
    d = steps.get(r["cluster_id"])
    return " ".join(x for x in (why, step_line(d) if d is not None else "") if x)


def bench_of(r, facts):
    """Session 1993 (faults file row 98): the benchmark a story names (brief.names_price on its title and why line), as
    the week's fuel table holds it (facts["fuel"]: the newest close and the close a week before), or None. A crude story
    that names neither crude takes Brent."""
    text = f" {' '.join(str(t) for t in (r.get('titles') or []))} {r.get('why') or ''} ".lower()
    named = [f for f in (facts or {}).get("fuel", []) if brief.names_price(f["label"], text)]
    if not named:
        return None
    own = [f for f in named if f["label"].split()[0].lower() in text]
    return (own or [f for f in named if f["label"] == "Brent crude"] or named)[0]


STORY_DAY_SLACK = 3   # session 3473 (row 174): the days a story's day's close may lie before it (a weekend, a holiday)


def story_day_closes(f, when):
    """Session 3473 (faults file row 174): (the close of a story's trading day, the close before it) from the week's
    closes (f["s"]), the story's day read in Eastern time ("Oil settles $3 higher ..." at 2026-11-12 01:52 UTC is the
    settle of 11 November); None when the series is not held or holds no close within STORY_DAY_SLACK days of it."""
    s, t = f.get("s"), utc_ts(when)
    if s is None or t is None or not len(s):
        return None
    day = t.tz_convert("America/New_York").normalize().tz_localize(None)
    d = pd.to_datetime(s["ts_utc"], utc=True).dt.tz_localize(None).dt.normalize()
    upto = s[d <= day]
    if len(upto) < 2:
        return None
    a, b = upto.iloc[-1], upto.iloc[-2]
    if (day - pd.Timestamp(a["ts_utc"]).tz_localize(None).normalize()).days > STORY_DAY_SLACK:
        return None
    return a, b


def bench_words(f, when=None):
    """Row 98: the week's close of a benchmark as the issue's fuel table prints it, with its mark. Session 3473 (row 174):
    for a story with its time (`when`), the close of the story's own day against the close before it, when held: W46's
    "Oil settles $3 higher ..." (11 November) was set beside the week's +0.30 USD/bbl, not the day's +1.98."""
    a, b = story_day_closes(f, when) or (f["a"], f["b"])
    return (f"the warehouse's {f['label']} close is {a['value']:.2f} {a['unit']} on {pd.Timestamp(a['ts_utc']):%Y-%m-%d}, against "
            f"{b['value']:.2f} on {pd.Timestamp(b['ts_utc']):%Y-%m-%d} {f['ref']}")


def evidence_gap(r, head="", deal=None, plant=None, bench=None):
    """What the evidence does not establish, from the record alone (session 1446, faults 30 and 31): the scored fields
    that are empty (no party named; no capacity or sum stated), a figure the headline states that is the outlet's and
    not a table's (a scored figure the headline does not hold is not claimed: "1GWh of storage" was printed as 1,000 MW),
    one outlet so far, an analysis piece. Nothing when every field is stated and the story is reported by more than
    one outlet: the sentence is not boilerplate.

    Session 1894 (row 63): when the story is a step in a deal energy_deals already holds (deal, from prior_deal), the
    figure is the table's and the deal has been reported before: the item says it is a step, names the row's date and
    figures, and the gap is what the week's step changes in that deal (an analysis piece is still said).

    Session 1895 (row 64): when the story names a plant eia860m_planned_generators lists (plant, from planned_plant), the
    gap says what EIA-860M lists (nameplate, vintage, planned date) against the outlet's MW, in place of "not a warehouse
    table's"; with no table on the machine, plant is None and the sentence is as before."""
    if deal is not None and deal.get("issue"):   # session 1908 (row 63): an earlier Digest's item, not a table's row
        fig = brief.story_figure(r)
        titles = " ".join(str(t) for t in (r.get("titles") or []))
        gaps = ["what the week's step changes in that story"]
        if fig and brief.figures_of(fig) & brief.figures_of(f"{head} {titles}"):
            gaps.append(f"the {fig} is the outlets' figure, not a warehouse table's")
        if r.get("kind") == "commentary":
            gaps.append("an analysis piece, not a reported event")
        return step_line(deal) + " What the evidence does not establish: " + "; ".join(gaps) + "."
    if deal is not None:
        gaps = ["what the week's step changes in that deal"]
        if r.get("kind") == "commentary":
            gaps.append("an analysis piece, not a reported event")
        return step_line(deal) + " What the evidence does not establish: " + "; ".join(gaps) + "."
    gaps = []
    fig = brief.story_figure(r)
    titles = " ".join(str(t) for t in (r.get("titles") or []))
    said = bool(fig and brief.figures_of(fig) & brief.figures_of(f"{head} {titles}"))
    if plant is not None:   # session 1895 (row 64): the table's listing, against the outlet's MW when the headline gives it
        mw_fig = fig if said and fig.endswith(" MW") else ""
        gaps.append(plant_words(plant, mw_fig))
        if said and not mw_fig:
            gaps.append(f"the {fig} is the outlet's figure, not a warehouse table's")
    elif said and bench is not None:
        # session 1993 (faults file row 98): a market move the warehouse holds: the table's close, not "not a table's"
        gaps.append(f"the {fig} is the outlet's figure; {bench_words(bench, r.get('first'))}")   # 3473, row 174
    elif said:
        gaps.append(f"the {fig} is the outlet's figure, not a warehouse table's")
    if not str(r.get("parties") or "").strip() and bench is None:   # row 98: a market move has no party to name
        gaps.append("no party is named")
    if not fig and plant is None:
        gaps.append("no capacity or sum is stated")
    lim = brief.limitation(r)
    if lim:
        gaps.append(lim[0].lower() + lim[1:].rstrip("."))
    if not gaps:
        return ""
    return "What the evidence does not establish: " + "; ".join(gaps) + "."


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
    out, seen, kinds = [], set(), set()
    for day, _sig, title, agency, sent, url in items:
        if title in seen:
            continue
        seen.add(title)
        # session 1447 (fault 36): one item of a kind (the agency and the sentence's kind of date) a day, so three FERC
        # comment deadlines on one Monday are one line, and the others wait for a different day or kind
        kind = (day, agency, event_kind(sent))
        if kind in kinds:
            continue
        kinds.add(kind)
        src = f" ([source]({url}))" if url.startswith("http") else ""
        # session 1897 (row 76): one line an item, the deadline in the row's form ("comments on the draft EIS due 17:00 Eastern")
        out.append(f"- **{brief.day_words(day)}**: {short_title(title)} ({agency}): {deadline_words(sent, day)}.{src}")
        if len(out) >= n:
            break
    log(f"  next week: {len(out)} dated item(s) of {len(items)} found in policy_reads")
    return sorted(out, key=lambda x: pd.Timestamp(re.search(r"\*\*(.+?)\*\*", x).group(1)))


NEXT_TITLE_MAX = 90


def short_title(title, n=NEXT_TITLE_MAX):
    """Session 1447 (fault 36): a filing's title cut at a word, never mid-word ("...Capacity Repl"), the docket's short
    name kept: the part before the first semicolon (the company) and the first clause after it, to n characters with an
    ellipsis of three stops when cut."""
    t = " ".join(str(title or "").split()).rstrip(".")
    parts = [p.strip() for p in t.split(";") if p.strip()]
    if len(parts) >= 2:
        t = f"{parts[0]}, {parts[1]}"
    if len(t) <= n:
        return t
    # session 1897 (row 76): a docket of several companies ("Cheniere Corpus Christi Pipeline, LP, Corpus Christi Liquefaction
    # Stage IV, LLC, Corpus..." was cut inside its list) keeps the short name of the company its subject names
    name = docket_company(title)
    if name:
        return name
    return t[:n].rsplit(" ", 1)[0].rstrip(",;:") + "..."


CORP_SUFFIX = re.compile(r"^(?:and\s+)?(?:L\.?\s?L\.?\s?C\.?|L\.?\s?P\.?|Inc\.?|Corp\.?|Co\.?|Ltd\.?|LLP)$", re.I)
CORP_TAIL = re.compile(r",?\s+(?:L\.?L\.?C|L\.?P|Inc|Corp|Ltd|LLP)\.?$", re.I)


def docket_companies(title):
    """The companies a filing's title opens with, their corporate suffixes taken off, and the title's subject (the first
    part that is not a company): "A Pipeline, LP, B Stage IV, LLC; Notice of ..." gives (["A Pipeline", "B Stage IV"],
    "Notice of ..."). Parts are separated by semicolons (a colon closes the list too); a part is a company while it ends in
    a corporate suffix, the first part always."""
    t = " ".join(str(title or "").split()).rstrip(".")
    parts = [p.strip() for p in re.split(r";|:\s", t) if p.strip()]
    if not parts:
        return [], ""
    heads, i = [parts[0]], 1
    while i < len(parts) and CORP_TAIL.search(parts[i]):
        heads.append(parts[i])
        i += 1
    subject = parts[i] if i < len(parts) else ""
    names = []
    for h in heads:
        for piece in re.split(r",\s*", h):
            piece = re.sub(r"^(?:(?:L\.?L\.?C|L\.?P|Inc|Corp|Ltd)\.?\s+)?and\s+", "", piece.strip())
            if piece and not CORP_SUFFIX.match(piece):
                piece = CORP_TAIL.sub("", piece).strip()
                if piece and piece not in names:
                    names.append(piece)
    return names, subject


def docket_company(title):
    """Session 1897 (row 76): the short name of a docket of several companies, the one whose words the title's subject holds
    most (the first on a tie): "Cheniere Corpus Christi Pipeline, LP, Corpus Christi Liquefaction Stage IV, LLC, Corpus
    Christi Liquefaction, LLC; Notice of Availability of the Draft Environmental Impact Statement for the Proposed Corpus
    Christi Liquefaction Stage 4 Project ..." gives "Corpus Christi Liquefaction Stage IV". One company: "" (the title is
    cut at a word as before)."""
    names, subject = docket_companies(title)
    t = " ".join(str(title or "").split())
    heads = t.split(subject)[0] if subject else t
    if len(names) < 2 or len(re.findall(r"\b(?:L\.?\s?L\.?\s?C|L\.?\s?P|Inc|Corp|Ltd|LLP)\b", heads)) < 2:
        return ""                       # two companies at least, each with its suffix ("City of Austin, Texas" is one name)
    held = {w.lower() for w in re.findall(r"[A-Za-z0-9]+", subject)}
    return max(names, key=lambda c: (sum(w.lower() in held for w in re.findall(r"[A-Za-z0-9]+", c)), -names.index(c)))


CLOCK = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s?m\.?(?:\s+(eastern|central|mountain|pacific)(?:\s+(?:standard|daylight|prevailing))?"
                   r"(?:\s+time)?)?", re.I)
COMMENT_FORMS = (
    re.compile(r"^(?:the\s+)?[\w.' -]+? must (?:receive|reach) (?P<what>(?:[\w,' -]+? )?comments?\b.*?) (?:by|on or before) (?P<when>.+)$", re.I),
    re.compile(r"^(?P<what>.*?\bcomments?\b.*?) (?:are|is) due(?: to (?:the )?[\w ]+?)? (?:by|on or before|on) (?P<when>.+)$", re.I),
    re.compile(r"^(?P<what>.*?\bcomments?\b.*?) must (?:be received|reach [\w ]+?)(?: by [\w ]+?)? (?:by|on or before) (?P<when>.+)$", re.I),
)


def clock_words(m):
    """A time of day as the issue writes it: 24-hour, its zone's name ("5:00 p.m. Eastern Time" is "17:00 Eastern")."""
    h, mins = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "p" else 0), m.group(2) or "00"
    return f"{h:02d}:{mins}" + (f" {m.group(4).title()}" if m.group(4) else "")


def deadline_words(sent, day):
    """Session 1897 (docs/reviews/periodicals-faults-2026-11-05.md, row 76): a dated sentence of policy_reads as one clause
    of the item's line. A comment deadline in the row's form: what is due, "due", the time of day in 24 hours with its
    zone, and the docket id the sentence gives ("FERC must receive comments on the draft EIS by 5:00 p.m. Eastern Time on
    November 9, 2026." is "comments on the draft EIS due 17:00 Eastern"); the day is the item's bold date, so it is not
    said again. Any other sentence, or one whose date is not the item's: the sentence as written, its first letter in
    lower case where the second is, its closing stop off."""
    s = " ".join(str(sent or "").split()).rstrip(".")
    date = f"{day.strftime('%B')} {day.day}, {day.year}"
    for form in COMMENT_FORMS:
        m = form.match(s)
        if not m or date not in m.group("when"):
            continue
        what = m.group("what").strip()
        before, _, after = m.group("when").partition(date)
        clock = CLOCK.search(before)
        rest = CLOCK.sub("", before) if clock else before
        if re.sub(r"\b(?:on|by|at|or|before)\b", "", rest).strip(" ,"):
            break                                   # words between the time and the date this form does not know
        docket = re.search(r"\bDocket (?:ID|No\.?|Number)\s*([A-Z0-9][\w.-]*[A-Za-z0-9])", after)
        what = what[0].lower() + what[1:] if len(what) > 1 and what[1].islower() else what
        return (f"{what} due" + (f" {clock_words(clock)}" if clock else "")
                + (f" (docket {docket.group(1)})" if docket else ""))
    # session 3480 (faults file row 179): "The final rule is effective on November 16, 2026" under the bold "16 November
    # 2026" said the day twice and in another form; a rule effective on the item's day "takes effect"
    m = EFFECTIVE.match(s)
    if m and m.group("when").strip(" ,") == date:
        what = m.group("what").strip()
        return (what[0].lower() + what[1:] if len(what) > 1 and what[1].islower() else what) + " takes effect"
    return s[0].lower() + s[1:] if len(s) > 1 and s[1].islower() else s


EFFECTIVE = re.compile(r"^(?P<what>.+?) (?:is|are|becomes|will be|will become|takes|take) effect(?:ive)? (?:on )?(?P<when>.+)$", re.I)


def event_kind(sentence):
    """The kind of a dated sentence: comments, effective, hearing, auction, release, deadline, or other."""
    s = str(sentence or "").lower()
    for word, kind in (("comment", "comment"), ("effect", "effective"), ("hearing", "hearing"), ("auction", "auction"),
                       ("release", "release"), ("deadline", "deadline")):
        if word in s:
            return kind
    return "other"


# Session 3473 (faults file row 173): "No dated events held this week" under "Next week" read as no event this week; the
# line is about the week ahead, as its second half said
NO_NEXT_WEEK = ("No event of the week ahead is held: the warehouse and the policy monitor hold no filing, auction, hearing, data "
                "release or project milestone dated in it.")


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
        # session 1894 (row 63): a story that is a step in a deal energy_deals held before the week is said so, and What
        # mattered ranks the week's first reports above it
        deal_ix = deal_index(read_table("energy_deals"))
        steps = {}
        for r in clusters.to_dict("records"):
            d = prior_deal(r, deal_ix, start)
            if d is not None:
                steps[r["cluster_id"]] = d
        log(f"  steps in deals held before the week: {len(steps)}")
        # session 1908 (row 63, its open part): where no row matches, an earlier Digest's item with the same parties and
        # quantity
        item_ix = issue_index()
        n_items = 0
        for r in clusters.to_dict("records"):
            if r["cluster_id"] not in steps:
                d = prior_item(r, item_ix, start)
                if d is not None:
                    steps[r["cluster_id"]] = d
                    n_items += 1
        log(f"  steps in stories an earlier Digest carried: {n_items}")
        clusters = first_reports_first(clusters, steps)
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

        newest = pd.to_datetime(s["event_date"], utc=True, format="ISO8601").max()   # session 1882 (rows 59, 60)
        span = intro_span(start, end, cut, newest)
        missed = missed_week_line(start)   # session 2702, rulings item 10
        intro = [  # session 21: one sentence (what, the period, the story count); the method is on /about#digest
             f"ERW's weekly roundup of energy news for {span}, from {len(s):,} scored stories.", "",   # 3334: row 117
             *([brief.NO_MODEL_LINE.replace("Today's", "This week's"), ""] if args.no_model else [])]
        # session 2704: the lines below are the fold ("More"); the page's order is assembled after the numbers
        L = ["### Weekend", ""]
        if weekend.empty:
            L.append(weekend_empty_line(wk_start, newest))   # session 1882 (row 60)
        for i, r in enumerate(weekend.to_dict("records"), 1):
            L += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({brief.sector_words(r['sector'])}, {r['n']} "
                                  f"{'story' if r['n'] == 1 else 'stories'})  ",
                                  more_why(r, heads, steps), f"Sources: {link_text(r['links'])}")  # 470, 577, 801, 802; 1894
        L += ["", "### The five stories of the week", ""]
        for i, r in enumerate(top5.to_dict("records"), 1):
            # session 21, ruling 4: the sector label, never the significance score
            L += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({brief.sector_words(r['sector'])}, {r['n']} "
                                  f"{'story' if r['n'] == 1 else 'stories'})  ",
                                  more_why(r, heads, steps), f"Sources: {link_text(r['links'])}")   # session 1894 (row 63)

        L += ["", "### Deals of the week", ""]
        deals = read_table("energy_deals")
        if deals is None:
            L.append("- energy_deals is not in the warehouse on this machine.")
        else:
            dw = deals[(pd.to_datetime(deals["event_date"], utc=True, format="ISO8601") >= start)
                       & (pd.to_datetime(deals["event_date"], utc=True, format="ISO8601") < cut)].sort_values("event_date")
            # session 2702, rulings item 11; session 3462 (row 161): the five's deal of the week is in the table
            shown_d, rest_d, under_d = floor_rows(dw, "energy_deals", keep=deal_of_week_id(dw))
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
                    kind, buyer, seller = deal_cells(r)   # session 1882 (row 67): no "other", a financing by its roles
                    # session 3445 (faults file row 150): a deal with no type says so, as every other empty cell does
                    L.append(f"| {r['event_date'][:10]} | {kind or 'not stated'} | {buyer} | "
                             f"{seller} | {asset_words(r['asset']) or 'not stated'} | {num(r['mw'])} | "
                             f"{usd_cell(r['dollars'])} | {r['status'] or 'not stated'} | [1]({first}) |")   # session 1476 (fault 54)
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
                    L.append(f"| {r['first_story_at'][:10]} | {dc_operator(r)} | "
                             f"{r['site_name'] or 'not stated'} | {dc_place(r)} | {num(r['mw'])} | "
                             f"{(r['project_status'] or 'not stated').replace('_', ' ')} | "
                             f"[1]({r['story_urls'].split(';')[0]}) |")
                L.append("")
                L.append(floor_note("datacenter_projects", "facilities", shown_c, rest_c, under_c)
                         + " `warehouse/datacenters/extract.py`, every field only as its story states it.")

        L += ["", "### ERW's Policy of the Week", ""] + policy_section(policy_of_the_week(start, cut, log), L, log)
        facts, picked = {}, {}
        nums = numbers(start, cut, log, facts)
        # session 1895 (rows 64 and 68): a plant a shown story names, looked up in eia860m_planned_generators (None
        # when the table is not on this machine: the lines are then as before)
        plant_ix = plant_index(read_table("eia860m_planned_generators"))
        plants = {}
        for r in shown.to_dict("records"):
            p = planned_plant(r, heads[r["cluster_id"]], plant_ix)
            if p is not None:
                plants[r["cluster_id"]] = p
        log(f"  plants named and listed in eia860m_planned_generators: {len(plants)}")
        cap = next(({"plant": plants[r["cluster_id"]], "rec": r} for r in shown.to_dict("records") if r["cluster_id"] in plants), None)
        picked["capacity"] = cap   # session 1895 (row 68): the five's first stand-in, before a second price
        picked["policy"] = policy_pick(start, cut)   # session 1907 (row 68): the second stand-in, before a second price
        five = five_numbers(label, start, cut, facts, log, picked)   # session 806, kept; session 2704: what the opening reads
        summary, su = (None, []) if args.no_model else brief.numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        L += ["", "### ERW's Numbers This Week", ""] + ([summary, ""] if summary else []) + nums
        # session 2704: the v2 order. The masthead (with the missed week), the opening number, the week in five numbers,
        # what mattered, the fold, the chart of the week, next week, the fun fact, the footer
        recs = mattered.to_dict("records")
        # session 1446 (fault 25): the top story's structural figure is a candidate, and the week's stories name the moves
        if recs and brief.story_figure(recs[0]):
            picked["story"] = {"text": f"{brief.story_figure(recs[0])}: {heads[recs[0]['cluster_id']].rstrip('.')}, as "
                                       f"{brief.outlet_of(recs[0])} reported", "fig": brief.story_figure(recs[0])}
        op = opening_number(picked, clusters)   # session 3330 (row 110): the week's stories name a move, not only those printed
        log(f"  opening number: {(op or {}).get('key', 'none')}")
        W = ["## What mattered", ""]
        if not recs:
            W.append("- no scored story of the week to rank.")
        for i, r in enumerate(recs, 1):
            W += brief.item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({brief.sector_words(r['sector'])}, {r['n']} "
                                  f"{'story' if r['n'] == 1 else 'stories'})  ",
                                  " ".join(x for x in (brief.why_line(r['why'], heads[r['cluster_id']], r.get('mw')), evidence_gap(r, heads[r['cluster_id']], steps.get(r['cluster_id']), plants.get(r['cluster_id']), bench_of(r, facts))) if x),
                                  f"Sources: {link_text(r['links'])}")
        nxt = next_week(end, log)
        tables_to = max(facts["reach"]) if facts.get("reach") else None   # session 1882 (row 59)
        L = (masthead_lines(label, end, cut, op, heads[recs[0]["cluster_id"]] if recs else "", missed, newest, tables_to)
             + intro + opening_lines(op)
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
