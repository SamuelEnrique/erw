"""Session 131: the freeze hold for the scheduled jobs (built, not switched on), and the loader's rewrite of whole
tables that made the daily run long and recorded two tables as failed on 5 October 2026.

Energy Research Warehouse (ERW). No request leaves the machine. The freeze hold is tested on real git repositories made
in a temporary directory (a bare "origin" and its clones), on the workflows' own text, and on the daily script's own
lines run in bash. The loader is tested on 360 real rows of ercot_as_prices as the connector wrote them on 5 October
2026 (tests/fixtures/session131/, ERCOT NP4-181-ER, public), against a stand-in for Supabase that keeps rows in memory.

    python -m unittest tests.test_session131 -v
"""

import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("scripts", "warehouse/supabase", "warehouse/connectors"):
    sys.path.insert(0, os.path.join(ROOT, p))

import freeze  # noqa: E402
import held  # noqa: E402
import load  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session131")
DAY = dt.date(2026, 10, 6)


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------ the switch and the answer

class Switch(unittest.TestCase):
    def root(self, switch=None, freeze_file=None):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        if switch is not None:
            os.makedirs(os.path.join(d, "warehouse", "config"))
            with open(os.path.join(d, freeze.HOLD_SWITCH), "w", encoding="utf-8") as f:
                f.write(switch)
        if freeze_file is not None:
            with open(os.path.join(d, "REVIEW_FREEZE"), "w", encoding="utf-8") as f:
                f.write(freeze_file)
        return d

    def test_only_a_plain_true_switches_it_on(self):
        for text, want in ((None, False), ("", False), ("enabled: false\n", False), ("# enabled: true\nenabled: false\n", False),
                           ("enabled: true\n", True), ("# a note\nenabled: true   # switched on by a person\n", True),
                           ("enabled: yes\n", False), ("enabled: true\nenabled: false\n", False), ("enabled true\n", False)):
            self.assertEqual(freeze.hold_enabled(self.root(text)), want, repr(text))

    def test_hold_needs_both_a_freeze_and_the_switch(self):
        frozen, before, after = "start: 2026-10-05\nend: 2026-10-07\n", "start: 2026-10-08\nend: 2026-10-09\n", "start: 2026-10-01\nend: 2026-10-05\n"
        on, off = "enabled: true\n", "enabled: false\n"
        for switch, file, want in ((off, frozen, False), (off, None, False), (None, frozen, False),
                                   (on, None, False), (on, before, False), (on, after, False),
                                   (on, frozen, True), (on, "start: soon\n", True)):       # a file that cannot be read is a freeze
            got, line = freeze.hold(self.root(switch, file), DAY)
            self.assertEqual(got, want, (switch, file, line))
            self.assertTrue(line.startswith("hold: " if want else "run: "), line)

    def test_the_last_day_is_held_and_the_day_after_is_not(self):
        r = self.root("enabled: true\n", "start: 2026-10-05\nend: 2026-10-07\n")
        self.assertTrue(freeze.hold(r, dt.date(2026, 10, 7))[0])
        self.assertFalse(freeze.hold(r, dt.date(2026, 10, 8))[0])

    def test_the_command_always_exits_0_and_tells_the_workflow(self):
        today = dt.datetime.now(dt.timezone.utc).date()
        span = f"start: {today - dt.timedelta(days=1)}\nend: {today + dt.timedelta(days=1)}\n"
        for switch, want in (("enabled: true\n", "1"), ("enabled: false\n", "0")):
            r = self.root(switch, span)
            out, env = os.path.join(r, "out.txt"), os.path.join(r, "env.txt")
            p = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "freeze.py"), "hold", "--root", r, "--github-output", "--github-env"],
                               capture_output=True, text=True, env=dict(os.environ, GITHUB_OUTPUT=out, GITHUB_ENV=env))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual((open(out).read(), open(env).read()), (f"hold={want}\n", f"ERW_FREEZE_HOLD={want}\n"))
        s = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "freeze.py"), "status", "--root", r], capture_output=True, text=True)
        self.assertEqual(s.returncode, 1)                                                   # status is as it was: frozen is exit 1

    def test_it_is_not_switched_on(self):
        """Session 131 was told to build the hold without switching it on. When a person switches it on, this is the
        test to change, with the date and who approved."""
        self.assertFalse(freeze.hold_enabled(), "warehouse/config/freeze_hold.yaml says enabled: true")
        self.assertFalse(freeze.hold()[0])


