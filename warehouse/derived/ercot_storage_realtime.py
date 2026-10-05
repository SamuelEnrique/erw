#!/usr/bin/env python3
"""What Texas's storage resources did in real time, set beside what they were awarded day-ahead, by month (session 120).

Energy Research Warehouse (ERW). Method: docs/methods/ercot_storage_realtime.md. No request is made.

Table: ercot_storage_rt_monthly. One entity, ercot:esr_fleet, and for each local (Central) month, over the operating
days both disclosures hold (the matched days):

  days_held, days_in_month, resources, resource_hours        what the month rests on
  mw                                  the sum of each resource's highest day-ahead HSL in the month (MW): the same
                                      denominator as ercot_storage_dam_awards_monthly, so the per-MW figures add up
  rt_discharge_mwh, rt_charge_mwh, rt_net_mwh                the fleet's Telemetered Net Output, integrated (MWh)
  da_sold_mwh, da_bought_mwh, da_net_mwh                     its day-ahead energy awards on the same days (MWh)
  rt_deviation_mwh                    rt_net_mwh less da_net_mwh: what it did beyond its day-ahead position
  as_rt_<service>_mwh, as_da_<service>_mwh                   real-time and day-ahead awards of each Ancillary
                                      Service, a MW for an hour (regup, regdn, rrs, ecrs, nspin), and
  as_imbalance_<service>_mwh          real-time less day-ahead: the quantity ERCOT settles at the real-time price of
                                      the service (Protocols 6.7.2.1). Not valued here: that price is in neither file
  revenue_da_energy_usd, revenue_da_ancillary_usd, revenue_da_usd   the day-ahead awards at their own prices, as
                                      the awards table values them, on the matched days (USD)
  revenue_rt_deviation_hub_usd        for each resource and each 15-minute interval, its real-time energy less a
                                      quarter of its day-ahead award of the hour, times the real-time price of the
                                      interval AT THE HUB AVERAGE (HB_HUBAVG), not at the resource's own node (USD)
  revenue_rt_output_hub_usd, revenue_da_position_hub_usd     its two halves: all real-time energy at that price,
                                      and the day-ahead position bought back at it (USD)
  revenue_market_hub_usd              revenue_da_usd plus revenue_rt_deviation_hub_usd (USD)
  <each revenue>_per_mw               over the month's mw (USD/MW; a page's per kW is this over 1,000)
  intervals, intervals_priced         resource-intervals in the month, and those with a hub price: only those are
                                      valued, and the share is stated
  da_node_minus_hub_sold, da_node_minus_hub_bought   the day-ahead price at the resources' own nodes less the hub
                                      average's, weighted by the MWh sold and by the MWh bought (USD/MWh): how far the
                                      nodes stood from the hub, measured where both prices are held

Why the hub, and what that costs. ERCOT settles a resource's real-time energy at the price of its own Resource Node
(Protocols 6.6.3.1), and its charging at the price at its own bus. ERCOT's public list keeps seven days of node prices
and the storage disclosure runs 60 days behind, so for no disclosed day is the node price public (warehouse/connectors/
ercot_rt_spp.py). The hub average is the price the warehouse holds for every interval. It is a stand-in and is named as
one in every variable that rests on it. A battery sits where prices move most; the hub average moves least. What the
stand-in misses is measured two ways and written beside it: da_node_minus_hub_* above, and the table
ercot_storage_node_basis (one real week of real-time prices at the nodes against the hub).

Nothing is filled. An interval with no hub price is not valued and is counted. A day one disclosure holds and the
other does not is not a matched day. A resource-hour in one file and not the other is counted and valued on what it
has: a day-ahead award with no real-time row is a position with no output (bought back in full), and real-time output
with no day-ahead row has no position.

    python warehouse/derived/ercot_storage_realtime.py
    python warehouse/derived/ercot_storage_realtime.py --out-dir <dir>      # a trial: records nothing
"""
import argparse
import calendar
import datetime as dt
import math
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import ercot_sced_esr as sced  # noqa: E402
import iso_prices as ip  # noqa: E402

