"""Audit of /equities, session 11403: every version of the equities list, board and energy price files in the public
repository's history, checked for a held value (a share price, an index level, a market value, a held grid's price).
Prints counts only. No request, no write (git show only)."""
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, encoding="utf-8").stdout


bad = 0
for name in ("index.json", "board.json", "energy_prices.json"):
    path = f"site/data/equities/{name}"
    shas = git("log", "--format=%h", "origin/main", "--", path).split()
    for sha in shas:
        txt = git("show", f"{sha}:{path}")
        if not txt.strip():
            continue
        d = json.loads(txt)
        hits = []
        if name == "index.json":
            for c in d.get("companies", []):
                if c.get("last_close") or c.get("market_value") or any((c.get("moves") or {}).values()):
                    hits.append(c.get("ticker"))
            if d.get("indices") and any(x.get("status") == "shown" for x in d["indices"]):
                hits.append("an index shown")
        elif name == "board.json":
            hits = [r["id"] for r in d.get("rows", []) if r.get("last") or r.get("spark")]
        else:
            for s in d.get("series", []):
                if s.get("status") != "shown" and (d.get("daily", {}).get(s["id"]) or s.get("last_value")):
                    hits.append(s["id"])
        if hits:
            bad += 1
            print(f"{sha} {path}: {len(hits)} held values ({hits[:5]})")
    print(f"{path}: {len(shas)} versions read")
print(f"versions with a held value: {bad}")
