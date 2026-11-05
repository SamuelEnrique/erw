"""Session 421 (chain 021, on portable-laptop): security M4, the report-only policy.

What is held to:
  check-csp.mjs opens, beside the release list, the four pages and views chain 019 added in review (/data/licenses,
    /deals?view=comparables, /datacenters?view=grids, /policy?tag=loads_interconnection_tariffs), each an address the
    site has (a page folder under site/app, the view's own key in its page);
  next.config.ts still sends the report-only header beside the enforced one: docs/security.md's M4 says it goes on or
    after 26 October 2026; the drop is a person's (an unattended edit removing it was refused on this machine);
  docs/security.md's M4 line names session 421 and that the drop waits for 26 October;
  no em or en dash in any file the session wrote."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DASHES = (chr(0x2014), chr(0x2013))
FILES = ["tests/test_session421.py", "archive/sessions/SESSION_421_REPORT.md"]
KEYS = {"/deals": "site/app/deals/page.tsx", "/datacenters": "site/app/datacenters/page.tsx", "/policy": "site/lib/policyweek.ts"}
VIEWS = ["/data/licenses", "/deals?view=comparables", "/datacenters?view=grids", "/policy?tag=loads_interconnection_tariffs"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheViews(unittest.TestCase):
    def test_check_csp_opens_the_four_views(self):
        csp = src("site", "scripts", "check-csp.mjs")
        m = re.search(r"const VIEWS = \[(.*?)\];", csp)
        self.assertIsNotNone(m)
        self.assertEqual(re.findall(r'"([^"]+)"', m.group(1)), VIEWS)
        self.assertIn("[...Object.keys(RELEASE), ...VIEWS,", csp)

    def test_each_view_is_an_address_the_site_has(self):
        for v in VIEWS:
            path, _, query = v.partition("?")
            page = os.path.join(ROOT, "site", "app", *path.strip("/").split("/"), "page.tsx")
            self.assertTrue(os.path.exists(page), page)
            if query:
                value = query.split("=", 1)[1]
                where = KEYS[path]
                self.assertIn(value, src(*where.split("/")), v)


class TheHeaderWaits(unittest.TestCase):
    def test_the_report_only_header_is_still_sent(self):
        c = src("site", "next.config.ts")
        self.assertIn('{ key: "Content-Security-Policy-Report-Only", value: CSP_REPORT_ONLY },', c)
        self.assertIn("const CSP_ENFORCED = CSP_FULL;", c)

    def test_m4_names_this_session_and_the_day(self):
        line = next(l for l in src("docs", "security.md").splitlines() if l.startswith("| M4 |"))
        self.assertIn("session 421", line.lower())
        self.assertNotIn("PROOF_421", line)
        self.assertIn("26 October 2026", line)
        self.assertIn("a person's", line)


class Words(unittest.TestCase):
    def test_no_dash(self):
        for f in FILES:
            if os.path.exists(os.path.join(ROOT, f)):
                t = src(f)
                for d in DASHES:
                    self.assertNotIn(d, t, f)


if __name__ == "__main__":
    unittest.main()
