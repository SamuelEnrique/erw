"""Session 8001 (chain 501, steps B3 to B7): the energy-source rule of warehouse/connectors/eia930_region_fuel_hourly.py
and the rules of warehouse/derived/regions_pages.py (a region's demand, the trade signs, the event baseline), on small
frames written here, and the contract's keys on the files where the data machine has written them.

Energy Research Warehouse (ERW). docs/methods/eia930_region_fuel_hourly.md, docs/methods/regions_pages.md,
docs/state/page_files_regions.md.

    python -m unittest tests.test_session8001_regions_pages -v
"""

import json
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import eia930_region_fuel_hourly as fuel  # noqa: E402
import regions_pages as rp  # noqa: E402

SITE = os.path.join(ROOT, "site", "data", "regions")


class Sources(unittest.TestCase):
    def test_columns_map_to_the_eight(self):
        self.assertEqual(fuel.source_of("Net Generation (MW) from Coal")[:2], ("coal", False))
        self.assertEqual(fuel.source_of("Net Generation (MW) from Natural Gas (Adjusted)")[:2], ("natural_gas", True))
        self.assertEqual(fuel.source_of("Net Generation (MW) from Pumped Storage  (Adjusted)")[:2], ("hydro", True))
        # EIA's misprint in the file of July to December 2024
        self.assertEqual(fuel.source_of("Net Generation (MW) from Solar witho Integrated Battery Storage (Adjusted)")[:2], ("solar", True))
        self.assertEqual(fuel.source_of("Net Generation (MW) from Battery Storage")[:2], ("storage", False))
        self.assertEqual(fuel.source_of("Net Generation (MW) from Geothermal")[:2], ("other", False))
        self.assertIsNone(fuel.source_of("Net Generation (MW) from Coal (Imputed)"))
        self.assertIsNone(fuel.source_of("Net Generation (MW)"))


def frame(rows, storage_cols=False):
    d = pd.DataFrame(rows)
    for s in fuel.SOURCES:
        if s not in d:
            d[s] = np.nan
    d["ts"] = pd.to_datetime(d["ts"], utc=True)
    d["has_storage_cols"] = storage_cols
    return d


class RegionRule(unittest.TestCase):
    def test_an_hour_needs_every_authority_held(self):
        d = frame([
            dict(ba="A", region="TEN", ts="2025-07-01T10:00Z", ng=100.0, coal=60.0, natural_gas=40.0),
            dict(ba="B", region="TEN", ts="2025-07-01T10:00Z", ng=50.0, wind=50.0),
            dict(ba="A", region="TEN", ts="2025-07-01T11:00Z", ng=100.0, coal=60.0, natural_gas=20.0),   # 80 of 100: not held
            dict(ba="B", region="TEN", ts="2025-07-01T11:00Z", ng=50.0, wind=50.0),
        ])
        rows, short = fuel.region_rows(d, "t", None, None)
        self.assertEqual(short, 1)
        self.assertEqual(set(rows["ts"]), {pd.Timestamp("2025-07-01T10:00Z")})
        got = dict(zip(rows["variable"], rows["value"]))
        self.assertEqual(got["net_generation_coal_mw"], 60.0)
        self.assertEqual(got["net_generation_wind_mw"], 50.0)
        self.assertEqual(got["net_generation_solar_mw"], 0.0)       # held hour, source printed by no one: zero
        self.assertNotIn("net_generation_storage_mw", got)          # no storage columns before July 2024: not written
        self.assertEqual(set(rows["x_bas"]), {2})

    def test_storage_written_when_the_file_has_its_columns(self):
        d = frame([dict(ba="A", region="TEX", ts="2025-07-01T20:00Z", ng=100.0, solar=110.0, storage=-10.0)], storage_cols=True)
        rows, _ = fuel.region_rows(d, "t", None, None)
        got = dict(zip(rows["variable"], rows["value"]))
        self.assertEqual(got["net_generation_storage_mw"], -10.0)

    def test_small_authority_within_one_mw(self):
        d = frame([dict(ba="A", region="NW", ts="2025-07-01T20:00Z", ng=2.0, wind=1.2)])
        rows, short = fuel.region_rows(d, "t", None, None)
        self.assertEqual(short, 0)
        self.assertTrue(len(rows))


def ref_of(**kw):
    out = {}
    for code, (region, gen_only, activated, retired) in kw.items():
        out[code] = dict(code=code, name=code, tz="America/Chicago", region=region, generation_only=gen_only, us=True,
                         active=retired is None, activated=activated, retired=retired)
    return out


