#!/usr/bin/env python3
"""EIA's Electric Power Annual: the capacity factors of the U.S. utility-scale fleet by energy source and technology, a
year and a month (Tables 4.8.A and 4.8.B), and the average operating heat rates of coal, petroleum, natural gas and
nuclear plants, a year (Table 8.1) (session 984, chain 055: EIA's own fleet figures beside the plant-level tables).

Energy Research Warehouse (ERW) connector. Two series tables from the Electric Power Annual's workbooks:

    https://www.eia.gov/electricity/annual/   (xls/epa_04_08_a.xlsx, epa_04_08_b.xlsx, epa_08_01.xlsx)

    eia_capacity_factors_annual    entity eia_epa_cf:<energy source>:<technology> (technology "all" where EIA gives none);
                                   variables capacity_factor (ratio) and time_adjusted_capacity (MW); ts_utc the year's 1
                                   January; freq P1Y (2015 on); geo US
    eia_capacity_factors_monthly   the same, a month (the three latest years), freq P1M
    eia_heat_rates_annual          entity eia_epa_heat_rate:<coal|petroleum|natural_gas|nuclear>; variable heat_rate; unit
                                   MMBtu/MWh (EIA's Btu per kWh over 1,000, the same figure); ts_utc the year's 1 January;
                                   freq P1Y; geo US

A heading not as read, a month not under a year, or a key given twice stops the run; a cell EIA leaves empty has no row;
nothing is filled.

    python warehouse/connectors/eia_epa_tables.py [--offline] [--table NAME]

Ceiling: three requests (the workbooks, saved in warehouse/raw/eia_electric_power_annual/ and reused offline). EIA's
robots file allows /electricity/. License: public (EIA, record 1 of license_reads.csv).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "eia_electric_power_annual"
SOURCE = "eia:electric_power_annual"
PAGE = "https://www.eia.gov/electricity/annual/"
BASE = PAGE + "xls/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CF, CFA, HR = "eia_capacity_factors_monthly", "eia_capacity_factors_annual", "eia_heat_rates_annual"
FREQ_OF = {CF: "P1M", CFA: "P1Y"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
HEAT_FUELS = {"Coal": "coal", "Petroleum": "petroleum", "Natural Gas": "natural_gas", "Nuclear": "nuclear"}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def capacity_factors(d, base):
    if text(d.iloc[2, 0]) != "Year/Month" or text(d.iloc[4, 0]) != "Annual Data":
        raise RuntimeError("capacity factors: headings not as read")
    pairs, fuel = [], ""
    for j in range(1, d.shape[1], 2):
        fuel = text(d.iloc[1, j]) or fuel
        tech = text(d.iloc[2, j]) or (text(d.iloc[2, j - 1]) if j > 1 and not text(d.iloc[1, j]) and fuel == "Solar" else "")
        if text(d.iloc[3, j]) != "Time Adjusted Capacity (MW)" or text(d.iloc[3, j + 1]) != "Capacity Factor":
            raise RuntimeError(f"capacity factors: the pair at column {j} is not as read")
        pairs.append((j, fuel, tech or "all"))
    out, year = [], None
    for i in range(5, len(d)):
        label = text(d.iloc[i, 0])
        if re.fullmatch(r"\d{4}", label) and year is None:
            ts, freq = f"{label}-01-01T00:00:00Z", "P1Y"
        elif re.fullmatch(r"Year \d{4}", label):
            year = label[5:]
            continue
        elif label in MONTHS:
            if year is None:
                raise RuntimeError(f"a month not under a year: {label}")
            ts, freq = f"{year}-{MONTHS.index(label) + 1:02d}-01T00:00:00Z", "P1M"
        else:
            break
        for j, f, tech in pairs:
            ent = f"eia_epa_cf:{slug(f)}:{slug(tech)}"
            for col, var, unit in ((j, "time_adjusted_capacity", "MW"), (j + 1, "capacity_factor", "ratio")):
                v = pd.to_numeric(d.iloc[i, col], errors="coerce")
                if pd.isna(v):
                    continue
                out.append(dict(base, entity=ent, variable=var, ts_utc=ts, value=float(v), unit=unit, freq=freq, geo="US", market="",
                                node=f"{f}, {tech}" if tech != "all" else f))
    return out


def heat_rates(d, base):
    heads = [text(v) for v in d.iloc[2].tolist()]
    if heads[0] != "Year" or heads[1:5] != list(HEAT_FUELS) or "Btu per Kilowatthour" not in text(d.iloc[1, 0]):
        raise RuntimeError(f"heat rates: headings not as read: {heads}")
    out = []
    for i in range(3, len(d)):
        y = text(d.iloc[i, 0])
        if not re.fullmatch(r"\d{4}", y.replace(".0", "")):
            break
        y = y.replace(".0", "")
        for j, (name, key) in enumerate(HEAT_FUELS.items(), start=1):
            v = pd.to_numeric(d.iloc[i, j], errors="coerce")
            if pd.isna(v):
                continue
            out.append(dict(base, entity=f"eia_epa_heat_rate:{key}", variable="heat_rate", ts_utc=f"{y}-01-01T00:00:00Z", value=float(v) / 1000,
                            unit="MMBtu/MWh", freq="P1Y", geo="US", market="", node=f"{name}, average operating heat rate"))
    return out


def common(run_id, base, urls):
    return [
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_epa_tables.py; the workbooks retrieved {base['retrieved_at']}, last modified {base['vintage']}",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        f"Source: {SOURCE} U.S. Energy Information Administration, Electric Power Annual, {PAGE}",
        f"  access: {'; '.join(urls)}",
        'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Electric Power Annual").',
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's Electric Power Annual: capacity factors and heat rates")
    ap.add_argument("--offline", action="store_true", help="the saved workbooks only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--table", choices=[CFA, CF, HR], action="append", help="the table(s) to write (default all three)")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, names = [], args.table or [CFA, CF, HR]
    for name in names:
        try:
            files = ["epa_04_08_a.xlsx", "epa_04_08_b.xlsx"] if name in FREQ_OF else ["epa_08_01.xlsx"]
            out, base = [], None
            for fn in files:
                content, rec = ip.fetch_raw(CONNECTOR, BASE + fn, log, offline=args.offline, headers=UA, timeout=120)
                base = dict(source=SOURCE, source_url=BASE + fn, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
                d = pd.read_excel(io.BytesIO(content), header=None)
                out += [r for r in capacity_factors(d, base) if r["freq"] == FREQ_OF[name]] if name in FREQ_OF else heat_rates(d, base)
            s = pd.DataFrame(out)
            if s.duplicated(["entity", "variable", "ts_utc"]).any():
                raise RuntimeError("an (entity, variable, ts_utc) given twice")
            s = s[ip.SERIES_COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
            if name in FREQ_OF:
                head = [
                    f"Energy Research Warehouse (ERW): EIA, Electric Power Annual, Tables 4.8.A and 4.8.B: capacity factors and time adjusted capacity of U.S. utility-scale generators by energy source and technology, a {'year' if name == CFA else 'month'} (session 984)",
                    "Shape: series (docs/datastandard.md v0). entity eia_epa_cf:<energy source>:<technology> ('all' where EIA gives none); variables capacity_factor "
                    "(ratio) and time_adjusted_capacity (MW: summer capacity in operation the whole month; a year's, the months' time weighted average); "
                    f"freq {FREQ_OF[name]}; geo US.",
                    f"{s.entity.nunique()} series; {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}. A cell EIA leaves empty has no row. Nothing is filled.",
                ]
            else:
                head = [
                    "Energy Research Warehouse (ERW): EIA, Electric Power Annual, Table 8.1: average operating heat rates of coal, petroleum, natural gas and nuclear plants, a year (session 984)",
                    "Shape: series (docs/datastandard.md v0). entity eia_epa_heat_rate:<coal|petroleum|natural_gas|nuclear>; variable heat_rate; unit MMBtu/MWh "
                    "(EIA's Btu per kWh over 1,000: the same figure); freq P1Y; geo US. Utility and independent power producer plants; combined heat and power and the "
                    "commercial and industrial sectors excluded, as EIA notes; nuclear the units' tested heat rate.",
                    f"Years {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}. Nothing is filled.",
                ]
            ip.write_snapshot(s, name, head + common(run_id, base, [BASE + f for f in files]), log, ip.SERIES_COLS)
            results.append(dict(table=name, market="all", status="ok", detail=f"{len(s)} rows"))
            print(f"{name}: {len(s)} rows, {s.entity.nunique()} series")
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"{name} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=name, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ok = [r["table"] for r in results if r["status"] == "ok"]
        if ok:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Electric Power Annual (Tables 4.8.A, 4.8.B and 8.1)", report_url=PAGE, document_list=BASE,
                                    license="public", tables=[CFA, CF, HR])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
