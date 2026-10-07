#!/usr/bin/env python3
"""Natural resource layers for "Where the resources are" (session 146).

What this connector does
  --pull    downloads each publisher's own file into the raw store, under one ceiling for all of them
            (4 GB). The size is asked first; a download that would pass the ceiling is refused before a
            byte of it is read. Every file, and every terms page, is one row of downloads.csv.
  --build   reduces each raw file to a web-sized layer in site/public/resources-data/ and describes it in
            site/data/resources/manifest.json (the contract with the page). The raw file keeps the full
            resolution; nothing is filled, smoothed or interpolated.
  --only    one layer id (or several, comma separated).
  --out-dir a trial folder for the web layers and the manifest, instead of the site's.

Self-contained: no import from another connector. The geospatial libraries it needs for --build are in
resource_layers.requirements.txt (not in requirements.txt: the daily runner does not build these layers).

Run it on downloaded files with python -I (the archives are untrusted data).
The only contact string this connector ever sends is its User-Agent, below. No e-mail address.
"""
import argparse
import base64
import csv
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import zipfile

UA = "ERW research project, github.com/SamuelEnrique/erw"
CEILING_BYTES = 4 * 1024 ** 3
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RAW_DIR = os.environ.get("ERW_RESOURCES_RAW") or os.path.join(REPO, "warehouse", "raw", "resources")
WEB_DIR = os.path.join(REPO, "site", "public", "resources-data")
MANIFEST = os.path.join(REPO, "site", "data", "resources", "manifest.json")
PAUSED_FILE = os.path.join(REPO, "warehouse", "metadata", "paused_sources.csv")
LEDGER_COLS = ["source", "layer", "url", "file", "bytes", "sha256", "retrieved_at_utc", "http_status",
               "terms_url", "terms_file", "terms_sha256"]
# never requested, whatever a source list says (CLAUDE.md, COMMON.md rule 6)
FORBIDDEN = re.compile(r"(?i)misoenergy\.org|pjm\.com")
NODATA = 65535
LEVELS = [0.2, 0.1, 0.05, 0.025]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print(f"[resource_layers {now_utc()}] {msg}", flush=True)


# ---------------------------------------------------------------------------------------------------------
# The raw store: the ledger, the ceiling, the downloads
# ---------------------------------------------------------------------------------------------------------

class CeilingRefused(Exception):
    """A download that would pass the ceiling. Raised before the download starts."""


class Paused(Exception):
    """A publisher that is never requested."""


def refuse_paused(url):
    if FORBIDDEN.search(url):
        raise Paused(f"never requested: {url}")
    if os.path.exists(PAUSED_FILE):
        with open(PAUSED_FILE, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("match") and re.search(r["match"], url):
                    raise Paused(f"paused publisher ({r.get('scope')}): {url}")


def ledger_path(raw_dir):
    return os.path.join(raw_dir, "downloads.csv")


def read_ledger(raw_dir):
    p = ledger_path(raw_dir)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ledger_total(rows):
    """Every byte read from a publisher counts, a terms page and an aborted read included."""
    return sum(int(r["bytes"] or 0) for r in rows)


def append_ledger(raw_dir, row):
    os.makedirs(raw_dir, exist_ok=True)
    p = ledger_path(raw_dir)
    new = not os.path.exists(p)
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        if new:
            w.writeheader()
        w.writerow({c: row.get(c, "") for c in LEDGER_COLS})


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def http_session():
    import requests
    s = requests.Session()
    s.headers.clear()
    s.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "identity"})
    return s


def ask_size(sess, url):
    """The size the server states for url, asked without reading the file: (bytes or None, status)."""
    r = sess.head(url, allow_redirects=True, timeout=60)
    n = r.headers.get("Content-Length", "")
    if r.status_code == 200 and n.isdigit() and int(n) > 0:
        return int(n), r.status_code
    r = sess.get(url, headers={"Range": "bytes=0-0"}, stream=True, allow_redirects=True, timeout=60)
    try:
        m = re.match(r"bytes \d+-\d+/(\d+)", r.headers.get("Content-Range", ""))
        if m:
            return int(m.group(1)), 200
        n = r.headers.get("Content-Length", "")
        if r.status_code == 200 and n.isdigit() and int(n) > 0:
            return int(n), r.status_code
        return None, r.status_code
    finally:
        r.close()


