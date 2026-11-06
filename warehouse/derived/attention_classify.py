#!/usr/bin/env python3
"""The classification behind the Attention and Friction indices (session 3401, chain 202).

Energy Research Warehouse (ERW). Reads news_stories (title and summary; the corpus holds no body) and asks a fixed Claude
model, in batches, for each story: its sector (the indices' seven, or other_energy, or not_energy), whether it is about
the United States, the one state and the county, city or metro the text names, whether it reports opposition
(moratoria, lawsuits, protests, denied permits, rate-case fights, local or political resistance), the kind of
opposition, and its tone. Every answer is normalised by code (an unknown enum value or state code is emptied, never
guessed). The indices themselves are counted by warehouse/derived/attention_index.py from the classified rows; this
script writes no warehouse table. Method: docs/methods/attention.md.

    python warehouse/derived/attention_classify.py --sample 200 --seed 3400 --in-dir DIR --out FILE
        draw the labeled set's skeleton (half from stories whose text holds an opposition word, half from the rest),
        with the story text, for a person to label by hand (tests/fixtures/attention/labeled_200.csv)
    python warehouse/derived/attention_classify.py --ids FILE --in-dir DIR --out FILE [--model M]
        classify the stories FILE lists (event_id column) and write the model's answers to FILE (the accuracy test)
    python warehouse/derived/attention_classify.py --in-dir DIR --cap-usd 3 [--order newest|oldest] [--max-calls N]
        the run over the corpus: every story not yet classified (the jsonl files under warehouse/raw/attention/ and the
        rows of attention_story_links), the newest first, until the cap or the calls run out; each call's rows are
        appended to warehouse/raw/attention/classified_<run_id>.jsonl as they arrive, so a run that stops keeps what it
        classified

Model: ATTENTION_MODEL (claude-sonnet-5-5 since session 3401's trial), fixed and priced in warehouse/config/model_prices.yaml; the call goes through
warehouse/llm.py so the cost ledger records every call. The system prompt carries the prompt-cache breakpoint. A call
that fails leaves its stories unclassified and is logged; nothing is retried in the same run beyond the SDK's own
retries. No request leaves this machine but the model call.
"""

import argparse
import datetime as dt
import glob
import json
import os
import random
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import iso_prices as ip  # noqa: E402

# Session 3401's trial on the 200 hand-labeled stories: Sonnet 5.5 for friction precision 0.94 (Haiku 0.88) and the US
# field 0.93 (Haiku 0.80), at USD 0.71 a thousand stories (Haiku 0.29). Priced in warehouse/config/model_prices.yaml.
ATTENTION_MODEL = "claude-sonnet-5-5"
STEP = "attention_classify"
RAW_DIR = os.path.join(ip.RAW_DIR, "attention")
LINKS = "attention_story_links"
BATCH = 40
PROMPT_VERSION = 2

SECTORS = ["datacenters", "transmission", "gas", "nuclear", "solar_wind", "storage", "oil_lng", "other_energy", "not_energy"]
INDEX_SECTORS = SECTORS[:7]
KINDS = ["none", "moratorium", "lawsuit", "protest", "permit_denied", "rate_case", "political_opposition", "other_opposition"]
PLACE_KINDS = ["", "county", "city", "metro"]
TONES = [-1, 0, 1]
STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico",
}
NAME_TO_CODE = {v.lower(): k for k, v in STATES.items()}

# The words that draw the labeled set's first half: a story whose title or summary holds one is a candidate for the
# friction classes, which are rare (about 7 percent of the corpus holds any of these words, session 3400).
OPPOSITION_WORDS = ["moratorium", "lawsuit", "sues", "sued", "protest", "oppos", "denied", "denies", "reject", "zoning",
                    "residents", "rate case", "backlash", "halt", "block", "petition", "hearing", "ban ", "appeal",
                    "court", "complaint", "nimby", "pushback", "fight", "challenge", "referendum", "council", "county",
                    "permit", "objection", "veto"]

