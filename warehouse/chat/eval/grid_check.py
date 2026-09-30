#!/usr/bin/env python3
"""Session 35, Part C: one question to each grid page's scoped chat (ask.py --grid), seven asks.

Energy Research Warehouse (ERW). Each answer must cite a table or the grid's written layer and state no number it did
not fetch (the loop's own post-check). Every call goes through the cost ledger (warehouse/llm.py); run with
ERW_SESSION and ERW_SPEND_CAP_USD set. The records are written to warehouse/chat/eval/results/<run>_grids.json.

    ERW_SESSION=35 ERW_SPEND_CAP_USD=3 python warehouse/chat/eval/grid_check.py
"""

import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ask  # noqa: E402

QUESTIONS = [
    ("ercot", "What was ERCOT's highest hourly demand in the last 30 days, and in which hour?"),
    ("caiso", "How many MWh did CAISO's batteries discharge on the latest complete day, and how many did they charge?"),
    ("pjm", "Who runs the PJM grid, and what is its capacity market called?"),
    ("nyiso", "What was the latest day-ahead daily mean price in NYISO's New York City zone?"),
    ("isone", "What was ISO New England's carbon intensity of generation in the latest month you hold?"),
    ("miso", "How many active solar projects are in MISO's interconnection queue, and how many MW do they add up to?"),
    ("spp", "What makes SPP different from other grids, and how much wind did it generate over the last 7 days you hold?"),
]


def main():
    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = []
    for grid, q in QUESTIONS:
        rec = ask.Asker(grid=grid).ask(q)
        out.append(rec)
        print(f"[{grid}] {rec['status']}; tools {rec['tool_calls']}; cost {rec['cost_usd']}; cites "
              f"{[c['table'] for c in rec['citations']]}\n  {rec['answer']}\n", flush=True)
    path = os.path.join(HERE, "results", f"{run}_grids.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"wrote {os.path.relpath(path)}; total USD {sum(r['cost_usd'] or 0 for r in out):.4f}")


if __name__ == "__main__":
    main()
