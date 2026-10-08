"""Session 151: the large-load statements, from forty entities to eighty, and the wait figures. The rule on rows made
for the test and on a few saved real rows (a sentence proved again against the pass's saved text; a wait row has a
duration and a sentence; a statement collected by two passes is one row; a third party's copy kept and flagged; a
duration that is not a load's wait kept, classed none and never counted as one); the distinct wait figures (one
duration as written, about one entity, on one stage, for one kind of load; counted once across documents and bodies);
nothing summed across entities; the counts in the one-page summary equal the table's. The tests that need the passes'
files skip on a machine without the raw store (it is not in the repository): they look under warehouse/raw of this
copy, or under the directory the environment variable ERW_RAW_ROOT names. No request and no model call."""
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import large_load_statements as ll  # noqa: E402

AT = chr(64)
ADDRESS = re.compile(r"[\w.+-]+(?:%40|" + AT + r")[\w-]+\.[a-z]{2,}", re.I)
BUILT = {}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def raw_root():
    """The directory that holds the passes' files, or None on a machine without them. Reads the environment, never sets it."""
    for d in (os.environ.get("ERW_RAW_ROOT"), os.path.join(ROOT, "warehouse", "raw")):
        if d and os.path.exists(os.path.join(d, "large_load_statements", "W1", "statements.csv")) and os.path.exists(os.path.join(d, "large_load_pilot", "A", "statements.csv")):
            return d
    return None


def built():
    """The table built once from the passes' files, with nothing written."""
    if "b" not in BUILT:
        BUILT["b"] = ll.build(ll.passes_under(raw_root()), "2026-10-08T00:00:00Z", lambda m: None)
    return BUILT["b"]


def row(**over):
    r = {"entity": "ERCOT", "entity_type": "grid operator", "parent_company": "", "document_title": "A filing", "document_type": "commission filing",
         "document_date": "2025-05-01", "document_url": "https://example.org/filing.pdf", "page_or_slide": "", "mw": "", "quantity_as_written": "approximately 220 days",
         "stage_as_worded": "in-service", "load_type_as_worded": "new large loads", "place_as_worded": "", "time_horizon_as_worded": "",
         "wait_or_lead_time_as_worded": "approximately 220 days", "sentence": "Loads were delayed in coming in service on average by approximately 220 days.", "local_file": "x",
         "retrieved_at": "2026-10-08T00:30:00Z", "verified": "yes", "notes": "MEASURED: an average of what happened.", "collected_in": "pass W1", "page": "8", "row_kind": "wait",
         "stage_class_proposed": "5 under construction or energized", "stage_class_reason": "a delay in coming in service", "terms_url": ""}
    r.update(over)
    return r


def out_row(**over):
    r = row(**over)
    r["entity_group"] = ll.group_of(r["entity"])
    return ll.to_row(r, "2026-10-08T01:00:00Z")


