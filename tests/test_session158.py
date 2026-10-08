"""Session 158: the owner's rulings of 8 October 2026 on the Thesis Builder's rule (warehouse/thesis).

    "for the Thesis Builder, a company name made of the niche's own words counts only when matched as a proper noun
    (capitalized, or with its domain, or in a list of companies), near-duplicate sentences count once, and data
    vendors' public pages are read but labeled as vendor pages in the report; Crunchbase answers are not kept until I
    rule on its terms."

On saved real evidence: tests/fixtures/session158/name_rule.json (the company "Geothermal Technologies
(geothermal.tech)" with the lines of the pages of 7 October 2026 that hold its name's words: the two sentences that
put it on the landscape in session 147's third run are there) and tests/fixtures/session147/pages.json (Quaise
Energy's one remark printed on two pages). A sentence written for a test says so. No network, no model call, no
database: a machine without the warehouse's tables runs every test here (the fixtures are in git).
"""
import copy
import gzip
import importlib.util
import json
import os
import random
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_LEDGER_BEFORE = []


def setUpModule():
    """The ledger is off while this module's tests run and is put back after them (never set at import)."""
    _LEDGER_BEFORE.append(os.environ.get("ERW_LEDGER"))
    os.environ["ERW_LEDGER"] = "0"


def tearDownModule():
    old = _LEDGER_BEFORE.pop()
    if old is None:
        os.environ.pop("ERW_LEDGER", None)
    else:
        os.environ["ERW_LEDGER"] = old


