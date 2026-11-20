"""ERW: hover fields, in each publisher's own words, for the resource map's point layers that name none.

Session 8011, chain 501 (data request 553 of the portable laptop). manifest.json gives `hover_fields` for some point
layers (Oak Ridge's hydropower layers) and none for two: the laboratory's 2024 land-based wind supply curve
(`wind_capacity_factor`) and USGS's identified hydrothermal systems (`geothermal_hydrothermal_sites`). Where a layer
names none, the page falls back on the file's raw column names. Chain 501's rule forbids changing manifest.json, an
existing page file, so the lists are written to a new file, `site/data/resources/hover_fields_added.json`, in the
manifest's pair form ([column, words]), each pair's words and unit cut from the publisher's own column description:

- wind_capacity_factor: the laboratory's column lookup saved beside the supply curve
  (`warehouse/raw/resources/openei/lbw_column_lookup.csv`, columns "reV Column", "Units", "Description");
- geothermal_hydrothermal_sites: USGS's metadata saved beside the shapefile
  (`warehouse/raw/resources/usgs/IdentifiedGeothermalSystems/IdentifiedGeothermalSystems.xml`, attrlabl and attrdef).

Each layer's `name` column is also described: the wind layer's `name` is the supply curve's `sc_point_gid` (the
connector, warehouse/connectors/resource_layers.py, writes it there), the hydrothermal layer's is the source's `Name`.
Nothing is written that the two files do not say. No model is called.

    python warehouse/derived/resource_hover_fields.py [--out PATH]
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "warehouse", "raw", "resources")
LOOKUP = os.path.join(RAW, "openei", "lbw_column_lookup.csv")
USGS_XML = os.path.join(RAW, "usgs", "IdentifiedGeothermalSystems", "IdentifiedGeothermalSystems.xml")
LAYERS = os.path.join(ROOT, "site", "data", "resources", "layers")
OUT = os.path.join(ROOT, "site", "data", "resources", "hover_fields_added.json")

# the layer's column -> the publisher's column it holds (the connector's choice, resource_layers.py)
WIND = {"name": "sc_point_gid", "resource": "resource", "capacity_ac_mw": "capacity_ac_mw", "area_developable_sq_km": "area_developable_sq_km"}
WIND_HOVER = ["resource", "capacity_ac_mw", "area_developable_sq_km"]
GEO_HOVER = ["State", "Temp_C_Li", "Temp_C_Mn", "Temp_C_Mx", "Vol_km3_Li", "Vol_km3_Mn", "Vol_km3_Mx", "MWe_P95", "MWe_P5"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def columns_of(layer_id):
    with open(os.path.join(LAYERS, layer_id + ".json"), encoding="utf-8") as f:
        return json.load(f)["columns"]


def wind():
    with open(LOOKUP, encoding="utf-8-sig", newline="") as f:
        look = {r["reV Column"]: r for r in csv.DictReader(f)}
    have = columns_of("wind_capacity_factor")
    pairs = []
    for c in WIND_HOVER:
        if c not in have:
            raise SystemExit(f"wind_capacity_factor.json has no column {c}")
        r = look[WIND[c]]
        unit = r["Units"].strip()
        pairs.append([c, r["Description"].strip() + ("" if unit in ("", "N/A") else f", {unit}")])
    n = look[WIND["name"]]
    return {"hover_fields": pairs,
            "name_column": {"column": "name", "source_column": "sc_point_gid", "words": n["Description"].strip(), "unit": n["Units"].strip()},
            "source_file": rel(LOOKUP), "source_sha256": sha256(LOOKUP),
            "how": "each pair's words are the Description column of the laboratory's lookup for the layer's column, its Units after a comma (none for N/A)"}


def geothermal():
    with open(USGS_XML, encoding="utf-8") as f:
        xml = f.read()
    defs = {m.group(1).strip(): re.sub(r"\s+", " ", m.group(2)).strip()
            for m in re.finditer(r"<attrlabl>(.*?)</attrlabl>\s*<attrdef>(.*?)</attrdef>", xml, re.S)}
    have = columns_of("geothermal_hydrothermal_sites")
    pairs = []
    for c in GEO_HOVER:
        if c not in have:
            raise SystemExit(f"geothermal_hydrothermal_sites.json has no column {c}")
        pairs.append([c, defs[c]])
    return {"hover_fields": pairs,
            "name_column": {"column": "name", "source_column": "Name", "words": defs["Name"], "unit": ""},
            "source_file": rel(USGS_XML), "source_sha256": sha256(USGS_XML),
            "how": "each pair's words are the attrdef USGS's metadata gives the column (its unit is inside the words)"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    doc = {"built_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "note": "hover_fields, in manifest.json's pair form, for the point layers of manifest.json that name none, each pair's words the "
                   "publisher's own column description; manifest.json is not changed (chain 501). A page uses a layer's list here when "
                   "manifest.json gives none. Built by warehouse/derived/resource_hover_fields.py (data request 553).",
           "layers": {"wind_capacity_factor": wind(), "geothermal_hydrothermal_sites": geothermal()}}
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    if chr(0x2014) in text:
        raise SystemExit("an em dash in the words")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    for k, v in doc["layers"].items():
        print(k, [p[1] for p in v["hover_fields"]], "| name:", v["name_column"]["words"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
