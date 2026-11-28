"""Audit of /impact's datacenter, finding 6 (session 11404, chain 770, docs/reviews/impact-datacenter-model-audit-2026-11-28.md):
the method note's decisions quote medians the file no longer holds. docs/methods/forecast.md 13.4, decision 1, gave the
median investment a MW as 10.0 and the mean as 17.11 "(54 rows)"; decision 2 gave "the 1,100 MW default (USD 11
billion) would be 550 jobs instead of 337"; 13.5's Illinois row gave "the default's 51.2 permanent jobs a 2025 USD
billion". The file (datacenter_announced.json, computed 27 November 2026, 72 rows in its medians) gives 12.0 and 17.00,
1,000 MW and USD 12 billion with 800 jobs by investment against 322.5 by MW, and 66.7 jobs a billion. And 13.1's
"operating years 5, 10, 15" reads as the fifth, tenth and fifteenth operating years; the model buys the equipment again
5, 10 and 15 years after the first operating year (the 6th, 11th and 16th), three purchases in 20 years, not four.

1. Against the page's own files and model (passes on main): the medians and counts above, recomputed from the rows; and
   through site/lib/dcimpact.ts (run by Node) the default run's refresh purchases fall in the 6th, 11th and 16th
   operating years.
2. The fix on this branch, words only (fails on main): the note's lines carry the file's figures and the refresh years."""
import json
import os
import statistics
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
const r = D.dcRun(D.dcDefaults(P, "va"), P);
const ops = r.years.filter((y) => y.phase === "operations");
console.log(JSON.stringify(ops.map((y, i) => [i + 1, y.equipment > 0])));
"""


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class StaleDecisions(unittest.TestCase):
    def test_the_file_holds_these_figures(self):
        A = json.loads(read("site", "data", "forecast", "datacenter_announced.json"))
        idx = json.loads(read("site", "data", "forecast", "deflator.json"))["index"]
        d = A["defaults"]
        rows = {r["id"]: r for r in A["rows"]}
        v = []
        for i in d["investment_per_mw"]["rows"]:
            r = rows[i]
            y = str(r["investment"]["year"])
            v.append(r["investment"]["value"] * (idx["2025"] / idx[y] if y in idx else 1) / 1e6 / r["mw"]["value"])
        self.assertEqual(statistics.median(v), 12.0)
        self.assertAlmostEqual(statistics.mean(v), 17.0041, places=3)
        self.assertEqual(sum(1 for r in A["rows"] if not r.get("to_date")), 72)
        self.assertEqual((d["mw_stated"]["median"], d["investment_per_mw"]["median"]), (1000.0, 12.0))
        self.assertAlmostEqual(12 * d["permanent_jobs_per_billion"]["median"], 800.0, places=3)
        self.assertAlmostEqual(1000 * d["permanent_jobs_per_mw"]["median"], 322.5)
        self.assertEqual(round(d["permanent_jobs_per_billion"]["median"], 1), 66.7)
        self.assertEqual(min(x["n"] for x in d.values()), 11)
        self.assertEqual(max(x["n"] for x in d.values()), 51)

    def test_refresh_years(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL, DATA], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        years = [n for n, bought in json.loads(out.stdout.strip().splitlines()[-1]) if bought]
        self.assertEqual(years, [6, 11, 16])

    def test_the_note_carries_the_files_figures(self):
        t = read("docs", "methods", "forecast.md")
        self.assertNotIn("the median, 10.0, keeps", t)
        self.assertIn("the median, 12.0, keeps", t)
        self.assertIn("USD 17.00 million a MW", t)
        self.assertNotIn("would be 550 jobs instead of 337", t)
        self.assertIn("would be 800 jobs instead of 322.5", t)
        self.assertIn("the default's 66.7 permanent jobs a 2025 USD billion", t)
        self.assertNotIn("(operating years 5, 10, 15, ... at the default cycle)", t)
        self.assertIn("the 6th, 11th and 16th operating years", t)


if __name__ == "__main__":
    unittest.main()
