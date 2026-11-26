"""Session 10402 (chain 720, part D, 26 November 2026): energy equities, a group on the price board and /equities.

Energy Research Warehouse (ERW). Both read the equities page files (site/data/equities/, the data machine's
warehouse/derived/equity_pages.py; contract docs/state/page_files_equities.md). Held here:

- what a reader sees and what the board is handed, drawn and computed by the site's own code without a build
  (site/scripts/test-equities.mjs): with no equities file, with the contract's example files at their real path (nothing
  of an example is shown as real, its rows' names included), and with files of the contract's shape and a test's made-up
  values (the board's rows as they were with the group after them; a held row with no figure; a segment's two weightings
  named plainly; an energy price laid over a line on its own axis; a held share price blank with the filed figures
  drawn; each filing's address; the table's filter and order; the downloads and their readers);
- on the source: /equities is in review and in no menu; the board keeps every column, group and row it had (the lean
  columns are a group's own mark); an equities row opens /equities and never the workbench; the tour stop waits; the
  addresses are in check-routes and the files are traced for the build; no new file holds an em dash.

Nothing here sets a key, reads a table or makes a request.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
NEW = [
    ("site", "lib", "equities.ts"), ("site", "lib", "equitiesfiles.ts"),
    ("site", "app", "equities", "page.tsx"), ("site", "app", "equities", "view.tsx"), ("site", "app", "equities", "reader.ts"),
    ("site", "app", "equities", "rows", "route.ts"), ("site", "app", "equities", "rows", "python", "route.ts"), ("site", "app", "equities", "rows", "stata", "route.ts"),
    ("site", "app", "equities", "filed", "route.ts"), ("site", "app", "equities", "filed", "python", "route.ts"), ("site", "app", "equities", "filed", "stata", "route.ts"),
    ("site", "app", "equities", "list", "route.ts"), ("site", "app", "equities", "list", "python", "route.ts"), ("site", "app", "equities", "list", "stata", "route.ts"),
    ("site", "scripts", "check-equities-files.mjs"),
    ("site", "scripts", "test-equities.mjs"),
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules", "react-dom")), "node or the site's packages are not on this machine")
class WhatAReaderSees(unittest.TestCase):
    def test_the_group_and_the_page_without_a_build(self):
        env = {k: v for k, v in os.environ.items() if k != "ERW_EQUITIES_DIR"}
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-equities.mjs"], cwd=SITE, env=env,
                           capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of energy equities")


class TheSource(unittest.TestCase):
    def test_in_review_and_in_no_menu(self):
        self.assertNotIn('"/equities"', src("site", "lib", "release.ts"))
        self.assertNotIn('"/equities"', src("site", "lib", "pages.ts"))
        page = src("site", "app", "equities", "page.tsx")
        self.assertIn('robots: { index: false, follow: false }', page)
        self.assertIn('title: "Energy equities"', page)

    def test_the_board_keeps_what_it_had(self):
        view = src("site", "components", "board", "BoardView.tsx")
        # every column the board had is still drawn for a group that is not lean
        for head in ("7-day avg", "30-day avg", "12-month avg", "30-day low to high", "One-year range", "Trend", "Latest", "Its date"):
            self.assertIn(f">{head}</th>", view)
        self.assertEqual(view.count("group.lean ? null : <th"), 5)
        self.assertIn('{group.lean ? "Series" : "Price"}', view)
        # the page adds the group through one function and changes nothing else of the file it reads
        page = src("site", "app", "board", "page.tsx")
        self.assertIn("const raw = withEquities(fileJson as unknown as BoardFile, equitiesBoard());", page)
        self.assertIn("const file = holdRows(raw, licenseHeldGrids().map(gridName));", page)
        self.assertIn('import fileJson from "@/data/board.json";', page)
        rows = src("site", "app", "board", "rows", "route.ts")
        self.assertIn("withEquities(holdRows(fileJson as unknown as BoardFile, licenseHeldGrids().map(gridName)), equitiesBoard())", rows)
        # the column count of the board's own groups is the line it was; a lean group has five fewer
        self.assertEqual(view.count("const cols = 8 + MOVES.length + (group.curve ? 1 : 0) + (group.extremes ? 1 : 0);"), 2)
        self.assertIn("const LEAN_LESS = 5;", view)
        lib = src("site", "lib", "equities.ts")
        merge = lib[lib.index("export function withEquities"):lib.index("// ---- The list")]
        self.assertIn("groups: [...file.groups, group]", merge)
        self.assertIn("rows: [...file.rows, ", merge)
        self.assertNotRegex(merge, r"file\.rows\.(filter|map|sort|splice)|file\.groups\.(filter|map|sort|splice)")

    def test_an_equities_row_opens_its_page_and_never_the_workbench(self):
        board = src("site", "lib", "board.ts")
        self.assertIn('r.status === "ok" && !r.open) ? id : null', board)
        bench = src("site", "components", "board", "Workbench.tsx")
        self.assertEqual(bench.count("!r.open"), 2)
        view = src("site", "components", "board", "BoardView.tsx")
        self.assertIn("if (hit.open) { window.location.assign(hit.open); return; }", view)
        self.assertIn('"data-row-href": row.open', view)
        # the row's name is the button it was (tests/test_session412.py): the keyboard opens the page through it
        self.assertIn('{row.status === "ok" ? <button type="button" aria-pressed={open} data-row-open={row.id}', view)

    def test_the_old_boards_last_commit(self):
        # tests/test_session104.py holds that the last commit to touch site/app/board/page.tsx does not say
        # "Session 104" (its own number). This chain's sessions are 10400 to 10599, whose names begin with those
        # words: a commit of this chain that touches that file names its session another way ("s10402").
        r = subprocess.run(["git", "log", "--format=%s", "-1", "--", "site/app/board/page.tsx"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("Session 104", r.stdout)

    def test_no_score_no_signal_no_view(self):
        for parts in NEW[:-1]:
            text = src(*parts)
            self.assertNotRegex(text, r"(?i)outperform|underperform|overweight|undervalued|\bbuy\b|\bsell\b", "/".join(parts))
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("No score, no signal and no view.", view)

    def test_the_page_reads_only_the_contracts_files(self):
        files = src("site", "lib", "equitiesfiles.ts")
        self.assertIn('path.join(process.cwd(), "data", "equities", ...parts)', files)
        self.assertIn('"fixture" in v && v.fixture && !process.env.ERW_EQUITIES_DIR', files)
        view = src("site", "app", "equities", "view.tsx")
        self.assertNotIn("supabase", view.lower())
        self.assertNotIn("fetch(", view)
        # only the SEC's own address is made a link
        self.assertIn(r"/^https:\/\/www\.sec\.gov\//", src("site", "lib", "equities.ts"))

    def test_the_tour_stop_waits(self):
        tour = src("site", "lib", "tour.ts")
        waiting = tour[tour.index("export const WAITING_STOPS"):tour.index("/** The guided path")]
        new = tour[tour.index("export const NEW_STOPS"):tour.index("export const WAITING_STOPS")]
        self.assertNotIn('"/equities"', new)
        stop = waiting[waiting.index('href: "/equities"'):]
        stop = stop[:stop.index("},")]
        self.assertIn("waits: \"the equities page files with figures (site/data/equities/)", stop)
        heads = json.loads(re.search(r"headings: (\[[^\]]*\])", stop).group(1))
        look = re.search(r'look: "((?:[^"\\]|\\.)*)"', stop).group(1)
        for quoted in re.findall(r'\\"([^"\\]+)\\"', look):
            self.assertIn(quoted, heads)
        view = src("site", "app", "equities", "view.tsx")
        for heading in heads:
            self.assertIn(f'<ToolSection title="{heading}"', view)

    def test_the_addresses_are_checked_and_the_files_traced(self):
        routes = src("site", "scripts", "check-routes.mjs")
        for page in ('"/equities"', '"/equities?a=zz&b=zz&p=zz&win=zz&seg=zz&sort=zz"'):
            self.assertIn(page, routes)
        config = src("site", "next.config.ts")
        for route in ("/equities", "/equities/rows", "/equities/filed"):
            self.assertIn(f'"{route}": ["./data/equities/**/*.json"]', config)

    def test_the_contracts_examples_show_nothing(self):
        d = os.path.join(SITE, "data", "equities")
        if not os.path.exists(os.path.join(d, "board.json")):
            self.skipTest("the equities files are not on this machine")
        with open(os.path.join(d, "board.json"), encoding="utf-8") as f:
            board = json.load(f)
        if board.get("example") is not True:
            self.skipTest("the data machine's real files have replaced the examples")
        for name in ("index.json", "energy_prices.json"):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                self.assertIs(json.load(f)["example"], True, name)

    def test_a_real_list_with_nothing_to_draw_is_not_called_unbuilt(self):
        # the files as the data machine first built them on 26 November 2026: 15 segments, no company, no index, no
        # segment line (SEC EDGAR refuses the ERW's contact string; no price source a license allows), 8 energy prices
        # shown. The page says why each part is held and draws the energy prices; "not built yet" is for an example
        # file or no file, and for nothing else
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("if (!list || list.example === true) {", view)
        self.assertNotIn("!picks.length) {", view)
        self.assertEqual(view.count('words="not built yet"'), 1)
        for k in ('k="line|none"', 'k="companies"', 'k="indices"'):
            self.assertIn(k, view)
        self.assertIn('<ToolSection title="Energy prices" id="prices">', view)
        lib = src("site", "lib", "equities.ts")
        # a monthly price's change over a day is its month's in the file: the page says the step, as the board does
        self.assertIn('(freq === "M" && (k === "d" || k === "w"))', lib)

    def test_the_value_check_knows_a_rise_is_written_with_its_sign(self):
        # session 10404: the value check run on a build with window A's files failed 21 of /equities' 43 figures
        # ("+0.32%" against 0.32): the page writes a change above zero with its sign (lib/equities.ts signedPct,
        # signedLevel), and the check's rule for it stands on its own line, beside the text test older tests pin
        text = src("site", "scripts", "check-values.mjs")
        self.assertIn("const equitiesSigned = /^pf\\|equities\\/", text)
        self.assertIn("if (!pass && equitiesSigned && t !== undefined && t !== null && same) pass = true;", text)
        self.assertIn('export const signedPct = (v: number) => `${v > 0 ? "+" : v < 0 ? "-" : ""}${fixed(Math.abs(v), 2)}%`;', src("site", "lib", "equities.ts"))
        rule = re.search(r"const equitiesSigned = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        for key in ("pf|equities/energy_prices.json|series/0/moves/d/pct", "pf|equities/series/XOM.json|moves/ytd/pct",
                    "pf|equities/series/seg-utilities.json|moves_value_weight/y/ch"):
            self.assertRegex(key, rule)
        for key in ("pf|equities/energy_prices.json|series/0/last_value/v", "pf|predict/scores.json|rows/1/moves/d/pct",
                    "pf|equities/series/XOM.json|filed/0/moves"):
            self.assertNotRegex(key, rule)

    def test_no_em_dash(self):
        for parts in NEW:
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
