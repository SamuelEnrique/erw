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
     web         a sentence of a page the run saved (session 147): the run fetches, in code, the address of every web
                 result its rows cite and keeps the page's text with its hash and the day it was retrieved
                 (pages.py). Every sentence of a saved page that names the company is evidence, whichever company's
                 row cited the page. A page that was refused, disallowed, truncated or not text holds no sentence.
                 Until session 147 this tier was the sentences the research QUOTED from a page; a quoted sentence
                 now decides nothing: when it is on the saved page and names the company it is simply one of the
                 page's sentences, and when it is not on the saved page it is not evidence. The quotations are still
                 saved, and quote_check() says of each whether the saved page holds it.
   A sentence of a page is a run of text inside one block of the page (a paragraph, a heading, a list item), cut at
   its sentence ends, of 12 to PAGE_SENTENCE_MAX (500) characters: a longer run without a sentence end is a menu, a
   list or a table, not a sentence (the longest sentence the research ever quoted had 369).
   A text "names the company" when it holds the company's whole normalized name, or its core name (the name without
   trailing generic words such as Energy or Technologies). A name or core name of one word must have four letters
   or more and the text must also hold a word of the niche's own name.
   Session 158 (the owner's ruling of 8 October 2026). A company whose name is MADE OF THE NICHE'S OWN WORDS is named
   by a text only as a proper noun. The name is made of the niche's own words when every word of it (normalized and
   folded as above) is a word of the niche's own name, a term of one of the five trends (rule 2), or one of the
   generic or stop words below (GENERIC, STOP), and at least one of them is a word of the niche's name or a trend's
   term ("Geothermal Technologies" in a geothermal niche). For such a company the text must hold the name's words as
   before AND one of three things must be true:
     capital   the name stands in the text with the capitals the company's rows write it with, and is not part of a
               longer capitalized name: the word just before it (only spaces or a hyphen between) does not start with
               a capital, unless it is one of SMALL_WORDS (The, In, And, ...), and the word just after it does not
               start with a capital, unless it is a legal form (Inc, LLC, ...) or a role (CEO, Founder, ...). So
               "the DOE Geothermal Technologies Office" is not the company. A name of one word that opens the
               sentence shows nothing by its capital. Nor does any name in a heading written with every word
               capitalized: when the text has two or more words of four letters or more outside the name that are
               not SMALL_WORDS and every one of them starts with a capital, this test fails.
     list      the name, with its capitals, is one whole item of an enumeration of LIST_MIN (3) or more capitalized
               names standing side by side: the text is cut at each comma, semicolon, bar or bullet and at "and",
               "or" and "&"; an item is a capitalized name when it is one to six words that each start with a
               capital; before the first item of a sentence and after its last there may be other words (so the
               first counts by the capitalized word it ends with, the last by the one it starts with). A table cell
               or list item that is the name alone is the name with its capitals standing alone: the first test.
     domain    the text holds the company's website domain, or the page (or fetched source) the text is from is at
               that domain or holds it in its text.
   Every other company is matched as before. Each company's record says which test counted each sentence and how
   many sentences held the name's words and were not counted.

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
   two pages of one university). Session 158: nor does the same REMARK printed with small differences. The words
   of a sentence as a remark: lower case, punctuation removed, and, when the sentence holds a quotation of
   NEAR_MIN_WORDS (8) words or more, only the words inside its quotation marks (the words around a quotation say who
   spoke). Two sentences are the same remark when both have NEAR_MIN_WORDS words or more and the words they share,
   each counted as often as both hold it, are NEAR_SAME (90 percent) or more of the words of the longer one. Of the
   copies, the one read first in the order above counts (highest points, then the higher tier, then the address a to
   z), so the higher-tier copy is kept; every merged pair is in the run's record.
   The company is TIED to the trend when that score is TIE_MIN (2) or more: one
   warehouse sentence, one fetched sentence, one strong web sentence, or two different web sentences from two
   addresses.

4. The tie-break. Companies are ordered by their total score over the trends they are tied to (highest first), then
   by their best evidence tier (warehouse before fetched before web), then by their normalized name (a to z).

5. Duplicate names. Two names are one company when their core names are equal, or when the core name of one is the
   leading words of the other's ("Eden" and "Eden GeoPower") and their website domains do not differ. A short name
   that leads two or more longer names that are not themselves one company is ambiguous and is merged with none.
   The company keeps its longest name (most words, then most letters, then a to z).

