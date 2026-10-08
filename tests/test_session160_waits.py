"""Session 160, part one: Texas and Grant County PUD in large_load_waits (warehouse/connectors/large_load_waits.py).
The second pull keeps session 155's method: only the publishers named are asked (New York's workbook is not); a file
already saved from a publisher is not asked for again; ERCOT's status reports are found under the names its task
force gave them from 2022 to 2024 and a study's "status update" is not one; the ceiling is the owner's 2,000,000
rows and refuses before a request; ERCOT's system totals are kept as written and never turned into a wait; the
stated figures set beside the measurement are ERCOT's and Oncor's own, as written; the one page holds the lines the
counts give.

Every page, report and figure in this file is MADE UP FOR THE TEST. The tests that need the saved copies skip on a
machine without the raw store. No request and no model call. The module reads the environment and never sets it."""
import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_waits as w  # noqa: E402

EM_DASH = chr(0x2014)
PAGE = ("docs", "accelerator", "large_load_waits.md")
DOCS = "https://www.ercot.com/files/docs/"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw_root():
    """The directory that holds large_load_waits/captures.csv, or None. Reads the environment, never sets it."""
    for d in (os.environ.get("ERW_RAW_ROOT"), os.path.join(ROOT, "warehouse", "raw")):
        if d and os.path.exists(os.path.join(d, "large_load_waits", "captures.csv")):
            return d
    return None


class FakeNet:
    """Stands where the network would be: canned pages, and a list of what was asked."""
    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def get(self, url, kind, rows_reserve=0, timeout=120):
        self.asked.append((url, kind))
        return "200", self.pages.get(url, b"<p>nothing linked</p>"), {}


class Names(unittest.TestCase):
    def test_the_task_forces_status_updates_are_wanted_under_their_own_names(self):
        e = w.WANTED["ercot"]
        for name in ("2023/02/17/LLI%20Queue%20Status%20Update%20-%202023-02-17.pdf", "2022/08/22/LLI%20Queue%20Status%20Update%20-%202022-08-22_.pdf",
                     "2024/08/07/04-lli-queue-status-update-2024-8-5.pdf", "2026/05/21/May-21-LLWG-Report.pptx", "2026/07/28/9.-LLWG-Report.zip",
                     "2026/03/12/March-TAC-Report.pdf"):
            self.assertTrue(e.search(DOCS + name) and not w.NOT_WANTED.search(DOCS + name), name)

    def test_a_status_update_of_a_study_or_of_a_planning_project_is_not_the_queues_report(self):
        e = w.WANTED["ercot"]
        for name in ("2026/01/20/Status-Update_Evaluation-of-Voltage-Ride-Through-Requirement-Jan-2026-LLWG.pdf",
                     "2025/10/21/Status-Update_Effectiveness-of-Transmission-Upgrades-Load-Loss-LLWG-2025-10-24.pdf",
                     "2025/04/28/EIR-BTU-Texas-A-M-University-System-RELLIS-Campus-Reliability-Project-Status-Update-RPG-Apr-2025.pdf",
                     "2026/09/10/LLWG-Batch1-Staw-poll.pptx", "2025/02/28/LL-Oscillation_LFLTF_Mar2025_Final.pptx"):
            self.assertFalse(e.search(DOCS + name) and not w.NOT_WANTED.search(DOCS + name), name)

    def test_the_listings_of_this_session_ask_by_year_and_only_since_2022(self):
        mine = [l for l in w.LISTINGS if "session 160" in l[4]]
        self.assertEqual(sorted(l[1] for l in mine if l[0] == "ercot"), [f"ercot.com/files/docs/{y}/" for y in range(2022, 2027)])
        self.assertEqual([l[1] for l in mine if l[0] == "grantpud"], ["grantpud.org/"])
        self.assertFalse([l for l in mine if l[0] == "nyiso"])   # New York's workbook is not in this session's pull


