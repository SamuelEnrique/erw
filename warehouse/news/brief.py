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
import glob
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


# Session 814 (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 6): a column, an interview or an analysis piece
# ranks after a reported event of the same significance. The rubric puts commentary at 1 to 3, but the scorer gave
# "Brookfield's Teskey sees no slowdown" and "Land & Expand tracks North America's data center pipeline" a 7 on 13 October
# and "Iran war tilts balance of global oil power" a 7 on 20 October; the score is the model's and is left alone, and the
# title's own form decides the order among equals. A title is commentary when it reads as one: a quoted or reported
# opinion ("says", "sees", "warns", "argues", "expects", "predicts"), a format word (Q&A, interview, explainer, opinion,
# analysis, column, podcast, newsletter, "explained"), a question, or a title that begins with "How", "Why", "What",
# "Should", "Can" or "Will".
COMMENTARY_WORDS = re.compile(r"\b(says|said|sees|warns|argues|expects|predicts|thinks|believes|urges|calls for|tells|told|"
                              r"q&a|q and a|interview|explainer|explained|opinion|analysis|column|podcast|newsletter|"
                              r"the week ahead|what to watch|takeaways|in charts|tracks)\b", re.I)
COMMENTARY_START = re.compile(r"^(?:how|why|what|should|can|could|will|is|are|does|do)\b", re.I)


def title_kind(title):
    """'commentary' when the title reads as a column, an interview or an analysis piece (COMMENTARY_WORDS, a question, a
    title that opens like one); else 'event'."""
    t = str(title or "").strip()
    if not t:
        return "event"
    if "?" in t or COMMENTARY_WORDS.search(t) or COMMENTARY_START.match(t):
        return "commentary"
    return "event"


def build_clusters(stories):
    rows = []
    for cid, g in stories.groupby("cluster_id"):
        g = g.sort_values(["sig", "event_date"], ascending=[False, True])
        lead = g.iloc[0]
        rows.append({
            "cluster_id": cid, "sig": int(g["sig"].max()), "ai": int(g["ai"].max()),
            # session 21: the MW and price of the cluster are the first any of its stories' scored fields hold
            "sector": lead["sector"], "region": str(lead.get("region", "") or ""), "why": lead["why"], "mw": next((x for x in g["mw"] if x), ""),
            "price": next((x for x in g["price_mentioned"] if x), ""), "parties": lead["parties"],
            "first": g["event_date"].min(), "n": len(g),
            "outlets": g["source"].astype(str).str.strip().str.lower().nunique(),   # session 2701: the outlets that ran it
            # session 470: one link an address (two stories of a cluster at one address printed it twice)
            "links": list({r.source_url: (r.source, r.source_url) for r in g.itertuples()}.values())[:3],
            "titles": list(g["title"])[:4], "summary": lead["summary"][:300],
            "kind": title_kind(lead["title"]),   # session 814: event or commentary, by the title's form
        })
    c = pd.DataFrame(rows)
    # session 814: among equals in significance, a reported event before commentary; then the tie-break.
    # Session 2701 (rulings item 4, the 24-hour default): the tie-break is the number of outlets that ran the story, then
    # the time, no longer AI relevance: the rubric gives an AI angle no credit by itself, and a 42 MW datacenter story
    # outranked a 600 MW gas deal at the same score
    c["_kind"] = (c["kind"] == "commentary").astype(int)
    return (c.sort_values(["sig", "_kind", "outlets", "first"], ascending=[False, True, False, True], kind="stable")
             .drop(columns="_kind").reset_index(drop=True))


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


# Session 176: a digest or Roundup written with --no-model (the daily model cap, warehouse/health.py budget)
NO_MODEL = "none (the daily model cap was reached)"
NO_MODEL_LINE = ("Today's headlines are the publishers' own titles, and the written summary of the numbers is left out: "
                 "the day's model budget was reached.")


def own_titles(clusters):
    """{cluster_id: the lead story's own title}, for an issue written without the model. Nothing is rewritten: the
    title is the publisher's, with a dash of the kind the ERW never prints replaced as in a model headline."""
    return {r["cluster_id"]: nodash(str(r["titles"][0]).strip()) for r in clusters.to_dict("records")}


def norm_headline(h):
    return re.sub(r"[^a-z0-9 ]+", "", h.lower()).strip()


# Session 470 (docs/reviews/digest-audit-2026-10-21.md, fix 5; roundup-audit fix 1): one event, one item. The scorer joins
# stories only within a scoring batch, so one event scored in two batches is two clusters: Korea's USD 120 billion nuclear
# framework was top 1 and top 2 on 2 October, the attack on Aramco's headquarters top 6 and top 7 on 14 October.
STOP = set("""the a an and or of to in on for with from by at as is are was were be been its it this that than into over under
after before about amid says said say new more most will would could may can has have had not no but up down out off
us usa per year years week day today report reports jan feb mar apr may jun jul aug sep sept oct nov dec january february march
april june july august september october november december""".split())
GENERIC_PARTY = set("department government ministry administration energy company group holdings corp corporation inc llc ltd "
                    "united states national federal state office agency commission".split())


def title_words(t):
    """The content words of a title, lower case, a plural's s taken off."""
    w = [x for x in re.findall(r"[a-z0-9]+", str(t).lower()) if len(x) >= 3 and x not in STOP and not x.isdigit()]
    return {x[:-1] if len(x) > 4 and x.endswith("s") else x for x in w}


def event_figures(r):
    """The amounts that name an event: a sum of money (not a price per unit) and a capacity in MW, as (kind, value)."""
    out = set()
    for f in figures(r):
        f = f.replace(",", "")
        if re.search(r"\bper\b|/", f):
            continue
        m = re.search(r"(\d[\d.]*)\s*(billion|bn|million|mn|mm|trillion|tn|b|m)?\b", f, re.I)
        if not m:
            continue
        try:
            v = float(m.group(1))
        except ValueError:
            continue
        if re.search(r"\$|USD|EUR|CAD|GBP", f):
            mult = {"billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "mn": 1e6, "mm": 1e6, "m": 1e6,
                    "trillion": 1e12, "tn": 1e12}.get((m.group(2) or "").lower(), 1)
            if v * mult >= 1e6:
                out.add(("usd", round(v * mult / 1e6)))
        elif re.search(r"GW\b", f):
            out.add(("mw", round(v * 1000)))
        elif re.search(r"MW\b", f) and v >= 10:
            out.add(("mw", round(v)))
    return out


def party_words(r):
    """The words of a cluster's parties that may name one event in common with another cluster, lower case, the generic
    words taken out. Session 2206 (digest audit, one-event matching): a whole word of two or more letters that is
    capitalized or all capitals ("Eni", "DOE", "SPP", "NextEra"), as the scorer writes a party's name; until then only
    runs of four or more letters counted, so a short name was never matched. A word of four or more letters still counts
    whatever its case, as before."""
    out = set()
    for p in str(r.get("parties") or "").split(";"):
        out |= {w.lower() for w in re.findall(r"\b(?:[A-Z][A-Za-z]+|[A-Z]{2,})\b", p)}
        out |= set(re.findall(r"[a-z]{4,}", p.lower()))
    return out - GENERIC_PARTY


def same_event(a, b):
    """Session 470: two clusters are one event when they name a party in common, are filed in one sector, and either their
    lead titles share most of their words (four or more, and 0.6 of the smaller set or more) or they share an amount (a
    sum of money of USD 1 million or more, a capacity of 10 MW or more). Without a party in common two titles of one kind
    (a day's gas futures report, a company's notice) are not one event; without one sector two stories that name a large
    party and a round sum (Nvidia and USD 5 billion, on 9 October, in two different stories) are not."""
    if a.get("sector") != b.get("sector") or not party_words(a) & party_words(b):
        return False
    ta, tb = title_words((a.get("titles") or [""])[0]), title_words((b.get("titles") or [""])[0])
    both = ta & tb
    if len(both) >= 4 and len(both) / min(len(ta), len(tb)) >= 0.6:
        return True
    return bool(event_figures(a) & event_figures(b))


