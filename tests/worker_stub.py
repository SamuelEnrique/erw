#!/usr/bin/env python3
"""A stand-in for Claude Code in the worker's tests and the end-to-end check (session 59): python scripts/worker.py
--runner "python tests/worker_stub.py". Takes Claude's flags, reads the prompt on stdin, follows the lines in it that
start with "STUB:", and prints a result in the shape of claude -p --output-format json. Spends nothing.

    STUB: write <path> <text>      write the file (relative to the checkout) and commit it
    STUB: require-lock             call warehouse/lock.py's require() for a file in warehouse/output: passes only under
                                   the data lock
    STUB: usage-limit-once         the first run answers with a usage limit; the resumed run goes on
"""

import json
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def out(result, error=False, session="stub-session"):
    print(json.dumps({"type": "result", "subtype": "error_during_execution" if error else "success", "is_error": error,
                      "result": result, "total_cost_usd": 0.0, "session_id": session, "num_turns": 1}))
    sys.exit(1 if error else 0)


def main():
    args = sys.argv[1:]
    prompt = sys.stdin.read()
    resumed = "--resume" in args
    task = os.environ.get("ERW_QUEUE_TASK", "task")
    marker = os.path.join(ROOT, ".erw", "worker", f"stub-limit-{task}")
    done = []
    if resumed and os.path.exists(marker):  # a resumed session gets "continue": like Claude, the stub picks up the task it had
        with open(marker, encoding="utf-8") as f:
            prompt = f.read()
        os.remove(marker)
        done.append("resumed after a usage limit")
    for ln in prompt.splitlines():
        if not ln.startswith("STUB:"):
            continue
        cmd = ln[5:].strip()
        if cmd == "usage-limit-once" and not resumed and not os.path.exists(marker):
            os.makedirs(os.path.dirname(marker), exist_ok=True)
            with open(marker, "w", encoding="utf-8") as f:
                f.write(prompt)  # the session's memory, for the resume
            out(f"Claude AI usage limit reached|{int(time.time()) + 5}", error=True)
        elif cmd == "usage-limit-once":
            continue
        elif cmd.startswith("write "):
            _, path, text = cmd.split(" ", 2)
            full = os.path.join(ROOT, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="\n") as f:
                f.write(text + "\n")
            subprocess.run(["git", "add", path], cwd=ROOT, check=True)
            subprocess.run(["git", "commit", "-q", "-m", f"queue stub: write {path}"], cwd=ROOT, check=True)
            done.append(f"wrote and committed {path}")
        elif cmd == "require-lock":
            r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, 'warehouse'); import lock; "
                                "lock.require('warehouse/output/x.csv', 'the stub data write'); print('lock ok')"],
                               cwd=ROOT, capture_output=True, text=True, env={**os.environ, "ERW_LOCK_EXEMPT": ""})
            if r.returncode != 0:
                out(f"the data lock check failed: {(r.stderr or r.stdout).strip()[-300:]}", error=True)
            done.append("the data lock check passed (lock.require in warehouse/output)")
    out("Stub run. " + "; ".join(done or ["nothing to do"]) + ".")


if __name__ == "__main__":
    main()
