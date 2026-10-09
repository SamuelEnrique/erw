"""Session 164: the policy monitor finished. What was built, held to its rules.

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written outside a temporary
folder. The environment is read, never set. Skips cleanly where Node or the tables are not on the machine.

    TheFetcher   warehouse/connectors/large_load_filings.py: it asks a host nothing before that host's robots.txt is
                 saved, nothing a saved robots file disallows (to every robot, to this script's name, or to the agent
                 that runs it by name), never MISO, PJM's Data Miner or API, or an address with an e-mail in it; its
                 User-Agent is the ruled contact string and nothing else; its ceilings are the session's.
    TheTerms     the terms file holds each host's robots words with their hash, and neither regulator's class moved.
    TheAudit     the audit of 100 run again: the findings it starts from (1,850 checks, 114 errors), how a value is
                 classed (the same value keeps its finding; a changed value nobody settled is never counted correct),
                 and the reading written down (every line a known class with its words, no pair twice).
    ThePage      the first view: no method sentence on the face, each the hover of the lead's own words and all three
                 in the Method note; the Tag filter and the chips, by the page's own pure functions on the site's own
                 files (the real tagged actions); the page in review; the browser check names all of it.
On the built site: node --import ./scripts/alias-register.mjs scripts/check-policy-tags.mjs <base> [screenshot.png].

    python -m unittest tests.test_session164
"""

import csv
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
EVAL = os.path.join(ROOT, "warehouse", "policy", "eval")
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"
EM_DASH = chr(0x2014)
MINE = (
    ("warehouse", "connectors", "large_load_filings.py"), ("warehouse", "policy", "audit", "audit_recheck_s164.py"),
    ("warehouse", "policy", "audit", "audit_judgments_s164.py"), ("warehouse", "policy", "eval", "audit_s164_judgments.csv"),
    ("site", "scripts", "check-policy-tags.mjs"), ("site", "app", "policy", "page.tsx"), ("site", "app", "policy", "PolicyTable.tsx"),
    ("site", "lib", "policyweek.ts"), ("site", "lib", "policyweekdata.ts"), ("docs", "methods", "policy_monitor.md"),
    ("warehouse", "config", "large_load_rule_terms.json"), ("tests", "test_session164.py"),
)
ILLINOIS = "\ufeffUser-agent: *\nDisallow: /\n\nUser-agent: Elastic-Crawler\nAllow: /\nDisallow: /test/\nCrawl-delay: 60\n"
OHIO = "User-agent: GPTBot\nUser-agent: anthropic-ai\nUser-agent: Claude-Web\nUser-agent: ClaudeBot\nUser-agent: Scrapy\nDisallow: /"
OPEN = "User-agent: *\nDisallow: /private/\n"
NOT_A_ROBOTS_FILE = "<!DOCTYPE html><html><head><title>404 Error Page</title></head><body>not found</body></html>"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def node(code):
    r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True,
                       encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheFetcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = load("large_load_filings_s164", "warehouse", "connectors", "large_load_filings.py")
        cls.tmp = tempfile.mkdtemp(prefix="erw164_")
        os.makedirs(os.path.join(cls.tmp, "D", "raw", "robots"))
        for host, text in (("icc.illinois.gov", ILLINOIS), ("dis.puc.state.oh.us", OHIO), ("open.example.gov", OPEN), ("puco.ohio.gov", NOT_A_ROBOTS_FILE)):
            with open(cls.f.robots_path(cls.tmp, host), "w", encoding="utf-8") as fh:
                fh.write(text)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_contact_string_and_no_address_of_a_person(self):
        self.assertEqual(self.f.UA, CONTACT)
        code = src("warehouse", "connectors", "large_load_filings.py")
        self.assertNotRegex(code, r"[\w.+-]+@[\w-]+\.[a-z]{2,}")
        self.assertEqual(re.findall(r'headers=\{([^}]*)\}', code), ['"User-Agent": UA, "Accept": "*/*"'])   # the one request, and all it sends

    def test_the_ceilings_are_the_sessions(self):
        self.assertEqual((self.f.MAX_DOCS, self.f.MAX_REQ, self.f.MAX_BYTES), (400, 600, 1_000_000_000))
        self.assertGreaterEqual(self.f.PACE, 2.0)

    def test_never_asked(self):
        for url in ("https://www.misoenergy.org/x.pdf", "https://api.pjm.com/api/v1/x", "https://dataminer2.pjm.com/feed/x",
                    "https://example.gov/files/jane.doe%40example.com/a.pdf", "ftp://example.gov/a.pdf"):
            self.assertTrue(self.f.refused(url), url)
        self.assertEqual(self.f.refused("https://icc.illinois.gov/downloads/public/a.pdf"), "")

    def test_a_host_is_asked_nothing_before_its_robots_file_is_saved(self):
        ok, why = self.f.robots_says(self.tmp, "https://unknown.example.gov/a.pdf")
        self.assertFalse(ok)
        self.assertIn("not saved yet", why)
        self.assertTrue(self.f.robots_says(self.tmp, "https://unknown.example.gov/robots.txt")[0])

    def test_a_robots_file_that_closes_the_site_to_every_robot(self):
        for path in ("/docket/P2025-0677/documents", "/downloads/public/minutes/08-19%20ROM%20Minutes.pdf", "/privacy.htm"):
            ok, why = self.f.robots_says(self.tmp, "https://icc.illinois.gov" + path)
            self.assertFalse(ok, path)
            self.assertIn("disallows", why)

    def test_a_robots_file_that_names_the_agent_that_runs_this_script(self):
        # the request would carry the project's name, which the file does not name: the agent that asks is named, so no
        ok, why = self.f.robots_says(self.tmp, "https://dis.puc.state.oh.us/DocumentRecord.aspx?DocID=x")
        self.assertFalse(ok)
        self.assertRegex(why, "anthropic-ai|ClaudeBot|Claude-Web")
        self.assertEqual(set(self.f.ASKED_BY), {"anthropic-ai", "ClaudeBot", "Claude-Web"})

    def test_what_may_be_asked(self):
        self.assertTrue(self.f.robots_says(self.tmp, "https://open.example.gov/files/a.pdf")[0])
        self.assertFalse(self.f.robots_says(self.tmp, "https://open.example.gov/private/a.pdf")[0])
        ok, why = self.f.robots_says(self.tmp, "https://puco.ohio.gov/anything")
        self.assertTrue(ok)
        self.assertIn("not a robots file", why)

    def test_a_check_is_never_read_as_a_document(self):
        code = src("warehouse", "connectors", "large_load_filings.py")
        for word in ("recaptcha", "captcha", "no robots or crawlers", "verify you are human"):
            self.assertIn(word.encode(), self.f.CHECK_WORDS)
        self.assertIn('kind = "check"', code)
        self.assertNotRegex(code, r"(?i)selenium|playwright|cookie|solve|internet archive|web\.archive|webcache")


