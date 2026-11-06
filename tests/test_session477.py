"""Session 477: the database gate inside the loader. Before its first write load.py asks scripts/db_probe.py's probe;
closed, it loads nothing and exits 75, a skip under warehouse/health.py. After a table that wrote 100,000 rows or more
it pauses before the next."""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402


class Gate(unittest.TestCase):
    def test_open_is_none(self):
        self.assertIsNone(load.gate(probe=lambda url: (0, 0.45, "1000 rows of iso_dam_hub_prices"), url="u"))

    def test_closed_says_why(self):
        why = load.gate(probe=lambda url: (1, 5.01, "QueryCanceled: canceling statement due to statement timeout"), url="u")
        self.assertEqual(why, "5.01 s, QueryCanceled: canceling statement due to statement timeout")

    def test_no_url_goes_on_as_before(self):
        asked = []
        with mock.patch.object(load, "db_url", return_value=None):
            self.assertIsNone(load.gate(probe=lambda url: asked.append(url) or (1, 0.0, "")))
        self.assertEqual(asked, [])

    def test_the_skip_is_healths(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import health
        self.assertEqual(load.GATE_SKIP, health.SKIP)

    def test_the_real_probe_is_the_scripts(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import db_probe
        self.assertEqual(db_probe.PASS_S, 3.0)


class Pause(unittest.TestCase):
    def test_a_large_write_pauses(self):
        slept = []
        self.assertEqual(load.pause_after(957_969, sleep=slept.append), load.PAUSE_S)
        self.assertEqual(slept, [load.PAUSE_S])

    def test_a_small_write_does_not(self):
        slept = []
        self.assertEqual(load.pause_after(474, sleep=slept.append), 0)
        self.assertEqual(slept, [])


if __name__ == "__main__":
    unittest.main()
