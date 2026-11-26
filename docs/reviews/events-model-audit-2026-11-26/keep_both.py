"""Session 10225: resolve git conflict blocks by keeping both sides, ours first, then theirs (each words branch adds
its own lines next to the other's). Usage: python keep_both.py <file> [<file> ...]"""
import sys

for path in sys.argv[1:]:
    with open(path, encoding="utf-8", newline="") as fh:
        lines = fh.read().splitlines(keepends=True)
    out, n = [], 0
    for ln in lines:
        if ln.startswith("<<<<<<< ") or ln.startswith("=======") and ln.strip() == "=======" or ln.startswith(">>>>>>> "):
            n += ln.startswith("<<<<<<< ")
            continue
        out.append(ln)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(out))
    print(f"{path}: {n} blocks resolved, both sides kept")
