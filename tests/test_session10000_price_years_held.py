"""Session 10000 (chain 701): scripts/price_years_rebuild.py takes the loader's exit 75 ("held", load.py GATE_SKIP) to the
read back instead of stopping. On 27 November 2026 the table loaded (63 rows written) and the loader ended held on the
stale source of the IEA; the script stopped before its read back. Steps stubbed as in tests/test_session5504.py."""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
spec = importlib.util.spec_from_file_location("t5504", os.path.join(ROOT, "tests", "test_session5504.py"))
t5504 = importlib.util.module_from_spec(spec)
sys.modules["t5504"] = t5504
spec.loader.exec_module(t5504)
row = t5504.row


class AHeldLoad(unittest.TestCase):
    # the stubs of tests/test_session5504.py's Apply, without running its own tests a second time
    setUp = t5504.Apply.setUp
    fake_run = t5504.Apply.fake_run
    patched = t5504.Apply.patched
    go = t5504.Apply.go

    def test_a_held_load_that_reads_back_is_proven(self):
        k = ("ercot:HB_HUBAVG", "battery_foresight_4h_last_12")
        built = {k: row(*k, "2025-11-01T00:00:00Z", 80.401613)}
        future = {k: row(*k, "2025-11-01T00:00:00Z", 80.401613, retrieved="2999-01-01T00:00:00Z")}
        self.codes["the load"] = 75
        self.assertEqual(self.go(rows=future, built=built), 0)
        self.assertEqual(self.calls, ["the freeze", "the data lock", "the build", "the validator", "the coverage row", "the load", "the lock released"])

    def test_a_held_load_that_does_not_read_back_is_not_proven(self):
        k = ("ercot:HB_HUBAVG", "battery_foresight_4h_last_12")
        built = {k: row(*k, "2025-11-01T00:00:00Z", 80.401613)}
        old = {k: row(*k, "2025-11-01T00:00:00Z", 80.34, retrieved="2026-11-14T09:16:00Z")}
        self.codes["the load"] = 75
        self.assertEqual(self.go(rows=old, built=built), 1)

    def test_another_failure_of_the_load_still_stops(self):
        self.codes["the load"] = 1
        self.assertEqual(self.go(), 1)

    def test_only_the_load_may_be_held(self):
        self.codes["the validator"] = 75
        self.assertEqual(self.go(), 1)
        self.assertEqual(self.calls[-1], "the lock released")
        self.assertNotIn("the load", self.calls)


if __name__ == "__main__":
    unittest.main()
