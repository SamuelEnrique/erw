"""Session 10212 (storage audit, finding 3): ISO-NE's and SPP's battery series carry no charging, and /storage read them as net.

The page's first decision says battery output is "negative while they charge", the "Discharged MWh" hover says the count
is "the fleet's net output, so a battery charging while another discharges cancels within the hour", and both charts read
"above zero ... discharging, below zero charging". EIA-930's BAT series for ISO-NE and SPP never go below zero, and
ERCOT's did not before 15 December 2025 (docs/methods/eia930_all_storage.md, "Charging is not in every series").
Measured on the year to 4 November 2026 (docs/reviews/storage-model-audit-2026-11-26/measures.json, "sign_by_series"):
ISO-NE 0 negative hours of 8,832 and above zero in 8,795; SPP 0 of 6,528, zero in 2,949; ERCOT's first hour below zero
2025-12-15 06:00 UTC, so its November 2025 shows 542,549 MWh discharged and 0 charged. The daily cycle's charged MWh for
ISO-NE and SPP is 0 on every day.

Words only (site/lib/decisions.ts and docs/methods/storage.md decision 1, word for word; site/lib/storagefleet.ts
DISCHARGED_TITLE; site/app/storage/page.tsx NO_CHARGE_WORDS): no figure moves.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORDS = ("ISO-NE's and SPP's series never go below zero, nor did ERCOT's before 15 December 2025: for them charging is not "
         "in the series, and a zero hour is not an idle battery.")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NoCharging(unittest.TestCase):
    def test_the_table_note_records_it(self):
        n = read("docs", "methods", "eia930_all_storage.md")
        self.assertIn("ISNE's and SWPP's values are never negative.", n)
        self.assertIn("ERCO's are never negative before 2025-12-15T06:00Z", n)

    def test_the_decision_says_it_in_both_places(self):
        self.assertIn(WORDS, read("site", "lib", "decisions.ts"))
        self.assertIn("negative while they charge, so a day's charging is the part below zero taken as a positive amount. " + WORDS + " **Default:**",
                      read("docs", "methods", "storage.md"))

    def test_the_hover_and_the_charts_say_it(self):
        f = read("site", "lib", "storagefleet.ts")
        self.assertIn("where the grid reports charging: ISO-NE and SPP report none (their series never go below zero)", f)
        self.assertIn("net output", f)
        p = read("site", "app", "storage", "page.tsx")
        self.assertIn('const NO_CHARGE_WORDS = " ISO-NE\'s and SPP\'s lines never go below zero: they report no charging to EIA-930', p)
        self.assertEqual(p.count("{NO_CHARGE_WORDS}"), 2)
        for s in (f, p, read("site", "lib", "decisions.ts")):
            self.assertNotIn(chr(0x2014), s)


if __name__ == "__main__":
    unittest.main()
