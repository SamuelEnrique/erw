"""Session 2028: DOE's electric emergency incident and disturbance reports (DOE-417).

Energy Research Warehouse (ERW). Tests warehouse/connectors/doe_oe417.py on a workbook built here in the summaries'
2024 form (made up for the test, not DOE's): the header found by its words below a title block, the printed total
checked, a row with no begin day left out and counted, the event types split and the form's comment label left out,
a figure printed as Unknown kept out of mw; a total that does not match and a begin date not a date stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session2028 -v
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
import doe_oe417 as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ["Event Month", "Date Began", "Time Began", "Date Restored", "Time Restored", "Area Affected", "Alert Criteria",
        "Event Type", "Demand Loss (MW)", "Customers Affected"]
LABEL = "Additional Information/Comments (limit 250 characters):"


def workbook(rows, total):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Annual Summary"
    ws.append(["DOE-417 Annual Summary"])
    ws.append([])
    ws.append(["made up for a test"])
    ws.append([])
    ws.append(HEAD)
    for r in rows:
        ws.append(r)
    ws.append([])
    ws.append([f"End of report - {total} total incident(s) for 2024"])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


R1 = ["January", "01/09/2024", "02:15 PM", "01/10/2024", "08:00 AM", "Harris County, Texas", "Loss of electric service",
      f"Weather or natural disaster; Other; {LABEL}", "350", "120,000"]
R2 = ["March", "03/26/2024", "04:00 AM", "Unknown", "Unknown", "Hanover County, Virginia", "Physical attack",
      "Vandalism", "Unknown", "Unknown"]
R3 = ["August", None, "05:00 PM", "08/02/2024", "06:00 PM", "Cook County, Illinois", "Suspicious activity", "Other", "0", "0"]


class Read(unittest.TestCase):
    def test_rows(self):
        rows, printed, no_day = D.read_year(workbook([R1, R2, R3], 3), 2024)
        self.assertEqual((len(rows), printed, no_day), (2, 3, 1))
        a, b = rows
        self.assertEqual((a["n"], a["begin"], a["rest"], a["area"]), (1, "2024-01-09", "2024-01-10", "Harris County, Texas"))
        self.assertEqual((b["n"], b["rest"], b["rest_raw"]), (2, "", "Unknown"))
        e = D.build([(2024, rows)], lambda y: {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}).set_index("event_id")
        self.assertEqual(e.loc["doe417:2024-0001", "event_type"], "weather_or_natural_disaster")
        self.assertEqual(e.loc["doe417:2024-0001", "x_event_types"], "weather_or_natural_disaster; other")
        self.assertEqual((e.loc["doe417:2024-0001", "mw"], e.loc["doe417:2024-0001", "x_customers_affected"]), ("350", "120000"))
        self.assertEqual((e.loc["doe417:2024-0002", "mw"], e.loc["doe417:2024-0002", "status"]), ("", ""))
        self.assertEqual(e.loc["doe417:2024-0001", "status"], "restored")

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            D.read_year(workbook([R1, R2], 3), 2024)
        with self.assertRaises(RuntimeError):
            D.read_year(workbook([R1[:1] + ["soon"] + R1[2:]], 1), 2024)

    def test_types_and_figures(self):
        self.assertEqual(D.types_of(chr(0xA0).join(["- Physical attack", "- Vandalism", "- Other"])), ["physical_attack", "vandalism", "other"])
        self.assertEqual(D.types_of("Severe Weather - Transmission Interruption"), ["severe_weather_transmission_interruption"])
        self.assertEqual(D.types_of(LABEL), [])
        self.assertEqual((D.number("1,200"), D.number("Unknown"), D.number("50-100")), ("1200", "", ""))
        self.assertEqual(D.url_of(2023)[-4:], ".xls")
        self.assertEqual(D.url_of(2024)[-5:], ".xlsx")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.TABLE), "power")
        self.assertIn(D.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
