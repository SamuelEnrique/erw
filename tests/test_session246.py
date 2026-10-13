"""Session 246: the CAISO battery at ERCOT's depth.

Energy Research Warehouse (ERW). docs/methods/battery_stack.md, "CAISO's stress days", "CAISO beside its market
monitor" and "For the page". What is held here: the rule that makes California's stress events from CAISO's own
notices (which kinds count, three days apart is one event, only days the model solved), the stress rows it writes,
that ERCOT's events are as they were, the market monitor's figures as they are typed and as the method quotes them,
that the comparison script puts the model back as it found it, and the list for the page.

No request and no table: the notices and the solved days are stand-ins.
"""

import os
import re
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (("warehouse", "derived"), ("warehouse", "analysis"), ("warehouse", "metadata")):
    sys.path.insert(0, os.path.join(ROOT, *p))
import battery_stack as bs  # noqa: E402

EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def notices(*rows):
    return pd.DataFrame(rows, columns=["event_date", "event_type"])


# CAISO's notices from September 2024 as caiso_grid_emergencies held them on 13 October 2026
HELD = notices(("2024-09-04", "rmo"), ("2024-09-05", "rmo"), ("2024-09-06", "rmo"), ("2024-09-06", "transmission_emergency"), ("2024-09-07", "transmission_emergency"),
               ("2024-09-09", "rmo"), ("2024-11-05", "transmission_emergency"), ("2024-11-06", "transmission_emergency"), ("2024-11-07", "transmission_emergency"),
               ("2025-01-20", "rmo"), ("2025-01-21", "rmo"), ("2025-04-30", "transmission_emergency"))


