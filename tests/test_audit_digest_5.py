"""Audit of the Digest and the Roundup, finding 5 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): "Highest
real-time price, yesterday" is the highest interval among the rows the warehouse held when the issue was written, and the
line names no grid whose table held no row of the day. It names only the grids held for licence ("Not read: ..."). In
the ten newest Digests, by the retrieval times of the main checkout's rows (r1b_rt_when.out):

  9 October: N.Y.C. (NYISO) 726.09 printed; no ERCOT or SPP row of 8 October was held at 15:34 UTC (SPP's 1,027.12 at
    SPPNORTH_HUB came the next day);
  13 October: LONGIL (NYISO) 129.57; SPP no row of the day;  20 October: N.Y.C. 192.89, written 06:55 UTC, no SPP row
    and no CAISO row yet;  23 October: LONGIL 129.51; no ERCOT row (retrieved 25 October);
  6 November: "no real-time table covers yesterday", the true case said.

1. The stored issues: each line names a highest price and says nothing of the grids missing that day. Passes on main.
2. brief.numbers_today on stand-in tables (no warehouse, no network): three grids' tables are read, two hold no row of
   the day, and the line names neither. Passes on main. Saying which grids had no row changes what an issue says, so it
   is for Samuel's ruling."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))


def rt_line(date):
    with open(os.path.join(ROOT, "docs", "digest", f"{date}.md"), encoding="utf-8") as f:
        return next(l for l in f.read().split("\n") if l.startswith("**Highest real-time price"))


class TheStoredLinesNameNoMissingGrid(unittest.TestCase):
    def test_each_line_names_a_highest_and_no_missing_grid(self):
        for date, iso, missing in (("2026-10-09", "NYISO", ("ERCOT", "SPP")), ("2026-10-13", "NYISO", ("SPP",)),
                                   ("2026-10-20", "NYISO", ("SPP", "CAISO")), ("2026-10-23", "NYISO", ("ERCOT",))):
            line = rt_line(date)
            self.assertIn(f"({iso})", line, date)
            for g in missing:
                self.assertNotIn(g, line, date)
            self.assertIsNone(re.search(r"no row|not covered|no interval|missing", line), date)


class TheWriterNamesNoMissingGrid(unittest.TestCase):
    def test_two_grids_with_no_row_are_not_named(self):
        try:
            import brief  # noqa: E402
            import pandas as pd
        except ImportError as exc:
            raise unittest.SkipTest(f"brief does not import here: {exc}")

        class Tables:
            def coverage(self):
                return pd.DataFrame({"table": ["iso_rtm_hub_prices"], "market": ["caiso_rtm;ercot_rtm;spp_rtm"]})

            def filter(self, market=None):
                return ["iso_rtm_hub_prices"]

            def fetch(self, table, start=None, end=None, market=None, **kw):
                cols = ["entity", "variable", "ts_utc", "value", "unit", "freq", "node"]
                if table == "iso_rtm_hub_prices" and market == "caiso_rtm":
                    return pd.DataFrame([{"entity": "caiso:TH_NP15_GEN-APND", "variable": "lmp_rtm_15m_mean",
                                          "ts_utc": start + pd.Timedelta(hours=17, minutes=45), "value": 74.63, "unit": "USD/MWh",
                                          "freq": "PT15M", "node": "TH_NP15_GEN-APND"}])
                return pd.DataFrame(columns=cols)

        saved = (brief.erw, brief.held_grids, brief.held_rt)
        brief.erw, brief.held_grids, brief.held_rt = Tables(), (lambda *a, **k: set()), (lambda parts, *a, **k: set())
        try:
            lines = brief.numbers_today("2026-10-09", lambda m: None)
        finally:
            brief.erw, brief.held_grids, brief.held_rt = saved
        line = next(l for l in lines if l.startswith("**Highest real-time price"))
        self.assertIn("74.63 USD/MWh at TH_NP15_GEN-APND (CAISO)", line)
        for g in ("ERCOT", "SPP"):
            self.assertNotIn(g, line)
        tables = next(l for l in lines if l.startswith("Tables: "))
        self.assertIn("real-time tables read: iso_rtm_hub_prices", tables)


if __name__ == "__main__":
    unittest.main()
