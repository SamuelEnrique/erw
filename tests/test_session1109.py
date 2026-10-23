"""Session 1109 (chain 075): the query tool on session 320's eight per-kW questions, on saved rows, no model.

Held here: the saved rows (tests/fixtures/session1109/battery_reads.json, written by
warehouse/chat/eval/fixture_s1109.py from battery_stack_monthly) sum, for each of b01 to b06, b08 and b09, to the
question's key times 1,000 (USD per MW against the key's USD per kW); warehouse/chat/tools.py per_kw adds the per-kW
figure only with ASK_PER_KW=on, for a table whose method names the conversion and rows all in USD/MW, and leaves a result
as it was otherwise; and site/scripts/test-ask-1109.mjs holds the same of site/lib/chat/tools.ts on the same rows.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CHAT = os.path.join(ROOT, "warehouse", "chat")
FIX = os.path.join(ROOT, "tests", "fixtures", "session1109", "battery_reads.json")


def fixture():
    with open(FIX, encoding="utf-8") as f:
        return json.load(f)


def chat_tools():
    if CHAT not in sys.path:
        sys.path.insert(0, CHAT)
    import tools  # noqa: E402
    return tools


class TheRows(unittest.TestCase):
    def test_each_question_sums_to_its_key_times_a_thousand(self):
        fx = fixture()
        self.assertEqual(sorted(fx["questions"]), ["b01", "b02", "b03", "b04", "b05", "b06", "b08", "b09"])
        for qid, q in fx["questions"].items():
            rows = [r for r in fx["rows"] if r["entity"] == q["entity"] and r["variable"] == q["variable"]
                    and q["start"] <= r["ts_utc"][:10] < q["end"]]
            self.assertEqual(len(rows), 12, qid)
            self.assertTrue(all(r["unit"] == "USD/MW" for r in rows), qid)
            total = sum(r["value"] for r in rows)
            self.assertAlmostEqual(total, q["sum_usd_per_mw"], places=4)
            self.assertLessEqual(abs(total / 1000 - q["key_usd_per_kw"]), 0.01, qid)

    def test_the_rows_are_dated_the_first_of_the_month_at_midnight_utc(self):
        for r in fixture()["rows"]:
            self.assertTrue(r["ts_utc"].endswith("-01T00:00:00+00:00"), r["ts_utc"])


class PerKw(unittest.TestCase):
    def setUp(self):
        self.t = chat_tools()

    def base(self):
        return {"units": ["USD/MW"], "result": [{"value": 81402.1896}]}

    def test_off_by_default_the_result_is_unchanged(self):
        out = self.base()
        self.assertEqual(self.t.per_kw(out, "battery_stack_monthly", env={}), self.base())
        self.assertEqual(self.t.per_kw(self.base(), "battery_stack_monthly", env={"ASK_PER_KW": "1"}), self.base())

    def test_on_the_figure_divided_by_a_thousand(self):
        out = self.t.per_kw(self.base(), "battery_stack_monthly", env={"ASK_PER_KW": "on"})
        self.assertAlmostEqual(out["result"][0]["value_usd_per_kw"], 81.4021896, places=6)
        self.assertEqual(out["per_kw"]["unit"], "USD/kW")
        self.assertIn("battery_stack.md", out["per_kw"]["rule"])

    def test_only_the_named_table_and_rows_all_in_usd_per_mw(self):
        on = {"ASK_PER_KW": "on"}
        self.assertNotIn("per_kw", self.t.per_kw(self.base(), "merchant_revenue_monthly", env=on))
        mixed = {"units": ["USD/MW", "count"], "result": [{"value": 3}]}
        self.assertNotIn("per_kw", self.t.per_kw(mixed, "battery_stack_monthly", env=on))

    def test_both_languages_name_the_same_tables(self):
        with open(os.path.join(SITE, "lib", "chat", "tools.ts"), encoding="utf-8") as f:
            ts = f.read()
        for name, rule in self.t.PER_KW_TABLES.items():
            self.assertIn(f'{name}: "{rule}"', ts)


class TheSiteTool(unittest.TestCase):
    def test_the_site_tool_on_the_same_rows(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/test-ask-1109.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("5 of 5 passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
