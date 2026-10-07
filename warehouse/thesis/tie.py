#!/usr/bin/env python3
"""The tie of a company to a trend, as a rule in code (session 142). INTERNAL: nothing here is sent to a reader.

Energy Research Warehouse (ERW), Thesis Builder. Until session 142 a model judged whether "a source ties a company to
a trend", and the same niche gave 8, 12 and 9 companies in three runs. This module replaces that judgement. It is
pure: no model call, no network, no warehouse import. Given the same saved evidence it returns the same landscape in
the same order, and every point it gives is traceable to one saved sentence and its address.

THE RULE

1. The order of evidence. A sentence about a company comes from one of three tiers, read in this order:
     warehouse   the warehouse's own tables: the company's row of energy_companies (its description and tags) and
                 the rows of energy_deals that name it. Read fresh from the tables at every run.
     fetched     text the run holds from a source it fetched: the title of a search result, and any passage the
                 search tool returned as cited, when that text names the company. Also a reported sentence (below)
                 that is found word for word in the held text of its source.
     web         a sentence the research reported from a web page, with the page's address, that the run does not
                 hold as fetched text.
   A text "names the company" when it holds the company's whole normalized name, or its core name (the name without
   trailing generic words such as Energy or Technologies). A name or core name of one word must have four letters
   or more and the text must also hold a word of the niche's own name.

2. A trend's own terms. From the trend's title and its search phrases: every word of four letters or more, and
   every word written in capitals of two letters or more (AI, DAS, DOE), lower case, a final "s" dropped, without
   the stop words (a fixed list, with a few words too general to tell one trend from another: system, method,
   public, high) and without the words of the niche's own name. A trend's phrases are its search phrases. A term
   that is a word of the company's own name is not counted for that company ("Resources" in a company's name is not
   evidence of resource characterization).

3. The scoring. A sentence SUPPORTS a trend when it holds MIN_TERMS (2) or more distinct terms of the trend, or
   every word of one of the trend's phrases. A supporting sentence is worth its tier's points (warehouse 3, fetched
   2, web 1) plus STRONG_POINT (1) when it is strong: it holds a whole phrase, or STRONG_TERMS (3) or more distinct
   terms. A company's score for a trend is the sum, over at most MAX_ADDRESSES (3) addresses, of the best supporting
   sentence of each address (highest first). One sentence counts once however many addresses carry it: the same
   words on two pages are one piece of evidence (the third run of 7 October 2026 found one press release sentence on
   two pages of one university). The company is TIED to the trend when that score is TIE_MIN (2) or more: one
   warehouse sentence, one fetched sentence, one strong web sentence, or two different web sentences from two
   addresses.

4. The tie-break. Companies are ordered by their total score over the trends they are tied to (highest first), then
   by their best evidence tier (warehouse before fetched before web), then by their normalized name (a to z).

5. Duplicate names. Two names are one company when their core names are equal, or when the core name of one is the
   leading words of the other's ("Eden" and "Eden GeoPower") and their website domains do not differ. A short name
   that leads two or more longer names that are not themselves one company is ambiguous and is merged with none.
   The company keeps its longest name (most words, then most letters, then a to z).

6. What is saved. The evidence store of a niche (one JSON file) keeps every fetched source by address with the hash
   of its text and the date fetched, every reported sentence with its address, and every row a run wrote about a
   company. A run reads what is saved plus what it newly fetched, so a run differs from the one before only because
   a source was added, changed or disappeared, and diff() says which, by company and source. A company's facts
   (kind, country, location, stage fit) and its descriptive cells are the first values saved for it: a fact not yet
   stated can be filled by a later run, with that run's sources, and a later run that reads a stated fact
   differently changes nothing; its reading is kept in the run's record as a disagreement for a person to rule on.
   (The first version of this rule let the value with the most sources win. The second run of 7 October 2026 then
   moved a company because the model called a university spinout a university: an opinion, not a source.)
"""

import hashlib
import json
import os
import re