NAME = "ercot_storage_rt_monthly"
BASIS = "ercot_storage_node_basis"
DAM = "ercot_dam_esr_awards"
DAM_MONTHLY = "ercot_storage_dam_awards_monthly"
HISTORY = "ercot_all_hub_prices_history"
ROLLING = "iso_rtm_hub_prices"
NODE_PRICES = "ercot_rtm_node_prices"
HUB = "HB_HUBAVG"
SOURCE = "erw:ercot_storage_realtime"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ercot_storage_realtime.md"
TZ = "America/Chicago"
ENTITY = "ercot:esr_fleet"
COLS = ip.SERIES_COLS
SERVICES = {"regup": (["x_regup_award_mw"], "x_regup_mcpc", ["as_regup_mwh"]), "regdn": (["x_regdn_award_mw"], "x_regdn_mcpc", ["as_regdn_mwh"]),
            "rrs": (["x_rrspfr_award_mw", "x_rrsffr_award_mw", "x_rrsufr_award_mw"], "x_rrs_mcpc", ["as_rrspfr_mwh", "as_rrsffr_mwh", "as_rrsufr_mwh"]),
            "ecrs": (["x_ecrs_award_mw"], "x_ecrs_mcpc", ["as_ecrs_mwh"]), "nspin": (["x_nonspin_award_mw"], "x_nonspin_mcpc", ["as_nspin_mwh"])}
REVENUES = ["da_energy", "da_ancillary", "da", "rt_deviation_hub", "rt_output_hub", "da_position_hub", "market_hub"]
UNITS = {"usd": "USD", "mwh": "MWh", "mw": "MW", "per_mw": "USD/MW"}


def _num(s):
    return pd.to_numeric(s.where(s != ""), errors="coerce")


def read_dam(first_ts, last_ts, out_dir=None):
    """The day-ahead awards of the storage resources between two UTC hour starts: one row a resource and hour."""
    path = os.path.join(out_dir or ip.OUT_DIR, DAM + ".csv")
    use = ["entity", "ts_utc", "value", "node", "x_energy_award_mw", "x_energy_price_usd_per_mwh"] + [c for a, p, _ in SERVICES.values() for c in a + [p]]
    parts = []
    for chunk in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=use, dtype=str, keep_default_na=False, chunksize=300_000):
        parts.append(chunk[(chunk["ts_utc"] >= first_ts) & (chunk["ts_utc"] <= last_ts)])
    d = pd.concat(parts, ignore_index=True)
    out = pd.DataFrame({"resource": d["entity"].str[len("ercot:"):], "ts_utc": d["ts_utc"], "da_hsl": _num(d["value"]), "node": d["node"],
                        "award": _num(d["x_energy_award_mw"]).fillna(0.0), "da_price": _num(d["x_energy_price_usd_per_mwh"])})
    has = out["award"] != 0
    if (has & out["da_price"].isna()).any():
        raise ValueError(f"{int((has & out['da_price'].isna()).sum())} energy awards have no settlement point price")
    out["da_energy_usd"] = (out["award"] * out["da_price"]).where(has, 0.0)
    for name, (awards, price, _) in SERVICES.items():
        a = sum(_num(d[c]).fillna(0.0) for c in awards)
        m = _num(d[price])
        if ((a != 0) & m.isna()).any():
            raise ValueError(f"{int(((a != 0) & m.isna()).sum())} {name} awards have no clearing price")
        out[f"da_{name}_mw"] = a
        out[f"da_{name}_usd"] = (a * m).where(a != 0, 0.0)
    return out


def read_sced(days_dir=None):
    """Every reduced real-time day on this machine: one row a resource and hour, the hour's start in UTC."""
    parts = []
    for day, _, df in sced.day_frames(days_dir):
        df = df.assign(day=day, ts_utc=df["hour"])   # a reduced day's hour is the hour's start in UTC
        parts.append(df)
    if not parts:
        raise FileNotFoundError("no reduced day under warehouse/raw/ercot_60d_sced/days/: run warehouse/connectors/ercot_sced_esr.py --pull first")
    return pd.concat(parts, ignore_index=True)