def unique_items(sections, heads, log):
    """Session 21, ruling 5: the digest once showed the same event twice with identical wording, because
    each section chose its clusters on its own, so a top-10 cluster came back under By sector and AI and
    power. The sections now take distinct clusters; this also drops a later cluster whose headline, once
    normalized, or any source link (session 470: any, not only the first) repeats an earlier item's, or that is
    the same event as an earlier item (session 470, same_event).
    Returns the sections with the repeats removed."""
    seen_h, seen_u, kept, out = set(), set(), [], {}
    for name, df in sections.items():
        keep = []
        for r in df.to_dict("records"):
            h, urls = norm_headline(heads[r["cluster_id"]]), [u for _, u in r["links"]]
            twin = next((k for k in kept if same_event(k, r)), None)
            if h in seen_h or set(urls) & seen_u or twin is not None:
                why = (f", the same event as {twin['cluster_id']}" if twin is not None and h not in seen_h
                       and not set(urls) & seen_u else "")
                log(f"  dropped a repeat in {name}: {heads[r['cluster_id']]!r} ({r['cluster_id']}{why})")
                continue
            seen_h.add(h)
            seen_u.update(urls)
            # session 802: a folded story at an address shown already is dropped from the item's "also" line
            for x in list(also_of(r)):
                if {u for _, u in x["links"]} & seen_u:
                    log(f"  dropped a folded repeat under {r['cluster_id']}: {x['title'][:80]!r} ({x['cluster_id']})")
                    r["also"].remove(x)
                else:
                    seen_u.update(u for _, u in x["links"])
            kept.append(r)
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
        elif ln.startswith("   ") and ("Sources:" in ln or ln.strip().startswith(ALSO_LABEL)):  # 802: the also line too
            urls += re.findall(r"\]\((https?://[^)]+)\)", ln)
    dh = sorted({h for h in heads if heads.count(h) > 1})
    du = sorted({u for u in urls if urls.count(u) > 1})
    if dh or du:
        raise RuntimeError(f"duplicate items in the brief: headlines {dh[:3]}, source URLs {du[:3]}")
    return len(heads)


def without_repeats(new, lines, log):
    """Session 176: the lines of `new` whose headline and source URL are not already an item of `lines`. A policy
    action that is also a scored story (an agency's release the feeds carry) was a repeat the hard check below
    refused, so the whole digest was not written; the later line is dropped and named, as unique_items does."""
    item = re.compile(r"^(?:\d+\. \*\*(.+?)\*\*|- (.+?) \()")
    link = re.compile(r"\]\((https?://[^)]+)\)")
    heads = {norm_headline(m.group(1) or m.group(2)) for m in map(item.match, lines) if m}
    urls = {u for ln in lines for u in link.findall(ln)}
    keep = []
    for ln in new:
        m = item.match(ln)
        if m and (norm_headline(m.group(1) or m.group(2)) in heads or set(link.findall(ln)) & urls):
            log(f"  dropped a repeat of an item above: {ln[:120]!r}")
            continue
        if m:  # session 470: two new lines that repeat each other (5 October: two policy actions of one title)
            heads.add(norm_headline(m.group(1) or m.group(2)))
            urls |= set(link.findall(ln))
        keep.append(ln)
    return keep


def drop_repeated_items(lines, log):
    """Session 470 (digest audit fix 3): the issues of 5 and 6 October were lost to the hard check below, a repeated
    headline and a repeated DOE address that the sections' own checks did not see (a policy action, then the same
    address under AI and power). The later item is dropped and named in the log, and the numbered items are numbered
    again; the hard check still runs after this and still refuses what this cannot place."""
    item = re.compile(r"^(?:(\d+)\. \*\*(.+?)\*\*|- (.+?) \()")
    link = re.compile(r"\]\((https?://[^)]+)\)")
    heads, urls, out, i = set(), set(), [], 0
    while i < len(lines):
        ln = lines[i]
        m = item.match(ln)
        block = [ln]
        if m and m.group(1):   # session 802: the why line and, after it, the "also" line
            while i + len(block) < len(lines) and lines[i + len(block)].startswith("   "):
                block.append(lines[i + len(block)])
        i += len(block)
        if not m or ln.startswith("- no "):
            out += block
            continue
        h = norm_headline(m.group(2) or m.group(3))
        u = {x for b in block for x in link.findall(b)}
        if h in heads or u & urls:
            log(f"  dropped a repeated item: {ln[:120]!r}")
            continue
        heads.add(h)
        urls |= u
        out += block
    n, fixed = 0, []
    for ln in out:  # the top items numbered again, 1 to n; session 806: each section's list from 1 (the Roundup has two)
        if ln.startswith("## "):
            n = 0
        m = re.match(r"^(\d+)\. (\*\*.*)$", ln)
        if m:
            n += 1
            ln = f"{n}. {m.group(2)}"
        fixed.append(ln)
    return fixed


LICENSE_FILE = os.path.join(ROOT, "warehouse", "metadata", "license_status.csv")
_LICENSED = {}


def licensed_outlets(path=None):
    """Session 803 (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 3): the outlets whose stories ask for a
    license: the publishers of the news index's row in warehouse/metadata/license_status.csv while that row's status is
    "license needed" (the ruling of 21 October, docs/licenses.md); an empty set once the hold is lifted or the file is not
    here. Read once a process for each path."""
    import csv
    path = path or LICENSE_FILE
    if path in _LICENSED:
        return _LICENSED[path]
    out = set()
    try:
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
                if r.get("table") == "news_index" and r.get("status") == "license needed":
                    out = {x.strip() for x in str(r.get("publishers", "")).split(";") if x.strip()}
    except OSError:
        out = set()
    _LICENSED[path] = out
    return out


def outlet_key(name):
    """An outlet's name as the license file and the feeds name it, made one: lower case, ".com" and punctuation off
    ("Bloomberg.com" in the feed's field is the "Bloomberg" of docs/licenses.md)."""
    return re.sub(r"[^a-z0-9]+", "", re.sub(r"\.com$", "", str(name).strip().lower()))


def source_text(src, url, licensed=None):
    """One source as an item prints it (session 803): the outlet's name from the feed's own field as the link text, never
    the address; "(via Google News)" after a Google News address (session 470, kept); an outlet whose stories ask for a
    license (licensed_outlets) is named with no link, so the item shows the outlet and the title only."""
    licensed = licensed_outlets() if licensed is None else licensed
    if outlet_key(src) in {outlet_key(x) for x in licensed}:
        return str(src)
    return f"[{src}]({url})" + (" (via Google News)" if "news.google.com" in str(url) else "")


def link_text(links, licensed=None):
    # session 470 (digest audit fix 7, roundup audit fix 4): a Google News address does not reach the outlet (the ingest
    # records it in url_resolved), and the reader is told where the link goes; session 803: source_text; session 807: a
    # source printed once (two stories of one cluster at one held outlet printed "POWER Magazine, POWER Magazine")
    return ", ".join(dict.fromkeys(source_text(src, url, licensed) for src, url in links))


# Session 470 (digest audit fix 9): one style for a sum of money, "USD 45 billion", as docs/voice.md writes it
CURRENCY = [(r"US\$|USD ?", "USD"), (r"C\$|CAD ?", "CAD"), (r"A\$|AUD ?", "AUD"), (r"\u20ac|EUR ?", "EUR"),
            (r"\u00a3|GBP ?", "GBP"), (r"\$", "USD")]
SCALE = {"billion": "billion", "bn": "billion", "b": "billion", "million": "million", "mn": "million", "mm": "million",
         "m": "million", "trillion": "trillion", "tn": "trillion", "k": "thousand", "thousand": "thousand"}
# session 577: a currency code is not read inside a word ("amateur 5", "arcade 3"), now that why lines go through this too
MONEY = re.compile(r"(?<![A-Za-z])(C\$|A\$|US\$|USD ?|CAD ?|AUD ?|EUR ?|GBP ?|\$|\u20ac|\u00a3)\s?(\d[\d,]*(?:\.\d+)?)(?:\s?"
                   r"(billion|bn|million|mn|mm|trillion|tn|thousand|k|b|m)\b)?", re.I)


