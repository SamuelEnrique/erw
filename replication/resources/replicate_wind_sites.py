"""Replication of a fourth layer of the natural resource map (/map?tab=resources): the wind supply curve's sites.

Energy Research Warehouse (ERW). Session 8622 (chain 504), 19 November 2026.

What it does. The layer `wind_capacity_factor` of the map is the laboratory's land-based wind supply curve (the 2024
edition, open access siting, a 2035 turbine): one row for each cell of about 11.5 km in which wind could be built.
The layer keeps every row and seven of its columns. This script reads the table as it is published and compares every
figure the map holds for the layer: the count of sites; each site's place, its number, its capacity factor (the
figure the hover shows) and the three columns listed under it; the smallest, mean and largest capacity factor.

The web file rounds what it keeps, and the comparison is to the rounding: the place to three decimals of a degree,
the capacity factor to four decimals, the wind speed (the source's `resource`) to two, the developable area to one;
the capacity is a whole number in the source. The layer's entry names the first two roundings; the other two are
found here and said (data request 555).

It is written from the layer's method note (docs/methods/resources.md, "Wind capacity factor") and the publisher's
file alone, not from the code that built the layer, with Python's standard library alone.

The publisher's file. https://data.openei.org/files/8314/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv
(12,829,421 bytes, sha256 ef13116bd66f31157b2f7db6369831d63f3098877e91c6163766dbe6da47eb7d on 7 October and on
19 November 2026). Its terms: "Content is available under Creative Commons Attribution 4.0 unless otherwise noted"
(https://data.openei.org/submissions/8314). The host has no robots file (read 19 November 2026: not found).

    python replication/resources/replicate_wind_sites.py --csv path/to/lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv

Exit 0 when every figure is reproduced, 1 when one differs, 2 when the publisher's file is not the one named above.
It writes wind_capacity_factor_figures_differ.csv (only the figures that differ, with a first line saying how many
were compared) and crosscheck_wind_sites.csv beside itself: for each state its sites, their capacity and developable
area summed from the publisher's rows, the box its sites lie in, and whether that box is inside the coverage the
dataset's own page states. That is the one figure of the publisher's found to set the file beside; the page states
no total of sites, capacity or area.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LAYER = os.path.join(ROOT, "site", "data", "resources", "layers", "wind_capacity_factor.json")
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
SHA256 = "ef13116bd66f31157b2f7db6369831d63f3098877e91c6163766dbe6da47eb7d"
# the web file's column: the publisher's column, and the decimals the web file keeps (None: as written)
COLUMNS = {"lon": ("longitude", 3), "lat": ("latitude", 3), "name": ("sc_point_gid", None), "value": ("capacity_factor_ac", 4),
           "resource": ("resource", 2), "capacity_ac_mw": ("capacity_ac_mw", 0), "area_developable_sq_km": ("area_developable_sq_km", 1)}


def number(text):
    t = (text or "").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def met(ours, theirs, decimals):
    """The web file's value against the publisher's cell: text as written; a number to the decimals the web file keeps."""
    if decimals is None:
        return str(ours) == (theirs or "").strip()
    t = number(theirs)
    if ours is None or ours == "":
        return t is None
    if t is None or isinstance(ours, bool) or not isinstance(ours, (int, float)):
        return False
    return abs(ours - t) <= 0.5 * 10 ** -decimals + 1e-9 and abs(ours * 10 ** decimals - round(ours * 10 ** decimals)) < 1e-6


def compare(source_rows, layer, entry):
    """Every figure of the layer beside the publisher's. Returns (compared, the figures that differ)."""
    columns, rows = layer["columns"], layer["rows"]
    at = {c: i for i, c in enumerate(columns)}
    by_id = {r["sc_point_gid"]: r for r in source_rows}
    assert len(by_id) == len(source_rows), "the publisher's site numbers are not one a site"
    differ, n = [], 0

    def figure(what, ours, theirs, ok):
        nonlocal n
        n += 1
        if not ok:
            differ.append({"figure": what, "the_map": ours, "the_publisher": theirs})

    figure("sites, count", len(rows), len(source_rows), len(rows) == len(source_rows))
    figure("the web file's columns", ",".join(columns), ",".join(COLUMNS), list(columns) == list(COLUMNS))
    seen = set()
    for r in rows:
        key = str(r[at["name"]])
        s = by_id.get(key)
        if s is None:
            figure("site %s: a site of the publisher's file" % key, key, None, False)
            continue
        seen.add(key)
        for c in columns:
            src, dec = COLUMNS.get(c, (c, None))
            figure("site %s: %s%s" % (key, c, "" if src == c else " (the source's %s)" % src), r[at[c]], s.get(src), met(r[at[c]], s.get(src), dec))
    for key in sorted(set(by_id) - seen, key=lambda k: (len(k), k))[:50]:
        figure("site %s: a site of the map's layer" % key, None, key, False)
    values = [v for v in (number(s["capacity_factor_ac"]) for s in source_rows) if v is not None]
    stats = entry["stats"]
    same = lambda a, b: isinstance(a, (int, float)) and abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))   # noqa: E731
    for name, ours, theirs in (("smallest capacity factor", stats["min"], min(values)), ("mean capacity factor", stats["mean"], sum(values) / len(values)),
                               ("largest capacity factor", stats["max"], max(values)), ("sites, the list of layers' count", stats["n"], len(values))):
        figure(name, ours, theirs, same(ours, theirs))
    figure("the unit of the list of layers", entry.get("unit"), "ratio", entry.get("unit") == "ratio")
    return n, differ


