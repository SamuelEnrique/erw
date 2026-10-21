#!/usr/bin/env python3
"""Session 539: session 320's thirty questions to Ask, graded again offline. No model call of any kind.

Energy Research Warehouse (ERW). Two steps:

    python warehouse/chat/eval/regrade_s539.py --keys     # the keys again, from the live set (Supabase, the anon key, reads only)
    python warehouse/chat/eval/regrade_s539.py            # offline: the stored answers graded against the stored and the new keys

`--keys` computes every expected number of questions_s320.yaml again, by the aggregation its note names, over the period
its question names (the questions name their months: "the last twelve complete months" is 2025-10 to 2026-09 in the
text, so the window is held fixed), and writes eval_s539_keys.json beside this file, with the reads a cause needs: each
battery figure in the table's own unit (USD per MW), the days left out, and NYISO's July 2026 price in the second table
that holds it. The default step reads only files: eval_s320_first_run.json (the answers as the run of 20 October wrote
them), questions_s320.yaml (the keys of 19 October) and eval_s539_keys.json, grades each answer with session 267's grader
(eval_s267.py) against both sets of keys, and prints and writes eval_s539_regrade.json. The causes are assigned in
CAUSES below from the stored answer, the server's log of the run (runs/chain_oct19/s320/server.out, not in git: the
number check's lines) and these reads; docs/reviews/ask-thirty-2026-10-21.md is the table.
"""

import datetime as dt
import importlib.util
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIRST_RUN = os.path.join(HERE, "eval_s320_first_run.json")
QUESTIONS = os.path.join(HERE, "questions_s320.yaml")
KEYS = os.path.join(HERE, "eval_s539_keys.json")
REGRADE = os.path.join(HERE, "eval_s539_regrade.json")
LICENSE = os.path.join(ROOT, "site", "data", "license_status.json")
GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}

B, M, C = "battery_stack_monthly", "merchant_revenue_monthly", "cost_of_power_monthly"
E, SP15, NP15 = "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "caiso:TH_NP15_GEN-APND"
NYC, ISNE, SPP = "nyiso:N.Y.C.", "isone:.H.INTERNAL_HUB", "spp:SPPNORTH_HUB"
L12 = ("2025-10", "2026-09")

# id: (table, entity, variable, aggregation, period, divisor). Aggregations: sum over a window, sum or mean over a year,
# the value of one month, the largest month of a year. divisor 1000: the question asks USD per kW of a USD per MW table.
SPEC = {
    "b01": (B, E, "foresight_4h_revenue_total_usd_per_mw", "sum", L12, 1000),
    "b02": (B, E, "foresight_4h_revenue_energy_usd_per_mw", "sum", L12, 1000),
    "b03": (B, E, "foresight_4h_revenue_ancillary_usd_per_mw", "sum", L12, 1000),
    "b04": (B, E, "dayahead_2h_revenue_total_usd_per_mw", "sum", L12, 1000),
    "b05": (B, E, "foresight_4h_revenue_total_usd_per_mw", "sum", ("2021-01", "2021-12"), 1000),
    "b06": (B, E, "foresight_4h_revenue_total_usd_per_mw", "sum", ("2025-01", "2025-12"), 1000),
    "b07": (B, E, "foresight_4h_revenue_total_usd_per_mw", "max", ("2025-01", "2025-12"), 1),
    "b08": (B, SP15, "foresight_4h_revenue_total_usd_per_mw", "sum", L12, 1000),
    "b09": (B, SP15, "dayahead_4h_revenue_energy_usd_per_mw", "sum", ("2025-01", "2025-12"), 1000),
    "b10": (B, E, "foresight_8h_discharged_mwh_per_mw", "month", ("2026-07", "2026-07"), 1),
    "g01": (M, E, "solar_capture_price", "month", ("2026-07", "2026-07"), 1),
    "g02": (M, E, "wind_capture_rate", "month", ("2026-06", "2026-06"), 1),
    "g03": (M, E, "peaker_revenue_per_mw", "sum", ("2025-01", "2025-12"), 1),
    "g04": (M, E, "solar_energy_per_mw", "sum", ("2025-01", "2025-12"), 1),
    "g05": (M, SP15, "solar_capture_rate", "mean", ("2025-01", "2025-12"), 1),
    "g06": (M, SPP, "wind_revenue_per_mw", "sum", ("2025-01", "2025-12"), 1),
    "g07": (M, ISNE, "solar_capture_price", "month", ("2026-08", "2026-08"), 1),
    "g08": (M, NYC, "flat_price", "month", ("2026-07", "2026-07"), 1),
    "g09": (M, E, "battery_4h_revenue_per_mw", "sum", L12, 1),
    "d01": (C, E, "rt_load_weighted", "month", ("2026-08", "2026-08"), 1),
    "d02": (C, E, "da_load_weighted", "month", ("2026-01", "2026-01"), 1),
    "d03": (C, NP15, "rt_shape_premium", "month", ("2026-07", "2026-07"), 1),
    "d04": (C, E, "rt_simple_mean", "mean", ("2025-01", "2025-12"), 1),
    "d05": (C, NYC, "rt_load_weighted", "month", ("2026-01", "2026-01"), 1),
    "d06": (C, SPP, "rt_hours", "month", ("2026-07", "2026-07"), 1),
    "d07": (C, ISNE, "da_shape_premium", "month", ("2026-06", "2026-06"), 1),
    "d08": (C, E, "rt_load_weighted", "max", ("2025-01", "2025-12"), 1),
}
# d09: a difference of two months, and its two parts
D09 = ((C, E, "rt_load_weighted", "2026-06"), (C, SP15, "rt_load_weighted", "2026-06"))
# the further reads a cause needs: the days the battery model left out in each battery question's period, and the
# second table that holds NYISO's flat July price (the one g08's answer read)
EXTRA = {
    "b08_days_left_out": (B, SP15, "foresight_4h_days_left_out", "sum", L12),
    "b09_days_left_out": (B, SP15, "dayahead_4h_days_left_out", "sum", ("2025-01", "2025-12")),
    "b01_days_left_out": (B, E, "foresight_4h_days_left_out", "sum", L12),
    "g08_cost_of_power_rt_simple_mean": (C, NYC, "rt_simple_mean", "month", ("2026-07", "2026-07")),
    "g08_cost_of_power_rt_hours": (C, NYC, "rt_hours", "month", ("2026-07", "2026-07")),
}

