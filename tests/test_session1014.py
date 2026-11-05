"""Session 1014 (chain 070): the Stata and R packages, second pass. With no result of the owner's run yet
(docs/reviews/packages-owner-run.md does not exist), the two were read against the specification and the conformance
file: a table refused by Redivis's streaming cap is read through its export, the citation names the released version's
tag, and the table list has titles, in both. What still differs is said in the method note. Both checkers pass. No
request, no model call."""
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SecondPass(unittest.TestCase):
    def test_stata(self):
        ado = src("packages", "stata", "erw.ado")
        for prog in ("_erw_redivis_export", "_erw_json_field", "_erw_redivis_version"):
            self.assertIn(f"program define {prog}", ado)
        self.assertIn('"`api\'/tables/datapages.erw:b9wm.`table\'/exports"', ado)
        self.assertIn("_erw_record release, saving(", ado)
        C = load("check_ado_1014", "packages", "stata", "check_ado.py")
        progs, p = C.programs(ado)
        p += C.check_structure(ado, progs) + C.check_style(progs)
        self.assertEqual(p, [])

    def test_r(self):
        r = src("packages", "r", "erw", "R", "erw.R")
        for fn in (".erw_redivis_export", ".erw_json_field", ".erw_redivis_version"):
            self.assertIn(f"{fn} <- function", r)
        self.assertIn('release = "docs/redivis/release-v1-stanford/tables.csv"', r)
        C = load("check_r_1014", "packages", "r", "check_r.py")
        self.assertEqual(C.scan(r, "erw.R")[0], [])
        self.assertEqual(C.check_description(), [])

    def test_the_note_says_what_still_differs(self):
        spec = src("docs", "methods", "packages.md")
        self.assertIn("## Where the three still differ (session 1014)", spec)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "reviews", "packages-owner-run.md")))


if __name__ == "__main__":
    unittest.main()
