#!/usr/bin/env python3
"""The fun fact engine: a bank of verified energy facts, and one item for each weekday digest.

Energy Research Warehouse (ERW), session 23. Files (all in git, so the daily run on GitHub can
re-verify an item before the digest prints it):

  warehouse/news/facts/bank.csv          one row per fact, verified when it was added
  warehouse/news/facts/raw/              the stored sources: Wikipedia extracts and EIA history pages (each
                                         saved as fetched, with its retrieval time),
                                         and, for a warehouse fact, the table rows it was computed from
  warehouse/news/facts/items/DATE.json   the item written for one digest date

    python warehouse/news/funfact.py --seed 20           # add 20 verified facts to the bank
    python warehouse/news/funfact.py                     # the daily run: add one fact, write today's item
    python warehouse/news/funfact.py --date 2026-09-29   # write the item for that date
    python warehouse/news/funfact.py --verify            # re-verify every fact in the bank

The rules (session 23 prompt):
  - The fact is always an energy fact first: a number or statistic from the warehouse, a piece of
    energy history, or a quirk of how the energy system works.
  - The second half is optional and rotates among structures by weekday: Monday none; Tuesday a
    comparison of scale; Wednesday an on-this-day history line; Thursday an etymology, or a
    cross-field connection on odd ISO weeks (so a cross-field angle is used some days and never by
    default); Friday a light pun. When no verified second half of the day's structure exists, the
    fact runs alone.
  - Every warehouse number passes the literal-number check (warehouse/chat/ask.py, as in the
    digest): each number in the text must appear in the stored rows the fact was computed from.
  - Every history or etymology claim is fetched from a stored source (Wikipedia or EIA's history
    pages, saved raw; the dictionary API the prompt allows, dictionaryapi.dev, answered HTTP 522 (a Cloudflare timeout) from
    this machine on 2026-09-28, so it is not used) and must quote it: the fact's supporting span must appear word
    for word in the stored text, and every number in the claim must appear in that span. A fact
    that fails either check is dropped (kept in the bank with status dropped and the reason).
  - Session 23, after the first seed: the span check alone passed drafts that added claims around a true
    quote, so a sourced fact must also be written in its spans' words (85% of the fact's content words,
    70% of a sourced second half's, found in the spans or the source's title), and at creation an
    independent model call must find every claim in the spans (a misreading of a quote passes the word
    checks). The word and number checks are rerun on the day's item before it is printed.
  - A conjecture is allowed only when phrased as one ("perhaps", "might", "may have", ...).
  - A pun makes no claim: it may hold no number.
  - A digest without a fun fact ships rather than one with an unverified fact: brief.py re-verifies
    the day's item against the stored files and leaves the section out on any failure.

Who writes what: warehouse facts are written by this script from computed values (no model).
History facts are drafted by the model (score.py's pick_model) from one stored source page, as JSON
with the exact spans; the checks above decide what is kept. On-this-day lines are taken verbatim
from the Wikipedia page for the date (its Events list), filtered by energy words.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import random
import re
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "package", "src"))
sys.path.insert(0, os.path.join(HERE, "..", "chat"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

FACTS = os.path.join(HERE, "facts")
BANK = os.path.join(FACTS, "bank.csv")
RAW = os.path.join(FACTS, "raw")
ITEMS = os.path.join(FACTS, "items")
UA = {"User-Agent": "ERW-energy-research-warehouse/1.0 (https://github.com/SamuelEnrique/erw; research)"}
COLS = ["fact_id", "created_at", "kind", "fact", "second", "structure", "conjecture", "sources", "status",
        "reason", "used_on", "key"]
STRUCTURES = ["none", "scale", "on_this_day", "etymology", "cross_field", "pun"]
HEDGE = re.compile(r"\b(perhaps|might|may have|may be|possibly|probably|it is tempting|one guess|could be|arguably)\b", re.I)
EM = "—"

# Stored sources for history, quirk and etymology facts: Wikipedia articles (plain-text extracts through
# the MediaWiki API; several hold an etymology) and EIA's history pages.
WIKI = ["Pearl Street Station", "Drake Well", "Hoover Dam", "Shippingport Atomic Power Station", "Chicago Pile-1",
        "Northeast blackout of 1965", "Northeast blackout of 2003", "2021 Texas power crisis", "War of the currents",
        "Henry Hub", "Strategic Petroleum Reserve (United States)", "1973 oil crisis", "Spindletop",
        "Trans-Alaska Pipeline System", "Barrel (unit)", "British thermal unit", "Watt", "Horsepower", "Kerosene",
        "Petroleum", "Electric Reliability Council of Texas", "Tennessee Valley Authority",
        "Rural Electrification Administration", "Grand Coulee Dam", "Three Mile Island accident", "Solar cell",
        "Adams Power Plant Transformer House", "Liquefied natural gas", "Hubbert peak theory",
        "Public Utility Regulatory Policies Act", "Federal Energy Regulatory Commission", "Smith–Putnam wind turbine",
        "Daylight saving time", "Duck curve", "Energy Information Administration", "Hydraulic fracturing in the United States",
        "The Geysers", "Price-Anderson Nuclear Industries Indemnity Act", "Colonial Pipeline",
        "Edison Electric Light Company", "Joule", "Volt", "Tesla (unit)", "Kilowatt-hour", "Therm", "Natural gas",
        "Electric power transmission", "Alternating current", "Power outage", "Capacity factor"]
EIA_PAGES = [
    ("EIA, History of wind power", "https://www.eia.gov/energyexplained/wind/history-of-wind-power.php"),
    ("EIA, Hydropower explained: history", "https://www.eia.gov/energyexplained/hydropower/"),
    ("EIA, Nuclear explained: US nuclear industry", "https://www.eia.gov/energyexplained/nuclear/us-nuclear-industry.php"),
    ("EIA, Oil and petroleum products explained", "https://www.eia.gov/energyexplained/oil-and-petroleum-products/"),
    ("EIA, Electricity explained: history of the grid", "https://www.eia.gov/energyexplained/electricity/delivery-to-consumers.php"),
]
ENERGY_WORDS = re.compile(r"\b(oil|petroleum|gasoline|natural gas|pipeline|electric light|electricity|electric power|"
                          r"power station|power plant|nuclear reactor|nuclear power|hydroelectric|coal mine|coal|OPEC|"
                          r"blackout|solar|wind turbine|energy|refinery|kerosene|uranium|oil well|oil field|dam)\b", re.I)
NOT_ENERGY = re.compile(r"\b(chair|execution|executed|bomb|weapon|guitar|missile|warhead)\b", re.I)


# ---------------------------------------------------------------------------------------------
# text checks
# ---------------------------------------------------------------------------------------------

def norm(s):
    """Whitespace collapsed, curly quotes and dashes made plain, case folded: for finding a span."""
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace(EM, "-").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().casefold()


def raw_text(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    return open(full, encoding="utf-8").read()


def unverified(text, pool):
    import ask as chat_ask
    return chat_ask.unverified(text, pool)


STOP = set("this that with from into over under than then when were have been their there which while about after "
           "before also only more most such some other them they these those what your will would could should being "
           "because since same just very much many first like".split())
FACT_COVERAGE, SECOND_COVERAGE = 0.85, 0.70


def coverage(text, spans, extra=""):
    """Session 23: the share of the text's content words (longer than 3 letters, not stopwords) found in the
    spans or in the source's title (extra), matching on the first five letters so an inflection counts.
    A span check alone passed drafts that added claims around a true quote; this catches most of them."""
    toks = lambda t: re.findall(r"[a-z]+", norm(t))  # noqa: E731
    words = [w for w in toks(text) if len(w) > 3 and w not in STOP]
    pool = set(toks(" ".join(spans) + " " + extra))
    pre = {w[:5] for w in pool}
    missing = [w for w in words if w not in pool and w[:5] not in pre]
    return 1 - len(missing) / max(1, len(words)), missing


def check_record(r):
    """The reasons a bank row or an item fails, [] if it passes. r has fact, second, structure,
    conjecture and sources: [{part: fact|second, label, url, raw, span, retrieved_at}]."""
    problems = []
    fact, second = r["fact"].strip(), (r.get("second") or "").strip()
    structure = r.get("structure") or "none"
    if not fact:
        return ["no fact"]
    if EM in fact + second:
        problems.append("em dash")
    srcs = r["sources"] if isinstance(r["sources"], list) else json.loads(r["sources"] or "[]")
    by_part = {"fact": [], "second": []}
    for s in srcs:
        text = raw_text(s["raw"])
        if text is None:
            problems.append(f"stored source missing: {s['raw']}")
            continue
        if not s.get("span") or norm(s["span"]) not in norm(text):
            problems.append(f"span not in its stored source ({s['raw']}): {s.get('span', '')[:80]!r}")
            continue
        by_part.setdefault(s["part"], []).append(s["span"])
    if not by_part["fact"]:
        problems.append("the fact has no verified source span")
    bad = unverified(fact, by_part["fact"])
    if bad:
        problems.append(f"numbers in the fact not in its source: {bad}")
    sourced = r.get("kind") in ("history", "quirk")
    titles = " ".join(s["label"].split(", ", 1)[-1] for s in srcs)
    if sourced and by_part["fact"]:
        c, miss = coverage(fact, by_part["fact"], titles)
        if c < FACT_COVERAGE:
            problems.append(f"the fact's words are {c:.0%} in its spans (needs {FACT_COVERAGE:.0%}; missing {miss[:8]})")
    if second:
        if structure == "none":
            problems.append("a second half with structure none")
        elif structure == "pun":
            if re.search(r"\d", second):
                problems.append("a pun holds a number")
        elif structure in ("scale", "on_this_day", "etymology", "cross_field"):
            conj = str(r.get("conjecture", "")).lower() in ("true", "1", "yes")
            if not by_part["second"] and not conj:
                problems.append(f"the {structure} half has no verified source span")
            if conj and not HEDGE.search(second):
                problems.append("a conjecture not phrased as one")
            bad = unverified(second, by_part["second"] + by_part["fact"])
            if bad:
                problems.append(f"numbers in the second half not in its sources: {bad}")
            if (sourced or structure == "on_this_day") and by_part["second"] and not conj:
                c, miss = coverage(second, by_part["second"] + by_part["fact"], titles)
                if c < SECOND_COVERAGE:
                    problems.append(f"the second half's words are {c:.0%} in its spans (needs {SECOND_COVERAGE:.0%}; "
                                    f"missing {miss[:8]})")
    return problems


# ---------------------------------------------------------------------------------------------
# the bank
# ---------------------------------------------------------------------------------------------

def read_bank():
    if not os.path.exists(BANK):
        return pd.DataFrame(columns=COLS)
    return pd.read_csv(BANK, dtype=str, keep_default_na=False)


def write_bank(df):
    os.makedirs(FACTS, exist_ok=True)
    df[COLS].to_csv(BANK, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)


def save_raw(sub, name, text, meta):
    """Store a fetched source as is, with a header naming where and when it was fetched."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = os.path.join(RAW, sub)
    os.makedirs(d, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:60]
    path = os.path.join(d, f"{slug}_{stamp}.txt")
    head = "".join(f"# {k}: {v}\n" for k, v in meta.items()) + f"# retrieved_at: {stamp}\n\n"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(head + text)
    return os.path.relpath(path, ROOT).replace(os.sep, "/"), stamp


