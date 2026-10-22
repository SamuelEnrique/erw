"""Session 581 (the chain of 22 October 2026, night, 034, code machine): every internal link and anchor resolves.
site/scripts/check-links.mjs reads every page of check-values' list and every method page in the internal view, in a
real browser, and lists each internal link that answers other than 200 (or through a redirect, or with the in-review
page) and each fragment the page it names does not hold. Its test, site/scripts/test-check-links.mjs, judges a fixture
site served in its own process (no browser here: the suite stays light; CHECK_LINKS_BROWSER_TEST=1 adds the browser
part). Energy Research Warehouse (ERW)."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
NEW = [("site", "scripts", "check-links.mjs"), ("site", "scripts", "test-check-links.mjs"), ("tests", "test_session581.py")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TestCheckLinks(unittest.TestCase):
    def test_no_dashes(self):
        for parts in NEW:
            text = src(*parts)
            for d in DASHES:
                self.assertNotIn(d, text, f"{'/'.join(parts)} holds a dash")

    def test_reads_check_values_list_and_methods(self):
        t = src("site", "scripts", "check-links.mjs")
        self.assertIn('"check-values.mjs"), "--list"]', t)
        self.assertIn("listed.internal", t)
        self.assertIn("/data/methods/", t)
        self.assertIn("content", t)

    def test_internal_view_and_no_usage(self):
        t = src("site", "scripts", "check-links.mjs")
        self.assertIn("unlockPost(base, token)", t)
        self.assertIn("h.unlock(base)", t)
        self.assertIn('"*/api/usage*"', t)
        self.assertIn('"*/api/ask*"', t)
        self.assertIn('"x-erw-check": "1"', t)
        self.assertNotIn("?token=", t)

    def test_waits_are_not_failures(self):
        t = src("site", "scripts", "check-links.mjs")
        self.assertIn('filter((f) => f.kind !== "waits" && f.kind !== "alias")', t)
        self.assertIn('address.startsWith("/api/")', t)
        self.assertIn('{ href: "/data/methods/price_board_v4", why:', t)

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_fixture(self):
        env = {k: v for k, v in os.environ.items() if k != "CHECK_LINKS_BROWSER_TEST"}
        r = subprocess.run([NODE, os.path.join("scripts", "test-check-links.mjs")], cwd=SITE, capture_output=True, text=True,
                           encoding="utf-8", env=env, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        m = re.search(r"test-check-links: (\d+) of (\d+) pass", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 20, r.stdout[-500:])


if __name__ == "__main__":
    unittest.main()