def fetch(sess, raw_dir, source, layer, url, file, terms=None, ceiling=CEILING_BYTES):
    """Download url to <raw_dir>/<source>/<file> under the ceiling. Returns the path.

    The size is asked first and the download is refused (CeilingRefused) when the bytes already in the
    ledger plus this file would pass the ceiling. A server that states no size is read with the remaining
    budget as a hard stop: the read ends before the byte that would pass the ceiling.
    """
    refuse_paused(url)
    rows = read_ledger(raw_dir)
    dest = os.path.join(raw_dir, source, file)
    held = [r for r in rows if r["source"] == source and r["file"] == file and r["http_status"] == "200"]
    if held and os.path.exists(dest) and sha256_file(dest) == held[-1]["sha256"]:
        log(f"held: {source}/{file} ({held[-1]['bytes']} bytes)")
        return dest
    spent = ledger_total(rows)
    size, status = ask_size(sess, url)
    if size is not None and spent + size > ceiling:
        raise CeilingRefused(f"{source}/{file}: {size} bytes asked, {spent} already read, ceiling {ceiling}")
    if size is None and status not in (200, 206):
        raise RuntimeError(f"{source}/{file}: HTTP {status} from {url}")
    budget = ceiling - spent
    if budget <= 0:
        raise CeilingRefused(f"{source}/{file}: nothing left under the ceiling ({spent} of {ceiling})")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):  # never overwrite a raw file: a changed file is kept beside the old one
        stem, ext = os.path.splitext(file)
        file = f"{stem}.{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}{ext}"
        dest = os.path.join(raw_dir, source, file)
    part = dest + ".part"
    got = 0
    h = hashlib.sha256()
    r = sess.get(url, stream=True, allow_redirects=True, timeout=120)
    try:
        if r.status_code != 200:
            raise RuntimeError(f"{source}/{file}: HTTP {r.status_code} from {url}")
        with open(part, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                if got + len(chunk) > budget:
                    f.close()
                    os.remove(part)
                    append_ledger(raw_dir, {"source": source, "layer": layer, "url": url, "file": file,
                                            "bytes": got, "retrieved_at_utc": now_utc(),
                                            "http_status": "stopped at the ceiling"})
                    raise CeilingRefused(f"{source}/{file}: stopped at {got} bytes, the ceiling")
                f.write(chunk)
                h.update(chunk)
                got += len(chunk)
    finally:
        r.close()
    os.replace(part, dest)
    row = {"source": source, "layer": layer, "url": url, "file": file, "bytes": got, "sha256": h.hexdigest(),
           "retrieved_at_utc": now_utc(), "http_status": "200"}
    if terms:
        row.update({"terms_url": terms["url"], "terms_file": terms["file"], "terms_sha256": terms["sha256"]})
    append_ledger(raw_dir, row)
    log(f"pulled: {source}/{file} {got} bytes (stated {size}); total {spent + got} of {ceiling}")
    return dest


def fetch_terms(sess, raw_dir, source, key, ceiling=CEILING_BYTES):
    """The publisher's terms page, saved as it came, with its hash. Returns {"url", "file", "sha256"}."""
    t = TERMS[key]
    file = os.path.join("terms", t["file"]).replace("\\", "/")
    path = fetch(sess, raw_dir, source, "terms", t["url"], file, ceiling=ceiling)
    rel = os.path.relpath(path, raw_dir).replace("\\", "/")
    return {"url": t["url"], "file": rel, "sha256": sha256_file(path)}


def unpack(zip_path):
    """Unpack an archive into its own new folder beside it (untrusted: no path may leave the folder)."""
    out = os.path.join(os.path.dirname(zip_path), "unpacked", os.path.splitext(os.path.basename(zip_path))[0])
    if os.path.isdir(out) and os.listdir(out):
        return out
    os.makedirs(out, exist_ok=True)
    root = os.path.realpath(out)
    with zipfile.ZipFile(zip_path) as z:
        for m in z.infolist():
            target = os.path.realpath(os.path.join(out, m.filename))
            if not (target == root or target.startswith(root + os.sep)):
                raise RuntimeError(f"archive member leaves its folder: {m.filename}")
        z.extractall(out)
    return out


def find_file(folder, pattern):
    rx = re.compile(pattern, re.I)
    hits = []
    for d, _, files in os.walk(folder):
        for f in files:
            if rx.search(f):
                hits.append(os.path.join(d, f))
    if not hits:
        raise FileNotFoundError(f"no file matching {pattern} under {folder}")
    return sorted(hits)[0]


def html_text(path):
    """The visible text of a saved page, whitespace collapsed: what a terms quote is checked against."""
    import html
    with open(path, "rb") as f:
        s = f.read().decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s).replace(" ", " ")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------------------------------------
# The web layers: the manifest, the grid encoding, the shape and point writers
# ---------------------------------------------------------------------------------------------------------

def write_json_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    os.replace(tmp, path)
    return os.path.getsize(path)


def read_manifest(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"built_at_utc": now_utc(), "layers": [], "missing": []}


def write_manifest(path, man):
    man["built_at_utc"] = now_utc()
    order = {k: i for i, k in enumerate(LAYER_ORDER)}
    man["layers"].sort(key=lambda l: order.get(l["id"], 999))
    man["missing"] = [m for m in man.get("missing", []) if m["id"] not in {l["id"] for l in man["layers"]}]
    man["missing"].sort(key=lambda l: order.get(l["id"], 999))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, ensure_ascii=False, indent=1, allow_nan=False)
        f.write("\n")
    os.replace(tmp, path)


def manifest_put(path, layer):
    man = read_manifest(path)
    man["layers"] = [l for l in man["layers"] if l["id"] != layer["id"]] + [layer]
    write_manifest(path, man)
    log(f"manifest: {layer['id']} ({layer['kind']}) written")


def manifest_missing(path, id, group, title, reason):
    man = read_manifest(path)
    if any(l["id"] == id for l in man["layers"]):
        return
    man["missing"] = [m for m in man.get("missing", []) if m["id"] != id] + [
        {"id": id, "group": group, "title": title, "reason": reason}]
    write_manifest(path, man)


