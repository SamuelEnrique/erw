"""Session 233: the weekly hunt for deeper findings.

The library's three tests on made-up yearly series (the series are test inputs, never data), what counts as news, which
regions may be drafted, a draft's card and its six files (the Python mirror is run on the draft's own CSV), the hunt's
caps and memory, the loader, the internal table's new column and function, the review page's files and Roundup button,
and the Saturday task. No network and no warehouse table.
"""
import base64
import csv
import datetime as dt
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
sys.path.insert(0, FIND)
import hunt  # noqa: E402
import run_finding  # noqa: E402

EM = chr(0x2014)
P = dict(name="test_pattern", module="negative_prices_west", sweep=None, region_col="hub", year_col="year", filter=None, measure="share_pct",
         n_col="n_hours", n_floor=8000, unit="percent of hours", decimals=2, change_threshold=1.0, title="HOURS WITH A PRICE BELOW ZERO",
         label="share of the year's hours with a real-time price below zero")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def series(values, first=2019, n=8760):
    return {str(first + i): (v, n) for i, v in enumerate(values)}


class TheThreeTests(unittest.TestCase):
    def test_a_steady_rise_passes_all_three(self):
        c = hunt.test_claim(series([1.0, 2.0, 2.5, 3.0, 4.0, 5.0]), P, 2026)
        self.assertTrue(c["passed"])
        self.assertEqual((c["first_year"], c["last_year"], c["direction"]), ("2019", "2024", "up"))
        self.assertEqual(c["change"], 4.0)
        self.assertEqual((c["years_held"], c["years_after"]), (5, 5))
        self.assertEqual([t["name"] for t in c["tests"]], ["holds in more than one year", "survives a change of window", "sample large enough"])

    def test_one_year_on_its_side_is_not_more_than_one_year(self):
        c = hunt.test_claim(series([3.0, 2.0, 1.0, 2.5, 4.0]), P, 2026)
        t = {x["name"]: x for x in c["tests"]}
        self.assertFalse(t["holds in more than one year"]["passed"])
        self.assertIn("1 of the 4 full years after 2019", t["holds in more than one year"]["words"])
        self.assertFalse(c["passed"])

    def test_a_change_that_turns_when_the_window_moves_fails(self):
        c = hunt.test_claim(series([1.0, 6.0, 5.5, 5.2, 5.0]), P, 2026)            # up from 2019, down from 2020
        t = {x["name"]: x for x in c["tests"]}
        self.assertTrue(t["holds in more than one year"]["passed"])
        self.assertFalse(t["survives a change of window"]["passed"])
        self.assertFalse(c["passed"])

    def test_fewer_than_four_full_years_cannot_move_the_window(self):
        c = hunt.test_claim(series([1.0, 2.0, 3.0]), P, 2026)
        t = {x["name"]: x for x in c["tests"]}
        self.assertFalse(t["survives a change of window"]["passed"])
        self.assertIn("four are needed", t["survives a change of window"]["words"])

    def test_a_thin_sample_fails(self):
        c = hunt.test_claim(series([1.0, 2.0, 3.0, 4.0, 5.0], n=5000), P, 2026)
        t = {x["name"]: x for x in c["tests"]}
        self.assertFalse(t["sample large enough"]["passed"])
        self.assertIn("the floor is 8,000", t["sample large enough"]["words"])

    def test_the_year_under_way_and_a_part_year_are_not_full_years(self):
        s = {"2018": (9.0, 2900), "2019": (1.0, 8760), "2020": (2.0, 8784), "2021": (3.0, 8760), "2022": (4.0, 8760), "2026": (99.0, 8760)}
        self.assertEqual(hunt.full_years(s, P, 2026), ["2019", "2020", "2021", "2022"])
        c = hunt.test_claim(s, P, 2026)
        self.assertEqual((c["first_year"], c["last_year"]), ("2019", "2022"))

    def test_no_claim_without_two_full_years_or_without_a_change(self):
        self.assertIsNone(hunt.test_claim(series([1.0]), P, 2026))
        self.assertIsNone(hunt.test_claim(series([2.0, 3.0, 2.0]), P, 2026))
        self.assertIsNone(hunt.test_claim({}, P, 2026))

    def test_strength_is_the_change_in_typical_yearly_moves(self):
        c = hunt.test_claim(series([1.0, 2.0, 3.0, 4.0, 5.0]), P, 2026)
        self.assertAlmostEqual(c["typical_move"], 1.4826)
        self.assertAlmostEqual(c["strength"], round(4.0 / 1.4826, 4))


