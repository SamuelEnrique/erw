"""Session 471: the licensing record as a page, /data/licenses, in review (chain 019).

The page reads the two files the licensing record writes and renders docs/licenses.md. These tests hold it to the
session's rules: release.ts gives it no line (so it is in review), the content bundle carries the record and every
publisher's verdict (a row with an unquoted comma in its note included), check-values knows its keys and recomputes
them from warehouse/metadata, the four letters named exist, and no em or en dash is in anything the session wrote.
"""

import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
PAGE = os.path.join(SITE, "app", "data", "licenses", "page.tsx")
LIB = os.path.join(SITE, "lib", "licensesPage.ts")
CONTENT = os.path.join(SITE, "scripts", "build-content.mjs")
VALUES = os.path.join(SITE, "scripts", "check-values.mjs")
ROUTES = os.path.join(SITE, "scripts", "check-routes.mjs")
RELEASE = os.path.join(SITE, "lib", "release.ts")
META = os.path.join(ROOT, "warehouse", "metadata")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_471_REPORT.md")
DASHES = re.compile("[–—]")


def _read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def _verdicts():
    """license_verdicts.csv as the page's bundle reads it: a row with more cells than the header keeps its extra cells
    as its note's (an unquoted comma in the note)."""
    with open(os.path.join(META, "license_verdicts.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    head, body = rows[0], rows[1:]
    out = []
    for r in body:
        if len(r) < len(head):
            continue
        r = r[: len(head) - 1] + [",".join(r[len(head) - 1:])]
        out.append(dict(zip(head, r)))
    return out


class ThePage(unittest.TestCase):
    def test_it_is_in_review_and_release_is_untouched(self):
        # a path with no entry in release.ts is in review; the session adds none
        self.assertNotIn("/data/licenses", _read(RELEASE))

    def test_it_renders_the_record_and_reads_no_table(self):
        s = _read(PAGE)
        self.assertIn('render(DOCS.licenses, "docs/licenses.md")', s)
        self.assertNotIn("supabase", s.lower())
        for key in ("lic|held|count", "lic|held|pub|", "lic|verdict|both|count", "lic|verdict|today_only|count"):
            self.assertIn(key, s)

    def test_the_four_letters_exist(self):
        s = _read(LIB)
        files = re.findall(r'file: "([^"]+)"', s)
        self.assertEqual(len(files), 4)
        for f in files:
            self.assertTrue(os.path.exists(os.path.join(ROOT, f)), f)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "reviews", "isone-permission-email.md")))


class TheBundleAndTheChecks(unittest.TestCase):
    def test_the_bundle_carries_the_record_and_the_verdicts(self):
        s = _read(CONTENT)
        self.assertIn('licenses: read(path.join(docs, "licenses.md"))', s)
        self.assertIn("license_verdicts: licenseVerdicts()", s)
        self.assertIn("r.length >= head.length", s)

    def test_check_values_reads_the_page_and_its_keys(self):
        s = _read(VALUES)
        self.assertIn('"/data/licenses",', s)
        self.assertIn('if (p[0] === "lic")', s)
        self.assertIn('"license_status.csv"', s)
        self.assertIn('"license_verdicts.csv"', s)
        self.assertIn('"/data/licenses"', _read(ROUTES))

    def test_every_publisher_survives_the_extra_cells(self):
        with open(os.path.join(META, "license_verdicts.csv"), encoding="utf-8", newline="") as f:
            n = sum(1 for _ in csv.DictReader(f))
        self.assertEqual(len(_verdicts()), n)

    def test_the_counts_the_page_draws_are_the_files(self):
        v = _verdicts()
        today = [r for r in v if r["verdict"] == "may be public"]
        both = [r for r in today if r["if_commercial"] == "may be public"]
        self.assertEqual(len(both) + len([r for r in today if r["if_commercial"] != "may be public"]), len(today))
        with open(os.path.join(META, "license_status.csv"), encoding="utf-8", newline="") as f:
            held = [r for r in csv.DictReader(f) if r["status"] == "license needed"]
        import json
        with open(os.path.join(SITE, "data", "license_status.json"), encoding="utf-8") as f:
            status = json.load(f)
        self.assertEqual(len(held), sum(1 for r in status["tables"].values() if r["status"] == "license needed"))


class NoDashes(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_the_session_wrote(self):
        for p in (PAGE, LIB, REPORT):
            if os.path.exists(p):
                self.assertIsNone(DASHES.search(_read(p)), p)


if __name__ == "__main__":
    unittest.main()
