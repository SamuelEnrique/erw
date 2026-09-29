#!/usr/bin/env python3
"""Extract datacenter facilities from scored news stories: the datacenter power tracker (tool 4).

Energy Research Warehouse (ERW), session 16. The same pattern and rules as the deal
extractor (warehouse/deals/extract.py), whose checks it imports.

    python warehouse/datacenters/extract.py                 # every eligible story not yet checked
    python warehouse/datacenters/extract.py --max-calls 2   # a trial

Eligible stories: scored rows of warehouse/output/news_stories.csv with sector
datacenter_power, at any significance. Stories go by cluster (score.py's cluster_id), in
batches, to the newest Sonnet-class model, with a JSON schema. For each cluster the model
says whether the stories name a specific datacenter facility (a named site, or a named
operator or developer at a stated place) and, for each facility: operator, developer, site
name, state, county, city, MW, phase, status (announced, permitted, under_construction,
operating, cancelled), planned year, power source, utility, confidence, and the evidence
sentence. Market commentary, sponsored content and company-wide plans without a site are
not facilities.

Nothing is inferred beyond the stated words (session 16 human ruling), and every value is
checked against the story's own title and summary:
- mw: the exact span it was read from must be in the story and parse to the same value
  (GW and MW applied), as in the deal extractor;
- state and status: the span each was read from must be in the story; a state's span must
  name it (name or postal code);
- county and city: the span (location_text) must be in the story and contain the name;
- planned_year: its span must be in the story and contain the year;
- operator, developer, site name, power source and utility: the name must appear in the story;
- anything that fails is left empty, and the run log names it.
ai_power is true on every row: this table is the platform's AI and datacenter power subset,
as ai_power marks that subset among the deals.

Deduplication by site: each call carries a reference list of the facilities already
extracted (id, operator, developer, site, place, MW); the model marks a facility that is one
of them (same_as), and that story's links are added to it, with any field the facility
still lacks filled from the new story.

Location for the map: a facility with a stated state and county is placed at the county's
internal point (Census county gazetteer, geo_precision county); with a state and city only,
at the city's internal point (Census places gazetteer, 2025, geo_precision place); else not
placed (geo_precision none). The gazetteers are downloaded each run into
warehouse/raw/census_gazetteer/<run_id>/.

Outputs:
  warehouse/output/datacenter_projects.csv            entities, entity_type datacenter,
      license public: the model's checked fields and the story links, no outlet text
  warehouse/output/datacenter_projects_evidence.csv   events, license internal: one row per
      facility and story, with the evidence sentence (outlet text)
  warehouse/datacenters/checked.csv                   every story sent (tracked in git)
Session 17 human ruling: an "applied" status (an application filed, not yet granted), and the
status span is required: a status without its span is left empty, which is correct.
--reextract rebuilds the tables from every story already checked (earlier tables kept in
warehouse/datacenters/history/).
Standard status (entities vocabulary): announced, applied and permitted -> planned,
under_construction, operating, cancelled -> withdrawn; the extractor's own word is in
project_status.
"""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import traceback

import anthropic
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import iso_prices as ip  # noqa: E402
from ingest import NAME as NEWS, NEWS_COLS  # noqa: E402
import energy_projects as ep  # noqa: E402  (county gazetteer and name matching)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import llm  # noqa: E402  session 30: every Anthropic call goes through the cost ledger

# the deal extractor's checks, loaded by path: this file has the same module name
_spec = importlib.util.spec_from_file_location("deals_extract", os.path.join(ROOT, "warehouse", "deals", "extract.py"))
deals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(deals)
PRICES, clean, norm, pick_model, stated_words, verified = (
    deals.PRICES, deals.clean, deals.norm, deals.pick_model, deals.stated_words, deals.verified)

TABLE = "datacenter_projects"
EVIDENCE = "datacenter_projects_evidence"
CHECKED = os.path.join(HERE, "checked.csv")
SECTORS_IN = ["datacenter_power"]
# session 17 ruling: "applied" (an application filed, not yet granted) between announced and permitted
STATUSES = ["announced", "applied", "permitted", "under_construction", "operating", "cancelled"]
STD_STATUS = {"announced": "planned", "applied": "planned", "permitted": "planned", "under_construction": "under_construction",
              "operating": "operating", "cancelled": "withdrawn"}
