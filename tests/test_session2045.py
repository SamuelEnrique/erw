"""Session 2045: NOAA's nClimDiv statewide monthly climate.

Energy Research Warehouse (ERW). Tests warehouse/connectors/noaa_climdiv_states.py on lines built here in nClimDiv's
fixed-width form (made up for the test, not NOAA's): a state's months and its 1901-2000 means, the latest year's
missing months omitted, Alaska and the regions not taken, the newest file of each name chosen from the listing; a line
not 94 characters, a missing mean and a missing value before the latest months stopping the run; the unit in in the
validator, the sector rule and the holds. No network.

    python -m unittest tests.test_session2045 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import noaa_climdiv_states as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402


def line(state, element, year, values):
    return f"{state:03d}0{element}{year}" + "".join(f"{v:7.2f}" for v in values)


TEMP = "\n".join([line(41, "02", "2025", [45.0 + m for m in range(12)]),
                  line(41, "02", "2026", [50.0] * 9 + [-99.90] * 3),
                  line(50, "02", "2025", [1.0] * 12), line(101, "02", "2025", [2.0] * 12)]).encode()
NORM_T = "\n".join([line(41, "02", "0031", [40.0 + m for m in range(12)]), line(41, "02", "0010", [0.0] * 12)]).encode()
PCPN = line(41, "01", "2025", [2.5] * 12).encode()
NORM_P = line(41, "01", "0031", [2.0] * 12).encode()
URLS, RET, VIN = {"tmpc": "u1", "pcpn": "u2"}, {"tmpc": "r", "pcpn": "r"}, {"tmpc": "v", "pcpn": "v"}


def data(temp=TEMP, norm_t=NORM_T):
    d = {"tmpc": N.records(temp, "02", "t"), "pcpn": N.records(PCPN, "01", "p")}
    n = {"tmpc": N.records(norm_t, "02", "nt"), "pcpn": N.records(NORM_P, "01", "np")}
    return d, n


class Build(unittest.TestCase):
    def test_rows(self):
        d, n = data()
        t = N.build(d, n, 2000, URLS, RET, VIN)
        self.assertEqual(set(t.entity), {"noaa_climdiv:041"})
        temp = t[t.variable == "temp_avg"].set_index("ts_utc")
        self.assertEqual(len(temp), 21)  # 12 of 2025 and 9 of 2026
        self.assertEqual((temp.loc["2025-03-01T00:00:00Z", "value"], temp.loc["2025-03-01T00:00:00Z", "x_mean_1901_2000"]), (47.0, 42.0))
        self.assertNotIn("2026-10-01T00:00:00Z", temp.index)
        p = t[t.variable == "precip"].iloc[0]
        self.assertEqual((p.unit, p.geo, p.node, p.x_mean_1901_2000), ("in", "US-TX", "Texas", 2.0))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            N.records(b"0410022025  45.00", "02", "short")
        d, n = data(norm_t=line(41, "02", "0010", [0.0] * 12).encode())
        with self.assertRaises(RuntimeError):
            N.build(d, n, 2000, URLS, RET, VIN)
        d, n = data(temp=line(41, "02", "2024", [-99.90] + [1.0] * 11).encode())
        d["tmpc"][(41, "2024")][0] = "-120.00"
        with self.assertRaises(RuntimeError):
            N.build(d, n, 2000, URLS, RET, VIN)

    def test_listing(self):
        html = "".join(f'<a href="climdiv-{k}-v1.0.0-{d}">x</a>' for k in ("tmpcst", "pcpnst", "norm-tmpcst", "norm-pcpnst")
                       for d in ("20260906", "20261006"))
        self.assertEqual(N.files(html)[("tmpc", False)], "climdiv-tmpcst-v1.0.0-20261006")
        self.assertEqual(N.files(html)[("pcpn", True)], "climdiv-norm-pcpnst-v1.0.0-20261006")


class Registered(unittest.TestCase):
    def test_unit_sector_and_holds(self):
        self.assertIn("in", V.UNITS)
        self.assertEqual(B.sector_of(N.NAME), "power;gas")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("60. **Session 2045: in.**", f.read())


if __name__ == "__main__":
    unittest.main()
