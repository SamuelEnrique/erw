"""Session 9817 (chain 610, part D): every list and field of the severance tax calculator (/severance) has a name a
screen reader can say. The credit's tier list had none: it sat under its option's checkbox with no label of its own.

Energy Research Warehouse (ERW). No network, no build: the source is read.

    python -m unittest tests.test_session9817 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCalculatorsControls(unittest.TestCase):
    def test_the_tier_list_is_named(self):
        t = src("site", "app", "severance", "Calculator.tsx")
        tier = [line for line in t.splitlines() if "<select value={tier[o.id]" in line]
        self.assertEqual(len(tier), 1)
        self.assertIn("aria-label={`Credit tier, ${o.name}`}", tier[0])

    def test_every_list_and_field_has_a_name(self):
        # a control is named by its own aria-label, by a <label htmlFor> of its id, or by the <label> it sits in
        t = src("site", "app", "severance", "Calculator.tsx")
        labelled = set(re.findall(r'htmlFor="([^"]+)"', t))
        for m in re.finditer(r"<(select|input)\b", t):
            line = t[m.start():t.find("\n", m.start())]
            if 'type="hidden"' in line or "aria-label=" in line:
                continue
            ident = re.search(r'\bid="([^"]+)"', line)
            if ident and ident.group(1) in labelled:
                continue
            before = t[max(0, m.start() - 600):m.start()]
            self.assertGreater(before.rfind("<label"), before.rfind("</label>"), f"a control with no name: {line[:120]}")


if __name__ == "__main__":
    unittest.main()
