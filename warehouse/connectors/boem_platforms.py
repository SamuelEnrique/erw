#!/usr/bin/env python3
"""The Bureau of Ocean Energy Management's offshore platforms: every oil and gas structure on the Outer Continental
Shelf, installed or removed, with its place, its dates, and its complex's water depth, distance to shore, operator number
and production flags (session 2007, chain 056: the offshore half of oil and gas supply, which the ERW held only as
BOEM's lease production).

Energy Research Warehouse (ERW) connector. One entities table from BOEM's Data Center platform files, each a fixed-width
text file in a zip, read by the layout BOEM publishes beside it:

    https://www.data.boem.gov/Main/Platform.aspx
    https://www.data.boem.gov/Platform/Files/platstrufixed.zip   Platform Structures (layout: HtmlPage.aspx?page=platformStructures)
    https://www.data.boem.gov/Platform/Files/platlocfixed.zip    Platform Locations  (layout: HtmlPage.aspx?page=platformLocations)
    https://www.data.boem.gov/Platform/Files/platmastfixed.zip   Platform Masters    (layout: HtmlPage.aspx?page=platformMasters)

    boem_offshore_platforms   entity_id boem_platform:<complex id>-<structure number>; entity_type platform (Decision 58);
                              name the structure's name; geo US (federal waters); lat, lon from the locations file;
                              capacity_mw empty; status retired where BOEM gives a removal date, else active; status_date
                              the removal date, else the install date; operator empty (BOEM gives a company number, kept in
                              x_company_num); x_ the structure's and its complex's fields (below)

A layout's start positions and lengths are read from its page, never assumed; a column the connector needs not in the
layout, a structure given twice, or a date not as BOEM writes it stops the run. A structure with no location row keeps
empty coordinates; a complex with no masters row keeps empty complex fields; both are counted in the header. Nothing is
filled.

    python warehouse/connectors/boem_platforms.py [--offline] [--out-dir DIR]

Ceiling: six requests (three layout pages and three zips), saved in warehouse/raw/boem_platforms/ and reused offline.
www.data.boem.gov's robots file names only other readers. License: public (BOEM, read 86 of license_reads.csv: "materials
produced by federal agencies are in the public domain").
"""

import argparse
import datetime as dt
import html as htmlmod
import io
import os
import re
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "boem_platforms"
SOURCE = "boem:platforms"
HOST = "https://www.data.boem.gov"
PAGE = HOST + "/Main/Platform.aspx"
FILES = {
    "structures": ("/Platform/Files/platstrufixed.zip", "/Main/HtmlPage.aspx?page=platformStructures"),
    "locations": ("/Platform/Files/platlocfixed.zip", "/Main/HtmlPage.aspx?page=platformLocations"),
    "masters": ("/Platform/Files/platmastfixed.zip", "/Main/HtmlPage.aspx?page=platformMasters"),
}
TABLE = "boem_offshore_platforms"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# the columns taken, as each layout names them (case and spacing ignored)
NEED = {
    "structures": ["Area Code", "Block Number", "Complex Id Num", "Structure Number", "Structure Name", "Structure Type Code", "Install Date",
                   "Removal Date", "Deck Count", "Slot Count", "Major Structure Flag", "Authority Status"],
    "locations": ["Complex Id Number", "Structure Number", "Longitude", "Latitude", "District Code"],
    "masters": ["Complex Id Num", "Mms Company Num", "Water Depth", "Distance To Shore", "Lease Number", "Field Name Code", "Production Flag",
                "Oil Prod Flag", "Gas Prod Flag", "Manned 24 Hr Fl", "Abandon Flag"],
}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
X_COLS = ["x_complex_id", "x_structure_number", "x_area_code", "x_block_number", "x_district", "x_structure_type", "x_install_date",
          "x_removal_date", "x_deck_count", "x_slot_count", "x_major_structure", "x_authority_status", "x_company_num", "x_water_depth_ft",
          "x_distance_to_shore_nmi", "x_lease_number", "x_field_name_code", "x_production", "x_oil_production", "x_gas_production",
          "x_manned_24h", "x_to_be_removed"]
