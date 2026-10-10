#!/usr/bin/env python3
"""Automated Analysis (platform tool 26): run every template, pick the chart of the week, write it out.

Energy Research Warehouse (ERW), session 23. Weekly, before the Energy Roundup (Sundays 23:00 UTC,
.github/workflows/roundup.yml):

    python warehouse/analysis/run.py                  # the ISO week that contains yesterday (UTC)
    python warehouse/analysis/run.py --week 2026-W39
    python warehouse/analysis/run.py --no-gallery     # skip the parameter grid
    python warehouse/analysis/run.py --no-model       # the note and caption from the template's own sentences
    python warehouse/analysis/run.py --dry-run        # session 152: the choosing step only (steps 1 and 2): every
                                                      # candidate with its score and the reason it competes or does not,
                                                      # the pick and the runner-up, printed. No model is called and no
                                                      # file is written: no log, no status row, no chart, nothing under
                                                      # docs/ or warehouse/output. Tables elsewhere: set ERW_DATA_DIR

Steps:
  1. Run every template in warehouse/analysis/templates/ at its default parameters, and every line of the watch list
     (warehouse/analysis/watch.py, session 119: one measure of a public table a line). A template or a line whose
     inputs are not in the warehouse on this machine (NoData) is skipped and named, with the reason.
  2. The chart of the week is the week's most notable real change, chosen by a rule and not by a model (session 119;
     until then the rule compared a headline's level with its history, and on 4 October 2026 it picked "energy deals
     in the news, by month", a count of what the ERW had read, at its highest because the ERW had just begun reading):
       a. Real: only a measurement of the energy system competes (ABOUT = "system"). A count of what the ERW itself
          has collected (deals in the news, facilities in the tracker: ABOUT = "coverage") is run and shown in the
          gallery and never chosen.
       b. A change: the statistic is the headline's change from the period it is compared with, not its level. The
          period before it, for a weekly figure (COMPARE = "previous"); the same month a year earlier, for a monthly
          figure with a season in it (COMPARE = "year"). Each template and each line says which.
       c. Notable against its own recent past: that change is ranked among the same measure's own earlier changes,
          the last 104 for a weekly figure and the last 36 for a monthly one (two and three years: a price's weekly
          moves at USD 100 a barrel are not those at USD 20, and a fleet adds more MW a month than it did). The score
          is the share of those earlier changes that were smaller in size, 0 to 100. At least 8 are needed. A first
          version scored a robust z over the whole history; on its first trial it chose an ordinary month of battery
          additions (29 of 138 earlier months had added as much), because most of that history is near zero. The z
          is still computed, over the same window, and only breaks a tie.
       d. This week's: the headline period must be new, one this measure has not shown as its headline in an earlier
          week's run (docs/analysis/history.csv), and must have ended within the last 100 days (EIA's monthly
          figures arrive about two months late).
       e. The highest score is chosen; ties go to the higher z, then to template order.
     If nothing passes d, the largest change among measures whose period is not new is chosen and the chart says so;
     if no measure has 8 earlier changes, the level rule of session 23 is used and the chart says so.
  3. An internal template is never picked and never written under docs/.
  4. The caption states the finding, and code writes it, not the model: what the measure was, in which period, how
     far it moved from the period it is compared with, and how that move ranks among the earlier ones. Its numbers
     are the table's. The note (two sentences) is drafted by the model from the template's own sentences and the
     finding, and checked with the chat's literal-number check (warehouse/chat/ask.py): every number must appear in
     them. One regeneration; if it still fails, the note is the finding and the template's first sentence as written.
  5. Writes docs/analysis/YYYY-Www/: results.json (every public template's result, notability and ECharts option),
     chart_of_the_week.json, chart_email.png (1200 x 750), social_1200x627.png, social_1080x1080.png; copies the
     two social PNGs and caption.txt to docs/analysis/social/ for manual posting; appends every template's
     headline to docs/analysis/history.csv; writes docs/analysis/templates.json (methods and parameters).
     Internal results go to warehouse/output/analysis_internal/ (not in git).
  6. The gallery: every public template over its grid of parameter values, each an ECharts option with its
     frame and citations, in docs/analysis/gallery/<template>/<params>.json and gallery/index.json. The site's
     /analysis serves these files; they are recomputed here, from the warehouse, every week.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import shutil
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "templates"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import iso_prices as ip  # noqa: E402
import templates  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
from voice import VOICE_NOTE  # noqa: E402  session 25: docs/voice.md
from common import NoData, nodes  # noqa: E402

DOCS = os.path.join(ROOT, "docs", "analysis")
INTERNAL = os.path.join(ROOT, "warehouse", "output", "analysis_internal")
HISTORY = os.path.join(DOCS, "history.csv")
MIN_HISTORY, MAX_AGE_DAYS, Z_CAP = 8, 45, 10.0
MAX_AGE_NEW = 100  # session 119: a headline period new this week may have ended this long ago (EIA's monthly lag)
WINDOW = {"week": 104, "month": 36}  # session 119: the earlier changes a change is ranked among
RULE = ("the change that ranks highest among the measure's own earlier changes, among measurements of the energy system "
        "whose newest period is new this week: the change from the period before (weekly figures) or from the same month "
        f"a year earlier (monthly figures with a season), ranked by size among the last {WINDOW['week']} weekly or "
        f"{WINDOW['month']} monthly changes before it (at least {MIN_HISTORY}); counts of what the ERW itself has "
        "collected never compete")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
EM = chr(0x2014)  # the em dash, which no file here may hold (CLAUDE.md, non-negotiable 2)


def week_label(week, now):
    if week:
        return week
    y, w, _ = (now - pd.Timedelta(days=1)).date().isocalendar()
    return f"{y}-W{w:02d}"


def period_end(period):
    """The last date of a headline period: 'YYYY-MM-DD to YYYY-MM-DD', 'YYYY-MM' or 'YYYY-MM-DD'."""
    last = str(period).split(" to ")[-1]
    if re.fullmatch(r"\d{4}-\d{2}", last):
        return (pd.Timestamp(last + "-01") + pd.offsets.MonthEnd(0)).date()
    return pd.Timestamp(last).date()


def notability(value, history):
    vals = [float(v) for v in history if v is not None and not pd.isna(v)]
    if value is None or len(vals) < MIN_HISTORY:
        return None, len(vals), None
    s = pd.Series(vals)
    med = float(s.median())
    mad = float((s - med).abs().median()) * 1.4826
    if mad == 0:  # a sparse history (mostly one value): the mean absolute deviation, scaled to a normal sd
        mad = float((s - med).abs().mean()) * 1.2533
    if mad == 0:
        z = 0.0 if float(value) == med else Z_CAP
    else:
        z = min(Z_CAP, abs(float(value) - med) / mad)
    rank = float((s < float(value)).mean() * 100)
    return round(z, 2), len(vals), round(rank, 1)


def ordered(headline, stored=None):
    """Every period the headline has a value for, oldest first: [(period, value)], the headline's own period last
    among equals. stored: {period: value} from history.csv, used where the tables no longer reach."""
    seen = {}
    for p, v in list((stored or {}).items()) + [tuple(x) for x in headline.get("history", [])] + [(headline["period"], headline["value"])]:
        if v is not None and not pd.isna(v):
            seen[p] = float(v)
    return sorted(seen.items(), key=lambda x: (period_end(x[0]), x[0]))


def change(headline, compare, stored=None):
    """The headline's change from the period it is compared with, and the same change for every earlier period:
    {delta, prev_period, prev_value, earlier: [deltas, oldest first]}, or None when the headline has no such period.
    compare "previous": the period before it in the history. "year": the same month a year earlier (monthly labels)."""
    seq = ordered(headline, stored)
    pairs = []
    if compare == "year":
        by = dict(seq)
        for p, v in seq:
            if re.fullmatch(r"\d{4}-\d{2}", p):
                q = f"{int(p[:4]) - 1}{p[4:]}"
                if q in by:
                    pairs.append((p, v, q, by[q]))
    else:
        pairs = [(seq[i][0], seq[i][1], seq[i - 1][0], seq[i - 1][1]) for i in range(1, len(seq))]
    if not pairs or pairs[-1][0] != headline["period"]:
        return None
    deltas = [v - pv for _, v, _, pv in pairs]
    earlier = deltas[:-1][-WINDOW["week" if " to " in str(headline["period"]) else "month"]:]
    d = deltas[-1]
    score = round(100.0 * sum(1 for x in earlier if abs(x) < abs(d)) / len(earlier), 1) if earlier else None
    return {"delta": d, "prev_period": pairs[-1][2], "prev_value": pairs[-1][3], "earlier": earlier, "score": score}


def month_words(p):
    """'2026-08' as 'August 2026'; anything else as it is."""
    return f"{MONTHS[int(p[5:7]) - 1]} {p[:4]}" if re.fullmatch(r"\d{4}-\d{2}", str(p)) else str(p)


def shown(v):
    """A number as a sentence gives it: whole when it is whole or large, else two decimals."""
    v = float(v)
    if abs(v) >= 100000 or v == int(v):
        return f"{int(round(v)):,}"
    return f"{round(v, 2):,}"


def finding(headline, ch, compare):
    """The finding in two plain sentences, written by code from the table's own numbers (session 119): what the
    measure was, how far it moved from the period it is compared with, and how that move ranks among the earlier ones.
    Returns (first sentence, second sentence)."""
    weekly = " to " in str(headline["period"])
    when = f"in the week of {headline['period']}" if weekly else f"in {month_words(headline['period'])}"
    versus = "a year earlier" if compare == "year" else ("the week before" if weekly else f"in {month_words(ch['prev_period'])}")
    label = headline["label"][0].upper() + headline["label"][1:]
    d = ch["delta"]
    moved = "unchanged from" if d == 0 else f"{'up' if d > 0 else 'down'} {shown(abs(d))} from"
    one = f"{label}: {shown(headline['value'])} {headline['unit']} {when}, {moved} {shown(ch['prev_value'])} {versus}."
    n = len(ch["earlier"])
    bigger = sum(1 for x in ch["earlier"] if abs(x) >= abs(d))
    kind = "year-over-year" if compare == "year" else ("week-to-week" if weekly else "month-to-month")
    if n == 0:
        two = ""
    elif bigger == 0:
        two = f"It is the largest {kind} move of the last {n + 1}."
    else:
        two = f"Of the {n} {kind} moves before it, {bigger} {'was' if bigger == 1 else 'were'} as large."
    return one, two


def seen_before(template, params, period, label):
    """Whether an earlier week's run already had this period as this template's headline (history.csv)."""
    if not os.path.exists(HISTORY):
        return False
    h = pd.read_csv(HISTORY, dtype=str, keep_default_na=False)
    h = h[(h["template"] == template) & (h["params"] == json.dumps(params, sort_keys=True)) & (h["week"] < label)]
    return bool((h["period"] == str(period)).any())


def tables_pattern(mods):
    """Session 173: every table a template reads, as one regular expression for scripts/sync.py --tables (the Roundup's
    runner restores them before the templates run, as it does the watch list's and the findings' tables; a template
    whose table the Redivis restore does not bring, portwatch_chokepoint_transits for one, was skipped there)."""
    return "^(" + "|".join(sorted({t for m in mods for t in m.TABLES})) + ")$"


def table_registry(mods):
    """Session 119: for every public table of coverage.csv, which template or watch line reads it, or why none does.
    Written to docs/analysis/tables.json on every run, so "the chooser draws on the public tables" is a list and a
    count, not a claim. A table is not read for one of four stated reasons; the last is the honest one."""
    cov_path = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
    cov = pd.read_csv(cov_path, dtype=str, keep_default_na=False)
    read_by = {}
    for m in mods:
        if m.PUBLIC:
            for t in m.TABLES:
                read_by.setdefault(t, []).append(m.NAME)
    held = set()
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import impossible_hours
        held = set(impossible_hours.HELD)
    except Exception:
        pass
    import watch
    named = {t: reason for reason, ts in watch.NOT_WATCHED.items() for t in ts}
    rows = []
    for r in cov[cov["license"] == "public"].sort_values("table").to_dict("records"):
        t, by = r["table"], sorted(read_by.get(r["table"], []))
        why = ""
        if not by:
            if r["interval"] in ("snapshot", "event"):
                why = "a list of things or of events, not a series: it has no period to compare with the one before"
            elif r["tier"] == "model_extracted" or "news" in r["sector"].split(";") or "platform" in r["sector"].split(";"):
                why = "the ERW's own reading or record, not a measurement of the energy system"
            elif t in held:
                why = "behind a fix held for approval (docs/methods/impossible_hours.md): not watched until the hold is lifted"
            elif t in named:
                why = named[t]
            else:
                why = "no template or watch line reads it yet"
        rows.append({"table": t, "interval": r["interval"], "sector": r["sector"], "tier": r["tier"], "read_by": by, "why_not": why})
    n = sum(1 for x in rows if x["read_by"])
    reasons = {}
    for x in rows:
        if x["why_not"]:
            reasons[x["why_not"]] = reasons.get(x["why_not"], 0) + 1
    return {"public_tables": len(rows), "read": n, "not_read": reasons, "tables": rows}


def stored_history(template, params):
    if not os.path.exists(HISTORY):
        return {}
    h = pd.read_csv(HISTORY, dtype=str, keep_default_na=False)
    h = h[(h["template"] == template) & (h["params"] == json.dumps(params, sort_keys=True))]
    return {r["period"]: float(r["value"]) for r in h.to_dict("records") if r["value"] != ""}


# ---------------------------------------------------------------------------------------------
# session 152: the choosing step alone, printed (--dry-run)
# ---------------------------------------------------------------------------------------------

def reason(res, eligible):
    """Why a measure competes for the chart of the week, or the first condition of the rule it does not meet."""
    ch, mod = res["_change"], res["_mod"]
    if eligible:
        return "competes: a measurement of the system, its newest period new this week, its change ranked among enough earlier ones"
    if not mod.PUBLIC:
        return "never chosen: an internal template"
    if ch["about"] != "system":
        return "never chosen: a count of what the ERW itself has collected, not a measurement of the energy system"
    if ch.get("delta") is None:
        return "does not compete: its newest period has no period to be compared with"
    if ch["score"] is None:
        return f"does not compete: {ch['n']} earlier changes, and {MIN_HISTORY} are needed"
    if not ch["new"]:
        return "does not compete: an earlier week's run already showed this period as its headline (docs/analysis/history.csv)"
    if ch["age"] > MAX_AGE_NEW:
        return f"does not compete: its newest period ended {ch['age']} days ago, and {MAX_AGE_NEW} is the most allowed"
    return "does not compete"


def candidates(results):
    """Every measure that ran, as the chooser saw it: competing ones first, by score, then z, then template order."""
    order = lambda r: -templates.ORDER.index(r[0]["template"])  # noqa: E731
    rows = []
    for r in sorted(results, key=lambda r: (r[4], r[0]["_change"]["score"] if r[0]["_change"]["score"] is not None else -1.0,
                                            r[0]["_change"]["z"] or 0, order(r)), reverse=True):
        res, z, n_hist, rank, eligible = r
        h, ch = res["headline"], res["_change"]
        found = finding(h, ch, ch["compare"]) if ch.get("delta") is not None else None
        rows.append({"template": res["template"], "title": res["title"], "label": h["label"], "period": h["period"], "value": h["value"],
                     "unit": h["unit"], "about": ch["about"], "compare": ch["compare"],
                     "change": None if ch.get("delta") is None else round(ch["delta"], 4), "previous_period": ch.get("prev_period"),
                     "previous_value": ch.get("prev_value"), "score": ch["score"], "change_z": ch["z"], "earlier_changes": ch["n"],
                     "new_this_week": ch["new"], "age_days": ch["age"], "level_z": z, "history_n": n_hist, "eligible": bool(eligible),
                     "reason": reason(res, eligible), "finding": " ".join(x for x in found if x) if found else None,
                     "tables": res["tables"]})
    return rows


def print_choice(label, rows, best, how_picked, skipped, out=print):
    """The dry run's report: the rule, each candidate, the pick, the runner-up, what was skipped."""
    out(f"chart of the week, {label}: the choosing step only (dry run; no model call, nothing written)")
    out(f"rule: {RULE}")
    out("score: the share, in percent, of the measure's own earlier changes (the last "
        f"{WINDOW['week']} weekly or {WINDOW['month']} monthly) that were smaller in size than this one; ties go to the "
        "higher robust z of the change over the same window, then to template order")
    out(f"candidates: {len(rows)} measures ran, {sum(1 for r in rows if r['eligible'])} compete, {len(skipped)} skipped")
    for i, r in enumerate(rows, 1):
        out(f"{i:>3}. {r['template']}: score {r['score']}, z {r['change_z']}, {r['earlier_changes']} earlier changes; "
            f"{r['label']} {r['period']} = {r['value']} {r['unit']}; change {r['change']} ({r['compare']}); new {r['new_this_week']}; "
            f"ended {r['age_days']} days ago; {r['reason']}")
        if r["finding"]:
            out(f"       {r['finding']}")
    pick = next(r for r in rows if r["template"] == best)
    out(f"pick: {pick['template']} ({pick['title']}), by {how_picked}: score {pick['score']}, z {pick['change_z']}, among {pick['earlier_changes']} earlier changes")
    if pick["finding"]:
        out(f"      {pick['finding']}")
    others = [r for r in rows if r["template"] != best and r["eligible"]] or [r for r in rows if r["template"] != best and r["score"] is not None and r["about"] == "system"]
    if others:
        ru = others[0]
        out(f"runner-up: {ru['template']} ({ru['title']}): score {ru['score']}, z {ru['change_z']}, among {ru['earlier_changes']} earlier changes"
            + ("" if ru["eligible"] else " (it does not compete: the largest change among those that do not)"))
        if ru["finding"]:
            out(f"      {ru['finding']}")
    for sk in skipped:
        out(f"skipped: {sk['template']}: {sk['reason']}")


