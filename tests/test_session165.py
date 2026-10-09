"""Session 165: more queues followed (warehouse/connectors/large_load_waits.py). Bonneville Power Administration's
interconnection queue workbook and the Alberta Electric System Operator's monthly project list (CANADA) are read by
session 155's method and appended to large_load_waits; ISO New England's posted queue holds no load and gives no row.

What is held here: only the queue's own file is wanted; Alberta is sampled one capture a month, the first month of a
quarter first; a copy is dated by its publisher (the stamp Bonneville prints, the day Alberta's workbook was saved)
and a file saved again long after its month is not used; only the publisher's own mark makes a row a load; a status
word the publisher does not explain is placed on no class and gives no lower bound to a milestone; Canada's figures
stand apart; the rows held before this session come out byte for byte; no request of the new publishers is named in
a tracked file.

Every request, project and workbook in this file is MADE UP FOR THE TEST. The tests that need the saved copies or the
table skip on a machine without them (neither is in the repository): they look under warehouse/raw and
warehouse/output of this copy, or where the environment variables ERW_RAW_ROOT and ERW_WAITS_TABLE point. No request
and no model call. The module reads the environment and never sets it."""
import csv
import datetime as dt
import hashlib
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_waits as w  # noqa: E402

EM_DASH = chr(0x2014)
PAGE = ("docs", "accelerator", "large_load_waits.md")
METHOD = ("docs", "methods", "large_load_waits.md")
BPA = "Bonneville Power Administration"
AESO = "Alberta Electric System Operator (Canada)"
OLD = ("New York ISO", "Grant County Public Utility District")
# the rows held before this session (New York ISO 486, Grant County PUD 5), as the table of 8 October 2026 wrote them:
# the sha256 of those lines in the table's order, each with its line end. A hash names no request.
OLD_ROWS = 491
OLD_SHA256 = "0ffba5f56e924f796d17689d1662bf43b9be772d28236191ea171516820dfbbf"
OLD_RETRIEVED = {"nyiso": "2026-10-08T08:47:50Z", "grantpud": "2026-10-08T08:48:30Z"}
BUILT = {}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw_root():
    """The directory that holds large_load_waits/captures.csv, or None. Reads the environment, never sets it."""
    for d in (os.environ.get("ERW_RAW_ROOT"), os.path.join(ROOT, "warehouse", "raw")):
        if d and os.path.exists(os.path.join(d, "large_load_waits", "captures.csv")):
            return d
    return None


def table_path():
    """The table on this machine, or None: where ERW_WAITS_TABLE points, else this copy's warehouse/output."""
    for p in (os.environ.get("ERW_WAITS_TABLE"), os.path.join(ROOT, "warehouse", "output", "large_load_waits.csv")):
        if p and os.path.exists(p):
            return p
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


