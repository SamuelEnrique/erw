"""Session 10231: the interconnection explorer's default view (CAISO, in positions, entry years 1999 to 2023), restated
from the operators' queue tables by the method note's rules (docs/methods/energy_projects.md, "Queue statistics"):
the entry year is the year of the queue date; operating, withdrawn and waiting by the ISO's own status word
(CAISO: COMPLETED, WITHDRAWN, every other word; ERCOT: the harmonized status, completed or active; SPP: IA FULLY
EXECUTED/COMMERCIAL OPERATION, WITHDRAWN or TERMINATED, every other word); a blank word is status not stated; the
withdrawn share by count; the wait from the queue date to the in-service date in days over 365.25, operating positions
with both dates in order, its median. Standard library; nothing of the builder is imported.

    python restate_ic.py <ic_opening.json> <caiso_q.csv> <ercot_q.csv> <spp_q.csv>
"""
import csv
import json
import statistics
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def day(s):
    s = (s or "").strip()
    if not s:
        return None
    return date.fromisoformat(s[:10])


def group(iso, row):
    w = (row["iso_status"] or "").strip()
    if iso == "ercot":
        st = (row["status"] or "").strip()
        return {"completed": "operating", "active": "waiting", "": "status_not_stated"}.get(st, "waiting")
    if not w:
        return "status_not_stated"
    if iso == "caiso":
        return {"COMPLETED": "operating", "WITHDRAWN": "withdrawn"}.get(w, "waiting")
    if iso == "spp":
        if w == "IA FULLY EXECUTED/COMMERCIAL OPERATION":
            return "operating"
        if w in ("WITHDRAWN", "TERMINATED"):
            return "withdrawn"
        return "waiting"


def stats(iso, path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(l for l in f if not l.startswith("#")):
            q = day(r["queue_date"])
            if q is None:
                continue
            y = q.year
            s = out.setdefault(y, {"entered": 0, "operating": 0, "withdrawn": 0, "waiting": 0, "status_not_stated": 0, "waits": []})
            s["entered"] += 1
            gname = group(iso, r)
            s[gname] += 1
            if gname == "operating":
                a = day(r["actual_in_service_date"])
                if a is not None and a >= q:
                    s["waits"].append((a - q).days / 365.25)
    return out


def text(v, whole):
    if whole:
        return f"{int(round(v)):,}"
    return f"{Decimal(repr(round(v, 6))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}"


def main():
    op = json.load(open(sys.argv[1], encoding="utf-8"))
    S = {"caiso": stats("caiso", sys.argv[2]), "ercot": stats("ercot", sys.argv[3]), "spp": stats("spp", sys.argv[4])}
    view = op["views"][0]
    eq = 0
    diff = []
    for key in dict.fromkeys(view["keys"]):
        _, _, ent, var, _ = key.split("|")
        if ":queue_" not in ent:
            diff.append((key, op["keyed"][key]["text"], "a header count, checked apart below"))
            continue
        iso, y = ent.split(":queue_")
        y = int(y)
        s = S[iso].get(y)
        if s is None:
            diff.append((key, op["keyed"][key]["text"], "no row"))
            continue
        if var.startswith("positions_"):
            v, whole = s[var[len("positions_"):]], True
        elif var == "withdrawal_rate":
            v, whole = s["withdrawn"] / s["entered"], False
        elif var == "wait_positions":
            v, whole = len(s["waits"]), True
        elif var == "wait_years_median":
            v, whole = statistics.median(s["waits"]), False
        else:
            diff.append((key, "variable not restated"))
            continue
        mine = text(v, whole)
        if mine == op["keyed"][key]["text"]:
            eq += 1
        else:
            diff.append((key, op["keyed"][key]["text"], mine))
    print(f"default view: {eq} of {len(dict.fromkeys(view['keys']))} distinct keyed figures equal the restatement from the queue tables held here")
    for d in diff:
        print("  differs:", d)
    print("CAISO 2023:", {k: v for k, v in S["caiso"][2023].items() if k != "waits"}, "; 2022:", {k: v for k, v in S["caiso"][2022].items() if k != "waits"})
    print("CAISO entry years held:", min(S["caiso"]), "to", max(S["caiso"]))
    with open(sys.argv[2], newline="", encoding="utf-8") as f:
        undated = sum(1 for r in csv.DictReader(l for l in f if not l.startswith("#")) if day(r["queue_date"]) is None)
    print("CAISO positions with no queue date:", undated)


if __name__ == "__main__":
    main()
