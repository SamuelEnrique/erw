#!/usr/bin/env python3
"""The deal extraction graded on a fixture of stored stories (session 2232, chain 156).

Energy Research Warehouse (ERW). `tests/fixtures/deals/stories_<N>.json` holds stored stories (title and summary as
`news_stories` holds them) and `answers_<N>.json` the answers a session wrote from those stories' own words. This
module does two things:

    python warehouse/deals/eval/fixture.py record --set 2232 --cap 3.00
        runs warehouse/deals/extract.py on the fixture's stories in a temporary folder with the real model (the
        owner's key), and writes what the model answered, call by call, to tests/fixtures/deals/recorded_<N>.json
        with each call's tokens and cost. Nothing is written to warehouse/output; no ledger row (ERW_LEDGER=0: a code
        machine holds no data lock); the run stops before a call that would pass the cap.

    python warehouse/deals/eval/fixture.py grade --set 2232
        replays the recorded answers through the extractor (a fake client: no model, no network) and prints the
        grade of every fault class of docs/reviews/deals-audit-2026-11-06.md.

grade() is what tests/test_session2232_deals.py asserts on. An answer's field is a value (the row must equal it), a
list (any of them), None (not graded) or "" (the row must leave it empty: a figure where the story states none is
a figure invented).
"""

import argparse
import contextlib
import datetime as dt
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types
from unittest import mock

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEALS_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(DEALS_DIR, "..", ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "deals")
sys.path.insert(0, DEALS_DIR)
import deal_parties as dp  # noqa: E402


def load_extract():
    spec = importlib.util.spec_from_file_location("erw_deals_extract_fixture", os.path.join(DEALS_DIR, "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


@contextlib.contextmanager
def sandbox(ex, client, model):
    """The extractor pointed at a temporary folder, with the given client; yields the folder."""
    tmp = tempfile.mkdtemp(prefix="erw_deals_fixture_")
    ip = ex.ip
    patches = [
        mock.patch.dict(os.environ, {"ERW_LOCK_EXEMPT": "1", "ERW_LEDGER": "0"}),
        mock.patch.object(ip, "OUT_DIR", tmp),
        mock.patch.object(ip, "LOG_DIR", os.path.join(tmp, "logs")),
        mock.patch.object(ip, "STATUS_DIR", os.path.join(tmp, "status")),
        mock.patch.object(ip, "METADATA_DIR", os.path.join(tmp, "metadata")),
        mock.patch.object(ip, "update_sources", lambda entries: None),
        mock.patch.object(ex, "CHECKED", os.path.join(tmp, "checked.csv")),
        mock.patch.object(ex, "pick_model", lambda c, log: model),
        mock.patch.object(ex.llm, "client", lambda *a, **k: client),
    ]
    if model == "replay":
        patches.append(mock.patch.object(ip, "load_key", lambda *a, **k: "replay"))
    for p in patches:
        p.start()
    try:
        os.makedirs(os.path.join(tmp, "metadata"))
        with open(os.path.join(tmp, "metadata", "sources.csv"), "w", encoding="utf-8") as f:
            f.write("source,tables\n")
        yield tmp
    finally:
        for p in reversed(patches):
            p.stop()
        shutil.rmtree(tmp, ignore_errors=True)


def write_news(ex, tmp, stories):
    cols = ex.NEWS_COLS
    pd.DataFrame([{c: s.get(c, "") for c in cols} for s in stories], columns=cols).to_csv(
        os.path.join(tmp, "news_stories.csv"), index=False, lineterminator="\n")


def rows_of(ex, tmp):
    p = os.path.join(tmp, "energy_deals.csv")
    return ex.ip.read_series(p, ex.DEAL_COLS) if os.path.exists(p) else pd.DataFrame(columns=ex.DEAL_COLS)


def log_of(tmp):
    out = ""
    d = os.path.join(tmp, "logs")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            out += fh.read()
    return out


# ------------------------------------------------------------------ the replay client

class Replay:
    """Answers each call from the recorded answers, by cluster id (the extractor batches the same way it did)."""

    def __init__(self, recorded):
        self.by_cluster = {}
        for call in recorded["calls"]:
            for r in json.loads(call["text"])["results"]:
                self.by_cluster[r["cluster_id"]] = r
        self.messages = self
        self.n = 0

    def create(self, **kw):
        user = kw["messages"][0]["content"]
        items = json.loads(user.split("Clusters (JSON):\n", 1)[1])
        self.n += 1
        text = json.dumps({"results": [self.by_cluster.get(i["cluster_id"], {"cluster_id": i["cluster_id"], "deals": []})
                                       for i in items]})
        return types.SimpleNamespace(
            usage=types.SimpleNamespace(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0,
                                        cache_read_input_tokens=0),
            stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=text)], _request_id="replay")


