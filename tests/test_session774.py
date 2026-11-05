"""Session 774 (chain 064): the All grids tab's check keys, proved whole. Every kind of key the tab's files draw
(allgrids|<kind>|...) has its branch in sitingStat (site/lib/siting.ts), which check-values uses to recompute each figure
from the tab's own functions; a kind drawn and not answered would be a figure no check reads. No request, no model call."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILES = [("site", "app", "cost-of-power", "AllGridsView.tsx"), ("site", "app", "cost-of-power", "AllGridsNodes.tsx")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def drawn():
    out = set()
    for p in FILES:
        s = src(*p)
        out |= set(re.findall(r"allgrids\|([a-z0-9]+)\|", s)) | set(re.findall(r'"allgrids\|([a-z0-9]+)"', s))
    return out


def answered():
    lib = src("site", "lib", "siting.ts")
    stat = lib[lib.index("export function sitingStat"):]
    return set(re.findall(r'p\[1\] === "([a-z0-9]+)"', stat))


class Keys(unittest.TestCase):
    def test_every_kind_drawn_is_answered(self):
        d, a = drawn(), answered()
        self.assertGreaterEqual(len(d), 25)
        self.assertEqual(sorted(d - a), [], "a key kind the tab draws that sitingStat does not answer")

    def test_check_values_reads_the_tab_through_sitingStat(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn("S.sitingStat(F.files(), check, await F.dc())", c)


if __name__ == "__main__":
    unittest.main()
