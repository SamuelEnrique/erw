#!/usr/bin/env python3
"""The Attention Index and the Friction Index, counted by code from the classified stories (session 3402, chain 202).

Energy Research Warehouse (ERW). Reads news_stories (every story: the week's denominators) and the rows the classifier
wrote (warehouse/derived/attention_classify.py: the jsonl files under warehouse/raw/attention/, and the rows the link
table already holds), and writes three tables:

  attention_story_links   events, one row a classified story: its week, sector, place, opposition, kind, tone and link.
                          The link from every index value to the stories that make it. No title or summary (the
                          news index's rule): the link, the outlet and the model's own headline.
  attention_index_weekly  series, by week (Monday 00:00Z, freq P1W), entity attention:<sector>:<geo>:
                          stories (count), attention_index (pct: the cell's stories as a share of the week's judged
                          stories), tone_mean (ratio, -1 to 1); and the entity attention:corpus:all with the week's
                          denominators (stories_week, stories_judged, stories_classified, stories_unsent_zero).
  friction_index_weekly   series, the same entities: opposition_stories (count), friction_index (pct: the cell's
                          opposition stories as a share of its stories), and one count a kind of opposition.

<sector> is one of the seven index sectors (datacenters, transmission, gas, nuclear, solar_wind, storage, oil_lng) or
"energy" (any energy sector, other_energy included). <geo> is "all" (every story), "US" (stories about the United
States) or a state's code. A week's "judged" stories are the classified ones plus the stories the news scorer gave
significance 0, which the classifier does not send (they count as not about energy). No model computes a number here;
the model's work is the classification, row by row, and every row is in the link table.

    python warehouse/derived/attention_index.py                      # reads and writes warehouse/output
    python warehouse/derived/attention_index.py --in-dir DIR --out-dir DIR2 --raw-dir DIR3   # a trial
    python warehouse/derived/attention_index.py --site-dir ../erw-3400/site   # also the page's two JSON files

Method: docs/methods/attention.md.
"""

import argparse
import datetime as dt
import glob
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import attention_classify as ac  # noqa: E402

LINKS, ATT, FRI = "attention_story_links", "attention_index_weekly", "friction_index_weekly"
SOURCE = "erw:attention"
METHOD = "docs/methods/attention.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD
LINK_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
             "source_url", "story_event_id", "week", "sector", "us", "state", "geo", "place", "place_kind", "opposition",
             "kind", "tone", "headline", "scorer_sector", "significance", "model_id", "prompt_version", "classified_at",
             "fixed", "retrieved_at"]
SERIES_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "source", "source_url", "retrieved_at"]
SECTORS = ac.INDEX_SECTORS + ["energy"]
ENERGY = set(ac.INDEX_SECTORS) | {"other_energy"}
OPP_KINDS = [k for k in ac.KINDS if k != "none"]


