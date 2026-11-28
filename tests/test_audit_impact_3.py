"""Audit of /impact's datacenter, finding 3 (session 11404, chain 770, docs/reviews/impact-datacenter-model-audit-2026-11-28.md):
the default construction workers are more than any announced document states. The default is the investment times the
median construction workers a USD billion, 833.3 (25 rows, chain 740's decision 27 after Meta's seven announcement
posts of campuses of USD 0.8 to 1 billion), so the default campus of USD 12 billion holds 10,000 workers on site in each
of its two construction years: 20,000 job-years, the page's first figure. Of the 45 announced rows that state a
construction headcount, the largest is 8,000 (the Department of Energy's Paducah site, USD 100 billion, period not
stated) and the largest at peak 7,500 (Meta's Hyperion, USD 50 billion). A ratio from small campuses, applied to a
large one, gives a headcount no large campus announces.

This branch makes no fix: a fix moves the construction jobs, earnings and income tax the page prints, which is Samuel's
ruling (chain 740's decision 27 already asks it). The test shows the size through site/lib/dcimpact.ts (run by Node)
on the page's own files: at 400 a billion (the median before Meta's posts) the Virginia default's construction jobs
fall 52 percent and its taxes' present value 10.4 percent; Texas's earnings' present value falls 40.4 percent."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = "file:///" + os.path.join(ROOT, "site", "lib", "dcimpact.ts").replace("\\", "/")
DATA = os.path.join(ROOT, "site", "data", "forecast")
JS = """
const D = await import(process.argv[1]);
const fs = await import("node:fs");
const data = (n) => JSON.parse(fs.readFileSync(process.argv[2] + "/" + n, "utf-8"));
const A = data("datacenter_announced.json");
const P = { announced: { defaults: A.defaults }, rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"), sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const Q = JSON.parse(JSON.stringify(P)); Q.announced.defaults.construction_jobs_per_billion.median = 400;
const out = {};
for (const st of ["va", "tx"]) {
  const x = D.dcDefaults(P, st), a = D.dcRun(x, P), b = D.dcRun(D.dcDefaults(Q, st), Q);
  out[st] = { invest: x.invest, cons: x.cons, build: x.build, cjobs: a.construction.jobs.onsite, cjobs400: b.construction.jobs.onsite, pvtax: a.pv.taxes, pvtax400: b.pv.taxes, pvearn: a.pv.earnings, pvearn400: b.pv.earnings };
}
console.log(JSON.stringify(out));
"""


class ConstructionWorkers(unittest.TestCase):
    def test_the_default_campus_holds_more_workers_than_any_document(self):
        with open(os.path.join(DATA, "datacenter_announced.json"), encoding="utf-8") as f:
            A = json.load(f)
        heads = sorted(((r["construction_jobs"]["value"], r["id"]) for r in A["rows"] if r.get("construction_jobs")), reverse=True)
        self.assertEqual(len(heads), 45)
        self.assertEqual(heads[0], (8000, "ky_paducah_2026"))
        med = A["defaults"]["construction_jobs_per_billion"]
        self.assertEqual((med["n"], med["median"]), (25, 833.333333))
        default_workers = round(12 * med["median"], 1)
        self.assertEqual(default_workers, 10000.0)
        self.assertGreater(default_workers, heads[0][0])

    def test_what_the_ratio_is_worth(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL, DATA], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        print(json.dumps(r))
        va, tx = r["va"], r["tx"]
        self.assertEqual((va["invest"], va["cons"], va["build"]), (12000, 10000, 2))
        self.assertEqual(va["cjobs"], 20000)
        self.assertEqual(va["cjobs400"], 9600)
        self.assertAlmostEqual(va["pvtax400"] / va["pvtax"] - 1, -0.1039, places=3)
        self.assertAlmostEqual(tx["pvearn400"] / tx["pvearn"] - 1, -0.4039, places=3)


if __name__ == "__main__":
    unittest.main()
