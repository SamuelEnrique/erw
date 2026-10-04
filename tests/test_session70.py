"""Session 70: the home battery game v4, three rule fixes before its release.

Energy Research Warehouse (ERW). No network, no model, no database.
1. The lights-out charge is priced at Texas's value of lost load, USD 35,000 per MWh, with its sources; the search for a
   multiple of the cap and its test are gone.
2. Going dark at any point of the outage is charged for the whole outage; the perfect battery never ends in lights out
   where the lights can be kept on, the larger-inverter batteries included (site/scripts/test-battery.mjs, "Part A").
3. The roof is curtailed at a negative price unless the battery is charging.
4. The page and the method say each rule, and the figures match the library's.
5. Still version 4: no new rules version, no new migration.

    python -m unittest tests.test_session70 -v
"""

import glob
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class Library(unittest.TestCase):
    def setUp(self):
        self.b = src("site", "lib", "battery.ts")

    def test_the_price_is_the_value_of_lost_load(self):
        self.assertIn("usdPerMwh: 35_000, study: 35_685, residential: 3_964,", self.b)
        self.assertIn("voll: LIGHTS_OUT.usdPerMwh", self.b)
        self.assertIn("Project No. 55837", self.b)
        self.assertNotIn("penaltyMultiple", self.b)
        self.assertNotIn("multiple:", self.b)
        for p in (("site", "scripts", "test-battery.mjs"), ("site", "scripts", "check-lights.mjs"), ("site", "scripts", "check-scorer.mjs"),
                  ("site", "app", "play", "battery", "Game.tsx"), ("site", "app", "play", "battery", "page.tsx"), ("site", "lib", "game.ts")):
            self.assertNotIn("penaltyMultiple", src(*p), p)
            self.assertNotIn("LIGHTS_OUT.multiple", src(*p), p)

    def test_lights_out_is_charged_for_the_whole_outage(self):
        # both the scorer and the perfect battery price the outage from its first interval, whenever the lights go out
        self.assertIn("const u = unserved(em.outage.first, em.outage.last, sun, r);", self.b)
        self.assertIn("const dark = out ? unserved(em.outage!.first, em.outage!.last, sun, r).usd : 0;", self.b)
        self.assertNotIn("unserved(i, ", self.b)
        self.assertIn("return { kwh, usd: (kwh * r.voll) / 1000 };", self.b)

    def test_the_roof_is_curtailed_below_zero(self):
        self.assertIn("function roofSale(sun: number, price: number, stored: number, r: Rules)", self.b)
        self.assertIn("if (price >= 0 || sun <= 0) return { usd: (sun * price) / 1000, curtailed: 0 };", self.b)
        # one function, called by the scorer and by the perfect battery
        self.assertEqual(self.b.count("roofSale(sun[i], P[i], "), 2)
        self.assertIn("the roof is switched off and earns nothing", self.b)

    def test_still_version_4(self):
        self.assertIn('export const RULES_VERSION = "v4";', self.b)
        # session 83: the newest migration of the game, not the newest migration (020 is the contracts page's functions)
        names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "warehouse", "supabase", "migrations", "*_game_*.sql")))
        self.assertEqual(names[-1], "019_game_v4.sql")


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class Node(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = subprocess.run(["node", "scripts/test-battery.mjs"], cwd=SITE, capture_output=True, text=True, timeout=1200)

    def test_it_passes(self):
        self.assertEqual(self.r.returncode, 0, self.r.stdout[-3000:] + self.r.stderr[-2000:])
        self.assertNotIn("FAIL", self.r.stdout)

    def test_the_required_result(self):
        out = self.r.stdout
        m = re.search(r"Part A: (\d+) cases \((\d+) with the 11\.5 kW inverter\), (\d+) where the lights can be kept on", out)
        self.assertIsNotNone(m, out[-2000:])
        self.assertEqual(m.group(1), m.group(3))                 # the lights can be kept on in every case
        self.assertGreaterEqual(int(m.group(2)), 54)             # six larger-inverter batteries on nine days
        self.assertIn("ok   Part A: at USD 35000/MWh for the whole outage the perfect battery never ends in lights out where the lights can be kept on", out)
        table = [ln for ln in out.splitlines() if ln.startswith("  v4, ")]
        self.assertEqual(len(table), 7)
        self.assertFalse([ln for ln in table if "lights_out" in ln])

    def test_the_charge_and_the_roof(self):
        out = self.r.stdout
        for label in ("ok   the lights-out charge is priced at USD 35000/MWh", "ok   lights out costs money: 4 intervals x 0.375 kWh at USD 35000/MWh = USD 52.5000",
                      "is charged for all 8 intervals, USD 105.0000, as lights out at interval 4 is", "ok   a whole two-hour outage in the dark costs USD 105.00",
                      "ok   below zero an idle battery's roof is curtailed", "ok   below zero a selling battery's roof is curtailed too",
                      "ok   below zero a charging battery takes the roof's power first", "ok   a roof larger than the charge",
                      "ok   a full battery told to charge takes nothing", "ok   at a price of zero or more nothing is curtailed", "ok   the DP plays by the curtailment rule",
                      # the DP against brute force under the two presets added for these rules, on every toy day
                      "ok   hard, default battery, rooftop solar, early sun, negative", "ok   hard, default battery, rooftop solar, early sun, flat",
                      "ok   hard, 13.5 kWh, 11.5 kW, no reserve, flat", "ok   hard, 13.5 kWh, 11.5 kW, no reserve, spike"):
            self.assertIn(label, out)


class Words(unittest.TestCase):
    def test_the_page(self):
        page = src("site", "app", "play", "battery", "page.tsx")
        self.assertIn("If the lights go out at any moment of the outage, you pay for the power the house needed in the whole outage, not only the part it missed", page)
        self.assertIn("Public Utility Commission of Texas approved for the ERCOT region on 29 August 2024 (Project No. 55837", page)
        self.assertIn("{LIGHTS_OUT.study.toLocaleString(\"en-US\")}", page)
        self.assertIn("{LIGHTS_OUT.residential.toLocaleString(\"en-US\")}", page)
        self.assertIn("the game uses the Texas figure on the California days too", page)
        self.assertIn("href={LIGHTS_OUT.release}", page)
        self.assertIn("href={LIGHTS_OUT.report}", page)
        self.assertNotIn("times the cap", page)
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn("you pay for the power the house needed in the whole outage, not only the part it missed", game)
        self.assertIn("LIGHTS_OUT.usdPerMwh", game)
        self.assertIn("(switched off: the price is below zero)", game)

    def test_the_method(self):
        m = src("docs", "methods", "battery_game.md")
        for part in ("**USD 35,000 per MWh**", "Project No. 55837", "$35,685 per MWh", "USD 3,964 for residential customers", "did not memorialize its vote in a written order",
                     "PUCT_Adopts_Reliability_Standard_for_the_ERCOT_Market.pdf", "Value-of-Lost-Load-Study-for-the-ERCOT-Region.pdf",
                     "The game applies the Texas figure on the California days too", "the unserved energy of the whole outage", "USD 105.00",
                     "Below zero the roof is curtailed (session 70)", "73 cases"):
            self.assertIn(part, m)
        self.assertNotIn("6 times the price cap**", m)

    def test_no_em_dash(self):
        for p in (("site", "lib", "battery.ts"), ("site", "app", "play", "battery", "Game.tsx"), ("site", "app", "play", "battery", "page.tsx"),
                  ("site", "scripts", "test-battery.mjs"), ("site", "scripts", "check-lights.mjs"), ("site", "scripts", "check-scorer.mjs"),
                  ("docs", "methods", "battery_game.md"), ("tests", "test_session66.py"), ("tests", "test_session70.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
