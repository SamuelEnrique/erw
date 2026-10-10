"""Energy Research Warehouse (ERW): the project map's files (session 105; session 167: the one page's file).

  python warehouse/derived/project_map.py            # site/data/map_v2.json and site/data/map.json, from the tables on this machine
  python warehouse/derived/project_map.py --in-dir C:/path/to/warehouse/output      # the tables of another folder (read only)

Session 167: /map is one page. Its file is site/data/map.json (build_page below): EIA's operating and planned units
with EIA's own status code for each (the connector's eia_status, kept beside the folded status since session 8), the
queue positions of energy_projects that are not withdrawn, and the datacenters of datacenter_facilities that the table
places in a US state, with the fields the unit card shows. site/data/map_v2.json is written as before, unchanged in
shape: /resources reads it. A file whose content did not change, apart from its built stamp, is left as it is.

Version 2's file (session 105), as it was:

Every operating and planned generating unit of EIA's monthly inventory (Form EIA-860M), batteries among them, as the
page /map/v2 reads it: one compact column per field, a unit per position. It makes no request and writes no warehouse
table: the units are the rows of eia860m_operating_generators and eia860m_planned_generators, unchanged. A site file,
like the network's replay files. Session 114: rebuilt by the monthly job (warehouse/run_monthly.sh), no longer by hand.

Fields of a unit: name (the plant's), state, grid (the seven ISOs by EIA's balancing authority code; every other
balancing authority, and a blank one, is "outside the seven ISOs"), technology group (the inventory's eleven; a
battery is the storage group's units whose prime mover is BA), status (operating, under construction, planned), MW
(nameplate, capacity_mw), the year it began or is planned to begin operating, latitude and longitude as EIA gives them.
Nothing is estimated and no unit is left out: a unit with no technology group is "not stated".
"""
import argparse
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

TABLES = ("eia860m_operating_generators", "eia860m_planned_generators")
SITE_FILE = os.path.join(ROOT, "site", "data", "map_v2.json")
GRIDS = [("ERCO", "ercot", "ERCOT"), ("CISO", "caiso", "CAISO"), ("PJM", "pjm", "PJM"), ("MISO", "miso", "MISO"), ("SWPP", "spp", "SPP"),
         ("NYIS", "nyiso", "NYISO"), ("ISNE", "isone", "ISO-NE")]
OUTSIDE = ("outside", "Outside the seven ISOs")
TECHS = [("solar", "Solar"), ("wind", "Wind"), ("battery", "Batteries"), ("storage", "Other storage"), ("natural_gas", "Natural gas"), ("nuclear", "Nuclear"),
         ("coal", "Coal"), ("hydro", "Hydro"), ("petroleum", "Petroleum"), ("biomass", "Biomass"), ("geothermal", "Geothermal"), ("other", "Other"),
         ("unknown", "Not stated")]
STATUSES = [("operating", "Operating"), ("under_construction", "Under construction"), ("planned", "Planned")]


