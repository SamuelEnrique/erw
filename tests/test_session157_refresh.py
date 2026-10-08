"""Session 157: the policy monitor's daily refresh (warehouse/connectors/policy_monitor_refresh.py) and its feeds file.

What is held to: the feeds file names eleven regulators and gives every unrefreshed one its reason; a regulator that
refuses is never requested (the request function is replaced by a recorder); the ceilings stop BEFORE 120 requests a
day and space two requests to one host; a redirect is followed only to the regulator's own listed host; the readers
on five saved real list pages (tests/fixtures/session157/lists, saved by the trial of 8 October 2026); a row cut from
a list says so and its sentence is a literal substring of the saved list; nothing municipal passes; the only contact
string is the ruled one. The state of "what is held" in the tests without tables is MADE UP and marked so; it lives in
memory or a temporary folder. The test on the real tables skips on a machine without them. No request and no model
call is made here; the environment is read, never set; no test compares a branch with another."""
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import large_load_rules as llr  # noqa: E402
import policy_monitor_refresh as pm  # noqa: E402

EM = chr(0x2014)
FX = os.path.join(ROOT, "tests", "fixtures", "session157", "lists")
CONNECTOR = os.path.join(ROOT, "warehouse", "connectors", "policy_monitor_refresh.py")
FEEDS = os.path.join(ROOT, "warehouse", "config", "policy_monitor_feeds.json")
TODAY = dt.date(2026, 10, 8)
REFUSING = ["dis.puc.state.oh.us", "puco.ohio.gov", "icc.illinois.gov", "ferc.gov", "misoenergy.org", "dataminer2.pjm.com",
            "api.pjm.com"]
VA_URL = pm.VA_DOCS.format(m=147127)
CA_URL = "https://apps.cpuc.ca.gov/apex/f?p=401:59::::RP,57,RIR:P5_PROCEEDING_SELECT:A2411007"
TX_SEARCH = pm.TX_DOCKETS.format(w="large%20load")
TX_60332 = pm.TX_FILINGS.format(n="60332")


def tables_dir():
    """Where the two real tables are, or None: this copy's warehouse/output, else ERW_TABLES_DIR (read, never set)."""
    for d in (os.path.join(ROOT, "warehouse", "output"), os.environ.get("ERW_TABLES_DIR") or ""):
        if d and all(os.path.exists(os.path.join(d, t + ".csv")) for t in pm.TABLES):
            return d
    return None


def fixture(name):
    with open(os.path.join(FX, name), "rb") as f:
        return f.read()


def held(key, dockets, last_read="2026-08-01", urls=(), blob=""):
    """MADE UP state: what the test says is held of a regulator (no such table). dockets: {number: (topic, title, url)}."""
    return {"name": llr.REGULATORS[key][0], "last_read": last_read, "urls": set(urls), "ids": set(), "blob": blob,
            "dockets": {d: {"topic": t, "title": title, "docket_url": url, "newest": ""} for d, (t, title, url) in dockets.items()}}


class Recorder:
    """Stands in for the request function: records every address asked and answers from a map, else HTTP 404."""

    def __init__(self, answers=None):
        self.asked, self.answers = [], answers or {}

    def __call__(self, url):
        self.asked.append(url)
        a = self.answers.get(url)
        if a is None:
            return 404, b"not found", {}
        return a if isinstance(a, tuple) else (200, a, {})


class Clock:
    def __init__(self):
        self.t, self.slept = 100.0, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def asker(tmp, send=None, clock=None, **kw):
    clock = clock or Clock()
    return pm.Asker(os.path.join(tmp, "run"), lambda m: None, send=send or Recorder(), clock=clock.now, sleep=clock.sleep, **kw)


