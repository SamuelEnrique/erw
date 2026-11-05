"""Session 2427: Eurostat's monthly crude oil imports by field of production, the EU (nrg_ti_coifpm, EU_V).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eurostat_crude_by_field.py on a JSON-stat answer built here
in Eurostat's form (figures made up for the test, not Eurostat's): the sparse values placed on their dimensions, thousand
USD written as USD, a volume of 0 kept and a price or grade of 0 left out and counted, a flag carried; a geo or an
indicator not expected, a company count for the EU and a value not a number stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2427 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import eurostat_crude_by_field as E  # noqa: E402
import build_coverage as B  # noqa: E402

INDIC = ["CMPY_NR", "API_DEG", "SULPH_PC", "VOL_THS_BBL", "VAL_THS_USD", "AVGPRC_USD_BBL"]


def answer(values, status=None, geo="EU_V", indic=None):
    def cat(codes, labels=None):
        c = {"index": {k: i for i, k in enumerate(codes)}}
        if labels:
            c["label"] = labels
        return {"category": c}
    ind = indic or INDIC
    return {"version": "2.0", "id": ["freq", "crudeoil", "indic_nrg", "geo", "time"], "size": [1, 2, len(ind), 1, 2],
            "dimension": {"freq": cat(["M"]), "crudeoil": cat(["TOTAL", "US_TXA_WTI"], {"TOTAL": "Total", "US_TXA_WTI": "United States Texas - West Texas Intermediate (WTI)"}),
                          "indic_nrg": cat(ind), "geo": cat([geo]), "time": cat(["2026-08", "2026-09"])},
            "value": values, "status": status or {}}


def at(crude, indic, time):
    # index = (crude * 6 + indic) * 2 + time
    return str((crude * 6 + INDIC.index(indic)) * 2 + time)


class Build(unittest.TestCase):
    def test_rows(self):
        vals = {at(1, "VOL_THS_BBL", 0): 36538.901, at(1, "VAL_THS_USD", 0): 3447.5, at(1, "AVGPRC_USD_BBL", 0): 94.356,
                at(1, "API_DEG", 0): 42.861, at(1, "VOL_THS_BBL", 1): 0, at(1, "AVGPRC_USD_BBL", 1): 0, at(1, "API_DEG", 1): 0}
        t, zeros = E.build(answer(vals, {at(1, "API_DEG", 0): "b"}), "2026-10-24T11:31:26Z")
        got = {(r.entity, r.variable, r.ts_utc): r for r in t.itertuples()}
        w = "eurostat_crude_field:EU:US_TXA_WTI"
        self.assertEqual((got[(w, "volume", "2026-08-01T00:00:00Z")].value, got[(w, "volume", "2026-08-01T00:00:00Z")].unit), (36538.901, "kbbl"))
        self.assertEqual(got[(w, "value", "2026-08-01T00:00:00Z")].value, 3447500.0)
        self.assertEqual((got[(w, "price", "2026-08-01T00:00:00Z")].unit, got[(w, "api_gravity", "2026-08-01T00:00:00Z")].x_flag), ("USD/bbl", "b"))
        self.assertEqual(got[(w, "volume", "2026-09-01T00:00:00Z")].value, 0.0)
        self.assertNotIn((w, "price", "2026-09-01T00:00:00Z"), got)
        self.assertEqual(zeros, {"price": 1, "api_gravity": 1})
        self.assertEqual(got[(w, "volume", "2026-08-01T00:00:00Z")].geo, "")

    def test_stops(self):
        for kw in ({"geo": "DE"}, {"indic": INDIC[:5] + ["NEW_IND"]}):
            with self.assertRaises(RuntimeError):
                E.build(answer({"2": 1.0}, **kw), "")
        with self.assertRaises(RuntimeError):
            E.build(answer({at(0, "CMPY_NR", 0): 3}), "")
        with self.assertRaises(RuntimeError):
            E.build(answer({at(0, "VOL_THS_BBL", 0): "x"}), "")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(E.NAME), "oil")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {E.NAME}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "warehouse", "redivis", "release_v1.py"), encoding="utf-8") as f:
            self.assertIn(f'"{E.NAME}",', f.read())


if __name__ == "__main__":
    unittest.main()