class Rule(unittest.TestCase):
    def test_eighty_entities_the_forty_first_and_the_bodies_outside_them(self):
        self.assertEqual(len(ll.GROUPS), 80)
        self.assertEqual(list(ll.GROUPS)[:40], ll.FORTY_141)
        self.assertNotIn("MISO", " ".join(ll.GROUPS) + " ".join(ll.OUTSIDE))
        self.assertEqual(len(ll.PASSES_151), 11)
        self.assertFalse(set(ll.GROUPS) & set(ll.OUTSIDE))
        self.assertEqual(ll.group_of("Public Service Company of New Mexico"), "TXNM Energy")
        self.assertEqual(ll.group_of("Public Service Company of Colorado"), "Xcel Energy")
        self.assertEqual(ll.group_of("National Grid (Niagara Mohawk Power Corporation)"), "National Grid")
        self.assertEqual(ll.group_of("Dominion Energy Virginia (Virginia Electric and Power Company)"), "Dominion Energy Virginia")
        self.assertIn(ll.group_of("Google LLC (about Dominion Energy Virginia)"), ll.OUTSIDE)
        self.assertEqual(out_row()["entity_list"], "the eighty")
        self.assertEqual(out_row(entity="Federal Energy Regulatory Commission")["entity_list"], "outside the eighty")

    def test_a_wait_row_has_a_duration_and_a_sentence(self):
        good, failed = ll.checked([row(), row(sentence=""), row(quantity_as_written="about 300 days")], lambda m: None)
        self.assertEqual((len(good), failed), (1, 2))   # no sentence; a duration that is not in the sentence
        r = out_row()
        self.assertEqual((r["row_kind"], r["mw"], r["wait_basis"], r["wait_counted"], r["load_scope"]), ("wait", "", "measured", "yes", ll.LARGE_LOADS))
        self.assertEqual(r["wait_figure"], "ERCOT | 220 day | 5 | large loads")
        self.assertEqual(out_row(row_kind="mw", mw="220", quantity_as_written="220 MW", sentence="It is 220 MW.")["wait_basis"], "")   # a megawatt row carries none of it
        # an undated PDF is filed on the day it was read, and says so
        self.assertEqual(out_row(document_date="")["event_date_basis"], "undated document: the day it was read")

    def test_the_basis_is_the_collecting_passes_word(self):
        self.assertEqual(ll.basis_of(row()), "measured")
        self.assertEqual(ll.basis_of(row(notes="Expected, not measured: a target.")), "expected")
        self.assertEqual(ll.basis_of(row(notes="EXPECTED (a general statement of how long it takes, not a count of cases).")), "general statement")
        self.assertEqual(ll.basis_of(row(notes="MEASURED only loosely: in some cases.")), "general statement")
        self.assertEqual(ll.basis_of(row(notes="Slide line. A general statement of experience, not a measured average.")), "general statement")
        self.assertEqual(ll.basis_of(row(entity="Texas-New Mexico Power", quantity_as_written="years", notes="x")), "what happened, no duration written")
        self.assertEqual(set(ll.BASES), {"measured", "what happened, no duration written", "general statement", "expected"})

    def test_a_duration_as_written(self):
        same = [("approximately nine months", "nine months"), ("90-day", "90 calendar days"), ("six (6) months", "six months"), ("9 to 12 months", "9-12 months"),
                ("within eight months", "8 months"), ("5-6 year", "5-6 years"), ("one hundred eighty (180) days", "180 Calendar Days")]
        for a, b in same:
            self.assertEqual(ll.duration_key(a), ll.duration_key(b), (a, b))
        for a, b in [("180 days", "six months"), ("90 days", "90 business days"), ("up to 5 years", "5 years"), ("3-5 years", "3-5+ years"), ("at least 12 months", "12 months")]:
            self.assertNotEqual(ll.duration_key(a), ll.duration_key(b), (a, b))   # nothing converted, and a bound is kept

    def test_what_is_not_a_loads_wait_is_kept_classed_none_and_never_counted(self):
        lead = out_row(entity="Austin Energy", quantity_as_written="3-5 years", stage_as_worded="building generation", sentence="Generation takes 3-5 years.",
                       wait_or_lead_time_as_worded="3-5 years", notes="A general statement.", stage_class_proposed="5 under construction or energized")
        self.assertEqual((lead["stage_class"], lead["wait_counted"]), ("none", "no: " + ll.LEAD_TIME))
        self.assertIn("the collecting pass proposed", lead["stage_class_basis"])
        self.assertEqual(lead["status"], "building generation")   # the document's own words stay
        vote = out_row(entity="Louisiana Public Service Commission", quantity_as_written="8 months", stage_as_worded="the Commission's vote", sentence="A vote within 8 months.",
                       wait_or_lead_time_as_worded="8 months", notes="EXPECTED: a target.")
        self.assertEqual(vote["wait_counted"], "no: " + ll.APPROVAL)
        rate = out_row(entity="Rappahannock Electric Cooperative", quantity_as_written="one batch per year", stage_as_worded="DE BATCH POSITION",
                       sentence="Queue advances one batch per year.", wait_or_lead_time_as_worded="one batch per year", notes="EXPECTED, not measured.")
        self.assertEqual(rate["wait_counted"], "no: " + ll.RATE)
        self.assertTrue(lead["wait_figure"].endswith("not a load's wait"))
        kinds = {k for _, _, _, k in ll.NOT_A_LOADS_WAIT}
        self.assertEqual(kinds, {ll.LEAD_TIME, ll.APPROVAL, ll.RATE})

    def test_flags_a_third_partys_copy_a_statement_about_another_and_an_address_with_a_filers_address(self):
        copy = out_row(entity="Minnesota Power (ALLETE)", document_url="https://hermantownmn.com/letter.pdf")
        self.assertIn("a third party's copy", copy["source_flag"])
        about = out_row(entity="Federal Energy Regulatory Commission", quantity_as_written="approximately nine months", sentence="It takes approximately nine months.",
                        wait_or_lead_time_as_worded="approximately nine months", stage_class_proposed="2 study or engineering")
        self.assertIn("a statement about another entity: New York ISO", about["source_flag"])
        self.assertEqual(about["wait_figure"], "New York ISO | 9 month | 2 | large loads")
        folder = "someone" + "%40" + "utility.example"   # put together here, so that this file holds no address
        ky = out_row(entity="East Kentucky Power Cooperative", document_url="https://psc.example.gov/pscecf/2025-00001/" + folder + "/01/answers.pdf")
        self.assertIn("e-mail address as a folder name", ky["source_flag"])
        self.assertNotIn("e-mail", out_row(document_url="https://www.scc.example.gov/docketsearch/DOCS/8" + AT + "jk01!.PDF")["source_flag"])   # a file name, not an address
        self.assertEqual(out_row(document_url="https://docs.example.gov/Efile/G000/M604/K023/604023792.PDF")["load_scope"], ll.ALL_DISTRIBUTION)

    def test_a_statement_collected_by_two_passes_is_one_row(self):
        o = row(entity="National Grid (United States utilities)", quantity_as_written="up to eight years", sentence="Upgrades can take up to eight years to construct.",
                wait_or_lead_time_as_worded="up to eight years", document_url="https://example.org/ViewDoc.aspx?DocRefId={C0F2}", page="22", collected_in="pass O")
        w2 = dict(o, entity="National Grid (Niagara Mohawk Power Corporation)", document_url="https://example.org/ViewDoc.aspx?DocRefId=C0F2", collected_in="pass W2")
        taken, left = ll.choose([o, w2])
        self.assertEqual([r["collected_in"] for r in taken], ["pass W2"])   # two names of one entity, one sentence of one document: one row, the later pass's
        self.assertIn("collected again in pass W2", left[0]["why_not_taken"])
        # a statement an earlier pass holds (the same document, page and figure; a line number apart) stays as held
        e = row(entity="Public Service Company of Colorado", quantity_as_written="at least 180 days", sentence="The study takes at least 180 days 16 assuming all is given.",
                wait_or_lead_time_as_worded="at least 180 days", page="48", collected_in="pass E")
        w3 = dict(e, sentence="The study takes at least 180 days assuming all is given.", collected_in="pass W3")
        taken, left = ll.choose([e, w3])
        self.assertEqual([r["collected_in"] for r in taken], ["pass E"])
        self.assertIn("held already from pass E", left[0]["why_not_taken"])
        # a third party's copy named in COPY_HOSTS is taken; session 141's hosts are still not
        taken, left = ll.choose([row(document_url="https://mrec.org/deck.pdf"), row(document_url="https://ceae.ku.edu/deck.pdf", sentence="Another: approximately 220 days.")])
        self.assertEqual((len(taken), len(left)), (1, 1))


