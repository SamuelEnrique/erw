#!/usr/bin/env python3
"""The Mine Safety and Health Administration's coal mines and their quarterly production, hours and employees, from
MSHA's open government data (session 2034, chain 058: the mines behind EIA's coal tables, with the quarters EIA's
yearly figures do not show).

Energy Research Warehouse (ERW) connector. Two tables from the pipe-delimited files of MSHA's Open Government Data page
(https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp), refreshed by MSHA each week:

    https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip                 Mines.txt, one row a mine
    https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdQuarterly.zip    MinesProdQuarterly.txt, a mine,
                                                                                  subunit and quarter a row

    msha_coal_mines            entities: every coal mine (COAL_METAL_IND C). entity_id msha_mine:<MINE_ID>, the
                               seven digits MSHA writes (EIA's tables drop the leading zero); entity_type plant; name the
                               current mine name; geo US-<STATE>; lat, lon as MSHA gives them; status from MSHA's current
                               status (Active and New Mine active; Temporarily Idled and NonProducing suspended; Abandoned
                               and Abandoned and Sealed retired), its words in x_mine_status; status_date the current
                               status date; operator the current operator's name; x_ the mine type, controller, county,
                               district and the rest below
    msha_coal_production_quarterly   series: a coal mine's quarter, its subunits summed, from 2010. entity
                               msha_mine:<MINE_ID>; variables coal_production (unit short_ton: MSHA's "tons"), employee_hours
                               (unit count: the hours the operator reports its employees worked) and average_employees
                               (unit count: the subunits' average employees, summed); ts_utc the calendar quarter's first
                               day; freq P3M; geo US-<STATE>; node the mine's name; x_subunits the subunits reported,
                               x_production_blank those whose production MSHA leaves empty

A mine and quarter whose production every subunit leaves empty has no coal_production row; where only some do, the
others are summed and the empty ones are counted in x_production_blank. Nothing is filled. A file without its columns, a
mine given twice, a quarter outside 1 to 4 or a figure not a number stops the run.

    python warehouse/connectors/msha_mines.py [--offline] [--out-dir DIR] [--from-year 2010]

Ceiling: two requests (the two zips, about 62 MB), saved in warehouse/raw/msha_mines/ and reused offline.
arlweb.msha.gov has no robots file (HTTP 404). License: public (the U.S. Department of Labor; read in session 2034).
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "msha_mines"
SOURCE = "msha:open_government_data"
HOST = "https://arlweb.msha.gov"
PAGE = HOST + "/OpenGovernmentData/OGIMSHA.asp"
FILES = {"mines": (HOST + "/OpenGovernmentData/DataSets/Mines.zip", "Mines.txt"),
         "prod": (HOST + "/OpenGovernmentData/DataSets/MinesProdQuarterly.zip", "MinesProdQuarterly.txt")}
MINES, PROD = "msha_coal_mines", "msha_coal_production_quarterly"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
NEED = {"mines": ["MINE_ID", "CURRENT_MINE_NAME", "COAL_METAL_IND", "CURRENT_MINE_TYPE", "CURRENT_MINE_STATUS", "CURRENT_STATUS_DT",
                  "CURRENT_CONTROLLER_NAME", "CURRENT_OPERATOR_NAME", "STATE", "FIPS_CNTY_CD", "FIPS_CNTY_NM", "DISTRICT", "PRIMARY_SIC",
                  "NO_EMPLOYEES", "LONGITUDE", "LATITUDE", "NEAREST_TOWN"],
        "prod": ["MINE_ID", "CURR_MINE_NM", "STATE", "SUBUNIT_CD", "CAL_YR", "CAL_QTR", "AVG_EMPLOYEE_CNT", "HOURS_WORKED",
                 "COAL_PRODUCTION", "COAL_METAL_IND"]}
STATUS = {"Active": "active", "New Mine": "active", "Temporarily Idled": "suspended", "NonProducing": "suspended",
          "Abandoned": "retired", "Abandoned and Sealed": "retired"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
X_MINES = ["x_mine_status", "x_mine_type", "x_controller", "x_county_fips", "x_county", "x_district", "x_primary_sic", "x_employees",
           "x_nearest_town"]
X_PROD = ["x_subunits", "x_production_blank"]
FROM_YEAR = 2010


def read(content, kind):
    inner = FILES[kind][1]
    z = zipfile.ZipFile(io.BytesIO(content))
    if inner not in z.namelist():
        raise RuntimeError(f"{kind}: the zip holds {z.namelist()[:5]}, not {inner}")
    d = pd.read_csv(io.BytesIO(z.read(inner)), sep="|", dtype=str, keep_default_na=False, encoding="latin-1",
                    usecols=lambda c: c in NEED[kind])
    miss = [c for c in NEED[kind] if c not in d.columns]
    if miss:
        raise RuntimeError(f"{kind}: no column {miss}")
    return d.apply(lambda s: s.str.strip())


def day(s, what):
    """MSHA's MM/DD/YYYY as YYYY-MM-DD; empty stays empty."""
    if s == "":
        return ""
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if not m:
        raise RuntimeError(f"{what}: a date not as MSHA writes it: {s!r}")
    return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"


