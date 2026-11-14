"""Session 3937 (chain 267): the large-load research pass as three events tables.

Held here on the committed research files (docs/research/large_load/): only public rows are written; a public row's
internal fields are left empty with their cites; a registry pointer is never a value; a month-only date is kept as
printed and the row dated by the day read; a row that breaks a rule stops the whole write. No network, no model.
"""
import os
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_research as llr  # noqa: E402


class TheCommittedFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = {k: llr.read(k) for k in llr.FILES}
        cls.built = {k: llr.BUILD[k](cls.raw[k]) for k in llr.FILES}

    def test_no_problem_in_the_files(self):
        for k, d in self.raw.items():
            self.assertEqual(llr.check(k, d), [], k)

    def test_only_public_rows_are_written(self):
        for k, (rows, held) in self.built.items():
            self.assertEqual(len(rows) + len(held), len(self.raw[k]), k)
            self.assertEqual(len(rows), int((self.raw[k]["license"] == "public").sum()), k)

    def test_internal_fields_are_left_out_of_a_public_row(self):
        rows, _ = self.built["rules"]
        raw = self.raw["rules"].set_index("row_id")
        hit = rows[rows["x_withheld"] != ""]
        self.assertGreater(len(hit), 0)
        for _, r in hit.iterrows():
            for f in r["x_withheld"].split(";"):
                self.assertEqual(r["x_" + f], "")
                self.assertEqual(r["x_" + f + "_cite"], "")
                self.assertNotEqual(raw.loc[r["x_row_id"], f], "")

    def test_a_registry_pointer_is_not_a_value(self):
        rows, _ = self.built["rules"]
        for f in llr.RULE_FIELDS:
            self.assertFalse(rows["x_" + f].str.startswith("held:").any(), f)
        self.assertTrue((rows["x_held"] != "").any())

    def test_every_event_has_a_day(self):
        for k, (rows, _) in self.built.items():
            self.assertTrue(rows["event_date"].str.match(r"^\d{4}-\d{2}-\d{2}$").all(), k)
        ch, _ = self.built["changes"]
        month = ch[ch["x_date"].str.match(r"^\d{4}-\d{2}$")]
        self.assertGreater(len(month), 0)
        self.assertTrue((month["x_date_kind"] == "date read").all())
        self.assertTrue((month["event_date"] == month["x_date_read"]).all())


class TheRefusal(unittest.TestCase):
    def test_a_bad_license_stops_the_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            for k, f in llr.FILES.items():
                shutil.copy(os.path.join(llr.RESEARCH, f), os.path.join(tmp, f))
            p = os.path.join(tmp, llr.FILES["laws"])
            text = open(p, encoding="utf-8").read().replace(",public,", ",maybe,", 1)
            open(p, "w", encoding="utf-8").write(text)
            out = os.path.join(tmp, "out")
            self.assertEqual(llr.main(["--folder", tmp, "--out-dir", out]), 1)
            self.assertFalse(os.path.exists(os.path.join(out, "state_large_load_laws.csv")))


if __name__ == "__main__":
    unittest.main()