class Feeds(unittest.TestCase):
    def setUp(self):
        with open(FEEDS, encoding="utf-8") as f:
            self.raw = f.read()
        self.feeds = json.loads(self.raw)

    def test_eleven_regulators_each_unrefreshed_one_with_its_reason(self):
        regs = self.feeds["regulators"]
        self.assertEqual([r["key"] for r in regs], ["ferc", "txpuc", "vascc", "puco", "iurc", "papuc", "ilcc", "gapsc", "azcc", "orpuc", "cpuc"])
        for r in regs:
            self.assertEqual(r["regulator"], llr.REGULATORS[r["key"]][0])
            self.assertEqual(r["state"], llr.REGULATORS[r["key"]][1])
            self.assertEqual(r["jurisdiction"], "federal" if r["key"] == "ferc" else "state")
            if r["refreshed"]:
                self.assertIsNone(r["reason"])
                self.assertIn(r["key"], pm.HOSTS, "a refreshed regulator has a listed host")
                self.assertIn(r["key"], pm.LINES, "a refreshed regulator has a reader")
                self.assertTrue(r["list_url"].startswith("https://"))
                self.assertIn(llr.host_of(r["list_url"]), pm.HOSTS[r["key"]])
            else:
                self.assertTrue(r["reason"] and r["reason"].startswith("Not refreshed: "), r["key"])
                self.assertIsNone(r["list_url"])
                self.assertNotIn(r["key"], pm.HOSTS, "a regulator that refuses has no host the step may ask")
        self.assertEqual([r["key"] for r in regs if not r["refreshed"]], ["puco", "ilcc"])
        self.assertIn("reCAPTCHA", regs[3]["reason"])
        self.assertIn('"Please, no robots or crawlers beyond this point."', regs[6]["reason"])

    def test_ceilings_scope_and_no_em_dash(self):
        self.assertEqual(self.feeds["ceilings"], {"requests_a_day": 120, "seconds_between_requests_to_a_host": 1})
        self.assertEqual(pm.MAX_REQUESTS, 120)
        self.assertEqual(pm.HOST_GAP, 1.0)
        self.assertIn("nothing municipal", self.feeds["scope"])
        self.assertNotIn(EM, self.raw)
        self.assertFalse(re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", self.raw), "no e-mail address in the feeds file")

    def test_terms_are_the_terms_file_s_word_for_word(self):
        terms = llr.load_terms()
        for r in self.feeds["regulators"]:
            t = terms[r["regulator"]]
            self.assertEqual(r["terms_class"], t["class"], r["key"])
            if r["key"] == "vascc":   # read for the first time in session 157: quoted here, the class unchanged
                self.assertIn("Permission is granted to make fair use of the contents of the SCC website.", r["terms_quote"])
                self.assertEqual(len(r["terms_sha256"]), 64)
                continue
            self.assertEqual(r["terms_url"] or "", t["terms_url"] or "", r["key"])
            self.assertEqual(r["terms_quote"] or "", t["terms_quote"] or "", r["key"])

    def test_federal_feeds_say_what_refuses(self):
        ff = self.feeds["federal_feeds"]
        self.assertTrue({"FERC", "DOE", "EPA", "NRC", "BLM", "Interior", "PUCT", "CPUC"} <= {f["agency"] for f in ff})
        for f in ff:
            self.assertEqual(bool(f["reason"]), not f["refreshed"])
        self.assertTrue(any(f["agency"] == "FERC" and not f["refreshed"] and "browser check" in f["reason"] for f in ff))


class NeverRequested(unittest.TestCase):
    def test_a_refusing_host_is_refused_before_any_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder()
            ask = asker(tmp, rec)
            for key, url in (("puco", "https://dis.puc.state.oh.us/CaseRecord.aspx?Caseno=26-0755&link=DIVA"),
                             ("puco", "https://puco.ohio.gov/"), ("ilcc", "https://icc.illinois.gov/docket/P2025-0677"),
                             ("ferc", "https://www.ferc.gov/media/e11-el26-72-000"), ("ferc", "https://elibrary.ferc.gov/eLibrary/search"),
                             ("ferc", "https://www.misoenergy.org/x"), ("ferc", "https://dataminer2.pjm.com/feed/x"),
                             ("ferc", "https://api.pjm.com/api/v1/x"), ("ferc", "https://unblock.federalregister.gov/"),
                             ("txpuc", "https://www.puc.pa.gov/docket/M-2026-3065062"),          # another regulator's host
                             ("txpuc", "https://interchange.puc.texas.gov/x/someone%40example.com/y")):   # an e-mail in the path
                with self.assertRaises(pm.Refused, msg=url):
                    ask.get(key, url, "x")
            self.assertEqual(rec.asked, [], "none of them reached the request function")
            self.assertEqual(ask.n, 0)

    def test_a_whole_run_asks_no_refusing_host(self):
        table = llr.pd.DataFrame(columns=llr.COLS)
        with open(FEEDS, encoding="utf-8") as f:
            feeds = json.load(f)
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder()   # every list answers 404: each regulator fails at its first list and is left
            ask = asker(tmp, rec)
            results, rows, _ = pm.run(feeds, table, ask, lambda m: None, TODAY)
        self.assertEqual(rows, [])
        self.assertEqual(results["puco"]["status"], "not requested")
        self.assertEqual(results["ilcc"]["status"], "not requested")
        self.assertEqual(results["puco"]["requests"] + results["ilcc"]["requests"], 0)
        hosts = {llr.host_of(u) for u in rec.asked}
        self.assertTrue(hosts, "the refreshed regulators were asked")
        for h in hosts:
            self.assertFalse(any(h == r or h.endswith("." + r) for r in REFUSING), h)
            self.assertTrue(any(h in v for v in pm.HOSTS.values()), h)
        self.assertEqual(results["txpuc"]["status"], "failed")   # HTTP 404: recorded, the others still ran
        self.assertEqual(results["cpuc"]["status"], "ok")        # no docket held, so nothing to ask

    def test_the_contact_string_is_the_only_one(self):
        self.assertEqual(pm.CONTACT, "ERW research project, github.com/SamuelEnrique/erw")
        with open(CONNECTOR, encoding="utf-8") as f:
            src = f.read()
        self.assertEqual(src.count('headers={"User-Agent": CONTACT}'), 1)
        self.assertEqual(src.count("requests.get("), 1, "one place makes a request")
        self.assertFalse(re.search(r"[\w.+-]+@[\w-]+\.(com|org|net|edu|gov)\b", src), "no e-mail address in the step")
        self.assertNotIn(EM, src)
        for word in ("anthropic", "llm.client", "messages.create"):
            self.assertNotIn(word, src, "no model reads a line")


class Ceilings(unittest.TestCase):
    def test_stops_before_the_ceiling_not_after(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder({VA_URL: fixture("va_docs_PUR-2026-00131.json")})
            ask = asker(tmp, rec, max_requests=3)
            for _ in range(3):
                ask.get("vascc", VA_URL, "docs.json")
            with self.assertRaises(pm.Stop):
                ask.get("vascc", VA_URL, "docs.json")
            self.assertEqual(len(rec.asked), 3, "the fourth request was never made")

    def test_the_day_s_count_carries_into_a_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder({VA_URL: fixture("va_docs_PUR-2026-00131.json")})
            ask = asker(tmp, rec, used=119)
            ask.get("vascc", VA_URL, "docs.json")   # the 120th of the day
            with self.assertRaises(pm.Stop):
                ask.get("vascc", VA_URL, "docs.json")
            self.assertEqual(len(rec.asked), 1)

    def test_one_request_a_second_to_a_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock = Clock()
            rec = Recorder({VA_URL: fixture("va_docs_PUR-2026-00131.json"), CA_URL: fixture("ca_decisions_A2411007.html")})
            ask = asker(tmp, rec, clock)
            ask.get("vascc", VA_URL, "a")
            ask.get("cpuc", CA_URL, "b")       # another host: no wait
            self.assertEqual(clock.slept, [])
            ask.get("vascc", VA_URL, "c")      # the same host at once: waits the whole second
            self.assertEqual(len(clock.slept), 1)
            self.assertAlmostEqual(clock.slept[0], 1.0)
            clock.t += 5
            ask.get("vascc", VA_URL, "d")      # five seconds later: no wait
            self.assertEqual(len(clock.slept), 1)

    def test_a_redirect_is_followed_only_to_the_listed_host(self):
        upper = "https://www.scc.virginia.gov/DocketSearchAPI/breeze/CaseDetails/GetDocuments?x=1"
        lower = "https://www.scc.virginia.gov/docketsearchapi/breeze/casedetails/getdocuments?x=1"
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder({upper: (307, b"", {"Location": lower}), lower: fixture("va_docs_PUR-2026-00131.json")})
            ask = asker(tmp, rec)
            ask.get("vascc", upper, "docs.json")
            self.assertEqual(rec.asked, [upper, lower])
            self.assertEqual(ask.n, 2, "each hop is a request")
            away = Recorder({upper: (302, b"", {"Location": "https://unblock.federalregister.gov/"})})
            ask2 = pm.Asker(os.path.join(tmp, "run2"), lambda m: None, send=away, clock=Clock().now, sleep=lambda s: None)
            with self.assertRaises(pm.Refused):
                ask2.get("vascc", upper, "docs.json")
            self.assertEqual(away.asked, [upper], "the other host was never asked")

    def test_a_robot_check_is_recorded_and_left(self):
        page = b"<html><head><title>Just a moment...</title></head><body>Please, no robots or crawlers beyond this point.</body></html>"
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder({CA_URL: page})
            ask = asker(tmp, rec)
            with self.assertRaises(pm.Refused):
                ask.get("cpuc", CA_URL, "decisions.html")
            with open(ask.manifest, encoding="utf-8") as f:
                notes = [r["note"] for r in csv.DictReader(f)]
            self.assertEqual(notes, ["answered with a check: not passed, left"])

    def test_a_regulator_that_failed_today_is_not_asked_again_today(self):
        table = llr.pd.DataFrame(columns=llr.COLS)
        feeds = {"regulators": [{"key": "txpuc", "refreshed": True, "reason": None}]}
        day = {"requests": 13, "left": {"txpuc": "HTTP 403"}, "done": []}
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder()
            results, _, _ = pm.run(feeds, table, asker(tmp, rec), lambda m: None, TODAY, day=day)
        self.assertEqual(rec.asked, [])
        self.assertEqual(results["txpuc"]["status"], "failed")
        self.assertIn("not asked again today", results["txpuc"]["detail"])


class Readers(unittest.TestCase):
    def test_which_lines_are_an_order_of_the_regulator(self):
        # every line here is a real line of a list read on 8 October 2026
        yes = ["ORDER ADOPTING NEW 16 TAC §25.194", "PROPOSAL FOR PUBLICATION NEW §25.521", "ORDER GRANTING GOOD CAUSE EXCEPTIONS",
               "Order Establishing Docket", "ORDER ADOPTING STIPULATION", "Secretarial Letter", "Opinion and Order", "Final Order",
               "SOAH ORDER NO. 12- ADMITTING EVIDENCE; REMANDING CASE TO THE COMMISSION; AND DISMISSING FROM SOAH’S DOCKET"]
        no = ["AXM's Motion to Intervene", "PROCEDURAL AND SCHEDULING ORDER", "FIRST AMENDED PROCEDURAL AND SCHEDULING ORDER",
              "Georgia Power Company’s Storm Cost Recovery (SCR) Application PIA Staff’s Proposed Order Adopting Stipulation",
              "Comments on data centers", "EPE's Response to TIEC's 2nd RFI", "Notice of Appeal", "Void Letter for Item 68",
              "ORDER NO. 1- REQUIRING COMMISSION STAFF COMMENTS AND RECOMMENDATIONS AND GRANTING AXM’S MOTION TO INTERVENE",
              "Data Request from Commission Staff (STF-PIA-46)"]
        for t in yes:
            self.assertTrue(pm.is_order(t), t)
        for t in no:
            self.assertFalse(pm.is_order(t), t)

    def test_the_topic_of_a_new_docket_is_by_its_words(self):
        self.assertEqual(pm.topic_of("REVIEW OF ERCOT'S INTERCONNECTION PROCESSES FOR LARGE LOADS"), "large-load interconnection")
        self.assertEqual(pm.topic_of("APPLICATION OF SOUTHWESTERN PUBLIC SERVICE COMPANY FOR APPROVAL OF LARGE LOAD CUSTOMER TARIFF PROVISIONS"),
                         "large-load tariff")
        self.assertEqual(pm.topic_of("Ex Parte: In Re: Allocating transmission costs to large-load customers"), "large-load tariff")
        self.assertEqual(pm.topic_of("Evaluation of Transmission Cost Recovery"), "transmission cost allocation")
        self.assertEqual(pm.topic_of("Rulemaking on interconnection queue reform"), "interconnection reform")
        self.assertEqual(pm.topic_of("Southern Indiana Gas and Electric Company"), "")
        self.assertTrue(set(t for t, _ in pm.TOPIC_RULES) == set(llr.TOPICS))

    def test_dates_as_the_lists_write_them(self):
        self.assertEqual(pm.day_of("10/6/2026"), "2026-10-06")
        self.assertEqual(pm.day_of("2026-08-25T00:00:00.000"), "2026-08-25")
        self.assertEqual(pm.day_of("September 03, 2026"), "2026-09-03")
        self.assertEqual(pm.day_of("08/25/2026"), "2026-08-25")
        self.assertEqual(pm.day_of("-"), "")
        self.assertEqual(pm.day_of("2/30/2026"), "")

    def test_virginia_s_document_list(self):
        rec = {"text": pm.norm(pm.as_text(fixture("va_docs_PUR-2026-00131.json")))}
        lines = pm.parse_va_docs(fixture("va_docs_PUR-2026-00131.json").decode("utf-8"), "PUR-2026-00131", rec)
        self.assertEqual(len(lines), 1)
        c = lines[0]
        self.assertEqual(c["date"], "2026-08-25")
        self.assertTrue(c["order"])
        self.assertEqual(c["line"], "Ex Parte: In the matter of allocating transmission costs to large-load customers - Order "
                                    "Establishing Docket - 08/25/2026")
        self.assertEqual(c["doc_url"], "https://www.scc.virginia.gov/docketsearch/DOCS/8%237%2501!.PDF")
        self.assertIn(c["line"], rec["text"], "the line is a literal substring of the saved list's text")

    def test_virginia_s_case_list(self):
        cases = json.loads(fixture("va_cases_large-load.json"))
        self.assertEqual({c["Case_Number"]: c["MATTER_NO"] for c in cases}["PUR-2026-00131"], pm.VA_MATTERS["PUR-2026-00131"])

    def test_texas_docket_search_and_filing_list(self):
        found = {c["docket"]: c["caption"] for c in pm.parse_tx_dockets(fixture("tx_dockets_large_load.html").decode("utf-8"))}
        self.assertIn("58481", found)
        self.assertEqual(found["60332"], "APPLICATION OF SOUTHWESTERN PUBLIC SERVICE COMPANY FOR APPROVAL OF LARGE LOAD CUSTOMER TARIFF PROVISIONS")
        lines = pm.parse_tx_filings(fixture("tx_filings_60332.html").decode("utf-8"), "60332", {"text": ""}, TX_60332)
        self.assertGreaterEqual(len(lines), 9)
        self.assertEqual(lines[0]["item"], "1")
        self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["date"]) for x in lines))
        self.assertTrue(all(x["doc_url"].startswith("https://interchange.puc.texas.gov/search/documents/?controlNumber=60332&itemNumber=") for x in lines))
        self.assertFalse(any(x["order"] for x in lines if "MOTION TO INTERVENE" in x["line"].upper()))

    def test_california_s_decisions_list(self):
        lines = pm.parse_ca_decisions(fixture("ca_decisions_A2411007.html").decode("utf-8"), "A.24-11-007", {"text": ""}, CA_URL)
        orders = [x for x in lines if x["order"]]
        self.assertEqual({x["doc_id"] for x in orders}, {"618383226", "574875643"})
        self.assertTrue(any(x["date"] == "2026-09-03" and x["line"].startswith("Decision D2609016 - Order Extending Statutory Deadline.") for x in orders))
        self.assertFalse(any(x["order"] for x in lines if x["line"].startswith("Proposed Decision")))

    def test_a_json_list_s_text_holds_every_leaf(self):
        text = pm.json_text({"a": [{"description": "Decision - Dissenting Opinion", "decisionNumber": 81587, "x": None}]})
        self.assertEqual(text, "description: Decision - Dissenting Opinion\ndecisionNumber: 81587")


