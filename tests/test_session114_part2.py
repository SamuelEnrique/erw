"""Session 114, part two: the builders that were run by hand, on a schedule.

Energy Research Warehouse (ERW). What is held here:
- the daily run starts the network's replay and the two EIA-930 daily tables it reads, and the monthly job the other six,
  each under warehouse/health.py without --strict, so a failure is recorded and never fails the run;
- the monthly job runs with the daily run of the third of the month, or with MONTHLY=1;
- a step whose inputs are not on the machine is a skip with the reason: it builds nothing and asks no one;
- the two connectors' --days merge adds and replaces days and never starts or shrinks a table (real rows, no request);
- the replay's daily build keeps what the file held and refuses a poorer file;
- each of the seven pages prints the built stamp of the file it reads, and stays in review.

No test here makes a request or writes to warehouse/output or to a shared store.
"""
import datetime as dt
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import health  # noqa: E402
import iso_prices as ip  # noqa: E402
import scheduled  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "session114")
DAILY = ["eia930_daily_interchange", "eia930_daily_demand", "network_replay"]
MONTHLY = ["mix_profile", "price_compare", "demand_growth", "curtailment_profile", "project_map", "large_load_snapshot"]
BASH = shutil.which("bash")


def text(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Schedule(unittest.TestCase):
    def test_the_daily_run_starts_the_replay_after_its_inputs(self):
        sh = text("warehouse", "run_daily.sh")
        at = [sh.index(f'soft_step {n} "$PYTHON" warehouse/scheduled.py {n}') for n in DAILY]
        self.assertEqual(at, sorted(at), "the two tables are extended before the replay is built")
        # after the consolidated price tables and the hub history the replay reads, before the validator
        self.assertLess(sh.index("warehouse/consolidate.py build"), at[0])
        self.assertLess(sh.index("warehouse/connectors/hub_history.py append"), at[0])
        self.assertLess(at[-1], sh.index('echo "== connector status"'))
        self.assertLess(sh.index(". warehouse/soft_step.sh"), at[0])

    def test_no_scheduled_builder_is_strict(self):
        for line in text("warehouse", "run_daily.sh").splitlines() + text("warehouse", "run_monthly.sh").splitlines():
            if "scheduled.py" in line and "--monthly-due" not in line and not line.lstrip().startswith("#"):
                self.assertNotIn("--strict", line)
                self.assertIn("soft_step", line)
        soft = text("warehouse", "soft_step.sh")
        call = [ln for ln in soft.splitlines() if "warehouse/health.py run" in ln and not ln.lstrip().startswith("#")]
        self.assertEqual(len(call), 1)
        self.assertNotIn("--strict", call[0])
        self.assertIn("return 0", soft)

    def test_the_monthly_job_holds_the_six(self):
        sh = text("warehouse", "run_monthly.sh")
        loop = re.search(r"^for name in (.+); do$", sh, re.M).group(1).split()
        self.assertEqual(sorted(loop), sorted(MONTHLY))
        self.assertEqual(sorted(n for n, j in scheduled.JOBS.items() if j["cadence"] == "monthly"), sorted(MONTHLY))
        self.assertEqual(sorted(n for n, j in scheduled.JOBS.items() if j["cadence"] == "daily"), sorted(DAILY))

    def test_every_step_names_a_script_that_exists_and_only_eia_is_asked(self):
        for name, j in scheduled.JOBS.items():
            self.assertTrue(os.path.exists(os.path.join(ROOT, j["cmd"][0])), name)
            self.assertLessEqual(set(j.get("restore", [])), set(j.get("tables", [])), name)
        asks = sorted(n for n, j in scheduled.JOBS.items() if "/connectors/" in j["cmd"][0])
        self.assertEqual(asks, ["eia930_daily_demand", "eia930_daily_interchange"], "no other step runs a connector")
        for n in asks:
            self.assertEqual(scheduled.JOBS[n]["cmd"][1:], ["--days", scheduled.REPLAY_DAYS])
        # a builder that reads a table makes no request: none of them imports requests
        for name, j in scheduled.JOBS.items():
            if "/derived/" in j["cmd"][0]:
                self.assertNotRegex(text(*j["cmd"][0].split("/")), r"(?m)^import requests|^from requests", name)

    def test_the_workflow_commits_what_the_schedule_rebuilds(self):
        wf = text(".github", "workflows", "daily-prices.yml")
        for p in ("site/public/network/daily_index.json", "site/data/mix", "site/data/price_compare.json", "site/data/demand_growth.json",
                  "site/data/curtailment_profile.json", "site/data/map_v2.json", "site/data/large_load_status.json", "site/public/network/daily_2*.json"):
            self.assertIn(p, wf)
        self.assertIn("MONTHLY: ${{ github.event.inputs.monthly || '0' }}", wf)

    def test_the_monthly_job_is_due_from_the_third_until_it_has_run(self):
        sh = text("warehouse", "run_daily.sh")
        cond = [ln for ln in sh.splitlines() if "MONTHLY:-0" in ln and ln.startswith("if ")]
        self.assertEqual(cond, ['if [ "${MONTHLY:-0}" = "1" ] || "$PYTHON" warehouse/scheduled.py --monthly-due; then'])
        self.assertIn("bash warehouse/run_monthly.sh", sh[sh.index(cond[0]):sh.index(cond[0]) + 200])
        with tempfile.TemporaryDirectory() as tmp:
            mark = os.path.join(tmp, "demand_growth.json")

            def due(day, built=None):
                if built is None:
                    if os.path.exists(mark):
                        os.remove(mark)
                else:
                    with open(mark, "w", encoding="utf-8") as f:
                        json.dump({"built": built}, f)
                return scheduled.monthly_due(dt.date.fromisoformat(day), mark)[0]
            self.assertFalse(due("2026-11-01", "2026-10-05T02:07:00Z"), "before the third: the month before may not be whole")
            self.assertFalse(due("2026-11-02", "2026-10-05T02:07:00Z"))
            self.assertTrue(due("2026-11-03", "2026-10-05T02:07:00Z"))
            self.assertTrue(due("2026-11-09", "2026-10-05T02:07:00Z"), "a daily run missed on the third does not cost the month")
            self.assertFalse(due("2026-11-04", "2026-11-03T14:40:00Z"), "once it has run, not again that month")
            self.assertFalse(due("2026-11-30", "2026-11-03T14:40:00Z"))
            self.assertTrue(due("2026-12-03", "2026-11-03T14:40:00Z"))
            self.assertTrue(due("2027-01-03", "2026-12-03T14:40:00Z"))
            self.assertTrue(due("2026-11-03"), "no stamp to read: due")
            self.assertFalse(due("2026-11-02"))

    @unittest.skipUnless(BASH, "bash is not on this machine")
    def test_forcing_the_monthly_job_does_not_ask_whether_it_is_due(self):
        sh = text("warehouse", "run_daily.sh")
        cond = [ln for ln in sh.splitlines() if "MONTHLY:-0" in ln and ln.startswith("if ")][0]
        script = "\n".join([cond, "  echo yes", "else", "  echo no", "fi", ""])

        def said(monthly, due):
            env = {**os.environ, "PYTHON": "true" if due else "false"}   # stands for scheduled.py --monthly-due: exit 0 or 1
            env.pop("MONTHLY", None)
            if monthly is not None:
                env["MONTHLY"] = monthly
            return subprocess.run([BASH, "-c", script], env=env, capture_output=True, text=True).stdout.strip()
        self.assertEqual(said("1", False), "yes")
        self.assertEqual(said(None, True), "yes")
        self.assertEqual(said(None, False), "no")
        self.assertEqual(said("0", False), "no")


class SoftStep(unittest.TestCase):
    """A failure is recorded and never fails the run."""

    def run_health(self, code, lines=()):
        rec = []
        out = health.run("a step", ["x"], retries=1, wait=0, strict=False, attempt=lambda cmd: (code, list(lines), 0.1), sleep=lambda s: None,
                         rec=lambda step, status, why, secs: rec.append((step, status, why)))
        return out, rec

    def test_a_failure_is_recorded_and_the_exit_is_zero(self):
        (rc, status), rec = self.run_health(1, ["Traceback", "RuntimeError: no"])
        self.assertEqual((rc, status), (0, "failed"))
        self.assertEqual(rec, [("a step", "failed", "RuntimeError: no")])

    def test_a_skip_is_recorded_with_its_reason(self):
        (rc, status), rec = self.run_health(health.SKIP, ["mix_profile SKIPPED: the table x is not on this machine"])
        self.assertEqual((rc, status), (0, "skipped"))
        self.assertIn("not on this machine", rec[0][2])

    @unittest.skipUnless(BASH, "bash is not on this machine")
    def test_the_status_file_says_what_happened_and_the_run_goes_on(self):
        said = {"bad": "::warning title=bad failed after a retry::RuntimeError: no", "away": "::notice::away skipped: away SKIPPED: the table x is not on this machine",
                "fine": "mix_profile.csv: rows=1"}
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "runs"))
            stub = os.path.join(tmp, "fakepython")
            with open(stub, "w", encoding="utf-8", newline="\n") as f:  # stands for "$PYTHON warehouse/health.py run --step <name> ..."
                f.write("#!/usr/bin/env bash\ncase \"$4\" in\n" + "".join(f"  {k}) echo '{v}';;\n" for k, v in said.items()) + "esac\nexit 0\n")
            os.chmod(stub, 0o755)
            soft = os.path.join(ROOT, "warehouse", "soft_step.sh").replace("\\", "/")
            # the real function, with the stub as its Python
            script = (f'cd "{tmp.replace(chr(92), "/")}"; status=runs/s.txt; PYTHON=./fakepython; . "{soft}"\n'
                      'for n in bad away fine; do soft_step "$n" echo; echo "rc=$?"; done\ncat runs/s.txt\n')
            r = subprocess.run([BASH, "-c", script], capture_output=True, text=True)
            out = r.stdout
        self.assertEqual(out.count("rc=0"), 3, out + r.stderr)
        self.assertIn("bad failed: RuntimeError: no (recorded in erw_health; the run goes on)", out)
        self.assertIn("away skipped: the table x is not on this machine", out)
        self.assertIn("fine ok", out)


class SkipWithoutInputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p1 = mock.patch.object(scheduled.ip, "OUT_DIR", self.tmp)
        p2 = mock.patch.object(scheduled, "RAW_930", os.path.join(self.tmp, "raw"))
        p1.start(), p2.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)
        self.ran = []

    def run_cmd(self, cmd, **kw):
        self.ran.append(cmd)
        return mock.Mock(returncode=0)

    def step(self, name, restore=lambda t: False, env=None):
        import contextlib
        import io
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env or {"ERW_SKIP_EXIT": "75"}), contextlib.redirect_stdout(buf):
            rc = scheduled.step(name, run=self.run_cmd, restore=restore)
        return rc, buf.getvalue()

    def test_the_price_comparison_without_the_ercot_history_builds_nothing(self):
        for t in scheduled.JOBS["price_compare"]["tables"]:
            if t != "ercot_all_hub_prices_history":
                open(os.path.join(self.tmp, t + ".csv"), "w").close()
        rc, out = self.step("price_compare")
        self.assertEqual(rc, 75)
        self.assertEqual(self.ran, [])
        self.assertIn("price_compare SKIPPED: the table ercot_all_hub_prices_history is not on this machine", out)

    def test_by_hand_a_skip_is_exit_zero_with_the_same_line(self):
        rc, out = self.step("demand_growth", env={"ERW_SKIP_EXIT": ""})
        self.assertEqual(rc, 0)
        self.assertEqual(self.ran, [])
        self.assertIn("demand_growth SKIPPED: EIA-930's CISO workbook", out)
        self.assertIn("US48", out)

    def test_a_missing_table_is_rebuilt_from_the_archive_where_the_step_allows_it(self):
        asked = []

        def restore(t):
            asked.append(t)
            open(os.path.join(self.tmp, t + ".csv"), "w").close()
            return True
        rc, _ = self.step("project_map", restore=restore)
        self.assertEqual(rc, 0)
        self.assertEqual(asked, ["eia860m_operating_generators", "eia860m_planned_generators"])
        self.assertEqual(len(self.ran), 1)
        self.assertTrue(self.ran[0][1].replace("\\", "/").endswith("warehouse/derived/project_map.py"))

    def test_a_table_the_archive_cannot_give_is_a_skip(self):
        rc, out = self.step("large_load_snapshot")
        self.assertEqual(rc, 75)
        self.assertEqual(self.ran, [])
        self.assertIn("ercot_large_load_status", out)

    def test_a_table_that_may_not_be_rebuilt_is_never_asked_of_the_archive(self):
        asked = []
        self.step("price_compare", restore=lambda t: asked.append(t) or False)
        self.step("mix_profile", restore=lambda t: asked.append(t) or False)
        self.assertEqual(asked, [])

    def test_check_runs_and_rebuilds_nothing(self):
        asked = []
        with mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}):
            rc = scheduled.step("project_map", check=True, run=self.run_cmd, restore=lambda t: asked.append(t) or True)
        self.assertEqual((rc, asked, self.ran), (75, [], []))