# The cause of each wrong answer: one of the four of the session's brief, with what it rests on. Assigned by hand from
# the stored answer, the run's server log and the reads above; the tests hold each to its evidence.
TOOL = "the tool did not return the figure"
STATED = "the answer stated a figure no tool returned"
REACH = "the question needs a table the tools cannot reach"
KEY = "the expected value was wrong"
CAUSES = {
    "b01": (TOOL, "USD per kW is held by no table; the answer gives the key's figure in USD per MW (81,402.19 = 81.4022 x 1,000) and refuses the conversion; the first draft's 1000 was untraced by the number check"),
    "b02": (TOOL, "as b01: 54,598.58 USD per MW stated, the key 54.5986 per kW"),
    "b03": (TOOL, "as b01: 26,803.61 USD per MW stated, the key 26.8036 per kW"),
    "b04": (TOOL, "as b01: 51,067.14 USD per MW stated, the key 51.0671 per kW"),
    "b05": (TOOL, "as b01: 3,430,556.56 USD per MW stated, the key 3,430.5566 per kW"),
    "b06": (TOOL, "as b01: 87,439.61 USD per MW stated, the key 87.4396 per kW"),
    "b08": (TOOL, "as b01; the USD per MW figure stated (79,308.31) missed the key of 19 October (79.046 per kW) but is the table now (79,308.31 = 79.3083 x 1,000): the table was run again between the keys and the asking (its run of 2026-10-20T01:04Z), so that key was stale too"),
    "b09": (TOOL, "as b01; the USD per MW figure stated (42,503.77) missed the key of 19 October (42.3137 per kW) but is the table now (42.5038 per kW, 3 days left out): the key was stale, as b08"),
    "g03": (KEY, "the figure is right (about 50,424 against 50,424.07); the key's absolute tolerance of 0.01 on a five-digit sum fails an answer rounded to the dollar"),
    "g06": (KEY, "as g03: about 66,963 against 66,963.01"),
    "g09": (KEY, "as g03: about 58,534 against 58,533.70"),
    "g08": (KEY, "the figure is right (73.87); the key names merchant_revenue_monthly only and the answer read and cited the same price in cost_of_power_monthly (rt_simple_mean)"),
    "d10": (KEY, "the refusal is right and states no figure; the key asks a refusal to cite cost_of_power_monthly, and a refusal cites no table (g10 passed only because its answer named the table it read)"),
}
FOURS = (TOOL, STATED, REACH, KEY)


