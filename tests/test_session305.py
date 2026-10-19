"""Session 305: Redivis out of every schedule's read path.

Energy Research Warehouse (ERW). Redivis refused every export from 15 October 2026 (100 GB in 30 days), and the daily
run stopped at its restore. These tests hold the new order (warehouse/restore_tables.py) against a bucket held in a
dict (no network, no keys): the rows are test fixtures, not data values.

  1. The archive's replay in slices gives what restore.py's replay gives: the latest line of each key, upserts only.
  2. A table comes from the cache only when its data SHA-256 is the archive's latest; otherwise from the archive, and
     only with the row count the latest run recorded; Redivis, left out, is never asked.
  3. The export ceiling: the day's ledger is summed from its objects' names, and an export that would pass it is refused.
  4. A Redivis read refused for the cap is a skip in the uploader (erw_headers) and in a table's stores, not a failure.
  5. The daily run, the Roundup and the data machine's commit step are wired as the session says.

    python -m unittest tests.test_session305 -v
"""

import datetime as dt
import gzip
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
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import restore_tables as rt  # noqa: E402
import restore as R  # noqa: E402
import table_stores  # noqa: E402

COLS = ["entity", "variable", "ts_utc", "value", "retrieved_at"]


class Bucket:
    """The bucket's ls, get and put over a dict of paths to bytes."""
    enabled = True

    def __init__(self):
        self.objects = {}

    def put(self, path, data, overwrite=False):
        if path in self.objects and not overwrite:
            raise RuntimeError("exists")
        self.objects[path] = data

    def get(self, path):
        return self.objects.get(path)

    def ls(self, prefix):
        prefix = prefix.rstrip("/")
        depth = len(prefix.split("/")) if prefix else 0
        names = {}
        for p in self.objects:
            parts = p.split("/")
            if prefix and not p.startswith(prefix + "/"):
                continue
            if len(parts) == depth + 1:
                names[parts[depth]] = {"name": parts[depth], "id": "file"}
            elif len(parts) > depth + 1:
                names.setdefault(parts[depth], {"name": parts[depth], "id": None})
        return [names[k] for k in sorted(names)]


def gz_csv(df):
    return gzip.compress(df.to_csv(index=False, lineterminator="\n").encode("utf-8"))


def table_text(df, header=("a header line",)):
    return "".join(f"# {h}\n" for h in header) + df.to_csv(index=False, lineterminator="\n")


def data_sha(df):
    return hashlib.sha256(df.to_csv(index=False, lineterminator="\n").encode("utf-8")).hexdigest()


def key(entity, ts):
    return hashlib.sha256(f"{entity}|{ts}".encode()).hexdigest()[:16]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.bucket = Bucket()
        R._BUCKET_RUNS.clear()
        # run 1: three rows; run 2: one row changed, one added
        r1 = pd.DataFrame([["x", "load", f"2026-10-0{i}T00:00:00Z", str(i), "t1"] for i in (1, 2, 3)], columns=COLS)
        r2 = pd.DataFrame([["x", "load", "2026-10-02T00:00:00Z", "20", "t2"], ["x", "load", "2026-10-04T00:00:00Z", "4", "t2"]],
                          columns=COLS)
        for rid, at, part in (("R1", "2026-10-10T00:00:00Z", r1), ("R2", "2026-10-11T00:00:00Z", r2)):
            lines = part.copy()
            lines.insert(0, "_key_sha", [key(e, t) for e, t in zip(part["entity"], part["ts_utc"])])
            lines.insert(0, "_op", "upsert")
            lines.insert(0, "_archived_at", at)
            lines.insert(0, "_run_id", rid)
            lines["_extra"] = ""
            self.bucket.put(f"tbl/2026-10/{rid}.csv.gz", gz_csv(lines))
        self.final = pd.DataFrame([["x", "load", "2026-10-01T00:00:00Z", "1", "t1"], ["x", "load", "2026-10-02T00:00:00Z", "20", "t2"],
                                   ["x", "load", "2026-10-03T00:00:00Z", "3", "t1"], ["x", "load", "2026-10-04T00:00:00Z", "4", "t2"]],
                                  columns=COLS)
        runs = pd.DataFrame([dict(run_id="R1", archived_at="2026-10-10T00:00:00Z", runner="local", table="tbl", month="2026-10",
                                  added=3, deleted=0, table_rows=3, data_sha256="old", columns=json.dumps(COLS), header="h1"),
                             dict(run_id="R2", archived_at="2026-10-11T00:00:00Z", runner="github", table="tbl", month="2026-10",
                                  added=2, deleted=0, table_rows=4, data_sha256=data_sha(self.final), columns=json.dumps(COLS),
                                  header="h2")])
        self.bucket.put("_runs/2026-10/R2.csv.gz", gz_csv(runs))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        R._BUCKET_RUNS.clear()

    def sources(self, **kw):
        return rt.Sources(bucket=self.bucket, log=lambda m: None, **kw)


