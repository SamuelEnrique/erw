"""Session 153: Ask ERCOT reads what stands behind four pages built this week.

Energy Research Warehouse (ERW). The pages: what a datacenter pays (/cost-of-power), curtailment with where free
energy is (/curtailment), the capture price (/cost-of-power/seller) and where the resources are (/resources). What is
held here, with no model call and no request:

  - the 20 test questions (warehouse/chat/eval_ercot_pages.json) are the ones the script writes from the site's own
    files, and well formed: four pages, sentences and charts, two refusals with their words;
  - the script's arithmetic on small cases worked by hand (a flat load, the capture price, the last twelve months);
  - where each source is registered: ten public tables of the live set join the panel, no table was added to the
    live set, and no internal table is offered anywhere;
  - the sources: the tool reads the pages' own files through the pages' own functions, the exported spec is as it
    was, the menu and the shared reader are untouched;
  - the Method note says what is read, what each is not and what is held;
  - the session's own tests in node (site/scripts/test-ask-tables.mjs), where node and the site's packages are.

The two questions answered from tables are computed again where the tables are: ERW_TABLES when that is set (another
copy's warehouse/output), else this copy's warehouse/output. Where they are not, those two are compared as committed.

    python -m unittest tests.test_session153 -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
DASH = chr(0x2014)
PAGES = ["/cost-of-power", "/curtailment", "/cost-of-power/seller", "/resources"]
TABLES = ["iso_curtailment_monthly", "caiso_curtailment_daily", "spp_curtailment_daily", "ercot_wind_solar_hsl_daily", "caiso_curtailment_profile",
          "eia930_demand_growth", "interconnection_queue_summary", "ercot_large_load_status", "cost_of_power_hourly_profile", "cost_of_power_carbon"]
HELD = ["isone_zone_prices_history", "isone_ddg_undelivered_monthly", "isone_zone_load_hourly", "nyiso_load_queue", "texas_transmission_matrix", "texas_delivery_charges"]
exp = None   # the script, loaded in setUpModule (nothing is changed at import)


def setUpModule():
    global exp
    sys.path.insert(0, EVAL)
    import ercot_pages_expected
    exp = ercot_pages_expected


def tearDownModule():
    if EVAL in sys.path:
        sys.path.remove(EVAL)


def tables_dir():
    """Where the warehouse's tables are on this machine: ERW_TABLES, else this copy's warehouse/output."""
    return os.environ.get("ERW_TABLES") or os.path.join(ROOT, "warehouse", "output")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def questions():
    return json.loads(src("warehouse", "chat", "eval_ercot_pages.json"))


class TheQuestions(unittest.TestCase):
    def test_the_committed_questions_are_what_the_script_writes_from_the_files(self):
        old = questions()
        kept = {q["id"]: q for q in old["questions"]}
        kept["_facts"] = old.get("facts", {})
        new = exp.build(tables_dir(), kept)
        # session 159: p14 rests on a file the daily run rebuilds (site/data/curtailment/ercot.json): its expected number
        # and that file's build stamp are left out of the comparison
        bare = lambda q: {k: v for k, v in q.items() if k != "table_read" and not (q.get("id") == "p14" and k == "expect")}
        self.assertEqual([bare(q) for q in new["questions"]], [bare(q) for q in old["questions"]])
        self.assertEqual({k: v for k, v in new["built_from"].items() if k not in ("tables_read", "texas")}, {k: v for k, v in old["built_from"].items() if k not in ("tables_read", "texas")})
        # the two questions answered from a table hold a number whether or not the table is on this machine
        for qid in ("p04", "p11"):
            self.assertEqual(len(kept[qid]["expect"]), 1, qid)

    def test_twenty_questions_four_pages_two_refusals_with_their_words(self):
        f = questions()
        qs = f["questions"]
        self.assertEqual(len(qs), 20)
        self.assertEqual(len({q["id"] for q in qs}), 20)
        for p in PAGES:
            self.assertGreaterEqual(sum(q["page"] == p for q in qs), 4, p)
        kinds = [q["kind"] for q in qs]
        self.assertEqual(kinds.count("refuse"), 2)
        self.assertGreaterEqual(kinds.count("chart"), 6)
        self.assertGreaterEqual(kinds.count("sentence"), 8)
        self.assertEqual(sorted(q["say"] for q in qs if q["kind"] == "refuse"), ["held, not shown", "paused while terms are reviewed"])
        old = json.loads(src("warehouse", "chat", "eval_ercot_panel.json"))["questions"]
        self.assertEqual(len(old), 100)                                                  # the 100 are as they were
        self.assertFalse({q["id"] for q in qs} & {q["id"] for q in old})
        self.assertFalse({q["q"] for q in qs} & {q["q"] for q in old})
        for q in qs:
            self.assertTrue(q["source"] and q["read"]["tool"] in ("page_file", "query"), q["id"])
            self.assertLessEqual(len(q["q"]), 500)
            if q["kind"] == "sentence":
                self.assertTrue(q.get("expect") or q.get("expect_all"), q["id"])
                self.assertTrue(re.search(q["cite"], q["source"]), q["id"])
            if q["kind"] == "chart":
                self.assertGreaterEqual(q["series_rows"], 3, q["id"])
                self.assertIn("value", q["series_has"])
        self.assertNotIn(DASH, json.dumps(f, ensure_ascii=False) + src("warehouse", "chat", "eval", "ercot_pages_expected.py"))
        self.assertIn("do not edit by hand", f["_about"])
        self.assertEqual(sorted(f["rules_added"]), ["cite", "expect", "expect_all", "must", "series_has", "series_rows"])

    def test_a_number_a_question_expects_is_a_number_of_its_file(self):
        """Read straight from the files, with no function of the script: the figures that need no arithmetic."""
        qs = {q["id"]: q for q in questions()["questions"]}
        free = json.loads(src("site", "data", "curtailment", "free_energy.json"))
        west = next(x for x in free["grids"]["ercot"]["locations"] if x["id"] == "HB_WEST")
        self.assertEqual(qs["p12"]["expect"], [west["year"]["under5"]])
        self.assertEqual(qs["p13"]["series_has"]["value"], next(x for x in free["grids"]["ercot"]["locations"] if x["id"] == "LZ_WEST")["year"]["under5"])
        texas = json.loads(src("site", "data", "curtailment", "ercot.json"))
        # session 159: the daily run rebuilds this file, so the share moves each day; the question file is written again
        # by the script before an evaluation (ercot_pages_expected.py); here only its shape is held
        self.assertEqual(len(qs["p14"]["expect"]), 1)
        self.assertIsInstance(qs["p14"]["expect"][0], (int, float))
        self.assertIsInstance(texas["window"]["both"]["share_pct"], (int, float))
        self.assertEqual(texas["first_day"], "2026-09-28")                               # the estimate's first day, as the guide says
        shares = json.loads(src("site", "data", "curtailment", "shares.json"))
        self.assertEqual(qs["p10"]["series_has"]["value"], round(shares["grids"]["spp"]["months"]["2025-04"]["share_pct"], 2))
        basins = json.loads(src("site", "data", "resources", "layers", "oil_gas_basins.json"))["features"]
        permian = next(b for b in basins if b["properties"]["name"] == "Permian")["properties"]["value"]
        self.assertEqual(qs["p16"]["expect"], [round(permian, 1)])
        self.assertEqual(qs["p17"]["series_rows"], len(basins))


class TheArithmetic(unittest.TestCase):
    """The script's rules on cases small enough to work by hand."""

    def test_the_last_twelve_months_are_the_newest_twelve_in_a_row_that_all_count(self):
        months = {f"2025-{m:02d}": (1.0, 700, 720) for m in range(1, 13)}
        months.update({"2026-01": (1.0, 744, 744), "2026-02": (1.0, 100, 672), "2026-03": (1.0, 744, 744)})   # February is short
        counted = lambda r: r[1] >= 0.95 * r[2]
        self.assertEqual(exp.last_twelve(months, counted), [f"2025-{m:02d}" for m in range(2, 13)] + ["2026-01"])
        self.assertIsNone(exp.last_twelve({"2026-01": (1.0, 744, 744)}, counted))
        self.assertEqual(exp.prev_month("2026-01", 1), "2025-12")
        self.assertEqual(exp.prev_month("2026-03", 14), "2025-01")

    def test_the_capture_price_is_price_times_generation_over_generation(self):
        # two months: 2 hours at 10 and 30 with generation 1 and 3; 1 hour at 20 with generation 4
        a, b = [2, 2, 40.0, 4.0, 10 * 1 + 30 * 3], [1, 1, 20.0, 4.0, 20 * 4]
        f = exp.capture_figure([a, b])
        self.assertEqual(f["price"], 22.5)                                               # (100 + 80) / 8
        self.assertEqual(f["flat"], 20.0)                                                # (40 + 20) / 3
        self.assertEqual(f["premium"], 2.5)
        self.assertEqual(f["pct"], 12.5)
        # a plant that generates the same in every hour captures the flat average exactly
        self.assertEqual(exp.capture_figure([[2, 2, 40.0, 2.0, 40.0]])["premium"], 0.0)

    def test_rounding_is_the_sites_and_a_year_has_its_hours(self):
        self.assertEqual(exp.js_round(2.675, 2), 2.68)        # half up on the product, as Math.round
        self.assertEqual(exp.js_round(-14.664, 2), -14.66)
        self.assertEqual(exp.plain(61763.2104), 61763.2)
        self.assertEqual(exp.plain(0.24191), 0.2419)
        self.assertEqual(exp.month_starts(2024)[-1], 8784)
        self.assertEqual(exp.month_starts(2025)[-1], 8760)
        self.assertEqual(exp.month_starts(2025)[2] - exp.month_starts(2025)[1], 24 * 28)


