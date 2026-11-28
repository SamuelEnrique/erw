"""Session 11408, readied for the owner's ruling (weekend page part 3.4, generator choice 9; the generator audit of 20
November, finding 9, docs/reviews/generator-model-audit-2026-11-20.md, carried from wip/audit-generator-9): the gas
peaker pays a cost per start, USD 50 per MW (the audit's middle sensitivity of 25, 50 and 100; no source, the value is
Samuel's to name), and a run that does not pay its start is skipped.

1. warehouse/derived/merchant_revenue.py, kept_runs: on a small case, a run worth less than its start is skipped; with
   a start cost of 0 every profitable hour runs (the rule until now).
2. The site's peakerOver (site/lib/merchant.ts, run by Node) on the page's snapshot, ERCOT, October 2025 to September
   2026: USD 37.14 per kW with 153 starts, against 48.15 with 406 (the month rows the page read); the Python rule on the
   same arrays gives the same figure.
3. The decision and the note's section 13 say so, word for word alike."""
import json
import os
import subprocess
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import merchant_revenue as mr  # noqa: E402

SNAP = os.path.join(ROOT, "site", "data", "merchant_snapshot.json")
L12 = ["2025-10", "2025-11", "2025-12"] + [f"2026-{k:02d}" for k in range(1, 10)]


class StartCost(unittest.TestCase):
    def test_kept_runs(self):
        p = [10, 100, 120, 10, 60, 10]
        cost = [50] * 6
        keep, starts = mr.kept_runs(p, cost, 50)
        self.assertEqual(list(keep), [False, True, True, False, False, False])   # 50 + 70 kept; 10 skipped
        self.assertEqual(starts, 1)
        keep0, starts0 = mr.kept_runs(p, cost, 0)
        self.assertEqual(list(keep0), [False, True, True, False, True, False])
        self.assertEqual(starts0, 2)
        self.assertEqual(mr.START_COST, 50.0)

    def test_the_site_and_the_builder_agree_on_ercot(self):
        js = ("const M = await import(process.argv[1]); const fs = await import('node:fs');"
              "const s = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')).isos.ercot;"
              "const L = JSON.parse(process.argv[3]); let a = 0, n = 0;"
              "for (const m of L) { const r = s.months[m]; const p = M.peakerOver(s, r.i0, r.i1, M.HEAT_RATE, M.VOM); a += p.revenue; n += p.starts; }"
              "console.log(JSON.stringify({ kw: a / 1000, starts: n }));")
        lib = "file:///" + os.path.join(ROOT, "site", "lib", "merchant.ts").replace("\\", "/")
        out = subprocess.run(["node", "--input-type=module", "-e", js, lib, SNAP, json.dumps(L12)], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertAlmostEqual(r["kw"], 37.14, places=2)
        self.assertEqual(r["starts"], 153)
        with open(SNAP, encoding="utf-8") as f:
            s = json.load(f)["isos"]["ercot"]
        self.assertAlmostEqual(sum(s["months"][m]["peaker"]["revenue_per_mw"] for m in L12) / 1000, 48.15, places=2)
        tot, starts = 0.0, 0
        for m in L12:
            row = s["months"][m]
            pr = [(p, h, (s.get("co2") or [None] * len(s["price"]))[i]) for i, (p, h) in enumerate(zip(s["price"], s["hh"])) if row["i0"] <= i < row["i1"]]
            pr = [(p, h * mr.HEAT_RATE + mr.VOM) for p, h, _c in pr if p is not None and h is not None]
            p, c = np.array([x[0] for x in pr]), np.array([x[1] for x in pr])
            keep, n = mr.kept_runs(p, c)
            tot += float((p[keep] - c[keep]).sum()) - mr.START_COST * n
            starts += n
        self.assertAlmostEqual(tot / 1000, r["kw"], places=6)
        self.assertEqual(starts, r["starts"])

    def test_the_words(self):
        words = "and a run that does not pay its start, USD 50 per MW (session 11408, no source; the value is the owner's), is skipped"
        for p in (("site", "lib", "decisions.ts"), ("docs", "methods", "generator_earns_algorithm.md")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                self.assertIn(words, f.read())


if __name__ == "__main__":
    unittest.main()
