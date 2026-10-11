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
         followed: a redirect is a request, and it is counted like one. The command refuses, before anything is sent,
         to pass the ceilings it is given (requests and bytes, the session's: 5 and 200 MB), to ask for a path the
         host's saved robots file disallows (--robots), and to ask the same host again sooner than the robots file's
         Crawl-delay (--min-gap).
  build  the raw GeoJSON, read from disk, to the site file. No request. Matching is exact: a shape is given to a node
         only when the publisher's own code for it is the node's EIA-930 code; nothing is matched by name or by guess.
         Every node with no shape and every shape with no node is listed in the provenance record.

Real data only: a shape that is not in the publisher's file is not drawn from anything else.

10 October 2026: the session's five requests, all to EIA's U.S. Energy Atlas (atlas.eia.gov), reached no boundary file
(docs/methods/grid_network.md, "The map", has each request and its answer). So no site file exists yet, the map says
the boundary file is not yet held, and the source registry has no row for it. The file is named for EIA because the
atlas was the publisher asked; --source names another publisher's file when a person rules which one is pulled.

10 October 2026, session 180b: the owner approved HIFLD's "Control Areas" layer (the Homeland Infrastructure
Foundation-Level Data open catalog on ArcGIS Hub), ten requests and 300 MB. Six were sent and none reached the layer:
the catalog's site answers "Item does not exist or is inaccessible" at hifld-geoplatform.hub.arcgis.com and "Site does
not exist" at hifld-geoplatform.opendata.arcgis.com, and the host that used to serve its layers answers 403 to a
request for its robots file, so nothing more was asked of it. Still no site file and no registry row. Since this
session `get` also keeps each answer's headers beside it (<name>.headers.txt, cookies left out) and writes the content
type into the log's note, so an answer that is not a file can be reported exactly as it came.

11 October 2026, session 193: a third pull, thirty requests and 300 MB allowed, twelve sent. EIA's own site holds no
boundary of the balancing authorities: its list of map layers now answers with the atlas's search (session 180), and
the Hourly Electric Grid Monitor draws thirteen regions (REG-CAL to REG-TEN, shapes inside its program) with each
balancing authority as a point. NREL's ReEDS publishes 134 model regions (p1 to p134) that carry no EIA-930 code. So
a third command was written:

  counties  a DERIVED map, and labeled as one wherever it is drawn. Each county is given to one balancing authority
            from EIA-861's annual files (Service_Territory: the counties each utility serves; Sales_Ult_Cust, the
            delivery companies' file and the short form: each utility's balancing authority and customers in a state), and a balancing authority's
            area is the counties given to it. County shapes are the Census Bureau's cartographic boundary files as
            the site's own package redistributes them (us-atlas). No request. It is not a published boundary and the
            site file says so in its provenance (derived, label, rule). docs/methods/grid_network.md has the rule.
"""
import argparse
import calendar
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
import urllib.robotparser
import zipfile

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


def robots_status(pull_dir, robots_path):
    """The status the saved robots file's own request answered, read from the request log ('' when the log has no
    row for that file)."""
    want = os.path.normcase(os.path.abspath(robots_path))
    for r in read_log(pull_dir):
        if r.get("saved_as") and os.path.normcase(os.path.abspath(os.path.join(pull_dir, r["saved_as"]))) == want:
            return str(r["status"])
    return ""


def get(url, name, pull_dir, max_requests, max_bytes, robots=None, note="", min_gap=0):
    """One request. Returns the log row. Raises SystemExit before sending when a ceiling or a rule forbids it."""
    sys.path.insert(0, HERE)
    import iso_prices  # the pause register: a paused publisher's host is never asked
    host = urllib.parse.urlsplit(url).hostname or ""
    if iso_prices.paused_host(host):
        raise SystemExit(f"REFUSED: {host} belongs to a paused publisher (warehouse/metadata/paused_sources.csv). No request made.")
    # session 180b: a host that answers 401 or 403 to the request for its robots file has given no file to read. The
    # standard library's reader (urllib.robotparser.read) takes that as every path disallowed, and so does this step:
    # what was saved is the refusal's body, not rules, and parsing it would allow everything.
    if robots and robots_status(pull_dir, robots) in ("401", "403"):
        raise SystemExit(f"REFUSED: the request for the robots file {robots} answered {robots_status(pull_dir, robots)}, "
                         "which is read as every path disallowed until a person rules otherwise. No request made.")
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
        # session 180b: the answer's own headers are kept beside it (the content type, the length, the date), so a
        # request that reaches no file can be reported exactly as it answered. Cookies are not kept.
        with open(out + ".headers.txt", "w", encoding="utf-8", newline="\n") as hf:
            hf.write(f"status: {status}\n")
            for k, v in resp.headers.items():
                if k.lower() != "set-cookie":
                    hf.write(f"{k}: {v}\n")
        ctype = resp.headers.get("Content-Type")
        if ctype:
            extra = (extra + " " if extra else "") + f"Content-Type: {ctype}"
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
        resp.close()
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


# ---------------------------------------------------------------------------------------------- counties (derived)

STATE_FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
              "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
              "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
              "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
              "54": "WV", "55": "WI", "56": "WY"}
DERIVED_LABEL = ("Derived map: each county is given to one balancing authority from the utilities that serve it (EIA-861). "
                 "It is not a boundary any balancing authority or agency published.")


def county_key(name):
    """A county's name as it is compared: accents and case dropped, the words county, parish, borough, census area and
    municipality dropped, Saint written St, then letters and digits only. "City" is kept: it is part of a name."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii").lower().strip()
    s = re.sub(r"\b(county|parish|borough|census area|municipality|city and borough)\b", "", s)
    s = re.sub(r"\bsainte\b", "ste", re.sub(r"\bsaint\b", "st", s))
    return re.sub(r"[^a-z0-9]", "", s)


