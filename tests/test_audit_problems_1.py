"""Session 10229 (the problems audit, finding 1): the bill questions of "Prices and your bill" (B3, B4) name the price
their key uses. The key values the default bill's metered kWh at the latest complete month's load-weighted real-time
price of the bill's hub, against the bill before taxes; a student given only "how many dollars are wholesale energy"
could as well take the month's simple mean, which gives another answer. The facts are read from the live rows kept in
replication/bill/source_rows.csv (September 2026); the words from site/lib/problems.ts and the kept page figures.
"""
import csv
import json
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "site", "lib", "problems.ts")
ROWS = os.path.join(ROOT, "replication", "bill", "source_rows.csv")
KEPT = os.path.join(ROOT, "replication", "problem_sets", "page_figures.json")
BILL = {"caiso:TH_NP15_GEN-APND": 229.6299, "ercot:HB_HUBAVG": 95.2732}  # the default bills, USD (lib/bill.ts)


def rows():
    out = {}
    with open(ROWS, encoding="utf-8") as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            out[(r["entity"], r["variable"], r["ts_utc"][:7])] = float(r["value"])
    return out


class TheKeyDependsOnTheChoice(unittest.TestCase):
    def test_the_simple_mean_gives_another_answer(self):
        r = rows()
        for ent, total in BILL.items():
            lw, sm = r[(ent, "rt_load_weighted", "2026-09")], r[(ent, "rt_simple_mean", "2026-09")]
            self.assertEqual(r[(ent, "rt_hours", "2026-09")], r[(ent, "hours_in_month", "2026-09")], ent)
            a, b = round(600 * lw / 1000, 2), round(600 * sm / 1000, 2)
            self.assertNotEqual(a, b, ent)
            self.assertNotEqual(round(a / total * 100, 2), round(b / total * 100, 2), ent)
        self.assertEqual(round(600 * r[("caiso:TH_NP15_GEN-APND", "rt_load_weighted", "2026-09")] / 1000, 2), 26.91)
        self.assertEqual(round(600 * r[("caiso:TH_NP15_GEN-APND", "rt_simple_mean", "2026-09")] / 1000, 2), 26.55)


class TheQuestionNamesIt(unittest.TestCase):
    def setUp(self):
        with open(SRC, encoding="utf-8") as f:
            self.src = f.read()
        m = re.search(r"const billQ = .*?\n  \}\);", self.src, re.S)
        self.assertIsNotNone(m)
        self.q = re.search(r"q: `([^`]*)`", m.group(0)).group(1)

    def test_the_words(self):
        for words in ("taxes and local fees are not on it", "Value the kWh on the meter, with no losses added",
                      "the load-weighted real-time price of the ${x.hub}", "the latest complete month"):
            self.assertIn(words, self.q)
        self.assertIn("hub: hubName(ent)", self.src)

    def test_the_kept_figures_carry_the_words(self):
        with open(KEPT, encoding="utf-8") as f:
            kept = json.load(f)
        qs = {q["id"]: q["q"] for q in kept["sets"]["prices-and-your-bill"]["questions"]}
        self.assertTrue(qs["b3"].endswith("at the load-weighted real-time price of the CAISO NP15 in the latest complete month, 2026-09."))
        self.assertTrue(qs["b4"].endswith("at the load-weighted real-time price of the ERCOT hub average in the latest complete month, 2026-09."))
        for q in (qs["b3"], qs["b4"]):
            self.assertNotIn(chr(0x2014), q)


if __name__ == "__main__":
    unittest.main()
