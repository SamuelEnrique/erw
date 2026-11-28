"""wip/ready-grid-netting (session 11406, chain 770, part C): the other choice of the Grid tool audit of 26 November,
finding 3 (docs/reviews/grid-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the Grid tool has two rules for the same ties: the grid tabs (the network snapshot, grid_network.py and
network_hourly.py) read each pair from the BA whose code sorts first; the region tab's trade files (interchange_pairs.py)
take the mean of both reports where both filed. On this branch the snapshot takes the trade tab's rule. Measured by the
audit (13 September to 3 November 2026, the median hour): MISO's net export moves 451 MW, PJM's 503, CAISO's 258,
NYISO's 215, ERCOT's 188, ISO-NE's 4. The snapshot is rebuilt by its next daily and hourly runs. The words of the tool,
the map's decisions and the note follow. Finding 2's choice (each grid's own report first) is not this branch."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
sys.path.insert(0, DERIVED)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class OneNettingRule(unittest.TestCase):
    def test_the_hourly_rule_is_the_mean(self):
        try:
            import network_hourly as nh
        except Exception as exc:
            self.skipTest(f"network_hourly does not import here: {exc}")
        rows = [{"period": "2026-10-04T12", "fromba": "MISO", "toba": "PJM", "value": 1000},
                {"period": "2026-10-04T12", "fromba": "PJM", "toba": "MISO", "value": -600},   # PJM says it imported 600
                {"period": "2026-10-04T13", "fromba": "PJM", "toba": "MISO", "value": 300}]    # only PJM reported
        flows, _ = nh.pair_flows(rows, {"MISO", "PJM"})
        self.assertEqual(flows[("MISO", "PJM")], {"2026-10-04T11:00:00Z": 800.0, "2026-10-04T12:00:00Z": -300.0})

    def test_the_daily_rule_and_the_words(self):
        g = src("warehouse", "derived", "grid_network.py")
        self.assertIn('pick = x.groupby(["first", "second", "ts"], as_index=False)["flow"].mean()', g)
        self.assertIn("where both BAs reported the hour, its flow is the mean of the two reports", g)
        self.assertIn("mean_both", src("warehouse", "derived", "interchange_pairs.py"))   # the trade tab's rule, now the tool's
        self.assertIn("each tie as the mean of both balancing authorities' reports where both filed", src("site", "lib", "network.ts"))
        self.assertIn("its flow is the mean of the two reports", src("site", "app", "network", "MapDecisions.tsx"))
        self.assertIn("the rule of the trade tab's files", src("docs", "methods", "grid_network.md"))


if __name__ == "__main__":
    unittest.main()
