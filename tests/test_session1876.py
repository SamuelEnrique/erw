"""Session 1876: the policy monitor's faults of 12 November 2026 (docs/reviews/policy-faults-2026-11-11.md), fixed in
site/lib/policymonitor.ts and site/app/policy/Monitor*.tsx.

Energy Research Warehouse (ERW). No request is made, no model is called and nothing is written. The environment is
read, never set.

    PureFunctions  site/scripts/test-policy-monitor.mjs (Node runs site/lib/policymonitor.ts with the site's alias
                   loader): the filter counts (row 2), the sector words (3), the week to the file's last document (4),
                   the steps the floor hides (6), the impact sentence's clause (14), the next step as of today (16) and
                   its key (17), the figure sort by unit (19), the open row's words and links (22), the page of 50
                   (23), the part month's label (26), the figures by month without sums (28), the CSV's columns (29).
    TheView        the components, read from their source (this session does not build): each fixed row drawn as the
                   functions give it, every data-check key kept.
    TheCheck       scripts/check_policy.py follows row 28: the page gives no sum key, the sum check stays for an older file.

    python -m pytest tests/test_session1876.py
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
LOADER = ["--import", "./scripts/alias-register.mjs"]
EM_DASH, EN_DASH = chr(0x2014), chr(0x2013)
MINE = (
    ("site", "lib", "policymonitor.ts"), ("site", "app", "policy", "MonitorView.tsx"), ("site", "app", "policy", "MonitorCalendar.tsx"),
    ("site", "app", "policy", "MonitorCharts.tsx"), ("site", "scripts", "test-policy-monitor.mjs"), ("scripts", "check_policy.py"),
    ("tests", "test_session1876.py"),
)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class PureFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, *LOADER, "scripts/test-policy-monitor.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_the_node_tests_pass(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1000:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2), self.out[-500:])

    def test_each_fixed_row_has_its_node_tests(self):
        for row in (2, 3, 4, 6, 14, 16, 17, 19, 22, 23, 26, 28, 29):
            self.assertRegex(self.out, rf"(?m)^ok   row {row}[ :(]", f"row {row} has a passing node test")


class TheView(unittest.TestCase):
    view = src("site", "app", "policy", "MonitorView.tsx")
    cal = src("site", "app", "policy", "MonitorCalendar.tsx")
    charts = src("site", "app", "policy", "MonitorCharts.tsx")
    lib = src("site", "lib", "policymonitor.ts")

    def test_row_1_both_grid_items_may_shrink_so_the_table_scrolls_in_its_box(self):
        self.assertIn('<section aria-label="Records" className="min-w-0">', self.view)
        self.assertIn('className={`min-w-0 ${showFilters ? "" : "hidden"} lg:block`}', self.view)
        self.assertRegex(self.view, r'<div className="overflow-x-auto">\s*<table className="w-full text-sm">')

    def test_row_2_the_counts_follow_the_filters(self):
        self.assertIn("options(rows, f), [rows, f]", self.view)

    def test_row_3_sectors_as_words_in_the_cell_and_the_chart(self):
        self.assertIn("{sectorWords(r.sector)}", self.view)
        self.assertIn("ss.sectors.map(sectorWords)", self.charts)
        self.assertNotIn('replace(/_/g, " ")', self.view + self.charts)

    def test_rows_4_and_6_the_calendar_reads_the_files_last_date_and_the_hidden_steps(self):
        self.assertIn("calendarOf(rows, today, last)", self.cal)
        self.assertIn("{c.weekFrom} to {c.weekTo}", self.cal)
        self.assertIn("The file's last week", self.cal)
        self.assertIn("None at significance {floor} or more;", self.cal)
        self.assertIn("data-monitor-lift={n}", self.cal)
        self.assertIn("floorHidden(rows, f, today)", self.view)
        self.assertIn("data-check={stepKey(row, step)}", self.cal, "the calendar's keys are kept")

    def test_row_9_the_dates_do_not_break(self):
        self.assertIn('<td className="whitespace-nowrap py-1 pr-3 tabular-nums" data-monitor-date="1">{r.date}</td>', self.view)
        self.assertIn('<span className="whitespace-nowrap">{nx.date}</span>', self.view)

    def test_row_14_the_cell_and_the_csv_cut_the_clause(self):
        self.assertIn("{impactText(r.impact.text)}", self.view)
        self.assertIn("r.impact ? impactText(r.impact.text) : undefined", self.lib)

    def test_rows_16_and_17_the_next_step_as_of_today_keyed_to_its_document(self):
        self.assertIn("const nx = nextOf(r, today)", self.view)
        self.assertIn("data-check={nx.event_id ? stepKey(r, nx) : undefined}", self.view)
        self.assertIn('nx.passed ? ", passed" : ""', self.view)
        self.assertIn("sortRows(filterRows(rows, f), sort[0], sort[1], today)", self.view)

    def test_row_19_the_figure_sort_has_a_unit_tier(self):
        self.assertIn('if (k === "figure") return r.figure ? figureTier(r.figure.unit) : "";', self.lib)

    def test_row_21_the_docs_count_is_a_button_that_opens_the_row(self):
        self.assertRegex(self.view, r'<button type="button" aria-expanded=\{open === r\.id\} aria-controls=\{openId\}')
        self.assertIn("data-record-open={r.id} id={openId}", self.view)
        self.assertIn("e.stopPropagation(); setOpen(open === r.id ? null : r.id)", self.view)

    def test_row_22_the_open_row_has_words_and_links(self):
        self.assertIn("proceedingOf(r.docket)", self.view)
        self.assertIn("historyOf(r).map(", self.view)
        self.assertIn("r.news.map((u, j) => <a key={u} href={u}", self.view)
        self.assertNotIn("news: ${r.news.length}", self.view)
        self.assertNotIn("<li key={h}>{h}</li>", self.view)

    def test_row_23_fifty_rows_then_the_next_fifty(self):
        self.assertIn("shown.slice(0, limit)", self.view)
        self.assertIn("useState(MONITOR_PAGE)", self.view)
        self.assertIn("setLimit(limit + MONITOR_PAGE)", self.view)
        self.assertNotIn("shown.slice(0, 300)", self.view)
        self.assertIn("toCsv(shown, built, today)", self.view, "the CSV keeps every row shown, drawn or not")

    def test_row_26_the_part_month_is_labelled(self):
        self.assertIn("x={monthLabels(bm.months, last)}", self.charts)
        self.assertIn("<MonitorCharts rows={rows} last={last} />", self.view)

    def test_row_28_no_sum_and_the_largest_keyed(self):
        self.assertNotIn("figureSums", self.charts + self.lib)
        self.assertNotIn("sumKey", self.charts + self.lib)
        self.assertIn("data-check={figureKey(m.top)}", self.charts)

    def test_row_29_the_csv_columns(self):
        for c in ("plain_read", "impact_quote", "impact_model", "impact_document", "figure_document", "steps", "next_step_passed"):
            self.assertIn(f'"{c}"', self.lib)

    def test_every_existing_key_is_kept(self):
        self.assertIn("data-check={figureKey(r)}", self.view)
        for k in ("policycal|", "policyfig|"):
            self.assertIn(k, self.lib)

    def test_no_em_or_en_dash(self):
        for p in MINE:
            t = src(*p)
            self.assertNotIn(EM_DASH, t, p)
            self.assertNotIn(EN_DASH, t, p)


class TheCheck(unittest.TestCase):
    def test_check_policy_says_the_sums_are_gone_and_keeps_the_sum_check(self):
        t = src("scripts", "check_policy.py")
        self.assertIn("Since session 1876 (policy faults row 28) the page shows no", t)
        self.assertIn("def check_sum(", t)


if __name__ == "__main__":
    unittest.main()
