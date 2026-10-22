"""Session 728 (chain 062): a zone's own demand growth from EIA-930's sub-regions (eia930_subba_demand_hourly and its
yearly tables), in the tab's headroom file, beside the grid's. The builder maps each load zone of the tab to its
sub-regions by a written table (ZONE_SUBBA, with the reason); the library picks the window it can fill (the grid's
twelve months where every month is held, else the last two whole calendar years) and says which; a row the mapping does
not name keeps the grid's figure, said so. Key allgrids|zdemand|<row>. No request, no model call, no database read."""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page as sp  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheMapping(unittest.TestCase):
    def test_every_load_zone_of_the_tab_is_mapped_with_a_reason(self):
        idx = json.loads(src("site", "data", "datacenter", "index.json"))
        zones = [f"{g}:{r['id']}" for g, v in idx["grids"].items() for r in v["regions"] if g in ("ercot", "nyiso", "isone") and not r["id"].startswith("HB_") and r["id"] != ".H.INTERNAL_HUB"]
        self.assertEqual(len(zones), 27)   # 8 ERCOT load zones, 11 NYISO zones, 8 ISO-NE zones
        for z in zones:
            self.assertIn(z, sp.ZONE_SUBBA, z)
            codes, note = sp.ZONE_SUBBA[z]
            self.assertTrue(codes and all(":" in c for c in codes), z)
            self.assertGreater(len(note), 20, z)
        # NYISO's and ISO-NE's zones are one sub-region each; ERCOT's North, South and West span two or three weather zones
        self.assertEqual(sp.ZONE_SUBBA["nyiso:N.Y.C."][0], ["NYIS:ZONJ"])
        self.assertEqual(sp.ZONE_SUBBA["isone:.Z.MAINE"][0], ["ISNE:4001"])
        self.assertEqual(sorted(sp.ZONE_SUBBA["ercot:LZ_NORTH"][0]), ["ERCO:EAST", "ERCO:NCEN", "ERCO:NRTH"])

    def test_the_builder_keeps_whole_months_and_sums_nothing_twice(self):
        # a fixture of two sub-regions over three months: one month short of 95 percent of its hours is left out, and a
        # row given in two files (the rolling table and a yearly one) is counted once (the last file wins)
        d = tempfile.mkdtemp()
        try:
            def write(name, rows):
                p = os.path.join(d, name)
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write("# a fixture\n")
                    w = csv.writer(f)
                    w.writerow(["entity", "variable", "ts_utc", "value"])
                    w.writerows(rows)
                return p
            rows = []
            for day in range(1, 32):
                for h in range(24):
                    rows.append(["eia930_subba:NYIS:ZONJ", "demand_mw", f"2025-01-{day:02d}T{h:02d}:00:00Z", "100"])
            for day in range(1, 29):
                for h in range(24):
                    rows.append(["eia930_subba:NYIS:ZONJ", "demand_mw", f"2025-02-{day:02d}T{h:02d}:00:00Z", "200"])
            for day in range(1, 20):   # March short: 19 of 31 days
                for h in range(24):
                    rows.append(["eia930_subba:NYIS:ZONJ", "demand_mw", f"2025-03-{day:02d}T{h:02d}:00:00Z", "300"])
            rows.append(["eia930_subba:NYIS:ZONJ", "other", "2025-01-01T00:00:00Z", "9"])        # another variable: ignored
            rows.append(["eia930_subba:SWPP:OKGE", "demand_mw", "2025-01-01T00:00:00Z", "9"])   # a sub-region no row maps to: ignored
            p1 = write("eia930_subba_demand_hourly_2025.csv", rows)
            p2 = write("eia930_subba_demand_hourly.csv", [r[:3] + ["150"] for r in rows if r[2].startswith("2025-02")])   # February again, other values
            part = sp.subba_part([p1, p2])
            self.assertEqual(list(part["months"].keys()), ["NYIS:ZONJ"])
            self.assertEqual(sorted(part["months"]["NYIS:ZONJ"].keys()), ["2025-01", "2025-02"])
            self.assertEqual(part["months"]["NYIS:ZONJ"]["2025-01"], [100.0, 744, 744])
            self.assertEqual(part["months"]["NYIS:ZONJ"]["2025-02"], [150.0, 672, 672])   # the last file read wins
            self.assertEqual((part["held_from"], part["held_to"]), ("2025-01", "2025-02"))
            self.assertEqual(part["zone_subba"]["nyiso:N.Y.C."], ["NYIS:ZONJ"])
            self.assertIn("ZONJ", part["zone_notes"]["nyiso:N.Y.C."])
        finally:
            shutil.rmtree(d, ignore_errors=True)


