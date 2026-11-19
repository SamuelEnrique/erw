"""Session 8460 (chain 503, part E): the replication of "The whole country" on /supply, and the reader's read.

replication/supply/replicate_regions.py recomputes, from the trade, matrix and mix files alone and by the method
note's rules, every figure the section prints, beside the figure the site's own code draws
(site/scripts/supply-regions-figures.mjs). Held here, without a build and without any warehouse table:

- on the test's fixtures (values made by a rule, not data) every figure the page draws is recomputed, N of N; a figure
  moved by one in its last digit is caught, and so are a figure the page drops, a figure the rule does not give, a
  mark of a large gap that is missing or one too many, a pair's row that names the wrong sender, and another year
  drawn first;
- on the site as it stands the replication runs and says what it finds: no file yet (nothing to recompute), or every
  figure of every file that is there;
- the same flow in two files (a pair's year in the matrix, the year's months in a region's trade file) is set side by
  side on request;
- the five hovers the reader's read completed are held by site/scripts/test-supply-regions-8460.mjs, run from here.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "supply", "replicate_regions.py")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
WRITTEN = [
    "replication/supply/replicate_regions.py", "site/scripts/supply-regions-figures.mjs", "site/scripts/test-supply-regions-8460.mjs",
    "tests/test_session8460_supply_regions_replication.py", "docs/reviews/supply-regions-read-2026-11-19.md", "docs/methods/supply_and_trade.md",
    "site/components/supply/Country.tsx",
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(script, args=(), regions_dir=None):
    env = {k: v for k, v in os.environ.items() if k != "ERW_REGIONS_DIR"}
    if regions_dir:
        env["ERW_REGIONS_DIR"] = regions_dir
    return subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", f"scripts/{script}", *args], cwd=SITE,
                          capture_output=True, text=True, encoding="utf-8", timeout=900, env=env)


def replicate(*args):
    return subprocess.run([sys.executable, REP, *args], capture_output=True, text=True, encoding="utf-8", timeout=600)


def module():
    spec = importlib.util.spec_from_file_location("replicate_regions_8460", REP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw-8460-")
        r = node("supply-regions-figures.mjs", ["--fixture", cls.tmp])
        assert r.returncode == 0, r.stderr[-800:]
        cls.figures = os.path.join(cls.tmp, "figures.json")
        r = node("supply-regions-figures.mjs", [cls.figures], regions_dir=cls.tmp)
        assert r.returncode == 0, r.stderr[-800:]
        with open(cls.figures, encoding="utf-8") as f:
            cls.page = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def changed(self, name, change):
        page = json.loads(json.dumps(self.page))
        change(page)
        at = os.path.join(self.tmp, name)
        with open(at, "w", encoding="utf-8") as f:
            json.dump(page, f)
        return replicate("--figures", at, "--files", self.tmp)

    def test_every_figure_of_the_fixtures_is_recomputed(self):
        r = replicate("--figures", self.figures, "--files", self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-800:])
        m = re.search(r"(\d+) of (\d+) figures over 27 files \(13 trade files, 13 mix files, 1 matrix file\)", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 30000, r.stdout[-400:])
        self.assertNotIn("FAIL", r.stdout)

    def test_the_figures_file_holds_every_kind_of_figure(self):
        f, page = self.page["figures"], self.page
        self.assertEqual(page["large_gap_pct"], 10)
        self.assertEqual(sum(1 for s in page["files"].values() if s.get("file")), 27)
        for key, shown in (("trade|TEN|2025|SE|own", "-14.0"), ("trade|TEN|2025|SE|gap_pct", "22.2"), ("trade|TEN|2025|SE|months|of", "12"),
                           ("trade|TEN|2025-01|SE|their", "-1.0"), ("trade|TEN|2025-01|SE|gap_pct", "22.2"), ("trade|CAR|2018|all|months", "3"),
                           ("pair|CAR-SE|2025|mean", "992.0"), ("bapair|DUK-TVA|2025|from_report", "11,002.0"), ("partners|2025|n", "3"),
                           ("mix|TEN|2025|natural_gas", "3.6"), ("mix|TEN|2025-02|days_held", "26"), ("mix|TEN|2025-02|days_in_month", "28"),
                           ("mix|CAR|2025|months", "11")):
            self.assertEqual(f.get(key), shown, key)
        self.assertIn("trade|TEN|2025|SE|gap_pct", page["large"])
        self.assertIn("trade|TEN|2025-01|SE", page["large"])
        self.assertIn("pair|SE-TEN|2025|gap_pct", page["large"])
        self.assertEqual(page["words"]["pair|CAR-TEN|2025"], {"sent": "Tennessee", "received": "Carolinas"})
        self.assertEqual(page["words"]["pair|FLA-SE|2025"], {"sent": "Florida and Southeast", "received": "no net flow"})
        self.assertEqual(page["first"], {"a": "CAL", "b": "CAR", "year": "2025"})

    def test_a_figure_moved_by_one_in_its_last_digit_is_caught(self):
        moved = {"trade|TEN|2025|SE|gap_pct": "22.3", "pair|CAR-SE|2025|mean": "992.1", "mix|TEN|2025|natural_gas": "3.7",
                 "trade|TEN|2025-01|SE|their": "-1.1", "trade|CAR|2018|all|months": "4", "mix|TEN|2025-02|days_held": "27"}
        r = self.changed("moved.json", lambda p: p["figures"].update(moved))
        self.assertEqual(r.returncode, 1, r.stdout[-800:])
        for key in moved:
            self.assertIn(f"FAIL {key}: the page shows {moved[key]}", r.stdout)
        self.assertEqual(r.stdout.count("FAIL"), len(moved))

    def test_a_figure_the_page_drops_and_one_the_rule_does_not_give_are_caught(self):
        def change(p):
            del p["figures"]["trade|CAL|2025|all"]
            p["figures"]["trade|TEX|2023|MEX|their"] = "+1.0"   # Mexico files nothing: no such figure by the rule
        r = self.changed("gone.json", change)
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"FAIL trade\|CAL\|2025\|all: ours [-\d.]+, not on the page")
        self.assertIn("FAIL trade|TEX|2023|MEX|their: the page shows +1.0, the file gives no figure by the note's rule", r.stdout)

    def test_the_marks_of_a_large_gap_are_held_both_ways(self):
        def change(p):
            p["large"].remove("pair|SE-TEN|2025|gap_pct")
            p["large"].append("trade|TEN|2025|CAR|gap_pct")
        r = self.changed("large.json", change)
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"FAIL pair\|SE-TEN\|2025\|gap_pct: large by the note's rule \(66\.6\d+ percent\), not marked on the page")
        self.assertIn("FAIL trade|TEN|2025|CAR|gap_pct: marked large on the page, not large by the note's rule", r.stdout)

    def test_a_row_that_names_the_wrong_sender_and_another_first_year_are_caught(self):
        def change(p):
            p["words"]["pair|CAR-TEN|2025"] = {"sent": "Carolinas", "received": "Tennessee"}
            p["first"]["year"] = "2026"
        r = self.changed("words.json", change)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL pair|CAR-TEN|2025: the page's row reads", r.stdout)
        self.assertIn("FAIL first|year: the page draws 2026 first, ours 2025", r.stdout)

    def test_a_file_the_page_did_not_read_is_caught(self):
        # in the test's folder the file says it is a fixture, which the site's reader refuses in its own folder
        r = self.changed("unread.json", lambda p: p["files"].update({"trade/ten.json": {"file": False}}))
        self.assertEqual(r.returncode, 1)
        self.assertIn("trade/ten.json: a fixture, which the site's reader refuses in its own folder: not recomputed", r.stdout)
        self.assertIn("FAIL trade|TEN|2025|all: the page shows -357.9, the file gives no figure by the note's rule", r.stdout)
        # the same file with no such line is a file the page was bound to read
        other = os.path.join(self.tmp, "as-real")
        shutil.copytree(os.path.join(self.tmp, "trade"), os.path.join(other, "trade"))
        at = os.path.join(other, "trade", "ten.json")
        with open(at, encoding="utf-8") as f:
            ten = json.load(f)
        del ten["fixture"]
        with open(at, "w", encoding="utf-8") as f:
            json.dump(ten, f)
        r = replicate("--figures", os.path.join(self.tmp, "unread.json"), "--files", other)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL trade/ten.json: the file is in the folder and the page did not read it", r.stdout)

    def test_the_same_flow_in_two_files_is_set_side_by_side_on_request(self):
        # the fixtures' trade files and matrix are made by two unrelated rules, so they do not agree: the flag says so
        r = replicate("--figures", self.figures, "--files", self.tmp, "--same-flow")
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"the same flow in two files: \d+ of \d+ agree within 0\.05 GWh")
        self.assertIn("DIFFERS CAR-SE 2025, CAR's report", r.stdout)
        self.assertRegex(r.stdout, r"(\d+) of \1 figures over 27 files")   # the page's own figures still all pass

    def test_on_the_site_as_it_stands(self):
        out = os.path.join(self.tmp, "site.json")
        r = node("supply-regions-figures.mjs", [out])
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        r = replicate("--figures", out)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        with open(out, encoding="utf-8") as f:
            files = json.load(f)["files"]
        self.assertEqual(len(files), 27)
        if not any(s.get("file") for s in files.values()):
            self.assertIn("no file of the whole country is on the site yet", r.stdout)
        else:
            self.assertRegex(r.stdout, r"(\d+) of \1 figures over \d+ files")

    def test_a_bad_figures_file_is_bad_input(self):
        self.assertEqual(replicate("--figures", os.path.join(self.tmp, "none.json")).returncode, 2)
        self.assertEqual(node("supply-regions-figures.mjs").returncode, 2)

    def test_the_hovers_the_read_completed(self):
        r = node("test-supply-regions-8460.mjs")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:])
        self.assertIn("20 of 20 passed", r.stdout)
        self.assertNotIn("FAIL", r.stdout)


class TheRules(unittest.TestCase):
    """The replication's own rules on rows made here (values made by the test, not data)."""

    def test_the_same_flow_agrees_when_the_two_files_hold_the_same_sums(self):
        m = module()
        months = [f"2025-{i:02d}" for i in range(1, 13)]
        car = {"months": months, "neighbors": {"SE": {"net_imports_mwh": [-100.0] * 12}}}
        se = {"months": months, "neighbors": {"CAR": {"net_imports_mwh": [90.0] * 12}}}
        row = {"a": "CAR", "b": "SE", "year": 2025, "a_report_mwh": 1200.0, "b_report_mwh": 1080.0}
        read = {"trade/car.json": car, "trade/se.json": se, "trade_matrix.json": {"region_pairs": [row]}}
        self.assertEqual(m.same_flow(read), (2, 2))
        row["b_report_mwh"] = 1180.0
        self.assertEqual(m.same_flow(read), (1, 2))
        car["neighbors"]["SE"]["net_imports_mwh"][3] = None    # a year held in part is not set against the matrix
        self.assertEqual(m.same_flow(read), (0, 1))

    def test_a_pair_with_no_direction_and_a_percent_that_cannot_be_formed(self):
        m = module()
        figs, large, words = {}, set(), {}
        rows = [{"a": "FLA", "b": "SE", "year": 2025, "a_report_mwh": 0, "b_report_mwh": 0, "mean_mwh": 0, "gap_mwh": 0, "direction": "none"},
                {"a": "CAR", "b": "SE", "year": 2025, "a_report_mwh": -4000, "b_report_mwh": -6000, "mean_mwh": -5000, "gap_mwh": 2000},
                {"a": "NW", "b": "SW", "year": 2025, "a_report_mwh": 5000, "b_report_mwh": None}]
        m.expected_matrix({"region_pairs": rows, "ba_pairs": [], "partners": {"TVA": {"2025": {"by_gross": []}}}}, ["2024", "2025"], figs, large, words)
        self.assertEqual(words["pair|FLA-SE|2025"], {"sent": "Florida and Southeast", "received": "no net flow"})
        self.assertNotIn("pair|FLA-SE|2025|gap_pct", figs)
        self.assertEqual(words["pair|CAR-SE|2025"], {"sent": "Southeast", "received": "Carolinas"})
        self.assertEqual((figs["pair|CAR-SE|2025|from_report"], figs["pair|CAR-SE|2025|to_report"], figs["pair|CAR-SE|2025|mean"], figs["pair|CAR-SE|2025|gap"]), (6.0, 4.0, 5.0, 2.0))
        self.assertAlmostEqual(figs["pair|CAR-SE|2025|gap_pct"], 40.0)
        self.assertIn("pair|CAR-SE|2025|gap_pct", large)
        self.assertEqual(words["pair|NW-SW|2025"], {"sent": "Northwest and Southwest", "received": "not held yet"})
        self.assertEqual((figs["partners|2025|n"], figs["partners|2024|n"], figs["bapairs|2025|n"]), (1.0, 0.0, 0.0))

    def test_large_is_ten_percent_or_more_before_rounding(self):
        m = module()
        self.assertAlmostEqual(m.gap_pct(-10, 100, -100), 10.0)
        self.assertIsNone(m.gap_pct(5, 0, 0))
        self.assertIsNone(m.gap_pct(None, 1, 1))
        self.assertEqual(m.parse("+1,234.5"), (1234.5, 0.1))
        self.assertEqual(m.parse("-10"), (-10.0, 1.0))
        self.assertEqual(m.LARGE_PCT, 10.0)

    def test_the_year_drawn_first(self):
        m = module()
        months = lambda ys: [f"{y}-01" for y in ys]
        self.assertEqual(m.first_year({"trade/cal.json": {"built": "2026-11-19T12:00:00Z", "months": months([2024, 2025, 2026])}}), "2025")
        self.assertEqual(m.first_year({"trade/cal.json": {"built": "2026-11-19T12:00:00Z", "months": months([2024, 2026])}}), "2024")
        self.assertEqual(m.first_year({"trade_matrix.json": {"built": "2026-11-19T12:00:00Z", "years": [2026]}}), "2026")
        self.assertIsNone(m.first_year({"trade/ten.json": {"built": "2026-11-19T12:00:00Z", "months": months([2025])}}))


