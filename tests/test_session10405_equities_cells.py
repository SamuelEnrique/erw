"""Session 10405 (chain 720, part E): the equities page and the board's group read the fields the contract gained.

Window A answered data requests 571 and 572 in the contract (docs/state/page_files_equities.md, the dated lines of
26 November 2026): each company of the list may carry `last_close`, `moves` and `market_value`; each `ok` row of the
board file may carry the board's own `avg7`, `avg30`, `avg365`, `lo30`, `hi30` and `range`. No file carries them yet
(the equity side is held). The page reads them as additions: a list and a board file with none of them are drawn as
they were. The Node test draws both states from a fixture.

    python -m pytest tests/test_session10405_equities_cells.py
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_what_a_reader_sees(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-equities-cells.mjs"],
                           capture_output=True, text=True, cwd=SITE, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of the equities list's and board rows' new fields")


class TheFieldsAreAdditions(unittest.TestCase):
    def test_the_columns_are_drawn_only_when_a_company_holds_one(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("const priced = companiesPriced(list.companies);", view)
        self.assertIn("...(priced ? pricedCells(c) : []),", view)
        # the seven columns the table had are in their places
        # (session 10414: the seventh, "Filed figures", is the newest period filed and its revenue where the list
        # carries them, and "Filed figures" as it was in a list that does not)
        self.assertIn('head={[sortHead("name"), sortHead("ticker"), sortHead("exchange"), sortHead("segment"), "Industry", <span key="p">Share price: {sortHead("first")} to {sortHead("last")}</span>,', view)
        self.assertIn('] : ["Filed figures"]),', view)

    def test_a_figures_key_names_the_companys_place_in_the_file(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("const i = list.companies.indexOf(c);", view)
        self.assertIn('pfKey(LIST, ["companies", i, "last_close", "v"])', view)
        self.assertIn('pfKey(LIST, ["companies", i, "market_value", "v"])', view)

    def test_the_group_is_lean_until_a_row_carries_the_boards_other_cells(self):
        lib = src("site", "lib", "equities.ts")
        self.assertIn("const group: Group = { ...eq.group, lean: eq.example === true || !eq.rows.some(hasWideCells) };", lib)
        self.assertIn('const WIDE_CELLS = ["avg7", "avg30", "avg365", "lo30", "hi30", "range"] as const;', lib)

    def test_the_value_check_reads_a_companys_rise_with_its_sign(self):
        text = src("site", "scripts", "check-values.mjs")
        rule = re.search(r"const equitiesSigned = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        for key in ("pf|equities/index.json|companies/3/moves/d/pct", "pf|equities/index.json|companies/12/moves/ytd/ch"):
            self.assertRegex(key, rule)
        for key in ("pf|equities/index.json|companies/3/last_close/v", "pf|equities/index.json|companies/3/market_value/v"):
            self.assertNotRegex(key, rule)

    def test_no_em_dash(self):
        self.assertNotIn(EM, src("site", "scripts", "test-equities-cells.mjs"))
        self.assertNotIn(EM, src("tests", "test_session10405_equities_cells.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
