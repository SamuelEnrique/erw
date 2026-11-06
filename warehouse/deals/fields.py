#!/usr/bin/env python3
"""The deal tracker's fields: one vocabulary each, with its reasoning, and the checks that keep a field only where a
story states it.

Energy Research Warehouse (ERW), session 2232 (chain 156, `docs/reviews/deals-audit-2026-11-06.md` rows A1 to A4, A6,
A9). `warehouse/deals/extract.py` asks the model for these fields and passes every deal through `finish()` before it is
written; `upgrade()` gives a row extracted before this session the fields that can be read from its own stored values,
with no model. `tests/test_session2232_deals.py` grades the whole path on the fixture of 40 stored stories
(`tests/fixtures/deals/`). Nothing here calls a model or reads a file.

A field the Roundup reads (`deal_type`, `buyer`, `seller`, `asset`, `mw`, `dollars`, `status`, `event_date`,
`story_urls`, `confidence`) keeps its name and meaning; every field below is new and sits beside them (the chain's
rule). `usd` is `dollars` and `usd_per_mwh` is `price` under the names the chain's prompt gives the units; the old two
stay for their readers.
"""

import re

# ---------------------------------------------------------------- the vocabularies

# KIND: what master plan tool 6 calls a deal ("nuclear restarts, SMR offtakes, gas buildouts, PPAs, behind-the-meter").
# deal_type stays the transaction's form (a PPA, an acquisition, a loan); kind is what a reader filters on. A deal is
# often both a form and a power kind (a PPA for a restarted reactor): the power kinds come first, in this order,
# because they are what tool 6 asks for and the form is still in deal_type. compute_capacity is the audit's class 4
# (a cloud, GPU or datacenter capacity contract stored as an offtake): kept, labelled, filterable, for Samuel's ruling.
KINDS = [
    ("nuclear_restart_uprate", "a reactor brought back into service or uprated: restart, recommission, reopen, uprate"),
    ("smr", "a small modular, micro or advanced reactor: SMR, small modular, microreactor, advanced reactor"),
    ("behind_the_meter", "power delivered to a load on its site, not through the grid: behind the meter, co-located, "
                         "on-site, off-grid"),
    ("gas_buildout", "new gas-fired generation: a gas plant, gas turbines or generation equipment, combined cycle, "
                     "peakers, to be built or ordered (buying a running plant is m_and_a)"),
    ("transmission", "a line, an interconnector or a substation"),
    ("storage", "a battery or other storage asset, alone or with solar or wind: battery, storage, BESS, pumped hydro"),
    ("compute_capacity", "cloud, GPU or datacenter capacity contracted, leased or hosted: not energy, kept apart"),
    ("ppa", "a power purchase agreement of none of the kinds above"),
    ("offtake", "an offtake of a product (LNG, hydrogen, fuel, minerals) or of power not called a PPA"),
    ("project_finance", "debt or equity raised for one named project"),
    ("m_and_a", "an acquisition, a merger, a sale or a stake bought or sold"),
    ("capital", "a company's debt, equity raise, tax equity or joint venture, no one project named"),
    ("fuel_supply", "a contract to supply fuel (gas, LNG, uranium, coal, oil)"),
    ("other", "a transaction of none of the kinds above"),
]
KIND_IDS = [k for k, _ in KINDS]
POWER_KINDS = KIND_IDS[:7]

