"""Session 9001, chain 601 part H: two rows found reading /congestion on production as its reader.

H1: the page drew two lists of constraints (bound most, cost most) under one heading, the second with only a repeated
header row, so a reader could not tell which list was which. Each list now has a visible heading of its own.
H2: a place read "SPP SPP North hub": the page wrote the operator's name before a place name that already begins with
it. The page now writes the operator once.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "congestion", "page.tsx")
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")


def page():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


def place_label(op, name):
    """The page's rule (placeLabel in page.tsx), kept in step with it by the test below."""
    return f"{op} {name}" if op and not name.startswith(f"{op} ") else name


class EachListHasItsHeading(unittest.TestCase):
    def test_both_lists_have_a_visible_heading_before_their_table(self):
        s = page()
        hours = s.find('data-list-heading="hours"')
        cost = s.find('data-list-heading="cost"')
        by_hours = s.find("top.by_hours.map(rowOf)")
        by_cost = s.find("top.by_cost.map(rowOf)")
        self.assertTrue(min(hours, cost, by_hours, by_cost) > 0)
        self.assertTrue(hours < by_hours < cost < by_cost, "each heading comes just before its own list")
        self.assertIn("Cost most", s[cost:by_cost])
        self.assertIn("Bound most", s[hours:by_hours])


class TheOperatorIsNamedOnce(unittest.TestCase):
    def test_the_page_builds_every_place_label_through_one_rule(self):
        s = page()
        self.assertIn("const placeLabel = (op: string | undefined, name: string) => (op && !name.startsWith(`${op} `) ? `${op} ${name}` : name);", s)
        self.assertNotRegex(s, r"opOf\(p\.id\)\?\.name\}? \$?\{p\.name\}", "no place label written by hand")
        self.assertEqual(len(re.findall(r"labelOf\(p\)", s)), 5)

    def test_no_place_of_the_file_reads_with_its_operator_twice(self):
        if not os.path.exists(FILE):
            self.skipTest("the page file is not in this checkout")
        with open(FILE, encoding="utf-8") as f:
            F = json.load(f)
        names = {o["id"]: o["name"] for o in F["operators"]}
        labels = [place_label(names.get(op), p["name"]) for op, places in F["places"].items() for p in places]
        self.assertTrue(labels)
        for lab in labels:
            words = lab.split()
            self.assertFalse(len(words) > 1 and words[0] == words[1], lab)
        self.assertIn("SPP North hub", labels)
        self.assertIn("CAISO NP15 trading hub", labels)


if __name__ == "__main__":
    unittest.main()
