#!/usr/bin/env python3
"""The parties of a deal, and when two extracted deals are one: the rules warehouse/deals/extract.py applies in code.

Energy Research Warehouse (ERW), session 531 (the Roundup audit's fix 8, docs/reviews/roundup-audit-2026-10-21.md).

Where the second row came from. The daily extraction sends only the stories it has not checked, so an event reported
over several days is sent again each day: the later stories of the same cluster, or a cluster of their own. The only
guard against a second row was the model's same_as, a choice from a reference list of earlier deals, and it missed
twice in the audit's weeks: the Vistra loan (2 October, "US" lends USD 4 billion, a cluster of one Bloomberg story; 5 to
6 October, "Department of Energy" lends USD 4.2 billion, a cluster of six) and the Amazon and Constellation PPA (30
September to 5 October; then on 7 October the Google and Constellation cluster's story "Constellation Energy has signed
20-year power purchase agreements with both Google and Amazon in the last week" made a second Amazon row, "nuclear
expansions"). Both tables, energy_deals and its evidence, are what the tracker (/deals) and the Roundup read.

The rules, all in code, no model and no request:

  same_deal(a, b)   one deal across days and weeks: the same deal_type, the same two parties (buyer and seller, in
                    either order: a name is the same party when one is the other with words added, "Constellation" and
                    "Constellation Energy"; the US government is one party whatever the story calls it, "US", "DOE",
                    "Department of Energy"), dated within WINDOW_DAYS of each other, assets that share a word when both
                    are named, and sums within DOLLAR_RATIO of each other when both are stated.
  find_same(d, deals)  the earlier deal a new one is, by same_deal, the nearest in date; None when there is none.
  fault(d, text)    why an extracted deal is not a transaction between two parties, or None: both parties are
                    governments (a country "buys" from a country: the story is policy, as "Trump says Russia to supply
                    diesel to US" is). Such a deal is not kept.
  unnamed(d, text)  the buyer or seller the story's words do not name ("investors" for an equity raise whose story
                    names none): that party is not kept, the deal is.

COUNTRIES and PUBLIC_BODIES were the company seeder's (warehouse/companies/seed_from_deals.py, session 28), which now
imports them from here so that the two read one list.
"""

import datetime as dt
import re

WINDOW_DAYS = 30      # the audit's repeats were 3 and 6 days apart; session 113's folded pairs 0 and 10
DOLLAR_RATIO = 1.25   # USD 4.0 and 4.2 billion are one loan; USD 200 and 15 billion (session 113, doubtful) are not

# Session 28: parties that are not company names (moved here from warehouse/companies/seed_from_deals.py, session 531)
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

US_ALIASES = {"us", "u s", "usa", "u s a", "united states", "united states of america", "america", "the us",
              "the united states"}
# the US government, whatever a story calls it: one party for same_deal
US_BODY = re.compile(
    r"^(?:the\s+)?(?:(?:us|u\s?s|united states|american|federal)\s+)?(?:"
    r"government|administration|federal government|department of energy|energy department|doe|"
    r"department of (?:defense|war|the treasury|commerce|the interior)|pentagon|treasury|white house|"
    r"loan programs office|lpo|office of energy dominance financing|exim(?: bank)?|export import bank|"
    r"army|navy|air force|military|dod|congress|federal reserve|fed|nrc|ferc|epa|blm)$")
SUFFIX = re.compile(r"\b(inc|llc|ltd|corp|corporation|co|company|plc|lp|sa|ag|nv|se|asa|gmbh|limited|holdings?|group)\b")
STOP = {"the", "a", "an", "of", "and", "for", "to", "in", "at", "on", "its", "new", "plant", "plants", "project",
        "projects", "unit", "units", "stake", "assets", "asset", "company", "deal", "power", "energy", "facility",
        "facilities", "portfolio", "business"}


def plain(s):
    """Lower case, no parentheses, punctuation or repeated spaces."""
    s = re.sub(r"\(.*?\)", " ", str(s or "").lower().replace("’", "'"))
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def government(name):
    """The government a party is, "us" or the country's name, or None for a company or a person."""
    p = plain(name)
    if not p:
        return None
    if p in US_ALIASES or US_BODY.match(p):
        return "us"
    low = str(name).strip().lower().rstrip(".")
    if low in COUNTRIES or p in COUNTRIES:
        return "us" if (low in {"us", "u.s.", "usa", "united states"} or p in US_ALIASES) else p
    if low in PUBLIC_BODIES:
        return "uk" if low == "british nuclear fund" else "us"
    m = re.match(r"^(?:the\s+)?(.+?)\s+government$", p)
    if m and (m.group(1) in COUNTRIES or m.group(1) in US_ALIASES):
        return "us" if m.group(1) in US_ALIASES else m.group(1)
    return None