class Rows(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.terms = llr.load_terms()

    def lines(self, key, url, name, parse, *args):
        ask = asker(self.tmp.name, Recorder({url: fixture(name)}))
        page, rec = ask.get(key, url, name)
        return parse(page, *[rec if a is None else a for a in args])

    def test_a_row_cut_from_a_list_says_so_and_is_proved(self):
        h = held("vascc", {"PUR-2026-00131": ("transmission cost allocation", "Ex Parte: In Re: Allocating transmission costs to large-load customers", "")})
        lines = self.lines("vascc", VA_URL, "va_docs_PUR-2026-00131.json", pm.parse_va_docs, "PUR-2026-00131", None)
        rows, left = pm.to_rows("vascc", lines, h, "2026-08-01", self.terms, TODAY)
        self.assertEqual((len(rows), left), (1, []))
        r = rows[0]
        self.assertEqual(list(r), llr.COLS, "the table's own columns, in order")
        self.assertEqual(r["sentence"], "Ex Parte: In the matter of allocating transmission costs to large-load customers - Order "
                                        "Establishing Docket - 08/25/2026")
        self.assertEqual(r["sentence_kind"], "docket list")
        self.assertTrue(r["row_flag"].startswith("cut from the docket list"))
        self.assertIn("Cut from the docket search's document list of the case", r["notes"])
        self.assertIn("the document itself was not read", r["notes"])
        self.assertEqual((r["event_date"], r["event_type"], r["row_kind"], r["status"], r["source"]),
                         ("2026-08-25", "regulatory_order", "order", "decided", "vascc:dockets"))
        self.assertEqual(r["topic"], "transmission cost allocation", "a row in a docket held takes the docket's own topic")
        self.assertEqual((r["regulator"], r["jurisdiction"], r["state"]), ("Virginia State Corporation Commission", "state", "VA"))
        self.assertEqual(r["page"], "")
        self.assertEqual(r["status_as_worded"], "", "a field the list does not state is empty")
        self.assertEqual(r["collected_in"], "daily refresh (policy_monitor_refresh.py)")
        self.assertEqual(len(r["text_sha256"]), 64)
        self.assertTrue(r["event_id"].startswith("vascc:PUR-2026-00131:order:"))

    def test_a_line_already_held_or_older_than_the_last_read_is_not_new(self):
        title = "Ex Parte: In Re: Allocating transmission costs to large-load customers"
        lines = self.lines("vascc", VA_URL, "va_docs_PUR-2026-00131.json", pm.parse_va_docs, "PUR-2026-00131", None)
        h = held("vascc", {"PUR-2026-00131": ("transmission cost allocation", title, "")},
                 urls=["https://www.scc.virginia.gov/docketsearch/DOCS/8%237%2501!.PDF"])
        self.assertEqual(pm.to_rows("vascc", lines, h, "2026-08-01", self.terms, TODAY)[0], [], "its address is a row already")
        h2 = held("vascc", {"PUR-2026-00131": ("transmission cost allocation", title, "")})
        self.assertEqual(pm.to_rows("vascc", lines, h2, "2026-10-06", self.terms, TODAY)[0], [], "dated before the lists were last read")
        h3 = held("vascc", {})
        self.assertEqual(pm.to_rows("vascc", lines, h3, "2026-08-01", self.terms, TODAY)[0], [], "an order in a docket not held is not a row")

    def test_the_baseline_is_the_last_read_less_two_days(self):
        self.assertEqual(pm.baseline({"last_read": "2026-10-08"}, TODAY), "2026-10-06")
        self.assertEqual(pm.baseline({"last_read": ""}, TODAY), "2026-10-06")

    def test_california_s_decision_is_found_again_when_its_row_is_not_held(self):
        title = "Application of Pacific Gas and Electric Company (U39E) for Approval of Electric Rule No. 30 for Transmission-Level Retail Electric Service."
        page_url = CA_URL.replace("401:59:", "401:56:")
        lines = self.lines("cpuc", CA_URL, "ca_decisions_A2411007.html", pm.parse_ca_decisions, "A.24-11-007", None, page_url)
        # MADE UP state: the docket held with its 2025 decision only; its caption names no topic term, the lines neither
        h = held("cpuc", {"A.24-11-007": ("large-load interconnection", title, page_url)}, blob="x/574875643.PDF")
        rows, left = pm.to_rows("cpuc", lines, h, "2026-08-01", self.terms, TODAY)
        self.assertEqual(rows, [])
        self.assertEqual([why for _, why in left], ["an order in a docket held whose caption names no topic term, and the line names none"])
        # the same docket under a caption that names large loads: every decision in it is on the topic
        h = held("cpuc", {"A.24-11-007": ("large-load interconnection", title + " (large load)", page_url)}, blob="x/574875643.PDF")
        rows, _ = pm.to_rows("cpuc", lines, h, "2026-08-01", self.terms, TODAY)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["sentence"].startswith("Decision D2609016 - Order Extending Statutory Deadline."))
        self.assertEqual(rows[0]["source_url"], "https://docs.cpuc.ca.gov/SearchRes.aspx?DocFormat=ALL&DocID=618383226")
        self.assertEqual(rows[0]["sentence_from"], "proceeding's decisions list")

    def test_a_new_texas_docket_is_a_proceeding_row_dated_by_its_first_filing(self):
        answers = {TX_SEARCH: fixture("tx_dockets_large_load.html"), TX_60332: fixture("tx_filings_60332.html"),
                   pm.TX_DOCKETS.format(w="data%20center"): fixture("tx_dockets_large_load.html")}
        rec = Recorder(answers)
        ask = asker(self.tmp.name, rec)
        # MADE UP state: nothing above control number 59999 is held, so 60332 on the search list is a docket not seen before
        h = held("txpuc", {"59999": ("large-load tariff", "MADE UP", TX_60332.replace("60332", "59999"))})
        answers[h["dockets"]["59999"]["docket_url"]] = fixture("tx_filings_60332.html")
        lines = pm.lines_txpuc(ask, h, "2026-08-01")
        new = [x for x in lines if x["kind"] == "proceeding"]
        self.assertEqual([x["docket"] for x in new], ["60332"])
        rows, _ = pm.to_rows("txpuc", new, h, "2026-08-01", self.terms, TODAY)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["row_kind"], r["event_type"], r["topic"], r["status_class"]),
                         ("proceeding", "regulatory_proceeding", "large-load tariff", "not stated"))
        self.assertEqual(r["sentence"], "APPLICATION OF SOUTHWESTERN PUBLIC SERVICE COMPANY FOR APPROVAL OF LARGE LOAD CUSTOMER TARIFF PROVISIONS")
        self.assertEqual(r["event_date"], "2026-09-24", "the day of the docket's first filing, as the list stamps it")
        self.assertIn("not a person's reading", r["notes"])
        self.assertTrue(all(llr.host_of(u) == "interchange.puc.texas.gov" for u in rec.asked))

    def test_nothing_municipal_passes(self):
        for word in ("zoning", "city council", "county board"):
            line = f"Order on a {word} matter for a large load"    # MADE UP line: no list holds it
            c = {"docket": "MADEUP-1", "date": "2026-10-07", "line": line, "doc_title": line, "kind": "order", "order": True,
                 "doc_url": "https://www.puc.pa.gov/pcdocs/0.pdf", "docket_url": "", "status_worded": "", "title": "",
                 "rec": {"text": line, "text_file": os.path.join(self.tmp.name, "t.txt"), "text_sha256": "0" * 64, "retrieved_at": "2026-10-08T00:00:00Z"},
                 "list": "the docket page's document list"}
            h = held("papuc", {"MADEUP-1": ("large-load tariff", "MADE UP large load docket", "")})
            rows, left = pm.to_rows("papuc", [c], h, "2026-10-01", self.terms, TODAY)
            self.assertEqual(rows, [], word)
            self.assertIn("municipal", left[0][1])

    def test_a_line_that_is_not_in_the_saved_text_is_left_out(self):
        line = "Order Establishing Docket"
        c = {"docket": "MADEUP-1", "date": "2026-10-07", "line": line, "doc_title": line, "kind": "order", "order": True,
             "doc_url": "https://www.puc.pa.gov/pcdocs/0.pdf", "docket_url": "", "status_worded": "", "title": "",
             "rec": {"text": "another text", "text_file": "t", "text_sha256": "0" * 64, "retrieved_at": "2026-10-08T00:00:00Z"},
             "list": "the docket page's document list"}
        h = held("papuc", {"MADEUP-1": ("large-load tariff", "MADE UP large load docket", "")})
        rows, left = pm.to_rows("papuc", [c], h, "2026-10-01", self.terms, TODAY)
        self.assertEqual(rows, [])
        self.assertEqual(left[0][1], "the line is not a literal substring of the saved list's text")


