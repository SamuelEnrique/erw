#!/usr/bin/env python3
"""ERW, the Grid tool (/grid): the replication a reader can run (sessions 3703 and 3704, chain 208).

It reads the network's snapshot (the file the page draws: public Storage's erw-public/network/grid_network.json, or the
repository's site/data/grid_network.json), the warehouse's tables as CSV (EIA-930's interchange, generation and CO2, the
carbon intensity the warehouse derives from them, and the tables the Ask panel's stored answers read), and this
folder's assumptions.json, and recomputes every figure page_figures.json lists without the page's code:

- network: the hour shown (the newest hour every reporting pair holds), its age at the snapshot's refresh, each grid's
  ties, their flows signed from its side, its net export or import and the number of ties, the largest flow, the
  largest net exporter; the gravity shape's net import, and its generation and share where the tables hold the hour;
- carbon: the network's carbon intensity per grid (the hour's row of carbon_intensity_hourly), and each month of the
  Clean tab's monthly block computed again from the hours: the month's CO2 (eia930_all_emissions,
  co2_emissions_generated) over its MWh, each hour's MWh being its CO2 over its intensity, over months whose every
  UTC day holds 24 hours;
- ask: each stored answer's figures, the query it names run again on the table (the Ask tool's rules: the filters,
  latest, mean, sum, min, max or count, the groups); a figure is met when the result holds it to its shown decimals.

A figure the page prints as "license needed" is printed so and not computed. A figure whose rows the tables given do not
hold is said so and does not fail the run.

    python replication/grid/replicate.py [--snapshot PATH] [--tables DIR] [--only network,carbon,ask]

Exit 0 when every computed figure is met (inside its tolerance), 1 when one is not, 2 when an input cannot be read.
Standard library and pandas only. Method: docs/methods/grid_network.md, "Replication". mix_now() applies the Mix tab's
latest-hour rules (components/grid/NowView.tsx) to rows a reader reads; it is not part of the comparison (see the method
note).
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SNAPSHOT = os.path.join(ROOT, "site", "data", "grid_network.json")
TABLES = os.path.join(ROOT, "warehouse", "output")
ISOS = ["ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iso_time(s):
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)


def half_up(x):
    """JavaScript's Math.round."""
    return math.floor(x + 0.5)


# ---------------------------------------------------------------- the network, from the snapshot
def complete_hour(hours, links, quiet):
    """The newest hour every reporting pair holds; a pair reports when it held a flow in the last `quiet` hours."""
    n = len(hours)
    last = []
    for l in links:
        i = max((h for h in range(n) if l["mw"][h] is not None), default=-1)
        last.append(i)
    reporting = [l for l, i in zip(links, last) if i >= n - quiet]
    for h in range(n - 1, -1, -1):
        if reporting and all(l["mw"][h] is not None for l in reporting):
            return hours[h], len(links), len(reporting)
    return None, len(links), len(reporting)


def ties(snap, ba, h):
    """A grid's ties with a flow in hour index h, each signed from its side (positive: power left it)."""
    out = []
    for l in snap["links"]:
        v = l["mw"][h]
        if v is None or ba not in (l["a"], l["b"]):
            continue
        out.append((l["b"] if l["a"] == ba else l["a"], float(v) if l["a"] == ba else -float(v)))
    return out


def network(snap, gen_at, a):
    """{check key: value} for the network's and the gravity shape's figures. gen_at: {BA: MW at the hour} or {}."""
    hour, pairs, reporting = complete_hour(snap["hours"], snap["links"], int(a["network_quiet_hours"]["value"]))
    hour = hour or snap["hours"][-1]
    h = snap["hours"].index(hour)
    v = {f"net|lag|{hour}|{snap['built']}": half_up((iso_time(snap["built"]) - iso_time(hour)).total_seconds() / 3600)}
    exports = {}
    for l in snap["links"]:
        x = l["mw"][h]
        if x is None:
            continue
        exports[l["a"]] = exports.get(l["a"], 0.0) + float(x)
        exports[l["b"]] = exports.get(l["b"], 0.0) - float(x)
    best = None
    for k in sorted(exports):
        if best is None or exports[k] > best[1]:
            best = (k, exports[k])
    if best:
        v[f"net|topexport|{hour}"] = best[1]
    for ba in ISOS:
        t = ties(snap, ba, h)
        v[f"net|ties|{ba}|{hour}"] = len(t)
        if not t:
            continue
        s = sum(x for _, x in t)
        v[f"net|export|{ba}|{hour}"] = s
        v[f"net|import|{ba}|{hour}"] = -s
        v[f"net|maxflow|{ba}|{hour}"] = max(abs(x) for _, x in t)
        for other, x in t:
            v[f"net|tie|{ba}|{other}|{hour}"] = x
        g = gen_at.get(ba)
        if g is not None:
            gk = f"series|eia930_all_generation|eia930:{ba}|net_generation_mw|{hour}"
            v[gk] = g
            if g > 0:
                nk = f"net|import|{ba}|{hour}"
                v[f"calc|pct|{nk.replace('|', '~')}|{gk.replace('|', '~')}"] = -s / g * 100
    if gen_at.get("US48") is not None:
        v[f"series|eia930_all_generation|eia930:US48|net_generation_mw|{hour}"] = gen_at["US48"]
    return hour, pairs, reporting, v


