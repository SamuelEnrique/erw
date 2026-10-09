"""Session 171: Virginia's public record for the PJM hole, and the commission's robots file that forbids it.

What is tested, with no request and no model call:
  the connector   Virginia's own ceilings (150 requests, 500 MB, one request every 2.5 seconds) sit in front of each
                  request (Budget.ask refuses before the request); the robots reader (robots_forbids) reads the
                  commission's file as it was saved on 9 October 2026 and finds "User-agent: *" "Disallow: /" over every
                  path the stage asks under; the stage (do_virginia) stops after the robots file and sends nothing more,
                  and, with a permitting robots file, stops at a policy sentence that speaks of automated access; the
                  contact string is the ruled one and no address of a person is anywhere in the connector
  the table       where the table and the raw store are on this machine (ERW_WAITS_TABLE, ERW_RAW_ROOT, or this
                  copy's warehouse): the 2,622 rows session 165 wrote come out byte for byte (a hash over the rows, which
                  names no request); exactly one request to the commission in requests.csv, and the robots file saved
                  with its hash in captures.csv
  how soon        the builder places Dominion under PJM's grid (ENTITY_GRID, STATED_GROUPS, PLACES); the site file's
                  PJM block is "not measured yet", Virginia, with Dominion's own expectations only; the builder's name
                  check refuses a shown entity's request name and lets a hidden entity's name that is a document's own
                  words pass (the rule session 171 wrote)
  the documents   the method note quotes the robots file's two lines and the policy's three sentences; the accelerator
                  page and the method note hold no em dash and no DocID's file name of the sixteen filings

The module reads the environment and never sets it. It skips cleanly on a machine without the tables."""

import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import large_load_waits as w  # noqa: E402
import how_soon as hs  # noqa: E402

EM_DASH = chr(0x2014)
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"
# the 2,622 rows of the table as session 165 wrote them (8 and 9 October 2026): the sha256 of the data lines in the
# table's order, each with its line end, the header lines and the column line aside. A hash names no request.
ROWS_165 = 2622
SHA256_165 = "d01309c6abe39774a785626805fe8baaac5f59b73fcbcba964c4e3ff76e3f685"
ROBOTS_SHA256 = "33f96f5c9080365c333c66b98064d269cff79840a057c3964bdb2cf5879a7338"
# the commission's robots file as saved on 9 October 2026 (vascc/20261009074426_robots.txt): its own words
ROBOTS_VA = """User-agent: Terminalfour Nutch Spider
Crawl-delay: 0.5
Disallow: /BFI-Complaint-Response
Disallow: /notfound

User-Agent: googlebot
Allow: /

User-Agent: bingbot
Allow: /

Sitemap: https://www.scc.virginia.gov/sitemap-en.xml

User-agent: *
Disallow: /
"""
POLICY_QUOTES = [
    "Information on the SCC website is public and should not be used for commercial purposes beyond its intended public availability.",
    "Permission is granted to make fair use of the contents of the SCC website.",
    "Attribution of the source of the information is encouraged.",
]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw_root():
    for d in (os.environ.get("ERW_RAW_ROOT"), os.path.join(ROOT, "warehouse", "raw")):
        if d and os.path.exists(os.path.join(d, "large_load_waits", "captures.csv")):
            return d
    return ""


def table_path():
    for p in (os.environ.get("ERW_WAITS_TABLE"), os.path.join(ROOT, "warehouse", "output", "large_load_waits.csv")):
        if p and os.path.exists(p):
            return p
    return ""


