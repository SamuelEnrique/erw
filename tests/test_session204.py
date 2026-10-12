"""Session 204: the data decisions of 12 October 2026, on the data machine.

What the owner ruled and this session built: ERCOT's node prices as a standing pull under a row ceiling, a soft step of
the data machine's daily run; the battery page's downloads, the generator page's builders and its hourly CSV in the
same run; a table's stores as one script; the two monthly storage tables added up again after the sync. No network:
the pull is run against three of ERCOT's own price zips (tests/fixtures/session120/) through a stand-in for requests.
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("ERW_LOCK_EXEMPT", "1")
for p in ("warehouse", "warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import battery_dispatch_export as bde  # noqa: E402
import battery_scenario_steps as bss  # noqa: E402
import ercot_rt_spp as spp  # noqa: E402
import scheduled  # noqa: E402
import table_stores  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session120")
STEPS = ["ercot_rtm_node_prices", "battery_dispatch_export", "battery_scenario_steps", "merchant_revenue", "merchant_hubs",
         "seller_hybrid", "generator_hourly_export"]
BASH = shutil.which("bash")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Reply:
    def __init__(self, content=b"", doc=None):
        self.content, self._doc, self.status_code = content, doc, 200
        self.text = json.dumps(doc) if doc is not None else ""

    def raise_for_status(self):
        pass

    def json(self):
        return self._doc


class TheCeiling(unittest.TestCase):
    """The pull against ERCOT's own three files, each request answered from the disk and written down."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        zips = os.path.join(self.tmp, "zips")
        self.patches = [mock.patch.object(spp, "RAW", self.tmp), mock.patch.object(spp, "ZIPS", zips),
                        mock.patch.object(spp, "MANIFEST", os.path.join(zips, "manifest.csv")),
                        mock.patch.object(spp, "ROWS_LOG", os.path.join(self.tmp, "rows_by_run.csv")),
                        mock.patch.object(spp, "PAUSE", 0), mock.patch.object(spp, "esr_points", lambda out_dir=None: set()),
                        mock.patch.object(spp.ip, "paused", lambda scope: None)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.files = sorted(f for f in os.listdir(FIX) if f.endswith("_csv.zip"))
        self.content = {}
        docs = []
        for i, name in enumerate(self.files):
            with open(os.path.join(FIX, name), "rb") as f:
                self.content[str(i)] = f.read()
            friendly = re.search(r"(SPPHLZNP6905_\d{8}_\d{4}_csv)", name).group(1)
            docs.append({"Document": {"FriendlyName": friendly, "ConstructedName": name, "DocID": str(i), "ContentSize": str(len(self.content[str(i)])),
                                      "PublishDate": "2026-09-28T00:02:02-05:00"}})
        self.listing = {"ListDocsByRptTypeRes": {"DocumentList": docs}}
        self.asked = []
        with open(os.path.join(FIX, self.files[0]), "rb") as f:
            self.kept = spp.kept_rows(f.read(), set())   # the hubs and Load Zones of one file: what the table keeps with no storage point

    def get(self, url, **kw):
        self.asked.append(url)
        if "IceDocListJsonWS" in url:
            return Reply(doc=self.listing)
        return Reply(content=self.content[url.rsplit("=", 1)[1]])

    def pull(self, max_rows):
        got, lines = {}, []
        rc = spp.pull(argparse.Namespace(offline=False, max_rows=max_rows), lines.append, get=self.get, run_id="test", result=got)
        return rc, got, lines

    def counted(self):
        with open(spp.ROWS_LOG, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_a_file_counts_the_rows_the_table_keeps_of_it(self):
        self.assertGreater(self.kept, 10)                 # the hubs and the Load Zones; no storage point is asked for here
        self.assertLess(self.kept, spp.ROW_MARGIN)        # the margin is more than a file's hubs and zones
        self.assertEqual(spp.kept_rows(b"not a zip", set()), 0)
        out, _, _ = spp.table(set(), lambda m: None, zips=FIX)
        self.assertEqual(len(out), 3 * self.kept)         # the count is the table's own rows of the three files

    def test_under_the_ceiling_every_listed_file_is_saved_and_counted(self):
        rc, got, lines = self.pull(spp.MAX_ROWS_DAY)
        self.assertEqual((rc, got["files"], got["rows"], got["stopped"]), (0, 3, 3 * self.kept, False))
        self.assertEqual(len(self.asked), 4)              # the list and three files
        row = self.counted()
        self.assertEqual(len(row), 1)
        self.assertEqual((int(row[0]["files_saved"]), int(row[0]["rows_counted"]), int(row[0]["ceiling"]), row[0]["stopped"]), (3, 3 * self.kept, 500000, "0"))
        self.assertTrue(any(f"rows counted against the ceiling: {3 * self.kept:,} of 500,000" in ln for ln in lines))

    def test_the_request_that_could_pass_the_ceiling_is_not_made(self):
        # room for two files and the margin, not for a third: the third file is never asked for
        rc, got, lines = self.pull(2 * self.kept + spp.ROW_MARGIN - 1)
        self.assertEqual((rc, got["files"], got["rows"], got["stopped"]), (3, 2, 2 * self.kept, True))
        self.assertEqual(len(self.asked), 3)              # the list and two files
        self.assertLessEqual(got["rows"], 2 * self.kept + spp.ROW_MARGIN - 1)
        self.assertTrue(any(ln.startswith("STOPPED before SPPHLZNP6905_") for ln in lines))
        self.assertEqual(self.counted()[0]["stopped"], "1")
        self.assertEqual(len([f for f in os.listdir(spp.ZIPS) if f.endswith(".zip")]), 2)

    def test_the_ceiling_is_the_days_and_a_second_run_counts_from_the_first(self):
        ceiling = 2 * self.kept + spp.ROW_MARGIN - 1
        self.pull(ceiling)
        self.asked.clear()
        rc, got, lines = self.pull(ceiling)               # the same UTC day: the two files' rows are already counted
        self.assertEqual((rc, got["files"], got["stopped"]), (3, 0, True))
        self.assertEqual(self.asked, [], "not even the list is asked when the day's count leaves no room for a file")
        self.assertTrue(lines[-1].startswith("STOPPED before any request"))
        day = self.counted()[0]["day_utc"]
        self.assertEqual(spp.rows_today(day), 2 * self.kept)
        self.assertEqual(spp.rows_today("1999-01-01"), 0)   # another day's runs are another day's

    def test_a_file_held_is_never_asked_for_twice(self):
        self.pull(spp.MAX_ROWS_DAY)
        self.asked.clear()
        rc, got, _ = self.pull(spp.MAX_ROWS_DAY)
        self.assertEqual((rc, got["files"], got["rows"]), (0, 0, 0))
        self.assertEqual(len(self.asked), 1)              # the list alone

    def test_the_pull_of_session_120_is_as_it_was_without_a_ceiling(self):
        rc, got, _ = self.pull(None)
        self.assertEqual((rc, got["files"]), (0, 3))
        self.assertFalse(os.path.exists(spp.ROWS_LOG))    # no ceiling named: nothing is counted

    def test_daily_names_the_ceiling_and_a_paused_publisher_is_a_skip(self):
        self.assertEqual(spp.MAX_ROWS_DAY, 500_000)
        with mock.patch.object(spp.ip, "paused", lambda scope: {"scope": "ercot"}), mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}):
            self.assertEqual(spp.main(["--daily"]), 75)
        self.assertEqual(self.asked, [])
        self.assertFalse(os.path.exists(spp.ZIPS) and os.listdir(spp.ZIPS))