class Figures(unittest.TestCase):
    def table(self):
        import pandas as pd
        rows = [
            out_row(collected_in="pass C", entity="New York ISO", quantity_as_written="nine months", sentence="An estimate is nine months.", wait_or_lead_time_as_worded="nine months",
                    notes="EXPECTED, an estimate.", stage_class_proposed="2 study or engineering"),
            out_row(collected_in="pass W1", entity="Federal Energy Regulatory Commission", quantity_as_written="approximately nine months", sentence="NYISO notes approximately nine months.",
                    wait_or_lead_time_as_worded="approximately nine months", notes="GENERAL STATEMENT.", stage_class_proposed="2 study or engineering"),
            out_row(collected_in="pass W1"),
            out_row(collected_in="pass I", entity="Southern California Edison", quantity_as_written="480", sentence="Average 480 171 338.", wait_or_lead_time_as_worded="480",
                    notes="Measured, a table row.", stage_class_proposed="none", document_url="https://docs.example.gov/604030059.PDF"),
            out_row(collected_in="pass K", entity="Austin Energy", quantity_as_written="3-5 years", stage_as_worded="building generation", sentence="Generation takes 3-5 years.",
                    wait_or_lead_time_as_worded="3-5 years", notes="A general statement."),
            out_row(collected_in="pass K", row_kind="mw", mw="500", entity="Austin Energy", quantity_as_written="500 MW", sentence="Requests of 500 MW.", notes="", stage_class_proposed="1 request or inquiry"),
        ]
        return ll.mark_holders(pd.DataFrame(rows, columns=ll.COLS))

    def test_one_figure_in_two_bodies_words_counts_once_under_the_row_that_held_it_first(self):
        t = self.table()
        nine = t[t["wait_figure"] == "New York ISO | 9 month | 2 | large loads"]
        self.assertEqual(len(nine), 2)
        self.assertEqual(list(nine.loc[nine["wait_figure_holder"] == "yes", "collected_in"]), ["pass C"])
        c = ll.wait_counts(t)
        self.assertEqual((c["wait_rows"], c["figures"], c["held_before"], c["new"]), (5, 4, 1, 3))
        self.assertEqual(c["by_scope"], {"large loads": 3, "all distribution": 1})
        self.assertEqual((c["by_basis"]["measured"], c["measured_large"], c["measured_all_distribution"]), (2, 1, 1))
        self.assertEqual((c["not_a_loads_wait"], c["large_and_counted"]), (1, 2))
        self.assertEqual(sum(c["by_stage"].values()), c["figures"])
        self.assertEqual(sum(c["by_basis"].values()), c["figures"])
        self.assertEqual(sum(c["by_entity"].values()), c["figures"])

    def test_nothing_is_summed_across_entities(self):
        text = src("warehouse", "connectors", "large_load_statements.py")
        self.assertIn("DO NOT SUM across rows or entities", text)
        self.assertIn("durations are never added or averaged across rows", text)
        self.assertIsNone(re.search(r"\[\"mw\"\]\s*\.\s*(sum|mean)\(|mw_low\"\]\s*\.\s*sum\(", text))   # no megawatts are ever added or averaged in the connector
        c = ll.wait_counts(self.table())

        def leaves(x):
            return [v for y in x.values() for v in (leaves(y) if isinstance(y, dict) else [y])]
        self.assertTrue(all(isinstance(v, int) and v <= c["wait_rows"] for v in leaves(c)))   # every number it returns is a count of statements


