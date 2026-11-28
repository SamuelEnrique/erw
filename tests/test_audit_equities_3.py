"""Audit of /equities, finding 3 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): the SEC industry
code rule is applied exactly, and what it gives is not what the segments' names say.

- Integrated oil and gas and Refining hold the same 18 companies (SIC 2911 in both): two names, one list.
- Independent power producers holds 64 companies, 63 of them also in Regulated electric and gas utilities (SIC 4911 in
  both); one company is there by its own code, AES (4991).
- So the nine segments that hold a company are eight lists.
- A code is a company's own filing choice, sometimes old: ConocoPhillips (no refinery since 2012) is in Refining and
  Integrated by 2911; HF Sinclair, a refiner, is in Midstream by 4610 and not in Refining.

The counts the page prints are right by the written rule (and the rule says "in both" on hover). The test shows what
the rule gives on main's files (it passes on main). A named list, or a split of 2911 and 4911, is judgment the note
leaves to Samuel: nothing is changed."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IDX = os.path.join(ROOT, "site", "data", "equities", "index.json")


class RuleAndNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(IDX, encoding="utf-8") as f:
            cls.idx = json.load(f)
        cls.seg = {s["id"]: {c["ticker"] for c in cls.idx["companies"] if s["id"] in c["segments"]} for s in cls.idx["segments"]}

    def test_counts_are_the_rules(self):
        for s in self.idx["segments"]:
            self.assertEqual(s["n_companies"], len(self.seg[s["id"]]), s["id"])

    def test_two_names_one_list(self):
        self.assertEqual(self.seg["integrated_oil_gas"], self.seg["refining"])
        self.assertEqual(len(self.seg["refining"]), 18)

    def test_independent_power_is_the_electric_utilities(self):
        ipp, reg = self.seg["independent_power"], self.seg["regulated_utilities"]
        self.assertEqual(len(ipp), 64)
        self.assertEqual(len(ipp & reg), 63)
        self.assertEqual(ipp - reg, {"AES"})

    def test_nine_segments_eight_lists(self):
        filled = [v for v in self.seg.values() if v]
        self.assertEqual(len(filled), 9)
        self.assertEqual(len({frozenset(v) for v in filled}), 8)

    def test_a_code_is_the_filers_own(self):
        self.assertIn("COP", self.seg["refining"])
        self.assertIn("DINO", self.seg["midstream_pipelines"])
        self.assertNotIn("DINO", self.seg["refining"])


if __name__ == "__main__":
    unittest.main()
