"""Session 7403 (chain 303): the datacenter tracker's cross-check table and its Stata do-file.

The cross-check's "Ours" column is held to the day's figures (replication/datacenter_tracker/page_figures.json), each
gap to ours less theirs, and every row to a publisher, a document and a date. The do-file's expected values are the
same figures, and its Python mirror (replicate.py --headline) gives the five lines on rows made up for the test.
"""

import csv
import importlib.util
import json
import os
import re
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REP = os.path.join(ROOT, "replication", "datacenter_tracker")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def figures():
    return {f["key"]: f["page"] for f in json.loads(src("replication", "datacenter_tracker", "page_figures.json"))["figures"]}


def rows_of(text):
    """The cells of the cross-check's table, one list a row, the header left out."""
    lines = [l for l in text.split("\n") if l.startswith("| ")]
    start = next(i for i, l in enumerate(lines) if l.startswith("| The tracker's figure |"))
    out = []
    for l in lines[start + 1:]:                                              # the rule under the header begins "|-" and is not among the lines kept
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", l)[1:-1]]
        if len(cells) != 6:
            break
        out.append(cells)
    return out


whole = lambda v: f"{round(v):,}"


class TheCrossCheck(unittest.TestCase):
    def setUp(self):
        self.text = src("docs", "methods", "crosschecks", "datacenter_tracker.md")
        self.rows = rows_of(self.text)
        self.f = figures()

    def test_ten_rows_each_with_its_publisher_document_and_date(self):
        self.assertEqual(len(self.rows), 10)
        for r in self.rows:
            self.assertRegex(r[3], r"(19|20)\d\d", r[0])                      # a date
            self.assertRegex(r[3], r"Lawrence Berkeley|Berkeley Lab|Energy Information Administration|ERCOT|PJM|Dominion|American Electric Power", r[0])
            self.assertGreater(len(r[5]), 60, r[0])                           # why they differ, in words
        for name in ("Lawrence Berkeley National Laboratory", "U.S. Energy Information Administration", "ERCOT", "PJM Interconnection", "Dominion Energy", "American Electric Power"):
            self.assertIn(name, self.text, name)

    def test_ours_is_the_days_figures(self):
        f, r = self.f, self.rows
        self.assertIn(f"{whole(f['datacenters|status_mw|operating'])} MW", r[0][1])
        self.assertIn(f"{whole(f['datacenters|mw_total'])} MW, stated by {whole(f['datacenters|n_with_mw'])} of {whole(f['datacenters|counted'])}", r[1][1])
        ahead = f["datacenters|status_mw|planned"] + f["datacenters|status_mw|under_construction"]
        self.assertIn(f"{whole(ahead)} MW ({whole(f['datacenters|status_mw|planned'])} planned, {whole(f['datacenters|status_mw|under_construction'])} under construction)", r[2][1])
        self.assertIn(f"{f['datacenters|mw_total'] * 8760 / 1e6:.1f} TWh", r[3][1])
        self.assertIn(f"{whole(f['datacenters|sites_texas'])} sites in Texas, {whole(f['datacenters|texas_n_with_mw'])} stating MW, {whole(f['datacenters|texas_mw'])} MW in all; "
                      f"{whole(f['dcgrid|planned|ERCOT'])} MW of it planned", r[4][1])
        self.assertIn(f"{whole(f['dcgrid|planned|ERCOT'])} MW, {f['dcgrid|share_of_peak|ERCOT']:.1f} percent of the {whole(f['dcgrid|peak_mw|ERCOT'])} MW peak hour", r[5][1])
        self.assertIn(f"{whole(f['datacenters|rollup_mw|grid|PJM'])} MW, stated by {whole(f['datacenters|rollup_with_mw|grid|PJM'])} of {whole(f['datacenters|rollup_facilities|grid|PJM'])} counted facilities", r[7][1])
        self.assertIn(f"{whole(f['datacenters|mw_total'])} MW", r[9][1])

    def test_each_gap_is_ours_less_theirs(self):
        f, r = self.f, self.rows
        self.assertEqual(r[0][4], f"{whole(f['datacenters|status_mw|operating'] - 176e6 / 8760)} MW".replace("-", "-"))
        self.assertEqual(r[1][4], f"{whole(f['datacenters|mw_total'] - 74000)} to {whole(f['datacenters|mw_total'] - 132000)} MW")
        self.assertIn(f"{whole(f['datacenters|texas_mw'] - 8927)} MW against the approved; {whole(f['datacenters|texas_mw'] - 3900)} MW against the observed", r[4][4])
        self.assertEqual(r[5][4], f"{whole(f['dcgrid|planned|ERCOT'] - (367790 - 85508))} MW")
        self.assertEqual(r[6][4], f"{whole(f['dcgrid|planned|ERCOT'] - 140000)} MW")
        self.assertIn(f"{100 * f['datacenters|rollup_mw|grid|PJM'] / 65733:.1f} percent of the ten-year growth", r[7][4])
        self.assertEqual(r[9][4], f"{whole(f['datacenters|mw_total'] - 84000)} MW")
        # ERCOT's two figures are the table's own newest report
        self.assertEqual(f["series|ercot_large_load_status|ercot:large_load|approved_to_energize_mw|2026-06-19T00:00:00Z"], 8927)
        self.assertEqual(f["series|ercot_large_load_status|ercot:large_load|observed_nonsimultaneous_peak_mw|2026-06-19T00:00:00Z"], 3900)
        self.assertEqual(f["series|ercot_large_load_status|ercot:large_load|new_submissions_mw|2026-03-13T00:00:00Z"], 140000)

    def test_no_publishers_text_is_quoted_and_the_unread_hosts_are_named(self):
        table = self.text[self.text.index("## The table"):self.text.index("## What the table says")]
        self.assertNotIn('"', table)                                          # facts with a link, no quoted text
        self.assertIn("MISO: paused since 4 October 2026 and never requested", self.text)
        self.assertIn("No figure of the tracker was adjusted to match one.", self.text)
        for host in ("eta-publications.lbl.gov", "www.eia.gov", "www.pjm.com", "www.ercot.com", "docs.aep.com"):
            self.assertIn(f"`{host}`", self.text, host)


