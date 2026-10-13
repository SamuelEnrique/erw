"""Session 254: each grid's own scarcity signal beside the USD 1,000 price count (scarcity_hours_by_grid).

The window in standard time, the price count of an hour, a notice's hours (across midnight UTC, across a clock
change, repeated by day), which notices make CAISO's signal, ERCOT's adder and where it ends, on made-up rows written
to a temporary directory (test inputs, never data); then the first run's counts against the table itself where the
data machine holds it. No network.
"""
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import scarcity_hours_by_grid as sh  # noqa: E402

EM = chr(0x2014)
TABLE = os.path.join(ROOT, "warehouse", "output", "scarcity_hours_by_grid.csv")


def write(d, name, head, lines, comment="# a test table: made-up rows, never data"):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write(comment + "\n" + head + "\n" + "\n".join(lines) + "\n")


class TheWindow(unittest.TestCase):
    def test_thirty_six_whole_months_in_the_grids_standard_time(self):
        a, b = sh.window("2026-10", 6)
        self.assertEqual((sh.ip.utc_iso(a), sh.ip.utc_iso(b)), ("2023-10-01T06:00:00Z", "2026-10-01T05:00:00Z"))
        self.assertEqual(int((b - a) / pd.Timedelta(hours=1)) + 1, 26304)
        a, b = sh.window("2026-10", 8)
        self.assertEqual((sh.ip.utc_iso(a), sh.ip.utc_iso(b)), ("2023-10-01T08:00:00Z", "2026-10-01T07:00:00Z"))
        self.assertEqual(sh.ip.utc_iso(sh.window("2026-01", 6)[0]), "2023-01-01T06:00:00Z")


class ThePriceCount(unittest.TestCase):
    def test_the_intervals_at_or_above_the_level_and_the_hours_mean(self):
        rt = pd.DataFrame({"ts_utc": ["2026-01-28T13:00:00Z", "2026-01-28T13:15:00Z", "2026-01-28T13:30:00Z", "2026-01-28T13:45:00Z", "2026-01-28T14:00:00Z", "2026-01-28T14:15:00Z"],
                           "value": [1000.0, 2500.0, 999.99, 30.0, 4000.0, 10.0]})
        da = pd.DataFrame({"ts_utc": ["2026-01-28T13:00:00Z", "2026-01-28T14:00:00Z"], "value": [1000.0, 999.0]})
        got = {(v, ts): (val, detail) for v, ts, val, detail in sh.price_rows(rt, da)}
        self.assertEqual(got[("rt_intervals_ge_1000", "2026-01-28T13:00:00Z")], (2, "held=4"))
        self.assertEqual(got[("rt_hour_ge_1000", "2026-01-28T13:00:00Z")], (1, ""))            # the mean of the four is 1,132.50
        self.assertEqual(got[("rt_intervals_ge_1000", "2026-01-28T14:00:00Z")], (1, "held=2"))  # two intervals held, and it says so
        self.assertEqual(got[("rt_hour_ge_1000", "2026-01-28T14:00:00Z")], (1, ""))
        self.assertEqual(got[("da_hour_ge_1000", "2026-01-28T13:00:00Z")], (1, ""))
        self.assertEqual(got[("da_hour_ge_1000", "2026-01-28T14:00:00Z")], (0, ""))
        self.assertEqual(sh.price_rows(rt.iloc[0:0], da.iloc[0:0]), [])                           # nothing held: no row, not a zero

    def test_an_interval_in_the_history_and_in_the_live_table_is_read_once(self):
        with tempfile.TemporaryDirectory() as d:
            head = "ts_utc,value,market,node"
            write(d, "hist", head, ["2026-08-26T04:30:00Z,1200,ercot_rtm,HB_HUBAVG", "2026-08-26T04:45:00Z,20,ercot_rtm,HB_HUBAVG", "2026-08-26T04:45:00Z,20,ercot_rtm,HB_NORTH",
                                    "2026-08-26T04:00:00Z,5,ercot_dam,HB_HUBAVG", "2019-01-01T06:00:00Z,9000,ercot_rtm,HB_HUBAVG"])
            write(d, "live", head, ["2026-08-26T04:45:00Z,99,ercot_rtm,HB_HUBAVG", "2026-08-26T05:00:00Z,21,ercot_rtm,HB_HUBAVG"])
            a, b = sh.window("2026-10", 6)
            got = sh.read_prices(["hist", "live"], "ercot_rtm", "HB_HUBAVG", a, b, d)
            self.assertEqual(dict(zip(got["ts_utc"], got["value"])), {"2026-08-26T04:30:00Z": 1200.0, "2026-08-26T04:45:00Z": 20.0, "2026-08-26T05:00:00Z": 21.0})
            with self.assertRaises(FileNotFoundError):
                sh.read_prices(["hist", "not_there"], "ercot_rtm", "HB_HUBAVG", a, b, d)


