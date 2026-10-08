"""Session 157: the policy monitor's reads, tags and feeds.

The printed text of a Federal Register action, read once (the place rule and the title rule on the saved real
documents of both audit samples; the store, the table held and the ceilings; the Register's own limit honoured: an
HTTP 429 is waited out and never written to a row; a redirect is never followed). The reader's three corrections held
by code, and its number check. The scorer's summary. The recheck: the stop before each call, a paid answer saved
before it is read, every row marked. The tag rule, version 3, on the cases the page's rule is held to as well. The
site files' shapes, and the daily step that never writes a thinner file. Rows made for a test are marked MADE UP and
live only in a temporary folder. No request and no model call; the environment is read, never set; a test that needs
a file a machine does not hold skips."""
import csv
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for part in ("connectors", "derived", "policy"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", part))
import policy_action_tags as pat  # noqa: E402
import policy_monitor_site as pms  # noqa: E402
import policy_sources as ps  # noqa: E402
import reads as R  # noqa: E402
import rules_in_motion as rim  # noqa: E402


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PS = load("policy_score_157", "warehouse", "policy", "score.py")   # not the news scorer, which is also named score
RC = load("policy_recheck_157", "warehouse", "policy", "recheck.py")

EM = chr(0x2014)
FIX = os.path.join(ROOT, "tests", "fixtures", "session157")
SITE = os.path.join(ROOT, "site", "data", "policy")
MINE = [("warehouse", "connectors", "policy_sources.py"), ("warehouse", "policy", "reads.py"),
        ("warehouse", "policy", "score.py"), ("warehouse", "policy", "recheck.py"),
        ("warehouse", "derived", "policy_monitor_site.py"), ("warehouse", "derived", "policy_action_tags.py"),
        ("warehouse", "config", "policy_tag_rules.json"), ("docs", "methods", "policy_monitor.md"),
        ("site", "data", "policy", "tag_rules.json"), ("site", "data", "policy", "grids.json"),
        ("site", "data", "policy", "state_rules.json"), ("site", "data", "policy", "refresh.json"),
        ("site", "data", "policy", "action_tags.json"), ("tests", "test_session157.py")]
KNOWN_MISSES = {"federalregister:2026-01151", "federalregister:2026-17529"}
DOC = ("<html><body><pre>\n[Federal Register Volume 91, Number 1 (Friday, January 2, 2026)]\n[Notices]\n"
       "[FR Doc No: 2026-00001]\n\n\n-----------------------------------------------------------------------\n\n"
       "DEPARTMENT OF ENERGY\n\nFederal Energy Regulatory Commission\n\n[Docket No. CP26-1-000]\n\n\n"
       "Made Up Louisiana Pipeline LLC; Notice of a Made Up Request\n\n"
       "    Take notice that Made Up Louisiana Pipeline LLC (MULP), 1001 Louisiana Street, Houston, Texas \n"
       "77002, asks to build a made up header in Jefferson County, Texas.\n</pre></body></html>")


def fr_row(n, day="2026-01-02", title="Made Up Louisiana Pipeline LLC; Notice of a Made Up Request"):
    """MADE UP: a Register row as the connector builds it (no such document)."""
    return {"event_id": f"federalregister:{n}", "event_date": day, "fr_document_number": n, "title": title,
            "abstract": "", "_text_url": f"https://www.federalregister.gov/documents/full_text/text/2026/01/02/{n}.txt"}


def quiet(*a, **k):
    return None


class PlaceAndTitle(unittest.TestCase):
    def test_the_rule_on_the_saved_documents_of_both_audit_samples(self):
        with open(os.path.join(FIX, "place_cases.json"), encoding="utf-8") as f:
            cases = json.load(f)["cases"]
        self.assertEqual(len(cases), 87)
        held_right, now_right, misses = 0, 0, set()
        for c in cases:
            with open(os.path.join(FIX, "fr_text", c["document"] + ".txt"), "rb") as f:
                raw = f.read().decode("utf-8", "replace")
            got = ps.printed(raw, c["title"])
            title = got["title"] if ps.cut_short(c["title"], got["title"]) else c["title"]
            first = ps.place_states(title, c["abstract"], got["first_paragraph"])
            new = first or ps.place_states(title, "", "", got["place_words"])
            held_right += c["held_states"] == c["true_states"]
            now_right += new == c["true_states"]
            if new != c["true_states"]:
                misses.add(c["event_id"])
        self.assertEqual(held_right, 54, "what the table held on 3 October: 54 of 87 as the document says")
        self.assertEqual(misses, KNOWN_MISSES, "the two the rule does not reach: a state that stands only in a company's name")
        self.assertEqual(now_right, 85)

    def test_a_title_the_record_cuts_at_a_semicolon_is_completed_from_the_print(self):
        with open(os.path.join(FIX, "fr_text", "2026-17632.txt"), "rb") as f:
            got = ps.printed(f.read().decode("utf-8", "replace"), "Gulf South Pipeline Company, LLC;")
        self.assertTrue(got["title"].startswith("Gulf South Pipeline Company, LLC; Notice of Intent To Prepare an Environmental"))
        self.assertTrue(ps.cut_short("Gulf South Pipeline Company, LLC;", got["title"]))
        self.assertTrue(got["first_paragraph"].startswith("The staff of the Federal Energy Regulatory Commission"))
        self.assertFalse(ps.cut_short("A Rule on Wood Products", "A Rule on Wood Products; Final Rule"), "a heading that adds a line is left")

    def test_what_is_not_a_place(self):
        f = lambda title, para: ps.place_states(title, "", para)
        self.assertEqual(f("Kinder Morgan Louisiana Pipeline LLC; Notice of Request", "facilities in Jefferson County, Texas"), "TX")
        self.assertEqual(f("City of Hamilton, Ohio and American Municipal Power, Inc.; Notice of Authorization", ""), "OH")
        self.assertEqual(f("City of Chignik, Alaska; Notice of Availability", ""), "AK")
        self.assertEqual(f("X; Notice", "Acme, 1001 Louisiana Street, Houston, Texas 77002, filed a request."), "")
        self.assertEqual(f("X; Notice", "The dam is on the Ohio River in Allegheny County, Pennsylvania."), "PA")
        self.assertEqual(f("X; Notice", "Comments are received in Washington, DC and at Rockville, Maryland."), "")
        self.assertEqual(f("X; Notice", "Texas Eastern Transmission, LP (Texas Eastern) will abandon a line near Louisiana. Texas Eastern's certificate stands."), "LA")
        self.assertEqual(f("X; Notice", "the New Hampshire Department of Environmental Services"), "NH")
        self.assertEqual(ps.states("units in the State of West Virginia"), "WV")

    def test_place_words_are_read_only_when_the_first_paragraph_names_no_state(self):
        got = ps.printed(DOC, "Made Up Louisiana Pipeline LLC; Notice of a Made Up Request")
        self.assertIn("Jefferson County, Texas", got["first_paragraph"])
        self.assertEqual(ps.place_states("T", "", "in Ohio", "in Adams County, Idaho"), "OH")
        self.assertEqual(ps.place_states("T", "", "no place here", "in Adams County, Idaho"), "ID")

    def test_hydrogen_chloride_is_not_the_hydrogen_sector(self):
        self.assertNotIn("hydrogen", ps.tags("emissions of hydrogen chloride from kilns"))
        self.assertIn("hydrogen", ps.tags("clean hydrogen hubs"))


class PrintedTextReadOnce(unittest.TestCase):
    def test_the_store_and_the_table_held_are_read_before_any_request(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "2026-00001.txt"), "w", encoding="utf-8") as f:
                f.write(DOC)
            rows = [fr_row("2026-00001"), fr_row("2026-00002")]
            held = {"federalregister:2026-00002": {"text_status": "read", "first_paragraph": "in Adams County, Idaho",
                                                   "place_words": "", "title_register": "", "text_read_at": "2026-10-01T00:00:00Z",
                                                   "title": rows[1]["title"]}}
            n = ps.read_texts(rows, held, d, quiet, fetch=lambda u: calls.append(u) or (200, b"", ""), sleep=quiet)
        self.assertEqual(calls, [], "a document held is never asked for again")
        self.assertEqual((n["store"], n["table"], n["asked"]), (1, 1, 0))
        self.assertEqual(rows[0]["states"], "TX", "not LA off the applicant's name, not the street")
        self.assertEqual(rows[1]["states"], "ID")
        self.assertEqual(rows[0]["text_status"], "read")

    def test_it_stops_before_the_ceiling(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            rows = [fr_row(f"2026-0000{i}", day=f"2026-01-0{i}") for i in range(1, 7)]
            n = ps.read_texts(rows, {}, d, quiet, max_requests=2, sleep=quiet,
                              fetch=lambda u: calls.append(u) or (200, DOC.encode(), ""))
        self.assertEqual(len(calls), 2)
        self.assertEqual(n["left"], 4)
        self.assertTrue(calls[0].endswith("2026-00006.txt"), "newest first")

    def test_a_429_is_waited_out_asked_once_more_and_never_written_to_a_row(self):
        answers = iter([(200, DOC.encode(), ""), (429, b"", "7"), (200, DOC.encode(), ""), (429, b"", ""), (429, b"", "")])
        calls, slept = [], []
        with tempfile.TemporaryDirectory() as d:
            rows = [fr_row(f"2026-0000{i}", day=f"2026-01-0{9 - i}") for i in range(1, 7)]
            n = ps.read_texts(rows, {}, d, quiet, max_requests=50, fetch=lambda u: calls.append(u) or next(answers),
                              sleep=slept.append)
        self.assertEqual(len(calls), 5, "after the second 429 in a row no document is asked for")
        self.assertEqual(slept, [7, ps.LIMIT_WAIT], "it waits as Retry-After says, else the stated wait")
        self.assertEqual((n["limited"], n["left"]), (3, 4))
        self.assertEqual([r.get("text_status", "") for r in rows], ["read", "read", "", "", "", ""])

    def test_a_redirect_is_not_followed_and_a_page_that_is_no_document_is_not_kept(self):
        for answer in ((302, b"", "https://unblock.federalregister.gov/"), (200, b"<html>Request Access</html>", "")):
            calls = []
            with tempfile.TemporaryDirectory() as d:
                rows = [fr_row("2026-00001"), fr_row("2026-00002", day="2026-01-01")]
                n = ps.read_texts(rows, {}, d, quiet, fetch=lambda u: calls.append(u) or answer, sleep=quiet)
                self.assertEqual(os.listdir(d), [], "nothing is kept")
            self.assertEqual(len(calls), 1, "the asking ends for the run")
            self.assertEqual([r.get("text_status", "") for r in rows], ["", ""])
            self.assertEqual(n["left"], 2, "the document refused and the one after it both wait for a later run")

    def test_an_address_with_an_email_in_it_is_not_requested_and_the_user_agent_holds_no_address(self):
        calls = []
        with tempfile.TemporaryDirectory() as d:
            r = fr_row("2026-00001")
            r["_text_url"] = "https://example.gov/someone@example.gov/x.txt"
            ps.read_texts([r], {}, d, quiet, fetch=lambda u: calls.append(u) or (200, b"", ""), sleep=quiet)
        self.assertEqual(calls, [])
        for ua in (ps.UA, R.UA, RC.UA):
            self.assertNotIn("@", ua["User-Agent"])

    def test_the_table_from_before_gains_the_columns_and_no_value_changes(self):
        import iso_prices as ip
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "policy_actions.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("# MADE UP: a table of before session 157\n")
                w = csv.writer(f, lineterminator="\n")
                w.writerow(ps.COLS_S154)
                w.writerow(["madeup:1"] + ["x"] * (len(ps.COLS_S154) - 1))
            keep = ip.OUT_DIR
            try:
                ip.OUT_DIR = d
                self.assertTrue(ps.widen_held(quiet))
                self.assertFalse(ps.widen_held(quiet), "a table already wide is left")
            finally:
                ip.OUT_DIR = keep
            with open(path, encoding="utf-8") as f:
                head = f.readline()
                rows = list(csv.DictReader(f))
        self.assertTrue(head.startswith("# MADE UP"))
        self.assertEqual(list(rows[0]), ps.COLS)
        self.assertTrue(all(rows[0][c] == "x" for c in ps.COLS_S154[1:]))
        self.assertTrue(all(rows[0][c] == "" for c in ps.TEXT_COLS + ["model_recheck", "model_rechecked_at"]))

    def test_the_listing_asks_for_the_text_address_and_for_the_treasury_and_the_irs(self):
        self.assertEqual(ps.AGENCIES["treasury-department"], "Treasury")
        self.assertEqual(ps.AGENCIES["internal-revenue-service"], "IRS")
        self.assertNotIn("Treasury", ps.ALWAYS_ENERGY, "a Treasury document is kept only when it names an energy subject")
        for c in ps.TEXT_COLS:
            self.assertIn(c, ps.COLS)


class ReaderAndScorer(unittest.TestCase):
    TEXT = ("Acme Louisiana Gas LLC, 1 Main Street, Idaho Falls, Idaho 83415, asks to build a natural gas pipeline in "
            "Jefferson County, Texas. The rule is at 10 CFR Part 609. Comments are due in 30 days.")

    def test_the_three_corrections_are_in_the_prompt_and_held_by_code(self):
        for words in ("where the action applies", "prices, rates or bills", "own word"):
            self.assertIn(words, R.SYSTEM)
        out = {"who_affected": {"sectors": ["nuclear", "gas"], "states": ["TX", "ID", "LA"]}, "direction": {"prices": "up"}}
        notes = R.enforce(out, self.TEXT)
        self.assertEqual(out["who_affected"]["sectors"], ["gas"], "a sector whose keyword the text lacks is taken out")
        self.assertEqual(out["who_affected"]["states"], ["TX"], "not an address, not a company's name")
        self.assertEqual(out["direction"]["prices"], "unclear")
        self.assertEqual(len(notes), 3)
        out = {"who_affected": {"sectors": ["gas"], "states": ["TX"]}, "direction": {"prices": "up"}}
        self.assertEqual(R.enforce(out, self.TEXT + " Rates will rise."), [])
        self.assertEqual(out["direction"]["prices"], "up")

    def test_a_number_in_the_text_read_is_accepted_and_one_that_is_not_is_refused(self):
        notes = []
        ok = R.check_field("what_changes", {"text": "It changes 10 CFR Part 609.", "spans": ["asks to build a natural gas pipeline"]},
                           self.TEXT, notes)
        self.assertEqual(ok, [])
        self.assertEqual(len(notes), 1, "the number accepted outside the quotations is noted")
        bad = R.check_field("what_changes", {"text": "It costs 45 million.", "spans": ["asks to build a natural gas pipeline"]}, self.TEXT)
        self.assertTrue(bad and "not in the text" in bad[0])
        self.assertTrue(R.check_field("what_changes", {"text": "x", "spans": ["words that are not there"]}, self.TEXT))

    def test_the_print_s_marks_are_read_as_a_model_copies_them(self):
        a = "the ``decision- making'' process" + chr(92) + "1" + chr(92) + " , now"
        self.assertEqual(R.norm(a), 'the "decision-making" process, now')

    def test_the_read_s_text_comes_from_the_printed_text_held(self):
        text = R.register_text("A title", DOC)
        self.assertTrue(text.startswith("A title. "))
        self.assertIn("Take notice that Made Up Louisiana Pipeline LLC", text)
        self.assertNotIn("<pre>", text)
        self.assertEqual(R.READ_COLS[-2:], ["recheck", "rechecked_at"])

    def test_the_scorer_is_given_the_first_paragraph_where_the_abstract_is_empty(self):
        r = {"event_id": "madeup:1", "title": "T", "abstract": "", "first_paragraph": "P" * 700, "status": "Notice."}
        self.assertEqual(PS.item_of(r)["summary"], "P" * 600)
        self.assertEqual(PS.item_of(dict(r, abstract="A"))["summary"], "A")
        self.assertEqual(PS.item_of(dict(r, first_paragraph=""))["summary"], "Notice.")
        self.assertIn("When the summary is empty, say what the title says and no more", PS.POLICY_NOTE)
        self.assertEqual(PS.SCORE_COLS[-2:], ["model_recheck", "model_rechecked_at"])
        self.assertEqual(PS.SCORE_COLS, ps.SCORE_COLS)


class Recheck(unittest.TestCase):
    def test_the_stop_sits_before_the_call_and_counts_the_calls_in_flight(self):
        b = RC.Budget(5.50, 5.30)
        self.assertTrue(b.take(0.09))
        self.assertTrue(b.take(0.09))
        self.assertFalse(b.take(0.09), "5.30 spent and 0.18 in flight: a third reserve of 0.09 would pass 5.50")
        b.done(0.09, 0.013)
        self.assertTrue(b.take(0.09))
        self.assertFalse(RC.may_call(5.45, 0.06, 5.50))
        self.assertTrue(RC.may_call(5.44, 0.06, 5.50))

    def test_the_reserve_is_a_worst_case(self):
        import llm
        res = RC.reserve_usd("claude-sonnet-5-5", 12000, RC.READ_MAX_TOKENS, llm)
        p = llm.prices()["models"]["claude-sonnet-5-5"]
        self.assertGreaterEqual(res, RC.READ_MAX_TOKENS * p["output"] / 1e6)
        self.assertGreater(res, 0.02, "above what a read was measured to cost")

    def test_a_release_on_a_host_that_is_no_regulator_s_is_not_requested(self):
        self.assertNotIn("gov.texas.gov", RC.RELEASE_HOSTS)
        with tempfile.TemporaryDirectory() as d:
            text, why = RC.release_text({"event_id": "puct:madeup", "source_url": "https://gov.texas.gov/news/post/made-up",
                                         "title": "MADE UP"}, d, {"lock": None, "last": {}, "requests": 0, "bytes": 0}, quiet)
        self.assertIsNone(text)
        self.assertTrue(why.startswith("not requested"))

    def test_the_tables_are_built_from_the_saved_answers_and_every_row_is_marked(self):
        with tempfile.TemporaryDirectory() as d:
            work = os.path.join(d, "work")
            os.makedirs(os.path.join(work, "answers", "reads"))
            os.makedirs(os.path.join(work, "answers", "scores"))
            os.makedirs(os.path.join(work, "no_text"))
            text = "MADE UP notice. The made up rule takes effect on a made up day in Adams County, Idaho."
            tfile = os.path.join(work, "t1.txt")
            with open(tfile, "w", encoding="utf-8") as f:
                f.write(text)
            acts = os.path.join(d, "policy_actions.csv")
            with open(acts, "w", encoding="utf-8", newline="") as f:
                f.write("# MADE UP\n")
                w = csv.DictWriter(f, fieldnames=ps.COLS, lineterminator="\n")
                w.writeheader()
                for i, (num, status) in enumerate((("2026-1", "read"), ("2026-2", "read"), ("2026-3", "not reachable: HTTP 404"), ("", ""))):
                    w.writerow({c: "" for c in ps.COLS} | {
                        "event_id": f"federalregister:{num}" if num else "nrc:madeup", "event_date": f"2026-01-0{i + 1}",
                        "fr_document_number": num, "title": "MADE UP notice", "agency": "FERC", "action_type": "notice",
                        "significance": "6", "sector": "gas", "why": "old why", "text_status": status,
                        "abstract": "" if i else "", "first_paragraph": "p"})
            reads = os.path.join(d, "policy_reads.csv")
            with open(reads, "w", encoding="utf-8", newline="") as f:
                f.write("# MADE UP\n")
                w = csv.DictWriter(f, fieldnames=R.READ_COLS_S154, lineterminator="\n")
                w.writeheader()
                for num in ("2026-1", "2026-2", "2026-3"):
                    w.writerow({c: "" for c in R.READ_COLS_S154} | {
                        "event_id": f"policyread:federalregister:{num}", "event_date": "2026-01-01",
                        "action_event_id": f"federalregister:{num}", "plain_read": "old read", "affected_states": "TX"})
            ans = {"what_changes": {"text": "A made up rule takes effect.", "spans": ["The made up rule takes effect"]},
                   "who_affected": {"sectors": ["nuclear"], "isos": [], "states": ["ID", "TX"], "text": "x", "spans": ["Adams County, Idaho"]},
                   "direction": {"supply": "unclear", "demand": "unclear", "prices": "up", "buildout": "unclear", "spans": ["MADE UP notice"]},
                   "timeline": {"text": "", "spans": []},
                   "plain_read": {"text": "A made up rule. It takes effect.", "spans": ["The made up rule takes effect"]}}
            RC.save_answer(os.path.join(work, "answers", "reads", "a.json"), {
                "key": "federalregister:2026-1", "stop_reason": "end_turn", "answer": json.dumps(ans), "model": "MADE-UP-MODEL",
                "at": "2026-10-08T10:00:00Z", "text_file": tfile})
            RC.save_answer(os.path.join(work, "no_text", "b.json"), {"key": "federalregister:2026-3", "why": "source not reachable: HTTP 404"})
            RC.save_answer(os.path.join(work, "answers", "scores", "s.json"), {
                "key": "s", "stop_reason": "end_turn", "model": "MADE-UP-MODEL", "at": "2026-10-08T10:05:00Z", "kind": "title",
                "ids": ["federalregister:2026-1"],
                "answer": json.dumps({"results": [{"id": "federalregister:2026-1", "significance": 3, "sector": "gas", "one_line_why": "new why"},
                                                  {"id": "federalregister:2026-9", "significance": 9, "sector": "gas", "one_line_why": "not asked"}]})})
            scores = os.path.join(d, "scores.csv")
            with open(scores, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["event_id", "significance", "sector", "why", "model_id", "scored_at"])
                for i in ("federalregister:2026-1", "federalregister:2026-2", "federalregister:2026-3", "nrc:madeup"):
                    w.writerow([i, "6", "gas", "old why", "m", "2026-09-01T00:00:00Z"])
            keep = RC.SCORES
            try:
                RC.SCORES = scores
                S = RC.load_modules()
                args = type("A", (), {"reads": reads, "evidence": None})()
                with open(os.devnull, "w") as null:
                    old, sys.stdout = sys.stdout, null
                    try:
                        RC.build(args, RC.read_events(acts), RC.read_events(reads), work, S, type("L", (), {"close": quiet})())
                    finally:
                        sys.stdout = old
            finally:
                RC.SCORES = keep
            out = {r["action_event_id"]: r for r in csv.DictReader(l for l in open(os.path.join(work, "out", "policy_reads.csv"), encoding="utf-8") if not l.startswith("#"))}
            sc = {r["event_id"]: r for r in csv.DictReader(open(os.path.join(work, "out", "scores.csv"), encoding="utf-8"))}
            ch = list(csv.DictReader(open(os.path.join(work, "out", "recheck_s157_changes.csv"), encoding="utf-8")))
        a, b, c = (out[f"federalregister:2026-{i}"] for i in (1, 2, 3))
        self.assertEqual((a["recheck"], a["rechecked_at"]), ("rechecked", "2026-10-08T10:00:00Z"))
        self.assertEqual(a["affected_states"], "ID", "the state the text does not name is taken out")
        self.assertEqual(a["affected_sectors"], "", "nuclear: its keyword is not in the text")
        self.assertEqual(a["direction_prices"], "unclear")
        self.assertEqual((b["recheck"], b["plain_read"]), ("not rechecked", "old read"), "a row the money did not reach is as it was, and says so")
        self.assertEqual((c["recheck"], c["plain_read"]), ("source not reachable", "old read"))
        self.assertEqual((sc["federalregister:2026-1"]["significance"], sc["federalregister:2026-1"]["model_recheck"]), ("3", "rechecked"))
        self.assertEqual(sc["federalregister:2026-2"]["model_recheck"], "not rechecked")
        self.assertEqual(sc["federalregister:2026-3"]["model_recheck"], "source not reachable")
        self.assertEqual((sc["nrc:madeup"]["model_recheck"], sc["nrc:madeup"]["significance"]), ("not rechecked", "6"))
        self.assertNotIn("federalregister:2026-9", sc, "an id the batch was not asked about is not taken")
        before = {(x["kind"], x["event_id"], x["field"]): (x["before"], x["after"]) for x in ch}
        self.assertEqual(before[("score", "federalregister:2026-1", "significance")], ("6", "3"))
        self.assertEqual(before[("score", "federalregister:2026-1", "why")], ("old why", "new why"))
        self.assertEqual(before[("read", "federalregister:2026-1", "affected_states")], ("TX", "ID"))


class TagRule(unittest.TestCase):
    def test_version_3_reads_the_first_paragraph_and_the_site_holds_the_same_file(self):
        rules = pat.load_rules()
        self.assertEqual(rules["version"], "3")
        self.assertEqual(rules["fields_matched"], ["title", "abstract", "first_paragraph"])
        self.assertIn("Treasury", rules["agencies_in_scope"]["federal"])
        self.assertIn("IRS", rules["agencies_in_scope"]["federal"])
        with open(os.path.join(ROOT, "warehouse", "config", "policy_tag_rules.json"), "rb") as f:
            a = f.read().replace(b"\r\n", b"\n")
        with open(os.path.join(SITE, "tag_rules.json"), "rb") as f:
            b = f.read().replace(b"\r\n", b"\n")
        self.assertEqual(a, b, "one rule file: the site's is a copy, byte for byte")

    def test_a_term_in_the_first_paragraph_tags_and_says_where(self):
        rules = pat.load_rules()
        row = {"agency": "FERC", "action_type": "notice", "title": "PJM Interconnection, L.L.C.; Notice of Filing", "abstract": "",
               "first_paragraph": "The filing sets terms for co-located load at a data center.", "docket": "Docket No. ER26-1-000"}
        hits = {h["tag"]: h for h in pat.tag_action(row, rules)}
        self.assertEqual(hits["large_load"]["matched_field"], "first_paragraph")
        self.assertNotIn("interconnection", hits, "the operator's own name is not a topic")
        row["first_paragraph"] += " The county board held a zoning hearing."
        self.assertEqual(pat.tag_action(row, rules), [], "nothing municipal is ever tagged")
        self.assertEqual(pat.tag_action(dict(row, first_paragraph=""), rules), [], "a row without the field is read on the other two")
        irs = {"agency": "IRS", "action_type": "notice", "title": "Beginning of Construction for the Clean Electricity Production Credit",
               "abstract": "Guidance under section 45Y of the tax code.", "first_paragraph": "", "docket": ""}
        self.assertIn("tax_credit", [h["tag"] for h in pat.tag_action(irs, rules)])

    def test_the_python_rule_gives_what_the_cases_say(self):
        path = os.path.join(FIX, "policy_tag_cases.json")
        if not os.path.exists(path):
            self.skipTest("the tag cases are not built yet")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        rules = pat.load_rules()
        self.assertEqual(d["rule_version"], rules["version"])
        self.assertGreater(len(d["cases"]), 200)
        for c in d["cases"]:
            self.assertEqual(pat.tag_action(c, rules), c["expect"], c["event_id"])
        with open(os.path.join(SITE, "action_tags.json"), encoding="utf-8") as f:
            site = json.load(f)
        tagged = {c["event_id"]: c["expect"] for c in d["cases"] if c["expect"]}
        self.assertEqual(site["tags"], tagged, "the site's file holds every tagged action, and the cases hold them all")
        self.assertEqual(site["rule_version"], rules["version"])
        for i in site["first_paragraph"]:
            self.assertTrue(any(h["matched_field"] == "first_paragraph" for h in site["tags"][i]))


class SiteFiles(unittest.TestCase):
    def read(self, name):
        with open(os.path.join(SITE, name), encoding="utf-8") as f:
            return json.load(f)

    def test_the_state_rows_have_the_agreed_shape_and_never_a_withheld_sentence(self):
        d = self.read("state_rules.json")
        keys = {"id", "date", "regulator", "regulator_key", "jurisdiction", "state", "docket", "title", "row_kind", "topics",
                "large_load", "status_as_worded", "status_class", "url", "page", "sentence", "sentence_withheld",
                "sentence_from", "sentence_kind", "flags", "terms_class", "read", "read_by", "read_model", "read_from", "grids",
                "all_grids", "why_here", "in_motion"}
        self.assertGreaterEqual(len(d["rows"]), 116)
        feeds = {r["key"] for r in self.read("refresh.json")["regulators"]}
        for r in d["rows"]:
            self.assertEqual(set(r), keys, r["id"])
            self.assertIn(r["regulator_key"], feeds)
            self.assertTrue(set(r["topics"]) <= set(d["topics"]) and r["topics"], r["id"])
            self.assertTrue(set(r["grids"]) <= set(rim.GRIDS))
            self.assertRegex(r["date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(r["url"].startswith("https://"))
            if r["terms_class"] in ("restricted", "not quoted"):
                self.assertIsNone(r["sentence"], r["id"])
                self.assertIsNone(r["status_as_worded"], r["id"])
                self.assertEqual(r["title"], "")
                self.assertTrue(r["sentence_withheld"])
            else:
                self.assertTrue(r["sentence"], r["id"])
            if r["read"] is not None:
                self.assertEqual(r["read_by"], "model")
                self.assertTrue(r["read_model"])
            shown = " ".join(str(r.get(k) or "") for k in ("title", "sentence", "read", "status_as_worded")).lower()
            for w in ("zoning", "city council", "county board"):
                self.assertNotIn(w, shown)
        self.assertEqual(d["rows"], sorted(d["rows"], key=lambda r: (r["date"], r["id"]), reverse=True))

    def test_each_regulator_has_its_list_or_the_exact_reason_it_is_not_asked(self):
        d = self.read("refresh.json")
        regs = {r["key"]: r for r in d["regulators"]}
        self.assertEqual(set(regs), {"ferc", "txpuc", "vascc", "puco", "iurc", "papuc", "ilcc", "gapsc", "azcc", "orpuc", "cpuc"})
        self.assertEqual(d["ceilings"], {"requests_a_day": 120, "seconds_between_requests_to_a_host": 1})
        for r in regs.values():
            if r["refreshed"]:
                self.assertTrue(r["list_url"] or r["list_name"], r["key"])
            else:
                self.assertTrue(r["reason"] and len(r["reason"]) > 40, r["key"])
        self.assertFalse(regs["puco"]["refreshed"])
        self.assertIn("reCAPTCHA", regs["puco"]["reason"])
        self.assertFalse(regs["ilcc"]["refreshed"])
        self.assertIn("no robots", regs["ilcc"]["reason"])
        self.assertTrue(any("ferc.gov" in x["host"] for x in regs["ferc"]["refused"]))

    def test_the_grids_file_and_miso_s_fixed_words(self):
        d = self.read("grids.json")
        self.assertEqual([g["key"] for g in d["grids"]], ["ercot", "pjm", "miso", "caiso", "nyiso", "isone", "spp"])
        self.assertEqual(d["paused"], {"miso": "paused while terms are reviewed"})

    def test_the_daily_step_never_writes_a_thinner_file_and_skips_without_the_tables(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(pms.daily(d, dt.date(2026, 10, 8), in_dirs=[d]), int(os.environ.get("ERW_SKIP_EXIT", "75")))
            self.assertEqual(os.listdir(d), [], "nothing is written without the tables")
        main_out = os.path.join(os.path.dirname(ROOT), "erw", "warehouse", "output")
        if not all(os.path.exists(os.path.join(main_out, t + ".csv")) for t in pms.DAILY_TABLES):
            self.skipTest("the large-load tables are not on this machine")
        with tempfile.TemporaryDirectory() as d:
            held = self.read("state_rules.json")
            fat = dict(held, rows=held["rows"] + [dict(held["rows"][0], id="madeup:extra")])   # MADE UP: one more row than the tables give
            with open(os.path.join(d, "state_rules.json"), "w", encoding="utf-8") as f:
                json.dump(fat, f)
            with self.assertRaises(RuntimeError):
                pms.daily(d, dt.date(2026, 10, 8), in_dirs=[main_out])
            with open(os.path.join(d, "state_rules.json"), encoding="utf-8") as f:
                self.assertEqual(len(json.load(f)["rows"]), len(fat["rows"]), "the fuller file is still there")

    def test_a_file_that_would_only_change_its_build_time_is_left(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.json")
            self.assertTrue(pms.write_whole(p, {"built_at_utc": "a", "as_of": "b", "rows": [1]}, keep_if_same=True))
            self.assertFalse(pms.write_whole(p, {"built_at_utc": "c", "as_of": "d", "rows": [1]}, keep_if_same=True))
            self.assertTrue(pms.write_whole(p, {"built_at_utc": "c", "as_of": "d", "rows": [1, 2]}, keep_if_same=True))
            with self.assertRaises(RuntimeError):
                pms.write_whole(p, {"x": "a" + EM + "b"})


class DailyRunAndFiles(unittest.TestCase):
    def test_the_two_steps_are_soft_steps_in_the_daily_run_and_the_workflow_commits_the_files(self):
        with open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8") as f:
            sh = f.read()
        a = sh.index('soft_step policy_monitor_refresh "$PYTHON" warehouse/connectors/policy_monitor_refresh.py')
        b = sh.index('soft_step policy_monitor_site "$PYTHON" warehouse/derived/policy_monitor_site.py --daily')
        self.assertLess(a, b, "the files are rebuilt after the refresh")
        with open(os.path.join(ROOT, ".github", "workflows", "daily-prices.yml"), encoding="utf-8") as f:
            self.assertIn("site/data/policy)", f.read())

    def test_no_live_page_s_table_is_written_by_the_new_steps(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = f.read()
        for t in ("large_load_rules", "large_load_rules_internal", "large_load_rule_reads", "policy_action_tags"):
            self.assertRegex(live, r"(?m)^\s+- " + t + r"\b", f"{t} is in a hold list: not loaded")
        with open(os.path.join(ROOT, "warehouse", "derived", "policy_monitor_site.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("write_csv", src)
        self.assertNotIn("write_snapshot", src)
        self.assertNotIn("import requests", src, "the builder makes no request")

    def test_no_em_dash_and_no_personal_address_in_this_session_s_files(self):
        for parts in MINE:
            path = os.path.join(ROOT, *parts)
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(EM, text, path)
            self.assertIsNone(re.search(r"[\w.]+@(gmail|yahoo|outlook|hotmail)\.", text), path)

    def test_the_method_note_states_what_the_owner_asked_it_to(self):
        path = os.path.join(ROOT, "docs", "methods", "policy_monitor.md")
        if not os.path.exists(path):
            self.skipTest("the Method note is not written yet")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for words in ("nothing municipal", "a model's", "not rechecked", "reCAPTCHA", "no robots", "HTTP 429",
                      "first paragraph", "version 3", "120 requests"):
            self.assertIn(words, text, words)


if __name__ == "__main__":
    unittest.main()
