"""Session 152: loose work landed.

1. The demand-with-weather page of sessions 126 and 129 (branch wip/129-demand-weather-finished), merged onto main and
   folded into the one demand page: /demand has two views, both in the address; /demand/weather redirects to the
   second; every chart sits in a hover frame; no method or limitations prose stands on the face (it is the hover of a
   short placeholder, and the Method notes hold the method); nothing the two pages showed is dropped; the page stays
   in review. The merge kept both sides' rows in the generated metadata and doubled none.
2. The weekly chart chooser's choosing step can be run without writing anything and without a model call
   (warehouse/analysis/run.py --dry-run).

Nothing here asks a publisher, a model or Supabase for anything, and nothing here changes the environment. The tests
of the built page are site/scripts/check-demand.mjs and site/scripts/check-demand-weather.mjs, which need a served
site; the tests here read the source and the site's own copies, and skip where a machine lacks node or a table.
"""
import contextlib
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
WROTE = [("site", "app", "demand", "page.tsx"), ("site", "components", "demand", "Weather.tsx"), ("site", "components", "demand", "Hover.tsx"),
         ("site", "components", "demand", "Hint.tsx"), ("site", "lib", "demandpage.ts"), ("site", "lib", "demandweather.ts"),
         ("site", "scripts", "check-demand.mjs"), ("site", "scripts", "check-demand-weather.mjs"), ("site", "next.config.ts"),
         ("docs", "methods", "demand_growth.md"), ("docs", "methods", "demand_weather.md"), ("warehouse", "analysis", "run.py"),
         ("tests", "test_session152.py")]
WEATHER_TABLES = ("noaa_grid_weather_stations", "noaa_grid_weather_hourly", "noaa_grid_weather_daily", "eia930_demand_weather",
                  "noaa_station_weather_hourly", "census_metro_population")
