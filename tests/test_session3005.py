"""Session 3005 (chain 164): the findings hunt, family generation, the mix (deep/generation.py), and the US first.

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
import generation as gen  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402
from test_session3001 import synthetic  # noqa: E402


def write(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a test table\n")
        frame.to_csv(f, index=False, lineterminator="\n")


def tables(d):
    rng = np.random.default_rng(3005)
    months = pd.date_range("2014-01-01", "2016-12-01", freq="MS").strftime("%Y-%m-%dT00:00:00Z")
    rows = []
    for st in ("US", "TX", "DC"):
        for src in ("ALL", "SUN", "WND", "COW", "NG", "DPV"):
            ts = months if not (st == "TX" and src == "SUN") else months[6:]       # a source missing some months counts as zero
            rows.append(pd.DataFrame({"entity": f"eia:generation:{st}:{src}", "variable": "net_generation", "ts_utc": ts,
                                      "value": np.round(rng.uniform(5000, 20000, len(ts)) * (10 if src == "ALL" else 1), 1), "geo": f"US-{st}"}))
    write(d, "eia_state_generation_monthly", pd.concat(rows))
    mrows = []
    for ent in ("iso:ercot", "iso:caiso"):
        for src in gen.MIX:
            for h in range(24):
                v = rng.uniform(-300 if src == "storage" else 0, 5000, len(months))
                mrows.append(pd.DataFrame({"entity": ent, "variable": f"avg_{src}_mw_h{h:02d}", "ts_utc": months, "value": np.round(v, 1)}))
    write(d, "generation_mix_hourly_profile", pd.concat(mrows))


class Reproduce(unittest.TestCase):
    def test_every_candidate_reproduces_from_the_table(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            hm.clear_cache()
            for P in gen.CANDIDATES:
                got = P["_fn"](d)
                regions = sorted({r["region"] for r in got["rows"]})
                self.assertTrue(regions, P["name"])
                if P["name"] == "small_solar_ratio":
                    self.assertNotIn("state_dpv_DC", regions)
                for region in [r for r in regions if r.endswith("_TX") or r.endswith("_mix")][:2]:
                    want = {r["year"]: r["value"] for r in got["rows"] if r["region"] == region}
                    path = os.path.join(d, f"r_{P['name']}.py")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(P["reproduce"](region)["py"])
                    table = "generation_mix_hourly_profile" if region.endswith("_mix") else "eia_state_generation_monthly"
                    r = subprocess.run([sys.executable, "-I", path, os.path.join(d, table + ".csv")], capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, (P["name"], r.stderr))
                    printed = {int(ln.split()[0]): float(ln.split()[1]) for ln in r.stdout.strip().splitlines()}
                    self.assertEqual(sorted(printed), sorted(want), (P["name"], region))
                    for y in want:
                        self.assertAlmostEqual(printed[y], want[y], places=5, msg=(P["name"], region, y))
                    do = P["reproduce"](region)["do"]
                    self.assertNotIn("///", do)
                    self.assertIn("destring value, replace force", do)
                    self.assertTrue(all("\n" not in b for b in do.strip("\n").split("\n\n")), P["name"])
            hm.clear_cache()


class UsFirst(unittest.TestCase):
    def test_the_united_states_is_kept_before_a_state_that_moved_more(self):
        P = builder.candidate("t", "testfam", synthetic([("state_x_US", 1.0), ("state_x_TX", 9.0), ("state_x_CA", 5.0)]), "percent", 1, 8000, 1.0,
                              "T", "t", lambda w: w, "Limits.", lambda region: {"py": '"""x"""\n', "do": "* x\n"}, consequence=2)
        P["rank"], P["rank_region"] = (lambda c: abs(c["change"])), gen._us_first
        with tempfile.TemporaryDirectory() as d, mock.patch.object(builder, "DOCS", os.path.join(d, "docs")), \
                mock.patch.object(hunt, "blocked_grids", lambda meta_dir=None: set()):
            s = builder.run("testfam", [P], d, dry_run=True, log=lambda m: None, out_root=os.path.join(d, "runs"))
        self.assertEqual(sorted(r["region"] for r in s["results"] if r["drafted"]), ["state_x_TX", "state_x_US"])


if __name__ == "__main__":
    unittest.main()