SYSTEM = """You classify energy news stories for the Energy Research Warehouse (ERW), the live, citable record of the US energy system, for its Attention Index (how much coverage a sector or a place gets) and its Friction Index (how much of that coverage reports opposition). For each story you get an id, a title and a summary of a sentence or two; there is no body. Answer only from that text. Never guess a place, a state or an opposition the text does not state or clearly imply (ERCOT implies Texas; CAISO implies California; PJM or MISO alone implies no one state).

Fields, one result per story, in the input's order; i is the story's number in the input, unchanged. The keys are short: s is the sector, us, st the state, pl the place, pk the place kind, op opposition, k the kind of opposition, t the tone.
- s (sector): what the story is mainly about. datacenters: data center power demand, siting, large loads, AI's electricity. transmission: power lines, grid operators' planning, interconnection queues, grid reliability. gas: natural gas pipelines, gas-fired plants, gas prices and supply. nuclear: nuclear plants, small modular reactors, nuclear fuel and uranium. solar_wind: solar or wind generation and their supply chains. storage: batteries, pumped hydro, long-duration storage. oil_lng: crude oil, refining, fuels, LNG export and import. other_energy: coal, hydrogen, geothermal, hydro, electricity or utility rates in general, energy policy or companies with no one sector above, EVs and transport fuel. not_energy: not about energy or electricity at all.
- us: true when the story is about the United States (a US place, a US company's US project, a federal or state action), false otherwise.
- st (state): the two-letter postal code of the one US state the story is mainly about; "" when none, several, or not US. DC for the District of Columbia.
- pl (place): the county, city or metro the text names as the place of the project or dispute, as written ("Loudoun County", "Phoenix", "Northern Virginia"); "" when none.
- pk (place kind): county, city or metro for a named place; "" when pl is "".
- op (opposition): true when the story reports opposition to an energy or data center project, plant, line, pipeline, policy, permit, lease or rate: a moratorium or ban, a lawsuit or court challenge, a protest or residents' organized resistance, a permit or approval denied, withdrawn or revoked, a fight over rates or who pays, a vote or official stand against, a regulator's rejection. Opposition anywhere in the world counts (then us is false). A story about prices, markets, earnings, a deal, a technology, or a project moving ahead with no one against it is false. A government acting against a foreign state (sanctions, tariffs) is not opposition to a project.
- k (kind): when op is true, its main kind. moratorium: a moratorium, ban or pause imposed by a government. lawsuit: a suit, appeal, court ruling or legal challenge. protest: protests, petitions, organized residents' resistance, hearings packed against. permit_denied: a permit, rezoning, license or approval denied, withdrawn, revoked or recommended against. rate_case: a fight over rates, bills, tariffs or cost allocation before a regulator or legislature. political_opposition: elected officials or a government opposing, vetoing or blocking a project or policy, a bill against it. other_opposition: any other. "none" when opposition is false.
- t (tone): the story's tone toward the project, sector or actor it is mainly about: -1 negative (setback, harm, failure, conflict, delay, cancellation, loss), 0 neutral or mixed (a report, a price move, a filing, a forecast), 1 positive (approval, completion, growth, a deal done, a record, a success)."""

# Session 3401: the answer's keys are short and the story is named by its place in the batch (i), because the output
# tokens were three quarters of a call's cost with the long keys and the 22-character ids (the trial of 6 November
# 2026: 67 output tokens a story on Sonnet 5.5). KEYS maps them back; nothing else about the answer changed.
KEYS = {"i": "i", "s": "sector", "us": "us", "st": "state", "pl": "place", "pk": "place_kind", "op": "opposition",
        "k": "kind", "t": "tone"}
SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "i": {"type": "integer"},
                    "s": {"type": "string", "enum": SECTORS},
                    "us": {"type": "boolean"},
                    "st": {"type": "string"},
                    "pl": {"type": "string"},
                    "pk": {"type": "string", "enum": PLACE_KINDS},
                    "op": {"type": "boolean"},
                    "k": {"type": "string", "enum": KINDS},
                    "t": {"type": "integer", "enum": TONES},
                },
                "required": ["i", "s", "us", "st", "pl", "pk", "op", "k", "t"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}

FIELDS = ["sector", "us", "state", "place", "place_kind", "opposition", "kind", "tone"]


def nodash(text):
    """The ERW writes no em or en dash in any file: model text is normalised."""
    return " ".join(str(text).replace(chr(0x2014), " - ").replace(chr(0x2013), " - ").split()) if text else ""


def norm_state(s):
    """A two-letter code of STATES, or the code of a state written in words, else ""."""
    s = (s or "").strip()
    if not s:
        return ""
    u = s.upper()
    if u in STATES:
        return u
    if u.startswith("US-") and u[3:] in STATES:
        return u[3:]
    return NAME_TO_CODE.get(s.lower(), "")


