"""Session 8440 (chain 503, part E): the replication of "The whole country" on the event pages.

replication/events/replicate_regions.py recomputes, from an event's file alone and by the method note's rules, every
figure the section and the index's line print, beside the figure the site's own code draws
(site/scripts/events-regions-figures.mjs). Held here, without a build and without any warehouse table:

- on the test's fixture (values made by a rule, not data) every figure the page draws is recomputed, N of N, and a
  figure moved by one in its last digit is caught;
- on the site as it stands the replication runs and says what it finds: no file yet (nothing to recompute), or every
  figure of every event whose file is there.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "events", "replicate_regions.py")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))


def node(args, regions_dir=None):
    env = {k: v for k, v in os.environ.items() if k not in ("EVENTS_DRAW_UNHELD", "ERW_REGIONS_DIR")}
    if regions_dir:
        env["ERW_REGIONS_DIR"] = regions_dir
    return subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/events-regions-figures.mjs", *args], cwd=SITE,
                          capture_output=True, text=True, encoding="utf-8", timeout=600, env=env)


def replicate(*args):
    return subprocess.run([sys.executable, REP, *args], capture_output=True, text=True, encoding="utf-8", timeout=600)


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="erw-8440-")
        r = node(["--fixture", cls.tmp])
        assert r.returncode == 0, r.stderr[-800:]
        cls.figures = os.path.join(cls.tmp, "figures.json")
        r = node([cls.figures], regions_dir=cls.tmp)
        assert r.returncode == 0, r.stderr[-800:]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_figure_of_the_fixture_is_recomputed(self):
        r = replicate("--figures", self.figures, "--files", os.path.join(self.tmp, "events"))
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-800:])
        m = re.search(r"(\d+) of (\d+) figures over 1 events", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 200, r.stdout[-400:])
        self.assertNotIn("FAIL", r.stdout)

    def test_a_figure_moved_by_one_in_its_last_digit_is_caught(self):
        with open(self.figures, encoding="utf-8") as f:
            page = json.load(f)
        figs = page["events"]["elliott_2022"]["figures"]
        self.assertEqual(figs["wc|TEN|demand_pct"], "+20.0")
        figs["wc|TEN|demand_pct"] = "+20.1"
        figs["wc|pair|CAR-TEN|mean_mw"] = "201"
        moved = os.path.join(self.tmp, "moved.json")
        with open(moved, "w", encoding="utf-8") as f:
            json.dump(page, f)
        r = replicate("--figures", moved, "--files", os.path.join(self.tmp, "events"))
        self.assertEqual(r.returncode, 1, r.stdout[-800:])
        self.assertIn("FAIL elliott_2022 wc|TEN|demand_pct", r.stdout)
        self.assertIn("FAIL elliott_2022 wc|pair|CAR-TEN|mean_mw", r.stdout)

    def test_a_figure_the_page_drops_is_caught(self):
        with open(self.figures, encoding="utf-8") as f:
            page = json.load(f)
        del page["events"]["elliott_2022"]["figures"]["wc|CAL|peak_mw"]
        gone = os.path.join(self.tmp, "gone.json")
        with open(gone, "w", encoding="utf-8") as f:
            json.dump(page, f)
        r = replicate("--figures", gone, "--files", os.path.join(self.tmp, "events"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("wc|CAL|peak_mw", r.stdout)
        self.assertIn("not on the page", r.stdout)

    def test_on_the_site_as_it_stands(self):
        out = os.path.join(self.tmp, "site.json")
        r = node([out])
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        r = replicate("--figures", out)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])
        with open(out, encoding="utf-8") as f:
            events = json.load(f)["events"]
        self.assertEqual(len(events), 9)
        if not any(e.get("file") for e in events.values()):
            self.assertIn("no event's file is on the site yet", r.stdout)
        else:
            self.assertRegex(r.stdout, r"(\d+) of \1 figures over \d+ events")

    def test_a_bad_figures_file_is_bad_input(self):
        self.assertEqual(replicate("--figures", os.path.join(self.tmp, "none.json")).returncode, 2)


class TheSource(unittest.TestCase):
    def test_written_from_the_note_not_from_the_pages_code(self):
        with open(REP, encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn("countryfiles", code.split('"""', 2)[2])
        self.assertNotIn("import subprocess", code)
        for d in DASHES:
            self.assertNotIn(d, code)

    def test_no_dash_in_the_scripts(self):
        for rel in (("site", "scripts", "events-regions-figures.mjs"), ("tests", "test_session8440_events_regions_replication.py")):
            with open(os.path.join(ROOT, *rel), encoding="utf-8") as f:
                text = f.read()
            for d in DASHES:
                self.assertNotIn(d, text, rel[-1])


if __name__ == "__main__":
    unittest.main()
