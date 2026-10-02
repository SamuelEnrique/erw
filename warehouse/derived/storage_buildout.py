#!/usr/bin/env python3
"""How much battery storage has been built, by grid and month, of what duration, against solar: from EIA-860M.

Energy Research Warehouse (ERW), session 69 (the storage build-out tracker, the site's /storage/buildout). No pull:
reads the three EIA-860M tables the ERW holds (eia860m_operating_generators, eia860m_planned_generators,
eia860m_retired_generators) and writes, through the merge writer, one derived `series` table:

    storage_buildout_monthly   freq P1M; entity iso:<caiso|ercot|isone|miso|nyiso|pjm|spp>, us:outside_isos, us:total

    python warehouse/derived/storage_buildout.py                                   # warehouse/output (the data lock)
    python warehouse/derived/storage_buildout.py --inputs-dir D --out-dir S        # a trial run: nothing in warehouse/output

Method: docs/methods/storage_buildout.md. In short:

- A battery is a generator with prime mover BA; solar is EIA's solar technologies (photovoltaic and solar thermal),
  utility scale by the form's own floor (plants of 1 MW and above).
- The grid of a generator is its balancing authority code in EIA-860M where that is one of the seven ISOs (CISO, ERCO,
  ISNE, MISO, NYIS, PJM, SWPP); every other code, and no code, is us:outside_isos. us:total is every generator, so it
  equals the seven grids plus us:outside_isos.
- Operating in a month: the unit's first operating month is that month or earlier, and it has not retired by it. The
  history is rebuilt from the one inventory held (its newest month), not from past inventories: a unit retired before
  the retired table's window (the vintage year and the year before) is absent from every month.
- Duration of a unit: its Nameplate Energy Capacity (MWh) over its nameplate MW, in the buckets lt2h (under 2 hours),
  2to4h (2 to under 4), 4to6h (4 to under 6), ge6h (6 and more). A unit EIA gives no energy for is in
  energy_not_reported and in no duration bucket; its MWh is never estimated from its MW.
- Planned: battery units of the planned table, as of the inventory month, in total and by the year of EIA's planned
  operation date. EIA's Planned sheet has no energy column, so no planned MWh is written.
"""

import argparse
import datetime as dt
import os
import sys
import traceback
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "storage_buildout_monthly"
SOURCE = "erw:storage_buildout"
METHOD = "docs/methods/storage_buildout.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/storage_buildout.md"
REGISTRY = os.path.join(ROOT, "warehouse", "metadata", "sources.csv")
INPUTS = {"operating": "eia860m_operating_generators", "planned": "eia860m_planned_generators",
          "retired": "eia860m_retired_generators"}
ISO_OF_BA = {"CISO": "caiso", "ERCO": "ercot", "ISNE": "isone", "MISO": "miso", "NYIS": "nyiso", "PJM": "pjm",
             "SWPP": "spp"}
OUTSIDE, TOTAL = "us:outside_isos", "us:total"
REGIONS = [f"iso:{v}" for v in ISO_OF_BA.values()] + [OUTSIDE]
ENTITIES = REGIONS + [TOTAL]
START = "2015-01"  # the first month written; units operating before it are in every month's total
BUCKETS = ["lt2h", "2to4h", "4to6h", "ge6h"]
NOT_REPORTED = "energy_not_reported"
SCALE = 10_000  # MW and MWh are summed as whole ten-thousandths, so a total carries no float noise


def month_index(ym):
    """Months since year 0 of a YYYY-MM string."""
    return int(ym[:4]) * 12 + int(ym[5:7]) - 1


def month_of(i):
    return f"{i // 12:04d}-{i % 12 + 1:02d}"


def scaled(text, what):
    """A published number as whole ten-thousandths; a number with more decimals than that fails loudly."""
    v = Decimal(text) * SCALE
    if v != v.to_integral_value():
        raise RuntimeError(f"{what}: {text} has more than four decimals")
    return int(v)


def bucket_of(mw, mwh):
    """The duration bucket of a unit: energy over power, both in the same scale. None for no energy value."""
    if mwh is None:
        return NOT_REPORTED
    if mw <= 0:
        raise RuntimeError("a battery unit with energy and no nameplate MW has no duration")
    if mwh < 2 * mw:
        return "lt2h"
    if mwh < 4 * mw:
        return "2to4h"
    if mwh < 6 * mw:
        return "4to6h"
    return "ge6h"


def region_of(ba):
    return f"iso:{ISO_OF_BA[ba]}" if ba in ISO_OF_BA else OUTSIDE


