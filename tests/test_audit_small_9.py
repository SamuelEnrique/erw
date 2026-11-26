"""Session 10238, the small pages' audit, finding 9 (docs/reviews/small-pages-audit-2026-11-26.md): the resource map's
decision "kinds-named" said coal has no layer among the files and is greyed, and its method document said "No layer of
the three is among the files". The coal fields are a layer since 19 November 2026 (manifest_added.json, the data
machine's list; site/data/resources/layers/coal_fields.json), drawn in their own group."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "site", "data", "resources")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheFiles(unittest.TestCase):
    def test_the_coal_fields_are_a_layer_with_its_file(self):
        added = json.load(open(os.path.join(RES, "manifest_added.json"), encoding="utf-8"))
        coal = [l for l in added["layers"] if l["id"] == "coal_fields"]
        self.assertEqual(len(coal), 1)
        self.assertEqual(coal[0]["group"], "coal")
        self.assertTrue(os.path.exists(os.path.join(RES, "layers", "coal_fields.json")))
        self.assertNotIn("coal_fields", [x.get("id") for x in added.get("missing", [])])


class TheWords(unittest.TestCase):
    def test_the_decision_does_not_call_coal_greyed(self):
        d = src("site", "app", "resources", "Decisions.tsx")
        self.assertNotIn("(coal, uranium, critical minerals, and the gross capacity factor of wind)", d)
        self.assertIn("(uranium, critical minerals, and the gross capacity factor of wind)", d)
        self.assertIn("Coal has a layer since 19 November 2026, the coal fields.", d)

    def test_the_method_document_says_the_coal_fields_arrived(self):
        n = re.sub(r"\s+", " ", src("docs", "methods", "resources.md"))
        self.assertIn("since then coal is a layer, and only uranium and critical minerals are greyed", n)


if __name__ == "__main__":
    unittest.main()
