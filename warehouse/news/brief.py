#!/usr/bin/env python3
"""Write the Energy Digest: docs/digest/YYYY-MM-DD.md and docs/digest/latest.md.

Energy Research Warehouse (ERW), platform tool 1. Takes the stories scored in
the last 24 hours (by publish time), groups them into clusters (cluster_id
from warehouse/news/score.py), ranks clusters by their highest significance
and writes a markdown brief titled "Energy Digest" with the date.

    python warehouse/news/brief.py
    python warehouse/news/brief.py --hours 24 --date 2026-09-25
    python warehouse/news/brief.py --out docs/digest/checks/2026-09-26T1600Z.md   # a check run

--out (session 13) writes the digest to that path only: the day's digest and
latest.md are left as they are, so a check run later in the day never
overwrites the digest the daily run published.

Session 23: the digest is written Monday to Friday only. For a Saturday or
Sunday digest date it writes nothing and prints "news_brief SKIPPED: no weekend
issue", unless --weekend is given; the weekend's stories open Sunday's Energy
Roundup (warehouse/news/roundup.py). The digest's last section is the Fun fact
(warehouse/news/funfact.py writes the day's item; it is re-verified here, and a
digest whose fact fails ships without one).

Who writes what: the model writes only the plain headlines (one call, JSON
schema). The why lines, MW, prices and parties are the stories' own scored
fields. Every number under "Numbers today" is read from the warehouse through
the erw package, with its table cited; a number the warehouse does not hold
is reported as missing, never filled.

Sector groups (model sector -> section):
  Power                   power_prices, generation, grid_conditions, transmission,
                          interconnection, storage, datacenter_power, ppa
  Oil and gas             oil, gas, lng, geopolitics
  Nuclear and renewables  nuclear, renewables, hydrogen
  Policy                  policy, then the policy actions of the window scored 5 or more (session 24)
  Capital and companies   capital, deal, company
  (transport and other appear only in the top 10)

Main hub per ISO for the day-ahead average (yesterday = the ISO's own local
operating day before the digest date): ERCOT HB_NORTH, CAISO TH_SP15_GEN-APND,
NYISO N.Y.C. (zone J), MISO INDIANA.HUB, SPP SPPSOUTH_HUB, ISO-NE
.H.INTERNAL_HUB. PJM has no price table (no API key).
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import traceback
from types import SimpleNamespace

import anthropic
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "package", "src"))
import erw  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "chat"))
import ask as chat_ask  # noqa: E402  session 21: the chat's literal-number check (numbers, unverified)
import iso_prices as ip  # noqa: E402
from ingest import NAME, NEWS_COLS  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
from voice import VOICE_NOTE  # noqa: E402  session 25: docs/voice.md in every writer's system prompt
import llm  # noqa: E402  session 30: every Anthropic call goes through the cost ledger

from score import PRICES, nodash, pick_model  # noqa: E402

DIGEST_DIR = os.path.join(ROOT, "docs", "digest")
GROUPS = {
    "Power": ["power_prices", "generation", "grid_conditions", "transmission", "interconnection",
              "storage", "datacenter_power", "ppa"],
    "Oil and gas": ["oil", "gas", "lng", "geopolitics"],
    "Nuclear and renewables": ["nuclear", "renewables", "hydrogen"],
    # session 24: policy is its own group, with the day's scored policy actions (policy_actions) under its stories
    "Policy": ["policy"],
    "Capital and companies": ["capital", "deal", "company"],
}
MAIN_HUBS = [  # (label, table, node, local tz); session 30: the consolidated tables by their own names
    ("ERCOT", "iso_dam_hub_prices", "HB_NORTH", "America/Chicago"),
    ("CAISO", "iso_dam_hub_prices", "TH_SP15_GEN-APND", "America/Los_Angeles"),
    ("NYISO", "nyiso_dam_zone_prices", "N.Y.C.", "America/New_York"),
    ("MISO", "iso_dam_hub_prices", "INDIANA.HUB", "EST"),
    ("SPP", "iso_dam_hub_prices", "SPPSOUTH_HUB", "America/Chicago"),
    ("ISO-NE", "isone_dam_zone_prices", ".H.INTERNAL_HUB", "America/New_York"),
]
# session 30: the partition of a consolidated table each main hub is read from (docs/migrations/2026-09-29-consolidation.md)
HUB_MARKET = {"ERCOT": "ercot_dam", "CAISO": "caiso_dam", "MISO": "miso_dam", "SPP": "spp_dam"}
RT_TZ = {"ercot": "America/Chicago", "caiso": "America/Los_Angeles", "nyiso": "America/New_York",
         "miso": "EST", "spp": "America/Chicago", "isone": "America/New_York"}
FUELS = [("Henry Hub natural gas", "eia:henry_hub"), ("WTI Cushing crude", "eia:wti_cushing"),
         ("Brent crude", "eia:brent")]

HEADLINE_SYSTEM = """You write plain news headlines for the Energy Digest of the Energy Research Warehouse (ERW).
For each cluster, write one headline of at most 14 words that states what happened, in plain words, no hype, no
clickbait, no question marks. Use only facts and words present in the cluster's titles and summaries; do not add
numbers, names, descriptors or claims (if a title is only an identifier, say only what it literally is). Do not
mention AI, artificial intelligence, datacenters, data centers or compute unless the cluster's own titles or
summaries do. Return every cluster id exactly once.
When a cluster lists figures (MW, prices, dollar amounts, percentages from its scored fields), the headline must carry
at least one of them, written as given. Never write a number that is not in the cluster's titles, summaries or
figures.""" + VOICE_NOTE
HEADLINE_SCHEMA = {
    "type": "object",
    "properties": {"headlines": {"type": "array", "items": {
        "type": "object",
        "properties": {"cluster_id": {"type": "string"}, "headline": {"type": "string"}},
        "required": ["cluster_id", "headline"], "additionalProperties": False}}},
    "required": ["headlines"], "additionalProperties": False,
}


def build_clusters(stories):
    rows = []
    for cid, g in stories.groupby("cluster_id"):
        g = g.sort_values(["sig", "event_date"], ascending=[False, True])
        lead = g.iloc[0]
        rows.append({
            "cluster_id": cid, "sig": int(g["sig"].max()), "ai": int(g["ai"].max()),
            # session 21: the MW and price of the cluster are the first any of its stories' scored fields hold
            "sector": lead["sector"], "why": lead["why"], "mw": next((x for x in g["mw"] if x), ""),
            "price": next((x for x in g["price_mentioned"] if x), ""), "parties": lead["parties"],
            "first": g["event_date"].min(), "n": len(g),
            "links": [(r.source, r.source_url) for r in g.itertuples()][:3],
            "titles": list(g["title"])[:4], "summary": lead["summary"][:300],
        })
    c = pd.DataFrame(rows)
    return c.sort_values(["sig", "ai", "n", "first"], ascending=[False, False, False, True]).reset_index(drop=True)


FIGURE = re.compile(r"(?:US\$|\$|USD ?)[\d,.]+(?: ?(?:billion|million|bn|mn|m|b)\b)?|"
                    r"[\d,.]*\d ?(?:%|percent\b|GW\b|MW\b|GWh\b|MWh\b|bcf\b|Bcf\b|mtpa\b)|"
                    r"[\d,.]*\d (?:billion|million) (?:dollars|USD|euros)")


def rt_parts():
    """Session 30: (iso, table, market) for every real-time interval price table; the consolidated
    iso_rtm_hub_prices is read one ISO at a time (its markets, from the coverage table). market is None for a
    table of one ISO."""
    cov = erw.coverage().set_index("table")
    out = []
    for table in erw.filter(market="rtm"):
        if not re.fullmatch(r"[a-z]+_rtm_(hub|zone)_prices(_hourly)?", table):
            continue
        if table.startswith("iso_"):
            for m in sorted(x for x in str(cov.loc[table, "market"]).split(";") if x.endswith("_rtm")):
                out.append((m.split("_")[0], table, m))
        else:
            out.append((table.split("_")[0], table, None))
    return out


def figures(r):
    """Session 21: the figures in a cluster's scored fields: the MW, the price mentioned, and the MW, price,
    dollar and percent figures in its scored reason (the why line)."""
    out = []
    if r.get("mw"):
        out.append(f"{float(r['mw']):,.0f} MW")
    if r.get("price"):
        out.append(str(r["price"]))
    out += [m.group(0).strip() for m in FIGURE.finditer(r.get("why") or "")]
    return list(dict.fromkeys(x for x in out if x))


def headlines(client, model, clusters, log):
    """Headlines for the clusters (session 21: using a scored figure where one exists), each checked with
    the chat's literal-number check against the cluster's titles, summary, why line and figures; the clusters
    that fail are asked again once, with the stray numbers named; a second failure stops the brief."""
    recs = {r["cluster_id"]: r for r in clusters.to_dict("records")}
    items = [{"cluster_id": cid, "titles": r["titles"], "summary": r["summary"], "figures": figures(r)}
             for cid, r in recs.items()]
    heads, usage, calls = _headline_call(client, model, items, log)
    pool = lambda r: [*r["titles"], r["summary"], r["why"] or "", *figures(r)]  # noqa: E731
    bad = {cid: chat_ask.unverified(h, pool(recs[cid])) for cid, h in heads.items() if cid in recs}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        log(f"  headlines: {len(bad)} with numbers not in their cluster: {bad}; asking again once")
        again = [dict(x, stray_numbers=bad[x["cluster_id"]]) for x in items if x["cluster_id"] in bad]
        h2, u2, c2 = _headline_call(client, model, again, log)
        usage = SimpleNamespace(input_tokens=usage.input_tokens + u2.input_tokens,
                                output_tokens=usage.output_tokens + u2.output_tokens)
        calls += c2
        still = {cid: chat_ask.unverified(h, pool(recs[cid])) for cid, h in h2.items() if cid in bad}
        still = {k: v for k, v in still.items() if v}
        if still:
            raise RuntimeError(f"headlines still carry numbers not in their clusters: {still}")
        heads.update({k: v for k, v in h2.items() if k in bad})
    return heads, usage, calls


def _headline_call(client, model, items, log):
    # session 30 (B2): the system prompt is cached, so a retry (and the Roundup's call soon after) reads it
    kwargs = dict(model=model, max_tokens=8000,
                  system=[{"type": "text", "text": HEADLINE_SYSTEM, "cache_control": {"type": "ephemeral"}}],
                  output_config={"effort": "low", "format": {"type": "json_schema", "schema": HEADLINE_SCHEMA}},
                  messages=[{"role": "user", "content": json.dumps(items, ensure_ascii=False)}])
    calls = 0
    try:
        calls += 1
        resp = client.messages.create(extra_body={"temperature": 0}, **kwargs)
    except anthropic.BadRequestError as exc:
        if "temperature" not in str(exc).lower():
            raise
        log(f"  {model} rejects temperature ({ip.redact(str(exc))[:120]}); retrying without it")
        calls += 1
        resp = client.messages.create(**kwargs)
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"headline call stop_reason {resp.stop_reason}")
    out = json.loads(next(b.text for b in resp.content if b.type == "text"))["headlines"]
    u = resp.usage
    return {h["cluster_id"]: nodash(h["headline"]) for h in out}, SimpleNamespace(
        input_tokens=u.input_tokens, output_tokens=u.output_tokens), calls


def norm_headline(h):
    return re.sub(r"[^a-z0-9 ]+", "", h.lower()).strip()


def unique_items(sections, heads, log):
    """Session 21, ruling 5: the digest once showed the same event twice with identical wording, because
    each section chose its clusters on its own, so a top-10 cluster came back under By sector and AI and
    power. The sections now take distinct clusters; this also drops a later cluster whose headline, once
    normalized, or first source link repeats an earlier item's (the same event in two clusters).
    Returns the sections with the repeats removed."""
    seen_h, seen_u, out = set(), set(), {}
    for name, df in sections.items():
        keep = []
        for r in df.to_dict("records"):
            h, urls = norm_headline(heads[r["cluster_id"]]), [u for _, u in r["links"]]
            if h in seen_h or (urls and urls[0] in seen_u):
                log(f"  dropped a repeat in {name}: {heads[r['cluster_id']]!r} ({r['cluster_id']})")
                continue
            seen_h.add(h)
            seen_u.update(urls)
            keep.append(r["cluster_id"])
        out[name] = df[df["cluster_id"].isin(keep)]
    return out


def assert_unique(lines):
    """The hard check (ruling 5): no two items of a brief share a normalized headline or a source URL.
    Raises, so a brief that fails it is not written."""
    heads, urls = [], []
    for ln in lines:
        m = re.match(r"^(?:\d+\. \*\*(.+?)\*\*|- (.+?) \()", ln)
        if m and not ln.startswith("- no "):  # "- no scored story in this group today" is not an item
            heads.append(norm_headline(m.group(1) or m.group(2)))
            urls += re.findall(r"\]\((https?://[^)]+)\)", ln)
        elif ln.startswith("   ") and "Sources:" in ln:
            urls += re.findall(r"\]\((https?://[^)]+)\)", ln)
    dh = sorted({h for h in heads if heads.count(h) > 1})
    du = sorted({u for u in urls if urls.count(u) > 1})
    if dh or du:
        raise RuntimeError(f"duplicate items in the brief: headlines {dh[:3]}, source URLs {du[:3]}")
    return len(heads)


def link_text(links):
    return ", ".join(f"[{src}]({url})" for src, url in links)


def detail(r):
    bits = []
    if r["mw"]:
        bits.append(f"{float(r['mw']):,.0f} MW")
    if r["price"]:
        bits.append(r["price"])
    if r["parties"]:
        bits.append("parties: " + r["parties"])
    return ("; ".join(bits) + ". ") if bits else ""


def mean2(values):
    """The mean of published prices, exact (decimal arithmetic on the values as written) and rounded
    half up to cents: a float mean can land a hair under a half (44.295 read as 44.29499...).
    Session 17; scripts/check-values.mjs rounds the same way."""
    from decimal import Decimal, ROUND_HALF_UP
    vals = [Decimal(repr(float(v))) for v in values]
    return (sum(vals) / len(vals)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Notes:
    """Session 21: each number keeps its table in a short footnote list at the end of its section,
    not inline. ref(table) gives the marker ("[1]"); lines() the list."""

    def __init__(self):
        self.tables, self.extra = [], {}

    def ref(self, table, extra=""):
        if table not in self.tables:
            self.tables.append(table)
        if extra:
            self.extra[table] = extra
        return f"[{self.tables.index(table) + 1}]"

    def lines(self):
        if not self.tables:
            return []
        items = [f"[{i}] {cite_short(t)}" + (f"; {self.extra[t]}" if t in self.extra else "")
                 for i, t in enumerate(self.tables, 1)]
        return ["", "Tables: " + "; ".join(items) + "."]


SUMMARY_SYSTEM = """You write the summary above the numbers section of the ERW's energy brief: two or three plain sentences
saying what the numbers say (for example where power was dearest or cheapest, how prices moved, what stands out).
Use only numbers written in the section, exactly as they are written there: do not compute new numbers (no sums,
differences, ratios or percentages that are not already in the section) and do not round them. No hype, no advice,
no em dashes. Return JSON with the field summary.""" + VOICE_NOTE
SUMMARY_SCHEMA = {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"],
                  "additionalProperties": False}


def section_pool(lines):
    """The section's text for the literal check: without footnote markers and the footnote list."""
    return "\n".join(re.sub(r"\[\d+\]", "", ln) for ln in lines if not ln.startswith("Tables: "))


