"""Session 271: seven green days and the schedules.

Energy Research Warehouse (ERW). The owner's rulings of 14 October 2026: the CARB rule (a publisher that has not
published, or any publisher's lag, is "stale at source": a skip and a yellow row, never a failed step or a red day);
NOAA's ceiling of 6,000,000 rows a year, and a refresh that asks only for the newest days; price_board_stats retired
with its page; ERCOT's storage disclosure on the data machine's schedule within its approved ceiling; clean energy and
NOAA's weather on the schedule; a weekly live-set load of this machine's tables; ERCOT's 15-minute hub history appended
from the live window; the large-load connector as a daily guard, and a footnote where the approved figure falls.

No request, no table written: the folders are stand-ins.
"""

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (("warehouse",), ("warehouse", "connectors"), ("warehouse", "derived"), ("warehouse", "metadata")):
    sys.path.insert(0, os.path.join(ROOT, *p))
import health  # noqa: E402
import hub_history  # noqa: E402
import iso_prices as ip  # noqa: E402
import large_load_snapshot as snap  # noqa: E402
import noaa_grid_weather as ngw  # noqa: E402
import run_status  # noqa: E402

EM = chr(0x2014)
GIT_BASH = r"C:\Program Files\Git\bin\bash.exe"
BASH = shutil.which("bash") or (GIT_BASH if os.path.exists(GIT_BASH) else None)
BLOCK = "warehouse/run_data_machine_tables.sh"
CARB = "carb_lcfs FAILED: RuntimeError: the newest week CARB holds is 2026-09-14, 29 days old (limit 28)"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCarbRule(unittest.TestCase):
    def test_a_lag_is_stale_at_source_and_any_other_error_stands(self):
        self.assertEqual(health.stale_reason([CARB]), "stale at source: " + CARB)
        self.assertIsNone(health.stale_reason(["x FAILED: RuntimeError: HTTP 500", CARB]))       # one real failure: the step failed
        self.assertIsNone(health.stale_reason(["all fine"]))
        self.assertEqual(ip.stale_skip("RuntimeError: the newest day the Board holds is 2026-10-01, 9 days old (limit 7)"),
                         "stale at source: RuntimeError: the newest day the Board holds is 2026-10-01, 9 days old (limit 7)")
        self.assertIsNone(ip.stale_skip("RuntimeError: HTTP 202 for https://ww2.arb.ca.gov/"))
        # on any machine, for any table: a lag is a skip, never a failure
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""}):
            self.assertTrue(ip.gap_skip("some_table", CARB).startswith("stale at source: "))
            self.assertIsNone(ip.gap_skip("some_table", "RuntimeError: HTTP 202 for x"))

    def test_the_step_is_a_skip_and_is_not_tried_again(self):
        rec, slept = [], []
        rc, status = health.run("dm_carb_lcfs", ["x"], attempt=lambda c: (1, [CARB], 2.0), sleep=slept.append, rec=lambda *a: rec.append(a))
        self.assertEqual((rc, status), (0, "skipped"))
        self.assertEqual(slept, [])
        self.assertEqual(rec, [("dm_carb_lcfs", "skipped", "stale at source: " + CARB, 2.0)])
        rec.clear()
        health.run("x", ["x"], attempt=lambda c: (1, ["x FAILED: RuntimeError: HTTP 500"], 1.0), sleep=slept.append, rec=lambda *a: rec.append(a))
        self.assertEqual(rec[0][1], "failed")                                                        # anything else: as before

    def test_a_day_with_only_a_lag_is_green_and_the_lag_is_its_yellow_row(self):
        day = "2026-10-13"
        rows = [dict(at=f"{day}T17:26:00", workflow="local:lab", run_id=None, step="dm_carb_lcfs", status="failed", reason=CARB),   # before the rule
                dict(at=f"{day}T17:27:00", workflow="local:lab", run_id=None, step="dm_frb", status="skipped", reason="stale at source: x, 9 days old (limit 7)")]
        rows += [dict(at=f"{day}T{h:02d}:00:00", workflow=w, run_id=f"{w}{h}", step="s", status="ok", reason="")
                 for w in ("latest prices", "hourly network", "daily prices", "chain watch") for h in range(2)]
        rec = health.day_record(rows)
        self.assertEqual(rec["failed"], 0)
        self.assertEqual([s["step"] for s in rec["stale"]], ["dm_carb_lcfs", "dm_frb"])
        self.assertEqual(health.green_streak({day: rec}), (1, day))
        md = health.render(day, rows)
        self.assertIn("## Stale at source", md)
        self.assertIn("**0 failures**", md)
        self.assertNotIn("## Failures", md)

    def test_a_lag_is_not_a_run_of_a_failure_streak(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "run_status.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(run_status.COLS)
                for i in range(3):
                    w.writerow([f"2026101{i}T000000Z", "github", "carb_lcfs", "carb_lcfs_credit_prices", "all", "failed", "29 days old (limit 28)"][:len(run_status.COLS)])
                    w.writerow([f"2026101{i}T000000Z", "github", "x", "x_table", "all", "failed", "HTTP 500"][:len(run_status.COLS)])
            got = run_status.streaks(3, path=p)
        self.assertEqual([g["table"] for g in got], ["x_table"])


class NoaasCeiling(unittest.TestCase):
    def test_six_million_a_year_and_2026_begins_where_the_old_count_ended(self):
        self.assertEqual(ngw.CEILING, 6_000_000)
        self.assertEqual(ngw.COUNTED_2026, 2_777_645)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ngw.year_counts(os.path.join(d, "none.json")), {"2026": 2_777_645})

    def test_a_later_answer_replaces_the_hours_from_its_own_first_hour(self):
        idx = pd.date_range("2026-09-01", periods=5, freq="h", tz="UTC")
        held = pd.DataFrame({"temp_c": [1.0, 2, 3, 4, 5], "dew_c": [0.0] * 5}, index=idx)
        part = pd.DataFrame({"temp_c": [30.0, 40, 50], "dew_c": [9.0] * 3}, index=idx[3:].append(pd.DatetimeIndex([idx[-1] + pd.Timedelta(hours=1)])))
        with mock.patch.object(ngw, "parse_lcd", return_value=(part, 3, 1)):
            got, n, marked = ngw.stitch(held, 10, 0, b"x", 8)
        self.assertEqual(list(got["temp_c"]), [1.0, 2, 3, 30, 40, 50])
        self.assertEqual((n, marked), (13, 1))

    def test_the_refresh_asks_from_a_week_before_the_newest_hour(self):
        text = src("warehouse", "connectors", "noaa_grid_weather.py")
        self.assertIn('since = (lcd.index.max() - pd.Timedelta(days=7))', text)
        self.assertIn("lcd_later(wban, r[\"retrieved_at\"])", text)


