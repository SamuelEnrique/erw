#!/usr/bin/env python3
"""docs/licenses.md: for every table, what its publishers' own pages allow (session 205, the licensing sweep).

Energy Research Warehouse (ERW). Three files in git hold what the document is built from, and this script writes it:

    warehouse/metadata/license_reads.csv      every read of a publisher's page: the address, the time, the answer
                                              (scripts/license_read.py writes it, one request a publisher)
    warehouse/metadata/license_verdicts.csv   for each publisher: the sentence taken from the page read, the verdict
                                              on it, the contact and the price where the page names one. Written by a
                                              session; the sentence is cut from the saved page, never typed
    warehouse/metadata/license_tables.csv     for each table of coverage.csv: its publishers (`tables`, below)

    python scripts/licenses.py tables --headers C:/.../warehouse/output    # a data machine: the tables' own headers are read
    python scripts/licenses.py write                                        # docs/licenses.md, from the three files and coverage.csv
    python scripts/licenses.py check                                        # exit 1 if a table or a publisher is not accounted for
    python scripts/licenses.py status                                       # session 207: warehouse/metadata/license_status.csv and the site's copy
    python scripts/licenses.py state                                        # session 248: docs/state/licenses_<the public day>.md (scripts/license_state.py)

A table's publishers: those the source registry names for it (warehouse/metadata/sources.csv). A table the ERW
derives takes the publishers of the tables its header names under "Derived from", and so on down; of the grid
operators among them it keeps those whose grid its own coverage row lists, so a table built from ERCOT's rows of a
shared price table does not inherit MISO. A table no rule resolves is named by hand in BY_HAND, with the reason.

A table's verdict is the most restrictive of its publishers' verdicts. A publisher whose page no session of this
sweep read has no verdict: a table that would otherwise be public is then "not settled", never public by default.

Nothing here changes coverage.csv: where its flag and the verdict differ, the document lists the table and a person
rules. A verdict is a session's reading of a sentence, not legal advice.
"""