def fetch_wiki(title, log):
    r = requests.get("https://en.wikipedia.org/w/api.php", headers=UA, timeout=60, params={
        "action": "query", "prop": "extracts|info", "explaintext": 1, "titles": title, "format": "json",
        "redirects": 1, "inprop": "url"})
    r.raise_for_status()
    page = next(iter(r.json()["query"]["pages"].values()))
    if "extract" not in page or not page["extract"].strip():
        raise RuntimeError(f"Wikipedia: no text for {title!r}")
    url = page.get("fullurl") or f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    raw, stamp = save_raw("wikipedia", title, page["extract"], {
        "source": "Wikipedia (CC BY-SA 4.0), MediaWiki API plain-text extract", "title": page.get("title", title),
        "url": url, "revision": page.get("lastrevid", "")})
    log(f"  fetched Wikipedia {title!r}: {len(page['extract'])} characters -> {raw}")
    return {"label": f"Wikipedia, {page.get('title', title)}", "url": url, "raw": raw, "retrieved_at": stamp,
            "text": page["extract"]}


def fetch_eia(label, url, log):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    html = r.text
    body = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"<[^>]+>", " ", body)
    import html as h
    text = re.sub(r"[ \t]+", " ", h.unescape(text))
    text = "\n".join(x.strip() for x in text.splitlines() if x.strip())
    raw, stamp = save_raw("eia", label, text, {"source": "U.S. Energy Information Administration (public domain)",
                                               "url": url})
    log(f"  fetched {label}: {len(text)} characters -> {raw}")
    return {"label": label, "url": url, "raw": raw, "retrieved_at": stamp, "text": text}