# ------------------------------------------------------------------ the held files, on real repositories

@unittest.skipUnless(shutil.which("git"), "git is not on this machine")
class HeldFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.origin = os.path.join(self.tmp, "origin.git")
        self.git("init", "--quiet", "--bare", "--initial-branch=main", self.origin, cwd=self.tmp)
        seed = self.clone("seed")
        self.write(seed, "STATUS.md", "main, day 0\n")
        self.write(seed, "docs/digest/2026-10-04.md", "digest of 4 October\n")
        self.write(seed, "site/app/page.tsx", "the page, as merged\n")
        self.git("add", "-A", cwd=seed)
        self.git("commit", "--quiet", "-m", "main as it stands", cwd=seed)
        self.git("push", "--quiet", "origin", "HEAD:main", cwd=seed)

    def git(self, *a, cwd):
        r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"git {' '.join(a)}: {r.stderr}")
        return r.stdout.strip()

    def clone(self, name):
        d = os.path.join(self.tmp, name)
        if not os.path.exists(os.path.join(self.origin, "refs", "heads", "main")) and not self.git("ls-remote", self.origin, cwd=self.tmp):
            os.makedirs(d)
            self.git("init", "--quiet", "--initial-branch=main", cwd=d)
            self.git("remote", "add", "origin", self.origin, cwd=d)
        else:
            self.git("clone", "--quiet", "-c", "core.autocrlf=false", self.origin, d, cwd=self.tmp)   # the files as committed, on any machine
        self.git("config", "user.name", "a test", cwd=d)
        self.git("config", "user.email", "test@example.org", cwd=d)
        self.git("config", "core.autocrlf", "false", cwd=d)
        return d

    def write(self, d, path, text):
        os.makedirs(os.path.dirname(os.path.join(d, path)) or d, exist_ok=True)
        with open(os.path.join(d, path), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def text(self, d, path):
        with open(os.path.join(d, path), encoding="utf-8") as f:
            return f.read()

    def test_nothing_held_is_the_usual_day(self):
        w = self.clone("run")
        self.assertEqual(held.restore(w), [])
        self.assertEqual(self.text(w, "runs/held_files.txt"), "")
        self.assertIsNone(held.tip(w))
        self.assertFalse(held.clear(w))

    def test_a_held_run_commits_to_the_branch_and_never_to_main(self):
        w = self.clone("run1")
        main_before = self.git("rev-parse", "origin/main", cwd=w)
        self.write(w, "STATUS.md", "held, day 1\n")
        self.write(w, "docs/digest/2026-10-05.md", "digest of 5 October\n")
        new = held.commit(["STATUS.md", "docs/digest", "not/there.csv"], "Daily prices 2026-10-05, held", w)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "held/scheduled", cwd=w).split()[0], new)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "main", cwd=w).split()[0], main_before)     # main did not move
        self.assertEqual(self.git("rev-parse", "HEAD", cwd=w), main_before)                                    # nor did the checkout
        self.assertEqual(self.git("diff", "--cached", "--name-only", cwd=w), "")                              # and nothing is staged in it
        self.assertEqual(held.manifest(new, w), ["STATUS.md", "docs/digest/2026-10-05.md"])
        self.assertEqual(self.git("show", f"{new}:site/app/page.tsx", cwd=w), "the page, as merged")           # the rest of the tree is main's
        self.assertIsNone(held.commit(["STATUS.md", "docs/digest"], "again", w))                              # nothing new: no commit

    def test_the_next_run_starts_from_what_was_held_and_the_run_after_the_freeze_brings_it_to_main(self):
        w1 = self.clone("run1")
        self.write(w1, "STATUS.md", "held, day 1\n")
        self.write(w1, "docs/digest/2026-10-05.md", "digest of 5 October\n")
        held.commit(["STATUS.md", "docs/digest"], "day 1, held", w1)
        # a person lands a change on main during the freeze (an approved deploy): it must survive
        s = self.clone("session")
        self.write(s, "site/app/page.tsx", "the page, changed by a person during the freeze\n")
        self.git("commit", "--quiet", "-am", "a person's change", cwd=s)
        self.git("push", "--quiet", "origin", "HEAD:main", cwd=s)
        # day 2, still frozen: a fresh checkout of main
        w2 = self.clone("run2")
        self.assertEqual(held.restore(w2), ["STATUS.md", "docs/digest/2026-10-05.md"])
        self.assertEqual(self.text(w2, "STATUS.md"), "held, day 1\n")
        self.assertEqual(self.text(w2, "docs/digest/2026-10-05.md"), "digest of 5 October\n")
        self.assertEqual(self.text(w2, "site/app/page.tsx"), "the page, changed by a person during the freeze\n")
        self.assertEqual(self.git("diff", "--cached", "--name-only", cwd=w2), "")                              # unstaged, as a run's own changes are
        self.write(w2, "STATUS.md", "held, day 2\n")
        self.write(w2, "queue/summary/2026-10-05-health.md", "health of 5 October\n")
        held.commit(["STATUS.md", "docs/digest"], "day 2, held", w2)
        held.commit(["queue/summary/2026-10-05-health.md"], "health summary, held", w2)
        # day 3, the freeze has ended: restore, the run's own work, commit to main as the workflow does, clear
        w3 = self.clone("run3")
        files = held.restore(w3)
        self.assertEqual(files, ["STATUS.md", "docs/digest/2026-10-05.md", "queue/summary/2026-10-05-health.md"])
        self.write(w3, "STATUS.md", "main, day 3\n")
        self.write(w3, "docs/digest/2026-10-08.md", "digest of 8 October\n")
        for p in ["STATUS.md", "docs/digest"] + self.text(w3, "runs/held_files.txt").split():
            self.git("add", "--", p, cwd=w3)
        self.git("commit", "--quiet", "-m", "Daily prices 2026-10-08", cwd=w3)
        self.git("push", "--quiet", "origin", "HEAD:main", cwd=w3)
        self.assertTrue(held.clear(w3))
        final = self.clone("after")
        self.assertEqual(self.text(final, "STATUS.md"), "main, day 3\n")
        for p, want in (("docs/digest/2026-10-05.md", "digest of 5 October\n"), ("docs/digest/2026-10-08.md", "digest of 8 October\n"),
                        ("queue/summary/2026-10-05-health.md", "health of 5 October\n"),
                        ("site/app/page.tsx", "the page, changed by a person during the freeze\n")):
            self.assertEqual(self.text(final, p), want, p)
        self.assertFalse(os.path.exists(os.path.join(final, ".held")))                                         # the branch's own list never reaches main
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "held/scheduled", cwd=final), "")
        self.assertEqual(held.restore(final), [])