class CaisosStressDays(unittest.TestCase):
    def test_the_two_events_of_the_held_prices(self):
        got = bs.caiso_stress_windows(HELD, "2024-09-01", "2026-10-11")
        self.assertEqual(got, {"caiso_notices_20240904": ("2024-09-04", "2024-09-09", ["rmo"]),
                               "caiso_notices_20250120": ("2025-01-20", "2025-01-21", ["rmo"])})
        # session 247: CAISO's report read again the same day holds six more notices, and the same rule makes two more events
        newer = pd.concat([HELD, notices(("2026-09-09", "rmo"), ("2026-09-10", "rmo"), ("2026-10-05", "rmo"), ("2026-10-06", "rmo"), ("2026-10-07", "rmo"),
                                         ("2026-10-08", "rmo"))], ignore_index=True)
        got = bs.caiso_stress_windows(newer, "2024-09-01", "2026-10-11")
        self.assertEqual(list(got), ["caiso_notices_20240904", "caiso_notices_20250120", "caiso_notices_20260909", "caiso_notices_20261005"])
        self.assertEqual(got["caiso_notices_20261005"], ("2026-10-05", "2026-10-08", ["rmo"]))

    def test_a_transmission_emergency_makes_no_stress_day(self):
        only = HELD[HELD["event_type"] == "transmission_emergency"]
        self.assertEqual(bs.caiso_stress_windows(only, "2024-09-01", "2026-10-11"), {})
        self.assertNotIn("transmission_emergency", bs.CAISO_NOTICES)
        self.assertNotIn("vlrp", bs.CAISO_NOTICES)
        for kind in ("flex_alert", "rmo", "eea_watch", "eea1", "eea2", "eea3", "stage1", "stage2", "stage3", "warning", "alert", "load_interruption"):
            self.assertIn(kind, bs.CAISO_NOTICES, kind)

    def test_days_at_most_three_apart_are_one_event_and_four_apart_are_two(self):
        self.assertEqual(bs.CAISO_NOTICE_GAP, 3)
        three = notices(("2025-08-20", "flex_alert"), ("2025-08-23", "eea1"))
        self.assertEqual(bs.caiso_stress_windows(three, "2024-09-01", "2026-10-11"), {"caiso_notices_20250820": ("2025-08-20", "2025-08-23", ["eea1", "flex_alert"])})
        four = notices(("2025-08-20", "flex_alert"), ("2025-08-24", "flex_alert"))
        self.assertEqual(list(bs.caiso_stress_windows(four, "2024-09-01", "2026-10-11")), ["caiso_notices_20250820", "caiso_notices_20250824"])

    def test_only_the_days_the_model_solved_count(self):
        old = notices(("2020-08-14", "stage3"), ("2022-09-06", "eea3"), ("2024-08-31", "rmo"), ("2024-09-04", "rmo"))
        self.assertEqual(list(bs.caiso_stress_windows(old, "2024-09-01", "2026-10-11")), ["caiso_notices_20240904"])
        self.assertEqual(bs.caiso_stress_windows(old, "2024-09-05", "2026-10-11"), {})
        self.assertEqual(bs.caiso_stress_windows(None, "2024-09-01", "2026-10-11"), {})
        self.assertEqual(bs.caiso_stress_windows(notices(), "2024-09-01", "2026-10-11"), {})

    def test_the_rows_are_the_held_days_of_each_window_by_stream(self):
        day = dict(energy=400.0, total=693.0, delivered=3.4, regup=100.0, regdn=180.0, spin=10.0, nonspin=3.0)
        days = {(s, d): {"2024-09-03": day, "2024-09-04": day, "2024-09-08": dict(day, energy=200.0), "2024-09-10": day}
                for s in bs.STRATEGIES for d in bs.DURATIONS}
        base = dict(entity="caiso:TH_SP15_GEN-APND", geo="US-CA", market="caiso", node="TH_SP15_GEN-APND", source=bs.SOURCE, source_url=bs.METHOD_URL,
                    retrieved_at="2026-10-13T07:22:01Z", vintage="")
        wins = bs.caiso_stress_windows(HELD, "2024-09-01", "2026-10-11")
        rows = pd.DataFrame(bs.stress_rows("caiso", days, base, wins))
        self.assertEqual(sorted(rows["event"].unique()), ["caiso_notices_20240904"])                # no solved day in January's window
        self.assertEqual(sorted(rows["ts_utc"].unique()), ["2024-09-04T00:00:00Z", "2024-09-08T00:00:00Z"])   # the 3rd and the 10th are outside
        self.assertEqual(len(rows), 2 * 2 * 3 * 3)                                                  # days, strategies, durations, streams
        one = rows[(rows["ts_utc"] == "2024-09-04T00:00:00Z") & (rows["x_strategy"] == "dayahead") & (rows["x_duration_hours"] == 4)].set_index("x_metric")["value"]
        self.assertEqual((one["revenue_energy_usd_per_mw"], one["revenue_ancillary_usd_per_mw"], one["revenue_total_usd_per_mw"]), (400.0, 293.0, 693.0))
        self.assertEqual(set(rows["freq"]), {"P1D"})

    def test_ercots_three_events_are_as_they_were(self):
        self.assertEqual(bs.STRESS, ["uri_2021", "elliott_2022", "ercot_heat_2023"])
        self.assertEqual(bs.ercot_stress_windows(), {"uri_2021": ("2021-02-07", "2021-02-24"), "elliott_2022": ("2022-12-19", "2022-12-29"),
                                                    "ercot_heat_2023": ("2023-08-01", "2023-09-10")})
        day = dict(energy=1.0, total=2.0, delivered=1.0, regup=1.0)
        days = {(s, d): {"2021-02-15": day, "2024-09-05": day} for s in bs.STRATEGIES for d in bs.DURATIONS}
        rows = pd.DataFrame(bs.stress_rows("ercot", days, dict(entity="ercot:HB_HUBAVG")))
        self.assertEqual(set(rows["event"]), {"uri_2021"})                                           # a California day is no ERCOT event

    def test_the_header_names_tables_only_where_coverage_reads_them(self):
        # session 246's first build wrote a note in brackets into the "Derived from" line; build_coverage.py reads every
        # name on that line as a table and refused both tables
        text = src("warehouse", "derived", "battery_stack.py")
        line = re.search(r'"Derived from: ([^"]+)"\s*\n\s*"([^"]+)"', text)
        names = [n.strip() for n in (line.group(1) + line.group(2)).split(";")]
        self.assertTrue(all(re.fullmatch(r"[a-z0-9_]+", n) for n in names), names)
        # coverage names both grids for both tables since this session (the stress days were ERCOT's alone)
        cov = src("warehouse", "metadata", "build_coverage.py")
        self.assertIn('if table in ("battery_stack_monthly", "battery_stack_stress_daily"):', cov)
        self.assertNotIn('else "ERCOT"', cov.split('if table in ("battery_stack_monthly", "battery_stack_stress_daily"):', 1)[1].split("\n    if ", 1)[0])


