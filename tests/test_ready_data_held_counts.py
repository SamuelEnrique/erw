"""wip/ready-data-held-counts (session 11406, chain 770, part C): the other choice of the data pages audit of
26 November, finding 8 (docs/reviews/data-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main /data prints the row count (catalogue|<table>|n_rows) and the first and last day of every held table it lists,
since components/Num.tsx's heldBy reads no catalogue| key as naming a table. On this branch heldBy does, and /data
draws a held table's two dates through it: the cells read "license needed". Counted on today's coverage.csv and
license record (the audit's own count, carried from tests/test_audit_data_9.py on wip/audit-data-9): the tables, the
rows and the dates no longer printed are printed by this test. The licenses page says it."""
import csv
import datetime as dt
import json
import os
import re
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class HeldTablesCountsAndDatesAreHeld(unittest.TestCase):
    def test_the_key_is_held_and_the_dates_ask(self):
        num = src("site", "components", "Num.tsx")
        held_by = num[num.index("export function heldBy"):]
        held_by = held_by[:held_by.index("\n}\n")]
        self.assertIn('else if (head === "catalogue") table = p[1] ?? "";', held_by)
        page = src("site", "app", "data", "page.tsx")
        self.assertIn("Num check={`catalogue|${r.table_name}|n_rows`}", page)
        self.assertIn("{heldBy(`catalogue|${r.table_name}|ts_min`) ? LICENSE_NEEDED : day(r.ts_min)}", page)
        self.assertIn("{heldBy(`catalogue|${r.table_name}|ts_max`) ? LICENSE_NEEDED : day(r.ts_max)}", page)
        self.assertIn("read &ldquo;license needed&rdquo; too", src("site", "app", "data", "licenses", "page.tsx"))

    def test_how_many(self):
        today = dt.datetime.now(dt.timezone.utc).date().isoformat()
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            cov = {r["table"]: r for r in csv.DictReader(f)}
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        rules = live["full"] + live["recent"]["tables"]
        loaded = lambda t: any(re.match(p, t) for p in rules)  # noqa: E731
        listed = {t for t, r in cov.items() if r["license"] == "public" and t not in set(live["catalogue_hold"])
                  and not (loaded(t) and t in set(live["review_hold"]))}
        st = json.loads(src("site", "data", "license_status.json"))["tables"]
        held = sorted(t for t in listed if st.get(t, {}).get("status") == "license needed" and today >= st[t]["from"])
        rows = sum(int(cov[t]["n_rows"] or 0) for t in held)
        print(f"held tables listed on /data: {len(held)}; row counts now 'license needed': {len(held)} ({rows:,} rows); dates: {2 * len(held)}")
        self.assertGreater(len(held), 0)


if __name__ == "__main__":
    unittest.main()
