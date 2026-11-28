"""A ready branch for Samuel's ruling (session 11407, chain 770 part C), from the play audit's finding 8 (session 10227,
docs/reviews/play-model-audit-2026-11-26.md, which made no branch for it: "to be confirmed by a person"): the battery
game said ERCOT's USD 5,000/MWh offer cap applied "since 2023", while the warehouse's own prices show it in 2022.

Measured in session 11407 from ercot_all_hub_prices_history (the main copy's, read only; runs/c770/11407/cap_years.py),
the highest HB_HUBAVG real-time interval of each year: 9,005.29 in 2019, 9,051.55 in 2021 (76 intervals above 9,000),
then 5,101.55 in 2022, 5,075.46 in 2023 and 4,981.33 in 2024, none above 9,000 from 2022 on. The page, the library's
comment and the method note now say "since 2022". Words only: the cap the game plays (EMERGENCY.cap) stays 5,000, and
no score moves. The Commission's own rule date was not read (no web read).

No table, no request, no model call; the environment is read, never set."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# the highest HB_HUBAVG real-time interval of each year, USD/MWh (session 11407, cap_years.out; the audit's summary.out agrees)
HIGHEST = {"2019": 9005.29, "2020": 2218.42, "2021": 9051.55, "2022": 5101.55, "2023": 5075.46, "2024": 4981.33}


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheCapsYear(unittest.TestCase):
    def test_the_prices_put_the_cap_in_2022(self):
        self.assertGreater(HIGHEST["2021"], 9000)                                       # the 9,000 cap, through 2021
        for y in ("2022", "2023", "2024"):
            self.assertLess(HIGHEST[y], 5000 * 1.03)                                     # at the 5,000 cap, adders aside
        self.assertGreater(HIGHEST["2022"], 5000)                                       # 2022 already reached it

    def test_the_words_say_2022(self):
        page = " ".join(read("site", "app", "play", "battery", "page.tsx").split())
        self.assertIn("ERCOT&apos;s offer cap since 2022, used for every grid", page)
        self.assertNotIn("offer cap since 2023", page)
        lib = read("site", "lib", "battery.ts")
        self.assertIn("ERCOT's system-wide offer cap since 2022 (USD 5,000/MWh", lib)
        note = read("docs", "methods", "battery_game.md")
        self.assertIn("USD 5,000/MWh is ERCOT's offer cap since 2022 (session 11407", note)
        self.assertNotIn("offer cap since 2023;", note)

    def test_the_cap_played_is_unchanged(self):
        lib = read("site", "lib", "battery.ts")
        self.assertIn("export const EMERGENCY = { cap: 5000, ramp: [0.25, 0.5, 0.75, 0.9], outageIntervals: 8, houseKw: 1.5 };", lib)

    def test_no_em_dash(self):
        for p in (("tests", "test_ready_play_cap_year.py"), ("site", "lib", "battery.ts"), ("docs", "methods", "battery_game.md"),
                  ("site", "app", "play", "battery", "page.tsx")):
            self.assertNotIn(chr(0x2014), read(*p))


if __name__ == "__main__":
    unittest.main()
