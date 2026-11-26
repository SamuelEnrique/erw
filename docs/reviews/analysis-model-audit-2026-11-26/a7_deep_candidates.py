"""Audit of Automated Analysis (session 10204): the deep hunt's candidates, counted from its own modules.

Imports every module of warehouse/analysis/findings/deep/ that defines CANDIDATES (no table read: a candidate's
function runs only when the builder calls it) and prints, per module: the candidates, those in a dollar unit, and of
those how many say in their limits that the dollars are nominal (not adjusted for inflation). Also prints each
candidate's unit, its first_words and its n_floor.

Run: python runs/a7_deep_candidates.py > runs/a7.out
"""
import glob
import importlib
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEEP = os.path.join(ROOT, "warehouse", "analysis", "findings", "deep")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, DEEP)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


def main():
    total, usd, usd_nominal, floor1 = 0, 0, 0, 0
    rows = []
    for path in sorted(glob.glob(os.path.join(DEEP, "*.py"))):
        name = os.path.basename(path)[:-3]
        if name in ("__init__", "builder", "check", "check_cards", "check_do", "rank", "redraw"):
            continue
        try:
            m = importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: not imported: {type(exc).__name__}: {str(exc)[:120]}")
            continue
        cands = getattr(m, "CANDIDATES", None)
        if not cands:
            print(f"{name}: no CANDIDATES")
            continue
        k_usd = k_nom = 0
        for P in cands:
            unit = str(P.get("unit", ""))
            lim = str(P.get("limits", ""))
            is_usd = "USD" in unit or "dollar" in unit.lower()
            nominal = "nominal" in lim.lower() or "nominal" in unit.lower()
            k_usd += is_usd
            k_nom += is_usd and nominal
            floor1 += float(P.get("n_floor", 0)) <= 1
            rows.append((name, P["name"], unit, P.get("n_floor"), P.get("first_words", ""), is_usd, nominal))
        total += len(cands)
        usd += k_usd
        usd_nominal += k_nom
        print(f"{name}: {len(cands)} candidates; in dollars {k_usd}; of those saying nominal {k_nom}")
    print(f"ALL: {total} candidates; in dollars {usd}; saying nominal {usd_nominal}; n_floor of 1 or less {floor1}")
    print()
    print("module,candidate,unit,n_floor,first_words,usd,says_nominal")
    for r in rows:
        print(",".join(str(x).replace(",", ";") for x in r))


if __name__ == "__main__":
    main()
