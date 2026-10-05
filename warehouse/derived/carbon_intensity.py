#!/usr/bin/env python3
"""Carbon intensity per balancing authority, hourly, daily and monthly, from EIA-930's CO2 estimates (session 32, Part
A2; session 34: from 2018, with the workbooks' own demand and net generation).

Energy Research Warehouse (ERW). Writes three derived series tables (partition column ba), method
docs/methods/emissions.md:

    carbon_intensity_hourly   per BA and hour
    carbon_intensity_daily    per BA and complete UTC day
    carbon_intensity_monthly  per BA and UTC calendar month whose every day is complete (session 34)

    intensity_generation  = co2_emissions_generated (eia930_all_emissions, tCO2) x 1000 / EIA's "Net generation" in the
                            same workbook row (MWh in the hour), kgCO2/MWh: the CO2 of the power made in the BA
    intensity_demand      = co2_emissions_consumed (eia930_all_emissions, tCO2) x 1000 / EIA's "Demand" in the same
                            workbook row, kgCO2/MWh: the CO2 of the power used in the BA, imports counted and exports
                            taken out, over its demand

Session 34: the denominators are the workbooks' own Demand and Net generation columns, read in the emissions
connector's single pass over each workbook and kept in its extract (warehouse/raw/eia930_emissions/<run_id>/
<ba>_hours.csv, the newest per BA), so intensity runs from 2018-07 like the emissions. Session 32 divided by the
warehouse's eia930_all_generation and eia930_all_demand, which keep about 30 days; that version is still computed for
the hours those tables hold, as a check, and its difference from the workbook version is logged and written in the
header. It is not written as rows.

The two differ by trade: a BA that imports power made with more CO2 than its own has a higher demand intensity than
generation intensity, and one that exports its dirtier power the reverse. An hour is written only when its numerator
and a denominator above zero are both present; the daily values are energy-weighted (the day's CO2 over the day's MWh)
over UTC days with all 24 hours; the monthly values the same over months whose every UTC day is complete.

EIA's own intensities in its workbooks (lbs/kWh) divide by positive generation and by "consumed electricity"
(generation by source plus imports minus exports); these divide by the reported net generation and demand, so they
can differ slightly. All three tables are rewritten whole each run, one BA at a time.

    python warehouse/derived/carbon_intensity.py
"""

import datetime as dt
import os
import sys
import traceback

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import caiso_join as cj  # noqa: E402  (session 82: California from the join)
import eia930_emissions as em  # noqa: E402  (FILE: the BAs; latest_extract, read_extract, extract_meta)
import impossible_hours as ih  # noqa: E402  (session 118: the one rule for impossible values)
import iso_prices as ip  # noqa: E402

METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md"
EMIS, GEN, DEM = "eia930_all_emissions", "eia930_all_generation", "eia930_all_demand"
COLS = ip.SERIES_COLS + ["ba"]
# variable -> (the CO2 variable, the extract's denominator column, the warehouse check table and variable)
PAIRS = {"intensity_generation": ("co2_emissions_generated", "net_generation_mwh", GEN, "net_generation_mw"),
         "intensity_demand": ("co2_emissions_consumed", "demand_mwh", DEM, "demand_mw")}
TABLES = ["carbon_intensity_hourly", "carbon_intensity_daily", "carbon_intensity_monthly"]