6. What is saved. The evidence store of a niche (one JSON document: an object of a private storage bucket since
   session 147, a local file where no key is set; store.py) keeps every fetched source by address with the hash
   of its text and the date fetched, every reported sentence with its address, every row a run wrote about a
   company, and since session 147 every page a run asked for, by address: its text, the SHA-256 of what was
   received and of the text, the day retrieved, the HTTP status, the bytes, and each earlier version whose text
   differed. A run reads what is saved plus what it newly fetched, so a run differs from the one before only because
   a source was added, changed or disappeared, and diff() says which, by company and source. A company's facts
   (kind, country, location, stage fit) and its descriptive cells are the first values saved for it: a fact not yet
   stated can be filled by a later run, with that run's sources, and a later run that reads a stated fact
   differently changes nothing; its reading is kept in the run's record as a disagreement for a person to rule on.
   (The first version of this rule let the value with the most sources win. The second run of 7 October 2026 then
   moved a company because the model called a university spinout a university: an opinion, not a source.)

7. Data vendors' public pages (session 158). A page of a data vendor (the list is one file, vendor_pages.csv, read by
   pages.py and handed to judge) is read like any other page, and every sentence from it carries the vendor's name
   ("vendor" on the evidence line and on a tying line). It changes no point: the label is for the reader.
"""

import collections
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
PAGE_SENTENCE_MAX = 500          # session 147: what a sentence of a saved page is, not a threshold of the scoring
STOP = {"the", "and", "for", "with", "from", "that", "this", "into", "their", "new", "not", "general", "only", "based", "using",
        "technologie", "technology", "companie", "company", "startup", "market", "energy", "power",
        "system", "method", "public", "high"}
GENERIC = {"energy", "power", "technologies", "technology", "systems", "international", "resources", "minerals", "partners",
           "labs", "group", "solutions", "services", "company", "industries"}
BLANK = {"", "not stated", "not disclosed", "unknown", "n/a", "none", "undisclosed"}
# Session 158. None of these is a threshold of the scoring (TIERS, STRONG_POINT, STRONG_TERMS, MIN_TERMS, TIE_MIN and
# MAX_ADDRESSES above are untouched): they say what "the same remark" and "a proper noun" are.
NEAR_SAME = 0.90                 # two sentences are one remark when they share this share of the longer one's words
NEAR_MIN_WORDS = 8               # and each has at least this many words; also the least a quotation holds to be the remark
LIST_MIN = 3                     # an enumeration of this many capitalized names is a list of companies
LEGAL = ("inc", "llc", "ltd", "corp", "corporation", "co", "plc", "lp", "sa", "ag", "gmbh", "limited", "holdings")      # as name_key drops them
ROLES = {"ceo", "cto", "cfo", "coo", "founder", "cofounder", "president", "chairman", "chief"}
SMALL_WORDS = {"the", "a", "an", "and", "but", "or", "nor", "in", "on", "at", "by", "for", "from", "with", "as", "to", "of", "into", "over", "under",
               "than", "via", "per", "when", "while", "after", "before", "since", "both", "also", "its", "their", "our", "your", "this", "that",
               "these", "those", "if", "how", "why", "what", "where", "who", "is", "are", "was", "were", "will", "been", "have", "more", "most",
               "about", "amid", "near", "onto", "upon"}
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
    return names_norm(" " + " ".join(words(text)) + " ", aliases, niche_words)


def names_norm(t, aliases, niche_words):
    """names_it on a text already written as its words between single spaces, with a space at each end."""
    in_niche = any(f" {w} " in t for w in niche_words)
    for full, core in aliases:
        for n in (full, core):
            if not n or f" {n} " not in t:
                continue
            if " " in n or (len(n) >= 4 and in_niche):
                return True
    return False


# ---------------------------------------------------------------------------------------------
# session 158: a name made of the niche's own words is named only as a proper noun
# ---------------------------------------------------------------------------------------------

_TOKEN = re.compile(r"[A-Za-z0-9]+")
_BESIDE = re.compile(r"[ \t -]*\Z")                  # two words stand side by side: only spaces or a hyphen between them
_CUT = re.compile(r"[,;|•·]|\s&\s|\band\b|\bor\b")
GENERIC_FOLDED = {fold(w) for w in GENERIC} | STOP


def niche_own(niche, trends):
    """The niche's own words: the words of its name (four letters or more, not a stop word) and the terms of its
    trends, each folded, exactly as judge and trend_terms compute them."""
    own = {fold(w) for w in words(head_of(niche)) if len(w) >= 4 and fold(w) not in STOP}
    for t in trends or []:
        own |= set(trend_terms(niche, t)[0])
    return own


def made_of_niche(key, own):
    """True when a normalized name is made of the niche's own words: every word of it is one of them or a generic or
    stop word, and at least one is one of them."""
    toks = tokens(key)
    return bool(toks) and any(t in own for t in toks) and all(t in own or t in GENERIC_FOLDED for t in toks)


def written_names(names):
    """The ways a company's rows write its name: each as its words in their own capitals, without what stands in
    brackets and without legal forms (as name_key drops them)."""
    out = []
    for name in names:
        toks = [t for t in _TOKEN.findall(re.sub(r"\(.*?\)", " ", name or "")) if t.lower() not in LEGAL]
        if toks and toks not in out:
            out.append(toks)
    return out


def carries_domain(text, d):
    """True when a text holds a website domain as written (not as part of a longer one)."""
    return bool(d) and re.search(r"(?<![a-z0-9.-])" + re.escape(d) + r"(?![a-z0-9-])(?!\.[a-z0-9])", (text or "").lower()) is not None


def on_domain(address, d):
    h = domain(address)
    return bool(d) and bool(h) and (h == d or h.endswith("." + d))


def _capital(text, toks, i, form):
    """The first test of rule 1: the name at token i with the company's own capitals, not part of a longer capitalized name."""
    n = len(form)
    if [t[0] for t in toks[i:i + n]] != form:
        return False
    if n == 1 and i == 0:
        return False                                   # one word opening the sentence: its capital shows nothing
    if i > 0:
        w = toks[i - 1]
        if _BESIDE.match(text[w[2]:toks[i][1]]) and w[0][0].isupper() and w[0].lower() not in SMALL_WORDS:
            return False
    if i + n < len(toks):
        w = toks[i + n]
        if _BESIDE.match(text[toks[i + n - 1][2]:w[1]]) and w[0][0].isupper() and w[0].lower() not in LEGAL and w[0].lower() not in ROLES:
            return False
    rest = [t[0] for k, t in enumerate(toks) if not i <= k < i + n and len(t[0]) >= 4 and t[0][0].isalpha() and t[0].lower() not in SMALL_WORDS]
    if len(rest) >= 2 and all(w[0].isupper() for w in rest):
        return False                                   # a heading with every word capitalized shows no proper noun
    return True


