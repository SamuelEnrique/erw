#!/usr/bin/env python3
"""The findings hunt over the whole warehouse (chain 164, session 3001): the shared builder.

Energy Research Warehouse (ERW). The plan is docs/reviews/findings-hunt-plan-2026-11-06.md. The owner's ruling of 12
October 2026 holds: findings are hunted automatically and appear on /research only after he approves them at
/internal/findings, having run the Stata himself. Nothing here approves, posts or sends anything.

A CANDIDATE is one question asked of a family's tables, written as a function that returns the weekly hunt's measure
rows ({"rows": [{"region", "words", "year", "value", "n", "context"}], "tables": {region: [tables]}}, as
hunt_measures.py does). Each region's series is tested by the weekly hunt's own claim and five tests (hunt.test_claim:
the last full year against the first, holds in more than one year, survives a change of window, sample large enough,
half the change remains without the first year, at least one typical yearly move). Only a claim that passes all five
is drafted. Its strength is the hunt's: the change in typical year-to-year moves (1.4826 times the median absolute
first difference of the full years), the scanner's robust standard deviation.

A DRAFT is a row of public.scanner_drafts under rule "hunt" (the store the weekly hunt writes, migration 031), loaded
by hunt.load_drafts, state draft. Its card holds the one sentence (every figure computed here, never by a model), the
chart (flag_line: the full years, the last marked, the first as a reference line), the callouts and a footnote with the
limits and the tables. Its files: the yearly CSV, the hunt's Stata and Python mirrors of the claim from that CSV, the
two reproduction scripts that recompute the figure from the tables as the public downloads hold them, the two pictures
and the caption. Beside the row, docs/findings/<family>/<slug>.md keeps the same in the repository.

    from deep import builder
    builder.run("prices", CANDIDATES, in_dir, dry_run=True)
"""

import base64
import datetime as dt
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FINDINGS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(FINDINGS, "..", "..", ".."))
sys.path.insert(0, FINDINGS)
import findings_common as common  # noqa: E402
import hunt  # noqa: E402

VERSION = "1.0.0"                  # session 3001
OUT = os.path.join(ROOT, "runs", "deep")
DOCS = os.path.join(ROOT, "docs", "findings")
METHOD = "docs/reviews/findings-hunt-plan-2026-11-06.md"
MAX_PER_CANDIDATE = 2              # the two strongest regions of one candidate: six hubs of one grid tell one story
MAX_DRAFTS = 12                    # a session keeps the ten best by consequence; two more are written for the check to fold


def candidate(name, family, fn, unit, decimals, n_floor, change_threshold, title, label, subject, limits, reproduce,
              consequence=2, context=None, first_words=None):
    """One candidate as a pattern the weekly hunt's functions accept, with this chain's own keys.

    subject(words) -> the sentence's subject ("the real-time price at ERCOT's West hub"); label: what the measure is;
    limits: the one sentence that says what the figure does not show; reproduce(region) -> {"py": text, "do": text}
    that recompute the yearly values from the tables; consequence: the rubric's first count (1 to 3), set by the
    candidate's author from its scale and checked in session 3020; first_words: what the first year is, when it is
    not the first full year the ERW holds (a comparison counted from a chosen year, session 3003)."""
    P = hunt.family(name, name, unit, decimals, n_floor, change_threshold, title, label, context=context)
    P.update(module=f"deep.{family}", family=family, _fn=fn, subject=subject, limits=limits, reproduce=reproduce, consequence=consequence)
    if first_words:
        P["first_words"] = first_words
    return P


def val(v, P):
    return f"{common.fmt(v, P['decimals'])} {P['unit']}"


def sentence(P, words, c):
    """The one sentence: the fact with its figure, unit, geography, period and comparison basis. No cause."""
    s = P["subject"](words)
    return (f"{s[0].upper()}{s[1:]} was {val(c['last'], P)} in {c['last_year']}, against {val(c['first'], P)} in {c['first_year']}, "
            f"{P.get('first_words', 'the first full year the ERW holds')}.")


def draft_id(P, region, c):
    return "scan-deep-" + hashlib.sha1(f"{P['name']}|{region}|{c['last_year']}|{round(c['change'], 3)}".encode("utf-8")).hexdigest()[:12]


def slug(P, region):
    return re.sub(r"[^a-z0-9]+", "-", f"{P['name']}-{region}".lower()).strip("-")