class PrintLog:
    """The dry run's log: lines go to the screen and no file is opened."""

    def __init__(self, quiet=False):
        self.quiet = quiet

    def __call__(self, msg):
        if not self.quiet:
            print(f"  log: {msg}")

    def close(self):
        pass


# ---------------------------------------------------------------------------------------------
# the note and the caption: drafted by the model, kept only under the literal-number check
# ---------------------------------------------------------------------------------------------

NOTE_SYSTEM = """You write the note under the ERW's chart of the week and a social caption for it. The ERW is the Energy
Research Warehouse, the live, citable record of the US energy system.
- note: exactly two plain sentences saying what the chart shows and what changed this week. Use only the numbers
  written in the facts and the finding, exactly as written; compute nothing new, round nothing. Name no statistic
  (no "z", no "deviation", no "percentile"): say what moved, by how much, and against what.
- caption: one or two sentences for a social post, at most 240 characters, the same rule for numbers, no hashtags,
  no emoji, no hype, no advice. (The engine publishes its own caption, the finding; yours is kept beside it.)
- No em dashes. Return JSON with the fields note and caption.""" + VOICE_NOTE
NOTE_SCHEMA = {"type": "object", "properties": {"note": {"type": "string"}, "caption": {"type": "string"}},
               "required": ["note", "caption"], "additionalProperties": False}


