"""Audit of Automated Analysis, finding 2 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): held and
paused grids' figures reach public files.

NYISO and SPP are held (daily_chart.HELD, the ruling of 12 October 2026); ISO-NE, MISO and NYISO are "license needed"
(warehouse/metadata/license_status.csv, from 21 October); MISO is paused. Shown here, on main:
  the impact study's default download holds NYISO New York City's daily prices as its control;
  the template gallery under docs/analysis/gallery/ (copied whole to the site's public/analysis-files/) holds charts of
    NYISO, ISO-NE and MISO with their figures;
  a week's results.json holds watch_nyiso_reg's headline value;
  run.py and watch.py never read license_status.csv;
  hunt.grid_of gives the deep drafts 8 and 9's regions (EIA's New York and New England) no held grid, so builder.run
    drafts them;
  the scanner chooses its tables from coverage.csv's license only.
The fix moves what a reader can see: the owner's ruling. Passes on main.

No table, no request, no model call; the environment is read, never set."""
import glob
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
HELD = {"nyiso", "isone", "miso", "spp"}


def text(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class HeldGridsInPublicFiles(unittest.TestCase):
    def test_impact_download_holds_nyiso_control(self):
        t = text("site", "public", "findings", "erw_2026_impact_event_control.csv")
        head = [ln for ln in t.splitlines() if ln.startswith("#")]
        self.assertTrue(any("NYISO" in ln and "control" in ln for ln in head))
        rows = [ln.split(",") for ln in t.splitlines() if not ln.startswith("#")]
        col = rows[0].index("control_value")
        vals = [r[col] for r in rows[1:] if len(r) > col and r[col] not in ("", "nan")]
        self.assertGreaterEqual(len(vals), 28)

    def test_gallery_holds_held_and_paused_grids(self):
        gal = os.path.join(ROOT, "docs", "analysis", "gallery")
        for iso in ("nyiso", "isone", "miso"):
            files = glob.glob(os.path.join(gal, "*", f"*iso={iso}_*.json"))
            self.assertTrue(files, iso)
            with_data = [p for p in files if '"data":[' in text(os.path.relpath(p, ROOT))]
            self.assertTrue(with_data, iso)
        self.assertIn('fs.cpSync(analysisDir, publicAnalysis', text("site", "scripts", "build-content.mjs"))

    def test_weekly_results_hold_nyiso(self):
        found = False
        for p in glob.glob(os.path.join(ROOT, "docs", "analysis", "2026-W*", "results.json")):
            for r in json.load(open(p, encoding="utf-8")).get("results", []):
                if r.get("template") == "watch_nyiso_reg" and (r.get("headline") or {}).get("value") is not None:
                    found = True
        self.assertTrue(found)
        for f in ("run.py", "watch.py"):
            self.assertNotIn("license_status", text("warehouse", "analysis", f))

    def test_deep_drafts_8_and_9_pass_the_grid_check(self):
        import hunt
        for region in ("rp_can_ny", "rn_ne"):
            self.assertNotIn(hunt.grid_of(region), HELD)
        self.assertIn("hunt.grid_of(region) in blocked", text("warehouse", "analysis", "findings", "deep", "builder.py"))

    def test_scanner_reads_coverage_license_only(self):
        t = text("warehouse", "analysis", "findings", "findings_scanner.py")
        self.assertIn('r.get("license") != "public"', t)
        self.assertNotIn("license_status", t)


if __name__ == "__main__":
    unittest.main()
