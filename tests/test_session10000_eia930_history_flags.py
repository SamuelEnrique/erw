"""Session 10000 (chain 701, predict data request 9): warehouse/connectors/eia930_history.py's --all-bas, --forecast and
--ceiling, read from a made-up six-month file in a temporary raw folder (--from-raw, --out-dir); no request is made."""
import csv
import importlib.util
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))

HEAD = ['"Balancing Authority"', '"Data Date"', '"Hour Number"', '"Local Time at End of Hour"', '"UTC Time at End of Hour"',
        '"Demand Forecast (MW)"', '"Demand (MW)"', '"Net Generation (MW)"', '"Demand (MW) (Adjusted)"',
        '"Net Generation (MW) (Adjusted)"']


def load():
    spec = importlib.util.spec_from_file_location("e930h_t", os.path.join(ROOT, "warehouse", "connectors", "eia930_history.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def write_file(d, name):
    run = os.path.join(d, "raw", "eia930_history", "20261127T000000Z")
    os.makedirs(run)
    fname = f"20261127T000001.000000Z_00001_{name}"
    with open(os.path.join(run, fname), "w", encoding="utf-8", newline="") as f:
        f.write(",".join(HEAD) + "\n")
        f.write('CISO,07/01/2015,1,07/01/2015 1:00:00 AM,07/01/2015 8:00:00 AM,"25,100","24,900","20,000","24,950","20,010"\n')
        f.write('AVA,07/01/2015,1,07/01/2015 1:00:00 AM,07/01/2015 8:00:00 AM,1500,1450,1600,1452,1601\n')
    with open(os.path.join(run, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["retrieved_at", "status", "bytes", "sha256", "last_modified", "file", "url"])
        w.writerow(["2026-11-27T00:00:01Z", "200", "1", "x", "Thu, 26 Nov 2026 00:00:00 GMT", fname, "u"])


def rows(d):
    p = os.path.join(d, "eia930_all_history.csv")
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


class TheFlags(unittest.TestCase):
    def run_with(self, *flags):
        m = load()
        d = tempfile.mkdtemp()
        write_file(d, "EIA930_BALANCE_2015_Jul_Dec.csv")
        code = m.main(["--file", "EIA930_BALANCE_2015_Jul_Dec.csv", "--from-raw", "--out-dir", d, *flags])
        return code, d

    def test_as_before_without_the_flags(self):
        code, d = self.run_with()
        self.assertEqual(code, 0)
        r = rows(d)
        self.assertEqual({x["entity"] for x in r}, {"eia930:CISO"})
        self.assertEqual({x["variable"] for x in r}, {"demand_mw", "net_generation_mw"})

    def test_every_authority_and_the_forecast(self):
        code, d = self.run_with("--all-bas", "--forecast")
        self.assertEqual(code, 0)
        r = rows(d)
        got = {(x["entity"], x["variable"]): x["value"] for x in r}
        self.assertEqual(got[("eia930:AVA", "demand_forecast_mw")], "1500")
        self.assertEqual(got[("eia930:CISO", "demand_forecast_mw")], "25100")
        self.assertEqual(got[("eia930:CISO", "demand_mw")], "24950")   # the Adjusted column, as before
        self.assertEqual({x["ba"] for x in r if x["entity"] == "eia930:AVA"}, {"ava"})
        self.assertEqual({x["geo"] for x in r if x["entity"] == "eia930:AVA"}, {""})
        self.assertEqual({x["ts_utc"] for x in r}, {"2015-07-01T07:00:00Z"})

    def test_the_ceiling_stops_a_run(self):
        code, d = self.run_with("--all-bas", "--forecast", "--ceiling", "3")
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(os.path.join(d, "eia930_all_history.csv")))

    def test_a_download_is_kept_and_a_quoted_header_read(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "eia930_history.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("ip.RAW.record(url, r.status_code, r.content, r.headers)", s)
        self.assertIn("lstrip(codecs.BOM_UTF8).lstrip(b'\"').startswith(b\"Balancing\")", s)


if __name__ == "__main__":
    unittest.main()
