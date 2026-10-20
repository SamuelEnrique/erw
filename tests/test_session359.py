"""Session 359: ERCOT's four coincident peaks (ercot_4cp_intervals, warehouse/connectors/ercot_4cp.py).

Energy Research Warehouse (ERW). The workbook here is a fixture built in the test, not ERCOT's data. No network.

  1. a month's header is read into its interval: the printed time is the interval's end in Central prevailing time,
     ts_utc its start;
  2. a workbook's four months are read from its Total row, under the month headers; a workbook without the four
     months, or without one Total row, is refused;
  3. the pull asks at most 20 times, and a file held is not asked for again.

    python -m unittest tests.test_session359 -v
"""

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_4cp as C  # noqa: E402


def book(headers, total, label_col=1):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["2030 Four Coincident Peak Load Calculation (MW)"])
    ws.append(["TDSP Code", "Load Entity Name", "DUNS NUMBER"] + headers + ["Average 4CP Load", "Load Ratio Share"])
    ws.append([1, "AN ENTITY (TDSP)", "1"] + [1.0] * len(headers) + [1.0, 0.5])
    row = [None] * 3 + total + [sum(total) / len(total), 1]
    row[label_col] = "Total"
    ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


HEADERS = ["June \n6/19/2030 17:00 ", "July\n7/30/2030 16:45", "August\n8/18/2030 17:00", "September\n9/04/2030 17:30"]


class TestInterval(unittest.TestCase):
    def test_end_printed_start_written(self):
        month, local, start = C.interval("June \n6/19/2025 17:00 ")
        self.assertEqual((month, local), (6, "2025-06-19 17:00"))
        self.assertEqual(start.strftime("%Y-%m-%dT%H:%M:%SZ"), "2025-06-19T21:45:00Z")  # 16:45 CDT is 21:45 UTC
        self.assertIsNone(C.interval("Average 4CP Load"))


class TestBook(unittest.TestCase):
    def test_total_row_under_the_headers(self):
        out = C.read_book(book(HEADERS, [10.0, 20.0, 30.0, 40.0]))
        self.assertEqual([(o[1], o[4]) for o in out], [(6, 10.0), (7, 20.0), (8, 30.0), (9, 40.0)])
        self.assertEqual(out[1][3].strftime("%H:%M"), "21:30")

    def test_refused_without_four_months_or_total(self):
        with self.assertRaises(ValueError):
            C.read_book(book(HEADERS[:3], [1.0, 2.0, 3.0]))
        wb = openpyxl.Workbook()
        wb.active.append(["TDSP Code", "Load Entity Name", "DUNS NUMBER"] + HEADERS)
        buf = io.BytesIO()
        wb.save(buf)
        with self.assertRaises(ValueError):
            C.read_book(buf.getvalue())


class TestPull(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="erw359_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_held_not_asked_again(self):
        listing = {"ListDocsByRptTypeRes": {"DocumentList": [{"Document": {"ConstructedName": "rpt.x.4CP20301124.xlsx", "DocID": "9",
                                                                            "PublishDate": "2030-11-24T08:00:00-06:00"}}]}}

        class R:
            def __init__(self, body=None, content=b"x"):
                self.text, self.content, self.status_code = json.dumps(body) if body else "", content, 200

            def raise_for_status(self):
                pass

            def json(self):
                return json.loads(self.text)
        calls = []

        def get(url, **kw):
            calls.append(url)
            return R(listing) if "IceDocList" in url else R()
        with mock.patch.object(C, "RAW", self.tmp), mock.patch.object(C, "FILES", os.path.join(self.tmp, "files")), \
                mock.patch.object(C, "MANIFEST", os.path.join(self.tmp, "files", "manifest.csv")), mock.patch.object(C, "PAUSE", 0), \
                mock.patch.object(C.ip, "paused", return_value=None):
            self.assertEqual(C.pull(lambda *_: None, get=get), 3)   # the list, the workbook, the zip
            self.assertEqual(C.pull(lambda *_: None, get=get), 1)   # the list alone
        self.assertEqual(len(calls), 4)


if __name__ == "__main__":
    unittest.main()