def party_tokens(name):
    return SUFFIX.sub(" ", plain(name)).split()


def same_party(a, b):
    """True when two names are one party: the same government, or one name the other with words added after it."""
    ga, gb = government(a), government(b)
    if ga or gb:
        return ga is not None and ga == gb
    ta, tb = party_tokens(a), party_tokens(b)
    if not ta or not tb:
        return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if all(t in STOP for t in short):
        return False   # "Energy" is not "Energy Transfer"
    return long_[:len(short)] == short


def _date(v):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(v or ""))
    if not m:
        return None
    return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _num(v):
    try:
        x = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def asset_words(s):
    return {w for w in plain(s).split() if len(w) > 2 and w not in STOP}


def same_deal(a, b, window_days=WINDOW_DAYS):
    """True when two extracted deals (dicts with deal_type, buyer, seller, asset, dollars, event_date) are one."""
    if (a.get("deal_type") or "") != (b.get("deal_type") or "") or not a.get("deal_type"):
        return False
    ab, as_, bb, bs = (a.get("buyer") or ""), (a.get("seller") or ""), (b.get("buyer") or ""), (b.get("seller") or "")
    if not (ab and as_ and bb and bs):
        return False
    if not ((same_party(ab, bb) and same_party(as_, bs)) or (same_party(ab, bs) and same_party(as_, bb))):
        return False
    da, db = _date(a.get("event_date")), _date(b.get("event_date"))
    if da is None or db is None or abs((da - db).days) > window_days:
        return False
    wa, wb = asset_words(a.get("asset")), asset_words(b.get("asset"))
    if wa and wb and not (wa & wb):
        return False
    xa, xb = _num(a.get("dollars")), _num(b.get("dollars"))
    if xa and xb and max(xa, xb) / min(xa, xb) > DOLLAR_RATIO:
        return False
    return True


def find_same(d, deals, window_days=WINDOW_DAYS):
    """The event_id of the earlier deal that d is (same_deal), the nearest in date; None when there is none."""
    dd = _date(d.get("event_date"))
    best = None
    for row in deals:
        if row.get("event_id") == d.get("event_id") or not same_deal(d, row, window_days):
            continue
        gap = abs((_date(row.get("event_date")) - dd).days)
        if best is None or gap < best[0] or (gap == best[0] and row["event_id"] < best[1]):
            best = (gap, row["event_id"])
    return best[1] if best else None


def named(name, text):
    """True when the story's words (plain text of its titles and summaries) name the party."""
    t = " " + plain(text) + " "
    p = plain(name)
    if not p:
        return False
    if f" {p} " in t:
        return True
    toks = party_tokens(name)
    if toks and f" {' '.join(toks)} " in t:
        return True
    if government(name) == "us":
        return any(f" {w} " in t for w in ("us", "u s", "usa", "united states", "america", "american", "doe",
                                           "department of energy", "energy department", "federal", "pentagon",
                                           "trump", "washington", "white house", "administration", "government"))
    if toks and len(toks[0]) > 2 and f" {toks[0]} " in t:
        return True   # "Vistra" for "Vistra Corp's", "Constellation" for "Constellation Energy Group"
    return False


def fault(d, text):
    """Why an extracted deal is not a transaction between two parties, or None (session 531): both parties are
    governments, a country "buying" from a country, which the stories held tell as policy, talks or a memorandum."""
    buyer, seller = (d.get("buyer") or "").strip(), (d.get("seller") or "").strip()
    if buyer and seller and government(buyer) and government(seller):
        return f"buyer {buyer!r} and seller {seller!r} are both governments: not a transaction between companies"
    return None


def unnamed(d, text):
    """The roles ("buyer", "seller") whose party the story's words do not name: such a party is not kept, as a number
    without its span is not (session 16's ruling: empty is the correct answer)."""
    return [role for role in ("buyer", "seller") if (d.get(role) or "").strip() and not named(d[role], text)]
