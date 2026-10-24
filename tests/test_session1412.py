"""Session 1412 (chain 107): the Flex Alert scorecard's small charts answer a hover.

/grid/caiso/alerts, "Each alert day through the evening": each small chart (session 60's drawing, unchanged, its
arithmetic moved to site/lib/alertDayChart.ts) is drawn by the client chart app/grid/caiso/alerts/DayChart.tsx, which
answers a hover and a tap with the hour, demand served, the model's estimate, its band and the difference, in the
shared charts' card. site/scripts/test-alert-day-chart.mjs holds the drawing to session 60's, string for string, and the
card's figures to the hour's rows; site/scripts/test-grid-render.mjs draws the scorecard. This file runs the first and
holds that the pieces are there.

    python -m unittest tests.test_session1412 -v
"""

import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheChart(unittest.TestCase):
    def test_the_node_test_holds(self):
        r = subprocess.run(["node", "scripts/test-alert-day-chart.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("string for string", r.stdout)
        self.assertIn("every case holds", r.stdout)

    def test_the_page_hands_each_day_to_the_client_chart(self):
        p = src("site", "app", "grid", "caiso", "alerts", "page.tsx")
        self.assertIn('import { DayChart as HoverDayChart } from "./DayChart";', p)
        self.assertIn("<HoverDayChart points={pointsOf(by)} ariaLabel={`${day}: actual and predicted demand through the evening`} />", p)
        self.assertIn("<DayChart rows={hours.get(d.day) ?? []} day={d.day} />", p)
        self.assertIn('data-alerts-days="1"', p)
        self.assertIn("<p className=\"mb-1 text-xs\"><span className=\"font-mono\">{d.day}</span>: cut <V r={val(d, \"reduction_mw\")} /> MW</p>", p)
        # the page no longer draws the svg itself
        self.assertNotIn("<polygon", p.split("function YearChart")[0])

    def test_the_client_chart_takes_the_shared_card(self):
        c = src("site", "app", "grid", "caiso", "alerts", "DayChart.tsx")
        self.assertTrue(c.startswith('"use client";'))
        self.assertIn('import { Card, num } from "@/components/svgchart";', c)
        self.assertIn("export function Card(", src("site", "components", "svgchart.tsx"))
        for w in ("Demand served", "Model&apos;s estimate", "90 percent band", "Estimate less demand", " Pacific", ", an alert hour"):
            self.assertIn(w, c, w)

    def test_the_render_test_has_the_scorecard(self):
        t = src("site", "scripts", "test-grid-render.mjs")
        self.assertIn('"name": "alerts_days on /grid/caiso/alerts", "page": "/grid/caiso/alerts"', t)
        self.assertIn("the scorecard's small charts: one a day of the ranked table", t)
        s = src("site", "scripts", "grid-render-standin.mjs")
        self.assertIn("export async function drawAlerts()", s)
        self.assertIn('["data-alerts-days", () => "alerts_days"]', s)

    def test_the_method_note_says_it(self):
        m = src("docs", "methods", "flex_alert_scorecard.md")
        self.assertIn("## 12. The small charts on hover (chain 107, 24 October 2026)", m)
        self.assertIn("Decisions: the card's figures are the chart's own points, not written figures", m)

    def test_the_bars_caption_is_left_for_the_ruling(self):
        # session 1159's ruling item: the words are not changed here
        self.assertIn("Bars: the estimate, green where demand was below the model, cardinal where above; whiskers: the 90 percent interval.",
                      src("site", "app", "grid", "caiso", "alerts", "page.tsx"))

    def test_no_em_dash(self):
        for parts in [("site", "lib", "alertDayChart.ts"), ("site", "app", "grid", "caiso", "alerts", "DayChart.tsx"),
                      ("site", "app", "grid", "caiso", "alerts", "page.tsx"), ("site", "components", "svgchart.tsx"),
                      ("site", "scripts", "test-alert-day-chart.mjs"), ("site", "scripts", "test-grid-render.mjs"),
                      ("site", "scripts", "grid-render-standin.mjs"), ("docs", "methods", "flex_alert_scorecard.md"),
                      ("tests", "test_session1412.py")]:
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