def hub_prices(first_ts, out_dir=None):
    """The hub average's real-time price by 15-minute interval start (UTC): the yearly history, then the rolling table
    after it. A Series indexed by the interval's start as an ISO string."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.csv as pcsv
    got = []
    for name in (HISTORY, ROLLING):
        path = os.path.join(out_dir or ip.OUT_DIR, name + ".csv")
        if not os.path.exists(path):
            continue
        cols = ["ts_utc", "value", "freq", "market", "node"]
        types = {c: pa.string() for c in cols}
        types["value"] = pa.float64()
        reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=ip.header_rows(path), block_size=1 << 24),
                               convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
        for b in reader:
            m = pc.and_(pc.and_(pc.equal(b.column("market"), "ercot_rtm"), pc.equal(b.column("node"), HUB)), pc.greater_equal(b.column("ts_utc"), first_ts))
            t = pa.Table.from_batches([b]).filter(m)
            if t.num_rows:
                got.append(t.to_pandas())
    if not got:
        raise FileNotFoundError(f"no real-time price of {HUB} on this machine ({HISTORY}, {ROLLING})")
    p = pd.concat(got, ignore_index=True)
    p = p[p["freq"] == "PT15M"].drop_duplicates("ts_utc", keep="first")   # the history first: it is ERCOT's settled file
    return p.set_index("ts_utc")["value"]


def value_hours(s, d, hub):
    """One row a resource and hour, from the real-time rows s and the day-ahead rows d (outer: a row in either), with
    the hub-priced values. hub: the 15-minute hub price by interval start."""
    m = s.merge(d, on=["resource", "ts_utc"], how="outer", indicator=True)
    t0 = pd.to_datetime(m["ts_utc"], utc=True)
    m["month"] = t0.dt.tz_convert(TZ).dt.strftime("%Y-%m")
    m["local_day"] = t0.dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
    award = m["award"].fillna(0.0)
    out_usd, pos_usd, priced = 0.0, 0.0, 0
    n_priced = pd.Series(0, index=m.index)
    for i, q in enumerate(sced.QUARTERS):
        ts = (t0 + pd.Timedelta(minutes=15 * i)).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        price = ts.map(hub)
        ok = price.notna()
        out_usd = out_usd + (m[q].fillna(0.0) * price).where(ok, 0.0)
        pos_usd = pos_usd + (award / 4.0 * price).where(ok, 0.0)
        n_priced = n_priced + ok.astype(int)
    m["rt_output_hub_usd"], m["da_position_hub_usd"], m["intervals_priced"] = out_usd, pos_usd, n_priced
    return m


def monthly(m, matched_days, mw_by_month):
    """{month: {variable: value}} from the valued resource-hours, over the matched days only."""
    m = m[m["local_day"].isin(matched_days)]
    out = {}
    for month, g in m.groupby("month"):
        y, mo = int(month[:4]), int(month[5:])
        days = sorted(set(g["local_day"]))
        f = lambda c: math.fsum(g[c].fillna(0.0))  # noqa: E731
        v = {"days_held": len(days), "days_in_month": calendar.monthrange(y, mo)[1], "resources": int(g["resource"].nunique()),
             "resource_hours": int(len(g)), "resource_hours_real_time_only": int((g["_merge"] == "left_only").sum()),
             "resource_hours_day_ahead_only": int((g["_merge"] == "right_only").sum())}
        v["rt_discharge_mwh"], v["rt_charge_mwh"], v["rt_net_mwh"] = round(f("discharge_mwh"), 3), round(f("charge_mwh"), 3), round(f("net_output_mwh"), 3)
        aw = g["award"].fillna(0.0)
        v["da_sold_mwh"], v["da_bought_mwh"] = round(math.fsum(aw.where(aw > 0, 0.0)), 3), round(math.fsum((-aw).where(aw < 0, 0.0)), 3)
        v["da_net_mwh"] = round(v["da_sold_mwh"] - v["da_bought_mwh"], 3)
        v["rt_deviation_mwh"] = round(v["rt_net_mwh"] - v["da_net_mwh"], 3)
        anc = 0.0
        for name, (_, _, rt_cols) in SERVICES.items():
            rt = math.fsum(sum(g[c].fillna(0.0) for c in rt_cols))
            da = f(f"da_{name}_mw")
            v[f"as_rt_{name}_mwh"], v[f"as_da_{name}_mwh"], v[f"as_imbalance_{name}_mwh"] = round(rt, 3), round(da, 3), round(rt - da, 3)
            anc += f(f"da_{name}_usd")
        v["revenue_da_energy_usd"], v["revenue_da_ancillary_usd"] = round(f("da_energy_usd"), 2), round(anc, 2)
        v["revenue_da_usd"] = round(v["revenue_da_energy_usd"] + v["revenue_da_ancillary_usd"], 2)
        v["revenue_rt_output_hub_usd"], v["revenue_da_position_hub_usd"] = round(f("rt_output_hub_usd"), 2), round(f("da_position_hub_usd"), 2)
        v["revenue_rt_deviation_hub_usd"] = round(v["revenue_rt_output_hub_usd"] - v["revenue_da_position_hub_usd"], 2)
        v["revenue_market_hub_usd"] = round(v["revenue_da_usd"] + v["revenue_rt_deviation_hub_usd"], 2)
        v["intervals"], v["intervals_priced"] = int(4 * len(g)), int(g["intervals_priced"].sum())
        mw = mw_by_month.get(month)
        if mw:
            v["mw"] = round(mw, 4)
            for r in REVENUES:
                v[f"revenue_{r}_usd_per_mw"] = round(v[f"revenue_{r}_usd"] / mw, 4)
        # how far the nodes stood from the hub day-ahead, where both prices are held
        sold, bought = aw.where(aw > 0, 0.0), (-aw).where(aw < 0, 0.0)
        basis = g["da_price"] - g["da_hub_price"]
        ok = basis.notna()
        if (sold[ok] > 0).any():
            v["da_node_minus_hub_sold"] = round(float((basis[ok] * sold[ok]).sum() / sold[ok].sum()), 4)
        if (bought[ok] > 0).any():
            v["da_node_minus_hub_bought"] = round(float((basis[ok] * bought[ok]).sum() / bought[ok].sum()), 4)
        out[month] = v
    return out


def unit_of(variable):
    if variable.endswith("_per_mw"):
        return UNITS["per_mw"]
    if variable.endswith("_usd"):
        return "USD"
    if variable.endswith("_mwh"):
        return "MWh"
    if variable == "mw":
        return "MW"
    if variable.startswith("da_node_minus_hub"):
        return "USD/MWh"
    return "count"


def node_basis(out_dir=None):
    """One real week at the storage resources' own nodes against the hub average, from the node prices held
    (ercot_rtm_node_prices): for each node, over the intervals both prices hold,

      intervals                 how many
      mean_node, mean_hub       the two mean real-time prices (USD/MWh)
      mean_abs_difference       the mean of |node less hub| (USD/MWh)
      spread_node, spread_hub   a day's mean of its 16 dearest intervals less the mean of its 16 cheapest (four hours
                                each), averaged over the whole days held (USD/MWh): what a battery that moved four hours
                                a day could capture at that price, before losses
    Returns a frame (node, variable, value, first, last), or None when the table is not on the machine."""
    path = os.path.join(out_dir or ip.OUT_DIR, NODE_PRICES + ".csv")
    if not os.path.exists(path):
        return None
    d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["node", "ts_utc", "value", "x_point_type"], dtype={"value": float})
    hub = d[d["node"] == HUB].set_index("ts_utc")["value"]
    if hub.empty:
        return None
    points = sced.settlement_points(out_dir)
    nodes = sorted(set(points.values()))
    rows = []
    local_day = pd.to_datetime(hub.index.to_series(), utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")

    def spread(s):
        g = s.groupby(local_day.reindex(s.index))
        full = [x.sort_values() for _, x in g if len(x) == 96]
        return (sum(x.iloc[-16:].mean() - x.iloc[:16].mean() for x in full) / len(full), len(full)) if full else (None, 0)
    hub_spread, hub_days = spread(hub)
    for node in nodes:
        s = d[d["node"] == node].set_index("ts_utc")["value"]
        both = s.index.intersection(hub.index)
        if len(both) == 0:
            continue
        a, b = s.loc[both], hub.loc[both]
        sp, n_days = spread(a)
        rec = {"intervals": len(both), "mean_node": a.mean(), "mean_hub": b.mean(), "mean_abs_difference": (a - b).abs().mean()}
        if sp is not None and hub_spread is not None and n_days == hub_days:
            rec["spread_node"], rec["spread_hub"], rec["whole_days"] = sp, hub_spread, n_days
        for k, val in rec.items():
            rows.append(dict(node=node, variable=k, value=round(float(val), 4), first=both.min(), last=both.max()))
    return pd.DataFrame(rows) if rows else None


ALL_NODES = "esr_nodes"   # the entity (ercot:esr_nodes) of the rows that sum the settlement points up


def basis_summary(nb):
    """The settlement points of node_basis() together, each point counted once whatever stands behind it: how many,
    over how many whole days, the hub's spread, and the points' spread (their median, mean, lowest and highest tenth)
    and distance from the hub. Only points with every whole day the hub has are in the spread figures. {variable: value}."""
    w = nb.pivot(index="node", columns="variable", values="value")
    out = {"nodes": int(len(w)), "intervals_median": float(w["intervals"].median()), "mean_node_median": float(w["mean_node"].median()),
           "mean_hub": float(w["mean_hub"].median()), "mean_abs_difference_median": float(w["mean_abs_difference"].median())}
    if "spread_node" in w.columns and w["spread_node"].notna().any():
        k = w[w["spread_node"].notna()]
        out.update({"nodes_with_spread": int(len(k)), "whole_days": int(k["whole_days"].iloc[0]), "spread_hub": float(k["spread_hub"].iloc[0]),
                    "spread_node_median": float(k["spread_node"].median()), "spread_node_mean": float(k["spread_node"].mean()),
                    "spread_node_p10": float(k["spread_node"].quantile(0.1)), "spread_node_p90": float(k["spread_node"].quantile(0.9)),
                    "nodes_spread_above_hub": int((k["spread_node"] > k["spread_hub"]).sum())})
        if k["whole_days"].nunique() != 1 or k["spread_hub"].nunique() != 1:
            raise RuntimeError("the settlement points do not share one hub spread over the same whole days")
    return {k_: (v if isinstance(v, int) else round(v, 4)) for k_, v in out.items()}


def write_table(name, rows, header, log, out_dir=None):
    out = pd.DataFrame(rows)[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
    if out.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError(f"{name}: two rows share a key")
    path = os.path.join(out_dir or ip.OUT_DIR, name + ".csv")
    if not out_dir:
        ip._require_lock(path, f"writing {name}")
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        for h in header + [f"File holds {len(out)} rows, rewritten whole by this run."]:
            f.write("# " + h + "\n")
        out.to_csv(f, index=False, lineterminator="\n")
    os.replace(path + ".tmp", path)
    log(f"  wrote {name}.csv: {len(out)} rows")
    print(f"{name}.csv: rows={len(out)}")
    return len(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT storage in real time, by month (session 120)")
    ap.add_argument("--out-dir", help="a trial: the tables under this directory; nothing recorded")
    a = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = os.path.join(a.out_dir or ip.OUT_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"ercot_storage_realtime_{run_id}.log"))
    results = []
    try:
        s = read_sced()
        first_ts, last_ts = s["ts_utc"].min(), s["ts_utc"].max()
        rt_days = sorted(set(s["day"]))
        log(f"real time: {len(s):,} resource-hours on {len(rt_days)} operating days, {rt_days[0]} to {rt_days[-1]}")
        d = read_dam(first_ts, last_ts)
        da_local = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
        da_days = set(da_local)
        matched = sorted(set(rt_days) & da_days)
        log(f"day-ahead: {len(d):,} resource-hours on {len(da_days)} operating days in that span; matched days {len(matched)}; "
            f"real time only {sorted(set(rt_days) - da_days)[:10]}; day-ahead only {sorted(da_days - set(rt_days))[:10]}")
        hub = hub_prices(first_ts)
        log(f"hub: {len(hub):,} 15-minute real-time prices of {HUB}, {hub.index.min()} to {hub.index.max()}")
        # the hub's day-ahead price by hour, for the measure of how far the nodes stood from it
        import price_board as pb
        dah = pb.read_table(HISTORY, market="ercot_dam", node=HUB, since=first_ts)
        rolling = pb.read_table("iso_dam_hub_prices", market="ercot_dam", node=HUB, since=first_ts)
        dah = pd.concat([dah, rolling[~rolling["ts_utc"].isin(set(dah["ts_utc"]))]], ignore_index=True)
        d["da_hub_price"] = d["ts_utc"].map(dah.drop_duplicates("ts_utc").set_index("ts_utc")["value"])
        m = value_hours(s, d, hub)
        # the denominator: each resource's highest day-ahead HSL in the month, as the awards table has it
        dm = d.assign(month=pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m"), local_day=da_local)
        dm = dm[dm["local_day"].isin(matched)]
        mw = dm.groupby(["month", "resource"])["da_hsl"].max().groupby("month").apply(lambda x: math.fsum(x.clip(lower=0)))
        months = monthly(m, set(matched), mw.to_dict())
        # a check against the awards table: over a month whose days are the same, the day-ahead revenue must be the same
        checked = []
        awards_path = os.path.join(ip.OUT_DIR, DAM_MONTHLY + ".csv")
        if os.path.exists(awards_path):
            aw = pd.read_csv(awards_path, skiprows=ip.header_rows(awards_path), dtype=str, keep_default_na=False)
            aw = aw.assign(month=aw["ts_utc"].str[:7], v=aw["value"].astype(float)).pivot(index="month", columns="variable", values="v")
            for month, v in months.items():
                if month in aw.index and int(aw.loc[month, "days_held"]) == v["days_held"]:
                    for mine, theirs in (("revenue_da_usd", "revenue_total_usd"), ("da_sold_mwh", "energy_sold_mwh"), ("mw", "mw")):
                        if abs(v[mine] - float(aw.loc[month, theirs])) > max(0.5, 1e-7 * abs(v[mine])):
                            raise RuntimeError(f"{month}: {mine} {v[mine]} is not {DAM_MONTHLY}'s {theirs} {aw.loc[month, theirs]}; nothing written")
                    checked.append(month)
        log(f"day-ahead revenue, MWh sold and MW equal {DAM_MONTHLY}'s in {len(checked)} months of the same days: {', '.join(checked)}")
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        base = dict(entity=ENTITY, geo="US-TX", market="", node="", freq="P1M", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
        rows = [dict(base, variable=k, ts_utc=f"{month}-01T00:00:00Z", value=val, unit=unit_of(k)) for month, v in sorted(months.items()) for k, val in v.items()]
        priced = sum(v["intervals_priced"] for v in months.values())
        total = sum(v["intervals"] for v in months.values())
        header = [
            "Energy Research Warehouse (ERW): what ERCOT's storage resources did in real time, beside what they were awarded day-ahead, by month (derived, session 120)",
            "Shape: series (docs/datastandard.md v0), entity ercot:esr_fleet, freq P1M, ts_utc the first day of the local (Central) month at 00:00:00Z. Over the operating "
            "days both disclosures hold. Variables: days_held, days_in_month, resources, resource_hours (and those in one file only); mw (each resource's highest day-ahead "
            "HSL of the month, added up); rt_discharge_mwh, rt_charge_mwh, rt_net_mwh (Telemetered Net Output integrated); da_sold_mwh, da_bought_mwh, da_net_mwh; "
            "rt_deviation_mwh; as_rt_<service>_mwh, as_da_<service>_mwh, as_imbalance_<service>_mwh (regup, regdn, rrs, ecrs, nspin: a MW for an hour); "
            "revenue_da_energy_usd, revenue_da_ancillary_usd, revenue_da_usd (the day-ahead awards at their own prices); revenue_rt_output_hub_usd, "
            "revenue_da_position_hub_usd, revenue_rt_deviation_hub_usd, revenue_market_hub_usd; each revenue also _per_mw; intervals, intervals_priced; "
            "da_node_minus_hub_sold, da_node_minus_hub_bought (USD/MWh).",
            f"THE REAL-TIME VALUES ARE AT THE HUB AVERAGE'S PRICE ({HUB}), NOT AT EACH RESOURCE'S OWN NODE. ERCOT settles real-time energy at the Resource Node "
            "(Nodal Protocols 6.6.3.1); its public list keeps seven days of node prices and this disclosure is 60 days old when it is published, so the node price of a "
            "disclosed day is not public. Every variable that rests on the hub price carries _hub in its name.",
            "What it leaves out: contracts and tolls outside the market; the real-time Ancillary Service imbalance (the quantities are here, the real-time prices are in "
            "neither file); Set Point Deviation Charges (Protocols 6.6.5.5), make-whole payments and every other charge and credit of the settlement statement. Real-time "
            "energy is telemetry, not the settlement meter. It is not what any battery earned.",
            f"Operating days: {len(matched)} matched, {matched[0]} to {matched[-1]}. Resource-intervals valued: {priced:,} of {total:,} (the rest have no hub price and are not valued).",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_storage_realtime.py",
            f"Run log: warehouse/output/logs/ercot_storage_realtime_{run_id}.log",
            f"Source: {SOURCE} ERW derived table (docs/methods/ercot_storage_realtime.md), {METHOD_URL}",
            f"Derived from: ercot_sced_esr_hourly; {DAM}; {HISTORY}; {ROLLING}; iso_dam_hub_prices",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): ERCOT's public disclosures and prices.",
        ]
        n = write_table(NAME, rows, header, log, a.out_dir)
        results.append(dict(table=NAME, market="derived", status="ok", detail=f"{n} rows; {len(months)} months; {len(matched)} matched days; {priced:,} of {total:,} intervals priced"))
        nb = node_basis()
        if nb is not None:
            brow = [dict(entity="ercot:" + r["node"], variable=r["variable"], ts_utc=r["first"][:10] + "T00:00:00Z", value=r["value"],
                         unit="count" if r["variable"] in ("intervals", "whole_days") else "USD/MWh", freq="P1W", geo="US-TX", market="ercot_rtm", node=r["node"],
                         source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="") for r in nb.to_dict("records")]
            count = ("nodes", "nodes_with_spread", "whole_days", "nodes_spread_above_hub", "intervals_median")
            brow += [dict(entity="ercot:" + ALL_NODES, variable=k, ts_utc=nb["first"].min()[:10] + "T00:00:00Z", value=val, unit="count" if k in count else "USD/MWh",
                          freq="P1W", geo="US-TX", market="ercot_rtm", node="", source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="")
                     for k, val in basis_summary(nb).items()]
            bh = [
                "Energy Research Warehouse (ERW): the real-time price at each storage resource's settlement point against the hub average, over the days of node "
                "prices held (derived, session 120)",
                "Shape: series (docs/datastandard.md v0), entity ercot:<settlement point>, ts_utc the first day held. Variables: intervals (15-minute intervals both "
                f"prices hold); mean_node, mean_hub (USD/MWh; the hub is {HUB}); mean_abs_difference (the mean of the absolute difference, USD/MWh); spread_node, "
                "spread_hub (a day's 16 dearest intervals less its 16 cheapest, averaged over whole_days: what moving four hours a day could capture, before losses). "
                f"The entity ercot:{ALL_NODES} sums the points up, each counted once: nodes, nodes_with_spread, whole_days, spread_hub, spread_node_median, _mean, _p10, _p90, "
                "nodes_spread_above_hub, mean_node_median, mean_hub, mean_abs_difference_median, intervals_median.",
                f"Coverage: {nb['node'].nunique()} settlement points, {nb['first'].min()} to {nb['last'].max()}. ERCOT's public list keeps seven days of node prices: this is "
                "the week listed when it was pulled, not the months the storage disclosure covers.",
                f"Retrieved: {run_id} (UTC) by warehouse/derived/ercot_storage_realtime.py",
                f"Run log: warehouse/output/logs/ercot_storage_realtime_{run_id}.log",
                f"Source: {SOURCE} ERW derived table (docs/methods/ercot_storage_realtime.md), {METHOD_URL}",
                f"Derived from: {NODE_PRICES}; {DAM}",
                "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): ERCOT's public prices and disclosures.",
            ]
            nbn = write_table(BASIS, brow, bh, log, a.out_dir)
            results.append(dict(table=BASIS, market="derived", status="ok", detail=f"{nbn} rows; {nb['node'].nunique()} settlement points"))
        else:
            log(f"  {NODE_PRICES} is not on this machine: {BASIS} not written")
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="ERCOT storage in real time beside its day-ahead awards, by month, and the storage nodes' prices against the hub (docs/methods/ercot_storage_realtime.md)",
                                    report_url=METHOD_URL, document_list="", license="public", tables=[NAME] + ([BASIS] if nb is not None else []))])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"ercot_storage_realtime FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not a.out_dir:
        ip.write_status("ercot_storage_realtime", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
