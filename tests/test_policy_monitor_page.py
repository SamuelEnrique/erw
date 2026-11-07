"""Sessions 3123 and 3124 (chain 169): the policy monitor's view read from its code, since this window never builds:
the layout at 390 and at 1280, and what a strict compile needs. The gate's build and snapshot are the real proof.

    .venv/Scripts/python.exe -m pytest -q tests/test_policy_monitor_page.py
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, "site", *p), encoding="utf-8") as f:
        return f.read()


class Layout(unittest.TestCase):
    view = src("app", "policy", "MonitorView.tsx")

    def test_inputs_left_results_right_at_1280_and_the_records_first_at_390(self):
        self.assertIn('className="grid gap-4 lg:grid-cols-[14rem_1fr]"', self.view)
        self.assertRegex(self.view, r'<button type="button" className="[^"]*lg:hidden"[^>]*aria-expanded=\{showFilters\}')
        self.assertIn('className={`${showFilters ? "" : "hidden"} lg:block`}', self.view)
        self.assertLess(self.view.index("data-monitor-filters-toggle"), self.view.index('<section aria-label="Records">'))

    def test_the_table_scrolls_inside_itself_never_the_page(self):
        self.assertRegex(self.view, r'<div className="overflow-x-auto">\s*<table className="w-full text-sm">')
        self.assertIn("<caption className=\"sr-only\">", self.view)
        cal = src("app", "policy", "MonitorCalendar.tsx")
        self.assertIn('className="mb-4 grid gap-4 md:grid-cols-2"', cal)
        self.assertEqual(cal.count("max-h-72 overflow-y-auto"), 2, "each list scrolls in its own box")

    def test_every_hover_explains_and_every_figure_shown_is_keyed(self):
        self.assertIn("data-check={figureKey(r)}", self.view)
        self.assertIn("data-check={stepKey(row, step)}", src("app", "policy", "MonitorCalendar.tsx"))
        self.assertIn("data-check={sumKey(s)}", src("app", "policy", "MonitorCharts.tsx"))
        for h in re.findall(r'(?<=\n  )(\w+): \["([^"]+)", "([^"]+)"\]', self.view):
            self.assertTrue(h[2].endswith("."), f"the hover of {h[0]} is a sentence")


class StrictCompile(unittest.TestCase):
    def test_the_sort_never_compares_a_string_with_a_number(self):
        lib = src("lib", "policymonitor.ts")
        self.assertIn('typeof x === "number" && typeof y === "number" ? (x < y ? -1 : 1) : String(x) < String(y) ? -1 : 1', lib)

    def test_the_chart_series_are_typed(self):
        charts = src("app", "policy", "MonitorCharts.tsx")
        self.assertIn("import { CategoryChart, type CatSeries } from \"@/components/svgchart\";", charts)
        self.assertEqual(charts.count("(s, i): CatSeries =>"), 2)


if __name__ == "__main__":
    unittest.main()