def load(name, *parts):
    """By path, under a name of its own: the suite already holds other modules named run, build and store."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


R = load("erw_thesis_run", "warehouse", "thesis", "run.py")
tie, tb, pg, es, pv = R.tie, R.tb, R.pg, R.es, R.pv
NAME = json.load(open(os.path.join(ROOT, "tests", "fixtures", "session158", "name_rule.json"), encoding="utf-8"))
PAIR = json.load(open(os.path.join(ROOT, "tests", "fixtures", "session147", "pages.json"), encoding="utf-8"))
OLD = json.load(open(os.path.join(ROOT, "tests", "fixtures", "session142", "evidence.json"), encoding="utf-8"))
NICHE, TRENDS = NAME["store"]["niche"], NAME["trends"]
UA = "ERW research project, github.com/SamuelEnrique/erw"
COMPANY = "Geothermal Technologies (geothermal.tech)"
FORMS = [["Geothermal", "Technologies"]]
DOMAINS = ["geothermal.tech"]
CTVC = "Government: The DOE Geothermal Technologies Office has been the major funder of geothermal innovation"
HTX = "Department of Energy to advance geothermal technologies and field tests."
OWN_SITE = "Geothermal Technologies is developing the technology to provide clean, economically competitive energy."
VENDORS = {"cbinsights.com": "CB Insights", "dealroom.co": "Dealroom", "sacra.com": "Sacra"}


def judged(fix=NAME, **k):
    return tie.judge(copy.deepcopy(fix["store"]), fix["warehouse"], fix["store"]["niche"], fix["trends"], **k)


def by_name(rows):
    return {c["name"]: c for c in rows}


def store_of(rows, pages, sources=None):
    """A small store written for a test: rows [(name, website, cited addresses)], pages {address: text}."""
    s = tie.empty_store(NICHE, "startups", "United States")
    s["runs"] = [{"run_id": "t1", "date": "2026-10-08", "seq": 1}]
    for name, site, urls in rows:
        s["rows"].append({"key": tie.name_key(name), "run_id": "t1", "seq": 1, "row": {
            "name": name, "website": site, "kind": "private company", "country": "United States", "location": "Reno, Nevada", "fits_stage": "yes",
            "description": "", "founders": "", "stage": "", "raised": "", "signal": "", "tam": "", "found_by": ["Q1"], "latest_source_year": "2026",
            "stage_primary": False, "raised_primary": False, "trends": [], "source_urls": list(urls)}})
    for url, text in pages.items():
        s["pages"][url] = {"address": url, "state": "fetched", "status": 200, "truncated": False, "text": text, "fetched": "2026-10-08", "reason": ""}
    for url, title in (sources or {}).items():
        s["sources"][url] = {"title": title, "cited": [], "page_age": "", "fetched": "2026-10-08", "sha": tie.sha(title), "first_run": "t1", "last_run": "t1", "history": []}
    return s


def judge_store(s, **k):
    return by_name(tie.judge(s, {"energy_companies": [], "energy_deals": []}, NICHE, TRENDS, **k))


class MadeOfTheNichesOwnWords(unittest.TestCase):
    """How "made of the niche's own words" is decided: the niche's name words and its trends' terms, as tie.py computes them."""

    def test_the_niches_own_words_are_its_name_words_and_its_trends_terms(self):
        own = tie.niche_own(NICHE, TRENDS)
        self.assertEqual({"geothermal", "mapping", "sensing"}, {tie.fold(w) for w in tie.words(tie.head_of(NICHE)) if len(w) >= 4 and tie.fold(w) not in tie.STOP})
        terms = {t for tr in TRENDS for t in tie.trend_terms(NICHE, tr)[0]}
        self.assertEqual(own, {"geothermal", "mapping", "sensing"} | terms)
        for w in ("resource", "doe", "fiber", "exploration", "survey"):
            self.assertIn(w, own, w)
        self.assertNotIn("technologie", own)                 # a generic word, never a word of the niche

    def test_which_names_are_made_of_them(self):
        own = tie.niche_own(NICHE, TRENDS)
        for name, made in (("Geothermal Technologies (geothermal.tech)", True), ("Geothermal Technologies, Inc.", True), ("Geothermal Resources", True),
                           ("Geothermal Exploration Systems", True), ("Fiber Sensing Technologies", True),
                           ("Geothermal Radar", False), ("Quaise Energy", False), ("XGS Energy", False), ("Zanskar Geothermal & Minerals", False),
                           ("Thermofilic, LLC", False), ("Geothermal Strategy Partners", False), ("Terra AI", False),
                           ("Energy Technologies", False)):          # generic words only: no word of the niche in it, so matched as before
            self.assertEqual(tie.made_of_niche(tie.name_key(name), own), made, name)

    def test_of_every_company_of_the_saved_fixtures_only_one_name_is(self):
        own = tie.niche_own(NICHE, TRENDS)
        made = sorted({x["row"]["name"] for fix in (NAME, PAIR, OLD) for x in fix["store"]["rows"] if tie.made_of_niche(x["key"], own)})
        self.assertEqual(made, [COMPANY])

    def test_the_name_as_its_rows_write_it(self):
        self.assertEqual(tie.written_names(["Geothermal Technologies (geothermal.tech)", "Geothermal Technologies, Inc.", "Geothermal Technologies"]), FORMS)
        self.assertEqual(tie.written_names(["Paulsson, Inc.", "TerraAI (Terra AI)"]), [["Paulsson"], ["TerraAI"]])
        for name in ("Geothermal Technologies (geothermal.tech)", "Zanskar Geothermal & Minerals", "Phase Advanced Sensor Systems Corp."):
            self.assertEqual(" ".join(w.lower() for w in tie.written_names([name])[0]), tie.name_key(name), name)


class ProperNoun(unittest.TestCase):
    """The three tests, case by case. Each sentence is real (a page of 7 October 2026) unless it says "written for this test"."""

    def how(self, text, **k):
        return tie.proper_noun(text, FORMS, DOMAINS, **k)

    def test_the_two_sentences_of_the_false_match_are_refused(self):
        self.assertEqual(self.how(CTVC + " and is responsible for R&D grants and common resources like FORGE and EGS Collab."), "not a proper noun")
        self.assertEqual(self.how(HTX), "not a proper noun")
        # and the loose matching of session 142, which every other company still has, would take both
        aliases = [("geothermal technologies", "geothermal technologies")]
        self.assertTrue(tie.names_it(CTVC, aliases, ["geothermal", "mapping", "sensing"]))
        self.assertTrue(tie.names_it(HTX, aliases, ["geothermal", "mapping", "sensing"]))

    def test_part_of_a_longer_capitalized_name_is_not_the_company(self):
        for text in ("It provides free access to data generated from projects funded by DOE's Geothermal Technologies Office to facilitate the open transfer of knowledge.",
                     "Funded by the Department of Energy’s Geothermal Technologies Office, the EGS Collab unites researchers from multiple national laboratories.",
                     "The award came from the Geothermal Technologies Program in 2019.",                      # written for this test
                     "Utah Geothermal Technologies drilled a second well."):                                  # written for this test: a longer name before it
            self.assertEqual(self.how(text), "not a proper noun", text)

    def test_running_text_in_lower_case_is_not_the_company(self):
        for text in ("Eavor is developing next-generation geothermal technologies.", "Next-generation geothermal technologies",
                     "NLR scientists explore geothermal technologies for creating fresh water from otherwise",
                     "Geothermal technologies are improving quickly."):                                         # written for this test: only the sentence's own capital
            self.assertEqual(self.how(text), "not a proper noun", text)

    def test_the_company_is_named_by_its_capitals(self):
        for text in (OWN_SITE,
                     "Geothermal Technologies’ GenaSysTM Geothermal Energy Harvesting System revolutionizes how we harness renewable energy.",
                     "Baltimore, MD – Geothermal Technologies, Inc. (GTI), a leading innovator in sustainable energy solutions, is proud to announce a paper.",
                     "The DOE grant went to Geothermal Technologies for field tests of its resource model.",          # written for this test
                     "Geothermal Technologies CEO Jane Roe said the grant pays for field tests.",                     # written for this test: a role after the name
                     "A team from Geothermal Technologies Inc drilled the test well."):                               # written for this test: a legal form after it
            self.assertEqual(self.how(text), "capital", text)

    def test_a_dash_parts_two_names_and_a_joining_hyphen_does_not(self):
        # the first is a real search result's title (zoominfo.com, 7 October 2026); the others are written for this test
        self.assertEqual(self.how("Geothermal Technologies - Overview, News & Similar companies"), "capital")
        self.assertEqual(self.how("The Nevada-Geothermal Technologies venture drilled a well."), "not a proper noun")
        self.assertEqual(self.how("A partner of Geothermal Technologies-Utah drilled a well."), "not a proper noun")
        self.assertEqual(self.how("Utah – Geothermal Technologies drilled a well."), "capital")

    def test_a_heading_with_every_word_capitalized_shows_no_proper_noun(self):
        heading = "Geothermal Technologies, Inc. to Present Paper and Lead a Panel at the Geothermal Rising Annual Meeting in Reno"
        self.assertEqual(self.how(heading), "not a proper noun")
        self.assertEqual(self.how("DOE Awards Grants for Geothermal Technologies and Field Tests"), "not a proper noun")       # written for this test
        self.assertEqual(self.how(heading, address="https://geothermal.tech/"), "domain")                                      # on the company's own page it is the company

    def test_a_name_of_one_word_opening_a_sentence_shows_nothing_by_its_capital(self):
        one = [["Exploration"]]
        self.assertEqual(tie.proper_noun("Exploration is costly in blind systems.", one), "not a proper noun")                 # written for this test
        self.assertEqual(tie.proper_noun("The grant went to Exploration for its geothermal survey.", one), "capital")          # written for this test

    def test_the_company_is_named_with_its_domain(self):
        self.assertEqual(self.how("Funding went to geothermal technologies (see geothermal.tech) for field tests."), "domain")           # written for this test: the sentence holds it
        self.assertEqual(self.how("We build geothermal technologies for deep wells.", address="https://www.geothermal.tech/about/"), "domain")   # written for this test: its own page
        self.assertEqual(self.how("We build geothermal technologies for deep wells.", address="https://news.geothermal.tech/a"), "domain")
        self.assertEqual(self.how("It works on geothermal technologies.", address="https://example.org/a", page_text="Profile: Geothermal Tech\nWebsite: geothermal.tech\n"), "domain")
        for address, text in (("https://notgeothermal.tech/", ""), ("https://example.org/", "see geothermal.technology for more"), ("https://example.org/", "see mygeothermal.tech")):
            self.assertEqual(self.how("It works on geothermal technologies.", address=address, page_text=text), "not a proper noun", (address, text))

    def test_the_company_is_named_in_a_list_of_companies(self):
        # every sentence here is written for this test
        self.assertEqual(self.how("Fervo Energy, Geothermal Technologies, Quaise Energy, Zanskar"), "list")                     # every word capitalized: only the list shows it
        self.assertEqual(self.how("Selected Projects: Fervo Energy, Sage Geosystems, Geothermal Technologies"), "list")
        self.assertEqual(self.how("Geothermal Technologies | Fervo Energy | Quaise Energy"), "list")
        self.assertEqual(self.how("Fervo Energy, Geothermal Technologies"), "not a proper noun")                                # two names are not a list
        self.assertEqual(self.how("Fervo Energy, Geothermal Technologies Office, Quaise Energy, Sandia"), "not a proper noun")  # the item is a longer name
        self.assertEqual(self.how("Fervo Energy, geothermal technologies, Quaise Energy"), "not a proper noun")                 # no capitals, no list
        self.assertEqual(self.how("Awards went to Fervo Energy, Geothermal Technologies, and Quaise Energy for field tests."), "capital")   # in running text the capitals already show it
        self.assertEqual(tie.LIST_MIN, 3)

    def test_a_text_without_the_names_words_names_nobody(self):
        self.assertEqual(self.how("Mazama says that will allow each well to produce more power."), "")
        self.assertEqual(self.how("geothermal energy technologies"), "")


class FalseMatch(unittest.TestCase):
    """Session 147's false match on the saved real pages: gone, and the real company of that name still matches."""

    def test_before_the_ruling_the_two_sentences_tied_it(self):
        c = by_name(judged(proper=False))[COMPANY]
        self.assertEqual((c["trends"], c["tie"]), ([3], 3))
        lines = c["ties"][3]["lines"]
        self.assertEqual([(x["points"], tie.domain(x["address"])) for x in lines], [(2, "ctvc.co"), (1, "energycapitalhtx.com")])
        self.assertTrue(lines[0]["text"].startswith(CTVC))
        self.assertEqual(lines[1]["text"], HTX)
        self.assertIsNone(c["name_rule"])

    def test_the_false_match_is_gone(self):
        c = by_name(judged())[COMPANY]
        self.assertEqual((c["trends"], c["tie"], c["tier"], c["reason"]), ([], 0, "", None))
        self.assertTrue(all(not t["lines"] for t in c["ties"].values()))
        texts = [e["text"] for e in c["evidence"]]
        self.assertNotIn(HTX, texts)
        self.assertFalse(any(t.startswith(CTVC) for t in texts))
        self.assertFalse(any("Technologies Office" in t for t in texts))

    def test_what_still_names_it_is_its_own_site_and_each_line_says_by_which_test(self):
        c = by_name(judged())[COMPANY]
        self.assertTrue(c["evidence"])
        for e in c["evidence"]:
            self.assertEqual(tie.domain(e["address"]), "geothermal.tech", e)
            self.assertIn(e["named"], ("capital", "domain"), e)
        self.assertIn(OWN_SITE, [e["text"] for e in c["evidence"] if e["named"] == "capital"])
        rule = c["name_rule"]
        self.assertEqual((rule["names"], rule["written"], rule["domains"]), (["geothermal technologies"], ["Geothermal Technologies"], ["geothermal.tech"]))
        self.assertGreater(rule["counted"]["capital"], 0)
        self.assertGreater(rule["counted"]["domain"], 0)
        self.assertGreaterEqual(rule["not_counted"], 10)             # the sentences about geothermal technologies in general
        self.assertEqual(len(c["evidence"]) < len(by_name(judged(proper=False))[COMPANY]["evidence"]), True)

    def test_the_real_company_would_still_be_tied_as_a_proper_noun_with_its_domain_and_in_a_list(self):
        # three pages written for this test, each a sentence that holds terms of trend 3 (grant, resource, DOE, field, test)
        cases = {"capital": ("https://example.org/news", "The DOE grant for resource characterization went to Geothermal Technologies after its field tests."),
                 "domain": ("https://example.org/profile", "Developer of geothermal technologies (geothermal.tech) that won a DOE grant for resource field tests."),
                 "list": ("https://example.org/awards", "DOE Resource Grant Field Test Awardees: Fervo Energy, Geothermal Technologies, Quaise Energy")}
        for how, (url, text) in cases.items():
            c = judge_store(store_of([(COMPANY, "geothermal.tech", [url])], {url: text}))[COMPANY]
            self.assertEqual(c["trends"], [3], how)
            self.assertEqual([e["named"] for e in c["evidence"]], [how], how)
            self.assertEqual(c["ties"][3]["lines"][0]["points"], 2, how)          # one web sentence (1), strong by three terms (+1): tied at 2, as before
        # and the same three pages with the office's name instead of the company's tie nothing
        c = judge_store(store_of([(COMPANY, "geothermal.tech", ["https://example.org/news"])],
                                 {"https://example.org/news": "The DOE Geothermal Technologies Office gave a grant for resource characterization field tests."}))[COMPANY]
        self.assertEqual((c["trends"], c["evidence"]), ([], []))

    def test_a_fetched_title_and_a_deal_row_follow_the_same_rule(self):
        s = store_of([(COMPANY, "geothermal.tech", [])], {}, sources={
            "https://example.org/a": "DOE grant funds geothermal technologies and resource field tests",              # written for this test: running text
            "https://example.org/b": "Geothermal Technologies wins a DOE grant for resource field tests"})            # written for this test: the company
        c = by_name(tie.judge(s, {"energy_companies": [], "energy_deals": [
            {"event_id": "d1", "parties": "DOE Geothermal Technologies Office; Fervo Energy", "asset": "field test grant", "technology": "resource characterization"},
            {"event_id": "d2", "parties": "Geothermal Technologies; DOE", "asset": "field test grant", "technology": "resource characterization"}]}, NICHE, TRENDS))[COMPANY]
        self.assertEqual(sorted((e["tier"], e["address"]) for e in c["evidence"]), [("fetched", "https://example.org/b"), ("warehouse", "erw:energy_deals/d2")])


