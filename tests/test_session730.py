"""Session 730 (chain 062): the large-load tariff charge, written against the documented shape of
utility_large_load_tariffs (warehouse/connectors/openei_large_load_tariffs.py, session 670 of chain 043) on a fixture,
since the table has not landed (coverage.csv holds no such name): not wired to a column, no key drawn, the gaps file's
rows 1 to 6 stand. The newest rate in force whose minimum demand the load meets; the demand and fixed charges spread over
the MWh the load uses in a year, plus the energy charge; a licensed rate is "license needed". No request, no model call,
no database read."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


# the fixture, in the connector's documented form: entity openei_urdb:<rate label>, ts_utc the start date, the variables
# energy_charge (USD/MWh), demand_charge (USD/kW-month), fixed_charge (USD a month), min_demand_mw; x_ the utility
def rate(label, start, eia, utility, energy, demand, fixed, min_mw, end=None, license="public"):
    base = {"entity": f"openei_urdb:{label}", "ts_utc": f"{start}T00:00:00Z", "node": f"Rate {label}", "x_eia_id": eia, "x_utility": utility,
            "x_sector": "Industrial", "x_uri": f"https://openei.org/apps/USURDB/rate/view/{label}", "x_end_date": end, "x_license": license}
    rows = []
    for v, val, unit in (("energy_charge", energy, "USD/MWh"), ("demand_charge", demand, "USD/kW-month"), ("fixed_charge", fixed, "USD"), ("min_demand_mw", min_mw, "MW")):
        if val is not None:
            rows.append({**base, "variable": v, "value": val, "unit": unit})
    return rows


FIXTURE = (
    rate("aaa1", "2024-01-01", "14328", "Pacific Gas & Electric Co", 60.0, 20.0, 500.0, 1.0)              # older rate of the same utility
    + rate("aaa2", "2025-06-01", "14328", "Pacific Gas & Electric Co", 55.0, 25.0, 600.0, 1.0)            # the newest in force
    + rate("aaa3", "2026-01-01", "14328", "Pacific Gas & Electric Co", 50.0, 30.0, 0.0, 500.0)            # minimum demand 500 MW: a 100 MW load does not meet it
    + rate("aaa4", "2026-09-01", "14328", "Pacific Gas & Electric Co", 40.0, 10.0, 0.0, 1.0, end="2026-10-01")   # ended before today
    + rate("bbb1", "2025-01-01", "4226", "Consolidated Edison Co-NY Inc", 30.0, 15.0, 100.0, 1.0, license="internal")  # held
    + rate("ccc1", "2025-01-01", "99999", "A Utility With Energy Only", 45.0, None, None, None)
)

SCRIPT = """
const S = await import('./lib/siting.ts');
const rows = %s;
const x = { mw: 100, lf: 0.9, hoursYear: 8760 };
const out = {
  pge: S.largeLoadTariff(rows, '14328', x, '2026-10-22'),
  pgeBig: S.largeLoadTariff(rows, '14328', { mw: 600, lf: 0.9, hoursYear: 8760 }, '2026-10-22'),
  pgeEarly: S.largeLoadTariff(rows, '14328', x, '2025-01-15'),
  coned: S.largeLoadTariff(rows, '4226', x, '2026-10-22'),
  energyOnly: S.largeLoadTariff(rows, '99999', x, '2026-10-22'),
  none: S.largeLoadTariff(rows, '1', x, '2026-10-22'),
  flexible: S.largeLoadTariff(rows, '14328', { mw: 100, lf: 0.9, hoursYear: 8546 }, '2026-10-22'),
};
process.stdout.write(JSON.stringify(out));
""" % json.dumps(FIXTURE)


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and ("Unknown file extension" in r.stderr or "strip" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


class TheCharge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_the_newest_rate_in_force_that_the_load_meets(self):
        p = self.o["pge"]
        self.assertEqual(p["rate"], "Rate aaa2")          # not aaa3 (500 MW minimum), not aaa4 (ended), not aaa1 (older)
        self.assertEqual(p["effective"], "2025-06-01")
        self.assertIsNone(p["end"])
        self.assertEqual(p["minMw"], 1.0)
        # a 600 MW load meets aaa3's minimum, the newest in force
        self.assertEqual(self.o["pgeBig"]["rate"], "Rate aaa3")
        # on 15 January 2025 only aaa1 was in force
        self.assertEqual(self.o["pgeEarly"]["rate"], "Rate aaa1")

    def test_the_arithmetic_by_the_tariffs_terms(self):
        p = self.o["pge"]
        mwh = 100 * 0.9 * 8760
        self.assertAlmostEqual(p["mwhYear"], mwh)
        self.assertAlmostEqual(p["demand"], 25.0 * 1000 * 100 * 12 / mwh, places=9)   # USD per kW-month, the full size, twelve months, over the year's MWh
        self.assertAlmostEqual(p["fixed"], 600.0 * 12 / mwh, places=9)
        self.assertAlmostEqual(p["energy"], 55.0)
        self.assertAlmostEqual(p["per"], p["demand"] + p["fixed"] + p["energy"], places=9)
        self.assertAlmostEqual(p["per"], 55.0 + 38.0517503805 + 0.00913242, places=6)
        # a load that runs fewer hours spreads the same demand charge over fewer MWh: more per MWh
        self.assertGreater(self.o["flexible"]["demand"], p["demand"])

    def test_held_energy_only_and_none(self):
        self.assertEqual(self.o["coned"]["words"], "license needed")
        self.assertIn("internal", self.o["coned"]["why"])
        e = self.o["energyOnly"]
        self.assertEqual((e["demand"], e["fixed"], e["energy"], e["per"]), (0, 0, 45.0, 45.0))
        self.assertEqual(self.o["none"]["words"], "not held")


class NotWired(unittest.TestCase):
    def test_no_column_reads_it_and_no_key_is_drawn(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertNotIn("largeLoadTariff", v)
        s = src("site", "lib", "siting.ts")
        self.assertIn("export function largeLoadTariff", s)
        self.assertNotIn("allgrids|tariff", s)
        self.assertNotIn("utility_large_load_tariffs", src("site", "lib", "sitingdata.ts"))
        cov = src("warehouse", "metadata", "coverage.csv")
        self.assertNotIn("utility_large_load_tariffs,", cov)      # the day it lands, 740 or a later session wires it
        self.assertIn("| CAISO | Transmission and 4CP |", src("docs", "reviews", "siting-gaps.md"))

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), src("site", "lib", "siting.ts"))


if __name__ == "__main__":
    unittest.main()
