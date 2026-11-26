"""Session 10219: resolve a merge conflict by keeping both sides, ours then theirs (for blocks of new constants that
each branch added at the same place). argv: the file. Prints how many blocks it resolved."""
import sys

p = sys.argv[1]
with open(p, encoding="utf-8", newline="") as fh:
    lines = fh.readlines()
out, n = [], 0
for ln in lines:
    s = ln.rstrip("\r\n")
    if s.startswith("<<<<<<< ") or s == "=======" or s.startswith(">>>>>>> "):
        if s.startswith("<<<<<<< "):
            n += 1
        continue
    out.append(ln)
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.writelines(out)
print(p, "blocks kept both:", n)
