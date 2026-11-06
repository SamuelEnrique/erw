"""Session 2923 (chain 153): the All grids tab wired to two held tables.

- Headroom: each grid's generation with a signed interconnection agreement and no operation date
  (interconnection_agreements_by_grid, public), in headroom.json's "signed", drawn as "<MW> MW signed", keyed
  allgrids|signed|<row> and written whole.
- Utility: a county row's delivery-only company (eia861_delivery_only, public: CenterPoint in Harris County, Oncor in
  Travis), in utility.json's county "delivery", drawn as "wires USD <x> <company>", keyed allgrids|wiresrev|<row>.

The builder's two functions are read on small files written here; the tab's files hold what they give from the
warehouse; the replication counts both again from the tables' rows. No figure the tab drew before moves: the two keys
were added to the committed files, nothing else of them rewritten. No request, no model call.
"""
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SIGNED = ("# Energy Research Warehouse (ERW): generation with a signed interconnection agreement by grid\n"
          "entity,variable,ts_utc,value,unit\n"
          "interconnection_agreements:ercot,mw_signed,2025-01-01T00:00:00Z,100.25,MW\n"
          "interconnection_agreements:ercot,projects_signed,2025-01-01T00:00:00Z,3,count\n"
          "interconnection_agreements:ercot,active_mw,2025-01-01T00:00:00Z,400,MW\n"
          "interconnection_agreements:ercot,active_projects,2025-01-01T00:00:00Z,9,count\n"
          "interconnection_agreements:ercot,signed_share_pct,2025-01-01T00:00:00Z,25.06,pct\n"
          "interconnection_agreements:ercot,mw_signed,2024-01-01T00:00:00Z,999,MW\n"                 # not the queue's end
          "interconnection_agreements:ercot:solar,mw_signed,2025-01-01T00:00:00Z,999,MW\n"           # a fuel's row
          "interconnection_agreements:iso_ne,mw_signed,2025-01-01T00:00:00Z,5,MW\n"                  # isone, incomplete
          "interconnection_agreements:west,mw_signed,2025-01-01T00:00:00Z,999,MW\n")                 # not a tab grid

DELIVERY = ("# Energy Research Warehouse (ERW): EIA-861 delivery-only companies\n"
            "variable,ts_utc,value,node,x_utility_number,x_state,x_ba_code\n"
            "industrial_sales,2025-01-01T00:00:00Z,1000,Wires Co,8901,TX,ERCO\n"
            "industrial_revenue,2025-01-01T00:00:00Z,12000,Wires Co,8901,TX,ERCO\n"
            "industrial_sales,2024-01-01T00:00:00Z,9,Wires Co,8901,TX,ERCO\n"                        # an older year
            "industrial_revenue,2024-01-01T00:00:00Z,9,Wires Co,8901,TX,ERCO\n"
            "industrial_sales,2025-01-01T00:00:00Z,500,Other Wires,7777,TX,ERCO\n"                   # not in the county
            "industrial_revenue,2025-01-01T00:00:00Z,500,Other Wires,7777,TX,ERCO\n")

COUNTY = {"ercot:HB_HOUSTON": {"state": "TX", "county": "Harris", "ba": "ERCO", "utilities": [{"name": "Wires Co", "number": "8901", "ba": []}, {"name": "A Coop", "number": "1", "ba": ["ERCO"]}]},
          "ercot:LZ_CPS": {"state": "TX", "county": "Bexar", "ba": "ERCO", "utilities": [{"name": "A Coop", "number": "1", "ba": ["ERCO"]}]}}


class Builder(unittest.TestCase):
    def setUp(self):
        self.m = load("siting_page_2923", "warehouse", "derived", "siting_page.py")

    def test_signed_by_grid(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write(SIGNED)
            got = self.m.signed_by_grid(p)
        self.assertEqual((got["table"], got["queue_end"]), ("interconnection_agreements_by_grid", "2025-01-01"))
        self.assertEqual(got["grids"], {"ercot": {"mw_signed": 100.2, "projects_signed": 3, "active_mw": 400.0, "active_projects": 9, "signed_share_pct": 25.06}})

    def test_county_delivery(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "d.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write(DELIVERY)
            got = self.m.county_delivery(p, COUNTY)
        self.assertEqual(set(got), {"ercot:HB_HOUSTON"})          # Bexar has no delivery-only company: no key
        self.assertEqual(got["ercot:HB_HOUSTON"], {"table": "eia861_delivery_only", "year": 2025,
                                                   "companies": [{"utility": "Wires Co", "number": "8901", "sales_mwh": 1000.0, "revenue_usd": 12000.0}]})


class TheFilesAndThePage(unittest.TestCase):
    def test_the_tab_files(self):
        h = json.loads(src("site", "data", "siting", "headroom.json"))
        self.assertEqual(h["signed"]["table"], "interconnection_agreements_by_grid")
        self.assertEqual(set(h["signed"]["grids"]), {"ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"})
        self.assertEqual(h["signed"]["grids"]["ercot"]["mw_signed"], 132566.1)   # Queued Up, the queue at the end of 2025
        u = json.loads(src("site", "data", "siting", "utility.json"))
        dl = u["county"]["ercot:HB_HOUSTON"]["delivery"]
        self.assertEqual((dl["table"], dl["year"], dl["companies"][0]["utility"], dl["companies"][0]["number"]), ("eia861_delivery_only", 2025, "CenterPoint Energy", "8901"))
        self.assertAlmostEqual(dl["companies"][0]["revenue_usd"] / dl["companies"][0]["sales_mwh"], 10.5685, places=4)
        # the county's top seller, the figure the cell drew before, is unchanged
        self.assertEqual(u["county"]["ercot:HB_HOUSTON"]["top"]["number"], "16638")

    def test_the_page_draws_and_keys_them(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("allgrids|signed|${r.id}", v)
        self.assertIn("allgrids|wiresrev|${r.id}", v)
        self.assertIn('data-headroom-signed=', v)
        self.assertIn('data-util-wires="1"', v)
        s = src("site", "lib", "siting.ts")
        self.assertIn('p[1] === "signed"', s)
        self.assertIn('p[1] === "wiresrev"', s)
        self.assertIn(r"(^allgrids\|signed\|)", src("site", "scripts", "check-values.mjs"))   # written whole


class TheReplication(unittest.TestCase):
    def test_counted_again_from_the_rows(self):
        m = load("repl_siting_2923", "warehouse", "replication", "siting.py")
        rows = [dict(zip(["entity", "variable", "ts_utc", "value", "unit"], ln.split(","))) for ln in SIGNED.strip().split("\n")[2:]]
        self.assertEqual(m.signed_figures(rows, ["ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND"]), {"allgrids|signed|ercot:HB_HUBAVG": 100.2})
        drows = [dict(zip(["variable", "ts_utc", "value", "node", "x_utility_number", "x_state", "x_ba_code"], ln.split(","))) for ln in DELIVERY.strip().split("\n")[2:]]
        got = m.wires_figures(drows, {"county": COUNTY})
        self.assertEqual(got, {"allgrids|wiresrev|ercot:HB_HOUSTON": 12.0})


if __name__ == "__main__":
    unittest.main()
