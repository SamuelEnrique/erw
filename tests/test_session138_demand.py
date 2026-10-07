"""Session 138: hourly load by zone or area, one connector an operator (ERCOT, NYISO, ISO-NE, CAISO).
No request is made. The parsers read short samples cut from the real files the session pulled, in each operator's
own layout (tests/fixtures/session138/; the lines are the operators' own, a few of each file), chosen to hold the
23-hour and the 25-hour day of 2025 (and of 2015 for ERCOT's older layout)."""
import io
import os
import re
import sys
import tempfile
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import caiso_area_load as caiso  # noqa: E402
import ercot_zone_load as ercot  # noqa: E402
import isone_zone_load as isone  # noqa: E402
import nyiso_zone_load as nyiso  # noqa: E402
import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session138")
CONNECTORS = {"ercot_zone_load": ercot, "nyiso_zone_load": nyiso, "isone_zone_load": isone, "caiso_area_load": caiso}
TABLES = ["ercot_zone_load_hourly", "nyiso_zone_load_hourly", "isone_zone_load_hourly", "caiso_area_load_hourly"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def sample(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


def hours(piece, entity):
    p = piece[piece["entity"] == entity].sort_values("ts")
    return {ip.utc_iso(t): v for t, v in zip(p["ts"], p["value"])}


class Ercot(unittest.TestCase):
    def test_the_files_from_2017_hour_ending_text_the_23_hour_day_and_the_repeated_hour_marked_dst(self):
        piece, n, lost, by_end = ercot.parse_frame(pd.read_csv(io.StringIO(sample("ercot_native_load_2025_sample.csv"))))
        self.assertEqual((n, lost, by_end), (16 * 9, [], 0))
        coast = hours(piece, "ercot:COAST")
        # 9 March 2025: hour ending 24:00 of the 8th, 01:00, 02:00, then 04:00 (no 03:00): four hours in a row in UTC
        self.assertEqual([coast[t] for t in ("2025-03-09T05:00:00Z", "2025-03-09T06:00:00Z", "2025-03-09T07:00:00Z", "2025-03-09T08:00:00Z")],
                         [11195.920423, 10636.512193, 10354.084428, 10214.514406])
        # 2 November 2025: 02:00 is daylight time (06:00Z), "02:00 DST" the second, standard time (07:00Z), 03:00 follows
        self.assertEqual([coast[t] for t in ("2025-11-02T06:00:00Z", "2025-11-02T07:00:00Z", "2025-11-02T08:00:00Z")], [10354.600289, 10157.466148, 10077.345423])
        self.assertEqual(coast["2025-11-03T05:00:00Z"], 10896.223514)                      # 24:00 is the hour that ends at midnight
        self.assertEqual(set(piece["entity"]), {"ercot:" + z for z in ercot.ZONES} | {"ercot:system"})
        self.assertEqual(set(piece[piece["entity"] == "ercot:system"]["node"]), {"ERCOT"})

    def test_the_files_of_2015_date_cells_older_column_names_and_the_spring_hour_labelled_by_its_end(self):
        df = pd.read_csv(io.StringIO(sample("ercot_native_load_2015_sample.csv")), parse_dates=["Hour_End"])
        piece, n, lost, by_end = ercot.parse_frame(df)
        self.assertEqual((n, lost, by_end), (16 * 9, [], 1))
        coast = hours(piece, "ercot:COAST")
        # 8 March 2015: ends 00:00, 01:00, then 03:00 (no 02:00): the hour that ended at 03:00 daylight time began at 07:00Z
        self.assertEqual([round(coast[t], 4) for t in ("2015-03-08T05:00:00Z", "2015-03-08T06:00:00Z", "2015-03-08T07:00:00Z")], [8725.2603, 8317.7111, 8248.0779])
        self.assertIn("2015-03-08T08:00:00Z", coast)
        # 1 November 2015: the stamp 01:59:59.997 twice: the first is 06:00Z (daylight time), the second 07:00Z
        self.assertEqual([round(coast[t], 4) for t in ("2015-11-01T06:00:00Z", "2015-11-01T07:00:00Z")], [8542.4003, 8261.1618])
        self.assertEqual(set(piece[piece["entity"] == "ercot:FWEST"]["node"]), {"FAR_WEST"})          # the same zone under its older column name
        self.assertEqual(set(piece[piece["entity"] == "ercot:NCENT"]["node"]), {"NORTH_C"})

    def test_a_file_laid_out_otherwise_and_a_dst_mark_out_of_order_are_refused(self):
        with self.assertRaises(RuntimeError):
            ercot.parse_frame(pd.DataFrame({"Hour Ending": ["01/01/2025 01:00"], "COAST": [1.0]}))
        text = sample("ercot_native_load_2025_sample.csv").replace("11/02/2025 02:00,", "11/02/2025 02:00 DST,")       # both marked: the first is not the second
        with self.assertRaises(RuntimeError):
            ercot.parse_frame(pd.read_csv(io.StringIO(text)))

    def test_the_page_gives_one_file_a_year_and_weather_zones_are_said_not_to_be_load_zones(self):
        html = ('<a href="https://www.ercot.com/files/docs/2016/01/07/native_load_2015.xls">2015</a> <a href="https://www.ercot.com/files/docs/2017/01/10/native_Load_2016.zip">2016</a>'
                '<a href="https://www.ercot.com/files/docs/2026/02/10/Native_Load_2026.zip">2026</a> <a href="https://www.ercot.com/files/docs/2015/10/22/2014_ercot_hourly_load_data.xls">2014</a>')
        self.assertEqual(sorted(ercot.links(html)), [2015, 2016, 2026])
        doc = " ".join(ercot.__doc__.split())
        for words in ("WEATHER ZONES ARE NOT LOAD ZONES", "does not join ercot:LZ_NORTH or ercot:HB_NORTH", "never a sum made here"):
            self.assertIn(words, doc, words)


class Nyiso(unittest.TestCase):
    def test_the_23_hour_day_the_files_time_zone_column_places_each_hour(self):
        piece, n, skipped = nyiso.parse_day(sample("nyiso_20250309palIntegrated_sample.csv"))
        self.assertEqual((n, sum(skipped.values())), (8, 0))
        # 9 March 2025: 00:00 EST, 01:00 EST, then 03:00 EDT (no 02:00), 04:00 EDT: four hours in a row in UTC
        self.assertEqual(list(hours(piece, "nyiso:N.Y.C.")), ["2025-03-09T05:00:00Z", "2025-03-09T06:00:00Z", "2025-03-09T07:00:00Z", "2025-03-09T08:00:00Z"])

    def test_the_25_hour_day_and_the_zone_names_of_the_price_tables(self):
        piece, n, skipped = nyiso.parse_day(sample("nyiso_20251102palIntegrated_sample.csv"))
        self.assertEqual(n, 12)
        cap = hours(piece, "nyiso:CAPITL")
        self.assertEqual((cap["2025-11-02T05:00:00Z"], cap["2025-11-02T06:00:00Z"]), (1072.1903, 1062.1101))      # 01:00 EDT, then 01:00 EST
        self.assertEqual(list(cap), [f"2025-11-02T0{h}:00:00Z" for h in range(4, 10)])
        self.assertEqual(nyiso.ZONES, ip.NYISO_ZONES)
        self.assertEqual(len(nyiso.ZONES), 11)

    def test_a_line_off_the_hour_or_blank_is_not_written_and_another_layout_is_refused(self):
        text = sample("nyiso_20251102palIntegrated_sample.csv") + '"11/02/2025 04:07:30","EST","CAPITL",61757,1.0\n"11/02/2025 05:00:00","EST","CAPITL",61757,\n'
        piece, n, skipped = nyiso.parse_day(text)
        self.assertEqual((n, len(piece), skipped["not on the hour"], skipped["blank load"]), (14, 12, 1, 1))
        with self.assertRaises(RuntimeError):
            nyiso.parse_day('"Time Stamp","Name","Load"\n"11/02/2025 00:00:00","CAPITL",1\n')


class Isone(unittest.TestCase):
    def sheet(self, name):
        return pd.read_csv(io.StringIO(sample(f"isone_smd_hourly_2025_{name}_sample.csv")), dtype={"Hr_End": str})

    def test_the_spring_day_goes_01_then_03_and_the_autumn_day_holds_02x(self):
        piece, n, lost = isone.parse_sheet(self.sheet("ME"), "ME")
        self.assertEqual((n, lost), (12, []))
        me = hours(piece, "isone:.Z.MAINE")
        # 9 March 2025: hour ending 01, 03, 04 are 05:00Z, 06:00Z, 07:00Z: three hours in a row
        self.assertEqual([me[t] for t in ("2025-03-09T05:00:00Z", "2025-03-09T06:00:00Z", "2025-03-09T07:00:00Z")], [1239.502, 1215.893, 1209.045])
        # 2 November 2025: 01 is 04:00Z, 02 is 05:00Z (daylight time), 02X is 06:00Z (standard time), 03 is 07:00Z
        self.assertEqual([round(me[t], 1) for t in ("2025-11-02T04:00:00Z", "2025-11-02T05:00:00Z", "2025-11-02T06:00:00Z", "2025-11-02T07:00:00Z")], [1007.3, 967.8, 973.1, 971.8])
        self.assertEqual(set(piece["node"]), {"ME"})

    def test_the_control_areas_sheet_is_the_system_and_the_zones_carry_the_price_tables_names(self):
        piece, n, lost = isone.parse_sheet(self.sheet("ISO_NE_CA"), "ISO NE CA")
        self.assertEqual(set(piece["entity"]), {"isone:system"})
        self.assertEqual(round(hours(piece, "isone:system")["2025-11-02T06:00:00Z"], 1), 9761.3)
        self.assertEqual({e.split(":", 1)[1] for e in isone.SHEETS.values()} - {"system"}, {n for n in ip.ISONE_NODES if n.startswith(".Z.")})

    def test_a_sheet_without_rt_demand_is_refused_and_the_list_gives_the_yearly_workbooks(self):
        with self.assertRaises(RuntimeError):
            isone.parse_sheet(pd.DataFrame({"Date": ["2025-01-01"], "Hr_End": ["01"], "DA_Demand": [1.0]}), "ME")
        text = ('{"data":[{"path":"/static-assets/documents/100032/2026_smd_hourly.xlsx","publishDate":"09/18/2026 04:42 PM EDT"},'
                '{"path":"/static-assets/documents/100032/2026_smd_daily.xlsx","publishDate":"09/18/2026 04:44 PM EDT"},{"path":"/static-assets/documents/2016/02/smd_hourly.xls","publishDate":"x"}]}')
        got = isone.listed([text])
        self.assertEqual(list(got), [2026])
        self.assertEqual((got[2026][0], ip.utc_iso(got[2026][1])), ("https://www.iso-ne.com/static-assets/documents/100032/2026_smd_hourly.xlsx", "2026-09-18T20:42:00Z"))

    def test_it_is_internal_and_answers_no_captcha(self):
        self.assertEqual(isone.SPEC["entry"]["license"], "internal")
        code = src("warehouse", "connectors", "isone_zone_load.py")
        self.assertNotIn("downloadDocumentZips", code)                    # the page's form behind the CAPTCHA is never posted to
        self.assertNotIn("validateCaptcha", code)


class Caiso(unittest.TestCase):
    def zipped(self, text):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("20251026_20251125_SLD_FCST_ACTUAL_v1.csv", text)
        return b.getvalue()

    def test_the_hours_are_caisos_own_gmt_stamps_the_repeated_hour_included(self):
        piece, n = caiso.parse(self.zipped(sample("caiso_sld_fcst_actual_20251102_sample.csv")))
        self.assertEqual(n, 12)
        self.assertEqual(set(piece["entity"]), {"caiso:system", "caiso:PGE-TAC", "caiso:VEA-TAC"})
        # 2 November 2025, Pacific: 00:00 PDT is 07:00Z, 01:00 PDT 08:00Z, 01:00 PST 09:00Z, 02:00 PST 10:00Z
        self.assertEqual(hours(piece, "caiso:system"), {"2025-11-02T07:00:00Z": 21295.0, "2025-11-02T08:00:00Z": 20717.0, "2025-11-02T09:00:00Z": 20536.0,
                                                        "2025-11-02T10:00:00Z": hours(piece, "caiso:system")["2025-11-02T10:00:00Z"]})
        self.assertEqual(set(piece[piece["entity"] == "caiso:system"]["node"]), {"CA ISO-TAC"})

    def test_no_data_is_no_hour_another_error_is_raised_and_another_item_is_not_read(self):
        none = "<m:ERROR><m:ERR_CODE>1000</m:ERR_CODE><m:ERR_DESC>No data returned for the specified selection</m:ERR_DESC></m:ERROR>"
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("x.xml", none)
        piece, n = caiso.parse(b.getvalue())
        self.assertEqual((len(piece), n), (0, 0))
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("x.xml", "<m:ERROR><m:ERR_CODE>1004</m:ERR_CODE><m:ERR_DESC>Data can be requested for period of 31 days only</m:ERR_DESC></m:ERROR>")
        with self.assertRaises(RuntimeError):
            caiso.parse(b.getvalue())
        text = sample("caiso_sld_fcst_actual_20251102_sample.csv").replace("SYS_FCST_ACT_MW", "SYS_FCST_DA_MW").replace(",ACTUAL,CA ISO-TAC", ",DAM,CA ISO-TAC")
        self.assertEqual(len(caiso.parse(self.zipped(text))[0]), 0)

    def test_a_request_is_30_days_names_the_six_areas_and_its_address_does_not_move(self):
        w = caiso.windows(pd.Timestamp("2021-10-01", tz="UTC"), pd.Timestamp("2026-10-07", tz="UTC"))
        self.assertTrue(all((b - a).days == 30 for a, b in w))
        self.assertEqual(w, caiso.windows(pd.Timestamp("2021-10-01", tz="UTC"), pd.Timestamp("2026-10-07", tz="UTC")))
        self.assertLessEqual(w[-1][0], pd.Timestamp("2021-10-01", tz="UTC"))
        self.assertGreater(w[0][1], pd.Timestamp("2026-10-07", tz="UTC"))
        self.assertIn("tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC", caiso.URL)
        self.assertGreaterEqual(caiso.PAUSE, 5)


class ClockChange(unittest.TestCase):
    """A day of 23 hours and a day of 25, under both ways of labelling the hour after the spring change."""

    def day(self, date, skip=None, twice=None):
        starts = []
        for h in range(24):
            if h == skip:
                continue
            starts.append(pd.Timestamp(date) + pd.Timedelta(hours=h))
            if h == twice:
                starts.append(pd.Timestamp(date) + pd.Timedelta(hours=h))
        return starts

    def test_a_23_hour_day_labelled_by_the_hours_number_or_by_its_end_is_the_same_23_hours(self):
        by_number, n1 = zl.to_utc(self.day("2025-03-09", skip=2), "America/Chicago")           # hour ending 01, 02, 04: starts 00, 01, 03
        by_end, n2 = zl.to_utc(self.day("2025-03-09", skip=1), "America/Chicago")              # hour ending 01, 03, 04: starts 00, 02, 03
        self.assertEqual((n1, n2), (0, 1))
        want = list(pd.date_range("2025-03-09T06:00:00Z", periods=23, freq="h"))
        self.assertEqual(list(by_number), want)
        self.assertEqual(list(by_end), want)

    def test_a_25_hour_day_is_25_hours_in_a_row(self):
        ts, n = zl.to_utc(self.day("2025-11-02", twice=1), "America/New_York")
        self.assertEqual((list(ts), n), (list(pd.date_range("2025-11-02T04:00:00Z", periods=25, freq="h")), 0))
        marked = [False] * 25
        marked[2] = True
        self.assertEqual(list(zl.to_utc(self.day("2025-11-02", twice=1), "America/New_York", second=marked)[0]), list(ts))

    def test_the_repeated_hour_held_once_is_not_placed_and_nothing_is_guessed(self):
        ts, n = zl.to_utc(self.day("2025-11-02"), "America/Chicago")
        self.assertEqual(int(ts.isna().sum()), 1)
        self.assertTrue(pd.isna(ts[1]))
        self.assertEqual(ts[2], pd.Timestamp("2025-11-02T08:00:00Z"))

    def test_an_hour_given_twice_is_refused_and_a_blank_is_not_written(self):
        t = pd.Timestamp("2025-01-01T06:00:00Z")
        rec = {"retrieved_at": "2026-10-07T00:00:00Z", "last_modified": ""}
        twice = pd.DataFrame({"entity": ["x:A", "x:A"], "node": ["A", "A"], "ts": [t, t], "value": [1.0, 2.0]})
        with self.assertRaises(RuntimeError):
            zl.rows(ercot.SPEC, twice, "u", rec)
        blank = pd.DataFrame({"entity": ["x:A", "x:A"], "node": ["A", "A"], "ts": [t, t + pd.Timedelta(hours=1)], "value": [1.0, None]})
        out = zl.rows(ercot.SPEC, blank, "u", rec)
        self.assertEqual(list(out.columns), ip.SERIES_COLS)
        self.assertEqual((len(out), out["variable"][0], out["unit"][0], out["freq"][0], out["ts_utc"][0]), (1, "load", "MW", "PT1H", "2025-01-01T06:00:00Z"))
        kept, differ = zl.once(twice, lambda *_: None, "x")
        self.assertEqual((len(kept), differ), (0, 1))                       # two different loads for one hour: neither is chosen
        same = twice.assign(value=[1.0, 1.0])
        self.assertEqual(len(zl.once(same, lambda *_: None, "x")[0]), 1)


class Ceiling(unittest.TestCase):
    def test_the_count_is_session_136s_and_stops_a_run_past_its_ceiling(self):
        c = zl.Counter(100)
        c.add(60)
        self.assertTrue(c.room(40))
        self.assertFalse(c.room(41))
        with self.assertRaises(zl.Ceiling):
            c.add(41)

    def test_each_connector_stops_before_a_file_that_would_pass_its_ceiling_and_asks_for_nothing(self):
        asked = []

        def fetch(connector, url, log, **kw):
            asked.append(url)
            if "load_hist" in url:
                return b'<a href="https://www.ercot.com/files/docs/2026/02/10/Native_Load_2026.zip">2026</a>', {"file": "", "retrieved_at": "x"}
            if "docWidgetGetMore" in url:
                return b'{"data":[{"path":"/static-assets/documents/100032/2026_smd_hourly.xlsx","publishDate":"09/18/2026 04:42 PM EDT"}]}', {"file": "", "retrieved_at": "x"}
            raise AssertionError(f"a data file was asked for past the ceiling: {url}")

        old_fetch, old_cached = ip.fetch_raw, ip.raw_cached
        ip.fetch_raw, ip.raw_cached = fetch, lambda connector, url: None
        try:
            first = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=5)
            for name, m in CONNECTORS.items():
                pieces, notes = m.pull(lambda *_: None, first, zl.Counter(10))
                self.assertEqual(pieces, [], name)
                self.assertTrue(any("would pass the ceiling" in n for n in notes), name)
        finally:
            ip.fetch_raw, ip.raw_cached = old_fetch, old_cached
        self.assertTrue(all("load_hist" in u or "docWidgetGetMore" in u for u in asked), asked)      # the page and the list only: no row of data

    def test_a_kept_raw_file_is_not_counted_again_and_the_room_is_asked_before_the_file(self):
        for name in CONNECTORS:
            code = src("warehouse", "connectors", name + ".py")
            body = code.split("def pull(")[1]
            self.assertIn("if not zl.reused(rec):", body, name)
            self.assertLess(body.index("counter.room("), body.index("counter.add("), name)
        self.assertIs(zl.reused, __import__("dam_cleared").reused)

    def test_the_plan_of_the_pull_stays_under_the_ceiling(self):
        # the shares given to the four pulls of session 138 (the --ceiling of each history run) and the hard ceiling
        shares = {"ercot": 1_000_000, "nyiso": 850_000, "isone": 200_000, "caiso": 300_000}
        self.assertLessEqual(sum(shares.values()), 3_600_000)
        self.assertLessEqual(3_600_000, 0.9 * 4_000_000)


class Frame(unittest.TestCase):
    def test_the_pause_list_is_asked_before_any_pull(self):
        frame = src("warehouse", "connectors", "zone_load.py")
        self.assertLess(frame.index('ip.paused(spec["iso"])'), frame.index("= pull(log, first, counter)"))
        self.assertLess(frame.index('ip.paused(spec["iso"])'), frame.index("ip.RAW.open("))

    def test_a_paused_publisher_is_never_asked(self):
        called = []
        keep = (ip.paused, ip.write_status, ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR)
        ip.paused = lambda scope: {"scope": scope, "paused_on": "2026-10-04"}
        ip.write_status = lambda *a, **k: None
        try:
            with tempfile.TemporaryDirectory() as d:
                for name, m in CONNECTORS.items():
                    code = zl.run(m.SPEC, lambda *a: called.append(name), ["--out-dir", d])
                    self.assertEqual(code, 0, name)
        finally:
            ip.paused, ip.write_status, ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR = keep
        self.assertEqual(called, [])

    def test_no_connector_names_a_miso_or_pjm_host_and_neither_has_a_connector(self):
        for name in list(CONNECTORS) + ["zone_load"]:
            code = src("warehouse", "connectors", name + ".py")
            for host in ("misoenergy.org", "pjm.com", "dataminer"):
                self.assertNotIn(host, code, (name, host))
        for name in CONNECTORS:
            self.assertIn("zl.run(SPEC, pull)", src("warehouse", "connectors", name + ".py"))
        for iso in ("miso", "pjm"):
            for kind in ("zone", "area"):
                self.assertFalse(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", f"{iso}_{kind}_load.py")))

    def test_each_connector_quotes_its_operators_terms_with_the_address_and_isone_alone_is_internal(self):
        quotes = {"ercot_zone_load": ("may be used, reproduced, and redistributed in compilations, charts", "https://www.ercot.com/help/terms"),
                  "caiso_area_load": ("credit the California ISO", "https://www.caiso.com/privacy-terms-of-use"),
                  "nyiso_zone_load": ("does not confer any license", "https://www.nyiso.com/legal-notice"),
                  "isone_zone_load": ("Any duplication of the Content or non-personal use may violate", "https://www.iso-ne.com/legal-privacy")}
        for name, (words, address) in quotes.items():
            doc = " ".join(CONNECTORS[name].__doc__.split())
            self.assertIn(words, doc, name)
            self.assertIn(address, doc, name)
            entry = CONNECTORS[name].SPEC["entry"]
            self.assertIn("[terms:", entry["report"], name)                  # the registry's row carries the sentence too
            self.assertIn(address, entry["report"], name)
        self.assertEqual({n: m.SPEC["entry"]["license"] for n, m in CONNECTORS.items()},
                         {"ercot_zone_load": "public", "nyiso_zone_load": "public", "caiso_area_load": "public", "isone_zone_load": "internal"})

    def test_the_tables_names_follow_the_rule_and_no_file_holds_an_em_dash(self):
        for m in CONNECTORS.values():
            self.assertRegex(m.NAME, r"^[a-z0-9]+(_[a-z0-9]+){2,}$")
            self.assertLessEqual(len(m.NAME), 40)
        self.assertEqual(sorted(m.NAME for m in CONNECTORS.values()), sorted(TABLES))
        for f in list(CONNECTORS) + ["zone_load"]:
            self.assertNotIn(chr(0x2014), src("warehouse", "connectors", f + ".py"), f)
        self.assertNotIn(chr(0x2014), src("tests", "test_session138_demand.py"))


class Wiring(unittest.TestCase):
    def test_the_weekly_refresh_runs_the_four_connectors_under_health_and_validates_their_tables(self):
        sh = src("warehouse", "refresh_supply.sh")
        self.assertIn("for t in ercot_zone nyiso_zone isone_zone caiso_area; do", sh)
        self.assertIn('health.py run --step "${t}_load" -- "$PY" "warehouse/connectors/${t}_load.py"', sh)
        self.assertIn("warehouse/output/cftc_cot_positions.csv $CLEARED $LOADS", sh)
        self.assertNotRegex(sh, r"(miso|pjm)_(zone|area)_load")
        self.assertIn("bash warehouse/refresh_supply.sh", src("warehouse", "run_daily.sh"))            # the daily run calls the refresh on Saturdays
        for t in ("ercot_zone", "nyiso_zone", "isone_zone", "caiso_area"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", f"{t}_load.py")), t)

    def test_the_tables_are_held_out_of_the_live_set_restored_on_the_runner_and_have_a_sector(self):
        import yaml
        y = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        for t in TABLES:
            self.assertIn(t, y["catalogue_hold"], t)
        for s in ("ercot:load_hist", "nyiso:palIntegrated", "isone:smd_hourly", "caiso:SLD_FCST"):
            self.assertIn(s, y["sources_hold"], s)
            self.assertIn(s, {m.SOURCE for m in CONNECTORS.values()})
        c = yaml.safe_load(src("warehouse", "redivis", "config.yaml"))
        for t in TABLES:
            self.assertTrue(any(re.fullmatch(p, t) for p in c["restore_before_run"]), t)
        rules = src("warehouse", "metadata", "build_coverage.py")
        self.assertIn('(r"^(ercot_zone|nyiso_zone|isone_zone|caiso_area)_load_hourly$", "power")', rules)


if __name__ == "__main__":
    unittest.main()
