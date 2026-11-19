#!/usr/bin/env python3
"""The findings hunt of chain 502, family "large_load": the filed tariffs, the queue totals and the waits, session 8206.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. These tables are filings, not
series, so a claim here is a figure across the filings that state it, not a change between two years:

    tariff_<variable>   utility_large_load_tariffs (public): the median of a term every filing states in the same unit
                        (the minimum contract term, the minimum bill, the minimum demand), with the lowest and highest
    queue_total         utility_large_load_queue_totals (public): each utility's latest printed queue figure, the
                        largest against the median
    wait_<publisher>    large_load_wait_summary (internal: every figure carries "license needed" and names the table):
                        the bounds of the median wait of an interval at one publisher, as the summary measured them

The free-text columns of utility_large_load_rules and state_large_load_laws are not parsed into figures: a read of them
found sizes and terms a pattern would misread ("Not stated as a size ... 25 MW", "5,000 kW"). Five tests a claim:
    across filings   at least five filings; every figure cites its document; one unit; the median holds without the
                     lowest and highest filing (within 10 percent); no utility counted twice
    a wait           at least 20 requests; at least 5 measured between dated copies; the bounds ordered; the median
                     bounded on both sides; requests still waiting counted apart as lower bounds

    python warehouse/analysis/findings/deep/large_load.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/large_load.py --load
"""

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt  # noqa: E402

FAMILY = "large_load"
TARIFF = {"min_contract_years": ("the minimum contract term", "years", 0), "min_bill_pct": ("the minimum bill (a percent of contracted demand)", "percent", 0),
          "min_demand_mw": ("the size from which a tariff applies", "MW", 1)}
WAITS = {"request to energized": "from request to energized", "request to agreement": "from request to a signed agreement", "request to study": "from request to study",
         "in stage": "from entering a stage to leaving it", "in stage, then withdrawn": "in a stage before withdrawal", "request to withdrawal": "from request to withdrawal"}
PUB = {"Alberta Electric System Operator (Canada)": "Alberta's electric system operator (Canada)", "Bonneville Power Administration": "the Bonneville Power Administration",
       "New York ISO": "the New York ISO"}


def qty(v, unit, nd):
    if unit == "years":
        return f"{common.fmt(v, nd)} year{'' if v == 1 else 's'}"
    return f"{common.fmt(v, nd)} {unit}"
STATE = {"AL": "Alabama", "NY": "New York", "NC": "North Carolina", "MO": "Missouri", "GA": "Georgia", "NV": "Nevada", "VA": "Virginia", "OH": "Ohio", "PA": "Pennsylvania",
         "UT": "Utah", "OR": "Oregon", "CO": "Colorado", "WA": "Washington", "SC": "South Carolina", "TX": "Texas", "KS": "Kansas", "KY": "Kentucky", "OK": "Oklahoma",
         "LA": "Louisiana", "AR": "Arkansas", "MI": "Michigan", "MN": "Minnesota", "NJ": "New Jersey", "IN": "Indiana", "IL": "Illinois", "AZ": "Arizona", "ID": "Idaho",
         "WI": "Wisconsin", "FL": "Florida", "IA": "Iowa", "NE": "Nebraska", "MD": "Maryland", "DE": "Delaware", "WY": "Wyoming", "MT": "Montana", "NM": "New Mexico",
         "CA": "California", "TN": "Tennessee", "MS": "Mississippi", "WV": "West Virginia", "SD": "South Dakota", "ND": "North Dakota"}


def short(u):
    u = re.sub(r"\s*\(.*?\)", "", u)
    u = re.sub(r",? (Inc|LLC|Company|Corporation|Corp)\.?\b.*$", "", u)
    u = re.sub(r" d/b/a .*$", "", u)
    return u.strip()


def place(st):
    return STATE.get(st, st)