# ---------------------------------------------------------------------------------------------
# warehouse facts: computed here, no model; the rows used are stored as the fact's raw source
# ---------------------------------------------------------------------------------------------

def _cite(table):
    import erw
    s = erw.sources(table)
    reps = "; ".join(f"{r.get('publisher', '')}: {r.get('report', '')} ({r.get('report_url', '')})" for r in s["reports"])
    return reps, s.get("retrieved", "")


def _wsource(key, table, evidence, part="fact"):
    reps, retrieved = _cite(table)
    raw, stamp = save_raw("warehouse", key, evidence, {"table": table, "source reports": reps,
                                                       "table retrieved": retrieved,
                                                       "computed by": "warehouse/news/funfact.py"})
    pubs = ", ".join(dict.fromkeys(r.split(":")[0] for r in reps.split("; ") if r))
    return {"part": part, "label": f"ERW table {table}", "table": table, "publisher": pubs, "url": "/data", "raw": raw,
            "span": evidence.splitlines()[0], "retrieved_at": stamp, "evidence": evidence}


def w_fuel_extreme(key):
    import erw
    _, entity, which = key.split(":", 2)
    names = {"henry_hub": ("Henry Hub natural gas", "USD/MMBtu"), "wti_cushing": ("WTI crude at Cushing", "USD/bbl"),
             "brent": ("Brent crude", "USD/bbl")}
    label, unit = names[entity]
    f = erw.fetch("eia_fuel_spot_prices")
    s = f[f["entity"] == f"eia:{entity}"].sort_values("ts_utc")
    row = s.loc[s["value"].idxmax()] if which == "max" else s.loc[s["value"].idxmin()]
    first, last = s.iloc[0], s.iloc[-1]
    ratio = abs(row["value"] / last["value"])
    ev = (f"eia_fuel_spot_prices eia:{entity}: {which} {row['value']:.2f} {unit} on {row['ts_utc']:%Y-%m-%d}; "
          f"series starts {first['ts_utc']:%Y-%m-%d}; latest {last['value']:.2f} on {last['ts_utc']:%Y-%m-%d}; "
          f"ratio of the {which} to the latest {ratio:.1f}")
    if which == "max":
        fact = (f"The highest daily {label} spot price in EIA's series, which starts on {first['ts_utc']:%Y-%m-%d}, was "
                f"{row['value']:.2f} {unit} on {row['ts_utc']:%Y-%m-%d}.")
        second = f"That is about {ratio:.1f} times the latest close, {last['value']:.2f} on {last['ts_utc']:%Y-%m-%d}."
    else:
        fact = (f"The lowest daily {label} spot price in EIA's series, which starts on {first['ts_utc']:%Y-%m-%d}, was "
                f"{row['value']:.2f} {unit} on {row['ts_utc']:%Y-%m-%d}"
                + (": below zero, sellers paid buyers to take the oil." if row["value"] < 0 else "."))
        second = "" if row["value"] <= 0 else f"The latest close, {last['value']:.2f} on {last['ts_utc']:%Y-%m-%d}, is about {last['value'] / row['value']:.1f} times it."
        if second:
            ev += f"; latest over the min {last['value'] / row['value']:.1f}"
    src = _wsource(key, "eia_fuel_spot_prices", ev)
    return dict(kind="warehouse", fact=fact, second=second, structure="scale" if second else "none",
                sources=[src] + ([dict(src, part="second")] if second else []))