PLACE_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_place_national.zip"
BATCH = 10
REFERENCE_MAX = 300

STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date",
       "operator", "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["kind", "developer", "site_name", "state", "county", "city", "mw", "phase", "project_status",
         "planned_year", "power_source", "utility", "ai_power", "confidence", "geo_precision", "geo_note",
         "first_story_at", "n_stories", "story_ids", "story_urls", "model_id", "extracted_at"]
COLS = STD + EXTRA
EVIDENCE_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency",
                 "status", "source", "source_url", "facility_id", "story_id", "evidence"]
CHECKED_COLS = ["story_id", "cluster_id", "checked_at", "model_id", "n_facilities"]

SYSTEM = f"""You extract datacenter facilities from energy news for the Energy Research Warehouse (ERW), the live, citable record of the US energy system.

Each item is one cluster: one or more stories (title and summary) about the same event. Decide whether the stories name a specific datacenter facility: a named datacenter site or campus, or a datacenter a named operator or developer is building, running or planning at a stated place. Market commentary, forecasts, conference reports, sponsored content, products, and company-wide spending plans without a site are not facilities: return none for them. Also not a facility (human ruling, session 23): a financing (a loan, an investment or a fund raise for a company or its datacenters with no named site), a purchase of chips or servers, and a campus that is not a datacenter (a factory, a manufacturing or office campus, even one run by a technology company).

For each facility, copy every value from the title or summary, character for character. Never infer: a value the words do not state is an empty string, and empty is the correct answer.
- operator: the company that will run or use the datacenter, as named; developer: the company building or owning the site, as named, if different; site_name: the site or campus name, as named
- state (US two-letter code) only if the story names that state (by name or postal code), with the exact span (state_text). Never infer a state from a city, county, utility or company.
- county, city: only as named, with location_text, the exact span that names them
- mw: the facility's power capacity or demand in MW as stated (digits only, GW converted to MW), with mw_text, the exact span with the number
- phase: the phase or building as stated ("phase one", "first 200 MW"), else empty
- status: one of {", ".join(STATUSES)}, only from the stated words, with status_text, the exact span: announced for announces, reveals, unveils, plans, proposes, will build; applied for applied, filed, submitted an application, requested a permit or right-of-way, sought approval (an application is not a permit); permitted for approved, permitted, granted, rezoned, cleared; under_construction for broke ground, building, under construction, construction began; operating for opened, operational, online, running, energized; cancelled for cancelled, scrapped, withdrawn, paused indefinitely. status_text is required: whenever you give a status, copy the words that state it into status_text; if you cannot copy them, leave status and status_text empty. An empty status is correct when the words do not say
- planned_year: the year the facility or phase is planned to start, as stated, with planned_year_text, the exact span
- power_source: how it will be powered, as stated (natural gas turbines, nuclear, solar and storage, grid); utility: the utility or power supplier as named; power_text: the exact span that states them
- confidence: 0 to 1, how sure you are that this is a real, specific facility and the fields are right
- evidence: one sentence (or the title) copied verbatim from the story that names the facility; story_id: the story it is from
- same_as: if this facility is already in the reference list (the same site), its id; if it is an earlier facility in this same request, that facility's key (cluster_id#n, n counting from 0 within its cluster); else empty

Return every cluster exactly once, with an empty facilities list when it names none."""

STR = {"type": "string"}
FIELDS = ["operator", "developer", "site_name", "state", "state_text", "county", "city", "location_text", "mw",
          "mw_text", "phase", "status_text", "planned_year", "planned_year_text", "power_source", "utility",
          "power_text", "evidence", "story_id", "same_as"]
SCHEMA = {
    "type": "object",
    "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "cluster_id": STR,
            "facilities": {"type": "array", "items": {
                "type": "object",
                "properties": {**{f: STR for f in FIELDS},
                               "status": {"type": "string", "enum": STATUSES + [""]},
                               "confidence": {"type": "number"}},
                "required": FIELDS + ["status", "confidence"],
                "additionalProperties": False}},
        },
        "required": ["cluster_id", "facilities"],
        "additionalProperties": False}}},
    "required": ["results"],
    "additionalProperties": False,
}


def named(value, text):
    """True when a name the model returned appears in the story's text."""
    return bool(value) and norm(value) in text


