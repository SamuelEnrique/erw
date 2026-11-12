"""Session 3751 (chain 211): main green again, and the data machine's commit path guarded.

docs/state/main_red_2026-11-11.md: from 7 November 2026 the data machine's page files made the suite red (board.json named
held tables in its rows' notes; the seller's capture file moved a month ahead of the hub models), while the daily run and
the weekly vacuum were refused at their push guard. Held here, with no request and no table:

- the data machine's commit runs scripts/push_guard.py before its push to main, sends a red commit to wip/red-dm-<day>
  and returns the checkout to origin/main (chain 208's three lines);
- scripts/page_tables.py does not count a table named only in the note of a row that draws no figure, and still counts
  one named in a sources line or in an ok row.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import page_tables  # noqa: E402


class TheDataMachinesCommit(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            self.src = f.read()

    def test_the_guard_runs_after_the_pull_and_before_the_push(self):
        guard = self.src.index('scripts/push_guard.py --who "data machine daily" --step "dm_commit" --red-branch "wip/red-dm-$day"')
        pull = self.src.index("git pull --rebase --quiet origin main")
        push = self.src.index("git push --quiet origin main")
        self.assertLess(pull, guard)
        self.assertLess(guard, push)

    def test_a_refused_commit_leaves_main_and_this_checkout_follows_origin(self):
        block = self.src[self.src.index('if ! "$PYTHON" scripts/push_guard.py'):self.src.index("git push --quiet origin main")]
        self.assertIn("git reset --quiet --keep origin/main", block)
        self.assertIn("exit 0", block)
        self.assertNotIn("git push", block)


class TheHoldNotes(unittest.TestCase):
    TABLES = ["isone_as_prices", "iso_rtm_hub_prices", "eia_fuel_spot_prices", "caiso_as_prices"]

    def read(self, d):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "board.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f)
            return page_tables.json_tables(path, self.TABLES, "/board")

    def test_a_held_rows_note_is_not_a_read(self):
        d = {"sources": ["ERCOT, the hub's real-time price (iso_rtm_hub_prices)"],
             "rows": [{"id": "a", "status": "licensed", "note": "held internal (isone_as_prices) while the terms are reviewed"},
                      {"id": "b", "status": "paused", "note": "paused (caiso_as_prices)"},
                      {"id": "c", "status": "ok", "note": "from eia_fuel_spot_prices"}]}
        self.assertEqual(self.read(d), {"iso_rtm_hub_prices", "eia_fuel_spot_prices"})

    def test_a_file_without_rows_is_read_whole(self):
        self.assertEqual(self.read({"note": "isone_as_prices"}), {"isone_as_prices"})


if __name__ == "__main__":
    unittest.main()
