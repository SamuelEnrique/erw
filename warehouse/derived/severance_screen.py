#!/usr/bin/env python3
"""The Texas severance refund finder (session 57): which leases may be paying more severance tax than the rules
require, and how much might they save.

Energy Research Warehouse (ERW) derived tables, internal. For every Texas lease in the RRC dump (the latest 48
production months, read county by county from warehouse/raw/rrc_pdq/<run>/counties48/, written there by
warehouse/connectors/rrc_statewide.py), it tests, month by month over the latest 24, the three rules the data can test,
with the rules and their citations from site/data/severance_rules.json:

    tx_lp_oil    low-producing oil lease credit (Exempt Type 11): the lease's oil averages less than 15 barrels per
                 well per day over the months of the 90 days ending with the month (the months it produced oil), with
                 the wells the RRC lists on the lease and no shut-in date (OG_WELL_COMPLETION, at the extract); the
                 credit is set by the Comptroller's certified price for the month
    tx_lp_gas    low-producing gas well credit: a gas lease (one gas well) averaging 90 Mcf a day or less over the three
                 months before (the months with a filed report; the month itself when none); certified price tier
    tx_inactive  two-year inactive wells (oil Sec. 202.056(b); gas Type 16): a lease producing again after 24 months or
                 more without production, having produced before. Two cases:
                 seen   the lease's production before the gap is in the 48 months read: the saving is estimated on the
                        volume the lease made in an average producing month of the 12 before the gap, at most (an
                        inactive well returning; new wells drilled on the lease are not exempt), each month from the
                        resumption to the end of the window
                 older  the gap runs back past the 48 months read, and the RRC's first month for the lease
                        (OG_SUMMARY_ONSHORE_LEASE, CYCLE_YEAR_MONTH_MIN) is at least 12 months before them: an old
                        lease whose production before the gap is not read; flagged, no saving estimated
                 A lease whose first RRC month falls inside the gap is new, not inactive, and is not flagged (session
                 57's first run flagged such leases: new Permian leases report zeros before their first well
                 produces).

These are the lease tool's tests (site/lib/lease.ts: txOilLease, txGasAverage, inactiveBefore), with two differences
the data forces, stated in each flag: the oil test divides by the RRC's well count (the lease tool reads a real lease as
one well), and the inactive run counts unfiled months as months without production (the lease tool's file holds only
filed months, so an unfiled month ends its run).

For every flag: the months, the test each month met, and the estimated tax at the base rate against the tax with the
credit or exemption, at the warehouse's monthly prices (WTI Cushing for oil and condensate, Henry Hub for gas, applied
per Mcf as if one Mcf held one MMBtu; monthly means of EIA's daily spot prices, eia_fuel_spot_prices), labeled as such.
A month whose certified price is not in the rules file gives no credit and no saving. "May qualify", never "qualifies":
each flag states what the data cannot see (certification and the Comptroller's and the Commission's forms, filings
already made, per-well volumes, water, the operator's own prices), and none of it is tax advice.

    python warehouse/derived/severance_screen.py

Writes (internal: not in git, the public database, public Redivis or any committed JSON):

    warehouse/output/severance_screen_flags.csv.gz   one row per lease and rule: the months, the test, base tax, tax
                                                     with the rule, the potential saving, what the flag cannot see
    warehouse/output/severance_screen_summary.json   totals by rule, by county, by operator (top 50), the largest leases
"""

import datetime as dt
import gzip
import glob
import json
import os
import sys
import time
import traceback
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import rrc_statewide as rs  # noqa: E402

