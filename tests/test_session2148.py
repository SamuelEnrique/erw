"""Session 2148: BPA's balancing authority load and generation, five-minute values to the hour.

Energy Research Warehouse (ERW). Tests warehouse/connectors/bpa_ba.py on workbooks built here in BPA's two formats
(figures made up for the test, not BPA's): the new format's UTC column, the old format's Pacific times across November's
repeated hour, an empty value left out of its hour's mean, the forecasts not taken; a time given twice, a step that is
not five minutes and a column not found each stopping the run; the yearly links found on the page; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2148 -v
"""

import io
import os
import sys
import unittest

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import bpa_ba as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
NEW_HEAD = ["Date/Time", "Date/Time (UTC)", "TOTAL WIND BASE SCHEDULE (FORECAST) IN BPA CONTROL AREA (MW; SCADA 1)",
            "TOTAL WIND BASEPOINT (FORECAST) IN BPA CONTROL AREA (MW; SCADA 2)", "TOTAL WIND GENERATION  IN BPA CONTROL AREA (MW; SCADA 3)",
            "TOTAL BPA CONTROL AREA LOAD (MW; SCADA 4)", "TOTAL HYDRO GENERATION (MW; SCADA 5)", "TOTAL FOSSIL/BIOMASS GENERATION (MW; SCADA 6)",
            "TOTAL NUCLEAR GENERATION (MW; 7)", "NET INTERCHANGE (MW; SCADA 8)", "TOTAL SOLAR BASE SCHEDULE (FORECAST) IN BPA CONTROL AREA (MW; 9)",
            "TOTAL SOLAR Basepoint (FORECAST) IN BPA CONTROL AREA (MW; 10)", "TOTAL SOLAR GENERATION  IN BPA CONTROL AREA (MW; SCADA 11)"]


def new_book(times, head=NEW_HEAD, empty_load_at=None):
    wb = openpyxl.Workbook()
    w = wb.active
    w.title = "Data"
    w.append(["TOTAL LOAD & VER GENERATION IN THE BPA CONTROL AREA (Balancing Authority Area)"])
    w.append(head)
    for k, (loc, utc) in enumerate(times):
        load = None if k == empty_load_at else 6000 + k
        w.append([loc, utc, 1, 2, 30, load, 5000, 800, 1100, 1700, 0, 0, 10])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def utc_hour(h, n=12):
    return [(f"01/01/24 {h:02d}:{m:02d}", f"01/01/24 {h + 8:02d}:{m:02d}") for m in range(0, 5 * n, 5)]


class Parse(unittest.TestCase):
    def test_new_format(self):
        t, fmt = P.read_year(new_book(utc_hour(0), empty_load_at=3), "x.xlsx", 2024)
        self.assertEqual(fmt, "new")
        self.assertNotIn("wind_basepoint", t.columns)
        h = P.hourly(t, fmt, BASE)
        load = h[h.variable == "load"].iloc[0]
        self.assertEqual((load.ts_utc, load.x_intervals, load.unit, load.ba), ("2024-01-01T08:00:00Z", 11, "MW", "bpat"))
        self.assertAlmostEqual(load.value, sum(6000 + k for k in range(12) if k != 3) / 11, places=3)
        self.assertEqual(h[h.variable == "solar_generation"].iloc[0].value, 10)
        self.assertEqual(sorted(h.variable), sorted(v for _, v in P.WANTED))

    def test_old_format_local_times(self):
        # the old format's local times, tested through the conversion the connector uses (an .xls cannot be written here)
        import pandas as pd
        loc = ["11/03/24 00:55", "11/03/24 01:00", "11/03/24 01:55", "11/03/24 01:00", "11/03/24 01:55", "11/03/24 02:00"]
        s = pd.to_datetime(pd.Series(loc), format="%m/%d/%y %H:%M").dt.tz_localize("America/Los_Angeles", ambiguous="infer")
        self.assertEqual(list(s.dt.tz_convert("UTC").dt.strftime("%H:%M")), ["07:55", "08:00", "08:55", "09:00", "09:55", "10:00"])

    def test_stops(self):
        times = utc_hour(0, 3)
        for content, words in [(new_book(times + times[-1:]), "given twice"),
                               (new_book([times[0], (times[0][0], "01/01/24 08:20")]), "not five minutes"),
                               (new_book(times, head=[h for h in NEW_HEAD if "NUCLEAR" not in h] + [None]), "no column for")]:
            with self.assertRaises(RuntimeError) as c:
                P.read_year(content, "x.xlsx", 2024)
            self.assertIn(words, str(c.exception))

    def test_year_links(self):
        page = ("<a href=OPITabularReports/WindGenTotalLoadYTD_2026.xlsx>2026</a> <a href=OPITabularReports/WindGenTotalLoadYTD_2021.xls>2021</a>"
                "<a href=OPITabularReports/ReservesDeployedYTD_2026.xlsx>r</a>")
        links = P.year_links(page)
        self.assertEqual(sorted(links), [2021, 2026])
        self.assertEqual(links[2021], "https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_2021.xls")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(P.TABLE), "power")
        self.assertIn(P.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {P.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
