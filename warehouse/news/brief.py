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


def is_google(url):
    """A Google News address: the link reaches Google's page, not the outlet's (the ingest's resolver, 22,619 of
    22,624 by 6 November 2026, got no redirect from Google)."""
    return "news.google.com" in str(url or "")


def direct_first(links):
    """The links with those reaching the outlet's own page first, each group in its order (session 1442)."""
    return [l for l in links if not is_google(l[1])] + [l for l in links if is_google(l[1])]


# Session 1443 (chain 149, fault 13): the scorer filed "CFTC looks into sale of futures equal to 6 million barrels in two
# minutes" under power_prices, and the Digest printed it under Power. A title about a commodity's price or futures
# (PRICE_STORY's words) is of that commodity's sector whatever the scorer's power tag.
POWER_TAGS = {"power_prices", "grid_conditions", "generation", "transmission"}
COMMODITY_SECTOR = {"oil": "oil", "gas": "gas"}


def sector_of(lead):
    """The cluster's sector: the scorer's, unless a power tag sits on a title about oil or gas prices (sector_of fixes it)."""
    sector = str(lead.get("sector") or "")
    if sector in POWER_TAGS:
        commodity = price_commodity({"titles": [str(lead.get("title") or "")]})
        if commodity in COMMODITY_SECTOR:
            return COMMODITY_SECTOR[commodity]
        # session 3335 (faults file row 120): a title about refining or road fuels is oil's, whatever power tag it got
        # ("U.S. Refineries Make Dramatic Shift Away From Gasoline" under Power, tagged power prices, 5 November)
        if REFINING.search(str(lead.get("title") or "")):
            return "oil"
    return sector


REFINING = re.compile(r"\b(?:refiner(?:y|ies|s)?|refining|gasoline|diesel(?! generat)|jet fuel)\b", re.I)   # 3335, row 120