RULES = os.path.join(ROOT, "site", "data", "severance_rules.json")
FLAGS = "severance_screen_flags"
SUMMARY = "severance_screen_summary"
WINDOW, HISTORY = 24, 48
NOT_SEEN = {
    "tx_lp_oil": ["certification: the operator must apply on Form AP-216 and the Comptroller must approve",
                  "the water test (less than 5 percent recoverable oil per barrel of water): the dump has no water volumes",
                  "per-well volumes: the RRC reports leases; the test divides the lease's oil by the wells listed and not shut in at the extract, not by the wells that produced each month",
                  "filings already made: a credit already claimed is not in the dump"],
    "tx_lp_gas": ["certification: Form AP-217 and the Comptroller's approval",
                  "flared gas, which the test excludes: the dump's gas volume is the lease's production",
                  "high-cost gas already reported for the same well and period (the two cannot be combined)",
                  "filings already made: a credit already claimed is not in the dump"],
    "tx_inactive": ["designation: the Railroad Commission must designate the well a two-year inactive well; five years from then",
                    "per-well history: the RRC reports leases, so a lease whose other wells kept producing hides an inactive well, and a resumed lease may resume from a well that was never inactive",
                    "the application dates and other conditions of Sec. 202.056, which the rules file does not state",
                    "filings already made: an exemption already claimed is not in the dump"],
}


def rules_of():
    with open(RULES, encoding="utf-8") as f:
        r = json.load(f)
    tx = r["states"]["TX"]["products"]
    opt = lambda p, i: next(o for o in tx[p]["options"] if o["id"] == i)  # noqa: E731
    base = lambda p: tx[p]["base"][0]  # noqa: E731
    return dict(version=r["version"], sources=r["sources"],
                oil=base("oil"), gas=base("gas"), cond=base("condensate"),
                lp_oil=opt("oil", "tx_lp_oil"), lp_gas=opt("gas", "tx_lp_gas"), inactive_oil=opt("oil", "tx_oil_inactive"),
                inactive_gas=opt("gas", "tx_gas_inactive"))


def credit_pct(option, period):
    """The credit percent and certified price for a production month, as lib/severance.ts's creditPct: the first of the
    option's bounds whose 'above' is null or below the certified price. (None, None) when the rules file holds no
    certified price for the month."""
    c = next((x for x in option["certified"]["prices"] if x["period"] == period), None)
    if c is None:
        return None, None
    b = next(t for t in option["bounds"] if t["above"] is None or c["price"] > t["above"])
    return b["pct"], c["price"]


def prices_of():
    """Monthly means of EIA's daily spot prices: WTI Cushing (USD/bbl) and Henry Hub (USD/MMBtu)."""
    path = os.path.join(ip.OUT_DIR, "eia_fuel_spot_prices.csv")
    n = sum(1 for ln in open(path, encoding="utf-8") if ln.startswith("#"))
    d = pd.read_csv(path, skiprows=n, usecols=["entity", "variable", "ts_utc", "value"])
    d = d[d["entity"].isin(["eia:wti_cushing", "eia:henry_hub"]) & (d["variable"] == "spot_price")]
    d["m"] = d["ts_utc"].str[:7]
    g = d.groupby(["entity", "m"])["value"].mean()
    return g.loc["eia:wti_cushing"].to_dict(), g.loc["eia:henry_hub"].to_dict()