class EveryOtherCompany(unittest.TestCase):
    """Every other company's matching is unchanged: on the saved fixtures of sessions 142 and 147 no name is made of the
    niche's own words, and the rule reads them as it did."""

    def test_the_name_rule_changes_nothing_on_the_fixtures_of_sessions_142_and_147(self):
        for fix, read in ((PAIR, "pages"), (OLD, "pages"), (OLD, "quotes")):
            a = tie.judge(copy.deepcopy(fix["store"]), fix["warehouse"], fix["store"]["niche"], fix["trends"], read=read, remarks=False)
            b = tie.judge(copy.deepcopy(fix["store"]), fix["warehouse"], fix["store"]["niche"], fix["trends"], read=read, remarks=False, proper=False)
            self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
            self.assertTrue(all(c["name_rule"] is None for c in a))
            self.assertTrue(all("named" not in e for c in a for e in c["evidence"]))

    def test_with_both_rulings_off_the_fixture_reads_as_session_147_recorded(self):
        got = [c["name"] for c in judged(PAIR, proper=False, remarks=False) if c["trends"]]
        self.assertEqual(got, ["Zanskar Geothermal & Minerals", "Thermofilic", "Geothermal Radar", "Quaise Energy", "XGS Energy"])

    def test_the_other_four_companies_score_what_they_scored(self):
        new, old = by_name(judged(PAIR)), by_name(judged(PAIR, proper=False, remarks=False))
        for name in ("Zanskar Geothermal & Minerals", "Thermofilic", "Geothermal Radar", "XGS Energy", "Bedrock Energy", "Mazama Energy"):
            self.assertEqual(json.dumps(new[name]["ties"], sort_keys=True), json.dumps(old[name]["ties"], sort_keys=True), name)
            self.assertEqual((new[name]["tie"], new[name]["tier"]), (old[name]["tie"], old[name]["tier"]), name)


