#!/usr/bin/env python3
"""DOE's Low-Income Energy Affordability Data (the LEAD Tool, 2022 update): households' energy burden, energy cost and
income by income bracket, a state's counties at a time (session 2140, chain 090).

Energy Research Warehouse (ERW) connector, in two steps:

    --pull    each state's zip from the Open Energy Data Initiative's submission 6219 streamed to disk under
              warehouse/raw/doe_lead/files/ (never held whole in memory), with a manifest; a zip already in the manifest
              is not asked again
    --write   the table built from the saved zips only, each state's AMI Counties CSV read in chunks and summed to the
              county and income bracket

    doe_lead_energy_burden   entity doe_lead:<county FIPS> or doe_lead:<state>; variable <measure>:ami_<bracket>;
                             measures households (count), income_avg, electricity_cost_avg, gas_cost_avg,
                             other_fuel_cost_avg, energy_cost_avg (USD a year) and energy_burden (pct, the cost averages
                             over the income average, computed here); brackets 0_30, 30_60, 60_80, 80_100, 100_150 and
                             150_up percent of area median income, and all; ts_utc 1 January of the year the files name

The census tract files and the FPL, SMI and LLSI files are not taken (the county AMI cells are the same households,
in the brackets the LEAD Tool shows first). A zip without one AMI Counties file, a row of another state, a bracket not
one of the six, two state codes, files naming two years or a county, bracket and measure given twice stops the write.
A state whose zip is not saved is left out and named in the header. Nothing is filled.

Source: https://data.openei.org/submissions/6219 (U.S. Department of Energy, Office of State and Community Energy
Programs, "Low-Income Energy Affordability Data - LEAD Tool - 2022 Update"), files at
https://data.openei.org/files/6219/<ST>-2022-LEAD-data.zip, 52 of them (the states, DC and Puerto Rico).

Ceiling: at most 60 requests a pull, 2 seconds apart, no retry. data.openei.org has no robots file. License: public (CC BY
4.0, the submission's license, read 261).
"""

import argparse
import csv
import datetime as dt
import hashlib
import os
import re
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "doe_lead"
SOURCE = "doe:lead_2022"
PAGE = "https://data.openei.org/submissions/6219"
FILE = "https://data.openei.org/files/6219/{st}-2022-LEAD-data.zip"
TABLE = "doe_lead_energy_burden"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
STATES = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME",
          "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN",
          "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
MAX_REQUESTS = 60
PAUSE = 2.0
CHUNK = 1 << 20
MANIFEST_COLS = ["state", "url", "file", "retrieved_at", "status", "bytes", "sha256", "last_modified"]
SUMS = ["UNITS", "HINCP*UNITS", "HINCP UNITS", "ELEP*UNITS", "ELEP UNITS", "GASP*UNITS", "GASP UNITS", "FULP*UNITS", "FULP UNITS"]
COLS = ["ABV", "STATE", "FIP", "NAME", "AMI150"] + SUMS
BRACKETS = {"0-30%": "0_30", "30-60%": "30_60", "60-80%": "60_80", "80-100%": "80_100", "100-150%": "100_150", "150%+": "150_up"}
VARS = [("households", "count"), ("income_avg", "USD"), ("electricity_cost_avg", "USD"), ("gas_cost_avg", "USD"),
        ("other_fuel_cost_avg", "USD"), ("energy_cost_avg", "USD"), ("energy_burden", "pct")]
X_COLS = ["x_level", "x_bracket", "x_fips", "x_file"]


def files_dir():
    return os.path.join(ip.RAW_DIR, CONNECTOR, "files")


def manifest_path():
    return os.path.join(files_dir(), "manifest.csv")


