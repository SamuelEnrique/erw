"""Energy Research Warehouse (ERW), session 149: the boundaries of the hubs and zones an operator publishes openly.

    python warehouse/connectors/zone_boundaries.py --pull [--only KEY] [--raw-dir DIR]
    python warehouse/connectors/zone_boundaries.py --build [--raw-dir DIR] [--out FILE]

--pull   fetches the files of SOURCES that the raw store does not hold yet, with plain requests and the one contact
         string the owner allows (CONTACT), and never past the ceiling: 30 requests and 200 MB in all, counted in
         <raw-dir>/requests.csv (every request ever made, a failure too). Each file is kept as it came under
         <raw-dir>/<operator>/ with a row of <raw-dir>/<operator>/downloads.csv (url, file, bytes, sha256,
         retrieved_at_utc, terms_url). A site that refuses a plain request is recorded and left.
--build  reads the raw store and writes site/data/curtailment/zone_shapes.json: for every place of the curtailment
         page (site/data/curtailment/free_energy.json) either its published boundary, simplified, with the centroid
         computed here from that boundary, its source, the source's date and its terms address, or the reason it has
         none. No point or line is chosen by hand and nothing is traced from a picture: a place whose operator
         publishes only a picture of a map has no shape and stays a tile on the page.

What counts as published (the owner's rule, session 149's brief): a file of shapes, a table of coordinates, or a
document that defines the place by named counties or other published shapes. What does not: a picture of a map, a
third party's file that does not name the operator's own definition, a point somebody chose.

Self-contained (no import from another connector). No table is written: the output is a file of the site, and
nothing here is loaded into Supabase or Redivis.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(ROOT, "warehouse", "raw", "zone_boundaries")
OUT = os.path.join(ROOT, "site", "data", "curtailment", "zone_shapes.json")
FREE = os.path.join(ROOT, "site", "data", "curtailment", "free_energy.json")
PAUSED_FILE = os.path.join(ROOT, "warehouse", "metadata", "paused_sources.csv")

# The one contact string a request may carry (the owner's ruling; COMMON.md rule 5). Nothing else identifies us.
CONTACT = "ERW research project, github.com/SamuelEnrique/erw"
MAX_REQUESTS = 30
MAX_BYTES = 200 * 1024 * 1024
# Never requested, whatever a list says: MISO is paused, PJM's Data Miner and API need a license.
FORBIDDEN_HOSTS = re.compile(r"(^|\.)misoenergy\.org$|(^|\.)dataminer2?\.pjm\.com$|(^|\.)api\.pjm\.com$", re.I)

REQ_COLS = ["n", "requested_at_utc", "operator", "url", "status", "bytes", "file", "error"]
DL_COLS = ["url", "file", "bytes", "sha256", "retrieved_at_utc", "terms_url"]


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_csv(path, cols, row):
    new = not os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def spent(raw_dir):
    """Requests made and bytes received so far, from the ledger of every request."""
    rows = read_csv(os.path.join(raw_dir, "requests.csv"))
    return len(rows), sum(int(r["bytes"] or 0) for r in rows)


def paused_hosts():
    """Hosts of publishers in warehouse/metadata/paused_sources.csv (session 89): never requested."""
    out = set()
    for r in read_csv(PAUSED_FILE):
        for o in r.get("outlets", "").split(";"):
            if "." in o and " " not in o:
                out.add(o.lower())
    return out


def allowed(url):
    host = re.sub(r"^https?://([^/:]+).*$", r"\1", url).lower()
    if FORBIDDEN_HOSTS.search(host):
        return f"{host} is never requested (MISO is paused; PJM's Data Miner and API need a license)"
    for p in paused_hosts():
        if host == p or host.endswith("." + p):
            return f"{host} is a paused publisher (warehouse/metadata/paused_sources.csv)"
    return None


def get(raw_dir, operator, url, file, terms_url, timeout=90):
    """One plain request, counted before it is sent. The body is kept as it came. Returns the path, or None."""
    why = allowed(url)
    if why:
        print(f"NOT REQUESTED: {url}: {why}")
        return None
    n, b = spent(raw_dir)
    if n + 1 > MAX_REQUESTS:
        print(f"NOT REQUESTED: {url}: the ceiling of {MAX_REQUESTS} requests is reached ({n} made)")
        return None
    if b >= MAX_BYTES:
        print(f"NOT REQUESTED: {url}: the ceiling of {MAX_BYTES} bytes is reached ({b} received)")
        return None
    row = {"n": n + 1, "requested_at_utc": now(), "operator": operator, "url": url, "status": "", "bytes": 0, "file": "", "error": ""}
    path = os.path.join(raw_dir, operator, file)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": CONTACT, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read(MAX_BYTES - b + 1)
            row["status"] = res.status
        row["bytes"] = len(body)
        if b + len(body) > MAX_BYTES:
            row["error"] = "past the byte ceiling: the body was not kept"
            append_csv(os.path.join(raw_dir, "requests.csv"), REQ_COLS, row)
            print(f"FAILED: {url}: {row['error']}")
            return None
        with open(path, "wb") as f:
            f.write(body)
        row["file"] = f"{operator}/{file}"
        append_csv(os.path.join(raw_dir, "requests.csv"), REQ_COLS, row)
        append_csv(os.path.join(raw_dir, operator, "downloads.csv"), DL_COLS,
                   {"url": url, "file": file, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "retrieved_at_utc": row["requested_at_utc"], "terms_url": terms_url})
        print(f"ok   request {n + 1} of {MAX_REQUESTS}: {url}: HTTP {row['status']}, {len(body):,} bytes -> {operator}/{file}")
        return path
    except urllib.error.HTTPError as e:
        row["status"], row["error"] = e.code, f"HTTP {e.code} {e.reason}"
    except Exception as e:  # a refusal, a timeout, a name that does not resolve: recorded with its exact words and left
        row["error"] = f"{type(e).__name__}: {e}"
    append_csv(os.path.join(raw_dir, "requests.csv"), REQ_COLS, row)
    print(f"FAILED request {n + 1} of {MAX_REQUESTS}: {url}: {row['error']} (recorded, left)")
    return None


# Every file the builder may ask for: key, operator folder, address, file name, the terms address, what it is.
CAISO_TERMS = "https://www.caiso.com/privacy-terms-of-use"
ERCOT_TERMS = "https://www.ercot.com/help/terms"
NYISO_TERMS = "https://www.nyiso.com/legal-notice"
SOURCES = [
    ("caiso_zones", "caiso", "https://www.caiso.com/documents/appendixi_isocongestionmanagementzones.pdf", "appendixi_isocongestionmanagementzones.pdf", CAISO_TERMS,
     "CAISO tariff, Appendix I, ISO Congestion Management Zones: what NP15, ZP26 and SP15 are"),
    ("ercot_maps", "ercot", "https://www.ercot.com/news/mediakit/maps", "mediakit_maps.html", ERCOT_TERMS,
     "ERCOT's own list of its maps: what it publishes for load zones and weather zones"),
    ("ercot_loadprofile", "ercot", "https://www.ercot.com/mktinfo/loadprofile", "mktinfo_loadprofile.html", ERCOT_TERMS,
     "ERCOT's Load Profiling page: where the Profile Decision Tree (ZIP code to weather zone) is posted"),
    ("ercot_lpg", "ercot", "https://www.ercot.com/mktrules/guides/loadprofiling/current", "loadprofiling_current.html", ERCOT_TERMS,
     "ERCOT's Load Profiling Guide, the current version's list of files (Appendix D, the Profile Decision Tree)"),
    ("ercot_tree", "ercot", "https://www.ercot.com/files/docs/2024/04/30/Appendix_D_Profile_Decision_Tree_050124.xlsx", "Appendix_D_Profile_Decision_Tree_050124.xlsx", ERCOT_TERMS,
     "ERCOT Load Profiling Guide, Appendix D, Profile Decision Tree (1 May 2024): the worksheet that assigns every ZIP code to a weather zone"),
    ("cec_search", "cec", "https://cecgis-caenergy.opendata.arcgis.com/api/search/v1/collections/dataset/items?q=NP15&limit=50", "hub_search_np15.json", "https://www.energy.ca.gov/conditions-of-use",
     "California Energy Commission, GIS open data: its catalogue asked for NP15 (is a layer of CAISO's zones published)"),
    ("cec_search_caiso", "cec", "https://cecgis-caenergy.opendata.arcgis.com/api/search/v1/collections/dataset/items?q=CAISO&limit=50", "hub_search_caiso.json", "https://www.energy.ca.gov/conditions-of-use",
     "California Energy Commission, GIS open data: its catalogue asked for CAISO (which layers name the operator)"),
    ("nygis_search", "nygis", "https://data.gis.ny.gov/api/search/v1/collections/dataset/items?q=NYISO&limit=50", "hub_search_nyiso.json", "https://www.ny.gov/terms-use",
     "New York State GIS Clearinghouse: its catalogue asked for NYISO (is a layer of the load zones published)"),
    ("nyiso_subzones", "nyiso", "https://mis.nyiso.com/public/pdf/tp/tp.pdf", "subzones_by_transmission_owner.pdf", NYISO_TERMS,
     "NYISO, Subzones by Transmission Owner (page reference P-23): what each load zone is made of"),
    ("caiso_terms", "caiso", CAISO_TERMS, "terms.html", CAISO_TERMS, "CAISO's Privacy and Terms of Use"),
    ("ercot_terms", "ercot", ERCOT_TERMS, "terms.html", ERCOT_TERMS, "ERCOT's Terms of Use"),
    ("nyiso_terms", "nyiso", NYISO_TERMS, "terms.html", NYISO_TERMS, "NYISO's Legal Notice"),
    ("cec_terms", "cec", "https://www.energy.ca.gov/conditions-of-use", "terms.html", "https://www.energy.ca.gov/conditions-of-use", "California Energy Commission, Conditions of Use"),
    ("ny_terms", "nygis", "https://www.ny.gov/terms-use", "terms.html", "https://www.ny.gov/terms-use", "New York State, Terms of Use"),
    ("nydps_zones", "nydps", "https://documents.dps.ny.gov/public/Common/ViewDoc.aspx?DocRefId=%7BF755802E-7537-4865-85A6-4BC440DD3188%7D", "nyca_load_zones_faq.pdf", "https://www.ny.gov/terms-use",
     "New York Department of Public Service: New York Control Area Load Zones (does it define NYISO's zones by county)"),
]


def pull(raw_dir, only=None):
    ledger = read_csv(os.path.join(raw_dir, "requests.csv"))
    held = {(r["operator"], r["file"].split("/", 1)[-1]) for r in ledger if r["file"]}
    refused = {r["url"]: r["error"] for r in ledger if not r["file"] and r["status"]}  # the site answered, and not with the file
    failed = 0
    for key, operator, url, file, terms_url, _what in SOURCES:
        if only and key not in only:
            continue
        if (operator, file) in held and os.path.exists(os.path.join(raw_dir, operator, file)):
            print(f"held {operator}/{file} (not asked for again)")
            continue
        if url in refused:
            print(f"left {url}: it answered {refused[url]} before (recorded, not asked for again)")
            continue
        if get(raw_dir, operator, url, file, terms_url) is None:
            failed += 1
    n, b = spent(raw_dir)
    print(f"requests so far {n} of {MAX_REQUESTS}; bytes so far {b:,} of {MAX_BYTES:,}")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--only", action="append", help="with --pull: a key of SOURCES (repeat for several)")
    ap.add_argument("--raw-dir", default=RAW_DIR)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--free", default=FREE, help="the page's places (site/data/curtailment/free_energy.json)")
    a = ap.parse_args()
    if not a.pull and not a.build:
        ap.error("say --pull or --build")
    code = 0
    if a.pull:
        code = pull(a.raw_dir, a.only)
    if a.build and code == 0:
        code = build(a.raw_dir, a.out, a.free)
    return code


# ---- build -------------------------------------------------------------------------------------------------------

# The file's shape, written at its top so that another page (the map of resources) can read it without this script.
ABOUT = [
    "Energy Research Warehouse (ERW), session 149: the published boundary of each hub and zone of the curtailment page, or the reason it has none.",
    "Written by warehouse/connectors/zone_boundaries.py --build from the raw files under warehouse/raw/zone_boundaries. Nothing here is drawn, traced or placed by hand.",
    "rule: what counts as a published boundary. places.<grid>.<place id>: one entry for every place of site/data/curtailment/free_energy.json that is not an average of hubs.",
    "A place is either {status: 'mapped', drawn, geometry, centroid, centroid_method, source, source_date, terms_url} or {status: 'tile', reason, sources}.",
    "mapped: geometry is GeoJSON (Polygon or MultiPolygon, longitude and latitude in degrees, WGS 84), simplified from the published boundary; centroid is [longitude, latitude], the area-weighted centroid of that boundary computed by the builder; drawn says exactly what the shape is (the zone, never a hub's location); source is an id of sources.",
    "tile: no shape and no point. reason is a short sentence for a hover; sources are the ids of the sources that were read to reach it (an empty list means the operator's site was not searched, and the reason says so).",
    "sources.<id>: publisher, title, url, file (under warehouse/raw/zone_boundaries), bytes, sha256, retrieved_at_utc, document_date where the document states one, terms_url, terms_quote (word for word from the saved terms page), finding (what the builder read in the file).",
    "definitions: a set of zones an operator defines by named shapes, which no place of the curtailment page uses. ercot_weather_zones: ERCOT's eight weather zones, each the ZIP codes ERCOT's own table assigns to it; shapes are not built (see its not_drawn).",
    "counts: places, mapped, tiles. requests and bytes: the pull against its ceiling.",
]
RULE = ("A place is mapped only when its grid operator, or a government agency naming the operator as its source, openly publishes a file of shapes, "
        "a table of coordinates, or a document that defines the place by named counties or other published shapes. A picture of a map, a third "
        "party's file and a chosen point do not count. The mark of a mapped place is the centre of the zone's published boundary, not a hub's location.")

TERMS = {
    "caiso": (CAISO_TERMS, "caiso/terms.html",
              "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information."),
    "ercot": (ERCOT_TERMS, "ercot/terms.html",
              "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement."),
    "nyiso": (NYISO_TERMS, "nyiso/terms.html",
              "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety."),
    "cec": ("https://www.energy.ca.gov/conditions-of-use", "cec/terms.html",
            "Most of these materials and information were generated, compiled, or assembled at public expense and are free for public use consistent with the Public Records Act (California Government Code Section 6250 et. seq.), provided the Energy Commission is credited when using these materials and information."),
}
ERCOT_WEATHER_NOTE = ("This map displays the various Weather Zones that exist within the ERCOT footprint, but it does not necessarily include all counties "
                      "that have participation within the ERCOT market.")
NYISO_IMAGES = "Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited"
DATA_FILE = re.compile(r"\.(zip|kmz|kml|shp|geojson|json|gdb|gpkg|csv|xlsx?|pdf)(\?|$)", re.I)


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def page_text(path):
    import html as _html
    t = read_text(path)
    t = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", t)
    return _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)))


def pdf_text(path):
    import pdfplumber
    with pdfplumber.open(path) as p:
        pages = list(p.pages)
        return "\n".join(pg.extract_text() or "" for pg in pages), sum(len(pg.images) for pg in pages)


def weather_zones(path):
    """ERCOT's ZIP code to weather zone table, as its worksheet lists it: {code: {name, zip_codes}}, and the rows whose
    zone name and zone code do not agree (held out of every zone, flagged, not guessed)."""
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["ZipToZone"]
    names, zones, flagged, rows = {}, {}, [], 0
    listed = []
    for row in ws.iter_rows(values_only=True):
        if len(row) < 5 or not isinstance(row[1], int) or row[2] is None:
            continue
        rows += 1
        zip_code, name, code = str(row[2]).strip().zfill(5), str(row[3]).strip(), str(row[4]).strip()
        listed.append((zip_code, name, code))
    # a code's name is the one most of its rows carry; a row whose name is another code's name is flagged
    for _, name, code in listed:
        names.setdefault(code, {}).setdefault(name, 0)
        names[code][name] += 1
    main = {code: max(by, key=by.get) for code, by in names.items()}
    for zip_code, name, code in listed:
        if name != main[code]:
            flagged.append({"zip_code": zip_code, "weather_zone_name": name, "weather_zone_code": code})
            continue
        zones.setdefault(code, {"name": name, "zip_codes": []})["zip_codes"].append(zip_code)
    for z in zones.values():
        z["zip_codes"] = sorted(set(z["zip_codes"]))
    return zones, flagged, rows


def build(raw_dir, out, free):
    need = ["caiso/appendixi_isocongestionmanagementzones.pdf", "ercot/mediakit_maps.html", "ercot/Appendix_D_Profile_Decision_Tree_050124.xlsx",
            "cec/hub_search_np15.json", "cec/hub_search_caiso.json", "nygis/hub_search_nyiso.json", "nyiso/subzones_by_transmission_owner.pdf"] + [t[1] for t in TERMS.values()]
    missing = [f for f in need if not os.path.exists(os.path.join(raw_dir, f))]
    if missing:
        print(f"zone_boundaries --build FAILED: the raw store lacks {', '.join(missing)}; run --pull (nothing was written)", file=sys.stderr)
        return 1
    rows = {}
    for op in sorted(os.listdir(raw_dir)):
        for r in read_csv(os.path.join(raw_dir, op, "downloads.csv")):
            with open(os.path.join(raw_dir, op, r["file"]), "rb") as f:
                body = f.read()
            if hashlib.sha256(body).hexdigest() != r["sha256"]:
                print(f"zone_boundaries --build FAILED: {op}/{r['file']} is not the file downloads.csv recorded (sha256 differs)", file=sys.stderr)
                return 1
            rows[f"{op}/{r['file']}"] = r
    terms = {}
    for op, (url, file, quote) in TERMS.items():
        text = page_text(os.path.join(raw_dir, file))
        if quote not in text:
            print(f"zone_boundaries --build FAILED: the sentence quoted from {url} is not in the saved page {file}", file=sys.stderr)
            return 1
        terms[op] = {"terms_url": url, "terms_quote": quote, "terms_file": file, "terms_sha256": rows[file]["sha256"], "terms_retrieved_at_utc": rows[file]["retrieved_at_utc"]}
    if NYISO_IMAGES not in page_text(os.path.join(raw_dir, "nyiso/terms.html")):
        print("zone_boundaries --build FAILED: NYISO's sentence on images is not in the saved legal notice", file=sys.stderr)
        return 1

    def src(file, publisher, title, op, finding, date=None):
        r = rows[file]
        return {"publisher": publisher, "title": title, "url": r["url"], "file": file, "bytes": int(r["bytes"]), "sha256": r["sha256"], "retrieved_at_utc": r["retrieved_at_utc"],
                "document_date": date, **{k: terms[op][k] for k in ("terms_url", "terms_quote")}, "finding": finding}

    # what each file says, read here from the file itself
    tariff, tariff_images = pdf_text(os.path.join(raw_dir, need[0]))
    zones_named = [z for z in ("NP15", "ZP26", "SP15") if z in tariff]
    if len(zones_named) != 3:
        print("zone_boundaries --build FAILED: CAISO's Appendix I no longer names NP15, ZP26 and SP15", file=sys.stderr)
        return 1
    issued = re.search(r"Effective: (\w+ \d+, \d{4})", tariff)
    maps = read_text(os.path.join(raw_dir, need[1]))
    images = sorted(set(re.findall(r'https://www\.ercot\.com/files/assets/[^"\s]+\.(?:jpg|jpeg|png|gif)', maps, re.I)))
    asset_files = sorted(set(re.findall(r'https://www\.ercot\.com/files/(?:assets|docs)/[^"\s]+', maps)))
    data_files = [u for u in asset_files if DATA_FILE.search(u)]
    load_map = [u for u in images if re.search(r"load-zone", u, re.I)]
    weather_map = [u for u in images if re.search(r"weather", u, re.I)]
    if not load_map or not weather_map or ERCOT_WEATHER_NOTE not in page_text(os.path.join(raw_dir, need[1])):
        print("zone_boundaries --build FAILED: ERCOT's maps page no longer lists its load zone and weather zone maps as read in session 149", file=sys.stderr)
        return 1
    np15 = read_json(os.path.join(raw_dir, need[3]))
    cec = read_json(os.path.join(raw_dir, need[4]))
    cec_titles = [f.get("properties", {}).get("title", "") for f in cec.get("features", [])]
    ny = read_json(os.path.join(raw_dir, need[5]))
    sub, sub_images = pdf_text(os.path.join(raw_dir, need[6]))
    sub_rows = [ln.split() for ln in sub.splitlines() if ln.startswith("MeteringAuthority-")]
    ny_zones = sorted({r[-1] for r in sub_rows})
    wz, flagged, wz_rows = weather_zones(os.path.join(raw_dir, need[2]))

    sources = {
        "caiso_tariff_appendix_i": src(need[0], "California ISO (CAISO)", "ISO Tariff, Appendix I, ISO Congestion Management Zones", "caiso",
                                       f"Names three active zones, {', '.join(zones_named)}, and gives no line, county or coordinate for any of them ({tariff_images} images, {len(tariff.split())} words in all).",
                                       issued.group(1) if issued else None),
        "cec_catalogue_np15": src(need[3], "California Energy Commission", "GIS open data, the catalogue asked for NP15", "cec",
                                  f"{np15.get('numberMatched')} datasets match NP15."),
        "cec_catalogue_caiso": src(need[4], "California Energy Commission", "GIS open data, the catalogue asked for CAISO", "cec",
                                   f"{cec.get('numberMatched')} datasets match CAISO: {'; '.join(cec_titles)}. None is a layer of NP15, ZP26 or SP15."),
        "ercot_maps_page": src(need[1], "Electric Reliability Council of Texas (ERCOT)", "Maps (media kit)", "ercot",
                               f"Lists {len(images)} maps, each an image: {', '.join(u.rsplit('/', 1)[-1] for u in images)}. Files of shapes, coordinates or counties on the page: {len(data_files)}. The load zone map and the weather zone map are pictures. Of the weather zone map the page says: \"{ERCOT_WEATHER_NOTE}\""),
        "ercot_profile_decision_tree": src(need[2], "Electric Reliability Council of Texas (ERCOT)", "Load Profiling Guide, Appendix D, Profile Decision Tree, worksheet ZipToZone", "ercot",
                                           f"Assigns {wz_rows} ZIP codes to {len(wz)} weather zones ({', '.join(f'{z} {len(v['zip_codes'])}' for z, v in sorted(wz.items()))}); {len(flagged)} row's zone name and code do not agree. It defines weather zones, not load zones or hubs.",
                                           "2024-05-01"),
        "nyiso_subzones": src(need[6], "New York Independent System Operator (NYISO)", "Subzones by Transmission Owner (page reference P-23)", "nyiso",
                              f"Lists {len(sub_rows)} subzones of {len(ny_zones)} zones ({', '.join(ny_zones)}) by transmission owner; no county, no coordinate and no shape ({sub_images} images)."),
        "ny_gis_catalogue": {"publisher": "New York State GIS Clearinghouse", "title": "The catalogue asked for NYISO", "url": rows[need[5]]["url"], "file": need[5], "bytes": int(rows[need[5]]["bytes"]),
                             "sha256": rows[need[5]]["sha256"], "retrieved_at_utc": rows[need[5]]["retrieved_at_utc"], "document_date": None, "terms_url": rows[need[5]]["terms_url"],
                             "terms_quote": None, "terms_note": "The terms address answered HTTP 404 on 7 October 2026; nothing of this source is shown, it is read only as evidence that no layer exists.",
                             "finding": f"{ny.get('numberMatched')} datasets match NYISO."},
    }
    reason = {
        ("caiso", "hub"): ("CAISO publishes no boundary or coordinates for this trading hub: its tariff names the zone without a line, so the place stays a tile.", ["caiso_tariff_appendix_i", "cec_catalogue_np15", "cec_catalogue_caiso"]),
        ("ercot", "zone"): ("ERCOT publishes its load zones as a picture of a map, with no file of shapes, counties or coordinates, so the place stays a tile.", ["ercot_maps_page", "ercot_profile_decision_tree"]),
        ("ercot", "hub"): ("ERCOT publishes no boundary or coordinates for its hubs, so the place stays a tile.", ["ercot_maps_page"]),
        ("nyiso", "zone"): ("NYISO lists this zone by its transmission owners' subzones and publishes no file of shapes, counties or coordinates, so the place stays a tile.", ["nyiso_subzones", "ny_gis_catalogue"]),
        ("isone", "zone"): ("No published boundary is held for this zone: ISO-NE's site was not searched, so the place stays a tile.", []),
        ("isone", "hub"): ("No published boundary is held for this hub: ISO-NE's site was not searched, so the place stays a tile.", []),
        ("spp", "hub"): ("No published boundary is held for this hub: SPP's site was not searched, so the place stays a tile.", []),
    }
    fe = read_json(free)
    places, n = {}, 0
    for gid, g in fe["grids"].items():
        places[gid] = {}
        for loc in g["locations"]:
            if loc["kind"] == "average":
                continue
            if (gid, loc["kind"]) not in reason:
                print(f"zone_boundaries --build FAILED: no finding is written for a {loc['kind']} of {gid} ({loc['id']}); nothing was written", file=sys.stderr)
                return 1
            why, ids = reason[(gid, loc["kind"])]
            places[gid][loc["id"]] = {"status": "tile", "kind": loc["kind"], "reason": why, "sources": ids}
            n += 1
    mapped = sum(1 for g in places.values() for p in g.values() if p["status"] == "mapped")
    req_n, req_b = spent(raw_dir)
    doc = {
        "about": ABOUT,
        "built": now(),
        "builder": "warehouse/connectors/zone_boundaries.py --build",
        "rule": RULE,
        "counts": {"places": n, "mapped": mapped, "tiles": n - mapped},
        "pull": {"requests": req_n, "requests_ceiling": MAX_REQUESTS, "bytes": req_b, "bytes_ceiling": MAX_BYTES, "user_agent": CONTACT},
        "grids": {
            "caiso": "CAISO publishes no boundary or coordinates for NP15, ZP26 or SP15: its tariff names the three zones without a line, and the California Energy Commission's catalogue holds no layer of them.",
            "ercot": "ERCOT publishes its load zones and weather zones as pictures of maps. Its weather zones are defined by ZIP code in its own table; no hub or load zone is defined by any published shape.",
            "nyiso": "NYISO lists each zone by its transmission owners' subzones and publishes no file of shapes, counties or coordinates; its legal notice forbids taking its map image as a file.",
            "isone": "ISO-NE's site was not searched for a boundary file.",
            "spp": "SPP's site was not searched for a boundary file.",
        },
        "nyiso_images": {"terms_url": NYISO_TERMS, "terms_quote": NYISO_IMAGES},
        "sources": sources,
        "places": places,
        "definitions": {
            "ercot_weather_zones": {
                "status": "defined, not drawn",
                "defined_by": "ZIP code",
                "source": "ercot_profile_decision_tree",
                "source_date": "2024-05-01",
                "terms_url": ERCOT_TERMS,
                "not_drawn": "No place of the curtailment page is a weather zone, and the shapes of ZIP codes are not in the site's atlas (us-atlas holds states and counties). Building them needs the Census Bureau's ZIP Code Tabulation Areas, a pull that session 149's brief did not name.",
                "rows_listed": wz_rows,
                "rows_not_assigned": flagged,
                "zones": wz,
            },
        },
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=True)
        f.write("\n")
    print(f"zone_boundaries: {n} places, {mapped} mapped, {n - mapped} tiles; ERCOT weather zones defined by {wz_rows} ZIP codes ({len(flagged)} not assigned); "
          f"{len(sources)} sources; pull {req_n} of {MAX_REQUESTS} requests, {req_b:,} of {MAX_BYTES:,} bytes -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
