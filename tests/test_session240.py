"""Session 240: top blocks. /board and /datacenters on the brand, each with a top block, the long part folded.

The owner's task of 13 October 2026: on /board a top block of the twelve numbers a trader checks first, the wall folded
by group below; on /datacenters a top block (facilities, megawatts, what changed this week), the list grouped by
operator. Here, the sources: the one list of twelve and what it may never hold, the shared pieces the two pages draw
with, the brand's two generic rules, the keys the value check learned, and that nothing the pages showed was dropped.
The built pages are checked by site/scripts/check-board.mjs, check-datacenters.mjs and check-values.mjs.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def twelve():
    lib = src("site", "lib", "board.ts")
    block = lib.split("export const TOP_TWELVE: string[] = [", 1)[1].split("];", 1)[0]
    return re.findall(r'^\s*"([^"]+)",', block, flags=re.M)


class TheTwelve(unittest.TestCase):
    def test_one_list_of_twelve_rows_of_the_board(self):
        ids = twelve()
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(set(ids)), 12)
        self.assertEqual(src("site", "lib", "board.ts").count("export const TOP_TWELVE"), 1)      # the list is in one place
        board = json.loads(src("site", "data", "board.json"))
        rows = {r["id"]: r for r in board["rows"]}
        for i in ids:
            self.assertIn(i, rows, i)
            r = rows[i]
            self.assertEqual(r["status"], "ok", i)
            self.assertEqual(r["freq"], "D", i)                               # a daily series: it has a move over a day and a week
            self.assertTrue(r["moves"]["d"] and r["moves"]["w"], i)
            self.assertGreaterEqual(len(r["spark"]["v"]), 2, i)

    def test_none_goes_dark_on_20_october_and_none_is_paused(self):
        # ISO-NE's, NYISO's and MISO's own prices are "license needed" from 20 October 2026, PJM's are licensed, MISO is paused
        status = json.loads(src("site", "data", "license_status.json"))
        self.assertEqual(status["from"], "2026-10-20")
        held = {"ISO-NE", "MISO", "NYISO"}
        self.assertTrue(held <= set(status["tables"]["price_board_latest"]["publishers"]))
        for i in twelve():
            self.assertIsNone(re.match(r"(isone|nyiso|miso|pjm)-", i), i)
        self.assertIn("export const TOP_NEVER = /^(isone|nyiso|miso|pjm)-/;", src("site", "lib", "board.ts"))
        board = json.loads(src("site", "data", "board.json"))
        rows = {r["id"]: r for r in board["rows"]}
        for i in twelve():
            self.assertNotIn(rows[i]["tags"].get("grid"), held | {"PJM"}, i)

    def test_they_cross_power_gas_crude_products_and_a_macro_line(self):
        board = json.loads(src("site", "data", "board.json"))
        rows = {r["id"]: r for r in board["rows"]}
        groups = [rows[i]["group"] for i in twelve()]
        for g in ("power", "gas", "crude", "products", "rates"):
            self.assertIn(g, groups)
        self.assertLessEqual(groups.count("rates"), 2)                        # one or two macro lines

    def test_a_tile_reads_the_walls_row_by_the_walls_code(self):
        v = src("site", "components", "board", "BoardView.tsx")
        block = v.split("function TopTwelve(", 1)[1].split("\nfunction Headline(", 1)[0]
        self.assertIn("const rows = topRows(file);", block)
        for piece in ("data-n={`top|${r.id}|last`}", "fmt(r.last.v, r.unit)", "data-n={`top|${r.id}|${k}`}", "signed(m.ch, r.unit)", "<Spark row={r} top />",
                      'label: k === "d" ? "Day" : "Week"', "dateWords(r.last.t, r.freq)", "PLACEHOLDER["):
            self.assertIn(piece, block, piece)
        self.assertIn("<TopTwelve file={file} onOpen={onOpen} />\n      <Headline ", v)      # above the strip the page had, which stays
        self.assertNotRegex(block, r"#[0-9a-fA-F]{3,6}\b")


class TheWallFolded(unittest.TestCase):
    def test_every_group_is_a_fold_and_no_row_is_dropped(self):
        v = src("site", "components", "board", "BoardView.tsx")
        self.assertEqual(v.count("<GroupFold "), 2)                           # the groups' table and the week's
        self.assertIn("useState<Record<string, boolean>>(() => ({ [file.groups[0].id]: true }))", v)      # the first group open as the page opens
        self.assertIn("<tbody>{rows.map((r) => <PriceRow key={r.id} row={r} group={group} open={open === r.id} onOpen={onOpen} file={file} />)}</tbody>", v)
        self.assertIn("data-count={group.id}>{rows.length}", v)
        self.assertIn("data-n={`fold|${group.id}|last`}", v)                  # a closed group keeps its first number in view
        for kept in ("function Headline(", "function WeekTable(", "function RangeBar(", "function Curve(", "<Workbench file={file}", "<BenchPlaceholder />",
                     "The week&apos;s highest real-time intervals", "PLACEHOLDER.paused", "PLACEHOLDER.licensed", 'data-fold-all="1"'):
            self.assertIn(kept, v, kept)
        self.assertNotRegex(v, r"#[0-9a-fA-F]{3,6}\b")                        # no color literal in the board's view
        self.assertNotRegex(v, r"text-\[\d+px\]")                            # the brand's sizes only

    def test_the_page_takes_the_brand(self):
        self.assertIn("return <Brand><BoardView file={file} /></Brand>;", src("site", "app", "board", "page.tsx"))
        self.assertIn('"/board": "review"', src("site", "lib", "release.ts"))

    def test_the_browser_check_reads_the_top_block_and_the_folds(self):
        c = src("site", "scripts", "check-board.mjs")
        for piece in ("b.topRows(file)", "b.TOP_NEVER.test(id)", "data-top-spark=", "data-group-fold=", "fold|${g.id}|last", "[data-group=\"gas\"] summary"):
            self.assertIn(piece, c, piece)
        self.assertIn("the twelve of the top block", src("site", "scripts", "test-board.mjs"))


class TheSharedPieces(unittest.TestCase):
    def test_the_tile_and_the_folds_are_shared_components(self):
        t = src("site", "components", "tool", "ToolPage.tsx")
        for name in ("export function NumberTile(", "export function NumberTileGrid(", "export function GroupFold(", "export function FoldRows("):
            self.assertIn(name, t, name)
        tile = t.split("export function NumberTile(", 1)[1].split("export function NumberTileGrid(", 1)[0]
        self.assertIn('m.dir > 0 ? "text-up" : m.dir < 0 ? "text-down" : "text-muted"', tile)      # the tokens' up and down colors
        self.assertIn(chr(0x25B2), tile)                                      # the arrow up
        self.assertIn(chr(0x25BC), tile)                                      # the arrow down
        self.assertNotRegex(t.split("// ---- Session 240", 1)[1], r"#[0-9a-fA-F]{3,6}\b")
        self.assertIn("<tbody hidden={!open} data-fold-rows={id}>{children}</tbody>", t)        # a closed group's rows stay in the page

    def test_the_brand_has_two_generic_rules_and_they_name_no_page(self):
        css = src("site", "app", "tokens.css")
        block = css.split("/* ---- session 240:", 1)[1]
        self.assertIn(".brand-a details[data-group-fold] > summary::before", block)
        self.assertIn(".brand-a table[data-dense] tbody td.text-right", block)
        rules = re.sub(r"/\*.*?\*/", "", "/* ---- session 240:" + block, flags=re.S)
        self.assertNotRegex(rules, r"board|datacenter")
        self.assertNotRegex(rules, r"#[0-9a-fA-F]{3,6}\b")
        for line in rules.splitlines():
            if "{" in line or line.strip().endswith(","):
                self.assertTrue(line.startswith(".brand-a "), line)           # every rule is scoped to the brand


class Datacenters(unittest.TestCase):
    def test_a_top_block_of_three_numbers_each_with_its_check_key(self):
        b = src("site", "app", "datacenters", "Body.tsx")
        self.assertEqual(b.count("<HeadlineNumber"), 3)
        for key in ('check="datacenters|count"', 'check="datacenters|mw_total"', "check={`datacenters|first_week|${start}`}", "check={`datacenters|status_mw|${k}`}",
                    'check="datacenters|counted"', 'check="datacenters|no_us_state"', 'check="datacenters|cancelled"', 'check="datacenters|n_with_mw"', 'check="datacenters|n_first_story"'):
            self.assertIn(key, b, key)
        self.assertIn('label="Facilities held"', b)
        self.assertIn('label="Megawatts stated"', b)
        self.assertIn('label="First reported this week"', b)
        self.assertIn("6 * DAY", b)                                           # the seven days that end today

    def test_what_is_not_held_is_said(self):
        b = src("site", "app", "datacenters", "Body.tsx")
        self.assertIn("Not held: a facility whose status or megawatts changed this week.", b)
        self.assertIn("its status date is empty on every row", b)
        self.assertIn('title="What changed this week"', b)

    def test_the_list_is_grouped_by_operator_and_keeps_its_rows_and_filters(self):
        t = src("site", "app", "datacenters", "DatacentersTable.tsx")
        self.assertIn("export function byOperator(rows: Facility[]): OperatorGroup[]", t)
        self.assertIn("Number(!a.operator) - Number(!b.operator) || b.mw - a.mw || b.rows.length - a.rows.length || a.operator.localeCompare(b.operator)", t)      # the largest first, the rows with no operator stated last
        self.assertIn("<FoldRows ", t)
        self.assertIn("check={`datacenters|operator_count|${g.operator}`}", t)
        self.assertIn("check={`datacenters|operator_mw|${g.operator}`}", t)
        self.assertIn('<tr key={f.id} className="border-b border-rule align-top">', t)             # the rows as they were
        for name in ('name="Country"', 'name="State"', 'name="Status"', 'name="Operator"', 'name="Source"', "MW at least"):
            self.assertIn(name, t, name)
        for head in ("First reported", "Operator, site", "Place", "Status", "Planned year", "Power", "Sources"):
            self.assertIn(">" + head + "</th>", t, head)
        p = src("site", "app", "datacenters", "page.tsx")
        self.assertIn("<Brand>", p)
        self.assertIn('<Link href="/map">project map</Link>', p)              # the map link stays
        self.assertIn('title="Datacenter power tracker"', p)

    def test_the_value_check_knows_the_new_keys(self):
        c = src("site", "scripts", "check-values.mjs")
        for what in ("status_mw", "first_week", "n_first_story", "operator_count"):
            self.assertIn('if (what === "%s")' % what, c, what)
        self.assertIn("(mw_total|state_mw|operator_mw|status_mw)", c)
        self.assertIn("first:extra->>first_story_at", c)


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("site", "app", "board", "page.tsx"), ("site", "components", "board", "BoardView.tsx"), ("site", "components", "board", "Workbench.tsx"),
                      ("site", "lib", "board.ts"), ("site", "components", "tool", "ToolPage.tsx"), ("site", "app", "tokens.css"),
                      ("site", "app", "datacenters", "page.tsx"), ("site", "app", "datacenters", "Body.tsx"), ("site", "app", "datacenters", "DatacentersTable.tsx"),
                      ("site", "scripts", "check-board.mjs"), ("site", "scripts", "test-board.mjs"), ("site", "scripts", "check-values.mjs"),
                      ("tests", "test_session240.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
