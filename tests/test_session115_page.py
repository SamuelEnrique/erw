"""Session 115, the page: what Texas's storage resources were awarded day-ahead (/cost-of-power/battery/awards).

Energy Research Warehouse (ERW). No request leaves the machine. The page is in review and reads
ercot_storage_dam_awards_monthly and, for the column labeled as the model's, battery_stack_monthly. These tests hold:

- the page is in review and the live battery page neither links to it nor reads its table;
- the page says what the awards are not before it shows a number, calls them a floor on market revenue, and never
  calls them what a battery made;
- the model's figure is labeled as the model's;
- the page's arithmetic (site/lib/storageawards.ts, run in Node): a year is the sum of its months, a partial month is
  never scaled and never set beside the model, an empty read gives no month and no sentence.

The rows of the arithmetic tests are made for the tests (small round numbers, never shown anywhere): they test the
sums, not the data. The table's own tests are in tests/test_session115.py.

    python -m unittest tests.test_session115_page -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = ("site", "app", "cost-of-power", "battery", "awards", "page.tsx")
LIB = ("site", "lib", "storageawards.ts")
LIVE = ["site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/BatteryForm.tsx", "site/app/cost-of-power/battery/Contract.tsx"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def month(m, days_held, days_in_month, energy, ancillary, resources=10, with_award=8, hours=1000, hours_energy=80, mw=500.0):
    """A month of the fleet's rows, made for the test."""
    ts = f"{m}-01T00:00:00Z"
    v = {"days_held": days_held, "days_missing": days_in_month - days_held, "days_in_month": days_in_month, "resources": resources,
         "resources_with_award": with_award, "resource_hours": hours, "resource_hours_energy_award": hours_energy, "mw": mw,
         "revenue_energy_usd_per_mw": energy, "revenue_ancillary_usd_per_mw": ancillary, "revenue_total_usd_per_mw": energy + ancillary}
    return [{"variable": k, "ts_utc": ts, "value": x} for k, x in v.items()]


def model(m, total, days_held, days_in_month):
    ts = f"{m}-01T00:00:00Z"
    v = {"revenue_total_usd_per_mw": total, "revenue_energy_usd_per_mw": total * 0.6, "revenue_ancillary_usd_per_mw": total * 0.4,
         "days_held": days_held, "days_in_month": days_in_month}
    return [{"variable": "dayahead_2h_" + k, "ts_utc": ts, "value": x} for k, x in v.items()]


class Release(unittest.TestCase):
    def test_the_page_is_in_review(self):
        release = src("site", "lib", "release.ts")
        self.assertRegex(release, r'"/cost-of-power/battery/awards": "review"')
        # session 166 (the owner's instruction of 8 October 2026): the battery page is in review too; no page is live
        self.assertRegex(release, r'"/cost-of-power/battery": "review"')
        self.assertEqual(re.findall(r'"(/[^"]*)":\s*"live"', release), [])
        got = node("const r = await import('./lib/release.ts'); console.log(JSON.stringify({a: r.statusOf('/cost-of-power/battery/awards'), "
                   "b: r.statusOf('/cost-of-power/battery'), m: r.statusOf('/data/methods/ercot_storage_dam_awards')}));")
        self.assertEqual(got, {"a": "review", "b": "review", "m": "review"})

    def test_the_route_check_asks_for_it(self):
        self.assertIn('"/cost-of-power/battery/awards"', src("site", "scripts", "check-routes.mjs"))

    def test_the_live_battery_page_does_not_know_of_it(self):
        """No link from the live page, no read of the new table there, no menu entry (the menu is on every live page)."""
        for f in LIVE + ["site/app/cost-of-power/Tabs.tsx", "site/lib/pages.ts", "site/app/about/page.tsx"]:
            text = src(*f.split("/"))
            for word in ("battery/awards", "storageawards", "ercot_storage_dam_awards"):
                self.assertNotIn(word, text, f)

    def test_the_live_battery_page_is_as_main_has_it(self):
        """While session 115's page is not on main: the three files of the live battery page are main's, byte for byte."""
        def git(*a):
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        if git("rev-parse", "--verify", "--quiet", "origin/main").returncode != 0:
            self.skipTest("origin/main is not in this checkout")
        if git("cat-file", "-e", "origin/main:" + "/".join(PAGE)).returncode == 0:
            self.skipTest("the page is on main: the session's deploy is done, and later sessions may change the battery page")
        r = git("diff", "--quiet", "origin/main", "--", *LIVE)
        self.assertEqual(r.returncode, 0, "the live battery page differs from origin/main")


