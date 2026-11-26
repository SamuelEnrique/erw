"""Session 292: the tour, guided (Samuel's ruling 11a of 14 October 2026).

Energy Research Warehouse (ERW). No network, no model, no browser (site/scripts/check-tour.mjs reads the pages).
A guided path: the tour's first page and one page a stop (/tour/1 to /tour/7), each with the progress bar (one shared
component, app/tour/TourBar.tsx), Back and Next; the stops at today's addresses (the three tools, the Grid, Research, the
price board, the Digest); a heading check that fails when a quoted heading is gone.

    python -m unittest tests.test_session292 -v
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


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
class TheStops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([NODE, "--input-type=module", "-e", "import { STOPS, MINUTES } from './lib/tour.ts'; console.log(JSON.stringify({ STOPS, MINUTES }));"],
                           cwd=SITE, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        cls.t = json.loads(r.stdout.strip().splitlines()[-1])

    def test_todays_addresses_in_the_ruled_order(self):
        # chain 507 (session 8902): the ruled seven first, in the ruled order; the stops of what the site gained from 17
        # November 2026 follow them (tests/test_session8902_tour.py), so the path is longer than five minutes
        # session 9601 (chain 620): the fourth stop, written "One grid at a time, ERCOT first", opens ERCOT's own
        # address; /grid alone has opened on the Lower 48 since session 299, where two of the stop's headings are not
        self.assertEqual([s["href"] for s in self.t["STOPS"]][:7],
                         ["/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power", "/grid?grid=ercot", "/research", "/board", "/digest"])
        self.assertEqual(self.t["MINUTES"], round(sum(s["seconds"] for s in self.t["STOPS"]) / 60))

    def test_each_quoted_heading_is_one_the_check_reads(self):
        for s in self.t["STOPS"]:
            self.assertTrue(s["headings"], s["href"])
            # session 9601: a stop may quote a fold and a heading inside it (`inFold`), which the check reads too
            read = s["headings"] + ([s["inFold"]["fold"]] + s["inFold"]["headings"] if s.get("inFold") else [])
            for q in re.findall(r'"([^"]+)"', s["look"]):
                self.assertIn(q, read, f"{s['href']}: the look quotes {q!r}, which the check does not read")

    def test_no_old_address(self):
        for s in self.t["STOPS"]:
            self.assertNotIn(s["href"], ("/network", "/grid/ercot", "/mix", "/emissions"))   # each answers by redirect today


class ThePath(unittest.TestCase):
    def test_one_shared_bar_on_every_stop(self):
        bar = src("site", "app", "tour", "TourBar.tsx")
        self.assertIn("export function TourBar({ at }: { at: number })", bar)
        self.assertIn('<Link href={back} rel="prev">Back</Link>', bar)
        self.assertIn('<Link href={next} rel="next">Next</Link>', bar)
        self.assertIn("block flex-1 py-2", bar)                              # a 24 px target around an 8 px segment
        stop = src("site", "app", "tour", "[stop]", "page.tsx")
        self.assertIn("<TourBar at={n} />", stop)
        self.assertIn("data-tour-open", stop)
        self.assertIn("return STOPS.map((_, i) => ({ stop: String(i + 1) }));", stop)
        first = src("site", "app", "tour", "page.tsx")
        self.assertIn("<TourBar at={0} />", first)
        self.assertIn("Start the tour", first)
        for f in (bar, stop, first):
            self.assertNotIn(chr(0x2014), f)
            self.assertNotIn("rounded", f)

    def test_the_heading_check(self):
        c = src("site", "scripts", "check-tour.mjs")
        self.assertIn("for (const q of s.headings) check(hs.includes(q)", c)
        self.assertIn('"x-erw-check": "1"', c)
        self.assertIn('"/tour", "/tour/1", "/tour/7"', src("site", "scripts", "check-routes.mjs"))

    def test_the_menu_line(self):
        # chain 507 (session 8902): twelve stops since the whole country's five joined the ruled seven. Session 10236 (the
        # audit of the home page and the tour, finding 9): sixteen since four more landed; the line keeps no count
        self.assertIn("A guided path for a first visit, one page a stop with Back and Next", src("site", "lib", "pages.ts"))


if __name__ == "__main__":
    unittest.main()
