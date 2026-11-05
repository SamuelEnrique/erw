"""Session 2358: StatBank's electricity by months, Moldova (in Bangladesh's place).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statbank_moldova.py on metadata and a JSON-stat answer built
here in StatBank's form (figures made up for the test, not the bureau's): the query built from the metadata, a row read
with its variable, an empty month no row; indicators not the seven expected, months not 01 to 12 and an answer not the
size of its dimensions each stopping the run; the sector rule and the hold. No network.

    python -m unittest tests.test_session2358 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statbank_moldova as S  # noqa: E402
import build_coverage as B  # noqa: E402

CODES = [str(i) for i in range(1, 8)]


def meta(labels=None, months=None):
    labels = labels or [S.INDICATORS[c][1] for c in CODES]
    months = months or [f"{m:02d}" for m in range(1, 13)]
    return {"variables": [{"code": "Indicatori", "values": CODES[:len(labels)], "valueTexts": labels},
                          {"code": "Ani", "values": ["2025", "2026"], "valueTexts": ["2025", "2026"]},
                          {"code": "Luni", "values": months, "valueTexts": months}]}


def answer(values):
    return {"id": ["Indicatori", "Ani", "Luni"], "size": [7, 2, 12],
            "dimension": {"Indicatori": {"category": {"index": {c: i for i, c in enumerate(CODES)}}},
                          "Ani": {"category": {"index": {"2025": 0, "2026": 1}}},
                          "Luni": {"category": {"index": {f"{m:02d}": m - 1 for m in range(1, 13)}}}},
            "value": values}


class Parse(unittest.TestCase):
    def test_rows(self):
        self.assertEqual([q["code"] for q in S.query(meta())["query"]], ["Indicatori", "Ani", "Luni"])
        v = [float(k) for k in range(168)]
        v[12 + 11] = None  # production, 2026-12: not yet published
        t = S.parse(answer(v), dict(source="s", source_url="u", retrieved_at="r", vintage=""))
        got = {(r.variable, r.ts_utc): r for r in t.itertuples()}
        r = got[("acquired_from_other_sources", "2025-03-01T00:00:00Z")]
        self.assertEqual((r.value, r.unit, r.freq, r.geo, r.x_code), (50.0, "MWh", "P1M", "MD", "3"))
        self.assertNotIn(("production", "2026-12-01T00:00:00Z"), got)
        self.assertEqual(len(t), 167)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            S.query(meta(labels=["Production", "Import"]))
        with self.assertRaises(RuntimeError):
            S.query(meta(months=["1", "2"]))
        with self.assertRaises(RuntimeError):
            S.parse(answer([1.0] * 167), {})


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