MONTHS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], start=1)}


def key(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def layout(page_html):
    """[(start, length, alias)] from the layout page's table headed Start Position, Item Length, Column Alias."""
    for tb in re.findall(r"<table.*?</table>", page_html, re.S | re.I):
        rows = []
        for tr in re.findall(r"<tr.*?</tr>", tb, re.S | re.I):
            cells = [re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", "", c))).strip() for c in re.findall(r"<t[dh].*?</t[dh]>", tr, re.S | re.I)]
            rows.append(cells)
        if rows and rows[0][:3] == ["Start Position", "Item Length", "Column Alias"]:
            out = [(int(r[0]), int(r[1]), r[2]) for r in rows[1:] if len(r) >= 3 and r[0].isdigit() and r[1].isdigit()]
            if out:
                return out
    raise RuntimeError("no layout table (Start Position, Item Length, Column Alias) in the page")


def read_fixed(text, lay, need, name):
    pos = {key(a): (s - 1, s - 1 + n) for s, n, a in lay}
    miss = [c for c in need if key(c) not in pos]
    if miss:
        raise RuntimeError(f"{name}: columns not in the layout: {miss}")
    rows = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        rows.append({c: ln[pos[key(c)][0]:pos[key(c)][1]].strip() for c in need})
    if not rows:
        raise RuntimeError(f"{name}: no row")
    return pd.DataFrame(rows)


def day(s):
    """BOEM's dates: DD-MON-YYYY (or DD-MON-YY), MM/DD/YYYY or YYYYMMDD; empty stays empty."""
    s = s.strip()
    if not s:
        return ""
    m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})-(\d{2}|\d{4})", s)
    if m and m.group(2).upper() in MONTHS:
        y = int(m.group(3))
        y = y + (1900 if y >= 40 else 2000) if y < 100 else y
        return f"{y:04d}-{MONTHS[m.group(2).upper()]:02d}-{int(m.group(1)):02d}"
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    raise RuntimeError(f"a date not as BOEM writes it: {s!r}")


def build(st, loc, mas, base):
    st = st.copy()
    st["id"] = st["Complex Id Num"].str.lstrip("0") + "-" + st["Structure Number"].str.lstrip("0").replace("", "0")
    if st["id"].duplicated().any():
        raise RuntimeError(f"a structure given twice: {st[st['id'].duplicated()]['id'].head(3).tolist()}")
    loc = loc.copy()
    loc["id"] = loc["Complex Id Number"].str.lstrip("0") + "-" + loc["Structure Number"].str.lstrip("0").replace("", "0")
    locs = loc.drop_duplicates("id", keep="first").set_index("id")  # a structure's first location row
    mas = mas.copy()
    mas["cid"] = mas["Complex Id Num"].str.lstrip("0")
    masters = mas.drop_duplicates("cid").set_index("cid")
    out, no_loc, no_mas = [], 0, 0
    for _, r in st.iterrows():
        inst, rem = day(r["Install Date"]), day(r["Removal Date"])
        lat = lon = ""
        if r["id"] in locs.index:
            lat_v, lon_v = pd.to_numeric(locs.at[r["id"], "Latitude"], errors="coerce"), pd.to_numeric(locs.at[r["id"], "Longitude"], errors="coerce")
            if not (pd.isna(lat_v) or pd.isna(lon_v)):
                lat, lon = f"{lat_v:.6f}", f"{lon_v:.6f}"
            district = locs.at[r["id"], "District Code"]
        else:
            no_loc += 1
            district = ""
        cid = r["Complex Id Num"].lstrip("0")
        m = masters.loc[cid] if cid in masters.index else None
        if m is None:
            no_mas += 1
        g = (lambda c: m[c] if m is not None else "")
        out.append(dict(
            entity_id=f"boem_platform:{r['id']}", entity_type="platform", name=r["Structure Name"], geo="US", lat=lat, lon=lon, capacity_mw="",
            status="retired" if rem else "active", status_date=rem or inst, operator="", **base,
            x_complex_id=cid, x_structure_number=r["Structure Number"].lstrip("0") or "0", x_area_code=r["Area Code"], x_block_number=r["Block Number"],
            x_district=district, x_structure_type=r["Structure Type Code"], x_install_date=inst, x_removal_date=rem, x_deck_count=r["Deck Count"],
            x_slot_count=r["Slot Count"], x_major_structure=r["Major Structure Flag"], x_authority_status=r["Authority Status"],
            x_company_num=g("Mms Company Num"), x_water_depth_ft=g("Water Depth"), x_distance_to_shore_nmi=g("Distance To Shore"),
            x_lease_number=g("Lease Number"), x_field_name_code=g("Field Name Code"), x_production=g("Production Flag"),
            x_oil_production=g("Oil Prod Flag"), x_gas_production=g("Gas Prod Flag"), x_manned_24h=g("Manned 24 Hr Fl"), x_to_be_removed=g("Abandon Flag")))
    return pd.DataFrame(out), no_loc, no_mas


