"""Session 6108 (chain 280): the investor's twenty and the lab's twenty through the site's own loop; a percentile's
ordinal is the name of a statistic.

Energy Research Warehouse (ERW).

Window P3 left the two sets unmeasured through the site's loop. Asked on 14 November 2026: the investor's twenty 19 of 20.
The one not right, iv14, was the loop's fixed refusal: the chat had the figure (the median months from request to
operation, CAISO, 2024: 95) and both drafts added the spread from the table's own variables, p25_months and p75_months,
written "the 25th and 75th percentile". The check read 75 as a number in no tool result. An ordinal written before
"percentile" is now the name of that percentile when a tool result or argument names it, in both loops; every other
number is checked as before.

No model, no network.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import ask  # noqa: E402

with open(os.path.join(ROOT, "tests", "fixtures", "session6108", "percentiles.json"), encoding="utf-8") as _f:
    FX = json.load(_f)


def sources_of(a):
    return FX["sources_unnamed"] if a.get("named") is False else FX["sources"]


class APercentilesName(unittest.TestCase):
    def test_each_answer_of_the_fixture(self):
        for a in FX["answers"]:
            self.assertEqual(ask.unverified(a["answer"], sources_of(a)), a["untraced"], a["id"])

    def test_only_the_ordinal_before_the_word_is_taken_out(self):
        self.assertEqual(ask.without_percentile_names(FX["phrase"], FX["sources"]), FX["phrase_stripped"])
        self.assertEqual(ask.without_percentile_names(FX["phrase"], FX["sources_unnamed"]), FX["phrase"])
        self.assertEqual(ask.without_percentile_names("The 75th day and the 25th hour.", FX["sources"]), "The 75th day and the 25th hour.")

    def test_a_percentile_the_query_asked_for_was_traced_before_and_still_is(self):
        """A percentile asked of the query tool is a tool argument (percentile: 90), a number of the sources."""
        src = ['{"table": "iso_dam_hub_prices", "aggregation": "percentile", "percentile": 90}', '{"result": [{"value": 61.2}]}']
        self.assertEqual(ask.unverified("The 90th percentile was 61.2 USD/MWh.", src), [])

    def test_the_site_returns_the_same(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        register = "./scripts/alias-register.mjs"
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            other = os.environ.get("ERW_NODE_MODULES_SITE") or os.path.join(os.path.dirname(ROOT), "erw", "site")
            if not os.path.isdir(os.path.join(other, "node_modules")) or not os.path.exists(os.path.join(SITE, "scripts", "eval-register.mjs")):
                raise unittest.SkipTest("the site's packages are not installed in this copy")
            register = "./scripts/eval-register.mjs"
        r = subprocess.run([exe, "--import", register, "scripts/test-ask-6108.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        line = next(x for x in r.stdout.splitlines() if x.startswith("{"))
        got = json.loads(line)
        self.assertEqual(got["unverified"], {a["id"]: ask.unverified(a["answer"], sources_of(a)) for a in FX["answers"]})
        self.assertEqual(got["stripped"], ask.without_percentile_names(FX["phrase"], FX["sources"]))

    def test_the_stored_answer_that_was_refused(self):
        """iv14 as asked in session 6108: the loop's fixed refusal, with the figure in its third result."""
        path = os.path.join(EVAL, "eval_s6108_site_investor_run.json")
        with open(path, encoding="utf-8") as f:
            q = next(x for x in json.load(f)["questions"] if x["id"] == "iv14")
        self.assertEqual(q["status"], "refused_unverified")
        self.assertIn("p75_months", json.dumps(q["trace"][2]["out"]))
        self.assertIn('"value": 95', json.dumps(q["trace"][2]["out"]))


class AnAnswerCutShort(unittest.TestCase):
    """Session 6109: the lab's l02, a refusal that reached the reader cut at an opening bracket."""

    L02 = "This is not in the warehouse. The energy_deals table, which holds power purchase agreements, is held for a license ("

    def test_what_is_cut_and_what_is_not(self):
        self.assertTrue(ask.cut_short(self.L02))
        for end in ("the price was,", "the tables are:", "it holds;", "see [", "  a set { \n"):
            self.assertTrue(ask.cut_short(end), end)
        for whole in ("49,421.92 MW (eia930_all_demand).", "It was 54.48 USD/MWh", "Not in the warehouse.", "The table is \"license needed\"", "100 percent", ""):
            self.assertFalse(ask.cut_short(whole), whole)

    def test_the_words_sent_back_are_the_sites(self):
        with open(os.path.join(SITE, "lib", "chat", "refused.ts"), encoding="utf-8") as f:
            ts = f.read()
        self.assertIn(f'export const CUT_SHORT = "{ask.CUT_SHORT}";', ts)
        self.assertIn('return t.length > 0 && "([{,:;".includes(t[t.length - 1]);', ts)

    def test_of_the_stored_answers_only_l02_is_cut(self):
        """The measure before the rule: every answer and refusal a loop let through in the stored runs. One is cut, the
        lab's l02 of session 6109, and it was graded not right: no right answer is sent back."""
        import glob
        cut, n = [], 0
        for path in sorted(glob.glob(os.path.join(EVAL, "eval_s*_run.json"))):
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
            for q in doc.get("questions") or []:
                if q.get("status") in ("answered", "not_in_warehouse") and q.get("answer"):
                    n += 1
                    if ask.cut_short(q["answer"]):
                        cut.append((os.path.basename(path), q["id"]))
        self.assertGreaterEqual(n, 880)
        self.assertEqual(cut, [("eval_s6109_site_s2224_run.json", "l02")])

    def test_a_refusal_after_a_held_table_gets_the_holds_words(self):
        held = ask.held_tables({"energy_deals": "table energy_deals is license needed: Reuters; Bloomberg"})
        said = ask.with_refusal_words(ask.with_hold_words("Not in the warehouse. The energy_deals table is held, so no PPA price can be given.", held))
        self.assertEqual(said, "energy_deals: license needed, so no figure of it is given here. Not in the warehouse. The energy_deals table is held, so no PPA price can be given.")
        # a refusal with none of the fixed words gets the hold's, and not "Not in the warehouse." as well
        self.assertEqual(ask.with_refusal_words(ask.with_hold_words("The energy_deals table is held.", held)),
                         "energy_deals: license needed, so no figure of it is given here. The energy_deals table is held.")
        # session 6166: a refusal that does not name the held table gets the refusal's own words, not the hold's
        self.assertEqual(ask.with_refusal_words(ask.with_hold_words("No table holds wildfires.", held)), "Not in the warehouse. No table holds wildfires.")
        # with no table held, as before
        self.assertEqual(ask.with_refusal_words(ask.with_hold_words("The table holds no row.", [])), "Not in the warehouse. The table holds no row.")
        py = open(os.path.join(ROOT, "warehouse", "chat", "ask.py"), encoding="utf-8").read()
        self.assertIn('final = dict(draft, answer=with_refusal_words(with_hold_words(draft["answer"], held_tables(refused_whole_words))))', py)
        ts = open(os.path.join(SITE, "lib", "chat", "ask.ts"), encoding="utf-8").read()
        self.assertIn("answer: withRefusalWords(withHoldWords(draft.answer, heldTables(refusedWholeWords)))", ts)


if __name__ == "__main__":
    unittest.main()