class WhatIsNews(unittest.TestCase):
    def setUp(self):
        self.c = hunt.test_claim(series([1.0, 2.0, 2.5, 3.0, 4.0, 5.0]), P, 2026)

    def test_a_claim_never_drafted_is_new(self):
        self.assertIn("new", hunt.news("k", self.c, P, {}))

    def test_the_same_claim_again_is_not_news(self):
        self.assertIsNone(hunt.news("k", self.c, P, {"k": {"last_year": "2024", "change": 4.0}}))
        self.assertIsNone(hunt.news("k", self.c, P, {"k": {"last_year": "2024", "change": 3.2}}))      # moved 0.8, threshold 1.0

    def test_a_change_past_the_threshold_or_a_newer_year_is(self):
        self.assertIn("moved by 1.50", hunt.news("k", self.c, P, {"k": {"last_year": "2024", "change": 2.5}}))
        self.assertIn("a newer last full year", hunt.news("k", self.c, P, {"k": {"last_year": "2023", "change": 4.0}}))


class WhichRegions(unittest.TestCase):
    def test_a_grid_that_needs_a_license_or_is_held_is_never_drafted(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "license_status.csv"), "w", encoding="utf-8") as f:
                f.write("table,status,from,publishers\na,license needed,2026-10-20,ISO-NE; MISO\nb,ok,,ERCOT\n")
            self.assertEqual(hunt.blocked_grids(d), {"isone", "miso", "nyiso", "spp"})
        blocked = hunt.blocked_grids()
        self.assertTrue({"nyiso", "spp"} <= blocked)
        self.assertNotIn("ercot", blocked)

    def test_a_region_names_its_grid(self):
        self.assertEqual([hunt.grid_of(r) for r in ("HB_WEST", "ercot_west", "spp_north", "caiso", "ERCOT")], ["ercot", "ercot", "spp", "caiso", "ercot"])

    def test_a_draft_names_only_its_own_grids_tables(self):
        t = ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "nyiso_rtm_zone_prices", "isone_zone_prices_history", "eia_fuel_spot_prices"]
        self.assertEqual(hunt.region_tables(t, "ercot"), ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "eia_fuel_spot_prices"])


class TheLibrary(unittest.TestCase):
    def test_every_pattern_reads_a_finding_and_columns_that_finding_writes(self):
        self.assertEqual(len({p["name"] for p in hunt.PATTERNS}), len(hunt.PATTERNS))
        for p in hunt.PATTERNS:
            if p.get("fn"):                              # session 251: a measure of hunt_measures.py, held by tests/test_session251.py
                continue
            self.assertIn(p["module"], run_finding.FINDINGS, p["name"])
            card = json.loads(src("site", "data", "findings", p["module"] + ".json"))
            with open(os.path.join(ROOT, "site", "public", "findings", card["downloads"]["csv"]), encoding="utf-8") as f:
                cols = next(csv.reader(ln for ln in f if not ln.startswith("#")))
            for c in [p["year_col"], p["measure"], p["n_col"]] + ([p["region_col"]] if p["region_col"] else []) + list((p.get("filter") or {})):
                self.assertIn(c, cols, f"{p['name']}: {c}")

    def test_every_finding_is_a_pattern_or_says_why_it_is_not_yet(self):
        covered = {p["module"] for p in hunt.PATTERNS} | set(hunt.NOT_YET)
        self.assertEqual(set(run_finding.FINDINGS) - covered, set())

    def test_the_measure_by_year_is_read_from_the_findings_own_rows(self):
        card = json.loads(src("site", "data", "findings", "negative_prices_west.json"))
        with open(os.path.join(ROOT, "site", "public", "findings", card["downloads"]["csv"]), encoding="utf-8") as f:
            rows = list(csv.DictReader(ln for ln in f if not ln.startswith("#")))
        npw = next(p for p in hunt.PATTERNS if p["name"] == "negative_prices")
        s = hunt.yearly(rows, npw, "ercot_west")
        self.assertAlmostEqual(s["2019"][0], card["numbers"]["ercot_west_first_share"])
        self.assertEqual(s["2019"][1], 8760.0)
        self.assertEqual(hunt.region_words(npw, "ercot_west", rows), "ERCOT West")

    def test_a_years_first_row_is_taken_and_a_year_written_as_a_float_is_read(self):
        rows = [{"hub": "a", "year": 2019.0, "share_pct": 1.5, "n_hours": 8760}, {"hub": "a", "year": 2019.0, "share_pct": 9.9, "n_hours": 1},
                {"hub": "b", "year": 2019, "share_pct": 7.0, "n_hours": 8760}, {"hub": "a", "year": "all", "share_pct": 3.0, "n_hours": 8760},
                {"hub": "a", "year": 2020, "share_pct": float("nan"), "n_hours": 8760}]
        self.assertEqual(hunt.yearly(rows, P, "a"), {"2019": (1.5, 8760.0)})