TIERS = {"warehouse": 3, "fetched": 2, "web": 1}
TIER_ORDER = ["warehouse", "fetched", "web"]
STRONG_POINT = 1
STRONG_TERMS = 3
MIN_TERMS = 2
TIE_MIN = 2
MAX_ADDRESSES = 3
STOP = {"the", "and", "for", "with", "from", "that", "this", "into", "their", "new", "not", "general", "only", "based", "using",
        "technologie", "technology", "companie", "company", "startup", "market", "energy", "power",
        "system", "method", "public", "high"}
GENERIC = {"energy", "power", "technologies", "technology", "systems", "international", "resources", "minerals", "partners",
           "labs", "group", "solutions", "services", "company", "industries"}
BLANK = {"", "not stated", "not disclosed", "unknown", "n/a", "none", "undisclosed"}
FACTS = ("kind", "country", "location", "fits_stage")
CELLS = ("website", "description", "founders", "stage", "raised", "signal", "tam")


# ---------------------------------------------------------------------------------------------
# words and names
# ---------------------------------------------------------------------------------------------

def fold(w):
    """A word as the rule compares it: a final "s" dropped from a word of four letters or more (not "ss")."""
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def words(text):
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def tokens(text):
    return [fold(w) for w in words(text)]


def head_of(niche):
    """The niche's own name: the words before its first comma, colon or bracket (as run.head_of)."""
    return re.split(r"[,:;(]", niche or "", maxsplit=1)[0].strip()


def name_key(name):
    """A company name for merging: the same normalization as build.name_key."""
    s = re.sub(r"\(.*?\)", " ", (name or "").lower())
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(inc|llc|ltd|corp|corporation|co|plc|lp|sa|ag|gmbh|limited|holdings)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def domain(url):
    m = re.match(r"(?:https?://)?(?:www\.)?([a-z0-9.-]+\.[a-z]{2,})", (url or "").strip().lower())
    return m.group(1) if m else ""


def sha(text):
    return hashlib.sha256(re.sub(r"\s+", " ", text or "").strip().encode("utf-8")).hexdigest()[:16]


def core_of(key, niche_words=()):
    """The name without its trailing generic words; never cut down to generic words only."""
    generic = GENERIC | set(niche_words)
    w = key.split()
    while len(w) > 1 and w[-1] in generic and not all(x in generic for x in w[:-1]):
        w = w[:-1]
    return " ".join(w)


def trend_terms(niche, trend):
    """(terms, phrases) of one trend: the terms in the order they are written, each phrase as its folded words."""
    head = set(tokens(head_of(niche)))
    phrases_raw = [p.strip() for p in (trend.get("search_phrases") or []) if p and p.strip()]
    terms = []
    for w in re.findall(r"[A-Za-z0-9]+", " ".join([trend.get("title", "")] + phrases_raw)):
        f = fold(w.lower())
        if f in head or f in STOP or f in terms:
            continue
        if len(w) >= 4 or (len(w) >= 2 and w.isupper()):
            terms.append(f)
    phrases = [(p, tokens(p)) for p in phrases_raw if len(tokens(p)) >= 2]
    return terms, phrases


def support(text, terms, phrases, own=()):
    """(matched terms, the phrase held or "") of one sentence for one trend. own: the words of the company's own
    name, which are not counted as terms for it."""
    have = set(tokens(text))
    matched = [t for t in terms if t in have and t not in own]
    phrase = next((p for p, toks in phrases if all(t in have for t in toks)), "")
    return matched, phrase


def names_it(text, aliases, niche_words):
    """True when the text names the company: (full name, core name) pairs, as rule 1 says."""
    t = " " + " ".join(words(text)) + " "
    in_niche = any(f" {w} " in t for w in niche_words)
    for full, core in aliases:
        for n in (full, core):
            if not n or f" {n} " not in t:
                continue
            if " " in n or (len(n) >= 4 and in_niche):
                return True
    return False


# ---------------------------------------------------------------------------------------------
# duplicate names
# ---------------------------------------------------------------------------------------------

