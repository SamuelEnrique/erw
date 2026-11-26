"""Audit of the project map, finding 4 (session 10216, docs/reviews/map-model-audit-2026-11-26.md): the transmission
layer draws every line of 230 kV and above alike. The connector asks PASDA for every line with VOLTAGE 230 or more,
with no condition on STATUS, and the web file keeps no status, no inferred flag and no date of HIFLD's: a line HIFLD
lists as under construction or of a status it does not state is drawn as a line in service, and the one date a reader
meets is the day the ERW read PASDA's copy. The tip did not say so. No figure moves.

1. Through the connector and the web file: no status filter, and no status or date in the file. Passes on main.
2. The fix on this branch, words only. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheLinesStatusAndDate(unittest.TestCase):
    def test_every_status_is_asked_for_and_none_is_kept(self):
        conn = src("warehouse", "connectors", "hifld_lines.py")
        self.assertIn('"where": "VOLTAGE>=230"', conn)
        self.assertNotRegex(conn, r'"where": "[^"]*STATUS', "no layer is asked for by status")
        layer = json.loads(src("site", "data", "map_layers", "transmission_230kv.json"))
        self.assertEqual(layer["fields"], ["id", "kv", "owner", "from", "to", "km"])
        self.assertTrue(all(r[layer["fields"].index("kv")] >= 230 for r in layer["rows"]))

    def test_the_words(self):
        page = src("site", "app", "map", "ProjectMap.tsx")
        self.assertIn("Every line HIFLD lists at 230 kV or more is drawn alike, whatever its status (in service, under construction, or a status "
                      "HIFLD does not state) and whether HIFLD inferred its voltage; the date in a line&apos;s hover is the day the ERW read "
                      "PASDA&apos;s copy, not the date of HIFLD&apos;s data, which the table keeps line by line.", page)
        note = src("docs", "methods", "map_layers.md")
        self.assertIn("What the drawing does not tell apart (session 10216", note)
        for text in (page, note):
            self.assertNotIn(chr(0x2014), text)


if __name__ == "__main__":
    unittest.main()