def numbers_summary(client, model, lines, log):
    """Session 21: a two or three sentence summary of a numbers section, written by the model under the
    chat's literal-number check (every number in it must appear in the section). Regenerated once with
    the violations named; if it still fails, no summary (returns None). Returns (summary, usage list)."""
    pool = section_pool(lines)
    msgs = [{"role": "user", "content": "The numbers section:\n\n" + pool}]
    usages = []
    for attempt in (1, 2):
        kwargs = dict(model=model, max_tokens=1200, messages=msgs,  # session 30 (B2): system cached
                      system=[{"type": "text", "text": SUMMARY_SYSTEM, "cache_control": {"type": "ephemeral"}}],
                      output_config={"effort": "low", "format": {"type": "json_schema", "schema": SUMMARY_SCHEMA}})
        resp = client.messages.create(**kwargs)
        usages.append(resp.usage)
        text = nodash(json.loads(next(b.text for b in resp.content if b.type == "text"))["summary"]).strip()
        bad = chat_ask.unverified(text, [pool])
        if not bad:
            log(f"  numbers summary: attempt {attempt} passed the literal check")
            return text, usages
        log(f"  numbers summary: attempt {attempt} has numbers not in the section: {bad}")
        msgs = msgs + [{"role": "assistant", "content": json.dumps({"summary": text})},
                       {"role": "user", "content": "These numbers are not in the section as written: " + ", ".join(bad)
                        + ". Rewrite the summary using only numbers written in the section."}]
    log("  numbers summary: omitted (failed the literal check twice)")
    return None, usages


