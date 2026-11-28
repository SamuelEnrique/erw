"""Session 10238, the small pages' audit, finding 10 (docs/reviews/small-pages-audit-2026-11-26.md): the resource map's
method note said the queue overlay draws rows "from the queue reports of the grids whose operators allow it", and names
ISO-NE among them. The ERW's own license status holds ISO-NE's queue table as "license needed" (needs written
permission) since 21 October 2026. The words drop the claim; whether ISO-NE's rows are drawn is the open ruling of the
map's audit (faults row 6, wip/alt-map-1), not changed here."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheStatus(unittest.TestCase):
    def test_isone_queue_is_shown_on_the_overlay_and_held_for_a_license(self):
        lib = re.sub(r"\s+", " ", src("site", "lib", "resources.ts"))
        # session 11405 (wip/ready-held-out, the weekend page's decision 1): held for a license, so not drawn
        self.assertIn('{ id: "isone", label: "ISO-NE", shown: false, words: "license needed", why: "ISO-NE', lib)
        verdicts = src("warehouse", "metadata", "license_verdicts.csv")
        self.assertRegex(verdicts, r"(?m)^ISO-NE,4,")
        holds = os.path.join(ROOT, "docs", "licenses_holds.csv")
        if os.path.exists(holds):
            self.assertIn("isone_interconnection_queue", src("docs", "licenses_holds.csv"))


class TheWords(unittest.TestCase):
    def test_the_note_does_not_say_the_operators_allow_it(self):
        v = src("site", "app", "resources", "view.tsx")
        self.assertNotIn("the grids whose operators allow it", v)
        self.assertIn("from the queue reports of these grids: {QUEUE_GRIDS", v)


if __name__ == "__main__":
    unittest.main()
