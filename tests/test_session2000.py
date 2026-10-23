"""Session 2000: the Department of Energy's U.S. Energy and Employment Report (USEER), its public data.

Energy Research Warehouse (ERW). Tests warehouse/connectors/doe_useer.py on sheets built here in the USEER workbook's
form (figures made up for the test, not DOE's): the nation's blocks by industry with the 2025 and 2024 totals, the
change column left out, the TDS block not taken, the state blocks by subsector and by industry, Puerto Rico's row
without a geo; a heading not as read and a state not in the map stopping the run; the sector rule and the holds. No
network.

    python -m unittest tests.test_session2000 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import doe_useer as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEADS = list(U.INDUSTRIES)


def national_sheet(skip_tds=False):
    rows = [["Industry Detail by Sector"], ["Source: test"], []]
    for title, sector, first in U.NATIONAL:
        rows.append([title])
        rows.append([first] + HEADS)
        rows.append(["Solar "] + [None, None, 10.0, 20.0] + [None] * 6 + [30.0, 35.0, -5.0])
        rows.append([f"{sector.upper()} Total"] + [None, None, 10.0, 20.0] + [None] * 6 + [30.0, 35.0, -5.0])
        rows.append([])
        if sector == "storage" and not skip_tds:
            rows += [[U.SKIPPED_BLOCK], ["TDS Subector"] + HEADS, ["TDS Total", 1.0], []]
    return pd.DataFrame(rows)


def state_sheet(state="AL"):
    titles, heads = [], []
    for title, sector in U.STATE_BLOCKS.items():
        cols = ["Agriculture and Forestry", "Utilities"] if sector == "all" else ["Solar", f"{sector} total"]
        titles += [title] + [None] * (len(cols) + 1) + [None]
        heads += ["State abbreviation", "State"] + cols + [None]
    width = len(heads)
    body = []
    for st, name in ((state, "Alabama"), (U.PR_USVI, "Puerto Rico and U.S. Virgin Islands")):
        r = []
        for title, sector in U.STATE_BLOCKS.items():
            r += [st, name, 1.0, 2.0, None]
        body.append(r)
    rows = [["State-level"], ["Source"], [None] * width, titles, heads] + body
    return pd.DataFrame([r + [None] * (width - len(r)) for r in rows])


class National(unittest.TestCase):
    def test_rows(self):
        out, sums = U.national(national_sheet(), BASE)
        s = pd.DataFrame(out).set_index(["entity", "ts_utc"])
        self.assertEqual(s.loc[("useer2026:US:epg:solar:utilities", "2025-01-01T00:00:00Z")].value, 10.0)
        self.assertEqual(s.loc[("useer2026:US:epg:solar:total", "2024-01-01T00:00:00Z")].value, 35.0)
        self.assertEqual(s.loc[("useer2026:US:storage:total:construction", "2025-01-01T00:00:00Z")].unit, "count")
        self.assertFalse(any(":tds:" in e for e, _ in s.index))  # the TDS block is not taken
        self.assertFalse((s.value == -5.0).any())  # nor the change column
        self.assertTrue(all(sums))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            U.national(national_sheet(skip_tds=True), BASE)
        bad = national_sheet()
        bad.iloc[4, 1] = "Farming"
        with self.assertRaises(RuntimeError):
            U.national(bad, BASE)


class States(unittest.TestCase):
    def test_rows(self):
        s = pd.DataFrame(U.states(state_sheet(), BASE)).set_index("entity")
        self.assertEqual(s.loc["useer2026:US-AL:epg:solar:total"].value, 1.0)
        self.assertEqual(s.loc["useer2026:US-AL:epg:total:total"].value, 2.0)
        self.assertEqual(s.loc["useer2026:US-AL:all:all:utilities"].value, 2.0)
        self.assertEqual(s.loc["useer2026:PR_VI:fuels:solar:total"].geo, "")

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            U.states(state_sheet("XX"), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.TABLE), "power;gas;oil;coal")
        self.assertIn(U.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
