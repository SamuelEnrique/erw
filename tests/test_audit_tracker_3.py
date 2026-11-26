"""Audit of the datacenter power tracker, finding 3 (session 10211, docs/reviews/tracker-model-audit-2026-11-26.md): the
headline "Megawatts stated" adds megawatts of every basis (mw_basis: IT load, a facility's total, a tenant's share, a
phase, or unstated: 20 of the 21 counted rows on 25 November 2026 state no basis, one a total), and the method note
(docs/methods/datacenter_tracker.md, section 4) says "the page says so beside it". Beside the rollups and the charts it
does; beside the headline, the sum a reader quotes, it did not.

1. Through the page's library (site/lib/dctop.ts, run by Node): a total and a row of unstated basis are added alike.
   Passes on main.
2. The fix on this branch, words only: the headline's note says the sum is of any basis. Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "dctop.ts").replace("\\", "/")
JS = """
const T = await import(process.argv[1]);
const row = (id, mw, basis) => ({ entity_id: id, capacity_mw: mw, status: "planned", operator: "", extra: { state: "OH", mw_basis: basis } });
const t = T.topBlock([row("a", 1000, "total"), row("b", 500, "unstated"), row("c", 50, "it_load")].map(T.topRowOf), "2026-11-26");
console.log(JSON.stringify({ total: t.totalMw, n: t.withMw.length }));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheHeadlineSaysItsBasis(unittest.TestCase):
    def test_every_basis_is_added_alike(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), {"total": 1550, "n": 3})
        self.assertIn("A sum adds MW of every basis, and the page says so beside it.", src("docs", "methods", "datacenter_tracker.md"))

    def test_the_headline_note_says_the_sum_is_of_any_basis(self):
        body = flat(src("site", "app", "datacenters", "Body.tsx"))
        self.assertIn("state no MW. A sum of any basis: IT load, a facility&apos;s total, a tenant&apos;s share or a phase, and for most a figure "
                      "whose basis the words do not say. By status, as the table has it:", body)


if __name__ == "__main__":
    unittest.main()
