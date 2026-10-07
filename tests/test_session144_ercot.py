"""Session 144: ERCOT wind and solar by the hour (warehouse/connectors/ercot_wind_solar_history.py). The parsers on
small saved real samples of each report (tests/fixtures/session144/ercot/: two postings each of NP4-742-CD and
NP4-745-CD as ERCOT served them, and the rows of 8 to 10 March and 1 to 3 November 2025 of the 2025 yearly workbook,
a 23-hour and a 25-hour day); the monthly sums against the daily sums of the same hours; the share; the 95 percent
rule; the ceiling stop; the pause. No request is made: every test that could reach the network replaces the request
with a function that fails the test."""
import glob
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_wind_solar_history as c  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session144", "ercot")
WIND_OLD = "14787_cdr.00014787.0000000000000000.20260930.005513154.WPPHRLYAVGACTGEONP4742_csv.zip"
WIND_NEW = "14787_cdr.00014787.0000000000000000.20260930.235512549.WPPHRLYAVGACTGEONP4742_csv.zip"
SOLAR_OLD = "21809_cdr.00021809.0000000000000000.20260930.005512599.PVGRHRLYAVGACTGEONP4745_csv.zip"
SOLAR_NEW = "21809_cdr.00021809.0000000000000000.20260930.235512454.PVGRHRLYAVGACTGEONP4745_csv.zip"
WORKBOOK = "ERCOT_2025_Hourly_WindSolar_Output_sample.xlsx"


def body(name):
    with open(os.path.join(FIX, name), "rb") as f:
        return f.read()


def hourly_table():
    """The four sample postings as the hourly table's rows, the newest posting winning, as --write builds them."""
    best = {}
    for name, fuel in ((WIND_OLD, "wind"), (WIND_NEW, "wind"), (SOLAR_OLD, "solar"), (SOLAR_NEW, "solar")):
        d, _ = c.parse_posting(body(name), fuel)
        for ts, entity, variable, value in d.itertuples(index=False):
            best[(entity, variable, ts)] = value
    rows = pd.DataFrame([(ts, e, v, x, "https://www.ercot.com/x", "2026-10-07T09:32:00Z") for (e, v, ts), x in best.items()],
                        columns=["ts", "entity", "variable", "value", "url", "retrieved"])
    return c.series(rows, c.SRC_REGION, c.region_of)


class Fixtures(unittest.TestCase):
    def test_samples_are_small(self):
        total = sum(os.path.getsize(p) for p in glob.glob(os.path.join(FIX, "*")))
        self.assertLess(total, 300_000)


