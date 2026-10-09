"""Session 155: how long large loads waited, measured from successive dated copies of public queues
(warehouse/connectors/large_load_waits.py). The ceilings refuse BEFORE a request; a publisher that is never asked is
refused whatever the address; the contact string is the ruled one and holds no address of a person; a copy is dated
by its publisher and never by its capture; a request seen in two copies gives a lower bound and is labeled; a
duration is a range between bounds and never a midpoint; a stage is counted only where a copy shows it; a figure on
fewer than five requests is its values and not a median; lower bounds are never mixed with measured durations; the
one-page summary's counts equal the table's; no NYISO request is named in a tracked file.

Every request and copy in this file is MADE UP FOR THE TEST (identifiers T1, T2 and so on): no row of a publisher's
queue is here. The tests that need the saved copies skip on a machine without the raw store (it is not in the
repository): they look under warehouse/raw of this copy, or under the directory the environment variable
ERW_RAW_ROOT names. No request and no model call. The module reads the environment and never sets it."""
import csv
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_waits as w  # noqa: E402

AT = chr(64)
EM_DASH = chr(0x2014)
BUILT = {}
KEY = {"1": "Scoping Meeting Pending", "4": "SRIS/SIS Pending", "5": "SRIS/SIS in Progress", "6": "SRIS/SIS Approved", "9": "FS in Progress",
       "11": "IA Completed", "12": "Under Construction", "14": "In Service Commercial", "0": "Withdrawn"}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw_root():
    """The directory that holds large_load_waits/captures.csv, or None on a machine without it. Reads the environment, never sets it."""
    for d in (os.environ.get("ERW_RAW_ROOT"), os.path.join(ROOT, "warehouse", "raw")):
        if d and os.path.exists(os.path.join(d, "large_load_waits", "captures.csv")):
            return d
    return None


def built():
    """The table built once from the saved copies, with nothing written and no request."""
    if "b" not in BUILT:
        raw = os.path.join(raw_root(), "large_load_waits")
        b = w.build(raw, lambda m: None)
        wf = os.path.join(raw_root(), "large_load_statements", "wait_figures.csv")
        stated = []
        if os.path.exists(wf):
            with open(wf, encoding="utf-8", newline="") as f:
                stated = list(csv.DictReader(f))
        comparison, none = w.compare(b["rows"], stated)
        BUILT["b"] = (b, w.counts_of(b, comparison, none))
    return BUILT["b"]


def seen(rid, *steps, qd="2020-01-10", mw="100", name="made up for the test"):
    """Observations of one made-up request: steps are (the copy's day, the status code)."""
    return [dict(id=rid, id_printed=rid, name=name, developer="", mw=mw, queue_date_printed=qd, queue_date=qd, status_code=code, status_words=KEY[code],
                 sheet="made up", date=day, stamp=day, url=f"https://web.archive.org/web/{day.replace('-', '')}000000id_/https://example.org/queue.xlsx", file="x")
            for day, code in steps]


def one(rows, interval, words=""):
    got = [r for r in rows if r["interval"] == interval and r["stage_as_worded"] == words]
    assert len(got) == 1, (interval, words, [(r["interval"], r["stage_as_worded"]) for r in rows])
    return got[0]


class NoSession:
    """Stands where the network would be: any use of it is a request that should not have been made."""
    def get(self, *a, **k):
        raise AssertionError("a request was made")


