#!/usr/bin/env python3
"""The datacenter tracker's one table: facilities from the news, the operators and the queues.

Energy Research Warehouse (ERW), session 22 (Task 2c and 2d). Method:
docs/methods/datacenter_facilities.md.

    python warehouse/derived/datacenter_facilities.py
    python warehouse/derived/datacenter_facilities.py --in-dir DIR --out-dir DIR2 --no-gazetteer   # a trial (session 166):
        the inputs read from DIR, every output (the table, the queue positions, logs, registry, status) under DIR2,
        and no request to the Census for the gazetteer: a queue row then keeps no point (a trial's rows say so)

Inputs, three kinds (the kind column):
- news: datacenter_projects (warehouse/datacenters/extract.py), facilities named in scored
  news stories, every field checked against the story;
- operator: datacenter_operator_sites (warehouse/datacenters/operators/run.py), the
  operators' own public lists of regions, campuses and data centers;
- queue: rows of the six ISO interconnection queues (<iso>_interconnection_queue) whose
  project name or fuel field indicates a datacenter or a large load (QUEUE_PATTERN). A queue
  position's MW is the generation or storage it asks to connect, not the load, so it is kept
  as queue_mw and never as the facility's mw.

Deduplication by operator plus location (session 22 prompt, Task 2d). Two rows are the same
facility when they share an operator (after the aliases in OPERATOR_ALIASES; a news row's
operator or developer) and a location: the same state and the same county or city, or both
placed within MATCH_KM of each other. Sites an operator lists separately (Vantage Ashburn I,
II and III; Equinix DC1 to DC15) are distinct by the operator's own word and are never merged
with each other. A news or queue row that matches exactly one operator site joins it; one
that matches several is kept on its own and geo_note says it was ambiguous. News rows that
match each other are merged (the extractor has no site ids). Rows without a state and a
county, city or point are never merged. The merged facility keeps: the operator site's name,
place and coordinates where there is one; mw from the operator's stated span, else the news;
status from the news (dated), else the operator; every member's id and source link.

Shape: entities (docs/datastandard.md), entity_type datacenter, a snapshot. A derived table
(Decision 23): source erw:datacenter_facilities, source_url the method doc.

Session 166 (accuracy): country is "US" when the row states a US state (or the District of Columbia) and empty
otherwise; no source records a country, so a row without a US state has none (Firmus's Tasmanian rows among them),
and geo is "US-<state>" or empty, never "US" for a row whose country no source states. The page counts only rows
with country "US" whose status is not withdrawn (cancelled) in its totals and bars.
"""

import argparse
import datetime as dt
import math
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import energy_projects as ep  # noqa: E402  (county gazetteer, plain names)

NAME = "datacenter_facilities"
METHOD = "docs/methods/datacenter_facilities.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_facilities.md"
SOURCE = "erw:datacenter_facilities"
NEWS, OPS = "datacenter_projects", "datacenter_operator_sites"
QUEUE_TABLE = "datacenter_queue_positions"  # the matched queue rows, kept between the weekly queue pulls
QUEUES = [f"{i}_interconnection_queue" for i in ep.QUEUE_ISOS]
QUEUE_PATTERN = re.compile(r"data ?cent(?:er|re)s?|datacenter|large load|co-?located load|digital campus|"
                           r"hyperscale|crypto|bitcoin", re.I)
MATCH_KM = 25.0
OPERATOR_ALIASES = {
    "amazon": ["amazon web services", "amazon data services", "amazon", "aws"],
    "microsoft": ["microsoft", "azure"],
    "google": ["google", "alphabet"],
    "meta": ["meta platforms", "meta", "facebook"],
    "oracle": ["oracle"],
    "vantage": ["vantage data centers", "vantage"],
    "switch": ["switch"],
    "digital realty": ["digital realty"],
    "equinix": ["equinix"],
    "qts": ["qts"],
    "coreweave": ["coreweave"],
    "crusoe": ["crusoe"],
}
STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date",
       "operator", "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["kind", "kinds", "site_type", "developer", "state", "county", "city", "country", "mw", "mw_span", "mw_from",
         "queue_mw", "project_status", "phase", "planned_year", "power_source", "utility", "confidence",
         "first_story_at", "geo_precision", "geo_note", "n_members", "member_ids", "source_urls"]
NEWS_ONLY = ["phase", "planned_year", "power_source", "utility", "confidence", "first_story_at"]
COLS = STD + EXTRA
PRIORITY = {"operator": 0, "news": 1, "queue": 2}
US_STATES = set(ep.STATES.values())  # the 50 states and the District of Columbia, as postal codes
IN_DIR = None  # session 166: --in-dir reads the inputs from another directory (a trial); None reads ip.OUT_DIR
GAZETTEER = True  # --no-gazetteer: no request to the Census; a queue row is then not placed


