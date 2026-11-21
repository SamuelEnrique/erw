"""Session 9601 (chain 620, 20 November 2026): after the browser's back button a list reads what the page shows.

Energy Research Warehouse (ERW). The browser read of the week's pages found it on every page with a list that submits
itself (`site/components/AutoSubmit.tsx`): two choices, one step back, and the address and the page went back while the
list kept the later choice (`/queues/places`: the table PacifiCorp, the list "Queue B" Duke). A browser puts a form's
last state back when a page of its history is shown again, and the list took its value from the page only once.

What is held here, on the source alone (the proof in a browser is `site/scripts/check-back-button.mjs <base>`, which
fails on a build without the mend and passes on one with it):
- the list still takes its first value from the page and still submits its form on a change, and works with no script;
- when the page is shown it is set to the value the page was drawn with, and the listener is taken off again;
- the label, the name and the options are as they were (an older test pins the label's markup);
- the browser check names the pages it reads and compares each list with a fresh load of the same address.
Nothing here sets the environment, reads a table or makes a request.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheList(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "components", "AutoSubmit.tsx")

    def test_it_still_opens_on_the_pages_value_and_submits_on_a_change(self):
        self.assertIn("defaultValue={value}", self.s)
        self.assertIn("onChange={(e) => e.currentTarget.form?.requestSubmit()}", self.s)
        self.assertNotIn(" value={value}\n", self.s, "the list is not made a controlled one: it must work before the script runs")

    def test_it_is_set_to_the_pages_value_when_the_page_is_shown(self):
        self.assertIn('window.addEventListener("pageshow", put)', self.s)
        self.assertIn('window.removeEventListener("pageshow", put)', self.s)
        put = re.search(r"const put = \(\) => \{([^}]*)\}", self.s)
        self.assertIsNotNone(put)
        self.assertIn("s.value !== value", put.group(1))
        self.assertIn("s.value = value", put.group(1))
        self.assertRegex(self.s, r"useEffect\(\(\) => \{\s*const put[\s\S]*?put\(\);[\s\S]*?\}, \[value\]\);", "set once when drawn, again each time the page is shown")
        self.assertIn("ref={ref}", self.s)

    def test_the_label_the_name_and_the_options_are_as_they_were(self):
        self.assertIn("<label className=\"flex flex-col text-xs text-muted\">\n      {label}\n      <select", self.s)
        self.assertIn("name={name}", self.s)
        self.assertIn("<option key={o.value} value={o.value}>", self.s)
        self.assertIn('className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink"', self.s)
        self.assertTrue(self.s.startswith('"use client";'))


class TheBrowserCheck(unittest.TestCase):
    def setUp(self):
        self.c = src("site", "scripts", "check-back-button.mjs")

    def test_it_reads_four_pages_with_two_choices_each(self):
        for page in ("/queues/places", "/storage/places", "/curtailment/where-when", "/ai-energy"):
            self.assertIn(f'["{page}", [', self.c)
        self.assertIn("history.back()", self.c)
        self.assertIn("history.forward()", self.c)

    def test_a_list_is_compared_with_a_fresh_load_of_the_same_address(self):
        self.assertIn("const fresh = async (address)", self.c)
        self.assertIn("same(backLists, wantBack)", self.c)

    def test_the_pages_that_draw_the_list_still_do(self):
        users = []
        for folder, _, files in os.walk(os.path.join(ROOT, "site", "app")):
            for f in files:
                if f.endswith(".tsx") and "AutoSubmitSelect" in src(folder, f):
                    users.append(os.path.relpath(os.path.join(folder, f), ROOT).replace(os.sep, "/"))
        for page in ("site/app/queues/places/page.tsx", "site/app/storage/places/page.tsx", "site/app/curtailment/where-when/page.tsx", "site/app/ai-energy/page.tsx"):
            self.assertIn(page, users)


class NoDash(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "components", "AutoSubmit.tsx"), ("site", "scripts", "check-back-button.mjs"), ("tests", "test_session9601_back_button.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
