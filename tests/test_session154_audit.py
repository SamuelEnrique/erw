"""Session 154: the audit of 50 policy actions against their source documents, and the extraction rules it fixed.

Every test reads a real document saved by the audit on 8 October 2026 (tests/fixtures/session154/, with the address,
the hash and the retrieval time of each in MANIFEST.csv): six records of the Federal Register's API, one printed
Register document, the NRC's news feed and the text of one NRC release. No request is made, no model is called and
no table is needed, so the tests run the same on a machine without warehouse/output.

What the audit found, and what is tested here (runs/session154/agent_report_audit.md):

1. states: "West Virginia" was also read as Virginia (2026-02830 held VA;WV), and "Washington, DC" as the state.
2. abstract: the Register's inline markup was replaced by a space, so NO<INF>X</INF> became "NO X " (2026-13027).
3. sector_tags: a FERC notice has no abstract in the API, so its tags rested on the applicant's name: gas pipeline
   applications had no tag or "transmission" (from "Columbia Gulf Transmission, LLC"), hydropower projects had none;
   NRC releases had no "nuclear" tag when the title did not say the word, and "storage" for spent fuel storage.
4. event_date of NRC and DOE news: the UTC day of the feed, a day after the day printed on the release for 24 of the
   feed's 167 items.
5. parties: a release of the Governor's office listed on the PUCT's news page named only the PUCT.
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "session154")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "policy", "audit"))

import policy_sources as ps  # noqa: E402

# The day printed on each NRC release the audit opened (the PDF's own heading, "No: 26-060 June 5, 2026"), against
# the feed's GMT stamp for the same link. Saved under runs/session154/audit/raw/ with their hashes.
PRINTED = {"2026/26-001-i.pdf": "2026-02-10", "2026/26-060.pdf": "2026-06-05", "2026/26-046.pdf": "2026-04-23",
           "2025/25-063.pdf": "2025-12-01", "2026/26-067.pdf": "2026-06-18", "2026/26-024.pdf": "2026-02-26",
           "2026/26-005.pdf": "2026-01-08"}


def record(number):
    with open(os.path.join(FIX, f"fr_{number}.api.json"), encoding="utf-8") as f:
        return json.load(f)


def connector_text(x):
    """The text the connector reads for a Register record: title, abstract and topics."""
    return f"{ps.clean(x.get('title'))} {ps.clean(x.get('abstract'))} {' '.join(x.get('topics') or [])}"


def docket(x):
    return ";".join([d for d in x.get("docket_ids") or [] if d] + [r for r in x.get("regulation_id_numbers") or [] if r])


class States(unittest.TestCase):
    def test_west_virginia_is_not_also_virginia(self):
        x = record("2026-02830")
        self.assertIn("West Virginia", x["title"])
        self.assertNotRegex(connector_text(x).replace("West Virginia", ""), r"\bVirginia\b")  # the record names no Virginia
        self.assertEqual(ps.states(connector_text(x)), "WV")

    def test_a_text_that_names_both_keeps_both(self):
        self.assertEqual(ps.states("plants in Virginia and West Virginia"), "VA;WV")

    def test_washington_dc_is_not_the_state(self):
        # the title of federalregister:2026-05037, as the table holds it
        self.assertEqual(ps.states("Notice of Intended Repatriation: U.S. Department of Energy, Office of Petroleum "
                                   "Reserves, Washington, DC"), "")
        # a sentence of 2026-06708 (Avista, the Spokane River project): the state of Washington is still read
        self.assertEqual(ps.states("in Spokane, Lincoln, and Stevens counties, Washington, and in Kootenai and Benewah "
                                   "counties, Idaho"), "ID;WA")

    def test_every_state_is_still_found_alone(self):
        for name, code in ps.STATES.items():
            self.assertEqual(ps.states(f"a project in {name}."), code, name)


class Abstract(unittest.TestCase):
    def test_inline_markup_leaves_no_space_inside_a_word(self):
        x = record("2026-13027")
        self.assertIn("NO<INF>X</INF>", x["abstract"])  # the Register's own markup
        a = ps.clean(x["abstract"])
        self.assertIn("oxides of nitrogen (NOX) motor vehicle emissions budgets", a)
        self.assertNotIn("NO X", a)

    def test_block_markup_still_separates_words(self):
        self.assertEqual(ps.clean("<p>one</p><p>two</p>"), "one two")


class Tags(unittest.TestCase):
    def test_a_ferc_gas_certificate_notice_is_gas(self):
        x = record("2026-19580")  # Transcontinental Gas Pipe Line Company, LLC; CP26-576-000; no abstract in the API
        self.assertIsNone(x["abstract"])
        self.assertEqual(ps.tags(connector_text(x)), "")  # the keyword rules alone found nothing
        self.assertEqual(ps.tags(connector_text(x), "FERC", docket(x)), "gas")

    def test_a_pipeline_company_named_transmission_is_not_the_transmission_sector(self):
        x = record("2026-16633")  # Columbia Gulf Transmission, LLC; CP26-25-000: 42 miles of natural gas pipeline
        self.assertEqual(ps.tags(connector_text(x)), "transmission")
        self.assertEqual(ps.tags(connector_text(x), "FERC", docket(x)), "gas")

    def test_a_ferc_project_number_is_hydropower(self):
        x = record("2026-06708")  # Avista Corporation; Project No. 2545-205, the Spokane River Hydroelectric Project
        self.assertEqual(ps.tags(connector_text(x)), "")
        self.assertEqual(ps.tags(connector_text(x), "FERC", docket(x)), "power;renewables")

    def test_an_electric_docket_keeps_its_transmission_tag(self):
        title = "New York Independent System Operator, Inc.; NextEra Energy Transmission New York, Inc.; Notice"
        self.assertEqual(ps.tags(title, "FERC", "Docket No. EL26-69-000"), "transmission")
        self.assertEqual(ps.tags(title, "FERC", "Docket No. EL26-69-000"), ps.tags(title))

    def test_nrc_spent_fuel_storage_is_not_the_storage_sector(self):
        x = record("2026-06373")  # List of Approved Spent Fuel Storage Casks: Holtec International HI-STORM UMAX
        self.assertIn("storage", ps.tags(connector_text(x)).split(";"))
        self.assertEqual(ps.tags(connector_text(x), "NRC", docket(x)), "nuclear")

    def test_an_nrc_release_is_nuclear_whatever_its_title(self):
        # the title of nrc:4cec785a9cad (release 26-072), which held no tag
        self.assertEqual(ps.tags("NRC Proposes Major Modernization of Environmental Review Process", "NRC"), "nuclear")
        self.assertEqual(ps.tags("NRC licenses a battery energy storage test facility", "NRC"), "nuclear;storage")

    def test_other_agencies_are_as_before(self):
        text = "Energy Conservation Program: electricity, natural gas, No. 2 heating oil"
        self.assertEqual(ps.tags(text, "DOE", ""), ps.tags(text))


class FeedDates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(FIX, "nrc_feed.xml"), "rb") as f:
            cls.content = f.read()
        cls.rows = ps.rss_rows("nrc", "NRC", cls.content, "2000-01-01", "2026-10-08T04:22:46Z")
        cls.by_link = {r["source_url"]: r for r in cls.rows}

    def test_the_feed_is_read_whole(self):
        self.assertEqual(len(self.rows), 167)
        # one item of the feed is stamped 26 February 2023 (release 26-022, the feed's own date): --since leaves it out
        self.assertEqual(len(ps.rss_rows("nrc", "NRC", self.content, "2025-01-01", "x")), 166)

    def test_the_day_is_the_day_printed_on_the_release(self):
        for tail, day in PRINTED.items():
            link = "https://www.nrc.gov/sites/default/files/cdn/doc-collection-news/" + tail
            self.assertEqual(self.by_link[link]["event_date"], day, tail)

    def test_the_sampled_release_states_its_day(self):
        with open(os.path.join(FIX, "nrc_26-001-i.txt"), encoding="utf-8") as f:
            text = f.read()
        self.assertRegex(re.sub(r"\s+", " ", text), r"No: I-26-001 February 10, 2026")

    def test_how_many_items_carried_the_next_day(self):
        import xml.etree.ElementTree as ET
        import pandas as pd
        moved = 0
        for it in ET.fromstring(self.content).iter("item"):
            utc = pd.to_datetime(it.findtext("pubDate"), utc=True).strftime("%Y-%m-%d")
            moved += utc != ps.release_day(it.findtext("pubDate"))
        self.assertEqual(moved, 24)

    def test_an_offset_stamp_and_a_bad_one(self):
        self.assertEqual(ps.release_day("Fri, 25 Sep 2026 21:30:00 -0400"), "2026-09-25")  # the DOE feed's form
        self.assertIsNone(ps.release_day("not a date"))
        self.assertIsNone(ps.release_day(None))


class Parties(unittest.TestCase):
    def test_a_governors_release_listed_by_the_puct_names_its_issuer(self):
        link = "https://gov.texas.gov/news/post/governor-abbott-announces-200-million-grant-for-electric-reliability-in-southeast-texas"
        r = ps.press("puct", "PUCT", link, "2026-06-15", "Governor Abbott Announces $200 Million Grant For Electric "
                     "Reliability In Southeast Texas", "", "2026-10-03T14:44:07Z", "TX")
        self.assertEqual(r["parties"], "Office of the Texas Governor;PUCT")
        self.assertEqual((r["agency"], r["event_id"]), ("PUCT", "puct:237f5d48d937"))  # the row keeps its id

    def test_the_commissions_own_release_is_as_before(self):
        r = ps.press("puct", "PUCT", "https://www.puc.texas.gov/agency/resources/pubs/news/2026/x.pdf", "2026-06-15",
                     "PUCT Approves Rule", "", "2026-10-03T14:44:07Z", "TX")
        self.assertEqual(r["parties"], "PUCT")


class AuditTools(unittest.TestCase):
    def test_the_sample_is_the_same_on_every_draw(self):
        import audit_sample as sample
        ids = [f"federalregister:2026-{n:05d}" for n in range(1, 400)]
        a, b = sample.draw(ids), sample.draw(list(reversed(ids)))
        self.assertEqual(a, b)
        self.assertEqual((len(a), len(set(a)), sample.SEED, sample.N), (50, 50, 154, 50))

    def test_the_printed_heading_is_read(self):
        import audit_check as check
        with open(os.path.join(FIX, "fr_2026-18359.text.txt"), encoding="utf-8") as f:
            p = check.fr_parse(check.fr_text(f.read()), ["DEPARTMENT OF ENERGY", "Federal Energy Regulatory Commission"])
        self.assertEqual((p["date"], p["section"], p["number"]), ("2026-09-09", "Notices", "2026-18359"))
        self.assertEqual(p["brackets"], ["Project No. 8405-024"])
        self.assertEqual(check.agency_of(p["agencies"]), "FERC")
        self.assertTrue(p["title"].startswith("Green River Power Corporation; Notice of Reasonable Period of Time"))

    def test_the_fetch_sends_no_persons_address_and_refuses_paused_hosts(self):
        import audit_fetch as fetch
        self.assertNotIn("@", fetch.UA["User-Agent"])
        self.assertEqual(fetch.UA, ps.UA)  # the connector's own header
        self.assertLessEqual(fetch.MAX_REQUESTS, 200)
        self.assertIn("misoenergy.org", fetch.FORBIDDEN)

    def test_a_trial_table_is_compared_field_by_field(self):
        import pandas as pd
        import audit_compare
        held = pd.DataFrame([dict(event_id="a", states="VA;WV", sector_tags="", retrieved_at="1"),
                             dict(event_id="b", states="", sector_tags="transmission", retrieved_at="1"),
                             dict(event_id="c", states="TX", sector_tags="gas", retrieved_at="1")])
        trial = pd.DataFrame([dict(event_id="a", states="WV", sector_tags="", retrieved_at="2"),
                              dict(event_id="b", states="", sector_tags="gas", retrieved_at="2"),
                              dict(event_id="d", states="", sector_tags="", retrieved_at="2")])
        diff, gone, new = audit_compare.compare(held, trial)
        self.assertEqual(diff, {"states": ["a"], "sector_tags": ["b"]})  # retrieved_at is the run's own time: left out
        self.assertEqual((gone, new), (["c"], ["d"]))

    def test_the_connector_takes_an_out_dir(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "policy_sources.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('"--out-dir"', src)
        self.assertIn("ip.set_out_dir(args.out_dir)", src)

    def test_no_em_dash_in_the_sessions_files(self):
        audit = os.path.join(ROOT, "warehouse", "policy", "audit")
        names = sorted(n for n in os.listdir(audit) if n.endswith(".py"))
        # this module puts the folder on sys.path: a file named tabulate.py there once hid the tabulate package from
        # gridstatus and broke the import of every connector, so each name carries the prefix
        self.assertEqual([n for n in names if not n.startswith("audit_")], [])
        # session 157 added two modules to the folder (audit_findings_s157.py, audit_truth.py), each with the prefix:
        # the seven of session 154 must all still be there, and a later session may add more
        self.assertGreaterEqual(len(names), 7)
        for n in ("audit_check.py", "audit_compare.py", "audit_fetch.py", "audit_findings.py", "audit_refix.py",
                  "audit_sample.py", "audit_table.py"):
            self.assertIn(n, names)
        paths = [os.path.join(audit, n) for n in names]
        paths += [os.path.join(ROOT, "warehouse", "connectors", "policy_sources.py"), os.path.abspath(__file__)]
        paths += [os.path.join(FIX, n) for n in os.listdir(FIX)]
        for p in paths:
            if os.path.exists(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    self.assertNotIn(chr(0x2014), f.read(), p)


if __name__ == "__main__":
    unittest.main()
