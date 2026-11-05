"""Session 661: the uploader's Stanford target (chain 043).

Energy Research Warehouse (ERW). `upload.py --target stanford` writes the draft of Datapages's `erw:b9wm` with its own
manifest, and only a table whose ERW verdict in docs/licenses.md is public, whatever coverage.csv's flag says. The default
target, the daily run's, is unchanged. No network and no token: nothing here reaches Redivis.

    python -m unittest tests.test_session661 -v
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))

import upload  # noqa: E402


class StanfordTarget(unittest.TestCase):
    def setUp(self):
        self.saved = (upload.TARGET, upload.PUBLIC, upload.INTERNAL, upload.MANIFEST)

    def tearDown(self):
        upload.TARGET, upload.PUBLIC, upload.INTERNAL, upload.MANIFEST = self.saved

    def test_config_names_the_stanford_dataset_and_keeps_the_default(self):
        t = upload.CONFIG["targets"]["stanford"]
        self.assertEqual((t["owner"], t["owner_kind"], t["dataset"]), ("datapages", "organization", "erw:b9wm"))
        self.assertEqual(t["manifest"], "warehouse/metadata/redivis_uploads_stanford.csv")
        self.assertEqual((upload.CONFIG["dataset"], upload.CONFIG["owner_kind"]), ("energy_research_warehouse", "user"))

    def test_verdicts_read_from_the_license_record(self):
        v = upload.erw_verdicts()
        self.assertEqual(v["eia_fuel_spot_prices"], "public")
        self.assertEqual(v["pjm_rpm_capacity_prices"], "internal")
        self.assertEqual(v["ai_power_regions"], "unsettled")
        self.assertTrue(set(v.values()) <= {"public", "internal", "unsettled"})

    def test_use_target_switches_dataset_and_manifest(self):
        upload.use_target("stanford")
        self.assertEqual(upload.PUBLIC, "erw:b9wm")
        self.assertIsNone(upload.INTERNAL)
        self.assertTrue(upload.MANIFEST.replace(os.sep, "/").endswith("metadata/redivis_uploads_stanford.csv"))

    def test_gate_allows_public_verdicts_only_under_a_target(self):
        self.assertTrue(upload.allowed("ai_power_regions"))  # the default target routes by license, as before
        upload.use_target("stanford")
        self.assertTrue(upload.allowed("eia_fuel_spot_prices"))
        self.assertFalse(upload.allowed("ai_power_regions"))  # flagged public in coverage.csv, unsettled by its verdict
        self.assertFalse(upload.allowed("pjm_rpm_capacity_prices"))
        self.assertFalse(upload.allowed("no_such_table"))

    def test_an_unsettled_table_is_refused_before_anything_is_read_or_sent(self):
        upload.use_target("stanford")
        drafts = mock.MagicMock()
        with mock.patch.object(upload, "Drafts", return_value=drafts), \
                mock.patch.object(upload, "write_manifest"), \
                mock.patch.object(upload, "push", side_effect=AssertionError("never pushed")) as push, \
                mock.patch("erw_validate.validate", side_effect=AssertionError("not even validated")):
            self.assertEqual(upload.run_upload(["ai_power_regions", "pjm_rpm_capacity_prices"], include_metadata=False), 1)
        push.assert_not_called()
        drafts.assert_not_called()

    def test_proof_by_listing_waits_for_the_rows_and_removes_a_failed_upload(self):
        class T:
            def __init__(self, name, n):
                self.name, self.properties = name, {"numRows": n}

        class DS:
            def __init__(self):
                self.calls, self.deleted = 0, []

            def list_tables(self):
                self.calls += 1
                # first listing: "a" still loading; second: "a" whole, "b" never more than 0
                return [T("a", 0 if self.calls == 1 else 5), T("b", 0)]

            def table(self, name):
                ds = self
                up = mock.MagicMock()
                up.get.return_value.properties = {"status": "failed", "errorMessage": "bad row 3"}
                t = mock.MagicMock()
                t.upload.return_value = up
                t.delete.side_effect = lambda: ds.deleted.append(name)
                return t

        ds = DS()
        with mock.patch.object(upload.time, "sleep"):
            out = upload.prove_by_listing(ds, {"a": 5, "b": 7}, every=0, timeout=0.5)
        self.assertEqual(out["a"], (5, 5, ""))
        self.assertEqual(out["b"][:2], (7, 0))
        self.assertIn("upload failed: bad row 3", out["b"][2])
        self.assertEqual(ds.deleted, ["b"])

    def test_prove_by_listing_needs_a_target(self):
        with self.assertRaises(SystemExit):
            upload.run_upload([], include_metadata=False, listing=True)

    def test_target_refuses_the_default_targets_own_modes(self):
        for mode in ("--restore", "--check-license", "--remove-migrated"):
            with self.assertRaises(SystemExit):
                upload.main(["--target", "stanford", mode])


if __name__ == "__main__":
    unittest.main()
