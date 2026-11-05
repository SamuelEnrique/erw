"""Session 502 (the chain of 21 October 2026, evening, 023, run on portable-laptop): each live view says what it holds
and under which license. /board, both tabs of /prices and every view of /grid carry one line under their title naming
the ERW tables they read and each one's license (components/tool/TableLicenses.tsx, lib/license.ts licenseWords); the
Ask panel says what it reads. Each line's list is the page's own: the board's and the prices tabs' are the lists their
downloads lines already pass, the Grid's views' are what scripts/page_tables.py finds in the components each view draws.
Every table on a line is public in coverage.csv, so "public" is true where the record holds nothing. Energy Research
Warehouse (ERW)."""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import page_tables  # noqa: E402

NODE = shutil.which("node")
LOADER = ["--import", "./scripts/alias-register.mjs"]
DASHES = (chr(0x2014), chr(0x2013))
NEW = [("site", "components", "tool", "TableLicenses.tsx"), ("site", "lib", "gridtables.ts"), ("site", "scripts", "test-session502.mjs"),
       ("tests", "test_session502.py")]

# the components each view of the Grid tool draws (app/grid/page.tsx), with the exports it calls; lib/grid.ts's load
# is called by the page for the Mix and Clean views
VIEWS = {
    "network": [("components/grid/NetworkView.tsx", "NetworkView")],
    "mix": [("components/grid/NowView.tsx", "NowView"), ("components/grid/MixView.tsx", "MixView"),
            ("components/grid/YourGrid.tsx", "GridMixParts"), ("components/grid/Conditions.tsx", "MixTable"), ("lib/grid.ts", "load")],
    "clean": [("components/grid/YourGrid.tsx", "GridCleanParts"), ("components/grid/Emissions.tsx", "EmissionsParts"),
              ("components/grid/MixView.tsx", "MixClean"), ("lib/grid.ts", "load")],
    "gravity": [("components/grid/NetworkView.tsx", "NetworkView"), ("components/grid/ExchangeView.tsx", "ExchangeView")],
}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def ts_list(text):
    return re.findall(r'"([a-z0-9_]+)"', text)


def grid_lists():
    t = src("site", "lib", "gridtables.ts")
    network = ts_list(re.search(r"const NETWORK = \[([^\]]*)\]", t).group(1))
    out = {}
    for v in ("network", "mix", "clean", "gravity"):
        m = re.search(rf"^\s*{v}: (NETWORK|\[([^\]]*)\])", t, re.M)
        out[v] = network if m.group(1) == "NETWORK" else ts_list(m.group(2))
    return out


def board_list():
    return ts_list(re.search(r"const TABLES = \[([^\]]*)\]", src("site", "app", "board", "page.tsx")).group(1))


def prices_lists():
    with open(os.path.join(SITE, "data", "markets.json"), encoding="utf-8") as f:
        markets = json.load(f)
    rows = markets["isos"]  # lib/data.ts: MARKETS = markets.isos
    now = []
    for m in rows:
        for k in ("rt", "da"):
            t = (m.get(k) or {}).get("table")
            if t:
                now.append(t)
    ercot = ts_list(re.search(r"const ERCOT_TABLES = \[([^\]]*)\]", src("site", "app", "prices", "page.tsx")).group(1))
    return now, ercot


def coverage():
    with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