# ------------------------------------------------------------------ the workflows and the daily script, as written

class Workflows(unittest.TestCase):
    def steps(self, name):
        wf = yaml.safe_load(read(".github", "workflows", name))
        return [s for j in wf["jobs"].values() for s in j["steps"]]

    def test_every_scheduled_push_to_main_is_behind_the_hold(self):
        found = 0
        for name in sorted(os.listdir(os.path.join(ROOT, ".github", "workflows"))):
            for s in self.steps(name):
                run = s.get("run") or ""
                if "git push" in run and "HEAD:main" in run:
                    found += 1
                    guard = run.find('if [ "${ERW_FREEZE_HOLD:-0}" = "1" ]; then')
                    self.assertGreaterEqual(guard, 0, f"{name}, step {s.get('name')}: a push to main with no hold")
                    block = run[guard:run.find("\nfi", guard)]
                    self.assertIn("scripts/held.py commit", block, name)
                    self.assertIn("exit 0", block, name)
                    self.assertLess(guard, run.find("git push"), name)                     # the hold is decided before the push
                    self.assertLess(guard, run.find("git pull") if "git pull" in run else len(run), name)
        self.assertEqual(found, 4)       # the daily run's files, its health summary, the Roundup, the vacuum's sizes

    def test_the_hold_is_decided_before_anything_is_pulled_or_pushed(self):
        for name in ("daily-prices.yml", "roundup.yml", "weekly-vacuum.yml"):
            steps = self.steps(name)
            names = [s.get("name") or s.get("uses") for s in steps]
            self.assertIn("Freeze hold, run or hold", names, name)
            i = names.index("Freeze hold, run or hold")
            self.assertEqual(steps[i]["run"], "python scripts/freeze.py hold --github-output --github-env")
            self.assertEqual(names[i + 1], "Freeze hold, the files held so far")
            first_work = min(k for k, s in enumerate(steps) if re.search(r"run_daily\.sh|lock\.py|git push|load\.py", s.get("run") or ""))
            self.assertLess(i, first_work, name)

    def test_no_scheduled_load_into_the_live_set_escapes_the_hold(self):
        for name in sorted(os.listdir(os.path.join(ROOT, ".github", "workflows"))):
            for s in self.steps(name):
                run = s.get("run") or ""
                for m in re.finditer(r"warehouse/supabase/load\.py", run):
                    before = run[:m.start()]
                    self.assertIn('if [ "${ERW_FREEZE_HOLD:-0}" = "1" ]; then', before, f"{name}: a load with no hold")
        daily = read("warehouse", "run_daily.sh")
        self.assertEqual(len(re.findall(r"warehouse/supabase/load\.py", daily.split('echo "== Supabase live set')[1])), 2)
        self.assertEqual(daily.count("supabase/load.py") - 2, sum(1 for ln in daily.splitlines() if ln.startswith("#") and "supabase/load.py" in ln))

    def test_the_feeds_a_visitor_expects_are_not_touched(self):
        for name in ("latest-prices.yml", "hourly-network.yml", "chain-watch.yml"):
            text = read(".github", "workflows", name)
            self.assertNotRegex(text, r"ERW_FREEZE_HOLD|freeze\.py|held\.py", name)
            self.assertNotIn("HEAD:main", text, name)
        r = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", ".github/workflows/latest-prices.yml", ".github/workflows/hourly-network.yml",
                            "warehouse/connectors/latest_prices.py", "warehouse/derived/network_hourly.py"], cwd=ROOT, capture_output=True)
        if r.returncode not in (0, 1):
            raise unittest.SkipTest("origin/main is not in this checkout")
        self.assertEqual(r.returncode, 0, "a kept-live job differs from main")

    @unittest.skipUnless(shutil.which("bash"), "bash is not on this machine")
    def test_the_daily_script_holds_the_load_and_nothing_else(self):
        daily = read("warehouse", "run_daily.sh")
        block = daily[daily.index('echo "== Supabase live set'):daily.index('echo "== Energy Digest')]
        with tempfile.TemporaryDirectory() as d:
            script = os.path.join(d, "block.sh")
            with open(script, "w", encoding="utf-8", newline="\n") as f:
                f.write('status="$1"\nPYTHON=python\nrun_other() { echo "RAN $*"; }\n' + block)
            for env, ran, said in (({"ERW_FREEZE_HOLD": "1"}, [], "supabase_load skipped: held by the review freeze"),
                                   ({"ERW_FREEZE_HOLD": "1", "DRY_STORES": "1"}, [], "supabase_load skipped: held by the review freeze"),
                                   ({"ERW_FREEZE_HOLD": "0"}, ["RAN supabase_load python warehouse/supabase/load.py"], ""),
                                   ({}, ["RAN supabase_load python warehouse/supabase/load.py"], ""),
                                   ({"DRY_STORES": "1"}, ["RAN supabase_load python warehouse/supabase/load.py --dry-run"], "")):
                status = os.path.join(d, "status.txt")
                open(status, "w").close()
                e = {k: v for k, v in os.environ.items() if k not in ("ERW_FREEZE_HOLD", "DRY_STORES")}
                r = subprocess.run(["bash", script.replace("\\", "/"), status.replace("\\", "/")], capture_output=True, text=True, env=dict(e, **env))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual([ln for ln in r.stdout.splitlines() if ln.startswith("RAN")], ran, env)
                self.assertEqual(open(status).read().startswith(said) if said else open(status).read() == "", True, env)
        # everything else of the day still runs under a hold: the hold appears once in the script
        self.assertEqual(daily.count('"${ERW_FREEZE_HOLD:-0}" = "1"'), 1)


