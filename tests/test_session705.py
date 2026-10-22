"""Session 705: time to connect on the All grids tab (docs/methods/siting.md). The median months from queue entry to
operation by grid, from Berkeley Lab's file, recomputed here from the table where it is on this machine; no median
under five requests; the newest decided large-load rule of the grid from "Your load"'s own rules file; ERCOT's approved
large loads from its reports; the measured waits held. No request, no model call."""
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import siting_page as sp  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


SCRIPT = """
const F = await import('./scripts/siting-files.mjs');
const S = await import('./lib/siting.ts');
const d = await F.dc(); const f = F.files();
const out = {};
for (const id of ['ercot:HB_HUBAVG', 'caiso:TH_SP15_GEN-APND', 'nyiso:N.Y.C.', 'isone:.H.INTERNAL_HUB', 'miso:INDIANA.HUB', 'pjm:grid', 'spp:SPPNORTH_HUB']) {
  const c = S.connectCell(f, S.rowOf(f, id));
  out[id] = { c, key: S.sitingStat(f, 'allgrids|connect|' + id, d) ?? null, ll: S.sitingStat(f, 'allgrids|llapproved|' + id, d) ?? null };
}
process.stdout.write(JSON.stringify(out));
"""


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=600, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class Connect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()
        cls.f = json.loads(src("site", "data", "siting", "connect.json"))

    def test_the_file_is_the_table_s_where_it_is_here(self):
        # session 718: from the data machine's interconnection_durations where it is held, else Berkeley Lab's file
        for d in (os.path.join(ROOT, "runs", "archive_restore"), os.path.join(os.path.dirname(ROOT), "erw", "runs", "archive_restore"), os.path.join(ROOT, "warehouse", "output")):
            q = os.path.join(d, "interconnection_durations.csv")
            if os.path.exists(q) and self.f["table"] == "interconnection_durations":
                again = sp.connect_from_durations(q)
                self.assertEqual({k: v for k, v in again.items() if k != "built"}, {k: v for k, v in self.f.items() if k != "built"})
                return
        p = os.path.join(ROOT, "warehouse", "output", "lbnl_interconnection_queue.csv")
        if not os.path.exists(p):
            p = os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output", "lbnl_interconnection_queue.csv")
        if not os.path.exists(p):
            raise unittest.SkipTest("lbnl_interconnection_queue is not on this machine")
        again = sp.connect_file(p)
        self.assertEqual({k: v for k, v in again.items() if k != "built"}, {k: v for k, v in self.f.items() if k != "built"})

    def test_the_median_and_the_floor_of_five(self):
        self.assertEqual((self.f["from"], self.f["to"], self.f["min_n"]), (2023, 2025, 5))
        for g, v in self.f["grids"].items():
            self.assertEqual(v["median"] is None, v["n"] < 5, g)
        self.assertEqual(self.o["ercot:HB_HUBAVG"]["key"], self.f["grids"]["ercot"]["median"])
        self.assertIsNone(self.o["isone:.H.INTERNAL_HUB"]["key"])
        self.assertIn("Fewer than 5", self.o["isone:.H.INTERNAL_HUB"]["c"]["gen"]["why"])

    def test_the_rule_is_the_newest_decided_one(self):
        rules = json.loads(src("site", "data", "datacenter", "rules.json"))
        for rid, g in (("ercot:HB_HUBAVG", "ercot"), ("pjm:grid", "pjm"), ("spp:SPPNORTH_HUB", "spp")):
            want = sorted((x for x in rules["grids"][g]["rows"] if x["status_class"] == "decided"), key=lambda x: x["date"])[-1]
            self.assertEqual(self.o[rid]["c"]["rule"]["date"], want["date"])
        self.assertIsNone(self.o["miso:INDIANA.HUB"]["c"]["rule"])
        self.assertIn("paused", self.o["miso:INDIANA.HUB"]["c"]["ruleWhy"])

    def test_ercot_s_approved_large_loads_and_the_held_waits(self):
        st = json.loads(src("site", "data", "large_load_status.json"))
        newest = sorted((r for r in st["reports"] if r["approved"] is not None), key=lambda r: r["day"])[-1]
        self.assertEqual(self.o["ercot:HB_HUBAVG"]["ll"], newest["approved"])
        self.assertIsNone(self.o["caiso:TH_SP15_GEN-APND"]["ll"])
        self.assertIn("held", self.o["nyiso:N.Y.C."]["c"]["wait"])
        self.assertIn("why", self.o["ercot:HB_HUBAVG"]["c"]["wait"])

    def test_the_tab_draws_the_keys(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("check={`allgrids|connect|${r.id}`}", v)
        self.assertIn("check={`allgrids|llapproved|${r.id}`}", v)
        self.assertIn('<Held table="large_load_waits"', v)


if __name__ == "__main__":
    unittest.main()
