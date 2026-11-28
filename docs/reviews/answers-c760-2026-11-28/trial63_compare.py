"""Chain 760, five-tools data request 63: the price forecast for 28 November made as at 14:00 UTC on 27 November (a
trial: run.py --now 2026-11-27T14:00:00Z --no-ledger, four places, runs/c760/trial63/site) beside the ledger's making
of 19:00 UTC (site/data/predict/ledger_price.csv), and beside the day-ahead price that came, where held.
Prints, by place, the mean absolute difference between the two makings and each making's mean absolute error.
"""
import csv
import json
import os

ROOT = r"C:\Users\Shared\Documents\erw"
LEDGER = os.path.join(ROOT, "runs", "c760", "trial63", "ledger_aside", "ledger_price.csv")  # the ledger as it stood
PLACES = ["region-cent", "ba-swpp", "region-cal", "ba-ciso"]


def ledger():
    out = {}
    with open(LEDGER, encoding="utf-8") as fh:
        rd = csv.DictReader(ln for ln in fh if not ln.startswith("#"))
        for r in rd:
            if r["place"] in PLACES and r["target_day"] == "2026-11-28" and r["erw"]:
                out[(r["place"], r["ts_utc"])] = (float(r["erw"]), r["made_utc"])
    return out


def trial(place):
    p = os.path.join(ROOT, "runs", "c760", "trial63", "site", place + ".json")
    d = json.load(open(p, encoding="utf-8"))
    s = d["series"]["price"]
    rows = s.get("tomorrow") or []
    cols = s.get("tomorrow_columns") or []
    out = {}
    for r in rows:
        rec = dict(zip(cols, r)) if isinstance(r, list) else r
        ts = rec.get("ts_utc") or rec.get("t")
        v = rec.get("erw")
        if ts and v is not None:
            out[ts] = v
    return s.get("target_day"), s.get("made_utc"), s.get("hub"), out


def main():
    lg = ledger()
    for place in PLACES:
        day, made, hub, tr = trial(place)
        pairs = [(tr[ts], lg[(place, ts)][0]) for ts in tr if (place, ts) in lg]
        if not pairs:
            print(f"{place}: trial target {day} made {made}: no hour in common with the ledger's making")
            continue
        mad = sum(abs(a - b) for a, b in pairs) / len(pairs)
        mean_t = sum(a for a, _ in pairs) / len(pairs)
        mean_l = sum(b for _, b in pairs) / len(pairs)
        print(f"{place} ({hub}): {len(pairs)} hours of {day}; trial made {made}, ledger made "
              f"{next(iter(lg[(place, ts)][1] for ts in tr if (place, ts) in lg))}; mean trial {mean_t:.2f}, "
              f"mean ledger {mean_l:.2f}, mean absolute difference {mad:.2f} USD/MWh")


if __name__ == "__main__":
    main()
