#!/usr/bin/env python3
"""The balancing authority areas of the United States: HIFLD's "Control Areas" layer, each polygon keyed to its EIA-930
balancing authority code (session 8000, chain 501 step B2).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ba_boundaries.csv, and one web file,
site/data/regions/ba_boundaries.json (the polygons simplified, under 1.5 MB). Method: docs/methods/ba_boundaries.md.

    python warehouse/connectors/hifld_control_areas.py get      # one request, the layer as GeoJSON, to warehouse/raw (no lock)
    python warehouse/connectors/hifld_control_areas.py build    # the table and the web file from the saved copy (data lock)
    python warehouse/connectors/hifld_control_areas.py build --out-dir DIR   # a trial: both under DIR

THE LAYER. "Control Areas", a feature class of the Homeland Infrastructure Foundation-Level Data (HIFLD) open catalog,
compiled by Oak Ridge, Los Alamos and Idaho National Laboratories and NGA's HSIP team; its metadata: "Limitations of use:
None (Public Use)". HIFLD's own open catalog was retired on 26 August 2025 (session 180b found its hub gone and its
former ArcGIS host refusing its robots file). Penn State's PASDA (Pennsylvania Spatial Data Access, the state's
geospatial clearinghouse, "free public access") serves the same national layer, 71 polygons, in its map service
HIFLD_FEMA, layer 26 (https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/26). That host's
robots file answers 404 (no rule), read on 19 November 2026 before any other request. NASA's HIFLD mirror
(maps.nccs.nasa.gov) did not resolve from this machine; DataLumos disallows ClaudeBot and anthropic-ai by name, so it was
not read.

THE KEY. HIFLD's ID is the authority's EIA entity identifier. EIA-861's annual file Balancing_Authority_<year>.xlsx
(saved by the eia861 connector, years 2015 to 2025) pairs each "BA ID" with its "BA Code", the code EIA-930 uses. A
polygon is given a code only through that pair: nothing is matched by name. A polygon whose ID no EIA-861 year pairs
with a code, or whose code EIA-930 does not list, is kept with entity_id hifld:control_area:<ID> and listed; an EIA-930
authority with no polygon is listed in the web file and the method note.

THE TABLE (entities, entity_type balancing_authority, Decision 80). entity_id eia930:<code> (hifld:control_area:<ID>
where no code), name as HIFLD writes it, geo the ISO 3166-2 code of HIFLD's STATE (the authority's address, not its
whole area), lat and lon the centroid of the polygon, source hifld:control_areas. x_hifld_id, x_eia930_code,
x_eia930_name, x_region (EIA-930's), x_area_km2 (the polygon's area on a sphere of radius 6,371.0088 km, before
simplification), x_parts (polygon parts), x_vertices, x_source_date and x_val_date (HIFLD's dates), x_year (the year of
HIFLD's load figures), x_peak_load_mw and x_total_cap_mw (as HIFLD prints them; -999 and blanks are left blank),
x_raw_sha256.

THE WEB FILE. Each polygon simplified (Douglas-Peucker with topology kept, shapely), coordinates rounded to 3 decimals.
The tolerance starts at 0.01 degrees and is doubled until the file is under 1.5 MB.
"""

import argparse
import csv
import datetime as dt
import glob
import hashlib
import io
import json
import math
import os
import sys
import zipfile

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "ba_boundaries"
SOURCE = "hifld:control_areas"
UA = "ERW research project, github.com/SamuelEnrique/erw"
HOST = "mapservices.pasda.psu.edu"
LAYER = f"https://{HOST}/server/rest/services/pasda/HIFLD_FEMA/MapServer/26"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ba_boundaries.md"
RAW = os.path.join(ROOT, "warehouse", "raw", "hifld_control_areas")
SITE_FILE = os.path.join(ROOT, "site", "data", "regions", "ba_boundaries.json")
MAX_BYTES = 200 * 1024 ** 2
BATCH, GAP = 8, 5
WEB_LIMIT = int(1.5 * 1024 ** 2)
R_KM = 6371.0088
COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
        "source", "source_url", "retrieved_at", "vintage", "x_hifld_id", "x_eia930_code", "x_eia930_name", "x_region",
        "x_area_km2", "x_parts", "x_vertices", "x_source_date", "x_val_date", "x_year", "x_peak_load_mw",
        "x_total_cap_mw", "x_raw_sha256"]