def checked_fields(d, text):
    """The facility's text fields kept only as the story states them, and the reasons for any dropped."""
    why = []
    out = {}
    for f in ("operator", "developer", "site_name", "power_source", "utility", "phase"):
        v = " ".join((d.get(f) or "").split())
        if v and not named(v, text):
            why.append(f"{f} {v!r}: not in the story")
            v = ""
        out[f] = v
    state, _, status, w = stated_words({"state": d.get("state"), "state_text": d.get("state_text"),
                                        "status": d.get("status"), "status_text": d.get("status_text")}, text)
    why += w
    out["state"], out["status"] = state, status
    span = d.get("location_text") or ""
    for f in ("county", "city"):
        v = " ".join((d.get(f) or "").split())
        if v and (not span or norm(span) not in text or norm(v) not in norm(span)):
            why.append(f"{f} {v!r}: location span {span!r} not in the story or does not name it")
            v = ""
        out[f] = v
    y = (d.get("planned_year") or "").strip()
    span = d.get("planned_year_text") or ""
    if y and (not re.fullmatch(r"20\d\d", y) or not span or norm(span) not in text or y not in span):
        why.append(f"planned_year {y!r}: span {span!r} not in the story or does not state it")
        y = ""
    out["planned_year"] = y
    return out, why


def load_places(log):
    """{(state, place key): (lat, lon, NAME)} from the Census places gazetteer (unique names only)."""
    gaz, rec, member = ep.fetch_gazetteer(PLACE_URL, log)
    by = {}
    for g in gaz.itertuples():
        key = re.sub(r" (city|town|village|cdp|borough|municipality|comunidad|zona urbana)$", "", ep.plain(g.NAME))
        by.setdefault((g.USPS, key), []).append((float(g.INTPTLAT), float(g.INTPTLONG), g.NAME, member))
    out = {}
    for k, v in by.items():
        incorporated = [x for x in v if not x[2].endswith(" CDP")]
        pick = incorporated if len(incorporated) == 1 else (v if len(v) == 1 else [])
        if pick:
            out[k] = pick[0]
    return out, member


def locate(row, counties, places):
    """(lat, lon, precision, note) for one facility, from its stated state and county or city."""
    if not row["state"]:
        return "", "", "none", "no US state stated"
    if row["county"]:
        a, b, p, n = ep.geocode(row["state"], row["county"], counties)
        if a is not None:
            return f"{a:.6f}", f"{b:.6f}", p, n
    if row["city"]:
        hit = places.get((row["state"], ep.plain(row["city"])))
        if hit:
            return f"{hit[0]:.6f}", f"{hit[1]:.6f}", "place", f"place {hit[2]} ({hit[3]})"
        return "", "", "none", f"city {row['city']!r} not a unique place in the gazetteer for {row['state']}"
    return "", "", "none", "no county or city stated"


