"""Session 8905 (chain 590): the tour's resource-map stop opens the Resources tab of /map, and the headings it quotes
are on that tab (they were not on the Projects tab, where "/map" alone led)."""
import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOUR = open(os.path.join(ROOT, "site", "lib", "tour.ts"), encoding="utf-8").read()


def stop_block(title):
    m = re.search(r"\{\s*(?://[^\n]*\n\s*)*href: \"([^\"]+)\", title: \"%s\".*?headings: \[([^\]]*)\]" % re.escape(title), TOUR, re.S)
    assert m, title
    return m.group(1), re.findall(r'"([^"]+)"', m.group(2))


class ResourceStop(unittest.TestCase):
    def test_opens_the_resources_tab(self):
        href, _ = stop_block("What is under the ground and in the wind")
        self.assertEqual(href, "/map?tab=resources")

    def test_its_headings_are_on_the_resources_tab(self):
        _, heads = stop_block("What is under the ground and in the wind")
        src = "".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(ROOT, "site", "app", "resources", "*.tsx")))
        for h in heads:
            self.assertIn(h, src, h)
        self.assertNotIn("The project map", heads)

    def test_the_tab_is_one_the_map_page_knows(self):
        tabs = open(os.path.join(ROOT, "site", "lib", "tabs.ts"), encoding="utf-8").read()
        self.assertRegex(tabs, r'"/map": \{ param: "tab", .*\["resources", "Resources"\]')


if __name__ == "__main__":
    unittest.main()
