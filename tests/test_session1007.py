"""Session 1007 (chain 070): /data says how to use the ERW in Python, Stata and R. The section's lines
(site/lib/packages.ts) are the specification's or a package README's, word for word: each install line and call in its
package's README, the lead, the citation and the held-table sentence in docs/methods/packages.md. The page draws the
section from that file and documents the download's CSV header. No request, no model call."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


LIB = src("site", "lib", "packages.ts")
SPEC = src("docs", "methods", "packages.md")


def ts_string(s):
    return s[1:-1].replace('\\"', '"').replace("\'", "'")


class Lines(unittest.TestCase):
    def test_every_panel_line_is_its_readme_s(self):
        panels = re.findall(r'name: "(\w+)",\s*install: \[(.*?)\],\s*calls: \[(.*?)\],\s*readme: "([^"]+)",\s*source: "([^"]+)"', LIB, re.S)
        self.assertEqual([p[0] for p in panels], ["Python", "Stata", "R"])
        for name, install, calls, readme, source in panels:
            text = src(*source.split("/"))
            lines = [ts_string(x) for x in re.findall(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"", install + calls)]
            self.assertEqual(len(re.findall(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"", calls)), 6, name)
            for ln in lines:
                self.assertIn(ln, text, f"{name}: {ln}")

    def test_the_lead_citation_and_held_sentence_are_the_specification_s(self):
        for const in ("PACKAGES_LEAD", "PACKAGES_CITATION", "PACKAGES_HELD"):
            m = re.search(rf"export const {const} =\s*\"((?:[^\"\\]|\\.)*)\";", LIB)
            self.assertTrue(m, const)
            self.assertIn(m.group(1), SPEC, const)


class Page(unittest.TestCase):
    def test_the_section_is_drawn_from_the_file(self):
        page = src("site", "app", "data", "page.tsx")
        self.assertIn('<Section title="Use the ERW in your tools" id="tools">', page)
        self.assertIn("PANELS.map", page)
        self.assertIn("# Downloaded from the ERW site&apos;s live set (Supabase) at", page)
        route = src("site", "app", "api", "download", "route.ts")
        self.assertIn("# Downloaded from the ERW site's live set (Supabase) at ${at}", route)
        self.assertNotIn(chr(0x2014), page + LIB)


if __name__ == "__main__":
    unittest.main()