def clusters(names, niche_words=()):
    """names: [(name, website)]. Returns {raw key: (canonical key, canonical name)}; the same for any input order."""
    by_key = {}
    for name, site in names:
        k = name_key(name)
        if not k:
            continue
        e = by_key.setdefault(k, {"names": set(), "domains": set()})
        e["names"].add(re.sub(r"\s+", " ", name).strip())
        if domain(site):
            e["domains"].add(domain(site))
    keys = sorted(by_key)
    core = {k: core_of(k, niche_words) for k in keys}
    parent = {k: k for k in keys}

    def find(k):
        while parent[k] != k:
            k = parent[k]
        return k

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for a in keys:                                   # equal core names
        for b in keys:
            if a < b and core[a] == core[b]:
                union(a, b)
    cores = sorted(set(core.values()))

    def doms(c):
        return set().union(*[by_key[k]["domains"] for k in keys if core[k] == c])

    for a in cores:                                  # a short name leading longer ones
        aw = a.split()
        longer = [b for b in cores if b != a and b.split()[:len(aw)] == aw]
        if not longer:
            continue
        chain = all(x.split()[:len(y.split())] == y.split() or y.split()[:len(x.split())] == x.split() for x in longer for y in longer)
        if not chain:
            continue                                 # ambiguous: merged with none
        for b in longer:
            da, db = doms(a), doms(b)
            if da and db and not (da & db):
                continue
            union(next(k for k in keys if core[k] == a), next(k for k in keys if core[k] == b))
    out = {}
    for root in sorted({find(k) for k in keys}):
        members = [k for k in keys if find(k) == root]
        all_names = sorted({n for k in members for n in by_key[k]["names"]}, key=lambda n: (-len(name_key(n).split()), -len(n), n))
        canon = all_names[0]
        for k in members:
            out[k] = (name_key(canon), canon)
    return out


# ---------------------------------------------------------------------------------------------
# the evidence store of one niche
# ---------------------------------------------------------------------------------------------

def empty_store(niche="", stage="", geography=""):
    return {"version": 1, "niche": niche, "stage": stage, "geography": geography, "runs": [], "sources": {}, "quotes": [],
            "rows": [], "last": None}


def load_store(path, niche="", stage="", geography=""):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return empty_store(niche, stage, geography)


def save_store(store, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=1, sort_keys=True, default=str)
    os.replace(tmp, path)


def source_text(s):
    return " | ".join([s.get("title", "")] + list(s.get("cited") or []))


def add_run(store, run_id, date, sources, orgs):
    """Add one run's fetched sources and rows to the store. sources: [{url, title, cited, page_age, retrieved}];
    orgs: the rows as structured, each with source_urls (addresses) and evidence [{quote, address}]. Returns the list
    of fetched addresses whose text changed since it was saved."""
    seq = len(store["runs"]) + 1
    changed = []
    for s in sources:
        url = s.get("url")
        if not url:
            continue
        h = sha(source_text(s))
        old = store["sources"].get(url)
        if old is None:
            store["sources"][url] = {"title": s.get("title", ""), "cited": list(s.get("cited") or []), "page_age": s.get("page_age", ""),
                                     "fetched": s.get("retrieved") or date, "sha": h, "first_run": run_id, "last_run": run_id, "history": []}
        else:
            if old["sha"] != h and (s.get("title") or s.get("cited")):
                old["history"].append({"sha": old["sha"], "title": old["title"], "until_run": run_id})
                old.update(title=s.get("title", ""), cited=list(s.get("cited") or []), sha=h, fetched=s.get("retrieved") or date)
                changed.append(url)
            old["last_run"] = run_id
    have = {(q["key"], q["address"], q["sha"]) for q in store["quotes"]}
    for o in orgs:
        k = name_key(o.get("name", ""))
        if not k:
            continue
        row = {f: o.get(f) for f in ("name",) + FACTS + CELLS + ("found_by", "latest_source_year", "stage_primary", "raised_primary", "trends")}
        row["source_urls"] = sorted(set(o.get("source_urls") or []))
        store["rows"].append({"key": k, "run_id": run_id, "seq": seq, "row": row})
        for q in o.get("evidence") or []:
            text = re.sub(r"\s+", " ", (q.get("quote") or "")).strip().strip('"').strip()
            addr = q.get("address") or ""
            if len(text) < 12 or not addr:
                continue                              # no address, or too short to be a sentence: not evidence
            ident = (k, addr, sha(text))
            if ident in have:
                continue
            have.add(ident)
            store["quotes"].append({"key": k, "address": addr, "text": text, "sha": sha(text), "fetched": date, "first_run": run_id})
    store["runs"].append({"run_id": run_id, "date": date, "seq": seq})
    return changed


