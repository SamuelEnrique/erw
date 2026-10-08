"""Session 161: Ask ERCOT's average day by hour as one line (an hour-of-day axis on the shared chart, drawn only when a
series asks for it), and the two slow shapes of session 156 as one call each: "this week" (the days of the week that are
held, in one result) and generation by fuel over a stretch of days (every fuel in one read, planned by rule). No model
call and no request: the sources are read, and the session's own tests run in node on reads recorded from the live set."""
import csv
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSharedChart(unittest.TestCase):
    def test_the_hour_axis_is_a_branch_and_every_other_axis_is_written_as_it_was(self):
        c = src("site", "components", "TimeChart.tsx")
        self.assertIn('x?: "minute" | "day" | "month" | "year" | "hour_of_day";', c)
        self.assertIn('const hod = x === "hour_of_day";', c)
        # the time axis, the slider and the grid of every chart that is not the hours of a day: the lines session 22 wrote
        for words in ('type: "time",', '{ type: "slider", height: 18, bottom: 6, filterMode: "none", borderColor: token("rule"), textStyle: { color: token("muted"), fontSize: 10 }, labelFormatter: (v: number) => fmt(v) },',
                      '? [{ type: "inside", filterMode: "none" }]', 'sampling: "lttb",', "bottom: hod ? 30 : 58 },", 'xAxis: hod', "dataZoom: hod"):
            self.assertIn(words, c, words)
        # hod appears only where a branch is taken: the header's note, its definition and the three branches
        self.assertEqual(c.count("hod"), 5, "a use of hod that is not one of the three branches")
        line = src("site", "components", "LineChart.tsx")
        self.assertIn('l.points.map((p) => [x === "hour_of_day" ? p.t : p.t * 1000, p.v])', line)

    def test_no_page_but_the_answer_panel_asks_for_the_hour_axis(self):
        asks = []
        for base, _dirs, files in os.walk(os.path.join(ROOT, "site", "app")):
            for f in files:
                if f.endswith((".tsx", ".ts")) and ('"hour_of_day"' in src(base, f) or "HOUR_GROUP" in src(base, f)):
                    asks.append(os.path.relpath(os.path.join(base, f), ROOT))
        self.assertEqual(asks, [])
        panel = src("site", "components", "ask", "AskPanel.tsx")
        self.assertIn('x={hours ? HOUR_GROUP : s.group_by === "year" ? "year" : s.group_by === "month" ? "month" : "minute"}', panel)
        self.assertIn("open={!chart || (s.rows.length <= SHOWN && !hours)}", panel)      # the 24 rows stay, folded under the line

    def test_the_pages_changed_stay_in_review(self):
        release = src("site", "lib", "release.ts")
        self.assertIn('"/ask/ercot": "review"', release)


class TheTwoShapes(unittest.TestCase):
    def test_this_week_is_one_form_of_the_query_and_the_guide_says_to_answer_from_it(self):
        tools = src("site", "lib", "chat", "tools.ts")
        for words in ("const thisWeek = a.day === THIS_WEEK;", "if (week) out.week = week;", "days_held_in_part", "no day of this week is held yet"):
            self.assertIn(words, tools, words)
        forms = src("site", "lib", "chat", "forms.ts")
        for words in ('export const THIS_WEEK = "this_week";', "enum: [NEWEST, THIS_WEEK]", "TWO MORE, EACH ONE CALL (session 161)", "THREE THINGS THE QUERY DOES IN ONE CALL (session 156)"):
            self.assertIn(words, forms, words)

    def test_generation_by_fuel_is_a_fourth_shape_of_the_rule(self):
        plan = src("site", "lib", "chat", "plan.ts")
        for words in ('"hub price" | "generation" | "generation by fuel" | "reserve"', "export const MAX_FUEL_DAYS = 35;", 'group_by: "variable"', 'variable: "net_generation_mw", ...when, tz, group_by: "day"'):
            self.assertIn(words, plan, words)

    def test_the_fixture_holds_real_reads_and_no_address_or_key(self):
        text = src("tests", "fixtures", "session161", "week_reads.json")
        fix = json.loads(text)
        self.assertNotIn("supabase.co", text)
        self.assertNotRegex(text, r"eyJ[A-Za-z0-9_-]{20,}")
        self.assertEqual(sorted(fix["results"]), ["by_day", "fuels", "held", "not_held", "total_by_day", "week_rows"])
        self.assertTrue(all(k.startswith("https://fixture.invalid/") for k in fix["reads"]))


