"""Session 302: Ask accuracy (the chain prompt of 19 October 2026). What is held to:

  the thirty questions of questions_s302.yaml: ten ERCOT (five through the Grid panel of session 299, five through the
    ERCOT-scoped chat), five CAISO, five on the other grids, five cross-grid comparisons, five it must refuse (PJM's
    prices, a forecast, a year before the tables, MISO paused, a number no table holds), each with the table it must
    read, the number it must state and a note that says how the number was computed;
  the recorded answers (eval_s302_fixtures.json, asked through the real route) replayed without a model: every one
    right by the grader of session 267 (the number, the table, the citation, the refusal); each question that was wrong
    at its first asking carries the cause and the fix;
  the fix at the cause: each grid's scope names the derived tables that hold its rows by hub (docs/grids/grids.json),
    and both tool sets keep such a table to the grid's own rows by its entity prefix, before the market rule;
  no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
EM = chr(0x2014)
FILES = ["warehouse/chat/eval/questions_s302.yaml", "warehouse/chat/eval/eval_s302_fixtures.json", "docs/grids/grids.json", "site/lib/chat/tools.ts",
         "warehouse/chat/tools.py", "warehouse/chat/README.md", "tests/test_session302.py"]
HUB_KEYED = ["cost_of_power_monthly", "cost_of_power_hourly_profile", "merchant_revenue_monthly", "battery_stack_monthly", "battery_stack_stress_daily", "iso_curtailment_monthly"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def grader():
    spec = importlib.util.spec_from_file_location("eval_s267", os.path.join(EVAL, "eval_s267.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def questions():
    qs, cur = [], None
    for line in open(os.path.join(EVAL, "questions_s302.yaml"), encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("- id: "):
            cur = {"id": line[6:].strip()}
            qs.append(cur)
        elif line.startswith("  ") and cur is not None and ": " in line:
            k, v = line[2:].split(": ", 1)
            if k in ("question", "expected", "text", "tables", "note"):
                cur[k] = json.loads(v)
            elif k == "tolerance":
                cur[k] = float(v)
            elif k == "refuse":
                cur[k] = v.strip() == "true"
            else:
                cur[k] = v.strip()
    return qs


class TheQuestions(unittest.TestCase):
    def setUp(self):
        self.qs = questions()

    def test_thirty_in_the_prompts_composition(self):
        qs = self.qs
        self.assertEqual([q["id"] for q in qs], [f"q{i:02d}" for i in range(1, 31)])
        answered = [q for q in qs if not q["refuse"]]
        refused = [q for q in qs if q["refuse"]]
        self.assertEqual(len(refused), 5)
        self.assertEqual(sum(1 for q in answered if q["grid"] == "ERCOT"), 10)
        self.assertEqual(sum(1 for q in answered if q["grid"] == "CAISO"), 5)
        self.assertEqual(sum(1 for q in answered if q["grid"] in ("NYISO", "SPP", "ISO-NE", "US48")), 5)
        self.assertEqual(sum(1 for q in answered if " vs " in q["grid"]), 5)
        self.assertEqual(sum(1 for q in qs if q["via"] == "panel"), 6)                # five ERCOT answers and the forecast, through the Grid panel
        self.assertEqual(sum(1 for q in qs if q["via"] == "panel" and not q["refuse"]), 5)
        self.assertEqual([q["grid"] for q in refused], ["PJM", "ERCOT", "ERCOT", "MISO", "US48"])   # PJM's prices, a forecast, before the tables, paused, not held
        for q in answered:
            self.assertTrue(q["expected"], q["id"])
            self.assertTrue(q["tables"], q["id"])
            self.assertGreater(len(q["note"]), 20, q["id"])
        for q in refused:
            self.assertEqual(q["expected"], [], q["id"])


class TheAnswers(unittest.TestCase):
    def setUp(self):
        self.fx = json.load(open(os.path.join(EVAL, "eval_s302_fixtures.json"), encoding="utf-8"))["questions"]
        self.by = {q["id"]: q for q in questions()}

    def test_every_recorded_answer_is_right_by_the_grader(self):
        G = grader()
        self.assertEqual(len(self.fx), 30)
        for a in self.fx:
            g = G.grade(self.by[a["id"]], a)
            self.assertTrue(g["ok"], (a["id"], g, (a.get("answer") or "")[:120]))
            self.assertEqual(a["verdict"], "right", a["id"])

    def test_the_route_and_the_pages_way_of_asking(self):
        for a in self.fx:
            self.assertEqual(a["http"], 200, a["id"])
            self.assertEqual(a["model"], "claude-sonnet-5-5", a["id"])
            self.assertIn(a["via"], ("panel", "grid", "general"), a["id"])
            self.assertGreater(a["cost_usd"], 0, a["id"])
            if not a["refuse"]:
                self.assertEqual(a["status"], "answered", a["id"])
                self.assertTrue(all(c.get("source_report") and c.get("data_version") for c in a["citations"]), a["id"])
            else:
                self.assertEqual(a["status"], "not_in_warehouse", a["id"])

    def test_each_first_wrong_answer_carries_its_cause_and_fix(self):
        wrong_first = [a for a in self.fx if a.get("first_asking", {}).get("verdict") == "wrong"]
        self.assertEqual(len(wrong_first), 11)
        for a in wrong_first:
            self.assertTrue(a["first_asking"]["cause"], a["id"])
            self.assertTrue(a["first_asking"]["fix"], a["id"])
        scoped = [a for a in wrong_first if a["via"] == "grid"]
        self.assertEqual(len(scoped), 10)
        for a in scoped:
            self.assertEqual(a["first_asking"]["status"], "not_in_warehouse", a["id"])
            self.assertIn("grids.json", a["first_asking"]["cause"])


class TheFix(unittest.TestCase):
    def test_each_grid_scope_names_the_derived_tables_that_hold_its_rows(self):
        g = json.load(open(os.path.join(ROOT, "docs", "grids", "grids.json"), encoding="utf-8"))
        tables = {x["slug"]: set(x["tables"]) for x in g["grids"]}
        for slug in ("ercot", "caiso", "nyiso", "isone", "spp", "miso"):
            self.assertTrue({"cost_of_power_monthly", "cost_of_power_hourly_profile", "merchant_revenue_monthly"} <= tables[slug], slug)
        self.assertTrue({"battery_stack_monthly", "battery_stack_stress_daily"} <= tables["ercot"] & tables["caiso"])
        self.assertTrue({"ercot_hub_prices_daily", "ercot_as_prices", "ercot_as_prices_monthly"} <= tables["ercot"])
        self.assertTrue({"iso_curtailment_monthly"} <= tables["caiso"] & tables["spp"])
        self.assertFalse("iso_curtailment_monthly" in tables["ercot"])          # no ERCOT row in it
        self.assertFalse("cost_of_power_monthly" in tables["pjm"])               # no PJM row in it (its prices are internal)
        self.assertIn("Session 302", g["_about"])

    def test_both_tool_sets_keep_a_hub_keyed_table_to_the_grids_rows_before_the_market_rule(self):
        # session 314: the hand-kept set HUB_KEYED is gone; the rule's file (docs/grids/grid_tables.json, "by") names the
        # tables kept by entity prefix, and both tool sets read it before any column rule (tests/test_session314.py)
        ts = src("site", "lib", "chat", "tools.ts")
        self.assertNotIn("HUB_KEYED", ts)
        prefix = ts.index('if (by === "entity" && shape === "series") return { entity: `like.${scope.slug}:*` };')
        market = ts.index("if (shape === \"series\" && scope.market_prefix && columns.includes(\"market\")) return { market: `like.${scope.market_prefix}*` };")
        self.assertLess(prefix, market)
        py = src("warehouse", "chat", "tools.py")
        self.assertNotIn("HUB_KEYED", py)
        p = py.index('if by == "entity" and "entity" in df.columns:')
        m = py.index('if "market" in df.columns and g.get("market_prefix"):')
        self.assertLess(p, m)
        self.assertIn('return df[df["entity"].fillna("").str.startswith(g["slug"] + ":")]', py)
        ruled = json.load(open(os.path.join(ROOT, "docs", "grids", "grid_tables.json"), encoding="utf-8"))["grids"]
        for t in HUB_KEYED:
            self.assertTrue(any(g["by"].get(t) == "entity" for g in ruled.values()), t)

    def test_no_em_dash_in_any_file_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