# ---------------------------------------------------------------- the tables
def read_table(folder, table, entities=None, variables=None, usecols=None):
    """A table as CSV, '#' header lines skipped, filtered in chunks as it is read; None when the folder does not hold it."""
    path = os.path.join(folder, table + ".csv")
    if not os.path.exists(path):
        return None
    parts = []
    for c in pd.read_csv(path, comment="#", dtype=str, keep_default_na=False, usecols=usecols, chunksize=500_000):
        if entities is not None:
            c = c[c["entity"].isin(entities)]
        if variables is not None:
            c = c[c["variable"].isin(variables)]
        parts.append(c)
    return pd.concat(parts, ignore_index=True)


def generation_at(folder, hour):
    df = read_table(folder, "eia930_all_generation", [f"eia930:{b}" for b in ISOS + ["US48"]], ["net_generation_mw"],
                    usecols=["entity", "variable", "ts_utc", "value"])
    if df is None:
        return {}
    df = df[(df["ts_utc"] == hour) & (df["value"] != "")]
    return {e.split(":", 1)[1]: float(x) for e, x in zip(df["entity"], df["value"])}


def carbon(folder, keys):
    """{key: value} for the carbon keys: an hourly key is its row of carbon_intensity_hourly; a monthly key is the month
    computed again from the hours (see the module's docstring). Keys whose rows the tables lack are left out."""
    hourly = [k for k in keys if k.startswith("series|carbon_intensity_hourly|")]
    monthly = [k for k in keys if k.startswith("series|carbon_intensity_monthly|")]
    ents = sorted({k.split("|")[2] for k in hourly + monthly})
    if not ents:
        return {}
    ci = read_table(folder, "carbon_intensity_hourly", ents, ["intensity_generation"], usecols=["entity", "variable", "ts_utc", "value"])
    if ci is None:
        return {}
    ci = ci[ci["value"] != ""]
    out = {}
    at = {(e, t): float(x) for e, t, x in zip(ci["entity"], ci["ts_utc"], ci["value"])}
    for k in hourly:
        _, _, e, _, t = k.split("|")
        if (e, t) in at:
            out[k] = at[(e, t)]
    if not monthly:
        return out
    months = {(k.split("|")[2], k.split("|")[4][:7]) for k in monthly}
    em = read_table(folder, "eia930_all_emissions", ents, ["co2_emissions_generated"], usecols=["entity", "variable", "ts_utc", "value"])
    if em is None:
        return out
    em = em[(em["value"] != "") & pd.Series([(e, t[:7]) in months for e, t in zip(em["entity"], em["ts_utc"])], index=em.index)]
    co2 = {(e, t): float(x) for e, t, x in zip(em["entity"], em["ts_utc"], em["value"])}
    for k in monthly:
        _, _, e, _, t = k.split("|")
        m = t[:7]
        hrs = sorted(ts for (ee, ts) in at if ee == e and ts[:7] == m)
        days = {}
        for ts in hrs:
            days[ts[:10]] = days.get(ts[:10], 0) + 1
        first = dt.date(int(m[:4]), int(m[5:7]), 1)
        n_days = ((first.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - first).days
        if len(days) != n_days or any(c != 24 for c in days.values()):
            continue   # the month is not whole in the hours given
        tot_co2 = tot_mwh = 0.0
        for ts in hrs:
            c, i = co2.get((e, ts)), at[(e, ts)]
            if c is None or i <= 0:
                tot_co2 = None
                break
            tot_co2 += c
            tot_mwh += c * 1000.0 / i
        if tot_co2 is not None and tot_mwh > 0:
            out[k] = tot_co2 * 1000.0 / tot_mwh
    return out


# ---------------------------------------------------------------- the Ask tool's query, again
def parse_filter(text):
    out = {}
    for part in text.split(", "):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = json.loads(v) if k.strip() == "where" else v.strip()
    return out


def shape_of(df):
    if {"entity", "variable", "ts_utc", "value"} <= set(df.columns):
        return "series"
    if "entity_id" in df.columns:
        return "entities"
    return "events"


def scoped(df, table, scope):
    """warehouse/chat/tools.py scope_rows: the rows of a table that carry the chat's grid."""
    if not scope:
        return df
    if scope.get("filters"):
        for col, val in scope["filters"].items():
            df = df[df[col].isin(val if isinstance(val, list) else [val])]
        return df
    by = scope.get("by")
    if by == "name":
        return df
    if by == "ba" and "ba" in df.columns:
        return df[df["ba"] == scope["ba"]]
    if by == "entity" and "entity" in df.columns:
        return df[df["entity"].str.startswith(scope["slug"] + ":")]
    if by == "isoentity" and "entity" in df.columns:
        return df[df["entity"] == "iso:" + scope["slug"]]
    if by == "market" and "market" in df.columns and scope.get("market_prefix"):
        return df[df["market"].str.startswith(scope["market_prefix"])]
    if by == "queue" and "source_table" in df.columns:
        return df[df["source_table"] == (scope.get("queue_table") or "")]
    if by == "iso" and "iso" in df.columns:
        return df[df["iso"] == scope["iso"]]
    if "ba" in df.columns:
        return df[df["ba"] == scope["ba"]]
    return df


def retrieved(folder, table):
    """The table copy's own "# Retrieved:" time, as YYYY-MM-DDTHH:MM:SSZ, or ""."""
    path = os.path.join(folder, table + ".csv")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            m = re.match(r"# Retrieved: (\d{8})T(\d{6})Z", line)
            if m:
                d, t = m.groups()
                return f"{d[:4]}-{d[4:6]}-{d[6:]}T{t[:2]}:{t[2:4]}:{t[4:]}Z"
    return ""


def run_query(folder, table, args, scope=None):
    """The numbers the Ask tool's query returns (warehouse/chat/tools.py query, the cases the stored answers use):
    every group's value, n and count, the rows matched and the groups (and, for groups, the mean of their values, which
    an answer may state). None when the folder lacks the table."""
    path = os.path.join(folder, table + ".csv")
    if not os.path.exists(path):
        return None
    df = scoped(pd.read_csv(path, comment="#", dtype=str, keep_default_na=False), table, scope)
    shape = shape_of(df)
    keep = pd.Series(True, index=df.index)
    if args.get("entity"):
        col = {"series": "entity", "entities": "entity_id", "events": "source"}[shape]
        keep &= df[col] == args["entity"]
    if args.get("variable"):
        keep &= df["variable"] == args["variable"]
    tcol = {"series": "ts_utc", "entities": "status_date", "events": "event_date"}[shape]
    if (args.get("start") or args.get("end")) and tcol in df:
        t = pd.to_datetime(df[tcol], utc=True, errors="coerce")
        if args.get("start"):
            keep &= t >= pd.Timestamp(args["start"], tz="UTC")
        if args.get("end"):
            keep &= t < pd.Timestamp(args["end"], tz="UTC")
    for col, val in (args.get("where") or {}).items():
        vals = val if isinstance(val, list) else [val]
        keep &= df[col].astype(str).isin([str(x) for x in vals])
    sel = df[keep].copy()
    vcol = {"series": "value", "entities": "capacity_mw", "events": "mw"}[shape]
    agg = args.get("aggregation", "latest")
    nums = [len(sel)]
    if not len(sel):
        return nums
    sel["_v"] = pd.to_numeric(sel[vcol], errors="coerce") if vcol in sel else float("nan")
    if tcol in sel:
        sel["_t"] = pd.to_datetime(sel[tcol], utc=True, errors="coerce")
    gb = args.get("group_by")
    if gb in ("year", "month", "day"):
        keys = sel["_t"].dt.strftime({"year": "%Y", "month": "%Y-%m", "day": "%Y-%m-%d"}[gb])
    elif gb == "entity":
        keys = sel["entity" if shape == "series" else "entity_id"]
    elif gb:
        keys = sel[gb]
    else:
        keys = None

    def one(g):
        if agg == "count":
            return [len(g)]
        if agg == "latest":
            return [float(g.loc[g["_t"].idxmax(), "_v"])]
        v = g["_v"].dropna()
        if not len(v):
            return []
        f = {"mean": v.mean, "sum": v.sum, "min": v.min, "max": v.max, "median": v.median}[agg]
        return [float(f()), len(v)]

    if keys is None:
        if agg == "latest" and shape == "series" and sel.groupby(["entity", "variable"]).ngroups > 1:
            for _, g in sel.groupby(["entity", "variable"]):
                nums += one(g)
        else:
            nums += one(sel)
    else:
        groups = list(sel.groupby(keys, sort=True))
        nums.append(len(groups))
        vals = []
        for _, g in groups:
            r = one(g)
            nums += r
            if r:
                vals.append(r[0])
        if len(vals) > 1:
            nums.append(sum(vals) / len(vals))
    return nums


def ask_numbers(folder, source):
    """The numbers of one stored source's tool result: a query's, or a compare's two sides with b less a and b over a."""
    if source["tool"] == "compare":
        m = re.match(r"a: (\w+) (.*); b: (\w+) (.*)$", source["filter"])
        if not m:
            return None
        a = run_query(folder, m.group(1), parse_filter(m.group(2)), source.get("scope"))
        b = run_query(folder, m.group(3), parse_filter(m.group(4)), source.get("scope"))
        if a is None or b is None:
            return None
        va, vb = (a[1] if len(a) > 1 else None), (b[1] if len(b) > 1 else None)
        extra = [vb - va] if va is not None and vb is not None else []
        if va and vb is not None:
            extra.append(vb / va)
        return a + b + extra
    return run_query(folder, source["tables"][0], parse_filter(source["filter"]), source.get("scope"))


# ---------------------------------------------------------------- the Mix tab's latest hour, as components/grid/NowView.tsx
def mix_now(demand, generation, intensity, ba):
    """The Mix tab's latest-hour figures from rows of eia930_all_demand (demand_mw), eia930_all_generation and
    carbon_intensity_hourly (frames of entity, variable, ts_utc, value, as the live set returns them): {check key: value}
    and the largest source's name. The latest demand hour and the same hour a week earlier; the latest hour that holds
    the total net generation, its sources largest first; each intensity variable's latest hour."""
    e = f"eia930:{ba}"
    out, top = {}, None
    d = demand[(demand["entity"] == e) & (demand["variable"] == "demand_mw")].sort_values("ts_utc")
    if len(d):
        r = d.iloc[-1]
        out[f"series|eia930_all_demand|{e}|demand_mw|{r['ts_utc']}"] = float(r["value"])
        week = (iso_time(r["ts_utc"]) - dt.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        w = d[d["ts_utc"] == week]
        if len(w):
            out[f"series|eia930_all_demand|{e}|demand_mw|{week}"] = float(w.iloc[0]["value"])
    g = generation[generation["entity"] == e]
    tot = g[g["variable"] == "net_generation_mw"].sort_values("ts_utc")
    if len(tot):
        ts = tot.iloc[-1]["ts_utc"]
        out[f"series|eia930_all_generation|{e}|net_generation_mw|{ts}"] = float(tot.iloc[-1]["value"])
        fuels = g[(g["ts_utc"] == ts) & (g["variable"] != "net_generation_mw") & g["variable"].str.startswith("net_generation_")]
        fuels = fuels.assign(v=fuels["value"].astype(float)).sort_values("v", ascending=False)
        for _, f in fuels.iterrows():
            out[f"series|eia930_all_generation|{e}|{f['variable']}|{ts}"] = f["v"]
        if len(fuels):
            top = fuels.iloc[0]["variable"]
    for var in ("intensity_generation", "intensity_demand"):
        c = intensity[(intensity["entity"] == e) & (intensity["variable"] == var)].sort_values("ts_utc")
        if len(c):
            out[f"series|carbon_intensity_hourly|{e}|{var}|{c.iloc[-1]['ts_utc']}"] = float(c.iloc[-1]["value"])
    return out, top


# ---------------------------------------------------------------- the run
def compute(snapshot, tables, page, a, only):
    snap = load_json(snapshot)
    got = {}
    if "network" in only:
        hour, _, _, net = network(snap, {}, a)
        gen = generation_at(tables, hour)
        hour, _, _, net = network(snap, gen, a)
        got.update(net)
    if "carbon" in only:
        got.update(carbon(tables, [f["check"] for f in page["figures"] if f["group"] == "carbon"]))
    ask = {}
    if "ask" in only:
        for f in page["figures"]:
            if f["group"] == "ask" and not f["held"]:
                k = json.dumps(f["source"], sort_keys=True)
                if k not in ask:
                    ask[k] = ask_numbers(tables, f["source"])
    return got, ask


def compare(got, ask, page, a, only, tables=TABLES):
    """[(figure, status, replicated, difference)]: status "yes" (met), "license needed", "not held: ..." or "NO"."""
    rows = []
    for f in page["figures"]:
        grp = "network" if f["group"] in ("network", "gravity") else f["group"]
        if grp not in only:
            continue
        if f["held"]:
            rows.append((f, "license needed", None, None))
            continue
        if f["group"] == "ask":
            nums = ask.get(json.dumps(f["source"], sort_keys=True))
            if nums is None:
                rows.append((f, f"not held: {', '.join(f['source']['tables'])} is not in the tables given", None, None))
                continue
            tol = f["tolerance"] + 1e-9
            hit = [x for x in nums if x is not None and abs(abs(x) - f["raw"]) <= tol]
            if hit:
                rows.append((f, "yes", hit[0], abs(hit[0]) - f["raw"]))
                continue
            got = retrieved(tables, f["source"]["tables"][0])
            if got and f.get("asked_at") and got[:10] != f["asked_at"][:10]:
                # the answer was asked of the live set of its day; a copy of the table made on another day can differ
                rows.append((f, f"no: a known difference (the table's copy was made {got[:10]}, the answer asked {f['asked_at'][:10]})", None, None))
            else:
                rows.append((f, "NO", None, None))
            continue
        v = got.get(f["check"])
        if v is None:
            why = "the tables given do not hold this hour or month whole" if f["group"] in ("carbon", "gravity") else "not computed"
            rows.append((f, f"not held: {why}" if f["group"] in ("carbon", "gravity") else "NO: not computed", None, None))
            continue
        diff = v - f["raw"]
        rows.append((f, "yes" if abs(diff) <= f["tolerance"] + 1e-9 else "NO", v, diff))
    return rows


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--tables", default=TABLES)
    ap.add_argument("--only", default="network,carbon,ask")
    o = ap.parse_args(argv)
    only = set(o.only.split(","))
    try:
        a = load_json(os.path.join(HERE, "assumptions.json"))
        page = load_json(os.path.join(HERE, "page_figures.json"))
        snap = load_json(o.snapshot)
        got, ask = compute(o.snapshot, o.tables, page, a, only)
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {type(exc).__name__}: {exc}")
        return 2
    if "network" in only and snap["built"] != page["snapshot_built"]:
        print(f"the snapshot given was built {snap['built']}; page_figures.json is of the snapshot built {page['snapshot_built']}: "
              "write it again (figures_of_the_page.py --snapshot) to set this snapshot's figures beside the page's")
        return 2
    rows = compare(got, ask, page, a, only, o.tables)
    print(f"The Grid tool (/grid): the snapshot built {snap['built']} (hour shown {page['hour_shown']}), the tables in {o.tables}")
    print("group | figure | key | replication | the page | difference | met")
    for f, status, v, d in rows:
        shown = f["page_text"] or (f"{f['raw']:g}" if f["raw"] is not None else "")
        print(f"{f['group']} | {f['name']} | {f['check']} | {'' if v is None else f'{v:,.4f}'} | {shown} | {'' if d is None else f'{d:+.4f}'} | {status}")
    yes = sum(1 for r in rows if r[1] == "yes")
    held = sum(1 for r in rows if r[1] == "license needed")
    nh = sum(1 for r in rows if r[1].startswith("not held"))
    known = sum(1 for r in rows if r[1].startswith("no: a known"))
    bad = [r for r in rows if r[1].startswith("NO")]
    print(f"{yes} of {len(rows) - held - nh} computed figures met, {known} a known difference; {held} license needed; {nh} not held in the tables given; "
          f"not replicated here: {page['not_replicated']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
