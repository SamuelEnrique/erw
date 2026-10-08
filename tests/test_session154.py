"""Session 154: rules in motion for large loads. The tags of the policy actions held (a written rule that code
applies: its terms, its exclusions, nothing municipal); the table of proceedings and orders (every row proved again:
the sentence a literal substring of the saved text, the page found by code; never MISO's site, never an address that
holds an e-mail address, never a host that is not a regulator's); the one-line reads (no number the text lacks, the
stop before the call); the site file (which grid sees which action, MISO paused with no row, nothing municipal, no
row of an internal table). Rows made for a test are marked MADE UP and live only in a temporary folder. The tests
that need the real tables or the built file skip on a machine without them. No request and no model call; the
environment is read, never set."""
import datetime as dt
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for part in ("connectors", "derived", "policy"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", part))
import large_load_rules as llr  # noqa: E402
import policy_action_tags as pat  # noqa: E402
import rule_reads as rr  # noqa: E402
import rules_in_motion as rim  # noqa: E402

EM = chr(0x2014)
FF = chr(12)
MINE = [("warehouse", "connectors", "large_load_rules.py"), ("warehouse", "derived", "policy_action_tags.py"),
        ("warehouse", "derived", "rules_in_motion.py"), ("warehouse", "policy", "rule_reads.py"),
        ("warehouse", "config", "policy_tag_rules.json"), ("warehouse", "config", "large_load_rule_terms.json"),
        ("warehouse", "config", "large_load_rule_grids.json"),
        ("docs", "methods", "policy_action_tags.md"), ("docs", "methods", "datacenter_cost.md"),
        ("docs", "accelerator", "rules_in_motion.md"), ("site", "data", "datacenter", "rules.json"),
        ("tests", "test_session154.py")]
SITE_FILE = os.path.join(ROOT, "site", "data", "datacenter", "rules.json")
ROW_KEYS = ["id", "date", "regulator", "jurisdiction", "state", "docket", "title", "row_kind", "topic", "tags",
            "status_as_worded", "status_class", "url", "page", "sentence", "read", "read_by", "read_model", "read_from",
            "why_here"]


def action(**over):
    """MADE UP: a policy action for the rule's tests (no such document)."""
    r = {"event_id": "madeup:1", "event_date": "2026-05-01", "agency": "FERC", "action_type": "notice",
         "title": "", "abstract": "", "docket": "", "source_url": "https://example.gov/x", "parties": ""}
    r.update(over)
    return r


def tags_of(**over):
    return {h["tag"]: h for h in pat.tag_action(action(**over), pat.load_rules())}


def pass_row(**over):
    """MADE UP: a pull pass's row for the connector's tests (no such order)."""
    r = {"regulator": "Federal Energy Regulatory Commission", "jurisdiction": "federal", "state": "", "grids": "PJM",
         "docket_number": "EL99-1-000", "proceeding_title": "A made-up proceeding", "row_kind": "order",
         "topic": "large-load interconnection", "document_title": "A made-up order", "document_date": "2026-03-02",
         "status_as_worded": "", "status_class": "decided", "document_url": "https://www.ferc.gov/made-up.pdf",
         "docket_url": "", "page": "2", "sentence": "The Commission directs the operator to file a made-up tariff.",
         "local_file": "raw/ferc/made-up.pdf", "retrieved_at": "2026-10-08T04:30:00Z", "verified": "yes", "notes": "",
         "terms_url": "", "collected_in": "pass A"}
    r.update(over)
    return r


class Tags(unittest.TestCase):
    def test_the_rule_file_names_the_four_tags_and_its_version(self):
        rules = pat.load_rules()
        self.assertEqual(list(rules["tags"]), ["large_load", "interconnection", "transmission_cost", "tax_credit"])
        self.assertEqual(rules["fields_matched"], ["title", "abstract"])
        self.assertTrue(rules["version"])
        self.assertTrue(rules["changes"], "the correction after the 40 and 40 is written in the rule file")

    def test_a_large_load_term_tags_and_records_the_term_and_field(self):
        t = tags_of(title="A Process to Manage Electricity Requests from Data Centers")
        self.assertEqual(t["large_load"]["matched_term"], "data centers")
        self.assertEqual(t["large_load"]["matched_field"], "title")
        t = tags_of(abstract="The rule sets standards for large-load customers.")
        self.assertEqual(t["large_load"]["matched_term"], "large load")   # a hyphen is a space
        self.assertEqual(tags_of(abstract="The rule applies to large electric generating units."), {})
        t = tags_of(abstract="The conference is on emerging large-loads and the grid.")
        self.assertEqual(t["large_load"]["matched_field"], "abstract")

    def test_a_company_name_is_not_a_topic(self):
        self.assertEqual(tags_of(title="PJM Interconnection, L.L.C.; Notice of Filing"), {})
        self.assertEqual(tags_of(title="Columbia Gas Transmission, LLC; Notice of Application"), {})

    def test_the_interconnection_of_a_gas_pipeline_is_not_the_grids(self):
        self.assertEqual(tags_of(title="Notice for the Proposed Constitution Pipeline and Wright Interconnect Projects",
                                 docket="Docket No. CP13-499-006"), {})
        self.assertEqual(tags_of(title="Wright Interconnect Project", docket="Docket No. CP13-499-006"), {})
        self.assertEqual(tags_of(abstract="The LNG project will be interconnected with the terminal.", agency="DOE"), {})
        self.assertIn("interconnection", tags_of(title="Improvements to Generator Interconnection Procedures"))

    def test_transmission_cost_needs_a_cost_word(self):
        self.assertIn("transmission_cost", tags_of(title="Electric Regional Transmission Planning and Cost Allocation"))
        self.assertIn("transmission_cost", tags_of(title="Transmission Formula Rate Processes; Notice of Workshop"))
        self.assertEqual(tags_of(title="Intent To Prepare an Environmental Impact Statement for a Transmission Line"), {})
        self.assertEqual(tags_of(title="Review of Cost Allocation for Administering the Federal Power Act"), {})
        # version 2: the rates of a balancing authority's ancillary services are not transmission's cost
        self.assertEqual(tags_of(abstract="the existing balancing authority area and transmission provider services "
                                          "formula rates are extended", agency="DOE"), {})
        self.assertIn("transmission_cost", tags_of(title="Protecting Electricity Customers: Transmission Advocacy", agency="CPUC",
                                                   action_type="press_release"))

    def test_a_bill_credit_is_not_a_tax_credit(self):
        self.assertEqual(tags_of(title="Shifting Climate Credits to High-Cost Months", agency="CPUC", action_type="press_release"), {})
        self.assertEqual(tags_of(abstract="revising the credit rating threshold for lessees", agency="Interior"), {})
        self.assertIn("tax_credit", tags_of(abstract="guidance on the clean electricity investment credit", agency="DOE"))
        self.assertIn("tax_credit", tags_of(title="Beginning of Construction for the Tax Credits of Wind and Solar", agency="DOE"))

    def test_nothing_municipal_is_ever_tagged(self):
        self.assertEqual(tags_of(title="Data Center Zoning Hearing"), {})
        self.assertEqual(tags_of(title="Large Loads", abstract="The city council will hold a hearing."), {})
        self.assertEqual(tags_of(title="Data Centers and the Grid", agency="City of Somewhere"), {})

    def test_a_docket_listed_by_number_tags_a_notice_whose_title_is_only_names(self):
        self.assertTrue(pat.docket_holds("Docket No. EL26-67-000", "EL26-67"))
        self.assertFalse(pat.docket_holds("Docket No. EL26-670-000", "EL26-67"))
        self.assertFalse(pat.docket_holds("Docket No. XEL26-67-000", "EL26-67"))
        rules = dict(pat.load_rules(), dockets={"list": [{"docket": "EL99-1", "tags": ["large_load", "interconnection"]}]})   # MADE UP docket
        hits = pat.tag_action(action(title="PJM Interconnection, L.L.C.", docket="Docket No. EL99-1-000"), rules)
        self.assertEqual({h["tag"]: (h["matched_term"], h["matched_field"]) for h in hits},
                         {"large_load": ("EL99-1", "docket"), "interconnection": ("EL99-1", "docket")})
        self.assertEqual(pat.tag_action(action(title="PJM Interconnection, L.L.C.", docket="Docket No. EL99-2-000"), rules), [])

    def test_one_row_an_action_and_tag(self):
        import pandas as pd
        acts = pd.DataFrame([action(event_id="madeup:1", title="Large Loads and Transmission Cost Allocation"),
                             action(event_id="madeup:2", title="A Hydropower Licence")])
        t = pat.build(acts, pat.load_rules(), "2026-10-08T00:00:00Z")
        self.assertEqual(sorted(t["event_id"]), ["madeup:1#large_load", "madeup:1#transmission_cost"])
        self.assertEqual(list(t.columns), pat.COLS)
        self.assertEqual(set(t["event_type"]), {"policy_tag"})

    def test_the_samples_are_drawn_by_the_seed(self):
        import pandas as pd
        acts = pd.DataFrame([action(event_id=f"madeup:{i}", title="Large Loads" if i % 5 == 0 else "A Dam") for i in range(50)])
        t = pat.build(acts, pat.load_rules(), "2026-10-08T00:00:00Z")
        a, b = pat.samples(acts, t, 4, 154), pat.samples(acts, t, 4, 154)
        self.assertEqual(a, b)
        self.assertTrue(all(i in set(t["action_event_id"]) for i in a[0]))
        self.assertTrue(all(i not in set(t["action_event_id"]) for i in a[1]))


class Connector(unittest.TestCase):
    def folder(self, text):
        """A temporary pass folder A with one saved text (MADE UP)."""
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "A", "text"))
        with open(os.path.join(d, "A", "text", "ferc__made-up.pdf.txt"), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return d

    def test_a_sentence_proves_and_its_page_is_found_here(self):
        d = self.folder("Page one of a made-up order." + FF + "Ordering paragraphs.\nThe Commission directs the operator\n to file a made-up tariff. More." + FF + "Page three.")
        why, page, path, sha, how = llr.proved(pass_row(page="7"), d, "A", {})
        self.assertEqual(why, [])
        self.assertEqual(page, "2")
        self.assertIn("the pass wrote page 7", how)
        self.assertEqual(len(sha), 64)

    def test_a_sentence_over_a_page_break_is_on_the_page_where_it_begins(self):
        d = self.folder("First." + FF + "Second page. The Commission directs the operator" + FF + "to file a made-up tariff. End.")
        why, page, _, _, _ = llr.proved(pass_row(), d, "A", {})
        self.assertEqual((why, page), ([], "2"))

    def test_a_sentence_that_is_not_in_the_text_does_not_prove(self):
        d = self.folder("The Commission directs the operator to file a different tariff.")
        why, *_ = llr.proved(pass_row(), d, "A", {})
        self.assertEqual(why, ["the sentence is not a literal substring of the saved text"])
        why, *_ = llr.proved(pass_row(local_file="raw/ferc/another.pdf"), d, "A", {})
        self.assertIn("no saved text", why[0])

    def test_a_row_must_hold_what_a_row_must(self):
        self.assertEqual(llr.row_check(pass_row()), [])
        self.assertTrue(llr.row_check(pass_row(verified="no")))
        self.assertTrue(llr.row_check(pass_row(document_date="2026-02-30")))
        self.assertTrue(llr.row_check(pass_row(document_date="")))
        self.assertTrue(llr.row_check(pass_row(topic="tax credits")))
        self.assertTrue(llr.row_check(pass_row(status_class="pending")))
        self.assertTrue(llr.row_check(pass_row(row_kind="filing")))
        self.assertTrue(llr.row_check(pass_row(docket_number="")))
        self.assertTrue(llr.row_check(pass_row(state="VA")))

    def test_only_federal_regulators_and_state_commissions(self):
        self.assertTrue(llr.row_check(pass_row(regulator="Loudoun County Board of Supervisors", jurisdiction="state", state="VA")))
        self.assertTrue(llr.row_check(pass_row(sentence="The zoning hearing is set for a made-up day.")))
        self.assertTrue(llr.row_check(pass_row(document_title="City council made-up resolution")))
        ok = pass_row(regulator="Public Utility Commission of Texas", jurisdiction="state", state="TX", grids="ERCOT",
                      document_url="https://interchange.puc.texas.gov/Documents/made-up.PDF")
        self.assertEqual(llr.row_check(ok), [])

    def test_never_misos_site_never_a_data_miner_never_an_address_with_an_e_mail(self):
        self.assertTrue(llr.row_check(pass_row(document_url="https://www.misoenergy.org/made-up.pdf")))
        self.assertTrue(llr.row_check(pass_row(document_url="https://dataminer2.pjm.com/feed/made-up")))
        at = chr(64)
        self.assertTrue(llr.row_check(pass_row(document_url="https://psc.ky.gov/pscecf/2025-00045/someone" + at + "example.com/made-up.pdf")))
        self.assertTrue(llr.row_check(pass_row(document_url="https://www.a-law-firm.com/note.pdf")))
        self.assertTrue(llr.row_check(pass_row(document_url="https://www.utilitydive.com/news/made-up/")))
        self.assertEqual(llr.row_check(pass_row(document_url="https://www.pjm.com/-/media/committees/made-up.pdf")), [])

    def test_the_whole_build_takes_proved_rows_and_lists_the_rest(self):
        import csv
        d = self.folder("One." + FF + "The Commission directs the operator to file a made-up tariff.")
        rows = [pass_row(), pass_row(sentence="A sentence the document does not hold."), pass_row()]
        with open(os.path.join(d, "A", "actions.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=llr.PASS_COLS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        b = llr.build(d, lambda m: None)
        self.assertEqual((b["read"], b["absent"]), (["A"], ["B", "C"]))
        self.assertEqual(len(b["out"]), 1)
        self.assertEqual(len(b["left"]), 2)
        r = b["out"].iloc[0]
        self.assertEqual((r["page"], r["event_type"], r["status"], r["source"]), ("2", "regulatory_order", "decided", "ferc:dockets"))
        self.assertTrue(r["event_id"].startswith("ferc:EL99-1-000:order:"))
        self.assertEqual(list(b["out"].columns), llr.COLS)

    def test_a_regulators_rows_are_public_only_by_its_own_quoted_terms(self):
        terms = {"A": {"class": "allowed", "terms_quote": "MADE UP: may be copied."},
                 "B": {"class": "public record", "terms_quote": "MADE UP: records are open."},
                 "C": {"class": "restricted", "terms_quote": "MADE UP: all rights reserved."},
                 "D": {"class": "not quoted", "terms_quote": ""},
                 "E": {"class": "allowed", "terms_quote": ""}}   # a class that needs a quotation and has none
        lic, classes = llr.license_of({"A", "B", "C", "D", "E", "F"}, terms)
        self.assertEqual(lic, {"A": "public", "B": "public", "C": "internal", "D": "internal", "E": "internal", "F": "internal"})
        self.assertEqual((classes["E"], classes["F"]), ("not quoted", "not quoted"))

    def test_the_terms_file_classes_each_of_the_eleven_with_its_sentence(self):
        terms = llr.load_terms()
        self.assertEqual(sorted(terms), sorted(v[0] for v in llr.REGULATORS.values()))
        for name, t in terms.items():
            self.assertIn(t["class"], llr.PUBLIC_CLASSES + llr.HELD_CLASSES, name)
            if t["class"] == "not quoted":
                self.assertEqual(t["terms_quote"], "")
                self.assertTrue(t["why_none"], name)
            else:
                self.assertTrue(t["terms_quote"] and t["terms_url"].startswith("https://") and len(t["sha256"]) == 64, name)
            if t["class"] in llr.HELD_CLASSES:
                self.assertTrue(t["withheld_words"].endswith("; open the document"), name)
        self.assertEqual(terms["California Public Utilities Commission"]["class"], "allowed")
        self.assertEqual(terms["Public Utility Commission of Texas"]["class"], "restricted")

    def test_each_quoted_sentence_stands_in_the_page_its_pass_saved(self):
        base = os.environ.get("ERW_RAW_ROOT") or os.path.join(ROOT, "warehouse", "raw")
        if not os.path.exists(os.path.join(base, "large_load_rules", "A", "actions.csv")):
            self.skipTest("the passes' files are not on this machine")
        n = 0
        for name, t in llr.load_terms().items():
            if t.get("saved_text"):
                with open(os.path.join(os.path.dirname(base), "..", t["saved_text"]) if False else os.path.join(base, t["saved_text"].split("warehouse/raw/", 1)[1]), encoding="utf-8", errors="replace") as f:
                    text = llr.norm(llr.html_text(f.read()))
                self.assertIn(llr.norm(t["terms_quote"]), text, name)
                n += 1
        self.assertGreaterEqual(n, 5)

    def test_every_source_of_both_tables_has_a_registry_row_with_its_license(self):
        """Coverage sets a table's license from the registry row of every source its rows name (build_coverage.py,
        events_row), so the connector registers one row a regulator beside the table's own."""
        self.assertEqual(sorted(llr.DOCKET_SYSTEMS), sorted(llr.REGULATORS))
        import pandas as pd
        lic = {v[0]: ("public" if k in ("cpuc", "orpuc") else "internal") for k, v in llr.REGULATORS.items()}   # MADE UP licenses
        part = pd.DataFrame([{"source": "cpuc:dockets"}, {"source": "cpuc:dockets"}, {"source": "orpuc:dockets"}])
        rows = llr.registry_entries(part, "large_load_rules", lic)
        self.assertEqual([(r["source"], r["publisher"], r["license"], r["tables"]) for r in rows],
                         [("cpuc:dockets", "California Public Utilities Commission", "public", ["large_load_rules"]),
                          ("orpuc:dockets", "Oregon Public Utility Commission", "public", ["large_load_rules"])])
        for r in rows:
            self.assertTrue(r["report_url"].startswith("https://") and r["document_list"].startswith("https://") and r["report"])
            self.assertNotIn(r["source"], ("puct:news", "cpuc:news"))   # the news releases' ids are another report's
        base = os.environ.get("ERW_RAW_ROOT") or os.path.join(ROOT, "warehouse", "raw")
        if not os.path.exists(os.path.join(base, "large_load_rules", "A", "actions.csv")):
            self.skipTest("the passes' files are not on this machine")
        out = llr.build(os.path.join(base, "large_load_rules"), lambda m: None)["out"]
        lic, classes = llr.license_of(set(out["regulator"]), llr.load_terms())
        registry = {}
        for name, want in (("large_load_rules", "public"), ("large_load_rules_internal", "internal")):
            part = out[out["regulator"].map(lic) == want]
            for r in llr.registry_entries(part, name, lic):
                registry[r["source"]] = r
            for src_id in set(part["source"]):   # every source value of the table has a row, with the table's license
                self.assertEqual((registry[src_id]["license"], registry[src_id]["tables"]), (want, [name]), src_id)
        self.assertEqual(sorted(registry), ["azcc:dockets", "cpuc:dockets", "ferc:dockets", "gapsc:dockets", "ilcc:dockets", "iurc:dockets",
                                            "orpuc:dockets", "papuc:dockets", "puco:dockets", "txpuc:dockets", "vascc:dockets"])
        self.assertEqual(sorted(k for k, r in registry.items() if r["license"] == "public"),
                         ["azcc:dockets", "cpuc:dockets", "ilcc:dockets", "orpuc:dockets", "papuc:dockets"])

    def test_what_a_sentence_is_cut_from(self):
        self.assertEqual(llr.sentence_from(pass_row(local_file="raw/oh/card_26-0113_all.html", document_title="Finding & Order")), ("docket card", "record"))
        self.assertEqual(llr.sentence_from(pass_row(local_file="raw/il_minutes/m03.pdf", document_title="Suspension Order, as recorded")), ("meeting minutes", "record"))
        self.assertEqual(llr.sentence_from(pass_row(local_file="raw/az_news_2026.html", document_title="ACC Approves")), ("news release", "record"))
        self.assertEqual(llr.sentence_from(pass_row(local_file="raw/ca_res_1.pdf", document_title="Draft Resolution E-0000")), ("draft resolution", "document"))
        self.assertEqual(llr.sentence_from(pass_row(document_title="ORDER GRANTING JOINT PETITION OF A COMPANY")), ("order text", "document"))
        self.assertEqual(llr.sentence_from(pass_row(document_title="Application (item 1)")), ("application or request", "document"))

    def test_flags_a_draft_is_never_decided_and_a_single_customer_contract_is_marked(self):
        d = self.folder("One." + FF + "The Commission directs the operator to file a made-up tariff.")
        import csv
        rows = [pass_row(regulator="California Public Utilities Commission", jurisdiction="state", state="CA", grids="",
                         docket_number="Resolution E-5420 (MADE UP)", document_title="Draft Resolution E-5420", status_as_worded="DRAFT",
                         status_class="decided", document_url="https://docs.cpuc.ca.gov/made-up.pdf"),
                pass_row(regulator="Illinois Commerce Commission", jurisdiction="state", state="IL", grids="", docket_number="26-0625",
                         document_url="https://icc.illinois.gov/made-up.pdf", collected_in="pass B",
                         sentence="The Commission directs the operator to file a made-up tariff.")]
        with open(os.path.join(d, "B", "actions.csv") if os.path.isdir(os.path.join(d, "B")) else os.path.join(d, "A", "actions.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=llr.PASS_COLS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        b = llr.build(d, lambda m: None)
        r = b["out"].iloc[0]
        self.assertEqual(len(b["out"]), 1)   # the Illinois order whose docket is tied only by a match across two lists is left out
        self.assertIn("not by the regulator's own words", b["left"][0]["why_not_taken"])
        ca = b["out"][b["out"]["state"] == "CA"].iloc[0]
        self.assertEqual(ca["status_class"], "not stated")   # no adopted text was read
        self.assertIn(llr.FLAG_DRAFT, ca["row_flag"])
        self.assertIn(llr.FLAG_SINGLE, ca["row_flag"])
        self.assertTrue(llr.FLAG_SINGLE.startswith(rim.SINGLE_FLAG))
        self.assertEqual(("Illinois Commerce Commission", "26-0625", "order") in llr.DOCKET_NOT_TIED, True)
        self.assertEqual(r["sentence_kind"], "document")


class Reads(unittest.TestCase):
    TEXT = "SENTENCE: A large load of 75 MW or more must post security for two years. The rule takes effect on 1 January 2027."

    def test_a_line_with_a_number_the_text_lacks_is_not_kept(self):
        self.assertEqual(rr.check_read("A load of 75 MW or more must post security.", self.TEXT), [])
        self.assertTrue(rr.check_read("A load of 100 MW or more must post security.", self.TEXT))
        self.assertTrue(rr.check_read("Loads must post security for three years.", self.TEXT))
        self.assertEqual(rr.check_read("Loads must post security for two years.", self.TEXT), [])
        self.assertEqual(rr.check_read("The rule applies from 2027.", self.TEXT), [])
        self.assertTrue(rr.check_read("The rule applies from 2028.", self.TEXT))

    def test_a_line_is_one_plain_line(self):
        self.assertTrue(rr.check_read("", self.TEXT))
        self.assertTrue(rr.check_read("A line" + EM + "with a dash.", self.TEXT))
        self.assertTrue(rr.check_read("Two\nlines.", self.TEXT))
        self.assertTrue(rr.check_read("x" * (rr.MAX_CHARS + 1), self.TEXT))
        self.assertTrue(rr.check_read("Large loads need a zoning change.", self.TEXT))
        self.assertTrue(rr.check_read("The order would permit earlier service.", self.TEXT))

    def test_a_line_about_a_restricted_regulator_quotes_nothing(self):
        text = "SENTENCE: A large load customer must execute an intermediate agreement before it is included in a study."
        quoting = "A large load customer must execute an intermediate agreement first."
        own = "Large customers have to sign an interim agreement to be studied."
        self.assertTrue(rr.check_read(quoting, text, no_quote=True))
        self.assertEqual(rr.check_read(quoting, text, no_quote=False), [])
        self.assertEqual(rr.check_read(own, text, no_quote=True), [])
        self.assertEqual(rr.copied_run("must execute an intermediate agreement", text), "")   # five words: allowed
        self.assertTrue(rr.copied_run("customer must execute an intermediate agreement", text))   # six: a quotation
        self.assertIn("never copy more than five consecutive words", rr.SYSTEM)

    def test_the_model_is_given_the_sentence_and_the_text_around_it(self):
        whole = "a" * 5000 + " The order does this. " + "b" * 5000
        got = rr.excerpt(whole, "The order does this.")
        self.assertIn("SENTENCE: The order does this.", got)
        self.assertLessEqual(len(got), rr.BEFORE + rr.AFTER + 60)
        self.assertIsNone(rr.excerpt(whole, "A sentence that is not there."))

    def test_the_stop_is_before_the_call(self):
        self.assertTrue(rr.may_call(3.60, 0.05, 3.70))
        self.assertFalse(rr.may_call(3.68, 0.05, 3.70))
        self.assertFalse(rr.may_call(3.70, 0.01, 3.70))
        src = open(os.path.join(ROOT, "warehouse", "policy", "rule_reads.py"), encoding="utf-8").read()
        self.assertLess(src.index("if not may_call(spent, res, args.stop_usd)"), src.index("client.messages.create("))
        self.assertIn('llm.client("rule_reads"', src)   # every call through the cost ledger

    def test_the_prompt_asks_for_nothing_the_text_lacks(self):
        self.assertIn("Use only the excerpt given", rr.SYSTEM)
        self.assertIn("No number", rr.SYSTEM)
        self.assertNotIn(EM, rr.SYSTEM)


class SiteFile(unittest.TestCase):
    def row(self, **over):
        """MADE UP: a row as the builder holds it before it is placed."""
        r = {"id": "madeup:1", "date": "2026-06-01", "regulator": "A made-up commission", "jurisdiction": "state",
             "state": "VA", "docket": "PUR-0000-00000", "title": "A made-up order", "row_kind": "order", "topic": "large-load tariff",
             "tags": [], "status_as_worded": "", "status_class": "decided", "url": "https://example.gov/a.pdf", "page": 1,
             "sentence": "A made-up sentence.", "read": None, "read_by": None, "read_model": None, "read_from": None, "named": []}
        r.update(over)
        return r

    def test_a_states_action_is_under_the_grids_that_serve_it(self):
        grids, federal, nowhere = rim.place([self.row(), self.row(id="madeup:2", state="IL"), self.row(id="madeup:3", state="TX"),
                                             self.row(id="madeup:4", state="CA"), self.row(id="madeup:5", state="GA")])
        self.assertEqual([r["id"] for r in grids["pjm"]], ["madeup:1", "madeup:2"])
        self.assertEqual([r["id"] for r in grids["miso"]], ["madeup:2"])
        named = rim.place([self.row(id="madeup:6", state="TX", named=["spp"]), self.row(id="madeup:7", state="IN", named=["miso"])])[0]
        self.assertEqual(([r["id"] for r in named["spp"]], named["ercot"], named["pjm"]), (["madeup:6"], [], []))   # own words win
        self.assertEqual([r["id"] for r in grids["ercot"]], ["madeup:3"])
        self.assertEqual([r["id"] for r in grids["caiso"]], ["madeup:4"])
        self.assertEqual([r["id"] for r, _ in nowhere], ["madeup:5"])
        self.assertEqual(federal, [])
        self.assertTrue(all(r["why_here"] for g in grids.values() for r in g))

    def test_a_federal_action_goes_where_its_own_words_say(self):
        grids, federal, _ = rim.place([self.row(jurisdiction="federal", state="", named=["pjm"]),
                                       self.row(id="madeup:2", jurisdiction="federal", state="", named=[])])
        self.assertEqual([r["id"] for r in grids["pjm"]], ["madeup:1"])
        self.assertEqual([r["id"] for r in federal], ["madeup:2"])
        self.assertIn("every grid", federal[0]["why_here"])

    def test_an_operator_is_named_by_its_own_words_only(self):
        self.assertEqual(rim.operators_named("PJM Interconnection, L.L.C. and Southwest Power Pool, Inc."), ["pjm", "spp"])
        self.assertEqual(rim.operators_named("a misoprostol study and spp."), [])
        self.assertEqual(rim.operators_named("ISO New England Inc.; the California Independent System Operator Corporation"), ["caiso", "isone"])
        self.assertEqual(rim.operators_named("Transmission Formula Rate Processes"), [])

    def test_twelve_months_back(self):
        self.assertEqual(rim.months_back(dt.date(2026, 10, 8), 12), dt.date(2025, 10, 8))
        self.assertEqual(rim.months_back(dt.date(2024, 2, 29), 12), dt.date(2023, 2, 28))

    def test_the_states_mapped_are_the_ten(self):
        self.assertEqual(sorted(rim.STATE_GRIDS), ["AZ", "CA", "GA", "IL", "IN", "OH", "OR", "PA", "TX", "VA"])
        for s in ("VA", "OH", "PA", "IL", "IN"):
            self.assertIn("pjm", rim.STATE_GRIDS[s][0])
        for s in ("GA", "AZ", "OR"):
            self.assertEqual(rim.STATE_GRIDS[s][0], [])

    def build_from(self, license_line, kind="order", cls="decided", date="2026-06-01", sentence="The Commission adopts a made-up tariff.", state="VA",
                   table="large_load_rules", regulator="Virginia State Corporation Commission", flag="", grids=""):
        """A build over a temporary folder holding one MADE UP table of one row."""
        import pandas as pd
        d = tempfile.mkdtemp()
        r = {c: "" for c in llr.COLS}
        r.update(event_id="vascc:PUR-0000-00000:order:0000000000", event_date=date, event_type="regulatory_" + kind, status=cls,
                 source="vascc:dockets", source_url="https://www.scc.virginia.gov/made-up.pdf", regulator=regulator,
                 jurisdiction="state", state=state, docket_number="PUR-0000-00000", proceeding_title="A made-up case", row_kind=kind,
                 topic="large-load tariff", document_title="A made-up order", status_class=cls, page="3", sentence=sentence,
                 status_as_worded="Final Order", sentence_from="order text", sentence_kind="document", row_flag=flag, grids=grids)
        with open(os.path.join(d, table + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# MADE UP for a test\n# " + license_line + "\n")
            pd.DataFrame([r], columns=llr.COLS).to_csv(f, index=False, lineterminator="\n")
        return rim.build([d], dt.date(2026, 10, 8))

    def test_an_order_of_the_last_twelve_months_is_in_motion(self):
        obj = self.build_from("License: public. MADE UP.")
        self.assertEqual(len(obj["grids"]["pjm"]["rows"]), 1)
        row = obj["grids"]["pjm"]["rows"][0]
        self.assertEqual([k for k in ROW_KEYS if k not in row], [])
        self.assertEqual((row["page"], row["read"], row["read_by"]), (3, None, None))
        self.assertEqual(self.build_from("License: public. MADE UP.", date="2025-03-01")["grids"]["pjm"]["state"], "none")
        self.assertEqual(len(self.build_from("License: public. MADE UP.", kind="proceeding", cls="open", date="2024-03-01")["grids"]["pjm"]["rows"]), 1)
        self.assertEqual(self.build_from("License: public. MADE UP.", kind="proceeding", cls="closed")["grids"]["pjm"]["state"], "none")

    def test_a_row_of_the_internal_table_shows_its_facts_and_never_its_sentence(self):
        obj = self.build_from("License: internal. MADE UP.", table="large_load_rules_internal")
        row = obj["grids"]["pjm"]["rows"][0]
        self.assertIsNone(row["sentence"])
        self.assertIsNone(row["status_as_worded"])
        self.assertEqual(row["title"], "")
        self.assertTrue(row["sentence_withheld"].endswith("; open the document"))
        self.assertEqual((row["date"], row["docket"], row["status_class"], row["topic"], row["url"]),
                         ("2026-06-01", "PUR-0000-00000", "decided", "large-load tariff", "https://www.scc.virginia.gov/made-up.pdf"))
        self.assertNotIn("The Commission adopts a made-up tariff.", json.dumps(obj))
        shown = self.build_from("License: public. MADE UP.")["grids"]["pjm"]["rows"][0]
        self.assertEqual((shown["sentence"], shown["status_as_worded"], shown["sentence_withheld"]), ("The Commission adopts a made-up tariff.", "Final Order", None))

    def test_a_table_whose_license_is_not_its_names_is_refused(self):
        with self.assertRaises(RuntimeError):
            self.build_from("License: public. MADE UP.", table="large_load_rules_internal")
        with self.assertRaises(RuntimeError):
            self.build_from("License: internal. MADE UP.")

    def test_the_owners_two_switches(self):
        name = "Virginia State Corporation Commission"
        old = rim.OFF_PAGE_REGULATORS, rim.SHOW_SENTENCE_REGULATORS
        try:
            rim.OFF_PAGE_REGULATORS = (name,)
            self.assertEqual(self.build_from("License: internal. MADE UP.", table="large_load_rules_internal")["grids"]["pjm"]["state"], "none")
            rim.OFF_PAGE_REGULATORS, rim.SHOW_SENTENCE_REGULATORS = (), (name,)
            row = self.build_from("License: internal. MADE UP.", table="large_load_rules_internal")["grids"]["pjm"]["rows"][0]
            self.assertEqual((row["sentence"], row["sentence_withheld"]), ("The Commission adopts a made-up tariff.", None))
        finally:
            rim.OFF_PAGE_REGULATORS, rim.SHOW_SENTENCE_REGULATORS = old
        self.assertEqual(old, ((), ()))   # as shipped: neither switch is thrown

    def test_miso_is_paused_and_holds_no_row(self):
        obj = self.build_from("License: public. MADE UP.", state="IL")
        self.assertEqual(obj["grids"]["miso"], {"state": "paused", "words": "paused while terms are reviewed", "rows": []})
        self.assertEqual(len(obj["grids"]["pjm"]["rows"]), 1)

    def test_a_row_with_a_word_the_block_never_shows_is_kept_out_and_counted(self):
        obj = self.build_from("License: public. MADE UP.", sentence="The made-up order would permit earlier service.")
        self.assertEqual(obj["grids"]["pjm"]["state"], "none")
        self.assertEqual(obj["not_on_page"]["count"], 1)
        # a withheld sentence is not shown, so its words keep no row out
        obj = self.build_from("License: internal. MADE UP.", table="large_load_rules_internal", sentence="The made-up order would permit earlier service.")
        self.assertEqual(len(obj["grids"]["pjm"]["rows"]), 1)

    def test_a_state_with_no_grid_on_the_page_is_counted_not_shown(self):
        obj = self.build_from("License: public. MADE UP.", state="GA")
        self.assertTrue(all(not g["rows"] for g in obj["grids"].values()))
        self.assertIn("GA: no grid on the page", obj["not_on_page"]["by_reason"])

    def test_the_ten_are_ten_at_most_one_a_docket_and_this_month_first(self):
        import pandas as pd
        d = tempfile.mkdtemp()
        rows = []
        for i in range(14):   # MADE UP: fourteen dockets of five regulators
            reg, st, ns = [("Virginia State Corporation Commission", "VA", "vascc"), ("Public Utility Commission of Texas", "TX", "txpuc"),
                           ("Federal Energy Regulatory Commission", "", "ferc"), ("Georgia Public Service Commission", "GA", "gapsc"),
                           ("Public Utilities Commission of Ohio", "OH", "puco")][i % 5]
            r = {c: "" for c in llr.COLS}
            r.update(event_id=f"{ns}:D{i}:order:{i:010d}", event_date=f"2026-{(i % 9) + 1:02d}-15", event_type="regulatory_order",
                     status="decided", source=f"{ns}:dockets", source_url=f"https://example.gov/{i}.pdf", regulator=reg,
                     jurisdiction="federal" if ns == "ferc" else "state", state=st, docket_number=f"D{i}", row_kind="order",
                     topic="large-load tariff" if i % 2 else "interconnection reform", document_title=f"A made-up order {i}",
                     status_class="decided", sentence=f"A made-up sentence {i}.", notes="Comments due October 20, 2026." if i == 3 else "")
            rows.append(r)
        rows.append(dict(rows[0], event_id="vascc:D0:order:9999999999", event_date="2026-09-30", sentence="A later made-up sentence."))
        with open(os.path.join(d, "large_load_rules.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# MADE UP for a test\n# License: public. MADE UP.\n")
            pd.DataFrame(rows, columns=llr.COLS).to_csv(f, index=False, lineterminator="\n")
        single = dict(rows[1], event_id="txpuc:D99:order:1111111111", docket_number="D99", event_date="2026-10-07",
                      row_flag="single-customer contract or agreement, not a rule for others")
        rows.append(single)
        with open(os.path.join(d, "large_load_rules.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# MADE UP for a test\n# License: public. MADE UP.\n")
            pd.DataFrame(rows, columns=llr.COLS).to_csv(f, index=False, lineterminator="\n")
        ten, pool = rim.ten_rules([d], dt.date(2026, 10, 8))
        self.assertNotIn("D99", [r["docket"] for r in ten])   # a contract with one customer sets no rule for others
        self.assertEqual((len(ten), pool), (10, 14))
        self.assertEqual(len({(r["regulator"], r["docket"]) for r in ten}), 10)
        self.assertTrue(all(sum(1 for r in ten if r["regulator"] == x["regulator"]) <= rim.TEN_PER_REGULATOR for x in ten))
        flags = [r["this_month"] for r in ten]
        self.assertEqual(flags, sorted(flags, reverse=True))   # this month first
        self.assertIn("D3", [r["docket"] for r in ten if r["this_month"]])   # a deadline within the month
        d0 = next(r for r in ten if r["docket"] == "D0")
        self.assertEqual(d0["sentence"], "A later made-up sentence.")   # a docket's newest row in motion
        self.assertEqual([r["rank"] for r in ten], list(range(1, 11)))

    def test_dates_a_row_states(self):
        self.assertEqual(rim.dates_in("Comments due October 20, 2026; hearing 2026-11-03; February 30, 2026"),
                         [dt.date(2026, 10, 20), dt.date(2026, 11, 3)])

    def test_the_built_file_keeps_the_contract(self):
        if not os.path.exists(SITE_FILE):
            self.skipTest("site/data/datacenter/rules.json is not built on this machine")
        with open(SITE_FILE, encoding="utf-8") as f:
            obj = json.load(f)
        self.assertEqual(obj["window_months"], 12)
        self.assertEqual(sorted(obj["grids"]), sorted(rim.GRIDS))
        self.assertEqual(obj["grids"]["miso"], {"state": "paused", "words": "paused while terms are reviewed", "rows": []})
        rows = [r for g in obj["grids"].values() for r in g["rows"]] + obj["federal_all_grids"]
        for g in obj["grids"].values():
            self.assertIn(g["state"], ("shown", "paused", "none"))
            if g["state"] == "none":
                self.assertTrue(g["why"])
            if g["state"] == "shown":
                self.assertTrue(g["rows"])
                self.assertEqual([r["date"] for r in g["rows"]], sorted((r["date"] for r in g["rows"]), reverse=True))
        for r in rows:
            self.assertEqual([k for k in ROW_KEYS if k not in r], [], r["id"])
            self.assertRegex(r["date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertGreaterEqual(r["date"], "2015-01-01")
            self.assertIn(r["jurisdiction"], ("federal", "state"))
            self.assertIn(r["row_kind"], ("proceeding", "order", "federal action"))
            self.assertIn(r["status_class"], ("open", "decided", "closed", "not stated"))
            self.assertTrue(r["url"].startswith("http"), r["id"])
            self.assertNotIn("misoenergy.org", r["url"])
            self.assertTrue(r["regulator"] and r["why_here"], r["id"])
            if r["sentence"] is None:   # a regulator whose terms restrict copying, or were not read: facts only
                self.assertIsNone(r["status_as_worded"], r["id"])
                self.assertEqual(r["title"], "", r["id"])
                self.assertTrue(r["sentence_withheld"].endswith("; open the document"), r["id"])
                self.assertIn(r["terms_class"], ("restricted", "not quoted"), r["id"])
            else:
                self.assertIsNone(r["sentence_withheld"], r["id"])
                self.assertNotIn(r["terms_class"], ("restricted", "not quoted"), r["id"])
            self.assertTrue(r["sentence_from"], r["id"])
            if r["read"] is None:
                self.assertEqual((r["read_by"], r["read_model"]), (None, None), r["id"])
            else:
                self.assertEqual(r["read_by"], "model", r["id"])   # a read is always marked as a model's
                self.assertTrue(r["read_model"] and r["read_from"], r["id"])
            shown = " ".join(str(r[k] or "") for k in ("title", "sentence", "read", "status_as_worded")).lower()
            for w in rim.MUNICIPAL_WORDS:
                self.assertNotIn(w, shown, r["id"])
        for r in obj["federal_all_grids"]:
            self.assertEqual(r["jurisdiction"], "federal")
        for s in obj["sources"]:
            self.assertTrue(s["regulator"] and s["terms_url"] and s["terms_quote"] and s["terms_class"])
        self.assertEqual(obj["not_on_page"]["count"], sum(obj["not_on_page"]["by_reason"].values()))


class Mapping(unittest.TestCase):
    """The mapping corrected (session 154): a row about one utility goes under that utility's own operator."""

    def row(self, state, placing, named=()):
        return {"id": f"madeup:{state}:{placing[0]}:{placing[1]['utility'] if placing[1] else ''}", "date": "2026-06-01", "jurisdiction": "state",
                "state": state, "named": list(named), "placing": placing}   # MADE UP

    def test_a_caption_says_whether_a_row_is_one_utilitys_or_a_statewide_rule(self):
        us = rim.load_utilities()
        scope, u = rim.utility_of("TX", "Application of El Paso Electric Company for Approval of a Tariff | 59611", us)
        self.assertEqual((scope, u["operator"]), ("one utility", None))
        scope, u = rim.utility_of("TX", "Application of Southwestern Electric Power Company for Authority to Amend Tariffs", us)
        self.assertEqual((scope, u["operator"]), ("one utility", "SPP"))
        self.assertEqual(rim.utility_of("TX", "Application of Southwestern Public Service Company | 60332", us)[1]["operator"], "SPP")
        self.assertEqual(rim.utility_of("TX", "Rulemaking to Implement Large Load Interconnection Standards under PURA 37.0561 | 58481", us), ("statewide", None))
        self.assertEqual(rim.utility_of("TX", "Review of ERCOT's Interconnection Processes for Large Loads | 59142", us), ("statewide", None))
        self.assertEqual(rim.utility_of("VA", "Ex Parte: Electric Utilities and Data Center Load Growth", us), ("statewide", None))
        self.assertEqual(rim.utility_of("IL", "Ameren Illinois Company d/b/a Ameren Illinois: revisions", us)[1]["operator"], "MISO")
        self.assertEqual(rim.utility_of("IL", "Illinois Commerce Commission on its own motion v. Commonwealth Edison Company", us)[1]["operator"], "PJM")
        self.assertEqual(rim.utility_of("IN", "NIPSCO Generation LLC: generation resources", us)[1]["operator"], "MISO")
        self.assertEqual(rim.utility_of("IN", "Indiana Michigan Power Company: modifications", us)[1]["operator"], "PJM")
        self.assertEqual(rim.utility_of("CA", " | Resolution E-5420 (PG&E Advice Letter 7569-E)", us)[1]["operator"], "CAISO")
        self.assertEqual(rim.utility_of("TX", "Application of A Made-Up Power Company for a Tariff", us), ("one utility, not listed", None))
        self.assertEqual(rim.utility_of("VA", "Application of El Paso Electric Company", us)[0], "one utility, not listed")   # a name counts in its own state only

    def test_a_row_about_one_utility_goes_under_that_utilitys_operator_or_nowhere(self):
        us = {u["utility"]: u for u in rim.load_utilities()}
        rows = [self.row("TX", ("one utility", us["El Paso Electric Company"])),
                self.row("TX", ("one utility", us["Southwestern Electric Power Company"])),
                self.row("TX", ("statewide", None)),
                self.row("IL", ("one utility", us["Ameren Illinois Company"])),
                self.row("IL", ("one utility", us["Commonwealth Edison Company"])),
                self.row("IL", ("one utility, not listed", None)),
                self.row("IN", ("one utility, not listed", None), named=["pjm"]),
                self.row("TX", ("statewide", None), named=["ercot"])]
        rows[2]["id"], rows[7]["id"] = "madeup:TX:rule", "madeup:TX:rule named"
        grids, federal, nowhere = rim.place(rows)
        self.assertEqual(sorted(r["id"] for r in grids["ercot"]), ["madeup:TX:rule", "madeup:TX:rule named"])
        self.assertEqual([r["utility"] for r in grids["spp"]], ["Southwestern Electric Power Company"])
        self.assertEqual([r["utility"] for r in grids["miso"]], ["Ameren Illinois Company"])   # and MISO shows no row
        self.assertEqual([r["utility"] for r in grids["pjm"]], ["Commonwealth Edison Company", None])
        self.assertEqual([why for _, why in nowhere], ["El Paso Electric Company: in no organized market on the page",
                                                       "IL: names a utility whose operator the mapping file does not state"])
        self.assertTrue(all(r["scope"] in ("one utility", "statewide") for g in grids.values() for r in g))

    def test_the_mapping_file_states_each_operator_with_its_source(self):
        us = rim.load_utilities()
        with open(rim.GRIDS_FILE, encoding="utf-8") as f:
            sources = json.load(f)["sources"]
        self.assertGreaterEqual(len(us), 20)
        for u in us:
            self.assertIn(u["operator"], (None, "ERCOT", "PJM", "MISO", "CAISO", "NYISO", "ISO-NE", "SPP"), u["utility"])
            self.assertTrue(u["why"] and u["names"] and u["state"] in rim.STATE_GRIDS, u["utility"])
            self.assertTrue(u["source"] == "stated plainly" or sources[u["source"]].startswith("https://www.ferc.gov/"), u["utility"])
        base = os.environ.get("ERW_RAW_ROOT") or os.path.join(ROOT, "warehouse", "raw")
        if not os.path.exists(os.path.join(base, "large_load_rules", "A", "text", "ferc__EL26-67-000.pdf.txt")):
            self.skipTest("the saved FERC orders are not on this machine")
        n = 0
        for u in us:   # a utility sourced to a FERC caption stands by name in that order's first pages
            if u["source"] != "stated plainly":
                with open(os.path.join(base, "large_load_rules", "A", "text", f"ferc__{u['source']}-000.pdf.txt"), encoding="utf-8", errors="replace") as f:
                    caption = llr.norm(f.read())[:6000]
                self.assertTrue(any(name in caption for name in u["names"]), u["utility"])
                n += 1
        self.assertGreaterEqual(n, 14)

    def test_the_built_file_places_no_utility_under_another_operator(self):
        if not os.path.exists(SITE_FILE):
            self.skipTest("site/data/datacenter/rules.json is not built on this machine")
        with open(SITE_FILE, encoding="utf-8") as f:
            obj = json.load(f)
        ops = {u["utility"]: u["operator"] for u in rim.load_utilities()}
        for g, v in obj["grids"].items():
            for r in v["rows"]:
                if r["jurisdiction"] == "state":
                    self.assertIn(r["scope"], ("one utility", "statewide"), r["id"])
                    if r.get("utility"):
                        self.assertEqual(rim.KEY_OF[ops[r["utility"]]], g, r["id"])
        shown = json.dumps(obj["grids"]["ercot"])
        for name in ("El Paso Electric", "Southwestern Electric Power", "Southwestern Public Service"):
            self.assertNotIn(name, shown)
        self.assertIn("El Paso Electric Company: in no organized market on the page", obj["not_on_page"]["by_reason"])


class Files(unittest.TestCase):
    def test_no_em_dash_in_this_sessions_files(self):
        for parts in MINE:
            path = os.path.join(ROOT, *parts)
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                self.assertNotIn(EM, f.read(), parts)

    def test_no_request_and_no_model_call_in_the_connector_the_tags_or_the_site_file(self):
        for parts in MINE[:3]:
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
                src = f.read()
            for word in ("import requests", "urllib.request", "import llm", "anthropic", "httpx"):
                self.assertNotIn(word, src, parts)

    def test_the_coverage_build_knows_the_new_tables(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"), encoding="utf-8") as f:
            src = f.read()
        for name in ("large_load_rules", "large_load_rule_reads", "policy_action_tags"):
            self.assertIn(name, src)
        import importlib.util   # by path: warehouse/validate holds a script of the same name that RUNS the builder
        import re
        spec = importlib.util.spec_from_file_location("erw_build_coverage_154", os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"))
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        for name in ("large_load_rules", "large_load_rules_internal", "large_load_rule_reads"):
            self.assertEqual(bc.tier_by_rule(name, "no"), "model_extracted", name)   # collected or written by a model
            self.assertEqual([sec for pat, sec in bc.SECTOR_RULES if re.match(pat, name)][:1], ["power;datacenters"], name)
        self.assertEqual([sec for pat, sec in bc.SECTOR_RULES if re.match(pat, "policy_action_tags")][:1], ["news"])
        # The hold lists of warehouse/supabase/live_set.yaml are NOT changed on this branch: session 153's test forbids
        # touching that file before the freeze ends, and session 102's asks that a held source be in the registry
        # first. The lines to add at the landing are in the session's report (hand-over).

    def test_the_real_tags_when_the_tables_are_held(self):
        main = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
        path = os.path.join(main, "policy_actions.csv")
        if not os.path.exists(path):
            self.skipTest("policy_actions is not on this machine")
        acts = pat.read_events(path)
        t = pat.build(acts, pat.load_rules(), "2026-10-08T00:00:00Z")
        self.assertFalse(t["event_id"].duplicated().any())
        self.assertTrue(set(t["tag"]) <= set(pat.load_rules()["tags"]))
        by = acts.set_index("event_id")
        for r in t.to_dict("records"):   # a person can redo it: the term stands in the field it names
            self.assertTrue(pat.has(r["matched_term"], pat.norm(by.loc[r["action_event_id"], r["matched_field"]])), r["event_id"])


if __name__ == "__main__":
    unittest.main()
