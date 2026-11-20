"""Session 9601 (chain 620, 20 November 2026): a transmission line's end that HIFLD does not name is said to be unnamed.

Energy Research Warehouse (ERW). The browser read of `/map` with the transmission lines on: a finger on a line at 390
px brought up "UNKNOWN201257 to UNKNOWN203126, HIGH PLAINS POWER INC, 230 kV". "UNKNOWN<number>" is the publisher's own
mark for an end it does not name; the hover printed it as a place. Of the layer's 10,692 lines, 881 have both ends so
marked and 2,861 one.

Held here, on the source and the committed layer file: an end so marked reads "an end HIFLD does not name" with the
mark kept beside it; a named end reads as it did; a line with no end in the file reads as it did; the file still
holds such marks (so the words are drawn). Nothing here sets the environment, reads a table or makes a request.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHover(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "lib", "maplayers.ts")

    def test_an_end_hifld_marks_unknown_is_said_to_be_unnamed_with_the_mark_kept(self):
        self.assertIn("const HIFLD_UNNAMED = /^UNKNOWN\\d+$/;", self.s)
        self.assertIn("return HIFLD_UNNAMED.test(s) ? `an end HIFLD does not name (its mark ${s})` : s;", self.s)
        self.assertIn('name: g("from") && g("to") ? `${lineEnd(g("from"))} to ${lineEnd(g("to"))}` : "No end named in the source",', self.s)

    def test_the_rest_of_the_hover_is_as_it_was(self):
        self.assertIn('operator: (g("owner") as string | null) ?? "Owner not stated",', self.s)
        self.assertIn('`${g("km")} km as drawn by HIFLD`', self.s)
        self.assertIn('name: (g("name") as string | null) ?? "No name in the source",', self.s)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.s)
        self.assertNotIn(EM, src("tests", "test_session9601_line_ends_unnamed.py"))


class TheFile(unittest.TestCase):
    def test_the_layer_file_holds_ends_so_marked_and_ends_with_names(self):
        j = json.loads(src("site", "data", "map_layers", "transmission_230kv.json"))
        names, fields = j["names"], j["fields"]
        fr, to = fields.index("from"), fields.index("to")
        mark = re.compile(r"^UNKNOWN\d+$")
        marked = named = 0
        for r in j["rows"]:
            for i in (r[fr], r[to]):
                if isinstance(i, int):
                    if mark.match(str(names[i])):
                        marked += 1
                    else:
                        named += 1
        self.assertGreater(marked, 1000)
        self.assertGreater(named, 1000)


if __name__ == "__main__":
    unittest.main()
