"""Session 7201 (chain 302): the large-load rules on the All grids tab of /cost-of-power and in the monitor of /policy.

The library's own tests are Node's (site/scripts/test-large-load-rules.mjs, run here); the rest reads the sources: the
tab's Utility and Time to connect cells draw the row's rule line, the section stands under the tab, a held row and a
withheld field are drawn blank with "license needed" on hover and never as a value, the page file reaches the browser
through one client module only, the monitor draws the states' laws under its State filter, the value checker knows the
section's keys and pages, and none of the chain's files holds an em or an en dash.
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
LOADER = ["--import", "./scripts/alias-register.mjs"]
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    ("site", "lib", "largeloadrules.ts"), ("site", "components", "largeload", "parts.tsx"), ("site", "app", "cost-of-power", "LargeLoadRules.tsx"),
    ("site", "app", "cost-of-power", "LargeLoadSection.tsx"), ("site", "app", "policy", "StateLaws.tsx"), ("site", "scripts", "test-large-load-rules.mjs"),
    ("warehouse", "derived", "large_load_rules_page.py"), ("docs", "reviews", "large-load-on-site", "questions.md"),
    ("tests", "test_session7200_large_load_rules_page.py"), ("tests", "test_session7201_large_load_on_site.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, *LOADER, "scripts/test-large-load-rules.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_the_node_tests_pass(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1000:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 80, self.out[-500:])

    def test_the_blank_cells_are_counted(self):
        self.assertRegex(self.out, r"(?m)^ok   8 fields of public rules are drawn blank with license needed")
        self.assertRegex(self.out, r"(?m)^ok   a held row's CSV line is its id, utility and place")
        self.assertRegex(self.out, r"(?m)^ok   a held row of the file is its name and place only")


class TheTab(unittest.TestCase):
    def test_the_two_cells_draw_the_rows_rule(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertEqual(v.count('<RuleLine r={r} x={x} cell="utility" />'), 3, "the utility cell's three forms: no utility, the state's largest seller, the county's")
        self.assertEqual(v.count('<RuleLine r={r} x={x} cell="connect" />'), 1)
        self.assertIn("<LargeLoadSection q={q} x={x} />", v)
        s = src("site", "app", "cost-of-power", "LargeLoadSection.tsx")
        for words in ("no large-load rule found", "no large-load rule read", "its rule's timed steps", "no timed step printed"):
            self.assertIn(words, s)
        self.assertIn("rowRules(LARGE_LOAD, utilities, state, r.grid)", s)
        self.assertNotIn("TableDownloads", s, "the tab reads files only: no catalogue read from the database")
        self.assertNotIn("supabase", s.lower().replace("no database is read", ""))

    def test_a_row_names_its_utilities_by_the_cells_own_function(self):
        lib = src("site", "lib", "siting.ts")
        m = re.search(r"export function rowUtilities\(.*?\n}\n", lib, re.S)
        self.assertTrue(m)
        self.assertIn("utilityCell(f, r)", m.group(0))
        self.assertIn("c.county.delivery?.companies", m.group(0))

    def test_the_section_counts_are_check_keys(self):
        s = src("site", "app", "cost-of-power", "LargeLoadSection.tsx")
        for key in ('"largeload|rules|all"', "`largeload|rules|status|${s}`", '"largeload|rules|held"', '"largeload|changes|public"', '"largeload|laws|public"', "`largeload|rules|state|${rr.state}`"):
            self.assertIn(key, s)
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "largeload")', c)
        self.assertIn("L.largeLoadStat(", c)
        self.assertIn('"/cost-of-power?view=allgrids&llrow=ercot%3ALZ_AEN", "/policy?view=monitor&state=MD"', c)

    def test_held_and_withheld_are_blank_with_license_needed(self):
        parts = src("site", "components", "largeload", "parts.tsx")
        blank = re.search(r"export function Blank\(.*?\n}\n", parts, re.S).group(0)
        self.assertIn("data-license-held={table}", blank)
        self.assertIn("aria-label={`${what}: ${LICENSE_NEEDED}`}", blank)
        self.assertIn("String.fromCharCode(160)", blank, "the cell prints nothing: a space the width of the cell")
        self.assertIn('if (d.kind === "withheld" || d.kind === "held") return <Blank', parts)
        t = src("site", "app", "cost-of-power", "LargeLoadRules.tsx")
        self.assertIn('{["Status", "Date", ...FIELDS.map((f) => FIELD_HEAD[f])].map((h) => <td key={h} className="px-2 py-1.5"><Blank tip={HELD_ROW_TIP(l.utility)} what={h} /></td>)}', t)
        self.assertIn("<HeldCard rule={l} />", t)
        # a held row's ten cells and the eight fields of public rows: what the table draws blank when every rule is drawn
        with open(os.path.join(SITE, "data", "siting", "large_load_rules.json"), encoding="utf-8") as fh:
            f = json.load(fh)
        fields = sum(1 for r in f["rules"] for c in r["fields"].values() if c["kind"] == "withheld" or (c["kind"] == "see" and c.get("held")))
        self.assertEqual((len(f["held_rules"]) * 10 + fields, len(f["held_changes"]) * 4, len(f["held_laws"]) * 4), (228, 16, 4))

    def test_the_page_file_reaches_the_browser_through_one_module(self):
        users = []
        for base in ("app", "components", "lib"):
            for d, _, files in os.walk(os.path.join(SITE, base)):
                for name in files:
                    if name.endswith((".ts", ".tsx")):
                        p = os.path.join(d, name)
                        with open(p, encoding="utf-8") as fh:
                            text = fh.read()
                        if "large_load_rules.json\"" in text and "import " in text and re.search(r'^import \w+ from "@/data/siting/large_load_rules\.json";', text, re.M):
                            users.append((os.path.relpath(p, SITE).replace(os.sep, "/"), text.lstrip().startswith('"use client"')))
        self.assertEqual(sorted(users), [("app/cost-of-power/LargeLoadRules.tsx", True), ("app/policy/page.tsx", False), ("lib/sitingdata.ts", False)])
        self.assertIn('import "server-only";', src("site", "lib", "sitingdata.ts"))

    def test_the_table_answers_to_the_mouse(self):
        t = src("site", "app", "cost-of-power", "LargeLoadRules.tsx")
        for mark in ('data-llr-filter="state"', 'data-llr-filter="grid"', 'data-llr-filter="status"', "data-llr-head={k}", 'data-llr-set="a"', 'data-llr-set="b"',
                     'data-llr-csv="rules"', 'data-download="python"', 'data-download="stata"', 'data-llr-csv="changes"', "data-llr-affects={af.id}", "data-llr-region={k || \"all\"}"):
            self.assertIn(mark, t)
        self.assertIn("window.history.replaceState", t, "the filters, the sort, A and B and the open rule are kept in the address")
        self.assertNotIn("fetch(", t)
        self.assertNotIn("title={", t.replace('title={`${l.rule!.title}, read ${l.rule!.read}`}', "").replace('title={`${c.title}, read ${c.read}`}', ""),
                         "an explanation is a tip a keyboard reaches; a title is kept for a link's document only")


class TheMonitor(unittest.TestCase):
    def test_the_laws_follow_the_state_filter(self):
        m = src("site", "app", "policy", "MonitorView.tsx")
        self.assertIn("{laws ? <StateLaws file={laws} states={f.states} clearStates={() => put({ ...f, states: [] })} /> : null}", m)
        p = src("site", "app", "policy", "page.tsx")
        self.assertIn("laws={{ laws: ll.laws, held: ll.held_laws, built: ll.built, retrieved: ll.retrieved }}", p)
        self.assertIn('<TableDownloads tables={["policy_actions", "policy_reads", "state_large_load_laws"]} />', p)
        s = src("site", "app", "policy", "StateLaws.tsx")
        self.assertIn("id={LAWS_ANCHOR}", s)
        self.assertIn('<Blank tip={HELD_TIP(l.bill)} table={LAWS_TABLE} what={h} />', s)
        self.assertIn("requirementsOf(l).map(", s)
        lib = src("site", "lib", "largeloadrules.ts")
        self.assertIn('export const lawsHref = (state?: string) => `/policy?view=monitor${state ? `&state=${encodeURIComponent(state)}` : ""}#${LAWS_ANCHOR}`;', lib)
        self.assertIn('list("state")', src("site", "lib", "policymonitor.ts"), "the monitor's State filter reads the address's state")


class TheSources(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for parts in MINE:
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
            self.assertNotIn(EN_DASH, text, parts)

    def test_the_stylesheet_is_whole(self):
        css = src("site", "app", "tokens.css")
        self.assertEqual(css.count("{"), css.count("}"))
        self.assertIn('.brand-a [data-llr] span.tip > [role="tooltip"][data-tp],', css)
        self.assertIn('.brand-a [data-allgrids] tbody td [data-llr="cell"],', css)

    def test_the_columns_are_the_questions(self):
        q = src("docs", "reviews", "large-load-on-site", "questions.md")
        lib = src("site", "lib", "largeloadrules.ts")
        order = re.search(r'export const FIELDS = \[(.*?)\] as const;', lib).group(1).replace('"', "").split(", ")
        asked = [c for c in re.findall(r"`x_(\w+)`", q) if c in order]
        self.assertEqual(list(dict.fromkeys(asked))[:8], order, "the table's columns stand in the order of the questions page")


if __name__ == "__main__":
    unittest.main()