def resolve(rows):
    """One row for a company from every saved row of it (rule 6): the first value saved stands. rows: the store's
    entries, any order. The row's "disagreements" lists every later reading of a fact that differs."""
    rows = sorted(rows, key=lambda x: (x["seq"], x["key"]))
    out = {"disagreements": [], "stated_by": {}}
    for f in FACTS:
        stated = [(x["run_id"], str(x["row"].get(f)).strip()) for x in rows if str(x["row"].get(f) or "").strip().lower() not in BLANK]
        out[f] = stated[0][1] if stated else ("not stated" if f != "kind" else "other")
        first = next((x for x in rows if str(x["row"].get(f) or "").strip().lower() not in BLANK), None)
        if first is not None:
            out["stated_by"][f] = {"run_id": first["run_id"], "sources": list(first["row"].get("source_urls") or [])}
        seen = {out[f].lower()}
        for run_id, v in stated:
            if v.lower() not in seen:
                seen.add(v.lower())
                out["disagreements"].append({"field": f, "kept": out[f], "said": v, "run_id": run_id})
    for f in CELLS:
        out[f] = next((str(x["row"].get(f)).strip() for x in rows if str(x["row"].get(f) or "").strip().lower() not in BLANK), "")
    found_by, urls, years = [], [], []
    for x in rows:
        for q in x["row"].get("found_by") or []:
            if q not in found_by:
                found_by.append(q)
        urls += [u for u in x["row"].get("source_urls") or [] if u not in urls]
        y = str(x["row"].get("latest_source_year") or "")[:4]
        if y.isdigit():
            years.append(y)
    out.update(found_by=found_by, source_urls=urls, latest_source_year=max(years) if years else "",
               stage_primary=any(bool(x["row"].get("stage_primary")) for x in rows),
               raised_primary=any(bool(x["row"].get("raised_primary")) for x in rows))
    return out


# ---------------------------------------------------------------------------------------------
# the judgement
# ---------------------------------------------------------------------------------------------

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"])", re.sub(r"\s+", " ", text or "")) if len(s.strip()) >= 12]