class BesideTheMarketMonitor(unittest.TestCase):
    def setUp(self):
        import battery_caiso_dmm
        self.d = battery_caiso_dmm

    def test_the_published_figures_are_typed_as_the_report_prints_them(self):
        t = self.d.DMM_TABLE_1_8
        self.assertEqual(t["CAISO System"], (28.8, 22.8, 14.2, 11.5, 77.3))
        for area, (q1, q2, q3, q4, total) in t.items():
            self.assertAlmostEqual(q1 + q2 + q3 + q4, total, delta=0.11, msg=area)                    # the report's own quarters add to its total
        self.assertEqual((self.d.DMM_SIMULATED, self.d.DMM_ACTUAL), ({"energy": 39.0, "regulation": 39.0}, {"energy": 35.0, "regulation": 9.0}))
        self.assertEqual((self.d.DMM_RTE, self.d.YEAR), (0.85, "2025"))
        self.assertIn("2025-annual-report-on-market-issues-and-performance.pdf", self.d.URL)

    def test_the_method_quotes_the_same_figures_and_computes_the_gaps_from_them(self):
        doc = src("docs", "methods", "battery_stack.md")
        part = doc.split("## CAISO beside its market monitor (session 246)", 1)[1].split("\n## ", 1)[0]
        for words in ("84.72 (as theirs)", '77.3, "CAISO System" (Table 1.8)', "+7.4 (10 percent)", "29.23 | 28.8 | +0.4", "24.30 | 22.8 | +1.5", "17.45 | 14.2 | +3.3",
                      "13.75 | 11.5 | +2.3", "41.89; 42.83", "+2.9; +3.8", "85.34", "91.74", "+14.4", "+7.3; +33.3", "62.6; 64.2; 66.3", "+22.1; +20.5; +18.4",
                      "53, 78 and 103", "361 days", "The whole gap is regulation"):
            self.assertIn(words, part, words)
        # each gap is ours less theirs, to the printed decimal
        for ours, theirs, gap in ((84.72, 77.3, 7.4), (29.23, 28.8, 0.4), (24.30, 22.8, 1.5), (17.45, 14.2, 3.3), (13.75, 11.5, 2.3), (41.89, 39, 2.9), (42.83, 39, 3.8),
                                  (85.34, 77.3, 8.0), (91.74, 77.3, 14.4), (42.31, 35, 7.3), (42.25, 9, 33.3), (84.72, 62.6, 22.1), (84.72, 64.2, 20.5), (84.72, 66.3, 18.4)):
            self.assertAlmostEqual(ours - theirs, gap, delta=0.051, msg=(ours, theirs))
        self.assertEqual(round(84.72 / 77.3 - 1, 2), 0.10)

    def test_the_comparison_puts_the_model_back_as_it_found_it(self):
        products = [p["key"] for p in bs.MARKETS["caiso"]["products"]]
        solve, check, seen = bs.solve_day, bs.check_day, {}
        keep = self.d.run
        self.d.run = lambda variant: seen.update(products=[p["key"] for p in bs.MARKETS["caiso"]["products"]], all=bs.ALL_MARKETS["caiso"] is bs.MARKETS["caiso"],
                                                 patched=bs.solve_day is not solve) or (pd.DataFrame(), [])
        try:
            self.d.as_dmm()
        finally:
            self.d.run = keep
        self.assertEqual(seen, {"products": ["regup", "regdn"], "all": True, "patched": True})        # inside: regulation only, another round trip
        self.assertEqual([p["key"] for p in bs.MARKETS["caiso"]["products"]], products)              # after: all four again
        self.assertIs(bs.solve_day, solve)
        self.assertIs(bs.check_day, check)
        self.assertEqual(bs.RTE, 0.86)

    def test_quarters_are_usd_per_kw_and_add_to_the_year(self):
        d = pd.DataFrame([dict(variant="page", strategy="dayahead", duration_h=4, day=f"2025-{m:02d}-15", energy=1000.0 * m, regulation=500.0, reserves=10.0, total=1000.0 * m + 510.0)
                          for m in range(1, 13)])
        q = self.d.quarters(d).set_index("quarter")
        self.assertEqual(list(q.index), ["Q1", "Q2", "Q3", "Q4", "year"])
        self.assertEqual(q.loc["Q1", "energy"], 6.0)                                                 # 1,000 + 2,000 + 3,000 USD per MW is 6 USD per kW
        self.assertAlmostEqual(q.loc[["Q1", "Q2", "Q3", "Q4"], "total"].sum(), q.loc["year", "total"], places=6)
        self.assertEqual(q.loc["year", "days"], 12)