def read(name, out=None):
    path = os.path.join(out or ip.OUT_DIR, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def units(out=None):
    """Every unit of the two tables, one frame, with the map's fields."""
    op, pl = read(TABLES[0], out), read(TABLES[1], out)
    op["year"] = op["operating_year"]
    pl["year"] = pl["planned_operation_date"].str[:4]
    d = pd.concat([op, pl], ignore_index=True)
    code = {c: slug for c, slug, _ in GRIDS}
    d["grid"] = d["balancing_authority"].map(code).fillna(OUTSIDE[0])
    known = {t for t, _ in TECHS}
    d["tech"] = d["technology_group"].where(d["technology_group"].isin(known), "unknown")
    d.loc[(d["technology_group"] == "storage") & (d["prime_mover"] == "BA"), "tech"] = "battery"
    d["mw"] = pd.to_numeric(d["capacity_mw"], errors="coerce")
    d["lat"] = pd.to_numeric(d["lat"], errors="coerce")
    d["lon"] = pd.to_numeric(d["lon"], errors="coerce")
    if d["mw"].isna().any() or not set(d["status"]) <= {s for s, _ in STATUSES}:
        raise ValueError("a unit has no MW, or a status the map does not know")
    return d


def build(out=None):
    d = units(out).sort_values(["mw", "entity_id"], ascending=[False, True]).reset_index(drop=True)
    vintages = sorted(set(d["vintage"]))
    if len(vintages) != 1:
        raise ValueError(f"the two tables are of different months: {vintages}")
    names = sorted(set(d["name"]))
    name_i = {n: i for i, n in enumerate(names)}
    states = sorted(set(d["state"]))
    grids = [slug for _, slug, _ in GRIDS] + [OUTSIDE[0]]
    techs = [t for t, _ in TECHS]
    statuses = [s for s, _ in STATUSES]
    located = d["lat"].notna() & d["lon"].notna()
    return {
        "tables": list(TABLES), "vintage": vintages[0], "retrieved": d["retrieved_at"].max(), "source_url": d["source_url"].iloc[0],
        "built": ip.utc_iso(pd.Timestamp.now(tz="UTC")),
        "grids": [{"slug": slug, "name": name} for _, slug, name in GRIDS] + [{"slug": OUTSIDE[0], "name": OUTSIDE[1]}],
        "techs": [{"slug": t, "name": n} for t, n in TECHS], "statuses": [{"slug": s, "name": n} for s, n in STATUSES],
        "states": states, "names": names,
        "counts": {"units": int(len(d)), "operating": int((d["status"] == "operating").sum()), "under_construction": int((d["status"] == "under_construction").sum()),
                   "planned": int((d["status"] == "planned").sum()), "batteries": int((d["tech"] == "battery").sum()),
                   "without_balancing_authority": int((d["balancing_authority"] == "").sum()), "under_1_mw": int((d["mw"] < 1).sum()),
                   "without_coordinates": int((~located).sum()), "without_year": int((d["year"] == "").sum()), "mw": round(float(d["mw"].sum()), 1)},
        # one column a field, a unit a position, largest first
        "n": [name_i[x] for x in d["name"]], "s": [states.index(x) for x in d["state"]], "g": [grids.index(x) for x in d["grid"]],
        "t": [techs.index(x) for x in d["tech"]], "st": [statuses.index(x) for x in d["status"]], "mw": [round(float(x), 1) for x in d["mw"]],
        "y": [int(x) if x.isdigit() else 0 for x in d["year"]],
        "la": [None if pd.isna(x) else round(float(x), 4) for x in d["lat"]], "lo": [None if pd.isna(x) else round(float(x), 4) for x in d["lon"]],
    }


# ---------------------------------------------------------------------------------------------------------------------
# Session 167: the one page's file, site/data/map.json
# ---------------------------------------------------------------------------------------------------------------------
PAGE_FILE = os.path.join(ROOT, "site", "data", "map.json")
PAGE_TABLES = TABLES + ("energy_projects", "datacenter_facilities")
KINDS = [("operating", "Operating units"), ("planned", "Planned units"), ("queue", "Queue positions"), ("datacenter", "Datacenters")]
# EIA's own status codes for a proposed unit (the EIA-860 instructions), in the plain words the owner gave (8 October 2026)
EIA_PROPOSED = [("P", "Planned, regulatory approvals not started"), ("L", "Regulatory approvals pending"),
                ("T", "Regulatory approvals received, not under construction"), ("U", "Under construction, half or less complete"),
                ("V", "Under construction, more than half complete"), ("TS", "Construction complete, not yet operating"), ("OT", "Other")]
EIA_OPERATING = ["OP", "SB", "OA", "OS"]           # the card names EIA's own label when the code is not OP
# a queue position's and a datacenter's own statuses (the tables' standard words), in this order when the table holds them
QUEUE_STATUS = [("active", "Active"), ("suspended", "Suspended"), ("completed", "Completed"), ("", "Not stated")]
DC_STATUS = [("operating", "Operating"), ("under_construction", "Under construction"), ("planned", "Planned"), ("active", "Active"),
             ("completed", "Completed"), ("withdrawn", "Withdrawn"), ("", "Not stated")]
# the queues whose rows the page may draw (site/lib/resources.ts, QUEUE_GRIDS, is the one list a person switches; a test
# holds the two equal). A held grid's rows are counted and never written to the file
QUEUE_SHOWN = {"ercot": "ERCOT", "spp": "SPP", "caiso": "CAISO", "isone": "ISO-NE"}
QUEUE_HELD = {"miso": ("MISO", "paused while terms are reviewed"), "nyiso": ("NYISO", "NYISO's terms do not allow it")}
PAGE_TECHS = TECHS[:-1] + [("queue_storage", "Storage (queue positions)"), ("hybrid", "Hybrid"), ("transmission", "Transmission"),
                           ("datacenter", "Datacenter (a load)"), TECHS[-1]]
NO_GRID = ("none", "Grid not stated")
PRECISION = {"point": 0, "county": 1, "place": 2, "operator": 3, "none": 4, "": 4}
CARD_KEYS = ("id", "o", "c", "tx", "operators", "counties", "technologies", "more")   # what only the unit card reads (the page reads them from /map/card)


def _date(text):
    """A date of the tables as a whole number: a queue date 2023-02-24 is 20230224, a year 2027 is 2027, nothing is 0."""
    t = (text or "").strip()
    if len(t) >= 10 and t[4] == "-" and t[7] == "-" and (t[:4] + t[5:7] + t[8:10]).isdigit():
        return int(t[:4] + t[5:7] + t[8:10])
    return int(t) if t.isdigit() and len(t) == 4 else 0


def page_rows(out=None):
    """Every row of the one page, one frame, a kind after another, the largest first inside a kind; the queues held
    back with their row counts; and the number of datacenters the table places in no US state."""
    d = units(out)
    d["kind"] = d["status"].map(lambda s: "operating" if s == "operating" else "planned")
    proposed = {c for c, _ in EIA_PROPOSED}
    bad = sorted(set(d.loc[d["kind"] == "planned", "eia_status"]) - proposed) + sorted(set(d.loc[d["kind"] == "operating", "eia_status"]) - set(EIA_OPERATING))
    if bad:
        raise ValueError(f"an EIA status code the map does not know: {bad}")
    d["st_slug"] = d["eia_status"].str.lower().where(d["kind"] == "planned", "operating")
    d["precision"] = (d["lat"].notna() & d["lon"].notna()).map({True: 0, False: 4})
    # EIA gives months: the operating month (status_date) or the planned one, as YYYYMM; the year alone where no month
    month = d["status_date"].where(d["kind"] == "operating", d["planned_operation_date"]).fillna("")
    d["date"] = [int(m[:4] + m[5:7]) if len(m) >= 7 else (int(y) if str(y).isdigit() else 0) for m, y in zip(month, d["year"])]
    d["card_id"] = d["entity_id"].str.replace("eia860:", "", n=1, regex=False)
    d["role"] = 0
    d["technology_text"] = d["technology"]

    ep = read("energy_projects", out)
    q = ep[ep["kind"] == "queue"].copy()
    q["grid"] = q["source_table"].str.replace("_interconnection_queue", "", regex=False)
    unknown = sorted(set(q["grid"]) - set(QUEUE_SHOWN) - set(QUEUE_HELD))
    if unknown:
        raise ValueError(f"a queue the map has no ruling for: {unknown}")
    q = q[q["status"] != "withdrawn"]                  # as the older map: a withdrawn position is not on the map
    held = [{"grid": g, "name": QUEUE_HELD[g][0], "words": QUEUE_HELD[g][1], "rows": int((q["grid"] == g).sum())} for g in QUEUE_HELD if (q["grid"] == g).any()]
    q = q[q["grid"].isin(QUEUE_SHOWN)].copy()
    known = {s for s, _ in QUEUE_STATUS}
    if not set(q["status"]) <= known:
        raise ValueError(f"a queue status the map does not know: {sorted(set(q['status']) - known)}")
    q["st_slug"] = "q-" + q["status"].replace("", "none")
    q["tech"] = q["technology_group"].replace({"storage": "queue_storage", "": "unknown"})
    q["mw"] = pd.to_numeric(q["capacity_mw"], errors="coerce")
    q["lat"], q["lon"] = pd.to_numeric(q["lat"], errors="coerce"), pd.to_numeric(q["lon"], errors="coerce")
    q["precision"] = q["geo_precision"].map(PRECISION)
    q["date"] = q["date"].map(_date)
    q["card_id"] = q["entity_id"]
    q["role"] = (q["operator_role"] == "developer").astype(int)
    q["technology_text"] = q["technology"]

    dc = read("datacenter_facilities", out)
    without_state = int((dc["state"] == "").sum())
    dc = dc[dc["state"] != ""].copy()                  # a US map: a facility the table places in no US state is counted, not written
    dc["source_kind"] = dc["kind"]                     # the table's own kind: news, operator or queue
    dc["kind"] = "datacenter"
    dc["grid"] = NO_GRID[0]
    dc["tech"] = "datacenter"
    dc["st_slug"] = "dc-" + dc["status"].replace("", "none")
    dc["mw"] = pd.to_numeric(dc["capacity_mw"], errors="coerce")
    dc["lat"], dc["lon"] = pd.to_numeric(dc["lat"], errors="coerce"), pd.to_numeric(dc["lon"], errors="coerce")
    dc["precision"] = dc["geo_precision"].map(PRECISION)
    dc["date"] = dc["planned_year"].map(_date)
    dc["card_id"] = dc["entity_id"]
    dc["role"] = 0
    dc["technology_text"] = ""

    for frame, what in ((q, "queue position"), (dc, "datacenter")):
        if frame["precision"].isna().any():
            raise ValueError(f"a {what} has a geo_precision the map does not know")
        if not set(frame["tech"]) <= {t for t, _ in PAGE_TECHS}:
            raise ValueError(f"a {what} has a technology group the map does not know: {sorted(set(frame['tech']) - {t for t, _ in PAGE_TECHS})}")
    text = ["entity_id", "card_id", "kind", "name", "state", "county", "grid", "tech", "st_slug", "operator", "technology_text", "vintage", "retrieved_at",
            "eia_status", "eia_status_label", "source_status", "city", "developer", "power_source", "utility", "source_urls", "source_kind"]
    parts = []
    for frame in (d[d["kind"] == "operating"], d[d["kind"] == "planned"], q, dc):
        f = frame.reindex(columns=text + ["mw", "lat", "lon", "precision", "date", "role"]).copy()
        f[text] = f[text].fillna("")
        f["sort_mw"] = f["mw"].fillna(-1.0)
        parts.append(f.sort_values(["sort_mw", "entity_id"], ascending=[False, True]))
    rows = pd.concat(parts, ignore_index=True)
    if rows["entity_id"].duplicated().any():
        raise ValueError("an entity is twice in the map's rows")
    return rows, held, without_state


def _index(values):
    names = sorted(set(values))
    return names, {n: i for i, n in enumerate(names)}


def build_page(out=None, card=True):
    """The one page's file. `card=False` leaves out what only the unit card reads (to weigh it; the page needs it)."""
    r, held, without_state = page_rows(out)
    eia = r[r["kind"].isin(["operating", "planned"])]
    vintages = sorted(set(eia["vintage"]))
    if len(vintages) != 1:
        raise ValueError(f"the two EIA tables are of different months: {vintages}")
    kinds = [k for k, _ in KINDS]
    grids = [slug for _, slug, _ in GRIDS] + [OUTSIDE[0], NO_GRID[0]]
    techs = [t for t, _ in PAGE_TECHS]
    statuses = [{"slug": "operating", "name": "Operating", "kind": 0}] + [{"slug": c.lower(), "name": n, "kind": 1} for c, n in EIA_PROPOSED]
    for ki, prefix, kind, vocabulary in ((2, "q-", "queue", QUEUE_STATUS), (3, "dc-", "datacenter", DC_STATUS)):
        have = set(r.loc[r["kind"] == kind, "st_slug"])
        listed = [(prefix + (s or "none"), n) for s, n in vocabulary]
        statuses += [{"slug": slug, "name": name, "kind": ki} for slug, name in listed if slug in have]
        # a status the table added since: its own word, never renamed
        statuses += [{"slug": slug, "name": slug[len(prefix):].replace("_", " ").capitalize(), "kind": ki} for slug in sorted(have - {s for s, _ in listed})]
    st_i = {s["slug"]: i for i, s in enumerate(statuses)}
    names, name_i = _index(r["name"])
    states = sorted(set(r["state"]))
    is_kind = {k: r["kind"] == k for k in kinds}
    u = units(out)
    f = {
        "tables": list(PAGE_TABLES), "vintage": vintages[0],
        "vintages": {k: (r.loc[is_kind[k], "vintage"].max() if is_kind[k].any() else "") for k in kinds},
        "retrieved": eia["retrieved_at"].max(), "source_url": u["source_url"].iloc[0], "built": ip.utc_iso(pd.Timestamp.now(tz="UTC")),
        "kinds": [{"slug": k, "name": n, "start": int(is_kind[k].values.argmax()) if is_kind[k].any() else len(r), "rows": int(is_kind[k].sum())} for k, n in KINDS],
        "grids": [{"slug": slug, "name": name} for _, slug, name in GRIDS] + [{"slug": OUTSIDE[0], "name": OUTSIDE[1]}, {"slug": NO_GRID[0], "name": NO_GRID[1]}],
        "techs": [{"slug": t, "name": n} for t, n in PAGE_TECHS], "statuses": statuses, "states": states, "names": names, "held": held,
        "counts": {"rows": int(len(r)), **{k: int(is_kind[k].sum()) for k in kinds}, **{k + "_mw": round(float(r.loc[is_kind[k], "mw"].sum()), 1) for k in kinds},
                   "units": int(len(eia)), "units_mw": round(float(eia["mw"].sum()), 1),
                   "batteries": int((r["tech"] == "battery").sum()), "under_1_mw": int((eia["mw"] < 1).sum()),
                   "without_balancing_authority": int((u["balancing_authority"] == "").sum()),
                   "without_mw": int(r["mw"].isna().sum()), "not_placed": int((r["precision"] == 4).sum()),
                   "datacenters_without_state": without_state, "queue_rows_held": int(sum(h["rows"] for h in held))},
        # one column a field, a row a position: a kind after another (kinds[].start), the largest first inside a kind
        "k": [kinds.index(x) for x in r["kind"]], "n": [name_i[x] for x in r["name"]], "s": [states.index(x) for x in r["state"]],
        "g": [grids.index(x) for x in r["grid"]], "t": [techs.index(x) for x in r["tech"]], "st": [st_i[x] for x in r["st_slug"]],
        "mw": [None if pd.isna(x) else round(float(x), 1) for x in r["mw"]],
        "la": [None if pd.isna(x) else round(float(x), 4) for x in r["lat"]], "lo": [None if pd.isna(x) else round(float(x), 4) for x in r["lon"]],
        "pr": [int(x) for x in r["precision"]],
    }
    if not card:
        return f
    operators, op_i = _index(x for x in r["operator"] if x)
    counties, co_i = _index(x for x in r["county"] if x)
    technologies, te_i = _index(x for x in r["technology_text"] if x)
    op, q, dc = r[is_kind["operating"]], r[is_kind["queue"]], r[is_kind["datacenter"]]
    labels = dict(zip(op["eia_status"], op["eia_status_label"]))
    q_status, qs_i = _index(q["source_status"])
    f.update({
        "id": list(r["card_id"]), "o": [op_i.get(x, -1) for x in r["operator"]], "c": [co_i.get(x, -1) for x in r["county"]],
        "tx": [te_i.get(x, -1) for x in r["technology_text"]], "d": [int(x) for x in r["date"]],
        "operators": operators, "counties": counties, "technologies": technologies,
        # what one kind alone carries, a row of the kind a position (the row's position less kinds[].start)
        "more": {
            "operating": {"codes": [{"code": c, "label": labels.get(c, "")} for c in EIA_OPERATING], "code": [EIA_OPERATING.index(x) for x in op["eia_status"]]},
            "queue": {"statuses": q_status, "status": [qs_i[x] for x in q["source_status"]], "developer": [int(x) for x in q["role"]]},
            "datacenter": {"city": list(dc["city"]), "developer": list(dc["developer"]), "power": list(dc["power_source"]), "utility": list(dc["utility"]),
                           "from": list(dc["source_kind"]), "urls": [[x for x in urls.split(";") if x] for urls in dc["source_urls"]]},
        },
    })
    return f


def _same(path, new):
    """True when the file on disk says what `new` says, its built stamp apart."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as fh:
            old = json.load(fh)
    except ValueError:
        return False
    return {k: v for k, v in old.items() if k != "built"} == {k: v for k, v in new.items() if k != "built"}


def _write(path, f):
    """Write a site file, unless the one on disk already says the same (its built stamp then stays the day it was built)."""
    if _same(path, f):
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(f, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the project map's files (site/data/map_v2.json and site/data/map.json)")
    ap.add_argument("--in-dir", help="read the tables from this folder (default: warehouse/output of this copy); nothing is written there")
    args = ap.parse_args(argv)
    f = build(args.in_dir)
    wrote = _write(SITE_FILE, f)
    c = f["counts"]
    print(f"map_v2.json: {c['units']:,} units of EIA-860M {f['vintage']} ({c['operating']:,} operating, {c['under_construction']:,} under construction, "
          f"{c['planned']:,} planned; {c['batteries']:,} batteries), {c['mw']:,.1f} MW; {os.path.getsize(SITE_FILE):,} bytes"
          + ("" if wrote else "; unchanged, left as it is"))
    p = build_page(args.in_dir)
    wrote = _write(PAGE_FILE, p)
    c = p["counts"]
    print(f"map.json: {c['rows']:,} rows ({c['operating']:,} operating and {c['planned']:,} planned units of EIA-860M {p['vintage']}; {c['queue']:,} queue positions, "
          f"vintage {p['vintages']['queue']}; {c['datacenter']:,} datacenters, vintage {p['vintages']['datacenter']}); held back: "
          + (", ".join(f"{h['name']} {h['rows']:,} queue rows ({h['words']})" for h in p["held"]) or "none")
          + f"; {c['datacenters_without_state']:,} datacenters in no US state are not written; {os.path.getsize(PAGE_FILE):,} bytes"
          + ("" if wrote else "; unchanged, left as it is"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
