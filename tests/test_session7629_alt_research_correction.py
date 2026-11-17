"""Session 7629: the other choice of the ruling on the stored chart of 12 November on /research (branch
wip/alt-research-2, not landed). "Today's chart" of 12 November 2026 says Wyoming's August gas generation broke July
2024's record (765,381 MWh), where July 2026 broke it first; under the other choice a correction line is drawn under the
stored record, the record itself left as stored.

What is held to:
  the record cell the correction states: 765,381 MWh (July 2024) to 1,034,451 MWh (July 2026), +269,070, +35.2 percent;
    August 2026's 1,060,504 MWh above it by 26,053 MWh (2.5 percent), not 295,122 (38.6 percent) as stored (the impact
    file's figures; July 2026 is the data machine's copy of eia_state_generation_monthly);
  the stored fact is unchanged, and the line is drawn only under the record of its date.

No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheCorrectionLine(unittest.TestCase):
    def test_the_arithmetic(self):
        self.assertEqual(1034451 - 765381, 269070)
        self.assertEqual(f"{100 * 269070 / 765381:.1f}", "35.2")
        self.assertEqual(1060504 - 1034451, 26053)
        self.assertEqual(f"{100 * 26053 / 1034451:.1f}", "2.5")
        self.assertEqual(f"{100 * 295123 / 765381:.1f}", "38.6")

    def test_the_page(self):
        with open(os.path.join(ROOT, "site", "app", "research", "page.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('"2026-11-12": "Correction: the record until now was 1,034,451 MWh, in July 2026, not July 2024\'s 765,381 MWh, so August 2026 was above it by 26,053 MWh (2.5 percent)', s)
        self.assertIn("{CORRECTIONS[today.date] ? <p className=\"text-sm\" data-today-correction={today.date}>", s)
        self.assertIn('<p className="lead-fact" data-today-fact="1">{today.fact}</p>', s)
        self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
