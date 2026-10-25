"""Session 2357: MakStat's electricity in MWh by months, North Macedonia (in Pakistan's place).

Energy Research Warehouse (ERW). Tests warehouse/connectors/makstat_macedonia.py on metadata and a JSON-stat answer built
here in MakStat's form (figures made up for the test, not MakStat's): the query built from the metadata, the three ways
MakStat writes a month, an empty cell no row, a plant total off its plants named; a list of indicators not the 21 expected,
a month in another form and an answer not the size of its dimensions each stopping the run; the sector rule and the hold.
No network.

    python -m unittest tests.test_session2357 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import makstat_macedonia as M  # noqa: E402
import build_coverage as B  # noqa: E402

CYR_M = chr(0x041C)
MONTHS = ["2019M08", "2019_09", f"2026{CYR_M}01"]


def meta(months=MONTHS, labels=None):
    labels = labels or [("..") + l if 4 <= i <= 9 or 11 <= i <= 16 else l for i, l in enumerate(M.LABELS)]
    return {"variables": [{"code": "IND", "values": [str(i) for i in range(len(labels))], "valueTexts": labels},
                          {"code": "TIME", "values": [str(i) for i in range(len(months))], "valueTexts": months}]}


def answer(values):
    return {"id": ["IND", "TIME"], "size": [21, 3],
            "dimension": {"IND": {"category": {"index": {str(i): i for i in range(21)}}},
                          "TIME": {"category": {"index": {"0": 0, "1": 1, "2": 2}}}},
            "value": values}


def values():
    v = [100.0] * 63
    v[3 * 3 + 0] = 600.0  # gross_production_total, 2019-08: its six plants are 100 each
    v[3 * 3 + 1] = 610.0  # 2019-09: off by 10, more than 1 MWh a plant
    v[3 * 3 + 2] = 600.0
    v[3 * 10:3 * 11] = [600.0, 600.0, 600.0]  # net_production_total
    v[3 * 20 + 2] = None  # households, 2026-01: empty
    return v


class Parse(unittest.TestCase):
    def test_rows(self):
        m = meta()
        q = M.query(m)
        self.assertEqual([x["code"] for x in q["query"]], ["IND", "TIME"])
        t = M.parse(answer(values()), m, dict(source="s", source_url="u", retrieved_at="r", vintage=""))
        got = {(r.variable, r.ts_utc): r for r in t.itertuples()}
        self.assertEqual(got[("gross_production_hydro", "2019-09-01T00:00:00Z")].value, 100.0)
        self.assertIn(("net_production_hydro", "2026-01-01T00:00:00Z"), got)
        self.assertNotIn(("final_consumption_households", "2026-01-01T00:00:00Z"), got)
        r = got[("imports", "2019-08-01T00:00:00Z")]
        self.assertEqual((r.unit, r.freq, r.geo, r.node, r.x_code), ("MWh", "P1M", "MK", "Imports", "0"))
        self.assertEqual(M.plants_off(t), ["gross 2019-09 +10"])

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            M.query(meta(labels=M.LABELS[:20]))
        with self.assertRaises(RuntimeError):
            M.query(meta(months=["2019-08", "2019_09", "2019M10"]))
        with self.assertRaises(RuntimeError):
            M.parse(answer(values()[:-1]), meta(), {})


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(M.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {M.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