CANADA = {"AB": "CA-AB", "BC": "CA-BC", "MB": "CA-MB", "NB": "CA-NB", "NS": "CA-NS", "ON": "CA-ON", "QC": "CA-QC",
          "SK": "CA-SK", "PE": "CA-PE", "NL": "CA-NL"}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(argv):
    """The layer as GeoJSON in batches of BATCH object ids (the service answered "Could not access any server machines"
    to the whole layer in one request on 19 November 2026). Each answer is saved as it came and logged; the batches are
    joined into control_areas.geojson only when every one is a GeoJSON FeatureCollection. GAP seconds between requests."""
    import time
    if ip.paused_host(HOST):
        print(f"refused: {HOST} is a paused publisher's host")
        return 1
    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(RAW, run)
    os.makedirs(d, exist_ok=True)
    log_rows, feats = [], []

    def fetch(url, name):
        t0 = dt.datetime.now(dt.timezone.utc)
        r = requests.get(url, headers={"User-Agent": UA}, timeout=600, allow_redirects=False)
        body = r.content
        if len(body) > MAX_BYTES:
            raise SystemExit(f"refused: an answer passed {MAX_BYTES} bytes")
        sha = hashlib.sha256(body).hexdigest()
        with open(os.path.join(d, name), "wb") as f:
            f.write(body)
        log_rows.append([url, r.status_code, len(body), round((dt.datetime.now(dt.timezone.utc) - t0).total_seconds(), 1),
                         t0.strftime("%Y-%m-%dT%H:%M:%SZ"), sha, name, r.headers.get("Content-Type", "")])
        print(f"  {r.status_code} {len(body):,} bytes {name}")
        return r.status_code, body

    try:
        st, body = fetch(LAYER + "/query?where=1%3D1&returnIdsOnly=true&f=json", "object_ids.json")
        ids = sorted(json.loads(body)["objectIds"]) if st == 200 else []
        if not ids:
            raise SystemExit("no object ids in the answer")
        for k in range(0, len(ids), BATCH):
            time.sleep(GAP)
            part = ids[k:k + BATCH]
            url = LAYER + "/query?objectIds=" + "%2C".join(str(i) for i in part) + "&outFields=*&returnGeometry=true&outSR=4326&f=geojson"
            st, body = fetch(url, f"batch_{k // BATCH + 1:02d}.geojson")
            try:
                gj = json.loads(body)
            except ValueError:
                raise SystemExit(f"batch {k // BATCH + 1} is not JSON (status {st}); nothing joined")
            if gj.get("type") != "FeatureCollection" or len(gj.get("features", [])) != len(part):
                raise SystemExit(f"batch {k // BATCH + 1}: not a FeatureCollection of {len(part)} features; nothing joined")
            feats.extend(gj["features"])
    finally:
        with open(os.path.join(d, "requests.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["url", "status", "bytes", "seconds", "retrieved_utc", "sha256", "saved_as", "content_type"])
            w.writerows(log_rows)
    joined = json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")).encode("utf-8")
    sha = hashlib.sha256(joined).hexdigest()
    path = os.path.join(d, "control_areas.geojson")
    with open(path, "wb") as f:
        f.write(joined)
    with open(os.path.join(d, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["url", "status", "bytes", "seconds", "retrieved_utc", "sha256", "saved_as", "content_type"])
        w.writerow([LAYER + "/query (" + str(len(log_rows) - 1) + " batches, requests.csv)", 200, len(joined), "",
                    log_rows[0][4], sha, os.path.basename(path), "application/geo+json (joined)"])
    print(f"{len(feats)} features, {len(joined):,} bytes sha256 {sha} -> {os.path.relpath(path, ROOT)}")
    return 0


def newest_raw():
    runs = sorted(glob.glob(os.path.join(RAW, "*", "control_areas.geojson")))
    if not runs:
        raise FileNotFoundError(f"no saved layer under {RAW}: run get first")
    path = runs[-1]
    with open(os.path.join(os.path.dirname(path), "manifest.csv"), encoding="utf-8") as f:
        man = list(csv.DictReader(f))[0]
    return path, man


def eia861_codes():
    """{BA ID: BA Code} from every saved EIA-861 Balancing_Authority file, newest year first; {code: set of IDs}."""
    import openpyxl
    pairs, years = {}, []
    files = sorted(glob.glob(os.path.join(ROOT, "warehouse", "raw", "eia861", "*", "*_f861*.zip")), key=os.path.basename)
    by_year = {}
    for z in files:
        y = os.path.basename(z)[-8:-4]
        by_year[y] = z
    for y in sorted(by_year, reverse=True):
        with zipfile.ZipFile(by_year[y]) as zf:
            names = [n for n in zf.namelist() if "balancing_authority" in n.lower() and n.lower().endswith(".xlsx")]
            if not names:
                continue
            ws = openpyxl.load_workbook(io.BytesIO(zf.read(names[0])), read_only=True).worksheets[0]
            rows = ws.iter_rows(values_only=True)
            head = [str(h).strip() if h is not None else "" for h in next(rows)]
            i, c = head.index("BA ID"), head.index("BA Code")
            for r in rows:
                if r[i] is None or not r[c]:
                    continue
                pairs.setdefault(int(r[i]), str(r[c]).strip())
            years.append(y)
    return pairs, years


def eia930_reference():
    import openpyxl
    f = sorted(glob.glob(os.path.join(ROOT, "warehouse", "raw", "eia930_reference", "*", "EIA930_Reference_Tables.xlsx")))[-1]
    rows = list(openpyxl.load_workbook(f, read_only=True)["BAs"].iter_rows(values_only=True))
    head = rows[0]
    return {r[0]: dict(zip(head, r)) for r in rows[1:] if r[0]}, f


def ring_area_km2(ring):
    """The area of a ring of (lon, lat) degrees on a sphere (the trapezoid rule on the sphere, absolute value)."""
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        s += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(s) * R_KM * R_KM / 2


def polys(geom):
    t, c = geom["type"], geom["coordinates"]
    return [c] if t == "Polygon" else c if t == "MultiPolygon" else []


def area_km2(geom):
    total = 0.0
    for p in polys(geom):
        rings = [[tuple(pt[:2]) for pt in r] for r in p]
        total += ring_area_km2(rings[0]) - sum(ring_area_km2(h) for h in rings[1:])
    return total


def clean_num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return ""
    return "" if f < 0 else f


def ms_date(v):
    try:
        return dt.datetime.fromtimestamp(int(v) / 1000, dt.timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return ""


def build(argv):
    from shapely.geometry import mapping, shape
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    path, man = newest_raw()
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    if man["sha256"] != hashlib.sha256(open(path, "rb").read()).hexdigest():
        raise SystemExit("the saved layer does not match its manifest's sha256")
    pairs, years = eia861_codes()
    ref, ref_file = eia930_reference()
    retrieved = man["retrieved_utc"]
    rows, feats, unmatched, seen = [], [], [], set()
    for ft in gj["features"]:
        p = ft["properties"]
        hid = int(p["ID"]) if str(p.get("ID", "")).strip().isdigit() else None
        code = pairs.get(hid) if hid is not None else None
        r930 = ref.get(code) if code else None
        g = shape(ft["geometry"])
        cen = g.representative_point() if not g.is_valid else g.centroid
        state, country = (p.get("STATE") or "").strip(), (p.get("COUNTRY") or "").strip()
        geo = f"US-{state}" if country == "USA" and len(state) == 2 else CANADA.get(state, "")
        eid = f"eia930:{code}" if r930 else f"hifld:control_area:{hid}"
        if not r930:
            unmatched.append({"id": hid, "name": p.get("NAME"), "eia861_code": code or None})
        else:
            seen.add(code)
        nparts = len(polys(ft["geometry"]))
        nvert = sum(len(r) for poly in polys(ft["geometry"]) for r in poly)
        rows.append({"entity_id": eid, "entity_type": "balancing_authority", "name": p.get("NAME"), "geo": geo,
                     "lat": round(cen.y, 5), "lon": round(cen.x, 5), "capacity_mw": "", "status": "", "status_date": "",
                     "operator": "", "source": SOURCE, "source_url": LAYER, "retrieved_at": retrieved,
                     "vintage": ms_date(p.get("SOURCEDATE")), "x_hifld_id": hid, "x_eia930_code": code or "",
                     "x_eia930_name": r930["BA Name"] if r930 else "", "x_region": r930["Region/Country Code"] if r930 else "",
                     "x_area_km2": round(area_km2(ft["geometry"]), 1), "x_parts": nparts, "x_vertices": nvert,
                     "x_source_date": ms_date(p.get("SOURCEDATE")), "x_val_date": ms_date(p.get("VAL_DATE")),
                     "x_year": p.get("YEAR") if str(p.get("YEAR", "")).isdigit() else "",
                     "x_peak_load_mw": clean_num(p.get("PEAK_LOAD")), "x_total_cap_mw": clean_num(p.get("TOTAL_CAP")),
                     "x_raw_sha256": man["sha256"]})
        if r930:
            feats.append((g, {"code": code, "name": r930["BA Name"], "region": r930["Region/Country Code"],
                              "source_id": str(hid), "area_km2": rows[-1]["x_area_km2"]}))
    us_bas = sorted(c for c, r in ref.items() if r.get("U.S. BA") == "Yes" and r.get("Region/Country Code") not in ("CAN", "MEX"))
    without = sorted(set(us_bas) - seen)
    dup = [r["entity_id"] for r in rows if sum(1 for q in rows if q["entity_id"] == r["entity_id"]) > 1]
    if dup:
        raise SystemExit(f"two polygons share an entity_id: {sorted(set(dup))}")
    # the table
    import pandas as pd
    out = pd.DataFrame(rows)[COLS]
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"hifld_control_areas_{run_id}.log"))
    log(f"  {len(rows)} polygons; {len(rows) - len(unmatched)} keyed to an EIA-930 code through EIA-861 years {years[-1]} to {years[0]}; "
        f"unmatched: {unmatched}; EIA-930 US authorities without a polygon: {without}")
    ip.write_snapshot(out, NAME, [
        "Energy Research Warehouse (ERW): the balancing authority areas of the United States, HIFLD's Control Areas layer, each polygon keyed to its EIA-930 code (session 8000, chain 501)",
        "Shape: entities (docs/datastandard.md v0), entity_type balancing_authority (Decision 80). entity_id eia930:<code>, or hifld:control_area:<HIFLD ID> where EIA-861 pairs the ID with no EIA-930 code. "
        "lat and lon: the polygon's centroid; geo: the authority's address state; x_area_km2: the polygon's area on a sphere. The polygons themselves are in the saved raw file and, simplified, in site/data/regions/ba_boundaries.json. Method: docs/methods/ba_boundaries.md.",
        f"Key: HIFLD's ID is EIA's entity identifier, paired with the EIA-930 code by EIA-861's Balancing_Authority files ({years[-1]} to {years[0]}); nothing matched by name. "
        f"{len(rows)} polygons, {len(unmatched)} without an EIA-930 code; EIA-930 authorities of the US without a polygon: {', '.join(without) or 'none'}.",
        f"Retrieved: {retrieved.replace('-', '').replace(':', '')} (UTC) by warehouse/connectors/hifld_control_areas.py get; built {run_id} (UTC) by its build",
        f"Run log: warehouse/output/logs/hifld_control_areas_{run_id}.log",
        f"Source: {SOURCE} Homeland Infrastructure Foundation-Level Data (HIFLD), Control Areas (ORNL, LANL, INL, NGA HSIP), as served by Penn State's PASDA: {LAYER}/query in batches (sha256 {man['sha256']}, saved at {os.path.relpath(path, ROOT).replace(os.sep, '/')}); "
        f"EIA-861 Balancing_Authority files (warehouse/raw/eia861); EIA-930 reference tables ({os.path.relpath(ref_file, ROOT).replace(os.sep, '/')})",
        "License: public (HIFLD's metadata: Limitations of use: None (Public Use); PASDA: free public access; EIA data are in the public domain)",
    ], log, COLS)
    ip.update_sources([dict(source=SOURCE, publisher="Homeland Infrastructure Foundation-Level Data (HIFLD), served by Penn State PASDA",
                            report="Control Areas (balancing authority areas), HIFLD open data layer, PASDA map service HIFLD_FEMA layer 26",
                            report_url=LAYER, document_list="docs/methods/ba_boundaries.md", license="public", tables=[NAME])])
    # the web file
    tol = 0.01
    while True:
        fc = []
        for g, props in sorted(feats, key=lambda x: x[1]["code"]):
            s = g.simplify(tol, preserve_topology=True)
            m = mapping(s)

            def rnd(c):
                if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
                    return [round(c[0], 3), round(c[1], 3)]
                return [rnd(x) for x in c]
            fc.append({"type": "Feature", "properties": props, "geometry": {"type": m["type"], "coordinates": rnd(m["coordinates"])}})
        doc = {"type": "FeatureCollection", "built": now(), "tables": [NAME], "method": "docs/methods/ba_boundaries.md", "license": "public",
               "source": "HIFLD Control Areas (ORNL, LANL, INL, NGA HSIP), served by Penn State PASDA", "source_url": LAYER,
               "retrieved_at": retrieved, "simplify_tolerance_deg": tol, "bas_without_polygon": without,
               "polygons_without_ba": [{"id": str(u["id"]), "name": u["name"]} for u in unmatched], "features": fc}
        text = json.dumps(doc, separators=(",", ":"))
        if len(text.encode("utf-8")) < WEB_LIMIT:
            break
        tol *= 2
    site = os.path.join(a.out_dir, "site", "ba_boundaries.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(site), exist_ok=True)
    with open(site, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    log(f"  web file {os.path.relpath(site, ROOT)}: {len(text):,} bytes at tolerance {tol} degrees, {len(fc)} features")
    log.close()
    print(f"{NAME}: {len(out)} rows ({len(unmatched)} without an EIA-930 code); web file {len(text):,} bytes, tolerance {tol}; "
          f"EIA-930 authorities without a polygon: {without}")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("get", "build"):
        print(__doc__)
        return 2
    return get(argv[1:]) if argv[0] == "get" else build(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