# STAGE: where the deal stands, as its words say. status keeps the five words the Roundup prints (rumored, announced,
# signed, closed, cancelled); stage adds the three a power deal reaches after signing (financed, under_construction,
# operating). Read only from the stated words, with the span (stage_text); empty when the words do not say.
STAGES = [
    ("rumored", "in talks, considering, exploring, looks to, weighs, reportedly, nears a deal"),
    ("announced", "announces, plans to, proposes, will acquire, to buy, offers, unveils, letter of intent"),
    ("signed", "signed, agreed, secured, awarded, entered into, inked, struck, sealed, locked in"),
    ("financed", "financial close, closes a loan or financing, raised, funded"),
    ("closed", "completed, closed, finalized, sold (an acquisition or a sale)"),
    ("under_construction", "broke ground, under construction, construction began"),
    ("operating", "online, operational, began commercial operation, energized, delivering"),
    ("cancelled", "cancelled, terminated, scrapped, withdrawn, called off"),
]
STAGE_IDS = [s for s, _ in STAGES]
# Session 2259 (chain 159): the stage read from the deal's own evidence words where the model gave none, in this order
# (the first that matches wins: a cancelled or rumored deal says so over its other verbs; "Meta picks Morgan Stanley
# ... source says" is rumored). The second read found 7 of 106 with the stage stated and left empty.
STAGE_WORDS = [
    ("cancelled", r"\bcancel\w*|\bterminat\w*|\bscrap(?:s|ped|ping)?\b|\bwithdr[ae]w\w*|called off|\bend(?:s|ed)? plans\b|"
                  r"\bdrop(?:s|ped)? (?:\w+ ){0,4}(?:plan|deal)\b|\babandon(?:s|ed)\b"),
    ("rumored", r"\bin talks\b|\btalks\b|\bconsider\w*|\bexplor\w*|\blooks? to\b|\bweigh(?:s|ing)?\b|\breportedly\b|"
                r"\bnear(?:s|ing)? (?:a )?deal\b|\bsources? (?:say|says|said)\b|people familiar|\bmull\w*|\bsaid to\b"),
    ("closed", r"\bcomplet(?:es|ed|ion)\b|\bclos(?:es|ed)\b(?! (?:in|to|on|down|up)\b)(?! (?:a |its |the )?(?:loan|financing|debt)\b)|"
               r"\bfinaliz\w*|\braised\b|\bsold\b|\bacquired\b"),
    ("financed", r"financial close|\bclos(?:es|ed) (?:a |its |the )?(?:loan|financing|debt)\b|\bfunded\b"),
    ("signed", r"\bsign(?:s|ed|ing)?\b|\bagree(?:s|d|ment)?\b|\bsecur(?:es|ed)\b|\bawarded?\b|entered into|\bink(?:s|ed)\b|"
               r"\bstr(?:uck|ikes?)\b|\bseal(?:s|ed)?\b|locked in|\bpartners? with\b|\bjoins?\b|\bpicks?\b|\bselects?\b|"
               r"\bdeal with\b|\bteams? up\b"),
    ("announced", r"\bannounc\w*|\bplans? to\b|\bpropos\w*|\bwill\b|\bunveil\w*|letter of intent|\boffers? to\b|"
                  r"\bto (?:buy|acquire|sell|serve|develop|build|supply|invest|lease|form|merge|partner|take)\b"),
]
def stage_from_words(evidence):
    """(stage, span) from the deal's own evidence sentence, by STAGE_WORDS in order; ("", "") when none says."""
    t = " ".join(str(evidence or "").replace("’", "'").split())
    for s, pat in STAGE_WORDS:
        m = re.search(pat, t, flags=re.I)
        if m:
            return s, m.group(0)
    return "", ""

# GRID: the US grid operators, kept only where the story's words name one. Never read from a state: a state split
# between grids would be a guess (the site reads a state's main grid on the page and says so, lib/deals2.ts).
GRIDS = {
    "ERCOT": [r"ercot", r"electric reliability council of texas"],
    "PJM": [r"pjm"],
    "MISO": [r"miso", r"midcontinent independent system operator"],
    "SPP": [r"spp", r"southwest power pool"],
    "CAISO": [r"caiso", r"california independent system operator", r"california iso"],
    "NYISO": [r"nyiso", r"new york independent system operator"],
    "ISO-NE": [r"iso-ne", r"iso new england"],
}

