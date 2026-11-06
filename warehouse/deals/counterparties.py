#!/usr/bin/env python3
"""The deal tracker's counterparties: one name a party, its parent, its EIA-861 utility number, and a directory.

Energy Research Warehouse (ERW), session 2234 (chain 156, `docs/reviews/deals-audit-2026-11-06.md` row A5). The
stored deals name a party as the outlet wrote it: "AEP" and "American Electric Power", "Constellation" and
"Constellation Energy", "Amazon" and "Amazon Web Services". This module gives every buyer and seller:

- **a canonical name** (`buyer_name`, `seller_name`): the spelling the deals use most for one company, where two
  spellings are the same company: the same words once suffixes ("Inc", "Corp", "Co") and punctuation are dropped, or
  one is the other with a company word added ("Energy", "Power", "Group"), or an alias of `aliases.yaml`;
- **a parent** (`buyer_parent`, `seller_parent`), a second field, never in place of the name: from `aliases.yaml`
  (each entry with the story that shows it), or where one name is another with a place or a business line added
  ("Duke Energy Florida", "Amazon Web Services"), the shorter name being a party of the deals itself;
- **an EIA-861 utility number** (`buyer_eia861`, `seller_eia861`) only where the canonical name is exactly one
  utility's name in `utility_service_territories` (EIA-861 2025, suffixes dropped on both sides) or an alias names the
  number; a name that is several utilities' (a holding company's subsidiaries share words) gets none.

The directory (`deal_counterparties`, the entities shape, the seed of the company database, tool 10): one row a
canonical name with its kind (utility where an EIA number is matched, ai_buyer for a party of `fields.AI_PARTIES`,
government, company), its parent, its spellings, its deals (as buyer, as seller, in all), the MW its deals state
summed with the count that state MW, and its first and last deal. Read from `energy_deals` (the folded pairs of
`duplicates.csv` once); no model; nothing inferred.

    python warehouse/deals/counterparties.py                # write warehouse/output/deal_counterparties.csv (data lock)
    python warehouse/deals/counterparties.py --out DIR      # write the directory elsewhere (no lock: outside output)
"""

import argparse
import datetime as dt
import os
import re
import sys

import pandas as pd


def _hdr(path):
    """The number of "#" header lines before a table's column row (iso_prices.header_rows: never comment="#")."""
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import deal_parties as dp  # noqa: E402
import fields  # noqa: E402

ALIASES = os.path.join(HERE, "aliases.yaml")
NAME = "deal_counterparties"
# a party field that holds a description, not a name (the audit's class 5): no directory row
DESCRIPTIONS = {"investors", "investor", "banks", "bank", "lenders", "lender", "shareholders", "management",
                "hyperscaler", "a hyperscaler", "us hyperscaler", "partners", "buyers", "bondholders", "creditors"}
# session 2250: a party field that describes a facility or a vehicle by its backer ("Meta-backed data centre",
# "Google-Linked Data Centers", "CoreWeave-tied data center", "Anthropic data centre backed by Google"): no row
DESCRIBED = re.compile(r"(?:-backed|-linked|-tied|\bbacked by\b)|\bdata ?cent(?:er|re)s?$", re.I)
# session 2250: the places a subsidiary's name may end with (a country or a region)
PLACES = sorted({c.title() for c in dp.COUNTRIES if len(c) > 3} | {"Asia Pacific", "Asia-Pacific", "Europe", "North America",
                 "Latin America", "Middle East", "Africa", "Americas", "UK", "US", "USA", "APAC", "EMEA"})
ROLE_COLS = ["buyer_name", "seller_name", "buyer_parent", "seller_parent", "buyer_eia861", "seller_eia861"]
COMPANY_WORDS = {"energy", "power", "group", "holdings", "holding", "partners", "corporation", "company", "co", "inc",
                 "resources", "international", "global", "the"}
STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
       "source", "source_url", "retrieved_at", "vintage"]
COLS = STD + ["kind", "parent", "eia861_utility_number", "spellings", "deals", "as_buyer", "as_seller", "mw_stated",
              "deals_with_mw", "ai_power_deals", "first_deal", "last_deal", "event_ids"]


