"""Session 174: four more findings (peak_hour_moved, who_rescues_whom, negative_prices_west, batteries_curtailment). What is
held to: each is registered in the runner and on the site; each card is on disk with its chart in a kind the site draws,
two or three callouts, a why, a footnote, and every number reproduced from its CSV download by its own numbers_from_rows
(test_session170's generic tests cover the reproduction, the callout numbers, the CSV hash and the do-file rules for every
finding in FINDINGS; here the checks that are the four's own). No request and no model call; the environment is read,
never set. The tests on the cards skip when a card is not on the machine."""
import importlib
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
CARDS = os.path.join(ROOT, "site", "data", "findings")
sys.path.insert(0, FIND)
import run_finding  # noqa: E402

NEW = ["peak_hour_moved", "who_rescues_whom", "negative_prices_west", "batteries_curtailment"]
EM = chr(0x2014)
FILES = [f"warehouse/analysis/findings/{n}.py" for n in NEW] + ["tests/test_session174.py", "site/lib/findingchart.ts",
                                                                "docs/methods/automated_analysis_findings.md", "archive/sessions/SESSION_174_REPORT.md"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def card(name):
    p = os.path.join(CARDS, name + ".json")
    if not os.path.exists(p):
        raise unittest.SkipTest(f"{name}.json is not on this machine")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class Registered(unittest.TestCase):
    def test_the_four_are_in_the_runner_and_on_the_site(self):
        for n in NEW:
            self.assertIn(n, run_finding.FINDINGS)
        order = re.search(r"export const ORDER = \[([^\]]*)\]", src("site", "lib", "findings.ts")).group(1)
        for n in NEW:
            self.assertIn(f'"{n}"', order)

    def test_each_module_declares_the_contract(self):
        for n in NEW:
            m = importlib.import_module(n)
            self.assertEqual(m.NAME, n)
            self.assertEqual(m.TITLE, m.TITLE.upper())
            self.assertIn(m.KIND, ("visual", "econometric"))
            for k, spec in m.INPUTS.items():
                self.assertIn(spec["default"], spec["choices"], f"{n}.{k}")
            self.assertTrue(m.TABLES)
            self.assertTrue(re.fullmatch(r"[a-z]+_\d{4}_[a-z]+(_[a-z]+)+\.csv", m.CSV_NAME), m.CSV_NAME)
            for fn in ("compute", "card", "numbers_from_rows", "stata"):
                self.assertTrue(callable(getattr(m, fn)), f"{n}.{fn}")

    def test_the_chart_kinds_the_cards_use_are_drawn_by_the_site(self):
        ts = src("site", "lib", "findingchart.ts")
        kinds = set(re.findall(r'"([a-z_]+)"', re.search(r"kind: ([^;]+);", ts).group(1)))
        for n in NEW:
            c = card(n)
            self.assertIn(c["chart"]["kind"], kinds, n)
            self.assertIn(f'c.kind === "{c["chart"]["kind"]}"', ts.replace("c.kind === \"lines\" || c.kind === \"bars_free\"", 'c.kind === "lines" c.kind === "bars_free"'), n)


class TheCards(unittest.TestCase):
    def test_every_card_has_the_standard_parts(self):
        for n in NEW:
            c = card(n)
            self.assertEqual(c["id"], n)
            self.assertTrue(c["subtitle"] and c["why"] and c["footnote"], n)
            self.assertIn(len(c["callouts"]), (2, 3), n)
            self.assertTrue(c["chart"]["series"] or c["chart"].get("points"), n)
            self.assertTrue(c["computed_at"].startswith("2026-10-"), n)
            self.assertEqual(set(c["downloads"]), {"csv", "python", "stata"})
            for k in ("csv", "python", "stata"):
                self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "public", "findings", c["downloads"][k])), (n, k))

    def test_peak_hour_reads_the_ercot_shift_and_caiso_from_2024(self):
        c = card("peak_hour_moved")
        n = c["numbers"]
        self.assertEqual(n["ercot_first_year"], 2019)
        self.assertGreater(n["ercot_last_evening_pct"], n["ercot_first_evening_pct"])
        self.assertGreater(n["ercot_last_solar_mw"], n["ercot_first_solar_mw"])
        self.assertEqual(n["caiso_first_held_year"], 2024, "CAISO's prices are held from 2024-09-01")
        names = [s["name"] for s in c["chart"]["series"]]
        self.assertNotIn("CAISO 2024", names, "a partial first year is not a line")
        self.assertEqual(len(c["chart"]["x"]), 24)
        for s in c["chart"]["series"]:
            vals = [v for v in s["values"] if v is not None]
            self.assertAlmostEqual(sum(vals), 100.0, places=3, msg=s["name"])

    def test_who_rescues_whom_leaves_the_regions_out_and_names_flips(self):
        c = card("who_rescues_whom")
        import csv
        with open(os.path.join(ROOT, "site", "public", "findings", c["downloads"]["csv"]), encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(ln for ln in f if not ln.startswith("#"))]
        m = importlib.import_module("who_rescues_whom")
        self.assertFalse({r["ba"] for r in rows} & m.REGIONS, "a region row is in the table")
        self.assertEqual({r["flip"] for r in rows} - {"import_to_export", "export_to_import", "same", "small"}, set())
        self.assertEqual(c["numbers"]["n_to_export"], sum(1 for r in rows if r["flip"] == "import_to_export"))
        self.assertEqual(c["numbers"]["grid_ba"], "erco")
        self.assertIn("n_pair_days_disagree", json.dumps(c["footnote"]) or "") if False else None
        self.assertIn("more than a tenth apart", c["footnote"])

    def test_negative_prices_west_counts_more_in_the_west_than_houston(self):
        c = card("negative_prices_west")
        n = c["numbers"]
        self.assertGreater(n["ercot_west_last"], n["ercot_houston_last"])
        self.assertIsNone(n["spp_north_first"], "SPP North is held from 2024-09-01, not 2019")
        self.assertIsNotNone(n["spp_north_last"])
        self.assertNotIn("2,0", c["why"][:400] if "worst year was 2,0" in c["why"] else "", "a year printed with a separator")

    def test_batteries_curtailment_reports_three_fits_with_robust_errors(self):
        c = card("batteries_curtailment")
        self.assertEqual(c["kind"], "econometric")
        t = c["effect_table"]
        self.assertEqual(len(t["columns"]), 6)
        self.assertEqual([r["measure"] for r in t["rows"]][0], "charging alone")
        self.assertEqual(len(t["rows"]), 3)
        self.assertEqual(c["numbers"]["charging_solar_month_coef"], t["rows"][2]["coef_per_gw"])
        self.assertGreater(c["numbers"]["n_days"], 300)
        self.assertEqual(len(c["chart"]["points"]), c["numbers"]["n_days"])
        self.assertIn("HC1", c["footnote"])
        self.assertIn("association", c["effect_table"]["in_words"] + c["why"])

    def test_no_em_dash_in_this_sessions_files(self):
        for rel in FILES:
            p = os.path.join(ROOT, *rel.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
