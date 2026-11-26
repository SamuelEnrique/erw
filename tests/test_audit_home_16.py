"""Audit of the Thesis Builder, finding 13's ruling (session 10236, docs/reviews/home-model-audit-2026-11-26.md), a test
only: warehouse/thesis/build.py, check_numbers, keeps a sentence of 40 characters or more whose numbers no cited source
holds and adds "(not confirmed: <the numbers>)"; only a trend's written Fact is replaced by its cited claim
(run.py, market_report). Where the saved runs of 6 October 2026 are held (warehouse/output/thesis_state on the main
copy), it counts the texts so printed: 49 texts, 80 numbers, in the five runs (9, 10, 7, 10, 13 texts).

This test shows it and passes on main. The choice, default "left as it is": a sentence holding a number no cited source
holds is not shown, as a trend's Fact already is not ("not confirmed" in its place). The effect on the saved runs: 49
texts of 5 runs replaced. No fix is made.
Nothing here sets the environment or makes a request."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheUnconfirmedSentences(unittest.TestCase):
    def test_a_long_sentence_is_kept_with_its_mark(self):
        b = src("warehouse", "thesis", "build.py")
        self.assertIn('return "not confirmed" if len(text) < 40 or not pool else text + f" (not confirmed: {\', \'.join(bad[:4])})"', b)
        run = src("warehouse", "thesis", "run.py")
        self.assertIn('if facts.get(n) and "not confirmed" in fact["text"]:', run)        # the one place a sentence is replaced

    def test_the_saved_runs_print_them(self):
        d = os.path.join(ROOT, "warehouse", "output", "thesis_state")
        files = sorted(f for f in os.listdir(d) if f.endswith(".json") and not f.startswith("partial_")) if os.path.isdir(d) else []
        if not files:
            self.skipTest("no saved run on this machine")
        counts = []
        for f in files:
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                rep = json.dumps(json.load(fh).get("report") or {}, ensure_ascii=False)
            counts.append(len(re.findall(r"\(not confirmed: [^)]*\)", rep)))
        self.assertGreater(sum(counts), 0, counts)


if __name__ == "__main__":
    unittest.main()
