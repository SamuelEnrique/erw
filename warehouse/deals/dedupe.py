#!/usr/bin/env python3
"""One record a deal: the deal tracker's deduplication (session 2233, chain 156).

Energy Research Warehouse (ERW). `warehouse/deals/extract.py` sends the daily run's new stories only, so one deal
reported by several outlets over several days reaches it as several clusters on several days. Session 531 matched a new
deal to one held when both had the same type and the same two named parties within 30 days (`deal_parties.same_deal`).
The audit of 6 November 2026 (`docs/reviews/deals-audit-2026-11-06.md`, row A10) and the fixture of this session found
what that rule misses, each now a rule here:

1. **One party named on one side.** A story that names only one party ("Energy Department Announces $4.2 Billion
   Investment to Boost Nuclear Power") is the same deal as one held when that party is one of the held deal's two, the
   kind or the type is the same, a stated size (USD or MW) agrees within the tolerance, and the assets share a word or
   the MW agree. A size is required here: one party alone (the Department of Energy lends to many) is not enough.
2. **A name and its initials.** "AEP" and "American Electric Power" are one party (the initials of a name of two or
   more words), as "Constellation" and "Constellation Energy" were (`deal_parties.same_party`).
3. **A later stage, a longer window.** A story that moves a held deal to a later stage (signed to closed, announced to
   signed) is matched within `STAGE_WINDOW_DAYS` (365), not 30: an acquisition closes months after it is signed
   ("Williams Closes $5.5B Momentum Deal", 32 days after "Williams Agrees to Buy Momentum Midstream"). The two parties
   must both match, and a stated size must agree.
4. **The size within tolerance.** USD within a quarter of each other (`deal_parties.DOLLAR_RATIO`), MW within a tenth
   (`MW_RATIO`); a sum of another thing (a combined company's value, USD 58 billion against a USD 21.5 billion purchase)
   keeps two records apart.

When a story joins a record (`merge`): its link is added to the sources; the record's date becomes the earliest
first-reported date when the date is a publish date (`date_basis` first_story_published; a stated announced date is
kept); a later stage replaces the record's stage and status, and every change is kept in `status_history` ("date stage
(story)", oldest first); a figure the record lacks is filled, a figure it holds is never replaced. No model is called.
"""

import datetime as dt
import re

import deal_parties as dp
import deal_fields as fields  # noqa: E402  session 3233: by its own name (deal_fields.py)

STAGE_WINDOW_DAYS = 365
MW_RATIO = 1.10
STAGE_RANK = {s: i for i, s in enumerate(fields.STAGE_IDS)}   # rumored ... operating, then cancelled
STATUS_RANK = {"rumored": 0, "announced": 1, "signed": 2, "closed": 3, "cancelled": 9}


def _initials(name):
    words = [w for w in dp.plain(dp.SUFFIX.sub(" ", dp.plain(name))).split() if w not in ("the", "of", "and", "&")]
    return "".join(w[0] for w in words) if len(words) >= 2 else ""


def same_party(a, b):
    """deal_parties.same_party, and a name and its initials ("AEP", "American Electric Power")."""
    if not a or not b:
        return False
    if dp.same_party(a, b):
        return True
    pa, pb = dp.plain(a).replace(" ", ""), dp.plain(b).replace(" ", "")
    ia, ib = _initials(a), _initials(b)
    return (len(pa) >= 2 and pa == ib) or (len(pb) >= 2 and pb == ia)


def _date(v):
    try:
        return dt.date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def _num(v):
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def size_agrees(a, b):
    """(agrees, stated): agrees is False when a size both state differs beyond the tolerance; stated is True when at
    least one size both state agrees."""
    stated = False
    for f, ratio in (("dollars", dp.DOLLAR_RATIO), ("mw", MW_RATIO)):
        x, y = _num(a.get(f)), _num(b.get(f))
        if x and y:
            if max(x, y) / min(x, y) > ratio:
                return False, False
            stated = True
    return True, stated


def _kind(d):
    return d.get("kind") or fields.kind_of(d)[0]


def _rank(d):
    s = d.get("stage") or ""
    if s:
        return STAGE_RANK.get(s, -1)
    return {"rumored": 0, "announced": 1, "signed": 2, "closed": 4, "cancelled": 8}.get(d.get("status") or "", -1)


