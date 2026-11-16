"""Session 7400 (chain 303): the datacenter tracker's replication (replication/datacenter_tracker/), the page's top
block as one library function (site/lib/dctop.ts) and the script that runs the page's functions on the rows
(site/scripts/datacenter-tracker-figures.mjs).

Every row here is made up for the test: no row of the held table datacenter_facilities is in this file. Node runs the
page's functions on the made-up rows and the replication's own Python computes the same figures from the method note's
rules; the two are compared key by key, as the replication does on the live set's rows.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "datacenter_tracker")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fac(i, operator, state, status, mw, **extra):
    x = {"kind": "news", "state": state, **({"country": "US"} if state else {}), **extra}
    return {"entity_id": f"datacenter:test{i:02d}", "entity_type": "datacenter", "name": f"Made-up site {i}", "lat": None, "lon": None,
            "capacity_mw": mw, "status": status, "status_date": None, "operator": operator, "source": "test", "source_url": "",
            "vintage": "2026-11-15T00:00:00Z", "table_name": "datacenter_facilities", "extra": {k: v for k, v in x.items() if v not in (None, "")}}


ROWS = [
    fac(1, "Alpha", "TX", "planned", 100, first_story_at="2026-11-12T10:00:00Z", planned_year="2028", power_kind="gas", grid="ERCOT", grid_basis="state"),
    fac(2, "Alpha", "TX", "under_construction", 250.5, first_story_at="2026-08-02T10:00:00Z", planned_year="2027", grid="ERCOT", grid_basis="named"),
    fac(3, "Alpha", "TX", "withdrawn", 900, first_story_at="2026-03-02T10:00:00Z"),
    fac(4, "Beta", "VA", "operating", 60),
    fac(5, "Beta", "VA", None, None),
    fac(6, "Beta", "", "planned", 5000, first_story_at="2026-11-10T00:00:00Z"),
    fac(7, None, "OH", "planned", 300, first_story_at="2025-12-30T10:00:00Z", energized_year="2029", power_kind="nuclear"),
    fac(8, "Gamma", "PR", "planned", 40, first_story_at="2026-02-01T10:00:00Z", planned_year="2026"),
    fac(9, "Gamma", "GA", "planned", None, first_story_at="2026-05-01T10:00:00Z", planned_year="2030"),
    fac(10, "Delta", "TX", "active", None, kind="queue", queue_mw="58.26"),
]
SERIES = [{"entity": "ercot:large_load", "variable": v, "ts_utc": f"{d}T00:00:00+00:00", "value": x, "unit": "MW", "table_name": "ercot_large_load_status"}
          for d, a, n, s in (("2025-05-28", 6874, 3489, 3441), ("2026-06-19", 8927, 3900, 3675))
          for v, x in (("approved_to_energize_mw", a), ("observed_nonsimultaneous_peak_mw", n), ("observed_simultaneous_peak_mw", s))]
SITES = [{"entity_id": "ercot_queue:TEST1", "capacity_mw": 133, "status": "completed", "table_name": "ercot_interconnection_queue", "extra": {"county": "Made-up"}},
         {"entity_id": "ercot_queue:TEST2", "capacity_mw": 58.26, "status": "active", "table_name": "ercot_interconnection_queue", "extra": {}}]
ACTIVE = [{"table_name": "ercot_interconnection_queue", "capacity_mw": 100.5, "status": "active", "zone": None},
          {"table_name": "ercot_interconnection_queue", "capacity_mw": None, "status": "active", "zone": None}]


def rows_dir(tmp):
    for name, obj in (("datacenter_facilities.json", ROWS), ("ercot_large_load_status.json", SERIES), ("queue_sites.json", SITES), ("queue_active.json", ACTIVE),
                      ("retrieved.json", {"retrieved_at": "2026-11-16T00:00:00Z", "source": "made up for the test", "vintage": "2026-11-15"})):
        with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
            json.dump(obj, f)
    return tmp


def page(tmp, today="2026-11-16"):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, os.path.join("scripts", "datacenter-tracker-figures.mjs"), tmp, today], cwd=SITE, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-800:])
    return json.loads(r.stdout)


class TheTopBlockIsOneFunction(unittest.TestCase):
    def test_the_component_reads_the_library(self):
        b = src("site", "app", "datacenters", "Body.tsx")
        self.assertIn('import { counted, firstReportedSince, topBlock, topRowOf, weekStart } from "@/lib/dctop";', b)
        self.assertIn("topBlock(rows, today)", b)
        self.assertIn("...topRowOf(r),", b)
        self.assertNotIn("const sumBy", b)                                   # the arithmetic is not in the component twice
        self.assertIn("return operatorGroups(rows);", src("site", "app", "datacenters", "DatacentersTable.tsx"))

    def test_the_library_restates_the_rules_of_largeload_unchanged(self):
        t, l = src("site", "lib", "dctop.ts"), src("site", "lib", "largeload.ts")
        states = lambda s: sorted(re.findall(r'"([A-Z]{2})"', s.split("US_STATES = new Set([", 1)[1].split("])", 1)[0]))
        self.assertEqual(states(t), states(l))
        self.assertEqual(len(states(t)), 52)                                 # the 50 states, the District of Columbia and Puerto Rico
        for rule in ('(country ?? "") || (US_STATES.has(state ?? "") ? "US" : "")', '["withdrawn", "cancelled"].includes((status ?? "").toLowerCase())'):
            self.assertIn(rule, t)
            self.assertIn(rule, l)
        self.assertNotRegex(t, r"(?m)^import ")                              # Node runs the file alone

    def test_the_rollups_count_the_states_the_top_block_counts(self):
        r = src("site", "lib", "dcrollups.ts")
        rolled = sorted(r.split('const STATES = new Set(("', 1)[1].split('").split(" ")', 1)[0].replace('" +\n  "', "").replace('" +\r\n  "', "").split())
        top = sorted(re.findall(r'"([A-Z]{2})"', src("site", "lib", "dctop.ts").split("US_STATES = new Set([", 1)[1].split("])", 1)[0]))
        self.assertEqual(rolled, top)                                        # faults row 15: Puerto Rico was in one list and not the other
        self.assertIn("WV WI WY PR", src("scripts", "check_datacenters.py"))


class TheReplicationAgreesWithThePage(unittest.TestCase):
    def test_made_up_rows_key_by_key(self):
        rep = module(os.path.join(REP, "replicate.py"), "dc_replicate")
        with tempfile.TemporaryDirectory() as tmp:
            shown = page(rows_dir(tmp))["figures"]
            mine = rep.facilities(ROWS, "2026-11-16")
            rep.grid_side(mine, json.loads(src("site", "data", "siting", "headroom.json")))
            mine.update(rep.ercot(SERIES, json.loads(src("site", "data", "large_load_status.json"))))
            q, grids = rep.queues(SITES, ACTIVE)
            mine.update(q)
        self.assertEqual(grids, ["ercot"])
        facility_keys = [k for k in shown if not k.startswith(("dcpow|", "series|", "ercot|"))]
        self.assertGreater(len(facility_keys), 60)
        for k in facility_keys:
            self.assertIn(k, mine, k)
            self.assertAlmostEqual(float(mine[k]), float(shown[k]), delta=rep.tolerance(k), msg=k)
        for k in mine:
            if not k.startswith(("series|", "ercot|")):
                self.assertIn(k, shown, k)                                   # nothing on one side only
        # the rules, on rows whose answers are known by hand
        self.assertEqual(shown["datacenters|count"], 10)
        self.assertEqual(shown["datacenters|counted"], 8)                    # a named US state (Puerto Rico is one), not cancelled
        self.assertEqual(shown["datacenters|no_us_state"], 1)
        self.assertEqual(shown["datacenters|cancelled"], 1)
        self.assertEqual(shown["datacenters|mw_total"], 100 + 250.5 + 60 + 300 + 40)   # the cancelled 900 and the stateless 5,000 are not summed
        self.assertEqual(shown["datacenters|n_with_mw"], 5)
        self.assertEqual(shown["datacenters|first_week|2026-11-10"], 2)      # the seven days to 16 November, both ends included
        self.assertEqual(shown["datacenters|rollup_facilities|grid|-"], 2)   # Puerto Rico and Georgia: no grid read from the state
        self.assertEqual(shown["datacenters|rollup_mw|grid|ERCOT"], 350.5)
        self.assertNotIn("datacenters|rollup_mw|grid|PJM", {k for k in shown if shown[k] is None})
        self.assertEqual(shown["datacenters|sites_mw"], 100 + 250.5 + 900 + 60 + 5000 + 300 + 40)   # every site held, the cancelled among them
        self.assertEqual(shown["dctime|rows"], 5)
        self.assertEqual(shown["dctime|count|year|2026"], 4)
        self.assertEqual(shown["dctime|median|year|2026"], 1.5)              # waits of 2, 1, 0 and 4 years
        self.assertNotIn("dctime|median|year|2025", shown)                   # fewer than three: no median
        self.assertEqual(shown["dcq|ercot|-|mw_asked"], 191.26)
        self.assertEqual(shown["dcq|ercot|-|active_positions"], 2)

    def test_the_queue_mw_never_fills_a_sum(self):
        rep = module(os.path.join(REP, "replicate.py"), "dc_replicate2")
        mine = rep.facilities(ROWS, "2026-11-16")
        self.assertEqual(mine["datacenters|rollup_without|operator|Delta"], 1)
        self.assertNotIn("datacenters|rollup_mw|operator|Delta", mine)


class TheFiguresFile(unittest.TestCase):
    def test_every_figure_is_inside_its_tolerance_and_names_its_day(self):
        p = json.loads(src("replication", "datacenter_tracker", "page_figures.json"))
        self.assertEqual(p["tool"], "/datacenters")
        self.assertRegex(p["retrieved_at"], r"^2026-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertGreater(len(p["figures"]), 400)
        for f in p["figures"]:
            self.assertIsNotNone(f["page"], f["key"])
            self.assertIsNotNone(f["replication"], f["key"])
            self.assertLessEqual(abs(float(f["page"]) - float(f["replication"])), f["tolerance"] + 1e-9, f["key"])

    def test_no_row_of_the_held_table_is_committed_with_the_replication(self):
        self.assertEqual(src("replication", "datacenter_tracker", "rows", ".gitignore").split("\n")[2:4], ["*", "!.gitignore"])
        got = subprocess.run(["git", "ls-files", "replication/datacenter_tracker/rows"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertIn(got, ([], ["replication/datacenter_tracker/rows/.gitignore"]))


class NoEmDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_the_session_wrote(self):
        for parts in (("site", "lib", "dctop.ts"), ("site", "scripts", "datacenter-tracker-figures.mjs"), ("replication", "datacenter_tracker", "replicate.py"),
                      ("replication", "datacenter_tracker", "fetch_rows.py"), ("tests", "test_session7400_trackers.py")):
            for ch in (chr(0x2014), chr(0x2013)):
                self.assertNotIn(ch, src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
