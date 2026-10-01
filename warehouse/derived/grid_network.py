#!/usr/bin/env python3
"""The grid network (session 42's Part B, run in session 49): nodes and links of the US balancing authorities, and the
static snapshot the /network page draws.

Energy Research Warehouse (ERW) derived tables, from eia930_all_interchange (EIA-930 hourly interchange, every BA pair
EIA reports), eia930_all_demand and carbon_intensity_hourly:

    warehouse/output/grid_network_nodes.csv   one entity per BA: demand_mw and intensity_generation (latest hour, the
                                              seven ISO BAs the warehouse holds), interchange_volume_mwh (the window)
    warehouse/output/grid_network_links.csv   one entity per BA pair and hour, the last 168 hours: flow_mw
    site/data/grid_network.json               the snapshot: nodes with fixed 3D positions, 168 hours of links

    python warehouse/derived/grid_network.py

The pair rule (each pair counted once): a pair's flow is read from the BA whose code sorts first, as that BA reported
it (positive = it exported to the other); in an hour it did not report, from the other BA's report with the sign
flipped. Both BAs' reports are in eia930_all_interchange.
Positions: a 3D force layout computed once per build with a fixed seed (42), links weighted by their mean flow, so the
page never re-settles them and a reader's mental map holds while the data change.
"""

import datetime as dt
import glob
import json
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NODES, LINKS = "grid_network_nodes", "grid_network_links"
SOURCE = "erw:grid_network"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md"
SNAPSHOT = os.path.join(ROOT, "site", "data", "grid_network.json")
HOURS = 168
ISO = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "MISO": "MISO", "NYIS": "NYISO", "PJM": "PJM", "SWPP": "SPP"}
# EIA reports interchange between its regions and with whole countries too (the same flows, summed): not nodes here
REGIONS = {"CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NY", "NW", "SE", "SW", "TEN", "TEX", "US48", "CAN", "MEX"}
RULE = ("Each pair is counted once: its flow is read from the BA whose code sorts first, as that BA reported it (positive "
        "= it exported to the other); in an hour it did not report, from the other BA's report with the sign flipped.")


def read(name, usecols=None):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, usecols=usecols)


def ba_names():
    """BA code -> EIA's name (EIA's fromba-name and toba-name): the committed snapshot's names first, then the raw pages
    of the interchange connector's runs and its checkpoints, newer over older (on the GitHub runner only the run's own
    raw pages are there)."""
    names = {}
    if os.path.exists(SNAPSHOT):
        with open(SNAPSHOT, encoding="utf-8") as f:
            names.update({n["id"]: n["name"] for n in json.load(f).get("nodes", []) if n.get("name") and n["name"] != n["id"]})
    for f in sorted(glob.glob(os.path.join(ip.RAW_DIR, "eia930_interchange", "*", "*"))):
        if f.endswith(".csv"):
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                for r in json.load(fh).get("response", {}).get("data", []):
                    names[r["fromba"]] = r.get("fromba-name") or names.get(r["fromba"], r["fromba"])
                    names[r["toba"]] = r.get("toba-name") or names.get(r["toba"], r["toba"])
        except (ValueError, KeyError, OSError, UnicodeDecodeError):
            continue
    for f in sorted(glob.glob(os.path.join(ip.RAW_DIR, "eia930_interchange", "checkpoints", "*.csv"))):
        d = pd.read_csv(f, dtype=str, keep_default_na=False, usecols=lambda c: c in ("fromba", "fromba-name", "toba", "toba-name"))
        names.update(dict(zip(d["fromba"], d["fromba-name"])))
        names.update(dict(zip(d["toba"], d["toba-name"])))
    return names


