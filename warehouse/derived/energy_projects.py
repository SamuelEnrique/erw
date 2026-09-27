#!/usr/bin/env python3
"""The project map table: every generator and queue position the ERW holds, on one map (tool 3).

Energy Research Warehouse (ERW), session 16. Method: docs/methods/energy_projects.md.

    python warehouse/derived/energy_projects.py

Builds the entities table energy_projects from eight ERW tables:
eia860m_operating_generators (kind operating), eia860m_planned_generators (kind
planned) and the six ISO interconnection queues, <iso>_interconnection_queue for
ERCOT, CAISO, NYISO, MISO, SPP and ISO-NE (kind queue). One row per input row;
nothing is merged, estimated or dropped.

Coordinates:
- where EIA gives lat and lon, they are used as given: geo_precision point;
- otherwise (every queue position, and the few EIA rows without coordinates), the
  row's county and state are looked up in the Census Bureau's county gazetteer
  (2025 Gazetteer Files, counties, national; the 2020 file fills Connecticut's
  legacy counties, which the 2025 file replaces with planning regions), downloaded each run into
  warehouse/raw/census_gazetteer/<run_id>/ with a manifest; lat and lon are the
  county's internal point (INTPTLAT, INTPTLONG): geo_precision county;
- a row whose county cannot be matched keeps lat and lon empty: geo_precision
  none, with the reason in geo_note. Where the queue lists several counties, the
  first that matches is used, and geo_note says so.

technology_group: EIA's own grouping (the EIA-860M connector's TECH_GROUPS) for
EIA rows; for queue positions, the ISO's fuel or technology text is grouped by
QUEUE_TECH below, the same groups plus hybrid (a position naming more than one of
solar, wind, storage or another technology) and transmission (merchant
transmission requests). unknown where the source states no technology.

Shape: entities (docs/datastandard.md), a snapshot (Decision 21): each run
replaces the table. A derived table (Decision 23): source erw:energy_projects,
source_url the method doc, a "Derived from:" header line, and the most
restrictive license of the inputs. In CI the queue tables are on the runner only
on Mondays (or a manual run with queues=1); on other days this script skips with
a warning (session 10 ruling 3) and Supabase keeps the last load.

Absent queues (session 18): the two EIA-860M tables are required; the queues are not. If
some queues are present and others absent (GitHub run 4: NYISO's queue answered HTTP 202,
so nyiso_interconnection_queue was not written), the table is built from the queues it has.
Each absent queue is named, with the reason from warehouse/metadata/run_status.csv, in an
"Absent inputs:" header line, in the run status and, through the coverage builder, in
docs/coverage.md. With no queue at all in CI, the script still skips (ruling 3 above).
"""

import datetime as dt
import io
import os
import re
import sys
import traceback
import unicodedata
import zipfile

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "energy_projects"
METHOD = "docs/methods/energy_projects.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md"
SOURCE = "erw:energy_projects"
GAZ_SOURCE = "census:gazetteer_counties"
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_counties_national.zip"
GAZ_URL_2020 = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/2020_Gaz_counties_national.zip"
GAZ_PAGE = "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html"
QUEUE_ISOS = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"]
REQUIRED = ["eia860m_operating_generators", "eia860m_planned_generators"]
QUEUES = [f"{i}_interconnection_queue" for i in QUEUE_ISOS]
INPUTS = REQUIRED + QUEUES

EXTRA = ["project_id", "kind", "technology_group", "mw", "state", "county", "geo_precision", "geo_note",
         "operator_role", "date", "date_kind", "technology", "source_status", "source_table"]
STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date",
       "operator", "source", "source_url", "retrieved_at", "vintage"]
COLS = STD + EXTRA

STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
    "connecticut": "CT", "delaware": "DE", "district of columbia": "DC", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD", "massachusetts": "MA",
    "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
    "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "puerto rico": "PR"}
CODES = set(STATES.values())

