"""Session 130: the deals tracker re-aimed at power deals (version 3), and its rule: no number without its sentence.

Energy Research Warehouse (ERW). No request leaves the machine and no model is called. The tests read what is in git:
the news table (warehouse/output/news_stories.csv), the model's answers as returned on 6 October 2026
(warehouse/deals/answers_v3.jsonl and second_read_v3.jsonl) and the site's copy (site/data/deals_v3.json). The stories
in the small cases below are real titles and summaries of that table, copied as held.

    python -m unittest tests.test_session130 -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/deals"):
    sys.path.insert(0, os.path.join(ROOT, p))

import extract_v3 as x  # noqa: E402


def story(i, title, summary=""):
    return {"event_id": f"s{i}", "event_date": f"2026-09-{i:02d}T10:00:00Z", "title": title, "summary": summary or title,
            "source": "an outlet", "source_url": f"https://example.org/{i}"}


# real stories of news_stories.csv, as held
STATKRAFT = story(1, "Statkraft, Greenvolt sign 10-year BESS toll in Poland",
                  "Statkraft and Greenvolt Power have signed a 10-year tolling agreement covering 400MW of BESS across two operating projects in Poland.")
PPL = story(2, "Blackstone to buy Pennsylvania power plant for about $1 billion")
BLOOM = story(3, "Bloom Energy to supply up to 2.8 GW of fuel cells under expanded Oracle deal")
FORD = story(4, "Ford unit signs five-year energy storage deal with EDF")
KKR = story(5, "KKR Buys Total Renewable Power Stake in €1.8 Billion Deal")
CHEVRON = story(6, "Microsoft in Talks With Chevron, Engine No. 1 Over $7 Billion Texas Power Plant")
LINEA_A = story(7, "Linea Energy Closes Project Debt Financing and Preferred Equity Commitment for 250 MW / 500 MWh Mesa View BESS in Texas")
LINEA_B = story(9, "Linea Energy closes debt financing and preferred equity for 250 MW / 500 MWh Texas battery project")


def answer(**kw):
    d = {k: "" for k in x.SCHEMA["properties"]["deals"]["items"]["required"]}
    d.update(c=0, kind="other", other_parties=[], technology=[], datacenter=False)
    d.update(kw)
    return d


class Sentences(unittest.TestCase):
    def test_a_title_is_one_sentence(self):
        self.assertEqual(x.find_sentence("for about $1 billion", [PPL]), ("s2", PPL["title"]))

    def test_the_whole_sentence_of_the_summary_is_kept_not_the_part_given(self):
        sid, s = x.find_sentence("a 10-year tolling agreement covering 400MW", [STATKRAFT])
        self.assertEqual(sid, "s1")
        self.assertEqual(s, STATKRAFT["summary"])

    def test_words_no_story_holds_are_not_found(self):
        self.assertIsNone(x.find_sentence("a 12-year tolling agreement", [STATKRAFT]))
        self.assertIsNone(x.find_sentence("", [STATKRAFT]))

    def test_a_summary_is_split_at_its_sentence_ends(self):
        self.assertEqual(x.split_sentences("One closed. Two signed a 5.4-GW deal. Three"), ["One closed.", "Two signed a 5.4-GW deal.", "Three"])


class Numbers(unittest.TestCase):
    def test_a_size_needs_its_unit_and_takes_its_scale(self):
        self.assertIsNone(x.number_ok("mw", 2800, "2.8 GW"))
        self.assertIsNone(x.number_ok("mw", 400, "400MW"))
        self.assertIsNone(x.number_ok("mwh", 1200, "1.2GWh"))
        self.assertIn("names no MW unit", x.number_ok("mw", 400, "400"))
        self.assertIn("names no MW unit", x.number_ok("mw", 500, "500 MWh"))      # megawatt-hours are not megawatts
        self.assertIn("is not what", x.number_ok("mw", 2.8, "2.8 GW"))            # 2.8 GW is 2,800 MW, nothing else

    def test_a_range_is_not_one_number(self):
        self.assertIn("a range", x.number_ok("mw", 200, "200 to 300 MW"))
        self.assertIn("a range", x.number_ok("mw", 300, "200-300 MW"))

    def test_dollars_are_us_dollars_stated_as_such(self):
        self.assertIsNone(x.number_ok("dollars", 1_000_000_000, "about $1 billion"))
        self.assertIsNone(x.number_ok("dollars", 1_360_000_000, "$1.36 bln"))
        self.assertIn("not in US dollars", x.number_ok("dollars", 1_800_000_000, "€1.8 Billion"))
        self.assertIn("names no dollars", x.number_ok("dollars", 1_000_000_000, "1 billion"))

    def test_a_term_is_in_years_and_may_be_a_word(self):
        self.assertIsNone(x.number_ok("term_years", 10, "10-year"))
        self.assertIsNone(x.number_ok("term_years", 5, "five-year"))
        self.assertIn("in months", x.number_ok("term_years", 18, "18-month"))
        self.assertIn("names no years", x.number_ok("term_years", 10, "10"))

    def test_a_price_is_per_unit_of_power_or_energy(self):
        self.assertIsNone(x.number_ok("price_value", 50, "$50 per MWh"))
        self.assertIsNone(x.number_ok("price_value", 4.5, "4.5 cents/kWh"))
        self.assertIn("not a price per unit", x.number_ok("price_value", 50, "$50"))

    def test_a_number_is_kept_only_with_its_sentence_and_its_words(self):
        ok = answer(term_years="10", term_text="10-year", term_sentence=STATKRAFT["summary"], mw="400", mw_text="400MW",
                    mw_sentence="a 10-year tolling agreement covering 400MW of BESS")
        got, why = x.check_number("mw", ok, [STATKRAFT])
        self.assertIsNone(why)
        self.assertEqual((got[0], got[1], got[2], got[3]), (400.0, "s1", STATKRAFT["summary"], "400MW"))
        for bad, reason in ((dict(mw_sentence=""), "no words or no sentence"), (dict(mw_text=""), "no words or no sentence"),
                            (dict(mw_sentence="Statkraft signed a 400MW toll in Poland last week."), "not in a story"),
                            (dict(mw_text="400 MW of solar"), "are not in its sentence"), (dict(mw="450"), "is not what")):
            got, why = x.check_number("mw", dict(ok, **bad), [STATKRAFT])
            self.assertIsNone(got)
            self.assertIn(reason, why)
        self.assertEqual(x.check_number("mwh", ok, [STATKRAFT]), (None, None))    # not stated: blank, and no complaint

    def test_the_word_that_limits_a_number(self):
        self.assertEqual(x.qualifier(BLOOM["title"], "2.8 GW"), "up to")
        self.assertEqual(x.qualifier(PPL["title"], "about $1 billion"), "about")
        self.assertEqual(x.qualifier(PPL["title"], "$1 billion"), "about")
        self.assertEqual(x.qualifier(FORD["title"], "five-year"), "")
        self.assertEqual(x.qualifier(CHEVRON["title"], "$7 Billion"), "")          # "in talks over" is not "more than"
        self.assertEqual(x.qualifier("Samsung SDI unit signs US battery deal worth over $1.36 bln for energy storage systems", "$1.36 bln"), "over")


class Deals(unittest.TestCase):
    def test_a_deal_with_its_sentence_keeps_what_the_words_hold(self):
        d, why = x.read_deal(answer(kind="tolling", buyer="Statkraft", seller="Greenvolt Power", other_parties=["Goldman Sachs"], asset="BESS",
                                    technology=["storage", "storage", "wave"], place="Poland", country="Poland", country_text="in Poland",
                                    status="signed", status_text="have signed", evidence=STATKRAFT["summary"],
                                    term_years="10", term_text="10-year", term_sentence=STATKRAFT["summary"],
                                    dollars="500000000", dollars_text="$500 million", dollars_sentence="worth $500 million"), [STATKRAFT])
        self.assertEqual((d["buyer"], d["seller"], d["others"]), ("Statkraft", "Greenvolt Power", []))   # a party the words do not hold is dropped
        self.assertEqual(d["technology"], ["storage"])
        self.assertEqual((d["place"], d["country"], d["status"]), ("Poland", "Poland", "signed"))
        self.assertEqual(list(d["numbers"]), ["term_years"])                                            # the invented dollars are not kept
        self.assertTrue(any("Goldman Sachs" in w for w in why) and any("dollars" in w for w in why))

    def test_no_evidence_sentence_no_deal_and_no_party_no_deal(self):
        d, why = x.read_deal(answer(buyer="Statkraft", evidence="Statkraft bought a battery."), [STATKRAFT])
        self.assertIsNone(d)
        self.assertIn("evidence sentence is not in a story", why[0])
        d, why = x.read_deal(answer(buyer="Vattenfall", evidence=STATKRAFT["title"]), [STATKRAFT])
        self.assertIsNone(d)
        self.assertIn("name no party", why[-1])

    def test_a_deal_that_states_no_number_keeps_blanks(self):
        d, why = x.read_deal(answer(buyer="KKR", evidence=KKR["title"], dollars="1800000000", dollars_text="€1.8 Billion", dollars_sentence=KKR["title"]), [KKR])
        self.assertEqual(d["numbers"], {})                                                              # euros are not turned into dollars
        self.assertIn("not in US dollars", why[0])


def deal(i, kind, buyer, seller, date, others=(), tech=(), **numbers):
    return dict(id=f"d{i}", kind=kind, buyer=buyer, seller=seller, others=list(others), date=date, technology=list(tech), story_ids=[f"s{i}"],
                asset="", place="", state="", country="", status="", datacenter=False, price_unit="", folded=[],
                evidences=[dict(story_id=f"s{i}", sentence="x")],
                numbers={f: dict(value=float(v), story_id=f"s{i}", sentence="x", text="x", qualifier="") for f, v in numbers.items()})


class Folding(unittest.TestCase):
    def test_the_same_parties_or_a_party_and_a_figure(self):
        a = deal(1, "acquisition", "KKR", "EDF", "2026-07-01T00:00:00Z")
        self.assertTrue(x.same_deal(a, deal(2, "acquisition", "EDF", "KKR Inc.", "2026-07-20T00:00:00Z")))
        self.assertFalse(x.same_deal(a, deal(2, "acquisition", "EDF", "KKR", "2026-10-20T00:00:00Z")))          # 111 days apart
        self.assertFalse(x.same_deal(a, deal(2, "project_finance", "EDF", "KKR", "2026-07-02T00:00:00Z")))      # another kind
        b = deal(3, "project_finance", "", "Linea Energy", "2026-10-01T00:00:00Z", mw=250, mwh=500)
        self.assertTrue(x.same_deal(b, deal(4, "project_finance", "", "Linea Energy", "2026-10-02T00:00:00Z", mw=250)))
        self.assertFalse(x.same_deal(b, deal(4, "project_finance", "", "Linea Energy", "2026-10-02T00:00:00Z", mw=300)))   # the sizes disagree
        self.assertFalse(x.same_deal(b, deal(4, "project_finance", "", "Linea Energy", "2026-10-02T00:00:00Z")))           # a party, no figure

    def test_two_reports_on_nearly_the_same_day_one_naming_one_party(self):
        a = deal(1, "power_purchase", "Google", "Commonwealth", "2025-06-30T08:00:00Z", tech=["nuclear"])
        b = deal(2, "power_purchase", "Google", "", "2025-06-30T15:00:00Z", tech=["nuclear"])
        self.assertTrue(x.same_deal(a, b))
        self.assertFalse(x.same_deal(a, dict(b, technology=["solar"])))
        self.assertFalse(x.same_deal(a, dict(b, technology=[])))
        self.assertFalse(x.same_deal(a, dict(b, date="2025-07-10T08:00:00Z")))
        self.assertFalse(x.same_deal(a, deal(2, "power_purchase", "Google", "Fervo", "2025-06-30T15:00:00Z", tech=["nuclear"])))

    def test_the_earliest_is_kept_with_every_story_and_a_gap_filled_with_its_sentence(self):
        a = deal(1, "project_finance", "", "Linea Energy", "2026-10-01T00:00:00Z", mw=250)
        b = deal(2, "project_finance", "", "Linea Energy", "2026-10-02T00:00:00Z", mw=250, mwh=500)
        kept, pairs = x.fold([b, a])
        self.assertEqual((len(kept), pairs), (1, [("d2", "d1")]))
        k = kept[0]
        self.assertEqual((k["id"], k["story_ids"], k["folded"]), ("d1", ["s1", "s2"], ["d2"]))
        self.assertEqual((k["numbers"]["mw"]["story_id"], k["numbers"]["mwh"]["story_id"]), ("s1", "s2"))   # the kept figure stays; the gap brings its own story

    def test_a_party_is_listed_once_after_a_fold(self):
        a = deal(1, "project_finance", "Brookfield", "Bloom Energy", "2025-10-13T00:00:00Z", dollars=5e9)
        b = deal(2, "project_finance", "", "", "2025-10-14T00:00:00Z", others=["Bloom Energy", "Brookfield"], dollars=5e9)
        kept, _ = x.fold([a, b])
        self.assertEqual((kept[0]["buyer"], kept[0]["seller"], kept[0]["others"]), ("Brookfield", "Bloom Energy", []))


class SecondRead(unittest.TestCase):
    def test_only_a_power_deal_is_kept_and_a_deal_not_read_twice_is_not(self):
        ds = [deal(i, "other", "A", "B", "2026-01-01T00:00:00Z") for i in range(4)]
        second = {"d0": dict(verdict="power_deal", kind="acquisition", roles="stated", datacenter=True),
                  "d1": dict(verdict="not_power", kind="other"), "d2": dict(verdict="not_a_transaction", kind="other")}
        kept, c = x.confirmed(ds, second)
        self.assertEqual([d["id"] for d in kept], ["d0"])
        self.assertEqual((kept[0]["kind"], kept[0]["first_kind"], kept[0]["datacenter"]), ("acquisition", "other", True))
        self.assertEqual((c["second_power_deal"], c["second_not_power"], c["second_not_a_transaction"], c["second_not_read"], c["kind_changed"], c["datacenter_changed"]), (1, 1, 1, 1, 1, 1))

    def test_sides_the_story_does_not_state_are_not_kept_as_sides(self):
        kept, c = x.confirmed([deal(0, "other", "KKR", "SK", "2026-06-30T00:00:00Z", others=["Macquarie"])], {"d0": dict(verdict="power_deal", kind="other", roles="not_stated")})
        self.assertEqual((kept[0]["buyer"], kept[0]["seller"], kept[0]["others"], c["roles_not_stated"]), ("", "", ["KKR", "SK", "Macquarie"], 1))

    def test_a_figure_not_the_deals_own_and_a_name_not_a_party_are_blanked(self):
        d = deal(0, "project_finance", "Blackstone", "VoltaGrid", "2026-05-11T00:00:00Z", dollars=1e9, mw=100)
        kept, c = x.confirmed([d], {"d0": dict(verdict="power_deal", kind="project_finance", roles="stated", not_the_deals=["dollars", "mwh"], not_parties=["Blackstone"])})
        self.assertEqual((kept[0]["buyer"], kept[0]["seller"], list(kept[0]["numbers"])), ("", "VoltaGrid", ["mw"]))
        self.assertEqual((c["numbers_not_the_deals"], c["names_not_parties"]), (1, 1))
        self.assertEqual(list(d["numbers"]), ["dollars", "mw"])                                             # the first read is left as it was
        kept, c = x.confirmed([deal(0, "other", "Blackstone", "", "2026-05-11T00:00:00Z")], {"d0": dict(verdict="power_deal", kind="other", not_parties=["Blackstone"])})
        self.assertEqual((kept, c["no_party_left"]), ([], 1))


class Order(unittest.TestCase):
    def test_a_cluster_takes_the_first_tier_any_of_its_stories_has(self):
        rows = [dict(event_id="a", cluster_id="c1", title="Oil falls", summary="Oil falls", scored_at="t", sector="oil"),
                dict(event_id="b", cluster_id="c1", title="Oil falls again", summary="Oil falls again", scored_at="t", sector="oil"),
                dict(event_id="c", cluster_id="c2", title="Utility signs 200 MW solar PPA", summary="", scored_at="t", sector="renewables"),
                dict(event_id="d", cluster_id="", title="Developer signs 20-year contract", summary="", scored_at="", sector=""),
                dict(event_id="e", cluster_id="c3", title="Rain in Spain", summary="", scored_at="t", sector="other"),
                dict(event_id="f", cluster_id="", title="Rain in Spain", summary="", scored_at="", sector="")]
        p = x.plan(pd.DataFrame(rows), {"b"}).set_index("event_id")
        self.assertEqual(p["tier"].to_dict(), {"a": 1, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5})
        self.assertEqual(p.loc["d", "cluster"], "story:d")

    def test_a_summary_that_only_repeats_the_title_is_not_sent(self):
        g = pd.DataFrame([dict(title="A signs PPA", summary="A signs PPA Reuters"), dict(title="B buys C", summary="The deal closes in May.")])
        self.assertEqual(x.items_of([g]), [{"c": 0, "stories": [{"title": "A signs PPA"}, {"title": "B buys C", "summary": "The deal closes in May."}]}])

    def test_the_schema_asks_for_the_words_and_the_sentence_of_every_number(self):
        need = set(x.SCHEMA["properties"]["deals"]["items"]["required"])
        for f in x.NUMBERS:
            self.assertTrue({f, x.TEXT_OF[f], x.SENTENCE_OF[f]} <= need, f)
        self.assertEqual(x.KINDS, ["power_purchase", "tolling", "offtake", "project_finance", "acquisition", "other"])


class TheTablesFromTheAnswersHeld(unittest.TestCase):
    """The tables rebuilt in memory from the answers and the news table in git: the rule holds on every number."""

    @classmethod
    def setUpClass(cls):
        cls.news = x.read_news()
        v2 = set(pd.read_csv(x.CHECKED_V2, dtype=str, keep_default_na=False)["story_id"])
        cls.kept, cls.pairs, cls.dropped, cls.counts = x.assemble(cls.news, x.load_answers(), v2, x.load_second())
        cls.deals, cls.evidence = x.tables(cls.kept, cls.news)

    def test_every_number_has_its_sentence_in_a_story_held(self):
        n = x.no_number_without_its_sentence(self.deals, self.evidence, self.news)
        self.assertGreater(n, 50)
        self.assertEqual(n, int(sum((self.deals[f] != "").sum() for f in x.NUMBERS)))

    def test_the_check_fails_when_a_sentence_is_missing_or_changed(self):
        with_number = self.evidence[self.evidence["field"] != "deal"].index
        gone = self.evidence.drop(with_number[0])
        with self.assertRaisesRegex(RuntimeError, "has no sentence"):
            x.no_number_without_its_sentence(self.deals, gone, self.news)
        changed = self.evidence.copy()
        changed.loc[with_number[0], "sentence"] = "A sentence no story holds, with 500 MW in it."
        with self.assertRaisesRegex(RuntimeError, "is not in story"):
            x.no_number_without_its_sentence(self.deals, changed, self.news)

    def test_the_words_of_every_number_are_in_its_sentence_and_say_the_number(self):
        for r in self.evidence[self.evidence["field"] != "deal"].to_dict("records"):
            self.assertIn(x.norm(r["text"]), x.norm(r["sentence"]), r["event_id"])
            self.assertIsNone(x.number_ok(r["field"], float(r["value"]), r["text"]), r["event_id"])

    def test_every_deal_names_a_party_and_has_its_evidence_sentence(self):
        self.assertFalse((self.deals["parties"] == "").any())
        with_evidence = set(self.evidence[self.evidence["field"] == "deal"]["deal_id"])
        self.assertEqual(set(self.deals["event_id"]) - with_evidence, set())
        self.assertTrue(self.deals["event_id"].is_unique and self.evidence["event_id"].is_unique)

    def test_no_deal_is_in_the_table_without_a_second_read_that_calls_it_a_power_deal(self):
        second = x.load_second()
        ids = set(self.deals["event_id"]) | {i for f in self.deals["folded_ids"] for i in f.split(";") if i}
        self.assertTrue(all(second[i]["verdict"] == "power_deal" for i in ids))
        self.assertEqual(self.counts["second_not_read"], 0)

    def test_the_public_table_holds_no_outlet_text(self):
        self.assertFalse({"sentence", "text", "evidence"} & set(x.DEAL_COLS))
        self.assertTrue({"sentence", "text"} <= set(x.EVIDENCE_COLS))

    def test_the_comparison_counts_what_the_tables_hold(self):
        r = x.stated(self.deals, "3")
        self.assertEqual(r["size"], int(((self.deals["mw"] != "") | (self.deals["mwh"] != "")).sum()))
        self.assertEqual(r["term"], int((self.deals["term_years"] != "").sum()))
        self.assertLessEqual(r["price_usd_mwh"], r["price"])


class TheSitesCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(x.SITE_COPY, encoding="utf-8") as f:
            cls.file = json.load(f)
        cls.rows, cls.s = cls.file["deals"], cls.file["summary"]

    def test_the_copy_holds_public_fields_only(self):
        keys = set(self.rows[0])
        self.assertFalse({"sentence", "text", "evidence", "model_id"} & keys)
        self.assertNotIn("sentence", json.dumps(self.file["deals"]))

    def test_every_number_of_the_copy_names_the_story_it_was_read_from(self):
        for r in self.rows:
            src = dict(p.split("=", 1) for p in r["number_stories"].split(";") if p)
            for f in x.NUMBERS:
                self.assertEqual(r[f] != "", f in src, (r["event_id"], f))
            self.assertTrue(set(src.values()) <= set(r["story_ids"].split(";")), r["event_id"])

    def test_the_summary_is_the_copys_own_count(self):
        last = self.s["compare"]["all"][-1]
        self.assertEqual((last["deals"], self.s["deals"]), (len(self.rows), len(self.rows)))
        self.assertEqual(last["size"], sum(1 for r in self.rows if r["mw"] or r["mwh"]))
        self.assertEqual(last["price"], sum(1 for r in self.rows if r["price_value"]))
        self.assertEqual(last["term"], sum(1 for r in self.rows if r["term_years"]))
        self.assertEqual(self.s["compare"]["storage"][-1]["deals"], sum(1 for r in self.rows if r["storage"] == "true"))
        self.assertEqual(self.s["compare"]["datacenter"][-1]["deals"], sum(1 for r in self.rows if r["datacenter"] == "true"))
        self.assertEqual(self.s["stories_read"] + self.s["stories_remaining"], self.s["stories_held"])
        self.assertLess(self.s["usd"], 8.0)                                                                # the session's cap

    def test_the_page_library_counts_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        js = ("const fs = (await import('node:fs')).default; const m = await import('./lib/deals3.ts');"
              "const f = JSON.parse(fs.readFileSync('./data/deals_v3.json', 'utf-8')); const all = f.deals.map(m.toDeal);"
              "const x = m.inputsOf({view: 'storage', states: 'size', kind: 'nonsense'}, all);"
              "console.log(JSON.stringify({all: m.counts(all), storage: m.select(all, m.inputsOf({view: 'storage'}, all)).length,"
              " dc: m.select(all, m.inputsOf({view: 'datacenter'}, all)).length, x, picked: m.select(all, x).length, href: m.hrefOf(x),"
              " linked: all.every((d) => [d.mw, d.mwh, d.term, d.dollars, d.price].every((n) => n === null || n.url.startsWith('http'))),"
              " sentence: m.summary(all, all, m.inputsOf({}, all)), tech: m.technologies(all)}))")
        r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
                raise unittest.SkipTest("this node does not read TypeScript files")
            raise AssertionError(r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        last = self.s["compare"]["all"][-1]
        c = got["all"]
        self.assertEqual((c["deals"], c["size"], c["withMw"], c["withMwh"], c["price"], c["term"], c["withDollars"]),
                         (last["deals"], last["size"], last["mw"], last["mwh"], last["price"], last["term"], last["dollars"]))
        self.assertEqual(c["mw"], sum(float(r["mw"]) for r in self.rows if r["mw"]))
        self.assertEqual((got["storage"], got["dc"]), (self.s["compare"]["storage"][-1]["deals"], self.s["compare"]["datacenter"][-1]["deals"]))
        self.assertEqual((got["x"]["kind"], got["x"]["view"], got["x"]["states"]), ("", "storage", "size"))     # a choice the page does not offer is dropped
        self.assertEqual(got["picked"], self.s["compare"]["storage"][-1]["size"])
        self.assertEqual(got["href"], "/deals/v3?view=storage&states=size")
        self.assertTrue(got["linked"])                                                                         # every number opens its story
        self.assertIn(f"{last['size']} state a size, {last['price']} state a price and {last['term']} state a term.", got["sentence"].replace(",", ", ").replace(",  ", ", "))
        self.assertEqual({t["value"]: t["n"] for t in got["tech"] if t["value"] != "not stated"}, {k: v for k, v in self.s["technologies"].items() if v})


class TheRepository(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_the_page_is_in_review_and_its_tables_are_held(self):
        self.assertRegex(self.read("site", "lib", "release.ts"), r'"/deals/v3": "review"')
        hold = self.read("warehouse", "supabase", "live_set.yaml").split("catalogue_hold:")[1].split("review_hold:")[0]
        self.assertRegex(hold, r"(?m)^  - power_deals$")
        self.assertNotRegex(self.read("warehouse", "supabase", "live_set.yaml").split("catalogue_hold:")[0], r"power_deals")   # not loaded

    def test_version_2_is_as_it_was(self):
        r = subprocess.run(["git", "status", "--porcelain", "--", "warehouse/deals/extract.py", "site/app/deals/v2/page.tsx", "site/lib/deals2.ts",
                            "site/app/deals/page.tsx"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")

    def test_the_page_shows_no_sentence_and_calls_no_model(self):
        page = self.read("site", "app", "deals", "v3", "page.tsx")
        self.assertIn('from "@/data/deals_v3.json"', page)
        self.assertNotRegex(page, r"anthropic|supabase|\.sentence\b")

    def test_no_em_dash_in_what_this_session_wrote(self):
        for p in (("warehouse", "deals", "extract_v3.py"), ("site", "lib", "deals3.ts"), ("site", "app", "deals", "v3", "page.tsx"),
                  ("docs", "methods", "power_deals.md"), ("tests", "test_session130.py")):
            t = self.read(*p)
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)


if __name__ == "__main__":
    unittest.main()