def layout(codes, weights, seed=42, steps=600):
    """A 3D Fruchterman-Reingold layout: repulsion between every pair, attraction along links (weight in [0, 1])."""
    rng = np.random.default_rng(seed)
    n = len(codes)
    pos = rng.uniform(-1, 1, (n, 3))
    idx = {c: i for i, c in enumerate(codes)}
    edges = [(idx[a], idx[b], w) for (a, b), w in weights.items()]
    k = 1.0 / np.sqrt(n)
    t = 0.2
    for _ in range(steps):
        d = pos[:, None, :] - pos[None, :, :]
        dist = np.linalg.norm(d, axis=2) + 1e-6
        disp = ((k * k / dist ** 2)[:, :, None] * d).sum(axis=1)
        for i, j, w in edges:
            v = pos[i] - pos[j]
            dd = np.linalg.norm(v) + 1e-6
            f = (dd * dd / k) * (0.3 + w) * v / dd
            disp[i] -= f
            disp[j] += f
        ln = np.linalg.norm(disp, axis=1) + 1e-9
        pos += disp / ln[:, None] * np.minimum(ln, t)[:, None]
        t = max(0.005, t * 0.99)
    pos -= pos.mean(axis=0)
    return pos / np.abs(pos).max() * 300


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}T{run_id[9:11]}:{run_id[11:13]}:{run_id[13:15]}Z"
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"grid_network_{run_id}.log"))
    results = []
    try:
        x = read("eia930_all_interchange", ["entity", "ts_utc", "value", "ba", "x_to_ba"])
        x["ts"] = pd.to_datetime(x["ts_utc"], utc=True)
        end = x["ts"].max() + pd.Timedelta(hours=1)
        start = end - pd.Timedelta(hours=HOURS)
        x = x[x["ts"] >= start]
        x["a"], x["b"] = x["ba"].str.upper(), x["x_to_ba"].str.upper()
        n_all = len(x)
        x = x[~x["a"].isin(REGIONS) & ~x["b"].isin(REGIONS)]  # balancing authorities only
        log(f"{n_all - len(x)} reports between EIA regions or with whole countries left out ({', '.join(sorted(REGIONS))})")
        hours = pd.date_range(start, end - pd.Timedelta(hours=1), freq="h", tz="UTC")
        # the pair rule
        x["first"] = np.where(x["a"] < x["b"], x["a"], x["b"])
        x["second"] = np.where(x["a"] < x["b"], x["b"], x["a"])
        x["flow"] = np.where(x["a"] < x["b"], x["value"], -x["value"])
        x["by_first"] = x["a"] < x["b"]
        x = x.sort_values(["first", "second", "ts", "by_first"])
        pick = x.drop_duplicates(["first", "second", "ts"], keep="last")  # the first BA's report when it exists
        n_both = int(x.duplicated(["first", "second", "ts"], keep=False).sum() // 2)
        log(f"window {start} to {end}: {len(x)} reports, {len(pick)} pair-hours ({n_both} reported by both BAs)")
        pairs = sorted(set(zip(pick["first"], pick["second"])))
        flow = {p: dict(zip(g["ts"], g["flow"])) for p, g in pick.groupby(["first", "second"])}
        codes = sorted({c for p in pairs for c in p})
        names = ba_names()
        # node figures
        vol = {c: 0.0 for c in codes}
        for (a, b), f in flow.items():
            v = float(np.abs(list(f.values())).sum())
            vol[a] += v
            vol[b] += v
        dem = read("eia930_all_demand", ["entity", "variable", "ts_utc", "value"])
        dem = dem[dem["variable"] == "demand_mw"]
        ci = read("carbon_intensity_hourly", ["entity", "variable", "ts_utc", "value"])
        ci = ci[ci["variable"] == "intensity_generation"]

        def latest(df, code):
            g = df[df["entity"] == f"eia930:{code}"]
            if not len(g):
                return None, None
            r = g.sort_values("ts_utc").iloc[-1]
            return float(r["value"]), str(r["ts_utc"])
        mean_abs = {p: float(np.mean(np.abs(list(f.values())))) for p, f in flow.items()}
        top = max(mean_abs.values()) if mean_abs else 1.0
        pos = layout(codes, {p: np.sqrt(v / top) for p, v in mean_abs.items()})
        nodes, node_rows = [], []
        for i, c in enumerate(codes):
            d, dts = latest(dem, c) if c in ISO else (None, None)
            it, its = latest(ci, c) if c in ISO else (None, None)
            nodes.append(dict(id=c, name=names.get(c, c), iso=ISO.get(c), demand_mw=d, demand_ts=dts, intensity=it, intensity_ts=its,
                              volume_mwh=round(vol[c], 1), x=round(float(pos[i, 0]), 2), y=round(float(pos[i, 1]), 2), z=round(float(pos[i, 2]), 2)))
            base = dict(entity=f"eia930:{c}", freq="PT1H", geo="", market="", node="", source=SOURCE, source_url=METHOD_URL,
                        retrieved_at=retrieved, vintage="", ba=c.lower(), x_name=names.get(c, c), x_iso=ISO.get(c, ""))
            if d is not None:
                node_rows.append(dict(base, variable="demand_mw", ts_utc=dts, value=d, unit="MW"))
            if it is not None:
                node_rows.append(dict(base, variable="intensity_generation", ts_utc=its, value=it, unit="kgCO2/MWh"))
            node_rows.append(dict(base, variable="interchange_volume_mwh", ts_utc=start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                  value=round(vol[c], 1), unit="MWh", freq=f"PT{HOURS}H"))
        link_rows, links = [], []
        for (a, b) in pairs:
            f = flow[(a, b)]
            series = [None if h not in f else round(float(f[h]), 1) for h in hours]
            links.append(dict(a=a, b=b, mw=series))
            for h, v in f.items():
                link_rows.append(dict(entity=f"eia930:{a}-{b}", variable="flow_mw", ts_utc=h.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                      value=float(v), unit="MW", freq="PT1H", geo="", market="", node="", source=SOURCE,
                                      source_url=METHOD_URL, retrieved_at=retrieved, vintage="", ba=a.lower(), x_to_ba=b.lower()))
        hdr = lambda what, cols: [  # noqa: E731
            f"Energy Research Warehouse (ERW): the grid network, {what} (derived, session 49; session 42's Part B)",
            f"Shape: series (docs/datastandard.md v0), partition column ba. {cols}",
            f"Window: {HOURS} hours, {start:%Y-%m-%dT%H:%M:%SZ} to {end:%Y-%m-%dT%H:%M:%SZ} (the latest hours of eia930_all_interchange).",
            f"Pair rule: {RULE}",
            "Balancing authorities only: EIA's regions and its country totals (" + ", ".join(sorted(REGIONS)) + ") are left out, "
            "since their interchange repeats their BAs'.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/grid_network.py",
            f"Run log: warehouse/output/logs/grid_network_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, grid network method (docs/methods/grid_network.md), {METHOD_URL}",
            "Derived from: eia930_all_interchange; eia930_all_demand; carbon_intensity_hourly",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23)."]
        for name, rows, cols, key, header in (
                (NODES, node_rows, ip.SERIES_COLS + ["ba", "x_name", "x_iso"], ["entity", "variable", "ts_utc"],
                 hdr("nodes, one per balancing authority", "demand_mw and intensity_generation: the latest hour held (the seven ISO BAs); "
                     "interchange_volume_mwh: the sum over the window of the absolute hourly flow on every link of the BA. x_name: "
                     "EIA's name; x_iso: the ISO, where the BA is one.")),
                (LINKS, link_rows, ip.SERIES_COLS + ["ba", "x_to_ba"], ["entity", "variable", "ts_utc"],
                 hdr("links, one per BA pair and hour", "entity eia930:<A>-<B>, A the code that sorts first; flow_mw, MW, positive "
                     "when A exported to B; ba is A, x_to_ba is B."))):
            path = os.path.join(ip.OUT_DIR, name + ".csv")
            if os.path.exists(path):
                os.remove(path)  # a rolling snapshot: rewritten whole each build
            ip.write_csv(pd.DataFrame(rows)[cols], name, header, log, cols=cols, key=key)
            results.append(dict(table=name, market="all", status="ok", detail=f"{len(rows)} rows"))
        snap = dict(built=retrieved, window=[start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")],
                    hours=[h.strftime("%Y-%m-%dT%H:%M:%SZ") for h in hours], rule=RULE, seed=42,
                    sources=["eia930_all_interchange", "eia930_all_demand", "carbon_intensity_hourly"], nodes=nodes, links=links)
        with open(SNAPSHOT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snap, f, separators=(",", ":"))
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)",
                                report="The grid network (warehouse/derived/grid_network.py)", report_url=METHOD_URL,
                                document_list="", license="public", tables=[NODES, LINKS])])
        msg = f"{len(codes)} BAs, {len(pairs)} pairs, {len(link_rows)} pair-hours; snapshot {os.path.getsize(SNAPSHOT) / 1024:.0f} KB"
        log(msg)
        print(f"grid_network: {msg}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"grid_network FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NODES, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("grid_network", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
