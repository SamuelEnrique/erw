#!/usr/bin/env python3
"""California from the join: CAISO's own supply by fuel from 16 December 2025 (session 78; Samuel's ruling on session 73).

Energy Research Warehouse (ERW). EIA-930's generation series for California changed in the hour starting
2025-12-16T08:00:00Z, midnight Pacific (docs/methods/eia930_caiso_break.md). The ruling: from that hour California's
generation, its generation mix and the generation side of its carbon figures come from CAISO's own supply by fuel
(caiso_fuel_supply); EIA-930 stays the source before it, and for interchange.

The join is one constant, JOIN. Nothing else in the ERW names the date.

What changes, for eia930:CISO, hour by hour (an hour is its start, UTC):

    net generation         before JOIN  EIA-930's
                           from JOIN    the sum of CAISO's own sources (every source of its supply but imports;
                                        batteries net), MWh
    intensity_generation   before JOIN  as EIA-930 gives it (the held rows, unchanged)
                           from JOIN    EIA's CO2 generated x 1000 / CAISO's own net generation, kgCO2/MWh

What does not change: CO2 generated stays EIA's estimate on both sides. CAISO's supply carries no emissions, and from
the join EIA's California gas series is CAISO's own: EIA's gas CO2 over CAISO's gas MWh is 0.4049 tCO2/MWh on the 6,593
hours from the join to 2026-09-30, against EIA's own factor of 0.4051 (F_GAS, below). What was wrong after the break is
the denominator: EIA's generation total runs about 9 percent below CAISO's own (its solar about 13 percent and its wind
about 21 percent below). The build checks that ratio on every run and stops if it leaves F_GAS by more than GAS_TOLERANCE:
if EIA's gas series ever parts from CAISO's again, the numerator is no longer good and a person must look.
intensity_demand (CO2 consumed over demand) keeps EIA's rows on both sides: neither its numerator (EIA's CO2 generated
plus imported less exported) nor its denominator (EIA's demand) is a generation series. The comparison of it across the
date is still not like for like, and the pages say so.

Never mixed. A period of intensity_generation is written from one source or not at all: an hour from JOIN is built on
CAISO's generation or is absent (never EIA's); the UTC day and the month that hold JOIN (2025-12-16, 2025-12) lie on
both sides and are not written; a day needs its 24 hours and a month every day, as in
warehouse/derived/carbon_intensity.py. Each row says which side it is on in its own source column:
erw:carbon_intensity before, erw:carbon_intensity_caiso from the join.

EIA's net generation by hour, for the comparison: the builders read it from the emissions connector's workbook extracts
(warehouse/raw, not in git). This module recovers it from the held tables instead, so that it runs on any machine:
net generation = CO2 generated x 1000 / intensity_generation and demand = CO2 consumed x 1000 / intensity_demand, of the
same hour (the held intensity is that quotient, rounded to four decimals; checked against eia930_all_demand and
eia930_all_generation on the hours those hold: within 0.04 MWh).

    python warehouse/derived/caiso_join.py                       # scratch build into runs/session78/ (nothing in warehouse/output)
    python warehouse/derived/caiso_join.py --out-dir runs/x      # another scratch folder
    python warehouse/derived/caiso_join.py --apply               # the live step, under the data lock: not run in session 78

Without --apply it never writes warehouse/output. --apply builds the three tables in a temporary folder, checks them
(check_joined: the same rows as the held tables everywhere but California's intensity_generation from the join, and no
row there on the wrong side), and only then replaces the three files in warehouse/output and registers the source. It is
meant to run directly after warehouse/derived/carbon_intensity.py, which must first stop writing California's
intensity_generation from JOIN (before_join, one line there), so that a day on which this step fails leaves those rows
absent, never EIA's. Making the correction live is a listed step (archive/sessions/SESSION_78_REPORT.md, "To finish").
"""

import argparse
import csv
import io
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_DIR = os.path.join(ROOT, "warehouse", "output")

JOIN = "2025-12-16T08:00:00Z"  # the one constant: the first hour that is CAISO's own (midnight Pacific, 16 December 2025)
JOIN_DAY, JOIN_MONTH = JOIN[:10], JOIN[:7]  # the UTC day and month that lie on both sides, and are not written

