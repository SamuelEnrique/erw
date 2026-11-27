"""Session 10410 (chain 720, part E): downloads of the forecast's new lines, and wind and solar by month and by hour.

Session 10409 gave `/forecast` a view for each output the forecast's files gained on 27 November 2026. This session
adds what the page's other views have: a download of each new line as a CSV with a reader in Python and in Stata
(`/forecast/net` for a place's net demand, wind and solar; `/forecast/realtime-price` for a hub's real-time price), and
the wind and solar scores month by month and by hour of the day, behind folds, from the wind and solar file's own rows.

    python -m pytest tests/test_session10410_forecast_downloads.py
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
EM = chr(0x2014)
ROUTES = ("net", "realtime-price")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_what_a_reader_gets(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-forecast-lines.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of the forecast's lines of 27 November")


class TheRoutes(unittest.TestCase):
    def test_each_download_has_its_csv_and_two_readers(self):
        for name in ROUTES:
            for parts in ((name, "route.ts"), (name, "reader.ts"), (name, "python", "route.ts"), (name, "stata", "route.ts")):
                self.assertTrue(os.path.exists(os.path.join(SITE, "app", "forecast", *parts)), "/".join(parts))

    def test_a_route_takes_only_a_name_the_files_list(self):
        net = src("site", "app", "forecast", "net", "route.ts")
        self.assertIn('const place = index?.places.find((p) => p.place === u.searchParams.get("place"));', net)
        rt = src("site", "app", "forecast", "realtime-price", "route.ts")
        self.assertIn('const hub = file && file.example !== true ? file.hubs.find((h) => h.hub === u.searchParams.get("hub")) : undefined;', rt)
        for name, word in (("net", "place"), ("realtime-price", "hub")):
            for kind in ("python", "stata"):
                text = src("site", "app", "forecast", name, kind, "route.ts")
                # the address written into a reader is built again from the listed name, never from the request's words
                self.assertRegex(text, r"const url = new URL\(`/forecast/%s\?%s=\$\{" % (re.escape(name), word))
                # the request's own query string is never copied: one named word is read and looked up in a file's list
                self.assertIsNone(re.search(r"\.search\b(?!Params)", text))
                self.assertEqual(len(re.findall(r"searchParams\.get\(", text)), 1)

    def test_the_routes_are_in_the_sites_lists(self):
        listed = src("tests", "test_session5160.py")
        for name in ROUTES:
            for sub in ("", "python/", "stata/"):
                self.assertIn(f'"app/forecast/{name}/{sub}route.ts"', listed)
        # the build carries the files each route reads: a place's file and the wind and solar file; the real-time file
        config = src("site", "next.config.ts")
        self.assertIn('"/forecast/net": ["./data/predict/*.json"], "/forecast/net/*": ["./data/predict/index.json"],', config)
        self.assertIn('"/forecast/realtime-price": ["./data/predict/rt_price.json"], "/forecast/realtime-price/*": ["./data/predict/rt_price.json"]', config)

    def test_no_route_reads_the_disk_itself(self):
        for name in ROUTES:
            for parts in ((name, "route.ts"), (name, "python", "route.ts"), (name, "stata", "route.ts")):
                self.assertNotIn("node:fs", src("site", "app", "forecast", *parts))


class TheCsvs(unittest.TestCase):
    def test_a_line_not_shown_has_no_row_and_the_header_says_why(self):
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn("head.push(`# ${fuel}: no line.", lib)
        self.assertIn("...(hub.tomorrow_held ? [`# tomorrow: no row. ${hub.tomorrow_held}`] : []),", lib)
        self.assertIn("never a published or official figure", lib)

    def test_the_day_ahead_price_is_named_the_comparator(self):
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn("the comparator, never an ERW method", lib)
        self.assertIn('"day_ahead_price"', lib)


class WindAndSolarByMonthAndHour(unittest.TestCase):
    def test_the_tables_are_the_files_rows_in_the_calendars_and_the_clocks_order(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        self.assertIn("export function WindSolarCuts", lines)
        self.assertIn('const cuts = lineScores(ws.rows_columns, ws.rows, { place: entry.place.place, fuel }, ["mae_mw", "nmae_pct"]);', lines)
        self.assertIn("const keys = orderedKeys(cut, g?.keys ?? []);", lines)
        self.assertIn('check={pfKey(WS_FILE, ["rows", c.i, col])}', lines)

    def test_the_value_check_reads_a_rows_megawatts_whole(self):
        text = src("site", "scripts", "check-values.mjs")
        rule = re.search(r"const predictLinesWhole = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        self.assertRegex("pf|predict/wind_solar.json|rows/412/6", rule)
        self.assertNotRegex("pf|predict/wind_solar.json|rows/412/7", rule)
        self.assertNotRegex("pf|predict/rt_price.json|rows/412/6", rule)


class TheValueCheckParsesAPageFileOnce(unittest.TestCase):
    """Found in a build of this session: with 2,350 keyed figures on /forecast the check parsed scores.json and
    wind_solar.json again for every key, held its own event loop about half a minute, and the server reset the
    connection of the batch's next page (ECONNRESET, "fetch failed" on /forecast's second address)."""

    def test_a_page_file_is_parsed_once_a_run(self):
        text = src("site", "scripts", "check-values.mjs")
        self.assertIn("const pfDocs = new Map();", text)
        self.assertIn("if (!pfDocs.has(k.file)) pfDocs.set(k.file, JSON.parse(fs.readFileSync(path.join(here, \"..\", \"data\", ...k.file.split(\"/\")), \"utf-8\")));", text)
        self.assertIn("return PF.resolveNumber(pfDocs.get(k.file), k.path);", text)
        # the file is not parsed inside the call that resolves one key any more
        self.assertNotIn("return PF.resolveNumber(JSON.parse(fs.readFileSync(", text)

    def test_the_value_check_reads_both_addresses_of_the_page(self):
        text = src("site", "scripts", "check-values.mjs")
        self.assertIn('"/forecast", "/forecast?a=region-cal&b=region-tex&s=price&m=mape",', text)


class Words(unittest.TestCase):
    def test_no_em_dash(self):
        for name in ROUTES:
            for parts in ((name, "route.ts"), (name, "reader.ts"), (name, "python", "route.ts"), (name, "stata", "route.ts")):
                self.assertNotIn(EM, src("site", "app", "forecast", *parts), "/".join(parts))
        self.assertNotIn(EM, src("tests", "test_session10410_forecast_downloads.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