def _in_a_list(text, toks, i, form):
    """The second test of rule 1: the name at token i, with its capitals, is one whole item of an enumeration of
    LIST_MIN or more capitalized names side by side."""
    n = len(form)
    if [t[0] for t in toks[i:i + n]] != form:
        return False
    edges = [0] + [x for m in _CUT.finditer(text) for x in m.span()] + [len(text)]
    items = []
    for a, b in zip(edges[0::2], edges[1::2]):
        inside = [k for k, t in enumerate(toks) if a <= t[1] and t[2] <= b]
        if inside:
            items.append(inside)
    at = next((m for m, it in enumerate(items) if i in it), None)
    if at is None or any(k not in items[at] for k in range(i, i + n)):
        return False

    def cap(k):
        return toks[k][0][0].isupper()

    def whole(it):
        return 1 <= len(it) <= 6 and all(cap(k) for k in it)

    first, last = 0, len(items) - 1
    before = [k for k in items[at] if k < i]
    after = [k for k in items[at] if k >= i + n]
    while after and toks[after[0]][0].lower() in LEGAL:
        after = after[1:]
    if before and not (at == first and not cap(before[-1])):
        return False
    if after and not (at == last and not cap(after[0])):
        return False
    count = 1
    for m in range(at - 1, -1, -1):
        if (m > first and whole(items[m])) or (m == first and cap(items[m][-1])):
            count += 1
        else:
            break
    for m in range(at + 1, len(items)):
        if (m < last and whole(items[m])) or (m == last and cap(items[m][0])):
            count += 1
        else:
            break
    return count >= LIST_MIN


