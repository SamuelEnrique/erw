"""Session 909: every country's electricity from EIA's International Energy Statistics bulk file.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_intl_bulk.py on a bulk file built here in EIA's form
(figures made up for the test, not EIA's): only annual billion kWh and million kW series taken, as MWh and MW; a country's
name read from its series' names (a comma inside a name kept); EIA's marks having no row; areas sorted into country,
former, part and region; a product or activity not in the map stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session909 -v
"""

import io
import json
import os
import sys
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_intl_bulk as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def ser(sid, name, data):
    return {"series_id": sid, "name": name, "units": "", "f": sid[-1], "data": data}


def bulk(series):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        lines = [json.dumps({"category_id": "1", "name": "Electricity", "childseries": []})] + [json.dumps(s) for s in series]
        z.writestr("INTL.txt", "\n".join(lines) + "\n")
    return buf.getvalue()


SERIES = [
    ser("INTL.2-12-GMB-BKWH.A", "Electricity net generation, Gambia, The, Annual", [["2024", 0.5], ["2023", "NA"]]),
    ser("INTL.37-7-GMB-MK.A", "Wind electricity installed capacity, Gambia, The, Annual", [["2024", 0.002], ["2023", "--"]]),
    ser("INTL.2-2-GMB-QBTU.A", "Electricity net consumption, Gambia, The, Annual", [["2024", 1.0]]),
    ser("INTL.2-12-WORL-BKWH.A", "Electricity net generation, World, Annual", [["2024", 30000]]),
    ser("INTL.2-3-WORL-BKWH.A", "Electricity imports, World, Annual", [["2024", "ie"]]),
    ser("INTL.2-12-SUN-BKWH.A", "Electricity net generation, Former U.S.S.R., Annual", [["1990", 1700]]),
    ser("INTL.2-4-SUN-BKWH.A", "Electricity exports, Former U.S.S.R., Annual", [["1990", 30]]),
    ser("INTL.2-12-GMB-BKWH.M", "Electricity net generation, Gambia, The, Monthly", [["202401", 0.04]]),
]


class Bulk(unittest.TestCase):
    def test_units_names_and_kinds(self):
        t, n = E.rows(E.read_series(bulk(SERIES)), "u", "r", "v")
        self.assertEqual(n, 6)
        g = t.set_index(["entity", "variable"])
        self.assertEqual((g.loc[("eia_intl:GMB:2", "generation"), "value"], g.loc[("eia_intl:GMB:2", "generation"), "unit"]), (0.5e6, "MWh"))
        self.assertEqual((g.loc[("eia_intl:GMB:37", "capacity"), "value"], g.loc[("eia_intl:GMB:37", "capacity"), "unit"]), (2.0, "MW"))
        self.assertEqual(g.loc[("eia_intl:GMB:37", "capacity"), "node"], "Gambia, The, Wind")
        self.assertEqual(g.loc[("eia_intl:WORL:2", "generation"), "x_area"], "region")
        self.assertEqual(g.loc[("eia_intl:SUN:2", "exports"), "x_area"], "former")
        self.assertEqual(g.loc[("eia_intl:GMB:2", "generation"), "x_area"], "country")
        self.assertEqual(set(t.geo), {""})
        self.assertEqual(len(t), 5)  # the marks NA, -- and ie, the Btu copy and the monthly series have no row

    def test_not_in_the_map_stops(self):
        for bad in (ser("INTL.99-12-GMB-BKWH.A", "X net generation, Gambia, The, Annual", [["2024", 1]]),
                    ser("INTL.2-77-GMB-BKWH.A", "Electricity something, Gambia, The, Annual", [["2024", 1]])):
            with self.assertRaises(RuntimeError):
                E.rows(E.read_series(bulk(SERIES + [bad])), "u", "r", "v")

    def test_one_name_is_not_enough(self):
        with self.assertRaises(RuntimeError):
            E.rows(E.read_series(bulk([ser("INTL.2-12-ABC-BKWH.A", "Electricity net generation, Abc, Annual", [["2024", 1]])])), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_world_electricity_annual"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
