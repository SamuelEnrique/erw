"""Replication of one layer of the natural resource map (/map?tab=resources): tight oil and shale gas plays.

Energy Research Warehouse (ERW). Session 8603 (chain 504), 19 November 2026.

What it does. The layer `oil_gas_plays` of the map is the Energy Information Administration's own file of play
outlines. This script reads that file as EIA publishes it and recomputes every figure the map holds for the layer:
each play's name and area (the figure the hover shows), the fields listed under it, the count of plays and the
smallest, mean and largest area. Then it sets the publisher's area of each play beside the area of the publisher's own
outline, computed here on the ellipsoid, as a cross-check.

It is written from the layer's method note (docs/methods/resources.md, "Tight oil and shale gas plays") and the
publisher's file alone, not from the code that built the layer. It reads the shapefile with nothing but Python's
standard library.

The publisher's file. https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip (323,424 bytes,
sha256 c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e on 7 October and on 19 November 2026).
EIA's terms: "Public domain and use of EIA content", https://www.eia.gov/about/copyrights_reuse.php. Its robots file
allows every path (read 19 November 2026).

    python replication/resources/replicate.py --zip path/to/TightOil_ShaleGas_Plays_Lower48_EIA.zip

Exit 0 when every figure is reproduced, 1 when one differs, 2 when the publisher's file is not the one named above.
It writes oil_gas_plays_figures.csv (every figure, the map's and the publisher's) and crosscheck.csv beside itself.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LAYER = os.path.join(ROOT, "site", "data", "resources", "layers", "oil_gas_plays.json")
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
SHA256 = "c09b3bd2982754cfb63d12bbbfde6c6c5e8c02eee73e54d231a7c7de73f0541e"
SQ_M_PER_SQ_MI = 1609.344 ** 2
# the WGS 84 ellipsoid, which the file's projection names
A, F = 6378137.0, 1 / 298.257223563
E2 = F * (2 - F)
E = math.sqrt(E2)


def read_dbf(raw):
    """The rows of a dBase table as a list of dicts: text as written, numbers as floats, blank as None."""
    n, header_len, record_len = struct.unpack("<IHH", raw[4:12])
    fields, pos = [], 32
    while raw[pos] != 0x0D:
        name = raw[pos:pos + 11].split(b"\x00")[0].decode("ascii")
        fields.append((name, chr(raw[pos + 11]), raw[pos + 16]))
        pos += 32
    rows = []
    for i in range(n):
        rec = raw[header_len + i * record_len: header_len + (i + 1) * record_len]
        if rec[:1] == b"*":
            continue
        at, row = 1, {}
        for name, kind, length in fields:
            text = rec[at:at + length].decode("utf-8").strip()
            at += length
            row[name] = (float(text) if text else None) if kind in "NF" else text
        rows.append(row)
    return rows


def read_polygons(raw):
    """The rings of each polygon of a shapefile, in the file's order: a list of lists of rings of (lon, lat)."""
    out, pos = [], 100
    while pos < len(raw):
        _, length = struct.unpack(">ii", raw[pos:pos + 8])
        body = raw[pos + 8: pos + 8 + 2 * length]
        pos += 8 + 2 * length
        kind = struct.unpack("<i", body[:4])[0]
        if kind == 0:
            out.append([])
            continue
        assert kind in (5, 15, 25), "not a polygon: shape type %d" % kind
        parts, points = struct.unpack("<ii", body[36:44])
        starts = list(struct.unpack("<%di" % parts, body[44:44 + 4 * parts])) + [points]
        xy = struct.unpack("<%dd" % (2 * points), body[44 + 4 * parts: 44 + 4 * parts + 16 * points])
        out.append([[(xy[2 * k], xy[2 * k + 1]) for k in range(starts[p], starts[p + 1])] for p in range(parts)])
    return out


def authalic_sine(lat_deg):
    """The sine of the authalic latitude, times the ellipsoid's q over 2: the term an equal-area sum needs."""
    s = math.sin(math.radians(lat_deg))
    return (1 - E2) * (s / (1 - E2 * s * s) - (1 / (2 * E)) * math.log((1 - E * s) / (1 + E * s))) / 2


