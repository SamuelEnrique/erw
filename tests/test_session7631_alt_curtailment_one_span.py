"""Session 7631: the other choice of the ruling on ERCOT's shares on /curtailment (branch wip/alt-curtailment-2, not
landed). ERCOT's view gave the share of output below the limit over more than one span (the head's whole days, and each
whole month); under the other choice only the head's share stays.

What is held to (site/data/curtailment/ercot.json, built 15 November 2026):
  the head's share over the whole days stays: 6.23 percent over 47 days (28 September to 14 November 2026);
  the month's share leaves the view: October 2026's 6.05 percent (the head's third number, the months' line under the
    table of complete months, and the Texas table's month row); the months' MWh stay;
  the code: ONE_SPAN in Sections.tsx; the head's whole-month number not drawn; the months' share cell a blank that says why.

No request, no model call."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class OneSpan(unittest.TestCase):
    def test_the_figures(self):
        with open(os.path.join(ROOT, "site", "data", "curtailment", "ercot.json"), encoding="utf-8") as f:
            e = json.load(f)
        self.assertEqual((e["whole_days"], f"{e['window']['both']['share_pct']:.2f}"), (47, "6.23"))
        self.assertEqual(f"{e['months']['2026-10']['both']['share_pct']:.2f}", "6.05")

    def test_the_code(self):
        s = src("site", "app", "curtailment", "Sections.tsx")
        self.assertIn("export const ONE_SPAN = true;", s)
        self.assertIn('ONE_SPAN || r.both.share_pct === null ? "" : <N key="p" k={`tx|${m}|share`}>', s)
        p = src("site", "app", "curtailment", "page.tsx")
        self.assertIn("{ONE_SPAN ? null : (() => { const wm = ercotWholeMonths(ercot).at(-1)", p)
        self.assertIn('{estimate && !ONE_SPAN ? <p className="mt-3 text-sm">', p)
        self.assertIn('if (estimate && ONE_SPAN) return <Blank words="over the head\'s days only"', p)
        for t in (s, p):
            self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()