def county_index(geoms):
    """{(state, name key): [county codes]} of the county shapes, and each code's own name."""
    by, names = {}, {}
    for g in geoms:
        st = STATE_FIPS.get(g["id"][:2])
        if st:
            by.setdefault((st, county_key(g["properties"]["name"])), []).append(g["id"])
            names[g["id"]] = g["properties"]["name"]
    return by, names


def county_code(index, state, name):
    """The county code of a state and a county name as EIA-861 writes them, or None. Exact on the name key. Where a
    state has a county and an independent city of one name (Virginia, Baltimore, St. Louis: the city's code ends in
    510 or more), the plain name is the county and "<name> City" is the city."""
    k = county_key(name)
    hit = index.get((state, k))
    if hit and len(hit) == 1:
        return hit[0]
    if hit:                                                # a county and a city of the same name: the plain name is the county
        low = [c for c in hit if int(c[2:]) < 500]
        return low[0] if len(low) == 1 else None
    if k.endswith("city"):                                 # "Norfolk City": the independent city of that name
        hit = index.get((state, k[:-4]))
        if hit:
            high = [c for c in hit if int(c[2:]) >= 500]
            return high[0] if len(high) == 1 else (hit[0] if len(hit) == 1 else None)
    return None


def _sheet(zf, member, sheet, skip):
    """The data rows of one sheet of a workbook inside the zip, after its heading rows: the rows whose first cell is a year."""
    import openpyxl
    ws = openpyxl.load_workbook(io.BytesIO(zf.read(member)), read_only=True, data_only=True)[sheet]
    return [r for i, r in enumerate(ws.iter_rows(values_only=True)) if i >= skip and r and r[0] is not None and str(r[0]).strip().isdigit()]


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def read_861(zip_path, year):
    """(territory {(utility, state): {county names}}, weight {(utility, state): {BA code: customers}}) from EIA-861's zip.
    Customers are those of the wires: Parts A, C and D of Sales_Ult_Cust, the delivery companies' file (Texas's
    delivery utilities report there and not in Sales_Ult_Cust) and the short form. Part B (energy sold by a marketer
    over another utility's wires) is left out: its customers are Part C's."""
    zf = zipfile.ZipFile(zip_path)
    terr, weight = {}, {}
    for r in _sheet(zf, f"Service_Territory_{year}.xlsx", "Counties_States", 1):
        terr.setdefault((str(r[1]).strip(), str(r[4]).strip()), set()).add(str(r[5]).strip())
    for member, sheet in ((f"Sales_Ult_Cust_{year}.xlsx", "States"), (f"Delivery_Companies_{year}.xlsx", "Delivery Companies")):
        for r in _sheet(zf, member, sheet, 3):
            if str(r[3]).strip() in ("A", "C", "D") and r[8] not in (None, ""):
                w = weight.setdefault((str(r[1]).strip(), str(r[6]).strip()), {})
                w[str(r[8]).strip()] = w.get(str(r[8]).strip(), 0.0) + _num(r[23])
    for r in _sheet(zf, f"Short_Form_{year}.xlsx", "861S", 1):
        if r[5] not in (None, ""):
            w = weight.setdefault((str(r[1]).strip(), str(r[4]).strip()), {})
            w[str(r[5]).strip()] = w.get(str(r[5]).strip(), 0.0) + _num(r[8])
    return terr, weight