# The coverage the dataset's own page states (https://data.openei.org/submissions/8314, read 19 November 2026): south,
# west, north, east, in degrees.
PAGE_BOX = (24.906576360863, -125.4514, 49.492589049135, -66.5318)


def by_state(source_rows):
    """A summary beside the cross-check: for each state the sites, their capacity and their developable area, summed
    from the publisher's rows, and the box of latitude and longitude its sites lie in."""
    out = {}
    for s in source_rows:
        cap, area, lat, lon = number(s.get("capacity_ac_mw")), number(s.get("area_developable_sq_km")), number(s.get("latitude")), number(s.get("longitude"))
        st = out.setdefault(s.get("state") or "not stated", {"sites": 0, "capacity_ac_mw": 0.0, "area_developable_sq_km": 0.0, "lat": [], "lon": []})
        st["sites"] += 1
        st["capacity_ac_mw"] += cap or 0.0
        st["area_developable_sq_km"] += area or 0.0
        if lat is not None and lon is not None:
            st["lat"].append(lat)
            st["lon"].append(lon)
    return [{"state": k, "sites": v["sites"], "capacity_ac_mw": round(v["capacity_ac_mw"], 1), "area_developable_sq_km": round(v["area_developable_sq_km"], 1),
             "south": min(v["lat"]) if v["lat"] else "", "north": max(v["lat"]) if v["lat"] else "", "west": min(v["lon"]) if v["lon"] else "", "east": max(v["lon"]) if v["lon"] else "",
             "inside_the_pages_box": "yes" if v["lat"] and min(v["lat"]) >= PAGE_BOX[0] and max(v["lat"]) <= PAGE_BOX[2] and min(v["lon"]) >= PAGE_BOX[1] and max(v["lon"]) <= PAGE_BOX[3] else "NO"}
            for k, v in sorted(out.items())]


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="the publisher's file, lbw_open_access_2035_moderate_115hh_170rd_supply_curve.csv")
    ap.add_argument("--no-write", action="store_true", help="compare and print; write neither csv")
    args = ap.parse_args(argv)
    with open(args.csv, "rb") as f:
        blob = f.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA256:
        print("the file is not the one the layer was built from: sha256 %s, wanted %s" % (digest, SHA256))
        return 2
    source_rows = list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline="")))
    with open(LAYER, encoding="utf-8") as f:
        layer = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        entry = [l for l in json.load(f)["layers"] if l["id"] == "wind_capacity_factor"][0]
    n, differ = compare(source_rows, layer, entry)
    check = by_state(source_rows)
    if not args.no_write:
        with open(os.path.join(HERE, "wind_capacity_factor_figures_differ.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# %d figures of the layer compared with the publisher's file (sha256 %s); the rows below are those that differ\n" % (n, digest))
            w = csv.DictWriter(f, fieldnames=["figure", "the_map", "the_publisher"], lineterminator="\n")
            w.writeheader()
            w.writerows(differ)
        with open(os.path.join(HERE, "crosscheck_wind_sites.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(check[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(check)

    print("the publisher's file: %d bytes, sha256 %s (the one the layer names)" % (len(blob), digest))
    print("%d of %d figures of the layer are the publisher's%s" % (n - len(differ), n, "" if not differ else "; %d differ" % len(differ)))
    for r in differ[:12]:
        print("   DIFFERS  %s: the map %r, the publisher %r" % (r["figure"], r["the_map"], r["the_publisher"]))
    sites, cap, area = sum(c["sites"] for c in check), sum(c["capacity_ac_mw"] for c in check), sum(c["area_developable_sq_km"] for c in check)
    held = [c for c in check if c["south"] != ""]
    south, north, west, east = min(c["south"] for c in held), max(c["north"] for c in held), min(c["west"] for c in held), max(c["east"] for c in held)
    inside = sum(1 for c in check if c["inside_the_pages_box"] == "yes")
    print("cross-check: the %d sites lie from %.4f to %.4f north and from %.4f to %.4f east; the dataset's page states its coverage as %.4f to %.4f north and %.4f to %.4f east; the sites of %d of %d states lie inside it"
          % (sites, south, north, west, east, PAGE_BOX[0], PAGE_BOX[2], PAGE_BOX[1], PAGE_BOX[3], inside, len(check)))
    print("summary, from the publisher's rows: %d states; capacity %s MW on %s square kilometres of developable land (no total is stated on the dataset's page to set these beside)"
          % (len(check), format(round(cap), ","), format(round(area), ",")))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
