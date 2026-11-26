"""Audit of the data pages, finding 1 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): /data's lead says
"Every public table in the ERW ... with the source report and retrieval time of every row". The catalogue it draws is
coverage.csv less the live set's catalogue_hold, and less the tables loaded under review_hold (warehouse/supabase/
load.py, site/lib/data.ts): on 26 November 111 of the 591 public tables. And some listed tables carry no retrieved_at
column (energy_deals, news_index), so a row's retrieval time is the header's.

1. Public tables of coverage.csv are under catalogue_hold, and a listed table has no retrieved_at column. Passes on main.
2. The fix on this branch, words only: the lead says "the public tables in the site's live catalogue", where the
   retrieval time is (the header lines, and each row that has the columns), and that a public table the live set holds
   back is not listed while coverage.csv lists every table. No figure moves. Fails on main."""
import csv
import os
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def columns(table):
    with open(os.path.join(ROOT, "warehouse", "output", table + ".csv"), encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return next(csv.reader([line]))


class TheLeadSaysWhatIsListed(unittest.TestCase):
    def test_public_tables_are_held_back_and_some_rows_carry_no_retrieval_time(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            public = {r["table"] for r in csv.DictReader(f) if r["license"] == "public"}
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        self.assertGreater(len(public & set(live["catalogue_hold"])), 0)
        for t in ("energy_deals", "news_index"):
            self.assertIn(t, public)
            self.assertNotIn("retrieved_at", columns(t))

    def test_the_lead_says_so(self):
        page = flat(src("site", "app", "data", "page.tsx"))
        self.assertNotIn("Every public table in the ERW.", page)
        self.assertNotIn("retrieval time of every row", page)
        self.assertIn("The public tables in the site&apos;s live catalogue.", page)
        self.assertIn("with the source report and retrieval time in its header lines, and on each row where the table has the columns", page)
        self.assertIn("Nor is a public table the live set holds back", page)
        self.assertIn("lists every table of the warehouse.", page)


if __name__ == "__main__":
    unittest.main()
