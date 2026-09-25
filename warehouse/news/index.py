#!/usr/bin/env python3
"""Write the public news index: warehouse/output/news_index.csv.

Energy Research Warehouse (ERW), session 7 ruling 4. A public companion to
news_stories (which stays internal: it holds the outlets' titles and
summaries). news_index carries only fields that are links, metadata or the
model's own words, for every scored story:

    event_id, event_date, event_type, source, source_url, sector, region,
    significance, ai_power_relevance, cluster_id, headline

event_type (always "news") is included because the events standard requires
it; nothing the outlet wrote is copied. headline is the model's per-story
headline (written by warehouse/news/score.py since session 7; empty for
stories scored before it, which are not re-scored). The header declares
"License: public", which the coverage builder reads as the table's license.

    python warehouse/news/index.py
"""

import datetime as dt
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
from ingest import NAME, NEWS_COLS  # noqa: E402

INDEX = "news_index"
INDEX_COLS = ["event_id", "event_date", "event_type", "source", "source_url", "sector", "region",
              "significance", "ai_power_relevance", "cluster_id", "headline"]


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_index_{run_id}.log"))
    df = ip.read_series(os.path.join(ip.OUT_DIR, NAME + ".csv"), NEWS_COLS)
    scored = df[df["scored_at"] != ""][INDEX_COLS].copy()
    n_head = int((scored["headline"] != "").sum())
    header = [
        "Energy Research Warehouse (ERW): Public news index: links, metadata and model scores",
        "Shape: events (docs/datastandard.md v0), event_type news. event_date is the publish time, UTC.",
        f"Retrieved: {run_id} (UTC) by warehouse/news/index.py from warehouse/output/{NAME}.csv "
        "(the feeds were retrieved by warehouse/news/ingest.py; see retrieval in that table)",
        f"Run log: warehouse/output/logs/news_index_{run_id}.log",
        f"Built from warehouse/output/{NAME}.csv by warehouse/news/index.py: every scored story, "
        f"{len(scored)} rows, {n_head} with a model headline (stories scored before session 7 have none).",
        "License: public. Only links, metadata and the model's own fields; no outlet text. The internal "
        f"table {NAME} holds titles and summaries.",
        "Sources: the outlet named in each row's source column; source_url links the story (a "
        "news.google.com link where Google News could not be resolved to the outlet).",
    ]
    log(f"ERW news_index {run_id}: {len(scored)} scored stories, {n_head} with a model headline")
    ip.write_csv(scored, INDEX, header, log, cols=INDEX_COLS, key=["event_id"],
                 time_col="event_date")
    # the outlets feed this table too; the registry keeps their entries (license internal for
    # the text; the public index is licensed at table level by its header)
    reg_path = os.path.join(ip.METADATA_DIR, "sources.csv")
    reg = pd.read_csv(reg_path, dtype=str, keep_default_na=False)
    entries = [dict(r, tables=[t for t in r["tables"].split(";") if t] + [INDEX])
               for r in reg[reg["source"].isin(set(scored["source"]))].to_dict("records")]
    ip.update_sources(entries)
    log("done")
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
