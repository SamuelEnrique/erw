"""Audit of the Digest and the Roundup, finding 2 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): a
weekend day's page, /digest/<Saturday or Sunday>, said the day's stories "open ERW's Roundup for <week> ... (not written
yet ...)" whatever the date, so on 26 November 2026 the weekend days of W46 and W47 promised Roundups whose Sundays had
passed and that were never written. The words follow the date now: a week whose Sunday 23:00 UTC has passed with no
Roundup is said to have none.

1. lib/digest.ts roundupDue at the edges (Node with the site's loaders). Fails on main (no such function).
2. The page says "No Roundup was written for" a due week. Fails on main."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AWeekWithNoRoundupIsSaidSo(unittest.TestCase):
    def test_the_page_says_no_roundup_was_written(self):
        page = src("site", "app", "digest", "[date]", "page.tsx")
        self.assertIn("roundupDue(week)", page)
        self.assertIn("No Roundup was written for {week}, the week that holds this", page)

    @unittest.skipUnless(NODE, "node is not installed")
    @unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
    def test_due_from_the_weeks_sunday_at_23_utc(self):
        r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/test-audit-digest-2.mjs"], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(out, {"w47_on_26_nov": True, "w46_on_26_nov": True, "w48_on_26_nov": False, "w47_before": False,
                               "w47_at": True, "w01_2027_before": False, "w01_2027_at": True, "w53_2026_at": True,
                               "not_a_week": False})


if __name__ == "__main__":
    unittest.main()
