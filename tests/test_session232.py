"""Session 232: the daily chart in the Digest, chosen and drawn by code.

The rule (records and first negatives first, then strength; never a chart a Digest has shown; else the watch list's
largest change; else no section), the fact written from the flag's own numbers, the picture, the section's lines on the
site and in the email, the candidates read with a wait, the migration's internal table, and the two machines' wiring.
No network and no warehouse table: the candidates are a fixture of real ones (tests/fixtures/session232/
candidates.json: the scan of 13 October 2026, three flags and two watch changes as the data machine published them).
"""
import json
import os
import re
import struct
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
sys.path.insert(0, FIND)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import daily_chart  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session232", "candidates.json")
EM = chr(0x2014)


def candidates():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)["candidates"]


# session 267: the fixture's record is 34 percent past the old one, so the guard (daily_chart.must_wait) holds it on the
# run that first sees it. These tests pin the rule as session 232 wrote it, on the run after the hold: its key is waited.
def waited():
    return {c["key"] for c in candidates() if (daily_chart.record_jump(c) or 0) > daily_chart.RECORD_JUMP}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def flag(rule, strength, fid):
    return {"id": fid, "rule": rule, "strength": strength}


class TheRule(unittest.TestCase):
    def test_records_and_first_negatives_come_first_then_strength(self):
        got = daily_chart.rank([flag("spike", 27.9, "a"), flag("record", 0.6, "b"), flag("weekly", 1.5, "c"), flag("negative", 0.9, "d"),
                                flag("record", 9.8, "e"), flag("pair", 3.0, "f")])
        self.assertEqual([f["id"] for f in got], ["e", "d", "b", "a", "f", "c"])

    def test_ties_go_by_id(self):
        self.assertEqual([f["id"] for f in daily_chart.rank([flag("record", 1.0, "z"), flag("record", 1.0, "a")])], ["a", "z"])

    def test_the_strongest_flag_not_shown_before_is_chosen(self):
        c = candidates()
        flags = [x for x in c if x["source"] == "scanner"]
        got, why = daily_chart.choose(c, set(), waited=waited())
        self.assertEqual(got["key"], flags[0]["key"])
        self.assertIn("strongest", why)
        got, _ = daily_chart.choose(c, {flags[0]["key"]}, waited=waited())
        self.assertEqual(got["key"], flags[1]["key"])

    def test_with_every_flag_shown_the_watch_list_is_next(self):
        c = candidates()
        flags = {x["key"] for x in c if x["source"] == "scanner"}
        watch = [x for x in c if x["source"] == "watch"]
        got, why = daily_chart.choose(c, flags)
        self.assertEqual(got["key"], watch[0]["key"])
        self.assertIn("watch list", why)
        got, why = daily_chart.choose(watch, set())
        self.assertIn("flagged nothing", why)

    def test_nothing_left_is_no_chart_and_a_reason(self):
        c = candidates()
        got, why = daily_chart.choose(c, {x["key"] for x in c})
        self.assertIsNone(got)
        self.assertIn("shown in an earlier Digest", why)
        got, why = daily_chart.choose([], set())
        self.assertIsNone(got)
        self.assertIn("flagged nothing", why)

    def test_the_fixture_is_ranked_as_the_rule_says(self):
        flags = [x["flag"] for x in candidates() if x["source"] == "scanner"]
        self.assertEqual([f["id"] for f in daily_chart.rank(flags)], [f["id"] for f in flags])
        watch = [x for x in candidates() if x["source"] == "watch"]
        self.assertEqual(watch, sorted(watch, key=lambda c: (-c["score"], -c["z"], c["key"])))