def cite_short(table):
    s = erw.sources(table)
    return f"`{table}` ({', '.join(r['source'] for r in s['reports'] if r.get('source'))})"


def numbers_today(digest_date, log):
    notes = Notes()
    lines = ["**Day-ahead average, yesterday, main hub** (mean of the 24 hourly prices of the operating day):", ""]
    lines += ["| ISO | Hub or zone | Operating day | Average USD/MWh | Table |", "|---|---|---|---|---|"]
    for label, table, node, tz in MAIN_HUBS:
        day = pd.Timestamp(digest_date) - pd.Timedelta(days=1)
        start = pd.Timestamp(day.date()).tz_localize(tz)
        end = pd.Timestamp((day + pd.Timedelta(days=1)).date()).tz_localize(tz)
        try:
            df = erw.fetch(table, start=start, end=end, node=node, market=HUB_MARKET.get(label))
        except Exception as exc:
            log(f"  numbers: {table} unavailable: {exc!r}")
            df = pd.DataFrame()
        n_expected = int((end - start) / pd.Timedelta(hours=1))
        if len(df) == n_expected:
            lines.append(f"| {label} | {node} | {day.date()} | {mean2(df['value'])} | {notes.ref(table)} |")
        else:
            lines.append(f"| {label} | {node} | {day.date()} | not in the warehouse ({len(df)} of "
                         f"{n_expected} hours) | {notes.ref(table)} |")
    lines.append("| PJM | | | no PJM price table (no API key) | |")
    best = None
    # Session 16: only the interval price tables. filter(market="rtm") also names the derived
    # ercot_peak_premium tables and the yearly ERCOT history, which are not on the CI runner
    # (coverage carries them over), and fetching one there ended the digest with ERWDataNotFound.
    parts = rt_parts()
    rt_tables = list(dict.fromkeys(t for _, t, _ in parts))
    for iso, table, market in parts:
        tz = RT_TZ.get(iso, "UTC")
        day = pd.Timestamp(digest_date) - pd.Timedelta(days=1)
        start = pd.Timestamp(day.date()).tz_localize(tz)
        try:
            df = erw.fetch(table, start=start, end=start + pd.Timedelta(days=1), market=market)
        except Exception as exc:
            log(f"  numbers: {table} unavailable: {exc!r}")
            continue
        if df.empty:
            continue
        top = df.loc[df["value"].idxmax()]
        if best is None or top["value"] > best[0]["value"]:
            best = (top, table, tz, iso)
    lines += ["", "**Highest real-time price, yesterday:** "]
    if best:
        top, table, tz, iso = best
        lines[-1] += (f"{top['value']:.2f} USD/MWh at {top['node']} ({iso.upper()}), "
                      f"interval starting {top['ts_utc'].tz_convert(tz):%Y-%m-%d %H:%M} local "
                      f"({top['ts_utc']:%Y-%m-%d %H:%M} UTC), {top['freq']} `{top['variable']}`"
                      f"{' (a 15-minute mean of 5-minute prices)' if top['variable'].endswith('_15m_mean') else ''} "
                      f"{notes.ref(table, 'real-time tables read: ' + ', '.join(rt_tables))}.")
    else:
        lines[-1] += "no real-time table covers yesterday."
    lines += ["", "**Latest fuel spot closes** (EIA, trading dates):", ""]
    try:
        fuel = erw.fetch("eia_fuel_spot_prices")
        for label, entity in FUELS:
            s = fuel[fuel["entity"] == entity].sort_values("ts_utc")
            last = s.iloc[-1]
            lines.append(f"- {label}: {last['value']:.2f} {last['unit']} on {last['ts_utc']:%Y-%m-%d} "
                         f"{notes.ref('eia_fuel_spot_prices')}")
    except Exception as exc:
        log(f"  numbers: fuel prices unavailable: {exc!r}")
        lines.append("- fuel prices: not in the warehouse")
    return lines + notes.lines()