# AI_POWER: true only where a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load
# the deal serves is a datacenter (the chain's rule). ai_power_basis says which: "party <name>" or "datacenter load:
# <words>". A party list in code, not the model's sense, so the tag is the same on every run (the audit's row A6:
# Amazon's 960 MW nuclear pact was tagged false, a story that merely says "as AI demand booms" true).
AI_PARTIES = [
    "openai", "anthropic", "xai", "mistral", "meta", "facebook", "google", "alphabet", "microsoft", "amazon", "aws",
    "oracle", "apple", "nvidia", "coreweave", "crusoe", "lambda", "nebius", "equinix", "digital realty", "qts",
    "vantage data centers", "aligned data centers", "stack infrastructure", "switch", "cyrusone", "compass datacenters",
    "edgecore", "related digital", "tract", "stargate", "iren", "core scientific", "applied digital", "terawulf",
    "cipher mining", "galaxy digital", "fermi america", "poolside", "humain", "g42", "bytedance", "tencent", "alibaba",
    "airtrunk", "dayone", "sttgdc", "st telemedia", "neysa", "cerebras", "firmus", "nscale", "fluidstack", "volta",
    "chronoscale", "soluna", "hut 8", "bitdeer", "cologix", "flexential", "ntt data", "princeton digital",
]
DATACENTER_WORDS = re.compile(r"data ?cent(?:er|re)s?|datacent(?:er|re)s?|\bhyperscal\w*|\bai (?:campus|factory|"
                              r"compute|cloud|infrastructure)|\bgpus?\b|\bcomputing (?:deal|partnership|capacity)",
                              re.I)

# Prices: an energy price only (the audit's row A8: "80% equity selldown" was kept as a price of 80 "%").
ENERGY_PRICE_UNIT = re.compile(r"(?i)^\s*(?:usd|us\$|\$|eur|€|gbp|£|cad|aud)?\s*/\s*(?:mwh|kwh|mw-?month|kw-?month|"
                               r"mw-?day|kw-?year|mmbtu)\s*$")

# Sanity bounds: a figure above is flagged on the row (flags), never dropped (session 2235 reads them on the page).
# mw: 20 GW (the chain's example of a figure to flag is a 50 GW PPA); mwh: an energy contract can run
# to TWh (TotalEnergies and Airbus, 3.3 TWh), so 50 TWh (session 2235); usd: USD 500 billion; usd_per_mwh: USD 1,000.
BOUNDS = {"mw": 20000.0, "mwh": 5e7, "usd": 5e11, "usd_per_mwh": 1000.0, "term_years": 40.0}

# energy_deals' new columns hold no outlet text: words copied from a story (the stage's span, the confidence's basis, the
# figures' spans) go to the internal energy_deals_evidence beside its evidence sentence (EVIDENCE_NEW_COLS), as the
# evidence sentence always has (the site never shows outlet text: site/app/deals/page.tsx).
NEW_COLS = ["kind", "kind_basis", "stage", "grid", "usd", "usd_per_mwh", "ai_power_basis", "flags", "fields_version",
            "status_history"]   # status_history: session 2233 (warehouse/deals/dedupe.py)
EVIDENCE_NEW_COLS = ["stage_text", "confidence_basis", "spans"]
VERSION = "2232"


def plain(s):
    return " ".join(str(s or "").replace("’", "'").replace(" ", " ").split()).lower()


def in_text(span, text):
    return bool(span) and plain(span) in text


def _words(pat, s):
    return re.search(pat, s) is not None