# ------------------------------------------------------------------ the loader: a row fetched again is not a changed row

class Store:
    """A stand-in for Supabase's REST client, holding rows in memory: what load.sync_table and load.count_rows ask of it."""

    def __init__(self, fail_counts=0):
        self.rows, self.upserted, self.fail_counts, self.count_calls = {}, 0, fail_counts, 0

    def table(self, shape):
        return Query(self, shape)


class Query:
    def __init__(self, store, shape):
        self.s, self.shape, self.f, self.op, self.rng, self.order_by, self.head = store, shape, [], "select", None, [], False

    def select(self, fields, count=None, head=False):
        self.fields, self.head = fields.split(","), head
        return self

    def eq(self, c, v):
        self.f.append(lambda r: str(r.get(c) if r.get(c) is not None else "") == str(v))
        return self

    def lt(self, c, v):
        self.f.append(lambda r: r[c] < v)
        return self

    def in_(self, c, vs):
        self.f.append(lambda r: r.get(c) in vs)
        return self

    def order(self, c, desc=False):
        self.order_by.append(c)
        return self

    def range(self, a, b):
        self.rng = (a, b)
        return self

    def limit(self, n):
        self.rng = (0, n - 1)
        return self

    def upsert(self, rows, on_conflict):
        self.op, self.payload, self.key = "upsert", rows, on_conflict.split(",")
        return self

    def delete(self):
        self.op = "delete"
        return self

    def execute(self):
        s = self.s
        got = sorted((r for r in s.rows.values() if all(f(r) for f in self.f)), key=lambda r: tuple(str(r.get(c) or "") for c in self.order_by))
        if self.op == "upsert":
            for r in self.payload:
                s.rows[tuple(str(r.get(c) or "") for c in self.key)] = dict(r)
            s.upserted += len(self.payload)
            return type("R", (), {"data": self.payload})()
        if self.op == "delete":
            for k in [k for k, r in s.rows.items() if all(f(r) for f in self.f)]:
                del s.rows[k]
            return type("R", (), {"data": []})()
        if self.head:
            s.count_calls += 1
            if s.count_calls <= s.fail_counts:
                raise RuntimeError("{'message': 'JSON could not be generated', 'code': 500}")
            return type("R", (), {"count": len(got), "data": []})()
        if self.rng:
            got = got[self.rng[0]:self.rng[1] + 1]
        return type("R", (), {"data": [dict(r) for r in got]})()