class Postings(unittest.TestCase):
    def test_wind_posting_as_ercot_prints_it(self):
        d, n_file = c.parse_posting(body(WIND_OLD), "wind")
        self.assertEqual(n_file, 216)  # 48 hours behind and 168 ahead
        self.assertEqual(sorted(d["entity"].unique()), ["ercot:system", "ercot:wind:COASTAL", "ercot:wind:NORTH", "ercot:wind:PANHANDLE",
                                                         "ercot:wind:SOUTH", "ercot:wind:WEST"])
        self.assertEqual(sorted(d["variable"].unique()), ["wind_generation_mw", "wind_hsl_mw"])
        # the HSL is system-wide only: a region has generation and nothing else (COP HSL and forecasts are not read)
        self.assertEqual(set(d[d["variable"] == "wind_hsl_mw"]["entity"]), {"ercot:system"})
        self.assertEqual(len(d), 48 * 7)
        # 09/28/2026 hour ending 01 (Central daylight time) starts at 05:00 UTC; the file's own figures for it
        first = d[d["ts"] == pd.Timestamp("2026-09-28T05:00:00Z")].set_index(["entity", "variable"])["value"]
        self.assertEqual(first[("ercot:system", "wind_generation_mw")], 9499.69)
        self.assertEqual(first[("ercot:system", "wind_hsl_mw")], 9945.47)
        self.assertEqual(first[("ercot:wind:PANHANDLE", "wind_generation_mw")], 1211.53)
        # the hours ahead have a forecast and no actual: a blank stays blank, no row
        self.assertEqual(d["ts"].max(), pd.Timestamp("2026-09-30T04:00:00Z"))

    def test_solar_posting_and_its_regions(self):
        d, _ = c.parse_posting(body(SOLAR_NEW), "solar")
        self.assertEqual(sorted(e for e in d["entity"].unique() if e != "ercot:system"),
                         ["ercot:solar:CenterEast", "ercot:solar:CenterWest", "ercot:solar:FarEast", "ercot:solar:FarWest",
                          "ercot:solar:NorthWest", "ercot:solar:SouthEast"])
        self.assertEqual(len(d), 48 * 8)
        noon = d[d["ts"] == pd.Timestamp("2026-09-29T16:00:00Z")].set_index(["entity", "variable"])["value"]  # hour ending 12
        self.assertEqual(noon[("ercot:system", "solar_generation_mw")], 23546.16)
        self.assertEqual(noon[("ercot:system", "solar_hsl_mw")], 23150.73)
        self.assertEqual(noon[("ercot:solar:FarEast", "solar_generation_mw")], 11398.96)

    def test_a_posting_of_another_report_is_refused(self):
        with self.assertRaises(Exception):
            c.parse_posting(body(WORKBOOK), "wind")

    def test_only_actual_columns_are_read(self):
        cols = c.posting_columns(["DELIVERY_DATE", "HOUR_ENDING", "SYSTEM_WIDE_GEN", "COP_HSL_SYSTEM_WIDE", "STWPF_SYSTEM_WIDE", "WGRPP_SYSTEM_WIDE",
                                  "GEN_WEST", "COP_HSL_WEST", "STWPF_WEST", "WGRPP_WEST", "SYSTEM_WIDE_HSL", "DSTFlag"], "wind")
        self.assertEqual(cols, {"SYSTEM_WIDE_GEN": ("ercot:system", "wind_generation_mw"), "GEN_WEST": ("ercot:wind:WEST", "wind_generation_mw"),
                                "SYSTEM_WIDE_HSL": ("ercot:system", "wind_hsl_mw")})

    def test_clock_change_labels(self):
        # clock labels only, no figure: ERCOT's hour ending 02 twice on the autumn day (DSTFlag Y on the second), and
        # the hour ending 03 that the spring day does not have
        d = pd.DataFrame({"DELIVERY_DATE": ["11/02/2025", "11/02/2025", "11/02/2025", "11/02/2025", "03/09/2025", "03/09/2025", "03/09/2025"],
                          "HOUR_ENDING": ["01", "02", "02", "03", "02", "03", "04"], "DSTFlag": ["N", "N", "Y", "N", "N", "N", "N"]})
        ts = c.hour_starts(d)
        self.assertEqual([t.strftime("%Y-%m-%dT%H:%MZ") for t in ts[:4]], ["2025-11-02T05:00Z", "2025-11-02T06:00Z", "2025-11-02T07:00Z", "2025-11-02T08:00Z"])
        self.assertEqual(ts[4].strftime("%Y-%m-%dT%H:%MZ"), "2025-03-09T07:00Z")
        self.assertTrue(pd.isna(ts[5]))
        self.assertEqual(ts[6].strftime("%Y-%m-%dT%H:%MZ"), "2025-03-09T08:00Z")  # hour ending 04 follows hour ending 02 with no hour lost

    def test_the_newest_posting_wins_and_the_hours_join(self):
        s = hourly_table()
        self.assertFalse(s.duplicated(["entity", "variable", "ts_utc"]).any())
        g = s[(s["entity"] == "ercot:system") & (s["variable"] == "wind_generation_mw")]
        ts = pd.to_datetime(g["ts_utc"]).sort_values()
        self.assertTrue((ts.diff().dropna() == pd.Timedelta(hours=1)).all())  # two postings, one unbroken run of hours
        self.assertEqual((g["unit"].unique().tolist(), g["freq"].unique().tolist()), (["MW"], ["PT1H"]))


