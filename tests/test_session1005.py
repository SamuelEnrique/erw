"""Session 1005 (chain 070): the R package erw (packages/r/erw), checked where R is not installed
(packages/r/check_r.py): the R files' brackets and escapes, NAMESPACE against the exported functions, DESCRIPTION, and
the address .erw_live_url builds for each of the ten real calls, which must be the Python package's. The checker is
shown to catch each kind of fault on a broken copy. No request, no model call."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "packages" / "r"
spec = importlib.util.spec_from_file_location("check_r_1005", R / "check_r.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
SRC = (R / "erw" / "R" / "erw.R").read_text(encoding="utf-8")


class ThePackage(unittest.TestCase):
    def test_every_check_passes(self):
        for f in sorted((R / "erw").rglob("*.R")):
            self.assertEqual(C.scan(f.read_text(encoding="utf-8"), f.name)[0], [], f.name)
        self.assertEqual(C.check_namespace(), [])
        self.assertEqual(C.check_description(), [])
        p, lines = C.check_addresses()
        self.assertEqual(p, [])
        self.assertEqual(len(lines), 10)

    def test_base_r_only(self):
        self.assertNotIn("library(", SRC)
        self.assertNotIn("require(", SRC)
        self.assertIn('method = "libcurl", headers = headers', SRC)


class TheCheckerCatches(unittest.TestCase):
    def test_an_unbalanced_bracket(self):
        self.assertTrue(C.scan(SRC.replace("  q <- paste0(\"select=*", "  q <- paste0((\"select=*", 1), "erw.R")[0])

    def test_an_escape_r_does_not_have(self):
        self.assertTrue(C.scan('x <- "a\\[b"\n', "t.R")[0])
        self.assertFalse(C.scan('x <- "a\\\\[b"\n', "t.R")[0])

    def test_an_address_that_differs(self):
        bad = SRC.replace('items <- paste0(items, sep, "%22", v, "%22")', 'items <- paste0(items, sep, v)', 1)
        body = C.function_body(bad, ".erw_live_url")[1]
        got = C.run(C.statements(body), {"table": "t", "base": "<B>", "shape": "series", "offset": 0, "limit": 1000,
                                          "entity": ["eia:x"], "variable": None, "start": None, "end": None,
                                          "market": None, "ba": None, "year": None})   # session 1017
        self.assertNotIn("%22eia:x%22", got)


if __name__ == "__main__":
    unittest.main()
