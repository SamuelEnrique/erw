"""Chain 507 (session 8902): the tour's stops for what the site gained from 17 November 2026.

Energy Research Warehouse (ERW). The ruled seven stay first, in the ruled order; a stop for each new view follows them;
a stop whose page is not yet on main is written and held back by its flag (landed: false), and this test fails the day
the flag and the page disagree, so the session that lands the page turns the flag. No network, no browser.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def page_exists(href):
    path = href.split("#")[0].split("?")[0].strip("/")
    return os.path.exists(os.path.join(SITE, "app", *path.split("/"), "page.tsx")) if path else True


@unittest.skipUnless(NODE, "node is not installed")
class NewStops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--input-type=module", "-e",
                            "import { STOPS, RULED_STOPS, NEW_STOPS, HELD_STOPS, MINUTES } from './lib/tour.ts'; console.log(JSON.stringify({ STOPS, RULED_STOPS, NEW_STOPS, HELD_STOPS, MINUTES }));"],
                           cwd=SITE, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        cls.t = json.loads(r.stdout.strip().splitlines()[-1])

    def test_the_ruled_seven_first_then_the_landed_new(self):
        t = self.t
        self.assertEqual(len(t["RULED_STOPS"]), 7)
        self.assertEqual(t["STOPS"][:7], t["RULED_STOPS"])
        self.assertEqual(t["STOPS"][7:], [s for s in t["NEW_STOPS"] if s["landed"]])
        self.assertEqual(t["HELD_STOPS"], [s for s in t["NEW_STOPS"] if not s["landed"]])

    def test_each_new_view_has_a_stop(self):
        hrefs = [s["href"] for s in self.t["NEW_STOPS"]]
        # session 8905 (chain 590): the resource map is the Resources tab of /map
        for h in ("/grid", "/events/elliott-2022", "/demand", "/supply", "/map?tab=resources", "/industry", "/ai-energy"):
            self.assertIn(h, hrefs)

    def test_the_flag_agrees_with_main(self):
        # a landed stop's page is in site/app; a held stop's is not yet (turn the flag when it lands)
        for s in self.t["NEW_STOPS"]:
            self.assertEqual(page_exists(s["href"]), bool(s["landed"]), f"{s['href']}: landed is {s['landed']}")

    def test_a_landed_stop_quotes_only_headings_the_check_reads(self):
        for s in self.t["STOPS"][7:]:
            self.assertTrue(s["headings"], s["href"])
            for q in re.findall(r'"([^"]+)"', s["look"]):
                self.assertIn(q, s["headings"], s["href"])

    def test_the_words(self):
        tour = open(os.path.join(SITE, "lib", "tour.ts"), encoding="utf-8").read()
        page = open(os.path.join(SITE, "app", "tour", "page.tsx"), encoding="utf-8").read()
        for f in (tour, page):
            self.assertNotIn(chr(0x2014), f)
        self.assertNotRegex(tour, r"\d+(\.\d+)? (MW|GW|TWh|percent)")   # no number of a page's own in a stop
        self.assertEqual(self.t["MINUTES"], round(sum(s["seconds"] for s in self.t["STOPS"]) / 60))
        self.assertIn('key={`${i}-${s.href}`}', page)   # two stops open /grid


if __name__ == "__main__":
    unittest.main()