class Workbook(unittest.TestCase):
    def setUp(self):
        self.rows, self.n_file = c.workbook_rows(body(WORKBOOK))

    def test_a_23_hour_and_a_25_hour_day(self):
        self.assertEqual(self.n_file, 2 * (72 - 1 + 72 + 1))
        for variable in ("wind_generation_mw", "solar_generation_mw"):
            g = self.rows[self.rows["variable"] == variable]
            days = g["ts"].dt.tz_convert(c.TZ).dt.strftime("%Y-%m-%d").value_counts()
            self.assertEqual(days["2025-03-09"], 23)
            self.assertEqual(days["2025-11-02"], 25)
            self.assertEqual(days["2025-03-08"], 24)
            for month in (3, 11):  # each block of three days is an unbroken run of UTC hours
                ts = g[g["ts"].dt.month == month]["ts"].sort_values()
                self.assertTrue((ts.diff().dropna() == pd.Timedelta(hours=1)).all(), (variable, month))

    def test_the_hour_is_named_by_its_end(self):
        w = self.rows[self.rows["variable"] == "wind_generation_mw"].set_index("ts")["value"]
        # the workbook's row "2025-03-09 01:00" (hour ending, standard time) is the hour from 06:00 UTC
        self.assertAlmostEqual(w[pd.Timestamp("2025-03-09T06:00:00Z")], 16794.973667534723, places=6)
        # its next row is "2025-03-09 03:00" (daylight time): the hour from 07:00 UTC, no hour lost
        self.assertAlmostEqual(w[pd.Timestamp("2025-03-09T07:00:00Z")], 15673.925111762153, places=6)
        # "2025-11-02 01:00" twice: the first is daylight time (from 05:00 UTC), the second standard (from 06:00 UTC)
        self.assertAlmostEqual(w[pd.Timestamp("2025-11-02T05:00:00Z")], 9134.998746202256, places=6)
        self.assertAlmostEqual(w[pd.Timestamp("2025-11-02T06:00:00Z")], 9859.250699869792, places=6)
        self.assertEqual(set(self.rows["entity"]), {"ercot:system"})

    def test_a_sample_is_not_a_whole_year(self):
        with self.assertRaises(RuntimeError):
            c.check_year(self.rows, "the sample")


