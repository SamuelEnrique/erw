"""Session 690: EIA-861's "empty provenance rows" were a reader's cut at a "#", and the header's Years held line is true.

Energy Research Warehouse (ERW). Session 674's note listed 111 rows of eia861_utility_sales (`eia861:19784:WA:A:BPAT`,
`eia861:40355:AZ:A:AZPS`) with an empty source_url and x_* fields. The file holds them whole: the utilities are named
"Vera Irrigation District #15" and "Maricopa County M W C Dist #1", and a reader with pandas' comment="#" cut each line
at the "#". The connector's header said "Years held: 2025" of a file holding 2015 to 2025; `years_held` now reads the file
whole and names every year. Files built here; no network.

    python -m unittest tests.test_session690 -v
"""

import os
import re
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia861_sales as E  # noqa: E402

COLS = "entity,variable,ts_utc,value,unit,freq,geo,market,node,source,source_url,retrieved_at,vintage,x_utility_number"
ROW = ("eia861:19784:WA:A:BPAT,commercial_customers,{y}-01-01T00:00:00Z,1103.0,count,P1Y,US-WA,,Vera Irrigation District #15,"
       "eia:eia861,https://www.eia.gov/electricity/data/eia861/archive/zip/f861{y}.zip,2026-10-21T17:49:02Z,,19784")


def table(years):
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="")
    f.write("# Energy Research Warehouse (ERW): a test table\n# Years held: 2025\n" + COLS + "\n")
    f.write("\n".join(ROW.format(y=y) for y in years) + "\n")
    f.close()
    return f.name


class YearsHeld(unittest.TestCase):
    def test_every_year_of_the_file_and_the_run(self):
        p = table([2015, 2016, 2024])
        self.assertEqual(E.years_held(p, 2025), [2015, 2016, 2024, 2025])
        os.unlink(p)

    def test_no_file_yet(self):
        self.assertEqual(E.years_held(os.path.join(tempfile.gettempdir(), "no_such_erw_table.csv"), 2025), [2025])

    def test_the_text(self):
        self.assertEqual(E.held_text(list(range(2015, 2026))), "2015 to 2025")
        self.assertEqual(E.held_text([2025]), "2025")
        self.assertEqual(E.held_text([2015, 2017]), "2015, 2017")


class TheHashInAName(unittest.TestCase):
    def test_a_comment_reader_cuts_the_row_and_the_whole_reader_does_not(self):
        p = table([2015])
        cut = pd.read_csv(p, comment="#", dtype=str, keep_default_na=False)
        self.assertEqual(cut.loc[0, "source_url"], "")          # what session 674's note saw
        with open(p, encoding="utf-8") as f:
            n = sum(1 for ln in f if ln.startswith("#"))
        whole = pd.read_csv(p, skiprows=n, dtype=str, keep_default_na=False)
        self.assertEqual(whole.loc[0, "node"], "Vera Irrigation District #15")
        self.assertTrue(whole.loc[0, "source_url"].endswith("f8612015.zip"))
        os.unlink(p)

    def test_the_paths_that_publish_never_cut_at_a_hash(self):
        """The package, the loader, the uploader, the validator and the coverage builder read every table; none may skip
        its header with comment="#" (two of the 2025 utilities, and 44 other tables on 23 October 2026, hold a "#")."""
        pat = re.compile(r"""comment\s*=\s*['"]#['"]""")
        for rel in ["package/src/erw/backends.py", "package/src/erw/api.py", "warehouse/supabase/load.py",
                    "warehouse/redivis/upload.py", "warehouse/validate/erw_validate.py", "warehouse/metadata/build_coverage.py",
                    "warehouse/connectors/iso_prices.py", "warehouse/archive/archive.py"]:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                code = [ln for ln in f if not ln.lstrip().startswith("#")]
            hits = [ln.strip() for ln in code if pat.search(ln) and "never" not in ln]
            self.assertEqual(hits, [], rel)


if __name__ == "__main__":
    unittest.main()
