"""Audit of the tour, finding 9 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the tour's line in
site/lib/pages.ts (drawn on /about and /data) said "Twelve stops for a first visit, about eight minutes"; the path holds
the ruled seven and nine later stops, 16, of 595 seconds ("about 10 minutes" on the tour itself). The tour's lead named
five of the nine later stops, and neither named "Where energy goes", "Energy per AI query", "Every state" or "Grid
conditions".

1. The stops and their seconds, read from site/lib/tour.ts as data. Passes on main.
2. The fix on this branch, words only: the line keeps no count it cannot keep, and both name the four. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


STOP = re.compile(r'href: "([^"]+)", title: "([^"]+)", seconds: (\d+)(?:, landed: (true|false))?')


class TheTourCount(unittest.TestCase):
    def test_sixteen_stops_ten_minutes(self):
        t = src("site", "lib", "tour.ts")
        ruled = STOP.findall(t[t.index("export const RULED_STOPS"):t.index("export const NEW_STOPS")])
        later = [x for x in STOP.findall(t[t.index("export const NEW_STOPS"):t.index("export const STOPS")]) if x[3] != "false"]
        self.assertEqual((len(ruled), len(later)), (7, 9))
        secs = sum(int(x[2]) for x in ruled + later)
        self.assertEqual(secs, 595)
        self.assertEqual(round(secs / 60), 10)

    def test_the_words_name_every_later_stop(self):
        line = re.search(r'href: "/tour", label: "The tour", line: "([^"]+)"', src("site", "lib", "pages.ts")).group(1)
        lead = src("site", "app", "tour", "page.tsx")
        self.assertNotIn("Twelve stops", line)
        self.assertNotIn("eight minutes", line)
        for words in (line, lead):
            self.assertIn("its regions, a storm across it, demand, trade, the resource map, where energy goes, the energy of AI, every state and grid conditions", words)


if __name__ == "__main__":
    unittest.main()