def money_style(s):
    """'$45 Billion' to 'USD 45 billion', '$800MM' to 'USD 800 million', 'C$14.3 Billion' to 'CAD 14.3 billion'; a price
    per unit keeps its unit ('$93.78 per barrel' to 'USD 93.78 per barrel'). Text that is not a sum is returned as it is."""
    def one(m):
        cur = next(code for pat, code in CURRENCY if re.fullmatch(pat, m.group(1).strip(), re.I))
        scale = SCALE.get((m.group(3) or "").lower())
        return f"{cur} {m.group(2)}" + (f" {scale}" if scale else "")
    return MONEY.sub(one, str(s))


def an_word(word):
    """Whether a word takes 'an': a vowel sound, by its spelling, with the common exceptions ('a utility', 'a one-off',
    'an hour', 'an 8 GW')."""
    w = str(word).lower()
    if re.match(r"(uni|use|usu|uti|ura|eu|one|once|ubi)", w):
        return False
    if re.match(r"(hour|honest|honor|honour|heir|8|11\b|18\b|80)", w):
        return True
    return w[:1] in "aeiou"


# Session 470 (digest audit fix 8): the why lines are the scorer's reasons; docs/voice.md cuts these adjectives.
# Session 801 (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 1): the list of seven the plan counted over the 13
# issues (107 of 397 why lines): massive, unprecedented, significant, major, critical, key, huge; and their adverbs.
WHY_ADJECTIVES = ("massive", "unprecedented", "significant", "major", "critical", "key", "huge")
# Session 2206: unprecedented, critical and key join the list. "key" and "critical" are also plain words of the trade
# ("the key to", "critical minerals"): TERM says where they stand, and plain() leaves those.
HYPE = r"(?:major|massive|significant|significantly|huge|unprecedented|critical|critically|key)"
TERM = r"(?!\s+(?:to|of|for|in|on|is|was|are|were|minerals?|infrastructure|mass|path|peak)\b)"


def plain(text):
    """The why line without the adjectives docs/voice.md cuts: 'a major 2 GW deal' to 'a 2 GW deal', 'Massive outage' to
    'Outage'; 'a' and 'an' follow the next word. Session 2206: an adjective at the end of a sentence or a clause ("The
    deal is significant.", "Prices rose, significantly") goes too; until then only one followed by a space did."""
    def article(m):
        an = an_word(m.group(2))
        cap = m.group(1)[0] == "A"
        return ("An" if cap else "an") + " " + m.group(2) if an else ("A" if cap else "a") + " " + m.group(2)
    t = re.sub(rf"\b(an|a)\s+{HYPE}{TERM}\s+(\w+)", article, str(text), flags=re.I)
    t = re.sub(rf"(^|(?<=[.!?] )){HYPE}{TERM}\s+(\w)", lambda m: m.group(1) + m.group(2).upper(), t, flags=re.I)
    t = re.sub(rf"\b{HYPE}{TERM}\s+", "", t, flags=re.I)
    # at a stop, a comma, a semicolon or the end: the word and the space before it go, the mark stays; between two
    # commas (", significantly,") the comma before it goes too
    t = re.sub(rf",\s*\b{HYPE}\b(?=\s*[.,;:!?])", "", t, flags=re.I)
    return re.sub(rf"\s*\b{HYPE}\b(?=\s*(?:[.,;:!?]|$))", "", t, flags=re.I)


NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
# a sentence's end: a stop, then a space and a capital or a digit; not after one capital letter ("U.S. Department"), an
# initial, or an abbreviation of ABBREVIATIONS ("Oct. 6", "Inc. and", "No. 5")
SENTENCE_END = re.compile(r"[.!?][\"'”)\]]*\s+(?=[A-Z0-9])")
ABBREVIATIONS = set("jan feb mar apr jun jul aug sep sept oct nov dec inc corp ltd co no vs mr ms mrs dr st mt approx est "
                    "fig vol pp".split())


def sentence_end(t):
    """The match of the first sentence's end in t (SENTENCE_END, skipping an abbreviation's stop), or None."""
    for m in SENTENCE_END.finditer(t):
        before = re.search(r"([A-Za-z.]+)$", t[:m.start()])
        w = before.group(1) if before else ""
        if "." in w or (len(w) == 1 and w.isupper()) or w.lower() in ABBREVIATIONS:
            continue
        return m
    return None
# a figure as a why line prints it: a sum of money in the one style, or a number with its unit or percent sign
FIGURE_PHRASE = (r"(?:(?:USD|CAD|AUD|EUR|GBP)\s)?{n}(?:\s?(?:billion|million|trillion|thousand|bn|mn|m|b|k)\b)?"
                 r"(?:(?:\s|-)?(?:%|percent|GW|MW|GWh|MWh|TWh|kV|bcf|Bcf|mcf|MMcf|mtpa|Mt|MMBtu|bpd|b/d|barrels|tons|tonnes|miles|km)"
                 r"(?:/d(?:ay)?)?)?")


def figures_of(text):
    """The numbers of a text, as plain strings ("6,600" and "6600" are one), years left out: the figures a headline gives
    are its amounts, and "by 2032" in a why line adds no figure the headline already holds."""
    out = set()
    for n in NUMBER.findall(str(text) or ""):
        v = n.replace(",", "")
        if re.fullmatch(r"(19|20)\d\d", v):
            continue
        out.add(v)
    return out


def why_check(text, head=""):
    """Session 801: the rule of the why line, as the brief's gate: one sentence; no adjective of WHY_ADJECTIVES; no figure
    the headline already gives; not empty. The problems found, as short strings; [] when the line passes. The scorer's
    prompt asks the model for the same, but a prompt is not a check: a line that fails here is rewritten by why_line."""
    t = str(text or "").strip()
    if not t:
        return ["empty"]
    out = [f"adjective: {m.lower()}" for m in re.findall(rf"\b{HYPE}\b", t, flags=re.I)]
    if sentence_end(t):
        out.append("two sentences")
    for n in sorted(figures_of(t) & figures_of(head)):
        out.append(f"figure of the headline: {n}")
    return out


def why_fallback(title):
    """The title's own clause as the why line, never an invented fact (session 801): the publisher's suffix ("- Reuters",
    "| Outlet"), a leading "Exclusive:" and a trailing ", Bloomberg reports" taken off, a stop at the end."""
    t = money_style(nodash(str(title or ""))).strip()
    t = re.sub(r"^(?:exclusive|breaking|update \d*|analysis|explainer)\s*[:|]\s*", "", t, flags=re.I)
    t = re.sub(r"\s+[-|]\s+[\w.&' ]{1,40}$", "", t)
    t = re.sub(r",?\s+(?:[A-Z][\w.]*\s)?(?:reports?|says)$", "", t)
    t = t.strip(" ,;:")
    if t and not re.search(r"[.!?][\"'”)\]]*$", t):
        t += "."
    return t


# the words before a figure phrase after which the phrase can go and the sentence still reads ("a 600 MW load" to "a load",
# "at 11 PJM reactors" to "at PJM reactors"); after a verb or "of" ("totaling 2.1 GW", "a total of 2.1 GW") it cannot
BEFORE_FIGURE = r"(?:a|an|the|its|their|this|at|for|with|about|over|nearly|some|around|up to|another|new)"


def fix_article(t):
    """'a uprate' to 'an uprate' and 'an load' to 'a load', after a figure between the article and its noun is gone."""
    def one(m):
        art, word = m.group(1), m.group(2)
        want = "an" if an_word(word) else "a"
        if art.lower() == want:
            return m.group(0)
        return (want.capitalize() if art[0] == "A" else want) + " " + word
    return re.sub(r"\b(an|a|An|A)\s+(\w+)", one, t)


