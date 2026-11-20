#!/usr/bin/env python3
"""The natural resource map's layers as a table, and the coal fields as a new layer (session 8006, chain 501 step D1).

Energy Research Warehouse (ERW). Two outputs:

    resource_layer_features   one entities table (entity_type resource, Decision 81): every cell, site or area of each
                              layer of the page "Where the resources are" that describes a resource in the ground, the
                              sun or the wind (not built capacity), with its value, unit, layer and publisher; and the
                              USGS coal fields
    site/data/resources/coal_fields.json   the coal fields of the conterminous United States, simplified (under 2 MB)

    python warehouse/derived/resource_tables.py                 # the table (data lock) and the coal fields' web file
    python warehouse/derived/resource_tables.py --out-dir DIR   # a trial

THE LAYERS read (site/data/resources/manifest.json and layers/, written by warehouse/connectors/resource_layers.py from
each publisher's file, whose address, terms and sha256 the manifest records): wind_speed_100m, solar_ghi, solar_dni
(grids, the finest level of each, 0.05 degrees, the lower 48), wind_capacity_factor, geothermal_hydrothermal_sites,
hydropower_npd (sites), geothermal_hydrothermal_favorability, geothermal_egs_favorability, oil_gas_basins,
oil_gas_plays, hydropower_nsd, biomass (areas). A grid cell's value is the layer's value as resource_layers.py reduced
the publisher's raster (the mean of the source cells in it; the method of that connector); a site's or an area's is the
publisher's own field the manifest names. Left out: offshore_wind_leases and offshore_wind_planning_areas (rights to
build, not a resource) and the Alaska and Hawaii grids (kept in their web files).

THE COAL FIELDS: U.S. Geological Survey Open-File Report 2012-1205 (East, J.A., 2013, Coal fields of the conterminous
United States, National Coal Resource Assessment updated version), its GIS.zip, shapefile "Updated Coal
Fields/Coal_Fields.shp": 602 polygons with province, field name, age and rank, NAD83. Public domain (USGS). One row a
polygon; the web file joins nothing and simplifies each polygon (Douglas-Peucker with topology kept, tolerance doubled
from 0.005 degrees until the file is under 2 MB).

Nothing is filled, smoothed or estimated. Method: docs/methods/resource_layers_table.md.
"""

import argparse
import base64
import csv
import datetime as dt
import glob
import hashlib
import json
import math
import os
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "resource_layer_features"
SOURCE = "erw:resource_layer_features"
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
LAYERS_DIR = os.path.join(ROOT, "site", "data", "resources", "layers")
COAL_RAW = os.path.join(ROOT, "warehouse", "raw", "usgs_coal_fields")
COAL_SHP = "GIS/Updated Coal Fields/Coal_Fields.shp"
COAL_URL = "https://pubs.usgs.gov/of/2012/1205/Downloads/GIS.zip"
COAL_PAGE = "https://pubs.usgs.gov/of/2012/1205/"
COAL_WEB = os.path.join(ROOT, "site", "data", "resources", "coal_fields.json")
WEB_LIMIT = 2 * 1024 ** 2
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/resource_layers_table.md"
TAKEN = ["wind_speed_100m", "solar_ghi", "solar_dni", "wind_capacity_factor", "geothermal_hydrothermal_sites", "hydropower_npd",
         "geothermal_hydrothermal_favorability", "geothermal_egs_favorability", "oil_gas_basins", "oil_gas_plays",
         "hydropower_nsd", "biomass"]
LEFT_OUT = {"offshore_wind_leases": "rights to build, not a resource", "offshore_wind_planning_areas": "areas planned for leases, not a resource"}
COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source",
        "source_url", "retrieved_at", "vintage", "x_layer", "x_kind", "x_value", "x_unit", "x_value_label", "x_publisher",
        "x_cell_deg", "x_area_km2", "x_extra", "x_source_sha256"]
R_KM = 6371.0088


def decode_grid(obj):
    raw = np.frombuffer(base64.b64decode(obj["values"]), dtype="<u2").reshape(obj["nrows"], obj["ncols"])
    v = raw.astype("float64") * obj["scale"] + obj["offset"]
    v[raw == obj["nodata"]] = np.nan
    return v


