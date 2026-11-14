"""Session 5501 (chain 269, portable laptop window P1): the five tools read on main as it stood on 14 November 2026
(production at 85e5b2eeb, in the internal view, 1280 and 390), and the six new faults fixed.

- Battery row 12: "1 days in all" under the income table; one day is "day".
- Battery row 13: the "Price years" choice named its leave-out windows by the table's ids ("less uri 2021", "less caiso
  notices 20230815"); site/lib/priceyears.ts names them in words (ERCOT's three as lib/batterystack.ts's EVENTS, a
  CAISO event by its first day).
- Generator row 4: two capture prices on the face with nothing to say why (23.20 and 32.10 beside 23.27 and 32.17); a
  line under the spans table names the two weighings, each figure with the key it already carries.
- Datacenter row 5: ercot_large_load_status named twice in the source line; SourceLine names a table once.
- Automated Analysis row 7: today's chart printed its record's figures as raw JSON floats; figureText rounds them as the
  chart-maker does.
- Grid row 6: "today so far" over a day that is not today; the heading names the latest day EIA has published.

Node runs the pure functions (no build, no network); the rest reads the sources.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_json(script):
    node = shutil.which("node")
    if not node or not os.path.exists(os.path.join(SITE, "scripts", "alias-register.mjs")):
        raise unittest.SkipTest("node or the site's alias loader is not here")
    r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                       capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-1500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class BatteryDays(unittest.TestCase):
    def test_one_day_is_day(self):
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertNotIn('<V pre={key} s="out" v={st("out")} /> days in all', page)
        self.assertRegex(page, r'<V pre=\{key\} s="out" v=\{st\("out"\)\} /> \{st\("out"\) === 1 /\*[^*]*\*/ \? "day" : "days"\} in all')


class PriceYearsWords(unittest.TestCase):
    def test_leave_out_windows_are_named_in_words(self):
        out = node_json("""
import { windowWords } from "@/lib/priceyears";
const w = (id) => windowWords({ id, kind: "all_less", from: "2018-01", to: "2026-09", months: 105, whole: true, value: 1, unit: "x", entity: "e", variable: "v", ts: "t" });
const ids = ["all_less_uri_2021", "all_less_elliott_2022", "all_less_ercot_heat_2023", "all_less_events", "all_less_caiso_notices_20230815", "all_less_caiso_notices_20261005", "all_less_spp_cold_2025"];
console.log(JSON.stringify(ids.map((id) => [w(id).label, w(id).sentence])));
""")
        labels = [l for l, _ in out]
        self.assertEqual(labels, [
            "Every month held, less Winter Storm Uri (February 2021)",
            "Every month held, less Winter Storm Elliott (December 2022)",
            "Every month held, less the summer 2023 heat",
            "Every month held, less every stress event",
            "Every month held, less CAISO's notice days from 15 August 2023",
            "Every month held, less CAISO's notice days from 5 October 2026",
            "Every month held, less spp cold 2025",
        ])
        self.assertTrue(out[0][1].endswith("with Winter Storm Uri (February 2021) taken out"), out[0][1])
        for label, _ in out[:6]:
            self.assertNotRegex(label, r"_|\b(uri|elliott|ercot heat|caiso notices) \d", label)

    def test_the_named_events_agree_with_the_battery_library(self):
        lib = src("site", "lib", "batterystack.ts")
        events = dict(re.findall(r'(\w+): "([^"]+)"', re.search(r"export const EVENTS: Record<string, string> = \{([^}]*)\}", lib).group(1)))
        py = src("site", "lib", "priceyears.ts")
        named = dict(re.findall(r'(\w+): "([^"]+)"', re.search(r"const NAMED_EVENTS: Record<string, string> = \{([^}]*)\}", py).group(1)))
        self.assertEqual(set(events), set(named))
        norm = lambda s: re.sub(r"[(),]", "", s).lower()
        for k in events:
            self.assertEqual(norm(events[k]), norm(named[k]), k)


class GeneratorTwoCaptures(unittest.TestCase):
    def test_the_line_under_the_spans_table(self):
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        m = re.search(r'\{fuel && mine && s\.twelve && s\.twelve\.capture !== null \? \(\s*<p [^>]*data-two-captures="1">(.*?)</p>', page, re.S)
        self.assertIsNotNone(m)
        body = m.group(1)
        for piece in ('spanNum("twelve", "capture", s.twelve.capture', 'spanNum("twelve", "flat", s.twelve.flat', 'check={capKey("price")}', 'check={capKey("flat")}',
                      "output per MW of that month&apos;s nameplate", "the generation itself"):
            self.assertIn(piece, body, piece)
        # it stands after the spans table and before the battery's line
        self.assertLess(page.index('caption={`${a.name} in ${g.name}, by span`}'), page.index('data-two-captures="1"'))
        self.assertLess(page.index('data-two-captures="1"'), page.index('<p className="mt-2 text-sm">Energy alone.'))

    def test_the_note_says_the_face_now_does(self):
        note = src("docs", "methods", "generator_earns_algorithm.md")
        self.assertNotIn("`cost_of_power.md` says so; the page face does not.", note)
        self.assertIn("since session 5501 (14 November 2026, generator faults row 4) the page face does too", note)


class DatacenterSourceLine(unittest.TestCase):
    def test_each_table_once(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        line = re.search(r"<SourceLine tables=\{\[(.*?)\]\}\n", page, re.S).group(1)
        self.assertEqual(line.count('"ercot_large_load_status"'), 1)
        tool = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn("const named = [...new Set(tables)];", tool)
        self.assertIn("Source: ERW tables {named.map((t, i) =>", tool)


class ResearchFigures(unittest.TestCase):
    def test_the_record_s_figures_are_rounded_as_the_chart_maker_does(self):
        out = node_json("""
