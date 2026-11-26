"""Session 10238 (chain 710, part D): the small pages' figures restated independently, from each page's own files.

    python runs/c10238/restate.py <worktree> <main copy> > runs/c10238/restate.out

Standard library and openpyxl only (no pandas, nothing of the ERW imported). Reads; writes nothing but its printout.
Sections: /about (the platform counts), /resources (the default layer's legend, the toggles, the decisions, the
outline area, the queue overlay's rows), /shoulder (ERCOT's default month and every ERCOT month, restated from EIA's
own workbook by the method note's words, then the decisions' figures), /attention (the default view, from the week
files of the same build).
"""
import base64
import csv
import glob
import json
import math
import os
import re
import struct
import sys
from datetime import datetime, timedelta, timezone

WT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
MAIN = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else ".")
OUT = os.path.join(MAIN, "warehouse", "output")
FAIL = []


def say(*a):
    print(*a, flush=True)


def check(label, page, mine, tol=0.0):
    ok = (page == mine) if tol == 0 else (page is not None and mine is not None and abs(float(page) - float(mine)) <= tol)
    say(f"  {'EQUAL ' if ok else 'DIFFER'} {label}: page/table {page} | restated {mine}")
    if not ok:
        FAIL.append(label)
    return ok


def read_csv(path, wanted=None):
    with open(path, encoding="utf-8", newline="") as fh:
        lines = (ln for ln in fh if not ln.startswith("#"))
        for r in csv.DictReader(lines):
            if wanted is None or wanted(r):
                yield r


# ---------------------------------------------------------------------------------------------------------------------
def about():
    say("== /about: the platform's counts, from docs/platform-tools.md")
    n = {"total": 0, "yes": 0, "partial": 0, "no": 0, "planned": 0}
    for ln in open(os.path.join(WT, "docs", "platform-tools.md"), encoding="utf-8"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0].isdigit():
            continue
        status = None
        for c in cells[1:]:
            m = re.match(r"\*\*(yes|partial|no|planned)", c)
            if m:
                status = m.group(1)
                break
        if status:
            n["total"] += 1
            n[status] += 1
    say(f"  restated: {n}; 'Today {n['yes'] + n['partial']} of them have a working data layer ({n['yes']} complete, "
        f"{n['partial']} partial), {n['no']} are not built and {n['planned']} are planned', of {n['total']} tools")
    docs = os.path.join(WT, "site", "content", "docs.json")
    if os.path.exists(docs):
        with open(docs, encoding="utf-8") as fh:
            text = fh.read()
        m = re.search(r'"platform":\s*(\{[^}]*\})', text)
        if m:
            p = json.loads(m.group(1))
            for k in n:
                check(f"platform {k} (site/content/docs.json)", p.get(k), n[k])