class Step(unittest.TestCase):
    def test_the_daily_run_starts_it_as_a_soft_step(self):
        with open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8") as f:
            sh = f.read()
        line = 'soft_step policy_monitor_refresh "$PYTHON" warehouse/connectors/policy_monitor_refresh.py'
        self.assertEqual(sh.count(line), 1)
        self.assertGreater(sh.index(line), sh.index(". warehouse/soft_step.sh"), "after the soft step function is read")
        self.assertLess(sh.index(line), sh.index('echo "== connector status"'), "before the status is recorded and the validator runs")
        self.assertNotIn("--strict", sh[sh.index(line):sh.index(line) + 200].splitlines()[0])

    def test_the_two_tables_stay_out_of_the_live_set(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            y = f.read()
        hold = y[y.index("large_load_statements"):]
        for t in pm.TABLES:
            self.assertRegex(hold, r"(?m)^\s*- " + t + r"\s*$")

    def test_a_new_row_is_merged_into_the_table_held_and_the_table_still_validates(self):
        """The whole step on saved real list pages, offline, into a temporary folder. The table it merges into is MADE
        UP (one row, marked so): the real tables are not on every machine."""
        title = "Ex Parte: In Re: Allocating transmission costs to large-load customers"
        row = {c: "" for c in llr.COLS}
        row.update({"event_id": "vascc:PUR-2026-00131:proceeding:madeup0001", "event_date": "2026-08-01", "event_type": "regulatory_proceeding",
                    "parties": "Virginia State Corporation Commission", "status": "open", "source": "vascc:dockets",
                    "source_url": "https://www.scc.virginia.gov/docketsearch/DOCS/MADEUP.PDF", "regulator": "Virginia State Corporation Commission",
                    "jurisdiction": "state", "state": "VA", "docket_number": "PUR-2026-00131", "proceeding_title": title,
                    "row_kind": "proceeding", "topic": "transmission cost allocation", "document_title": "MADE UP for a test",
                    "status_class": "open", "sentence": "MADE UP for a test: no document holds this sentence.", "sentence_from": "order text",
                    "sentence_kind": "document", "notes": "MADE UP for a test", "retrieved_at": "2026-08-01T00:00:00Z"})
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "in"))
            with open(os.path.join(tmp, "in", "large_load_rules_internal.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# MADE UP for a test (tests/test_session157_refresh.py): one row, no such document\n"
                        "# Shape: events (docs/datastandard.md v0)\n# Source: erw:large_load_rules_internal\n# License: internal.\n")
                llr.pd.DataFrame([row], columns=llr.COLS).to_csv(f, index=False, lineterminator="\n")
            off = os.path.join(tmp, "off")
            os.makedirs(off)
            index = {pm.VA_CASES.format(w=w): os.path.join(FX, "va_cases_large-load.json") for w in ("large%20load", "large-load", "data%20center")}
            index[VA_URL] = os.path.join(FX, "va_docs_PUR-2026-00131.json")
            with open(os.path.join(off, "index.json"), "w", encoding="utf-8") as f:
                json.dump(index, f)
            out = os.path.join(tmp, "out")
            p = subprocess.run([sys.executable, CONNECTOR, "--offline", off, "--in-dir", os.path.join(tmp, "in"), "--out-dir", out,
                                "--only", "vascc"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            path = os.path.join(out, "large_load_rules_internal.csv")
            got = pm.read_events(path)
            self.assertEqual(list(got.columns), llr.COLS)
            self.assertEqual(len(got), 2, p.stdout)
            new = got[got["event_id"] != row["event_id"]].iloc[0]
            self.assertEqual((new["docket_number"], new["event_date"], new["row_kind"], new["sentence_kind"]),
                             ("PUR-2026-00131", "2026-08-25", "order", "docket list"))
            self.assertTrue(new["row_flag"].startswith("cut from the docket list"))
            self.assertFalse(os.path.exists(os.path.join(out, "large_load_rules.csv")), "Virginia's rows are internal: the public table gains none")
            with open(path, encoding="utf-8") as f:
                header = "".join(next(f) for _ in range(ip.header_rows(path)))
            self.assertIn("License: internal", header)
            self.assertIn("Daily refresh (session 157)", header)
            with open(os.path.join(out, "policy_monitor_refresh_last_run.json"), encoding="utf-8") as f:
                last = json.load(f)
            self.assertEqual(set(last), {"at_utc", "requests", "bytes", "regulators", "tables_written"})
            self.assertEqual(last["requests"], 0, "offline: no request")
            self.assertEqual(last["regulators"]["vascc"]["new_rows"], 1)
            self.assertEqual(set(last["regulators"]["vascc"]), {"requests", "new_rows", "status", "detail"})
            self.assertEqual(last["tables_written"], {"large_load_rules_internal": 1})
            again = subprocess.run([sys.executable, CONNECTOR, "--offline", off, "--out-dir", out, "--only", "vascc"],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertEqual(len(pm.read_events(path)), 2, "a second run adds the row no second time")
            v = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "validate", "erw_validate.py"), path],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(v.returncode, 0, v.stdout + v.stderr)

    def test_on_the_real_tables_a_removed_row_is_found_again_and_written(self):
        d = tables_dir()
        if not d:
            self.skipTest("large_load_rules is not on this machine")
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(d, "large_load_rules.csv")
            n = ip.header_rows(src)
            with open(src, encoding="utf-8") as f:
                head = [next(f) for _ in range(n)]
            t = pm.read_events(src)
            keep = t[(t["docket_number"] == "A.24-11-007") & ~t["source_url"].str.contains("618383226")]
            if len(keep) != len(t[t["docket_number"] == "A.24-11-007"]) - 1 or not len(keep):
                self.skipTest("the table no longer holds Decision 26-09-016 of A.24-11-007 as one row")
            os.makedirs(os.path.join(tmp, "in"))
            with open(os.path.join(tmp, "in", "large_load_rules.csv"), "w", encoding="utf-8", newline="") as f:
                f.writelines(head)
                keep.to_csv(f, index=False, lineterminator="\n")
            off = os.path.join(tmp, "off")
            os.makedirs(off)
            with open(os.path.join(off, "index.json"), "w", encoding="utf-8") as f:
                json.dump({CA_URL: os.path.join(FX, "ca_decisions_A2411007.html")}, f)
            out = os.path.join(tmp, "out")
            p = subprocess.run([sys.executable, CONNECTOR, "--offline", off, "--in-dir", os.path.join(tmp, "in"), "--out-dir", out,
                                "--only", "cpuc", "--since", "2026-08-01"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            got = pm.read_events(os.path.join(out, "large_load_rules.csv"))
            new = got[~got["event_id"].isin(set(keep["event_id"]))]
            if "large load" not in " ".join(keep["proceeding_title"]).lower():
                # the docket's caption names no topic term and the decision's line names none: the rule leaves it out
                self.assertEqual(len(new), 0)
                return
            self.assertEqual(len(new), 1, p.stdout)
            r = new.iloc[0]
            self.assertEqual((r["docket_number"], r["event_date"], r["sentence_kind"]), ("A.24-11-007", "2026-09-03", "docket list"))
            with open(os.path.join(out, "large_load_rules.csv"), encoding="utf-8") as f:
                header = "".join(next(f) for _ in range(ip.header_rows(os.path.join(out, "large_load_rules.csv"))))
            self.assertIn("License: public", header)
            self.assertIn("Daily refresh (session 157)", header)
            with open(os.path.join(out, "policy_monitor_refresh_last_run.json"), encoding="utf-8") as f:
                last = json.load(f)
            self.assertEqual(set(last), {"at_utc", "requests", "bytes", "regulators", "tables_written"})
            self.assertEqual(last["requests"], 0, "offline: no request")
            v = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "validate", "erw_validate.py"),
                                os.path.join(out, "large_load_rules.csv")], capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(v.returncode, 0, v.stdout + v.stderr)


if __name__ == "__main__":
    unittest.main()