class Saved(unittest.TestCase):
    """On the saved real rows: skipped where the raw store is absent."""

    def setUp(self):
        if raw_root() is None:
            self.skipTest("the passes' files are not on this machine (warehouse/raw, or ERW_RAW_ROOT)")

    def test_real_rows_prove_again_against_the_saved_text_and_a_changed_one_does_not(self):
        base = os.path.join(raw_root(), "large_load_statements")
        rows = ll.read_pass("W1", base)
        ercot = next(r for r in rows if r["entity"] == "ERCOT" and r["quantity_as_written"] == "approximately 220 days")
        cache = {}
        self.assertEqual(ll.proved(ercot, base, "W1", cache)[0], [])
        self.assertIn("approximately 220 days", ercot["sentence"])
        self.assertTrue(ll.figure_in_sentence(ercot))
        self.assertNotEqual(ll.proved(dict(ercot, sentence=ercot["sentence"].replace("220", "120")), base, "W1", cache)[0], [])
        self.assertNotEqual(ll.proved(dict(ercot, page=str(int(ercot["page"]) + 1)), base, "W1", cache)[0], [])
        for letter in ("I", "N", "W2"):
            cache = {}
            for r in ll.read_pass(letter, base)[:12]:
                self.assertEqual(ll.proved(r, base, letter, cache)[0], [], (letter, r["quantity_as_written"]))

    def test_the_table_from_the_passes(self):
        b = built()
        t = b["out"]
        self.assertEqual(b["unproved"], [])
        self.assertFalse(t["event_id"].duplicated().any())
        self.assertEqual(list(t.columns), ll.COLS)
        wait = t[t["row_kind"] == "wait"]
        self.assertTrue((wait["mw"] == "").all() and (wait["quantity_as_written"] != "").all() and (wait["sentence"] != "").all())
        self.assertTrue(wait["wait_basis"].isin(ll.BASES).all() and (wait["wait_figure"] != "").all())
        for _, r in wait.iterrows():
            self.assertIn(" ".join(r["quantity_as_written"].split()).lower().replace("-", ""), r["sentence"].lower().replace("-", ""))   # the duration stands in its sentence
        self.assertTrue((t.loc[t["row_kind"] == "mw", "wait_basis"] == "").all())
        self.assertTrue((wait.loc[wait["wait_counted"] != "yes", "stage_class"] == "none").all())   # what is not a load's wait is classed none
        self.assertTrue(t["source_url"].str.startswith("http").all() and (t["event_date"] != "").all() and (t["entity"] != "").all())
        self.assertEqual(wait.groupby("wait_figure")["wait_figure_holder"].apply(lambda s: (s == "yes").sum()).unique().tolist(), [1])   # one holder a figure
        self.assertEqual(set(t.loc[t["entity_list"] == "the eighty", "entity_group"]) - set(ll.GROUPS), set())
        ercot = wait[(wait["entity"] == "ERCOT") & (wait["quantity_as_written"] == "approximately 220 days")].iloc[0]
        self.assertEqual((ercot["wait_basis"], ercot["wait_counted"], ercot["page"]), ("measured", "yes", "8"))
        self.assertIn("180 days", ercot["sentence"])   # the same sentence says 180 days is the delay ERCOT chose to apply
        sce = wait[(wait["entity"] == "Southern California Edison") & (wait["quantity_as_written"] == "480")].iloc[0]
        self.assertEqual((sce["wait_basis"], sce["load_scope"]), ("measured", ll.ALL_DISTRIBUTION))
        # the rows held since session 141 keep their ids: Oncor's measured average is still the row it was
        oncor = wait[wait["quantity_as_written"] == "825 days"].iloc[0]
        self.assertEqual((oncor["collected_in"], oncor["wait_figure_holder"], oncor["wait_basis"]), ("pass H", "yes", "measured"))

    def test_the_counts_in_the_summary_equal_the_tables(self):
        b = built()
        t = b["out"]
        c = ll.wait_counts(t)
        doc = " ".join(src("docs", "accelerator", "large_load_eighty.md").split())
        eighty = t[t["entity_list"] == "the eighty"]
        mw, wait = int((t["row_kind"] == "mw").sum()), int((t["row_kind"] == "wait").sum())
        not_wait = t[(t["row_kind"] == "wait") & (t["wait_figure_holder"] == "yes") & (t["wait_counted"] != "yes")]["wait_counted"]
        lc = c["large_and_counted_by_basis"]
        for words in (
            f"**{len(t)}** ({mw} megawatt figures, {wait} durations)",
            f"**{eighty['entity_group'].nunique()} of 80**, {len(eighty)} statements; {len(t) - len(eighty)} more from the {t.loc[t['entity_list'] != 'the eighty', 'entity_group'].nunique()} bodies outside",
            f"{sum(1 for r in b['collected'] + b['unproved'] if r['collected_in'].replace('pass ', '') in ll.PASSES_151)} statements came back",
            f"| {int((t['page'] != '').sum())} |",
            f"**{c['figures']} distinct wait figures** in {c['wait_rows']} statements of a duration: {c['held_before']} held before, {c['new']} new",
            f"request {c['by_stage']['1']}, study {c['by_stage']['2']}, financial commitment {c['by_stage']['3']}, signed agreement {c['by_stage']['4']}, construction to energization {c['by_stage']['5']}, none {c['by_stage']['none']}",
            f"{c['by_basis']['measured']} measured, {c['by_basis']['what happened, no duration written']} say what happened and write no duration, {c['by_basis']['general statement']} general statements of experience, {c['by_basis']['expected']} expected",
            f"{c['by_scope']['large loads']} against {c['by_scope']['all distribution']}",
            f"{c['not_a_loads_wait']} are not a load's wait ({int(not_wait.str.contains('lead time').sum())} generation or equipment lead times, {int(not_wait.str.contains('approval').sum())} a regulator's approval time, {int(not_wait.str.contains('rate').sum())} a rate or a difference)",
            f"**{c['large_and_counted']} are a load's wait: {lc['measured']} measured**, {lc['what happened, no duration written']} what happened, {lc['general statement']} general, {lc['expected']} expected",
            f"{c['entities_of_eighty_with_a_figure']} of the eighty entities state at least one figure",
            f"**Measured, all distribution projects ({c['measured_all_distribution']}):**",
            f"{int(t['source_flag'].str.contains('e-mail').sum())} statements rest on such addresses",
            f"{int(((t['row_kind'] == 'mw') & (t['stage_class'] == 'none')).sum())} sit on no stage",
        ):
            self.assertIn(words, doc)
        self.assertEqual(c["by_basis"]["measured"] - c["measured_all_distribution"] - lc["measured"], 1)   # the twelfth: a regulator's approval time
        self.assertEqual(len([g for g in ll.GROUPS if g not in set(eighty["entity_group"])]), 10)
        for fig in ("825 days", "687 days", "approximately 220 days", "480", "235", "243", "427", "129", "950 calendar days", "1,285 calendar days", "492 days", "approximately a year"):
            self.assertTrue(((t["row_kind"] == "wait") & (t["quantity_as_written"] == fig) & (t["wait_basis"] == "measured")).any(), fig)   # every measured figure the page quotes is a row
        v, f = b["vocab"], ll.funnels(b["vocab"])
        verdicts = [x["verdict"] for x in f.values()]
        self.assertIn(f"{len(v)} stage words of {len({x['entity_group'] for x in v if x['entity_group'] in ll.GROUPS})} of the eighty", doc)
        self.assertIn(f"{verdicts.count('placed')} placed whole, {verdicts.count('placed in part')} in part**, {verdicts.count('one stage only')} with one stage only, {verdicts.count('not placed')} not at all", doc)
        self.assertEqual(sorted(g for g, x in f.items() if x["against_order"]), ["Avista", "El Paso Electric", "Grant County Public Utility District"])