class CaisosSignal(unittest.TestCase):
    HEAD = "event_id,event_date,event_type,x_region,x_start,x_end"

    def test_a_notices_hours_in_utc_any_part_of_the_hour(self):
        n = pd.DataFrame({"event_type": ["eea_watch"], "x_region": ["CAISO Grid"], "x_start": ["2024-07-24 17:25"], "x_end": ["2024-07-24 23:59"]})
        self.assertEqual(sorted(sh.notice_hours(n)), [f"2024-07-25T0{h}:00:00Z" for h in range(7)])     # Pacific daylight time is UTC-7
        w = pd.DataFrame({"event_type": ["flex_alert"], "x_region": ["CAISO Grid"], "x_start": ["2024-01-10 16:00"], "x_end": ["2024-01-10 21:00"]})
        self.assertEqual(sorted(sh.notice_hours(w))[0], "2024-01-11T00:00:00Z")                           # Pacific standard time is UTC-8
        self.assertEqual(len(sh.notice_hours(w)), 6)                                                      # 16:00 to 21:00 touches six hours

    def test_a_notice_printed_on_each_day_it_covers_is_read_once_and_a_row_without_hours_is_left_out(self):
        n = pd.DataFrame({"event_type": ["transmission_emergency"] * 2 + ["rmo"], "x_region": ["Southern CA Region"] * 2 + ["CAISO Grid"],
                          "x_start": ["2024-09-06 17:24", "2024-09-06 17:24", ""], "x_end": ["2024-09-07 01:27", "2024-09-07 01:27", ""]})
        got = sh.notice_hours(n)
        self.assertEqual(len(got), 9)                                                                      # 17:24 to 01:27: nine hours
        self.assertTrue(all(v == ["transmission_emergency@Southern CA Region"] for v in got.values()))

    def test_an_eea_or_an_alert_makes_the_signal_and_restricted_maintenance_is_named_and_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "caiso_grid_emergencies", self.HEAD,
                  ["a,2023-10-02,rmo,CAISO Grid,2023-10-02 06:00,2023-10-02 22:00", "b,2023-10-02,eea_watch,CAISO Grid,2023-10-02 18:00,2023-10-02 19:30",
                   "c,2023-10-03,flex_alert,CAISO Grid,2023-10-03 16:00,2023-10-03 16:59"],
                  comment="# Retrieved: a test; the report's revision date 10/05/2023")
            a = pd.Timestamp("2023-10-01T08:00:00Z")
            rows, revised = sh.caiso_signal(a, pd.Timestamp("2026-10-01T07:00:00Z"), d)
            self.assertEqual(revised, "10/05/2023")
            self.assertEqual((rows[0][1], rows[-1][1]), ("2023-10-01T08:00:00Z", "2023-10-04T23:00:00Z"))      # held to the day before the report was revised
            by = {ts: (v, detail) for _, ts, v, detail in rows}
            self.assertEqual(by["2023-10-02T13:00:00Z"], (0, "rmo@CAISO Grid"))                                # 06:00 Pacific daylight: named, not the signal
            self.assertEqual(by["2023-10-03T01:00:00Z"], (1, "eea_watch@CAISO Grid;rmo@CAISO Grid"))           # 18:00
            self.assertEqual(by["2023-10-03T02:00:00Z"][0], 1)                                                 # 19:00 to 19:30: any part of the hour
            self.assertEqual(by["2023-10-03T03:00:00Z"], (0, "rmo@CAISO Grid"))
            self.assertEqual(by["2023-10-03T23:00:00Z"], (1, "flex_alert@CAISO Grid"))
            self.assertEqual(by["2023-10-01T08:00:00Z"], (0, ""))                                              # no notice: a zero, because the report is whole
            self.assertEqual(sum(v for v, _ in by.values()), 3)