KIND_WORDS = [
    ("nuclear_restart_uprate", r"\brestart\w*|recommission\w*|\breopen\w*|\buprat\w*|"
                               r"nuclear (?:plant |fleet |reactor )?upgrad\w*"),   # session 2258: "Illinois Nuclear Upgrades"
    ("smr", r"\bsmrs?\b|small modular|micro-?reactors?|advanced (?:nuclear|reactors?)|bwrx-?300"),
    ("behind_the_meter", r"behind[- ]the[- ]meter|co-?locat\w*|\bon-?site\b|\boff-?grid\b"),
    ("transmission", r"\btransmission\b|interconnector|\bhvdc\b|power lines?\b|\bsubstations?\b"),
    ("storage", r"batter(?:y|ies)|\bstorage\b|\bbess\b|pumped hydro"),
    ("compute_capacity", r"\bcloud\b|\bgpus?\b|computing|\bcompute\b|data ?cent(?:er|re) (?:capacity|lease)|"
                         r"ai capacity|\bhost\b"),
]
GAS = r"\bgas\b|natural gas|natgas|gas-fired"
# session 2258 (chain 159): the words that refine a deal the rule would call "other" (the second read's kind faults)
NUCLEAR = r"\bnuclear\b|\breactors?\b"
DC_ASSET = r"data ?cent(?:er|re)s?\b"
# what is sold to a data center rather than its capacity ("optical fiber for data centers", "local energy
# infrastructure for Louisiana data center")
DC_SUPPLY = r"\bfor\b|\benergy\b|\bpower\b|\bfib(?:er|re)\b|infrastructure|equipment|\bsuppl\w*|cool\w*"
FINANCE = r"\bcredit\b|backstop|\bloans?\b|\bbonds?\b|\bfinanc\w*|guarantee\w*"
STAKE = r"\bstakes?\b|\bacqui\w*|\bmerg\w*|\bdivest\w*|\bexits?\b|\bsells?\b|\bsale\b|\bbuys?\b"
GAS_BUILD = r"plant|turbines?|generat\w*|combined[- ]cycle|peakers?|power station|power (?:deal|push|project)"


def kind_of(d, text=""):
    """(kind, basis). The power kinds from the deal's own words (its asset, technology and evidence, and the story's
    text when given), then the model's kind when it is a form, then the form read from deal_type. Session 2258: a
    deal that would be "other" is read once more (other_of)."""
    k, basis = _kind_of(d, text)
    if k == "other":
        k2 = other_of(d)
        if k2:
            return k2
    return k, basis


def other_of(d):
    """(kind, basis) for a deal the rule would call "other", from its own words (asset and evidence), or None. In
    order: a lease of a data center is compute capacity (a lease is a lease, whatever funds the building); a credit
    backstop, credit support, loan, bond or guarantee is project finance where the deal names its asset, else capital;
    a data center as the asset of a deal of no other form is compute capacity; a stake bought, sold or exited is
    m_and_a."""
    t = d.get("deal_type") or ""
    asset = plain(d.get("asset"))
    own = plain(" ".join(str(d.get(f) or "") for f in ("asset", "evidence")))
    if t == "lease" and _words(DC_ASSET, own):
        return "compute_capacity", "a lease of a data center"
    m = re.search(FINANCE, own)
    if m:
        return ("project_finance", f"finance for a named asset: {m.group(0)}") if asset else ("capital", f"finance: {m.group(0)}")
    if t in ("other", "") and _words(DC_ASSET, asset) and not _words(DC_SUPPLY, asset) \
            and (d.get("buyer") or "").strip() and (d.get("seller") or "").strip():
        return "compute_capacity", "a data center between two named parties as the deal's asset"
    m = re.search(STAKE, own)
    if m and t in ("other", ""):
        return "m_and_a", f"the deal's words: {m.group(0)}"
    return None