def assign_counties(terr, weight, index):
    """Each county to one balancing authority code. A utility's customers in a state, under each of its codes, are
    split evenly over the counties it serves there; a county goes to the code with the most customers so allotted.
    Where no utility of a county reports a customer, the code most of its utilities name. A tie is no assignment.
    Returns ({county code: (BA code, its share of the county's allotted customers, how many codes were named)}, a
    record of what was left out)."""
    allot, named, left = {}, {}, {"county_names_not_in_the_shapes": set(), "utility_states_without_a_code": 0, "ties": []}
    for (util, state), names in sorted(terr.items()):
        codes = weight.get((util, state))
        if not codes:
            left["utility_states_without_a_code"] += 1
            continue
        fips = set()
        for name in names:
            c = county_code(index, state, name)
            if c is None:
                left["county_names_not_in_the_shapes"].add(f"{state}: {name}")
            else:
                fips.add(c)
        for c in sorted(fips):
            for code, cust in codes.items():
                allot.setdefault(c, {})
                allot[c][code] = allot[c].get(code, 0.0) + cust / len(fips)
                named.setdefault(c, {})
                named[c][code] = named[c].get(code, 0) + 1
    out = {}
    for c, by in allot.items():
        total = sum(by.values())
        rank = sorted(by.items(), key=lambda kv: (-kv[1], kv[0])) if total > 0 else sorted(((k, float(v)) for k, v in named[c].items()), key=lambda kv: (-kv[1], kv[0]))
        if len(rank) > 1 and rank[0][1] == rank[1][1]:
            left["ties"].append(c)
            continue
        out[c] = (rank[0][0], round(rank[0][1] / total, 4) if total > 0 else None, len(by))
    left["county_names_not_in_the_shapes"] = sorted(left["county_names_not_in_the_shapes"])
    return out, left