def build_clusters(stories):
    rows = []
    for cid, g in stories.groupby("cluster_id"):
        g = g.sort_values(["sig", "event_date"], ascending=[False, True])
        lead = g.iloc[0]
        rows.append({
            "cluster_id": cid, "sig": int(g["sig"].max()), "ai": int(g["ai"].max()),
            # session 21: the MW and price of the cluster are the first any of its stories' scored fields hold
            "sector": sector_of(lead), "region": str(lead.get("region", "") or ""), "why": lead["why"], "mw": next((x for x in g["mw"] if x), ""),
            "price": next((x for x in g["price_mentioned"] if x), ""), "parties": lead["parties"],
            # session 3318 (faults file row 107): the story each figure came from, which the block's key names, so
            # scripts/check_digest.py reads the row that holds it (the cluster's id named Hart Energy's "$2B" where JPT's
            # "$2.1 Billion" was printed, 12 November)
            "mw_id": next((e for x, e in zip(g["mw"], g["event_id"]) if x), "") if "event_id" in g else "",
            "price_id": next((e for x, e in zip(g["price_mentioned"], g["event_id"]) if x), "") if "event_id" in g else "",
            "first": g["event_date"].min(), "n": len(g),
            "outlets": g["source"].astype(str).str.strip().str.lower().nunique(),   # session 2701: the outlets that ran it
            # session 470: one link an address (two stories of a cluster at one address printed it twice); session 1442
            # (fault 23): a link that reaches the outlet's own page before one that reaches Google's, so the item's first
            # source is the outlet's wherever one story of the cluster has it (the ingest's resolver reaches no outlet)
            "links": direct_first(list({r.source_url: (r.source, r.source_url) for r in g.itertuples()}.values()))[:3],
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
    return {h["cluster_id"]: headline_style(nodash(h["headline"])) for h in out}, SimpleNamespace(
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
    """A headline for comparison: money in the one style and the publisher's suffix off (why_fallback), then letters,
    digits and spaces only. Session 1437 (faults 10 and 33): "$100" and "USD 100" are one, so a fallback that is the
    headline in the money style prints nothing, as item 16 says."""
    return re.sub(r"[^a-z0-9 ]+", "", why_fallback(h).lower()).strip()


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
        if MOVER_LINE.match(ln):   # session 1986 (row 91): a mover is a figure; its reason links a story above by design
            continue
        if m and not ln.startswith("- no "):  # "- no scored story in this group today" is not an item
            heads.append(norm_headline(m.group(1) or m.group(2)))
            urls += re.findall(r"\]\((https?://[^)]+)\)", ln)
        elif ln.startswith("   ") and ("Sources:" in ln or ALSO_RE.match(ln.strip())):  # 802: the also line too (1466: either label)
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


MOVER_LINE = re.compile(r"^- [^:\n]+: -?[\d,]+\.\d{2} \S+ on \d{4}-\d{2}-\d{2}, (?:up|down) ")   # mover_text's form


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
        # session 1986 (faults file row 91): a mover is a figure, not a story item; its reason's link is a story printed above
        # by design, and the link dropped Brent's move from "What moved most" on 12 November (Henry Hub's on main's run)
        if not m or ln.startswith("- no ") or MOVER_LINE.match(ln):
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
        if ln.startswith(("## ", "### ")):   # session 3336 (row 122): the Roundup's weekend list and its five are two lists
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
    # Session 2701 (rulings item 15, the 24-hour default): a held outlet's item keeps its link. The hold is about
    # republishing text, and a link republishes nothing; `licensed` is kept in the signature for the callers.
    return f"[{outlet_name(src)}]({url})" + (" (via Google News)" if "news.google.com" in str(url) else "")


# Session 1978 (faults file row 83): a feed's title is not the outlet's name ("JPT Homepage", 115 stories of
# news_stories; "California State Portal | CA.gov", 46): the name an issue prints drops a " Homepage" tail and keeps the
# last part of a "Portal | site" title
OUTLET_NAMES = {"California State Portal | CA.gov": "CA.gov", "IEA - International Energy Agency": "IEA",   # 3312: row 102
                "ft.com": "Financial Times", "wsj.com": "WSJ"}   # session 3352 (rows 133, 134): the paper's name, as its other links give it


def outlet_name(src):
    s = str(src or "").strip()
    if s in OUTLET_NAMES:
        return OUTLET_NAMES[s]
    return re.sub(r"\s+Home ?page$", "", s, flags=re.I) or s


def link_text(links, licensed=None):
    # session 470 (digest audit fix 7, roundup audit fix 4): a Google News address does not reach the outlet (the ingest
    # records it in url_resolved), and the reader is told where the link goes; session 803: source_text; session 807: a
    # source printed once (two stories of one cluster at one held outlet printed "POWER Magazine, POWER Magazine")
    # session 3352 (faults file row 132): one outlet once, whatever its addresses ("[Bloomberg.com] (via Google News),
    # [Bloomberg.com] (via Google News)", two Google addresses of one outlet, W41)
    seen, out = set(), []
    for src, url in links:
        k = outlet_name(src).lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(source_text(src, url, licensed))
    return ", ".join(out)


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


# Session 1479 (chain 154, fault 56 of docs/reviews/periodicals-faults-2026-11-05.md): the model's headline wrote a sum
# three ways on the same stories ("a $4 Billion, 702 MW ..." in one run, "a 4 billion USD fuel-cell project" in the next);
# the issue's form is "USD 4 billion". A code after the number is read as one before it.
TRAILING_CODE = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s?(billion|million|trillion|bn|mn)\s+(USD|CAD|AUD|EUR|GBP)\b", re.I)


def headline_style(head):
    """A headline the model wrote, its sums in the one money style (money_style), "4 billion USD" read as "USD 4
    billion", and the voice's adjectives out (plain, session 1480). The publisher's own titles (own_titles, the no-model
    path) are not passed through it."""
    h = TRAILING_CODE.sub(lambda m: f"{m.group(3).upper()} {m.group(1)} {SCALE[m.group(2).lower()]}", str(head or ""))
    # session 1480 (chain 154, fault 57): an adjective of the voice's list goes from the ERW's own headline as from its why
    # line ("... as third major US offshore wind farm" to "... as third US offshore wind farm")
    return plain(money_style(h))


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
# Session 1437 (chain 149, faults 7 to 11 of docs/reviews/periodicals-faults-2026-11-05.md): a verb that asserts nothing
# in place of a fact ("capacity expansion signals rising demand"), and a line whose content words are the headline's
# (half or more of them: "Major oil company nearing deal to invest in Venezuela's oil fields" under "Exxon nears
# preliminary deal to invest in Venezuela's oil fields"). Either fails the check and the item prints the headline alone.
HOLLOW_VERBS = ("signals", "demonstrates", "reflects", "underscores", "highlights")
HOLLOW = re.compile(r"\b(?:signals?|demonstrates?|reflects?|underscores?|highlights?"
                    # session 1462 (chain 150): their -ing and past forms, which the scorer's new prompt still writes
                    # ("Woodfibre LNG accelerates timeline while AECO spot curve softens, signaling weaker 2027 North
                    # American gas pricing.", the probe of 26 October's top ten, runs/s1462/)
                    r"|signal(?:l)?(?:ing|ed)|demonstrat(?:ing|ed)|reflect(?:ing|ed)|underscor(?:ing|ed)|highlight(?:ing|ed))\b", re.I)
# Session 1462: a trailing clause led by a comma and one of those -ing forms is the line's inference, not its fact; why_line
# cuts it and keeps what comes before ("..., signaling weaker 2027 North American gas pricing" goes), then the check runs
HOLLOW_TAIL = re.compile(r",\s*(?:signal(?:l)?ing|demonstrating|reflecting|underscoring|highlighting)\b[^.;!?]*", re.I)
RESTATES_SHARE = 0.5
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
    out += [f"hollow verb: {m.lower()}" for m in HOLLOW.findall(t)]
    if sentence_end(t):
        out.append("two sentences")
    for n in sorted(figures_of(t) & figures_of(head)):
        out.append(f"figure of the headline: {n}")
    share = restates(t, head)
    if head and share >= RESTATES_SHARE:
        out.append(f"restates the headline: {share:.2f}")
    # session 1458 (chain 150, fault 7): a line that names nothing the headline lacks, and leans on the headline's words or
    # strings two clauses on a semicolon, fails; named last, so a line with another fault is named by that one
    if head and scale_against(t, head):   # session 1466 (fault 44)
        out.append(f"scale word against the headline's figure: {scale_against(t, head)}")
    if head and not out and not new_things(t, head) and (share >= NOTHING_NEW_SHARE or ";" in t):
        out.append("names nothing the headline lacks")
    return out


# Session 1466 (chain 150, fault 44): "Gigawatt-scale hyperscale power deal ..." under "AEP and Google advance a 702 MW
# Bloom Energy fuel-cell project": a scale word that the headline's own capacity contradicts. why_line takes the word out
# (as plain() takes an adjective out) and why_check names it in a raw line.
SCALE_WORD = re.compile(r"\b(?:multi-?)?(?:gigawatt|GW)[- ]scale\s*", re.I)
HEAD_MW = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?(MW|GW)\b", re.I)


def scale_against(text, head):
    """The scale word of a line ("gigawatt-scale") when every capacity the headline states is under 1,000 MW; "" when the
    line has none, or the headline states no capacity or one of a gigawatt or more."""
    m = SCALE_WORD.search(str(text or ""))
    caps = [float(v.replace(",", "")) * (1000 if u.upper() == "GW" else 1) for v, u in HEAD_MW.findall(str(head or ""))]
    if not m or not caps or max(caps) >= 1000:
        return ""
    return m.group(0).strip().lower()


# Session 1458 (chain 150, fault 7 of docs/reviews/periodicals-faults-2026-11-05.md): "LNG or gas project faces executive
# departures and alleged Russian involvement claims; geopolitical risk to US energy sector." under "US executives quit
# $25bn gas venture over claims of secret Russian control" shares 0.29 of its content words with the headline, under
# RESTATES_SHARE, and holds no hollow verb, so it printed; it names no party, place, date, quantity or rule the headline
# lacks. Such a line fails when it also shares a quarter of its words with the headline, or strings two clauses on a
# semicolon ("AI data center financing; power infrastructure capex commitment."). Over the stored scored stories of
# significance 7 and above whose lines passed the check before (news_stories on 6 November), 167 of 784 fail it; the rule
# alone, as the faults file words it, would refuse 560 of 784 (NOTHING_NEW_SHARE = 0 makes it so: for the owner).
NOTHING_NEW_SHARE = 0.25
# words with a capital that name no one: the country of the issue, the trade's acronyms and units
GENERIC_NAMES = set("""us u.s usa u.s.a america american ai lng ev evs gw mw gwh mwh twh kv ceo cfo ipo esg iso rto ppa ppas
capex opex bess hvdc llm""".split())
MONTH_DAY = set("""january february march april may june july august september october november december jan feb mar apr
jun jul aug sep sept oct nov dec monday tuesday wednesday thursday friday saturday sunday""".split())
NAME_WORD = re.compile(r"[A-Za-z][A-Za-z0-9&'.-]*[A-Za-z0-9]|[A-Za-z]")
# a quantity in words is a quantity ("Half of India's coal plants operating with low fuel stocks")
NUMBER_WORDS = set("""half third thirds quarter quarters two three four five six seven eight nine ten eleven twelve dozen
dozens hundred hundreds thousand thousands double doubled doubles triple tripled twice""".split())


def _name_stem(w):
    w = re.sub(r"'s$", "", w.lower().strip(".'"))
    return w[:-1] if w.endswith("s") and len(w) > 4 else w


def _held_by(w, head_stems):
    s = _name_stem(w)
    if s in head_stems:
        return True
    # a demonym and its country, a name and its adjective ("Russian" and "Russia", "Qatari" and "Qatar")
    return len(s) >= 5 and any(len(h) >= 5 and s[:5] == h[:5] for h in head_stems)


def new_things(text, head):
    """Session 1458 (fault 7): what the line names that the headline does not, as a list: a number the headline does
    not hold (an amount, or a year: a date), a quantity in words (NUMBER_WORDS), a month or a weekday, or a name (a word
    with a capital letter, past the line's first word unless that word is an acronym or carries a capital inside, and
    not a word of GENERIC_NAMES). [] when the line names nothing the headline lacks."""
    t, h = str(text or ""), str(head or "")
    hs = {_name_stem(w) for w in NAME_WORD.findall(h)}
    hn = {n.replace(",", "") for n in NUMBER.findall(h)}
    out = [n for n in (x.replace(",", "") for x in NUMBER.findall(t)) if n not in hn]
    for i, w in enumerate(NAME_WORD.findall(t)):
        s = _name_stem(w)
        if w.lower() in NUMBER_WORDS:
            if w.lower() not in {x.lower() for x in NAME_WORD.findall(h)}:
                out.append(w)
            continue
        if s in MONTH_DAY:
            if not _held_by(w, hs):
                out.append(w)
            continue
        if not w[0].isupper() or s.replace(".", "") in GENERIC_NAMES or s in GENERIC_NAMES:
            continue
        if i == 0 and not any(c.isupper() for c in w[1:]):
            continue
        if not _held_by(w, hs):
            out.append(w)
    return out


def content_words(text):
    """The content words of a line for restates(): lower case, money in the one style, STOP words and words under three
    letters out, a plural's s off (so "executives" and "executive" are one)."""
    out = set()
    for w in re.findall(r"[a-z0-9]+", money_style(str(text or "")).lower()):
        if w in STOP or len(w) < 3:
            continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def restates(text, head):
    """The share of the line's content words that the headline holds: 1.0 when the line is the headline, 0 when nothing
    of it is. Over the 13 issues of 25 September to 23 October the lines at 0.5 and above restate ("Cost and regulatory
    hurdles threaten AI sector's plans to use nuclear power" under "AI's nuclear power push runs into cost and
    regulatory hurdles"); those under it add a fact (0.46: "Awards fell short of the 800-MW target, showing PJM
    capacity strain" under "Maryland's first bulk storage procurement nets 440 MW")."""
    ww = content_words(text)
    if not ww or not head:
        return 0.0
    return len(ww & content_words(head)) / len(ww)


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
    t = HOLLOW_TAIL.sub("", t)   # session 1462: a trailing ", signaling ..." clause is cut, its fact kept
    if head and scale_against(t, head):   # session 1466 (fault 44): the scale word goes, as an adjective does
        t = SCALE_WORD.sub("", t, count=1).strip()
        t = t[:1].upper() + t[1:]
    # "an $800MM loan" was right as written; as "USD 800 million" the article follows the code as it is said
    t = re.sub(r"\b([Aa])n? (USD|CAD|EUR|GBP|AUD)\b",
               lambda m: m.group(1) + ("n " if m.group(2) == "AUD" else " ") + m.group(2), t)
    # session 3353 (faults file row 135): an acronym said letter by letter from a vowel sound takes "an" ("a LNG expansion")
    t = re.sub(r"\b([Aa]) (LNG|SMR|NRC|EIA|IEA|EV)\b", lambda m: m.group(1) + "n " + m.group(2), t)
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
    if r["parties"] and bits:
        # kept as written beside a figure: the Roundup reads the parties of a stored issue's item here (roundup.ISSUE_FIELDS)
        bits.append("Parties: " + r["parties"])   # session 3350 (row 130): a label in capitals; the Roundup reads either case
    elif r["parties"]:
        # session 1979 (faults file row 84): with no figure, a party the headline names is not printed again ("parties:
        # Repsol." under "Repsol takes final investment decision ..."), and the others read as a sentence
        rest = [p.strip() for p in str(r["parties"]).split(";") if p.strip() and not party_in_head(p.strip(), head)]
        return f"Also named: {', '.join(rest)}. " if rest else ""
    return ("; ".join(bits) + ". ") if bits else ""


COMMON_FIRST = {"united", "the", "new", "north", "south", "west", "east", "great", "federal", "national", "state",
                "department", "american", "general", "energy", "power", "royal", "central", "first"}


def party_in_head(party, head):
    """Session 3313 (row 84, refined): whether the headline already names a party: the name itself, or its initials as a
    word ("DOE" for the Department of Energy, "US" for the United States); a party that names no one ("unnamed
    hyperscaler", "undisclosed buyer") counts as named, so it is never printed as one."""
    low, h = party.lower().rstrip("+*. "), str(head or "")   # session 3367 (row 143): "OPEC+" is named by "OPEC"
    if low.startswith(("unnamed", "undisclosed", "an unnamed", "a unnamed")) or low in h.lower():
        return True
    # session 3349 (faults file row 128): a party that is a description, not a name ("US regulator", "a utility"): a word
    # in lower case other than of, the, and, for, de; it is never printed as one named
    if any(w[:1].islower() and w not in ("of", "the", "and", "for", "de", "du", "la") for w in party.split()):
        return True
    if len(low) > 4 and low.endswith("s") and re.search(rf"\b{re.escape(low[:-1])}\b", h.lower()):   # "Houthis", "Houthi attacks"
        return True
    initials = "".join(w[0] for w in re.findall(r"[A-Za-z][\w'-]*", party) if w[0].isupper())
    if len(initials) >= 2 and re.search(rf"\b{initials}\b", h):
        return True
    # session 3332 (faults file row 113): a name's distinctive first word ("Saudi" of Saudi Arabia, "Ontario" of Ontario
    # Power Generation); a common first word ("United", "New", "Department") names no one by itself
    words = party.split()
    if (len(words) > 1 and len(words[0]) >= 4 and words[0][0].isupper() and words[0].lower() not in COMMON_FIRST
            and re.search(rf"\b{re.escape(words[0])}\b", h)):
        return True
    if initials == "DOE" or party.lower() == "department of energy":
        return bool(re.search(r"\bDOE\b|\bEnergy Department\b", h))
    return False


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
        # session 1439: news_stories is cited by name alone (cite_short would list its hundred outlets)
        items = [f"[{i}] {'`news_stories`' if t == 'news_stories' else cite_short(t)}" + (f"; {self.extra[t]}" if t in self.extra else "")
                 for i, t in enumerate(self.tables, 1)]
        return ["", "Tables: " + "; ".join(items) + "."]


SUMMARY_SYSTEM = """You write the summary above the numbers section of the ERW's energy brief: two or three plain sentences
saying what the numbers say (for example where power was dearest or cheapest, how prices moved, what stands out).
Use only numbers written in the section, exactly as they are written there: do not compute new numbers (no sums,
differences, ratios or percentages that are not already in the section) and do not round them. One number a clause:
never "each rose 7.46 and 7.47" or two figures joined by "and" for two things; say each thing in its own clause.
No hype, no advice, no em dashes. Return JSON with the field summary.""" + VOICE_NOTE
# session 1447 (chain 149, fault 38): a summary sentence that pairs two figures under "each" or "respectively" is not
# one number a clause; the summary is left out rather than printed so
PAIRED = re.compile(r"\beach\b[^.;]*\d[\d,.]*\s+and\s+\d[\d,.]*|\brespectively\b", re.I)
SUMMARY_SCHEMA = {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"],
                  "additionalProperties": False}


def section_pool(lines):
    """The section's text for the literal check: without footnote markers and the footnote list."""
    return "\n".join(re.sub(r"\[\d+\]", "", ln) for ln in lines if not ln.startswith("Tables: "))


def summary_check(text):
    """Session 1447 (fault 38): the problems of a numbers summary: a clause pairing two figures ("each rose about 7.46
    and 7.47"); [] when it passes."""
    return ["two figures in one clause"] if PAIRED.search(str(text or "")) else []


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
        text = re.sub(r"\bunchanged at 0(?:\.0+)?%", "unchanged", text)   # session 1975 (row 80): "unchanged at 0.0%"
        bad = chat_ask.unverified(text, [pool]) + summary_check(text)   # session 1447 (fault 38): one number a clause
        if not bad:
            log(f"  numbers summary: attempt {attempt} passed the literal check")
            return text, usages
        log(f"  numbers summary: attempt {attempt} has numbers not in the section, or two in one clause: {bad}")
        msgs = msgs + [{"role": "assistant", "content": json.dumps({"summary": text})},
                       {"role": "user", "content": "These numbers are not in the section as written, or two figures share one clause: " + ", ".join(bad)
                        + ". Rewrite the summary using only numbers written in the section, one number a clause."}]
    log("  numbers summary: omitted (failed the checks twice)")
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
# session 1440: a story that says "oil prices" or "crude" names the crude benchmarks; "gas prices" names Henry Hub
PRICE_WORDS = {"Henry Hub natural gas": ("henry hub", "natural gas price", "gas prices"), "WTI Cushing crude": ("wti", "oil price", "crude price"),
               "Brent crude": ("brent", "oil price", "crude price"),
               "ERCOT": ("ercot",), "CAISO": ("caiso",), "NYISO": ("nyiso",), "MISO": ("miso",),
               "SPP": ("southwest power pool", " spp "), "ISO-NE": ("iso-ne", "iso new england", "new england")}
# session 1975 (faults file row 80): a headline that moves oil or crude names the crude benchmarks ("Oil settles USD 3
# higher on attacks on Saudi energy sites", 12 November, top 2), the verb right after the noun ("Saudi oil production
# surges" is output, not a price)
CRUDE_MOVE = re.compile(r"\b(?:oil|crude)(?: prices?| futures)? (?:settles?|settled|rises?|rose|falls?|fell|jumps?|jumped|slips?|"
                        r"slipped|climbs?|climbed|drops?|dropped|gains?|gained|surges?|surged|tumbles?|tumbled|slides?|slid|sinks?|sank)\b")


FOREIGN_GAS = re.compile(r"\b(?:euros?|eu|europe|european|ttf|dutch|asia|asian|jkm|japan|korea|china|uk|british|nbp|germany|"
                         r"german)\b")   # session 3334, row 115


def names_price(label, text):
    """Session 1975: whether `text` (a story's title and why line, lower case, padded with spaces) names the price."""
    words = PRICE_WORDS.get(label) or PRICE_WORDS.get(label.split(" ")[0]) or ()
    # session 3334 (faults file row 115): a story of another gas market names no move of Henry Hub's ("Natural gas prices
    # hit 100 euros per MWh as EU confronts refinery closures", W44, given as the reason for Henry Hub's 12.9% fall)
    if label == "Henry Hub natural gas" and "henry hub" not in text and FOREIGN_GAS.search(text):
        return False
    if any(w in text for w in words):
        return True
    if label == "Henry Hub natural gas":   # session 3330 (faults file row 110): "Natural Gas Forward Rally"
        return bool(GAS_MOVE.search(text))
    return label in ("WTI Cushing crude", "Brent crude") and bool(CRUDE_MOVE.search(text))


# Session 3330 (faults file row 110): a headline that moves US natural gas names Henry Hub ("Record LNG Demand Ignites
# Natural Gas Forward Rally", 11 November), as CRUDE_MOVE does for the crudes; "gas" alone is not read (a gas plant)
GAS_MOVE = re.compile(r"\bnatural gas(?: prices?| futures| forwards?| forward prices)? (?:rall(?:y|ies|ied)|settles?|settled|"
                      r"rises?|rose|falls?|fell|jumps?|jumped|slips?|slipped|climbs?|climbed|drops?|dropped|surges?|surged|"
                      r"tumbles?|tumbled|slides?|slid|sinks?|sank|soars?|soared|plunges?|plunged)\b")


# Session 3312 (faults file row 104): a story names a move only when its direction words do not contradict it. W45's
# Brent fell 18.6% on the week and "ConocoPhillips boosts dividend ... on higher oil prices" counted as naming it
RISE_WORDS = re.compile(r"\b(?:rise|rises|rose|rising|higher|jumps?|jumped|surges?|surged|gains?|gained|climbs?|climbed|"
                        r"rall(?:y|ies|ied)|soars?|soared|spikes?|spiked|"
                        r"supports?|supported|lifts?|lifted|boosts?|boosted|rebounds?|rebounded)\b")   # 3334: W44's "support"
FALL_WORDS = re.compile(r"\b(?:fall|falls|fell|falling|lower|drops?|dropped|slumps?|slumped|tumbles?|tumbled|slides?|slid|"
                        r"sinks?|sank|plunges?|plunged|declines?|declined|slips?|slipped|"
                        r"weighs?|weighed|pressures?|pressured|routs?|retreats?|retreated)\b")


def agrees(text, pct):
    """Row 104: False when the text speaks of the opposite direction only (a rise beside a fall, or a fall beside a rise);
    True otherwise, and always when the move's sign is not given."""
    if pct is None:
        return True
    up, down = bool(RISE_WORDS.search(text)), bool(FALL_WORDS.search(text))
    return not ((float(pct) < 0 and up and not down) or (float(pct) > 0 and down and not up))


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


def price_named(label, clusters, pct=None):
    """Session 1446: whether a story of the day or the week names the price (PRICE_WORDS in its title or why line),
    whatever its why line prints: a move is "named" for the opening number's choice even when the story's why line
    fails the check and no reason is printed beside the mover."""
    words = PRICE_WORDS.get(label) or PRICE_WORDS.get(label.split(" ")[0]) or ()
    if clusters is None or not len(clusters) or not words:
        return False
    for r in clusters.to_dict("records"):
        text = f" {str((r.get('titles') or [''])[0])} {r.get('why') or ''} ".lower()
        if names_price(label, text) and agrees(text, pct):   # row 104
            return True
    return False


def price_story(label, clusters, pct=None):
    """Session 3312 (faults file row 101): the highest-ranked story of `clusters` that names the price (names_price), as
    " Named in the week's stories: <its title> (<its first link>)." in the money style; "" when none names it. The
    Roundup's opening move prints it when no naming story's why line passes the check (price_reason)."""
    if clusters is None or not len(clusters):
        return ""
    for r in clusters.to_dict("records"):
        title = str((r.get("titles") or [""])[0])
        text = f" {title} {r.get('why') or ''} ".lower()
        # row 126: a title with a price of its own ("Oil Prices Climb Above $106", beside WTI's 108.21) is passed over
        if names_price(label, text) and agrees(text, pct) and not MONEY.search(title):   # row 104
            return f" Named in the week's stories: {money_style(nodash(title)).strip().rstrip('.')} ({link_text(list(r.get('links') or [])[:1])})."
    return ""


def price_reason(label, clusters, pct=None):
    """The why line of the day's highest-ranked scored story that names the price (PRICE_WORDS), with its outlet, as
    the reason beside a mover; "" when no story of the day names it (the figure then stands with no reason)."""
    words = PRICE_WORDS.get(label) or PRICE_WORDS.get(label.split(" ")[0]) or ()
    if clusters is None or not len(clusters) or not words:
        return ""
    for r in clusters.to_dict("records"):
        title = str((r.get("titles") or [""])[0])
        text = f" {title} {r.get('why') or ''} ".lower()
        if names_price(label, text) and agrees(text, pct):   # row 104
            why = why_line(r.get("why") or "", title)
            # session 1465 (chain 150, fault 43): a price's reason names something (a party, a place, a date, a quantity
            # or a rule the title does not), whatever its share of the title's words: "Commodity price movement driven
            # by fundamentals, impacts market sentiment and producer economics." beside Henry Hub named nothing
            if not why or not new_things(why, title):
                continue
            # session 3348 (faults file row 126): a line with prices of its own ("Brent near USD 106.80 and WTI USD 93.78")
            # contradicts the close it would explain (WTI at 108.21 the same week); the next naming story is tried
            if MONEY.search(why):
                continue
            return f" Reason, from the day's stories: {why} ({link_text(list(r.get('links') or [])[:1])})"
    return ""


def demand_lines(digest_date, log, notes, store=None):
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
    if store is not None:   # session 2703: the numbers block's physical row
        store.update(top=top, day=day, before=day - pd.Timedelta(days=364))
    ref = notes.ref("eia930_all_demand", "balancing authority us48")
    out[-1] += f"peaked at {top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC {ref}; "
    before = day - pd.Timedelta(days=364)
    try:
        old = peak(before)
    except Exception as exc:
        log(f"  numbers: US48 demand a year before unavailable: {exc!r}")
        old = None
    span = "year"
    if old is None:
        # session 1439 (chain 149, fault 3): the year before is the data machine's (rulings item 18); until it is held the
        # change is against the same weekday a week before, which the hourly table's window holds, said so
        week = day - pd.Timedelta(days=7)
        try:
            old = peak(week)
        except Exception as exc:
            log(f"  numbers: US48 demand a week before unavailable: {exc!r}")
            old = None
        if old is None:
            out[-1] += (f"the same weekday a year before ({before:%Y-%m-%d}) and a week before ({week:%Y-%m-%d}) are not held: "
                        "the hourly table's window does not reach them.")
            return out
        span, before = "week", week
        if store is not None:
            store["before"] = week
    if store is not None:
        store.update(old=old, span=span)
    pct = 100 * (float(top["value"]) / float(old["value"]) - 1) if float(old["value"]) > 0 else None
    out[-1] += (f"the same weekday a {span} before ({before:%Y-%m-%d}) peaked at {old['value']:,.0f} MW in the hour starting "
                f"{old['ts_utc']:%Y-%m-%d %H:%M} UTC {ref}" + (f", so {pct:+.1f}% on the {span}." if pct is not None else "."))
    if span == "week":
        out[-1] += " The same weekday a year before is not held (the hourly table's window does not reach it)."
    return out


def mover_list(cands, clusters):
    """"What moved most": its heading and its lines, from the candidates sorted by the size of their move. Session 1986
    (faults file row 92): a price that did not move is no "largest move" ("Henry Hub natural gas: 3.00 USD/MMBtu ..., up
    0.00 USD/MMBtu (0.0%)" with a reason, 12 November): the list ranks the moves, its heading counts them, and the
    unchanged prices are named on a line of their own, with no figure (each is printed and keyed in its table below)."""
    moved = [c for c in cands if abs(float(c["pct"])) >= 0.05]
    still = [c for c in cands if abs(float(c["pct"])) < 0.05]
    ranked = moved[:MOVERS_N]
    count = "largest move" if len(ranked) == 1 else f"{len(ranked)} largest moves"
    movers = ["", f"**What moved most** (the {count} in percent among the main hubs' day-ahead averages against the "
              "day before, and EIA's spot closes against the close before them):", ""]
    for c in ranked:
        movers.append(f"- {c['label']}: {c['v']:.2f} {c['unit']} on {c['d']:%Y-%m-%d}, {'up' if c['ch'] >= 0 else 'down'} "
                      f"{abs(c['ch']):.2f} {c['unit']} ({abs(c['pct']):.1f}%) from {c['pv']:.2f} {c['unit']} on {c['pd']:%Y-%m-%d} {c['ref']}."
                      + price_reason(c["key"], clusters, c["pct"]))
    if not cands:
        movers.append("- no price with a day before it is held, so no move is ranked.")
    return movers


def unchanged_line(cands):
    """Session 1986 (row 92): the prices that did not move, named with no figure, after the list's "Not ranked" line."""
    still = [c["label"] for c in cands if abs(float(c["pct"])) < 0.05]
    return ["- Unchanged: " + ", ".join(still) + "."] if still else []


def numbers_today(digest_date, log, clusters=None, facts=None, now=None):
    """The numbers section (session 804: what moved). clusters: the day's clusters (build_clusters), for the reasons.
    facts (session 2703): a dict filled with the candidates of the moves (each with its table and reason) and US48
    demand's peak, for the opening number and the numbers block. now (session 1439, fault 1): the issue's cutoff; a
    close dated after it is not read, so a dry run of a past day reproduces the day and no issue prints a row dated
    after its own cutoff (the 26 October dry run opened with a Henry Hub close of 3 November)."""
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
            cell = f"{h['n1']} of {h['x1']} hours held, no daily mean"   # session 1882 (faults file row 71)
        if not h["held"]:
            prev = f"{h['m0']}" if h["m0"] is not None else ("" if h["pause"] else f"{h['n0']} of {h['x0']} hours held, no daily mean")
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
    # session 1976 (faults file row 81): EIA's lag varies (one day on 12 November, five on 8 November); each line gives its own
    lines += ["", "**Latest fuel spot closes** (EIA, trading dates; EIA publishes a close from one day to about a week after its day):", ""]
    fuels = []
    try:
        fuel = erw.fetch("eia_fuel_spot_prices")
        if now is not None:
            fuel = fuel[fuel["ts_utc"] <= pd.Timestamp(now)]
        for label, entity in FUELS:
            s = fuel[fuel["entity"] == entity].sort_values("ts_utc")
            last = s.iloc[-1]
            age = (pd.Timestamp(digest_date).tz_localize("UTC") - last["ts_utc"]).days
            # a close dated after the issue's day: the table was read later than the issue (a rerun, a check)
            when = (f"{age} day{'' if age == 1 else 's'} before this issue" if age >= 0 else "dated after this issue's day: the table was read later")
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
                          pv=float(h["m0"]), pd=before, ref=notes.ref(h["table"]), table=h["table"], node=h["node"], **mv))
    for f in fuels:
        mv = day_move(f["v"], f["d"], f["pv"], f["pd"])
        if mv["pct"] is None:
            continue
        cands.append(dict(f, key=f["label"], table="eia_fuel_spot_prices", **mv))
    cands.sort(key=lambda c: (-abs(c["pct"]), c["label"]))
    movers = mover_list(cands, clusters)
    not_ranked = [f"{h['label']} {h['node']} ({LICENSED_NOTE})" for h in hubs if h["held"] and not h["pause"]]
    not_ranked += [f"{h['label']} {h['node']} (paused by the ERW since {h['pause']['paused_on']})" for h in hubs if h["pause"]]
    not_ranked += [f"{name} ({why})" for name, why in NOT_HELD]
    movers.append("- Not ranked: " + "; ".join(not_ranked) + ".")
    movers += unchanged_line(cands)   # session 1986 (row 92)
    lines = movers + [""] + lines
    store = {}
    lines += demand_lines(digest_date, log, notes, store)
    if facts is not None:   # session 2703
        for c in cands:
            c["reason"] = price_reason(c["key"], clusters, c["pct"])
            c["named"] = price_named(c["key"], clusters, c["pct"])   # session 1446: named, whether or not a reason prints
        facts.update(cands=cands, demand=store)
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
    return [policy_line(r, kinds) for r in a.to_dict("records")]


def policy_line(r, kinds):
    """One policy action under Policy. Session 1980 (faults file row 85, row 72's fault in the Digest): a why line that
    failed left "(DOE news release, policy action):  [DOE](...)", a colon introducing nothing and a double space; the line
    then closes on its bracket with a stop. The site keeps the line under a held news index by ", policy action)"
    (site/lib/digest.ts)."""
    head = f"- {money_style(r['title'])} ({r['agency']} {kinds.get(r['action_type'], r['action_type'])}, policy action)"   # row 86
    why = why_line(r["why"], r["title"]).strip()
    return f"{head}: {why} [{r['agency']}]({r['source_url']})" if why else f"{head}. [{r['agency']}]({r['source_url']})"


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
# Session 1466 (chain 150, fault 45): a story folded because its sector holds SECTOR_MAX items already is not of the item's
# topic ("Also on this topic: Lambda to develop four-building data center campus in Lowndes County, Alabama" under AEP and
# Google's Wyoming fuel cells, the dry run of 6 November); it is said to be of the sector. Either label opens the line.
ALSO_SECTOR = "Also in {sector}:"
ALSO_RE = re.compile(r"^Also (?:on this topic|in [a-z][a-z ]*):")


def region_key(r):
    """A cluster's region as the topic key reads it: the scorer's region (a US state, a country, or "global"), lower case;
    "" when the scorer gave none."""
    return re.sub(r"\s+", " ", str(r.get("region") or "").strip().lower())


# Session 1438 (chain 149, fault 12): a price story's topic is its commodity, whatever region the scorer gave. On
# 26 October "Oil prices rise on fears of Middle East conflict escalation" (oil, global) and "Oil prices dip but hold
# above $100" (oil, Middle East) were two of the top ten; a reader counts them as one story. A story of the oil sector
# that is not about the price (a Venezuelan field, a refinery) keeps the sector-and-region key.
PRICE_STORY = {"oil": r"\b(?:brent|wti|crude|oil prices?|oil futures|barrels?)\b",   # session 1443: "6 million barrels" of futures
               # session 3347 (faults file row 125): "European Gas Hits €97 ..." is a gas price story too
               "gas": r"\b(?:henry hub|ttf|jkm|gas prices?|natural gas prices?|mmbtu|gas (?:hits|touches|tops|nears|climbs|jumps|"
                      r"surges|soars|rises|falls|drops|slumps|tumbles|plunges))\b",
               "power": r"\b(?:power prices?|electricity prices?|per mwh|usd/mwh)\b"}


def price_commodity(r):
    """The commodity a price story is about ("oil", "gas", "power") from its lead title's words, "" for a story that is
    not about a price."""
    title = str((r.get("titles") or [""])[0] if isinstance(r, dict) else "").lower()
    for k, pat in PRICE_STORY.items():
        if re.search(pat, title):
            return k
    return ""


def same_topic(a, b):
    """Two clusters are one topic: one sector in one region, or a party in common and TOPIC_WORDS or more content words
    shared by their lead titles. Session 2701 (rulings item 13, the 24-hour default): the key is the sector with the
    region, so Mexico's 8,200 MW and India's coal stocks are two topics though both are "generation"; a cluster whose
    region is not given is of every region (the sector alone decides, as before). Session 1438: two price stories of one
    commodity (price_commodity) are one topic whatever their regions."""
    pa, pb = price_commodity(a), price_commodity(b)
    if pa and pa == pb:
        return True
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
            kind = "sector"   # session 1466: said so on the line
        else:
            kind = "topic"
        if len(twin["also"]) >= ALSO_MAX:
            log(f"  {what}: left for the sections below, the topic of {twin['cluster_id']} is full: "
                f"{str((r.get('titles') or [''])[0])[:80]!r} ({r['cluster_id']})")
            continue
        twin["also"].append({"cluster_id": r["cluster_id"], "title": str((r.get("titles") or [""])[0]), "sector": r.get("sector"),
                             "links": list(r.get("links") or [])[:1], "parties": r.get("parties", ""), "kind": kind})
        folded.add(r["cluster_id"])
        log(f"  {what}: folded under {twin['cluster_id']} (one topic, {r.get('sector')}): "
            f"{str((r.get('titles') or [''])[0])[:80]!r} ({r['cluster_id']})")
    out = pd.DataFrame(top, columns=list(clusters.columns) + ["also"]) if top else clusters.head(0).assign(also=None)
    return out.reset_index(drop=True), folded


# Session 2701 (rulings items 5 and 14, the 24-hour defaults): the two-minute form. The words above the fold are the
# prose before the "More" heading; the "also" lines are not counted (they are the fold, item 14), nor the source lines,
# the numbers block (its table rows and figure lines), pictures, headings, comments and the footer.
FOLD_HEADING = "## More"


def above_fold_words(md):
    """The words of prose above the fold of an issue's markdown. Session 2703 (the v2 order): the fold (FOLD_HEADING) is a
    section like any other, so its lines are skipped to the next "## " heading, as is the numbers block ("## The
    numbers"); the masthead's date line, comments, source lines (Sources:, Source:, Table `...`, Tables:), the also lines
    (item 14), table rows, pictures, headings and the footer are not counted. An issue without the fold counts to its
    footer, as before."""
    n, skip = 0, False
    for ln in md.splitlines():
        t = ln.strip()
        if t.startswith("## "):
            skip = t in (FOLD_HEADING, "## The numbers", "## The week in five numbers")   # 2704: the Roundup's block too
            continue
        if t in ("ERW", "---") or t.startswith("[How this is made.]"):   # the footer (the stamp line also begins "ERW's")
            break
        if skip:
            continue
        if (not t or t.startswith(("#", "|", "![", "<!--", "Tables: ", "Sources: ", "Source: ", "Table `")) or ALSO_RE.match(t)
                or re.match(r"^\[\d+\] ", t) or re.match(r"^\*\*\d{1,2} [A-Z][a-z]+ \d{4}\.\*\* Data through", t)):
            continue
        t = re.sub(r"^\d+\.\s+", "", t.split(" Sources: ")[0].split(" Source: ")[0])   # a list's number is not a word
        n += len(re.findall(r"[A-Za-z0-9][^\s]*", re.sub(r"\*\*|\[(\d+)\]", " ", t)))
    return n


def also_line(recs):
    """The line under an item for the stories folded under it: each its publisher's own title and its first outlet.
    Session 1466: the stories of the item's topic under ALSO_LABEL, then those folded because the sector was full under
    ALSO_SECTOR, one line."""
    def part(x):
        # session 1981 (faults file row 86): the publisher's title in the issue's money style ("USD 1.5 billion", not
        # "$1.5 Billion" beside "USD 74 billion"), its words otherwise as published
        title = money_style(nodash(x["title"]).strip())
        # session 3335 (faults file row 119): the publisher's own tail ("... Projects - Company Announcement - FT.com")
        # goes, as why_fallback takes it off: the outlet is named in the brackets after it
        outlet = outlet_name((x.get("links") or [("", "")])[0][0]).lower()
        tail = re.search(r"(?:\s+[-|]\s+[\w.&' ]{1,40}){1,2}$", title)
        if tail and (".com" in tail.group(0).lower() or "announcement" in tail.group(0).lower()
                     or (outlet and outlet in tail.group(0).lower())):
            title = title[:tail.start()].rstrip()
        return f"{title.rstrip('.')} ({link_text(x['links'])})" if x.get("links") else title
    topic = [part(x) for x in recs if x.get("kind") != "sector"]
    sector = [x for x in recs if x.get("kind") == "sector"]
    out = [f"{ALSO_LABEL} " + "; ".join(topic) + "."] if topic else []
    if sector:
        label = ALSO_SECTOR.format(sector=sector_words(sector[0].get("sector")) or "this sector")
        out.append(f"{label} " + "; ".join(part(x) for x in sector) + ".")
    return " ".join(out)


def sector_line(r, head):
    """Session 1467 (chain 150, fault 46): a by-sector or AI and power line: "- headline (sector): why [Outlet](url)", or,
    when the story has no why line that passes the check, "- headline (sector). [Outlet](url)": no colon that introduces
    nothing (the dry run of 6 November: "... plans coal use to 2038 (generation): [Utility Dive](...)")."""
    why = why_line(r["why"], head)
    link = link_text(r["links"][:1])
    lead = f"- {head} ({sector_words(r['sector'])})"
    if why:
        return f"{lead}: " + " ".join(x for x in (why, link) if x)
    return f"{lead}." + (f" {link}" if link else "")


SECTOR_WORDS = {"lng": "LNG", "ppa": "PPA"}   # session 3348 (faults file row 127): "(lng, 3 stories)", "(ppa, 4 stories)"


def sector_words(sector):
    """A sector's tag as an item line prints it: its words, an acronym in capitals."""
    s = str(sector or "")
    return SECTOR_WORDS.get(s, s.replace("_", " "))


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


def stamp_line(hours, start, now, n, folder=None):
    """The issue's first line: the window's real bounds, both ends written (session 2206; the form "for the N hours to
    <time> UTC" stays first, as tests/test_session470.py and STAMP_END read it). Session 1985 (faults file row 90): no
    "from ... from"; the start in a clause of its own; and when the issue before is more than one weekday back (no issue
    from 7 to 11 November 2026), the reader is told why the window is long: "the first issue since 6 November"."""
    since = previous_issue_day(f"{now:%Y-%m-%d}", folder)
    gap = ""
    if since is not None and len(pd.bdate_range(since + pd.Timedelta(days=1), pd.Timestamp(f"{now:%Y-%m-%d}"))) > 1:
        gap = f", the first issue since {since.day} {since:%B}"
    return (f"ERW's weekday brief of energy news for the {hours} hours to {now:%Y-%m-%d %H:%M} UTC (the window opened "
            f"{start:%Y-%m-%d %H:%M} UTC): {n:,} scored {'story' if n == 1 else 'stories'}{gap}.")   # 3333: row 114


UNSCORED_MIN = 20       # session 3333 (faults file row 114): held stories the scorer has not read, said from this many
THIN_WINDOW = 50        # and a window holding fewer stories than this, said


def held_lines(df, start, now, hours):
    """Session 3333 (faults file row 114): the window as the warehouse holds it, when a reader would misread the issue
    without it: stories held but not scored (the scorer's cap, or a run that stopped), when they are UNSCORED_MIN or more
    and a tenth of the window; and a window that holds fewer than THIN_WINDOW stories (6 to 10 November 2026 held 3 in 96
    hours, where a weekday brings several hundred). [] otherwise. Counts only; no cause is claimed."""
    try:
        when = pd.to_datetime(df["event_date"], utc=True, format="ISO8601")
        inside = df[(when >= start) & (when <= now)]
    except (KeyError, ValueError, TypeError):
        return []
    held = len(inside)
    unscored = int((inside["scored_at"] == "").sum()) if "scored_at" in inside else 0
    out = []
    if held < THIN_WINDOW:
        out.append(f"The warehouse holds {held} {'story' if held == 1 else 'stories'} of these {hours} hours, where a weekday "
                   "usually brings several hundred.")
    if unscored >= UNSCORED_MIN and unscored * 10 >= held:
        out.append(f"A further {unscored:,} stories of the window are held but not scored yet, so this issue does not rank them.")
    return (out + [""]) if out else []


def previous_issue_day(digest_date, folder=None):
    """Session 1985: the date of the newest stored issue dated before `digest_date` (docs/digest/<date>.md), or None."""
    try:
        names = sorted(f for f in os.listdir(folder or DIGEST_DIR) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", f) and f[:10] < str(digest_date))
    except OSError:
        return None
    return pd.Timestamp(names[-1][:10]) if names else None


# ---------------------------------------------------------------------------------------------------------------------
# Session 2703: the Digest in the brandbook's v2 shape (the owner's rulings of 24 October 2026, queue file 131). The
# promise: a two-minute read on what changed since the last issue, with the source trail close at hand. The order is
# fixed: the masthead; the opening number; the numbers block; what moved (two or three stories, the rest folded under
# "More", rulings items 5 and 14); the chart of the day; the fun fact; the footer.
# ---------------------------------------------------------------------------------------------------------------------
V2_TITLE = "ERW Daily Digest"
EASTERN = "America/New_York"
# the move a price must make to lead the issue (percent against the day before): a hub's day-ahead mean swings more
# from day to day than a benchmark's close; the metric that led the previous issue leads again only at twice the bar
MATERIAL_PCT = {"hub": 10.0, "fuel": 3.0}
# Session 1440 (chain 149, fault 2, and the survey of the 13 issues in runs/s1440): a move no story names needs
# UNNAMED_FACTOR times the bar to open the issue (a fuel: 4.5 percent), and an unnamed hub never opens it while a top
# story states a structural figure (14 October would have opened with SPP's day-ahead mean up 676.7 percent from a
# near-zero day; it opens with Taiwan's USD 4.4 billion for Alaska LNG instead; 21 October with 6,600 MW of reactors
# instead of WTI down 3.6 percent that no story named).
UNNAMED_FACTOR = 1.5
FUEL_PLACE = {"Henry Hub natural gas": "EIA's spot close at Henry Hub, Louisiana, the US natural gas benchmark",
              "WTI Cushing crude": "EIA's spot close of WTI at Cushing, Oklahoma, the US crude benchmark",
              "Brent crude": "EIA's spot close of Brent, the North Sea crude benchmark"}
GRID_PLACE = {"ERCOT": "Texas", "CAISO": "California", "SPP": "the central US", "MISO": "the Midwest", "NYISO": "New York",
              "ISO-NE": "New England"}
CAPACITY_SECTORS = {"generation", "storage", "interconnection", "transmission", "nuclear", "renewables", "datacenter_power",
                    "hydrogen", "lng", "ppa", "gas", "oil"}
CAPITAL_SECTORS = {"capital", "deal", "company", "policy", "grid_conditions", "power_prices"}
OPENING_RE = re.compile(r"<!-- opening: (\S*) -->")
MOVED_MAX = 3


def day_words(ts):
    """A day as the masthead writes it: "26 October 2026"."""
    t = pd.Timestamp(ts)
    return f"{t.day} {t:%B %Y}"


def cutoff_words(now):
    """The data cutoff in Eastern Time with UTC beside it: "Data through 11:45 ET, 15:45 UTC." (never "real-time")."""
    et = pd.Timestamp(now).tz_convert(EASTERN)
    return f"Data through {et:%H:%M} ET, {pd.Timestamp(now).tz_convert('UTC'):%H:%M} UTC."


def previous_opening(digest_date, folder=None):
    """The key of the opening number of the newest issue before `digest_date` (its "<!-- opening: key -->" line), or None."""
    folder = folder or DIGEST_DIR
    try:
        names = sorted(f for f in os.listdir(folder) if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", f) and f[:10] < str(digest_date))
    except OSError:
        return None
    if not names:
        return None
    with open(os.path.join(folder, names[-1]), encoding="utf-8") as f:
        m = OPENING_RE.search(f.read())
    return m.group(1) if m else None


def cand_kind(c):
    return "fuel" if c.get("key") in FUEL_PLACE else "hub"


def story_figure(r, order=("mw", "money")):
    """A structural figure a story states in its scored fields, in `order`: its MW, its sum of money; "" when it states
    none of them."""
    for what in order:
        if what == "mw":
            try:
                if r.get("mw") not in ("", None) and float(r["mw"]) > 0:
                    return f"{float(r['mw']):,.0f} MW"
            except (TypeError, ValueError):
                pass
        elif what == "money":
            raw = str(r.get("price") or "")
            price = money_style(raw)
            # session 3367 (faults file row 142): a price per share, per barrel or per unit is no structural sum ("CAD 12
            # Per Share" was a deal's value, 7 October)
            if re.search(r"\bper\b|/", raw, re.I):
                continue
            if MONEY.search(raw) and re.search(r"\d", price):
                return price
    return ""


def opening_number(cands, stories, prev_key=None):
    """The issue's opening number: one verified finding, chosen by rule, not by a person or a model.

    Among the day's moves (numbers_today's candidates: the main hubs' day-ahead means and EIA's spot closes, each against
    the value before it; held and paused prices are never candidates):
      1. a move must be defensible: at least MATERIAL_PCT in percent (10 for a hub's day-ahead mean, 3 for a benchmark
         close); the metric that opened the previous issue (prev_key) must move twice that to open again;
      2. consequence for the system or the market first: a move a story of the day names as its reason scores 2, a
         national benchmark (Henry Hub, WTI, Brent) 1 more, a single hub nothing more;
      3. novelty since the last issue second: a metric other than the previous issue's opening number first;
      4. source quality third: every candidate is a warehouse table's figure, so this ties;
      5. only then the size of the move: the largest percentage move is never the choice by default.
    Session 1440: a move no story names needs UNNAMED_FACTOR times the bar, and an unnamed single hub opens the issue
    only when no named move and no unnamed benchmark passes and no top story states a structural figure.
    When no move is defensible, the opening number is a structural figure (a MW, a sum of money) of the day's
    highest-ranked story that states one, with its outlet. Returns {kind: "mover" | "story" | None, key, ...}."""
    ok, last = [], []
    for c in cands:
        if c.get("pct") is None:
            continue
        kind = cand_kind(c)
        named = bool(c.get("reason")) or bool(c.get("named"))
        again = str(c["key"]).replace(" ", "_") == prev_key   # the opening's key is written with underscores
        # session 1440: a move no story names must be larger (UNNAMED_FACTOR), and an unnamed hub is the last resort
        bar = MATERIAL_PCT[kind] * (2 if again else 1) * (1 if named else UNNAMED_FACTOR)
        if abs(float(c["pct"])) < bar:
            continue
        consequence = (2 if named else 0) + (1 if kind == "fuel" else 0)
        entry = ((-consequence, -(0 if again else 1), -1, -abs(float(c["pct"])), c["label"]), c)
        (ok if named or kind == "fuel" else last).append(entry)
    if ok:
        ok.sort(key=lambda x: x[0])
        c = ok[0][1]
        return {"kind": "mover", "key": str(c["key"]).replace(" ", "_"), "cand": c}
    if last:
        last.sort(key=lambda x: x[0])
    for rank, r in enumerate(stories, 1):
        fig = story_figure(r)
        if fig:
            # session 1974 (faults file row 79): the unnamed hub's move the rule passed over is kept, so the opening says
            # what the rule did instead of "No price moved enough to lead" beside a 39.1% move in the numbers below
            return {"kind": "story", "key": f"story:{r['cluster_id']}", "rec": r, "figure": fig, "rank": rank,
                    "passed": last[0][1] if last else None}
    if last:
        c = last[0][1]
        return {"kind": "mover", "key": str(c["key"]).replace(" ", "_"), "cand": c}
    return {"kind": None, "key": ""}


def mover_text(c, ref):
    """A move in the form the site's parser and scripts/check_digest.py key (lib/digest.ts, the mover line)."""
    return (f"{c['label']}: {c['v']:.2f} {c['unit']} on {c['d']:%Y-%m-%d}, {'up' if c['ch'] >= 0 else 'down'} "
            f"{abs(c['ch']):.2f} {c['unit']} ({abs(c['pct']):.1f}%) from {c['pv']:.2f} {c['unit']} on {c['pd']:%Y-%m-%d} {ref}")


def place_words(c):
    """The geography and the comparison basis of a move, in words."""
    if cand_kind(c) == "fuel":
        return f"{FUEL_PLACE[c['key']]}, against the close before it."
    grid = str(c["key"])
    return (f"The mean of the 24 hourly day-ahead prices at {grid}'s {c.get('node', '')} ({GRID_PLACE.get(grid, 'the US')}) for "
            "the operating day, against the day before.")


def outlet_of(r):
    """The outlet of a story's first link, named (no address: the story's link is in its item)."""
    links = list(r.get("links") or [])
    return outlet_name(links[0][0]) if links else "its outlet"   # session 1978 (row 83): "JPT", not "JPT Homepage"


def passed_words(c):
    """Session 1974 (faults file row 79): the sentence after a story's figure in the opening. With no move past its bar,
    "No price moved enough to lead"; with a single hub's move that no story names (session 1440's last resort), that
    move is named, so the opening does not deny a move the numbers below print."""
    if not c:
        return "No price moved enough to lead; this is a reported figure, not a warehouse table's."
    # session 3375 (faults file row 144): the move is named, its figure left to the numbers below, where it is keyed; the
    # "down 39.1%" this sentence printed had no key a tracer could follow
    word = "rise" if float(c.get("ch", c["pct"])) >= 0 else "fall"
    return (f"The day's largest move, {c['label']}'s {word} (in the numbers below), is one hub's and no story names it, so a "
            "reported figure leads; it is the outlet's, not a warehouse table's.")


def opening_lines(op, heads):
    """The opening number's section: one sentence with metric, value, unit, geography, period and comparison basis."""
    L = ["## The opening number", ""]
    if op["kind"] == "mover":
        c, notes = op["cand"], Notes()
        L.append(f"**{mover_text(c, notes.ref(c['table']))}.** {place_words(c)}" + (c.get("reason") or ""))
        return L + notes.lines() + [""]
    if op["kind"] == "story":
        r = op["rec"]
        L.append(f"**{op['figure']}**: {heads.get(r['cluster_id'], str((r.get('titles') or [''])[0])).rstrip('.')}, as "
                 f"{outlet_of(r)} reported on {pd.Timestamp(r['first']):%Y-%m-%d} (ranked {op['rank']} of the day's top ten). "
                 + passed_words(op.get("passed")))
        return L + [""]
    return L + ["No price moved enough to lead, and no story of the day states a figure.", ""]


def subject_line(op, digest_date):
    """ERW Daily | <metric or market>: <value and unit>, <comparison period>: a figure only when it is a warehouse table's."""
    if op["kind"] == "mover":
        c = op["cand"]
        return (f"ERW Daily | {c['label']}: {c['v']:.2f} {c['unit']}, {'up' if c['ch'] >= 0 else 'down'} "
                f"{abs(c['pct']):.1f}% on {'the close before' if cand_kind(c) == 'fuel' else 'the day before'}")
    if op.get("kind") == "story" and op.get("rec"):
        clause = subject_clause(op["rec"].get("head") or str((op["rec"].get("titles") or [""])[0]))
        if clause:
            return f"ERW Daily | {clause}"
    return f"ERW Daily | {day_words(digest_date)}"


SUBJECT_CLAUSE_MAX = 70
# a verb that takes no "in" before its object: a figure taken out of "plans USD 74 billion in data center projects" leaves
# "plans in data center projects", read as "plans data center projects"; "invests in" keeps its "in"
NO_IN_VERB = re.compile(r"\b(plans|unveils|announces|signs|secures|raises|targets|commits|approves|files|proposes|wins|closes|"
                        r"seals|pledges|outlines|books|lands) in (?=[a-z])")


def subject_clause(head):
    """Session 1984 (faults file row 89): the subject when the opening is a story's figure: the top story's headline as the
    issue printed it, its figures taken out (chain 131: a figure in the subject only when it is a warehouse table's; the
    Roundup's row 62 form, roundup.head_clause), cut at a word to SUBJECT_CLAUSE_MAX with no "...". "" when nothing
    readable is left."""
    import roundup   # noqa: E402  (roundup imports this module: read here, not at the top)
    # session 3352 (faults file row 131): the voice's adjectives go from the subject ("Google enters massive ... deal")
    t = roundup.head_clause(money_style(plain(nodash(str(head or "")))).rstrip("."), SUBJECT_CLAUSE_MAX + 20)
    t = NO_IN_VERB.sub(lambda m: m.group(1) + " ", t)
    if len(t) > SUBJECT_CLAUSE_MAX:
        full = t
        t = roundup.head_clause(t, SUBJECT_CLAUSE_MAX)
        # a cut inside a name ("... battery in Western" of "Western Australia") goes back to before the name
        rest = full[len(t):].split()
        while t and rest and re.match(r"[A-Z]", rest[0]) and re.search(r"\b[A-Z][\w'.-]*$", t):
            t = re.sub(r"\s*\b[A-Z][\w'.-]*$", "", t)
            rest = ["X"]   # one name is taken back, then the tail is tidied
        t = roundup.CLAUSE_TAIL.sub("", t).strip(" ,;:")
    return t


STORIES_SHORT_HOURS = 2   # session 1444 (fault 21): the newest story more than this before the cutoff is said


def masthead_lines(digest_date, now, op, newest=None):
    """The masthead: the title with the issue's date (as the email and the archive read it), the date in words and the
    cutoff, and two comments: the subject line and the opening number's key (the next issue's novelty). Session 1444
    (fault 21): when the newest story held (`newest`) is more than STORIES_SHORT_HOURS before the cutoff, the line says
    so ("Stories through 03:55 ET, 07:55 UTC; prices through 11:45 ET, 15:45 UTC."), since the scorer or the ingest
    stopped short of the cutoff and the stories do not cover the hours the cutoff claims."""
    cut = cutoff_words(now)
    if newest is not None:
        newest = pd.Timestamp(newest)
        if newest.tzinfo is None:
            newest = newest.tz_localize("UTC")
        if pd.Timestamp(now) - newest > pd.Timedelta(hours=STORIES_SHORT_HOURS):
            et = newest.tz_convert(EASTERN)
            cut = (f"Stories through {et:%H:%M} ET, {newest.tz_convert('UTC'):%H:%M} UTC; prices through "
                   f"{pd.Timestamp(now).tz_convert(EASTERN):%H:%M} ET, {pd.Timestamp(now).tz_convert('UTC'):%H:%M} UTC.")
    return [f"# {V2_TITLE}, {digest_date}", "", f"**{day_words(digest_date)}.** {cut}", "",
            f"<!-- subject: {subject_line(op, digest_date)} -->", "", f"<!-- opening: {op['key']} -->", ""]


def best_price(cands, skip_key):
    """The market price of the numbers block: the candidates in opening_number's order of consequence, the opening's own
    metric left out; a candidate with a percent first."""
    pool = [c for c in cands if str(c["key"]).replace(" ", "_") != skip_key and c.get("pct") is not None]
    # session 1975 (faults file row 80): a price that did not move ("up 0.00 USD/MMBtu (0.0%)") comes after every move
    pool.sort(key=lambda c: (abs(float(c["pct"])) < 0.05, -((2 if c.get("reason") or c.get("named") else 0) + (1 if cand_kind(c) == "fuel" else 0)), -abs(float(c["pct"])), c["label"]))
    return pool[0] if pool else None


# Session 1439 (chain 149, faults 4 to 6): a story row names its measure by the story's sector, its place by the scorer's
# region, its figure once, and who (the parties, else the outlet); the headline is the item's, not the row's. The row's
# key is the story's row of news_stories (its cluster id and the field read), so scripts/check_digest.py can trace it.
SECTOR_NOUN = {"datacenter_power": "Datacenter load", "generation": "Generation capacity", "storage": "Storage capacity",
               "nuclear": "Nuclear capacity", "renewables": "Renewable capacity", "transmission": "Transmission",
               "interconnection": "Interconnection queue", "lng": "LNG capacity", "gas": "Gas supply", "hydrogen": "Hydrogen capacity",
               "capital": "Capital raised", "deal": "Deal value", "policy": "Policy sum", "company": "Company spending",
               "ppa": "Power contracted",   # session 3364 (faults file row 138): "Ppa, Wyoming: 702 MW"
               "grid_conditions": "Reliability", "geopolitics": "Supply at risk", "oil": "Oil supply"}


RAISED = re.compile(r"\b(?:rais(?:e|es|ed|ing)|funding|round|ipo|loan|bonds?|debt|financing|secures?)\b", re.I)   # row 137
TOTAL_OF_DEALS = re.compile(r"\btotal(?:s|ed|ing)?\b|\bin [\w-]+(?: [\w-]+)? deals\b", re.I)   # session 3332, row 112
# row 123, narrowed by row 124 (session 3347): the headline's sum stands right before the company it describes ("To Form $50B
# Gas Giant", "Will Create $50 Billion Gas 'Champion'"); "Creating Largest US Gas Producer" with no sum keeps "Deal value"
COMBINED = re.compile(r"(?:\$|USD ?)[\d.,]+\s?(?:B|bn|billion|trillion)?\b[^,.;]{0,24}?\b(?:giant|company|producer|group|firm|"
                      r"champion|powerhouse)\b", re.I)
DISPATCHED = re.compile(r"\b(?:dispatch(?:ed|es|ing)?|discharg(?:e|ed|es|ing)|delivered)\b", re.I)   # session 1977, row 82


def story_who(r):
    """The parties of a story (the first two), else its outlet."""
    parties = [p.strip() for p in str(r.get("parties") or "").split(";") if p.strip()]
    return ", ".join(parties[:2]) if parties else outlet_of(r)


def story_row(label, recs, sectors, heads, skip_id, what, order, notes=None):
    """A block row from the day's top stories: the highest-ranked in `sectors` stating a figure of `order` (story_figure),
    in the block's form (measure, place: figure (who; outlet, date) [n]. Change. Status.). A price story (price_commodity)
    is never a row: its figure is a price, which the market row holds. Returns (line, key detail or "")."""
    for r in recs:
        if r["cluster_id"] == skip_id or str(r.get("sector")) not in sectors or price_commodity(r):
            continue
        fig = story_figure(r, order)
        if not fig:
            continue
        field = "mw" if fig.endswith(" MW") else "price"
        noun = SECTOR_NOUN.get(str(r.get("sector")), str(r.get("sector")).replace("_", " ").capitalize())
        if field == "mw" and DISPATCHED.search(f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}"):
            # session 1977 (faults file row 82): "Sunrun and Tesla dispatched more than 580 MW from 140,000 home batteries"
            # is power dispatched, not storage capacity built
            noun = "Storage dispatched" if str(r.get("sector")) == "storage" else "Power dispatched"
        if field != "mw" and TOTAL_OF_DEALS.search(f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}"):
            # session 3332 (faults file row 112): "US Oil and Gas M&A Activity Accelerates With $12.6 Billion in Third-Quarter
            # Deals" is a quarter's total, not one deal's value
            noun = "Deals in total"
        elif field != "mw" and COMBINED.search(f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}"):
            # session 3337 (faults file row 123): "EQT, Range Resources To Combine To Form $50B Gas Giant" states the
            # combined company's size, not the deal's (USD 13 billion in energy_deals)
            noun = "Combined company value"
        elif field != "mw" and re.search(r"\bbacklogs?\b", f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}", re.I):
            # session 3354 (faults file row 136): "Kinder Morgan Backlog Surges ..." states a company's backlog, not a deal
            noun = "Project backlog"
        elif (field != "mw" and str(r.get("sector")) in ("deal", "capital", "company")
              and re.search(r"\bplans?\b|\bplanned\b", f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}", re.I)
              and not re.search(r"\b(?:buy|buys|acquir\w*|merg\w*|sells?|sale|stake|takeover|deal)\b",
                                f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}", re.I)
              and not RAISED.search(f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}")):
            # session 3365 (faults file row 141): "EQT's Zelestra unveils a USD 12 billion plan to meet US AI demand" is a plan
            # to invest, not a deal's value
            noun = "Investment planned"
        elif field != "mw" and str(r.get("sector")) == "capital":
            # session 3355 (faults file row 137): "Meta Reports $825 Billion in Future Spending Commitments" was "Capital
            # raised"; the measure follows the headline: money raised, money to be spent, else capital
            text = f"{(r.get('titles') or [''])[0]} {(heads or {}).get(r['cluster_id'], '')}"
            if re.search(r"\b(?:spend(?:s|ing)?|capex|commitments?|invest(?:s|ing|ment)?)\b", text, re.I) and not RAISED.search(text):
                noun = "Spending committed"
            elif not RAISED.search(text):
                noun = "Capital"
        region = str(r.get("region") or "").strip()
        place = f", {region}" if region and region.lower() != "global" else ""
        ref = f" {notes.ref('news_stories')}" if notes is not None else ""
        who, outlet = story_who(r), outlet_of(r)
        # session 3332 (faults file row 111): with no party, story_who is the outlet: "(Rigzone; Rigzone, ...)" said it twice
        by = outlet if who == outlet else f"{who}; {outlet}"
        line = (f"- **{label}.** {noun}{place}: {fig} ({by}, {pd.Timestamp(r['first']):%Y-%m-%d}){ref}. "
                "Change: first report, no earlier figure held. Status: the outlet's figure, not a table's.")
        return line, f"story {r.get(field + '_id') or r['cluster_id']} ({field})"   # row 107: the story the figure came from
    return f"- **{label}.** No story of the day states {what}.", ""


def numbers_block(facts, op, recs, heads):
    """The numbers block: four rows by the default mix (a market price; a physical measure; a project, queue or capacity
    figure; a policy, capital or reliability figure), each with its metric and geography, value and unit, change against
    a stated reference, period, status and source. A held value is never a row (the candidates hold none); a slot with
    no figure says so. The price and demand rows keep the forms the site's parser and check_digest key."""
    notes = Notes()
    L = ["## The numbers", ""]
    c = best_price(facts.get("cands", []), op.get("key"))
    if c:
        status = ("the mean of the operating day's 24 hourly day-ahead prices" if cand_kind(c) == "hub"
                  # session 1976 (faults file row 81): the close's own day, not "about a week after" beside a close one day old
                  else f"EIA's spot close of the trading day {c['d']:%Y-%m-%d}, the newest EIA had published")
        L.append(f"- **Market price.** {mover_text(c, notes.ref(c['table']))}. Status: observed, {status}.")
    else:
        L.append("- **Market price.** No price with a value before it is held today, so no move is shown.")
    d = facts.get("demand") or {}
    if d.get("top") is not None:
        top = d["top"]
        ref = notes.ref("eia930_all_demand", "balancing authority us48")
        line = f"- **Physical.** US48 demand peaked at {top['value']:,.0f} MW in the hour starting {top['ts_utc']:%Y-%m-%d %H:%M} UTC {ref}; "
        old = d.get("old")
        span = d.get("span", "year")
        if old is not None and float(old["value"]) > 0:
            pct = 100 * (float(top["value"]) / float(old["value"]) - 1)
            line += (f"the same weekday a {span} before ({d['before']:%Y-%m-%d}) peaked at {old['value']:,.0f} MW in the hour "
                     f"starting {old['ts_utc']:%Y-%m-%d %H:%M} UTC {ref}, so {pct:+.1f}% on the {span}.")
            if span == "week":   # session 1439 (fault 3): the year before is the data machine's (item 18)
                line += " The same weekday a year before is not held."
        else:
            # session 3364 (faults file row 139): neither the year before nor the week before is held, as the numbers in full
            # say it ("... and a week before (2026-10-05) are not held"), where this row named the year only
            wk = d["day"] - pd.Timedelta(days=7) if d.get("day") is not None else None
            line += (f"the same weekday a year before ({d['before']:%Y-%m-%d})"
                     + (f" and a week before ({wk:%Y-%m-%d})" if wk is not None else "") + " are not held, so no change is shown."
                     if wk is not None else f"the same weekday a year before ({d['before']:%Y-%m-%d}) is not held, so no change is shown.")
        L.append(line + " Status: observed, EIA-930 hourly demand.")
    else:
        L.append("- **Physical.** US48 demand for yesterday is not in the warehouse.")
    skip = op["rec"]["cluster_id"] if op.get("kind") == "story" else None
    details = []
    for label, sectors, what, order in (("Project or capacity", CAPACITY_SECTORS, "a capacity figure in MW", ("mw",)),
                                        ("Policy, capital or reliability", CAPITAL_SECTORS, "a policy or capital figure", ("money",))):
        line, detail = story_row(label, recs, sectors, heads, skip, what, order, notes)
        L.append(line)
        if detail:
            details.append(detail)
    if details:
        notes.extra["news_stories"] = "; ".join(details)
    return L + notes.lines() + [""]


def limitation(r):
    """One limitation of a story, when material: an analysis rather than a report, or one outlet so far."""
    if r.get("kind") == "commentary":
        return "An analysis piece, not a reported event."
    try:
        if int(r.get("outlets") or 0) == 1:
            return "One outlet has reported it so far."
    except (TypeError, ValueError):
        pass
    return ""


def moved_count(recs):
    """Two or three stories under What moved: three, unless fewer are held or the third is commentary."""
    if len(recs) >= MOVED_MAX and recs[MOVED_MAX - 1].get("kind") != "commentary":
        return MOVED_MAX
    return min(2, len(recs))


# Session 1444 (chain 149, fault 22; the brandbook: 350 to 450 words of prose above the fold). The dry run of 26 October
# stood at 295 words with three stories: a fourth is lifted from the rest while the count is under FOLD_MIN, up to
# MOVED_LIFT_MAX stories; a count past FOLD_MAX with three drops to two. The also lines, the source lines and the block
# are not counted (above_fold_words).
FOLD_MIN, FOLD_MAX, MOVED_LIFT_MAX = 350, 450, 5


def lift_count(words, n0, n_recs):
    """The number of stories above the fold: from n0 (moved_count), up while words(n) is under FOLD_MIN and a story is
    left (to MOVED_LIFT_MAX), down to two while words(n) is past FOLD_MAX. words(n) gives the prose count with n."""
    n = n0
    w = words(n)
    while w < FOLD_MIN and n < min(MOVED_LIFT_MAX, n_recs):
        n += 1
        w = words(n)
    while w > FOLD_MAX and n > 2:
        n -= 1
        w = words(n)
    return n


def no_chart_lines(facts, n=3):
    """When no valid chart can be built: the issue says no chart is shown, and a small table of the day's largest moves
    (numbers_today's candidates, at most n) stands in its place."""
    L = ["", "## ERW's Chart of the Day", "", "No chart is shown today: no candidate passed the chart's rules (the run log says why)."]
    cands = [c for c in facts.get("cands", []) if c.get("pct") is not None][:n]
    if cands:
        L += ["", "| Measure | Value | Change | Period | Table |", "|---|---|---|---|---|"]
        for c in cands:
            L.append(f"| {c['label']} | {c['v']:.2f} {c['unit']} | {'up' if c['ch'] >= 0 else 'down'} {abs(c['pct']):.1f}% | "
                     f"{c['d']:%Y-%m-%d} against {c['pd']:%Y-%m-%d} | `{c['table']}` |")
    return L


def footer_lines(now, run_id, model):
    """The footer: methods, corrections, preferences and unsubscribe, signed ERW."""
    return ["", "ERW", "", "---", "", "[How this is made.](/about#digest)", "",
            "Corrections: [open an issue](https://github.com/SamuelEnrique/erw/issues). Preferences and topics: [subscribe](/subscribe). "
            "Every email carries its own unsubscribe link.", "",
            f"<!-- Generated by warehouse/news/brief.py at {now:%Y-%m-%d %H:%M} UTC; run log "
            f"warehouse/output/logs/news_brief_{run_id}.log; model {model}; story data "
            "warehouse/output/news_stories.csv. -->"]


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
        # session 2703 (the owner's rulings of 24 October 2026): the brandbook's v2 order. The numbers come first, so the
        # opening number and the block can be chosen from them
        facts = {}
        nums = numbers_today(digest_date, log, clusters, facts, now=now)   # session 804: the day's clusters, for the reasons beside the movers
        summary, su = (None, []) if args.no_model else numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        recs = top10.to_dict("records")
        for r in recs:   # session 1983 (faults file row 88): the headline as the issue prints it, which the chart's line quotes
            r["head"] = heads.get(r["cluster_id"], "")
        op = opening_number(facts.get("cands", []), recs, previous_opening(digest_date))
        log(f"  opening number: {op['kind'] or 'none'} {op['key']}")
        newest = pd.to_datetime(s["event_date"], utc=True, format="ISO8601").max() if len(s) else None
        L = masthead_lines(digest_date, now, op, newest) + [
             # session 21: one sentence (what, the period, the story count); the method is on /about#digest
             stamp_line(hours, start, now, len(s)), "",
             *held_lines(df, start, now, hours),   # session 3333 (faults file row 114): a thin or unscored window, said
             *([NO_MODEL_LINE, ""] if args.no_model else [])]
        L += opening_lines(op, heads)
        # session 1439 (fault 5): the story rows read the whole issue's items in rank (the top ten, then the sections,
        # then AI and power), since the day's policy or capital figure is often in a section bullet
        pool, seen = [], set()
        for frame in [top10, *by_group.values(), ai]:
            for r in (frame.to_dict("records") if frame is not None and len(frame) else []):
                if r["cluster_id"] not in seen:
                    seen.add(r["cluster_id"])
                    pool.append(r)
        L += numbers_block(facts, op, pool, heads)
        policy_lines = policy_actions_lines(start, now, log)

        def middle(n_moved):
            """What moved with n_moved stories, then the fold: the rest of the top ten, the sectors, AI and power, the
            numbers in full (session 1444: built again when the fold's count asks for another story)."""
            M = ["## What moved", ""]
            for i, r in enumerate(recs[:n_moved], 1):
                M += item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({sector_words(r['sector'])})  ",
                                " ".join(x for x in (why_line(r['why'], heads[r['cluster_id']]), limitation(r)) if x),
                                f"Sources: {link_text(r['links'])}")
            # rulings items 5 and 14: the rest folds under "More", not cut
            M += ["", FOLD_HEADING, "", "### The rest of the top ten", ""]
            if len(recs) <= n_moved:
                M.append("- no further story in the top ten today")
            for i, r in enumerate(recs[n_moved:], n_moved + 1):
                M += item_lines(r, f"{i}. **{heads[r['cluster_id']]}** ({sector_words(r['sector'])})  ",
                                (why_line(r['why'], heads[r['cluster_id']]) + " " + detail(r, heads[r['cluster_id']])).strip(),
                                f"Sources: {link_text(r['links'])}")
            M += ["", "### By sector", ""]
            for g, c in by_group.items():
                M.append(f"**{g}**")
                M.append("")
                if c.empty:
                    M.append("- no scored story in this group today")
                for r in c.to_dict("records"):
                    M.append(sector_line(r, heads[r['cluster_id']]))   # session 1467 (fault 46)
                if g == "Policy":
                    M += without_repeats(policy_lines, L + M, log)
                M.append("")
            M += ["### AI and power", ""]
            if ai.empty:
                M.append("- no further story on AI and power today (any such story is listed above)")
            for r in ai.to_dict("records"):
                M.append(sector_line(r, heads[r['cluster_id']]))   # session 1467 (fault 46)
            M += ["", "### ERW's Numbers Today", ""] + ([summary, ""] if summary else []) + nums
            return M

        # session 232: the chart of the day, chosen and drawn by code; omitted, with the reason logged, when there is none
        tail = daily_chart_section(digest_date, log, args.out, stories=recs) or no_chart_lines(facts)   # 805; 2703: the stand-in
        # session 23: the Fun fact, last; re-verified from its stored sources, omitted if it fails
        tail += fun_fact_section(digest_date, log)
        # session 21: the method is on /about#digest; the generation record stays in the file, not on the page
        tail += footer_lines(now, run_id, model)   # session 25: signed ERW; session 2703: corrections, preferences, unsubscribe
        # session 1444 (fault 22): the stories above the fold are as many as bring the prose to 350 words, at most five
        n_moved = lift_count(lambda n: above_fold_words(chr(10).join(L + middle(n) + tail)), moved_count(recs), len(recs))
        L += middle(n_moved) + tail
        log(f"  words of prose above the fold: {above_fold_words(chr(10).join(L))} with {n_moved} stories under What moved")
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