def key(name):
    """The words of a name with suffixes and punctuation dropped: two names with one key are one spelling."""
    return " ".join(dp.party_tokens(name))


def load_aliases(path=ALIASES):
    """{key of an alias: entry}; an entry has name (canonical), and may have parent, eia861 and evidence."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    out = {}
    for e in doc.get("aliases", []):
        for a in [e["name"]] + list(e.get("aliases") or []):
            out[key(a)] = e
    return out


def territories_path():
    """utility_service_territories in this checkout, or in the main checkout beside a worktree (session 718's rule)."""
    main = os.path.join(os.path.dirname(ROOT), "erw")
    for base in dict.fromkeys([ROOT, main]):
        for p in (os.path.join(base, "warehouse", "output", "utility_service_territories.csv"),
                  os.path.join(base, "runs", "archive_restore", "utility_service_territories.csv")):
            if os.path.exists(p):
                return p
    return None


def load_utilities(path=None):
    """{key of a utility's name: set of EIA-861 utility numbers}, from utility_service_territories."""
    path = path or territories_path()
    if not path:
        return {}
    t = pd.read_csv(path, skiprows=_hdr(path), dtype=str, usecols=["name", "x_utility_number"]).dropna().drop_duplicates()
    out = {}
    for r in t.itertuples():
        out.setdefault(key(r.name), set()).add(r.x_utility_number)
    return out


def _extra(short, long_):
    """The words long_ adds after short (both keys), or None when long_ does not begin with short."""
    s, l = short.split(), long_.split()
    if len(s) >= len(l) or l[:len(s)] != s:
        return None
    return l[len(s):]


class Names:
    """Canonical names, parents and EIA numbers for a list of party spellings."""

    def __init__(self, spellings, aliases=None, utilities=None):
        self.aliases = load_aliases() if aliases is None else aliases
        self.utilities = load_utilities() if utilities is None else utilities
        counts = pd.Series([s for s in spellings if s and str(s).strip()]).value_counts()
        groups = {}   # key -> {spelling: count}
        for s, n in counts.items():
            k = key(s)
            if not k:
                continue
            a = self.aliases.get(k)
            if a:
                k = key(a["name"])
            groups.setdefault(k, {})
            groups[k][s] = groups[k].get(s, 0) + int(n)
        # one company spelled with a company word added: "Constellation" and "Constellation Energy"
        keys = sorted(groups, key=len)
        self.merged = {}
        for k in keys:
            for k2 in keys:
                ex = _extra(k, k2)
                if ex and all(w in COMPANY_WORDS for w in ex) and k2 in groups and k in groups and k2 not in self.merged:
                    for s, n in groups.pop(k2).items():
                        groups[k][s] = groups[k].get(s, 0) + n
                    self.merged[k2] = k
        self.groups = groups
        self.canon = {}
        for k, sp in groups.items():
            a = self.aliases.get(k)
            best = a["name"] if a else max(sp.items(), key=lambda x: (x[1], len(x[0]), x[0]))[0]   # a tie: the fuller name
            self.canon[k] = " ".join(str(best).split())

    def _k(self, s):
        k = key(s)
        a = self.aliases.get(k)
        if a:
            k = key(a["name"])
        return self.merged.get(k, k)

    def name(self, s):
        if not s or not str(s).strip():
            return ""
        if dp.government(s) == "us":
            return "US government"
        return self.canon.get(self._k(s), " ".join(str(s).split()))

    def parent(self, s):
        """The parent a party's own words or aliases.yaml show: "ADNOC's XRG", "Blackstone's QTS" (a possessive),
        "Amazon data center unit" (a unit, an arm, a subsidiary). A name that only begins like another ("Related
        Digital", "Golar LNG") gets none: two companies can share a first word."""
        if not s or not str(s).strip() or dp.government(s):
            return ""
        a = self.aliases.get(key(s)) or self.aliases.get(self._k(s))
        if a and a.get("parent"):
            return a["parent"]
        raw = " ".join(str(s).replace("’", "'").split())
        m = (re.match(r"^(.+?)'s?\s+\S", raw) or
             re.match(r"^(.+?)\s+(?:data cent(?:er|re)\s+|venture\s+|power\s+|renewables?\s+)?(?:unit|subsidiary|arm|division)$",
                      raw, re.I))
        if m and not re.search(r",| and ", m.group(1)):
            return self.name(m.group(1))
        # session 2250: a party of the deals followed by a place ("Chevron Australia", "ExxonMobil Asia Pacific"): the
        # subsidiary that runs the party's business there; the place must be a country or a region, the shorter name a
        # party the deals name themselves
        m = re.match(r"^(.+?)\s+(" + "|".join(sorted((re.escape(p) for p in PLACES), key=len, reverse=True)) + r")$", raw, re.I)
        if m and key(m.group(1)) in self.groups:
            return self.canon[key(m.group(1))]
        return ""

    def eia861(self, s):
        if not s or not str(s).strip() or dp.government(s):
            return ""
        a = self.aliases.get(key(s)) or self.aliases.get(self._k(s))
        if a and a.get("eia861"):
            return str(a["eia861"])
        nums = self.utilities.get(self._k(s)) or self.utilities.get(key(s))
        return next(iter(nums)) if nums and len(nums) == 1 else ""


def split(raw):
    """A party field that holds several parties ("Nvidia, Dell", "Apollo and Blackstone") as its parties; one party
    otherwise. Split only where every piece begins with a capital or a digit."""
    raw = " ".join(str(raw or "").split())
    parts = [x.strip() for x in re.split(r",\s*(?:and\s+)?|\s+and\s+|\s+&\s+", raw) if x.strip()]
    if len(parts) >= 2 and all(re.match(r"[A-Z0-9]", x) for x in parts):
        return parts
    return [raw] if raw else []


def annotate(deals, names=None):
    """The six role columns of every deal, from its buyer and seller (a frame, returned with the columns set)."""
    names = names or Names([p for x in list(deals["buyer"]) + list(deals["seller"]) for p in split(x)])
    out = deals.copy()
    for role in ("buyer", "seller"):
        out[f"{role}_name"] = ["; ".join(names.name(p) for p in split(x)) for x in out[role]]
        out[f"{role}_parent"] = ["; ".join(filter(None, (names.parent(p) for p in split(x)))) for x in out[role]]
        out[f"{role}_eia861"] = ["; ".join(filter(None, (names.eia861(p) for p in split(x)))) for x in out[role]]
    return out


def directory(deals, folded=(), names=None, run_id=""):
    """The directory frame (COLS) from the deals; the folded duplicates are counted once."""
    d = deals[~deals["event_id"].isin(set(folded))]
    names = names or Names([p for x in list(d["buyer"]) + list(d["seller"]) for p in split(x)])
    rows = {}
    for r in d.to_dict("records"):
        for role, raw in [(ro, p) for ro in ("buyer", "seller") for p in split(r.get(ro) or "")]:
            n = names.name(raw)
            if not n or dp.plain(raw) in DESCRIPTIONS or re.search(r"\b(?:owners|investors|startup|lenders|banks)$", dp.plain(raw)) \
                    or DESCRIBED.search(raw):
                continue
            e = rows.setdefault(n, {"spellings": set(), "ids": [], "as_buyer": 0, "as_seller": 0, "mw": 0.0,
                                    "with_mw": 0, "ai": 0, "dates": [], "raw": raw})
            e["spellings"].add(" ".join(str(raw).split()))
            if r["event_id"] in e["ids"]:
                continue
            e["ids"].append(r["event_id"])
            e[f"as_{role}"] += 1
            try:
                mw = float(r.get("mw") or "")
                e["mw"] += mw
                e["with_mw"] += 1
            except ValueError:
                pass
            e["ai"] += str(r.get("ai_power", "")).lower() == "true"
            e["dates"].append(str(r.get("event_date", ""))[:10])
            url = str(r.get("source_url") or "")
            if url.startswith("http") and (not e.get("url") or str(r.get("event_date", "")) < e["url_date"]):
                e["url"], e["url_date"] = url, str(r.get("event_date", ""))   # the earliest deal's first story
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for n, e in sorted(rows.items(), key=lambda x: (-len(x[1]["ids"]), x[0])):
        eia = names.eia861(e["raw"])
        gov = dp.government(e["raw"])
        ai, _ = fields.ai_of({"buyer": n}, "")
        kind = "government" if gov else "utility" if eia else "ai_buyer" if ai else "company"
        out.append({"entity_id": "counterparty:" + re.sub(r"[^a-z0-9]+", "_", key(n) or n.lower()).strip("_"),
                    "entity_type": "company", "name": n, "geo": "", "lat": "", "lon": "", "capacity_mw": "",
                    "status": "", "status_date": "", "operator": "", "source": "erw:energy_deals",
                    "source_url": e.get("url", ""), "retrieved_at": now, "vintage": run_id,
                    "kind": kind, "parent": names.parent(e["raw"]), "eia861_utility_number": eia,
                    "spellings": "; ".join(sorted(e["spellings"])), "deals": str(len(e["ids"])),
                    "as_buyer": str(e["as_buyer"]), "as_seller": str(e["as_seller"]),
                    "mw_stated": (f"{e['mw']:g}" if e["with_mw"] else ""), "deals_with_mw": str(e["with_mw"]),
                    "ai_power_deals": str(e["ai"]), "first_deal": min(e["dates"]), "last_deal": max(e["dates"]),
                    "event_ids": ";".join(e["ids"])})
    return pd.DataFrame(out, columns=COLS)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="", help="write the directory to this folder instead of warehouse/output")
    args = ap.parse_args(argv)
    import iso_prices as ip
    src = os.path.join(ip.OUT_DIR, "energy_deals.csv")
    deals = pd.read_csv(src, skiprows=_hdr(src), dtype=str, keep_default_na=False)
    reg = os.path.join(HERE, "duplicates.csv")
    folded = []
    if os.path.exists(reg):
        r = pd.read_csv(reg, dtype=str, keep_default_na=False)
        folded = list(r.loc[r["ruling"] == "fold", "duplicate_event_id"])
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    names = Names([p for x in list(deals["buyer"]) + list(deals["seller"]) for p in split(x)])
    out = directory(deals, folded, names, run_id)
    header = [
        "Energy Research Warehouse (ERW): the deal tracker's counterparties, one row a canonical name (the seed of the company database, tool 10)",
        "Shape: entities (docs/datastandard.md), entity_type company; derived from energy_deals by warehouse/deals/counterparties.py (session 2234); the folded duplicates of warehouse/deals/duplicates.csv counted once.",
        f"Retrieved: {run_id} (UTC) from warehouse/output/energy_deals.csv",
        "Columns: kind utility (an exact EIA-861 utility name, utility_service_territories), ai_buyer (fields.AI_PARTIES), government, company; parent from aliases.yaml or a shorter party name the longer begins with; mw_stated sums the MW the deals state, deals_with_mw counts them.",
        "License: as energy_deals (license needed since 2026-10-21): the names and counts are the ERW's own extraction from the news.",
        "Sources: energy_deals; EIA-861 2025 (utility_service_territories) for the utility numbers.",
    ]
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, NAME + ".csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            for h in header:
                f.write("# " + h + "\n")
            out.to_csv(f, index=False, lineterminator="\n")
        print(f"{path}: {len(out)} counterparties")
    else:
        log = ip.Log(os.path.join(ip.LOG_DIR, f"deal_counterparties_{run_id}.log"))
        ip.write_csv(out, NAME, header, log, cols=COLS, key=["entity_id"], time_col="retrieved_at")
        log.close()
    print(f"deal_counterparties: {len(out)} names from {len(deals)} deals; utilities {int((out['kind'] == 'utility').sum())}, "
          f"ai buyers {int((out['kind'] == 'ai_buyer').sum())}, with a parent {int((out['parent'] != '').sum())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
