#!/usr/bin/env python3
"""Extract energy deals from scored news stories: the deal tracker's data (platform tool 6).

Energy Research Warehouse (ERW), session 15.

    python warehouse/deals/extract.py                 # every eligible story not yet checked
    python warehouse/deals/extract.py --max-calls 5   # a trial

Eligible stories: rows of warehouse/output/news_stories.csv that are scored, with
sector deal, ppa, capital, nuclear, generation, datacenter_power, lng, oil or gas
and significance 5 or more. Stories are sent by cluster (score.py's cluster_id:
stories about the same event), in batches, to the newest Sonnet-class model in
the API's models list, with a JSON schema. For each cluster the model says whether
the stories report a specific transaction and, if so, extracts each deal:
deal_type, buyer, seller, other_parties, asset, technology, state, country, mw,
mwh, dollars, price (value and unit as stated), term_years, status,
announced_date, ai_power, confidence, and the evidence sentence.

No number is inferred. The model returns, for every number, the exact span of the
title or summary it read it from (mw_text, dollars_text, ...). The number is kept
only if that span is in the story's own title or summary and parses to the same
value (unit words such as GW, bn and million are applied); otherwise it becomes
null and the run log says so. The evidence sentence must also be in the story.

Deduplication: each call carries a reference list of deals already extracted, and
the model marks a deal that is one of them (same_as); its story links are added to
that deal instead of making a new one. Deals in the same call can point to an
earlier deal of that call.

Outputs (the events shape, docs/datastandard.md):
  warehouse/output/energy_deals.csv            license public: the model's structured
      fields and the story links, no outlet text; event_type deal
  warehouse/output/energy_deals_evidence.csv   license internal: one row per deal and
      story, with the evidence sentence (outlet text)
  warehouse/deals/checked.csv                  every story sent, so a later run sends
      only new stories (tracked in git, like news_stories.csv)
Calls, tokens and cost are logged per call and per run; dollars use PRICES (the
claude-api skill's table, cached 2026-06-24). The key is ANTHROPIC_API_KEY.
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import traceback

import anthropic
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import iso_prices as ip  # noqa: E402
from ingest import NAME as NEWS, NEWS_COLS  # noqa: E402

DEALS = "energy_deals"
EVIDENCE = "energy_deals_evidence"
CHECKED = os.path.join(HERE, "checked.csv")
SECTORS_IN = ["deal", "ppa", "capital", "nuclear", "generation", "datacenter_power", "lng", "oil", "gas"]
MIN_SIGNIFICANCE = 5
DEAL_TYPES = ["ppa", "offtake", "m_and_a", "project_finance", "tax_equity", "debt", "equity_raise",
              "joint_venture", "lease", "behind_the_meter", "nuclear_restart", "smr", "fuel_supply", "other"]
STATUSES = ["announced", "signed", "closed", "cancelled", "rumored"]
PRICES = {"claude-sonnet-5": (2.00, 10.00), "claude-sonnet-4-6": (3.00, 15.00)}
BATCH = 12          # clusters per call
REFERENCE_MAX = 250  # earlier deals offered as same_as candidates

DEAL_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency",
             "status", "source", "source_url",
             "deal_type", "buyer", "seller", "other_parties", "asset", "technology", "state", "country",
             "mwh", "dollars", "price_value", "price_unit", "term_years", "announced_date", "date_basis",
             "ai_power", "confidence", "n_stories", "story_ids", "story_urls", "model_id", "extracted_at"]
EVIDENCE_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency",
                 "status", "source", "source_url", "deal_id", "story_id", "evidence"]
CHECKED_COLS = ["story_id", "cluster_id", "checked_at", "model_id", "n_deals"]

SYSTEM = f"""You extract energy transactions from news stories for the Energy Research Warehouse (ERW), the live, citable record of the US energy system.

