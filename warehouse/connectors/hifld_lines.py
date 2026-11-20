#!/usr/bin/env python3
"""Two line layers for the project map: HIFLD's electric transmission lines of 230 kV and above, and EIA's hydrocarbon
gas liquids (HGL) pipelines, both as Penn State PASDA serves them (session 8014, chain 581 part D).

Energy Research Warehouse (ERW) connector. Two entities tables, warehouse/output/hifld_transmission_lines.csv and
warehouse/output/eia_hgl_pipelines.csv, and two web files under site/data/map_layers/ (each under 2 MB). Method:
docs/methods/map_layers.md.

    python warehouse/connectors/hifld_lines.py get      # the two layers as GeoJSON, in batches, to warehouse/raw (no lock)
    python warehouse/connectors/hifld_lines.py build    # the tables and the web files from the saved copies (data lock)
    python warehouse/connectors/hifld_lines.py build --out-dir DIR   # a trial: all under DIR

THE LAYERS. Penn State's PASDA (Pennsylvania Spatial Data Access, "free public access") serves, in its map service
HIFLD_FEMA (https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer), the national layers of
the retired HIFLD open catalog, among them layer 178 "Transmission_Lines" (HIFLD's Electric Power Transmission Lines,
ORNL and NGA HSIP; HIFLD's metadata: public use) and layer 47 "HGL_Pipelines_US_EIA" (EIA's layer, "Updated January
2020", copyright text "U.S. Energy Information Administration"; EIA's data are in the public domain). That host's
robots file answers 404 (no rule), read on 20 November 2026 before any other request (runs/c581/probe/probe.csv).

EIA's own layers of natural gas, crude oil and petroleum product pipelines, LNG terminals, refineries and underground
storage are served from services7.arcgis.com, whose robots file answers 403: the stricter reading is kept (as session
180b did), so they are not read here. HIFLD's compressor stations and substations are not in PASDA's service.

THE TABLES (entities). hifld_transmission_lines: entity_type transmission_line, entity_id hifld:transmission_line:<ID>,
name "<SUB_1> to <SUB_2>" where HIFLD names both ends (else blank), operator OWNER as printed (NOT AVAILABLE left blank),
status from STATUS (IN SERVICE operating, UNDER CONSTRUCTION under_construction, else blank; x_status keeps HIFLD's
word), lat and lon the line's midpoint, x_voltage_kv (VOLTAGE; -999999 left blank), x_volt_class, x_type,
x_inferred, x_sub_1, x_sub_2, x_length_km (on a sphere), x_source, x_source_date, x_val_date, x_raw_sha256. Only lines
whose VOLTAGE is 230 or more are asked for. eia_hgl_pipelines: entity_type pipeline, entity_id
eia:hgl_pipeline:<OBJECTID>, name Pipename, operator Opername, x_length_km, x_raw_sha256. A line's geometry is kept in
the saved raw file and, simplified, in the web file, since no table shape holds a line (Decision 80's rule for a polygon).

THE WEB FILES. site/data/map_layers/transmission_230kv.json and hgl_pipelines.json: each line simplified (Douglas-Peucker,
shapely), coordinates rounded to 3 decimals, the tolerance doubled from 0.005 degrees until the file is under 2 MB; in
columns (fields, rows, names, paths), since GeoJSON's keys alone would fill the limit for 10,692 lines.
"""

import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import math
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

UA = "ERW research project, github.com/SamuelEnrique/erw"
HOST = "mapservices.pasda.psu.edu"
SERVICE = f"https://{HOST}/server/rest/services/pasda/HIFLD_FEMA/MapServer"
RAW = os.path.join(ROOT, "warehouse", "raw", "hifld_lines")
SITE_DIR = os.path.join(ROOT, "site", "data", "map_layers")
MAX_BYTES = 200 * 1024 ** 2
GAP = 5
WEB_LIMIT = 2 * 1024 ** 2
R_KM = 6371.0088
LAYERS = {
    "transmission": {"layer": 178, "where": "VOLTAGE>=230", "batch": 400, "table": "hifld_transmission_lines", "source": "hifld:transmission_lines",
                     "web": "transmission_230kv.json", "words": "HIFLD Electric Power Transmission Lines (ORNL, NGA HSIP), 230 kV and above, served by Penn State PASDA"},
    "hgl": {"layer": 47, "where": "1=1", "batch": 400, "table": "eia_hgl_pipelines", "source": "eia:hgl_pipelines",
            "web": "hgl_pipelines.json", "words": "U.S. Energy Information Administration, HGL Pipelines (updated January 2020), served by Penn State PASDA"},
}
TCOLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source", "source_url",
         "retrieved_at", "vintage", "x_hifld_id", "x_voltage_kv", "x_volt_class", "x_type", "x_inferred", "x_status", "x_sub_1", "x_sub_2", "x_length_km",
         "x_source", "x_source_date", "x_val_date", "x_raw_sha256"]
