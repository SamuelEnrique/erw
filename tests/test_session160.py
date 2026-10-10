"""Session 160: the owner's four rulings of 8 October 2026 (evening) on the Thesis Builder (warehouse/thesis).

    "keep a page's last good text when it later refuses, with the retrieval date shown; a search result's title is
    not evidence, only page text is; a vendor page's sentence may tie a company but is labeled as a vendor page;
    merge a company that stands under several names into one by domain where it has one."

On saved real evidence: tests/fixtures/session160/rulings.json, cut from the bucket's evidence store as it was after
session 147's three runs and after the runner's run of session 158 (XGS Energy's page of renewablesnow.com, read on
7 October and refused with 403 on 8 October; Terra AI under its three names; the search result whose title tied
Teverra LLC). A page or a sentence written for a test says so. No network, no model call, no database: a machine
without the warehouse's tables runs every test here, and the tests of the real case skip when the fixture is absent.
"""
import copy
import importlib.util
import inspect
import json
import os
import random
import sys
import tempfile
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
tie, tb, pg = R.tie, R.tb, R.pg
FIX_PATH = os.path.join(ROOT, "tests", "fixtures", "session160", "rulings.json")
FIX = json.load(open(FIX_PATH, encoding="utf-8")) if os.path.exists(FIX_PATH) else None
NO_FIX = "the saved real evidence (tests/fixtures/session160/rulings.json) is not on this machine"
NAME_FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "session158", "name_rule.json"), encoding="utf-8"))
NICHE, TRENDS = NAME_FIX["store"]["niche"], NAME_FIX["trends"]
UA = "ERW research project, github.com/SamuelEnrique/erw"
EMPTY_WH = {"energy_companies": [], "energy_deals": []}
VENDORS = {"cbinsights.com": "CB Insights", "dealroom.co": "Dealroom", "sacra.com": "Sacra"}
RUN1, RUN2, RUN3 = "20261007T000000Z-test01", "20261008T000000Z-test02", "20261009T000000Z-test03"
DAY1, DAY2, DAY3 = "2026-10-07", "2026-10-08", "2026-10-09"
URL = "https://example.org/heatwell"                    # every page at example.org is written for these tests
TEXT = "Heatwell Labs won a DOE grant for resource characterization field tests in Nevada."
HTML = f"<html><body><p>{TEXT}</p></body></html>"


def by_name(rows):
    return {c["name"]: c for c in rows}


class Web:
    """A stand-in for the one network call. answers: {address: [answer, ...]}, used in order (the last one repeats).
    An answer is (status, body), (status, body, truncated) or an exception to raise. robots.txt answers 404 (no rule)
    unless given. Every request is recorded with its headers."""

    def __init__(self, answers):
        self.answers, self.asked = {u: list(a) for u, a in answers.items()}, []

    def __call__(self, url, headers, timeout, max_bytes):
        self.asked.append((url, dict(headers)))
        left = self.answers.get(url)
        if not left:
            return 404, {"content-type": "text/plain"}, b"", False
        a = left.pop(0) if len(left) > 1 else left[0]
        if isinstance(a, Exception):
            raise a
        status, body = a[0], a[1]
        return status, {"content-type": "text/html; charset=utf-8"}, body.encode("utf-8"), (a[2] if len(a) > 2 else False)


def pull(store, web, run_id, day, urls=(URL,)):
    t = {"t": 0.0}
    return pg.fetch_run(store, list(urls), run_id, day, get=web, sleep=lambda s: t.__setitem__("t", t["t"] + s), clock=lambda: t["t"], paused={"misoenergy.org"})


def store_of(rows, pages=None, sources=None):
    """A small store written for a test: rows [(name, website, cited addresses)] or [(name, website, cited, seq, kind)]."""
    s = tie.empty_store(NICHE, "startups", "United States")
    s["runs"] = [{"run_id": f"t{n}", "date": DAY1, "seq": n} for n in (1, 2, 3)]
    for r in rows:
        name, site, urls = r[0], r[1], r[2]
        seq, kind = (r[3] if len(r) > 3 else 1), (r[4] if len(r) > 4 else "private company")
        s["rows"].append({"key": tie.name_key(name), "run_id": f"t{seq}", "seq": seq, "row": {
            "name": name, "website": site, "kind": kind, "country": "United States", "location": "Reno, Nevada", "fits_stage": "yes",
            "description": "", "founders": "", "stage": "", "raised": "", "signal": "", "tam": "", "found_by": ["Q1"], "latest_source_year": "2026",
            "stage_primary": False, "raised_primary": False, "trends": [], "source_urls": list(urls)}})
    for url, text in (pages or {}).items():
        s["pages"][url] = {"address": url, "state": "fetched", "status": 200, "truncated": False, "text": text, "fetched": DAY1, "reason": ""}
    for url, (title, cited) in (sources or {}).items():
        s["sources"][url] = {"title": title, "cited": list(cited), "page_age": "", "fetched": DAY1, "sha": tie.sha(title), "first_run": "t1", "last_run": "t1", "history": []}
    return s


def judge_store(s, **k):
    return by_name(tie.judge(s, EMPTY_WH, NICHE, TRENDS, **k))


def real_store(xgs="before", upto=4):
    """The saved real evidence as a store: the rows as the runs saved them, XGS Energy's page as it was held on
    7 October ("before") or as the runner recorded it on 8 October ("after": refused, the earlier text in its history)."""
    s = tie.empty_store(FIX["niche"], FIX["stage"], FIX["geography"])
    s["runs"] = [r for r in FIX["runs"] if r["seq"] <= upto]
    s["rows"] = [copy.deepcopy(x) for x in FIX["rows"] if x["seq"] <= upto]
    s["pages"][FIX["xgs"]["address"]] = copy.deepcopy(FIX["xgs"][xgs])
    for u, p in FIX["terra_pages"].items():
        s["pages"][u] = copy.deepcopy(p)
    for u, x in dict(FIX["sources"], **{FIX["teverra"]["address"]: FIX["teverra"]["source"]}).items():
        s["sources"][u] = dict(copy.deepcopy(x), history=[])
    return s


