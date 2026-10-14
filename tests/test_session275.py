"""Session 275: Redivis release v1, prepared.

Energy Research Warehouse (ERW). The package for one click (docs/redivis/release-v1/ and docs/redivis/release-v1.md),
built from the repository's records; nothing done on Redivis. Held here: the list agrees with coverage and the license
record; no internal table and no held table is in v1; every v1 table has a description, a license line and a
citation; the script makes no request; the steps name the 40 held tables' removal and the click as a person's.
"""

import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import release_v1 as R  # noqa: E402

EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def table_rows():
    with open(os.path.join(ROOT, "docs", "redivis", "release-v1", "tables.csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class ThePackage(unittest.TestCase):
    def test_it_agrees_with_the_records(self):
        self.assertEqual(R.check(), [])

    def test_no_internal_or_held_table_is_in_v1(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            lic = {r["table"]: r["license"] for r in csv.DictReader(f)}
        held = R.held()
        for r in table_rows():
            if r["in_v1"] == "yes" and r["shape"] != "metadata":
                self.assertEqual(lic[r["table"]], "public", r["table"])
                self.assertNotIn(r["table"], held)
                for k in ("description", "license_line", "citation"):
                    self.assertTrue(r[k].strip(), (r["table"], k))
                self.assertRegex(r["license_line"], r"^License: (public|CC BY 4.0)", r["table"])   # Berkeley Lab's two tables carry CC BY 4.0
                self.assertIn("Redivis dataset `energy_research_warehouse`, version v1", r["citation"])
        self.assertEqual({r["table"] for r in table_rows() if r["in_v1"] == "no" and r["reason"].startswith("license needed")}, set(held) & set(lic))

    def test_the_counts_the_steps_state(self):
        rows = table_rows()
        v1 = [r for r in rows if r["in_v1"] == "yes" and r["shape"] != "metadata"]
        out = [r for r in rows if r["in_v1"] == "no"]
        steps = src("docs", "redivis", "release-v1.md")
        self.assertIn(f"**{len(v1)} tables and the three metadata tables**", steps)
        self.assertIn(f"**{len(out)} tables of the public draft are held out**", steps)
        self.assertIn(f"Version 1 holds {len(v1)} tables", src("docs", "redivis", "release-v1", "README.md"))


class NothingOnRedivis(unittest.TestCase):
    def test_the_script_asks_nothing_and_the_click_is_a_persons(self):
        code = src("warehouse", "redivis", "release_v1.py")
        for word in ("import redivis", "requests", "urllib", "upload.py --all", ".release("):
            self.assertNotIn(word, code)
        steps = src("docs", "redivis", "release-v1.md")
        self.assertIn("**Nothing was created, changed or released on Redivis in preparing this.**", steps)
        self.assertIn("**Click Release.**", steps)
        for rel in ("docs/redivis/release-v1.md", "docs/redivis/release-v1/README.md", "docs/redivis/release-v1/tables.csv",
                    "warehouse/redivis/release_v1.py", "tests/test_session275.py"):
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
