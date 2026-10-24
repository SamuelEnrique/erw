"""Session 2149: NRCS SNOTEL's daily snow water equivalent.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nrcs_snotel.py on answers built here in the AWDB service's
form (figures made up for the test, not NRCS's): the stations' metadata kept, a day with no value left out and counted,
inches; an answer missing a station, a unit other than inches and a day given twice each stopping the run; the encoded
commas of the addresses; the sector rule and the holds (internal: not in the release's storage hold). No network.

    python -m unittest tests.test_session2149 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nrcs_snotel as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
META = {t: {"stationTriplet": t, "name": f"Station {t}", "huc": "140100010101", "elevation": 11000.0, "latitude": 39.0, "longitude": -106.0}
        for b in N.BASINS.values() for t in b}


def answer(basin, unit="in", values=None, drop=None):
    out = []
    for t in N.BASINS[basin]:
        if t == drop:
            continue
        vals = values if values is not None else [{"date": "2024-04-01", "value": 20.5}, {"date": "2024-04-02"}]
        out.append({"stationTriplet": t, "data": [{"stationElement": {"elementCode": "WTEQ", "storedUnitCode": unit}, "values": vals}]})
    return out


class Parse(unittest.TestCase):
    def test_answer(self):
        missing, absent = {}, {}
        rows = N.parse(answer("california", values=[{"date": "2024-04-01", "value": 20.5}, {"date": "2024-04-02"},
                                                   {"date": "2024-04-04", "value": 19.0}]), "california", META, BASE, missing, absent)
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(missing.values()), 4)
        self.assertEqual(sum(absent.values()), 4)  # 3 April has no entry at any of the four stations (session 2157)
        r = rows[0]
        self.assertEqual((r["entity"], r["ts_utc"], r["value"], r["unit"], r["geo"], r["x_basin"], r["x_elevation_ft"]),
                         ("snotel:1067:ca", "2024-04-01T00:00:00Z", 20.5, "in", "US-CA", "california", 11000.0))

    def test_stops(self):
        for kw, words in [(dict(drop="356:CA:SNTL"), "not the stations asked"), (dict(unit="mm"), "not inches"),
                          (dict(values=[{"date": "2024-04-01", "value": 1}, {"date": "2024-04-01", "value": 2}]), "given twice")]:
            with self.assertRaises(RuntimeError) as c:
                N.parse(answer("california", **kw), "california", META, BASE, {}, {})
            self.assertIn(words, str(c.exception))
        with self.assertRaises(RuntimeError):
            N.parse_meta(list(META.values())[:-1])

    def test_addresses(self):
        u = N.data_url(N.BASINS["california"], "2026-10-23")
        self.assertIn("stationTriplets=1067:CA:SNTL%2C391:CA:SNTL%2C428:CA:SNTL%2C356:CA:SNTL&elements=WTEQ", u)
        self.assertNotIn(",", u)
        self.assertEqual(sum(len(b) for b in N.BASINS.values()), 20)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.TABLE), "power")
        self.assertNotIn(N.TABLE, R.STORAGE_HELD)  # internal until its license is settled
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
