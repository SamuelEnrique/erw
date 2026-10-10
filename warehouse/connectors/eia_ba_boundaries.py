#!/usr/bin/env python3
"""Energy Research Warehouse (ERW), session 180: the boundaries of the US balancing authorities, reference geometry
for the network page's map view.

This is not a table. The data standard has three table shapes (series, entities, events) and a polygon is none of them,
so nothing here goes through the validator or into warehouse/output: the connector keeps the publisher's file as it
came (the raw file, with its request log beside it) and writes one small file the site ships,
site/public/network/ba_boundaries.json: only the balancing authorities the network draws, matched to its ids, each
shape simplified, with a provenance record (source, URL, retrieval time, sha256 of the raw file, the simplification).

Two steps, each its own command:

  get    one request to an outside host, logged in <pull-dir>/requests.csv (URL, status, bytes, time, sha256). The
         contact string is the ruled one. A paused publisher's host is refused (iso_prices.paused_host). No redirect is
         followed: a redirect is a request, and it is counted like one. The command refuses to pass the ceilings it is
         given (requests and bytes, the session's: 5 and 200 MB).
  build  the raw GeoJSON, read from disk, to the site file. No request. Matching is exact: a shape is given to a node
         only when the publisher's own code for it is the node's EIA-930 code; nothing is matched by name or by guess.
         Every node with no shape and every shape with no node is listed in the provenance record.

Real data only: a shape that is not in the publisher's file is not drawn from anything else.
"""
import argparse
import calendar
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"
LOG_COLS = ["n", "url", "status", "bytes", "seconds", "retrieved_utc", "sha256", "saved_as", "note"]
SOURCE_ID = "eia:atlas:balancing_authorities"


# ---------------------------------------------------------------------------------------------- get

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):  # a redirect is returned as it is, never followed
        return None


