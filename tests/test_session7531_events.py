"""Session 7531 (chain 304, part A): /events and its nine event pages taken to the done line.

Held here: the ten pages drawn to HTML with the site's own code on the public rows kept beside the replication
(site/scripts/test-events-render.mjs: faults 2, 3 and 4, the decisions block on every page, the method note's list, the
hold as it stands); the replication run again on those rows (every figure of the pages, the table's comparison rows,
the builder's estimates, the pages' sentences); the do-file's expected values; the method note, the cross-check and the
faults file. No table of the warehouse is needed: every table the tool reads is public, and the rows are beside the
replication.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "events")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePagesDrawn(unittest.TestCase):
    """The ten pages and their decisions blocks drawn without a build."""

    @classmethod
    def setUpClass(cls):
        env = {k: v for k, v in os.environ.items() if k != "EVENTS_DRAW_UNHELD"}
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-events-render.mjs"], cwd=SITE, capture_output=True,
                           text=True, encoding="utf-8", timeout=900, env=env)
        cls.code, cls.out, cls.err = r.returncode, r.stdout, r.stderr

    def test_every_check_passes(self):
        self.assertEqual(self.code, 0, self.out[-3000:] + self.err[-1500:])
        self.assertNotIn("FAIL", self.out)
        m = re.search(r"(\d+) of (\d+) passed", self.out)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 40, self.out[-500:])

    def test_the_three_fixes_are_checked(self):
        for fault in ("fault 2", "fault 3", "fault 4"):
            self.assertIn(f"ok   {fault}", self.out)


class TheReplication(unittest.TestCase):
    """replicate.py on the rows beside it: every figure, the comparison rows, the builder's estimates, the sentences."""

    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, encoding="utf-8", timeout=900)
        cls.code, cls.out = r.returncode, r.stdout + r.stderr

    def test_exit_and_counts(self):
        self.assertEqual(self.code, 0, self.out[-3000:])
        # session 7531's held-row fix: 27 figures of ISO-NE's, MISO's and NYISO's hubs and 3 of their estimates are held,
        # counted and not recomputed (the run said 1176 of 1176 and 195 of 195 before)
        self.assertIn("part 1, the pages' figures: 1151 of 1151 pass (named 0); held, not recomputed here: 27", self.out)
        self.assertIn("part 2, the table's comparison rows recomputed from its level rows: 2890 of 2890", self.out)
        self.assertRegex(self.out, r"part 3, the pooled estimates against event_study_estimates \(retrieved \d{8}T\d{6}Z\): 186 of 186; held, not recomputed here: 3 estimates")
        self.assertIn("29469 rows kept, 484 held", self.out)
        self.assertNotIn("FALSE", self.out)
        self.assertNotIn("MISS", self.out)
        self.assertEqual(self.out.count("  TRUE "), 15)

    def test_page_figures_file(self):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            fig = json.load(f)
        self.assertEqual(sum(len(p["figures"]) for p in fig["pages"].values()), 1102)  # session 7549: Uri's highest hour and its baseline's
        self.assertEqual(sum(p.get("heldFigures", 0) for p in fig["pages"].values()), 27)
        self.assertEqual(fig["tables"]["event_window_daily"], "20261019T094329Z")
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1102 + 9)  # each number not held, and one line of day counts a page with an event study
        self.assertTrue(all(r["pass"] == "yes" for r in rows))

    def test_the_rows_beside_are_the_public_table(self):
        with open(os.path.join(REP, "window_rows.csv"), encoding="utf-8") as f:
            head = [next(f) for _ in range(3)]
        self.assertTrue(head[1].startswith("# Retrieved: 20261019T094329Z"))
        self.assertEqual(head[2].strip(), "entity,variable,ts_utc,value,freq,ba,event")

    def test_the_replication_is_not_the_pages_code(self):
        rep = src("replication", "events", "replicate.py")
        for word in ("import subprocess", "eventstudy.ts", "EventWindow", "studyOf("):
            self.assertNotIn(word, rep.split('"""', 2)[2])