class Ceilings(unittest.TestCase):
    def budget(self, **over):
        d = tempfile.mkdtemp(prefix="erw155_")
        return w.Budget(d, **over), d

    def test_the_ceilings_are_the_owners(self):
        self.assertEqual((w.CEILING_ROWS, w.CEILING_REQUESTS, w.CEILING_BYTES, w.CEILING_LISTINGS_OTHER), (1_500_000, 1_500, 3 * 1024 ** 3, 60))   # session 165: the owner's ceiling for the third pull, the lowest of the three (160: 2,000,000)
        self.assertGreaterEqual(w.ARCHIVE_PAUSE, 2.0)   # one request every two seconds to the Archive at most

    def test_a_request_past_the_request_ceiling_is_refused_before_it_is_made(self):
        b, d = self.budget(requests=2)
        b.spend("https://web.archive.org/a", "capture", "200", 10)
        b.spend("https://web.archive.org/b", "capture", "200", 10)
        net = w.Net(b, lambda m: None, sleep=lambda s: None)
        net.session = NoSession()
        with self.assertRaises(w.Refused):
            net.get("https://web.archive.org/c", "capture")
        self.assertEqual(b.requests, 2)
        with open(os.path.join(d, "requests.csv"), encoding="utf-8") as f:
            self.assertEqual(len(f.readlines()), 3)   # the header and the two requests made: the refused one is not there

    def test_the_bytes_and_rows_ceilings_refuse_before_the_request(self):
        b, _ = self.budget(nbytes=1000)
        with self.assertRaises(w.Refused):   # one more answer could be larger than what is left
            b.ask("https://web.archive.org/x", "capture")
        b2, _ = self.budget(rows=w.ROWS_RESERVE - 1)
        with self.assertRaises(w.Refused):   # one more copy could hold more rows than are left
            b2.ask("https://web.archive.org/x", "capture", rows_reserve=w.ROWS_RESERVE)
        self.assertGreater(b2.ask("https://web.archive.org/x", "listing"), 0)   # a listing holds no row of a request

    def test_a_copy_fetched_and_not_yet_read_counts_as_the_most_a_copy_may_hold(self):
        b, d = self.budget()
        w.append_capture(d, dict(publisher="nyiso", original="https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx", capture="20260101000000",
                                 sha256="aa", file="nyiso/x.xlsx", status="200"))
        self.assertEqual(w.Budget(d).rows, w.ROWS_RESERVE)
        with open(os.path.join(d, "copies.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("publisher,sha256,file,date,rows,note\nnyiso,aa,nyiso/x.xlsx,2026-01-01,74,\n")
        self.assertEqual(w.Budget(d).rows, 74)

    def test_the_other_queues_listings_stop_at_sixty(self):
        b, _ = self.budget()
        for i in range(w.CEILING_LISTINGS_OTHER):
            b.ask(f"https://web.archive.org/cdx/search/cdx?url=example{i}.org", "listing of another queue")
            b.spend(f"https://web.archive.org/cdx/search/cdx?url=example{i}.org", "listing of another queue", "200", 3)
        with self.assertRaises(w.Refused):
            b.ask("https://web.archive.org/cdx/search/cdx?url=example.org", "listing of another queue")

    def test_miso_and_pjm_are_never_asked_not_even_through_the_archive(self):
        b, _ = self.budget()
        for url in ("https://www.misoenergy.org/x", "https://dataminer2.pjm.com/feed", "https://api.pjm.com/api/v1/x",
                    "https://web.archive.org/web/2024id_/https://www.misoenergy.org/queue.xlsx", "https://web.archive.org/cdx/search/cdx?url=pjm.com&matchType=domain"):
            with self.assertRaises(w.Refused, msg=url):
                b.ask(url, "capture")
        self.assertEqual(b.requests, 0)

    def test_a_429_is_waited_out_once_and_the_address_is_then_left(self):
        b, _ = self.budget()
        waits = []

        class Answer:
            status_code, headers, url = 429, {}, "https://web.archive.org/web/1id_/https://example.org/q.xlsx"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def iter_content(self, n):
                return iter(())

        class Once:
            calls = 0

            def get(self, url, **k):
                Once.calls += 1
                return Answer()

        net = w.Net(b, lambda m: None, sleep=waits.append)
        net.session = Once()
        status, content, _ = net.get(Answer.url, "capture")
        self.assertEqual((status, content), ("429", b""))
        self.assertIn(w.BACKOFF, waits)
        with self.assertRaises(w.Refused):   # not asked a second time
            net.get(Answer.url, "capture")
        self.assertEqual(Once.calls, 1)

    def test_the_contact_string_is_the_ruled_one_and_no_address_of_a_person_is_sent(self):
        self.assertEqual(w.CONTACT, "ERW research project, github.com/SamuelEnrique/erw")
        self.assertEqual(w.UA, {"User-Agent": w.CONTACT})
        code = src("warehouse", "connectors", "large_load_waits.py")
        self.assertNotRegex(code, r"[\w.+-]+" + AT + r"[\w-]+\.[a-z]{2,}")
        self.assertNotIn("anthropic", code.lower())   # no model or API call from this code
        self.assertNotIn("Mozilla", code)

    def test_only_the_queues_own_files_are_wanted(self):
        ok = w.WANTED["grantpud"]
        self.assertTrue(ok.search("https://www.grantpud.org/images/2026/Transmission-Queue/Transmission%20Queue%2020260730.pdf"))
        for other in ("https://www.grantpud.org/images/2026/Transmission-Queue/LGIA%20V1%2003122026.pdf",
                      "https://www.grantpud.org/images/2026/Transmission-Queue/GrantPUD_OATT_2026-06-22.pdf"):
            self.assertFalse(ok.search(other) and not w.NOT_WANTED.search(other), other)
        e = w.WANTED["ercot"]
        self.assertTrue(e.search("https://www.ercot.com/files/docs/2026/03/12/March-TAC-Report.pdf"))
        self.assertFalse(e.search("https://www.ercot.com/files/docs/2026/09/17/Tesla-comments-_-ERCOT-VRT-_-LLWG_9.17.26_vFinal.pdf"))


class FakeNet:
    """Stands where the network would be for the current copies: canned pages, and a list of what was asked."""
    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def get(self, url, kind, rows_reserve=0, timeout=120):
        self.asked.append((url, kind))
        return "200", self.pages.get(url, b"%PDF-1.7 made up for the test"), {}


class Captures(unittest.TestCase):
    def test_the_same_file_captured_twice_is_fetched_once_in_its_raw_form(self):
        d = tempfile.mkdtemp(prefix="erw155_")
        address = "https://www.grantpud.org/images/2026/Transmission-Queue/Transmission%20Queue%2020260730.pdf"
        listing = b'[["timestamp","original","mimetype","statuscode","digest","length"],' \
                  b'["20260801000000","' + address.encode() + b'","application/pdf","200","AAAA","10"],' \
                  b'["20260901000000","' + address.encode() + b'","application/pdf","200","AAAA","10"],' \
                  b'["20260915000000","' + address.encode() + b'","application/pdf","200","BBBB","10"],' \
                  b'["20260915000000","https://www.grantpud.org/images/2026/Transmission-Queue/LGIA%20V1.pdf","application/pdf","200","CCCC","10"]]'
        one_listing = [("grantpud", "grantpud.org", "domain", "(?i).*queue.*", "made up for the test")]
        net = FakeNet({w.cdx_url("grantpud.org", "domain", "(?i).*queue.*"): listing})
        w.do_list(d, net, lambda m: None, listings=one_listing)
        self.assertEqual(len(net.asked), 1)
        w.do_list(d, net, lambda m: None, listings=one_listing)   # already listed: not asked again
        self.assertEqual(len(net.asked), 1)
        counts = w.do_pull_archive(d, net, lambda m: None)
        fetched = [u for u, kind in net.asked if kind == "capture"]
        self.assertEqual(fetched, [f"https://web.archive.org/web/20260801000000id_/{address}", f"https://web.archive.org/web/20260915000000id_/{address}"])
        self.assertEqual((counts["grantpud"]["listed"], counts["grantpud"]["distinct"], counts["grantpud"]["fetched"]), (3, 2, 2))
        rows = w.read_captures(d)
        self.assertEqual([r["digest"] for r in rows], ["AAAA", "BBBB"])
        self.assertEqual(list(rows[0])[:9], ["publisher", "original", "capture", "archive_url", "digest", "bytes", "sha256", "retrieved_at", "status"])
        w.do_pull_archive(d, net, lambda m: None)   # a second run asks for nothing
        self.assertEqual(len([u for u, kind in net.asked if kind == "capture"]), 2)


class CurrentCopies(unittest.TestCase):
    def test_only_the_queue_is_asked_for_among_the_files_a_page_links(self):
        d = tempfile.mkdtemp(prefix="erw155_")
        grant = (b'<a href="/images/2026/Transmission-Queue/GrantPUD_OATT_2026-06-22.pdf">tariff</a>'
                 b'<a href="/images/2026/Transmission-Queue/LGIA%20V1%2003122026.pdf">agreement</a>'
                 b'<a href="/images/2026/Transmission-Queue/Transmission Queue 20260730.pdf">queue</a>')
        llwg = b'<a href="/calendar/09172026-LLWG-Meeting">meeting</a> <a href="/calendar/01012099-LLWG-Meeting">a meeting to come</a>'
        meeting = (b'<a href="/files/docs/2026/09/17/Some-comments-_-LLWG_9.17.26.pdf">comments</a>'
                   b'<a href="/files/docs/2026/09/16/September-TAC-Report.pdf">status</a>')
        net = FakeNet({w.CURRENT["grantpud_page"]: grant, w.CURRENT["ercot_pages"][0]: llwg, w.CURRENT["ercot_pages"][1]: b"<p>no meeting listed</p>",
                       w.CURRENT["ercot_pages"][2]: b"<p>no meeting listed</p>", w.CURRENT["ercot_pages"][3]: b"<p>no report linked</p>",
                       "https://www.ercot.com/calendar/09172026-LLWG-Meeting": meeting})
        w.do_pull_current(d, net, lambda m: None)
        asked = [u for u, _ in net.asked]
        self.assertIn(w.CURRENT["nyiso"], asked)
        self.assertIn("https://www.grantpud.org/images/2026/Transmission-Queue/Transmission%20Queue%2020260730.pdf", asked)
        self.assertIn("https://www.ercot.com/files/docs/2026/09/16/September-TAC-Report.pdf", asked)
        for other in ("OATT", "LGIA", "Some-comments", "01012099"):
            self.assertFalse([u for u in asked if other in u], other)
        # the workbook; Grant's page and its queue; ERCOT's four pages (session 160: two more), one meeting and one report;
        # session 165: Bonneville's workbook and Alberta's page (which links no monthly list here, so no list is asked for)
        self.assertEqual(len(asked), 11)
        self.assertEqual([u for u in asked if "bpa.gov" in u or "aeso.ca" in u], [w.CURRENT["bpa"], w.CURRENT["aeso_page"]])
        rows = w.read_captures(d)
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(len(r["sha256"]) == 64 and r["retrieved_at"] and r["status"] == "200" for r in rows))

    def test_a_terms_quote_that_is_not_in_the_saved_page_fails_the_stage(self):
        d = tempfile.mkdtemp(prefix="erw155_")
        whole = {t["ask"]: ("<p>" + " ".join(t["quotes"]) + "</p>").encode("utf-8") for t in w.TERMS.values() if t["ask"]}
        w.do_terms(d, FakeNet(whole), lambda m: None)
        saved = {t["name"]: t for t in w.terms_saved(d)}
        self.assertTrue(all(ok for _, ok in saved["ercot"]["quotes"]))
        self.assertEqual(len(saved["ercot"]["sha256"]), 64)
        self.assertEqual(saved["nyiso"]["file"], "")   # saved by another session's connector: not on this made-up machine, and never asked for here
        d2 = tempfile.mkdtemp(prefix="erw155_")
        with self.assertRaises(RuntimeError):
            w.do_terms(d2, FakeNet({t["ask"]: b"<p>a page that says something else</p>" for t in w.TERMS.values() if t["ask"]}), lambda m: None)


class Following(unittest.TestCase):
    def copies(self, *copies):
        return [dict(publisher="nyiso", date=day, stamp=day, url="https://web.archive.org/web/x", file=day, rows=rows) for day, rows in copies]

    def row(self, rid, code="4", qd="2020-01-10", mw="100"):
        return dict(id=rid, id_printed=rid, name="made up", developer="", mw=mw, queue_date_printed=qd, queue_date=qd, status_code=code, status_words=KEY[code], sheet="made up")

    def test_a_request_is_followed_by_its_identifier_and_one_copy_is_not_enough(self):
        followed, not_followed = w.follow(self.copies(("2021-01-01", [self.row("T1"), self.row("T2")]), ("2021-06-01", [self.row("T1", "5")])))
        self.assertEqual(list(followed), [("nyiso", "T1")])
        self.assertEqual([(n["id"], n["why"]) for n in not_followed], [("T2", "seen in one copy only")])

    def test_an_ambiguous_identifier_is_not_followed(self):
        followed, not_followed = w.follow(self.copies(("2021-01-01", [self.row("T1"), self.row("T1", "6")]), ("2021-06-01", [self.row("T1", "6")])))
        self.assertEqual(followed, {})
        self.assertIn("two rows of one copy", not_followed[0]["why"])
        followed, not_followed = w.follow(self.copies(("2021-01-01", [self.row("T3")]), ("2021-06-01", [self.row("T3", qd="2019-05-05")])))
        self.assertEqual(followed, {})
        self.assertIn("queue date printed for it differs", not_followed[0]["why"])

    def test_the_identifier_is_the_position_as_printed_without_leading_zeros(self):
        self.assertEqual({w.request_id(x) for x in ("123", "0123", 123.0, 123)}, {"123"})
        self.assertEqual(w.request_id("0045a"), "45A")
        self.assertNotEqual(w.request_id("45A"), w.request_id("45"))

    def test_megawatts_are_kept_as_written_and_a_change_is_recorded(self):
        obs = seen("T1", ("2021-01-01", "4"), ("2021-06-01", "4"), ("2022-01-01", "5"))
        obs[2]["mw"] = "88"
        r = w.durations("nyiso", "T1", obs, "2022-01-01")[0]
        self.assertEqual((r["mw_first"], r["mw_last"]), ("100", "88"))
        self.assertEqual(r["mw_as_written_changes"], "2021-01-01: 100; 2022-01-01: 88")
        self.assertEqual(r["size_class"], "20 to under 100 MW")
        self.assertEqual([w.size_class(x) for x in ("19.9", "20", "99", "100", "299.9", "300", "")],
                         ["under 20 MW", "20 to under 100 MW", "20 to under 100 MW", "100 to under 300 MW", "100 to under 300 MW", "300 MW and over", "megawatts not a number"])


class Durations(unittest.TestCase):
    def test_a_request_seen_in_two_copies_only_gives_a_lower_bound_and_is_labeled(self):
        # the two copies even show it entering service: the brief's rule is that two copies give a lower bound, labeled
        rows = w.durations("nyiso", "T1", seen("T1", ("2021-01-01", "12"), ("2021-06-01", "14")), "2021-06-01")
        self.assertTrue(rows)
        for r in rows:
            self.assertEqual(r["label"], "two copies only", r["interval"])
            self.assertEqual(r["days_at_most"], "")
            self.assertNotEqual(r["days_at_least"], "")
            self.assertEqual(r["copies_seen"], 2)
        still = w.durations("nyiso", "T2", seen("T2", ("2021-01-01", "4"), ("2021-06-01", "4")), "2021-06-01")
        r = one(still, "request to energized")
        self.assertEqual((r["label"], r["days_at_least"], r["days_at_most"]), ("two copies only", (w.dt.date(2021, 6, 1) - w.dt.date(2020, 1, 10)).days, ""))

    def test_a_duration_is_a_range_between_its_bounds_and_never_a_midpoint(self):
        # request T1 (made up): queue date printed 10 January 2020; in a study status on 1 March 2020 and 1 September 2020;
        # in service in the copy of 1 March 2021
        obs = seen("T1", ("2020-03-01", "4"), ("2020-09-01", "4"), ("2021-03-01", "14"))
        r = one(w.durations("nyiso", "T1", obs, "2021-03-01"), "request to energized")
        least, most = (w.dt.date(2020, 9, 1) - w.dt.date(2020, 1, 10)).days, (w.dt.date(2021, 3, 1) - w.dt.date(2020, 1, 10)).days
        self.assertEqual((r["label"], r["days_at_least"], r["days_at_most"]), ("measured", least, most))
        self.assertEqual((r["end_earlier_date"], r["end_later_date"]), ("2020-09-01", "2021-03-01"))   # both copies are on the row
        self.assertTrue(r["end_earlier_url"].startswith("https://web.archive.org/") and r["end_later_url"].startswith("https://web.archive.org/"))
        self.assertEqual((r["start_earlier_date"], r["start_later_date"], r["start_later_basis"]), ("2020-01-10", "2020-01-10", "the queue date the copies print"))
        mid = (least + most) / 2
        self.assertNotIn(mid, (r["days_at_least"], r["days_at_most"]))
        self.assertNotIn("2020-12-01", (r["event_date"], r["end_earlier_date"], r["end_later_date"]))   # no day between the copies is written
        # the function itself: at least is the later start to the earlier end, at most the earlier start to the later end
        S = ({"date": "2020-01-01", "url": "u", "kind": "copy"}, {"date": "2020-02-01", "url": "u", "kind": "copy"})
        E = ({"date": "2020-06-01", "url": "u", "kind": "copy"}, {"date": "2020-08-01", "url": "u", "kind": "copy"})
        last = {"date": "2020-12-01", "url": "u", "kind": "copy"}
        self.assertEqual(w.measure(S, E, last, 5), (121, 213, "measured"))
        self.assertEqual(w.measure(S, None, last, 5), (304, None, "lower bound"))
        self.assertEqual(w.measure((None, S[1]), E, last, 5), (121, None, "lower bound"))     # the start is bounded on one side only
        self.assertEqual(w.measure(S, (None, E[1]), last, 5), (None, 213, "upper bound"))     # the end had come before the first copy
        self.assertIsNone(w.measure((None, None), (None, E[1]), last, 5))
        self.assertEqual(w.measure(S, E, last, 2), (121, None, "two copies only"))
        code = src("warehouse", "connectors", "large_load_waits.py")
        self.assertNotRegex(code, r"(?i)\binterpolat(e|ed|ion)\(|/ 2\.0|midpoint\s*=")

    def test_a_stage_already_reached_in_the_first_copy_is_an_upper_bound_not_a_measure(self):
        # in service in the first copy that holds it: only "at most" can be said of its wait
        rows = w.durations("nyiso", "T1", seen("T1", ("2021-01-01", "14"), ("2021-06-01", "14"), ("2022-01-01", "14"), qd="2015-01-01"), "2022-01-01")
        r = one(rows, "request to energized")
        self.assertEqual((r["label"], r["days_at_least"]), ("upper bound", ""))
        self.assertEqual(r["days_at_most"], (w.dt.date(2021, 1, 1) - w.dt.date(2015, 1, 1)).days)

    def test_a_request_not_yet_energized_gives_a_lower_bound_only(self):
        rows = w.durations("nyiso", "T1", seen("T1", ("2021-01-01", "1"), ("2021-06-01", "4"), ("2022-01-01", "5")), "2022-01-01")
        r = one(rows, "request to energized")
        self.assertEqual((r["label"], r["days_at_most"]), ("lower bound", ""))
        self.assertEqual(r["days_at_least"], (w.dt.date(2022, 1, 1) - w.dt.date(2020, 1, 10)).days)
        study = one(rows, "request to study")
        self.assertEqual((study["label"], study["end_earlier_date"], study["end_later_date"]), ("measured", "2021-01-01", "2021-06-01"))

    def test_a_stage_is_counted_only_where_a_copy_shows_it(self):
        # from a study status straight to in service: no agreement is read into the request
        rows = w.durations("nyiso", "T1", seen("T1", ("2021-01-01", "4"), ("2021-06-01", "6"), ("2022-01-01", "14")), "2022-01-01")
        kinds = {r["interval"] for r in rows}
        self.assertNotIn("request to agreement", kinds)
        self.assertNotIn("study to agreement", kinds)
        self.assertNotIn("agreement to energized", kinds)
        self.assertNotIn("request to construction", kinds)
        self.assertIn("request to energized", kinds)
        shown = w.durations("nyiso", "T2", seen("T2", ("2021-01-01", "4"), ("2021-06-01", "11"), ("2022-01-01", "12"), ("2022-06-01", "14")), "2022-06-01")
        self.assertEqual(one(shown, "study to agreement")["label"], "measured")
        self.assertEqual(one(shown, "agreement to energized")["end_as_worded"], "In Service Commercial")

    def test_a_withdrawn_request_gives_no_lower_bound_for_a_stage_it_never_reached(self):
        rows = w.durations("nyiso", "T1", seen("T1", ("2021-01-01", "4"), ("2021-06-01", "4"), ("2022-01-01", "0")), "2022-01-01")
        kinds = {r["interval"] for r in rows}
        self.assertNotIn("request to energized", kinds)
        self.assertEqual(one(rows, "request to withdrawal")["end_as_worded"], "Withdrawn")
        self.assertEqual(one(rows, "in stage, then withdrawn", "SRIS/SIS Pending")["label"], "measured")

    def test_the_stage_words_are_kept_beside_their_class(self):
        rows = w.durations("nyiso", "T1", seen("T1", ("2021-01-01", "1"), ("2021-06-01", "4"), ("2022-01-01", "12")), "2022-01-01")
        r = one(rows, "in stage", "SRIS/SIS Pending")
        self.assertEqual((r["stage_as_worded"], r["stage_class"], r["stage_code"]), ("SRIS/SIS Pending", "2 study or engineering", "4"))
        self.assertEqual([w.stage_class(x)[0][:1] for x in ("Scoping Meeting Pending", "FS in Progress", "Accepted Cost Allocation/IA in Progress", "IA Completed",
                                                           "Under Construction", "In Service for Test", "Construction Agreement Signed", "Facility Study Completed")],
                         ["1", "2", "3", "4", "5", "5", "4", "2"])
        self.assertEqual(w.stage_class("Withdrawn")[0], "none")
        self.assertEqual(w.stage_class("Removed from Queue")[0], "none")


class Figures(unittest.TestCase):
    def rows(self, n, label="measured"):
        return [dict(label=label, days_at_least=100 + 10 * i, days_at_most=200 + 10 * i, entity="E", interval="request to energized", stage_as_worded="",
                     stage_class="", size_class="100 to under 300 MW") for i in range(n)]

    def test_a_figure_on_fewer_than_five_requests_is_its_values_and_not_a_median(self):
        self.assertEqual(w.MIN_FOR_MEDIAN, 5)
        f = w.figure(self.rows(4))
        self.assertEqual((f["measured_n"], f["measured_median_at_least"], f["measured_median_at_most"]), (4, "", ""))
        self.assertEqual(f["measured_values"], "100 to 200; 110 to 210; 120 to 220; 130 to 230")
        g = w.figure(self.rows(5))
        self.assertEqual((g["measured_n"], g["measured_median_at_least"], g["measured_median_at_most"], g["measured_values"]), (5, 120, 220, ""))
        self.assertEqual(g["measured_range"], "100 to 240")

    def test_lower_bounds_are_counted_apart_and_never_averaged(self):
        f = w.figure(self.rows(6, "lower bound") + self.rows(2))
        self.assertEqual((f["measured_n"], f["lower_bound_n"], f["lower_bound_range"]), (2, 6, "100 to 150"))
        self.assertEqual(f["measured_median_at_least"], "")   # two measured: no median, whatever the count of lower bounds
        self.assertFalse([k for k in f if "mean" in k or "average" in k or ("median" in k and "lower" in k)])
        two = w.figure(self.rows(3, "two copies only"))
        self.assertEqual((two["measured_n"], two["lower_bound_n"], two["two_copies_only_n"]), (0, 0, 3))

    def test_the_comparison_never_ranks_and_says_where_none_can_be_made(self):
        rows = [dict(entity_group="New York ISO", interval=w.SIS_WHOLE[0], stage_as_worded="", label=lab, days_at_least=a, days_at_most=b)
                for lab, a, b in (("measured", 300, 400), ("measured", 100, 200), ("measured", 250, 300), ("lower bound", 500, ""), ("lower bound", 10, ""))]
        rows.append(dict(entity_group="Grant County Public Utility District", interval="request to energized", stage_as_worded="", label="lower bound", days_at_least=9, days_at_most=""))
        stated = [dict(wait_figure="New York ISO | 9 month | 2 | large loads", quantity_as_written="nine months", wait_basis="expected", wait_counted="yes", load_scope="large loads"),
                  dict(wait_figure="New York ISO | 2 week | 1 | large loads", quantity_as_written="2 weeks", wait_basis="expected", wait_counted="yes", load_scope="large loads"),
                  dict(wait_figure="New York ISO | 1 year | 2 | large loads", quantity_as_written="one year", wait_basis="measured", wait_counted="yes", load_scope="large loads")]
        out, none = w.compare(rows, stated)
        self.assertEqual(none, ["Grant County Public Utility District"])
        whole = [x for x in out if x["stated_as_written"] == "nine months" and x["measured_interval"] == w.SIS_WHOLE[0]][0]
        self.assertEqual((whole["measured_n"], whole["above"], whole["below"], whole["inside"]), (3, 1, 1, 1))
        self.assertEqual((whole["lower_bounds_n"], whole["lower_bounds_already_longer"]), (2, 1))
        weeks = [x for x in out if x["stated_as_written"] == "2 weeks"]
        self.assertEqual(len(weeks), 1)
        self.assertTrue(weeks[0]["comparison"].startswith("no comparison"))
        self.assertFalse([x for x in out if x["stated_as_written"] == "one year"])   # a measured statement is not an expectation
        self.assertFalse([k for x in out for k in x if "rank" in k])


class Copies(unittest.TestCase):
    def test_a_copy_is_dated_by_its_publisher_never_by_its_capture(self):
        code = src("warehouse", "connectors", "large_load_waits.py")
        self.assertIn("never by the day the Archive happened to capture it", code)
        self.assertEqual(w.http_day("Fri, 11 Sep 2026 17:26:02 GMT"), ("2026-09-11", "2026-09-11T17:26:02Z"))
        self.assertEqual(w.http_day(""), ("", ""))
        self.assertEqual(w.workbook_saved(os.path.join(ROOT, "CLAUDE.md")), ("", ""))   # not a workbook: no date is made up

    def test_a_date_is_read_only_where_the_cell_holds_one(self):
        self.assertEqual(w.iso_day("4/19/2019"), "2019-04-19")
        self.assertEqual(w.iso_day(w.dt.datetime(2016, 9, 27)), "2016-09-27")
        self.assertEqual([w.iso_day(x) for x in ("11-2026", "I/S", "", None, "TBD")], ["", "", "", "", ""])

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_the_saved_copies_are_read_and_no_status_goes_backwards_for_want_of_a_date(self):
        b, counts = built()
        self.assertGreaterEqual(counts["copies"]["New York ISO"]["read"], 37)
        self.assertGreaterEqual(counts["copies"]["Grant County Public Utility District"]["read"], 5)
        dates = [c["stamp"] for c in b["copies"] if c["publisher"] == "nyiso"]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(len(dates), len(set(dates)))
        for c in b["copies"]:
            self.assertRegex(c["date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(c["url"].startswith("https://"), c["url"])

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_every_row_holds_its_bounds_and_its_label(self):
        b, counts = built()
        self.assertEqual(counts["rows"], len(b["rows"]))
        self.assertEqual(sum(counts["rows_by_label"].values()), len(b["rows"]))
        for r in b["rows"]:
            self.assertIn(r["label"], w.LABELS)
            self.assertTrue(r["source_url"].startswith("https://"), r["source_url"])
            if r["label"] == "measured":
                self.assertNotIn("", (r["start_earlier_date"], r["start_later_date"], r["end_earlier_date"], r["end_later_date"]), r["event_id"])
                self.assertEqual((r["end_earlier_basis"], r["end_later_basis"]), ("a copy", "a copy"))
                self.assertLessEqual(r["days_at_least"], r["days_at_most"])
                self.assertEqual(r["days_at_least"], max(0, w.days(r["start_later_date"], r["end_earlier_date"])))
                self.assertEqual(r["days_at_most"], w.days(r["start_earlier_date"], r["end_later_date"]))
                self.assertGreater(r["copies_seen"], 2)
            elif r["label"] in ("lower bound", "two copies only"):
                self.assertEqual(r["days_at_most"], "")
                self.assertNotEqual(r["days_at_least"], "")
            else:
                self.assertEqual(r["days_at_least"], "")
            if r["label"] == "two copies only":
                self.assertEqual(r["copies_seen"], 2)
        self.assertEqual(len({r["event_id"] for r in b["rows"]}), len(b["rows"]))
        self.assertEqual(counts["requests"]["New York ISO"]["followed"] + sum(counts["requests"]["New York ISO"]["not_followed"].values()), counts["requests"]["New York ISO"]["seen"])


class Summary(unittest.TestCase):
    PAGE = ("docs", "accelerator", "large_load_waits.md")

    def test_the_page_exists_is_pointed_to_and_holds_no_em_dash(self):
        page = src(*self.PAGE)
        self.assertIn("(large_load_waits.md)", src("docs", "accelerator", "large_load_eighty.md").split("\n## ")[0])
        for rel in (self.PAGE, ("warehouse", "connectors", "large_load_waits.py"), ("tests", "test_session155.py")):
            self.assertNotIn(EM_DASH, src(*rel), rel)
        self.assertIn("internal", page)
        self.assertIn("never a midpoint", page)
        for t in w.TERMS.values():   # each terms quote is on the page word for word
            for q in t["quotes"]:
                self.assertIn(q, page, t["who"])

    def test_no_nyiso_megawatt_stands_on_the_page(self):
        page = src(*self.PAGE)
        for line in page.split("\n"):
            if "New York ISO" in line or "NYISO" in line:
                self.assertNotRegex(line, r"\d[\d,.]*\s*(MW|megawatts)\b", line[:80])

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_the_summarys_counts_equal_the_tables(self):
        b, counts = built()
        page = src(*self.PAGE)
        stated = dict(re.findall(r"\*\*([^*\n]+)\*\*: \d+ dated copies read, \d{4}-\d{2}-\d{2} to (\d{4}-\d{2}-\d{2})", page))   # session 165: every entity followed, whatever its name
        self.assertEqual(set(stated), set(counts["copies"]))
        if any(counts["copies"][e]["last"] != stated[e] for e in stated):
            self.skipTest("the raw store holds a newer copy than the page was written from: write the page again from --summary")
        for line in w.summary_lines(counts) + w.comparison_lines(counts):
            self.assertIn(line, page)

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_no_nyiso_request_is_named_in_a_tracked_file(self):
        b, _ = built()
        names = set()
        for c in b["copies"]:
            if c["publisher"] == "nyiso":
                for r in c["rows"]:
                    names.update(x for x in (r["name"],) if len(x) >= 10 and " " in x)   # a project's name of two words or more
        self.assertGreater(len(names), 40)
        for rel in (self.PAGE, ("warehouse", "connectors", "large_load_waits.py"), ("tests", "test_session155.py"), ("docs", "accelerator", "large_load_eighty.md")):
            text = src(*rel).lower()
            hit = [n for n in names if n.lower() in text]
            self.assertFalse(hit, f"{'/'.join(rel)} names {len(hit)} of NYISO's requests")


if __name__ == "__main__":
    unittest.main()