class SameRemark(unittest.TestCase):
    """Near-duplicate sentences count once, on the saved real pair: one remark of Quaise Energy's chief executive printed
    on two pages with two attributions."""

    HTX = "https://energycapitalhtx.com/fervo-quaise-xgs-geothermaldoe-funding"
    QUAISE = "https://www.quaise.com/news/quaise-energy-selected-for-up-to-25-million-in-u-s-department-of-energy-support-to-advance-worlds-first-commercial-superhot-geothermal-power-plant"

    def pair(self):
        c = by_name(judged(PAIR, remarks=False))["Quaise Energy"]
        return [x["text"] for x in c["ties"][3]["lines"]]

    def test_the_saved_pair_is_two_different_sentences_and_one_remark(self):
        a, b = self.pair()
        self.assertNotEqual(tie.sha(a), tie.sha(b))
        self.assertIn("said in a release", a)
        self.assertIn("said Carlos Araque, CEO and President of Quaise Energy", b)
        ra, rb = tie.remark(a), tie.remark(b)
        self.assertEqual(ra, rb)                                  # inside the quotation marks the words are the same
        self.assertEqual(tie.remark_share(ra, rb), 1.0)
        self.assertTrue(tie.same_remark(ra, rb))
        self.assertNotIn("araque", ra)                            # who spoke is outside the quotation marks, and left out
        self.assertEqual(ra[:4], ["this", "doe", "support", "is"])
        # the whole sentences, attribution and all, are also over the measure: 0.90 of the longer one's words
        self.assertGreaterEqual(tie.remark_share(tie.words(a), tie.words(b)), tie.NEAR_SAME)

    def test_the_pair_counts_once_and_the_merge_is_on_record(self):
        before, after = by_name(judged(PAIR, remarks=False))["Quaise Energy"], by_name(judged(PAIR))["Quaise Energy"]
        self.assertEqual((before["ties"][3]["score"], before["ties"][3]["tied"], len(before["ties"][3]["lines"])), (2, True, 2))
        self.assertEqual((after["ties"][3]["score"], after["ties"][3]["tied"], len(after["ties"][3]["lines"])), (1, False, 1))
        self.assertEqual(after["trends"], [])
        self.assertEqual(before["near_duplicates"], [])
        self.assertEqual(len(after["near_duplicates"]), 1)
        m = after["near_duplicates"][0]
        self.assertEqual((m["kept"]["address"], m["dropped"]["address"], m["share"], m["trends"]), (self.HTX, self.QUAISE, 1.0, [3]))
        self.assertEqual(after["ties"][3]["lines"][0]["address"], self.HTX)
        self.assertEqual(sum(len(c["near_duplicates"]) for c in judged(PAIR)), 1)          # no other pair of the fixture is one remark

    def test_the_higher_tier_copy_is_kept(self):
        a, b = self.pair()
        s = copy.deepcopy(PAIR["store"])
        # the same remark also as the passage a search result cited (the fetched tier, 2 points), at a third address
        s["sources"]["https://example.org/wire"] = {"title": "", "cited": [b.replace("said Carlos Araque", "said Mr. Carlos Araque")], "page_age": "", "fetched": "2026-10-07",
                                                    "sha": "x", "first_run": "t", "last_run": "t", "history": []}
        c = by_name(tie.judge(s, PAIR["warehouse"], PAIR["store"]["niche"], PAIR["trends"]))["Quaise Energy"]
        lines = c["ties"][3]["lines"]
        self.assertEqual([(x["tier"], x["address"], x["points"]) for x in lines], [("fetched", "https://example.org/wire", 2)])
        self.assertEqual(sorted((m["kept"]["tier"], m["dropped"]["tier"]) for m in c["near_duplicates"]), [("fetched", "web"), ("fetched", "web")])

    def test_two_different_sentences_about_one_thing_are_not_one_remark(self):
        t = by_name(judged(PAIR))["Thermofilic"]["ties"][4]["lines"]                     # two pages describe Thermofilic in their own words
        self.assertEqual(len(t), 2)
        share = tie.remark_share(tie.remark(t[0]["text"]), tie.remark(t[1]["text"]))
        self.assertLess(share, 0.75)
        self.assertFalse(tie.same_remark(tie.remark(t[0]["text"]), tie.remark(t[1]["text"])))

    def test_the_measure_by_hand(self):
        a = "one two three four five six seven eight nine ten".split()
        self.assertTrue(tie.same_remark(a, a[:9] + ["other"]))                            # 9 of 10 shared: 0.90
        self.assertFalse(tie.same_remark(a, a[:8] + ["other", "words"]))                  # 8 of 10
        self.assertFalse(tie.same_remark(a[:7], a[:7]))                                   # under eight words: never merged
        self.assertFalse(tie.same_remark(a, a + a))                                       # a sentence inside a much longer one is not the same remark
        self.assertEqual(tie.remark_share("a a b".split(), "a b b".split()), 2 / 3)       # each word counted as often as both hold it
        self.assertEqual((tie.NEAR_SAME, tie.NEAR_MIN_WORDS), (0.90, 8))

    def test_what_a_remark_is(self):
        said = "“We will drill the confirmation well this year and publish the data,” said Jane Roe, chief executive."        # written for this test
        self.assertEqual(tie.remark(said), "we will drill the confirmation well this year and publish the data".split())
        self.assertEqual(tie.remark("\"Short one,\" she said of the well."), tie.words("\"Short one,\" she said of the well."))       # a quotation under eight words: the whole sentence
        self.assertEqual(tie.remark("No quotation here at all."), ["no", "quotation", "here", "at", "all"])

    def test_the_same_saved_evidence_gives_the_same_result_in_any_order(self):
        want = json.dumps([(c["name"], c["trends"], c["tie"], c["near_duplicates"]) for c in judged(PAIR)], sort_keys=True)
        rng = random.Random(158)
        for _ in range(4):
            s = copy.deepcopy(PAIR["store"])
            rng.shuffle(s["rows"])
            s["pages"] = dict(rng.sample(sorted(s["pages"].items()), len(s["pages"])))
            s["sources"] = dict(rng.sample(sorted(s["sources"].items()), len(s["sources"])))
            got = tie.judge(s, PAIR["warehouse"], PAIR["store"]["niche"], PAIR["trends"])
            self.assertEqual(json.dumps([(c["name"], c["trends"], c["tie"], c["near_duplicates"]) for c in got], sort_keys=True), want)


class NoThresholdChanged(unittest.TestCase):
    def test_the_constants_of_the_scoring(self):
        self.assertEqual(tie.TIERS, {"warehouse": 3, "fetched": 2, "web": 1})
        self.assertEqual(tie.TIER_ORDER, ["warehouse", "fetched", "web"])
        self.assertEqual((tie.STRONG_POINT, tie.STRONG_TERMS, tie.MIN_TERMS, tie.TIE_MIN, tie.MAX_ADDRESSES, tie.PAGE_SENTENCE_MAX), (1, 3, 2, 2, 3, 500))
        self.assertEqual((R.PIPELINE_MIN, R.PIPELINE_MAX, R.RUN_USD, R.DAY_USD), (60, 10, 2.0, 8.0))
        self.assertEqual(R.STAGE_USD, {"research a": 0.45, "structure a": 0.16, "landscape": 0.85, "risks": 0.12, "structure landscape": 0.34, "structure rest": 0.16})

    def test_the_lines_that_score_tie_and_order_are_as_they_were(self):
        code = src("warehouse", "thesis", "tie.py")
        for line in ('if not phrase and len(matched) < MIN_TERMS:',
                     'pts = TIERS[e["tier"]] + (STRONG_POINT if phrase or len(matched) >= STRONG_TERMS else 0)',
                     'if old is None or (-pts, TIER_ORDER.index(e["tier"]), e["sha"]) < (-old["points"], TIER_ORDER.index(old["tier"]), old["sha"]):',
                     'for x in sorted(per_addr.values(), key=lambda x: (-x["points"], TIER_ORDER.index(x["tier"]), x["address"])):',
                     'lines = lines[:MAX_ADDRESSES]',
                     'score = sum(x["points"] for x in lines)',
                     'ties[n] = {"score": score, "tied": score >= TIE_MIN, "lines": lines}',
                     'return (-c["tie"], TIER_ORDER.index(c["tier"]) if c["tier"] else len(TIER_ORDER), c["key"])',
                     'if " " in n or (len(n) >= 4 and in_niche):'):
            self.assertEqual(code.count(line), 1, line)

    def test_the_pulls_ceilings_and_its_one_header(self):
        self.assertEqual(pg.UA, UA)
        self.assertEqual(pg.HEADERS, {"User-Agent": UA})
        self.assertEqual((pg.MAX_ADDRESSES_RUN, pg.MAX_ADDRESSES_SESSION, pg.MAX_REQUESTS_RUN, pg.MAX_REQUESTS_SESSION, pg.MAX_BYTES, pg.TIMEOUT, pg.HOST_GAP,
                          pg.MAX_REDIRECTS, pg.MAX_SECONDS_RUN), (150, 450, 450, 1350, 2_000_000, 20, 1.0, 3, 600))
        self.assertEqual(pg.LICENSED_HOSTS, ("pitchbook.com", "crunchbase.com", "harmonic.ai"))
        self.assertEqual(pg.NEVER_HOSTS, ("misoenergy.org",))