def w_oldest_generator(key):
    import erw
    g = erw.fetch("eia860m_operating_generators")
    g = g[g["operating_year"].astype(str).str.fullmatch(r"\d{4}")]
    y = g["operating_year"].astype(int)
    oldest = g[y == y.min()]
    r = oldest.iloc[0]
    n_units = len(oldest)
    ev = (f"eia860m_operating_generators: earliest operating_year {r['operating_year']}: plant {r['name']}, state "
          f"{r['state']}, technology {r['technology']}, {n_units} generators with that year; inventory vintage {r['vintage']}; "
          f"{len(g)} operating generators with a year")
    fact = (f"The oldest generators still operating in EIA's inventory entered service in {r['operating_year']}: "
            f"{n_units} {r['technology'].lower()} units at the {r['name']} plant in {STATES.get(r['state'], r['state'])}.")
    return dict(kind="warehouse", fact=fact, second="", structure="none",
                sources=[_wsource(key, "eia860m_operating_generators", ev)])


def w_state_share(key):
    import erw
    _, state, fuel = key.split(":", 2)
    m = erw.fetch("state_generation_mix_monthly")
    m = m[m["entity"] == f"eia:{state}"]
    m = m.assign(year=m["ts_utc"].dt.year)
    full = m.groupby("year")["ts_utc"].nunique()
    years = [y for y, n in full.items() if n == 12]
    y0, y1 = years[0], years[-1]
    def share(y):
        t = m[m["year"] == y]
        return 100 * t[t["variable"] == f"net_generation_{fuel}_mwh"]["value"].sum() / t["value"].sum()
    s0, s1 = share(y0), share(y1)
    label = fuel.replace("_", " ")
    ev = (f"state_generation_mix_monthly eia:{state}: {label} share of net generation {s0:.1f}% in {y0}, {s1:.1f}% in {y1} "
          f"(sums of monthly MWh over complete years)")
    fact = f"In {y0}, {label} made {s0:.1f}% of the electricity generated in {STATES[state]}; in {y1} it made {s1:.1f}%."
    return dict(kind="warehouse", fact=fact, second="", structure="none",
                sources=[_wsource(key, "state_generation_mix_monthly", ev)])


def w_peak_premium(key):
    import erw
    _, hub = key.split(":", 1)
    a = erw.fetch("ercot_peak_premium_annual")
    a = a[a["entity"] == f"ercot:{hub}"]
    mx = a[a["variable"] == "all_max"].sort_values("value").iloc[-1]
    neg = a[a["variable"] == "n_negative"].sort_values("value").iloc[-1]
    ev = (f"ercot_peak_premium_annual ercot:{hub}: years {a['ts_utc'].min():%Y} to {a['ts_utc'].max():%Y}; "
          f"highest all_max {mx['value']:.2f} USD/MWh in {mx['ts_utc']:%Y}; "
          f"most negative 15-minute intervals {neg['value']:.0f} in {neg['ts_utc']:%Y}")
    fact = (f"ERCOT's real-time price at {hub} reached {mx['value']:.2f} USD/MWh in a 15-minute interval in {mx['ts_utc']:%Y}, "
            f"the highest of any year since {a['ts_utc'].min():%Y}; the year with the most negative-price intervals there was "
            f"{neg['ts_utc']:%Y}, with {neg['value']:.0f}.")
    return dict(kind="warehouse", fact=fact, second="", structure="none",
                sources=[_wsource(key, "ercot_peak_premium_annual", ev)])


