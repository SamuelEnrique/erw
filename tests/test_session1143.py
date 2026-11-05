"""Session 1143 (chain 085): Ask ERCOT on the general chat's rules. Held here: Ask ERCOT's own prompt says the limit its
loop enforces (12 tool calls since session 1111; it said 8), in warehouse/chat/ercot.py and in the spec the site reads;
the refusal's words and the read lines under an answer reach it through the loop it shares (the general refusal of the
spec, ask.ts base()). No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class AskErcotsRules(unittest.TestCase):
    def test_the_limit_it_states_is_the_limit_it_has(self):
        ercot = json.loads(src("site", "lib", "chat", "spec_ercot.json"))
        general = json.loads(src("site", "lib", "chat", "spec.json"))
        self.assertIn(f"6. You have at most {general['max_tool_calls']} tool calls.", ercot["system"])
        self.assertNotIn("at most 8 tool calls", ercot["system"])
        self.assertIn("6. You have at most 12 tool calls.", src("warehouse", "chat", "ercot.py"))

    def test_the_shared_loop_carries_the_rest(self):
        self.assertNotIn("refusal", json.loads(src("site", "lib", "chat", "spec_ercot.json")))   # its refusal is the general one
        loop = src("site", "lib", "chat", "ask.ts")
        self.assertIn("answer: `${spec.refusal} ${why}`.trim()", loop)
        self.assertIn("...(readsLog.length ? { reads: readsLog } : {})", loop)


if __name__ == "__main__":
    unittest.main()
