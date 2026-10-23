"""Session 473: the brand applied to the Grid page and /board (docs/brand.md, direction A, as the battery page carries it).

Both pages already took the wrapper (<Brand>, sessions 237 and 240), so the tokens' rules reached their shared pieces;
what did not reach them was markup of their own components that the tokens cannot override without moving other pages:
type at 10 and 11 px (the brand's smallest size is 12), rounded corners on labels and swatches (corners are square),
two hover cards with a shadow (nothing casts a shadow), and uppercase labels with letter-spacing (sentence case, no
letter-spacing; tokens.css already neutralized them, so their removal moves nothing). Each is fixed in the component,
and only in components that no page but the Grid page or the board draws: the battery page, the reference, does not
move. No number moved: every checked-number key is where it was (check-values on a build is the landing's proof).
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")

# the components the two pages draw that are drawn by no other page (checked in session 473 by import search)
OWN = {
    "components/board/BoardView.tsx": 0,
    "components/board/Workbench.tsx": 0,
    "components/grid/Conditions.tsx": 11,  # session 1166: eight more, the F of "Yesterday" and the mix table, and its seven uses
    "components/grid/Emissions.tsx": 4,  # session 1151: one more, the last 24 hours' figures (F, grid_clean24_<grid>)
    "components/grid/YourGrid.tsx": 18,  # session 1166: one more, "Hours held" (series_n)
    "components/mix/Now.tsx": 2,
    "components/mix/views.tsx": 1,  # session 1166: the committed files' figures; its one K writes every key
    "app/network/Network.tsx": 2,
    "app/network/NetworkMap.tsx": 0,
    "app/network/NetworkGravity.tsx": 0,
    "components/StackedArea.tsx": 0,
    "components/grid/MixFigures.tsx": 1,  # session 1152: the energy mix panel (grid_mix_<grid>); its one F writes every key
    "components/grid/ScarcityPanel.tsx": 1,  # session 1154: the scarcity hours (grid_scarcity_<grid>); its one F writes every key
    "components/grid/CaisoAlertState.tsx": 1,  # session 1155: CAISO's alerts today (grid_caisoalert_caiso); its one F writes every key
}
FORBIDDEN = {
    "type under 12 px": re.compile(r"text-\[(?:[0-9]|1[01])(?:\.\d+)?px\]"),
    "a rounded corner": re.compile(r"\brounded(?:-(?:sm|md|lg|xl|full))?\b"),
    "a shadow": re.compile(r"\bshadow(?:-(?:sm|md|lg|xl))?\b"),
    "uppercase by style": re.compile(r"\buppercase\b"),
    "letter-spacing": re.compile(r"\btracking-(?:wide|wider|widest|tight)\b"),
    "a color literal": re.compile(r"#[0-9A-Fa-f]{6}\b"),
}


def src(rel):
    with open(os.path.join(SITE, rel), encoding="utf-8") as f:
        return f.read()


def class_values(text):
    """The values of every className attribute (string literals and template literals)."""
    return re.findall(r'className=(?:"([^"]*)"|\{`([^`]*)`\})', text)


class TheOwnComponents(unittest.TestCase):
    def test_no_class_the_brand_forbids(self):
        for rel in OWN:
            for a, b in class_values(src(rel)):
                cls = a or b
                for what, pat in FORBIDDEN.items():
                    self.assertIsNone(pat.search(cls), f"{rel}: {what} in className {cls!r}")

    def test_no_color_literal_anywhere_in_them(self):
        for rel in OWN:
            self.assertIsNone(FORBIDDEN["a color literal"].search(src(rel)), rel)

    def test_every_checked_number_key_is_still_there(self):
        for rel, n in OWN.items():
            self.assertEqual(src(rel).count("check="), n, rel)

    def test_no_other_page_draws_them(self):
        """A change here reaches the Grid page and the board only (the battery page is the reference and does not move)."""
        allowed = {"app/grid/page.tsx", "app/board/page.tsx", "components/board/BoardView.tsx", "components/grid/MixView.tsx",
                   "components/grid/YourGrid.tsx", "components/grid/NowView.tsx", "components/grid/NetworkView.tsx",
                   "components/mix/Now.tsx", "components/mix/views.tsx", "app/network/Network.tsx",
                   "components/grid/ScarcityPanel.tsx"}  # session 1154: drawn by the Grid page only; it takes Missing from mix/Now.tsx
        for dirpath, dirs, files in os.walk(SITE):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".next", "_retired", "public")]
            for fn in files:
                if not fn.endswith((".ts", ".tsx")):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, SITE).replace(os.sep, "/")
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                for spec in re.findall(r'^import (?!type )[^;]*?from "([^"]+)"', text, re.M | re.S):
                    if spec.startswith("@/"):
                        target = spec[2:]
                    elif spec.startswith("."):
                        target = os.path.normpath(os.path.join(os.path.dirname(rel), spec)).replace(os.sep, "/")
                    else:
                        continue
                    for comp in OWN:
                        if target == os.path.splitext(comp)[0] and rel != comp:
                            self.assertIn(rel, allowed, f"{rel} draws {comp}")


class TheBrandFile(unittest.TestCase):
    def test_the_tokens_already_neutralize_what_was_removed(self):
        """Uppercase and letter-spacing were already undone by tokens.css: removing the classes moves nothing."""
        t = src("app/tokens.css")
        self.assertRegex(t, r"\.brand-a \.uppercase \{\s*text-transform: none;[^}]*letter-spacing: 0;")
        self.assertRegex(t, r'\.brand-a \[role="tooltip"\],\s*\.brand-a a\.rounded \{\s*border-radius: 0;\s*box-shadow: none;')

    def test_both_pages_wear_the_wrapper(self):
        for rel in ("app/grid/page.tsx", "app/board/page.tsx"):
            self.assertIn("<Brand", src(rel), rel)

    def test_no_dash_in_this_sessions_files(self):
        for rel in ("tests/test_session473.py", "archive/sessions/SESSION_473_REPORT.md", "docs/brand/review-473/README.md"):
            p = os.path.join(ROOT, rel)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    text = f.read()
                self.assertNotIn(chr(0x2014), text, rel)
                self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
