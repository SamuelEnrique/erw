"""Session 10214 (demand audit): the consumption view of /demand restated from the main copy's tables (read only), and
what a forecaster would ask of it. Standard library only; each table is streamed.

  1. The view's figures by its own rules (app/consumption/view.tsx): the newest month of retail sales ends twelve months;
     the twelve before are the comparison; a total only when all twelve months are held; the fastest states among those
     that sold at least 1 TWh to the sector in the earlier twelve.
  2. Reclassification: for each state in the two "fastest" lists, the change of the other sector over the same months,
     and the state's months where industrial and commercial sales stepped in opposite directions by similar amounts.
  3. The rows' retrieval dates in the two windows (a row EIA stops giving is kept from an earlier run).
  4. The Monthly Energy Review rows: how much of "total energy consumed" is electrical system losses.

Usage: python consumption.py <eia_retail_sales_monthly.csv> <eia_sector_energy_consumption_monthly.csv> <out json>
"""
import csv
import json
import sys
from collections import defaultdict

STATES = ("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD "
          "TN TX UT VT VA WA WV WI WY").split()


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rd)
        ix = {k: i for i, k in enumerate(head)}
        for r in rd:
            yield {k: r[i] for k, i in ix.items()}


def month_add(m, k):
    y, mm = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{y + mm // 12:04d}-{mm % 12 + 1:02d}"


def main(sales_path, mer_path, out):
    v = {}            # (state, sector, month) -> MWh
    got = defaultdict(int)
    for r in rows(sales_path):
        if r["variable"] != "retail_sales":
            continue
        _, _, st, sec = r["entity"].split(":")
        m = r["ts_utc"][:7]
        v[(st, sec, m)] = float(r["value"])
        got[(m, r["retrieved_at"][:10])] += 1
    latest = max(m for (_, _, m) in v)
    cur = [month_add(latest, -k) for k in range(11, -1, -1)]
    prev = [month_add(m, -12) for m in cur]
    tot = lambda st, sec, ms: (sum(v[(st, sec, m)] for m in ms) if all((st, sec, m) in v for m in ms) else None)
    res = {"latest": latest, "window": [cur[0], cur[-1]], "before": [prev[0], prev[-1]]}
    us = {sec: (tot("US", sec, cur), tot("US", sec, prev)) for sec in ("ALL", "RES", "COM", "IND", "TRA", "OTH")}
    res["us"] = {sec: {"cur": a, "prev": b, "growth_pct": (100 * (a - b) / b if a and b else None), "share_pct": (100 * a / us["ALL"][0] if a else None)} for sec, (a, b) in us.items()}
    table = {}
    for st in STATES:
        table[st] = {sec: (tot(st, sec, cur), tot(st, sec, prev)) for sec in ("ALL", "RES", "COM", "IND", "TRA", "OTH")}
    def fastest(sec):
        xs = [(st, a, b) for st, d in table.items() for (a, b) in [d[sec]] if a is not None and b is not None and b >= 1_000_000 and b > 0]
        return sorted(xs, key=lambda x: -(x[1] - x[2]) / x[2])[:10]
    res["fastest"] = {}
    for sec, other in (("IND", "COM"), ("COM", "IND")):
        lst = []
        for st, a, b in fastest(sec):
            oa, ob = table[st][other]
            alla, allb = table[st]["ALL"]
            lst.append({"state": st, "mwh": a, "change_mwh": a - b, "growth_pct": 100 * (a - b) / b,
                        "other_sector_change_mwh": (oa - ob) if oa is not None and ob is not None else None,
                        "all_sectors_change_mwh": (alla - allb) if alla is not None and allb is not None else None})
        res["fastest"][sec] = lst
    # 2. offsetting steps: a month whose industrial change on the month a year before and commercial change are of opposite
    # sign, each above 10 percent of the state's monthly all-sector sales, and within a quarter of each other
    steps = []
    months = sorted({m for (_, _, m) in v if m >= month_add(latest, -47)})
    for st in STATES:
        for m in months:
            p = month_add(m, -12)
            try:
                di = v[(st, "IND", m)] - v[(st, "IND", p)]
                dc = v[(st, "COM", m)] - v[(st, "COM", p)]
                al = v[(st, "ALL", p)]
            except KeyError:
                continue
            if di * dc < 0 and min(abs(di), abs(dc)) > 0.10 * al and abs(abs(di) - abs(dc)) < 0.25 * max(abs(di), abs(dc)):
                steps.append({"state": st, "month": m, "industrial_change_mwh": di, "commercial_change_mwh": dc, "all_sectors_month_before_mwh": al})
    res["offsetting_steps"] = steps
    # sectors adding to all: in the current window, ALL against the sum of the four (and OTH)
    gaps = []
    for st in STATES:
        a = table[st]["ALL"][0]
        parts = [table[st][s][0] for s in ("RES", "COM", "IND", "TRA") if table[st][s][0] is not None]
        if a:
            gaps.append((st, a - sum(parts)))
    res["all_less_parts_max_abs_mwh"] = max(gaps, key=lambda x: abs(x[1])) if gaps else None
    res["retrieved_in_windows"] = sorted({d: 0 for (m, d) in got if m in cur or m in prev}.keys())
    # 4. the Monthly Energy Review
    mer = defaultdict(dict)
    for r in rows(mer_path):
        mer[r["entity"].split(":")[1]][r["ts_utc"][:7]] = float(r["value"])
    ml = max(mer["TEICBUS"])
    mc = [month_add(ml, -k) for k in range(11, -1, -1)]
    s = lambda msn: sum(mer[msn].get(m, 0) for m in mc)
    res["mer"] = {"latest": ml, "TEICBUS": s("TEICBUS"), "TNICBUS": s("TNICBUS"), "LOICBUS": s("LOICBUS"), "TECCBUS": s("TECCBUS"), "TNCCBUS": s("TNCCBUS"),
                  "industrial_losses_share_pct": 100 * s("LOICBUS") / s("TEICBUS"), "commercial_total_less_end_use_share_pct": 100 * (s("TECCBUS") - s("TNCCBUS")) / s("TECCBUS")}
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print(f"latest {latest}; US all sectors {us['ALL'][0]:,.0f} MWh, {res['us']['ALL']['growth_pct']:+.2f} percent")
    for sec in ("IND", "COM"):
        print(sec, ", ".join(f"{x['state']} {x['growth_pct']:+.1f} (other {x['other_sector_change_mwh'] or 0:+,.0f}; own {x['change_mwh']:+,.0f})" for x in res["fastest"][sec]))
    print(f"offsetting steps in the last 48 months: {len(steps)}")
    for x in steps[:40]:
        print(f"  {x['state']} {x['month']}: industrial {x['industrial_change_mwh']:+,.0f}, commercial {x['commercial_change_mwh']:+,.0f} on the same month a year before (all sectors {x['all_sectors_month_before_mwh']:,.0f})")
    print("MER:", json.dumps(res["mer"]))
    print("retrieved dates of rows in the windows:", res["retrieved_in_windows"])
    print("largest ALL less the four sectors:", res["all_less_parts_max_abs_mwh"])


if __name__ == "__main__":
    main(*sys.argv[1:4])
