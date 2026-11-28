"""Ready branch wip/ready-impact-meta-out (session 11405, chain 770): decision 7 of docs/reviews/weekend-2026-11-28.md,
Meta's seven announcement posts out of the datacenter medians on /impact (docs/methods/forecast.md, decision 27; the
audit docs/reviews/impact-datacenter-model-audit-2026-11-28.md, finding 3, whose test wip/audit-impact-3 this carries
over and turns round).

On main the seven posts (requests 545 to 551) enter every median: the construction workers default is 833.3 a USD
billion (25 projects), 10,000 workers in each construction year of the default USD 12 billion campus, more than any
document states. On this branch they are offered in the picker and enter no median: 400 a billion (18 projects),
4,800 workers a year; Virginia's default construction jobs 20,000 to 9,600 (-52 percent), its taxes' present value
-10.4 percent, Texas's earnings' present value -40.4 percent.

The site file is the builder's own output from files in the repository, rebuilt here and checked to be current."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = "file:///" + os.path.join(ROOT, "site", "lib", "dcimpact.ts").replace("\\", "/")
DATA = os.path.join(ROOT, "site", "data", "forecast")
SEVEN = {"in_meta_jeffersonville_announce_2024", "wi_meta_beaverdam_announce_2025", "tx_meta_temple_announce_2022",
         "id_meta_kuna_announce_2022", "mo_meta_kansascity_announce_2022", "az_meta_mesa_announce_2021",
         "tn_meta_gallatin_announce_2020"}
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


class MetaPostsOut(unittest.TestCase):
    def setUp(self):
        self.A = json.loads(load("site", "data", "forecast", "datacenter_announced.json"))

    def test_the_seven_posts_are_offered_and_enter_no_median(self):
        ids = {r["id"] for r in self.A["rows"]}
        self.assertTrue(SEVEN <= ids)
        self.assertEqual(set(self.A["left_out"]["rows"]), SEVEN)
        for k, s in self.A["defaults"].items():
            self.assertFalse(SEVEN & set(s.get("rows", [])), k)
        med = self.A["defaults"]["construction_jobs_per_billion"]
        self.assertEqual((med["n"], med["median"]), (18, 400.0))
        perm = self.A["defaults"]["permanent_jobs_per_billion"]
        self.assertEqual((perm["n"], perm["median"]), (44, 53.995782))
        # the medians dcDefaults reads other than construction do not move
        self.assertEqual(self.A["defaults"]["mw_stated"]["median"], 1000.0)
        self.assertEqual(self.A["defaults"]["investment_per_mw"]["median"], 12.0)
        self.assertEqual(self.A["defaults"]["permanent_jobs_per_mw"]["median"], 0.3225)

    def test_the_default_campus_holds_no_more_workers_than_the_documents(self):
        heads = sorted((r["construction_jobs"]["value"] for r in self.A["rows"] if r.get("construction_jobs")), reverse=True)
        self.assertEqual(heads[0], 8000)
        self.assertLess(12 * self.A["defaults"]["construction_jobs_per_billion"]["median"], heads[0])

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
        self.assertEqual((va["invest"], va["cons"]), (12000, 4800))
        self.assertEqual((va["cjobs"], va["cjobsMain"]), (9600, 20000))
        self.assertAlmostEqual(va["pvtax"] / va["pvtaxMain"] - 1, -0.1039, places=3)
        self.assertAlmostEqual(tx["pvearn"] / tx["pvearnMain"] - 1, -0.4039, places=3)

    def test_the_page_and_the_note_say_so(self):
        d = load("site", "app", "impact", "Datacenter.tsx")
        self.assertIn("announcement posts of campuses it also reports to date are offered and enter no median either", d)
        self.assertIn("left_out", load("site", "lib", "forecastdata.ts"))
        note = load("docs", "methods", "forecast.md")
        self.assertIn("| Construction workers each year | investment times 400 a USD billion | the median of 18 projects'", note)
        self.assertNotIn("investment times 833.3 a USD billion", note)
        self.assertIn("enters no median (session 10822; taken out by Samuel's ruling", note)


if __name__ == "__main__":
    unittest.main()
