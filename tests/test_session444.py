"""Session 444: the weekly Roundup, read as its most demanding reader (the chain of 21 October 2026).

Energy Research Warehouse (ERW). docs/reviews/roundup-audit-2026-10-21.md audits every Roundup issue the repository
holds (docs/roundup/2026-W*.md and the saved emails in docs/digest/email/), traces each figure to its table, checks every
link under a ceiling of 150 requests, and ranks fixes for the code machine.

What is held here: no em or en dash in what the session wrote; every Roundup page and saved Roundup email in the
repository is named in the audit; every path the audit names in backticks exists (but for the named exceptions: a draft
on another branch, the Digest audit written in parallel, and runs/, which git ignores); every ranked fix names a file
that exists; the W39 figures the audit calls equal are the figures the W39 page prints; and the link log, when this
machine holds it, stays within its ceiling and agrees with the audit's count.
Nothing here writes a file or makes a request.
"""

import csv
import glob
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "roundup-audit-2026-10-21.md")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_444_REPORT.md")
WRITTEN = [DOC, REPORT, os.path.abspath(__file__)]
LINKS = os.path.join(ROOT, "runs", "chain_oct21_third", "s444", "links.csv")
# named in the audit, not on this branch's tree: the findings hunt's draft (wip/findings-oct20) and session 442's file
ELSEWHERE = {"docs/roundup/drafts/2026-W43.md", "docs/reviews/digest-audit-2026-10-21.md"}
CEILING = 150


def text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def named_paths(s):
    """Every backticked token that looks like a repository path (holds a slash and starts with a top folder)."""
    out = set()
    for tok in re.findall(r"`([^`\s]+)`", s):
        tok = tok.rstrip(".,;:")
        if "/" in tok and re.match(r"^(docs|warehouse|site|tests|archive|scripts|queue|package|runs|\.github)/", tok):
            out.add(tok.split("*")[0].rstrip("/") if "*" in tok else tok)
    return out


class TestSession444(unittest.TestCase):
    def test_no_dashes(self):
        for p in WRITTEN:
            if os.path.exists(p):
                s = text(p)
                self.assertNotIn(chr(0x2014), s, p)
                self.assertNotIn(chr(0x2013), s, p)

    def test_every_issue_named(self):
        s = text(DOC)
        # session 2777: the audit is dated; it names every issue to 2026-W43 (its added section), not the Sundays after it
        pages = [os.path.relpath(p, ROOT).replace(os.sep, "/") for p in glob.glob(os.path.join(ROOT, "docs", "roundup", "2026-W*.md"))
                 if os.path.basename(p)[:8] <= "2026-W43"]
        self.assertTrue(pages)
        for p in pages:
            self.assertIn(f"`{p}`", s, p)
        for p in glob.glob(os.path.join(ROOT, "docs", "digest", "email", "*-roundup.txt")):
            if os.path.basename(p)[:8] > "2026-W43":
                continue
            stem = os.path.basename(p)[:-len(".txt")]
            self.assertIn(stem, s, p)

    def test_named_paths_exist(self):
        missing = []
        for tok in sorted(named_paths(text(DOC))):
            if tok in ELSEWHERE or tok.startswith("runs/") or "<" in tok:  # a pattern such as docs/roundup/<week>.md
                continue
            base = tok.split(".*")[0]
            if not (os.path.exists(os.path.join(ROOT, tok)) or glob.glob(os.path.join(ROOT, base + "*"))):
                missing.append(tok)
        self.assertEqual(missing, [])

    def test_every_fix_names_a_file(self):
        s = text(DOC)
        sec = s.split("## Fixes for the code machine, ranked", 1)[1].split("\n## ", 1)[0]
        fixes = re.findall(r"^\d+\. \*\*.+$", sec, re.M)
        self.assertGreaterEqual(len(fixes), 10)
        for f in fixes:
            files = [t for t in named_paths(f) if not t.startswith("runs/")]
            if f.startswith("13."):  # the trace on a current machine: its script is under runs/ by design
                self.assertIn("runs/chain_oct21_third/s444/trace.py", f)
                continue
            self.assertTrue(files, f[:80])
            self.assertTrue(any(os.path.exists(os.path.join(ROOT, t)) for t in files), f[:80])
            self.assertIn("Test:", f, f[:80])

    def test_w39_figures_are_the_page_s(self):
        page = text(os.path.join(ROOT, "docs", "roundup", "2026-W39.md"))
        for v in ("41.84", "39.90", "36.84", "36.79", "39.36", "45.97", "40.45", "75.37", "33.96", "46.44", "36.12",
                  "44.30", "521.36", "2.90", "2.97", "96.41", "101.44", "114.89", "119.66", "608,317", "29.01", "30.11",
                  "50.09", "28.08"):
            self.assertIn(v, page, v)
            self.assertIn(v, text(DOC), v)

    def test_link_log_within_ceiling(self):
        if not os.path.exists(LINKS):
            self.skipTest("runs/ is not in git: the link log is on portable-laptop only")
        with open(LINKS, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        made = [r for r in rows if r["n"]]
        self.assertLessEqual(len(made), CEILING)
        self.assertEqual([int(r["n"]) for r in made], list(range(1, len(made) + 1)))
        self.assertIn(f"**{len(made)} requests of the ceiling of {CEILING}**", text(DOC))
        self.assertFalse([r for r in made if re.search(r"misoenergy\.org|scc\.virginia\.gov", r["url"], re.I)])
        self.assertTrue(all(r["note"] for r in rows if not r["n"]))


if __name__ == "__main__":
    unittest.main()
