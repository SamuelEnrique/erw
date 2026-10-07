"""Session 140: the zone and hub price history from 2019 (warehouse/connectors/zone_price_history.py). Each parser on a
small real sample cut from the publishers' own files (tests/fixtures/session140/history/), the 23-hour and the 25-hour
day, the ceiling's stop before the request, the pause check, a refusal that is not worked around, and the table's
merge into two tables split by license (iso_zone_prices_history: NYISO, CAISO, SPP, public sources;
isone_zone_prices_history: ISO-NE, internal). No request and no model call: the one function that reaches the network
is replaced."""
import gzip
import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import iso_prices as ip  # noqa: E402
import zone_price_history as zh  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session140", "history")


def raw(name):
    with open(os.path.join(FIX, name), "rb") as f:
        return f.read()


def text(name):
    return raw(name).decode("utf-8")


def nyiso_zip(kind, days=("20250309", "20251102")):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for d in days:
            z.writestr(f"{d}{kind}_zone.csv", text(f"nyiso_{d}{kind}_zone_sample.csv"))
    return buf.getvalue()


class Response:
    def __init__(self, status, content=b"", headers=None, url=""):
        self.status_code, self.content, self.headers, self.url = status, content, headers or {}, url


class Sandbox(unittest.TestCase):
    """A raw folder and an output folder of its own; the network function replaced by one that counts its calls."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw140_")
        self.keep = (zh.RAW_ROOT, zh.CEILING, zh.http_get, dict(zh.PAUSE), ip.paused, ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR, zh.time.sleep)
        zh.RAW_ROOT = os.path.join(self.tmp, "raw")
        for k in zh.PAUSE:
            zh.PAUSE[k] = 0
        zh.time.sleep = lambda s: None
        self.calls = []
        zh.RUN["rows"] = 0

    def tearDown(self):
        (zh.RAW_ROOT, zh.CEILING, zh.http_get, pause, ip.paused, ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR, zh.time.sleep) = self.keep
        zh.PAUSE.update(pause)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def serve(self, answer):
        def fake(url, headers=None, timeout=300):
            self.calls.append(url)
            return answer(url)
        zh.http_get = fake


class Hours(unittest.TestCase):
    def test_nyiso_day_ahead_23_hour_day(self):
        got, k, n = zh.parse_nyiso(nyiso_zip("damlbmp", ("20250309",)), "nyiso_dam")
        p = got["nyiso_dam"]
        self.assertEqual(sorted(p["entity"].unique()), ["nyiso:N.Y.C.", "nyiso:WEST"])      # the external proxy PJM is read and not kept
        self.assertEqual((k, n), (46, 69))
        nyc = p[p["entity"] == "nyiso:N.Y.C."].sort_values("ts")
        self.assertEqual(len(nyc), 23)
        self.assertEqual(str(nyc["ts"].iloc[0]), "2025-03-09 05:00:00+00:00")                # midnight Eastern standard time
        self.assertEqual(str(nyc["ts"].iloc[-1]), "2025-03-10 03:00:00+00:00")               # 23:00 Eastern daylight time
        self.assertTrue((nyc["ts"].diff().dropna() == pd.Timedelta(hours=1)).all())          # no hour skipped in UTC
        first = [ln for ln in text("nyiso_20250309damlbmp_zone_sample.csv").splitlines() if ",N.Y.C.," in ln.replace('"', "")][0]
        self.assertAlmostEqual(nyc["value"].iloc[0], float(first.split(",")[3]), places=6)

    def test_nyiso_25_hour_day_both_markets(self):
        for kind, market in (("damlbmp", "nyiso_dam"), ("rtlbmp", "nyiso_rtm")):
            got, k, n = zh.parse_nyiso(nyiso_zip(kind, ("20251102",)), market)
            w = got[market][got[market]["entity"] == "nyiso:WEST"].sort_values("ts")
            self.assertEqual(len(w), 25, kind)
            self.assertEqual(w["ts"].nunique(), 25, kind)
            self.assertEqual(str(w["ts"].iloc[0]), "2025-11-02 04:00:00+00:00")
            self.assertEqual(str(w["ts"].iloc[-1]), "2025-11-03 04:00:00+00:00")
            # the file's two 01:00 lines, in the file's order, are 05:00 and 06:00 UTC
            lines = [ln.replace('"', "") for ln in text(f"nyiso_20251102{kind}_zone_sample.csv").splitlines() if ",WEST," in ln.replace('"', "") and " 01:00" in ln]
            self.assertEqual(len(lines), 2)
            at = w.set_index("ts")["value"]
            self.assertAlmostEqual(at[pd.Timestamp("2025-11-02T05:00:00Z")], float(lines[0].split(",")[3]), places=6)
            self.assertAlmostEqual(at[pd.Timestamp("2025-11-02T06:00:00Z")], float(lines[1].split(",")[3]), places=6)

    def test_a_repeated_hour_held_once_is_not_placed(self):
        local = pd.to_datetime(["2025-11-02 00:00", "2025-11-02 01:00", "2025-11-02 02:00", "2025-03-09 02:00"])
        ts = zh.place(local, ["A"] * 4, "America/New_York")
        self.assertEqual(str(ts[0]), "2025-11-02 04:00:00+00:00")
        self.assertTrue(pd.isna(ts[1]))            # 01:00 once: daylight or standard time, not known
        self.assertEqual(str(ts[2]), "2025-11-02 07:00:00+00:00")
        self.assertTrue(pd.isna(ts[3]))            # a clock time the spring day never had

    def test_isone_sheet_hour_ending_and_both_clock_changes(self):
        df = pd.read_csv(os.path.join(FIX, "isone_smd_hourly_2025_CT_sample.csv"), dtype={"Hr_End": str})
        got, n = zh.parse_isone_sheet(df, "CT")
        self.assertEqual(n, 24 + 23 + 25)
        for market, col in (("isone_dam", "DA_LMP"), ("isone_rtm", "RT_LMP")):
            p = got[market].sort_values("ts").reset_index(drop=True)
            self.assertEqual(set(p["entity"]), {"isone:.Z.CONNECTICUT"})
            self.assertEqual(p["ts"].nunique(), 72)
            # hour ending 01 of 8 March is the hour from midnight Eastern standard time: 05:00 UTC
            self.assertEqual(str(p["ts"].iloc[0]), "2025-03-08 05:00:00+00:00")
            self.assertAlmostEqual(p["value"].iloc[0], round(float(df[col].iloc[0]), 2), places=6)
            spring = p[(p["ts"] >= "2025-03-09T05:00:00Z") & (p["ts"] < "2025-03-10T04:00:00Z")]
            self.assertEqual(len(spring), 23)
            self.assertTrue((spring["ts"].diff().dropna() == pd.Timedelta(hours=1)).all())   # the line "03" is placed by its end
            autumn = p[(p["ts"] >= "2025-11-02T04:00:00Z") & (p["ts"] < "2025-11-03T05:00:00Z")]
            self.assertEqual(len(autumn), 25)
            x = df[(df["Date"] == "2025-11-02") & (df["Hr_End"] == "02X")][col].iloc[0]
            self.assertAlmostEqual(autumn.set_index("ts")["value"][pd.Timestamp("2025-11-02T06:00:00Z")], round(float(x), 2), places=6)

    def test_caiso_day_ahead_keeps_the_lmp_lines_at_their_gmt_start(self):
        for day, hours, first in (("20250309", 23, "2025-03-09 08:00:00+00:00"), ("20251102", 25, "2025-11-02 07:00:00+00:00")):
            got, k, n = zh.parse_caiso(raw(f"caiso_PRC_LMP_DAM_{day}_sample.zip"), "caiso_dam")
            p = got["caiso_dam"].sort_values("ts")
            self.assertEqual((len(p), k, n), (hours, hours, 2 * hours), day)                 # the sample holds LMP and MCC lines
            self.assertEqual(set(p["entity"]), {"caiso:TH_ZP26_GEN-APND"})
            self.assertEqual(str(p["ts"].iloc[0]), first)
            self.assertTrue((p["ts"].diff().dropna() == pd.Timedelta(hours=1)).all())

    def test_caiso_real_time_is_the_mean_of_three_and_never_of_two(self):
        content = raw("caiso_PRC_INTVL_LMP_RTM_20251102_sample.zip")
        got, k, n = zh.parse_caiso(content, "caiso_rtm")
        p = got["caiso_rtm"].sort_values("ts").reset_index(drop=True)
        z = zipfile.ZipFile(io.BytesIO(content))
        name = z.namelist()[0]
        df = pd.read_csv(io.BytesIO(z.read(name)))
        lmp = df[df["LMP_TYPE"] == "LMP"].sort_values("INTERVALSTARTTIME_GMT")
        self.assertEqual(k, len(lmp))
        self.assertEqual(len(p), len(lmp) // 3)
        col = "MW" if "MW" in lmp.columns else "VALUE"
        self.assertAlmostEqual(p["value"].iloc[0], round(lmp[col].iloc[:3].mean(), 4), places=6)
        self.assertTrue((p["ts"].diff().dropna() == pd.Timedelta(minutes=15)).all())
        # one 5-minute line taken away: its quarter hour is not written, the others stand
        short = df.drop(lmp.index[4])
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as o:
            o.writestr(name, short.to_csv(index=False))
        q, _, _ = zh.parse_caiso(buf.getvalue(), "caiso_rtm")
        self.assertEqual(len(q["caiso_rtm"]), len(p) - 1)
        self.assertNotIn(p["ts"].iloc[1], set(q["caiso_rtm"]["ts"]))

    def test_caiso_refusal_is_read_as_one(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as o:
            o.writestr("INVALID_REQUEST.xml", "<m:ERR_CODE>1015</m:ERR_CODE><m:ERR_DESC>GroupZip DownLoad is in Processing, Please Submit request after Sometime.</m:ERR_DESC>")
        self.assertIn("1015", zh.caiso_error(buf.getvalue()))
        self.assertEqual(zh.caiso_error(raw("caiso_PRC_LMP_DAM_20250309_sample.zip")), "")

    def test_spp_keeps_the_hub_at_the_hour_before_its_gmt_end(self):
        names = sorted(f for f in os.listdir(FIX) if f.startswith("spp_DA-LMP-SL-"))
        self.assertEqual(len(names), 2)            # SPP's two ways of naming columns and writing the hour: 4 June and 1 October 2026
        self.assertTrue(text(names[0]).startswith("INTERVAL,GMTINTERVALEND,BAA,SETTLEMENT_LOCATION"))
        self.assertTrue(text(names[1]).startswith("Interval,GMTIntervalEnd,BAA,Settlement Location"))
        for name in names:
            body = raw(name)
            for content in (body, gzip.compress(body)):
                got, k, n = zh.parse_spp(content, "spp_dam")
                p = got["spp_dam"].sort_values("ts")
                self.assertEqual(set(p["entity"]), {"spp:SPPSOUTH_HUB"})
                self.assertEqual(n, 3 * k)                                                  # the sample holds three settlement locations
                self.assertTrue((p["ts"].diff().dropna() == pd.Timedelta(hours=1)).all())
                line = [ln for ln in body.decode("utf-8").splitlines() if ",SPPSOUTH_HUB," in ln][0].split(",")
                end = pd.to_datetime(line[1], format="%m/%d/%Y %H:%M:%S" if line[1].count(":") == 2 else "%m/%d/%Y %H:%M").tz_localize("UTC")
                self.assertAlmostEqual(p.set_index("ts")["value"][end - pd.Timedelta(hours=1)], float(line[5]), places=6)
            day = name.split("-")[3][:8]
            want = {"20260308": 23, "20250309": 23, "20251102": 25}.get(day, 24)
            self.assertEqual(k, want, name)


class Pull(Sandbox):
    def test_the_ceiling_stops_before_the_request(self):
        self.serve(lambda url: Response(200, nyiso_zip("damlbmp"), {"Last-Modified": "Mon, 01 Dec 2025 10:00:00 GMT"}))
        zh.CEILING = 100                                   # a month's file is taken to hold 8,525 rows: no request at all
        out = zh.pull(["nyiso"], first="2025-03-01", log=lambda m: None)
        self.assertTrue(out["nyiso"].startswith("ceiling"), out)
        self.assertEqual(self.calls, [])
        zh.CEILING = 8525 + 50                             # room for one file; the file gives 96 rows, so the second is not asked for
        out = zh.pull(["nyiso"], first="2025-03-01", log=lambda m: None)
        self.assertTrue(out["nyiso"].startswith("ceiling"), out)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(zh.counted()[0], 96)
        self.assertEqual(zh.counted()[2], 1)

    def test_a_paused_publisher_is_never_asked(self):
        self.serve(lambda url: Response(200, nyiso_zip("damlbmp")))
        real = ip.paused
        ip.paused = lambda scope: {"scope": "nyiso", "paused_on": "2026-10-07", "reason": "a test", "terms_url": "x", "until": "a review"} if scope == "nyiso" else real(scope)
        out = zh.pull(["nyiso"], first="2026-09-01", log=lambda m: None)
        self.assertEqual(self.calls, [])
        self.assertTrue(out["nyiso"].startswith("paused"))
        self.assertFalse(os.path.exists(zh.manifest_path("nyiso")))

    def test_miso_and_pjm_have_no_pull(self):
        self.assertEqual(sorted(zh.PULLS), ["caiso", "isone", "nyiso", "spp"])
        with self.assertRaises(SystemExit):
            zh.main(["--pull", "--iso", "miso"])

    def test_a_refusal_stops_the_publisher_and_is_not_tried_again(self):
        self.serve(lambda url: Response(403, b"Forbidden"))
        out = zh.pull(["nyiso"], first="2026-09-01", log=lambda m: None)
        self.assertTrue(out["nyiso"].startswith("blocked"), out)
        self.assertEqual(len(self.calls), 1)

    def test_a_page_where_a_file_was_expected_stops_the_publisher(self):
        self.serve(lambda url: Response(200, b"<html><body>Please verify you are a human</body></html>"))
        out = zh.pull(["nyiso"], first="2026-09-01", log=lambda m: None)
        self.assertTrue(out["nyiso"].startswith("blocked"), out)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(zh.held("nyiso"), {})

    def test_a_kept_file_is_not_asked_for_again(self):
        self.serve(lambda url: Response(200, nyiso_zip("rtlbmp" if "rtlbmp" in url else "damlbmp")))
        first = (pd.Timestamp.now(tz="UTC").tz_localize(None).normalize().replace(day=1) - pd.offsets.MonthBegin(3)).strftime("%Y-%m-%d")
        zh.pull(["nyiso"], first=first, log=lambda m: None)
        n = len(self.calls)
        self.assertEqual(n, 8)                             # four months, two reports
        zh.pull(["nyiso"], first=first, log=lambda m: None)
        self.assertEqual(len(self.calls), n)               # finished months are final; this month's file is less than 20 hours old
        rows = zh.manifest("nyiso")
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(r["sha256"] and r["bytes"] and r["url"].startswith("http://mis.nyiso.com/public/csv/") for r in rows))

    def test_the_weekly_run_is_counted_apart_and_never_starts_a_table(self):
        self.serve(lambda url: Response(200, nyiso_zip("rtlbmp" if "rtlbmp" in url else "damlbmp")))
        zh.REFRESH = True
        try:
            out = zh.pull(["nyiso"], first=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-01"), log=lambda m: None)
            self.assertTrue(out["nyiso"].startswith("ok"), out)
            self.assertEqual(len(self.calls), 2)
            self.assertTrue(all(r["note"].startswith("refresh") for r in zh.manifest("nyiso")))
            self.assertEqual(zh.counted()[0], 0)               # not rows of the history pull: its ceiling is not spent by the weekly run
            self.assertEqual(zh.RUN["rows"], 2 * 96)
            zh.RUN["rows"] = zh.REFRESH_CEILING                # a run that has read its 250,000 rows asks for nothing more
            with self.assertRaises(zh.CeilingStop):
                zh.ask(1, "one more file")
            out_dir = os.path.join(self.tmp, "out")
            self.assertEqual(zh.write(["nyiso"], out_dir, recent=9), 1)
            self.assertFalse(os.path.exists(os.path.join(out_dir, zh.NAME + ".csv")))
        finally:
            zh.REFRESH = False

    def test_a_404_is_recorded_and_the_pull_goes_on(self):
        self.serve(lambda url: Response(404) if "damlbmp" in url else Response(200, nyiso_zip("rtlbmp")))
        first = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-01")
        out = zh.pull(["nyiso"], first=first, log=lambda m: None)
        self.assertTrue(out["nyiso"].startswith("ok"), out)
        self.assertEqual([r["status"] for r in zh.manifest("nyiso")], ["404", "200"])


class Table(Sandbox):
    def workbook(self):
        """A workbook of the eight load zones' sheets, each holding the real CT sample's lines (the test's own
        container: ISO-NE's year is 8 MB)."""
        df = pd.read_csv(os.path.join(FIX, "isone_smd_hourly_2025_CT_sample.csv"), dtype={"Hr_End": str})
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            for sheet in zh.ISONE_SHEETS:
                df.to_excel(w, sheet_name=sheet, index=False)
        return buf.getvalue()

    def fill(self):
        for kind, market in (("damlbmp", "nyiso_dam"), ("rtlbmp", "nyiso_rtm")):
            zh.save("nyiso", f"20250301{kind}_zone_csv.zip", nyiso_zip(kind), market, "2025-03", f"http://mis.nyiso.com/public/csv/{kind}/20250301{kind}_zone_csv.zip",
                    {"Last-Modified": "Mon, 01 Dec 2025 10:00:00 GMT"})
        zh.save("caiso", "PRC_LMP_DAM_20251101_20251201.zip", raw("caiso_PRC_LMP_DAM_20251102_sample.zip"), "caiso_dam", "2025-11", "https://oasis.caiso.com/oasisapi/SingleZip?x=1", {})
        zh.save("caiso", "PRC_INTVL_LMP_RTM_20251101_20251201.zip", raw("caiso_PRC_INTVL_LMP_RTM_20251102_sample.zip"), "caiso_rtm", "2025-11", "https://oasis.caiso.com/oasisapi/SingleZip?x=2", {})
        zh.save("spp", "DA-LMP-SL-202610010100.csv.gz", raw("spp_DA-LMP-SL-202610010100_sample.csv"), "spp_dam", "2026-10-01", "https://portal.spp.org/file-browser-api/download/x?path=/y.csv", {})
        zh.save("isone", "2025_smd_hourly.xlsx", self.workbook(), "isone_dam", "2025", "https://www.iso-ne.com/static-assets/documents/100020/2025_smd_hourly.xlsx", {})

    def test_two_tables_by_license_built_from_the_saved_files_and_a_second_write_adds_nothing(self):
        import erw_validate
        self.fill()
        out = os.path.join(self.tmp, "out")
        self.assertEqual(zh.write(["nyiso", "isone", "caiso", "spp"], out), 0)
        public, internal = os.path.join(out, zh.NAME + ".csv"), os.path.join(out, zh.NAME_ISONE + ".csv")
        self.assertEqual((zh.NAME, zh.NAME_ISONE), ("iso_zone_prices_history", "isone_zone_prices_history"))
        s, e = ip.read_series(public), ip.read_series(internal)
        # the public table: NYISO, CAISO and SPP only, and no ISO-NE row by market, entity, source or address
        self.assertEqual(sorted(s["market"].unique()), ["caiso_dam", "caiso_rtm", "nyiso_dam", "nyiso_rtm", "spp_dam"])
        self.assertEqual(sorted(s["entity"].str.split(":").str[0].unique()), ["caiso", "nyiso", "spp"])
        self.assertEqual(sorted(s["source"].unique()), ["caiso:PRC_INTVL_LMP", "caiso:PRC_LMP", "nyiso:damlbmp", "nyiso:rtlbmp", "spp:DA-LMP-SL"])
        for col in ("entity", "market", "node", "source", "source_url"):
            self.assertFalse(s[col].str.contains("isone|iso-ne", case=False).any(), col)
        self.assertTrue(all(zh.SOURCES[x]["license"] == "public" for x in s["source"].unique()))
        # the internal table: ISO-NE's two markets only, and no row of another grid
        self.assertEqual(sorted(e["market"].unique()), ["isone_dam", "isone_rtm"])
        self.assertTrue(e["entity"].str.startswith("isone:.Z.").all())
        self.assertEqual(e["entity"].nunique(), 8)
        self.assertEqual(set(e["source"]), {"isone:smd_hourly_lmp"})
        self.assertEqual(zh.SOURCES["isone:smd_hourly_lmp"]["license"], "internal")
        self.assertEqual(len(e), 2 * 8 * 72)
        self.assertEqual(list(s.columns), list(e.columns))
        # what was true of the one table
        self.assertEqual(len(s[s["market"] == "nyiso_dam"]), 2 * (23 + 25))
        self.assertEqual(set(s[s["market"] == "nyiso_rtm"]["variable"]), {"lmp_rtm"})
        self.assertEqual(set(s[s["market"] == "caiso_rtm"]["freq"]), {"PT15M"})
        self.assertEqual(len(s[s["market"] == "spp_dam"]), 24)
        heads = {}
        for path, t in ((public, s), (internal, e)):
            self.assertFalse(t.duplicated(ip.SERIES_KEY).any())
            self.assertTrue(t["source_url"].str.startswith("http").all() and (t["retrieved_at"] != "").all())
            self.assertEqual(erw_validate.validate(path)["errors"], [])
            with open(path, encoding="utf-8") as f:
                heads[path] = [ln for ln in f if ln.startswith("#")]
        # each header says what it holds and names the other; only the internal one declares a license, and it is internal
        self.assertIn(zh.NAME_ISONE, heads[public][0])
        self.assertIn(zh.NAME, heads[internal][0].replace(zh.NAME_ISONE, ""))
        self.assertTrue(any(ln.startswith("# License: internal.") for ln in heads[internal]))
        self.assertFalse(any(ln.startswith("# License:") for ln in heads[public]))
        self.assertFalse(any(ln.startswith("# Source: isone") for ln in heads[public]))
        self.assertEqual([ln.split()[2] for ln in heads[internal] if ln.startswith("# Source: ")], ["isone:smd_hourly_lmp"])
        reg = pd.read_csv(os.path.join(out, "metadata", "sources.csv"), dtype=str, keep_default_na=False).set_index("source")
        self.assertEqual(reg.loc["isone:smd_hourly_lmp", ["license", "tables"]].tolist(), ["internal", zh.NAME_ISONE])
        self.assertTrue(all(reg.loc[x, "tables"] == zh.NAME and reg.loc[x, "license"] == "public" for x in reg.index if not x.startswith("isone")))
        # a second write of the same files adds nothing to either
        self.assertEqual(zh.write(["nyiso", "isone", "caiso", "spp"], out), 0)
        for path, t in ((public, s), (internal, e)):
            again = ip.read_series(path)
            pd.testing.assert_frame_equal(t[ip.SERIES_COLS], again[ip.SERIES_COLS])
            with open(path, encoding="utf-8") as f:
                head = [ln for ln in f if ln.startswith("#")]
            self.assertTrue(any("0 new" in ln and f"{len(t)} replacing" in ln for ln in head))
        self.assertFalse(any(x.endswith((".part", ".body", ".tmp")) for x in os.listdir(out)))
        # a run of one publisher writes its own table only and leaves the other as it is
        before = os.path.getmtime(public)
        self.assertEqual(zh.write(["isone"], out), 0)
        self.assertEqual(os.path.getmtime(public), before)

    def test_a_row_of_another_table_is_refused(self):
        self.fill()
        parts, _ = zh.build(["nyiso", "isone"], lambda m: None)
        out = os.path.join(self.tmp, "out")
        ip.set_out_dir(out)
        header = lambda held: ["a test"]  # noqa: E731
        with self.assertRaises(RuntimeError):                    # an ISO-NE market into the public table
            zh.write_table(zh.NAME, {"isone_dam": parts["isone_dam"]}, header, lambda m: None)
        with self.assertRaises(RuntimeError):                    # another grid's market into the internal table
            zh.write_table(zh.NAME_ISONE, {"nyiso_dam": parts["nyiso_dam"]}, header, lambda m: None)
        with self.assertRaises(RuntimeError):                    # ISO-NE's rows under another market's name
            zh.write_table(zh.NAME, {"nyiso_dam": parts["isone_dam"].assign(market="nyiso_dam")}, header, lambda m: None)
        self.assertEqual([f for f in os.listdir(out) if f.endswith(".csv")], [])
        # a public table that already held an ISO-NE row is not merged into
        zh.write_table(zh.NAME_ISONE, {"isone_dam": parts["isone_dam"]}, header, lambda m: None)
        os.replace(os.path.join(out, zh.NAME_ISONE + ".csv"), os.path.join(out, zh.NAME + ".csv"))
        with self.assertRaises(RuntimeError):
            zh.write_table(zh.NAME, {"nyiso_dam": parts["nyiso_dam"]}, header, lambda m: None)

    def test_every_market_has_one_table(self):
        listed = [m for ms in zh.TABLES.values() for m in ms]
        self.assertEqual(sorted(listed), sorted(zh.MARKETS))
        self.assertEqual(len(listed), len(set(listed)))
        self.assertEqual(zh.TABLES[zh.NAME_ISONE], ["isone_dam", "isone_rtm"])
        self.assertTrue(all(zh.SOURCES[zh.MARKETS[m][3]]["license"] == "public" for m in zh.TABLES[zh.NAME]))

    def test_an_hour_the_file_does_not_hold_is_counted_and_never_filled(self):
        self.fill()
        parts, _ = zh.build(["nyiso"], lambda m: None)
        s = parts["nyiso_dam"]
        short = s[~((s["entity"] == "nyiso:WEST") & (s["ts_utc"] == "2025-03-09T12:00:00Z"))]
        g = zh.gaps(short, "nyiso_dam")
        both = zh.gaps(s, "nyiso_dam")
        self.assertEqual(g["nyiso:WEST"][3], both["nyiso:WEST"][3] + 1)
        self.assertEqual(g["nyiso:WEST"][0], both["nyiso:WEST"][0] - 1)

    def test_a_zone_hour_given_twice_with_two_prices_is_not_written(self):
        t = pd.Timestamp("2025-03-09T05:00:00Z")
        piece = pd.DataFrame({"entity": ["a", "a", "a", "a"], "node": ["a"] * 4, "ts": [t, t, t + pd.Timedelta(hours=1), t + pd.Timedelta(hours=1)], "value": [1.0, 1.0, 2.0, 3.0]})
        kept, differ = zh.once(piece)
        self.assertEqual((len(kept), differ), (1, 1))
        self.assertEqual(kept["value"].tolist(), [1.0])


class Check(unittest.TestCase):
    def frames(self):
        ts = pd.date_range("2026-09-01T04:00:00Z", periods=48, freq="1h")
        v = [20 + (i * 7) % 31 + 0.01 * i for i in range(48)]
        return pd.DataFrame({"entity": "nyiso:WEST", "ts": ts, "value": v})

    def test_the_same_hour_matches_and_a_shifted_one_does_not(self):
        mine = self.frames()
        r = zh.check_market(mine, mine.copy(), "nyiso_dam")
        self.assertEqual(r[0]["joined"], 48)
        self.assertEqual(r[0]["exact"], 1.0)
        self.assertLess(r[1]["exact"], 0.1)
        late = mine.assign(ts=mine["ts"] + pd.Timedelta(hours=1))        # a history written one hour late is found at lag -1, not at 0
        r = zh.check_market(late, mine.copy(), "nyiso_dam")
        self.assertLess(r[0]["exact"], 0.1)
        self.assertEqual(r[-1]["exact"], 1.0)

    def test_a_join_that_fans_out_fails(self):
        mine = self.frames()
        live = pd.concat([mine, mine.iloc[:3]], ignore_index=True)
        with self.assertRaises(AssertionError):
            zh.check_market(mine, live, "nyiso_dam")


class House(unittest.TestCase):
    def test_no_em_dash_and_the_fixtures_are_small(self):
        for p in (os.path.join(ROOT, "warehouse", "connectors", "zone_price_history.py"), os.path.abspath(__file__)):
            with open(p, encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), p)
        size = sum(os.path.getsize(os.path.join(FIX, f)) for f in os.listdir(FIX))
        self.assertLess(size, 300_000)

    def test_the_table_reads_as_the_comparison_reads_prices(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import price_compare as pc
        for market, (iso, variable, freq, source) in zh.MARKETS.items():
            self.assertIn(variable, pc.DAM_VARS if market.endswith("_dam") else pc.RTM_VARS, market)
            self.assertIn(freq, ("PT1H", "PT15M"))
            self.assertIn(source, zh.SOURCES)
        self.assertEqual(zh.SOURCES["isone:smd_hourly_lmp"]["license"], "internal")


if __name__ == "__main__":
    unittest.main()