def judge(store, warehouse, niche, trends):
    """Every company of the store with its evidence, its score for each trend and its order.

    warehouse: {"energy_companies": [row dicts], "energy_deals": [row dicts]} as read from the tables now.
    Returns a list of companies in the order of rule 4, each:
      {key, name, aliases, row (resolved), evidence: [{tier, address, text, sha, fetched}],
       ties: {trend number: {score, tied, lines: [{address, tier, points, terms, phrase, text}]}},
       trends: [numbers tied], tie: total score, tier: best tier of a tying line or "", reason: the best tying line}
    """
    niche_words = [w for w in words(head_of(niche)) if len(w) >= 4 and fold(w) not in STOP]
    names = [(x["row"].get("name") or x["key"], x["row"].get("website") or "") for x in store["rows"]]
    cl = clusters(names, niche_words)
    groups = {}
    for x in store["rows"]:
        if x["key"] in cl:
            groups.setdefault(cl[x["key"]], []).append(x)
    specs = [trend_terms(niche, t) for t in trends]
    out = []
    for (ckey, cname), rows in sorted(groups.items()):
        raw_keys = sorted({x["key"] for x in rows})
        aliases = sorted({(k, core_of(k, niche_words)) for k in raw_keys})
        cores = {c for _, c in aliases}
        ev = []
        for x in warehouse.get("energy_companies") or []:
            k = name_key(x.get("name", ""))
            if k and (k in raw_keys or core_of(k, niche_words) in cores):
                addr = f"erw:energy_companies/{x.get('name', '')}"
                for s in sentences(x.get("description", "")) + ([f"Tags: {x['niche_tags']}"] if x.get("niche_tags") else []):
                    ev.append({"tier": "warehouse", "address": addr, "text": s, "sha": sha(s), "fetched": x.get("retrieved_at", "")[:10]})
        for x in warehouse.get("energy_deals") or []:
            cells = " | ".join(str(x.get(c) or "") for c in ("deal_type", "parties", "asset", "technology") if x.get(c))
            if names_it(str(x.get("parties") or "") + " " + str(x.get("asset") or "") + " " + str(x.get("technology") or ""), aliases, niche_words):
                ev.append({"tier": "warehouse", "address": f"erw:energy_deals/{x.get('event_id', '')}", "text": cells, "sha": sha(cells),
                           "fetched": str(x.get("extracted_at") or x.get("event_date") or "")[:10]})
        for url in sorted(store["sources"]):
            s = store["sources"][url]
            for text in [s.get("title", "")] + list(s.get("cited") or []):
                if len(text) >= 12 and names_it(text, aliases, niche_words):
                    ev.append({"tier": "fetched", "address": url, "text": text, "sha": sha(text), "fetched": s.get("fetched", "")})
        for q in sorted(store["quotes"], key=lambda q: (q["address"], q["sha"])):
            if q["key"] not in raw_keys:
                continue
            held = store["sources"].get(q["address"])
            inside = held is not None and " ".join(words(q["text"])) in " ".join(words(source_text(held)))
            ev.append({"tier": "fetched" if inside else "web", "address": q["address"], "text": q["text"], "sha": q["sha"], "fetched": q.get("fetched", "")})
        seen, uniq = set(), []
        for e in ev:                                   # one saved sentence of one address counts once, at its best tier
            ident = (e["address"], e["sha"])
            if ident not in seen:
                seen.add(ident)
                uniq.append(e)
        own = {t for k in raw_keys for t in tokens(k)}
        ties, tied, total, best_tier, best_line = {}, [], 0, "", None
        for n, (terms, phrases) in enumerate(specs, 1):
            per_addr = {}
            for e in uniq:
                matched, phrase = support(e["text"], terms, phrases, own)
                if not phrase and len(matched) < MIN_TERMS:
                    continue
                pts = TIERS[e["tier"]] + (STRONG_POINT if phrase or len(matched) >= STRONG_TERMS else 0)
                line = {"address": e["address"], "tier": e["tier"], "points": pts, "terms": matched, "phrase": phrase, "text": e["text"], "sha": e["sha"]}
                old = per_addr.get(e["address"])
                if old is None or (-pts, TIER_ORDER.index(e["tier"]), e["sha"]) < (-old["points"], TIER_ORDER.index(old["tier"]), old["sha"]):
                    per_addr[e["address"]] = line
            lines, said = [], set()
            for x in sorted(per_addr.values(), key=lambda x: (-x["points"], TIER_ORDER.index(x["tier"]), x["address"])):
                if x["sha"] not in said:              # the same sentence on a second address is not a second piece of evidence
                    said.add(x["sha"])
                    lines.append(x)
            lines = lines[:MAX_ADDRESSES]
            score = sum(x["points"] for x in lines)
            ties[n] = {"score": score, "tied": score >= TIE_MIN, "lines": lines}
            if score >= TIE_MIN:
                tied.append(n)
                total += score
                top = lines[0]
                if best_line is None or (-top["points"], TIER_ORDER.index(top["tier"]), top["address"]) < (-best_line["points"], TIER_ORDER.index(best_line["tier"]), best_line["address"]):
                    best_line = top
                for x in lines:
                    if not best_tier or TIER_ORDER.index(x["tier"]) < TIER_ORDER.index(best_tier):
                        best_tier = x["tier"]
        row = resolve(rows)
        for sb in row["stated_by"].values():          # which of the sources behind a fact were first fetched by the run that stated it
            sb["new_sources"] = [u for u in sb["sources"] if (store["sources"].get(u) or {}).get("first_run") == sb["run_id"]]
        out.append({"key": ckey, "name": cname, "aliases": raw_keys, "row": row, "evidence": uniq, "ties": ties,
                    "trends": tied, "tie": total, "tier": best_tier, "reason": best_line})
    out.sort(key=order_key)
    return out


