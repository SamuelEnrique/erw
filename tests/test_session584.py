"""Session 584 (the chain of 22 October 2026, night, 034, code machine): 390 pixels on every page.
site/scripts/check-390.mjs reads every page of check-values' list in the internal view at 390 by 844 as a phone and
lists the content wider than the window, the tables with no sideways scroll frame and the SVG labels cut. The fixes are
in tokens.css and the shared charts only: a select narrows to its frame; the mix bar's notes wrap; the heat legend's
blank key takes a line of its own; a reference line's long name wraps; category, group and date labels stay inside the
drawing; the time chart's names stay above its bottom. No value moves. Energy Research Warehouse (ERW)."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))
TOUCHED = [
    ("site", "scripts", "check-390.mjs"), ("site", "app", "tokens.css"), ("site", "components", "svgchart.tsx"),
    ("site", "components", "TimeChart.tsx"), ("site", "components", "EventStudy.tsx"),
    ("site", "components", "tool", "GroupedBars.tsx"), ("site", "components", "tool", "SeriesChart.tsx"),
    ("tests", "test_session584.py"),
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCheck(unittest.TestCase):
    def test_no_dashes(self):
        for parts in TOUCHED:
            text = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, text, f"{'/'.join(parts)} holds a dash")

    def test_reads_check_values_list_as_a_phone_in_the_internal_view(self):
        t = src("site", "scripts", "check-390.mjs")
        self.assertIn('"check-values.mjs"), "--list"]', t)
        self.assertIn("[...j.pages, ...j.internal]", t)
        self.assertIn('width: 390, height: 844, deviceScaleFactor: 1, mobile: true', t)
        self.assertIn("await unlock(base)", t)
        self.assertNotIn("process.argv[2] === \"--write\"", t)

    def test_three_measures_and_exit_codes(self):
        t = src("site", "scripts", "check-390.mjs")
        for key in ("wide: wide.slice(0, 12)", "tables, labels", "scrollWidth: document.documentElement.scrollWidth"):
            self.assertIn(key, t)
        self.assertIn("process.exit(failed ? 2 : withFindings ? 1 : 0)", t)
        # a closed <details> is not drawn; a text's em box is not a cut
        self.assertIn('e.parentElement.tagName === "DETAILS" && !e.parentElement.open', t)
        self.assertIn("v > 3.5", t)


class TheFixes(unittest.TestCase):
    def test_select_narrows_to_its_frame(self):
        css = src("site", "app", "tokens.css")
        self.assertRegex(css, r"\.brand-a select \{\s*max-width: 100%;\s*\}")

    def test_mix_bar_notes_wrap(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("const tall = TOP + H + BOT + 13 * Math.max(0, notes.length - 1);", s)
        self.assertIn('<tspan key={j} x={0} dy={j ? 13 : 0}>{ln}</tspan>', s)
        self.assertNotIn('narrow.map((s) => `${s.name} ${s.share.toFixed(1)}%`).join("; ")', s)

    def test_heat_legend_blank_key_on_its_own_line(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("const split = 4 + span > W - 4;", s)
        self.assertIn("const height = TOP + rows.length * ch + BOT + (split ? 16 : 0);", s)
        self.assertIn('data-legend-split={split ? "1" : undefined}', s)

    def test_reference_name_wraps_and_labels_clamp(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("wrapName(r.name, Math.max(40, plotR - L - 4), 11)", s)
        self.assertIn("x={Math.max(Math.min(cx(i), W - 1 - textWidth(c, 11) * 0.55), textWidth(c, 11) * 0.55 + 1)}", s)
        g = src("site", "components", "tool", "GroupedBars.tsx")
        self.assertIn("x={inside(x0 + (bw * n) / 2, g.sub)}", g)
        self.assertIn("x={inside(x0 + (bw * n) / 2, g.label)}", g)
        sc = src("site", "components", "tool", "SeriesChart.tsx")
        self.assertIn("x={Math.max(Math.min(cx(i), W - 1 - s.length * 3.3), s.length * 3.3 + 1)}", sc)

    def test_time_chart_names_stay_above_the_bottom(self):
        t = src("site", "components", "TimeChart.tsx")
        self.assertIn("const floorY = height - 8;", t)
        i, j = t.index("const floorY"), t.index("for (let i = labels.length - 2; i >= 0; i--)")
        self.assertLess(i, j, "the last name is clamped before the names above it make room")

    def test_event_study_margin_and_dates(self):
        e = src("site", "components", "EventStudy.tsx")
        self.assertIn("L = Math.max(64, Math.ceil(tickW) + 10)", e)
        self.assertIn("x={dayX(i)}", e)
        self.assertEqual(len(re.findall(r"x=\{x\(i\)\} y=\{H - 8\}", e)), 0)


if __name__ == "__main__":
    unittest.main()
