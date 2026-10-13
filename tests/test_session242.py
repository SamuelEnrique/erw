"""Session 242, the final pass of the chain of 12 to 13 October 2026: every page shot at 1280 and at 390 px wide,
and one table of what is still off the brand.

The owner's task: "Then screenshots of every page at 1280 and 390 to docs/brand/review-final/, and a table of any
remaining inconsistency, fixed where it is one file."

  TheFolder     docs/brand/review-final/ holds its README, the facts and a picture at both widths for each menu page
  TheTable      the README holds the table, one row a page shot, and the two lists
  TheFixes      the two pages this pass brought to the brand carry the wrapper, once
  NoEmDash      nothing this session wrote holds an em dash
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = chr(0x2014)
FOLDER = os.path.join(ROOT, "docs", "brand", "review-final")

# the menu's pages on the night of the pass (site/lib/pages.ts, the 35 entries of GROUPS): written out, so that a
# page added to the menu later does not ask this folder for a picture it never held
MENU = [
    "/board", "/prices", "/supply", "/contracts", "/severance", "/learn/bill", "/cost-of-power/battery",
    "/cost-of-power/seller", "/cost-of-power", "/battery/customer", "/shoulder", "/grid", "/demand", "/curtailment",
    "/map", "/datacenters", "/storage", "/deals", "/research", "/ask", "/events", "/policy", "/thesis",
    "/play/battery", "/tour", "/learn/problems/know-your-grid", "/learn/problems/prices-and-your-bill",
    "/learn/problems/when-the-grid-broke", "/learn/problems/networks-and-money", "/data", "/about", "/terms",
    "/digest", "/roundup", "/subscribe",
]


def slug(address):
    """The picture's name for an address, as runs/session242/final/shots.mjs writes it."""
    return re.sub(r"^-+|-+$", "", re.sub(r"[^A-Za-z0-9]+", "-", address.lstrip("/"))) or "home"


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def facts():
    rows = []
    for line in read("docs", "brand", "review-final", "facts.jsonl").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class TheFolder(unittest.TestCase):
    def test_the_readme_and_the_facts_are_there(self):
        for name in ("README.md", "facts.jsonl"):
            self.assertTrue(os.path.isfile(os.path.join(FOLDER, name)), name)

    def test_each_menu_page_has_a_picture_at_both_widths(self):
        missing = [f"{slug(a)}_{w}.png" for a in MENU for w in (1280, 390)
                   if not os.path.isfile(os.path.join(FOLDER, f"{slug(a)}_{w}.png"))]
        self.assertEqual(missing, [])

    def test_each_menu_page_has_a_line_of_facts(self):
        held = {r["address"] for r in facts()}
        self.assertEqual([a for a in MENU if a not in held], [])

    def test_every_picture_a_line_names_is_in_the_folder(self):
        missing = [p for r in facts() for p in r.get("pictures", []) if not os.path.isfile(os.path.join(FOLDER, p))]
        self.assertEqual(missing, [])

    def test_a_line_of_facts_holds_what_the_table_is_built_from(self):
        for r in facts():
            if "error" in r:
                continue
            for key in ("address", "final", "title", "brand", "height", "w1280", "w390", "exceptions", "off", "bodyBg"):
                self.assertIn(key, r, r["address"])
            self.assertIn("sideways", r["w390"], r["address"])

    def test_the_folder_is_under_twelve_megabytes(self):
        total = sum(os.path.getsize(os.path.join(FOLDER, f)) for f in os.listdir(FOLDER))
        self.assertLess(total, 12 * 1024 * 1024)

    def test_the_home_page_and_a_games_page_are_shot_all_the_same(self):
        for name in ("home_1280.png", "home_390.png", "tour_1280.png", "play-battery_390.png"):
            self.assertTrue(os.path.isfile(os.path.join(FOLDER, name)), name)


class TheTable(unittest.TestCase):
    def test_the_readme_holds_the_table_and_the_two_lists(self):
        text = read("docs", "brand", "review-final", "README.md")
        for words in ("## The table", "| Page | On the brand | Sideways at 390 | Exceptions | What remains |",
                      "## Fixed in this pass", "## Not fixed, with the one file it lives in", "outside by ruling"):
            self.assertIn(words, text)

    def test_one_row_a_page_shot(self):
        text = read("docs", "brand", "review-final", "README.md")
        rows = set(re.findall(r"^\| `([^`]+)` \|", text, flags=re.M))
        self.assertEqual(sorted(r["address"] for r in facts() if r["address"] not in rows), [])

    def test_the_readme_says_a_picture_is_capped(self):
        self.assertIn("6,000 px", read("docs", "brand", "review-final", "README.md"))


class TheFixes(unittest.TestCase):
    def test_the_two_pages_carry_the_wrapper_once(self):
        for parts in (("prices", "compare", "page.tsx"), ("prices", "[entity]", "page.tsx")):
            text = read("site", "app", *parts)
            self.assertIn('import { Brand } from "@/components/Brand";', text, parts)
            self.assertEqual(len(re.findall(r"<Brand[ >]", text)), 1, parts)
            self.assertEqual(text.count("</Brand>"), 1, parts)


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("docs", "brand", "review-final", "README.md"), ("docs", "brand", "review-final", "facts.jsonl"),
                      ("archive", "sessions", "SESSION_242_REPORT.md"), ("tests", "test_session242.py"),
                      ("site", "app", "prices", "compare", "page.tsx"), ("site", "app", "prices", "[entity]", "page.tsx")):
            self.assertNotIn(DASH, read(*parts), parts)


if __name__ == "__main__":
    unittest.main()
