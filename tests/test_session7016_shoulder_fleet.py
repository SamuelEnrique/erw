"""Session 7016 (chain 301, done-line request 26): the shoulder table's fleet is the storage buildout's. shoulder_hours.py
is a monthly step of the data machine (dm_shoulder_hours), storage_buildout.py a step of the daily run, so the two can
drift apart for up to a month; this fails when a month both hold differs. On 16 November 2026: 380 of 380 equal, in
the tables and in the live set. It reads the tables where they are held (the data machine) and skips elsewhere. No
request, no model call."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
PAIRS = {"fleet_mw": "battery_operating_mw", "fleet_mwh": "battery_operating_mwh"}


def read(name, variables):
    out = {}
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if r["variable"] in variables and r["value"] not in ("", None):
                out[(r["entity"], r["variable"], r["ts_utc"][:7])] = float(r["value"])
    return out


class TheFleet(unittest.TestCase):
    def test_every_month_both_hold_is_the_same_fleet(self):
        names = ("shoulder_hours_monthly", "storage_buildout_monthly")
        if not all(os.path.exists(os.path.join(OUT, n + ".csv")) for n in names):
            self.skipTest("the tables are held on the data machine")
        sh = read(names[0], set(PAIRS))
        sb = read(names[1], set(PAIRS.values()))
        both, bad = 0, []
        for (entity, var, month), v in sh.items():
            k = (entity.replace("caiso_own", "caiso"), PAIRS[var], month)   # CAISO's own supply uses CAISO's fleet
            if k in sb:
                both += 1
                if abs(sb[k] - v) > 1e-6:
                    bad.append((entity, var, month, v, sb[k]))
        self.assertGreater(both, 0)
        self.assertEqual(bad, [], f"{len(bad)} of {both} months differ; rebuild shoulder_hours_monthly after storage_buildout_monthly")


if __name__ == "__main__":
    unittest.main()
