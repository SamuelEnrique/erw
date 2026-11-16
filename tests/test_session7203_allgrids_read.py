"""Session 7203 (chain 302, goal 4): the All grids tab read for five cases, and the site faults the read found.

The read is docs/reviews/allgrids-read-2026-11-16.md: numbered rows, each a site fault fixed with a test, a request of
the data machine, a license or a ruling. The fixes are held on the drawn tab by Node (site/scripts/test-allgrids-read.mjs,
run here): the whole tab is drawn to HTML without a build, and "Your load" is run through its own model on the same files.
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheTabDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-allgrids-read.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 25, self.out[-500:])

    def test_each_site_row_of_the_read_has_its_check(self):
        for row in (1, 2, 3, 7, 10, 12):
            self.assertRegex(self.out, rf"(?m)^ok   row {row}: ", f"row {row} of the read is held on the drawn tab")

    def test_the_two_views_agree_on_the_prices_they_share(self):
        got = re.findall(r'(?m)^ok   "Your load" and the tab agree on (LZ_WEST|HB_WEST)\'s (day-ahead|real-time) price', self.out)
        self.assertEqual(sorted(got), sorted([("LZ_WEST", "day-ahead"), ("LZ_WEST", "real-time"), ("HB_WEST", "day-ahead"), ("HB_WEST", "real-time")]))


class TheRead(unittest.TestCase):
    def test_every_row_is_fixed_requested_or_written_for_a_ruling(self):
        doc = src("docs", "reviews", "allgrids-read-2026-11-16.md")
        rows = re.findall(r"(?m)^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (site|data machine|license|ruling) \| ([^|]+) \|$", doc)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, 18)), "seventeen rows, numbered in order")
        for n, _, _, _, kind, state in rows:
            if kind == "site":
                self.assertTrue(state.strip().startswith("fixed"), f"row {n}: a site fault is fixed")
            elif kind == "data machine":
                self.assertRegex(state, r"requested \(row \d+\)|row \d+|known", f"row {n}: a data fault names its request")
            else:
                self.assertIn("default", state, f"row {n}: a license or a ruling is written with its default")
        self.assertEqual(sorted({int(x) for r in rows for x in re.findall(r"requested \(row (\d+)\)", r[5])}), [20, 21, 22, 23, 24, 25])
        self.assertEqual(len(re.findall(r"(?m)^- \*\*", doc.split("## What a lab's reader still cannot get from the tab, and why")[1])), 5)

    def test_the_fixes_are_in_the_source(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('<span className="mr-1 text-xs" data-da="1">da</span>', v)
        self.assertIn("would itself do to them is not modelled.", v)
        self.assertIn("Each is rounded to the cent after B less A is taken", v)
        self.assertIn('r.kind === "grid"', v)
        self.assertIn("deliveryStat(DELIVERY.rows, x.mw, `${slugOf(u)}:transmission`)", v, "the same function \"Your load\"'s delivery table draws with")
        s = src("site", "app", "cost-of-power", "LargeLoadSection.tsx")
        self.assertIn("function GridPanel(", s)
        self.assertIn('if (r.kind === "grid") return <GridPanel r={r} x={x} />;', s)
        css = src("site", "app", "tokens.css")
        self.assertEqual(css.count("{"), css.count("}"))
        self.assertIn(".brand-a [data-allgrids] tbody td [data-da] {", css)

    def test_no_em_or_en_dash(self):
        for parts in (("docs", "reviews", "allgrids-read-2026-11-16.md"), ("site", "scripts", "test-allgrids-read.mjs"), ("tests", "test_session7203_allgrids_read.py")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)


if __name__ == "__main__":
    unittest.main()
