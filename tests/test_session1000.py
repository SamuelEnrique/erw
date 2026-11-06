"""Session 1000 (chain 070): the packages' one specification, docs/methods/packages.md. It names the six calls, the
three backends and the column types by shape, and its citation line is release_v1.py's own words on the Stanford
dataset. The Python package is read against it (the gaps table). No request, no model call."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Specification(unittest.TestCase):
    def setUp(self):
        self.spec = src("docs", "methods", "packages.md")

    def test_the_six_calls_and_three_backends(self):
        for call in ("tables()", "coverage(table)", "fetch(table, entity=, variable=, start=, end=, backend=)",
                     "cite(table)", "license(table)", "standard(table)"):
            self.assertIn(f"### `{call}`", self.spec)
        for b in ("`redivis`", "`live`", "`local`", "`auto`"):
            self.assertIn(b, self.spec)
        self.assertIn("datapages.erw:b9wm", self.spec)

    def test_the_citation_is_the_release_package_words(self):
        rel = src("warehouse", "redivis", "release_v1.py")
        self.assertIn('STANFORD = {"dataset": "datapages.erw"', rel)
        self.assertIn("Via the Energy Research Warehouse (ERW), table `{table}`, Redivis dataset `{DATASET}`, version", rel)
        self.assertIn("Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `datapages.erw`, version <tag>",
                      self.spec)

    def test_every_shape_has_its_types(self):
        for shape in ("series", "entities", "events"):
            self.assertTrue(re.search(rf"^\| {shape} \| ", self.spec, re.M), shape)
        self.assertIn("stringcols(_all)", self.spec)
        self.assertIn('tz = "UTC"', self.spec)

    def test_the_python_package_is_read_against_it(self):
        self.assertIn("## The Python package against this note (session 1000)", self.spec)
        for call in ("`tables()`", "`license(table)`", "`standard(table)`", "Redivis", "The live set", "Requests"):
            self.assertTrue(re.search(rf"^\| {re.escape(call)}", self.spec, re.M), call)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.spec)


if __name__ == "__main__":
    unittest.main()