class TheDailyCommand(unittest.TestCase):
    """--daily: the pull under the day's ceiling, then the table when a file was saved."""

    def daily(self, rc, files):
        wrote, asked = [], []
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)

        def pull(a, log, get=None, run_id=None, result=None):
            asked.append(a.max_rows)
            result.update(files=files, rows=files * 312, stopped=rc == 3)
            return rc

        def write(log, run_id):
            wrote.append(run_id)
            return 0
        with mock.patch.object(spp, "RAW", tmp), mock.patch.object(spp, "pull", pull), mock.patch.object(spp, "write", write), \
                mock.patch.object(spp.ip, "paused", lambda scope: None), mock.patch("builtins.print"):
            code = spp.main(["--daily"])
        return code, asked, len(wrote)

    def test_a_day_with_new_files_writes_the_table_under_the_ceiling_named(self):
        self.assertEqual(self.daily(0, 96), (0, [500000], 1))

    def test_a_day_with_no_new_file_leaves_the_table_as_it_is(self):
        self.assertEqual(self.daily(0, 0), (0, [500000], 0))

    def test_a_run_stopped_at_the_ceiling_still_writes_what_it_saved(self):
        self.assertEqual(self.daily(3, 40), (0, [500000], 1))
        self.assertEqual(self.daily(3, 0), (0, [500000], 0))

    def test_a_pull_that_failed_writes_nothing_and_says_so_by_its_exit(self):
        self.assertEqual(self.daily(1, 5), (1, [500000], 0))


