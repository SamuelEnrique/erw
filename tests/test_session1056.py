"""Session 1056 (chain 072): the package's errors read by a stranger. Two failures answered with a sentence that did not
say what to do: a start or end that is not a date (pandas' own "month must be in 1..12") and a start after the end (an
empty window, a warning). Both now stop the call before any request, with one sentence in the three packages. And a
table of the record that the live set does not hold, asked of the live set, was "No ERW table named ..." in Python and
an empty frame in Stata and R: now one sentence that says where it is. No request, no model call."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))

import erw  # noqa: E402
from erw import errors  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def fragments(t):
    return [f for f in re.split(r"\{[a-z_]+\}", t) if len(f.strip()) >= 8]


class TheWindow(unittest.TestCase):
    def setUp(self):
        erw.requests(reset=True)

    def test_a_date_that_cannot_be_read(self):
        with self.assertRaises(erw.ERWBadWindow) as e:
            erw.fetch("eia_fuel_spot_prices", start="2026-13-45", backend="live")
        self.assertEqual(str(e.exception), "The start 2026-13-45 is not a date the ERW reads: write it as YYYY-MM-DD, or "
                                           "YYYY-MM-DDTHH:MM:SSZ in UTC, then try again.")
        with self.assertRaises(erw.ERWBadWindow) as e:
            erw.fetch("eia_fuel_spot_prices", end="last week", backend="live")
        self.assertTrue(str(e.exception).startswith("The end last week is not a date"))

    def test_a_start_not_before_the_end(self):
        for s, t in (("2026-10-01", "2026-09-01"), ("2026-10-01", "2026-10-01")):
            with self.assertRaises(erw.ERWBadWindow) as e:
                erw.fetch("eia_fuel_spot_prices", start=s, end=t, backend="live")
            self.assertEqual(str(e.exception), f"The start {s} is not before the end {t}, so the window [start, end) holds no "
                                               "time: give a start before the end, then try again.")
        self.assertEqual(erw.requests()["live"], 0)                     # said before any request

    def test_a_table_the_live_set_does_not_hold(self):
        from erw import licenses
        t = next(k for k, v in sorted(licenses.rows().items()) if v.get("live_window") == "none" and v.get("verdict") == "public")
        old = {k: os.environ.get(k) for k in ("ERW_LIVE_URL", "ERW_LIVE_KEY")}
        os.environ["ERW_LIVE_URL"], os.environ["ERW_LIVE_KEY"] = "https://example.invalid", "not-a-key"
        try:
            with self.assertRaises(erw.ERWDataNotFound) as e:
                erw.fetch(t, backend="live")
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.assertEqual(str(e.exception), f"{t} is not in the live set: erw.tables() says which tables are (in_live); read "
                                           "it from the Stanford dataset or a clone's tables instead.")
        self.assertEqual(erw.requests()["live"], 0)

    def test_a_bad_window_is_a_value_error(self):
        self.assertTrue(issubclass(erw.ERWBadWindow, ValueError))


class OneWording(unittest.TestCase):
    def test_the_three_packages_and_the_conformance_file(self):
        conf = json.loads(src("packages", "conformance", "conformance.json"))["errors"]["templates"]
        ado, r = src("packages", "stata", "erw.ado"), src("packages", "r", "erw", "R", "erw.R")
        for kind in ("bad_date", "bad_window", "not_live"):
            self.assertEqual(conf[kind], errors.WORDS[kind])
            for f in fragments(errors.WORDS[kind].replace("{tables_call}", "|TC|")):
                for part in f.split("|TC|"):
                    if len(part.strip()) >= 8:
                        self.assertIn(part, ado, (kind, part))
                        self.assertIn(part, r, (kind, part))

    def test_stata_checks_before_its_first_read(self):
        ado = src("packages", "stata", "erw.ado")
        i = ado.index("program define _erw_fetch")
        body = ado[i:ado.index("\nend\n", i)]
        self.assertLess(body.index("is not a date the ERW reads"), body.index("_erw_record licenses"))
        self.assertNotIn("///", body)

    def test_r_checks_before_its_first_read(self):
        r = src("packages", "r", "erw", "R", "erw.R")
        i = r.index("erw_fetch <- function")
        body = r[i:r.index("\n}\n", i)]
        self.assertLess(body.index("is not a date the ERW reads"), body.index(".erw_shape(table)"))


if __name__ == "__main__":
    unittest.main()
