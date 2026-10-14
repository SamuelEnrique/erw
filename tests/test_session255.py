"""Session 255: the large-load statements, public where it is safe.

How a source document is classed and what verdict it gets (from its address, its type and session 205's reads), which
rows reach large_load_public and what they may hold (a figure, a class, a date, a title and a link: no words of the
document), on made-up rows (test inputs, never data); then the counts of the method note against the two tables where
the data machine holds them. No network.
"""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import large_load_public as L  # noqa: E402

EM = chr(0x2014)
OUT = os.path.join(ROOT, "warehouse", "output")
READ = {"ERCOT": ("may be public", "may be public", "2"), "CAISO": ("may be public", "may be public", "3"), "SPP": ("may be public", "needs written permission", "6"),
        "NYISO": ("needs written permission", "needs written permission", "5"), "PJM": ("needs a paid license", "needs a paid license", "15")}
# the statements table's columns that hold a document's own words, or the collecting pass's: none may be in the public table
WORDS = {"sentence", "stage_as_worded", "load_type_as_worded", "place_as_worded", "time_horizon_as_worded", "wait_or_lead_time_as_worded", "quantity_as_written", "notes",
         "stage_class_basis", "wait_basis_words", "document_date_as_stated"}


def statement(**kw):
    base = dict(event_id="llstmt:0000000000000001", event_date="2026-04-14", event_type="large_load_statement", parties="A Utility", entity_ids="", mw="220.0", price="",
                currency="", status="Electric Service Agreement: Maximum Contract Demand", source="erw:large_load_pilot", source_url="https://apps.psc.wi.gov/ERF/x.pdf",
                entity_group="A Group", entity="A Utility", entity_type="utility", document_title="Direct Testimony, docket 1", document_type="large load tariff filing",
                page="5", quantity_as_written="220 MW", mw_low="", mw_high="", stage_as_worded="Electric Service Agreement: Maximum Contract Demand", sentence="a sentence of the document",
                row_kind="mw", stage_class="4 signed service agreement", event_date_basis="document", source_flag="", wait_basis="", load_scope="", wait_counted="")
    base.update(kw)
    return base


def waits():
    return pd.DataFrame([dict(source="nyiso:interconnection_queue_dated_copies", source_url="https://web.archive.org/web/2020/https://www.nyiso.com/q.xlsx"),
                         dict(source="bpa:interconnection_queue_dated_copies", source_url="https://www.bpa.gov/q.xlsx"),
                         dict(source="bpa:interconnection_queue_dated_copies", source_url="https://www.bpa.gov/q.xlsx")])