def ring_area_km2(ring):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        s += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(s) * R_KM * R_KM / 2


def geom_area_km2(geom):
    t, c = geom["type"], geom["coordinates"]
    polys = [c] if t == "Polygon" else c if t == "MultiPolygon" else []
    return sum(ring_area_km2([tuple(p[:2]) for p in poly[0]]) - sum(ring_area_km2([tuple(p[:2]) for p in h]) for h in poly[1:]) for poly in polys)


def centroid(geom):
    from shapely.geometry import shape
    g = shape(geom)
    p = g.centroid if g.is_valid else g.representative_point()
    return round(p.y, 5), round(p.x, 5)


def layer_rows(layer):
    lid, kind = layer["id"], layer["kind"]
    base = dict(entity_type="resource", status="", status_date="", operator="", capacity_mw="", source=SOURCE,
                source_url=layer["source_url"], retrieved_at=layer["retrieved_at_utc"], vintage=str(layer.get("vintage") or ""),
                x_layer=lid, x_unit=layer.get("unit") or "", x_value_label=layer.get("value_label") or "",
                x_publisher=layer.get("publisher") or "", x_source_sha256=layer.get("source_sha256") or "")
    rows = []
    if kind == "grid":
        lv = layer["levels"][-1]
        g = json.load(open(os.path.join(LAYERS_DIR, lv["file"]), encoding="utf-8"))
        v = decode_grid(g)
        rr, cc = np.nonzero(np.isfinite(v))
        for r, c in zip(rr, cc):
            lat = g["lat0"] - (r + 0.5) * g["dlat"]
            lon = g["lon0"] + (c + 0.5) * g["dlon"]
            rows.append({**base, "entity_id": f"resource:{lid}:r{r}c{c}", "name": f"{lid} cell r{r} c{c}", "geo": "US",
                         "lat": round(lat, 4), "lon": round(lon, 4), "x_kind": "grid cell", "x_value": round(float(v[r, c]), 6),
                         "x_cell_deg": g["dlon"], "x_area_km2": "", "x_extra": ""})
    elif kind == "points":
        d = json.load(open(os.path.join(LAYERS_DIR, layer["file"]), encoding="utf-8"))
        cols = d["columns"]
        for i, row in enumerate(d["rows"]):
            x = dict(zip(cols, row))
            extra = {k: x[k] for k in cols if k not in ("lon", "lat", "name", "value")}
            rows.append({**base, "entity_id": f"resource:{lid}:{i}", "name": str(x.get("name") or f"{lid} {i}"), "geo": "US",
                         "lat": x["lat"], "lon": x["lon"], "x_kind": "site", "x_value": x.get("value"), "x_cell_deg": "",
                         "x_area_km2": "", "x_extra": json.dumps(extra, separators=(",", ":"), ensure_ascii=False)})
    else:
        d = json.load(open(os.path.join(LAYERS_DIR, layer["file"]), encoding="utf-8"))
        for i, ft in enumerate(d["features"]):
            p = ft["properties"]
            lat, lon = centroid(ft["geometry"])
            extra = {k: v for k, v in p.items() if k not in ("name", "value", "kind", "value_unit")}
            rows.append({**base, "entity_id": f"resource:{lid}:{i}", "name": str(p.get("name") or f"{lid} {i}"), "geo": "US",
                         "lat": lat, "lon": lon, "x_kind": p.get("kind") or "area", "x_value": p.get("value"),
                         "x_unit": p.get("value_unit") or base["x_unit"], "x_cell_deg": "",
                         "x_area_km2": round(geom_area_km2(ft["geometry"]), 1) if ft["geometry"] else "",
                         "x_extra": json.dumps(extra, separators=(",", ":"), ensure_ascii=False)})
    return rows


