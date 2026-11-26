"""Session 10212 (storage audit): the build-out tab's figures restated independently from EIA-860M.

    python restate_buildout.py <trial dir> <out json> <drawn n.json> [<drawn n.json> ...]

Standard library only, written from docs/methods/storage_buildout.md and the page's words, none of the builder's code:
a unit operates at a month's end when its first operating month is that month or earlier and it has not retired in or
before it; duration is MWh over MW; the year-end fleet is December's; the twelve months' change is the month less the
month twelve before. Compares every data-check figure of each drawn view (raw value and shown text).
"""
import csv
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

trial, out = sys.argv[1], sys.argv[2]
views = sys.argv[3:]
T = "storage_buildout_monthly"


def read(name):
    with open(os.path.join(trial, name + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


REG = {"CISO": "iso:caiso", "ERCO": "iso:ercot", "ISNE": "iso:isone", "MISO": "iso:miso", "NYIS": "iso:nyiso", "PJM": "iso:pjm", "SWPP": "iso:spp"}


def region(ba):
    return REG.get(ba, "us:outside_isos")


def mi(y, m):
    return int(y) * 12 + int(m) - 1


bat, sol = [], []
for t in ("eia860m_operating_generators", "eia860m_retired_generators"):
    for x in read(t):
        is_b = x["prime_mover"] == "BA"
        is_s = x["technology_group"] == "solar" and not is_b
        if not (is_b or is_s):
            continue
        end = mi(x["retirement_date"][:4], x["retirement_date"][5:7]) if t.endswith("retired_generators") else None
        u = dict(reg=region(x["balancing_authority"]), first=mi(x["operating_year"], x["operating_month"]), end=end,
                 mw=Decimal(x["nameplate_mw"]), mwh=Decimal(x["energy_capacity_mwh"]) if is_b and x["energy_capacity_mwh"] != "" else None)
        (bat if is_b else sol).append(u)
plan = [x for x in read("eia860m_planned_generators") if x["prime_mover"] == "BA"]
vint = read("eia860m_operating_generators")[0]["vintage"]
last = mi(vint[:4], vint[5:7])
ENT = list(REG.values()) + ["us:outside_isos", "us:total"]


def month(i):
    return f"{i // 12:04d}-{i % 12 + 1:02d}"


def bucket(u):
    if u["mwh"] is None:
        return "energy_not_reported"
    h = u["mwh"] / u["mw"]
    return "lt2h" if h < 2 else "2to4h" if h < 4 else "4to6h" if h < 6 else "ge6h"


def q4(a, b):
    return (a / b).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if b else None


V = {}
needed = sorted({last, last - 12} | {mi(y, 12) for y in range(2015, int(vint[:4]))} | {mi(y, 12) - 12 for y in range(2016, int(vint[:4]))})
for m in needed:
    live = [u for u in bat if u["first"] <= m and (u["end"] is None or u["end"] > m)]
    ls = [u for u in sol if u["first"] <= m and (u["end"] is None or u["end"] > m)]
    for e in ENT:
        b = live if e == "us:total" else [u for u in live if u["reg"] == e]
        s = ls if e == "us:total" else [u for u in ls if u["reg"] == e]
        held = [u for u in b if u["mwh"] is not None]
        mwv, mwh, mwheld = sum((u["mw"] for u in b), Decimal(0)), sum((u["mwh"] for u in held), Decimal(0)), sum((u["mw"] for u in held), Decimal(0))
        solar = sum((u["mw"] for u in s), Decimal(0))
        k = (e, month(m))
        V[(e, "battery_operating_mw", month(m))] = mwv
        V[(e, "battery_operating_mwh", month(m))] = mwh
        V[(e, "battery_operating_units", month(m))] = Decimal(len(b))
        V[(e, "solar_operating_mw", month(m))] = solar
        for bk in ("lt2h", "2to4h", "4to6h", "ge6h", "energy_not_reported"):
            g = [u for u in b if bucket(u) == bk]
            V[(e, f"battery_operating_mw_{bk}", month(m))] = sum((u["mw"] for u in g), Decimal(0))
            if bk != "energy_not_reported":
                V[(e, f"battery_operating_mwh_{bk}", month(m))] = sum((u["mwh"] for u in g), Decimal(0))
        if q4(mwh, mwheld) is not None:
            V[(e, "battery_operating_mwh_per_mw", month(m))] = q4(mwh, mwheld)
        if q4(mwh, solar) is not None:
            V[(e, "battery_mwh_per_solar_mw", month(m))] = q4(mwh, solar)
for e in ENT:
    for var in ("battery_operating_mw", "battery_operating_mwh"):
        for m in needed:
            if (e, var, month(m - 12)) in V:
                V[(e, f"{var}_net_added_12m", month(m))] = V[(e, var, month(m))] - V[(e, var, month(m - 12))]
    pe = plan if e == "us:total" else [x for x in plan if region(x["balancing_authority"]) == e]
    V[(e, "battery_planned_mw", month(last))] = sum((Decimal(x["nameplate_mw"]) for x in pe), Decimal(0))
    V[(e, "battery_planned_units", month(last))] = Decimal(len(pe))
    for y in sorted({x["planned_operation_date"][:4] for x in plan}):
        V[(e, f"battery_planned_mw_online_{y}", month(last))] = sum((Decimal(x["nameplate_mw"]) for x in pe if x["planned_operation_date"][:4] == y), Decimal(0))

WHOLE = ("battery_operating_mw", "battery_operating_mwh", "battery_planned_mw", "solar_operating_mw")


def written(var, v):
    whole = any(var == w or var.startswith(w + "_") for w in WHOLE) and "_per_" not in var
    if whole:
        return f"{int(v.quantize(Decimal('1'), rounding=ROUND_HALF_UP)):,}"
    if v == v.to_integral_value():
        return f"{int(v):,}"
    return f"{v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"


lines, agree, differ = [], 0, 0
for path in views:
    page = json.load(open(path, encoding="utf-8"))
    a = dd = 0
    for k, p in page.items():
        if not k.startswith(f"series|{T}|"):
            continue
        _, _, e, var, ts = k.split("|")
        key = (e, var, ts[:7])
        if key not in V:
            lines.append(f"NOT RESTATED {k}")
            dd += 1
            continue
        v = V[key]
        if Decimal(p["raw"]) == v and p["shown"] == written(var, v):
            a += 1
        else:
            dd += 1
            lines.append(f"DIFFER {os.path.basename(path)} {k}: page {p['raw']} '{p['shown']}', restated {v} '{written(var, v)}'")
    lines.append(f"{os.path.basename(path)}: {a} agree, {dd} differ")
    agree += a
    differ += dd
print(f"build-out: {agree} agree, {differ} differ")
print("\n".join(lines))
us = {var: str(V[("us:total", var, month(last))]) for var in ("battery_operating_mw", "battery_operating_mwh", "battery_operating_mwh_per_mw", "battery_operating_units", "battery_operating_mw_net_added_12m", "battery_operating_mwh_net_added_12m", "solar_operating_mw", "battery_mwh_per_solar_mw")}
json.dump(dict(vintage=vint, us=us, agree=agree, differ=differ), open(out, "w", encoding="utf-8"), indent=1)