class AClassAndAVerdict(unittest.TestCase):
    def of(self, url, kind="other", flag=""):
        return L.classify(url, kind, flag, READ)[:2]

    def test_an_sec_filing_and_a_regulators_docket_are_public(self):
        self.assertEqual(self.of("https://www.sec.gov/Archives/edgar/data/1/2/ex99.htm", "earnings presentation"), ("SEC filing", "public"))
        self.assertEqual(self.of("https://interchange.puc.texas.gov/Documents/1.PDF", "commission filing"), ("regulatory filing", "public"))
        c = L.classify("https://psc.mo.gov/CMSInternetData/x.pdf", "operator report", "", READ)
        self.assertEqual((c[0], c[1], c[3], c[4]), ("regulatory filing", "public", "Missouri Public Service Commission", "MO"))   # an operator's report, where a regulator posts it
        self.assertIn("may be republished as a fact, with a link", c[2])
        self.assertIn("no long quotation", c[2])

    def test_only_the_commissions_folder_of_indianas_site(self):
        self.assertEqual(self.of("https://www.in.gov/iurc/files/irp.pdf", "integrated resource plan"), ("regulatory filing", "public"))
        self.assertEqual(self.of("https://www.in.gov/oed/files/x.pdf", "other")[1], "not settled")

    def test_a_read_operator_is_public_only_when_its_terms_allow_it_today_and_if_the_erw_sells(self):
        self.assertEqual(self.of("https://www.ercot.com/files/x.pdf", "operator report"), ("read publisher's document", "public"))
        self.assertEqual(self.of("https://stakeholdercenter.caiso.com/x.pdf", "operator report"), ("read publisher's document", "public"))
        self.assertEqual(self.of("https://www.spp.org/documents/x.pdf", "operator report"), ("read publisher's document", "needs written permission"))   # held with its tables
        self.assertEqual(self.of("https://www.nyiso.com/x.pdf", "operator report"), ("read publisher's document", "needs written permission"))
        self.assertEqual(self.of("https://www.pjm.com/x.pdf", "load forecast report"), ("read publisher's document", "needs a paid license"))
        self.assertEqual(L.classify("https://www.ercot.com/x.pdf", "operator report", "", {})[1], "not settled")                                         # a publisher 205 did not read

    def test_what_is_not_settled_and_what_is_not_public(self):
        self.assertEqual(self.of("https://www.pacificorp.com/irp.pdf", "integrated resource plan"), ("filed document, the filer's own copy", "not settled"))
        self.assertEqual(self.of("https://investor.avistacorp.com/10k.pdf", "SEC filing"), ("filed document, the filer's own copy", "not settled"))
        self.assertEqual(self.of("https://s1.q4cdn.com/x/deck.pdf", "earnings presentation"), ("publisher's own document", "not settled"))
        self.assertEqual(self.of("https://www.bpa.gov/x.pdf", "operator report"), ("federal body's document", "not settled"))
        self.assertEqual(self.of("https://www.pnnl.gov/x.pdf", "other"), ("publisher's own document", "not settled"))                                   # a laboratory's is its contractor's
        self.assertEqual(self.of("https://www.sec.gov/Archives/x.htm", "earnings presentation", "a third party's copy: a conference host's copy"), ("third party's copy", "not public"))

    def test_every_publisher_of_the_waits_table_has_a_verdict_and_none_is_public(self):
        self.assertEqual(sorted(L.WAIT_PUBLISHERS), ["aeso:connection_project_list_dated_copies", "bpa:interconnection_queue_dated_copies",
                                                     "grantpud:interconnection_queue_dated_copies", "nyiso:interconnection_queue_dated_copies"])
        self.assertTrue(all(v[1] != "public" for v in L.WAIT_PUBLISHERS.values()))