class TheSource(unittest.TestCase):
    def test_written_from_the_note_not_from_the_pages_code(self):
        code = src("replication", "supply", "replicate_regions.py").split('"""', 2)[2]
        for word in ("countrytrade", "countryfiles", "Country.tsx", "import subprocess"):
            self.assertNotIn(word, code)
        figures = src("site", "scripts", "supply-regions-figures.mjs")
        self.assertIn('await import("../components/supply/Country.tsx")', figures)   # the page's figures are the site's own code's
        self.assertIn("createElement(S.Country, { q })", figures)                    # read through the site's own reader

    def test_no_dash_in_what_was_written(self):
        for rel in WRITTEN:
            text = src(*rel.split("/"))
            for d in DASHES:
                self.assertNotIn(d, text, rel)

    def test_the_method_note_holds_the_rules_the_replication_needed(self):
        note = src("docs", "methods", "supply_and_trade.md")
        part = note[note.index("## The whole country (session 8430"):note.index("## The cross-checks (session 7018")]
        for said in ("The rules above, made exact (session 8460)", "before rounding is 10 or more", "file's value unturned", "no net flow",
                     "else the newest year they hold before", "Five hovers completed (session 8460)", "The replication (session 8460)",
                     "replication/supply/replicate_regions.py", "33,132 of 33,132", "--same-flow", "docs/reviews/supply-regions-read-2026-11-19.md"):
            self.assertIn(said, part, said)

    def test_the_fixes_are_hovers_and_the_owners_switches_stand(self):
        code = src("site", "components", "supply", "Country.tsx")
        self.assertIn("export const abroadWhy = ", code)
        self.assertIn("files Form EIA-930: a flow across the border stands by the report of the balancing authorities of the United States alone.", code)
        self.assertIn("export const SHOWN = { importShare: false };", code)
        self.assertIn("export const REGIONS_HELD: string[] = [];", code)
        self.assertIn('"/supply": "review"', src("site", "lib", "release.ts"))

    def test_the_read_names_its_reader_its_cases_and_what_waits(self):
        read = src("docs", "reviews", "supply-regions-read-2026-11-19.md")
        for said in ("## The reader and the five cases", "## State on 19 November 2026", "## Gaps found before any file", "waits for the files",
                     "https://erw-flame.vercel.app/supply?region=ten&b=car&year=2025#whole-country", "Hourly Electric Grid Monitor", "Electric Power Monthly"):
            self.assertIn(said, read, said)
        self.assertNotRegex(read, r"\b(should|recommend)\b")


if __name__ == "__main__":
    unittest.main()
