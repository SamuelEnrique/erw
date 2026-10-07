"""Session 147: the pages a Thesis Builder run cites are fetched in code and the rule reads their saved sentences.

On saved real pages of the session's own pull (tests/fixtures/session147/pages.json: a few small page texts with
their hashes, cut from the evidence store of the first run of 7 October 2026): the fetcher refuses a paused address
and a disallowed address before any request; a ceiling stops before the request that would pass it; a truncated or
refused page yields no sentence; the same saved pages give the same landscape under shuffles; a quoted sentence that
is not on the saved page gives no point; the bucket store round-trips against a stand-in for the storage API and
falls back to the file; the one header sent is the stated User-Agent. No network, no model call, no database.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import random
import re
import subprocess
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


R = load("erw_thesis_run", "warehouse", "thesis", "run.py")
tie, tb, pg, es = R.tie, R.tb, R.pg, R.es
FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "session147", "pages.json"), encoding="utf-8"))
NICHE, TRENDS = FIX["store"]["niche"], FIX["trends"]
UA = "ERW research project, github.com/SamuelEnrique/erw"
DAY = "2026-10-07"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def judged(store=None, warehouse=None, read="pages"):
    return tie.judge(store if store is not None else copy.deepcopy(FIX["store"]), warehouse if warehouse is not None else FIX["warehouse"], NICHE, TRENDS, read=read)


def by_name(rows):
    return {c["name"]: c for c in rows}


class Web:
    """A stand-in for the one network call: answers from a table, and records every request with its headers."""

    def __init__(self, pages=None, robots=None):
        self.pages, self.robots, self.asked = pages or {}, robots or {}, []

    def __call__(self, url, headers, timeout, max_bytes):
        self.asked.append((url, dict(headers), timeout, max_bytes))
        if url.endswith("/robots.txt"):
            host = url.split("/")[2]
            r = self.robots.get(host, (404, ""))
            return r[0], {"content-type": "text/plain"}, r[1].encode("utf-8"), False
        p = self.pages.get(url)
        if p is None:
            return 404, {"content-type": "text/html"}, b"not here", False
        if isinstance(p, Exception):
            raise p
        status, head, body = p
        body = body if isinstance(body, bytes) else body.encode("utf-8")
        return status, head, body[:max_bytes], len(body) > max_bytes

    def urls(self):
        return [a[0] for a in self.asked]


class Clock:
    def __init__(self):
        self.t, self.slept = 0.0, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def pull(addresses, web, store=None, **k):
    store = store if store is not None else tie.empty_store()
    clock = Clock()
    k.setdefault("paused", {"misoenergy.org", "cdn.misoenergy.org"})
    tally = pg.fetch_run(store, addresses, "run-t", k.pop("day", DAY), get=web, sleep=clock.sleep, clock=clock.now, **k)
    return store, tally, clock


HTML = {"content-type": "text/html; charset=utf-8"}
PAGE = "<html><head><title>T</title><script>var x = 'Zanskar';</script></head><body><nav>Zanskar menu</nav><h1>A headline</h1><p>Some Co maps heat with fiber. It sells data.</p><footer>Zanskar footer</footer></body></html>"


class Refusals(unittest.TestCase):
    """What is never asked for is refused before any request."""

    def test_a_miso_address_is_refused_before_any_request(self):
        web = Web()
        store, tally, _ = pull(["https://www.misoenergy.org/markets-and-operations/", "https://cdn.misoenergy.org/x.pdf", "http://misoenergy.org/"], web)
        self.assertEqual(web.asked, [])                       # not the page, and not its robots.txt
        self.assertEqual((tally["paused"], tally["requests"], tally["requested"]), (3, 0, 0))
        for p in store["pages"].values():
            self.assertEqual((p["state"], p["reason"], p["text"]), ("not fetched", "not fetched: paused", ""))

    def test_miso_is_refused_even_when_the_pause_file_is_gone(self):
        self.assertIn("misoenergy.org", pg.paused_hosts(os.path.join(ROOT, "no", "such", "file.csv")))
        self.assertEqual(pg.never("https://www.misoenergy.org/a", pg.paused_hosts(os.path.join(ROOT, "no", "such", "file.csv"))), "not fetched: paused")
        self.assertIn("cdn.misoenergy.org", pg.paused_hosts())          # the pause file's own outlets are read too

    def test_a_pjm_data_miner_or_api_address_is_refused_before_any_request(self):
        web = Web()
        urls = ["https://dataminer2.pjm.com/feed/da_hrl_lmps", "https://api.pjm.com/api/v1/da_hrl_lmps", "https://www.pjm.com/api/markets"]
        store, tally, _ = pull(urls, web)
        self.assertEqual(web.asked, [])
        self.assertEqual(tally["licensed"], 3)
        self.assertEqual({p["reason"] for p in store["pages"].values()}, {"not fetched: licensed source needed"})

    def test_the_site_of_a_licensed_database_is_refused_before_any_request(self):
        web = Web()
        urls = ["https://pitchbook.com/profiles/company/509380-30", "https://www.crunchbase.com/organization/some-co", "https://console.harmonic.ai/dashboard/company/1"]
        store, tally, _ = pull(urls, web)
        self.assertEqual(web.asked, [])                         # not the page, and not its robots.txt
        self.assertEqual((tally["licensed"], tally["requests"]), (3, 0))
        self.assertEqual({p["reason"] for p in store["pages"].values()}, {"not fetched: licensed source needed"})
        self.assertEqual(pg.never("https://www.pjm.com/about-pjm"), "")             # a plain page of PJM's site is not a Data Miner or API address

    def test_an_address_robots_txt_disallows_for_all_agents_is_not_requested(self):
        web = Web(pages={"https://a.example/private/x": (200, HTML, PAGE), "https://a.example/open/y": (200, HTML, PAGE)},
                  robots={"a.example": (200, "User-agent: *\nDisallow: /private/\n\nUser-agent: OtherBot\nDisallow: /\n")})
        store, tally, _ = pull(["https://a.example/private/x", "https://a.example/open/y"], web)
        self.assertEqual(web.urls(), ["https://a.example/robots.txt", "https://a.example/open/y"])      # robots.txt once; the disallowed page never
        self.assertEqual(store["pages"]["https://a.example/private/x"]["reason"], "not fetched: robots.txt")
        self.assertEqual(store["pages"]["https://a.example/open/y"]["state"], "fetched")
        self.assertEqual((tally["robots_disallowed"], tally["robots_requests"], tally["requested"], tally["requests"]), (1, 1, 1, 2))

    def test_robots_rules_the_longest_match_wins_and_allow_wins_a_draw(self):
        rules, delay = pg.robots_rules("# c\nUser-agent: *\nDisallow: /a/\nAllow: /a/b/\nDisallow: /*.pdf$\nCrawl-delay: 4\n\nUser-agent: X\nDisallow: /\n")
        self.assertEqual(delay, 4.0)
        self.assertFalse(pg.robots_allows(rules, "https://h.example/a/x"))
        self.assertTrue(pg.robots_allows(rules, "https://h.example/a/b/x"))
        self.assertFalse(pg.robots_allows(rules, "https://h.example/files/x.pdf"))
        self.assertTrue(pg.robots_allows(rules, "https://h.example/files/x.pdf?download=1"))
        self.assertTrue(pg.robots_allows(rules, "https://h.example/news"))
        self.assertEqual(pg.robots_rules("User-agent: *\nDisallow:\n")[0], [])                # an empty Disallow allows everything
        self.assertTrue(pg.robots_allows([[False, "/x"], [True, "/x"]], "https://h.example/x"))

    def test_a_robots_txt_that_cannot_be_read_closes_the_host(self):
        for status in (401, 403, 429, 500, 503):
            web = Web(pages={"https://b.example/p": (200, HTML, PAGE)}, robots={"b.example": (status, "")})
            store, tally, _ = pull(["https://b.example/p"], web)
            self.assertEqual(web.urls(), ["https://b.example/robots.txt"], status)
            self.assertTrue(store["pages"]["https://b.example/p"]["reason"].startswith("not fetched: robots.txt could not be read"), status)
        web = Web(pages={"https://b.example/p": (200, HTML, PAGE)})                           # no robots.txt (404): nothing is disallowed
        store, tally, _ = pull(["https://b.example/p"], web)
        self.assertEqual(store["pages"]["https://b.example/p"]["state"], "fetched")

    def test_an_address_that_is_not_a_public_web_page_is_not_requested(self):
        web = Web()
        store, tally, _ = pull(["http://127.0.0.1/x", "http://localhost/x", "https://h.example:8443/x", "ftp://h.example/x", "https://user@h.example/x", "erw:energy_companies/Some Co"], web)
        self.assertEqual(web.asked, [])
        self.assertEqual(tally["cited"], 5)                     # the warehouse's own address is not a web address at all
        self.assertEqual(tally["not_web"], 5)

    def test_a_redirect_is_followed_by_hand_and_never_to_a_login_or_a_paused_host(self):
        web = Web(pages={"http://c.example/a": (301, {"location": "https://c.example/a"}, ""), "https://c.example/a": (200, HTML, PAGE),
                         "https://c.example/b": (302, {"location": "https://c.example/login?next=/b"}, ""),
                         "https://c.example/c": (302, {"location": "https://www.misoenergy.org/c"}, ""),
                         "https://c.example/d": (302, {"location": "https://dataminer2.pjm.com/d"}, "")})
        store, tally, _ = pull(["http://c.example/a", "https://c.example/b", "https://c.example/c", "https://c.example/d"], web)
        p = store["pages"]
        self.assertEqual((p["http://c.example/a"]["state"], p["http://c.example/a"]["final"]), ("fetched", "https://c.example/a"))
        self.assertEqual(p["https://c.example/b"]["reason"], "redirects to a login (302)")
        self.assertIn("not fetched: paused", p["https://c.example/c"]["reason"])
        self.assertIn("licensed source needed", p["https://c.example/d"]["reason"])
        self.assertFalse(any("misoenergy" in u or "pjm.com" in u or "login" in u for u in web.urls()))
        self.assertEqual(tally["hop_requests"], 1)
        self.assertFalse(pg.to_login("https://c.example/news/authentic-heat", "http://c.example/news/authentic-heat"))
        self.assertTrue(pg.to_login("https://login.c.example/x", "https://c.example/y"))


class Ceilings(unittest.TestCase):
    def test_the_ceiling_of_a_run_stops_before_the_request_that_would_pass_it(self):
        urls = [f"https://h{i}.example/p" for i in range(5)]
        web = Web(pages={u: (200, HTML, PAGE) for u in urls})
        store, tally, _ = pull(urls, web, max_run=2)
        self.assertEqual(web.urls(), ["https://h0.example/robots.txt", "https://h0.example/p", "https://h1.example/robots.txt", "https://h1.example/p"])
        self.assertEqual((tally["requested"], tally["fetched"], tally["ceiling"]), (2, 2, 3))
        self.assertEqual(sorted(store["pages"]), urls[:2])        # an address left by the ceiling has no record: a later run asks for it
        self.assertIn("ceiling of addresses", tally["stopped"])

    def test_the_ceiling_of_a_session_is_kept_across_runs_in_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "count.json")
            urls = [f"https://h{i}.example/p" for i in range(6)]
            web = Web(pages={u: (200, HTML, PAGE) for u in urls})
            pull(urls[:3], web, count=pg.Count(path), max_session=4)
            self.assertEqual(json.load(open(path))["addresses"], 3)
            store, tally, _ = pull(urls[3:], web, count=pg.Count(path), max_session=4)
            self.assertEqual((tally["requested"], tally["ceiling"]), (1, 2))
            self.assertEqual(json.load(open(path))["addresses"], 4)
            self.assertNotIn("https://h4.example/p", web.urls())

    def test_the_ceiling_of_requests_counts_robots_txt_and_hops(self):
        urls = [f"https://h{i}.example/p" for i in range(4)]
        web = Web(pages={u: (200, HTML, PAGE) for u in urls})
        store, tally, _ = pull(urls, web, max_requests_run=3)
        self.assertEqual(len(web.asked), 3)
        self.assertEqual(tally["requests"], 3)

    def test_a_page_the_session_already_holds_is_copied_and_not_asked_of_its_publisher_again(self):
        urls = ["https://h.example/p", "https://h.example/q", "https://other.example/r"]
        web = Web(pages={u: (200, HTML, PAGE) for u in urls})
        shelf, _, _ = pull(urls[:2], web)                          # a store of this session, fetched today
        asked = len(web.asked)
        store, tally, _ = pull([urls[0], urls[2]], web, shelf=shelf)            # a replay through a store of its own
        self.assertEqual((tally["copied"], tally["requested"]), (1, 1))
        self.assertEqual(web.urls()[asked:], ["https://other.example/robots.txt", urls[2]])
        self.assertEqual(sorted(store["pages"]), [urls[0], urls[2]])           # only what this run asked for: nothing else of the shelf comes along
        self.assertEqual(store["pages"][urls[0]]["text_sha256"], shelf["pages"][urls[0]]["text_sha256"])
        self.assertEqual(store["pages"][urls[0]]["copied_from_run"], "run-t")
        store, tally, _ = pull([urls[1]], web, shelf=shelf, max_run=0)          # with the ceiling at nought no request can be made at all
        self.assertEqual((tally["copied"], tally["requests"]), (1, 0))
        store, tally, _ = pull([urls[0]], web, shelf=shelf, day="2026-10-08")   # a shelf from an earlier day is not used
        self.assertEqual((tally["copied"], tally["requested"]), (0, 1))

    def test_the_pull_of_a_run_stops_asking_after_its_ten_minutes(self):
        urls = [f"https://slow.example/p{i}" for i in range(6)]
        web = Web(pages={u: (200, HTML, PAGE) for u in urls}, robots={"slow.example": (200, "User-agent: *\nCrawl-delay: 30\n")})
        store, tally, clock = pull(urls, web, max_seconds=70)       # each page waits the host's 30 seconds: the third request starts at 60, the fourth would start at 90
        self.assertEqual(len(web.asked), 4)                          # robots.txt and three pages
        self.assertIn("ceiling of time", tally["stopped"])
        self.assertEqual((tally["fetched"], tally["ceiling"]), (3, 3))
        self.assertEqual(pg.MAX_SECONDS_RUN, 600)

    def test_the_ceilings_are_the_owners(self):
        self.assertEqual((pg.MAX_ADDRESSES_RUN, pg.MAX_ADDRESSES_SESSION, pg.MAX_BYTES, pg.TIMEOUT, pg.HOST_GAP), (150, 450, 2_000_000, 20, 1.0))
        web = Web(pages={"https://h.example/p": (200, HTML, PAGE)})
        pull(["https://h.example/p"], web)
        self.assertTrue(all((t, m) == (20, 2_000_000) for _, _, t, m in web.asked))

    def test_one_host_is_asked_at_most_once_a_second_and_its_robots_txt_once(self):
        urls = [f"https://one.example/p{i}" for i in range(3)]
        web = Web(pages={u: (200, HTML, PAGE) for u in urls})
        store, tally, clock = pull(urls, web)
        self.assertEqual(web.urls().count("https://one.example/robots.txt"), 1)
        self.assertEqual(clock.slept, [1.0, 1.0, 1.0])            # before each of the three pages, after the request before it
        web = Web(pages={u: (200, HTML, PAGE) for u in urls}, robots={"one.example": (200, "User-agent: *\nCrawl-delay: 5\n")})
        store, tally, clock = pull(urls, web)
        self.assertEqual(clock.slept, [5.0, 5.0, 5.0])            # the host's own crawl delay, when it asks for a longer one

    def test_an_address_is_requested_once_a_run_and_not_again_the_same_day(self):
        u = "https://h.example/p"
        web = Web(pages={u: (200, HTML, PAGE)})
        store, tally, _ = pull([u, u, u], web)
        self.assertEqual(web.urls().count(u), 1)
        store, tally, _ = pull([u], web, store=store)             # a second run, the same day
        self.assertEqual((web.urls().count(u), tally["held"], tally["requests"]), (1, 1, 0))

    def test_a_later_day_asks_again_and_a_changed_page_is_kept_beside_the_first(self):
        u = "https://h.example/p"
        web = Web(pages={u: (200, HTML, PAGE)})
        store, _, _ = pull([u], web)
        first = store["pages"][u]["text_sha256"]
        web.pages[u] = (200, HTML, PAGE.replace("fiber", "radar"))
        store, tally, _ = pull([u], web, store=store, day="2026-10-08")
        p = store["pages"][u]
        self.assertEqual(tally["changed"], [u])
        self.assertEqual((p["fetched"], p["first_fetched"]), ("2026-10-08", DAY))
        self.assertNotEqual(p["text_sha256"], first)
        self.assertEqual([(h["fetched"], h["text_sha256"]) for h in p["history"]], [(DAY, first)])
        self.assertIn("fiber", p["history"][0]["text"])
        store, tally, _ = pull([u], web, store=store, day="2026-10-09")          # asked again, unchanged: nothing is added to its history
        self.assertEqual((len(store["pages"][u]["history"]), tally["changed"]), (1, []))


class Pages(unittest.TestCase):
    """What a page holds: its text with its hashes, or nothing."""

    def test_a_fetched_page_is_saved_with_its_hashes_status_bytes_and_day(self):
        u = "https://h.example/p"
        store, tally, _ = pull([u], Web(pages={u: (200, HTML, PAGE)}))
        p = store["pages"][u]
        self.assertEqual((p["state"], p["status"], p["fetched"], p["bytes"], p["truncated"]), ("fetched", 200, DAY, len(PAGE.encode()), False))
        self.assertEqual(p["sha256"], hashlib.sha256(PAGE.encode()).hexdigest())
        self.assertEqual(p["text_sha256"], hashlib.sha256(p["text"].encode("utf-8")).hexdigest())
        self.assertEqual(p["text"], "A headline\nSome Co maps heat with fiber. It sells data.")     # no script, menu, footer or title
        self.assertEqual(tie.page_sentences(p["text"]), ["Some Co maps heat with fiber.", "It sells data."])

    def test_a_truncated_page_holds_no_sentence(self):
        u = "https://h.example/big"
        body = "<html><body><p>Zanskar Geothermal uses AI geothermal exploration.</p>" + "x" * 3000 + "</body></html>"
        store, tally, _ = pull([u], Web(pages={u: (200, HTML, body)}), max_bytes=1000)
        p = store["pages"][u]
        self.assertEqual((p["state"], p["truncated"], p["text"], p["bytes"], tally["truncated"]), ("truncated", True, "", 1000, 1))
        self.assertFalse(tie.page_holds(p))

    def test_a_refused_page_holds_no_sentence(self):
        cases = {"https://h.example/403": (403, HTML, "<html><body><p>Zanskar Geothermal uses AI geothermal exploration.</p></body></html>"),
                 "https://h.example/img": (200, {"content-type": "image/png"}, b"\x89PNG"), "https://h.example/empty": (200, HTML, "<html><body><script>x</script></body></html>"),
                 "https://h.example/down": TimeoutError("no answer")}
        store, tally, _ = pull(list(cases), Web(pages=cases))
        for u in cases:
            self.assertEqual((store["pages"][u]["text"], tie.page_holds(store["pages"][u])), ("", False), u)
        self.assertEqual(store["pages"]["https://h.example/403"]["reason"], "answered 403")
        self.assertEqual(store["pages"]["https://h.example/img"]["reason"], "answered 200 without text (image/png)")
        self.assertTrue(store["pages"]["https://h.example/down"]["reason"].startswith("no answer: TimeoutError"))
        self.assertEqual((tally["refused"], tally["not_text"], tally["empty"], tally["failed"], tally["fetched"]), ({"403": 1}, 1, 1, 1, 0))

    def test_a_page_that_holds_no_sentence_gives_the_rule_nothing(self):
        store = copy.deepcopy(FIX["store"])
        base = by_name(judged(store))
        name, c = next((n, c) for n, c in sorted(base.items()) if any(e["tier"] == "web" for e in c["evidence"]))
        for url in {e["address"] for e in c["evidence"] if e["tier"] == "web"}:
            for change in ({"truncated": True, "state": "truncated"}, {"state": "refused", "status": 403, "reason": "answered 403"}, {"state": "not fetched", "reason": "not fetched: robots.txt"}):
                s = copy.deepcopy(store)
                s["pages"][url].update(change)                       # the text is still there: the state alone must silence it
                after = by_name(judged(s))[name]
                self.assertFalse(any(e["tier"] == "web" and e["address"] == url for e in after["evidence"]), (url, change))

    def test_the_fixtures_pages_are_real_and_hash_to_what_was_saved(self):
        pages = FIX["store"]["pages"]
        self.assertGreaterEqual(sum(1 for p in pages.values() if tie.page_holds(p)), 3)
        for url, p in pages.items():
            if p.get("text"):
                self.assertEqual(hashlib.sha256(p["text"].encode("utf-8")).hexdigest(), p["text_sha256"], url)
            self.assertEqual(p["fetched"], DAY, url)
            self.assertRegex(p.get("sha256") or "0" * 64, r"^[0-9a-f]{64}$")
        self.assertTrue(any(not tie.page_holds(p) for p in pages.values()), "the fixture keeps a page that was not fetched")

    def test_a_long_run_without_a_sentence_end_is_not_a_sentence(self):
        menu = " ".join(["Zanskar AI exploration"] * 40)
        self.assertGreater(len(menu), tie.PAGE_SENTENCE_MAX)
        self.assertEqual(tie.page_sentences(menu + "\nZanskar Geothermal uses AI geothermal exploration."), ["Zanskar Geothermal uses AI geothermal exploration."])
        self.assertEqual(tie.PAGE_SENTENCE_MAX, 500)

    def test_a_pdf_is_read_a_page_at_a_time(self):
        code = src("warehouse", "thesis", "pages.py")
        part = code.split("def pdf_text(")[1].split("\ndef ")[0]
        self.assertIn("pdfplumber", part)
        self.assertIn("for page in pdf.pages", part)
        self.assertIn("pdfplumber", src("requirements.txt"))


class Rule(unittest.TestCase):
    """The web tier reads the saved pages; the model's quotations decide nothing; the thresholds are as built."""

    def test_the_thresholds_the_points_and_the_tie_are_as_session_142_built_them(self):
        self.assertEqual(tie.TIERS, {"warehouse": 3, "fetched": 2, "web": 1})
        self.assertEqual(tie.TIER_ORDER, ["warehouse", "fetched", "web"])
        self.assertEqual((tie.MIN_TERMS, tie.STRONG_TERMS, tie.STRONG_POINT, tie.TIE_MIN, tie.MAX_ADDRESSES), (2, 3, 1, 2, 3))
        self.assertEqual((R.PIPELINE_MIN, R.PIPELINE_MAX), (60, 10))

    def test_the_same_saved_pages_give_the_same_landscape_twice_and_under_shuffles(self):
        one = judged()
        self.assertEqual(json.dumps(one, sort_keys=True), json.dumps(judged(), sort_keys=True))
        base = [(c["name"], c["trends"], c["tie"], c["tier"]) for c in one]
        self.assertTrue(any(c["trends"] and c["tier"] == "web" for c in one), "the fixture ties no company by a saved page")
        for seed in range(6):
            s = copy.deepcopy(FIX["store"])
            rnd = random.Random(seed)
            rnd.shuffle(s["quotes"])
            rnd.shuffle(s["rows"])
            s["sources"] = dict(rnd.sample(sorted(s["sources"].items()), len(s["sources"])))
            s["pages"] = dict(rnd.sample(sorted(s["pages"].items()), len(s["pages"])))
            wh = {k: rnd.sample(v, len(v)) for k, v in FIX["warehouse"].items()}
            self.assertEqual([(c["name"], c["trends"], c["tie"], c["tier"]) for c in judged(s, wh)], base, seed)

    def test_every_web_line_is_a_sentence_of_a_saved_page_that_names_the_company(self):
        niche_words = ["geothermal", "mapping", "sensing"]
        n = 0
        for c in judged():
            aliases = sorted({(k, tie.core_of(k, niche_words)) for k in c["aliases"]})
            for e in c["evidence"]:
                if e["tier"] != "web":
                    continue
                n += 1
                page = FIX["store"]["pages"][e["address"]]
                self.assertTrue(tie.page_holds(page))
                self.assertIn(e["text"], tie.page_sentences(page["text"]))
                self.assertTrue(tie.names_it(e["text"], aliases, niche_words), (c["name"], e["text"]))
                self.assertEqual(e["fetched"], page["fetched"])
        self.assertGreater(n, 0)

    def test_a_quoted_sentence_that_is_not_on_the_saved_page_gives_no_point(self):
        store = copy.deepcopy(FIX["store"])
        base = by_name(judged(store))
        target = next(c for _, c in sorted(base.items()) if not c["trends"])
        url = next(u for u, p in sorted(store["pages"].items()) if tie.page_holds(p))
        quote = "TEST SENTENCE, NOT A SOURCE: a distributed acoustic sensing array on optic fiber for monitoring."
        store["quotes"].append({"key": target["aliases"][0], "address": url, "fetched": DAY, "first_run": "t", "sha": tie.sha(quote), "text": quote})
        after = by_name(judged(store))[target["name"]]
        self.assertEqual((after["trends"], after["tie"]), ([], 0))                                 # a strong sentence, by the old reading 2 points: now nothing
        self.assertEqual(json.dumps(after["evidence"], sort_keys=True), json.dumps(target["evidence"], sort_keys=True))
        check = next(q for q in tie.quote_check(store) if q["sha"] == tie.sha(quote))
        self.assertEqual((check["page"], check["found"]), ("held", False))
        old = by_name(judged(store, read="quotes"))[target["name"]]                               # session 142's reading, kept for comparison, would have tied it
        self.assertEqual(old["trends"], [2])

    def test_a_quoted_sentence_that_is_on_the_saved_page_is_simply_one_of_its_sentences(self):
        store = copy.deepcopy(FIX["store"])
        base = by_name(judged(store))
        c = next(c for _, c in sorted(base.items()) if any(e["tier"] == "web" for e in c["evidence"]))
        e = next(e for e in c["evidence"] if e["tier"] == "web")
        store["quotes"] = [{"key": c["aliases"][0], "address": e["address"], "fetched": DAY, "first_run": "t", "sha": tie.sha(e["text"]), "text": e["text"]}]
        with_quote = by_name(judged(store))[c["name"]]
        store["quotes"] = []
        without = by_name(judged(store))[c["name"]]
        self.assertEqual(json.dumps(with_quote, sort_keys=True), json.dumps(without, sort_keys=True))      # the quotation adds nothing and removes nothing
        store["quotes"] = [{"key": c["aliases"][0], "address": e["address"], "fetched": DAY, "first_run": "t", "sha": tie.sha(e["text"]), "text": e["text"]}]
        self.assertEqual([(q["page"], q["found"]) for q in tie.quote_check(store)], [("held", True)])

    def test_a_quotation_from_a_page_that_was_not_fetched_is_on_record_as_such(self):
        store = copy.deepcopy(FIX["store"])
        url = next(u for u, p in sorted(store["pages"].items()) if not tie.page_holds(p))
        store["quotes"] = [{"key": "x", "address": url, "fetched": DAY, "first_run": "t", "sha": "aa", "text": "A sentence the research reported."},
                           {"key": "x", "address": "https://never.example/asked", "fetched": DAY, "first_run": "t", "sha": "bb", "text": "Another sentence it reported."}]
        self.assertEqual([(q["page"], q["found"]) for q in tie.quote_check(store)], [("never asked for", False), ("not held", False)])

    def test_a_store_written_before_the_pages_reads_as_one_with_none(self):
        old = {"version": 1, "niche": NICHE, "stage": "startups", "geography": "United States", "runs": [], "sources": {}, "quotes": [], "rows": [], "last": None}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.json")
            json.dump(old, open(path, "w", encoding="utf-8"))
            self.assertEqual((tie.load_store(path)["pages"], tie.load_store(path)["robots"]), ({}, {}))
            self.assertEqual(es.FileStore(path).load()["pages"], {})
        self.assertEqual(judged(old), [])

    def test_the_rule_still_makes_no_call_and_reaches_no_network(self):
        rule = src("warehouse", "thesis", "tie.py").split('"""', 2)[2]
        for w in ("anthropic", "llm", "requests", "urllib", "client", "import iso_prices", "pandas", "socket", "http.client", "subprocess"):
            self.assertNotIn(w, rule, w)
        for name in ("pages.py", "store.py"):
            code = src("warehouse", "thesis", name)
            for w in ("anthropic", "import llm", "messages.create", "connectors", "PITCHBOOK_API_KEY", "mcp"):
                self.assertNotIn(w, code, (name, w))
        self.assertIn("pitchbook.com", pg.LICENSED_HOSTS)          # the fetcher's one word about PitchBook: its site is never asked for a page
        code = src("warehouse", "thesis", "run.py")
        body = code.split("def execute(")[1].split("\ndef ")[0]
        self.assertEqual(body.count("r.guard("), 7)                 # the stop still stands before each of the seven paid stages
        self.assertEqual(body.count("r.research(") + body.count("r.structure(") + body.count("r.structure_groups("), 7)
        for fn in ("def tied_rows(", "def tie_done(", "def cited_addresses("):
            part = code.split(fn)[1].split("\ndef ")[0]
            for w in ("r.research(", "r.structure(", "r.client", "messages.create"):
                self.assertNotIn(w, part, (fn, w))


