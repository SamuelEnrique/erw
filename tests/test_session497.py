"""Session 497: EIA's State Energy Data System. Units into the standard's vocabulary (billion Btu as TBtu, million
dollars as USD, dollars per million Btu as USD/MMBtu); the U.S. row's geo US, a state's US-<state>; an unknown unit or a
repeated key stops the run; a withheld value has no row."""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_seds as es  # noqa: E402


def api(sid, state, period, value, unit):
    return dict(seriesId=sid, stateId=state, period=period, value=value, unit=unit, seriesDescription=sid)


class Seds(unittest.TestCase):
    def test_units_and_geo(self):
        t = es.rows([api("ESTCB", "US", "2024", "13563828", "Billion Btu"), api("ESTCV", "TX", "2024", "41000.5", "Million Dollars"),
                     api("ESRCD", "CA", "2024", "88.1", "Dollars per Million Btu")], "u", "r")
        got = list(zip(t["entity"], t["unit"], t["value"].round(3), t["geo"]))
        self.assertEqual(got, [("eia_seds:ESTCB:US", "TBtu", 13563.828, "US"), ("eia_seds:ESTCV:TX", "USD", 41000500000.0, "US-TX"),
                               ("eia_seds:ESRCD:CA", "USD/MMBtu", 88.1, "US-CA")])

    def test_an_unknown_unit_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "not in the map"):
            es.rows([api("CLTCP", "US", "2024", "1.0", "Thousand Short Tons")], "u", "r")

    def test_a_withheld_value_has_no_row_and_a_repeat_stops_the_run(self):
        self.assertEqual(len(es.rows([api("ESTCB", "US", "2024", None, "Billion Btu")], "u", "r")), 0)
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            es.rows([api("ESTCB", "US", "2024", "1", "Billion Btu")] * 2, "u", "r")


if __name__ == "__main__":
    unittest.main()
