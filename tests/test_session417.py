"""Session 417 (the chain of 21 October 2026, day, 021): the shared year axis. components/TimeChart.tsx with x="year"
spaced its ticks evenly in time and wrote a year twice where a chart holds few years (sessions 404 and 405: "2020,
2020, 2021, 2023, 2024, 2024, 2026"). A year axis now puts its ticks on whole years only (1 January, UTC, where every
caller puts a year's point), every year or every 2, 5, 10 ... so that they fit; every other axis is as it was.
Energy Research Warehouse (ERW)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASHES = (chr(0x2014), chr(0x2013))
CALLERS = [("site", "app", "explore", "ercot-peak-premium", "page.tsx"), ("site", "app", "explore", "interconnection", "page.tsx"),
           ("site", "app", "explorer", "ercot-peak-premium", "Explorer.tsx")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def year_ticks_js():
    """The function as the file holds it, its type notes taken out so that node runs it."""
    s = src("site", "components", "TimeChart.tsx")
    body = re.search(r"export function yearTicks\(t0: number, t1: number, n: number\): number\[\] \{.*?\n\}", s, re.S).group(0)
    body = body.replace("export function yearTicks(t0: number, t1: number, n: number): number[]", "function yearTicks(t0, t1, n)")
    return body.replace("const out: number[] = [];", "const out = [];")


def ticks(cases):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on the path")
    code = (year_ticks_js() + f"; const cases = {json.dumps(cases)};"
            "console.log(JSON.stringify(cases.map(([a, b, n]) => yearTicks(Date.UTC(a, 0, 1), Date.UTC(b, 0, 1), n).map((t) => new Date(t).toISOString().slice(0, 4)))))")
    out = subprocess.run([exe, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class TheYearAxis(unittest.TestCase):
    def test_a_year_is_written_once_and_ticks_sit_on_whole_years(self):
        # 2020 to 2026 at seven ticks: the case of sessions 404 and 405, once a year; ERCOT's median wait, 2018 to 2025;
        # a phone's two ticks; one year alone; forty years at seven ticks
        r = ticks([[2020, 2026, 7], [2018, 2025, 7], [2018, 2025, 2], [2024, 2024, 7], [1985, 2025, 7]])
        self.assertEqual(r[0], ["2020", "2021", "2022", "2023", "2024", "2025", "2026"])
        for got in r:
            self.assertEqual(len(got), len(set(got)), got)
        self.assertEqual(r[1], ["2018", "2020", "2022", "2024"])     # eight years do not fit seven: every second year
        self.assertEqual(r[2], ["2018", "2023"])                      # a phone's two ticks: every fifth year
        self.assertEqual(r[3], ["2024"])
        self.assertEqual(r[4], ["1985", "1995", "2005", "2015", "2025"])

    def test_the_chart_uses_it_for_the_year_axis_only(self):
        s = src("site", "components", "TimeChart.tsx")
        self.assertIn('return x === "year" ? yearTicks(t0, t1, n) : Array.from({ length: n }, (_, i) => t0 + ((t1 - t0) * i) / (n - 1));', s)
        # a label is anchored to an edge on a year axis only where its tick is that edge; other axes as they were
        self.assertIn('textAnchor={x === "year" ? (t === t0 ? "start" : t === t1 ? "end" : "middle") : i === 0 ? "start" : i === xTicks.length - 1 ? "end" : "middle"}', s)

    def test_every_caller_puts_a_years_point_on_1_january(self):
        for parts in CALLERS:
            self.assertIn('x="year"', src(*parts), parts)
        self.assertIn("Date.UTC(y, 0, 1) / 1000", src("site", "app", "explore", "interconnection", "page.tsx"))

    def test_no_dash_in_this_sessions_lines(self):
        for line in src("site", "components", "TimeChart.tsx").splitlines() + src("tests", "test_session417.py").splitlines():
            for d in DASHES:
                self.assertNotIn(d, line)


if __name__ == "__main__":
    unittest.main()
