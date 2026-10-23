"""Session 2021: EIA's U.S. liquefaction capacity (LNG export projects and trains).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_lng_liquefaction.py on a workbook built here in EIA's
form (figures made up for the test, not EIA's): a train in operation and one commissioning, an approved project, a
footnote mark split from its figure and kept, "Note A" and "n/a" as no figure, an offshore project; text where a figure
belongs, a status not in the map, a location not in the map and a train given twice stopping the run; the sector rule
and the holds. No network.

    python -m unittest tests.test_session2021 -v
"""

import datetime as dt
import io
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_lng_liquefaction as L  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
N = None
EX_HEAD = ["Project name", "Train", "Baseload nameplate capacity per Train", N, "Peak nameplate capacity per Train", N, N, "Project status",
           "In-service date", "Date of the start of commercial operation", "Location (U.S. state)", "DOE-authorized export quantity", N,
           "DOE FTA application docket number", "DOE-authorized export quantity", N, "DOE non-FTA application docket number",
           "FERC-authorized export quantity", N, "FERC docket number", "Project type", "Operator"]
EX_UNITS = [N, N, "Bcf/d", "Mtpa", "Bcf/d", "Mtpa", N, N, N, N, N, "Bcf/d", "Mtpa", N, "Bcf/d", "Mtpa", N, "Bcf/d", "Mtpa", N, N, N]
AP_HEAD = ["Project name", "Project operator", "Proposed design capacity per train", N, "Number of trains", "Proposed design capacity", N,
           "Project status", "Location (state)", "DOE-authorized export quantity", N, "DOE FTA application docket number",
           "DOE-authorized export quantity", N, "DOE non-FTA application docket number", "FERC-authorized export quantity", N, "FERC docket number",
           "Project type"]
AP_UNITS = [N, N, "Bcf/d", "Mtpa", N, "Bcf/d", "Mtpa", N, N, "Bcf/d", "Mtpa", N, "Bcf/d", "Mtpa", N, "Bcf/d", "Mtpa", N, N]


def ex_row(name="Sabine Pass", train="Train 1", status="Commercial operation", state="LA", peak=0.76, ins=dt.datetime(2016, 2, 1)):
    return [name, train, 0.59, 4.5, peak, 5.76, N, status, ins, dt.datetime(2016, 5, 1) if status.startswith("Commercial") else N, state,
            0.76, 5.77, "10-85-LNG", 0.76, 5.77, "10-111-LNG", 0.76, 5.76, "CP11-72", "Brownfield", "Cheniere Energy"]


AP = ["Lake Charles LNG", "Energy Transfer, LP", 0.72, 5.5, 3, 2.17, "16.50^", "Completed FEED", "LA", 1.97, "15.00^", "11-59-LNG", "2.00B",
      "15.00^", "11-59-LNG", "n/a", "Note A", "CP14-120", "Brownfield"]


def book(ex, ap=None):
    b = io.BytesIO()
    with pd.ExcelWriter(b) as w:
        pd.DataFrame([["Existing, under construction"] + [N] * 21, EX_HEAD, EX_UNITS] + ex + [["Notes:"] + [N] * 21]).to_excel(
            w, sheet_name="Existing & Under Construction", index=False, header=False)
        pd.DataFrame([["U.S. large scale approved"] + [N] * 18, ["(listed)"] + [N] * 18, AP_HEAD, AP_UNITS] + [ap or AP]
                     + [["Notes:"] + [N] * 18]).to_excel(w, sheet_name="Approved", index=False, header=False)
    return b.getvalue()


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = L.parse(book([ex_row(), ex_row("Golden Pass", "Train 1D", "Commissioning", "TX", "0.80D", dt.datetime(2026, 4, 1)),
                             ex_row("Delfin FLNG", "Train 1", "Under construction", "Offshore", 0.58, "2030")]), BASE)
        got = {r["entity_id"]: r for r in rows}
        s = got["eia_lng:sabine_pass:train_1"]
        self.assertEqual((s["status"], s["status_date"], s["x_commercial_operation_date"], s["geo"], s["x_peak_bcfd"]),
                         ("operating", "2016-02-01", "2016-05-01", "US-LA", 0.76))
        g = got["eia_lng:golden_pass:train_1d"]
        self.assertEqual((g["status"], g["x_status"], g["x_peak_bcfd"], g["x_marks"]), ("", "Commissioning", 0.80, "peak_bcfd:D"))
        d = got["eia_lng:delfin_flng:train_1"]
        self.assertEqual((d["status"], d["status_date"], d["x_in_service"], d["geo"]), ("under_construction", "", "2030", "US"))
        a = got["eia_lng:lake_charles_lng"]
        self.assertEqual((a["status"], a["x_trains"], a["x_peak_mtpa"], a["x_doe_nonfta_bcfd"], a["x_ferc_bcfd"], a["x_ferc_mtpa"]),
                         ("planned", 3, 16.5, 2.0, "", ""))
        self.assertEqual(a["x_marks"], "peak_mtpa:^; doe_fta_mtpa:^; doe_nonfta_bcfd:B; doe_nonfta_mtpa:^; ferc_bcfd:n/a; ferc_mtpa:Note A")

    def test_stops(self):
        for ex in ([ex_row(peak="about 0.8")], [ex_row(status="Mothballed")], [ex_row(state="Ontario")], [ex_row(), ex_row()]):
            with self.assertRaises(RuntimeError):
                L.parse(book(ex), BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(L.TABLE), "gas")
        self.assertIn(L.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {L.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