def workbook(rows, name="Sheet1"):
    """A made-up .xlsx workbook of one sheet in a new temporary file; its path."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = name
    for r in rows:
        ws.append(r)
    fd, path = tempfile.mkstemp(prefix="erw165_", suffix=".xlsx")
    os.close(fd)
    wb.save(path)
    return path


def seen(words, day, rid="L9001", qd="2020-01-10", mw="50", code=""):
    return dict(id=rid, id_printed=rid, name="made up for the test", developer="", mw=mw, queue_date_printed=qd, queue_date=qd, status_code=code,
                status_words=words, sheet="made up", date=day, stamp=day,
                url=f"https://web.archive.org/web/{day.replace('-', '')}000000id_/https://example.org/queue.xlsx", file="x")


class FakeNet:
    """Stands where the network would be: canned pages, and a list of what was asked."""
    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def get(self, url, kind, rows_reserve=0, timeout=120):
        self.asked.append((url, kind))
        return "200", self.pages.get(url, b"<p>nothing linked</p>"), {}


class Pull(unittest.TestCase):
    def test_the_rows_ceiling_is_the_owners_for_this_pull_and_the_contact_is_the_ruled_one(self):
        self.assertEqual((w.CEILING_ROWS, w.CEILING_REQUESTS, w.CEILING_BYTES), (1_500_000, 1_500, 3 * 1024 ** 3))
        self.assertEqual(w.UA, {"User-Agent": "ERW research project, github.com/SamuelEnrique/erw"})
        self.assertNotIn(chr(64), w.CONTACT)
        self.assertGreaterEqual(w.ARCHIVE_PAUSE, 2.0)
        b = w.Budget(tempfile.mkdtemp(prefix="erw165_"))
        for url in ("https://www.misoenergy.org/x.xlsx", "https://web.archive.org/web/1id_/https://www.pjm.com/queue.xlsx", "https://dataminer2.pjm.com/feed"):
            with self.assertRaises(w.Refused):
                b.ask(url, "capture")
        self.assertEqual(b.requests, 0)

    def test_only_the_queues_own_file_is_wanted(self):
        ok = w.WANTED["bpa"]
        for good in ("https://www.bpa.gov/-/media/Aep/transmission-media-documents/InterconnectionQueueOutput.xlsx",
                     "http://transmission.bpa.gov:80/business/generation_interconnection/InterconnectionQueueOutput.xls"):
            self.assertTrue(ok.search(good) and not w.NOT_WANTED.search(good), good)
        for other in ("https://www.bpa.gov/-/media/Aep/transmission/transmission-availability/ltf-pending-queue.xlsx",
                      "https://www.bpa.gov/-/media/Aep/transmission/interconnection/generator-interconnection-queue-reform-faq.pdf",
                      "http://www.transmission.bpa.gov:80/Business/Reserve_and_Schedule_Transmission/Documents/PendingQueue.xls"):
            self.assertFalse(ok.search(other), other)
        ok = w.WANTED["aeso"]
        for good in ("https://www.aeso.ca/assets/Uploads/project-reporting/April-2023-Project-List.xlsx", "https://www.aeso.ca/assets/Uploads/Final-June-2018-Project-List.xls"):
            self.assertTrue(ok.search(good), good)
        for other in ("https://www.aeso.ca/assets/AESO-Connection-Project-List-Guide.pdf", "https://www.aeso.ca/assets/Uploads/project-reporting/Cluster-2-Project-List-Results.pdf"):
            self.assertFalse(ok.search(other), other)

    def test_alberta_is_sampled_one_capture_a_month_the_quarters_first(self):
        base = "https://www.aeso.ca/assets/Uploads/project-reporting/"
        caps = [dict(timestamp=ts, original=base + name, digest=ts) for ts, name in (
            ("20240105000000", "February-2023-Project-List.xlsx"), ("20240101000000", "January-2023-Project-List.xlsx"),
            ("20250101000000", "January-2023-Project-List.xlsx"), ("20240103000000", "April-2023-Project-List.xlsx"),
            ("20240104000000", "Final-March-2019-Project-List.xlsx"), ("20240106000000", "AESO-Connection-Project-List-Guide.pdf"))]
        got = w.aeso_sample(caps)
        self.assertEqual([w.aeso_month(c["original"]) for c in got], [(2023, 1), (2023, 4), (2019, 3), (2023, 2)])   # a quarter's first month before the others
        self.assertEqual(got[0]["timestamp"], "20250101000000")   # the latest capture of a month's file
        self.assertEqual(w.aeso_month(base + "December-1-2022-Project-List.xlsx"), (2022, 12))
        self.assertIsNone(w.aeso_month(base + "Project-List.xlsx"))

    def test_the_listings_session_155_saved_are_the_listings_of_these_queues(self):
        self.assertEqual(w.LISTED_AS, {"other-bpa2": "bpa", "other-bpa3": "bpa", "other-aeso": "aeso"})
        self.assertEqual([x for x in w.OTHER_QUEUES if x[0] not in w.LISTED_AS], [])   # nothing of session 155's list is left to follow next

    def test_the_current_copies_are_the_one_workbook_and_the_newest_month_and_no_other(self):
        d = tempfile.mkdtemp(prefix="erw165_")
        page = (b'<a href="/assets/Uploads/project-reporting/August-2026-Project-List.xlsx">a</a>'
                b'<a href="/assets/Uploads/project-reporting/September-2026-Project-List.xlsx">b</a>'
                b'<a href="/assets/Uploads/project-reporting/December-2025-Project-List.xlsx">c</a>'
                b'<a href="/assets/AESO-Connection-Project-List-Guide-v2.pdf">guide</a><a href="/legal/">legal</a>')
        net = FakeNet({w.CURRENT["aeso_page"]: page})
        w.do_pull_current(d, net, lambda m: None, None, {"bpa", "aeso"})
        asked = [u for u, _ in net.asked]
        self.assertEqual(asked, [w.CURRENT["bpa"], w.CURRENT["aeso_page"], "https://www.aeso.ca/assets/Uploads/project-reporting/September-2026-Project-List.xlsx"])
        self.assertTrue(w.WANTED["bpa"].search(w.CURRENT["bpa"]))
        net2 = FakeNet({})
        w.do_pull_current(d, net2, lambda m: None, None, {"grantpud"})   # a publisher not named is not asked
        self.assertFalse([u for u, _ in net2.asked if "bpa.gov" in u or "aeso.ca" in u])

    def test_only_the_named_publishers_terms_are_asked_for(self):
        d = tempfile.mkdtemp(prefix="erw165_")
        pages = {t["ask"]: ("<p>" + " ".join(t["quotes"]) + "</p>").encode("utf-8") for t in w.TERMS.values() if t["ask"]}
        net = FakeNet(pages)
        w.do_terms(d, net, lambda m: None, {"bpa", "aeso"})
        self.assertEqual([u for u, _ in net.asked], [w.TERMS["bpa"]["ask"], w.TERMS["aeso"]["ask"]])
        for name in ("bpa", "aeso", "isone"):
            self.assertGreaterEqual(len(w.TERMS[name]["quotes"]), 2, name)
            self.assertNotIn(EM_DASH, " ".join(w.TERMS[name]["quotes"]))


class Bonneville(unittest.TestCase):
    HEAD = ["Request Number", "Request Date", "Project Name", "Requestor", "Comments", "Point Of Interconnection", "Status", "State", "County",
            "Connection Type", "Requested In-Service Date", "Agreed To: (Blank=TBD)", "Max Summer MW", "Max Winter MW"]

    def book(self, stamp):
        return workbook([
            [None, None, None, "Bonneville Power Administration Interconnection Request Queue", None, None, None, None, stamp],
            ["Note: MADE UP FOR THE TEST."],
            self.HEAD,
            ["L9001", dt.datetime(2020, 1, 10), "made up load one", "made up utility", "", "made up substation", "STUDY", "", "", "LL", None, None, 50, 50],
            ["G9002", dt.datetime(2020, 2, 11), "", "", "", "made up line", "RECEIVED", "OR", "", "GI", None, None, 100, 100],
            ["L9003", dt.datetime(2021, 3, 12), "made up load two", "made up utility", "", "made up tap", "CONST AGRMT EXE", "", "", "LL", None, None, None, None],
        ])

    def test_only_the_rows_bonneville_marks_ll_are_read_and_the_copy_is_dated_by_its_printed_stamp(self):
        for stamp, want in ((dt.datetime(2024, 11, 28, 16, 1, 6), ("2024-11-28", "2024-11-28T16:01:06")), ("03/19/2013 09:06", ("2013-03-19", "2013-03-19T09:06:00"))):
            path = self.book(stamp)
            rows, notes, day, full = w.read_bpa(path)
            os.remove(path)
            self.assertEqual((day, full), want)
            self.assertEqual([r["id"] for r in rows], ["L9001", "L9003"])   # the generator (GI) is not a load request
            self.assertEqual([r["status_words"] for r in rows], ["STUDY", "CONST AGRMT EXE"])   # the publisher's words, kept
            self.assertEqual([(r["queue_date"], r["mw"]) for r in rows], [("2020-01-10", "50"), ("2021-03-12", "")])   # a blank megawatt cell stays blank
            self.assertIn("3 requests in the sheet, 2 of them of Connection Type LL", notes)

    def test_a_workbook_with_no_stamp_has_no_date_and_is_not_used(self):
        path = self.book(None)
        _, _, day, full = w.read_bpa(path)
        os.remove(path)
        self.assertEqual((day, full), ("", ""))

    def test_bonnevilles_words_are_placed_only_where_they_say_a_stage(self):
        got = {x: w.stage_class(x)[0] for x in ("RECEIVED", "STUDY", "STUDY COMPLETED", "E&P EXECUTED", "CONST AGRMT EXE", "ENERGIZED", "WITHDRAWN",
                                                "CONFIRMED", "COMPLETED", "BPA COMPLETED")}
        self.assertEqual(got, {"RECEIVED": w.STAGES[0], "STUDY": w.STAGES[1], "STUDY COMPLETED": w.STAGES[1], "E&P EXECUTED": w.STAGES[2],
                               "CONST AGRMT EXE": w.STAGES[3], "ENERGIZED": w.STAGES[4], "WITHDRAWN": w.NONE,
                               "CONFIRMED": "not classed", "COMPLETED": "not classed", "BPA COMPLETED": "not classed"})
        self.assertTrue(w.IN_SERVICE.search("ENERGIZED") and not w.IN_SERVICE.search("BPA COMPLETED") and not w.IN_SERVICE.search("COMPLETED"))

    def test_the_words_of_the_earlier_publishers_are_placed_as_before(self):
        before = {"Scoping Meeting Pending": w.STAGES[0], "SRIS/SIS Pending": w.STAGES[1], "SRIS/SIS in Progress": w.STAGES[1], "SRIS/SIS Approved": w.STAGES[1],
                  "FS in Progress": w.STAGES[1], "IA Completed": w.STAGES[3], "Under Construction": w.STAGES[4], "In Service Commercial": w.STAGES[4],
                  "Withdrawn": w.NONE, "Construction Agreement Signed": w.STAGES[3], "Accepted Cost Allocation/IA in Progress": w.STAGES[2], "": "not classed"}
        self.assertEqual({k: w.stage_class(k)[0] for k in before}, before)
        self.assertFalse(w.IN_SERVICE.search("Under Construction") or w.LEFT.search("In Service Commercial"))

    def test_a_request_is_followed_from_received_to_energized_as_ranges(self):
        obs = [seen("RECEIVED", "2020-02-01"), seen("STUDY", "2020-08-01"), seen("CONST AGRMT EXE", "2022-08-01"), seen("ENERGIZED", "2023-08-01")]
        rows = {r["interval"]: r for r in w.durations("bpa", "L9001", obs, "2023-08-01") if r["interval"].startswith(("request", "study", "agreement"))}
        self.assertEqual(set(rows), {"request to study", "request to agreement", "request to energized", "study to agreement", "agreement to energized"})
        r = rows["request to energized"]
        self.assertEqual((r["label"], r["days_at_least"], r["days_at_most"]), ("measured", w.days("2020-01-10", "2022-08-01"), w.days("2020-01-10", "2023-08-01")))
        self.assertEqual((r["entity"], r["source"]), (BPA, "bpa:interconnection_queue_dated_copies"))
        self.assertNotIn("request to construction", {x["interval"] for x in w.durations("bpa", "L9001", obs[:2], "2023-08-01")})   # Bonneville prints no construction status

    def test_a_request_still_waiting_gives_a_labeled_lower_bound(self):
        obs = [seen("RECEIVED", "2020-02-01"), seen("STUDY", "2020-08-01"), seen("STUDY", "2023-08-01")]
        r = next(x for x in w.durations("bpa", "L9001", obs, "2023-08-01") if x["interval"] == "request to energized")
        self.assertEqual((r["label"], r["days_at_least"], r["days_at_most"]), ("lower bound", w.days("2020-01-10", "2023-08-01"), ""))

    def test_words_the_publisher_does_not_explain_give_no_lower_bound_to_a_milestone(self):
        obs = [seen("STUDY", "2020-02-01"), seen("BPA COMPLETED", "2021-08-01"), seen("BPA COMPLETED", "2023-08-01")]
        rows = w.durations("bpa", "L9001", obs, "2023-08-01")
        self.assertFalse([r for r in rows if r["interval"] in ("request to energized", "request to agreement", "study to agreement")])
        stage = [r for r in rows if r["interval"] == "in stage" and r["stage_as_worded"] == "BPA COMPLETED"]
        self.assertEqual([(r["label"], r["stage_class"]) for r in stage], [("lower bound", "not classed")])   # the words kept, on no class
        # the same last words do not stop New York: the rule is Bonneville's alone
        self.assertFalse(w.ENTITIES["nyiso"].get("unclassed_stops") or w.ENTITIES["grantpud"].get("unclassed_stops"))


class Alberta(unittest.TestCase):
    def sections_book(self):
        return workbook([
            ["Project Information", None, None, None, None, None, None, "Energization 1"],
            ["Project Name", "Planning Area", "Project Type", "MW Type", "Stage", "Inclusion", "Applied On", "STS MW", "DTS MW", "ISD"],
            ["Active"],
            ["P9001 Made Up Load One", "01-Made Up", "Connection", "Load", 3, "No", dt.datetime(2020, 1, 10), 0, 25, dt.datetime(2027, 1, 1)],
            ["P9002 Made Up Solar", "01-Made Up", "Connection", "Solar", 2, "No", dt.datetime(2020, 2, 10), 40, 0, dt.datetime(2027, 1, 1)],
            ["P9003 Made Up Contract Change", "01-Made Up", "Contract", "DTS", 2, "No", dt.datetime(2020, 3, 10), 0, 9, dt.datetime(2027, 1, 1)],
            ["On Hold"],
            ["P9004 Made Up Load Two", "01-Made Up", "Connection", "Load", 2, "No", dt.datetime(2021, 4, 10), 0, 80, dt.datetime(2027, 1, 1)],
            ["Recently Energized"],
            ["P0905 Made Up Load Three", "01-Made Up", "Connection", "Load", 6, "No", dt.datetime(2019, 5, 10), 0, 12, dt.datetime(2021, 3, 1)],
            ["Recently Cancelled"],
            ["P9006 Made Up Load Four", "01-Made Up", "BTF", "Load", 2, "No", dt.datetime(2019, 6, 10), 0, 300, None],
            ["BTF denotes a behind the fence project and is not governed by the Connection Process. MADE UP FOR THE TEST."],
        ], name="Connection Project List")

    def test_only_the_lists_own_load_types_are_read_and_the_status_is_the_lists(self):
        path = self.sections_book()
        rows, notes = w.read_aeso(path)
        os.remove(path)
        self.assertEqual([(r["id"], r["status_words"], r["status_code"]) for r in rows],
                         [("9001", "Stage 3", "3"), ("9004", "Stage 2", "2"), ("905", "Recently Energized", "6"), ("9006", "Recently Cancelled", "2")])
        self.assertEqual([r["id_printed"] for r in rows], ["P9001", "P9004", "P0905", "P9006"])   # the number as printed is kept beside the identifier
        self.assertEqual([r["mw"] for r in rows], ["25", "80", "12", "300"])
        self.assertEqual(rows[1]["sheet"], "Connection Project List: On Hold")   # the section is kept, and is not a stage
        self.assertIn("6 projects' rows in the sheet Connection Project List, 4 of them of a load MW Type", notes)

    def test_the_status_column_of_2025_and_a_generator_with_a_load(self):
        path = workbook([
            ["Status", "Project Name", "Planning Area", "Cluster", "Project Type", "MW Type", "Stage", "CA Modelled", "Inclusion", "Applied On", "EN1 STS MW", "EN1 DTS MW", "EN1 ISD"],
            ["Active", "P9011 Made Up Data Centre", "01-Made Up", "", "Connection", "Data Load", 2, "Yes", "No", dt.datetime(2024, 5, 1), 0, 400, None],
            ["Active", "P9012 Made Up Gas And Data", "01-Made Up", "", "Connection", "Gas + Data Load", 2, "Yes", "No", dt.datetime(2024, 5, 2), 300, 300, None],
            ["Recently Energized", "P9013 Made Up Feeder", "01-Made Up", "", "Connection", "Distribution Load", 6, "Yes", "No", dt.datetime(2022, 5, 3), 0, 15, None],
            ["Recently Cancelled", "P9014 Made Up Plant", "01-Made Up", "", "Connection", "Industrial Load", 1, "Yes", "No", dt.datetime(2025, 1, 4), 0, 60, None],
        ], name="Connection Project List")
        rows, _ = w.read_aeso(path)
        os.remove(path)
        self.assertEqual([(r["id"], r["status_words"], r["mw_type"]) for r in rows],
                         [("9011", "Stage 2", "Data Load"), ("9013", "Recently Energized", "Distribution Load"), ("9014", "Recently Cancelled", "Industrial Load")])

    def test_a_project_on_several_rows_is_one_where_its_rows_show_one_stage(self):
        head = ["Project", "Subproject", "Project Type", "Planning Area", "STS MW Change", "DTS MW Change", "MW Type", "Process Stage", "Planned ISD", "Applied On"]
        path = workbook([[None], head,
                         ["P9021 Made Up Load", 1, "Connection", "1-Made Up", 0, 10, "Load", 3, None, dt.datetime(2018, 1, 5)],
                         ["P9021 Made Up Load", 2, "Connection", "1-Made Up", 0, 20, "Load", 3, None, dt.datetime(2018, 1, 5)],
                         ["P9022 Made Up Other Load", 1, "Connection", "1-Made Up", 0, 10, "Load", 5, None, dt.datetime(2018, 2, 5)],
                         ["P9022 Made Up Other Load", 2, "Connection", "1-Made Up", 0, 20, "Load", 2, None, dt.datetime(2018, 2, 5)]], name="AESO Connection Pro - Data List")
        rows, notes = w.read_aeso(path)
        os.remove(path)
        self.assertEqual([(r["id"], r["mw"], r["status_words"]) for r in rows], [("9021", "10", "Stage 3"), ("9022", "10", "Stage 5"), ("9022", "20", "Stage 2")])
        copy = dict(publisher="aeso", date="2018-03-01", stamp="2018-03-01", url="https://web.archive.org/web/1id_/https://example.org/a.xlsx", file="x", rows=rows)
        later = dict(copy, date="2018-04-01", stamp="2018-04-01")
        followed, not_followed = w.follow([copy, later])
        self.assertEqual(list(followed), [("aeso", "9021")])   # two rows that differ in stage: the project is not followed
        self.assertIn("two rows", not_followed[0]["why"])

    def test_a_file_saved_again_long_after_its_month_is_not_used(self):
        fd, path = tempfile.mkstemp(prefix="erw165_", suffix=".xls")
        os.write(fd, b"\xd0\xcf\x11\xe0 made up for the test")
        os.close(fd)
        base = "https://www.aeso.ca/assets/Uploads/"
        day, full, basis = w.aeso_day(path, "Tue, 03 Apr 2018 20:35:22 GMT", base + "Final-April-2018-Project-List.xls")
        self.assertEqual((day, full), ("2018-04-03", "2018-04-03T20:35:22Z"))
        self.assertIn("Last-Modified", basis)
        day, _, why = w.aeso_day(path, "Thu, 27 May 2021 22:36:03 GMT", base + "Final-February-2018-Project-List.xls")
        self.assertEqual(day, "")
        self.assertIn("is not near the month its name gives", why)
        self.assertEqual(w.aeso_day(path, "", base + "Final-April-2018-Project-List.xls")[0], "")   # no date of its own: never the capture's
        os.remove(path)

    def test_a_stage_number_is_kept_and_placed_on_no_class(self):
        for n in range(7):
            self.assertEqual(w.stage_class(f"Stage {n}")[0], "not classed", n)
        self.assertEqual((w.stage_class("Recently Energized")[0], w.stage_class("Recently Cancelled")[0]), (w.STAGES[4], w.NONE))
        self.assertTrue(w.IN_SERVICE.search("Recently Energized") and w.LEFT.search("Recently Cancelled"))

    def test_albertas_rows_say_canada_and_carry_only_the_intervals_its_words_can(self):
        obs = [seen("Stage 2", "2021-05-01", rid="9001", code="2"), seen("Stage 3", "2021-06-01", rid="9001", code="3"),
               seen("Recently Energized", "2021-07-01", rid="9001", code="6")]
        rows = w.durations("aeso", "9001", obs, "2021-07-01")
        self.assertEqual({r["interval"] for r in rows}, {"request to energized", "in stage"})
        for r in rows:
            self.assertIn("Canada", r["entity"])
            self.assertIn("Canada", r["entity_group"])
            self.assertEqual(r["source"], "aeso:connection_project_list_dated_copies")
        r = next(x for x in rows if x["interval"] == "request to energized")
        self.assertEqual((r["label"], r["days_at_least"], r["days_at_most"]), ("measured", w.days("2020-01-10", "2021-06-01"), w.days("2020-01-10", "2021-07-01")))
        stage = next(x for x in rows if x["stage_as_worded"] == "Stage 3")
        self.assertEqual((stage["label"], stage["stage_class"], stage["days_at_least"], stage["days_at_most"]), ("measured", "not classed", 0, 61))
        waiting = w.durations("aeso", "9001", obs[:2], "2021-06-01")
        low = next(x for x in waiting if x["interval"] == "request to energized")
        self.assertEqual((low["label"], low["days_at_most"]), ("two copies only", ""))   # two copies: a lower bound, labeled so
        gone = next(x for x in w.durations("aeso", "9001", obs[:2] + [seen("Stage 3", "2021-06-15", rid="9001", code="3")], "2022-01-01") if x["interval"] == "request to energized")
        self.assertEqual(gone["label"], "lower bound")
        self.assertIn("no longer in the publisher's newest copy", gone["notes"])

    def test_canadas_figures_stand_apart(self):
        self.assertEqual(w.CANADA, (AESO,))
        us = [dict(entity=BPA, interval="request to energized", stage_as_worded="", stage_class="", size_class="all sizes", label="lower bound", days_at_least=10, days_at_most="")]
        ca = [dict(us[0], entity=AESO)]
        counts = dict(copies={BPA: dict(read=2, not_read=0, first="2020-01-01", last="2021-01-01"), AESO: dict(read=3, not_read=1, first="2020-02-01", last="2021-02-01")},
                      requests={e: dict(seen=1, followed=1, not_followed={}, in_service_in_last_copy=0, withdrawn_in_last_copy=0, no_longer_listed_and_no_word_why=n)
                                for e, n in ((BPA, 0), (AESO, 1))},
                      rows=2, rows_by_label={"measured": 0, "lower bound": 2, "two copies only": 0, "upper bound": 0}, rows_by_entity={BPA: 1, AESO: 1},
                      figures=[f for f in w.figures(us + ca) if f["size_class"] == "all sizes"])
        us_lines, ca_lines = "\n".join(w.summary_lines(counts)), "\n".join(w.canada_lines(counts))
        self.assertIn(BPA, us_lines)
        self.assertNotIn("Alberta", us_lines)
        self.assertIn(AESO, ca_lines)
        self.assertNotIn(BPA, ca_lines)
        self.assertIn("**Canada's rows in the table**: 1 of the 2.", ca_lines)
        self.assertEqual(w.gone_lines(counts), [])
        self.assertEqual(len(w.gone_lines(counts, canada=True)), 1)
        self.assertIn("is not a wait still running", w.gone_lines(counts, canada=True)[0])


class Header(unittest.TestCase):
    """The table's header line "This run:" is read by another builder (warehouse/derived/how_soon.py, session 163): it
    keeps its wording and its order, and the publishers added in session 165 stand on a line of their own after it."""
    ENTITY = r": (\d+) copies read \((\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)\), (\d+) requests seen, (\d+) followed"
    ERCOT = r"ERCOT[^:.;]*: (\d+) status reports read \((\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)\), (\d+) name a request"

    def test_the_line_this_run_keeps_its_wording_and_the_new_publishers_follow_on_their_own_line(self):
        import re
        names = [e["entity"] for e in w.ENTITIES.values()]
        counts = dict(copies={e: dict(read=3 + i, first="2020-01-01", last="2021-01-01") for i, e in enumerate(names)},
                      requests={e: dict(seen=9 + i, followed=7 + i) for i, e in enumerate(names)},
                      rows_by_label={"measured": 1, "lower bound": 2, "two copies only": 3, "upper bound": 4},
                      ercot=dict(status_reports=5, first="2022-04-26", last="2026-06-19", reports_naming_a_request=0))
        lines = w.header_lines("20261009T000000Z", dict(rows=[0] * 10), counts)
        at = [i for i, x in enumerate(lines) if x.startswith("This run:")]
        self.assertEqual(len(at), 1)
        run = lines[at[0]]
        self.assertEqual(run, "This run: New York ISO: 3 copies read (2020-01-01 to 2021-01-01), 9 requests seen, 7 followed; Grant County Public Utility District: "
                              "4 copies read (2020-01-01 to 2021-01-01), 10 requests seen, 8 followed. 10 rows: measured 1, lower bound 2, two copies only 3, "
                              "upper bound 4. ERCOT (session 160): 5 status reports read (2022-04-26 to 2026-06-19), 0 name a request, no row.")
        self.assertTrue(re.search(re.escape("New York ISO") + self.ENTITY, run) and re.search(self.ERCOT, run))
        self.assertNotIn("Bonneville", run)
        self.assertNotIn("Alberta", run)
        after = lines[at[0] + 1]
        self.assertTrue(after.startswith("Added in session 165, the same run: Bonneville Power Administration: 5 copies read"), after)
        self.assertTrue(re.search(re.escape(AESO) + self.ENTITY, after))

    @unittest.skipUnless(table_path(), "the table is not on this machine")
    def test_the_tables_own_line_reads_as_before(self):
        import re
        with open(table_path(), encoding="utf-8") as f:
            head = [x[1:].strip() for x in f if x.startswith("#")]
        run = [h for h in head if h.startswith("This run:")]
        self.assertEqual(len(run), 1)
        self.assertRegex(run[0], r"^This run: New York ISO" + self.ENTITY + r"; Grant County Public Utility District" + self.ENTITY
                         + r"\. \d+ rows: measured \d+, lower bound \d+, two copies only \d+, upper bound \d+\. ERCOT \(session 160\): \d+ status reports read "
                         r"\(\d{4}-\d\d-\d\d to \d{4}-\d\d-\d\d\), \d+ name a request, no row\.$")
        self.assertTrue(re.search(self.ERCOT, run[0]))


class Store(unittest.TestCase):
    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_the_new_copies_are_read_dated_by_their_publishers_and_in_order(self):
        b, counts = built()
        self.assertGreaterEqual(counts["copies"][BPA]["read"], 22)
        self.assertGreaterEqual(counts["copies"][AESO]["read"], 97)
        for pub in ("bpa", "aeso"):
            stamps = [c["stamp"] for c in b["copies"] if c["publisher"] == pub]
            self.assertEqual(stamps, sorted(stamps))
            self.assertEqual(len(stamps), len(set(stamps)), pub)
        for c in b["copies"]:
            if c["publisher"] == "aeso":   # a copy's own date stands near the month its file is named for
                ym = w.aeso_month(c["captures"][0]["original"])
                self.assertLessEqual(abs((dt.date.fromisoformat(c["date"]) - dt.date(ym[0], ym[1], 1)).days), 45, c["file"])
        self.assertLessEqual(sum(len(c["rows"]) for c in b["copies"]), w.CEILING_ROWS)

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_every_new_row_holds_its_bounds_its_label_and_its_country(self):
        b, counts = built()
        new = [r for r in b["rows"] if r["entity"] in (BPA, AESO)]
        self.assertGreater(len(new), 1000)
        for r in new:
            self.assertIn(r["label"], w.LABELS)
            self.assertTrue(r["source_url"].startswith("https://"), r["source_url"])
            if r["label"] == "measured":
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
            if r["entity"] == AESO:
                self.assertIn(r["interval"], ("request to energized", "request to withdrawal", "in stage", "in stage, then withdrawn"))
                self.assertIn(r["stage_class"], ("", "not classed"))
            else:
                self.assertNotEqual(r["interval"], "request to construction")
        for e in (BPA, AESO):
            self.assertEqual(counts["requests"][e]["followed"] + sum(counts["requests"][e]["not_followed"].values()), counts["requests"][e]["seen"])

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_no_request_of_the_new_publishers_is_named_in_a_tracked_file(self):
        b, _ = built()
        names = set()
        for c in b["copies"]:
            if c["publisher"] in ("bpa", "aeso"):
                for r in c["rows"]:
                    names.update(x for x in (r["name"],) if len(x) >= 12 and x.count(" ") >= 2)   # a project's name of three words or more
        self.assertGreater(len(names), 200)
        for rel in (PAGE, METHOD, ("warehouse", "connectors", "large_load_waits.py"), ("tests", "test_session165.py"), ("docs", "accelerator", "large_load_eighty.md")):
            text = src(*rel).lower()
            hit = [n for n in names if n.lower() in text]
            self.assertFalse(hit, f"{'/'.join(rel)} names {len(hit)} of the new publishers' requests")


class Table(unittest.TestCase):
    def rows(self):
        with open(table_path(), "rb") as f:
            lines = [x for x in f.read().split(b"\n") if x and not x.startswith(b"#")]
        head = next(csv.reader([lines[0].decode("utf-8")]))
        return head, lines[1:]

    @unittest.skipUnless(table_path() and raw_root(), "the table or the saved copies are not on this machine")
    def test_the_rows_held_before_come_out_byte_for_byte_and_the_new_rows_are_added(self):
        last = {}
        for c in w.read_captures(os.path.join(raw_root(), "large_load_waits")):
            if c["publisher"] in OLD_RETRIEVED and c["file"] and c["status"] == "200" and w.WANTED[c["publisher"]].search(c["original"]):
                last[c["publisher"]] = max(last.get(c["publisher"], ""), c["retrieved_at"])
        if last != OLD_RETRIEVED:
            self.skipTest("a copy of New York's or Grant County PUD's queue was read after 8 October 2026: their rows carry a newer retrieval stamp")
        head, lines = self.rows()
        e = head.index("entity")
        old = [x for x in lines if next(csv.reader([x.decode("utf-8")]))[e] in OLD]
        new = [x for x in lines if next(csv.reader([x.decode("utf-8")]))[e] not in OLD]
        self.assertEqual(len(old), OLD_ROWS)
        self.assertEqual(hashlib.sha256(b"".join(x + b"\n" for x in old)).hexdigest(), OLD_SHA256)
        if not new:
            self.skipTest("the table on this machine is the one of before session 165: the locked write has not run")
        entities = {next(csv.reader([x.decode("utf-8")]))[e] for x in new}
        self.assertEqual(entities, {BPA, AESO})

    @unittest.skipUnless(table_path(), "the table is not on this machine")
    def test_every_row_of_alberta_says_canada_in_the_table(self):
        head, lines = self.rows()
        e, s, p = head.index("entity"), head.index("source"), head.index("parties")
        n = 0
        for x in lines:
            r = next(csv.reader([x.decode("utf-8")]))
            if r[s].startswith("aeso:"):
                n += 1
                self.assertIn("Canada", r[e])
                self.assertIn("Canada", r[p])
            else:
                self.assertNotIn("Canada", r[e])
        if not n:
            self.skipTest("the table on this machine is the one of before session 165")


class Pages(unittest.TestCase):
    def test_the_page_and_the_method_note_hold_no_em_dash_and_keep_canada_apart(self):
        page, method = src(*PAGE), src(*METHOD)
        for rel in (PAGE, METHOD, ("warehouse", "connectors", "large_load_waits.py"), ("tests", "test_session165.py")):
            self.assertNotIn(EM_DASH, src(*rel), rel)
        self.assertIn("\n## Canada", page)
        us, canada = page.split("\n## Canada", 1)
        canada = canada.split("\n## ", 1)[0]
        self.assertIn("| " + AESO + " |", canada)
        self.assertNotIn("| " + AESO + " |", us)   # no figure of Alberta's stands in the United States' table
        self.assertNotIn("| " + BPA + " |", canada)
        self.assertIn("Session 165", page)
        self.assertIn("internal", page)
        for name in ("bpa", "aeso", "isone"):
            for q in w.TERMS[name]["quotes"]:   # each new publisher's terms, word for word, on the page and in the method note
                self.assertIn(q, page, name)
                self.assertIn(q, method, name)
        self.assertIn("lower bound", page)
        self.assertIn("ISO New England", page)

    def test_no_megawatt_of_a_request_of_the_new_publishers_stands_on_the_page(self):
        for line in src(*PAGE).split("\n"):
            if "Bonneville" in line or "Alberta" in line:
                self.assertNotRegex(line, r"\d[\d,.]*\s*(MW|megawatts)\b", line[:80])

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_the_pages_lines_of_the_new_entities_are_the_tables_counts(self):
        b, counts = built()
        page = src(*PAGE)
        if f"**{BPA}**: {counts['copies'][BPA]['read']} dated copies read, {counts['copies'][BPA]['first']} to {counts['copies'][BPA]['last']}" not in page:
            self.skipTest("the raw store holds a newer copy than the page was written from: write the page again from --summary")
        for line in w.summary_lines(counts) + w.gone_lines(counts) + w.canada_lines(counts) + w.gone_lines(counts, canada=True):
            self.assertIn(line, page)


if __name__ == "__main__":
    unittest.main()
