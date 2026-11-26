"""Audit of the company database, finding 1 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): the
lead of /companies and its line on the site's list of pages say the directory lists "the policy actions' agencies".
Since 13 November 2026 policy_actions is held for a license, so the page files (site/data/companies/, built 16 November)
list no agency, no company is of the kind regulator, and every company's policy actions are 0: the column, its order
and the "Has: Policy actions" choice show nothing, unmarked.

1. The page files hold policy_actions among the held tables; no listed company has a policy action or is a regulator.
   Passes on main.
2. The fix on this branch, words only: the lead names the agencies only while policy_actions is not held and otherwise
   says they are not listed; the column's head carries a hover saying every count is 0 while held; the "Has" choice is
   marked "(license needed)" and its hover says it finds none; the site's list of pages and the method note say the
   same. No figure moves. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class PolicyActionsAreHeld(unittest.TestCase):
    def test_the_page_files_list_no_policy_action(self):
        ix = json.loads(src("site", "data", "companies", "index.json"))
        self.assertIn("policy_actions", ix["held_tables"])
        col = ix["columns"].index("n_policy_actions")
        self.assertEqual(sum(1 for r in ix["rows"] if r[col]), 0)
        self.assertNotIn("regulator", ix["kinds"])

    def test_the_page_says_so(self):
        page = flat(src("site", "app", "companies", "page.tsx"))
        self.assertIn('const policyHeld = held.includes("policy_actions");', page)
        self.assertIn("The policy actions&apos; agencies are not listed while policy_actions is held for a license.", page)
        self.assertIn("so every company&apos;s count is 0 until a permission is recorded.", page)
        self.assertIn('(k === "policy" && policyHeld) ? `${v} (license needed)` : v', page)
        self.assertIn("Policy actions are held too: no listed company has one while they are, so that choice finds none.", page)
        self.assertIn("ERCOT's queue and the NRC's licensees (the policy agencies are held for a license)", src("site", "lib", "pages.ts"))
        self.assertIn("While `policy_actions` is held (from 13 November 2026), no agency is listed", src("docs", "methods", "companies.md"))


if __name__ == "__main__":
    unittest.main()
