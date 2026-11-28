"""Session 11408 (chain 770, part C): /demand, the other choice of the demand audit's finding 7
(docs/reviews/demand-model-audit-2026-11-26.md; its test branch wip/audit-demand-8, carried over here and turned to the
new rule). Not for landing until the owner rules.

The rule on this branch: beside growth since 2019, each whole year after 2019 carries its average's and peak's growth
on 2018 (avg_demand_growth_since_2018_pct, peak_demand_growth_since_2018_pct), and the summary says the newest whole
year's average against 2018. Measured by running the builder on this machine's EIA workbooks of 4 October 2026 (written
only into the worktree): 2025's average on 2018 against on 2019, ERCOT +29.54 and +27.22, SPP +9.62 and +11.14, Lower
48 +6.04 and +7.03, PJM +2.66 and +5.37, CAISO -0.74 and +4.45, MISO -0.63 and +2.20, NYISO -5.92 and -2.73, ISO-NE
-6.51 and -2.54; no figure of origin/main moves (90 figures added). The site file is rebuilt at landing by the desk.

1. warehouse/derived/demand_growth.py summarize on a small series: the second base's growth, and none for a year after
   2019 when 2018 is not whole.
2. The page's sentence and check-demand's key.
3. Once the site file is rebuilt, CAISO's and MISO's 2025 sit below 2018 (the audit's measure, turned)."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def series(values_by_year):
    import pandas as pd
    parts = []
    for y, v in values_by_year.items():
        idx = pd.date_range(f"{y}-01-01T00:00:00Z", f"{y}-12-31T23:00:00Z", freq="h")
        parts.append(pd.Series(float(v), index=idx))
    return pd.concat(parts)


class ASecondBase(unittest.TestCase):
    def test_growth_on_2018_beside_2019(self):
        import demand_growth as dg
        self.assertEqual((dg.BASE, dg.SECOND_BASE), (2019, 2018))
        out, _, _ = dg.summarize(series({2018: 100, 2019: 110, 2020: 121, 2021: 121}), "UTC")
        self.assertEqual(out[2020]["avg_demand_growth_since_2019_pct"], 10.0)
        self.assertEqual(out[2020]["avg_demand_growth_since_2018_pct"], 21.0)
        self.assertEqual(out[2020]["peak_demand_growth_since_2018_pct"], 21.0)
        self.assertNotIn(2018, out)                        # nothing else of 2018 is written

    def test_no_second_base_when_2018_is_not_whole(self):
        import demand_growth as dg
        s = series({2018: 100, 2019: 110, 2020: 121, 2021: 121})
        s = s[s.index >= "2018-03-01"]
        out, _, _ = dg.summarize(s, "UTC")
        self.assertNotIn("avg_demand_growth_since_2018_pct", out[2020])

    def test_the_page_and_the_check(self):
        with open(os.path.join(ROOT, "site", "app", "demand", "page.tsx"), encoding="utf-8") as f:
            page = f.read()
        self.assertIn('k="sum|avg_growth_2018"', page)
        self.assertIn("Against 2018, also a whole year in EIA&apos;s file", page)
        with open(os.path.join(ROOT, "site", "scripts", "check-demand.mjs"), encoding="utf-8") as f:
            self.assertIn('maybe("sum|avg_growth_2018", last.row.avg_demand_growth_since_2018_pct, g.signed);', f.read())

    def test_the_site_file_once_rebuilt(self):
        with open(os.path.join(ROOT, "site", "data", "demand_growth.json"), encoding="utf-8") as f:
            site = json.load(f)
        y = site["areas"]["CISO"]["years"]["2025"]
        if "avg_demand_growth_since_2018_pct" not in y:
            self.skipTest("the site file is rebuilt at landing by the desk")
        self.assertLess(y["avg_demand_growth_since_2018_pct"], 0)
        self.assertLess(site["areas"]["MISO"]["years"]["2025"]["avg_demand_growth_since_2018_pct"], 0)


if __name__ == "__main__":
    unittest.main()
