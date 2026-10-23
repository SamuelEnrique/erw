"""Session 1017 (chain 070): the researcher's path. The walk (docs/reviews/packages-path.md) found that the Stata and R
packages lacked the partition options the specification gives them (market, ba, year); both now take them, and the
address of a partitioned call is the Python package's in all three. No request, no model call."""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))

from erw import live  # noqa: E402


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


CALL = {"table": "ercot_all_hub_prices_history", "entity": ["HB_HUBAVG"], "start": "2025-01-01", "end": "2026-01-01",
        "market": "ercot_dam", "year": 2025}


class Partitions(unittest.TestCase):
    def python(self):
        f = live.series_filters(["HB_HUBAVG"], None, "2025-01-01", "2026-01-01") + [("market", "eq.ercot_dam"), ("year", "eq.2025")]
        return live.live_url("<ERW_LIVE_URL>", "series", live.page_params("series", f, 0, table_name=CALL["table"]))

    def test_stata_s_address_is_python_s(self):
        S = load("check_ado_1017", "packages", "stata", "check_ado.py")
        progs, _ = S.programs(src("packages", "stata", "erw.ado"))
        self.assertEqual(S.stata_url(progs["_erw_live_url"], CALL, "series"), self.python())
        self.assertIn("MARKet(string) BA(string) YEAR(string) BACKend(string) CLEAR]", src("packages", "stata", "erw.ado"))

    def test_r_s_address_is_python_s(self):
        R = load("check_r_1017", "packages", "r", "check_r.py")
        self.assertEqual(R.r_url(src("packages", "r", "erw", "R", "erw.R"), CALL, "series"), self.python())
        self.assertIn('backend = "auto",\n                      market = NULL, ba = NULL, year = NULL)', src("packages", "r", "erw", "R", "erw.R"))

    def test_the_walk_is_written(self):
        doc = src("docs", "reviews", "packages-path.md")
        self.assertIn("erw fetch ercot_all_hub_prices_history, market(ercot_dam) year(2025) clear", doc)
        self.assertNotIn(chr(0x2014), doc)


if __name__ == "__main__":
    unittest.main()
