"""Replication of a second layer of the natural resource map (/map?tab=resources): the sedimentary basins.

Energy Research Warehouse (ERW). Session 8619 (chain 504), 19 November 2026.

What it does. The layer `oil_gas_basins` of the map is the Energy Information Administration's own file of basin
outlines. This script reads that file as EIA publishes it and recomputes every figure the map holds for the layer:
each basin's name and area (the figure the hover shows), the fields kept under it, the count of basins and the
smallest, mean and largest area. Then, as cross-checks, it sets the publisher's area of each basin beside the area of
the publisher's own outline, computed here on the ellipsoid, and the publisher's square kilometres beside its square
miles.

It is written from the layer's method note (docs/methods/resources.md, "Sedimentary basins") and the publisher's file
alone, not from the code that built the layer. It reads the shapefile with nothing but Python's standard library; the
readers of the two file kinds and the area on the ellipsoid are those of replicate.py in this folder.

The publisher's file. https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip (440,871 bytes, sha256
02a017ccb84bdcc15726838098e3cfa73450b9655cf06e28d2eca6f3c04edcff on 7 October and on 19 November 2026). EIA's terms:
"Public domain and use of EIA content", https://www.eia.gov/about/copyrights_reuse.php. Its robots file allows the
path (read 19 November 2026).

    python replication/resources/replicate_basins.py --zip path/to/SedimentaryBasins_US_EIA.zip

Exit 0 when every figure is reproduced, 1 when one differs, 2 when the publisher's file is not the one named above.
It writes oil_gas_basins_figures.csv (every figure, the map's and the publisher's) and crosscheck_basins.csv beside
itself.

One rule is the layer's and not the publisher's: a basin's name. EIA writes names in capitals ("FORT WORTH"); the
layer shows each word with a capital first and the rest small ("Fort Worth"), and keeps EIA's own spelling beside it
(the field NAME). The rule is applied here as written, so the one name it serves badly is reproduced too: EIA's
"TX-LA-MS SALT", three states' codes, reads "Tx-La-Ms Salt" on the map (data request 554).
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LAYER = os.path.join(ROOT, "site", "data", "resources", "layers", "oil_gas_basins.json")
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
SHA256 = "02a017ccb84bdcc15726838098e3cfa73450b9655cf06e28d2eca6f3c04edcff"
SQ_KM_PER_SQ_MI = 1.609344 ** 2

_spec = importlib.util.spec_from_file_location("erw_replicate_plays", os.path.join(HERE, "replicate.py"))
_plays = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_plays)
read_dbf, read_polygons, area_sq_mi, same = _plays.read_dbf, _plays.read_polygons, _plays.area_sq_mi, _plays.same


def shown_name(source_name):
    """The layer's rule for a name: each run of letters with its first letter a capital and the rest small."""
    return source_name.title()


