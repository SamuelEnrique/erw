"""Session 1607 (chain 165): the gas and oil spreads.

Held here: a product's crack is its gallon times 42 less the crude's barrel on the days both are published, on EIA's
real closes (tests/fixtures/board_1607/), with the newest day's inputs for the hover; the gas spreads are the World
Bank's monthly prices less each other, built only where its table is (it is not on the old laptop: the arithmetic is
checked on an in-memory reading, not on a fixture of invented values); the regional basis and the LNG netback are
placeholders naming who would supply them; the page writes a single-product crack's inputs. No network, no model.
Nothing here sets the environment at import.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1607")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


class TheSpreads(unittest.TestCase):
    def setUp(self):
        self.bp = builder()
        self.saved, self.absent = self.bp.ip.OUT_DIR, list(self.bp.ABSENT)
        self.bp.ip.OUT_DIR = FIX

    def tearDown(self):
        self.bp.ip.OUT_DIR, self.bp.ABSENT[:] = self.saved, self.absent

    def fuels(self):
        out = {}
        for t in ("eia_product_spot_prices", "eia_fuel_spot_prices"):
            s, _ = self.bp.table_daily(t)
            out.update({e: v for (e, var), v in s.items() if var == "spot_price"})
        return out

    def test_the_heating_oil_crack_on_the_real_closes(self):
        b = self.bp.Board()
        self.bp.build_fuel_spreads(b, self.fuels(), lambda s: None)
        rows = {r["id"]: r for r in b.rows}
        r = rows["eia-eer-epd2f-pf4-y35ny-dpg-less-eia-brent"]
        p = pd.read_csv(os.path.join(FIX, "eia_product_spot_prices.csv"), comment="#")
        c = pd.read_csv(os.path.join(FIX, "eia_fuel_spot_prices.csv"), comment="#")
        p = p[p["entity"] == "eia:EER_EPD2F_PF4_Y35NY_DPG"].set_index("ts_utc")["value"]
        c = c[c["entity"] == "eia:brent"].set_index("ts_utc")["value"]
        both = sorted(set(p.index) & set(c.index))
        self.assertEqual(r["last"]["t"], both[-1][:10])
        self.assertAlmostEqual(r["last"]["v"], p[both[-1]] * 42 - c[both[-1]], places=3)
        self.assertEqual(r["inputs"], {"t": both[-1][:10], "product": round(float(p[both[-1]]), 4), "crude": round(float(c[both[-1]]), 4)})
        self.assertEqual((r["group"], r["label"], r["unit"]), ("oilspreads", "Heating oil crack", "USD/bbl"))
        self.assertTrue(r["formula"].startswith("New York Harbor No. 2 heating oil x 42 - Brent"))
        # a crack whose product is not in the fixture is "not held yet", never a figure
        self.assertEqual(rows["eia-eer-epjk-pf4-rgc-dpg-less-eia-wti-cushing"]["status"], "not_held")

    def test_the_gas_spreads_where_the_table_is(self):
        b = self.bp.Board()
        self.bp.build_fuel_spreads(b, {}, lambda s: None)
        ids = {r["id"] for r in b.rows}
        self.assertFalse([i for i in ids if i.startswith("erw-wb")])                 # the table is not in the fixture: no row
        self.assertIn("gasbasis-regional", ids)
        self.assertIn("lng-netback", ids)
        months = {dt.date(2026, 8, 1): 11.0, dt.date(2026, 9, 1): 12.5}
        us = {dt.date(2026, 8, 1): 3.0, dt.date(2026, 9, 1): 2.5}
        saved_here, saved_read = self.bp.here, self.bp.table_daily
        self.bp.here = lambda name: True
        self.bp.table_daily = lambda name, since=None: ({("wb_pink:natural_gas_europe", "price"): months, ("wb_pink:natural_gas_us", "price"): us}, {})
        try:
            b = self.bp.Board()
            self.bp.build_fuel_spreads(b, {}, lambda s: None)
        finally:
            self.bp.here, self.bp.table_daily = saved_here, saved_read
        r = next(r for r in b.rows if r["id"] == "erw-wb-natural-gas-europe-less-natural-gas-us")
        self.assertEqual((r["freq"], r["last"]["t"], r["last"]["v"], r["group"]), ("M", "2026-09-01", 10.0, "gasspreads"))

    def test_the_group_and_the_placeholders_words(self):
        ids = [g["id"] for g in self.bp.GROUPS]
        self.assertEqual(ids[ids.index("oilspreads") + 1], "gasspreads")
        self.assertIn("Spark Commodities", self.bp.NETBACK_NOTE)
        self.assertIn("Natural Gas Intelligence", self.bp.BASIS_NOTE)

    def test_the_page_writes_a_product_cracks_inputs(self):
        exe = shutil.which("node")
        if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        script = ("const b = await import('./lib/board.ts');"
                  "process.stdout.write(JSON.stringify(b.inputsWords({ inputs: { t: '2026-10-20', product: 2.4, crude: 70.5 } })));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), "Made of, on 20 Oct 2026: the product 2.40 USD/gal, crude 70.50 USD/bbl")


if __name__ == "__main__":
    unittest.main()
