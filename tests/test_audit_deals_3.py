"""Audit of the energy deal tracker, finding 3 (session 10215, docs/reviews/deals-model-audit-2026-11-26.md): decision 4
says no sum is drawn across every kind of deal and its default reads "sums are by the kind of supply on the AI view". The
AI view groups by buyer by default, and by grid and quarter too, and sums the US dollars of every tagged deal of a group,
whatever its kind and stage: on the rows of 12 November 2026, 15 of the 82 buyers' sums add two kinds of supply or more
(USD 1.13 trillion), 6 of the 7 quarters' do, rumored talks are USD 235 billion of the USD 3.06 trillion, and the
register's doubtful pairs add USD 55 billion twice. The tracker's headline note also names "a valuation" among the values
in US dollars, which decision 4 and the table's column tip say is not kept.

1. Through the page's library (site/lib/dealsai.ts, run by Node): a buyer's US-dollar sum adds a raise and a compute
   contract, and a rumored deal with a signed one; by the kind of supply they are apart. Passes on main.
2. The fix on this branch, words only: decision 4's default (site/lib/decisions.ts and the method note, word for word), the
   AI view's lead and the method note's section 7.4 say what a group's sum adds; the tracker's note says a contract's value,
   not a valuation. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dealsai.ts").replace("\\", "/")
JS = """
const A = await import(%s);
const d = (id, kind, status, dollars) => ({ id, date: "2026-02-10", month: "2026-02", year: "2026", type: "", group: "other", status, buyer: "B", seller: "S",
  others: [], names: ["B", "S"], asset: "", technology: "", state: "", country: "", grid: "", mw: null, mwh: null, dollars, price: null, priceOther: null,
  termYears: null, ai: true, storage: false, kinds: [], source: "", links: [], folded: [], kind, buyerName: "B", sellerName: "S", aiBasis: "" });
const deals = [d("a", "capital", "rumored", 40e9), d("b", "compute_capacity", "signed", 10e9)];
const byBuyer = A.aiCells(deals, "buyer").map((c) => [c.value, c.usd, c.withUsd]);
const bySupply = A.aiCells(deals, "supply").map((c) => [c.value, c.usd]);
console.log(JSON.stringify({ byBuyer, bySupply }));
""" % json.dumps(LIB)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheDollarSumsOfTheAiView(unittest.TestCase):
    def test_a_buyers_sum_adds_kinds_and_stages(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        got = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(got["byBuyer"], [["B", 50e9, 2]])
        self.assertEqual(sorted(got["bySupply"]), [["capital", 40e9], ["compute", 10e9]])

    def test_the_words_say_what_a_sum_adds(self):
        default = ("No total over all deals. The AI view sums the US dollars of each group it shows: by the kind of supply, one kind a sum; by "
                   "buyer (its default), grid or quarter, a group's sum adds raises, acquisitions, financings and contracts together, rumored "
                   "deals among them.")
        self.assertIn(f'def: "{default}"', src("site", "lib", "decisions.ts"))
        note = src("docs", "methods", "deal_tracker.md")
        self.assertIn(f"**Default:** {default} **Source:** The extraction's prompt and session 2271's rule", note)
        self.assertIn("by buyer, grid or quarter a US-dollar sum adds a raise, an acquisition, a financing and a compute contract alike", flat(note))
        ai = flat(src("site", "app", "deals", "ai", "view.tsx"))
        self.assertIn("A group&apos;s sum adds every kind of deal in it and every stage: by buyer, grid or quarter, the US dollars of a raise, an "
                      "acquisition, a financing and a compute contract are added together, rumored talks with signed deals; grouped by the kind "
                      "of supply, each sum is of one kind.", ai)
        v2 = flat(src("site", "app", "deals", "v2", "view.tsx"))
        self.assertNotIn("a financing or a valuation", v2)
        self.assertIn("a purchase price, a financing or a contract&apos;s value, each as stated (a valuation is not kept)", v2)


if __name__ == "__main__":
    unittest.main()
