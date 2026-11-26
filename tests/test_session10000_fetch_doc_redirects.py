"""Session 10000 (chain 701): the large-load research reader checks a redirect's target before following it.

Data request 27 of docs/state/data_requests_five_tools.md: the reader followed assets.senate.mn to assets.mnsenate.gov
and read the page before that host's robots file. CheckedRedirect now asks the barred list and the target's robots
file first. No request is made here: the checks are replaced by stand-ins."""
import importlib.util
import os
import unittest
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("fetch_doc_t", os.path.join(ROOT, "docs", "research", "large_load", "fetch_doc.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheRedirectIsCheckedFirst(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.req = urllib.request.Request("https://a.example.org/doc", headers={"User-Agent": "t"})

    def test_a_disallowed_target_is_refused(self):
        self.m.refused = lambda host: None
        self.m.robots_verdict = lambda url: (False, "robots.txt 200: DISALLOWED")
        h = self.m.CheckedRedirect()
        with self.assertRaises(self.m.RedirectRefused) as cm:
            h.redirect_request(self.req, None, 302, "Found", {}, "https://b.example.org/doc")
        self.assertIn("b.example.org", str(cm.exception))
        self.assertEqual(h.followed, [])

    def test_a_barred_host_is_refused_before_its_robots_file_is_asked(self):
        asked = []
        self.m.refused = lambda host: "barred: terms" if host.endswith("b.example.org") else None
        self.m.robots_verdict = lambda url: asked.append(url) or (True, "allowed")
        with self.assertRaises(self.m.RedirectRefused):
            self.m.CheckedRedirect().redirect_request(self.req, None, 301, "Moved", {}, "https://b.example.org/doc")
        self.assertEqual(asked, [])

    def test_an_allowed_target_is_followed_and_recorded(self):
        self.m.refused = lambda host: None
        self.m.robots_verdict = lambda url: (True, "robots.txt answered 404: no robots file, allowed")
        h = self.m.CheckedRedirect()
        new = h.redirect_request(self.req, None, 302, "Found", {}, "https://b.example.org/doc")
        self.assertEqual(new.full_url, "https://b.example.org/doc")
        self.assertEqual(h.followed, [{"to": "https://b.example.org/doc", "code": 302,
                                       "robots": "robots.txt answered 404: no robots file, allowed"}])
        self.assertEqual(h.max_redirections, 5)

    def test_fetch_uses_the_checked_opener(self):
        with open(os.path.join(ROOT, "docs", "research", "large_load", "fetch_doc.py"), encoding="utf-8") as f:
            s = f.read()
        body = s[s.index("def fetch(url: str)"):]
        self.assertIn("resp, redirects = get_checked(url)", body)
        self.assertNotIn("with get(url) as r:", body)


if __name__ == "__main__":
    unittest.main()
