"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 3).

The peak premium explorer's decision "no-cap" said "February 2021 (Winter Storm Uri) is in 2021's figures: 645
intervals at or above 1,000 USD/MWh", which reads as February's count. 645 is the year's; February holds 608 of them,
and the year's 99.9th percentile, 9,000.85, is February's doing (1,058.53 without it). Words only. The data test reads
the two tables where they are held (warehouse/output, or a folder named by ERW_AUDIT_OUTPUT); the 99.9th percentile
without February needs the 15-minute prices (ERW_AUDIT_HUBAVG, the audit's extract); the words test runs everywhere.
"""
import csv
import datetime as dt
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UTC = dt.timezone.utc


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def table(name):
    for d in (os.environ.get("ERW_AUDIT_OUTPUT"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, name + ".csv")):
            return os.path.join(d, name + ".csv")
    return None


def rows(path):
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            if r["entity"] == "ercot:HB_HUBAVG":
                out[(r["variable"], r["ts_utc"][:7])] = float(r["value"])
    return out


class TheStormsCountIsTheYears(unittest.TestCase):
    def test_645_is_the_years_and_608_februarys(self):
        a, m = table("ercot_peak_premium_annual"), table("ercot_peak_premium_monthly")
        if not (a and m):
            self.skipTest("the peak premium tables are not held on this machine")
        a, m = rows(a), rows(m)
        self.assertEqual(a[("n_scarcity", "2021-01")], 645)
        self.assertEqual(m[("n_scarcity", "2021-02")], 608)
        self.assertEqual(f"{a[('all_p999', '2021-01')]:.2f}", "9000.85")

    def test_the_years_999th_percentile_without_february(self):
        path = os.environ.get("ERW_AUDIT_HUBAVG")
        if not path or not os.path.exists(path):
            self.skipTest("no extract of HB_HUBAVG's 15-minute prices is named here")
        v = []
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["variable"] != "spp_rtm":
                    continue
                t = dt.datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ")
                # the local year 2021 and its February in Central Standard Time (no clock change falls on their edges)
                loc = t - dt.timedelta(hours=6)
                if loc.year == 2021 and loc.month != 2:
                    v.append(float(r["value"]))
        v.sort()
        pos = (len(v) - 1) * 0.999
        lo = int(pos)
        p = v[lo] + (v[lo + 1] - v[lo]) * (pos - lo)
        self.assertEqual(f"{p:.2f}", "1058.53")

    def test_the_decision_says_whose_count_it_is(self):
        d = src("site", "app", "explore", "ercot-peak-premium", "Decisions.tsx")
        self.assertIn("February 2021 (Winter Storm Uri) is in 2021's figures: the year has 645 intervals at or above 1,000 USD/MWh at the hub average, 608 of them in February, and a 99.9th percentile of 9,000.85, which would be 1,058.53 without February.", d)
        self.assertNotIn(chr(0x2014), d)


if __name__ == "__main__":
    unittest.main()
