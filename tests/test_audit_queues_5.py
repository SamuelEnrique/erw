"""Audit of the interconnection queue, finding 4 (session 10213, docs/reviews/queues-model-audit-2026-11-26.md): the
headline "Active capacity" said "The most entered in 2025." Its function (peakActive, site/lib/queues.ts) gives the year
of most MW still active. In the default view the most MW entered in 2023 (861,011) and the most requests in 2022
(3,435); in 54 of the 76 views the year of most MW still active is not both the year of most MW entered and of most
requests entered. The bar hovers also read "in 1 requests" (155 years of the file's views). No figure moves.

1. Through the page's file: the default view's year of most MW still active is 2025, of most MW entered 2023, of most
   requests entered 2022. Passes on main.
2. The fix on this branch, words only: the note says which year it names; a bar of one request says "1 request".
   Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheHeadlineSaysWhichYear(unittest.TestCase):
    def test_the_three_years_differ_in_the_default_view(self):
        ys = json.loads(src("site", "data", "queues.json"))["views"]["us|all"]["years"]
        top = lambda k: max(ys.items(), key=lambda x: x[1][k])[0]
        self.assertEqual((top("mw_active"), top("mw_entered"), top("requests_entered")), ("2025", "2023", "2022"))

    def test_the_words(self):
        page = src("site", "app", "queues", "page.tsx")
        self.assertNotIn("The most entered in {peak.year}.", page)
        self.assertIn("More of it entered in {peak.year} than in any other year (by the MW still active; the year in which the most MW or the "
                      "most requests entered can be another).", page)
        self.assertIn('${whole(d.row!.requests_active)} ${d.row!.requests_active === 1 ? "request" : "requests"}', page)
        self.assertIn("export function peakActive(view: View)", src("site", "lib", "queues.ts"))
        self.assertNotIn(chr(0x2014), page)


if __name__ == "__main__":
    unittest.main()