def shift(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def days_in(m):
    y, mo = int(m[:4]), int(m[5:7])
    return (dt.date(y + (mo == 12), mo % 12 + 1, 1) - dt.date(y, mo, 1)).days


def lease_arrays(df, months):
    """Per lease (summed over counties), arrays over the 48 months: oil, gas, cond, csgd, filed, present; and the
    lease's facts (the county with most rows, operator of the latest month, names)."""
    ix = {m: i for i, m in enumerate(months)}
    df = df.assign(t=df["CYCLE_YEAR_MONTH"].map(lambda s: ix.get(f"{s[:4]}-{s[4:]}")))
    df = df[df["t"].notna()]
    df["t"] = df["t"].astype(int)
    df["lease_id"] = df["OIL_GAS_CODE"] + "-" + df["DISTRICT_NO"] + "-" + df["LEASE_NO"]
    for c in rs.VOLS:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["filed"] = (df["PROD_REPORT_FILED_FLAG"] == "Y").astype(int)
    agg = df.groupby(["lease_id", "t"]).agg(oil=("CNTY_LSE_OIL_PROD_VOL", "sum"), gas=("CNTY_LSE_GAS_PROD_VOL", "sum"),
                                            cond=("CNTY_LSE_COND_PROD_VOL", "sum"), csgd=("CNTY_LSE_CSGD_PROD_VOL", "sum"),
                                            filed=("filed", "max"))
    ids = agg.index.get_level_values(0).unique()
    L, T = len(ids), len(months)
    li = pd.Index(ids)
    rows, cols = li.get_indexer(agg.index.get_level_values(0)), agg.index.get_level_values(1).values
    out = {}
    for c in ("oil", "gas", "cond", "csgd", "filed"):
        a = np.zeros((L, T))
        a[rows, cols] = agg[c].values
        out[c] = a
    present = np.zeros((L, T), dtype=bool)
    present[rows, cols] = True
    out["present"] = present
    last = df.sort_values("t").groupby("lease_id").tail(1).set_index("lease_id")
    county = df.groupby(["lease_id", "COUNTY_NAME"]).size().reset_index().sort_values(0).groupby("lease_id").tail(1).set_index("lease_id")["COUNTY_NAME"]
    facts = pd.DataFrame({"lease_id": ids, "code": [i[0] for i in ids], "district_no": [i.split("-")[1] for i in ids],
                          "county": county.reindex(ids).str.strip().values,
                          "operator_no": last["OPERATOR_NO"].reindex(ids).values, "operator_name": last["OPERATOR_NAME"].reindex(ids).str.strip().values,
                          "lease_name": last["LEASE_NAME"].reindex(ids).str.strip().values, "field_name": last["FIELD_NAME"].reindex(ids).str.strip().values,
                          "district": last["DISTRICT_NAME"].reindex(ids).values})
    return facts, out


def lease_firsts(z):
    """(code, district, lease) -> the RRC's first month for the lease, YYYY-MM (OG_SUMMARY_ONSHORE_LEASE's
    CYCLE_YEAR_MONTH_MIN, the earliest over its rows)."""
    d = rs.read_dsv(z, "OG_SUMMARY_ONSHORE_LEASE_DATA_TABLE.dsv", usecols=["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO", "CYCLE_YEAR_MONTH_MIN"])
    g = d.groupby(["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO"])["CYCLE_YEAR_MONTH_MIN"].min()
    return g.map(lambda v: f"{v[:4]}-{v[4:6]}")


def screen(facts, a, months, wells, R, wti, hh, firsts=None):
    """The flags of a block of leases: one dict per lease and rule."""
    T = len(months)
    first = T - WINDOW
    days = np.array([days_in(m) for m in months], dtype=float)
    oil_px = np.array([wti.get(m, np.nan) for m in months])
    gas_px = np.array([hh.get(m, np.nan) for m in months])
    oil_rate, gas_rate, cond_rate = R["oil"]["rate"], R["gas"]["rate"], R["cond"]["rate"]
    out = []
    w = wells.reindex([tuple(x.split("-")) for x in facts["lease_id"]])
    n_wells = w["wells"].fillna(0).values.astype(int)
    n_open = w["wells_open"].fillna(0).values.astype(int)
    lp_oil_pct = [credit_pct(R["lp_oil"], m) for m in months]
    lp_gas_pct = [credit_pct(R["lp_gas"], m) for m in months]
    base_all = (a["oil"] * oil_px * oil_rate + a["cond"] * oil_px * cond_rate + (a["gas"] + a["csgd"]) * gas_px * gas_rate)
    for i, f in enumerate(facts.itertuples(index=False)):
        oil, gas, filed, present = a["oil"][i], a["gas"][i], a["filed"][i], a["present"][i]
        common = dict(lease_id=f.lease_id, code=f.code, district=f.district, county=f.county, operator_no=f.operator_no,
                      operator_name=f.operator_name, lease_name=f.lease_name, field_name=f.field_name, wells=int(n_wells[i]), wells_open=int(n_open[i]))
        # low-producing oil lease
        if f.code == "O":
            wn = max(int(n_open[i]), 1)
            ms, tests, base, withc, notes = [], [], 0.0, 0.0, set()
            for t in range(first, T):
                if oil[t] <= 0 or not filed[t]:
                    continue
                held = [k for k in (t - 2, t - 1, t) if k >= 0 and oil[k] > 0]
                pwd = oil[held].sum() / (days[held].sum() * wn)
                if pwd < 15:
                    pct, cp = lp_oil_pct[t]
                    b = oil[t] * oil_px[t] * oil_rate
                    ms.append(months[t])
                    tests.append(pwd)
                    base += b
                    withc += b * (1 - (pct or 0) / 100)
                    notes.add(f"no certified price in the rules file for {months[t]}: no credit" if pct is None else f"certified ${cp} for {months[t]}: {pct} percent")
            if ms:
                out.append(dict(common, rule="tx_lp_oil", months=len(ms), first=ms[0], last=ms[-1], month_list=";".join(ms),
                                test=f"{min(tests):.2f} to {max(tests):.2f} bbl per well per day over the months of the 90 days ending with each month ({wn} well{'s' if wn > 1 else ''} listed and not shut in{'; none listed, read as one' if n_open[i] == 0 else ''}), under 15",
                                base_tax=round(base, 2), tax_with=round(withc, 2), savings=round(base - withc, 2), price_note=compress(notes)))
        # low-producing gas well
        if f.code == "G":
            ms, tests, base, withc, notes = [], [], 0.0, 0.0, set()
            for t in range(first, T):
                if gas[t] <= 0 or not filed[t]:
                    continue
                prior = [k for k in (t - 3, t - 2, t - 1) if k >= 0 and filed[k]]
                use = prior or [t]
                pd_ = gas[use].sum() / days[use].sum()
                if pd_ <= 90:
                    pct, cp = lp_gas_pct[t]
                    b = gas[t] * gas_px[t] * gas_rate
                    ms.append(months[t])
                    tests.append(pd_)
                    base += b
                    withc += b * (1 - (pct or 0) / 100)
                    notes.add(f"no certified price in the rules file for {months[t]}: no credit" if pct is None else f"certified ${cp} for {months[t]}: {pct} percent")
            if ms:
                out.append(dict(common, rule="tx_lp_gas", months=len(ms), first=ms[0], last=ms[-1], month_list=";".join(ms),
                                test=f"{min(tests):.2f} to {max(tests):.2f} Mcf per day over the three months before each month (the months with a filed report), 90 or less",
                                base_tax=round(base, 2), tax_with=round(withc, 2), savings=round(base - withc, 2), price_note=compress(notes)))
        # two-year inactive: the first month in the window that produces after 24 or more months without production
        cond, csgd = a["cond"][i], a["csgd"][i]
        prod = (oil + gas + cond + csgd) > 0
        for t in range(first, T):
            if not prod[t] or not filed[t]:
                continue
            k = t - 1
            while k >= 0 and not prod[k]:
                k -= 1
            run = t - 1 - k
            if run < 24:
                break
            lf = firsts.get(tuple(f.lease_id.split("-"))) if firsts is not None else None
            prod_ms = [m for m, p in zip(months[t:], prod[t:]) if p]
            if k >= 0:
                # seen: the exempt volume each month is at most the lease's average producing month of the 12 before the gap
                pre = [j for j in range(max(0, k - 11), k + 1) if prod[j]]
                cap = {v: float(np.mean(a[v][i][pre])) for v in ("oil", "gas", "cond", "csgd")}
                ex = {v: np.minimum(a[v][i][t:], cap[v]) for v in cap}
                b = float(np.nansum(base_all[i, t:]))
                sav = float(np.nansum(ex["oil"] * oil_px[t:] * oil_rate + ex["cond"] * oil_px[t:] * cond_rate + (ex["gas"] + ex["csgd"]) * gas_px[t:] * gas_rate))
                out.append(dict(common, rule="tx_inactive", months=len(prod_ms), first=months[t], last=months[T - 1], month_list=";".join(prod_ms),
                                test=f"produced in {months[t]} after {run} months without production (last before the gap: {months[k]}), 24 or more; the saving is "
                                     f"estimated on at most its average producing month of the 12 before the gap ({', '.join(f'{v} {cap[v]:,.0f}' for v in cap if cap[v] > 0)})",
                                base_tax=round(b, 2), tax_with=round(b - sav, 2), savings=round(sav, 2), case="seen",
                                price_note="0.0 percent of market value for five years from designation, on the inactive well's volume"))
            elif lf is not None and lf <= shift(months[0], -12):
                b = float(np.nansum(base_all[i, t:]))
                out.append(dict(common, rule="tx_inactive", months=len(prod_ms), first=months[t], last=months[T - 1], month_list=";".join(prod_ms),
                                test=f"produced in {months[t]} after {run} months without production, back past the 48 months read (from {months[0]}); "
                                     f"the RRC's first month for the lease is {lf}, so it is not new; its production before {months[0]} is not read",
                                base_tax=round(b, 2), tax_with=round(b, 2), savings=0.0, case="older",
                                price_note="no saving estimated: the volume of the inactive well cannot be told from the lease's"))
            break
    return out


def compress(notes):
    """The price notes, grouped by month (24 notes a lease are long): the certified months with their credit percents,
    and the months the rules file holds no certified price for."""
    none = sorted(n.split(" for ")[1].split(":")[0] for n in notes if n.startswith("no certified"))
    got = sorted((n.split(" for ")[1].split(":")[0], n.rsplit(": ", 1)[1]) for n in notes if n.startswith("certified"))
    parts = []
    if got:
        pcts = sorted({p for _, p in got}, key=lambda x: int(x.split()[0]))
        parts.append(f"certified prices for {len(got)} month{'s' if len(got) > 1 else ''} ({got[0][0]} to {got[-1][0]}): {', '.join(pcts)}")
    if none:
        parts.append(f"no certified price in the rules file for {', '.join(none)}: no credit")
    return "; ".join(parts)


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"severance_screen_{run_id}.log"))
    results = []
    try:
        path = rs.dump_path()
        z = zipfile.ZipFile(path)
        months48, rng = rs.months_of(z, HISTORY)
        months = [f"{m[:4]}-{m[4:]}" for m in months48]
        wells = rs.wells_table(z)
        firsts = lease_firsts(z).to_dict()
        R = rules_of()
        wti, hh = prices_of()
        missing = [m for m in months[-WINDOW:] if m not in wti or m not in hh]
        if missing:
            raise RuntimeError(f"no monthly WTI or Henry Hub mean for {missing}")
        files = sorted(glob.glob(os.path.join(rs.split_dir(path), "*.dsv.gz")))
        log(f"ERW severance_screen {run_id}: {len(files)} county files, months {months[0]} to {months[-1]} (window {months[-WINDOW]} to {months[-1]}); "
            f"rules {R['version']}")
        # leases reported in more than one county: tested once, on their statewide sum
        seen = {}
        for fp in files:
            ids = pd.read_csv(fp, sep="}", dtype=str, encoding="latin-1", keep_default_na=False, compression="gzip",
                              usecols=["OIL_GAS_CODE", "DISTRICT_NO", "LEASE_NO"]).drop_duplicates()
            for x in (ids["OIL_GAS_CODE"] + "-" + ids["DISTRICT_NO"] + "-" + ids["LEASE_NO"]):
                seen[x] = seen.get(x, 0) + 1
        multi = {k for k, v in seen.items() if v > 1}
        log(f"{len(seen):,} leases in the 48 months; {len(multi):,} reported in more than one county, tested on their sum")
        flags, multi_rows, n_leases, t0 = [], [], 0, time.time()
        for fp in files:
            df = rs.county_frame(fp)
            lid = df["OIL_GAS_CODE"] + "-" + df["DISTRICT_NO"] + "-" + df["LEASE_NO"]
            mm = lid.isin(multi)
            if mm.any():
                multi_rows.append(df[mm])
            df = df[~mm]
            if not len(df):
                continue
            facts, arr = lease_arrays(df, months)
            n_leases += len(facts)
            flags += screen(facts, arr, months, wells, R, wti, hh, firsts)
        if multi_rows:
            facts, arr = lease_arrays(pd.concat(multi_rows, ignore_index=True), months)
            n_leases += len(facts)
            flags += screen(facts, arr, months, wells, R, wti, hh, firsts)
        log(f"screened {n_leases:,} leases in {time.time() - t0:.0f} s: {len(flags):,} flags")
        fl = pd.DataFrame(flags)
        fl["not_seen"] = fl["rule"].map(lambda r: " | ".join(NOT_SEEN[r]))
        fl = fl.sort_values(["savings", "lease_id"], ascending=[False, True])
        header = [
            "Energy Research Warehouse (ERW): the Texas severance refund finder, one row per lease and rule (session 57, internal)",
            f"Window: {months[-WINDOW]} to {months[-1]}, each lease's latest 24 production months in the RRC dump; the 24 before them for the inactive test.",
            "Rules: tx_lp_oil, tx_lp_gas and tx_inactive (oil Sec. 202.056(b), gas Type 16) from site/data/severance_rules.json "
            f"(version {R['version']}), each with its citation there. May qualify, never qualifies; not tax advice.",
            "Money: estimated tax at the base rate (oil and condensate 4.6 percent, gas and casinghead gas 7.5 percent of value) against the tax with "
            "the credit or exemption, at monthly means of EIA's daily spot prices (WTI Cushing per barrel; Henry Hub per MMBtu applied per Mcf), "
            "not the operator's prices.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/severance_screen.py",
            f"Run log: warehouse/output/logs/severance_screen_{run_id}.log",
            f"Source: rrc:pdq_dump RRC Production Data Query dump (PDQ_DSV.zip), {rs.SHARE}",
            "Derived from: rrc_lease_production_statewide; eia_fuel_spot_prices",
            "License: internal (the RRC grants no reuse in writing). Not in git, the public database, public Redivis or any committed JSON.",
        ]
        out = os.path.join(ip.OUT_DIR, FLAGS + ".csv.gz")
        with gzip.open(out, "wt", encoding="utf-8", newline="\n") as f:
            for h in header:
                f.write(f"# {h}\n")
            fl.to_csv(f, index=False)
        summary = summarize(fl, months, R, n_leases, len(files), rng, run_id)
        with open(os.path.join(ip.OUT_DIR, SUMMARY + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=1)
        msg = (f"{n_leases:,} leases, {len(fl):,} flags; potential savings USD {fl['savings'].sum():,.2f} "
               + "; ".join(f"{r}: {len(g):,} leases, USD {g['savings'].sum():,.2f}" for r, g in fl.groupby("rule")))
        log(msg)
        print(f"severance_screen: {msg}")
        results.append(dict(table=FLAGS, market="statewide", status="ok", detail=msg[:300]))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"severance_screen FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=FLAGS, market="statewide", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("severance_screen", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


def summarize(fl, months, R, n_leases, n_counties, rng, run_id):
    """Totals by rule, county and operator (top 50), and the largest leases, for /severance/finder."""
    def tot(g):
        return dict(leases=int(g["lease_id"].nunique()), flags=int(len(g)), months=int(g["months"].sum()),
                    base_tax=round(float(g["base_tax"].sum()), 2), savings=round(float(g["savings"].sum()), 2),
                    with_savings=int((g["savings"] > 0).sum()))
    by_rule = {r: tot(g) for r, g in fl.groupby("rule")}
    ina = fl[fl["rule"] == "tx_inactive"]
    by_case = {c: tot(g) for c, g in ina.groupby("case")} if "case" in ina else {}
    by_county = sorted(({"county": c, **tot(g)} for c, g in fl.groupby("county")), key=lambda x: (-x["savings"], -x["leases"], x["county"]))
    by_op = sorted(({"operator_no": o, "operator_name": g["operator_name"].iloc[0], **tot(g)} for o, g in fl.groupby("operator_no")),
                   key=lambda x: (-x["savings"], -x["leases"], x["operator_no"]))
    lease_tot = fl.groupby("lease_id").agg(savings=("savings", "sum"), rules=("rule", lambda s: ";".join(sorted(s))), county=("county", "first"),
                                           operator_name=("operator_name", "first"), lease_name=("lease_name", "first"), code=("code", "first"),
                                           months=("months", "max")).reset_index().sort_values(["savings", "lease_id"], ascending=[False, True])
    return dict(
        note="ERW, session 57: the Texas severance refund finder's summary (internal). May qualify, never qualifies; not tax advice.",
        built=run_id, window=[months[-WINDOW], months[-1]], history_from=months[0], rules_version=R["version"],
        dump=dict(newest=rng["NEWEST_PROD_CYCLE_YEAR_MONTH"], oil_extract=rng["OIL_EXTRACT_DATE"], gas_extract=rng["GAS_EXTRACT_DATE"]),
        leases_screened=n_leases, counties=n_counties, total=tot(fl), by_rule=by_rule, by_case=by_case, by_county=by_county, by_operator=by_op[:50],
        top_leases=lease_tot.head(100).to_dict("records"),
        cites={r: {"cite": R[k]["cite"], "source": R["sources"][R[k]["cite"]], "code": R[k].get("code")}
               for r, k in (("tx_lp_oil", "lp_oil"), ("tx_lp_gas", "lp_gas"), ("tx_inactive_oil", "inactive_oil"), ("tx_inactive_gas", "inactive_gas"))},
        not_seen=NOT_SEEN,
        prices="Monthly means of EIA's daily spot prices (eia_fuel_spot_prices): WTI Cushing per barrel for oil and condensate; Henry Hub per MMBtu, "
               "applied per Mcf as if one Mcf held one MMBtu, for gas and casinghead gas. Not the operator's prices.",
    )


def summary_only():
    """Rebuild the summary from the flags file (no screening): python severance_screen.py --summary-only"""
    z = zipfile.ZipFile(rs.dump_path())
    months48, rng = rs.months_of(z, HISTORY)
    months = [f"{m[:4]}-{m[4:]}" for m in months48]
    path = os.path.join(ip.OUT_DIR, FLAGS + ".csv.gz")
    head = [ln for ln in gzip.open(path, "rt", encoding="utf-8") if ln.startswith("#")]
    fl = pd.read_csv(path, skiprows=len(head), dtype={"operator_no": str, "district": str})
    old = json.load(open(os.path.join(ip.OUT_DIR, SUMMARY + ".json"), encoding="utf-8"))
    built = next(h.split()[2] for h in head if h.startswith("# Retrieved:"))
    summary = summarize(fl, months, rules_of(), old["leases_screened"], old["counties"], rng, built)
    with open(os.path.join(ip.OUT_DIR, SUMMARY + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1)
    print(f"summary rebuilt from {len(fl):,} flags")


if __name__ == "__main__":
    sys.exit(summary_only() if "--summary-only" in sys.argv else main())
