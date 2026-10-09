"""Session 105: the project map, version 2 (/map/v2, in review).

The site's copy of EIA's inventory is the two tables, unit for unit; the page's selection and totals
(site/lib/map2.ts) equal the tables' own for a spread of choices; the queue beside the map is the queue summary's;
the page says what the inventory leaves out, in EIA's words where they are EIA's. No network.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import project_map as pm  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
HELD = all(os.path.exists(os.path.join(OUT, t + ".csv")) for t in pm.TABLES)
STDIN = "JSON.parse(await new Promise((done) => { let s = ''; process.stdin.on('data', (d) => { s += d; }); process.stdin.on('end', () => done(s)); }))"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js, stdin=None):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180, input=stdin)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheFile(unittest.TestCase):
    def setUp(self):
        self.f = json.loads(src("site", "data", "map_v2.json"))

    def test_one_column_a_field_and_a_unit_a_position(self):
        n = self.f["counts"]["units"]
        for k in ("n", "s", "g", "t", "st", "mw", "y", "la", "lo"):
            self.assertEqual(len(self.f[k]), n, k)
        self.assertEqual(self.f["mw"], sorted(self.f["mw"], reverse=True))       # largest first
        self.assertEqual([g["slug"] for g in self.f["grids"]], ["ercot", "caiso", "pjm", "miso", "spp", "nyiso", "isone", "outside"])
        self.assertEqual([s["slug"] for s in self.f["statuses"]], ["operating", "under_construction", "planned"])
        self.assertIn("battery", [t["slug"] for t in self.f["techs"]])
        c = self.f["counts"]
        self.assertEqual(c["operating"] + c["under_construction"] + c["planned"], n)
        self.assertEqual(c["batteries"], self.f["t"].count([t["slug"] for t in self.f["techs"]].index("battery")))

    @unittest.skipUnless(HELD, "the EIA-860M tables are not on this machine")
    def test_it_is_the_two_tables_unit_for_unit(self):
        d = pm.units()
        if sorted(set(d["vintage"])) != [self.f["vintage"]]:
            self.skipTest("the tables on this machine are of another month than the site's copy")
        self.assertEqual(len(d), self.f["counts"]["units"])
        self.assertAlmostEqual(float(d["mw"].sum()), self.f["counts"]["mw"], places=0)
        names, states = self.f["names"], self.f["states"]
        grids = [g["slug"] for g in self.f["grids"]]
        techs = [t["slug"] for t in self.f["techs"]]
        statuses = [s["slug"] for s in self.f["statuses"]]
        mine = sorted(zip(d["name"], d["state"], d["grid"], d["tech"], d["status"], d["mw"].round(1), d["year"].map(lambda y: int(y) if y.isdigit() else 0)))
        theirs = sorted((names[self.f["n"][i]], states[self.f["s"][i]], grids[self.f["g"][i]], techs[self.f["t"][i]], statuses[self.f["st"][i]], self.f["mw"][i], self.f["y"][i])
                        for i in range(len(self.f["mw"])))
        self.assertEqual(mine, theirs)
        self.assertEqual(int((d["balancing_authority"] == "").sum()), self.f["counts"]["without_balancing_authority"])
        self.assertEqual(int((d["mw"] < 1).sum()), self.f["counts"]["under_1_mw"])
        # a battery is a storage unit whose prime mover is a battery, and nothing else
        self.assertEqual(int(((d["technology_group"] == "storage") & (d["prime_mover"] == "BA")).sum()), self.f["counts"]["batteries"])

    @unittest.skipUnless(HELD, "the EIA-860M tables are not on this machine")
    def test_the_pages_selection_is_the_tables_own(self):
        d = pm.units()
        if sorted(set(d["vintage"])) != [self.f["vintage"]]:
            self.skipTest("the tables on this machine are of another month than the site's copy")
        grids = [g["slug"] for g in self.f["grids"]]
        techs = [t["slug"] for t in self.f["techs"]]
        statuses = [s["slug"] for s in self.f["statuses"]]
        choices = [dict(grid=-1, tech=-1, status=-1, min=0, max=None), dict(grid=grids.index("ercot"), tech=-1, status=-1, min=0, max=None),
                   dict(grid=grids.index("ercot"), tech=techs.index("battery"), status=-1, min=0, max=None),
                   dict(grid=grids.index("caiso"), tech=techs.index("solar"), status=statuses.index("under_construction"), min=0, max=None),
                   dict(grid=grids.index("outside"), tech=techs.index("nuclear"), status=statuses.index("operating"), min=500, max=1300),
                   dict(grid=grids.index("pjm"), tech=techs.index("natural_gas"), status=statuses.index("planned"), min=0, max=None),
                   dict(grid=-1, tech=-1, status=-1, min=0, max=0.9)]
        got = node(f"const m = await import('./lib/map2.ts'); const f = (await import('node:fs')).default; const file = JSON.parse(f.readFileSync('data/map_v2.json', 'utf-8')); const cs = {STDIN};"
                   "console.log(JSON.stringify(cs.map((c) => { const p = m.select(file, { ...c, max: c.max === null ? Infinity : c.max }); const t = m.totals(file, p); return { units: t.units, mw: t.mw, by: t.byStatus }; })));",
                   stdin=json.dumps(choices))
        for c, g in zip(choices, got):
            x = d
            if c["grid"] >= 0:
                x = x[x["grid"] == grids[c["grid"]]]
            if c["tech"] >= 0:
                x = x[x["tech"] == techs[c["tech"]]]
            if c["status"] >= 0:
                x = x[x["status"] == statuses[c["status"]]]
            x = x[(x["mw"].round(1) >= c["min"]) & ((x["mw"].round(1) <= c["max"]) if c["max"] is not None else True)]
            self.assertEqual(g["units"], len(x), c)
            self.assertAlmostEqual(g["mw"], float(x["mw"].round(1).sum()), places=0, msg=str(c))
            for i, s in enumerate(statuses):
                self.assertEqual(g["by"][i]["units"], int((x["status"] == s).sum()), (c, s))
        self.assertGreater(got[2]["units"], 100)             # Texas has batteries
        self.assertGreater(got[6]["units"], 1000)            # and the file holds units under 1 MW


class TheLogic(unittest.TestCase):
    def test_a_size_is_a_number_or_it_is_nothing(self):
        out = node("const m = await import('./lib/map2.ts');"
                   "console.log(JSON.stringify(['200', ' 1,500 ', '0.5', '', 'abc', '-3', '1e3', '12 MW'].map((t) => m.sizeOf(t, -1))));")
        self.assertEqual(out, [200, 1500, 0.5, -1, -1, -1, -1, -1])

    def test_the_queue_beside_the_map_is_the_queue_summarys(self):
        q = json.loads(src("site", "data", "queues.json"))
        out = node("const m = await import('./lib/map2.ts'); const f = (await import('node:fs')).default; const q = JSON.parse(f.readFileSync('data/queues.json', 'utf-8'));"
                   "console.log(JSON.stringify({ ercot: m.queueRows(q.views, 'ercot', 'battery'), outside: m.queueRows(q.views, 'outside', 'all'), all: m.queueRows(q.views, 'all', 'solar') }));")
        by = {r["slug"]: r for r in out["ercot"]}
        self.assertEqual(by["all"]["mw"], q["views"]["ercot|all"]["whole"]["total_active_mw"])
        self.assertEqual(by["battery"]["requests"], q["views"]["ercot|battery"]["whole"]["total_active_requests"])
        self.assertEqual(sorted(r["slug"] for r in out["ercot"] if r["marked"]), ["battery", "solar_battery"])   # a battery answers to both
        self.assertEqual(sorted({r["region"] for r in out["outside"]}), ["Southeast, outside the ISOs", "West, outside the ISOs"])
        self.assertFalse(any(r["marked"] for r in out["outside"]))
        self.assertEqual(out["all"][0]["mw"], q["views"]["us|all"]["whole"]["total_active_mw"])
        self.assertEqual(sorted(r["slug"] for r in out["all"] if r["marked"]), ["solar", "solar_battery"])
        # a region with no request of a kind (offshore wind in the West) is "none in the file", never a zero made up
        for r in out["outside"]:
            key = ("west" if r["region"].startswith("West") else "southeast") + "|" + r["slug"]
            self.assertEqual(r["mw"] is None, key not in q["views"], key)


class ThePage(unittest.TestCase):
    def test_in_review_in_the_battery_pages_layout_and_says_what_is_left_out(self):
        page = src("site", "app", "_retired", "map-v2", "page.tsx")   # session 167: retired, kept unrouted
        client = src("site", "app", "_retired", "map-v2", "MapV2.tsx")
        for piece in ("ToolPage", "ToolHeader", "Fold", "SourceLine"):
            self.assertIn(f"<{piece}", page)
        for piece in ("InputPanel", "HeadlineRow", "ToolSection", "ToolTable"):
            self.assertIn(f"<{piece}", client)
        for choice in ('data-map-choice="grid"', 'data-map-choice="tech"', 'data-map-choice="status"', 'data-map-choice="min"', 'data-map-choice="max"'):
            self.assertIn(choice, client)
        self.assertIn('title="What the inventory leaves out"', page)
        # EIA's own sentence, as its page gives it (read 2026-10-04, https://www.eia.gov/electricity/data/eia860m/)
        self.assertIn("existing and proposed generating units at electric power plants with 1 megawatt or greater of combined nameplate capacity", page)
        for word in ("Retired units", "balancing authority", "Energy for planned batteries", "Puerto Rico"):
            self.assertIn(word, page)
        self.assertIn("a request is not a plant", client)
        self.assertIn("are not added", client)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/map/v2":\s*"review"')
        r = subprocess.run(["git", "log", "--format=%s", "-1", "--", "site/app/map/page.tsx", "site/app/map/Body.tsx", "site/app/map/MapView.tsx"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("Session 105", r.stdout)            # the older map is not this session's to touch

    def test_no_em_dash(self):
        for rel in ("site/lib/map2.ts", "site/app/_retired/map-v2/page.tsx", "site/app/_retired/map-v2/MapV2.tsx", "site/scripts/check-map-v2.mjs", "warehouse/derived/project_map.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
