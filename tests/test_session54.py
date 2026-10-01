"""Session 54: the grid network, refreshed every hour.

Energy Research Warehouse (ERW). No network, no model: the merge runs on the committed snapshot
(site/data/grid_network.json, real EIA-930 values), with "fresh" hours made from that snapshot's own values moved
forward, and a few EIA-shaped rows written by hand for the pair rule.
1. The merge keeps 168 contiguous hours ending at the newest hour, and every node's position unchanged.
2. A pulled pair-hour replaces the base's; an hour not pulled keeps the base's, else the other snapshot's.
3. The pair rule, the newest complete hour, and demand as warehouse/derived/network_hourly.py states them.
4. The page falls back to the committed snapshot when Storage is unreachable, broken or older (site/lib/network.ts).
5. The workflow never writes to the database or git and never overlaps the daily or weekly job.

    python -m unittest tests.test_session54 -v
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


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def committed():
    with open(nh.COMMITTED, encoding="utf-8") as f:
        return json.load(f)


def later(t, h):
    return nh.iso(nh.parse(t) + dt.timedelta(hours=h))


class Merge(unittest.TestCase):
    def setUp(self):
        self.base = committed()
        self.end = self.base["hours"][-1]
        # six new hours: each pair's last value of the committed week, moved forward (real values, new hours)
        self.flows = {(l["a"], l["b"]): {later(self.end, k): l["mw"][-1] for k in range(1, 7)} for l in self.base["links"] if l["mw"][-1] is not None}
        self.newest = later(self.end, 6)

    def test_168_hours_and_positions_unchanged(self):
        s = nh.merge(self.base, None, self.flows, self.newest, {}, "2026-10-01T18:00:00Z")
        self.assertEqual(len(s["hours"]), 168)
        self.assertEqual(s["hours"][-1], self.newest)
        self.assertEqual(s["window"], [s["hours"][0], later(self.newest, 1)])
        self.assertEqual([(n["id"], n["x"], n["y"], n["z"]) for n in s["nodes"]], [(n["id"], n["x"], n["y"], n["z"]) for n in self.base["nodes"]])
        self.assertGreaterEqual(nh.check(s, self.base), 100)
        self.assertEqual(s["base_built"], self.base["built"])
        # the older hours are the base's, moved six places
        old = {(l["a"], l["b"]): l["mw"] for l in self.base["links"]}
        for l in s["links"]:
            self.assertEqual(l["mw"][:162], old[(l["a"], l["b"])][6:], (l["a"], l["b"]))

    def test_volumes_recomputed(self):
        s = nh.merge(self.base, None, self.flows, self.newest, {}, "2026-10-01T18:00:00Z")
        n = next(x for x in s["nodes"] if x["id"] == "ERCO")
        want = sum(abs(v) for l in s["links"] if "ERCO" in (l["a"], l["b"]) for v in l["mw"] if v is not None)
        self.assertAlmostEqual(n["volume_mwh"], round(want, 1), places=1)

    def test_pulled_hour_replaces_base_and_other_fills_gaps(self):
        (a, b), l = next(((x["a"], x["b"]), x) for x in self.base["links"] if all(v is not None for v in x["mw"][-3:]))
        h = self.base["hours"][-2]
        base = copy.deepcopy(self.base)
        bl = next(x for x in base["links"] if (x["a"], x["b"]) == (a, b))
        gap_h = base["hours"][-3]
        other = copy.deepcopy(self.base)
        bl["mw"][-3] = None  # a hole in the base; the other snapshot has it
        flows = {(a, b): {h: l["mw"][-2] + 7.0}}
        s = nh.merge(base, other, flows, self.end, {}, "2026-10-01T18:00:00Z")
        got = dict(zip(s["hours"], next(x for x in s["links"] if (x["a"], x["b"]) == (a, b))["mw"]))
        self.assertEqual(got[h], round(l["mw"][-2] + 7.0, 1))
        self.assertEqual(got[gap_h], l["mw"][-3])

    def test_unknown_nodes_left_out_and_moved_positions_refused(self):
        s = nh.merge(self.base, None, {**self.flows, ("AAAA", "ZZZZ"): {self.newest: 5.0}}, self.newest, {}, "x")
        self.assertNotIn(("AAAA", "ZZZZ"), {(l["a"], l["b"]) for l in s["links"]})
        moved = copy.deepcopy(s)
        moved["nodes"][0]["x"] += 1
        with self.assertRaises(AssertionError):
            nh.check(moved, self.base)

    def test_demand(self):
        rows = [dict(respondent="ERCO", type="D", period="2026-10-01T15", value="64661"),
                dict(respondent="ERCO", type="D", period="2026-10-01T16", value="64000"),
                dict(respondent="ERCO", type="D", period="2026-10-01T17", value=None),
                dict(respondent="BPAT", type="D", period="2026-10-01T16", value="5000")]
        d = nh.demand_of(rows)
        self.assertEqual(d, {"ERCO": {"2026-10-01T14:00:00Z": 64661.0, "2026-10-01T15:00:00Z": 64000.0}})
        s = nh.merge(self.base, None, self.flows, self.newest, d, "x")
        n = next(x for x in s["nodes"] if x["id"] == "ERCO")
        self.assertEqual((n["demand_mw"], n["demand_ts"], n["demand_src"]), (64000.0, "2026-10-01T15:00:00Z", "hourly"))
        self.assertEqual(len(n["demand_recent"]), 2)
        self.assertNotIn("demand_src", next(x for x in s["nodes"] if x["id"] == "PJM"))


class PairRule(unittest.TestCase):
    def test_rule(self):
        nodes = {"ERCO", "SWPP", "CEN", "MISO"}
        rows = [dict(period="2026-09-30T05", fromba="ERCO", toba="SWPP", value="-157"),
                dict(period="2026-09-30T05", fromba="SWPP", toba="ERCO", value="150"),   # ERCO sorts first: its report wins
                dict(period="2026-09-30T06", fromba="SWPP", toba="ERCO", value="140"),   # only SWPP reported: sign flipped
                dict(period="2026-09-30T05", fromba="ERCO", toba="CEN", value="189"),
                dict(period="2026-09-30T05", fromba="MISO", toba="TEX", value="10"),     # a region: left out
                dict(period="2026-09-30T05", fromba="MISO", toba="XXXX", value="10"),    # not a node: left out
                dict(period="2026-09-30T05", fromba="MISO", toba="SWPP", value=None)]
        f, left = nh.pair_flows(rows, nodes)
        self.assertEqual(f[("ERCO", "SWPP")], {"2026-09-30T04:00:00Z": -157.0, "2026-09-30T05:00:00Z": -140.0})
        self.assertEqual(f[("CEN", "ERCO")], {"2026-09-30T04:00:00Z": -189.0})
        self.assertEqual(left, {("MISO", "XXXX")})
        self.assertNotIn(("MISO", "SWPP"), f)

    def test_newest_full_hour(self):
        f = {(f"A{i:03d}", "ZZZ"): {"2026-09-30T01:00:00Z": 1.0, "2026-09-30T02:00:00Z": 1.0} for i in range(100)}
        for i in range(95):
            f[(f"A{i:03d}", "ZZZ")]["2026-09-30T03:00:00Z"] = 1.0
        for i in range(60):
            f[(f"A{i:03d}", "ZZZ")]["2026-09-30T04:00:00Z"] = 1.0
        newest, per = nh.newest_full_hour(f)
        self.assertEqual(newest, "2026-09-30T03:00:00Z")  # 95 of a median 100 is complete; 60 is not
        self.assertEqual(per["2026-09-30T04:00:00Z"], 60)


@unittest.skipUnless(NODE, "node is not installed")
class Fallback(unittest.TestCase):
    def pick(self, fetched):
        code = ("import { pickSnapshot } from './lib/network.ts'; import fs from 'node:fs';"
                "const c = JSON.parse(fs.readFileSync('data/grid_network.json', 'utf-8'));"
                "const f = JSON.parse(fs.readFileSync(0, 'utf-8'));"
                "const r = pickSnapshot(f === 'COMMITTED_NEWER' ? { ...c, hours: c.hours.map(() => '2000-01-01T00:00:00Z') } : f, c);"
                "console.log(r.from + ' ' + r.snap.hours.at(-1));")
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120,
                           input=json.dumps(fetched))  # on stdin: a whole snapshot is too long for a command line
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip().splitlines()[-1].split()

    def test_fallback(self):
        end = committed()["hours"][-1]
        self.assertEqual(self.pick(None), ["committed", end])  # Storage unreachable
        self.assertEqual(self.pick({"built": "x", "nodes": []}), ["committed", end])  # not whole
        self.assertEqual(self.pick("COMMITTED_NEWER"), ["committed", end])  # older than the committed one
        s = nh.merge(committed(), None, {}, later(end, 2), {}, "2026-10-01T18:00:00Z")
        self.assertEqual(self.pick(s), ["storage", later(end, 2)])

    def test_page_reads_storage_with_revalidation_and_catches(self):
        page = src("site", "app", "network", "page.tsx")
        self.assertIn("export const revalidate = 3600", page)
        self.assertIn("next: { revalidate: HOURLY }", page)
        self.assertIn("catch {", page)
        self.assertIn("pickSnapshot(await hourly(), committed)", page)
        self.assertIn("Newest hour:", page)
        self.assertIn("The color updates daily", src("site", "app", "network", "Network.tsx"))


class Workflow(unittest.TestCase):
    def test_never_db_git_or_overlap(self):
        wf = src(".github", "workflows", "hourly-network.yml")
        self.assertIn("--skip-if-busy", wf)
        self.assertIn("group: hourly-network", wf)
        self.assertIn('cron: "0 0-13,15-23 * * *"', wf)
        self.assertIn("workflow_dispatch", wf)
        for bad in ("SUPABASE_DB_URL", "git commit", "git push", "contents: write", "run_daily"):
            self.assertNotIn(bad, wf)
        py = src("warehouse", "derived", "network_hourly.py")
        for bad in ("/rest/v1", "iso_prices", "write_status", "warehouse/output", "psycopg"):
            self.assertNotIn(bad, py.split('"""', 2)[2], bad)
        self.assertEqual(nh.BUSY, ("daily-prices.yml", "weekly-vacuum.yml"))
        # the daily run still builds the committed snapshot (the fallback)
        self.assertIn("grid_network.py", src("warehouse", "run_daily.sh"))

    def test_storage_url_from_a_supabase_url_with_a_path(self):
        # the dispatched run failed here: the secret carries /rest/v1, and Storage is beside it, not under it
        self.assertEqual(nh.origin("https://abc.supabase.co/rest/v1/"), "https://abc.supabase.co")
        self.assertEqual(nh.public_url(nh.origin("https://abc.supabase.co")),
                         "https://abc.supabase.co/storage/v1/object/public/erw-public/network/grid_network.json")

    def test_check_values_reads_the_hourly_demand(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('p[0] === "netsnap"', cv)
        self.assertIn("erw-public/network/grid_network.json", cv)
        self.assertTrue(re.search(r'netsnap\|\$\{pick\.id\}\|demand_mw', src("site", "app", "network", "Network.tsx")))

    def test_no_em_dashes(self):
        for p in (("warehouse", "derived", "network_hourly.py"), (".github", "workflows", "hourly-network.yml"), ("site", "lib", "network.ts"),
                  ("site", "app", "network", "page.tsx"), ("site", "app", "network", "Network.tsx"), ("tests", "test_session54.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
