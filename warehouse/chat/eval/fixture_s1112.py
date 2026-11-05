"""Session 1112 (chain 075): the saved rows behind session 320's four questions on held grids (g07, g08, d05, d07), for a
test with no model and no database (site/scripts/test-ask-1112.mjs, tests/test_session1112.py).

Energy Research Warehouse (ERW). Reads this machine's warehouse/output/merchant_revenue_monthly.csv and
cost_of_power_monthly.csv and writes tests/fixtures/session1112/held_reads.json: the two tables' catalogue rows and,
for each question, the rows of its variable in its month for every hub the table holds, the held grids' (ISO-NE, NYISO,
MISO) included, so the test can prove that none of them leaves the tool. Every value is the table's, untouched.

    python warehouse/chat/eval/fixture_s1112.py
"""
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "tests", "fixtures", "session1112", "held_reads.json")

# id: (table, held entity, variable, month) as session 539's keys name them (eval_s539_keys.json)
QUESTIONS = {
    "g07": ("merchant_revenue_monthly", "isone:.H.INTERNAL_HUB", "solar_capture_price", "2026-08"),
    "g08": ("merchant_revenue_monthly", "nyiso:N.Y.C.", "flat_price", "2026-07"),
    "d05": ("cost_of_power_monthly", "nyiso:N.Y.C.", "rt_load_weighted", "2026-01"),
    "d07": ("cost_of_power_monthly", "isone:.H.INTERNAL_HUB", "da_shape_premium", "2026-06"),
}


def read(table):
    path = os.path.join(ROOT, "warehouse", "output", f"{table}.csv")
    with open(path, encoding="utf-8") as f:
        head = []
        for line in f:
            if not line.startswith("#"):
                break
            head.append(line.rstrip("\n"))
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    return head, rows


def build():
    tables, rows, questions = {}, [], {}
    for qid, (table, held, variable, month) in QUESTIONS.items():
        if table not in tables:
            tables[table] = read(table)
        head, all_rows = tables[table]
        sel = [r for r in all_rows if r["variable"] == variable and r["ts_utc"].startswith(month)]
        questions[qid] = {"table": table, "entity": held, "variable": variable, "start": f"{month}-01",
                          "end": (dt.date.fromisoformat(f"{month}-01").replace(day=28) + dt.timedelta(days=4)).replace(day=1).isoformat(),
                          "public": {r["entity"]: float(r["value"]) for r in sel if not r["entity"].startswith(("isone:", "nyiso:", "miso:"))}}
        for r in sel:
            rows.append({"table_name": table, "entity": r["entity"], "variable": r["variable"],
                         "ts_utc": r["ts_utc"].replace("Z", "+00:00"), "value": float(r["value"]), "unit": r["unit"]})
    catalogue = []
    for table, (head, all_rows) in tables.items():
        times = [r["ts_utc"] for r in all_rows]
        catalogue.append({"table_name": table, "iso": "CAISO;ERCOT;ISO-NE;MISO;NYISO;SPP", "market": None, "n_nodes": 1,
                          "interval": "P1M", "ts_min": min(times).replace("Z", "+00:00"), "ts_max": max(times).replace("Z", "+00:00"),
                          "n_rows": len(all_rows), "source_report": f"erw:{table.replace('_monthly', '')}", "last_run": None,
                          "validator_status": "pass", "license": "public", "sector": "power", "derived": "yes", "in_live_set": "yes",
                          "columns": json.dumps(list(all_rows[0].keys())), "tier": "derived"})
    return {"_about": "Session 1112: the rows behind session 320's four held-grid questions, every hub of the month, copied "
                      "untouched from this machine's warehouse/output CSVs by warehouse/chat/eval/fixture_s1112.py.",
            "recorded_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "table_headers": {t: [h for h in head if h.startswith(("# Retrieved", "# Source"))] for t, (head, _) in tables.items()},
            "questions": questions, "catalogue": catalogue, "rows": rows}


def main():
    fix = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(fix, f, indent=1)
        f.write("\n")
    for qid, q in fix["questions"].items():
        print(qid, q["table"], q["variable"], q["start"], q["end"], q["public"])
    print("wrote", os.path.relpath(OUT, ROOT), len(fix["rows"]), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
