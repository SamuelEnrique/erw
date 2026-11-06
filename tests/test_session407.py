"""Session 407: ten LinkedIn posts, drafted, not posted.

docs/reviews/linkedin/posts-001-010.md (the ten posts), posts-notes.md (which three first, for Samuel's ruling),
posts.json (every key, the raw value the page read and the text it showed), read-407.mjs (the read from Supabase) and
shots-407.mjs (the ten 1200 by 627 images from a local build). These tests hold the posts to the chain's rules: under
150 words, the figure first, the address and the source last, at most three hashtags, no em dash, each post's key
named, every key of the series form check-values.mjs resolves, every page a route of the site, and the images either
made at 1200 by 627 or said to wait.
"""

import json
import os
import re
import struct
import unittest
from decimal import ROUND_HALF_UP, Decimal
from urllib.parse import urlsplit

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DIR = os.path.join(ROOT, "docs", "reviews", "linkedin")
POSTS = os.path.join(DIR, "posts-001-010.md")
NOTES = os.path.join(DIR, "posts-notes.md")
SPEC = os.path.join(DIR, "posts.json")
APP = os.path.join(ROOT, "site", "app")
NEXT_CONFIG = os.path.join(ROOT, "site", "next.config.ts")
SITE = "https://erw-flame.vercel.app"


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def bodies(text):
    """The text of each post: what stands between its two fences."""
    return re.findall(r"^```text\n(.*?)^```", text, re.S | re.M)


def sections(text):
    """Each post's section, from its heading to the next."""
    return re.split(r"^## Post \d+:", text, flags=re.M)[1:]


class TheFiles(unittest.TestCase):
    def test_every_file_exists_and_holds_no_dash(self):
        for name in ("posts-001-010.md", "posts-notes.md", "posts.json", "read-407.mjs", "shots-407.mjs"):
            t = read(os.path.join(DIR, name))
            self.assertNotIn(chr(0x2014), t, name)
            self.assertNotIn(chr(0x2013), t, name)

    def test_nothing_is_posted(self):
        self.assertIn("not posted", read(POSTS).splitlines()[0])
        self.assertIn("Nothing has been posted anywhere", read(POSTS))
        self.assertIn("Nothing is posted", read(NOTES))

    def test_no_script_posts_or_sends(self):
        for name in ("read-407.mjs", "shots-407.mjs"):
            t = read(os.path.join(DIR, name))
            self.assertNotIn("linkedin.com", t.lower(), name)
            self.assertNotRegex(t, r"method:\s*\"(POST|PUT|PATCH|DELETE)\"", name)


class TenPosts(unittest.TestCase):
    def setUp(self):
        self.text = read(POSTS)
        self.posts = bodies(self.text)
        self.spec = json.loads(read(SPEC))

    def test_ten_posts_ten_figures(self):
        self.assertEqual(len(self.posts), 10)
        self.assertEqual(len(sections(self.text)), 10)
        self.assertEqual([p["n"] for p in self.spec["posts"]], list(range(1, 11)))

    def test_each_under_150_words(self):
        for i, b in enumerate(self.posts, 1):
            n = len(re.findall(r"\S+", b))
            self.assertLess(n, 150, f"post {i}: {n} words")

    def test_at_most_three_hashtags(self):
        for i, b in enumerate(self.posts, 1):
            self.assertLessEqual(len(re.findall(r"(?<!\S)#\w+", b)), 3, f"post {i}")

    def test_the_figure_first(self):
        """The post's first sentence holds its figure, as the page shows it."""
        for b, p in zip(self.posts, self.spec["posts"]):
            first = b.strip().split("\n")[0]
            self.assertIn(p["shown"], first[:len(p["shown"]) + 12], f"post {p['n']}: {first[:80]}")

    def test_the_address_and_the_source_last(self):
        for b, p in zip(self.posts, self.spec["posts"]):
            lines = [x for x in b.strip().split("\n") if x.strip()]
            self.assertEqual(lines[-2], f"Page: {SITE}{p['page']}", f"post {p['n']}")
            self.assertTrue(lines[-1].startswith("Source: "), f"post {p['n']}")
            for x in lines[:-2]:
                self.assertNotIn(SITE, x, f"post {p['n']}: the address only on its line")

    def test_each_post_names_its_key_and_image(self):
        for sec, p in zip(sections(self.text), self.spec["posts"]):
            self.assertIn(f"- Key: `{p['key']}` ({p['shown']})", sec, f"post {p['n']}")
            self.assertIn(f"`{p['file']}`, from `{p['page']}`", sec, f"post {p['n']}")

    def test_every_figure_in_a_post_has_its_key(self):
        """Every number the post's text shows is a key's text in posts.json, or plain arithmetic or a date."""
        shown = {p["n"]: {p["shown"]} for p in self.spec["posts"]}
        for a in self.spec["also"]:
            shown[a["n"]].add(a["shown"])
        allowed = {"15-minute", "364", "728", "75", "40", "37", "eight", "2", "3"}
        for b, p in zip(self.posts, self.spec["posts"]):
            text = b.split("\n#")[0]
            for m in re.finditer(r"(?<![\w:/.,-])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?![\w-]|,\d)", text):
                v = m.group(0)
                if re.fullmatch(r"(19|20)\d\d", v) or v in allowed or re.fullmatch(r"\d{1,2}", v):
                    continue
                self.assertIn(v, shown[p["n"]], f"post {p['n']}: {v} has no key")
            for v in shown[p["n"]]:
                self.assertIn(v, b, f"post {p['n']}: {v} is listed and not used")