def read_log(pull_dir):
    path = os.path.join(pull_dir, "requests.csv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_log(pull_dir, rows):
    path = os.path.join(pull_dir, "requests.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def robots_allows(robots_path, url):
    """Whether a saved robots file allows this URL to the ERW's agent (the standard library's reading of it)."""
    rp = urllib.robotparser.RobotFileParser()
    with open(robots_path, encoding="utf-8", errors="replace") as f:
        rp.parse(f.read().splitlines())
    return rp.can_fetch(CONTACT, url)


def get(url, name, pull_dir, max_requests, max_bytes, robots=None, note="", min_gap=0):
    """One request. Returns the log row. Raises SystemExit before sending when a ceiling or a rule forbids it."""
    sys.path.insert(0, HERE)
    import iso_prices  # the pause register: a paused publisher's host is never asked
    host = urllib.parse.urlsplit(url).hostname or ""
    if iso_prices.paused_host(host):
        raise SystemExit(f"REFUSED: {host} belongs to a paused publisher (warehouse/metadata/paused_sources.csv). No request made.")
    if robots and not robots_allows(robots, url):
        raise SystemExit(f"REFUSED: the robots file {robots} disallows {url} to this agent. No request made.")
    os.makedirs(pull_dir, exist_ok=True)
    log = read_log(pull_dir)
    if len(log) >= max_requests:
        raise SystemExit(f"REFUSED: {len(log)} requests already made, the ceiling is {max_requests}. No request made.")
    spent = sum(int(r["bytes"] or 0) for r in log)
    left = max_bytes - spent
    if left <= 0:
        raise SystemExit(f"REFUSED: {spent} bytes already read, the ceiling is {max_bytes}. No request made.")
    # a robots file's Crawl-delay: the newest request to the same host must be at least min_gap seconds old
    same = [r for r in log if (urllib.parse.urlsplit(r["url"]).hostname or "") == host]
    if min_gap and same:
        last = calendar.timegm(time.strptime(same[-1]["retrieved_utc"], "%Y-%m-%dT%H:%M:%SZ"))
        if time.time() - last < min_gap:
            raise SystemExit(f"REFUSED: the last request to {host} was {time.time() - last:.0f} s ago, the delay asked is {min_gap} s. No request made.")
    out_dir = os.path.join(pull_dir, f"{len(log) + 1:02d}_{name.split('.')[0]}")
    os.makedirs(out_dir, exist_ok=False)  # its own new directory
    out = os.path.join(out_dir, name)
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": CONTACT, "Accept": "*/*"})
    t0 = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status, n, h, extra = "", 0, hashlib.sha256(), note
    try:
        try:
            resp = opener.open(req, timeout=600)
        except urllib.error.HTTPError as e:  # a refusal or a redirect: its body is still read and kept
            resp = e
        status = str(resp.status if hasattr(resp, "status") else resp.code)
        loc = resp.headers.get("Location")
        if loc:
            extra = (extra + " " if extra else "") + f"Location: {loc}"
        with open(out, "wb") as f:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                n += len(chunk)
                if n > left:
                    extra = (extra + " " if extra else "") + "STOPPED: the byte ceiling was reached, the file is not whole"
                    break
                f.write(chunk)
                h.update(chunk)
    except Exception as e:  # the exact error, logged; the request still counts
        status = status or "error"
        extra = (extra + " " if extra else "") + f"{type(e).__name__}: {e}"
    row = {"n": len(log) + 1, "url": url, "status": status, "bytes": n, "seconds": f"{time.time() - t0:.1f}",
           "retrieved_utc": stamp, "sha256": h.hexdigest() if n else "", "saved_as": os.path.relpath(out, pull_dir).replace("\\", "/"),
           "note": extra}
    log.append(row)
    write_log(pull_dir, log)
    return row


# ---------------------------------------------------------------------------------------------- build

def _rings(geom, digits):
    """Every ring of a polygon or multipolygon (outer rings and holes alike: the page fills them even-odd)."""
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = [[round(x, digits), round(y, digits)] for x, y in ring.coords]
            pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
            if len(pts) >= 4:
                out.append(pts)
    return out


def build(a):
    """The raw GeoJSON to the site file. Exit 0 written, 1 refused (said why), 2 bad input."""
    from pyproj import Geod
    from shapely.geometry import shape
    from shapely.ops import unary_union
    from shapely.validation import make_valid

    with open(a.raw, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    with open(a.requests, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["sha256"] == sha]
    if not rows:
        print(f"REFUSED: no row of {a.requests} holds the raw file's sha256 ({sha}); a file with no logged request is not built from.")
        return 1
    req = rows[-1]
    try:
        feats = json.loads(raw.decode("utf-8"))["features"]
    except Exception as e:
        print(f"BAD INPUT: {a.raw} is not a GeoJSON FeatureCollection ({type(e).__name__}: {e})")
        return 2
    props = sorted({k for f in feats for k in (f.get("properties") or {})})
    with open(a.network, encoding="utf-8") as f:
        nodes = json.load(f)["nodes"]
    ids = [n["id"] for n in nodes]
    if a.code_field not in props:
        # which property holds the EIA-930 codes is a person's reading of the file: say what each would match, choose none
        print(f"REFUSED: the file has no property named {a.code_field!r}. Its properties, with the nodes each matches exactly:")
        for k in props:
            vals = {str((f.get("properties") or {}).get(k, "")).strip() for f in feats}
            print(f"  {k}: {len(vals & set(ids))} of {len(ids)} nodes")
        return 1
    by = {}
    for f in feats:
        pr = f.get("properties") or {}
        code = str(pr.get(a.code_field, "")).strip()
        if not f.get("geometry"):
            continue
        g = make_valid(shape(f["geometry"]))
        by.setdefault(code, {"name": str(pr.get(a.name_field, "")).strip() if a.name_field else "", "parts": []})["parts"].append(g)
    geod = Geod(ellps="WGS84")
    regions, tiny = [], 0
    for nid in ids:
        if nid not in by:   # exact, or not at all: no name is compared, nothing is guessed
            continue
        g = unary_union(by[nid]["parts"])
        area_full = abs(geod.geometry_area_perimeter(g)[0]) / 1e6
        s = g.simplify(a.tolerance, preserve_topology=True) if a.tolerance > 0 else g
        polys = [p for p in ([s] if s.geom_type == "Polygon" else list(getattr(s, "geoms", []))) if p.geom_type == "Polygon"]
        keep = [p for p in polys if p.area >= a.tolerance * a.tolerance] or sorted(polys, key=lambda p: -p.area)[:1]
        tiny += len(polys) - len(keep)
        if not keep:
            continue
        rings = _rings(unary_union(keep), a.digits)
        if not rings:
            continue
        pt = max(keep, key=lambda p: p.area).representative_point()
        regions.append({"id": nid, "source_name": by[nid]["name"], "area_km2": round(area_full), "point": [round(pt.x, a.digits), round(pt.y, a.digits)],
                        "rings": rings})
    regions.sort(key=lambda r: -r["area_km2"])   # the largest first: a balancing authority inside another is drawn on top of it
    drawn = {r["id"] for r in regions}
    out = {
        "what": "The boundaries of the balancing authorities the network page draws, simplified for the web. Reference geometry, not a table.",
        "provenance": {
            "source": a.source, "publisher": a.publisher, "title": a.title, "vintage": a.vintage,
            "url": req["url"], "retrieved_utc": req["retrieved_utc"], "raw_bytes": len(raw), "raw_sha256": sha,
            "license_quoted": a.license_quoted, "terms_url": a.terms_url, "code_field": a.code_field,
            "simplification": {
                "method": "each balancing authority's parts joined (shapely unary_union), then Douglas-Peucker with topology kept (shapely simplify, preserve_topology)",
                "tolerance_degrees": a.tolerance, "coordinate_digits": a.digits,
                "parts_dropped_smaller_than_square_degrees": a.tolerance * a.tolerance, "parts_dropped": tiny,
                "note": "each shape is simplified on its own, so two neighbours' shared border may open or overlap by up to the tolerance"},
            "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "builder": "warehouse/connectors/eia_ba_boundaries.py build",
        },
        "order": "largest area first; the page draws in this order, so a smaller balancing authority is on top of a larger one it sits inside",
        "nodes": len(ids), "matched": len(regions),
        "nodes_without_shape": [{"id": n["id"], "name": n["name"]} for n in nodes if n["id"] not in drawn],
        "shapes_without_node": sorted(({"code": c, "name": v["name"]} for c, v in by.items() if c not in drawn), key=lambda x: x["code"]),
        "regions": regions,
    }
    text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    size = len(text.encode("utf-8"))
    print(f"{len(regions)} of {len(ids)} nodes have a shape; {len(out['shapes_without_node'])} shapes have no node; tolerance {a.tolerance} degrees; {size} bytes")
    for n in out["nodes_without_shape"]:
        print(f"  no shape: {n['id']} {n['name']}")
    for x in out["shapes_without_node"]:
        print(f"  no node: {x['code']} {x['name']}")
    if size > a.max_out_bytes:
        print(f"REFUSED: {size} bytes is over the ceiling of {a.max_out_bytes}; raise --tolerance. Nothing written.")
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    os.replace(tmp, a.out)
    print(f"wrote {a.out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get", help="one logged request")
    g.add_argument("url")
    g.add_argument("name", help="the file name to save under (in its own new directory of the pull directory)")
    g.add_argument("--pull-dir", required=True)
    g.add_argument("--max-requests", type=int, default=5)
    g.add_argument("--max-bytes", type=int, default=200_000_000)
    g.add_argument("--robots", help="a saved robots file of the URL's host: the request is refused if it disallows the URL")
    g.add_argument("--note", default="")
    g.add_argument("--min-gap", type=int, default=0, help="seconds since the last request to the same host (the robots file's Crawl-delay)")
    b = sub.add_parser("build", help="the raw file to the site file; no request")
    b.add_argument("--raw", required=True, help="the publisher's GeoJSON as it came")
    b.add_argument("--requests", required=True, help="the request log that holds the raw file's row")
    b.add_argument("--network", default=os.path.join(ROOT, "site", "data", "grid_network.json"))
    b.add_argument("--out", default=os.path.join(ROOT, "site", "public", "network", "ba_boundaries.json"))
    b.add_argument("--code-field", required=True, help="the property that holds each shape's EIA-930 code; named by a person who has read the file, never guessed")
    b.add_argument("--name-field", default="", help="the property that holds the publisher's name of the shape (kept beside it, never matched on)")
    b.add_argument("--tolerance", type=float, default=0.02, help="Douglas-Peucker tolerance, degrees (0.02 is about 2 km)")
    b.add_argument("--digits", type=int, default=3, help="decimals kept in a coordinate (3 is about 100 m)")
    b.add_argument("--max-out-bytes", type=int, default=400_000)
    b.add_argument("--source", default=SOURCE_ID, help="the id the source has, or will have, in warehouse/metadata/sources.csv")
    b.add_argument("--publisher", required=True)
    b.add_argument("--title", required=True, help="the publisher's title of the file")
    b.add_argument("--vintage", required=True, help="the date the publisher gives the boundaries")
    b.add_argument("--license-quoted", required=True, help="the publisher's own words that make the file public domain or equivalent")
    b.add_argument("--terms-url", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "get":
        row = get(a.url, a.name, a.pull_dir, a.max_requests, a.max_bytes, a.robots, a.note, a.min_gap)
        print(json.dumps(row))
        return 0 if row["status"] == "200" and "STOPPED" not in row["note"] else 1
    return build(a)


if __name__ == "__main__":
    sys.exit(main())
