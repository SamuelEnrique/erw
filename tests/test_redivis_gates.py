"""Session 28: the uploader's gates against silent history loss (Ben Domingue's review, item 2).

Energy Research Warehouse (ERW). Tests warehouse/redivis/upload.py against a mocked Redivis
client (no network, no token): a dict of tables stands in for the draft. The rows are
three-line test fixtures, not data values.

  1. --restore fails when a table the manifest lists (and restore_before_run matches) is
     absent from the draft, or holds fewer rows than the manifest recorded.
  2. An upload refuses to shrink a rolling-window table below its recorded row count,
     unless --allow-shrink names it; other tables may shrink.
  3. Existence is read from the table's metadata, not list_tables(): a table that
     list_tables() leaves out is still found and restored, and an error other than a 404
     fails the restore rather than reading as "absent".
  4. (review item 3) Uploads are routed by license: an internal table goes to the internal
     dataset, push() refuses it for the public one, and --check-license fails when one is
     in the public dataset or the internal dataset is not private; --fix moves it.

    python -m unittest discover -s tests -v
"""

import io
import os
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

import pandas as pd
import redivis

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))

import upload  # noqa: E402

ROLLING = "iso_dam_hub_prices"        # matched by restore_before_run (session 29: the consolidated table)
MIGRATED = "ercot_dam_hub_prices"     # session 29: consolidated into iso_dam_hub_prices, never restored
ROLLING_2 = "weather_obs_hourly"      # matched too
FULL = "eia_fuel_spot_prices"         # a full-history table: not matched
INT = "pjm_rpm_capacity_prices"       # licensed internal
COLS = ["entity", "variable", "ts_utc", "value"]


def frame(n):
    return pd.DataFrame([[f"E{i}", "v", f"2026-09-{i + 1:02d}T00:00:00Z", str(i)] for i in range(n)], columns=COLS)


class FakeUpload:
    def __init__(self, table):
        self.table = table

    def create(self, fh, **kw):
        self.table.ds.rows[self.table.name] = pd.read_csv(fh, dtype=str, keep_default_na=False)


class FakeTable:
    def __init__(self, ds, name):
        self.ds, self.name, self.properties = ds, name, {}

    def exists(self):
        return self.name in self.ds.rows

    def get(self):
        if self.name in self.ds.broken:  # the SDK's error that hides a 5xx (the IRW's finding)
            raise AttributeError("'NoneType' object has no attribute 'get'")
        if self.name not in self.ds.rows:
            raise redivis.exceptions.NotFoundError("Not found", 404, f"table {self.name} not found")
        self.properties = {"name": self.name, "numRows": len(self.ds.rows[self.name])}
        return self

    def delete(self):
        self.ds.rows.pop(self.name, None)

    def create(self, description=None):
        self.ds.rows[self.name] = pd.DataFrame(columns=COLS)
        return self

    def upload(self, fname):
        return FakeUpload(self)

    def to_pandas_dataframe(self, **kw):
        return self.ds.rows[self.name].copy()