class NoHeldRowInTheFolder(unittest.TestCase):
    """Session 7531's held-row fix: this is a public repository, and event_window_daily and event_study_estimates are
    "license needed", held by grid (site/data/license_status.json). No file of replication/events/ holds a row or a page
    figure of a deciding grid's entity, by the site's rule (site/lib/license.ts licenseHeldRow, gridOfEntity), read here
    on its own from the status file."""

    TABLES = ("event_window_daily", "event_study_estimates")
    GRID = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(SITE, "data", "license_status.json"), encoding="utf-8") as f:
            tables = json.load(f)["tables"]
        cls.held = set()
        for t in cls.TABLES:
            r = tables[t]
            assert r["status"] == "license needed" and all(p in cls.GRID for p in r["publishers"]), t  # held by grid, as the fix assumes
            cls.held |= {cls.GRID[p] for p in r["publishers"]}
        # an entity of a held grid: "<grid>:...", "<grid>_queue:...", "<grid>_load_queue:...", "iso:<grid>" (entities are
        # lower case; the files' first line names the grids in words, "ISO-NE, MISO and NYISO: site/data/...")
        g = "|".join(sorted(cls.held))
        cls.entity = re.compile(rf"(?<![A-Za-z0-9_-])(?:(?:{g})(?:_(?:load_)?queue)?:|iso:(?:{g})\b)")
        cls.files = sorted(p for p in os.listdir(REP) if p.endswith((".csv", ".json")))

    def test_the_held_grids(self):
        self.assertEqual(self.held, {"isone", "miso", "nyiso"})

    def test_no_held_entity_in_any_data_file(self):
        self.assertGreaterEqual(len(self.files), 6)
        for name in self.files:
            with open(os.path.join(REP, name), encoding="utf-8") as f:
                text = f.read()
            self.assertIsNone(self.entity.search(text), f"{name}: {self.entity.search(text)}")

    def test_every_row_and_key_kept_by_the_rule(self):
        with open(os.path.join(REP, "window_rows.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(l for l in f if not l.startswith("#")))
        with open(os.path.join(REP, "estimate_rows.csv"), encoding="utf-8") as f:
            est = list(csv.DictReader(l for l in f if not l.startswith("#")))
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            keys = [g["check"] for p in json.load(f)["pages"].values() for g in p["figures"]]
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            keys += [r["key"] for r in csv.DictReader(f)]
        grid = lambda e: (e.split(":", 1)[0].lower() if ":" in e else "")
        self.assertEqual(len(rows), 29469)
        self.assertFalse([r["entity"] for r in rows + est if grid(r["entity"]) in self.held])
        self.assertFalse([k for k in keys if k.startswith(("series|", "es|")) and grid(k.split("|")[2]) in self.held])
        # rows of no grid are kept: EIA-930's ISO-NE, MISO and NYISO, the weather stations, ERCOT's hub
        ents = {r["entity"] for r in rows}
        self.assertTrue({"eia930:ISNE", "eia930:MISO", "eia930:NYIS", "ercot:HB_HUBAVG"} <= ents and any(e.startswith("noaa:") for e in ents))

    def test_the_counts_are_written_not_the_rows(self):
        for name, n in (("window_rows.csv", 484), ("estimate_rows.csv", 3)):
            with open(os.path.join(REP, name), encoding="utf-8") as f:
                self.assertIn(f"held, not copied: {n} rows", f.readline(), name)


class TheDoFile(unittest.TestCase):
    def test_expected_values_match_the_replication(self):
        do = src("replication", "events", "replicate.do")
        with open(os.path.join(REP, "page_figures.csv"), encoding="utf-8", newline="") as f:
            got = {r["key"]: r["shown"] for r in csv.DictReader(f)}
        pairs = [("9,051.55 USD/MWh on 2021-02-17", "series|event_window_daily|ercot:HB_HUBAVG|rt_max|2021-02-17T00:00:00Z|uri_2021", "9,051.55"),
                 ("135,328 MW on 2022-12-23", "series|event_window_daily|eia930:PJM|demand_max_mw|2022-12-23T00:00:00Z|elliott_2022", "135,328"),
                 ("85,432 MW on 2023-08-10", "series|event_window_daily|eia930:ERCO|demand_max_mw|2023-08-10T00:00:00Z|ercot_heat_2023", "85,432"),
                 ("155,794.96 MWh a day", "es|uri_2021|eia930:ERCO|demand_mwh|pooled|est", "155,794.96"),
                 ("386,999.95 MWh a day", "es|elliott_2022|eia930:PJM|demand_mwh|pooled|est", "386,999.95")]
        for words, key, shown in pairs:
            self.assertIn(words, do)
            self.assertEqual(got.get(key), shown, key)
        self.assertIn("vce(robust)", do)
        self.assertIn("ib1.dw", do)


class TheWrittenParts(unittest.TestCase):
    def test_no_dashes(self):
        for p in [("docs", "methods", "events.md"), ("docs", "methods", "event_study.md"), ("docs", "reviews", "events-faults-2026-11-16.md"),
                  ("docs", "reviews", "events-crosscheck-2026-11-16.md"), ("replication", "events", "replicate.py"), ("replication", "events", "replicate.do"),
                  ("site", "app", "events", "Decisions.tsx"), ("site", "app", "events", "page.tsx"), ("site", "app", "events", "covid-2020", "page.tsx"),
                  ("site", "app", "events", "ercot-heat-2023", "page.tsx"), ("site", "scripts", "events-pages.mjs"), ("site", "scripts", "test-events-render.mjs")]:
            text = src(*p)
            self.assertFalse(any(d in text for d in DASHES), p)

    def test_faults_file(self):
        t = src("docs", "reviews", "events-faults-2026-11-16.md")
        rows = re.findall(r"^\| (\d+) \| ([a-z ,]+) \|", t, re.M)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, 11)))
        kinds = [k for _, k in rows]
        self.assertEqual(kinds.count("site, fixed"), 3)
        self.assertEqual(kinds.count("ruling"), 5)
        self.assertEqual(kinds.count("data machine"), 1)
        self.assertIn("Site faults fixed: 3", t)

    def test_crosscheck(self):
        t = src("docs", "reviews", "events-crosscheck-2026-11-16.md")
        self.assertEqual(len(re.findall(r"^\| \d+ \|", t, re.M)), 16)
        for who in ("FERC", "CAISO", "ERCOT", "PJM", "EIA", "nerc.com was not read"):
            self.assertIn(who, t)

    def test_every_event_page_mounts_its_decisions(self):
        for slug in ("uri-2021", "covid-2020", "caiso-heat-2020", "caiso-heat-2022", "elliott-2022", "ercot-heat-2023", "cold-2025", "east-heat-2025", "cold-2026"):
            page = src("site", "app", "events", slug, "page.tsx")
            self.assertIn('import { EventDecisions } from "../Decisions";', page)
            self.assertIn(f'<EventDecisions event="{slug.replace("-", "_")}" />', page)
            self.assertLess(page.index("<EventStudy"), page.index("<EventDecisions"))
        self.assertIn("<EventDecisions />", src("site", "app", "events", "page.tsx"))


if __name__ == "__main__":
    unittest.main()
