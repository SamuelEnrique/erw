"""Session 730 (chain 062): large-load tariffs, written and not wired. utility_large_load_tariffs (the data machine's,
warehouse/connectors/openei_large_load_tariffs.py) had not landed, so the builder's step (siting_page.tariffs_file)
and the tab's functions (lib/siting.ts, tariffFor and tariffParts) are tested on a fixture in the connector's
documented shape. No request, no model call."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))

FIXTURE = """# Energy Research Warehouse (ERW): fixture for tests/test_session730.py, in the shape of utility_large_load_tariffs
entity,variable,ts_utc,value,unit,freq,geo,node,x_eia_id,x_utility,x_sector,x_uri,x_end_date
openei_urdb:a1,energy_charge,2024-01-01T00:00:00Z,61.5,USD/MWh,,US-TX,Large Power A,1,Fixture Power Co,Industrial,u1,
openei_urdb:a1,demand_charge,2024-01-01T00:00:00Z,12.0,USD/kW-month,,US-TX,Large Power A,1,Fixture Power Co,Industrial,u1,
openei_urdb:a1,fixed_charge,2024-01-01T00:00:00Z,730,USD,,US-TX,Large Power A,1,Fixture Power Co,Industrial,u1,
openei_urdb:a1,min_demand_mw,2024-01-01T00:00:00Z,1,MW,,US-TX,Large Power A,1,Fixture Power Co,Industrial,u1,
openei_urdb:a2,energy_charge,2025-06-01T00:00:00Z,58.0,USD/MWh,,US-TX,Large Power B,1,Fixture Power Co,Industrial,u2,
openei_urdb:a2,demand_charge,2025-06-01T00:00:00Z,15.0,USD/kW-month,,US-TX,Large Power B,1,Fixture Power Co,Industrial,u2,
openei_urdb:a2,min_demand_mw,2025-06-01T00:00:00Z,50,MW,,US-TX,Large Power B,1,Fixture Power Co,Industrial,u2,
"""

SCRIPT = """
const S = await import('./lib/siting.ts');
const rates = JSON.parse(process.argv[1]);
const small = S.tariffFor(rates, 10), big = S.tariffFor(rates, 100), none = S.tariffFor([], 100);
process.stdout.write(JSON.stringify({ small: small && small.rate, big: big && big.rate, none, parts: S.tariffParts(small, 10, 1.0), half: S.tariffParts(small, 10, 0.5) }));
"""


class Tariffs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import siting_page
        d = tempfile.mkdtemp()
        p = os.path.join(d, "utility_large_load_tariffs.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        cls.f = siting_page.tariffs_file(p)
        shutil.rmtree(d)

    def test_the_builder_keeps_each_rate_by_utility_newest_first(self):
        r = self.f["utilities"]["1"]
        self.assertEqual([x["rate"] for x in r], ["openei_urdb:a2", "openei_urdb:a1"])
        self.assertEqual((r[1]["energy"], r[1]["demand"], r[1]["fixed"], r[1]["min_mw"]), (61.5, 12.0, 730.0, 1.0))
        self.assertIsNone(r[0]["fixed"])                           # a2 states no fixed charge: none, not zero

    def test_the_tab_takes_the_newest_rate_open_to_the_load_and_spreads_the_demand_charge(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        out = subprocess.run([exe, "--input-type=module", "-e", SCRIPT, json.dumps(self.f["utilities"]["1"])], cwd=SITE,
                             capture_output=True, text=True, timeout=300, encoding="utf-8")
        if out.returncode != 0:
            raise AssertionError(out.stderr)
        o = json.loads(out.stdout)
        self.assertEqual(o["small"], "openei_urdb:a1")             # a 10 MW load is under a2's 50 MW minimum
        self.assertEqual(o["big"], "openei_urdb:a2")
        self.assertIsNone(o["none"])
        # 12 USD/kW-month on 10 MW over 10 x 1.0 x 730 MWh: 12,000 x 10 / 7,300 = 16.438...; fixed 730 / 7,300 = 0.1
        self.assertAlmostEqual(o["parts"]["demand"], 12 * 10 * 1000 / 7300, places=6)
        self.assertAlmostEqual(o["parts"]["fixed"], 0.1, places=6)
        self.assertAlmostEqual(o["parts"]["wires"], 12 * 10 * 1000 / 7300 + 0.1, places=6)
        self.assertAlmostEqual(o["half"]["demand"], 2 * o["parts"]["demand"], places=6)   # half the hours, twice per MWh
        self.assertEqual(o["parts"]["energy"], 61.5)

    def test_it_is_not_wired(self):
        self.assertNotIn("tariffs.json", open(os.path.join(SITE, "lib", "sitingdata.ts"), encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