class TheWords(unittest.TestCase):
    def test_the_method_says_how_californias_stress_days_are_made_and_what_they_paid(self):
        doc = src("docs", "methods", "battery_stack.md")
        part = doc.split("## CAISO's stress days (session 246)", 1)[1].split("\n## ", 1)[0]
        for words in ("Restricted Maintenance Operations", "a Transmission Emergency", "at most three days apart", "caiso_notices_<YYYYMMDD>", "`caiso_notices_20240904`",
                      "`caiso_notices_20250120`", "3,670 | 4,101 | 4,464 | 3,938", "475 | 638 | 854 | 731", "held to 30 April 2025",
                      # session 247 read CAISO's report again: two more events, by the same rule
                      "`caiso_notices_20260909`", "`caiso_notices_20261005`", "957 | 979 | 983 | 915", "1,976 | 2,135 | 2,314 | 1,930", "read every day since session 247"):
            self.assertIn(words, part, words)
        self.assertIn("## The daily run", doc)                                                       # the section the new ones were put before is still there

    def test_the_list_for_the_page_names_each_place(self):
        doc = src("docs", "methods", "battery_stack.md")
        part = doc.split("## For the page: what CAISO still lacks beside ERCOT (session 246)", 1)[1].split("\n## ", 1)[0]
        for words in ("The page was not edited", "`ready: true`", "`EVENTS`", "`stress`", 'x.grid === "ercot"', "`awardsBeside`", "site/lib/batterystack.ts",
                      "site/app/cost-of-power/battery/page.tsx", "From September 2024: 25 months"):
            self.assertIn(words, part, words)
        # and it is true of the page as it stands: three ERCOT events in a fixed list, the sentence for ERCOT alone
        lib = src("site", "lib", "batterystack.ts")
        self.assertIn('{ id: "caiso", name: "CAISO", ready: true', lib)
        self.assertIn("export const EVENTS: Record<string, string> = { uri_2021:", lib)
        self.assertIn('if (grid !== "ercot") return null;', lib)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in ("warehouse/derived/battery_stack.py", "warehouse/analysis/battery_caiso_dmm.py", "docs/methods/battery_stack.md", "tests/test_session246.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
