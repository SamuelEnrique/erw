"""Session 532: /about#digest says what the brief does since session 470.

The page's words are pinned to the code: each function a comment beside the text names exists, and the figures the page
states (seven days, 5 or more, 7 or more, up to five, up to three) are the code's own. No test reaches the network or a model.
"""

import inspect
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402

PAGE = os.path.join(ROOT, "site", "app", "about", "page.tsx")


def page():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


def digest_section():
    t = page()
    start = t.index('id="digest"')
    return t[start:t.index("The platform", start)]


def visible(text):
    """The section as a reader sees it: JSX comments taken out, entities read, white space joined."""
    t = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    t = t.replace("&apos;", "'").replace("&ldquo;", '"').replace("&rdquo;", '"').replace('{" "}', " ")
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


class ThePageSaysWhatTheBriefDoes(unittest.TestCase):
    def test_the_four_claims_are_in_the_visible_text(self):
        v = visible(digest_section())
        for words in ("One event once.", "the top 10 still holds ten stories",
                      "A story that a digest of the seven days before printed is left out",
                      "5 or more for significance", "(via Google News)",
                      "the stories the previous week's Roundup printed"):
            self.assertIn(words, v)

    def test_each_function_a_comment_names_exists(self):
        sec = digest_section()
        # the claims' comments, not the section's opening note
        comments = [c for c in re.findall(r"\{/\*(.*?)\*/\}", sec, flags=re.S) if not c.strip().startswith("Session")]
        funcs = set()
        for c in comments:
            for group in re.findall(r"brief\.py ([^;:]+)", c):
                for part in re.sub(r"\([^)]*\)", "", group).split(","):
                    word = part.strip().split(" ")[0]
                    if re.fullmatch(r"[a-z_]+", word):
                        funcs.add(word)
        self.assertTrue({"select", "same_event", "one_per_event", "unique_items", "drop_repeated_items",
                         "earlier_issues", "repeat_of", "not_shown_before", "build_clusters", "link_text"} <= funcs, funcs)
        for f in funcs:
            self.assertTrue(hasattr(brief, f), f"brief.{f} is named on /about but is not in brief.py")
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
        with open(os.path.join(ROOT, "warehouse", "news", "email_digest.py"), encoding="utf-8") as f:
            self.assertIn("def story_list", f.read())
        with open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8") as f:
            self.assertIn("brief.not_shown_before", f.read())

    def test_the_page_s_figures_are_the_code_s(self):
        self.assertEqual(brief.AI_MIN_SIG, 5)
        self.assertEqual(inspect.signature(brief.earlier_issues).parameters["days"].default, 7)
        sel = inspect.getsource(brief.select)
        self.assertIn('clusters["ai"] >= 7', sel)
        self.assertIn("ai = clusters[", sel)
        self.assertRegex(sel, r"AI_MIN_SIG[^\n]*\.head\(5\)")
        self.assertRegex(sel, r"by_group\[g\] = [^\n]*\.head\(3\)")
        self.assertIn("top10, folded = one_per_topic(clusters, 10, log)", sel)   # session 802: one topic, one item
        self.assertIn(".values())[:3]", inspect.getsource(brief.build_clusters))
        same = inspect.getsource(brief.same_event)
        self.assertIn("len(both) >= 4", same)
        ev = inspect.getsource(brief.event_figures)
        self.assertIn("v * mult >= 1e6", ev)
        self.assertIn("v >= 10", ev)
        self.assertEqual(brief.link_text([("Reuters", "https://news.google.com/rss/articles/x")]),
                         "[Reuters](https://news.google.com/rss/articles/x) (via Google News)")
        self.assertEqual(brief.link_text([("Reuters", "https://reuters.com/x")]), "[Reuters](https://reuters.com/x)")

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), page())


if __name__ == "__main__":
    unittest.main()
