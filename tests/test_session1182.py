"""Session 1182 (chain 091): each new panel's table, to download.

Energy Research Warehouse (ERW).

Each panel chains 077 and 078 added to the Grid tool (the network ties, the balance, the gravity table, the last 24
hours' table, the energy mix panel's fuels and monthly table, the scarcity counts, CAISO's and ERCOT's notice lines, the
Exchange blocks' week per tie and twelve months, the stress tables, the replayed day) offers its table as a CSV made from
the cells the panel draws (site/components/grid/PanelFile.tsx), written into its link as a data: address with the
download attribute: no new route and no read. The file opens with its provenance (the panel and page, the tables, the
filter, the hour or window, the time drawn), a held grid's figure is written "license needed", never its value.
site/scripts/test-grid-files.mjs draws each panel on committed real rows and holds the file's figures to the page's;
scripts/check-table-downloads.mjs and check-download.mjs --grid read the files from a served page
(site/scripts/grid-files.mjs).

    python -m unittest tests.test_session1182 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT")}


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-files.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("every case holds", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"^ok   ", r.stdout, re.M)), 53)
        for block in ("grid_network_ercot", "balance_ERCO", "grid_network_us48", "replay_ERCO", "replay_BPAT", "grid_gravity_ercot", "view_exchange",
                      "grid_clean24_ercot", "grid_mix_ercot", "grid_mix_caiso", "grid_scarcity_ercot", "grid_scarcity_caiso", "grid_caisoalert_caiso",
                      "grid_ercotnotice_ercot", "mixview_stress"):
            self.assertIn(f": {block}\n", r.stdout)
        self.assertIn('a held grid\'s figure is written "license needed"', r.stdout)


class TheFile(unittest.TestCase):
    def test_the_header_and_the_cells(self):
        p = src("site", "components", "grid", "PanelFile.tsx")
        for line in ("`Panel: ${of.panel}", "`Tables: ${of.tables.join(\"; \")}`", "`Filter: ${of.filter}`", "of.window,", "`Drawn: ${new Date(drawn).toISOString()}"):
            self.assertIn(line, p)
        self.assertIn("if (isFig(node)) { out.push(heldBy(node.check) ? { held: true } : { fig: { check: node.check, raw: node.raw } }); return; }", p)
        self.assertIn("if (props[\"data-license-held\"] !== undefined) { out.push({ held: true }); return; }", p)
        self.assertIn('href={`data:text/csv;charset=utf-8,${encodeURIComponent(f.csv)}`} download={f.name}', p)
        self.assertNotIn("fetch(", p)
        self.assertNotIn('"use client"', p)

    def test_every_panel_offers_its_table(self):
        for parts, n in ((("components", "grid", "NetworkFigures.tsx"), 4), (("components", "grid", "ReplayDay.tsx"), 1), (("components", "grid", "Emissions.tsx"), 3),  # session 1415: and the ranked table's and the monthly's
                         (("components", "grid", "MixFigures.tsx"), 2), (("components", "grid", "ScarcityPanel.tsx"), 1), (("components", "grid", "CaisoAlertState.tsx"), 1),
                         (("components", "grid", "ErcotNoticeState.tsx"), 1), (("components", "grid", "ExchangeView.tsx"), 3)):
            s = src("site", *parts)
            self.assertIn('from "@/components/grid/PanelFile"', s, parts)
            self.assertEqual(s.count("<PanelFile "), n, parts)
        v = src("site", "components", "mix", "views.tsx")
        self.assertIn("<PanelFile of={file} columns={head} rows={rows.map((r) => r.cells)} />", v)
        self.assertEqual(v.count("file={stressFile("), 3)
        self.assertIn('file={{ panel: "grid_stress_all"', v)
        self.assertNotIn("hrefOf", v)   # session 411's assertion, kept

    def test_the_rows_drawn_are_the_rows_filed(self):
        n = src("site", "components", "grid", "NetworkFigures.tsx")
        for rows in ("rows48", "tieRows", "balRows", "gRows"):
            self.assertIn(f"rows={{{rows}}} />", n)
            self.assertIn(f"rows={{{rows}.map((r) => r.cells)}} />", n)
        e = src("site", "components", "grid", "ExchangeView.tsx")
        for rows in ("rows48", "tieRows", "supRows"):
            self.assertIn(f"rows={{{rows}}} />", e)
            self.assertIn(f"rows={{{rows}.map((r) => r.cells)}} />", e)


class TheChecks(unittest.TestCase):
    def test_the_two_check_scripts_read_the_files(self):
        a = src("site", "scripts", "check-table-downloads.mjs")
        self.assertIn('import { GRID_FILE_PAGES, gridFileProblems, gridFilesOf, missingFiles, rawsOf } from "./grid-files.mjs";', a)
        self.assertIn("process.env.CHECK_GRID_FILES", a)
        b = src("site", "scripts", "check-download.mjs")
        self.assertIn('import { GRID_FILE_PAGES, gridFileProblems, gridFilesOf, missingFiles, rawsOf } from "./grid-files.mjs";', b)
        self.assertIn('if (args.includes("--grid")) {', b)
        # what the two did before is kept: the ten tables and the downloads line
        self.assertIn('const SIX = ["eia930_all_emissions"', b)
        self.assertIn("data-downloads=", a)

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_they_parse(self):
        for f in ("check-download.mjs", "check-table-downloads.mjs", "grid-files.mjs", "test-grid-files.mjs"):
            r = subprocess.run([NODE, "--check", os.path.join("scripts", f)], cwd=SITE, capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, f + r.stderr[-1000:])

    def test_the_fixture_is_real_rows_with_its_source(self):
        d = json.loads(src("site", "scripts", "fixtures", "grid_files.json"))
        self.assertIn("anon key", d["_source"])
        self.assertIn("Real rows, unchanged.", d["_source"])
        self.assertEqual({r["entity"] for r in d["ba_supply_monthly"]}, {"eia930:ERCO", "eia930:ERCO-CEN", "eia930:ERCO-SWPP"})
        self.assertEqual({r["entity"] for r in d["generation_mix_hourly_profile"]}, {"iso:caiso"})


class TheMethodAndTheLetter(unittest.TestCase):
    def test_the_method_note(self):
        m = src("docs", "methods", "grid_network.md")
        self.assertIn("## Each panel's table, to download (chain 091, 24 October 2026)", m)
        sec = m[m.index("## Each panel's table, to download"):]
        self.assertIn("Decisions (session 1182):", sec)

    def test_no_em_dash(self):
        for parts in (("site", "components", "grid", "PanelFile.tsx"), ("site", "scripts", "grid-files.mjs"), ("site", "scripts", "test-grid-files.mjs"),
                      ("site", "scripts", "check-download.mjs"), ("site", "scripts", "check-table-downloads.mjs"), ("docs", "methods", "grid_network.md"),
                      ("tests", "test_session1182.py")):
            self.assertNotIn(EM, src(*parts), parts)
        if os.path.exists(os.path.join(ROOT, "archive", "sessions", "SESSION_1182_REPORT.md")):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_1182_REPORT.md"))


if __name__ == "__main__":
    unittest.main()