class ByHand(unittest.TestCase):
    """The scoring redone by hand from the saved pages. Each case: the company, the trend, and for every line that
    counts its tier, its address, the terms a reader finds in the sentence, its phrase, and its points; then the sum."""

    BIZWEST = "https://bizwest.com/2024/02/06/innosphere-ventures-selects-2024-cleantech-cohort/"
    VENTUREWELL = "https://venturewell.org/rose-rock-ascend-2024/"
    HTX = "https://energycapitalhtx.com/fervo-quaise-xgs-geothermaldoe-funding"
    QUAISE = "https://www.quaise.com/news/quaise-energy-selected-for-up-to-25-million-in-u-s-department-of-energy-support-to-advance-worlds-first-commercial-superhot-geothermal-power-plant"
    RENEWABLESNOW = "https://renewablesnow.com/news/xgs-tapped-for-doe-funding-for-geothermal-drilling-project-in-new-mexico-1302041/"
    CASES = [
        # Zanskar, trend 1: the warehouse's own row (3) holding a whole phrase (+1), and two fetched titles (2 each), each holding a whole phrase (+1). No page is needed
        ("Zanskar Geothermal & Minerals", 1, [
            ("warehouse", "erw:energy_companies/Zanskar Geothermal & Minerals", ["ai", "exploration"], "AI geothermal exploration", 4),
            ("fetched", "https://baytobaynews.com/daily-state-news/stories/zanskar-reveals-big-blind-the-discovery-of-the-first-blind-geothermal-system-in-the-us-by,275569",
             ["blind", "discovery"], "blind geothermal discovery", 3),
            ("fetched", "https://energynews.pro/en/zanskar-raises-115m-to-accelerate-ai-powered-geothermal-exploration-in-the-united-states", ["ai", "exploration"], "AI geothermal exploration", 3)], 10, True),
        # Thermofilic, trend 4: one sentence on each of two saved pages (1 each), each strong by three terms (+1): 2 + 2
        ("Thermofilic", 4, [("web", BIZWEST, ["prediction", "investment", "decision"], "", 2), ("web", VENTUREWELL, ["prediction", "investment", "decision"], "", 2)], 4, True),
        # Geothermal Radar, trend 4: one sentence of one saved page (1), strong by three terms and a whole phrase (+1)
        ("Geothermal Radar", 4, [("web", VENTUREWELL, ["modeling", "assessment", "digital"], "geothermal digital modeling", 2)], 2, True),
        # XGS Energy, trend 3: the page draws its article with JavaScript; the sentence is the page's own description, in its head (1), strong by four terms and a whole phrase (+1)
        ("XGS Energy", 3, [("web", RENEWABLESNOW, ["grant", "doe", "field", "test"], "DOE geothermal field tests", 2)], 2, True),
        # Quaise Energy, trend 3: one quotation of its chief executive, printed on two pages with two different endings: two sentences of two terms (1 each)
        ("Quaise Energy", 3, [("web", HTX, ["doe", "field"], "", 1), ("web", QUAISE, ["doe", "field"], "", 1)], 2, True),
        # Bedrock Energy: no sentence of a saved page holds two terms of a trend, and the warehouse's row holds one ("subsurface modeling")
        ("Bedrock Energy", 4, [], 0, False),
        ("Mazama Energy", 3, [], 0, False),
    ]

    def test_each_case(self):
        rows = by_name(judged())
        for name, trend, lines, score, tied in self.CASES:
            t = rows[name]["ties"][trend]
            got = [(x["tier"], x["address"], x["terms"], x["phrase"], x["points"]) for x in t["lines"]]
            self.assertEqual(got, lines, (name, trend))
            self.assertEqual((t["score"], t["tied"]), (score, tied), (name, trend))
            for tier, address, terms, phrase, points in lines:
                self.assertEqual(points, tie.TIERS[tier] + (1 if phrase or len(terms) >= 3 else 0))
                sentence = next(x["text"] for x in t["lines"] if x["address"] == address)
                have = set(tie.tokens(sentence))
                self.assertTrue(all(w in have for w in terms), (name, terms, sentence))
                if tier == "web":
                    self.assertIn(sentence, tie.page_sentences(FIX["store"]["pages"][address]["text"]), (name, address))

    def test_the_landscape_of_the_fixture_in_the_rules_order(self):
        self.assertEqual([c["name"] for c in judged() if c["trends"]], ["Zanskar Geothermal & Minerals", "Thermofilic", "Geothermal Radar", "Quaise Energy", "XGS Energy"])

    def test_the_xgs_sentence_is_on_its_page_only_in_what_the_page_says_of_itself(self):
        """The quotation session 142's third run turned on. The research quoted it in every run; a plain GET of the page
        shows menus and headlines, and the sentence stands in the page's description, which the fetcher reads."""
        store = copy.deepcopy(FIX["store"])
        q = [q for q in store["quotes"] if q["address"] == self.RENEWABLESNOW]
        self.assertEqual(len(q), 1)
        self.assertTrue(q[0]["text"].startswith("US geothermal technology company XGS Energy Inc has been selected by the Department of Energy (DOE)"))
        self.assertEqual([(c["page"], c["found"]) for c in tie.quote_check(store) if c["address"] == self.RENEWABLESNOW], [("held", True)])
        self.assertEqual(store["pages"][self.RENEWABLESNOW]["extractor"], pg.EXTRACTOR)
        html_page = ('<html><head><meta name="description" content="X Co Inc was selected for a federal grant."/>'
                     '<script type="application/ld+json">{"@type":"NewsArticle","headline":"X Co tapped","articleBody":"<p>X Co Inc was selected &amp; funded.</p> <p>It drills wells.</p>"}</script>'
                     '<script>var hidden = "never read";</script></head><body><div>Menu one</div></body></html>')
        self.assertEqual(pg.html_text(html_page), "X Co Inc was selected for a federal grant.\nX Co tapped\nX Co Inc was selected & funded.\nIt drills wells.\nMenu one")

    def test_one_quotation_printed_with_two_endings_counts_as_two_sentences_as_the_rule_was_built(self):
        """Flagged for the owner, not changed: the rule counts the same sentence on two addresses once, by its exact
        words; a press release printed twice with different attributions is two sentences to it."""
        c = by_name(judged())["Quaise Energy"]
        a, b = [x["text"] for x in c["ties"][3]["lines"]]
        self.assertNotEqual(tie.sha(a), tie.sha(b))
        self.assertEqual(a[:150], b[:150])

    def test_a_name_made_of_the_niches_own_words_is_named_by_running_text_as_the_rule_was_built(self):
        """Flagged for the owner, not changed: the third run of 7 October 2026 put "Geothermal Technologies
        (geothermal.tech)" on the landscape by two sentences about geothermal technologies in general. The name
        matching is session 142's, untouched: a whole name of two words is matched wherever those words stand."""
        niche_words = ["geothermal", "mapping", "sensing"]
        key = tie.name_key("Geothermal Technologies (geothermal.tech)")
        self.assertEqual(key, "geothermal technologies")
        aliases = [(key, tie.core_of(key, niche_words))]
        self.assertEqual(aliases, [("geothermal technologies", "geothermal technologies")])
        self.assertTrue(tie.names_it("Department of Energy to advance geothermal technologies and field tests.", aliases, niche_words))
        self.assertTrue(tie.names_it("The DOE Geothermal Technologies Office has been the major funder of geothermal innovation.", aliases, niche_words))