class AnIntervalPostedTwice(unittest.TestCase):
    """ERCOT posted the interval ending 8 October 2026 11:45 twice, a second apart, with the same prices (found by this
    session's pull: the table refused both). Built here from one of ERCOT's own files, posted again under a later name."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.first = sorted(f for f in os.listdir(FIX) if f.endswith("_csv.zip"))[0]
        shutil.copy(os.path.join(FIX, self.first), os.path.join(self.tmp, self.first))
        self.second = self.first.replace(".000202403.", ".000203111.")   # the same interval, posted a second later
        self.assertNotEqual(self.first, self.second)

    def again(self, change=None):
        import io
        import zipfile
        with open(os.path.join(FIX, self.first), "rb") as f:
            z = zipfile.ZipFile(io.BytesIO(f.read()))
        name = z.namelist()[0]
        text = z.read(name).decode("utf-8")
        if change:
            text = change(text)
        with zipfile.ZipFile(os.path.join(self.tmp, self.second), "w") as w:
            w.writestr(name, text)

    def test_the_same_prices_twice_are_one_interval(self):
        self.again()
        lines = []
        out, n, bad = spp.table(set(), lines.append, zips=self.tmp)
        self.assertEqual((n, bad), (1, []))
        self.assertFalse(out.duplicated(["entity", "ts_utc"]).any())
        alone, _, _ = spp.table(set(), lambda m: None, zips=FIX)
        self.assertEqual(len(out), len(alone[alone["ts_utc"] == "2026-09-28T04:45:00Z"]))
        self.assertTrue(any("posted twice with the same prices" in ln and self.second in ln for ln in lines))

    def test_two_postings_whose_prices_differ_leave_the_interval_out(self):
        def change(text):
            head, row, rest = text.split("\n", 2)
            cells = row.rstrip("\r").split(",")
            at = head.rstrip("\r").split(",").index("SettlementPointPrice")
            cells[at] = str(float(cells[at]) + 1)
            return head + "\n" + ",".join(cells) + "\n" + rest
        self.again(change)
        third = sorted(f for f in os.listdir(FIX) if f.endswith("_csv.zip"))[1]
        shutil.copy(os.path.join(FIX, third), os.path.join(self.tmp, third))     # another interval, so that the table is not empty
        out, n, bad = spp.table(set(), lambda m: None, zips=self.tmp)
        self.assertEqual(n, 1)
        self.assertEqual(sorted(b[0] for b in bad), sorted([self.first, self.second]))
        self.assertTrue(all("prices that differ" in b[1] for b in bad))
        self.assertEqual(set(out["ts_utc"]), {"2026-09-28T05:00:00Z"})           # neither posting was chosen


class TheSchedule(unittest.TestCase):
    def test_the_list_names_the_seven_and_the_runners_schedule_is_as_it_was(self):
        self.assertEqual(list(scheduled.DATA_MACHINE), STEPS)
        self.assertEqual(set(scheduled.DATA_MACHINE) & set(scheduled.JOBS), set())
        self.assertEqual(scheduled.STEPS, {**scheduled.JOBS, **scheduled.DATA_MACHINE})
        for name, j in scheduled.DATA_MACHINE.items():
            self.assertTrue(os.path.exists(os.path.join(ROOT, j["cmd"][0])), name)
            self.assertEqual(j["cadence"], "data machine, daily", name)
            self.assertLessEqual(set(j.get("restore", [])), set(j.get("tables", [])), name)
        with mock.patch("builtins.print") as out:
            self.assertEqual(scheduled.main(["--list"]), 0)
        printed = "\n".join(str(c.args[0]) for c in out.call_args_list)
        for name in STEPS + list(scheduled.JOBS):
            self.assertRegex(printed, rf"(?m)^{name} \(", name)

    def test_the_node_pull_is_the_one_step_that_asks_and_it_names_the_ceiling(self):
        asks = [n for n, j in scheduled.DATA_MACHINE.items() if "/connectors/" in j["cmd"][0]]
        self.assertEqual(asks, ["ercot_rtm_node_prices"])
        self.assertEqual(scheduled.DATA_MACHINE["ercot_rtm_node_prices"]["cmd"], ["warehouse/connectors/ercot_rt_spp.py", "--daily", "--max-rows", "500000"])
        self.assertEqual(int(scheduled.NODE_ROWS_A_DAY), spp.MAX_ROWS_DAY)
        self.assertIn('ip.paused("ercot")', src("warehouse", "connectors", "ercot_rt_spp.py"))
        for name, j in scheduled.DATA_MACHINE.items():   # a builder makes no request
            if "/derived/" in j["cmd"][0]:
                self.assertNotRegex(src(*j["cmd"][0].split("/")), r"(?m)^import requests|^from requests", name)

    def test_the_battery_files_are_kept_when_nothing_moved(self):
        for name in ("battery_dispatch_export", "battery_scenario_steps"):
            self.assertEqual(scheduled.DATA_MACHINE[name]["cmd"][1:], ["--keep-same"], name)

    def test_a_data_machines_step_refuses_anywhere_else(self):
        held = lambda t: True  # noqa: E731
        self.assertIn("GitHub runner", scheduled.where(env={"GITHUB_ACTIONS": "true"}, role="data", held=held))
        self.assertIn("role is 'code', not data", scheduled.where(env={}, role="code", held=held))
        self.assertIn("ercot_zone_prices_history", scheduled.where(env={}, role="data", held=lambda t: t != "ercot_zone_prices_history"))
        self.assertEqual(scheduled.where(env={}, role="data", held=held), "")
        ran, restored = [], []
        with mock.patch("builtins.print") as out, mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}):
            rc = scheduled.step("ercot_rtm_node_prices", run=lambda *a, **k: ran.append(a), restore=lambda t: restored.append(t),
                                where=lambda: "this is the GitHub runner (GITHUB_ACTIONS is true): it holds no price history")
        self.assertEqual((rc, ran, restored), (75, [], []))     # a skip with its reason: nothing asked for, nothing rebuilt
        self.assertTrue(str(out.call_args_list[-1].args[0]).startswith("ercot_rtm_node_prices SKIPPED: this is the GitHub runner"))

    def test_the_runner_starts_none_of_them(self):
        for f in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            text = src(".github", "workflows", f)
            self.assertNotIn("ercot_rt_spp", text, f)
            self.assertNotIn("run_data_machine", text, f)
        for f in ("run_daily.sh", "run_monthly.sh"):
            text = src("warehouse", f)
            self.assertNotIn("ercot_rt_spp", text, f)
            for name in STEPS:
                self.assertNotIn(f"scheduled.py {name}", text, f"{f}: {name}")

    def test_the_node_table_is_in_no_live_set(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        self.assertIn("ercot_rtm_node_prices", live["catalogue_hold"])
        loaded = list(live["full"]) + [r if isinstance(r, str) else str(r) for r in live.get("recent", [])] + [str(r) for r in live.get("select", [])]
        for rule in loaded:
            self.assertNotIn("ercot_rtm_node", rule)
        for rule in live["full"]:
            self.assertIsNone(re.search(rule, "ercot_rtm_node_prices"), rule)


class TheRun(unittest.TestCase):
    def setUp(self):
        self.text = src("warehouse", "run_data_machine.sh")
        self.body = self.text.split("set -uo pipefail", 1)[1]

    def at(self, s):
        self.assertEqual(self.body.count(s), 1, s)
        return self.body.index(s)

    def test_each_new_step_is_a_soft_step_through_the_schedule(self):
        for name in STEPS:
            step = "dm_ercot_node_prices" if name == "ercot_rtm_node_prices" else f"dm_{name}"
            target = '"$NODES"' if name == "ercot_rtm_node_prices" else name
            self.at(f'soft_step {step} "$PYTHON" warehouse/scheduled.py {target}')
        self.assertIn("NODES=ercot_rtm_node_prices\n", self.body)
        self.assertNotIn("--strict", self.body)

    def test_the_order(self):
        sync, zones = self.at("soft_step dm_sync"), self.at("soft_step dm_ercot_zone_prices")
        rollup, nodes = self.at("soft_step dm_storage_rollup"), self.at("soft_step dm_ercot_node_prices")
        self.assertLess(sync, rollup)
        self.assertLess(rollup, nodes)
        self.assertLess(nodes, zones)                     # a listed day is lost for good after a week: the pull goes first
        commit = self.at("# ---- 4. the commit")
        export = self.at("soft_step dm_datacenter_export")
        capture_test = self.at("page_test dm_test_capture test-capture.mjs")
        first = self.at("soft_step dm_battery_dispatch_export")
        self.assertLess(export, first)
        self.assertLess(capture_test, self.at("soft_step dm_merchant_revenue"))   # the capture file is final before the generator's builders read it
        for name in ("dm_battery_scenario_steps", "dm_merchant_revenue", "dm_merchant_hubs", "dm_generator_hourly_export", "dm_seller_hybrid"):
            self.assertLess(first, self.at(f"soft_step {name}") + 1)
            self.assertLess(self.at(f"soft_step {name}"), commit)
        self.assertLess(self.at("soft_step dm_merchant_revenue"), self.at("soft_step dm_merchant_hubs"))
        self.assertLess(self.at("soft_step dm_merchant_hubs"), self.at("soft_step dm_generator_hourly_export"))
        self.assertLess(self.at("soft_step dm_seller_hybrid"), self.at("group dm_test_battery_dispatch"))
        self.assertLess(self.at("group dm_test_hybrid"), commit)

    def test_the_rollup_adds_the_awards_up_before_the_offers(self):
        line = next(ln for ln in self.body.splitlines() if ln.startswith("soft_step dm_storage_rollup"))
        self.assertLess(line.index("ercot_storage_dam_awards.py"), line.index("ercot_storage_dam_offers.py"))
        self.assertIn("&&", line)
        self.assertNotIn("|", line)

    def test_a_table_gets_its_stores_when_it_moved_and_only_then(self):
        self.at('table_stores dm_node_stores "$NODES" "$was"')
        self.at('table_stores dm_merchant_stores "$MERCHANT" "$was"')
        self.assertIn("MERCHANT=merchant_revenue_monthly\n", self.body)
        fn = self.body.split("table_stores() {", 1)[1].split("\n}\n", 1)[0]
        self.assertIn('if [ "$(sha_of "$table")" = "$was" ]; then', fn)
        self.assertIn('soft_step "$name" "$PYTHON" warehouse/table_stores.py "$table"', fn)
        # each "was" is taken just before the step that writes the table
        for step in ("soft_step dm_ercot_node_prices", "soft_step dm_merchant_revenue"):
            before = self.body[:self.body.index(step)].rstrip().splitlines()[-1].strip()
            self.assertRegex(before, r'^was="\$\(sha_of "\$[A-Z]+"\)"$')

    def test_the_snapshots_group_is_switched_off_and_one_word_turns_it_on(self):
        # six tests on main hold the generator's CSV to its export of 7 October 2026; the snapshot, its table, the hub
        # files and the CSV move together or not at all, so the three steps wait behind GENERATOR=1 (the note in the script)
        on = self.body.split('if [ "${GENERATOR:-0}" = "1" ]; then', 1)[1].split("\nfi\n", 1)[0]
        steps, off = on.split("\nelse\n", 1)
        for name in ("dm_merchant_revenue", "dm_merchant_hubs", "dm_generator_hourly_export"):
            self.assertIn(f"soft_step {name} ", steps)
            self.assertNotIn(f"soft_step {name} ", off)
        self.assertIn("table_stores dm_merchant_stores", steps)
        self.assertIn('skipped: switched off until the tests that hold the CSV to its export of 7 October 2026 are changed (GENERATOR=1)', off)
        self.assertNotIn("soft_step dm_seller_hybrid", on)          # the hybrid's hours are not of that group: every day
        self.assertEqual(self.body.count('if [ "${GENERATOR:-0}" = "1" ]; then'), 2)   # the steps, and their group's tests
        self.assertLess(self.body.index("GENERATOR_OK=0"), self.body.index('git add -- "$RECORD_PATH"'))
        for words in ("tests/test_session183_replication.py", "tests/test_session199.py", "72,384 rows", "SESSION_204_REPORT.md"):
            self.assertIn(words, self.body)

    def test_a_group_whose_step_or_test_failed_is_put_back_whole(self):
        fn = self.body.split("group() {", 1)[1].split("\n}\n", 1)[0]
        self.assertIn('"$PYTHON" -m unittest $tests > "runs/data_machine_${name}.out" 2>&1\n    rc=$?', fn)   # not piped; its own exit code read
        self.assertIn('git checkout -- "$@"', fn)
        self.assertIn('warehouse/health.py record --step "$name" --status failed', fn)
        calls = self.body.split("\n}\n", self.body.count("\n}\n"))[-1]
        gen = re.search(r'group dm_test_generator "([^"]+)" \\\n\s+"([^"]+)" -- \\\n\s+(.+?) \|\| GENERATOR_OK=0', self.body)
        self.assertEqual(gen.group(1).split(), ["dm_merchant_revenue", "dm_merchant_hubs", "dm_generator_hourly_export"])
        self.assertEqual(gen.group(3).split(), ["site/data/merchant_snapshot.json", "site/data/seller/hubs", "site/public/seller/erw_2026_generator_hourly.csv"])
        for module in gen.group(2).split() + ["tests.test_session178", "tests.test_session179", "tests.test_session162"]:
            self.assertTrue(os.path.exists(os.path.join(ROOT, *module.split(".")) + ".py"), module)
        self.assertIn('group dm_test_battery_dispatch "dm_battery_dispatch_export" "tests.test_session178" -- site/public/battery/erw_2026_battery_dispatch.csv', calls)
        self.assertIn('group dm_test_battery_steps "dm_battery_scenario_steps" "tests.test_session179" -- site/data/battery_scenario_steps.json', calls)
        self.assertIn('group dm_test_hybrid "dm_seller_hybrid" "tests.test_session162" -- site/data/seller/hybrid.json site/public/seller/prices', calls)

    def test_the_commit_names_the_new_files(self):
        paths = self.text.split("PAGE_PATHS=(", 1)[1].split(")", 1)[0].split()
        for p in ("site/public/battery/erw_2026_battery_dispatch.csv", "site/data/battery_scenario_steps.json", "site/data/merchant_snapshot.json",
                  "site/data/seller/hubs", "site/public/seller/erw_2026_generator_hourly.csv", "site/data/seller/hybrid.json", "site/public/seller/prices"):
            self.assertIn(p, paths)
        self.assertIn("RECORD_PATH=docs/methods/figures\n", self.text)
        self.assertIn('[ "${GENERATOR_OK:-0}" = "1" ] && [ -e "$RECORD_PATH" ] && git add -- "$RECORD_PATH"', self.body)
        self.assertNotIn("git add -A", self.text)
        self.assertNotIn("warehouse/output", " ".join(paths))

    def test_the_script_is_sound_and_says_what_it_would_run(self):
        if not BASH:
            self.skipTest("bash is not on this machine")
        import subprocess
        r = subprocess.run([BASH, "-n", "warehouse/run_data_machine.sh"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertIn("ERCOT's node prices (scheduled.py ercot_rtm_node_prices, 500,000 rows a day at most)", self.body)
        self.assertIn("The data machine's daily run since session 204", src("docs", "machines.md"))


class TheStores(unittest.TestCase):
    class Done:
        def __init__(self, rc):
            self.returncode = rc

    def run_with(self, codes):
        ran, lines = [], []
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)

        def run(cmd, **kw):
            step = os.path.basename(cmd[1])
            ran.append(step)
            self.assertNotIn("|", " ".join(cmd))
            return self.Done(codes.get(step, 0))
        ok = table_stores.stores("ercot_rtm_node_prices", run=run, log=lines.append, runs=tmp)
        return ok, ran, lines

    def test_the_four_in_order(self):
        steps = table_stores.commands("merchant_revenue_monthly")
        self.assertEqual([(s, g) for s, g, _ in steps], [("validate", True), ("coverage", True), ("archive", False), ("redivis", False)])
        self.assertEqual(steps[0][2], ["warehouse/validate/erw_validate.py", "warehouse/output/merchant_revenue_monthly.csv"])
        self.assertEqual(steps[1][2][1:], ["--only", "^merchant_revenue_monthly$"])
        self.assertEqual(steps[2][2][1:], ["write", "--tables", "^merchant_revenue_monthly$"])
        self.assertEqual(steps[3][2][1:], ["--tables", "merchant_revenue_monthly"])
        ok, ran, _ = self.run_with({})
        self.assertEqual((ok, ran), (True, ["erw_validate.py", "build_coverage.py", "archive.py", "upload.py"]))

    def test_a_table_the_validator_blocks_reaches_no_store(self):
        ok, ran, lines = self.run_with({"erw_validate.py": 1})
        self.assertEqual((ok, ran), (False, ["erw_validate.py"]))
        self.assertIn("FAILED: validate exited 1, a gate", lines[-1])
        ok, ran, _ = self.run_with({"build_coverage.py": 1})
        self.assertEqual((ok, ran), (False, ["erw_validate.py", "build_coverage.py"]))

    def test_the_archive_failing_does_not_keep_the_draft_from_being_tried(self):
        ok, ran, _ = self.run_with({"archive.py": 1})
        self.assertEqual((ok, ran), (False, ["erw_validate.py", "build_coverage.py", "archive.py", "upload.py"]))

    def test_it_releases_nothing_loads_nothing_and_knows_a_table_by_its_file(self):
        text = src("warehouse", "table_stores.py")
        self.assertNotIn("supabase", text.split('"""', 2)[2])
        self.assertNotIn("release", text.split('"""', 2)[2])
        with mock.patch("builtins.print"):
            self.assertEqual(table_stores.main(["a_table_that_is_not_here"]), 2)
            self.assertEqual(table_stores.main(["a_table_that_is_not_here", "--dry-run"]), 0)
        with self.assertRaises(SystemExit), mock.patch("sys.stderr"):
            table_stores.main(["../outside"])