def without_figures(t, head):
    """The line with every figure phrase the headline already gives taken out where the sentence still reads: the phrase
    follows an article or a preposition (BEFORE_FIGURE) and a word follows it. "" when a phrase cannot go that way, or
    what is left is not a sentence (under four words, or not starting with a letter): the caller then falls back."""
    for n in sorted(figures_of(head), key=len, reverse=True):
        if n not in figures_of(t):
            continue
        shown = next((m for m in NUMBER.findall(t) if m.replace(",", "") == n), n)
        pat = re.compile(r"(?<![\w.,])" + FIGURE_PHRASE.format(n=re.escape(shown)) + r"(?=\s+[A-Za-z])", re.I)
        m = pat.search(t)
        if not m or not re.search(r"(?:^|\s)" + BEFORE_FIGURE + r"\s*$", t[:m.start()], re.I):
            return ""
        t = (t[:m.start()] + t[m.end():]).replace("  ", " ")
        t = fix_article(re.sub(r"\s+([,;:.])", r"\1", t).strip(" ,;:"))
    words = re.findall(r"[A-Za-z]+", t)
    if len(words) < 4 or not re.match(r"[A-Za-z\"'(]", t):
        return ""
    return t[0].upper() + t[1:]


def why_line(text, head=""):
    """Session 577 (digest audit fixes 8 and 9, as session 470 left them): the scorer's reason as an issue prints it: the
    adjectives docs/voice.md cuts taken out (plain), each sum of money in the one style (money_style: the "$3.2bn" and
    "$45 Billion" of the why lines, not only the price field), and a stop at its end, so the figures or the links that
    follow do not run on from it ("affecting global oil markets and prices parties: Iran.", 20 October, top 8).
    Session 801: with the printed headline (`head`) the line is held to why_check's rule: its first sentence only, and
    no figure the headline already gives (the phrase is taken out); what fails the check after that, or is left too
    short, is replaced by the headline's own clause (why_fallback), never by an invented fact."""
    t = money_style(plain(text)).strip()
    # "an $800MM loan" was right as written; as "USD 800 million" the article follows the code as it is said
    t = re.sub(r"\b([Aa])n? (USD|CAD|EUR|GBP|AUD)\b",
               lambda m: m.group(1) + ("n " if m.group(2) == "AUD" else " ") + m.group(2), t)
    if head:
        m = sentence_end(t)
        if m:
            t = t[:m.start()] + t[m.start():m.end()].rstrip()
        if figures_of(t) & figures_of(head):
            t = without_figures(t, head)
        if t and not re.search(r"[.!?][\"'”)\]]*$", t):
            t += "."
        if why_check(t, head):
            fb = why_fallback(head)
            # session 807: the headline's own clause is no why line when it is the headline (the dry run printed
            # "Crusoe plans Spark Liquid ... (datacenter power): Crusoe plans Spark Liquid ..."); the item then has none
            return "" if norm_headline(fb) == norm_headline(head) else fb
        return t
    if t and not re.search(r"[.!?][\"'”)\]]*$", t):
        t += "."
    return t


def detail(r, head=""):
    """The figures line after the why line: the MW, the price and the parties of the cluster's scored fields. Session 801:
    a MW or a price whose figure the printed headline already gives is not printed again ("Anthropic may spend $750 Billion
    ... $750 Billion; parties: Anthropic", 21 October, top 1)."""
    bits = []
    hf = figures_of(head)
    if r["mw"] and not figures_of(f"{float(r['mw']):,.0f}") & hf:
        bits.append(f"{float(r['mw']):,.0f} MW")
    if r["price"] and not (figures_of(r["price"]) and figures_of(r["price"]) <= hf):
        bits.append(money_style(r["price"]))  # session 470
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


PAUSED_FILE = os.path.join(ROOT, "warehouse", "metadata", "paused_sources.csv")


def paused_row(label):
    """Session 470: the pause of a grid's publisher (warehouse/metadata/paused_sources.csv, the file every connector asks
    first), as its row, or None. label: "MISO"."""
    try:
        rows = pd.read_csv(PAUSED_FILE, dtype=str, keep_default_na=False).to_dict("records")
    except (OSError, ValueError):
        return None
    return next((r for r in rows if r.get("scope") == str(label).lower().replace("-", "")), None)


def rt_label(iso, variable):
    """Session 470 (digest audit fix 12): a reader's name for a real-time price variable. ERCOT's `spp_rtm` is its
    settlement point price, not the Southwest Power Pool."""
    name = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "isone": "ISO-NE", "spp": "SPP", "miso": "MISO",
            "pjm": "PJM"}.get(str(iso).lower(), str(iso).upper())
    v = str(variable)
    if v.startswith("spp_rtm"):
        return f"{name}'s real-time settlement point price"
    if v.startswith("lmp_rtm"):
        return f"{name}'s real-time locational marginal price"
    return f"{name}'s real-time price"


def cite_short(table):
    """The footnote's words for a table: its name and its source reports. Session 804: a table this machine does not hold
    (the section already says "not in the warehouse" for its figures) is named alone, so the footnotes never stop the
    section."""
    try:
        s = erw.sources(table)
    except Exception:
        return f"`{table}`"
    return f"`{table}` ({', '.join(r['source'] for r in s['reports'] if r.get('source'))})"


# Session 804 (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 4): the numbers section says what moved. The
# section listed six averages of one day with no day before, one real-time maximum and three fuel closes a week old with
# no change; a reader learned where power was dearest, not what moved. Now: the day-ahead table carries the day before
# and the change; "What moved most" ranks the MOVERS_N largest moves in percent among the main hubs' day-ahead averages
# (against the day before) and EIA's spot closes (against the close before them), each with a reason only when a scored
# story of the day names that price; a held grid's price is not ranked (the board's own rule for a "license needed"
# series, warehouse/derived/board_page.py LICENSED); TTF and JKM are not held and say so; the fuel closes say how old
# they are; US48 demand's peak is set against the same weekday a year before where the warehouse holds it.
MOVERS_N = 5
LICENSED_NOTE = "licensed source needed"
# the words a scored story must name, in its title or its why line, for its why line to be the reason beside a price
PRICE_WORDS = {"Henry Hub natural gas": ("henry hub",), "WTI Cushing crude": ("wti",), "Brent crude": ("brent",),
               "ERCOT": ("ercot",), "CAISO": ("caiso",), "NYISO": ("nyiso",), "MISO": ("miso",),
               "SPP": ("southwest power pool", " spp "), "ISO-NE": ("iso-ne", "iso new england", "new england")}
NOT_HELD = (("TTF, the Dutch gas benchmark", "not held: its source asks for a license"),
            ("JKM, the Japan-Korea LNG marker", "not held: its source asks for a license"))
US48 = "eia930:US48"


def held_rows(path=None):
    """The rows of warehouse/metadata/license_status.csv whose status is "license needed"; [] when the file is not here."""
    import csv
    try:
        with open(path or LICENSE_FILE, encoding="utf-8", newline="") as f:
            return [r for r in csv.DictReader(ln for ln in f if not ln.startswith("#")) if r.get("status") == "license needed"]
    except OSError:
        return []


def table_held(table, grid, rows):
    """A grid's figures of `table` are held: the table's row is "license needed" and names the grid among its publishers
    (a row naming none holds every grid of the table)."""
    for r in rows:
        if r.get("table") != table:
            continue
        pubs = [x.strip() for x in str(r.get("publishers", "")).split(";") if x.strip()]
        if not pubs or outlet_key(grid) in {outlet_key(x) for x in pubs}:
            return True
    return False


def held_grids(path=None):
    """The grids of MAIN_HUBS whose table is "license needed" in warehouse/metadata/license_status.csv (a consolidated
    table holds a grid only when the row's publishers name it): {"NYISO", "ISO-NE", "MISO"} on 22 October 2026."""
    rows = held_rows(path)
    return {label for label, table, _node, _tz in MAIN_HUBS if table_held(table, label, rows)}


# Session 2701 (rulings item 1, the default of 24 October 2026): the real-time parts' grids by the label the license
# file's publishers use, so the highest real-time price skips a held grid's table
RT_GRID = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO", "spp": "SPP", "isone": "ISO-NE"}