def country_of(state):
    """Session 166: "US" when the row states a US state; empty when no source states a country."""
    return "US" if state in US_STATES else ""


def read(name):
    path = os.path.join(IN_DIR or ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def op_keys(*names):
    """The alias keys a row's operator and developer names carry ("Amazon Data Services" -> amazon);
    a name with no alias is its own key (plain text)."""
    keys = set()
    for n in names:
        p = ep.plain(n)
        if not p:
            continue
        hit = [k for k, al in OPERATOR_ALIASES.items() if any(re.search(r"\b" + re.escape(a) + r"\b", p) for a in al)]
        keys |= set(hit) if hit else {re.sub(r"\b(inc|llc|corp|corporation|co|ltd|lp)\b", "", p).strip()}
    return keys


def loc_key(s):
    s = ep.plain(s)
    return re.sub(r"\b(county|parish|city of)\b", "", s).strip()


def km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2, dl = math.radians(la1), math.radians(la2), math.radians(lo2 - lo1)
    x = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(min(1.0, x)))


def point(r):
    try:
        return (float(r["lat"]), float(r["lon"])) if r["lat"] and r["lon"] else None
    except ValueError:
        return None


def same_place(a, b):
    if not a["state"] or a["state"] != b["state"]:
        return False
    for f in ("county", "city"):
        if a[f] and b[f] and loc_key(a[f]) == loc_key(b[f]):
            return True
    pa, pb = point(a), point(b)
    return bool(pa and pb and km(pa, pb) <= MATCH_KM)


def members(log):
    """Every input row as one member dict, with its kind."""
    out = []
    news = read(NEWS)
    if news is None:
        raise RuntimeError(f"{NEWS}.csv is missing; run warehouse/datacenters/extract.py")
    for r in news.to_dict("records"):
        out.append(dict(kind="news", id=r["entity_id"], name=r["site_name"] or r["name"], operator=r["operator"],
                        developer=r["developer"], state=r["state"], county=r["county"], city=r["city"],
                        lat=r["lat"], lon=r["lon"], mw=r["mw"], mw_span="", status=r["status"],
                        project_status=r["project_status"], site_type="", geo_precision=r["geo_precision"],
                        geo_note=r["geo_note"], source=r["source"], source_url=r["source_url"],
                        urls=[u for u in r["story_urls"].split(";") if u] or [r["source_url"]], queue_mw="",
                        **{f: r[f] for f in NEWS_ONLY}))
    ops = read(OPS)
    if ops is None:
        log(f"  WARNING: {OPS}.csv is missing; no operator sites (run warehouse/datacenters/operators/run.py)")
    else:
        for r in ops.to_dict("records"):
            out.append(dict(kind="operator", id=r["entity_id"], name=r["name"], operator=r["operator"], developer="",
                            state=r["state"], county=r["county"], city=r["city"], lat=r["lat"], lon=r["lon"],
                            mw=r["mw"], mw_span=r["mw_span"], status=r["status"], project_status=r["status_text"],
                            site_type=r["site_type"], geo_precision=r["geo_precision"], geo_note=r["geo_note"],
                            source=r["source"], source_url=r["source_url"], urls=[r["source_url"]], queue_mw="",
                            **{f: "" for f in NEWS_ONLY}))
    qp = queue_positions(log)
    look = None
    for r in qp.to_dict("records"):
        if look is None and GAZETTEER:
            run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            look, _ = ep.load_gazetteer(run_id, log)
        if look is None:
            a, b, p, note = None, None, "none", "not placed: the gazetteer was not read (--no-gazetteer, a trial)"
        else:
            a, b, p, note = ep.geocode(r["state"], r["county"], look)
        out.append(dict(kind="queue", id=r["entity_id"], name=r["name"], operator=r["operator"], developer="",
                        state=r["state"], county=r["county"], city="", lat=f"{a:.6f}" if a is not None else "",
                        lon=f"{b:.6f}" if b is not None else "", mw="", mw_span="", status=r["status"],
                        project_status=r["iso_status"], site_type="queue_position", geo_precision=p,
                        geo_note=note, source=r["source"], source_url=r["source_url"], urls=[r["source_url"]],
                        queue_mw=r["capacity_mw"], **{f: "" for f in NEWS_ONLY}))
    log(f"  members: {sum(m['kind'] == 'news' for m in out)} news, {sum(m['kind'] == 'operator' for m in out)} "
        f"operator, {len(qp)} queue")
    return out