def proper_noun(text, forms, domains=(), address="", page_text="", page_carries=None):
    """How a text names a company whose name is made of the niche's own words (rule 1, session 158).
    forms: the name as its rows write it (written_names), and its core name. domains: the company's website domains.
    address, page_text: the page or fetched source the text is from. Returns "capital", "list" or "domain" (the test
    that holds, tried in that order), "not a proper noun" when the name's words are there and no test holds, or ""
    when the name's words are not in the text at all. page_carries: what the caller already knows of the page (it is
    at one of the domains or holds one), so that a page is searched once and not once a sentence."""
    toks = [(m.group(), m.start(), m.end()) for m in _TOKEN.finditer(text or "")]
    low = [t[0].lower() for t in toks]
    found, listed = False, False
    for form in forms:
        n, want = len(form), [w.lower() for w in form]
        for i in range(len(toks) - n + 1):
            if low[i:i + n] != want:
                continue
            found = True
            if _capital(text, toks, i, form):
                return "capital"
            listed = listed or _in_a_list(text, toks, i, form)
    if not found:
        return ""
    if listed:
        return "list"
    if page_carries is None:
        page_carries = any(on_domain(address, d) or carries_domain(page_text, d) for d in domains)
    if page_carries or any(carries_domain(text, d) for d in domains):
        return "domain"
    return "not a proper noun"


# ---------------------------------------------------------------------------------------------
# session 158: the same remark printed twice counts once; a data vendor's page is labeled
# ---------------------------------------------------------------------------------------------

def remark(text):
    """The words of a sentence as a remark is compared (rule 3): lower case, no punctuation; when the sentence holds a
    quotation of NEAR_MIN_WORDS words or more, only the words inside its quotation marks."""
    parts = re.split("[\"“”«»]", text or "")
    inside = [w for seg in parts[1::2] for w in words(seg)]
    return inside if len(inside) >= NEAR_MIN_WORDS else words(text)


def remark_share(a, b):
    """The words two remarks share, each counted as often as both hold it, over the words of the longer one."""
    if not a or not b:
        return 0.0
    return sum((collections.Counter(a) & collections.Counter(b)).values()) / max(len(a), len(b))


def same_remark(a, b):
    return len(a) >= NEAR_MIN_WORDS and len(b) >= NEAR_MIN_WORDS and remark_share(a, b) >= NEAR_SAME


def vendor_of(address, vendors):
    """The data vendor whose page an address is (rule 7), or "". vendors: {domain: the vendor's name}."""
    h = domain(address)
    for d in sorted(vendors or {}):
        if h and (h == d or h.endswith("." + d)):
            return vendors[d]
    return ""


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
    """Session 147: version 2 holds the saved pages by address (pages) and each host's robots.txt rules (robots)."""
    return {"version": 2, "niche": niche, "stage": stage, "geography": geography, "runs": [], "sources": {}, "quotes": [],
            "rows": [], "pages": {}, "robots": {}, "last": None}


def load_store(path, niche="", stage="", geography=""):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            store = json.load(f)
        store.setdefault("pages", {})                 # a store written before session 147 holds no page
        store.setdefault("robots", {})
        return store
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


def page_sentences(text):
    """The sentences of a saved page (rule 1): each block of the page is a line of the saved text; a line is cut at its
    sentence ends, and a run longer than PAGE_SENTENCE_MAX is not a sentence."""
    return [s for line in (text or "").split("\n") for s in sentences(line) if len(s) <= PAGE_SENTENCE_MAX]


def page_holds(page):
    """True when a saved page holds sentences: fetched whole, with text. A refused, disallowed or truncated page holds none."""
    return bool(page) and page.get("state") == "fetched" and not page.get("truncated") and bool(page.get("text"))


def quote_check(store):
    """Of every quotation the research reported: does the saved page of its address hold it, word for word? For the
    run's record only: a quotation decides nothing (rule 1). Returns [{key, address, sha, page, found}] where page is
    "held", "not held" (no sentence could be read from it) or "never asked for"."""
    pages, flat, out = store.get("pages") or {}, {}, []
    for q in sorted(store.get("quotes") or [], key=lambda q: (q["address"], q["sha"], q["key"])):
        p = pages.get(q["address"])
        state = "never asked for" if p is None else ("held" if page_holds(p) else "not held")
        found = False
        if state == "held":
            if q["address"] not in flat:
                flat[q["address"]] = " " + " ".join(words(p["text"])) + " "
            found = (" " + " ".join(words(q["text"])) + " ") in flat[q["address"]]
        out.append({"key": q["key"], "address": q["address"], "sha": q["sha"], "page": state, "found": found})
    return out