def topo_polygons(topo, obj="counties"):
    """{id: shapely geometry} of a TopoJSON object: the arcs decoded (their deltas summed, the transform applied) and
    each geometry's rings put together from them. Shared borders keep the same points on both sides."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from shapely.validation import make_valid
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for a in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts += a if not pts else a[1:]
        return pts

    def poly(rings):
        rs = [ring(r) for r in rings]
        return Polygon(rs[0], [h for h in rs[1:] if len(h) >= 4]) if len(rs[0]) >= 4 else None

    out = {}
    for g in topo["objects"][obj]["geometries"]:
        parts = [poly(g["arcs"])] if g["type"] == "Polygon" else [poly(p) for p in g["arcs"]] if g["type"] == "MultiPolygon" else []
        parts = [make_valid(p) for p in parts if p is not None]
        if parts:
            out[g["id"]] = unary_union(parts)
    return out


def counties(a):
    """EIA-861's zip and the county shapes to the site file, a derived map. Exit 0 written, 1 refused, 2 bad input."""
    from pyproj import Geod
    from shapely.ops import unary_union

    with open(a.zip, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    with open(a.requests, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["sha256"] == sha]
    if not rows:
        print(f"REFUSED: no row of {a.requests} holds the zip's sha256 ({sha}); a file with no logged request is not built from.")
        return 1
    req = rows[-1]
    with open(a.county_shapes, "rb") as f:
        shapes_raw = f.read()
    topo = json.loads(shapes_raw.decode("utf-8"))
    index, county_names = county_index(topo["objects"]["counties"]["geometries"])
    try:
        terr, weight = read_861(a.zip, a.year)
    except KeyError as e:
        print(f"BAD INPUT: {a.zip} does not hold the workbook or the sheet this reads ({e})")
        return 2
    given, left = assign_counties(terr, weight, index)
    with open(a.network, encoding="utf-8") as f:
        nodes = json.load(f)["nodes"]
    ids = [n["id"] for n in nodes]
    polys = topo_polygons(topo)
    by = {}
    for c, (code, share, n) in given.items():
        if c in polys:
            by.setdefault(code, []).append(c)
    geod = Geod(ellps="WGS84")
    regions, tiny = [], 0
    for nid in ids:
        if nid not in by:                                   # exact on EIA's own code, or not at all
            continue
        g = unary_union([polys[c] for c in by[nid]])
        area_full = abs(geod.geometry_area_perimeter(g)[0]) / 1e6
        s = g.simplify(a.tolerance, preserve_topology=True) if a.tolerance > 0 else g
        parts = [p for p in ([s] if s.geom_type == "Polygon" else list(getattr(s, "geoms", []))) if p.geom_type == "Polygon"]
        keep = [p for p in parts if p.area >= a.tolerance * a.tolerance] or sorted(parts, key=lambda p: -p.area)[:1]
        tiny += len(parts) - len(keep)
        rings = _rings(unary_union(keep), a.digits) if keep else []
        if not rings:
            continue
        pt = max(keep, key=lambda p: p.area).representative_point()
        shares = [given[c][1] for c in by[nid] if given[c][1] is not None]
        regions.append({"id": nid, "source_name": next(n["name"] for n in nodes if n["id"] == nid), "area_km2": round(area_full),
                        "point": [round(pt.x, a.digits), round(pt.y, a.digits)], "counties": len(by[nid]),
                        "counties_with_another_code": sum(1 for c in by[nid] if given[c][2] > 1),
                        "least_share_of_a_county": min(shares) if shares else None, "rings": rings})
    regions.sort(key=lambda r: -r["area_km2"])
    drawn = {r["id"] for r in regions}
    lower48 = [c for c in polys if STATE_FIPS.get(c[:2]) not in (None, "AK", "HI")]
    one = sum(1 for c in given if given[c][2] == 1)
    out = {
        "what": "The areas of the balancing authorities the network page draws, DERIVED by the ERW from counties: each county is given to one "
                "balancing authority from the utilities that serve it. Not a published boundary. Reference geometry, not a table.",
        "provenance": {
            "derived": True, "label": DERIVED_LABEL,
            "source": a.source, "publisher": "U.S. Energy Information Administration (EIA); county shapes: U.S. Census Bureau",
            "title": f"Annual Electric Power Industry Report, Form EIA-861 detailed data files, {a.year} (Service_Territory, Sales_Ult_Cust, Delivery_Companies, Short_Form)",
            "vintage": a.vintage, "url": req["url"], "retrieved_utc": req["retrieved_utc"], "raw_bytes": len(raw), "raw_sha256": sha,
            "license_quoted": a.license_quoted, "terms_url": a.terms_url, "code_field": "BA Code (Sales_Ult_Cust, Delivery_Companies, Short_Form)",
            "county_shapes": {"file": a.county_shapes_name, "sha256": hashlib.sha256(shapes_raw).hexdigest(), "bytes": len(shapes_raw),
                              "origin": a.county_shapes_origin, "counties": len(polys)},
            "rule": "A utility's customers in a state under each of its balancing authority codes (Parts A, C and D of Sales_Ult_Cust, the delivery companies' file and the short form) are "
                    "split evenly over the counties Service_Territory lists for it in that state. A county is given to the code with the most customers so "
                    "allotted; where no utility of a county reports a customer, to the code most of its utilities name; a tie is no assignment. A balancing "
                    "authority's area is the counties given to it, joined. A code that is not one of the page's grids is not drawn.",
            "simplification": {
                "method": "each balancing authority's counties joined (shapely unary_union), then Douglas-Peucker with topology kept (shapely simplify, preserve_topology)",
                "tolerance_degrees": a.tolerance, "coordinate_digits": a.digits,
                "parts_dropped_smaller_than_square_degrees": a.tolerance * a.tolerance, "parts_dropped": tiny,
                "note": "each area is simplified on its own, so two neighbours' shared border may open or overlap by up to the tolerance"},
            "counts": {"counties_in_the_shapes": len(polys), "counties_of_the_lower_48_and_dc": len(lower48), "counties_given_a_code": len(given),
                       "counties_whose_utilities_name_one_code": one, "counties_whose_utilities_name_several_codes": len(given) - one,
                       "counties_drawn": sum(r["counties"] for r in regions),
                       "counties_of_the_lower_48_not_drawn": sum(1 for c in lower48 if c not in given or given[c][0] not in drawn),
                       "counties_given_a_code_with_no_shape": sorted(c for c in given if c not in polys),
                       "utility_states_with_a_territory": len(terr), "utility_states_without_a_code": left["utility_states_without_a_code"],
                       "county_ties": len(left["ties"])},
            "county_names_not_in_the_shapes": left["county_names_not_in_the_shapes"],
            "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "builder": "warehouse/connectors/eia_ba_boundaries.py counties",
        },
        "order": "largest area first; the page draws in this order. No two areas overlap: a county has one balancing authority here",
        "nodes": len(ids), "matched": len(regions),
        "nodes_without_shape": [{"id": n["id"], "name": n["name"]} for n in nodes if n["id"] not in drawn],
        "shapes_without_node": sorted(({"code": c, "name": "", "counties": len(v)} for c, v in by.items() if c not in drawn), key=lambda x: x["code"]),
        "regions": regions,
    }
    text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    size = len(text.encode("utf-8"))
    k = out["provenance"]["counts"]
    print(f"{len(regions)} of {len(ids)} grids have an area; {k['counties_drawn']} counties drawn of {k['counties_of_the_lower_48_and_dc']} in the lower 48 and DC; "
          f"{k['counties_whose_utilities_name_several_codes']} of {k['counties_given_a_code']} counties given a code had utilities of several; tolerance {a.tolerance} degrees; {size} bytes")
    for n in out["nodes_without_shape"]:
        print(f"  no area: {n['id']} {n['name']}")
    for x in out["shapes_without_node"]:
        print(f"  no grid: {x['code']} ({x['counties']} counties)")
    print(f"  county names of EIA-861 not in the shapes: {len(left['county_names_not_in_the_shapes'])}; utility-states without a code: {left['utility_states_without_a_code']}; ties: {len(left['ties'])}")
    if size > a.max_out_bytes:
        print(f"REFUSED: {size} bytes is over the ceiling of {a.max_out_bytes}; raise --tolerance. Nothing written.")
        return 1
    if a.assignments:
        os.makedirs(os.path.dirname(os.path.abspath(a.assignments)), exist_ok=True)
        with open(a.assignments, "w", encoding="utf-8", newline="") as f:
            f.write("# Energy Research Warehouse (ERW): each county's balancing authority, DERIVED by the ERW (not a published boundary).\n"
                    f"# Source: {out['provenance']['title']}, {req['url']}, retrieved {req['retrieved_utc']}, sha256 {sha}.\n"
                    f"# County codes and names: {a.county_shapes_name} ({a.county_shapes_origin}).\n"
                    f"# Rule: {out['provenance']['rule']}\n"
                    "# share_of_allotted_customers: the given code's share of the customers allotted to the county; codes_named: how many codes the county's "
                    "utilities name; drawn: whether the code is one of the network page's grids. Method: docs/methods/grid_network.md.\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["county_code", "state", "county", "ba_code", "share_of_allotted_customers", "codes_named", "drawn"])
            for c in sorted(given):
                w.writerow([c, STATE_FIPS[c[:2]], county_names[c], given[c][0], "" if given[c][1] is None else given[c][1], given[c][2], "yes" if given[c][0] in drawn and c in polys else "no"])
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
    c = sub.add_parser("counties", help="a derived map from EIA-861 and county shapes; no request")
    c.add_argument("--zip", required=True, help="EIA-861's annual zip as it came")
    c.add_argument("--requests", required=True, help="the request log that holds the zip's row")
    c.add_argument("--year", required=True, help="the data year in the workbooks' names (Service_Territory_<year>.xlsx)")
    c.add_argument("--county-shapes", default=os.path.join(ROOT, "site", "node_modules", "us-atlas", "counties-10m.json"))
    c.add_argument("--county-shapes-name", default="us-atlas 3.0.1, counties-10m.json")
    c.add_argument("--county-shapes-origin", default="the U.S. Census Bureau's cartographic boundary files, 2017 edition, as TopoJSON (the us-atlas package the site already uses; no request)")
    c.add_argument("--network", default=os.path.join(ROOT, "site", "data", "grid_network.json"))
    c.add_argument("--out", default=os.path.join(ROOT, "site", "public", "network", "ba_boundaries.json"))
    c.add_argument("--assignments", default="", help="also write every county's balancing authority here (a CSV for a reader to check)")
    c.add_argument("--tolerance", type=float, default=0.02)
    c.add_argument("--digits", type=int, default=3)
    c.add_argument("--max-out-bytes", type=int, default=400_000)
    c.add_argument("--source", default="erw:balancing_authority_counties", help="the id the derived map has in warehouse/metadata/sources.csv")
    c.add_argument("--vintage", required=True, help="the date EIA gives the files")
    c.add_argument("--license-quoted", required=True, help="EIA's own words on reuse")
    c.add_argument("--terms-url", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "counties":
        return counties(a)
    if a.cmd == "get":
        row = get(a.url, a.name, a.pull_dir, a.max_requests, a.max_bytes, a.robots, a.note, a.min_gap)
        print(json.dumps(row))
        return 0 if row["status"] == "200" and "STOPPED" not in row["note"] else 1
    return build(a)


if __name__ == "__main__":
    sys.exit(main())
