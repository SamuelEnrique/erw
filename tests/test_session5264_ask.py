"""Session 5264 (window P3's close-out of 14 November 2026): a hub spread belongs to its two hubs' grids.

Energy Research Warehouse (ERW). tests/test_session137.py failed on main in the Ask panel's own script
(site/scripts/test-ask-panel.mjs; window P1 found it on 13 November 2026): a search of the price board for ERCOT's
panel returned "caiso-th-sp15-gen-apnd-ercot-hb-hubavg-da", CAISO's SP15 less ERCOT's hub average.

The cause. The panel's page tool (site/lib/chat/panel.ts boardRows) returned a grid's rows and the rows of no grid, and
took a row with no `grid` tag for a row of no grid. The board's group "Hub spreads, within and across grids" (session
1606) tags its rows with a scope ("within", "across") and no grid. So ERCOT's panel read CAISO's own spread, SPP's own
spread and the spreads across two grids.

The fix. gridsOf: a tagged row is its grid's; a hub spread is of the grids of the two hubs its id is made of, each hub a
row of the board that carries its grid; any other untagged row is the grid its id begins with (lib/board.ts gridOfRow)
or no grid's. boardRows returns a row only when every grid it is of is the panel's; a spread whose hubs cannot be told
is returned to no panel.

Held here with no node and no model: the source, the count of the script's tests, and on the board's file as it stands
the two facts the fix leans on (the spreads carry no grid tag; each one's id is two hubs the board names). The
behaviour itself is the script's ninth test, which tests/test_session137.py runs where the site's packages are.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTHER = re.compile(r"(^|-)(caiso|miso|pjm|nyiso|isone|spp)-")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def board():
    return json.loads(src("site", "data", "board.json"))["rows"]


def grid_tag(r):
    return (r.get("tags") or {}).get("grid")


def hubs(rows):
    """{a hub's id without its market: its grid}, from the rows that carry a grid and end in the market."""
    return {re.sub(r"-(da|rt)$", "", r["id"]): grid_tag(r).upper() for r in rows if grid_tag(r) and re.search(r"-(da|rt)$", r["id"])}


def grids_of_spread(r, hub):
    """panel.ts gridsOf for a hub spread, as the test reads it: the two hubs' grids, or None."""
    stem = re.sub(r"-(da|rt)$", "", r["id"])
    for m in re.finditer("-", stem):
        a, b = hub.get(stem[:m.start()]), hub.get(stem[m.start() + 1:])
        if a and b:
            return sorted({a, b})
    return None


class TheRule(unittest.TestCase):
    def test_the_panel_asks_each_rows_grids_not_its_tag_alone(self):
        p = src("site", "lib", "chat", "panel.ts")
        self.assertIn("export function gridsOf(", p)
        self.assertIn('import { gridOfRow } from "@/lib/board";', p)
        rows = p[p.index("export function boardRows("):p.index("export function supplyRows(")]
        self.assertIn("const g = gridsOf(r); return g !== null && g.every((x) => x === mine);", rows)
        self.assertNotIn("!r.tags?.grid || r.tags.grid.toUpperCase() === iso.toUpperCase()", p)     # the rule that had the gap
        of = p[p.index("export function gridsOf("):p.index("export function boardRows(")]
        self.assertIn('r.group === "hubspread" || r.tags?.scope === "within" || r.tags?.scope === "across"', of)
        self.assertIn("return null;", of)                      # a spread whose hubs cannot be told: no panel's

    def test_the_scripts_ninth_test_and_the_count_the_suite_asks_for(self):
        s = src("site", "scripts", "test-ask-panel.mjs")
        self.assertEqual(len(re.findall(r"^test\(", s, re.M)), 9)
        self.assertIn("a hub spread is of its two hubs' grids: a panel reads its own grid's spreads and no other", s)
        self.assertIn('self.assertIn("9 tests pass", r.stdout)', src("tests", "test_session137.py"))

    def test_the_method_note_and_the_faults_file_say_it(self):
        self.assertIn("A hub spread is its hubs' grids' (session 5264, 14 November 2026)", src("docs", "methods", "ask_ercot.md"))
        self.assertIn("## Found after the table: the panel read other grids' hub spreads (session 5264, 14 November 2026)", src("docs", "reviews", "ask-faults-2026-11-05.md"))


class TheBoardsFileAsItStands(unittest.TestCase):
    """The two facts the fix leans on, read from site/data/board.json. A failure here says the board moved, and how."""

    def test_the_cause_the_hub_spreads_carry_no_grid_tag_and_the_old_rule_let_others_in(self):
        rows = board()
        spreads = [r for r in rows if r["group"] == "hubspread"]
        if not spreads or all(grid_tag(r) for r in spreads):
            self.skipTest("the board holds no hub spread without a grid tag: the tag's own rule holds them")
        old = [r["id"] for r in rows if not grid_tag(r) or grid_tag(r) == "ERCOT"]       # the rule until session 5264
        leaked = [i for i in old if OTHER.search(i)]
        self.assertTrue(leaked)                                                         # the fault, on this file
        hub = hubs(rows)
        new = [r["id"] for r in rows if (grid_tag(r) == "ERCOT") or (not grid_tag(r) and (r["group"] != "hubspread" or grids_of_spread(r, hub) == ["ERCOT"]))]
        self.assertEqual([i for i in new if OTHER.search(i)], [])
        self.assertEqual(set(old) - set(new), {r["id"] for r in spreads if grids_of_spread(r, hub) != ["ERCOT"]})   # nothing else left out

    def test_every_hub_spread_is_two_hubs_the_board_names(self):
        rows = board()
        hub = hubs(rows)
        untold = [r["id"] for r in rows if r["group"] == "hubspread" and not grid_tag(r) and grids_of_spread(r, hub) is None]
        self.assertEqual(untold, [], "a hub spread whose hubs the board does not name is read by no panel, its own grid's included")

    def test_no_untagged_row_outside_the_spreads_begins_with_a_grids_name(self):
        # such a row is that grid's by its id (lib/board.ts gridOfRow); none stands today, so nothing else changed for ERCOT
        named = [r["id"] for r in board() if not grid_tag(r) and r["group"] != "hubspread" and re.match(r"(ercot|caiso|miso|pjm|nyiso|isone|spp)-", r["id"])]
        self.assertEqual(named, [])


if __name__ == "__main__":
    unittest.main()
