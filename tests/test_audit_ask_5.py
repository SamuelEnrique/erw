"""Session 10234 (chain 710, part D): the general chat's answer line names no reason the loop did not give.

docs/reviews/ask-model-audit-2026-11-26.md, finding 5. site/app/ask/AskForm.tsx drew "the first draft was sent back
because a number could not be traced" under every answer whose first draft was sent back. The loop sends a draft back
for a figure in no tool result, and also for a unit, a cited table no tool read, an empty or uncited answer, a refusal
that states a figure, an answer cut short and an answer to a table the site cannot read (site/lib/chat/ask.ts; the same
in warehouse/chat/ask.py). Of the 20 stored answers sent back whose record says why, 3 were sent back for no untraced
number (the audit's a5). Words only: the line says the draft did not pass the checks. Fails on main, passes on the
branch.

The form is drawn to HTML with the site's own code (site/scripts/tsx-register.mjs, no build, no network), its state
given as an answer that was sent back once, when node and the site's packages are here; skipped otherwise.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
FORM = os.path.join(SITE, "app", "ask", "AskForm.tsx")
NEW = "; the first draft did not pass the checks and was sent back once"
OLD = "because a number could not be traced"


class TheAnswerLine(unittest.TestCase):
    def test_the_source(self):
        with open(FORM, encoding="utf-8") as f:
            s = f.read()
        self.assertIn(NEW, s)
        self.assertNotIn(OLD, s)

    def test_the_loop_sends_a_draft_back_for_more_than_a_number(self):
        with open(os.path.join(SITE, "lib", "chat", "ask.ts"), encoding="utf-8") as f:
            a = f.read()
        for words in ("unitMismatches(draft.answer, sources)", "cutShort", "refusalFigures"):
            self.assertIn(words, a)

    def test_the_form_drawn_with_a_retried_answer(self):
        node = shutil.which("node")
        if not node or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's packages are not here")
        tmp = tempfile.mkdtemp(prefix="audit_ask_5_")
        script = os.path.join(tmp, "draw.mjs")
        out = os.path.join(tmp, "form.txt")
        with open(script, "w", encoding="utf-8") as f:
            f.write(DRAW)
        r = subprocess.run([node, "--import", "./scripts/tsx-register.mjs", script, out], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        with open(out, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Answered from the warehouse", text)
        self.assertIn("2 warehouse queries by claude-stand-in; the first draft did not pass the checks and was sent back once; model cost USD 0.0400.", text)
        self.assertNotIn(OLD, text)


# The form's state is handed in by standing in for React's useState before the form is imported (its five states in
# their order: the question, busy, the answer, the error, the turns). Nothing else of the form is changed.
DRAW = r"""
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
const [outFile] = process.argv.slice(2);
const req = createRequire(path.join(process.cwd(), "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const res = { answer: "HB_NORTH averaged 50.80 USD/MWh (iso_dam_hub_prices).", status: "answered", model: "claude-stand-in", tool_calls: 2,
  retried: true, cost_usd: 0.04, citations: [{ table: "iso_dam_hub_prices", source_report: "ercot:NP4-190-CD", data_version: "v", tier: "source" }] };
const states = ["q", false, res, null, [{ question: "q", res }]];
let i = 0;
React.useState = () => [states[i++ % states.length], () => {}];
const { AskForm } = await import(pathToFileURL(path.join(process.cwd(), "app", "ask", "AskForm.tsx")).href);
const html = renderToStaticMarkup(React.createElement(AskForm, {}));
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
fs.writeFileSync(outFile, ent(html.replace(/<[^>]+>/g, "")).replace(/\s+/g, " "));
process.exitCode = 0;
"""


if __name__ == "__main__":
    unittest.main()
