"""Audit of the data pages, finding 8, for Samuel's ruling (session 10233, docs/reviews/data-model-audit-2026-11-26.md).
A test only, not for landing: it shows what /data prints of a held table, and changes nothing.

/data draws each listed table's row count through components/Num.tsx with the check key catalogue|<table>|n_rows, and
its first and last day as plain text. Num's heldBy reads no catalogue| key as naming a table, so for every held table
/data lists, the row count is printed where the licenses page's rule ("A number read from a held table is not shown")
would print "license needed". On 26 November: 32 held tables listed, 1,112,934 rows printed between them, 64 dates.

The other choice, not made (it moves 32 printed figures): heldBy reads catalogue|<table>|... as naming <table>, so the
32 cells print "license needed" (and the dates likewise). Default: left as it is; the licenses page's words say what is
shown (wip/audit-data-8)."""
import csv
import json
import os
import re
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TODAY = "2026-11-26"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class HeldTablesRowCountsArePrinted(unittest.TestCase):
    def test_the_count_key_is_not_held_and_held_tables_are_listed_with_counts(self):
        num = src("site", "components", "Num.tsx")
        held_by = num[num.index("export function heldBy"):]
        held_by = held_by[:held_by.index("\n}\n")]
        self.assertNotIn('"catalogue"', held_by)
        self.assertIn("Num check={`catalogue|${r.table_name}|n_rows`}", src("site", "app", "data", "page.tsx"))
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            cov = {r["table"]: r for r in csv.DictReader(f)}
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        rules = live["full"] + live["recent"]["tables"]
        loaded = lambda t: any(re.match(p, t) for p in rules)
        listed = {t for t, r in cov.items() if r["license"] == "public" and t not in set(live["catalogue_hold"])
                  and not (loaded(t) and t in set(live["review_hold"]))}
        st = json.loads(src("site", "data", "license_status.json"))["tables"]
        held = sorted(t for t in listed if st.get(t, {}).get("status") == "license needed" and TODAY >= st[t]["from"])
        rows = sum(int(cov[t]["n_rows"] or 0) for t in held)
        self.assertGreater(len(held), 0)
        self.assertGreater(rows, 0)
        print(f"\nheld tables listed on /data with a printed row count: {len(held)}; rows printed between them: {rows:,}; dates: {2 * len(held)}")


if __name__ == "__main__":
    unittest.main()