def read(name, variables, since=None):
    """entity, variable, ts_utc, value, geo, ba of a table, streamed and filtered while read."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = 0
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    cols = ["entity", "variable", "ts_utc", "value", "geo", "ba"]
    types = {c: pa.string() for c in cols}
    types["value"] = pa.float64()
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=n, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
    parts = []
    for b in reader:
        m = pc.is_in(b.column("variable"), value_set=pa.array(variables))
        if since:
            m = pc.and_(m, pc.greater_equal(b.column("ts_utc"), since))
        parts.append(pa.Table.from_batches([b]).filter(m))
    return pa.concat_tables(parts) if parts else None


def r4(v):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(float(v))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


class Out:
    """One table written a BA at a time, through a temporary file."""

    def __init__(self, name):
        self.name, self.path = name, os.path.join(ip.OUT_DIR, name + ".csv")
        self.body = self.path + ".rows.tmp"
        self.f = open(self.body, "w", encoding="utf-8", newline="")
        self.n = 0

    def add(self, df):
        df = df[COLS].sort_values(["entity", "variable", "ts_utc"])
        if df.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError(f"{self.name}: duplicate keys")
        df.to_csv(self.f, index=False, header=False, lineterminator="\n")
        self.n += len(df)

    def close(self, header, log):
        self.f.close()
        with open(self.path + ".tmp", "w", encoding="utf-8", newline="") as f:
            for h in header + [f"File holds {self.n} rows, rewritten whole by this run."]:
                f.write("# " + h + "\n")
            f.write(",".join(COLS) + "\n")
            with open(self.body, encoding="utf-8") as b:
                for line in b:
                    f.write(line)
        os.replace(self.path + ".tmp", self.path)
        os.remove(self.body)
        log(f"  wrote {self.name}.csv: {self.n} rows")
        print(f"{self.name}.csv: rows={self.n}")

    def abort(self):
        self.f.close()
        if os.path.exists(self.body):
            os.remove(self.body)


def check(emis, extracts, log):
    """Session 34: the session 32 version (the warehouse's eia930_all_generation and eia930_all_demand as the
    denominators) against the workbook version, over the hours both hold. Returns summary lines."""
    lines = []
    for var, (co2, col, table, wvar) in PAIRS.items():
        w = read(table, [wvar])
        if w is None:
            continue
        w = w.to_pandas()[["entity", "ts_utc", "value"]].rename(columns={"value": "w_mwh"})
        stats = []
        for code, x in extracts.items():
            e = emis[(emis["ba"] == code) & (emis["variable"] == co2)][["entity", "ts_utc", "value"]]
            j = e.merge(x[["ts_utc", col]], on="ts_utc").merge(w, on=["entity", "ts_utc"])
            j = j[(j[col] > 0) & (j["w_mwh"] > 0)]
            if not len(j):
                continue
            a, b = j["value"] * 1000 / j[col], j["value"] * 1000 / j["w_mwh"]
            d = (b - a).abs()
            stats.append((code, len(j), j["ts_utc"].min(), j["ts_utc"].max(), float(d.mean()), float(d.max()),
                          float((d / a.abs()).median() * 100), int((d > 0.0001).sum())))
            log(f"  check {var} {code}: {len(j)} hours {j['ts_utc'].min()}..{j['ts_utc'].max()}; |warehouse - workbook| "
                f"mean {d.mean():.4f}, max {d.max():.4f} kgCO2/MWh, median {(d / a.abs()).median() * 100:.4f}%; "
                f"hours differing by more than 0.0001: {(d > 0.0001).sum()}; denominators differ in "
                f"{(j[col] - j['w_mwh']).abs().gt(0.5).sum()} hours by more than 0.5 MWh")
        if stats:
            n = sum(s[1] for s in stats)
            lines.append(f"{var}: {n} hours in {len(stats)} BAs; mean |difference| "
                         f"{sum(s[4] * s[1] for s in stats) / n:.4f} kgCO2/MWh, largest {max(s[5] for s in stats):.4f}; "
                         f"{sum(s[7] for s in stats)} hours differ by more than 0.0001")
    return lines


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"carbon_intensity_{run_id}.log"))
    results = []
    outs = []
    try:
        # the workbooks' demand and net generation: the newest extract of every BA, or nothing is written
        extracts, used = {}, []
        for code in em.FILE:
            p = em.latest_extract(code)
            if p is None:
                raise RuntimeError(f"no extract of {code} under warehouse/raw/eia930_emissions/ (the emissions "
                                   "connector writes one per BA each run); the tables are left as they are")
            url, lm, got = em.extract_meta(p)
            # session 118: an impossible hour of demand or of net generation is a blank (docs/methods/impossible_hours.md):
            # the hour is then not written, its day is not complete and its month is not written, by this table's own rule
            log(f"  {code}:")
            extracts[code] = ih.screen_extract(em.read_extract(p)[["ts_utc", "demand_mwh", "net_generation_mwh"]], TABLES[0], log=log)
            used.append(f"{code}: {os.path.relpath(p, ROOT)} ({url}, Last-Modified {lm})")
        log("extracts: " + "; ".join(used))
        emis = read(EMIS, ["co2_emissions_generated", "co2_emissions_consumed"]).to_pandas()
        log(f"inputs: {EMIS} {len(emis)} rows of generated and consumed CO2")
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        base = dict(unit="kgCO2/MWh", market="", node="", source="erw:carbon_intensity", source_url=METHOD_URL,
                    retrieved_at=retrieved, vintage="")
        outs = [Out(t) for t in TABLES]
        hourly, daily, monthly = outs
        span = []
        for code, x in extracts.items():
            for var, (co2, col, _, _) in sorted(PAIRS.items()):  # the file sorted by entity, variable, ts_utc
                e = emis[(emis["ba"] == code) & (emis["variable"] == co2)][["entity", "ts_utc", "value", "geo", "ba"]]
                j = e.merge(x[["ts_utc", col]].rename(columns={col: "mwh"}), on="ts_utc")
                j = j[j["mwh"] > 0].rename(columns={"value": "co2"})
                if code == cj.BA and ih.applies(TABLES[0]):
                    # session 118: EIA's file holds no hydro for California for 7,869 hours in a row; its generation, its
                    # net generation and the CO2 traced through them are left out of every figure (ih.CISO_NO_HYDRO).
                    # And EIA's California hours of November 2023 to 2 December 2025 are read one hour earlier, where
                    # they belong (caiso_join.true_hours): the CO2 and its denominator sit in the same late row
                    gap = ih.in_hydro_gap(j["ts_utc"])
                    log(f"  {code} {var}: {int(gap.sum())} hours in the hydro gap not written")
                    j = j[~gap]
                    k = cj.true_hours(j.set_index(pd.to_datetime(j["ts_utc"], utc=True)))
                    j = k.assign(ts_utc=k.index.strftime("%Y-%m-%dT%H:%M:%SZ")).reset_index(drop=True)
                if code == cj.BA and var == cj.VARIABLE:
                    # session 82: from the join California's generation is CAISO's own, written by caiso_join.py --apply
                    # (the next step of the daily run); EIA's generation is never written for those hours
                    j = cj.before_join(j)
                if not len(j):
                    continue
                span += [j["ts_utc"].min(), j["ts_utc"].max()]
                hourly.add(j.assign(variable=var, freq="PT1H", value=(j["co2"] * 1000 / j["mwh"]).map(r4), **base))
                j = j.assign(day=j["ts_utc"].str[:10])
                g = j.groupby(["entity", "geo", "ba", "day"]).agg(co2=("co2", "sum"), mwh=("mwh", "sum"),
                                                                   n=("co2", "size")).reset_index()
                g = g[g["n"] == 24]
                daily.add(pd.DataFrame({"entity": g["entity"], "variable": var, "ts_utc": g["day"] + "T00:00:00Z",
                                        "value": (g["co2"] * 1000 / g["mwh"]).map(r4), "geo": g["geo"], "ba": g["ba"],
                                        "freq": "P1D", **base}))
                # a month is written only when every UTC day of it is complete
                g = g.assign(month=g["day"].str[:7])
                m = g.groupby(["entity", "geo", "ba", "month"]).agg(co2=("co2", "sum"), mwh=("mwh", "sum"),
                                                                     days=("day", "size")).reset_index()
                m = m[m["days"] == pd.to_datetime(m["month"] + "-01").dt.days_in_month]
                monthly.add(pd.DataFrame({"entity": m["entity"], "variable": var, "ts_utc": m["month"] + "-01T00:00:00Z",
                                          "value": (m["co2"] * 1000 / m["mwh"]).map(r4), "geo": m["geo"], "ba": m["ba"],
                                          "freq": "P1M", **base}))
                log(f"  {code} {var}: {len(j)} hours, {len(g)} complete days, {len(m)} complete months")
        checked = check(emis, extracts, log)
        head = lambda what: [  # noqa: E731
            f"Energy Research Warehouse (ERW): carbon intensity per balancing authority, {what} (derived, sessions 32 "
            "and 34)",
            "Shape: series (docs/datastandard.md v0), partition column ba, kgCO2/MWh. intensity_generation = EIA's CO2 "
            "emissions generated / EIA's net generation; intensity_demand = EIA's CO2 emissions consumed (generated plus "
            "imported minus exported) / EIA's demand. Daily values: the day's CO2 over the day's MWh, complete UTC days "
            "only; monthly values the same over UTC months whose every day is complete.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/carbon_intensity.py",
            f"Run log: warehouse/output/logs/carbon_intensity_{run_id}.log",
            f"Source: erw:carbon_intensity ERW derived table, emissions method (docs/methods/emissions.md), {METHOD_URL}",
            f"Derived from: {EMIS}",
        ] + ([  # session 118: said only by a build that did it (the tables are held: impossible_hours.HELD)
            "Left out (session 118, docs/methods/impossible_hours.md): an hour whose demand or net generation is impossible "
            "(not above zero, further than 25 percent from the median of the four hours around it, or outside one third to "
            "three times the grid's own median hour) is not written for the intensity that divides by it; California's "
            f"hours from {ih.CISO_NO_HYDRO[0]} to {ih.CISO_NO_HYDRO[1]} (hour starts, both included), in which EIA's file "
            "holds no hydro, are not written at all; EIA's California hours of 2023-11 to 2025-12-02 are read one hour "
            "earlier. A day short of an hour is not a complete day, and its month is not written. Nothing is filled.",
        ] if ih.applies(TABLES[0]) else []) + [
            "Denominators (session 34): the Demand and Net generation columns of the same EIA workbooks the CO2 comes from "
            "(sheet Published Hourly Data), from the emissions connector's extracts: " + "; ".join(used),
            f"Reach: {min(span)} to {max(span)}.",
            "Check against the session 32 version (the warehouse's eia930_all_generation and eia930_all_demand as "
            "denominators, the hours they hold): " + (" | ".join(checked) or "no overlapping hours"),
        ]
        for o, what in zip(outs, ["hourly", "daily", "monthly"]):
            o.close(head(what), log)
        outs = []
        ip.update_sources([{"source": "erw:carbon_intensity", "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "Carbon intensity per balancing authority (docs/methods/emissions.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": TABLES}])
        results.append(dict(table="carbon_intensity", market="derived", status="ok",
                            detail=f"hourly {hourly.n}, daily {daily.n}, monthly {monthly.n} rows; " + " | ".join(checked)
                            [:200]))
    except Exception:
        for o in outs:
            o.abort()
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"carbon_intensity FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table="carbon_intensity", market="derived", status="failed",
                            detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("carbon_intensity", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
