"""Session 140: ERCOT's load zone prices (warehouse/connectors/ercot_zone_prices.py).

No request is made and nothing is written under warehouse/output. The parser reads two short workbooks cut from the
real 2015 files of NP4-180-ER and NP6-785-ER (tests/fixtures/session140/, made by
runs/session140/ercot_zones/make_fixtures.py): every line of 8 March 2015, the 23-hour day, and of 1 November 2015,
the 25-hour day. hub_rows_two_days.csv holds the hub history's own rows of those two days: the hubs of the fixture,
read by this connector's code, must equal them."""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import ercot_zone_prices as z  # noqa: E402
import erw_validate  # noqa: E402
import iso_prices as ip  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session140")
SPRING = pd.date_range("2015-03-08T06:00:00Z", "2015-03-09T05:00:00Z", freq="1h", inclusive="left")    # 23 hours
AUTUMN = pd.date_range("2015-11-01T05:00:00Z", "2015-11-02T06:00:00Z", freq="1h", inclusive="left")    # 25 hours


def fixture(market):
    with open(os.path.join(FIX, f"{market}_2015_two_days.xlsx"), "rb") as f:
        return f.read()


def args(**kw):
    base = dict(offline=False, years=None, markets=None, ceiling=z.CEILING, hub_table=None, out_dir=None)
    base.update(kw)
    return argparse.Namespace(**base)


class Answer:
    def __init__(self, content, status=200):
        self.content, self.status_code = content, status

    def json(self):
        return json.loads(self.content)


def listing(report_type, years):
    docs = [{"Document": {"DocID": str(1000 + y), "ConstructedName": f"rpt.000{report_type}.0000000000000000.X_{y}.zip",
                          "FriendlyName": f"X_{y}", "PublishDate": f"{y + 1}-01-01T08:00:00-06:00", "ContentSize": "0"}}
            for y in years]
    return json.dumps({"ListDocsByRptTypeRes": {"DocumentList": docs}}).encode()


class Getter:
    """Stands for requests.get: answers ERCOT's list with a made-up list of document names and ids (no data), and a
    document with the real fixture workbook. Keeps every address asked."""

    def __init__(self, years, market):
        self.years, self.market, self.asked = years, market, []

    def __call__(self, url, **kw):
        self.asked.append(url)
        if "IceDocListJsonWS" in url:
            return Answer(listing(url.rsplit("=", 1)[1], self.years))
        return Answer(fixture(self.market))


def save_copy(raw, market, year, doc, when="2026-10-07T09:00:00Z", published="2016-01-01T08:03:08-05:00"):
    """A fixture workbook in a raw directory as --pull would have saved it."""
    content = fixture(market)
    name = f"{market}_{year}_{doc}.zip"
    with open(os.path.join(raw, name), "wb") as f:
        f.write(content)
    z._append_csv(os.path.join(raw, "manifest.csv"), z.MANIFEST_COLS,
                  {"market": market, "year": year, "file": name, "doc_id": doc, "url": z.FILE_URL.format(doc=doc),
                   "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(), "published": published,
                   "friendly_name": "", "retrieved_at": when, "how": "requested"})


