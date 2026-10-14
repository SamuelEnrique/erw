"""Session 272: the 341 large-load statements, public.

Energy Research Warehouse (ERW). The owner's ruling of 14 October 2026: large_load_public is public (facts with a link,
no quoted text). Held here: the builder's header and source registry say public; coverage lets a public selection of
an internal table stand (and only that table); the live set loads it and still holds the verdicts; the one read helper
the datacenter page needs reads it through lib/supabase.ts; the verdicts table stays internal. No request is made.
"""

import csv
import os
import re
import sys
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (("warehouse", "derived"), ("warehouse", "metadata"), ("warehouse", "connectors")):
    sys.path.insert(0, os.path.join(ROOT, *p))
import build_coverage as bc  # noqa: E402
import large_load_public as L  # noqa: E402

EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRuling(unittest.TestCase):
    def test_the_builder_says_public_and_the_verdicts_stay_internal(self):
        code = src("warehouse", "derived", "large_load_public.py")
        self.assertIn('"License: public, by the owner\'s ruling of 14 October 2026 (session 272)', code)
        self.assertIn("License: internal. It lists the documents of two internal tables", code)
        self.assertIn('license="public", tables=[PUBLIC]),  # session 272', code)
        self.assertIn('license="internal", tables=[VERDICTS])', code)

    def test_the_source_registry_and_coverage_say_public(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "sources.csv"), encoding="utf-8") as f:
            lic = {r["source"]: r["license"] for r in csv.DictReader(f)}
        self.assertEqual((lic[L.SOURCE_PUBLIC], lic[L.SOURCE_VERDICTS]), ("public", "internal"))
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8") as f:
            cov = {r["table"]: r for r in csv.DictReader(f)}
        self.assertEqual(cov[L.PUBLIC]["license"], "public")
        self.assertEqual(cov[L.VERDICTS]["license"], "internal")
        self.assertEqual(cov[L.PUBLIC]["n_rows"], "341")

    def test_only_this_table_may_be_public_over_an_internal_input(self):
        self.assertEqual(set(bc.PUBLIC_SELECTIONS), {"large_load_public"})
        rows = [dict(table="large_load_statements", license="internal", _derived_from=None),
                dict(table="large_load_public", license="public", _derived_from=["large_load_statements"]),
                dict(table="other_selection", license="public", _derived_from=["large_load_statements"])]
        with self.assertRaises(ValueError):
            bc.apply_derived([dict(r) for r in rows])                                # any other table still fails
        out = bc.apply_derived([dict(r) for r in rows[:2]])
        self.assertEqual([r["derived"] for r in out], ["no", "yes"])

    def test_the_live_set_loads_it_and_holds_the_verdicts(self):
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        self.assertIn("^large_load_public$", live["full"])
        self.assertNotIn(L.PUBLIC, live["catalogue_hold"])
        self.assertNotIn(L.SOURCE_PUBLIC, live["sources_hold"])
        self.assertIn(L.VERDICTS, live["catalogue_hold"])
        self.assertIn(L.SOURCE_VERDICTS, live["sources_hold"])


class TheReadHelper(unittest.TestCase):
    def test_one_read_of_the_events_table_by_the_anon_route(self):
        ts = src("site", "lib", "largeloadpublic.ts")
        self.assertIn('import "server-only";', ts)
        self.assertIn('import { HOURLY, rest } from "./supabase";', ts)
        self.assertEqual(len(re.findall(r"export async function", ts)), 1)
        self.assertIn('rest<LargeLoadStatement>("events", query, HOURLY, 2_000)', ts)
        self.assertIn("table_name: `eq.${TABLE}`", ts)
        self.assertIn('query["extra->>grid"] = `eq.${grid}`', ts)
        # every column it asks for is a column of the table; none is a column of the document's words
        cols = re.findall(r'"([a-z_]+)"', ts.split("const TOP = ", 1)[1].split("/**", 1)[0])
        self.assertLessEqual(set(cols), set(L.PUBLIC_COLS))
        self.assertNotIn("stage_as_worded", ts)
        self.assertNotIn("SUPABASE_SERVICE", ts)

    def test_no_em_dash(self):
        for rel in ("site/lib/largeloadpublic.ts", "docs/methods/large_load_public.md", "warehouse/derived/large_load_public.py",
                    "warehouse/metadata/build_coverage.py", "warehouse/supabase/live_set.yaml", "tests/test_session272.py"):
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