class ErcotsSignal(unittest.TestCase):
    def test_the_adder_above_zero_its_mean_beside_it_and_no_hour_after_its_last(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "ercot_rtm_price_adders", "entity,variable,ts_utc,value",
                  ["ercot:system,rtorpa_mean,2025-12-05T04:00:00Z,0.0", "ercot:system,rtorpa_mean,2025-12-05T05:00:00Z,0.0312", "ercot:system,rtorpa_max,2025-12-05T05:00:00Z,9",
                   "ercot:system,rtrdpa_mean,2025-12-06T05:00:00Z,150", "ercot:system,rtorpa_mean,2020-01-01T06:00:00Z,412.74"])
            a, b = sh.window("2026-10", 6)
            self.assertEqual(sh.ercot_signal(a, b, d), [("own_signal", "2025-12-05T04:00:00Z", 0, "rtorpa_mean=0.0"), ("own_signal", "2025-12-05T05:00:00Z", 1, "rtorpa_mean=0.0312")])


class ARowThatComesOutAsItWas(unittest.TestCase):
    def test_keeps_its_retrieved_at_and_a_new_or_changed_row_takes_this_runs(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "old.csv")
            write(d, "old", "entity,variable,ts_utc,value,x_detail,retrieved_at",
                  ["iso:ercot,own_signal,2025-01-01T06:00:00Z,0,rtorpa_mean=0.0,2026-10-13T18:42:41Z", "iso:ercot,own_signal,2025-01-01T07:00:00Z,0,rtorpa_mean=0.0,2026-10-13T18:42:41Z",
                   "iso:ercot,rt_intervals_ge_1000,2025-01-01T06:00:00Z,0,held=4,2026-10-13T18:42:41Z"])
            s = pd.DataFrame({"entity": ["iso:ercot"] * 4, "variable": ["own_signal", "own_signal", "rt_intervals_ge_1000", "rt_hour_ge_1000"],
                              "ts_utc": ["2025-01-01T06:00:00Z", "2025-01-01T07:00:00Z", "2025-01-01T06:00:00Z", "2025-01-01T06:00:00Z"],
                              "value": [0, 1, 0, 0], "x_detail": ["rtorpa_mean=0.0", "rtorpa_mean=0.5", "held=3", ""]})
            self.assertEqual(sh.kept_retrieved(s, path, "2026-11-03T12:00:00Z"),
                             ["2026-10-13T18:42:41Z",      # as it was
                              "2026-11-03T12:00:00Z",      # its value changed
                              "2026-11-03T12:00:00Z",      # its detail changed
                              "2026-11-03T12:00:00Z"])     # a new row


class TheSchedule(unittest.TestCase):
    def test_a_monthly_step_of_the_data_machines_run_and_a_rule_of_the_live_set_under_both_holds(self):
        import yaml
        with open(os.path.join(ROOT, "warehouse", "run_data_machine_tables.sh"), encoding="utf-8") as f:
            block = f.read()
        self.assertIn('"dm_scarcity_hours|scarcity_hours_by_grid|monthly|warehouse/derived/scarcity_hours_by_grid.py"', block)
        # after the notices it reads, which the same block refreshes every day
        self.assertLess(block.index('"dm_caiso_emergencies|'), block.index('"dm_scarcity_hours|'))
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        self.assertIn("^scarcity_hours_by_grid$", live["full"])
        self.assertIn("scarcity_hours_by_grid", live["review_hold"])                 # loaded, and in no count a visitor sees
        self.assertIn("erw:scarcity_hours_by_grid", live["sources_hold"])


