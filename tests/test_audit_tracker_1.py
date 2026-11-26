"""Audit of the datacenter power tracker, finding 1 (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md): the
scope words said "A facility found by several stories, or by the news and an operator's list (same operator and place),
is one row", which is not the news extractor's rule (the same operator or developer, the same site, or the same county
or city in a state, since session 166), and the page never said that one row joined on a state alone before that rule
(9,400 of the 28,254 MW stated on 25 November 2026) stays in every sum until the news table is rebuilt.

1. Through the page's library (site/lib/dctop.ts, run by Node): a facility's stated MW is in the sum whatever joined it;
   nothing in a row marks a join. Passes on main.
2. The fix on this branch, words only: the scope words state the two join rules and the one old join; the line under the
   bars says that row is in every sum. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dctop.ts").replace("\\", "/")
JS = """
const T = await import(process.argv[1]);
const row = (id, state, mw, extra) => ({ entity_id: id, name: id, capacity_mw: mw, status: "planned", operator: "", extra: { state, ...extra } });
const rows = [row("a", "UT", 9400, { first_story_at: "2025-03-04T08:00:00Z" }), row("b", "OH", 100, {}), row("c", "TX", null, {})].map(T.topRowOf);
const t = T.topBlock(rows, "2026-11-26");
console.log(JSON.stringify({ total: t.totalMw, withMw: t.withMw.length, noMw: t.noMw, byState: t.byState }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class OneOldJoinInTheSums(unittest.TestCase):
    def test_a_joined_row_is_summed_like_any_other(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["total"], 9500)
        self.assertEqual((r["withMw"], r["noMw"]), (2, 1))
        self.assertEqual(r["byState"][0], ["UT", 9400])
        # the builder's and the extractor's rules, as their notes state them
        self.assertIn("a state alone joins nothing", src("docs", "methods", "datacenter_projects.md"))
        self.assertIn("on the word \"Utah\" alone", src("docs", "methods", "datacenter_facilities.md"))

    def test_the_page_states_the_join_rules_and_the_old_join(self):
        page = flat(src("site", "app", "datacenters", "page.tsx"))
        self.assertNotIn("(same operator and place), is one row", page)
        self.assertIn("Stories are one facility when they name the same operator or developer, the same site, or the same county or city in a state; "
                      "a story and an operator&apos;s list are one when they share an operator and a place.", page)
        self.assertIn("One row was joined from two stories on their state alone, before that rule, and stays as it is until the news table is rebuilt.", page)
        body = flat(src("site", "app", "datacenters", "Body.tsx"))
        self.assertIn("One facility joined from two stories on their state alone, before the rule that now refuses such a join, is in every sum with the "
                      "megawatts of the later story until the news table is rebuilt (the tracker&apos;s method note, section 4).", body)


if __name__ == "__main__":
    unittest.main()
