"""Session 10000 (chain 701, part C2): the datacenter carbon file's hours end where the hourly price file's end.

From 25 November the data machine's replication group put back every refresh of the datacenter files: the carbon file
(read from the live set) ran a few days past the page's last price hour, the do-file counts every hour of it as priced,
and test_session5074 found 10,159 hours against the mirror's 10,141. The writer now cuts its hours at the price file's
last hour. Made-up rows; no request.
"""
import importlib.util
import os
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("carbon_t", os.path.join(ROOT, "site", "scripts", "write-datacenter-carbon.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheHoursEndWithThePrices(unittest.TestCase):
    def test_the_last_price_hour_is_read_from_the_hourly_file(self):
        m = load()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "erw_2026_datacenter_hourly.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# a header line\n# another\nhour_utc,std_month,rt_usd_mwh,da_usd_mwh,hub_rt_usd_mwh,in_last_twelve\n")
                f.write("2026-11-21T04:00:00Z,2026-11,30,31,29,0\n2026-11-21T05:00:00Z,2026-11,32,33,31,0\n")
            self.assertEqual(m.last_price_hour(p), "2026-11-21T05:00:00")
            self.assertIsNone(m.last_price_hour(os.path.join(d, "absent.csv")))

    def test_the_writer_cuts_its_hours_there(self):
        with open(os.path.join(ROOT, "site", "scripts", "write-datacenter-carbon.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('hourly = [r for r in hourly if r["ts_utc"][:19] <= last]', s)
        self.assertLess(s.index("last = last_price_hour("), s.index('lines = head + ["kind,ts_utc,kg_co2_per_mwh"]'))


if __name__ == "__main__":
    unittest.main()
