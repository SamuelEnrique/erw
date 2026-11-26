"""Session 10229 (the problems audit, finding 2): the "why it matters" of the bill questions (B3, B4 of "Prices and your
bill"). It said "Most of a home's bill pays for wires, programs and fixed charges, not the power itself"; on the default
Oncor bill the retailer's energy charge, the power as the home buys it, is more than half the bill, and the wires less
than half. What is small is the wholesale energy at the hub (about a quarter). The facts from site/data/bill_rules.json
and the live rows kept in replication/bill/source_rows.csv; the words from site/lib/problems.ts.
"""
import csv
import json
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RULES = os.path.join(ROOT, "site", "data", "bill_rules.json")
ROWS = os.path.join(ROOT, "replication", "bill", "source_rows.csv")
SRC = os.path.join(ROOT, "site", "lib", "problems.ts")


def texas(key):
    b = json.load(open(RULES, encoding="utf-8"))["bills"][key]
    kwh = b["defaults"]["kwh"]
    energy = kwh * b["energy_default"]["rate"]
    wires = sum(f["rate"] for f in b["fixed"]) + kwh * sum(p["rate"] for p in b["per_kwh"])
    return kwh, energy, wires


class TheDefaultTexasBills(unittest.TestCase):
    def test_the_energy_charge_is_more_than_half(self):
        for key in ("TX", "TXC"):
            kwh, energy, wires = texas(key)
            self.assertGreater(energy / (energy + wires), 0.5, key)
            self.assertLess(wires / (energy + wires), 0.5, key)
        kwh, energy, wires = texas("TX")
        self.assertEqual(round(energy / (energy + wires) * 100, 2), 57.12)

    def test_the_wholesale_energy_is_the_smaller_part(self):
        with open(ROWS, encoding="utf-8") as f:
            lw = [float(r["value"]) for r in csv.DictReader(line for line in f if not line.startswith("#"))
                  if r["entity"] == "ercot:HB_HUBAVG" and r["variable"] == "rt_load_weighted" and r["ts_utc"].startswith("2026-09")][0]
        kwh, energy, wires = texas("TX")
        self.assertLess(kwh * lw / 1000 / (energy + wires), 0.5)


class TheWords(unittest.TestCase):
    def test_why(self):
        src = open(SRC, encoding="utf-8").read()
        m = re.search(r"const billQ = .*?\n  \}\);", src, re.S)
        why = re.search(r'why: "([^"]*)"', m.group(0)).group(1)
        self.assertNotIn("not the power itself", why)
        self.assertIn("The wholesale energy is the smaller part of a home's bill.", why)
        self.assertIn("in Texas the retailer's energy charge alone is more than half the default bill", why)
        self.assertNotIn(chr(0x2014), why)


if __name__ == "__main__":
    unittest.main()
