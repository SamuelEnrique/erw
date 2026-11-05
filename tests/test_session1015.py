"""Session 1015 (chain 070): the packages on 390 pixels. Each install line and call of /data's three panels has a
control that copies it (components/CopyLine.tsx: a button that names what it copies to a screen reader), and each line
scrolls inside its own frame. AccessLint, the 390 check and the link check ran on a build (the session's report). No
request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Copy(unittest.TestCase):
    def test_each_line_has_its_control(self):
        page = src("site", "app", "data", "page.tsx")
        self.assertIn("{p.install.map((ln) => <CopyLine key={ln} line={ln} />)}", page)
        self.assertIn("{p.calls.map((ln) => <CopyLine key={ln} line={ln} />)}", page)

    def test_the_control_says_what_it_copies(self):
        c = src("site", "components", "CopyLine.tsx")
        self.assertTrue(c.startswith('"use client";'))
        self.assertIn('type="button"', c)
        self.assertIn("aria-label={`Copy: ${line}`}", c)
        self.assertIn("navigator.clipboard?.writeText(line)", c)
        self.assertIn("overflow-x-auto whitespace-pre", c)
        self.assertNotIn(chr(0x2014), c)


if __name__ == "__main__":
    unittest.main()