# Queue fuel or technology text -> groups. Patterns run on the lower-cased text; a position
# naming several groups is "hybrid" unless all are fossil (then the first one named).
QUEUE_TECH = [
    ("solar", r"solar|photovoltaic|(?<![a-z])sun(?![a-z])|(?<![a-z])pv(?![a-z])"),
    ("wind", r"wind|(?<![a-z])wnd(?![a-z])"),
    ("storage", r"batter|storage|(?<![a-z])bat(?![a-z])|flywheel|compressed air|(?<![a-z])bess(?![a-z])"),
    ("hydro", r"hydro|(?<![a-z])wat(?![a-z])|water"),
    ("nuclear", r"nuclear|(?<![a-z])nuc(?![a-z])"),
    ("coal", r"coal|(?<![a-z])(bit|sub|lig)(?![a-z])"),
    ("petroleum", r"(?<![a-z])(dfo|ker|jf|rfo|wo)(?![a-z])|diesel|fuel oil"),
    ("biomass", r"(?<![a-z])(wds|lfg|msw|blq|bio)(?![a-z])|wood|biomass|solid waste|methane"),
    ("geothermal", r"geotherm"),
    ("natural_gas", r"(?<![a-z])(gas|ng|rice|ctg|ct|cc)(?![a-z])|natural gas|combined.cycle|combustion|"
                    r"gas turbine|reciprocating|cogeneration|dual fuel|thermal - (ct|cc|ctg|st)"),
    ("transmission", r"transmission|high voltage dc|(?<![a-z])vft(?![a-z])"),
]
FOSSIL = {"natural_gas", "petroleum", "coal"}


def queue_group(text):
    t = (text or "").lower().strip()
    if not t:
        return "unknown"
    if t.startswith("hybrid"):
        return "hybrid"
    found = []
    for g, pat in QUEUE_TECH:
        m = re.search(pat, t)
        if m:
            found.append((m.start(), g))
    groups = [g for _, g in sorted(found)]
    if not groups:
        return "other"
    if len(set(groups)) == 1:
        return groups[0]
    if set(groups) <= FOSSIL:
        return groups[0]
    return "hybrid"