class ThePublicRows(unittest.TestCase):
    def build(self, rows):
        return L.build(pd.DataFrame(rows), waits(), READ, "2026-10-13")

    def test_a_public_documents_row_holds_a_figure_a_class_a_date_a_title_and_a_link_and_no_words_of_the_document(self):
        public, verdicts, _ = self.build([statement()])
        self.assertEqual(len(public), 1)
        r = public.iloc[0]
        self.assertEqual((r["event_id"], r["statement_id"], r["parties"], r["mw"], r["status"], r["event_date"], r["document_title"], r["page"], r["source_url"]),
                         ("llpub:0000000000000001", "llstmt:0000000000000001", "A Utility", "220.0", "4 signed service agreement", "2026-04-14", "Direct Testimony, docket 1", "5",
                          "https://apps.psc.wi.gov/ERF/x.pdf"))
        self.assertEqual((r["public_basis"], r["regulator"], r["state"], r["grid"]), ("public regulatory filing", "Public Service Commission of Wisconsin", "WI", "not placed"))
        self.assertEqual(set(public.columns) & WORDS, set())
        self.assertNotIn("Maximum Contract Demand", " ".join(str(x) for x in r.values))            # the stage in the document's words is not in the row
        self.assertNotIn("a sentence of the document", " ".join(str(x) for x in r.values))

    def test_a_row_whose_address_holds_an_email_address_or_whose_document_is_not_public_is_not_there(self):
        rows = [statement(),
                statement(event_id="llstmt:2", source_url="https://psc.ky.gov/pscecf/2025-00001/someone%40example.com/x.pdf"),
                statement(event_id="llstmt:3", source_url="https://psc.ky.gov/pscecf/2025-00001/someone@example.com/y.pdf"),
                statement(event_id="llstmt:4", source_url="https://www.pjm.com/x.pdf", document_type="load forecast report"),
                statement(event_id="llstmt:5", source_url="https://s1.q4cdn.com/x/deck.pdf", document_type="earnings presentation"),
                statement(event_id="llstmt:6", source_url="http://www.sec.gov/Archives/x.htm", document_type="SEC filing")]
        public, verdicts, s = self.build(rows)
        self.assertEqual(public["statement_id"].tolist(), ["llstmt:0000000000000001"])
        n = L.summary(public, verdicts, s)
        self.assertEqual((n["statements"], n["public_verdict_rows"], n["held_out_for_an_email_address"], n["public_rows"]), (6, 4, 2, 1))
        v = verdicts[verdicts["of_table"] == "large_load_statements"].set_index("source_url")
        self.assertEqual(v.loc["https://psc.ky.gov/pscecf/2025-00001/someone@example.com/y.pdf", "address_holds_email"], "yes")
        self.assertEqual((v.loc["https://www.pjm.com/x.pdf", "status"], v.loc["https://www.pjm.com/x.pdf", "rows_public"]), ("needs a paid license", 0))
        w = verdicts[verdicts["of_table"] == "large_load_waits"]
        self.assertEqual(sorted(zip(w["parties"], w["status"], w["rows"])), [("Bonneville Power Administration", "not settled", 2), ("New York ISO", "needs written permission", 1)])

    def test_a_duration_is_its_figure_and_a_clause_is_not_copied(self):
        rows = [statement(row_kind="wait", mw="", quantity_as_written="  within 18 months ", wait_basis="expected", wait_counted="yes", stage_class="none"),
                statement(event_id="llstmt:2", row_kind="wait", mw="", quantity_as_written="approximately 6 months for smaller projects with available capacity to several years",
                          wait_basis="general statement", wait_counted="yes", stage_class="not classed")]
        public, _, _ = self.build(rows)
        self.assertEqual(public["duration_as_stated"].tolist(), ["within 18 months", L.IN_WORDS])
        self.assertEqual(public["status"].tolist(), ["not classed", "not classed"])                # a class of the ERW's, or "not classed"; never the words
        self.assertEqual(public["mw"].tolist(), ["", ""])
        self.assertLessEqual(len(L.IN_WORDS), 50)

    def test_an_entity_of_the_place_list_gets_its_states_and_grid_and_a_regulators_state_comes_first(self):
        rows = [statement(entity="Oncor Electric Delivery", source_url="https://www.sec.gov/Archives/x.htm", document_type="SEC filing"),
                statement(event_id="llstmt:2", entity="El Paso Electric", source_url="https://interchange.puc.texas.gov/Documents/1.PDF", document_type="commission filing")]
        public, _, _ = self.build(rows)
        by = public.set_index("parties")
        self.assertEqual((by.loc["Oncor Electric Delivery", "state"], by.loc["Oncor Electric Delivery", "grid"], by.loc["Oncor Electric Delivery", "public_basis"]), ("TX", "ercot", "SEC filing"))
        self.assertEqual((by.loc["El Paso Electric", "state"], by.loc["El Paso Electric", "grid"]), ("TX", "none of the seven"))   # the Texas commission's state; not ERCOT's grid
        grids = {g for _, g in L.PLACE.values()}
        self.assertLessEqual(grids, {"ercot", "caiso", "pjm", "miso", "spp", "nyiso", "isone", "none of the seven", "more than one"})