def judge_real(s, **k):
    return by_name(tie.judge(s, EMPTY_WH, FIX["niche"], FIX["trends"], vendors=pg.labeled_vendors(), **k))


def refuse_as_the_runner_did(store):
    """The runner's own record of 8 October (answered 403) reaches the store as a replay copies it: from a shelf, with no request."""
    after = {k: v for k, v in FIX["xgs"]["after"].items() if k != "history"}
    web = Web({})
    t = {"t": 0.0}
    tally = pg.fetch_run(store, [FIX["xgs"]["address"]], "20261008T101706Z-605e62", DAY2, get=web, shelf={"pages": {FIX["xgs"]["address"]: after}, "robots": {}}, max_run=0,
                         sleep=lambda s: None, clock=lambda: t["t"], paused={"misoenergy.org"})
    return tally, web


class Saved:
    """A researcher holding sources, and no client."""

    def __init__(self):
        self.sources, self.erw = {}, []

    source = tb.Researcher.source
    texts_of = tb.Researcher.texts_of


def report_of(store, niche, trends):
    """The report a user reads, from a store: the run's own code after its paid calls, with no new organisation."""
    r = Saved()
    land = {"fact": "", "fact_sources": [], "organisations": []}
    a = {"scope": {"definition": "", "definition_sources": [], "value_chain": [], "excluded": [], "definitions": []},
         "trends": [dict(t, fact="", table={"columns": [], "rows": []}, chart={"kind": "none", "title": "", "category_column": 0, "value_columns": []}, unit="", sources=[]) for t in trends]}
    log, real = [], R.warehouse_rows
    R.warehouse_rows = lambda: {"energy_companies": [], "energy_deals": []}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.json")
            tie.save_store(store, path)
            rows, ctx = R.tied_rows(r, "20261008T000000Z-test01", niche, "startups", "United States", trends, land, path, log.append)
            report, placed = R.build_report(niche, "startups", "United States", r, a, dict(land, organisations=rows), {}, None, R.query_plan(niche, "United States", trends), log.append)
            tied = R.tie_done(ctx, placed, log.append)
    finally:
        R.warehouse_rows = real
    return report, tied, log


# ---------------------------------------------------------------------------------------------
# 1. a page's last good text is kept when the page later refuses
# ---------------------------------------------------------------------------------------------