def _kind_of(d, text=""):
    own = plain(" ".join(str(d.get(f) or "") for f in ("asset", "technology", "evidence")))
    words = own   # the deal's own words: a company's description in the summary is not the deal's kind (D011)
    t = d.get("deal_type") or ""
    for kid, pat in KIND_WORDS:
        if kid == "compute_capacity":
            if t in ("offtake", "lease", "other", "joint_venture", "ppa", "") and _words(pat, words) \
                    and not _words(r"\bpower purchase|\bppa\b|\bmw\b|\bgw\b", own):
                return kid, "the deal's words name cloud, GPU or computing capacity"
            continue
        if _words(pat, words):
            if kid == "storage" and t == "m_and_a":
                continue   # buying a storage developer is an acquisition
            return kid, f"the deal's words: {re.search(pat, words).group(0)}"
        if kid == "behind_the_meter" and t == "behind_the_meter":
            return kid, "deal_type behind_the_meter"
        if kid == "nuclear_restart_uprate" and t == "nuclear_restart":
            return kid, "deal_type nuclear_restart"
        if kid == "smr" and t == "smr":
            return kid, "deal_type smr"
    if _words(GAS, words) and _words(GAS_BUILD, words) and t not in ("m_and_a", "fuel_supply"):
        return "gas_buildout", "the words name gas and a plant, turbines or generation"
    tx = plain(text)
    m = re.search(KIND_WORDS[0][1], tx) if tx else None
    if m and _words(NUCLEAR, own) and t != "m_and_a":   # session 2258: "May Restart Abandoned US Nuclear Project"
        return "nuclear_restart_uprate", f"a nuclear deal whose stories say: {m.group(0)}"
    k = (d.get("kind") or "").strip()
    if k in KIND_IDS and k not in POWER_KINDS:
        return k, "the model's kind"
    form = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "m_and_a",
            "debt": "capital", "equity_raise": "capital", "tax_equity": "capital", "joint_venture": "capital",
            "lease": "other", "fuel_supply": "fuel_supply"}.get(t)
    if form:
        return form, f"deal_type {t}"
    return "other", "no kind's words and no form"


def grid_of(text):
    """(grid, the words) where the story names a US grid operator; ("", "") otherwise."""
    for name, pats in GRIDS.items():
        for p in pats:
            m = re.search(r"(?<![a-z])" + p + r"(?![a-z])", text)
            if m:
                return name, m.group(0)
    return "", ""


# Session 2257 (chain 159): a country as the story's words name it, by its name or its adjective. The second read
# found 12 of 106 deals with a place missed: two where the model gave "Indonesia" for the span "Indonesian", which the
# check refused (the span must name the country), and ten where the model left the country empty though the headline
# names it before the asset ("US Shale", "US power deal", "Venezuela's energy infrastructure").
COUNTRIES = {
    "United States": ["United States", "U.S.", "US", "USA", "America", "American"],
    "Canada": ["Canada", "Canadian"], "Mexico": ["Mexico", "Mexican"], "Brazil": ["Brazil", "Brazilian"],
    "Argentina": ["Argentina", "Argentine", "Argentinian"], "Chile": ["Chile", "Chilean"],
    "Colombia": ["Colombia", "Colombian"], "Venezuela": ["Venezuela", "Venezuelan"], "Guyana": ["Guyana", "Guyanese"],
    "United Kingdom": ["United Kingdom", "UK", "U.K.", "Britain", "British"], "Ireland": ["Ireland", "Irish"],
    "Norway": ["Norway", "Norwegian"], "Germany": ["Germany", "German"], "France": ["France", "French"],
    "Spain": ["Spain", "Spanish"], "Italy": ["Italy", "Italian"], "Netherlands": ["Netherlands", "Dutch"],
    "Poland": ["Poland", "Polish"], "Romania": ["Romania", "Romanian"], "Turkey": ["Turkey", "Turkish"],
    "Israel": ["Israel", "Israeli"], "Saudi Arabia": ["Saudi Arabia", "Saudi"], "Qatar": ["Qatar", "Qatari"],
    "United Arab Emirates": ["United Arab Emirates", "UAE", "Emirati"], "Egypt": ["Egypt", "Egyptian"],
    "Nigeria": ["Nigeria", "Nigerian"], "Mozambique": ["Mozambique", "Mozambican"], "South Africa": ["South Africa", "South African"],
    "India": ["India", "Indian"], "China": ["China", "Chinese"], "Japan": ["Japan", "Japanese"],
    "South Korea": ["South Korea", "Korea", "Korean"], "Taiwan": ["Taiwan", "Taiwanese"],
    "Vietnam": ["Vietnam", "Vietnamese"], "Indonesia": ["Indonesia", "Indonesian"], "Malaysia": ["Malaysia", "Malaysian"],
    "Philippines": ["Philippines", "Philippine"], "Australia": ["Australia", "Australian"],
    "New Zealand": ["New Zealand"], "Kazakhstan": ["Kazakhstan", "Kazakh"],
}
# the words that make a country word the asset's: what is bought, built or sold there
ASSET_WORDS = (r"(?:shale|power|nuclear|gas|oil|lng|utility|utilities|solar|wind|grid|pipelines?|electrical|electricity|"
               r"energy|fleet|plants?|projects?|assets?|offshore|onshore|blocks?|refiner(?:y|ies)|reactors?|storage|"
               r"batter(?:y|ies)|transmission|upstream|midstream|coal|hydro|geothermal|hydrogen|data ?cent(?:er|re)s?)")


