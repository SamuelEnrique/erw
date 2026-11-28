"""Audit of /equities, finding 8 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): every download of
/equities named, in its provenance line, a builder that does not exist.

A company's day-by-day CSV (/equities/rows) and the list of every company (/equities/list), with their Python and
Stata readers, said "written by warehouse/derived/equity_pages.py" (site/lib/equities.ts seriesCsv and listCsv). The
builder is warehouse/derived/equity_page_files.py; no file equity_pages.py has been in the repository. A reader who
follows the provenance, as the ERW's rule 5 asks every number to allow, finds nothing.

1. The builder the files name is there, and equity_pages.py is not (passes on main).
2. The fix on this branch (fails on main): no site file names equity_pages.py; the two CSV headers name
   equity_page_files.py. No figure moves."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class Provenance(unittest.TestCase):
    def test_the_builder(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "derived", "equity_page_files.py")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "warehouse", "derived", "equity_pages.py")))

    def test_the_downloads_name_it(self):
        src = open(os.path.join(SITE, "lib", "equities.ts"), encoding="utf-8").read()
        self.assertEqual(src.count("written by warehouse/derived/equity_page_files.py"), 2)
        for rel in ("lib/equities.ts", "lib/equitiesfiles.ts", "app/equities/page.tsx", "app/equities/view.tsx",
                    "app/equities/reader.ts"):
            self.assertNotIn("equity_pages.py", open(os.path.join(SITE, rel), encoding="utf-8").read(), rel)


if __name__ == "__main__":
    unittest.main()