class TheReplay(Fixture):
    def test_the_sliced_replay_keeps_the_latest_line_of_each_key(self):
        s = self.sources(redivis=False)
        out = os.path.join(self.tmp, "tbl.csv")
        n = s.replay_sliced("tbl", s.latest("tbl"), out)
        self.assertEqual(n, 4)
        got = pd.read_csv(out, comment="#", dtype=str).sort_values("ts_utc").reset_index(drop=True)
        pd.testing.assert_frame_equal(got, self.final)
        self.assertIn("as of run R2", open(out, encoding="utf-8").readline())


class TheOrder(Fixture):
    def test_a_current_cached_copy_is_taken_as_it_is(self):
        cache = os.path.join(self.tmp, "cache")
        os.makedirs(cache)
        with open(os.path.join(cache, "tbl.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(table_text(self.final))
        out = os.path.join(self.tmp, "tbl.csv")
        n, source, _ = self.sources(cache=cache, redivis=False).restore("tbl", out)
        self.assertEqual((n, source), (4, "GitHub's cache"))
        self.assertEqual(open(out, encoding="utf-8").read(), table_text(self.final))

    def test_a_stale_cached_copy_is_passed_over_for_the_archive(self):
        cache = os.path.join(self.tmp, "cache")
        os.makedirs(cache)
        with open(os.path.join(cache, "tbl.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(table_text(self.final.iloc[:3]))
        n, source, _ = self.sources(cache=cache, redivis=False).restore("tbl", os.path.join(self.tmp, "tbl.csv"))
        self.assertEqual((n, source), (4, "the archive"))

    def test_a_rebuild_with_another_row_count_is_refused_and_redivis_left_out_is_not_asked(self):
        rl = R._BUCKET_RUNS  # the run log says five rows; the archive rebuilds four
        bad = self.bucket.objects["_runs/2026-10/R2.csv.gz"]
        runs = pd.read_csv(gzip.open(__import__("io").BytesIO(bad)), dtype=str)
        runs.loc[runs["run_id"] == "R2", "table_rows"] = "5"
        self.bucket.objects["_runs/2026-10/R2.csv.gz"] = gz_csv(runs)
        rl.clear()
        out = os.path.join(self.tmp, "tbl.csv")
        n, source, why = self.sources(redivis=False).restore("tbl", out)
        self.assertIsNone(source)
        self.assertIn("rebuilt 4 rows, the latest run (R2) recorded 5", why)
        self.assertIn("Redivis is left out", why)
        self.assertFalse(os.path.exists(out), "nothing half-written is left")

    def test_a_moving_window_table_may_rebuild_with_more_rows(self):
        bad = self.bucket.objects["_runs/2026-10/R2.csv.gz"]
        runs = pd.read_csv(gzip.open(__import__("io").BytesIO(bad)), dtype=str)
        runs.loc[runs["run_id"] == "R2", "table_rows"] = "3"
        self.bucket.objects["_runs/2026-10/R2.csv.gz"] = gz_csv(runs)
        R._BUCKET_RUNS.clear()
        with mock.patch.dict(rt.CONFIG, {"judge_by_newest": ["^tbl$"]}):
            n, source, _ = self.sources(redivis=False).restore("tbl", os.path.join(self.tmp, "tbl.csv"))
        self.assertEqual((n, source), (4, "the archive"))
        R._BUCKET_RUNS.clear()
        n, source, why = self.sources(redivis=False).restore("tbl", os.path.join(self.tmp, "tbl2.csv"))
        self.assertIsNone(source, "any other table with more rows than recorded is refused")

    def test_a_bucket_copy_with_the_latest_sha_is_taken(self):
        self.bucket.put(f"_copies/tbl/{data_sha(self.final)}.csv.gz", gzip.compress(table_text(self.final).encode("utf-8")))
        n, source, _ = self.sources(redivis=False).restore("tbl", os.path.join(self.tmp, "tbl.csv"))
        self.assertEqual((n, source), (4, "a copy in the archive bucket"))


class TheCeiling(Fixture):
    def test_the_days_ledger_is_summed_and_an_export_over_the_ceiling_is_not_asked(self):
        s = self.sources()
        day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        s.record_export("a", 1_500_000_000)
        self.assertEqual(s.exported_today(), (day, 1_500_000_000))
        up = mock.MagicMock()
        up.licenses.return_value = {}
        up.table_meta.return_value = {"numRows": 10, "numBytes": 900_000_000}
        with mock.patch.dict(sys.modules, {"upload": up}), mock.patch.object(rt, "ceiling_bytes", return_value=2_000_000_000):
            with self.assertRaisesRegex(RuntimeError, "not asked of Redivis"):
                s.from_redivis("tbl", os.path.join(self.tmp, "tbl.csv"))
        up.restore.assert_not_called()

    def test_the_ceiling_is_set_in_the_config(self):
        self.assertEqual(rt.ceiling_bytes(), 2_000_000_000)


class TheCapIsASkip(unittest.TestCase):
    def test_a_capped_header_read_is_a_skip_of_erw_headers(self):
        import upload as up
        exc = RuntimeError("[400 invalid_request] Cannot export more than 100GB within a 30 day period")
        self.assertTrue(up.capped(exc))
        results = []
        drafts = mock.MagicMock()
        with mock.patch.object(up, "table_meta", return_value={"numRows": 3}), \
                mock.patch.object(up, "read_frame", side_effect=exc), mock.patch.object(up, "log"):
            up.merge_headers(drafts, ["t"], {"t": "public"}, "now", results)
        self.assertEqual(results, [(up.HEADERS_TABLE, None, None, up.CAP_SKIP)])

    def test_a_capped_upload_is_a_skip_of_the_stores(self):
        table_stores.CAP_SKIPPED.clear()
        rcs = {"validate": 0, "coverage": 0, "archive": 0, "redivis": table_stores.SKIP}

        def run(cmd, **kw):
            step = next(s for s, _, c in table_stores.commands("t") if os.path.join(ROOT, c[0]) == cmd[1])
            return mock.Mock(returncode=rcs[step])
        with tempfile.TemporaryDirectory() as d:
            ok = table_stores.stores("t", run=run, log=lambda m: None, runs=d)
        self.assertTrue(ok)
        self.assertEqual(table_stores.CAP_SKIPPED, {"t"})
        table_stores.CAP_SKIPPED.clear()


class TheWiring(unittest.TestCase):
    def read(self, *p):
        return open(os.path.join(ROOT, *p), encoding="utf-8").read()

    def test_the_daily_run_restores_through_restore_tables_with_the_cache(self):
        sh = self.read("warehouse", "run_daily.sh")
        self.assertIn('warehouse/restore_tables.py --rolling ${RESTORE_CACHE:+--cache "$RESTORE_CACHE"}', sh)
        self.assertNotIn('"$PYTHON" warehouse/redivis/upload.py --restore', sh)
        y = self.read(".github", "workflows", "daily-prices.yml")
        self.assertIn("actions/cache/restore@v4", y)
        self.assertIn("actions/cache/save@v4", y)
        self.assertIn('restore_tables.py --rolling --stash "${{ runner.temp }}/erw-rolling"', y)
        self.assertLess(y.index("actions/cache/restore@v4"), y.index("- name: Pull, validate, rebuild coverage"))

    def test_the_roundup_restores_the_same_way(self):
        y = self.read(".github", "workflows", "roundup.yml")
        self.assertIn("restore_tables.py --rolling --cache", y)
        self.assertNotIn("upload.py --restore", y.split("run: |")[-1])

    def test_the_data_machine_sets_aside_tracked_changes_before_its_pull(self):
        sh = self.read("warehouse", "run_data_machine.sh")
        self.assertLess(sh.index('git stash push --quiet -m "dm_commit $day'), sh.index("git pull --rebase --quiet origin main"))

    def test_the_bucket_pull_leaves_out_the_restores_own_folders(self):
        self.assertIn('if name in ("_state", "_copies", "_exports")', self.read("warehouse", "archive", "archive.py"))


if __name__ == "__main__":
    unittest.main()