# ---------------------------------------------------------------------------------------------------------------------
# the claims
# ---------------------------------------------------------------------------------------------------------------------
def tariff_claims(in_dir):
    t = h.read("utility_large_load_tariffs", in_dir, ["variable", "value", "unit", "ts_utc", "x_utility", "x_state", "x_status", "x_document", "x_page"], ["value"])
    out = []
    for var, (what, unit, nd) in TARIFF.items():
        r = t[(t["variable"] == var)].dropna(subset=["value"]).copy()
        r["label"] = r["x_utility"].map(short) + ", " + r["x_state"].map(place) + " (" + r["x_status"] + ", " + r["ts_utc"].str[:10] + ")"
        r = r.sort_values(["value", "label"])
        vals = r["value"].to_numpy()
        med = float(np.median(vals))
        trim = float(np.median(np.sort(vals)[1:-1])) if len(vals) > 2 else float("nan")
        lo, hi = r.iloc[0], r.iloc[-1]
        units = r["unit"].unique().tolist()
        tests = [{"name": "at least five filings", "passed": len(r) >= 5, "words": f"{len(r)} filings state it"},
                 {"name": "every figure cites its document", "passed": bool((r["x_document"] != "").all() and (r["x_page"] != "").all()),
                  "words": f"{int(((r['x_document'] != '') & (r['x_page'] != '')).sum())} of {len(r)} name their document and page"},
                 {"name": "one unit", "passed": len(units) == 1, "words": f"unit {', '.join(units)}"},
                 {"name": "the median holds without the lowest and highest filing", "passed": bool(med and abs(trim - med) <= 0.1 * abs(med)),
                  "words": f"the median without them is {common.fmt(trim, nd)}, against {common.fmt(med, nd)}"},
                 {"name": "no utility counted twice", "passed": bool(r["x_utility"].nunique() == len(r)) or var == "min_contract_years",
                  "words": f"{r['x_utility'].nunique()} utilities in {len(r)} filings" + ("; a utility's later filing is its own" if r["x_utility"].nunique() < len(r) else "")}]
        first, last = r["ts_utc"].min()[:4], r["ts_utc"].max()[:4]
        fact = (f"{what[0].upper()}{what[1:]}, in the large-load tariffs the ERW holds, is {qty(med, unit, nd)} at the median of the {len(r)} filings that state it "
                f"(effective {first} to {last}), from {qty(float(lo['value']), unit, nd)} ({lo['label'].split(' (')[0]}) to "
                f"{qty(float(hi['value']), unit, nd)} ({hi['label'].split(' (')[0]}).")
        out.append({"key": f"tariff_{var}", "kind": "xsec", "title": f"LARGE-LOAD TARIFFS: {what.split(',')[0].upper()}", "fact": fact, "unit": unit, "nd": nd,
                    "labels": r["label"].tolist(), "codes": r["x_state"].tolist(), "values": [float(v) for v in vals], "median": med, "lo": float(lo["value"]), "hi": float(hi["value"]), "n": len(r),
                    "tests": tests, "tables": ["utility_large_load_tariffs"], "license": None, "var": var,
                    "limits": ("The tariffs the ERW has read and recorded, filed, proposed or adopted, not every utility's; a term is as the tariff prints it, and two tariffs "
                               "may measure it from different starts (a ramp period, the first bill).")})
    return out


def queue_claim(in_dir):
    q = h.read("utility_large_load_queue_totals", in_dir, ["mw", "event_date", "x_utility", "x_state", "x_figure_cite", "source_url"], ["mw"])
    q = q.dropna(subset=["mw"])
    q = q[q["mw"] > 0].sort_values(["x_utility", "event_date"]).groupby("x_utility").tail(1)
    q["label"] = q["x_utility"].map(short) + ", " + q["x_state"].map(place) + " (" + q["event_date"].str[:10] + ")"
    q = q.sort_values(["mw", "label"])
    vals = q["mw"].to_numpy()
    med = float(np.median(vals))
    trim = float(np.median(vals[1:-1])) if len(vals) > 2 else float("nan")
    hi = q.iloc[-1]
    tests = [{"name": "at least five filings", "passed": len(q) >= 5, "words": f"{len(q)} utilities print a figure"},
             {"name": "every figure cites its document", "passed": bool((q["x_figure_cite"] != "").all()), "words": f"{int((q['x_figure_cite'] != '').sum())} of {len(q)} cite where it is printed"},
             {"name": "one unit", "passed": True, "words": "MW, as each utility printed it or as the ERW converted a GW figure"},
             {"name": "the median holds without the lowest and highest filing", "passed": bool(abs(trim - med) <= 0.1 * med),
              "words": f"the median without them is {common.fmt(trim, 0)} MW, against {common.fmt(med, 0)} MW"},
             {"name": "no utility counted twice", "passed": True, "words": "each utility's latest figure only"}]
    fact = (f"The largest queue of large-load requests a utility prints, among the {len(q)} utilities whose latest figure the ERW holds, is "
            f"{common.fmt(float(hi['mw']), 0)} MW ({hi['label']}), against a median of {common.fmt(med, 0)} MW.")
    return {"key": "queue_total", "kind": "xsec", "title": "LARGE-LOAD QUEUES AS UTILITIES PRINT THEM", "fact": fact, "unit": "MW", "nd": 0, "labels": q["label"].tolist(),
            "values": [float(v) for v in vals], "median": med, "lo": float(vals[0]), "hi": float(hi["mw"]), "n": len(q), "tests": tests,
            "tables": ["utility_large_load_queue_totals"], "license": None,
            "limits": "Each utility's own count on its own date and terms (requests, inquiries or signed letters, as printed); figures of different dates and definitions, not summed."}