# ---------------------------------------------------------------------------------------------------------------------
def grid_values(path):
    g = json.load(open(path, encoding="utf-8"))
    raw = base64.b64decode(g["values"])
    vals = struct.unpack("<%dH" % (len(raw) // 2), raw)
    held = [v * g["scale"] + (g.get("offset") or 0) for v in vals if v != g.get("nodata", 65535)]
    return g, held


def resources():
    say("== /resources (the Resources tab of /map): the default view")
    R = os.path.join(WT, "site", "data", "resources")
    first = json.load(open(os.path.join(R, "manifest.json"), encoding="utf-8"))
    added = json.load(open(os.path.join(R, "manifest_added.json"), encoding="utf-8")) if os.path.exists(os.path.join(R, "manifest_added.json")) else {}
    ids = [l["id"] for l in first["layers"]]
    layers = list(first["layers"]) + [l for l in added.get("layers", []) if l["id"] not in ids]
    held = []
    for l in layers:
        files = [v["file"] for v in l.get("levels", []) or []] + ([l["file"]] if l.get("file") else []) + \
            [f if isinstance(f, str) else f["file"] for f in l.get("files", []) or []]
        if any(os.path.exists(os.path.join(R, "layers", f)) or os.path.exists(os.path.join(WT, "site", "public", "resources-data", f)) for f in files):
            held.append(l)
    say(f"  layers in the two lists: {len(layers)}; with a file on the server: {len(held)}: {', '.join(l['id'] for l in held)}")
    by = {}
    for l in held:
        by.setdefault(l["group"], []).append(l["id"])
    say(f"  held by group: {by}")
    missing = list(first.get("missing", [])) + [x for x in added.get("missing", []) if x.get("id") not in {y.get('id') for y in first.get('missing', [])} and x.get("id") not in {l['id'] for l in held}]
    say(f"  named as not held: {[(x.get('group'), x.get('title')) for x in missing]}")
    say(f"  coal fields held: {'coal_fields' in [l['id'] for l in held]}; a wind capacity factor layer held: "
        f"{[l['title'] for l in held if 'capacity' in l['id']]}")
    # the default layer and its legend
    wind = next(l for l in held if l["group"] == "wind" and "speed" in (l["id"] + l["title"]).lower())
    say(f"  the default layer (a bare address): {wind['id']} ({wind['title']}, {wind.get('unit')})")
    lg = wind["legend"]
    lo, hi = None, None
    for lev in wind["levels"]:
        g, vals = grid_values(os.path.join(R, "layers", lev["file"]))
        say(f"    level {lev['cell_deg']} deg: {g['ncols']} x {g['nrows']} cells, {len(vals)} held, min {min(vals):.3f}, max {max(vals):.3f}, "
            f"mean {sum(vals) / len(vals):.3f}")
        lo = min(vals) if lo is None else min(lo, min(vals))
        hi = max(vals) if hi is None else max(hi, max(vals))
    check("legend minimum = the files' lowest held cell", round(lg["min"], 3), round(lo, 3))
    check("legend maximum = the files' highest held cell", round(lg["max"], 3), round(hi, 3))
    rng = lg["max"] - lg["min"]
    ticks = sorted(set([lg["min"], *lg.get("stops", []), lg["max"]]))

    def tick(v):
        if rng >= 100000:
            return "compact"
        d = (0 if (float(v).is_integer() or abs(v) >= 100) else 1) if rng >= 50 else (1 if rng >= 5 else 2)
        return f"{v:,.{d}f}"
    say(f"  the legend's ticks as printed (range {rng:.3f}, so {'one decimal' if 5 <= rng < 50 else 'other'}): {[tick(t) for t in ticks]}")
    say(f"  KX = cos(37.5 degrees) = {math.cos(math.radians(37.5)):.4f}; the page prints KX.toFixed(4)")
    # the decisions
    dec = open(os.path.join(WT, "site", "app", "resources", "Decisions.tsx"), encoding="utf-8").read()
    n_dec = len(re.findall(r'\{ key: "', dec))
    say(f"  decisions listed: {n_dec} (the summary prints the count)")
    # the outline area of the Marcellus
    plays = json.load(open(os.path.join(R, "layers", "oil_gas_plays.json"), encoding="utf-8"))
    marc = [f["properties"] for f in plays["features"] if "marcellus" in str(f["properties"].get("Shale_play", "")).lower()]
    for p in marc:
        say(f"  Marcellus in the plays file: Area_sq_mi {p.get('Area_sq_mi')} (page: 58,326) -> {round(p.get('Area_sq_mi')):,}")
    tol = {}
    for l in held:
        m = re.search(r"tolerance ([0-9.]+) degrees|simplified to ([0-9.]+) degrees", l.get("reduction") or "")
        tol[l["id"]] = (m.group(1) or m.group(2)) if m else ("not simplified" if l["kind"] == "shapes" else l["kind"])
    say(f"  simplification by layer: {tol}")
    # the queue overlay: energy_projects' queue rows by grid and by the precision of their place (the main copy's table)
    p = os.path.join(OUT, "energy_projects.csv")
    if os.path.exists(p):
        cnt, mw = {}, {}
        for r in read_csv(p, lambda r: r.get("kind") == "queue"):
            k = (r.get("source_table", "").replace("_interconnection_queue", ""), r.get("geo_precision", ""))
            cnt[k] = cnt.get(k, 0) + 1
            try:
                mw[k] = mw.get(k, 0.0) + float(r.get("capacity_mw") or 0)
            except ValueError:
                pass
        say("  energy_projects queue rows (main copy, retrieved 2026-10-03) by grid and place precision:")
        for k in sorted(cnt):
            say(f"    {k[0]:8s} {k[1] or '(none)':10s} {cnt[k]:6d} rows {mw[k]:12,.1f} MW")


# ---------------------------------------------------------------------------------------------------------------------
# /shoulder: ERCOT restated from EIA's own workbook, by the words of the page's fold and docs/methods/shoulder_hours.md.

def chicago(ts):
    """UTC to Central time by the US rule since 2007 (second Sunday of March 02:00 to first Sunday of November 02:00)."""
    y = ts.year

    def nth_sunday(month, n):
        d = datetime(y, month, 1, tzinfo=timezone.utc)
        first = d + timedelta(days=(6 - d.weekday()) % 7)
        return first + timedelta(days=7 * (n - 1))
    start = nth_sunday(3, 2) + timedelta(hours=8)    # 02:00 CST = 08:00 UTC
    end = nth_sunday(11, 1) + timedelta(hours=7)     # 02:00 CDT = 07:00 UTC
    off = -5 if start <= ts < end else -6
    return ts + timedelta(hours=off)


def load_erco():
    import openpyxl
    files = [f for f in glob.glob(os.path.join(MAIN, "warehouse", "raw", "eia930_emissions", "*", "*_ERCO.xlsx")) if os.path.getsize(f) > 0]
    path = max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))
    say(f"  EIA's workbook: {os.path.relpath(path, MAIN)}")
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    col = {k: head.index(k) for k in ("UTC time", "Adjusted demand", "Adjusted SUN Gen", "Adjusted SNB Gen", "Adjusted WND Gen",
                                       "Adjusted WNB Gen", "Adjusted BAT Gen") if k in head}
    say(f"  columns found: {sorted(col)}")
    H = {}
    for r in rows:
        t = r[col["UTC time"]]
        if t is None or t.year < 2018:
            continue
        start = t.replace(tzinfo=timezone.utc) - timedelta(hours=1)   # EIA dates an hour by its end; the ERW by its start

        def num(k):
            if k not in col:
                return None
            v = r[col[k]]
            return float(v) if isinstance(v, (int, float)) else None
        if start in H:
            continue
        H[start] = dict(d=num("Adjusted demand"), sun=num("Adjusted SUN Gen"), snb=num("Adjusted SNB Gen"), wnd=num("Adjusted WND Gen"),
                        wnb=num("Adjusted WNB Gen"), bat=num("Adjusted BAT Gen"))
    return H


