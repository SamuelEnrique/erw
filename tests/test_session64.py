"""Session 64: the second year of hub history, two events, the tight-evening forecast.

Energy Research Warehouse (ERW). No request leaves the machine: SPP's archive is an in-memory zip served by a fake
requests.get that honours byte ranges.

    python -m unittest tests.test_session64 -v
"""

import io
import os
import re
import sys
import types
import unittest
import urllib.error
import zipfile

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))

import hub_history as hh  # noqa: E402
import caiso_tight_evening as te  # noqa: E402

DA = "https://portal.spp.org/file-browser-api/download/da-lmp-by-settlement-location"
MEMBER = "2024/09/By_Day/DA-LMP-SL-202409150100.csv"
CSV = b"Interval,GMTIntervalEnd,Settlement Location,Pnode,LMP\n09/15/2024 01:00:00,09/15/2024 06:00:00,SPPNORTH_HUB,SPPNORTH_HUB,21.5\n"


def archive():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("2024/", b"")
        z.writestr("2024/09/By_Day/DA-LMP-SL-202409140100.csv", b"x,y\n1,2\n" * 50)
        z.writestr(MEMBER, CSV)
    return buf.getvalue()


class Ranged:
    """A fake requests module: GET with a Range header answers 206 with those bytes of the archive."""

    def __init__(self, blob):
        self.blob, self.calls = blob, []

    def get(self, url, headers=None, timeout=None, **k):
        self.calls.append((url, headers))
        a, b = map(int, re.match(r"bytes=(\d+)-(\d+)", headers["Range"]).groups())
        body = self.blob[a:b + 1]
        return types.SimpleNamespace(status_code=206, content=body,
                                     headers={"Content-Range": f"bytes {a}-{b}/{len(self.blob)}"})


class SppArchive(unittest.TestCase):
    def setUp(self):
        import requests
        self.requests, self.saved_get, self.saved_read = requests, requests.get, pd.read_csv
        self.fake = Ranged(archive())
        requests.get = self.fake.get
        hh._ARCHIVES.clear()

    def tearDown(self):
        self.requests.get = self.saved_get
        pd.read_csv = self.saved_read
        hh._ARCHIVES.clear()

    def test_member_by_range(self):
        got = hh._archive_member(f"{DA}?path=/2024/2024.zip", MEMBER)
        self.assertEqual(got, CSV)
        self.assertTrue(all(h and "Range" in h for _, h in self.fake.calls))

    def test_a_404_daily_file_is_read_from_the_years_archive(self):
        orig = pd.read_csv

        def gone(src, *a, **k):
            if isinstance(src, str):
                raise urllib.error.HTTPError(src, 404, "Not Found", None, None)
            return orig(src, *a, **k)
        pd.read_csv = gone
        hh.spp_archive()
        df = pd.read_csv(f"{DA}?path=/{MEMBER}")
        self.assertEqual(df["Settlement Location"].tolist(), ["SPPNORTH_HUB"])
        self.assertEqual(df["LMP"].tolist(), [21.5])
        self.assertTrue(all(u == f"{DA}?path=/2024/2024.zip" for u, _ in self.fake.calls))

    def test_other_errors_and_urls_pass_through(self):
        orig = pd.read_csv

        def boom(src, *a, **k):
            if isinstance(src, str):
                raise urllib.error.HTTPError(src, 500, "Server Error", None, None)
            return orig(src, *a, **k)
        pd.read_csv = boom
        hh.spp_archive()
        with self.assertRaises(urllib.error.HTTPError):
            pd.read_csv(f"{DA}?path=/{MEMBER}")
        self.assertEqual(self.fake.calls, [])
        df = pd.read_csv(io.StringIO("a,b\n1,2\n"))  # not a URL: untouched
        self.assertEqual(len(df), 1)

    def test_a_missing_member_is_an_error_not_a_fill(self):
        with self.assertRaises(FileNotFoundError):
            hh._archive_member(f"{DA}?path=/2024/2024.zip", "2024/10/By_Day/DA-LMP-SL-202410010100.csv")


class TightEvening(unittest.TestCase):
    def test_threshold_maximizes_f1(self):
        peaks = np.array([40, 41, 42, 45, 46, 47.0])
        alert = np.array([False, False, False, True, True, False])
        t, f1 = te.best_threshold(peaks, alert)
        self.assertEqual(t, 45.0)
        self.assertAlmostEqual(f1, 2 * 2 / (2 * 2 + 1 + 0))

    def test_auc(self):
        self.assertEqual(te.auc(np.array([1, 2, 3, 4.0]), np.array([False, False, True, True])), 1.0)
        self.assertEqual(te.auc(np.array([1, 1.0]), np.array([True, False])), 0.5)
        self.assertIsNone(te.auc(np.array([1.0]), np.array([False])))

    def test_the_table_is_internal_and_not_live(self):
        import yaml
        live = yaml.safe_load(open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
        pats = [p for v in live.values() if isinstance(v, list) for p in v if isinstance(p, str)]
        self.assertFalse(any(re.search(p, te.NAME) for p in pats))
        src = open(os.path.join(ROOT, "warehouse", "derived", "caiso_tight_evening.py"), encoding="utf-8").read()
        self.assertIn('"License: internal.', src)
        self.assertIn('license="internal"', src)


class Events(unittest.TestCase):
    def test_the_two_events(self):
        import event_window as ew
        ids = {m["event"]: m for m in ew.MULTI}
        self.assertEqual((ids["cold_2025"]["start"], ids["cold_2025"]["end"]), ("2025-01-17", "2025-01-26"))
        self.assertEqual((ids["east_heat_2025"]["start"], ids["east_heat_2025"]["end"]), ("2025-06-20", "2025-06-28"))
        for e in ("cold_2025", "east_heat_2025"):
            for h in ids[e]["hubs"]:
                self.assertIn(h, hh.ENTITIES)  # every hub is one the history holds
        for page in ("cold-2025", "east-heat-2025"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "app", "events", page, "page.tsx")))


if __name__ == "__main__":
    unittest.main()
