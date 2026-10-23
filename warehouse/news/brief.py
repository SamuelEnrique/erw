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
            # session 470: one link an address (two stories of a cluster at one address printed it twice)
            "links": list({r.source_url: (r.source, r.source_url) for r in g.itertuples()}.values())[:3],
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
        elif ln.startswith("   ") and "Sources:" in ln:
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
        if m and m.group(1) and i + 1 < len(lines) and lines[i + 1].startswith("   ") and "Sources:" in lines[i + 1]:
            block.append(lines[i + 1])
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
    for ln in out:  # the top items numbered again, 1 to n
        m = re.match(r"^(\d+)\. (\*\*.*)$", ln)
        if m:
            n += 1
            ln = f"{n}. {m.group(2)}"
        fixed.append(ln)
    return fixed


def link_text(links):
    # session 470 (digest audit fix 7, roundup audit fix 4): a Google News address does not reach the outlet (the ingest
    # records it in url_resolved), and the reader is told where the link goes
    return ", ".join(f"[{src}]({url})" + (" (via Google News)" if "news.google.com" in str(url) else "")
                     for src, url in links)


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
# Session 2206: unprecedented, critical and key join the list. "key" and "critical" are also plain words of the trade
# ("the key to", "critical minerals"): TERM says where they stand, and plain() leaves those.
HYPE = r"(?:major|massive|significant|significantly|huge|unprecedented|critical|key)"
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


def why_line(text):
    """Session 577 (digest audit fixes 8 and 9, as session 470 left them): the scorer's reason as an issue prints it: the
    adjectives docs/voice.md cuts taken out (plain), each sum of money in the one style (money_style: the "$3.2bn" and
    "$45 Billion" of the why lines, not only the price field), and a stop at its end, so the figures or the links that
    follow do not run on from it ("affecting global oil markets and prices parties: Iran.", 20 October, top 8)."""
    t = money_style(plain(text)).strip()
    # "an $800MM loan" was right as written; as "USD 800 million" the article follows the code as it is said
    t = re.sub(r"\b([Aa])n? (USD|CAD|EUR|GBP|AUD)\b",
               lambda m: m.group(1) + ("n " if m.group(2) == "AUD" else " ") + m.group(2), t)
    if t and not re.search(r"[.!?][\"'”)\]]*$", t):
        t += "."
    return t


