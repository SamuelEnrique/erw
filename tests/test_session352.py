"""Session 352 (the chain of 20 October 2026, night, second part): the price years on the three economics pages. A
"Price years" choice reads the data machine's price_years_by_window (session 357) and prices scenario A and B, the
results and the sensitivity on the chosen window; the last twelve months stay the default and write nothing into the
address, so no default number moves. Energy Research Warehouse (ERW)."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    if not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
        raise unittest.SkipTest("the site's packages are not here")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


ROWS = [
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_4h_last_12", "ts_utc": "2025-10-01T00:00:00+00:00", "value": 81.4, "unit": "USD/kW-year", "freq": "P12M"},
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_4h_year_2021", "ts_utc": "2021-01-01T00:00:00+00:00", "value": 3430.56, "unit": "USD/kW-year", "freq": "P12M"},
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_4h_year_2024", "ts_utc": "2024-01-01T00:00:00+00:00", "value": 147.67, "unit": "USD/kW-year", "freq": "P12M"},
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_4h_year_2026", "ts_utc": "2026-01-01T00:00:00+00:00", "value": 60.19, "unit": "USD/kW-year", "freq": "P9M"},
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_4h_avg_3y", "ts_utc": "2023-01-01T00:00:00+00:00", "value": 255.08, "unit": "USD/kW-year", "freq": "P36M"},
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_4h_all_less_uri_2021", "ts_utc": "2018-01-01T00:00:00+00:00", "value": 269.52, "unit": "USD/kW-year", "freq": "P105M"},
    {"entity": "ercot:HB_HUBAVG", "variable": "battery_foresight_8h_last_12", "ts_utc": "2025-10-01T00:00:00+00:00", "value": 99.0, "unit": "USD/kW-year", "freq": "P12M"},
]


class TheLibrary(unittest.TestCase):
    def test_windows_are_read_from_the_series_columns(self):
        out = node("const p = await import('./lib/priceyears.ts'); const rows = " + json.dumps(ROWS) + ";"
                   "const ws = p.windowsOf(rows, 'battery_foresight_4h_');"
                   "console.log(JSON.stringify({ ids: ws.map((w) => w.id), y26: ws.find((w) => w.id === 'year_2026'), bw: p.highLow(ws), dflt: p.chosen(ws, 'last_12'), y21: p.chosen(ws, 'year_2021')?.value,"
                   " words: ws.map((w) => p.windowWords(w).label) }));")
        self.assertEqual(out["ids"], ["last_12", "year_2026", "year_2024", "year_2021", "avg_3y", "all_less_uri_2021"])   # the 8-hour row is another configuration
        self.assertEqual((out["y26"]["from"], out["y26"]["to"], out["y26"]["months"], out["y26"]["whole"]), ("2026-01", "2026-09", 9, False))
        self.assertEqual((out["bw"]["high"]["id"], out["bw"]["low"]["id"]), ("year_2021", "year_2024"))   # a year held in part is neither
        self.assertIsNone(out["dflt"])                    # the default is the page's own last twelve months, not a row
        self.assertEqual(out["y21"], 3430.56)
        self.assertIn("2026, 9 months held (their sum, not a full year)", out["words"])


class TheDefaultsHold(unittest.TestCase):
    def test_the_default_writes_nothing_and_each_page_reads_py_only(self):
        view = src("site", "lib", "battery", "view.ts")
        self.assertIn('measure: "npv", py: "last_12" };', view)
        self.assertIn('if (v.py !== DEFAULT_VIEW.py) out.push(["py", v.py]);', view)
        nav = src("site", "components", "tool", "PriceYearsNav.tsx")
        self.assertIn('if (id === DEFAULT_WINDOW) q.delete("py"); else q.set("py", id);', nav)
        self.assertIn('const pyId = q.py && WINDOW_RE.test(q.py) ? q.py : DEFAULT_WINDOW;', src("site", "app", "cost-of-power", "seller", "model.ts"))
        self.assertIn("const pyId = q.py && WINDOW_RE.test(q.py) ? q.py : null;", src("site", "app", "cost-of-power", "model.ts"))
        # the battery's revenue under a window is the table's at the model's step, and not held at another
        sc = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        self.assertIn("const out: Revenue | null = rte === MODEL.rte && cycles === MODEL.cycles", sc)
        self.assertIn("? { l12: win.value, first: win.from, last: win.to,", sc)

    def test_show_keeps_the_price_years_and_a_figure_is_a_bare_number(self):
        keep = 'const py = new URLSearchParams(window.location.search).get("py"); if (py) q.set("py", py); }'
        for parts in (("seller", "SellerForm.tsx"), ("LoadForm.tsx",), ("battery", "BatteryForm.tsx")):
            self.assertIn(keep, src("site", "app", "cost-of-power", *parts), parts)
        # check-values reads a figure's text as a number: the currency stays outside the Num
        for parts in (("battery", "Scenarios.tsx"), ("seller", "page.tsx"), ("page.tsx",)):
            self.assertNotIn("raw={w.value}>USD", src("site", "app", "cost-of-power", *parts), parts)

    def test_the_packs_say_what_the_pages_show_now(self):
        for name in ("battery", "generator", "datacenter"):
            self.assertIn("Since session 352 (20 October 2026)", src("docs", "reviews", "packs", f"{name}.md"), name)


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "lib", "priceyears.ts"), ("site", "lib", "priceyearsread.ts"), ("site", "components", "tool", "PriceYearsChoice.tsx"),
                      ("site", "components", "tool", "PriceYearsNav.tsx"), ("site", "app", "cost-of-power", "battery", "Scenarios.tsx"),
                      ("site", "app", "cost-of-power", "seller", "model.ts"), ("site", "app", "cost-of-power", "model.ts"), ("site", "app", "cost-of-power", "page.tsx"),
                      ("site", "app", "cost-of-power", "seller", "page.tsx"), ("docs", "reviews", "packs", "battery.md"), ("tests", "test_session352.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
