#!/usr/bin/env python3
"""Score policy actions with the news scorer's machinery (platform tool 12, session 24).

Energy Research Warehouse (ERW). Each unscored row of policy_actions (warehouse/connectors/policy_sources.py) is scored
exactly as a news story is: the same system prompt with the rubric (warehouse/news/rubric.md), the same JSON schema and
the same model choice, imported from warehouse/news/score.py (SYSTEM, SCHEMA, pick_model, PRICES). The item is the
action's title and, for a Federal Register document, its abstract (the Register's own summary), with the beat "policy".
Kept per action: significance (0 to 10), the scorer's sector and its one-line why, with the model and time, in
warehouse/policy/scores.csv (in git, so an action is scored once) and in the table's score columns.

    python warehouse/policy/score.py                  # every unscored action
    python warehouse/policy/score.py --max-usd 6      # stop before the spend passes this (default 6)
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import iso_prices as ip  # noqa: E402

NAME = "policy_actions"
SCORES = os.path.join(HERE, "scores.csv")
BATCH = 40
SCORE_COLS = ["significance", "sector", "why", "model_id", "scored_at"]


def read_table(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return head, pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def write_table(path, head, df, note):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for ln in head:
            if not ln.startswith("# Scores merged"):
                f.write(ln if ln.endswith("\n") else ln + "\n")
        f.write(f"# Scores merged {note}\n")
        df.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)


def first_list(obj):
    if isinstance(obj, list):
        return obj
    for v in obj.values():
        if isinstance(v, list):
            return v
    raise RuntimeError("no result list in the scorer's answer")


def score_batch(client, model, items):
    from score import SCHEMA, SYSTEM, nodash
    resp = client.messages.create(
        model=model, max_tokens=16000, system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": json.dumps({"stories": items}, ensure_ascii=False)}])
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason {resp.stop_reason}")
    out = first_list(json.loads(next(b.text for b in resp.content if b.type == "text")))
    return {r["id"]: (int(r["significance"]), r["sector"], nodash(r.get("one_line_why") or "")) for r in out}, resp.usage


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score ERW policy actions")
    ap.add_argument("--max-usd", type=float, default=6.0)
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"policy_score_{run_id}.log"))
    status = dict(table=NAME, market="score", status="ok", detail="")
    try:
        import anthropic
        from score import PRICES, pick_model
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        head, df = read_table(path)
        old = pd.read_csv(SCORES, dtype=str, keep_default_na=False) if os.path.exists(SCORES) else \
            pd.DataFrame(columns=["event_id"] + SCORE_COLS)
        todo = df[~df["event_id"].isin(set(old["event_id"]))]
        log(f"{len(df)} actions, {len(old)} scored before, {len(todo)} to score")
        new = []
        cost = 0.0
        if len(todo):
            client = anthropic.Anthropic(api_key=ip.load_key("ANTHROPIC_API_KEY", log))
            model = pick_model(client, log)
            price = PRICES.get(model)
            items = [{"id": r["event_id"], "feed_beat": "policy", "title": r["title"],
                      "summary": (r["abstract"] or r["status"])[:600]} for r in todo.to_dict("records")]
            batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]
            per_call = 0.12  # a ceiling per call, USD; the run stops before a group would pass --max-usd
            with cf.ThreadPoolExecutor(4) as pool:
                for g in range(0, len(batches), 4):
                    group = batches[g:g + 4]
                    if cost + per_call * len(group) > args.max_usd:
                        log(f"  stopping before batch {g + 1} of {len(batches)}: the spend would pass USD {args.max_usd}")
                        break
                    try:
                        answers = list(pool.map(lambda b: score_batch(client, model, b), group))
                    except Exception as exc:  # keep what is scored; the next run scores the rest
                        log(f"  batches {g + 1} to {g + len(group)} FAILED: {ip.redact(repr(exc))[:300]}")
                        status.update(status="failed")
                        break
                    for k, (res, u) in zip(range(g, g + len(group)), answers):
                        c = (u.input_tokens * price[0] + u.output_tokens * price[1]) / 1e6 if price else 0
                        cost += c
                        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
                        new += [dict(event_id=i, significance=str(s_), sector=sec, why=w, model_id=model, scored_at=now)
                                for i, (s_, sec, w) in res.items()]
                        log(f"  batch {k + 1} of {len(batches)}: {len(res)} scored, USD {c:.4f}; total USD {cost:.4f}")
        known = set(df["event_id"])
        new = [r for r in new if r["event_id"] in known]
        allsc = pd.concat([old, pd.DataFrame(new, columns=["event_id"] + SCORE_COLS)], ignore_index=True) \
            .drop_duplicates("event_id", keep="last")
        allsc.to_csv(SCORES, index=False, lineterminator="\n")
        df = df.drop(columns=SCORE_COLS).merge(allsc, on="event_id", how="left").fillna("")
        cols = [c for c in read_table(path)[1].columns]
        write_table(path, head, df[cols], f"by warehouse/policy/score.py at {run_id} (UTC); run log "
                                          f"warehouse/output/logs/policy_score_{run_id}.log")
        n5 = int((pd.to_numeric(df["significance"], errors="coerce") >= 5).sum())
        status["detail"] = (f"{len(new)} newly scored, {int((df['significance'] != '').sum())} of {len(df)} scored; "
                            f"{n5} at significance 5 or more; cost USD {cost:.4f}")
        log(status["detail"])
        print(f"policy_score: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"policy_score FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("policy_score", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
