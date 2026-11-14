"""Session 1300 (chain 093): the two loops answer alike, turn by turn.

The same scripted model turns (tests/fixtures/session1300/turns.json: an answer, a figure in no result sent back and
refused, a compare, a refusal, a table cited but never read, a held grid's question) run through the Python loop
(warehouse/chat/ask.py Asker, a fake client replaying the turns, the tools reading the rows of
tests/fixtures/session1112/held_reads.json, the hold on as the site's) and through the site's (lib/chat/ask.ts, by
site/scripts/run-ask-turns-1300.mjs over the same rows): each scenario's status, whether it was sent back, its tool
calls, its model calls, its cited tables, its answer and its reason are the same. Session 1191 compared the two tool by
tool; this compares what a reader is given.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import types
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CHAT = os.path.join(ROOT, "warehouse", "chat")
sys.path.insert(0, CHAT)
import ask  # noqa: E402
import tools  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session1112", "held_reads.json")
TURNS = os.path.join(ROOT, "tests", "fixtures", "session1300", "turns.json")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Usage:
    input_tokens = output_tokens = 0
    cache_creation_input_tokens = cache_read_input_tokens = 0


class Scripted:
    """The scenario's turns in order, whatever is sent; the last one again if the loop asks for more."""

    def __init__(self, turns):
        self.turns, self.n = turns, 0
        self.messages = self
        self.choices = []   # session 2222: what each call allowed (auto: tools; none: write only), as the site's runner records it

    def create(self, **kw):
        t = self.turns[min(self.n, len(self.turns) - 1)]
        self.n += 1
        self.choices.append((kw.get("tool_choice") or {}).get("type"))
        if t.get("cut"):
            # session 5272: a reply that stops at the model's output limit: a thinking block, no text
            return types.SimpleNamespace(stop_reason="max_tokens", content=[types.SimpleNamespace(type="thinking", thinking="")], usage=Usage(), _request_id="req_fixture")
        if "tools" in t:
            content = [types.SimpleNamespace(type="tool_use", name=c["name"], input=c["input"], id=f"toolu_fixture_{i + 1}") for i, c in enumerate(t["tools"])]
            return types.SimpleNamespace(stop_reason="tool_use", content=content, usage=Usage(), _request_id="req_fixture")
        return types.SimpleNamespace(stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=json.dumps(t["text"]))], usage=Usage(), _request_id="req_fixture")


def no_fetch(name, *args, **kwargs):
    raise tools.erw.ERWDataNotFound(f"{name} is not in the fixture")


class Frames:
    """The fixture's rows as the tools' frames, the backend never asked (as tests/test_session1191.py)."""

    def __enter__(self):
        self.saved = dict(tools._frames), tools._backend_ready, tools.SCOPE
        self.patches = [mock.patch.object(tools.erw, "version", return_value={"backend": "fixture"}),
                        mock.patch.object(tools.erw, "cite", return_value="fixture"),
                        # session 5256: the fixture stands for the live set, so a table with no rows in it cannot be read, as the
                        # live set answers for a table of the record it does not hold (the scenario a_table_not_in_the_live_set)
                        mock.patch.object(tools, "live_only", return_value=True),
                        mock.patch.object(tools.erw, "fetch", side_effect=no_fetch),
                        mock.patch.dict(os.environ, {"ASK_HOLD": "on"})]
        for p in self.patches:
            p.start()
        return self

    def load(self):
        """The frames, after an Asker is made: making one sets its scope, which drops the frames read so far."""
        fx = load(FIX)
        turns = load(TURNS)
        extras = turns.get("extra") or []
        for extra in (extras if isinstance(extras, list) else [extras]):
            # session 1317: a scenario's extra rows, recorded from the live set in another fixture and read from there;
            # session 2221: a list of them, and a fixture that holds plain rows (session 1109's) beside one of recorded reads
            other, t = load(os.path.join(ROOT, extra["fixture"])), extra["table"]
            if "reads" in other:
                rows = next(v for k, v in other["reads"].items() if f"table_name=eq.{t}&" in k)
                fx["rows"] += [{"table_name": t, "entity": r["entity"], "variable": r["variable"], "ts_utc": r["t"], "value": r["v"], "unit": r["unit"]} for r in rows]
                fx["catalogue"].append(next(c for c in next(v for k, v in other["reads"].items() if "/catalogue?" in k) if c["table_name"] == t))
            else:
                fx["rows"] += [r for r in other["rows"] if r["table_name"] == t]
                fx["catalogue"].append(next(c for c in other["catalogue"] if c["table_name"] == t))
        tools._frames.clear()
        tools._backend_ready = True
        tools._frames["_coverage"] = pd.DataFrame([{"table": c["table_name"], "source_report": c["source_report"], "license": c["license"],
                                                    "tier": c.get("tier"), "last_run": pd.NaT, "ts_min": c.get("ts_min"), "ts_max": c.get("ts_max"),
                                                    "sector": c.get("sector"), "iso": c.get("iso"), "interval": c.get("interval"),
                                                    # session 5256: what list_tables reads besides (the new scenario lists the tables)
                                                    "n_rows": c.get("n_rows") or 0, "derived": c.get("derived") or "no"} for c in fx["catalogue"]])
        rows = pd.DataFrame(fx["rows"])
        for t, df in rows.groupby("table_name"):
            df = df.drop(columns=["table_name"]).reset_index(drop=True)
            df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
            df["freq"] = next((c.get("interval") for c in fx["catalogue"] if c["table_name"] == t), None) or "P1M"
            tools._frames[t] = df
        return fx

    def __exit__(self, *exc):
        for p in reversed(self.patches):
            p.stop()
        tools._frames.clear()
        tools._frames.update(self.saved[0])
        tools._backend_ready, tools.SCOPE = self.saved[1], self.saved[2]
        tools._cites.clear()