def read_manifest():
    p = manifest_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pull(states, log):
    """Each state's zip not yet saved, streamed to a .part file and renamed when whole; the manifest row written after."""
    os.makedirs(files_dir(), exist_ok=True)
    have = {r["state"] for r in read_manifest() if r["status"] == "200"}
    asked = 0
    for st in states:
        if st in have:
            continue
        if asked >= MAX_REQUESTS:
            log(f"the ceiling of {MAX_REQUESTS} requests reached; {st} and after not asked")
            break
        url = FILE.format(st=st)
        if ip.paused_host("data.openei.org"):
            raise RuntimeError("data.openei.org is paused")
        if asked:
            time.sleep(PAUSE)
        asked += 1
        name = f"{st}-2022-LEAD-data.zip"
        part = os.path.join(files_dir(), name + ".part")
        at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        h, n = hashlib.sha256(), 0
        with requests.get(url, headers=UA, timeout=120, stream=True) as r:
            if r.status_code != 200:
                log(f"{st}: HTTP {r.status_code}, not saved")
                row = dict(state=st, url=url, file="", retrieved_at=at, status=str(r.status_code), bytes="0", sha256="", last_modified="")
            else:
                with open(part, "wb") as f:
                    for b in r.iter_content(CHUNK):
                        f.write(b)
                        h.update(b)
                        n += len(b)
                want = r.headers.get("Content-Length")
                if want and int(want) != n:
                    os.remove(part)
                    raise RuntimeError(f"{st}: {n} bytes of {want}; not saved")
                os.replace(part, os.path.join(files_dir(), name))
                row = dict(state=st, url=url, file=name, retrieved_at=at, status="200", bytes=str(n), sha256=h.hexdigest(),
                           last_modified=r.headers.get("Last-Modified", ""))
                log(f"{st}: {n:,} bytes saved")
        new = not os.path.exists(manifest_path())
        with open(manifest_path(), "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=MANIFEST_COLS, lineterminator="\n")
            if new:
                w.writeheader()
            w.writerow(row)
        print(f"{st}: {row['status']} {int(row['bytes']):,} bytes", flush=True)
    return asked


def county_cells(path, st):
    """The zip's AMI Counties CSV, read in chunks, summed to (county, bracket): households and each sum and its count."""
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if re.fullmatch(rf"{st} AMI Counties \d{{4}}\.csv", n)]
        if len(names) != 1:
            raise RuntimeError(f"{st}: the zip holds {len(names)} AMI Counties files: {z.namelist()}")
        year = int(re.search(r"(\d{4})\.csv$", names[0]).group(1))
        parts, fips = [], set()
        with z.open(names[0]) as f:
            for c in pd.read_csv(f, usecols=COLS, dtype={"FIP": str, "STATE": str, "ABV": str, "NAME": str, "AMI150": str}, chunksize=200_000):
                if (c.ABV != st).any():
                    raise RuntimeError(f"{st}: a row of another state: {c.ABV[c.ABV != st].iloc[0]!r}")
                bad = set(c.AMI150) - set(BRACKETS)
                if bad:
                    raise RuntimeError(f"{st}: a bracket not one of the six: {sorted(bad)}")
                fips |= set(c.STATE)
                parts.append(c.groupby(["FIP", "NAME", "AMI150"], as_index=False)[SUMS].sum())
    g = pd.concat(parts).groupby(["FIP", "NAME", "AMI150"], as_index=False)[SUMS].sum()
    if len(fips) != 1:
        raise RuntimeError(f"{st}: more than one state code: {sorted(fips)}")
    return g, year, names[0], fips.pop()


def measures(g):
    """Households, average income and costs (USD a year) and the energy burden (pct, the costs' averages over the
    income's average) of grouped sums."""
    out = pd.DataFrame(index=g.index)
    out["households"] = g["UNITS"]
    out["income_avg"] = g["HINCP*UNITS"] / g["HINCP UNITS"]
    for k, v in (("ELEP", "electricity_cost_avg"), ("GASP", "gas_cost_avg"), ("FULP", "other_fuel_cost_avg")):
        out[v] = g[f"{k}*UNITS"] / g[f"{k} UNITS"]
    out["energy_cost_avg"] = out.electricity_cost_avg + out.gas_cost_avg + out.other_fuel_cost_avg
    out["energy_burden"] = out.energy_cost_avg / out.income_avg * 100
    return out


