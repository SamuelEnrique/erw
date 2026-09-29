#!/usr/bin/env python3
"""Seed the company database (platform tool 10) from the deal tracker's counterparties.

Energy Research Warehouse (ERW), session 27 (human ruling on session 26). For every buyer, seller and other party in
energy_deals (warehouse/deals/extract.py), create or merge one row of energy_companies (the table the Thesis Builder,
warehouse/thesis/build.py, started in session 25):

    name          the party as the deal names it (the most frequent spelling across its deals)
    sector        the sector of its deals: the news scorer's sector of the stories each deal was extracted from
                  (news_stories), all of them, ";"-separated
    niche_tags    "deal:<deal_type>" and "tech:<technology>" for each of its deals
    location      the place a deal states (its state or country), only where one is stated; it is where the deal is,
                  not necessarily where the company is based, and the table says so
    sources       the deals' story links
    confidence    the Thesis Builder's rule (warehouse/thesis/build.py confidence()): 20 per independent source, up to 3,
                  plus 20 or 10 for recency; a deal-only row has no primary confirmation of stage or raised, so it starts at
                  the source count and recency
    first_seen    the date of its first deal
    description, founders, stage, raised: blank; the confidence note starts "from deals; not yet researched" (nothing is
                  invented: the deals state none of these)

Session 28 (human ruling): a party that is not a company name is left out of energy_companies; it stays in
energy_deals as the deal states it. A party naming several companies ("Nvidia, Amazon and Microsoft") is split into
them. Left out, by not_a_company(): descriptions ("bond investors", "a Leading Frontier AI Lab", "German firm",
"Amazon data center unit", "Meta-backed data centre"), governments, countries and public bodies ("US government",
"DOE", "Qatar"), laws ("CHIPS Act") and universities. Every party left out is named in the run log with its reason,
and counted in the header.

Merge rule: two rows are one company when their normalized names match (lower case, no punctuation, no legal suffix
such as Inc, LLC, Corp) and, when both have a website, their website domains match. A row the Thesis Builder researched
keeps its description, founders, stage, raised, confidence and note; it gains the deal sources and tags. Deal-only rows
are rebuilt from energy_deals on every run, so the step is idempotent.

    python warehouse/companies/seed_from_deals.py
"""

import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "thesis"))
import iso_prices as ip  # noqa: E402
from build import ENT_COLS, company_id, confidence, domain, name_key  # noqa: E402

NAME = "energy_companies"
DEAL_NOTE = "from deals; not yet researched"


# Session 28: parties that are not company names (see the module docstring)
COUNTRIES = {
    "afghanistan", "albania", "algeria", "angola", "argentina", "armenia", "australia", "austria", "azerbaijan",
    "bahrain", "bangladesh", "belarus", "belgium", "bolivia", "bosnia", "botswana", "brazil", "brunei", "bulgaria",
    "cambodia", "cameroon", "canada", "chad", "chile", "china", "colombia", "congo", "costa rica", "croatia", "cuba",
    "cyprus", "czech republic", "czechia", "denmark", "ecuador", "egypt", "estonia", "ethiopia", "eu", "european union",
    "finland", "france", "gabon", "georgia", "germany", "ghana", "greece", "guatemala", "guyana", "hungary", "iceland",
    "india", "indonesia", "iran", "iraq", "ireland", "israel", "italy", "ivory coast", "jamaica", "japan", "jordan",
    "kazakhstan", "kenya", "korea", "south korea", "north korea", "kuwait", "kyrgyzstan", "latvia", "lebanon", "libya",
    "lithuania", "luxembourg", "malaysia", "mali", "malta", "mauritania", "mexico", "moldova", "mongolia", "montenegro",
    "morocco", "mozambique", "myanmar", "namibia", "nepal", "netherlands", "new zealand", "nicaragua", "niger",
    "nigeria", "norway", "oman", "pakistan", "panama", "paraguay", "peru", "philippines", "poland", "portugal", "qatar",
    "romania", "russia", "rwanda", "saudi arabia", "senegal", "serbia", "singapore", "slovakia", "slovenia", "somalia",
    "south africa", "spain", "sri lanka", "sudan", "suriname", "sweden", "switzerland", "syria", "taiwan",
    "tajikistan", "tanzania", "thailand", "trinidad and tobago", "tunisia", "turkey", "turkiye", "turkmenistan",
    "uae", "united arab emirates", "uganda", "uk", "united kingdom", "britain", "great britain", "ukraine", "uruguay",
    "us", "u.s.", "usa", "united states", "uzbekistan", "venezuela", "vietnam", "yemen", "zambia", "zimbabwe",
}
PUBLIC_BODIES = {"doe", "pentagon", "white house", "congress", "treasury", "fed", "federal reserve", "nrc", "ferc",
                 "epa", "blm", "british nuclear fund"}