def country_names(country):
    """The lower-case words that name a country (its name and adjectives), for the span check."""
    c0 = " ".join(str(country).split()).lower()
    for c, words in COUNTRIES.items():
        if c.lower() == c0 or any(w.lower() == c0 for w in words):
            return {w.lower() for w in words} | {c.lower()}
    return {c0}


def country_of(raw):
    """(country, span) where the story's own words name one country just before an asset word ("US shale",
    "Venezuela's energy infrastructure", "Indonesian offshore blocks"); ("", "") when none or more than one. Read on
    the text as written (not lower-cased), so the pronoun "us" is never the United States; a country named only as a
    party's home ("Japan's Jera") is not the asset's and is not taken. The United States by any of its words; another
    country only by its name ("Venezuela's energy", "Venezuela gas infrastructure"), since its adjective often
    describes a party ("the Italian oil and gas group" is Eni, not where its renewables arm's assets are); the model's
    own "Indonesian" is kept by the span check instead (country_names). Where the United States and one other country
    are both found, the other is taken: "US energy services firm Baker Hughes ... Venezuela's natural gas" describes
    the party by the one and the asset by the other."""
    raw = " ".join(str(raw or "").replace("’", "'").split())
    found = {}
    for c, words in COUNTRIES.items():
        forms = [(w, r"(?:'s)?") for w in words] if c == "United States" else [(words[0], r"(?:'s)?")]
        for w, poss in sorted(forms, key=lambda f: len(f[0]), reverse=True):
            pat = r"(?<![A-Za-z.])" + re.escape(w) + poss + r"\s+(?i:" + ASSET_WORDS + r")(?![A-Za-z])"
            m = re.search(pat, raw)
            if m:
                found.setdefault(c, m.group(0))
                break
    if len(found) == 2 and "United States" in found:
        found.pop("United States")
    if len(found) == 1:
        return next(iter(found.items()))
    return "", ""


def ai_of(d, text):
    """(ai_power, basis) by the rule: a named AI party, or a datacenter load in the story's words."""
    names = [d.get("buyer"), d.get("seller")] + list(d.get("other_parties") or [])
    for n in names:
        p = plain(n)
        for a in AI_PARTIES:
            if re.search(r"(?<![a-z])" + re.escape(a) + r"(?![a-z])", p):
                return True, f"party {' '.join(str(n).split())}"
    m = DATACENTER_WORDS.search(text or "")
    if m:
        return True, f"datacenter load: {m.group(0)}"
    return False, ""


def stage_of(d, text):
    """(stage, span): the model's stage only when its span is in the story."""
    s = (d.get("stage") or "").strip()
    span = " ".join(str(d.get("stage_text") or "").split())
    if s in STAGE_IDS and in_text(span, text):
        return s, span
    return "", ""


def energy_price(unit):
    return bool(unit) and ENERGY_PRICE_UNIT.match(unit) is not None