def unzip_text(content, name):
    z = zipfile.ZipFile(io.BytesIO(content))
    files = [n for n in z.namelist() if not n.endswith("/")]
    if len(files) != 1:
        raise RuntimeError(f"{name}: the zip holds {len(files)} files, not one: {files[:5]}")
    return z.read(files[0]).decode("latin-1"), files[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="BOEM's offshore platforms (structures, locations, masters)")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
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
        frames, inner, recs = {}, {}, {}
        for name, (zpath, lpath) in FILES.items():
            page, _ = ip.fetch_raw(CONNECTOR, HOST + lpath, log, offline=args.offline, headers=UA, timeout=60, pause=1)
            lay = layout(page.decode("utf-8", errors="replace"))
            content, rec = ip.fetch_raw(CONNECTOR, HOST + zpath, log, offline=args.offline, headers=UA, timeout=120, pause=1)
            text, inner[name] = unzip_text(content, name)
            frames[name] = read_fixed(text, lay, NEED[name], name)
            recs[name] = rec
        rec = recs["structures"]
        base = dict(source=SOURCE, source_url=HOST + FILES["structures"][0], retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        e, no_loc, no_mas = build(frames["structures"], frames["locations"], frames["masters"], base)
        cols = ENTITY_COLS + X_COLS
        e = e[cols].sort_values("entity_id").reset_index(drop=True)
        active = int((e.status == "active").sum())
        head = [
            "Energy Research Warehouse (ERW): Bureau of Ocean Energy Management (BOEM), Data Center, Platform Structures, Platform Locations and Platform "
            "Masters: every oil and gas structure on the Outer Continental Shelf, installed or removed, with its place, dates and its complex's fields (session 2007)",
            "Shape: entities (docs/datastandard.md v0). entity_id boem_platform:<complex id>-<structure number>; entity_type platform (Decision 58); name the "
            "structure's name; geo US; lat, lon from the locations file; status retired where BOEM gives a removal date, else active; status_date the "
            "removal date, else the install date; operator empty (x_company_num is BOEM's company number); x_ the structure's and its complex's fields.",
            f"{len(e)} structures in {e.x_complex_id.nunique()} complexes: {active} active, {len(e) - active} removed. {no_loc} structures have no location "
            f"row and {no_mas} no masters row; their fields stay empty. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/boem_platforms.py; the structures file retrieved {base['retrieved_at']}, last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Bureau of Ocean Energy Management, Data Center, Platform, {PAGE}",
            "  access: " + "; ".join(f"{HOST}{z} ({inner[n]}, layout {HOST}{lp})" for n, (z, lp) in FILES.items()),
            'License: public (BOEM: "materials produced by federal agencies are in the public domain"; cite "Bureau of Ocean Energy Management").',
        ]
        ip.write_snapshot(e, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(e)} rows"))
        print(f"{TABLE}: {len(e)} structures, {active} active; no location {no_loc}, no masters {no_mas}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Bureau of Ocean Energy Management (BOEM)",
                                    report="Data Center: Platform Structures, Platform Locations and Platform Masters", report_url=PAGE,
                                    document_list=HOST + "/Platform/Files/", license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
