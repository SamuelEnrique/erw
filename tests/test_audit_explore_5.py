"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 4).

/explore/demand-growth's decision "hours-used" ended "Nothing is filled." It reads the same table as /demand, whose
audit of tonight (docs/reviews/demand-model-audit-2026-11-26.md, finding 1) found that EIA's adjusted demand already
holds EIA's own estimates and that MISO's highest hour of 2025 is one. That audit's branch (wip/audit-demand-1) changes
/demand's words only; the explorer prints the same peak (?grid=miso&window=peak) under the same sentence. Words only.
The data test reads the table where it is held (warehouse/output, or a folder named by ERW_AUDIT_OUTPUT); the words
test runs everywhere.
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def table(name):
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, name + ".csv")):
            return os.path.join(d, name + ".csv")
    return None


class EiasEstimatesReachTheExplorer(unittest.TestCase):
    def test_the_explorer_reads_misos_2025_peak_from_the_table(self):
        path = table("eia930_demand_growth")
        if not path:
            self.skipTest("eia930_demand_growth is not held on this machine")
        got = {}
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(line for line in f if not line.startswith("#")):
                if r["entity"] == "eia930:MISO" and r["ts_utc"].startswith("2025"):
                    got[r["variable"]] = float(r["value"])
        self.assertEqual(got["peak_demand_mw"], 120343.0)
        self.assertEqual(f"{got['peak_demand_growth_since_2019_pct']:.2f}", "3.21")
        lib = src("site", "lib", "explore", "demandgrowth.ts")
        self.assertIn('mw: "peak_demand_mw"', lib)

    def test_the_decision_no_longer_says_nothing_is_filled_alone(self):
        d = src("site", "app", "explore", "demand-growth", "Decisions.tsx")
        self.assertNotIn("median hour. Nothing is filled.\"", d)
        self.assertIn("Nothing is filled here, but EIA's adjusted demand already holds EIA's own estimate for an hour an operator reported nothing for or reported implausibly, and such an hour is used as a reported one.", d)
        self.assertIn("From 2019 to 2025, 351 hours of the seven operators are EIA's estimates (ERCOT 24, CAISO 94, PJM 171, MISO 58, SPP 2, ISO-NE 2), among them MISO's highest hour of 2025, 120,343 MW on 24 July 2025, a day MISO reported nothing: on MISO's own reports its 2025 peak is 118,106 MW, +1.29 percent on 2019 against +3.21 here.", d)
        self.assertNotIn(chr(0x2014), d)


if __name__ == "__main__":
    unittest.main()
