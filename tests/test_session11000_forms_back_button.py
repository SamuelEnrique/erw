"""Session 11000 (chain 750, the browser read of 26 November 2026): after the back button a form's fields read what
the page shows, on /prices/compare and /conditions.

A browser puts a form's last state back when a page of its history is shown again. A field that takes its value from
the page once (defaultValue) then reads the later choice over the earlier page. Session 9601 mended the lists that
submit themselves (components/AutoSubmit.tsx sets the list to the page's value on pageshow). Two forms that submit with
their button had fields outside that mend, read in a browser at 1280 and 390 px:

  /prices/compare  A or B chosen, Compare, back: the page showed no A, the list still read SP15 (4 of 4)
  /conditions      a day typed, Show, back: the page drew the newest 35 days, the Day box still read the day (4 of 4)

Each form now says autocomplete="off", so the browser keeps no state for it; tried on production's own pages before
this was written, 8 of 8 then read the page's value. (/companies has the same mend on its own branch.)

Energy Research Warehouse (ERW). No network, no build: the pages' source is read.

    python -m unittest tests.test_session11000_forms_back_button -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def get_forms(text):
    """Each GET form of a source file: (its opening tag, its body)."""
    out = []
    for m in re.finditer(r"<form\b[^>]*>", text):
        end = text.find("</form>", m.end())
        out.append((m.group(0), text[m.end():end if end > 0 else len(text)]))
    return out


class TheFormsKeepNoState(unittest.TestCase):
    def check(self, *parts, field):
        forms = [(tag, body) for tag, body in get_forms(read(*parts)) if field in body]
        self.assertEqual(len(forms), 1, f"{'/'.join(parts)}: one form holds {field}")
        tag, body = forms[0]
        self.assertIn('method="get"', tag)
        self.assertIn("defaultValue", body, "the field no longer takes its value from the page once: read this test again")
        self.assertIn('autoComplete="off"', tag, f"{'/'.join(parts)}: a form whose field takes its value once must keep no state, or the back button leaves the field on the later choice")

    def test_prices_compare(self):
        self.check("site", "app", "prices", "compare", "page.tsx", field="data-ab-pick")

    def test_conditions(self):
        self.check("site", "app", "conditions", "page.tsx", field='name="day"')

    def test_the_rule_bites(self):
        tag = '<form method="get" action="/prices/compare" className="mb-3">'
        self.assertNotIn('autoComplete="off"', tag)


if __name__ == "__main__":
    unittest.main()