def queue_positions(log):
    """The queue rows whose name or fuel field matches QUEUE_PATTERN, as the table
    datacenter_queue_positions (the queue's own columns). An ISO whose queue table is absent (in CI
    the queues are pulled on Mondays only) keeps its rows from the last table, and the log says so;
    the table is rewritten only when at least one queue was read."""
    prev = read(QUEUE_TABLE)
    parts, read_any = [], False
    for q in QUEUES:
        iso = q.split("_", 1)[0]
        df = read(q)
        if df is None:
            kept = prev[prev["entity_id"].str.startswith(f"{iso}_queue:")] if prev is not None else None
            n = 0 if kept is None else len(kept)
            log(f"  {q}.csv is absent; {n} matched rows kept from the last {QUEUE_TABLE}")
            if n:
                parts.append(kept)
            continue
        read_any = True
        hit = df[df["name"].str.contains(QUEUE_PATTERN) | df["fuel_technology"].str.contains(QUEUE_PATTERN)].copy()
        log(f"  {q}: {len(df)} rows, {len(hit)} whose name or fuel field indicates a datacenter or large load")
        if len(hit):
            hit["matched"] = [QUEUE_PATTERN.search(f"{a} | {b}").group(0) for a, b in zip(hit["name"], hit["fuel_technology"])]
            parts.append(hit)
    cols = (list(prev.columns) if prev is not None else None)
    table = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=cols or ["entity_id"])
    if read_any and len(table):
        header = [
            "Energy Research Warehouse (ERW): ISO queue positions that name a datacenter or a large load (session 22)",
            "Shape: entities (docs/datastandard.md), the queue tables' own columns and rows, plus matched (the words "
            "that matched). capacity_mw is the generation or storage the position asks to connect, not the load.",
            "Retrieved: by warehouse/derived/datacenter_facilities.py from " + ", ".join(QUEUES) + " (an absent queue "
            "keeps its rows from the previous file)",
            f"Pattern, on the name and fuel_technology fields only: {QUEUE_PATTERN.pattern}",
            f"Method: {METHOD}. License: public (the ISOs' queue reports).",
        ]
        ip.write_snapshot(table, QUEUE_TABLE, header, log, list(table.columns))
    elif not read_any:
        log(f"  no queue table present; {QUEUE_TABLE} kept as it was ({len(table)} rows)")
    return table


def merge(ms, log):
    """Groups of members that are one facility (see the module docstring)."""
    for m in ms:
        m["keys"] = op_keys(m["operator"], m["developer"])
    ops = [m for m in ms if m["kind"] == "operator"]
    groups = [[m] for m in ops]
    anchor = {m["id"]: g for m, g in zip(ops, groups)}
    loose = []
    ambiguous = 0
    for m in (x for x in ms if x["kind"] != "operator"):
        placed = m["state"] and (m["county"] or m["city"] or point(m))
        cands = [o for o in ops if placed and m["keys"] & o["keys"] and same_place(m, o)] if m["keys"] else []
        if len(cands) == 1:
            anchor[cands[0]["id"]].append(m)
            continue
        if len(cands) > 1:
            ambiguous += 1
            m["geo_note"] = (m["geo_note"] + "; " if m["geo_note"] else "") + \
                f"matches {len(cands)} operator sites at this place; not merged (ambiguous)"
        loose.append(m)
    # news rows that match each other (same operator and place); queue rows stay on their own
    for m in loose:
        placed = m["state"] and (m["county"] or m["city"] or point(m))
        target = None
        if m["kind"] == "news" and placed and m["keys"]:
            target = next((g for g in groups if g[0]["kind"] == "news" and m["keys"] & g[0]["keys"]
                           and same_place(m, g[0])), None)
        if target is not None:
            target.append(m)
        else:
            groups.append([m])
    log(f"  {len(ms)} members -> {len(groups)} facilities; {ambiguous} rows matched several operator sites "
        f"and were kept on their own")
    return groups


