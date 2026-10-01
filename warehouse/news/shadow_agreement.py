#!/usr/bin/env python3
"""How far the shadow model's news scores agree with the published (Sonnet-class) ones, and what each costs.

Energy Research Warehouse (ERW), session 30 (Part B4). Reads news_stories (the published scores) and
news_scores_shadow (the shadow's, warehouse/news/shadow.py), joined on the story, and reports, per publish day (UTC)
and overall:

  selection     the digest's selection: the top N clusters of the day, each model's own clusters ranked as
                brief.build_clusters ranks them (highest significance, then AI-power relevance, then stories, then
                first published). A published top-N cluster is matched when a shadow top-N cluster shares a story
                with it; overlap = matched / N. Also the top N stories by significance, compared as sets.
  significance  Pearson and Spearman correlation, mean absolute difference, exact and within-1 agreement.
  AI-power tag  ai_power_relevance >= 7 (the digest's "AI and power" rule): agreement, Cohen's kappa, and the mean
                absolute difference of the 0 to 10 score.
  cost          of each model for the same stories. The shadow's is measured: its calls in api_cost_ledger. The
                published model's is measured where the ledger has its scoring calls (from session 30 on); for
                stories scored before the ledger existed it is an estimate, labelled as one: the stories times the
                mean cost per story of the scoring runs whose logs are on this machine (warehouse/output/logs/
                news_score_*.log, their "RUN" lines).

--labels (default warehouse/news/eval/eval_sample.csv, Samuel's 50-story eval file) adds both models against the
human's labels once human_significance and human_ai_power are filled: mean absolute error, Spearman correlation and
top-10 overlap, as warehouse/news/eval/eval.py reports them for the published model.

    python warehouse/news/shadow_agreement.py
    python warehouse/news/shadow_agreement.py --model claude-haiku-4-5 --days 30 --top 10 --json out.json
"""

import argparse
import glob
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import llm  # noqa: E402
from ingest import NAME as NEWS, NEWS_COLS  # noqa: E402
import shadow  # noqa: E402

AI_TAG = 7
EVAL = os.path.join(HERE, "eval", "eval_sample.csv")


def clusters_top(df, sig, ai, cl, n):
    """The top n clusters as brief.build_clusters ranks them, each as the set of its story ids."""
    d = df[df[sig] > 0]
    if d.empty:
        return []
    g = d.groupby(cl).agg(sig=(sig, "max"), ai=(ai, "max"), n=("story_id", "size"), first=("event_date", "min"),
                          stories=("story_id", lambda s: frozenset(s)))
    g = g.sort_values(["sig", "ai", "n", "first"], ascending=[False, False, False, True])
    return list(g["stories"].head(n))


def top_stories(df, sig, ai, n):
    d = df.sort_values([sig, ai, "event_date", "story_id"], ascending=[False, False, True, True])
    return set(d["story_id"].head(n))


def kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) == 0:
        return None
    po = float((a == b).mean())
    pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return None if pe == 1 else (po - pe) / (1 - pe)


def stats(d, n):
    s, h = d["sig_p"], d["sig_s"]
    out = {"stories": int(len(d))}
    if len(d) >= 3 and s.nunique() > 1 and h.nunique() > 1:
        out["sig_pearson"] = round(float(s.corr(h)), 3)
        out["sig_spearman"] = round(float(s.rank().corr(h.rank())), 3)
    out["sig_mad"] = round(float((s - h).abs().mean()), 3) if len(d) else None
    out["sig_exact"] = round(float((s == h).mean()), 3) if len(d) else None
    out["sig_within1"] = round(float(((s - h).abs() <= 1).mean()), 3) if len(d) else None
    out["ai_mad"] = round(float((d["ai_p"] - d["ai_s"]).abs().mean()), 3) if len(d) else None
    tp, ts = d["ai_p"] >= AI_TAG, d["ai_s"] >= AI_TAG
    out["ai_tag_published"], out["ai_tag_shadow"] = int(tp.sum()), int(ts.sum())
    out["ai_tag_agree"] = round(float((tp == ts).mean()), 3) if len(d) else None
    k = kappa(tp, ts)
    out["ai_tag_kappa"] = None if k is None else round(k, 3)
    top_p = clusters_top(d, "sig_p", "ai_p", "cl_p", n)
    top_s = clusters_top(d, "sig_s", "ai_s", "cl_s", n)
    if top_p:
        matched = sum(1 for c in top_p if any(c & x for x in top_s))
        out["top_clusters"] = len(top_p)
        out["top_clusters_matched"] = matched
        out["selection_overlap"] = round(matched / len(top_p), 3)
    sp, ss = top_stories(d, "sig_p", "ai_p", n), top_stories(d, "sig_s", "ai_s", n)
    out["top_stories_overlap"] = round(len(sp & ss) / max(1, min(n, len(d))), 3)
    return out


