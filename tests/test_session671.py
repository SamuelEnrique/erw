"""Session 671: interconnection request to operation, from Berkeley Lab's Queued Up file (chain 043).

Energy Research Warehouse (ERW). Tests warehouse/derived/interconnection_durations.py on a few requests built here (test
fixtures, not Berkeley Lab's values), the unit month, the sector rule and the holds. No network.

    python -m unittest tests.test_session671 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# the validate folder last on the path: its build_coverage.py is a shim that runs the real one
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
for d in (("warehouse", "derived"), ("warehouse", "metadata"), ("warehouse", "redivis")):
    sys.path.insert(0, os.path.join(ROOT, *d))
import interconnection_durations as D  # noqa: E402
import grid_peak_vs_capacity as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

COLS = ["entity_id", "name", "geo", "lat", "lon", "capacity_mw", "operator", "source_url", "retrieved_at", "vintage", "q_id",
        "q_status", "q_date", "on_date", "region", "state", "county", "utility", "lbnl_entity", "type_clean"]


def q(rows):
    base = dict(name="n", geo="US-TX", lat="", lon="", capacity_mw="100", operator="", source_url="u", retrieved_at="r",
                vintage="v", q_id="1", state="TX", county="c", utility="", lbnl_entity="e", type_clean="Solar")
    return pd.DataFrame([dict(base, **r) for r in rows], columns=COLS)


class Durations(unittest.TestCase):
    def test_counts_only_operational_projects_with_both_dates_in_order(self):
        t, left = D.durations(q([
            dict(entity_id="lbnl:a:1", q_status="operational", q_date="2020-01-01", on_date="2022-01-01", region="ERCOT"),
            dict(entity_id="lbnl:a:2", q_status="operational", q_date="2020-01-01", on_date="", region="ERCOT"),
            dict(entity_id="lbnl:a:3", q_status="operational", q_date="2022-01-01", on_date="2020-01-01", region="ERCOT"),
            dict(entity_id="lbnl:a:4", q_status="withdrawn", q_date="2020-01-01", on_date="2021-01-01", region="ERCOT"),
        ]))
        self.assertEqual(t["entity_id"].tolist(), ["lbnl:a:1"])
        self.assertEqual(t["months_to_operation"].iloc[0], round(731 / 30.4375, 1))
        self.assertEqual(left, {"operational": 3, "without a request or an operation date": 1,
                                "operation date before the request date": 1})
        self.assertEqual(list(t.columns), D.ENTITY_COLS + D.EXTRA)

    def test_summary_by_grid_and_the_us(self):
        t, _ = D.durations(q([
            dict(entity_id=f"lbnl:a:{i}", q_status="operational", q_date="2020-01-01", on_date=f"202{i}-01-01", region=g)
            for i, g in ((1, "ERCOT"), (2, "ERCOT"), (3, "ISO-NE"))]))
        s = D.summary(t)
        self.assertEqual(sorted(s["entity"].unique()), ["lbnl_durations:ercot", "lbnl_durations:isone", "lbnl_durations:us"])
        us23 = s[(s.entity == "lbnl_durations:us") & (s.ts_utc == "2023-01-01T00:00:00Z")].set_index("variable")["value"]
        self.assertEqual(us23["projects"], 1.0)
        self.assertEqual(us23["projects_5y"], 3.0)
        self.assertTrue(set(s["unit"]) <= V.UNITS)
        self.assertEqual(list(s.columns), D.ip.SERIES_COLS)

    def test_month_is_a_unit(self):
        self.assertIn("month", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as h:
            self.assertIn("49. **Session 671: month.**", h.read())

    def test_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        for t in ("interconnection_durations", "interconnection_durations_summary"):
            self.assertEqual(B.sector_of(t), "power")
            self.assertIn(f"  - {t}\n", y[y.index("catalogue_hold:"):])
            self.assertIn(f"upload.py {t}", R.STORAGE_HELD[t])

    def test_no_em_dash(self):
        for f in ("tests/test_session671.py", "warehouse/derived/interconnection_durations.py",
                  "docs/methods/interconnection_durations.md",
                  "warehouse/derived/grid_peak_vs_capacity.py", "docs/methods/grid_peak_vs_capacity.md"):
            with open(os.path.join(ROOT, f), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read())


class PeakVsCapacity(unittest.TestCase):
    """Session 672's second half: the grid's own generators by balancing authority, no state mapped."""

    def test_capacity_by_balancing_authority_and_split_states(self):
        peaks = pd.DataFrame([dict(entity=f"eia930:{ba}", variable="peak_demand_mw", ts_utc="2025-01-01T00:00:00Z",
                                   value="100", retrieved_at="r", x_at="2025-07-01T21:00:00Z") for ba in G.GRIDS.values()])
        gens = pd.DataFrame([dict(state="TX", balancing_authority="ERCO", net_summer_mw="150", operating_year="2020",
                                  energy_source="NG", vintage="2026-08"),
                             dict(state="TX", balancing_authority="ERCO", net_summer_mw="50", operating_year="2026",
                                  energy_source="SUN", vintage="2026-08"),
                             dict(state="TX", balancing_authority="SWPP", net_summer_mw="20", operating_year="2010",
                                  energy_source="WND", vintage="2026-08")]
                            + [dict(state="NY", balancing_authority=ba, net_summer_mw="10", operating_year="2000",
                                    energy_source="NG", vintage="2026-08") for ba in ("CISO", "ISNE", "MISO", "NYIS", "PJM")])
        t = G.build(peaks, gens, "u")
        e = t[t.entity == "grid_peak_vs_capacity:ercot"].set_index("variable")
        self.assertEqual(e.loc["capacity_mw", "value"], 150.0)          # the 2026 generator is not online by 2025
        self.assertEqual(e.loc["capacity_mw_listed", "value"], 200.0)
        self.assertEqual(e.loc["peak_to_capacity", "value"], round(100 / 150, 4))
        self.assertEqual(e.loc["peak_demand_mw", "x_at"], "2025-07-01T21:00:00Z")
        self.assertEqual(e["x_split_states"].iloc[0], "TX")             # 20 of Texas's 220 MW is SPP's
        self.assertEqual(list(t.columns), G.COLS)
        self.assertTrue(set(t["unit"]) <= V.UNITS)
        self.assertEqual(B.sector_of("grid_peak_vs_capacity"), "power;capacity")
        with self.assertRaises(RuntimeError):  # a grid with no capacity listed stops the run
            G.build(peaks, gens[gens.balancing_authority != "PJM"], "u")
        self.assertIn("upload.py grid_peak_vs_capacity", R.STORAGE_HELD["grid_peak_vs_capacity"])


if __name__ == "__main__":
    unittest.main()
