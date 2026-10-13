"""Session 253: the CAISO generator at ERCOT's depth (docs/methods/generator_earns_algorithm.md, section 12).

Energy Research Warehouse (ERW). warehouse/analysis/generator_caiso_check.py runs the generator page's own model for
CAISO at its three hubs and sets the result beside CAISO's market monitor's combustion turbine and Lawrence Berkeley
National Laboratory's market value of wind and solar. The page was not edited: the note lists what the code machine
changes.

What is held here: the published figures typed into the script add up as their own tables do, and the note quotes
them; the finance of the script is the page's (ERCOT's default case comes out at the note's own figures); the note's
tables are the kept results; the section sits before "Checks", so the note still ends with the cross-checks the page
counts; and the page still says 10. No request, no table.
"""

import csv
import json
import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
import generator_caiso_check as G  # noqa: E402

NOTE = ("docs", "methods", "generator_earns_algorithm.md")
KEPT = ("docs", "howitworks", "computed")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def section():
    note = src(*NOTE)
    return note[note.index('<a id="caiso-depth"></a>'):note.index("<!-- end of the session 253 section -->")]


def rows_after(text, head):
    part = text[text.index(head):]
    lines = part.split("\n")[2:]
    out = []
    for line in lines:
        if not line.startswith("| "):
            break
        out.append([c.strip() for c in line.strip().strip("|").split(" | ")])
    return out


class ThePublishedFigures(unittest.TestCase):
    def test_the_market_monitors_table_adds_up(self):
        for hub, t in G.DMM_CT.items():
            self.assertAlmostEqual(t["revenue"] - t["costs"], t["net"], delta=0.011, msg=hub)

    def test_lbnls_energy_and_capacity_values_add_to_its_totals(self):
        for name, t in (("wind", G.LBNL_WIND_2025), ("solar", G.LBNL_SOLAR_2024)):
            for e, c, total in zip(t["energy"], t["capacity"], t["total"]):
                self.assertAlmostEqual(e + c, total, delta=0.011, msg=name)
        self.assertAlmostEqual(G.LBNL_SOLAR_2024["total"][3] / G.LBNL_SOLAR_2024["total"][0], G.LBNL_SOLAR_VALUE_FACTOR_2024, delta=0.0005)

    def test_the_note_quotes_them(self):
        s = section()
        for figure in ("3.52 net", "0.78 net", "running 3.43 percent", "running 1.32 percent", "| 34.21: a flat profile", "32.97: the wind profile at all power plants",
                       "31.21 at the wind plants' own nodes", "30.82 after curtailment", "2024: 8.62 for the solar profile", "34.35 for a flat block at all nodes",
                       "USD 47.06: LevelTen's CAISO solar index, 2024", "USD 27.45: LBNL's sample", "USD 78.2: LevelTen's CAISO wind index, 2025", "0.053165 tonnes per MMBtu at USD 29.89",
                       "PG&E Citygate 3.40 and SoCal Citygate 3.60"):
            self.assertIn(figure, s, figure)
        for address in (G.DMM_URL, G.WIND_URL, G.SOLAR_URL):
            self.assertIn(address, s, address)
        self.assertNotIn("emp.lbl.gov/sites", s)             # the host that refused the reader is named, never linked


class TheFinance(unittest.TestCase):
    def test_ercots_default_case_comes_out_at_the_notes_own_figures(self):
        # docs/howitworks/generator.md: 59.85 USD per kW on 2,580 MWh per MW; 0.67 times; 39.14; 58.36; debt payment 70.79
        r = G.finance("solar", 59.85226, 2.580)
        self.assertAlmostEqual(r["debt_payment_per_kw"], 70.78769, places=3)
        self.assertAlmostEqual(r["coverage"], 0.67, delta=0.005)
        self.assertAlmostEqual(r["price_for_coverage_1_25"], 39.14, delta=0.02)
        self.assertAlmostEqual(r["breakeven_ppa"], 58.36, delta=0.03)
        self.assertAlmostEqual(r["npv_per_kw"], -741.60, delta=0.5)

    def test_a_peakers_toll_is_a_fixed_charge(self):
        a, b = G.finance("peaker", 30.0, 2.9), G.finance("peaker", 45.0, 3.6)
        self.assertAlmostEqual(a["price_for_coverage_1_25"], 8.34, delta=0.005)
        self.assertEqual(a["breakeven_ppa"], b["breakeven_ppa"])        # a contract on the whole plant for its life: the market is not in it
        self.assertEqual(a["unit"], "USD/kW-month")

    def test_the_peakers_rule_with_an_adder_on_the_fuel(self):
        h = pd.DataFrame({"month": ["2025-01"] * 4, "p": [30.0, 60.0, 90.0, 40.0], "hh": [3.0, 3.0, 3.0, None]})
        plain = G.peaker_as(h, ["2025-01"], 10.0, 5.0, 0.0)             # cost 35: runs at 60 and 90
        self.assertEqual((plain["hours_run"], plain["hours"]), (2, 3))
        self.assertAlmostEqual(plain["margin_per_kw"], (25.0 + 55.0) / 1000)
        dear = G.peaker_as(h, ["2025-01"], 10.0, 5.0, 3.0)              # cost 65: runs at 90 alone
        self.assertEqual(dear["hours_run"], 1)
        self.assertAlmostEqual(dear["margin_per_kw"], 25.0 / 1000)


