#!/usr/bin/env python3
"""The Research cards' statistics: Newey-West beside HC1, the claims of a round, and the daily recompute (session 361).

Energy Research Warehouse (ERW). docs/methods/automated_analysis_findings.md, "Session 361: the statistics a card
carries". Three things, each added beside a card's figures and never changing one:

  1. **Newey-West beside HC1.** The monthly regressions (batteries_lunch, batteries_lunch_grids) and the daily one
     (batteries_curtailment) are recomputed from the card's own CSV download, the rows the card was computed from;
     every HC1 figure must come out equal to the card's (else the card is left as it is and the run fails), and the
     Newey-West error is added beside it (findings_common.ols_hc1, NW_RULE). impact_study's errors were Newey-West
     already; batteries_curtailment_hourly's are clustered by day.
  2. **The claims of a round.** Every card carries the round it was computed in: the claims the library tested that
     round (each regression a card reports with a p-value: every card's numbers ending in _p, a test repeated on two
     cards counted once), how many passed at 5 percent, and each of the card's own claims' Benjamini-Hochberg q-value
     over the round. A caveat, never a gate: no figure, verdict or word of a card changes with it.
  3. **The daily recompute** (--recompute, the data machine's daily run after the scan, step dm_findings_recompute):
     each finding at its default inputs computed again from today's tables (run_finding.run), then 1 and 2 again, and
     a line a card in warehouse/metadata/findings_recompute.csv: the day, the card, the numbers that moved, the status.
     A finding whose table is not on the machine keeps its card as it was, said in the record.

    python warehouse/analysis/findings/card_statistics.py               # 1 and 2 on the cards as they are
    python warehouse/analysis/findings/card_statistics.py --check       # the same, writing nothing; exit 1 if a card lacks them
    python warehouse/analysis/findings/card_statistics.py --recompute   # 3
"""

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import findings_common as common  # noqa: E402
import run_finding  # noqa: E402

CARD_DIR = run_finding.CARD_DIR
DOWNLOAD_DIR = run_finding.DOWNLOAD_DIR
RECORD = os.path.join(ROOT, "warehouse", "metadata", "findings_recompute.csv")
RECORD_COLS = ["day", "card", "status", "computed_at", "numbers", "numbers_moved", "detail"]
ALPHA = 0.05
SAME = 1e-9   # the HC1 figures recomputed from the CSV must equal the card's to this (relative)
CAVEAT = ("Many claims were tested in this round; a claim's q-value is the false discovery rate at which it would still be "
          "kept over all of them (Benjamini and Hochberg). A caveat, not a test the card had to pass.")


def tracked_cards():
    """The default cards and their committed variants: the JSON files of site/data/findings git holds, the catalogue out."""
    r = subprocess.run(["git", "ls-files", "site/data/findings/*.json"], cwd=ROOT, capture_output=True, text=True)
    names = [os.path.basename(p) for p in r.stdout.split()] if r.returncode == 0 else sorted(os.listdir(CARD_DIR))
    return [n[:-5] for n in names if n.endswith(".json") and n != "catalogue.json"]


def read_card(cid):
    with open(os.path.join(CARD_DIR, cid + ".json"), encoding="utf-8") as f:
        return json.load(f)