def norm_row(r):
    """One result normalised: every enum checked, the state a code or empty, the kind "none" without opposition, the
    place kind empty without a place. Nothing is guessed: a value outside the vocabulary is emptied or set to the
    neutral value, and the row says so in `fixed`."""
    fixed = []
    sector = str(r.get("sector", "")).strip().lower()
    if sector not in SECTORS:
        fixed.append(f"sector:{sector}")
        sector = "other_energy"
    us = r.get("us")
    if not isinstance(us, bool):
        fixed.append(f"us:{us}")
        us = str(us).strip().lower() in ("true", "yes", "1")
    state = norm_state(r.get("state", ""))
    if (r.get("state") or "").strip() and not state:
        fixed.append(f"state:{r.get('state')}")
    if not us and state:
        fixed.append(f"state_without_us:{state}")
        state = ""
    place = nodash(r.get("place", ""))[:80]
    place_kind = str(r.get("place_kind", "")).strip().lower()
    if place_kind not in PLACE_KINDS:
        fixed.append(f"place_kind:{place_kind}")
        place_kind = ""
    if not place:
        place_kind = ""
    opposition = r.get("opposition")
    if not isinstance(opposition, bool):
        fixed.append(f"opposition:{opposition}")
        opposition = str(opposition).strip().lower() in ("true", "yes", "1")
    kind = str(r.get("kind", "none")).strip().lower()
    if kind not in KINDS:
        fixed.append(f"kind:{kind}")
        kind = "other_opposition" if opposition else "none"
    if not opposition:
        kind = "none"
    elif kind == "none":
        fixed.append("kind_none_with_opposition")
        kind = "other_opposition"
    try:
        tone = int(r.get("tone", 0))
    except (TypeError, ValueError):
        tone = 0
        fixed.append(f"tone:{r.get('tone')}")
    if tone not in TONES:
        fixed.append(f"tone:{tone}")
        tone = 0
    return {"sector": sector, "us": us, "state": state, "place": place, "place_kind": place_kind,
            "opposition": opposition, "kind": kind, "tone": tone, "fixed": ";".join(fixed)}


def read_stories(in_dir):
    path = os.path.join(in_dir, "news_stories.csv")
    d = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    d["_when"] = pd.to_datetime(d["event_date"], utc=True, format="ISO8601", errors="coerce")
    return d


def has_opposition_word(title, summary):
    t = f"{title} {summary}".lower()
    return any(w in t for w in OPPOSITION_WORDS)


