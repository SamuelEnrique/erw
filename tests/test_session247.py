"""Session 247: stale and empty.

Energy Research Warehouse (ERW). Four things: session 218's stale public tables on a schedule (one block of the data
machine's daily run, warehouse/run_data_machine_tables.sh); the table of /supply whose five-year columns are all "not
held"; the two days the network's newest hour stands behind; and the price board's page builder on a machine that
lacks a table.

What is held here: the block's steps, their order and their cadence, that it is sourced where the daily run can use
its own soft steps, and that it refuses where the daily run does; the curtailment connector's saved-plus-new mode;
that the board's builder gives no row, and does not stop, for a table that is not on the machine; and the words of
the three methods. No request, no table written: the folders are stand-ins.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (("warehouse", "connectors"), ("warehouse", "derived"), ("warehouse", "supabase")):
    sys.path.insert(0, os.path.join(ROOT, *p))
import board_page  # noqa: E402
import caiso_curtailment_intervals as cci  # noqa: E402
import load  # noqa: E402

EM = chr(0x2014)
GIT_BASH = r"C:\Program Files\Git\bin\bash.exe"   # the data machine's: bash is not on PATH for a Windows shell there
BASH = shutil.which("bash") or (GIT_BASH if os.path.exists(GIT_BASH) else None)
BLOCK = "warehouse/run_data_machine_tables.sh"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBlock(unittest.TestCase):
    def setUp(self):
        self.text = src(*BLOCK.split("/"))
        self.steps = [tuple(line.strip().strip('"').split("|")) for line in self.text.split("TABLE_STEPS=(", 1)[1].split("\n)", 1)[0].strip().splitlines()]

    def test_the_nine_steps_their_tables_and_their_cadence(self):
        self.assertEqual([(s[0], s[1], s[2]) for s in self.steps[:10]], [   # session 271 adds eight after them (tests/test_session271.py)
            ("dm_eia930_total_interchange", "eia930_daily_total_interchange", "daily"),
            ("dm_caiso_ws_forecast", "caiso_wind_solar_forecast", "daily"),
            ("dm_ercot_ws_forecast", "ercot_wind_solar_forecast", "daily"),
            ("dm_nrc_reactor_status", "nrc_reactor_status", "daily"),
            ("dm_caiso_emergencies", "caiso_grid_emergencies", "daily"),
            ("dm_caiso_reliability", "caiso_reliability_daily", "daily"),
            ("dm_caiso_curtailment", "caiso_curtailment_intervals", "monthly pull"),
            ("dm_storage_owners", "storage_owners_monthly", "monthly"),
            ("dm_shoulder_hours", "shoulder_hours_monthly", "monthly"),
            ("dm_scarcity_hours", "scarcity_hours_by_grid", "monthly")])                           # session 254: a tenth step, derived, no request
        for name, table, cadence, cmd in self.steps:
            self.assertTrue(os.path.exists(os.path.join(ROOT, *cmd.split()[0].split("/"))), cmd)     # every command is a file of the repository
            self.assertTrue(name.startswith("dm_"), name)                                           # a step of the data machine's daily run, as erw_health counts it
        # the notices are read before the table that counts them by day
        names = [s[0] for s in self.steps]
        self.assertLess(names.index("dm_caiso_emergencies"), names.index("dm_caiso_reliability"))

    def test_no_step_asks_a_grid_this_chain_may_not_ask_or_a_paused_publisher(self):
        for name, table, cadence, cmd in self.steps:
            for word in ("nyiso", "isone", "miso", "spp", "pjm", "vascc"):
                self.assertNotIn(word, cmd.lower(), cmd)
        # session 271: NOAA's weather is in the block since the ceiling became 6,000,000 rows a year (the owner's ruling)
        self.assertEqual([s[0] for s in self.steps if "noaa" in s[3].lower()], ["dm_noaa_weather"])

    def test_the_monthly_pull_asks_only_for_what_is_not_saved(self):
        cmd = dict((s[0], s[3]) for s in self.steps)["dm_caiso_curtailment"]
        self.assertTrue(cmd.endswith("caiso_curtailment_intervals.py --new-only"), cmd)
        with tempfile.TemporaryDirectory() as d:
            for run, days in (("20261004T103956Z", ["2026-01-01", "2026-01-02"]), ("20261013T030814Z", ["2026-01-02", "2026-10-11"])):
                os.makedirs(os.path.join(d, run))
                for day in days:
                    with open(os.path.join(d, run, f"drr_{day}.html"), "w", encoding="utf-8") as f:
                        f.write(run)
            os.makedirs(os.path.join(d, "20261013T075329Z"))                                        # this run's own folder, empty
            saved = cci.saved_reports(d)
        self.assertEqual(sorted(saved), ["2026-01-01", "2026-01-02", "2026-10-11"])
        self.assertIn("20261013T030814Z", saved["2026-01-02"])                                      # a day saved twice: the newer run's copy
        for bad in (["--new-only", "--no-reports"], ["--new-only", "--from-dir", "x"], ["--new-only", "--reports-dir", "x"]):
            with mock.patch("sys.stderr"), self.assertRaises(SystemExit):
                cci.main(bad)

    def test_the_month_is_run_once_from_the_third_and_can_be_forced(self):
        self.assertIn("MONTHLY_DAY=3", self.text)
        self.assertIn('stamp="runs/dm_monthly_${month}.done"', self.text)
        self.assertIn('if [ "${MONTHLY:-0}" = "1" ]; then', self.text)
        self.assertIn('elif [ ! -f "$stamp" ] && [ "$((10#$(date -u +%d)))" -ge "$MONTHLY_DAY" ]; then', self.text)   # 10#: the 8th and 9th are not octal
        self.assertIn('[ "${MONTHLY_PULLS:-1}" = "0" ]', self.text)

    def test_the_live_set_load_names_only_tables_the_live_set_holds(self):
        only = re.search(r"LIVE_ONLY='\^\(([a-z0-9_|]+)\)\$'", self.text).group(1).split("|")
        self.assertEqual(only, ["caiso_reliability_daily", "caiso_grid_emergencies", "storage_owners_monthly", "shoulder_hours_monthly", "ercot_rtm_price_adders",
                                "scarcity_hours_by_grid"])                                          # session 254
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        for t in only:
            self.assertEqual(load.live_rule(t), ("full", None), t)
            self.assertNotIn(t, live["catalogue_hold"], t)
        self.assertIn('soft_step dm_live_set "$PYTHON" warehouse/supabase/load.py --no-vacuum --only "$LIVE_ONLY"', self.text)

    def test_the_daily_run_sources_it_after_the_adders_and_before_the_load_zones(self):
        sh = src("warehouse", "run_data_machine.sh")
        line = ". warehouse/run_data_machine_tables.sh"
        self.assertEqual(sh.count("\n" + line + "\n"), 1)
        self.assertLess(sh.index('table_stores dm_rt_adders_stores "$ADDERS" "$was"'), sh.index("\n" + line))
        self.assertLess(sh.index("\n" + line), sh.index("# ---- 2. ERCOT's load zones"))
        self.assertIn("bash warehouse/run_data_machine_tables.sh --list", sh)
        # sourced, it defines nothing the daily run already has: its own setting-up is behind one test
        self.assertIn("if ! declare -F soft_step > /dev/null; then", self.text)

    @unittest.skipUnless(BASH, "no bash on this machine")
    def test_it_parses_lists_its_steps_and_refuses_on_the_runner(self):
        def run(args, env=None):
            return subprocess.run([BASH, BLOCK] + args, cwd=ROOT, capture_output=True, text=True, timeout=120, env={**os.environ, **(env or {})})
        self.assertEqual(subprocess.run([BASH, "-n", BLOCK], cwd=ROOT, capture_output=True, text=True, timeout=60).returncode, 0)
        r = run(["--list"])
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.strip().splitlines()
        self.assertEqual(len(lines), 23)                                                           # ten steps since session 254, eight more since session 271, two since 277, and the two loads
        self.assertTrue(lines[0].startswith("dm_eia930_total_interchange: eia930_daily_total_interchange (daily): python warehouse/connectors/"), lines[0])
        self.assertTrue(lines[-2].startswith("dm_live_set: python warehouse/supabase/load.py --no-vacuum --only"), lines[-2])
        self.assertTrue(lines[-1].startswith("dm_live_set_weekly (weekly): python warehouse/supabase/load.py --no-vacuum --only"), lines[-1])
        r = run([], env={"GITHUB_ACTIONS": "true"})
        self.assertEqual(r.returncode, 0)
        self.assertIn("run_data_machine_tables REFUSED: this is the GitHub runner", r.stdout)       # nothing asked, nothing built, no status file written


class TheBoardWithoutATable(unittest.TestCase):
    def test_a_table_that_is_not_here_gives_no_row_and_is_named(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(board_page.ip, "OUT_DIR", d):
            del board_page.ABSENT[:]
            self.assertEqual(board_page.table_daily("eia_fuel_spot_prices"), ({}, {}))
            self.assertEqual(board_page.table_daily("imf_commodity_prices", since="2019-01-01"), ({}, {}))
            self.assertFalse(board_page.here("eia_fuel_spot_prices"))
            said = []
            self.assertEqual(board_page.build_week(said.append), ([], []))
            self.assertIn("no week built (page_keep.py keeps the held one)", said[0])
            self.assertEqual(board_page.ABSENT, ["eia_fuel_spot_prices", "imf_commodity_prices", "iso_trader_daily"])   # each once, in the order asked
        del board_page.ABSENT[:]

    def test_every_table_the_builder_reads_whole_goes_through_the_check(self):
        text = src("warehouse", "derived", "board_page.py")
        # pb.read_table is called in four places; each is behind a test that the table is on the machine
        # every function that reads a table whole asks first whether the table is on the machine
        bodies = ["def " + b for b in text.split("\ndef ")[1:]]
        readers = [b for b in bodies if "pb.read_table(" in b]
        self.assertEqual(sorted(b.split("(", 1)[0][4:] for b in readers), ["build_as", "build_week", "hourly_store", "table_daily"])
        for b in readers:
            first = b.index("pb.read_table(")
            self.assertTrue("os.path.exists(" in b[:first] or "here(" in b[:first], b.split("(", 1)[0])
        # and a week the builder could not make never blanks the page's week: page_keep.py takes the held one
        keep = src("warehouse", "derived", "page_keep.py")
        self.assertIn('week = new_body.get("week") or old_body.get("week") or []', keep)
        self.assertIn('spikes = new_body.get("spikes") or old_body.get("spikes") or []', keep)


class TheWords(unittest.TestCase):
    def test_the_network_method_says_whose_lag_it_is(self):
        doc = src("docs", "methods", "grid_network.md")
        part = doc.split("## How far behind the newest hour is, and why (session 247)", 1)[1].split("\n## ", 1)[0]
        for words in ("53 hours", "The lag is EIA's, and both of its public routes have it", "EIA930_INTERCHANGE_2026_Jul_Dec.csv", "the second morning after it",
                      "129, 97 and 88 of 157 pairs", "Demand is not behind"):
            self.assertIn(words, part, words)

    def test_the_supply_method_names_the_table_and_what_would_fill_each_row(self):
        doc = src("docs", "methods", "supply_and_trade.md")
        part = doc.split('### The table whose five-year columns are all "not held" (session 247)', 1)[1].split("\n### ", 1)[0]
        for words in ("in all eight rows", "ERCOT lists 31 days of this report", "about 39 months back", "this chain may not ask NYISO", "this chain may not ask SPP",
                      "So nothing was pulled for this table"):
            self.assertIn(words, part, words)

    def test_the_machines_document_lists_the_blocks_steps(self):
        doc = src("docs", "machines.md")
        part = doc.split("### The data machine's daily run since session 247", 1)[1].split("\n### ", 1)[0]
        for words in ("warehouse/run_data_machine_tables.sh", "dm_eia930_total_interchange", "dm_caiso_emergencies", "dm_caiso_curtailment", "--new-only", "dm_live_set",
                      "NOAA's weather", "3,000,000"):
            self.assertIn(words, part, words)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in (BLOCK, "warehouse/run_data_machine.sh", "warehouse/derived/board_page.py", "warehouse/connectors/caiso_curtailment_intervals.py", "docs/methods/grid_network.md",
                  "docs/methods/supply_and_trade.md", "docs/machines.md", "tests/test_session247.py"):
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
