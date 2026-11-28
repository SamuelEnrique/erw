"""Session 10401 (chain 720, part C, 26 November 2026): the ERW forecast page, /forecast.

Energy Research Warehouse (ERW). The page draws the ERW's own day-ahead forecast of demand and price for a place from
the page files of the data machine's forecast build (site/data/predict/, contract docs/state/page_files_predict.md),
the operator's own forecast beside it, and the report card of each. Held here:

- what a reader sees, drawn to HTML by the site's own code without a build (site/scripts/test-forecast.mjs): with no
  files on the site, with the contract's own example files (nothing shown as a forecast), and with files of the
  contract's shape and a test's made-up values (the figures and their keys into the files, "ERW forecast" on every
  chart, a held price blank with "license needed", the months and hours the model lost drawn as the ones it won, two
  places side by side, the downloads and their readers);
- on the source: the page is in review and in no menu (no line of its own in the release gate or the menu), nothing of
  the Economic impact tool is imported, its tour stop is held by its flag, its addresses are in check-routes, its files
  are traced for the build, and no new file holds an em dash.

Nothing here sets a key, reads a table or makes a request.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
NEW = [
    ("site", "lib", "predict.ts"), ("site", "lib", "predictfiles.ts"), ("site", "lib", "csvreader.ts"),
    ("site", "app", "forecast", "page.tsx"), ("site", "app", "forecast", "view.tsx"),
    ("site", "app", "forecast", "rows", "route.ts"), ("site", "app", "forecast", "rows", "reader.ts"),
    ("site", "app", "forecast", "rows", "python", "route.ts"), ("site", "app", "forecast", "rows", "stata", "route.ts"),
    ("site", "app", "forecast", "scores", "route.ts"), ("site", "app", "forecast", "scores", "reader.ts"),
    ("site", "app", "forecast", "scores", "python", "route.ts"), ("site", "app", "forecast", "scores", "stata", "route.ts"),
    ("site", "app", "forecast", "ledger", "route.ts"), ("site", "app", "forecast", "ledger", "reader.ts"),
    ("site", "app", "forecast", "ledger", "python", "route.ts"), ("site", "app", "forecast", "ledger", "stata", "route.ts"),
    ("site", "scripts", "check-forecast-files.mjs"),
    ("site", "scripts", "test-forecast.mjs"),
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules", "react-dom")), "node or the site's packages are not on this machine")
class WhatAReaderSees(unittest.TestCase):
    def test_the_page_drawn_without_a_build(self):
        env = {k: v for k, v in os.environ.items() if k != "ERW_PREDICT_DIR"}
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-forecast.mjs"], cwd=SITE, env=env,
                           capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of /forecast")


class TheSource(unittest.TestCase):
    def test_in_review_and_in_no_menu(self):
        # a path with no line in the release gate is in review; a page not in lib/pages.ts is in no menu
        self.assertIn('"/forecast": "review"', src("site", "lib", "release.ts"))   # session 11405 (decision 4, readied): its own line in the release gate, in review
        self.assertIn('{ href: "/forecast", label: "ERW forecast"', src("site", "lib", "pages.ts"))   # session 11405 (decision 4 of the weekend page of 28 November 2026, readied): in the menu under its own name
        page = src("site", "app", "forecast", "page.tsx")
        self.assertIn('robots: { index: false, follow: false }', page)
        self.assertIn('title: "ERW forecast"', page)

    def test_nothing_of_the_impact_tool_is_imported(self):
        for parts in NEW[:-1]:
            text = src(*parts)
            for line in text.splitlines():
                if line.lstrip().startswith("import ") or " from \"" in line:
                    self.assertNotRegex(line, r"@/lib/forecast|@/data/forecast|app/impact|/impact/", f"{'/'.join(parts)}: {line.strip()}")

    def test_the_page_reads_only_the_contracts_files(self):
        files = src("site", "lib", "predictfiles.ts")
        self.assertIn('path.join(process.cwd(), "data", "predict")', files)
        self.assertIn("ERW_PREDICT_DIR", files)
        # a file marked as a test's fixture is never read from the site's own folder
        self.assertIn('"fixture" in v && v.fixture && !process.env.ERW_PREDICT_DIR', files)
        view = src("site", "app", "forecast", "view.tsx")
        self.assertNotIn("supabase", view.lower())
        self.assertNotIn("fetch(", view)

    def test_the_words_on_the_model_line(self):
        lib = src("site", "lib", "predict.ts")
        self.assertIn('export const LABEL = "ERW forecast";', lib)
        self.assertIn("erw: LABEL", lib)
        view = src("site", "app", "forecast", "view.tsx")
        # the model's series on a chart is named by LABEL and nothing else
        self.assertIn("{ name: LABEL, color: \"accent\", kind: \"line\"", view)
        self.assertNotRegex(view, r"name: \"(Forecast|Published|Official)")

    def test_no_sorting_by_score(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertNotIn(".sort(", view)
        lib = src("site", "lib", "predict.ts")
        ordered = lib[lib.index("export function orderedKeys"):lib.index("export function rowHours")]
        # the only orders are the calendar's and the clock's
        self.assertEqual(len(re.findall(r"\.sort\(", ordered)), 2)
        self.assertNotRegex(ordered, r"mae|mape")

    def test_the_tour_stop_is_held_by_its_flag(self):
        tour = src("site", "lib", "tour.ts")
        # a new stop is `landed` exactly when its page is in site/app (tests/test_session8902_tour.py), so the stop of a
        # page that is on main before its files waits in a list of its own, on no page of the tour
        waiting = tour[tour.index("export const WAITING_STOPS"):tour.index("/** The guided path")]
        new = tour[tour.index("export const NEW_STOPS"):tour.index("export const WAITING_STOPS")]
        self.assertNotIn('"/forecast"', new)
        self.assertIn('href: "/forecast", title: "ERW forecast"', waiting)
        self.assertIn("waits: \"the ERW forecast's page files (site/data/predict/)", waiting)
        self.assertIn('headings: ["Tomorrow", "How it has done", "Every place"]', waiting)
        self.assertNotIn("WAITING_STOPS", tour[tour.index("/** The guided path"):])   # the path does not read it
        # when it moves into the path it must pass the tour's own rule: what `look` quotes is among its headings
        look = re.search(r'look: "((?:[^"\\]|\\.)*)"', waiting).group(1)
        for quoted in re.findall(r'\\"([^"\\]+)\\"', look):
            self.assertIn(quoted, ["Tomorrow", "How it has done", "Every place"])
        view = src("site", "app", "forecast", "view.tsx")
        for heading in ("Tomorrow", "How it has done", "Every place"):
            self.assertIn(f'<ToolSection title="{heading}"', view)

    def test_the_addresses_are_checked_and_the_files_traced(self):
        routes = src("site", "scripts", "check-routes.mjs")
        for page in ('"/forecast"', '"/forecast?a=zz&b=zz&s=zz&day=zz&m=zz"'):
            self.assertIn(page, routes)
        config = src("site", "next.config.ts")
        for route in ("/forecast", "/forecast/rows", "/forecast/scores"):
            self.assertIn(f'"{route}": ["./data/predict/*.json"]', config)
        self.assertIn('"/forecast/ledger": ["./data/predict/*.csv"]', config)

    def test_the_ledger_is_served_as_written(self):
        # the contract's change of 26 November 2026: every forecast as made on its day, never rewritten. The route hands
        # the file on as it is, and only the two ledgers can be named
        files = src("site", "lib", "predictfiles.ts")
        self.assertIn('series === "price" ? "ledger_price.csv" : series === "demand" ? "ledger_demand.csv" : null', files)
        route = src("site", "app", "forecast", "ledger", "route.ts")
        self.assertIn("return new Response(text, {", route)
        reader = src("site", "app", "forecast", "ledger", "reader.ts")
        for col in ("series", "place", "target_day", "ts_utc", "local_hour", "made_utc", "inputs_through_utc", "horizon_days", "method", "erw", "lo", "hi"):
            self.assertIn(f'"{col}"', reader)

    def test_a_long_reason_is_a_hover_not_a_cell(self):
        # found at a phone's width on the real files: "not published: no operator publishes a forecast of its day-ahead
        # price" in every operator cell made the price tables 1,794 px wide
        view = src("site", "app", "forecast", "view.tsx")
        self.assertNotRegex(view, r'words=\{[^}]*operator_held \?\?')
        self.assertGreaterEqual(view.count("shortHeld("), 6)

    def test_the_month_table_holds_every_month(self):
        view = src("site", "app", "forecast", "view.tsx")
        # a long table scrolls inside a frame of its own height; nothing folds its rows away
        self.assertIn("tall={keys.length > 30}", view)
        self.assertIn("max-h-[30rem] overflow-y-auto", view)
        table = view[view.index("function ScoreTable("):view.index("/** The report card of the places chosen")]
        self.assertNotIn("<details", table)
        self.assertNotRegex(table, r"\.slice\(|\.filter\(")

    def test_the_contracts_examples_show_nothing(self):
        d = os.path.join(ROOT, "docs", "state", "page_files_predict_examples")
        for name in ("index.json", "region-tex.json", "scores.json"):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                self.assertIs(json.load(f)["example"], True, name)

    def test_the_value_check_knows_a_megawatt_is_written_whole(self):
        # session 10404: the value check run on a build with window B's files failed 70 of tomorrow's 72 hours of demand
        # ("54,040" against 54039.5): the page writes a megawatt whole (lib/predict.ts valueWords), and the check's
        # rule for it stands on its own line, beside the text test older tests pin
        text = src("site", "scripts", "check-values.mjs")
        self.assertIn("const predictWhole = /^pf\\|predict\\/", text)
        self.assertIn("if (!pass && predictWhole && t !== undefined && t !== null && same) pass = true;", text)
        self.assertIn('unit === "MW" ? Math.round(v).toLocaleString("en-US")', src("site", "lib", "predict.ts"))
        rule = re.search(r"const predictWhole = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        for key in ("pf|predict/region-tex.json|series/demand/tomorrow/17/2", "pf|predict/ba-ciso.json|series/demand/history/40/3",
                    "pf|predict/region-tex.json|series/demand/summary/backtest/mae/erw", "pf|predict/scores.json|rows/7495/6"):
            self.assertRegex(key, rule)
        for key in ("pf|predict/region-tex.json|series/price/tomorrow/17/2", "pf|predict/scores.json|rows/7495/7",
                    "pf|predict/region-tex.json|series/demand/summary/backtest/mape/erw", "pf|conditions/x.json|series/demand/tomorrow/1/2"):
            self.assertNotRegex(key, rule)

    def test_no_em_dash(self):
        for parts in NEW:
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        self.assertNotIn(EM, src("tests", "test_session10401_forecast.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