def coord(s, lo, hi):
    v = pd.to_numeric(s, errors="coerce")
    return "" if pd.isna(v) or not (lo <= v <= hi) or v == 0 else f"{v:.6f}"


def mines(m, base):
    c = m[m.COAL_METAL_IND == "C"]
    if c.MINE_ID.duplicated().any():
        raise RuntimeError(f"a mine given twice: {c.MINE_ID[c.MINE_ID.duplicated()].head(3).tolist()}")
    unknown = sorted(set(c.CURRENT_MINE_STATUS) - set(STATUS) - {""})
    if unknown:
        raise RuntimeError(f"a mine status not known: {unknown}")
    if (~c.STATE.str.fullmatch(r"[A-Z]{2}")).any():
        raise RuntimeError(f"a state not a code: {c.STATE[~c.STATE.str.fullmatch(r'[A-Z]{2}')].unique()[:5].tolist()}")
    lon = c.LONGITUDE.map(lambda s: coord(s, -180, 180))
    lat = c.LATITUDE.map(lambda s: coord(s, -90, 90))
    lone = (lat == "") != (lon == "")  # a place given by one coordinate is no place: both left empty
    lat, lon = lat.where(~lone, ""), lon.where(~lone, "")
    return pd.DataFrame({
        "entity_id": "msha_mine:" + c.MINE_ID, "entity_type": "plant", "name": c.CURRENT_MINE_NAME, "geo": "US-" + c.STATE,
        "lat": lat, "lon": lon, "capacity_mw": "", "status": c.CURRENT_MINE_STATUS.map(STATUS).fillna(""),
        "status_date": [day(s, f"mine {i}") for s, i in zip(c.CURRENT_STATUS_DT, c.MINE_ID)], "operator": c.CURRENT_OPERATOR_NAME, **base,
        "x_mine_status": c.CURRENT_MINE_STATUS, "x_mine_type": c.CURRENT_MINE_TYPE, "x_controller": c.CURRENT_CONTROLLER_NAME,
        "x_county_fips": c.FIPS_CNTY_CD, "x_county": c.FIPS_CNTY_NM, "x_district": c.DISTRICT, "x_primary_sic": c.PRIMARY_SIC,
        "x_employees": c.NO_EMPLOYEES, "x_nearest_town": c.NEAREST_TOWN})


def production(q, base, from_year):
    c = q[q.COAL_METAL_IND == "C"].copy()
    for col in ("CAL_YR", "CAL_QTR"):
        if (~c[col].str.fullmatch(r"\d+")).any():
            raise RuntimeError(f"{col} not a number: {c[col][~c[col].str.fullmatch(r'[0-9]+')].unique()[:3].tolist()}")
    c["y"], c["qn"] = c.CAL_YR.astype(int), c.CAL_QTR.astype(int)
    if not c.qn.between(1, 4).all():
        raise RuntimeError("a quarter outside 1 to 4")
    c = c[c.y >= from_year]
    for col in ("AVG_EMPLOYEE_CNT", "HOURS_WORKED", "COAL_PRODUCTION"):
        v = pd.to_numeric(c[col], errors="coerce")
        bad = v.isna() & (c[col] != "")
        if bad.any():
            raise RuntimeError(f"{col} not a number: {c.loc[bad, col].head(3).tolist()}")
        c[col + "_n"] = v
    c["blank"] = c.COAL_PRODUCTION == ""
    g = c.groupby(["MINE_ID", "y", "qn"], sort=True).agg(
        name=("CURR_MINE_NM", "last"), state=("STATE", "last"), subunits=("SUBUNIT_CD", "size"), blank=("blank", "sum"),
        prod=("COAL_PRODUCTION_n", "sum"), hours=("HOURS_WORKED_n", "sum"), emp=("AVG_EMPLOYEE_CNT_n", "sum"),
        hours_given=("HOURS_WORKED_n", "count"), emp_given=("AVG_EMPLOYEE_CNT_n", "count")).reset_index()
    ts = g.y.astype(str) + "-" + ((g.qn - 1) * 3 + 1).map("{:02d}".format) + "-01T00:00:00Z"
    common = dict(unit=None, freq="P3M", market="", **base)
    out = []
    for var, col, unit, keep in (("coal_production", "prod", "short_ton", g.blank < g.subunits),
                                 ("employee_hours", "hours", "count", g.hours_given > 0),
                                 ("average_employees", "emp", "count", g.emp_given > 0)):
        k = g[keep]
        out.append(pd.DataFrame({"entity": "msha_mine:" + k.MINE_ID, "variable": var, "ts_utc": ts[keep], "value": k[col].round(2),
                                 **{**common, "unit": unit}, "geo": "US-" + k.state, "node": k.name,
                                 "x_subunits": k.subunits, "x_production_blank": k.blank}))
    s = pd.concat(out, ignore_index=True)
    s["value"] = s["value"].map(lambda v: f"{v:.0f}" if float(v).is_integer() else f"{v:.2f}")
    return s, int(c.blank.sum())


