"""Session 1496 (chain 158): the explorers offer the rows they draw as a download of their own (GET /api/download with
the filters the route reads: entity, variable, a UTC window), and their method note names each explorer's question, its
tables, its computation, its tolerance and its limits.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheRowsDownload(unittest.TestCase):
    def test_the_frame_offers_the_rows(self):
        t = src("site", "components", "explore", "Explore.tsx")
        self.assertIn("export function rowsHref(r: DrawnRows): string", t)
        self.assertIn('for (const k of ["entity", "variable", "start", "end"] as const)', t)
        self.assertIn("data-rows-download={rows.table}", t)
        self.assertIn("return `/api/download?${q.toString()}`;", t)

    def test_the_route_reads_those_filters(self):
        t = src("site", "lib", "downloadfilter.ts")
        for f in ("entity", "variable", "start, end"):
            self.assertIn(f, t)

    def test_the_peak_premium_gives_its_hub_and_years(self):
        t = src("site", "app", "explore", "ercot-peak-premium", "page.tsx")
        self.assertIn("table, entity: hub, start: `${Math.min(from, to)}-01-01`, end: `${Math.max(from, to) + 1}-01-01`", t)
        self.assertIn("the download does not filter by month", t)

    def test_demand_growth_gives_its_window(self):
        t = src("site", "app", "explore", "demand-growth", "page.tsx")
        self.assertIn('{ table: TABLE, variable: variablesOf(win).join(","),', t)

    def test_interconnection_keeps_the_whole_table(self):
        # its rows are the queue's entities by prefix (like.<iso>:queue_*), which the route's filter does not read
        t = src("site", "app", "explore", "interconnection", "page.tsx")
        self.assertNotIn("rows={rows}", t)
        self.assertIn("like.${iso}:queue_*", t)


class TheMethodNote(unittest.TestCase):
    def test_each_explorer_has_its_parts(self):
        t = src("docs", "methods", "explorers.md")
        for name in ("ERCOT peak premium", "Demand growth", "Interconnection"):
            self.assertIn(f"## {name}", t)
        for part in ("**The question.**", "**The tables.**", "**The computation.**", "**The tolerance.**", "**The limits.**", "**The download.**"):
            self.assertEqual(t.count(part), 3, part)
        self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