SCRIPT = """
const S = await import('./lib/siting.ts');
const F = await import('./scripts/siting-files.mjs');
const f = F.files(), dc = await F.dc();
const z = (id) => S.zoneGrowth(f.demand, f.headroom, S.rowOf(f, id));
const out = { nyc: z('nyiso:N.Y.C.'), houston: z('ercot:LZ_HOUSTON'), north: z('ercot:LZ_NORTH'), maine: z('isone:.Z.MAINE'), hub: z('ercot:HB_HUBAVG'),
  statNyc: S.sitingStat(f, 'allgrids|zdemand|nyiso:N.Y.C.', dc), statHub: S.sitingStat(f, 'allgrids|zdemand|ercot:HB_HUBAVG', dc),
  grid: S.demandGrowth(f.demand, 'nyiso'), subba: !!f.headroom?.subba, held: f.headroom?.subba ? [f.headroom.subba.held_from, f.headroom.subba.held_to] : null };
process.stdout.write(JSON.stringify(out));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode and "TypeScript" in (r.stderr or "") and "strip" in (r.stderr or ""):
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


class TheZoneGrowth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = run()

    def test_the_file_holds_the_sub_regions_and_the_zones_draw_a_figure(self):
        o = self.out
        self.assertTrue(o["subba"], "headroom.json has no subba part")
        for k in ("nyc", "houston", "north", "maine"):
            self.assertIn("pct", o[k], (k, o[k]))
            self.assertIn(o[k]["window"], ("twelve", "years"))
            self.assertGreater(o[k]["mw"], 0)
            self.assertTrue(o[k]["note"])
        # the North load zone sums three weather zones; its mean is far above Houston's one
        self.assertEqual(len(o["north"]["codes"]), 3)
        self.assertGreater(o["north"]["mw"], o["houston"]["mw"])
        # a window the grid's twelve months cannot fill falls back to two whole years, said so
        if o["nyc"]["window"] == "years":
            self.assertEqual(o["nyc"]["to"], f"{o['nyc']['year']}-12")

    def test_the_key_and_the_hub(self):
        o = self.out
        self.assertAlmostEqual(o["statNyc"], o["nyc"]["pct"], places=9)
        self.assertIn("why", o["hub"])
        self.assertIsNone(o.get("statHub"))
        # the grid's own figure is untouched by the zone's
        self.assertIn("pct", o["grid"])


class TheViewsWords(unittest.TestCase):
    def test_the_cell_and_the_builder(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("<ZoneGrowthLine r={r} />", v)
        self.assertIn("check={`allgrids|zdemand|${r.id}`}", v)
        self.assertIn('data-headroom-zone="none"', v)
        self.assertNotIn("@/lib/supabase", v)
        b = src("warehouse", "derived", "siting_page.py")
        self.assertIn('ap.add_argument("--subba"', b)
        r = src("warehouse", "replication", "siting.py")
        self.assertIn('allgrids|zdemand|', r)

    def test_no_em_dash(self):
        for p in (("site", "app", "cost-of-power", "AllGridsView.tsx"), ("site", "lib", "siting.ts"), ("warehouse", "derived", "siting_page.py"), ("warehouse", "replication", "siting.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
