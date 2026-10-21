"""Session 416 (the chain of 21 October 2026, day, 021): the four faults the landing of chain 015 found (session 415's
note, "Faults found"). The shared charts' zero tick is "0", never "-0" (ticksOf in components/svgchart.tsx, which the
peak-premium explorer's box chart draws through, and TimeChart's own); /emissions' "Monthly since 2018" draws on a
month axis; /data's coverage table names each table in a row header, so that the sticky first column of tokens.css
keeps the head and the body in step at 390 px; session 410's shot script takes the viewport as it is (its clip, read
from the document's top under mobile emulation, drew a band the height of the scroll); check-table-downloads takes a
page that Git Bash rewrote into a Windows path. Energy Research Warehouse (ERW)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(code):
    """Run a snippet with node; skip where node is not on the path."""
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on the path")
    out = subprocess.run([exe, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class TheZeroTick(unittest.TestCase):
    def test_the_svg_charts_ticks_never_hold_minus_zero(self):
        s = src("site", "components", "svgchart.tsx")
        body = re.search(r"export function ticksOf\(b: Bounds\): number\[\] \{(.*?)\n\}", s, re.S).group(1)
        self.assertIn("Math.round(t * 1e6) / 1e6 || 0", body)
        js = body.replace("const step = nice(b.hi - b.lo), out: number[] = [];", "const step = 0.5, out = [];")
        # lo -0.3 with a step of 0.5: Math.ceil(-0.6) is -0, and -0 * 0.5 is -0, the tick the explorer drew as "-0"
        r = node(f"const f = (b) => {{{js}}}; const t = f({{ lo: -0.3, hi: 1 }});"
                 "console.log(JSON.stringify([t.map(String), t.some((v) => Object.is(v, -0))]))")
        self.assertEqual(r, [["0", "0.5", "1"], False])

    def test_the_time_charts_ticks_never_hold_minus_zero(self):
        s = src("site", "components", "TimeChart.tsx")
        line = re.search(r"const ticksOf = \(b: Bounds\) => \{(.*?)\};", s).group(1)
        self.assertIn("|| 0", line)
        js = line.replace("const out: number[] = [];", "const out = [];")
        r = node(f"const f = (b) => {{{js}}}; const t = f({{ lo: -0, hi: 1, step: 0.5 }});"
                 "console.log(JSON.stringify([t.map(String), t.some((v) => Object.is(v, -0))]))")
        self.assertEqual(r, [["0", "0.5", "1"], False])

    def test_the_explorers_box_chart_draws_through_the_fixed_ticks(self):
        self.assertIn('import { BoxPlot } from "./svgchart";', src("site", "components", "BoxChart.tsx"))
        s = src("site", "components", "svgchart.tsx")
        box = s[s.index("export function BoxPlot"):]
        self.assertIn("ticksOf(b).map", box)


class TheEmissionsAxis(unittest.TestCase):
    def test_monthly_since_2018_is_drawn_on_a_month_axis(self):
        s = src("site", "components", "grid", "Emissions.tsx")
        monthly = s[s.index("function Monthly"):s.index("function Monthly") + 2500]
        self.assertRegex(monthly, r'<LineChart lines=\{lines\} unit="kg CO2/MWh" height=\{280\} x="month"')
        t = src("site", "components", "TimeChart.tsx")
        self.assertIn('month: (t) => new Date(t).toISOString().slice(0, 7),', t)
        # the last 24 hours keep the minute axis
        self.assertIn('<LineChart lines={lines} unit="kg CO2/MWh" height={260} ariaLabel="Carbon intensity of generation per ISO, the last 24 hours" />', s)


class TheDataTable(unittest.TestCase):
    def test_each_row_is_headed_by_its_table_name(self):
        s = src("site", "app", "data", "page.tsx")
        cov = s[s.index('id="coverage"'):]
        cov = cov[:cov.index("</table>")]
        self.assertIn('<th scope="row" className="py-1 pr-3 text-left align-top font-mono text-xs font-normal">', cov)
        self.assertNotIn('<td className="py-1 pr-3 font-mono text-xs">', cov)
        self.assertEqual(cov.count("<th scope=\"row\""), 1)

    def test_the_sticky_rule_is_the_reason(self):
        t = src("site", "app", "tokens.css")
        self.assertIn(".brand-a .overflow-x-auto table:not([data-scenario-table]) th:first-child,", t)

    def test_session_410s_script_takes_the_viewport_as_it_is(self):
        s = src("docs", "brand", "review-410", "shot-410.mjs")
        self.assertNotIn("clip:", s)
        self.assertIn('send("Page.captureScreenshot", { format: "png" })', s)


class TheDownloadsCheck(unittest.TestCase):
    def test_a_page_rewritten_by_git_bash_is_read_back(self):
        s = src("site", "scripts", "check-table-downloads.mjs")
        expr = re.search(r"const pages = \(args.length > 1 \? args.slice\(1\) : \[\"/board\", \"/prices\"\]\)(.*);", s).group(1)
        given = ["C:/Program Files/Git/explore/ercot-peak-premium", "/prices", "data"]
        r = node(f"console.log(JSON.stringify({json.dumps(given)}{expr}))")
        self.assertEqual(r, ["/explore/ercot-peak-premium", "/prices", "/data"])


class TheWords(unittest.TestCase):
    def test_no_dash_in_the_lines_this_session_wrote(self):
        for parts in [("site", "app", "data", "page.tsx"), ("docs", "brand", "review-410", "shot-410.mjs"),
                      ("site", "scripts", "check-table-downloads.mjs"), ("tests", "test_session416.py")]:
            for line in src(*parts).splitlines():
                if "session 416" in line:
                    for d in DASHES:
                        self.assertNotIn(d, line, parts)


if __name__ == "__main__":
    unittest.main()
