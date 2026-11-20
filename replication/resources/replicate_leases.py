"""Replication of a fifth layer of the natural resource map (/map?tab=resources): offshore wind lease areas.

Energy Research Warehouse (ERW). Session 8623 (chain 504), 19 November 2026.

What it does. The layer `offshore_wind_leases` of the map is the Bureau of Ocean Energy Management's own outlines of
the leases, easements and research leases it has issued. This script reads BOEM's archive as BOEM serves it and
compares every figure the map holds for the layer: the count of outlines; each one's name, kind, area in acres (the
figure the hover shows; none where BOEM's ACRES is 0) and the fields kept under it; the smallest, mean and largest
area. Then two cross-checks inside BOEM's own archive: each lease's ACRES beside the area of its own outline on the
ellipsoid, and each lease's type in the outlines table beside its type in the archive's table of lease blocks.

It is written from the layer's method note (docs/methods/resources.md, "Offshore wind lease areas") and the
publisher's file alone, not from the code that built the layer. It reads the shapefiles with nothing but Python's
standard library; the readers of the two file kinds and the area on the ellipsoid are those of replicate.py in this
folder.

The publisher's file. https://www.boem.gov/renewable-energy/boem-renewable-energy-shapefiles (a zip, 1,031,812
bytes, sha256 47c5f33f5d16cede3295394fb54549fbbfc5b7f80f25acf073275939d1404a0b on 7 October and on 19 November 2026).
BOEM is an agency of the United States government; its robots file allows the path (read 19 November 2026).

    python replication/resources/replicate_leases.py --zip path/to/boem-renewable-energy-shapefiles.zip

Exit 0 when every figure is reproduced, 1 when one differs, 2 when the publisher's file is not the one named above.
It writes offshore_wind_leases_figures.csv (every figure, the map's and the publisher's) and crosscheck_leases.csv
beside itself.
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
LAYER = os.path.join(ROOT, "site", "data", "resources", "layers", "offshore_wind_leases.json")
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
SHA256 = "47c5f33f5d16cede3295394fb54549fbbfc5b7f80f25acf073275939d1404a0b"
ACRES_PER_SQ_MI = 640.0
OWN = ("name", "kind", "value", "value_unit")      # the layer's own four; every other property is a field of the source

_spec = importlib.util.spec_from_file_location("erw_replicate_plays", os.path.join(HERE, "replicate.py"))
_plays = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_plays)
read_dbf, read_polygons, area_sq_mi = _plays.read_dbf, _plays.read_polygons, _plays.area_sq_mi


def same(ours, theirs):
    """The layer's value against the publisher's cell: a blank of the source is none on the map; numbers to nine figures."""
    blank = lambda v: v is None or (isinstance(v, str) and v.strip() == "")   # noqa: E731
    if blank(ours) or blank(theirs):
        return blank(ours) and blank(theirs)
    if isinstance(ours, (int, float)) and not isinstance(ours, bool) and isinstance(theirs, (int, float)):
        return abs(ours - theirs) <= 1e-9 * max(1.0, abs(ours), abs(theirs))
    return str(ours) == str(theirs).strip()


def compare(outlines, shapes, blocks, layer, entry):
    """Every figure of the layer beside the publisher's, and the cross-check rows. `outlines` are the rows of the
    outlines table, `shapes` their rings, `blocks` the rows of the table of lease blocks. Returns (rows, differ, check)."""
    feats = layer["features"]
    rows, differ = [], 0

    def figure(what, ours, theirs, ok=None):
        nonlocal differ
        ok = same(ours, theirs) if ok is None else ok
        differ += 0 if ok else 1
        rows.append({"figure": what, "the_map": ours, "the_publisher": theirs, "same": "yes" if ok else "NO"})

    figure("outlines, count", len(feats), len(outlines))
    # an outline is told by its lease number and name together; the table's own order breaks a tie
    key = lambda r: (r.get("LEASE_NUMB"), r.get("LEASE_NU_1"))   # noqa: E731
    left = {}
    for r in outlines:
        left.setdefault(key(r), []).append(r)
    for ft in feats:
        p = ft["properties"]
        mine = left.get(key(p))
        if not mine:
            figure("%s: an outline of the publisher's file" % p.get("LEASE_NU_1"), p.get("name"), None, ok=False)
            continue
        r = mine.pop(0)
        tag = r["LEASE_NUMB"]
        figure("%s: name (the source's LEASE_NU_1)" % tag, p["name"], r["LEASE_NU_1"])
        figure("%s: kind (lease area, with the source's LEASE_TYPE)" % tag, p["kind"], "lease area (%s)" % r["LEASE_TYPE"])
        acres = r.get("ACRES")
        figure("%s: area, acres (the hover's figure; the source's ACRES, none where it is 0)" % tag, p["value"], acres if acres else None)
        figure("%s: the unit the hover gives" % tag, p.get("value_unit"), "acres")
        for k in p:
            if k not in OWN:
                figure("%s: %s" % (tag, k), p[k], r.get(k), ok=None if k in r else False)
    for k, mine in left.items():
        for r in mine:
            figure("%s: an outline of the map's layer" % r.get("LEASE_NU_1"), None, r.get("LEASE_NU_1"), ok=False)
    held = [r["ACRES"] for r in outlines if r.get("ACRES")]
    stats = entry["stats"]
    for name, ours, theirs in (("smallest area, acres", stats["min"], min(held)), ("mean area, acres", stats["mean"], sum(held) / len(held)), ("largest area, acres", stats["max"], max(held)),
                               ("outlines with an area, the list of layers' count", stats["n"], len(held)), ("features, the list of layers' count", entry["features"], len(outlines)),
                               ("the unit of the list of layers", entry.get("unit"), "acres")):
        figure(name, ours, theirs)

    types = {}
    for b in blocks:
        types.setdefault(b.get("LEASE_NUMB"), set()).add(b.get("LEASE_TYPE") or "")
    check = []
    for r, rings in zip(outlines, shapes):
        mine = area_sq_mi(rings) * ACRES_PER_SQ_MI if rings else None
        acres = r.get("ACRES") or None
        in_blocks = sorted(t for t in types.get(r["LEASE_NUMB"], set()) if t)
        check.append({"lease": r["LEASE_NUMB"], "name": r["LEASE_NU_1"], "acres_publisher": acres if acres else "", "acres_of_its_outline": round(mine, 1) if mine is not None else "",
                      "difference_pct": round(100 * (mine - acres) / acres, 3) if acres and mine is not None else "",
                      "type_in_the_outlines_table": r["LEASE_TYPE"], "type_in_the_blocks_table": "; ".join(in_blocks) if in_blocks else "not in that table",
                      # a lease with an easement has two types in the blocks table: the outline's type must be one of them
                      "types_agree": "" if not in_blocks else ("yes" if r["LEASE_TYPE"] in in_blocks else "NO")})
    check.sort(key=lambda c: -abs(c["difference_pct"]) if c["difference_pct"] != "" else 1)
    return rows, differ, check


def read_archive(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        pick = lambda end: [n for n in names if n.endswith(end)][0]   # noqa: E731
        outlines = read_dbf(z.read(pick("Offshore_Wind_Leases_outlines.dbf")))
        shapes = read_polygons(z.read(pick("Offshore_Wind_Leases_outlines.shp")))
        blocks = read_dbf(z.read(pick("Offshore_Wind_Leases.dbf")))
    assert len(outlines) == len(shapes), (len(outlines), len(shapes))
    return outlines, shapes, blocks


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, help="the publisher's file, the archive of BOEM's renewable energy shapefiles")
    ap.add_argument("--no-write", action="store_true", help="compare and print; write neither csv")
    args = ap.parse_args(argv)
    with open(args.zip, "rb") as f:
        blob = f.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA256:
        print("the file is not the one the layer was built from: sha256 %s, wanted %s" % (digest, SHA256))
        return 2
    outlines, shapes, blocks = read_archive(blob)
    with open(LAYER, encoding="utf-8") as f:
        layer = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        entry = [l for l in json.load(f)["layers"] if l["id"] == "offshore_wind_leases"][0]
    rows, differ, check = compare(outlines, shapes, blocks, layer, entry)
    if not args.no_write:
        with open(os.path.join(HERE, "offshore_wind_leases_figures.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["figure", "the_map", "the_publisher", "same"], lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(HERE, "crosscheck_leases.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(check[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(check)

    print("the publisher's file: %d bytes, sha256 %s (the one the layer names)" % (len(blob), digest))
    print("%d of %d figures of the layer are the publisher's%s" % (len(rows) - differ, len(rows), "" if not differ else "; %d differ" % differ))
    for r in rows:
        if r["same"] == "NO":
            print("   DIFFERS  %s: the map %r, the publisher %r" % (r["figure"], r["the_map"], r["the_publisher"]))
    held = [c for c in check if c["difference_pct"] != ""]
    theirs, mine = sum(c["acres_publisher"] for c in held), sum(c["acres_of_its_outline"] for c in held)
    within = sum(1 for c in held if abs(c["difference_pct"]) <= 1)
    print("cross-check 1: for the %d outlines with an area, BOEM's ACRES sum to %s and the outlines' own areas to %s acres (%+.3f percent); %d of %d agree within 1 percent"
          % (len(held), format(round(theirs), ","), format(round(mine), ","), 100 * (mine - theirs) / theirs if theirs else 0.0, within, len(held)))
    for c in held[:4]:
        print("   %-11s %-46s ACRES %10s  outline %12s  %+.3f percent" % (c["lease"], c["name"][:46], format(c["acres_publisher"], ",.0f"), format(c["acres_of_its_outline"], ",.1f"), c["difference_pct"]))
    both = [c for c in check if c["types_agree"] != ""]
    apart = [c for c in both if c["types_agree"] == "NO"]
    print("cross-check 2: %d of the %d outlines are also in the archive's table of lease blocks; the outline's lease type is one that table gives the lease for %d and not for %d"
          % (len(both), len(check), len(both) - len(apart), len(apart)))
    for c in apart:
        print("   %-11s %-46s outlines: %s; blocks: %s" % (c["lease"], c["name"][:46], c["type_in_the_outlines_table"], c["type_in_the_blocks_table"]))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