def csv_text(P, region, words, series, c, tables):
    lines = [f"# Energy Research Warehouse (ERW): findings hunt (chain 164), candidate {P['name']}, region {region} ({words})",
             f"# Computed {common.now_iso()} by warehouse/analysis/findings/deep/{P['family']}.py ({P['name']}); plan https://github.com/SamuelEnrique/erw/blob/main/{METHOD}",
             f"# Rows: one per year held: {P['label']} ({P['unit']}), the observations it rests on, and whether the year is full",
             f"# Tables: {', '.join(tables)}",
             "region,year,value,n_observations,full_year"]
    for y, (v, n) in series.items():
        lines.append(f"{region},{y},{v!r},{n!r},{1 if y in c['years'] else 0}")
    return "\n".join(lines) + "\n"


def mirrors(P, region, c, csv_name, py_name):
    """The weekly hunt's Stata and Python mirrors of the claim, read from the draft's CSV, with this chain's name."""
    do = hunt.do_text(P, region, csv_name, c).replace("ERW weekly hunt, pattern", "ERW findings hunt (chain 164), candidate")
    py = hunt.PY_MIRROR.format(py_name=py_name, csv_name=csv_name, name=P["name"], region=region, n_floor=P["n_floor"], full_share=hunt.FULL_SHARE)
    py = py.replace("ERW weekly hunt: the Python mirror", "ERW findings hunt (chain 164): the Python mirror")
    return do, py


def check_text(text, name):
    if chr(0x2014) in text or chr(0x2013) in text:
        raise ValueError(f"{name}: a dash the repository forbids")
    return text