class TheTerms(unittest.TestCase):
    def test_each_hosts_robots_words_are_held_and_no_class_moved(self):
        terms = {t["regulator"]: t for t in json.loads(src("warehouse", "config", "large_load_rule_terms.json"))["regulators"]}
        il, oh = terms["Illinois Commerce Commission"], terms["Public Utilities Commission of Ohio"]
        self.assertEqual(il["robots_quote"], "User-agent: *\nDisallow: /")
        for name in ("anthropic-ai", "Claude-Web", "ClaudeBot", "Disallow: /"):
            self.assertIn(name, oh["robots_quote"])
        for t in (il, oh):
            self.assertRegex(t["robots_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(t["robots_retrieved"], r"^2026-10-09T\d\d:\d\d:\d\dZ$")
            self.assertTrue(t["robots_url"].endswith("/robots.txt"))
        self.assertEqual((il["class"], oh["class"]), ("public record", "not quoted"))   # whose sentences a page may show is the owner's
        self.assertEqual(oh["terms_quote"], "")                                           # Ohio's terms are still not read: nothing is quoted

    def test_the_method_note_quotes_them(self):
        note = " ".join(src("docs", "methods", "policy_monitor.md").split())
        for said in ('"User-agent: *" "Disallow: /"', '"User-agent: anthropic-ai"', "0 of the 400 allowed", "Ohio's terms are still not read"):
            self.assertIn(said, note)


class TheAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pandas  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("pandas is not on this machine")
        cls.r = load("audit_recheck_s164", "warehouse", "policy", "audit", "audit_recheck_s164.py")

    def findings(self):
        rows = []
        for _, name in self.r.FINDINGS:
            with open(os.path.join(EVAL, name), encoding="utf-8", newline="") as f:
                rows += list(csv.DictReader(f))
        return rows

    def test_what_it_starts_from(self):
        rows = self.findings()
        self.assertEqual(len(rows), 1850)
        self.assertEqual(len({r["event_id"] for r in rows}), 100)
        self.assertEqual(sum(r["cls"] in self.r.BAD for r in rows), 114)
        by = {}
        for r in rows:
            if r["cls"] in self.r.BAD:
                by[r["field"]] = by.get(r["field"], 0) + 1
        self.assertEqual((by["states"], by["sector_tags"], by["sector"], by["why"]), (40, 47, 8, 8))

    def test_the_place_against_the_document(self):
        c = self.r.states_class
        self.assertEqual(c("PA", "PA"), "correct")
        self.assertEqual(c("TX;LA", "LA;TX"), "correct")
        self.assertEqual(c("", ""), "source_silent")
        self.assertEqual(c("", "AZ"), "missing")
        self.assertEqual(c("CT", "CT;SC;VA"), "missing")
        self.assertEqual(c("VA;WV", "WV"), "wrong")
        self.assertEqual(c("TX", ""), "wrong")

    def test_how_a_value_is_classed(self):
        s = self.r.settle
        f = {"event_id": "x:1", "group": "model", "field": "why", "cls": "unsupported", "row_value": "old line", "trial_value": ""}
        self.assertEqual(s(f, "old line", {}, {})[0], "unsupported")                 # the same value: the finding stands
        self.assertEqual(s(f, "a new line", {}, {})[0], self.r.NOT_READ)             # changed and settled by nobody: never correct
        self.assertNotIn(self.r.NOT_READ, self.r.GOOD + self.r.BAD)
        self.assertEqual(s(f, "a new line", {}, {("x:1", "why"): {"cls": "supported", "words": "w"}})[0], "supported")
        self.assertEqual(s(f, None, {}, {})[0], "not_reachable")
        sig = dict(f, field="significance", cls="judgment", row_value="2")
        self.assertEqual(s(sig, "6", {}, {})[0], "judgment")
        st = dict(f, group="extracted", field="states", cls="missing", row_value="")
        self.assertEqual(s(st, "AZ", {"x:1": {"true_states": "AZ"}}, {})[0], "correct")
        self.assertEqual(s(st, "TX", {"x:1": {"true_states": "AZ"}}, {})[0], "wrong")
        d = dict(f, group="read", field="direction_prices", cls="unsupported", row_value="down")
        self.assertEqual(s(d, "unclear", {}, {})[0], "no_direction")
        self.assertEqual(s(d, "up", {}, {})[0], self.r.NOT_READ)                      # a direction claimed is read, not assumed
        a = dict(f, group="read", field="affected_states", cls="supported", row_value="VA;WV")
        self.assertEqual(s(a, "WV;VA", {}, {})[0], "supported")
        self.assertEqual(s(a, "", {}, {("x:1", "affected_states"): {"cls": "missing", "words": "w"}})[0], "missing")   # the reading wins
        ab = dict(f, group="extracted", field="abstract", cls="correct", row_value="a" * 500)
        self.assertEqual(s(ab, "a" * 500 + " and more", {}, {})[0], "correct")
        self.assertEqual(s(dict(ab, cls="wrong"), "a" * 500 + " and more", {}, {})[0], self.r.NOT_READ)   # an error is never waved through

    def test_the_reading_written_down(self):
        with open(os.path.join(EVAL, self.r.JUDGMENTS), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 100)
        keys = [(r["event_id"], r["field"]) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        audited = {r["event_id"] for r in self.findings()}
        known = set(self.r.GOOD + self.r.BAD + self.r.NEUTRAL)
        for r in rows:
            self.assertIn(r["event_id"], audited)
            self.assertIn(r["cls"], known)
            self.assertGreater(len(r["words"]), 20)
        errors = {(r["event_id"], r["field"]) for r in rows if r["cls"] in self.r.BAD}
        self.assertEqual(len(errors), 4)                                               # the reading found new errors and says so
        self.assertNotIn("significance", {r["field"] for r in rows})

    def test_on_the_tables_where_they_are(self):
        tables = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
        if not (os.path.exists(os.path.join(tables, "policy_actions.csv")) and os.path.exists(os.path.join(tables, "policy_reads.csv"))):
            self.skipTest("the policy tables are not on this machine")
        df, recheck, _, _ = self.r.run(tables)
        self.assertEqual(len(df), 1850)
        self.assertEqual(int(df["cls_then"].isin(self.r.BAD).sum()), 114)
        self.assertLess(int(df["cls_now"].isin(self.r.BAD).sum()), 114)
        same = df[df["changed"] == "no"]
        self.assertTrue((same["cls_then"] == same["cls_now"]).all())                   # a value that did not change keeps its finding


class ThePage(unittest.TestCase):
    def test_in_review(self):
        self.assertRegex(src("site", "lib", "release.ts"), r'"/policy": "review"')

    def test_no_method_sentence_on_the_first_views_face(self):
        page, lib = src("site", "app", "policy", "page.tsx"), src("site", "lib", "policyweek.ts")
        note = " ".join(src("docs", "methods", "policy_monitor.md").split())
        sentences = re.findall(r'^  (scored|read|ferc): "([^"]+)",$', lib, re.M)
        self.assertEqual([k for k, _ in sentences], ["scored", "read", "ferc"])
        for key, said in sentences:
            self.assertNotIn(said[:40], page)                                          # not written on the face
            self.assertIn(f"title={{FIRST_VIEW_METHOD.{key}}}", page)                  # the hover of the words it explains
            self.assertIn(said, note)                                                  # and in the Method note, word for word
        self.assertNotIn('text-sm text-muted">\n        Significance', page)
        self.assertIn("METHOD.href", page)

    def test_the_tag_filter_is_in_the_address_and_the_table(self):
        table, page = src("site", "app", "policy", "PolicyTable.tsx"), src("site", "app", "policy", "page.tsx")
        for said in ('sel("Tag"', "data-policy-tag=", "title={t.why}", "tagHref(next)", "hasTag(r.tags, tag)"):
            self.assertIn(said, table)
        self.assertIn("allTags(a.data)", page)
        self.assertIn("tagOf(q,", page)
        data = src("site", "lib", "policyweekdata.ts")
        self.assertNotRegex(data, r"anthropic|messages\.create")                       # no model tags a row
        self.assertEqual(len(re.findall(r'table_name: "eq\.policy_action_tags"', data + page + table)), 0)   # the tags' table is not read: not needed

    @unittest.skipUnless(NODE, "Node is not on this machine")
    def test_the_chips_of_the_real_tagged_actions(self):
        got = node("""
          import fs from "node:fs";
          import { ANY_TAG, chipsOf, hasTag, tagAction, tagHref, tagOf, topicsOf, uniteTags } from "./lib/policyweek.ts";
          const rules = JSON.parse(fs.readFileSync("data/policy/tag_rules.json", "utf8")), file = JSON.parse(fs.readFileSync("data/policy/action_tags.json", "utf8"));
          const topics = topicsOf(rules, []);
          const chips = Object.fromEntries(Object.entries(file.tags).map(([id, hits]) => [id, chipsOf(uniteTags([], hits, rules), topics, rules)]));
          const tags = Object.keys(rules.tags);
          console.log(JSON.stringify({ tags, version: rules.version, actions: Object.keys(chips).length,
            by: Object.fromEntries(tags.map((t) => [t, Object.values(chips).filter((c) => hasTag(c, t)).length])), any: Object.values(chips).filter((c) => hasTag(c, ANY_TAG)).length,
            tips: Object.values(chips).flat().map((c) => c.why), labels: [...new Set(Object.values(chips).flat().map((c) => c.label))],
            none: hasTag([], ANY_TAG), all: hasTag([], ""), untagged: chipsOf(tagAction({ agency: "FERC", action_type: "notice", title: "Notice of Meeting" }, rules), topics, rules).length,
            of: [tagOf({ tag: "large_load" }, tags), tagOf({ tag: "ANY" }, tags), tagOf({ tag: "zoning" }, tags), tagOf({}, tags)], href: [tagHref(""), tagHref("tax_credit"), tagHref(ANY_TAG)] }));
        """)
        self.assertEqual(got["tags"], ["large_load", "interconnection", "transmission_cost", "tax_credit"])
        self.assertEqual(got["any"], got["actions"])
        self.assertGreater(got["actions"], 0)
        for tag in got["tags"]:
            self.assertGreater(got["by"][tag], 0, f"no real action carries {tag}")     # each of the four chips has a real row to be seen on
        for tip in got["tips"]:
            self.assertRegex(tip, r'^Tagged by the written rule, version %s: ".+" in the .+\. Not by a model\.$' % re.escape(str(got["version"])))
        self.assertEqual(sorted(got["labels"]), ["Interconnection", "Large loads", "Tax credits", "Transmission cost"])
        self.assertEqual((got["none"], got["all"], got["untagged"]), (False, True, 0))
        self.assertEqual(got["of"], ["large_load", "any", "", ""])
        self.assertEqual(got["href"], ["/policy", "/policy?tag=tax_credit", "/policy?tag=any"])

    def test_the_browser_check_names_it(self):
        check = src("site", "scripts", "check-policy-tags.mjs")
        for said in ("withBrowser", "data-policy-tag", "Input.dispatchMouseEvent", "matches(':hover')", "Page.captureScreenshot", "action_tags.json", "FIRST_VIEW_METHOD",
                     "for (const tag of TAGS)"):
            self.assertIn(said, check)
        self.assertIn("document.querySelectorAll('tr[data-policy-row]')", check)       # every row is read back from the page: none is made for the check

    def test_no_em_dash_and_the_live_pages_take_nothing_of_it(self):
        for parts in MINE:
            self.assertNotIn(EM_DASH, src(*parts), "/".join(parts))
        for parts in (("site", "app", "network"), ("site", "app", "storage"), ("site", "app", "cost-of-power", "battery")):
            for folder, _, names in os.walk(os.path.join(ROOT, *parts)):
                for n in names:
                    if n.endswith((".ts", ".tsx")):
                        with open(os.path.join(folder, n), encoding="utf-8") as f:
                            self.assertNotRegex(f.read(), r"policyweek|PolicyTable|FIRST_VIEW_METHOD", os.path.join(folder, n))


if __name__ == "__main__":
    unittest.main()
