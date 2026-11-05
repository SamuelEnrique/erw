"""Session 1069 (chain 073): ERCOT's planned generation in a placed node's county (eia860m_planned_generators, public:
Texas, balancing authority ERCO), due in the twelve months after the table's vintage, nameplate MW and count by EIA's
status as the Headroom column counts them, on the node's panel, keyed allgrids|nodeplanned|<node>|construction|
approved|other and written whole. The builder's function is read on a small file written here; the tab's file holds
what the builder wrote. No request, no model call."""
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


PLANNED = ("# Energy Research Warehouse (ERW): EIA-860M planned generators, vintage 2026-08\n"
           "state,county,balancing_authority,eia_status,planned_operation_date,nameplate_mw\n"
           "TX,Fayette,ERCO,U,2026-09-01,100.5\n"
           "TX,Fayette,ERCO,T,2027-08-01,20\n"
           "TX,Fayette,ERCO,P,2027-09-01,999\n"         # after the twelve months
           "TX,Fayette,ERCO,P,2026-08-01,999\n"         # the vintage month itself, before them
           "TX,Fayette,SWPP,U,2026-10-01,999\n"         # not ERCOT
           "OK,Fayette,ERCO,U,2026-10-01,999\n"         # not Texas
           "TX,Harris,ERCO,L,2027-01-01,7\n")


class Builder(unittest.TestCase):
    def test_a_county_s_generators_by_status(self):
        m = load("siting_page_1069", "warehouse", "derived", "siting_page.py")
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "planned.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write(PLANNED)
            got = m.county_planned(p, {"FAYETTE", "HARRIS", "TRAVIS"})
        self.assertEqual((got["vintage"], got["from"], got["to"]), ("2026-08", "2026-09", "2027-08"))
        self.assertEqual(got["counties"]["FAYETTE"], {"construction_mw": 100.5, "construction_n": 1, "approved_mw": 20.0, "approved_n": 1,
                                                      "other_mw": 0.0, "other_n": 0})
        self.assertEqual((got["counties"]["HARRIS"]["other_mw"], got["counties"]["HARRIS"]["other_n"]), (7.0, 1))
        self.assertEqual(got["counties"]["TRAVIS"]["construction_n"], 0)        # none: zeros, said so on the panel


class TheFileAndThePage(unittest.TestCase):
    def test_the_tab_file_and_the_panel(self):
        n = json.loads(src("site", "data", "siting", "nodes.json"))
        pg = n["planned"]
        self.assertEqual(pg["table"], "eia860m_planned_generators")
        self.assertEqual(set(pg["counties"]), {k["county"] for k in n["nodes"] if "county" in k})
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn('data-node-planned="1"', v)
        self.assertIn("allgrids|nodeplanned|${id}|construction", v)
        self.assertNotIn("summing the planned generators by county for the panel is not built yet", v)
        self.assertIn('p[1] === "nodeplanned"', src("site", "lib", "siting.ts"))
        self.assertIn("(planned|nodeplanned|year|mwh|yeardiff|capratio)", src("site", "scripts", "check-values.mjs"))   # written whole


class TheReplication(unittest.TestCase):
    def test_counted_again_from_the_rows(self):
        m = load("repl_siting_1069", "warehouse", "replication", "siting.py")
        places = [{"entity_id": "ercot_node:X_ALL", "x_county": "FAYETTE"}]
        rows = [dict(zip(["state", "county", "balancing_authority", "eia_status", "planned_operation_date", "nameplate_mw"], ln.split(",")))
                for ln in PLANNED.strip().split("\n")[2:]]
        got = m.planned_figures(places, rows, "2026-08", node="X_ALL")
        self.assertEqual(got, {"allgrids|nodeplanned|ercot:X_ALL|construction": 100.5, "allgrids|nodeplanned|ercot:X_ALL|approved": 20.0,
                               "allgrids|nodeplanned|ercot:X_ALL|other": 0.0})
        self.assertEqual(m.planned_figures(places, rows, "2026-12", node="X_ALL")["allgrids|nodeplanned|ercot:X_ALL|approved"], 20.0)   # 2027-01 to 2027-12


if __name__ == "__main__":
    unittest.main()
