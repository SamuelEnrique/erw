#!/usr/bin/env python3
"""Draw a findings draft's chart again from its own card and its own sentence (session 9820, desktop window 4).

Energy Research Warehouse (ERW). The audit of 19 November 2026 (chain 506, docs/reviews/findings-audit-2026-11-19.md)
mended the sentence of 76 drafts in wording only; the line under each chart's title is the sentence, drawn into the
PNG, so those pictures kept the old words. This script draws a draft's picture again:

  - the card is the draft's own row of public.scanner_drafts (read only, through SUPABASE_DB_URL, cached in
    runs/findings_charts/cards.json), the chart's points, title and source line exactly as the builder stored them;
  - the line under the title is the sentence the draft's .md says now ("**The finding.** ...");
  - before it writes, every figure the picture carries is set against the draft's own files: the marked point and the
    reference line against the CSV's last and first full years, every point of the line against the CSV, and the
    sentence's two figures against the card's numbers as the builder rounds them. A mismatch writes nothing.

Nothing here approves, posts or sends a draft, and nothing writes to Supabase: the row keeps its card; only the
picture under docs/findings/ is drawn again. No number is computed here.

    python redraw.py fetch                      read every docs/findings draft's card into the cache
    python redraw.py draw <family>/<slug> ...   draw each again (writes docs/findings/<family>/<slug>.png)
    python redraw.py check <family>/<slug> ...  the checks only, nothing written
"""

import csv
import io
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FINDINGS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(FINDINGS, "..", "..", ".."))
sys.path.insert(0, FINDINGS)
DOCS = os.environ.get("ERW_FINDINGS_DOCS") or os.path.join(ROOT, "docs", "findings")   # another checkout's docs/findings, when set
CACHE = os.path.join(ROOT, "runs", "findings_charts", "cards.json")


def env(name, env_file=None):
    """A setting from the environment, else from the .env file named (or ERW_ENV_FILE, or the repository's .env)."""
    if os.environ.get(name):
        return os.environ[name]
    path = env_file or os.environ.get("ERW_ENV_FILE") or os.path.join(ROOT, ".env")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def drafts():
    """{"family/slug": draft id} of every draft under docs/findings/ (the id is on the .md's second paragraph)."""
    out = {}
    for fam in sorted(os.listdir(DOCS)):
        d = os.path.join(DOCS, fam)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".md") and not name.startswith("README"):
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    m = re.search(r"Draft `(scan-deep-[0-9a-f]+)`", f.read())
                if m:
                    out[f"{fam}/{name[:-3]}"] = m.group(1)
    return out


def fetch():
    """Read the cards of every draft from public.scanner_drafts, read only, into the cache."""
    import psycopg
    url = env("SUPABASE_DB_URL")
    if not url:
        raise SystemExit("FAILED: SUPABASE_DB_URL is not set (the environment, ERW_ENV_FILE or .env)")
    want = drafts()
    ids = sorted(set(want.values()))
    with psycopg.connect(url, autocommit=False) as con:
        con.execute("set transaction read only")
        rows = con.execute("select id, state, card from public.scanner_drafts where id = any(%s)", (ids,)).fetchall()
        con.rollback()
    got = {r[0]: {"state": r[1], "card": r[2]} for r in rows}
    cache = {key: dict(id=did, **got[did]) for key, did in want.items() if did in got}
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cache, f, ensure_ascii=False, indent=0)
    missing = [k for k, did in want.items() if did not in got]
    print(f"{len(want)} drafts under docs/findings, {len(cache)} cards read, {len(missing)} with no row: {', '.join(missing[:10])}")
    states = {}
    for v in cache.values():
        states[v["state"]] = states.get(v["state"], 0) + 1
    print("states:", states)
    return 0


def sentence_of(md_text):
    m = re.search(r"\*\*The finding\.\*\* (.+)", md_text)
    if not m:
        raise ValueError("no '**The finding.**' line")
    return m.group(1).strip()


def csv_rows(path):
    with open(path, encoding="utf-8") as f:
        body = "".join(line for line in f if not line.startswith("#"))
    return list(csv.DictReader(io.StringIO(body)))


def fmt(v, nd):
    import findings_common as common
    return common.fmt(v, nd)


