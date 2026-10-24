"""Session 1411 (chain 107): the older blocks of the Grid tool on a failed read.

Session 1181's list of older blocks that said "not held", "not in the warehouse yet", "none" or nothing when their read
failed (YourGrid's battery cycle and units, the price board, the carbon intensity, the station's temperatures in
"Yesterday", CAISO's daily series, the table citations and the Flex Alert scorecard's notices column) now each say
"could not be read". site/scripts/test-grid-failed-reads.mjs holds them (tests/test_session1181.py runs it); this file
holds that its cases, its fixture and the failure branches are there.

    python -m unittest tests.test_session1411 -v
"""

import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCases(unittest.TestCase):
    def test_the_node_test_holds_each_older_block(self):
        t = src("site", "scripts", "test-grid-failed-reads.mjs")
        for w in ("older_Batteries (1411), storage_daily_cycle", "older_Batteries (1411), storage_capacity",
                  "older_What it costs (1411), price_board_latest", "older_What it costs (1411), price_board_peak_offpeak",
                  "older_How clean (1411), carbon_intensity_hourly", "older_How clean (1411), carbon_intensity_monthly",
                  "older_ERCOT: yesterday (1411), weather_obs_hourly", "older_Reliability (1411), caiso_reliability_daily",
                  "the table citations (1411), catalogue", "the Flex Alert scorecard's notices column (1411), caiso_grid_emergencies",
                  'fx("grid_older_reads.json")', "let withCatalogue = false;"):
            self.assertIn(w, t, w)

    def test_the_fixture_holds_real_rows_of_each_table(self):
        import json
        f = json.loads(src("site", "scripts", "fixtures", "grid_older_reads.json"))
        self.assertIn("anon key", f["_note"])
        for table in ("storage_daily_cycle", "price_board_latest", "price_board_peak_offpeak", "carbon_intensity_monthly",
                      "weather_obs_hourly", "caiso_reliability_daily", "flex_alert_effects", "flex_alert_model"):
            self.assertTrue(f["rows"][table], table)
        self.assertGreater(len(f["catalogue"]), 100)


class TheBranches(unittest.TestCase):
    def test_each_block_says_could_not_be_read(self):
        y = src("site", "components", "grid", "YourGrid.tsx")
        for w in (") : d.errors.cycle ? (", ") : d.errors.units ? (", "if (!last && d.errors.ci) return <Unread", ") : d.errors.monthly ? (",
                  "if (g.hub && !d.prices.length && d.errors.prices) return <Unread", "const peakN = (r?: SeriesRow) => (d.errors.peak && !r ?"):
            self.assertIn(w, y, w)
        self.assertIn("data-yesterday-unread={WX}", src("site", "components", "grid", "Conditions.tsx"))
        r = src("site", "components", "grid", "Reliability.tsx")
        self.assertIn('data-reliability-daily-unread="peaks"', r)
        self.assertIn("function RowUnread(", r)
        self.assertIn('wholeSeriesRead(DAILY, "every Pacific day since 2018"', r)
        self.assertIn('data-cite-unread="catalogue"', src("site", "components", "Cite.tsx"))
        self.assertIn("data-alerts-unread={EMERGENCIES}", src("site", "app", "grid", "caiso", "alerts", "page.tsx"))

    def test_the_method_note_says_it(self):
        m = src("docs", "methods", "grid_network.md")
        self.assertIn("## The older blocks when a read fails (chain 107, 24 October 2026)", m)
        self.assertIn("Decisions (chain 107, session 1411):", m)

    def test_no_em_dash(self):
        for parts in [("site", "scripts", "test-grid-failed-reads.mjs"), ("site", "scripts", "fixtures", "grid_older_reads.json"),
                      ("site", "scripts", "same-figures.mjs"), ("site", "components", "grid", "YourGrid.tsx"),
                      ("site", "components", "grid", "Conditions.tsx"), ("site", "components", "grid", "Reliability.tsx"),
                      ("site", "components", "Cite.tsx"), ("site", "app", "grid", "caiso", "alerts", "page.tsx"),
                      ("site", "lib", "gridReads.ts"), ("docs", "methods", "grid_network.md"), ("tests", "test_session1411.py")]:
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