def a_draft(d, values=(1.0, 2.0, 2.5, 3.0, 4.0, 5.0), region="ercot_west"):
    s = series(list(values))
    c = hunt.test_claim(s, P, 2026)
    return hunt.build_draft(P, region, "ERCOT West", s, c, "new: this pattern had not been drafted for this region", {}, ["ercot_all_hub_prices_history", "nyiso_rtm_zone_prices"], d), s, c


class ADraft(unittest.TestCase):
    def test_the_row_is_one_the_review_list_takes(self):
        with tempfile.TemporaryDirectory() as d:
            row, _, c = a_draft(d)
            self.assertRegex(row["id"], r"^scan-hunt-[0-9a-f]{12}$")
            self.assertEqual((row["rule"], row["flag_date"], row["value"]), ("hunt", "2024-12-31", 4.0))
            self.assertEqual(row["flag_key"], "hunt|negative_prices_west|test_pattern|ercot_west")
            card = row["card"]
            self.assertEqual((card["card_id"], card["draft"], card["why"], card["chart"]["kind"]), (row["id"], True, "", "flag_line"))
            self.assertEqual(card["chart"]["x"], c["years"])
            self.assertEqual(card["chart"]["mark"], {"x": "2024", "value": 5.0, "label": "the last full year"})
            self.assertEqual(len(card["callouts"]), 3)
            self.assertIn("not reviewed", card["footnote"])
            self.assertIn("it does not say what caused it", card["footnote"])
            self.assertEqual(card["scanner"]["rule"], "hunt")
            self.assertNotIn("nyiso", card["source_line"])
            self.assertEqual(card["numbers"]["change"], 4.0)
            json.dumps(row["card"], allow_nan=False)
            self.assertNotIn(EM, json.dumps(row, ensure_ascii=False))

    def test_the_fact_and_the_caption_hold_the_claims_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            row, _, _ = a_draft(d)
            card = row["card"]
            self.assertEqual(card["subtitle"], "ERCOT West: share of the year's hours with a real-time price below zero, 5.00 percent of hours in 2024, "
                                               "up from 1.00 percent of hours in 2019. The direction holds in 5 of the 5 full years after 2019.")
            cap = card["hunt"]["caption"]
            for piece in ("2019: 1.00 percent of hours. 2024: 5.00 percent of hours.", "A change of +4.00 percent of hours.", "Checked three ways",
                          "5 of the 5 full years after 2019 lie above 2019's value", "the floor is 8,000", "Energy Research Warehouse (ERW)"):
                self.assertIn(piece, cap)

    def test_the_six_files_and_the_two_pictures_sizes(self):
        with tempfile.TemporaryDirectory() as d:
            row, _, _ = a_draft(d)
            did, files = row["id"], row["files"]
            self.assertEqual(sorted(files), sorted(row["card"]["hunt"]["files"]))
            self.assertEqual(sorted(f[len(did):] for f in files), sorted([".csv", ".do", ".py", "_1200x627.png", "_1080x1080.png", "_caption.txt"]))
            for name, size in ((f"{did}_1200x627.png", (1200, 627)), (f"{did}_1080x1080.png", (1080, 1080))):
                self.assertEqual(files[name]["kind"], "png")
                raw = base64.b64decode(files[name]["content"])
                self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", raw[16:24]), size)
            do = files[f"{did}.do"]["content"]
            self.assertNotIn("///", do)
            self.assertIn(f'import delimited "{did}.csv", varnames(5) rowrange(6) stringcols(_all) clear', do)
            self.assertIn("destring value, replace force", do)
            self.assertEqual(files[f"{did}.csv"]["content"].splitlines()[4], "region,year,value,n_observations,full_year")
            for f in os.listdir(d):
                self.assertTrue(f.startswith(did))

    def test_the_python_mirror_recomputes_the_claim_from_the_drafts_own_csv(self):
        with tempfile.TemporaryDirectory() as d:
            row, _, _ = a_draft(d)
            did = row["id"]
            r = subprocess.run([sys.executable, os.path.join(d, did + ".py"), os.path.join(d, did + ".csv")], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("claim: 1.0 in 2019, 5.0 in 2024; change 4.0", r.stdout)
            self.assertEqual(r.stdout.count(": pass"), 3)


class TheHunt(unittest.TestCase):
    def setUp(self):
        self.saved = (hunt.PATTERNS, hunt.run_pattern)
        self.d = tempfile.TemporaryDirectory()

    def tearDown(self):
        hunt.PATTERNS, hunt.run_pattern = self.saved
        self.d.cleanup()

    def fake(self, by_pattern):
        def run_pattern(Pn, in_dir, this_year, blocked, log=print, compute=None):
            out = []
            for region, values in by_pattern[Pn["name"]]:
                s = series(values)
                c = hunt.test_claim(s, Pn, this_year)
                why = None if c is None else (None if c["passed"] else "failed: " + "; ".join(t["name"] for t in c["tests"] if not t["passed"]))
                out.append((region, region, s, c, why if c is not None else "no claim: fewer than two full years, or no change", {}, ["ercot_all_hub_prices_history"]))
            return out
        hunt.run_pattern = run_pattern

    def run_hunt(self, **kw):
        loaded = []
        s = hunt.hunt(in_dir=self.d.name, log=lambda m: None, now=dt.datetime(2026, 10, 17, tzinfo=dt.timezone.utc),
                      state_path=os.path.join(self.d.name, "state.json"), out_root=self.d.name,
                      load=lambda drafts, log: loaded.extend(drafts) or [x["id"] for x in drafts], **kw)
        return s, loaded

    def test_the_strongest_two_regions_of_a_pattern_and_never_the_same_numbers_twice(self):
        hunt.PATTERNS = [dict(P, name="one"), dict(P, name="two")]
        # session 308: the hunt folds the regions of one grid over one span into one draft (tests/test_session308.py);
        # here every region is its own story, so this test's rule, two regions a pattern, still shows
        saved_fold = hunt.fold_key
        hunt.fold_key = lambda pattern, region, first_year, last_year: (pattern, region)
        self.addCleanup(setattr, hunt, "fold_key", saved_fold)
        rise = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        self.fake({"one": [("ercot_a", rise), ("ercot_b", [1.0, 2.0, 3.0, 4.0, 5.0, 9.0]), ("ercot_c", [1.0, 2.0, 3.0, 4.0, 5.0, 12.0]), ("ercot_d", [3.0, 2.0, 1.0, 2.5, 4.0])],
                   "two": [("ercot", rise)]})
        s, loaded = self.run_hunt()
        self.assertEqual((s["claims"], s["passed"], s["drafts"], s["loaded"]), (5, 4, 3, 3))
        by = {r["key"]: r for r in s["results"]}
        # pattern one: its two strongest regions; ercot_a is a third. Pattern two reads ercot_a's numbers and, since
        # ercot_a was not drafted, is drafted itself: a number is drafted once, not never
        self.assertEqual({r["key"] for r in s["results"] if r["drafted"]}, {"one|ercot_c", "one|ercot_b", "two|ercot"})
        self.assertIn("beyond the 2 strongest regions of its pattern", by["one|ercot_a"]["reason"])
        self.assertIn("failed: holds in more than one year", by["one|ercot_d"]["reason"])
        self.assertEqual(len(loaded), 3)
        with open(os.path.join(self.d.name, "state.json"), encoding="utf-8") as f:
            self.assertEqual(set(json.load(f)), {"one|ercot_b", "one|ercot_c", "two|ercot"})
        self.assertTrue(os.path.exists(os.path.join(self.d.name, "2026-10-17", "hunt.json")))

    def test_two_patterns_that_read_the_same_numbers_are_drafted_once(self):
        hunt.PATTERNS = [dict(P, name="one"), dict(P, name="two")]
        rise = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        self.fake({"one": [("ercot_a", rise)], "two": [("ercot", rise)]})
        s, loaded = self.run_hunt()
        by = {r["key"]: r for r in s["results"]}
        self.assertEqual((s["drafts"], len(loaded)), (1, 1))
        self.assertTrue(by["one|ercot_a"]["drafted"])
        self.assertIn("the same numbers as one|ercot_a, drafted once", by["two|ercot"]["reason"])

    def test_the_next_hunt_drafts_only_what_is_new_or_changed(self):
        hunt.PATTERNS = [dict(P, name="one")]
        self.fake({"one": [("ercot_a", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])]})
        self.assertEqual(self.run_hunt()[0]["drafts"], 1)
        s, loaded = self.run_hunt()
        self.assertEqual((s["drafts"], loaded), (0, []))
        self.assertIn("not new and not changed", s["results"][0]["reason"])
        self.fake({"one": [("ercot_a", [1.0, 2.0, 3.0, 4.0, 5.0, 8.0])]})
        self.assertEqual(self.run_hunt()[0]["drafts"], 1)

    def test_a_dry_run_loads_nothing_and_remembers_nothing(self):
        hunt.PATTERNS = [dict(P, name="one")]
        self.fake({"one": [("ercot_a", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])]})
        s, loaded = self.run_hunt(dry_run=True)
        self.assertEqual((s["drafts"], s["loaded"], loaded), (1, 0, []))
        self.assertFalse(os.path.exists(os.path.join(self.d.name, "state.json")))


