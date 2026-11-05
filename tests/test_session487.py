"""Session 487: the NLR (NREL) Electricity ATB's projected costs. The ATB's default view only (the R&D case, a 30-year
cost recovery period); the newest year and version in the bucket; units from the standard's vocabulary; a repeated key
stops the run; values as the ATB gives them."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import nlr_atb_costs as na  # noqa: E402


def atb(*rows):
    cols = ["core_metric_parameter", "core_metric_case", "crpyears", "technology", "techdetail", "techdetail2", "resourcedetail",
            "scale", "scenario", "display_name", "default", "maturity", "core_metric_variable", "value"]
    return pd.DataFrame([dict(zip(cols, r)) for r in rows])


BATT = ["Utility-Scale Battery Storage", "4Hr Battery Storage", "Lithium Ion 4 hr", "Lithium Ion 4 hr", "Utility", "Moderate",
        "Utility-Scale Battery Storage - 4Hr", 1, "Y", 2025]


def row(param, case, crp, value, year=2025):
    return [param, case, crp] + BATT[:-1] + [year, value]


class Rows(unittest.TestCase):
    def test_the_default_view_only(self):
        d = atb(row("CAPEX", "R&D", 30, 1396.7), row("CAPEX", "R&D", 20, 1396.7), row("CAPEX", "R&D + TC", 30, 1000.0),
                row("CFC", "R&D", 30, 5.0), row("Fixed O&M", "R&D", 30, 49.87))
        s = na.rows(d, 2025, "u", "r", "v1.0.0", "2026-08-27T00:00:00Z")
        self.assertEqual(sorted(zip(s["variable"], s["value"])), [("capex", 1396.7), ("fixed_om", 49.87)])
        self.assertEqual(set(s["entity"]), {"nlr_atb_2025:utility_scale_battery_storage:4hr_battery_storage:lithium_ion_4_hr:utility:moderate"})
        self.assertEqual(dict(zip(s["variable"], s["unit"])), {"capex": "USD/kW", "fixed_om": "USD/kW-year"})
        self.assertEqual(set(s["x_dollar_year"]), {"2023"})
        self.assertEqual(set(s["ts_utc"]), {"2025-01-01T00:00:00Z"})

    def test_every_unit_is_in_the_standards_vocabulary(self):
        self.assertTrue({u for _, u in na.PARAMS.values()} <= {"USD/kW", "USD/kW-year", "USD/MWh", "ratio"})

    def test_a_repeated_key_stops_the_run(self):
        with self.assertRaisesRegex(RuntimeError, "given twice"):
            na.rows(atb(row("CAPEX", "R&D", 30, 1.0), row("CAPEX", "R&D", 30, 2.0)), 2025, "u", "r", "v")

    def test_the_newest_year_and_version(self):
        xml = ("<Key>ATB/electricity/parquet/2024/v4.0.0/ATBe.parquet</Key><Key>ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet</Key>"
               "<Key>ATB/electricity/parquet/2024/v10.0.0/ATBe.parquet</Key>")
        self.assertEqual(na.newest_key(xml), ("ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet", 2025, "v1.0.0"))


if __name__ == "__main__":
    unittest.main()