def w_retail_top(key):
    import erw
    r = erw.fetch("eia_retail_sales_monthly")
    st = r["entity"].str.split(":").str[2]
    r = r[(r["variable"] == "retail_sales") & r["entity"].str.endswith(":ALL") & st.isin(STATES)]
    r = r.assign(year=r["ts_utc"].dt.year)
    n = r.groupby("year")["ts_utc"].nunique()
    y = max(k for k, v in n.items() if v == 12)
    t = r[r["year"] == y].groupby("entity")["value"].sum().sort_values(ascending=False)
    top, second = STATES[t.index[0].split(":")[2]], STATES[t.index[1].split(":")[2]]
    ratio = t.iloc[0] / t.iloc[1]
    ev = (f"eia_retail_sales_monthly retail_sales ALL sectors, {y}: {top} {t.iloc[0]:,.0f} MWh; {second} {t.iloc[1]:,.0f} MWh; "
          f"ratio {ratio:.2f}")
    fact = f"In {y}, {top} bought more electricity than any other state: {t.iloc[0]:,.0f} MWh at retail."
    sec = f"That is {ratio:.2f} times the next state, {second}, at {t.iloc[1]:,.0f} MWh."
    src = _wsource(key, "eia_retail_sales_monthly", ev)
    return dict(kind="warehouse", fact=fact, second=sec, structure="scale", sources=[src, dict(src, part="second")])


def w_curtailment_record(key):
    import erw
    m = erw.fetch("iso_curtailment_monthly")
    c = m[(m["entity"] == "caiso:ISO") & m["variable"].isin(["curtailed_solar_local_mwh", "curtailed_solar_system_mwh",
                                                              "curtailed_wind_local_mwh", "curtailed_wind_system_mwh"])]
    t = c.groupby("ts_utc")["value"].sum().sort_values()
    top_ts, top = t.index[-1], t.iloc[-1]
    ev = (f"iso_curtailment_monthly caiso:ISO: wind and solar curtailed (local and system), most in one month "
          f"{top:,.0f} MWh in {top_ts:%Y-%m}; months {len(t)} from {t.index.min():%Y-%m}")
    fact = (f"California's grid operator curtailed {top:,.0f} MWh of wind and solar output in {top_ts:%B %Y}, "
            f"its most in any month since {t.index.min():%Y}.")
    return dict(kind="warehouse", fact=fact, second="", structure="none",
                sources=[_wsource(key, "iso_curtailment_monthly", ev)])


def w_datacenter_operator(key):
    import erw
    d = erw.fetch("datacenter_facilities")
    col = "operator" if "operator" in d.columns else d.columns[0]
    c = d[d[col].astype(str) != ""][col].value_counts()
    ev = (f"datacenter_facilities: {len(d)} facilities; most by one operator: {c.index[0]} {c.iloc[0]}; "
          f"next {c.index[1]} {c.iloc[1]}")
    fact = (f"Of the {len(d)} datacenter facilities the ERW tracks, {c.index[0]} runs the most, {c.iloc[0]}, "
            f"ahead of {c.index[1]} with {c.iloc[1]}.")
    return dict(kind="warehouse", fact=fact, second="", structure="none",
                sources=[_wsource(key, "datacenter_facilities", ev)])


W_KEYS = (["fuel:henry_hub:max", "fuel:wti_cushing:min", "fuel:brent:max", "fuel:wti_cushing:max", "fuel:henry_hub:min",
           "oldest", "retail_top", "curtailment_record", "datacenter_operator"]
          + [f"share:{s}:{f}" for s, f in (("TX", "wind"), ("CA", "solar"), ("IA", "wind"), ("IL", "nuclear"),
                                           ("WV", "coal"), ("WA", "hydro"), ("FL", "natural_gas"), ("KS", "wind"))]
          + [f"premium:{h}" for h in ("HB_NORTH", "HB_WEST", "HB_HOUSTON")])


STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
          "CT": "Connecticut", "DE": "Delaware", "DC": "the District of Columbia", "FL": "Florida", "GA": "Georgia",
          "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
          "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
          "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
          "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
          "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
          "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
          "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}


def warehouse_fact(key):
    kind = key.split(":")[0]
    fn = {"fuel": w_fuel_extreme, "oldest": w_oldest_generator, "share": w_state_share, "premium": w_peak_premium,
          "retail_top": w_retail_top, "curtailment_record": w_curtailment_record,
          "datacenter_operator": w_datacenter_operator}[kind]
    return fn(key)


# ---------------------------------------------------------------------------------------------
# history facts: drafted by the model from one stored source, checked here
# ---------------------------------------------------------------------------------------------