def median(xs):
    s = sorted(xs)
    n = len(s)
    return None if not n else (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)


def screen(H):
    """Rule A of docs/methods/impossible_hours.md, written again from its words: held, above zero, within 25 percent of the
    median of the four hours around it (two before, two after, those held and above zero), and between one third of and
    three times the median of the grid's hours that pass the first three tests."""
    first3 = {}
    for t, r in H.items():
        v = r["d"]
        if v is None or v <= 0:
            continue
        nb = [H[t + timedelta(hours=k)]["d"] for k in (-2, -1, 1, 2) if (t + timedelta(hours=k)) in H]
        nb = [x for x in nb if x is not None and x > 0]
        m = median(nb)
        if m is None or abs(v - m) <= 0.25 * m:
            first3[t] = v
    gm = median(list(first3.values()))
    ok = {t for t, v in first3.items() if gm / 3 <= v <= 3 * gm}
    blanked = sum(1 for t, r in H.items() if r["d"] is not None and t not in ok)
    say(f"  rule A: grid median {gm:,.1f} MW; {blanked} held hours of demand blanked")
    return ok


def ssum(a, b):
    return None if a is None and b is None else (a or 0.0) + (b or 0.0)


def day_figures(nl, sol):
    """One day (24 local hours): the midday surplus, the evening shoulder, the second measure, by the page's words."""
    mean = sum(nl) / 24
    low = min(range(24), key=lambda h: (nl[h], h))
    a = b = low
    while a - 1 >= 0 and nl[a - 1] < mean:
        a -= 1
    while b + 1 <= 23 and nl[b + 1] < mean:
        b += 1
    trough = list(range(a, b + 1)) if nl[low] < mean else []
    out = dict(net_load_mean_mw=mean, midday_low_hour=low, midday_surplus_hours=len(trough), midday_surplus_mwh=sum(mean - nl[h] for h in trough))
    peak = max(range(24), key=lambda h: (sol[h], -h))
    start = next((h for h in range(peak + 1, 24) if sol[h] < 0.5 * sol[peak]), None)
    if start is None or sol[peak] <= 0:
        return out
    # the second measure: around the evening's highest net load from the shoulder's start to midnight
    ph = max(range(start, 24), key=lambda h: (nl[h], -h))
    out.update(evening_peak_hour=ph, evening_peak_mw=nl[ph])
    if nl[ph] > mean:
        lvl = (mean + nl[ph]) / 2
        s2, e2 = ph, ph
        while s2 - 1 >= start and nl[s2 - 1] > lvl:
            s2 -= 1
        while e2 + 1 <= 23 and nl[e2 + 1] > lvl:
            e2 += 1
        out.update(shoulder2_start_hour=s2, shoulder2_end_hour=e2 + 1, shoulder2_hours=e2 + 1 - s2,
                   shoulder2_mwh_above_midpoint=sum(nl[h] - lvl for h in range(s2, e2 + 1)))
    else:
        out.update(shoulder2_start_hour=ph, shoulder2_end_hour=ph, shoulder2_hours=0, shoulder2_mwh_above_midpoint=0.0)
    rise = next((h for h in range(start, 24) if nl[h] > mean), None)
    if rise is None:
        out.update(shoulder_start_hour=start, shoulder_end_hour=start, shoulder_hours=0, shoulder_mwh_above_mean=0.0, shoulder_runs_to_midnight=0)
        return out
    end = next((h for h in range(rise + 1, 24) if nl[h] <= mean), None)
    mid = end is None
    end = 24 if mid else end
    out.update(shoulder_start_hour=start, shoulder_end_hour=end, shoulder_hours=end - start,
               shoulder_mwh_above_mean=sum(max(0.0, nl[h] - mean) for h in range(start, end)), shoulder_runs_to_midnight=int(mid))
    return out


