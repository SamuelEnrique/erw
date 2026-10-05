"""Session 119: the news products.

The Roundup's run after its email (the rendered copy's commit, the cost ledger's coverage row, the question a scheduled
start asks first); the weekly chart's chooser (a real change, ranked among the measure's own earlier changes, new this
week), its watch list over the public tables and the caption that states the finding. No network, no model.
tests/fixtures/session119/ holds real rows of four public tables, every column, unaltered.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("ERW_LOCK_EXEMPT", "1")
for p in ("warehouse/analysis", "warehouse/analysis/templates", "warehouse/news", "warehouse/connectors", "warehouse/metadata", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import email_digest as ed  # noqa: E402
import run  # noqa: E402
import templates  # noqa: E402
import watch  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session119")
NOW = pd.Timestamp("2026-10-05T09:00:00Z")
SPEC = {s["name"]: s for s in watch.WATCH}
BASH, GIT = shutil.which("bash"), shutil.which("git")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def rows(table):
    d = pd.read_csv(os.path.join(FIX, f"{table}_sample.csv"), comment="#")
    d["ts_utc"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def headline(ps, label="x", unit="u"):
    return {"label": label, "value": ps[-1][1], "unit": unit, "period": ps[-1][0], "history": ps[:-1]}


# --------------------------------------------------------------------------------------------- the Roundup's run
class TheWorkflows(unittest.TestCase):
    def test_every_workflow_file_is_yaml_a_runner_can_read(self):
        # a colon and a space inside an unquoted run line made roundup.yml unreadable in this session before it was pushed
        d = os.path.join(ROOT, ".github", "workflows")
        for f in sorted(os.listdir(d)):
            w = yaml.safe_load(src(".github", "workflows", f))
            self.assertIn("jobs", w, f)
            for name, job in w["jobs"].items():
                for step in job.get("steps", []):
                    self.assertTrue("run" in step or "uses" in step, f"{f} {name}: a step with neither run nor uses")

    def steps(self):
        w = yaml.safe_load(src(".github", "workflows", "roundup.yml"))
        return {s.get("name") or s.get("uses"): s for s in w["jobs"]["roundup"]["steps"]}

    def test_the_rendered_copy_is_committed_by_the_script_and_never_fails_the_run(self):
        send = "\n".join(ln for ln in self.steps()["Send the Roundup by email"]["run"].splitlines() if not ln.lstrip().startswith("#"))
        self.assertNotIn("git pull --rebase", send)                       # 4 October 2026: exit 128 after the email was out
        self.assertIn('python warehouse/health.py run --step "commit the rendered email" --retries 0 -- bash warehouse/news/commit_paths.sh', send)
        self.assertLess(send.index("email_digest.py --roundup"), send.index("commit_paths.sh"))
        self.assertIn('--step "send the Roundup" --retries 0', send)       # the send itself is still never tried twice

    def test_the_ledgers_coverage_row_is_rebuilt_before_its_load_and_each_step_is_recorded(self):
        led = self.steps()["Keep the cost ledger"]["run"]
        order = ["build_coverage.py --only '^api_cost_ledger$'", "archive.py write --tables '^api_cost_ledger$'",
                 "load.py --only '^api_cost_ledger$'", "upload.py api_cost_ledger"]
        at = [led.index(x) for x in order]
        self.assertEqual(at, sorted(at))
        self.assertEqual(led.count("python warehouse/health.py run --step"), 4)   # one that fails no longer stops the next

    def test_a_scheduled_start_asks_whether_the_roundup_was_sent_before_it_writes_it_again(self):
        s = self.steps()
        names = list(s)
        self.assertLess(names.index("Was this week's Roundup already sent"), names.index("Restore tables, pull fuel prices, run the analysis, write the Roundup"))
        ask = s["Was this week's Roundup already sent"]
        self.assertIn("email_digest.py --roundup --sent-check", ask["run"])
        self.assertIn("github.event_name == 'schedule'", ask["if"])
        self.assertIn("github.event.inputs.once == '1'", ask["if"])       # a person's run still writes again
        self.assertIn("steps.sent.outputs.status != 'skipped'", s["Restore tables, pull fuel prices, run the analysis, write the Roundup"]["if"])

    def test_the_watch_lists_tables_are_restored_and_a_failure_does_not_stop_the_roundup(self):
        main = self.steps()["Restore tables, pull fuel prices, run the analysis, write the Roundup"]["run"]
        self.assertIn('python scripts/sync.py --no-git --tables \\"$(python warehouse/analysis/watch.py --tables)\\" || echo', main)
        self.assertLess(main.index("upload.py --restore"), main.index("scripts/sync.py"))
        self.assertLess(main.index("scripts/sync.py"), main.index("warehouse/analysis/run.py"))


class TheSentCheck(unittest.TestCase):
    def setUp(self):
        self.get, self.env = ed.requests.get, dict(os.environ)
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"] = "https://example.supabase.co", "k"
        os.environ.pop("ERW_SKIP_EXIT", None)

    def tearDown(self):
        ed.requests.get = self.get
        os.environ.clear()
        os.environ.update(self.env)

    def fake(self, payload, status=200):
        asked = {}

        class R:
            status_code = status
            text = "x"

            def json(self_inner):
                return payload

        def get(url, **kw):
            asked.update(url=url, params=kw.get("params"))
            return R()
        ed.requests.get = get
        return asked

    def test_a_roundup_already_sent_is_a_skip_with_its_reason(self):
        # the row as it stood on 5 October 2026: sent to one recipient by run 37242113598
        asked = self.fake([{"day": "2026-10-04", "issue": "2026-W40", "status": "sent", "claimed_at": "2026-10-04T23:05:45.77473+00:00",
                            "recipients": 1, "run_id": "37242113598"}])
        self.assertEqual(ed.main(["--roundup", "--sent-check"]), 75)
        self.assertTrue(asked["url"].endswith("/rest/v1/digest_sends"))
        self.assertEqual(asked["params"]["kind"], "eq.roundup")

    def test_nothing_sent_yet_is_a_go(self):
        self.fake([])
        self.assertEqual(ed.main(["--roundup", "--sent-check"]), 0)

    def test_the_roundups_day_runs_to_monday_three_utc(self):
        # GitHub's own schedule started its run at 01:23 UTC on Monday 5 October: still Sunday's Roundup
        late = pd.Timestamp("2026-10-05T01:23:00Z").to_pydatetime()
        self.assertEqual(ed.send_day("roundup", late), "2026-10-04")
        asked = self.fake([])
        ed.already_sent("roundup", late)
        self.assertEqual(asked["params"]["day"], "eq.2026-10-04")

    def test_it_claims_nothing(self):
        s = src("warehouse", "news", "email_digest.py")
        body = s[s.index("def already_sent("):s.index("def claim(")]
        self.assertNotIn("requests.post", body)
        self.assertNotIn("requests.delete", body)


@unittest.skipUnless(BASH and GIT, "bash and git are needed")
class TheCommitScript(unittest.TestCase):
    """warehouse/news/commit_paths.sh in a real repository made for the test: a bare origin and two clones."""

    def git(self, cwd, *a, check=True):
        r = subprocess.run([GIT, "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                            "-c", "core.autocrlf=false", *a], cwd=cwd, capture_output=True, text=True)
        if check and r.returncode:
            raise AssertionError(f"git {' '.join(a)}: {r.stderr}")
        return r.stdout.strip()

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.origin, self.work, self.other = (os.path.join(self.tmp, n) for n in ("origin.git", "work", "other"))
        self.git(self.tmp, "init", "--bare", "-b", "main", self.origin)
        self.git(self.tmp, "clone", self.origin, self.work)
        os.makedirs(os.path.join(self.work, "docs", "digest", "email"))
        os.makedirs(os.path.join(self.work, "warehouse", "metadata"))
        for rel, text in (("docs/digest/email/old.html", "old\n"), ("warehouse/metadata/coverage.csv", "table,n_rows\nx,1\n")):
            with open(os.path.join(self.work, *rel.split("/")), "w", newline="\n") as f:
                f.write(text)
        self.git(self.work, "add", "-A")
        self.git(self.work, "commit", "-m", "start")
        self.git(self.work, "push", "origin", "HEAD:main")
        for k in ("user.name", "user.email"):
            self.git(self.work, "config", k, "t@example.com")
        self.git(self.work, "config", "core.hooksPath", "/dev/null")
        self.git(self.work, "config", "core.autocrlf", "false")
        self.script = os.path.join(ROOT, "warehouse", "news", "commit_paths.sh").replace("\\", "/")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_script(self, *paths):
        return subprocess.run([BASH, self.script, "Energy Roundup email rendered", "a test", *paths], cwd=self.work, capture_output=True, text=True, timeout=120)

    def the_run_leaves_its_mess(self):
        # what the Roundup's runner holds when it reaches this step: a tracked file changed by the restore, a log
        with open(os.path.join(self.work, "warehouse", "metadata", "coverage.csv"), "a", newline="\n") as f:
            f.write("y,2\n")
        with open(os.path.join(self.work, "roundup.log"), "w", newline="\n") as f:
            f.write("log\n")
        with open(os.path.join(self.work, "docs", "digest", "email", "2026-W40-roundup.html"), "w", newline="\n") as f:
            f.write("<p>the Roundup</p>\n")

    def test_it_commits_only_the_paths_with_other_changes_in_the_tree(self):
        self.the_run_leaves_its_mess()
        r = self.run_script("docs/digest/email")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.git(self.origin, "show", "--stat", "--format=%s", "main").splitlines()[0], "Energy Roundup email rendered")
        files = self.git(self.origin, "show", "--name-only", "--format=", "main").split()
        self.assertEqual(files, ["docs/digest/email/2026-W40-roundup.html"])       # the coverage change and the log are not in it
        self.assertIn("y,2", open(os.path.join(self.work, "warehouse", "metadata", "coverage.csv")).read())   # and are put back
        self.assertTrue(os.path.exists(os.path.join(self.work, "roundup.log")))

    def test_it_pulls_when_main_moved_under_it(self):
        # 4 October 2026: main had moved (the Roundup's own commit, a session's merge) and the pull refused the dirty tree
        self.git(self.tmp, "clone", self.origin, self.other)
        with open(os.path.join(self.other, "elsewhere.txt"), "w", newline="\n") as f:
            f.write("a session's commit\n")
        self.git(self.other, "add", "-A")
        self.git(self.other, "commit", "-m", "elsewhere")
        self.git(self.other, "push", "origin", "HEAD:main")
        self.the_run_leaves_its_mess()
        r = self.run_script("docs/digest/email")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        log = self.git(self.origin, "log", "--format=%s", "main").splitlines()
        self.assertEqual(log[:2], ["Energy Roundup email rendered", "elsewhere"])
        self.assertIn("y,2", open(os.path.join(self.work, "warehouse", "metadata", "coverage.csv")).read())

    def test_nothing_under_the_paths_is_nothing_to_commit(self):
        with open(os.path.join(self.work, "roundup.log"), "w", newline="\n") as f:
            f.write("log\n")
        before = self.git(self.origin, "rev-parse", "main")
        r = self.run_script("docs/digest/email")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("nothing to commit", r.stdout)
        self.assertEqual(self.git(self.origin, "rev-parse", "main"), before)

    def test_it_never_forces(self):
        s = src("warehouse", "news", "commit_paths.sh")
        code = "\n".join(ln for ln in s.splitlines() if not ln.lstrip().startswith("#"))
        self.assertNotIn("--force", code)
        self.assertNotIn(" -f ", code)


class OneTablesCoverageRow(unittest.TestCase):
    def test_the_option_carries_every_other_row_word_for_word(self):
        s = src("warehouse", "metadata", "build_coverage.py")
        self.assertIn('ap.add_argument("--only"', s)
        self.assertIn("files = [p for p in files if re.search(args.only, os.path.basename(p)[:-4])]", s)
        self.assertIn("sys.exit(main() or 0)", s)                           # a failed --only is an exit code a gate can read
        import build_coverage as bc
        r = dict(table="x_y", iso="", market="", _variable="v", n_nodes=1, _nodes="a|b", interval="P1D", ts_min="2026-01-01T00:00:00Z",
                 ts_max="2026-01-02T00:00:00Z", n_rows=1234, source_report="s;t", last_run="2026-10-05T00:00:00Z", validator_status="pass",
                 license="public", sector="power;gas", derived="no", tier="source")
        line = bc.md_line(r)
        self.assertTrue(line.startswith("| `x_y` | "))
        self.assertIn("| 1,234 |", line)
        self.assertIn("a\\|b", line)                                        # a bar inside a cell does not break the table


# --------------------------------------------------------------------------------------------- the chooser
class TheChange(unittest.TestCase):
    def test_wti_in_the_week_of_21_september_2026(self):
        ps = watch.periods(rows("eia_fuel_spot_prices"), SPEC["watch_wti"], NOW)
        self.assertEqual(ps[-2:], [["2026-09-14 to 2026-09-20", 103.54], ["2026-09-21 to 2026-09-27", 93.57]])
        h = headline(ps, SPEC["watch_wti"]["label"], "USD/bbl")
        ch = run.change(h, "previous")
        self.assertAlmostEqual(ch["delta"], -9.97, places=2)
        self.assertEqual((len(ch["earlier"]), ch["score"]), (104, 93.3))    # the last 104 weekly moves; 7 of them as large
        one, two = run.finding(h, ch, "previous")
        self.assertEqual(one, "WTI spot price at Cushing, weekly mean: 93.57 USD/bbl in the week of 2026-09-21 to 2026-09-27, down 9.97 from 103.54 the week before.")
        self.assertEqual(two, "Of the 104 week-to-week moves before it, 7 were as large.")
        self.assertLessEqual(len(one + " " + two), 240)

    def test_an_ordinary_month_of_battery_additions_is_not_notable(self):
        # the first version's z over the whole history called this the week's biggest change (9.32)
        ps = watch.periods(rows("storage_buildout_monthly"), SPEC["watch_storage_buildout"], NOW)
        self.assertEqual(ps[-1], ["2026-08", 54488.9])
        h = headline(ps, "US operating battery storage", "MW")
        ch = run.change(h, "previous")
        self.assertEqual((len(ch["earlier"]), ch["score"]), (36, 27.8))
        whole = [ps[i][1] - ps[i - 1][1] for i in range(1, len(ps))]
        self.assertEqual(run.notability(whole[-1], whole[:-1])[0], 9.32)    # what the rank replaced
        self.assertEqual(run.finding(h, ch, "previous"), (
            "US operating battery storage: 54,488.9 MW in August 2026, up 743.4 from 53,745.5 in July 2026.",
            "Of the 36 month-to-month moves before it, 26 were as large."))

    def test_a_monthly_figure_with_a_season_is_set_beside_the_same_month_a_year_earlier(self):
        ps = watch.periods(rows("state_generation_mix_monthly"), SPEC["watch_us_solar_share"], NOW)
        self.assertEqual(ps[-1], ["2026-07", 9.13])
        h = headline(ps, SPEC["watch_us_solar_share"]["label"], "percent")
        ch = run.change(h, "year")
        self.assertEqual(ch["prev_period"], "2025-07")
        self.assertEqual(dict(ps)["2025-07"], ch["prev_value"])
        self.assertTrue(run.finding(h, ch, "year")[0].endswith("a year earlier."))
        self.assertEqual(len(ps) - 12 - 1, 42)                               # one change for each month that has a year before it
        self.assertEqual(len(ch["earlier"]), 36)                             # ranked among the last 36 of them

    def test_no_period_to_compare_with_is_no_change(self):
        self.assertIsNone(run.change({"label": "x", "value": 1.0, "unit": "u", "period": "2026-07", "history": []}, "previous"))
        self.assertIsNone(run.change({"label": "x", "value": 1.0, "unit": "u", "period": "2026-07", "history": [["2026-06", 2.0]]}, "year"))

    def test_the_finding_says_largest_unchanged_and_one(self):
        h = {"label": "a measure", "value": 10.0, "unit": "MW", "period": "2026-08", "history": [["2026-05", 1.0], ["2026-06", 2.0], ["2026-07", 3.0]]}
        ch = run.change(h, "previous")
        self.assertEqual(run.finding(h, ch, "previous")[1], "It is the largest month-to-month move of the last 3.")
        h2 = dict(h, value=3.0)
        self.assertIn("unchanged from 3 in July 2026", run.finding(h2, run.change(h2, "previous"), "previous")[0])
        h3 = dict(h, value=4.0)
        self.assertEqual(run.finding(h3, run.change(h3, "previous"), "previous")[1], "Of the 2 month-to-month moves before it, 2 were as large.")

    def test_no_statistic_is_named_to_the_reader(self):
        h = headline(watch.periods(rows("eia_fuel_spot_prices"), SPEC["watch_wti"], NOW), "WTI", "USD/bbl")
        text = " ".join(run.finding(h, run.change(h, "previous"), "previous")).lower()
        for word in ("robust", " z ", "deviation", "percentile", "score"):
            self.assertNotIn(word, text)
        self.assertIn("Name no statistic", run.NOTE_SYSTEM)


class FakeTemplate:
    """A measure made for the test, with the attributes the engine asks of a template."""
    PUBLIC, PARAMS, TABLES = True, {}, []
    METHOD = "made for a test"

    def __init__(self, name, about, compare, series):
        self.NAME, self.TITLE, self.ABOUT, self.COMPARE, self.series = name, name, about, compare, series

    def compute(self, **_):
        from common import result
        ps = self.series
        return result(self.NAME, {}, self.TITLE, "sub", pd.DataFrame({"period": [p for p, _ in ps], "value": [v for _, v in ps]}), [],
                      {"kind": "line", "x": [p for p, _ in ps], "series": [{"name": self.NAME, "values": [v for _, v in ps]}]},
                      {"label": self.NAME, "value": ps[-1][1], "unit": "u", "period": ps[-1][0], "history": ps[:-1]}, [f"{self.NAME}: a fact."])

    def render(self, res, size, path=None):
        if path:
            with open(path, "wb") as f:
                f.write(b"png")
        return {"series": []}


def weeks(values, last="2026-09-28"):
    start = pd.Timestamp(last) - pd.Timedelta(weeks=len(values) - 1)
    return [[f"{(start + pd.Timedelta(weeks=i)).date()} to {(start + pd.Timedelta(weeks=i, days=6)).date()}", float(v)] for i, v in enumerate(values)]


def months(values, last="2026-08"):
    idx = pd.period_range(end=last, periods=len(values), freq="M")
    return [[str(p), float(v)] for p, v in zip(idx, values)]


class ThePick(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.saved = (run.DOCS, run.HISTORY, run.INTERNAL, templates.load_all, list(templates.ORDER), run.ip.LOG_DIR, run.ip.STATUS_DIR,
                      run.table_registry)
        run.DOCS, run.HISTORY, run.INTERNAL = self.tmp, os.path.join(self.tmp, "history.csv"), os.path.join(self.tmp, "_i")
        run.ip.LOG_DIR = run.ip.STATUS_DIR = os.path.join(self.tmp, "_logs")
        run.table_registry = lambda mods: {"public_tables": 0, "read": 0, "not_read": {}, "tables": []}

    def tearDown(self):
        (run.DOCS, run.HISTORY, run.INTERNAL, templates.load_all, order, run.ip.LOG_DIR, run.ip.STATUS_DIR, run.table_registry) = self.saved
        templates.ORDER[:] = order
        shutil.rmtree(self.tmp, ignore_errors=True)

    def pick(self, mods, week):
        templates.load_all = lambda: mods
        templates.ORDER[:] = [m.NAME for m in mods]
        self.assertEqual(run.main(["--no-model", "--no-gallery", "--week", week]), 0)
        return json.load(open(os.path.join(self.tmp, week, "chart_of_the_week.json"), encoding="utf-8"))

    def test_a_count_of_what_the_erw_collected_is_never_the_chart_of_the_week(self):
        # 4 October 2026: deals in the news, 11 to 59 in a month, the largest move by far, and not a change in the system
        calm = [50, 51, 50, 52, 51, 50, 51, 52, 50, 51, 53]
        mods = [FakeTemplate("deals", "coverage", "previous", months([3, 4, 3, 5, 4, 3, 4, 5, 3, 11, 59], "2026-09")),
                FakeTemplate("a_price", "system", "previous", weeks(calm))]
        c = self.pick(mods, "2026-W40")
        self.assertEqual(c["template"], "a_price")
        self.assertEqual(c["picked_by"], "the rule")
        self.assertEqual(c["caption"], c["finding"])                          # the caption is the finding, written by code
        self.assertTrue(c["caption"].startswith("A_price: 53 u in the week of 2026-09-28 to 2026-10-04, up 2 from 51 the week before."))
        self.assertIn("counts of what the ERW itself has collected never compete", c["rule"])
        self.assertEqual([a["template"] for a in c["also_moved"]], [])        # the count is not among the runners-up either

    def test_the_larger_move_against_its_own_past_wins_not_the_larger_number(self):
        quiet = FakeTemplate("quiet", "system", "previous", weeks([100, 100.1, 100, 100.1, 100, 100.1, 100, 100.1, 100, 100.1, 103]))
        loud = FakeTemplate("loud", "system", "previous", weeks([100, 150, 90, 160, 80, 170, 70, 180, 60, 190, 150]))
        c = self.pick([loud, quiet], "2026-W40")
        self.assertEqual(c["template"], "quiet")                              # up 2.9: larger than every earlier move of its own
        self.assertEqual(c["change"]["score"], 100.0)
        self.assertIn("It is the largest week-to-week move of the last 10.", c["finding"])
        self.assertEqual(c["also_moved"][0]["template"], "loud")

    def test_a_month_already_shown_is_not_this_weeks_news(self):
        monthly = FakeTemplate("monthly", "system", "previous", months([1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 9]))
        weekly = FakeTemplate("weekly", "system", "previous", weeks([5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5.5]))
        self.assertEqual(self.pick([monthly, weekly], "2026-W40")["template"], "monthly")
        weekly2 = FakeTemplate("weekly", "system", "previous", weeks([5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5.5, 6], "2026-10-05"))
        c = self.pick([monthly, weekly2], "2026-W41")                         # the same August figure a week later
        self.assertEqual(c["template"], "weekly")
        self.assertTrue(run.seen_before("monthly", {}, "2026-08", "2026-W41"))
        h = pd.read_csv(os.path.join(self.tmp, "history.csv"), dtype=str, keep_default_na=False)
        self.assertEqual(list(h[(h["week"] == "2026-W41") & (h["template"] == "monthly")]["new"]), ["False"])

    def test_with_nothing_new_it_says_so(self):
        monthly = FakeTemplate("monthly", "system", "previous", months([1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 9]))
        self.pick([monthly], "2026-W40")
        c = self.pick([monthly], "2026-W41")
        self.assertEqual(c["template"], "monthly")
        self.assertTrue(c["picked_by"].startswith("no measure's newest period was new this week"))

    def test_too_little_past_falls_back_to_the_level_rule_and_says_so(self):
        short = FakeTemplate("short", "system", "previous", weeks([1, 2, 3, 4, 5, 6, 7, 8, 30]))    # 8 earlier values, 7 earlier changes
        c = self.pick([short], "2026-W40")
        self.assertTrue(c["picked_by"].startswith("no measure had 8 earlier changes"))


class TheWatchList(unittest.TestCase):
    def test_a_week_short_of_its_rows_is_not_a_week(self):
        d = rows("eia_fuel_spot_prices")
        full = watch.periods(d, SPEC["watch_wti"], NOW)
        week = d[(d["ts_utc"] >= "2026-09-21") & (d["ts_utc"] < "2026-09-28")]
        self.assertEqual(len(week), 5)                                        # five business days, as EIA published them
        cut = d.drop(week.index[:2])                                          # three left: under the four a week needs
        short = watch.periods(cut, SPEC["watch_wti"], NOW)
        self.assertEqual(len(short), len(full) - 1)
        self.assertNotIn("2026-09-21 to 2026-09-27", [p for p, _ in short])   # left out, never estimated from three days

    def test_the_week_and_the_month_under_way_are_not_shown(self):
        ps = watch.periods(rows("eia_fuel_spot_prices"), SPEC["watch_wti"], pd.Timestamp("2026-09-24T00:00:00Z"))
        self.assertEqual(ps[-1][0], "2026-09-14 to 2026-09-20")
        ps = watch.periods(rows("storage_buildout_monthly"), SPEC["watch_storage_buildout"], pd.Timestamp("2026-08-15T00:00:00Z"))
        self.assertEqual(ps[-1][0], "2026-07")

    def test_a_month_counts_only_when_every_day_of_it_is_held(self):
        # ERCOT's disclosure begins on 6 December 2025 and the table held 5 days of August 2026
        ps = watch.periods(rows("ercot_storage_dam_awards_monthly"), SPEC["watch_dam_awards"], NOW)
        self.assertEqual([p for p, _ in ps], ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07"])
        self.assertEqual(ps[0][1], 2356.92)

    def test_a_variable_eia_writes_only_some_months_counts_as_zero_when_it_is_named_optional(self):
        d = rows("state_generation_mix_monthly")
        self.assertEqual(len(watch.periods(d, SPEC["watch_us_solar_share"], NOW)), 55)
        strict = dict(SPEC["watch_us_solar_share"])
        strict.pop("optional")
        self.assertEqual(watch.periods(d, strict, NOW), [])                   # without it no month of this sample is whole

    def test_a_line_is_a_template_to_the_engine(self):
        t = watch.WatchTemplate(SPEC["watch_wti"])
        res = t.result(watch.periods(rows("eia_fuel_spot_prices"), SPEC["watch_wti"], NOW))
        self.assertEqual(res["headline"]["value"], 93.57)
        self.assertEqual(res["chart"]["kind"], "line")
        self.assertEqual(len(res["chart"]["x"]), 104)
        self.assertEqual((t.ABOUT, t.COMPARE, t.PUBLIC, t.TABLES), ("system", "previous", True, ["eia_fuel_spot_prices"]))
        self.assertIn("Nothing is filled", t.METHOD)

    def test_every_line_reads_a_public_table_and_the_four_the_prompt_named_are_there(self):
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
        lic = dict(zip(cov["table"], cov["license"]))
        for s in watch.WATCH:
            self.assertEqual(lic.get(s["table"]), "public", s["name"])
            self.assertIn(s["compare"], ("previous", "year"))
            self.assertIn(s["by"], ("week", "month"))
        tables = {s["table"] for s in watch.WATCH}
        for t in ("storage_buildout_monthly", "shoulder_hours_monthly", "ercot_storage_dam_awards_monthly", "iso_curtailment_monthly", "spp_curtailment_daily"):
            self.assertIn(t, tables)
        self.assertEqual(len({s["name"] for s in watch.WATCH}), len(watch.WATCH))
        self.assertTrue(re.fullmatch(r"\^\(([a-z0-9_]+\|)+[a-z0-9_]+\)\$", watch.tables()))

    def test_no_line_reads_a_table_behind_a_held_fix(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import impossible_hours
        for s in watch.WATCH:
            if s["table"] in impossible_hours.HELD:
                # the cost of power table is held for New York, SPP and California; Texas's rows do not move (session 118)
                self.assertEqual((s["table"], s["entity"]), ("cost_of_power_monthly", "ercot:HB_HUBAVG"), s["name"])

    def test_the_registry_accounts_for_every_public_table(self):
        mods = templates.load_all()
        reg = run.table_registry(mods)
        self.assertEqual(reg["read"] + sum(reg["not_read"].values()), reg["public_tables"])
        self.assertGreaterEqual(reg["read"], 38)
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str, keep_default_na=False)
        self.assertEqual(reg["public_tables"], int((cov["license"] == "public").sum()))
        by = {r["table"]: r for r in reg["tables"]}
        self.assertEqual(by["carbon_intensity_monthly"]["read_by"], [])
        self.assertTrue(by["carbon_intensity_monthly"]["why_not"].startswith("behind a fix held for approval"))
        self.assertIn("watch_storage_buildout", by["storage_buildout_monthly"]["read_by"])
        named = [t for ts in watch.NOT_WATCHED.values() for t in ts]
        self.assertEqual(len(named), len(set(named)))
        for t in named:
            self.assertEqual(by[t]["read_by"], [], f"{t} is named as not watched and a line reads it")

    def test_what_each_template_is_about(self):
        mods = {m.NAME: m for m in templates.load_all()}
        self.assertEqual(mods["deals_by_month"].ABOUT, "coverage")
        self.assertEqual(mods["datacenters_by_state"].ABOUT, "coverage")
        self.assertEqual(mods["negative_price_hours"].COMPARE, "year")
        self.assertEqual(getattr(mods["curtailment_midday"], "ABOUT", "system"), "system")
        self.assertGreaterEqual(sum(1 for n in mods if n.startswith("watch_")), 25)

    def test_the_two_templates_that_read_demand_use_the_rule_for_impossible_hours(self):
        self.assertIn("screened_demand(d[d[\"variable\"] == \"demand_mw\"])", src("warehouse", "analysis", "templates", "storage_evening_peak.py"))
        self.assertIn("screened_demand(d[d[\"variable\"] == \"demand_mw\"])", src("warehouse", "analysis", "templates", "forecast_error.py"))
        from common import screened_demand
        ts = pd.date_range("2026-02-09T18:00:00Z", periods=12, freq="h")
        d = pd.DataFrame({"ts_utc": ts, "value": [20000, 20500, 21000, 21500, 22000, 0, 0, 22500, 22000, 21500, 21000, 20500.0]})
        kept = screened_demand(d)
        self.assertEqual(len(kept), 10)                                       # New York's zeros are not hours of demand
        self.assertTrue((kept["value"] > 0).all())


class Standing(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (("warehouse", "analysis", "watch.py"), ("warehouse", "analysis", "run.py"), ("warehouse", "news", "commit_paths.sh"),
                      ("warehouse", "news", "email_digest.py"), (".github", "workflows", "roundup.yml"), ("docs", "methods", "automated_analysis.md"),
                      ("docs", "email_domain.md"), ("tests", "test_session119.py")):
            text = src(*parts)
            if parts[-1] == "run.py":
                text = text.replace("EM = chr(0x2014)", "")
            self.assertNotIn(chr(0x2014), text, parts[-1])

    def test_miso_is_still_paused(self):
        self.assertIn("miso", src("warehouse", "metadata", "paused_sources.csv").lower())


if __name__ == "__main__":
    unittest.main()