class RegionDemand(unittest.TestCase):
    def test_generation_only_is_not_waited_for_and_a_retired_one_stops(self):
        ref = ref_of(A=("SE", False, None, None), B=("SE", False, None, "2025-07-01"), G=("SE", True, None, None))
        ts = pd.date_range("2025-07-01T03:00Z", periods=8, freq="h")
        rows = []
        for i, t in enumerate(ts):
            rows.append(dict(entity="eia930:A", variable="demand_mw", ts=t, value=100.0 + i))
            if t < pd.Timestamp("2025-07-01", tz="America/Chicago"):
                rows.append(dict(entity="eia930:B", variable="demand_mw", ts=t, value=10.0))
        dem = pd.DataFrame(rows)
        total, summed = rp.region_demand("SE", ref, dem)
        self.assertEqual(summed, ["A", "B"])
        self.assertEqual(float(total.iloc[0]), 110.0)                  # both, before B's retirement
        self.assertEqual(float(total.iloc[-1]), 107.0)                 # A alone after it
        self.assertTrue(total.notna().all())

    def test_a_missing_active_authority_leaves_the_hour_out(self):
        ref = ref_of(A=("SE", False, None, None), B=("SE", False, None, None))
        ts = pd.date_range("2025-06-30T03:00Z", periods=3, freq="h")
        dem = pd.DataFrame([dict(entity="eia930:A", variable="demand_mw", ts=t, value=1.0) for t in ts]
                           + [dict(entity="eia930:B", variable="demand_mw", ts=ts[0], value=1.0)])
        total, _ = rp.region_demand("SE", ref, dem)
        self.assertEqual(float(total.iloc[0]), 2.0)
        self.assertTrue(np.isnan(total.iloc[1]))


class TradeSigns(unittest.TestCase):
    def test_each_side_reads_its_own_imports(self):
        # pair CAR-SE: the first report is CAR's, power from CAR to SE; the second is SE's, turned to the same direction
        ts = pd.date_range("2025-08-01T04:00Z", periods=2, freq="h")
        pairs = pd.DataFrame({"entity": "eia930:CAR-SE", "ts": ts, "value": [-700.0, -690.0],
                              "x_first_report": [-700.0, -690.0], "x_second_report": [-710.0, np.nan]})
        docs = rp.trade_docs(pairs, {})
        car, se = docs["CAR"]["neighbors"]["SE"], docs["SE"]["neighbors"]["CAR"]
        self.assertEqual(car["net_imports_mwh"], [1390.0])     # CAR imports from SE by its own report
        self.assertEqual(car["their_report_mwh"], [710.0])
        self.assertEqual(car["gap_mwh"], [-10.0])              # 700 less 710, the one hour both held
        self.assertEqual(car["hours_both"], [1])
        self.assertEqual(se["net_imports_mwh"], [-710.0])      # SE exports to CAR by its own report
        self.assertEqual(se["their_report_mwh"], [-1390.0])


class EventBaseline(unittest.TestCase):
    def test_the_mean_of_the_offsets_that_hold_the_hour(self):
        e = dict(event="x", title="x", start="2025-01-20", end="2025-01-20", baseline="b", years_back=None, offsets=[364, 728])
        idx = pd.date_range("2022-01-01T00:00Z", "2025-02-01T00:00Z", freq="h")
        s = pd.Series(np.nan, index=idx)
        hours = pd.date_range(pd.Timestamp("2025-01-20", tz="America/New_York").tz_convert("UTC"), periods=3, freq="h")
        s[hours] = 500.0
        s[hours - pd.Timedelta(days=364)] = 100.0
        s[hours[0] - pd.Timedelta(days=728)] = 300.0
        keys = {"demand_mw": s, "net_generation_mw": s, "net_imports_mw": s, "gen": {k: s for k in rp.SOURCES}}
        doc = rp.event_doc(e, {"TEN": keys}, {"CAR-SE": s})
        r = doc["regions"]["TEN"]
        self.assertEqual(r["demand_mw"][:3], [500, 500, 500])
        self.assertEqual(r["baseline"]["demand_mw"][:3], [200, 100, 100])
        self.assertEqual(doc["pairs"]["CAR-SE"]["baseline_mw"][0], 200)
        # Eastern midnight of the first day to Pacific midnight after the last: 24 + 3 hours
        self.assertEqual(doc["hours"]["n"], 27)


@unittest.skipUnless(os.path.exists(os.path.join(SITE, "index.json")), "the page files are written on the data machine")
class Contract(unittest.TestCase):
    def test_index(self):
        d = json.load(open(os.path.join(SITE, "index.json"), encoding="utf-8"))
        self.assertEqual([r["code"] for r in d["regions"]], rp.REGIONS)
        tva = [b for b in d["bas"] if b["code"] == "TVA"][0]
        self.assertEqual(set(tva), {"code", "name", "region", "tz", "grid", "region_grids", "generation_only", "active",
                                    "retired", "first_hour", "last_hour", "files", "us", "files_eia930"})

    def test_texas_mix_equals_ercots(self):
        a = json.load(open(os.path.join(SITE, "mix", "tex.json"), encoding="utf-8"))
        b = json.load(open(os.path.join(ROOT, "site", "data", "mix", "ercot.json"), encoding="utf-8"))
        for m in ("2019-03", "2024-01", "2025-08"):
            for s in ("natural_gas", "coal", "nuclear", "wind", "solar"):
                self.assertAlmostEqual(a["months"][m][f"{s}_share_pct"], b["months"][m][f"{s}_share_pct"], places=2, msg=(m, s))

    def test_every_region_has_its_files(self):
        for r in rp.REGIONS:
            for part in ("demand", "mix", "trade"):
                self.assertTrue(os.path.exists(os.path.join(SITE, part, f"{r.lower()}.json")), (part, r))


if __name__ == "__main__":
    unittest.main()