def detail(r):
    bits = []
    if r["mw"]:
        bits.append(f"{float(r['mw']):,.0f} MW")
    if r["price"]:
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
        pause = paused_row(label)
        if len(df) == n_expected:
            lines.append(f"| {label} | {node} | {day.date()} | {mean2(df['value'])} | {notes.ref(table)} |")
        elif pause:  # session 470 (digest audit fix 12): why the grid is absent, not "not in the warehouse"
            lines.append(f"| {label} | {node} | {day.date()} | not requested: paused by the ERW since {pause['paused_on']} "
                         f"({pause['reason']}) | {notes.ref(table)} |")
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
                      f"({top['ts_utc']:%Y-%m-%d %H:%M} UTC), {top['freq']} `{top['variable']}`, {rt_label(iso, top['variable'])}"
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
    return [f"- {r['title']} ({r['agency']} {kinds.get(r['action_type'], r['action_type'])}, policy action): {why_line(r['why'])} "
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


def daily_chart_section(digest_date, log, out=None):
    """Session 232 (Samuel's ruling of 12 October 2026: the daily chart is fully automatic, a fact and its chart, no
    approval): the day's chart, chosen and drawn by code (warehouse/analysis/findings/daily_chart.py: the day's
    strongest scanner flag no Digest has shown, else the watch list's largest change of the latest period). No model
    is called and none of its words are a model's. Nothing to show, or any failure, gives no section and the reason
    in the log: a digest without a chart ships. out: a check run's path (--out); its picture and record are then
    written beside that file, the wait for the day's scan is skipped, and docs/digest/charts/ is not touched."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import daily_chart
        if out:
            return daily_chart.section(digest_date, log, chart_dir=os.path.join(os.path.dirname(os.path.abspath(out)), "charts"), wait=0,
                                       used=daily_chart.used_keys(but=digest_date),
                                       waited=daily_chart.held_before(digest_date))   # session 267: the guard's memory is the real one
        wait = os.environ.get("DAILY_CHART_WAIT", "")
        return daily_chart.section(digest_date, log, wait=int(wait) if wait.isdigit() else None)
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
            block = ln + (" " + lines[i + 1] if m.group(1) and i + 1 < len(lines) and lines[i + 1].startswith("   ") else "")
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


def select(clusters, digest_date, log, folder=None):
    """The issue's sections: (top 10, {group: clusters}, AI and power). Session 21, ruling 5: each cluster appears once;
    a section takes only clusters not shown above it. Session 470: a story an issue of the last seven days printed is
    left out first (not_shown_before), and the AI section takes significance 5 or more."""
    clusters = one_per_event(not_shown_before(clusters, earlier_issues(digest_date, folder=folder), log), log)
    top10 = clusters.head(10)
    used = set(top10["cluster_id"])
    by_group = {}
    for g, secs in GROUPS.items():
        by_group[g] = clusters[clusters["sector"].isin(secs) & ~clusters["cluster_id"].isin(used)].head(3)
        used |= set(by_group[g]["cluster_id"])
    ai = clusters[(clusters["ai"] >= 7) & (clusters["sig"] >= AI_MIN_SIG) & ~clusters["cluster_id"].isin(used)].head(5)
    return top10, by_group, ai


def window_rows(df, now, hours):
    """Session 2206 (digest audit, the window): the scored energy stories of the window, (rows, start, bounds). The window
    is the `hours` before `now` and ends at `now`: a story dated after the run (a feed's clock ahead, an item dated for
    its print edition) is left for the next issue, where until now it was taken and the stamp "the 24 hours to <the
    run>" was false. bounds is the earliest and the latest publish time among the rows, or None when there are none."""
    when = pd.to_datetime(df["event_date"], utc=True, format="ISO8601")
    start = now - pd.Timedelta(hours=hours)
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
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: today, UTC)")
    ap.add_argument("--out", help="write the digest to this path only (not docs/digest/<date>.md, not latest.md)")
    ap.add_argument("--weekend", action="store_true", help="write a digest for a Saturday or Sunday date anyway")
    ap.add_argument("--stories", help="read the scored stories from this file instead of news_stories (session 30: the "
                    "shadow scorer's view, warehouse/news/shadow.py)")
    ap.add_argument("--no-model", action="store_true", help="session 176: no model call (the daily model cap is reached, "
                    "warehouse/health.py budget): each headline is the lead story's own title as its publisher wrote it, "
                    "and the model-written summary of the numbers is left out; the digest still publishes")
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
        s, start, bounds = window_rows(df, now, args.hours)   # session 2206: the window ends at the run, and is said so
        log(f"digest {digest_date}: {len(s)} scored energy stories in the {args.hours} hours from {start:%Y-%m-%d %H:%M} to "
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
             stamp_line(args.hours, start, now, len(s)), "",
             *([NO_MODEL_LINE, ""] if args.no_model else []),
             "## Top of the industry", ""]
        for i, r in enumerate(top10.to_dict("records"), 1):
            L.append(f"{i}. **{heads[r['cluster_id']]}** ({r['sector'].replace('_', ' ')})  ")
            L.append(f"   {why_line(r['why'])} {detail(r)}Sources: {link_text(r['links'])}")
        L += ["", "## By sector", ""]
        for g, c in by_group.items():
            L.append(f"**{g}**")
            L.append("")
            if c.empty:
                L.append("- no scored story in this group today")
            for r in c.to_dict("records"):
                L.append(f"- {heads[r['cluster_id']]} ({r['sector'].replace('_', ' ')}): {why_line(r['why'])} {link_text(r['links'][:1])}")
            if g == "Policy":
                L += without_repeats(policy_actions_lines(now - pd.Timedelta(hours=args.hours), now, log), L, log)
            L.append("")
        L += ["## AI and power", ""]
        if ai.empty:
            L.append("- no further story on AI and power today (any such story is listed above)")
        for r in ai.to_dict("records"):
            L.append(f"- {heads[r['cluster_id']]} ({r['sector'].replace('_', ' ')}): {why_line(r['why'])} "
                     f"{link_text(r['links'][:1])}")
        nums = numbers_today(digest_date, log)
        summary, su = (None, []) if args.no_model else numbers_summary(client, model, nums, log)
        if model in PRICES:
            scost = sum(x.input_tokens * PRICES[model][0] + x.output_tokens * PRICES[model][1] for x in su) / 1e6
            log(f"  numbers summary: {len(su)} call(s), cost USD {scost:.4f}")
            cost = f"{cost} + summary USD {scost:.4f}"
        L += ["", "## ERW's Numbers Today", ""] + ([summary, ""] if summary else []) + nums
        # session 232: the chart of the day, chosen and drawn by code; omitted, with the reason logged, when there is none
        L += daily_chart_section(digest_date, log, args.out)
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
