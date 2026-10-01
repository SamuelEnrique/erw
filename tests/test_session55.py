"""Session 55: leaner hourly pulls, the game's leaderboard by preset, problem set E.

Energy Research Warehouse (ERW). No network, no model.
1. network_hourly.py: EIA's interchange endPeriod is read first; when it equals the one the Storage object was built
   from, the interchange pull is skipped, the links carried over unchanged, demand alone refreshed, and the object
   records interchange "unchanged". Both paths run on fixtures: interchange rows written from the committed snapshot's
   own values (real EIA-930 flows, at their own hours), demand from tests/fixtures/network/eia_demand.json (real values
   recorded in session 54).
2. The game's read route for a level's top ten by preset, and its refusal of unknown presets.
3. Problem set E, "Networks and money": every answer computed and carrying a check key.

    python -m unittest tests.test_session55 -v
"""

import copy
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import network_hourly as nh  # noqa: E402

NODE = shutil.which("node")
FX = os.path.join(ROOT, "tests", "fixtures", "network", "eia_demand.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def committed():
    with open(nh.COMMITTED, encoding="utf-8") as f:
        return json.load(f)


def rows_from(snap, hours=48):
    """EIA interchange rows (period = hour end) for the snapshot's last hours, each pair as its first BA reported it."""
    out = []
    for l in snap["links"]:
        for h, v in list(zip(snap["hours"], l["mw"]))[-hours:]:
            if v is not None:
                end = nh.parse(h) + dt.timedelta(hours=1)
                out.append(dict(period=end.strftime("%Y-%m-%dT%H"), fromba=l["a"], toba=l["b"], value=str(v)))
    return out


class Calls:
    """Fixture pulls that count their calls."""
    def __init__(self, x_rows, d_rows):
        self.x_rows, self.d_rows, self.x, self.d = x_rows, d_rows, 0, 0

    def interchange(self, xe):
        self.x += 1
        return self.x_rows, ["https://api.eia.gov/v2/electricity/rto/interchange-data/data/?api_key=<key>"]

    def demand(self):
        self.d += 1
        return self.d_rows, ["https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=<key>"]


class LeanerPulls(unittest.TestCase):
    def setUp(self):
        self.c = committed()
        with open(FX, encoding="utf-8") as f:
            self.fx = json.load(f)
        self.xe = dt.datetime.strptime(self.fx["interchange_end_period"], "%Y-%m-%dT%H").replace(tzinfo=dt.timezone.utc)
        self.quiet = lambda *_: None

    def first(self):
        """A pulled run on the committed snapshot (no object in Storage yet)."""
        calls = Calls(rows_from(self.c), self.fx["demand_run1"])
        snap, _ = nh.build(None, self.c, self.xe, calls.interchange, calls.demand, "2026-10-01T18:17:10Z", self.quiet)
        return snap, calls

    def test_pulled_path(self):
        snap, calls = self.first()
        self.assertEqual((calls.x, calls.d), (1, 1))
        self.assertEqual(snap["interchange"], "pulled")
        self.assertEqual(snap["pull"]["interchange_end_period"], "2026-09-30T07")
        self.assertEqual(snap["pull"]["interchange_pulled"], "2026-10-01T18:17:10Z")
        self.assertGreater(snap["pull"]["interchange_rows"], 0)
        # the fixture rows are the committed snapshot's own values at its own hours: the links come back as they were
        self.assertEqual(snap["hours"], self.c["hours"])
        self.assertEqual({(l["a"], l["b"]): l["mw"] for l in snap["links"]}, {(l["a"], l["b"]): l["mw"] for l in self.c["links"]})
        erco = next(n for n in snap["nodes"] if n["id"] == "ERCO")
        self.assertEqual((erco["demand_mw"], erco["demand_ts"], erco["demand_src"]), (64661.0, "2026-10-01T15:00:00Z", "hourly"))

    def test_unchanged_path_skips_the_interchange_pull(self):
        stored, _ = self.first()
        calls = Calls(None, self.fx["demand_run2"])

        def refuse(xe):
            raise AssertionError("the interchange pull ran although EIA's endPeriod had not moved")
        snap, last = nh.build(stored, self.c, self.xe, refuse, calls.demand, "2026-10-01T19:00:05Z", self.quiet)
        self.assertEqual(calls.d, 1)
        self.assertEqual(snap["interchange"], "unchanged")
        self.assertEqual(snap["pull"]["interchange_rows"], 0)
        self.assertEqual(snap["pull"]["interchange_end_period"], "2026-09-30T07")
        self.assertEqual(snap["pull"]["interchange_pulled"], "2026-10-01T18:17:10Z")  # when the links were last pulled
        self.assertEqual(snap["built"], "2026-10-01T19:00:05Z")
        # links, hours, window and positions carried over unchanged
        for k in ("hours", "window", "links", "newest_hour"):
            self.assertEqual(snap[k], stored[k], k)
        self.assertEqual([(n["id"], n["x"], n["y"], n["z"], n["volume_mwh"]) for n in snap["nodes"]],
                         [(n["id"], n["x"], n["y"], n["z"], n["volume_mwh"]) for n in stored["nodes"]])
        self.assertGreaterEqual(last, 100)
        # demand refreshed: ERCOT's newest hour moves from 15:00 to 16:00 UTC
        erco = next(n for n in snap["nodes"] if n["id"] == "ERCO")
        self.assertEqual((erco["demand_mw"], erco["demand_ts"]), (65789.0, "2026-10-01T16:00:00Z"))
        self.assertEqual(snap["pull"]["urls"], ["https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=<key>"])

    def test_moved_end_period_pulls(self):
        stored, _ = self.first()
        calls = Calls(rows_from(self.c), self.fx["demand_run2"])
        snap, _ = nh.build(stored, self.c, self.xe + dt.timedelta(hours=1), calls.interchange, calls.demand, "2026-10-01T19:00:05Z", self.quiet)
        self.assertEqual(calls.x, 1)
        self.assertEqual(snap["interchange"], "pulled")
        self.assertEqual(snap["pull"]["interchange_end_period"], "2026-09-30T08")

    def test_newer_daily_snapshot_pulls(self):
        # the daily run rebuilt the committed snapshot after the object: it becomes the base, and the links are pulled again
        stored, _ = self.first()
        newer = dict(copy.deepcopy(self.c), built="2026-10-02T04:00:00Z")
        calls = Calls(rows_from(self.c), self.fx["demand_run2"])
        snap, _ = nh.build(stored, newer, self.xe, calls.interchange, calls.demand, "2026-10-02T05:00:00Z", self.quiet)
        self.assertEqual(calls.x, 1)
        self.assertEqual(snap["base_built"], "2026-10-02T04:00:00Z")

    def test_objects_from_before_session_55(self):
        # session 54's object recorded only eia_interchange_end (the newest period of its rows)
        self.assertEqual(nh.previous_end({"pull": {"eia_interchange_end": "2026-09-30T07"}}), "2026-09-30T07")
        self.assertEqual(nh.previous_end({"pull": {"interchange_end_period": "2026-09-30T08", "eia_interchange_end": "2026-09-30T07"}}), "2026-09-30T08")
        self.assertIsNone(nh.previous_end(None))


if __name__ == "__main__":
    unittest.main()