class TheNote(unittest.TestCase):
    def test_the_section_sits_before_checks_and_the_note_still_ends_with_the_cross_checks(self):
        note = src(*NOTE)
        self.assertEqual(note.count("## 12. CAISO at ERCOT's depth (session 253)"), 1)
        self.assertLess(note.index("<!-- end of the session 253 section -->"), note.index("\n## Checks\n"))
        self.assertTrue(note.rstrip().split("\n## ")[-1].startswith("Cross-checks"))
        self.assertEqual([h for h in re.findall(r"^### (12\.\d) ", section(), flags=re.M)], ["12.1", "12.2", "12.3", "12.4", "12.5", "12.6"])

    def test_the_tables_are_the_kept_results(self):
        s = section()
        kept = list(csv.DictReader(ln for ln in src(*KEPT, "generator_caiso_check_2026-10-13.csv").split("\n") if ln and not ln.startswith("#")))
        self.assertEqual(len(kept), 36)                                  # three hubs, two markets, three assets, two spans
        table = {(r[0], r[1]): r for r in rows_after(s, "| Hub | Asset | 2025: revenue, USD per kW |")}
        self.assertEqual(len(table), 9)
        for r in kept:
            if r["market"] != "rt" or r["span"] != "2025":
                continue
            cells = table[(r["hub"], "gas peaker" if r["asset"] == "peaker" else r["asset"])]
            self.assertEqual(cells[2], f"{float(r['revenue_per_kw']):,.2f}", r)
            self.assertEqual(cells[3], f"{float(r['energy_mwh_per_mw']):,.0f}", r)
            self.assertEqual(cells[4], f"{float(r['capture_price']):,.2f}", r)
        detail = json.loads(src(*KEPT, "generator_caiso_check_2026-10-13.json"))
        cap = {(r[0], r[1], r[2]): r for r in rows_after(s, "| Hub | Market | Fuel | 2025: capture price |")}
        self.assertEqual(len(cap), 12)
        for r in detail["capture_file"]:
            if r["span"] == "2025":
                cells = cap[(r["hub"], "real time" if r["market"] == "rt" else "day-ahead", r["fuel"])]
                self.assertEqual(cells[3], f"{r['capture_price']:,.2f}", r)
                self.assertEqual(cells[5], f"{r['capture_rate_pct']:,.1f}%", r)

    def test_the_pages_files_equal_the_rebuild_in_every_whole_month(self):
        detail = json.loads(src(*KEPT, "generator_caiso_check_2026-10-13.json"))
        self.assertEqual(len(detail["page_files"]), 9)
        for r in detail["page_files"]:
            self.assertGreaterEqual(r["months_compared"], 24, r)
            self.assertLessEqual(set(r["months_that_differ"]), {"2026-09", "2026-10"}, r)      # the month under way; September's late gas prices
            if r["asset"] != "peaker":
                self.assertLessEqual(set(r["months_that_differ"]), {"2026-10"}, r)

    def test_the_comparisons_each_hold_a_gap_or_say_why_not_and_a_reason(self):
        s = section()
        rows = rows_after(s, "| What | Ours | Theirs | Gap | Reason |")
        self.assertEqual(len(rows), 12)
        for r in rows:
            self.assertEqual(len(r), 5, r[0][:50])
            self.assertTrue(all(r), r[0][:50])
            self.assertGreater(len(r[4]), 30, r[0][:50])
        gaps = [r for r in rows if not r[3].startswith("not computed")]
        self.assertEqual(len(gaps), 10)
        self.assertIn("- These 12 rows are not in the table of \"Cross-checks\" below", s)
        self.assertIn("10 of them hold a gap", s)
        self.assertIn("flip the count from 10 to 20 in three places", s)

    def test_the_page_was_not_edited(self):
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        self.assertIn('<span data-checked-against="10">Checked against: 10 published figures (Lazard, the Annual Technology Baseline, EIA).', page)
        self.assertIn("const c = g * hr + vom;", src("site", "lib", "merchant.ts"))

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (NOTE, ("warehouse", "analysis", "generator_caiso_check.py"), ("tests", "test_session253.py"), ("archive", "sessions", "SESSION_253_REPORT.md")):
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertEqual(src(*parts).count(chr(0x2014)), 0, parts)


if __name__ == "__main__":
    unittest.main()