class KeptText(unittest.TestCase):
    """Pages written for these tests, asked through the stand-in for the network."""

    def good_then(self, answer, robots=None):
        answers = {URL: [(200, HTML), answer]}
        if robots is not None:
            answers["https://example.org/robots.txt"] = robots
        web, store = Web(answers), tie.empty_store()
        first = pull(store, web, RUN1, DAY1)
        self.assertEqual((store["pages"][URL]["state"], store["pages"][URL]["text"], first["fetched"], first["kept"]), ("fetched", TEXT, 1, {}))
        second = pull(store, web, RUN2, DAY2)
        return store, second, web

    def test_a_refusal_after_a_good_read_keeps_the_text_and_its_date(self):
        store, tally, web = self.good_then((403, "Forbidden"))
        p = store["pages"][URL]
        self.assertEqual((p["state"], p["text"], p["retrieved"], p["fetched"]), ("kept", TEXT, DAY1, DAY2))
        self.assertEqual((p["status"], p["reason"]), (403, "answered 403"))                  # the refusal stands beside the text
        self.assertEqual({k: p["refusal"][k] for k in ("state", "status", "reason", "day", "run")},
                         {"state": "refused", "status": 403, "reason": "answered 403", "day": DAY2, "run": RUN2})
        self.assertTrue(p["refusal"]["at"].startswith("20") and p["retrieved_at"].startswith("20"))        # the time of each
        self.assertEqual((p["age_days"], p["retrieved_run"], len(p["refusals"])), (1, RUN1, 1))
        self.assertEqual(p["history"], [])                         # the text did not change: nothing went to the history
        self.assertEqual(tally["kept"], {URL: {"retrieved": DAY1, "reason": "answered 403", "status": 403, "age_days": 1}})
        self.assertEqual((tally["fetched"], tally["refused"], tally["changed"]), (0, {"403": 1}, []))
        self.assertTrue(tie.page_holds(p))
        self.assertEqual(tie.page_day(p), DAY1)
        self.assertEqual(tie.page_kept(p), {"retrieved": DAY1, "refused": DAY2, "status": 403, "reason": "answered 403", "age_days": 1})
        self.assertTrue(all(h == {"User-Agent": UA} for _, h in web.asked))

    def test_every_sentence_from_a_kept_text_carries_the_day_it_was_retrieved(self):
        store, _, _ = self.good_then((403, "Forbidden"))
        store["rows"] = store_of([("Heatwell Labs", "heatwell.example", [URL])])["rows"]
        store["runs"] = [{"run_id": RUN1, "date": DAY1, "seq": 1}]
        c = judge_store(store)["Heatwell Labs"]
        self.assertEqual([(e["tier"], e["fetched"], e["kept"]["retrieved"], e["kept"]["refused"], e["kept"]["age_days"]) for e in c["evidence"]], [("web", DAY1, DAY1, DAY2, 1)])
        line = c["ties"][3]["lines"][0]
        self.assertEqual((line["points"], line["kept"]["retrieved"], c["trends"]), (2, DAY1, [3]))            # one web sentence, strong: 2 points, as any page's sentence
        self.assertEqual(c["reason"]["kept"]["retrieved"], DAY1)
        off = judge_store(copy.deepcopy(store), kept=False)["Heatwell Labs"]                # as before the ruling: the page holds no sentence
        self.assertEqual((off["trends"], off["evidence"]), ([], []))

    def test_each_kind_of_failure_after_a_good_read_keeps_the_text(self):
        cases = {"a status of 400 or over": ((404, "gone"), None, "answered 404"),
                 "a server error": ((503, "busy"), None, "answered 503"),
                 "a timeout": (TimeoutError("no complete answer in 20 seconds"), None, "no answer: TimeoutError: no complete answer in 20 seconds"),
                 "an empty body": ((200, "<html><body></body></html>"), None, "answered 200 with no text in the html"),
                 "a truncated body": ((200, HTML, True), None, "truncated at 2000000 bytes"),
                 "a redirect that leads nowhere": ((302, ""), None, "answered 302"),
                 "a robots.txt that now disallows it": ((200, HTML), [(404, ""), (200, "User-agent: *\nDisallow: /heatwell\n")], "not fetched: robots.txt"),
                 "a robots.txt that cannot be read": ((200, HTML), [(404, ""), (403, "no")], "not fetched: robots.txt could not be read (robots.txt answered 403)")}
        for what, (answer, robots, reason) in cases.items():
            store, tally, _ = self.good_then(answer, robots)
            p = store["pages"][URL]
            self.assertEqual((p["state"], p["text"], p["retrieved"], p["reason"], p["truncated"]), ("kept", TEXT, DAY1, reason, False), what)
            self.assertEqual((p["refusal"]["reason"], p["refusal"]["day"], list(tally["kept"])), (reason, DAY2, [URL]), what)
            self.assertTrue(tie.page_holds(p), what)

    def test_a_page_never_read_holds_nothing(self):
        web, store = Web({URL: [(403, "Forbidden")]}), tie.empty_store()
        for run_id, day in ((RUN1, DAY1), (RUN2, DAY2)):
            tally = pull(store, web, run_id, day)
            p = store["pages"][URL]
            self.assertEqual((p["state"], p["text"], p["text_sha256"], tally["kept"]), ("refused", "", "", {}), day)
            self.assertNotIn("retrieved", p)
            self.assertFalse(tie.page_holds(p))
            self.assertIsNone(tie.page_kept(p))
        store["rows"] = store_of([("Heatwell Labs", "heatwell.example", [URL])])["rows"]
        self.assertEqual(judge_store(store)["Heatwell Labs"]["evidence"], [])
        self.assertEqual(pg.restore_kept(store), [])

    def test_a_refusal_of_our_own_keeps_no_earlier_text(self):
        """A licensed database's site and a paused publisher are refused by this code before any request: a text held of
        one from an earlier day (written for this test; no run holds one) is not kept."""
        for url, reason in (("https://www.crunchbase.com/organization/heatwell", "not fetched: licensed source needed"), ("https://www.misoenergy.org/heatwell", "not fetched: paused")):
            store = tie.empty_store()
            store["pages"][url] = {"address": url, "state": "fetched", "status": 200, "truncated": False, "text": TEXT, "text_sha256": "x", "fetched": DAY1, "fetched_at": "2026-10-07T00:00:00Z", "reason": "", "last_run": RUN1}
            web = Web({})
            tally = pull(store, web, RUN2, DAY2, [url])
            p = store["pages"][url]
            self.assertEqual((p["state"], p["reason"], p["text"], tally["kept"], web.asked), ("not fetched", reason, "", {}, []), url)
            self.assertFalse(tie.page_holds(p))
        self.assertEqual(pg.OUR_REFUSALS, ("not fetched: paused", "not fetched: licensed source needed", "not fetched: not a web address", "not fetched: not a public web address"))

    def test_a_kept_page_is_asked_once_a_day_and_a_later_good_read_replaces_it(self):
        new = "Heatwell Labs won a second DOE grant for resource characterization field tests in Utah."
        web, store = Web({URL: [(200, HTML), (403, "Forbidden"), (200, f"<html><body><p>{new}</p></body></html>")]}), tie.empty_store()
        pull(store, web, RUN1, DAY1)
        pull(store, web, RUN2, DAY2)
        asked = len(web.asked)
        again = pull(store, web, RUN2, DAY2)                        # the same day: held, not asked again
        self.assertEqual((again["held"], again["requested"], len(web.asked)), (1, 0, asked))
        tally = pull(store, web, RUN3, DAY3)
        p = store["pages"][URL]
        self.assertEqual((p["state"], p["text"], p["fetched"], tally["kept"], tally["changed"]), ("fetched", new, DAY3, {}, [URL]))
        self.assertNotIn("refusal", p)
        self.assertEqual([(r["status"], r["day"]) for r in p["refusals"]], [(403, DAY2)])        # the refusal stays on record
        self.assertEqual([(h["state"], h["text"], h["retrieved"]) for h in p["history"]], [("kept", TEXT, DAY1)])        # the earlier text, with its day
        self.assertIsNone(tie.page_kept(p))

    def test_no_age_limit_is_invented_and_the_age_is_on_record(self):
        web, store = Web({URL: [(200, HTML), (403, "Forbidden")]}), tie.empty_store()
        pull(store, web, RUN1, DAY1)
        pull(store, web, "20261106T000000Z-test09", "2026-11-06")
        p = store["pages"][URL]
        self.assertEqual((p["state"], p["age_days"], p["retrieved"]), ("kept", 30, DAY1))
        self.assertEqual(pg.days_between("2026-10-07", "2027-10-07"), 365)
        code = src("warehouse", "thesis", "pages.py") + src("warehouse", "thesis", "tie.py")
        for w in ("MAX_AGE", "AGE_LIMIT", "MAX_DAYS", "KEEP_DAYS"):
            self.assertNotIn(w, code, w)

    def test_two_refusals_in_a_row_keep_the_first_days_text(self):
        web, store = Web({URL: [(200, HTML), (403, "Forbidden"), (500, "down")]}), tie.empty_store()
        for run_id, day in ((RUN1, DAY1), (RUN2, DAY2), (RUN3, DAY3)):
            pull(store, web, run_id, day)
        p = store["pages"][URL]
        self.assertEqual((p["state"], p["text"], p["retrieved"], p["retrieved_run"], p["age_days"], p["reason"]), ("kept", TEXT, DAY1, RUN1, 2, "answered 500"))
        self.assertEqual([(r["status"], r["day"]) for r in p["refusals"]], [(403, DAY2), (500, DAY3)])
        self.assertEqual(p["history"], [])