def held_rt(parts, path=None):
    """The (iso, table) pairs of rt_parts whose figures are held (table_held, by RT_GRID)."""
    rows = held_rows(path)
    return {(iso, table) for iso, table, _m in parts if table_held(table, RT_GRID.get(iso, iso.upper()), rows)}


def dam_mean(label, table, node, tz, day, log):
    """(mean, hours held, hours expected) of the hub's day-ahead prices over the ISO's local operating day `day`; the
    mean is None unless every hour is held."""
    start = pd.Timestamp(day.date()).tz_localize(tz)
    end = pd.Timestamp((day + pd.Timedelta(days=1)).date()).tz_localize(tz)
    expected = int((end - start) / pd.Timedelta(hours=1))
    try:
        df = erw.fetch(table, start=start, end=end, node=node, market=HUB_MARKET.get(label))
    except Exception as exc:
        log(f"  numbers: {table} unavailable: {exc!r}")
        return None, 0, expected
    return (mean2(df["value"]) if len(df) == expected else None), len(df), expected


def day_move(newest, newest_day, prev, prev_day):
    """The move of a daily series from the value held before to the newest, as the price board computes it
    (warehouse/derived/board_page.py, stats: the move of the day): {ch, pct}, pct None when the base is not positive.
    board_page.stats is used when it imports here; else its formula, which the tests hold equal."""
    series = {pd.Timestamp(prev_day).date(): float(prev), pd.Timestamp(newest_day).date(): float(newest)}
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import board_page
        m = board_page.stats(series)["moves"]["d"]
        if m is not None:
            return {"ch": m["ch"], "pct": m["pct"]}
    except Exception:
        pass
    v0, v = float(newest), float(prev)
    return {"ch": round(v0 - v, 4), "pct": round(100 * (v0 - v) / v, 2) if v > 0 and v0 >= 0 else None}


def price_reason(label, clusters):
    """The why line of the day's highest-ranked scored story that names the price (PRICE_WORDS), with its outlet, as
    the reason beside a mover; "" when no story of the day names it (the figure then stands with no reason)."""
    words = PRICE_WORDS.get(label) or PRICE_WORDS.get(label.split(" ")[0]) or ()
    if clusters is None or not len(clusters) or not words:
        return ""
    for r in clusters.to_dict("records"):
        title = str((r.get("titles") or [""])[0])
        text = f" {title} {r.get('why') or ''} ".lower()
        if any(w in text for w in words):
            why = why_line(r.get("why") or "", title)
            if not why:
                continue
            return f" Reason, from the day's stories: {why} ({link_text(list(r.get('links') or [])[:1])})"
    return ""


def demand_lines(digest_date, log, notes):
    """US48 demand's peak hour of yesterday (the UTC day before the issue) and, where the warehouse holds it, the peak of
    the same weekday a year before (364 days earlier); the two values and their hours, and the change in percent."""
    day = pd.Timestamp(digest_date).tz_localize("UTC") - pd.Timedelta(days=1)
    out = ["", "**US48 demand, yesterday:** "]

    def peak(d):
        df = erw.fetch("eia930_all_demand", start=d, end=d + pd.Timedelta(days=1), ba="us48")
        df = df[df["variable"] == "demand_mw"]
        if df.empty:
            return None
        top = df.loc[df["value"].idxmax()]
        return top
    try:
        top = peak(day)
    except Exception as exc:
        log(f"  numbers: US48 demand unavailable: {exc!r}")
        out[-1] += "not in the warehouse."
        return out
    if top is None:
        out[-1] += f"not in the warehouse for {day:%Y-%m-%d}."
        return out
    ref = notes.ref("eia930_all_demand", "balancing authority us48")
    out[-1] += f"peaked at {top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC {ref}; "
    before = day - pd.Timedelta(days=364)
    try:
        old = peak(before)
    except Exception as exc:
        log(f"  numbers: US48 demand a year before unavailable: {exc!r}")
        old = None
    if old is None:
        out[-1] += f"the same weekday a year before ({before:%Y-%m-%d}) is not held: the hourly table's window does not reach it."
        return out
    pct = 100 * (float(top["value"]) / float(old["value"]) - 1) if float(old["value"]) > 0 else None
    out[-1] += (f"the same weekday a year before ({before:%Y-%m-%d}) peaked at {old['value']:,.0f} MW in the hour starting "
                f"{old['ts_utc']:%Y-%m-%d %H:%M} UTC {ref}" + (f", so {pct:+.1f}% on the year." if pct is not None else "."))
    return out