def draft_note(res, z, log, use_model=True, found=None):
    import ask as chat_ask
    h = res["headline"]
    head = f"Headline: {h['label']}, {h['period']}: {h['value']} {h['unit']}."
    if found:  # session 119: the finding leads, and the model is not told the statistic
        head = "Finding: " + " ".join(x for x in found if x)
        fallback = (" ".join(x for x in (found[0], res["facts"][0]) if x), found[0][:240], "the finding and the template's own sentence")
    else:
        fallback = (" ".join(res["facts"][:2]), res["facts"][0][:240], "the template's own sentences")
    pool = res["facts"] + [head]
    if not use_model:
        return fallback
    try:
        import llm
        from score import PRICES, pick_model
        client = llm.client("analysis_note", log)
        model = pick_model(client, log)
        msgs = [{"role": "user", "content": f"Chart: {res['title']}. {res['subtitle']}.\n\nFacts:\n" +
                 "\n".join(f"- {f}" for f in res["facts"]) + f"\n- {head}"}]
        cost = 0.0
        for attempt in (1, 2):
            resp = client.messages.create(model=model, max_tokens=800, system=NOTE_SYSTEM, messages=msgs,
                                          output_config={"effort": "low", "format": {"type": "json_schema",
                                                                                     "schema": NOTE_SCHEMA}})
            if model in PRICES:
                cost += (resp.usage.input_tokens * PRICES[model][0] + resp.usage.output_tokens * PRICES[model][1]) / 1e6
            out = json.loads(next(b.text for b in resp.content if b.type == "text"))
            note, cap = out["note"].replace(EM, ",").strip(), out["caption"].replace(EM, ",").strip()
            bad = chat_ask.unverified(note + " " + cap, pool)
            sentences = len(re.findall(r"[.!?](\s|$)", note))
            if not bad and sentences == 2 and len(cap) <= 240:
                log(f"  note and caption: attempt {attempt} passed the literal check; cost USD {cost:.4f}")
                return note, cap, f"model {model}, literal-number check passed (attempt {attempt}), USD {cost:.4f}"
            log(f"  note attempt {attempt}: numbers not in the facts {bad}; sentences {sentences}; caption {len(cap)} chars")
            msgs += [{"role": "assistant", "content": json.dumps(out)},
                     {"role": "user", "content": f"These numbers are not in the facts as written: {bad}. The note must be "
                      "exactly two sentences and the caption at most 240 characters. Rewrite both."}]
        log(f"  note: the model's drafts failed twice; the template's own sentences are used (cost USD {cost:.4f})")
    except Exception as exc:
        log(f"  note: model unavailable ({ip.redact(repr(exc))[:200]}); the template's own sentences are used")
    return fallback


