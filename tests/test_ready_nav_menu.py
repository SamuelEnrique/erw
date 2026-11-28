"""Session 11405 (chain 770, part C): decision 4 of the weekend page of 28 November 2026 readied, not landed without
Samuel's word. The ten pages no menu led to (/forecast, /equities, /states, /industry, /ai-energy, /queues/places,
/storage/places, /curtailment/where-when, /conditions, /congestion) are in the menu (site/lib/pages.ts), each under
the name its own page gives itself (its metadata title, which its header repeats), each beside its nearest sibling;
no menu list holds more than eight. The menu's name for /impact is kept: the page calls itself "Local impact".
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")

TEN = {
    "/equities": "Economics",
    "/conditions": "Grid", "/congestion": "Grid", "/forecast": "Grid", "/industry": "Grid", "/curtailment/where-when": "Grid",
    "/states": "Infrastructure", "/queues/places": "Infrastructure", "/storage/places": "Infrastructure",
    "/ai-energy": "Analysis",
}
# where the page's own title is held, when not in its page.tsx (the two tools whose title is a constant)
TITLE_AT = {"/forecast": (("site", "lib", "predict.ts"), r'export const LABEL = "([^"]+)"'),
            "/equities": (("site", "app", "equities", "view.tsx"), r'const TITLE = "([^"]+)"')}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def own_title(href):
    if href in TITLE_AT:
        parts, rx = TITLE_AT[href]
        return re.search(rx, src(*parts)).group(1)
    page = src("site", "app", *href.strip("/").split("/"), "page.tsx")
    return re.search(r'export const metadata: Metadata = \{ title: "([^"]+)"', page).group(1)


@unittest.skipUnless(NODE, "node is not installed")
class TheMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = ("import { GROUPS } from './lib/pages.ts'; console.log(JSON.stringify(GROUPS.map((g) => ({ label: g.label, aside: !!g.aside, "
                "pages: g.pages.map((p) => [p.href, p.menu ?? p.label, p.label]), sub: g.sub ? { label: g.sub.label, pages: g.sub.pages.map((p) => [p.href, p.menu ?? p.label, p.label]) } : null }))));")
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        cls.groups = json.loads(r.stdout.strip().splitlines()[-1])

    def where(self, href):
        for g in self.groups:
            for p in g["pages"] + (g["sub"]["pages"] if g["sub"] else []):
                if p[0] == href:
                    return g["label"], p
        return None, None

    def test_every_one_of_the_ten_is_in_the_menu_under_its_own_name(self):
        for href, group in TEN.items():
            g, p = self.where(href)
            self.assertEqual(g, group, href)
            self.assertEqual(p[1], own_title(href), href)     # the name the menu shows
            self.assertEqual(p[2], own_title(href), href)     # and the page's own name everywhere else

    def test_impact_keeps_local_impact(self):
        g, p = self.where("/impact")
        self.assertEqual((g, p[1]), ("Economics", "Local impact"))
        self.assertEqual(own_title("/impact"), "Local impact")

    def test_no_menu_list_holds_more_than_eight(self):
        for g in self.groups:
            self.assertLessEqual(len(g["pages"]), 8, g["label"])
            if g["sub"]:
                self.assertLessEqual(len(g["sub"]["pages"]), 8, g["label"])

    def test_each_page_once(self):
        hrefs = [p[0] for g in self.groups for p in g["pages"] + (g["sub"]["pages"] if g["sub"] else [])]
        self.assertEqual(len(hrefs), len(set(hrefs)))

    def test_the_sub_group_of_infrastructure(self):
        g = next(x for x in self.groups if x["label"] == "Infrastructure")
        self.assertEqual(g["sub"]["label"], "Every authority and state")
        self.assertEqual([p[0] for p in g["sub"]["pages"]], ["/states", "/queues/places", "/storage/places"])


class TheGate(unittest.TestCase):
    def test_each_is_in_review_and_has_a_line_or_a_parent_line(self):
        rel = dict(re.findall(r'^\s*"(/[^"]*)": "(live|review)"', src("site", "lib", "release.ts"), flags=re.M))
        for href in TEN:
            k = href
            while k not in rel and "/" in k[1:]:
                k = k[:k.rfind("/")]
            self.assertEqual(rel.get(k), "review", href)

    def test_the_inventory_names_each(self):
        tools = src("docs", "tools.md")
        for href in TEN:
            self.assertIn(f"`{href}`", tools, href)


if __name__ == "__main__":
    unittest.main()
