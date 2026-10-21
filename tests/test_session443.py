"""Session 443: the company database's seed (master plan tool 10), docs/reviews/companies-seed.csv and its note.

One row a company named in the warehouse's deals, datacenter and project tables and in the Thesis Builder's list; no
field invented. These tests read the two files as they stand: no dash, a name and a table on every row, every table
cited one the warehouse has, a source beside every filled field, no name twice."""

import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SEED = os.path.join(ROOT, "docs", "reviews", "companies-seed.csv")
NOTE = os.path.join(ROOT, "docs", "reviews", "companies-seed.md")
DASHES = ("\u2014", "\u2013")


def seed_rows():
    with open(SEED, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def known_tables():
    names = set()
    with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            names.add(r["table"])
    out = os.path.join(ROOT, "warehouse", "output")
    if os.path.isdir(out):
        names |= {n[:-4] for n in os.listdir(out) if n.endswith(".csv")}
    return names


def cited(cell):
    """The table names of a "tables" or "policy_mentions" cell: "energy_deals (17); datacenter_projects (4)"."""
    return re.findall(r"([a-z0-9_]+) \(\d+\)", cell)


class Files(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for path in (SEED, NOTE):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for d in DASHES:
                self.assertNotIn(d, text, f"{os.path.basename(path)} holds {d!r}")

    def test_the_columns(self):
        rows = seed_rows()
        self.assertGreater(len(rows), 0)
        for c in ("name", "description", "description_source", "segment", "segment_source", "stage", "stage_source",
                  "tables", "roles", "row_ids", "policy_mentions", "energy_companies_id"):
            self.assertIn(c, rows[0])


class Rows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = seed_rows()
        cls.tables = known_tables()

    def test_every_row_has_a_name_and_a_table(self):
        for r in self.rows:
            self.assertTrue(r["name"].strip(), r)
            self.assertTrue(cited(r["tables"]), f"{r['name']}: no ERW table")
            self.assertTrue(r["row_ids"].strip(), f"{r['name']}: no row")

    def test_every_table_cited_exists(self):
        seen = set()
        for r in self.rows:
            seen |= set(cited(r["tables"])) | set(cited(r["policy_mentions"]))
            seen |= {x.split(".")[0] for x in r["roles"].split(";") if x}
        self.assertTrue(seen)
        self.assertEqual(sorted(seen - self.tables), [])

    def test_a_filled_field_has_its_source(self):
        for r in self.rows:
            for field in ("description", "segment", "stage"):
                if r[field].strip():
                    self.assertTrue(r[field + "_source"].strip(), f"{r['name']}: {field} without a source")

    def test_no_name_twice(self):
        names = [r["name"] for r in self.rows]
        self.assertEqual(len(names), len(set(names)))
        keys = [r["name_key"] for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_filled_fields_come_only_from_energy_companies(self):
        for r in self.rows:
            for field in ("description", "segment", "stage"):
                if r[field].strip():
                    self.assertTrue(r[field + "_source"].startswith("energy_companies erwco:"), r["name"])

    def test_not_disclosed_is_not_a_stage(self):
        for r in self.rows:
            self.assertNotIn(r["stage"].strip().lower(), ("not disclosed", "not confirmed"))


if __name__ == "__main__":
    unittest.main()