def policy_actions_lines(start, end, log, n=3):
    """Session 24: the policy actions of the window (policy_actions: the Federal Register and agency news) scored 5 or
    more with the news rubric, most significant first, as the Policy group's last lines. The title is the agency's own."""
    path = os.path.join(ip.OUT_DIR, "policy_actions.csv")
    if not os.path.exists(path):
        log("  policy actions: policy_actions.csv not on this machine")
        return []
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    a = pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)
    d = pd.to_datetime(a["event_date"], utc=True, format="ISO8601")
    # the actions are dated by day: the window's days, from the day it starts
    a = a[(d >= start.normalize()) & (d < end) & (a["significance"] != "")]
    a = a[a["significance"].astype(int) >= 5].assign(sig=lambda x: x["significance"].astype(int))
    a = a.sort_values(["sig", "event_date"], ascending=[False, False]).head(n)
    kinds = {"rule": "final rule", "proposed_rule": "proposed rule", "notice": "notice", "press_release": "news release"}
    log(f"  policy actions: {len(a)} scored 5 or more in the window")
    return [f"- {r['title']} ({r['agency']} {kinds.get(r['action_type'], r['action_type'])}, policy action): {r['why']} "
            f"[{r['agency']}]({r['source_url']})" for r in a.to_dict("records")]