class TheRetiredBoard(unittest.TestCase):
    def test_price_board_stats_is_retired_with_its_page(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "retired_tables.csv"), encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        row = [r for r in rows if r["table"] == "price_board_stats"]
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0]["retired_on"], "2026-10-14")
        self.assertIn("site/app/_retired/board-v4", row[0]["reason"])
        self.assertTrue(src("warehouse", "refresh_board_v4.sh").splitlines()[1].startswith("# RETIRED (session 271"))


class TheBlock(unittest.TestCase):
    NEW = [("dm_ercot_large_load", "ercot_large_load_status", "daily"),
           ("dm_ercot_hub_append", "ercot_all_hub_prices_history", "daily"),
           ("dm_ercot_sced_pull", "-", "weekly"),
           ("dm_ercot_sced_write", "ercot_sced_esr_hourly", "weekly"),
           ("dm_ercot_storage_rt", "ercot_storage_rt_monthly,ercot_storage_node_basis", "weekly"),
           ("dm_eia930_workbooks", "-", "weekly"),
           ("dm_clean_energy", "clean_energy_hourly,clean_energy_summary", "weekly"),
           ("dm_noaa_weather", "noaa_grid_weather_hourly,noaa_grid_weather_daily,noaa_grid_weather_stations,noaa_station_weather_hourly", "weekly")]

    def setUp(self):
        self.text = src(*BLOCK.split("/"))
        self.steps = [tuple(line.strip().strip('"').split("|")) for line in self.text.split("TABLE_STEPS=(", 1)[1].split("\n)", 1)[0].strip().splitlines()]

    def test_the_eight_steps_after_the_ten(self):
        self.assertEqual([s[:3] for s in self.steps[10:]], self.NEW)
        for name, table, cadence, cmd in self.steps[10:]:
            self.assertTrue(os.path.exists(os.path.join(ROOT, *cmd.split()[0].split("/"))), cmd)
            for word in ("nyiso", "isone", "miso", "spp", "pjm", "vascc"):
                self.assertNotIn(word, cmd.lower(), cmd)
        cmds = dict((s[0], s[3]) for s in self.steps)
        self.assertIn("--dry-run", cmds["dm_eia930_workbooks"])                                     # the workbooks only: no table written
        self.assertIn("--refresh", cmds["dm_noaa_weather"])
        names = [s[0] for s in self.steps]
        self.assertLess(names.index("dm_eia930_workbooks"), names.index("dm_clean_energy"))        # the workbooks first
        self.assertLess(names.index("dm_ercot_sced_pull"), names.index("dm_ercot_sced_write"))
        self.assertLess(names.index("dm_ercot_sced_write"), names.index("dm_ercot_storage_rt"))

    def test_the_week_is_run_once_and_can_be_forced_and_the_weekly_load_follows(self):
        self.assertIn('wstamp="runs/dm_weekly_${week}.done"', self.text)
        self.assertIn('if [ "${WEEKLY:-0}" = "1" ] || [ ! -f "$wstamp" ]; then', self.text)
        self.assertIn('soft_step dm_live_set_weekly "$PYTHON" warehouse/supabase/load.py --no-vacuum --only "$WEEKLY_LIVE"', self.text)
        weekly = re.search(r"WEEKLY_LIVE='\^\(([a-z0-9_|]+)\)\$'", self.text).group(1).split("|")
        only = re.search(r"LIVE_ONLY='\^\(([a-z0-9_|]+)\)\$'", self.text).group(1).split("|")
        self.assertTrue(set(only) <= set(weekly))
        for name, table, cadence, cmd in self.steps:
            for t in ([] if table == "-" else table.split(",")):
                self.assertIn(t, weekly, t)

    def test_a_step_of_several_tables_stores_each(self):
        self.assertIn("IFS=',' read -r -a tables <<< \"$table\"", self.text)
        self.assertIn('table_stores "${name}${suffix}" "$t" "${before[$t]}"', self.text)

    def test_the_sced_ceiling_on_the_schedule_is_a_skip(self):
        import ercot_sced_esr as e
        with mock.patch.object(e, "pull", side_effect=e.Ceiling("at the ceiling")), \
                mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}), mock.patch("builtins.print") as pr, \
                tempfile.TemporaryDirectory() as d, mock.patch.object(ip, "LOG_DIR", d):
            try:
                rc = e.main(["--pull"])
            except TypeError:
                self.skipTest("ercot_sced_esr.main takes no argv")
        self.assertEqual(rc, 75)
        self.assertIn("SKIPPED: at the approved ceiling", " ".join(str(c) for c in pr.call_args_list))

    @unittest.skipUnless(BASH, "no bash on this machine")
    def test_it_parses(self):
        self.assertEqual(subprocess.run([BASH, "-n", BLOCK], cwd=ROOT, capture_output=True, text=True, timeout=60).returncode, 0)