def shoulder():
    say("== /shoulder: ERCOT, from EIA-930's own workbook, by the method's words")
    table = os.path.join(OUT, "shoulder_hours_monthly.csv")
    T = {}
    for r in read_csv(table, lambda r: r["entity"] in ("iso:ercot", "iso:caiso", "iso:caiso_own")):
        T[(r["entity"], r["variable"], r["ts_utc"][:10])] = float(r["value"])
    REQUIRED = ["days_held", "shoulder_hours", "shoulder_start_hour", "shoulder_end_hour", "shoulder_mwh_above_mean", "fleet_mw", "fleet_mwh",
                "fleet_hours", "shoulder_hours_covered", "shoulder_hours_needed", "midday_surplus_mwh", "midday_surplus_hours", "midday_low_hour",
                "shoulder2_hours", "shoulder2_start_hour", "shoulder2_end_hour", "shoulder2_mwh_above_midpoint", "shoulder2_hours_needed",
                "evening_peak_mw", "evening_peak_hour"]
    months = sorted({k[2][:7] for k in T if k[0] == "iso:ercot" and k[1] == "days_held"})
    complete = [m for m in months if all(("iso:ercot", v, m + "-01") in T for v in REQUIRED)]
    default = complete[-1]
    later = [m for m in months if m > default]
    say(f"  ERCOT months held: {len(months)} ({months[0]} to {months[-1]}); the default month (latest with every figure): {default}; later held: {later}")
    # the fleet
    fleet = {}
    for r in read_csv(os.path.join(OUT, "storage_buildout_monthly.csv"), lambda r: r["variable"] in ("battery_operating_mw", "battery_operating_mwh")):
        fleet[(r["entity"], r["variable"], r["ts_utc"][:7])] = float(r["value"])
    H = load_erco()
    ok = screen(H)
    # local hours
    L = {}
    for t, r in H.items():
        lt = chicago(t)
        day = lt.strftime("%Y-%m-%d")
        sol, wnd = ssum(r["sun"], r["snb"]), ssum(r["wnd"], r["wnb"])
        dem = r["d"] if t in ok else None
        L.setdefault(day, []).append(dict(h=lt.hour, dem=dem, sol=sol, wnd=wnd, bat=r["bat"]))
    full = {d for d, hs in L.items() if len(hs) in (23, 24, 25) and all(x["dem"] is not None and x["sol"] is not None and x["wnd"] is not None for x in hs)}
    say(f"  local days {len(L)}, complete {len(full)}")
    keys_month = ["days_held", "net_load_mean_mw", "midday_low_hour", "midday_surplus_hours", "midday_surplus_mwh", "shoulder_start_hour",
                  "shoulder_end_hour", "shoulder_hours", "shoulder_mwh_above_mean", "shoulder_runs_to_midnight", "evening_peak_hour", "evening_peak_mw",
                  "shoulder2_start_hour", "shoulder2_end_hour", "shoulder2_hours", "shoulder2_mwh_above_midpoint", "fleet_mw", "fleet_mwh",
                  "fleet_hours", "shoulder_hours_covered", "shoulder_hours_needed", "shoulder2_hours_covered", "shoulder2_hours_needed"]
    n_eq = n_all = 0
    diffs = []
    mine_by_month = {}
    for m in months:
        y, mo = int(m[:4]), int(m[5:])
        dim = (datetime(y + (mo == 12), mo % 12 + 1, 1) - datetime(y, mo, 1)).days
        days = sorted(d for d in full if d.startswith(m))
        if len(days) < 0.9 * dim:
            continue
        acc = {k: [[] for _ in range(24)] for k in ("dem", "sol", "wnd", "nl", "bat")}
        for d in days:
            for x in L[d]:
                acc["dem"][x["h"]].append(x["dem"])
                acc["sol"][x["h"]].append(x["sol"])
                acc["wnd"][x["h"]].append(x["wnd"])
                acc["nl"][x["h"]].append(x["dem"] - x["sol"] - x["wnd"])
        if any(not acc["nl"][h] for h in range(24)):
            continue
        nl = [sum(v) / len(v) for v in acc["nl"]]
        sol = [sum(v) / len(v) for v in acc["sol"]]
        f = day_figures(nl, sol)
        f["days_held"] = len(days)
        mw, mwh = fleet.get(("iso:ercot", "battery_operating_mw", m)), fleet.get(("iso:ercot", "battery_operating_mwh", m))
        if mw and mwh and "shoulder_hours" in f:
            f.update(fleet_mw=mw, fleet_mwh=mwh, fleet_hours=mwh / mw, shoulder_hours_covered=min(f["shoulder_hours"], mwh / mw),
                     shoulder_hours_needed=f["shoulder_mwh_above_mean"] / mw)
            if "shoulder2_hours" in f:
                f.update(shoulder2_hours_covered=min(f["shoulder2_hours"], mwh / mw), shoulder2_hours_needed=f["shoulder2_mwh_above_midpoint"] / mw)
        mine_by_month[m] = f
        for k in keys_month:
            tv = T.get(("iso:ercot", k, m + "-01"))
            if tv is None and k not in f:
                continue
            n_all += 1
            mv = f.get(k)
            if tv is not None and mv is not None and abs(round(mv, 4) - tv) <= 1.5e-4:
                n_eq += 1
            else:
                diffs.append((m, k, tv, None if mv is None else round(mv, 4)))
    say(f"  every ERCOT month's figures: {n_eq} of {n_all} equal to the table (to 0.0001); differing: {len(diffs)}")
    for d in diffs[:40]:
        say(f"    DIFFER {d}")
    if diffs:
        FAIL.append(f"shoulder months: {len(diffs)} figures differ")
    f = mine_by_month.get(default, {})

    def shown(v):
        return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"
    say(f"  the default month as the page prints it, restated: In {default}, ERCOT's evening shoulder lasted {shown(f['shoulder_hours'])} hours, "
        f"from {int(f['shoulder_start_hour']):02d}:00 to {int(f['shoulder_end_hour']):02d}:00{' (midnight)' if f.get('shoulder_runs_to_midnight') else ''}; "
        f"its batteries could run {shown(round(f['fleet_hours'], 4))} hours at full power, covering {shown(round(f['shoulder_hours_covered'], 4))} of them. "
        f"... would need {shown(round(f['shoulder_hours_needed'], 4))} hours on the average day")
    say(f"    headline notes: {shown(round(f['shoulder_mwh_above_mean'], 4))} MWh above the mean; fleet {shown(f['fleet_mw'])} MW holding {shown(f['fleet_mwh'])} MWh; "
        f"midday surplus {shown(round(f['midday_surplus_mwh'], 4))} MWh over {f['midday_surplus_hours']} hours around {f['midday_low_hour']:02d}:00; "
        f"net load mean {shown(round(f['net_load_mean_mw'], 4))} MW; days {f['days_held']}; second measure {f.get('shoulder2_hours')} h "
        f"{f.get('shoulder2_start_hour')}:00 to {f.get('shoulder2_end_hour')}:00, {shown(round(f['shoulder2_mwh_above_midpoint'], 4))} MWh, needed "
        f"{shown(round(f['shoulder2_hours_needed'], 4))} h; evening peak {shown(round(f['evening_peak_mw'], 4))} MW at {f['evening_peak_hour']:02d}:00")
    # the ten worst days of the default month's year
    yr = default[:4]
    per = []
    for d in sorted(full):
        if not d.startswith(yr):
            continue
        hs = sorted(L[d], key=lambda x: x["h"])
        if len(hs) != 24 or [x["h"] for x in hs] != list(range(24)):
            continue
        nl = [x["dem"] - x["sol"] - x["wnd"] for x in hs]
        g = day_figures(nl, [x["sol"] for x in hs])
        if not g.get("shoulder_hours"):
            continue
        per.append((d, g, hs))
    per.sort(key=lambda t: (-t[1]["shoulder_mwh_above_mean"], t[0]))
    top = per[:10]
    say(f"  {yr}: {len(per)} days ranked (table: {T.get(('iso:ercot', 'year_days_ranked', yr + '-01-01'))})")
    check(f"{yr} days ranked", T.get(("iso:ercot", "year_days_ranked", yr + "-01-01")), float(len(per)))
    needed = []
    for rank, (d, g, hs) in enumerate(top, 1):
        mw = fleet.get(("iso:ercot", "battery_operating_mw", d[:7]))
        n = g["shoulder_mwh_above_mean"] / mw if mw else None
        needed.append(n)
        tr = T.get(("iso:ercot", "worst_rank", d))
        te = T.get(("iso:ercot", "day_shoulder_mwh_above_mean", d))
        tn = T.get(("iso:ercot", "day_shoulder_hours_needed", d))
        bat = [x["bat"] for x in hs[int(g["shoulder_start_hour"]):int(g["shoulder_end_hour"])]]
        dis = sum(max(0.0, b) for b in bat) if all(b is not None for b in [x["bat"] for x in hs]) else None
        tb = T.get(("iso:ercot", "day_battery_discharge_mwh", d))
        ok_ = tr == rank and te is not None and abs(te - round(g["shoulder_mwh_above_mean"], 4)) <= 1.5e-4 and \
            (tn is None and n is None or (tn is not None and n is not None and abs(tn - round(n, 4)) <= 1.5e-4)) and \
            (tb is None and dis is None or (tb is not None and dis is not None and abs(tb - round(dis, 4)) <= 1.5e-4))
        say(f"    {'EQUAL ' if ok_ else 'DIFFER'} rank {rank} {d}: above mean {g['shoulder_mwh_above_mean']:,.2f} (table {te}), needed "
            f"{'-' if n is None else f'{n:.4f}'} (table {tn}), discharged {'-' if dis is None else f'{dis:,.2f}'} (table {tb}), rank in table {tr}")
        if not ok_:
            FAIL.append(f"worst day {d}")
    if all(x is not None for x in needed) and needed:
        check(f"{yr}: the ten worst days' mean hours needed", T.get(("iso:ercot", "year_worst10_mean_shoulder_hours_needed", yr + "-01-01")),
              round(sum(needed) / len(needed), 4), tol=1.5e-4)
    # the decisions' figures
    say("  the decisions' figures:")
    for e, lab in (("iso:ercot", "ERCOT"), ("iso:caiso", "CAISO")):
        say(f"    end of 2025, {lab}: {fleet.get((e, 'battery_operating_mw', '2025-12'))} MW, {fleet.get((e, 'battery_operating_mwh', '2025-12'))} MWh")
    for e in ("iso:ercot", "iso:caiso", "iso:caiso_own"):
        ms = sorted({k[2][:7] for k in T if k[0] == e and k[1] == "days_held"})
        cut = [m for m in ms if T.get((e, "shoulder_runs_to_midnight", m + "-01")) == 1]
        say(f"    {e}: {len(ms)} months; cut at midnight in {len(cut)}; by year: "
            + ", ".join(f"{y} {sum(1 for m in cut if m.startswith(y))} of {sum(1 for m in ms if m.startswith(y))}" for y in sorted({m[:4] for m in ms})))
        lows = [(m, T.get((e, "midday_low_hour", m + "-01"))) for m in ms]
        night = [m for m, h in lows if h is not None and 1 <= h <= 4]
        mid = [m for m, h in lows if h is not None and 9 <= h <= 14]
        say(f"      lowest hour 01:00 to 04:00 in {len(night)} of {len(ms)} months (last {night[-1] if night else '-'}); 09:00 to 14:00 in {len(mid)}"
            f"; since 2024-07 all in 09 to 14: {all(9 <= (h or -1) <= 14 for m, h in lows if m >= '2024-07')}")
        bat = [m for m in ms if ("iso:ercot" == e) and T.get((e, "avg_battery_mw_h00", m + "-01")) is not None]
        if e == "iso:ercot":
            say(f"      battery output held from {bat[0] if bat else '-'} ({len(bat)} months); the panel's note says 'battery output, from January 2019'")
    a = sorted({k[2][:7] for k in T if k[0] == "iso:caiso" and k[1] == "days_held"})
    b = sorted({k[2][:7] for k in T if k[0] == "iso:caiso_own" and k[1] == "days_held"})
    both = sorted(set(a) & set(b))
    say(f"    both California sources hold {len(both)} months: {both}")