ENTITY, BA, GEO = "eia930:CISO", "ciso", "US-CA"
VARIABLE = "intensity_generation"  # the one variable of the carbon tables that changes
SOURCE_EIA = "erw:carbon_intensity"
SOURCE_JOIN = "erw:carbon_intensity_caiso"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia930_caiso_break.md"
SUPPLY = "caiso_fuel_supply"
# CAISO's own sources: every source of its supply but imports. Batteries are net (negative when charging), as EIA's
# net generation counts storage.
OWN = ["batteries_mw", "biogas_mw", "biomass_mw", "coal_mw", "geothermal_mw", "large_hydro_mw", "natural_gas_mw",
       "nuclear_mw", "other_mw", "small_hydro_mw", "solar_mw", "wind_mw"]
ALL = OWN + ["imports_mw"]
# EIA's emission factor for natural gas in California, tCO2 per MWh: EIA's gas CO2 (eia930_all_emissions) over EIA's gas
# generation (eia930_all_generation), eia930:CISO, summed over the 864 hours both tables held on 2026-10-03
# (2026-08-26T00:00:00Z to 2026-09-30T23:00:00Z). Hour by hour it runs 0.4026 to 0.4079 (EIA's MWh are whole numbers).
# Used only as the check that EIA's gas is still CAISO's gas from the join (gas_ratio).
F_GAS = 0.4051
GAS_TOLERANCE = 0.02  # the share by which EIA's gas CO2 over CAISO's gas MWh may leave F_GAS before the build stops
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "ba"]
TABLES = {"carbon_intensity_hourly": "PT1H", "carbon_intensity_daily": "P1D", "carbon_intensity_monthly": "P1M"}


