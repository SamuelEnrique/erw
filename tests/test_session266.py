"""Session 266: the Grid tool, deep, and the gravity view (the chain of 14 October 2026).

Energy Research Warehouse (ERW). What is held here:
- the gravity shape's rule (site/lib/networkGravity.ts), run in Node on typed cases: a net importer sits nearer the
  center than a net exporter, a larger generation draws a larger circle, a grid with no tie in the hour sits on the
  middle ring, a grid with zero or no generation is an outline (never a stand-in), nothing overlaps the Lower 48 or
  leaves the frame; and the panel's own sum of net imports;
- the third toggle and its address word (site/lib/networkMap.ts, site/app/network/Network.tsx), the colors from the
  tokens only (no literal color in the new files);
- the lag's check key (net|lag in site/lib/network.ts) on a typed snapshot, and the two places that show it: the Now
  view's sentence and the line under the network;
- the replication files: the CSV's header and kinds, the do-file and its Python mirror printing the same names, and the
  mirror run on the committed CSV; Ask's briefing stating the hourly carbon's real span;
- the review pack's existence and the old note's absence (the form itself is tests/test_session262.py); no em dash.
Nothing here sets the environment, reads a table or makes a request.
"""

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
GRID = os.path.join(SITE, "public", "grid")
NODE = shutil.which("node")
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node(code):
    r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(NODE, "node is not installed")
class TheGravityRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # typed cases, not data: the Lower 48 at 400,000 MW; A imports 30 percent of its generation, B exports 10
        # percent, C has no tie in the hour, D has zero generation and imports, E's generation is not held
        cls.lay = node(
            "import { gravityLayout, GRAVITY } from './lib/networkGravity.ts';"
            "const gen = { US48: 400000, CISO: 20000, ERCO: 60000, ISNE: 10000, MISO: 0, NYIS: null, PJM: 80000, SWPP: 30000 };"
            "const net = { CISO: 6000, ERCO: -6000, ISNE: null, MISO: 500, NYIS: 1000, PJM: 0, SWPP: -100000 };"
            "console.log(JSON.stringify({ g: GRAVITY, l: gravityLayout(gen, net) }));")
        cls.g = cls.lay["g"]
        cls.at = {p["id"]: p for p in cls.lay["l"]["places"]}

    def test_an_importer_is_nearer_the_center_than_an_exporter(self):
        self.assertLess(self.at["CISO"]["d"], self.g["D_MID"])
        self.assertGreater(self.at["ERCO"]["d"], self.g["D_MID"])
        self.assertEqual(self.at["PJM"]["d"], self.g["D_MID"])   # a net exchange of zero: on the ring
        self.assertAlmostEqual(self.at["CISO"]["share"], 0.3)
        self.assertEqual(self.at["CISO"]["d"], self.g["D_MID"] - self.g["D_SPAN"])  # 30 percent is past the full pull

    def test_the_area_follows_generation(self):
        self.assertAlmostEqual(self.at["ERCO"]["r"], self.g["R_CENTER"] * (60000 / 400000) ** 0.5)
        self.assertGreater(self.at["PJM"]["r"], self.at["ERCO"]["r"])

    def test_no_tie_sits_on_the_ring(self):
        self.assertEqual(self.at["ISNE"]["state"], "no-ties")
        self.assertIsNone(self.at["ISNE"]["net"])
        self.assertEqual(self.at["ISNE"]["d"], self.g["D_MID"])

    def test_zero_or_no_generation_is_an_outline_never_a_stand_in(self):
        self.assertEqual(self.at["MISO"]["state"], "zero-generation")
        self.assertIsNone(self.at["MISO"]["share"])
        self.assertEqual(self.at["MISO"]["r"], self.g["R_MIN"])
        self.assertLess(self.at["MISO"]["d"], self.g["D_MID"])   # it imports: the full pull in
        self.assertEqual(self.at["NYIS"]["state"], "no-generation")
        self.assertIsNone(self.at["NYIS"]["gen"])

    def test_nothing_overlaps_the_center_or_leaves_the_frame(self):
        c = self.g["SIZE"] / 2
        for p in self.at.values():
            self.assertGreaterEqual(p["d"], self.g["R_CENTER"] + p["r"] + self.g["GAP"] - 1e-9, p["id"])
            self.assertLessEqual(p["d"] + p["r"], c - self.g["GAP"] + 1e-9, p["id"])
        self.assertEqual(len(self.at), 7)

    def test_the_net_imports_are_the_panels_sum(self):
        got = node("import { netImportAt } from './lib/networkGravity.ts';"
                   "const links = [{ a: 'CISO', b: 'BPAT', mw: [-300, null] }, { a: 'AZPS', b: 'CISO', mw: [200, null] }, { a: 'CISO', b: 'NEVP', mw: [50, null] }];"
                   "console.log(JSON.stringify([netImportAt(links, 'CISO', 0), netImportAt(links, 'CISO', 1)]));")
        self.assertEqual(got, [300 + 200 - 50, None])

    def test_the_lag_key(self):
        got = node("import { netValue } from './lib/network.ts';"
                   "const s = { hours: ['2026-10-12T03:00:00Z'], links: [], nodes: [] };"
                   "console.log(JSON.stringify([netValue(s, 'net|lag|2026-10-12T03:00:00Z|2026-10-14T08:05:18Z'), netValue(s, 'net|lag|2026-10-12T04:00:00Z|2026-10-14T08:05:18Z') ?? null]));")
        self.assertEqual(got, [53, None])

    def test_the_shape_word(self):
        got = node("import { parseShape, withShape } from './lib/networkMap.ts';"
                   "console.log(JSON.stringify([parseShape('?shape=gravity'), parseShape('?shape=map'), parseShape(''), withShape('?view=live', 'gravity'), withShape('', 'network')]));")
        self.assertEqual(got, ["gravity", "map", "network", "?view=live&shape=gravity", ""])