def plain(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = s.lower().replace("&", " and ").replace("saint ", "st ").replace("ste. ", "ste ")
    s = re.sub(r"[.'`]", "", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return " ".join(s.split())


SUFFIX = re.compile(r" (county|parish|prsh|borough|census area|city and borough|municipality|municipio|cnty|co)$")


def county_key(s):
    return SUFFIX.sub("", plain(s))


def state_code(s):
    """A two-letter code from the source's state text: the code itself, a state name, or the
    first of several ("IA/MN"). Empty when it names no US state."""
    s = (s or "").strip()
    if not s:
        return ""
    first = re.split(r"[/,;&]| and ", s)[0].strip()
    if first.upper() in CODES:
        return first.upper()
    return STATES.get(plain(first), "")


def fetch_gazetteer(url, log):
    """(DataFrame, retrieval record, member name) for one Census county gazetteer zip."""
    with ip.RAW.collect() as recs:
        r = requests.get(url, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Census gazetteer HTTP {r.status_code}: {url}")
    rec = recs[-1] if recs else {"retrieved_at": pd.Timestamp.now(tz="UTC"), "file": ""}
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        member = [n for n in z.namelist() if n.lower().endswith(".txt")][0]
        first = z.open(member).readline().decode("latin-1")
        gaz = pd.read_csv(z.open(member), sep="|" if "|" in first else "	", dtype=str,
                          keep_default_na=False, encoding="latin-1")
    gaz.columns = [c.strip() for c in gaz.columns]
    log(f"gazetteer: {member}, {len(gaz)} counties, saved as {rec['file']}")
    return gaz, rec, member


def load_gazetteer(run_id, log):
    """(lookup {(state, county key): (lat, lon, NAME, file)}, [(member, retrieval record)]).

    The 2025 file first. The 2020 file only fills names the 2025 file lacks: Connecticut's
    eight legacy counties, which the Census Bureau replaced with planning regions in 2022
    while the ISO-NE queue still names the counties."""
    ip.RAW.open("census_gazetteer", run_id)
    look, got = {}, []
    for url in (GAZ_URL, GAZ_URL_2020):
        gaz, rec, member = fetch_gazetteer(url, log)
        got.append((member, rec))
        cities, new = {}, {}
        for g in gaz.itertuples():
            lat, lon = float(g.INTPTLAT), float(g.INTPTLONG)
            v = (lat, lon, g.NAME, member)
            new.setdefault((g.USPS, county_key(g.NAME)), v)
            new.setdefault((g.USPS, plain(g.NAME)), v)
            if plain(g.NAME).endswith(" city"):   # independent cities: "richmond city" and, if free, "richmond"
                cities.setdefault((g.USPS, plain(g.NAME)[:-5]), []).append(v)
        for k, v in cities.items():
            if k not in new and len(v) == 1:
                new[k] = v[0]
        for k, v in new.items():
            look.setdefault(k, v)
    return look, got


def geocode(state, county, look):
    """(lat, lon, precision, note) from county and state; lat and lon None when not matched.
    The whole text is tried first ("Miami-Dade"), then each county of a list ("Tioga - Bradford")."""
    if not state:
        return None, None, "none", "no US state stated"
    if not county.strip():
        return None, None, "none", "no county stated"
    s = re.sub(r",\s*[A-Z]{2}$", "", county.strip())   # "Kern County, CA"
    parts = [p for p in re.split(r"[/,;&-]| and |\\", s) if p.strip()]
    for p in [s] + parts:
        hit = look.get((state, county_key(p))) or look.get((state, plain(p)))
        if hit:
            note = f"county {hit[2]} ({hit[3]})"
            if p != s and len(parts) > 1:
                note += f", the first matching of {len(parts)} counties listed"
            return hit[0], hit[1], "county", note
    return None, None, "none", f"county {county!r} not found in the gazetteer for {state}"


def read(name):
    """An ERW table as text, whatever its shape (the leading '#' lines are its header)."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    with open(path, encoding="utf-8") as f:
        n = 0
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def build(look, log, queue_isos=QUEUE_ISOS):
    frames = []
    for name, kind in (("eia860m_operating_generators", "operating"), ("eia860m_planned_generators", "planned")):
        d = read(name)
        if kind == "operating":
            date = d["operating_year"]
            date_kind = d["operating_year"].map(lambda v: "operating_year" if v else "")
        else:
            date = d["planned_operation_date"]
            date_kind = d["planned_operation_date"].map(lambda v: "planned_operation_date" if v else "")
        frames.append(pd.DataFrame({
            "entity_id": d["entity_id"], "entity_type": d["entity_type"], "name": d["name"],
            "lat": d["lat"], "lon": d["lon"], "capacity_mw": d["capacity_mw"], "status": d["status"],
            "status_date": d["status_date"], "operator": d["operator"], "retrieved_at": d["retrieved_at"],
            "vintage": d["vintage"], "kind": kind, "technology_group": d["technology_group"].replace("", "unknown"),
            "state": d["state"], "county": d["county"], "operator_role": d["operator"].map(lambda v: "operator" if v else ""),
            "date": date, "date_kind": date_kind, "technology": d["technology"], "source_status": d["eia_status_label"],
            "source_table": name}))
        log(f"{name}: {len(d)} rows")
    for iso in queue_isos:
        name = f"{iso}_interconnection_queue"
        d = read(name)
        frames.append(pd.DataFrame({
            "entity_id": d["entity_id"], "entity_type": d["entity_type"], "name": d["name"],
            "lat": d["lat"], "lon": d["lon"], "capacity_mw": d["capacity_mw"], "status": d["status"],
            "status_date": d["status_date"], "operator": d["operator"], "retrieved_at": d["retrieved_at"],
            "vintage": d["vintage"], "kind": "queue", "technology_group": d["fuel_technology"].map(queue_group),
            "state": d["state"], "county": d["county"], "operator_role": d["operator"].map(lambda v: "developer" if v else ""),
            "date": d["queue_date"], "date_kind": d["queue_date"].map(lambda v: "queue_date" if v else ""),
            "technology": d["fuel_technology"], "source_status": d["iso_status"], "source_table": name}))
        log(f"{name}: {len(d)} rows")
    t = pd.concat(frames, ignore_index=True).fillna("")
    t["state"] = t["state"].map(state_code)
    lat, lon, prec, note = [], [], [], []
    for r in t.itertuples():
        if r.lat and r.lon:
            lat.append(r.lat), lon.append(r.lon), prec.append("point"), note.append("")
            continue
        a, b, p, n = geocode(r.state, r.county, look)
        lat.append("" if a is None else f"{a:.6f}")
        lon.append("" if b is None else f"{b:.6f}")
        prec.append(p), note.append(n)
    t["lat"], t["lon"], t["geo_precision"], t["geo_note"] = lat, lon, prec, note
    t["geo"] = t["state"].map(lambda s: f"US-{s}" if s else "US")
    t["project_id"] = t["entity_id"]
    t["mw"] = t["capacity_mw"]
    t["source"] = SOURCE
    t["source_url"] = METHOD_URL
    return t[COLS].sort_values("entity_id").reset_index(drop=True)


def absent_reason(table):
    """The latest failed or skipped run_status row of a table, as a short reason."""
    path = os.path.join(ip.METADATA_DIR, "run_status.csv")
    if not os.path.exists(path):
        return "no run status"
    st = pd.read_csv(path, dtype=str, keep_default_na=False)
    st = st[(st["table"] == table) & st["status"].isin(["failed", "skipped", "gap"])]
    if st.empty:
        return "not on this machine; no failed run recorded"
    r = st.sort_values("run_id").iloc[-1]
    return f"{r['status']} in run {r['run_id']}: {r['detail'][:160]}"


def derived_license(log, inputs=INPUTS):
    reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
    lic = dict(zip(reg["source"], reg["license"]))
    srcs = set()
    for n in inputs:
        srcs |= set(read(n)["source"])
    missing = sorted(s for s in srcs if s not in lic)
    if missing:
        raise RuntimeError(f"input sources {missing} are not in the registry; cannot set the license")
    out = "internal" if any(lic[s] == "internal" for s in srcs) else "public"
    log(f"input sources {sorted(srcs)}: licenses {sorted({lic[s] for s in srcs})} -> {out}")
    return out, sorted(srcs)


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"energy_projects_{run_id}.log"))
    have = lambda n: os.path.exists(os.path.join(ip.OUT_DIR, n + ".csv"))  # noqa: E731
    absent = [n for n in INPUTS if not have(n)]
    present_queues = [q for q in QUEUES if have(q)]
    # session 18: some queues absent, the rest present: build from what is here
    partial = bool(present_queues) and all(have(n) for n in REQUIRED)
    if absent and not partial and os.environ.get("GITHUB_ACTIONS") == "true":
        msg = (f"inputs absent in CI ({len(absent)} tables, e.g. {', '.join(absent[:3])}; the queues are "
               "pulled on Mondays or a manual run); table not written (session 10 ruling 3)")
        log(f"SKIPPED: {msg}")
        print(f"::warning::energy_projects SKIPPED: {msg}")
        print(f"energy_projects SKIPPED: {msg}")
        ip.write_status("energy_projects", run_id, [dict(table=NAME, market="", status="skipped", detail=msg)])
        log.close()
        return 0
    try:
        if absent and not partial:
            raise RuntimeError(f"input tables absent: {absent}")
        inputs = REQUIRED + present_queues
        missing_q = [(q, absent_reason(q)) for q in QUEUES if q not in present_queues]
        for q, why in missing_q:
            log(f"ABSENT input {q}: {why}; the table is built from the other queues")
            print(f"::warning::energy_projects: {q} absent ({why}); built from {len(present_queues)} queues")
        log(f"ERW energy_projects {run_id}: method {METHOD}")
        license_, srcs = derived_license(log, inputs)
        look, got = load_gazetteer(run_id, log)
        t = build(look, log, [q.split("_")[0] for q in present_queues])
        n = len(t)
        by = t.groupby(["kind", "geo_precision"]).size()
        log("rows by kind and geo_precision: " + "; ".join(f"{k[0]} {k[1]} {v}" for k, v in by.items()))
        for why, c in t.loc[t["geo_precision"] == "none", "geo_note"].str.replace(r"'.*'", "'...'", regex=True) \
                .value_counts().head(10).items():
            log(f"  not placed: {c} rows: {why}")
        header = [
            "Energy Research Warehouse (ERW): Energy projects for the project map: EIA-860M generators "
            "and ISO interconnection queue positions (derived, platform tool 3)",
            "Shape: entities (docs/datastandard.md), a snapshot (Decision 21): each run replaces the table. "
            "One row per input row. project_id = entity_id; mw = capacity_mw as the source states it.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/energy_projects.py",
            f"Run log: warehouse/output/logs/energy_projects_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, energy projects method ({METHOD}), {METHOD_URL}",
            "Derived from: " + "; ".join(inputs),
            "  input sources: " + "; ".join(srcs),
            f"Geocoding: {GAZ_SOURCE} U.S. Census Bureau, Gazetteer Files, counties: {got[0][0]} ({GAZ_URL}), "
            f"and, only for names it lacks (Connecticut's legacy counties), {got[1][0]} ({GAZ_URL_2020}); "
            f"retrieved {ip.utc_iso(got[0][1]['retrieved_at'])}, kept in warehouse/raw/census_gazetteer/{run_id}/ "
            "(manifest.csv). lat and lon of a county-precision row are the county's internal point "
            "(INTPTLAT, INTPTLONG); geo_note names the county and the file.",
            "geo_precision: point (EIA's plant coordinates), county (the county's internal point, from county "
            "and state), none (no county or state matched; geo_note says why).",
            "kind: operating (eia860m_operating_generators), planned (eia860m_planned_generators), queue "
            "(<iso>_interconnection_queue). date: operating year, planned operation date or queue date, named "
            "by date_kind. operator_role: operator (EIA) or developer (the queue's interconnection customer).",
            f"License: {license_}. A derived table inherits the most restrictive license of its inputs "
            "(Decision 23); the Census gazetteer is public domain.",
        ]
        if missing_q:
            header.append("Absent inputs: " + "; ".join(f"{q} ({why})" for q, why in missing_q)
                          + ". Their queue positions are not in this snapshot (session 18).")
        ip.write_snapshot(t, NAME, header, log, COLS)
        ip.update_sources([
            dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                 report="Energy projects for the project map (docs/methods/energy_projects.md)",
                 report_url=METHOD_URL, document_list=METHOD, license=license_, tables=[NAME]),
            dict(source=GAZ_SOURCE, publisher="U.S. Census Bureau",
                 report="Gazetteer Files, counties (2025), county internal points", report_url=GAZ_URL,
                 document_list=GAZ_PAGE, license="public", tables=[NAME]),
        ])
        detail = (f"absent: {', '.join(q for q, _ in missing_q)}; " if missing_q else "") + f"{n} rows; " \
            + "; ".join(f"{k[0]} {k[1]} {v}" for k, v in by.items())
        status = [dict(table=NAME, market="", status="ok", detail=detail[:300])]
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"energy_projects FAILED, no output file written: {last}", file=sys.stderr)
        status = [dict(table=NAME, market="", status="failed", detail=last[:300])]
    ip.write_status("energy_projects", run_id, status)
    log.close()
    print(f"energy_projects run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if status[0]["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
