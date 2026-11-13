"""Session 1898: three faults session 1885 found walking the lab's path on 13 November 2026 (docs/reviews/lab-path.md,
"Walked 13 November 2026 (session 1885)", faults 2 to 4). One class a fault.

No network, no model, no browser. Nothing here sets the environment at import.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node_ok():
    return shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules"))


class Fault2WaitsForTheOwnersRuling(unittest.TestCase):
    """Fault 2: "The facilities against each grid" prints "license needed" (note 1, the facilities' hold) in the Peak
    hour MW and Capacity MW columns of every grid and in ERCOT's Reserve margin.

    Session 1898 printed the grids' own figures (KEY_STAT_TABLE in Num.tsx and check-holds.mjs); it landed with chain
    217's stack at b1bc8829f. The same cells are row 4 of docs/reviews/datacenter-faults-2026-11-11.md, whose state is
    "ruling": the owner decides whether a grid's public columns show while its facility counts are held (the state
    review of 6 November, item 28; the recommendation was yes). Session 1905 put the default back until the owner rules:
    every dcgrid| key is the held facilities table's, and the cells carry footnote 1."""

    def test_no_second_word_map_in_either_file(self):
        self.assertNotIn("KEY_STAT_TABLE", src("site", "components", "Num.tsx"))
        self.assertNotIn("KEY_STAT_TABLE", src("site", "scripts", "check-holds.mjs"))

    def test_every_dcgrid_key_is_the_facilities_table(self):
        for parts in (("site", "components", "Num.tsx"), ("site", "scripts", "check-holds.mjs")):
            self.assertIn('dcgrid: "datacenter_facilities"', src(*parts), "/".join(parts))

    def test_the_faults_file_row_is_the_owners(self):
        row = next(ln for ln in src("docs", "reviews", "datacenter-faults-2026-11-11.md").splitlines() if ln.startswith("| 4 |"))
        self.assertTrue(row.rstrip().rstrip("|").rstrip().endswith("ruling"), row[-200:])

    @unittest.skipUnless(node_ok(), "node or site/node_modules is not on this machine")
    def test_check_holds_judges_every_grid_cell_held(self):
        script = (
            "import { judgeKey } from './scripts/check-holds.mjs';"
            "const held = new Map([['datacenter_facilities', { byGrid: false, grids: new Set() }]]);"
            "const out = {};"
            "for (const k of ['dcgrid|peak_mw|ERCOT', 'dcgrid|capacity_mw|PJM', 'dcgrid|reserve_margin|ERCOT', 'dcgrid|planned|ERCOT'])"
            "  out[k] = judgeKey(k, held, new Set()) ? 'held' : 'free';"
            "console.log(JSON.stringify(out));"
        )
        r = subprocess.run(["node", "--input-type=module", "-e", script], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(set(got.values()), {"held"}, got)


class Fault3TheNetExportCardHasNoUnitWithoutAFigure(unittest.TestCase):
    """Fault 3: on /grid the Lower 48's second card read "Net export" then "by grid MW": words where the figure goes,
    with the unit after them (and a grid with no tie read "not reported MW").

    Fix: components/grid/NowView.tsx gives the card its unit only when the ties carry a figure
    (unit={ties.length ? "MW" : undefined}); the words stand alone. components/tool/ToolPage.tsx HeadlineNumber draws
    no unit when none is given."""

    def card(self):
        s = src("site", "components", "grid", "NowView.tsx")
        i = s.index('label={ties.length && !out ? "Net import" : "Net export"}')
        return s[i:s.index("/>", s.index("note={ties.length", i))]

    def test_the_unit_follows_the_figure(self):
        c = self.card()
        self.assertIn('unit={ties.length ? "MW" : undefined}', c)
        self.assertNotIn('unit="MW"', c)
        # the words are still the card's (tests/test_session266.py holds them)
        self.assertIn('grid.slug === "us48" ? "by grid" : "not reported"', c)

    def test_headline_number_draws_no_unit_when_none_is_given(self):
        s = src("site", "components", "tool", "ToolPage.tsx")
        self.assertIn('{unit ? <span className="ml-1 font-sans text-sm text-muted">{unit}</span> : null}', s)


class Fault4HeldStoriesAreSaidHeldNotUnmatched(unittest.TestCase):
    """Fault 4: the grid page's "In the news" held the count ("license needed scored stories since 2026-10-30") and then
    said "No story in the last 14 days matched", which reads as a search of the held table that found nothing.

    Fix: components/grid/YourGrid.tsx News asks heldBy for its own check key (gridnews| is news_index, held whole from
    2026-10-21) before it draws anything; held, the section is one sentence that says the stories are held for a license
    and why, with data-license-held and the hold's title, and no count, no list, no "No story ... matched"."""

    def news(self):
        s = src("site", "components", "grid", "YourGrid.tsx")
        return s[s.index("function News("):s.index("// ------------------------------------------------------------------ the page")]

    def test_the_hold_is_asked_before_anything_is_drawn(self):
        n = self.news()
        self.assertIn("const key = `gridnews|${g.slug}|${d.newsSince}|n`;", n)
        ask = n.index("const held = heldBy(key);")
        self.assertLess(ask, n.index("if (held) {"))
        self.assertLess(n.index("if (held) {"), n.index("<Num check={key} raw={n}>"))
        self.assertIn('import { Num, heldBy } from "@/components/Num";', src("site", "components", "grid", "YourGrid.tsx"))

    def test_the_held_branch_says_only_the_hold(self):
        n = self.news()
        branch = n[n.index("if (held) {"):n.index("  return (\n    <>\n      <div className=\"mb-2 text-sm\">")]
        self.assertIn("data-license-held={held.table} title={held.title}", branch)
        self.assertIn("The scored stories are held for a license (license needed)", branch)
        self.assertNotIn("No story", branch)
        self.assertNotIn("<Num", branch)
        self.assertNotIn("d.news", branch)
        # the empty-result line stays for a public table that found nothing
        self.assertIn("No story in the last 14 days matched.", n[n.index("<Num check={key} raw={n}>"):])

    def test_news_index_is_held_and_gridnews_names_it(self):
        self.assertEqual(json.loads(src("site", "data", "license_status.json"))["tables"]["news_index"]["status"], "license needed")
        self.assertIn('gridnews: "news_index"', src("site", "components", "Num.tsx"))


class NoDashes(unittest.TestCase):
    def test_no_em_or_en_dash_in_the_files_written(self):
        for parts in (("tests", "test_session1898.py"), ("site", "components", "Num.tsx"), ("site", "scripts", "check-holds.mjs"),
                      ("site", "components", "grid", "NowView.tsx"), ("site", "components", "grid", "YourGrid.tsx")):
            s = src(*parts)
            self.assertEqual(s.count(chr(0x2014)) + s.count(chr(0x2013)), 0, "/".join(parts))


if __name__ == "__main__":
    unittest.main()
