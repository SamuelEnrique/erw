"""Session 1003 (chain 070): the Stata command erw (packages/stata/erw.ado, erw.sthlp), checked where Stata is not
installed (packages/stata/check_ado.py): its structure, the owner's style, its help, and the address it builds for each
of ten real calls, which must be the Python package's. The checker is shown to catch each kind of fault on a broken
copy. The ten fixtures are the live set's own answers (recorded by packages/stata/fixtures/record.py) and carry no
address or key of the live set. No request, no model call."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATA = ROOT / "packages" / "stata"


def checker():
    spec = importlib.util.spec_from_file_location("check_ado_1003", STATA / "check_ado.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = checker()
ADO = (STATA / "erw.ado").read_text(encoding="utf-8")
HLP = (STATA / "erw.sthlp").read_text(encoding="utf-8")


def problems(ado=ADO, hlp=HLP):
    progs, p = C.programs(ado)
    p += C.check_structure(ado, progs) + C.check_style(progs) + C.check_help(hlp, ado)
    if "_erw_live_url" in progs:
        p += C.check_addresses(progs)[0]
    return p


class TheCommand(unittest.TestCase):
    def test_every_check_passes(self):
        self.assertEqual(problems(), [])

    def test_the_six_subcommands(self):
        for sub in C.SUBCOMMANDS:
            self.assertIn(f'"`sub\'" == "{sub}"', ADO)

    def test_the_ten_addresses_are_the_python_package_s(self):
        progs, _ = C.programs(ADO)
        p, lines = C.check_addresses(progs)
        self.assertEqual(p, [])
        self.assertEqual(len(lines), 10)


class TheCheckerCatches(unittest.TestCase):
    def test_an_empty_line_inside_a_block(self):
        bad = ADO.replace('        local tcol "ts_utc"\n', '        local tcol "ts_utc"\n\n', 1)
        self.assertTrue(any("inside a block" in x for x in problems(bad)))

    def test_two_commands_with_no_empty_line(self):
        bad = ADO.replace("    tempname fh\n\n    file open", "    tempname fh\n    file open", 1)
        self.assertTrue(any("empty lines before" in x for x in problems(bad)))

    def test_a_line_continuation(self):
        bad = ADO.replace("    tempname fh\n", "    tempname ///\n        fh\n", 1)
        self.assertTrue(any("///" in x for x in problems(bad)))

    def test_an_address_that_differs(self):
        bad = ADO.replace('local list "`list\'`sep\'%22`v\'%22"', 'local list "`list\'`sep\'`v\'"', 1)
        self.assertTrue(any(x.startswith("call ") for x in problems(bad)))

    def test_a_missing_help_section(self):
        self.assertTrue(any("examples" in x for x in problems(hlp=HLP.replace("{marker examples}", ""))))

    def test_an_unbalanced_brace(self):
        bad = ADO.replace("    if \"`which'\" == \"coverage\" {", "    if \"`which'\" == \"coverage\" {\n        if 1 {", 1)
        self.assertTrue(any("balance" in x for x in problems(bad)))


class Fixtures(unittest.TestCase):
    def test_ten_real_answers_with_no_address_or_key(self):
        rec = json.loads((STATA / "fixtures" / "calls.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rec["calls"]), 10)
        for c in rec["calls"]:
            self.assertEqual(c["python_rows"], c["csv_rows"], c["file"])
            self.assertTrue(all(a.startswith("<ERW_LIVE_URL>/rest/v1/") for a in c["addresses"]))
            body = (STATA / "fixtures" / c["file"]).read_text(encoding="utf-8")
            self.assertEqual(len(body.splitlines()) - 1, c["csv_rows"])
        for f in (STATA / "fixtures").iterdir():
            text = f.read_text(encoding="utf-8")
            self.assertNotIn("supabase.co", text, f.name)
            self.assertNotRegex(text, r"eyJ[A-Za-z0-9_-]{20,}", f.name)   # no key (a JWT)
        self.assertLessEqual(rec["requests"]["live"], 100)


class Style(unittest.TestCase):
    def test_no_em_dash_and_no_continuation(self):
        for f in STATA.rglob("*"):
            if f.is_file() and f.suffix in (".ado", ".sthlp", ".py", ".md", ".do"):
                text = f.read_text(encoding="utf-8")
                self.assertNotIn(chr(0x2014), text, f.name)
                if f.suffix in (".ado", ".do"):
                    self.assertNotIn("///", text, f.name)


if __name__ == "__main__":
    unittest.main()
