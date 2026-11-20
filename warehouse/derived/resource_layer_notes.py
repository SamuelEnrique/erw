#!/usr/bin/env python3
"""Notes on three layers of the resource map, in a new file beside them (session 8013, chain 505, data requests 554 to 556).

Energy Research Warehouse (ERW). The portable laptop's replications of the resource map (chain 504) asked three things
of layer files written in October by warehouse/connectors/resource_layers.py. Chain 505's rule is "add, never change":
those files and site/data/resources/manifest.json stay as they are, and what was asked is written here, in a new file,
as data request 553's answer was (site/data/resources/hover_fields_added.json). A page that wants these reads this file;
nothing else moves.

    python warehouse/derived/resource_layer_notes.py                 # writes site/data/resources/layer_notes_added.json
    python warehouse/derived/resource_layer_notes.py --out FILE      # a trial

What it writes, each part computed from the publisher's own file or the layer's own web file, never typed by hand:

  oil_gas_basins (request 554): EIA's NAME field is in capitals, and the connector writes each word with its first
      letter a capital (str.title). The rule here, stated once: a word or a hyphenated part that is a US state's postal
      code keeps its capitals; "and", "of", "the", "in" are small unless first; every other word has its first letter a
      capital. A basin is listed only where this rule's name differs from the layer's. The plays' names do not pass
      through str.title (the connector keeps the publisher's text), so they are not listed.
  wind_capacity_factor (request 555): the decimals each column of the web file is kept to, measured over every row
      (the most decimals any value of the column has), and the sentence of the reduction that names all of them.
  offshore_wind_leases (request 556): BOEM's archive holds two tables, the lease outlines (which the layer draws) and
      the lease blocks. For every outline whose LEASE_TYPE is not among the types the blocks table gives the same
      lease, both are listed. Nothing chooses between them: both are BOEM's.

Inputs: site/data/resources/layers/oil_gas_basins.json (its NAME property is EIA's own field),
site/data/resources/layers/wind_capacity_factor.json, site/data/resources/manifest.json (each layer's source address
and sha256), and BOEM's saved archive under warehouse/raw/resources/boem/ (the file the manifest names).
"""

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(REPO, "site", "data", "resources")
OUT = os.path.join(RES, "layer_notes_added.json")
RAW = os.environ.get("ERW_RESOURCES_RAW") or os.path.join(REPO, "warehouse", "raw", "resources")

STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA",
          "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
          "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"}
SMALL = {"and", "of", "the", "in"}


def name_as_written(name):
    """EIA's capitals to a name as a reader writes it, by the rule of the module's docstring."""
    words = str(name).strip().split()
    out = []
    for i, w in enumerate(words):
        parts = []
        for p in w.split("-"):
            if p.upper() in STATES and len(p) == 2:
                parts.append(p.upper())
            elif p.lower() in SMALL and i > 0:
                parts.append(p.lower())
            else:
                parts.append(p[:1].upper() + p[1:].lower())
        out.append("-".join(parts))
    return " ".join(out)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def manifest_entry(layer_id):
    for l in load(os.path.join(RES, "manifest.json"))["layers"]:
        if l["id"] == layer_id:
            return l
    raise SystemExit(f"manifest.json has no layer {layer_id}")


def source_of(entry):
    return {k: entry.get(k) for k in ("source_url", "source_sha256", "retrieved_at_utc") if entry.get(k)}


def basins():
    layer = load(os.path.join(RES, "layers", "oil_gas_basins.json"))
    changed = []
    for f in layer["features"]:
        p = f["properties"]
        new = name_as_written(p["NAME"])
        if new != p["name"]:
            changed.append({"NAME": p["NAME"], "name_in_layer": p["name"], "name_as_written": new})
    changed.sort(key=lambda r: r["NAME"])
    return {"request": 554, "features": len(layer["features"]), "names_that_differ": changed,
            "rule": ("a word or hyphenated part that is a US state's postal code keeps its capitals; 'and', 'of', "
                     "'the', 'in' are small unless first; every other word has its first letter a capital"),
            "plays": "oil_gas_plays keeps the publisher's own text (no str.title), so no play is listed",
            "source": source_of(manifest_entry("oil_gas_basins"))}


