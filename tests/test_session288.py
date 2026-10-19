"""Session 288: the Games menu, the problem sets' words and the bill's season and shares, as Samuel ruled on 14 October 2026.

Energy Research Warehouse (ERW). No network, no model.
1. The menu (ruling 14): Games is the battery game, the tour, the bill explainer and "Problem sets" (the index of the
   five); the bill left Economics; the index lists all five sets.
2. The problem sets: "all hubs", named and counted (ruling 4); the latest complete month for sets B and D (5a); set E
   question 5 sets the storm's days against as many normal days (6a), with a check key check-values recomputes; the
   ratio questions reworded (7a).
3. The bill: every California default in winter, the season of 1 October 2026 when the tariffs were read (9a); the two
   time-of-use shares clamped at 100 together (10b). site/scripts/test-bill.mjs holds the hand-computed bills.

    python -m unittest tests.test_session288 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = node("import { GROUPS } from './lib/pages.ts'; console.log(JSON.stringify(Object.fromEntries(GROUPS.map((g) => [g.label, g.pages.map((p) => p.href)]))));")

    def test_games_is_the_ruled_four(self):
        # session 294: the EV game joins on the games branch (ruling 14's fifth entry)
        self.assertEqual(self.g["Games"], ["/play/battery", "/tour", "/learn/bill", "/learn/problems", "/play/ev"])

    def test_the_bill_left_economics(self):
        self.assertNotIn("/learn/bill", self.g["Economics"])

    def test_the_index_lists_all_five_sets(self):
        p = src("site", "lib", "problems.ts")
        sets = re.findall(r'\{ slug: "([^"]+)"', p)
        self.assertEqual(sets, ["know-your-grid", "prices-and-your-bill", "when-the-grid-broke", "storage-and-taxes", "networks-and-money"])
        self.assertIn("SETS.map((s) =>", src("site", "app", "learn", "problems", "page.tsx"))


class TheProblemSets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = src("site", "lib", "problems.ts")

    def test_hubs_named_and_counted(self):
        self.assertNotIn("all six ISO hubs", self.p)
        self.assertIn("The table holds ${ents.length} hubs: ${ents.map(hubName).join(\", \")}", self.p)
        for e, n in (("caiso:TH_NP15_GEN-APND", "CAISO NP15"), ("caiso:TH_SP15_GEN-APND", "CAISO SP15"), ("ercot:HB_HUBAVG", "ERCOT hub average"),
                     ("isone:.H.INTERNAL_HUB", "ISO-NE internal hub"), ("miso:INDIANA.HUB", "MISO Indiana hub"), ("nyiso:N.Y.C.", "NYISO New York City"),
                     ("spp:SPPNORTH_HUB", "SPP North hub")):
            self.assertIn(f'"{e}": "{n}"', self.p)
        self.assertNotIn("months may be partial", self.p)

    def test_latest_complete_month(self):
        b2 = self.p[self.p.index('id: "b2"') - 1600:self.p.index('id: "b2"')]
        # no month is whole at all seven hubs (ISO-NE misses hours): the latest month each holds at least 95 percent of
        self.assertIn("ents.every((e) => near(e, t))", b2)
        self.assertIn("const NEAR_FULL = 0.95;", self.p)
        self.assertIn("const pm = latestFull(prof, full);", self.p)                                   # set B, question 5
        self.assertIn('latestFull(prof, fullMonths(await series("cost_of_power_monthly"', self.p)     # set D, question 3
        self.assertIn('hours.get(day(r.ts_utc)) === r.value', self.p)

    def test_eighteen_days_against_eighteen(self):
        e5 = self.p[self.p.index('id: "e5"') - 900:self.p.index("return [q1, q2, q3, q4, q5];\n}\n\nexport const SETS")]
        self.assertIn('mrs("base_window", st.baseMean * st.days, "USD")', e5)
        self.assertIn('calc("ratio", tot, normal, "times")', e5)
        self.assertNotIn('calc("ratio", tot, week, "times")', e5)
        self.assertIn("against as many normal days", e5)

    def test_ratio_questions_reworded(self):
        for q in ("ERCOT's peak was how many times CAISO's?", "CAISO's discharge was how many times ERCOT's?",
                  "the highest 15-minute real-time price during the storm window was how many times the highest on the same days of 2019 and 2020?",
                  "Winter Storm Uri's highest 15-minute real-time price was how many times the summer 2023 heat's?"):
            self.assertIn(q, self.p)
        self.assertNotIn("how many times CAISO's was ERCOT's", self.p)
        self.assertNotIn("how many times the summer 2023 heat's highest", self.p)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_check_key_recomputes(self):
        self.assertIn('if (p[0] === "mrs") {', src("site", "scripts", "check-values.mjs"))
        got = node("""import * as M from './lib/merchant.ts'; import fs from 'node:fs';
const s = JSON.parse(fs.readFileSync('data/merchant_snapshot.json', 'utf-8'));
const sol = M.inputsOf({ iso: 'ercot', asset: 'solar' });
const e = M.stress(s, sol).find((x) => x.event === 'uri_2021');
console.log(JSON.stringify({ days: e.days, base: e.baseMean, week: M.stat(s, sol, 'stress_week:uri_2021'), tot: M.stat(s, sol, 'stress_total:uri_2021'), mean: M.stat(s, sol, 'stress_mean:uri_2021') }));""")
        self.assertAlmostEqual(got["week"], got["base"] * 7, places=6)
        # the storm's days against as many normal days: the total over (the mean normal day times the days) is the mean storm day over the mean normal day
        self.assertAlmostEqual(got["tot"] / (got["base"] * got["days"]), got["mean"] / got["base"], places=9)
        self.assertGreater(got["days"], 7)


@unittest.skipUnless(NODE, "node is not installed")
class TheBill(unittest.TestCase):
    def test_california_defaults_in_winter(self):
        rules = json.loads(src("site", "data", "bill_rules.json"))
        for k in ("CA", "SCE", "SDGE"):
            self.assertEqual(rules["bills"][k]["defaults"]["season"], "winter", k)
        page = src("site", "app", "learn", "bill", "page.tsx")
        self.assertNotIn('CA: "Summer,', page)
        self.assertNotIn('SDGE: "Summer,', page)

    def test_shares_clamped(self):
        got = node("""import { clampShares, defaultsTOU } from './lib/bill.ts'; import fs from 'node:fs';
const r = JSON.parse(fs.readFileSync('data/bill_rules.json', 'utf-8')); const d = defaultsTOU(r, 'SDGE');
console.log(JSON.stringify([clampShares({ ...d, superShare: 0.4 }, 'peakShare', 0.8).peakShare, clampShares({ ...d, peakShare: 0.8 }, 'superShare', 0.4).superShare, clampShares(d, 'peakShare', 0.1).peakShare]));""")
        self.assertAlmostEqual(got[0], 0.6)
        self.assertAlmostEqual(got[1], 0.2)
        self.assertAlmostEqual(got[2], 0.1)
        calc = src("site", "app", "learn", "bill", "BillCalc.tsx")
        self.assertNotIn("the off-peak share is negative", calc)
        self.assertIn('setShare("peakShare"', calc)
        self.assertIn('setShare("superShare"', calc)

    def test_hand_computed_bills(self):
        r = subprocess.run([NODE, "scripts/test-bill.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])


if __name__ == "__main__":
    unittest.main()