class Words(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src(*PAGE)
        # what a reader can see: the comments of the file are not the page
        cls.text = re.sub(r"^\s*//.*$", "", cls.page, flags=re.M)

    def test_what_it_is_not_comes_first(self):
        first = self.text.index("What this is not")
        for later in ("data-awards-summary", "<ChartFrame", "<ToolSection", "<ToolTable", "MonthBars ms="):
            self.assertLess(first, self.text.index(later), later)
        lead = self.text[first:first + 700]
        for said in ("day-ahead awards only", "no real-time settlement", "no deployment energy", "no contracts", "floor", "not what any battery earned"):
            self.assertIn(said, lead)

    def test_it_is_never_called_what_a_battery_made(self):
        for body in (self.page, src(*LIB)):
            low = body.lower()
            self.assertEqual(len(re.findall(r"earned", low)), len(re.findall(r"not what any battery earned", low)))
            for word in ("measured revenue", "earnings", "revenue earned", "what batteries earn", "what the fleet earn"):
                self.assertNotIn(word, low)
        self.assertIn("floor", self.text)
        self.assertIn("awarded", self.text)
        self.assertNotIn(chr(0x2014), self.page + src(*LIB))  # no em dash

    def test_the_model_is_labeled_as_the_models(self):
        heads = re.findall(r"head=\{\[(.*?)\]\}", self.text, flags=re.S)
        self.assertEqual(len(heads), 2)
        for h in heads:
            self.assertRegex(h, r"The model&apos;s")
            self.assertIn("2-hour battery, day-ahead schedule", h)
        self.assertIn("is the model&apos;s", self.text)
        self.assertIn("not a measure of the model&apos;s error", self.text)

    def test_what_it_reads(self):
        lib = src(*LIB)
        self.assertIn('export const TABLE = "ercot_storage_dam_awards_monthly"', lib)
        self.assertIn('export const ENTITY = "ercot:esr_fleet"', lib)
        self.assertIn('export const MODEL_TABLE = "battery_stack_monthly"', lib)
        self.assertIn('export const MODEL_PREFIX = "dayahead_2h_"', lib)
        self.assertIn("not loaded in the site&apos;s database, so no number is shown", self.text)
        self.assertNotRegex(self.text, r"\bno data\b")  # the route check counts those words
        self.assertNotIn("data-check=", self.page)       # scripts/check-values.mjs has no rule for this page
        self.assertNotRegex(self.page, r"anthropic|\bfetch\(")  # no model call, no request of its own
        self.assertIn('export const dynamic = "force-dynamic"', self.page)  # never read while the site is built


class Arithmetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = (month("2025-12", 26, 31, 300.0, 100.0) + month("2026-01", 31, 31, 500.0, 250.0) + month("2026-02", 28, 28, 200.0, 50.0, hours=2000, hours_energy=120)
                + month("2026-03", 5, 31, 40.0, 10.0))
        mod = model("2025-12", 4000.0, 31, 31) + model("2026-01", 11000.0, 31, 31) + model("2026-02", 2000.0, 28, 28) + model("2026-03", 2800.0, 31, 31)
        cls.got = node(
            "const m = await import('./lib/storageawards.ts');"
            f"const rows = {json.dumps(rows)}; const mod = {json.dumps(mod)};"
            "const ms = m.monthsOf(rows, mod);"
            "const short = m.monthsOf(rows, mod.filter((r) => !r.ts_utc.startsWith('2026-02')));"
            "const part = m.monthsOf(rows, mod.map((r) => (r.ts_utc.startsWith('2026-02') && r.variable.endsWith('days_held') ? { ...r, value: 20 } : r)));"
            "console.log(JSON.stringify({ ms, ys: m.years(ms), newest: m.newestComplete(ms), share: m.energyAwardShare(ms), sentence: m.summary(ms),"
            " none: { ms: m.monthsOf([], mod), ys: m.years([]), sentence: m.summary([]), share: m.energyAwardShare([]) },"
            " noModel: m.years(m.monthsOf(rows, [])), shortModel: m.years(short), partModel: m.years(part),"
            " strings: m.monthsOf(rows.map((r) => ({ ...r, value: String(r.value) })), mod).length,"
            " lacking: m.monthsOf(rows.filter((r) => !(r.ts_utc.startsWith('2026-01') && r.variable === 'days_held')), mod).map((r) => r.m),"
            " span: [m.span(['2026-01', '2026-02']), m.span(['2026-01']), m.span(['2025-12', '2026-01']), m.span(['2026-01', '2026-03'])], kw: m.kw(680.4) }));")

    def test_months(self):
        ms = self.got["ms"]
        self.assertEqual([r["m"] for r in ms], ["2025-12", "2026-01", "2026-02", "2026-03"])
        self.assertEqual([r["complete"] for r in ms], [False, True, True, False])
        self.assertEqual(ms[1]["total"], 750.0)
        self.assertEqual(ms[1]["model"], {"total": 11000.0, "energy": 6600.0, "ancillary": 4400.0, "whole": True})
        self.assertEqual(self.got["strings"], 4)  # the live set may serve a value as a string
        self.assertEqual(self.got["lacking"], ["2025-12", "2026-02", "2026-03"])  # a month without its days is not shown

    def test_a_year_is_the_sum_of_its_months_and_no_partial_month_is_scaled(self):
        y25, y26 = self.got["ys"]
        self.assertEqual((y25["y"], y25["daysHeld"], y25["daysInMonths"], y25["total"]), ("2025", 26, 31, 400.0))
        self.assertEqual((y26["y"], y26["daysHeld"], y26["daysInMonths"]), ("2026", 64, 90))
        self.assertEqual((y26["energy"], y26["ancillary"], y26["total"]), (740.0, 310.0, 1050.0))  # the 5 days of March as they are

    def test_the_model_stands_only_beside_whole_months(self):
        y25, y26 = self.got["ys"]
        self.assertEqual((y25["completeMonths"], y25["awardsComplete"], y25["modelComplete"]), ([], None, None))
        self.assertIn("no month", y25["noModel"])
        self.assertEqual(y26["completeMonths"], ["2026-01", "2026-02"])
        self.assertEqual((y26["awardsComplete"], y26["modelComplete"], y26["noModel"]), (1000.0, 13000.0, None))  # March's 2,800 is not in it
        for other in ("noModel", "shortModel", "partModel"):  # no model row, a month without one, a model month that is partial
            y = self.got[other][1]
            self.assertIsNone(y["modelComplete"], other)
            self.assertEqual(y["awardsComplete"], 1000.0, other)
            self.assertIn("2026-02", y["noModel"], other)

    def test_the_sentence_and_the_share(self):
        self.assertEqual(self.got["newest"]["m"], "2026-02")
        s = self.got["sentence"]
        self.assertTrue(s.startswith("In February 2026, ERCOT's disclosure lists 10 storage resources with 500 MW between them"), s)
        self.assertIn("day-ahead awards came to USD 0.25 per kW for the month, 0.20 from energy net of charging and 0.05 from ancillary services.", s)
        self.assertEqual(self.got["share"], {"hours": 5000, "withAward": 360, "share": 0.072})
        self.assertEqual(self.got["kw"], "0.68")
        self.assertEqual(self.got["span"], ["January to February 2026", "January 2026", "December 2025 to January 2026", "Jan 2026, Mar 2026"])

    def test_an_empty_read_shows_nothing(self):
        self.assertEqual(self.got["none"], {"ms": [], "ys": [], "sentence": None, "share": None})


if __name__ == "__main__":
    unittest.main()