class TheRecord(unittest.TestCase):
    def rows(self):
        with open(os.path.join(ROOT, "warehouse", "chat", "eval_ercot_results_161.csv"), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(l for l in f if not l.startswith("#")))

    def test_the_cap_stopped_the_run_at_104_and_every_answer_asked_passed(self):
        rows = self.rows()
        old, new = [r for r in rows if r["set"] == "old"], [r for r in rows if r["set"] == "new"]
        self.assertEqual((len(old), len(new), len({r["id"] for r in rows})), (100, 4, 104))
        self.assertEqual(sum(int(r["pass"]) for r in rows), 104)
        spent = sum(float(r["usd"]) for r in rows)
        self.assertLess(spent, 2.0)                                   # the session's cap
        self.assertAlmostEqual(spent, 1.7806, places=3)
        self.assertIn("Asked: 100 of the 100", src("warehouse", "chat", "eval_ercot_results_161.csv"))
        self.assertIn("4 of the 20", src("warehouse", "chat", "eval_ercot_results_161.csv"))

    def test_the_two_slow_shapes_are_one_call_each_and_nothing_takes_twenty_seconds(self):
        rows = {r["id"]: r for r in self.rows()}
        week, fuel = rows["s02"], rows["h05"]
        self.assertEqual((week["pass"], week["model_calls"], week["tool_calls"], week["tools"]), ("1", "2", "1", "query:eia930_all_demand+this_week"))
        self.assertEqual((fuel["pass"], fuel["model_calls"], fuel["planned_by"], fuel["tools"]), ("1", "1", "rule", "query:eia930_all_generation query:eia930_all_generation"))
        self.assertEqual((week["s156_seconds_words"], week["s156_model_calls"], fuel["s156_seconds_words"], fuel["s156_model_calls"]), ("24.7", "10", "28.6", "7"))
        self.assertLess(float(week["seconds_words"]), 8)
        self.assertLess(float(fuel["seconds_words"]), 4)
        self.assertTrue(all(float(r["seconds_words"]) < 20 for r in rows.values()))
        for i in ("h13", "h24"):                                      # the average day by hour: one read, one series of 24 rows
            self.assertEqual((rows[i]["pass"], rows[i]["tool_calls"], rows[i]["series_rows"]), ("1", "1", "24"), i)
            self.assertIn("+hour_of_day", rows[i]["tools"])

    def test_the_note_says_what_was_measured_and_what_was_not_asked(self):
        note = src("docs", "methods", "ask_ercot.md")
        for words in ("## A day's hours as a line, and two slow answers (session 161, 8 October 2026)", "stopped the run after 104 of the 120", "The 16 not asked are not counted anywhere below",
                      "| Questions about numbers (50; target 5 seconds) | 50 | 4.65 (4.6) | 28 under 5 seconds (30) |", "| About an idea (25; target 2 seconds) | 25 | 2.4 (2.1) | 4 under 2 seconds (8) |",
                      "No table of generation by fuel by day is held", "Each question was asked once."):
            self.assertIn(words, note, words)
        rows = self.rows()
        nums = sorted(float(r["seconds_words"]) for r in rows if r["set"] == "old" and r["kind"] in ("chart", "sentence"))
        self.assertEqual((round((nums[24] + nums[25]) / 2, 2), sum(1 for x in nums if x < 5)), (4.65, 28))
        self.assertNotIn(DASH, note)


class TheFiles(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("site", "components", "TimeChart.tsx"), ("site", "components", "LineChart.tsx"), ("site", "components", "ask", "AskPanel.tsx"), ("site", "lib", "chat", "series.ts"),
                      ("site", "lib", "chat", "forms.ts"), ("site", "lib", "chat", "plan.ts"), ("site", "lib", "chat", "tools.ts"), ("site", "lib", "chat", "ercot.ts"),
                      ("site", "scripts", "test-ask-161.mjs"), ("site", "scripts", "chart-options.mjs"), ("site", "scripts", "check-ask-hours.mjs"), ("tests", "fixtures", "session161", "week_reads.json"),
                      ("warehouse", "chat", "eval", "ercot_results_161.py"), ("warehouse", "chat", "eval_ercot_results_161.csv")):
            self.assertNotIn(DASH, src(*parts), parts)


class TheNodeTests(unittest.TestCase):
    def test_the_sessions_own_tests_pass_with_no_request(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("node or the site's packages are not here")
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-161.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1200:])
        self.assertIn("8 tests pass", r.stdout)


if __name__ == "__main__":
    unittest.main()