GENERIC_WORDS = {"investors", "investor", "lenders", "lender", "allies", "banks", "buyers", "sellers", "shareholders",
                 "owners", "customers", "developers", "operators", "utilities", "governments"}
GENERIC_END = re.compile(r"(?i)\b(firms?|investors?|hyperscalers?|startups?|joint venture|jv|refinery|refineries|"
                         r"banks?|lenders?|unit|subsidiary|vehicle|project|consortium|data cent(?:er|re)s?)$")


def not_a_company(name):
    """Why a deal party is not a company name, or None when it is one (session 28 ruling)."""
    n = name.strip()
    low = n.lower().rstrip(".")
    if low in COUNTRIES:
        return "a country"
    if low in PUBLIC_BODIES or re.match(r"(?i)^(us|u\.s\.|uk|eu)\s+(government|army|navy|air force|exim|treasury|"
                                         r"department|military)\b", n) or re.search(r"(?i)\bgovernment\b", n):
        return "a government or public body"
    if re.search(r"\bAct$", n):
        return "a law"
    if re.search(r"(?i)\buniversity\b", n):
        return "a university"
    if low in GENERIC_WORDS or re.match(r"(?i)^(a|an|the|one|two|several|some|various|unnamed|undisclosed|unidentified|"
                                         r"other|multiple)\s", n):
        return "a description"
    if " " in n and n[:1].islower():
        return "a description"
    if re.search(r"(?i)-(owned|backed|tied|linked)\b|\bdata cent(?:er|re)s?\b", n) or GENERIC_END.search(n):
        return "a description"
    return None


def split_names(raw):
    """A party naming several companies, "A, B and C", as its names; any other party as itself."""
    raw = raw.strip()
    if not raw:
        return []
    if raw.lower().rstrip(".") in COUNTRIES:  # "Trinidad and Tobago" is one name
        return [raw]
    parts = [x.strip() for x in re.split(r",\s*|\s+and\s+", raw) if x.strip()]
    if len(parts) > 1 and all(x[:1].isupper() or x[:1].isdigit() for x in parts):
        return parts
    return [raw]


def key(name):
    """The same normalization as the site's /companies anchors (site/lib/companies.ts companyKey) and the Thesis
    Builder's merge (build.name_key)."""
    return name_key(name)


def fold_researched(df, log):
    """Researched rows that are one company (the same normalized name, and the same website domain or one of them
    without a website) are folded into one: the fields of the higher-confidence row, the sources and niche tags of both,
    the earlier first_seen (session 27: two runs had written "Tyba" and "Tyba (Tyba Energy Inc.)")."""
    df = df.assign(_k=df["name"].map(key), _c=pd.to_numeric(df["confidence"], errors="coerce").fillna(0))
    keep, drop = [], set()
    for k, g in df.groupby("_k", sort=False):
        g = g.sort_values("_c", ascending=False)
        doms = {domain(w) for w in g["website"] if domain(w)}
        if len(g) == 1 or len(doms) > 1:
            keep += list(g.index)
            continue
        top = g.index[0]
        df.at[top, "sources"] = ";".join(dict.fromkeys(u for s in g["sources"] for u in s.split(";") if u))
        df.at[top, "niche_tags"] = ";".join(sorted({t for s in g["niche_tags"] for t in s.split(";") if t}))
        df.at[top, "first_seen"] = min(x for x in g["first_seen"] if x)
        if not df.at[top, "website"] or df.at[top, "website"] == "not disclosed":
            df.at[top, "website"] = next((w for w in g["website"] if domain(w)), df.at[top, "website"])
        keep.append(top)
        drop |= set(g.index[1:])
        log(f"  folded {len(g) - 1} researched row(s) into {df.at[top, 'name']!r}: {list(g['name'][1:])}")
    return df.loc[[i for i in keep if i not in drop]].drop(columns=["_k", "_c"])