class OnlyPublicTables(unittest.TestCase):
    def test_a_table_that_is_not_public_or_needs_a_license_is_never_a_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "coverage.csv"), "w", encoding="utf-8") as f:
                f.write("table,iso,license\nopen_table,EIA,public\ninternal_table,EIA,internal\nheld_table,EIA,public\nspp_table,SPP,public\n")
            with open(os.path.join(d, "license_status.csv"), "w", encoding="utf-8") as f:
                f.write("table,status\nheld_table,license needed\n")
            self.assertEqual(daily_chart.public_tables(d), {"open_table"})
            base = candidates()[0]["flag"]
            flags = [dict(base, id=f"scan-record-{i:012x}", table=t) for i, t in enumerate(("open_table", "internal_table", "held_table", "spp_table"))]
            flags.append(dict(base, id="scan-record-00000000000f", table="open_table", series=dict(base["series"], entity="nyiso:N.Y.C.")))
            got = daily_chart.from_flags(flags, lambda fl: {"title": "T", "subtitle": "s"}, d)
            self.assertEqual([(c["table"], c["flag"]["series"]["entity"]) for c in got], [("open_table", base["series"]["entity"])])
            self.assertEqual(got[0]["rank"], 1)
        self.assertEqual(daily_chart.HELD, ("nyiso", "spp"))


class TheFact(unittest.TestCase):
    def test_every_number_of_a_fact_is_one_the_flag_holds(self):
        for c in candidates():
            if c["source"] != "scanner":
                continue
            fl = c["flag"]
            self.assertEqual(c["fact"], daily_chart.fact_from_flag(fl))
            pool = [fl["value"], fl["threshold"]["value"], fl["history"]["points"]] + [v for v in fl["compared"].values() if isinstance(v, (int, float))]
            pool += list(fl["threshold"]["config"].values())
            shown = set()
            for v in pool:
                for nd in (0, 1, 2, 4):
                    shown.add(f"{abs(float(v)):,.{nd}f}")
            text = re.sub(r"\d{1,2} [A-Z][a-z]+ \d{4}|[A-Z][a-z]+ \d{4}", "", c["fact"])      # dates are checked below
            for n in re.findall(r"\d[\d,]*\.?\d*", text):
                if n.rstrip(".") in ("99", "7"):                                             # "99th percentile", "7 days"
                    continue
                self.assertIn(n.rstrip("."), shown, f"{n} in {c['fact']!r}")
            self.assertNotIn(EM, c["fact"])

    def test_a_monthly_record_is_dated_by_its_month(self):
        rec = next(c for c in candidates() if c["source"] == "scanner" and c["flag"]["rule"] == "record")
        fl = rec["flag"]
        y, m, _ = fl["date"].split("-")
        self.assertIn(f"in {daily_chart.MONTHS[int(m) - 1]} {y}", rec["fact"])
        self.assertIn("The record until now was", rec["fact"])

    def test_a_series_is_named_plainly_only_where_its_codes_are_known(self):
        n = daily_chart.plain_name
        self.assertEqual(n("eia_state_generation_monthly", {"entity": "eia:generation:WY:NG", "variable": "net_generation"}, "raw"),
                         "Net generation from natural gas in Wyoming")
        self.assertEqual(n("eia_retail_electricity_prices", {"entity": "eia:retail_price:IA:IND", "variable": "retail_price"}, "raw"),
                         "Retail electricity price in Iowa, industrial")
        self.assertEqual(n("caiso_as_prices", {"entity": "caiso:AS_CAISO_EXP", "variable": "as_price_dam_nr"}, "raw"),
                         "CAISO day-ahead non-spinning reserve price (AS_CAISO_EXP)")
        self.assertEqual(n("eia_state_generation_monthly", {"entity": "eia:generation:WY:XYZ", "variable": "net_generation"}, "raw"), "raw")
        self.assertEqual(n("some_table", {"entity": "a:b", "variable": "c"}, "a:b c"), "a:b c")


