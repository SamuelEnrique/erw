"""Session 358: the node, ERCOT's settlement points against the hub (node_basis_daily, node_basis_summary,
ercot_node_prices_hourly), and the day-ahead stage of ercot_rt_spp.py.

Energy Research Warehouse (ERW). The rows here are test fixtures, not data values. No network, no keys.

  1. a day's statistics: the mean, the four dearest hours less the four cheapest, written only when every hour is held;
  2. the disclosure's resource files read into points: a point whose hours are not the day's is left out, the spring
     day has 23 hours, the types at a point make its class;
  3. the summary: a point counts with 90 percent of the hub's days, percentiles across points, the share wider than the
     hub over the point's own days;
  4. the hourly table keeps the newest days under the ceiling;
  5. the day-ahead stage saves each listed day once and writes no table.

    python -m unittest tests.test_session358 -v
"""

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import node_basis as N  # noqa: E402
import ercot_rt_spp as rt  # noqa: E402


def disclosure_zip(path, day_mdy, rows):
    """A 60-day disclosure zip with one Gen Resource Data file: rows of (hour ending, resource type, point, price)."""
    d = pd.DataFrame(rows, columns=["Hour Ending", "Resource Type", "Settlement Point Name", "Energy Settlement Point Price"])
    d.insert(0, "Delivery Date", day_mdy)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("60d_DAM_Gen_Resource_Data-01-JAN-26.csv", d.to_csv(index=False))


class TestDay(unittest.TestCase):
    def test_stats_whole_day_only(self):
        hrs = {k: float(k) for k in range(24)}
        mean, spread, v = N.day_stats(hrs, 24)
        self.assertAlmostEqual(mean, 11.5)
        self.assertAlmostEqual(spread, (20 + 21 + 22 + 23) / 4 - (0 + 1 + 2 + 3) / 4)
        self.assertEqual(len(v), 24)
        del hrs[5]
        self.assertIsNone(N.day_stats(hrs, 24))

    def test_hours_in_clock_change_days(self):
        self.assertEqual(N.hours_in("2026-03-08"), 23)
        self.assertEqual(N.hours_in("2025-11-02"), 25)
        self.assertEqual(N.hours_in("2026-07-01"), 24)

    def test_class(self):
        self.assertEqual(N.class_of({"PVGR"}), "solar")
        self.assertEqual(N.class_of({"PWRSTR"}), "storage")
        self.assertEqual(N.class_of({"ESR"}), "storage")
        self.assertEqual(N.class_of({"PVGR", "ESR"}), "mixed")
        self.assertEqual(N.class_of({"NUC"}), "other")


