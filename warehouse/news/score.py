#!/usr/bin/env python3
"""Score and cluster ERW news stories with the Claude API.

Energy Research Warehouse (ERW). For every unscored story in
warehouse/output/news_stories.csv published in the last N days, asks a
Sonnet-class Claude model for a JSON object per story (significance,
ai_power_relevance, sector, region, mw_mentioned, price_mentioned, parties,
one_line_why, is_duplicate_of) under the rubric in warehouse/news/rubric.md,
which is placed verbatim in the system prompt. Writes the scores into the same
rows through the shared merge writer, and clusters stories that share an
is_duplicate_of chain.

    python warehouse/news/score.py              # unscored stories from the last 3 days
    python warehouse/news/score.py --days 2 --max-calls 24

Model: chosen at run time from the API's models list (the newest model whose
id contains "sonnet"); never hardcoded. Recorded in the run log and per row.
Temperature 0 is requested; if the chosen model rejects sampling parameters
(Claude Sonnet 5 does, with HTTP 400), the run logs that and continues without
it, relying on the JSON schema for consistent output.
Batching: stories are split so one run makes at most --max-calls calls.
Cost: token usage is logged per call and per run; dollars use the per-token
prices in PRICES, from the claude-api skill's model table (cached 2026-06-24).
A model not in PRICES is logged as cost unknown, never guessed.
The key comes from ANTHROPIC_API_KEY (environment or .env) and is never logged.
"""

import argparse
import datetime as dt
import json
import math
import os
import sys
import traceback

import anthropic
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
from ingest import KEY, NAME, NEWS_COLS  # noqa: E402

RUBRIC = open(os.path.join(HERE, "rubric.md"), encoding="utf-8").read().strip()
SECTORS = ["oil", "gas", "lng", "power_prices", "generation", "nuclear", "renewables", "storage",
           "transmission", "grid_conditions", "interconnection", "datacenter_power", "deal", "ppa",
           "policy", "capital", "company", "geopolitics", "transport", "hydrogen", "other"]
# USD per million tokens (input, output), from the claude-api skill model table, cached 2026-06-24
PRICES = {"claude-sonnet-5": (2.00, 10.00), "claude-sonnet-4-6": (3.00, 15.00)}
REFERENCE_MAX = 400  # earlier stories offered as is_duplicate_of candidates per call
MIN_BATCH = 25  # stories per call, unless fewer remain

SYSTEM = f"""You score energy news stories for the Energy Research Warehouse (ERW), the live, citable record of the US energy system.

Rubric (apply exactly):
{RUBRIC}

For each story in the request, return one result with:
- id: the story's id, exactly as given
- significance: integer 0 to 10, per the rubric
- ai_power_relevance: integer 0 to 10, per the rubric
- sector: exactly one of {", ".join(SECTORS)}
- region: the US state, the country, or "global"
- mw_mentioned: a capacity in MW stated in the title or summary, as a number (convert GW to MW), else null
- price_mentioned: a price or dollar amount stated in the title or summary, verbatim, else null
- parties: companies, agencies or governments named as parties to the story (may be empty)
- headline: a plain headline of at most 14 words stating what happened, no hype, no question marks
- one_line_why: under 25 words, why an energy professional should care; plain, no hype
- is_duplicate_of: the id of an EARLIER story (from the reference list, or earlier in this request) about the same event, else null

Use only what the title and summary say. Do not invent numbers or parties. The headline and one_line_why must not mention AI, artificial intelligence, datacenters, data centers or compute unless the story's own title or summary does; judge and describe the energy consequences. Return every story exactly once."""

SCHEMA = {
    "type": "object",
    "properties": {"results": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "significance": {"type": "integer"},
            "ai_power_relevance": {"type": "integer"},
            "sector": {"type": "string", "enum": SECTORS},
            "region": {"type": "string"},
            "mw_mentioned": {"anyOf": [{"type": "number"}, {"type": "null"}]},
            "price_mentioned": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "parties": {"type": "array", "items": {"type": "string"}},
            "headline": {"type": "string"},
            "one_line_why": {"type": "string"},
            "is_duplicate_of": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        },
        "required": ["id", "significance", "ai_power_relevance", "sector", "region", "mw_mentioned",
                     "price_mentioned", "parties", "headline", "one_line_why", "is_duplicate_of"],
        "additionalProperties": False}}},
    "required": ["results"],
    "additionalProperties": False,
}


def nodash(text):
    """The ERW writes no em dashes in any file (CLAUDE.md); model text is normalised."""
    return " ".join(str(text).replace("—", " - ").split()) if text else text


