"""Session 1492 (chain 158): the datacenter's do-file, replication/datacenter/replicate.do. It reads only the page's public
hourly and carbon files and this folder's assumptions.csv (the same values as assumptions.json), and follows the owner's Stata
rules: no continuation operator, one empty line between commands outside loops and none inside, every column read as
text destrung with force. Stata is not on this machine: the file is read here, not run; replicate.py runs the same steps.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import csv
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "datacenter")
PUBLIC_DO = os.path.join(ROOT, "site", "public", "datacenter", "erw_2026_datacenter_replication.do")


class TheDoFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REP, "replicate.do"), encoding="utf-8", newline="") as f:
            cls.text = f.read()
        cls.lines = cls.text.split("\n")

    def test_no_continuation_operator(self):
        self.assertNotIn("///", self.text)
        self.assertNotIn("#delimit", self.text.lower())
        self.assertNotIn("\r", self.text)
        self.assertNotIn(chr(0x2014), self.text)
        self.assertNotIn(chr(0x2013), self.text)

    def test_one_empty_line_between_commands_outside_loops_and_none_inside(self):
        lines = self.lines[:-1] if self.lines[-1] == "" else self.lines
        depth, prev_blank = 0, True
        for i, line in enumerate(lines, 1):
            blank = line.strip() == ""
            if depth:
                self.assertFalse(blank, f"line {i}: an empty line inside a loop")
                if line.strip() == "}":
                    depth -= 1
                    prev_blank = False
                elif line.rstrip().endswith("{"):
                    depth += 1
                continue
            if blank:
                self.assertFalse(prev_blank, f"line {i}: two empty lines together")
                prev_blank = True
                continue
            self.assertTrue(prev_blank, f"line {i}: no empty line before this command: {line[:60]}")
            prev_blank = False
            if line.rstrip().endswith("{"):
                depth += 1
        self.assertEqual(depth, 0)

    def test_it_reads_only_the_public_file_and_the_assumptions(self):
        reads = re.findall(r'^import delimited using "([^"]+)"', self.text, flags=re.M)
        self.assertEqual(reads, ["../../site/public/datacenter/erw_2026_datacenter_hourly.csv", "assumptions.csv", "../../site/public/datacenter/erw_2026_datacenter_hourly.csv", "../../site/public/datacenter/erw_2026_datacenter_carbon.csv"])
        self.assertIn("destring value, replace force", self.text)
        # the ten defaults come from the file, not from scalars typed in the do-file
        for n in ("mw", "gpu_kw", "pue"):
            self.assertNotRegex(self.text, rf"(?m)^scalar s_{n} = ")

    def test_the_steps_are_the_public_do_files(self):
        with open(PUBLIC_DO, encoding="utf-8") as f:
            public = f.read()
        for step in ('display "power per GPU-hour, USD: " %9.4f s_l12_usd_mwh * s_gpu_kw * s_pue / 1000', "scalar s_bad_rank"):
            self.assertIn(step, public)
            self.assertIn(step, self.text)

    def test_the_csv_assumptions_are_the_json_ones(self):
        with open(os.path.join(REP, "assumptions.json"), encoding="utf-8") as f:
            a = json.load(f)
        with open(os.path.join(REP, "assumptions.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 3)
        by = {}
        for r in rows:
            self.assertEqual(float(r["value"]), float(a[by.get(r["name"], r["name"])]["value"]), r["name"])

    def test_the_page_figures_csv_is_the_json_one(self):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            p = json.load(f)
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([(r["field"], float(r["page"])) for r in rows], [(x["field"], float(x["page"])) for x in p["figures"]])


if __name__ == "__main__":
    unittest.main()