def area_sq_mi(rings):
    """The area of a polygon on the WGS 84 ellipsoid, in square miles. A shapefile's holes run the other way round
    from its outer rings, so the signed areas of all rings are summed and the size of the sum is the area. Each side
    is taken as a straight line in longitude and authalic latitude (the trapezoid rule), which is exact as the points
    grow dense; EIA's outlines are dense."""
    total = 0.0
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            total += math.radians(x2 - x1) * (authalic_sine(y1) + authalic_sine(y2)) / 2
    return abs(total) * A * A / SQ_M_PER_SQ_MI


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    return (a or "") == (b or "")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, help="the publisher's file, TightOil_ShaleGas_Plays_Lower48_EIA.zip")
    args = ap.parse_args()
    with open(args.zip, "rb") as f:
        blob = f.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA256:
        print("the file is not the one the layer was built from: sha256 %s, wanted %s" % (digest, SHA256))
        return 2
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        dbf = read_dbf(z.read([n for n in z.namelist() if n.endswith(".dbf")][0]))
        shapes = read_polygons(z.read([n for n in z.namelist() if n.endswith(".shp")][0]))
    with open(LAYER, encoding="utf-8") as f:
        layer = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        entry = [l for l in json.load(f)["layers"] if l["id"] == "oil_gas_plays"][0]
    feats = layer["features"]
    assert len(dbf) == len(shapes), (len(dbf), len(shapes))

    rows, differ = [], 0

    def figure(what, ours, theirs):
        nonlocal differ
        ok = same(ours, theirs)
        differ += 0 if ok else 1
        rows.append({"figure": what, "the_map": ours, "the_publisher": theirs, "same": "yes" if ok else "NO"})

    figure("plays, count", len(feats), len(dbf))
    by_id = {r["ID"]: r for r in dbf}
    assert len(by_id) == len(dbf), "the publisher's IDs are not one a play"
    source_fields = [k for k in dbf[0] if k not in ("Shape_Leng", "Shape_Area")]
    for ft in feats:
        p = ft["properties"]
        r = by_id.get(p.get("ID"))
        if r is None:
            figure("%s: a play of the publisher's file" % p.get("ID"), p.get("name"), None)
            continue
        figure("%s: name (the source's Shale_play)" % r["ID"], p["name"], r["Shale_play"])
        figure("%s: area, square miles (the hover's figure; the source's Area_sq_mi)" % r["ID"], p["value"], r["Area_sq_mi"])
        for k in source_fields:
            if k in p:
                figure("%s: %s" % (r["ID"], k), p[k], r[k])
    areas = [r["Area_sq_mi"] for r in dbf]
    for name, ours, theirs in (("smallest area, square miles", entry["stats"]["min"], min(areas)), ("mean area, square miles", entry["stats"]["mean"], sum(areas) / len(areas)),
                               ("largest area, square miles", entry["stats"]["max"], max(areas)), ("plays, the list of layers' count", entry["stats"]["n"], len(areas)),
                               ("features, the list of layers' count", entry["features"], len(dbf))):
        figure(name, ours, theirs)
    with open(os.path.join(HERE, "oil_gas_plays_figures.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["figure", "the_map", "the_publisher", "same"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # the cross-check: the publisher's area of each play beside the area of the publisher's own outline
    check = []
    for r, rings in zip(dbf, shapes):
        mine = area_sq_mi(rings)
        check.append({"id": r["ID"], "play": r["Shale_play"], "basin": r["Basin"], "area_sq_mi_publisher": round(r["Area_sq_mi"], 3), "area_sq_mi_of_its_outline": round(mine, 3),
                      "difference_sq_mi": round(mine - r["Area_sq_mi"], 3), "difference_pct": round(100 * (mine - r["Area_sq_mi"]) / r["Area_sq_mi"], 3)})
    check.sort(key=lambda c: -abs(c["difference_pct"]))
    with open(os.path.join(HERE, "crosscheck.csv"), "w", encoding="utf-8", newline="") as f:
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
    print("cross-check: the %d plays' areas sum to %s square miles by the publisher's field and %s by its outlines (%+.3f percent); %d of %d plays agree within 1 percent"
          % (len(check), format(round(total_theirs), ","), format(round(total_mine), ","), 100 * (total_mine - total_theirs) / total_theirs, within, len(check)))
    for c in check[:5]:
        print("   %-10s %-28s publisher %12s  outline %12s  %+.3f percent" % (c["id"], c["play"][:28], format(c["area_sq_mi_publisher"], ",.1f"), format(c["area_sq_mi_of_its_outline"], ",.1f"), c["difference_pct"]))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
