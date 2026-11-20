"""Audit of "What a generator earns", finding 8 (session 9841, docs/reviews/generator-model-audit-2026-11-20.md): the note's
table of the scenarios' defaults (docs/methods/generator_earns_algorithm.md, section 11.1) gave the hurdle rate as 9.6 and
solar's degradation as 0, where the page uses 12 (session 208) and 0.7 (ruling 7a of 18 October 2026).

The test reads the two rows of the note's table and the two constants of site/lib/seller/finance.ts and holds them equal.
It fails on main (the note says 9.6 and 0) and passes on this branch, whose fix is the two rows in words."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NoteTableAgainstCode(unittest.TestCase):
    def test_defaults_in_the_note_are_the_codes(self):
        lib = read("site", "lib", "seller", "finance.ts")
        hurdle = float(re.search(r"export const HURDLE = ([\d.]+);", lib).group(1))
        solar = float(re.search(r"export const SOLAR_DEG = ([\d.]+);", lib).group(1))
        note = read("docs", "methods", "generator_earns_algorithm.md")
        h = re.search(r"^\| Hurdle rate, percent a year \| ([^|]+) \|", note, re.M).group(1).strip()
        d = re.search(r"^\| Degradation, percent a year \| ([^|]+) \|", note, re.M).group(1).strip()
        self.assertEqual(float(h), hurdle, f"the note's hurdle {h}, the code's {hurdle}")
        self.assertIn(f"solar {solar:g}", d, f"the note's degradation row: {d}; the code's solar {solar}")


if __name__ == "__main__":
    unittest.main()
