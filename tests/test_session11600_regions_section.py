"""Session 11600 (chain 780, part A): "Where the next gigawatts can go", the regions section of the All grids tab.

Samuel ruled on 22 October 2026 that the siting question lives on the All grids tab of /cost-of-power, not on a page of
its own. The data machine writes each place's counts into site/data/siting/regions (the contract
docs/state/page_files_siting_regions.md); this section sets them side by side:

- one table of every place (a region, a market operator or a large balancing authority), a column a count; each column
  sorts from its head, and the columns shown are the reader's choice;
- a place opened shows everything its own file holds: its counts, its hubs, its top constraints, its partners, the
  large-load rules of its utilities, its one small trend;
- two places side by side as A and B; the rows shown as a CSV with a Python and a Stata reader;
- a count held for a license is a blank with "license needed" on hover; a count of a table the site itself holds is a
  blank whatever the file carries; nothing is scored, ranked or advised.

The tab keeps everything it had, in the order it had it: the section is one import and one line of AllGridsView.tsx.

    python -m pytest tests/test_session11600_regions_section.py
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
TOOL = os.path.join(SITE, "app", "cost-of-power")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
EM = chr(0x2014)
# the section's files stand in the tool's own folder: a folder under it would read as one more address of the tool
# (tests/test_session138.py and test_session194.py hold the tool to its four)
FILES = ["regions.ts", "regionsdata.ts", "RegionsSection.tsx", "RegionsChoices.tsx", "RegionsDownload.tsx"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_what_a_reader_sees(self):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-regions-section.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of the regions section of the All grids tab")


class TheTabKeepsWhatItHad(unittest.TestCase):
    def test_the_section_is_one_import_and_one_line_of_the_tab(self):
        view = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertEqual(view.count('import { RegionsSection } from "./RegionsSection";'), 1)
        # one tool, one page, one address: the section adds no folder under the tool
        self.assertEqual(sorted(x for x in os.listdir(TOOL) if os.path.isdir(os.path.join(TOOL, x))), ["battery", "months.csv", "seller", "tables.csv"])
        self.assertEqual(view.count("<RegionsSection q={q} />"), 1)
        self.assertEqual(view.count("RegionsSection"), 3)   # the import names it twice, the tab mounts it once
        # after the hub table's method line and before the large-load rules, which stand as they stood
        self.assertLess(view.index("data-allgrids-method"), view.index("<RegionsSection q={q} />"))
        self.assertLess(view.index("<RegionsSection q={q} />"), view.index("<LargeLoadSection q={q} x={x} />"))

    def test_the_tabs_own_rule_of_one_titled_box_stands(self):
        # tests/test_session714.py: the tab's file holds one ` title=` (its input box); the section is a file of its own
        self.assertEqual(src("site", "app", "cost-of-power", "AllGridsView.tsx").count(' title="'), 1)

    def test_its_names_in_the_address_are_none_of_the_tabs(self):
        lib = src("site", "app", "cost-of-power", "regions.ts")
        m = re.search(r"export const PARAMS = \[([^\]]+)\] as const;", lib)
        mine = re.findall(r'"([a-z]+)"', m.group(1))
        self.assertEqual(mine, ["srsort", "srdir", "srcols", "srkind", "sropen", "sra", "srb"])
        tabs = ["view", "profile", "mw", "lf", "strike", "rows", "sort", "dir", "grid", "kind", "lo", "hi", "held", "a", "b", "node", "nq", "ncls", "ncounty", "nzone",
                "nsort", "ndir", "llrow", "rstate", "rgrid", "rstatus", "rq", "rsort", "rdir", "ra", "rb", "rule", "rregion"]
        self.assertFalse(set(mine) & set(tabs))
        siting = src("site", "lib", "siting.ts") + src("site", "app", "cost-of-power", "LargeLoadSection.tsx") + src("site", "app", "cost-of-power", "AllGridsView.tsx")
        for name in mine:
            self.assertNotIn(f"q.{name}", siting, name)


class TheFilesAndTheirRules(unittest.TestCase):
    def test_no_em_dash_and_no_hex_colour(self):
        for name in FILES:
            text = src("site", "app", "cost-of-power", name)
            self.assertNotIn(EM, text, name)
            self.assertIsNone(re.search(r"#[0-9a-fA-F]{6}\b", text), name)
        for rel in [("site", "scripts", "test-regions-section.mjs"), ("tests", "fixtures", "siting_regions", "make_fixture.py")]:
            self.assertNotIn(EM, src(*rel), rel[-1])

    def test_the_browsers_parts_read_no_file(self):
        # regions.ts is read by the browser's choices and downloads: it imports nothing; the two client files import no reader
        lib = src("site", "app", "cost-of-power", "regions.ts")
        self.assertIsNone(re.search(r"^import ", lib, re.M))
        for name in ["RegionsChoices.tsx", "RegionsDownload.tsx"]:
            text = src("site", "app", "cost-of-power", name)
            self.assertTrue(text.startswith('"use client";'), name)
            self.assertNotIn("pagefile", text, name)
            self.assertNotIn("./data", text, name)

    def test_the_files_are_read_through_the_sites_one_reader(self):
        # tests/test_session5171.py lists every file that reads the disk itself; this one reads through lib/pagefile.ts
        data = src("site", "app", "cost-of-power", "regionsdata.ts")
        self.assertIn('import { DATA_DIR, readPageFile } from "@/lib/pagefile";', data)
        for name in FILES:
            self.assertIsNone(re.search(r'from "(node:)?fs"', src("site", "app", "cost-of-power", name)), name)
        # no Supabase read: the tab's rule (tests/test_session716.py)
        for name in FILES:
            self.assertNotIn("supabase", src("site", "app", "cost-of-power", name).lower(), name)

    def test_the_examples_are_not_drawn_as_a_table(self):
        data = src("site", "app", "cost-of-power", "regionsdata.ts")
        self.assertIn("if (index.example === true || table.example === true) {", data)
        self.assertIn('return { state: "example", why: "not built yet: the files on this build are the contract\'s own examples', data)

    def test_the_sites_own_hold_wins_over_the_file(self):
        sec = src("site", "app", "cost-of-power", "RegionsSection.tsx")
        self.assertIn('import { licenseByGrid, licenseByRow, licenseHeldRow } from "@/lib/license";', sec)
        self.assertIn("function siteHolds(table: string | null | undefined, entity: string | null): boolean {", sec)
        self.assertIn("const held = r.held ?? (siteHolds(source, place?.ref_hub ?? null) ? siteHoldWords(source as string) : null);", sec)
        # the two tables the contract first called public are held whole on the site
        status = json.loads(src("site", "data", "license_status.json"))["tables"]
        for table in ("datacenter_facilities", "datacenter_projects"):
            self.assertEqual(status[table]["status"], "license needed", table)

    def test_a_figure_is_written_in_the_value_checks_own_form(self):
        # scripts/check-values.mjs `shown`: a whole value whole with commas, any other to two decimals; so the section
        # needs no rule of its own there
        lib = src("site", "app", "cost-of-power", "regions.ts")
        self.assertIn('export const figure = (v: number, unit?: string | null): string => (Number.isInteger(v) && !(unit && DECIMAL_UNITS.has(unit)) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));', lib)
        self.assertIn('const DECIMAL_UNITS = new Set(["USD/MWh", "pct", "years", "kgCO2/MWh"]);', lib)
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('return Number.isInteger(x) ? x.toLocaleString("en-US") : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });', check)
        # the check passes words that begin with `shown`: "60.00" for a whole 60 begins with "60"
        self.assertIn("text.startsWith(usdFormat ? usd(Number(raw)) : whole ? Math.round(Number(raw)).toLocaleString(\"en-US\") : shown(raw))", check)
        self.assertIn('"/cost-of-power?view=allgrids"', check)

    def test_the_trace_names_the_folder_and_the_old_line_stands(self):
        cfg = src("site", "next.config.ts")
        self.assertIn('outputFileTracingIncludes: { "/cost-of-power": ["./data/datacenter/*.json"]', cfg)
        self.assertIn('traced["/cost-of-power"] = [...(traced["/cost-of-power"] ?? []), "./data/siting/regions/*.json"];', cfg)

    def test_the_fixture_says_its_values_are_made_up(self):
        base = os.path.join(ROOT, "tests", "fixtures", "siting_regions", "siting", "regions")
        names = sorted(os.listdir(base))
        self.assertEqual(names, ["index.json", "op-ercot.json", "op-nyiso.json", "region-tex.json", "table.json"])
        for name in names:
            with open(os.path.join(base, name), encoding="utf-8") as f:
                d = json.load(f)
            self.assertIn("MADE-UP", d["fixture"], name)
            self.assertIs(d["example"], False, name)


if __name__ == "__main__":
    unittest.main()