class Monthly(unittest.TestCase):
    def test_a_month_under_95_percent_of_its_hours_is_not_written(self):
        s = hourly_table()  # three days of September 2026
        m, left = c.monthly(s)
        self.assertTrue(m.empty)
        self.assertEqual({(e, f, p) for e, f, p, _, _ in left if e == "ercot:system"}, {("ercot:system", "wind", "2026-09"), ("ercot:system", "solar", "2026-09")})
        held, want = next((n, w) for e, f, p, n, w in left if (e, f) == ("ercot:system", "wind"))
        self.assertEqual((held, want), (71, 720))

    def test_monthly_sums_equal_the_daily_sums_of_the_same_hours(self):
        s = hourly_table()
        with mock.patch.object(c, "MIN_SHARE_OF_HOURS", 0.05):  # the rule lowered so that the sample's month is written
            m, left = c.monthly(s)
        self.assertEqual(left, [])
        self.assertEqual(set(m["ts_utc"]), {"2026-09-01T00:00:00Z"})
        days = c.sums(c.wide(s), "D")
        self.assertEqual(sorted(days["period"].unique()), ["2026-09-28", "2026-09-29", "2026-09-30"])
        got = m.set_index(["entity", "variable"])["value"]
        for (entity, fuel), g in days.groupby(["entity", "fuel"]):
            self.assertAlmostEqual(got[(entity, f"{fuel}_generation_mwh")], g["generation_mwh"].sum(), places=2)
            self.assertEqual(got[(entity, f"{fuel}_hours_held")], g["hours_held"].sum())
            self.assertEqual(got[(entity, f"{fuel}_hours_in_month")], 720)
            if entity == "ercot:system":
                self.assertAlmostEqual(got[(entity, f"{fuel}_hsl_mwh")], g["hsl_mwh"].sum(), places=2)
                self.assertAlmostEqual(got[(entity, f"{fuel}_below_hsl_mwh")], g["below_hsl_mwh"].sum(), places=2)
            else:  # ERCOT prints no HSL for a region: no HSL, no estimate, no share
                for v in ("hsl_mwh", "below_hsl_mwh", "below_hsl_share_pct"):
                    self.assertNotIn((entity, f"{fuel}_{v}"), got.index)

    def test_below_hsl_is_the_daily_table_s_estimate(self):
        s = hourly_table()
        w = c.wide(s)
        g = w[(w["entity"] == "ercot:system") & (w["fuel"] == "wind") & (w["ts"] >= "2026-09-29T05:00:00Z") & (w["ts"] < "2026-09-30T05:00:00Z")]
        self.assertEqual(len(g), 24)
        by_hand = sum(max(0.0, h - x) for x, h in zip(g["gen"], g["hsl"]))
        day = c.sums(w, "D")
        got = day[(day["entity"] == "ercot:system") & (day["fuel"] == "wind") & (day["period"] == "2026-09-29")].iloc[0]
        self.assertAlmostEqual(got["below_hsl_mwh"], by_hand, places=6)
        self.assertEqual((got["hours_held"], got["hours_in_period"]), (24, 24))

    def test_a_share_never_exceeds_100(self):
        s = hourly_table()
        with mock.patch.object(c, "MIN_SHARE_OF_HOURS", 0.05):
            m, _ = c.monthly(s)
        share = m[m["variable"].str.endswith("_below_hsl_share_pct")]
        self.assertEqual(len(share), 2)  # wind and solar, system-wide
        self.assertTrue(((share["value"] >= 0) & (share["value"] <= 100)).all())
        self.assertEqual(share["unit"].unique().tolist(), ["pct"])
        # the guard itself, on figures made up for this test and held nowhere: output below zero would put the sum of
        # max(0, HSL - GEN) above the HSL; such a share is left out, never clipped to 100
        made_up = pd.DataFrame({"entity": "ercot:system", "variable": ["wind_generation_mw", "wind_hsl_mw"] * 2,
                                "ts_utc": ["2026-09-28T05:00:00Z"] * 2 + ["2026-09-28T06:00:00Z"] * 2, "value": [-5.0, 1.0, -5.0, 1.0],
                                "retrieved_at": "2026-10-07T00:00:00Z"})
        said = []
        with mock.patch.object(c, "MIN_SHARE_OF_HOURS", 0.0):
            m2, _ = c.monthly(made_up, said.append)
        self.assertFalse(m2["variable"].str.endswith("_share_pct").any())
        self.assertTrue(any("above 100" in x for x in said))

    def test_hours_in_a_month_follow_the_clock(self):
        w = pd.DataFrame({"entity": "ercot:system", "fuel": "wind", "ts": pd.to_datetime(["2025-03-15T12:00:00Z", "2025-11-15T12:00:00Z", "2025-03-09T12:00:00Z"]),
                          "gen": [1.0, 1.0, 1.0], "hsl": [1.0, 1.0, 1.0]})
        months = c.sums(w, "M").set_index("period")["hours_in_period"]
        self.assertEqual((months["2025-03"], months["2025-11"]), (743, 721))
        days = c.sums(w, "D").set_index("period")["hours_in_period"]
        self.assertEqual(days["2025-03-09"], 23)