def write(states, log, run_id):
    man = {r["state"]: r for r in read_manifest() if r["status"] == "200"}
    rows, done, missing, years = [], [], [st for st in states if st not in man], set()
    for st in states:
        if st not in man:
            continue
        r = man[st]
        g, year, inner, st_fips = county_cells(os.path.join(files_dir(), r["file"]), st)
        years.add(year)
        base = dict(source=SOURCE, source_url=r["url"], retrieved_at=r["retrieved_at"], vintage=r["retrieved_at"])
        cty = g.copy()
        allb = g.groupby(["FIP", "NAME"], as_index=False)[SUMS].sum().assign(AMI150="all")
        state = pd.concat([g.groupby("AMI150", as_index=False)[SUMS].sum(),
                           pd.DataFrame([g[SUMS].sum()]).assign(AMI150="all")], ignore_index=True)
        state["FIP"], state["NAME"] = st_fips, st
        for frame, level in ((pd.concat([cty, allb], ignore_index=True), "county"), (state, "state")):
            m = measures(frame)
            for i, f in frame.iterrows():
                ent = f"doe_lead:{st}" if level == "state" else f"doe_lead:{f.FIP}"
                for var, unit in VARS:
                    v = m.at[i, var]
                    if pd.isna(v) or v in (float("inf"), float("-inf")):
                        continue  # a cell with no households reporting it: no row
                    rows.append(dict(entity=ent, variable=f"{var}:ami_{BRACKETS.get(f.AMI150, 'all')}", ts_utc=f"{year}-01-01T00:00:00Z",
                                     value=round(float(v), 4), unit=unit, freq="P1Y", geo=f"US-{st}", market="", node=f.NAME, **base,
                                     x_level=level, x_bracket=f.AMI150, x_fips=f.FIP, x_file=inner))
        done.append(st)
        log(f"{st}: {len(g)} county-bracket cells from {inner}")
        print(f"{st}: {len(g)} cells", flush=True)
    if not rows:
        raise RuntimeError("no state's zip saved")
    if len(years) != 1:
        raise RuntimeError(f"the files name more than one year: {sorted(years)}")
    s = pd.DataFrame(rows)
    if s.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a county, bracket and measure given twice")
    cols = ip.SERIES_COLS + X_COLS
    s = s[cols].sort_values(["entity", "variable"]).reset_index(drop=True)
    stt = s[(s.x_level == "state") & (s.variable == "energy_burden:ami_all")]
    us_h = s[(s.x_level == "state") & (s.variable == "households:ami_all")].value.sum()
    head = [
        "Energy Research Warehouse (ERW): U.S. Department of Energy, Low-Income Energy Affordability Data (LEAD Tool), 2022 update: households, "
        "their average income and energy costs, and their energy burden, by county and state and by income as a share of area median income (session 2140)",
        "Shape: series (docs/datastandard.md v0). entity doe_lead:<county FIPS> or doe_lead:<state>; variable <measure>:ami_<bracket> (brackets "
        "0_30, 30_60, 60_80, 80_100, 100_150, 150_up percent of area median income, and all); measures households (count, LEAD's UNITS), income_avg, "
        "electricity_cost_avg, gas_cost_avg, other_fuel_cost_avg, energy_cost_avg (USD a year), energy_burden (pct). ts_utc 1 January of the year the "
        "file names; freq P1Y; x_level county or state; x_bracket as LEAD writes it; x_fips; x_file the CSV read.",
        "Method: each state's AMI Counties file, LEAD's cells (county by bracket by tenure, building age, building type and heating fuel), summed "
        "to the county and bracket: households the sum of UNITS; each average a sum of LEAD's value-times-units over the sum of its units; "
        "energy_cost_avg the three averages added; energy_burden energy_cost_avg over income_avg times 100 (computed by the ERW, as the LEAD Tool "
        "computes a group's burden from its averages). The census tract files and the FPL, SMI and LLSI files are not taken.",
        f"{len(s)} rows: {len(done)} states and territories ({', '.join(done)}); not held: {', '.join(missing) if missing else 'none'}. "
        f"{us_h:,.0f} households in the states held; the state burden for all households from {stt.value.min():.2f} to {stt.value.max():.2f} pct. "
        "A cell with no households reporting it has no row. Nothing is filled.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/doe_lead.py --write, from the zips in warehouse/raw/{CONNECTOR}/files/ (manifest.csv: each "
        "zip's address, retrieval time and sha256)",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Source: {SOURCE} DOE, LEAD Tool 2022 Update, {PAGE}",
        f"  access: {FILE.format(st='<ST>')}",
        'License: public (CC BY 4.0, the submission\'s license; cite "U.S. Department of Energy, Low-Income Energy Affordability Data (LEAD) Tool").',
    ]
    ip.write_snapshot(s, TABLE, head, log, cols)
    return len(s), done


def main(argv=None):
    ap = argparse.ArgumentParser(description="DOE's LEAD Tool, 2022 update")
    ap.add_argument("--pull", action="store_true", help="stream the state zips not yet saved")
    ap.add_argument("--write", action="store_true", help="build the table from the saved zips")
    ap.add_argument("--states", help="comma-separated two-letter codes (default: all 52)")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    states = [s.strip().upper() for s in args.states.split(",")] if args.states else STATES
    if args.pull and (ip.paused(CONNECTOR) or ip.paused_host("data.openei.org")):
        print(f"{TABLE}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results = []
    try:
        if args.pull:
            n = pull(states, log)
            print(f"{TABLE}: {n} requests")
        if args.write:
            n, done = write(states, log, run_id)
            results.append(dict(table=TABLE, market="all", status="ok", detail=f"{n} rows, {len(done)} states"))
            print(f"{TABLE}: {n} rows, {len(done)} states")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if args.write and not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Low-Income Energy Affordability Data (LEAD Tool), 2022 Update", report_url=PAGE,
                                    document_list=FILE.format(st="<ST>"), license="public", tables=[TABLE])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
