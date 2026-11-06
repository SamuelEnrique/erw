"""Session 3009 (chain 164): the queues (deep/queues.py), the shared reader's "#" fault, and a draft corrected in place.

Energy Research Warehouse (ERW). Small tables written here; no warehouse file, no network, no database.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings", "deep"))
sys.path.insert(0, os.path.dirname(__file__))
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402
import queues  # noqa: E402
from test_session3001 import synthetic  # noqa: E402


def lbnl_table(d):
    rng = np.random.default_rng(3009)
    rows = []
    for i in range(1500):
        qy = int(rng.integers(2003, 2025))
        q = pd.Timestamp(f"{qy}-01-01") + pd.Timedelta(days=int(rng.integers(0, 360)))
        fate = rng.choice(["on", "wd", "active"])
        on = (q + pd.Timedelta(days=int(rng.integers(200, 3000)))) if fate == "on" else pd.NaT
        wd = (q + pd.Timedelta(days=int(rng.integers(100, 2000)))) if fate == "wd" else pd.NaT
        t1 = rng.choice(["Solar", "Battery", "Wind", "Gas"])
        rows.append({"entity_id": f"lbnl:x:{i}", "name": f"Project #{i}, phase #2", "q_date": q.strftime("%Y-%m-%d"),
                     "on_date": "" if pd.isna(on) else on.strftime("%Y-%m-%d"), "wd_date": "" if pd.isna(wd) else wd.strftime("%Y-%m-%d"),
                     "q_status": fate, "region": rng.choice(["PJM", "CAISO", "MISO", "Southeast"]), "type_clean": t1, "type_1": t1,
                     "type_2": "Battery" if t1 == "Solar" and rng.random() < 0.4 else "", "type_3": "", "mw_1": round(float(rng.uniform(5, 500)), 1), "q_year": qy})
    with open(os.path.join(d, "lbnl_interconnection_queue.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n# its second header line\n")
        pd.DataFrame(rows).to_csv(f, index=False, lineterminator="\n")


class Reader(unittest.TestCase):
    def test_a_hash_inside_a_field_keeps_the_row_whole(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "t.csv"), "w", encoding="utf-8", newline="\n") as f:
                f.write("# header one\n# header two\nname,mw\n\"Solar #2\",150.5\nWind,20\n")
            got = common.read_table("t", d)
        self.assertEqual(list(got["name"]), ["Solar #2", "Wind"])
        self.assertEqual(list(got["mw"]), ["150.5", "20"])            # comment="#" left "Solar " and an empty mw


class Queues(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            lbnl_table(d)
            hm.clear_cache()
            for P in queues.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                for region in [r for r in regions if r.startswith("us_") or r.startswith("pjm_")][:2]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, "lbnl_interconnection_queue.csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
                    do = P["reproduce"](region)["do"]
                    self.assertNotIn("///", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()


class Correction(unittest.TestCase):
    def test_an_open_draft_is_corrected_under_its_own_id(self):
        P = builder.candidate("t", "testfam", synthetic([("ercot_A", 3.0), ("ercot_B", 2.0)]), "MW", 0, 8000, 1.0, "T", "t", lambda w: w,
                              "Limits.", lambda region: {"py": '"""x"""\n', "do": "* x\n"}, consequence=2)
        added, patched = [], []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: set()):
            s = builder.run("testfam", [P], d, dry_run=False, log=lambda m: None, out_root=os.path.join(d, "runs"), replace=True,
                            open_drafts=lambda: {"hunt|deep.testfam|t|ercot_A": "scan-deep-oldoldoldold"},
                            load=lambda rows, log: added.extend(r["id"] for r in rows) or [r["id"] for r in rows],
                            patch=lambda rows, log: patched.extend(r["id"] for r in rows) or [r["id"] for r in rows])
        self.assertEqual(patched, ["scan-deep-oldoldoldold"])            # the open draft keeps its id and is updated
        self.assertEqual(len(added), 1)
        self.assertTrue(added[0].startswith("scan-deep-") and added[0] != "scan-deep-oldoldoldold")
        self.assertEqual(sorted(s["loaded"]), sorted(patched + added))


if __name__ == "__main__":
    unittest.main()
