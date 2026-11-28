"""wip/ready-thesis-unconfirmed (session 11406, chain 770, part C): the other choice of the home page audit of
26 November, finding 13 (docs/reviews/home-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the Thesis Builder's check_numbers (warehouse/thesis/build.py) keeps a text of 40 characters or more whose
numbers no cited source holds and adds "(not confirmed: <the numbers>)". On this branch such a text reads "not
confirmed" whatever its length, and the page draws a saved run's marked text the same way (site/lib/thesis/view.ts,
str). The saved runs of 6 October 2026 (warehouse/output/thesis_state on the main copy, read only): 49 texts in 5 runs
(9, 10, 7, 10, 13) are drawn "not confirmed" instead of a sentence with its mark (before 49 marked sentences, after
0). The audit's test (tests/test_audit_home_16.py on wip/audit-home-16) is carried, turned round."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MAIN_COPY = os.environ.get("ERW_MAIN_COPY") or os.path.abspath(os.path.join(ROOT, "..", "erw"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class UnconfirmedSentencesAreNotShown(unittest.TestCase):
    def test_the_builder_and_the_page(self):
        b = src("warehouse", "thesis", "build.py")
        self.assertNotIn('text + f" (not confirmed: {\', \'.join(bad[:4])})"', b)
        body = b[b.index("def check_numbers"):b.index("PUBLIC = re.compile")]
        self.assertIn('        return "not confirmed"\n    return text', body)
        v = src("site", "lib", "thesis", "view.ts")
        self.assertIn("export const UNCONFIRMED = /\\(not confirmed: [^)]*\\)/;", v)
        self.assertIn('(UNCONFIRMED.test(v) ? "not confirmed" : v)', v)

    def test_the_saved_runs(self):
        found = None
        for root in (ROOT, MAIN_COPY):
            d = os.path.join(root, "warehouse", "output", "thesis_state")
            if os.path.isdir(d):
                found = d
                break
        if not found:
            self.skipTest("no saved run on this machine")
        files = sorted(f for f in os.listdir(found) if f.endswith(".json") and not f.startswith("partial_"))
        texts = []
        for f in files:
            with open(os.path.join(found, f), encoding="utf-8") as fh:
                rep = json.load(fh).get("report") or {}

            def walk(x):
                if isinstance(x, dict):
                    for y in x.values():
                        yield from walk(y)
                elif isinstance(x, list):
                    for y in x:
                        yield from walk(y)
                elif isinstance(x, str):
                    yield x
            texts.append(sum(1 for t in walk(rep) if re.search(r"\(not confirmed: [^)]*\)", t)))
        print(f"saved runs: {len(files)}, texts drawn 'not confirmed' on this branch: {sum(texts)} {texts}")
        self.assertGreater(sum(texts), 0)


if __name__ == "__main__":
    unittest.main()