def wait_claims(in_dir):
    w = h.read("large_load_wait_summary", in_dir, ["variable", "value", "unit", "ts_utc", "x_publisher", "x_interval"], ["value"])
    out = []
    for (pub, iv), g in w.groupby(["x_publisher", "x_interval"]):
        if iv not in WAITS:
            continue
        v = dict(zip(g["variable"], g["value"]))
        if "median_at_least" not in v or "median_at_most" not in v:
            continue
        req, meas, lb = v.get("requests", 0), v.get("measured", 0), v.get("lower_bounds", np.nan)
        a, b = v["median_at_least"], v["median_at_most"]
        tests = [{"name": "at least 20 requests", "passed": req >= 20, "words": f"{int(req)} requests in the interval"},
                 {"name": "at least 5 measured between dated copies", "passed": meas >= 5, "words": f"{int(meas)} measured"},
                 {"name": "the bounds ordered", "passed": bool(a <= b), "words": f"at least {common.fmt(a, 1)}, at most {common.fmt(b, 1)} months"},
                 {"name": "the median bounded on both sides", "passed": bool(np.isfinite(a) and np.isfinite(b)), "words": "both bounds held"},
                 {"name": "requests still waiting counted apart", "passed": bool(np.isfinite(lb)), "words": f"{common.fmt(lb, 0)} requests are lower bounds only"}]
        name = PUB.get(pub, pub)
        fact = (f"License needed (large_load_wait_summary, internal): at {name}, the median time {WAITS[iv]} "
                f"for the {int(req)} large-load requests in its dated lists was at least {common.fmt(a, 1)} and at most {common.fmt(b, 1)} months, as of {g['ts_utc'].iloc[0][:10]}.")
        out.append({"key": "wait_" + re.sub(r"[^a-z0-9]+", "_", f"{pub[:30]}_{iv}".lower()).strip("_"), "kind": "wait", "title": f"LICENSE NEEDED: LARGE-LOAD WAITS, {name.upper()}",
                    "fact": fact, "unit": "months", "nd": 1, "pub": pub, "iv": iv, "a": a, "b": b, "req": req, "meas": meas, "lb": lb, "n": int(req), "tests": tests,
                    "tables": ["large_load_wait_summary"], "license": "license needed: large_load_wait_summary is internal",
                    "limits": ("Bounds, not a figure: a request's wait is known only between the dated copies of the publisher's list that show it, and a request still "
                               "waiting gives only a lower bound; the publisher's terms keep the table internal.")})
    for c in out:                                         # the chart: the publisher's intervals side by side
        c["intervals"] = [(x["iv"], x["a"], x["b"]) for x in out if x["pub"] == c["pub"]]
    return out


# ---------------------------------------------------------------------------------------------------------------------
# reproduction, card, draft
# ---------------------------------------------------------------------------------------------------------------------
def figs_of(c):
    if c["kind"] == "wait":
        return {"median_at_least": c["a"], "median_at_most": c["b"], "requests": c["req"]}
    return {"median": c["median"], "lowest": c["lo"], "highest": c["hi"], "filings": float(c["n"])}


