"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 4).

The consumption view of /demand ranks "where industrial and commercial load is growing fastest" by a billing class's
retail sales. Customers move between classes: in the twelve months to August 2026 Texas's commercial sales rose 13.7 TWh
while its industrial sales fell 7.7 TWh. The Monthly Energy Review's sector totals hold the electrical system's losses.
The data tests run where the tables are (the data machine's warehouse/output, or a folder named by ERW_AUDIT_TABLES).
"""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def table(name):
    for d in (os.environ.get("ERW_AUDIT_TABLES"), os.path.join(ROOT, "warehouse", "output")):
        if d and os.path.exists(os.path.join(d, name)):
            return os.path.join(d, name)
    return None


def months(a, b):
    y, m, out = int(a[:4]), int(a[5:]), []
    while f"{y:04d}-{m:02d}" <= b:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


class ASectorIsABillingClass(unittest.TestCase):
    def test_texas_commercial_up_while_industrial_down(self):
        path = table("eia_retail_sales_monthly.csv")
        if not path:
            self.skipTest("eia_retail_sales_monthly is not held on this machine")
        want = {f"eia:retail_sales:TX:{s}" for s in ("IND", "COM", "ALL")}
        v = {}
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.reader(line for line in f if not line.startswith("#"))
            head = next(rd)
            e, var, t, val = head.index("entity"), head.index("variable"), head.index("ts_utc"), head.index("value")
            for r in rd:
                if r[e] in want and r[var] == "retail_sales":
                    v[(r[e].split(":")[-1], r[t][:7])] = float(r[val])
        if ("IND", "2026-08") not in v:
            self.skipTest("the table held does not reach August 2026")
        cur, prev = months("2025-09", "2026-08"), months("2024-09", "2025-08")
        ch = {s: sum(v[(s, m)] for m in cur) - sum(v[(s, m)] for m in prev) for s in ("IND", "COM", "ALL")}
        self.assertGreater(ch["COM"], 10_000_000)
        self.assertLess(ch["IND"], -5_000_000)
        self.assertLess(ch["ALL"], ch["COM"])

    def test_industrial_total_holds_losses(self):
        path = table("eia_sector_energy_consumption_monthly.csv")
        if not path:
            self.skipTest("eia_sector_energy_consumption_monthly is not held on this machine")
        s = {}
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.reader(line for line in f if not line.startswith("#"))
            head = next(rd)
            e, t, val = head.index("entity"), head.index("ts_utc"), head.index("value")
            for r in rd:
                if r[t][:4] == "2025":
                    s[r[e]] = s.get(r[e], 0.0) + float(r[val])
        self.assertAlmostEqual(s["eia:TEICBUS"], s["eia:TNICBUS"] + s["eia:LOICBUS"], delta=0.01)
        self.assertGreater(s["eia:LOICBUS"] / s["eia:TEICBUS"], 0.10)

    def test_the_view_and_its_note_say_it(self):
        view = src("site", "app", "consumption", "view.tsx")
        self.assertIn("A sector is the class a utility bills a customer under, and customers move between classes, so one sector's growth can be another's loss", view)
        self.assertIn("The months are EIA's estimates from its monthly sample of sellers, revised when the annual survey is in", view)
        self.assertIn("A sector's total energy consumed holds its share of the electrical system's losses", view)
        self.assertIn("## What a sector's change is and is not (session 10214)", src("docs", "methods", "consumption.md"))


if __name__ == "__main__":
    unittest.main()
