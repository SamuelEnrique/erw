"""Audit of "What a datacenter pays", finding 3 (session 10203, docs/reviews/datacenter-model-audit-2026-11-26.md): the
load is a price taker at any size the form takes (0.1 to 10,000 MW, LIMITS in site/lib/datacenter.ts) and every dollar
is the figure for 1 MW times the size, yet until this branch no word on the page or in the note's list of what the model
cannot see said that the load's own demand is taken not to move the price.

1. Through the page's library (run by Node): the size reaches 10,000 MW, the price per MWh does not depend on it (no
   function of the months takes a size), and 10,000 MW is more than 15 percent of ERCOT's mean demand in the page's own 2026
   file. Where ERCOT's hourly load is on the machine (ERW_TABLES_DIR, or warehouse/output), a rough merit order (the
   median zone price by load in 1 GW bins over the page's last twelve months) moves the price by more than USD 2 per MWh
   at 10,000 MW. Passes on main: it shows the fault.
2. The fix on this branch, words only: the sentence under the cost table and the note's list say it. Fails on main."""
import bisect
import csv
import json
import os
import statistics
import subprocess
import unittest
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "datacenter")
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "datacenter.ts").replace("\\", "/")
JS = """
const L = await import(process.argv[1]);
const fs = await import("node:fs");
const dir = process.argv[2];
const index = JSON.parse(fs.readFileSync(dir + "/index.json", "utf-8"));
const x = L.inputsOf({ grid: "ercot", mw: "10000" }, index);
const files = index.grids.ercot.years.map((y) => JSON.parse(fs.readFileSync(dir + "/ercot_" + y + ".json", "utf-8")));
const s = L.span(L.lastTwelve(L.monthsRuled(files, "LZ_NORTH", "rt", { run: "flat", n: 0, pct: 0, shift: 0 }, "forecast").months));
console.log(JSON.stringify({ mw: x.mw, limit: L.LIMITS.mw[1], per: s.per, months: L.monthsRuled.length, mean: files.at(-1).demand_mean_mw }));
"""


def tables_dir():
    for d in (os.environ.get("ERW_TABLES_DIR"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, "ercot_zone_load_hourly.csv")):
            return d
    return None


class PriceTaker(unittest.TestCase):
    def test_size_scales_and_never_moves_the_price(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, LIB, DIR], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["mw"], 10000)
        self.assertEqual(r["limit"], 10000)
        self.assertGreater(10000 / r["mean"], 0.15)              # 16.6 percent of ERCOT's mean demand, priced as if it were nothing

    @unittest.skipUnless(tables_dir(), "ercot_zone_load_hourly is not on this machine")
    def test_rough_merit_order(self):
        idx = json.load(open(os.path.join(DIR, "index.json"), encoding="utf-8"))
        prices = {}
        for y in idx["grids"]["ercot"]["years"]:
            if y < 2025:
                continue
            f = json.load(open(os.path.join(DIR, f"ercot_{y}.json"), encoding="utf-8"))
            s = f["regions"]["LZ_NORTH"]["rt"]
            t0 = datetime(y, 1, 1, 6)
            for i, v in enumerate(s["v"]):
                if v is not None:
                    prices[(t0 + timedelta(hours=s["s"] + i)).strftime("%Y-%m-%dT%H:%M:%SZ")] = v
        pairs = []
        with open(os.path.join(tables_dir(), "ercot_zone_load_hourly.csv"), encoding="utf-8") as fh:
            for r in csv.DictReader(l for l in fh if not l.startswith("#")):
                if r["entity"] == "ercot:system" and "2025-11-01T06" <= r["ts_utc"] < "2026-11-01T06" and r["ts_utc"] in prices:
                    pairs.append((float(r["value"]), prices[r["ts_utc"]]))
        self.assertGreater(len(pairs), 6000)
        bins = {}
        for load, p in pairs:
            bins.setdefault(int(load // 1000), []).append(p)
        med = {b: statistics.median(v) for b, v in bins.items() if len(v) >= 20}
        ks = sorted(med)

        def curve(load):
            b = int(load // 1000)
            return med[b] if b in med else med[ks[min(bisect.bisect_left(ks, b), len(ks) - 1)]]
        rise = sum(curve(load + 10000) - curve(load) for load, _ in pairs) / len(pairs)
        self.assertGreater(rise, 2.0)

    def test_the_page_says_it(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "page.tsx"), encoding="utf-8") as f:
            self.assertIn("its own demand is taken not to move that price (at hundreds of megawatts and more it would", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "datacenter_pays_algorithm.md"), encoding="utf-8") as f:
            self.assertIn("- The load is a price taker: its own demand is taken not to move the price, at any size from 0.1 to 10,000 MW", f.read())


if __name__ == "__main__":
    unittest.main()
