"""Ruling alternative 1 of /play/ev (session 7720, 17 November 2026, branch wip/alt-ev-game-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-ev-game-2026-11-17.md, line 1): the home
electricity default, the state's average residential price or a family's time-of-use rate? On this branch California's
default is PG&E's E-TOU-C off-peak total rate, winter (1 October to 31 May), 36.757 cents (site/lib/ev.ts TOU_DEFAULT, as
site/data/bill_rules.json holds it). Pinned with the game's own arithmetic (verdict, at its defaults) on the committed
price file (site/scripts/alt-ev-game-figures.mjs). On the file built 17 November 2026 (California's August 2026 average
29.75 cents, gasoline USD 5.562): saved a year USD 1,707 to 1,381 (-19.1 percent), payback 2.9 to 3.6 years, net present
value USD 6,030 to 3,924 (-34.9 percent); at the summer off-peak, 39.940 cents, 1,233, 4.1 years and 2,968. The impact
file measured the same line on the file of 15 October (July's 33.61 cents): 1,897 to 1,750, NPV 7,258 to 6,312.

    python -m unittest tests.test_alt_ev_game_1 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheTimeOfUseDefault(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-ev-game-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_the_rate_is_the_bill_files(self):
        self.assertEqual(self.f["tou"], round(self.f["bill_winter"] * 1000, 2))

    def test_california_on_the_committed_file(self):
        f = self.f
        self.assertEqual((f["file_built"], f["ca_power"], f["ca_gas"]), ("2026-11-17T07:34:57Z", 297.5, 5.562))
        m, b = f["main"], f["branch"]
        self.assertEqual((round(m["saved"]), round(m["payback"], 1), round(m["npv"])), (1707, 2.9, 6030))
        self.assertEqual((round(b["saved"]), round(b["payback"], 1), round(b["npv"])), (1381, 3.6, 3924))

    def test_the_game_uses_it(self):
        with open(os.path.join(SITE, "app", "play", "ev", "EvGame.tsx"), encoding="utf-8") as fh:
            s = fh.read()
        self.assertIn("TOU_DEFAULT[st.code]", s)
        self.assertIn("keyed(defPower, place.gas.value)", s)


if __name__ == "__main__":
    unittest.main()