def same_record(new, held):
    """True when a new deal (the extractor's candidate) is the record held."""
    if dp.same_deal(new, held):
        return True
    if _kind(new) != _kind(held) and (new.get("deal_type") or "") != (held.get("deal_type") or ""):
        return False
    nb, ns = (new.get("buyer") or ""), (new.get("seller") or "")
    hb, hs = (held.get("buyer") or ""), (held.get("seller") or "")
    both = (same_party(nb, hb) and same_party(ns, hs)) or (same_party(nb, hs) and same_party(ns, hb))
    agrees, stated = size_agrees(new, held)
    if not agrees:
        return False
    dn, dh = _date(new.get("event_date")), _date(held.get("event_date"))
    if dn is None or dh is None:
        return False
    gap = abs((dn - dh).days)
    wa, wb = dp.asset_words(new.get("asset")), dp.asset_words(held.get("asset"))
    assets_ok = not (wa and wb) or bool(wa & wb)
    if both and assets_ok:
        if gap <= dp.WINDOW_DAYS:
            return True
        # rule 3: a later stage within a year, a size both state agreeing
        return gap <= STAGE_WINDOW_DAYS and stated and _rank(new) > _rank(held)
    # rule 1: one deal names one party only, it is one of the other's, and a stated size agrees; the assets share a word
    # or the two state the same MW (two outlets name one project two ways: "960-Megawatt Nuclear Project", "12-SMR plant")
    mw_a, mw_b = _num(new.get("mw")), _num(held.get("mw"))
    same_mw = bool(mw_a and mw_b and max(mw_a, mw_b) / min(mw_a, mw_b) <= MW_RATIO)
    if gap <= dp.WINDOW_DAYS and stated and (assets_ok or same_mw):
        pn, ph = [p for p in (nb, ns) if p], [p for p in (hb, hs) if p]
        for one, other in ((pn, ph), (ph, pn)):
            if len(one) == 1 and any(same_party(one[0], p) for p in other):
                return True
    return False


def find_record(new, held_rows):
    """The event_id of the record the new deal is, the nearest in date; None when there is none."""
    dn = _date(new.get("event_date"))
    best = None
    for row in held_rows:
        if row.get("event_id") == new.get("event_id") or not same_record(new, row):
            continue
        gap = abs((_date(row.get("event_date")) - dn).days)
        if best is None or gap < best[0] or (gap == best[0] and row["event_id"] < best[1]):
            best = (gap, row["event_id"])
    return best[1] if best else None


def history_entry(date, stage, story_id):
    return f"{str(date)[:10]} {stage} ({story_id})"


def merge(row, new, story_date, story_id):
    """Fold a new deal (its checked fields) into the record row, in place. Returns the changes, as words."""
    changes = []
    # the earliest first-reported date, when the date is a publish date
    if (row.get("date_basis") or "") != "stated" and story_date and str(story_date) < str(row.get("event_date") or "9"):
        changes.append(f"date {row.get('event_date', '')[:10]} to {str(story_date)[:10]} (earlier story)")
        row["event_date"] = story_date
    # a later stage replaces the record's, with its history
    old_rank, new_rank = _rank(row), _rank(new)
    hist = [h for h in (row.get("status_history") or "").split("; ") if h]
    if not hist and (row.get("stage") or row.get("status")):
        hist.append(history_entry(row.get("event_date"), row.get("stage") or row.get("status"), "first record"))
    if new_rank > old_rank and (new.get("stage") or new.get("status")):
        word = new.get("stage") or new.get("status")
        hist.append(history_entry(story_date, word, story_id))
        if new.get("stage"):
            row["stage"] = new["stage"]
        if new.get("status") and STATUS_RANK.get(new["status"], -1) > STATUS_RANK.get(row.get("status") or "", -1):
            row["status"] = new["status"]
        changes.append(f"stage {word} from {story_id}")
    row["status_history"] = "; ".join(hist)
    for f in ("mw", "mwh", "dollars", "price_value", "term_years", "state", "country", "grid", "usd", "usd_per_mwh"):
        if (row.get(f) or "") == "" and (new.get(f) or "") != "":
            row[f] = new[f]
            changes.append(f"{f} filled")
    if (row.get("dollars") or "") != "" and (row.get("usd") or "") == "":
        row["usd"] = row["dollars"]
    if (row.get("buyer") or "") == "" and new.get("buyer"):
        row["buyer"] = new["buyer"]
        changes.append("buyer filled")
    if (row.get("seller") or "") == "" and new.get("seller"):
        row["seller"] = new["seller"]
        changes.append("seller filled")
    # session 2260 (chain 159): a party the later story names joins the record ("Microsoft, Chevron and Engine No. 1
    # sign" folded into "Chevron, Microsoft Eye Massive Texas Power Project" had lost Engine No. 1)
    others = [p for p in str(row.get("other_parties") or "").split(";") if p.strip()]
    have = {" ".join(str(p).split()).lower() for p in [row.get("buyer"), row.get("seller")] + others if p}
    nw = new.get("other_parties") or []
    for p in (nw.split(";") if isinstance(nw, str) else nw):
        p = " ".join(str(p or "").split())
        if p and p.lower() not in have:
            others.append(p)
            have.add(p.lower())
            changes.append(f"party {p} added")
    if "other_parties" in row or others:
        row["other_parties"] = ";".join(others)
    if "parties" in row:   # buyer;seller;other_parties, as the extractor writes it
        row["parties"] = ";".join(p for p in [row.get("buyer"), row.get("seller")] + others if p)
    return changes
