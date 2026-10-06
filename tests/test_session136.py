"""Session 136: day-ahead energy cleared, one connector an operator that publishes it openly, and its rows on /supply.
No request is made: the parsers read short samples written here in each operator's own layout (the values are made
up for the tests and are no operator's), and the page's rule is exercised on small tables in a temporary folder."""
import datetime as dt
import io
import json
import os
import re
import sys
import tempfile
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import caiso_dam_cleared as caiso  # noqa: E402
import dam_cleared as dc  # noqa: E402
import ercot_dam_cleared as ercot  # noqa: E402
import isone_dam_cleared as isone  # noqa: E402
import nyiso_dam_cleared as nyiso  # noqa: E402
import spp_dam_cleared as spp  # noqa: E402
import iso_prices as ip  # noqa: E402
import supply_page as sp  # noqa: E402

ISOS = ("ercot", "caiso", "nyiso", "isone", "spp")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def zipped(name, text):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, text)
    return b.getvalue()


class Parsers(unittest.TestCase):
    def test_ercot_sums_the_settlement_points_of_an_hour_and_skips_an_hour_with_a_blank(self):
        text = ("DeliveryDate,HourEnding,Settlement_Point,Total_DAM_Energy_Bought,RepeatedHourFlag\n"
                "10/07/2026,01:00,A,10.5,N\n10/07/2026,01:00,B,20,N\n10/07/2026,02:00,A,5,N\n10/07/2026,02:00,B,,N\n10/07/2026,24:00,A,7,N\n")
        hours, n = ercot.parse(zipped("x.csv", text))
        self.assertEqual(n, 5)
        self.assertEqual({ip.utc_iso(t): v for t, v in hours.items()}, {"2026-10-07T05:00:00Z": 30.5, "2026-10-08T04:00:00Z": 7.0})

    def test_ercot_refuses_a_file_laid_out_otherwise(self):
        with self.assertRaises(RuntimeError):
            ercot.parse(zipped("x.csv", "DeliveryDate,HourEnding,Settlement_Point,Energy\n10/07/2026,01:00,A,1\n"))

    def test_caiso_keeps_the_load_item_of_the_isos_totals_only(self):
        head = "INTERVALSTARTTIME_GMT,INTERVALENDTIME_GMT,SLRS_TYPE,OPR_DT,OPR_HR,OPR_INTERVAL,MARKET_RUN_ID,TAC_ZONE_NAME,SCHEDULE,XML_DATA_ITEM,POS,MW,GROUP\n"
        rows = ("2026-10-04T18:00:00-00:00,2026-10-04T19:00:00-00:00,ALL,2026-10-04,12,0,DAM,Caiso_Totals,Export,ISO_TOT_EXP_MW,1,1868,1\n"
                "2026-10-04T18:00:00-00:00,2026-10-04T19:00:00-00:00,ALL,2026-10-04,12,0,DAM,Caiso_Totals,Load,ISO_TOT_LOAD_MW,1,25000.5,1\n"
                "2026-10-04T19:00:00-00:00,2026-10-04T20:00:00-00:00,ALL,2026-10-04,13,0,DAM,Caiso_Totals,Load,ISO_TOT_LOAD_MW,1,,1\n")
        hours, n = caiso.parse(zipped("x.csv", head + rows))
        self.assertEqual((n, {ip.utc_iso(t): v for t, v in hours.items()}), (3, {"2026-10-04T18:00:00Z": 25000.5}))

    def test_caiso_no_data_is_no_hour_and_another_error_is_raised(self):
        none = "<m:ERROR><m:ERR_CODE>1000</m:ERR_CODE><m:ERR_DESC>No data returned for the specified selection</m:ERR_DESC></m:ERROR>"
        self.assertEqual(caiso.parse(zipped("x.xml", none)), ({}, 0))
        with self.assertRaises(RuntimeError):
            caiso.parse(zipped("x.xml", "<m:ERROR><m:ERR_CODE>1004</m:ERR_CODE><m:ERR_DESC>Data can be requested for period of 31 days only</m:ERR_DESC></m:ERROR>"))

    def test_caiso_never_asks_for_31_days(self):
        self.assertIn("m + pd.Timedelta(days=15)", src("warehouse", "connectors", "caiso_dam_cleared.py"))

    def test_nyiso_reads_total_load_scheduled_and_not_the_total_line(self):
        text = "Date Hour,NYISO Load Forecast,Total Load Offered,Total Load Scheduled,Generation Bids Scheduled\n10/05/2026 00:00,13169.0,14492.0,13101.0,10279.2\n10/05/2026 01:00,12707.0,13992.0,12694.0,10071.0\nTotal,339134.0,1.0,25795.0,2.0\n"
        hours, n = nyiso.parse_day(text)
        self.assertEqual((n, {ip.utc_iso(t): v for t, v in hours.items()}), (3, {"2026-10-05T04:00:00Z": 13101.0, "2026-10-05T05:00:00Z": 12694.0}))

    def test_isone_reads_cleared_demand_in_mwh_and_the_repeated_hour(self):
        text = ('"C","Day-Ahead Hourly Cleared Demand"\n"H","Date","Hour Ending","Day-Ahead Cleared Demand"\n"H","Date","HE","MWh"\n'
                '"D","11/01/2026","02","9000"\n"D","11/01/2026","02X","9100"\n"D","11/01/2026","03",""\n"T","3 lines"\n')
        hours, n = isone.parse(text.encode())
        self.assertEqual((n, {ip.utc_iso(t): v for t, v in hours.items()}), (3, {"2026-11-01T05:00:00Z": 9000.0, "2026-11-01T06:00:00Z": 9100.0}))
        with self.assertRaises(RuntimeError):
            isone.parse(b'"H","Date","Hour Ending","Something Else"\n')

    def test_spp_reads_total_demand_by_area_and_an_older_file_as_one_area(self):
        new = ("Interval,GMTIntervalEnd,BAA,Generation,Cleared Demand Bid,Total Demand\n"
               "10/04/2026 01:00:00,10/04/2026 06:00:00,SPP,27594.075,40.200,30221.3\n10/04/2026 01:00:00,10/04/2026 06:00:00,SWPW,2427.172,0.000,2652.3\n")
        hours, n = spp.parse(new.encode())
        self.assertEqual({(a, ip.utc_iso(t)): v for (a, t), v in hours.items()}, {("SPP", "2026-10-04T05:00:00Z"): 30221.3, ("SWPW", "2026-10-04T05:00:00Z"): 2652.3})
        old = "Interval,GMTIntervalEnd, Generation, Total Demand\n10/04/2025 01:00:00,10/04/2025 06:00:00,27594.075,\n10/04/2025 02:00:00,10/04/2025 07:00:00,1,29000\n"
        hours, n = spp.parse(old.encode())
        self.assertEqual({(a, ip.utc_iso(t)): v for (a, t), v in hours.items()}, {("SPP", "2025-10-04T06:00:00Z"): 29000.0})