class Lists(unittest.TestCase):
    def test_the_zones(self):
        self.assertEqual(z.COMPETITIVE_ZONES, ["LZ_HOUSTON", "LZ_NORTH", "LZ_SOUTH", "LZ_WEST"])
        self.assertEqual(sorted(z.LOAD_ZONES), sorted(["LZ_HOUSTON", "LZ_NORTH", "LZ_SOUTH", "LZ_WEST", "LZ_AEN", "LZ_CPS", "LZ_LCRA", "LZ_RAYBN"]))
        self.assertEqual(z.MARKETS["dam"]["zones"], z.LOAD_ZONES)            # day-ahead: all eight
        self.assertEqual(z.MARKETS["rtm"]["zones"], z.COMPETITIVE_ZONES)     # real time: the four competitive zones
        for cfg in z.MARKETS.values():
            self.assertFalse([p for p in cfg["zones"] if not p.startswith("LZ_") or p.startswith("LZ_DC")])
            self.assertFalse(set(cfg["zones"]) & set(z.HUBS))

    def test_the_table_is_shaped_as_the_hub_history(self):
        self.assertEqual(z.COLS, ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source",
                                  "source_url", "retrieved_at", "vintage", "year"])
        self.assertEqual((z.MARKETS["dam"]["variable"], z.MARKETS["dam"]["freq"], z.MARKETS["dam"]["market"]), ("spp_dam", "PT1H", "ercot_dam"))
        self.assertEqual((z.MARKETS["rtm"]["variable"], z.MARKETS["rtm"]["freq"], z.MARKETS["rtm"]["market"]), ("spp_rtm", "PT15M", "ercot_rtm"))
        self.assertEqual(z.TABLE, "ercot_zone_prices_history")
        self.assertEqual(z.CEILING, 3_000_000)

    def test_the_whole_history_fits_under_the_ceiling(self):
        most = sum(z.bound(m, y) for m in z.MARKETS for y in range(z.FIRST_YEAR, 2027))
        self.assertLess(most, z.CEILING)
        self.assertEqual(z.bound("dam", 2015), 8760 * 8)
        self.assertEqual(z.bound("rtm", 2016), 8784 * 4 * 4)


