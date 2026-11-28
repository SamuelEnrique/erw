"""Session 11408 (chain 770, part C): /demand, the other choice of the demand audit's finding 1
(docs/reviews/demand-model-audit-2026-11-26.md; its test branch wip/audit-demand-2, carried over here and turned to the
new rule). Not for landing until the owner rules.

The rule on this branch: warehouse/derived/demand_growth.py reads each area's own "Demand" (its report to EIA), not EIA's
"Adjusted demand", which holds EIA's estimate where an authority reported nothing or an implausible value; such an hour
is blank and not used. Measured by running the builder on this machine's EIA workbooks of 4 October 2026 (written only
into the worktree): MISO's 2025 peak 120,343 MW (+3.21 percent on 2019) on origin/main, 118,106 MW on 29 July 2025
(+1.29) here; CAISO's 2025 average growth +4.45 to +4.58; MISO's +2.20 to +2.10; blank hours since 2019 ERCOT 48 to 72,
CAISO 48 to 172, PJM 27 to 213, MISO 24 to 96, SPP 24 to 49, ISO-NE 24 to 27, NYISO and the Lower 48 24 unchanged. The
site file (site/data/demand_growth.json) is rebuilt at landing by the desk; it then records column "Demand".

1. On a small workbook written by the test: the builder reads "Demand", and an hour EIA estimated is blank.
2. Where the EIA workbooks are held (ERW_READY_RAW, else the checkout's warehouse/raw; else skipped): MISO's highest
   used hour of 2025 is 118,106 MW at 21:00 UTC on 29 July 2025.
3. Once the site file is rebuilt with column "Demand", it carries that peak and +1.29 percent."""
import datetime
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))


def dg():
    import demand_growth
    return demand_growth


class EachAreasOwnDemand(unittest.TestCase):
    def test_the_builder_reads_demand_and_leaves_an_estimate_blank(self):
        import openpyxl
        m = dg()
        self.assertEqual(m.COLUMN, "Demand")
        tmp = tempfile.mkdtemp(prefix="erw11408_")
        os.makedirs(os.path.join(tmp, "run1"))
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Published Hourly Data"
        ws.append(["UTC time", "Demand", "Adjusted demand"])
        t0 = datetime.datetime(2025, 7, 24, 20)
        ws.append([t0, None, 120343])           # the operator reported nothing; EIA estimated
        ws.append([t0 + datetime.timedelta(hours=1), 110000, 110000])
        wb.save(os.path.join(tmp, "run1", "x_MISO.xlsx"))
        old = m.RAW
        m.RAW = tmp
        try:
            d, _, column = m.read_demand("MISO")
        finally:
            m.RAW = old
        self.assertEqual(column, "Demand")
        self.assertTrue(d.iloc[0] != d.iloc[0])  # NaN: the estimate is not read
        self.assertEqual(float(d.iloc[1]), 110000.0)

    def test_misos_2025_peak_on_its_own_reports(self):
        m = dg()
        raw = os.environ.get("ERW_READY_RAW") or m.RAW
        if not os.path.isdir(raw):
            self.skipTest("the EIA-930 workbooks are not on this machine")
        old = m.RAW
        m.RAW = raw
        try:
            d, _, column = m.read_demand("MISO")
        finally:
            m.RAW = old
        used = m.screened(d)
        local = used.index.tz_convert("America/Chicago")
        y25 = used[local.year == 2025].dropna()
        self.assertEqual(float(y25.max()), 118106.0)
        self.assertEqual(y25.idxmax().strftime("%Y-%m-%dT%H:%M:%SZ"), "2025-07-29T21:00:00Z")

    def test_the_site_file_once_rebuilt(self):
        with open(os.path.join(ROOT, "site", "data", "demand_growth.json"), encoding="utf-8") as f:
            site = json.load(f)
        if site.get("column") != "Demand":
            self.skipTest("the site file is rebuilt at landing by the desk")
        y = site["areas"]["MISO"]["years"]["2025"]
        self.assertEqual((y["peak_demand_mw"], y["peak_demand_growth_since_2019_pct"]), (118106.0, 1.29))


if __name__ == "__main__":
    unittest.main()
