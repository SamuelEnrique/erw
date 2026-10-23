"""Session 2042: NOAA's Storm Events Database.

Energy Research Warehouse (ERW). Tests warehouse/connectors/noaa_storm_events.py on rows built here in NCEI's form
(made up for the test, not NCEI's): the local standard time turned to UTC by the zone's own offset, the damage figures in
dollars, the types kept and dropped, the newest file of a year chosen from the listing; a heading not in the map, a zone
or damage figure not in NCEI's form and an event given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2042 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import noaa_storm_events as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEADINGS = sorted(S.USED) + list(S.FIELDS) + sorted(S.NOT_TAKEN)


def row(eid, etype="Ice Storm", zone="CST-6", ym="202102", d="15", hm="2330", prop="1.50M", fips="48", **kw):
    r = {h: "" for h in HEADINGS}
    r.update(EVENT_ID=eid, EVENT_TYPE=etype, CZ_TIMEZONE=zone, BEGIN_YEARMONTH=ym, BEGIN_DAY=d, BEGIN_TIME=hm,
             END_YEARMONTH=ym, END_DAY=d, END_TIME="2359", DAMAGE_PROPERTY=prop, DAMAGE_CROPS="0.00K", STATE_FIPS=fips,
             STATE="TEXAS", CZ_TYPE="Z", CZ_FIPS="123", EPISODE_ID="9")
    r.update(kw)
    return r


def frame(*rows):
    return pd.DataFrame(list(rows), columns=HEADINGS)


class Build(unittest.TestCase):
    def test_rows(self):
        t = S.build([(frame(row("1"), row("2", etype="Hail"), row("3", etype="Hurricane (Typhoon)", zone="EST-5", hm="5",
                                                                          prop="", fips="12")), "u", "r", "20260918")])
        self.assertEqual(list(t.event_id), ["noaa_storm:3", "noaa_storm:1"])  # sorted by the UTC time
        a = t.set_index("event_id").loc["noaa_storm:1"]
        self.assertEqual((a.event_date, a.x_begin_local, a.event_type), ("2021-02-16T05:30:00Z", "2021-02-15T23:30:00", "ice_storm"))
        self.assertEqual((a.x_damage_property_usd, a.x_damage_crops_usd, a.x_geo), ("1500000", "0", "US-TX"))
        self.assertEqual(a.x_file_created, "2026-09-18")
        b = t.set_index("event_id").loc["noaa_storm:3"]
        self.assertEqual((b.event_date, b.event_type, b.x_damage_property_usd, b.x_geo),
                         ("2021-02-15T05:05:00Z", "hurricane_typhoon", "", "US-FL"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            S.build([(frame(row("1"), row("1")), "u", "r", "20260918")])
        with self.assertRaises(RuntimeError):
            S.build([(frame(row("1", zone="Central")), "u", "r", "20260918")])
        with self.assertRaises(RuntimeError):
            S.build([(frame(row("1", prop="lots")), "u", "r", "20260918")])
        f = frame(row("1"))
        f["NEW_HEADING"] = ""
        with self.assertRaises(RuntimeError):
            S.build([(f, "u", "r", "20260918")])

    def test_territories_and_daylight_zones(self):
        # session 2052: NCEI codes the territories 96 to 99, not by FIPS; a row may name a daylight zone
        t = S.build([(frame(row("5", fips="99", zone="AST-4"), row("6", fips="98", zone="GST10"), row("7", zone="PDT-7"),
                            row("8", fips="72")), "u", "r", "20260918")]).set_index("event_id")
        self.assertEqual(t.loc["noaa_storm:5"].x_geo, "US-PR")
        self.assertEqual((t.loc["noaa_storm:6"].x_geo, t.loc["noaa_storm:6"].event_date), ("US-GU", "2021-02-15T13:30:00Z"))
        self.assertEqual(t.loc["noaa_storm:7"].event_date, "2021-02-16T06:30:00Z")
        self.assertEqual(t.loc["noaa_storm:8"].x_geo, "")  # 72 is not NCEI's code for Puerto Rico

    def test_damage_and_listing(self):
        self.assertEqual([S.damage(v) for v in ("10.00K", "2B", "K", "0", "")], ["10000", "2000000000", "0", "0", ""])
        html = ('<a href="StormEvents_details-ftp_v1.0_d2024_c20260323.csv.gz">x</a>'
                '<a href="StormEvents_details-ftp_v1.0_d2024_c20260728.csv.gz">x</a>'
                '<a href="StormEvents_fatalities-ftp_v1.0_d2024_c20260728.csv.gz">x</a>')
        self.assertEqual(S.listing(html), {2024: ("StormEvents_details-ftp_v1.0_d2024_c20260728.csv.gz", "20260728")})
        with self.assertRaises(RuntimeError):
            S.listing("<html></html>")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        self.assertIn(S.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
