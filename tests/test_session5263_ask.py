"""Session 5263 (window P3's close-out of 14 November 2026): the evaluation's spend guard reads the whole ledger.

Session 5262 found it on 13 November 2026: warehouse/chat/eval/eval_s1113.py spent_today() asked Supabase for the day's
rows of the site's cost ledger (site_api_calls, the step site_ask_eval) in one request with "limit=5000". Supabase
answers a request with at most 1,000 rows whatever limit it names. The ledger held 1,092 rows that day, so the count
stopped at 1,000 (USD 18.01) and the cap was checked against less than the day's spend.

Held here, with a stand-in for the server that holds more than 1,000 rows and answers 1,000 at most, as Supabase does:
every row is counted; the size of the server's page is not leaned on; a row written during the reading is counted once;
a day that cannot be counted whole (fewer rows than the server counts, a page that does not move on, a call with no
price) stops the asking before the call, never falling back to a smaller number; the cap of the asking is held against
the whole day. And that no other spend helper of the repository reads its total through one row-limited request.

No network, no model: the one request function (ledger_page) and the one posting function (post) are stand-ins.
"""
import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
import re
import tempfile
import unittest
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
DAY = dt.datetime(2026, 11, 13, 21, 30, tzinfo=dt.timezone.utc)


def runner():
    spec = importlib.util.spec_from_file_location("eval_s1113_for_test_5263", os.path.join(EVAL, "eval_s1113.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Ledger:
    """Supabase's answer for site_api_calls, as far as the guard asks it: the filters eq. on step, gte. on ts_utc and
    gt. on id, the order by id, limit and offset, the exact count of the rows the filters match in Content-Range, and
    never more than `most` rows in one answer, whatever limit the request names (Supabase's setting is 1,000)."""

    def __init__(self, rows, most=1000):
        self.rows, self.most, self.asked = list(rows), most, []
        self.between = None     # called before each answer but the first: rows written while the reading runs

    def __call__(self, url, headers):
        u = urllib.parse.urlparse(url)
        q = dict(urllib.parse.parse_qsl(u.query))
        if self.asked and self.between:
            self.between(self)
        self.asked.append({"path": u.path, "query": q, "headers": dict(headers)})
        rows = [r for r in self.rows if r["step"] == q["step"][len("eq."):] and r["ts_utc"] >= q["ts_utc"][len("gte."):]]
        if "id" in q:
            rows = [r for r in rows if r["id"] > int(q["id"][len("gt."):])]
        if q.get("order") == "id.asc":
            rows = sorted(rows, key=lambda r: r["id"])
        offset = int(q.get("offset", "0"))
        page = rows[offset:offset + min(int(q.get("limit", self.most)), self.most)]
        said = f"{offset}-{offset + len(page) - 1}/{len(rows)}" if page else f"*/{len(rows)}"
        return [{k: r[k] for k in q["select"].split(",")} for r in page], said


def day_rows(n, usd=0.02, ts="2026-11-13T08:00:00Z", step="site_ask_eval", first_id=5001):
    return [{"id": first_id + i, "usd": usd, "ts_utc": ts, "step": step} for i in range(n)]


def the_day_of_13_november():
    """1,092 rows of the evaluation's step on the day, with rows the guard must leave out: the day before, and the
    public tools' own steps on the day (their ceilings are the database's, migration 035)."""
    return (day_rows(40, usd=0.5, ts="2026-11-12T23:59:59Z", first_id=1)
            + day_rows(25, usd=0.3, step="site_ask", first_id=101)
            + day_rows(1092)
            + day_rows(10, usd=0.3, step="site_ask_ercot", first_id=9001))


def spent(m, ledger, **k):
    return m.spent_today(get=ledger, url="https://example.supabase.co", key="k" * 40, now=DAY, **k)


class TheWholeLedgerIsRead(unittest.TestCase):
    def test_one_request_is_answered_with_a_thousand_rows_whatever_limit_it_names(self):
        # the fault as session 5262 met it: the old read, one request with limit=5000, against 1,092 rows
        ledger = Ledger(the_day_of_13_november())
        q = urllib.parse.urlencode({"select": "usd", "step": "eq.site_ask_eval", "ts_utc": "gte.2026-11-13T00:00:00Z", "limit": "5000"})
        rows, said = ledger(f"https://example.supabase.co/rest/v1/site_api_calls?{q}", {})
        self.assertEqual((len(rows), said), (1000, "0-999/1092"))
        self.assertAlmostEqual(sum(r["usd"] for r in rows), 20.00, places=6)     # 1.84 short of the day

    def test_every_row_past_the_first_thousand_is_counted(self):
        m = runner()
        ledger = Ledger(the_day_of_13_november())
        usd, calls = spent(m, ledger)
        self.assertEqual(calls, 1092)
        self.assertAlmostEqual(usd, 1092 * 0.02, places=6)                        # 21.84, not 20.00
        self.assertGreater(len(ledger.asked), 1)
        for a in ledger.asked:                                                     # each request is the day's step, in the key's order
            self.assertEqual(a["path"], "/rest/v1/site_api_calls")
            self.assertEqual((a["query"]["step"], a["query"]["ts_utc"], a["query"]["order"]), ("eq.site_ask_eval", "gte.2026-11-13T00:00:00Z", "id.asc"))
            self.assertEqual(a["headers"]["Prefer"], "count=exact")
        self.assertNotIn("id", ledger.asked[0]["query"])
        self.assertEqual(ledger.asked[1]["query"]["id"], "gt.6000")               # the second page begins after the last row read

    def test_many_more_rows_and_a_smaller_page_of_the_server_are_read_whole(self):
        m = runner()
        for n, most in ((2500, 1000), (1092, 250), (30, 1), (1000, 1000), (1001, 1000), (999, 1000), (3, 1000)):
            usd, calls = spent(m, Ledger(day_rows(n), most=most))
            self.assertEqual(calls, n, (n, most))
            self.assertAlmostEqual(usd, n * 0.02, places=6)

    def test_a_day_with_no_call_is_zero_and_not_an_error(self):
        m = runner()
        self.assertEqual(spent(m, Ledger(day_rows(40, ts="2026-11-12T10:00:00Z"))), (0, 0))

    def test_a_row_written_while_the_ledger_is_read_is_counted_once(self):
        m = runner()
        ledger = Ledger(day_rows(1092))
        added = []

        def between(led):
            if not added:
                added.extend(day_rows(7, usd=0.11, first_id=20001))
                led.rows += added
        ledger.between = between
        usd, calls = spent(m, ledger)
        self.assertEqual(calls, 1099)
        self.assertAlmostEqual(usd, 1092 * 0.02 + 7 * 0.11, places=6)

    def test_no_keys_or_no_answer_is_none_and_the_runs_own_costs_stand_in(self):
        m = runner()
        self.assertIsNone(m.spent_today(get=Ledger([]), url="", key="k" * 40, now=DAY))
        self.assertIsNone(m.spent_today(get=Ledger([]), url="https://example.supabase.co", key="", now=DAY))

        def down(url, headers):
            raise OSError("timed out")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertIsNone(spent(m, down))
        self.assertIn("ledger unreadable", out.getvalue())


class ADayThatCannotBeCountedStopsTheAsking(unittest.TestCase):
    def test_fewer_rows_than_the_server_counts_is_refused(self):
        m = runner()
        whole = Ledger(day_rows(1092))

        def short(url, headers):                   # the first page, then nothing: 1,000 read of 1,092 counted
            rows, said = whole(url, headers)
            return (rows, said) if len(whole.asked) == 1 else ([], "*/0")
        with self.assertRaises(m.LedgerNotWhole) as e:
            spent(m, short)
        self.assertIn("1092", str(e.exception))
        self.assertIn("1000", str(e.exception))

    def test_a_page_that_does_not_move_on_is_refused_and_the_reading_ends(self):
        m = runner()
        first = day_rows(1000)

        def stuck(url, headers):                   # a server that leaves the id filter out answers the same page again
            return [{"id": r["id"], "usd": r["usd"]} for r in first], "0-999/1092"
        with self.assertRaises(m.LedgerNotWhole):
            spent(m, stuck)

    def test_an_answer_that_stops_after_the_first_page_is_refused_not_taken_as_the_day(self):
        m = runner()
        whole = Ledger(day_rows(1092))

        def breaks(url, headers):
            if whole.asked:
                raise OSError("connection reset")
            return whole(url, headers)
        with self.assertRaises(m.LedgerNotWhole) as e:
            spent(m, breaks)
        self.assertIn("1000 rows", str(e.exception))

    def test_a_call_with_no_price_and_an_answer_with_no_count_are_refused(self):
        m = runner()
        rows = day_rows(12)
        rows[5]["usd"] = None
        with self.assertRaises(m.LedgerNotWhole):
            spent(m, Ledger(rows))
        ledger = Ledger(day_rows(12))
        with self.assertRaises(m.LedgerNotWhole):
            spent(m, lambda url, headers: (ledger(url, headers)[0], ""))
        with self.assertRaises(m.LedgerNotWhole):
            spent(m, lambda url, headers: ({"message": "JWT expired"}, ""))


class TheCapIsHeldAgainstTheWholeDay(unittest.TestCase):
    """ask(): the day's 1,092 calls are USD 21.84, the first thousand USD 20.00. With the reserve of USD 0.50, a cap of
    USD 21 let the next question through on the first thousand rows; on the whole day it is stopped before the call."""

    def setUp(self):
        self.m = runner()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_path = os.path.join(self.tmp.name, "run.json")
        self.m.SETS["s320"] = dict(self.m.SETS["s320"], run=self.run_path)
        self.m.questions = lambda path=None: [{"id": "q01", "grid": "ERCOT", "via": "general", "question": "What was the price?"}]
        secrets = {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_KEY": "k" * 40, "ASK_EVAL_TOKEN": "t" * 30}
        self.m.env_file = lambda path, name: secrets.get(name, "")
        self.posted = []

        def post(base, token, q, ip):
            self.posted.append(q["id"])
            return {"status": "answered", "answer": "x", "cost_usd": 0.1, "tool_calls": 2, "_http": 200, "_seconds": 1.0}
        self.m.post = post

    def ask(self, ledger, cap):
        self.m.ledger_page = ledger
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.m.ask("http://127.0.0.1:1", cap)
        return out.getvalue()

    def today(self, n, **k):      # stamped after any day the test runs on: the guard asks for the rows since today's midnight
        return day_rows(n, ts="2999-01-01T00:00:00Z", **k)

    def test_a_cap_between_the_first_thousand_and_the_whole_day_stops_before_the_call(self):
        said = self.ask(Ledger(self.today(1092)), 21.0)
        self.assertEqual(self.posted, [])
        self.assertIn("q01: STOPPED before the call: spent 21.8400", said)
        self.assertFalse(os.path.exists(self.run_path))

    def test_the_same_cap_on_a_day_under_it_asks(self):
        said = self.ask(Ledger(self.today(1000)), 21.0)        # USD 20.00 and the reserve are under the cap
        self.assertEqual(self.posted, ["q01"])
        self.assertNotIn("STOPPED", said)
        with open(self.run_path, encoding="utf-8") as f:
            self.assertEqual([x["id"] for x in json.load(f)["questions"]], ["q01"])

    def test_a_day_that_cannot_be_counted_asks_nothing_and_the_last_line_still_prints(self):
        whole = Ledger(self.today(1092))

        def short(url, headers):
            rows, said = whole(url, headers)
            return (rows, said) if "id" not in dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query)) else ([], "*/0")
        said = self.ask(short, 1000.0)
        self.assertEqual(self.posted, [])
        self.assertIn("STOPPED before the call: the day's spend is not known", said)
        self.assertIn("the step's ledger today: not counted", said)


class TheDaysCeilingOfTheSitesLoop(unittest.TestCase):
    """eval_site.py --day-cap: the UTC day's ceiling over every asking that writes the ledger, read whole first."""

    def site(self):
        spec = importlib.util.spec_from_file_location("eval_site_for_test_5263", os.path.join(EVAL, "eval_site.py"))
        s = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(s)
        return s

    def with_ledger(self, ledger):
        m = runner()
        secrets = {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_KEY": "k" * 40}
        m.env_file = lambda path, name: secrets.get(name, "")
        m.ledger_page = ledger
        return m

    def test_what_the_day_has_left_is_counted_on_every_row(self):
        s = self.site()
        left, line = s.day_room(self.with_ledger(Ledger(day_rows(1092, ts="2999-01-01T00:00:00Z"))), 22.0)
        self.assertAlmostEqual(left, 22.0 - 21.84, places=6)      # on the first thousand rows it would have been USD 2.00
        self.assertIn("USD 21.8400 in 1092 calls", line)
        left, _ = s.day_room(self.with_ledger(Ledger(day_rows(1092, ts="2999-01-01T00:00:00Z"))), 20.0)
        self.assertEqual(left, 0.0)                               # a day over its ceiling has nothing left, never less

    def test_a_day_that_cannot_be_counted_or_asked_has_nothing_left(self):
        s = self.site()

        def stuck(url, headers):
            return [{"id": 7, "usd": 0.1}], "0-0/5"
        left, line = s.day_room(self.with_ledger(stuck), 20.0)
        self.assertEqual(left, 0.0)
        self.assertIn("not known", line)
        m = self.with_ledger(Ledger([]))
        m.env_file = lambda path, name: ""
        left, line = s.day_room(m, 20.0)
        self.assertEqual(left, 0.0)
        self.assertIn("could not be asked", line)

    def test_the_runner_is_given_the_lesser_of_the_sessions_ceiling_and_the_days(self):
        src = read("warehouse", "chat", "eval", "eval_site.py")
        self.assertIn("cap_total = min(cap, before + left)", src)
        self.assertIn('cmd = node_command(qpath, F["run"], cap_total,', src)
        self.assertIn("--day-cap goes without --no-ledger", src)
        self.assertIn("if left <= 0:\n                ids = []", src)

    def test_the_command_that_prints_the_days_spend(self):
        m = self.with_ledger(Ledger(day_rows(1092, ts="2999-01-01T00:00:00Z")))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(m.main(["--spent"]), 0)
        self.assertEqual(out.getvalue().strip(), "site_ask_eval today (UTC): USD 21.8400 in 1092 calls")
        m.ledger_page = lambda url, headers: ([{"id": 7, "usd": None}], "0-0/1")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(m.main(["--spent"]), 3)
        m.env_file = lambda path, name: ""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(["--spent"]), 4)


class NoOtherSpendHelperHasTheLimit(unittest.TestCase):
    """What each of the other spend guards reads, pinned from its source: a sum the database makes, a file read whole,
    the run's own costs, or pages. None takes its total from one request of rows."""

    def test_the_guard_asks_for_no_single_large_page(self):
        s = read("warehouse", "chat", "eval", "eval_s1113.py")
        body = s[s.index("def spent_today("):s.index("def ledger_line(")]
        self.assertNotIn('"limit": "5000"', s)
        self.assertIn('"order": "id.asc"', body)
        self.assertIn('p["id"] = f"gt.{last}"', body)
        self.assertIn("if not page:", body)                    # the reading ends on an empty page, not on a short one

    def test_the_sites_ceilings_are_sums_the_database_makes(self):
        route = read("site", "app", "api", "ask", "route.ts")
        self.assertIn('rpc("internal_ask_spend"', route)       # the evaluation's day spend (limits.ts admitEvaluation)
        self.assertIn('rpc("site_ask_admit"', route)           # the public day and month
        m23 = read("warehouse", "supabase", "migrations", "023_ask_limits.sql")
        spend = m23[m23.index("create or replace function public.internal_ask_spend"):]
        self.assertIn("returns jsonb", spend.split("as $$")[0])    # one value, so no page of rows to be cut
        self.assertIn("coalesce(sum(usd), 0) as usd", spend)
        self.assertIn("group by 1, 2", spend)
        m35 = read("warehouse", "supabase", "migrations", "035_ask_eval_step.sql")
        self.assertEqual(len(re.findall(r"coalesce\(sum\(usd\), 0\)", m35)), 2)
        self.assertNotIn("site_api_calls?", read("site", "lib", "chat", "limits.ts"))   # no REST read of the ledger's rows

    def test_the_sites_loop_and_its_runner_count_the_runs_own_file(self):
        loop = read("site", "scripts", "eval-ask-site-loop.mjs")
        self.assertIn("const spent = costOf(run);", loop)
        self.assertIn("[...(run.questions ?? []), ...(run.superseded ?? [])].reduce", loop)
        self.assertNotIn("rest/v1", loop)
        self.assertNotIn("rest/v1", read("warehouse", "chat", "eval", "eval_site.py"))
        self.assertNotIn("rest/v1", read("warehouse", "chat", "eval", "eval_loop.py"))

    def test_the_warehouses_guards_read_a_file_whole_a_sum_or_pages(self):
        llm = read("warehouse", "llm.py")
        total = llm[llm.index("def session_total("):llm.index("HEADER = [")]
        self.assertIn("df = read_ledger()", total)             # the ledger's file on the machine, every row
        thesis = read("warehouse", "thesis", "run.py")
        self.assertIn('"select coalesce(sum(usd), 0) from public.thesis_runs', thesis[thesis.index("def spent_today(conn):"):][:400])
        health = read("warehouse", "health.py")
        remote = health[health.index("def ledger_remote("):health.index("def model_spend(")]
        self.assertIn('"Range": f"{start}-{start + 999}"', remote)   # the daily cap's read of Supabase's copy: pages of 1,000
        self.assertIn("start += 1000", remote)


if __name__ == "__main__":
    unittest.main()
