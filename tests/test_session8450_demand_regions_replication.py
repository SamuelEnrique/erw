"""Session 8450 (chain 503, part E): the done line of "The whole country", the fourth view of /demand.

replication/demand/replicate_regions.py recomputes, from the page files alone and by the method note's rules, every
figure the view prints, beside the figure the site's own code draws (site/scripts/demand-regions-figures.mjs). Held
here, without a build and without any warehouse table:

- on the test's fixture (values made by a rule, not data) every figure the view draws is recomputed, N of N; a figure
  moved by one in its last digit is caught (a checked number, a chart's hover, a point of the chart of days, a figure
  of the second place); a figure the page drops and a figure the rule does not give are caught;
- a file that is not public gives no figure and is not recomputed; a file that breaks the contract (a day counted
  whole on two of its hours) is said as a note, and fails the run only with --strict;
- on the site as it stands the replication runs and says what it finds: no file yet (nothing to recompute), or every
  figure of the places drawn;
- the five faults the reader's read fixed in the view (docs/reviews/demand-regions-read-2026-11-19.md, rows 1 to 5):
  the lists held to a phone's width, a unit and a hover on each head of the check, a grid drawn as a balancing
  authority linked to its own view with a hover that names both files, a summary with no growth that says why, and
  since when the hours left out are counted.
"""
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
REP = os.path.join(ROOT, "replication", "demand", "replicate_regions.py")
FIGURES = "scripts/demand-regions-figures.mjs"
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))


def node(args, regions_dir=None):
    env = {k: v for k, v in os.environ.items() if k != "ERW_REGIONS_DIR"}
    if regions_dir:
        env["ERW_REGIONS_DIR"] = regions_dir
    return subprocess.run([NODE, "--import", "./scripts/battery-awards-page-register.mjs", FIGURES, *args], cwd=SITE, capture_output=True, text=True,
                          encoding="utf-8", timeout=1200, env=env)


