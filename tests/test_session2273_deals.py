"""Session 2273 (chain 174): a facility's power source from the story's words, where the model gave none.

The second read (session 2249) found 2 of 60 sampled facilities with the power source missed: "Another Solar Company
Trying Gas-Powered Data Center on Federal Lands" (no answer) and "DataOne's unpermitted generator fleet" (the model's
"generators" was refused, not being the story's word). warehouse/datacenters/facility_fields.py (power_from_words)
reads, for a cluster of one facility, the words that say how the facility itself is powered; the kind follows from
them as for any power source. On the replayed answers: 2 to 0, nothing else changing on either fixture.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters", "eval"))
import facility_fields as ff  # noqa: E402
import dc_fixture  # noqa: E402


class TheWords(unittest.TestCase):
    def test_how_a_facility_is_powered(self):
        self.assertEqual(ff.power_from_words("Trying Gas-Powered Data Center on Federal Lands"), ("Gas-Powered", "gas"))
        self.assertEqual(ff.power_from_words("DataOne's unpermitted generator fleet"), ("generator fleet", "behind_the_meter_gas"))
        self.assertEqual(ff.power_from_words("a campus with on-site gas turbines")[1], "behind_the_meter_gas")
        self.assertEqual(ff.power_from_words("powered by small modular reactors")[1], "nuclear")

    def test_words_that_do_not_say(self):
        self.assertEqual(ff.power_from_words("Another Solar Company buys land"), ("", ""))   # a solar company is not the power
        self.assertEqual(ff.power_from_words("utility raises rates for data centers"), ("", ""))


class TheSample(unittest.TestCase):
    def test_power_missed_two_to_none(self):
        _, log = dc_fixture.replay("2249")
        fills = sorted(l.split("power_source ")[1].split(" (")[0] for l in log.splitlines() if "power_source" in l and "from the words" in l)
        self.assertEqual(fills, ["'Gas-Powered'", "'generator fleet'"])


if __name__ == "__main__":
    unittest.main()