STATUS = {"IN SERVICE": "operating", "UNDER CONSTRUCTION": "under_construction"}   # HIFLD's word, kept in x_status (Decision 82)
HCOLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source", "source_url",
         "retrieved_at", "vintage", "x_objectid", "x_length_km", "x_raw_sha256"]


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(argv):
    """Each layer's object ids (with its where clause), then its features as GeoJSON in batches (a range of object ids
    added to the where clause), GAP seconds apart. Each answer is saved as it came and logged; a layer's batches are joined only when every one is a GeoJSON
    FeatureCollection with the features asked for."""
    from urllib.parse import quote
    if ip.paused_host(HOST):
        print(f"refused: {HOST} is a paused publisher's host")
        return 1
    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(RAW, run)
    os.makedirs(d, exist_ok=True)
    log_rows = []

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

    manifest = []
    try:
        for key, L in LAYERS.items():
            base = f"{SERVICE}/{L['layer']}"
            st, body = fetch(f"{base}/query?where={quote(L['where'])}&returnIdsOnly=true&f=json", f"{key}_object_ids.json")
            ans = json.loads(body) if st == 200 else {}
            ids = sorted(ans.get("objectIds") or [])
            oid = ans.get("objectIdFieldName") or "OBJECTID"
            if not ids:
                raise SystemExit(f"{key}: no object ids in the answer")
            feats = []
            for k in range(0, len(ids), L["batch"]):
                time.sleep(GAP)
                part = ids[k:k + L["batch"]]
                # a range of the layer's own object ids within the where clause: the service answers 404 to a list of
                # 400 ids in the address (20 November 2026); the range holds exactly the batch's ids, as the ids are sorted
                cond = f"({L['where']}) AND {oid}>={part[0]} AND {oid}<={part[-1]}"
                url = f"{base}/query?where={quote(cond)}&outFields=*&returnGeometry=true&outSR=4326&f=geojson"
                st, body = fetch(url, f"{key}_batch_{k // L['batch'] + 1:03d}.geojson")
                try:
                    gj = json.loads(body)
                except ValueError:
                    raise SystemExit(f"{key} batch {k // L['batch'] + 1} is not JSON (status {st}); nothing joined")
                if gj.get("type") != "FeatureCollection" or len(gj.get("features", [])) != len(part):
                    raise SystemExit(f"{key} batch {k // L['batch'] + 1}: not a FeatureCollection of {len(part)} features; nothing joined")
                feats.extend(gj["features"])
            joined = json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")).encode("utf-8")
            sha = hashlib.sha256(joined).hexdigest()
            name = f"{key}.geojson"
            with open(os.path.join(d, name), "wb") as f:
                f.write(joined)
            manifest.append([f"{base}/query where {L['where']} ({-(-len(ids) // L['batch'])} batches, requests.csv)", 200, len(joined), "",
                             log_rows[-1][4], sha, name, "application/geo+json (joined)"])
            print(f"{key}: {len(feats)} features, {len(joined):,} bytes sha256 {sha}")
            time.sleep(GAP)
    finally:
        with open(os.path.join(d, "requests.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["url", "status", "bytes", "seconds", "retrieved_utc", "sha256", "saved_as", "content_type"])
            w.writerows(log_rows)
    with open(os.path.join(d, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["url", "status", "bytes", "seconds", "retrieved_utc", "sha256", "saved_as", "content_type"])
        w.writerows(manifest)
    return 0


def newest_raw():
    runs = sorted(glob.glob(os.path.join(RAW, "*", "manifest.csv")))
    if not runs:
        raise FileNotFoundError(f"no saved layers under {RAW}: run get first")
    d = os.path.dirname(runs[-1])
    with open(runs[-1], encoding="utf-8") as f:
        man = {r["saved_as"].split(".")[0]: r for r in csv.DictReader(f)}
    for key in LAYERS:
        if key not in man:
            raise SystemExit(f"the newest saved run {d} has no {key} layer")
        if man[key]["sha256"] != hashlib.sha256(open(os.path.join(d, man[key]["saved_as"]), "rb").read()).hexdigest():
            raise SystemExit(f"the saved {key} layer does not match its manifest's sha256")
    return d, man


def length_km(geom):
    """A line's length on a sphere of radius R_KM, summed over its parts (haversine between vertices)."""
    parts = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
    s = 0.0
    for p in parts:
        for (x1, y1), (x2, y2) in zip(p[:-1], p[1:]):
            p1, p2 = math.radians(y1), math.radians(y2)
            a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(x2 - x1) / 2) ** 2
            s += 2 * R_KM * math.asin(min(1.0, math.sqrt(a)))
    return s


def ms_date(v):
    try:
        return dt.datetime.fromtimestamp(int(v) / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d") if v not in (None, "") else ""
    except (TypeError, ValueError, OSError):
        return ""


def text(v):
    s = "" if v is None else str(v).strip()
    return "" if s.upper() in ("NOT AVAILABLE", "NA", "N/A", "-999999") else s


def web_file(feats, key, retrieved, path, extra):
    """The simplified lines under WEB_LIMIT bytes, in columns (a GeoJSON feature a line would spend most of the limit on
    its keys): `fields` names each row's values, `rows` one list a line, text values given as an index into `names`,
    `paths` one list a line of its parts, each part a flat list x0, y0, x1, y1, ... rounded to 3 decimals. The
    tolerance is doubled from 0.005 degrees; past 0.32 degrees the build stops (no file is better than a false one)."""
    from shapely.geometry import mapping, shape
    fields = list(feats[0][1].keys()) if feats else []
    names, index = [], {}

    def name_of(v):
        if v is None or v == "":
            return None
        if v not in index:
            index[v] = len(names)
            names.append(v)
        return index[v]
    rows = [[(name_of(v) if isinstance(v, str) and k != "id" else v) for k, v in props.items()] for _, props in feats]
    shapes = [shape(g) for g, _ in feats]
    tol = 0.005
    while True:
        paths = []
        for sh in shapes:
            m = mapping(sh.simplify(tol, preserve_topology=False))
            parts = m["coordinates"] if m["type"] == "MultiLineString" else [m["coordinates"]]
            paths.append([[round(c, 3) for pt in part for c in pt[:2]] for part in parts])
        doc = {"built": now(), "tables": [LAYERS[key]["table"]], "method": "docs/methods/map_layers.md", "license": "public",
               "source": LAYERS[key]["words"], "source_url": f"{SERVICE}/{LAYERS[key]['layer']}", "retrieved_at": retrieved,
               "simplify_tolerance_deg": tol, **extra, "fields": fields, "text_fields": [k for k in fields if k != "id" and any(isinstance(p[k], str) for _, p in feats)],
               "names": names, "rows": rows, "paths": paths}
        out = json.dumps(doc, separators=(",", ":"))
        if len(out.encode("utf-8")) < WEB_LIMIT:
            break
        tol *= 2
        if tol > 0.32:
            raise SystemExit(f"{key}: no tolerance up to 0.32 degrees brings the web file under {WEB_LIMIT} bytes ({len(out):,} at {tol / 2})")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    return len(out), tol, len(paths)


def mid(geom):
    from shapely.geometry import shape
    g = shape(geom)
    p = g.interpolate(0.5, normalized=True) if g.geom_type == "LineString" else g.representative_point()
    return round(p.y, 5), round(p.x, 5)


def build(argv):
    import pandas as pd
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    d, man = newest_raw()
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"hifld_lines_{run_id}.log"))
    site_dir = os.path.join(a.out_dir, "site") if a.out_dir else SITE_DIR
    # transmission
    m = man["transmission"]
    gj = json.load(open(os.path.join(d, m["saved_as"]), encoding="utf-8"))
    rows, feats = [], []
    for ft in gj["features"]:
        p, g = ft["properties"], ft["geometry"]
        if not g:
            continue
        hid = text(p.get("ID"))
        kv = p.get("VOLTAGE")
        kv = kv if isinstance(kv, (int, float)) and kv > 0 else None
        lat, lon = mid(g)
        s1, s2 = text(p.get("SUB_1")), text(p.get("SUB_2"))
        rows.append({"entity_id": f"hifld:transmission_line:{hid}", "entity_type": "transmission_line", "name": f"{s1} to {s2}" if s1 and s2 else "",
                     "geo": "", "lat": lat, "lon": lon, "capacity_mw": "", "status": STATUS.get(text(p.get("STATUS")).upper(), ""), "status_date": "",
                     "operator": text(p.get("OWNER")), "source": LAYERS["transmission"]["source"], "source_url": f"{SERVICE}/178",
                     "retrieved_at": m["retrieved_utc"], "vintage": ms_date(p.get("SOURCEDATE")), "x_hifld_id": hid,
                     "x_voltage_kv": kv if kv is not None else "", "x_volt_class": text(p.get("VOLT_CLASS")), "x_type": text(p.get("TYPE")),
                     "x_inferred": text(p.get("INFERRED")), "x_status": text(p.get("STATUS")), "x_sub_1": s1, "x_sub_2": s2, "x_length_km": round(length_km(g), 2),
                     "x_source": text(p.get("SOURCE")), "x_source_date": ms_date(p.get("SOURCEDATE")), "x_val_date": ms_date(p.get("VAL_DATE")),
                     "x_raw_sha256": m["sha256"]})
        feats.append((g, {"id": hid, "kv": kv, "owner": text(p.get("OWNER")) or None, "from": s1 or None, "to": s2 or None,
                          "km": round(rows[-1]["x_length_km"], 1)}))
    dup = pd.Series([r["entity_id"] for r in rows]).duplicated()
    if dup.any():
        raise SystemExit(f"two transmission lines share an entity_id: {sorted(set(r['entity_id'] for r, x in zip(rows, dup) if x))[:5]}")
    t = pd.DataFrame(rows)[TCOLS]
    ip.write_snapshot(t, "hifld_transmission_lines", [
        "Energy Research Warehouse (ERW): electric transmission lines of 230 kV and above, HIFLD's Electric Power Transmission Lines layer (session 8014, chain 581 part D)",
        "Shape: entities (docs/datastandard.md v0), entity_type transmission_line (Decision 82). entity_id hifld:transmission_line:<HIFLD ID>; lat and lon: the line's midpoint; "
        "operator: HIFLD's OWNER as printed; x_voltage_kv: HIFLD's VOLTAGE (a code below zero left blank); x_length_km on a sphere. The lines themselves are in the saved raw file and, simplified, in site/data/map_layers/transmission_230kv.json. Method: docs/methods/map_layers.md.",
        f"Retrieved: {m['retrieved_utc'].replace('-', '').replace(':', '')} (UTC) by warehouse/connectors/hifld_lines.py get; built {run_id} (UTC) by its build",
        f"Run log: warehouse/output/logs/hifld_lines_{run_id}.log",
        f"Source: hifld:transmission_lines Homeland Infrastructure Foundation-Level Data (HIFLD), Electric Power Transmission Lines (ORNL, NGA HSIP), as served by Penn State's PASDA: {SERVICE}/178/query where VOLTAGE>=230, in batches (sha256 {m['sha256']}, saved at {os.path.relpath(os.path.join(d, m['saved_as']), ROOT).replace(os.sep, '/')})",
        "License: public (HIFLD's metadata: public use; PASDA: free public access)",
    ], log, TCOLS)
    n1, tol1, f1 = web_file(feats, "transmission", m["retrieved_utc"], os.path.join(site_dir, LAYERS["transmission"]["web"]),
                            {"unit": "kV", "lines": len(feats), "km": round(sum(r["x_length_km"] for r in rows), 0)})
    log(f"  hifld_transmission_lines: {len(t)} rows; web file {n1:,} bytes at tolerance {tol1}, {f1} features")
    # HGL pipelines
    m = man["hgl"]
    gj = json.load(open(os.path.join(d, m["saved_as"]), encoding="utf-8"))
    rows, feats = [], []
    for ft in gj["features"]:
        p, g = ft["properties"], ft["geometry"]
        if not g:
            continue
        oid = p.get("OBJECTID")
        lat, lon = mid(g)
        rows.append({"entity_id": f"eia:hgl_pipeline:{oid}", "entity_type": "pipeline", "name": text(p.get("Pipename")), "geo": "", "lat": lat, "lon": lon,
                     "capacity_mw": "", "status": "", "status_date": "", "operator": text(p.get("Opername")), "source": LAYERS["hgl"]["source"],
                     "source_url": f"{SERVICE}/47", "retrieved_at": m["retrieved_utc"], "vintage": "2020-01", "x_objectid": oid,
                     "x_length_km": round(length_km(g), 2), "x_raw_sha256": m["sha256"]})
        feats.append((g, {"id": str(oid), "name": rows[-1]["name"] or None, "operator": rows[-1]["operator"] or None, "km": rows[-1]["x_length_km"]}))
    h = pd.DataFrame(rows)[HCOLS]
    ip.write_snapshot(h, "eia_hgl_pipelines", [
        "Energy Research Warehouse (ERW): hydrocarbon gas liquids (HGL) pipelines of the United States, EIA's HGL Pipelines layer (session 8014, chain 581 part D)",
        "Shape: entities (docs/datastandard.md v0), entity_type pipeline (Decision 82). entity_id eia:hgl_pipeline:<OBJECTID>; name: EIA's Pipename; operator: EIA's Opername; lat and lon: the line's midpoint; "
        "x_length_km on a sphere. EIA: interstate trunk lines and selected intrastate lines, from public sources of varying scale and accuracy, updated January 2020. The lines are in the saved raw file and, simplified, in site/data/map_layers/hgl_pipelines.json. Method: docs/methods/map_layers.md.",
        f"Retrieved: {m['retrieved_utc'].replace('-', '').replace(':', '')} (UTC) by warehouse/connectors/hifld_lines.py get; built {run_id} (UTC) by its build",
        f"Run log: warehouse/output/logs/hifld_lines_{run_id}.log",
        f"Source: eia:hgl_pipelines U.S. Energy Information Administration, HGL Pipelines (updated January 2020), as served by Penn State's PASDA: {SERVICE}/47/query, in batches (sha256 {m['sha256']}, saved at {os.path.relpath(os.path.join(d, m['saved_as']), ROOT).replace(os.sep, '/')})",
        "License: public (EIA's data are in the public domain; PASDA: free public access)",
    ], log, HCOLS)
    n2, tol2, f2 = web_file(feats, "hgl", m["retrieved_utc"], os.path.join(site_dir, LAYERS["hgl"]["web"]),
                            {"unit": "km", "lines": len(feats), "km": round(sum(r["x_length_km"] for r in rows), 0)})
    log(f"  eia_hgl_pipelines: {len(h)} rows; web file {n2:,} bytes at tolerance {tol2}, {f2} features")
    ip.update_sources([
        dict(source=LAYERS["transmission"]["source"], publisher="Homeland Infrastructure Foundation-Level Data (HIFLD), served by Penn State PASDA",
             report="Electric Power Transmission Lines, HIFLD open data layer, PASDA map service HIFLD_FEMA layer 178", report_url=f"{SERVICE}/178",
             document_list="docs/methods/map_layers.md", license="public", tables=["hifld_transmission_lines"]),
        dict(source=LAYERS["hgl"]["source"], publisher="U.S. Energy Information Administration, served by Penn State PASDA",
             report="HGL Pipelines (updated January 2020), PASDA map service HIFLD_FEMA layer 47", report_url=f"{SERVICE}/47",
             document_list="docs/methods/map_layers.md", license="public", tables=["eia_hgl_pipelines"])])
    log.close()
    print(f"hifld_transmission_lines: {len(t)} rows, web {n1:,} bytes (tolerance {tol1}); eia_hgl_pipelines: {len(h)} rows, web {n2:,} bytes (tolerance {tol2})")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in ("get", "build"):
        print(__doc__)
        return 2
    return get(argv[1:]) if argv[0] == "get" else build(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
