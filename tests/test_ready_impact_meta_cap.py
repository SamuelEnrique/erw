"""Ready branch wip/ready-impact-meta-cap (session 11405, chain 770): decision 7 of docs/reviews/weekend-2026-11-28.md,
its second branch: a cap on one company's rows in the datacenter medians on /impact (docs/methods/forecast.md,
decision 27; the audit docs/reviews/impact-datacenter-model-audit-2026-11-28.md, finding 3, whose test
wip/audit-impact-3 this carries over and turns round).

On main Meta gives 15 of the construction median's 25 projects: 833.3 construction workers a USD billion, 10,000
workers in each construction year of the default USD 12 billion campus. On this branch one company gives at most two
projects to any median, its newest documents (two: no company but Meta gives more than two to the construction median,
and none more than two to the size, investment and jobs per MW medians, which stay as they were): 258.3 a billion (12
projects), 3,100 workers a year; Virginia's default construction jobs 20,000 to 6,200, its taxes' present value -13.8
percent, Texas's earnings' present value -53.6 percent. The permanent jobs per billion (the hover only) 66.7 of 51 to
35.6 of 20."""
import collections
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = "file:///" + os.path.join(ROOT, "site", "lib", "dcimpact.ts").replace("\\", "/")
DATA = os.path.join(ROOT, "site", "data", "forecast")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "forecast"))
import datacenter_announced as builder  # noqa: E402

JS = """
const D = await import(process.argv[1]);
const fs = await import("node:fs");
const data = (n) => JSON.parse(fs.readFileSync(process.argv[2] + "/" + n, "utf-8"));
const A = data("datacenter_announced.json");
const P = { announced: { defaults: A.defaults }, rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"), sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const Q = JSON.parse(JSON.stringify(P)); Q.announced.defaults.construction_jobs_per_billion.median = 833.333333;
const out = {};
for (const st of ["va", "tx"]) {
  const x = D.dcDefaults(P, st), a = D.dcRun(x, P), b = D.dcRun(D.dcDefaults(Q, st), Q);
  out[st] = { invest: x.invest, cons: x.cons, cjobs: a.construction.jobs.onsite, cjobsMain: b.construction.jobs.onsite, pvtax: a.pv.taxes, pvtaxMain: b.pv.taxes, pvearn: a.pv.earnings, pvearnMain: b.pv.earnings };
}
console.log(JSON.stringify(out));
"""


def load(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class CompanyCap(unittest.TestCase):
    def setUp(self):
        self.A = json.loads(load("site", "data", "forecast", "datacenter_announced.json"))
        self.rows = {r["id"]: r for r in self.A["rows"]}

    def test_no_company_gives_more_than_two_rows_to_a_median(self):
        self.assertEqual(builder.COMPANY_CAP, 2)
        self.assertEqual(self.A["capped_out"]["cap"], 2)
        self.assertEqual(builder.parent("Facebook (Meta)"), "meta")
        self.assertEqual(builder.parent("Meta Platforms (Vemerald)"), "meta")
        self.assertEqual(builder.parent("Amazon Web Services; STACK Infrastructure"), "amazon")
        for k, s in self.A["defaults"].items():
            c = collections.Counter(builder.parent(self.rows[i]["company"]) for i in s["rows"])
            self.assertLessEqual(max(c.values()), 2, k)
            for i in self.A["capped_out"]["rows"].get(k, []):
                self.assertIn(i, self.rows)
                self.assertNotIn(i, s["rows"])
        med = self.A["defaults"]["construction_jobs_per_billion"]
        self.assertEqual((med["n"], med["median"]), (12, 258.333333))
        self.assertIn("ok_meta_tulsa_announce_2026", med["rows"])
        self.assertIn("la_meta_richland_2026", med["rows"])
        self.assertEqual(len(self.A["capped_out"]["rows"]["construction_jobs_per_billion"]), 13)
        perm = self.A["defaults"]["permanent_jobs_per_billion"]
        self.assertEqual((perm["n"], perm["median"]), (20, 35.625))
        self.assertEqual(self.A["defaults"]["mw_stated"]["median"], 1000.0)
        self.assertEqual(self.A["defaults"]["investment_per_mw"]["median"], 12.0)
        self.assertEqual(self.A["defaults"]["permanent_jobs_per_mw"]["median"], 0.3225)
        self.assertEqual(len(self.A["rows"]), 93)

    def test_the_site_file_is_the_builders_output(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "forecast", "datacenter_announced.py"), "--check"],
                             capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout), self.A["defaults"])

    def test_what_it_moves(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL, DATA], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        va, tx = r["va"], r["tx"]
        self.assertEqual((va["invest"], va["cons"]), (12000, 3100))
        self.assertEqual((va["cjobs"], va["cjobsMain"]), (6200, 20000))
        self.assertAlmostEqual(va["pvtax"] / va["pvtaxMain"] - 1, -0.1379, places=3)
        self.assertAlmostEqual(tx["pvearn"] / tx["pvearnMain"] - 1, -0.5360, places=3)

    def test_the_page_and_the_note_say_so(self):
        self.assertIn("One company gives at most ${P2.announced.capped_out.cap} projects to a median", load("site", "app", "impact", "Datacenter.tsx"))
        self.assertIn("capped_out", load("site", "lib", "forecastdata.ts"))
        note = load("docs", "methods", "forecast.md")
        self.assertIn("| Construction workers each year | investment times 258.3 a USD billion | the median of 12 projects'", note)
        self.assertIn("27. **One company gives at most two projects to any median", note)


if __name__ == "__main__":
    unittest.main()