def draw_sample(d, n, seed):
    """n stories: half from those whose text holds an opposition word, half from the rest; random.Random(seed) over
    the event ids sorted, so the draw can be made again."""
    hit = d[[has_opposition_word(t, s) for t, s in zip(d["title"], d["summary"])]]
    rest = d[~d.index.isin(hit.index)]
    rng = random.Random(seed)
    a = rng.sample(sorted(hit["event_id"]), min(n // 2, len(hit)))
    b = rng.sample(sorted(rest["event_id"]), n - len(a))
    ids = set(a) | set(b)
    s = d[d["event_id"].isin(ids)].sort_values("event_date")
    s = s.assign(drawn_from=["opposition_words" if i in set(a) else "rest" for i in s["event_id"]])
    return s


def items_of(rows):
    """The batch as the model sees it: each story numbered by its place in the batch (i), its title and summary."""
    return [{"i": k, "title": nodash(r.title)[:300], "summary": nodash(r.summary)[:600]} for k, r in enumerate(rows.itertuples())]


def classify_batch(client, model, rows, log):
    """One call: the batch's results by id, normalised, and the call's usage."""
    items = items_of(rows)
    resp = client.messages.create(
        model=model, max_tokens=8000,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": "Stories (JSON):\n" + json.dumps(items, ensure_ascii=False)}])
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason {resp.stop_reason}")
    text = "".join(b.text for b in resp.content if b.type == "text")
    results = json.loads(text)["results"]
    order = [r.event_id for r in rows.itertuples()]
    ids = set(order)
    out = {}
    for r in results:
        try:
            k = int(r.get("i"))
        except (TypeError, ValueError):
            continue
        if 0 <= k < len(order) and order[k] not in out:
            out[order[k]] = norm_row({KEYS.get(a, a): b for a, b in r.items()})
    missing = ids - set(out)
    if missing:
        log(f"  {len(missing)} of {len(ids)} stories had no result in the answer")
    import llm
    usage = llm.usage_numbers(resp.usage)
    return out, usage, getattr(resp, "model", model)


def usd_of(model, usage):
    """The call's cost at the configured prices (warehouse/llm.py), or None for a model not priced."""
    import llm
    return llm.usd(model, usage)


ACCURACY_FIELDS = ["sector", "us", "state", "opposition", "kind", "tone", "place"]


def accuracy(labeled, answers):
    """The model's answers against the hand labels, by field and by class (the test's measure). Returns a dict:
    n (stories in both files), by_field {field: share equal}, by_class {field: {class: {n, recall, precision}}},
    friction {precision, recall, f1} for opposition, sector_index (share of stories whose sector is right among the
    stories the labels put in an index sector), and the disagreements as rows."""
    lab = labeled.set_index("event_id")
    ans = answers.set_index("event_id")
    ids = [i for i in lab.index if i in ans.index]
    rows, by_field, by_class = [], {}, {}

    def norm(v, f):
        if f in ("us", "opposition"):
            return str(v).strip().lower() in ("true", "1", "yes")
        if f == "tone":
            return int(float(v)) if str(v).strip() not in ("", "nan") else 0
        return str(v).strip().lower()

    for f in ACCURACY_FIELDS:
        eq = 0
        classes = {}
        for i in ids:
            a, b = norm(lab.at[i, f], f), norm(ans.at[i, f], f)
            if f == "place":
                a, b = a.replace(",", " ").split()[0] if a else "", b.replace(",", " ").split()[0] if b else ""
            same = a == b
            eq += same
            c = classes.setdefault(str(a), dict(n=0, hit=0, said=0))
            c["n"] += 1
            c["hit"] += same
            classes.setdefault(str(b), dict(n=0, hit=0, said=0))["said"] += 1
            if not same:
                rows.append(dict(event_id=i, field=f, labeled=str(a), model=str(b)))
        by_field[f] = round(eq / len(ids), 4) if ids else None
        by_class[f] = {k: dict(n=v["n"], recall=round(v["hit"] / v["n"], 3) if v["n"] else None,
                               precision=round(v["hit"] / v["said"], 3) if v["said"] else None)
                       for k, v in sorted(classes.items())}
    opp = by_class["opposition"].get("True", dict(n=0, recall=None, precision=None))
    p, r = opp["precision"], opp["recall"]
    f1 = round(2 * p * r / (p + r), 3) if p and r else None
    idx = [i for i in ids if norm(lab.at[i, "sector"], "sector") in INDEX_SECTORS]
    sector_index = round(sum(norm(lab.at[i, "sector"], "sector") == norm(ans.at[i, "sector"], "sector") for i in idx) / len(idx), 4) if idx else None
    return dict(n=len(ids), by_field=by_field, by_class=by_class, friction=dict(precision=p, recall=r, f1=f1, n=opp["n"]),
                sector_index=sector_index, disagreements=rows)


def already_classified(in_dir):
    """The ids the jsonl files and the link table already hold."""
    done = set()
    for p in glob.glob(os.path.join(RAW_DIR, "classified_*.jsonl")):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line)["event_id"])
    path = os.path.join(in_dir, LINKS + ".csv")
    if os.path.exists(path):
        t = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, usecols=["event_id"])
        done |= set(t["event_id"])
    return done


