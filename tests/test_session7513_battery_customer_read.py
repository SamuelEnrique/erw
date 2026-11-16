"""Session 7513 (chain 304, part B): What a battery saves a customer (/battery/customer) read as its reader.

Energy Research Warehouse (ERW). No network, no model, no warehouse table: the page reads none.

- TheReadDrawn   site/scripts/test-battery-customer-read.mjs: the five cases of the read drawn with the page's own
                 calculator; a rate typed in cents is told its unit; the line under the hours field says whose hours;
                 the round trip of the site's three battery pages; no way to send or store was added.
- TheReadFile    docs/reviews/battery-customer-read-2026-11-16.md: the reader, the cases and how it was read at the top;
                 ten numbered rows, each with a kind; five closing bullets; the figures the test above holds.

    python -m unittest tests.test_session7513_battery_customer_read -v
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
READ = ("docs", "reviews", "battery-customer-read-2026-11-16.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheReadDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.done = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-battery-customer-read.mjs"],
                                 cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)

    def test_every_check_passes(self):
        self.assertEqual(self.done.returncode, 0, self.done.stdout[-3000:] + self.done.stderr[-1500:])
        self.assertNotIn("FAIL", self.done.stdout)
        m = re.search(r"(\d+) of (\d+) passed", self.done.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 28, self.done.stdout[-500:])

    def test_the_three_site_rows_are_held(self):
        self.assertRegex(self.done.stdout, r"(?m)^ok   row 1: 14\.66 and 5\.82")
        self.assertRegex(self.done.stdout, r"(?m)^ok   row 2: the line under")
        self.assertRegex(self.done.stdout, r"(?m)^ok   row 3: the round trip starts at 86 percent")


class TheReadFile(unittest.TestCase):
    def test_the_top_names_the_reader_the_cases_and_how_it_was_read(self):
        read = src(*READ)
        top = read.split("## The cases, in one line each")[0]
        for words in ("**The reader.**", "**The five cases.**", "**How it was read, and what was not seen.**", "energy manager of a grocery chain",
                      "27,625 square feet", "about 247 kW in 2012", "NREL/TP-6A20-64987", "No key was pressed", "No web request was made"):
            self.assertIn(words, top)
        for n in range(1, 6):
            self.assertIn(f"({n}) ", top)

    def test_ten_rows_each_with_a_kind(self):
        read = src(*READ)
        table = read.split("## The rows")[1].split("**Counts.**")[0]
        rows = [ln for ln in table.splitlines() if re.match(r"\| \d+ \|", ln)]
        self.assertEqual([int(r.split("|")[1]) for r in rows], list(range(1, 11)))
        kinds = [r.split("|")[5].strip() for r in rows]
        self.assertEqual((kinds.count("site"), kinds.count("ruling"), kinds.count("browser")), (3, 6, 1))
        self.assertIn("Site, fixed: 3 (rows 1 to 3). Rulings: 6 (rows 4 to 9). Browser: 1 (row 10). Data machine: 0.", read)

    def test_it_ends_with_five_bullets(self):
        end = src(*READ).split("## What this reader still cannot get from the tool, and why")[1]
        self.assertEqual(len([ln for ln in end.splitlines() if ln.startswith("- **")]), 5)

    def test_its_figures_are_the_ones_the_drawn_test_holds(self):
        read, test = src(*READ), src("site", "scripts", "test-battery-customer-read.mjs")
        for shown, held in (("USD 3,519", "$3,519 a year"), ("USD 12,795", "$12,795 a year"), ("USD 5,977", "$5,977 a year"), ("USD 21,733", "$21,733 a year"),
                            ("USD 13,376", "$13,376 a year"), ("USD 8,784", "8783.57"), ("USD 4,593", "4592.85"), ("USD 1,620", "1619.6"), ("USD 9,824", "$9,824 a year"),
                            ("USD 22,080", "$22,080 a year"), ("USD 13,906", "13905.69"), ("USD 1,633.50", "1633.5"), ("$70,169 a year", "$70,169 a year"),
                            ("USD 337", "=== 337"), ("USD 522", "=== 522"), ("USD 1,897", "=== 1897"), ("USD 965", "964.8"), ("USD 2,194", "2194.2")):
            self.assertIn(shown, read, shown)
            self.assertIn(held, test, held)

    def test_part_a_is_cited_and_not_reopened(self):
        read = src(*READ)
        for words in ("part A, row 3", "part A, row 5", "part A, row 6", "part A, row 8"):
            self.assertIn(words, read)
        faults = src("docs", "reviews", "battery-customer-faults-2026-11-16.md")
        self.assertIn("Site faults fixed: 2 (rows 1 and 2). Data machine: 0", faults)      # part A's file is as it was

    def test_no_long_dash_in_what_the_session_wrote(self):
        for parts in (READ, ("site", "scripts", "test-battery-customer-read.mjs"), ("tests", "test_session7513_battery_customer_read.py"),
                      ("site", "lib", "customerbattery.ts"), ("site", "app", "battery", "customer", "Calc.tsx"), ("site", "app", "battery", "customer", "Decisions.tsx"),
                      ("docs", "methods", "battery_customer.md")):
            text = src(*parts)
            self.assertNotIn(chr(0x2014), text, parts[-1])
            self.assertNotIn(chr(0x2013), text, parts[-1])


if __name__ == "__main__":
    unittest.main()