def fun_fact_section(digest_date, log):
    """Session 23: the day's fun fact (warehouse/news/funfact.py wrote it to warehouse/news/facts/items/),
    checked again against its stored raw sources and the literal-number check. Any failure, or no item,
    gives no section: a digest without a fun fact ships rather than one with an unverified fact."""
    try:
        import funfact
        item = funfact.load_item(digest_date)
        if item is None:
            log(f"  fun fact: no item for {digest_date}; section omitted")
            return []
        problems = funfact.verify_item(item)
        if problems:
            log(f"  fun fact: {item['fact_id']} failed re-verification ({problems}); section omitted")
            return []
        log(f"  fun fact: {item['fact_id']} ({item['structure']}) re-verified")
        return ["", "## ERW's Fun Fact", ""] + funfact.item_markdown(item)
    except Exception as exc:
        log(f"  fun fact: omitted ({ip.redact(repr(exc))[:200]})")
        return []


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Energy Digest")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: today, UTC)")
    ap.add_argument("--out", help="write the digest to this path only (not docs/digest/<date>.md, not latest.md)")
    ap.add_argument("--weekend", action="store_true", help="write a digest for a Saturday or Sunday date anyway")
    ap.add_argument("--stories", help="read the scored stories from this file instead of news_stories (session 30: the "
                    "shadow scorer's view, warehouse/news/shadow.py)")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_brief_{run_id}.log"))
    status = dict(table="digest", market="brief", status="ok", detail="")
    digest_date = args.date or pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")
    if pd.Timestamp(digest_date).weekday() >= 5 and not args.weekend:
        # session 23: Monday to Friday only; the weekend opens Sunday's Energy Roundup
        day = pd.Timestamp(digest_date).strftime("%A")
        msg = f"no weekend issue ({day} {digest_date}); the weekend's stories are in Sunday's Energy Roundup"
        log(msg)
        print(f"news_brief SKIPPED: {msg}")
        ip.write_status("news_brief", run_id, [dict(status, status="skipped", detail=msg)])
        log.close()
        return 0
    try:
        now = pd.Timestamp.now(tz="UTC")
        df = ip.read_series(args.stories or os.path.join(ip.OUT_DIR, NAME + ".csv"), NEWS_COLS)
        when = pd.to_datetime(df["event_date"], utc=True, format="ISO8601")
        s = df[(df["scored_at"] != "") & (when >= now - pd.Timedelta(hours=args.hours))].copy()
        s["sig"] = s["significance"].astype(int)
        s["ai"] = s["ai_power_relevance"].astype(int)
        s = s[s["sig"] > 0]  # 0 = not about energy (rubric)
        log(f"digest {digest_date}: {len(s)} scored energy stories in the last {args.hours} hours")
        if s.empty:
            raise RuntimeError("no scored stories in the window; not writing an empty digest")
        clusters = build_clusters(s)
        top10 = clusters.head(10)
        # session 21, ruling 5: each cluster appears once; a section takes only clusters not shown above it
        used = set(top10["cluster_id"])
        by_group = {}
        for g, secs in GROUPS.items():
            by_group[g] = clusters[clusters["sector"].isin(secs) & ~clusters["cluster_id"].isin(used)].head(3)
            used |= set(by_group[g]["cluster_id"])
        ai = clusters[(clusters["ai"] >= 7) & ~clusters["cluster_id"].isin(used)].head(5)
        shown = pd.concat([top10, *by_group.values(), ai]).drop_duplicates("cluster_id")
        key = ip.load_key("ANTHROPIC_API_KEY", log)
        client = llm.client("digest", log, api_key=key)
        model = pick_model(client, log)
        heads, u, calls = headlines(client, model, shown, log)
        missing = set(shown["cluster_id"]) - set(heads)
        if missing:
            raise RuntimeError(f"headlines missing for {len(missing)} clusters")
        secs = unique_items({"top": top10, **{g: c for g, c in by_group.items()}, "ai": ai}, heads, log)
        top10, ai = secs.pop("top"), secs.pop("ai")
        by_group = secs
        # ruling 4: the share of the top 10 whose headline carries a number, and how many could
        n_fig = sum(1 for r in top10.to_dict("records") if figures(r))
        n_num = sum(1 for cid in top10["cluster_id"] if chat_ask.numbers(heads[cid]))
        log(f"  top 10: {n_num} of {len(top10)} headlines carry a number; {n_fig} of {len(top10)} clusters have a "
            "scored figure")
        cost = ""
        if model in PRICES:
            pi, po = PRICES[model]
            cost = f"USD {(u.input_tokens * pi + u.output_tokens * po) / 1e6:.4f}"
        log(f"  headlines: {len(heads)} from {model}; {calls} call(s); tokens in {u.input_tokens} "
            f"out {u.output_tokens}; cost {cost or 'unknown'}")
        L = [f"# ERW's Energy Digest, {digest_date}", "",
             # session 21: one sentence (what, the period, the story count); the method is on /about#digest
             f"ERW's weekday brief of energy news for the {args.hours} hours to {now:%Y-%m-%d %H:%M} UTC, "
             f"from {len(s)} scored stories.", "",
             "## Top of the industry", ""]
        for i, r in enumerate(top10.to_dict("records"), 1):
            L.append(f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')})  ")
            L.append(f"   {r['why']} {detail(r)}Sources: {link_text(r['links'])}")
        L += ["", "## By sector", ""]
        for g, c in by_group.items():
            L.append(f"**{g}**")
            L.append("")
            if c.empty:
                L.append("- no scored story in this group today")
            for r in c.to_dict("records"):
                L.append(f"- {heads[r['cluster_id']]} ({r['sector'].replace('_', ' ')}): {r['why']} {link_text(r['links'][:1])}")
            if g == "Policy":
                L += policy_actions_lines(now - pd.Timedelta(hours=args.hours), now, log)
            L.append("")
        L += ["## AI and power", ""]
        if ai.empty:
            L.append("- no further story on AI and power today (any such story is listed above)")
        for r in ai.to_dict("records"):
            L.append(f"- {heads[r['cluster_id']]} ({r['sector'].replace('_', ' ')}): {r['why']} "
                     f"{link_text(r['links'][:1])}")
        nums = numbers_today(digest_date, log)
        summary, su = numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        L += ["", "## ERW's Numbers Today", ""] + ([summary, ""] if summary else []) + nums
        # session 23: the Fun fact, last; re-verified from its stored sources, omitted if it fails
        L += fun_fact_section(digest_date, log)
        # session 21: the method is on /about#digest; the generation record stays in the file, not on the page
        L += ["", "ERW", "", "---", "", "[How this is made.](/about#digest)", "",  # session 25: signed ERW
              f"<!-- Generated by warehouse/news/brief.py at {now:%Y-%m-%d %H:%M} UTC; run log "
              f"warehouse/output/logs/news_brief_{run_id}.log; model {model}; story data "
              "warehouse/output/news_stories.csv. -->"]
        n_items = assert_unique(L)  # ruling 5: the hard check; a failure writes nothing
        log(f"  {n_items} items, no two sharing a normalized headline or a source URL")
        text = "\n".join(L) + "\n"
        if args.out:  # a check run: this path only, the day's digest and latest.md untouched
            path = os.path.abspath(args.out)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        else:
            os.makedirs(DIGEST_DIR, exist_ok=True)
            path = os.path.join(DIGEST_DIR, f"{digest_date}.md")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            shutil.copyfile(path, os.path.join(DIGEST_DIR, "latest.md"))
        status["detail"] = (f"top 10 with a number {n_num} of {len(top10)} ({n_fig} with a scored figure); "
                            f"{len(s)} stories, {len(clusters)} clusters, {calls} call(s), tokens in "
                            f"{u.input_tokens} out {u.output_tokens}, cost {cost or 'unknown'}")
        log(f"wrote {os.path.relpath(path, ROOT)}{'' if args.out else ' and latest.md'}; {status['detail']}")
        print(f"digest: {os.path.relpath(path, ROOT)}; {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"news_brief digest FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("news_brief", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
