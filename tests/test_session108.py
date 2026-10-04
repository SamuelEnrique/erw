"""Session 108: scoping what real batteries earned, from ERCOT's 60-day disclosure data.

The sample's script on zips made for the test (no file of ERCOT's is in the repository): which documents belong to a
month, the columns kept, whole days under the ceiling, and that the sample is written outside coverage. No network.
"""
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_disclosure_sample as s  # noqa: E402
import iso_prices as ip  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def made_zip(day, resources=3, extra=("QSE submitted Curve-MW1", "QSE submitted Curve-Price1")):
    """A disclosure zip as ERCOT shapes it, with an ESR file of `resources` resources by 24 hours."""
    rows = []
    for r in range(resources):
        for h in range(1, 25):
            row = {c: "" for c in s.KEEP + list(extra)}
            row.update({"Delivery Date": day.strftime("%m/%d/%Y"), "Hour Ending": h, "QSE": "Q1", "DME": "D1", "Resource Name": f"ESR{r}", "Resource Type": "ESR", "HSL": 10.0, "LSL": -10.0,
                        "Resource Status": "ON", "Awarded Quantity": 5.0 if h == 20 else "", "Settlement Point Name": "RN", "Energy Settlement Point Price": 30.0})
            rows.append(row)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"60d_DAM_ESR_Data-{(day + dt.timedelta(days=60)).strftime('%d-%b-%y').upper()}.csv", pd.DataFrame(rows).to_csv(index=False))
        z.writestr("60d_DAM_Gen_Resource_Data-X.csv", "a,b\n1,2\n")
    return buf.getvalue()


class TheSample(unittest.TestCase):
    def test_an_operating_day_is_the_day_published_less_sixty(self):
        docs = [{"PublishDate": "2026-09-29T05:42:55-05:00", "DocID": "1"}, {"PublishDate": "2026-08-30T05:00:00-05:00", "DocID": "2"},
                {"PublishDate": "2026-08-29T05:00:00-05:00", "DocID": "3"}, {"PublishDate": "2026-09-30T05:00:00-05:00", "DocID": "4"}]
        got = s.wanted(docs, "2026-07")
        self.assertEqual([(str(d), x["DocID"]) for d, x in got], [("2026-07-01", "2"), ("2026-07-31", "1")])     # 30 June and 1 August are not July

    def test_the_award_columns_are_kept_and_the_offer_curve_is_not(self):
        name, df, cols, sizes = s.esr_frame(made_zip(dt.date(2026, 7, 1)))
        self.assertTrue(name.startswith("60d_DAM_ESR_Data-"))
        self.assertEqual(list(df.columns), s.KEEP)
        self.assertEqual(len(df), 72)
        self.assertIn("QSE submitted Curve-MW1", cols)
        for c in ("Awarded Quantity", "Energy Settlement Point Price", "RegUp Awarded", "RegUp MCPC", "ECRSSD Awarded", "NonSpin MCPC", "HSL", "LSL"):
            self.assertIn(c, s.KEEP)
        self.assertFalse(any("Curve" in c for c in s.KEEP))
        with self.assertRaises(ValueError):                 # a zip with no ESR file, or with a column gone, stops the run
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("60d_DAM_Gen_Resource_Data-X.csv", "a\n1\n")
            s.esr_frame(buf.getvalue())

    def test_whole_days_are_kept_while_they_fit_under_the_ceiling(self):
        with tempfile.TemporaryDirectory() as d:
            zips, out = os.path.join(d, "zips"), os.path.join(d, "out")
            os.makedirs(zips)
            for i in range(1, 5):
                with open(os.path.join(zips, f"day{i}.zip"), "wb") as f:
                    f.write(made_zip(dt.date(2026, 7, i)))
            old = (s.CEILING, s.OUT_DIR)
            s.CEILING, s.OUT_DIR = 200, out                 # each made day is 72 rows: two fit, the third would pass 200
            try:
                self.assertEqual(s.main(["--month", "2026-07", "--from-dir", zips]), 0)
            finally:
                s.CEILING, s.OUT_DIR = old
            path = os.path.join(out, "ercot_60d_dam_esr_awards_2026-07.csv")
            t = pd.read_csv(path, skiprows=ip.header_rows(path))
            self.assertEqual(len(t), 144)
            self.assertEqual(sorted(t["delivery_date"].unique()), ["2026-07-01", "2026-07-02"])
            meta = json.load(open(os.path.join(out, "ercot_60d_dam_esr_awards_2026-07.json"), encoding="utf-8"))
            self.assertEqual((meta["rows"], meta["requests"], len(meta["days"])), (144, 0, 2))
            self.assertTrue(any("would pass the ceiling" in n for n in meta["notes"]))
            self.assertIn("Not in coverage", open(path, encoding="utf-8").read(2500))

    def test_it_is_kept_out_of_coverage_and_asks_the_pause_list(self):
        code = src("warehouse", "analysis", "ercot_disclosure_sample.py")
        self.assertEqual(s.CEILING, 300_000)
        self.assertTrue(s.OUT_DIR.replace("\\", "/").endswith("warehouse/output/analysis_internal"))
        self.assertIn("warehouse/output/analysis_internal/", src(".gitignore"))
        self.assertIn('if ip.paused("ercot"):', code)
        self.assertNotIn("ip.write_csv", code)              # no warehouse table: not in coverage, the archive, Redivis or Supabase
        cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str)
        self.assertFalse(cov["table"].str.contains("60d|esr_awards").any())

    def test_the_note_says_what_was_and_was_not_read(self):
        note = " ".join(src("docs", "methods", "ercot_disclosure_scoping.md").split())
        for words in ("244,968, of a ceiling of 300,000", "This is not what the batteries earned", "raw data provided in public portions of this website may be used",
                      "this session pulls nothing more", "was not read this session", "7,657,472,543", "23,022,905,292"):
            self.assertIn(words, note)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()
