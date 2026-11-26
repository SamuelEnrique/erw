"""Session 10229: print each drawn question and its answer (from draw/sets.json), for reading."""
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for slug, s in d.items():
    print("=" * 10, slug)
    for q in s["questions"]:
        print(f"[{q['id']}] Q: {q['q']}")
        print(f"   A: {q['answer']}")
        print(f"   L: {q['line']}")
        if len(sys.argv) > 2:
            for st in q["steps"]:
                print(f"   S: {st}")