def write_json(cid, card):
    with open(os.path.join(CARD_DIR, cid + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(card, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")


def rows_of(card):
    name = (card.get("downloads") or {}).get("csv") or card.get("csv_name")
    if not name:
        return None
    path = os.path.join(DOWNLOAD_DIR, name)
    return common.read_rows_csv(path) if os.path.exists(path) else None


def close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= SAME * max(1.0, abs(a), abs(b))


def regressions(card, rows):
    """[(spec, label, numbers key prefix, fit of the coefficient)] for a card on the HC1 helper; [] for the others."""
    fid = card.get("id")
    out = []
    if fid == "batteries_lunch":
        import batteries_lunch as m
        f = m.fit(rows)
        for y, key in (("worst_interval_multiple", "reg_multiple"), ("hours_ge_1000", "reg_hours1000"), ("hours_top1pct", "reg_top1")):
            out.append((y, f[y]["label"] + ", per GW of batteries", key, f[y], f[y]["n"]))
    elif fid == "batteries_lunch_grids":
        import batteries_lunch_grids as m
        _, fits = m.numbers_from_rows(rows)
        for grid, f in fits.items():
            if not f:
                continue
            for y, key in (("worst_interval_multiple", "reg_multiple"), ("hours_ge_1000", "reg_hours1000"), ("hours_top1pct", "reg_top1")):
                out.append((f"{grid}:{y}", f"{grid.upper()}: {f[y]['label']}, per GW of batteries", f"{grid}_{key}", f[y], f[y]["n"]))
    elif fid == "batteries_curtailment":
        import batteries_curtailment as m
        f, _ = m.fit(rows)
        for k in ("charging", "charging_solar", "charging_solar_month"):
            c = f[k]["coef"]["charging_gwh"]
            out.append((k, f"{k.replace('_', ' ')}: MWh curtailed per GWh charged", k, {**c, "n": f[k]["n"], "nw_lag": f[k]["nw_lag"]}, f[k]["n"]))
        s = f["charging_solar_month"]["coef"]["solar_gwh"]
        out.append(("solar", "solar: MWh curtailed per GWh of solar (with charging and the month)", "solar",
                    {**s, "n": f["charging_solar_month"]["n"], "nw_lag": f["charging_solar_month"]["nw_lag"]}, f["charging_solar_month"]["n"]))
    return out


def newey_west(card, rows):
    """The card's regressions with HC1 (checked equal to the card) and Newey-West beside it; None when it has none."""
    regs = regressions(card, rows)
    if not regs:
        return None
    nums = card.get("numbers") or {}
    out = []
    for spec, label, key, c, n in regs:
        for name, have in (("coef", nums.get(f"{key}_coef")), ("se", nums.get(f"{key}_se")), ("p", nums.get(f"{key}_p"))):
            if have is not None and not close(c[name], have):
                raise ValueError(f"{card['id']}: {key}_{name} recomputed from the card's CSV is {c[name]!r}, the card says {have!r}")
        lag = c.get("nw_lag") if "nw_lag" in c else common.nw_lag(n)
        out.append({"spec": spec, "label": label, "numbers_key": key, "coef": c["coef"], "se_hc1": c["se"], "p_hc1": c["p"],
                    "se_nw": c["se_nw"], "p_nw": c["p_nw"], "nw_lag": int(lag), "n": int(n)})
    return {"rows": out, "rule": common.NW_RULE, "words": "Newey-West errors allow for correlation between neighbouring months (or days); "
            "HC1, the card's own, does not. Both are from the rows of the card's CSV, in time order."}


def claims_of(card):
    """The card's tested claims: its numbers ending in _p, {key: p}."""
    return {k: v for k, v in (card.get("numbers") or {}).items() if k.endswith("_p") and isinstance(v, (int, float))}


def round_of(cards, day):
    """The round: every card's claims, a test on two cards counted once (the same p-value to the last digit: the grid
    card's ERCOT rows are the ERCOT card's), and each claim's q-value."""
    seen, keys = {}, []
    for cid, card in cards.items():
        for k, p in claims_of(card).items():
            keys.append((cid, k, p))
            seen.setdefault(repr(p), p)
    distinct = list(seen.values())
    q = dict(zip((repr(p) for p in distinct), common.bh_q(distinct)))
    passing = sum(1 for p in distinct if p < ALPHA)
    return {"name": f"the findings library's cards as computed by {day}", "claims_tested": len(distinct), "claims_passing": passing,
            "alpha": ALPHA, "method": "Benjamini-Hochberg over the round's distinct p-values", "caveat": CAVEAT}, q


def attach(cids=None, check=False, log=print):
    """Newey-West and the round on every tracked card. Returns the cards that changed."""
    cids = cids or tracked_cards()
    cards = {cid: read_card(cid) for cid in cids}
    computed = max(str(c.get("computed_at") or "") for c in cards.values())[:10]
    rnd, q = round_of(cards, computed)
    changed = []
    for cid, card in cards.items():
        stats = {"session": 361, "round": dict(rnd)}
        own = claims_of(card)
        stats["round"]["claims_of_this_card"] = len(own)
        stats["round"]["q_bh"] = {k: q[repr(p)] for k, p in own.items()}
        if not own:
            stats["round"]["this_card"] = "no claim of this card is a test with a p-value: it states figures, and the round's count is the library's"
        rows = rows_of(card)
        nw = newey_west(card, rows) if rows is not None else None
        if nw:
            stats["newey_west"] = nw
        if card.get("statistics") != json.loads(json.dumps(stats, default=common.round6)):
            changed.append(cid)
            if not check:
                card["statistics"] = stats
                write_json(cid, card)
        log(f"  {cid}: {len(own)} claims of its own{', Newey-West on ' + str(len(nw['rows'])) + ' regressions' if nw else ''}")
    log(f"round: {rnd['claims_tested']} claims tested, {rnd['claims_passing']} pass at {ALPHA}; {len(changed)} cards {'would change' if check else 'written'}")
    return changed


def recompute(log=print):
    """Each finding at its default inputs from today's tables, then attach(); a record line a card."""
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    lines, done = [], []
    for name in run_finding.FINDINGS:
        before = read_card(name) if os.path.exists(os.path.join(CARD_DIR, name + ".json")) else {}
        try:
            run_finding.run(name, {}, log=log)
            after = read_card(name)
            nb, na = before.get("numbers") or {}, after.get("numbers") or {}
            moved = sorted(k for k in set(nb) | set(na) if json.dumps(nb.get(k), default=str) != json.dumps(na.get(k), default=str))
            lines.append(dict(day=day, card=name, status="recomputed", computed_at=after.get("computed_at", ""), numbers=len(na), numbers_moved=len(moved),
                              detail="; ".join(moved[:12]) + ("; ..." if len(moved) > 12 else "")))
            done.append(name)
        except common.NoData as exc:
            lines.append(dict(day=day, card=name, status="kept", computed_at=before.get("computed_at", ""), numbers=len(before.get("numbers") or {}),
                              numbers_moved=0, detail=f"a table is not on this machine: {str(exc)[:200]}"))
        except Exception as exc:
            lines.append(dict(day=day, card=name, status="failed", computed_at=before.get("computed_at", ""), numbers=len(before.get("numbers") or {}),
                              numbers_moved=0, detail=f"{type(exc).__name__}: {str(exc)[:200]}"))
            log(traceback.format_exc())
    attach(log=log)
    new = not os.path.exists(RECORD)
    with open(RECORD, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RECORD_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        for line in lines:
            w.writerow(line)
    bad = [l["card"] for l in lines if l["status"] == "failed"]
    log(f"recompute {day}: {len(done)} cards recomputed, {sum(l['status'] == 'kept' for l in lines)} kept, {len(bad)} failed")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--recompute", action="store_true")
    a = ap.parse_args(argv)
    if a.recompute:
        return recompute()
    changed = attach(check=a.check)
    return 1 if (a.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
