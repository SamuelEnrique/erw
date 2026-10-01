"""Session 48: known gaps open no issue, and the draft shape premium report.

Energy Research Warehouse (ERW). No network, no model.
1. warehouse/metadata/run_status.py streaks: a table in warehouse/metadata/known_gaps.csv that failed three runs in a row
   is printed as a known gap and left out of the file the workflow opens issues from; another table is written.
2. site/lib/shapepremium.ts's statistics equal an independent pandas computation on cost_of_power_monthly, where the
   table is on this machine: complete months, months with a positive premium, the mean premium and premium x hours.
3. /reports/draft/shape-premium: gated by the internal token (404 without it), not indexed, not in the nav.

    python -m unittest tests.test_session48 -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import run_status  # noqa: E402


class KnownGaps(unittest.TestCase):
    def test_a_known_gap_opens_no_issue(self):
        tmp = tempfile.mkdtemp()
        try:
            hist = os.path.join(tmp, "run_status.csv")
            rows = []
            for i, run in enumerate(["20260927T000000Z", "20260928T000000Z", "20260929T000000Z"]):
                for table in ("carb_auction_allowance_prices", "some_new_table"):
                    rows.append(dict(run_id=run, runner="github", connector="c", table=table, market="all",
                                     status="failed", detail=f"run {i}"))
            pd.DataFrame(rows).to_csv(hist, index=False)
            gaps = os.path.join(tmp, "known_gaps.csv")
            pd.DataFrame([dict(table="carb_auction_allowance_prices", reason="HTTP 202", since="2026-09-27",
                               decided="test")]).to_csv(gaps, index=False)
            found = run_status.streaks(3, path=hist, runner="github")
            self.assertEqual(sorted(f["table"] for f in found), ["carb_auction_allowance_prices", "some_new_table"])
            known = run_status.known_gaps(gaps)
            self.assertEqual([f["table"] for f in found if f["table"] not in known], ["some_new_table"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_real_list_names_the_three(self):
        k = run_status.known_gaps()
        for t in ("carb_auction_allowance_prices", "nyiso_interconnection_queue", "ercot_large_load_queue"):
            self.assertIn(t, k)
            self.assertTrue(k[t])


class ShapeStats(unittest.TestCase):
    def test_against_pandas(self):
        path = os.path.join(ROOT, "warehouse", "output", "cost_of_power_monthly.csv")
        node = shutil.which("node")
        if not os.path.exists(path) or not node:
            self.skipTest("cost_of_power_monthly.csv or node is not on this machine")
        n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
        df = pd.read_csv(path, skiprows=n)
        e = "ercot:HB_HUBAVG"
        w = df[df.entity == e].pivot_table(index="ts_utc", columns="variable", values="value").reset_index()
        w = w[(w.rt_hours == w.hours_in_month) & (w.ts_utc >= "2019-01-01") & (w.ts_utc < "2026-01-01")]
        want = dict(n=len(w), npos=int((w.rt_shape_premium > 0).sum()), mean=float(w.rt_shape_premium.mean()),
                    usdmw=float((w.rt_shape_premium * w.rt_hours).sum()))
        rows = df[df.entity == e][["entity", "variable", "ts_utc", "value"]].to_dict("records")
        tmp = tempfile.mkdtemp()
        try:
            jp = os.path.join(tmp, "rows.json")
            json.dump(rows, open(jp, "w", encoding="utf-8"))
            js = ("import fs from 'node:fs'; import { stats } from './lib/shapepremium.ts';"
                  f"const rows = JSON.parse(fs.readFileSync({json.dumps(jp)}, 'utf-8'));"
                  f"console.log(JSON.stringify(stats(rows, '{e}', 'rt', '2019-01-01', '2026-01-01')));")
            r = subprocess.run([node, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            got = json.loads(r.stdout.strip().splitlines()[-1])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(got["n"], want["n"])
        self.assertEqual(got["npos"], want["npos"])
        self.assertAlmostEqual(got["mean"], want["mean"], places=6)
        self.assertAlmostEqual(got["usdmw"], want["usdmw"], places=3)


class ReportPage(unittest.TestCase):
    def test_gated_unindexed_not_in_nav(self):
        page = open(os.path.join(SITE, "app", "reports", "draft", "shape-premium", "page.tsx"), encoding="utf-8").read()
        self.assertIn('if (want.length < 24 || token !== want) notFound();', page)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertNotIn("/reports", open(os.path.join(SITE, "lib", "pages.ts"), encoding="utf-8").read())
        self.assertNotIn(chr(0x2014), page)


if __name__ == "__main__":
    unittest.main()