class TestDisclosure(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw358_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_points_and_types(self):
        rows = []
        for h in range(1, 25):
            rows += [(h, "PVGR", "SOLAR_RN", 10.0 + h), (h, "ESR", "BATT_RN", 20.0 + h), (h, "ESR", "BATT_RN", 20.0 + h)]  # two resources, one point
            if h != 7:
                rows.append((h, "WIND", "SHORT_RN", 5.0))  # an hour missing: not written
        p = os.path.join(self.tmp, "d.zip")
        disclosure_zip(p, "07/01/2026", rows)
        pts, types = N.read_disclosure(p, "2026-07-01")
        self.assertEqual(set(pts), {"SOLAR_RN", "BATT_RN"})
        self.assertEqual(pts["SOLAR_RN"][0], 11.0)
        self.assertEqual(types["BATT_RN"], {"ESR"})

    def test_spring_day_has_23_hours(self):
        rows = [(h, "PVGR", "SOLAR_RN", float(h)) for h in range(1, 25) if h != 3]
        p = os.path.join(self.tmp, "s.zip")
        disclosure_zip(p, "03/08/2026", rows)
        pts, _ = N.read_disclosure(p, "2026-03-08")
        self.assertEqual(len(pts["SOLAR_RN"]), 23)
        self.assertEqual(pts["SOLAR_RN"][2], 4.0)  # hour ending 4 is the day's third hour

    def test_wrong_date_refused(self):
        p = os.path.join(self.tmp, "w.zip")
        disclosure_zip(p, "07/02/2026", [(h, "PVGR", "X", 1.0) for h in range(1, 25)])
        with self.assertRaises(ValueError):
            N.read_disclosure(p, "2026-07-01")


class TestSummary(unittest.TestCase):
    def frame(self):
        rows = []
        days = [f"2026-07-{k:02d}" for k in range(1, 11)]
        for i, day in enumerate(days):
            rows.append(("HB_HUBAVG", day, "dam", 30.0, 20.0, 0.0, "hub", "HU"))
            for j in range(10):
                rows.append((f"S{j}", day, "dam", 30.0 + j, 20.0 + 2 * j, float(j), "storage", "ESR"))
            if i < 5:  # half the days: does not count
                rows.append(("HALF", day, "dam", 99.0, 99.0, 69.0, "storage", "ESR"))
        return pd.DataFrame(rows, columns=["sp", "day", "market", "mean", "spread", "basis", "cls", "typ"])

    def test_percentiles_and_share(self):
        s = N.summary_rows(self.frame(), "2026-10-20T00:00:00Z")
        get = lambda v: float(s[s.variable == v]["value"].iloc[0])
        self.assertEqual(get("dam_storage_points"), 10.0)
        self.assertEqual(get("dam_storage_days"), 10.0)
        self.assertAlmostEqual(get("dam_storage_basis_p50"), float(np.percentile(range(10), 50)))
        self.assertAlmostEqual(get("dam_storage_hub_spread_4h"), 20.0)
        self.assertAlmostEqual(get("dam_storage_share_wider_pct"), 90.0)  # S0's spread equals the hub's: not wider
        self.assertEqual(set(s.x_class), {"all", "storage"})
        self.assertEqual(set(s.ts_utc), {"2026-07-01T00:00:00Z"})


class TestHourly(unittest.TestCase):
    def test_newest_days_under_ceiling(self):
        keep = [(f"S{j}", f"2026-07-{d:02d}", "dam", np.zeros(24)) for d in range(1, 11) for j in range(3)]
        with mock.patch.object(N, "HOURLY_CEILING", 24 * 3 * 4):
            df, (a, b) = N.hourly_rows(keep, "2026-10-20T00:00:00Z")
        self.assertEqual((a, b), ("2026-07-07", "2026-07-10"))
        self.assertEqual(len(df), 24 * 3 * 4)
        self.assertEqual(df.ts_utc.min(), "2026-07-07T05:00:00Z")  # Central daylight time: midnight is 05:00 UTC


class TestDamStage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw358d_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_saves_each_day_once(self):
        csv_text = "DeliveryDate,HourEnding,SettlementPoint,SettlementPointPrice,DSTFlag\n10/01/2026,01:00,HB_HUBAVG,30.1,N\n"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("cdr.00012331.0000000000000000.20260930.123000000.DAMSPNP4190.csv", csv_text)
        content = buf.getvalue()
        listing = {"ListDocsByRptTypeRes": {"DocumentList": [{"Document": {
            "FriendlyName": "DAMSPNP4190_csv", "ConstructedName": "cdr.x.DAMSPNP4190_csv.zip", "DocID": "1", "ContentSize": str(len(content)),
            "PublishDate": "2026-09-30T12:30:00-05:00"}}]}}

        class R:
            def __init__(self, body=None, content=b""):
                self.text, self.content, self.status_code = json.dumps(body) if body else "", content, 200

            def raise_for_status(self):
                pass

            def json(self):
                return json.loads(self.text)

        calls = []

        def get(url, **kw):
            calls.append(url)
            return R(listing) if "IceDocList" in url else R(content=content)
        with mock.patch.object(rt, "DAM_RAW", self.tmp), mock.patch.object(rt, "DAM_ZIPS", os.path.join(self.tmp, "zips")), \
                mock.patch.object(rt, "DAM_MANIFEST", os.path.join(self.tmp, "zips", "manifest.csv")), mock.patch.object(rt, "PAUSE", 0), \
                mock.patch.object(rt.ip, "paused", return_value=None):
            self.assertEqual(rt.pull_dam(None, lambda *_: None, get=get), 1)
            self.assertEqual(rt.pull_dam(None, lambda *_: None, get=get), 0)  # held: not asked again
            with open(os.path.join(self.tmp, "zips", "manifest.csv"), encoding="utf-8") as f:
                self.assertIn("2026-10-01", f.read())
        self.assertEqual(sum("mirDownload" in c for c in calls), 1)


if __name__ == "__main__":
    unittest.main()