class LoaderStamps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = os.path.join(FIX, "ercot_as_prices_3_days.csv")
        cls.df = pd.read_csv(p, comment="#", dtype=str, keep_default_na=False)
        cls.now = pd.Timestamp("2026-10-06T14:30:00Z")

    def test_the_sample_is_three_whole_days_of_five_services(self):
        self.assertEqual((len(self.df), self.df["entity"].nunique(), self.df["retrieved_at"].nunique()), (360, 5, 1))
        self.assertEqual(list(self.df.columns), load.SERIES_COLS)

    def sync(self, store, df, stamp):
        return load.sync_table(store, "ercot_as_prices", df, "series", "public", stamp, None, self.now)

    def test_a_table_rebuilt_from_the_same_documents_fetched_again_writes_only_its_new_day(self):
        store = Store()
        two_days = self.df[self.df["ts_utc"] < "2026-10-03T05:00:00Z"].assign(retrieved_at="2026-10-04T14:20:00Z")
        self.assertEqual(self.sync(store, two_days, "2026-10-04T14:50:00Z"), (240, 0))      # the first load writes every row
        # the next day the connector builds the whole table again: every row carries the new retrieval stamp
        self.assertEqual(self.sync(store, self.df, "2026-10-05T15:23:51Z"), (120, 0))       # before session 131: (360, 0)
        self.assertEqual(len(store.rows), 360)
        kept = [r for r in store.rows.values() if r["ts_utc"] < "2026-10-03T05:00:00Z"]
        self.assertEqual({r["retrieved_at"] for r in kept}, {"2026-10-04T14:20:00Z"})       # the stamp of the load that last changed the row
        self.assertEqual({r["loaded_at"] for r in kept}, {"2026-10-04T14:50:00Z"})
        self.assertEqual(self.sync(store, self.df.assign(retrieved_at="2026-10-06T14:20:00Z"), "2026-10-06T14:50:00Z"), (0, 0))

    def test_a_revised_price_and_a_new_document_are_still_written(self):
        store = Store()
        self.sync(store, self.df, "2026-10-05T15:00:00Z")
        revised = self.df.assign(retrieved_at="2026-10-06T14:20:00Z").copy()
        revised.loc[revised.index[7], "value"] = str(float(revised["value"].iloc[7]) + 0.01)
        self.assertEqual(self.sync(store, revised, "2026-10-06T14:50:00Z"), (1, 0))
        republished = revised.copy()
        day = republished["ts_utc"] >= "2026-10-03T05:00:00Z"
        republished.loc[day, "vintage"] = "2026-10-11T13:00:05Z"                            # ERCOT republishes the year's file: a new vintage
        self.assertEqual(self.sync(store, republished, "2026-10-07T14:50:00Z"), (120, 0))
        gone = republished[republished["ts_utc"] >= "2026-10-02T05:00:00Z"]
        self.assertEqual(self.sync(store, gone, "2026-10-08T14:50:00Z"), (0, 120))          # rows the selection no longer has still leave

    def test_the_hash_of_a_table_does_not_move_with_the_stamp(self):
        again = self.df.assign(retrieved_at="2026-10-06T14:20:00Z")
        self.assertEqual(load.rows_sha256(self.df, "public"), load.rows_sha256(again, "public"))
        self.assertNotEqual(load.rows_sha256(self.df, "public"), load.rows_sha256(self.df, "internal"))
        changed = self.df.copy()
        changed.loc[changed.index[0], "value"] = "999"
        self.assertNotEqual(load.rows_sha256(self.df, "public"), load.rows_sha256(changed, "public"))
        self.assertNotEqual(load.rows_sha256(self.df, "public"), load.rows_sha256(self.df.iloc[:-1], "public"))

    def test_the_stamp_is_the_only_column_left_out(self):
        r = load.records("ercot_as_prices", self.df.iloc[:1], "series", "public", "2026-10-05T15:00:00Z")[0]
        k, body = load.canon(r, "series")
        for c in load.SERIES_COLS:
            other = dict(r, **{c: "2020-01-01T00:00:00Z" if c in load.TIMESTAMP else ("1.5" if c in load.NUMERIC else "another")})
            k2, body2 = load.canon(other, "series")
            self.assertEqual((k, body) == (k2, body2), c == "retrieved_at", c)
        e = {"table_name": "t", "event_id": "e1", "event_date": "2026-10-01T00:00:00Z", "license": "internal", "extra": {"title": "A", "retrieved_at": "x"}}
        self.assertEqual(load.canon(e, "events"), load.canon(dict(e, extra={"title": "A", "retrieved_at": "y"}), "events"))
        self.assertNotEqual(load.canon(e, "events"), load.canon(dict(e, extra={"title": "B", "retrieved_at": "x"}), "events"))

    def test_a_count_that_fails_is_asked_again_before_a_table_is_called_failed(self):
        store, waits = Store(fail_counts=2), []
        self.sync(store, self.df, "2026-10-05T15:00:00Z")
        self.assertEqual(load.count_rows(store, "series", "ercot_as_prices", sleep=waits.append), 360)
        self.assertEqual((waits, store.count_calls), ([10, 30], 3))
        store = Store(fail_counts=3)
        with self.assertRaisesRegex(RuntimeError, "JSON could not be generated"):
            load.count_rows(store, "series", "ercot_as_prices", sleep=waits.append)
        self.assertEqual(store.count_calls, 3)
        self.assertEqual(read("warehouse", "supabase", "load.py").count("n = count_rows(client, shape, name)"), 1)


class TheRepository(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for p in (("scripts", "held.py"), ("scripts", "freeze.py"), ("warehouse", "config", "freeze_hold.yaml"), ("docs", "freeze_hold.md"),
                  ("docs", "loader_stamps.md"), ("tests", "test_session131.py"), (".github", "workflows", "daily-prices.yml"),
                  (".github", "workflows", "roundup.yml"), (".github", "workflows", "weekly-vacuum.yml"), ("warehouse", "run_daily.sh")):
            t = read(*p)
            self.assertNotIn(chr(0x2014), t, p)


if __name__ == "__main__":
    unittest.main()
