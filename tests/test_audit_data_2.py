"""Audit of the data pages, finding 2 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): /data says Redivis
holds "Every ERW table, full history, versioned" and that "The full history of every table, and the tables not in the
live set, are on Redivis", and that ERCOT's yearly history is "on Redivis only". Version 1's list for the dataset /data
links (docs/redivis/release-v1/tables.csv) marks most tables held, not yet in the dataset because the account's storage
is full, ERCOT's yearly history among them, which the live set does not load either. A Redivis link's hover said "On
Redivis" for such a table too.

1. The list marks tables held, ERCOT's yearly history among them, and the live set has no rule for it. Passes on main.
2. The fix on this branch, words only: the download note, the Redivis cell's hover and the Access section say Redivis
   holds the tables version 1's list marks in version 1, that a table it marks held is not on Redivis yet, and that
   ERCOT's yearly history is in neither place yet. No figure moves. Fails on main."""
import csv
import os
import re
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class RedivisHoldsWhatItsListMarks(unittest.TestCase):
    def test_the_list_marks_tables_held_and_the_yearly_history_among_them(self):
        with open(os.path.join(ROOT, "docs", "redivis", "release-v1", "tables.csv"), encoding="utf-8", newline="") as f:
            rel = {r["table"]: r for r in csv.DictReader(f)}
        held = [t for t, r in rel.items() if r["in_v1"] == "held"]
        yes = [t for t, r in rel.items() if r["in_v1"] == "yes"]
        self.assertGreater(len(held), len(yes))
        self.assertEqual(rel["ercot_all_hub_prices_history"]["in_v1"], "held")
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        rules = live["full"] + live["recent"]["tables"]
        self.assertFalse(any(re.match(p, "ercot_all_hub_prices_history") for p in rules))

    def test_the_page_says_so(self):
        page = flat(src("site", "app", "data", "page.tsx"))
        for gone in ("Every ERW table, full history, versioned", "The full history of every table, and the tables not in the live set, are on",
                     'title="On Redivis; version 1 is pending release"', "The ERCOT yearly history and the EIA-860M operating and planned generator tables are on Redivis only"):
            self.assertNotIn(gone, page)
        self.assertIn("marks the table in version 1; a table the list marks held is not on Redivis yet (the account&apos;s storage is full). On Redivis, version 1 is pending release.", page)
        self.assertIn("On Redivis where version 1's list marks the table in version 1, not yet where it marks it held; version 1 is pending release", page)
        self.assertIn("The tables version 1&apos;s list marks in version 1, full history, versioned:", page)
        self.assertIn("the ERCOT yearly history is not in the live set and, version 1&apos;s list marking it held, not yet on the dataset linked here.", page)


if __name__ == "__main__":
    unittest.main()
