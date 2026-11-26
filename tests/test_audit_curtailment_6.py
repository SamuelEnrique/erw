"""Session 10210 (curtailment audit, finding 6): "Pacific time" on California's hour of the day is clock time.

/curtailment draws California's curtailment by hour of the day in Pacific clock time (CAISO's record, daylight saving from
March to November) under the words "Pacific time", and on the same page "Where free energy is" counts the hubs' hours in
Pacific standard time. From March to November the two clocks are an hour apart. Measured on the page's own profile file:
2026's hour with the most is 15:00 on the clock and 14:00 on standard time; the MWh-weighted centre of the day moves from
12.95 to 12.05 (docs/reviews/curtailment-model-audit-2026-11-26/measures.json, "6_clock").

Words only (site/app/curtailment/page.tsx, CLOCK_WORDS): no figure moves.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ClockWords(unittest.TestCase):
    def test_the_two_clocks(self):
        f = json.loads(read("site", "data", "curtailment", "free_energy.json"))
        self.assertEqual(f["grids"]["caiso"]["std_name"], "US Pacific standard time")
        w = json.loads(read("site", "data", "curtailment", "where_when.json"))
        caiso = next(c for c in w["curtailment"] if c["id"] == "caiso")
        self.assertIn("Pacific clock time", caiso["time"])

    def test_the_peak_hour_moves_on_standard_time(self):
        prof = json.loads(read("site", "data", "curtailment_profile.json"))
        ms = [m for m in prof["months"] if m.startswith("2026")]
        clock = [sum(prof["months"][m].get(f"curtailed_solar_mwh_h{h:02d}", 0) + prof["months"][m].get(f"curtailed_wind_mwh_h{h:02d}", 0) for m in ms) for h in range(24)]
        dst = {"03": 24 / 31, "04": 1, "05": 1, "06": 1, "07": 1, "08": 1, "09": 1, "10": 1}
        std = [0.0] * 24
        for m in ms:
            r, frac = prof["months"][m], dst.get(m[5:], 0.0)
            for h in range(24):
                v = r.get(f"curtailed_solar_mwh_h{h:02d}", 0) + r.get(f"curtailed_wind_mwh_h{h:02d}", 0)
                std[(h - 1) % 24] += frac * v
                std[h] += (1 - frac) * v
        self.assertEqual(clock.index(max(clock)), 15)
        self.assertEqual(std.index(max(std)), 14)

    def test_the_page_says_clock_time(self):
        p = read("site", "app", "curtailment", "page.tsx")
        self.assertIn("const CLOCK_WORDS = \"Pacific clock time, with daylight saving time from March to November", p)
        self.assertIn("note={CLOCK_WORDS}>", p)
        self.assertNotIn('note="Pacific time', p)
        self.assertNotIn(chr(0x2014), p)


if __name__ == "__main__":
    unittest.main()