def r4(v):
    return float(Decimal(repr(float(v))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def header_lines(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            out.append(ln.rstrip("\n"))
    return out


def read_entity(name, entity, in_dir=OUT_DIR):
    """variable, ts_utc, value of one entity of a series table, streamed (the hourly tables hold millions of rows)."""
    path = os.path.join(in_dir, name + ".csv")
    cols = ["entity", "variable", "ts_utc", "value"]
    types = {c: pa.string() for c in cols}
    types["value"] = pa.float64()
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=len(header_lines(path)), block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
    parts = [pa.Table.from_batches([b]).filter(pc.equal(b.column("entity"), entity)) for b in reader]
    return pa.concat_tables(parts).to_pandas()[["variable", "ts_utc", "value"]]


def caiso_hours(in_dir=OUT_DIR):
    """CAISO's own supply by hour (index ts_utc): each source's MW and net_generation_mwh. Only hours that hold all
    thirteen sources: an hour short of one is absent, never filled."""
    f = pd.read_csv(os.path.join(in_dir, SUPPLY + ".csv"), comment="#", usecols=["entity", "variable", "ts_utc", "value"])
    if set(f["entity"]) != {"caiso:ISO"}:
        raise RuntimeError(f"{SUPPLY}: entities {sorted(set(f['entity']))}, expected caiso:ISO alone")
    w = f.pivot(index="ts_utc", columns="variable", values="value")
    missing = [c for c in ALL if c not in w]
    if missing:
        raise RuntimeError(f"{SUPPLY}: no {missing}")
    w = w.dropna(subset=ALL)
    w["net_generation_mwh"] = w[OWN].sum(axis=1)
    return w


def eia_hours(in_dir=OUT_DIR):
    """EIA-930's California hours (index ts_utc): CO2 generated, consumed and from natural gas (tCO2), the held
    intensities, and the demand and net generation they imply (see the module's note)."""
    e = read_entity("eia930_all_emissions", ENTITY, in_dir).pivot(index="ts_utc", columns="variable", values="value")
    c = read_entity("carbon_intensity_hourly", ENTITY, in_dir).pivot(index="ts_utc", columns="variable", values="value")
    x = e[["co2_emissions_generated", "co2_emissions_consumed", "co2_emissions_natural_gas"]].join(c, how="left")
    x["demand_mwh"] = x["co2_emissions_consumed"] * 1000 / x["intensity_demand"]
    x["net_generation_mwh"] = x["co2_emissions_generated"] * 1000 / x["intensity_generation"]
    return x


def gas_ratio(eia, caiso):
    """EIA's gas CO2 over CAISO's own gas MWh, summed over the hours from JOIN that hold both, and the hours counted.
    While EIA's California gas series is CAISO's own, this is EIA's emission factor (F_GAS)."""
    j = pd.concat([eia["co2_emissions_natural_gas"], caiso["natural_gas_mw"]], axis=1, join="inner").dropna()
    j = j[j.index >= JOIN]
    if not len(j) or j["natural_gas_mw"].sum() <= 0:
        return None, 0
    return float(j["co2_emissions_natural_gas"].sum() / j["natural_gas_mw"].sum()), len(j)


def joined(eia, caiso):
    """California by hour across the join (index ts_utc): co2_generated (EIA's on both sides), net_generation_mwh and
    side ("eia930" or "caiso"). Before JOIN every row is EIA's; from JOIN the generation is CAISO's own, and an hour
    CAISO does not hold is absent."""
    pre = eia[eia.index < JOIN]
    a = pd.DataFrame({"co2_generated": pre["co2_emissions_generated"], "net_generation_mwh": pre["net_generation_mwh"],
                      "side": "eia930"})
    post = caiso[caiso.index >= JOIN]
    b = pd.DataFrame({"co2_generated": eia["co2_emissions_generated"].reindex(post.index),
                      "net_generation_mwh": post["net_generation_mwh"], "side": "caiso"})
    return pd.concat([a, b]).sort_index()


def period_side(ts, freq):
    """Which side of JOIN a period lies on: "before", "after", or "both" (it holds JOIN and is not written)."""
    if freq == "PT1H":
        return "before" if ts < JOIN else "after"
    key, held = (ts[:10], JOIN_DAY) if freq == "P1D" else (ts[:7], JOIN_MONTH)
    return "both" if key == held else "before" if key < held else "after"


def intensity_rows(j, retrieved):
    """California's intensity_generation rows from the join, for the three tables: {table: DataFrame}. As the builder:
    hourly where the CO2 and a generation above zero are held; daily over UTC days with all 24 hours; monthly over
    months whose every UTC day is complete. The day and the month that hold JOIN are left out."""
    post = j[j["side"] == "caiso"]
    base = dict(entity=ENTITY, variable=VARIABLE, unit="kgCO2/MWh", geo=GEO, market="", node="", source=SOURCE_JOIN,
                source_url=METHOD_URL, retrieved_at=retrieved, vintage="", ba=BA)
    h = post[["co2_generated", "net_generation_mwh"]].dropna()
    h = h[h["net_generation_mwh"] > 0].rename(columns={"co2_generated": "co2", "net_generation_mwh": "mwh"})
    d = h.assign(day=h.index.str[:10]).groupby("day").agg(co2=("co2", "sum"), mwh=("mwh", "sum"), n=("co2", "size"))
    d = d[(d["n"] == 24) & (d.index != JOIN_DAY)]
    m = d.assign(month=d.index.str[:7]).groupby("month").agg(co2=("co2", "sum"), mwh=("mwh", "sum"), days=("n", "size"))
    m = m[(m["days"].values == pd.to_datetime(m.index + "-01").days_in_month.values) & (m.index != JOIN_MONTH)]

    def frame(x, freq, ts):
        return pd.DataFrame(dict(base, freq=freq, ts_utc=list(ts), value=[r4(v) for v in x["co2"] * 1000 / x["mwh"]]))[COLS]
    return {"carbon_intensity_hourly": frame(h, "PT1H", h.index),
            "carbon_intensity_daily": frame(d, "P1D", d.index + "T00:00:00Z"),
            "carbon_intensity_monthly": frame(m, "P1M", m.index + "-01T00:00:00Z")}


def splice(name, new, in_dir, out_dir, note):
    """The held table with California's intensity_generation from the join replaced: every line of another balancing
    authority, of California's other variable, and of California before the join is copied as it stands; California's
    intensity_generation lines from the join (and of the day and month that hold it) are dropped; the new rows take
    their place, in the file's order. Returns counts."""
    freq = TABLES[name]
    src, dst = os.path.join(in_dir, name + ".csv"), os.path.join(out_dir, name + ".csv")
    head = header_lines(src)
    kept = dropped = 0
    written = in_block = False
    prefix = f"{ENTITY},{VARIABLE},"

    def emit(f):
        nonlocal written
        if written:
            return
        written = True
        buf = io.StringIO()
        new.to_csv(buf, index=False, header=False, lineterminator="\n")
        f.write(buf.getvalue())

    with open(src, encoding="utf-8", newline="") as fin, open(dst + ".tmp", "w", encoding="utf-8", newline="") as f:
        for ln in fin:
            if ln.startswith("#"):
                continue
            if ln.startswith("entity,"):
                if ln.strip().split(",") != COLS:
                    raise RuntimeError(f"{name}: columns {ln.strip()} are not the carbon tables' columns")
                for h in head:
                    f.write(h + "\n")
                for h in note:
                    f.write("# " + h + "\n")
                f.write(ln if ln.endswith("\n") else ln + "\n")
                continue
            if not ln.startswith(prefix):
                if in_block:
                    emit(f)  # California's block has ended: the new rows go at its end if no held line was from the join
                f.write(ln)
                kept += 1
                continue
            in_block = True
            ts = next(csv.reader([ln]))[2]
            if period_side(ts, freq) == "before":
                f.write(ln)
                kept += 1
            else:
                emit(f)
                dropped += 1
        emit(f)
    os.replace(dst + ".tmp", dst)
    return dict(table=name, kept=kept, dropped=dropped, added=len(new), rows=kept + len(new))


def before_join(j):
    """The rows of an hourly frame (column ts_utc) that lie before JOIN. For warehouse/derived/carbon_intensity.py: applied
    to California's intensity_generation, it keeps EIA's generation out of every period from the join (the day and the
    month that hold JOIN then fall short of their hours and are not written, by that builder's own rule)."""
    return j[j["ts_utc"] < JOIN]


def check_joined(in_dir, out_dir):
    """The joined tables against the held ones: the list of what is wrong (empty when nothing is). Every row that is not
    California's intensity_generation must be the held table's, unchanged; California's intensity_generation must carry
    SOURCE_EIA before JOIN and SOURCE_JOIN from it, and hold no period that contains JOIN."""
    bad = []
    for name, freq in TABLES.items():
        a = pd.read_csv(os.path.join(in_dir, name + ".csv"), comment="#", dtype=str, keep_default_na=False)
        b = pd.read_csv(os.path.join(out_dir, name + ".csv"), comment="#", dtype=str, keep_default_na=False)
        ours = lambda d: (d["entity"] == ENTITY) & (d["variable"] == VARIABLE)  # noqa: E731
        ra, rb = a[~ours(a)].reset_index(drop=True), b[~ours(b)].reset_index(drop=True)
        if not ra.equals(rb):
            bad.append(f"{name}: rows other than California's {VARIABLE} differ from the held table")
        ca, cb = a[ours(a)], b[ours(b)]
        side = cb["ts_utc"].map(lambda ts: period_side(ts, freq))
        if (side == "both").any():
            bad.append(f"{name}: {int((side == 'both').sum())} rows in a period that holds the join")
        if set(cb.loc[side == "before", "source"]) - {SOURCE_EIA}:
            bad.append(f"{name}: a row before the join does not carry {SOURCE_EIA}")
        if set(cb.loc[side == "after", "source"]) - {SOURCE_JOIN}:
            bad.append(f"{name}: a row from the join does not carry {SOURCE_JOIN}")
        pre_a = ca[ca["ts_utc"].map(lambda ts: period_side(ts, freq)) == "before"].reset_index(drop=True)
        if not pre_a.equals(cb[side == "before"].reset_index(drop=True)):
            bad.append(f"{name}: California's {VARIABLE} before the join differs from the held table")
        if cb.duplicated(["entity", "variable", "ts_utc"]).any():
            bad.append(f"{name}: duplicate keys")
    return bad


def apply(log=print):
    """The live step: the joined tables replace the three carbon tables in warehouse/output. Under the data lock; built
    and checked in a temporary folder first, so a failure leaves warehouse/output as it was."""
    import shutil
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    import iso_prices as ip
    import lock
    lock.require(os.path.join(OUT_DIR, "carbon_intensity_hourly.csv"), "caiso_join --apply")
    tmp = tempfile.mkdtemp(prefix="erw-caiso-join-")
    try:
        _, counts, ratio, n = build(OUT_DIR, tmp, log)
        bad = check_joined(OUT_DIR, tmp)
        if bad:
            raise RuntimeError("the joined tables failed their check, nothing replaced: " + "; ".join(bad))
        for name in TABLES:
            os.replace(os.path.join(tmp, name + ".csv"), os.path.join(OUT_DIR, name + ".csv"))
        ip.update_sources([{"source": SOURCE_JOIN, "publisher": "Energy Research Warehouse (ERW), derived",
                            "report": "California's carbon intensity of generation from the join of 16 December 2025 "
                                      "(docs/methods/eia930_caiso_break.md)",
                            "report_url": METHOD_URL, "document_list": "", "license": "public", "tables": list(TABLES)}])
        log(f"caiso_join: applied to {', '.join(TABLES)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


def build(in_dir=OUT_DIR, out_dir=None, log=print):
    """The three carbon tables with California joined, written to out_dir (a scratch folder). Returns (the joined hours,
    the per-table counts, the gas ratio and its hours)."""
    if out_dir is None:
        raise RuntimeError("caiso_join.build needs an out_dir; it does not write warehouse/output")
    if os.path.abspath(out_dir) == os.path.abspath(OUT_DIR):
        raise RuntimeError("caiso_join.build is a scratch build: out_dir may not be warehouse/output")
    os.makedirs(out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    retrieved = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    caiso, eia = caiso_hours(in_dir), eia_hours(in_dir)
    ratio, n = gas_ratio(eia, caiso)
    if ratio is None or abs(ratio / F_GAS - 1) > GAS_TOLERANCE:
        raise RuntimeError(f"EIA's gas CO2 over CAISO's gas MWh from the join is {ratio} over {n} hours, not within "
                           f"{GAS_TOLERANCE:.0%} of EIA's factor {F_GAS}: EIA's California gas is no longer CAISO's own, "
                           "so EIA's CO2 generated cannot be set over CAISO's generation; nothing written")
    log(f"gas check: EIA's gas CO2 over CAISO's own gas MWh from the join = {ratio:.4f} tCO2/MWh over {n:,} hours "
        f"(EIA's factor {F_GAS})")
    j = joined(eia, caiso)
    rows = intensity_rows(j, retrieved)
    post = j[(j["side"] == "caiso") & j["co2_generated"].notna()]
    note = [
        f"California from the join (session 78; built {run_id}): from {JOIN} (JOIN, "
        f"warehouse/derived/caiso_join.py) the {VARIABLE} rows of {ENTITY} carry source {SOURCE_JOIN}: EIA's CO2 generated "
        f"over CAISO's own net generation ({SUPPLY}: every source of its supply but imports, batteries net). EIA's CO2 "
        f"generated stays the numerator: from the join EIA's California gas series is CAISO's own (EIA's gas CO2 over CAISO's "
        f"gas MWh {ratio:.4f} tCO2/MWh over {n:,} hours, EIA's factor {F_GAS}). Before the join, intensity_demand on both "
        "sides, and every other balancing authority: EIA-930, the held rows as they stand. The UTC day "
        f"{JOIN_DAY} and the month {JOIN_MONTH} hold the join and are not written for California's {VARIABLE}; an hour, day or "
        "month CAISO's supply does not hold completely is not written and never taken from EIA.",
        f"Join method: docs/methods/eia930_caiso_break.md, {METHOD_URL}",
        f"Also derived from: {SUPPLY} ({len(post):,} hours from the join, {post.index.min()} to {post.index.max()})",
    ]
    counts = []
    for name in TABLES:
        c = splice(name, rows[name], in_dir, out_dir, note)
        counts.append(c)
        log(f"{name}: {c['rows']:,} rows ({c['kept']:,} copied, {c['dropped']:,} of California's {VARIABLE} from the join "
            f"dropped, {c['added']:,} written on CAISO's generation) -> "
            f"{os.path.relpath(os.path.join(out_dir, name + '.csv'), ROOT)}")
    return j, counts, ratio, n


def main(argv=None):
    ap = argparse.ArgumentParser(description="California from the join, a scratch build (session 78)")
    ap.add_argument("--in-dir", default=OUT_DIR)
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "runs", "session78"))
    ap.add_argument("--apply", action="store_true", help="replace the three tables in warehouse/output (the data lock)")
    a = ap.parse_args(argv)
    if a.apply:
        return apply()
    build(a.in_dir, a.out_dir)
    bad = check_joined(a.in_dir, a.out_dir)
    for b in bad:
        print("CHECK FAILED: " + b, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