class Parser(unittest.TestCase):
    def test_day_ahead(self):
        lines, stats = z.read_workbook(fixture("dam"), "dam")
        self.assertEqual(stats["rows_read"], 672)                             # 14 settlement points x (23 + 25) hours
        self.assertEqual(len(stats["points"]), 14)
        rows, notes = z.shape(lines, "dam", 2015)
        self.assertEqual(len(rows), 8 * 48)
        self.assertEqual(notes["blank_prices"], 0)
        for zone in z.LOAD_ZONES:
            have = pd.DatetimeIndex(rows.loc[rows["node"] == zone, "interval_start"])
            self.assertEqual(list(have), list(SPRING) + list(AUTUMN), zone)   # 23 hours, then 25, each once, in UTC
        h = rows[rows["node"] == "LZ_HOUSTON"].set_index("interval_start")["value"]
        self.assertEqual(h[pd.Timestamp("2015-11-01T06:00:00Z")], 15.55)      # hour ending 2, Repeated Hour Flag N: 01:00 CDT
        self.assertEqual(h[pd.Timestamp("2015-11-01T07:00:00Z")], 15.34)      # hour ending 2, flag Y: 01:00 CST
        self.assertEqual(h[pd.Timestamp("2015-11-01T08:00:00Z")], 13.26)      # hour ending 3
        self.assertEqual(h[pd.Timestamp("2015-03-08T07:00:00Z")], 18.03)      # hour ending 2 of the spring day
        self.assertEqual(h[pd.Timestamp("2015-03-08T08:00:00Z")], 17.71)      # hour ending 4: ERCOT skips hour ending 3

    def test_real_time(self):
        lines, stats = z.read_workbook(fixture("rtm"), "rtm")
        self.assertEqual(stats["rows_read"], 4224)                            # 22 point and type pairs x (92 + 100) intervals
        self.assertEqual(stats["empty_sheets"], 1)                            # a month to come: read as empty, not an error
        self.assertEqual(stats["points"]["LZ_HOUSTON|LZ"], 192)
        self.assertEqual(stats["points"]["LZ_HOUSTON|LZEW"], 192)             # the zone's second row, left in the file
        rows, _ = z.shape(lines, "rtm", 2015)
        self.assertEqual(sorted(rows["node"].unique()), sorted(z.COMPETITIVE_ZONES))
        self.assertEqual(len(rows), 4 * (92 + 100))
        want = list(pd.date_range(SPRING[0], periods=92, freq="15min")) + list(pd.date_range(AUTUMN[0], periods=100, freq="15min"))
        for zone in z.COMPETITIVE_ZONES:
            self.assertEqual(list(rows.loc[rows["node"] == zone, "interval_start"]), want, zone)
        h = rows[rows["node"] == "LZ_HOUSTON"].set_index("interval_start")["value"]
        self.assertEqual([h[pd.Timestamp(t)] for t in ("2015-11-01T06:45:00Z", "2015-11-01T07:00:00Z", "2015-11-01T07:45:00Z", "2015-11-01T08:00:00Z")],
                         [18.79, 18.47, 18.00, 17.80])
        self.assertEqual([h[pd.Timestamp(t)] for t in ("2015-03-08T07:45:00Z", "2015-03-08T08:00:00Z")], [16.40, 16.58])

    def test_the_lz_row_is_taken_and_the_lzew_row_left(self):
        lines, _ = z.read_workbook(fixture("rtm"), "rtm")
        one = lines[(lines["point"] == "LZ_LCRA") & (lines["date"] == "2015-03-08") & (lines["he"] == 2) & (lines["interval"] == 2)]
        self.assertEqual(sorted(zip(one["ptype"], one["price"].astype(float))), [("LZ", 16.04), ("LZEW", 16.05)])
        rows, _ = z.shape(lines, "rtm", 2015, zones=["LZ_LCRA"])
        self.assertEqual(len(rows), 192)
        self.assertEqual(rows.set_index("interval_start")["value"][pd.Timestamp("2015-03-08T07:15:00Z")], 16.04)

    def test_the_hubs_of_the_same_workbooks_equal_the_hub_history(self):
        hub = pd.read_csv(os.path.join(FIX, "hub_rows_two_days.csv"))
        hub["ts"] = pd.to_datetime(hub["ts_utc"], utc=True)
        for market, n in (("dam", 6 * 48), ("rtm", 6 * 192)):
            lines, _ = z.read_workbook(fixture(market), market)
            mine, _ = z.shape(lines, market, 2015, zones=z.HUBS)
            theirs = hub[hub["variable"] == z.MARKETS[market]["variable"]]
            self.assertEqual((len(mine), len(theirs)), (n, n))
            j = theirs.merge(mine, left_on=["node", "ts"], right_on=["node", "interval_start"], how="outer", validate="one_to_one")
            self.assertEqual(len(j), n)                                       # the same hubs and the same UTC intervals
            self.assertEqual(float((j["value_x"] - j["value_y"]).abs().max()), 0.0)

    def test_nothing_is_guessed_at_the_clock_change(self):
        ok = pd.DataFrame({"date": ["2015-11-01", "2015-11-01"], "he": [2, 2], "interval": [1, 1], "flag": ["N", "Y"]})
        self.assertEqual([ip.utc_iso(t) for t in z.interval_start(ok)], ["2015-11-01T06:00:00Z", "2015-11-01T07:00:00Z"])
        with self.assertRaises(RuntimeError):                                 # a Y that is not the repeated hour
            z.interval_start(pd.DataFrame({"date": ["2015-11-01"], "he": [5], "interval": [1], "flag": ["Y"]}))
        with self.assertRaises(Exception):                                    # 02:00 on the spring day does not exist
            z.interval_start(pd.DataFrame({"date": ["2015-03-08"], "he": [3], "interval": [1], "flag": ["N"]}))
        with self.assertRaises(RuntimeError):
            z.interval_start(pd.DataFrame({"date": ["2015-06-01"], "he": [25], "interval": [1], "flag": ["N"]}))
        with self.assertRaises(RuntimeError):
            z.interval_start(pd.DataFrame({"date": ["2015-06-01"], "he": [1], "interval": [1], "flag": [""]}))

    def test_a_blank_price_is_not_written_and_two_prices_stop_the_year(self):
        lines, _ = z.read_workbook(fixture("dam"), "dam")
        blank = lines.astype({"price": object})
        i = blank.index[blank["point"] == "LZ_WEST"][0]
        blank.loc[i, "price"] = ""
        rows, notes = z.shape(blank, "dam", 2015)
        self.assertEqual((len(rows), notes["blank_prices"]), (8 * 48 - 1, 1))  # missing stays missing
        twice = pd.concat([lines, lines[lines["point"] == "LZ_WEST"].head(1).assign(price=999.0)], ignore_index=True)
        with self.assertRaises(RuntimeError):
            z.shape(twice, "dam", 2015)
        with self.assertRaises(RuntimeError):                                 # a workbook of another year
            z.shape(lines, "dam", 2016)


