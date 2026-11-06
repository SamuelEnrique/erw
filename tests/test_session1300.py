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

    def create(self, **kw):
        t = self.turns[min(self.n, len(self.turns) - 1)]
        self.n += 1
        if "tools" in t:
            content = [types.SimpleNamespace(type="tool_use", name=c["name"], input=c["input"], id=f"toolu_fixture_{i + 1}") for i, c in enumerate(t["tools"])]
            return types.SimpleNamespace(stop_reason="tool_use", content=content, usage=Usage(), _request_id="req_fixture")
        return types.SimpleNamespace(stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=json.dumps(t["text"]))], usage=Usage(), _request_id="req_fixture")


class Frames:
    """The fixture's rows as the tools' frames, the backend never asked (as tests/test_session1191.py)."""

    def __enter__(self):
        self.saved = dict(tools._frames), tools._backend_ready, tools.SCOPE
        self.patches = [mock.patch.object(tools.erw, "version", return_value={"backend": "fixture"}),
                        mock.patch.object(tools.erw, "cite", return_value="fixture"),
                        mock.patch.dict(os.environ, {"ASK_HOLD": "on"})]
        for p in self.patches:
            p.start()
        return self

    def load(self):
        """The frames, after an Asker is made: making one sets its scope, which drops the frames read so far."""
        fx = load(FIX)
        turns = load(TURNS)
        if turns.get("extra"):
            # session 1317: a scenario's extra rows, recorded from the live set in another fixture and read from there
            other, t = load(os.path.join(ROOT, turns["extra"]["fixture"])), turns["extra"]["table"]
            rows = next(v for k, v in other["reads"].items() if f"table_name=eq.{t}&" in k)
            fx["rows"] += [{"table_name": t, "entity": r["entity"], "variable": r["variable"], "ts_utc": r["t"], "value": r["v"], "unit": r["unit"]} for r in rows]
            fx["catalogue"].append(next(c for c in next(v for k, v in other["reads"].items() if "/catalogue?" in k) if c["table_name"] == t))
        tools._frames.clear()
        tools._backend_ready = True
        tools._frames["_coverage"] = pd.DataFrame([{"table": c["table_name"], "source_report": c["source_report"], "license": c["license"],
                                                    "tier": c.get("tier"), "last_run": pd.NaT, "ts_min": c.get("ts_min"), "ts_max": c.get("ts_max"),
                                                    "sector": c.get("sector"), "iso": c.get("iso"), "interval": c.get("interval")} for c in fx["catalogue"]])
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
                            "citations": sorted(c.get("table") for c in rec.get("citations") or []), "answer": rec.get("answer"), "why": rec.get("why") or "",
                            "series": [{"result_id": x["result_id"], "table": x["table"], "title": x["title"], "group_by": x["group_by"], "unit": x["unit"],
                                        "rows": [[y["key"], y["value"]] for y in x["rows"]], "check": x["check"]} for x in rec.get("series") or []]}
    return out


def site_loop():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    if not os.path.isdir(os.path.join(SITE, "node_modules")):
        raise unittest.SkipTest("the site's packages are not installed in this copy")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/run-ask-turns-1300.mjs"], cwd=SITE,
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
                          "a_series": "answered"})
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
            for k in ("status", "retried", "tool_calls", "model_calls", "citations", "answer", "why", "series"):
                self.assertEqual(py[sid][k], site[sid][k], f"{sid}: {k}")


if __name__ == "__main__":
    unittest.main()
