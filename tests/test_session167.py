"""Session 167: the project map, one page (/map, in review).

The page's file (site/data/map.json) is the four tables' rows as warehouse/derived/project_map.py reads them: EIA's
units with EIA's own status codes in the owner's words, the queue positions not withdrawn with the held queues left
out (the list site/lib/resources.ts keeps), the datacenters placed in a US state. The page's functions
(site/lib/projectmap.ts) select and add up what an independent count of the file gives, and keep a choice in the
address and read it back. Version 1 and version 2 are kept unrouted and /map/v2 redirects to /map. No network.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import project_map as pm  # noqa: E402

OWNER_WORDS = {  # the owner's file of 8 October 2026, session 167, word for word
    "p": "Planned, regulatory approvals not started", "l": "Regulatory approvals pending", "t": "Regulatory approvals received, not under construction",
    "u": "Under construction, half or less complete", "v": "Under construction, more than half complete", "ts": "Construction complete, not yet operating",
    "ot": "Other", "operating": "Operating",
}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = json.loads(src("site", "data", "map.json"))

    def test_one_column_a_field_a_kind_after_another(self):
        f = self.f
        n = f["counts"]["rows"]
        for k in ("k", "n", "s", "g", "t", "st", "mw", "la", "lo", "pr", "id", "o", "c", "tx", "d"):
            self.assertEqual(len(f[k]), n, k)
        self.assertEqual([k["slug"] for k in f["kinds"]], ["operating", "planned", "queue", "datacenter"])
        for ki, kind in enumerate(f["kinds"]):
            rows = range(kind["start"], kind["start"] + kind["rows"])
            self.assertTrue(all(f["k"][i] == ki for i in rows), kind["slug"])
            mw = [f["mw"][i] if f["mw"][i] is not None else -1 for i in rows]
            self.assertEqual(mw, sorted(mw, reverse=True), kind["slug"])        # the largest first inside a kind
            self.assertTrue(all(f["statuses"][f["st"][i]]["kind"] == ki for i in rows), kind["slug"])
        self.assertEqual(sum(k["rows"] for k in f["kinds"]), n)
        self.assertEqual(len(f["more"]["operating"]["code"]), f["kinds"][0]["rows"])
        self.assertEqual(len(f["more"]["queue"]["status"]), f["kinds"][2]["rows"])
        self.assertEqual(len(f["more"]["datacenter"]["urls"]), f["kinds"][3]["rows"])
        self.assertEqual(len(set(f["id"])), n)

    def test_eias_own_statuses_in_the_owners_words(self):
        eia = [s for s in self.f["statuses"] if s["kind"] in (0, 1)]
        self.assertEqual({s["slug"]: s["name"] for s in eia}, OWNER_WORDS)
        self.assertEqual([s["slug"] for s in eia], ["operating", "p", "l", "t", "u", "v", "ts", "ot"])
        # queue positions and datacenters keep their own statuses
        self.assertTrue(all(s["slug"].startswith("q-") for s in self.f["statuses"] if s["kind"] == 2))
        self.assertTrue(all(s["slug"].startswith("dc-") for s in self.f["statuses"] if s["kind"] == 3))
        self.assertNotIn("q-withdrawn", [s["slug"] for s in self.f["statuses"]])     # a withdrawn position is not on the map

    def test_held_queues_never_reach_the_file(self):
        shown_false = set(re.findall(r'id: "([a-z]+)", label: "[^"]+", shown: false', src("site", "lib", "resources.ts")))
        self.assertEqual(shown_false, set(pm.QUEUE_HELD))                           # the one list a person switches
        shown_true = set(re.findall(r'id: "([a-z]+)", label: "[^"]+", shown: true', src("site", "lib", "resources.ts")))
        self.assertEqual(shown_true, set(pm.QUEUE_SHOWN))
        queue = self.f["kinds"][2]
        ids = self.f["id"][queue["start"]:queue["start"] + queue["rows"]]
        self.assertFalse([i for i in ids if i.split("_queue:")[0] in pm.QUEUE_HELD])
        for h in self.f["held"]:
            self.assertIn(h["grid"], pm.QUEUE_HELD)
            if h["grid"] == "miso":
                self.assertEqual(h["words"], "paused while terms are reviewed")

    def test_datacenters_are_in_a_us_state_with_no_grid_guessed(self):
        dc = self.f["kinds"][3]
        rows = range(dc["start"], dc["start"] + dc["rows"])
        self.assertTrue(all(self.f["states"][self.f["s"][i]] for i in rows))
        self.assertTrue(all(self.f["grids"][self.f["g"][i]]["slug"] == "none" for i in rows))


class FromTheTables(unittest.TestCase):
    """The file is project_map.py's build of the tables (skipped without the tables, as on GitHub's runner)."""

    @classmethod
    def setUpClass(cls):
        cls.out = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
        if not all(os.path.exists(os.path.join(cls.out, t + ".csv")) for t in pm.PAGE_TABLES):
            raise unittest.SkipTest("the four tables are not on this machine")
        cls.f = json.loads(src("site", "data", "map.json"))

    def test_the_file_is_the_build_of_the_tables(self):
        built = pm.build_page(self.out)
        if built["vintages"] != self.f["vintages"]:
            self.skipTest(f"the tables on this machine are of other vintages ({built['vintages']}) than the site's copy ({self.f['vintages']})")
        for k in built:
            if k != "built":
                self.assertEqual(built[k], self.f[k], k)

    def test_every_planned_unit_keeps_eias_code(self):
        d = pm.units(self.out)
        if sorted(set(d["vintage"])) != [self.f["vintage"]]:
            self.skipTest("the EIA tables on this machine are of another month than the site's copy")
        planned = d[d["status"] != "operating"]
        theirs = sorted(self.f["statuses"][self.f["st"][i]]["slug"] for i in range(len(self.f["k"])) if self.f["k"][i] == 1)
        self.assertEqual(sorted(planned["eia_status"].str.lower()), theirs)


class TheConnector(unittest.TestCase):
    def test_the_raw_code_stands_beside_the_folded_status(self):
        text = src("warehouse", "connectors", "eia860.py")
        self.assertIn('"status": code.map(status_map)', text)       # the folded status, kept
        self.assertIn('"eia_status": code, "eia_status_label": label', text)   # EIA's own code and label, beside it


class TheFunctions(unittest.TestCase):
    """lib/projectmap.ts against an independent count of the file."""

    def test_select_and_totals_are_the_files_own(self):
        f = json.loads(src("site", "data", "map.json"))
        slugs = {w: [x["slug"] for x in f[k]] for w, k in (("kind", "kinds"), ("grid", "grids"), ("tech", "techs"), ("status", "statuses"))}
        slugs["state"] = [s or "na" for s in f["states"]]
        addresses = ["", "?grid=ercot", "?kind=queue&grid=caiso,ercot", "?tech=solar,battery&state=CA,TX", "?status=u,v,ts", "?kind=datacenter&min=100",
                     "?kind=operating,planned&min=500&max=1300", "?grid=none", "?kind=planned&status=p,l,t&state=AZ"]
        got = node("const m = await import('./lib/projectmap.ts'); const f = JSON.parse((await import('node:fs')).default.readFileSync('data/map.json', 'utf-8'));"
                   f"console.log(JSON.stringify({json.dumps(addresses)}.map((a) => {{ const c = m.parseChoice(a, f); const p = m.select(f, c); const t = m.totals(f, p);"
                   " return { q: m.queryOf(c, f), rows: t.rows, kind: t.byKind.map((x) => [x.rows, Math.round(x.mw)]) }; })));")
        for a, g in zip(addresses, got):
            want = {}
            for part in [p for p in a.lstrip("?").split("&") if p]:
                k, v = part.split("=")
                want[k] = v
            lo, hi = float(want.get("min", -1)), float(want.get("max", -1))
            pick = []
            for i in range(len(f["k"])):
                ok = True
                for w, col in (("kind", "k"), ("grid", "g"), ("tech", "t"), ("status", "st"), ("state", "s")):
                    if w in want and (want[w] == "none" or slugs[w][f[col][i]] not in want[w].split(",")):
                        ok = False
                mw = f["mw"][i]
                if (lo >= 0 or hi >= 0) and (mw is None or (lo >= 0 and mw < lo) or (hi >= 0 and mw > hi)):
                    ok = False
                if ok:
                    pick.append(i)
            self.assertEqual(g["rows"], len(pick), a)
            kinds = [[sum(1 for i in pick if f["k"][i] == k), math.floor(sum(f["mw"][i] or 0 for i in pick if f["k"][i] == k) + 0.5)] for k in range(4)]
            self.assertEqual(g["kind"], kinds, a)
            # the address read back is the same address, in the page's own order
            self.assertEqual(g["q"], a if a != "?kind=queue&grid=caiso,ercot" else "?kind=queue&grid=ercot,caiso", a)

    def test_a_state_click_toggles_and_never_leaves_a_dead_end(self):
        out = node("const m = await import('./lib/projectmap.ts'); let s = null; const seen = [];"
                   "for (const i of [5, 9, 5, 9]) { s = m.clickState(s, i, 53); seen.push(s); }"
                   "console.log(JSON.stringify({ seen, all: m.toggle([0, 1, 2], 3, 4), none: m.toggle([0], 0, 4), unknown: m.parseChoice('?grid=nowhere&state=none', { kinds: [], grids: [{ slug: 'ercot' }], techs: [], statuses: [], states: ['TX'] }) }));")
        self.assertEqual(out["seen"], [[5], [5, 9], [9], None])
        self.assertIsNone(out["all"])          # every option ticked is no choice at all
        self.assertEqual(out["none"], [])
        self.assertIsNone(out["unknown"]["grid"])
        self.assertEqual(out["unknown"]["state"], [])


class ThePage(unittest.TestCase):
    def test_one_page_one_address(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "app", "map", "page.tsx")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "app", "map", "v2")))
        for rel in ("_retired/map-v1/page.tsx", "_retired/map-v1/Body.tsx", "_retired/map-v1/MapView.tsx", "_retired/map-v1/groups.ts",
                    "_retired/map-v2/page.tsx", "_retired/map-v2/MapV2.tsx"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "app", *rel.split("/"))), rel)
        self.assertIn('{ source: "/map/v2", destination: "/map", permanent: true }', src("site", "next.config.ts"))
        release = src("site", "lib", "release.ts")
        self.assertRegex(release, r'"/map":\s*"review"')
        self.assertRegex(release, r'"/map/v2":\s*"review"')       # its line stays

    def test_what_the_owner_kept_and_deleted(self):
        page, client = src("site", "app", "map", "page.tsx"), src("site", "app", "map", "ProjectMap.tsx")
        for piece in ('title="Choose"', "data-map-summary", "data-map-total", "data-map-drawn", "data-map-reset", "UnitCard", 'title="By technology"', "Select all", "Clear"):
            self.assertIn(piece, client, piece)
        self.assertIn("<SourceLine", page)
        for which in ("kind", "grid", "tech", "status", "state"):
            self.assertIn(f'which="{which}"', client)
        for gone in ("Beside it: the interconnection queue", "What is selected", "What the inventory leaves out", "How to read it", "What the map holds",
                     "legendselectchanged", "/api/entity"):
            self.assertNotIn(gone, page + client, gone)
        self.assertNotIn("legend:", client)                         # the chart has no legend that toggles; the key is plain
        # the card's fields: left out of the page, read once from /map/card, a route built from the same file (never Supabase)
        self.assertIn("faceOf(f)", page)
        self.assertIn('fetch("/map/card")', client)
        route = src("site", "app", "map", "card", "route.ts")
        self.assertIn('import mapJson from "@/data/map.json"', route)
        self.assertIn('export const dynamic = "force-static"', route)
        self.assertNotRegex(route, r"from \"@/lib/(supabase|data)\"")
        keys = re.search(r"CARD_KEYS = \[([^\]]+)\] as const", src("site", "lib", "projectmap.ts")).group(1)
        self.assertEqual(tuple(pm.CARD_KEYS), tuple(k.strip().strip('"') for k in keys.split(",")))
        method = src("docs", "methods", "energy_projects.md")
        for moved in ("existing and proposed generating units at electric power plants with 1 megawatt or greater of combined nameplate capacity",
                      "Retired units", "Energy for planned batteries", "A row is a generating unit, not a plant", "Hybrid is a queue position naming more than one technology"):
            self.assertIn(moved, method)

    def test_no_em_dash(self):
        for rel in ("site/app/map/page.tsx", "site/app/map/ProjectMap.tsx", "site/lib/projectmap.ts", "site/scripts/check-map.mjs", "site/scripts/check-map-v2.mjs",
                    "warehouse/derived/project_map.py", "docs/methods/energy_projects.md", "tests/test_session167.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
