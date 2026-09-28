#!/usr/bin/env python3
"""Fail if the site's chat spec is older than the briefing it is built from (session 26).

Energy Research Warehouse (ERW). site/lib/chat/spec.json is generated from package/llms.txt, warehouse/chat/ask.py and
warehouse/chat/tools.py by `python warehouse/chat/ask.py --export-spec site/lib/chat/spec.json` (ARCHITECTURE.md). Session
23 changed llms.txt without regenerating it, so the site's /ask ran on an older briefing than the Python chat. This check
regenerates the spec into runs/ and compares it with the committed one: the content, not the file times (a fresh checkout
gives every file the same time), with line endings normalized. Exit 0 when they match, 1 when the committed spec is stale.

    python warehouse/chat/check_spec.py
"""

import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SPEC = os.path.join(ROOT, "site", "lib", "chat", "spec.json")
FRESH = os.path.join(ROOT, "runs", "spec_check.json")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def main():
    os.makedirs(os.path.dirname(FRESH), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "chat", "ask.py"), "--export-spec", FRESH], check=True,
                   stdout=subprocess.DEVNULL)
    if not os.path.exists(SPEC) or read(SPEC) != read(FRESH):
        print("chat spec STALE: site/lib/chat/spec.json does not match package/llms.txt, ask.py and tools.py. Run: "
              "python warehouse/chat/ask.py --export-spec site/lib/chat/spec.json, and commit it with the briefing.")
        return 1
    print("chat spec current: site/lib/chat/spec.json matches package/llms.txt, ask.py and tools.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