def order_key(c):
    """Rule 4: total score, then best tier, then normalized name."""
    return (-c["tie"], TIER_ORDER.index(c["tier"]) if c["tier"] else len(TIER_ORDER), c["key"])


# ---------------------------------------------------------------------------------------------
# what changed between two runs
# ---------------------------------------------------------------------------------------------

def snapshot(run_id, judged, placed):
    """What one run rested on, kept in the store for the next run's diff. placed: {key: (funnel stage, confidence)}."""
    return {"run_id": run_id, "companies": {c["key"]: {
        "name": c["name"], "aliases": c["aliases"], "reached": placed.get(c["key"], ("", None))[0], "trends": c["trends"], "tie": c["tie"],
        "facts": dict({f: c["row"].get(f) for f in FACTS}, confidence=placed.get(c["key"], ("", None))[1],
                      stage_cell=c["row"].get("stage"), raised_cell=c["row"].get("raised")),
        "stated_by": c["row"].get("stated_by", {}),
        "evidence": sorted([e["tier"], e["address"], e["sha"]] for e in c["evidence"])} for c in judged}}


def diff(before, after):
    """Every difference of evidence and of place between two snapshots, by company and source.
    Returns {new_companies, gone_companies, moved: [{name, from, to, added, removed, facts}], evidence_only: n}."""
    a = after["companies"]
    same = {alias: k for k, c in a.items() for alias in c.get("aliases") or []}       # a company that gained a longer name is the same company
    b = {}
    for k, c in ((before or {}).get("companies", {})).items():
        k2 = k if k in a else next((same[x] for x in [k] + list(c.get("aliases") or []) if x in same), k)
        if k2 in b:                                    # two names of the run before are one company now: their evidence together
            c = dict(b[k2], evidence=sorted(b[k2]["evidence"] + [e for e in c["evidence"] if e not in b[k2]["evidence"]]))
        b[k2] = c
    out = {"from_run": (before or {}).get("run_id", ""), "to_run": after["run_id"], "new_companies": [], "gone_companies": [], "moved": [], "evidence_changes": 0}
    for k in sorted(set(a) | set(b)):
        if k not in b:
            out["new_companies"].append({"name": a[k]["name"], "reached": a[k]["reached"], "evidence": a[k]["evidence"]})
            continue
        if k not in a:
            out["gone_companies"].append({"name": b[k]["name"], "reached": b[k]["reached"]})
            continue
        eb, ea = {tuple(e) for e in b[k]["evidence"]}, {tuple(e) for e in a[k]["evidence"]}
        added, removed = sorted(ea - eb), sorted(eb - ea)
        facts = {f: [b[k]["facts"].get(f), a[k]["facts"].get(f)] for f in sorted(set(a[k]["facts"]) | set(b[k]["facts"])) if b[k]["facts"].get(f) != a[k]["facts"].get(f)}
        out["evidence_changes"] += len(added) + len(removed)
        if b[k]["reached"] != a[k]["reached"] or b[k]["trends"] != a[k]["trends"]:
            out["moved"].append({"name": a[k]["name"], "from": b[k]["reached"], "to": a[k]["reached"], "trends_from": b[k]["trends"], "trends_to": a[k]["trends"],
                                 "added": [list(e) for e in added], "removed": [list(e) for e in removed], "facts": facts,
                                 "fact_sources": {f: a[k].get("stated_by", {}).get(f) for f in facts if a[k].get("stated_by", {}).get(f)},
                                 "explained": bool(added or removed or facts)})
            m = out["moved"][-1]
            # a fact filled from sources the store already held is the model's reading, not a change of source: said so
            filled = [s for s in m["fact_sources"].values() if s.get("run_id") == after["run_id"]]
            m["reading_only"] = bool(not added and not removed and filled and not any(s.get("new_sources") for s in filled))
    # the pipeline map holds a fixed number: a company can leave or enter it because another company's evidence changed
    others = bool(out["new_companies"]) or any(m["explained"] for m in out["moved"])
    for m in out["moved"]:
        if not m["explained"] and {m["from"], m["to"]} == {"trend", "pipeline"} and others:
            m["explained"], m["by_order"] = True, True
    return out