DRAFT_SYSTEM = """You write one fun fact for the daily Energy Digest of the Energy Research Warehouse (ERW), from one source text.
Rules:
- fact: one sentence, an energy fact first: a piece of energy history, or a quirk of how the energy system works. Plain, accurate, at most 40 words. Every number in it must appear in fact_spans.
- fact_spans: one to three exact quotes, each copied character for character from the source text (each at most 300 characters), that together support every word of the fact. Write the fact in the words of the spans: add no descriptor, cause, consequence, superlative or name that the spans do not state. A checker compares the fact's words with the spans and drops the fact if they are not there.
- second: an optional second sentence of the requested structure, at most 30 words:
  etymology: where an energy word comes from, supported by second_spans (exact quotes from the source text), in their words;
  cross_field: a connection from the energy fact to another field (science, language, art, sport, economics), supported by second_spans, in their words;
  pun: a light, clean pun on the fact; it makes no claim and holds no number; second_spans empty;
  none: leave second empty and second_spans empty.
  If the source text cannot support the requested structure, return second empty and second_spans empty.
- conjecture: true only if the second sentence is a guess the source does not state; then it must be phrased as one (perhaps, might, may have). Prefer false.
- No em dashes. No hype. Do not use facts that are not in the source text."""
DRAFT_SCHEMA = {"type": "object", "properties": {
    "fact": {"type": "string"}, "fact_spans": {"type": "array", "items": {"type": "string"}},
    "second": {"type": "string"}, "second_spans": {"type": "array", "items": {"type": "string"}},
    "conjecture": {"type": "boolean"}},
    "required": ["fact", "fact_spans", "second", "second_spans", "conjecture"], "additionalProperties": False}


JUDGE_SYSTEM = """You check a fun fact against quotes from its source. For the sentence given, decide whether the quotes
state everything the sentence claims: every date, number, name, place, cause, sequence and superlative. A claim the quotes
do not state, or state differently (for example "before 1903" read as "in 1903"), makes it unsupported. A pun or a
sentence phrased as a guess (perhaps, might) makes no claim of its own; judge only what it asserts as fact.
Return JSON: supported (true or false) and unsupported (the claims the quotes do not state, empty if none)."""
JUDGE_SCHEMA = {"type": "object", "properties": {"supported": {"type": "boolean"},
                                                 "unsupported": {"type": "array", "items": {"type": "string"}}},
                "required": ["supported", "unsupported"], "additionalProperties": False}


class Model:
    def __init__(self, log):
        import anthropic
        from score import PRICES, pick_model
        self.client = anthropic.Anthropic(api_key=ip.load_key("ANTHROPIC_API_KEY", log))
        self.model = pick_model(self.client, log)
        self.price = PRICES.get(self.model)
        self.cost, self.calls, self.log = 0.0, 0, log

    def draft(self, src, structure):
        text = src["text"][:14000]
        msg = (f"Source: {src['label']} ({src['url']})\nRequested structure for the second sentence: {structure}\n\n"
               f"Source text:\n{text}")
        resp = self.client.messages.create(
            model=self.model, max_tokens=1500, system=DRAFT_SYSTEM, messages=[{"role": "user", "content": msg}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": DRAFT_SCHEMA}})
        self.calls += 1
        if self.price:
            self.cost += (resp.usage.input_tokens * self.price[0] + resp.usage.output_tokens * self.price[1]) / 1e6
        return json.loads(next(b.text for b in resp.content if b.type == "text"))

    def judge(self, sentence, spans):
        """Session 23: an independent check, at creation only, that the quotes state every claim of the sentence
        (the span and coverage checks cannot see a misreading of a quote). Returns the unsupported claims."""
        msg = "Sentence:\n" + sentence + "\n\nQuotes from the source:\n" + "\n".join(f"- {x}" for x in spans)
        resp = self.client.messages.create(
            model=self.model, max_tokens=800, system=JUDGE_SYSTEM, messages=[{"role": "user", "content": msg}],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}})
        self.calls += 1
        if self.price:
            self.cost += (resp.usage.input_tokens * self.price[0] + resp.usage.output_tokens * self.price[1]) / 1e6
        out = json.loads(next(b.text for b in resp.content if b.type == "text"))
        return [] if out["supported"] and not out["unsupported"] else (out["unsupported"] or ["not supported"])


def history_fact(model, src, structure, key):
    d = model.draft(src, structure)
    base = {"label": src["label"], "url": src["url"], "raw": src["raw"], "retrieved_at": src["retrieved_at"]}
    srcs = [dict(base, part="fact", span=x) for x in d["fact_spans"][:3] if x.strip()]
    second = d["second"].strip()
    st = structure if second else "none"
    if second:
        srcs += [dict(base, part="second", span=x) for x in d["second_spans"][:2] if x.strip()]
    kind = "history" if src["raw"].split("/")[-2] in ("wikipedia", "eia") else "quirk"
    return dict(kind=kind, fact=d["fact"].strip(), second=second, structure=st, conjecture=str(bool(d["conjecture"])),
                sources=srcs)