class Pull(unittest.TestCase):
    def setUp(self):
        self.raw, self.tmp = c.RAW, tempfile.mkdtemp(prefix="erw144_")
        c.RAW = self.tmp
        self.addCleanup(self._restore)

    def _restore(self):
        c.RAW = self.raw
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def no_request(*a, **k):
        raise AssertionError("a request was made")

    DOCS = [{"FriendlyName": "WPPHRLYAVGACTGEONP4742_csv", "PublishDate": "2026-09-30T23:55:12-05:00", "DocID": "1", "ConstructedName": "a.zip", "Extension": "zip"}]

    def test_the_ceiling_stops_before_the_file(self):
        c.record(retrieved_at="2026-10-07T00:00:00Z", status=200, bytes=1, sha256="", kind="probe", file="", url="https://www.ercot.com/x", published="",
                 series_rows=c.CEILING - 10, file_rows=0, note="rows already read")
        self.assertEqual(c.counted()[0], c.CEILING - 10)
        with self.assertRaises(c.CeilingStop):
            c.ask(c.POSTING_EST, "one posting")
        c.ask(10, "ten rows")  # exactly at the ceiling is allowed, one more is not
        with self.assertRaises(c.CeilingStop):
            c.ask(11, "eleven rows")
        with mock.patch.object(c.ip, "paused", lambda scope: None), mock.patch.object(c, "listing", lambda rtid, log: self.DOCS), \
                mock.patch.object(c, "http_get", self.no_request):
            with self.assertRaises(c.CeilingStop):
                c.pull(lambda m: None)
        self.assertEqual(len(c.manifest()), 1)  # nothing was asked, nothing recorded

    def test_a_paused_publisher_is_never_asked(self):
        row = {"scope": "ercot", "paused_on": "2026-10-07", "reason": "a test", "terms_url": "https://www.ercot.com/help/terms", "until": "a person lifts it"}
        with mock.patch.object(c.ip, "paused", lambda scope: row if scope == "ercot" else None), mock.patch.object(c, "http_get", self.no_request), \
                mock.patch.object(c.requests, "get", self.no_request):
            said = []
            self.assertEqual(c.pull(said.append), "paused: no request made")
        self.assertTrue(any("PAUSED" in x for x in said))
        self.assertEqual(c.manifest(), [])

    def test_a_saved_file_is_not_asked_for_again(self):
        os.makedirs(os.path.join(self.tmp, "postings"))
        shutil.copy(os.path.join(FIX, WIND_NEW), os.path.join(self.tmp, "postings", "a.zip"))
        c.record(retrieved_at="2026-10-07T00:00:00Z", status=200, bytes=1, sha256="", kind="posting", file="postings/a.zip", url=c.DOC.format("1"),
                 published="2026-09-30T23:55:12-05:00", series_rows=336, file_rows=216, note="NP4-742-CD wind")
        self.assertIn(c.DOC.format("1"), c.held())
        with mock.patch.object(c.ip, "paused", lambda scope: None), mock.patch.object(c, "listing", lambda rtid, log: self.DOCS if rtid == 14787 else []), \
                mock.patch.object(c, "http_get", self.no_request):
            self.assertEqual(c.pull(lambda m: None), "ok: 0 files saved")

    def test_an_access_control_stops_the_pull(self):
        class Answer:
            status_code, content = 403, b"denied"
        with mock.patch.object(c, "http_get", lambda url: Answer()), mock.patch.object(c.time, "sleep", lambda s: None):
            with self.assertRaises(c.AccessStop):
                c.fetch(c.DOC.format("1"), "posting", "a.zip", lambda m: None)
        self.assertEqual([r["status"] for r in c.manifest()], ["403"])
        self.assertEqual(c.held(), {})

    def test_the_postings_wanted(self):
        docs = [{"FriendlyName": "X_csv", "PublishDate": f"2026-10-0{d}T{h:02d}:55:12-05:00", "DocID": f"{d}{h:02d}"} for d in (1, 2, 3) for h in (0, 12, 23)]
        docs += [{"FriendlyName": "X_xml", "PublishDate": "2026-10-03T23:56:00-05:00", "DocID": "x"}]
        first = c.pick_postings(docs)
        self.assertEqual([x["DocID"] for x in first], ["100", "123", "223", "323"])  # the oldest, then the last of each day
        later = c.pick_postings(docs, ["2026-09-30T23:55:12-05:00"])  # one as old is saved: the oldest adds nothing
        self.assertEqual([x["DocID"] for x in later], ["123", "223", "323"])


class House(unittest.TestCase):
    def test_no_em_dash_and_the_estimate_is_named(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "ercot_wind_solar_history.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn(chr(0x2014), text)
        self.assertIn("ESTIMATE", text)
        self.assertIn("ip.paused(\"ercot\")", text)
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
