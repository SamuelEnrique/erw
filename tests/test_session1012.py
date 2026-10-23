"""Session 1012 (chain 070): the package reads what the pages read. Ten figures of the Grid tool's ERCOT page and the
battery page, with their check keys and shown values (package/tests/page_figures.json), are recomputed by the Python
package in a remote test (package/tests/test_page_figures.py); the method note lists them with their results. This
test, offline, holds the file's shape and the note's table. No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Figures(unittest.TestCase):
    def test_ten_keys_of_three_kinds(self):
        fx = json.loads(src("package", "tests", "page_figures.json"))["figures"]
        self.assertEqual(len(fx), 10)
        self.assertEqual({f["key"].split("|")[0] for f in fx}, {"series", "series_max", "series_sum"})
        self.assertEqual({f["page"] for f in fx}, {"/grid/ercot", "/cost-of-power/battery"})
        for f in fx:
            float(f["raw"])
            self.assertIn(f["backend"], ("live", "local"))

    def test_the_note_lists_them(self):
        spec = src("docs", "methods", "packages.md")
        self.assertIn("## The package reads what the pages read (session 1012)", spec)
        for f in json.loads(src("package", "tests", "page_figures.json"))["figures"]:
            self.assertIn(f"`{f['key']}`", spec)

    def test_the_remote_test_is_marked(self):
        self.assertIn("pytestmark = pytest.mark.remote", src("package", "tests", "test_page_figures.py"))


if __name__ == "__main__":
    unittest.main()
