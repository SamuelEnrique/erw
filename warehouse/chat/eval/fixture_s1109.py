"""Session 1109 (chain 075): the saved rows behind session 320's eight per-kW questions, for a test with no model and no
database (tests/test_session1109.py, site/scripts/test-ask-1109.mjs).

Energy Research Warehouse (ERW). Reads the local warehouse/output/battery_stack_monthly.csv (the table as this machine
holds it; its own header names the run) and writes tests/fixtures/session1109/battery_reads.json: the catalogue row of
the table and, for each of b01 to b06, b08 and b09, the monthly rows of the one variable its question asks over the months
it names. Every value is the table's, untouched. Each question's per-MW sum and its key (session 539's keys of
21 October, eval_s539_keys.json; questions_s320.yaml where 539 kept it) are written beside it, so a reader sees whether
the rows agree with the key.

    python warehouse/chat/eval/fixture_s1109.py            # writes the fixture
    python warehouse/chat/eval/fixture_s1109.py --check    # prints the agreement, writes nothing
"""
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TABLE = os.path.join(ROOT, "warehouse", "output", "battery_stack_monthly.csv")
OUT = os.path.join(ROOT, "tests", "fixtures", "session1109", "battery_reads.json")

# id: (entity, variable, start, end) as the question names them (questions_s320.yaml)
QUESTIONS = {
    "b01": ("ercot:HB_HUBAVG", "foresight_4h_revenue_total_usd_per_mw", "2025-10-01", "2026-10-01"),
    "b02": ("ercot:HB_HUBAVG", "foresight_4h_revenue_energy_usd_per_mw", "2025-10-01", "2026-10-01"),
    "b03": ("ercot:HB_HUBAVG", "foresight_4h_revenue_ancillary_usd_per_mw", "2025-10-01", "2026-10-01"),
    "b04": ("ercot:HB_HUBAVG", "dayahead_2h_revenue_total_usd_per_mw", "2025-10-01", "2026-10-01"),
    "b05": ("ercot:HB_HUBAVG", "foresight_4h_revenue_total_usd_per_mw", "2021-01-01", "2022-01-01"),
    "b06": ("ercot:HB_HUBAVG", "foresight_4h_revenue_total_usd_per_mw", "2025-01-01", "2026-01-01"),
    "b08": ("caiso:TH_SP15_GEN-APND", "foresight_4h_revenue_total_usd_per_mw", "2025-10-01", "2026-10-01"),
    "b09": ("caiso:TH_SP15_GEN-APND", "dayahead_4h_revenue_energy_usd_per_mw", "2025-01-01", "2026-01-01"),
}


def header():
    lines = []
    with open(TABLE, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            lines.append(line.rstrip("\n"))
    return lines


def rows():
    with open(TABLE, encoding="utf-8") as f:
        body = (line for line in f if not line.startswith("#"))
        return list(csv.DictReader(body))


def keys():
    with open(os.path.join(HERE, "eval_s539_keys.json"), encoding="utf-8") as f:
        k = json.load(f)["keys"]
    return {q: (v["expected"] if isinstance(v, dict) else v) for q, v in k.items()} if isinstance(k, dict) else {
        v["id"]: v["expected"] for v in k}


def build():
    all_rows = rows()
    key = keys()
    picked, questions = [], {}
    for qid, (entity, variable, start, end) in QUESTIONS.items():
        sel = [r for r in all_rows if r["entity"] == entity and r["variable"] == variable and start <= r["ts_utc"][:10] < end]
        sel.sort(key=lambda r: r["ts_utc"])
        total = round(sum(float(r["value"]) for r in sel), 6)
        k = key.get(qid)
        k = k[0] if isinstance(k, list) else k
        questions[qid] = {"entity": entity, "variable": variable, "start": start, "end": end, "months": len(sel),
                          "sum_usd_per_mw": total, "key_usd_per_kw": k,
                          "agrees": k is not None and abs(total / 1000 - float(k)) <= 0.01}
        for r in sel:
            picked.append({"table_name": "battery_stack_monthly", "entity": r["entity"], "variable": r["variable"],
                           "ts_utc": r["ts_utc"].replace("Z", "+00:00"), "value": float(r["value"]), "unit": r["unit"]})
    seen, uniq = set(), []
    for r in picked:
        k = (r["entity"], r["variable"], r["ts_utc"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    head = header()
    times = [r["ts_utc"] for r in all_rows]
    catalogue = [{"table_name": "battery_stack_monthly", "iso": "CAISO;ERCOT", "market": "caiso;ercot", "n_nodes": 2,
                  "interval": "P1M", "ts_min": min(times).replace("Z", "+00:00"), "ts_max": max(times).replace("Z", "+00:00"),
                  "n_rows": len(all_rows), "source_report": "erw:battery_stack", "last_run": None, "validator_status": "pass",
                  "license": "public", "sector": "power", "derived": "yes", "in_live_set": "yes",
                  "columns": json.dumps(list(all_rows[0].keys())), "tier": "derived"}]
    return {"_about": "Session 1109: the monthly rows of battery_stack_monthly behind session 320's eight per-kW questions, "
                      "copied untouched from this machine's warehouse/output/battery_stack_monthly.csv by "
                      "warehouse/chat/eval/fixture_s1109.py; the table's own header lines are under table_header.",
            "recorded_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "table_header": head[:1] + [h for h in head if h.startswith(("# Retrieved", "# Source", "# Run log"))],
            "questions": questions, "catalogue": catalogue, "rows": uniq}


def main(argv):
    fix = build()
    for qid, q in fix["questions"].items():
        print(qid, q["months"], q["sum_usd_per_mw"], q["key_usd_per_kw"], "agrees" if q["agrees"] else "DIFFERS")
    if "--check" in argv:
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(fix, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(OUT, ROOT), len(fix["rows"]), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
