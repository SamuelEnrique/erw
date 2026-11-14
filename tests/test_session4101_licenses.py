"""Session 4101 (chain 229, the licensing sweep): verdicts confirmed against the publishers' current pages, and the
verdict and the flag agreeing for every table.

scripts/license_confirm.py checks a verdict's quoted sentence on a page read now (piece by piece across "[...]"),
answers a robots file for the ERW's agent and for Anthropic's crawlers by name, cuts sentences by code, and records
warehouse/metadata/license_confirmations.csv. scripts/licenses.py writes the confirmations and the stale count into
docs/licenses.md.
"""

import csv
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import license_confirm as C  # noqa: E402
import licenses as L  # noqa: E402

META = os.path.join(ROOT, "warehouse", "metadata")

# Tables flagged public with a publisher no read covers, as chain 229 found them (session 4100). The sweep reads
# them; this set only shrinks. A table that joins it fails the test.
UNREAD_PUBLIC_KNOWN = {
    "company_aliases", "company_directory", "company_links", "datacenter_facilities", "datacenter_projects", "energy_deals", "news_index",
    "ferc714_forecast_growth", "ferc714_planning_area_forecasts", "impact_tax_rules", "large_load_connection_rules",
    "large_load_public", "large_load_rule_reads", "large_load_rules", "policy_action_tags", "policy_actions", "policy_reads",
    "usace_nid_dams", "utility_large_load_tariffs",
    # session 3937 (chain 267): the large-load research pass's three tables, public row by row under the owner's ruling 4
    # of 6 November 2026 as utility_large_load_tariffs is (each written row a commission's copy, a filed tariff book, an SEC
    # filing, a grid operator's posted document or a legislature's text; rows whose only host asks permission not written)
    "state_large_load_laws", "utility_large_load_rule_changes", "utility_large_load_rules",
}