class DaysMerge(unittest.TestCase):
    """--days on the two EIA-930 daily connectors, on real rows (tests/fixtures/session114), with EIA played by the fixture."""

    def table(self, name, upto):
        """A table in a scratch folder holding the fixture's rows up to a day; returns (folder, every fixture row)."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        src = os.path.join(FIX, name + "_excerpt.csv")
        rows = pd.read_csv(src, skiprows=ip.header_rows(src), dtype=str, keep_default_na=False)
        held = rows[rows["ts_utc"].str[:10] <= upto]
        with open(os.path.join(tmp, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# a test's table: real rows of the warehouse, the fixture's first days\n")
            held.to_csv(f, index=False, lineterminator="\n")
        return tmp, rows, held

    def api(self, name, rows):
        if name == "eia930_daily_interchange":
            pair = rows["entity"].str[7:].str.split("-")
            return pd.DataFrame({"period": rows["ts_utc"].str[:10], "fromba": pair.str[0], "toba": pair.str[1], "value": rows["value"],
                                 "_url": rows["source_url"], "_retrieved": rows["retrieved_at"]})
        return pd.DataFrame({"period": rows["ts_utc"].str[:10], "respondent": rows["entity"].str[7:], "type": "D", "value": rows["value"],
                             "_url": rows["source_url"], "_retrieved": rows["retrieved_at"]})

    def merge(self, name):
        conn = __import__(name)
        days = sorted(self.rows_of_fixture(name)["ts_utc"].str[:10].unique())
        tmp, rows, held = self.table(name, days[2])               # the table holds the first three days
        asked_from = days[1]                                      # EIA is asked again from the second
        answer = rows[rows["ts_utc"].str[:10] >= asked_from]
        today = dt.date.fromisoformat(asked_from) + dt.timedelta(days=5)
        was = ip.OUT_DIR
        ip.set_out_dir(tmp)
        self.addCleanup(ip.set_out_dir, was)
        log = ip.Log(os.path.join(tmp, "log.txt"))
        self.addCleanup(log.close)
        with mock.patch.object(conn, "month", return_value=self.api(name, answer)) as month, mock.patch.object(ip, "load_key", return_value="none"), \
                mock.patch.object(ip.RAW, "open"), mock.patch.object(ip, "update_sources"):
            msg = conn.recent(5, "20261005T000000Z", log, today=today)
        self.assertEqual(month.call_args[0][1:3], (asked_from, "2099-12-31"))
        path = os.path.join(tmp, name + ".csv")
        got = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
        return rows, held, got, msg

    def rows_of_fixture(self, name):
        src = os.path.join(FIX, name + "_excerpt.csv")
        return pd.read_csv(src, skiprows=ip.header_rows(src), dtype=str, keep_default_na=False)

    def check(self, name):
        rows, held, got, msg = self.merge(name)
        key = ["entity", "variable", "ts_utc"]
        self.assertGreater(len(got), len(held))
        self.assertEqual(len(got), len(rows), "every day of the fixture, each once")
        self.assertFalse(got.duplicated(key).any())
        a, b = rows.sort_values(key).reset_index(drop=True), got.sort_values(key).reset_index(drop=True)
        self.assertEqual(list(a.columns), list(b.columns))
        self.assertTrue((a["value"].astype(float) == b["value"].astype(float)).all(), "a value is EIA's, never changed by the merge")
        self.assertTrue((a[key + ["unit", "freq", "source", "ba"]] == b[key + ["unit", "freq", "source", "ba"]]).all().all())
        self.assertIn(f"{len(rows) - len(held)} new", msg)

    def test_daily_demand_takes_the_new_days_and_keeps_the_rest(self):
        self.check("eia930_daily_demand")

    def test_daily_interchange_takes_the_new_days_and_keeps_the_rest(self):
        self.check("eia930_daily_interchange")

    def test_without_the_table_nothing_is_asked_and_nothing_is_started(self):
        for name in ("eia930_daily_demand", "eia930_daily_interchange"):
            conn = __import__(name)
            tmp = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, tmp, True)
            was = ip.OUT_DIR
            ip.set_out_dir(tmp)
            self.addCleanup(ip.set_out_dir, was)
            with mock.patch.object(conn, "get") as get, mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}), mock.patch("builtins.print") as said:
                rc = conn.main(["--days", "5"])
            self.assertEqual(rc, 75)
            get.assert_not_called()
            self.assertIn("SKIPPED", said.call_args[0][0])
            self.assertEqual([f for f in os.listdir(tmp) if f.endswith(".csv")], [])

    def test_an_empty_answer_writes_nothing(self):
        conn = __import__("eia930_daily_demand")
        tmp, rows, held = self.table("eia930_daily_demand", "2099-01-01")
        was = ip.OUT_DIR
        ip.set_out_dir(tmp)
        self.addCleanup(ip.set_out_dir, was)
        log = ip.Log(os.path.join(tmp, "log.txt"))
        self.addCleanup(log.close)
        before = open(os.path.join(tmp, "eia930_daily_demand.csv"), encoding="utf-8").read()
        with mock.patch.object(conn, "month", return_value=pd.DataFrame()), mock.patch.object(ip, "load_key", return_value="none"), mock.patch.object(ip.RAW, "open"):
            with self.assertRaises(RuntimeError):
                conn.recent(5, "20261005T000000Z", log, today=dt.date(2026, 10, 5))
        self.assertEqual(open(os.path.join(tmp, "eia930_daily_demand.csv"), encoding="utf-8").read(), before)


class Replay(unittest.TestCase):
    """The daily build of the replay: what the file held is kept, and a poorer file is refused. The values are a test's."""

    def setUp(self):
        import network_daily
        self.nd = network_daily
        self.old = dict(days=["d1", "d2", "d3"], links=[dict(a="A", b="B", mw=[1.0, 2.0, None])], intensity={"A": [5.0, 5.0, 5.0]},
                        demand={"A": [9.0, 9.0, 9.0]}, hub_prices={"A": [30.0, 31.0, None]})

    def new(self, **over):
        y = dict(days=["d1", "d2", "d3", "d4"], links=[dict(a="A", b="B", mw=[1.0, 2.0, None, 4.0])], intensity={"A": [5.0, 5.0, 5.0, 5.0]},
                 demand={"A": [9.0, 9.0, 9.0, 9.0]}, hub_prices={"A": [None, None, 32.0, 33.0]})
        y.update(over)
        return y

    def test_a_price_the_build_lacks_is_kept_from_the_file_and_counted(self):
        y = self.new()
        self.assertEqual(self.nd.keep_prices(y, self.old), 2)
        self.assertEqual(y["hub_prices"]["A"], [30.0, 31.0, 32.0, 33.0])
        self.assertEqual(self.nd.poorer(y, self.old), {})

    def test_a_price_the_build_has_is_never_replaced_by_the_files(self):
        y = self.new(hub_prices={"A": [40.0, None, None, None]})
        self.nd.keep_prices(y, self.old)
        self.assertEqual(y["hub_prices"]["A"], [40.0, 31.0, None, None])

    def test_a_hub_the_build_lacks_whole_is_kept(self):
        y = self.new(hub_prices={})
        self.assertEqual(self.nd.keep_prices(y, self.old), 2)
        self.assertEqual(y["hub_prices"]["A"], [30.0, 31.0, None, None])

    def test_a_poorer_file_is_named(self):
        y = self.new(demand={}, links=[dict(a="A", b="B", mw=[None, None, None, 4.0])])
        self.nd.keep_prices(y, self.old)
        self.assertEqual(self.nd.poorer(y, self.old), {"flows": (2, 0), "demand": (3, 0)})

    def test_the_replay_on_the_site_is_whole(self):
        idx = json.loads(text("site", "public", "network", "daily_index.json"))
        years = list(idx["years"])
        self.assertEqual(years, sorted(years))
        self.assertEqual(years[0], "2019")
        self.assertEqual(idx["years"][years[-1]]["last"], idx["last"])
        for y, e in idx["years"].items():
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "public", e["file"].lstrip("/"))), y)
        newest = json.loads(text("site", "public", "network", f"daily_{years[-1]}.json"))
        self.assertEqual(newest["days"][-1], idx["last"])
        self.assertIn("hub_price_days_kept", newest["missing"])
        dt.datetime.strptime(idx["built"], "%Y-%m-%dT%H:%M:%SZ")