def coal(retrieved_dir):
    import geopandas as gpd
    from shapely.geometry import mapping
    zips = sorted(glob.glob(os.path.join(COAL_RAW, "*", "GIS.zip")))
    if not zips:
        raise FileNotFoundError(f"no saved GIS.zip under {COAL_RAW}")
    zp = zips[-1]
    man = list(csv.DictReader(open(os.path.join(os.path.dirname(zp), "manifest.csv"), encoding="utf-8")))
    m = [r for r in man if r["saved_as"] == "GIS.zip"][0]
    if hashlib.sha256(open(zp, "rb").read()).hexdigest() != m["sha256"]:
        raise SystemExit("the saved GIS.zip does not match its manifest")
    g = gpd.read_file(f"zip://{zp}!{COAL_SHP}").to_crs(4326)
    rows, feats = [], []
    for i, r in g.reset_index(drop=True).iterrows():
        geom = mapping(r.geometry)
        c = r.geometry.centroid if r.geometry.is_valid else r.geometry.representative_point()
        props = {"province": r["PROVINCE"], "name": r["NAME"], "age": r["AGE"], "rank": r["RANK"]}
        rows.append(dict(entity_id=f"resource:coal_fields:{i}", entity_type="resource", name=str(r["NAME"]), geo="US", lat=round(c.y, 5),
                         lon=round(c.x, 5), capacity_mw="", status="", status_date="", operator="", source="usgs:of2012_1205_coal_fields",
                         source_url=COAL_URL, retrieved_at=m["retrieved_utc"], vintage="2013", x_layer="coal_fields", x_kind="coal field",
                         x_value="", x_unit="", x_value_label="coal field (province, age and rank as USGS gives them)",
                         x_publisher="U.S. Geological Survey", x_cell_deg="", x_area_km2=round(geom_area_km2(geom), 1),
                         x_extra=json.dumps(props, separators=(",", ":"), ensure_ascii=False), x_source_sha256=m["sha256"]))
        feats.append((r.geometry, props, rows[-1]["x_area_km2"]))
    return rows, feats, m


def coal_web(feats, m, path):
    from shapely.geometry import mapping
    tol = 0.005
    while True:
        fc = []
        for geom, props, area in feats:
            s = mapping(geom.simplify(tol, preserve_topology=True))

            def rnd(c):
                if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
                    return [round(c[0], 3), round(c[1], 3)]
                return [rnd(x) for x in c]
            fc.append({"type": "Feature", "properties": {**props, "area_km2": area}, "geometry": {"type": s["type"], "coordinates": rnd(s["coordinates"])}})
        doc = {"type": "FeatureCollection", "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "tables": [NAME], "method": "docs/methods/resource_layers_table.md", "license": "public",
               "source": "U.S. Geological Survey Open-File Report 2012-1205: Coal fields of the conterminous United States (East, 2013)",
               "source_url": COAL_PAGE, "retrieved_at": m["retrieved_utc"], "source_sha256": m["sha256"],
               "simplify_tolerance_deg": tol, "features": fc}
        text = json.dumps(doc, separators=(",", ":"), allow_nan=False)
        if len(text.encode("utf-8")) < WEB_LIMIT:
            break
        tol *= 2
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return len(text), tol


MAP_LAYER = os.path.join(ROOT, "site", "data", "resources", "layers", "coal_fields.json")
MANIFEST_ADDED = os.path.join(ROOT, "site", "data", "resources", "manifest_added.json")
USGS_TERMS = {"terms_url": "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
              "terms_quote": "USGS-authored or produced data and information are considered to be in the U.S. Public Domain. [...] When using "
                             "information from USGS information products, publications, or websites, we ask that proper credit be given.",
              "terms_file": "usgs/terms/usgs_copyrights_and_credits.html",
              "terms_sha256": "be68d363d1ab447ea0bea87e436ad6c8614e0f5dc4e17643e2393f7e18504820"}


