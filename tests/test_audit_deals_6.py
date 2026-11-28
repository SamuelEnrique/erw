"""Audit of the energy deal tracker, finding 6 (session 10215, docs/reviews/deals-model-audit-2026-11-26.md): the
comparables (by deal type, the default) show a median size wherever three deals of a group state one, and say nothing of
what a group mixes. On the rows of 12 November 2026 the power purchases' median, 348 MW of 12, runs over a 43.5 MW solar
PPA to a 3,600 MW nuclear one; the acquisitions' 892 MW is one gas plant's, between a 65 MW datacenter and a 5,400 MW
portfolio; 38,147 of the 40,297 MW stated name no country. Decision 6 keeps a floor of three so that one deal's terms do
not read as a market's, yet a median of three is the middle deal's own figure.

1. Through the page's library (site/lib/deals2.ts, run by Node): a median of three is the middle deal's figure, of any mix,
   and fewer than three give none. Passes on main.
2. The fix on this branch, words only: the chart's note says a group mixes technologies, countries and stages and that a
   median of three is one deal's figure. Fails on main. Raising the floor (to five: 13 medians to 8) is a figure, for the
   owner's ruling, not made here."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "deals2.ts").replace("\\", "/")
JS = """
const D = await import(%s);
console.log(JSON.stringify([D.medianOf([43.5, 3600, 348]), D.medianOf([43.5, 702, 348, 2800, 3600]), D.medianOf([43.5, 3600])]));
""" % json.dumps(LIB)


def flat(s):
    return " ".join(s.split())


class TheComparablesMix(unittest.TestCase):
    def test_a_median_of_three_is_one_deals_figure(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        # session 11408 (wip/ready-deals-median-five): three give none; a median of five is still the middle deal's figure
        self.assertEqual(json.loads(out.stdout.strip().splitlines()[-1]), [None, 702, None])

    def test_the_note_says_what_a_group_mixes(self):
        with open(os.path.join(ROOT, "site", "app", "deals", "comparables", "view.tsx"), encoding="utf-8") as f:
            v = flat(f.read())
        self.assertIn("A group holds every technology, country and stage of its kind: by deal type, a power purchase&apos;s median sets a solar "
                      "plant of tens of MW beside a nuclear plant of thousands, and a median of five is the middle deal&apos;s own figure, not a "
                      "market&apos;s.", v)


if __name__ == "__main__":
    unittest.main()
