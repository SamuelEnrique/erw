"""Ruling alternative 2 of /events (session 7712, 17 November 2026, branch wip/alt-events-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-events-2026-11-17.md, line 2): on the Elliott
page, add a second column with temperature to PJM's estimate for each day? On this branch the table of each day's estimate
has a column "Controlling for temperature" on that page (components/EventStudy.tsx dayTemp, the page passes it; the key
es|...|day_temp|<day>|est, which scripts/check-values.mjs recomputes), with a hover saying it is an extrapolation. Pinned
with the site's own lib/eventstudy.ts and the page drawn with its own component on the replication's public rows
(site/scripts/alt-events-figures.mjs): every day moves, most of them up: 23 December 619,177 to 1,419,061 MWh, 24 December
909,793 to 2,225,024, 29 December 123,403 to 558,439; the pooled figure 387,000 to 134,171 MWh a day. On main's hold the
eleven cells draw "license needed" with the rest of the EIA-930 figures (ruling alternative 1 draws them); with the hold
stood aside (EVENTS_DRAW_UNHELD=1) they draw as numbers. No other page gains the column.

    python -m unittest tests.test_alt_events_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def figures(unheld):
    env = dict(os.environ)
    env.pop("EVENTS_DRAW_UNHELD", None)
    if unheld:
        env["EVENTS_DRAW_UNHELD"] = "1"
    p = subprocess.run(["node", "--import", "./scripts/events-page-register.mjs", "scripts/alt-events-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=600, env=env)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


class EachDayWithTemperature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.u = figures(True)
        cls.h = figures(False)

    def test_the_days(self):
        d = self.u["days"]
        got = {k: (round(d[k][0]), round(d[k][1])) for k in ("2022-12-23", "2022-12-24", "2022-12-29")}
        # 619,176.4999...: the site rounds it to 619,176, the impact file (the Python twin) printed 619,177; half a unit apart
        self.assertEqual(got, {"2022-12-23": (619176, 1419061), "2022-12-24": (909793, 2225024), "2022-12-29": (123403, 558439)})
        self.assertEqual(len(d), 11)

    def test_the_pooled_figure(self):
        self.assertEqual([round(v) for v in self.u["pooled"]], [387000, 134171])

    def test_the_page_draws_the_column(self):
        self.assertEqual(self.u["drawn"], {"numbers": 11, "tip": True, "held": 0})
        self.assertEqual((self.h["drawn"]["numbers"], self.h["drawn"]["tip"]), (0, True))
        self.assertFalse(self.u["uriHasColumn"])


if __name__ == "__main__":
    unittest.main()
