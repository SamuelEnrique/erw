"""Session 10234 (chain 710, part D): a held grid's question is headed "Answered from the warehouse".

docs/reviews/ask-model-audit-2026-11-26.md, finding 8. When a question asks for a held grid's rows, both loops' tools
answer with the hold's words, the public grids' figures and the instruction "Answer with not_in_warehouse false"
(site/lib/chat/tools.ts, warehouse/chat/tools.py), so the answer's status is "answered", which the general form heads
"Answered from the warehouse" (site/app/ask/AskForm.tsx STATUS) above a first sentence that says the grid's rows are
held. In the stored runs 45 of the 48 held-grid questions ended so (the audit's a6). This shows it; it changes nothing.
Whether a held answer gets a status and a heading of its own is Samuel's ruling. Passes on main. No node, no network.
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class AHeldGridsQuestion(unittest.TestCase):
    def test_the_tools_ask_for_an_answer_not_a_refusal(self):
        self.assertIn("Answer with not_in_warehouse false: say first that ${name}'s rows are held for a license", read("site", "lib", "chat", "tools.ts"))
        self.assertIn("Answer with not_in_warehouse false: say first that {name}'s rows are held for a license", read("warehouse", "chat", "tools.py"))

    def test_the_form_heads_an_answer_answered_from_the_warehouse(self):
        f = read("site", "app", "ask", "AskForm.tsx")
        self.assertIn('answered: "Answered from the warehouse",', f)
        self.assertNotIn("held", f.split("const STATUS")[1].split("};")[0])   # no heading of its own for a held answer


if __name__ == "__main__":
    unittest.main()