def add_facts(n, log, rng):
    """Add n verified facts to the bank: warehouse and history facts in turn, from sources not used yet.
    A fact that fails a check is kept with status dropped and the reason, and does not count."""
    bank = read_bank()
    used = set(bank["key"])
    added, tries, model = 0, 0, None
    wk = [k for k in W_KEYS if k not in used]
    wiki = [t for t in WIKI if f"wiki:{t}" not in used]
    eia = [p for p in EIA_PAGES if f"eia:{p[1]}" not in used]
    rng.shuffle(wk)
    rng.shuffle(wiki)
    # structures asked of history facts, in turn; cross-field only sometimes
    wanted = ["etymology", "pun", "none", "cross_field", "etymology", "pun", "none"]
    while added < n and tries < n * 4:
        tries += 1
        use_w = (len(bank) + tries) % 3 == 0 and wk
        key = "?"
        try:
            if use_w:
                key = wk.pop()
                rec = warehouse_fact(key)
            else:
                if model is None:
                    model = Model(log)
                structure = wanted[(len(bank) + tries) % len(wanted)]
                if eia and tries % 5 == 0:
                    label, url = eia.pop()
                    key = f"eia:{url}"
                    src = fetch_eia(label, url, log)
                elif wiki:
                    title = wiki.pop()
                    key = f"wiki:{title}"
                    src = fetch_wiki(title, log)
                elif wk:
                    key = wk.pop()
                    rec = warehouse_fact(key)
                    src = None
                else:
                    log("  no unused source left")
                    break
                if src is not None:
                    rec = history_fact(model, src, structure, key)
        except Exception as exc:
            log(f"  {key}: FAILED to build ({ip.redact(repr(exc))[:200]})")
            continue
        problems = check_record(rec)
        if not problems and rec["kind"] in ("history", "quirk"):
            fsp = [x["span"] for x in rec["sources"] if x["part"] == "fact"]
            un = model.judge(rec["fact"], fsp)
            if un:
                problems.append(f"the judge found the fact's claims not in its spans: {un}")
            elif rec.get("second") and rec.get("structure") in ("etymology", "cross_field"):
                un = model.judge(rec["second"], fsp + [x["span"] for x in rec["sources"] if x["part"] == "second"])
                if un:
                    problems.append(f"the judge found the second half's claims not in its spans: {un}")
        fid = "ff_" + hashlib.sha1(f"{key}|{rec['fact']}".encode()).hexdigest()[:10]
        row = dict(fact_id=fid, created_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   kind=rec["kind"], fact=rec["fact"], second=rec.get("second", ""), structure=rec.get("structure", "none"),
                   conjecture=rec.get("conjecture", "False"),
                   sources=json.dumps([{k: v for k, v in s.items() if k != "evidence"} for s in rec["sources"]], ensure_ascii=False),
                   status="dropped" if problems else "verified", reason="; ".join(problems), used_on="", key=key)
        if problems and rec.get("second") and not any("fact" in p and "second" not in p for p in problems):
            # the fact passes and only the second half fails: keep the fact alone
            only_fact = dict(rec, second="", structure="none",
                             sources=[s for s in rec["sources"] if s["part"] == "fact"])
            judged = (only_fact["kind"] == "warehouse" or model is None or not any(
                "judge found the fact" in p for p in problems) and not model.judge(
                only_fact["fact"], [x["span"] for x in only_fact["sources"]]))
            if not check_record(only_fact) and judged:
                row.update(second="", structure="none", status="verified",
                           reason="second half dropped: " + "; ".join(problems),
                           sources=json.dumps([{k: v for k, v in s.items() if k != "evidence"} for s in only_fact["sources"]],
                                              ensure_ascii=False))
        bank = pd.concat([bank, pd.DataFrame([row])], ignore_index=True)
        used.add(key)
        if row["status"] == "verified":
            added += 1
            log(f"  + {fid} ({row['kind']}, {row['structure']}): {row['fact']} {row['second']}".rstrip())
        else:
            log(f"  - {fid} dropped: {row['reason']}")
        write_bank(bank)
    cost = model.cost if model else 0.0
    return added, cost, (model.calls if model else 0)


# ---------------------------------------------------------------------------------------------
# the day's item
# ---------------------------------------------------------------------------------------------

def structure_for(date):
    d = pd.Timestamp(date)
    wd = d.weekday()
    if wd == 3:
        return "cross_field" if d.isocalendar()[1] % 2 == 1 else "etymology"
    return {0: "none", 1: "scale", 2: "on_this_day", 4: "pun"}.get(wd, "none")