import { figureText } from "@/lib/researchrules";
import { chartText } from "@/lib/digest";
const nums = { sigma: 26822.265161999996, value: 1060503.7, margin: 295122.29999999993, strength: 11.0029, threshold: 765381.4, stood_points: 25, history_years: 25.41, history_points: 306, small: 0.012345, words: "n/a" };
const shown = Object.fromEntries(Object.entries(nums).map(([k, v]) => [k, figureText(v)]));
const same = [26822.265161999996, 1060503.7, 11.0029, 25.41, 0.012345, 150.55, -42.123].every((v) => figureText(v) === chartText(v));
console.log(JSON.stringify({ shown, same }));
""")
        self.assertEqual(out["shown"], {"sigma": "26,822", "value": "1,060,504", "margin": "295,122", "strength": "11.00", "threshold": "765,381",
                                        "stood_points": "25", "history_years": "25.41", "history_points": "306", "small": "0.0123", "words": "n/a"})
        self.assertTrue(out["same"])

    def test_the_page_writes_them_through_it_and_the_checker_accepts_the_form(self):
        page = src("site", "app", "research", "page.tsx")
        self.assertIn('import { figureText } from "@/lib/researchrules";', page)
        self.assertIn('<span className="font-mono">{figureText(v)}</span>', page)
        self.assertNotIn('<span className="font-mono">{String(v)}</span>', page)
        check = src("site", "scripts", "check-values.mjs")
        # the value checker's digest_chart rule rounds as the chart-maker does, and a whole number written whole is its raw text
        self.assertIn("const nd = a >= 10000 ? 0 : a >= 100 ? 1 : a >= 1 ? 2 : 4;", check)
        self.assertIn("const chartOk = /^digest_chart\\|/.test(check) && text === digestChartText(Number(raw));", check)
        self.assertIn("text === raw ||", check)


class GridLatestDay(unittest.TestCase):
    def test_the_heading_names_the_latest_day(self):
        mix = src("site", "components", "grid", "MixView.tsx")
        self.assertIn("<h2 className={h2}>{b.label}: the latest day EIA has published, so far</h2>", mix)
        self.assertNotIn(": today so far</h2>", mix)
        self.assertIn('"the latest day EIA has published, so far"', src("tests", "test_session133.py"))
        chk = src("site", "scripts", "check-mix.mjs")
        self.assertEqual(chk.count('"the latest day EIA has published, so far"'), 2)
        self.assertNotIn('"today so far"', chk)


class FaultsRows(unittest.TestCase):
    ROWS = {"battery": (12, 13), "generator": (4,), "datacenter-cost": (5,), "analysis": (7,), "grid": (6,)}

    def test_each_row_is_written_and_fixed(self):
        for tool, ns in self.ROWS.items():
            text = src("docs", "reviews", f"{tool}-faults-2026-11-13.md")
            for n in ns:
                self.assertRegex(text, rf"\n\| {n} \|[^\n]*found in session 5501[^\n]*\| fixed \(session 5501\) \|", (tool, n))
            self.assertIn("## The read of 14 November (session 5501, chain 269)", text, tool)

    def test_no_dash(self):
        for rel in (("tests", "test_session5501.py"), ("site", "lib", "priceyears.ts"), ("site", "lib", "researchrules.ts"),
                    ("site", "app", "cost-of-power", "seller", "page.tsx"), ("site", "components", "grid", "MixView.tsx"),
                    ("docs", "methods", "generator_earns_algorithm.md")) + tuple(("docs", "reviews", f"{t}-faults-2026-11-13.md") for t in self.ROWS):
            text = src(*rel)
            self.assertNotIn(chr(0x2014), text, rel)
            self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