class ThePage(unittest.TestCase):
    def test_the_third_toggle_and_the_same_panel(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('(["map", "network", "gravity"] as const)', n)
        self.assertIn('shape === "gravity" && gravity ? (', n)
        self.assertIn("onPick={(id) => setPick(snap.nodes.find((n) => n.id === id) ?? null)} />", n)
        g = src("site", "app", "network", "NetworkGravity.tsx")
        self.assertIn("data-gravity-hover", g)

    def test_colors_from_the_tokens_only(self):
        for parts in (("site", "app", "network", "NetworkGravity.tsx"), ("site", "lib", "networkGravity.ts")):
            text = src(*parts)
            self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,6}\b|rgb\(", text), "/".join(parts))
        self.assertIn('stroke="var(--color-rule)"', src("site", "app", "network", "NetworkGravity.tsx"))

    def test_the_lag_is_said_twice_and_keyed(self):
        now = src("site", "components", "grid", "NowView.tsx")
        # also covered by site/scripts/test-grid-render.mjs: view_now on /grid?grid=ercot&view=mix
        self.assertIn("check={`net|lag|${xHour}|${snap.built}`}", now)
        # also covered by site/scripts/test-grid-render.mjs: older_the sentence on /grid?grid=ercot&view=mix
        self.assertIn("hours before the latest hourly refresh of EIA-930&apos;s interchange", now)
        nv = src("site", "components", "grid", "NetworkView.tsx")
        # also covered by site/scripts/test-grid-render.mjs: view_exchange on /grid?grid=ercot&view=gravity
        self.assertIn("check={`net|lag|${shownHour}|${snap.built}`}", nv)
        # also covered by site/scripts/test-grid-render.mjs: view_gravity on /grid?grid=ercot&view=gravity
        self.assertIn("on the second morning after it", nv)

    def test_a_grid_with_no_tie_is_not_written_as_the_lower_48(self):
        now = src("site", "components", "grid", "NowView.tsx")
        self.assertIn('grid.slug === "us48" ? "by grid" : "not reported"', now)

    def test_generation_is_read_for_the_gravity_shape(self):
        d = src("site", "app", "network", "data.ts")
        self.assertIn('series("eia930_all_generation", { variable: "net_generation_mw", since })', d)


class TheReplication(unittest.TestCase):
    def test_the_csv_holds_its_header_and_kinds(self):
        with open(os.path.join(GRID, "erw_2026_grid_replication.csv"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertTrue(all(line.startswith("#") for line in lines[:8]))
        self.assertTrue(lines[6].startswith("# snapshot_built,") and lines[7].startswith("# hour_shown,"))
        self.assertEqual(lines[8], "kind,id,other,ts_utc,value,unit")
        rows = list(csv.DictReader(lines[8:]))
        self.assertEqual({r["kind"] for r in rows}, {"node", "tie", "demand", "generation"})
        self.assertIn("US48", [r["id"] for r in rows if r["kind"] == "generation"])

    def test_the_do_file_and_the_mirror_print_the_same_names(self):
        do = src("site", "public", "grid", "erw_2026_grid_replication.do")
        py = src("site", "public", "grid", "erw_2026_grid_replication.py")
        for name in ("hour_shown", "snapshot_built", "lag_hours", "nodes", "pairs_reporting", "generation_", "ties_", "net_import_",
                     "net_share_of_demand_pct_", "gravity_share_", "gravity_r_", "gravity_d_"):
            self.assertIn(f'"{name}', do, name)
            self.assertIn(f"{name}", py, name)
        self.assertIn("varnames(9) rowrange(10)", do)
        self.assertIn("HEADER_LINES = 8", py)
        for k in ("s_rc = 80", "s_dmid = 205", "s_dspan = 90", "s_sfull = 0.25", "s_rmin = 6", "s_gap = 4"):
            self.assertIn(k, do)
        self.assertIn("SIZE, R_CENTER, D_MID, D_SPAN, S_FULL, R_MIN, GAP = 640, 80, 205, 90, 0.25, 6, 4", py)

    def test_the_mirror_runs_on_the_committed_file(self):
        r = subprocess.run([sys.executable, os.path.join(GRID, "erw_2026_grid_replication.py")], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        got = dict(line.split(" = ") for line in r.stdout.strip().splitlines())
        self.assertEqual(len([k for k in got if k.startswith("gravity_d_")]), 7)
        self.assertTrue(got["lag_hours"].isdigit())


class TheBriefingAndThePack(unittest.TestCase):
    def test_ask_is_told_the_hourly_carbons_span(self):
        llms = src("package", "llms.txt")
        self.assertIn("carbon_intensity_hourly holds about 14 months hour by", llms)
        self.assertIn("2025-08-09T16:00 to 2026-10-10T23:00 UTC as read on", llms)
        self.assertNotIn("`_daily` (last ~30 days)", llms)
        self.assertIn("about 14 months hour by", src("site", "lib", "chat", "spec.json"))

    def test_the_pack_replaces_the_note(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "reviews", "packs", "grid.md")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "howitworks", "grid.md")))
        self.assertIn("(../reviews/packs/grid.md)", src("docs", "howitworks", "README.md"))
        self.assertIn("## The gravity shape (session 266)", src("docs", "methods", "grid_network.md"))

    def test_no_em_dash(self):
        for parts in (("site", "lib", "networkGravity.ts"), ("site", "app", "network", "NetworkGravity.tsx"), ("site", "app", "network", "Network.tsx"),
                      ("site", "components", "grid", "NowView.tsx"), ("site", "components", "grid", "NetworkView.tsx"), ("site", "lib", "network.ts"),
                      ("site", "lib", "networkMap.ts"), ("site", "app", "network", "data.ts"), ("site", "scripts", "write-grid-replication.mjs"),
                      ("site", "scripts", "check-grid-replication.mjs"), ("site", "public", "grid", "erw_2026_grid_replication.do"),
                      ("site", "public", "grid", "erw_2026_grid_replication.py"), ("site", "public", "grid", "erw_2026_grid_replication.csv"),
                      ("docs", "reviews", "packs", "grid.md"), ("docs", "methods", "grid_network.md"), ("package", "llms.txt"), ("tests", "test_session266.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        for parts in (("archive", "sessions", "SESSION_266_REPORT.md"), ("docs", "brand", "review-266", "README.md")):
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