@unittest.skipIf(FIX is None, NO_FIX)
class TheSavedRealCase(unittest.TestCase):
    """renewablesnow.com answered 200 on 7 October 2026 (21:43 UTC) and 403 to the runner on 8 October (10:22 UTC);
    XGS Energy's one tying sentence is on that page, and it left the runner's landscape."""

    def test_the_fixture_is_real_and_says_where_it_is_from(self):
        self.assertIn("runs/session160/make_fixture.py", FIX["note"])
        self.assertIn("Nothing here is written for a test", FIX["note"])
        b, a = FIX["xgs"]["before"], FIX["xgs"]["after"]
        self.assertEqual((b["state"], b["status"], b["fetched"], b["fetched_at"]), ("fetched", 200, "2026-10-07", "2026-10-07T21:43:23Z"))
        self.assertEqual((a["state"], a["status"], a["reason"], a["fetched"], a["fetched_at"], a["text"]), ("refused", 403, "answered 403", "2026-10-08", "2026-10-08T10:22:53Z", ""))
        self.assertEqual(tie.domain(FIX["xgs"]["address"]), "renewablesnow.com")
        self.assertEqual(len(b["saved_text_sha256"]), 64)
        self.assertIn(FIX["xgs"]["sentence"], b["text"])
        self.assertEqual(sorted({x["row"]["name"] for x in FIX["rows"]}), ["Terra AI", "Terra AI, Inc.", "TerraAI (Terra AI)", "Teverra LLC", "XGS Energy"])
        self.assertEqual(FIX["runs"][-1]["run_id"], "20261008T101706Z-605e62")

    def test_before_the_refusal_the_page_tied_it(self):
        c = judge_real(real_store("before", upto=3))["XGS Energy"]
        self.assertEqual((c["trends"], c["tie"]), ([3], 2))
        self.assertEqual((c["ties"][3]["lines"][0]["text"], c["ties"][3]["lines"][0].get("kept")), (FIX["xgs"]["sentence"], None))

    def test_the_refusal_keeps_the_text_of_7_october_and_xgs_energy_stays_tied(self):
        store = real_store("before")
        tally, web = refuse_as_the_runner_did(store)
        p = store["pages"][FIX["xgs"]["address"]]
        self.assertEqual((web.asked, tally["requests"], tally["requested"], tally["copied"]), ([], 0, 0, 1))        # no request: the runner's own record
        self.assertEqual((p["state"], p["text"], p["retrieved"], p["retrieved_at"]), ("kept", FIX["xgs"]["before"]["text"], "2026-10-07", "2026-10-07T21:43:23Z"))
        self.assertEqual({k: p["refusal"][k] for k in ("state", "status", "reason", "day", "at")},
                         {"state": "refused", "status": 403, "reason": "answered 403", "day": "2026-10-08", "at": "2026-10-08T10:22:53Z"})
        self.assertEqual((p["age_days"], list(tally["kept"])), (1, [FIX["xgs"]["address"]]))
        c = judge_real(store)["XGS Energy"]
        self.assertEqual((c["trends"], c["tie"]), ([3], 2))
        line = c["ties"][3]["lines"][0]
        self.assertEqual((line["text"], line["points"], line["tier"]), (FIX["xgs"]["sentence"], 2, "web"))
        self.assertEqual(line["kept"], {"retrieved": "2026-10-07", "refused": "2026-10-08", "status": 403, "reason": "answered 403", "age_days": 1})
        self.assertEqual(judge_real(copy.deepcopy(store), kept=False)["XGS Energy"]["trends"], [])         # as the runner executed it on 8 October

    def test_a_store_written_before_the_ruling_gets_its_text_back_from_its_history(self):
        store = real_store("after")                                 # the record as the runner's code of 8 October left it
        url = FIX["xgs"]["address"]
        self.assertFalse(tie.page_holds(store["pages"][url]))
        self.assertEqual(judge_real(copy.deepcopy(store))["XGS Energy"]["trends"], [])
        history = copy.deepcopy(store["pages"][url]["history"])
        self.assertEqual(pg.restore_kept(store), [url])
        p = store["pages"][url]
        self.assertEqual((p["state"], p["retrieved"], p["retrieved_at"], p["fetched"], p["status"], p["age_days"]), ("kept", "2026-10-07", "2026-10-07T21:43:23Z", "2026-10-08", 403, 1))
        self.assertEqual(p["refusal"]["at"], "2026-10-08T10:22:53Z")
        self.assertEqual(p["history"], history)                     # the history is left as it is
        self.assertEqual(judge_real(store)["XGS Energy"]["trends"], [3])
        self.assertEqual(pg.restore_kept(store), [])                # a store in the new form is unchanged

    def test_the_report_shows_the_day_the_kept_text_was_retrieved(self):
        report, tied, log = report_of(real_store("after"), FIX["niche"], FIX["trends"])          # tied_rows restores the kept page itself
        rows = {c["name"]: c for c in report["landscape"]["companies"]}
        self.assertEqual(rows["XGS Energy"]["reason_kept"], {
            "mark": "retrieved 7 October 2026", "retrieved": "2026-10-07",
            "note": "This sentence is from the page as it was read on 7 October 2026. The page did not give its text when it was asked again on 8 October 2026."})
        self.assertIn("(renewablesnow.com)", rows["XGS Energy"]["reason"])
        self.assertNotIn("reason_kept", rows["Terra AI, Inc."])
        k = tied["kept_pages"]
        self.assertEqual((list(k["pages"]), k["restored_from_history"], k["reasons_shown"], k["age_limit"]), ([FIX["xgs"]["address"]], [FIX["xgs"]["address"]], ["XGS Energy"], None))
        self.assertEqual((k["pages"][FIX["xgs"]["address"]]["retrieved"], k["pages"][FIX["xgs"]["address"]]["age_days"], k["lines"][0]["name"]), ("2026-10-07", 1, "XGS Energy"))
        self.assertTrue(any("kept pages again" in ln for ln in log))

    def test_the_mark_is_short_and_says_nothing_of_the_method(self):
        self.assertEqual(R.KEPT_MARK.format(day=R.day_words("2026-10-07")), "retrieved 7 October 2026")
        self.assertEqual((R.day_words("2026-01-31"), R.day_words("not a day")), ("31 January 2026", "not a day"))
        for w in ("point", "tier", "threshold", "score", "rule", "robots", "TIE_MIN", "403", "status"):
            self.assertNotIn(w, R.KEPT_NOTE, w)
        page = src("site", "components", "thesis", "Report.tsx")
        self.assertIn("<KeptMark v={c?.reason_kept} />", page)
        self.assertIn('data-kept-text="1"', page)
        self.assertIn("reason_kept?: { mark: string; note: string; retrieved?: string }", src("site", "lib", "thesis", "types.ts"))


