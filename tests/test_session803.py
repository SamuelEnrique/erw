"""Session 803: the sources say the outlet (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 3).

Where the ingest's resolver failed (18,976 of 18,981 Google News links), the item shows the outlet's name from the feed's
own field as the link text with "(via Google News)" after it (session 470's rule, kept), never the address; the email's
text part the same (it printed the 200-character Google address in full); an outlet whose stories ask for a license (the
news index's publishers in warehouse/metadata/license_status.csv while its row is "license needed", the ruling of 21
October) is named with no link, so the item shows the outlet and the title only. No model, no network.
"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import email_digest  # noqa: E402

GN = "https://news.google.com/rss/articles/CBMisgFBVV95cUxNOXVpSjBJbkx2b2NpZ1R5U1ViUklsVVFNZnNxc0QzcUxv?oc=5"
HEADER = "table,status,from,publishers,verdict,permission,permission_ref,note\n"


def status_file(d, status="license needed"):
    p = os.path.join(d, "license_status.csv")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(HEADER + f"news_index,{status},2026-10-21,Bloomberg; Reuters; Utility Dive,needs written permission,,,note\n"
                + "nyiso_as_prices,license needed,2026-10-21,NYISO,needs written permission,,,note\n")
    return p


class TheOutlets(unittest.TestCase):
    def test_the_news_index_s_publishers_while_held(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(brief.licensed_outlets(status_file(d)), {"Bloomberg", "Reuters", "Utility Dive"})

    def test_none_once_the_hold_is_lifted(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(brief.licensed_outlets(status_file(d, status="public")), set())

    def test_none_without_the_file(self):
        self.assertEqual(brief.licensed_outlets(os.path.join(tempfile.gettempdir(), "no-such-license-file.csv")), set())

    def test_the_repository_s_file_names_the_outlets_of_21_october(self):
        got = brief.licensed_outlets()
        if not got:
            self.skipTest("the news index is not held on this checkout")
        self.assertTrue({"Bloomberg", "Reuters", "Financial Times", "WSJ"} <= got, got)


class TheSourceText(unittest.TestCase):
    lic = {"Bloomberg", "Reuters", "Utility Dive"}

    def test_a_google_news_address_shows_the_outlet_s_name_and_where_it_goes(self):
        self.assertEqual(brief.source_text("Heatmap News", GN, self.lic), f"[Heatmap News]({GN}) (via Google News)")

    def test_an_outlet_s_own_address_is_a_plain_link(self):
        self.assertEqual(brief.source_text("T&D World", "https://www.tdworld.com/x", self.lic), "[T&D World](https://www.tdworld.com/x)")

    def test_a_licensed_outlet_is_named_with_no_link(self):
        self.assertEqual(brief.source_text("Reuters", GN, self.lic), "Reuters")
        self.assertEqual(brief.source_text("Bloomberg.com", GN, {"Bloomberg"}), "Bloomberg.com")   # the feed's field, the list's name
        self.assertEqual(brief.outlet_key("OilPrice.com"), "oilprice")
        self.assertEqual(brief.source_text("Utility Dive", "https://www.utilitydive.com/news/x", self.lic), "Utility Dive")

    def test_link_text_joins_them(self):
        t = brief.link_text([("Reuters", GN), ("POWER Magazine", "https://www.powermag.com/x"), ("Bloomberg.com", GN)], self.lic)
        # Bloomberg.com is the feed's name for the list's Bloomberg: named, no link
        self.assertEqual(t, "Reuters, [POWER Magazine](https://www.powermag.com/x), Bloomberg.com")
        self.assertNotIn("news.google.com", t)

    def test_the_session_470_form_holds_without_a_hold(self):
        t = brief.link_text([("Reuters", GN), ("POWER", "https://www.powermag.com/x")], set())
        self.assertIn(f"[Reuters]({GN}) (via Google News)", t)
        self.assertNotIn("powermag.com/x) (via", t)

    def test_the_also_line_names_a_licensed_outlet_without_a_link(self):
        recs = [{"cluster_id": "b", "title": "Nextdc cuts outlook", "sector": "datacenter_power", "links": [("Reuters", GN)], "parties": ""}]
        with tempfile.TemporaryDirectory() as d:
            brief._LICENSED[brief.LICENSE_FILE] = brief.licensed_outlets(status_file(d))
            try:
                self.assertEqual(brief.also_line(recs), "Also on this topic: Nextdc cuts outlook (Reuters).")
            finally:
                brief._LICENSED.pop(brief.LICENSE_FILE, None)


class TheEmail(unittest.TestCase):
    def lines(self, src):
        return ["# ERW's Energy Digest, 2026-10-21", "", "## Top of the industry", "",
                "1. **Head** (oil)  ", f"   The why. Sources: {src}", "", "## By sector"]

    def test_a_google_news_address_is_not_printed_in_the_text_part(self):
        items = email_digest.numbered(self.lines(f"[Bloomberg.com]({GN}) (via Google News)"), ("## Top of the industry",))
        self.assertEqual(items[0]["src"], ("Bloomberg.com", GN))
        t, h = email_digest.story_list(items)
        self.assertEqual(t[-1], "   Bloomberg.com (via Google News)")
        self.assertNotIn("news.google.com", "\n".join(t))
        self.assertIn(f'<a href="{GN}">Bloomberg.com</a> (via Google News)', h)

    def test_an_outlet_s_own_address_is_printed(self):
        items = email_digest.numbered(self.lines("[T&D World](https://www.tdworld.com/x)"), ("## Top of the industry",))
        t, h = email_digest.story_list(items)
        self.assertEqual(t[-1], "   T&D World: https://www.tdworld.com/x")
        self.assertIn('<a href="https://www.tdworld.com/x">T&amp;D World</a>', h)

    def test_a_licensed_outlet_is_named_alone(self):
        items = email_digest.numbered(self.lines("Reuters, [POWER Magazine](https://www.powermag.com/x)"), ("## Top of the industry",))
        self.assertEqual(items[0]["src"], ("Reuters", None))
        self.assertEqual(items[0]["why"], "The why.")
        t, h = email_digest.story_list(items)
        self.assertEqual(t[-1], "   Reuters")
        self.assertNotIn("<a ", h.split("</span>")[-1] if "</span>" in h else h)
        self.assertIn("Reuters</li>", h)

    def test_an_item_with_no_source(self):
        items = email_digest.numbered(self.lines(""), ("## Top of the industry",))
        self.assertIsNone(items[0]["src"])
        t, _ = email_digest.story_list(items)
        self.assertEqual(len(t), 2)


class ThePrintedIssue(unittest.TestCase):
    """A top item built from fixture clusters, with the hold on: the outlet and the title only."""

    def test_the_item_lines(self):
        r = {"cluster_id": "a", "titles": ["T"], "sector": "oil", "parties": "Iran", "sig": 8, "ai": 0, "why": "Why.",
             "mw": "", "price": "", "n": 2, "first": "", "summary": "", "links": [("Reuters", GN), ("OilPrice.com", "https://oilprice.com/x")],
             "also": []}
        with tempfile.TemporaryDirectory() as d:
            brief._LICENSED[brief.LICENSE_FILE] = brief.licensed_outlets(status_file(d))
            try:
                L = brief.item_lines(r, "1. **Head** (oil)  ", brief.why_line(r["why"], "Head") + " " + brief.detail(r, "Head"),
                                     f"Sources: {brief.link_text(r['links'])}")
            finally:
                brief._LICENSED.pop(brief.LICENSE_FILE, None)
        self.assertEqual(L[1], "   Why. parties: Iran. Sources: Reuters, [OilPrice.com](https://oilprice.com/x)")
        self.assertEqual(brief.assert_unique(L), 1)


if __name__ == "__main__":
    unittest.main()