import argparse
import collections
import csv
import datetime as dt
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
META = os.path.join(ROOT, "warehouse", "metadata")
COVERAGE, SOURCES = os.path.join(META, "coverage.csv"), os.path.join(META, "sources.csv")
READS, VERDICTS, TABLES = (os.path.join(META, f"license_{n}.csv") for n in ("reads", "verdicts", "tables"))
DOC = os.path.join(ROOT, "docs", "licenses.md")
HOLDS_SHOWN = os.path.join(ROOT, "docs", "licenses_holds.csv")   # session 505: site/scripts/check-holds.mjs --csv
PUBLIC, PERMISSION, PAID, FORBIDDEN = "may be public", "needs written permission", "needs a paid license", "forbidden"
ORDER = [PUBLIC, PERMISSION, PAID, FORBIDDEN]
OWN = {"ERW", "Anthropic"}          # the ERW's own work and its own bills: no publisher's page applies
GRIDS = {"CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "SPP", "PJM"}
# a registry name, or a host a story was read on, to the short name the verdicts file uses
CANON = [
    (r"California (ISO|Independent System Operator)|^caiso\.com$|^CAISO$", "CAISO"), (r"New York (ISO|Independent System Operator)|^nyiso\.com$", "NYISO"),
    (r"Energy Information Administration|^EIA ", "EIA"), (r"Electric Reliability Council|^ercot\.com$", "ERCOT"), (r"ISO New England|^ISO-NE", "ISO-NE"),
    (r"^nyiso mis$", "NYISO"),  # session 311: the news feed of NYISO's market notices is NYISO's
    (r"Southwest Power Pool", "SPP"), (r"Midcontinent|misoenergy\.org|^MISO", "MISO"), (r"^PJM", "PJM"),
    (r"National Centers for Environmental", "NOAA NCEI"), (r"National Weather Service", "NWS"), (r"Air Resources Board", "CARB"),
    (r"St\. Louis|FRED", "FRED"),  # a name "through FRED" is FRED's: this rule goes before the Board's
    (r"Board of Governors|Federal Reserve System", "FRB"),  # session 207: the Board's own H.15 download (frb_treasury_yields)
    (r"PortWatch", "IMF PortWatch"), (r"International Monetary Fund", "IMF"), (r"Berkeley", "Berkeley Lab"), (r"Nuclear Regulatory", "NRC"),
    (r"Census", "Census Bureau"), (r"Commodity Futures", "CFTC"), (r"Regional Greenhouse", "RGGI"), (r"Railroad Commission", "RRC"),
    (r"Federal Energy Regulatory|^FERC$", "FERC"), (r"Energy Research Warehouse|^ERW$", "ERW"),
    (r"(?i)bloomberg", "Bloomberg"), (r"(?i)^ft\.com$|\.ft\.com$|^FT Channels$|Financial Times", "Financial Times"), (r"(?i)hart ?energy", "Hart Energy"),
    (r"(?i)^WSJ$|wsj\.com$", "WSJ"), (r"(?i)reuters", "Reuters"), (r"(?i)hydrogen ?insight", "Hydrogen Insight"), (r"(?i)^JPT Homepage$|jpt\.spe\.org", "JPT"),
    (r"IEA .* International Energy Agency", "IEA"), (r"(?i)cpuc\.ca\.gov|California Public Utilities Commission", "California Public Utilities Commission"),
    (r"Public Utility Commission of Texas|PUC Interchange", "Public Utility Commission of Texas"), (r"(?i)epa\.gov|Environmental Protection Agency|EPA's", "EPA"),
]
# tables no rule resolves, or resolves wrongly: their publishers by hand, each with the reason
BY_HAND = {
    "eia930_demand_growth": (["EIA"], "its header: EIA publications"),
    "eia_all_futures_prices": (["EIA", "CME Group (NYMEX), whose prices EIA republished"], "its header: EIA names the New York Mercantile Exchange as the source of these prices"),
    "ercot_peak_premium_annual": (["ERCOT"], "its header: derived from ERCOT's hub prices (reports NP6-785-ER and NP6-905-CD)"),
    "ercot_peak_premium_monthly": (["ERCOT"], "its header: derived from ERCOT's hub prices (reports NP6-785-ER and NP6-905-CD)"),
    "ercot_node_prices_hourly": (["ERCOT"], "its header: ERCOT's prices read from the saved files of NP3-966-ER, NP4-190-CD and NP6-905-CD (session 378)"),
    "ercot_all_hub_prices_history": (["ERCOT"], "ERCOT's hub price reports"),
    "datacenter_queue_positions": (["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "SPP"], "its header: rows of the six operators' queue tables"),
    "energy_companies": (["ERW"], "its header: names, one-line descriptions written by the ERW, and links"),
    "known_data_faults": (["ERW"], "its header: the ERW's own account of its sources' data"),
    # session 311: derived from the six grids' hub prices (ercot_hub_prices_daily, iso_hub_prices_history) and CAISO's notices
    "grid_stress_days": (["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "SPP"], "its header: the main hubs' real-time prices of six grids, CAISO's notices and ERCOT's (session 322)"),
    "iso_queue_statistics": (["CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "SPP"], "its header: the six ISOs' interconnection queues it counts (session 348)"),
    "large_load_rule_reads": (["Arizona Corporation Commission", "California Public Utilities Commission", "Illinois Commerce Commission",
                               "Oregon Public Utility Commission", "Pennsylvania Public Utility Commission", "Office of the Federal Register (NARA)"],
                              "its header: a model's reads of the rows of large_load_rules and of policy_actions"),
    "large_load_statements": (["utilities and operators, each row's own document (not listed one by one)"], "its header: each row's source is the utility's or operator's own document"),
    "news_scores_shadow": (["the outlets of news_stories"], "its header: scores of the stories of news_stories"),
    "policy_reads": (["Office of the Federal Register (NARA)", "U.S. Department of Energy (DOE)", "NRC", "California Public Utilities Commission", "Public Utility Commission of Texas"],
                     "its header: read from policy_actions"),
    "policy_reads_evidence": (["Office of the Federal Register (NARA)", "U.S. Department of Energy (DOE)", "NRC", "California Public Utilities Commission", "Public Utility Commission of Texas"],
                              "its header: spans of the actions of policy_actions"),
}
NEWS_TABLES = {"news_index", "news_stories"}
# what a table holds, where that matters to the reading of a publisher's sentence
HOLDS = {
    "news_index": "links, dates and the model's own fields; no outlet text",
    "energy_deals": "the model's fields and the story links; no outlet text",
    "datacenter_projects": "the model's fields and the story links; no outlet text",
    "datacenter_facilities": "facts and links; no outlet text",
    "datacenter_operator_sites": "facts from the operators' pages (a site's name and place); no page text",
    "news_stories": "the outlets' titles and summaries",
    "energy_deals_evidence": "a sentence of each story's title or summary",
    "datacenter_projects_evidence": "a sentence of each story's title or summary",
}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def canon(name):
    for rx, key in CANON:
        if re.search(rx, name):
            return key
    return name.strip()


def header_of(path):
    out = {"derived_from": "", "license": ""}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("#"):
                break
            s = line[2:].strip()
            if s.startswith("Derived from:"):
                out["derived_from"] = s
            elif s.startswith("License:"):
                out["license"] = s
    return out


def build_tables(headers_dir, coverage=None, sources=None):
    """[(table, [publishers], how)] for every table of coverage.csv."""
    cov = coverage or rows(COVERAGE)
    registry = {}
    for r in sources or rows(SOURCES):
        for t in re.split(r"[;,]\s*", r["tables"]):
            if t.strip():
                registry.setdefault(t.strip(), set()).add(canon(r["publisher"]))
    names = sorted((r["table"] for r in cov), key=len, reverse=True)
    grids_of = {r["table"]: {g.strip() for g in r["iso"].split(";")} & GRIDS for r in cov}
    heads = {}
    for r in cov:
        p = os.path.join(headers_dir, r["table"] + ".csv")
        heads[r["table"]] = header_of(p) if os.path.exists(p) else {"derived_from": "", "license": ""}

    def inputs(t):
        text = heads[t]["derived_from"] + (" " + heads[t]["license"] if "Derived from" in heads[t]["license"] else "")
        return [n for n in names if n != t and re.search(r"(?<![a-z0-9_])" + re.escape(n) + r"(?![a-z0-9_])", text)]

    def resolve(t, seen=()):
        if t in BY_HAND:
            return set(BY_HAND[t][0]), "by hand: " + BY_HAND[t][1]
        own = set(registry.get(t, set()))
        if not (own - OWN) and t.startswith("iso_") and grids_of[t]:
            return set(grids_of[t]), "the grids its coverage row lists (a table of several operators' own prices)"
        if not (own - OWN) and t.startswith("eia930_"):
            return {"EIA"}, "EIA-930 (its name; the registry lists no row for it)"
        ins = [i for i in inputs(t) if i not in seen]
        got = set(own)
        for i in ins:
            got |= resolve(i, seen + (t,))[0]
        how = "the source registry" if not ins else "the source registry and the tables its header derives it from: " + ", ".join(sorted(ins))
        if ins and grids_of[t]:
            got = {p for p in got if p not in GRIDS or p in grids_of[t]}       # the operators whose grid its own rows cover
        return got, how

    out = []
    for r in cov:
        got, how = resolve(r["table"])
        if r["table"] in NEWS_TABLES:      # a grid operator is here as the outlet of its own news releases; PJM's data agreement is not about those
            got = {"PJM (its news releases)" if p == "PJM" else p for p in got}
        pubs = sorted(got - OWN) or sorted(got & OWN) or ["ERW"]
        out.append((r["table"], pubs, how))
    return out


def worst(vs):
    return max(vs, key=ORDER.index) if vs else PUBLIC


def judge(pubs, verdicts, column="verdict"):
    """(verdict, deciding publishers, publishers not read) for one table."""
    if set(pubs) <= OWN:
        return PUBLIC, [], []
    read = {p: verdicts[p][column] for p in pubs if p in verdicts}
    unread = [p for p in pubs if p not in verdicts and p not in OWN]
    v = worst(list(read.values()))
    return v, sorted(p for p, x in read.items() if x == v and v != PUBLIC), unread


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ").strip()


def short(pubs, n=6):
    return "; ".join(pubs[:n]) + (f"; and {len(pubs) - n} more" if len(pubs) > n else "")


# Session 324 (the chain prompt of 19 October 2026): a table kept internal by the owner's ruling although the sentence
# read allows it, with the reason. The document says it is ruled, not open.
RULED_INTERNAL = {
    "portwatch_chokepoint_transits": "kept internal by the owner's default of 19 October 2026 (the morning note's item 12): the IMF's "
                                     "terms (read 13) prohibit bulk download of information by automated technology without explicit "
                                     "permission, and the table is the daily pull of PortWatch's series; commercial reuse needs "
                                     "copyright@imf.org's permission",
    # session 378: ERCOT's sentence allows it; the table is internal by the owner's rule for the hourly table (session 358)
    "ercot_node_prices_hourly": "kept internal by the owner's rule for the hourly table (its header, session 358: the storage "
                                "points' hourly prices kept in the warehouse, not in the live set, under 500,000 rows); "
                                "ERCOT's terms (read 2) would allow it",
}
STATUS = os.path.join(META, "license_status.csv")


def erw_verdict(flag, standing):
    """Session 378: one word a table. internal: flagged internal (by the ERW's choice or a ruling); public: flagged
    public and every publisher's sentence read allows it as the ERW is today; unsettled: anything else (a publisher not
    read, a "license needed" ruling waiting for a permission, a flag and a verdict that disagree)."""
    if flag != "public":
        return "internal"
    return "public" if standing == "agrees" else "unsettled"


def license_needed():
    """{table: from} of license_status.csv's "license needed" rows (session 207's ruling: the flag stays public, the
    table shows "license needed" from that day until a permission is recorded)."""
    if not os.path.exists(STATUS):
        return {}
    return {r["table"]: r["from"] for r in rows(STATUS) if r["status"] == "license needed" and not r.get("permission")}


def write(doc=None):
    cov = rows(COVERAGE)
    needed = license_needed()
    reads = rows(READS)
    verdicts = {r["key"]: r for r in rows(VERDICTS)}
    tables = {r["table"]: r for r in rows(TABLES)}
    by_n = {r["n"]: r for r in reads}
    L = []
    w = L.append
    lines = []      # (table, publishers, verdict, deciding, unread, flag, standing, if sold)
    for r in cov:
        pubs = [p for p in tables[r["table"]]["publishers"].split("; ") if p]
        v, why, unread = judge(pubs, verdicts)
        vc, whyc, _ = judge(pubs, verdicts, "if_commercial")
        own = set(pubs) <= OWN
        if own:
            standing = "agrees" if r["license"] == "public" else "internal by the ERW's own choice"
        elif unread and v == PUBLIC:
            standing = "not settled"
        elif (r["license"] == "public") == (v == PUBLIC):
            standing = "agrees"
        else:
            standing = "DISAGREES: the flag is looser" if r["license"] == "public" else "DISAGREES: the flag is stricter"
        # session 324: a disagreement a newer record settles is ruled, not open
        if standing == "DISAGREES: the flag is looser" and r["table"] in needed:
            standing = f"ruled: license needed from {needed[r['table']]}"
        if standing == "DISAGREES: the flag is stricter" and r["table"] in RULED_INTERNAL:
            standing = "ruled: kept internal"
        lines.append(dict(table=r["table"], pubs=pubs, v=v, why=why, unread=unread, flag=r["license"], standing=standing, vc=vc, whyc=whyc, own=own, rows=r["n_rows"]))
    n_ask = sum(1 for r in reads if not r["outcome"].startswith("not asked"))
    n_read = sum(1 for r in reads if r["outcome"] == "read")
    count = lambda s: sum(1 for x in lines if x["standing"].startswith(s))  # noqa: E731

    w("# Licenses: what each publisher's own page allows")
    w("")
    w("Energy Research Warehouse (ERW), session 205, 12 October 2026. Written by `scripts/licenses.py write` from three files in `warehouse/metadata/` "
      "(`license_reads.csv`, `license_verdicts.csv`, `license_tables.csv`) and `coverage.csv`. Do not edit this file by hand.")
    w("")
    w("- **What a verdict is.** A session read one page of each publisher, once, and took the sentence that allows or forbids redistribution. The verdict is that session's reading of the sentence. It is not legal advice, and no lawyer has read it.")
    w("- **Two verdicts a publisher.** \"As the ERW is today\": an open research project that sells nothing. \"If the ERW sells anything\": the same sentence read for a commercial product. They differ where a page allows noncommercial use only.")
    w("- **Nothing was changed in `coverage.csv`.** Where its flag and the verdict differ, the table is listed below and a person rules.")
    w("- **A publisher not read has no verdict.** A table that would otherwise be public is then \"not settled\", never public by default.")
    w("- **A quoted sentence is cut by code from the page as it was saved,** never typed. The pages themselves are a publisher's and stay on the data machine (`runs/license_reads/`).")
    w("")
    w("## Read these first")
    w("")
    w(f"- **{len(lines)} tables.** The flag and the verdict agree on {count('agrees')}; a ruling settles {count('ruled')} (session 324: "
      f"the \"license needed\" rows of `license_status.csv`, and {len(RULED_INTERNAL)} tables kept internal by a ruling); disagree on {count('DISAGREES')}; "
      f"{count('not settled')} are not settled (a publisher not read); {count('internal by')} is internal by the ERW's own choice.")
    ev = collections.Counter(erw_verdict(x["flag"], x["standing"]) for x in lines)
    w(f"- **The ERW's verdict (session 378): {ev['public']} public, {ev['internal']} internal, {ev['unsettled']} unsettled** "
      "(one word a table, in \"Every table\"; an unsettled table waits for a permission, a read, or a ruling).")
    w(f"- **{len(reads)} publishers in the record: {n_ask} requests (each sweep under its own ceiling: session 205, 40; sessions 307 and 308, one each; session 311, 60; session 388, 16 with its robots files; sessions 484, 493 and 496, one each), {n_read} pages read, {n_ask - n_read} that could not be read, "
      f"{len(reads) - n_ask} not asked (paused).**")
    loose = [x for x in lines if x["standing"] == "DISAGREES: the flag is looser"]
    strict = [x for x in lines if x["standing"] == "DISAGREES: the flag is stricter"]
    by = {}
    # session 324: the tables flagged public whose publisher asks for permission, open or settled as "license needed"
    asks = loose + [x for x in lines if x["standing"].startswith("ruled: license needed")]
    for x in asks:
        for p in x["why"]:
            by.setdefault(p, []).append(x["table"])
    w(f"- **{len(asks)} tables are flagged public where a publisher's sentence asks for permission or a license** ({len(asks) - len(loose)} of them settled as \"license needed\"). By the publisher that decides it (a table can be under several): "
      + "; ".join(f"{p} {len(t)}" for p, t in sorted(by.items(), key=lambda kv: -len(kv[1]))) + ".")
    w(f"- **{len(strict)} tables are flagged internal where the sentence read allows them" + (":** " + ", ".join(f"`{x['table']}`" for x in strict) + "." if strict else ".**"))
    change = [x for x in lines if x["v"] == PUBLIC and x["vc"] != PUBLIC and not x["own"]]
    byc = {}
    for x in change:
        for p in x["whyc"]:
            byc.setdefault(p, []).append(x["table"])
    w(f"- **{len(change)} tables that may be public today would need permission if the ERW sells anything** (" + "; ".join(f"{p} {len(t)}" for p, t in sorted(byc.items(), key=lambda kv: -len(kv[1]))) + ").")
    w("")
    w("## The reads")
    w("")
    w("One request a publisher, no second try. Times are UTC, 12 October 2026.")
    w("")
    w("| # | Publisher | Address asked | Time | Answer | Bytes | Outcome |")
    w("|---|---|---|---|---|---|---|")
    for r in reads:
        moved = f" (answered at {r['final_url']})" if r["final_url"] and r["final_url"].rstrip("/") != r["url"].rstrip("/") else ""
        w(f"| {r['n']} | {cell(r['publisher'])} | {r['url']}{moved} | {r['read_at'][11:19]} | {r['http_status'] or 'no request'} | {r['bytes'] or ''} | {cell(r['outcome'])} |")
    w("")
    w("## The publishers: the sentence and the verdict")
    w("")
    w("| Publisher | Read | The sentence taken from the page | As the ERW is today | If the ERW sells anything | Who to write to | Price | Note |")
    w("|---|---|---|---|---|---|---|---|")
    for k, v in verdicts.items():
        n = v["read"]
        ref = f"#{n}: {cell(by_n[n]['outcome']).split(' (')[0]}" if n else "no"
        s = f"\"{cell(v['sentence'])}\"" if v["sentence"] else "none"
        w(f"| {k} | {ref} | {s} | {v['verdict']} | {v['if_commercial']} | {cell(v['contact']) or 'not named'} | {cell(v['price']) or 'none stated'} | {cell(v['note'])} |")
    w("")
    unread_all = sorted({p for x in lines for p in x["unread"]})
    w(f"**Publishers no read of this sweep covers ({len(unread_all)}):** " + "; ".join(unread_all) + ".")
    w("")
    w("## Every table")
    w("")
    w("\"Decided by\" names the publisher whose sentence sets the verdict. A table of the ERW's own work has no publisher.")
    w("")
    w("\"ERW verdict\" (session 378) is one word a table: public (flagged public, and every publisher's sentence read allows it), internal "
      "(flagged internal), unsettled (a publisher not read, a \"license needed\" ruling waiting for its permission, or a flag and a verdict that disagree). "
      "A verdict that needs a document the ERW does not hold says so under \"Not read\"; such a table stays as it is flagged.")
    w("")
    w("| Table | Publishers | Verdict today | Decided by | Not read | Flag in coverage.csv | Flag and verdict | If the ERW sells anything | ERW verdict |")
    w("|---|---|---|---|---|---|---|---|---|")
    for x in lines:
        pubs = "the ERW's own work" if x["own"] else short(x["pubs"])
        v = x["v"] if not (x["unread"] and x["v"] == PUBLIC) else f"not settled ({PERMISSION} by default)"
        w(f"| `{x['table']}` | {cell(pubs)} | {v} | {cell(short(x['why'], 4)) or ''} | {cell(short(x['unread'], 3)) or ''} | {x['flag']} | {x['standing']} | {x['vc']} | {erw_verdict(x['flag'], x['standing'])} |")
    w("")
    ruled = [x for x in lines if x["standing"].startswith("ruled")]
    w("## Settled by a ruling (session 324)")
    w("")
    w("The flag and the verdict differ, and a newer record says what holds. A table flagged public whose publisher asks for "
      "permission keeps its flag by the owner's ruling of 12 October 2026 (session 207): from the day in "
      "`warehouse/metadata/license_status.csv` it shows \"license needed\" in place of its numbers until a permission is recorded "
      "in its row. The verdict is right about the clause; the flag is the table's place once permitted.")
    w("")
    for x in ruled:
        why = RULED_INTERNAL.get(x["table"]) or f"{x['v']}, by {short(x['why'], 8)}; license needed from {needed.get(x['table'], '')}"
        w(f"- `{x['table']}`: {why}.")
    w("")
    w("## Where the flag and the verdict disagree")
    w("")
    w("None of these was changed. Each is a ruling.")
    w("")
    w("### Flagged public; a publisher's sentence asks for permission or a license")
    w("")
    for x in loose:
        holds = f" The table holds {HOLDS[x['table']]}." if x["table"] in HOLDS else ""
        w(f"- `{x['table']}`: {x['v']}, by {short(x['why'], 8)}.{holds}")
    w("")
    w("### Flagged internal; the sentence read allows it")
    w("")
    for x in strict:
        w(f"- `{x['table']}`: {x['v']} ({short(x['pubs'], 4)}).")
    w("")
    w("### Not settled: a publisher was not read")
    w("")
    for x in lines:
        if x["standing"] == "not settled":
            w(f"- `{x['table']}` (flag {x['flag']}): not read: {short(x['unread'], 6)}.")
    w("")
    w("## Three lists")
    w("")
    pub_now = [x for x in lines if x["v"] == PUBLIC and x["flag"] == "public" and not (x["unread"] and not x["own"])]
    w(f"### Public now ({len(pub_now)} tables)")
    w("")
    w("The flag says public and every publisher's sentence read allows it, as the ERW is today.")
    w("")
    w(", ".join(f"`{x['table']}`" for x in pub_now) + ".")
    w("")
    w("### Permission needed")
    w("")
    w("By publisher: the tables its sentence decides, and who to write to where the page names someone.")
    w("")
    need = {}
    for x in lines:
        if x["v"] == PERMISSION:
            for p in x["why"]:
                need.setdefault(p, []).append(x["table"])
    for p, ts in sorted(need.items(), key=lambda kv: -len(kv[1])):
        w(f"- **{p}** ({len(ts)} tables). Write to: {verdicts[p]['contact'] or 'no person or address on the page read'}. Tables: " + ", ".join(f"`{t}`" for t in ts) + ".")
    later = {}
    for x in change:
        for p in x["whyc"]:
            if verdicts[p]["if_commercial"] == PERMISSION:
                later.setdefault(p, []).append(x["table"])
    if later:
        w("")
        w("Only if the ERW sells anything:")
        w("")
        for p, ts in sorted(later.items(), key=lambda kv: -len(kv[1])):
            w(f"- **{p}** ({len(ts)} tables). Write to: {verdicts[p]['contact'] or 'no person or address on the page read'}.")
    w("")
    w("### Paid")
    w("")
    paid = {}
    for x in lines:
        for p in x["pubs"]:
            if p in verdicts and PAID in (verdicts[p]["verdict"], verdicts[p]["if_commercial"]):
                paid.setdefault(p, []).append(x["table"])
    for p, ts in sorted(paid.items(), key=lambda kv: -len(kv[1])):
        when = "today" if verdicts[p]["verdict"] == PAID else "if the ERW sells anything"
        w(f"- **{p}** ({when}). Price: {verdicts[p]['price'] or 'none stated on the page read'}. Tables: " + ", ".join(f"`{t}`" for t in ts) + ".")
    w("")
    w("No page read states a price. For the letter of intent, a price has to be asked for.")
    w("")
    # session 505: the held figures a page still shows, one line a page, from docs/licenses_holds.csv (written by
    # site/scripts/check-holds.mjs --csv on a build); no file, no section. Before session 378's prices, which close the
    # document (tests/test_session378.py; session 555)
    if os.path.exists(HOLDS_SHOWN):
        shown = rows(HOLDS_SHOWN)
        day = shown[0]["day"] if shown else ""
        w("## Held figures that still show (session 505)")
        w("")
        w("A table held for a license is drawn as \"license needed\" (`site/lib/license.ts`, `components/Num.tsx`). "
          "`site/scripts/check-holds.mjs` reads every page of check-values' list on a build and lists each figure drawn from "
          "a held table without those words. How such a figure is held is Samuel's ruling; no page was changed. "
          + (f"Read on {day}: {len(shown)} pages." if shown else "Read: no page shows a held figure."))
        w("")
        for r in shown:
            grids = f", grids {r['grids']}" if r["grids"] else ""
            w(f"- `{r['page']}`: {r['figures']} held figures shown ({r['kinds']}), from `" + "`, `".join(r["tables"].split("; ")) + f"`{grids}.")
        w("")
    # session 378: the prices for the letter of intent, one row a publisher whose verdict is not "may be public" today or
    # if the ERW sells anything, with what its page says of a price and who to write to; the four letters are named
    letters = {"NYISO": "nyiso", "SPP": "spp", "PJM": "pjm", "MISO": "miso"}
    w("## The publishers' prices, for the letter of intent (session 378)")
    w("")
    w("What each page read says of a price, for every publisher whose sentence asks for permission or a license, today or "
      "if the ERW sells anything. A figure is written only where the page states one; none does. The four grid operators' "
      "letters are drafts under `docs/reviews/licenses/`, for Samuel to send.")
    w("")
    w("| Publisher | Today | If the ERW sells anything | Price, as the page states it | Who to write to | Letter |")
    w("|---|---|---|---|---|---|")
    for k, v in sorted(verdicts.items(), key=lambda kv: (kv[0] not in letters, kv[0].lower())):
        if v["verdict"] == PUBLIC and v["if_commercial"] == PUBLIC:
            continue
        letter = f"`docs/reviews/licenses/{letters[k]}-permission-letter.md`" if k in letters else ""
        w(f"| {k} | {v['verdict']} | {v['if_commercial']} | {cell(v['price']) or 'none stated'} | {cell(v['contact']) or 'not named'} | {letter} |")
    w("")
    text ="\n".join(L) + "\n"
    if chr(0x2014) in text:
        text = text.replace(chr(0x2014), ":")     # a publisher's own dash inside a quotation would break the house rule; none is expected
    with open(doc or DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return lines


# Session 207 (the owner's ruling of 12 October 2026): a license status for the tables flagged public whose publisher's
# sentence asks for permission or a license. From STATUS_FROM such a table shows "license needed" (as PJM's prices do)
# unless a permission is recorded in its row (the columns permission and permission_ref, filled by a person; the
# sentence of the permission, its date, who gave it). Nothing on the site changes before STATUS_FROM. The site reads
# site/data/license_status.json (site/lib/license.ts); the builders read the CSV (warehouse/metadata/license_status.py).
STATUS = os.path.join(META, "license_status.csv")
SITE_STATUS = os.path.join(ROOT, "site", "data", "license_status.json")
# Session 248: the public day moved from 20 to 21 October 2026 (Samuel's ruling of 12 October 2026, night;
# docs/roadmap.md), and this day moves with it. STATUS_WAS is the day the file was first written with.
STATUS_FROM = "2026-10-21"
STATUS_WAS = "2026-10-20"
STATUS_COLS = ["table", "status", "from", "publishers", "verdict", "permission", "permission_ref", "note"]
NEEDED, RECORDED = "license needed", "permission recorded"


def moved_day(prev):
    """The `from` day of a row on a rebuild (session 248). A row with no day, or with the day the file was first
    written with and no permission, takes the public day as it now stands. A row a person filled (a permission) keeps
    its own day, and so does a row whose day someone set to another one."""
    day = (prev or {}).get("from") or ""
    if not day or (day == STATUS_WAS and not (prev or {}).get("permission")):
        return STATUS_FROM
    return day


def status_lines():
    """(table, verdict, deciding publishers) for every table flagged public whose verdict asks for permission or a
    license: the "flag is looser" lines of write(), by the same judge."""
    verdicts = {r["key"]: r for r in rows(VERDICTS)}
    tables = {r["table"]: r for r in rows(TABLES)}
    out = []
    for r in rows(COVERAGE):
        pubs = [p for p in tables[r["table"]]["publishers"].split("; ") if p] if r["table"] in tables else []
        if not pubs or set(pubs) <= OWN:
            continue
        v, why, _ = judge(pubs, verdicts)
        if r["license"] == "public" and v != PUBLIC:
            out.append((r["table"], v, why))
    return out


def write_status(today=None):
    """warehouse/metadata/license_status.csv and site/data/license_status.json from the verdicts, keeping every permission
    a person recorded (a row is never dropped while it holds one). Returns the rows written."""
    import json
    kept = {r["table"]: r for r in rows(STATUS)} if os.path.exists(STATUS) else {}
    out = {}
    for table, v, why in status_lines():
        prev = kept.get(table, {})
        permission, ref = prev.get("permission", ""), prev.get("permission_ref", "")
        out[table] = {"table": table, "status": RECORDED if permission else NEEDED, "from": moved_day(prev),
                      "publishers": "; ".join(why), "verdict": v, "permission": permission, "permission_ref": ref,
                      "note": prev.get("note") or f"flagged public; the publisher's sentence read in session 205 asks for it (docs/licenses.md)"}
    for t, r in kept.items():  # a recorded permission is kept even when the verdict no longer asks for one
        if r.get("permission") and t not in out:
            out[t] = {c: r.get(c, "") for c in STATUS_COLS}
    with open(STATUS, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=STATUS_COLS, lineterminator="\n")
        wr.writeheader()
        for t in sorted(out):
            wr.writerow(out[t])
    site = {"from": STATUS_FROM, "written": (today or dt.datetime.now(dt.timezone.utc).date().isoformat()),
            "what": f"Tables flagged public whose publisher's own page asks for permission or a license (docs/licenses.md). From {STATUS_FROM} "
                    f"a table with status '{NEEDED}' shows 'license needed' on the site unless a permission is recorded (warehouse/metadata/license_status.csv).",
            "tables": {t: {"status": r["status"], "from": r["from"], "publishers": [p for p in r["publishers"].split("; ") if p]} for t, r in sorted(out.items())}}
    os.makedirs(os.path.dirname(SITE_STATUS), exist_ok=True)
    with open(SITE_STATUS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(site, f, indent=1)
        f.write("\n")
    return list(out.values())


def check():
    cov = {r["table"] for r in rows(COVERAGE)}
    tables = {r["table"]: r for r in rows(TABLES)}
    verdicts = {r["key"]: r for r in rows(VERDICTS)}
    reads = rows(READS)
    bad = [f"table not in license_tables.csv: {t}" for t in sorted(cov - set(tables))]
    bad += [f"table of license_tables.csv not in coverage.csv: {t}" for t in sorted(set(tables) - cov)]
    numbers = {r["n"] for r in reads}
    for k, v in verdicts.items():
        if v["verdict"] not in ORDER or v["if_commercial"] not in ORDER:
            bad.append(f"{k}: a verdict that is not one of the four")
        if v["read"] and v["read"] not in numbers:
            bad.append(f"{k}: read {v['read']} is not in license_reads.csv")
        if v["sentence"] and not v["read"]:
            bad.append(f"{k}: a sentence with no read behind it")
    asked = sum(1 for r in reads if not r["outcome"].startswith("not asked"))
    for line in bad:
        print(line)
    print(f"{len(cov)} tables, {len(verdicts)} publishers with a verdict, {asked} requests in the record; {len(bad)} problems")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="docs/licenses.md: what each publisher's own page allows (session 205)")
    ap.add_argument("what", choices=["tables", "write", "check", "status", "state"])
    ap.add_argument("--headers", help="tables: the folder of the tables themselves (warehouse/output of a data machine)")
    ap.add_argument("--branch", default="", help="state: the branch whose page code is read, for the document's first paragraph")
    a = ap.parse_args(argv)
    if a.what in ("status", "state"):  # session 207; session 248: the license table for the public day follows
        import license_state  # scripts/license_state.py: every table's status and the pages it darkens
        if a.what == "status":
            out = write_status()
            n = sum(1 for r in out if r["status"] == NEEDED)
            print(f"{os.path.relpath(STATUS, ROOT)} and {os.path.relpath(SITE_STATUS, ROOT)}: {len(out)} tables, {n} '{NEEDED}' from {STATUS_FROM}, "
                  f"{len(out) - n} with a permission recorded")
        # the status file's rebuild writes the site's file without its two keys "all" and "pages": they are written again here
        return license_state.write(day=STATUS_FROM, branch=a.branch)
    if a.what == "tables":
        if not a.headers or not os.path.isdir(a.headers):
            ap.error("tables needs --headers, the folder that holds the tables")
        out = build_tables(a.headers)
        with open(TABLES, "w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f, lineterminator="\n")
            wr.writerow(["table", "publishers", "how"])
            for t, pubs, how in out:
                wr.writerow([t, "; ".join(pubs), how])
        print(f"{os.path.relpath(TABLES, ROOT)}: {len(out)} tables")
        return 0
    if a.what == "write":
        lines = write()
        print(f"docs/licenses.md: {len(lines)} tables")
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
