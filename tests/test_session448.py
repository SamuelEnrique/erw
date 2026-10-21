"""Session 448: the economics pages against Lazard and the ATB (docs/reviews/cross-checks-external.md and .json).

Energy Research Warehouse (ERW). No network, no model. Checks the review and its rows file: no em or en dash; the
requests numbered from 1 and within the ceiling of 10, every one to Lazard's or NLR's hosts; every row with a source
link and a page or row reference, or a reason it was not read; the landing rows in the five columns
site/scripts/check-cross-checks.mjs reads, as that script asserts them (no empty cell, a link in every source, a
reason longer than 30 characters); the review's tables and the JSON holding the same rows; and the counts each page
would carry after the landing.

    python -m unittest tests.test_session448 -v
"""

import json
import os
import re
import unittest
from urllib.parse import urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MD = os.path.join(ROOT, "docs", "reviews", "cross-checks-external.md")
JS = os.path.join(ROOT, "docs", "reviews", "cross-checks-external.json")
HOSTS = {"www.lazard.com", "lazard.com", "atb.nlr.gov", "www.nlr.gov", "nlr.gov", "data.openei.org"}
REQUEST_HOSTS = {"www.lazard.com", "atb.nlr.gov", "www.nlr.gov"}
COLUMNS = ["Our figure", "Published figure", "Source and date", "Gap", "Reason"]
CHECKER = os.path.join(ROOT, "site", "scripts", "check-cross-checks.mjs")


def text():
    with open(MD, encoding="utf-8") as f:
        return f.read()


def data():
    with open(JS, encoding="utf-8") as f:
        return json.load(f)


def cells(line):
    """The cells of a markdown table row, with escaped pipes kept inside their cell."""
    parts = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip() for c in parts[1:-1]]


def section(md, head):
    """The lines of the markdown section that starts with `head`, up to the next heading of the same or higher level."""
    lines = md.split("\n")
    i = lines.index(head)
    level = len(head) - len(head.lstrip("#"))
    out = []
    for ln in lines[i + 1:]:
        if ln.startswith("#") and len(ln) - len(ln.lstrip("#")) <= level:
            break
        out.append(ln)
    return out


class Dashes(unittest.TestCase):
    def test_no_em_or_en_dash(self):
        for p in (MD, JS, __file__):
            with open(p, encoding="utf-8") as f:
                s = f.read()
            self.assertNotIn(chr(0x2014), s, p)
            self.assertNotIn(chr(0x2013), s, p)


class Requests(unittest.TestCase):
    def test_numbered_within_the_ceiling_and_to_the_two_publishers(self):
        rows = [cells(ln) for ln in section(text(), "## The requests") if ln.startswith("| ") and not ln.startswith("| n ")]
        self.assertTrue(1 <= len(rows) <= 10, len(rows))
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)))
        for r in rows:
            host = urlparse(r[2].strip("`")).hostname
            self.assertIn(host, REQUEST_HOSTS, r[2])
        self.assertIn(f"**{len(rows)} requests of the ceiling of 10**", text())

    def test_terms_and_robots_read_before_the_documents(self):
        rows = [cells(ln) for ln in section(text(), "## The requests") if ln.startswith("| ") and not ln.startswith("| n ")]
        first = {}
        for r in rows:
            u = r[2].strip("`")
            pub = "lazard" if "lazard" in u else "nlr"
            first.setdefault(pub, []).append(u)
        self.assertTrue(first["lazard"][0].endswith("/robots.txt") and "terms" in first["lazard"][1])
        self.assertTrue(first["nlr"][0].endswith("/robots.txt") and "disclaimer" in first["nlr"][1])


class Rows(unittest.TestCase):
    def test_every_row_has_a_source_and_a_reference(self):
        n = 0
        for note in data()["notes"]:
            for r in note["rows"]:
                n += 1
                self.assertRegex(r["source"], r"\]\(https://", r["our"])
                for u in re.findall(r"\]\((https://[^)]+)\)", r["source"]):
                    self.assertIn(urlparse(u).hostname, HOSTS, u)
                self.assertTrue(r["source_refs"], r["our"])
                for ref in r["source_refs"]:
                    self.assertTrue(ref["source"] and ref["page"], r["our"])
                self.assertTrue(r["read"].strip(), r["our"])
                self.assertTrue(r["where"].strip(), r["our"])
        self.assertEqual(n, 26)

    def test_rows_in_the_form_check_cross_checks_reads(self):
        with open(CHECKER, encoding="utf-8") as f:
            checker = f.read()
        self.assertIn('["Our figure", "Published figure", "Source and date", "Gap", "Reason"]', checker)
        self.assertIn("r[4].text.length > 30", checker)
        self.assertEqual(data()["columns"], COLUMNS)
        for note in data()["notes"]:
            for r in note["rows"]:
                vals = [r[k] for k in ("our", "published", "source", "gap", "reason")]
                self.assertTrue(all(v.strip() for v in vals), r["our"])
                self.assertGreater(len(r["reason"]), 30, r["our"])
                self.assertTrue("https://" in r["source"] or r["source"] == "the same", r["our"])
                for v in vals:
                    self.assertNotIn("|", v, r["our"])

    def test_the_review_holds_the_same_rows(self):
        md = text()
        for note in data()["notes"]:
            head = f"### {note['note']}.md, for {note['page']}"
            lines = section(md, head)
            body = [cells(ln) for ln in lines if ln.startswith("| ") and not ln.startswith("| Our figure")]
            hdr = [cells(ln) for ln in lines if ln.startswith("| Our figure")]
            self.assertEqual(hdr, [COLUMNS], head)
            self.assertEqual(len(body), len(note["rows"]), head)
            for row, r in zip(body, note["rows"]):
                self.assertEqual(row, [r[k] for k in ("our", "published", "source", "gap", "reason")])
            self.assertEqual(note["count_after"], note["count_now"] + len(note["rows"]))
            self.assertIn(f"goes from {note['count_now']} to {note['count_after']}", md)

    def test_counts_now_match_the_pages(self):
        # session 461: once the rows land (sessions 462 to 464) the line moves and the count grows; the page holds one
        # count, never fewer than the review found on 21 October (check-cross-checks.mjs proves it equals the note's rows)
        for note in data()["notes"]:
            path, _ = note["count_line"].rsplit(":", 1)
            with open(os.path.join(ROOT, path), encoding="utf-8") as f:
                found = re.findall(r'data-checked-against="(\d+)"', f.read())
            self.assertEqual(len(found), 1, path)
            self.assertGreaterEqual(int(found[0]), note["count_now"], path)


if __name__ == "__main__":
    unittest.main()
