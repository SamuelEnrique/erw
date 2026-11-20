"""Audit of "What a battery earns", finding 7 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the size
field runs to 5,000 MW and every dollar figure is the per-MW figure times the size (site/lib/batterystack.ts, inputsOf
and stat's `scaled`), so the battery is paid for reserve megawatts ERCOT never buys.

1. The page's library (run by Node) reads mw=5000 as 5,000 MW and scales the last twelve months' revenue by exactly 50
   against 100 MW.
2. The model's own awards in the public dispatch file, September 2026, against ERCOT's day-ahead ancillary service plan
   for the same hours (ercot_as_quantities, read when it is on the machine; otherwise the figures session 9840 read from
   it on 20 November 2026): at 5,000 MW the model holds more Regulation Down than ERCOT plans to buy in total in most
   hours (83.3 percent measured), and more than a quarter of the hours' revenue is for megawatts ERCOT does not buy.
It passes on main: it shows the fault. Nothing is written."""
import csv
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "batterystack.ts").replace("\\", "/")
# session 9840's read of ercot_as_quantities (retrieved 20261011T200229Z), 3 to 30 September 2026: the median and the
# lowest planned MW of each product over the 672 hours the public file also holds
PLAN_SEEN = {"regup": (387, 251), "regdn": (393, 252), "rrs": (2446, 2344), "ecrs": (1652, 1042), "nspin": (2176, 1670)}


def september():
    with open(CSV, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    return [{c: r[i] for c, i in ix.items()} for r in rows[1:] if r[ix["local_month"]] == "2026-09"]


def plan():
    """{hour_utc: {product: MW}} from the table when it is on the machine, else None."""
    path = os.path.join(ROOT, "warehouse", "output", "ercot_as_quantities.csv")
    if not os.path.exists(path):
        return None
    out = {}
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    ix = {c: i for i, c in enumerate(rows[0])}
    for r in rows[1:]:
        out.setdefault(r[ix["ts_utc"]], {})[r[ix["entity"]].split(":")[1].lower()] = float(r[ix["value"]])
    return out


class SizeBeyondTheMarket(unittest.TestCase):
    def test_page_scales_linearly_to_5000_mw(self):
        js = ("const B = await import(process.argv[1]);"
              "const rows = [];"
              "for (let k = 0; k < 12; k++) { const m = new Date(Date.UTC(2025, 9 + k, 1)).toISOString().slice(0, 7) + '-01T00:00:00Z';"
              "  for (const [v, x] of [['days_held', 30], ['days_left_out', 0], ['days_in_month', 30], ['revenue_total_usd_per_mw', 6783.5], ['revenue_energy_usd_per_mw', 4500], ['revenue_ancillary_usd_per_mw', 2283.5]])"
              "    rows.push({ variable: 'foresight_4h_' + v, ts_utc: m, value: x }); }"
              "const at = (mw) => B.stat(rows, [], B.inputsOf({ mw: String(mw) }), 'l12:total');"
              "console.log(JSON.stringify({ mw: B.inputsOf({ mw: '5000' }).mw, a: at(100), b: at(5000) }));")
        out = subprocess.run(["node", "--input-type=module", "-e", js, LIB], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(r["mw"], 5000)
        self.assertEqual(r["b"], 50 * r["a"])

    def test_awards_beyond_what_ercot_buys(self):
        hrs = september()
        self.assertEqual(len(hrs), 720)
        p = plan()
        S = 5000
        over = paid = excess = 0.0
        n = 0
        for h in hrs:
            q = p.get(h["hour_utc"]) if p is not None else None
            if p is not None and q is None:
                continue                                           # an hour the plan does not hold (1 and 2 September)
            n += 1
            aw = float(h["award_regdn_mw"])
            cap = q["regdn"] if q else PLAN_SEEN["regdn"][0]
            over += aw * S > cap
            for k in ("regup", "regdn", "rrs", "ecrs", "nspin"):
                a, price = float(h[f"award_{k}_mw"]), float(h[f"price_{k}_usd_mw"])
                c = q[k] if q else PLAN_SEEN[k][0]
                excess += max(0.0, a * S - c) * price
            paid += float(h["revenue_total_usd"]) * S
        self.assertGreater(over / n, 0.6, f"Regulation Down above ERCOT's whole plan in {100 * over / n:.1f} percent of hours")
        self.assertGreater(excess / paid, 0.2, f"{100 * excess / paid:.1f} percent of the revenue is for megawatts ERCOT does not buy")


if __name__ == "__main__":
    unittest.main()
