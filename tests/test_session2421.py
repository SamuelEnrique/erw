"""Session 2421: Statistics Botswana's Electricity Generation and Distribution Stats Brief, Botswana's generation, imports
and distribution a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/statsbots_botswana.py's reader on text built here in the
form pdfplumber gives the brief (figures made up for the test, not the bureau's): the table of contents passed over,
months checked against their quarters and years, distribution against generation plus imports, a distribution month
printed as its generation left out (and the printed totals checked with the sound figure), the quarter by source as
P3M rows; a month not adding to its quarter, a distribution off in any other way and a value that is not a number
stopping the run; the newest brief found on the home page; the sector rule and the live-set hold. No network, no PDF.

    python -m unittest tests.test_session2421 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statsbots_botswana as S  # noqa: E402
import build_coverage as B  # noqa: E402

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def table(n, title, a, b, a_total=None):
    """Two years, the second to February only: a and b give each month's value of the first and the second year."""
    lines = [f"Table {n}: {title} (MWH): January 2025 - February 2026", "Period 2025 2026*"]
    for k, name in enumerate(MONTHS):
        lines.append(f"{name} {a[k]:,}" + (f" {b[k]:,}" if k < len(b) else ""))
    q = [sum(a[3 * i:3 * i + 3]) for i in range(4)]
    lines += [f"Q{i + 1} {q[i]:,}" for i in range(4)]
    lines += [f"TOTAL {a_total or sum(a):,} {sum(b):,}", "Note:", "1. 2026* Data is up to the second quarter only"]
    return lines


def text(feb_dist=None, jan_gen=10, gen_q2="Coal 25.0 83.3", dist_feb_total=None):
    gen_a = [jan_gen] + [10] * 11
    imp_a = [5] * 12
    gen_b, imp_b = [20, 30], [4, 6]
    dist_a = [g + i for g, i in zip(gen_a, imp_a)]
    dist_b = [24, feb_dist if feb_dist is not None else 36]
    t11 = table(11, "Physical Volume of Electricity Distribution", dist_a, dist_b)
    if dist_feb_total:  # the printed year total as the bureau printed it, not the sum of its months
        t11 = [l if not l.startswith("TOTAL") else f"TOTAL {sum(dist_a):,} {dist_feb_total:,}" for l in t11]
    return "\n" + "\n".join(
        ["Table 3: Physical Volume of Electricity Generation MWH: January 2025 - February 2026 ........ 12",
         "Table 2: Electricity Generation by Source in MWH: First Quarter 2025",
         "Source MWH %", gen_q2, "Solar 5.0 16.7", "Diesel 0.0 0.0", "Total 30.0 100.0"]
        + table(3, "Physical Volume of Electricity Generation", gen_a, gen_b)
        + table(7, "Physical Volume of Imported Electricity", imp_a, imp_b)
        + ["Table 10: Imported Electricity by Source in MWH: First Quarter 2025", "Source MWH %",
           "Eskom (SA) 10.0 66.7", "SAPP Markets (SADC) 3.0 20.0", "Cross Border 2.0 13.3", "Total 15.0 100.0"]
        + t11)


class Rows(unittest.TestCase):
    def test_rows(self):
        rows, left = S.parse(text())
        got = {(v, y, m): (x, f) for v, y, m, x, f in rows}
        self.assertEqual(got[("generation", 2026, 2)], (30.0, "P1M"))
        self.assertEqual(got[("distribution", 2025, 12)], (15.0, "P1M"))
        self.assertEqual(got[("generation_coal", 2025, 1)], (25.0, "P3M"))
        self.assertEqual(got[("imports_cross_border", 2025, 1)], (2.0, "P3M"))
        self.assertNotIn(("generation", 2026, 3), got)
        self.assertEqual(left, [])

    def test_distribution_printed_as_generation(self):
        rows, left = S.parse(text(feb_dist=30, dist_feb_total=60))
        self.assertEqual(left, [(2026, 2, 30.0, 36.0)])
        self.assertNotIn(("distribution", 2026, 2), {(v, y, m) for v, y, m, *_ in rows})

    def test_stops(self):
        for t in (text(feb_dist=31), text(feb_dist=30, dist_feb_total=54), text(gen_q2="Coal 28.0 83.3"),
                  text().replace("January 10 20", "January x 20"),
                  text().replace("TOTAL 120 50", "TOTAL 125 50")):
            with self.assertRaises(RuntimeError):
                S.parse(t)

    def test_brief_on_home_page(self):
        home = '<a href="https://www.statsbots.org.bw/sites/default/files/Electricity%20Generation%20and%20Distribution%20Stats%20Brief%2C%20Second%20Quarter%202026.pdf">'
        self.assertTrue(S.brief_url(home).endswith("Second%20Quarter%202026.pdf"))
        with self.assertRaises(RuntimeError):
            S.brief_url('<a href="/water.pdf">')


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
