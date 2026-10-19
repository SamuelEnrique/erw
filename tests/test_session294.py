"""Session 294: "Should your family get an EV?" (/play/ev), Samuel's ruling 17 of 14 October 2026.

Energy Research Warehouse (ERW). No network, no model.
Five screens: where you live (each state's home electricity price and gasoline price, with table and date; a state
without its own gasoline series takes its region's, and says so), your car (sliders with sourced defaults and a reset),
the money (prices, years kept, a federal credit off by default with the IRS's line), the verdict (two bars, a year,
payback and NPV, what would change the answer), and every number for the parents with a print button. The solar half is
not built.

    python -m unittest tests.test_session294 -v
"""

import csv
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
OUT = os.path.join(ROOT, "warehouse", "output")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
class TheArithmetic(unittest.TestCase):
    def test_hand_computed(self):
        r = subprocess.run([NODE, "scripts/test-ev.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertIn("ok   NPV, 8 years at 5 percent: $7258.00", r.stdout)


class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(src("site", "data", "ev_prices.json"))

    def test_shape(self):
        self.assertEqual(len(self.d["states"]), 51)
        self.assertEqual(set(self.d["sources"]), {"eia_retail_electricity_prices", "eia_regional_retail_fuel_prices"})
        for s in self.d["states"]:
            self.assertTrue(s["power"]["entity"].endswith(f":{s['code']}:RES"), s)
            self.assertTrue(s["gas"]["entity"].startswith("eia:EMM_EPMR_PTE_"), s)

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "eia_regional_retail_fuel_prices.csv")), "the warehouse's tables are not on this machine")
    def test_values_are_the_tables(self):
        want = {s["gas"]["entity"]: (s["gas"]["ts"], s["gas"]["value"]) for s in self.d["states"]}
        got = {}
        with open(os.path.join(OUT, "eia_regional_retail_fuel_prices.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r["entity"] in want and r["ts_utc"][:10] == want[r["entity"]][0]:
                    got[r["entity"]] = float(r["value"])
        for e, (_, v) in want.items():
            self.assertEqual(got.get(e), v, e)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = src("site", "app", "play", "ev", "EvGame.tsx")

    def test_five_screens(self):
        self.assertIn('const SCREENS = ["Where do you live?", "Your car", "The money", "The verdict", "Show your parents"];', self.g)
        for s in range(5):
            self.assertIn(f"step === {s} ", self.g)

    def test_the_credit_is_off_by_default_and_says_why(self):
        self.assertIn("const [creditOn, setCreditOn] = useState(false);", self.g)
        self.assertIn("{NO_CREDIT_LINE}", self.g)
        self.assertIn('NO_CREDIT_LINE = "No federal credit for cars bought after 30 September 2025."', src("site", "lib", "ev.ts"))
        self.assertIn("your family's own assumption", src("site", "lib", "ev.ts"))

    def test_region_said(self):
        self.assertIn("EIA does not publish a weekly price for", self.g)

    def test_every_number_with_its_source_and_print(self):
        self.assertIn('aria-label="Every number used"', self.g)
        self.assertIn('<PrintButton label="Print for my parents" />', self.g)
        self.assertIn('"changed by you"', self.g)

    def test_no_solar_and_the_brand(self):
        self.assertNotIn("solar", self.g.lower())
        self.assertIn("<Brand noUsage>", src("site", "app", "play", "ev", "page.tsx"))
        for t in ("rounded", "#", "rgba("):
            self.assertNotIn(t, self.g.replace("&apos;", "").replace("&#", ""), t)

    def test_menu_and_method(self):
        self.assertIn('href: "/play/ev"', src("site", "lib", "pages.ts"))
        self.assertIn('"/play/ev"', src("site", "scripts", "check-routes.mjs"))
        m = src("docs", "methods", "ev_game.md")
        self.assertIn("No federal credit for cars bought after 30 September 2025.", m)
        self.assertNotIn(chr(0x2014), m + self.g + src("site", "lib", "ev.ts"))


if __name__ == "__main__":
    unittest.main()