def units(op, rt, log):
    """One row per battery or solar unit that operates or operated: region, first month, the month it retired (None
    while operating), MW, MWh (None where EIA gives none) and bucket."""
    rows = []
    for table, d in (("operating", op), ("retired", rt)):
        for kind, sel in (("battery", d["prime_mover"] == "BA"), ("solar", d["technology_group"] == "solar")):
            g = d[sel & ~((kind == "solar") & (d["prime_mover"] == "BA"))]
            for r in g.to_dict("records"):
                if not r["operating_year"] or not r["operating_month"]:
                    raise RuntimeError(f"{r['entity_id']}: no operating year or month in the {table} table")
                first = int(r["operating_year"]) * 12 + int(r["operating_month"]) - 1
                end = None
                if table == "retired":
                    if not r["retirement_date"]:
                        raise RuntimeError(f"{r['entity_id']}: retired with no retirement date")
                    end = month_index(r["retirement_date"])
                mw = scaled(r["nameplate_mw"], f"{r['entity_id']} nameplate_mw")
                mwh = scaled(r["energy_capacity_mwh"], f"{r['entity_id']} energy_capacity_mwh") if kind == "battery" and r["energy_capacity_mwh"] != "" else None
                rows.append(dict(entity_id=r["entity_id"], kind=kind, table=table, ba=r["balancing_authority"],
                                 region=region_of(r["balancing_authority"]), first=first, end=end, mw=mw, mwh=mwh,
                                 bucket=bucket_of(mw, mwh) if kind == "battery" else ""))
    u = pd.DataFrame(rows)
    if u["entity_id"].duplicated().any():
        raise RuntimeError(f"a unit is in both the operating and the retired table: {sorted(u.loc[u['entity_id'].duplicated(), 'entity_id'])[:6]}")
    log(f"  units: {int((u['kind'] == 'battery').sum())} battery, {int((u['kind'] == 'solar').sum())} solar (operating and retired)")
    return u