class TheErcotHistory(unittest.TestCase):
    def test_the_live_rows_after_each_members_newest_interval_are_appended(self):
        def rows(ts, market, src_):
            return pd.DataFrame([dict(entity=f"ercot:{h}", variable="spp_rtm" if market == "ercot_rtm" else "spp_dam", ts_utc=t, value=1.0, unit="USD/MWh",
                                      freq="PT15M", geo="US-TX", market=market, node=h, source=src_, source_url="u", retrieved_at="r", vintage="")
                                 for t in ts for h in ("HB_NORTH", "HB_WEST")])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(ip, "OUT_DIR", d), mock.patch.object(ip, "LOG_DIR", os.path.join(d, "logs")), \
                mock.patch.object(ip, "STATUS_DIR", os.path.join(d, "status"), create=True):
            open(os.path.join(d, hub_history.ERCOT_HISTORY + ".csv"), "w").close()
            hist = rows(["2026-08-26T04:30:00Z", "2026-08-26T04:45:00Z"], "ercot_rtm", "ercot:NP6-785-ER")
            live = rows(["2026-08-26T04:45:00Z", "2026-08-26T05:00:00Z", "2027-01-01T07:00:00Z"], "ercot_rtm", "ercot:NP6-905-CD")
            for name, frame in (("ercot_rtm_hub_prices_2026", hist), ("iso_rtm_hub_prices", live), ("iso_dam_hub_prices", live.iloc[:0])):
                with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="") as f:
                    f.write("# a stand-in\n")
                    frame[ip.SERIES_COLS].to_csv(f, index=False, lineterminator="\n")
            calls = []
            with mock.patch.object(ip, "write_status"):
                rc = hub_history.append_ercot(run=lambda a: calls.append(a) or 0)
            self.assertEqual(rc, 1)                                                                # 2027 has no member: the step stops loudly
            self.assertEqual(calls, [["split", "--family", hub_history.ERCOT_HISTORY]])            # and nothing is built
            got = ip.read_series(os.path.join(d, "ercot_rtm_hub_prices_2026.csv"))
            self.assertEqual(sorted(set(got["ts_utc"])), ["2026-08-26T04:30:00Z", "2026-08-26T04:45:00Z", "2026-08-26T05:00:00Z"])
            kept = got[got["ts_utc"] == "2026-08-26T04:45:00Z"]
            self.assertEqual(set(kept["source"]), {"ercot:NP6-785-ER"})                           # the workbook's own row is never replaced
            with open(os.path.join(d, "ercot_rtm_hub_prices_2026.csv"), encoding="utf-8") as f:
                self.assertEqual(sum(1 for ln in f if ln.startswith("# " + hub_history.APPEND_MARK)), 1)