class Web:
    """A stand-in for the one network call: answers from a table, and records every request with its headers."""

    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def __call__(self, url, headers, timeout, max_bytes):
        self.asked.append((url, dict(headers)))
        if url.endswith("/robots.txt"):
            return 404, {"content-type": "text/plain"}, b"", False
        body = self.pages.get(url)
        if body is None:
            return 404, {"content-type": "text/html"}, b"not here", False
        return 200, {"content-type": "text/html; charset=utf-8"}, body.encode("utf-8"), False


class Saved:
    """A researcher holding sources, and no client."""

    def __init__(self):
        self.sources, self.erw = {}, []

    source = tb.Researcher.source
    texts_of = tb.Researcher.texts_of


class VendorPages(unittest.TestCase):
    """Data vendors' public pages are read, and labeled. The sentences here are written for these tests."""

    CB = "https://www.cbinsights.com/company/heatwell-labs"
    NEWS = "https://example.org/heatwell"
    TEXT = "Heatwell Labs won a DOE grant for resource characterization field tests in Nevada."

    def test_the_list_is_one_file_with_a_reason_for_every_row(self):
        import csv
        with open(os.path.join(ROOT, "warehouse", "thesis", "vendor_pages.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        self.assertEqual([r["domain"] for r in rows][:3], ["cbinsights.com", "dealroom.co", "sacra.com"])           # the three session 147 met holding text
        for r in rows:
            self.assertTrue(r["vendor"] and len(r["reason"]) > 20 and r["first_met"] and r["met"], r)
            self.assertFalse(any(r["domain"] == h or r["domain"].endswith("." + h) for h in pg.LICENSED_HOSTS + pg.NEVER_HOSTS), r)
        self.assertEqual(pg.vendor_pages(), {r["domain"]: r["vendor"] for r in rows})
        self.assertEqual(sum(1 for path, _, files in os.walk(os.path.join(ROOT, "warehouse", "thesis")) for n in files if n.startswith("vendor_") and "__pycache__" not in path), 1)

    def test_a_host_is_a_vendors_when_it_is_the_domain_or_under_it(self):
        for url, v in (("https://www.cbinsights.com/company/x", "CB Insights"), ("https://app.dealroom.co/companies/x", "Dealroom"), ("https://sacra.com/c/x/", "Sacra"),
                       ("https://notcbinsights.com/", ""), ("https://example.org/cbinsights.com", ""), ("https://www.ctvc.co/a", "")):
            self.assertEqual(pg.vendor_of(url), v, url)
            self.assertEqual(tie.vendor_of(url, pg.vendor_pages()), v, url)

    def test_a_vendors_page_is_fetched_as_before_and_its_record_carries_the_label(self):
        web = Web({self.CB: f"<html><body><p>{self.TEXT}</p></body></html>", self.NEWS: f"<html><body><p>{self.TEXT}</p></body></html>"})
        store, t = tie.empty_store(), {"t": 0.0}
        tally = pg.fetch_run(store, [self.CB, self.NEWS, "https://www.crunchbase.com/organization/heatwell", "https://pitchbook.com/profiles/company/1", "https://harmonic.ai/x"],
                             "20261008T000000Z-test01", "2026-10-08", get=web, sleep=lambda s: t.__setitem__("t", t["t"] + s), clock=lambda: t["t"], paused={"misoenergy.org"})
        self.assertEqual((store["pages"][self.CB]["state"], store["pages"][self.CB]["vendor"], store["pages"][self.CB]["text"]), ("fetched", "CB Insights", self.TEXT))
        self.assertNotIn("vendor", store["pages"][self.NEWS])
        self.assertEqual((tally["vendor_pages"], tally["vendor_pages_held"]), ({self.CB: "CB Insights"}, 1))
        # the sites refused before any request stay refused, and every request carries the one header
        asked = [u for u, _ in web.asked]
        for host in ("crunchbase.com", "pitchbook.com", "harmonic.ai", "misoenergy.org"):
            self.assertFalse(any(host in u for u in asked), host)
        self.assertEqual(tally["licensed"], 3)
        for u in ("https://www.crunchbase.com/organization/heatwell", "https://pitchbook.com/profiles/company/1", "https://harmonic.ai/x"):
            self.assertEqual(store["pages"][u]["reason"], "not fetched: licensed source needed")
        self.assertTrue(all(h == {"User-Agent": UA} for _, h in web.asked))
        self.assertEqual(len(asked), 4)                              # two pages and the robots.txt of their two hosts

    def test_every_sentence_from_a_vendors_page_is_labeled_and_scores_what_any_sentence_scores(self):
        s = store_of([("Heatwell Labs", "heatwell.example", [self.CB, self.NEWS])], {self.CB: self.TEXT, self.NEWS: "Heatwell Labs maps blind systems. " + self.TEXT})
        c = judge_store(s, vendors=VENDORS)["Heatwell Labs"]
        ev = {(e["address"], e["text"]): e.get("vendor") for e in c["evidence"]}
        self.assertEqual(ev[(self.CB, self.TEXT)], "CB Insights")
        self.assertTrue(all(v is None for (a, _), v in ev.items() if a == self.NEWS))
        plain = judge_store(copy.deepcopy(s))["Heatwell Labs"]                             # without the list: the same points, no label
        self.assertEqual((c["trends"], c["tie"]), (plain["trends"], plain["tie"]))
        self.assertTrue(all("vendor" not in e for e in plain["evidence"]))

    def test_a_search_result_of_a_licensed_database_is_labeled_too_and_its_site_is_still_never_asked(self):
        """The search tool returns titles of crunchbase.com and pitchbook.com pages; the rule has read them in its
        fetched tier since session 142. They carry the label; no page of theirs is fetched for it."""
        names = pg.labeled_vendors()
        self.assertEqual({k: names[k] for k in pg.LICENSED_HOSTS}, {"pitchbook.com": "PitchBook", "crunchbase.com": "Crunchbase", "harmonic.ai": "Harmonic"})
        self.assertEqual({k: v for k, v in names.items() if k not in pg.LICENSED_HOSTS}, pg.vendor_pages())
        self.assertEqual(set(pg.vendor_pages()) & set(pg.LICENSED_HOSTS), set())
        url = "https://www.crunchbase.com/organization/heatwell-labs"
        s = store_of([("Heatwell Labs", "heatwell.example", [])], {}, sources={url: "Heatwell Labs - a DOE grant for resource field tests"})       # written for this test
        c = judge_store(s, vendors=names)["Heatwell Labs"]
        self.assertEqual([(e["tier"], e["address"], e["vendor"]) for e in c["evidence"]], [("fetched", url, "Crunchbase")])
        self.assertEqual(c["reason"]["vendor"], "Crunchbase")
        self.assertEqual(pg.never(url), "not fetched: licensed source needed")
        self.assertIn("pg.labeled_vendors()", src("warehouse", "thesis", "run.py"))

    def run_once(self, pages, cited):
        r = Saved()
        for u in cited:
            r.source(u, "A profile page")
        ids = {s["url"]: s["id"] for s in r.sources.values()}
        org = {"name": "Heatwell Labs", "website": "heatwell.example", "description": "Maps heat.", "kind": "private company", "country": "United States", "location": "Reno, Nevada",
               "founders": "", "stage": "", "raised": "", "signal": "", "fits_stage": "yes", "trends": [], "trend_reason": "", "tam": "", "sources": [ids[u] for u in cited],
               "found_by": ["Q1"], "independent_sources": 1, "latest_source_year": "2026", "stage_primary": False, "raised_primary": False, "evidence": []}
        land = {"fact": "", "fact_sources": [], "organisations": [org]}
        a = {"scope": {"definition": "", "definition_sources": [], "value_chain": [], "excluded": [], "definitions": []},
             "trends": [dict(t, fact="", table={"columns": [], "rows": []}, chart={"kind": "none", "title": "", "category_column": 0, "value_columns": []}, unit="", sources=[]) for t in TRENDS]}
        store = store_of([], pages)
        log, real = [], R.warehouse_rows
        R.warehouse_rows = lambda: {"energy_companies": [], "energy_deals": []}
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                path = os.path.join(tmp, "s.json")
                tie.save_store(store, path)
                rows, ctx = R.tied_rows(r, "20261008T000000Z-test01", NICHE, "startups", "United States", TRENDS, land, path, log.append)
                report, placed = R.build_report(NICHE, "startups", "United States", r, a, dict(land, organisations=rows), {}, None, R.query_plan(NICHE, "United States", TRENDS), log.append)
                tied = R.tie_done(ctx, placed, log.append)
        finally:
            R.warehouse_rows = real
        return report, tied, log

    def test_the_report_shows_vendor_page_beside_a_reason_that_comes_from_one(self):
        report, tied, log = self.run_once({self.CB: self.TEXT}, [self.CB])
        row = report["landscape"]["companies"][0]
        self.assertEqual(row["name"], "Heatwell Labs")
        self.assertIn("(cbinsights.com)", row["reason"])
        self.assertEqual(row["reason_vendor"], {"mark": "vendor page", "note": "This sentence is from a public page of a data vendor (CB Insights), not from the company or the press."})
        v = tied["vendor_pages"]
        self.assertEqual((list(v["pages"]), v["pages"][self.CB]["vendor"], v["sentences_labeled"], v["reasons_shown"]), ([self.CB], "CB Insights", 1, ["Heatwell Labs"]))
        self.assertTrue(any("pages of data vendors" in ln or "data vendors' pages" in ln for ln in log))

    def test_a_reason_from_any_other_page_carries_no_mark(self):
        report, tied, _ = self.run_once({self.NEWS: self.TEXT}, [self.NEWS])
        row = report["landscape"]["companies"][0]
        self.assertNotIn("reason_vendor", row)
        self.assertEqual(tied["vendor_pages"]["reasons_shown"], [])
        self.assertEqual(tied["vendor_pages"]["pages"], {})

    def test_the_mark_is_short_and_says_nothing_of_the_method(self):
        self.assertEqual(R.VENDOR_MARK, "vendor page")
        for w in ("point", "tier", "threshold", "score", "rule", "robots", "TIE_MIN"):
            self.assertNotIn(w, R.VENDOR_NOTE, w)
        page = src("site", "components", "thesis", "Report.tsx")
        self.assertIn("reason_vendor", page)
        self.assertIn('data-vendor-page="1"', page)
        self.assertIn("reason_vendor?: { mark: string; note: string }", src("site", "lib", "thesis", "types.ts"))


class RunsRecord(unittest.TestCase):
    """What a run's record says of the rulings (state["tie"]): the names matched as proper nouns, the merged pairs."""

    def test_the_record_of_a_run_on_the_saved_pair(self):
        r = Saved()
        for url, s in PAIR["store"]["sources"].items():
            r.source(url, s["title"], s.get("page_age", ""))
        ids = {s["url"]: s["id"] for s in r.sources.values()}
        orgs = []
        for x in PAIR["store"]["rows"]:
            o = dict(x["row"], independent_sources=1, tam="")
            o["sources"] = [ids[u] for u in x["row"]["source_urls"] if u in ids]
            o["evidence"] = []
            orgs.append(o)
        land = {"fact": "", "fact_sources": [], "organisations": orgs}
        store = copy.deepcopy(PAIR["store"])
        store["rows"], store["runs"], store["last"] = [], [], None
        log, real = [], R.warehouse_rows
        R.warehouse_rows = lambda: PAIR["warehouse"]
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                path = os.path.join(tmp, "s.json")
                tie.save_store(store, path)
                rows, ctx = R.tied_rows(r, "20261008T000000Z-test02", PAIR["store"]["niche"], PAIR["store"]["stage"], PAIR["store"]["geography"], PAIR["trends"], land, path, log.append)
                tied = R.tie_done(ctx, [dict(o, reached="found", score=0) for o in rows], log.append)
        finally:
            R.warehouse_rows = real
        self.assertEqual(tied["near_duplicates"]["pairs"], 1)
        self.assertEqual((tied["near_duplicates"]["list"][0]["name"], tied["near_duplicates"]["same_share"], tied["near_duplicates"]["least_words"]), ("Quaise Energy", 0.90, 8))
        self.assertEqual(tied["name_rule"], {"companies": [], "sentences_not_counted": 0})
        self.assertTrue(any("remarks printed twice and counted once: 1 pairs" in ln for ln in log))
        trace = {c["name"]: c for c in tied["trace"]}
        self.assertEqual(len(trace["Quaise Energy"]["near_duplicates"]), 1)
        self.assertIsNone(trace["Quaise Energy"]["name_rule"])


class Crunchbase(unittest.TestCase):
    """Crunchbase answers are not kept until its terms are ruled on: refused with the plain words, nothing stored."""

    WORDS = "Crunchbase answers are not kept until its terms are ruled on"

    def test_the_servers_list_says_which_provider_is_not_kept_and_in_which_words(self):
        self.assertEqual(pv.NOT_KEPT, {"crunchbase": self.WORDS})
        self.assertEqual([(p.id, pv.kept(p.id)) for p in pv.PROVIDERS], [("pitchbook", True), ("harmonic", True), ("crunchbase", False)])
        self.assertEqual([(p.id, p.label, p.format) for p in pv.PROVIDERS],
                         [("pitchbook", "PitchBook", "erw-pitchbook-1"), ("harmonic", "Harmonic", "erw-harmonic-1"), ("crunchbase", "Crunchbase", "erw-crunchbase-1")])

    def test_no_stamp_and_so_no_stored_fact_can_be_made_of_a_crunchbase_answer(self):
        pasted = '{"format": "erw-crunchbase-1", "companies": [{"name": "Made-up Co", "found": true}]}'          # written for this test
        with self.assertRaises(pv.NotKept) as cm:
            pv.stamp("crunchbase", pasted, "2026-10-08T12:00:00Z")
        self.assertEqual(str(cm.exception), self.WORDS)
        self.assertNotIn("Made-up", str(cm.exception))                                 # nothing of the pasted text is in the refusal
        for other in ("pitchbook", "harmonic"):
            self.assertEqual(pv.stamp(other, pasted, "2026-10-08T12:00:00Z")["provider"], other)

    def test_the_site_says_the_same_and_refuses_before_the_pasted_text_is_read_hashed_or_stored(self):
        lib = src("site", "lib", "thesis", "providers.ts")
        self.assertIn('NOT_KEPT: Partial<Record<ProviderId, string>> = { crunchbase: "' + self.WORDS + '" }', lib)
        route = src("site", "app", "api", "thesis", "provider", "route.ts")
        body = route.split("export async function POST", 1)[1]
        refusal = body.index("const held = notKept(body.provider);")
        self.assertIn("if (held) return no(held, 400);", body)
        for later in ("typeof body.pasted", "checkPaste(", "createHash(", "getRun(", "acceptProvider("):
            self.assertEqual(body.count(later), 1, later)
            self.assertLess(refusal, body.index(later), later)
        check = lib.split("export function checkPaste", 1)[1].split("\n}\n", 1)[0]
        self.assertLess(check.index("notKept(chosen)"), check.index("extractJson("))      # the function every caller uses refuses too, before the text is parsed

    def test_the_choice_on_the_page_shows_it_as_not_yet_available_with_those_words_on_hover(self):
        panel = src("site", "components", "thesis", "PitchbookPanel.tsx")
        self.assertIn('NOT_KEPT_MARK = "not yet available"', src("site", "lib", "thesis", "providers.ts"))
        self.assertIn("data-thesis-provider-unavailable={id}", panel)
        self.assertIn("title={off}", panel)
        self.assertIn("disabled={done || busy || !!off}", panel)
        self.assertIn("!have(id) && !notKept(id)", panel)                                 # never the chosen provider, so its request text is never in the box

    def test_pitchbook_and_harmonic_are_as_they_were_and_the_stored_runs_are_not_touched(self):
        self.assertEqual(R.FORMAT, "erw-pitchbook-1")
        self.assertIs(pv.DEFAULT, pv.PITCHBOOK)
        self.assertIs(pv.provider_of({"format": "erw-pitchbook-1", "run_id": "any run written before session 150"}), pv.PITCHBOOK)
        names = sorted(n for n in os.listdir(os.path.join(ROOT, "warehouse", "supabase", "migrations")) if "thesis" in n)
        self.assertEqual(names, ["024_thesis.sql", "025_thesis_providers.sql"])             # no migration of this session: no stored row is rewritten or removed
        for name in ("tie.py", "pages.py", "store.py", "providers.py"):
            self.assertNotIn("thesis_runs set", src("warehouse", "thesis", name), name)     # only run.py writes the runs table, and only the run it was given
        code = src("warehouse", "thesis", "run.py")
        self.assertEqual(code.count("update public.thesis_runs set"), 3)                    # claim, finish, fail: each "where run_id = %s"
        self.assertEqual(code.count("where run_id = %s"), 3)

    def test_no_connector_of_a_licensed_database_is_called_by_the_run(self):
        for name in ("run.py", "tie.py", "pages.py", "store.py", "providers.py"):
            code = src("warehouse", "thesis", name)
            self.assertNotIn("connectors", code.split('"""', 2)[2], name)


class Storage:
    """A stand-in for the storage API: objects by path, every call recorded."""

    def __init__(self):
        self.objects, self.calls = {}, []

    def __call__(self, method, url, headers, body=None, timeout=60):
        path = url.split("/storage/v1/", 1)[1].split("?")[0]
        self.calls.append((method, path, dict(headers)))
        key = path.split("object/erw-thesis/", 1)[1]
        if method == "GET":
            return (200, self.objects[key]) if key in self.objects else (400, b'{"statusCode":"404","error":"not_found","message":"Object not found"}')
        if key in self.objects and headers.get("x-upsert") != "true":
            return 409, b'{"error":"Duplicate","message":"The resource already exists"}'
        self.objects[key] = body
        return 200, b"{}"


class RunnerKeepsWhatItPaidFor(unittest.TestCase):
    """The runner's files are discarded with it: a run whose store is the bucket keeps its state there, and a run can be
    started on the trends of a saved state kept there (the like-for-like run of sessions 142 and 147, on the runner)."""

    ENV = {"SUPABASE_URL": "https://abc.supabase.co/rest/v1/", "SUPABASE_SERVICE_KEY": "service-key-not-real"}

    def handle(self, send):
        return es.BucketStore(self.ENV["SUPABASE_URL"], self.ENV["SUPABASE_SERVICE_KEY"], "a-niche__any__any", send=send, sleep=lambda s: None)

    def test_a_state_is_written_once_under_its_own_name_and_read_back(self):
        send = Storage()
        h = self.handle(send)
        state = {"run_id": "20261008T120000Z-abc123", "notes_b": "a paid answer", "land": {"organisations": []}}
        where = h.keep_state("a-niche_20261008T120000Z-abc123", state)
        self.assertIn("erw-thesis/states/a-niche_20261008T120000Z-abc123.json.gz", where)
        self.assertEqual(list(send.objects), ["states/a-niche_20261008T120000Z-abc123.json.gz"])
        self.assertEqual(json.loads(gzip.decompress(send.objects["states/a-niche_20261008T120000Z-abc123.json.gz"])), state)
        self.assertEqual(send.calls[0][2]["x-upsert"], "false")
        self.assertIn("already held, not replaced", h.keep_state("a-niche_20261008T120000Z-abc123", {"other": 1}))        # never replaced
        self.assertEqual(json.loads(gzip.decompress(send.objects["states/a-niche_20261008T120000Z-abc123.json.gz"])), state)
        self.assertEqual(es.read_state("a-niche_20261008T120000Z-abc123", env=self.ENV, send=send), state)
        self.assertFalse(any(k.startswith("evidence/") for k in send.objects))                                              # the evidence store is not touched by it

    def test_a_name_that_is_not_a_states_name_is_refused(self):
        for bad in ("", "../evidence/x", "a/b", "a b", "x" * 200, ".hidden"):
            with self.assertRaises(ValueError):
                es.state_object(bad)
        self.assertEqual(es.state_object("geothermal-mapping-and-sensing_20261006T193007Z-8fea8a"), "states/geothermal-mapping-and-sensing_20261006T193007Z-8fea8a.json.gz")
        with self.assertRaises(RuntimeError):
            es.read_state("not-there", env=self.ENV, send=Storage())
        with self.assertRaises(RuntimeError):
            es.read_state("any", env={"SUPABASE_URL": "", "SUPABASE_SERVICE_KEY": ""})                                      # no key, no bucket: said, and no request made

    def test_only_a_run_whose_store_is_the_bucket_keeps_its_state_there_and_a_refusal_never_costs_the_run(self):
        log, send = [], Storage()
        self.assertEqual(R.keep_in_bucket(es.FileStore("x.json"), False, "n", {"a": 1}, log.append), "")
        self.assertEqual(R.keep_in_bucket(None, True, "n", {"a": 1}, log.append), "")
        self.assertEqual(send.calls, [])
        where = R.keep_in_bucket(self.handle(send), True, "a-niche_run", {"notes_b": "paid"}, log.append)
        self.assertIn("states/a-niche_run.json.gz", where)
        kept = json.loads(gzip.decompress(send.objects["states/a-niche_run.json.gz"]))
        self.assertEqual(kept["notes_b"], "paid")
        self.assertIsInstance(kept["ledger"], list)                 # the run's own rows of the cost ledger travel with it

        class Refusing:
            kind = "bucket"

            def keep_state(self, name, state):
                raise RuntimeError("the storage API answered 500 on the state's write")

        self.assertEqual(R.keep_in_bucket(Refusing(), True, "n", {"a": 1}, log.append), "")
        self.assertTrue(any("STATE NOT KEPT IN THE BUCKET" in ln for ln in log))

    def test_the_run_reads_a_bucket_state_before_anything_is_paid_for_and_keeps_its_own_after(self):
        code = src("warehouse", "thesis", "run.py")
        one = code.split("def one(", 1)[1].split("\ndef main(", 1)[0]
        self.assertLess(one.index("es.read_state(name)"), one.index("execute(r, run_id"))
        self.assertIn("landscape_from=landscape_from", one)
        self.assertEqual(one.count("keep_in_bucket(handle, in_bucket,"), 3)                 # the finished state, and the partial state on a stop and on a failure
        self.assertEqual(R.BUCKET_STATE, "bucket:")

    def test_the_workflow_runs_the_pages_runs_as_before_and_takes_a_run_by_hand(self):
        yml = src(".github", "workflows", "thesis.yml")
        import yaml
        wf = yaml.safe_load(yml)
        inputs = wf[True]["workflow_dispatch"]["inputs"]
        self.assertEqual(list(inputs), ["run_id", "niche", "stage", "geography", "landscape_from", "max_usd", "session"])
        self.assertTrue(all(not v.get("required") and v.get("default") == "" for v in inputs.values()))
        self.assertNotIn("schedule", wf[True])
        script = wf["jobs"]["run"]["steps"][-1]["run"]
        self.assertIn('python warehouse/thesis/run.py --run-id "$RUN_ID"', script)          # the page's run, word for word as before
        self.assertIn("python warehouse/thesis/run.py --queue", script)
        self.assertIn('python warehouse/thesis/run.py --niche "$NICHE" --stage "${STAGE:-}" --geography "${GEOGRAPHY:-}" --store', script)
        self.assertIn('--landscape-from "$LANDSCAPE_FROM"', script)
        self.assertIn('--max-usd "$MAX_USD"', script)
        self.assertNotIn("${{", script)                                                     # no input is written into the script: each arrives as an environment value
        self.assertNotIn("--no-fetch", yml)
        self.assertNotIn("--evidence-store file", yml)
        self.assertNotIn("git push", yml)
        self.assertEqual(wf["permissions"], {"contents": "read"})


class Files(unittest.TestCase):
    PARTS = (("warehouse", "thesis", "tie.py"), ("warehouse", "thesis", "run.py"), ("warehouse", "thesis", "pages.py"), ("warehouse", "thesis", "store.py"),
             ("warehouse", "thesis", "providers.py"), ("warehouse", "thesis", "vendor_pages.csv"), (".github", "workflows", "thesis.yml"),
             ("tests", "test_session158.py"), ("tests", "test_session147.py"), ("tests", "fixtures", "session158", "name_rule.json"),
             ("docs", "methods", "thesis_builder.md"), ("site", "lib", "thesis", "providers.ts"), ("site", "lib", "thesis", "types.ts"),
             ("site", "app", "api", "thesis", "provider", "route.ts"), ("site", "components", "thesis", "PitchbookPanel.tsx"),
             ("site", "components", "thesis", "Report.tsx"), ("site", "scripts", "test-thesis-providers.mjs"), ("site", "scripts", "check-thesis.mjs"),
             ("site", "scripts", "thesis-stub.mjs"))

    def test_no_em_dash_in_the_sessions_files(self):
        for parts in self.PARTS:
            self.assertNotIn(chr(0x2014), src(*parts), parts)

    def test_the_fixture_is_real_and_says_where_it_is_from(self):
        self.assertIn("runs/session158/make_fixture.py", NAME["note"])
        self.assertEqual([x["row"]["name"] for x in NAME["store"]["rows"]], [COMPANY])
        self.assertEqual(NAME["store"]["rows"][0]["run_id"], "20261007T215433Z-596e3d")
        import hashlib
        for url, p in NAME["store"]["pages"].items():
            self.assertTrue(p["excerpt"] and len(p["saved_text_sha256"]) == 64, url)
            self.assertEqual(hashlib.sha256(p["text"].encode("utf-8")).hexdigest(), p["text_sha256"], url)
        self.assertEqual(sorted(tie.domain(u) for u in NAME["store"]["sources"]), ["geothermal.tech", "geothermal.tech"])

    def test_thesis_stays_in_review_and_the_menu_is_not_this_sessions(self):
        self.assertIn('"/thesis": "review"', src("site", "lib", "release.ts"))

    def test_the_rulings_are_not_in_the_published_methods(self):
        for name in os.listdir(os.path.join(ROOT, "docs", "methods")):
            if name.endswith(".md") and name != "thesis_builder.md":          # thesis_builder.md is internal and not built into the site (session 135)
                text = src("docs", "methods", name)
                for w in ("NEAR_SAME", "proper_noun", "vendor_pages.csv", "made of the niche"):
                    self.assertNotIn(w, text, (name, w))

    def test_the_internal_method_states_the_rulings(self):
        text = src("docs", "methods", "thesis_builder.md")
        for w in ("proper noun", "NEAR_SAME", "90 percent", "vendor_pages.csv", "vendor page", "Crunchbase answers are not kept until its terms are ruled on",
                  "states/", "LIST_MIN"):
            self.assertIn(w, text, w)

    def test_this_module_changes_no_environment_at_import(self):
        code = src("tests", "test_session158.py")
        top = code.split("class MadeOfTheNichesOwnWords")[0]
        self.assertNotIn("os.environ[", top.split("def setUpModule")[0])
        self.assertIn("def setUpModule", top)
        self.assertIn("def tearDownModule", top)
        self.assertNotIn("origin/" + "main", code)                  # asserts on file contents, never on what a branch changed


if __name__ == "__main__":
    unittest.main()
