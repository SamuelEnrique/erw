"""Session 2120: the USGS's earthquake catalog for Oklahoma, Kansas, Texas and New Mexico.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usgs_earthquakes.py on an answer built here in the FDSN
service's CSV form (made up for the test, not the USGS's): the time to the second with the milliseconds kept, the place's
state read in full or from a postal code, a border region left blank; a header not the catalog's, an event given twice,
a time not the catalog's format, a magnitude below 2.5, an event that is not an earthquake and an answer at the service's
limit stopping the run; the query's address; the sector rule and the holds. No network.

    python -m unittest tests.test_session2120 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import usgs_earthquakes as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ("time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,"
        "magError,magNst,status,locationSource,magSource\n")
ROW = ('2016-09-03T12:02:44.430Z,36.43,-96.93,5.6,5.8,mww,,20,,0.6,us,us10006jxs,2026-01-01T00:00:00.000Z,'
       '"14 km NW of Pawnee, Oklahoma",earthquake,1.7,1.9,0.04,,reviewed,us,us\n')


def row(**kw):
    r = ROW
    for k, v in kw.items():
        r = r.replace(k, v)
    return r


class Build(unittest.TestCase):
    def test_rows(self):
        t = U.build(HEAD + ROW + row(us10006jxs="ok2014abc", **{"14 km NW of Pawnee, Oklahoma": "2 km E of Choctaw, OK",
                                                                 "2016-09-03T12:02:44.430Z": "2014-01-01T00:00:01.000Z"})
                    + row(us10006jxs="tx2020xyz", **{"14 km NW of Pawnee, Oklahoma": "Texas-Chihuahua border region",
                                                      "2016-09-03T12:02:44.430Z": "2020-05-05T05:05:05.500Z"}), "u", "r")
        a = t[t.event_id == "usgs_comcat:us10006jxs"].iloc[0]
        self.assertEqual((a.event_date, a.x_time_utc, a.event_type, a.status), ("2016-09-03T12:02:44Z", "2016-09-03T12:02:44.430Z", "earthquake", "reviewed"))
        self.assertEqual((a.x_magnitude, a.x_magnitude_type, a.x_depth_km, a.x_place_state), ("5.8", "mww", "5.6", "Oklahoma"))
        self.assertEqual(t[t.event_id == "usgs_comcat:ok2014abc"].iloc[0].x_place_state, "Oklahoma")
        self.assertEqual(t[t.event_id == "usgs_comcat:tx2020xyz"].iloc[0].x_place_state, "")
        self.assertEqual(list(t.event_id), ["usgs_comcat:ok2014abc", "usgs_comcat:us10006jxs", "usgs_comcat:tx2020xyz"])

    def test_place_state(self):
        self.assertEqual(U.place_state("western Texas"), "Texas")
        self.assertEqual(U.place_state("New Mexico"), "New Mexico")
        self.assertEqual(U.place_state("19 km WSW of Naica, Mexico"), "Mexico")
        self.assertEqual(U.place_state("2024 North of Tarzan, Texas Earthquake"), "")

    def test_stops(self):
        for bad in (HEAD.replace("magSource", "magSrc") + ROW, HEAD + ROW + ROW, HEAD + row(**{"T12:02:44.430Z": " 12:02"}),
                    HEAD + row(**{",5.8,mww": ",2.4,mww"}), HEAD + row(earthquake="quarry blast")):
            with self.assertRaises(RuntimeError):
                U.build(bad, "u", "r")
        limit, U.LIMIT = U.LIMIT, 1
        try:
            with self.assertRaises(RuntimeError):
                U.build(HEAD + ROW, "u", "r")
        finally:
            U.LIMIT = limit

    def test_query(self):
        u = U.query_url("2026-10-23")
        for part in ("format=csv", "eventtype=earthquake", "starttime=2010-01-01", "endtime=2026-10-23", "minmagnitude=2.5",
                     "minlatitude=25.8", "maxlatitude=40.0", "minlongitude=-109.06", "maxlongitude=-93.5"):
            self.assertIn(part, u)
        self.assertTrue(u.startswith("https://earthquake.usgs.gov/fdsnws/event/1/query?"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.NAME), "oil;gas")
        self.assertIn(U.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
