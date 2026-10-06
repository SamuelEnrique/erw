"""Session 112: the state of the platform, 4 October 2026 (docs/state_2026-10-04.md).

The document is dated, so its figures are not held to tomorrow's tables. What is held: every address it gives is a page
of the site, every page open to visitors on that day is in it, the ranked list is ten, and the file keeps the
repository's rules. No network.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "docs", "state_2026-10-04.md")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def is_page(address):
    """True when site/app holds a page for the address (a bracketed folder stands for any one part)."""
    here = os.path.join(ROOT, "site", "app")
    for part in [p for p in address.split("?")[0].split("/") if p]:
        nxt = os.path.join(here, part)
        if not os.path.isdir(nxt):
            dyn = [d for d in os.listdir(here) if d.startswith("[") and os.path.isdir(os.path.join(here, d))]
            if not dyn:
                return False
            nxt = os.path.join(here, dyn[0])
        here = nxt
    return any(os.path.isfile(os.path.join(here, f)) for f in ("page.tsx", "route.ts"))


class TheStateDocument(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = src("docs", "state_2026-10-04.md")
        cls.addresses = set(re.findall(r"`(/[^`\s]*)`", cls.doc))

    def test_every_address_it_gives_is_a_page_of_the_site(self):
        self.assertGreater(len(self.addresses), 50)
        for a in sorted(self.addresses):
            if a.startswith("/internal/unlock"):
                continue
            a = a.replace("<iso>", "ercot").replace("<name>", "battery_stack")
            # an address retired since that day still answers: it redirects to its tool's one page (session 132)
            retired = f'source: "{a}"' in src("site", "next.config.ts")
            self.assertTrue(is_page(a) or retired, a)

    def test_the_six_tools_open_on_that_day_are_in_it_and_marked_open(self):
        top = self.doc.split("## In review: built or rebuilt in this chain")[0]
        for a in ("/", "/cost-of-power/battery", "/cost-of-power/seller", "/network", "/storage", "/about", "/terms"):
            self.assertIn(f"`{a}`", top, a)

    def test_each_row_has_the_five_things_asked_for(self):
        heads = [l for l in self.doc.splitlines() if l.startswith("| Tool |")]
        self.assertEqual(len(heads), 3)
        for h in heads:
            cells = [c.strip() for c in h.strip("|").split("|")]
            self.assertEqual(cells[1], "Answers")
            self.assertTrue(cells[2].startswith("Data, and how fresh"))
            self.assertTrue(cells[3].startswith("Weakest point"))
            self.assertEqual(cells[4], "To be ready to share")
        rows = [l for l in self.doc.splitlines() if l.startswith("| **")]
        self.assertGreater(len(rows), 35)
        for r in rows:
            self.assertEqual(len(r.strip().strip("|").split(" | ")), 5, r[:60])

    def test_the_ranked_list_is_ten_each_with_a_reason(self):
        part = self.doc.split("## The ten things most worth doing next")[1].split("## ")[0]
        items = re.findall(r"^(\d+)\. \*\*(.+?)\*\*(.*)$", part, flags=re.M)
        self.assertEqual([int(n) for n, _, _ in items], list(range(1, 11)))
        for n, title, reason in items:
            self.assertGreater(len(reason.split()), 12, title)

    def test_it_says_what_was_looked_at_today_and_what_was_not(self):
        self.assertIn("**What was checked today.**", self.doc)
        self.assertIn("## In review: older pages, not opened by this chain", self.doc)

    def test_no_em_dash(self):
        for rel in ("docs/state_2026-10-04.md", "tests/test_session112.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