def replay(set_id, stories=None):
    """(rows, log) of the extractor run on the fixture with the recorded answers."""
    ex = load_extract()
    rec = read(f"recorded_{set_id}.json")
    with sandbox(ex, Replay(rec), "replay") as tmp:
        write_news(ex, tmp, stories or read(f"stories_{set_id}.json"))
        rc = ex.main([])
        if rc != 0:
            raise RuntimeError(f"the extractor exited {rc}: {log_of(tmp)[-600:]}")
        return rows_of(ex, tmp), log_of(tmp)


# ------------------------------------------------------------------ the grade

def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _match(field, want, got):
    """True when the row's value meets the answer's."""
    if want is None:
        return True
    opts = want if isinstance(want, list) else [want]
    got = "" if got is None else str(got).strip()
    for w in opts:
        if w == "" and got == "":
            return True
        if w == "":
            continue
        if field in ("mw", "mwh", "usd", "term_years", "usd_per_mwh"):
            if _num(got) is not None and abs(_num(got) - float(w)) < 1e-6 * max(1.0, abs(float(w))):
                return True
        elif field in ("buyer", "seller"):
            if got and dp.same_party(got, w):
                return True
        elif field == "country":
            g = dp.plain(got)
            if g and (g == dp.plain(w) or (dp.plain(w) in ("uk", "united kingdom") and g in ("uk", "united kingdom"))
                      or (dp.plain(w) in dp.US_ALIASES and g in dp.US_ALIASES)):
                return True
        elif field == "ai_power":
            if got.lower() == str(bool(w)).lower():
                return True
        else:
            if got == str(w):
                return True
    return False


GRADED = ["deal_type", "kind", "buyer", "seller", "mw", "mwh", "usd", "term_years", "usd_per_mwh", "stage", "country",
          "state", "ai_power"]


def grade(rows, answers, view="new"):
    """Counts of each fault class on the fixture. rows: the extractor's energy_deals (view "new") or the stored rows
    of each answer (view "stored", the table as it was). Returns {class: [n or detail]}."""
    out = {"clusters": len(answers), "deal_found_wrongly": [], "deal_missed": [], "fields": {f: [] for f in GRADED},
           "figure_invented": [], "price_not_energy": []}
    for a in answers:
        if view == "stored":
            s = a["stored"]
            mine = [] if not s.get("event_id") else [{**s, "usd": s.get("dollars", ""), "kind": None, "stage": None,
                                                      "term_years": None, "mwh": None, "usd_per_mwh": None}]
        else:
            mine = [r for r in rows.to_dict("records")
                    if a["cluster_id"] in [x for x in str(r.get("story_ids", "")).split(";")] or
                    any(s in str(r.get("story_ids", "")).split(";") for s in a.get("story_ids", []))]
        if a["is_deal"] is False:
            if mine:
                out["deal_found_wrongly"].append(a["n"])
            continue
        if not mine:
            if a["is_deal"] is True:
                out["deal_missed"].append(a["n"])
            continue
        want = a["deals"][0]
        # the row that is the answer's deal: the one whose parties match best
        def score(r):
            return sum(_match(f, want.get(f), r.get(f)) for f in ("buyer", "seller", "deal_type", "kind"))
        r = max(mine, key=score)
        for f in GRADED:
            if view == "stored" and r.get(f) is None:
                continue   # a field the stored table does not have is not graded on it
            if not _match(f, want.get(f), r.get(f)):
                out["fields"][f].append(f"{a['n']}: {r.get(f)!r}, answer {want.get(f)!r}")
                if f in ("mw", "mwh", "usd", "term_years", "usd_per_mwh") and want.get(f) == "" and str(r.get(f) or "") != "":
                    out["figure_invented"].append(f"{a['n']}: {f} {r.get(f)}")
        if view == "new" and str(r.get("price_value") or "") != "" and "%" in str(r.get("price_unit") or ""):
            out["price_not_energy"].append(a["n"])
    return out