def replicate(*args):
    return subprocess.run([sys.executable, REP, *args], capture_output=True, text=True, encoding="utf-8", timeout=600)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def zones():
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo("America/New_York")
        return True
    except Exception:
        return False


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw-8450-")
        cls.fx = os.path.join(cls.tmp, "fx")
        r = node(["--fixture", cls.fx])
        assert r.returncode == 0, r.stderr[-800:]
        cls.figures = os.path.join(cls.tmp, "figures.json")
        r = node([cls.figures], regions_dir=cls.fx)
        assert r.returncode == 0, r.stderr[-800:]
        with open(cls.figures, encoding="utf-8") as f:
            cls.page = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def changed(self, name, change):
        """The figures file with one change made to it, written beside it."""
        page = json.loads(json.dumps(self.page))
        change(page)
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(page, f)
        return path

    @staticmethod
    def view(page, kind, a, b=""):
        return next(v for v in page["views"] if v["kind"] == kind and v["a"] == a and v["b"] == b)

    def test_every_figure_of_the_fixture_is_recomputed(self):
        r = replicate("--figures", self.figures, "--files", self.fx)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-800:])
        m = re.search(r"(\d+) of (\d+) figures over (\d+) views of 20 places", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 19000 and int(m.group(3)) >= 160, r.stdout[-600:])
        self.assertNotIn("FAIL", r.stdout)
        for kind in ("place", "days", "figure", "year", "pair"):
            self.assertRegex(r.stdout, rf"{kind}: (\d+) of \1 figures over \d+ views")
        self.assertRegex(r.stdout, r"the tables at the foot: 14 of 14 figures")
        self.assertRegex(r.stdout, r"the files against themselves: (\d+) of \1 checks agree")

    def test_the_figures_file_holds_what_the_view_shows(self):
        # Tennessee is place number 12 of the fixture: every value below is the fixture's rule, worked here
        ten = self.view(self.page, "place", "ten")["figures"]
        self.assertEqual(ten["cd|a|sum|avg1"], "12,600")
        self.assertEqual(ten["cd|a|day|top_gwh"], f"{24 * (12000 + 160) / 1000:.1f}")
        self.assertEqual(ten["cd|a|pt|2024-12-30|avg"], "12,050")          # day 5: 24 (12000 + 50) MWh over 24 hours
        self.assertEqual(ten["cd|a|pt|2024-12-30|peak"], "12,550")
        self.assertNotIn("cd|a|pt|2024-12-28|avg", ten)                    # day 3 holds 20 of its hours: no point, never a filled one
        self.assertNotIn("cd|a|pt|2024-12-28|peak", ten)
        self.assertEqual((ten["cd|a|tip|cell|12|23|pct"], ten["cd|a|tip|cell|12|23|mw"]), ("+8.30", "+35"))
        self.assertNotIn("cd|a|tip|cell|2|3|pct", ten)                     # the cell the fixture leaves out
        self.assertEqual((ten["cd|a|tip|month|12|pct"], ten["cd|a|tip|hour|23|pct"]), ("+6.00", "+2.30"))
        self.assertEqual((ten["cd|a|tip|year|2025|avg"], ten["cd|a|tip|year|2025|peak"]), ("12,600", "25,200"))
        self.assertEqual((ten["cd|a|tip|w|2025|g"], ten["cd|a|tip|w|2025|w"], ten["cd|a|tip|w|2025|u"], ten["cd|a|tip|w|2025|pm"]), ("+16.0", "+1.0", "+15.0", "2.0"))
        self.assertEqual(sum(1 for k in ten if "|tip|cell|" in k), 2 * 287)
        self.assertEqual((self.page["index"]["figures"]["index|SE|bas"], self.page["index"]["figures"]["index|bas"]), ("3", "8"))
        kinds = [v["kind"] for v in self.page["views"]]
        self.assertEqual((kinds.count("place"), kinds.count("pair")), (20, 2))
        self.assertEqual(self.view(self.page, "days", "ten")["days"], "2024")
        year = next(v for v in self.page["views"] if v["kind"] == "year" and v["a"] == "ten" and v["year"] == "2023")
        self.assertEqual(sorted(year["figures"]), ["cd|a|tip|w|2023|g", "cd|a|tip|w|2023|pm", "cd|a|tip|w|2023|u", "cd|a|tip|w|2023|w"])
        pair = self.view(self.page, "pair", "tex", "ba-erco")
        self.assertEqual((pair["figures"]["cd|a|alike|apart"], pair["figures"]["cd|b|sum|avg0"]), ("7", "24,000"))
        self.assertFalse(any("|pt|" in k for k in pair["figures"]))
        self.assertTrue(all(not v["clashes"] for v in self.page["views"]))

    def test_a_figure_moved_by_one_in_its_last_digit_is_caught(self):
        def move(page):
            ten = self.view(page, "place", "ten")["figures"]
            self.assertEqual(ten["cd|a|sum|avg_growth"], "+5.00")
            ten["cd|a|sum|avg_growth"] = "+5.01"
            ten["cd|a|tip|cell|12|23|mw"] = "+36"
            ten["cd|a|pt|2024-12-30|avg"] = "12,051"
            both = self.view(page, "pair", "ten", "car")["figures"]
            self.assertEqual(both["cd|b|new|2025-01-10|gwh"], "51.8")
            both["cd|b|new|2025-01-10|gwh"] = "51.9"
        r = replicate("--figures", self.changed("moved.json", move), "--files", self.fx)
        self.assertEqual(r.returncode, 1, r.stdout[-800:])
        for key in ("place ten cd|a|sum|avg_growth", "place ten cd|a|tip|cell|12|23|mw", "place ten cd|a|pt|2024-12-30|avg", "pair ten and car cd|b|new|2025-01-10|gwh"):
            self.assertIn(f"FAIL {key}", r.stdout)
        self.assertEqual(r.stdout.count("FAIL"), 4, r.stdout[-1200:])

    def test_a_figure_the_page_drops_is_caught(self):
        def drop(page):
            del self.view(page, "place", "ten")["figures"]["cd|a|day|low_gwh"]
            del self.view(page, "figure", "car")["figures"]["cd|a|h|hour"]
        r = replicate("--figures", self.changed("gone.json", drop), "--files", self.fx)
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"FAIL place ten cd\|a\|day\|low_gwh: ours 288\.0+, not on the page")
        self.assertRegex(r.stdout, r"FAIL figure car \w+ cd\|a\|h\|hour: ours [\d.]+, not on the page")

    def test_a_figure_the_rule_does_not_give_is_caught(self):
        def add(page):
            self.view(page, "place", "ba-grid")["figures"]["cd|a|sum|avg_growth"] = "+1.00"   # its record begins in 2022: no growth since 2019
            self.view(page, "place", "ten")["clashes"].append("cd|a|sum|avg0")
        r = replicate("--figures", self.changed("more.json", add), "--files", self.fx)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL place ba-grid cd|a|sum|avg_growth: the page shows +1.00, the file gives no figure by the note's rule", r.stdout)
        self.assertIn("FAIL place ten cd|a|sum|avg0: drawn twice with two values", r.stdout)

    def other_fixture(self, name, code, change):
        """A copy of the fixture's folder with one file changed, and its figures for the places named."""
        folder = os.path.join(self.tmp, name)
        shutil.copytree(self.fx, folder)
        path = os.path.join(folder, "demand", f"{code}.json")
        with open(path, encoding="utf-8") as f:
            file = json.load(f)
        change(file)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(file, f)
        figures = os.path.join(self.tmp, f"{name}.json")
        r = node([figures, "--places", f"{code},tex"], regions_dir=folder)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        return folder, figures

    def test_a_file_that_is_not_public_gives_no_figure_and_is_not_recomputed(self):
        folder, figures = self.other_fixture("held", "ten", lambda f: f.update(license="internal"))
        with open(figures, encoding="utf-8") as f:
            page = json.load(f)
        self.assertTrue(page["places"]["ten"]["held"])
        ten = self.view(page, "place", "ten")
        self.assertEqual((ten["figures"], ten["states"]), ({}, {"a": "held"}))
        self.assertEqual([v["kind"] for v in page["views"] if v["a"] == "ten"], ["place"])
        r = replicate("--figures", figures, "--files", folder)
        self.assertEqual(r.returncode, 0, r.stdout[-800:])
        self.assertIn("ten: the file is not public, not recomputed", r.stdout)
        self.assertRegex(r.stdout, r"(\d+) of \1 figures over \d+ views of 1 places")
        ten["figures"]["cd|a|sum|avg0"] = "12,000"                           # a held figure drawn is a failure
        with open(figures, "w", encoding="utf-8") as f:
            json.dump(page, f)
        r = replicate("--figures", figures, "--files", folder)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL place ten cd|a|sum|avg0", r.stdout)

    @unittest.skipUnless(zones(), "this Python holds no time zone data")
    def test_a_day_counted_whole_on_two_of_its_hours_is_said(self):
        # the fault read in the data machine's builder on its branch (data request 328): the first and the last local day
        # of a series hold only the hours inside the record, and are written as whole days
        def short(file):
            file["daily"]["hours"][0] = 2
            file["daily"]["demand_mwh"][0] = 4000
        folder, figures = self.other_fixture("short", "car", short)
        r = replicate("--figures", figures, "--files", folder)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:])                  # the page shows what the file gives
        self.assertNotIn("FAIL", r.stdout)
        self.assertIn("note car: 1 days whose demand is held without all the day's hours used, or not held with all of them", r.stdout)
        m = re.search(r"the files against themselves: (\d+) of (\d+) checks agree", r.stdout)
        self.assertTrue(m and int(m.group(2)) - int(m.group(1)) == 1, r.stdout[-400:])
        self.assertEqual(replicate("--figures", figures, "--files", folder, "--strict").returncode, 1)

    def test_a_grid_drawn_as_a_balancing_authority_is_set_beside_the_as_metered_view(self):
        metered = os.path.join(self.tmp, "metered.json")
        with open(metered, "w", encoding="utf-8") as f:   # ERCO is place number 24 of the fixture: 24,600 MW in 2025, 24,500 in 2024
            json.dump({"areas": {"ERCO": {"years": {"2025": {"avg_demand_mw": 24600.0}, "2024": {"avg_demand_mw": 24000.0}}}}}, f)
        r = replicate("--figures", self.figures, "--files", self.fx, "--metered", metered)
        self.assertEqual(r.returncode, 0, r.stdout[-800:])
        self.assertIn("note ba-erco 2024: this view's file gives 24500 MW, the as-metered view's 24000.0 MW (+2.08 percent)", r.stdout)
        self.assertIn("the seven grids as balancing authorities beside the as-metered view: 1 of 2 year averages are equal (both stand)", r.stdout)

    def test_on_the_site_as_it_stands(self):
        out = os.path.join(self.tmp, "site.json")
        r = node([out, "--places", "ten,car,ba-tva"])
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        r = replicate("--figures", out)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        with open(out, encoding="utf-8") as f:
            page = json.load(f)
        if not any(p.get("file") for p in page["places"].values()):
            self.assertIn("no place's file is on the site yet", r.stdout)
            self.assertEqual(page["views"], [])
        else:
            self.assertRegex(r.stdout, r"(\d+) of \1 figures over \d+ views of \d+ places")

    def test_bad_input(self):
        self.assertEqual(replicate("--figures", os.path.join(self.tmp, "none.json")).returncode, 2)
        self.assertEqual(node([]).returncode, 2)
        self.assertEqual(node(["--draw"]).returncode, 2)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheReadersFaults(unittest.TestCase):
    """The five faults the reader's read fixed in the view, each held on the view as drawn from the fixture."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw-8450-read-")
        cls.fx = os.path.join(cls.tmp, "fx")
        assert node(["--fixture", cls.fx]).returncode == 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def draw(self, address):
        out = os.path.join(self.tmp, "view.html")
        r = node(["--draw", out, "--address", address], regions_dir=self.fx)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        with open(out, encoding="utf-8") as f:
            return f.read().replace("&#x27;", "'").replace("&amp;", "&")

    def test_row_1_the_lists_are_held_to_the_width_of_the_form(self):
        html = self.draw("")
        form = re.search(r'<form [^>]*class="([^"]*)"[^>]*data-cd-form="1"', html).group(1)
        for rule in ("[&_label]:min-w-0", "[&_label]:max-w-full", "[&_select]:max-w-full", "flex-wrap"):
            self.assertIn(rule, form.split())
        self.assertEqual(html.count("<select"), 3)
        self.assertEqual(len(re.findall(r"<label[^>]*>[^<]*<select", html)), 3)   # each list stands in a label, which the rule holds

    def test_row_2_each_head_of_the_check_says_its_unit_on_hover(self):
        html = self.draw("a=se&b=fla&figure=summer")
        heads = dict((m[1], m[0]) for m in re.findall(r'<span title="([^"]*)" data-cd-head="([^"]+)"', html))
        for year in ("2019", "2020", "2021"):
            self.assertRegex(heads[f"out-{year}"], rf"^The growth of the summer peak in {year} that the weather does not explain .* percent\.$")
        self.assertIn("as a percent of the hour's demand", heads["out-hour"])
        self.assertIn("as a percent of the day's demand", heads["out-day"])
        self.assertTrue(heads["pm"].endswith("In percent, as the column before it."))
        self.assertIn(">On a day left out</span>", html)                    # the words of the heads did not move
        self.assertIn(">Error on an hour left out, percent</span>", html)

    def test_row_3_a_grid_drawn_as_a_balancing_authority_names_both_files(self):
        html = self.draw("a=tex&b=ba-erco")
        self.assertEqual(html.count('data-cd-grid="'), 1)                    # the authority, not EIA's region beside it
        m = re.search(r'data-cd-grid="ERCO"><a href="/demand\?area=ercot">ERCOT as metered</a> <span[^>]*title="([^"]*)"[^>]*>another file</span>', html)
        self.assertTrue(m, "the link to the grid's own view, with its hover")
        why = m.group(1)
        self.assertIn("site/data/regions/demand/ba/erco.json", why)
        self.assertIn("docs/methods/demand_growth.md", why)
        self.assertTrue(why.endswith("Both stand; neither is corrected to the other."))
        self.assertNotIn("data-cd-grid=", self.draw("a=ba-tva&b=ten"))       # an authority that is none of the seven grids

    def test_row_4_a_summary_with_no_growth_says_why(self):
        html = self.draw("a=ba-grid&b=ten")                                  # the fixture's Gridforce begins in 2022
        m = re.search(r'data-cd-no-base="a"><span[^>]*title="([^"]*)"[^>]*>no growth since 2019</span>', html)
        self.assertTrue(m, "the words after the sentence, with their hover")
        self.assertIn("holds no whole year 2019: its first whole year is 2022", m.group(1))
        self.assertEqual(html.count("data-cd-no-base="), 1)                  # Tennessee, whole from 2019, has its percent and no such words
        self.assertNotIn('data-n="cd|a|sum|avg_growth"', html)
        self.assertIn('data-n="cd|b|sum|avg_growth"', html)

    def test_row_5_the_hours_left_out_say_since_when(self):
        self.assertIn("The hours left out are counted from 1 January of the base year to the file's last hour.", self.draw(""))


class TheSource(unittest.TestCase):
    def test_written_from_the_note_not_from_the_pages_code(self):
        code = src("replication", "demand", "replicate_regions.py")
        body = code.split('"""', 2)[2]
        for word in ("countrydemand", "Country.tsx", "demandgrowth", "import subprocess", "import numpy", "import pandas"):
            self.assertNotIn(word, body)
        for d in DASHES:
            self.assertNotIn(d, code)

    def test_the_note_gives_every_rule_the_replication_uses(self):
        note = src("docs", "methods", "demand_growth.md")
        section = note.split("## The whole country (session 8420, 19 November 2026)")[1]
        for words in ("Every figure, in the view's order (session 8450)", "The replication (session 8450)", "replication/demand/replicate_regions.py",
                      "site/scripts/demand-regions-figures.mjs", "the first in the order of months then hours", "the seven newest",
                      "half the last digit shown", "docs/reviews/demand-regions-read-2026-11-19.md"):
            self.assertIn(words, section)
        for d in DASHES:
            self.assertNotIn(d, section)

    def test_the_charts_way_of_writing_a_value_is_the_sites(self):
        chart = re.search(r"^const num = \(v: number\) => (.*)$", src("site", "components", "TimeChart.tsx"), re.M).group(1)
        self.assertIn(f"const num = (v) => {chart}", src("site", "scripts", "demand-regions-figures.mjs"))

    def test_the_read_names_its_reader_its_cases_and_what_waits(self):
        read = src("docs", "reviews", "demand-regions-read-2026-11-19.md")
        for words in ("## The reader and the five cases", "## State on 19 November 2026", "## Gaps found before any file", "waits for the files"):
            self.assertIn(words, read)
        self.assertEqual(len(re.findall(r"^\d\. \*\*", read, re.M)), 5)
        self.assertGreaterEqual(len(re.findall(r"^\| \d+ \|", read, re.M)), 6)
        for d in DASHES:
            self.assertNotIn(d, read)

    def test_no_dash_in_the_scripts_and_no_do_file_before_the_files(self):
        for rel in (("site", "scripts", "demand-regions-figures.mjs"), ("tests", "test_session8450_demand_regions_replication.py"), ("site", "components", "demand", "Country.tsx")):
            for d in DASHES:
                self.assertNotIn(d, src(*rel), rel[-1])
        # a do-file's expected values are real figures: none is written while no file is on the site
        if not os.path.exists(os.path.join(SITE, "data", "regions", "index.json")):
            self.assertFalse(os.path.exists(os.path.join(ROOT, "replication", "demand", "replicate_regions.do")))


if __name__ == "__main__":
    unittest.main()
