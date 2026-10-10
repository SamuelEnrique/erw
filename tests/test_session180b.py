"""Session 180b: the second pull for the map's boundary file (HIFLD's "Control Areas" layer), which reached no file.

What is held to: the request step keeps an answer's headers beside it, without cookies, and writes the content type
into the log's note, so an answer that is not a file can be reported exactly as it came; a host that answers 401 or
403 to the request for its robots file is not asked anything else (the standard library's reading of such an answer);
the Method note holds the six requests and their answers word for word; nothing is shipped and nothing is registered
that the pull did not reach (tests/test_session180.py holds the file and its registry row together).
No request and no model call is made here: the one answer read comes from a file on this machine, through a file
address. The environment is read, never set.
"""
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_ba_boundaries as BA  # noqa: E402

EM = chr(0x2014)
TMP = None


def setUpModule():
    global TMP
    TMP = tempfile.mkdtemp(prefix="erw180b_")


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheAnswerIsKeptAsItCame(unittest.TestCase):
    def test_the_headers_are_kept_beside_the_answer_and_the_content_type_is_in_the_log(self):
        answer = os.path.join(TMP, "answer.json")
        with open(answer, "w", encoding="utf-8", newline="\n") as f:
            f.write('{"error":"Site does not exist"}')
        pull = os.path.join(TMP, "pull_headers")
        row = BA.get(pathlib.Path(answer).as_uri(), "kept.json", pull, 10, 10**6)   # a file address: no network
        self.assertEqual(row["bytes"], 31)
        self.assertIn("Content-Type: application/json", row["note"])
        kept = os.path.join(pull, "01_kept", "kept.json")
        with open(kept, encoding="utf-8") as f:
            self.assertEqual(f.read(), '{"error":"Site does not exist"}')
        with open(kept + ".headers.txt", encoding="utf-8") as f:
            head = f.read()
        self.assertTrue(head.startswith("status: "))
        self.assertIn("application/json", head)
        self.assertEqual(BA.read_log(pull)[0]["saved_as"], "01_kept/kept.json")

    def test_cookies_are_not_kept(self):
        code = src("warehouse", "connectors", "eia_ba_boundaries.py")
        self.assertIn('if k.lower() != "set-cookie":', code)


class ARobotsFileThatWasRefused(unittest.TestCase):
    def pull(self, name, status):
        d = os.path.join(TMP, name)
        os.makedirs(os.path.join(d, "01_robots"))
        with open(os.path.join(d, "01_robots", "robots.txt"), "w", encoding="utf-8") as f:
            f.write("Invalid URL")   # the refusal's body: parsed as rules it would allow every path
        BA.write_log(d, [{"n": 1, "url": "https://example.org/robots.txt", "status": status, "bytes": 11, "seconds": "0.1",
                          "retrieved_utc": "2026-10-10T00:00:00Z", "sha256": "", "saved_as": "01_robots/robots.txt", "note": ""}])
        return d

    def test_a_403_or_401_on_the_robots_file_stops_every_later_request(self):
        for status in ("403", "401"):
            d = self.pull("refused_" + status, status)
            robots = os.path.join(d, "01_robots", "robots.txt")
            self.assertTrue(BA.robots_allows(robots, "https://example.org/arcgis/rest/services"))   # why the status is read
            self.assertEqual(BA.robots_status(d, robots), status)
            with self.assertRaises(SystemExit) as e:
                BA.get("https://example.org/arcgis/rest/services", "x.json", d, 10, 10**6, robots=robots)
            self.assertIn(f"answered {status}", str(e.exception))
            self.assertIn("No request made", str(e.exception))
            self.assertEqual(len(BA.read_log(d)), 1)   # nothing was sent, nothing was logged

    def test_a_robots_file_that_is_not_in_the_log_has_no_status(self):
        d = self.pull("other", "200")
        self.assertEqual(BA.robots_status(d, os.path.join(TMP, "elsewhere.txt")), "")
        self.assertEqual(BA.robots_status(d, os.path.join(d, "01_robots", "robots.txt")), "200")


class WhatTheSecondPullReached(unittest.TestCase):
    def test_the_method_note_holds_the_six_requests_and_their_answers(self):
        note = src("docs", "methods", "grid_network.md")
        for words in ("**The second pull (session 180b, 10 October 2026)",
                      "`https://hifld-geoplatform.hub.arcgis.com/robots.txt`",
                      '`{"error":"CONT_0001: Item does not exist or is inaccessible."}`',
                      '`{"message":"CONT_0001: Item does not exist or is inaccessible.","statusCode":400}`',
                      "`https://services1.arcgis.com/robots.txt`", "403, 11 bytes", "`Invalid URL`",
                      '`{"error":"Site does not exist"}`', "`Not Found. Redirecting to /404`",
                      "Six requests and 382 bytes against a ceiling of ten and 300 MB",
                      "No license words are quoted for the layer", "a ruling for the owner"):
            self.assertIn(words, note)
        # session 180's own account stays whole
        for words in ("## The map (session 180)", "The boundary file is not yet held", "Five requests and 658,303 bytes"):
            self.assertIn(words, note)

    def test_the_page_names_no_boundary_source_it_does_not_hold(self):
        if os.path.exists(os.path.join(ROOT, "site", "public", "network", "ba_boundaries.json")):
            self.skipTest("a boundary file is held: tests/test_session180.py holds it to its registry row")
        page = src("site", "app", "network", "page.tsx")
        self.assertNotIn("HIFLD", page)
        self.assertNotIn("Control Areas", page)
        self.assertNotIn("HIFLD", src("warehouse", "metadata", "sources.csv"))

    def test_the_page_stays_in_review(self):
        self.assertIn('"/network": "review"', src("site", "lib", "release.ts"))

    def test_no_em_dash(self):
        for parts in (("warehouse", "connectors", "eia_ba_boundaries.py"), ("docs", "methods", "grid_network.md"), ("tests", "test_session180b.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        report = os.path.join(ROOT, "archive", "sessions", "SESSION_180B_REPORT.md")
        if os.path.exists(report):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_180B_REPORT.md"))


if __name__ == "__main__":
    unittest.main()