def build(P, region, words, series, c, tables, out_dir, why):
    """One draft: the row of public.scanner_drafts with its card and files, and its document under docs/findings/."""
    import card_image
    did, s = draft_id(P, region, c), slug(P, region)
    fact = sentence(P, words, c)
    tests_words = " ".join(f"{t['name'].capitalize()}: {t['words']} ({'passed' if t['passed'] else 'failed'})." for t in c["tests"])
    source_line = f"Source: the ERW tables {', '.join(tables)}, the rows for {words}; computed by warehouse/analysis/findings/deep/{P['family']}.py ({P['name']})."
    files = [f"{did}.csv", f"{did}.do", f"{did}.py", f"{did}_reproduce.py", f"{did}_reproduce.do", f"{did}_1200x627.png", f"{did}_1080x1080.png", f"{did}_caption.txt"]
    shown = list(c["years"])
    card = {"id": "hunt_pattern", "card_id": did, "title": f"{P['title']}: {words.upper()}", "kind": "visual", "subtitle": fact, "draft": True,
            "params": {"pattern": P["name"], "region": str(region)}, "inputs_words": {"pattern": P["name"], "region": words},
            "chart": {"kind": "flag_line", "x": shown, "x_label": "full years held; the last one is marked",
                      "series": [{"name": f"{words}: {P['label']}", "type": "line", "unit": P["unit"], "values": [common.round6(series[y][0]) for y in shown]}],
                      "mark": {"x": c["last_year"], "value": common.round6(c["last"]), "label": "the last full year"},
                      "ref_lines": [{"name": f"{c['first_year']}", "value": common.round6(c["first"])}], "y_left_label": P["unit"], "decimals": P["decimals"]},
            "callouts": [common.callout("The claim", c["first_year"], val(c["first"], P), c["last_year"], val(c["last"], P)),
                         common.callout("How large", "typical yearly move", val(c["typical_move"], P), "this change, in those", common.fmt(c["strength"], 1)),
                         common.callout("The tests", "years on its side", f"{c['years_held']} of {c['years_after']}",
                                        "tests passed", f"{sum(1 for t in c['tests'] if t['passed'])} of {len(c['tests'])}")],
            "why": "",
            "footnote": (f"A draft of the findings hunt over the whole warehouse (chain 164), builder version {VERSION}, on {common.now_iso()[:10]}; not reviewed. "
                         f"Candidate {P['name']}: {P['label']}. Region: {words} ({region}). {tests_words} Limits: {P['limits']} "
                         f"A full year is not the year under way and holds at least {int(hunt.FULL_SHARE * 100)} percent of the fullest year's observations. "
                         f"The claim states a change; it does not say what caused it. Plan and rubric: {METHOD}."),
            "numbers": {"first": c["first"], "last": c["last"], "change": c["change"], "first_year": int(c["first_year"]), "last_year": int(c["last_year"]),
                        "years_held": c["years_held"], "years_after": c["years_after"], "n_first": c["n_first"], "n_last": c["n_last"],
                        "typical_move": c["typical_move"], "strength": c["strength"], "full_years": len(c["years"])},
            "source_line": source_line, "tables": list(tables), "computed_at": common.now_iso(),
            "method": "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD,
            "scanner": {"version": VERSION, "rule": "hunt", "date": f"{c['last_year']}-12-31", "flag_id": did, "strength": c["strength"], "full_card": None},
            "hunt": {"pattern": P["name"], "module": P["module"], "region": str(region), "region_words": words, "why": why, "tests": c["tests"], "files": files,
                     "measure": P["name"], "family": P["family"], "chain": 164, "limits": P["limits"], "consequence": P["consequence"]}}
    caption = "\n".join([fact, "", f"Checked five ways before it was drafted: {tests_words}", "", f"Limits: {P['limits']}", "", source_line,
                         "Computed by the Energy Research Warehouse (ERW). A draft: not reviewed."])
    card["hunt"]["caption"] = caption
    rep = P["reproduce"](region)
    do_m, py_m = mirrors(P, region, c, files[0], files[2])
    texts = {files[0]: csv_text(P, region, words, series, c, tables), files[1]: do_m, files[2]: py_m,
             files[3]: expected_header(rep["py"], c, P, "#"), files[4]: expected_header(rep["do"], c, P, "*"), files[7]: caption + "\n"}
    os.makedirs(out_dir, exist_ok=True)
    stored = {}
    for name, text in texts.items():
        check_text(text, name)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        stored[name] = {"kind": "text", "content": text}
    check_text(json.dumps(card, ensure_ascii=False), did)
    for name, size in ((files[5], "linkedin_wide"), (files[6], "linkedin_square")):
        p = card_image.render(card, os.path.join(out_dir, name), size, fact=fact)
        with open(p, "rb") as f:
            stored[name] = {"kind": "png", "content": base64.b64encode(f.read()).decode("ascii")}
    flag = {"id": did, "rule": "hunt", "pattern": P["name"], "module": P["module"], "region": str(region), "hunt_version": hunt.VERSION, "deep_version": VERSION,
            "claim": {k: c[k] for k in ("first_year", "last_year", "first", "last", "change", "direction", "years", "values", "n_first", "n_last",
                                        "years_held", "years_after", "typical_move", "strength")},
            "tests": c["tests"], "why": why, "thresholds": {"n_floor": P["n_floor"], "change_threshold": P["change_threshold"], "full_share": hunt.FULL_SHARE}}
    row = {"id": did, "flag_key": f"hunt|{P['module']}|{P['name']}|{region}", "rule": "hunt", "table_name": tables[0],
           "series_key": f"pattern={P['name']}|region={region}", "flag_date": f"{c['last_year']}-12-31", "value": c["change"], "strength": c["strength"],
           "scanner_version": VERSION, "flag": flag, "card": card, "files": stored}
    with open(os.path.join(out_dir, did + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(row, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")
    document(P, s, did, region, words, fact, c, tables, texts, files, out_dir)
    return row


def expected_header(text, c, P, mark):
    """The expected figures at the top of a reproduction script, so the owner sees what his run must print."""
    head = [f"{mark} Expected: {c['first_year']} {common.round6(c['first'])}, {c['last_year']} {common.round6(c['last'])}, "
            f"change {common.round6(c['change'])} ({P['unit']}); tolerance 0.5 percent of the change."]
    if text.startswith("#!") or text.startswith('"""'):
        return text.replace("\n", "\n" + head[0] + "\n", 1) if text.startswith("#!") else head[0] + "\n" + text
    return head[0] + "\n\n" + text


def document(P, s, did, region, words, fact, c, tables, texts, files, out_dir):
    """docs/findings/<family>/<slug>.md, its chart, its reproduction scripts and its CSV."""
    d = os.path.join(DOCS, P["family"])
    os.makedirs(d, exist_ok=True)
    for src, dst in ((files[0], f"{s}.csv"), (files[3], f"{s}.reproduce.py"), (files[4], f"{s}.reproduce.do")):
        with open(os.path.join(d, dst), "w", encoding="utf-8", newline="\n") as f:
            f.write(texts[src])
    with open(os.path.join(out_dir, files[5]), "rb") as f, open(os.path.join(d, f"{s}.png"), "wb") as g:
        g.write(f.read())
    years = ", ".join(f"{y}: {common.fmt(v, P['decimals'])}" for y, v in zip(c["years"], c["values"]))
    md = [f"# {P['title'].capitalize()}: {words}", "",
          f"Draft `{did}` of the findings hunt over the whole warehouse (chain 164), {common.now_iso()[:10]}. State: draft, not reviewed. "
          f"Review at `/internal/findings`.", "",
          f"**The finding.** {fact}", "",
          f"![{P['title'].capitalize()}, {words}]({s}.png)", "",
          f"**The figure by full year** ({P['unit']}): {years}.", "",
          f"**The tables and rows.** {', '.join('`' + t + '`' for t in tables)}; the rows for {words}, region key `{region}` "
          f"(the card's `hunt.region`), years {c['first_year']} to {c['last_year']}. The yearly values: `{s}.csv`.", "",
          f"**Its strength.** The change is {common.fmt(c['strength'], 2)} typical yearly moves (a typical move is {val(c['typical_move'], P)}, "
          f"1.4826 times the median absolute change between full years). " + " ".join(f"{t['name'].capitalize()}: {t['words']}." for t in c["tests"]), "",
          f"**Its limits.** {P['limits']}", "",
          f"**Reproduce.** `python {s}.reproduce.py <the table's CSV>` and `do {s}.reproduce.do` (Stata) recompute the figures by year from the "
          f"tables as the public downloads hold them; each names the expected values at its top.", ""]
    text = "\n".join(md)
    check_text(text, s)
    with open(os.path.join(d, f"{s}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run(family, candidates, in_dir=None, dry_run=True, load=None, log=print, now=None, out_root=None, max_drafts=MAX_DRAFTS):
    """Every candidate of a family: test each region, keep the strongest passing claims, build their drafts and (not a
    dry run) add them to the review list. Returns the summary (also runs/deep/<day>/<family>.json)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    out_dir = os.path.join(out_root or OUT, now.strftime("%Y-%m-%d"), family)
    os.makedirs(out_dir, exist_ok=True)
    blocked = hunt.blocked_grids()
    results, passing, failed = [], [], []
    for P in candidates:
        try:
            got = P["_fn"](in_dir or common.DEFAULT_IN_DIR)
        except common.NoData as exc:
            failed.append({"candidate": P["name"], "reason": f"a table is not on this machine: {str(exc)[:160]}"})
            log(f"  {P['name']}: NOT RUN, a table is not on this machine: {exc}")
            continue
        rows = got["rows"]
        for region in sorted({str(r["region"]) for r in rows}):
            words = next(r["words"] for r in rows if str(r["region"]) == region)
            tables = list(got["tables"].get(region, []))
            row = {"candidate": P["name"], "region": region, "words": words, "drafted": False}
            if hunt.grid_of(region) in blocked:
                row["reason"] = "a grid that needs a license or is held: never drafted"
                results.append(row)
                continue
            series = hunt.yearly(rows, P, region)
            c = hunt.test_claim(series, P, now.year)
            if c is None:
                row["reason"] = "no claim: fewer than two full years, or no change"
            else:
                row.update({k: c[k] for k in ("first_year", "last_year", "first", "last", "change", "strength", "passed")})
                row["tests"] = c["tests"]
                if c["passed"]:
                    passing.append((P, region, words, series, c, tables, row))
                else:
                    row["reason"] = "failed: " + "; ".join(t["name"] for t in c["tests"] if not t["passed"])
            results.append(row)
        log(f"  {P['name']}: {len(rows)} rows, {len({r['region'] for r in rows})} regions, {sum(1 for x in passing if x[0] is P)} pass")
    passing.sort(key=lambda x: (-x[0]["consequence"], -x[4]["strength"], x[1]))
    built, per, seen = [], {}, set()
    for P, region, words, series, c, tables, row in passing:
        same = (round(c["first"], 6), round(c["last"], 6), c["first_year"], c["last_year"])
        story = (P["name"], P.get("area", lambda r: r)(region))
        if same in seen:
            row["reason"] = "passes; the same numbers as a draft kept before it"
            continue
        if story in seen:
            row["reason"] = "passes; folded into the draft of the same candidate and area (a hub and its load zone of one name tell one story)"
            continue
        if per.get(P["name"], 0) >= MAX_PER_CANDIDATE:
            row["reason"] = f"passes; beyond the {MAX_PER_CANDIDATE} strongest regions of its candidate"
            continue
        if len(built) >= max_drafts:
            row["reason"] = f"passes; beyond the {max_drafts} kept this session"
            continue
        seen.add(same)
        seen.add(story)
        per[P["name"]] = per.get(P["name"], 0) + 1
        d = build(P, region, words, series, c, tables, out_dir, "new: the findings hunt over the whole warehouse (chain 164)")
        row.update(drafted=True, draft_id=d["id"], fact=d["card"]["subtitle"])
        built.append(d)
    loaded = []
    if built and not dry_run:
        loaded = (load or hunt.load_drafts)(built, log)
    summary = {"deep_version": VERSION, "family": family, "computed_at": common.now_iso(), "candidates": [P["name"] for P in candidates],
               "claims": len(results), "passed": len(passing), "drafts": [d["id"] for d in built], "loaded": list(loaded), "dry_run": bool(dry_run),
               "failed": failed, "results": results}
    with open(os.path.join(out_dir, f"{family}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")
    log(f"deep {VERSION}, {family}: {len(candidates)} candidates, {len(results)} claims, {len(passing)} pass, {len(built)} drafts, {len(loaded)} loaded"
        + (" (dry run)" if dry_run else ""))
    return summary
