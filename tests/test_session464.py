"""Session 464: the battery page calibrated against Modo Energy's ERCOT 2025 figures.

Energy Research Warehouse (ERW). docs/methods/battery_earns_algorithm.md gains two rows in its "Cross-checks" table
(Modo's 2025 nowcast set beside the 2-hour battery on the day-ahead schedule; Modo's June share of energy arbitrage)
and a section "Modo Energy's ERCOT 2025 figures, reconciled". The page's "Checked against" count follows the table
(15 to 17). No figure the page shows moves. The arithmetic of the rows is recomputed from battery_stack_monthly
where this machine holds it (skipped where it does not, as on GitHub's check).
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTE = os.path.join(ROOT, "docs", "methods", "battery_earns_algorithm.md")
PAGE = os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "page.tsx")
STACK = os.path.join(os.environ.get("ERW_OUTPUT_DIR") or os.path.join(ROOT, "warehouse", "output"), "battery_stack_monthly.csv")
HOW = "https://modoenergy.com/research/en/how-does-battery-energy-storage-make-money"
WHY = "https://modoenergy.com/research/en/why-were-ercot-battery-revenues-so-low-in-2025-weather-energy-arbitrage-builodout"


def src(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def table_rows(note):
    lines = note.split("\n")
    i = lines.index("## Cross-checks")
    while not lines[i].startswith("| Our figure"):
        i += 1
    rows = []
    for line in lines[i + 2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split(" | ")])
    return rows


class TheRows(unittest.TestCase):
    def setUp(self):
        self.note = src(NOTE)
        self.rows = table_rows(self.note)

    def test_the_table_has_the_rows_the_page_counts(self):
        n = int(re.search(r'data-checked-against="(\d+)"', src(PAGE)).group(1))
        self.assertEqual(n, 17)
        self.assertEqual(len(self.rows), n)
        self.assertIn('Checked against: 17 published figures (', src(PAGE))

    def test_every_row_has_five_cells_and_a_reason(self):
        for r in self.rows:
            self.assertEqual(len(r), 5, r[0][:60])
            self.assertTrue(all(c for c in r), r[0][:60])
            self.assertGreater(len(r[4]), 30, r[0][:60])

    def test_the_two_new_rows_quote_modo_with_its_address_and_date(self):
        a, b = self.rows[-2], self.rows[-1]
        self.assertIn("2-hour", a[0]); self.assertIn("USD 56.01 per kW", a[0]); self.assertIn("$29.4/kW", a[1])
        self.assertIn(WHY, a[2]); self.assertIn("read 12 October 2026", a[2]); self.assertIn("+26.61", a[3])
        self.assertIn("46.8 percent", b[0]); self.assertIn("76% of revenue from energy arbitrage in June 2025", b[1])
        self.assertIn(HOW, b[2]); self.assertIn("19 May 2026", b[2]); self.assertIn("read 21 October 2026", b[2])
        self.assertIn("-29.2 points", b[3])

    def test_the_rows_that_were_there_are_unchanged_in_order(self):
        firsts = [r[0][:40] for r in self.rows[:15]]
        self.assertTrue(firsts[0].startswith("CAISO, 100 MW, 4-hour, at SP15"))
        self.assertTrue(self.rows[14][0] == "the same" and "Potomac" in self.rows[14][2])

    def test_the_section_says_no_figure_moves_and_what_was_read(self):
        i = self.note.index("### Modo Energy's ERCOT 2025 figures, reconciled (session 464)")
        sec = self.note[i:]
        self.assertIn("No figure on the page moves", sec)
        self.assertIn("series|price_years_by_window|ercot:HB_HUBAVG|battery_dayahead_2h_year_2025|2025-01-01T00:00:00Z", sec)
        self.assertIn("Three requests of the four allowed", sec)
        self.assertIn('<a id="modo-2025"></a>', self.note)

    def test_no_dash(self):
        for p in (NOTE, PAGE, __file__):
            self.assertNotRegex(src(p), "[\u2013\u2014]", p)


@unittest.skipUnless(os.path.exists(STACK), "battery_stack_monthly is not on this machine")
class TheArithmetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pandas as pd
        d = pd.read_csv(STACK, comment="#")
        cls.e = d[d.entity == "ercot:HB_HUBAVG"]

    def total(self, var, prefix):
        e = self.e
        return e[(e.variable == var) & (e.ts_utc.str.startswith(prefix))].value.sum()

    def test_the_2_hour_year_and_its_parts(self):
        t = self.total("dayahead_2h_revenue_total_usd_per_mw", "2025") / 1000
        en = self.total("dayahead_2h_revenue_energy_usd_per_mw", "2025") / 1000
        an = self.total("dayahead_2h_revenue_ancillary_usd_per_mw", "2025") / 1000
        f = self.total("foresight_2h_revenue_total_usd_per_mw", "2025") / 1000
        self.assertAlmostEqual(t, 56.01, places=2)
        self.assertAlmostEqual(en, 29.94, places=2)
        self.assertAlmostEqual(an, 26.07, places=2)
        self.assertAlmostEqual(f, 64.41, places=2)
        self.assertAlmostEqual(round(t, 2) - 29.4, 26.61, places=2)

    def test_the_june_shares(self):
        want = {(2, "2025-06"): 46.8, (2, "2024-06"): 27.4, (4, "2025-06"): 66.6, (4, "2024-06"): 23.2, (8, "2025-06"): 76.1, (8, "2024-06"): 41.0}
        for (h, m), share in want.items():
            en = self.total(f"dayahead_{h}h_revenue_energy_usd_per_mw", m)
            t = self.total(f"dayahead_{h}h_revenue_total_usd_per_mw", m)
            self.assertAlmostEqual(round(100 * en / t, 1), share, places=1, msg=f"{h}h {m}")


if __name__ == "__main__":
    unittest.main()