# ---------------------------------------------------------------------------------------------
# 2. a search result's title is not evidence
# ---------------------------------------------------------------------------------------------

class Titles(unittest.TestCase):
    TITLE = "Heatwell Labs wins a DOE grant for resource field tests"           # written for these tests

    def test_a_title_scores_nothing_and_ties_nothing(self):
        s = store_of([("Heatwell Labs", "heatwell.example", [])], sources={URL: (self.TITLE, [])})
        c = judge_store(copy.deepcopy(s))["Heatwell Labs"]
        self.assertEqual((c["evidence"], c["trends"], c["tie"], c["reason"]), ([], [], 0, None))
        self.assertEqual(c["titles_not_counted"], [{"address": URL, "title": self.TITLE}])          # kept as how the page was found, not counted
        old = judge_store(s, titles=True)["Heatwell Labs"]                                    # as the rule read it until the ruling
        self.assertEqual((old["trends"], old["tie"], [(e["tier"], e["text"]) for e in old["evidence"]], old["titles_not_counted"]), ([3], 3, [("fetched", self.TITLE)], []))

    def test_a_title_that_is_the_companys_own_name_scores_nothing(self):
        for title in ("Heatwell Labs", "Heatwell Labs | DOE grant resource field tests"):
            s = store_of([("Heatwell Labs", "heatwell.example", [])], sources={"https://heatwell.example/": (title, [])})
            c = judge_store(s)["Heatwell Labs"]
            self.assertEqual((c["evidence"], c["trends"]), ([], []), title)
            self.assertEqual([x["title"] for x in c["titles_not_counted"]], [title])

    def test_only_text_counts_a_passage_the_search_tool_returned_and_a_page_that_was_read(self):
        s = store_of([("Heatwell Labs", "heatwell.example", [URL])], pages={URL: TEXT}, sources={URL: (self.TITLE, []), "https://example.org/b": ("A page", [TEXT])})
        c = judge_store(s)["Heatwell Labs"]
        self.assertEqual(sorted((e["tier"], e["address"], e["text"]) for e in c["evidence"]), [("fetched", "https://example.org/b", TEXT), ("web", URL, TEXT)])
        self.assertNotIn(self.TITLE, [e["text"] for e in c["evidence"]])

    def test_the_one_line_that_changed_and_the_default(self):
        code = src("warehouse", "thesis", "tie.py")
        self.assertEqual(code.count('for text in ([title] if titles else []) + list(s.get("cited") or []):'), 1)
        self.assertEqual(code.count('for text in [s.get("title", "")] + list(s.get("cited") or []):'), 0)
        p = inspect.signature(tie.judge).parameters
        self.assertEqual((p["titles"].default, p["kept"].default, p["by_domain"].default, p["proper"].default, p["remarks"].default), (False, True, True, True, True))
        self.assertNotIn("titles=", src("warehouse", "thesis", "run.py"))            # a run never asks for the old reading

    @unittest.skipIf(FIX is None, NO_FIX)
    def test_teverra_llc_entered_by_one_title_and_no_longer_does(self):
        title = FIX["teverra"]["source"]["title"]
        self.assertEqual((title, FIX["teverra"]["source"]["cited"]), ("Teverra secures US DOE grant to develop geothermal geomechanics tool", []))
        old = judge_real(real_store(), titles=True)["Teverra LLC"]
        self.assertEqual((old["trends"], old["tie"]), ([3], 2))
        self.assertEqual([(x["tier"], x["points"], x["text"], x["terms"]) for x in old["ties"][3]["lines"]], [("fetched", 2, title, ["grant", "doe"])])
        now = judge_real(real_store())["Teverra LLC"]
        self.assertEqual((now["trends"], now["tie"], now["evidence"]), ([], 0, []))
        self.assertEqual(now["titles_not_counted"], [{"address": FIX["teverra"]["address"], "title": title}])


# ---------------------------------------------------------------------------------------------
# 3. a vendor page's sentence may tie a company, and is labeled
# ---------------------------------------------------------------------------------------------