class TheLists(unittest.TestCase):
    def test_each_grid_view_list_is_what_its_components_read(self):
        tables = page_tables.coverage_tables()
        lists = grid_lists()
        for view, parts in VIEWS.items():
            found = set()
            for f, export in parts:
                found |= set(page_tables.walk(os.path.join(SITE, f), tables, root_idents=[export]))
            self.assertEqual(sorted(lists[view]), sorted(found), view)

    def test_the_grid_page_draws_those_components_in_each_view(self):
        page = src("site", "app", "grid", "page.tsx")
        starts = sorted((page.index(f'{{view === "{v}" ?'), v) for v in VIEWS)
        ends = [s for s, _ in starts[1:]] + [page.index("<Decisions />")]
        blocks = {v: page[s:e] for (s, v), e in zip(starts, ends)}
        for view, parts in VIEWS.items():
            for f, export in parts:
                if export == "load":
                    self.assertRegex(page, r'view === "mix" \|\| view === "clean"\) \? await load\(cfg\)')
                else:
                    self.assertIn(f"<{export}", blocks[view], f"{view}: {export}")

    def test_the_board_line_and_the_downloads_take_one_list_the_page_reads(self):
        page = src("site", "app", "board", "page.tsx")
        self.assertIn("under={<TableLicenses tables={TABLES} />} footer={<>", page)   # session 1137: the rows' own CSV, then the downloads
        self.assertIn("<TableDownloads tables={TABLES} /></>}", page)
        found = set(page_tables.read()["/board"]["tables"])
        self.assertEqual(sorted(board_list()), sorted(found))

    def test_the_prices_tabs_lines_and_downloads_take_one_list_each(self):
        page = src("site", "app", "prices", "page.tsx")
        self.assertIn("<TableDownloads tables={tab === \"ercot\" ? ERCOT_TABLES : NOW_TABLES} />", page)
        self.assertIn("<PeakPremiumView under={<TableLicenses tables={ERCOT_TABLES} />} />", page)
        self.assertRegex(page, r'<h1 className="mb-1 text-3xl">Power prices</h1>\s*<TableLicenses tables=\{NOW_TABLES\} />')
        self.assertIn("const NOW_TABLES = MARKETS.flatMap((m) => [m.rt?.table, m.da.table]).filter((t): t is string => Boolean(t));", page)
        now, ercot = prices_lists()
        found = set(page_tables.read()["/prices"]["tables"])
        self.assertTrue(now and ercot)
        self.assertLessEqual(set(now) | set(ercot), found)

    def test_every_table_on_a_line_is_public_in_coverage(self):
        cov = coverage()
        now, ercot = prices_lists()
        every = set(board_list()) | set(now) | set(ercot) | {t for ts in grid_lists().values() for t in ts}
        for t in sorted(every):
            self.assertIn(t, cov, t)
            self.assertEqual(cov[t]["license"], "public", t)


class TheWiring(unittest.TestCase):
    def test_the_lines_sit_under_the_titles(self):
        self.assertIn("{under}", src("site", "components", "tool", "ToolPage.tsx"))
        self.assertIn("under={<TableLicenses tables={GRID_VIEW_TABLES[view]} />}", src("site", "app", "grid", "page.tsx"))
        board = src("site", "components", "board", "BoardView.tsx")
        self.assertLess(board.index('<h1 className="font-serif text-3xl text-accent">Price board</h1>'), board.index("data-board-licenses"))
        view = src("site", "app", "explorer", "ercot-peak-premium", "view.tsx")
        self.assertRegex(view, r'<h1 className="mb-1 text-3xl">ERCOT peak premium</h1>\s*\{under\}')

    def test_the_ask_panel_says_what_it_reads(self):
        page = src("site", "app", "grid", "page.tsx")
        self.assertIn("data-ask-licenses={licenseNeededTables().length}", page)
        self.assertIn("the public tables of the site&apos;s live set", page)
        tools = src("site", "lib", "chat", "tools.ts")
        self.assertIn("if (licenseNeeded(name) && !licenseByGrid(name)) throw new ToolError", tools)

    def test_no_link_to_the_licenses_page_and_release_untouched(self):
        for p in (("site", "components", "tool", "TableLicenses.tsx"), ("site", "lib", "gridtables.ts")):
            self.assertNotIn("/data/licenses\"", src(*p))
            self.assertNotIn("href", src(*p))

    def test_the_line_reads_no_live_set(self):
        t = src("site", "components", "tool", "TableLicenses.tsx")
        self.assertNotIn("supabase", t)
        self.assertNotIn("catalogue", t.split("\n", 8)[-1])

    def test_no_dash(self):
        for p in NEW:
            text = src(*p)
            for d in DASHES:
                self.assertNotIn(d, text, "/".join(p))


class TheWords(unittest.TestCase):
    @unittest.skipUnless(NODE and os.path.isdir(os.path.join(SITE, "node_modules")), "node or the site's packages are not on this machine")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, *LOADER, "scripts/test-session502.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertRegex(r.stdout, r"(\d+) of \1 passed")


if __name__ == "__main__":
    unittest.main()