class WhereEachSourceIs(unittest.TestCase):
    def test_the_ten_tables_are_public_tables_the_live_set_already_loads_and_nothing_was_added_to_it(self):
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        for t in TABLES:
            self.assertTrue(any(re.search(rule, t) for rule in live["full"]), f"{t} matches no rule of the live set")
            self.assertNotIn(t, live["catalogue_hold"])
        text = src("warehouse", "supabase", "live_set.yaml")
        self.assertNotIn("session 153", text)                                           # no table is loaded for this session
        p = src("site", "lib", "chat", "pagefiles.ts")
        for t in TABLES:
            self.assertIn(f"  {t}: ", p)

    def test_no_internal_table_is_offered_and_each_is_held_out_of_the_sites_database(self):
        live = yaml.safe_load(src("warehouse", "supabase", "live_set.yaml"))
        p = src("site", "lib", "chat", "pagefiles.ts")
        spec = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        for t in HELD:
            self.assertIn(t, live["catalogue_hold"], t)                                  # not loaded, not in the public catalogue
            self.assertNotIn(t, live.get("review_hold", []))
            self.assertIn(f'table: "{t}"', p)
            self.assertNotIn(t, spec["tables"])
            self.assertNotIn(f"  {t}: ", p.split("export const PAGES_FILTERS")[1].split("};")[0])
        self.assertIn('export const HELD_WORDS = "held, not shown";', p)
        self.assertIn('miso: "paused while terms are reviewed", pjm: "licensed source needed"', p)
        # the tool reads neither the file of Texas charges nor New York's queue
        for f in ("texas_delivery.json", "nyiso_load_queue.json", "large_load_status.json"):
            self.assertNotIn(f, p)
        # an internal table is named in that file only to be refused: in the list of what is held, or where a view
        # looks its refusal up. No line reads one (session 149's test lets this one file name ISO-NE's monthly table)
        for t in HELD:
            for line in p.split("\n"):
                if t in line:
                    self.assertTrue(line.lstrip().startswith(f'{{ table: "{t}"') or f'HELD.find((h) => h.table === "{t}")' in line, line[:160])

    def test_new_yorks_load_file_holds_no_request(self):
        ny = json.loads(src("site", "data", "nyiso_load_queue.json"))
        self.assertIs(ny["shown"], False)
        self.assertNotIn("rows", ny)
        self.assertNotIn("zones", ny)