class TheDoFile(unittest.TestCase):
    def test_its_expected_values_are_the_days_figures(self):
        do, f = src("replication", "datacenter_tracker", "replicate.do"), figures()
        for line in (f"*   1. facilities held: {whole(f['datacenters|count'])}",
                     f"*   2. counted in the sums (a named US state, not cancelled): {whole(f['datacenters|counted'])}",
                     f"*   3. megawatts stated by the counted facilities: {whole(f['datacenters|mw_total'])}",
                     f"*   4. counted facilities that state megawatts: {whole(f['datacenters|n_with_mw'])}",
                     "*   5. ERCOT, megawatts approved to energize, newest report (2026-06-19): 8,927"):
            self.assertIn(line, do, line)
        self.assertIn("This do-file has not been run: Stata is not installed on the machine that wrote it.", do)
        self.assertIn('import delimited using "rows/facilities_slim.csv", delimiter(comma) varnames(2) rowrange(3) stringcols(_all) clear', do)
        self.assertIn('gen byte cancelled = inlist(lower(status), "withdrawn", "cancelled")', do)
        self.assertIn("gen byte counted = us & !cancelled", do)
        self.assertEqual(len(re.search(r'local states " (.+?) "', do).group(1).split()), 52)

    def test_the_mirror_prints_the_five_lines_on_made_up_rows(self):
        spec = importlib.util.spec_from_file_location("dc_replicate_headline", os.path.join(REP, "replicate.py"))
        rep = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rep)
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "facilities_slim.csv"), "w", encoding="utf-8", newline="") as fh:
                fh.write("# made up for the test\n")
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["entity_id", "state", "country", "status", "capacity_mw", "operator", "kind", "grid", "first_story_day", "energized_year", "planned_year"])
                w.writerows([["t1", "TX", "US", "planned", "100", "Alpha", "news", "ERCOT", "", "", ""], ["t2", "TX", "US", "withdrawn", "900", "Alpha", "news", "ERCOT", "", "", ""],
                             ["t3", "", "", "planned", "5000", "Beta", "news", "", "", "", ""], ["t4", "PR", "", "", "40.5", "", "news", "", "", "", ""],
                             ["t5", "VA", "US", "", "", "Beta", "operator", "PJM", "", "", ""]])
            with open(os.path.join(tmp, "ercot_large_load.csv"), "w", encoding="utf-8", newline="") as fh:
                fh.write("# made up for the test\nday,variable,value\n2026-05-21,approved_to_energize_mw,9062\n2026-06-19,approved_to_energize_mw,8927\n2026-06-19,observed_simultaneous_peak_mw,3675\n")
            got = [(w, v, m) for w, v, m in rep.headline(tmp)]
        self.assertEqual([v for _, v, _ in got], [5, 3, 140.5, 2, 8927])     # Puerto Rico by its state; the cancelled and the stateless in no sum
        self.assertEqual(got[4][2], " (2026-06-19)")


class NoEmDash(unittest.TestCase):
    def test_no_em_or_en_dash_in_what_the_session_wrote(self):
        for parts in (("docs", "methods", "crosschecks", "datacenter_tracker.md"), ("replication", "datacenter_tracker", "replicate.do"),
                      ("replication", "datacenter_tracker", "replicate.py"), ("replication", "datacenter_tracker", "fetch_rows.py"), ("tests", "test_session7403_trackers.py"),
                      ("docs", "reviews", "datacenter-faults-2026-11-11.md")):
            text = src(*parts)
            if parts[-1].startswith("datacenter-faults"):
                text = text[text.index("## Found by chain 303"):]
            for ch in (chr(0x2014), chr(0x2013)):
                self.assertNotIn(ch, text, parts[-1])


if __name__ == "__main__":
    unittest.main()
