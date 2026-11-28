"""Ready branch wip/ready-impact-project-split (session 11405, chain 770): part 3.3 of docs/reviews/weekend-2026-11-28.md,
"a picked project takes its document's own wage and spending split" (the audit
docs/reviews/impact-datacenter-model-audit-2026-11-28.md, finding 4, whose test wip/audit-impact-4 this carries over and
turns round; docs/methods/forecast.md, decision 28).

On main a picked project sets its MW, investment and jobs only: Project Blue (Pima County's bulletin: average salaries of
USD 64,000; USD 2.4 billion of 3.6 for equipment) keeps Census County Business Patterns' Arizona wage, 98,701, and
JLARC's split. On this branch the pick takes a stated annual wage and a stated split: Project Blue's operating earnings
USD 17.8 million a year to 11.5 (-35.2 percent), income tax over the life -17.4 percent, sales tax paid -2.25 percent,
taxes' present value -3.0 percent. A wage stated by the hour (Google's and Vantage's in Storey County) is not taken."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
JS = """
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const site = process.argv[1];
const data = (n) => JSON.parse(fs.readFileSync(site + "/data/forecast/" + n, "utf-8"));
const D = await import(pathToFileURL(site + "/lib/dcimpact.ts").href);
const M = await import(pathToFileURL(site + "/lib/dcui.ts").href);
const U = await import(pathToFileURL(site + "/lib/forecastui.ts").href);
const A = data("datacenter_announced.json");
const P = { announced: { defaults: A.defaults }, rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"), sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const list = M.dcProjects(A.rows, P.deflator.index);
const p = list.find((q) => q.id === "az_beale_pima_2025");
const set = { invest: p.invest, perm: p.perm, cons: p.cons };
const own = { ...set, opwage: p.opwage, ...p.split };
const r = (s) => { const x = D.dcDefaults(P, "az", s); const a = D.dcRun(x, P); return { opwage: x.opwage, earn: a.operations.earnings.onsite, income: a.sums.income, sales: a.sums.sales, pvtax: a.pv.taxes }; };
const q = { tech: "datacenter", state: "az", dcproj: "az_beale_pima_2025" };
const s = U.withProjects(U.parse(q), q, [], list.map((x) => x.id), list);
console.log(JSON.stringify({ p, before: r(set), after: r(own), addr: [s.a.opwage, s.a.bld, s.a.eq, s.a.land],
  hourly: ["nv_google_storey_2020", "nv_vantage_storey_2024"].map((i) => list.find((x) => x.id === i).opwage) }));
"""


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class StatedWagesTaken(unittest.TestCase):
    def test_the_rows_carry_the_stated_wage_and_split_as_figures(self):
        A = json.loads(read("site", "data", "forecast", "datacenter_announced.json"))
        R = json.loads(read("warehouse", "forecast", "datacenter_announced_rows.json"))
        self.assertEqual(A["rows"], R["rows"])  # the site file's rows are the builder's
        rows = {r["id"]: r for r in A["rows"]}
        b = rows["az_beale_pima_2025"]
        self.assertEqual((b["wage"]["value"], b["construction_cost"]["value"], b["equipment_cost"]["value"]), (64000, 1.2e9, 2.4e9))
        self.assertIn("average salaries of $64,000", b["wage"]["quote"])
        self.assertIn("$2.4 billion for equipment", b["equipment_cost"]["quote"])
        self.assertEqual(rows["mo_metrobloks_clay_2026"]["wage"]["value"], 95649)
        self.assertEqual(rows["al_facebook_huntsville_2018"]["wage"]["value"], 80000)
        self.assertNotIn("wage", rows["nv_google_storey_2020"])
        ui = read("site", "lib", "dcui.ts")
        self.assertIn("opwage: number | null", ui)
        W = json.loads(read("site", "data", "forecast", "datacenter_wages.json"))
        idx = json.loads(read("site", "data", "forecast", "deflator.json"))["index"]
        self.assertEqual(round(W["states"]["az"]["operations"]["per_job_usd"] * idx["2025"] / idx[str(W["year"])]), 98701)

    def test_the_pick_and_the_address_take_them(self):
        d = read("site", "app", "impact", "Datacenter.tsx")
        self.assertIn('"opwage", "bld", "eq", "land"', d)
        self.assertIn("...(p.opwage !== null ? { opwage: p.opwage } : {}), ...(p.split !== null ? p.split : {})", d)
        self.assertIn("the average annual wage (as the earnings per permanent job) and the split of the spending the document states", d)
        self.assertNotIn("A wage or a split of the spending that a document states is not taken", d)
        out = subprocess.run(["node", "--no-warnings", "--import", "./scripts/tsx-register.mjs", "--input-type=module", "-e", JS, SITE],
                             cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["p"]["opwage"], 64000)
        self.assertEqual(r["p"]["split"], {"bld": 33.3333, "eq": 66.6666, "land": 0})
        self.assertEqual(r["addr"], [64000, 33.3333, 66.6666, 0])
        self.assertEqual(r["hourly"], [None, None])
        b, a = r["before"], r["after"]
        self.assertEqual((b["opwage"], a["opwage"]), (98701, 64000))
        self.assertEqual((round(b["earn"]), round(a["earn"])), (17766180, 11520000))
        self.assertAlmostEqual(a["earn"] / b["earn"] - 1, -0.352, places=3)
        self.assertAlmostEqual(a["income"] / b["income"] - 1, -0.174, places=3)
        self.assertAlmostEqual(a["sales"] / b["sales"] - 1, -0.0225, places=4)
        self.assertAlmostEqual(a["pvtax"] / b["pvtax"] - 1, -0.030, places=3)

    def test_the_note_says_so(self):
        note = read("docs", "methods", "forecast.md")
        self.assertIn("28. **A picked project takes its document's own annual wage and split of the spending", note)
        self.assertIn("takes it as the earnings per permanent job instead (decision 28)", note)


if __name__ == "__main__":
    unittest.main()
