"""Session 172, part D: the Virginia State Corporation Commission is paused (warehouse/metadata/paused_sources.csv, scope
vascc), on the owner's ruling of 9 October 2026 after session 171 read the commission's robots file (User-agent: * /
Disallow: /). What is held to: the row is there and says what it quotes; the policy monitor's daily refresh sends the
commission nothing while the row is there (the regulator is marked "not requested" with the pause as its reason, and
the request function is never reached); the host itself is refused whatever regulator key asks for it; the other
regulators are asked as before; the pause note of the source registry points at the publisher's own method note; the
method note and the permission draft exist, quote the robots file's two lines, name the ruled contact string, and hold
no e-mail address and no em dash. No request and no model call is made here; the environment is read, never set."""
import csv
import datetime as dt
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import large_load_rules as llr  # noqa: E402
import policy_monitor_refresh as pm  # noqa: E402

EM = chr(0x2014)
PAUSED = os.path.join(ROOT, "warehouse", "metadata", "paused_sources.csv")
FEEDS = os.path.join(ROOT, "warehouse", "config", "policy_monitor_feeds.json")
TODAY = dt.date(2026, 10, 10)
FILES = ("warehouse/connectors/policy_monitor_refresh.py", "warehouse/connectors/iso_prices.py", "warehouse/metadata/paused_sources.csv",
         "docs/methods/vascc_pause.md", "docs/reviews/scc-permission-email.md", "docs/methods/policy_monitor.md", "tests/test_session172.py")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def paused_rows():
    with open(PAUSED, encoding="utf-8", newline="") as f:
        return {r["scope"]: r for r in csv.DictReader(f)}


class Recorder:
    """Stands in for the request function: records every address asked and answers 404 to each."""

    def __init__(self):
        self.asked = []

    def __call__(self, url):
        self.asked.append(url)
        return 404, b"not found", {}


class Clock:
    def __init__(self):
        self.t = 100.0

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


def asker(tmp, rec):
    c = Clock()
    return pm.Asker(os.path.join(tmp, "run"), lambda m: None, send=rec, clock=c.now, sleep=c.sleep)


class TheRow(unittest.TestCase):
    def test_virginia_is_paused_and_the_row_says_what_it_quotes(self):
        rows = paused_rows()
        self.assertIn("vascc", rows, "the pause is lifted: a person deleted the row, and this test follows")
        self.assertIn("miso", rows, "MISO's row is untouched")
        r = rows["vascc"]
        self.assertEqual(r["paused_on"], "2026-10-10")
        self.assertEqual(r["terms_url"], "https://www.scc.virginia.gov/robots.txt")
        self.assertEqual(r["terms_quoted"], "User-agent: * Disallow: /")
        self.assertIn("Samuel, 9 October 2026", r["ruled_by"])
        self.assertIn("scc-permission-email.md", r["until"])
        self.assertIn("nothing is deleted", r["note"].lower())
        self.assertTrue(re.search(r["match"], "vascc:dockets"))
        self.assertTrue(re.search(r["match"], "https://www.scc.virginia.gov/docketsearch"))
        self.assertFalse(re.search(r["match"], "txpuc:dockets"))
        self.assertEqual(ip.paused("vascc")["scope"], "vascc")
        self.assertIsNone(ip.paused("txpuc"))

    def test_the_host_is_known_as_paused_whatever_the_caller(self):
        for h in ("www.scc.virginia.gov", "scc.virginia.gov", "WWW.SCC.VIRGINIA.GOV"):
            self.assertEqual(ip.paused_host(h)["scope"], "vascc", h)
        self.assertEqual(ip.paused_host("cdn.misoenergy.org")["scope"], "miso")
        for h in ("apps.cpuc.ca.gov", "interchange.puc.texas.gov", "www.federalregister.gov", "", None):
            self.assertIsNone(ip.paused_host(h), h)

    def test_the_registry_note_points_at_the_publishers_own_method_note(self):
        note = ip.pause_note("vascc:dockets", "Virginia State Corporation Commission")
        self.assertIn("[PAUSED 2026-10-10", note)
        self.assertIn("docs/methods/vascc_pause.md", note)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "methods", "vascc_pause.md")))
        miso = ip.pause_note("miso:da_expost_lmp", "Midcontinent Independent System Operator (MISO)")
        self.assertIn("docs/methods/miso_pause.md", miso)
        self.assertEqual(ip.pause_note("spp:DA-MCP", "Southwest Power Pool (SPP)"), "")


