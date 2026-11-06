"""Session 2044: DOE's summary of LNG export applications.

Energy Research Warehouse (ERW). Tests warehouse/connectors/doe_lng_exports.py on a page built here in the summary's
form (made up for the test, not the Department's): the rows split at the company column's ruling lines, a name across
two lines, the 7-point footnote markers left out, the FTA and non-FTA quantities and a design increase, the statuses
and dockets, the section carried to the next page, the totals row kept apart; a status not in the map and a row
without a docket stopping the run; the sector rule and the holds. No network, no PDF.

    python -m unittest tests.test_session2044 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import doe_lng_exports as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

COLS = [59, 270, 396, 558, 742]


class Page:
    """Enough of a pdfplumber page: words with their places, the ruling lines, the text."""

    def __init__(self, number, lines, rules, heading=""):
        self.page_number, self.lines, self.rules, self.heading = number, lines, rules, heading
        self.edges = [{"orientation": "v", "x0": x, "height": 400} for x in COLS]
        self.edges += [{"orientation": "h", "x0": COLS[0], "x1": COLS[1], "top": t} for t in rules]

    def filter(self, keep):
        small = [w for w in self.lines if keep({"object_type": "char", "size": w.get("size", 11)})]
        return Page(self.page_number, small, self.rules, self.heading)

    def extract_words(self, **kw):
        return [{"text": w["text"], "x0": w["x0"], "x1": w["x0"] + 3 * len(w["text"]), "top": w["top"],
                 "bottom": w["top"] + 10} for w in self.lines]

    def extract_text(self):
        return self.heading + "\n" + " ".join(w["text"] for w in self.lines)


def words(top, x0, phrase, size=11):
    out, x = [], x0
    for t in phrase.split():
        out.append({"text": t, "x0": x, "top": top, "size": size})
        x += 3 * len(t) + 3
    return out


HEAD = words(100, 64, "Company") + words(100, 280, "Quantity") + words(112, 280, "(Docket Number)")
PAGE1 = Page(1, HEAD
             + words(130, 64, "Cove Point LNG, LP (Formerly Dominion") + words(130, 180, "(zz)", size=7)
             + words(142, 64, "Energy Cove Point LNG, LP) (g)") + words(130, 280, "1.0 Bcf/d: FTA")
             + words(142, 280, "0.77 Bcf/d: Non-FTA") + words(130, 400, "Approved (11-115-LNG)")
             + words(130, 562, "Approved (F) (11-128-LNG)")
             + words(160, 64, "Plaquemines LNG, LLC") + words(160, 280, "3.40 Bcf/d 0.45 Bcf/d Design Increase")
             + words(160, 400, "Approved (16-28-LNG)") + words(160, 562, "Under DOE Review (16-28-LNG) *")
             + words(190, 64, "Total of all Applications Received") + words(190, 400, "4.40 Bcf/d") + words(190, 562, "3.62 Bcf/d"),
             [100.0, 100.9, 125, 155, 185, 210])
PAGE2 = Page(2, HEAD + words(130, 64, "Blue Water Fuels, LLC (Long-Term)") + words(130, 280, "0.009")
             + words(130, 400, "n/a") + words(130, 562, "Vacated (F) (19-99-LNG)"),
             [100.0, 125, 155], heading="SMALL-SCALE APPLICATIONS (Includes Short-Term & Long-Term)")
PAGE3 = Page(3, HEAD + words(130, 64, "Accel LNG Energy Llc") + words(130, 280, "0.14") + words(130, 400, "Under DOE Review (26-59-LNG)"),
             [100.0, 125, 155])


class Build(unittest.TestCase):
    def test_rows(self):
        t, totals = D.build([(1, PAGE1), (2, PAGE2), (3, PAGE3)], "u", "r", "2026-09-30")
        t = t.set_index("entity_id")
        a = t.loc["doe_lng:11-115-LNG"]
        self.assertEqual((a["name"], a.x_footnotes, a.x_fta_bcfd, a.x_non_fta_bcfd, a.status),
                         ("Cove Point LNG, LP (Formerly Dominion Energy Cove Point LNG, LP)", "g", "1", "0.77", "active"))
        self.assertEqual((a.x_non_fta_status, a.x_non_fta_docket), ("Approved (F)", "11-128-LNG"))
        b = t.loc["doe_lng:16-28-LNG"]
        self.assertEqual((b.x_fta_bcfd, b.x_non_fta_bcfd, b.x_nepa_pending), ("3.85", "3.85", "yes"))
        c = t.loc["doe_lng:19-99-LNG"]
        self.assertEqual((c.x_section, c.status, c.x_fta_bcfd, c.x_non_fta_bcfd), ("small_scale", "withdrawn", "", "0.009"))
        self.assertEqual((t.loc["doe_lng:26-59-LNG"].x_section, t.loc["doe_lng:26-59-LNG"].status), ("small_scale", "planned"))
        self.assertEqual(totals, [("lower48", "4.40 Bcf/d", "3.62 Bcf/d")])

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            D.part(["Pondering (12-01-LNG)"])
        bad = Page(1, HEAD + words(130, 64, "No Docket LLC") + words(130, 280, "0.1") + words(130, 400, "n/a"), [100.0, 125, 155])
        with self.assertRaises(RuntimeError):
            D.build([(1, bad)], "u", "r", "2026-09-30")
        self.assertEqual(D.part(["Approved (12-88 -LNG)", "Approved (Design Increase)"]), ("Approved", "12-88-LNG", False))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "gas;lng")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