class TheWords(unittest.TestCase):
    def test_the_rule_names_the_table_the_level_and_what_is_not_in_it_and_no_forbidden_dash(self):
        with open(os.path.join(ROOT, "docs", "methods", "scarcity_hours_by_grid.md"), encoding="utf-8") as f:
            text = f.read()
        for piece in ("`scarcity_hours_by_grid`", "USD 1,000 per MWh", "An hour without a row is not held. It is not a zero.", "Held to 4 December 2025 and no longer.",
                      "NYISO, ISO-NE, SPP, MISO", "`rt_intervals_ge_1000`", "`rt_hour_ge_1000`", "`da_hour_ge_1000`", "`own_signal`", "California ISO"):
            self.assertIn(piece, text)
        with open(os.path.join(ROOT, "warehouse", "derived", "scarcity_hours_by_grid.py"), encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn(EM, text + code)
        self.assertEqual([g["grid"] for g in sh.GRIDS], ["ercot", "caiso"])
        self.assertEqual((sh.LEVEL, sh.MONTHS), (1000.0, 36))


@unittest.skipUnless(os.path.exists(TABLE) and not os.environ.get("GITHUB_ACTIONS"), "the table is on the data machine, not on this one")
class TheTableOnTheDataMachine(unittest.TestCase):
    """The counts the method note prints, read from the table as built. Skipped where the table is not held."""
    @classmethod
    def setUpClass(cls):
        d = pd.read_csv(TABLE, comment="#", dtype=str, keep_default_na=False)
        d["value"] = d["value"].astype(float)
        cls.d = d
        with open(TABLE, encoding="utf-8") as f:
            cls.october = any(ln.startswith("# Window: the 36 whole months before 2026-10,") for ln in f if ln.startswith("#"))

    def test_the_first_runs_counts(self):
        if not self.october:
            self.skipTest("the table has been rebuilt for a later month: the note's first-run counts are of October 2026")
        d = self.d
        cnt = lambda grid, var, on=None: int(((d["entity"] == f"iso:{grid}") & (d["variable"] == var) & ((d["value"] >= 1) if on else True)).sum())  # noqa: E731
        self.assertEqual((cnt("ercot", "rt_hour_ge_1000"), cnt("ercot", "rt_hour_ge_1000", True), cnt("ercot", "da_hour_ge_1000", True)), (26304, 12, 22))
        self.assertEqual((cnt("ercot", "own_signal"), cnt("ercot", "own_signal", True)), (19097, 759))
        self.assertEqual((cnt("caiso", "rt_hour_ge_1000"), cnt("caiso", "rt_hour_ge_1000", True), cnt("caiso", "own_signal"), cnt("caiso", "own_signal", True)), (18191, 1, 26304, 7))
        self.assertEqual(d[(d["entity"] == "iso:ercot") & (d["variable"] == "own_signal")]["ts_utc"].max(), "2025-12-05T05:00:00Z")

    def test_one_row_a_grid_hour_and_variable_and_only_zeros_and_small_counts(self):
        d = self.d
        self.assertEqual(int(d.duplicated(["entity", "variable", "ts_utc"]).sum()), 0)
        self.assertEqual(sorted(d["variable"].unique()), ["da_hour_ge_1000", "own_signal", "rt_hour_ge_1000", "rt_intervals_ge_1000"])
        self.assertTrue(d["value"].between(0, 4).all())
        self.assertTrue(d[d["variable"] != "rt_intervals_ge_1000"]["value"].isin([0, 1]).all())


if __name__ == "__main__":
    unittest.main()
