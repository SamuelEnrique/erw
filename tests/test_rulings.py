"""Session 5 rulings: raw pruning keeps manifests, run status is appended and streaks found.

Energy Research Warehouse (ERW). These tests build only file layouts and
status records in temporary directories; no data values are involved.

    python -m unittest discover -s tests -v
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))

import prune_raw  # noqa: E402
import run_status  # noqa: E402
import iso_prices as ip  # noqa: E402

NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def touch(path, content=b"x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


class PruneRawTest(unittest.TestCase):
    def setUp(self):
        self.raw = tempfile.mkdtemp()
        self.old = os.path.join(self.raw, "ercot", "20260901T000000Z")
        self.new = os.path.join(self.raw, "ercot", "20260920T000000Z")
        self.odd = os.path.join(self.raw, "isone_test", "probe")
        for d in (self.old, self.new, self.odd):
            touch(os.path.join(d, "manifest.csv"))
            touch(os.path.join(d, "20260901T000000.000000Z_00001_file.csv"))

    def tearDown(self):
        shutil.rmtree(self.raw)

    def test_old_runs_lose_files_but_keep_manifests(self):
        r = prune_raw.prune(self.raw, days=14, now=NOW)
        self.assertEqual(r["runs"], ["ercot/20260901T000000Z"])
        self.assertEqual(os.listdir(self.old), ["manifest.csv"])
        self.assertEqual(len(os.listdir(self.new)), 2)
        self.assertEqual(len(os.listdir(self.odd)), 2)
        self.assertIn(os.path.join("isone_test", "probe"), r["skipped"])

    def test_dry_run_removes_nothing(self):
        r = prune_raw.prune(self.raw, days=14, now=NOW, dry_run=True)
        self.assertEqual(r["files"], 1)
        self.assertEqual(len(os.listdir(self.old)), 2)


class RunStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.csv = os.path.join(self.tmp, "run_status.csv")
        self.status = os.path.join(self.tmp, "status")
        os.makedirs(self.status)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def day(self, run_id, rtm_status, runner="github"):
        with open(os.path.join(self.status, "miso.json"), "w") as f:
            json.dump({"connector": "miso", "run_id": run_id, "runner": runner, "results": [
                {"table": "miso_dam_hub_prices", "market": "DAM", "status": "ok", "detail": ""},
                {"table": "miso_rtm_hub_prices", "market": "RTM", "status": rtm_status,
                 "detail": "SourceGap" if rtm_status == "failed" else ""}]}, f)
        return run_status.record(self.status, self.csv)

    def test_record_appends_once_per_run(self):
        self.assertEqual(self.day("20260923T140000Z", "failed"), 2)
        self.assertEqual(run_status.record(self.status, self.csv), 0)  # same run again: nothing
        self.assertEqual(len(run_status.load(self.csv)), 2)

    def test_three_failed_runs_in_a_row_is_a_streak(self):
        self.day("20260922T140000Z", "failed")
        self.day("20260923T140000Z", "failed")
        self.assertEqual(run_status.streaks(3, self.csv), [])
        self.day("20260924T140000Z", "failed")
        found = run_status.streaks(3, self.csv)
        self.assertEqual([f["table"] for f in found], ["miso_rtm_hub_prices"])
        self.day("20260925T140000Z", "ok")
        self.assertEqual(run_status.streaks(3, self.csv), [])

    def test_local_runs_do_not_count_for_the_github_rule(self):
        for d in ("22", "23", "24"):
            self.day(f"202609{d}T140000Z", "failed", runner="local")
        self.assertEqual(run_status.streaks(3, self.csv, runner="github"), [])
        self.assertEqual(len(run_status.streaks(3, self.csv)), 1)


class SecretsAndLicenseTest(unittest.TestCase):
    def test_keys_never_survive_redaction(self):
        ip.SECRETS.add("abcdefghijklmnopqrstuvwxyz0123456789ABCD")
        url = "https://api.eia.gov/v2/x/data/?api_key=abcdefghijklmnopqrstuvwxyz0123456789ABCD&a=1"
        self.assertNotIn("abcdefghij", ip.redact(url))
        self.assertIn("api_key=REDACTED", ip.redact(url))
        self.assertIn("REDACTED", ip.redact("error for abcdefghijklmnopqrstuvwxyz0123456789ABCD"))

    def test_license_rule(self):
        self.assertEqual(ip.license_of("pjm:da_hrl_lmps"), "internal")
        self.assertEqual(ip.license_of("ercot:NP4-190-CD"), "public")
        self.assertEqual(ip.license_of("eia:electricity/rto/region-data"), "public")


if __name__ == "__main__":
    unittest.main()
