"""Session 1006 (chain 070): one test, three packages. packages/conformance/conformance.json holds twenty calls with
the answers the Python package gave (the live set and the record); the Python runner passed all twenty
(results_python.json); the Stata and R runners are written from the same file (write_runners.py), in sync with it, the
Stata one in the owner's style and the R one with balanced brackets and R's escapes. No request, no model call."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "packages" / "conformance"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


W = load("write_runners_1006", CONF / "write_runners.py")
STATA = load("check_ado_1006", ROOT / "packages" / "stata" / "check_ado.py")
R = load("check_r_1006", ROOT / "packages" / "r" / "check_r.py")
REC = json.loads((CONF / "conformance.json").read_text(encoding="utf-8"))


class Conformance(unittest.TestCase):
    def test_twenty_calls_of_six_kinds(self):
        calls = REC["calls"]
        self.assertEqual(len(calls), 20)
        kinds = [c["call"] for c in calls]
        self.assertEqual(kinds.count("fetch"), 10)
        self.assertEqual(set(kinds), {"fetch", "cite", "license", "refusal", "standard", "tables"})
        ref = next(c for c in calls if c["call"] == "refusal")["expect"]["message"]
        self.assertTrue(ref.startswith("iso_rtm_hub_prices is not public: unsettled. "))
        self.assertLessEqual(REC["requests"]["live"], 50)

    def test_python_passes_every_call(self):
        res = json.loads((CONF / "results_python.json").read_text(encoding="utf-8"))
        self.assertEqual((res["passed"], res["of"]), (20, 20))

    def test_the_runners_are_written_from_the_file(self):
        self.assertEqual((CONF / "run_stata.do").read_text(encoding="utf-8"), W.stata(REC["calls"]))
        self.assertEqual((CONF / "run_r.R").read_text(encoding="utf-8"), W.r(REC["calls"]))

    def test_the_runners_read_as_their_languages(self):
        self.assertEqual(STATA.check_do((CONF / "run_stata.do").read_text(encoding="utf-8")), [])
        self.assertEqual(R.scan((CONF / "run_r.R").read_text(encoding="utf-8"), "run_r.R")[0], [])

    def test_the_specification_has_the_table(self):
        spec = (ROOT / "docs" / "methods" / "packages.md").read_text(encoding="utf-8")
        self.assertIn("## The conformance file (session 1006)", spec)


if __name__ == "__main__":
    unittest.main()