def env(name):
    if os.environ.get(name):
        return os.environ[name].strip()
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        m = re.match(rf"^{name}=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"')
    raise SystemExit(f"{name} not in .env")


def rows(url, headers, table, entity, variable):
    out, off = [], 0
    while True:
        q = {"table_name": f"eq.{table}", "entity": f"eq.{entity}", "variable": f"eq.{variable}", "select": "ts_utc,value", "order": "ts_utc", "limit": "1000", "offset": str(off)}
        req = urllib.request.Request(f"{url}/series?" + urllib.parse.urlencode(q), headers=headers)
        with urllib.request.urlopen(req, timeout=90) as r:
            page = json.loads(r.read())
        out += page
        if len(page) < 1000:
            break
        off += 1000
    if not out:
        raise SystemExit(f"no rows: {table} {entity} {variable}")
    return [(r["ts_utc"][:7], float(r["value"])) for r in out if r["value"] is not None]


def months(a, b):
    y, m = int(a[:4]), int(a[5:])
    out = []
    while f"{y:04d}-{m:02d}" <= b:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def aggregate(series, how, period):
    want = months(*period)
    got = {m: v for m, v in series if m in want}
    missing = [m for m in want if m not in got]
    if missing:
        raise SystemExit(f"months missing: {missing}")
    vals = [got[m] for m in want]
    if how == "sum":
        return sum(vals), None
    if how == "mean":
        return sum(vals) / len(vals), None
    if how == "month":
        return vals[0], None
    if how == "max":
        best = max(want, key=lambda m: got[m])
        return got[best], best
    raise ValueError(how)


def build_keys():
    url = env("SUPABASE_URL").rstrip("/")
    key = env("SUPABASE_ANON_KEY")
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    cache = {}

    def series(t, e, v):
        if (t, e, v) not in cache:
            cache[(t, e, v)] = rows(url, h, t, e, v)
        return cache[(t, e, v)]

    out = {}
    for qid, (t, e, v, how, period, div) in SPEC.items():
        val, at = aggregate(series(t, e, v), how, period)
        rec = {"table": t, "entity": e, "variable": v, "aggregation": how, "period": list(period), "table_unit_value": round(val, 4), "expected": [round(val / div, 4)]}
        if at:
            rec["month"] = at
            rec["month_name"] = dt.date(int(at[:4]), int(at[5:]), 1).strftime("%B")
        out[qid] = rec
    (t1, e1, v1, m1), (t2, e2, v2, m2) = D09
    a = aggregate(series(t1, e1, v1), "month", (m1, m1))[0]
    b = aggregate(series(t2, e2, v2), "month", (m2, m2))[0]
    out["d09"] = {"table": t1, "entity": f"{e1} less {e2}", "variable": v1, "aggregation": "difference", "period": [m1, m1], "table_unit_value": round(a - b, 4), "expected": [round(a - b, 4), round(a, 4), round(b, 4)]}
    extra = {}
    for name, (t, e, v, how, period) in EXTRA.items():
        extra[name] = round(aggregate(series(t, e, v), how, period)[0], 4)
    doc = {
        "_about": "Session 539: the expected numbers of questions_s320.yaml computed again from the live set (Supabase, the anon key, reads only, no model call) by warehouse/chat/eval/regrade_s539.py --keys; each key by the aggregation its note names over the months its question names. table_unit_value is the figure in the table's own unit (USD per MW for the battery revenues asked per kW).",
        "computed_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": f"the live set's series view, read with the anon key: table_name in ({B}, {M}, {C})",
        "keys": out,
        "extra": extra,
    }
    with open(KEYS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"wrote {KEYS}: {len(out)} keys")
    return doc


def load_yaml(path):
    qs, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("- id: "):
            cur = {"id": line[6:].strip()}
            qs.append(cur)
        elif line.startswith("  ") and cur is not None and ": " in line:
            k, v = line[2:].split(": ", 1)
            if k in ("question", "expected", "text", "tables", "note"):
                cur[k] = json.loads(v)
            elif k == "tolerance":
                cur[k] = float(v)
            elif k == "refuse":
                cur[k] = v.strip() == "true"
            else:
                cur[k] = v.strip()
    return qs


def grader():
    spec = importlib.util.spec_from_file_location("eval_s267_for_s539", os.path.join(HERE, "eval_s267.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def held_row(table, entity, day):
    """The site's license hold on one row (site/lib/license.ts, licenseHeldRow): a table "license needed" from its day,
    decided by grid operators only, holds the rows of those grids; one decided by anyone else is held whole."""
    with open(LICENSE, encoding="utf-8") as f:
        r = json.load(f)["tables"].get(table)
    if not r or r["status"] != "license needed" or day < r["from"]:
        return False
    pubs = r.get("publishers") or []
    if not pubs or not all(p in GRID_PREFIX for p in pubs):
        return True
    return entity.split(":", 1)[0] in {GRID_PREFIX[p] for p in pubs}


def regrade(keys_doc=None):
    G = grader()
    with open(FIRST_RUN, encoding="utf-8") as f:
        run = {q["id"]: q for q in json.load(f)["questions"]}
    if keys_doc is None:
        with open(KEYS, encoding="utf-8") as f:
            keys_doc = json.load(f)
    keys = keys_doc["keys"]
    rows_out = []
    for q in load_yaml(QUESTIONS):
        qid, ans = q["id"], run[q["id"]]
        then = G.grade(q, ans)
        now_q = dict(q)
        k = keys.get(qid)
        if k:
            now_q["expected"] = k["expected"]
            if qid in ("b07", "d08") and k.get("month_name"):
                now_q["text"] = ([k["month"][:4]] if qid == "b07" else []) + [k["month_name"]]
        now = G.grade(now_q, ans)
        # what the grade would be if the three open rulings went the answers' way (informative only, nothing is ruled):
        # a battery revenue asked per kW accepted in the table's USD per MW; a figure of 1,000 or more accepted rounded
        # to the unit; a key accepting every table that holds the figure, and a refusal not graded on a table
        if_q = dict(now_q)
        if k and SPEC.get(qid, (None,) * 6)[5] == 1000:
            if_q["expected"] = [k["table_unit_value"]]
            if_q["tolerance"] = q["tolerance"] * 1000
        if any(abs(x) >= 1000 for x in if_q["expected"]):
            if_q["tolerance"] = max(if_q["tolerance"], 0.5)
        if qid == "g08" and keys_doc.get("extra", {}).get("g08_cost_of_power_rt_simple_mean") is not None and abs(keys_doc["extra"]["g08_cost_of_power_rt_simple_mean"] - k["expected"][0]) <= q["tolerance"]:
            if_q["tables"] = q["tables"] + [C]
        if q["refuse"]:
            if_q["tables"] = []
        if_ruled = G.grade(if_q, ans)
        # the key under the site's license hold on the day the keys were read: a held row is now a refusal ("license
        # needed"), as Ask's tools refuse it (site/lib/chat/tools.ts, session 215; the hold of 21 October)
        day = (keys_doc.get("computed_at_utc") or "")[:10]
        held = bool(k) and not q["refuse"] and any(held_row(k["table"], e.strip(), day) for e in k["entity"].split(" less "))
        held_q = dict(now_q, expected=[], text=["license needed"], tables=[], refuse=True) if held else now_q
        held_g = G.grade(held_q, ans)
        moved = [(a, b) for a, b in zip(q["expected"], now_q["expected"]) if abs(a - b) > q["tolerance"]]
        if q["text"] != now_q["text"]:
            moved.append((q["text"], now_q["text"]))
        cause = CAUSES.get(qid)
        rows_out.append({
            "id": qid, "stored_verdict": ans["verdict"], "then_ok": then["ok"], "now_ok": now["ok"],
            "expected_then": q["expected"], "expected_now": now_q["expected"], "moved": bool(moved),
            "grade_now": now, "ok_if_ruled": if_ruled["ok"], "held_since_21_october": held, "ok_under_hold": held_g["ok"], "cause": cause[0] if (cause and not now["ok"]) else None, "evidence": cause[1] if (cause and not now["ok"]) else None,
            "tool_calls": ans["tool_calls"], "retried": ans["retried"],
        })
    doc = {
        "_about": "Session 539: the 30 stored answers of eval_s320_first_run.json graded again, offline, with eval_s267.py's grader, against the keys of 19 October (questions_s320.yaml) and the keys as the live set holds them now (eval_s539_keys.json); each wrong answer's cause is one of four. No model call.",
        "keys_computed_at_utc": keys_doc.get("computed_at_utc"),
        "right_then": sum(r["then_ok"] for r in rows_out),
        "right_now": sum(r["now_ok"] for r in rows_out),
        "right_if_ruled": sum(r["ok_if_ruled"] for r in rows_out),
        "right_under_hold": sum(r["ok_under_hold"] for r in rows_out),
        "held": [r["id"] for r in rows_out if r["held_since_21_october"]],
        "moved": [r["id"] for r in rows_out if r["moved"]],
        "by_cause": {c: [r["id"] for r in rows_out if r["cause"] == c] for c in FOURS},
        "questions": rows_out,
    }
    return doc


def main(argv):
    keys_doc = build_keys() if "--keys" in argv else None
    doc = regrade(keys_doc)
    with open(REGRADE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    for r in doc["questions"]:
        print(r["id"], "right" if r["now_ok"] else "WRONG", "(then", "right)" if r["then_ok"] else "wrong)", "moved" if r["moved"] else "", r["expected_then"], r["expected_now"], r["cause"] or "")
    print(f"{doc['right_then']} of 30 right on the keys of 19 October; {doc['right_now']} of 30 on the keys now; moved: {', '.join(doc['moved']) or 'none'}; {doc['right_if_ruled']} of 30 if the three rulings went the answers' way")
    print(f"held since 21 October (the key is now a refusal): {', '.join(doc['held']) or 'none'}; {doc['right_under_hold']} of 30 right under the hold")
    for c, ids in doc["by_cause"].items():
        print(f"  {c}: {len(ids)} {' '.join(ids)}")
    unassigned = [r["id"] for r in doc["questions"] if not r["now_ok"] and r["cause"] is None]
    if unassigned:
        print("a wrong answer with no cause assigned:", unassigned)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
