"""Session 3282 (the Ask evaluation chain of 6 November 2026, queue/done/199): the faults the trader's and the investor's
twenty found in the Python loop, each held by a scripted turn over session 1300's fixture rows (tests/test_session1300.py's
Scripted client and Frames), and the grader's two new readings of a key (a text entry's parts joined by "|", a key whose
words must open the answer).

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import test_session1300 as T  # noqa: E402  the scripted client and the fixture's frames
import ask  # noqa: E402
import tools  # noqa: E402

TODAY = "2026-11-06"
CITE = {"table": "merchant_revenue_monthly", "source_report": "erw:merchant_revenue", "data_version": "fixture", "tier": "derived"}


def run(question, turns, prepare=None):
    """One scripted question through the Python loop over the fixture's rows; `prepare` may change the frames first."""
    with T.Frames() as frames:
        client = T.Scripted(turns)
        asker = ask.Asker(model="claude-sonnet-5-5", client=client, record_tools=True)
        frames.load()
        if prepare:
            prepare()
        rec = asker.ask(question, today=TODAY)
        return rec, client


class ALatestOfATextColumn(unittest.TestCase):
    """tr13 and tr14 of the trader set (6 November 2026): the model asked `latest` of price_board_spreads with value_column
    x_gas_date, a text column blank in every row of the live set; tools._num raised ValueError on the blank and the question
    ended with no answer and no record of its cost. The site's loop reads a blank as null. Now the result's value is None and
    the loop goes on to answer from the figure it then fetches."""

    def blank_text_column(self):
        df = tools._frames["merchant_revenue_monthly"]
        tools._frames["merchant_revenue_monthly"] = df.assign(x_gas_date="")

    def test_the_value_of_a_blank_text_column_is_none_and_the_answer_stands(self):
        turns = [
            {"tools": [{"name": "query", "input": {"table": "merchant_revenue_monthly", "aggregation": "latest", "entity": "ercot:HB_HUBAVG",
                                                  "variable": "flat_price", "value_column": "x_gas_date"}}]},
            {"tools": [{"name": "query", "input": {"table": "merchant_revenue_monthly", "aggregation": "latest", "entity": "ercot:HB_HUBAVG",
                                                  "variable": "flat_price"}}]},
        ]
        fx = T.load(T.FIX)
        value = next(r["value"] for r in fx["rows"] if r["table_name"] == "merchant_revenue_monthly" and r["entity"] == "ercot:HB_HUBAVG" and r["variable"] == "flat_price")
        answer = f"ERCOT's hub average flat price was {value} USD/MWh in its latest month (merchant_revenue_monthly)."
        rec, client = run("What was ERCOT's latest flat price, and the date of the gas price behind it?",
                          turns + [{"text": {"answer": answer, "citations": [CITE], "not_in_warehouse": False}}], self.blank_text_column)
        self.assertEqual(rec["status"], "answered")
        self.assertEqual(rec["tool_calls"], 2)
        self.assertEqual(rec["answer"], answer)
        first = rec["trace"][0]["out"]
        self.assertIsNone(first["result"][0]["value"])
        self.assertFalse(rec["trace"][0].get("is_error"))

    def test_num_reads_text_as_no_figure(self):
        self.assertIsNone(tools._num(""))
        self.assertIsNone(tools._num("  "))
        self.assertIsNone(tools._num("2026-11-03"))
        self.assertEqual(tools._num("12.5"), 12.5)
        self.assertEqual(tools._num(7), 7)


class TheGradersReadings(unittest.TestCase):
    """eval_s1113.py grade_set: a text entry with "|" is met by any one of its parts (an hour written in UTC, in local time or
    as the hour ending), and a key marked first: true only when its words open the answer."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("eval_s1113_for_3282", os.path.join(ROOT, "warehouse", "chat", "eval", "eval_s1113.py"))
        self.E = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.E)

    def grade(self, key, record, tmp):
        qpath, rpath, gpath = (os.path.join(tmp, n) for n in ("q.yaml", "r.json", "g.json"))
        lines = ["questions:", f"- id: {key['id']}", "  grid: none", "  via: general", f"  question: {json.dumps('q')}", f"  expected: {json.dumps(key['expected'])}",
                 f"  tolerance: {key.get('tolerance', 0.01)}", f"  text: {json.dumps(key['text'])}", f"  tables: {json.dumps(key['tables'])}",
                 f"  refuse: {'true' if key.get('refuse') else 'false'}", f"  hold: false", f"  first: {'true' if key.get('first') else 'false'}", f"  note: {json.dumps('n')}"]
        with open(qpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump({"questions": [{"id": key["id"], **record}]}, f)
        self.E.SETS["t3282"] = {"questions": qpath, "run": rpath, "grades": gpath}
        return self.E.grade_set("t3282", self.E.G.RULES_2223)["questions"][0]

    def test_an_hour_written_any_listed_way(self):
        import tempfile
        key = {"id": "h1", "expected": [150.0], "text": ["00:00 UTC|18:00|6 p.m.|hour ending 19"], "tables": ["iso_dam_hub_prices"]}
        cit = [{"table": "iso_dam_hub_prices", "source_report": "x", "data_version": "y"}]
        with tempfile.TemporaryDirectory() as tmp:
            for ans, ok in (("The highest was 150.00 USD/MWh at 6 p.m. Central (iso_dam_hub_prices).", True),
                            ("The highest was 150.00 USD/MWh in hour ending 19 (iso_dam_hub_prices).", True),
                            ("The highest was 150.00 USD/MWh at 2026-11-04 00:00 UTC (iso_dam_hub_prices).", True),
                            ("The highest was 150.00 USD/MWh at 3 p.m. (iso_dam_hub_prices).", False)):
                g = self.grade(key, {"status": "answered", "answer": ans, "citations": cit}, tmp)
                self.assertEqual(g["ok"], ok, ans)

    def test_not_in_the_warehouse_opens_the_answer(self):
        import tempfile
        key = {"id": "f1", "expected": [], "text": ["not in the warehouse"], "tables": [], "refuse": True, "first": True}
        with tempfile.TemporaryDirectory() as tmp:
            for ans, ok in (("That figure is not in the warehouse: no table holds project returns.", True),
                            ("No table holds project returns. It is not in the warehouse.", False)):
                g = self.grade(key, {"status": "not_in_warehouse", "not_in_warehouse": True, "answer": ans, "citations": []}, tmp)
                self.assertEqual(g["ok"], ok, ans)
        self.assertEqual(self.E.first_sentence("Not in the warehouse: 1.5 is a decimal. Next."), "Not in the warehouse: 1.5 is a decimal.")


class ARefusalAfterTheList(unittest.TestCase):
    """iv13 to iv15 of the investor set (6 November 2026): asked the months from request to operation by grid, the loop read
    the ISO's queue table, found no duration column and answered "not in the warehouse" without listing the tables, while the
    derived interconnection_durations_summary holds them (iv16 listed the tables and found it). Rule 3 of the prompt both
    loops read (site/lib/chat/spec.json, exported from ask.py) now asks for list_tables before that answer."""

    def test_rule_3_asks_for_the_list_first_in_both_loops(self):
        words = 'Answer "not in the warehouse" only after list_tables has shown no table that holds it'
        self.assertIn(words, ask.SYSTEM)
        with open(os.path.join(ROOT, "site", "lib", "chat", "spec.json"), encoding="utf-8") as f:
            spec = json.load(f)
        self.assertIn(words, spec["system"])
        self.assertEqual(spec["system"], ask.SYSTEM)


if __name__ == "__main__":
    unittest.main()
