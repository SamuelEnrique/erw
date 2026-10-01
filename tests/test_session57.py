"""Session 57: the Texas severance refund finder.

Energy Research Warehouse (ERW). No network, no model. The data is internal and lives only on a warehouse machine:
the tests that need it skip where it is absent.
1. Internal stays internal: the statewide table, the county files and the finder's outputs are ignored by git, and no
   tracked file holds them; the finder's page and download answer 404 without the internal token.
2. The credit tiers are the rules file's bounds, as lib/severance.ts reads them.
3. By hand, on real leases: a low-producing gas well's months, tax and saving recomputed from its county's lines and
   the monthly Henry Hub means, independently of the finder; and the lease tool agrees with the finder on a gas and an
   oil lease (site/scripts/test-finder.mjs).
4. The two-year inactive flags: never a new lease (the RRC's first month for the lease is before the gap), a saving no
   larger than the tax, and none estimated for an older lease; one recomputed by hand from its 48 months.

    python -m unittest tests.test_session57 -v
"""

import datetime as dt
import glob
import gzip
import json
import os
import shutil
import subprocess
import sys
import unittest
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import severance_screen as ss  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
FLAGS = os.path.join(OUT, "severance_screen_flags.csv.gz")
PART = os.path.join(OUT, "rrc_lease_production_statewide")
HAVE = os.path.exists(FLAGS) and os.path.exists(os.path.join(PART, "_index.csv"))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flags():
    with gzip.open(FLAGS, "rt", encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(FLAGS, skiprows=n, dtype={"operator_no": str, "district": str, "wells": int, "wells_open": int})


def hh_means():
    path = os.path.join(OUT, "eia_fuel_spot_prices.csv")
    n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    d = pd.read_csv(path, skiprows=n, usecols=["entity", "variable", "ts_utc", "value"])
    d = d[(d["entity"] == "eia:henry_hub") & (d["variable"] == "spot_price")]
    return d.groupby(d["ts_utc"].str[:7])["value"].mean().to_dict()


class Internal(unittest.TestCase):
    def test_ignored_and_untracked(self):
        paths = ["warehouse/output/rrc_lease_production_statewide/_index.csv", "warehouse/output/severance_screen_flags.csv.gz",
                 "warehouse/output/severance_screen_summary.json", "warehouse/raw/rrc_pdq/x/counties48/MARTIN.dsv.gz"]
        r = subprocess.run(["git", "check-ignore", *paths], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(sorted(r.stdout.split()), sorted(paths))
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertFalse([t for t in tracked if "rrc_lease_production_statewide" in t or t.startswith("warehouse/output/severance_screen")
                          or "counties48" in t])
        self.assertFalse([t for t in tracked if t.startswith("site/data/") and ("rrc" in t or "screen" in t)])

    def test_pages_behind_the_token(self):
        page = src("site", "app", "severance", "finder", "page.tsx")
        self.assertIn("if (!tokenOk(token)) notFound();", page)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertIn('export const dynamic = "force-dynamic"', page)
        route = src("site", "app", "severance", "finder", "download", "route.ts")
        self.assertIn('if (!tokenOk(new URL(req.url).searchParams.get("token"))) return new Response("Not found", { status: 404 });', route)
        lib = src("site", "lib", "finder.ts")
        self.assertIn('want.length >= 24 && token === want', lib)
        real = src("site", "app", "severance", "lease", "real", "page.tsx")
        self.assertIn('.find((r) => r[0] === county)', real)  # the county from the index, never a path from the query
        self.assertNotIn("severance/finder", src("site", "lib", "pages.ts"))  # not in the public nav

    def test_credit_tiers_are_the_bounds(self):
        R = ss.rules_of()
        self.assertEqual(ss.credit_pct(R["lp_gas"], "2025-01"), (100, 1.2))
        self.assertEqual(ss.credit_pct(R["lp_oil"], "2025-01"), (0, 43.3))
        self.assertEqual(ss.credit_pct(R["lp_gas"], "2024-12"), (None, None))
        opt = {"certified": {"prices": [{"period": "x", "price": 3.2}, {"period": "y", "price": 2.75}, {"period": "z", "price": 3.5}]}, "bounds": R["lp_gas"]["bounds"]}
        self.assertEqual([ss.credit_pct(opt, p)[0] for p in "xyz"], [25, 50, 25])  # 3.50 is "over $3 to $3.50"

    def test_no_em_dashes(self):
        for p in (("warehouse", "connectors", "rrc_statewide.py"), ("warehouse", "derived", "severance_screen.py"), ("site", "lib", "finder.ts"),
                  ("site", "app", "severance", "finder", "page.tsx"), ("site", "app", "severance", "finder", "download", "route.ts"),
                  ("site", "scripts", "test-finder.mjs"), ("tests", "test_session57.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


@unittest.skipUnless(HAVE, "the finder's internal outputs are not on this machine")
class ByHand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fl = flags()
        cls.index = pd.read_csv(os.path.join(PART, "_index.csv")).set_index("county")["file"].to_dict()

    def county(self, c):
        p = os.path.join(PART, self.index[c])
        with gzip.open(p, "rt", encoding="utf-8") as f:
            n = sum(1 for ln in f if ln.startswith("#"))
        return pd.read_csv(p, skiprows=n, dtype=str)

    def test_a_gas_well_by_hand(self):
        hh, R = hh_means(), ss.rules_of()
        cand = self.fl[(self.fl["rule"] == "tx_lp_gas") & (self.fl["months"] == 24)].sort_values(["savings", "lease_id"], ascending=[False, True])
        for f in cand.head(20).itertuples():
            d = self.county(f.county)
            d = d[(d["lease_id"] == f.lease_id) & (d["filed"] == "Y")].sort_values("month")
            gas = d.set_index("month")["gas_mcf"].astype(float)
            base = sum(gas[m] * hh[m] * 0.075 for m in gas.index if gas[m] > 0)
            if abs(base - f.base_tax) > 0.05:
                continue  # a lease reported in another county too: its county file holds a share
            saving, months = 0.0, []
            for m in gas.index:
                if gas[m] <= 0:
                    continue
                prior = [ss.shift(m, -k) for k in (3, 2, 1)]
                held = [p for p in prior if p in gas.index and gas[p] > 0]
                held = held if len(held) == 3 else [m]  # as lib/lease.ts txGasAverage: a full three-month history, else the month
                per_day = sum(gas[p] for p in held) / sum(ss.days_in(p) for p in held)
                if per_day <= 90:
                    months.append(m)
                    pct = ss.credit_pct(R["lp_gas"], m)[0] or 0
                    saving += gas[m] * hh[m] * 0.075 * pct / 100
            # the first month's prior months lie before the 24 in the county file: the finder read them from the 48
            w0 = gas.index[0]
            self.assertEqual([m for m in months if m != w0], [m for m in f.month_list.split(";") if m != w0], f.lease_id)
            self.assertAlmostEqual(saving, f.savings, delta=0.01 * 24)
            self.assertAlmostEqual(base, f.base_tax, delta=0.05)
            return
        self.fail("no single-county gas lease among the 20 largest")

    def test_the_lease_tool_agrees(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        r = subprocess.run([node, os.path.join("scripts", "test-finder.mjs")], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("the lease tool agrees on both leases", r.stdout)

    def test_inactive_flags(self):
        ina = self.fl[self.fl["rule"] == "tx_inactive"]
        self.assertTrue(len(ina) > 0)
        self.assertTrue((ina["savings"] <= ina["base_tax"] + 0.01).all())
        self.assertTrue((ina.loc[ina["case"] == "older", "savings"] == 0).all())
        z = zipfile.ZipFile(ss.rs.dump_path())
        firsts = ss.lease_firsts(z).to_dict()
        months48, _ = ss.rs.months_of(z, ss.HISTORY)
        start = f"{months48[0][:4]}-{months48[0][4:]}"
        for f in ina.itertuples():
            lf = firsts.get(tuple(f.lease_id.split("-")))
            self.assertIsNotNone(lf, f.lease_id)
            if f.case == "older":
                self.assertLessEqual(lf, ss.shift(start, -12), f.lease_id)
        # one seen lease by hand, from its county's 48 months
        f = ina[ina["case"] == "seen"].sort_values(["savings", "lease_id"], ascending=[False, True]).iloc[0]
        raw = glob.glob(os.path.join(os.path.dirname(ss.rs.dump_path()), "counties48", "*.dsv.gz"))
        fp = next(p for p in raw if os.path.basename(p).startswith(f["county"].replace(" ", "_") + ".dsv"))
        d = ss.rs.county_frame(fp)
        d = d[(d["OIL_GAS_CODE"] + "-" + d["DISTRICT_NO"] + "-" + d["LEASE_NO"]) == f["lease_id"]]
        vol = {c: pd.to_numeric(d[c]).groupby(d["CYCLE_YEAR_MONTH"]).sum() for c in ss.rs.VOLS}
        tot = sum(vol.values())
        prod = sorted(m for m, v in tot.items() if v > 0)
        first = f["first"].replace("-", "")
        before = [m for m in prod if m < first]
        gap = (int(first[:4]) * 12 + int(first[4:])) - (int(before[-1][:4]) * 12 + int(before[-1][4:])) - 1
        self.assertGreaterEqual(gap, 24, f["lease_id"])
        self.assertIn(f"after {gap} months without production", f["test"])


if __name__ == "__main__":
    unittest.main()