class Frame(unittest.TestCase):
    def test_the_count_stops_a_run_past_its_ceiling(self):
        c = dc.Counter(100)
        c.add(60)
        self.assertTrue(c.room(40))
        self.assertFalse(c.room(41))
        with self.assertRaises(dc.Ceiling):
            c.add(41)

    def test_a_raw_file_kept_from_an_earlier_run_is_not_counted_again(self):
        self.assertTrue(dc.reused({"file": "warehouse/raw/x/y.zip"}))
        self.assertFalse(dc.reused({"file": "", "cached": False}))
        for iso in ("ercot", "caiso", "nyiso", "spp"):
            self.assertIn("if not dc.reused(rec):", src("warehouse", "connectors", f"{iso}_dam_cleared.py"), iso)

    def test_every_connector_asks_the_pause_list_first_and_none_names_miso_or_pjm_hosts(self):
        frame = src("warehouse", "connectors", "dam_cleared.py")
        self.assertLess(frame.index('ip.paused(spec["iso"])'), frame.index("pull(log, args.days, counter)"))
        for iso in ISOS:
            code = src("warehouse", "connectors", f"{iso}_dam_cleared.py")
            for host in ("misoenergy.org", "pjm.com", "dataminer"):
                self.assertNotIn(host, code, (iso, host))
            self.assertIn("dc.run(SPEC, pull)", code)
        for iso in ("miso", "pjm"):
            self.assertFalse(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", f"{iso}_dam_cleared.py")))

    def test_each_connector_quotes_its_operators_terms_and_isone_is_internal(self):
        quotes = {"ercot": "may be used, reproduced, and redistributed in compilations, charts", "caiso": "credit the California ISO", "nyiso": "does not confer any license",
                  "isone": "Any duplication of the Content or non-personal use may violate", "spp": "Permission is implicitly granted to copy and distribute"}
        for iso, words in quotes.items():
            doc = " ".join(src("warehouse", "connectors", f"{iso}_dam_cleared.py").split('"""')[1].split())
            self.assertIn(words, doc, iso)
        self.assertEqual(isone.SPEC["entry"]["license"], "internal")
        self.assertEqual({m.SPEC["entry"]["license"] for m in (ercot, caiso, nyiso, spp)}, {"public"})

    def test_no_em_dash(self):
        for f in ["dam_cleared.py"] + [f"{iso}_dam_cleared.py" for iso in ISOS]:
            self.assertNotIn(chr(0x2014), src("warehouse", "connectors", f), f)


class PageRule(unittest.TestCase):
    """A week is the mean of seven whole days; a day is whole when every hour of the operator's day is held."""

    def table(self, folder, name, rows):
        with open(os.path.join(folder, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# a test table\nentity,variable,ts_utc,value,unit,node\n")
            for e, ts, v in rows:
                f.write(f"{e},dam_cleared_energy,{ts},{v},MW,x\n")

    def hours(self, entity, first_day, days, tz="America/Chicago", value=100.0, skip=()):
        out = []
        end = (pd.Timestamp(first_day) + pd.Timedelta(days=days)).tz_localize(tz)          # calendar days: a week with a clock change has 169 hours
        for h in pd.date_range(pd.Timestamp(first_day, tz=tz), end, freq="h", inclusive="left"):
            if h.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ") not in skip:
                out.append((entity, h.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ"), value))
        return out

    def run_rule(self, rows, tz="America/Chicago", entity=None):
        with tempfile.TemporaryDirectory() as d:
            self.table(d, "t", rows)
            old = ip.OUT_DIR
            ip.OUT_DIR = d
            try:
                return sp.cleared_weekly("t", tz, entity)
            finally:
                ip.OUT_DIR = old

    def test_a_whole_week_is_the_mean_of_its_seven_days(self):
        w = self.run_rule(self.hours("x:system", "2026-09-26", 7))             # Saturday 26 September to Friday 2 October
        self.assertEqual(w, {dt.date(2026, 10, 2): 2400.0})

    def test_a_week_missing_one_hour_is_not_shown(self):
        w = self.run_rule(self.hours("x:system", "2026-09-26", 7, skip=("2026-09-28T15:00:00Z",)))
        self.assertEqual(w, {})

    def test_a_clock_change_day_needs_its_25_hours(self):
        rows = self.hours("x:system", "2026-10-31", 7, tz="America/New_York")   # Sunday 1 November 2026 has 25 hours
        w = self.run_rule(rows, tz="America/New_York")
        self.assertEqual(list(w), [dt.date(2026, 11, 6)])
        self.assertAlmostEqual(w[dt.date(2026, 11, 6)], (6 * 2400 + 2500) / 7)

    def test_one_area_is_read_alone(self):
        rows = self.hours("spp:SPP", "2026-09-26", 7) + self.hours("spp:SWPW", "2026-09-26", 7, value=10.0)
        self.assertEqual(self.run_rule(rows, entity="spp:SPP"), {dt.date(2026, 10, 2): 2400.0})
        self.assertEqual(self.run_rule(rows, entity="spp:SWPW"), {dt.date(2026, 10, 2): 240.0})

    def test_a_table_that_is_not_here_is_said_so_and_nothing_is_filled(self):
        old = ip.OUT_DIR
        ip.OUT_DIR = tempfile.mkdtemp()
        try:
            self.assertIsNone(sp.cleared_weekly("nothing", "America/Chicago"))
        finally:
            ip.OUT_DIR = old
        body = src("warehouse", "derived", "supply_page.py").split("def cleared_weekly")[1].split("def calendar")[0]
        for words in ("fillna", "interpolate", "ffill", "bfill"):
            self.assertNotIn(words, body, words)


class OnThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8") as f:
            cls.rows = {r["id"]: r for r in json.load(f)["rows"]}

    def test_miso_and_pjm_cleared_rows_are_blank_with_their_reasons(self):
        self.assertEqual((self.rows["cleared-miso"]["status"], self.rows["cleared-pjm"]["status"]), ("paused", "licensed"))
        self.assertNotIn("last", self.rows["cleared-miso"])
        self.assertNotIn("last", self.rows["cleared-pjm"])

    def test_the_five_operators_rows_hold_a_whole_week_in_mwh_a_day(self):
        for rid in ("cleared-ercot", "cleared-caiso", "cleared-nyiso", "cleared-iso-ne", "cleared-spp"):
            r = self.rows[rid]
            self.assertEqual((r["status"], r["unit"], r["freq"]), ("ok", "MWh/d", "W"), rid)
            self.assertGreater(r["last"]["v"], 100000, rid)                     # a grid clears far more than 100 GWh a day
            self.assertEqual(dt.date.fromisoformat(r["last"]["t"]).weekday(), 4, rid)     # a week ends on a Friday

    def test_miso_and_pjm_fuel_burn_rows_are_shown_because_they_are_federal_data(self):
        # the owner's ruling (the chain prompt of 6 October 2026): figures from EIA-930 are shown for every grid
        for rid in ("burn-miso-natural-gas", "burn-pjm-natural-gas", "burn-miso-coal", "burn-pjm-coal"):
            self.assertEqual(self.rows[rid]["status"], "ok", rid)
            self.assertIn("EIA-930", json.dumps(self.rows[rid]) + src("warehouse", "derived", "supply_page.py"))


class Wiring(unittest.TestCase):
    def test_the_weekly_refresh_runs_the_five_connectors_under_health_and_validates_their_tables(self):
        sh = src("warehouse", "refresh_supply.sh")
        self.assertIn("for iso in ercot caiso nyiso isone spp; do", sh)
        self.assertIn('health.py run --step "${iso}_dam_cleared" -- "$PY" "warehouse/connectors/${iso}_dam_cleared.py"', sh)
        self.assertIn("warehouse/output/cftc_cot_positions.csv $CLEARED", sh)
        self.assertNotRegex(sh, r"(miso|pjm)_dam_cleared")

    def test_the_tables_are_held_out_of_the_live_set_and_restored_on_the_runner(self):
        import yaml
        y = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        for iso in ISOS:
            self.assertIn(f"{iso}_dam_cleared_energy", y["catalogue_hold"], iso)
        for s in ("ercot:NP4-192-CD", "caiso:ENE_SLRS", "nyiso:damenergy", "isone:hourlydayaheaddemand", "spp:DA-MC:cleared"):
            self.assertIn(s, y["sources_hold"], s)
        c = yaml.safe_load(src("warehouse", "redivis", "config.yaml"))
        self.assertTrue(any(re.fullmatch(p, "ercot_dam_cleared_energy") for p in c["restore_before_run"]))

    def test_the_method_note_states_the_measures_and_quotes_the_terms(self):
        note = src("docs", "methods", "supply_and_trade.md")
        for words in ("NP4-192-CD", "ISO_TOT_LOAD_MW", "Total Load Scheduled", "Day-Ahead Cleared Demand", "SWPW", "should not be added or ranked", "include cleared virtual bids",
                      "redistributed in compilations, charts, and analyses", "credit the California ISO", "CAPTCHA", "with appropriate citation", "Nothing is filled"):
            self.assertIn(words, note, words)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()
