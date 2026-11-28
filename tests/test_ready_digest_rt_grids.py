"""wip/ready-digest-rt-grids (session 11406, chain 770, part C): the other choice of the Digest audit of 26 November,
finding 5 (docs/reviews/digest-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the Digest's "Highest real-time price, yesterday" names the highest interval among the rows held when the issue
was written and says nothing of a grid whose table held no row of the day (4 of the 9 issues with the line: 9, 13, 20
and 23 October). On this branch the line adds "No row of the day yet: <grids>." Measured: those 4 issues' lines would
have named ERCOT and SPP (9 October), SPP (13 October), CAISO and SPP (20 October), ERCOT (23 October); the stored
issues are untouched. The audit's writer test (tests/test_audit_digest_5.py on wip/audit-digest-5) is carried, turned
round: brief.numbers_today on stand-in tables, no warehouse, no network, no model."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))


class TheWriterNamesTheMissingGrids(unittest.TestCase):
    def test_two_grids_with_no_row_are_named(self):
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
        print(line)
        self.assertIn("74.63 USD/MWh at TH_NP15_GEN-APND (CAISO)", line)
        self.assertIn("No row of the day yet: ERCOT, SPP.", line)

    def test_the_code(self):
        with open(os.path.join(ROOT, "warehouse", "news", "brief.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('empty_words = (" No row of the day yet: "', s)


if __name__ == "__main__":
    unittest.main()