class FakeDataset:
    def __init__(self, rows, unlisted=(), broken=()):
        self.rows, self.unlisted, self.broken = dict(rows), set(unlisted), set(broken)

    def table(self, name):
        return FakeTable(self, name)

    def list_tables(self):
        return [FakeTable(self, n) for n in self.rows if n not in self.unlisted]


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out = os.path.join(self.tmp, "output")
        os.makedirs(self.out)
        self.manifest = os.path.join(self.tmp, "redivis_uploads.csv")
        self.patches = [
            mock.patch.object(upload, "OUT", self.out),
            mock.patch.object(upload, "TMP", os.path.join(self.tmp, "redivis")),
            mock.patch.object(upload, "MANIFEST", self.manifest),
            mock.patch.object(upload, "count_rows", lambda t: len(t.ds.rows[t.name])),
            mock.patch.object(upload, "licenses",
                              lambda: {ROLLING: "public", ROLLING_2: "public", FULL: "public", INT: "internal"}),
            mock.patch.dict(sys.modules, {"erw_validate": types.SimpleNamespace(validate=lambda p: {"errors": []})}),
        ]
        for p in self.patches:
            p.start()
        self.log = io.StringIO()
        self.patches.append(mock.patch.object(upload, "log", lambda m: self.log.write(m + "\n")))
        self.patches[-1].start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def manifest_rows(self, **rows):
        upload.write_manifest(pd.DataFrame(
            [(t, "x", str(n), "2026-09-28T00:00:00Z", t, upload.PUBLIC, "") for t, n in rows.items()],  # session 29: migrated_to
            columns=upload.MANIFEST_COLS))

    def local(self, name, n):
        with open(os.path.join(self.out, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# test fixture\n")
            frame(n).to_csv(f, index=False, lineterminator="\n")

    def use(self, ds):
        p = mock.patch.object(upload, "open_draft", lambda *a, **k: ds)
        p.start()
        self.patches.append(p)

    def use_two(self, pub, internal, level="none"):
        dss = {upload.PUBLIC: pub, upload.INTERNAL: internal}
        meta = types.SimpleNamespace(exists=lambda: True, get=lambda: types.SimpleNamespace(
            properties={"publicAccessLevel": level}))
        for p in (mock.patch.object(upload, "open_draft", lambda name=None, create=False: dss[name or upload.PUBLIC]),
                  mock.patch.object(upload, "account", lambda: types.SimpleNamespace(dataset=lambda n: meta))):
            p.start()
            self.patches.append(p)

    # 1. restore: a listed table absent from the draft fails the run
    def test_restore_fails_when_a_listed_table_is_absent(self):
        self.manifest_rows(**{ROLLING: 5, ROLLING_2: 4})
        self.use(FakeDataset({ROLLING_2: frame(4)}))  # ROLLING was deleted and never recreated
        self.assertEqual(upload.restore(), 1)
        self.assertIn(f"FAIL restore {ROLLING}: RuntimeError: absent from the draft", self.log.getvalue())
        self.assertTrue(os.path.exists(os.path.join(self.out, ROLLING_2 + ".csv")))  # the others still restored

    def test_a_migrated_table_is_never_restored_nor_required(self):
        """Session 29: an old table consolidated into another (table_migrations.csv) is neither expected in the draft
        nor restored, even while it is still there; its rows come back inside the consolidated table."""
        self.manifest_rows(**{ROLLING: 5, MIGRATED: 5})
        ds = FakeDataset({ROLLING: frame(5), MIGRATED: frame(5)})
        self.use(ds)
        self.assertEqual(upload.restore(), 0)
        self.assertFalse(os.path.exists(os.path.join(self.out, MIGRATED + ".csv")))
        del ds.rows[MIGRATED]  # removed from the draft by --remove-migrated
        os.remove(os.path.join(self.out, ROLLING + ".csv"))
        self.assertEqual(upload.restore(), 0)

    def test_restore_fails_when_the_draft_is_shorter_than_recorded(self):
        self.manifest_rows(**{ROLLING: 5})
        self.use(FakeDataset({ROLLING: frame(3)}))
        self.assertEqual(upload.restore(), 1)
        self.assertIn("the draft holds 3 rows, fewer than the 5 last uploaded", self.log.getvalue())

    def test_restore_passes_when_every_listed_table_is_there(self):
        self.manifest_rows(**{ROLLING: 5, FULL: 9})  # FULL is not rolling, so not expected in the draft
        self.use(FakeDataset({ROLLING: frame(5)}))
        self.assertEqual(upload.restore(), 0)
        back = pd.read_csv(os.path.join(self.out, ROLLING + ".csv"), comment="#", dtype=str)
        self.assertEqual(len(back), 5)

    def test_restore_checks_a_table_that_exists_locally(self):
        self.manifest_rows(**{ROLLING: 5})
        self.local(ROLLING, 5)
        self.use(FakeDataset({}))
        self.assertEqual(upload.restore(), 1)

    # 2. the shrink gate
    def test_upload_refuses_to_shrink_a_rolling_table(self):
        self.manifest_rows(**{ROLLING: 5})
        ds = FakeDataset({ROLLING: frame(5)})
        self.use(ds)
        self.local(ROLLING, 3)
        self.assertEqual(upload.run_upload([ROLLING], include_metadata=False), 1)
        self.assertEqual(len(ds.rows[ROLLING]), 5)  # the draft table was not deleted
        self.assertIn("refused: 3 rows would shrink the rolling-window table below the 5 rows", self.log.getvalue())
        self.assertEqual(pd.read_csv(self.manifest, dtype=str).set_index("table").loc[ROLLING, "rows"], "5")

    def test_allow_shrink_names_the_table(self):
        self.manifest_rows(**{ROLLING: 5})
        ds = FakeDataset({ROLLING: frame(5)})
        self.use(ds)
        self.local(ROLLING, 3)
        self.assertEqual(upload.run_upload([ROLLING], include_metadata=False, allow_shrink=[ROLLING]), 0)
        self.assertEqual(len(ds.rows[ROLLING]), 3)
        self.assertEqual(pd.read_csv(self.manifest, dtype=str).set_index("table").loc[ROLLING, "rows"], "3")

    def test_a_full_history_table_may_shrink(self):
        self.manifest_rows(**{FULL: 5})
        ds = FakeDataset({FULL: frame(5)})
        self.use(ds)
        self.local(FULL, 3)
        self.assertEqual(upload.run_upload([FULL], include_metadata=False), 0)

    def test_growing_is_never_refused(self):
        self.manifest_rows(**{ROLLING: 5})
        ds = FakeDataset({ROLLING: frame(5)})
        self.use(ds)
        self.local(ROLLING, 7)
        self.assertEqual(upload.run_upload([ROLLING], include_metadata=False), 0)
        self.assertEqual(len(ds.rows[ROLLING]), 7)

    # 3. existence from metadata, not list_tables()
    def test_a_table_list_tables_leaves_out_is_still_restored(self):
        self.manifest_rows(**{ROLLING: 5})
        self.use(FakeDataset({ROLLING: frame(5)}, unlisted={ROLLING}))
        self.assertEqual(upload.restore(), 0)
        self.assertTrue(os.path.exists(os.path.join(self.out, ROLLING + ".csv")))

    def test_an_error_other_than_404_is_not_read_as_absent(self):
        self.manifest_rows(**{ROLLING: 5})
        ds = FakeDataset({ROLLING: frame(5)}, broken={ROLLING})
        self.use(ds)
        with self.assertRaises(AttributeError):
            upload.table_meta(ds, ROLLING)
        self.assertEqual(upload.restore(), 1)
        self.assertIn(f"FAIL restore {ROLLING}: AttributeError", self.log.getvalue())
        self.assertIsNone(upload.table_meta(ds, "no_such_table"))

    # 4. routing by license
    def test_an_internal_table_goes_to_the_internal_dataset(self):
        pub, idd = FakeDataset({}), FakeDataset({})
        self.use_two(pub, idd)
        self.local(INT, 3)
        self.local(FULL, 2)
        self.assertEqual(upload.run_upload([INT, FULL], include_metadata=False), 0)
        self.assertIn(INT, idd.rows)
        self.assertNotIn(INT, pub.rows)
        self.assertIn(FULL, pub.rows)
        m = pd.read_csv(self.manifest, dtype=str).set_index("table")
        self.assertEqual((m.loc[INT, "dataset"], m.loc[FULL, "dataset"]), (upload.INTERNAL, upload.PUBLIC))

    def test_push_refuses_an_internal_license_for_the_public_dataset(self):
        with self.assertRaises(RuntimeError):
            upload.push(FakeDataset({}), INT, [], frame(2).to_csv(index=False), "internal", dataset=upload.PUBLIC)
        with self.assertRaises(RuntimeError):
            upload.push(FakeDataset({}), INT, [], frame(2).to_csv(index=False), "", dataset=upload.PUBLIC)

    def test_check_license_fails_on_an_internal_table_in_public(self):
        self.use_two(FakeDataset({FULL: frame(2), INT: frame(3)}, unlisted={INT}), FakeDataset({}))
        self.assertEqual(upload.check_license(), 1)
        self.assertIn(f"FAIL {INT}: license 'internal'", self.log.getvalue())

    def test_check_license_fails_on_an_unknown_table_in_public(self):
        self.use_two(FakeDataset({FULL: frame(2), "stray_table": frame(1)}), FakeDataset({}))
        self.assertEqual(upload.check_license(), 1)

    def test_check_license_fails_if_the_internal_dataset_is_not_private(self):
        self.use_two(FakeDataset({FULL: frame(2)}), FakeDataset({}), level="overview")
        self.assertEqual(upload.check_license(), 1)

    def test_check_license_passes_when_clean(self):
        self.use_two(FakeDataset({FULL: frame(2), "erw_coverage": frame(1)}), FakeDataset({INT: frame(3)}))
        self.assertEqual(upload.check_license(), 0)

    def test_a_scheduled_upload_never_creates_the_internal_dataset(self):
        created = []
        missing = types.SimpleNamespace(exists=lambda: False, create=lambda **k: created.append(k))
        with mock.patch.object(upload, "account", lambda: types.SimpleNamespace(dataset=lambda *a, **k: missing)):
            with self.assertRaises(RuntimeError):
                upload.open_draft(upload.INTERNAL)
        self.assertEqual(created, [])

    def test_fix_moves_an_internal_table_and_then_passes(self):
        pub, idd = FakeDataset({FULL: frame(2), INT: frame(3)}), FakeDataset({})
        self.use_two(pub, idd)
        self.local(INT, 3)
        self.assertEqual(upload.check_license(fix=True), 0)
        self.assertNotIn(INT, pub.rows)
        self.assertEqual(len(idd.rows[INT]), 3)

    def test_a_table_whose_route_changed_is_uploaded_again(self):
        self.local(INT, 3)
        _, data = upload.split_header(os.path.join(self.out, INT + ".csv"))
        upload.write_manifest(pd.DataFrame([(INT, upload.sha(data), "3", "t", INT, upload.PUBLIC, "")],
                                           columns=upload.MANIFEST_COLS))
        self.assertEqual(upload.changed_tables(), [INT])


if __name__ == "__main__":
    unittest.main()
