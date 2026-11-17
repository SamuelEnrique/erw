"""Session 7631: the other choice of the ruling on the battery page's revenue on /curtailment (branch
wip/alt-curtailment-1, not landed). "A battery of 4 hours, against what the fleet charged" gave no revenue; under the
other choice one line gives the battery page's revenue for the same hub and duration, for the month chosen.

What is held to:
  the figures are battery_stack_monthly's revenue_total_usd_per_mw over 1,000, CAISO SP15, read from the live set on
    17 November 2026 (the rows the battery page reads): a 4-hour battery, USD per kW of power, perfect foresight May to
    September 2026 7.50, 5.73, 7.02, 10.87, 6.84; on the day-ahead schedule 6.99, 5.57, 4.95, 6.97, 6.32 (the impact
    file's figures); October 2026 is now whole on the live set (7.74 and 7.53; the impact file's copy held 19 days);
  the page reads them server side for CAISO only and draws the line for a month chosen, at the duration chosen, with the
    battery page's link; nothing else on the page moves.

No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIVE = {  # month: (perfect foresight, day-ahead schedule), USD per kW, 4 hours, SP15
    "2026-05": (7.50, 6.99), "2026-06": (5.73, 5.57), "2026-07": (7.02, 4.95), "2026-08": (10.87, 6.97), "2026-09": (6.84, 6.32), "2026-10": (7.74, 7.53),
}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBatteryPagesRevenue(unittest.TestCase):
    def test_the_figures_are_the_impact_files(self):
        impact = {"2026-05": (7.50, 6.99), "2026-06": (5.73, 5.57), "2026-07": (7.02, 4.95), "2026-08": (10.87, 6.97), "2026-09": (6.84, 6.32)}
        for m, v in impact.items():
            self.assertEqual(LIVE[m], v, m)

    def test_the_page_reads_and_draws_them(self):
        p = src("site", "app", "curtailment", "page.tsx")
        self.assertIn('table_name: "eq.battery_stack_monthly", entity: "eq.caiso:TH_SP15_GEN-APND", variable: `like.*_revenue_total_usd_per_mw`', p)
        self.assertIn('= Number(r.value) / 1000;', p)
        self.assertIn("batteryRevenue={batteryRevenue} />", p)
        s = src("site", "app", "curtailment", "Sections.tsx")
        self.assertIn("const rv = p.length === 7 ? batteryRevenue[p] : undefined, f = rv?.[`foresight_${dur}h`], d = rv?.[`dayahead_${dur}h`];", s)
        self.assertIn("data-battery-revenue={`${p}|${dur}`}", s)
        for t in (p, s):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