def run_batches(client, model, todo, log, out_path=None, cap_usd=None, max_calls=None):
    """Classify todo in batches; append each call's rows to out_path (jsonl) when given. Returns (rows, usage total,
    usd total, failed calls)."""
    batches = [todo.iloc[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    if max_calls:
        batches = batches[:max_calls]
    log(f"{len(todo)} stories in {len(batches)} calls of up to {BATCH}")
    rows, total, usd, failed = [], dict(input=0, output=0, cache_write=0, cache_read=0), 0.0, 0
    now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for bi, batch in enumerate(batches, 1):
        if cap_usd is not None and usd >= cap_usd:
            log(f"cap USD {cap_usd} reached after {bi - 1} calls: {sum(len(b) for b in batches[bi - 1:])} stories left")
            break
        try:
            out, usage, model_id = classify_batch(client, model, batch, log)
        except Exception as exc:
            failed += 1
            log(f"  call {bi} FAILED ({len(batch)} stories left unclassified): {ip.redact(repr(exc))[:300]}")
            continue
        for k in total:
            total[k] += usage[k]
        c = usd_of(model_id, usage)
        usd += c or 0.0
        got = []
        for r in batch.itertuples():
            if r.event_id in out:
                row = dict(event_id=r.event_id, event_date=r.event_date, source=r.source, source_url=r.source_url,
                           headline=nodash(getattr(r, "headline", "")), significance=getattr(r, "significance", ""),
                           scorer_sector=getattr(r, "sector", ""), **out[r.event_id],
                           model_id=model_id, prompt_version=PROMPT_VERSION, classified_at=now)
                got.append(row)
        rows.extend(got)
        if out_path:
            with open(out_path, "a", encoding="utf-8", newline="\n") as f:
                for row in got:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
        log(f"  call {bi}: {len(batch)} stories, {len(got)} classified; tokens in {usage['input']} (cache read "
            f"{usage['cache_read']}, write {usage['cache_write']}), out {usage['output']}; USD {c if c is not None else 'unknown'}; "
            f"run USD {usd:.4f}")
    return rows, total, usd, failed


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the classification behind the Attention and Friction indices")
    ap.add_argument("--in-dir", default=ip.OUT_DIR, help="where news_stories.csv (and attention_story_links.csv) are read")
    ap.add_argument("--sample", type=int, default=0, help="draw this many stories for hand labeling and write them to --out")
    ap.add_argument("--seed", type=int, default=3400)
    ap.add_argument("--ids", help="classify the stories this CSV lists (event_id) and write the answers to --out")
    ap.add_argument("--out", help="the sample's or the answers' file")
    ap.add_argument("--model", default=ATTENTION_MODEL)
    ap.add_argument("--cap-usd", type=float, help="the corpus run: stop when the run's ledger cost reaches this")
    ap.add_argument("--max-calls", type=int, help="at most this many calls")
    ap.add_argument("--order", choices=["newest", "oldest"], default="newest")
    ap.add_argument("--since", help="the corpus run: only stories published on or after this date (YYYY-MM-DD)")
    ap.add_argument("--all-significance", action="store_true", help="the corpus run: send the stories the news scorer gave significance 0 too")
    ap.add_argument("--log-dir", help="where the run log goes (default warehouse/output/logs)")
    args = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = args.log_dir or ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"{STEP}_{run_id}.log"))
    d = read_stories(args.in_dir)
    log(f"{len(d)} stories read from {args.in_dir}")
    if args.sample:
        s = draw_sample(d, args.sample, args.seed)
        cols = ["event_id", "event_date", "source", "source_url", "title", "summary", "drawn_from"]
        s[cols].to_csv(args.out, index=False, lineterminator="\n")
        print(f"sample of {len(s)} written to {args.out} ({(s['drawn_from'] == 'opposition_words').sum()} from opposition words)")
        log.close()
        return 0
    import llm
    client = llm.client(STEP, log)
    if args.ids:
        want = pd.read_csv(args.ids, dtype=str, keep_default_na=False)["event_id"]
        todo = d[d["event_id"].isin(set(want))].set_index("event_id").loc[[i for i in want if i in set(d["event_id"])]].reset_index()
        rows, total, usd, failed = run_batches(client, args.model, todo, log, max_calls=args.max_calls)
        pd.DataFrame(rows).to_csv(args.out, index=False, lineterminator="\n")
        line = (f"{len(rows)} of {len(todo)} stories classified by {args.model} in {len(todo) // BATCH + 1} calls; tokens "
                f"in {total['input']} (cache read {total['cache_read']}, write {total['cache_write']}), out {total['output']}; "
                f"USD {usd:.4f}; failed calls {failed}; answers in {args.out}")
        log(line)
        print(line)
        log.close()
        return 0 if failed == 0 else 1
    done = already_classified(args.in_dir)
    todo = d[~d["event_id"].isin(done)]
    if args.since:
        todo = todo[todo["_when"] >= pd.Timestamp(args.since, tz="UTC")]
    if not args.all_significance:
        # session 3401: a story the news scorer gave significance 0 ("not energy relevant") is not sent; it stays in
        # its week's denominator as unclassified, and docs/methods/attention.md says so
        zero = todo["significance"].str.strip() == "0"
        log(f"{int(zero.sum())} stories scored 0 by the news scorer are not sent (--all-significance sends them)")
        todo = todo[~zero]
    todo = todo.sort_values("_when", ascending=(args.order == "oldest"))
    log(f"{len(done)} stories already classified; {len(todo)} to do, {args.order} first")
    os.makedirs(RAW_DIR, exist_ok=True)
    out_path = os.path.join(RAW_DIR, f"classified_{run_id}.jsonl")
    rows, total, usd, failed = run_batches(client, args.model, todo, log, out_path=out_path, cap_usd=args.cap_usd,
                                           max_calls=args.max_calls)
    left = len(todo) - len(rows)
    line = (f"{len(rows)} stories classified by {args.model}; {left} left unclassified; tokens in {total['input']} "
            f"(cache read {total['cache_read']}, write {total['cache_write']}), out {total['output']}; USD {usd:.4f}; "
            f"failed calls {failed}; rows in {out_path}")
    log(line)
    print(line)
    log.close()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