def numbers_today(digest_date, log, clusters=None):
    """The numbers section (session 804: what moved). clusters: the day's clusters (build_clusters), for the reasons."""
    notes = Notes()
    held = held_grids()
    day = pd.Timestamp(digest_date) - pd.Timedelta(days=1)
    before = day - pd.Timedelta(days=1)
    hubs = []
    for label, table, node, tz in MAIN_HUBS:
        m1, n1, x1 = dam_mean(label, table, node, tz, day, log)
        m0, n0, x0 = dam_mean(label, table, node, tz, before, log)
        hubs.append(dict(label=label, table=table, node=node, day=day, m1=m1, n1=n1, x1=x1, m0=m0, n0=n0, x0=x0,
                         pause=paused_row(label), held=label in held))
    lines = ["**Day-ahead average, yesterday, main hub** (mean of the 24 hourly prices of the operating day, and the day before):", "",
             "| ISO | Hub or zone | Operating day | Average USD/MWh | Table | Day before USD/MWh | Change |", "|---|---|---|---|---|---|---|"]
    for h in hubs:
        ref = notes.ref(h["table"])
        paused = (f"not requested: paused by the ERW since {h['pause']['paused_on']} ({h['pause']['reason']})"
                  if h["pause"] else "")
        if h["held"]:   # session 2701 (rulings item 1): a held grid prints no digit, in the markdown and so in the email
            cell, prev = paused or LICENSED_NOTE, ""
        elif h["m1"] is not None:
            cell = f"{h['m1']}"
        elif h["pause"]:  # session 470 (digest audit fix 12): why the grid is absent, not "not in the warehouse"
            cell = paused
        else:
            cell = f"not in the warehouse ({h['n1']} of {h['x1']} hours)"
        if not h["held"]:
            prev = f"{h['m0']}" if h["m0"] is not None else ("" if h["pause"] else f"not in the warehouse ({h['n0']} of {h['x0']} hours)")
        if h["m1"] is not None and h["m0"] is not None and not h["held"]:
            mv = day_move(h["m1"], day, h["m0"], before)
            chg = f"{mv['ch']:+.2f}" + (f" ({mv['pct']:+.1f}%)" if mv["pct"] is not None else "")
        else:
            chg = "not computed"
        lines.append(f"| {h['label']} | {h['node']} | {day.date()} | {cell} | {ref} | {prev} | {chg} |")
    lines.append("| PJM | | | no PJM price table (no API key) | | | |")

    # the real-time maximum (session 16; session 30: the consolidated table one ISO at a time)
    best = None
    parts = rt_parts()
    held_parts = held_rt(parts)   # session 2701 (rulings item 1): a held grid's real-time table is not read for the maximum
    if held_parts:
        log(f"  numbers: real-time maximum skips the held {', '.join(sorted(f'{i} ({t})' for i, t in held_parts))}")
    parts = [p for p in parts if (p[0], p[1]) not in held_parts]
    rt_tables = list(dict.fromkeys(t for _, t, _ in parts))
    for iso, table, market in parts:
        tz = RT_TZ.get(iso, "UTC")
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
                      f"({top['ts_utc']:%Y-%m-%d %H:%M} UTC), {top['freq']} `{top['variable']}`, {rt_label(iso, top['variable'])}"
                      f"{' (a 15-minute mean of 5-minute prices)' if top['variable'].endswith('_15m_mean') else ''} "
                      f"{notes.ref(table, 'real-time tables read: ' + ', '.join(rt_tables))}.")
    else:
        lines[-1] += "no real-time table covers yesterday."
    if held_parts:
        lines[-1] += (" Not read: " + ", ".join(sorted({RT_GRID.get(i, i.upper()) for i, _t in held_parts}))
                      + f" ({LICENSED_NOTE}).")

    # the fuel closes, with their age, and the close before each
    lines += ["", "**Latest fuel spot closes** (EIA, trading dates; EIA publishes its closes about a week after the day):", ""]
    fuels = []
    try:
        fuel = erw.fetch("eia_fuel_spot_prices")
        for label, entity in FUELS:
            s = fuel[fuel["entity"] == entity].sort_values("ts_utc")
            last = s.iloc[-1]
            age = (pd.Timestamp(digest_date).tz_localize("UTC") - last["ts_utc"]).days
            # a close dated after the issue's day: the table was read later than the issue (a rerun, a check)
            when = (f"{age} days before this issue" if age >= 0 else "dated after this issue's day: the table was read later")
            lines.append(f"- {label}: {last['value']:.2f} {last['unit']} on {last['ts_utc']:%Y-%m-%d} "
                         f"{notes.ref('eia_fuel_spot_prices')}, EIA's newest close when this was written ({when})")
            if len(s) > 1:
                prev = s.iloc[-2]
                fuels.append(dict(label=label, unit=last["unit"], v=float(last["value"]), d=last["ts_utc"], pv=float(prev["value"]),
                                  pd=prev["ts_utc"], ref=notes.ref("eia_fuel_spot_prices")))
    except Exception as exc:
        log(f"  numbers: fuel prices unavailable: {exc!r}")
        lines.append("- fuel prices: not in the warehouse")

    # what moved most
    cands = []
    for h in hubs:
        if h["held"] or h["pause"] or h["m1"] is None or h["m0"] is None:
            continue
        mv = day_move(h["m1"], day, h["m0"], before)
        if mv["pct"] is None:
            continue
        cands.append(dict(label=f"{h['label']} {h['node']} day-ahead", key=h["label"], unit="USD/MWh", v=float(h["m1"]), d=day,
                          pv=float(h["m0"]), pd=before, ref=notes.ref(h["table"]), **mv))
    for f in fuels:
        mv = day_move(f["v"], f["d"], f["pv"], f["pd"])
        if mv["pct"] is None:
            continue
        cands.append(dict(f, key=f["label"], **mv))
    cands.sort(key=lambda c: (-abs(c["pct"]), c["label"]))
    movers = ["", f"**What moved most** (the {MOVERS_N} largest moves in percent among the main hubs' day-ahead averages against the "
              "day before, and EIA's spot closes against the close before them):", ""]
    for c in cands[:MOVERS_N]:
        movers.append(f"- {c['label']}: {c['v']:.2f} {c['unit']} on {c['d']:%Y-%m-%d}, {'up' if c['ch'] >= 0 else 'down'} "
                      f"{abs(c['ch']):.2f} {c['unit']} ({abs(c['pct']):.1f}%) from {c['pv']:.2f} {c['unit']} on {c['pd']:%Y-%m-%d} {c['ref']}."
                      + price_reason(c["key"], clusters))
    if not cands:
        movers.append("- no price with a day before it is held, so no move is ranked.")
    not_ranked = [f"{h['label']} {h['node']} ({LICENSED_NOTE})" for h in hubs if h["held"] and not h["pause"]]
    not_ranked += [f"{h['label']} {h['node']} (paused by the ERW since {h['pause']['paused_on']})" for h in hubs if h["pause"]]
    not_ranked += [f"{name} ({why})" for name, why in NOT_HELD]
    movers.append("- Not ranked: " + "; ".join(not_ranked) + ".")
    lines = movers + [""] + lines
    lines += demand_lines(digest_date, log, notes)
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
    return [f"- {r['title']} ({r['agency']} {kinds.get(r['action_type'], r['action_type'])}, policy action): {why_line(r['why'], r['title'])} "
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


def daily_chart_section(digest_date, log, out=None, stories=None):
    """Session 232 (Samuel's ruling of 12 October 2026: the daily chart is fully automatic, a fact and its chart, no
    approval): the day's chart, chosen and drawn by code (warehouse/analysis/findings/daily_chart.py: the day's
    strongest scanner flag no Digest has shown, else the watch list's largest change of the latest period). No model
    is called and none of its words are a model's. Nothing to show, or any failure, gives no section and the reason
    in the log: a digest without a chart ships. out: a check run's path (--out); its picture and record are then
    written beside that file, the wait for the day's scan is skipped, and docs/digest/charts/ is not touched.
    stories (session 805): the day's top ten, so the chart follows the day (daily_chart.relevance)."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import daily_chart
        if out:
            return daily_chart.section(digest_date, log, chart_dir=os.path.join(os.path.dirname(os.path.abspath(out)), "charts"), wait=0,
                                       used=daily_chart.used_keys(but=digest_date),
                                       waited=daily_chart.held_before(digest_date),   # session 267: the guard's memory is the real one
                                       stories=stories)
        wait = os.environ.get("DAILY_CHART_WAIT", "")
        return daily_chart.section(digest_date, log, wait=int(wait) if wait.isdigit() else None, stories=stories)
    except Exception as exc:
        log(f"  daily chart: omitted ({ip.redact(repr(exc))[:200]})")
        return []


LINK_RE = re.compile(r"\]\((https?://[^)]+)\)")


def earlier_issues(digest_date, days=7, folder=None):
    """The Digests of the `days` days before digest_date, as paths."""
    day, folder = pd.Timestamp(digest_date), folder or DIGEST_DIR
    out = []
    for f in sorted(glob.glob(os.path.join(folder, "????-??-??.md"))):
        try:
            t = pd.Timestamp(os.path.basename(f)[:10])
        except ValueError:
            continue
        if day - pd.Timedelta(days=days) <= t < day:
            out.append(f)
    return out


ITEM_RE = re.compile(r"^(?:\d+\. \*\*(.+?)\*\*|- (.+?) \()")


def issue_items(paths):
    """Session 470: the story items of the issues at `paths`, each as {head, words, figs, urls}: its headline's content
    words, every word of its lines, the amounts its lines print (event_figures) and its links."""
    out = []
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for i, ln in enumerate(lines):
            m = ITEM_RE.match(ln)
            if not m or ln.startswith("- no ") or "policy action)" in ln:
                continue
            block = ln
            if m.group(1):   # session 802: every indented line of the item, the "also" line included
                for nxt in lines[i + 1:i + 3]:
                    if nxt.startswith("   "):
                        block += " " + nxt
            out.append({"head": title_words(m.group(1) or m.group(2)), "words": set(re.findall(r"[a-z]{4,}", block.lower())),
                        "figs": event_figures({"why": block, "mw": "", "price": ""}), "urls": set(LINK_RE.findall(block))})
    return out


def repeat_of(r, item):
    """Session 470: whether cluster r is the story of an earlier issue's item: a link in common; or a party of r named in
    the item and either an amount in common or a lead title that shares most of its content words (five or more, and 0.6
    of the smaller set) with the item's headline. A day's market report with no party is never a repeat by its title."""
    if {u for _, u in r["links"]} & item["urls"]:
        return True
    if not party_words(r) & item["words"]:
        return False
    if event_figures(r) & item["figs"]:
        return True
    t = title_words((r.get("titles") or [""])[0])
    both = t & item["head"]
    return len(both) >= 5 and len(both) / min(len(t), len(item["head"])) >= 0.6


def not_shown_before(clusters, paths, log, what="an earlier Digest"):
    """Session 470 (digest audit fix 4, roundup audit fix 1): a cluster that is an earlier issue's story (repeat_of) is
    left out: Voltus's USD 225 million on 8, 9 and 12 October, Google and Constellation's 890 MW on 7, 8 and 9 October.
    It is kept when it brings a sum of money none of those issues printed, which makes it news again (a price disclosed
    after the deal)."""
    items = issue_items(paths)
    if not items:
        return clusters
    sums = {f for it in items for f in it["figs"] if f[0] == "usd"}
    keep = []
    for r in clusters.to_dict("records"):
        twin = next((it for it in items if repeat_of(r, it)), None)
        if twin is not None and not {f for f in event_figures(r) if f[0] == "usd"} - sums:
            log(f"  left out, shown in {what}: {str((r.get('titles') or [''])[0])[:100]!r} ({r['cluster_id']})")
            continue
        keep.append(r["cluster_id"])
    return clusters[clusters["cluster_id"].isin(keep)].reset_index(drop=True)


def one_per_event(clusters, log):
    """Session 470: the clusters in their rank, each event once (same_event): the later twin is left out before the
    sections are filled, so the top 10 still holds ten items."""
    kept, keep = [], []
    for r in clusters.to_dict("records"):
        twin = next((k for k in kept if same_event(k, r)), None)
        if twin is not None:
            log(f"  left out, the same event as {twin['cluster_id']}: {str((r.get('titles') or [''])[0])[:100]!r} "
                f"({r['cluster_id']})")
            continue
        kept.append(r)
        keep.append(r["cluster_id"])
    return clusters[clusters["cluster_id"].isin(keep)].reset_index(drop=True)


AI_MIN_SIG = 5  # session 470 (digest audit fix 16): the AI section takes no story the scorer called commentary (under 5)

# Session 802 (docs/reviews/periodicals-plan-2026-10-23.md, Digest change 2): one topic, one item, the rest below. Seven of
# the 13 issues held three or more top-ten items of one sector (five on oil on 12 October, five on datacenter power on 13
# October), and a reader took the Digest for a letter on that one topic. A topic is the scorer's sector tag; two clusters
# of different sectors are one topic when they name a party in common and their lead titles share TOPIC_WORDS content
# words (the strike on Aramco's headquarters under oil, the Houthi attacks under geopolitics). At most ALSO_MAX stories
# fold under an item: an item with three "also" lines still reads in a breath, and a topic that fills more than that is
# in "By sector" below, so no story is lost (session 470's rule of fix 3).
TOPIC_WORDS = 2
ALSO_MAX = 3
# Session 2701 (rulings item 13): with the region in the key a sector may hold more than one item, and the ruling's words
# were "lets a sector hold two items": a third item of a sector folds under the sector's first, as one topic did before
SECTOR_MAX = 2
ALSO_LABEL = "Also on this topic:"


def region_key(r):
    """A cluster's region as the topic key reads it: the scorer's region (a US state, a country, or "global"), lower case;
    "" when the scorer gave none."""
    return re.sub(r"\s+", " ", str(r.get("region") or "").strip().lower())


def same_topic(a, b):
    """Two clusters are one topic: one sector in one region, or a party in common and TOPIC_WORDS or more content words
    shared by their lead titles. Session 2701 (rulings item 13, the 24-hour default): the key is the sector with the
    region, so Mexico's 8,200 MW and India's coal stocks are two topics though both are "generation"; a cluster whose
    region is not given is of every region (the sector alone decides, as before)."""
    if a.get("sector") == b.get("sector"):
        ra, rb = region_key(a), region_key(b)
        if not ra or not rb or ra == rb:
            return True
    if not party_words(a) & party_words(b):
        return False
    return len(title_words((a.get("titles") or [""])[0]) & title_words((b.get("titles") or [""])[0])) >= TOPIC_WORDS


def also_of(r):
    """The stories folded under a record (its `also` column), [] where there are none."""
    v = r.get("also") if isinstance(r, dict) else None
    return v if isinstance(v, list) else []


def one_per_topic(clusters, n, log, what="the top ten"):
    """Session 802: the first n clusters in rank with at most one item a topic. A later cluster of a topic already among
    the n, met before the n are filled, folds under that item (up to ALSO_MAX, in the item's `also` column: its lead
    title, sector, links, cluster id); past ALSO_MAX it is left for the sections below. Clusters met after the n are
    filled are left as they are. Returns (the n as a frame with an `also` column, the folded cluster ids)."""
    top, folded = [], set()
    for r in clusters.to_dict("records"):
        if len(top) >= n:
            break
        twin = next((k for k in top if same_topic(k, r)), None)
        if twin is None:
            same_sector = [k for k in top if k.get("sector") == r.get("sector")]
            if len(same_sector) < SECTOR_MAX:
                top.append(dict(r, also=[]))
                continue
            twin = same_sector[0]   # session 2701: the sector holds SECTOR_MAX items already
        if len(twin["also"]) >= ALSO_MAX:
            log(f"  {what}: left for the sections below, the topic of {twin['cluster_id']} is full: "
                f"{str((r.get('titles') or [''])[0])[:80]!r} ({r['cluster_id']})")
            continue
        twin["also"].append({"cluster_id": r["cluster_id"], "title": str((r.get("titles") or [""])[0]), "sector": r.get("sector"),
                             "links": list(r.get("links") or [])[:1], "parties": r.get("parties", "")})
        folded.add(r["cluster_id"])
        log(f"  {what}: folded under {twin['cluster_id']} (one topic, {r.get('sector')}): "
            f"{str((r.get('titles') or [''])[0])[:80]!r} ({r['cluster_id']})")
    out = pd.DataFrame(top, columns=list(clusters.columns) + ["also"]) if top else clusters.head(0).assign(also=None)
    return out.reset_index(drop=True), folded


def also_line(recs):
    """The line under an item for the stories folded under it: each its publisher's own title and its first outlet."""
    parts = [f"{nodash(x['title']).strip().rstrip('.')} ({link_text(x['links'])})" if x.get("links") else nodash(x["title"]).strip()
             for x in recs]
    return f"{ALSO_LABEL} " + "; ".join(parts) + "."


def item_lines(r, head, why, sources):
    """A top item's lines: the headline, the why line with its figures and sources, and the "also" line when the item
    carries folded stories (the line before it ends with two spaces, markdown's line break)."""
    L = [f"{head}", "   " + " ".join(x for x in (str(why).strip(), str(sources).strip()) if x)]
    if also_of(r):
        L[-1] += "  "
        L.append("   " + also_line(also_of(r)))
    return L


def select(clusters, digest_date, log, folder=None):
    """The issue's sections: (top 10, {group: clusters}, AI and power). Session 21, ruling 5: each cluster appears once;
    a section takes only clusters not shown above it. Session 470: a story an issue of the last seven days printed is
    left out first (not_shown_before), and the AI section takes significance 5 or more."""
    clusters = one_per_event(not_shown_before(clusters, earlier_issues(digest_date, folder=folder), log), log)
    top10, folded = one_per_topic(clusters, 10, log)   # session 802: one topic, one item, the rest folded under it
    used = set(top10["cluster_id"]) | folded
    by_group = {}
    for g, secs in GROUPS.items():
        by_group[g] = clusters[clusters["sector"].isin(secs) & ~clusters["cluster_id"].isin(used)].head(3)
        used |= set(by_group[g]["cluster_id"])
    ai = clusters[(clusters["ai"] >= 7) & (clusters["sig"] >= AI_MIN_SIG) & ~clusters["cluster_id"].isin(used)].head(5)
    return top10, by_group, ai


# Session 2701 (rulings item 3, the 24-hour default): the window opens where the previous issue's ended, so Monday's issue
# holds Friday evening and a weekday the run missed is caught up by the next; never more than WINDOW_CAP_HOURS back.
WINDOW_CAP_HOURS = 96
DEFAULT_HOURS = 24
STAMP_END = re.compile(r"for the \d+ hours to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC")
GENERATED_AT = re.compile(r"Generated by warehouse/news/brief\.py at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC")


def previous_end(digest_date, folder=None):
    """The end of the newest issue dated before `digest_date` (docs/digest/<date>.md): the time of its stamp's "for the
    N hours to <time> UTC", else of its "Generated by ... at <time> UTC" line; None when no earlier issue says one."""
    folder = folder or DIGEST_DIR
    try:
        names = sorted(f for f in os.listdir(folder) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", f) and f[:10] < str(digest_date))
    except OSError:
        return None
    for name in reversed(names):
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            text = f.read()
        m = STAMP_END.search(text) or GENERATED_AT.search(text)
        if m:
            return pd.Timestamp(m.group(1)).tz_localize("UTC")
    return None


def window_start(now, hours=None, prev_end=None, cap=WINDOW_CAP_HOURS):
    """Where the window opens. Given `hours` (the --hours flag), the hours before now, as before; else the previous issue's
    end (previous_end), but never more than `cap` hours back, and DEFAULT_HOURS back when there is no earlier issue or
    its end is not before now."""
    if hours is not None:
        return now - pd.Timedelta(hours=hours)
    if prev_end is None or prev_end >= now:
        return now - pd.Timedelta(hours=DEFAULT_HOURS)
    return max(prev_end, now - pd.Timedelta(hours=cap))


def window_hours(start, now):
    """The window's length in whole hours, as the stamp says it."""
    return int(round((now - start) / pd.Timedelta(hours=1)))


def window_rows(df, now, hours, start=None):
    """Session 2206 (digest audit, the window): the scored energy stories of the window, (rows, start, bounds). The window
    is the `hours` before `now` and ends at `now`: a story dated after the run (a feed's clock ahead, an item dated for
    its print edition) is left for the next issue, where until now it was taken and the stamp "the 24 hours to <the
    run>" was false. bounds is the earliest and the latest publish time among the rows, or None when there are none.
    Session 2701: `start`, when given, opens the window instead of `hours` (window_start)."""
    when = pd.to_datetime(df["event_date"], utc=True, format="ISO8601")
    start = now - pd.Timedelta(hours=hours) if start is None else start
    s = df[(df["scored_at"] != "") & (when >= start) & (when <= now)].copy()
    s["sig"] = s["significance"].astype(int)
    s["ai"] = s["ai_power_relevance"].astype(int)
    s = s[s["sig"] > 0]  # 0 = not about energy (rubric)
    held = when[s.index]
    return s, start, ((held.min(), held.max()) if len(s) else None)


def stamp_line(hours, start, now, n):
    """The issue's first line: the window's real bounds, both ends written (session 2206; the form "for the N hours to
    <time> UTC" stays first, as tests/test_session470.py reads it)."""
    return (f"ERW's weekday brief of energy news for the {hours} hours to {now:%Y-%m-%d %H:%M} UTC, "
            f"from {start:%Y-%m-%d %H:%M} UTC, from {n} scored stories.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Energy Digest")
    ap.add_argument("--hours", type=int, default=None, help="session 2701: a fixed window of this many hours (default: from the "
                    "previous issue's end, at most WINDOW_CAP_HOURS back; DEFAULT_HOURS when there is no earlier issue)")
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: today, UTC)")
    ap.add_argument("--out", help="write the digest to this path only (not docs/digest/<date>.md, not latest.md)")
    ap.add_argument("--weekend", action="store_true", help="write a digest for a Saturday or Sunday date anyway")
    ap.add_argument("--stories", help="read the scored stories from this file instead of news_stories (session 30: the "
                    "shadow scorer's view, warehouse/news/shadow.py)")
    ap.add_argument("--no-model", action="store_true", help="session 176: no model call (the daily model cap is reached, "
                    "warehouse/health.py budget): each headline is the lead story's own title as its publisher wrote it, "
                    "and the model-written summary of the numbers is left out; the digest still publishes")
    ap.add_argument("--now", help="session 807: the end of the window, YYYY-MM-DDTHH:MMZ (default: now), for a dry run of a "
                    "past day on the stories as they were scored; with --out only")
    args = ap.parse_args(argv)
    if args.now and not args.out:
        ap.error("--now is for a dry run: give --out too")
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
        now = pd.Timestamp(args.now).tz_localize("UTC") if args.now and pd.Timestamp(args.now).tzinfo is None else (
            pd.Timestamp(args.now).tz_convert("UTC") if args.now else pd.Timestamp.now(tz="UTC"))
        df = ip.read_series(args.stories or os.path.join(ip.OUT_DIR, NAME + ".csv"), NEWS_COLS)
        # session 2701 (rulings item 3): the window opens at the previous issue's end, capped at WINDOW_CAP_HOURS
        start = window_start(now, args.hours, None if args.hours is not None else previous_end(digest_date))
        hours = window_hours(start, now)
        s, start, bounds = window_rows(df, now, hours, start)   # session 2206: the window ends at the run, and is said so
        log(f"digest {digest_date}: {len(s)} scored energy stories in the {hours} hours from {start:%Y-%m-%d %H:%M} to "
            f"{now:%Y-%m-%d %H:%M} UTC" + (f"; the stories run from {bounds[0]:%Y-%m-%d %H:%M} to {bounds[1]:%Y-%m-%d %H:%M} UTC" if bounds else ""))
        if s.empty:
            raise RuntimeError("no scored stories in the window; not writing an empty digest")
        clusters = build_clusters(s)
        top10, by_group, ai = select(clusters, digest_date, log)
        shown = pd.concat([top10, *by_group.values(), ai]).drop_duplicates("cluster_id")
        if args.no_model:
            client, model = None, NO_MODEL
            heads, u, calls = own_titles(shown), SimpleNamespace(input_tokens=0, output_tokens=0), 0
            log(f"  --no-model: {len(heads)} headlines are the publishers' own titles; no model call")
        else:
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
             stamp_line(hours, start, now, len(s)), "",
             *([NO_MODEL_LINE, ""] if args.no_model else []),
             "## Top of the industry", ""]
        for i, r in enumerate(top10.to_dict("records"), 1):
            L += item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')})  ",
                            (why_line(r['why'], heads[r['cluster_id']]) + " " + detail(r, heads[r['cluster_id']])).strip(),
                            f"Sources: {link_text(r['links'])}")
        L += ["", "## By sector", ""]
        for g, c in by_group.items():
            L.append(f"**{g}**")
            L.append("")
            if c.empty:
                L.append("- no scored story in this group today")
            for r in c.to_dict("records"):
                L.append(f"- {heads[r['cluster_id']]} ({r['sector'].replace('_', ' ')}): "
                         + " ".join(x for x in (why_line(r['why'], heads[r['cluster_id']]), link_text(r['links'][:1])) if x))
            if g == "Policy":
                L += without_repeats(policy_actions_lines(start, now, log), L, log)
            L.append("")
        L += ["## AI and power", ""]
        if ai.empty:
            L.append("- no further story on AI and power today (any such story is listed above)")
        for r in ai.to_dict("records"):
            L.append(f"- {heads[r['cluster_id']]} ({r['sector'].replace('_', ' ')}): "
                     + " ".join(x for x in (why_line(r['why'], heads[r['cluster_id']]), link_text(r['links'][:1])) if x))
        nums = numbers_today(digest_date, log, clusters)   # session 804: the day's clusters, for the reasons beside the movers
        summary, su = (None, []) if args.no_model else numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        L += ["", "## ERW's Numbers Today", ""] + ([summary, ""] if summary else []) + nums
        # session 232: the chart of the day, chosen and drawn by code; omitted, with the reason logged, when there is none
        L += daily_chart_section(digest_date, log, args.out, stories=top10.to_dict("records"))   # session 805: the chart follows the day
        # session 23: the Fun fact, last; re-verified from its stored sources, omitted if it fails
        L += fun_fact_section(digest_date, log)
        # session 21: the method is on /about#digest; the generation record stays in the file, not on the page
        L += ["", "ERW", "", "---", "", "[How this is made.](/about#digest)", "",  # session 25: signed ERW
              f"<!-- Generated by warehouse/news/brief.py at {now:%Y-%m-%d %H:%M} UTC; run log "
              f"warehouse/output/logs/news_brief_{run_id}.log; model {model}; story data "
              "warehouse/output/news_stories.csv. -->"]
        L = drop_repeated_items(L, log)  # session 470: a repeat the sections did not see is dropped, not the issue
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
