"""Session 2226 (chain 152, Ask): an answer's dashes, in both loops.

The repository writes no em dash and no en dash in any file, and every stored run holds its answers word for word; both
loops normalised the em dash alone, and the site's answers of 6 November 2026 wrote "2015" and "2025" joined by an en
dash. Held here: the Python loop's nodash turns an em dash into " - " and an en dash into "-", and the site's nodash is
written the same way. (Named _ask: tests/test_session2226.py is chain 098's.) No network, no model.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402


class TheDashes(unittest.TestCase):
    def test_the_python_loop(self):
        self.assertEqual(ask.nodash("rose over 2015" + chr(0x2013) + "2025 " + chr(0x2014) + " a step up"), "rose over 2015-2025 - a step up")
        self.assertNotIn(chr(0x2013), ask.nodash("a" + chr(0x2013) + "b" + chr(0x2013) + "c"))
        self.assertEqual(ask.nodash("no dash here"), "no dash here")

    def test_the_site_loop_is_written_the_same_way(self):
        with open(os.path.join(ROOT, "site", "lib", "chat", "ask.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('.split(String.fromCharCode(0x2013)).join("-")', src)
        self.assertIn('.split(String.fromCharCode(0x2014)).join(" - ")', src)


if __name__ == "__main__":
    unittest.main()