def num(v):
    """A figure in plain digits, as a flag writes it: 50000, 4200000000, 1.5."""
    x = float(v)
    return str(int(x)) if x.is_integer() else f"{x:f}".rstrip("0").rstrip(".")


def flags_of(row):
    out = []
    for f, b in BOUNDS.items():
        v = row.get(f)
        try:
            if v not in (None, "") and float(v) > b:
                out.append(f"{f} {num(v)} above the bound {num(b)}")
        except (TypeError, ValueError):
            pass
    return out


def named_party(d, text=""):
    """A deal is kept only where the story names a party to it: the buyer, the seller, a partner of a joint venture
    (other_parties, as the model gives them), or, for an acquisition, the company or asset sold ("Oryx Energies Sold
    for About $1 Billion")."""
    if any((d.get(r) or "").strip() for r in ("buyer", "seller")):
        return True
    t = plain(text)
    if any(plain(p) and plain(p) in t for p in d.get("other_parties") or []):
        return True
    asset = plain(d.get("asset"))
    return d.get("deal_type") == "m_and_a" and bool(asset) and asset in t and len(asset.split()) <= 6


def finish(d, text, vals, evidence):
    """The new fields of one deal the extractor keeps. d is the model's deal (after the party checks), text the plain
    text of its cluster, vals the checked numbers, evidence the verified sentence. Returns (fields, notes)."""
    notes = []
    kind, kind_basis = kind_of({**d, "evidence": evidence}, text)
    stage, stage_text = stage_of(d, text)
    if d.get("stage") and not stage:
        notes.append(f"stage {d.get('stage')!r}: span {d.get('stage_text')!r} not in the story, not kept")
    if not stage:   # session 2259: the deal's own words, where the model gave no stage
        stage, stage_text = stage_from_words(evidence)
    grid, _ = grid_of(text)
    ai, ai_basis = ai_of(d, text)
    if bool(d.get("ai_power")) != ai:
        notes.append(f"ai_power {bool(d.get('ai_power'))} from the model; the rule says {ai} ({ai_basis or 'no AI party or datacenter load'})")
    basis = " ".join(str(d.get("confidence_basis") or "").split())
    if basis and not in_text(basis, text):
        basis = ""
    spans = "; ".join(f"{f}: {' '.join(str(d.get(t) or '').split())}" for f, t in
                      (("mw", "mw_text"), ("mwh", "mwh_text"), ("dollars", "dollars_text"), ("price", "price_text"),
                       ("term_years", "term_text")) if vals.get(f if f != "price" else "price_value") is not None)
    row = {"kind": kind, "kind_basis": kind_basis, "stage": stage, "grid": grid,
           "usd": vals.get("dollars"), "usd_per_mwh": None, "ai_power": ai, "ai_power_basis": ai_basis,
           "fields_version": VERSION, "status_history": "",
           # to energy_deals_evidence (internal): the story's own words
           "stage_text": stage_text, "confidence_basis": basis, "spans": spans}
    flags = flags_of({"mw": vals.get("mw"), "mwh": vals.get("mwh"), "usd": vals.get("dollars"),
                      "term_years": vals.get("term_years")})
    row["flags"] = "; ".join(flags)
    return row, notes


def upgrade(row):
    """The new fields of a row extracted before session 2232, read from its own stored values: no model, nothing
    guessed (stage, grid and the bases stay empty: they need the story's spans). ai_power is left as extracted."""
    out = dict(row)
    if (out.get("fields_version") or "") != "":
        return out
    k, kb = kind_of(out)   # from the row's asset, technology and deal_type
    out.update(kind=k, kind_basis=kb, stage="", grid="", usd=out.get("dollars", ""),
               usd_per_mwh=out.get("price", ""), ai_power_basis="", flags="; ".join(flags_of({"mw": out.get("mw"), "mwh": out.get("mwh"),
                                                              "usd": out.get("dollars"), "term_years": out.get("term_years")})),
               fields_version="upgraded")
    return out