class Held(unittest.TestCase):
    def test_the_table_is_internal_and_nothing_of_it_is_published(self):
        text = src("warehouse", "connectors", "large_load_statements.py")
        self.assertIn("License: internal", text)
        for words in ("urlopen", "requests.get", "import requests", "anthropic", "httpx"):
            self.assertNotIn(words, text.lower())   # integration makes no request and no model call
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("- large_load_statements", live.split("catalogue_hold:", 1)[1])
        self.assertNotIn("large_load_statements", live.split("catalogue_hold:", 1)[0])
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "data", "large_load_statements.json")))
        self.assertNotIn("large_load", src("site", "lib", "release.ts"))

    def test_no_address_of_a_person_and_no_long_dash_in_what_this_session_wrote(self):
        for parts in (("docs", "accelerator", "large_load_eighty.md"), ("tests", "test_session151.py"), ("warehouse", "connectors", "large_load_statements.py"),
                      ("docs", "accelerator", "large_load_forty.md")):
            text = src(*parts)
            self.assertIsNone(ADDRESS.search(text), parts)
            self.assertNotIn(chr(0x2014), text, parts)

    def test_the_summary_is_one_page_and_the_forty_page_points_to_it(self):
        doc = src("docs", "accelerator", "large_load_eighty.md")
        self.assertLessEqual(len(doc.splitlines()), 90)
        for words in ("no number without its sentence", "nothing summed across entities", "not a person's review", "Estimates from the rates measured here, not measurements",
                      "approximately 220 days", "825 days", "For the owner to rule"):
            self.assertIn(words, " ".join(doc.split()))
        forty = src("docs", "accelerator", "large_load_forty.md")
        self.assertIn("large_load_eighty.md", "\n".join(forty.splitlines()[:4]))
        self.assertIn("434", forty)   # extended, not overwritten


if __name__ == "__main__":
    unittest.main()
