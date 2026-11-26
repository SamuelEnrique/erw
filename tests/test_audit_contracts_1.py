"""Audit of the contracts page, finding 1 (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md): the quarters
listed are survivors, not signings.

Every quarter of /contracts is read from the newest quarter's file (ferc_eqr_contracts, filed for 2026 Q2), which holds
the contracts in effect in 2026 Q2. A contract signed in an earlier quarter that has since ended is not in it, and the
newest quarter lacks the contracts its filers report a quarter late. The page said "This lists the contracts by the
quarter they were signed" and nothing of either.

1. Measured from the two tables (skipped where they are not on the machine, or are another retrieval): of the energy,
   capacity and tolling rows 2025 Q3's own file holds as signed in 2025 Q3 (2,129), 2026 Q2's file holds 273; 46 of
   2,052 contracts kept; 159 contracts of 2026 Q1 first filed a quarter late, on 556. Passes on main.
2. The fix on this branch, words only: the lead, the hover on "Quarter signed" and the note say it. Fails on main.
   No figure moves. Reading each quarter from its own file is the owner's ruling (default: left as it is).
Counts only: no party's name, figure or row (the tables are internal)."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}
RETRIEVED = {"ferc_eqr_contracts": "20261004T035009Z", "ferc_eqr_contracts_history": "20261005T165835Z"}


def tables():
    """This checkout's tables, else the main checkout's beside it (replication/contracts/copy_rows.py does the same)."""
    for d in (os.path.join(ROOT, "warehouse", "output"), os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")):
        if all(os.path.exists(os.path.join(d, t + ".csv")) for t in RETRIEVED):
            return d
    return None


def retrieved(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return ""
            if line.startswith("# Retrieved: "):
                return line.split()[2]
    return ""


def rows(path):
    csv.field_size_limit(1 << 30)
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def qtr(day):
    return f"{day[:4]}_Q{(int(day[5:7]) - 1) // 3 + 1}"


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class QuartersAreSurvivors(unittest.TestCase):
    def test_measured_from_the_tables(self):
        d = tables()
        if d is None:
            self.skipTest("ferc_eqr_contracts and its history are not on this machine")
        for t, r in RETRIEVED.items():
            if retrieved(os.path.join(d, t + ".csv")) != r:
                self.skipTest(f"{t} is another retrieval than the one measured ({r})")
        n, keys = {}, {}
        for t in RETRIEVED:
            for r in rows(os.path.join(d, t + ".csv")):
                e = qtr(r["event_date"][:10])
                if e in ("2025_Q3", "2026_Q1") and r["x_product_name"].strip().upper() in POWER:
                    f = r["x_quarter"]
                    n[(f, e)] = n.get((f, e), 0) + 1
                    keys.setdefault((f, e), set()).add(f"{r['x_company_id']}|{r['x_contract_unique_id']}")
        self.assertEqual(n[("2025_Q3", "2025_Q3")], 2129)
        self.assertEqual(n[("2026_Q2", "2025_Q3")], 273)
        self.assertEqual(len(keys[("2025_Q3", "2025_Q3")]), 2052)
        self.assertEqual(len(keys[("2025_Q3", "2025_Q3")] & keys[("2026_Q2", "2025_Q3")]), 46)
        self.assertEqual(len(keys[("2026_Q1", "2026_Q1")]), 556)
        self.assertEqual(len(keys[("2026_Q2", "2026_Q1")] - keys[("2026_Q1", "2026_Q1")]), 159)

    def test_the_page_and_the_note_say_it(self):
        page = read("site", "app", "contracts", "page.tsx")
        lead = page[page.index("<ToolHeader"):page.index("</ToolHeader>") if "</ToolHeader>" in page else page.index("<Limits rows=")]
        self.assertIn("an earlier quarter shows only the contracts still in effect in the newest one, not every contract signed in it", lead)
        tip = page[page.index('data-quarter-rows="1"'):page.index("</Tip>", page.index('data-quarter-rows="1"'))]
        self.assertIn("The counts are not a series of signings", tip)
        self.assertIn("report a quarter late", tip)
        note = read("docs", "methods", "contracts.md")
        self.assertIn("**What an earlier quarter holds**", note)
        self.assertIn("+28.6 percent", note)


if __name__ == "__main__":
    unittest.main()
