"""Session 3298 (platform tool 15, the rigor layer): package/llms.txt's catalogue of every table, written by
scripts/build_llms.py from warehouse/metadata/coverage.csv, sources.csv and the package's license record.

  1. The catalogue is never older than coverage.csv's newest row: its "Generated:" time is at or after the newest
     last_run. A session or a run that rebuilds coverage without the catalogue fails here
     (build_coverage.py rewrites it after every build, so this fails only when that step failed or was skipped).
  2. It lists every table of coverage.csv once: the public ones (the package's verdict `public`, the same list
     erw/data/tables.csv ships) with their seven cells, the held ones by name with "license needed" and no figure.
  3. Every method note it names exists.
  4. The chat's briefing leaves it out (site/lib/chat/spec.json), and no em or en dash is in the file.

No request, no model call; nothing here writes a file.
"""
import csv
import os
import re
import unittest
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def rows(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


LLMS = src("package", "llms.txt")
BEGIN = "<!-- BEGIN catalogue: written by scripts/build_llms.py, never by hand -->"
END = "<!-- END catalogue -->"


def utc(ts):
    return datetime.strptime(ts.strip(), "%Y-%m-%dT%H:%M:%SZ")


def catalogue():
    return LLMS.split(BEGIN, 1)[1].split(END, 1)[0]


class Fresh(unittest.TestCase):
    def test_the_catalogue_is_not_older_than_coverage_s_newest_row(self):
        self.assertIn(BEGIN, LLMS, "package/llms.txt has no catalogue: run python scripts/build_llms.py")
        m = re.search(r"^Generated: (\S+) by scripts/build_llms.py", catalogue(), re.M)
        self.assertIsNotNone(m, "the catalogue has no Generated line")
        newest = max(r["last_run"] for r in rows("warehouse", "metadata", "coverage.csv") if r.get("last_run"))
        self.assertGreaterEqual(utc(m.group(1)), utc(newest),
                                f"package/llms.txt's catalogue ({m.group(1)}) is older than coverage.csv's newest row "
                                f"({newest}): run python scripts/build_llms.py and commit package/llms.txt")

    def test_coverage_rebuilds_rewrite_it(self):
        bc = src("warehouse", "metadata", "build_coverage.py")
        self.assertIn("def write_llms_catalogue():", bc)
        self.assertIn("        write_llms_catalogue()", bc)
        self.assertIn("package/llms.txt", src(".github", "workflows", "daily-prices.yml").split("paths=(", 1)[1].split(")", 1)[0])
        self.assertIn("package/llms.txt", src("warehouse", "run_data_machine.sh").split("META_PATHS=(", 1)[1].split(")", 1)[0])


class Lists(unittest.TestCase):
    def setUp(self):
        text = catalogue()
        self.public_block = text.split("### 10.1 Public tables", 1)[1].split("### 10.2", 1)[0]
        self.held_block = text.split("### 10.2 Held tables", 1)[1].split("### 10.3", 1)[0]
        self.public = re.findall(r"^- `([a-z0-9_]+)`: ", self.public_block, re.M)
        self.held = re.findall(r"^- `([a-z0-9_]+)`: license needed", self.held_block, re.M)

    def test_every_table_once(self):
        cov = [r["table"] for r in rows("warehouse", "metadata", "coverage.csv")]
        self.assertEqual(sorted(self.public + self.held), sorted(cov))
        self.assertEqual(len(set(self.public + self.held)), len(cov))

    def test_public_is_the_package_s_public(self):
        shipped = {r["table"] for r in rows("package", "src", "erw", "data", "tables.csv") if r["verdict"] == "public"}
        self.assertEqual(set(self.public), shipped)

    def test_each_public_line_has_its_cells(self):
        for ln in self.public_block.splitlines():
            if ln.startswith("- `"):
                for cell in (". Unit: ", ". Period: ", ". Granularity: ", ". License: public (", ". Method: ", ". Download: "):
                    self.assertIn(cell, ln, ln[:80])

    def test_held_lines_carry_no_figure(self):
        for ln in self.held_block.splitlines():
            if ln.startswith("- `"):
                self.assertRegex(ln, r"^- `[a-z0-9_]+`: license needed \((internal|unsettled|not in the record)\)$")

    def test_every_method_note_named_exists(self):
        for path in re.findall(r"\. Method: (docs/methods/[^ ]+\.md)\. ", self.public_block):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, *path.split("/"))), path)

    def test_the_pages_are_listed_with_ask_and_the_periodicals(self):
        pages = catalogue().split("### 10.3", 1)[1]
        for href in ("/ask", "/digest", "/roundup", "/data", "/board"):
            self.assertIn(f"\n- {href} (", pages)
        self.assertLess(pages.index("The periodicals:"), pages.index("Ask:"))


class Briefing(unittest.TestCase):
    def test_the_chat_leaves_the_catalogue_out(self):
        spec = src("site", "lib", "chat", "spec.json")
        self.assertNotIn("BEGIN catalogue", spec)
        self.assertNotIn("### 10.1 Public tables", spec)

    def test_no_dash(self):
        self.assertNotIn(chr(0x2014), LLMS)
        self.assertNotIn(chr(0x2013), LLMS)
        self.assertNotIn(chr(0x2014), src("scripts", "build_llms.py"))
        self.assertNotIn(chr(0x2013), src("scripts", "build_llms.py"))


if __name__ == "__main__":
    unittest.main()
