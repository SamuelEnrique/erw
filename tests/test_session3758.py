"""Sessions 3758 and 3759 (chain 211): FERC-714's planning-area forecasts, their revisions, and decision 77.

Held here, with no request and no table: the connector's reshaping of PUDL's rows (every filing kept, a blank no row, a
row given twice refused), the derived revisions (this filing less the one and two before, a percent only over a
positive base), and the validator's key for a table that keeps its revisions (vintage in the key, a blank vintage an
error; without the header line a repeated key is still an error).
"""
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in (("warehouse", "connectors"), ("warehouse", "derived"), ("warehouse", "validate")):
    sys.path.insert(0, os.path.join(ROOT, *sub))
import erw_validate  # noqa: E402
import ferc714_forecast_growth as growth  # noqa: E402
import ferc714_forecasts as fc  # noqa: E402


def pudl(rows):
    return pd.DataFrame(rows, columns=["respondent_id_ferc714", "report_year", "forecast_year", "summer_peak_demand_forecast_mw",
                                       "winter_peak_demand_forecast_mw", "net_demand_forecast_mwh"])


PUDL = pudl([(119, 2023, 2030, 160000.0, 140000.0, 900000000.0), (119, 2024, 2030, 176010.0, 150000.0, None),
             (119, 2025, 2030, 175135.0, 151000.0, 950000000.0), (24, 2025, 2030, 0.0, 30000.0, 1.0)])


class TheForecastsTable(unittest.TestCase):
    def test_every_filing_is_a_row_and_a_blank_is_none(self):
        t = fc.forecasts(PUDL, fc.URL, "2026-11-12T10:30:00Z")
        self.assertEqual(list(t.columns), fc.COLS)
        self.assertEqual(len(t), 11)  # 12 figures, one blank
        pjm = t[(t["entity"] == "ferc714:119") & (t["variable"] == "summer_peak_forecast_mw")]
        self.assertEqual(list(pjm["vintage"]), ["2024-06-01T00:00:00Z", "2025-06-01T00:00:00Z", "2026-06-01T00:00:00Z"])
        self.assertEqual(list(pjm["x_report_year"]), ["2023", "2024", "2025"])
        self.assertEqual(set(t["ts_utc"]), {"2030-01-01T00:00:00Z"})
        self.assertEqual(set(t.loc[t["variable"] == "net_energy_forecast_mwh", "unit"]), {"MWh"})

    def test_a_row_given_twice_stops_the_run(self):
        with self.assertRaises(RuntimeError):
            fc.forecasts(pd.concat([PUDL, PUDL.head(1)]), fc.URL, "x")


class TheRevisions(unittest.TestCase):
    def setUp(self):
        self.t = growth.build(fc.forecasts(PUDL, fc.URL, "x").astype(str), "2026-11-12T10:30:00Z")

    def get(self, ent, var, year):
        r = self.t[(self.t["entity"] == ent) & (self.t["variable"] == var) & (self.t["x_report_year"] == year)]
        return list(r["value"])

    def test_one_and_two_filings_back(self):
        self.assertEqual(self.get("ferc714:119", "summer_peak_revision_1y_mw", "2024"), [16010.0])
        self.assertEqual(self.get("ferc714:119", "summer_peak_revision_1y_mw", "2025"), [-875.0])
        self.assertEqual(self.get("ferc714:119", "summer_peak_revision_2y_mw", "2025"), [15135.0])
        self.assertEqual(self.get("ferc714:119", "summer_peak_revision_1y_pct", "2024"), [10.006])

    def test_a_blank_in_either_filing_is_no_row(self):
        self.assertEqual(self.get("ferc714:119", "net_energy_revision_1y_mwh", "2024"), [])
        self.assertEqual(self.get("ferc714:119", "net_energy_revision_1y_mwh", "2025"), [])
        self.assertEqual(self.get("ferc714:119", "net_energy_revision_2y_mwh", "2025"), [50000000.0])

    def test_an_area_with_one_filing_has_no_revision(self):
        self.assertFalse((self.t["entity"] == "ferc714:24").any())


class DecisionSeventySeven(unittest.TestCase):
    def check(self, header, rows):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ferc714_planning_area_forecasts.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                for h in header:
                    f.write("# " + h + "\n")
                pd.DataFrame(rows).to_csv(f, index=False, lineterminator="\n")
            return erw_validate.validate(path)

    def rows(self, v2="2026-06-01T00:00:00Z"):
        base = dict(entity="ferc714:119", variable="summer_peak_forecast_mw", ts_utc="2030-01-01T00:00:00Z", value=1.0, unit="MW",
                    freq="P1Y", geo="US", market="", node="", source="pudl:x", source_url="https://example.org", retrieved_at="2026-11-12T10:30:00Z")
        return [dict(base, vintage="2025-06-01T00:00:00Z"), dict(base, value=2.0, vintage=v2)]

    HEADER = ["Energy Research Warehouse (ERW): test", "Source: pudl:x test", "Retrieved: 20261112T103000Z (UTC)"]

    def test_a_table_that_keeps_its_revisions_is_keyed_by_vintage(self):
        r = self.check(self.HEADER + [erw_validate.REVISIONS_KEPT + ". Key: entity, variable, ts_utc, vintage."], self.rows())
        self.assertEqual([e for e in r["errors"] if e["check"] in ("duplicate_key", "vintage_required")], [])

    def test_without_the_line_the_repeat_is_an_error(self):
        r = self.check(self.HEADER, self.rows())
        self.assertTrue(any(e["check"] == "duplicate_key" for e in r["errors"]), r["errors"])

    def test_a_blank_vintage_is_refused(self):
        r = self.check(self.HEADER + [erw_validate.REVISIONS_KEPT], self.rows(v2=""))
        self.assertTrue(any(e["check"] == "vintage_required" for e in r["errors"]), r["errors"])


if __name__ == "__main__":
    unittest.main()
