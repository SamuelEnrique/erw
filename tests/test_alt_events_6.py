"""Ruling alternative 6 of /events (session 7712, 17 November 2026, branch wip/alt-events-6; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-events-2026-11-17.md, line 6): on the September
2022 California heat page, each airport's hottest day in the window? On this branch a sentence gives them from the event
table's NOAA rows (site/app/events/caiso-heat-2022/page.tsx, temp_max_f of noaa:SAC and noaa:LAX): Sacramento 114.08 F on
5 September 2022, Los Angeles 100.94 F on 9 September 2022. Two figures added; nothing that stands moves. Pinned with the
page drawn with its own code on the replication's public rows (site/scripts/alt-events-figures.mjs). Under main's hold
of 21 October the two figures read "license needed", as every figure of a row of event_window_daily that names no grid
does; with the hold stood aside (EVENTS_DRAW_UNHELD=1) they draw as numbers.

    python -m unittest tests.test_alt_events_6 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def drawn(unheld):
    env = dict(os.environ)
    env.pop("EVENTS_DRAW_UNHELD", None)
    if unheld:
        env["EVENTS_DRAW_UNHELD"] = "1"
    p = subprocess.run(["node", "--import", "./scripts/events-page-register.mjs", "scripts/alt-events-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=600, env=env)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


class TheAirports(unittest.TestCase):
    def test_the_hottest_days(self):
        f = drawn(True)
        self.assertEqual((f["sac"], f["lax"], f["held"]), (["2022-09-05T00:00:00Z", "114.08"], ["2022-09-09T00:00:00Z", "100.94"], 0))
        self.assertIn("at Sacramento was 2022-09-05, 114.08 F", f["sentence"])
        self.assertIn("at Los Angeles 2022-09-09, 100.94 F", f["sentence"])

    def test_under_mains_hold(self):
        self.assertEqual(drawn(False)["held"], 2)


if __name__ == "__main__":
    unittest.main()