class RunPath(unittest.TestCase):
    """The run's own code after the model's calls, with the pull switched on and a stand-in for the network."""

    class Saved:
        def __init__(self):
            self.sources, self.erw = {}, []

        source = tb.Researcher.source
        texts_of = tb.Researcher.texts_of

    def run_once(self, store_path, web, fetch=True, land=None):
        r = self.Saved()
        for url, s in FIX["store"]["sources"].items():
            r.source(url, s["title"], s.get("page_age", ""))
        ids = {s["url"]: s["id"] for s in r.sources.values()}
        orgs = []
        for x in FIX["store"]["rows"]:
            o = dict(x["row"], independent_sources=1, tam="")
            o["sources"] = [ids[u] for u in x["row"]["source_urls"] if u in ids]
            o["evidence"] = [{"quote": q["text"], "source": ids[q["address"]]} for q in FIX["store"]["quotes"] if q["key"] == x["key"] and q["address"] in ids]
            orgs.append(o)
        land = land or {"fact": "", "fact_sources": [], "organisations": orgs}
        a = {"scope": {"definition": "", "definition_sources": [], "value_chain": [], "excluded": [], "definitions": []},
             "trends": [dict(t, fact="", table={"columns": [], "rows": []}, chart={"kind": "none", "title": "", "category_column": 0, "value_columns": []}, unit="", sources=[]) for t in TRENDS]}
        log, real = [], R.warehouse_rows
        R.warehouse_rows = lambda: FIX["warehouse"]
        clock = Clock()
        try:
            rows, ctx = R.tied_rows(r, "20261007T220000Z-test01", NICHE, FIX["store"]["stage"], FIX["store"]["geography"], TRENDS, land, store_path, log.append,
                                    fetch={"get": web, "sleep": clock.sleep, "clock": clock.now, "paused": {"misoenergy.org"}} if fetch else None)
            report, placed = R.build_report(NICHE, FIX["store"]["stage"], FIX["store"]["geography"], r, a, dict(land, organisations=rows), {}, None, R.query_plan(NICHE, "United States", TRENDS), log.append)
            tied = R.tie_done(ctx, placed, log.append)
        finally:
            R.warehouse_rows = real
        return report, placed, tied, log

    def web(self):
        """The fixture's own saved pages, served back as HTML: one paragraph a saved line."""
        pages = {}
        for url, p in FIX["store"]["pages"].items():
            if tie.page_holds(p):
                import html
                pages[url] = (200, HTML, "<html><body>" + "".join(f"<p>{html.escape(line)}</p>" for line in p["text"].split("\n")) + "</body></html>")
            elif p.get("status"):
                pages[url] = (p["status"], HTML, "refused")
        return Web(pages=pages)

    def test_a_run_asks_for_every_address_its_rows_cite_and_the_landscape_is_the_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "e", "s.json")
            web = self.web()
            report, placed, tied, log = self.run_once(path, web)
            cited = {u for x in FIX["store"]["rows"] for u in x["row"]["source_urls"] if u.startswith("http")} | {q["address"] for q in FIX["store"]["quotes"]}
            asked = {u for u in web.urls() if not u.endswith("/robots.txt")}
            self.assertTrue(asked <= cited)
            self.assertEqual(tied["pull"]["cited"], len(cited))
            self.assertEqual(tied["pull"]["user_agent"], UA)
            self.assertEqual(tied["store_kind"], "file")
            saved = json.load(open(path, encoding="utf-8"))
            self.assertEqual(saved["version"], 2)
            self.assertEqual(set(saved["pages"]), cited)                                  # every cited address has its record, fetched or not; no other page is asked for
            for url, p in FIX["store"]["pages"].items():
                if tie.page_holds(p) and url in cited:
                    self.assertEqual(saved["pages"][url]["text"], p["text"], url)          # the page read back is the page saved
                    self.assertEqual(saved["pages"][url]["text_sha256"], p["text_sha256"], url)
            want = [c["name"] for c in judged() if c["trends"]]
            on = [o["name"] for o in sorted(placed, key=R.rank) if o["reached"] in ("trend", "pipeline")]
            self.assertEqual(on, [n for n in want if n in on])
            self.assertTrue(on)
            again, _, tied2, _ = self.run_once(path, web)                                 # the same day: nothing is asked for again, and the landscape is the same
            self.assertEqual(tied2["pull"]["requests"], 0)
            self.assertEqual([c["name"] for c in again["landscape"]["companies"]], [c["name"] for c in report["landscape"]["companies"]])
            self.assertEqual([c["name"] for c in again["pipeline"]["companies"]], [c["name"] for c in report["pipeline"]["companies"]])

    def test_a_run_that_asks_for_no_page_reads_what_the_store_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.json")
            json.dump(FIX["store"], open(path, "w", encoding="utf-8"))
            report, placed, tied, log = self.run_once(path, None, fetch=False)
            self.assertIsNone(tied["pull"])
            self.assertTrue(report["landscape"]["companies"])

    def test_a_pull_that_fails_never_costs_the_run_its_answers(self):
        def broken(*a, **k):
            raise RuntimeError("the fetcher itself broke")
        real = pg.fetch_run
        pg.fetch_run = broken
        try:
            with tempfile.TemporaryDirectory() as tmp:
                report, placed, tied, log = self.run_once(os.path.join(tmp, "s.json"), Web())
        finally:
            pg.fetch_run = real
        self.assertIn("the fetcher itself broke", tied["pull"]["error"])
        self.assertTrue(any("THE PULL FAILED" in s for s in log))
        self.assertTrue(report["funnel"]["companies"])

    def test_why_a_company_is_here_is_a_sentence_of_a_saved_page_or_of_the_warehouse(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, placed, tied, log = self.run_once(os.path.join(tmp, "s.json"), self.web())
        texts = {R.clean(e["text"].strip().rstrip(".")) for c in judged() for e in c["evidence"]}
        self.assertTrue(report["landscape"]["companies"])
        for c in report["landscape"]["companies"]:
            m = re.match(r'^"(.*)" \((.+)\)', c["reason"])
            self.assertIsNotNone(m, c["reason"])
            self.assertIn(m.group(1), texts, c["reason"])

    def test_the_report_holds_none_of_the_rules_or_the_pulls_mechanics(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, placed, tied, log = self.run_once(os.path.join(tmp, "s.json"), self.web())

        def strings(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    yield k
                    yield from strings(v)
            elif isinstance(x, list):
                for v in x:
                    yield from strings(v)
            elif isinstance(x, str):
                yield x
        own = [e["text"] for c in judged() for e in c["evidence"]]
        for s in strings(report):
            if any(s.strip('"') in t or t in s for t in own):
                continue                                       # a source's own words may hold any word
            for w in ("robots.txt", "user-agent", "sha256", "evidence store", "storage bucket", "erw-thesis", "points", "threshold", "tie-break", "not fetched", "truncated"):
                self.assertNotIn(w, s.lower(), (w, s[:120]))
        for k in ("pull", "pages", "quotes", "quote_checks", "robots", "text_sha256", "store_kind"):
            self.assertNotIn(k, set(strings(report)), k)

    def test_the_addresses_asked_for_are_the_runs_own_then_the_stores(self):
        orgs = [{"source_urls": ["https://b.example/2", "erw:energy_companies/X", "https://a.example/1"], "evidence": [{"address": "https://c.example/3"}, {"address": ""}]}]
        store = {"rows": [{"row": {"source_urls": ["https://a.example/1", "https://z.example/9"]}}], "quotes": [{"address": "https://y.example/8"}]}
        self.assertEqual(R.cited_addresses(orgs, store), ["https://a.example/1", "https://b.example/2", "https://c.example/3", "https://y.example/8", "https://z.example/9"])

    def test_the_runs_day_is_the_utc_day_of_its_id(self):
        self.assertEqual(R.run_day("20261007T235959Z-abc123"), "2026-10-07")
        self.assertRegex(R.run_day("run-x"), r"^\d{4}-\d{2}-\d{2}$")


class Headers(unittest.TestCase):
    """The one header a page request carries, exactly; no personal address anywhere."""

    def test_the_user_agent_is_exactly_the_owners_string(self):
        self.assertEqual(pg.UA, UA)
        self.assertEqual(pg.HEADERS, {"User-Agent": UA})
        self.assertEqual(pg.request_of("https://h.example/p").header_items(), [("User-agent", UA)])
        self.assertEqual(pg.request_of("https://h.example/p").get_method(), "GET")

    def test_every_request_of_a_pull_carries_that_header_and_no_other(self):
        urls = ["https://h.example/p", "http://r.example/a"]
        web = Web(pages={urls[0]: (200, HTML, PAGE), urls[1]: (301, {"location": "https://r.example/a"}, ""), "https://r.example/a": (200, HTML, PAGE)})
        pull(urls, web)
        self.assertGreaterEqual(len(web.asked), 5)                # two pages, a hop, and each host's robots.txt
        for url, headers, _, _ in web.asked:
            self.assertEqual(headers, {"User-Agent": UA}, url)

    def test_no_personal_address_no_cookie_and_no_archive_service_in_the_fetcher(self):
        code = src("warehouse", "thesis", "pages.py")
        self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", code))
        self.assertNotIn("@", UA)
        for w in ("CookieJar", "HTTPCookieProcessor", "Cookie\"", "web.archive.org", "archive.org", "webcache", "archive.ph", "Mozilla", "Referer", "Authorization"):
            self.assertNotIn(w, code, w)
        body = code.split("def transport(")[1].split("\ndef ")[0]
        self.assertIn("_NoRedirect", body)                         # a redirect is never followed by the library
        self.assertIn("opener.addheaders = []", body)

    def test_the_default_opener_follows_no_redirect_and_holds_no_cookie_jar(self):
        import urllib.request
        opener = urllib.request.build_opener(pg._NoRedirect)
        names = {type(h).__name__ for h in opener.handlers}
        self.assertNotIn("HTTPCookieProcessor", names)
        self.assertIsNone(pg._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://h.example/x"))


class FakeStorage:
    """A stand-in for the storage API: objects by path, every call recorded with its headers."""

    def __init__(self, bucket=True, refuse_write=False, stale=0):
        self.objects, self.calls, self.bucket, self.refuse_write, self.stale = {}, [], bucket, refuse_write, stale
        self.before = {}

    def __call__(self, method, url, headers, body=None, timeout=60):
        path = url.split("/storage/v1/", 1)[1].split("?")[0]
        self.calls.append((method, path, dict(headers), url))
        if path == "bucket/erw-thesis":
            return (200, json.dumps({"id": "erw-thesis", "public": self.bucket == "public"}).encode()) if self.bucket else (400, b'{"statusCode":"404","error":"Bucket not found"}')
        if path == "bucket" and method == "POST":
            self.bucket = True
            self.made = json.loads(body)
            return 200, b'{"name":"erw-thesis"}'
        key = path.split("object/erw-thesis/", 1)[1]
        if method == "GET":
            if self.stale and key in self.before:                    # a read just after a write answered with the version before it
                self.stale -= 1
                return 200, self.before[key]
            return (200, self.objects[key]) if key in self.objects else (400, b'{"statusCode":"404","error":"not_found","message":"Object not found"}')
        if method == "POST":
            if self.refuse_write:
                return 500, b"no"
            if key in self.objects and headers.get("x-upsert") != "true":
                return 409, b'{"error":"Duplicate"}'
            if key in self.objects:
                self.before[key] = self.objects[key]
            self.objects[key] = body
            return 200, b"{}"
        return 405, b""


class Store(unittest.TestCase):
    NAME = "geothermal-mapping-and-sensing__united-states__startups"

    def bucket(self, send, fallback=None, log=None):
        import datetime as dt
        ticks = iter(range(100))
        now = lambda: dt.datetime(2026, 10, 7, 22, 0, 0, tzinfo=dt.timezone.utc) + dt.timedelta(seconds=next(ticks))
        return es.BucketStore("https://abc.supabase.co/rest/v1/", "service-key-not-real", self.NAME, send=send, fallback=fallback, log=log, now=now, sleep=lambda s: None)

    def test_the_stores_name_is_the_one_the_local_file_always_had(self):
        self.assertEqual(es.store_name(NICHE, "startups", "United States"), self.NAME)
        self.assertEqual(os.path.basename(R.store_path("x", NICHE, "startups", "United States")), self.NAME + ".json")
        self.assertEqual(es.store_name("Grid batteries: software", "", ""), "grid-batteries__any__any")

    def test_the_bucket_store_round_trips_whole(self):
        api = FakeStorage()
        b = self.bucket(api)
        self.assertEqual(b.ensure_bucket(), "exists")
        first = b.load(NICHE, "startups", "United States")
        self.assertEqual((first["version"], first["rows"], first["pages"]), (2, [], {}))
        store = copy.deepcopy(FIX["store"])
        where = b.save(store)
        self.assertEqual(where, f"supabase storage (private): erw-thesis/evidence/{self.NAME}.json.gz")
        self.assertEqual(list(api.objects), [f"evidence/{self.NAME}.json.gz"])
        self.assertEqual(json.loads(gzip.decompress(api.objects[f"evidence/{self.NAME}.json.gz"])), json.loads(json.dumps(store, sort_keys=True, default=str)))
        self.assertEqual(self.bucket(api).load(), json.loads(json.dumps(store, default=str)))
        self.assertTrue(all(u.startswith("https://abc.supabase.co/storage/v1/") for _, _, _, u in api.calls))       # /rest/v1/ is dropped from SUPABASE_URL

    def test_the_object_as_it_was_is_kept_under_a_dated_name_before_it_is_replaced(self):
        api = FakeStorage()
        b = self.bucket(api)
        one = copy.deepcopy(FIX["store"])
        b.save(one)
        v1 = api.objects[f"evidence/{self.NAME}.json.gz"]
        two = copy.deepcopy(one)
        two["runs"].append({"run_id": "later", "date": "2026-10-08", "seq": 99})
        b.save(two)
        kept = [k for k in api.objects if k.startswith(f"evidence/history/{self.NAME}/")]
        self.assertEqual(len(kept), 1)
        self.assertRegex(kept[0], r"/20261007T2200\d\dZ\.json\.gz$")
        self.assertEqual(api.objects[kept[0]], v1)
        self.assertEqual(b.load()["runs"][-1]["run_id"], "later")
        b.save(two)                                                # the same content again: nothing to keep, nothing new under history
        self.assertEqual(len([k for k in api.objects if k.startswith(f"evidence/history/{self.NAME}/")]), 1)
        posts = [(p, h.get("x-upsert")) for m, p, h, _ in api.calls if m == "POST"]
        self.assertIn(("object/erw-thesis/" + kept[0], "false"), posts)                   # a dated copy is never overwritten

    def test_a_write_is_believed_only_when_it_reads_back(self):
        api = FakeStorage()
        b = self.bucket(api)
        b.save(copy.deepcopy(FIX["store"]))
        two = copy.deepcopy(FIX["store"])
        two["runs"].append({"run_id": "later", "date": "2026-10-08", "seq": 99})
        api.stale = 0
        gets = sum(1 for m, _, _, _ in api.calls if m == "GET")
        b.save(two)
        self.assertGreaterEqual(sum(1 for m, _, _, _ in api.calls if m == "GET") - gets, 2)         # read before the write, and read back after it
        reads = [u for m, _, _, u in api.calls if m == "GET" and "/object/" in u]
        self.assertEqual(len(reads), len(set(reads)))              # every read carries a query of its own: none is answered from a cache

    def test_a_refused_write_falls_back_to_the_file_and_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, lines = os.path.join(tmp, "e", self.NAME + ".json"), []
            b = self.bucket(FakeStorage(refuse_write=True), fallback=path, log=lines.append)
            where = b.save(copy.deepcopy(FIX["store"]))
            self.assertTrue(where.startswith("local file (the bucket refused the write)"))
            self.assertEqual(b.kind, "file")
            self.assertEqual(json.load(open(path, encoding="utf-8"))["niche"], NICHE)
            self.assertTrue(any("NOT WRITTEN TO THE BUCKET" in s for s in lines))
        with self.assertRaises(RuntimeError):
            self.bucket(FakeStorage(refuse_write=True)).save(copy.deepcopy(FIX["store"]))          # with no fallback the failure is loud

    def test_with_no_key_the_store_is_the_local_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            h = es.open_store(tmp, NICHE, "startups", "United States", mode="auto", env={})
            self.assertEqual((h.kind, h.where), ("file", os.path.join(tmp, self.NAME + ".json")))
            h.save(copy.deepcopy(FIX["store"]))
            self.assertEqual(es.open_store(tmp, NICHE, "startups", "United States", mode="auto", env={}).load()["niche"], NICHE)
            with self.assertRaises(RuntimeError):
                es.open_store(tmp, NICHE, "startups", "United States", mode="bucket", env={})
            env = {"SUPABASE_URL": "https://abc.supabase.co/rest/v1/", "SUPABASE_SERVICE_KEY": "service-key-not-real"}
            b = es.open_store(tmp, NICHE, "startups", "United States", mode="auto", env=env, send=FakeStorage())
            self.assertEqual((b.kind, b.fallback), ("bucket", os.path.join(tmp, self.NAME + ".json")))
            self.assertEqual(es.open_store(tmp, NICHE, "startups", "United States", mode="file", env=env).kind, "file")

    def test_the_bucket_is_created_private_with_one_call_and_a_public_one_is_refused(self):
        api = FakeStorage(bucket=False)
        self.assertEqual(self.bucket(api).ensure_bucket(), "created")
        self.assertEqual(api.made, {"id": "erw-thesis", "name": "erw-thesis", "public": False})
        self.assertEqual([(m, p) for m, p, _, _ in api.calls], [("GET", "bucket/erw-thesis"), ("POST", "bucket")])
        with self.assertRaises(RuntimeError):
            self.bucket(FakeStorage(bucket="public")).ensure_bucket()

    def test_the_key_goes_only_to_the_storage_api_and_is_never_in_the_record(self):
        api = FakeStorage()
        b = self.bucket(api)
        b.save(copy.deepcopy(FIX["store"]))
        for _, _, headers, url in api.calls:
            self.assertEqual(headers["Authorization"], "Bearer service-key-not-real")
            self.assertNotIn("service-key-not-real", url)
        self.assertNotIn("service-key-not-real", json.dumps(b.calls) + b.where)
        self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", src("warehouse", "thesis", "store.py")))

    def test_a_handle_is_made_from_a_path_and_none_stays_none(self):
        self.assertIsNone(es.handle_of(None))
        self.assertEqual(es.handle_of("x.json").kind, "file")
        h = es.FileStore("y.json")
        self.assertIs(es.handle_of(h), h)


class Runner(unittest.TestCase):
    """What the GitHub runner holds and needs."""

    def test_the_workflow_gives_the_run_the_two_storage_credentials(self):
        yml = src(".github", "workflows", "thesis.yml")
        for name in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY"):
            self.assertIn(name + ": ${{ secrets." + name + " }}", yml)
        self.assertIn("warehouse/thesis/run.py", yml)
        self.assertNotIn("--no-fetch", yml)
        self.assertNotIn("--evidence-store file", yml)

    def test_the_warehouse_tier_is_on_the_runner_because_its_two_tables_are_in_git(self):
        ignore = src(".gitignore")
        for name in ("energy_companies.csv", "energy_deals.csv"):
            self.assertIn("!warehouse/output/" + name, ignore, name)          # allowlisted in sessions 27 and 15
        try:
            out = subprocess.run(["git", "ls-files", "warehouse/output/energy_companies.csv", "warehouse/output/energy_deals.csv"], cwd=ROOT, capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            self.skipTest("git is not here")
        if out.returncode != 0:
            self.skipTest("not a git checkout")
        self.assertEqual(sorted(out.stdout.split()), ["warehouse/output/energy_companies.csv", "warehouse/output/energy_deals.csv"])

    def test_a_run_started_by_the_page_fetches_and_uses_the_bucket_and_a_test_does_neither(self):
        code = src("warehouse", "thesis", "run.py")
        self.assertIn('ap.add_argument("--evidence-store", choices=["auto", "bucket", "file"], default="auto"', code)
        self.assertIn('getattr(args, "evidence_store", "file")', code)        # arguments built by a test, without the flag: the file
        self.assertIn('getattr(args, "no_fetch", True)', code)                # and no request


class Files(unittest.TestCase):
    PARTS = (("warehouse", "thesis", "tie.py"), ("warehouse", "thesis", "run.py"), ("warehouse", "thesis", "pages.py"), ("warehouse", "thesis", "store.py"),
             ("tests", "test_session147.py"), ("tests", "fixtures", "session147", "pages.json"), ("docs", "methods", "thesis_builder.md"))

    def test_no_em_dash_in_the_sessions_files(self):
        for parts in self.PARTS:
            self.assertNotIn(chr(0x2014), src(*parts), parts)

    def test_the_rule_and_the_pull_are_not_in_the_published_methods(self):
        for name in os.listdir(os.path.join(ROOT, "docs", "methods")):
            if name.endswith(".md") and name != "thesis_builder.md":          # thesis_builder.md is internal and not built into the site (session 135)
                text = src("docs", "methods", name)
                for w in ("pages.py", "PAGE_SENTENCE_MAX", "erw-thesis", "TIE_MIN"):
                    self.assertNotIn(w, text, (name, w))
        self.assertIn("thesis_builder", src("site", "scripts", "build-content.mjs"))

    def test_the_internal_method_describes_the_pull_and_the_store(self):
        text = src("docs", "methods", "thesis_builder.md")
        for w in (UA, "robots.txt", "erw-thesis", "SHA-256", "misoenergy.org", "150", "2 MB", "tie.py", "pages.py", "store.py"):
            self.assertIn(w, text, w)

    def test_this_module_changes_no_environment_at_import(self):
        code = src("tests", "test_session147.py")
        top = code.split("class Web:")[0]
        self.assertNotIn("os.environ[", top.split("def setUpModule")[0])
        self.assertIn("def setUpModule", top)
        self.assertIn("def tearDownModule", top)


if __name__ == "__main__":
    unittest.main()