def read_table(path, cols):
    if not os.path.exists(path):
        return pd.DataFrame(columns=cols)
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def facility_id(first_story, n):
    return "datacenter:" + hashlib.sha1(f"{first_story}#{n}".encode()).hexdigest()[:16]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW datacenter facility extraction")
    ap.add_argument("--max-calls", type=int, default=30)
    ap.add_argument("--reextract", action="store_true",
                    help="rebuild both tables from every story already checked (session 17); the earlier tables "
                         "are copied to warehouse/datacenters/history/ first")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"datacenters_extract_{run_id}.log"))
    status = dict(table=TABLE, market="extract", status="ok", detail="")
    try:
        key = ip.load_key("ANTHROPIC_API_KEY", log)
        if key is None:
            raise RuntimeError("ANTHROPIC_API_KEY is empty")
        news = ip.read_series(os.path.join(ip.OUT_DIR, NEWS + ".csv"), NEWS_COLS)
        checked = (pd.read_csv(CHECKED, dtype=str, keep_default_na=False) if os.path.exists(CHECKED)
                   else pd.DataFrame(columns=CHECKED_COLS))
        if args.reextract:
            # the same stories as before, from nothing: copy the earlier tables aside, then start empty
            hist = os.path.join(HERE, "history")
            os.makedirs(hist, exist_ok=True)
            for t in (TABLE, EVIDENCE):
                src = os.path.join(ip.OUT_DIR, t + ".csv")
                if os.path.exists(src):
                    dst = os.path.join(hist, f"{t}_before_{run_id}.csv")
                    shutil.copyfile(src, dst)
                    os.remove(src)
                    log(f"re-extract: {t} copied to {os.path.relpath(dst, ROOT)}; the table is rebuilt")
            checked = checked[~checked["story_id"].isin(set(news["event_id"]))]
        table = read_table(os.path.join(ip.OUT_DIR, TABLE + ".csv"), COLS)
        elig = news[(news["scored_at"] != "") & news["sector"].isin(SECTORS_IN)]
        todo = elig[~elig["event_id"].isin(set(checked["story_id"]))]
        log(f"ERW datacenters extract {run_id}: {len(news)} stories, {len(elig)} eligible, {len(todo)} not yet "
            f"checked; {len(table)} facilities already in the table")
        if todo.empty:
            log("nothing to do")
            ip.write_status("datacenters", run_id, [status])
            log.close()
            print("datacenters extract: no new eligible stories")
            return 0
        # the gazetteers first: if they cannot be read, stop before spending on the model
        counties, got = ep.load_gazetteer(run_id, log)
        places, place_member = load_places(log)
        client = llm.client("datacenters_extract", log, api_key=key)
        model = pick_model(client, log)
        clusters = [g for _, g in todo.sort_values("event_date").groupby("cluster_id", sort=False)]
        clusters.sort(key=lambda g: g["event_date"].min())
        batches = [clusters[i:i + BATCH] for i in range(0, len(clusters), BATCH)][:args.max_calls]
        log(f"{len(clusters)} clusters in {len(batches)} calls (at most {BATCH} per call)")
        news_by_id = news.set_index("event_id")
        by_id = {r["entity_id"]: dict(r) for r in table.to_dict("records")}
        new_evidence, new_checked, usage, failed_calls, dropped = [], [], [], 0, []
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for bi, batch in enumerate(batches, 1):
            items = [{"cluster_id": g["cluster_id"].iloc[0],
                      "stories": [{"story_id": r.event_id, "published": r.event_date, "outlet": r.source,
                                   "title": r.title, "summary": r.summary} for r in g.itertuples()]} for g in batch]
            ref = sorted(by_id.values(), key=lambda d: d["first_story_at"])[-REFERENCE_MAX:]
            ref_lines = [f"{d['entity_id']} | operator {d['operator'] or '-'} | developer {d['developer'] or '-'} | "
                         f"site {d['site_name'] or '-'} | {d['city'] or d['county'] or '-'}, {d['state'] or '-'} | "
                         f"{d['mw'] or '-'} MW" for d in ref]
            user = ("Reference list of facilities already extracted (id | operator | developer | site | place | MW), "
                    "candidates for same_as:\n" + ("\n".join(ref_lines) if ref_lines else "(none)")
                    + "\n\nClusters (JSON):\n" + json.dumps(items, ensure_ascii=False))
            try:
                resp = client.messages.create(
                    model=model, max_tokens=16000,
                    system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
                    output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                    messages=[{"role": "user", "content": user}])
                u = resp.usage
                usage.append(dict(input=u.input_tokens, output=u.output_tokens,
                                  cache_write=u.cache_creation_input_tokens or 0,
                                  cache_read=u.cache_read_input_tokens or 0))
                if resp.stop_reason != "end_turn":
                    raise RuntimeError(f"stop_reason {resp.stop_reason}")
                results = {r["cluster_id"]: r for r in
                           json.loads("".join(b.text for b in resp.content if b.type == "text"))["results"]}
            except Exception as exc:
                failed_calls += 1
                log(f"  call {bi} FAILED ({len(batch)} clusters left unchecked): {ip.redact(repr(exc))[:300]}")
                continue
            keys = {}
            n_new = n_merged = 0
            for g in batch:
                cid = g["cluster_id"].iloc[0]
                if cid not in results:
                    log(f"  call {bi}: cluster {cid} missing from the answer; its stories stay unchecked")
                    continue
                story_ids = list(g["event_id"])
                text = norm(" ".join(g["title"]) + " " + " ".join(g["summary"]))
                facs = results[cid]["facilities"]
                for n, d in enumerate(facs):
                    d = {k: (None if v == "" else v) for k, v in d.items()}
                    mw = None
                    if d.get("mw") is not None:
                        try:
                            mw = float(str(d["mw"]).replace(",", "").strip())
                        except ValueError:
                            dropped.append(f"{cid}: mw {d['mw']!r} is not a number, not kept")
                    mw, why = verified("mw", mw, d.get("mw_text"), text)
                    if why:
                        dropped.append(f"{cid}: {why}")
                    vals, why = checked_fields(d, text)
                    dropped.extend(f"{cid}: {w}" for w in why)
                    ev = d.get("evidence") or ""
                    if norm(ev) not in text:
                        dropped.append(f"{cid}: evidence not verbatim in the story, not kept: {ev[:100]!r}")
                        ev = ""
                    src_story = d.get("story_id") if d.get("story_id") in story_ids else story_ids[0]
                    same = d.get("same_as")
                    target = same if same in by_id else keys.get(same) if same else None
                    here = news_by_id.loc[story_ids].sort_values("event_date")
                    if target:
                        row = by_id[target]
                        ids = [x for x in row["story_ids"].split(";") if x]
                        urls = [x for x in row["story_urls"].split(";") if x]
                        for sid in here.index:
                            if sid not in ids:
                                ids.append(sid)
                                urls.append(here.loc[sid, "source_url"])
                        row.update(story_ids=";".join(ids), story_urls=";".join(urls), n_stories=str(len(ids)))
                        for f in ("developer", "site_name", "state", "county", "city", "phase", "planned_year",
                                  "power_source", "utility"):
                            if not row.get(f) and vals[f]:
                                row[f] = vals[f]
                        if not row.get("operator") and vals["operator"]:
                            row["operator"] = vals["operator"]
                        if not row.get("mw") and mw is not None:
                            row["mw"] = row["capacity_mw"] = clean(mw)
                        if not row.get("project_status") and vals["status"]:
                            row["project_status"] = vals["status"]
                            row["status"] = STD_STATUS[vals["status"]]
                        n_merged += 1
                        did = target
                    else:
                        first = here.iloc[0]
                        did = facility_id(first.name, n)
                        by_id[did] = {
                            "entity_id": did, "entity_type": "datacenter", "name": vals["site_name"],
                            "geo": "", "lat": "", "lon": "", "capacity_mw": clean(mw),
                            "status": STD_STATUS.get(vals["status"], ""), "status_date": "",
                            "operator": vals["operator"], "source": first["source"], "source_url": first["source_url"],
                            "retrieved_at": now, "vintage": "", "kind": "datacenter",
                            "developer": vals["developer"], "site_name": vals["site_name"], "state": vals["state"],
                            "county": vals["county"], "city": vals["city"], "mw": clean(mw), "phase": vals["phase"],
                            "project_status": vals["status"], "planned_year": vals["planned_year"],
                            "power_source": vals["power_source"], "utility": vals["utility"], "ai_power": "true",
                            "confidence": clean(round(max(0.0, min(1.0, float(d.get("confidence") or 0))), 2)),
                            "geo_precision": "", "geo_note": "", "first_story_at": first["event_date"],
                            "n_stories": str(len(here)), "story_ids": ";".join(here.index),
                            "story_urls": ";".join(here["source_url"]), "model_id": model, "extracted_at": now}
                        n_new += 1
                    keys[f"{cid}#{n}"] = did
                    if ev:
                        s = news_by_id.loc[src_story]
                        new_evidence.append({"event_id": f"{did}|{src_story}", "event_date": s["event_date"],
                                             "event_type": "datacenter_evidence", "parties": "", "entity_ids": did,
                                             "mw": "", "price": "", "currency": "", "status": "",
                                             "source": s["source"], "source_url": s["source_url"],
                                             "facility_id": did, "story_id": src_story, "evidence": " ".join(ev.split())})
                for sid in story_ids:
                    new_checked.append({"story_id": sid, "cluster_id": cid, "checked_at": now, "model_id": model,
                                        "n_facilities": str(len(facs))})
            u = usage[-1]
            log(f"  call {bi}: {len(batch)} clusters, {n_new} new facilities, {n_merged} merged; tokens in "
                f"{u['input']} out {u['output']} cache read {u['cache_read']}; request {resp._request_id}")

        for d in dropped:
            log(f"  not kept: {d}")
        # place every facility (a merge may have added a county or city)
        for row in by_id.values():
            row["lat"], row["lon"], row["geo_precision"], row["geo_note"] = locate(row, counties, places)
            row["geo"] = f"US-{row['state']}" if row["state"] else ""
        out = pd.DataFrame(list(by_id.values()), columns=COLS).fillna("")
        common = [f"Retrieved: {run_id} (UTC) by warehouse/datacenters/extract.py from warehouse/output/{NEWS}.csv",
                  f"Run log: warehouse/output/logs/datacenters_extract_{run_id}.log"]
        if len(out):
            ip.write_snapshot(out.sort_values("entity_id").reset_index(drop=True), TABLE, [
                "Energy Research Warehouse (ERW): Datacenter facilities extracted from scored news stories "
                "(the datacenter power tracker, platform tool 4)",
                "Shape: entities (docs/datastandard.md), entity_type datacenter; the whole table is rewritten each "
                "run from the facilities already extracted and the new stories. capacity_mw = mw, as stated.",
                *common,
                f"Model: {model}, JSON schema output. Every value was checked against the story's title or summary "
                "and kept only as stated (session 16 ruling); mw only if its span parses to the same value.",
                "Columns: status is the entities vocabulary (announced and permitted -> planned, cancelled -> "
                "withdrawn); project_status is the extractor's word. ai_power is true on every row (the AI and "
                "datacenter power subset). geo_precision: county or place (the Census gazetteer's internal point "
                f"of the stated county or city; {got[0][0]}, {place_member}, kept in "
                f"warehouse/raw/census_gazetteer/{run_id}/), or none.",
                "License: public. The model's checked fields and the story links only, no outlet text; the evidence "
                f"sentences are in the internal table {EVIDENCE}.",
                "Sources: the outlet named in each row's source column (the first story); story_urls lists every story.",
            ], log, COLS)
        if new_evidence:
            ip.write_csv(pd.DataFrame(new_evidence, columns=EVIDENCE_COLS), EVIDENCE, [
                "Energy Research Warehouse (ERW): Evidence sentences for datacenter_projects, copied verbatim from the stories",
                "Shape: events (docs/datastandard.md v0), event_type datacenter_evidence; one row per facility and "
                "story. event_date is the story's publish time.",
                *common,
                "License: internal. Outlet text (a sentence of the story's title or summary); never shown publicly.",
                "Sources: the outlet named in each row's source column; source_url links the story.",
            ], log, cols=EVIDENCE_COLS, key=["event_id"], time_col="event_date")
        if new_checked:
            chk = pd.concat([checked, pd.DataFrame(new_checked, columns=CHECKED_COLS)], ignore_index=True)
            chk.drop_duplicates("story_id", keep="last").sort_values("story_id").to_csv(
                CHECKED, index=False, lineterminator="\n")
        reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
        srcs = set(out["source"]) | {e["source"] for e in new_evidence}
        entries = [dict(r, tables=[t for t in r["tables"].split(";") if t] + [TABLE, EVIDENCE])
                   for r in reg[reg["source"].isin(srcs)].to_dict("records")]
        entries += [dict(source=ep.GAZ_SOURCE, publisher="U.S. Census Bureau",
                         report="Gazetteer Files, counties (2025) and places (2025), internal points",
                         report_url=ep.GAZ_URL, document_list=ep.GAZ_PAGE, license="public", tables=[TABLE])]
        ip.update_sources(entries)
        tin = sum(x["input"] for x in usage)
        tout = sum(x["output"] for x in usage)
        cw = sum(x["cache_write"] for x in usage)
        cr = sum(x["cache_read"] for x in usage)
        if model in PRICES:
            pi, po = PRICES[model]
            cost = f"USD {(tin * pi + cw * pi * 1.25 + cr * pi * 0.1 + tout * po) / 1e6:.4f}"
        else:
            cost = "unknown (model not in PRICES)"
        summary = (f"model {model}; calls {len(usage)} ({failed_calls} failed); stories checked {len(new_checked)}; "
                   f"facilities in table {len(out)}; evidence rows {len(new_evidence)}; fields not kept {len(dropped)}; "
                   f"tokens in {tin} out {tout} cache write {cw} cache read {cr}; cost {cost}")
        log(summary)
        print(f"datacenters extract: {summary}")
        status["detail"] = summary[:300]
        if failed_calls and not usage:
            raise RuntimeError(f"all {failed_calls} calls failed")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"datacenters extract FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
        ip.write_status("datacenters", run_id, [status])
        log.close()
        return 1
    ip.write_status("datacenters", run_id, [status])
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