# ---------------------------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------------------------

def public_record(res, z, n_hist, rank):
    ch = res.get("_change") or {}
    return {"template": res["template"], "params": res["params"], "title": res["title"], "subtitle": res["subtitle"],
            "headline": {k: v for k, v in res["headline"].items() if k != "history"},
            "history_n": n_hist, "notability_z": z, "percentile": rank,
            # session 119: what the chooser compared
            "about": ch.get("about"), "compare": ch.get("compare"), "change": None if ch.get("delta") is None else round(ch["delta"], 4),
            "change_score": ch.get("score"), "change_z": ch.get("z"), "earlier_changes": ch.get("n"), "new_this_week": ch.get("new"),
            "source_line": res["source_line"],
            "tables": res["tables"], "citations": res["citations"], "facts": res["facts"],
            "option": res["_option"], "frame": json.loads(res["frame"].to_json(orient="records", date_format="iso"))}


def param_grid(mod):
    """Every combination of a template's parameter choices; a hub's choices are the nodes of the ISO's tables."""
    names = list(mod.PARAMS)
    if "hub" in names and "iso" in names:
        out = []
        others = [n for n in names if n not in ("iso", "hub")]
        for iso in mod.PARAMS["iso"]["choices"]:
            hubs = sorted(set(hub_choices(mod, iso)))
            for hub in hubs:
                for combo in itertools.product(*[mod.PARAMS[n]["choices"] for n in others]):
                    out.append(dict(iso=iso, hub=hub, **dict(zip(others, combo))))
        return out
    return [dict(zip(names, combo)) for combo in itertools.product(*[mod.PARAMS[n]["choices"] for n in names])]