class VendorSentence(unittest.TestCase):
    CB = "https://www.cbinsights.com/company/heatwell-labs"
    DR = "https://dealroom.co/companies/heatwell-labs/"
    A = "Heatwell Labs maps blind geothermal systems with AI prospecting."        # written for these tests: two terms of trend 1, not strong
    B = "The AI prospecting of Heatwell Labs finds blind systems under cover."

    def test_two_vendor_sentences_tie_a_company_and_each_is_labeled(self):
        s = store_of([("Heatwell Labs", "heatwell.example", [self.CB, self.DR])], pages={self.CB: TEXT, self.DR: TEXT.replace("Nevada", "Utah, its second award")})
        c = judge_store(s, vendors=VENDORS)["Heatwell Labs"]
        self.assertTrue(c["trends"])
        n = c["trends"][0]
        self.assertTrue(c["ties"][n]["tied"])
        self.assertEqual(sorted(x["vendor"] for x in c["ties"][n]["lines"]), ["CB Insights", "Dealroom"])
        self.assertEqual(c["reason"]["vendor"], "Dealroom")                                   # of two lines of equal points the address first a to z is shown (rule 4, unchanged)
        self.assertTrue(all(e["vendor"] in ("CB Insights", "Dealroom") for e in c["evidence"]))
        plain = judge_store(copy.deepcopy(s))["Heatwell Labs"]                               # the label changes no point
        self.assertEqual((plain["trends"], plain["tie"]), (c["trends"], c["tie"]))

    @unittest.skipIf(FIX is None, NO_FIX)
    def test_terra_ai_is_tied_by_two_vendor_sentences_and_a_press_release(self):
        c = judge_real(real_store())["Terra AI, Inc."]
        self.assertEqual((c["trends"], c["tie"]), ([4], 3))
        self.assertEqual([(tie.domain(x["address"]), x.get("vendor"), x["points"], x["tier"]) for x in c["ties"][4]["lines"]],
                         [("dealroom.co", "Dealroom", 1, "web"), ("sacra.com", "Sacra", 1, "web"), ("prnewswire.com", None, 1, "web")])
        self.assertEqual(c["reason"]["vendor"], "Dealroom")
        s = real_store()
        for u in list(s["pages"]):
            if tie.vendor_of(u, pg.labeled_vendors()):
                del s["pages"][u]
        without = judge_real(s)["Terra AI, Inc."]                   # the press release alone is 1 point, under the tie of 2
        self.assertEqual((without["trends"], without["ties"][4]["score"], without["ties"][4]["tied"]), ([], 1, False))

    @unittest.skipIf(FIX is None, NO_FIX)
    def test_the_label_reaches_the_report_a_user_holds(self):
        report, tied, _ = report_of(real_store("after"), FIX["niche"], FIX["trends"])
        row = {c["name"]: c for c in report["landscape"]["companies"]}["Terra AI, Inc."]
        self.assertEqual(row["reason_vendor"], {"mark": "vendor page", "note": "This sentence is from a public page of a data vendor (Dealroom), not from the company or the press."})
        self.assertIn("(dealroom.co)", row["reason"])
        v = tied["vendor_pages"]
        self.assertEqual((v["reasons_shown"], sorted((x["vendor"], x["tied"]) for x in v["lines"] if x["name"] == "Terra AI, Inc." and x["trend"] == 4)),
                         (["Terra AI, Inc."], [("Dealroom", True), ("Sacra", True)]))


# ---------------------------------------------------------------------------------------------
# 4. one company under several names is merged by domain
# ---------------------------------------------------------------------------------------------

