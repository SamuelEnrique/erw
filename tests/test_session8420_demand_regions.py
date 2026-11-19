"""Session 8420 (chain 503, part C): /demand for the whole country.

/demand gains a fourth view, "The whole country" (site/components/demand/Country.tsx, ?view=country): any of EIA's
thirteen regions of the lower 48 and any balancing authority, two side by side, from the data machine's page files
(site/data/regions/index.json, demand/<region>.json, demand/ba/<code>.json; the contract is
docs/state/page_files_regions.md). Held here:

- add, never change: outside the new tab, each of 50 addresses of the page is byte for byte what the branch's base drew
  (site/scripts/test-demand-pin.mjs);
- the view drawn to HTML from a fixture in the contract's form, and the whole page with and without a file
  (site/scripts/test-demand-regions.mjs);
- the rules of the chain in the source: the page's own charts and no second versions of them, no fixture in the site's
  folder, no dash, the page still in review, the method note says what the view shows.
"""
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
NEW = ["site/lib/countrydemand.ts", "site/components/demand/Country.tsx", "site/components/demand/Growth.tsx", "site/scripts/regions-fixture-demand.mjs",
       "site/scripts/demand-pages.mjs", "site/scripts/test-demand-regions.mjs", "site/scripts/test-demand-pin.mjs"]
CHARTS = ("YearsChart", "Heat", "ChangeBars")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def shown(code):
    """A source file without its comments."""
    return re.sub(r"//.*|/\*\*?[\s\S]*?\*/", "", code)


def node(script, *args):
    env = {k: v for k, v in os.environ.items() if k != "ERW_REGIONS_DIR"}
    return subprocess.run([NODE, "--import", "./scripts/battery-awards-page-register.mjs", script, *args], cwd=SITE, capture_output=True, text=True,
                          encoding="utf-8", timeout=1200, env=env)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    def check(self, r, least):
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertNotIn("FAIL", r.stdout)
        m = re.search(r"(\d+) of (\d+) passed", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= least, r.stdout[-500:])

    def test_nothing_the_page_showed_moves(self):
        r = node("scripts/test-demand-pin.mjs")
        said = [line for line in r.stdout.splitlines() if line.startswith("DATA MOVED")]
        if said and r.returncode == 0:
            # the data machine rebuilt a file the page reads: a page that differs cannot be told from one that moved with it
            self.skipTest(said[0])
        self.check(r, 101)

    def test_the_pin_fails_a_page_that_moved_and_says_so_when_its_data_moved(self):
        pin = json.loads(src("site", "scripts", "pins", "demand-page-8420.json"))
        current = {}
        for rel in pin["data"]:
            with open(os.path.join(SITE, *rel.split("/")), encoding="utf-8", newline="") as f:
                current[rel] = hashlib.sha256(f.read().replace("\r\n", "\n").encode("utf-8")).hexdigest()
        moved_page = copy.deepcopy(pin)
        moved_page["data"] = dict(current)
        moved_page["addresses"]["plain"]["sha256"] = "0" * 64
        moved_both = copy.deepcopy(moved_page)
        moved_both["data"]["data/demand_growth.json"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            for name, body in (("page.json", moved_page), ("both.json", moved_both)):
                with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
                    json.dump(body, f)
            # a page that differs while its data is what the pin was drawn on: a failure
            r = node("scripts/test-demand-pin.mjs", "--pin", os.path.join(tmp, "page.json"), "--only", "plain")
            self.assertEqual(r.returncode, 1, r.stdout[-1500:] + r.stderr[-800:])
            self.assertIn("FAIL plain: outside what was added, the page is as it was", r.stdout)
            self.assertNotIn("DATA MOVED", r.stdout)
            # the same page once a data file has moved: said, with the file's name, and nothing failed
            r = node("scripts/test-demand-pin.mjs", "--pin", os.path.join(tmp, "both.json"), "--only", "plain")
            self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-800:])
            self.assertIn("skip plain: the page differs and its data moved since the pin", r.stdout)
            self.assertIn("DATA MOVED: data/demand_growth.json is not what the pin was drawn on", r.stdout)
            self.assertNotIn("FAIL", r.stdout)

    def test_the_whole_country_view(self):
        r = node("scripts/test-demand-regions.mjs")
        self.check(r, 93)
        for held in ("the table of regions has the thirteen by name, the six new ones marked",
                     "every region and every balancing authority that files demand can be chosen by its name",
                     "the hover of each difference says why, in the data machine's own sentence",
                     "the view draws no chart of its own: every chart is one the site already had",
                     "with no file the view says not built yet for each place and for the index",
                     "a fixture in the site's own folder is refused: the index and the files",
                     "a file that is not public: every cell of the place blank with license needed on hover"):
            self.assertIn(held, r.stdout)