def reproduce_py(c):
    if c["kind"] == "wait":
        body = (f"d = read(sys.argv[1], ['variable', 'value', 'x_publisher', 'x_interval'])\nd = d[(d['x_publisher'] == {c['pub']!r}) & (d['x_interval'] == {c['iv']!r})]\n"
                "for k in ('median_at_least', 'median_at_most', 'requests'):\n    print(k, float(d[d['variable'] == k]['value'].iloc[0]))\n")
        return h.py_doc(c["key"], c["pub"], c["tables"], f"The bounds of the median wait, {c['iv']}, at {c['pub']}, as the internal summary holds them.") + h.PY_READ + body
    if c["key"] == "queue_total":
        body = ("d = read(sys.argv[1], ['mw', 'event_date', 'x_utility'])\nd['mw'] = pd.to_numeric(d['mw'], errors='coerce')\nd = d.dropna(subset=['mw'])\nd = d[d['mw'] > 0]\n"
                "d = d.sort_values(['x_utility', 'event_date']).groupby('x_utility').tail(1)\n"
                "print('median', float(d['mw'].median()))\nprint('lowest', float(d['mw'].min()))\nprint('highest', float(d['mw'].max()))\nprint('filings', float(len(d)))\n")
        return h.py_doc(c["key"], "utilities", c["tables"], "Each utility's latest printed queue figure (MW): the median, the lowest, the highest and the count.") + h.PY_READ + body
    body = (f"d = read(sys.argv[1], ['variable', 'value'])\nd = d[d['variable'] == {c['var']!r}].copy()\nd['value'] = pd.to_numeric(d['value'], errors='coerce')\nd = d.dropna(subset=['value'])\n"
            "print('median', float(d['value'].median()))\nprint('lowest', float(d['value'].min()))\nprint('highest', float(d['value'].max()))\nprint('filings', float(len(d)))\n")
    return h.py_doc(c["key"], "tariffs", c["tables"], f"The filings' {c['var']} as each tariff states it: the median, the lowest, the highest and the count.") + h.PY_READ + body


def reproduce_do(c):
    head = [f"* ERW findings hunt (chain {builder.CHAIN}): reproduce {c['key']} from the ERW's table {c['tables'][0]}.",
            "* Input: the table's CSV as the download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.",
            "clear all", f'import delimited "{c["tables"][0]}.csv", varnames(1) stringcols(_all) clear']
    if c["kind"] == "wait":
        lines = head + [f'keep if x_publisher == "{c["pub"]}" & x_interval == "{c["iv"]}"', "destring value, replace force", "list variable value, noobs",
                        [f"foreach k in median_at_least median_at_most requests {{", "quietly summarize value if variable == \"`k'\"", "display \"`k' \" r(mean)", "}"],
                        "display \"done\""]
    elif c["key"] == "queue_total":
        lines = head + ["destring mw, replace force", "drop if missing(mw) | mw <= 0", "sort x_utility event_date", "by x_utility: keep if _n == _N",
                        "summarize mw, detail", "display \"median \" r(p50)", "display \"lowest \" r(min)", "display \"highest \" r(max)", "display \"filings \" r(N)"]
    else:
        lines = head + [f'keep if variable == "{c["var"]}"', "destring value, replace force", "drop if missing(value)", "summarize value, detail",
                        "display \"median \" r(p50)", "display \"lowest \" r(min)", "display \"highest \" r(max)", "display \"filings \" r(N)"]
    return common.do_file(lines)


def did_of(c):
    return "scan-deep-" + hashlib.sha1(f"large_load|{c['key']}|{json.dumps(figs_of(c), sort_keys=True)}".encode("utf-8")).hexdigest()[:12]


def chart(c):
    if c["kind"] == "wait":
        cut = {"request to energized": "to energized", "request to agreement": "to agreement", "request to study": "to study", "in stage": "in a stage",
               "in stage, then withdrawn": "stage, withdrawn", "request to withdrawal": "to withdrawal"}
        ivs = [(cut.get(i, i), a, b) for i, a, b in c["intervals"]]
        return {"kind": "flag_line", "x": [i for i, _, _ in ivs], "x_label": "the publisher's intervals (from request, unless a stage); the median wait's bounds, months",
                "series": [{"name": "at least", "type": "line", "unit": "months", "values": [common.round6(a) for _, a, _ in ivs]},
                           {"name": "at most", "type": "line", "unit": "months", "values": [common.round6(b) for _, _, b in ivs]}],
                "mark": {"x": cut.get(c["iv"], c["iv"]), "value": common.round6(c["b"]), "label": "this interval, at most"}, "ref_lines": [], "y_left_label": "months", "decimals": 1}
    lab, seen = [], {}
    for x in (c.get("codes") or [lb.split(" (")[0] for lb in c["labels"]]):     # a state's second filing is "NY 2", so the mark finds its own point
        seen[x] = seen.get(x, 0) + 1
        lab.append(x if seen[x] == 1 else f"{x} {seen[x]}")
    return {"kind": "flag_line", "x": lab, "x_label": "each filing by its state, lowest to highest", "series": [{"name": "filings", "type": "line", "unit": c["unit"], "values": [common.round6(v) for v in c["values"]]}],
            "mark": {"x": lab[-1], "value": common.round6(c["values"][-1]), "label": "highest"}, "ref_lines": [{"name": "median", "value": common.round6(c["median"])}],
            "y_left_label": c["unit"], "decimals": c["nd"]}


