"""Session 8410 (chain 503, part B): the events pages for the whole country.

Each of the nine event pages gains a section "The whole country" (site/app/events/WholeCountry.tsx) that draws EIA's
thirteen regions of the lower 48 from the data machine's file of the event (site/data/regions/events/<event>.json, the
contract docs/state/page_files_regions.md), and each row of /events says how many regions the event reached. Held here:

- add, never change: outside what the session added, each of the ten pages is byte for byte what origin/main drew
  before it (site/scripts/test-events-pin.mjs, as a visitor's build draws the pages and with the hold stood aside);
- the section drawn to HTML from a fixture in the contract's form, and the whole pages with and without a file
  (site/scripts/test-events-regions.mjs);
- the rules of the chain in the source: no fixture in the site's folder, no dash, every page still in review, the
  method note says what the section shows.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
NEW = ["site/lib/countryfiles.ts", "site/app/events/WholeCountry.tsx", "site/scripts/regions-fixture.mjs", "site/scripts/events-added.mjs",
       "site/scripts/test-events-regions.mjs", "site/scripts/test-events-pin.mjs"]
EVENTS = ["uri_2021", "covid_2020", "caiso_heat_2020", "caiso_heat_2022", "elliott_2022", "ercot_heat_2023", "cold_2025", "east_heat_2025", "cold_2026"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(script, unheld=False):
    env = {k: v for k, v in os.environ.items() if k not in ("EVENTS_DRAW_UNHELD", "ERW_REGIONS_DIR")}
    if unheld:
        env["EVENTS_DRAW_UNHELD"] = "1"
    return subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", script], cwd=SITE, capture_output=True, text=True,
                          encoding="utf-8", timeout=900, env=env)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePagesDrawn(unittest.TestCase):
    def check(self, r, least):
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertNotIn("FAIL", r.stdout)
        m = re.search(r"(\d+) of (\d+) passed", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= least, r.stdout[-500:])

    def test_nothing_the_pages_showed_moves_as_a_visitor_sees_them(self):
        self.check(node("scripts/test-events-pin.mjs"), 21)

    def test_nothing_the_pages_showed_moves_with_the_hold_stood_aside(self):
        self.check(node("scripts/test-events-pin.mjs", unheld=True), 21)

    def test_the_whole_country_section(self):
        r = node("scripts/test-events-regions.mjs")
        self.check(r, 77)
        for held in ("the six regions new to the site carry their mark", "pair by pair: which region sent and which took",
                     "with no file the section says not built yet", "a fixture in the site's own folder is refused",
                     "a file that is not public: every cell blank with license needed on hover"):
            self.assertIn(held, r.stdout)


class TheSource(unittest.TestCase):
    def test_the_pin_holds_ten_pages_in_two_modes(self):
        pin = json.loads(src("site", "scripts", "pins", "events-pages-8410.json"))
        self.assertEqual(sorted(pin["modes"]), ["unheld", "visitor"])
        for mode in pin["modes"].values():
            self.assertEqual(len(mode), 10)
            for page in mode.values():
                self.assertRegex(page["sha256"], r"^[0-9a-f]{64}$")

    def test_each_event_page_mounts_the_section_once_with_its_own_event(self):
        for ev in EVENTS:
            page = src("site", "app", "events", ev.replace("_", "-"), "page.tsx")
            self.assertEqual(page.count("<WholeCountrySection "), 1, ev)
            self.assertIn(f'<WholeCountrySection event="{ev}" path="/events/{ev.replace("_", "-")}"', page)
            self.assertIn("searchParams={searchParams}", page)
            self.assertLess(page.index("<WholeCountrySection "), page.index("<EventDecisions "), ev)
        self.assertEqual(src("site", "app", "events", "page.tsx").count("<RegionsReached "), 1)

    def test_no_dash_in_what_was_written(self):
        for f in NEW + ["tests/test_session8410_events_regions.py"]:
            text = src(*f.split("/"))
            for d in DASHES:
                self.assertNotIn(d, text, f)

    def test_no_fixture_and_no_held_figure_in_the_sites_folder(self):
        folder = os.path.join(SITE, "data", "regions")
        if not os.path.isdir(folder):
            return
        for base, _dirs, files in os.walk(folder):
            for name in files:
                if name.endswith(".json"):
                    with open(os.path.join(base, name), encoding="utf-8") as f:
                        head = f.read(4000)
                    self.assertNotIn('"fixture"', head, name)

    def test_the_fixture_says_it_is_not_data(self):
        fx = src("site", "scripts", "regions-fixture.mjs")
        self.assertIn("not data", fx)
        self.assertIn("fixture: FIXTURE", fx)
        self.assertIn('"fixture" in v && v.fixture && !process.env.ERW_REGIONS_DIR', src("site", "lib", "countryfiles.ts"))

    def test_the_pages_stay_in_review(self):
        self.assertIn('"/events": "review"', src("site", "lib", "release.ts"))

    def test_no_estimate_and_no_ledger_in_the_section(self):
        code = src("site", "app", "events", "WholeCountry.tsx") + src("site", "lib", "countryfiles.ts")
        shown = re.sub(r"//.*|/\*\*?[\s\S]*?\*/", "", code)
        for word in ("donor", "taker", "covered by imports"):
            self.assertNotIn(word, shown.lower())

    def test_the_method_note_says_what_the_section_shows(self):
        note = src("docs", "methods", "events.md")
        self.assertIn("The whole country", note)
        for said in ("site/data/regions/events/", "5 percent", "docs/state/page_files_regions.md", "not built yet", "no ledger"):
            self.assertIn(said, note, said)


if __name__ == "__main__":
    unittest.main()