def pick_model(client, log):
    models = list(client.models.list())
    log(f"models list: {len(models)} models: {', '.join(m.id for m in models)}")
    sonnets = [m for m in models if "sonnet" in m.id.lower()]
    if not sonnets:
        raise RuntimeError("the models list has no Sonnet-class model")
    best = max(sonnets, key=lambda m: m.created_at)
    log(f"chosen model: {best.id} (newest Sonnet-class by created_at {best.created_at})")
    return best.id


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW news scoring")
    ap.add_argument("--days", type=int, default=3, help="score unscored stories from the last N days")
    ap.add_argument("--max-calls", type=int, default=23, help="at most this many scoring calls (plus one temperature probe, which a model may reject: 24 requests at most)")
    ap.add_argument("--limit", type=int, help="score at most N stories (trial runs)")
    ap.add_argument("--out-dir", help="read and write under this directory instead (trial runs)")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_score_{run_id}.log"))
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    status = dict(table=NAME, market="scoring", status="ok", detail="")
    try:
        key = ip.load_key("ANTHROPIC_API_KEY", log)
        if key is None:
            raise RuntimeError("ANTHROPIC_API_KEY is empty")
        df = ip.read_series(path, NEWS_COLS)
        with open(path, encoding="utf-8") as f:
            header = [ln[2:].rstrip("\n") for ln in f if ln.startswith("# ")]
        header = [h for h in header if not h.startswith(("File holds", "Scored:"))]
        client = anthropic.Anthropic(api_key=key)
        model = pick_model(client, log)
        cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=args.days)
        when = pd.to_datetime(df["event_date"], utc=True)
        todo = df[(df["scored_at"] == "") & (when >= cutoff)].copy()
        todo = todo.assign(_when=when[todo.index]).sort_values("_when")
        if args.limit:
            todo = todo.head(args.limit)
        log(f"stories: {len(df)} stored, {len(todo)} unscored since {ip.utc_iso(cutoff)} to score")
        if todo.empty:
            log("nothing to score")
            print("news score: nothing to score")
            ip.write_status("news_score", run_id, [status])
            log.close()
            return 0
        # at least MIN_BATCH stories per call: each call carries the reference list, so tiny
        # batches waste tokens (18 one-story calls cost USD 0.67 on 2026-09-25)
        size = max(math.ceil(len(todo) / args.max_calls), MIN_BATCH)
        batches = [todo.iloc[i:i + size] for i in range(0, len(todo), size)]
        log(f"batches: {len(batches)} of up to {size} stories")
        reference = df[(df["scored_at"] != "") & (when >= cutoff - pd.Timedelta(days=2))]
        ref_list = [f"{r.event_id} | {r.title[:120]}" for r in reference.sort_values("event_date").itertuples()]
        use_temperature, known = True, set(df["event_id"])
        results, usage_rows, failed_batches = {}, [], 0
        for bi, batch in enumerate(batches, 1):
            stories = [{"id": r.event_id, "published": r.event_date, "outlet": r.source,
                        "feed_beat": r.feed_sector, "title": r.title, "summary": r.summary}
                       for r in batch.itertuples()]
            refs = (ref_list + [f"{e} | {t[:120]}" for e, t in results.get("_seen", [])])[-REFERENCE_MAX:]
            user = ("Reference list of earlier stories (id | title), candidates for is_duplicate_of:\n"
                    + ("\n".join(refs) if refs else "(none)")
                    + "\n\nStories to score (JSON):\n" + json.dumps(stories, ensure_ascii=False))
            kwargs = dict(model=model, max_tokens=16000,
                          system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
                          output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                          messages=[{"role": "user", "content": user}])
            try:
                try:
                    # the 1.x SDK has no temperature argument, so it goes in the raw body
                    resp = client.messages.create(extra_body={"temperature": 0}, **kwargs)                         if use_temperature else client.messages.create(**kwargs)
                except anthropic.BadRequestError as exc:
                    if use_temperature and "temperature" in str(exc).lower():
                        use_temperature = False
                        log(f"  model {model} rejects temperature (HTTP 400: {ip.redact(str(exc))[:200]}); "
                            "continuing without it, output constrained by the JSON schema")
                        resp = client.messages.create(**kwargs)
                    else:
                        raise
                u = resp.usage
                usage_rows.append(dict(input=u.input_tokens, output=u.output_tokens,
                                       cache_write=u.cache_creation_input_tokens or 0,
                                       cache_read=u.cache_read_input_tokens or 0))
                if resp.stop_reason not in ("end_turn",):
                    raise RuntimeError(f"stop_reason {resp.stop_reason}")
                text = next(b.text for b in resp.content if b.type == "text")
                out = json.loads(text)["results"]
                got = {r["id"]: r for r in out if r["id"] in set(batch["event_id"])}
                missing = set(batch["event_id"]) - set(got)
                log(f"  call {bi}: {len(batch)} stories, {len(got)} scored, {len(missing)} missing; "
                    f"tokens in {u.input_tokens} out {u.output_tokens} cache_read "
                    f"{u.cache_read_input_tokens or 0}; request {resp._request_id}")
                for eid, r in got.items():
                    results[eid] = r
                    results.setdefault("_seen", []).append((eid, batch.set_index("event_id").loc[eid, "title"]))
            except Exception as exc:
                failed_batches += 1
                log(f"  call {bi} FAILED ({len(batch)} stories left unscored): {ip.redact(repr(exc))[:300]}")
        results.pop("_seen", None)
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        upd = df.set_index("event_id")
        # cluster_id: the cluster of the earlier story this one duplicates, else its own id.
        # Stories are taken in publish order, so a parent is always resolved first; clusters
        # from earlier runs are kept as they are.
        cluster = {e: c for e, c in upd["cluster_id"].items() if c}
        bad_dup = 0
        for eid in todo["event_id"]:
            if eid not in results:
                continue
            r = results[eid]
            sig, ai = int(r["significance"]), int(r["ai_power_relevance"])
            if not (0 <= sig <= 10 and 0 <= ai <= 10):
                log(f"  {eid}: score out of range ({sig}, {ai}); left unscored")
                continue
            dup = r["is_duplicate_of"]
            if dup and (dup == eid or dup not in known):
                bad_dup += 1
                dup = None
            cluster[eid] = cluster.get(dup, dup) if dup else eid
            upd.loc[eid, ["significance", "ai_power_relevance", "sector", "region", "price_mentioned",
                          "why", "model_id", "scored_at", "cluster_id"]] = [
                str(sig), str(ai), r["sector"], nodash(r["region"]), nodash(r["price_mentioned"] or ""),
                nodash(" ".join(r["one_line_why"].split())), model, now, cluster[eid]]
            upd.loc[eid, "mw"] = "" if r["mw_mentioned"] is None else f"{float(r['mw_mentioned']):g}"
            upd.loc[eid, "parties"] = nodash("; ".join(p.replace(";", ",") for p in r["parties"]))
            upd.loc[eid, "headline"] = nodash(r["headline"])
        upd = upd.reset_index()
        scored = upd["scored_at"] != ""
        changed = upd[upd["event_id"].isin(results.keys())]
        tin = sum(x["input"] for x in usage_rows)
        tout = sum(x["output"] for x in usage_rows)
        cw = sum(x["cache_write"] for x in usage_rows)
        cr = sum(x["cache_read"] for x in usage_rows)
        if model in PRICES:
            pi, po = PRICES[model]
            # cache writes at 1.25x input and reads at 0.1x input (5-minute TTL), per the skill
            cost = (tin * pi + cw * pi * 1.25 + cr * pi * 0.1 + tout * po) / 1e6
            cost_s = f"USD {cost:.4f}"
        else:
            cost_s = "unknown (model not in PRICES)"
        n_clusters = upd.loc[scored, "cluster_id"].nunique()
        summary = (f"model {model}; calls {len(usage_rows)} ({failed_batches} failed); stories scored "
                   f"{len(results)} of {len(todo)}; tokens input {tin}, output {tout}, cache write {cw}, "
                   f"cache read {cr}; cost {cost_s}; duplicate links rejected {bad_dup}; clusters "
                   f"{n_clusters} among {int(scored.sum())} scored stories; temperature "
                   f"{'0' if use_temperature else 'not accepted by model'}")
        log("RUN " + summary)
        header.append(f"Scored: {run_id} by warehouse/news/score.py, {summary}. Rubric: "
                      "warehouse/news/rubric.md; run log warehouse/output/logs/news_score_"
                      f"{run_id}.log.")
        ip.write_csv(changed[NEWS_COLS], NAME, header, log, cols=NEWS_COLS, key=KEY,
                     time_col="event_date")
        status["detail"] = summary[:300]
        if failed_batches or len(results) < len(todo):
            status["status"] = "failed" if not results else "ok"
        print(f"news score: {summary}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"news_score {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("news_score", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
