"""Audit of "What a battery earns", finding 11 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the
replication proves a window the page has left.

1. replication/battery/replicate.py reads only the public dispatch file and page_figures.json, both written for the last
   twelve months October 2025 to September 2026 (USD 81.40 per kW). It compares the one with the other, so it passes
   whatever the live table says: it exits 0 here.
2. On a machine with battery_stack_monthly (the data machine's main checkout), the page's own rule (the newest whole held
   month whose eleven months before it are held) is applied to the table's ERCOT foresight 4-hour rows; the window must
   be the replication's. Session 9840 read the table of 14 November 2026: November 2025 to October 2026, USD 80.34 per
   kW, so this fails there until the public file and the page figures are written again. Skipped where the table is not.
Nothing is written (replicate.py prints only)."""
import csv
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REP = os.path.join(ROOT, "replication", "battery")


def page_window():
    with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
        w = json.load(f)["window"]["last_twelve"]
    return w[0], w[1]


class ReplicationWindow(unittest.TestCase):
    def test_replication_passes_on_its_own_window(self):
        out = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stdout[-2000:] + out.stderr[-2000:])
        self.assertEqual(page_window(), ("2025-10", "2026-09"))

    def test_the_tables_window_is_the_replications(self):
        path = os.path.join(ROOT, "warehouse", "output", "battery_stack_monthly.csv")
        if not os.path.exists(path):
            self.skipTest("battery_stack_monthly is not on this machine")
        pre = "foresight_4h_"
        m = {}
        with open(path, encoding="utf-8") as f:
            rows = csv.reader(line for line in f if not line.startswith("#"))
            head = next(rows)
            ix = {c: i for i, c in enumerate(head)}
            for r in rows:
                if r[ix["entity"]] == "ercot:HB_HUBAVG" and r[ix["variable"]].startswith(pre):
                    m.setdefault(r[ix["ts_utc"]][:7], {})[r[ix["variable"]][len(pre):]] = float(r[ix["value"]])
        held = {k: "revenue_total_usd_per_mw" in d and d["days_held"] / d["days_in_month"] >= 0.9 - 1e-9 for k, d in m.items()}
        whole = {k: d["days_held"] + d.get("days_left_out", 0) >= d["days_in_month"] for k, d in m.items()}

        def back(k, i):
            y, mo = int(k[:4]), int(k[5:7]) - i
            while mo < 1:
                y, mo = y - 1, mo + 12
            return f"{y}-{mo:02d}"
        last = next(k for k in sorted(m, reverse=True) if held[k] and whole[k] and all(held.get(back(k, i)) for i in range(12)))
        self.assertEqual((back(last, 11), last), page_window(), "the page's last twelve months are not the replication's")


if __name__ == "__main__":
    unittest.main()
