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


def node(code, stdin=None):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True,
                       timeout=120, input=stdin)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class Leaderboard(unittest.TestCase):
    def test_presets_round_trip_and_unknown_ones_refused(self):
        got = node("""import { parsePreset, presetOf, DEFAULT_SETTINGS } from './lib/battery.ts';
const ok = ['easy', 'normal', 'hard'].map((d) => presetOf(DEFAULT_SETTINGS, d));
ok.push(presetOf({ kwh: 30, kw: 11.5, rte: 0.75, reserve: 0.5, deg: 0.3 }, 'hard'), presetOf({ kwh: 5, kw: 1, rte: 0.95, reserve: 0, deg: 0 }, 'normal'));
const bad = ['', 'normal', 'normal:13.5-5-90-r20-d0.11', 'hard:13.5-5-90', 'normal:13.50-5-90', 'normal:13.5-5.0-90', 'normal:100-5-90',
  'normal:13.3-5-90', 'normal:13.5-5-96', 'extreme:13.5-5-90', 'Normal:13.5-5-90', 'normal:13.5-5-90;drop', 'hard:13.5-5-90-r21-d0.11',
  'hard:13.5-5-90-r20-d0.115', ' normal:13.5-5-90', 'normal:13.5-5-90 ', 'x'.repeat(100), 42, null];
console.log(JSON.stringify({ ok: ok.map((p) => [p, JSON.stringify(parsePreset(p) && presetOf(parsePreset(p).settings, parsePreset(p).difficulty))]),
  bad: bad.map((p) => parsePreset(p)) }));""")
        for p, back in got["ok"]:
            self.assertEqual(json.loads(back), p)
        self.assertEqual(got["bad"], [None] * len(got["bad"]))

    def test_read_route(self):
        route = src("site", "app", "api", "play", "top", "route.ts")
        self.assertIn("export async function GET", route)
        self.assertIn("if (!parsePreset(preset)) return fail(", route)
        self.assertIn("if (!level) return fail(", route)
        self.assertIn("leaderboard(level.date, 60, preset)", route)
        self.assertNotIn("insertRow", route)  # read only
        self.assertIn("allowRead(clientIp(req))", route)
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn("/api/play/top?${new URLSearchParams({ level: level.date, preset })}", game)
        self.assertIn('phase !== "pick" || !ok', game)
        self.assertIn("Leaderboard, {topFor.date}: {presetLabel(topFor.preset)}", game)


@unittest.skipUnless(NODE, "node is not installed")
class SetE(unittest.TestCase):
    def test_network_answers_on_the_committed_snapshot(self):
        c = committed()
        h = c["hours"][-1]
        got = node("""import { netValue, tiesAt, topExporter } from './lib/network.ts'; import fs from 'node:fs';
const s = JSON.parse(fs.readFileSync('data/grid_network.json', 'utf-8')); const h = s.hours.at(-1);
console.log(JSON.stringify({ ties: tiesAt(s, 'ERCO', h), top: topExporter(s, h), v: ['net|ties|ERCO|' + h, 'net|maxflow|ERCO|' + h, 'net|topexport|' + h,
  'net|ties|ERCO|1999-01-01T00:00:00Z'].map((k) => netValue(s, k) ?? null) }));""")
        # by hand, in Python, from the same file
        i = len(c["hours"]) - 1
        ties = [(l["b"] if l["a"] == "ERCO" else l["a"], (1 if l["a"] == "ERCO" else -1) * l["mw"][i]) for l in c["links"] if "ERCO" in (l["a"], l["b"]) and l["mw"][i] is not None]
        net = {}
        for l in c["links"]:
            if l["mw"][i] is not None:
                net[l["a"]] = net.get(l["a"], 0) + l["mw"][i]
                net[l["b"]] = net.get(l["b"], 0) - l["mw"][i]
        top = max(sorted(net), key=lambda k: net[k])
        self.assertEqual(sorted((t["other"], t["mw"]) for t in got["ties"]), sorted(ties))
        self.assertEqual(got["top"]["id"], top)
        self.assertAlmostEqual(got["top"]["mw"], net[top], places=6)
        self.assertEqual(got["v"][0], len(ties))
        self.assertAlmostEqual(got["v"][1], max(abs(v) for _, v in ties), places=6)
        self.assertAlmostEqual(got["v"][2], net[top], places=6)
        self.assertIsNone(got["v"][3])
        self.assertGreater(len(ties), 0, h)

    def test_money_answers_from_lib_merchant(self):
        got = node("""import * as M from './lib/merchant.ts'; import fs from 'node:fs';
const s = JSON.parse(fs.readFileSync('data/merchant_snapshot.json', 'utf-8'));
const sol = M.inputsOf({ iso: 'ercot', asset: 'solar' }), bat = M.inputsOf({ iso: 'ercot', asset: 'battery' });
const mo = M.months(s, sol).filter((r) => r.held).at(-1).m;
console.log(JSON.stringify({ mo, cap: M.stat(s, sol, 'capture:' + mo), flat: M.stat(s, sol, 'flat:' + mo), rate: M.stat(s, sol, 'rate:' + mo),
  n: M.stat(s, bat, 'n'), under: M.stat(s, bat, 'under1'), tot: M.stat(s, sol, 'stress_total:uri_2021'), week: M.stat(s, sol, 'stress_week:uri_2021'),
  bat: [bat.mw, bat.mwh] }));""")
        self.assertAlmostEqual(got["rate"], got["cap"] / got["flat"] * 100, places=9)
        self.assertEqual(got["bat"], [100, 400])
        self.assertTrue(0 <= got["under"] <= got["n"])
        self.assertGreater(got["tot"], 0)
        self.assertGreater(got["week"], 0)

    def test_wired(self):
        p = src("site", "lib", "problems.ts")
        self.assertIn('slug: "networks-and-money", title: "Networks and money"', p)
        self.assertIn('slug === "networks-and-money" ? await setE()', p)
        for k in ("net|ties|ERCO|", "net|maxflow|ERCO|", "net|topexport|", "capture:${mo}", "flat:${mo}", "rate:${mo}", '"n", "months"', '"under1", "months"',
                  "stress_total:${ev}", "stress_week:${ev}"):
            self.assertIn(k, p)
        body = p[p.index("async function setE"):p.index("export const SETS")]
        self.assertIsNone(re.search(r"\b\d{3,}\.\d+\b", body), "a typed number in set E")
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('p[0] === "net"', cv)
        self.assertIn('"/learn/problems/networks-and-money"', cv)
        self.assertIn('"/learn/problems/networks-and-money"', src("site", "scripts", "check-routes.mjs"))
        self.assertIn('href: "/learn/problems/networks-and-money"', src("site", "lib", "pages.ts"))
        self.assertIn("`/learn/problems/networks-and-money`", src("docs", "tools.md"))
        self.assertIn('case "flat":', src("site", "lib", "merchant.ts"))

    def test_no_em_dashes(self):
        for p in (("site", "lib", "problems.ts"), ("site", "lib", "network.ts"), ("site", "lib", "battery.ts"), ("site", "lib", "game.ts"),
                  ("site", "app", "api", "play", "top", "route.ts"), ("site", "app", "play", "battery", "Game.tsx"), ("site", "scripts", "check-values.mjs"),
                  ("warehouse", "derived", "network_hourly.py"), ("tests", "test_session55.py"), ("docs", "tools.md")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