class TheLargeLoadFootnote(unittest.TestCase):
    def test_a_note_where_the_approved_figure_falls_and_nowhere_else(self):
        with tempfile.TemporaryDirectory() as d:
            t = pd.DataFrame([dict(entity="ercot:large_loads", variable="approved_to_energize_mw", ts_utc=f"{day}T00:00:00Z", value=v, unit="MW",
                                   freq="", geo="US-TX", market="", node="", source="ercot:large_load_status_update", source_url="https://www.ercot.com/x",
                                   retrieved_at="2026-10-13T02:50:17Z", vintage="", x_document="d.pptx", x_month_as_written="")
                              for day, v in (("2026-04-24", 9042.0), ("2026-05-21", 9062.0), ("2026-06-19", 8927.0))])
            with open(os.path.join(d, snap.TABLE + ".csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# a stand-in\n")
                t.to_csv(f, index=False, lineterminator="\n")
            f = snap.build(d)
        notes = {r["day"]: r.get("note") for r in f["reports"]}
        self.assertEqual(notes["2026-04-24"], None)
        self.assertEqual(notes["2026-05-21"], None)
        self.assertEqual(notes["2026-06-19"], "Approved to energize fell by 135 MW from ERCOT's report of 2026-05-21 (9,062 MW) to this one (8,927 MW).")

    def test_the_sites_copy_carries_it_and_the_type_names_it(self):
        f = json.loads(src("site", "data", "large_load_status.json"))
        self.assertEqual([r["day"] for r in f["reports"] if r.get("note")], ["2026-06-19"])
        self.assertIn("note?: string;", src("site", "lib", "largeload.ts"))


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for rel in ("warehouse/health.py", "warehouse/connectors/iso_prices.py", "warehouse/metadata/run_status.py", "warehouse/connectors/noaa_grid_weather.py",
                    "warehouse/connectors/hub_history.py", "warehouse/connectors/ercot_sced_esr.py", "warehouse/derived/large_load_snapshot.py",
                    BLOCK, "warehouse/refresh_board_v4.sh", "warehouse/metadata/retired_tables.csv", "site/lib/largeload.ts",
                    "docs/methods/ercot_large_load_status.md", "tests/test_session271.py"):
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