def main(argv=None):
    ap = argparse.ArgumentParser(description="MSHA's coal mines and their quarterly production, hours and employees")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--from-year", type=int, default=FROM_YEAR)
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        frames, bases = {}, {}
        for kind, (url, _) in FILES.items():
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300, pause=1)
            frames[kind] = read(content, kind)
            bases[kind] = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            del content
        e = mines(frames["mines"], bases["mines"])
        s, blanks = production(frames["prod"], bases["prod"], args.from_year)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a mine, variable and quarter given twice")
        common = [
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/msha_mines.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Mine Safety and Health Administration (MSHA), U.S. Department of Labor, Open Government Data, {PAGE}",
        ]
        lic = 'License: public (a work of the U.S. Department of Labor; cite "Mine Safety and Health Administration, Open Government Data").'
        cols_e = ENTITY_COLS + X_MINES
        e = e[cols_e].sort_values("entity_id").reset_index(drop=True)
        st = e.x_mine_status.value_counts().to_dict()
        head_e = [
            "Energy Research Warehouse (ERW): Mine Safety and Health Administration (MSHA), Open Government Data, Mines: every coal mine, its current "
            "status, operator, place and type (session 2034)",
            "Shape: entities (docs/datastandard.md v0). entity_id msha_mine:<MINE_ID> (seven digits; EIA's coal tables drop the leading zero); "
            "entity_type plant; name the current mine name; geo US-<state>; lat, lon as MSHA gives them (a zero or out-of-range one left empty); "
            "status from MSHA's current status (Active, New Mine: active; Temporarily Idled, NonProducing: suspended; Abandoned, Abandoned and "
            "Sealed: retired), its words in x_mine_status; status_date the current status date; operator the current operator.",
            f"{len(e)} coal mines: " + ", ".join(f"{k} {v}" for k, v in st.items()) + f". {int((e.lat != '').sum())} with a place; a mine whose "
            "latitude or longitude MSHA leaves empty, zero or out of range has both empty. Nothing is filled.",
        ] + common + [f"  access: {FILES['mines'][0]} ({FILES['mines'][1]})", lic]
        ip.write_snapshot(e, MINES, head_e, log, cols_e)
        results.append(dict(table=MINES, market="all", status="ok", detail=f"{len(e)} rows"))
        cols_s = ip.SERIES_COLS + X_PROD
        s = s[cols_s].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head_s = [
            "Energy Research Warehouse (ERW): Mine Safety and Health Administration (MSHA), Open Government Data, Quarterly Mine Employment and "
            f"Production: each coal mine's quarter from {args.from_year}, its subunits summed (session 2034)",
            "Shape: series (docs/datastandard.md v0). entity msha_mine:<MINE_ID>; variables coal_production (short_ton: MSHA's tons), employee_hours "
            "(count: the hours the operator reports its employees worked) and average_employees (count: the subunits' average employees, summed); "
            "ts_utc the calendar quarter's first day; freq P3M; geo US-<state>; node the mine's name; x_subunits the subunits reported; "
            "x_production_blank those whose production MSHA leaves empty.",
            f"{len(s)} rows, {s.entity.nunique()} mines, {s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]}. A quarter whose production every subunit "
            f"leaves empty has no coal_production row; {blanks} subunit quarters leave it empty. Nothing is filled. The newest quarters grow as "
            "operators report.",
        ] + common + [f"  access: {FILES['prod'][0]} ({FILES['prod'][1]})", lic]
        ip.write_snapshot(s, PROD, head_s, log, cols_s)
        results.append(dict(table=PROD, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{MINES}: {len(e)} mines; {PROD}: {len(s)} rows, {s.entity.nunique()} mines")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results = [dict(table=t, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]) for t in (MINES, PROD)]
    if not args.out_dir:
        if results and all(r["status"] == "ok" for r in results):
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Labor, Mine Safety and Health Administration (MSHA)",
                                    report="Open Government Data: Mines; Quarterly Mine Employment and Production", report_url=PAGE,
                                    document_list=HOST + "/OpenGovernmentData/DataSets/", license="public", tables=[MINES, PROD])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
