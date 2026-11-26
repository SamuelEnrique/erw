"""Session 11000 (chain 750, the browser read of 26 November 2026): two things a reader met on /companies.

1. Five of its six fields had no name for a screen reader. Each stands in a <label> with an "i" mark before it, and a
   <label> names the first field inside it: the mark's own button ("About The search"). Of the 392 fields of the 82
   pages with a fixed address, read in a browser, these five were the only ones with no name. Each now carries
   aria-label.
2. After a choice, Show and the browser's back button, the page listed every company while the list still read the
   choice (Kind: OEM, State: CA; 4 of 4 tries at 1280 and 390 px). A browser puts a form's last state back when a page
   of its history is shown again, and these fields take their value from the page once. The form says
   autocomplete="off": the browser keeps no state for it (tried on production's own page: 4 of 4 read the page's value).

Energy Research Warehouse (ERW). No network, no build: the page's source is read.

    python -m unittest tests.test_session11000_companies_fields -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src():
    with open(os.path.join(ROOT, "site", "app", "companies", "page.tsx"), encoding="utf-8") as f:
        return f.read()


def labels(text):
    """Each <label>...</label> of the source, as text."""
    return re.findall(r"<label\b.*?</label>", text, re.S)


class TheFieldsHaveNames(unittest.TestCase):
    def test_a_field_after_a_tip_in_its_label_names_itself(self):
        found = 0
        for lab in labels(src()):
            field = re.search(r"<(select|input|textarea)\b[^>]*>", lab, re.S)
            if not field:
                continue
            before = lab[:field.start()]
            if "{tip}" in before or "<Tip " in before:
                found += 1
                self.assertIn("aria-label=", field.group(0), "a field that stands after a tip inside its label needs its own name: " + field.group(0)[:120])
        self.assertGreaterEqual(found, 2, "the page's labels no longer hold a tip before their field: read this test again")

    def test_the_two_forms_of_field(self):
        t = src()
        self.assertIn('<select name={name} defaultValue={value} aria-label={label} ', t)
        self.assertIn('<input type="search" name="q" defaultValue={q.q} maxLength={80} aria-label="Name" ', t)


class TheBackButton(unittest.TestCase):
    def test_the_form_keeps_no_state(self):
        t = src()
        self.assertIn('<form method="get" action="/companies" autoComplete="off">', t)
        self.assertNotIn('<form method="get" action="/companies">', t)


if __name__ == "__main__":
    unittest.main()