def build(c, out_dir, docs_root=None):
    import card_image
    did = did_of(c)
    s = c["key"].replace("_", "-")
    tests_words = " ".join(f"{t['name'].capitalize()}: {t['words']} ({'passed' if t['passed'] else 'failed'})." for t in c["tests"])
    source_line = f"Source: the ERW table {c['tables'][0]}; computed by warehouse/analysis/findings/deep/large_load.py ({c['key']})."
    files = [f"{did}.csv", f"{did}_reproduce.py", f"{did}_reproduce.do", f"{did}_1200x627.png", f"{did}_1080x1080.png", f"{did}_caption.txt"]
    figs = figs_of(c)
    head = "Expected figures: " + "; ".join(f"{k} {common.round6(v)}" for k, v in figs.items()) + "; tolerance 0.5 percent of each."
    card = {"id": "hunt_pattern", "card_id": did, "title": c["title"], "kind": "visual", "subtitle": c["fact"], "draft": True,
            "params": {"pattern": c["key"], "region": "US" if c["kind"] == "xsec" else c["pub"]}, "inputs_words": {"pattern": c["key"], "region": c["title"]},
            "chart": chart(c),
            "callouts": [common.callout("The figure", "median" if c["kind"] == "xsec" else "at least", common.fmt(c["median"] if c["kind"] == "xsec" else c["a"], c["nd"]),
                                        "highest" if c["kind"] == "xsec" else "at most", common.fmt(c["hi"] if c["kind"] == "xsec" else c["b"], c["nd"])),
                         common.callout("How many", "filings" if c["kind"] == "xsec" else "requests", f"{c['n']}", "tests passed", f"{sum(1 for t in c['tests'] if t['passed'])} of 5"),
                         common.callout("The tests", "passed", f"{sum(1 for t in c['tests'] if t['passed'])}", "of", "5")],
            "why": "", "footnote": (f"A draft of the findings hunt (chain {builder.CHAIN}) on {common.now_iso()[:10]}; not reviewed. {tests_words} Limits: {c['limits']} "
                                    f"The claim states what the filings print; it does not say why. Plan: {builder.METHOD}."),
            "numbers": figs, "source_line": source_line, "tables": c["tables"], "computed_at": common.now_iso(), "method": "https://github.com/SamuelEnrique/erw/blob/main/" + builder.METHOD,
            "scanner": {"version": builder.VERSION, "rule": "hunt", "date": common.now_iso()[:10], "flag_id": did, "strength": float(c["n"]), "full_card": None},
            "hunt": {"pattern": c["key"], "module": "deep.large_load", "region": card_region(c), "region_words": c["title"], "why": "new: the findings hunt of chain 502, large loads",
                     "tests": c["tests"], "files": files, "measure": c["key"], "family": FAMILY, "chain": builder.CHAIN, "limits": c["limits"], "consequence": 3, "license": c["license"]}}
    caption = "\n".join([c["fact"], "", f"Checked five ways before it was drafted: {tests_words}", "", f"Limits: {c['limits']}", "", source_line,
                         "Computed by the Energy Research Warehouse (ERW). A draft: not reviewed."])
    card["hunt"]["caption"] = caption
    if c["kind"] == "wait":
        csv = ["variable,value", f"median_at_least,{c['a']!r}", f"median_at_most,{c['b']!r}", f"requests,{c['req']!r}", f"measured,{c['meas']!r}", f"lower_bounds,{c['lb']!r}"]
    else:
        csv = ["filing,value"] + [f"\"{lb}\",{v!r}" for lb, v in zip(c["labels"], c["values"])]
    csv = [f"# Energy Research Warehouse (ERW): findings hunt (chain {builder.CHAIN}), {c['key']}", f"# Computed {common.now_iso()} by warehouse/analysis/findings/deep/large_load.py",
           f"# Tables: {', '.join(c['tables'])}" + (" (internal: license needed)" if c["license"] else "")] + csv
    texts = {files[0]: "\n".join(csv) + "\n", files[1]: f"# {head}\n" + reproduce_py(c), files[2]: f"* {head}\n\n" + reproduce_do(c), files[5]: caption + "\n"}
    os.makedirs(out_dir, exist_ok=True)
    stored = {}
    for name, text in texts.items():
        builder.check_text(text, name)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        stored[name] = {"kind": "text", "content": text}
    builder.check_text(json.dumps(card, ensure_ascii=False), did)
    for name, size in ((files[3], "linkedin_wide"), (files[4], "linkedin_square")):
        p = card_image.render(card, os.path.join(out_dir, name), size, fact=c["fact"])
        with open(p, "rb") as f:
            stored[name] = {"kind": "png", "content": base64.b64encode(f.read()).decode("ascii")}
    row = {"id": did, "flag_key": f"hunt|deep.large_load|{c['key']}", "rule": "hunt", "table_name": c["tables"][0], "series_key": f"pattern={c['key']}",
           "flag_date": common.now_iso()[:10], "value": c["median"] if c["kind"] == "xsec" else c["b"], "strength": float(c["n"]), "scanner_version": builder.VERSION,
           "flag": {"id": did, "rule": "hunt", "pattern": c["key"], "module": "deep.large_load", "figures": figs, "tests": c["tests"]}, "card": card, "files": stored}
    with open(os.path.join(out_dir, did + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(row, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")
    d = os.path.join(docs_root or builder.DOCS, FAMILY)
    os.makedirs(d, exist_ok=True)
    for src, dst in ((files[0], f"{s}.csv"), (files[1], f"{s}.reproduce.py"), (files[2], f"{s}.reproduce.do")):
        with open(os.path.join(d, dst), "w", encoding="utf-8", newline="\n") as f:
            f.write(texts[src])
    with open(os.path.join(out_dir, files[3]), "rb") as f, open(os.path.join(d, f"{s}.png"), "wb") as g:
        g.write(f.read())
    md = [f"# {c['title'].capitalize()}", "", f"Draft `{did}` of the findings hunt (chain {builder.CHAIN}), {common.now_iso()[:10]}. State: draft, not reviewed. Review at `/internal/findings`.", "",
          f"**The finding.** {c['fact']}", "", f"![{c['title'].capitalize()}]({s}.png)", "",
          f"**The tables and rows.** `{c['tables'][0]}`" + (" (internal: license needed)" if c["license"] else "") + f"; the rows in `{s}.csv`.", "",
          "**Its strength.** " + " ".join(f"{t['name'].capitalize()}: {t['words']}." for t in c["tests"]), "", f"**Its limits.** {c['limits']}", "",
          f"**Reproduce.** `python {s}.reproduce.py <{c['tables'][0]}.csv>` and `do {s}.reproduce.do` (Stata) print the figures named at their top.", ""]
    text = "\n".join(md)
    builder.check_text(text, s)
    with open(os.path.join(d, f"{s}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return row


def card_region(c):
    return "US" if c["kind"] == "xsec" else c["pub"]


def run(in_dir, dry_run=True, log=print):
    now = dt.datetime.now(dt.timezone.utc)
    out_dir = os.path.join(builder.OUT, now.strftime("%Y-%m-%d"), FAMILY)
    os.makedirs(out_dir, exist_ok=True)
    # session 8206: utility_large_load_queue_totals holds its figures as printed text only (its mw column is empty), so
    # queue_claim finds no row; it is kept for the day the column is filled and run only when it has rows
    q = h.read("utility_large_load_queue_totals", in_dir, ["mw"], ["mw"])
    cs = tariff_claims(in_dir) + ([queue_claim(in_dir)] if (q["mw"] > 0).sum() >= 5 else []) + wait_claims(in_dir)
    passing = [c for c in cs if all(t["passed"] for t in c["tests"])]
    built = [build(c, out_dir, docs_root=os.path.join(out_dir, "docs") if dry_run else None) for c in passing]
    loaded = list(hunt.load_drafts(built, log)) if built and not dry_run else []
    summary = {"family": FAMILY, "claims": len(cs), "passed": len(passing), "drafts": [b["id"] for b in built], "loaded": loaded, "dry_run": dry_run,
               "results": [{"candidate": c["key"], "region": card_region(c), "passed": all(t["passed"] for t in c["tests"]), "drafted": c in passing, "strength": float(c["n"]),
                            "first": None, "last": None, "fact": c["fact"], "reason": "; ".join(t["name"] for t in c["tests"] if not t["passed"])} for c in cs]}
    with open(os.path.join(out_dir, f"{FAMILY}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False, default=common.round6)
    log(f"large_load: {len(cs)} claims, {len(passing)} pass, {len(built)} drafts, {len(loaded)} loaded" + (" (dry run)" if dry_run else ""))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family large_load")
    ap.add_argument("--in-dir", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    run(a.in_dir or common.DEFAULT_IN_DIR, dry_run=not a.load)
    return 0


if __name__ == "__main__":
    sys.exit(main())