class OnlyThePublishersNamed(unittest.TestCase):
    def pages(self):
        llwg = (b'<a href="/committees/tac/llwg/2025">2025</a> <a href="/committees/tac/2024">another committee</a>'
                b'<a href="/calendar/09172026-LLWG-Meeting">meeting</a>')
        llwg25 = b'<a href="/calendar/05162025-LLWG-Meeting-_-Webex">meeting</a>'
        tac = b'<a href="/committees/tac/2025">2025</a> <a href="/committees/tac/2024">2024</a> <a href="/committees/tac/2021">2021</a>'
        lfltf = (b'<a href="/committees/inactive/lfltf/2023">2023</a> <a href="/committees/inactive/lfltf/2021">2021</a>'
                 b'<a href="https://www.ercot.com/files/docs/2024/02/06/LLI-Queue-Status-Update-2024-1-25.pdf">the last update</a>')
        lfltf23 = b'<a href="/calendar/02172023-LFLTF-Meeting">meeting</a>'
        m23 = (b'<a href="/files/docs/2023/02/17/LLI Queue Status Update - 2023-02-17.pdf">status</a>'
               b'<a href="/files/docs/2023/02/17/LFL_Analysis.pptx">analysis</a>')
        m26 = b'<a href="/files/docs/2026/09/16/September-TAC-Report.pdf">status</a>'
        base = "https://www.ercot.com"
        return {w.CURRENT["ercot_pages"][0]: llwg, base + "/committees/tac/llwg/2025": llwg25, w.CURRENT["ercot_pages"][1]: tac,
                w.CURRENT["ercot_pages"][2]: lfltf, base + "/committees/inactive/lfltf/2023": lfltf23,
                base + "/calendar/02172023-LFLTF-Meeting": m23, base + "/calendar/09172026-LLWG-Meeting": m26,
                w.CURRENT["grantpud_page"]: b'<a href="/images/2026/Transmission-Queue/Transmission Queue 20260730.pdf">queue</a>'}

    def test_new_yorks_workbook_is_not_asked_for_when_it_is_not_named(self):
        d = tempfile.mkdtemp(prefix="erw160_")
        net = FakeNet(self.pages())
        w.do_pull_current(d, net, lambda m: None, None, {"ercot", "grantpud"})
        asked = [u for u, _ in net.asked]
        self.assertFalse([u for u in asked if "nyiso" in u])
        self.assertIn("https://www.grantpud.org/images/2026/Transmission-Queue/Transmission%20Queue%2020260730.pdf", asked)

    def test_the_years_followed_are_the_committees_own_and_tac_only_since_2025(self):
        d = tempfile.mkdtemp(prefix="erw160_")
        net = FakeNet(self.pages())
        w.do_pull_current(d, net, lambda m: None, None, {"ercot"})
        asked = [u for u, _ in net.asked]
        base = "https://www.ercot.com"
        for u in (base + "/committees/tac/llwg/2025", base + "/committees/tac/2025", base + "/committees/inactive/lfltf/2023",
                  base + "/calendar/02172023-LFLTF-Meeting", base + "/calendar/05162025-LLWG-Meeting-_-Webex",
                  DOCS + "2023/02/17/LLI%20Queue%20Status%20Update%20-%202023-02-17.pdf",
                  DOCS + "2024/02/06/LLI-Queue-Status-Update-2024-1-25.pdf", DOCS + "2026/09/16/September-TAC-Report.pdf"):
            self.assertIn(u, asked)
        for other in ("/committees/tac/2024", "/committees/tac/2021", "/committees/inactive/lfltf/2021", "LFL_Analysis", "grantpud", "nyiso"):
            self.assertFalse([u for u in asked if other in u], other)
        self.assertEqual(len(asked), len(set(asked)))   # nothing asked twice

    def test_a_file_already_saved_from_the_publisher_is_not_asked_for_again(self):
        d = tempfile.mkdtemp(prefix="erw160_")
        net = FakeNet(self.pages())
        w.do_pull_current(d, net, lambda m: None, None, {"ercot", "grantpud"})
        first = len(net.asked)
        files = [u for u, _ in net.asked if u.lower().endswith((".pdf", ".pptx", ".zip"))]
        self.assertTrue(files)
        w.do_pull_current(d, net, lambda m: None, None, {"ercot", "grantpud"})
        again = [u for u, _ in net.asked[first:]]
        self.assertFalse([u for u in again if u in files])

    def test_the_archive_is_asked_only_for_the_publishers_named(self):
        d = tempfile.mkdtemp(prefix="erw160_")
        ny = "https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx"
        er = DOCS + "2023/02/17/LLI%20Queue%20Status%20Update%20-%202023-02-17.pdf"
        head = b'[["timestamp","original","mimetype","statuscode","digest","length"],'
        net = FakeNet({w.cdx_url("nyiso.com/x/", "prefix"): head + b'["20260801000000","' + ny.encode() + b'","application/x","200","AAAA","10"]]',
                       w.cdx_url("ercot.com/files/docs/2023/", "prefix"): head + b'["20230320000000","' + er.encode() + b'","application/pdf","200","BBBB","10"]]'})
        w.do_list(d, net, lambda m: None, listings=[("nyiso", "nyiso.com/x/", "prefix", "", "made up"), ("ercot", "ercot.com/files/docs/2023/", "prefix", "", "made up")])
        w.do_pull_archive(d, net, lambda m: None, {"ercot"})
        fetched = [u for u, kind in net.asked if kind == "capture"]
        self.assertEqual(fetched, [f"https://web.archive.org/web/20230320000000id_/{er}"])


