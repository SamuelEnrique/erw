"""Session 757 (chain 063): the trader's path walked again. One fault found: the node list's sort line lowercased the whole
heading, so "Basis to HB_HUBAVG" read "basis to hb_hubavg"; only the first letter is lowered now. No request, no model
call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class SortLine(unittest.TestCase):
    def test_only_the_first_letter_is_lowered(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "AllGridsNodes.tsx"), encoding="utf-8") as f:
            n = f.read()
        self.assertNotIn("HEADS[by].toLowerCase()", n)
        self.assertIn("HEADS[by].charAt(0).toLowerCase() + HEADS[by].slice(1)", n)


if __name__ == "__main__":
    unittest.main()
