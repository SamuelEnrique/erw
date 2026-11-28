"""Audit of /forecast, finding 1 (session 11402, docs/reviews/forecast-model-audit-2026-11-28.md): a place file whose
tomorrow is the ledger's first making (warehouse/predict/run.py from_ledger, done-line request 577) took the making's
values, band, method and hour from the ledger, but its horizon, the last hour of demand read and the fit day from the
build that wrote the file. On main's files (built 2026-11-27T14:39:36Z, made as at 18:00 UTC 26 November) all 29 places
whose tomorrow comes from the ledger say "2 days before the day forecast", from demand through 25 November, while the
ledger's making (11:00 UTC 26 November) read demand through 24 November at a horizon of 3 (4 for MIDW, NW and MISO);
the six price places likewise (1 against 2). The page prints both in the place's hover.

1. Against the page's own files (passes on main while its files are those audited; skipped once rebuilt): the values
   and bands of tomorrow equal the ledger's in every place, while the horizon and the last hour read differ in all 29.
2. The fix on this branch (fails on main): from_ledger carries the ledger's horizon and last hour read, so the file says
   what the forecast drawn was made from."""
import csv
import importlib.util
import json
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site", "data", "predict")
AUDITED = "2026-11-27T14:39:36Z"


def ledger_rows(name="ledger_demand.csv"):
    with open(os.path.join(SITE, name), encoding="utf-8") as f:
        lines = [x for x in f.read().splitlines() if x and not x.startswith("#")]
    return list(csv.DictReader(lines))


def load_run():
    spec = importlib.util.spec_from_file_location("predict_run_audit1", os.path.join(ROOT, "warehouse", "predict", "run.py"))
    run = importlib.util.module_from_spec(spec)   # its own name: other tests import modules named "run"
    spec.loader.exec_module(run)
    return run


class LedgerMakingLabels(unittest.TestCase):
    def test_main_files_mislabel_the_making(self):
        with open(os.path.join(SITE, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        if idx.get("built") != AUDITED:
            self.skipTest("the place files are not those audited (rebuilt since)")
        led = ledger_rows()
        by = {}
        for r in led:
            by.setdefault((r["place"], r["target_day"]), []).append(r)
        same_values, wrong_label = 0, 0
        for p in idx["places"]:
            with open(os.path.join(SITE, p["file"]), encoding="utf-8") as f:
                s = json.load(f)["series"]["demand"]
            if not s.get("tomorrow_from"):
                continue
            rows = by[(p["place"], s["target_day"])]
            tm = {r[0]: r[2] for r in s["tomorrow"]}
            if all(float(r["erw"]) == tm[r["ts_utc"]] for r in rows):
                same_values += 1
            if int(rows[0]["horizon_days"]) != s["horizon_days"] and rows[0]["inputs_through_utc"] != s["inputs_through_utc"]:
                wrong_label += 1
        self.assertEqual(same_values, 29)
        self.assertEqual(wrong_label, 29)

    def test_from_ledger_carries_the_makings_horizon_and_inputs(self):
        run = load_run()
        ts = pd.date_range("2026-11-27T06:00:00Z", periods=24, freq="h")
        tm = pd.DataFrame({"ts": ts, "hour": range(24), "regression_recent": 1.0, "regression_recent_lo": 0.9,
                           "regression_recent_hi": 1.1, "operator": float("nan")})
        p = {"place": "region-tex", "target": pd.Timestamp("2026-11-27"), "tomorrow": tm, "choice": "regression_recent",
             "h": 2, "inputs_through": pd.Timestamp("2026-11-26T05:00:00Z")}
        led = pd.DataFrame({"series": "demand", "place": "region-tex", "target_day": "2026-11-27",
                            "ts_utc": [t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in ts], "local_hour": range(24),
                            "made_utc": "2026-11-26T11:00:00Z", "inputs_through_utc": "2026-11-25T05:00:00Z",
                            "horizon_days": 3, "method": "regression", "erw": 2.0, "lo": 1.8, "hi": 2.2})
        q, made, m = run.from_ledger(p, led, "demand")
        self.assertEqual((made, m), ("2026-11-26T11:00:00Z", "regression"))
        self.assertEqual(q["h"], 3)
        self.assertEqual(run.iso(q["inputs_through"]), "2026-11-25T05:00:00Z")


if __name__ == "__main__":
    unittest.main()
