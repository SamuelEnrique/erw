#!/usr/bin/env python3
"""The datacenter extraction graded on a fixture of stored stories (session 2236, chain 156).

Energy Research Warehouse (ERW). The facilities' form of `warehouse/deals/eval/fixture.py`: `tests/fixtures/datacenters/`
holds `stories_<N>.json` (stored stories), `answers_<N>.json` (answers written from their words) and
`recorded_<N>.json` (what the model answered, recorded once under a cap). The Census gazetteers are not read (a county
or a place is placed by them, which this fixture does not grade); utility_service_territories is read where held.

    python warehouse/datacenters/eval/dc_fixture.py record --set 2236 --cap 3.00
    python warehouse/datacenters/eval/dc_fixture.py grade --set 2236
"""

import argparse
import contextlib
import datetime as dt
import importlib.util
import json
import os
import sys
import types
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
DC = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(DC, "..", ".."))
FIX = os.path.join(ROOT, "tests", "fixtures", "datacenters")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
_spec = importlib.util.spec_from_file_location("erw_deals_fixture", os.path.join(ROOT, "warehouse", "deals", "eval", "fixture.py"))
deals_fixture = importlib.util.module_from_spec(_spec)   # the sandbox, the replay and the recorder, loaded by path
_spec.loader.exec_module(deals_fixture)


def load_extract():
    spec = importlib.util.spec_from_file_location("erw_dc_extract_fixture", os.path.join(DC, "extract.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


@contextlib.contextmanager
def sandbox(ex, client, model):
    with deals_fixture.sandbox(ex, client, model) as tmp, \
            mock.patch.object(ex.ep, "load_gazetteer", lambda run_id, log: ({}, [("fixture: no gazetteer read",)])), \
            mock.patch.object(ex, "load_places", lambda log: ({}, "fixture")), \
            mock.patch.object(ex, "locate", lambda row, c, p: ("", "", "none", "fixture: not placed")):
        yield tmp


class Replay(deals_fixture.Replay):
    def __init__(self, recorded):
        self.by_cluster = {}
        for call in recorded["calls"]:
            for r in json.loads(call["text"])["results"]:
                self.by_cluster[r["cluster_id"]] = r
        self.messages = self
        self.n = 0

    def create(self, **kw):
        items = json.loads(kw["messages"][0]["content"].split("Clusters (JSON):\n", 1)[1])
        text = json.dumps({"results": [self.by_cluster.get(i["cluster_id"], {"cluster_id": i["cluster_id"], "facilities": []})
                                       for i in items]})
        return types.SimpleNamespace(
            usage=types.SimpleNamespace(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0,
                                        cache_read_input_tokens=0),
            stop_reason="end_turn", content=[types.SimpleNamespace(type="text", text=text)], _request_id="replay")


def rows_of(ex, tmp):
    p = os.path.join(tmp, ex.TABLE + ".csv")
    return ex.read_table(p, ex.COLS)


def replay(set_id):
    ex = load_extract()
    with sandbox(ex, Replay(read(f"recorded_{set_id}.json")), "replay") as tmp:
        deals_fixture.write_news(ex, tmp, read(f"stories_{set_id}.json"))
        rc = ex.main([])
        if rc != 0:
            raise RuntimeError(f"the extractor exited {rc}: {deals_fixture.log_of(tmp)[-600:]}")
        return rows_of(ex, tmp), deals_fixture.log_of(tmp)


def _ok(want, got):
    if want is None:
        return True
    opts = want if isinstance(want, list) else [want]
    g = " ".join(str(got or "").split()).lower()
    for w in opts:
        w = str(w).lower()
        if (w == "" and g == "") or (w and (g == w or (w in g and len(w) >= 4))):
            return True
    return False


GRADED = ["operator", "state", "country", "city", "county", "mw", "mw_basis", "project_status", "power_kind",
          "energized_year", "planned_year"]


def grade(rows, answers, view="new"):
    out = {"clusters": len(answers), "found_wrongly": [], "missed": [], "two_places_one_row": [],
           "fields": {f: [] for f in GRADED}}
    rec = rows.to_dict("records") if rows is not None else []
    row_of = {}
    for a in answers:
        if view == "stored":
            mine = [a["stored"]] if a.get("stored") else []
        else:
            mine = [r for r in rec if set(str(r["story_ids"]).split(";")) & set(a["story_ids"])]
        if mine:
            row_of[a["n"]] = mine[0].get("entity_id")
        if a["is_facility"] is False:
            if mine:
                out["found_wrongly"].append(a["n"])
            continue
        if not mine:
            if a["is_facility"] is True:
                out["missed"].append(a["n"])
            continue
        r = mine[0]
        for f in GRADED:
            if view == "stored" and f not in r:
                continue
            if not _ok(a.get(f), r.get(f)):
                out["fields"][f].append(f"{a['n']}: {r.get(f)!r}, answer {a.get(f)!r}")
    for a in answers:
        for other in a.get("not_with", []):
            if a["n"] in row_of and other in row_of and row_of[a["n"]] == row_of[other]:
                out["two_places_one_row"].append(f"{a['n']} and {other}")
    return out


def summary(g):
    lines = [f"clusters {g['clusters']}; a facility kept where none is: {len(g['found_wrongly'])} {g['found_wrongly']}; "
             f"missed: {len(g['missed'])} {g['missed']}; two places in one row: {g['two_places_one_row']}"]
    for f, bad in g["fields"].items():
        lines.append(f"  {f}: {len(bad)} wrong" + (f" ({'; '.join(bad[:6])})" if bad else ""))
    return "\n".join(lines)


def record(set_id, cap):
    ex = load_extract()
    import anthropic
    key = ex.ip.load_key("ANTHROPIC_API_KEY", print)
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is empty")
    real = anthropic.Anthropic(api_key=key)
    model = ex.pick_model(real, print)
    rec = deals_fixture.Recorder(real, cap, model)
    with sandbox(ex, rec, model) as tmp:
        deals_fixture.write_news(ex, tmp, read(f"stories_{set_id}.json"))
        rc = ex.main([])
        log = deals_fixture.log_of(tmp)
    out = {"set": set_id, "model": model, "recorded_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "extractor_exit": rc, "usd": round(rec.spent, 6), "calls": rec.calls}
    with open(os.path.join(FIX, f"recorded_{set_id}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"recorded {len(rec.calls)} calls, USD {rec.spent:.4f}, model {model}, extractor exit {rc}")
    for line in log.splitlines():
        if "FAILED" in line or "cost USD" in line:
            print("  log:", line[:300])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=["record", "grade"])
    ap.add_argument("--set", default="2236")
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
