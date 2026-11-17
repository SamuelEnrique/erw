"""Session 7611 (portable-laptop): mark one tool's row of docs/state/ruling_impact_claims.md done (exactly one row must match)."""
import sys

tool, session = sys.argv[1], sys.argv[2]
path = "docs/state/ruling_impact_claims.md"
raw = open(path, "rb").read().decode("utf-8")
old = f"| {tool} | portable-laptop | {session} | claimed |"
new = f"| {tool} | portable-laptop | {session} | done |"
n = raw.count(old)
assert n == 1, f"{n} rows match {old!r}"
open(path, "wb").write(raw.replace(old, new).encode("utf-8"))
print("marked done:", tool)
