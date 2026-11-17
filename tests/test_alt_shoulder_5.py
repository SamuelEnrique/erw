"""Ruling alternative 5 of /shoulder (session 7703, 17 November 2026, branch wip/alt-shoulder-5; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-shoulder-2026-11-17.md, line 5): the fleet,
EIA-860M's count or the market monitors' larger counts? On this branch, for December 2025 (the one month the monitors
count), warehouse/derived/shoulder_hours.py fleet_for gives the monitor's count (MONITOR_FLEET: Potomac Economics, more
than 17,000 MW and 31,500 MWh for ERCOT; CAISO's Department of Market Monitoring, over 17 GW for California, no MWh), and
the month carries fleet_from_monitor, which the page names on hover.

Pinned with the builder's own functions on the table's December 2025 shoulders, where shoulder_hours_monthly is on the
machine (warehouse/output, or the folder ERW_TABLES_DIR names), and with the page drawn on the table with those rows put
in its place (site/scripts/alt-shoulder-draw.mjs): ERCOT hours needed 2.43 to 1.99 (-18.2 percent), fleet hours 1.55 to
1.85 (+19.4 percent); California by CAISO's own data, hours needed 2.87 to 2.66 (-7.3 percent), fleet hours not given.

    python -m unittest tests.test_alt_shoulder_5 -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import shoulder_hours as sh  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "shoulder_hours_monthly.csv")
FLEET_VARS = ("fleet_mw", "fleet_mwh", "fleet_hours", "shoulder_hours_covered", "shoulder_hours_needed", "shoulder2_hours_covered", "shoulder2_hours_needed", "fleet_from_monitor")


class TheRule(unittest.TestCase):
    def test_the_monitor_stands_for_december_2025_only(self):
        fl = pd.DataFrame({"battery_operating_mw": [13909.3, 14000.0], "battery_operating_mwh": [21578.8, 22000.0]}, index=["2025-12", "2026-01"])
        self.assertEqual(sh.fleet_for("ercot", "2025-12", fl), (17000.0, 31500.0, True))
        self.assertEqual(sh.fleet_for("ercot", "2026-01", fl), (14000.0, 22000.0, False))
        self.assertEqual(sh.fleet_for("caiso", "2025-12", fl), (17000.0, None, True))

    def test_mw_alone_gives_hours_needed_only_for_a_monitor(self):
        self.assertEqual(sh.fleet_metrics(8.0, 45185.6953, 17000.0, None), {})                                      # main's rule for a month with no MWh
        got = sh.fleet_metrics(8.0, 45185.6953, 17000.0, None, 7.0, 16830.7545, mw_only=True)
        self.assertEqual(set(got), {"fleet_mw", "shoulder_hours_needed", "shoulder2_hours_needed"})
        self.assertEqual(round(got["shoulder_hours_needed"], 2), 2.66)


def table():
    n = 0
    with open(CSV, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(CSV, skiprows=n, dtype=str, keep_default_na=False)


@unittest.skipUnless(os.path.exists(CSV), "shoulder_hours_monthly is not on this machine")
class OnTheTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        t = table()
        cls.t = t
        val = lambda e, v: float(t[(t["entity"] == e) & (t["variable"] == v) & (t["ts_utc"] == "2025-12-01T00:00:00Z")]["value"].iloc[0])
        cls.new = {}
        for entity, grid in (("iso:ercot", "ercot"), ("iso:caiso_own", "caiso")):
            mw, mwh, monitor = sh.fleet_for(grid, "2025-12", pd.DataFrame())
            f = sh.fleet_metrics(val(entity, "shoulder_hours"), val(entity, "shoulder_mwh_above_mean"), mw, mwh, val(entity, "shoulder2_hours"),
                                 val(entity, "shoulder2_mwh_above_midpoint"), mw_only=monitor)
            f["fleet_from_monitor"] = 1
            cls.new[entity] = f

    def test_the_builder_figures(self):
        e, c = self.new["iso:ercot"], self.new["iso:caiso_own"]
        self.assertEqual((round(e["shoulder_hours_needed"], 2), round(e["fleet_hours"], 2), round(e["shoulder_hours_covered"], 2)), (1.99, 1.85, 1.85))
        self.assertEqual(round(c["shoulder_hours_needed"], 2), 2.66)
        self.assertNotIn("fleet_hours", c)

    def test_the_page_drawn_with_the_months_new_rows(self):
        t = self.t
        dec = (t["ts_utc"] == "2025-12-01T00:00:00Z") & t["entity"].isin(list(self.new)) & t["variable"].isin(FLEET_VARS)
        keep = t[~dec]
        add = []
        for entity, f in self.new.items():
            base = t[(t["entity"] == entity) & (t["ts_utc"] == "2025-12-01T00:00:00Z")].iloc[0].to_dict()
            for k, v in f.items():
                add.append(dict(base, variable=k, value=str(round(float(v), 4))))
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "shoulder_hours_monthly.csv")
            pd.concat([keep, pd.DataFrame(add)], ignore_index=True).to_csv(path, index=False)
            p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-shoulder-draw.mjs", path,
                                json.dumps([{"grid": "ercot", "month": "2025-12"}, {"grid": "caiso-own", "month": "2025-12"}])], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        e, c = json.loads(p.stdout)
        self.assertIn("its batteries could run 1.85 hours at full power", e["summary"])
        self.assertIn("they would need 1.99 hours on the average day", e["summary"])
        self.assertIn("monitor-fleet=iso:ercot", e["marks"])
        self.assertIn("Hours the battery fleet covers 1.85 hours 17,000 MW", e["text"])
        self.assertIn("holding 31,500 MWh. At that power, all of the shoulder's MWh above the mean would take 1.99 hours", e["text"])
        self.assertIn("they would need 2.66 hours on the average day", c["summary"])
        self.assertIn("monitor-fleet=iso:caiso_own", c["marks"])
        self.assertIn("the monitor gives no MWh, so no hours covered", c["text"])


if __name__ == "__main__":
    unittest.main()
