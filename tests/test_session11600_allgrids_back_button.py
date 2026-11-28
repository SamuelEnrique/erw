"""Session 11600 (chain 780): the All grids tab follows the back button to the address it was opened on.

The read of 26 November (docs/reviews/browser-read-2026-11-26.md, row CP2) found that on
/cost-of-power?view=allgrids a choice (the Profile list set to "flexible") followed by the browser's back button put
the address back and left the page as it was, 8 of 8 tries. The read of 28 November found why, in a build
(docs/reviews/browser-read-2026-11-28.md): the entry the page is opened on holds no state at all
(`history.state === null` on the tab, the router's two keys on every other page tried), and the site's router lets a
move of the history that carries no state pass. Two effects of the tab write the address as the page first draws,
before the router has taken hold of the history, and each handed `null` to `history.replaceState`:

- site/app/cost-of-power/LargeLoadRules.tsx (the rules' filters kept in the address; drawn on both views of the tab);
- site/app/cost-of-power/AllGridsNodes.tsx (the node list's sort and filters).

Each now hands back the entry's own state. A press that writes the address later (after the router is in place) is
not what wiped it, and is left as it was.

    python -m pytest tests/test_session11600_allgrids_back_button.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def effects(text):
    """The bodies of a file's `useEffect(() => { ... }, [...])` calls, by brace matching."""
    out = []
    for m in re.finditer(r"useEffect\(\(\) => \{", text):
        depth, i = 1, m.end()
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        out.append(text[m.end():i])
    return out


class TheEntryKeepsItsState(unittest.TestCase):
    def test_the_rules_effect_hands_back_the_entrys_state(self):
        rules = src("site", "app", "cost-of-power", "LargeLoadRules.tsx")
        self.assertIn('window.history.replaceState(window.history.state, "", `${window.location.pathname}${s ? `?${s}` : ""}${window.location.hash}`);', rules)

    def test_the_nodes_effect_hands_back_the_entrys_state(self):
        nodes = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertIn('window.history.replaceState(window.history.state, "", `${window.location.pathname}${s ? `?${s}` : ""}`);', nodes)
        self.assertNotIn("replaceState(null", nodes)

    def test_no_effect_of_the_tab_writes_the_address_with_no_state(self):
        # an effect runs as the page first draws: a null there wipes the router's state on the opening entry
        for name in sorted(os.listdir(os.path.join(ROOT, "site", "app", "cost-of-power"))):
            if not name.endswith(".tsx"):
                continue
            for body in effects(src("site", "app", "cost-of-power", name)):
                self.assertNotIn("replaceState(null", body, name)
                self.assertNotIn("pushState(null", body, name)

    def test_the_press_that_writes_the_address_later_is_left(self):
        # openRule runs on a press, after the router has taken hold of the history: the router then keeps its own state
        rules = src("site", "app", "cost-of-power", "LargeLoadRules.tsx")
        self.assertEqual(rules.count("replaceState(null"), 1)
        self.assertIn('if (window.location.hash) window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}#llr`);', rules)

    def test_no_em_dash(self):
        for name in ("LargeLoadRules.tsx", "AllGridsNodes.tsx"):
            self.assertNotIn(EM, src("site", "app", "cost-of-power", name), name)


if __name__ == "__main__":
    unittest.main()