def on_this_day(date, log):
    """An energy event on this month and day, verbatim from the Wikipedia page for the date (its Events
    list), with the stored source; None if the page lists none."""
    d = pd.Timestamp(date)
    title = f"{d:%B} {d.day}"
    src = fetch_wiki(title, log)
    text = src["text"]
    ev = text.split("== Births ==")[0]
    for ln in ev.splitlines():
        m = re.match(r"^\s*(\d{3,4})\s*[–-]\s*(.+)$", ln)
        if m and ENERGY_WORDS.search(m.group(2)) and not NOT_ENERGY.search(m.group(2)):
            line = m.group(2).strip().rstrip(".").replace(EM, ",")
            return (f"On this day in {m.group(1)}: {line}.",
                    {"part": "second", "label": src["label"], "url": src["url"], "raw": src["raw"], "span": ln.strip(),
                     "retrieved_at": src["retrieved_at"]})
    log(f"  on this day: no energy event on {title}")
    return None


def write_item(date, log):
    bank = read_bank()
    ok = bank[(bank["status"] == "verified") & (bank["used_on"] == "")]
    if ok.empty:
        ok = bank[bank["status"] == "verified"]  # every fact used: start again from the least recently used
    if ok.empty:
        raise RuntimeError("no verified fact in the bank")
    want = structure_for(date)
    rng = random.Random(date)
    same = ok[ok["structure"] == want]
    pick = (same if not same.empty and want not in ("none", "on_this_day") else ok).sample(1, random_state=rng.randrange(10**6)).iloc[0]
    srcs = json.loads(pick["sources"])
    item = dict(date=date, fact_id=pick["fact_id"], kind=pick["kind"], fact=pick["fact"], second="", structure="none",
                conjecture=pick["conjecture"], sources=[s for s in srcs if s["part"] == "fact"])
    if want == "on_this_day":
        try:
            otd = on_this_day(date, log)
        except Exception as exc:
            log(f"  on this day: FAILED ({ip.redact(repr(exc))[:200]})")
            otd = None
        if otd:
            item.update(second=otd[0], structure="on_this_day", sources=item["sources"] + [otd[1]])
    elif want != "none" and pick["structure"] == want and pick["second"]:
        item.update(second=pick["second"], structure=want, sources=srcs)
    problems = check_record(item)
    if problems and item["second"]:
        log(f"  item second half failed ({problems}); the fact runs alone")
        item.update(second="", structure="none", sources=[s for s in item["sources"] if s["part"] == "fact"])
        problems = check_record(item)
    if problems:
        raise RuntimeError(f"the picked fact {pick['fact_id']} failed its check: {problems}")
    os.makedirs(ITEMS, exist_ok=True)
    with open(os.path.join(ITEMS, f"{date}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(item, f, ensure_ascii=False, indent=1)
    bank.loc[bank["fact_id"] == pick["fact_id"], "used_on"] = date
    write_bank(bank)
    return item


def load_item(date):
    p = os.path.join(ITEMS, f"{date}.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def verify_item(item):
    return check_record(item)


def item_markdown(item):
    text = item["fact"] + (" " + item["second"] if item.get("second") else "")
    seen, links = set(), []
    for s in item["sources"]:
        if s["url"] in seen:
            continue
        seen.add(s["url"])
        links.append(f"[{s['label']}]({s['url']})" if s["url"].startswith("http")
                     else f"`{s.get('table', s['label'])}` ({s.get('publisher') or 'ERW'})")
    return [text, "", "Sources: " + ", ".join(links) + "."]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW fun fact engine")
    ap.add_argument("--seed", type=int, help="add this many verified facts to the bank, and write no item")
    ap.add_argument("--add", type=int, default=1, help="facts to add on a daily run (default 1)")
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: today, UTC)")
    ap.add_argument("--verify", action="store_true", help="re-verify every verified fact in the bank")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_funfact_{run_id}.log"))
    status = dict(table="funfact", market="bank", status="ok", detail="")
    try:
        rng = random.Random(run_id)
        if args.verify:
            bank = read_bank()
            bad = 0
            for r in bank[bank["status"] == "verified"].to_dict("records"):
                p = check_record(r)
                if p:
                    bad += 1
                    log(f"  {r['fact_id']}: {p}")
            status["detail"] = f"{(bank['status'] == 'verified').sum()} verified facts re-checked, {bad} failed"
        elif args.seed:
            added, cost, calls = add_facts(args.seed, log, rng)
            status["detail"] = f"seed: {added} verified facts added, {calls} model calls, cost USD {cost:.4f}"
            if added < args.seed:
                status["status"] = "failed"
                status["detail"] += f" (asked for {args.seed})"
        else:
            date = args.date or pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")
            if pd.Timestamp(date).weekday() >= 5:
                msg = f"no weekend issue ({date}): no item written"
                log(msg)
                print(f"news_funfact SKIPPED: {msg}")
                ip.write_status("news_funfact", run_id, [dict(status, status="skipped", detail=msg)])
                log.close()
                return 0
            added, cost, calls = add_facts(args.add, log, rng)
            item = write_item(date, log)
            status["detail"] = (f"{date}: {item['fact_id']} ({item['structure']}); bank +{added}, {calls} model calls, "
                                f"cost USD {cost:.4f}")
        log(status["detail"])
        print(f"funfact: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"news_funfact FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("news_funfact", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