def encode_grid(values, scale, offset=0.0):
    """A float array (NaN where empty) as uint16 little-endian base64, row-major, north to south."""
    import numpy as np
    v = np.asarray(values, dtype="float64")
    q = np.rint((v - offset) / scale)
    ok = np.isfinite(v)
    if ok.any() and (q[ok].min() < 0 or q[ok].max() >= NODATA):
        raise ValueError(f"values do not fit uint16 at scale {scale}: {q[ok].min()} to {q[ok].max()}")
    out = np.where(ok, q, NODATA).astype("<u2")
    return base64.b64encode(out.tobytes()).decode("ascii")


def decode_grid(obj):
    """The grid file back to a float array (NaN where empty)."""
    import numpy as np
    raw = np.frombuffer(base64.b64decode(obj["values"]), dtype="<u2").reshape(obj["nrows"], obj["ncols"])
    v = raw.astype("float64") * obj["scale"] + obj["offset"]
    v[raw == obj["nodata"]] = np.nan
    return v


def allowed_levels(source_cell_deg):
    """The pyramid's cell sizes for a source of this cell size: never finer than the source."""
    return [c for c in LEVELS if c + 1e-12 >= source_cell_deg]


def source_cell_deg(ds):
    """The source raster's cell size in degrees. For a projected raster: the wider of its north to south
    size and its east to west size at the northern edge of what it covers (where a degree of longitude is
    shortest), so that no level is finer than the source anywhere."""
    import pyproj
    if ds.crs.is_geographic:
        return max(abs(ds.transform.a), abs(ds.transform.e))
    tr = pyproj.Transformer.from_crs(ds.crs, 4326, always_xy=True)
    b = ds.bounds
    lats = [tr.transform(x, y)[1] for x in (b.left, (b.left + b.right) / 2, b.right) for y in (b.top, b.bottom)]
    north = min(max(lats), 89.0)
    unit = ds.crs.linear_units_factor[1] if ds.crs.linear_units_factor else 1.0
    dx = abs(ds.transform.a) * unit
    dy = abs(ds.transform.e) * unit
    return max(dy / 111320.0, dx / (111320.0 * math.cos(math.radians(north))))


def snap(v, step, up):
    k = v / step
    k = math.ceil(k - 1e-9) if up else math.floor(k + 1e-9)
    return round(k * step, 6)


def accumulate_raster(path, band, lon0, lat0, cell, ncols, nrows, valid=None, chunk_rows=256):
    """Assign every source cell centre to a cell of the target grid; return (sum, n_valid, n_cells, stats).

    n_cells counts every source cell whose centre falls in the target cell, valid or not, so that the
    half rule can be applied. Read by windows: memory stays small whatever the raster's size.
    """
    import numpy as np
    import pyproj
    import rasterio
    from rasterio.windows import Window
    n = ncols * nrows
    s = np.zeros(n)
    c = np.zeros(n)
    t = np.zeros(n)
    st = {"n_valid": 0, "sum": 0.0, "min": math.inf, "max": -math.inf, "n_cells": 0,
          "n_valid_in_grid": 0, "sum_in_grid": 0.0}
    with rasterio.open(path) as ds:
        tr = None if ds.crs.is_geographic else pyproj.Transformer.from_crs(ds.crs, 4326, always_xy=True)
        nod = ds.nodatavals[band - 1]
        T = ds.transform
        cols = np.arange(ds.width) + 0.5
        for r0 in range(0, ds.height, chunk_rows):
            h = min(chunk_rows, ds.height - r0)
            a = ds.read(band, window=Window(0, r0, ds.width, h)).astype("float64")
            ok = np.isfinite(a)
            if nod is not None and not (isinstance(nod, float) and math.isnan(nod)):
                ok &= a != nod
            if valid is not None:
                ok &= valid(a)
            rows = np.arange(r0, r0 + h) + 0.5
            cc, rr = np.meshgrid(cols, rows)
            x = T.a * cc + T.b * rr + T.c
            y = T.d * cc + T.e * rr + T.f
            if tr is not None:
                x, y = tr.transform(x, y)
            ci = np.floor((x - lon0) / cell).astype("int64")
            ri = np.floor((lat0 - y) / cell).astype("int64")
            inside = (ci >= 0) & (ci < ncols) & (ri >= 0) & (ri < nrows)
            idx = ri * ncols + ci
            t += np.bincount(idx[inside], minlength=n)
            m = inside & ok
            c += np.bincount(idx[m], minlength=n)
            s += np.bincount(idx[m], weights=a[m], minlength=n)
            st["n_cells"] += a.size
            if ok.any():
                st["n_valid"] += int(ok.sum())
                st["sum"] += float(a[ok].sum())
                st["min"] = min(st["min"], float(a[ok].min()))
                st["max"] = max(st["max"], float(a[ok].max()))
                st["n_valid_in_grid"] += int(m.sum())
                st["sum_in_grid"] += float(a[m].sum())
    return s.reshape(nrows, ncols), c.reshape(nrows, ncols), t.reshape(nrows, ncols), st


