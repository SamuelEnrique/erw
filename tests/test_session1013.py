"""Session 1013 (chain 070): the package's errors, in words. One sentence a failure, that says what to do: no
network, a table not found, a held table, an empty window, a Redivis token missing, the live set's keys missing, a row
limit the live set passed. The Python package says them (erw.errors), and the Stata command and the R package say the
same (each sentence's fixed words are in their source); packages/conformance/conformance.json holds them. Each failure
is made here, offline. No request, no model call."""
import json
import os
import re
import sys
import unittest
import warnings

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))

import erw  # noqa: E402
from erw import errors, live  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def fragments(template, tables_call):
    """The template's fixed words, at least eight characters, with the language's call put in."""
    t = template.replace("{tables_call}", tables_call)
    return [f for f in re.split(r"\{[a-z_]+\}", t) if len(f.strip()) >= 8]


class OneWording(unittest.TestCase):
    def test_the_conformance_file_holds_them(self):
        conf = json.loads(src("packages", "conformance", "conformance.json"))["errors"]
        self.assertEqual(conf["templates"], errors.WORDS)

    def test_stata_and_r_say_the_same(self):
        ado, r = src("packages", "stata", "erw.ado"), src("packages", "r", "erw", "R", "erw.R")
        for kind in ("not_found", "held", "empty_window", "redivis_token", "live_keys", "row_limit", "no_network"):
            for f in fragments(errors.WORDS[kind], "erw tables"):
                self.assertIn(f, ado, (kind, f))
            for f in fragments(errors.WORDS[kind], "erw_tables()"):
                self.assertIn(f, r, (kind, f))


class EachFailure(unittest.TestCase):
    def setUp(self):
        erw.set_backend(OUT)

    def tearDown(self):
        erw.set_backend()

    def test_a_table_not_found(self):
        with self.assertRaises(erw.ERWDataNotFound) as e:
            erw.fetch("energy_deal")
        self.assertEqual(str(e.exception), "No ERW table named energy_deal. erw.tables() lists every table; with a close "
                                           "name: energy_deals, energy_deals_evidence.")

    def test_a_held_table(self):
        class Served(erw.LocalBackend):
            name = "live"
        erw.set_backend(Served(OUT))
        with self.assertRaises(erw.ERWLicenseHeld) as e:
            erw.fetch("energy_deals")
        lic = erw.license("energy_deals")
        self.assertEqual(str(e.exception), errors.say("held", table="energy_deals", verdict=lic["verdict"],
                                                        words=lic["words"], url=erw.licenses.LICENSES_URL))

    def test_an_empty_window(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df = erw.fetch("energy_deals", start="1900-01-01", end="1900-02-01")
        self.assertTrue(df.empty)
        said = [str(x.message) for x in w if x.category.__name__ == "ERWEmptyWindow"]
        self.assertEqual(len(said), 1)
        self.assertTrue(said[0].startswith("No rows of energy_deals start in [1900-01-01T00:00:00Z, 1900-02-01T00:00:00Z); "
                                           "its rows run from "))

    def test_no_network(self):
        with self.assertRaises(ConnectionError) as e:
            live.LiveBackend(url="http://127.0.0.1:9", key="x")._get("catalogue", [("select", "*")])
        self.assertTrue(str(e.exception).startswith("The ERW's live set could not be reached ("))
        self.assertTrue(str(e.exception).endswith("Check the network connection, then try again."))

    def test_the_keys_missing(self):
        self.assertEqual(errors.missing_key("REDIVIS_API_TOKEN"), errors.WORDS["redivis_token"])
        self.assertEqual(errors.missing_key("ERW_LIVE_KEY"), errors.WORDS["live_keys"])

    def test_a_row_limit_passed(self):
        b = live.LiveBackend(url="http://127.0.0.1:9", key="x")
        b._get = lambda table, params: [{}] * (live.PAGE + 1)
        with self.assertRaises(RuntimeError) as e:
            b._select("series", table_name="t")
        self.assertEqual(str(e.exception), errors.say("row_limit", got=live.PAGE + 1, page=live.PAGE))


if __name__ == "__main__":
    unittest.main()
