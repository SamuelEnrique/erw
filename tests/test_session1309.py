"""Session 1309 (chain 095): the site's checks and the Python checks give the same verdict on the stored answers.

Every answer warehouse/chat/eval/replay.py replays (157 on 23 October 2026), with its sources built as the replay builds
them, and a copy of each with one figure moved (so that answers the checks catch are compared too, not only answers
they let through), run through the number check and the unit check of both loops: warehouse/chat/ask.py (unverified,
unit_mismatches) and site/lib/chat/ask.ts (unverified, unitMismatches, by site/scripts/run-checks-1309.mjs). Each case's
two lists are the same.
No network, no model. Nothing here sets the environment at import.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def replay():
    if EVAL not in sys.path:
        sys.path.insert(0, EVAL)
    import replay as R  # noqa: E402
    return R


def sources_of(R, q):
    trace = R.trace_of(q) or []
    today = (q.get("asked_at_utc") or "")[:10]
    return [q.get("question") or "", f"Today is {today} (UTC)."] + [json.dumps(t.get("out"), default=str) for t in trace] \
        + [json.dumps(t.get("input"), default=str) for t in trace]


def cases():
    R = replay()
    out = []
    for name, _, label in R.RUNS:
        for q in R.load(name)["questions"]:
            if not R.trace_of(q) or not q.get("answer") or q.get("status") not in ("answered", "not_in_warehouse"):
                continue
            src = sources_of(R, q)
            out.append({"key": f"{label}|{q['id']}", "answer": q["answer"], "sources": src})
            m = re.search(r"\d+\.\d+", q["answer"])
            if m:
                moved = f"{float(m.group()) + 7.13:.{len(m.group().split('.')[1])}f}"
                out.append({"key": f"{label}|{q['id']}|moved", "answer": q["answer"][:m.start()] + moved + q["answer"][m.end():], "sources": src})
    return out


class BothChecks(unittest.TestCase):
    def test_the_same_verdict_on_every_stored_answer(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        R = replay()
        cs = cases()
        self.assertGreater(len(cs), 250)
        tmp = tempfile.mkdtemp(prefix="erw1309_")
        try:
            src, dst = os.path.join(tmp, "cases.json"), os.path.join(tmp, "out.json")
            with open(src, "w", encoding="utf-8") as f:
                json.dump(cs, f)
            r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/run-checks-1309.mjs", src, dst], cwd=SITE,
                               capture_output=True, text=True, timeout=600, encoding="utf-8")
            if r.returncode != 0 and "Unknown file extension" in r.stderr:
                raise unittest.SkipTest("this node does not read TypeScript files")
            self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
            with open(dst, encoding="utf-8") as f:
                site = json.load(f)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        differ = []
        caught = 0
        for c in cs:
            py = {"numbers": R.ask.unverified(c["answer"], c["sources"]), "units": R.ask.unit_mismatches(c["answer"], c["sources"])}
            if py != site[c["key"]]:
                differ.append((c["key"], py, site[c["key"]]))
            caught += bool(py["numbers"] or py["units"])
        self.assertEqual(differ[:5], [])
        self.assertGreater(caught, 100)   # the moved copies are caught: the comparison is not of empty lists only


if __name__ == "__main__":
    unittest.main()