class TheKeys(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(read(SPEC))
        self.items = self.spec["posts"] + self.spec["also"]

    def test_series_keys_of_the_form_check_values_reads(self):
        for it in self.items:
            parts = it["key"].split("|")
            self.assertEqual(parts[0], "series", it["key"])
            self.assertIn(len(parts), (5, 6), it["key"])
            self.assertRegex(parts[4], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|\+00:00)$", it["key"])
            if parts[1] == "event_window_daily":
                self.assertEqual(len(parts), 6, f"{it['key']}: an event key carries its event")

    def test_the_shown_text_is_the_raw_value_rounded(self):
        """Whole counts with commas, everything else two decimals with commas, as the pages print these keys."""
        for it in self.items:
            raw, shown = it["raw"], it["shown"]
            plain = float(shown.replace(",", ""))
            digits = len(shown.split(".")[1]) if "." in shown else 0
            self.assertIn(digits, (0, 2), shown)
            half_up = Decimal(repr(raw)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)   # the page's toLocaleString
            self.assertEqual(float(half_up), plain, it["key"])
            self.assertEqual(f"{plain:,.{digits}f}", shown, it["key"])

    def test_every_page_is_a_route_or_a_redirect(self):
        config = read(NEXT_CONFIG)
        for p in self.spec["posts"]:
            path = urlsplit(p["page"]).path
            route = os.path.join(APP, *path.strip("/").split("/"), "page.tsx")
            redirect = f'source: "{path}"' in config
            self.assertTrue(os.path.exists(route) or redirect, p["page"])

    def test_the_battery_income_is_left_to_the_newsletter(self):
        """Session 406's newsletter took the battery's income by stream: no post repeats it."""
        for it in self.items:
            self.assertFalse(it["key"].startswith(("bs|", "bsa|")), it["key"])
            self.assertNotIn("storage_buildout_monthly", it["key"])
            self.assertNotIn("battery_", it["key"])


class TheImages(unittest.TestCase):
    def test_made_at_1200_by_627_or_said_to_wait(self):
        spec = json.loads(read(SPEC))
        text = read(POSTS)
        waiting = "point at files that do not exist yet" in text
        for p in spec["posts"]:
            f = os.path.join(DIR, p["file"])
            if not os.path.exists(f):
                self.assertTrue(waiting, f"{p['file']} is missing and the posts do not say the images wait")
                continue
            with open(f, "rb") as h:
                head = h.read(24)
            self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n", p["file"])
            self.assertEqual(struct.unpack(">II", head[16:24]), (1200, 627), p["file"])

    def test_the_shots_script_is_1200_by_627_and_uses_the_shared_charts(self):
        t = read(os.path.join(DIR, "shots-407.mjs"))
        self.assertIn("const W = 1200, H = 627", t)
        for marker in ("data-time-chart", "data-svg-chart", "data-series-chart"):
            self.assertIn(marker, t)
        self.assertIn("await unlock(base)", t)
        self.assertNotIn("INTERNAL_COSTS_TOKEN", t, "the token is posted by the form, never written here")


class TheNotes(unittest.TestCase):
    def test_three_first_with_why_for_the_ruling(self):
        t = read(NOTES)
        firsts = re.findall(r"^\d\. \*\*Post (\d+),", t, re.M)
        self.assertEqual(len(firsts), 3, firsts)
        self.assertIn("## For Samuel's ruling", t)
        self.assertIn("What a sceptic says", t)
        words = len(re.findall(r"\S+", t))
        self.assertLess(words, 900, f"one page: {words} words")


if __name__ == "__main__":
    unittest.main()