# ---------------------------------------------------------------------------------------------------------------------
def attention():
    say("== /attention: the default view, from the week files of the same build")
    f = json.load(open(os.path.join(WT, "site", "data", "attention.json"), encoding="utf-8"))
    built = datetime.strptime(f["built"], "%Y-%m-%dT%H:%M:%SZ")
    monday = (built - timedelta(days=built.weekday())).strftime("%Y-%m-%d")
    inb = lambda i: f["weeks"][i][:10] <= monday
    den = {d[0]: d for d in f["denominators"]}
    full = [d[0] for d in f["denominators"] if d[3] >= 50 and inb(d[0])]
    wk = max(full)
    say(f"  built {f['built']} (its Monday {monday}); the opening week: {f['weeks'][wk][:10]} (index {wk}); sector 0 = {f['sectors'][0]}; place: every story")
    weekfiles = {}
    for p in glob.glob(os.path.join(WT, "site", "public", "attention", "stories", "*.json")):
        j = json.load(open(p, encoding="utf-8"))
        weekfiles[j["week"][:10]] = [dict(zip(j["columns"], r)) for r in j["rows"]]
        if j.get("built") != f["built"]:
            say(f"  NOTE {os.path.basename(p)} built {j.get('built')}, not the file's")
    ENERGY = set(f["sectors"]) - {"energy"} | {"other_energy"}

    def cell(rows, sector, geo):
        out = [s for s in rows if (s["sector"] in ENERGY if sector == "energy" else s["sector"] == sector)]
        if geo == "US":
            out = [s for s in out if s.get("us") == 1]
        elif geo.startswith("US-"):
            out = [s for s in out if s["state"] == geo[3:]]
        return out
    W = f["weeks"][wk][:10]
    rows = weekfiles[W]
    classified = len(rows)
    d = den[wk]
    check("classified stories of the week (the week file's rows)", d[3], classified)
    check("judged = classified + scored 0 and not sent", d[2], d[3] + d[4])
    sec = f["sectors"][0]
    c = cell(rows, sec, "all")
    opp = [s for s in c if s["opposition"] == 1]
    cellrow = next(x for x in f["cells"] if x[0] == 0 and x[1] == f["geos"].index("all") and x[2] == wk)
    check(f"{sec}, every story, stories", cellrow[3], len(c))
    check(f"{sec}, Attention Index (shown to 2 decimals)", f"{cellrow[4]:.2f}", f"{100 * len(c) / (classified + d[4]):.2f}")
    check(f"{sec}, opposition stories", cellrow[5], len(opp))
    check(f"{sec}, Friction Index (2 decimals)", f"{cellrow[6]:.2f}", f"{100 * len(opp) / len(c):.2f}")
    check(f"{sec}, tone (2 decimals)", f"{cellrow[7]:+.2f}", f"{sum(s['tone'] for s in c) / len(c):+.2f}")
    kinds = {}
    for s in opp:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    check(f"{sec}, kinds of opposition", f.get("kinds", {}).get(f"0|{f['geos'].index('all')}|{wk}", {}), kinds)
    say(f"  the headline row, restated: {len(c)} stories of {d[2]:,} judged ({d[3]:,} classified, {d[4]:,} scored 0 and not sent; {d[1]:,} held); "
        f"Attention Index {100 * len(c) / d[2]:.2f}; Friction Index {100 * len(opp) / len(c):.2f} ({len(opp)} stories: {kinds}); tone {sum(s['tone'] for s in c) / len(c):+.2f}")
    # what rose: the week's sectors and states against the classified weeks among the four before
    classified_weeks = [i for i in den if den[i][3] > 0]
    before = [i for i in range(max(0, wk - 4), wk) if i in classified_weeks]
    say(f"  the weeks before the opening week that count: {[f['weeks'][i][:10] for i in before]} ({len(before)} of the four)")

    def index_of(i, sector, geo):
        rws = weekfiles.get(f["weeks"][i][:10])
        if rws is None:
            return None
        n = len(cell(rws, sector, geo))
        return 100 * n / den[i][2] if n else 0.0
    n_eq = n_all = 0
    for r in [x for x in f["rising"] if x[0] == wk]:
        sector, geo = (f["sectors"][r[2]], "all") if r[1] == "sector" else ("energy", "US-" + r[2])
        this = index_of(wk, sector, geo)
        prev = [index_of(i, sector, geo) or 0.0 for i in before]
        mean = sum(prev) / len(prev)
        n_all += 1
        if abs(round(this, 4) - r[3]) <= 1.5e-4 and abs(round(mean, 4) - r[4]) <= 1.5e-4 and abs(round(this - mean, 4) - r[5]) <= 2.5e-4:
            n_eq += 1
        else:
            say(f"    DIFFER rising {r[:6]} restated {this:.4f} {mean:.4f}")
    check("what rose: rows equal (this week, the mean before, the change)", n_all, n_eq)
    # the places, for the default sector
    pl = {}
    for s in rows:
        if s["place"] and s.get("us") == 1 and s["sector"] == sec:
            k = (s["place"], s["state"])
            a = pl.setdefault(k, [0, 0])
            a[0] += 1
            a[1] += s["opposition"]
    filep = {(p[1], p[2]): [p[4], p[5]] for p in f["places"] if p[3] == wk and p[0] == 0}
    check(f"places named, {sec}", filep, pl)
    top = sorted(pl.items(), key=lambda kv: (-kv[1][0], -kv[1][1], kv[0][0]))[:10]
    say(f"  places as listed (first ten): {top}")
    # the footer
    total = sum(len(v) for v in weekfiles.values())
    oppn = sum(sum(1 for s in v if s["opposition"] == 1) for v in weekfiles.values())
    check("footer: classified stories (sum of week files)", f["counts"]["stories"], total)
    check("footer: reporting opposition", f["counts"]["opposition"], oppn)
    check("footer: weeks with stories", f["counts"]["weeks_with_stories"], len([v for v in weekfiles.values() if v]))
    m = re.match(r"(\d+) of the (\d+) stories held are classified \(([\d.]+) percent\)", f["note"])
    if m:
        check("the note's percent", m.group(3), f"{100 * int(m.group(1)) / int(m.group(2)):.1f}")
        check("the note's classified = the footer's", int(m.group(1)), f["counts"]["stories"])
        check("the note's stories held = the sum of the weeks' stories held", int(m.group(2)), sum(d[1] for d in f["denominators"]))


if __name__ == "__main__":
    for part in (about, resources, attention, shoulder):
        try:
            part()
        except Exception as exc:   # say it and go on: every section is read by itself
            say(f"  FAILED {part.__name__}: {exc!r}")
            FAIL.append(part.__name__)
    say(f"== {len(FAIL)} not equal: {FAIL}")
    sys.exit(1 if FAIL else 0)