Each item is one cluster: one or more stories (title and summary) about the same event. Decide whether the stories report a specific transaction: a named deal between named parties (a power purchase agreement, an offtake, an acquisition or merger, project finance, tax equity, debt, an equity raise, a joint venture, a lease, a behind-the-meter supply deal, a nuclear restart deal, a small modular reactor deal, a fuel supply contract). Market commentary, policy, earnings, forecasts, generic plans and prices are not transactions: return no deals for them.

For each transaction, return:
- deal_type: one of {", ".join(DEAL_TYPES)}
- buyer, seller: the parties as the story names them (the offtaker or acquirer is the buyer; in an equity raise, debt or project finance, the company raising the money is the seller and the investors or lenders are the buyer); empty when not named
- other_parties: any other named parties (lenders, partners, advisers named as parties)
- asset: the project, plant, company or asset traded, as named; technology: the generation or asset technology (solar, wind, gas, nuclear, storage, LNG, oil, ...) when stated
- state (US two-letter code) and country, when the story states the location
- mw, mwh, dollars (US dollars, as a number), price_value with price_unit exactly as stated (for example 50 and "USD/MWh"), term_years
- for every number, the exact text span you read it from, copied character for character from the title or summary (mw_text, mwh_text, dollars_text, price_text, term_text)
- status: one of {", ".join(STATUSES)}
- announced_date: YYYY-MM-DD only if the story states the date of the deal, else empty
- ai_power: true only if the load or offtake serves datacenters or AI
- confidence: 0 to 1, how sure you are that this is a real, specific transaction and the fields are right
- evidence: one sentence (or the title) copied verbatim from the story that shows the transaction; story_id: the story it is from
- same_as: if this deal is already in the reference list, its id; if it is an earlier deal in this same request, that deal's key (cluster_id#n, n counting from 0 within its cluster); else empty