def facility(g, now):
    g = sorted(g, key=lambda m: PRIORITY[m["kind"]])
    head = g[0]
    first = lambda f, order=None: next((m[f] for m in (order or g) if m[f]), "")  # noqa: E731
    by_news_first = sorted(g, key=lambda m: {"news": 0, "operator": 1, "queue": 2}[m["kind"]])
    mw_member = next((m for m in g if m["mw"]), None)
    r = {c: "" for c in COLS}
    # a news facility keeps its id (datacenter:<hex>); another head's id is prefixed (datacenter:dcsite-<hex>,
    # datacenter:ercot_queue-25INR0688)
    hid = head["id"]
    r.update(entity_id=hid if hid.startswith("datacenter:") else "datacenter:" + hid.replace(":", "-"),
             entity_type="datacenter", name=head["name"], operator=first("operator"), developer=first("developer"),
             state=first("state"), county=first("county"), city=first("city"), lat=head["lat"], lon=head["lon"],
             geo_precision=head["geo_precision"], geo_note=head["geo_note"], kind=head["kind"],
             kinds=";".join(sorted({m["kind"] for m in g}, key=PRIORITY.get)), site_type=head["site_type"],
             status=first("status", by_news_first), project_status=first("project_status", by_news_first),
             queue_mw=first("queue_mw"), source=head["source"], source_url=head["source_url"],
             retrieved_at=now, vintage=now[:10], n_members=str(len(g)),
             member_ids=";".join(m["id"] for m in g),
             source_urls=";".join(dict.fromkeys(u for m in g for u in m["urls"] if u)))
    if not head["lat"]:
        placed = next((m for m in g if m["lat"]), None)
        if placed:
            r["lat"], r["lon"], r["geo_precision"], r["geo_note"] = (placed["lat"], placed["lon"],
                                                                      placed["geo_precision"], placed["geo_note"])
    for f in NEWS_ONLY:
        r[f] = first(f, by_news_first)
    if mw_member:
        r["mw"] = r["capacity_mw"] = mw_member["mw"]
        r["mw_span"], r["mw_from"] = mw_member["mw_span"], f"{mw_member['kind']}:{mw_member['id']}"
    # session 166: a country only where a US state is stated; geo is never "US" on the word of no source
    r["country"] = country_of(r["state"])
    r["geo"] = f"US-{r['state']}" if r["country"] else ""
    return r


def main(argv=None):
    global IN_DIR, GAZETTEER
    ap = argparse.ArgumentParser(description="The datacenter tracker's one table (the module docstring)")
    ap.add_argument("--in-dir", help="read the input tables from this directory (a trial)")
    ap.add_argument("--out-dir", help="write the table, the queue positions, logs, registry and status under this directory (a trial)")
    ap.add_argument("--no-gazetteer", action="store_true", help="no request to the Census: queue rows are not placed (a trial)")
    a = ap.parse_args(argv)
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    IN_DIR = os.path.abspath(a.in_dir) if a.in_dir else None
    GAZETTEER = not a.no_gazetteer
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"datacenter_facilities_{run_id}.log"))
    log(f"ERW datacenter facilities {run_id}")
    try:
        ms = members(log)
        groups = merge(ms, log)
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        table = pd.DataFrame([facility(g, now) for g in groups], columns=COLS)
        dup = table["entity_id"].duplicated()
        if dup.any():
            raise RuntimeError(f"{int(dup.sum())} repeated entity ids: {table.loc[dup, 'entity_id'].head().tolist()}")
        table = table.sort_values(["state", "operator", "name"]).reset_index(drop=True)
        n_mw = int((table["mw"] != "").sum())
        header = [
            "Energy Research Warehouse (ERW): Datacenter facilities from the news, the operators and the ISO queues "
            "(the datacenter power tracker, platform tool 4; session 22)",
            "Shape: entities (docs/datastandard.md), entity_type datacenter; a snapshot. kind: news, operator or "
            "queue (the first member's); kinds lists every member's kind. capacity_mw = mw, as a source states it "
            "(mw_from names the member, mw_span the operator's exact words); queue_mw is a queue position's "
            "generation or storage MW, not the load.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/datacenter_facilities.py",
            f"Run log: warehouse/output/logs/datacenter_facilities_{run_id}.log",
            f"Derived from: {NEWS}, {OPS}, " + ", ".join(QUEUES) + f". Method: {METHOD}.",
            f"Deduplication: operator (aliases) plus location (same state and county or city, or within {MATCH_KM:g} km); "
            "an operator's own separately listed sites are never merged with each other.",
            f"Facilities: {len(table)}; with a stated MW: {n_mw}; with a US state stated (country US): "
            f"{int((table['country'] == 'US').sum())}. No source records a country: a row without a US state has none, "
            "and geo is empty for it (session 166).",
            "License: public (the news rows carry no outlet text; operator and queue facts are public).",
        ]
        ip.write_snapshot(table, NAME, header, log, COLS)
        ip.update_sources([dict(source=SOURCE, publisher="ERW",
                                report="Datacenter facilities: news, operator lists and ISO queues, deduplicated",
                                report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        ip.write_status("datacenter_facilities", run_id, [dict(table=NAME, market="all", status="ok",
                                                               detail=f"{len(table)} facilities, {n_mw} with MW")])
    except Exception as exc:
        log(f"FAILED: {exc!r}")
        ip.write_status("datacenter_facilities", run_id, [dict(table=NAME, market="all", status="failed",
                                                               detail=repr(exc)[:300])])
        log.close()
        raise
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
