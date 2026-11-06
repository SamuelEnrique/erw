"""Session 1145 (chain 085): Ask beside the board, and the general chat's form brought to what the route returns.

Held here: the general chat and the six other grids' chats are drawn by app/ask/AskForm.tsx (the Grid tool's AskView;
only Ask ERCOT uses components/ask/AskPanel.tsx), which drew the answer and its sources only. It now draws, as the
panel does, the lines of what each query read (session 1115), the time the answer took, the nearest tables of a
refusal (session 1132), the series an answer rests on (session 1142, the panel's own SeriesBlock), the refusal's words
(session 1110), and it keeps the conversation (session 1129: the last three turns sent, a "New conversation" button).
The board page carries the form with the five board questions (site/data/board_questions.json, written by
warehouse/chat/eval/expected_s1122.py from questions_s1122.yaml) as examples a reader can click; a click places the
question in the box and sends nothing. No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheForm(unittest.TestCase):
    def test_the_form_draws_what_the_route_returns(self):
        f = src("site", "app", "ask", "AskForm.tsx")
        # session 1194: the reads under an answer are drawn by components/ask/AnswerSources.tsx, the form passes them
        self.assertIn("data-reads={rs.length}", src("site", "components", "ask", "AnswerSources.tsx"))
        for words in ("<AnswerSources citations={res.citations} reads={res.reads} />", "Answered in {res.seconds.toFixed(1)} seconds", "data-nearest={res.nearest!.length}",
                      "<SeriesBlock key={s.result_id} s={s} form=\"chart\" />", 'refused_unverified: "The warehouse does not hold that figure"',
                      "...(history.length ? { history } : {})", 'data-new-conversation="1"', "onClick={() => setQ(x)}"):
            self.assertIn(words, f)
        self.assertIn("export function SeriesBlock", src("site", "components", "ask", "AskPanel.tsx"))

    def test_the_board_asks_its_own_questions(self):
        page = src("site", "app", "board", "page.tsx")
        self.assertIn('import boardQuestions from "@/data/board_questions.json";', page)
        self.assertIn('<AskForm examples={BOARD_QUESTIONS}', page)
        self.assertIn('data-board-ask="1"', page)
        qs = json.loads(src("site", "data", "board_questions.json"))["questions"]
        keys = json.loads(src("warehouse", "chat", "eval", "expected_s1122.json"))["questions"]
        self.assertEqual([q["question"] for q in qs], [k["question"] for k in keys])
        self.assertEqual(len(qs), 5)


if __name__ == "__main__":
    unittest.main()