class Pull(unittest.TestCase):
    def setUp(self):
        self.raw = tempfile.mkdtemp(prefix="erw_s140_raw_")
        self.addCleanup(shutil.rmtree, self.raw, ignore_errors=True)
        self.lines = []

    def log(self, m):
        self.lines.append(str(m))

    def test_it_stops_before_the_file_that_would_pass_the_ceiling(self):
        get = Getter([2015, 2016], "dam")
        a = args(years=[2015, 2016], markets=["dam"], ceiling=z.bound("dam", 2015) + 10)
        rc = z.pull(a, self.log, get=get, sleep=lambda s: None, raw=self.raw)
        self.assertEqual(rc, 3)
        files = [u for u in get.asked if "mirDownload" in u]
        self.assertEqual(files, [z.FILE_URL.format(doc="3015")])               # 2015 asked; 2016 never requested
        self.assertTrue(any(line.startswith("STOPPED before dam 2016") for line in self.lines))
        self.assertEqual([m["year"] for m in z.manifest(self.raw)], ["2015"])
        self.assertLessEqual(z.counted(self.raw), a.ceiling)

    def test_a_ceiling_below_the_first_file_requests_no_file(self):
        get = Getter([2015], "rtm")
        rc = z.pull(args(years=[2015], markets=["rtm"], ceiling=z.bound("rtm", 2015) - 1), self.log, get=get, sleep=lambda s: None, raw=self.raw)
        self.assertEqual(rc, 3)
        self.assertFalse([u for u in get.asked if "mirDownload" in u])
        self.assertEqual(z.manifest(self.raw), [])

    def test_a_held_year_is_never_asked_for_twice(self):
        get = Getter([2015], "dam")
        a = args(years=[2015], markets=["dam"])
        self.assertEqual(z.pull(a, self.log, get=get, sleep=lambda s: None, raw=self.raw), 0)
        self.assertEqual(z.pull(a, self.log, get=get, sleep=lambda s: None, raw=self.raw), 0)
        self.assertEqual(len([u for u in get.asked if "mirDownload" in u]), 1)
        self.assertEqual(len(z.manifest(self.raw)), 1)
        with open(os.path.join(self.raw, "requests.csv"), encoding="utf-8") as f:
            self.assertEqual(len(f.read().strip().splitlines()), 1 + 3)        # every request is written down: two lists, one file

    def test_a_year_still_growing_is_asked_again_and_a_finished_year_is_not(self):
        save_copy(self.raw, "dam", 2015, "77", published="2015-10-04T08:01:37-05:00")     # a copy from within its year
        get = Getter([2015], "dam")
        a = args(years=[2015], markets=["dam"])
        self.assertEqual(z.pull(a, self.log, get=get, sleep=lambda s: None, raw=self.raw), 0)
        self.assertEqual([u for u in get.asked if "mirDownload" in u], [z.FILE_URL.format(doc="3015")])
        self.assertEqual([m["doc_id"] for m in z.manifest(self.raw)], ["77", "3015"])
        self.assertEqual(z.pull(a, self.log, get=get, sleep=lambda s: None, raw=self.raw), 0)   # that document is held now
        self.assertEqual(len([u for u in get.asked if "mirDownload" in u]), 1)
        other = tempfile.mkdtemp(prefix="erw_s140_raw_")
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        save_copy(other, "dam", 2015, "88", published="2016-01-01T08:03:08-05:00")        # the year's final copy
        get = Getter([2015], "dam")
        self.assertEqual(z.pull(a, self.log, get=get, sleep=lambda s: None, raw=other), 0)
        self.assertFalse([u for u in get.asked if "mirDownload" in u])

    def test_the_count_is_the_kept_rows_and_a_repeat_counts_once(self):
        # Session 149 (the owner's ruling of 7 October 2026 on the refresh, read narrowly: a row counts once). Until
        # then this test was "a repeat counts again", and the second copy made the count 2 * 8 * 48
        save_copy(self.raw, "dam", 2015, "1")
        self.assertEqual(z.counted(self.raw), z.bound("dam", 2015))            # not read yet: the most it can hold
        z.parsed(z.manifest(self.raw)[0], self.log, self.raw)
        self.assertEqual(z.counted(self.raw), 8 * 48)                          # read: what it holds
        self.assertEqual(z.counts(self.raw)[z.manifest(self.raw)[0]["sha256"]]["rows_read"], 672)
        save_copy(self.raw, "dam", 2015, "2")                                  # a second copy of the year, the same rows
        self.assertEqual(z.counted(self.raw), 8 * 48)                          # the rows of a workbook downloaded again are not counted again

    def test_a_paused_publisher_is_not_requested(self):
        def get(url, **kw):
            raise AssertionError("a request was made to a paused publisher")
        row = {"scope": "ercot", "paused_on": "2026-10-07", "reason": "a test", "terms_url": "https://example.org", "until": "a review"}
        with mock.patch.object(ip, "paused_rows", return_value=[row]):
            self.assertEqual(ip.paused("ercot"), row)
            self.assertEqual(z.pull(args(), self.log, get=get, sleep=lambda s: None, raw=self.raw), 0)
        self.assertTrue(any("PAUSED since 2026-10-07" in line for line in self.lines))
        self.assertFalse(os.path.exists(os.path.join(self.raw, "requests.csv")))

    def test_the_pause_is_asked_before_any_request(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "ercot_zone_prices.py"), encoding="utf-8") as f:
            code = f.read()
        body = code[code.index("def pull("):code.index("# Reading a workbook")]
        self.assertLess(body.index('ip.paused("ercot")'), body.index("get(url"))
        self.assertNotIn(chr(0x2014), code)                                      # no em dash