class KeptWhenNothingMoved(unittest.TestCase):
    def test_the_dispatch_csv_is_the_same_but_for_its_two_dated_lines(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        body = "# Window: local (Central) months 2023-10 to 2026-09\nhour_utc,price\n2023-10-01T05:00:00Z,18.705\n"

        def write(name, retrieved, exported, body=body):
            with open(os.path.join(tmp, name), "w", encoding="utf-8", newline="\n") as f:
                f.write(f"# Retrieved (UTC) as each table's own header states: {retrieved}\n# Exported: {exported} (UTC)\n" + body)
            return os.path.join(tmp, name)
        a = write("a.csv", "battery_stack_monthly 20261010T150928Z", "2026-10-10T08:06:34Z")
        b = write("b.csv", "battery_stack_monthly 20261011T153437Z", "2026-10-12T09:09:43Z")
        self.assertTrue(bde.same_but_stamps(a, b))
        c = write("c.csv", "battery_stack_monthly 20261011T153437Z", "2026-10-12T09:09:43Z", body.replace("18.705", "18.706"))
        self.assertFalse(bde.same_but_stamps(a, c))       # one hour moved
        d = write("d.csv", "battery_stack_monthly 20261011T153437Z", "2026-10-12T09:09:43Z", body.replace("2026-09", "2026-10"))
        self.assertFalse(bde.same_but_stamps(a, d))       # the window moved
        self.assertFalse(bde.same_but_stamps(a, os.path.join(tmp, "not_there.csv")))

    def test_the_steps_file_is_the_same_but_for_when(self):
        held = {"built": "2026-10-10T08:43:26Z", "retrieved": {"battery_stack_monthly": "20261010T150928Z"}, "model": {"sha256": "ab"},
                "rte_steps": [86, 89, 92], "cases": {"ercot|foresight|4": {"months": ["2026-09"], "cells": {"86|1": [1234.5678]}}}}
        new = json.loads(json.dumps(held))
        new.update(built="2026-10-12T09:23:00Z", retrieved={"battery_stack_monthly": "20261011T153437Z"})
        self.assertTrue(bss.same_but_when(held, new))
        new["cases"]["ercot|foresight|4"]["cells"]["86|1"] = [1234.5679]
        self.assertFalse(bss.same_but_when(held, new))    # a month of a cell moved
        new = json.loads(json.dumps(held))
        new["model"]["sha256"] = "cd"
        self.assertFalse(bss.same_but_when(held, new))    # the model changed
        self.assertEqual(bss.WHEN, ("built", "retrieved"))


class House(unittest.TestCase):
    FILES = ["tests/test_session204.py", "warehouse/table_stores.py", "warehouse/scheduled.py", "warehouse/run_data_machine.sh",
             "warehouse/connectors/ercot_rt_spp.py", "warehouse/derived/battery_dispatch_export.py", "warehouse/derived/battery_scenario_steps.py",
             "archive/sessions/LAST_ANSWERED", "docs/machines.md"]

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in self.FILES:
            self.assertNotIn(chr(0x2014), src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