def check(key, card, sentence):
    """Every figure the picture carries, set against the draft's own CSV and sentence. Returns a list of faults."""
    fam, s = key.split("/", 1)
    faults = []
    ch = card["chart"]
    nd = ch.get("decimals", 2)
    rows = csv_rows(os.path.join(DOCS, fam, f"{s}.csv"))
    near = lambda a, b: a is not None and b is not None and abs(float(a) - float(b)) <= 1e-6 * max(1.0, abs(float(b)))   # noqa: E731
    if "event_year" in (rows[0] if rows else {}):
        # an event: the CSV holds each year's highest hour of the window; the chart the event year's days and the
        # other years' mean by day. The marked point is the event year's row and the day line's highest point.
        ev = [r for r in rows if str(r["event_year"]).strip() in ("1", "1.0")]
        num = card.get("numbers") or {}
        m = ch.get("mark") or {}
        if len(ev) != 1 or not near(m.get("value"), ev[0]["value"]):
            faults.append(f"the marked point {m.get('value')} is not the CSV's event year {[r['value'] for r in ev]}")
        day = [v for v in ch["series"][0]["values"] if v is not None]
        if not day or not near(max(day), m.get("value")):
            faults.append("the marked point is not the highest of the event year's days")
        others = [float(r["value"]) for r in rows if r not in ev]
        if others and not near(sum(others) / len(others), num.get("mean_other")):
            faults.append(f"the mean of the other years {sum(others) / len(others)} is not the card's {num.get('mean_other')}")
        for v in (m.get("value"), num.get("mean_other")):
            if v is not None and fmt(v, nd) not in sentence:
                faults.append(f"the sentence does not carry {fmt(v, nd)}")
        return faults
    if "filing" in (rows[0] if rows else {}):
        # a tariff measure: the CSV holds one row a filing, lowest to highest; the chart each filing, the median line
        vals = sorted(float(r["value"]) for r in rows)
        got = [float(v) for v in ch["series"][0]["values"]]
        if got != vals:
            faults.append(f"the chart's filings {got} are not the CSV's {vals}")
        m = ch.get("mark") or {}
        if not near(m.get("value"), max(vals)):
            faults.append(f"the marked point {m.get('value')} is not the highest filing {max(vals)}")
        import statistics
        refs = ch.get("ref_lines") or []
        if refs and not near(refs[0]["value"], statistics.median(vals)):
            faults.append(f"the median line {refs[0]['value']} is not the CSV's median {statistics.median(vals)}")
        for v in (statistics.median(vals), min(vals), max(vals)):
            if fmt(v, nd) not in sentence:
                faults.append(f"the sentence does not carry {fmt(v, nd)}")
        return faults
    full = {str(r["year"]): float(r["value"]) for r in rows if str(r.get("full_year", "1")).strip() in ("1", "1.0", "True")}
    x = [str(v) for v in ch["x"]]
    vals = ch["series"][0]["values"]
    for y, v in zip(x, vals):
        if y not in full:
            faults.append(f"the chart's year {y} is not a full year of the CSV")
        elif v is None or abs(float(v) - full[y]) > 1e-6 * max(1.0, abs(full[y])):
            faults.append(f"{y}: the chart has {v}, the CSV {full[y]}")
    if sorted(full) != sorted(x):
        faults.append(f"full years differ: chart {x[0]} to {x[-1]} ({len(x)}), CSV {len(full)}")
    m = ch.get("mark") or {}
    last, first = x[-1], x[0]
    if str(m.get("x")) != last or abs(float(m["value"]) - full.get(last, math.nan)) > 1e-6 * max(1.0, abs(full.get(last, 1.0))):
        faults.append(f"the marked point {m.get('x')} {m.get('value')} is not the last full year {last} {full.get(last)}")
    refs = ch.get("ref_lines") or []
    if not refs or refs[0]["name"] != first or abs(float(refs[0]["value"]) - full.get(first, math.nan)) > 1e-6 * max(1.0, abs(full.get(first, 1.0))):
        faults.append(f"the reference line {refs[:1]} is not the first full year {first} {full.get(first)}")
    num = card.get("numbers") or {}
    for k, yr in (("last", last), ("first", first)):
        shown = fmt(num.get(k, full.get(yr)), nd)
        if f"{shown} " not in sentence and f"{shown}," not in sentence:
            faults.append(f"the sentence does not carry the {k} figure {shown}")
        if str(yr) not in sentence:
            faults.append(f"the sentence does not name the year {yr}")
    return faults


def draw(keys, write=True, preview=None):
    """preview: a folder to draw into instead of docs/findings/ (to look before writing)."""
    import card_image
    with open(CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    bad = 0
    for key in keys:
        key = key.replace("\\", "/").removesuffix(".png").removesuffix(".md")
        fam, s = key.split("/", 1)
        if key not in cache:
            print(f"{key}: NOT DRAWN, no card in the cache")
            bad += 1
            continue
        card = cache[key]["card"]
        with open(os.path.join(DOCS, fam, f"{s}.md"), encoding="utf-8") as f:
            sentence = sentence_of(f.read())
        try:
            faults = check(key, card, sentence)
        except Exception as exc:     # a draft whose files do not read is not drawn
            faults = [f"{type(exc).__name__}: {exc}"]
        if faults:
            print(f"{key}: NOT DRAWN: " + "; ".join(faults))
            bad += 1
            continue
        old = card.get("subtitle", "")
        if write:
            out = os.path.join(preview, key.replace("/", "__") + ".png") if preview else os.path.join(DOCS, fam, f"{s}.png")
            card_image.render(card, out, "linkedin_wide", fact=sentence)
            if card_image.WARNINGS:
                print(f"{key}: WARNING: " + "; ".join(card_image.WARNINGS))
        print(f"{key}: {'drawn' if write else 'checked'}; figures agree; sentence {'changed' if old != sentence else 'as the card'}")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("fetch", "draw", "check", "preview"):
        sys.exit(__doc__)
    if sys.argv[1] == "fetch":
        sys.exit(fetch())
    if sys.argv[1] == "preview":
        sys.exit(draw(sys.argv[2:], preview=os.path.join(ROOT, "runs", "findings_charts", "preview")))
    sys.exit(draw(sys.argv[2:], write=sys.argv[1] == "draw"))