class Ceiling(unittest.TestCase):
    def test_the_rows_ceiling_is_two_million_and_refuses_before_the_request(self):
        self.assertEqual(w.CEILING_ROWS, 2_000_000)
        d = tempfile.mkdtemp(prefix="erw160_")
        b = w.Budget(d)
        b.add_rows(2_000_000 - w.ROWS_RESERVE + 1)
        with self.assertRaises(w.Refused):
            b.ask("https://web.archive.org/web/1id_/https://www.ercot.com/a.pdf", "capture", rows_reserve=w.ROWS_RESERVE)
        self.assertEqual(b.requests, 0)   # refused before it was made


class Totals(unittest.TestCase):
    SENTENCE = ("Of the 1,234 MW that have received Approval to Energize, ERCOT has observed a non- simultaneous peak consumption of 567 MW. "
                "MADE UP FOR THE TEST")

    def test_the_sentence_is_kept_as_written_with_its_basis(self):
        m = w.ERCOT_A2E.search(self.SENTENCE)
        self.assertEqual((m.group(1), m.group(3), m.group(2)), ("1,234", "567", None))
        m = w.ERCOT_A2E.search("Of the 1234 MW that have received Approval to Energize, ERCOT has observed a non-simultaneous monthly peak consumption of 567 MW in a month")
        self.assertEqual((m.group(1), m.group(3), m.group(2)), ("1234", "567", "monthly "))

    def test_a_report_that_prints_a_column_head_of_a_list_of_requests_is_flagged(self):
        self.assertTrue(w.ERCOT_LISTS.search("Project Name MW Status"))
        self.assertTrue(w.ERCOT_LISTS.search("Queue Position"))
        self.assertFalse(w.ERCOT_LISTS.search("Large Load Project Distribution by Load Zone"))
        self.assertFalse(w.ERCOT_LISTS.search(self.SENTENCE))

    def counts(self):
        rep = lambda day, a, o, basis: dict(day=day, document="made-up.pdf", held_by="the Internet Archive", names_a_request=False, stages_named=[],  # noqa: E731
                                            approved_to_energize_mw=a, observed_consuming_mw=o, observed_basis=basis, sentence="made up")
        reports = [rep("2023-01-01", "", "", ""), rep("2023-02-01", "1000", "400", "the all-time non-simultaneous peak"),
                   rep("2026-03-01", "9000", "4000", "the month's non-simultaneous peak")]
        stated = [dict(entity_group="Oncor Electric Delivery", quantity_as_written="825 days", wait_basis="measured", status="placed in service", stage_class="5",
                       event_date="2025-08-25", source_url="u", page="64", wait_counted="yes"),
                  dict(entity_group="ERCOT", quantity_as_written="15 weeks", wait_basis="expected", status="a study step", stage_class="2", event_date="2026-05-05",
                       source_url="u", page="18", wait_counted="yes"),
                  dict(entity_group="Some Other Utility", quantity_as_written="3 years", wait_basis="expected", status="x", stage_class="5", event_date="2026-01-01",
                       source_url="u", page="1", wait_counted="yes"),
                  dict(entity_group="ERCOT", quantity_as_written="2 days", wait_basis="expected", status="not counted", stage_class="2", event_date="2026-01-01",
                       source_url="u", page="1", wait_counted="no")]
        return dict(ercot=dict(status_reports=3, first="2023-01-01", last="2026-03-01", requests_listed=0, reports=reports, held_by_archive=3,
                               held_by_publisher=0, reports_naming_a_request=0), texas_stated=w.texas_stated(stated))

    def test_the_stated_figures_set_beside_are_ercots_and_oncors_as_written(self):
        c = self.counts()
        self.assertEqual([(x["entity_group"], x["as_written"]) for x in c["texas_stated"]], [("Oncor Electric Delivery", "825 days"), ("ERCOT", "15 weeks")])

    def test_no_wait_is_made_from_the_system_totals(self):
        lines = w.texas_lines(self.counts())
        self.assertIn("measured waits: none", lines[0])
        self.assertIn("requests followed: 0", lines[0])
        totals = lines[1]
        self.assertIn("1,000 MW approved to energize and 400 MW observed consuming", totals)
        self.assertIn("9,000 MW and 4,000 MW", totals)
        self.assertIn("not a request's wait", totals)
        self.assertNotRegex(totals, r"\d\s*days")          # megawatts over time are not turned into a duration
        self.assertNotRegex(" ".join(lines[:2]), r"(?i)median|average|at least \d")
        self.assertIn('- **Oncor Electric Delivery** wrote "825 days" (measured; placed in service; 2025-08-25).', lines)
        self.assertFalse([l for l in lines if EM_DASH in l])