def rows(name):
    with open(os.path.join(META, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class Wildcards(unittest.TestCase):
    """Session 4161: urllib's parser reads "*" and "$" literally; the confirmation tool reads them as the convention does."""

    def test_a_star_rule_refuses_every_path_below_the_root(self):
        lines = ["User-agent: *", "Disallow: /*/", "Disallow: /fmtemp/"]
        self.assertFalse(C.wildcard_allows(lines, "ERW-connector", "/taxes/"))
        self.assertFalse(C.wildcard_allows(lines, "ClaudeBot", "/about/policies/privacy.php"))
        self.assertTrue(C.wildcard_allows(lines, "ERW-connector", "/index.html"))

    def test_the_longest_rule_wins_and_allow_wins_a_tie(self):
        lines = ["User-agent: *", "Disallow: /data/", "Allow: /data/terms$", "Allow: /x", "Disallow: /x"]
        self.assertTrue(C.wildcard_allows(lines, "ERW-connector", "/data/terms"))
        self.assertFalse(C.wildcard_allows(lines, "ERW-connector", "/data/terms/more"))
        self.assertTrue(C.wildcard_allows(lines, "ERW-connector", "/x"))

    def test_a_group_naming_the_agent_replaces_the_star_group(self):
        lines = ["User-agent: *", "Disallow:", "", "User-agent: ClaudeBot", "User-agent: GPTBot", "Disallow: /"]
        self.assertTrue(C.wildcard_allows(lines, "ERW-connector", "/terms"))
        self.assertFalse(C.wildcard_allows(lines, "ClaudeBot", "/terms"))


class Pieces(unittest.TestCase):
    def test_a_sentence_joined_with_an_ellipsis_in_brackets_is_found_piece_by_piece(self):
        s = "Permission is granted to copy the data. [...] Write to the office at 1 Main Street for anything else."
        self.assertEqual(C.pieces(s), ["Permission is granted to copy the data.", "Write to the office at 1 Main Street for anything else."])

    def test_a_note_in_brackets_is_not_a_piece(self):
        self.assertEqual(C.pieces("[The site's footer:] Content is available under CC BY 4.0."), ["Content is available under CC BY 4.0."])

    def test_typographic_quotes_and_spaces_are_made_plain(self):
        self.assertEqual(C.norm("It" + chr(0x2019) + "s" + chr(0xA0) + " free" + chr(0x200B) + "."), "It's free.")


class OnThePage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.meta = os.path.join(self.tmp, "meta")
        os.makedirs(self.meta)
        self.pages = os.path.join(self.tmp, "pages")
        self.reads = os.path.join(self.meta, "license_reads.csv")
        self.verdicts = os.path.join(self.meta, "license_verdicts.csv")
        self.conf = os.path.join(self.meta, "license_confirmations.csv")
        C.write_rows(self.reads, ["n", "publisher", "url", "final_url", "read_at", "http_status", "bytes", "sha256", "content_type", "outcome"], [
            dict(n="1", publisher="Example Agency", url="https://x.gov/terms", read_at="2026-10-01T00:00:00Z", content_type="text/html", outcome="read"),
            dict(n="2", publisher="Example Agency, current terms (session 4101)", url="https://x.gov/terms", read_at="2026-11-13T00:00:00Z", content_type="text/html", outcome="read"),
            dict(n="3", publisher="Example Agency, x.gov's robots file (session 4101)", url="https://x.gov/robots.txt", read_at="2026-11-13T00:00:00Z", content_type="text/plain", outcome="read"),
        ])
        C.write_rows(self.verdicts, C.VERDICT_COLS, [dict(key="Example", read="1", sentence="Our data are in the public domain. [...] Please cite the agency.", verdict="may be public", if_commercial="may be public")])
        self.save(2, "Example Agency, current terms (session 4101)", b"<html><body><p>Our data are in the <b>public domain</b>.</p><p>Please cite the agency.</p><script>x()</script></body></html>")
        self.save(3, "Example Agency, x.gov's robots file (session 4101)", b"User-agent: *\nDisallow: /private # a note\n\nUser-agent: ClaudeBot\nDisallow: /\n")
        self.patch = mock.patch.multiple(C, READS=self.reads, VERDICTS=self.verdicts, CONFIRMATIONS=self.conf, SESSION="4101")
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def save(self, n, publisher, body):
        d = os.path.join(self.pages, f"{n:02d}_{C.slug(publisher)}")
        os.makedirs(d)
        with open(os.path.join(d, "page.bin"), "wb") as f:
            f.write(body)

    def test_the_sentence_is_found_on_the_new_page_without_its_markup(self):
        self.assertTrue(C.find("Example", "2", [self.pages], out=lambda *_: None))

    def test_a_confirmation_row_is_written_and_a_second_run_replaces_it(self):
        C.confirm("Example", "2", note="first", pages=[self.pages], out=lambda *_: None)
        C.confirm("Example", "2", note="again", pages=[self.pages], out=lambda *_: None)
        got = C.rows(self.conf)
        self.assertEqual(len(got), 1)
        self.assertEqual((got[0]["sentence"], got[0]["verdict_after"], got[0]["session"], got[0]["note"]), ("on the page", "may be public", "4101", "again"))

    def test_a_sentence_gone_from_the_page_is_not_confirmed(self):
        C.write_rows(self.verdicts, C.VERDICT_COLS, [dict(key="Example", read="1", sentence="All rights reserved; no copying at all.", verdict="forbidden", if_commercial="forbidden")])
        state = C.confirm("Example", "2", pages=[self.pages], out=lambda *_: None)
        self.assertTrue(state.startswith("changed"))
        self.assertEqual(C.rows(self.conf)[0]["verdict_after"], "")

    def test_robots_refuses_when_anthropics_crawler_is_named(self):
        lines = []
        self.assertEqual(C.robots("3", "/legal/terms", [self.pages], out=lines.append), 1)
        self.assertIn("ClaudeBot: REFUSED /legal/terms", lines)
        self.assertIn("ERW-connector: may fetch /legal/terms", lines)
        self.assertFalse(any("a note" in x for x in lines))          # comments are taken away before the rules are printed

    def test_a_verdict_is_cut_by_index_from_the_page_never_typed(self):
        sents = C.cut("2", [], [self.pages], out=lambda *_: None)
        row = C.verdict("Example", "2", "0+1", "may be public", "may be public", replace=True, pages=[self.pages], out=lambda *_: None)
        self.assertEqual(row["sentence"], sents[0] + " " + sents[1])
        self.assertEqual(C.rows(self.conf)[0]["sentence"], "cut again from this page")

    def test_a_footer_after_menu_words_is_cut_from_its_phrase(self):
        self.save(4, "Example Agency, its footer (session 4112)", b"<html><body><p>Home Data Contact (c) Example Agency. All rights reserved.</p></body></html>")
        with open(self.reads, "a", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\n").writerow(["4", "Example Agency, its footer (session 4112)", "https://x.gov/", "",
                                                         "2026-11-13T00:00:00Z", "200", "1", "x", "text/html", "read"])
        row = C.verdict("Example", "4", "0+1", "needs written permission", "needs written permission", replace=True, start="(c) Example",
                        pages=[self.pages], out=lambda *_: None)
        self.assertEqual(row["sentence"], "(c) Example Agency. All rights reserved.")
        row = C.verdict("Example", "4", "0+1", "needs written permission", "needs written permission", replace=True, start="(c) Example",
                        end="Agency.", pages=[self.pages], out=lambda *_: None)
        self.assertEqual(row["sentence"], "(c) Example Agency.")
        with self.assertRaises(SystemExit):
            C.verdict("Example", "4", "0", "needs written permission", "needs written permission", replace=True, start="not there",
                      pages=[self.pages], out=lambda *_: None)

    def test_a_verdict_is_one_of_the_four(self):
        with self.assertRaises(SystemExit):
            C.verdict("Example", "2", "0", "probably fine", "may be public", replace=True, pages=[self.pages], out=lambda *_: None)


class TheRecord(unittest.TestCase):
    def test_every_confirmation_names_a_verdict_and_a_read_of_a_current_page(self):
        verdicts = {r["key"]: r for r in rows("license_verdicts.csv")}
        reads = {r["n"]: r for r in rows("license_reads.csv")}
        for c in rows("license_confirmations.csv"):
            self.assertIn(c["key"], verdicts)
            self.assertIn(c["read"], reads)
            self.assertTrue(reads[c["read"]]["outcome"].startswith("read"), c)
            self.assertEqual(c["read_at"], reads[c["read"]]["read_at"])
            if c["sentence"] in ("on the page", "cut again from this page"):
                self.assertEqual(c["verdict_after"], verdicts[c["key"]]["verdict"], c["key"])

    def test_a_confirmation_never_loosens_a_verdict(self):
        order = L.ORDER
        for c in rows("license_confirmations.csv"):
            if c["verdict_after"] and c["verdict_before"]:
                self.assertGreaterEqual(order.index(c["verdict_after"]), order.index(c["verdict_before"]), c["key"])

    def test_every_session_41xx_read_of_a_page_has_its_hosts_robots_read_first(self):
        reads = rows("license_reads.csv")
        for r in reads:
            if "(session 41" in r["publisher"] and "robots file" not in r["publisher"] and r["outcome"].startswith("read"):
                host = r["url"].split("/")[2]
                robots = [x for x in reads if f"https://{host}/robots.txt" in (x["url"], x["final_url"]) and x["read_at"] <= r["read_at"]
                          and "(session 41" in x["publisher"]]
                self.assertTrue(robots, f"{r['publisher']}: no robots read of {host} before it")


class FlagAndVerdict(unittest.TestCase):
    """The flag in coverage.csv and the verdict in docs/licenses.md agree for every table (roadmap item 5)."""

    def lines(self):
        verdicts = {r["key"]: r for r in rows("license_verdicts.csv")}
        tables = {r["table"]: r for r in rows("license_tables.csv")}
        needed = L.license_needed()
        out = []
        for r in rows("coverage.csv"):
            pubs = [p for p in tables[r["table"]]["publishers"].split("; ") if p]
            v, why, unread = L.judge(pubs, verdicts)
            out.append((r["table"], r["license"], v, unread, r["table"] in needed))
        return out

    def test_no_table_is_flagged_public_where_a_verdict_read_asks_more_unless_a_ruling_holds_it(self):
        bad = [t for t, flag, v, _, ruled in self.lines() if flag == "public" and v != L.PUBLIC and not ruled]
        self.assertEqual(bad, [])

    def test_no_new_table_is_flagged_public_with_a_publisher_not_read(self):
        unread_public = {t for t, flag, _, unread, _ in self.lines() if flag == "public" and unread}
        self.assertEqual(unread_public - UNREAD_PUBLIC_KNOWN, set())

    def test_the_document_says_what_the_files_say(self):
        with open(os.path.join(ROOT, "docs", "licenses.md"), encoding="utf-8") as f:
            doc = f.read()
        self.assertIn("## Confirmed against the current page (chain 229)", doc)
        n = len({c["key"] for c in rows("license_confirmations.csv")})
        self.assertIn(f"session 4101 on): {n} publishers", doc)


if __name__ == "__main__":
    unittest.main()