def summary(g):
    n = g["clusters"]
    lines = [f"clusters {n}; a deal kept where none is: {len(g['deal_found_wrongly'])} {g['deal_found_wrongly']}; "
             f"a deal missed: {len(g['deal_missed'])} {g['deal_missed']}; figures invented: {len(g['figure_invented'])}"]
    for f, bad in g["fields"].items():
        lines.append(f"  {f}: {len(bad)} wrong" + (f" ({'; '.join(bad[:6])})" if bad else ""))
    return "\n".join(lines)


# ------------------------------------------------------------------ the record

class Recorder:
    def __init__(self, inner, cap, model):
        self.inner, self.cap, self.model = inner, cap, model
        self.calls, self.spent = [], 0.0
        self.messages = self

    def create(self, **kw):
        if self.spent >= self.cap:
            raise RuntimeError(f"the cap of USD {self.cap:.2f} is reached (USD {self.spent:.4f} spent)")
        resp = self.inner.messages.create(**kw)
        text = "".join(b.text for b in resp.content if b.type == "text")
        try:   # the cost is counted after the call has been paid for: a fault here must not lose the answer
            import llm
            n = llm.usage_numbers(resp.usage)
            cost = llm.usd(self.model, n) or 0.0
        except Exception as exc:  # noqa: BLE001
            n, cost = {"error": repr(exc)[:200]}, 0.0
        self.spent += cost
        self.calls.append({"request_id": getattr(resp, "_request_id", ""), "stop_reason": resp.stop_reason,
                           "tokens": n, "usd": round(cost, 6), "text": text})
        return resp


def record(set_id, cap):
    ex = load_extract()
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    import anthropic
    import llm
    key = ex.ip.load_key("ANTHROPIC_API_KEY", print)
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is empty")
    real = anthropic.Anthropic(api_key=key)
    model = ex.pick_model(real, print)
    rec = Recorder(real, cap, model)
    with sandbox(ex, rec, model) as tmp:
        write_news(ex, tmp, read(f"stories_{set_id}.json"))
        rc = ex.main([])
        log = log_of(tmp)
    out = {"set": set_id, "model": model, "recorded_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "extractor_exit": rc, "usd": round(rec.spent, 6), "calls": rec.calls}
    with open(os.path.join(FIX, f"recorded_{set_id}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"recorded {len(rec.calls)} calls, USD {rec.spent:.4f}, model {model}, extractor exit {rc}")
    for line in log.splitlines():
        if "FAILED" in line or "cost USD" in line:
            print("  log:", line[:300])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=["record", "grade"])
    ap.add_argument("--set", default="2232")
    ap.add_argument("--cap", type=float, default=3.0)
    args = ap.parse_args(argv)
    if args.what == "record":
        record(args.set, args.cap)
    answers = read(f"answers_{args.set}.json")
    print("stored rows (the table as it was):")
    print(summary(grade(None, answers, view="stored")))
    if os.path.exists(os.path.join(FIX, f"recorded_{args.set}.json")):
        rows, _ = replay(args.set)
        print(f"\nthe extractor on the recorded answers ({len(rows)} rows):")
        print(summary(grade(rows, answers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