def hub_choices(mod, iso):
    from common import DA, RT
    if mod.NAME == "implied_heat_rate":
        return nodes(f"{iso}_trader_daily")
    if mod.NAME == "da_rt_spread_by_hour":
        return sorted(set(nodes(DA[iso])) & set(nodes(RT[iso][0])))
    return nodes(RT[iso][0])


def key(params):
    return re.sub(r"[^A-Za-z0-9_.=-]+", "_", "&".join(f"{k}={params[k]}" for k in sorted(params)))


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), default=str)


def gallery(mods, log):
    index = []
    gdir = os.path.join(DOCS, "gallery")
    for mod in mods:
        if not mod.PUBLIC:
            continue
        combos, ok = {}, 0
        for params in param_grid(mod):
            k = key(params)
            try:
                res = mod.compute(history=False, **params)
                write_json(os.path.join(gdir, mod.NAME, f"{k}.json"), {
                    "template": mod.NAME, "params": params, "title": res["title"], "subtitle": res["subtitle"],
                    "source_line": res["source_line"], "citations": res["citations"], "facts": res["facts"],
                    "option": mod.render(res, "site"), "computed_at": ip.utc_iso(pd.Timestamp.now(tz="UTC"))})
                combos[k] = {"params": params, "file": f"{mod.NAME}/{k}.json"}
                ok += 1
            except NoData as exc:
                combos[k] = {"params": params, "file": None, "reason": str(exc)[:200]}
            except Exception as exc:
                combos[k] = {"params": params, "file": None, "reason": f"failed: {ip.redact(repr(exc))[:200]}"}
                log(f"  gallery {mod.NAME} {k}: FAILED {ip.redact(repr(exc))[:200]}")
        log(f"  gallery {mod.NAME}: {ok} of {len(combos)} parameter combinations computed")
        default = {k: (v["default"] if not isinstance(v["default"], dict) else v["default"][mod.PARAMS["iso"]["default"]])
                   for k, v in mod.PARAMS.items()}
        index.append({"template": mod.NAME, "title": mod.TITLE, "combos": combos, "default": key(default)})
    write_json(os.path.join(gdir, "index.json"), {"computed_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "templates": index})
    return index


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Automated Analysis")
    ap.add_argument("--week", help="ISO week YYYY-Www (default: the week that contains yesterday, UTC)")
    ap.add_argument("--no-gallery", action="store_true")
    ap.add_argument("--no-model", action="store_true")
    ap.add_argument("--gallery-only", action="store_true", help="recompute only the gallery (and templates.json)")
    ap.add_argument("--tables-only", action="store_true",
                    help="session 119: write only docs/analysis/tables.json (which public table each template and watch line reads)")
    ap.add_argument("--dry-run", action="store_true",
                    help="session 152: the choosing step only: print every candidate, its score and its reason, the pick and the "
                         "runner-up; call no model and write nothing")
    ap.add_argument("--tables", action="store_true",
                    help="session 173: print every template's tables as one regular expression (for scripts/sync.py --tables) and stop")
    args = ap.parse_args(argv)
    if args.tables:
        print(tables_pattern(templates.load_all()))
        return 0
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.dry_run:
        if args.gallery_only or args.tables_only:
            ap.error("--dry-run is the choosing step alone: not with --gallery-only or --tables-only")
        log = PrintLog()
    else:
        os.makedirs(ip.LOG_DIR, exist_ok=True)
        log = ip.Log(os.path.join(ip.LOG_DIR, f"analysis_{run_id}.log"))
    status = dict(table="analysis", market="weekly", status="ok", detail="")
    try:
        now = pd.Timestamp.now(tz="UTC")
        label = week_label(args.week, now)
        out = os.path.join(DOCS, label)
        mods = templates.load_all()
        if args.tables_only:
            reg = table_registry(mods)
            write_json(os.path.join(DOCS, "tables.json"), reg)
            status["detail"] = f"tables only: {reg['read']} of {reg['public_tables']} public tables read by a template or a watch line"
            log(status["detail"])
            print(f"analysis: {status['detail']}")
            ip.write_status("analysis", run_id, [status])
            log.close()
            return 0
        if args.gallery_only:
            write_json(os.path.join(DOCS, "templates.json"), {"templates": [
                {"template": m.NAME, "title": m.TITLE, "public": m.PUBLIC, "method": " ".join(m.METHOD.split()),
                 "params": m.PARAMS, "tables": m.TABLES} for m in mods]})
            idx = gallery(mods, log)
            n_gal = sum(1 for t in idx for c in t["combos"].values() if c["file"])
            status["detail"] = f"gallery only: {n_gal} charts"
            log(status["detail"])
            print(f"analysis: {status['detail']}")
            ip.write_status("analysis", run_id, [status])
            log.close()
            return 0
        results, skipped, hist_rows = [], [], []
        for mod in mods:
            try:
                res = mod.compute()
            except NoData as exc:
                skipped.append({"template": mod.NAME, "reason": str(exc)[:300]})
                log(f"{mod.NAME}: skipped ({exc})")
                continue
            except Exception as exc:
                skipped.append({"template": mod.NAME, "reason": f"failed: {ip.redact(repr(exc))[:300]}"})
                log(f"{mod.NAME}: FAILED\n{ip.redact(traceback.format_exc())}")
                continue
            h = res["headline"]
            past = dict(h["history"])
            for period, v in stored_history(mod.NAME, res["params"]).items():
                if period != h["period"]:
                    past.setdefault(period, v)
            z, n_hist, rank = notability(h["value"], list(past.values()))
            age = (now.date() - period_end(h["period"])).days
            # session 119: the change rule (the docstring, step 2)
            about, compare = getattr(mod, "ABOUT", "system"), getattr(mod, "COMPARE", "previous")
            stored = {p: v for p, v in stored_history(mod.NAME, res["params"]).items() if p != h["period"]}
            ch = change(h, compare, stored)
            cz, n_ch, _ = notability(ch["delta"], ch["earlier"]) if ch else (None, 0, None)
            score = ch["score"] if ch and n_ch >= MIN_HISTORY else None
            new = not seen_before(mod.NAME, res["params"], h["period"], label)
            res["_change"] = dict(ch or {}, z=cz, n=n_ch, compare=compare, about=about, new=new, age=age, score=score)
            eligible = bool(mod.PUBLIC and about == "system" and score is not None and new and age <= MAX_AGE_NEW)
            res["_option"] = None if args.dry_run else mod.render(res, "site")  # session 152: a dry run draws nothing
            res["_mod"] = mod
            results.append((res, z, n_hist, rank, eligible))
            hist_rows.append({"week": label, "template": mod.NAME, "params": json.dumps(res["params"], sort_keys=True),
                              "period": h["period"], "value": h["value"], "unit": h["unit"], "history_n": n_hist,
                              "notability_z": "" if z is None else z, "public": mod.PUBLIC,
                              "about": about, "compare": compare, "change": "" if not ch else round(ch["delta"], 4),
                              "change_score": "" if score is None else score, "change_z": "" if cz is None else cz,
                              "changes_n": n_ch, "new": new})
            log(f"{mod.NAME}: {h['label']} {h['period']} = {h['value']} {h['unit']}; history {n_hist}; level z {z}; "
                f"change {None if not ch else round(ch['delta'], 4)} ({compare}), score {score} (z {cz}) among {n_ch} earlier "
                f"changes; about {about}; new {new}; age {age} days; eligible {eligible}")
        order = lambda r: -templates.ORDER.index(r[0]["template"])  # noqa: E731
        pool = [r for r in results if r[4]]
        how_picked = "the rule"
        if not pool:  # nothing new this week passes: the largest change among measures whose period is not new
            pool = [r for r in results if r[0]["_mod"].PUBLIC and r[0]["_change"]["about"] == "system" and r[0]["_change"]["score"] is not None
                    and r[0]["_change"]["age"] <= MAX_AGE_NEW]
            how_picked = "no measure's newest period was new this week; the largest change among periods already seen"
        if pool:
            best = max(pool, key=lambda r: (r[0]["_change"]["score"], r[0]["_change"]["z"] or 0, order(r)))
        else:  # no measure has enough earlier changes: session 23's level rule, among measurements of the system first
            level = [r for r in results if r[0]["_mod"].PUBLIC and r[1] is not None and r[2] >= MIN_HISTORY and
                     (now.date() - period_end(r[0]["headline"]["period"])).days <= MAX_AGE_DAYS]
            pool = [r for r in level if r[0]["_change"]["about"] == "system"] or level
            how_picked = (f"no measure had {MIN_HISTORY} earlier changes; the level rule of session 23 (the headline's robust z against "
                          "its own history)")
            if not pool:
                raise RuntimeError(f"no eligible public template (skipped: {skipped})")
            best = max(pool, key=lambda r: (r[1], order(r)))
        res, z, n_hist, rank, _ = best
        mod = res["_mod"]
        ch = res["_change"]
        if args.dry_run:  # session 152: the choice is made; say it and stop before the note (a model call) and every file
            print_choice(label, candidates(results), mod.NAME, how_picked, skipped)
            return 0
        found = finding(res["headline"], ch, ch["compare"]) if ch.get("delta") is not None else None
        log(f"chart of the week: {mod.NAME} ({how_picked}; score {ch['score']}, z {ch['z']}, among {ch['n']} earlier changes; level z {z})")
        if found:
            log("  finding: " + " ".join(x for x in found if x))
        note, model_caption, how = draft_note(res, z, log, use_model=not args.no_model, found=found)
        # session 119: the caption is the finding, written by code. Two sentences when they fit a social post, else the first
        caption = model_caption
        if found:
            both = " ".join(x for x in found if x)
            caption = both if len(both) <= 240 else found[0][:240]
        also = sorted([r for r in results if r is not best and r[0]["_mod"].PUBLIC and r[0]["_change"]["about"] == "system"
                       and r[0]["_change"]["score"] is not None],
                      key=lambda r: (r[0]["_change"]["score"], r[0]["_change"]["z"] or 0, order(r)), reverse=True)[:5]
        os.makedirs(out, exist_ok=True)
        files = {"email": "chart_email.png", "social_wide": "social_1200x627.png", "social_square": "social_1080x1080.png"}
        for size, f in files.items():
            mod.render(res, size, os.path.join(out, f))
        cow = {"week": label, "template": mod.NAME, "title": res["title"], "subtitle": res["subtitle"], "note": note,
               "caption": caption, "note_by": how, "source_line": res["source_line"], "citations": res["citations"],
               "tables": res["tables"], "params": res["params"], "headline": {k: v for k, v in res["headline"].items()
                                                                               if k != "history"},
               "notability_z": z, "percentile": rank, "history_n": n_hist, "files": files, "option": res["_option"],
               "chart": res["chart"],
               # session 119: the finding, the change it rests on, how it was picked, and what else moved
               "finding": " ".join(x for x in found if x) if found else None, "model_caption": model_caption,
               "change": None if ch.get("delta") is None else {
                   "compare": ch["compare"], "delta": round(ch["delta"], 4), "previous_period": ch["prev_period"],
                   "previous_value": ch["prev_value"], "score": ch["score"], "z": ch["z"], "earlier_changes": ch["n"],
                   "new_this_week": ch["new"]},
               "picked_by": how_picked,
               "also_moved": [{"template": r[0]["template"], "title": r[0]["title"], "score": r[0]["_change"]["score"],
                               "change_z": r[0]["_change"]["z"],
                               "new_this_week": r[0]["_change"]["new"],
                               "finding": " ".join(x for x in finding(r[0]["headline"], r[0]["_change"], r[0]["_change"]["compare"]) if x)}
                              for r in also],
               "rule": RULE, "computed_at": ip.utc_iso(now)}
        write_json(os.path.join(out, "chart_of_the_week.json"), cow)
        write_json(os.path.join(out, "results.json"), {
            "week": label, "computed_at": ip.utc_iso(now), "picked": mod.NAME,
            "results": [public_record(r[0], r[1], r[2], r[3]) for r in results if r[0]["_mod"].PUBLIC],
            "skipped": [s for s in skipped if next(m for m in mods if m.NAME == s["template"]).PUBLIC]})
        # internal templates: kept on this machine only
        for r in results:
            if not r[0]["_mod"].PUBLIC:
                write_json(os.path.join(INTERNAL, label, f"{r[0]['template']}.json"), public_record(*r[:4]))
        social = os.path.join(DOCS, "social")
        os.makedirs(social, exist_ok=True)
        for size in ("social_wide", "social_square"):
            shutil.copyfile(os.path.join(out, files[size]), os.path.join(social, f"{label}_{mod.NAME}_{files[size]}"))
        with open(os.path.join(social, f"{label}_{mod.NAME}_caption.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(caption + "\n\n" + res["source_line"] + "\n")
        hist = pd.DataFrame(hist_rows)
        hist["picked"] = hist["template"] == mod.NAME
        if os.path.exists(HISTORY):
            old = pd.read_csv(HISTORY, dtype=str, keep_default_na=False)
            old = old[old["week"] != label]
            hist = pd.concat([old, hist.astype(str)], ignore_index=True)
        hist.to_csv(HISTORY, index=False, lineterminator="\n")
        write_json(os.path.join(DOCS, "templates.json"), {"templates": [
            {"template": m.NAME, "title": m.TITLE, "public": m.PUBLIC, "method": " ".join(m.METHOD.split()),
             "params": m.PARAMS, "tables": m.TABLES} for m in mods]})
        write_json(os.path.join(DOCS, "tables.json"), table_registry(mods))  # session 119
        n_gal = 0
        if not args.no_gallery:
            idx = gallery(mods, log)
            n_gal = sum(1 for t in idx for c in t["combos"].values() if c["file"])
        status["detail"] = (f"{label}: {len(results)} templates run, {len(skipped)} skipped; chart of the week "
                            f"{mod.NAME} (score {ch.get('score')}); note by {how.split(',')[0]}; gallery {n_gal} charts")
        log(status["detail"])
        print(f"analysis: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"analysis FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    if args.dry_run:  # a dry run that failed: said above, and no status row is written
        return 1
    ip.write_status("analysis", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
