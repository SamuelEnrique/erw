"""Session 1010 (chain 070): the release package proves the packages. The Stanford dataset's README says how to read it
in Python, Stata and R; its table list carries each table's fetch line in each package (the specification's "One line a
table"); the release note gains "After the click" with each language's commands. Nothing is released. No request."""
import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
DOCS = os.path.join(ROOT, "docs", "redivis", "release-v1-stanford")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Release(unittest.TestCase):
    def test_every_table_has_its_three_lines(self):
        with open(os.path.join(DOCS, "tables.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 190)
        for r in rows:
            if r["shape"] == "metadata":
                self.assertEqual((r["fetch_python"], r["fetch_stata"], r["fetch_r"]), ("", "", ""))
                continue
            t = r["table"]
            self.assertEqual(r["fetch_python"], f'erw.fetch("{t}")')
            self.assertEqual(r["fetch_stata"], f"erw fetch {t}, clear")
            self.assertEqual(r["fetch_r"], f'erw_fetch("{t}")')

    def test_the_readme_says_how(self):
        readme = src("docs", "redivis", "release-v1-stanford", "README.md")
        self.assertIn("## Read it in Python, Stata or R", readme)
        for line in ('pip install "erw-energy[redivis] @ git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"',
                     'net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/") replace',
                     'remotes::install_github("SamuelEnrique/erw", subdir = "packages/r/erw")'):
            self.assertIn(line, readme)
        import release_v1 as R
        self.assertEqual(R.FETCH["fetch_stata"].format(t="x"), "erw fetch x, clear")

    def test_the_release_note_has_after_the_click(self):
        note = src("docs", "reviews", "redivis-v1-release-note-2026-10-23.md")
        self.assertIn("## After the click: prove the release in each language (session 1010, chain 070)", note)
        for s in ('backend="redivis")', "backend(redivis) clear", 'backend = "redivis")'):
            self.assertIn(s, note)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()
