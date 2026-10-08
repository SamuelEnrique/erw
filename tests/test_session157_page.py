"""Session 157, the page half: "What changed this week", the second view of the policy monitor (/policy, in review).

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written outside a temporary
folder. The environment is read, never set.

    PureFunctions  site/scripts/test-policy-week.mjs: the two views and the address, the windows, the tag rule, the
                   grid an action is under, the agency filter and its marks, the rows and their hovers, the filters,
                   the chart's counts (Node runs site/lib/policyweek.ts with the site's alias loader). Its rows are made
                   up and marked so; where the site's files are on the machine it also reads them.
    TheTags        the page applies the one rule file: site/data/policy/tag_rules.json is the warehouse's file, and the
                   page's rule (TypeScript) gives the Python rule's tags on every action of the table held (the table
                   is read from ERW_TABLES_DIR or warehouse/output; skipped on a machine without it).
    ThePage        the page's rules, read from its source: in review; one page with two views, the first as it was;
                   the view reads the live set through lib/supabase.ts and five site files, and calls no model; MISO's
                   words and hover are the site's; the municipal words; the live pages and the shared tool components
                   take nothing of it; no em dash; the checks name it.
    TheFiles       where site/data/policy/*.json are on the machine: the shapes the page reads, no made-up row.
On the built site: node --import ./scripts/alias-register.mjs scripts/check-policy.mjs <base>.

    python -m unittest tests.test_session157_page
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
POLICY = os.path.join(SITE, "data", "policy")
RULES = os.path.join(POLICY, "tag_rules.json")
MINE = (
    ("site", "app", "policy", "page.tsx"), ("site", "app", "policy", "WeekView.tsx"), ("site", "lib", "policyweek.ts"), ("site", "lib", "policyweekdata.ts"),
    ("site", "scripts", "test-policy-week.mjs"), ("site", "scripts", "check-policy.mjs"), ("tests", "test_session157_page.py"),
)
GRIDS = ["ercot", "pjm", "miso", "caiso", "nyiso", "isone", "spp"]
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
LOADER = ["--import", "./scripts/alias-register.mjs"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, *LOADER, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def sources_under(*parts):
    out = []
    for folder, _, names in os.walk(os.path.join(ROOT, *parts)):
        for n in names:
            if n.endswith((".ts", ".tsx")):
                out.append(os.path.join(folder, n))
    return out


def python_rule():
    """warehouse/derived/policy_action_tags.py, loaded by its path; None where pandas is not installed."""
    try:
        import pandas  # noqa: F401
    except ImportError:
        return None
    spec = importlib.util.spec_from_file_location("erw_policy_action_tags_157", os.path.join(ROOT, "warehouse", "derived", "policy_action_tags.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@unittest.skipUnless(NODE, "node is not installed")
class PureFunctions(unittest.TestCase):
    def test_the_node_tests_pass(self):
        r = subprocess.run([NODE, *LOADER, "scripts/test-policy-week.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"all \d+ passed")
        self.assertNotIn("FAIL", r.stdout)

    def test_its_rows_are_marked_made_up(self):
        t = src("site", "scripts", "test-policy-week.mjs")
        self.assertIn("THE ROWS BELOW ARE MADE UP FOR THIS TEST", t)
        self.assertIn("example.invalid", t)            # no address of a real agency or regulator stands in a made-up row
        for real in ("federalregister.gov", "ferc.gov", "puc.texas.gov", "cpuc.ca.gov"):
            self.assertNotIn(real, t)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.exists(RULES), "site/data/policy/tag_rules.json is not on this machine")
class TheTags(unittest.TestCase):
    def test_one_rule_file(self):
        with open(RULES, "rb") as a, open(os.path.join(ROOT, "warehouse", "config", "policy_tag_rules.json"), "rb") as b:
            self.assertEqual(a.read().replace(b"\r\n", b"\n"), b.read().replace(b"\r\n", b"\n"), "the page's rule file is the warehouse's")
        self.assertEqual(re.findall(r'"data", "policy", "(tag_rules\.json)"', src("site", "lib", "policyweekdata.ts")), ["tag_rules.json"])

    def compare(self, cases):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cases.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"cases": cases}, f)
            r = subprocess.run([NODE, *LOADER, "scripts/test-policy-week.mjs", "--cases", path, RULES], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual((r.returncode, got["differ"], got["cases"]), (0, 0, len(cases)), got)
        return got

    def test_the_page_gives_the_python_rules_tags_on_the_table_held(self):
        main = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
        table = os.path.join(main, "policy_actions.csv")
        if not os.path.exists(table):
            self.skipTest("policy_actions is not on this machine")
        pat = python_rule()
        if pat is None:
            self.skipTest("pandas is not installed")
        rules = pat.load_rules(RULES)
        acts = pat.read_events(table)
        keep = ["event_id", "agency", "action_type", "docket"] + list(rules["fields_matched"])
        cases = [{**{k: r.get(k, "") for k in keep}, "expect": pat.tag_action(r, rules)} for r in acts.to_dict("records")]
        self.assertGreater(len(cases), 1000)
        got = self.compare(cases)
        self.assertEqual(got["tagged"], sum(1 for c in cases if c["expect"]))
        self.assertGreater(got["tagged"], 0)

    def test_the_page_gives_the_python_rules_tags_on_the_warehouses_cases(self):
        fixture = os.path.join(ROOT, "tests", "fixtures", "session157", "policy_tag_cases.json")
        if not os.path.exists(fixture):
            self.skipTest("tests/fixtures/session157/policy_tag_cases.json is not on this machine")
        with open(fixture, encoding="utf-8") as f:
            file = json.load(f)
        self.assertEqual(str(file["rule_version"]), str(json.loads(src("site", "data", "policy", "tag_rules.json"))["version"]))
        got = self.compare(file["cases"])
        self.assertEqual(got["tagged"], sum(1 for c in file["cases"] if c["expect"]))


class ThePage(unittest.TestCase):
    def test_in_review(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/policy": "review"')

    def test_one_page_two_views_and_the_first_as_it_was(self):
        page = src("site", "app", "policy", "page.tsx")
        self.assertIn('if (view === "week")', page)
        self.assertEqual(page.count("<WeekView "), 1)
        # everything the page showed before is still in it, in the view an address without view=week opens
        for said in ("Energy rules, proposed rules and notices of DOE, FERC, EPA, NRC, BLM and Interior from the Federal Register", "Significance uses the same rubric as the news digest",
                     '<Section title="This week in policy">', '<Section title="Every action">', "<PolicyTable rows={rows} />", "Number(x.significance) >= 5",
                     'tables={["policy_actions", "policy_reads"]} note="Scores from warehouse/policy/score.py (the news rubric)', '<Related href="/policy" />'):
            self.assertIn(said, page)
        table = src("site", "app", "policy", "PolicyTable.tsx")
        for label in ('sel("Agency"', 'sel("Type"', 'sel("Sector"', 'sel("State"', 'sel("Significance"', 'type="date"', "<Detail r={r} />"):
            self.assertIn(label, table)
        self.assertNotRegex(table, r"policyweek|WeekView")       # the table of every action is not changed for the view
        self.assertFalse(os.path.exists(os.path.join(SITE, "app", "policy", "week")), "the view is a view of /policy, not a second page")

    def test_what_the_view_reads_and_that_no_model_is_called(self):
        view, data, lib = src("site", "app", "policy", "WeekView.tsx"), src("site", "lib", "policyweekdata.ts"), src("site", "lib", "policyweek.ts")
        self.assertEqual(sorted(re.findall(r'"data", "policy", "([a-z_]+\.json)"', data)), ["action_tags.json", "grids.json", "refresh.json", "state_rules.json", "tag_rules.json"])
        self.assertIn('table_name: "eq.policy_actions"', data)
        self.assertIn('table_name: "eq.policy_reads"', data)
        self.assertIn('from "./supabase"', data)                                         # the one reader of the live set, with the anon key
        self.assertEqual(re.findall(r'^import .* from "([^"]+)";', lib, re.M), ["@/lib/rules"])   # pure: the words of session 154's block and nothing else
        for name, t in (("WeekView.tsx", view), ("policyweekdata.ts", data), ("policyweek.ts", lib)):
            self.assertIsNone(re.search(r"(?i)anthropic|/api/|fetch\(|service_role|service_key", t), name)   # no model, no request of its own, never the service key
        self.assertIn('"use client"', view)
        self.assertIsNone(re.search(r'from "[^"]*(policyweekdata|supabase|node:fs|lib/data)[^"]*"', view))   # the browser only chooses among the rows it was given
        self.assertNotIn("first_paragraph", view)

    def test_the_address_holds_the_window_and_the_filters(self):
        view, lib = src("site", "app", "policy", "WeekView.tsx"), src("site", "lib", "policyweek.ts")
        self.assertIn("window.history.replaceState(null, \"\", weekHref(next))", view)
        for key in ('q.set("days", "30")', 'q.set("agency", c.agency)', 'q.set("topic", c.topic)', 'q.set("grid", c.grid)', 'q.set("large", "1")'):
            self.assertIn(key, lib)
        self.assertIn("chosenOf(q, {", src("site", "app", "policy", "page.tsx"))

    def test_miso_and_the_municipal_words(self):
        lib = src("site", "lib", "policyweek.ts")
        self.assertIn('export const MUNICIPAL = ["zoning", "city council", "county board"] as const;', lib)
        self.assertIn('export const paused = (grid: string): boolean => grid === "miso";', lib)
        self.assertIn('export const PAUSED_WORDS = "paused while terms are reviewed";', src("site", "lib", "rules.ts"))
        self.assertIn("MISO's terms forbid automated access to its site; its pulls are paused.", src("site", "components", "mix", "views.tsx"))
        self.assertIn("{ PAUSED_WORDS, PAUSE_WHY }", lib)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_words_the_owner_fixed(self):
        got = node("import * as W from './lib/policyweek.ts';"
                   "console.log(JSON.stringify({ views: W.VIEWS, windows: W.WINDOWS, paused: W.PAUSED_WORDS, why: W.PAUSE_WHY, none: W.NO_READ, municipal: W.MUNICIPAL, method: W.METHOD,"
                   " miso: W.shownRows([{ id: 'x', date: '2026-10-08', body: 'a', topics: [], grids: ['miso'], allGrids: true, largeLoad: true, link: { words: '' } }], { days: 30, agency: '', topic: '', grid: 'miso', large: false }, '2026-10-08') }));")
        self.assertEqual([v[0] for v in got["views"]], ["all", "week"])
        self.assertEqual(got["views"][1][1], "What changed this week")
        self.assertEqual(got["windows"], [7, 30])
        self.assertEqual(got["paused"], "paused while terms are reviewed")
        self.assertTrue(got["why"].startswith("MISO's terms forbid automated access"))
        self.assertEqual(got["none"], "no read yet")
        self.assertEqual(got["municipal"], ["zoning", "city council", "county board"])
        self.assertEqual(got["method"], {"href": "/data/methods/policy_monitor", "doc": "docs/methods/policy_monitor.md"})
        self.assertEqual(got["miso"], [])

    def test_no_live_page_and_no_shared_component_takes_anything_of_it(self):
        took = re.compile(r"policyweek|WeekView|What changed this week|data/policy")
        for parts in (("site", "app", "cost-of-power"), ("site", "app", "network"), ("site", "app", "storage"), ("site", "components")):
            for f in sources_under(*parts):
                with open(f, encoding="utf-8") as fh:
                    self.assertIsNone(took.search(fh.read()), f)
        for parts in (("site", "lib", "pages.ts"), ("site", "lib", "supabase.ts"), ("site", "lib", "rules.ts"), ("site", "lib", "data.ts"), ("site", "lib", "release.ts")):
            self.assertIsNone(took.search(src(*parts)), parts[-1])

    def test_no_em_dash(self):
        for parts in MINE + (("site", "scripts", "check-routes.mjs"),):
            t = src(*parts)
            self.assertNotIn(EM_DASH, t, parts[-1])
            self.assertNotIn(EN_DASH, t, parts[-1])

    def test_the_checks_name_it(self):
        check = src("site", "scripts", "check-policy.mjs")
        for said in ("What changed this week", "data-week-paused", "MUNICIPAL", "METHOD.doc", "Input.dispatchKeyEvent", "refresh.json", "This week in policy", "data-in-review"):
            self.assertIn(said, check)
        routes = src("site", "scripts", "check-routes.mjs")
        for address in ('"/policy"', '"/policy?view=week"', '"/policy?view=week&days=30"', '"/policy?view=week&grid=miso"'):
            self.assertIn(address, routes)


@unittest.skipUnless(os.path.isdir(POLICY), "site/data/policy is not on this machine")
class TheFiles(unittest.TestCase):
    def file(self, name):
        path = os.path.join(POLICY, name)
        if not os.path.exists(path):
            self.skipTest("site/data/policy/%s is not on this machine" % name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertNotRegex(text, r"(?i)made[- ]up|example\.invalid|example\.com|lorem ipsum", name)   # no made-up row in a file the site ships
        self.assertNotIn(EM_DASH, text, name)
        return json.loads(text)

    def test_the_grids(self):
        f = self.file("grids.json")
        self.assertEqual([g["key"] for g in f["grids"]], GRIDS)
        self.assertEqual([g["name"] for g in f["grids"]], ["ERCOT", "PJM", "MISO", "CAISO", "NYISO", "ISO-NE", "SPP"])
        self.assertTrue(all(g["words"] for g in f["grids"]))

    def test_the_regulators(self):
        f = self.file("refresh.json")
        self.assertEqual(len(f["regulators"]), 11)
        self.assertEqual(len({r["key"] for r in f["regulators"]}), 11)
        for r in f["regulators"]:
            self.assertIn(r["jurisdiction"], ("federal", "state"), r["key"])           # federal regulators and state commissions only
            self.assertTrue(r["regulator"] and r["short"], r["key"])
            if r["refreshed"] is False:
                self.assertGreater(len(r["reason"] or ""), 20, r["key"])                # the page's hover is this, word for word
        self.assertTrue(any(r["refreshed"] is False for r in f["regulators"]))

    def test_the_docket_rows(self):
        f = self.file("state_rules.json")
        self.assertEqual(len(f["topics"]), 4)
        keys = {r["key"] for r in self.file("refresh.json")["regulators"]}
        for r in f["rows"]:
            self.assertIn(r["regulator_key"], keys, r["id"])
            self.assertIn(r["jurisdiction"], ("federal", "state"), r["id"])
            self.assertRegex(r["url"], r"^https?://", r["id"])
            self.assertTrue(set(r["topics"]) <= set(f["topics"]), r["id"])
            self.assertTrue(set(r["grids"]) <= set(GRIDS), r["id"])
            self.assertTrue(r["sentence"] or r["sentence_withheld"], r["id"])            # a sentence of its document, or the phrase in its place
            if not r["sentence"]:
                self.assertFalse(r["status_as_worded"], r["id"])                         # a regulator's text that is not copied: no worded status either
            self.assertTrue(r["read"] is None or r["read_by"] == "model", r["id"])

    def test_the_tags_of_the_printed_text(self):
        f = self.file("action_tags.json")
        tags = set(self.file("tag_rules.json")["tags"])
        self.assertEqual(str(f["rule_version"]), str(self.file("tag_rules.json")["version"]))
        for event_id, hits in f["tags"].items():
            self.assertTrue(hits and {h["tag"] for h in hits} <= tags, event_id)
        self.assertTrue(set(f.get("first_paragraph", {})) <= set(f["tags"]))


if __name__ == "__main__":
    unittest.main()