def compare(blob, layer, entry):
    """Every figure of the layer beside the publisher's, and the cross-check rows. Returns (rows, differ, check)."""
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        dbf = read_dbf(z.read([n for n in z.namelist() if n.endswith(".dbf")][0]))
        shapes = read_polygons(z.read([n for n in z.namelist() if n.endswith(".shp")][0]))
    assert len(dbf) == len(shapes), (len(dbf), len(shapes))
    feats = layer["features"]
    rows, differ = [], 0

    def figure(what, ours, theirs):
        nonlocal differ
        ok = same(ours, theirs)
        differ += 0 if ok else 1
        rows.append({"figure": what, "the_map": ours, "the_publisher": theirs, "same": "yes" if ok else "NO"})

    figure("basins, count", len(feats), len(dbf))
    by_name = {r["NAME"]: r for r in dbf}
    assert len(by_name) == len(dbf), "the publisher's names are not one a basin"
    seen = set()
    for ft in feats:
        p = ft["properties"]
        r = by_name.get(p.get("NAME"))
        if r is None:
            figure("%s: a basin of the publisher's file" % p.get("NAME"), p.get("name"), None)
            continue
        seen.add(r["NAME"])
        figure("%s: name as shown (the source's NAME, by the layer's rule)" % r["NAME"], p["name"], shown_name(r["NAME"]))
        figure("%s: area, square miles (the hover's figure; the source's Area_sq_mi)" % r["NAME"], p["value"], r["Area_sq_mi"])
        figure("%s: the unit the hover gives" % r["NAME"], p.get("value_unit"), "square miles")
        for k in r:
            if k in p:
                figure("%s: %s" % (r["NAME"], k), p[k], r[k])
    for name in sorted(set(by_name) - seen):
        figure("%s: a basin of the map's layer" % name, None, name)
    areas = [r["Area_sq_mi"] for r in dbf]
    for name, ours, theirs in (("smallest area, square miles", entry["stats"]["min"], min(areas)), ("mean area, square miles", entry["stats"]["mean"], sum(areas) / len(areas)),
                               ("largest area, square miles", entry["stats"]["max"], max(areas)), ("basins, the list of layers' count", entry["stats"]["n"], len(areas)),
                               ("features, the list of layers' count", entry["features"], len(dbf)), ("the unit of the list of layers", entry.get("unit"), "square miles")):
        figure(name, ours, theirs)

    check = []
    for r, rings in zip(dbf, shapes):
        mine = area_sq_mi(rings)
        check.append({"basin": r["NAME"], "area_sq_mi_publisher": round(r["Area_sq_mi"], 3), "area_sq_mi_of_its_outline": round(mine, 3),
                      "difference_sq_mi": round(mine - r["Area_sq_mi"], 3), "difference_pct": round(100 * (mine - r["Area_sq_mi"]) / r["Area_sq_mi"], 3),
                      "area_sq_km_publisher": round(r["Area_sq_km"], 3), "sq_km_from_its_sq_mi": round(r["Area_sq_mi"] * SQ_KM_PER_SQ_MI, 3),
                      "sq_km_difference_pct": round(100 * (r["Area_sq_mi"] * SQ_KM_PER_SQ_MI - r["Area_sq_km"]) / r["Area_sq_km"], 4)})
    check.sort(key=lambda c: -abs(c["difference_pct"]))
    return rows, differ, check


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, help="the publisher's file, SedimentaryBasins_US_EIA.zip")
    ap.add_argument("--no-write", action="store_true", help="compare and print; write neither csv")
    args = ap.parse_args(argv)
    with open(args.zip, "rb") as f:
        blob = f.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA256:
        print("the file is not the one the layer was built from: sha256 %s, wanted %s" % (digest, SHA256))
        return 2
    with open(LAYER, encoding="utf-8") as f:
        layer = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        entry = [l for l in json.load(f)["layers"] if l["id"] == "oil_gas_basins"][0]
    rows, differ, check = compare(blob, layer, entry)
    if not args.no_write:
        with open(os.path.join(HERE, "oil_gas_basins_figures.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["figure", "the_map", "the_publisher", "same"], lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(HERE, "crosscheck_basins.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(check[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(check)

    print("the publisher's file: %d bytes, sha256 %s (the one the layer names)" % (len(blob), digest))
    print("%d of %d figures of the layer are the publisher's%s" % (len(rows) - differ, len(rows), "" if not differ else "; %d differ" % differ))
    for r in rows:
        if r["same"] == "NO":
            print("   DIFFERS  %s: the map %r, the publisher %r" % (r["figure"], r["the_map"], r["the_publisher"]))
    total_theirs, total_mine = sum(c["area_sq_mi_publisher"] for c in check), sum(c["area_sq_mi_of_its_outline"] for c in check)
    within = sum(1 for c in check if abs(c["difference_pct"]) <= 1)
    print("cross-check 1: the %d basins' areas sum to %s square miles by the publisher's field and %s by its outlines (%+.3f percent); %d of %d basins agree within 1 percent"
          % (len(check), format(round(total_theirs), ","), format(round(total_mine), ","), 100 * (total_mine - total_theirs) / total_theirs, within, len(check)))
    for c in check[:5]:
        print("   %-22s publisher %12s  outline %12s  %+.3f percent" % (c["basin"][:22], format(c["area_sq_mi_publisher"], ",.1f"), format(c["area_sq_mi_of_its_outline"], ",.1f"), c["difference_pct"]))
    worst = max(abs(c["sq_km_difference_pct"]) for c in check)
    print("cross-check 2: the publisher's square kilometres are its square miles times %.6f in every basin to within %.4f percent" % (SQ_KM_PER_SQ_MI, worst))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