Use an empty string for every field that is not stated. Never infer, estimate or convert a number the title or summary does not state: an empty string is the correct answer. Write numbers as plain digits in the unit named (mw in MW, dollars in US dollars), with no commas or words. Do not convert other currencies to dollars. Copy names as written. Return every cluster exactly once, with an empty deals list when it reports no transaction."""

# Optional fields are strings, with "" for "not stated": the API caps how many nullable
# (union-typed) fields a schema may have. Numbers come back as their digits and are parsed.
NUM = {"type": "string"}
STR = {"type": "string"}
SCHEMA = {
    "type": "object",
    "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "cluster_id": {"type": "string"},
            "deals": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "deal_type": {"type": "string", "enum": DEAL_TYPES},
                    "buyer": STR, "seller": STR,
                    "other_parties": {"type": "array", "items": {"type": "string"}},
                    "asset": STR, "technology": STR, "state": STR, "country": STR,
                    "mw": NUM, "mw_text": STR, "mwh": NUM, "mwh_text": STR,
                    "dollars": NUM, "dollars_text": STR,
                    "price_value": NUM, "price_unit": STR, "price_text": STR,
                    "term_years": NUM, "term_text": STR,
                    "status": {"type": "string", "enum": STATUSES},
                    "announced_date": STR,
                    "ai_power": {"type": "boolean"},
                    "confidence": {"type": "number"},
                    "evidence": {"type": "string"},
                    "story_id": {"type": "string"},
                    "same_as": STR,
                },
                "required": ["deal_type", "buyer", "seller", "other_parties", "asset", "technology", "state",
                             "country", "mw", "mw_text", "mwh", "mwh_text", "dollars", "dollars_text",
                             "price_value", "price_unit", "price_text", "term_years", "term_text", "status",
                             "announced_date", "ai_power", "confidence", "evidence", "story_id", "same_as"],
                "additionalProperties": False}},
        },
        "required": ["cluster_id", "deals"],
        "additionalProperties": False}}},
    "required": ["results"],
    "additionalProperties": False,
}


# ------------------------------------------------------------------ number checks

def norm(s):
    return " ".join(str(s).replace("’", "'").replace(" ", " ").split()).lower()


# a unit word, not glued to other letters ("3.2bn" and "230MW" match; "bond" and "mwh" do not)
def _w(words):
    return r"(?<![a-z])(?:" + words + r")(?![a-z])"


SCALE = {
    "mw": [(_w(r"gw|gigawatts?"), 1000.0), (_w(r"mw|megawatts?"), 1.0), (_w(r"kw|kilowatts?"), 0.001)],
    "mwh": [(_w(r"twh|terawatt.hours?"), 1e6), (_w(r"gwh|gigawatt.hours?"), 1000.0),
            (_w(r"mwh|megawatt.hours?"), 1.0), (_w(r"kwh|kilowatt.hours?"), 0.001)],
    "dollars": [(_w(r"trillion|tn|t"), 1e12), (_w(r"billion|bn|b|bln"), 1e9),
                (_w(r"million|mn|m|mln|mm"), 1e6), (_w(r"thousand|k"), 1e3)],
}
FOREIGN = re.compile(r"€|£|¥|\beur\b|\beuros?\b|\bgbp\b|\byen\b|\bjpy\b|\bc\$|\bcad\b|\baud\b|\ba\$|\binr\b|\brupees?\b|\byuan\b|\brmb\b|\bcny\b|\bkrw\b")


def span_numbers(span):
    return [float(m.replace(",", "")) for m in re.findall(r"\d[\d,]*(?:\.\d+)?", span)]


def verified(field, value, span, text):
    """(value or None, reason) for one extracted number."""
    if value is None:
        return None, None
    if not span:
        return None, f"{field} {value}: no source span"
    if norm(span) not in text:
        return None, f"{field} {value}: span {span!r} not in the story"
    nums = span_numbers(span)
    if not nums:
        return None, f"{field} {value}: no number in span {span!r}"
    s = norm(span)
    if field == "dollars" and FOREIGN.search(s):
        return None, f"dollars {value}: span {span!r} is not in US dollars"
    scales = [1.0]
    if field in SCALE:
        found = [m for pat, m in SCALE[field] if re.search(pat, s)]
        scales = found or [1.0]
    if field == "term_years" and re.search(r"month", s):
        return None, f"term_years {value}: span {span!r} is in months"
    for n in nums:
        for m in scales:
            # the stated number with its unit applied, nothing looser
            if math.isclose(n * m, float(value), rel_tol=1e-9, abs_tol=1e-9):
                return float(value), None
    return None, f"{field} {value}: does not match span {span!r}"


# ------------------------------------------------------------------ helpers

def pick_model(client, log):
    models = list(client.models.list())
    sonnets = [m for m in models if "sonnet" in m.id.lower()]
    if not sonnets:
        raise RuntimeError("the models list has no Sonnet-class model")
    best = max(sonnets, key=lambda m: m.created_at)
    log(f"chosen model: {best.id} (newest Sonnet-class by created_at)")
    return best.id


def read_or_empty(path, cols):
    if os.path.exists(path):
        return ip.read_series(path, cols)
    return pd.DataFrame(columns=cols)


def deal_id(first_story, n):
    return "deal:" + hashlib.sha1(f"{first_story}#{n}".encode()).hexdigest()[:16]


def clean(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.6g}" if not float(v).is_integer() else str(int(v))
    return " ".join(str(v).split())


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW deal extraction")
    ap.add_argument("--max-calls", type=int, default=60, help="at most this many model calls")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"deals_extract_{run_id}.log"))
    status = dict(table=DEALS, market="extract", status="ok", detail="")
    try:
        key = ip.load_key("ANTHROPIC_API_KEY", log)
        if key is None:
            raise RuntimeError("ANTHROPIC_API_KEY is empty")
        news = ip.read_series(os.path.join(ip.OUT_DIR, NEWS + ".csv"), NEWS_COLS)
        checked = (pd.read_csv(CHECKED, dtype=str, keep_default_na=False) if os.path.exists(CHECKED)
                   else pd.DataFrame(columns=CHECKED_COLS))
        deals = read_or_empty(os.path.join(ip.OUT_DIR, DEALS + ".csv"), DEAL_COLS)
        evid = read_or_empty(os.path.join(ip.OUT_DIR, EVIDENCE + ".csv"), EVIDENCE_COLS)
        sig = pd.to_numeric(news["significance"], errors="coerce")
        elig = news[(news["scored_at"] != "") & news["sector"].isin(SECTORS_IN) & (sig >= MIN_SIGNIFICANCE)]
        todo = elig[~elig["event_id"].isin(set(checked["story_id"]))]
        log(f"ERW deals extract {run_id}: {len(news)} stories, {len(elig)} eligible, {len(todo)} not yet checked; "
            f"{len(deals)} deals already in the table")
        if todo.empty:
            log("nothing to do")
            ip.write_status("deals", run_id, [status])
            log.close()
            print("deals extract: no new eligible stories")
            return 0
        client = anthropic.Anthropic(api_key=key)
        model = pick_model(client, log)
        clusters = [g for _, g in todo.sort_values("event_date").groupby("cluster_id", sort=False)]
        clusters.sort(key=lambda g: g["event_date"].min())
        batches = [clusters[i:i + BATCH] for i in range(0, len(clusters), BATCH)][:args.max_calls]
        log(f"{len(clusters)} clusters in {len(batches)} calls (at most {BATCH} per call)")
        news_by_id = news.set_index("event_id")
        by_id = {r["event_id"]: dict(r) for r in deals.to_dict("records")}   # deal_id -> row
        new_evidence, new_checked, usage, failed_calls, dropped = [], [], [], 0, []
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for bi, batch in enumerate(batches, 1):
            items = []
            for g in batch:
                items.append({"cluster_id": g["cluster_id"].iloc[0],
                              "stories": [{"story_id": r.event_id, "published": r.event_date, "outlet": r.source,
                                           "title": r.title, "summary": r.summary} for r in g.itertuples()]})
            ref = sorted(by_id.values(), key=lambda d: d["event_date"])[-REFERENCE_MAX:]
            ref_lines = [f"{d['event_id']} | {d['deal_type']} | buyer {d['buyer'] or '-'} | seller {d['seller'] or '-'} | "
                         f"{d['asset'] or '-'} | {d['event_date'][:10]}" for d in ref]
            user = ("Reference list of deals already extracted (id | type | buyer | seller | asset | date), "
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
                text = "".join(b.text for b in resp.content if b.type == "text")
                results = {r["cluster_id"]: r for r in json.loads(text)["results"]}
            except Exception as exc:
                failed_calls += 1
                log(f"  call {bi} FAILED ({len(batch)} clusters left unchecked): {ip.redact(repr(exc))[:300]}")
                continue
            keys = {}   # cluster_id#n -> deal_id, within this call
            n_new = n_merged = 0
            for g in batch:
                cid = g["cluster_id"].iloc[0]
                story_ids = list(g["event_id"])
                text = norm(" ".join(g["title"]) + " " + " ".join(g["summary"]))
                out = results.get(cid, {"deals": []})
                if cid not in results:
                    log(f"  call {bi}: cluster {cid} missing from the answer; its stories stay unchecked")
                    continue
                for n, d in enumerate(out["deals"]):
                    d = {k: (None if v == "" else v) for k, v in d.items()}
                    for f in ("mw", "mwh", "dollars", "price_value", "term_years"):
                        if d.get(f) is not None:
                            try:
                                d[f] = float(str(d[f]).replace(",", "").replace("$", "").strip())
                            except ValueError:
                                dropped.append(f"{cid}: {f} {d[f]!r} is not a number, not kept")
                                d[f] = None
                    vals = {}
                    for f in ("mw", "mwh", "dollars", "price_value", "term_years"):
                        span = d.get({"price_value": "price_text", "term_years": "term_text"}.get(f, f + "_text"))
                        v, why = verified(f, d.get(f), span, text)
                        vals[f] = v
                        if why:
                            dropped.append(f"{cid}: {why}")
                    ev = d.get("evidence") or ""
                    if norm(ev) not in text:
                        dropped.append(f"{cid}: evidence not verbatim in the story, not kept: {ev[:100]!r}")
                        ev = ""
                    src_story = d.get("story_id") if d.get("story_id") in story_ids else story_ids[0]
                    target = None
                    same = d.get("same_as")
                    if same and same in by_id:
                        target = same
                    elif same and same in keys:
                        target = keys[same]
                    stories_here = news_by_id.loc[story_ids]
                    if target:   # add this cluster's stories to the existing deal
                        row = by_id[target]
                        ids = [x for x in row["story_ids"].split(";") if x]
                        urls = [x for x in row["story_urls"].split(";") if x]
                        for sid in story_ids:
                            if sid not in ids:
                                ids.append(sid)
                                urls.append(news_by_id.loc[sid, "source_url"])
                        row.update(story_ids=";".join(ids), story_urls=";".join(urls), n_stories=str(len(ids)))
                        for f in ("mw", "mwh", "dollars", "price_value", "term_years"):   # fill a gap only
                            if row.get(f, "") == "" and vals[f] is not None:
                                row[f] = clean(vals[f])
                        n_merged += 1
                        did = target
                    else:
                        first = stories_here.sort_values("event_date").iloc[0]
                        did = deal_id(first.name, n)
                        ad = d.get("announced_date") or ""
                        if ad and not re.match(r"^\d{4}-\d{2}-\d{2}$", ad):
                            dropped.append(f"{cid}: announced_date {ad!r} not YYYY-MM-DD, not kept")
                            ad = ""
                        parties = [p for p in [d.get("buyer"), d.get("seller")] + list(d.get("other_parties") or []) if p]
                        pu = (d.get("price_unit") or "").strip()
                        per_mwh_usd = vals["price_value"] is not None and re.fullmatch(r"(?i)(usd|\$|us\$)\s*/\s*mwh", pu)
                        by_id[did] = {
                            "event_id": did, "event_date": ad or first["event_date"], "event_type": "deal",
                            "parties": ";".join(clean(p) for p in parties), "entity_ids": "",
                            "mw": clean(vals["mw"]), "price": clean(vals["price_value"]) if per_mwh_usd else "",
                            "currency": "USD" if per_mwh_usd else "", "status": d["status"],
                            "source": first["source"], "source_url": first["source_url"],
                            "deal_type": d["deal_type"], "buyer": clean(d.get("buyer")), "seller": clean(d.get("seller")),
                            "other_parties": ";".join(clean(p) for p in d.get("other_parties") or []),
                            "asset": clean(d.get("asset")), "technology": clean(d.get("technology")),
                            "state": clean(d.get("state")).upper()[:2] if d.get("state") else "",
                            "country": clean(d.get("country")),
                            "mwh": clean(vals["mwh"]), "dollars": clean(vals["dollars"]),
                            "price_value": clean(vals["price_value"]),
                            "price_unit": pu if vals["price_value"] is not None else "",
                            "term_years": clean(vals["term_years"]),
                            "announced_date": ad, "date_basis": "stated" if ad else "first_story_published",
                            "ai_power": "true" if d.get("ai_power") else "false",
                            "confidence": clean(round(max(0.0, min(1.0, float(d.get("confidence") or 0))), 2)),
                            "n_stories": str(len(story_ids)), "story_ids": ";".join(stories_here.sort_values("event_date").index),
                            "story_urls": ";".join(stories_here.sort_values("event_date")["source_url"]),
                            "model_id": model, "extracted_at": now}
                        n_new += 1
                    keys[f"{cid}#{n}"] = did
                    if ev:
                        s = news_by_id.loc[src_story]
                        new_evidence.append({"event_id": f"{did}|{src_story}", "event_date": s["event_date"],
                                             "event_type": "deal_evidence", "parties": "", "entity_ids": "",
                                             "mw": "", "price": "", "currency": "", "status": "",
                                             "source": s["source"], "source_url": s["source_url"],
                                             "deal_id": did, "story_id": src_story, "evidence": " ".join(ev.split())})
                for sid in story_ids:
                    new_checked.append({"story_id": sid, "cluster_id": cid, "checked_at": now, "model_id": model,
                                        "n_deals": str(len(out["deals"]))})
            u = usage[-1]
            log(f"  call {bi}: {len(batch)} clusters, {n_new} new deals, {n_merged} merged into earlier deals; "
                f"tokens in {u['input']} out {u['output']} cache read {u['cache_read']}; request {resp._request_id}")

        for d in dropped:
            log(f"  not kept: {d}")
        header_common = [f"Retrieved: {run_id} (UTC) by warehouse/deals/extract.py from warehouse/output/{NEWS}.csv",
                         f"Run log: warehouse/output/logs/deals_extract_{run_id}.log"]
        out_deals = pd.DataFrame(list(by_id.values()), columns=DEAL_COLS).fillna("")
        if len(out_deals):
            ip.write_csv(out_deals, DEALS, [
                "Energy Research Warehouse (ERW): Energy deals extracted from scored news stories (platform tool 6)",
                "Shape: events (docs/datastandard.md v0), event_type deal. event_date is the announced date when the "
                "story states it (date_basis stated), else the first story's publish time (first_story_published).",
                *header_common,
                f"Model: {model}, JSON schema output; every number was checked against a span of the story's title or "
                "summary and kept only if the span is there and parses to the same value (warehouse/deals/extract.py).",
                "Columns: mw, mwh, dollars (US dollars) and term_years as stated; price and currency only for a price stated "
                "in USD/MWh, otherwise price_value with price_unit as stated. parties is buyer;seller;other_parties.",
                "License: public. The model's structured fields and the story links only, no outlet text; the evidence "
                f"sentences are in the internal table {EVIDENCE}.",
                "Sources: the outlet named in each row's source column (the first story); story_urls lists every story.",
            ], log, cols=DEAL_COLS, key=["event_id"], time_col="event_date")
        if new_evidence:
            ip.write_csv(pd.DataFrame(new_evidence, columns=EVIDENCE_COLS), EVIDENCE, [
                "Energy Research Warehouse (ERW): Evidence sentences for energy_deals, copied verbatim from the stories",
                "Shape: events (docs/datastandard.md v0), event_type deal_evidence; one row per deal and story. "
                "event_date is the story's publish time.",
                *header_common,
                "License: internal. Outlet text (a sentence of the story's title or summary); never shown publicly.",
                "Sources: the outlet named in each row's source column; source_url links the story.",
            ], log, cols=EVIDENCE_COLS, key=["event_id"], time_col="event_date")
        if new_checked:
            chk = pd.concat([checked, pd.DataFrame(new_checked, columns=CHECKED_COLS)], ignore_index=True)
            chk = chk.drop_duplicates("story_id", keep="last").sort_values("story_id")
            chk.to_csv(CHECKED, index=False, lineterminator="\n")
        # the outlets feed these tables too (license internal for their text; energy_deals is public
        # by its header, as news_index is)
        reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
        srcs = set(out_deals["source"]) | {e["source"] for e in new_evidence}
        entries = [dict(r, tables=[t for t in r["tables"].split(";") if t] + [DEALS, EVIDENCE])
                   for r in reg[reg["source"].isin(srcs)].to_dict("records")]
        if entries:
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
                   f"deals in table {len(out_deals)}; evidence rows {len(new_evidence)}; numbers or fields not kept "
                   f"{len(dropped)}; tokens in {tin} out {tout} cache write {cw} cache read {cr}; cost {cost}")
        log(summary)
        print(f"deals extract: {summary}")
        status["detail"] = summary[:300]
        if failed_calls and not usage:
            raise RuntimeError(f"all {failed_calls} calls failed")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"deals extract FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
        ip.write_status("deals", run_id, [status])
        log.close()
        return 1
    ip.write_status("deals", run_id, [status])
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
