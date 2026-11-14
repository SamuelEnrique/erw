"""Session 5267 (chain 256): a query bounded by a start and an end says whether its window is whole.

Energy Research Warehouse (ERW). The chat found a short day, week or month by counting the window's rows itself and by
grouping them again: 79 of the 257 tool calls made after the figure was in hand on 13 November 2026
(docs/reviews/ask-eval-2026-11-13.md). The query tool of both loops now says it with the first result, under `window`:
the steps held, the steps the window has at the table's step, the runs missing. A pure function in each language
(warehouse/chat/window.py, site/lib/chat/window.ts), held to the same answers on the made windows of
tests/fixtures/session5267/window_cases.json.

Held here, with no network and no model: the Python function on every made window; the Python tool on session 1300's
fixture rows (whole, in part, nothing held, a threshold, no end, a time zone on a table of years); the site's function
through `node --test` (node strips the types: no package of the site is needed, and no file is written); the site's
tool by its source (no request added, none changed); and the stored replays that set the new key apart.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import test_session1300 as T  # noqa: E402  the fixture's frames
import tools  # noqa: E402
import window as W  # noqa: E402

Q = dict(table="ercot_peak_premium_annual", entity="ercot:HB_HUBAVG", variable="peak_minus_midday_median")   # twelve yearly rows, 2015 to 2026


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def cases():
    return json.loads(src("tests", "fixtures", "session5267", "window_cases.json"))["cases"]


def query(**kw):
    with T.Frames() as frames:
        frames.load()
        return tools.query(**{**Q, **kw})


class TheFunction(unittest.TestCase):
    def test_every_made_window(self):
        cs = cases()
        self.assertGreaterEqual(len(cs), 38)
        for c in cs:
            got = W.window_of(c["start"], c["end"], c["steps"], c["series"])
            self.assertEqual(got, c["window"], c["name"])
            if got:
                self.assertEqual(list(got), list(c["window"]), c["name"])       # the keys in the same order as the site's

    def test_the_cases_say_what_their_names_say(self):
        by = {c["name"]: c["window"] for c in cases()}
        day = by["an hourly day with two runs missing"]
        self.assertEqual((day["steps_held"], day["steps_in_window"], day["steps_missing"], day["whole"]), (19, 24, 5, False))
        self.assertEqual(day["missing"], [{"from": "2026-11-10T05:00:00Z", "until": "2026-11-10T08:00:00Z", "steps": 3},
                                          {"from": "2026-11-10T22:00:00Z", "until": "2026-11-11T00:00:00Z", "steps": 2}])
        week = by["a week of hours held for three of its seven days"]
        self.assertEqual((week["steps_held"], week["steps_in_window"], week["missing"][0]["steps"]), (72, 168, 96))
        none = by["an hourly day, no row held, the series named"]
        self.assertEqual((none["steps_held"], none["steps_in_window"], none["whole"], none["note"]), (0, 24, False, W.NONE_HELD))
        self.assertEqual(by["a local day of 25 hours (the clocks go back)"]["steps_in_window"], 25)
        self.assertEqual(by["a table of months, February missing"]["missing"], [{"from": "2025-02-01T00:00:00Z", "until": "2025-03-01T00:00:00Z", "steps": 1}])
        self.assertEqual(by["a table of two steps, the rows five minutes apart"]["step"], "PT5M")
        self.assertIsNone(by["no series"])
        # session 5276: SP15's real-time prices on the live set's missing day: a table of two steps, no row. Not "not told"
        gap = by["a missing local day of a table of two steps, no row (SP15 real time)"]
        self.assertEqual((gap["steps_held"], gap["steps_in_window"], gap["whole"], gap["note"]), (0, None, False, W.NONE_HELD_ANY_STEP))
        self.assertIsNone(by["a table of two steps, no row, a window shorter than one of them: not told"]["whole"])
        self.assertIsNone(by["a table of hours and weeks and no row: not told"]["whole"])      # a week's grid is only told by a row
        # a whole window of hours says no check is needed; of days or longer, that every row is held and the row's cover is the table's to say
        self.assertEqual(by["an hourly UTC day, whole"]["note"], W.WHOLE)
        for name in ("a table of months, a year whole", "a table of months, the one month asked, held", "a table of days and months, the rows a day apart"):
            self.assertEqual(by[name]["note"], W.WHOLE_ROWS, name)
        self.assertIn("da_hours, days_held", W.WHOLE_ROWS)

    def test_it_is_never_whole_and_never_in_part_on_a_guess(self):
        for c in cases():
            w = c["window"]
            if w is None:
                continue
            if w["steps_in_window"] is None and w["whole"] is False:
                # session 5276: the one thing said with no count of the window's steps: no row at all is held, and the
                # window has steps at every step the table may have. That is no guess
                self.assertEqual((w["steps_held"], w["first_held"], w["step"]), (0, None, None), c["name"])
                self.assertTrue(w["note"].startswith(W.NONE_HELD_ANY_STEP), c["name"])
                self.assertNotIn("missing", w, c["name"])
            elif w["steps_in_window"] is None:
                self.assertIsNone(w["whole"], c["name"])
                self.assertTrue(w["note"].startswith(W.UNKNOWN), c["name"])
                self.assertNotIn("missing", w, c["name"])
            elif isinstance(w["steps_held"], int) and w["steps_in_window"]:
                self.assertEqual(w["whole"], w["steps_held"] == w["steps_in_window"], c["name"])
                self.assertEqual(w["steps_missing"], w["steps_in_window"] - w["steps_held"], c["name"])

    def test_the_notes_are_the_sites_word_for_word(self):
        ts = src("site", "lib", "chat", "window.ts")
        for words in (W.WHOLE, W.WHOLE_ROWS, W.NONE_HELD_ANY_STEP, W.PART, W.NONE_HELD, W.UNKNOWN, W.SEVERAL, W.EMPTY):
            self.assertIn(json.dumps(words), ts, words[:50])
        self.assertIn(f"export const MISSING_SHOWN = {W.MISSING_SHOWN};", ts)
        self.assertIn(f"export const MOST_LABELS = {W.MOST_LABELS};", ts)


class ThePythonTool(unittest.TestCase):
    def test_a_window_held_whole(self):
        w = query(aggregation="mean", start="2019-01-01", end="2025-01-01")["window"]
        self.assertEqual((w["step"], w["steps_held"], w["steps_in_window"], w["steps_missing"], w["whole"]), ("P1Y", 6, 6, 0, True))
        self.assertEqual((w["from"], w["until"], w["first_held"], w["last_held"]), ("2019-01-01T00:00:00Z", "2025-01-01T00:00:00Z", "2019-01-01T00:00:00Z", "2024-01-01T00:00:00Z"))
        self.assertEqual(w["note"], W.WHOLE_ROWS)      # a table of years: every row held, and a row's own cover is the table's to say

    def test_a_window_held_in_part_names_the_run_missing(self):
        out = query(aggregation="max", start="2014-01-01", end="2027-01-01")
        w = out["window"]
        self.assertEqual((out["rows_matched"], w["steps_held"], w["steps_in_window"], w["whole"]), (12, 12, 13, False))
        self.assertEqual(w["missing"], [{"from": "2014-01-01T00:00:00Z", "until": "2015-01-01T00:00:00Z", "steps": 1}])
        self.assertEqual(w["note"], W.PART)

    def test_a_window_with_nothing_held_says_so(self):
        out = query(aggregation="mean", start="2030-01-01", end="2031-01-01")
        self.assertEqual((out["rows_matched"], out["result"]), (0, []))
        self.assertEqual((out["window"]["steps_held"], out["window"]["steps_in_window"], out["window"]["whole"], out["window"]["note"]), (0, 1, False, W.NONE_HELD))
        with T.Frames() as frames:      # with no entity and no variable named too: no row of the table is in the window
            frames.load()
            bare = tools.query(table=Q["table"], aggregation="mean", start="2030-01-01", end="2031-01-01")["window"]
        self.assertEqual((bare["steps_held"], bare["steps_in_window"], bare["whole"]), (0, 1, False))

    def test_the_window_is_counted_before_a_threshold_keeps_some_rows(self):
        out = query(aggregation="count", start="2019-01-01", end="2025-01-01", threshold={"above": 10})
        self.assertEqual((out["rows_matched"], out["threshold"]["rows_in_window"], out["window"]["steps_held"], out["window"]["whole"]), (1, 6, 6, True))

    def test_no_window_without_both_bounds_and_a_time_zone_moves_no_year(self):
        self.assertNotIn("window", query(aggregation="mean", start="2019-01-01"))
        self.assertNotIn("window", query(aggregation="mean", end="2025-01-01"))
        self.assertNotIn("window", query(aggregation="mean"))
        w = query(aggregation="mean", start="2019-01-01", end="2025-01-01", tz="America/Chicago")["window"]
        self.assertEqual((w["from"], w["steps_held"], w["steps_in_window"]), ("2019-01-01T00:00:00Z", 6, 6))     # a table of years is bounded by its labels

    def test_every_other_key_of_the_answer_is_as_it_was(self):
        keys = list(query(aggregation="mean", start="2019-01-01", end="2025-01-01"))
        self.assertEqual(keys[:5], ["aggregation", "value_column", "filters", "rows_matched", "window"])
        self.assertEqual([k for k in keys if k != "window"], list(query(aggregation="mean", start="2019-01-01")))


class TheSitesTool(unittest.TestCase):
    def test_the_field_is_made_from_the_rows_read_and_asks_the_database_nothing(self):
        t = src("site", "lib", "chat", "tools.ts")
        self.assertIn('import { windowOf } from "./window";', t)
        block = t[t.index("// session 5267 (lib/chat/window.ts)"):t.index("if (dcol) out.date_column")]
        self.assertIn('if (shape === "series" && !family && a.day === undefined && a.start && a.end) {', block)
        self.assertIn("for (const r of all) if (r.t)", block)
        self.assertIn('if (!all.length) by[`${a.entity ?? "*"}|${a.variable ?? "*"}`] = [];', block)     # no row in the window: 0 of its steps                              # the rows before a threshold, as the Python tool
        self.assertIn('windowOf(parseTime(a.start, btz), parseTime(a.end, btz), (c.interval ?? "").split(";").filter(Boolean), by)', block)
        for word in ("rest(", "read(", "await "):                                         # no request added
            self.assertNotIn(word, block, word)
        # and none changed: the read's select is what it was (the recorded reads of four fixtures are found by it)
        self.assertIn('if (shape === "series" && a.day === THIS_WEEK) sel.push("freq");', t)
        self.assertEqual(t.count('sel.push("freq")'), 1)

    def test_the_stored_replays_set_the_new_key_apart_and_check_it(self):
        for name in ("test-ask-161.mjs", "test-ask-ready.mjs", "test-ask-speed.mjs"):
            self.assertIn('k.endsWith("_local") || k === "window" ? undefined : v', src("site", "scripts", name), name)
        self.assertIn('["PT1H", 96, 96, 0, true, "2026-09-28T05:00:00Z", "2026-10-02T04:00:00Z"]', src("site", "scripts", "test-ask-161.mjs"))
        self.assertIn('[["P1D", 30, 30, true], undefined, ["P1M", 1, 1, true]]', src("site", "scripts", "test-ask-speed.mjs"))

    def test_the_sites_function_answers_every_made_window_as_the_python_one(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not here")
        r = subprocess.run([node, "--test", os.path.join("site", "scripts", "test-ask-window.test.mjs")], cwd=ROOT, capture_output=True, text=True, timeout=180)
        if r.returncode != 0 and "ERR_UNKNOWN_FILE_EXTENSION" in (r.stdout + r.stderr):
            self.skipTest("this node does not strip a .ts file's types")
        self.assertEqual(r.returncode, 0, (r.stdout[-1500:] + r.stderr[-800:]))
        self.assertRegex(r.stdout, r"pass 6\b")
        self.assertRegex(r.stdout, r"fail 0\b")


if __name__ == "__main__":
    unittest.main()
