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


def exact(key, card):
    """The card with its line, its marked point and its reference line read again from the draft's CSV at full
    precision. The card holds them rounded to six decimals; 28.424999999999997 became 28.425, and the picture printed
    28.43 where the sentence, written from the CSV, says 28.42 (gas/s2s-in-s2in-alabama). An event's or a tariff's
    chart is not a year series and is left as stored."""
    import copy
    fam, s = key.split("/", 1)
    rows = csv_rows(os.path.join(DOCS, fam, f"{s}.csv"))
    if not rows or "year" not in rows[0] or "event_year" in rows[0]:
        return card
    full = {str(r["year"]): float(r["value"]) for r in rows if str(r.get("full_year", "1")).strip() in ("1", "1.0", "True")}
    card = copy.deepcopy(card)
    ch = card["chart"]
    x = [str(v) for v in ch["x"]]
    if not all(y in full for y in x) or len(ch["series"]) != 1:
        return card
    ch["series"][0]["values"] = [full[y] for y in x]
    if ch.get("mark") and str(ch["mark"].get("x")) in full:
        ch["mark"]["value"] = full[str(ch["mark"]["x"])]
    for r in ch.get("ref_lines") or []:
        if str(r.get("name")) in full:
            r["value"] = full[str(r["name"])]
    return card


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
    import card_image
    for what, v in (("the marked figure", m.get("value")), ("the reference line's figure", refs[0]["value"] if refs else None)):
        drawn = card_image._num(v, nd) if v is not None else None     # the figure exactly as the picture prints it
        if drawn is not None and drawn not in sentence:
            faults.append(f"{what} as drawn, {drawn}, is not in the sentence")
    num = card.get("numbers") or {}
    for k, yr in (("last", last), ("first", first)):
        shown = fmt(num.get(k, full.get(yr)), nd)
        if f"{shown} " not in sentence and f"{shown}," not in sentence:
            faults.append(f"the sentence does not carry the {k} figure {shown}")
        if str(yr) not in sentence:
            faults.append(f"the sentence does not name the year {yr}")
    return faults


def diagnose(key, card, sentence, old_module):
    """What the picture as drawn before had wrong, measured, not guessed: the card rendered again by the old drawing
    code (old_module, the card_image.py the picture was drawn with), its artists read back. Returns a list of faults in
    words."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import card_image
    got = {}
    real_close = plt.close
    plt.close = lambda fig=None: got.setdefault("fig", fig)
    try:
        old_module.render(card, os.path.join(ROOT, "runs", "findings_charts", "old.png"), "linkedin_wide", fact=card.get("subtitle", ""))
    finally:
        plt.close = real_close
    fig = got["fig"]
    r = fig.canvas.get_renderer()
    ax = fig.axes[0]
    W, H = fig.get_size_inches() * fig.dpi
    out = []
    md_sentence = sentence
    if card.get("subtitle", "").strip() != md_sentence.strip():
        out.append("the line under the title still had the sentence's old words")
    series = [ln for ln in ax.get_lines() if len(ln.get_xdata()) > 2 or (len(ln.get_xdata()) == 2 and list(ln.get_xdata()) != [0, 1])]
    pts = []
    for ln in series:
        xd = [float(v) for v in ax.convert_xunits(ln.get_xdata())]
        pts.append([tuple(ln.get_transform().transform((a, float(b)))) for a, b in zip(xd, ln.get_ydata())])
    ch = card["chart"]
    for t in ax.texts:
        bb = t.get_window_extent(r)
        rect = (bb.x0, bb.y0, bb.x1, bb.y1)
        if any(card_image._segments_hit(rect, p) for p in pts):
            txt = t.get_text()
            kind = "the first year's label" if ":" in txt else "the marked figure"
            out.append(f"{kind} ({txt}) sat on the line")
    leg = ax.get_legend()
    if leg is not None:
        bb = leg.get_window_extent(r)
        if any(card_image._segments_hit((bb.x0, bb.y0, bb.x1, bb.y1), p) for p in pts):
            out.append("the legend sat over the data")
        else:
            out.append("a legend where the brand file names each series on its line")
    lo, hi = ax.get_ylim()
    if lo < 0 < hi:
        out.append("no ink zero line (docs/brand.md, section 6), though zero is on the scale")
    years = card_image._years(ch["x"])
    if years and any(b - a > 1 for a, b in zip(years, years[1:])):
        miss = sorted(set(range(years[0], years[-1] + 1)) - set(years))
        out.append(f"missing years ({', '.join(map(str, miss[:6]))}{' ...' if len(miss) > 6 else ''}) drawn as if one year apart")
    labels = [t.get_text() for t in ax.get_xticklabels() if t.get_text()]
    if years and str(ch["x"][-1]) not in labels:
        out.append(f"the marked year {ch['x'][-1]} had no label on the axis")
    m = ch.get("mark") or {}
    if m.get("value") is not None and old_module._num(m["value"], ch.get("decimals", 2)) not in md_sentence and not key.startswith("events/"):
        out.append(f"the marked figure printed {old_module._num(m['value'], ch.get('decimals', 2))} where the sentence says otherwise (the card's value rounded to six decimals)")
    for t in fig.texts:
        bb = t.get_window_extent(r)
        if bb.x1 > W - 2 or t.get_text().endswith(" ..."):
            out.append(f"text cut off: {t.get_text()[:50]}")
    if any(t.get_text().endswith(" ...") for t in ax.texts):
        out.append("a label cut off")
    real_close(fig)
    return out


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
            card = exact(key, card)
            faults = check(key, card, sentence)
        except Exception as exc:     # a draft whose files do not read is not drawn
            faults = [f"{type(exc).__name__}: {exc}"]
        if faults:
            print(f"{key}: NOT DRAWN: " + "; ".join(faults))
            bad += 1
            continue
        old = card.get("subtitle", "")
        if write and os.environ.get("ERW_OLD_CARD_IMAGE"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("card_image_old", os.environ["ERW_OLD_CARD_IMAGE"])
            old_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(old_mod)
            faults = diagnose(key, cache[key]["card"], sentence, old_mod)
            with open(os.path.join(ROOT, "runs", "findings_charts", "rows.jsonl"), "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"key": key, "wrong": faults, "mark": card_image._num(card["chart"]["mark"]["value"], card["chart"].get("decimals", 2))
                                    if (card["chart"].get("mark") or {}).get("value") is not None else None}, ensure_ascii=False) + "\n")
        if write:
            out = os.path.join(preview, key.replace("/", "__") + ".png") if preview else os.path.join(DOCS, fam, f"{s}.png")
            before = open(out, "rb").read() if os.path.exists(out) else b""
            card_image.render(card, out, "linkedin_wide", fact=sentence)
            if os.environ.get("ERW_OLD_CARD_IMAGE"):
                with open(os.path.join(ROOT, "runs", "findings_charts", "rows.jsonl"), "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps({"key": key, "changed": open(out, "rb").read() != before, "warnings": list(card_image.WARNINGS)}) + "\n")
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