def judge(store, warehouse, niche, trends, read="pages", vendors=None, proper=True, remarks=True):
    """Every company of the store with its evidence, its score for each trend and its order.

    read: "pages" (the rule since session 147: the web tier is the sentences of the saved pages) or "quotes" (the web
    tier as session 142 built it, the sentences the research quoted: kept so that the two readings can be compared on
    the same saved answers, and used by no run).
    warehouse: {"energy_companies": [row dicts], "energy_deals": [row dicts]} as read from the tables now.
    vendors: {domain: name} of the data vendors whose public pages are labeled (rule 7; pages.vendor_pages()), or None.
    proper, remarks: True, always, for a run. False reads the saved evidence as before session 158 (a name made of the
    niche's own words matched wherever its words stand; a remark printed twice counted twice), so that what each
    ruling changes can be measured on the same saved answers; no run uses it.
    Session 158: each company also carries name_rule (None, or for a name made of the niche's own words the tests
    that counted its sentences and those not counted) and near_duplicates (the pairs of sentences read as one remark).
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
    own_words = niche_own(niche, trends)               # session 158: a name made only of these is named as a proper noun only

    def flat_of(text):
        return " " + " ".join(words(text)) + " "

    saved = []                                         # session 147: every sentence of every saved page, cut once
    if read == "pages":
        for url in sorted(store.get("pages") or {}):
            p = store["pages"][url]
            if page_holds(p):
                saved.append((url, p.get("fetched", ""), " " + " ".join(words(p["text"])) + " ",
                              [(s, " " + " ".join(words(s)) + " ") for s in page_sentences(p["text"])], p["text"]))
    out = []
    for (ckey, cname), rows in sorted(groups.items()):
        raw_keys = sorted({x["key"] for x in rows})
        aliases = sorted({(k, core_of(k, niche_words)) for k in raw_keys})
        cores = {c for _, c in aliases}
        # session 158: the aliases made of the niche's own words are matched as proper nouns only; the others as before
        strict = [(k, c) for k, c in aliases if proper and made_of_niche(k, own_words)]
        loose = [a for a in aliases if a not in strict]
        forms, doms = [], set()
        for k, c in strict:
            for w in written_names([x["row"].get("name") or "" for x in rows if x["key"] == k]):
                for form in (w, w[:len(c.split())]):
                    if form and form not in forms:
                        forms.append(form)
        for x in rows if strict else []:
            doms.add(domain(x["row"].get("website") or ""))
            for inner in re.findall(r"\(([^)]*)\)", x["row"].get("name") or ""):       # a domain written in the name's brackets
                if re.match(r"(?:https?://)?(?:www\.)?[a-z0-9.-]+\.[a-z]{2,}/?\Z", inner.strip().lower()):
                    doms.add(domain(inner.strip()))
        doms = sorted(doms - {""})
        counted, refused = {"capital": 0, "list": 0, "domain": 0}, []

        def named(text, norm, address="", page_text="", page_carries=None):
            """How a text names this company: "" (it does not), "name" (as before session 158), or the test of rule 1."""
            if names_norm(norm, loose, niche_words):
                return "name"
            if not strict or not names_norm(norm, strict, niche_words):
                return ""
            why = proper_noun(text, forms, doms, address, page_text, page_carries)
            if why in counted:
                counted[why] += 1
                return why
            refused.append({"address": address, "text": text})
            return ""

        ev = []
        for x in warehouse.get("energy_companies") or []:
            k = name_key(x.get("name", ""))
            if k and (k in raw_keys or core_of(k, niche_words) in cores):
                addr = f"erw:energy_companies/{x.get('name', '')}"
                for s in sentences(x.get("description", "")) + ([f"Tags: {x['niche_tags']}"] if x.get("niche_tags") else []):
                    ev.append({"tier": "warehouse", "address": addr, "text": s, "sha": sha(s), "fetched": x.get("retrieved_at", "")[:10]})
        for x in warehouse.get("energy_deals") or []:
            cells = " | ".join(str(x.get(c) or "") for c in ("deal_type", "parties", "asset", "technology") if x.get(c))
            deal = str(x.get("parties") or "") + " " + str(x.get("asset") or "") + " " + str(x.get("technology") or "")
            if named(deal, flat_of(deal), str(x.get("source_url") or "")):
                ev.append({"tier": "warehouse", "address": f"erw:energy_deals/{x.get('event_id', '')}", "text": cells, "sha": sha(cells),
                           "fetched": str(x.get("extracted_at") or x.get("event_date") or "")[:10]})
        for url in sorted(store["sources"]):
            s = store["sources"][url]
            carries = any(on_domain(url, d) or carries_domain(source_text(s), d) for d in doms) if strict else None
            for text in [s.get("title", "")] + list(s.get("cited") or []):
                how = named(text, flat_of(text), url, page_carries=carries) if len(text) >= 12 else ""
                if how:
                    ev.append({"tier": "fetched", "address": url, "text": text, "sha": sha(text), "fetched": s.get("fetched", "")})
                    if how != "name":
                        ev[-1]["named"] = how
        for url, day, flat, sents, raw in saved:      # session 147: the web tier is read from the saved pages
            if not any(n and f" {n} " in flat for pair in aliases for n in pair):
                continue                               # the page does not hold the company's name at all
            carries = any(on_domain(url, d) or carries_domain(raw, d) for d in doms) if strict else None
            for s, norm in sents:
                how = named(s, norm, url, page_carries=carries)
                if how:
                    ev.append({"tier": "web", "address": url, "text": s, "sha": sha(s), "fetched": day})
                    if how != "name":
                        ev[-1]["named"] = how
        for q in sorted(store["quotes"], key=lambda q: (q["address"], q["sha"])) if read == "quotes" else []:
            if q["key"] not in raw_keys:              # session 142's reading, for comparison only: no run uses it
                continue
            held = store["sources"].get(q["address"])
            inside = held is not None and " ".join(words(q["text"])) in " ".join(words(source_text(held)))
            ev.append({"tier": "fetched" if inside else "web", "address": q["address"], "text": q["text"], "sha": q["sha"], "fetched": q.get("fetched", "")})
        seen, uniq = set(), []
        for e in ev:                                   # one saved sentence of one address counts once, at its best tier
            ident = (e["address"], e["sha"])
            if ident not in seen:
                seen.add(ident)
                v = vendor_of(e["address"], vendors) if e["tier"] != "warehouse" else ""
                if v:                                  # session 158: a sentence from a data vendor's public page carries its label
                    e["vendor"] = v
                uniq.append(e)
        merged = []                                    # session 158: the pairs of sentences read as one remark
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
                if e.get("vendor"):
                    line["vendor"] = e["vendor"]
                old = per_addr.get(e["address"])
                if old is None or (-pts, TIER_ORDER.index(e["tier"]), e["sha"]) < (-old["points"], TIER_ORDER.index(old["tier"]), old["sha"]):
                    per_addr[e["address"]] = line
            lines, said, kept = [], set(), []
            for x in sorted(per_addr.values(), key=lambda x: (-x["points"], TIER_ORDER.index(x["tier"]), x["address"])):
                if x["sha"] not in said:              # the same sentence on a second address is not a second piece of evidence
                    mine = remark(x["text"])
                    twin = next((y for y, theirs in kept if same_remark(mine, theirs)), None) if remarks else None
                    if twin is not None:              # session 158: nor is the same remark printed with small differences
                        pair = {"kept": {"address": twin["address"], "sha": twin["sha"], "tier": twin["tier"]},
                                "dropped": {"address": x["address"], "sha": x["sha"], "tier": x["tier"]},
                                "share": round(remark_share(mine, remark(twin["text"])), 4), "trends": [n]}
                        old = next((m for m in merged if m["kept"] == pair["kept"] and m["dropped"] == pair["dropped"]), None)
                        if old is None:
                            merged.append(pair)
                        else:
                            old["trends"].append(n)
                        continue
                    said.add(x["sha"])
                    kept.append((x, mine))
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
        name_rule = None if not strict else {"names": [k for k, _ in strict], "written": [" ".join(f) for f in forms], "domains": doms, "counted": counted,
                                             "not_counted": len(refused), "not_counted_examples": refused[:5]}
        out.append({"key": ckey, "name": cname, "aliases": raw_keys, "row": row, "evidence": uniq, "ties": ties,
                    "trends": tied, "tie": total, "tier": best_tier, "reason": best_line, "name_rule": name_rule, "near_duplicates": merged})
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