WEATHER_SOURCES = ("noaa:isd_lite", "noaa:lcd_v2", "erw:demand_weather", "census:popest_cbsa")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def keys(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as f:
        return [row[0] for row in csv.reader(f) if row][1:]


class OnePageOneAddress(unittest.TestCase):
    def test_the_weather_page_is_a_view_of_the_demand_page_and_has_no_route_of_its_own(self):
        self.assertFalse(os.path.exists(os.path.join(SITE, "app", "demand", "weather")))        # one address
        page = src("site", "app", "demand", "page.tsx")
        self.assertIn('view === "weather" ? <WeatherView q={q} /> : <MeteredView q={q} />', page)
        self.assertIn('{ source: "/demand/weather", destination: "/demand?view=weather", permanent: true }', src("site", "next.config.ts"))
        release = src("site", "lib", "release.ts")
        self.assertIn('"/demand": "review"', release)                                           # locked, and it stays so
        self.assertIn('"/demand/weather": "review"', release)                                   # an address typed by hand still has a status
        self.assertNotIn('"/demand": "live"', release)

    def test_the_two_pages_as_they_were_are_kept_and_not_routed(self):
        old = src("site", "app", "_retired", "demand-weather", "page.tsx")
        for words in ("What the remainder is not", "New England under two rules", "How it is computed", "What is not here"):
            self.assertIn(words, old)
        first = src("site", "app", "_retired", "demand-original", "page.tsx")
        for words in ("Weather is not removed.", "How it is computed", "What is not here", "Tennessee Valley Authority"):
            self.assertIn(words, first)

    def test_the_views_and_their_addresses(self):
        d = node("import * as p from './lib/demandpage.ts'; import * as w from './lib/demandweather.ts'; import * as g from './lib/demandgrowth.ts';"
                 "console.log(JSON.stringify({ views: p.VIEWS.map((v) => v[0]), none: p.viewOf({}), odd: p.viewOf({ view: 'mars' }), weather: p.viewOf({ view: 'weather' }),"
                 " hrefs: [p.viewHref('metered'), p.viewHref('weather')], fig: w.href('night', 2026), area: g.href('caiso', 'peak'),"
                 " methods: [p.METHODS.metered.href, p.METHODS.weather.href] }));")
        self.assertEqual(d["views"], ["metered", "weather"])
        self.assertEqual([d["none"], d["odd"], d["weather"]], ["metered", "metered", "weather"])     # what it does not understand is the page as metered
        self.assertEqual(d["hrefs"], ["/demand", "/demand?view=weather"])
        self.assertEqual(d["fig"], "/demand?view=weather&figure=night&year=2026")                    # the whole state is in the address
        self.assertEqual(d["area"], "/demand?area=caiso&rank=peak")                                  # the first view's addresses did not move
        self.assertEqual(d["methods"], ["/data/methods/demand_growth", "/data/methods/demand_weather"])

    def test_the_route_check_reads_the_view_and_the_address_it_was_built_at(self):
        routes = src("site", "scripts", "check-routes.mjs")
        for page in ('"/demand?view=weather"', '"/demand?view=weather&figure=night&year=2026"', '"/demand/weather"', '"/data/methods/demand_weather"', '"/demand?area=caiso&rank=peak"'):
            self.assertIn(page, routes)


class TheFace(unittest.TestCase):
    FILES = (("site", "app", "demand", "page.tsx"), ("site", "components", "demand", "Weather.tsx"))

    def test_every_chart_sits_in_a_hover_frame_and_keeps_no_browser_tooltip(self):
        page, view = (src(*f) for f in self.FILES)
        self.assertEqual(len(re.findall(r"<Hover><(YearsChart|Heat|ChangeBars) ", page)), 4)
        self.assertEqual(len(re.findall(r"<(YearsChart|Heat|ChangeBars) ", page)), 4)                # none drawn outside one
        self.assertEqual(view.count("<Hover><Explained "), 1)
        self.assertEqual(view.count("<Explained "), 1)
        for text in (page, view):
            self.assertNotIn("<title>", text)                                                        # the mark's words are data-tip, shown at once
            self.assertIn("data-tip=", text)
        hover = src("site", "components", "demand", "Hover.tsx")
        self.assertTrue(hover.startswith('"use client";'))
        for words in ('closest("[data-tip]")', 'data-tooltip="1"', "onMouseMove", "onTouchStart", "onMouseLeave"):
            self.assertIn(words, hover)

    def test_no_method_or_limitations_prose_is_folded_on_the_face(self):
        for f in self.FILES:
            text = src(*f)
            self.assertNotIn('<Fold title="How it is computed"', text, f)
            self.assertNotIn('<Fold title="What is not here"', text, f)
            self.assertNotIn("border-l-2 border-accent bg-paper", text, f)                           # the two boxed paragraphs are placeholders now
        self.assertIn("Method, sources and gaps", src(*self.FILES[0]))

    def test_what_the_face_said_is_a_hover_now_and_nothing_is_dropped(self):
        page, view = (src(*f) for f in self.FILES)
        hover = lambda text: " ".join(re.findall(r"why=(?:\{`|\")(.*?)(?:`\}|\") />", text, flags=re.S))
        said = hover(page)
        for words in ("hot summer and cold snap included", "These are differences between years, not a trend line", "a faulty high hour would otherwise be a year's peak",
                      "Nothing is filled", "One hot or mild month colors a whole row", "The Lower 48 is the total, not a grid among the seven",
                      "Its total holds its members' faulty hours", "are set back before anything is computed"):
            self.assertIn(words, said)
        for words in ("Weather is not removed.", "screen|jumps", "screen|zero", "screen|blank", "does not step at the break", "built {file.built.slice(0, 10)}"):
            self.assertIn(words, page)                                                               # the short words, the hours left out, the finding, the stamp
        self.assertNotIn("supabase", page)
        said = hover(view)
        for words in ("The warehouse cannot split them", "the largest miss the method made on a year it had not seen", "never interpolated across more than three hours",
                      "Which rule stands is a ruling still to be made", "the fit is reaching past what it was made on", "holds the lockdowns",
                      "if demand sat on the wrong hour, the fit would match it clearly better moved by an hour"):
            self.assertIn(words, said)
        for words in ("What the remainder is not.", "Census Bureau", "People, 2020", "New England under two rules", "The check: years the fit had not seen",
                      "The stations and their weights", "California across December 2025", "@/data/demand_weather.json", "eq|energy"):
            self.assertIn(words, view)                                                               # every table and every number it showed

    def test_the_method_notes_hold_what_left_the_face(self):
        growth, weather = src("docs", "methods", "demand_growth.md"), src("docs", "methods", "demand_weather.md")
        for words in ("## Which hours are used", "## What the table does not hold", "## On the page"):
            self.assertIn(words, growth)
        for words in ("## What the remainder is not", "## The fit", "## What is not in it", "## On the page"):
            self.assertIn(words, weather)
        for note in (growth, weather):
            self.assertIn("/demand?view=weather", note)

    def test_the_copies_the_views_read_hold_what_the_placeholders_count(self):
        with open(os.path.join(SITE, "data", "demand_growth.json"), encoding="utf-8") as f:
            growth = json.load(f)
        for ba, area in growth["areas"].items():
            self.assertEqual(sorted(area["screened"]), ["blank", "jumps", "not_positive"], ba)       # the hours left out, shown under "Year by year"
        with open(os.path.join(SITE, "data", "demand_weather.json"), encoding="utf-8") as f:
            weather = json.load(f)
        self.assertEqual(len(weather["weather"]["stations"]), 35)
        self.assertEqual(weather["train"], [2019, 2020, 2021])


class TheMerge(unittest.TestCase):
    def test_no_row_is_doubled_in_the_generated_metadata(self):
        for parts in (("warehouse", "metadata", "coverage.csv"), ("warehouse", "metadata", "sources.csv"),
                      ("warehouse", "metadata", "archive_manifest.csv"), ("warehouse", "metadata", "redivis_uploads.csv")):
            ks = keys(*parts)
            self.assertEqual(len(ks), len(set(ks)), parts)
        md = re.findall(r"^\| `([a-z0-9_]+)` \|", src("docs", "coverage.md"), flags=re.M)
        self.assertEqual(len(md), len(set(md)))
        self.assertEqual(sorted(md), sorted(keys("warehouse", "metadata", "coverage.csv")))          # the document lists the tables the file does

    def test_the_branchs_tables_and_sources_are_registered(self):
        cov = keys("warehouse", "metadata", "coverage.csv")
        for t in WEATHER_TABLES + ("ferc_eqr_contracts_history", "ferc_eqr_contract_terms", "ferc_eqr_party_mw", "ferc_eqr_quarter_changes"):
            self.assertIn(t, cov)
            self.assertIn(t, keys("warehouse", "metadata", "archive_manifest.csv"))
            self.assertIn(t, keys("warehouse", "metadata", "redivis_uploads.csv"))
        for s in WEATHER_SOURCES:
            self.assertIn(s, keys("warehouse", "metadata", "sources.csv"))

    def test_the_weather_tables_are_held_and_not_loaded(self):
        import yaml
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        patterns = list(live["full"]) + list(live["recent"]["tables"]) + list(live["select"]) + list(live["review_hold"])
        for t in WEATHER_TABLES:
            self.assertIn(t, live["catalogue_hold"])
            self.assertFalse([p for p in patterns if re.fullmatch(p.strip("^$"), t) or p == t], t)   # not loaded: the view reads the site's own copy
        for s in WEATHER_SOURCES:
            self.assertIn(s, live["sources_hold"])


class Measure:
    """A measure made for the test, with the attributes the chooser asks of a template."""
    PUBLIC, PARAMS, TABLES = True, {}, []
    METHOD = "made for a test"

    def __init__(self, name, about, series, public=True):
        self.NAME, self.TITLE, self.ABOUT, self.COMPARE, self.series, self.PUBLIC = name, name, about, "previous", series, public

    def compute(self, **_):
        ps = self.series
        return {"template": self.NAME, "params": {}, "title": self.TITLE, "subtitle": "sub", "tables": [], "citations": [], "source_line": "",
                "facts": [f"{self.NAME}: a fact."], "chart": {}, "frame": None,
                "headline": {"label": self.NAME, "value": ps[-1][1], "unit": "u", "period": ps[-1][0], "history": ps[:-1]}}

    def render(self, res, size, path=None):
        raise AssertionError("a dry run draws nothing")


def weeks(values, last):
    import pandas as pd
    start = pd.Timestamp(last) - pd.Timedelta(weeks=len(values) - 1)
    return [[f"{(start + pd.Timedelta(weeks=i)).date()} to {(start + pd.Timedelta(weeks=i, days=6)).date()}", float(v)] for i, v in enumerate(values)]


class TheChoosersDryRun(unittest.TestCase):
    """warehouse/analysis/run.py --dry-run: the choosing step alone, printed. No model, no file."""

    @classmethod
    def setUpClass(cls):
        cls.path = list(sys.path)
        for p in ("warehouse/analysis", "warehouse/analysis/templates", "warehouse/news", "warehouse/connectors", "warehouse"):
            sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
        try:
            import run
            import templates
        except Exception as exc:  # a machine without the engine's packages
            sys.path[:] = cls.path
            raise unittest.SkipTest(f"the analysis engine cannot be imported here: {exc!r}")
        cls.engine, cls.templates = run, templates

    @classmethod
    def tearDownClass(cls):
        sys.path[:] = cls.path

    def setUp(self):
        run, templates = self.engine, self.templates
        self.tmp = tempfile.mkdtemp()
        self.saved = (run.DOCS, run.HISTORY, run.INTERNAL, templates.load_all, list(templates.ORDER), run.ip.LOG_DIR, run.ip.write_status,
                      run.draft_note, run.write_json, run.ip.Log)
        run.DOCS, run.HISTORY, run.INTERNAL = self.tmp, os.path.join(self.tmp, "history.csv"), os.path.join(self.tmp, "_i")
        run.ip.LOG_DIR = os.path.join(self.tmp, "_logs")

        def never(*a, **k):
            raise AssertionError("a dry run writes nothing and calls no model")
        run.ip.write_status = run.draft_note = run.write_json = run.ip.Log = never

    def tearDown(self):
        run, templates = self.engine, self.templates
        (run.DOCS, run.HISTORY, run.INTERNAL, templates.load_all, order, run.ip.LOG_DIR, run.ip.write_status, run.draft_note, run.write_json,
         run.ip.Log) = self.saved
        templates.ORDER[:] = order
        shutil.rmtree(self.tmp, ignore_errors=True)

    def dry(self, mods):
        import pandas as pd
        self.templates.load_all = lambda: mods
        self.templates.ORDER[:] = [m.NAME for m in mods]
        y, w, _ = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=1)).date().isocalendar()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.engine.main(["--dry-run", "--week", f"{y}-W{w:02d}"])
        return code, out.getvalue()

    def last_week(self):
        import pandas as pd
        today = pd.Timestamp.now(tz="UTC").normalize().tz_localize(None)
        return str((today - pd.Timedelta(days=today.dayofweek + 7)).date())           # the Monday of the last whole week

    def test_it_prints_every_candidate_the_pick_and_the_runner_up_and_writes_nothing(self):
        calm = [50, 51, 50, 52, 51, 50, 51, 52, 50, 51]
        mods = [Measure("steady", "system", weeks(calm + [51.5], self.last_week())),
                Measure("jumped", "system", weeks(calm + [70], self.last_week())),
                Measure("counted", "coverage", weeks(calm + [500], self.last_week())),
                Measure("short", "system", weeks([1, 2, 9], self.last_week()))]
        code, text = self.dry(mods)
        self.assertEqual(code, 0, text)
        self.assertEqual(os.listdir(self.tmp), [])                                    # no week folder, no history, no log
        self.assertIn("candidates: 4 measures ran, 2 compete, 0 skipped", text)
        self.assertIn("pick: jumped (jumped), by the rule: score 100.0", text)
        self.assertIn("runner-up: steady (steady): score", text)
        self.assertRegex(text, r"counted: score 100\.0.*never chosen: a count of what the ERW itself has collected")
        self.assertRegex(text, r"short: score None.*does not compete: 1 earlier changes, and 8 are needed")
        self.assertIn("It is the largest week-to-week move of the last 10.", text)    # the finding, written by code
        self.assertIn("no model call, nothing written", text)

    def test_a_period_already_shown_does_not_compete_and_the_dry_run_says_why(self):
        calm = [50, 51, 50, 52, 51, 50, 51, 52, 50, 51]
        series = weeks(calm + [70], self.last_week())
        with open(self.engine.HISTORY, "w", encoding="utf-8", newline="\n") as f:
            f.write("week,template,params,period,value,unit\n" + f'2020-W01,jumped,{{}},{series[-1][0]},70.0,u\n')
        before = open(self.engine.HISTORY, encoding="utf-8").read()
        code, text = self.dry([Measure("jumped", "system", series), Measure("steady", "system", weeks(calm + [51.5], self.last_week()))])
        self.assertEqual(code, 0, text)
        self.assertIn("pick: steady", text)
        self.assertRegex(text, r"jumped: score 100\.0.*an earlier week's run already showed this period")
        self.assertEqual(open(self.engine.HISTORY, encoding="utf-8").read(), before)     # read, never written
        self.assertEqual(os.listdir(self.tmp), ["history.csv"])

    def test_the_dry_run_stops_before_the_note_and_every_file(self):
        code = src("warehouse", "analysis", "run.py")
        main = code[code.index("def main(argv=None):"):]
        stop = main.index("if args.dry_run:  # session 152: the choice is made")
        for later in ("draft_note(res, z, log", "mod.render(res, size, os.path.join(out, f))", "write_json(os.path.join(out,", "hist.to_csv(HISTORY"):
            self.assertGreater(main.index(later), stop, later)
        self.assertIn("log = PrintLog()", main)
        self.assertLess(main.index("if args.dry_run:  # a dry run that failed"), main.rindex('ip.write_status("analysis", run_id, [status])'))


class Repository(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in WROTE:
            path = os.path.join(ROOT, *parts)
            if not os.path.exists(path):
                continue
            self.assertNotIn(chr(0x2014), src(*parts), parts)

    def test_this_module_leaves_the_environment_alone(self):
        text = src("tests", "test_session152.py")
        self.assertNotIn("os.environ" + "[", text)
        self.assertNotIn("os." + "putenv", text)


if __name__ == "__main__":
    unittest.main()