class MergedByDomain(unittest.TestCase):
    def test_two_names_of_one_domain_are_one_company(self):
        c = tie.clusters([("Terra AI", "terraai.com"), ("TerraAI (Terra AI)", "https://www.terraai.com/"), ("Terra Watts Inc.", "")], ["geothermal"])
        self.assertEqual(c["terra ai"], c["terraai"])
        self.assertNotEqual(c["terra watts"], c["terra ai"])
        self.assertEqual(c["terraai"][1], "Terra AI")              # the longest name is kept (rule 5): two words before one
        before = tie.clusters([("Terra AI", "terraai.com"), ("TerraAI (Terra AI)", "https://www.terraai.com/")], ["geothermal"], by_domain=False)
        self.assertNotEqual(before["terra ai"], before["terraai"])

    def test_a_company_with_no_domain_is_never_merged_by_name_likeness(self):
        for a, b in ((("TerraAI", ""), ("Terra AI", "")), (("TerraAI", "terraai.com"), ("Terra AI", "")), (("TerraAI", "not disclosed"), ("Terra AI", "not disclosed"))):
            c = tie.clusters([a, b], ["geothermal"])
            self.assertNotEqual(c["terraai"], c["terra ai"], (a, b))

    def test_a_host_of_many_companies_is_not_a_companys_domain(self):
        cases = {"a social network": ("https://www.linkedin.com/company/alpha-heat", "https://www.linkedin.com/company/beta-steam"),
                 "a social network's bare domain": ("linkedin.com", "linkedin.com"),
                 "a site host": ("alphaheat.github.io", "betasteam.github.io"),
                 "a page on any host": ("https://example.org/companies/alpha", "https://example.org/companies/beta"),
                 "a newswire": ("prnewswire.com", "prnewswire.com"),
                 "a government site": ("energy.gov", "energy.gov")}
        for what, (x, y) in cases.items():
            c = tie.clusters([("Alpha Heat", x), ("Beta Steam", y)], ["geothermal"])
            self.assertNotEqual(c["alpha heat"], c["beta steam"], what)
            self.assertEqual((tie.company_domain(x), tie.company_domain(y)), ("", ""), what)
        # a data vendor's and a licensed database's domain, handed in from the list of rule 7
        shared = set(pg.labeled_vendors())
        for site in ("crunchbase.com", "https://www.cbinsights.com", "app.dealroom.co", "pitchbook.com"):
            self.assertEqual(tie.company_domain(site, shared), "", site)
            c = tie.clusters([("Alpha Heat", site), ("Beta Steam", site)], ["geothermal"], shared)
            self.assertNotEqual(c["alpha heat"], c["beta steam"], site)
        self.assertEqual((tie.company_domain("terraai.com"), tie.company_domain("https://www.terraai.com/"), tie.company_domain("not disclosed"), tie.company_domain("")), ("terraai.com", "terraai.com", "", ""))

    def test_a_news_site_is_shown_to_be_shared_by_the_store_itself(self):
        """A domain at which a row of ANOTHER website cites a page is not a company's own (written for this test)."""
        news = "https://heatnews.example/alpha-and-beta"
        rows = [("Alpha Heat", "heatnews.example", []), ("Beta Steam", "heatnews.example", []), ("Gamma Rock", "gammarock.example", [news])]
        s = store_of(rows)
        self.assertEqual(tie.shared_hosts(s, {"sacra.com": "Sacra"}), {"sacra.com", "heatnews.example"})
        names = {c["name"] for c in tie.judge(s, EMPTY_WH, NICHE, TRENDS)}
        self.assertEqual(names, {"Alpha Heat", "Beta Steam", "Gamma Rock"})
        s2 = store_of(rows[:2] + [("Gamma Rock", "", [news])])       # a row that states no website shows nothing
        self.assertEqual(tie.shared_hosts(s2), set())
        merged = by_name(tie.judge(s2, EMPTY_WH, NICHE, TRENDS))
        self.assertEqual(sorted(merged), ["Alpha Heat", "Gamma Rock"])
        self.assertEqual((merged["Alpha Heat"]["also"], merged["Alpha Heat"]["merged_by_domain"]["domains"]), (["Beta Steam"], ["heatnews.example"]))

    def test_the_evidence_is_pooled_and_the_same_sentence_still_counts_once(self):
        a, b = "https://example.org/a", "https://example.org/b"
        s = store_of([("HeatWell", "heatwell.example", [a]), ("Heat Well Labs", "heatwell.example", [b])],
                     pages={a: "HeatWell maps geothermal heat and holds a DOE grant for resource field tests.", b: "Heat Well Labs won a DOE grant for resource characterization field tests in Nevada."})
        c = judge_store(s)
        self.assertEqual(list(c), ["Heat Well Labs"])
        one = c["Heat Well Labs"]
        self.assertEqual((one["aliases"], one["also"], one["merged_by_domain"]["names"]), (["heat well labs", "heatwell"], ["HeatWell"], ["Heat Well Labs", "HeatWell"]))
        self.assertEqual(sorted({e["address"] for e in one["evidence"]}), [a, b])                 # the evidence of both names
        self.assertEqual(len({(e["address"], e["sha"]) for e in one["evidence"]}), len(one["evidence"]))
        self.assertEqual((one["ties"][3]["score"], len(one["ties"][3]["lines"])), (4, 2))              # two strong web sentences from two addresses: 2 + 2
        apart = judge_store(copy.deepcopy(s), by_domain=False)
        self.assertEqual(sorted(apart), ["Heat Well Labs", "HeatWell"])
        self.assertEqual({n: (x["also"], x["merged_by_domain"]) for n, x in apart.items()}, {"Heat Well Labs": ([], None), "HeatWell": ([], None)})

    def test_which_reading_stands_for_a_merged_company(self):
        def row(seq, key, kind, site="", urls=()):
            return {"key": key, "run_id": f"r{seq}", "seq": seq, "row": {"name": key, "kind": kind, "website": site, "country": "United States", "source_urls": list(urls)}}
        d = ["terraai.com"]
        # (1) the value most rows state
        r = tie.resolve([row(1, "terraai", "private company"), row(2, "terra ai", "other", "terraai.com"), row(3, "terraai", "private company", "terraai.com")], d)
        self.assertEqual((r["kind"], r["read_by"], r["stated_by"]["kind"]["run_id"]), ("private company", {"kind": "rows"}, "r1"))
        self.assertEqual(r["disagreements"], [{"field": "kind", "kept": "private company", "said": "other", "run_id": "r2"}])
        # (2) on a draw, a value stated by a row that itself states the company's domain
        r = tie.resolve([row(1, "terra ai", "other"), row(2, "terraai", "private company", "terraai.com")], d)
        self.assertEqual((r["kind"], r["read_by"]), ("private company", {"kind": "domain"}))
        r = tie.resolve([row(1, "terraai", "private company"), row(2, "terra ai", "other", "terraai.com")], d)
        self.assertEqual((r["kind"], r["read_by"]), ("other", {"kind": "domain"}))
        # (3) on a further draw, the value first stated latest
        r = tie.resolve([row(1, "terra ai", "other", "terraai.com"), row(2, "terraai", "private company", "terraai.com")], d)
        self.assertEqual((r["kind"], r["read_by"]), ("private company", {"kind": "later"}))
        # a company that is not merged by domain: rule 6 as it was, the first value saved stands
        r = tie.resolve([row(1, "terra ai", "other", "terraai.com"), row(2, "terra ai", "private company", "terraai.com"), row(3, "terra ai", "private company", "terraai.com")])
        self.assertEqual((r["kind"], "read_by" in r), ("other", False))
        self.assertEqual(inspect.signature(tie.resolve).parameters["domains"].default, None)

    @unittest.skipIf(FIX is None, NO_FIX)
    def test_terra_ai_under_three_names_is_one_company(self):
        c = judge_real(real_store())
        self.assertEqual(sorted(n for n in c if "erra" in n), ["Terra AI, Inc.", "Teverra LLC"])
        one = c["Terra AI, Inc."]
        self.assertEqual((one["aliases"], one["also"]), (["terra ai", "terraai"], ["Terra AI", "TerraAI (Terra AI)"]))
        self.assertEqual(one["merged_by_domain"], {"domains": ["terraai.com"], "names": ["Terra AI, Inc.", "Terra AI", "TerraAI (Terra AI)"], "apart_by_name": ["terra ai", "terraai"]})
        self.assertEqual((one["row"]["kind"], one["row"]["read_by"]["kind"]), ("private company", "rows"))              # three rows say so, one says "other"
        self.assertIn({"field": "kind", "kept": "private company", "said": "other", "run_id": "20261007T214812Z-2b3411"}, one["row"]["disagreements"])
        apart = judge_real(real_store(), by_domain=False)             # as the runner read it on 8 October: the name first read as "other" is held at "found"
        self.assertEqual((apart["Terra AI, Inc."]["row"]["kind"], apart["TerraAI (Terra AI)"]["row"]["kind"]), ("other", "private company"))
        self.assertEqual(tie.shared_hosts(real_store(), pg.labeled_vendors()) & {"terraai.com"}, set())

    @unittest.skipIf(FIX is None, NO_FIX)
    def test_the_report_holds_one_row_with_the_other_names(self):
        report, tied, _ = report_of(real_store("after"), FIX["niche"], FIX["trends"])
        names = [c["name"] for c in report["landscape"]["companies"]]
        self.assertEqual(names, ["Terra AI, Inc.", "XGS Energy"])            # Teverra LLC is not tied: its one line was a title
        row = report["landscape"]["companies"][0]
        self.assertEqual(row["also"], ["TerraAI (Terra AI)"])       # "Terra AI" differs from the name shown only by its legal form: not repeated
        self.assertNotIn("also", report["landscape"]["companies"][1])
        self.assertEqual([(x["name"], x["domains"], x["kind"]) for x in tied["merged_by_domain"]], [("Terra AI, Inc.", ["terraai.com"], "private company")])
        self.assertEqual([x["name"] for x in tied["titles_not_counted"]["list"] if x["name"] == "Teverra LLC"], ["Teverra LLC"])
        self.assertIn('data-also="1"', src("site", "components", "thesis", "Report.tsx"))

    @unittest.skipIf(FIX is None, NO_FIX)
    def test_the_same_saved_evidence_gives_the_same_result_in_any_order(self):
        want = [(c["name"], c["tie"], c["trends"], c["row"]["kind"]) for c in tie.judge(real_store(), EMPTY_WH, FIX["niche"], FIX["trends"], vendors=pg.labeled_vendors())]
        rnd = random.Random(160)
        for _ in range(5):
            s = real_store()
            rnd.shuffle(s["rows"])
            s["pages"] = dict(rnd.sample(sorted(s["pages"].items()), len(s["pages"])))
            self.assertEqual([(c["name"], c["tie"], c["trends"], c["row"]["kind"]) for c in tie.judge(s, EMPTY_WH, FIX["niche"], FIX["trends"], vendors=pg.labeled_vendors())], want)