class Page(unittest.TestCase):
    def test_the_page_says_what_texas_gives_and_holds_no_em_dash(self):
        page = src(*PAGE)
        self.assertNotIn(EM_DASH, page)
        self.assertIn("Session 160", page)
        self.assertIn("measured waits: none", page)
        self.assertIn("825 days", page)

    @unittest.skipUnless(raw_root(), "the saved copies are not on this machine")
    def test_the_pages_texas_lines_are_the_counts(self):
        raw = os.path.join(raw_root(), "large_load_waits")
        ercot = w.read_ercot(raw, lambda m: None)
        wf = os.path.join(raw_root(), "large_load_statements", "wait_figures.csv")
        if not os.path.exists(wf):
            self.skipTest("the stated figures are not on this machine")
        with open(wf, encoding="utf-8", newline="") as f:
            stated = list(csv.DictReader(f))
        counts = dict(ercot=dict(status_reports=len(ercot), first=ercot[0]["day"], last=ercot[-1]["day"], requests_listed=0, reports=ercot,
                                 held_by_archive=sum(1 for r in ercot if r["held_by"] == "the Internet Archive"),
                                 held_by_publisher=sum(1 for r in ercot if r["held_by"] != "the Internet Archive"),
                                 reports_naming_a_request=sum(1 for r in ercot if r["names_a_request"])), texas_stated=w.texas_stated(stated))
        page = src(*PAGE)
        if f"{len(ercot)} large load status reports read" not in page:
            self.skipTest("the raw store holds a report the page was not written from: write the page again from --summary")
        for line in w.texas_lines(counts):
            self.assertIn(line, page)


if __name__ == "__main__":
    unittest.main()