class TheSection(unittest.TestCase):
    def test_it_draws_the_picture_keeps_the_choice_and_writes_the_lines(self):
        c = candidates()
        with tempfile.TemporaryDirectory() as d:
            said = []
            L = daily_chart.section("2026-10-13", said.append, chart_dir=d, candidates=c, waited=waited())
            self.assertEqual(L[1], "## ERW's Chart of the Day")
            self.assertTrue(L[3].startswith("![") and L[3].endswith("](charts/2026-10-13.png)"))
            self.assertEqual(L[5], c[0]["fact"])
            self.assertIn(f"`{c[0]['table']}`", L[7])
            self.assertIn(f"(/data#{c[0]['table']})", L[7])
            self.assertIn("not by a person or a model", L[7])
            self.assertNotIn(EM, "\n".join(L))
            with open(os.path.join(d, "2026-10-13.png"), "rb") as f:
                head = f.read(24)
            self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", head[16:24]), (1200, 880))
            with open(os.path.join(d, "2026-10-13.json"), encoding="utf-8") as f:
                rec = json.load(f)
            self.assertEqual(rec["key"], c[0]["key"])
            self.assertEqual(rec["fact"], c[0]["fact"])
            self.assertNotIn("proof", rec)
            self.assertTrue(any("daily chart" in m and c[0]["key"] in m for m in said))

    def test_the_next_day_shows_the_next_flag_and_a_rerun_shows_the_same(self):
        c = candidates()
        with tempfile.TemporaryDirectory() as d:
            daily_chart.section("2026-10-13", lambda m: None, chart_dir=d, candidates=c, waited=waited())
            daily_chart.section("2026-10-14", lambda m: None, chart_dir=d, candidates=c, waited=waited())
            daily_chart.section("2026-10-13", lambda m: None, chart_dir=d, candidates=c, waited=waited())
            keys = {}
            for day in ("2026-10-13", "2026-10-14"):
                with open(os.path.join(d, f"{day}.json"), encoding="utf-8") as f:
                    keys[day] = json.load(f)["key"]
            self.assertEqual(keys["2026-10-13"], c[0]["key"])
            self.assertEqual(keys["2026-10-14"], c[1]["key"])

    def test_a_shadow_copy_of_the_day_chooses_what_the_day_chose(self):
        c = candidates()
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as shadow:
            daily_chart.section("2026-10-13", lambda m: None, chart_dir=d, candidates=c, waited=waited())
            self.assertEqual(daily_chart.used_keys(d, but="2026-10-13"), set())
            daily_chart.section("2026-10-13", lambda m: None, chart_dir=shadow, candidates=c, used=daily_chart.used_keys(d, but="2026-10-13"), waited=waited())
            with open(os.path.join(shadow, "2026-10-13.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["key"], c[0]["key"])
        self.assertIn("used=daily_chart.used_keys(but=digest_date)", src("warehouse", "news", "brief.py"))

    def test_a_proof_is_not_counted_as_shown(self):
        c = candidates()
        with tempfile.TemporaryDirectory() as d:
            daily_chart.section("2026-10-12", lambda m: None, chart_dir=d, candidates=c, proof=True, waited=waited())
            self.assertEqual(daily_chart.used_keys(d), set())
            daily_chart.section("2026-10-13", lambda m: None, chart_dir=d, candidates=c, waited=waited())
            self.assertEqual(daily_chart.used_keys(d), {c[0]["key"]})

    def test_nothing_to_show_is_no_section_and_a_logged_reason(self):
        with tempfile.TemporaryDirectory() as d:
            said = []
            self.assertEqual(daily_chart.section("2026-10-13", said.append, chart_dir=d, candidates=[]), [])
            self.assertTrue(any("section omitted" in m for m in said))
            self.assertEqual(os.listdir(d), [])

    def test_a_failure_is_no_section_never_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            said = []
            bad = [dict(candidates()[0], card={"title": "T", "subtitle": "s", "chart": {"kind": "no such kind", "x": [], "series": []}})]
            self.assertEqual(daily_chart.section("2026-10-13", said.append, chart_dir=d, candidates=bad, waited=waited()), [])
            self.assertTrue(any("omitted" in m for m in said))
            self.assertFalse(os.path.exists(os.path.join(d, "2026-10-13.json")))


class Answer:
    def __init__(self, rows, status=200):
        self.status_code, self._rows, self.text = status, rows, ""

    def json(self):
        return self._rows


class TheCandidatesAcrossTwoMachines(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock
        self.lock, self.saved = lock, lock.env
        lock.env = lambda name: {"SUPABASE_URL": "https://example.invalid", "SUPABASE_SERVICE_KEY": "k"}.get(name, "")

    def tearDown(self):
        self.lock.env = self.saved

    def test_todays_row_is_used_at_once(self):
        row, why = daily_chart.read_candidates("2026-10-13", 0, get=lambda *a, **k: Answer([{"day": "2026-10-13", "computed_at": "t", "candidates": [1]}]))
        self.assertEqual(row["candidates"], [1])
        self.assertIn("the scan of 2026-10-13", why)

    def test_it_waits_for_today_and_then_takes_yesterday(self):
        clock = {"t": 0.0}
        slept = []

        def sleep(s):
            slept.append(s)
            clock["t"] += s
        row, why = daily_chart.read_candidates("2026-10-13", 60, get=lambda *a, **k: Answer([{"day": "2026-10-12", "computed_at": "t", "candidates": [2]}]),
                                               sleep=sleep, clock=lambda: clock["t"])
        self.assertEqual(row["day"], "2026-10-12")
        self.assertEqual(sum(slept), 60)
        self.assertIn("was not there after 60 seconds", why)

    def test_today_arriving_during_the_wait_is_taken(self):
        calls = {"n": 0}

        def get(*a, **k):
            calls["n"] += 1
            return Answer([{"day": "2026-10-13", "computed_at": "t", "candidates": [3]}] if calls["n"] >= 3 else [])
        row, _ = daily_chart.read_candidates("2026-10-13", 300, get=get, sleep=lambda s: None, clock=lambda: 0.0)
        self.assertEqual(row["candidates"], [3])
        self.assertEqual(calls["n"], 3)

    def test_no_row_and_a_refusal_are_none_with_the_reason(self):
        row, why = daily_chart.read_candidates("2026-10-13", 0, get=lambda *a, **k: Answer([]))
        self.assertIsNone(row)
        self.assertIn("no candidates", why)
        row, why = daily_chart.read_candidates("2026-10-13", 0, get=lambda *a, **k: Answer([], 404))
        self.assertIsNone(row)
        self.assertIn("HTTP 404", why)

    def test_a_day_is_one_row_replaced_by_a_later_scan(self):
        seen = {}

        def post(url, params=None, data=None, headers=None, timeout=None):
            seen.update(url=url, params=params, body=json.loads(data), headers=headers)
            return Answer([], 201)
        self.assertTrue(daily_chart.publish("2026-10-13", candidates()[:1], "1.1.0", "m", post=post))
        self.assertTrue(seen["url"].endswith("/rest/v1/daily_chart_candidates"))
        self.assertEqual(seen["params"], {"on_conflict": "day"})
        self.assertIn("resolution=merge-duplicates", seen["headers"]["Prefer"])
        self.assertEqual(seen["body"]["day"], "2026-10-13")
        self.assertEqual(len(seen["body"]["candidates"]), 1)

    def test_the_scan_publishes_and_is_never_failed_by_it(self):
        text = src("warehouse", "analysis", "findings", "findings_scanner.py")
        body = text[text.index("def daily_request("):text.index("HISTORIES = ")]
        self.assertIn("extras=extras", body)
        self.assertIn("daily_chart.publish_day(", body)
        self.assertLess(body.index("load_drafts(drafts, log=log)"), body.index("daily_chart.publish_day("))
        self.assertIn("except Exception", body[body.index("daily_chart.publish_day("):])
        said = []
        self.lock.env = lambda name: ""                    # no key on the machine: said, not raised
        with tempfile.TemporaryDirectory() as d:
            n = daily_chart.publish_day("2026-10-13", candidates()[:1], d, "1.1.0", said.append, now="2026-10-13T12:00:00")
            self.assertEqual(n, 0)
            self.assertTrue(os.path.exists(os.path.join(d, "daily_chart.json")))
        self.assertTrue(any("NOT published" in m for m in said))


class TheDigestAndTheEmail(unittest.TestCase):
    def test_the_section_sits_after_the_numbers_and_before_the_fun_fact(self):
        text = src("warehouse", "news", "brief.py")
        a, b, c = text.index('"## ERW\'s Numbers Today"'), text.index("L += daily_chart_section(digest_date, log, args.out)"), text.index("L += fun_fact_section(digest_date, log)")
        self.assertLess(a, b)
        self.assertLess(b, c)

    def test_a_check_run_touches_no_file_of_docs(self):
        text = src("warehouse", "news", "brief.py")
        body = text[text.index("def daily_chart_section("):text.index("def main(")]
        self.assertIn('os.path.join(os.path.dirname(os.path.abspath(out)), "charts")', body)
        self.assertIn("wait=0", body)

    def test_the_email_shows_the_picture_inline_at_600_pixels(self):
        import email_digest
        c = candidates()[0]
        lines = ["# ERW's Energy Digest, 2026-10-13", ""] + daily_chart.markdown("2026-10-13", c) + ["", "## ERW's Fun Fact", "", "x"]
        body = email_digest.section(lines, ("## ERW's Chart of the Day",))
        text, html = email_digest.block(body, img_base="docs/digest")
        self.assertIn(f'src="{email_digest.RAW}/docs/digest/charts/2026-10-13.png"', html)
        self.assertIn('width="600"', html)
        self.assertTrue(any(c["fact"] in t for t in text))
        self.assertIn('("## ERW\'s Chart of the Day", "## Chart of the day")', src("warehouse", "news", "email_digest.py"))

    def test_the_site_serves_the_picture(self):
        self.assertIn("/digest-charts/${m[1]}", src("site", "lib", "markdown.ts"))
        self.assertIn(r"docs\/digest\/charts\/(\d{4}-\d{2}-\d{2}\.png)", src("site", "lib", "markdown.ts"))
        build = src("site", "scripts", "build-content.mjs")
        self.assertIn('path.join(here, "..", "public", "digest-charts")', build)
        self.assertIn("/public/digest-charts/", src("site", ".gitignore"))

    def test_the_daily_commit_carries_the_charts(self):
        self.assertIn("docs/digest ", src(".github", "workflows", "daily-prices.yml"))   # the whole folder, charts with it


class TheInternalTable(unittest.TestCase):
    def test_the_table_is_internal_and_has_a_rollback(self):
        sql = src("warehouse", "supabase", "migrations", "030_daily_chart.sql")
        self.assertIn("create table if not exists public.daily_chart_candidates", sql)
        self.assertIn("alter table public.daily_chart_candidates enable row level security", sql)
        self.assertIn("revoke all on public.daily_chart_candidates from public, anon, authenticated", sql)
        self.assertNotIn("create policy", sql)
        self.assertIn("drop table if exists public.daily_chart_candidates", src("warehouse", "supabase", "rollbacks", "030_daily_chart.sql"))
        self.assertIn('"daily_chart_candidates": "blocked"', src("warehouse", "supabase", "verify_rls.py"))


class NoModelAnywhere(unittest.TestCase):
    def test_the_chart_and_its_words_call_no_model(self):
        for f in ("daily_chart.py", "card_image.py"):
            text = src("warehouse", "analysis", "findings", f)
            for word in ("anthropic", "llm.client", "messages.create"):
                self.assertNotIn(word, text, f)


if __name__ == "__main__":
    unittest.main()