def coarsen(a, k):
    """Sum blocks of k by k cells."""
    r, c = a.shape
    return a.reshape(r // k, k, c // k, k).sum(axis=(1, 3))


def nice_stops(lo, hi, n=6):
    if not (math.isfinite(lo) and math.isfinite(hi)) or hi <= lo:
        return [lo, hi]
    raw = (hi - lo) / (n - 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = min((1, 2, 2.5, 5, 10), key=lambda m: abs(m * mag - raw)) * mag
    first = math.ceil(lo / step - 1e-9) * step
    out = []
    v = first
    while v <= hi + 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def build_grid(id, raster, band, web_dir, bounds, scale, valid=None, level_cells=None):
    """One raster to a pyramid of grid files. Returns (levels, legend, stats, source_res_deg).

    bounds: (west, south, east, north) in degrees, snapped outward here to 0.2 degrees.
    The mean in each cell is the mean of the source's own valid cells whose centres fall in it; a cell with
    fewer than half of its source cells valid is empty. No interpolation, no filling, no smoothing.
    """
    import numpy as np
    import rasterio
    with rasterio.open(raster) as ds:
        res = source_cell_deg(ds)
    cells = level_cells or allowed_levels(res)
    if not cells:
        raise RuntimeError(f"{id}: the source's cells ({res:.4f} degrees) are coarser than every level")
    base = min(cells)
    k_top = int(round(0.2 / base))
    w, s_, e, n_ = bounds
    lon0, lat0 = snap(w, 0.2, False), snap(n_, 0.2, True)
    ncols = int(round((snap(e, 0.2, True) - lon0) / 0.2)) * k_top
    nrows = int(round((lat0 - snap(s_, 0.2, False)) / 0.2)) * k_top
    S, C, T, st = accumulate_raster(raster, band, lon0, lat0, base, ncols, nrows, valid=valid)
    src_mean = st["sum"] / st["n_valid"] if st["n_valid"] else float("nan")
    log(f"{id}: source {st['n_valid']} valid cells of {st['n_cells']}, mean {src_mean:.6g}, "
        f"min {st['min']:.6g}, max {st['max']:.6g}; cell {res:.5f} degrees; "
        f"{st['n_valid_in_grid']} valid cells inside the grid")
    levels, checks = [], []
    finest = None
    for cell in sorted(cells, reverse=True):
        k = int(round(cell / base))
        s, c, t = coarsen(S, k), coarsen(C, k), coarsen(T, k)
        keep = (c > 0) & (c * 2 >= t)
        v = np.full(s.shape, np.nan)
        v[keep] = s[keep] / c[keep]
        tag = ("%g" % cell).replace(".", "p")
        file = f"{id}_{tag}.json"
        obj = {"lon0": lon0, "lat0": lat0, "dlon": cell, "dlat": cell, "ncols": int(v.shape[1]),
               "nrows": int(v.shape[0]), "scale": scale, "offset": 0.0, "nodata": NODATA,
               "encoding": "uint16-le-base64", "values": encode_grid(v, scale)}
        size = write_json_atomic(os.path.join(web_dir, file), obj)
        back = decode_grid(obj)
        okb = np.isfinite(back)
        wmean = float((back[okb] * c[okb]).sum() / c[okb].sum())
        kept_share = float(c[keep].sum() / st["n_valid"]) if st["n_valid"] else float("nan")
        kept_src_mean = float(s[keep].sum() / c[keep].sum())
        checks.append({"cell_deg": cell, "cells_with_value": int(okb.sum()), "mean_of_cells": float(back[okb].mean()),
                       "mean_weighted_by_source_cells": wmean, "source_mean_of_kept_cells": kept_src_mean,
                       "source_mean_all": src_mean, "share_of_source_cells_kept": kept_share,
                       "min": float(back[okb].min()), "max": float(back[okb].max())})
        log(f"{id} {cell}: {v.shape[1]}x{v.shape[0]}, {int(okb.sum())} cells with a value, {size} bytes; "
            f"mean weighted by source cells {wmean:.6g} against the source's {kept_src_mean:.6g} over the same "
            f"cells and {src_mean:.6g} over all ({kept_share:.4%} of the source's valid cells kept); "
            f"plain mean of cells {back[okb].mean():.6g}")
        if abs(wmean - kept_src_mean) > scale:
            raise RuntimeError(f"{id} {cell}: the level's mean {wmean} is not the source's {kept_src_mean}")
        levels.append({"file": file, "cell_deg": cell, "ncols": int(v.shape[1]), "nrows": int(v.shape[0]),
                       "bytes": size})
        finest = back
    okf = np.isfinite(finest)
    lo, hi = float(finest[okf].min()), float(finest[okf].max())
    p2, p98 = (float(x) for x in np.percentile(finest[okf], [2, 98]))
    legend = {"min": round(lo, 6), "max": round(hi, 6), "stops": nice_stops(p2, p98)}
    st["mean"] = src_mean
    st["checks"] = checks
    return levels, legend, st, res


def round_geom(geom, tolerance, digits=3):
    """Simplify one geometry with its topology kept, then put its coordinates on a 10^-digits grid."""
    import shapely
    g = shapely.simplify(geom, tolerance, preserve_topology=True) if tolerance else geom
    g = shapely.set_precision(g, 10 ** -digits)
    if g.is_empty:
        g = shapely.set_precision(geom, 10 ** -digits)
    return g


def geom_json(g, digits=3):
    import shapely
    obj = json.loads(shapely.to_geojson(g))

    def rnd(x):
        if isinstance(x, (list, tuple)):
            return [rnd(v) for v in x]
        return round(x, digits)
    if "coordinates" in obj:
        obj["coordinates"] = rnd(obj["coordinates"])
    else:
        for gg in obj.get("geometries", []):
            gg["coordinates"] = rnd(gg["coordinates"])
    return obj


def clean(v):
    """A source field as JSON: numbers stay numbers, missing is null, text is stripped."""
    import numpy as np
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return None if not math.isfinite(float(v)) else float(v)
    if isinstance(v, (dt.date, dt.datetime)) or hasattr(v, "isoformat"):
        try:
            return v.isoformat()
        except Exception:
            return str(v)
    s = str(v).strip()
    return s if s else None


def write_shapes(web_dir, file, gdf, props_fn, tolerance=0.01):
    """A GeoDataFrame to one GeoJSON FeatureCollection in WGS84. Returns (bytes, features, bounds)."""
    g = gdf.to_crs(4326) if gdf.crs is not None and gdf.crs.to_epsg() != 4326 else gdf
    feats = []
    for _, row in g.iterrows():
        if row.geometry is None or row.geometry.is_empty:
            continue
        geom = round_geom(row.geometry, tolerance)
        if geom.is_empty:
            continue
        feats.append({"type": "Feature", "properties": props_fn(row), "geometry": geom_json(geom)})
    size = write_json_atomic(os.path.join(web_dir, file), {"type": "FeatureCollection", "features": feats})
    b = [round(float(x), 3) for x in g.total_bounds]
    return size, len(feats), b


def source_fields(row, skip=("geometry",)):
    return {k: clean(v) for k, v in row.items() if k not in skip}


EXPECTED = {
    "wind_speed_100m": ("wind", "Wind speed at 100 m"),
    "wind_capacity_factor": ("wind", "Wind capacity factor"),
    "solar_ghi": ("solar", "Global horizontal irradiance"),
    "solar_dni": ("solar", "Direct normal irradiance"),
    "geothermal_hydrothermal_sites": ("geothermal", "Identified hydrothermal sites"),
    "geothermal_egs_favorability": ("geothermal", "Deep enhanced geothermal favorability"),
    "oil_gas_basins": ("oil and gas", "Sedimentary basins"),
    "oil_gas_plays": ("oil and gas", "Tight oil and shale gas plays"),
    "hydropower_potential": ("hydropower", "Hydropower potential"),
    "biomass": ("biomass", "Biomass resource"),
    "offshore_wind_leases": ("offshore wind", "Offshore wind lease areas"),
    "offshore_wind_planning_areas": ("offshore wind", "Offshore wind planning areas"),
}
LAYER_ORDER = list(EXPECTED)

# The publishers' terms pages. The quotes used in the manifest are checked word for word against the saved
# page by --check-terms (and by the tests when the raw store is on the machine).
TERMS = {
    "eia": {"url": "https://www.eia.gov/about/copyrights_reuse.php", "file": "eia_copyrights_reuse.html",
            "quote": "U.S. government publications are in the public domain and are not subject to copyright "
                     "protection. You may use and/or distribute any of our data, files, databases, reports, "
                     "graphs, charts, and other information products that are on our website or that you "
                     "receive through our email distribution service. However, if you use or reproduce any of "
                     "our information products, you should use an acknowledgment, which includes the "
                     "publication date, such as: \"Source: U.S. Energy Information Administration (Oct 2008).\""},
    "boem": {"url": "https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data",
             "file": "boem_renewable_energy_gis_data.html",
             "quote": "Note to users: Data downloaded from this site is to be used for informational and "
                      "planning purposes only."},
}
SOURCES = {
    "eia_basins": {"source": "eia", "layers": ["oil_gas_basins"], "terms": "eia",
                   "url": "https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip",
                   "file": "SedimentaryBasins_US_EIA.zip"},
    "eia_plays": {"source": "eia", "layers": ["oil_gas_plays"], "terms": "eia",
                  "url": "https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip",
                  "file": "TightOil_ShaleGas_Plays_Lower48_EIA.zip"},
    "boem_shapefiles": {"source": "boem", "layers": ["offshore_wind_leases", "offshore_wind_planning_areas"],
                        "terms": "boem",
                        "url": "https://www.boem.gov/renewable-energy/boem-renewable-energy-shapefiles",
                        "file": "boem-renewable-energy-shapefiles.zip"},
    "boem_geodatabase": {"source": "boem", "layers": ["offshore_wind_planning_areas"], "terms": "boem",
                         "url": "https://www.boem.gov/renewable-energy/boem-renewable-energy-geodatabase",
                         "file": "boem-renewable-energy-geodatabase.zip"},
    "boem_planning_meta": {
        "source": "boem", "layers": ["offshore_wind_planning_areas"], "terms": "boem",
        "url": "https://services7.arcgis.com/G5Ma95RzqJRPKsWL/ArcGIS/rest/services/"
               "Wind_Planning_Area_Boundaries__BOEM_/FeatureServer/0?f=json",
        "file": "Wind_Planning_Area_Boundaries_layer0.json"},
    "boem_planning": {
        "source": "boem", "layers": ["offshore_wind_planning_areas"], "terms": "boem",
        "url": "https://services7.arcgis.com/G5Ma95RzqJRPKsWL/ArcGIS/rest/services/"
               "Wind_Planning_Area_Boundaries__BOEM_/FeatureServer/0/query"
               "?where=1%3D1&outFields=*&outSR=4326&f=geojson",
        "file": "Wind_Planning_Area_Boundaries_layer0.geojson"},
}
BUILDERS = {}


def builder(id):
    def deco(fn):
        BUILDERS[id] = fn
        return fn
    return deco


def held(raw_dir, key):
    """The ledger row of a pulled source file, with its path. Fails loudly when the file is not held."""
    src = SOURCES[key]
    rows = [r for r in read_ledger(raw_dir)
            if r["source"] == src["source"] and r["file"] == src["file"] and r["http_status"] == "200"]
    if not rows:
        raise FileNotFoundError(f"{key}: not in the raw store ({raw_dir}); run --pull first")
    r = dict(rows[-1])
    r["path"] = os.path.join(raw_dir, r["source"], r["file"])
    if not os.path.exists(r["path"]):
        raise FileNotFoundError(r["path"])
    return r


def base_layer(id, group, title, kind, row, key, **more):
    """The manifest fields every layer carries, from its source's ledger row."""
    t = TERMS[SOURCES[key]["terms"]]
    layer = {"id": id, "group": group, "title": title, "kind": kind,
             "source_url": row["url"], "terms_url": row["terms_url"], "terms_quote": t["quote"],
             "terms_file": row["terms_file"], "terms_sha256": row["terms_sha256"],
             "retrieved_at_utc": row["retrieved_at_utc"],
             "source_file": f"{row['source']}/{row['file']}", "source_bytes": int(row["bytes"]),
             "source_sha256": row["sha256"]}
    layer.update(more)
    return layer


def shape_stats(values):
    v = [x for x in values if isinstance(x, (int, float)) and math.isfinite(x)]
    if not v:
        return None
    return {"n": len(v), "min": min(v), "mean": sum(v) / len(v), "max": max(v)}


EIA_ACK = "Source: U.S. Energy Information Administration"


@builder("oil_gas_basins")
def build_basins(raw_dir, web_dir, manifest):
    import geopandas as gpd
    row = held(raw_dir, "eia_basins")
    shp = find_file(unpack(row["path"]), r"\.shp$")
    g = gpd.read_file(shp)

    def props(r):
        p = {"name": clean(r["NAME"]).title(), "kind": "sedimentary basin",
             "value": clean(r["Area_sq_mi"]), "value_unit": "square miles"}
        p.update(source_fields(r))
        return p
    size, n, b = write_shapes(web_dir, "oil_gas_basins.json", g, props, tolerance=0.01)
    manifest_put(manifest, base_layer(
        "oil_gas_basins", "oil and gas", "Sedimentary basins", "shapes", row, "eia_basins",
        unit="square miles", value_label="area of the basin (the source's Area_sq_mi)",
        publisher="U.S. Energy Information Administration (EIA)",
        source_title="U.S. Sedimentary Basins (SedimentaryBasins_US_May2011_v2.shp)",
        vintage="as of 5-6-2011 (the file's metadata: \"Sedimentary basins associated with the EIA shale "
                "plays as of 5-6-2011\"); file modified 10 March 2016",
        extent="contiguous United States", source_resolution="polygons, no scale stated by the source",
        reduction="each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one "
                  "feature at a time); coordinates to 3 decimals; no feature dropped",
        file="oil_gas_basins.json", bytes=size, features=n, bounds=b,
        legend={"kinds": ["sedimentary basin"]},
        stats=shape_stats([clean(x) for x in g["Area_sq_mi"]]),
        acknowledgment=EIA_ACK + " (May 2011)",
        notes_for_method="EIA's words: \"Sedimentary basins associated with the EIA shale plays as of "
                         "5-6-2011. Sedimentary basin which do not have shale plays as of publication date are "
                         "not included in this file. Sources for the basins are mostly from the US Geological "
                         "Survey and state agencies such as the WY Geological Survey.\" It is an outline of where "
                         "the basins lie, not a measure of oil or gas in place or of what can be recovered. The "
                         "file's own limit: \"These data and related graphics, if available, are not legal "
                         "documents and are not intended to be used as such. The information contained in these "
                         "data is dynamic and may change over time.\""))


@builder("oil_gas_plays")
def build_plays(raw_dir, web_dir, manifest):
    import geopandas as gpd
    row = held(raw_dir, "eia_plays")
    shp = find_file(unpack(row["path"]), r"\.shp$")
    g = gpd.read_file(shp)

    def props(r):
        p = {"name": clean(r["Shale_play"]), "kind": "tight oil and shale gas play",
             "value": clean(r["Area_sq_mi"]), "value_unit": "square miles"}
        p.update(source_fields(r, skip=("geometry", "Shape_Leng", "Shape_Area", "Age_color")))
        return p
    size, n, b = write_shapes(web_dir, "oil_gas_plays.json", g, props, tolerance=0.01)
    manifest_put(manifest, base_layer(
        "oil_gas_plays", "oil and gas", "Tight oil and shale gas plays", "shapes", row, "eia_plays",
        unit="square miles", value_label="area of the play (the source's Area_sq_mi)",
        publisher="U.S. Energy Information Administration (EIA)",
        source_title="Tight Oil and Shale Gas Plays in the U.S. (ShalePlays_US_EIA_Dec2021.shp)",
        vintage="updated December 2021 (the file's metadata: \"Updated December 2021 with addition of "
                "Spraberry and Wolfcamp Plays in the Permian Basin\")",
        extent="contiguous United States (the source's Lower 48)",
        source_resolution="polygons, \"General areas for shale plays in the U.S.\"",
        reduction="each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one "
                  "feature at a time); coordinates to 3 decimals; no feature dropped",
        file="oil_gas_plays.json", bytes=size, features=n, bounds=b,
        legend={"kinds": ["tight oil and shale gas play"]},
        stats=shape_stats([clean(x) for x in g["Area_sq_mi"]]),
        acknowledgment=EIA_ACK + " (Dec 2021)",
        notes_for_method="EIA's words: \"General areas for shale plays in the U.S. Source: EIA based on Enverus "
                         "DrillingInfo Inc., the U.S. Geological Survey, publicly available peer-reviewed "
                         "research papers, academic theses, and publications of State Geological Agencies. "
                         "Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian "
                         "Basin.\" A play's outline is a general area, not a reserve estimate and not a lease "
                         "map. The file's own limit: \"None (public use). Users are advised to thoroughly review "
                         "the metadata to understand the appropriate use and limitations of the data.\""))


@builder("offshore_wind_leases")
def build_leases(raw_dir, web_dir, manifest):
    import geopandas as gpd
    row = held(raw_dir, "boem_shapefiles")
    shp = find_file(unpack(row["path"]), r"Offshore_Wind_Leases_outlines\.shp$")
    g = gpd.read_file(shp)

    def props(r):
        lt = clean(r["LEASE_TYPE"])
        p = {"name": clean(r["LEASE_NU_1"]) or clean(r["LEASE_NUMB"]),
             "kind": f"lease area ({lt})" if lt else "lease area",
             "value": clean(r["ACRES"]) or None, "value_unit": "acres"}
        p.update(source_fields(r, skip=("geometry", "Shape_Leng", "Shape_Area")))
        return p
    size, n, b = write_shapes(web_dir, "offshore_wind_leases.json", g, props, tolerance=0.001)
    kinds = sorted({f"lease area ({clean(x)})" for x in g["LEASE_TYPE"] if clean(x)})
    manifest_put(manifest, base_layer(
        "offshore_wind_leases", "offshore wind", "Offshore wind lease areas", "shapes", row,
        "boem_shapefiles", unit="acres", value_label="area of the lease (the source's ACRES)",
        publisher="Bureau of Ocean Energy Management (BOEM)",
        source_title="Renewable Energy Leases and Planning Areas, All Shapefile "
                     "(Offshore_Wind_Leases_outlines.shp)",
        vintage="last file update on 02/05/2025 (BOEM's page); the archive on BOEM's server is dated "
                "6 August 2025",
        extent="US Outer Continental Shelf: Atlantic, Gulf and Pacific",
        source_resolution="lease outlines built from Outer Continental Shelf blocks",
        reduction="coordinates to 3 decimals (about 100 m); no other simplification; no feature dropped",
        file="offshore_wind_leases.json", bytes=size, features=n, bounds=b,
        legend={"kinds": kinds},
        stats=shape_stats([clean(x) for x in g["ACRES"] if x]),
        zero_acres=int((g["ACRES"] == 0).sum()),
        notes_for_method="BOEM's words: \"Boundaries of renewable energy lease areas, wind planning areas, and "
                         "marine hydrokinetic planning areas (last file update on 02/05/2025).\" These are the "
                         "outlines of leases, easements and research leases BOEM has issued; a lease is a right "
                         "to propose a project, not a wind farm and not a measure of the wind. A lease's status "
                         "may have changed since the file's date. Where the source's ACRES field is 0 (some "
                         "easements and cable routes) no area is shown: the field is kept as the source wrote "
                         "it and the value is left empty."))


@builder("offshore_wind_planning_areas")
def build_planning(raw_dir, web_dir, manifest):
    import geopandas as gpd
    row = held(raw_dir, "boem_planning")
    meta_row = held(raw_dir, "boem_planning_meta")
    with open(meta_row["path"], encoding="utf-8") as f:
        meta = json.load(f)
    g = gpd.read_file(row["path"])
    if len(g) == 0:
        raise RuntimeError("the planning area service returned no feature")
    edit = meta.get("editingInfo", {}).get("dataLastEditDate")
    edited = dt.datetime.fromtimestamp(edit / 1000, dt.timezone.utc).strftime("%Y-%m-%d") if edit else None

    def props(r):
        cat = clean(r.get("CATEGORY1"))
        p = {"name": clean(r.get("ADDITIONAL_INFORMATION")) or clean(r.get("PROTRACTION_NUMBER")),
             "kind": f"planning area ({cat})" if cat else "planning area",
             "value": None, "value_unit": None}
        p.update(source_fields(r, skip=("geometry", "Shape__Area", "Shape__Length")))
        return p
    size, n, b = write_shapes(web_dir, "offshore_wind_planning_areas.json", g, props, tolerance=0.001)
    kinds = sorted({f"planning area ({clean(x)})" for x in g["CATEGORY1"] if clean(x)}) or ["planning area"]
    manifest_put(manifest, base_layer(
        "offshore_wind_planning_areas", "offshore wind",
        "Offshore wind planning areas (rescinded July 30, 2025)", "shapes", row, "boem_planning",
        unit="", value_label="no quantity in the source",
        publisher="Bureau of Ocean Energy Management (BOEM)",
        source_title=meta.get("name", "Offshore Wind Planning Area Outlines"),
        vintage=f"data last edited {edited} (the service's own date); BOEM names the layer "
                f"\"{meta.get('name')}\"",
        extent="US Outer Continental Shelf",
        source_resolution="planning area outlines built from Outer Continental Shelf blocks",
        reduction="coordinates to 3 decimals (about 100 m); no other simplification; no feature dropped",
        file="offshore_wind_planning_areas.json", bytes=size, features=n, bounds=b,
        legend={"kinds": kinds}, stats=None, source_rows=int(len(g)),
        area_status={str(k): int(v) for k, v in g["AREA_STATUS"].value_counts().items()},
        notes_for_method="BOEM's words: \"These data are an outline version of BOEM's offshore wind planning "
                         "areas. These areas represent the current investigations by BOEM for new areas of "
                         "interest in wind energy development. Individual blocks within each wind planning area "
                         "dissolved into single polygons to generate the area outlines.\" BOEM's own name for "
                         f"the layer is \"{meta.get('name')}\": the planning areas were rescinded, and are shown "
                         "as the record of where BOEM had been looking, not as areas open to leasing. The "
                         "archive BOEM offers for download holds the leases only; the planning areas come from "
                         "BOEM's public map service, which BOEM's page links. The service holds 19 rows; one "
                         "has no shape and no name and is not drawn. Each area's AREA_STATUS (Active or "
                         "Inactive) is the source's own field and was last edited before the rescission."))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check-terms", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--raw-dir", default=RAW_DIR)
    args = ap.parse_args()
    only = [x for x in args.only.split(",") if x]
    web_dir = os.path.join(args.out_dir, "resources-data") if args.out_dir else WEB_DIR
    manifest = os.path.join(args.out_dir, "manifest.json") if args.out_dir else MANIFEST
    failed = []
    if args.pull:
        sess = http_session()
        for key, src in SOURCES.items():
            if only and not (set(only) & set(src["layers"])) and key not in only:
                continue
            try:
                terms = fetch_terms(sess, args.raw_dir, src["source"], src["terms"])
                fetch(sess, args.raw_dir, src["source"], ";".join(src["layers"]), src["url"], src["file"], terms)
            except Exception as e:  # a pull that fails is recorded with its exact error and left
                log(f"FAILED pull {key}: {type(e).__name__}: {e}")
                failed.append(key)
        log(f"ledger total: {ledger_total(read_ledger(args.raw_dir))} bytes of {CEILING_BYTES}")
    if args.build:
        man = read_manifest(manifest)
        known = {l["id"] for l in man["layers"]} | {m["id"] for m in man.get("missing", [])}
        for id, (group, title) in EXPECTED.items():
            if id not in known:
                manifest_missing(manifest, id, group, title, "not built yet")
        for id, fn in BUILDERS.items():
            if only and id not in only:
                continue
            try:
                fn(args.raw_dir, web_dir, manifest)
            except Exception as e:
                import traceback
                traceback.print_exc()
                log(f"FAILED build {id}: {type(e).__name__}: {e}")
                failed.append(id)
    if args.check_terms:
        failed += check_terms(args.raw_dir, manifest)
    if failed:
        log(f"failed: {failed}")
        return 1
    return 0


def check_terms(raw_dir, manifest):
    """Every terms quote in the manifest is in the saved terms page, word for word."""
    bad = []
    man = read_manifest(manifest)
    for l in man["layers"]:
        t = l.get("terms_file")
        if not t or not os.path.exists(os.path.join(raw_dir, t)):
            log(f"terms check {l['id']}: the saved page is not on this machine")
            bad.append(l["id"])
            continue
        text = html_text(os.path.join(raw_dir, t))
        for q in l.get("terms_quotes", [l["terms_quote"]]):
            if re.sub(r"\s+", " ", q).strip() not in text:
                log(f"terms check {l['id']}: NOT FOUND word for word: {q[:80]}")
                bad.append(l["id"])
    if not bad:
        log(f"terms check: every quote of {len(man['layers'])} layers is in its saved page")
    return bad


if __name__ == "__main__":
    sys.exit(main())