def read(name):
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        skip = sum(1 for ln in f if ln.startswith("#"))
    return pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False)


def header(run_id, n_thesis, n_deals, n_left_out=0):
    return [
        "Energy Research Warehouse (ERW): energy companies, the company database (tool 10): companies the Thesis Builder "
        "(tool 27) researched, and every party of the deal tracker's deals (energy_deals)",
        "Shape: entities (docs/datastandard.md v0), entity_type company; one row per company, merged on normalized name "
        "plus website domain when both are known. Thesis Builder rows: the model's fields from public web sources it cites "
        "(a number no cited source confirmed reads not confirmed; a public company's raised is blank). Deal rows (session "
        "27): name, the sector and niche tags of the deals, a location only where a deal states one (where the deal is), the "
        "deals' story links; description, founders, stage and raised are blank and the confidence_note starts \"from "
        "deals; not yet researched\". confidence 0 to 100 by the rule in warehouse/thesis/build.py, explained in "
        "confidence_note. No licensed data.",
        f"Rows: {n_thesis} researched by the Thesis Builder, {n_deals} from deals only. Session 28 ruling: "
        f"{n_left_out} deal parties that are not company names (descriptions, governments, countries, laws, "
        "universities) are left out, and stay in energy_deals; a party naming several companies is split into them.",
        f"Retrieved: {run_id} (UTC) by warehouse/companies/seed_from_deals.py (deal rows) and warehouse/thesis/build.py "
        "(researched rows)",
        f"Run log: warehouse/output/logs/companies_from_deals_{run_id}.log",
        "Source: erw:thesis_builder (public web sources, each row's sources column); erw:energy_deals (the deals' stories).",
        "License: public (names, one-line descriptions written by the ERW, and links).",
    ]


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"companies_from_deals_{run_id}.log"))
    status = dict(table=NAME, market="deals", status="ok", detail="")
    try:
        deals = read("energy_deals")
        if deals is None:
            raise RuntimeError("energy_deals is not on this machine")
        old = read(NAME)
        old = old if old is not None else pd.DataFrame(columns=ENT_COLS)
        before, before_desc = len(old), int((old["description"].str.strip() != "").sum()) if len(old) else 0
        researched = old[~old["confidence_note"].str.startswith(DEAL_NOTE)].copy()  # deal-only rows are rebuilt
        researched = fold_researched(researched.reset_index(drop=True), log).reset_index(drop=True)
        stories = read("news_stories")
        sector_of = dict(zip(stories["event_id"], stories["sector"])) if stories is not None else {}

        parties, left_out = {}, {}
        for d in deals.to_dict("records"):
            raw = [d["buyer"], d["seller"]] + d["other_parties"].split(";")
            names = []
            for r in raw:  # session 28: lists split, parties that are not company names left out
                for n in split_names(r):
                    why = not_a_company(n)
                    if why:
                        left_out.setdefault(n, why)
                    else:
                        names.append(n)
            sectors = [sector_of.get(s, "") for s in d["story_ids"].split(";") if s]
            place = ", ".join(x for x in (d.get("state", ""), d.get("country", "")) if x)
            urls = [u for u in d["story_urls"].split(";") if u]
            date = d["event_date"][:10]
            for n in names:
                n = n.strip()
                k = key(n)
                if not k:
                    continue
                p = parties.setdefault(k, {"names": {}, "sectors": set(), "tags": set(), "places": set(), "urls": [],
                                           "dates": [], "deals": set()})
                p["names"][n] = p["names"].get(n, 0) + 1
                p["sectors"].update(s for s in sectors if s)
                p["tags"].add(f"deal:{d['deal_type']}" if d["deal_type"] else "deal")
                if d.get("technology"):
                    p["tags"].add(f"tech:{d['technology']}")
                if place:
                    p["places"].add(place)
                p["urls"] += [u for u in urls if u not in p["urls"]]
                p["dates"].append(date)
                p["deals"].add(d["event_id"])
        log(f"{len(deals)} deals, {len(parties)} distinct parties (normalized names)")
        log(f"{len(left_out)} parties left out as not company names (they stay in energy_deals):")
        for n, why in sorted(left_out.items(), key=lambda x: (x[1], x[0].lower())):
            log(f"  {why}: {n}")

        rkeys = {}
        for i, r in researched.iterrows():
            rkeys.setdefault(key(r["name"]), []).append(i)
        new_rows, merged = [], 0
        now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for k, p in parties.items():
            hits = rkeys.get(k, [])  # deals state no website, so a normalized name match is the merge
            if hits:
                for i in hits:  # a researched company gains the deal sources, tags and an earlier first_seen
                    researched.at[i, "sources"] = ";".join(dict.fromkeys(filter(None, researched.at[i, "sources"].split(";") + p["urls"])))
                    researched.at[i, "niche_tags"] = ";".join(sorted(set(filter(None, researched.at[i, "niche_tags"].split(";"))) | p["tags"]))
                    researched.at[i, "first_seen"] = min(researched.at[i, "first_seen"] or "9999", min(p["dates"]))
                merged += 1
                continue
            name = max(p["names"].items(), key=lambda x: (x[1], -len(x[0])))[0]
            n_src = len({domain(u) or u for u in p["urls"]})
            latest = max(p["dates"])[:4]
            score, clause = confidence({"independent_sources": n_src, "sources": p["urls"], "latest_source_year": latest,
                                        "stage_primary": False, "raised_primary": False})
            clause = clause.replace("; stage not confirmed and raised not confirmed by a primary source",
                                    "; stage and raised not researched")
            new_rows.append({
                "entity_id": company_id(name, ""), "entity_type": "company", "name": name, "geo": "", "lat": "", "lon": "",
                "capacity_mw": "", "status": "", "status_date": "", "operator": "", "source": "erw:energy_deals",
                "source_url": p["urls"][0] if p["urls"] else "", "retrieved_at": now, "vintage": run_id,
                "description": "", "sector": ";".join(sorted(p["sectors"])), "niche_tags": ";".join(sorted(p["tags"])),
                "stage": "", "raised": "", "location": "; ".join(sorted(p["places"])), "founders": "", "website": "",
                "sources": ";".join(p["urls"]), "confidence": str(score),
                "confidence_note": f"{DEAL_NOTE}; {len(p['deals'])} deal{'s' if len(p['deals']) != 1 else ''}, {clause}"
                                   + ("; location is where a deal is" if p["places"] else ""),
                "first_seen": min(p["dates"])})
        out = pd.concat([researched, pd.DataFrame(new_rows, columns=ENT_COLS)], ignore_index=True)[ENT_COLS]
        out = out[out["source_url"] != ""]
        dup = out["entity_id"].duplicated(keep="first")
        if dup.any():
            log(f"  {int(dup.sum())} rows share an entity_id with an earlier row and were folded into it")
            out = out[~dup]
        out = out.sort_values("entity_id")
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            for ln in header(run_id, len(researched), len(out) - len(researched), len(left_out)):
                f.write("# " + ln + "\n")
            out.to_csv(f, index=False, lineterminator="\n")
        os.replace(tmp, path)
        ip.update_sources([dict(source="erw:energy_deals", publisher="Energy Research Warehouse (ERW)",
                                report="Deal tracker counterparties (energy_deals, warehouse/deals/extract.py)",
                                report_url="https://github.com/SamuelEnrique/erw/blob/main/warehouse/companies/seed_from_deals.py",
                                document_list="", license="public", tables=[NAME])])
        desc = int((out["description"].str.strip() != "").sum())
        status["detail"] = (f"{before} rows before ({before_desc} with a description), {len(out)} after ({desc} with a "
                            f"description, {100 * desc / max(1, len(out)):.1f}%); {len(new_rows)} deal-only rows, "
                            f"{merged} deal parties merged into researched rows; {len(left_out)} parties left out as "
                            "not company names")
        log(status["detail"])
        print(f"companies_from_deals: {status['detail']}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"companies_from_deals FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        status.update(status="failed", detail=tb.strip().splitlines()[-1][:300])
    ip.write_status("companies_from_deals", run_id, [status])
    log.close()
    return 0 if status["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
