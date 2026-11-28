"""Audit of the data pages, finding 8 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): /data/licenses says
"A number read from a held table is not shown." /data draws each listed table's row count with the check key
catalogue|<table>|n_rows, which components/Num.tsx does not read as naming a held table, and its first and last day
plainly, so the row counts and dates of the held tables it lists are printed; /data/faults prints the register's counts
of ISO-NE's and NYISO's missing intervals.

1. Num's heldBy holds no catalogue| key; the faults register's ISO-NE and NYISO entry counts days and hours. Passes on main.
2. The fix on this branch, words only: the licenses page says a number read from a held table's values is not shown, and
   that what describes the table (its name, row count and first and last day on /data, the faults register's counts of
   its source's gaps) is. Whether to hold those too is for Samuel's ruling (wip/audit-data-9). Fails on main."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class WhatOfAHeldTableIsShown(unittest.TestCase):
    def test_the_catalogue_counts_are_not_held(self):
        num = src("site", "components", "Num.tsx")
        body = num[num.index("export function heldBy"):]
        self.assertIn('"catalogue"', body[:body.index("\n}\n")])   # wip/ready-data-held-counts: the key is held
        self.assertIn("Num check={`catalogue|${r.table_name}|n_rows`}", src("site", "app", "data", "page.tsx"))
        faults = src("warehouse", "faults", "faults.yaml")
        entry = faults[faults.index("id: iso_realtime_price_gaps"):]
        entry = entry[:entry.index("\n  - id:")]
        self.assertTrue(re.search(r"\d+ days", entry))

    def test_the_licenses_page_says_so(self):
        page = flat(src("site", "app", "data", "licenses", "page.tsx"))
        self.assertNotIn("<li>A number read from a held table is not shown.", page)
        self.assertIn("A number read from a held table&apos;s values is not shown.", page)
        self.assertIn("Its row count and its first and last day on <Link href=\"/data\">Data</Link> read &ldquo;license needed&rdquo; too", page)   # wip/ready-data-held-counts


if __name__ == "__main__":
    unittest.main()