class TheRefresh(unittest.TestCase):
    def test_the_commissions_addresses_are_refused_before_any_request(self):
        for url in (pm.VA_DOCS.format(m=146728), pm.VA_CASES.format(w="large%20load"),
                    "https://www.scc.virginia.gov/docketsearch/DOCS/x.PDF"):
            why = pm.Asker.allowed("vascc", url)
            self.assertIn("paused since 2026-10-10", why, url)
        # the host is refused under another regulator's key too (it would be refused as "not the listed host" anyway,
        # and the pause is named first only when the key is paused; either way nothing is sent)
        self.assertNotEqual(pm.Asker.allowed("txpuc", pm.VA_DOCS.format(m=146728)), "")
        self.assertEqual(pm.Asker.allowed("txpuc", "https://interchange.puc.texas.gov/search/filings/?UtilityType=A&ControlNumber=60332"), "")
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder()
            ask = asker(tmp, rec)
            with self.assertRaises(pm.Refused):
                ask.get("vascc", pm.VA_DOCS.format(m=146728), "docs.json")
            self.assertEqual(rec.asked, [])
            self.assertEqual(ask.n, 0)

    def test_a_whole_run_sends_the_commission_nothing_and_asks_the_others(self):
        table = llr.pd.DataFrame(columns=llr.COLS)
        with open(FEEDS, encoding="utf-8") as f:
            feeds = json.load(f)
        va = next(r for r in feeds["regulators"] if r["key"] == "vascc")
        self.assertTrue(va["refreshed"], "the feeds file still lists Virginia as refreshed: the pause file alone is the switch")
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder()
            results, rows, _ = pm.run(feeds, table, asker(tmp, rec), lambda m: None, TODAY)
        self.assertEqual(results["vascc"]["status"], "not requested")
        self.assertEqual(results["vascc"]["requests"], 0)
        self.assertIn("Paused since 2026-10-10", results["vascc"]["detail"])
        self.assertIn("paused_sources.cs", results["vascc"]["detail"][:300])
        self.assertFalse([u for u in rec.asked if "scc.virginia.gov" in u], "an address of the commission reached the request function")
        self.assertTrue([u for u in rec.asked if "interchange.puc.texas.gov" in u], "Texas was not asked: the pause stopped more than Virginia")
        self.assertEqual(rows, [])

    def test_the_step_consults_the_pause_file_in_its_code(self):
        code = src("warehouse", "connectors", "policy_monitor_refresh.py")
        self.assertIn("ip.paused(key)", code)
        self.assertIn("ip.paused_host(host)", code)


class TheDocuments(unittest.TestCase):
    def test_the_method_note_quotes_the_robots_file_and_says_what_stays(self):
        note = src("docs", "methods", "vascc_pause.md")
        for word in ("User-agent: *", "Disallow: /", "Nothing is deleted", "paused_sources.csv", "To lift the pause",
                     "Not paused", "scc-permission-email.md", "robots.txt"):
            self.assertIn(word, note, word)
        self.assertIn("vascc_pause.md", src("docs", "methods", "policy_monitor.md"))
        self.assertIn("vascc_pause.md", src("CLAUDE.md"))

    def test_the_permission_draft_is_short_polite_and_holds_no_address_of_a_person(self):
        draft = src("docs", "reviews", "scc-permission-email.md")
        self.assertIn("ERW research project, github.com/SamuelEnrique/erw", draft)
        self.assertIn("academic research project", draft)
        self.assertIn("PUR-2026-00011", draft)
        self.assertIn("Nothing here was sent", draft)
        self.assertFalse(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", draft), "an e-mail address is in the draft")
        body = draft.split("---", 1)[1]
        self.assertLess(len(body.split()), 520, "the draft is not short")
        for word in ("Dear", "Thank you", "Kind regards"):
            self.assertIn(word, body, word)

    def test_no_em_dash_in_this_sessions_files(self):
        for rel in FILES:
            self.assertNotIn(EM, src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