class TheWords(unittest.TestCase):
    def test_the_method_note_states_the_rule_and_holds_no_forbidden_dash(self):
        with open(os.path.join(ROOT, "docs", "methods", "large_load_public.md"), encoding="utf-8") as f:
            text = f.read()
        for piece in ("a public regulatory filing and an SEC filing state facts that may be republished as facts with a link; long quotation may not", "internal until the owner rules",
                      "**No quoted text.**", "17 U.S.C. 105", "`large_load_document_verdicts`", "`large_load_public`", "Do not sum"):
            self.assertIn(piece, text)
        with open(os.path.join(ROOT, "warehouse", "derived", "large_load_public.py"), encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn(EM, text + code)
        self.assertNotIn(chr(0x2013), text + code)
        self.assertNotIn('comment="#"', code)                                                      # session 103's rule: a table is read by its header's line count

    def test_neither_table_is_loaded_and_both_sources_are_held(self):
        # session 272: large_load_public is public by the owner's ruling and loaded; the verdicts stay held
        import yaml
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = yaml.safe_load(f)
        self.assertIn(L.VERDICTS, live["catalogue_hold"])
        self.assertIn(L.SOURCE_VERDICTS, live["sources_hold"])
        self.assertNotIn(L.PUBLIC, live["catalogue_hold"])
        self.assertNotIn(L.SOURCE_PUBLIC, live["sources_hold"])


@unittest.skipUnless(all(os.path.exists(os.path.join(OUT, t + ".csv")) for t in (L.PUBLIC, L.VERDICTS, "large_load_statements")) and not os.environ.get("GITHUB_ACTIONS"),
                     "the tables are on the data machine, not on this one")
class TheTablesOnTheDataMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p, cls.v, cls.s = L.read(L.PUBLIC), L.read(L.VERDICTS), L.read("large_load_statements")

    def test_both_are_flagged_internal(self):
        # session 272: large_load_public is public by the owner's ruling of 14 October 2026; the verdicts stay internal
        for t, lic in ((L.PUBLIC, "public"), (L.VERDICTS, "internal")):
            with open(os.path.join(OUT, t + ".csv"), encoding="utf-8") as f:
                head = [ln for ln in f if ln.startswith("#")]
            self.assertTrue(any(ln.startswith(f"# License: {lic}") for ln in head), t)

    def test_every_public_row_is_its_statement_and_carries_none_of_its_words(self):
        m = self.p.merge(self.s, left_on="statement_id", right_on="event_id", suffixes=("", "_s"))
        self.assertEqual(len(m), len(self.p))
        for a, b in (("event_date", "event_date_s"), ("source_url", "source_url_s"), ("parties", "entity")):
            self.assertTrue((m[a] == m[b]).all(), a)
        self.assertTrue((m.loc[m["row_kind"] == "mw", "mw"] == m.loc[m["row_kind"] == "mw", "mw_s"]).all())
        self.assertEqual(set(self.p.columns) & WORDS, set())
        self.assertFalse(self.p["source_url"].str.contains("@|%40").any())
        self.assertTrue(self.p["source_url"].str.startswith("https://").all())
        self.assertLessEqual(int(self.p["duration_as_stated"].str.len().max()), 50)
        self.assertTrue(self.p["status"].isin(L.STAGES | {"not classed"}).all())
        self.assertFalse((self.p["grid"] == "not placed").any())                                   # every entity with a public row is in PLACE
        # no public row repeats its statement's sentence, or the stage as the document words it (where that is more than a class's name)
        long_words = m[m["stage_as_worded"].str.len() > 30]
        for _, r in long_words.iterrows():
            self.assertNotIn(r["stage_as_worded"], " | ".join(str(r[c]) for c in self.p.columns if c not in ("document_title", "parties", "entity_group")))

    def test_the_method_notes_counts(self):
        if len(self.s) != 796:
            self.skipTest("large_load_statements has changed since session 255: the note's counts are of 13 October 2026")
        p, v = self.p, self.v
        vs = v[v["of_table"] == "large_load_statements"]
        self.assertEqual((len(v), len(vs), int((v["of_table"] == "large_load_waits").sum())), (427, 301, 126))
        self.assertEqual(vs.groupby("status").size().to_dict(), {"needs a paid license": 21, "needs written permission": 18, "not public": 4, "not settled": 113, "public": 145})
        self.assertEqual((len(p), int((p["row_kind"] == "mw").sum()), int((p["row_kind"] == "wait").sum()), p["parties"].nunique(), p["entity_group"].nunique(), p["source_url"].nunique()),
                         (341, 250, 91, 67, 55, 124))
        self.assertEqual(p.groupby("public_basis").size().to_dict(), {"SEC filing": 71, "public regulatory filing": 239, "publisher's terms read in session 205": 31})
        self.assertEqual(p.groupby("grid").size().to_dict(), {"caiso": 48, "ercot": 67, "miso": 43, "more than one": 13, "none of the seven": 74, "nyiso": 5, "pjm": 72, "spp": 19})
        self.assertEqual(int((vs["address_holds_email"] == "yes").sum()), 21)
        self.assertEqual(int(vs.loc[vs["address_holds_email"] == "yes", "rows"].astype(int).sum()), 48)
        self.assertEqual(int(v.loc[v["of_table"] == "large_load_waits", "rows_public"].astype(int).sum()), 0)


if __name__ == "__main__":
    unittest.main()