# ---------------------------------------------------------------------------------------------
# no point, threshold, tie or tie-break changed
# ---------------------------------------------------------------------------------------------

class NoThresholdChanged(unittest.TestCase):
    def test_the_constants_of_the_scoring(self):
        self.assertEqual(tie.TIERS, {"warehouse": 3, "fetched": 2, "web": 1})
        self.assertEqual(tie.TIER_ORDER, ["warehouse", "fetched", "web"])
        self.assertEqual((tie.STRONG_POINT, tie.STRONG_TERMS, tie.MIN_TERMS, tie.TIE_MIN, tie.MAX_ADDRESSES, tie.PAGE_SENTENCE_MAX), (1, 3, 2, 2, 3, 500))
        self.assertEqual((tie.NEAR_SAME, tie.NEAR_MIN_WORDS, tie.LIST_MIN), (0.90, 8, 3))
        self.assertEqual((R.PIPELINE_MIN, R.PIPELINE_MAX, R.RUN_USD, R.DAY_USD), (60, 10, 1.0, 8.0))      # session 169: the owner lowered RUN_USD to 1.00
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
        self.assertEqual((pg.UA, pg.HEADERS), (UA, {"User-Agent": UA}))
        self.assertEqual((pg.MAX_ADDRESSES_RUN, pg.MAX_ADDRESSES_SESSION, pg.MAX_REQUESTS_RUN, pg.MAX_REQUESTS_SESSION, pg.MAX_BYTES, pg.TIMEOUT, pg.HOST_GAP,
                          pg.MAX_REDIRECTS, pg.MAX_SECONDS_RUN), (150, 450, 450, 1350, 2_000_000, 20, 1.0, 3, 600))
        self.assertEqual((pg.LICENSED_HOSTS, pg.NEVER_HOSTS), (("pitchbook.com", "crunchbase.com", "harmonic.ai"), ("misoenergy.org",)))
        self.assertEqual((pg.KEPT, tie.KEPT), ("kept", "kept"))


class Files(unittest.TestCase):
    PARTS = (("warehouse", "thesis", "tie.py"), ("warehouse", "thesis", "run.py"), ("warehouse", "thesis", "pages.py"), ("tests", "test_session160.py"),
             ("tests", "test_session158.py"), ("tests", "test_session147.py"), ("tests", "test_session142.py"), ("tests", "fixtures", "session160", "rulings.json"),
             ("docs", "methods", "thesis_builder.md"), ("site", "lib", "thesis", "types.ts"), ("site", "components", "thesis", "Report.tsx"),
             ("site", "scripts", "check-thesis.mjs"), ("site", "scripts", "thesis-stub.mjs"))

    def test_no_em_dash_in_the_sessions_files(self):
        for parts in self.PARTS:
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(chr(0x2014), src(*parts), parts)

    def test_thesis_stays_in_review(self):
        self.assertIn('"/thesis": "review"', src("site", "lib", "release.ts"))

    def test_the_rulings_are_not_in_the_published_methods(self):
        for name in os.listdir(os.path.join(ROOT, "docs", "methods")):
            if name.endswith(".md") and name != "thesis_builder.md":          # thesis_builder.md is internal and not built into the site (session 135)
                text = src("docs", "methods", name)
                for w in ("restore_kept", "HOSTS_OF_MANY", "titles_not_counted", "merged by domain"):
                    self.assertNotIn(w, text, (name, w))

    def test_the_internal_method_states_the_rulings(self):
        text = src("docs", "methods", "thesis_builder.md")
        for w in ("session 160", "last good text", "retrieved", "No age limit", "A search result's title is not evidence", "HOSTS_OF_MANY", "also written",
                  "the value stated by the most rows", "vendor page"):
            self.assertIn(w, text, w)

    def test_the_page_draws_both_marks_and_its_check_reads_them(self):
        check, stub = src("site", "scripts", "check-thesis.mjs"), src("site", "scripts", "thesis-stub.mjs")
        for w in ('data-kept-text="1"', 'data-also="1"', "KEPT_MARK", "KEPT_NOTE", "ALSO"):
            self.assertIn(w, check, w)
        self.assertIn('reason_kept: { mark: KEPT_MARK, note: KEPT_NOTE, retrieved: "2026-10-07" }', stub)

    def test_this_module_changes_no_environment_at_import(self):
        code = src("tests", "test_session160.py")
        top = code.split("class KeptText")[0]
        self.assertNotIn("os.environ[", top.split("def setUpModule")[0])
        self.assertIn("def setUpModule", top)
        self.assertIn("def tearDownModule", top)
        self.assertNotIn("origin/" + "main", code)                  # asserts on file contents, never on what a branch changed


if __name__ == "__main__":
    unittest.main()