class TheSource(unittest.TestCase):
    def test_the_pin_holds_fifty_addresses_written_from_the_base(self):
        pin = json.loads(src("site", "scripts", "pins", "demand-page-8420.json"))
        self.assertRegex(pin["from_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(len(pin["addresses"]), 50)
        names = set(pin["addresses"])
        for name in ("plain", "metered-ercot-avg", "metered-us48-ytd", "weather", "weather-night-2026", "consumption", "odd-view"):
            self.assertIn(name, names)
        for page in pin["addresses"].values():
            self.assertRegex(page["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(page["bytes"], 5000)
        self.assertEqual(pin["addresses"]["plain"]["sha256"], pin["addresses"]["metered-ercot-avg"]["sha256"])
        # the data the pages were drawn on, by its hash: the pin holds the code while the data is what it was
        self.assertEqual(sorted(pin["data"]), ["data/data_faults.json", "data/demand_growth.json", "data/demand_weather.json", "data/license_status.json",
                                               "data/markets.json", "data/site.json"])
        for h in pin["data"].values():
            self.assertRegex(h, r"^[0-9a-f]{64}$")

    def test_the_page_mounts_the_view_once_and_the_three_before_it_stand(self):
        page = src("site", "app", "demand", "page.tsx")
        self.assertEqual(page.count("<CountryView "), 1)
        self.assertIn('if (view === "country") {', page)
        self.assertIn('view === "weather" ? <WeatherView q={q} /> : <MeteredView q={q} />', page)
        self.assertIn("<ConsumptionView />", page)
        self.assertEqual(page.count('<Tabs page="/demand" active={view} />'), 3)
        self.assertLess(page.index('if (view === "consumption") {'), page.index('if (view === "country") {'))

    def test_the_tab_and_the_view_are_added_after_the_three(self):
        tabs = src("site", "lib", "tabs.ts")
        self.assertIn('["metered", "As metered"], ["weather", "With the weather taken out"], ["consumption", "Consumption"], ["country", "The whole country"]]', tabs)
        views = src("site", "lib", "demandpage.ts")
        self.assertIn('export const VIEWS = [["metered", "As metered"], ["weather", "With the weather taken out"], ["consumption", "Consumption"], ["country", "The whole country"]] as const;', views)
        self.assertNotIn("country", src("site", "components", "tool", "Tabs.tsx"))   # the shared tabs component is as it was

    def test_the_charts_are_the_pages_own_and_there_is_no_second_version(self):
        charts = src("site", "components", "demand", "Growth.tsx")
        page = src("site", "app", "demand", "page.tsx")
        view = src("site", "components", "demand", "Country.tsx")
        for name in CHARTS:
            self.assertEqual(charts.count(f"export function {name}("), 1, name)
            self.assertNotIn(f"function {name}(", page)
            self.assertNotIn(f"function {name}(", view)
            self.assertIn(f"<{name} ", page)
            self.assertIn(f"<{name} ", view)
        self.assertIn('import { ChangeBars, DOWN, Heat, UP, YearsChart } from "@/components/demand/Growth";', page)
        self.assertIn('import { ChangeBars, DOWN, Heat, UP, YearsChart } from "@/components/demand/Growth";', view)
        self.assertIn("export function Explained(", src("site", "components", "demand", "Weather.tsx"))
        self.assertIn("<Explained ", view)
        for mark in ("<svg", "<rect", "<path", "<line "):
            self.assertNotIn(mark, shown(view), mark)
        # every chart of the view sits in a frame that answers the mouse: the page's hover frame, or the site's time chart
        self.assertEqual(len(re.findall(r"<Hover><(YearsChart|Heat|ChangeBars|Explained) ", view)), 5)
        self.assertEqual(len(re.findall(r"<(YearsChart|Heat|ChangeBars|Explained) ", view)), 5)
        self.assertIn("<TimeChart ", view)

    def test_the_view_reads_the_files_through_the_one_reader(self):
        lib = src("site", "lib", "countrydemand.ts")
        self.assertIn("readRegionFile<DemandPlaceFile>(placeFilePath(p))", lib)
        self.assertIn('readRegionFile<IndexFile>("index.json")', lib)
        self.assertIn('from "./countryfiles"', lib)
        self.assertIn(r"/^(ba-)?([a-z0-9]{2,8})$/", lib)   # an address value becomes a file name: letters and digits only
        for f in ("site/lib/countrydemand.ts", "site/components/demand/Country.tsx"):
            code = shown(src(*f.split("/")))
            self.assertNotIn("readFileSync", code, f)
            self.assertNotIn("supabase", code.lower(), f)
            self.assertNotIn("fetch(", code, f)

    def test_the_server_trace_names_the_files_the_view_reads(self):
        # a file read by a name built at request time is not in the deployed function unless the folder is named
        # (session 138 found it for /cost-of-power); the older entries stand as they were
        config = src("site", "next.config.ts")
        self.assertIn('"/demand": ["./data/regions/index.json", "./data/regions/demand/**/*.json"],', config)
        self.assertIn('outputFileTracingIncludes: { "/cost-of-power": ["./data/datacenter/*.json"]', config)

    def test_part_b_is_not_touched(self):
        # the three pages' branches stay free of conflicts: this session's code is in files of its own
        self.assertIn("export function readRegionFile<T>(rel: string): T | null {", src("site", "lib", "countryfiles.ts"))
        self.assertNotIn("8420", src("site", "lib", "countryfiles.ts"))
        self.assertNotIn("8420", src("site", "app", "events", "WholeCountry.tsx"))
        self.assertNotIn("8420", src("site", "scripts", "regions-fixture.mjs"))

    def test_no_dash_in_what_was_written(self):
        for f in NEW + ["tests/test_session8420_demand_regions.py", "docs/methods/demand_growth.md", "site/lib/demandpage.ts", "site/lib/tabs.ts",
                        "site/lib/demandgrowth.ts", "site/lib/demandweather.ts", "site/components/demand/Weather.tsx", "site/app/demand/page.tsx"]:
            text = src(*f.split("/"))
            for d in DASHES:
                self.assertNotIn(d, text, f)

    def test_no_fixture_in_the_sites_folder(self):
        folder = os.path.join(SITE, "data", "regions")
        if not os.path.isdir(folder):
            return
        for base, _dirs, files in os.walk(folder):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(base, name), encoding="utf-8") as f:
                        head = f.read(4000)
                    self.assertNotIn('"fixture"', head, name)

    def test_the_fixture_says_it_is_not_data(self):
        fx = src("site", "scripts", "regions-fixture-demand.mjs")
        self.assertIn("not data", fx)
        self.assertEqual(fx.count("fixture: FIXTURE"), 2)   # the index and each place's file
        self.assertIn('"fixture" in v && v.fixture && !process.env.ERW_REGIONS_DIR', src("site", "lib", "countryfiles.ts"))

    def test_the_page_stays_in_review(self):
        release = src("site", "lib", "release.ts")
        self.assertIn('"/demand": "review"', release)
        self.assertNotIn('"/demand": "live"', release)

    def test_no_estimate_no_ledger_and_no_advice_in_the_view(self):
        code = shown(src("site", "components", "demand", "Country.tsx") + src("site", "lib", "countrydemand.ts")).lower()
        for word in ("donor", "taker", "covered by imports", "should", "recommend"):
            self.assertNotIn(word, code, word)

    def test_each_default_is_said_with_whose_choice_it_is(self):
        lib = src("site", "lib", "countrydemand.ts")
        view = src("site", "components", "demand", "Country.tsx")
        self.assertIn("This page's own choice (session 8420); no publisher's default stands behind it.", lib)
        self.assertIn("Default: every day held, this page's own choice (session 8420).", view)
        self.assertIn("this page's own choice (session 8420); every day is in the chart above and in the file.", view)
        self.assertIn("Defaults: the year's energy, in the last whole year held, as the weather view of the seven grids opens.", view)

    def test_the_method_note_says_what_the_view_shows(self):
        note = src("docs", "methods", "demand_growth.md")
        self.assertIn("\n## The whole country (session 8420, 19 November 2026)\n", note)
        part = note[note.index("## The whole country (session 8420"):]
        for said in ("/demand?view=country", "site/data/regions/", "docs/state/page_files_regions.md", "not built yet", "What it computes", "What it does not do",
                     "no ledger", "Tennessee and the Carolinas", "Both figures stand", "the Southeast, Florida, the Carolinas, Tennessee, the Northwest and the Southwest",
                     "site/scripts/test-demand-pin.mjs", "Not seen in a browser"):
            self.assertIn(said, part, said)

    def test_the_report_is_written(self):
        report = src("archive", "sessions", "SESSION_8420_REPORT.md")
        for head in ("## What was built", "## The files it waits for", "## Add, never change: how it is held", "## What to review", "## Needs the key",
                     "## Decisions made without you", "## For Samuel's ruling"):
            self.assertIn(head, report, head)
        self.assertIn("https://erw-flame.vercel.app/demand?view=country", report)
        for d in DASHES:
            self.assertNotIn(d, report)


if __name__ == "__main__":
    unittest.main()