def sonnet_cost_per_story():
    """(USD per story, stories, runs) from the scoring logs on this machine: the estimate for stories scored before
    the ledger existed."""
    usd, n, runs = 0.0, 0, 0
    for f in glob.glob(os.path.join(ip.LOG_DIR, "news_score_*.log")):
        for line in open(f, encoding="utf-8", errors="replace"):
            m = re.search(r"^RUN model (\S+);.*stories scored (\d+) of \d+;.*cost USD ([\d.]+)", line)
            if m and "sonnet" in m.group(1):
                n += int(m.group(2))
                usd += float(m.group(3))
                runs += 1
    return (usd / n if n else None), n, runs


def labels_report(merged, path, n):
    if not os.path.exists(path):
        return {"file": os.path.relpath(path, ROOT), "status": "absent"}
    e = pd.read_csv(path, dtype=str, keep_default_na=False)
    e = e[(e["human_significance"].str.strip() != "") & (e["human_ai_power"].str.strip() != "")]
    if e.empty:
        return {"file": os.path.relpath(path, ROOT), "status": "no human labels yet (human_significance and "
                "human_ai_power are empty)"}
    e = e.assign(h_sig=pd.to_numeric(e["human_significance"]), h_ai=pd.to_numeric(e["human_ai_power"]))
    m = merged.merge(e[["id", "h_sig", "h_ai"]], left_on="story_id", right_on="id")
    out = {"file": os.path.relpath(path, ROOT), "labelled": int(len(e)), "with_both_models": int(len(m))}
    for who, sig, ai in (("published", "sig_p", "ai_p"), ("shadow", "sig_s", "ai_s")):
        r = {"sig_mae": round(float((m[sig] - m["h_sig"]).abs().mean()), 3),
             "ai_mae": round(float((m[ai] - m["h_ai"]).abs().mean()), 3),
             "sig_spearman": round(float(m[sig].rank().corr(m["h_sig"].rank())), 3),
             "ai_spearman": round(float(m[ai].rank().corr(m["h_ai"].rank())), 3)}
        top_h = set(m.sort_values(["h_sig", "h_ai", "story_id"], ascending=[False, False, True])["story_id"].head(n))
        top_m = set(m.sort_values([sig, ai, "story_id"], ascending=[False, False, True])["story_id"].head(n))
        r["top_overlap"] = f"{len(top_h & top_m)} of {min(n, len(m))}"
        out[who] = r
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Shadow scorer agreement (session 30, B4)")
    ap.add_argument("--model", default=os.environ.get("SHADOW_MODEL") or "claude-haiku-4-5")
    ap.add_argument("--days", type=int, default=30, help="stories published in the last N days (default 30)")
    ap.add_argument("--top", type=int, default=10, help="N of the top-N selection (the digest's top 10)")
    ap.add_argument("--labels", default=EVAL, help="the human eval file (default warehouse/news/eval/eval_sample.csv)")
    ap.add_argument("--json", help="also write the numbers to this file")
    args = ap.parse_args(argv)

    news = ip.read_series(os.path.join(ip.OUT_DIR, NEWS + ".csv"), NEWS_COLS)
    news = news[news["scored_at"] != ""]
    sh = shadow.read_shadow()
    sh = sh[sh["model_id"] == args.model]
    p = news[["event_id", "event_date", "significance", "ai_power_relevance", "cluster_id", "model_id"]].rename(
        columns={"event_id": "story_id", "significance": "sig_p", "ai_power_relevance": "ai_p", "cluster_id": "cl_p",
                 "model_id": "model_p"})
    s = sh[["story_id", "significance", "ai_power_relevance", "cluster_id"]].rename(
        columns={"significance": "sig_s", "ai_power_relevance": "ai_s", "cluster_id": "cl_s"})
    m = p.merge(s, on="story_id")
    for c in ("sig_p", "sig_s", "ai_p", "ai_s"):
        m[c] = pd.to_numeric(m[c])
    when = pd.to_datetime(m["event_date"], utc=True, format="ISO8601")
    labelled = m.copy()
    m = m[when >= pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=args.days)]
    m = m.assign(day=pd.to_datetime(m["event_date"], utc=True, format="ISO8601").dt.strftime("%Y-%m-%d"))

    report = {"model_shadow": args.model, "models_published": sorted(m["model_p"].unique().tolist()),
              "window_days": args.days, "top_n": args.top, "overall": stats(m, args.top),
              "per_day": {d: stats(g, args.top) for d, g in m.groupby("day")}}
    # the digest selects per day: the mean of the days' overlaps, each day weighted equally, and weighted by stories
    pdx = pd.DataFrame(report["per_day"]).T
    if "selection_overlap" in pdx:
        so = pdx["selection_overlap"].astype(float)
        report["overall"]["selection_overlap_mean_per_day"] = round(float(so.mean()), 3)
        report["overall"]["selection_overlap_story_weighted"] = round(float((so * pdx["stories"]).sum() / pdx["stories"].sum()), 3)
        report["overall"]["top_stories_overlap_mean_per_day"] = round(float(pdx["top_stories_overlap"].astype(float).mean()), 3)
    # costs
    led = llm.read_ledger()
    led["usd"] = pd.to_numeric(led["usd"], errors="coerce")
    # the API answers with a dated id (claude-haiku-4-5-20251001): a row is the shadow model's if it is the alias or
    # a dated form of it
    is_shadow = led["model"].str.fullmatch(re.escape(args.model) + r"(-\d{8})?")
    shadow_calls = led[is_shadow & (led["step"] == "news_score_shadow")]
    measure = led[led["step"] == "news_score_shadow_nocache"]
    pub_calls = led[(led["step"] == "news_score") & led["model"].str.contains("sonnet")]
    per, n_logs, runs = sonnet_cost_per_story()
    report["cost"] = {
        "shadow_usd_measured": round(float(shadow_calls["usd"].sum()), 4),
        "shadow_calls": int(len(shadow_calls)),
        "shadow_stories": int(len(sh)),
        "shadow_usd_per_story": round(float(shadow_calls["usd"].sum()) / len(sh), 5) if len(sh) else None,
        "published_usd_in_ledger": round(float(pub_calls["usd"].sum()), 4),
        "published_usd_per_story_estimate": None if per is None else round(per, 5),
        "published_estimate_basis": f"{n_logs} stories in {runs} Sonnet scoring runs whose logs are on this machine",
        "published_usd_estimate_same_stories": None if per is None else round(per * len(sh), 4),
        "no_cache_measurement_usd": round(float(measure["usd"].sum()), 4) if len(measure) else None,
    }
    report["labels"] = labels_report(labelled, args.labels, args.top)

    o = report["overall"]
    print(f"Shadow {args.model} against the published scores ({', '.join(report['models_published'])}), "
          f"{o['stories']} stories, last {args.days} days")
    for k in ("selection_overlap_mean_per_day", "selection_overlap_story_weighted", "top_stories_overlap_mean_per_day",
              "selection_overlap", "top_clusters_matched", "top_stories_overlap", "sig_pearson", "sig_spearman",
              "sig_mad", "sig_exact", "sig_within1", "ai_mad", "ai_tag_published", "ai_tag_shadow", "ai_tag_agree",
              "ai_tag_kappa"):
        print(f"  {k}: {o.get(k)}")
    print("Per day:")
    print("  day | stories | selection overlap | top stories overlap | sig r | sig MAD | AI tag agree | kappa")
    for d, x in report["per_day"].items():
        print(f"  {d} | {x['stories']} | {x.get('selection_overlap')} | {x.get('top_stories_overlap')} | "
              f"{x.get('sig_pearson')} | {x.get('sig_mad')} | {x.get('ai_tag_agree')} | {x.get('ai_tag_kappa')}")
    print("Cost:", json.dumps(report["cost"]))
    print("Labels:", json.dumps(report["labels"]))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