def week_of(when):
    """The Monday 00:00Z of the week holding each timestamp, as YYYY-MM-DDT00:00:00Z."""
    w = when.dt.tz_convert("UTC").dt.normalize()
    return (w - pd.to_timedelta(w.dt.weekday, unit="D")).dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def read_classified(raw_dir, in_dir):
    """Every classified row: the jsonl files and the link table's rows, the newest classification of a story kept."""
    rows = []
    for p in sorted(glob.glob(os.path.join(raw_dir, "classified_*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    new = pd.DataFrame(rows)
    path = os.path.join(in_dir, LINKS + ".csv")
    old = None
    if os.path.exists(path):
        t = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
        old = pd.DataFrame({"event_id": t["story_event_id"], "event_date": t["event_date"], "source": t["source"],
                            "source_url": t["source_url"], "headline": t["headline"], "significance": t["significance"],
                            "scorer_sector": t["scorer_sector"], "sector": t["sector"], "us": t["us"] == "true",
                            "state": t["state"], "place": t["place"], "place_kind": t["place_kind"],
                            "opposition": t["opposition"] == "true", "kind": t["kind"], "tone": t["tone"].astype(int),
                            "fixed": t["fixed"], "model_id": t["model_id"], "prompt_version": t["prompt_version"].astype(int),
                            "classified_at": t["classified_at"]})
    parts = [x for x in (old, new) if x is not None and len(x)]
    if not parts:
        return pd.DataFrame(columns=["event_id"])
    c = pd.concat(parts, ignore_index=True)
    for col in ("us", "opposition"):
        c[col] = c[col].map(lambda v: v if isinstance(v, bool) else str(v).lower() == "true")
    c["tone"] = c["tone"].astype(int)
    c = c.sort_values("classified_at").drop_duplicates("event_id", keep="last")
    # session 3403: a story classified before prompt version 3 with no headline takes the one the backfill wrote
    # (attention_classify.py --headlines, the jsonl files headlines_*.jsonl); the headline is the model's text either way
    c["headline"] = c["headline"].fillna("")
    backfilled = ac.read_headlines(raw_dir)
    if backfilled:
        empty = c["headline"] == ""
        c.loc[empty, "headline"] = c.loc[empty, "event_id"].map(backfilled).fillna("")
    return c.reset_index(drop=True)


def build(stories, classified, now):
    """The three tables and the page's data, from the stories and the classified rows."""
    stories = stories.copy()
    stories["_when"] = pd.to_datetime(stories["event_date"], utc=True, format="ISO8601")
    stories["week"] = week_of(stories["_when"])
    zero = stories["significance"].str.strip() == "0"
    done = stories["event_id"].isin(set(classified["event_id"]))
    weeks = (stories.groupby("week").agg(stories_week=("event_id", "size"))
             .join(stories[done].groupby("week").size().rename("stories_classified"))
             .join(stories[zero & ~done].groupby("week").size().rename("stories_unsent_zero")).fillna(0).astype(int))
    weeks["stories_judged"] = weeks["stories_classified"] + weeks["stories_unsent_zero"]

    c = classified.merge(stories[["event_id", "week"]], on="event_id", how="inner")
    c["geo"] = ["US-" + s if s else ("US" if u else "") for s, u in zip(c["state"], c["us"])]
    links = pd.DataFrame({
        "event_id": "attn:" + c["event_id"].str.replace("^news:", "", regex=True),
        "event_date": c["event_date"], "event_type": "attention_link", "parties": "", "entity_ids": "", "mw": "", "price": "",
        "currency": "", "status": "", "source": c["source"], "source_url": c["source_url"], "story_event_id": c["event_id"],
        "week": c["week"], "sector": c["sector"], "us": c["us"].map({True: "true", False: "false"}), "state": c["state"],
        "geo": c["geo"], "place": c["place"], "place_kind": c["place_kind"],
        "opposition": c["opposition"].map({True: "true", False: "false"}), "kind": c["kind"], "tone": c["tone"].astype(str),
        "headline": c["headline"].fillna(""), "scorer_sector": c["scorer_sector"].fillna(""), "significance": c["significance"].fillna(""),
        "model_id": c["model_id"], "prompt_version": c["prompt_version"].astype(str), "classified_at": c["classified_at"],
        "fixed": c["fixed"].fillna(""), "retrieved_at": now,
    })[LINK_COLS].sort_values(["event_date", "event_id"]).reset_index(drop=True)

    # the cells: (sector, geo, week) with the stories in them
    cells = []
    for sector in SECTORS:
        s = c[c["sector"].isin(ENERGY)] if sector == "energy" else c[c["sector"] == sector]
        for geo_key, g in (("all", s), ("US", s[s["us"]])):
            cells.append((sector, geo_key, g))
        for st, g in s[s["state"] != ""].groupby("state"):
            cells.append((sector, "US-" + st, g))
    att, fri = [], []

    def srow(entity, var, week, value, unit, geo):
        return dict(entity=entity, variable=var, ts_utc=week, value=value, unit=unit, freq="P1W", geo=geo, source=SOURCE,
                    source_url=METHOD_URL, retrieved_at=now)

    for week, w in weeks.iterrows():
        e = "attention:corpus:all"
        for var in ("stories_week", "stories_judged", "stories_classified", "stories_unsent_zero"):
            att.append(srow(e, var, week, int(w[var]), "count", ""))
    for sector, geo_key, g in cells:
        entity = f"attention:{sector}:{geo_key}"
        geo = "" if geo_key == "all" else geo_key
        for week, gw in g.groupby("week"):
            n = len(gw)
            judged = int(weeks.at[week, "stories_judged"]) if week in weeks.index else 0
            att.append(srow(entity, "stories", week, n, "count", geo))
            att.append(srow(entity, "attention_index", week, round(100.0 * n / judged, 4) if judged else 0.0, "pct", geo))
            att.append(srow(entity, "tone_mean", week, round(float(gw["tone"].mean()), 4), "ratio", geo))
            opp = gw[gw["opposition"]]
            fri.append(srow(entity, "opposition_stories", week, len(opp), "count", geo))
            fri.append(srow(entity, "friction_index", week, round(100.0 * len(opp) / n, 4), "pct", geo))
            counts = opp["kind"].value_counts()
            for k in OPP_KINDS:
                fri.append(srow(entity, f"kind_{k}", week, int(counts.get(k, 0)), "count", geo))
    att = pd.DataFrame(att, columns=SERIES_COLS).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
    fri = pd.DataFrame(fri, columns=SERIES_COLS).sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
    return links, att, fri, weeks, c


def site_files(links, att, fri, weeks, c, site_dir, now, header_note):
    """The page's two files: site/data/attention.json (the series and the cells, small) and
    site/public/attention/stories.json (every classified story's link, fetched on demand for the hovers)."""
    week_list = sorted(weeks.index)
    wi = {w: i for i, w in enumerate(week_list)}
    states = sorted({s for s in c["state"] if s})
    geos = ["all", "US"] + ["US-" + s for s in states]
    gi = {g: i for i, g in enumerate(geos)}
    si = {s: i for i, s in enumerate(SECTORS)}
    cells = []  # [sector_i, geo_i, week_i, stories, attention_index, opposition_stories, friction_index, tone_mean]
    a = att[att["variable"].isin(["stories", "attention_index", "tone_mean"])].pivot_table(index=["entity", "ts_utc"], columns="variable", values="value", aggfunc="first")
    f = fri[fri["variable"].isin(["opposition_stories", "friction_index"])].pivot_table(index=["entity", "ts_utc"], columns="variable", values="value", aggfunc="first")
    j = a.join(f, how="left").reset_index()
    for r in j.itertuples():
        _, sector, geo = r.entity.split(":")
        if sector not in si or geo not in gi:
            continue
        cells.append([si[sector], gi[geo], wi[r.ts_utc], int(r.stories), float(r.attention_index), int(r.opposition_stories),
                      float(r.friction_index), float(r.tone_mean)])
    kinds = {}
    for r in fri[fri["variable"].str.startswith("kind_")].itertuples():
        if r.value:
            _, sector, geo = r.entity.split(":")
            kinds.setdefault(f"{si[sector]}|{gi[geo]}|{wi[r.ts_utc]}", {})[r.variable[5:]] = int(r.value)
    # the places: county, city or metro named, by sector and week (the page's rising places)
    places = []
    pl = c[(c["place"] != "") & (c["us"])]
    for (sector, place, state, week), g in pl.groupby(["sector", "place", "state", "week"]):
        if sector in ENERGY:
            places.append([si[sector] if sector in si else si["energy"], place, state, wi[week], len(g), int(g["opposition"].sum())])
    denominators = [[wi[w], int(r.stories_week), int(r.stories_judged), int(r.stories_classified), int(r.stories_unsent_zero)]
                    for w, r in weeks.iterrows()]
    # what rose: for each week with classified stories, each sector (geo all) and each state (sector energy), the
    # attention index against the mean of the four weeks before (0 where a week before holds no row), so the page's
    # "rising this week" lists are read, not computed, on the page. rows: [week_i, kind, sector_i or state, this, mean_before, change]
    att_i = {(r.entity, r.ts_utc): float(r.value) for r in att[att["variable"] == "attention_index"].itertuples()}
    rising = []
    for w_i, week in enumerate(week_list):
        before = week_list[max(0, w_i - 4):w_i]
        for sector in SECTORS:
            e = f"attention:{sector}:all"
            this = att_i.get((e, week))
            if this is None:
                continue
            prev = [att_i.get((e, b), 0.0) for b in before]
            mean = round(sum(prev) / len(prev), 4) if prev else 0.0
            rising.append([w_i, "sector", si[sector], this, mean, round(this - mean, 4)])
        for st_code in states:
            e = f"attention:energy:US-{st_code}"
            this = att_i.get((e, week))
            if this is None:
                continue
            prev = [att_i.get((e, b), 0.0) for b in before]
            mean = round(sum(prev) / len(prev), 4) if prev else 0.0
            rising.append([w_i, "state", st_code, this, mean, round(this - mean, 4)])
    data = dict(built=now, note=header_note, weeks=week_list, sectors=SECTORS, geos=geos, states=states,
                denominators=denominators, cells=cells, kinds=kinds, places=places, rising=rising,
                counts=dict(stories=int(len(c)), opposition=int(c["opposition"].sum()), weeks_with_stories=int(c["week"].nunique())),
                model=sorted(c["model_id"].unique().tolist()), tables=[LINKS, ATT, FRI])
    os.makedirs(os.path.join(site_dir, "data"), exist_ok=True)
    with open(os.path.join(site_dir, "data", "attention.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    # the stories, one short record each, one file a week (site/public/attention/stories/<monday>.json, fetched when a
    # reader opens a week's hover), newest first within the week; the hover finds a cell's stories by sector, geo and week
    cols = ["id", "date", "outlet", "url", "headline", "sector", "state", "opposition", "kind", "tone", "place"]
    out = os.path.join(site_dir, "public", "attention", "stories")
    os.makedirs(out, exist_ok=True)
    for old in glob.glob(os.path.join(out, "*.json")):
        os.remove(old)
    n_st = 0
    for week, g in links.sort_values("event_date", ascending=False).groupby("week"):
        st = [[r.story_event_id, r.event_date[:10], r.source, r.source_url, r.headline, r.sector, r.state,
               1 if r.opposition == "true" else 0, r.kind, int(r.tone), r.place] for r in g.itertuples()]
        n_st += len(st)
        with open(os.path.join(out, week[:10] + ".json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(built=now, week=week, columns=cols, rows=st), fh, ensure_ascii=False, separators=(",", ":"))
            fh.write("\n")
    return len(cells), len(places), n_st


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the Attention and Friction indices from the classified stories")
    ap.add_argument("--in-dir", help="read news_stories and attention_story_links from this directory instead of warehouse/output")
    ap.add_argument("--out-dir", help="a trial: every output under this directory; nothing in warehouse/output")
    ap.add_argument("--raw-dir", default=ac.RAW_DIR, help="where the classifier's jsonl files are")
    ap.add_argument("--site-dir", help="also write site/data/attention.json and site/public/attention/stories.json under this site directory")
    args = ap.parse_args(argv)
    in_dir = os.path.abspath(args.in_dir) if args.in_dir else ip.OUT_DIR
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"attention_index_{run_id}.log"))
    try:
        stories = ac.read_stories(in_dir).drop(columns=["_when"])
        classified = read_classified(args.raw_dir, in_dir)
        if classified.empty:
            raise RuntimeError("no classified story: nothing is written")
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        links, att, fri, weeks, c = build(stories, classified, now)
        models = ", ".join(sorted(c["model_id"].unique()))
        first, last = c["week"].min()[:10], c["week"].max()[:10]
        share = f"{len(c)} of the {len(stories)} stories held are classified ({100.0 * len(c) / len(stories):.1f} percent), weeks {first} to {last}"
        common = [
            f"Built from: warehouse/output/news_stories.csv (the stories, their weeks and the week's denominators) and the classification of "
            f"warehouse/derived/attention_classify.py (model {models}; prompt version {int(c['prompt_version'].max())}). {share}.",
            "License: public. Only links, metadata and the model's own fields; no outlet text. The internal table news_stories holds titles and summaries.",
            f"Method: {METHOD}. The indices are counted by code from the classified rows; the model classifies one story at a time and never computes an index.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/attention_index.py",
            f"Run log: warehouse/output/logs/attention_index_{run_id}.log",
        ]
        h_links = ["Energy Research Warehouse (ERW): the stories behind the Attention and Friction indices, one row a classified story (session 3402)",
                   "Shape: events (docs/datastandard.md v0), event_type attention_link; event_date is the story's publish time, UTC; week is the Monday "
                   "00:00Z of its week; geo is US-<state> where the story names one state, US where it is about the United States, else empty; "
                   "opposition, kind and tone are the model's reading of the title and summary; fixed names any value the code emptied."] + common
        h_att = ["Energy Research Warehouse (ERW): the Attention Index by week, sector and place (session 3402)",
                 "Shape: series (docs/datastandard.md v0), freq P1W, ts_utc the Monday 00:00Z of the week. entity attention:<sector>:<geo>, sector one of "
                 "datacenters, transmission, gas, nuclear, solar_wind, storage, oil_lng or energy (any energy sector), geo all, US or a state code. "
                 "stories: the cell's classified stories; attention_index: those as a percent of the week's judged stories (attention:corpus:all, "
                 "stories_judged: the classified stories plus the stories the news scorer gave significance 0, which are not sent and count as not "
                 "about energy); tone_mean: the mean of the stories' tone, -1 to 1. A week whose stories are only partly classified is a lower bound; "
                 "the corpus entity says how many of the week's stories were judged."] + common
        h_fri = ["Energy Research Warehouse (ERW): the Friction Index by week, sector and place (session 3402)",
                 "Shape: series (docs/datastandard.md v0), freq P1W, ts_utc the Monday 00:00Z of the week; the entities of attention_index_weekly. "
                 "opposition_stories: the cell's stories that report opposition (a moratorium or ban, a lawsuit, a protest, a permit denied, a rate-case "
                 "fight, political opposition, other); friction_index: those as a percent of the cell's stories; kind_<kind>: the count of each kind."] + common
        ip.write_csv(links, LINKS, h_links, log, cols=LINK_COLS, key=["event_id"], time_col="event_date")
        ip.write_snapshot(att, ATT, h_att, log, SERIES_COLS)
        ip.write_snapshot(fri, FRI, h_fri, log, SERIES_COLS)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW)",
                                report="The Attention and Friction indices: coverage and opposition by week, sector and place, from the "
                                       "classified news stories (the ERW's own derivation)",
                                report_url=METHOD_URL, document_list="", license="public", tables=[LINKS, ATT, FRI])])
        detail = f"{share}; {len(links)} link rows, {len(att)} attention rows, {len(fri)} friction rows; {int(c['opposition'].sum())} opposition stories"
        if args.site_dir:
            n_cells, n_places, n_st = site_files(links, att, fri, weeks, c, args.site_dir, now, share)
            detail += f"; site files: {n_cells} cells, {n_places} place rows, {n_st} stories"
        log(detail)
        print(f"attention_index: {detail}")
        ip.write_status("attention_index", run_id, [dict(table=t, market="all", status="ok", detail=detail) for t in (LINKS, ATT, FRI)])
    except Exception as exc:
        log(f"FAILED: {exc!r}")
        ip.write_status("attention_index", run_id, [dict(table=t, market="all", status="failed", detail=repr(exc)[:300]) for t in (LINKS, ATT, FRI)])
        log.close()
        raise
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