def python_loop():
    out = {}
    turns = load(TURNS)
    with Frames() as frames:
        for s in turns["scenarios"]:
            client = Scripted(s["turns"])
            asker = ask.Asker(model="claude-sonnet-5-5", client=client)
            frames.load()
            rec = asker.ask(s["question"], today=turns["today"])
            out[s["id"]] = {"status": rec.get("status"), "retried": bool(rec.get("retried")), "tool_calls": rec.get("tool_calls"), "model_calls": client.n,
                            "tool_choices": client.choices, "reads": len(rec.get("reads") or []),
                            "citations": sorted(c.get("table") for c in rec.get("citations") or []), "answer": rec.get("answer"), "why": rec.get("why") or "",
                            "series": [{"result_id": x["result_id"], "table": x["table"], "title": x["title"], "group_by": x["group_by"], "unit": x["unit"],
                                        "rows": [[y["key"], y["value"]] for y in x["rows"]], "check": x["check"]} for x in rec.get("series") or []]}
    return out


def site_loop():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    register = "./scripts/alias-register.mjs"
    if not os.path.isdir(os.path.join(SITE, "node_modules")):
        # session 5256: a git worktree with no packages of its own reads the main checkout's, where they stand, through
        # scripts/eval-loader.mjs (session 5202): nothing is installed, linked or copied
        other = os.environ.get("ERW_NODE_MODULES_SITE") or os.path.join(os.path.dirname(ROOT), "erw", "site")
        if not os.path.isdir(os.path.join(other, "node_modules")) or not os.path.exists(os.path.join(SITE, "scripts", "eval-register.mjs")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        register = "./scripts/eval-register.mjs"
    r = subprocess.run([exe, "--import", register, "scripts/run-ask-turns-1300.mjs"], cwd=SITE,
                       capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stdout[-2000:] + r.stderr[-2000:])
    lines = [x for x in r.stdout.splitlines() if x.startswith("{") and not x.startswith('{"erw_ask_check"')]
    return json.loads(lines[-1])


class ThePythonLoop(unittest.TestCase):
    def test_each_scenario_ends_as_written(self):
        got = python_loop()
        self.assertEqual({k: v["status"] for k, v in got.items()},
                         {"answered": "answered", "a_figure_in_no_result": "refused_unverified", "a_compare": "answered",
                          "not_in_the_warehouse": "not_in_warehouse", "a_table_cited_unread": "refused_unverified", "a_held_grid": "answered",
                          "a_series": "answered", "a_per_kw_question": "answered", "a_repeated_call": "answered",
                          "a_table_held_whole": "not_in_warehouse", "misos_pause": "not_in_warehouse", "a_threshold_count": "answered",
                          "a_table_not_in_the_live_set": "not_in_warehouse", "a_refused_table_asked_again": "not_in_warehouse",
                          "a_held_grids_own_table": "not_in_warehouse",
                          "an_answer_cut_off_then_written": "answered", "an_answer_cut_off_twice": "refused_unverified"})
        # session 5272 (chain 256): a reply cut off at the model's output limit (its thinking counts toward the limit; three
        # askings of 14 November 2026 ended so and the loops threw). The cut-off reply is dropped and the model is told once:
        # the call after it may only write, and the answer it writes stands, checked as any other. One query, one read,
        # three model calls, the third with no tool; not "retried", which is a draft sent back by the number check
        r = got["an_answer_cut_off_then_written"]
        self.assertEqual((r["tool_calls"], r["reads"], r["retried"], r["model_calls"], r["tool_choices"]), (1, 1, False, 3, ["auto", "auto", "none"]))
        self.assertEqual((r["answer"], r["citations"]), (got["answered"]["answer"], ["cost_of_power_monthly"]))
        # cut off a second time, the question ends in the cut-off's own words: no figure, no citation, and no error raised
        r = got["an_answer_cut_off_twice"]
        self.assertEqual((r["tool_calls"], r["reads"], r["retried"], r["model_calls"], r["tool_choices"]), (1, 1, False, 3, ["auto", "auto", "none"]))
        self.assertEqual((r["answer"], r["why"], r["citations"]), (ask.CUT_OFF_ANSWER, ask.CUT_OFF_WHY, []))
        self.assertIsNone(re.search(r"\d", r["answer"] + r["why"]))
        # session 5260 (chain 238, the platform set's pj08): a held grid's own table of things (ISO New England's queue) is
        # refused by name with the hold's words, as a table held whole is; its description, asked next, is not read either
        r = got["a_held_grids_own_table"]
        self.assertEqual((r["tool_calls"], r["reads"], r["retried"], r["model_calls"], r["tool_choices"]), (2, 0, False, 3, ["auto", "auto", "none"]))
        self.assertIn("license needed", r["answer"])
        # session 5256: told once that a table cannot be read, a model that asks it again with other arguments is not obeyed:
        # the two later calls are counted and not made, and the call after that turn may only write
        r = got["a_refused_table_asked_again"]
        self.assertEqual((r["tool_calls"], r["reads"], r["retried"], r["model_calls"], r["tool_choices"]), (3, 0, False, 3, ["auto", "auto", "none"]))
        # session 5256 (chain 238, the platform set's oi07): a table the catalogue lists and the live set does not hold. Its
        # query is refused with words that say how to answer; a first draft that answers as an answer, with the refused table
        # as its source, is sent back (list_tables naming a table does not make it the source of an answer), and the second,
        # a refusal, stands: two tool calls, no read, four model calls
        r = got["a_table_not_in_the_live_set"]
        self.assertEqual((r["tool_calls"], r["reads"], r["retried"], r["model_calls"], r["citations"], r["why"]), (2, 0, True, 4, [], ""))
        self.assertIn("on Redivis and not in the live set", r["answer"])
        # session 3297 (the trader set's tr15): a count past a value threshold, answered at the first draft from the tool's count
        r = got["a_threshold_count"]
        self.assertEqual((r["tool_calls"], r["reads"], r["retried"]), (1, 1, False))
        self.assertIn("in 3 of the 12 years", r["answer"])
        # session 2225 (chain 152): a table held whole is refused by name with the hold's words, MISO's rows with the pause's,
        # and the answer is a refusal that carries those words and no figure
        self.assertIn("license needed", got["a_table_held_whole"]["answer"])
        self.assertIn("paused while terms are reviewed", got["misos_pause"]["answer"])
        for sid in ("a_table_held_whole", "misos_pause"):
            self.assertEqual((got[sid]["tool_calls"], got[sid]["reads"], got[sid]["retried"]), (1, 0, False), sid)
        # session 2222 (chain 152): the second, identical call is counted and not read (one read in the record), and the turn of only
        # repeats makes the third model call one that may not read
        r = got["a_repeated_call"]
        self.assertEqual((r["tool_calls"], r["reads"], r["model_calls"], r["tool_choices"]), (2, 1, 3, ["auto", "auto", "none"]))
        self.assertEqual(got["answered"]["tool_choices"], ["auto", "auto"])
        # session 2221 (chain 152): a question in USD per kW answered with the tool's own value_usd_per_kw passes the number
        # check at the first draft (before, the per-kW figure was in no result and the draft was sent back)
        self.assertFalse(got["a_per_kw_question"]["retried"])
        self.assertIn("81.40 USD per kW", got["a_per_kw_question"]["answer"])
        # session 1317: the general chat's answer that rests on a series carries it, the tool's twelve rows; the others none
        s = got["a_series"]["series"]
        self.assertEqual(len(s), 1)
        self.assertEqual((s[0]["table"], s[0]["group_by"], len(s[0]["rows"]), s[0]["check"]["same"]), ("ercot_peak_premium_annual", "year", 12, True))
        self.assertEqual(s[0]["rows"][0], ["2015", -0.16])
        self.assertTrue(all(not v["series"] for k, v in got.items() if k != "a_series"))
        self.assertTrue(got["a_figure_in_no_result"]["retried"])
        self.assertTrue(got["a_figure_in_no_result"]["answer"].startswith(ask.REFUSAL))


class BothLoops(unittest.TestCase):
    def test_the_same_turn_by_turn(self):
        site = site_loop()
        py = python_loop()
        self.assertEqual(sorted(site), sorted(py))
        for sid in site:
            for k in ("status", "retried", "tool_calls", "model_calls", "tool_choices", "reads", "citations", "answer", "why", "series"):
                self.assertEqual(py[sid][k], site[sid][k], f"{sid}: {k}")


if __name__ == "__main__":
    unittest.main()