def decimals(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    if isinstance(v, int):
        return 0
    s = repr(float(v))
    if "e" in s or "E" in s:
        raise SystemExit(f"a value in exponent form ({s}): the decimals cannot be read from it")
    return len(s.split(".")[1].rstrip("0")) if "." in s else 0


def wind():
    layer = load(os.path.join(RES, "layers", "wind_capacity_factor.json"))
    cols = layer["columns"]
    most = {c: None for c in cols}
    for row in layer["rows"]:
        for c, v in zip(cols, row):
            d = decimals(v)
            if d is not None and (most[c] is None or d > most[c]):
                most[c] = d
    entry = manifest_entry("wind_capacity_factor")
    words = {"lon": "coordinates", "value": "the capacity factor", "resource": "the wind speed",
             "capacity_ac_mw": "the capacity", "area_developable_sq_km": "the developable area"}
    if most.get("lon") != most.get("lat"):
        raise SystemExit("longitude and latitude are kept to different decimals: the sentence below assumes one")
    said = [f"{words[c]} to {most[c]}" for c in ("lon", "value", "resource", "area_developable_sq_km")
            if most.get(c) is not None]   # the capacity is whole megawatts in the file; its decimals are in decimals_kept
    return {"request": 555, "rows": len(layer["rows"]),
            "decimals_kept": {c: most[c] for c in cols if most[c] is not None},
            "reduction_in_manifest": entry.get("reduction"),
            "reduction_all_roundings": ("none: every row of the source at the source's own centroid (" +
                                        ", ".join(said[:-1]) + " and " + said[-1] + " decimals); the state, county, "
                                        "cost and transmission columns are left out of the web file"),
            "source": source_of(entry)}


def leases():
    import pyogrio
    entry = manifest_entry("offshore_wind_leases")
    found = glob.glob(os.path.join(RAW, "boem", "unpacked", "**", "Offshore_Wind_Leases_outlines.shp"), recursive=True)
    if len(found) != 1:
        raise SystemExit(f"BOEM's outlines table: {len(found)} copies under {RAW}/boem/unpacked, one expected")
    d = os.path.dirname(found[0])
    zips = glob.glob(os.path.join(RAW, "boem", "*.zip"))
    sha = {os.path.basename(z): hashlib.sha256(open(z, "rb").read()).hexdigest() for z in zips}
    want = (entry.get("source_sha256") or "").lower()
    if want and not any(h.startswith(want[:16]) or want.startswith(h[:16]) for h in sha.values()):
        raise SystemExit(f"no saved BOEM archive has the sha256 the manifest names ({want[:16]}): {sha}")
    outl = pyogrio.read_dataframe(found[0], read_geometry=False)
    blocks = pyogrio.read_dataframe(os.path.join(d, "Offshore_Wind_Leases.shp"), read_geometry=False)
    by = {}
    for n, t in zip(blocks["LEASE_NUMB"], blocks["LEASE_TYPE"]):
        by.setdefault(str(n).strip(), set()).add(str(t).strip())
    differ = []
    for _, r in outl.iterrows():
        n, t = str(r["LEASE_NUMB"]).strip(), str(r["LEASE_TYPE"]).strip()
        bt = sorted(by.get(n, set()))
        if t not in bt:
            differ.append({"LEASE_NUMB": n, "COMPANY": str(r["COMPANY"]).strip(), "outline_type": t,
                           "outline_acres": None if r["ACRES"] is None else float(r["ACRES"]),
                           "block_types": bt, "kind_in_layer": f"lease area ({t})" if t else "lease area"})
    differ.sort(key=lambda x: (x["LEASE_NUMB"], x["outline_type"]))
    return {"request": 556, "outlines": int(len(outl)), "block_rows": int(len(blocks)),
            "outlines_whose_type_the_blocks_do_not_give": differ,
            "tables": {"outlines": "Offshore_Wind_Leases_outlines (the layer draws these)",
                       "blocks": "Offshore_Wind_Leases (one row a lease block)"},
            "choice": "none: both of BOEM's tables are listed where they differ; the layer is unchanged",
            "source": source_of(entry)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    doc = {"built_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "note": ("Notes on three layers of the resource map, asked by data requests 554 to 556 "
                    "(docs/state/data_requests_done_line.md). The layer files and manifest.json are unchanged; "
                    "built by warehouse/derived/resource_layer_notes.py."),
           "layers": {"oil_gas_basins": basins(), "wind_capacity_factor": wind(), "offshore_wind_leases": leases()}}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    L = doc["layers"]
    print(f"wrote {a.out}: basins {len(L['oil_gas_basins']['names_that_differ'])} names differ; wind decimals "
          f"{L['wind_capacity_factor']['decimals_kept']}; leases "
          f"{len(L['offshore_wind_leases']['outlines_whose_type_the_blocks_do_not_give'])} outlines differ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