class Answer:
    def __init__(self, rows, status=200):
        self.status_code, self._rows = status, rows

    def json(self):
        return self._rows

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class TheLoader(unittest.TestCase):
    def test_a_draft_already_there_or_with_an_open_draft_is_not_added_again(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock
        saved, lock.env = lock.env, lambda name: {"SUPABASE_URL": "https://example.invalid", "SUPABASE_SERVICE_KEY": "k"}.get(name, "")
        try:
            with tempfile.TemporaryDirectory() as d:
                a, _, _ = a_draft(d)
                b, _, _ = a_draft(d, values=(1.0, 2.0, 3.0, 4.0, 5.0, 9.0), region="ercot_north")
                c, _, _ = a_draft(d, values=(1.0, 2.0, 3.0, 4.0, 5.0, 12.0), region="ercot_south")
            posted = []
            have = [{"id": a["id"], "flag_key": a["flag_key"], "state": "dismissed"}, {"id": "scan-hunt-000000000000", "flag_key": b["flag_key"], "state": "draft"}]
            added = hunt.load_drafts([a, b, c], lambda m: None, get=lambda *x, **k: Answer(have),
                                     post=lambda url, data=None, headers=None, timeout=None: posted.append(json.loads(data)) or Answer([], 201))
            self.assertEqual(added, [c["id"]])
            self.assertEqual(len(posted), 1)
            self.assertEqual(sorted(posted[0][0]), sorted(["id", "flag_key", "rule", "table_name", "series_key", "flag_date", "value", "strength", "scanner_version", "flag", "card", "files"]))
            self.assertEqual(len(posted[0][0]["files"]), 6)
        finally:
            lock.env = saved


class TheReviewListAndThePage(unittest.TestCase):
    def test_the_table_takes_the_hunts_rule_and_files_and_serves_one_file_behind_the_token(self):
        sql = src("warehouse", "supabase", "migrations", "031_hunt_drafts.sql")
        self.assertIn("check (rule in ('record', 'negative', 'spike', 'weekly', 'pair', 'hunt'))", sql)
        self.assertIn("add column if not exists files jsonb not null default '{}'::jsonb", sql)
        f = sql[sql.index("create or replace function public.scanner_draft_file"):]
        self.assertIn("erw_private.site_token_ok(p_token)", f)
        self.assertIn("stable security definer", f)
        self.assertNotIn("update ", f.lower().replace("create or replace", ""))
        back = src("warehouse", "supabase", "rollbacks", "031_hunt_drafts.sql")
        self.assertIn("drop function if exists public.scanner_draft_file(text, text, text)", back)
        self.assertIn("delete from public.scanner_drafts where rule = 'hunt'", back)
        self.assertIn('("scanner_draft_file", {"p_id": "scan-hunt-000000000000", "p_name": "scan-hunt-000000000000.csv"})', src("warehouse", "supabase", "verify_rls.py"))
        self.assertNotIn("files", src("warehouse", "supabase", "migrations", "029_scanner_drafts.sql").split("scanner_drafts_list")[1].split("$$;")[0])

    def test_the_file_route_answers_only_the_internal_view_and_only_a_drafts_own_file(self):
        route = src("site", "app", "internal", "findings", "file", "route.ts")
        self.assertIn("if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();", route)
        self.assertIn("!name.startsWith(id)", route)
        self.assertIn("ID.test(id)", route)
        self.assertIn('"attachment"', route)
        self.assertNotIn("POST", route)
        self.assertIn('rpc<DraftFile | null>("scanner_draft_file"', src("site", "lib", "scanner.ts"))

    def test_the_page_shows_the_tests_the_files_and_the_caption_and_posts_nothing(self):
        page = src("site", "app", "internal", "findings", "page.tsx")
        for piece in ("{d.card.hunt ? <HuntFiles id={d.id} hunt={d.card.hunt} /> : null}", "data-hunt-file={f}", "data-hunt-caption={id}", "nothing is posted by this page",
                      "LinkedIn picture, 1200 x 627", "LinkedIn picture, 1080 x 1080"):
            self.assertIn(piece, page)
        self.assertNotIn("linkedin.com", page.lower())

    def test_an_approved_draft_can_be_chosen_for_the_roundup(self):
        review = src("site", "components", "analysis", "DraftReview.tsx")
        self.assertIn('{state === "approved" ? (', review)
        self.assertIn('body: JSON.stringify({ kind: "roundup", card_id: id })', review)
        self.assertIn("Use in Roundup", review)
        import roundup_pick
        self.assertTrue(roundup_pick.DRAFT_ID.match("scan-hunt-0123456789ab"))


class TheSaturdayTask(unittest.TestCase):
    def test_it_runs_the_hunt_every_saturday_and_catches_up_a_missed_one(self):
        ps = src("scripts", "register_weekly_hunt.ps1")
        self.assertIn("New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At $At", ps)
        self.assertIn("' --weekly >> \"'", ps)
        self.assertIn("-StartWhenAvailable", ps)
        self.assertIn('$TaskName = "ERW weekly hunt"', ps)
        self.assertIn('$TaskName = "ERW weekly hunt"', src("scripts", "unregister_weekly_hunt.ps1"))

    def test_the_hunt_calls_no_model_and_posts_nowhere(self):
        text = src("warehouse", "analysis", "findings", "hunt.py")
        for word in ("anthropic", "llm.client", "messages.create", "api.linkedin", "linkedin.com"):
            self.assertNotIn(word, text)


if __name__ == "__main__":
    unittest.main()