class Write(unittest.TestCase):
    def setUp(self):
        self.raw = tempfile.mkdtemp(prefix="erw_s140_raw_")
        self.out = tempfile.mkdtemp(prefix="erw_s140_out_")
        self.addCleanup(shutil.rmtree, self.raw, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.out, ignore_errors=True)
        saved = (ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR)

        def restore():
            ip.OUT_DIR, ip.LOG_DIR, ip.RAW_DIR, ip.METADATA_DIR, ip.STATUS_DIR = saved
        self.addCleanup(restore)
        ip.set_out_dir(self.out)
        self.path = os.path.join(self.out, z.TABLE + ".csv")
        self.lines = []

    def log(self, m):
        self.lines.append(str(m))

    def table(self):
        return pd.read_csv(self.path, skiprows=ip.header_rows(self.path), dtype=str, keep_default_na=False)

    def write(self, **kw):
        with mock.patch("requests.Session.send", side_effect=AssertionError("--write made a request")):
            return z.write(args(**kw), self.log, "20261007T000000Z", raw=self.raw)

    def test_the_table_from_the_saved_files(self):
        self.assertFalse(os.path.normcase(self.path).startswith(os.path.normcase(os.path.join(ROOT, "warehouse", "output"))))
        save_copy(self.raw, "dam", 2015, "1")
        save_copy(self.raw, "rtm", 2015, "2", published="2016-01-01T08:21:39-05:00")
        self.assertEqual(self.write(), 0)
        t = self.table()
        self.assertEqual(list(t.columns), z.COLS)
        self.assertEqual(len(t), 8 * 48 + 4 * 192)
        self.assertEqual(t.groupby(["market", "variable", "freq", "unit", "geo", "year"]).size().to_dict(),
                         {("ercot_dam", "spp_dam", "PT1H", "USD/MWh", "US-TX", "2015"): 384,
                          ("ercot_rtm", "spp_rtm", "PT15M", "USD/MWh", "US-TX", "2015"): 768})
        self.assertEqual(set(t["entity"]), {"ercot:" + p for p in z.LOAD_ZONES})
        self.assertEqual(set(t.loc[t["market"] == "ercot_rtm", "node"]), set(z.COMPETITIVE_ZONES))
        self.assertEqual(set(t.loc[t["market"] == "ercot_dam", "source"]), {"ercot:NP4-180-ER"})
        self.assertEqual(set(t.loc[t["market"] == "ercot_rtm", "source"]), {"ercot:NP6-785-ER"})
        self.assertEqual(set(t.loc[t["market"] == "ercot_dam", "source_url"]), {"https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1"})
        self.assertEqual(set(t["retrieved_at"]), {"2026-10-07T09:00:00Z"})
        self.assertEqual(set(t.loc[t["market"] == "ercot_dam", "vintage"]), {"2016-01-01T14:03:08Z"})   # as the hub history has it
        one = t[(t["entity"] == "ercot:LZ_HOUSTON") & (t["variable"] == "spp_dam") & (t["ts_utc"] == "2015-11-01T07:00:00Z")]
        self.assertEqual(list(one["value"]), ["15.34"])
        report = erw_validate.validate(self.path)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["shape"], "series")
        with open(self.path, encoding="utf-8") as f:
            head = [line for line in f if line.startswith("#")]
        self.assertTrue(any(line.startswith("# Source: ERCOT NP4-180-ER Historical DAM Load Zone and Hub Prices, https://") for line in head))
        self.assertTrue(any(line.startswith("# Source: ERCOT NP6-785-ER Historical RTM Load Zone and Hub Prices, https://") for line in head))
        self.assertTrue(any("may be used, reproduced, and redistributed" in line for line in head))
        self.assertTrue(any(line.startswith("# File holds 1152 rows") for line in head))
        reg = pd.read_csv(os.path.join(self.out, "metadata", "sources.csv"), dtype=str, keep_default_na=False)
        self.assertEqual(dict(zip(reg["source"], reg["tables"])), {"ercot:NP4-180-ER": z.TABLE, "ercot:NP6-785-ER": z.TABLE})
        with open(os.path.join(self.out, "status", "ercot_zone_prices.json"), encoding="utf-8") as f:
            self.assertEqual([(r["table"], r["market"], r["status"]) for r in json.load(f)["results"]],
                             [(z.TABLE, "DAM", "ok"), (z.TABLE, "RTM", "ok")])

    def test_a_second_write_changes_nothing_and_a_machine_with_one_file_never_thins_the_table(self):
        save_copy(self.raw, "dam", 2015, "1")
        save_copy(self.raw, "rtm", 2015, "2")
        self.assertEqual(self.write(), 0)
        first = self.table()
        self.assertEqual(self.write(), 0)
        pd.testing.assert_frame_equal(self.table(), first)
        other = tempfile.mkdtemp(prefix="erw_s140_raw_")                       # the runner: it holds the day-ahead copy only
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        save_copy(other, "dam", 2015, "1")
        with mock.patch("requests.Session.send", side_effect=AssertionError("--write made a request")):
            self.assertEqual(z.write(args(), self.log, "20261008T000000Z", raw=other), 0)
        pd.testing.assert_frame_equal(self.table(), first)                     # the real-time rows are still there
        self.assertEqual(erw_validate.validate(self.path)["errors"], [])

    def test_two_copies_of_a_year_and_years_named(self):
        save_copy(self.raw, "dam", 2015, "1", when="2026-10-07T09:00:00Z")
        save_copy(self.raw, "dam", 2015, "2", when="2026-10-14T09:00:00Z")                # the same year, posted again
        save_copy(self.raw, "rtm", 2015, "3")
        self.assertEqual(self.write(years=[2015]), 0)
        t = self.table()
        self.assertEqual(len(t), 8 * 48 + 4 * 192)                                        # each interval once
        self.assertEqual(set(t.loc[t["market"] == "ercot_dam", "retrieved_at"]), {"2026-10-14T09:00:00Z"})   # the newer copy's rows
        self.assertEqual(self.write(years=[2014]), 0)                                     # no saved year named: the table stays
        pd.testing.assert_frame_equal(self.table(), t)

    def test_it_refuses_to_write_past_the_ceiling(self):
        save_copy(self.raw, "dam", 2015, "1")
        with self.assertRaises(RuntimeError):
            self.write(ceiling=8 * 48 - 1)
        self.assertFalse(os.path.exists(self.path))
        self.assertEqual(self.write(ceiling=8 * 48), 0)


class Fixtures(unittest.TestCase):
    def test_they_are_small(self):
        mine = ["dam_2015_two_days.xlsx", "rtm_2015_two_days.xlsx", "hub_rows_two_days.csv"]   # other tests keep theirs in folders beside
        total = sum(os.path.getsize(os.path.join(FIX, f)) for f in mine)
        self.assertLess(total, 300_000)


if __name__ == "__main__":
    unittest.main()