class FakeNet:
    """Answers in order; records every address asked. No request is made."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.asked = []

    def get(self, url, kind, rows_reserve=0, timeout=120):
        self.asked.append((url, kind))
        if not self.answers:
            raise AssertionError(f"a request past the stop: {url}")
        status, body = self.answers.pop(0)
        return status, body, {}


class TheCeilings(unittest.TestCase):
    def test_the_owners_ceilings_and_pace(self):
        self.assertEqual(w.VA_CEILING_REQUESTS, 150)
        self.assertEqual(w.VA_CEILING_BYTES, 500 * 1024 ** 2)
        self.assertEqual(w.VA_PAUSE, 2.5)
        self.assertEqual(w.VA_CASE, "PUR-2026-00011")
        self.assertEqual(w.CONTACT, CONTACT)
        self.assertEqual(w.UA, {"User-Agent": CONTACT})
        self.assertIn("misoenergy.org", w.NEVER)
        self.assertIn("pjm.com", w.NEVER)
        self.assertTrue(all(isinstance(d, int) for d in w.VA_DOCIDS))
        self.assertEqual(len(w.VA_DOCIDS), 16)

    def test_no_address_of_a_person_in_the_connector(self):
        text = src("warehouse", "connectors", "large_load_waits.py")
        self.assertNotRegex(text, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        self.assertNotIn(EM_DASH, text)

    def _raw(self, d, n_requests, n_bytes):
        with open(os.path.join(d, "requests.csv"), "w", encoding="utf-8", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=w.REQUEST_COLS, lineterminator="\n")
            wr.writeheader()
            for i in range(n_requests):
                wr.writerow(dict(at="2026-10-09T07:00:00Z", kind="document", host="www.scc.virginia.gov", url=f"https://www.scc.virginia.gov/docketsearch/DOCS/{i}!.PDF",
                                 status="200", bytes=n_bytes // n_requests if n_requests else 0, note=""))
            wr.writerow(dict(at="2026-10-09T07:00:00Z", kind="capture", host="web.archive.org", url="https://web.archive.org/x", status="200", bytes=10, note=""))

    def test_the_stop_sits_before_the_request(self):
        with tempfile.TemporaryDirectory() as d:
            self._raw(d, 149, 1000)
            b = w.Budget(d)
            self.assertEqual(b.va, {"requests": 149, "bytes": 1000 - 1000 % 149})
            self.assertEqual(b.requests, 150)   # the Archive's row counts in the whole, not in Virginia's
            b.ask(w.VA_ROBOTS, "robots file")
            b.spend(w.VA_ROBOTS, "robots file", "200", 707)
            self.assertEqual(b.va["requests"], 150)
            with self.assertRaises(w.Refused) as cm:
                b.ask(w.VA_TERMS, "terms page")
            self.assertIn("151", str(cm.exception))
            self.assertIn("150", str(cm.exception))
        with tempfile.TemporaryDirectory() as d:
            self._raw(d, 10, w.VA_CEILING_BYTES - w.VA_BYTES_RESERVE + 10)
            with self.assertRaises(w.Refused) as cm:
                w.Budget(d).ask(w.VA_DOC.format(f="x!.PDF"), "document")
            self.assertIn("bytes", str(cm.exception))
        with tempfile.TemporaryDirectory() as d:
            self._raw(d, 10, 1000)
            room = w.Budget(d).ask(w.VA_DOC.format(f="x!.PDF"), "document")
            self.assertEqual(room, w.VA_BYTES_RESERVE)

    def test_the_pause_by_host(self):
        self.assertIs(w.VA_PAUSE, w.VA_PAUSE)
        line = [ln for ln in src("warehouse", "connectors", "large_load_waits.py").splitlines() if "pause = ARCHIVE_PAUSE if" in ln][0]
        self.assertIn("VA_PAUSE if host.endswith(VA_HOST)", line)


class TheRobotsFile(unittest.TestCase):
    def test_the_commissions_file_forbids_every_path_for_every_agent_it_does_not_name(self):
        bad = w.robots_forbids(ROBOTS_VA, w.VA_PATHS)
        self.assertEqual(len(bad), len(w.VA_PATHS))
        self.assertTrue(all(agents == "*" and rule == "/" for agents, rule in bad))

    def test_a_named_agents_rules_are_not_ours(self):
        self.assertEqual(w.robots_forbids("User-agent: googlebot\nDisallow: /\n", w.VA_PATHS), [])
        self.assertEqual(w.robots_forbids("User-agent: Terminalfour Nutch Spider\nDisallow: /docketsearch/\n", w.VA_PATHS), [])

    def test_a_file_that_allows(self):
        self.assertEqual(w.robots_forbids("User-agent: *\nDisallow: /private/\nDisallow:\n", w.VA_PATHS), [])
        self.assertEqual(w.robots_forbids("", w.VA_PATHS), [])

    def test_prefixes_wildcards_and_anchors(self):
        self.assertEqual(w.robots_forbids("User-agent: *\nDisallow: /docketsearch\n", w.VA_PATHS), [("*", "/docketsearch")] * 2)
        self.assertEqual(w.robots_forbids("User-agent: *\nDisallow: /*api/\n", w.VA_PATHS), [("*", "/*api/")])
        self.assertEqual(w.robots_forbids("User-agent: *\nDisallow: /docketsearch$\n", w.VA_PATHS), [])
        self.assertEqual(w.robots_forbids("User-agent: *\nDisallow: /robots.txt$\n", w.VA_PATHS), [("*", "/robots.txt$")])

    def test_two_agents_in_one_group(self):
        self.assertEqual(w.robots_forbids("User-agent: bingbot\nUser-agent: *\nDisallow: /docketsearch/\n", w.VA_PATHS), [("bingbot, *", "/docketsearch/")])


class TheStage(unittest.TestCase):
    def _log(self):
        lines = []
        return lines, lines.append

    def test_it_stops_after_the_commissions_robots_file(self):
        with tempfile.TemporaryDirectory() as d:
            net = FakeNet([("200", ROBOTS_VA.encode())])
            lines, log = self._log()
            got = w.do_virginia(d, net, log)
            self.assertEqual(got["stopped"], "robots")
            self.assertEqual(net.asked, [(w.VA_ROBOTS, "robots file")])
            caps = w.read_captures(d)
            self.assertEqual(len(caps), 1)
            self.assertEqual((caps[0]["publisher"], caps[0]["original"], caps[0]["status"]), ("vascc", w.VA_ROBOTS, "200"))
            self.assertEqual(caps[0]["sha256"], hashlib.sha256(ROBOTS_VA.encode()).hexdigest())
            self.assertTrue(os.path.exists(os.path.join(d, caps[0]["file"])))
            self.assertTrue(any("Disallow: /" in ln and "nothing more is sent" in ln for ln in lines))

    def test_a_robots_file_that_cannot_be_read_is_not_permission(self):
        with tempfile.TemporaryDirectory() as d:
            net = FakeNet([("503", b"")])
            got = w.do_virginia(d, net, lambda m: None)
            self.assertEqual(got["stopped"], "robots unreadable")
            self.assertEqual(len(net.asked), 1)

    def test_with_a_permitting_robots_file_the_policy_is_read_next_and_a_sentence_on_automated_access_stops_it(self):
        policy = b"<html><body><p>" + " ".join(POLICY_QUOTES).encode() + b" Automated harvesting of this site is not permitted.</p></body></html>"
        with tempfile.TemporaryDirectory() as d:
            net = FakeNet([("200", b"User-agent: *\nDisallow: /private/\n"), ("200", policy)])
            lines, log = self._log()
            got = w.do_virginia(d, net, log)
            self.assertEqual(got["stopped"], "terms")
            self.assertEqual([u for u, _ in net.asked], [w.VA_ROBOTS, w.VA_TERMS])
            self.assertTrue(any("found word for word" in ln for ln in lines))
            self.assertTrue(any("Automated harvesting" in ln for ln in lines))
            caps = w.read_captures(d)
            self.assertEqual([c["publisher"] for c in caps], ["vascc", "terms"])
            self.assertTrue(caps[1]["file"].startswith("terms/"))

    def test_with_a_permitting_robots_file_and_a_silent_policy_the_list_is_read_and_the_filings_follow(self):
        policy = b"<html><body><p>" + " ".join(POLICY_QUOTES).encode() + b"</p></body></html>"
        listing = json.dumps([{"DocID": 1, "FileName": "8a!.PDF", "Document_Name": "Virginia Electric and Power Company - Application", "Date_Filed": "2026-02-02T00:00:00"},
                              {"DocID": 2, "FileName": "8b!.PDF", "Document_Name": "Someone - Notice of Participation", "Date_Filed": "2026-02-03T00:00:00"}]).encode()
        with tempfile.TemporaryDirectory() as d:
            net = FakeNet([("200", b"User-agent: *\nDisallow: /private/\n"), ("200", policy), ("200", listing), ("200", b"%PDF-1.4 made up")])
            got = w.do_virginia(d, net, lambda m: None, docids=(1, 9))
            self.assertEqual(got["stopped"], "")
            self.assertEqual(got["documents"], 2)
            self.assertEqual(got["missing"], [9])
            self.assertEqual([u for u, _ in net.asked], [w.VA_ROBOTS, w.VA_TERMS, w.VA_DOCS_LIST, w.VA_DOC.format(f="8a!.PDF")])
            caps = w.read_captures(d)
            self.assertEqual([c["publisher"] for c in caps], ["vascc", "terms", "vascc", "vascc"])
            self.assertIn("DocID 1", caps[-1]["note"])
            # asked again, the filing already held is not asked for
            net2 = FakeNet([("200", b"User-agent: *\nDisallow: /private/\n"), ("200", policy), ("200", listing)])
            got2 = w.do_virginia(d, net2, lambda m: None, docids=(1,))
            self.assertEqual(got2["stopped"], "")
            self.assertEqual(len(net2.asked), 3)
            self.assertEqual(got2["fetched"], [(1, caps[-1]["file"])])

    def test_the_stage_is_a_flag_of_the_connector_and_asks_the_pause_file(self):
        text = src("warehouse", "connectors", "large_load_waits.py")
        self.assertIn('"--virginia"', text)
        self.assertIn('ip.paused("vascc")', text)


@unittest.skipUnless(raw_root(), "the raw store is not on this machine (ERW_RAW_ROOT names it)")
class ThePullOnThisMachine(unittest.TestCase):
    def test_one_request_to_the_commission_and_its_robots_file_saved_with_its_hash(self):
        raw = os.path.join(raw_root(), "large_load_waits")
        with open(os.path.join(raw, "requests.csv"), encoding="utf-8", newline="") as f:
            mine = [r for r in csv.DictReader(f) if r["host"].endswith(w.VA_HOST)]
        self.assertLessEqual(len(mine), w.VA_CEILING_REQUESTS)
        self.assertLessEqual(sum(int(r["bytes"] or 0) for r in mine), w.VA_CEILING_BYTES)
        self.assertEqual([(r["kind"], r["url"], r["status"]) for r in mine], [("robots file", w.VA_ROBOTS, "200")])
        caps = [c for c in w.read_captures(raw) if c["publisher"] == "vascc"]
        self.assertEqual(len(caps), 1)
        self.assertEqual(caps[0]["sha256"], ROBOTS_SHA256)
        with open(os.path.join(raw, caps[0]["file"]), "rb") as f:
            body = f.read()
        self.assertEqual(hashlib.sha256(body).hexdigest(), ROBOTS_SHA256)
        text = body.decode("utf-8")
        self.assertTrue(text.rstrip().endswith("User-agent: *\nDisallow: /"))
        self.assertEqual(len(w.robots_forbids(text, w.VA_PATHS)), len(w.VA_PATHS))
        self.assertEqual(w.Budget(raw).va["requests"], 1)


@unittest.skipUnless(table_path(), "the table is not on this machine (ERW_WAITS_TABLE names it)")
class TheTableOnThisMachine(unittest.TestCase):
    def test_the_rows_of_session_165_come_out_byte_for_byte_and_no_row_of_dominions_stands_among_them(self):
        with open(table_path(), "rb") as f:
            lines = [ln for ln in f.read().split(b"\n") if not ln.startswith(b"#")]
        head = next(csv.reader([lines[0].decode("utf-8")]))
        data = [ln for ln in lines[1:] if ln]
        e = head.index("entity")
        entities = {next(csv.reader([ln.decode("utf-8")]))[e] for ln in data}
        self.assertNotIn("Dominion Energy Virginia", entities)
        self.assertEqual(len(data), ROWS_165)
        self.assertEqual(hashlib.sha256(b"".join(x + b"\n" for x in data)).hexdigest(), SHA256_165)


class HowSoon(unittest.TestCase):
    FILE = os.path.join(ROOT, "site", "data", "datacenter", "how_soon.json")

    def test_dominion_under_pjm_in_the_builder(self):
        self.assertEqual(hs.ENTITY_GRID["Dominion Energy Virginia"], "pjm")
        self.assertEqual(hs.ENTITY_GRID["PJM Interconnection"], "pjm")
        self.assertEqual(hs.STATED_GROUPS["pjm"], ["Dominion Energy Virginia"])
        self.assertEqual(hs.PLACES["pjm"], "Virginia")
        self.assertNotIn("miso", hs.STATED_GROUPS)
        self.assertNotIn("miso", hs.ENTITY_GRID.values())

    def test_the_site_file_shows_virginia_under_pjm_with_dominions_own_expectations_only(self):
        with open(self.FILE, encoding="utf-8") as f:
            file = json.load(f)
        g = file["grids"]["pjm"]
        self.assertEqual((g["state"], g["place"], g["stages"]), ("not measured yet", "Virginia", []))
        self.assertGreater(len(g["stated"]), 0)
        for s in g["stated"]:
            self.assertEqual((s["stated_by"], s["basis"]), ("Dominion Energy Virginia", "expected"))
            self.assertTrue(s["url"].startswith("https://"))
            self.assertNotIn("@", s["url"])
            self.assertTrue(s["document"] and s["date"] and s["figure"] and s["covers"])
            self.assertNotIn("sentence", s)
        text = json.dumps(g, ensure_ascii=False)
        self.assertNotIn("Amazon", text)
        self.assertNotIn("Google", text)
        self.assertNotIn(EM_DASH, text)
        self.assertNotIn("miso", file["grids"])

    def test_the_name_check_reads_the_entities_the_file_shows(self):
        file = {"grids": {"pjm": {"state": "not measured yet", "stages": [], "stated": [{"document": "A letter about data center load", "figure": "3 years"}]},
                          "nyiso": {"state": "measured", "entity": "New York ISO", "stages": [{"label": "Request to in service"}], "stated": []}}}
        rows = [{"entity": "Bonneville Power Administration", "request_name": "Data Center", "request_names_seen": "1"},
                {"entity": "New York ISO", "request_name": "Made-up Load Number A0", "request_names_seen": "1"}]
        hs.check(file, rows)   # the hidden entity's name is a document's own words: not a leak
        rows[1]["request_name"] = "data center"
        with self.assertRaises(SystemExit):
            hs.check(file, rows)   # the same words as a shown entity's request name are refused
        bad = json.loads(json.dumps(file))
        bad["grids"]["pjm"]["mw"] = "x"
        with self.assertRaises(SystemExit):
            hs.check(bad, rows[:1])


class TheDocuments(unittest.TestCase):
    def test_the_method_note_quotes_the_robots_file_and_the_policy(self):
        note = src("docs", "methods", "large_load_waits.md")
        self.assertIn('"User-agent: *"', note)
        self.assertIn('"Disallow: /"', note)
        self.assertIn(ROBOTS_SHA256, note)
        for q in POLICY_QUOTES:
            self.assertIn(q, note)
        self.assertIn("150", note)
        self.assertIn("500 MB", note)
        page = src("docs", "accelerator", "large_load_waits.md")
        for q in POLICY_QUOTES:
            self.assertIn(q, page)
        self.assertIn("robots file", page)

    def test_no_em_dash_and_no_filing_of_the_sixteen_named_by_its_address(self):
        for parts in (("docs", "methods", "large_load_waits.md"), ("docs", "accelerator", "large_load_waits.md"), ("docs", "methods", "datacenter_cost.md"),
                      ("docs", "accelerator", "letter_facts.md"), ("warehouse", "derived", "how_soon.py"), ("site", "scripts", "check-how-soon.mjs"), ("tests", "test_session171.py")):
            text = src(*parts)
            self.assertNotIn(EM_DASH, text, parts)
        # the sixteen filings were not fetched: no tracked file of this session names one by the docket's file name
        for parts in (("docs", "methods", "large_load_waits.md"), ("docs", "accelerator", "large_load_waits.md")):
            self.assertNotRegex(src(*parts), r"docketsearch/DOCS/8[@#%$][^\s)]*!\.PDF", parts)

    def test_the_page_check_names_virginia_under_pjm(self):
        check = src("site", "scripts", "check-how-soon.mjs")
        self.assertIn("Virginia (Dominion), session 171", check)
        self.assertIn('"Dominion Energy Virginia"', check)
        self.assertIn("licensed source needed", check)


if __name__ == "__main__":
    unittest.main()