class BuiltDate(unittest.TestCase):
    """Each of the seven pages prints the built stamp of the file it reads (never the time the page was drawn)."""
    PAGES = {  # page: (its source, the expression that prints the stamp, the files that carry it)
        "/network/v3": ("site/app/network/v3/page.tsx", "built {utc(index.built)}", ["site/public/network/daily_index.json"]),
        "/mix/v2": ("site/app/mix/v2/page.tsx", "built {file.built.slice(0, 10)}", [f"site/data/mix/{g}.json" for g in ("caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp")]),
        "/prices/compare": ("site/app/prices/compare/page.tsx", "Built {file.built.slice(0, 10)}", ["site/data/price_compare.json"]),
        "/demand": ("site/app/demand/page.tsx", "built {file.built.slice(0, 10)}", ["site/data/demand_growth.json"]),
        "/curtailment/v2": ("site/app/curtailment/v2/page.tsx", "Built {file.built.slice(0, 10)}", ["site/data/curtailment_profile.json"]),
        "/map/v2": ("site/app/map/v2/page.tsx", "built {f.built.slice(0, 10)}", ["site/data/map_v2.json"]),
        "/datacenters/v2": ("site/app/datacenters/v2/page.tsx", "built {f.built.slice(0, 10)}", ["site/data/large_load_status.json"]),
    }

    def test_each_page_prints_its_files_built_stamp(self):
        self.assertEqual(sorted(self.PAGES), sorted({j["page"] for j in scheduled.JOBS.values()}))
        for page, (src, expr, files) in self.PAGES.items():
            self.assertIn(expr, text(*src.split("/")), page)
            for f in files:
                built = json.loads(text(*f.split("/")))["built"]
                at = dt.datetime.strptime(built, "%Y-%m-%dT%H:%M:%SZ")
                self.assertLessEqual(at, dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(minutes=5), f)

    def test_the_stamp_is_the_builders_own(self):
        for script in ("network_daily.py", "project_map.py", "large_load_snapshot.py"):
            self.assertIn('ip.utc_iso(pd.Timestamp.now(tz="UTC"))', text("warehouse", "derived", script), script)
        for script in ("mix_profile.py", "price_compare.py", "demand_growth.py", "curtailment_profile.py"):
            self.assertRegex(text("warehouse", "derived", script), r'"?built"?[=:] ?retrieved', script)

    def test_the_seven_pages_stay_in_review(self):
        release = text("site", "lib", "release.ts")
        for page in self.PAGES:
            self.assertRegex(release, rf'"{re.escape(page)}": "review"', page)


if __name__ == "__main__":
    unittest.main()