def ratio(num, den):
    """num over den to four decimals, half up; None when the denominator is zero."""
    if den == 0:
        return None
    return float((Decimal(num) / Decimal(den)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def build(op, pl, rt, log=lambda m: None):
    """The table's rows as (entity, variable, month, value, unit), and the counts the header and the report state."""
    vint = sorted(set(op["vintage"]) | set(pl["vintage"]) | set(rt["vintage"]))
    if len(vint) != 1:
        raise RuntimeError(f"the three EIA-860M tables are not one vintage: {vint}")
    vintage = vint[0]
    last, first = month_index(vintage), month_index(START)
    u = units(op, rt, log)
    if (u["first"] > last).any():
        raise RuntimeError("a unit's first operating month is after the inventory month")
    months = list(range(first, last + 1))
    out, held_at = [], {}
    add = lambda e, v, m, val, unit: out.append((e, v, month_of(m), val, unit))  # noqa: E731
    for m in months:
        live = u[(u["first"] <= m) & (u["end"].isna() | (u["end"] > m))]
        b, s = live[live["kind"] == "battery"], live[live["kind"] == "solar"]
        for e in ENTITIES:
            be = b if e == TOTAL else b[b["region"] == e]
            se = s if e == TOTAL else s[s["region"] == e]
            mw, held = int(be["mw"].sum()), be[be["bucket"] != NOT_REPORTED]
            mwh, mw_held, solar = int(held["mwh"].sum()), int(held["mw"].sum()), int(se["mw"].sum())
            add(e, "battery_operating_mw", m, mw / SCALE, "MW")
            add(e, "battery_operating_mwh", m, mwh / SCALE, "MWh")
            held_at[(e, m)] = (mw, mwh)
            if (e, m - 12) in held_at:  # the change over twelve months, net of retirements; from the 13th month written
                add(e, "battery_operating_mw_net_added_12m", m, (mw - held_at[(e, m - 12)][0]) / SCALE, "MW")
                add(e, "battery_operating_mwh_net_added_12m", m, (mwh - held_at[(e, m - 12)][1]) / SCALE, "MWh")
            add(e, "battery_operating_units", m, float(len(be)), "count")
            for k in BUCKETS + [NOT_REPORTED]:
                g = be[be["bucket"] == k]
                add(e, f"battery_operating_mw_{k}", m, int(g["mw"].sum()) / SCALE, "MW")
                if k != NOT_REPORTED:
                    add(e, f"battery_operating_mwh_{k}", m, int(g["mwh"].sum()) / SCALE, "MWh")
            add(e, "solar_operating_mw", m, solar / SCALE, "MW")
            # the two ratios are omitted, never zero, where their denominator is zero
            if ratio(mwh, mw_held) is not None:
                add(e, "battery_operating_mwh_per_mw", m, ratio(mwh, mw_held), "MWh/MW")
            if ratio(mwh, solar) is not None:
                add(e, "battery_mwh_per_solar_mw", m, ratio(mwh, solar), "MWh/MW")
    # planned battery units, as of the inventory month
    p = pl[pl["prime_mover"] == "BA"].copy()
    if (p["planned_operation_date"] == "").any():
        raise RuntimeError("a planned battery unit has no planned operation date")
    p["region"] = p["balancing_authority"].map(region_of)
    p["mw"] = [scaled(v, "planned nameplate_mw") for v in p["nameplate_mw"]]
    p["y"] = p["planned_operation_date"].str[:4]
    for e in ENTITIES:
        pe = p if e == TOTAL else p[p["region"] == e]
        add(e, "battery_planned_mw", last, int(pe["mw"].sum()) / SCALE, "MW")
        add(e, "battery_planned_units", last, float(len(pe)), "count")
        add(e, "battery_planned_mw_under_construction", last, int(pe.loc[pe["status"] == "under_construction", "mw"].sum()) / SCALE, "MW")
        for y in sorted(set(p["y"])):
            add(e, f"battery_planned_mw_online_{y}", last, int(pe.loc[pe["y"] == y, "mw"].sum()) / SCALE, "MW")
    b_op = u[(u["kind"] == "battery") & (u["table"] == "operating")]
    s_op = u[(u["kind"] == "solar") & (u["table"] == "operating")]

    def outside(g, ba, mw):
        o = g[g[ba].map(region_of) == OUTSIDE]
        return dict(units=len(o), mw=int(o[mw].sum()) / SCALE, no_code_units=int((o[ba] == "").sum()),
                    no_code_mw=int(o.loc[o[ba] == "", mw].sum()) / SCALE, codes=int(o.loc[o[ba] != "", ba].nunique()))
    stats = dict(vintage=vintage, months=len(months),
                 battery_units=len(b_op), battery_retired=int(((u["kind"] == "battery") & (u["table"] == "retired")).sum()),
                 battery_no_energy=int((b_op["bucket"] == NOT_REPORTED).sum()), solar_units=len(s_op),
                 planned_units=len(p), planned_years=sorted(set(p["y"])),
                 outside_battery=outside(b_op, "ba", "mw"), outside_solar=outside(s_op, "ba", "mw"),
                 outside_planned=outside(p, "balancing_authority", "mw"))
    return pd.DataFrame(out, columns=["entity", "variable", "month", "value", "unit"]), stats


def read(path):
    with open(path, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--inputs-dir", help="read the three EIA-860M tables from this directory (default: warehouse/output)")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory instead of "
                                      "warehouse/output (a trial run)")
    a = ap.parse_args(argv)
    inputs_dir = os.path.abspath(a.inputs_dir) if a.inputs_dir else ip.OUT_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"storage_buildout_{run_id}.log"))
    status = dict(table=NAME, market="derived", status="ok", detail="")
    missing = [t for t in INPUTS.values() if not os.path.exists(os.path.join(inputs_dir, t + ".csv"))]
    if missing:  # session 10 ruling 3: a derived table without its inputs on the runner skips with a warning
        msg = f"inputs not on this machine: {', '.join(missing)}; the table is left as it is"
        log(f"SKIPPED: {msg}")
        print(f"storage_buildout SKIPPED: {msg}")
        ip.write_status("storage_buildout", run_id, [dict(status, status="skipped", detail=msg)])
        log.close()
        return 0
    try:
        op, pl, rt = (read(os.path.join(inputs_dir, INPUTS[k] + ".csv")) for k in ("operating", "planned", "retired"))
        reg = pd.read_csv(REGISTRY, dtype=str, keep_default_na=False)
        lic = dict(zip(reg["source"], reg["license"]))
        srcs = sorted(set(op["source"]) | set(pl["source"]) | set(rt["source"]))
        unknown = [s for s in srcs if s not in lic]
        if unknown:
            raise RuntimeError(f"input sources {unknown} are not in the registry; cannot set the license")
        license_ = "internal" if any(lic[s] == "internal" for s in srcs) else "public"
        urls = sorted(set(op["source_url"]) | set(pl["source_url"]) | set(rt["source_url"]))
        rows, st = build(op, pl, rt, log)
        s = pd.DataFrame({
            "entity": rows["entity"], "variable": rows["variable"], "ts_utc": rows["month"] + "-01T00:00:00Z",
            "value": rows["value"], "unit": rows["unit"], "freq": "P1M", "geo": "US", "market": "", "node": "",
            "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")),
            "vintage": "",
        }).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        # Decision 26: a row whose value is unchanged keeps the retrieved_at of the run that first wrote it, so the
        # Supabase loader rewrites only the months a new inventory adds or revises
        out_path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(out_path):
            prev = ip.read_series(out_path, ip.SERIES_COLS)
            prev["value"] = pd.to_numeric(prev["value"])
            key = ["entity", "variable", "ts_utc", "value"]
            s = s.merge(prev[key + ["retrieved_at"]].rename(columns={"retrieved_at": "_prev"}), on=key, how="left")
            kept = int(s["_prev"].notna().sum())
            s["retrieved_at"] = s["_prev"].fillna(s["retrieved_at"])
            s = s.drop(columns="_prev")
            log(f"{kept} of {len(s)} rows unchanged since the last run keep their retrieved_at")
        ob, os_, opl = st["outside_battery"], st["outside_solar"], st["outside_planned"]
        header = [
            "Energy Research Warehouse (ERW): Battery storage built, by grid and month, by duration, against solar, "
            f"and planned by year online; EIA-860M inventory of {st['vintage']} (derived, session 69)",
            "Shape: series (docs/datastandard.md v0). freq P1M: ts_utc is the first of the month, 00:00:00Z, and a "
            "value is the fleet at that month's end. entity iso:<caiso|ercot|isone|miso|nyiso|pjm|spp>, "
            "us:outside_isos, us:total.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/storage_buildout.py",
            f"Run log: warehouse/output/logs/storage_buildout_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, storage build-out method ({METHOD}), {METHOD_URL}",
            "Derived from: " + "; ".join(INPUTS.values()),
            f"  input sources: {'; '.join(srcs)} ({'; '.join(urls)}), inventory month {st['vintage']}",
            "Variables: battery_operating_mw, battery_operating_mwh, battery_operating_units; "
            "battery_operating_mw_<bucket> and battery_operating_mwh_<bucket> for the duration buckets lt2h (under 2 "
            "hours), 2to4h, 4to6h, ge6h (6 and more), a unit's Nameplate Energy Capacity (MWh) over its nameplate MW; "
            "battery_operating_mw_energy_not_reported (units EIA gives no energy for: in no duration bucket, MWh "
            "never estimated); solar_operating_mw (photovoltaic and solar thermal); battery_operating_mwh_per_mw "
            "(average duration: MWh over the MW of the units that report energy) and battery_mwh_per_solar_mw, "
            "omitted where the denominator is zero; battery_operating_mw_net_added_12m and "
            "battery_operating_mwh_net_added_12m (the month's value less the value twelve months before, so net of "
            "retirements; from the thirteenth month). At the inventory month only: battery_planned_mw, "
            "battery_planned_units, battery_planned_mw_under_construction, battery_planned_mw_online_<year> (the year "
            "of EIA's planned operation date). No planned MWh: EIA-860M's Planned sheet has no energy column.",
            "Grid: the generator's balancing authority code in EIA-860M where it is one of the seven ISOs (CISO, "
            "ERCO, ISNE, MISO, NYIS, PJM, SWPP); us:outside_isos is every other code and no code; us:total is every "
            "unit (Puerto Rico included), the seven grids plus us:outside_isos. Outside the seven in this inventory: "
            f"{ob['units']} operating battery units, {ob['mw']:,.1f} MW ({ob['no_code_units']} with no code, "
            f"{ob['no_code_mw']:,.1f} MW); {os_['units']} operating solar units, {os_['mw']:,.1f} MW "
            f"({os_['no_code_units']} with no code); {opl['units']} planned battery units, {opl['mw']:,.1f} MW "
            f"({opl['no_code_units']} with no code).",
            f"History: months {START} to {st['vintage']} are rebuilt from this one inventory by each unit's first "
            "operating month and, for the retired table's units, its retirement month. A unit retired before the "
            "retired table's window (the inventory year and the year before) is in no month; a unit's MW and MWh are "
            "its present ones in every month it operated. Operating is EIA's operating inventory: statuses OP, SB, OS "
            f"and OA. {st['battery_no_energy']} of {st['battery_units']} operating battery units carry no energy value.",
            f"License: {license_}. A derived table inherits the most restrictive license of its inputs (Decision 23).",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report=f"Storage build-out by grid and month ({METHOD})", report_url=METHOD_URL,
                                document_list=METHOD, license=license_, tables=[NAME])])
        status["detail"] = (f"{len(s)} rows, {st['months']} months to {st['vintage']}; {st['battery_units']} operating "
                            f"battery units ({st['battery_no_energy']} without energy), {st['battery_retired']} retired, "
                            f"{st['solar_units']} solar, {st['planned_units']} planned; outside the seven ISOs: "
                            f"{ob['units']} battery units, {ob['mw']:,.1f} MW ({ob['no_code_units']} with no code)")
        log(status["detail"])
        log(f"stats: {st}")
        print(f"storage_buildout: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"storage_buildout FAILED, no output file written: {last}", file=sys.stderr)
        status.update(status="failed", detail=last[:300])
    ip.write_status("storage_buildout", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