class TheSources(unittest.TestCase):
    def test_the_tool_reads_the_pages_own_files_through_the_pages_own_functions(self):
        p = src("site", "lib", "chat", "pagefiles.ts")
        for words in ('import captureJson from "@/data/seller/capture.json";', 'import freeJson from "@/data/curtailment/free_energy.json";', 'import sharesJson from "@/data/curtailment/shares.json";',
                      'import worthJson from "@/data/curtailment/worth.json";', 'import texasJson from "@/data/curtailment/ercot.json";',
                      'from "@/lib/capture";', 'from "@/lib/curtailment";', 'from "@/lib/datacenter";', 'import { INDEX, yearFiles } from "@/lib/datacenterdata";', 'from "@/lib/freeenergy";', 'from "@/lib/resources";',
                      'path.join(process.cwd(), "data", "resources", "manifest.json")', 'path.join(process.cwd(), "data", "resources", "layers", file)', 'path.join(process.cwd(), "data", "datacenter", `${grid}_${y}.json`)',
                      'return env !== "off";', "the page's file could not be read, so no figure is given"):
            self.assertIn(words, p, words)
        # the same imports the pages make
        self.assertIn('import captureJson from "@/data/seller/capture.json";', src("site", "app", "cost-of-power", "seller", "page.tsx"))
        for f in ("ercot", "free_energy", "shares", "worth"):
            self.assertIn(f'from "@/data/curtailment/{f}.json";', src("site", "app", "curtailment", "page.tsx"))
        self.assertIn('import { DELIVERY, INDEX, yearFiles, type MatrixRow } from "@/lib/datacenterdata";', src("site", "app", "cost-of-power", "page.tsx"))
        self.assertNotIn("@/lib/supabase", p)                                            # nothing here reads the database
        self.assertNotIn("fetch(", p)
        self.assertNotIn(DASH, p + src("site", "lib", "chat", "pagelinks.ts") + src("site", "scripts", "test-ask-tables.mjs") + src("site", "scripts", "eval-judge.mjs"))

    def test_the_profile_adds_the_pages_on_session_148s_and_the_exported_spec_is_untouched(self):
        e = src("site", "lib", "chat", "ercot.ts")
        # session 156: the profile of this session keeps its body and has a name of its own (profile153); the profile the
        # route serves, ercotProfile, is that one with session 156's layer on it
        for words in ("function profile148(): Profile {", "export function profile153(): Profile {\n  const p = profile148();\n  if (!pagesOffered() || !p.scope) return p;",
                      "export function ercotProfile(): Profile {\n  const p = profile153();",
                      "system: p.system + pagesGuide(),", "const held = heldIn(input);\n      if (held) return Promise.resolve({ out: heldRefusal(held), isError: true });",
                      "...ROLLUP_TABLES, ...PAGES_NEAR];", "?? PAGES_HOLDS[t] ?? \"\"",
                      # what sessions 137 and 148 pinned is still there, word for word
                      "system: spec.system + addendum(base.slug, base.iso),", "tools: [PAGE_TOOL],", "tables: [...spec.tables, ...MIX_TABLES]",
                      "return offered ? { ...profile, system: spec.system + rollupGuide() + addendum(base.slug, base.iso) } : profile;"):
            self.assertIn(words, e, words)
        spec = json.dumps(json.loads(src("site", "lib", "chat", "spec_ercot.json")))
        for words in ("page_file", "iso_curtailment_monthly", "held, not shown"):
            self.assertNotIn(words, spec)                                                # the Python export is as it was
        limits = json.loads(src("site", "lib", "chat", "limits.json"))
        self.assertEqual((limits["daily_usd"], limits["monthly_usd"]), (3, 30))          # production's ceilings are untouched

    def test_the_menu_the_shared_reader_and_the_live_pages_are_not_in_this_sessions_changes(self):
        git = shutil.which("git")
        if not git:
            self.skipTest("git is not here")
        # session 154: the guard is about session 153's own changes, so it runs on that session's branch only; on a
        # later branch it would forbid every later change to the menu, the live set or a site data file
        branch = subprocess.run([git, "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if branch != "wip/153-ask-tables":
            self.skipTest("this guard belongs to session 153's own branch")
        base = subprocess.run([git, "merge-base", "HEAD", "origin/main"], cwd=ROOT, capture_output=True, text=True)
        if base.returncode != 0:
            self.skipTest("origin/main is not known to this copy")
        changed = subprocess.run([git, "diff", "--name-only", base.stdout.strip(), "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        working = subprocess.run([git, "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        for f in changed + working:
            self.assertNotIn(f, ("site/lib/pages.ts", "site/lib/supabase.ts", "site/lib/release.ts", "warehouse/supabase/live_set.yaml", "site/lib/chat/limits.json", "site/lib/chat/spec_ercot.json", "site/next.config.ts"), f)
            for live in ("site/app/cost-of-power/battery/", "site/app/network/", "site/app/storage/", "site/data/", "site/public/network/"):
                self.assertFalse(f.startswith(live), f)

    def test_the_runner_takes_another_set_and_judges_the_hundred_as_before(self):
        r = src("site", "scripts", "eval-ask-speed.mjs")
        self.assertIn('const setArg = args.indexOf("--set") >= 0 ? args[args.indexOf("--set") + 1] : null;', r)
        self.assertIn('path.resolve(here, "..", "..", "warehouse", "chat", "eval_ercot_panel.json")', r)       # the default set is the 100
        self.assertIn("if (!mayAsk(sessionSpend(spend), reserve, stop)) { stopped = true;", r)                 # the stop is before a question
        self.assertIn('if (!/^https?:\\/\\/(localhost|127\\.0\\.0\\.1)(:\\d+)?$/.test(base))', r)              # a local server only
        j = src("site", "scripts", "eval-judge.mjs")
        self.assertIn('if (q.kind !== "refuse") {', j)
        self.assertIn("A question of the 100 carries none of these fields and is judged exactly as it was.", j)


class TheMethodNote(unittest.TestCase):
    def test_it_says_what_is_read_what_each_is_not_and_what_is_held(self):
        note = src("docs", "methods", "ask_ercot.md")
        self.assertIn("## Four pages more (session 153, 8 October 2026)", note)
        for t in TABLES + HELD:
            self.assertIn(f"`{t}`", note, t)
        for words in ("No table was loaded for it and no page changed.", "A figure from `page_file` is the page's figure", "It is the fleet's shape, not a site's",
                      "two revenues added", "It is not a siting study", "is not a gross capacity factor and is not called one", "rest on its Today's Outlook output",
                      "from 28 September 2026", "the 2026 matrices are filed, not approved", '"held, not shown"', '"paused while terms are reviewed"', '"licensed source needed"',
                      "`ASK_PAGES=off`", "warehouse/chat/eval_ercot_pages.json"):
            self.assertIn(words, note, words)
        # what stood before still stands: every refusal of the section "What it does not answer". Its first sentence was
        # "Ask ERCOT speaks for ERCOT only."; session 156 reworded it, on the owner's instruction of 8 October 2026,
        # because with these four pages it stopped being true (the note still says when the tool speaks for ERCOT only)
        for words in ("## What it does not answer", "**Licensed data.**", "**What a named company earned, bid or owns.**", "**Forecasts and advice.**", "each have their own page on this site"):
            self.assertIn(words, note, words)
        self.assertIn("Ask ERCOT answers for the Texas grid, and for the other grids only what four pages of this site show", note)
        self.assertIn("still speaks for ERCOT only", note)
        self.assertNotIn(DASH, note)


class TheRecord(unittest.TestCase):
    """The 120 questions as they were asked on 8 October 2026 (phase 2). The record is in git; the answers are not."""

    def rows(self):
        import csv
        with open(os.path.join(ROOT, "warehouse", "chat", "eval_ercot_pages_results_153.csv"), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(l for l in f if not l.startswith("#")))

    def test_every_question_was_asked_once_and_none_twice_but_the_one_named(self):
        rows = self.rows()
        new = [r for r in rows if r["set"] == "new"]
        old = [r for r in rows if r["set"] == "old"]
        again = [r for r in rows if r["set"] == "reask"]
        self.assertEqual(sorted(r["id"] for r in new), sorted(q["id"] for q in questions()["questions"]))
        self.assertEqual(sorted(r["id"] for r in old), sorted(q["id"] for q in json.loads(src("warehouse", "chat", "eval_ercot_panel.json"))["questions"]))
        self.assertEqual([r["id"] for r in again], ["p14"])
        self.assertEqual(len(rows), 121)
        self.assertTrue(all(float(r["usd"]) > 0 for r in rows))                         # every answer's cost is known: none is counted at a guess

    def test_the_counts_the_method_note_gives_are_the_records(self):
        rows = self.rows()
        new = [r for r in rows if r["set"] == "new"]
        old = [r for r in rows if r["set"] == "old"]
        self.assertEqual((sum(int(r["pass"]) for r in new), sum(int(r["pass"]) for r in old)), (19, 98))
        self.assertEqual(sorted(r["id"] for r in rows if r["set"] != "reask" and not int(r["pass"])), ["h13", "h14", "p14"])
        self.assertEqual(int(next(r for r in rows if r["set"] == "reask")["pass"]), 1)
        total = sum(float(r["usd"]) for r in rows)
        self.assertLess(total, 2.80)                                                     # under the session's stop
        self.assertEqual(round(total, 4), 2.6096)
        self.assertEqual(round(sum(float(r["usd"]) for r in new) / 20, 4), 0.0281)
        self.assertEqual(round(sum(float(r["usd"]) for r in old) / 100, 4), 0.0202)
        # the two refusals were refusals, and the ten older questions about another grid still are
        self.assertTrue(all(r["status"] == "not_in_warehouse" and int(r["pass"]) for r in new if r["kind"] == "refuse"))
        other = ("r01", "r02", "r03", "r04", "r05", "r06", "r16", "r19", "r22", "r25")
        self.assertTrue(all(r["status"] == "not_in_warehouse" and int(r["pass"]) for r in old if r["id"] in other))
        # no answer was shown and taken back, and no series was shown under a refusal
        self.assertEqual(sum(int(r["withdrawn"]) for r in new), 0)
        note = src("docs", "methods", "ask_ercot.md")
        for words in ("| The 20 of the four pages | 19 of 20 | 5.0 | 0.0281 |", "| The 100 of before | 98 of 100 | 4.1 | 0.0202 |", "warehouse/chat/eval_ercot_pages_results_153.csv"):
            self.assertIn(words, note, words)
        self.assertNotIn(DASH, src("warehouse", "chat", "eval_ercot_pages_results_153.csv") + src("warehouse", "chat", "eval", "ercot_pages_results.py"))


class TheNodeTests(unittest.TestCase):
    def test_the_sessions_own_tests_pass_with_no_request(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(ROOT, "site", "node_modules")):
            self.skipTest("node or the site's packages are not here")
        # the session's switch is taken out of the child's environment only: this process's is not changed
        env = {k: v for k, v in os.environ.items() if k not in ("ASK_PAGES", "ASK_ROLLUP", "ASK_RULE_PLAN", "ASK_READER_EFFORT", "NEXT_PHASE")}
        r = subprocess.run([node, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-tables.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-2500:] + r.stderr[-1500:])
        self.assertIn("14 of 14 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
