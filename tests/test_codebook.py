"""The codebook stays true (chain 630, part C).

warehouse/metadata/variables/ holds one file a table (<table>.yaml, written by warehouse/codebook/build_variables.py
and by hand) and _shared.yaml, the column names many tables share, defined once. This test fails when:

- a public table of coverage.csv has no metadata file;
- a file lists a column its table lacks, or misses one it has, or holds them in another order (read from the table's
  header row the way the validator reads it: comment lines counted, then the first row; on a machine that holds the
  tables, warehouse/output or the folder ERW_CODEBOOK_TABLES names; a clean checkout holds none and skips this check);
- a column of a public table's file has no unit (a column defined in _shared.yaml takes its unit from there);
- a shared name is defined twice: a key repeated in _shared.yaml, or a table's file giving a shared column a label or
  a unit of its own;
- a file holds an em dash (CLAUDE.md rule 2).
"""
import csv
import os
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VARS = ROOT / "warehouse" / "metadata" / "variables"
TABLES = Path(os.environ.get("ERW_CODEBOOK_TABLES") or (ROOT / "warehouse" / "output"))
EM = chr(0x2014)


class _UniqueKeys(yaml.SafeLoader):
    """A loader that refuses a mapping key written twice (PyYAML keeps the last one silently)."""


def _no_duplicates(loader, node, deep=False):
    seen = set()
    for k, _ in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f"key {key!r} written twice", k.start_mark)
        seen.add(key)
    return loader.construct_mapping(node, deep)


_UniqueKeys.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def coverage():
    with open(ROOT / "warehouse" / "metadata" / "coverage.csv", encoding="utf-8", newline="") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


def header_row(path):
    """The validator's reading: the comment lines first, then the first row is the header."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            return next(csv.reader([line.rstrip("\r\n")]))
    return []


def load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeys) or {}


class CodebookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cov = coverage()
        cls.public = sorted(t for t, r in cls.cov.items() if r.get("license") == "public")
        cls.shared = load(VARS / "_shared.yaml")["columns"]
        cls.files = {p.stem: p for p in VARS.glob("*.yaml") if not p.stem.startswith("_")}

    def test_every_public_table_has_a_file(self):
        missing = [t for t in self.public if t not in self.files]
        self.assertEqual(missing, [], f"{len(missing)} public tables have no file in {VARS}: {missing[:20]}")

    def test_shared_names_defined_once_with_a_unit(self):
        # a repeated key in _shared.yaml raises in load() (setUpClass); each definition needs its unit and label
        for name, d in self.shared.items():
            self.assertTrue(str(d.get("unit") or "").strip(), f"_shared.yaml: {name} has no unit")
            self.assertTrue(str(d.get("label") or "").strip(), f"_shared.yaml: {name} has no label")

    def test_files_name_their_table_and_hold_one_entry_a_column(self):
        for t, p in self.files.items():
            d = load(p)
            self.assertEqual(d.get("table"), t, f"{p.name} names table {d.get('table')!r}")
            names = [c["name"] for c in d.get("columns") or []]
            self.assertTrue(names, f"{p.name} lists no column")
            self.assertEqual(len(names), len(set(names)), f"{p.name} lists a column twice")

    def test_no_shared_name_redefined_in_a_table(self):
        bad = []
        for t, p in self.files.items():
            for c in load(p).get("columns") or []:
                if c["name"] in self.shared and (c.get("label") or c.get("unit")):
                    bad.append(f"{t}.{c['name']}")
                if c.get("shared") and c["name"] not in self.shared:
                    bad.append(f"{t}.{c['name']} (marked shared, not in _shared.yaml)")
        self.assertEqual(bad, [], f"shared names given a definition of their own: {bad[:20]}")

    def test_every_column_of_a_public_table_has_a_unit(self):
        empty = []
        for t in self.public:
            p = self.files.get(t)
            if p is None:
                continue
            for c in load(p).get("columns") or []:
                if c["name"] in self.shared:
                    continue
                if not str(c.get("unit") or "").strip():
                    empty.append(f"{t}.{c['name']}")
        self.assertEqual(empty, [], f"{len(empty)} columns without a unit: {empty[:20]}")

    def test_columns_match_the_tables(self):
        held = [t for t in self.files if (TABLES / f"{t}.csv").is_file()]
        if not held:
            self.skipTest(f"no table is held in {TABLES} (a clean checkout); the column check runs where they are")
        wrong = []
        for t in held:
            listed = [c["name"] for c in load(self.files[t]).get("columns") or []]
            actual = header_row(TABLES / f"{t}.csv")
            if listed != actual:
                lacks = [c for c in listed if c not in actual]
                misses = [c for c in actual if c not in listed]
                wrong.append(f"{t}: lists {lacks} the table lacks, misses {misses}" if lacks or misses
                             else f"{t}: columns in another order")
        self.assertEqual(wrong, [], f"{len(wrong)} files disagree with their tables: {wrong[:10]}")

    def test_no_em_dash(self):
        bad = [p.name for p in VARS.glob("*.yaml") if EM in p.read_text(encoding="utf-8")]
        self.assertEqual(bad, [], f"files holding an em dash: {bad}")


if __name__ == "__main__":
    unittest.main()