def coal_map_layer(feats, m, layer_path, manifest_path):
    """Session 8009 (data request 542 of the portable laptop): the coal fields in the form the resource map's layer files
    have (properties name, kind, value, value_unit, the source's own fields beside them), written to layers/, and their
    entry in manifest_added.json, a new file in the manifest's form, so the map draws the layer without manifest.json
    changing (chain 501's rule: no existing page file changes)."""
    from shapely.geometry import mapping
    fc, lons, lats = [], [], []
    # session 8011 (data request 552 of the portable laptop): the value in square miles, the unit of the map's other
    # outlines (EIA's basins and plays), with the square kilometres kept beside it as AREA_KM2
    KM2_PER_MI2 = 2.589988110336
    for geom, props, area in feats:
        s = mapping(geom.simplify(0.01, preserve_topology=True))

        def rnd(c):
            if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
                lons.append(c[0]); lats.append(c[1])
                return [round(c[0], 3), round(c[1], 3)]
            return [rnd(x) for x in c]
        fc.append({"type": "Feature", "properties": {"name": f"{props['name']} ({props['province']})", "kind": "coal field",
                                                     "value": round(area / KM2_PER_MI2, 1), "value_unit": "square miles", "AREA_KM2": area, "PROVINCE": props["province"],
                                                     "NAME": props["name"], "AGE": props["age"], "RANK": props["rank"]},
                   "geometry": {"type": s["type"], "coordinates": rnd(s["coordinates"])}})
    text = json.dumps({"type": "FeatureCollection", "features": fc}, separators=(",", ":"), allow_nan=False)
    os.makedirs(os.path.dirname(layer_path), exist_ok=True)
    with open(layer_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    vals = [round(p[2] / KM2_PER_MI2, 1) for p in feats]
    entry = {"id": "coal_fields", "group": "coal", "title": "Coal fields", "kind": "shapes",
             "measure": "Where coal lies in the ground in the lower 48, by field, with its age and rank, as the U.S. Geological Survey maps it.",
             "source_url": COAL_URL, **USGS_TERMS, "retrieved_at_utc": m["retrieved_utc"], "source_file": "usgs_coal_fields/GIS.zip",
             "source_bytes": int(m["bytes"]), "source_sha256": m["sha256"], "unit": "square miles",
             "value_label": "area of the coal field (computed on a sphere from the source's polygon, square kilometres over 2.589988110336; AREA_KM2 holds the square kilometres)",
             "publisher": "U.S. Geological Survey (USGS)",
             "source_title": "Coal fields of the conterminous United States, National Coal Resource Assessment updated version (Open-File Report 2012-1205, East 2013), Updated Coal Fields/Coal_Fields.shp",
             "vintage": "2013", "extent": "contiguous United States", "source_resolution": "polygons, the report's map at 1:5,000,000",
             "reduction": "each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one feature at a time); coordinates to 3 decimals; no feature dropped",
             "file": "coal_fields.json", "bytes": len(text), "features": len(fc),
             "bounds": [round(min(lons), 3), round(min(lats), 3), round(max(lons), 3), round(max(lats), 3)],
             "legend": {"kinds": ["coal field"]},
             "stats": {"n": len(vals), "min": min(vals), "mean": sum(vals) / len(vals), "max": max(vals)},
             "hover_fields": ["PROVINCE", "NAME", "AGE", "RANK"],
             "acknowledgment": "Source: U.S. Geological Survey, Open-File Report 2012-1205 (2013)",
             "notes_for_method": "An outline of where coal fields lie and their rank, not a measure of coal in place or of what can be mined.",
             "method_note": "docs/methods/resource_layers_table.md"}
    doc = {"built_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "note": "Layers added after manifest.json, in its form; manifest.json is not changed (chain 501). A page reads both.",
           "layers": [entry],
           "missing": [{"id": "uranium_deposits", "group": "uranium", "title": "Uranium deposits",
                        "reason": "Not fetched: USGS's mineral deposit databases are served from mrdata.usgs.gov, whose robots file disallows every path to every agent, and from ScienceBase, whose robots file disallows Claude by name; EIA's atlas lists no uranium deposit layer."},
                       {"id": "critical_mineral_deposits", "group": "critical minerals", "title": "Critical mineral deposits",
                        "reason": "Not fetched: the same two USGS hosts; the warehouse's usgs_mcs_critical_minerals is national statistics, not places."}]}
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    return len(text)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--map-only", action="store_true", help="write only the map's layer file and manifest_added.json (no table)")
    a = ap.parse_args(argv)
    if a.map_only:
        _, feats, m = coal(None)
        print("the map's layer file:", coal_map_layer(feats, m, MAP_LAYER, MANIFEST_ADDED), "bytes; manifest_added.json written")
        return 0
    man = json.load(open(MANIFEST, encoding="utf-8"))
    layers = {l["id"]: l for l in man["layers"]}
    rows = []
    counts = {}
    for lid in TAKEN:
        r = layer_rows(layers[lid])
        counts[lid] = len(r)
        rows.extend(r)
    crow, feats, m = coal(None)
    counts["coal_fields"] = len(crow)
    rows.extend(crow)
    t = pd.DataFrame(rows)[COLS]
    if t["entity_id"].duplicated().any():
        raise SystemExit("an entity_id is given twice")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"resource_tables_{run_id}.log"))
    pubs = "; ".join(f"{lid}: {layers[lid].get('publisher')}, {layers[lid]['source_url']} (sha256 {layers[lid].get('source_sha256')})" for lid in TAKEN)
    ip.write_snapshot(t, NAME, [
        "Energy Research Warehouse (ERW): the natural resource map's layers, every cell, site and area, with the USGS coal fields (session 8006, chain 501)",
        "Shape: entities (docs/datastandard.md v0), entity_type resource (Decision 81). entity_id resource:<layer>:<r..c.. for a grid cell, or the feature's place in its layer>; lat and lon the cell's center or the feature's centroid; "
        "x_layer, x_kind (grid cell, site or the area's kind), x_value in x_unit (x_value_label says what it is), x_publisher, x_cell_deg (a grid's cell), x_area_km2 (an area's, on a sphere), x_extra (the publisher's other fields, JSON), x_source_sha256. Method: docs/methods/resource_layers_table.md.",
        "Rows by layer: " + ", ".join(f"{k} {v:,}" for k, v in counts.items()) + ". Left out: " + "; ".join(f"{k} ({v})" for k, v in LEFT_OUT.items()) + "; the Alaska and Hawaii grids.",
        f"Built {run_id} (UTC) by warehouse/derived/resource_tables.py from site/data/resources/manifest.json (built {man.get('built_at_utc')}) and its layer files, and the saved USGS GIS.zip",
        f"Run log: warehouse/output/logs/resource_tables_{run_id}.log",
        f"Source: {SOURCE} the ERW's reduction of each publisher's file (warehouse/connectors/resource_layers.py): {pubs}; coal_fields: usgs:of2012_1205_coal_fields {COAL_URL} (sha256 {m['sha256']})",
        "License: public (each layer's publisher's terms as the manifest quotes them: NLR's notice to keep with copies and credit to DOE/NLR; OpenEI; USGS, EIA and ORNL HydroSource public)",
    ], log, COLS)
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="The natural resource map's layers as a table (docs/methods/resource_layers_table.md)", report_url=METHOD_URL,
                            document_list="site/data/resources/manifest.json", license="public", tables=[NAME]),
                       dict(source="usgs:of2012_1205_coal_fields", publisher="U.S. Geological Survey (USGS)",
                            report="Open-File Report 2012-1205: Coal fields of the conterminous United States, National Coal Resource Assessment updated version (East, 2013)",
                            report_url=COAL_PAGE, document_list=COAL_URL, license="public", tables=[NAME])])
    web = os.path.join(a.out_dir, "site", "coal_fields.json") if a.out_dir else COAL_WEB
    size, tol = coal_web(feats, m, web)
    log(f"  coal fields web file: {size:,} bytes at tolerance {tol}")
    if a.out_dir:
        msize = coal_map_layer(feats, m, os.path.join(a.out_dir, "site", "layers", "coal_fields.json"), os.path.join(a.out_dir, "site", "manifest_added.json"))
    else:
        msize = coal_map_layer(feats, m, MAP_LAYER, MANIFEST_ADDED)
    log(f"  the map's layer file: {msize:,} bytes; manifest_added.json written")
    log.close()
    print(f"{NAME}: {len(t):,} rows ({counts}); coal_fields.json {size:,} bytes, tolerance {tol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
