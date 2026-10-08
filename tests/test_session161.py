"""Session 161: Ask ERCOT's average day by hour as one line (an hour-of-day axis on the shared chart, drawn only when a
series asks for it), and the two slow shapes of session 156 as one call each: "this week" (the days of the week that are
held, in one result) and generation by fuel over a stretch of days (every fuel in one read, planned by rule). No model
call and no request: the sources are read, and the session's own tests run in node on reads recorded from the live set."""
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


class TheFiles(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("site", "components", "TimeChart.tsx"), ("site", "components", "LineChart.tsx"), ("site", "components", "ask", "AskPanel.tsx"), ("site", "lib", "chat", "series.ts"),
                      ("site", "lib", "chat", "forms.ts"), ("site", "lib", "chat", "plan.ts"), ("site", "lib", "chat", "tools.ts"), ("site", "lib", "chat", "ercot.ts"),
                      ("site", "scripts", "test-ask-161.mjs"), ("site", "scripts", "chart-options.mjs"), ("tests", "fixtures", "session161", "week_reads.json")):
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
