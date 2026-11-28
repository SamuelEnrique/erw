"""Ready for the owner's ruling (session 11407, chain 770 part C): the contracts page reads each quarter of execution
from the file filed for it, where the history table holds that file.

The audit (session 10226, docs/reviews/contracts-model-audit-2026-11-26.md, finding 1, test branch wip/audit-contracts-1)
found every quarter of /contracts read from the newest quarter's file (2026 Q2), so an earlier quarter listed only the
contracts still in effect in 2026 Q2. The other choice, made here: warehouse/supabase/load.py's own_quarter, named by
live_set.yaml (own_quarter_from: ferc_eqr_contracts_history), replaces the rows of 2025 Q3, 2025 Q4 and 2026 Q1 by
their own files' rows signed in them.

1. The rule on a small made-up pair of files (no real figure): a held quarter is replaced, the newest and an earlier
   quarter are kept, the window applies, a missing history fails.
2. Measured from the two tables (skipped where they are not on the machine, or are another retrieval), for the load of
   5 October 2026: energy, capacity and tolling rows 2025 Q3 273 to 2,129, 2025 Q4 311 to 2,209, 2026 Q1 396 to 701;
   2026 Q2 227 unchanged; rows held 18,989 to 22,087.
3. The page's lead and hover and the note say it.
Counts only: no party's name, figure or row (the tables are internal)."""
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402

POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}
RETRIEVED = {"ferc_eqr_contracts": "20261004T035009Z", "ferc_eqr_contracts_history": "20261005T165835Z"}
COLS = ["event_id", "event_date", "x_product_name", "x_quarter"]


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


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def power_by_quarter(df):
    q = load.execution_quarter(df["event_date"])
    p = df["x_product_name"].str.strip().str.upper().isin(POWER)
    return q[p].value_counts().to_dict()


class TheRule(unittest.TestCase):
    def test_a_held_quarter_is_read_from_its_own_file(self):
        newest = pd.DataFrame([
            ["n1", "2024-02-01", "ENERGY", "2026_Q2"],   # before the history's quarters: kept
            ["n2", "2025-08-01", "ENERGY", "2026_Q2"],   # 2025 Q3, held in the history: replaced
            ["n3", "2026-05-01", "ENERGY", "2026_Q2"],   # the newest quarter: kept
            ["n4", "2027-01-01", "ENERGY", "2026_Q2"],   # dated after the quarter filed for: kept
        ], columns=COLS)
        history = pd.DataFrame([
            ["h1", "2025-07-02", "ENERGY", "2025_Q3"],
            ["h2", "2025-09-30", "CAPACITY", "2025_Q3"],
            ["h3", "2024-03-01", "ENERGY", "2025_Q3"],   # signed before its file's quarter: not its own quarter's row
            ["h4", "2025-08-01", "ENERGY", "2025_Q4"],   # 2025 Q3 filed again in 2025 Q4: not taken
            ["h5", "2025-11-01", "ENERGY", "2025_Q4"],
            ["h6", "2026-05-01", "ENERGY", "2026_Q2"],   # the newest quarter is the newest file's own
        ], columns=COLS)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "h.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("# a header comment\n")
                history.to_csv(f, index=False)
            out = load.own_quarter(newest, path, None, chunksize=2)
            self.assertEqual(sorted(out["event_id"]), ["h1", "h2", "h5", "n1", "n3", "n4"])
            self.assertEqual(list(out.columns), COLS)
            cut = load.own_quarter(newest, path, "2025-08-01", chunksize=2)
            self.assertEqual(sorted(cut["event_id"]), ["h2", "h5", "n1", "n3", "n4"])  # the window applies to the history too
            with self.assertRaises(RuntimeError):
                load.own_quarter(newest, os.path.join(d, "missing.csv"))

    def test_the_live_set_names_the_history(self):
        import yaml
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        self.assertEqual(live["select"]["ferc_eqr_contracts"], {"event_days": 1000, "own_quarter_from": "ferc_eqr_contracts_history"})
        self.assertIn('sel.get("own_quarter_from")', read("warehouse", "supabase", "load.py"))


class MeasuredFromTheTables(unittest.TestCase):
    def test_the_load_of_5_october(self):
        d = tables()
        if d is None:
            self.skipTest("ferc_eqr_contracts and its history are not on this machine")
        for t, r in RETRIEVED.items():
            if retrieved(os.path.join(d, t + ".csv")) != r:
                self.skipTest(f"{t} is another retrieval than the one measured ({r})")
        cut = "2024-01-09"  # 1,000 days before 5 October 2026
        path = os.path.join(d, "ferc_eqr_contracts.csv")
        with open(path, encoding="utf-8") as f:
            skip = sum(1 for line in f if line.startswith("#"))
        parts = [c[c["event_date"].str[:10] >= cut] for c in
                 pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False, na_values=[], chunksize=20000)]
        before = pd.concat(parts, ignore_index=True)
        after = load.own_quarter(before, os.path.join(d, "ferc_eqr_contracts_history.csv"), cut)
        self.assertEqual((len(before), len(after)), (18989, 22087))
        b, a = power_by_quarter(before), power_by_quarter(after)
        self.assertEqual((b["2025_Q3"], a["2025_Q3"]), (273, 2129))
        self.assertEqual((b["2025_Q4"], a["2025_Q4"]), (311, 2209))
        self.assertEqual((b["2026_Q1"], a["2026_Q1"]), (396, 701))
        self.assertEqual((b["2026_Q2"], a["2026_Q2"]), (227, 227))     # the default view does not move
        self.assertEqual((b["2025_Q2"], a["2025_Q2"]), (354, 354))     # a quarter whose file is not held stays
        self.assertEqual(sorted(set(after["x_quarter"])), ["2025_Q3", "2025_Q4", "2026_Q1", "2026_Q2"])
        self.assertLessEqual(int(load.execution_quarter(after["event_date"]).value_counts().max()), 5000)


class ThePageAndTheNote(unittest.TestCase):
    def test_the_words(self):
        page = read("site", "app", "contracts", "page.tsx")
        lead = page[page.index("<ToolHeader"):page.index("<Limits rows=")]
        self.assertIn("A quarter whose own filings are held is", lead)
        self.assertIn("read from them, as first filed", lead)
        self.assertNotIn("all read from the newest quarter", lead)
        tip = page[page.index('data-quarter-rows="1"'):page.index("</Tip>", page.index('data-quarter-rows="1"'))]
        self.assertIn("is read from its own filings: its contracts as first filed", tip)
        self.assertNotIn("Every quarter is read from the newest", tip)
        note = read("docs", "methods", "contracts.md")
        self.assertIn("**Each quarter from its own file**", note)
        self.assertIn("2025 Q3 273 to 2,129", note)


if __name__ == "__main__":
    unittest.main()
