#!/usr/bin/env python3
"""Rules in motion for large loads: the site's file for the block in "How soon" on /cost-of-power (session 154).

Energy Research Warehouse (ERW). No warehouse table is written, no request is made and nothing is loaded: this reads
tables already built and writes one file, site/data/datacenter/rules.json, whole, by rename. Method:
docs/methods/datacenter_cost.md, section "Rules in motion".

    python warehouse/derived/rules_in_motion.py --in-dir TRIAL --in-dir C:/.../warehouse/output
    python warehouse/derived/rules_in_motion.py --in-dir TRIAL --in-dir MAIN --out-dir DIR      # a trial: DIR/rules.json
    python warehouse/derived/rules_in_motion.py --ten DIR                # also the ten rules of the month (ten.json)

Tables read (the first --in-dir that holds a table wins; a table none holds is left out and named in the file):
    policy_actions, policy_action_tags, policy_reads      the federal actions held, their tags and their reads
    large_load_rules, large_load_rule_reads               the proceedings and orders of FERC and ten state commissions
                                                          (warehouse/connectors/large_load_rules.py) and the model's
                                                          one-line reads (warehouse/policy/rule_reads.py)

What is "in motion": a proceeding whose status class is open; an order or rule dated in the last 12 months; a tagged
federal action held of the last 12 months.

Which grid sees which action: an action whose own words name a grid operator is under that operator; a state
commission's action is under the operators that serve that state's utilities (STATE_GRIDS, written down below with its
source); a federal action that names no operator is in a group of its own, "Federal, all grids". MISO's block holds
the words "paused while terms are reviewed" and no row. Georgia, Arizona and Oregon have no grid on the page: their
actions are in the table and not in the file.

Never in the file: a row of a table whose license is internal; anything municipal (a row whose title, sentence or
read holds one of MUNICIPAL_WORDS is kept out and counted); a read line a model did not write; a filled field.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE_FILE = os.path.join(ROOT, "site", "data", "datacenter", "rules.json")
TERMS_FILE = os.path.join(ROOT, "warehouse", "config", "large_load_rule_terms.json")
WINDOW_MONTHS = 12
GRIDS = ["ercot", "pjm", "miso", "caiso", "nyiso", "isone", "spp"]
MISO_WORDS = "paused while terms are reviewed"
# The names by which a document's own words name a grid operator (whole words, any case).
OPERATOR_WORDS = {
    "ercot": ["ERCOT", "Electric Reliability Council of Texas"],
    "pjm": ["PJM"],
    "miso": ["MISO", "Midcontinent Independent System Operator"],
    "caiso": ["CAISO", "California Independent System Operator", "California ISO"],
    "nyiso": ["NYISO", "New York Independent System Operator", "New York ISO"],
    "isone": ["ISO-NE", "ISO New England"],
    "spp": ["SPP", "Southwest Power Pool"],
}
GRID_NAMES = {"ercot": "ERCOT", "pjm": "PJM", "miso": "MISO", "caiso": "CAISO", "nyiso": "NYISO", "isone": "ISO-NE",
              "spp": "SPP"}
# Which operator serves which state's utilities, for the ten states whose commissions were read. Stated plainly as
# common knowledge of the US power system, the states listed (no federal table of it is cited in this repository):
# the operators' own membership is public (each names its transmission owners), and the method note repeats this list.
# A state with no organized market operator on the page has an empty list: its actions are in the table, not the file.
STATE_GRIDS = {
    "TX": (["ercot"], "The Texas commission regulates the ERCOT region, where most of the state's load is served; the "
                      "parts of Texas in SPP and MISO see a Texas action only when its own words name them."),
    "VA": (["pjm"], "Virginia's investor-owned utilities (Dominion Energy Virginia, Appalachian Power) are in PJM."),
    "OH": (["pjm"], "Ohio's utilities (AEP Ohio, FirstEnergy's Ohio companies, AES Ohio, Duke Energy Ohio) are in PJM."),
    "PA": (["pjm"], "Pennsylvania's utilities (PECO, PPL Electric, FirstEnergy's Pennsylvania company, Duquesne Light) are in PJM."),
    "IL": (["pjm", "miso"], "Illinois is served by PJM in the north (Commonwealth Edison) and MISO elsewhere (Ameren Illinois)."),
    "IN": (["pjm", "miso"], "Indiana is served by PJM (Indiana Michigan Power) and by MISO (the state's other utilities)."),
    "CA": (["caiso"], "California's investor-owned utilities (PG&E, Southern California Edison, SDG&E) are in CAISO."),
    "GA": ([], "Georgia's utilities are in no organized market: no grid on the page."),
    "AZ": ([], "Arizona's utilities are in no organized market operator's footprint: no grid on the page."),
    "OR": ([], "Oregon's utilities are in no organized market operator's footprint: no grid on the page."),
}
# The block never shows these words (session 154: nothing municipal). A row holding one is kept out and counted.
MUNICIPAL_WORDS = ["zoning", "permit", "city council", "county board"]
AGENCY_NAMES = {"FERC": "Federal Energy Regulatory Commission", "DOE": "Department of Energy",
                "EPA": "Environmental Protection Agency", "NRC": "Nuclear Regulatory Commission",
                "BLM": "Bureau of Land Management", "Interior": "Department of the Interior"}
FEDERAL = list(AGENCY_NAMES)
TAG_TOPICS = {"large_load": "large loads", "interconnection": "interconnection",
              "transmission_cost": "transmission cost", "tax_credit": "tax credits"}
# The status class of a held federal action, from its type alone (the Register gives no docket status).
ACTION_CLASS = {"rule": "decided", "proposed_rule": "open", "notice": "not stated", "press_release": "not stated"}
READ_FROM_HELD = ("the action's own text in the Federal Register or the agency's release; kept only where its "
                  "supporting quotations were found word for word in that text (policy_reads)")


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = []
        for ln in f:
            if not ln.startswith("#"):
                break
            head.append(ln[1:].strip())
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False), head


def find(name, dirs):
    for d in dirs:
        p = os.path.join(d, name + ".csv")
        if os.path.exists(p):
            return p
    return None


def license_of(head):
    """'public' or 'internal', from the table's header (the line that states its License)."""
    for h in head:
        m = re.search(r"License:\s*(public|internal)", h)
        if m:
            return m.group(1)
    return "internal"  # a table that does not say is not shown


def operators_named(text):
    """The grids whose operator the text names, in GRIDS order."""
    out = []
    for g in GRIDS:
        for w in OPERATOR_WORDS[g]:
            if re.search(r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])", text or "", flags=re.I if " " in w else 0):
                out.append(g)
                break
    return out


def months_back(day, months):
    y, m = day.year, day.month - months
    while m <= 0:
        y, m = y - 1, m + 12
    d = min(day.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return dt.date(y, m, d)


def municipal(row):
    text = " ".join(str(row.get(k) or "") for k in ("title", "sentence", "read", "status_as_worded")).lower()
    return [w for w in MUNICIPAL_WORDS if w in text]


def sentence_of(text, term):
    """The sentence of an abstract that holds the term (the abstract's own words), else ''."""
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", text or ""):
        if re.search(re.escape(term).replace(r"\ ", r"[\s-]+"), s, flags=re.I):
            return s.strip()
    return ""


def docket_words(row):
    d = re.sub(r"\bDocket Nos?\.\s*", "", row.get("docket", "") or "").strip()
    d = d.split(";")[0].strip()
    if d:
        return d
    if row.get("fr_document_number"):
        return "FR Doc. " + row["fr_document_number"]
    return ""


def held_rows(dirs, cutoff, notes):
    """The tagged federal actions held of the last 12 months, as ROWs; (rows, counted-out reasons)."""
    pa, pt = find("policy_actions", dirs), find("policy_action_tags", dirs)
    if not pa or not pt:
        notes.append("policy_actions or policy_action_tags is not held: no federal action held is in the file")
        return [], {}
    acts, head = read_events(pa)
    tags, thead = read_events(pt)
    out, off = [], {}
    if license_of(head) != "public" or license_of(thead) != "public":
        notes.append("policy_actions or policy_action_tags is internal: none of its rows is in the file")
        return [], {"internal table": int(tags["action_event_id"].nunique())}
    reads = {}
    pr = find("policy_reads", dirs)
    if pr:
        r, rhead = read_events(pr)
        if license_of(rhead) == "public":
            reads = {x["action_event_id"]: x for x in r.to_dict("records") if x["plain_read"].strip()}
    extra = {}
    er = find("large_load_rule_reads", dirs)
    if er:
        r, rhead = read_events(er)
        if license_of(rhead) == "public":
            extra = {x["rule_event_id"]: x for x in r.to_dict("records") if x["read"].strip()}
    by = acts.set_index("event_id")
    for aid, g in tags.groupby("action_event_id", sort=False):
        a = by.loc[aid].to_dict()
        a["event_id"] = aid
        if a["agency"] not in FEDERAL:
            off["a state commission's news release held (in the tags table; the block shows a state's dockets, not its releases)"] = \
                off.get("a state commission's news release held (in the tags table; the block shows a state's dockets, not its releases)", 0) + 1
            continue
        if a["event_date"][:10] < cutoff.isoformat():
            off["older than 12 months"] = off.get("older than 12 months", 0) + 1
            continue
        first = g.iloc[0]
        sent, sfrom = "", "title"
        if first["matched_field"] == "abstract":
            sent, sfrom = sentence_of(a["abstract"], first["matched_term"]), "abstract"
        if not sent:
            sent, sfrom = a["title"], "title"
        rd = reads.get(aid)
        ex = extra.get(aid)
        row = {
            "id": aid, "date": a["event_date"][:10], "regulator": AGENCY_NAMES[a["agency"]], "jurisdiction": "federal",
            "state": "", "docket": docket_words(a), "title": a["title"], "row_kind": "federal action",
            "topic": "; ".join(TAG_TOPICS[t] for t in g["tag"]), "tags": list(g["tag"]),
            "status_as_worded": a["status"] if a["status"] not in ("", "news release") else "",
            "status_class": ACTION_CLASS.get(a["action_type"], "not stated"), "url": a["source_url"], "page": None,
            "sentence": sent, "sentence_from": sfrom,
            "read": rd["plain_read"] if rd else (ex["read"] if ex else None),
            "read_by": "model" if (rd or ex) else None,
            "read_model": rd["model_id"] if rd else (ex["model_id"] if ex else None),
            "read_from": READ_FROM_HELD if rd else (ex["read_from"] if ex else None),
            "named": operators_named(a["title"] + " " + a["abstract"]),
        }
        out.append(row)
    return out, off


def table_rows(dirs, cutoff, notes):
    """The proceedings and orders in motion, as ROWs; (rows, counted-out reasons, the regulators with a row)."""
    p = find("large_load_rules", dirs)
    if not p:
        notes.append("large_load_rules is not built yet: the file holds the federal actions held only")
        return [], {}
    t, head = read_events(p)
    if license_of(head) != "public":
        notes.append("large_load_rules is internal: none of its rows is in the file")
        return [], {"internal table": len(t)}
    reads = {}
    rp = find("large_load_rule_reads", dirs)
    if rp:
        r, rhead = read_events(rp)
        if license_of(rhead) == "public":
            reads = {x["rule_event_id"]: x for x in r.to_dict("records") if x["read"].strip()}
    out, off = [], {}
    for a in t.to_dict("records"):
        kind, cls, day = a["row_kind"], a["status_class"], a["event_date"][:10]
        moving = (kind == "proceeding" and cls == "open") or (kind == "order" and day >= cutoff.isoformat())
        if not moving:
            why = "a proceeding whose status class is not open" if kind == "proceeding" else "an order older than 12 months"
            off[why] = off.get(why, 0) + 1
            continue
        rd = reads.get(a["event_id"])
        named = [g for g in GRIDS if GRID_NAMES[g] in [x.strip() for x in a["grids"].split(";")]]
        for g in operators_named(" ".join([a["proceeding_title"], a["document_title"], a["sentence"]])):
            if g not in named:
                named.append(g)
        out.append({
            "id": a["event_id"], "date": day, "regulator": a["regulator"], "jurisdiction": a["jurisdiction"],
            "state": a["state"], "docket": a["docket_number"], "title": a["document_title"] or a["proceeding_title"],
            "row_kind": kind, "topic": a["topic"].replace(";", "; "), "tags": [],
            "status_as_worded": a["status_as_worded"], "status_class": cls, "url": a["source_url"],
            "page": int(a["page"]) if a["page"].strip().isdigit() else None, "sentence": a["sentence"],
            "sentence_from": "document",
            "read": rd["read"] if rd else None, "read_by": "model" if rd else None,
            "read_model": rd["model_id"] if rd else None, "read_from": rd["read_from"] if rd else None,
            "named": named,
        })
    return out, off


def place(rows):
    """{grid: [rows]}, the federal group, and the rows with no grid on the page, by the mapping above."""
    grids = {g: [] for g in GRIDS}
    federal, nowhere = [], []
    for r in rows:
        named = r.pop("named")
        if r["jurisdiction"] == "state":
            base, why = STATE_GRIDS.get(r["state"], ([], f"{r['state']}: no mapping written for this state"))
            where = list(dict.fromkeys(list(base) + named))
            if not where:
                nowhere.append((r, why))
                continue
            for g in where:
                extra = "" if g in base else f" Its own words name {GRID_NAMES[g]}."
                grids[g].append(dict(r, why_here=(why + extra).strip()))
        elif named:
            for g in named:
                grids[g].append(dict(r, why_here=f"A federal action whose own words name {GRID_NAMES[g]}."))
        else:
            federal.append(dict(r, why_here="A federal action that names no grid operator: it is under every grid."))
    return grids, federal, nowhere


def order(rows):
    return sorted(rows, key=lambda r: (r["date"], r["id"]), reverse=True)


def build(dirs, today):
    cutoff = months_back(today, WINDOW_MONTHS)
    notes, off = [], {}
    rows = []
    for fn in (table_rows, held_rows):
        got, out = fn(dirs, cutoff, notes)
        rows += got
        for k, v in out.items():
            off[k] = off.get(k, 0) + v
    seen, kept = set(), []
    for r in rows:
        words = municipal(r)
        if words:
            k = "a row that holds a word the block never shows (" + ", ".join(MUNICIPAL_WORDS) + "): in the table, not in the file"
            off[k] = off.get(k, 0) + 1
            continue
        if r["url"] + "|" + r["row_kind"] + "|" + r["docket"] in seen:
            continue
        seen.add(r["url"] + "|" + r["row_kind"] + "|" + r["docket"])
        kept.append(r)
    grids, federal, nowhere = place(kept)
    for r, why in nowhere:
        k = f"{r['state']}: no grid on the page"
        off[k] = off.get(k, 0) + 1
    miso_rows = len(grids["miso"])
    if miso_rows:
        off["under MISO only or also (MISO shows no row)"] = miso_rows
    out_grids = {}
    for g in GRIDS:
        if g == "miso":
            out_grids[g] = {"state": "paused", "words": MISO_WORDS, "rows": []}
        elif grids[g]:
            out_grids[g] = {"state": "shown", "rows": order(grids[g])}
        else:
            out_grids[g] = {"state": "none", "rows": [],
                            "why": "No proceeding or order held names this grid or comes from a state it serves; "
                                   "the federal actions that name no grid are in the group Federal, all grids."}
    sources = []
    if os.path.exists(TERMS_FILE):
        with open(TERMS_FILE, encoding="utf-8") as f:
            terms = json.load(f)["regulators"]
        shown = {r["regulator"] for g in out_grids.values() for r in g["rows"]} | {r["regulator"] for r in federal}
        for t in terms:
            if t["regulator"] in shown and t.get("terms_quote"):
                sources.append({"regulator": t["regulator"], "terms_url": t["terms_url"], "terms_quote": t["terms_quote"]})
    n_off = sum(off.values())
    why = "; ".join(f"{v} {k}" for k, v in sorted(off.items())) if off else "Every row in motion held is in the file."
    return {
        "built_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of": today.isoformat(), "window_months": WINDOW_MONTHS, "window_from": cutoff.isoformat(),
        "sources": sources, "grids": out_grids, "federal_all_grids": order(federal),
        "not_on_page": {"count": n_off, "why": why, "by_reason": dict(sorted(off.items()))},
        "notes": notes,
    }


# ---------------------------------------------------------------- the ten rules of the month (session 154, part e)
TEN = 10
TEN_PER_REGULATOR = 3
MONTH_DAYS = 31
DIRECTNESS = {"large-load interconnection": 3, "large-load tariff": 3, "transmission cost allocation": 2,
              "interconnection reform": 1}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
DATE_WORDS = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s+(\d{4})\b|\b(\d{4})-(\d{2})-(\d{2})\b")


def dates_in(text):
    """The dates a text writes ('October 20, 2026' or '2026-10-20'), as dates."""
    out = []
    for m in DATE_WORDS.finditer(text or ""):
        try:
            if m.group(1):
                out.append(dt.date(int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2))))
            else:
                out.append(dt.date(int(m.group(4)), int(m.group(5)), int(m.group(6))))
        except ValueError:
            pass
    return out


def ten_rules(dirs, today):
    """The ten rules a datacenter buyer most needs to know this month, by a stated rule (docs/accelerator/
    rules_in_motion.md says it in words). The pool: every row in motion of large_load_rules, whichever the state (a
    state with no grid on the page is in the pool). One row a docket: its newest row in motion. Ordered by
        1. this month first: the document is dated in the MONTH_DAYS days up to today, or its row states a date
           (a comment deadline, a hearing, an effective date, in notes or status_as_worded) in the MONTH_DAYS days
           from today;
        2. how directly it sets when or at what cost a large load is served: its topic's DIRECTNESS (interconnection
           standards and tariffs with minimum terms and collateral, then who pays for transmission, then
           interconnection reform at large); two topics add;
        3. breadth: a federal action before a state's; more grids named before fewer;
        4. the newest document first.
    At most TEN_PER_REGULATOR rows a regulator, so that ten rows are not one commission's docket list. Ten rows, no
    more. Returns (the rows, the size of the pool)."""
    p = find("large_load_rules", dirs)
    if not p:
        return [], 0
    t, head = read_events(p)
    lic = license_of(head)
    reads = {}
    rp = find("large_load_rule_reads", dirs)
    if rp:
        r, _ = read_events(rp)
        reads = {x["rule_event_id"]: x for x in r.to_dict("records") if x["read"].strip()}
    cutoff = months_back(today, WINDOW_MONTHS)
    month_from, month_to = today - dt.timedelta(days=MONTH_DAYS), today + dt.timedelta(days=MONTH_DAYS)
    pool = {}
    for a in t.to_dict("records"):
        kind, cls, day = a["row_kind"], a["status_class"], a["event_date"][:10]
        if not ((kind == "proceeding" and cls == "open") or (kind == "order" and day >= cutoff.isoformat())):
            continue
        key =(a["regulator"], re.sub(r"-\d{3}$", "", a["docket_number"]))
        if key not in pool or (day, a["event_id"]) > (pool[key]["event_date"][:10], pool[key]["event_id"]):
            pool[key] = a
    scored = []
    for a in pool.values():
        day = dt.date.fromisoformat(a["event_date"][:10])
        ahead = [d for d in dates_in(a["notes"] + " " + a["status_as_worded"]) if today <= d <= month_to]
        this_month = day >= month_from or bool(ahead)
        direct = sum(DIRECTNESS.get(x.strip(), 0) for x in a["topic"].split(";"))
        named = [g for g in a["grids"].split(";") if g.strip()]
        breadth = (2 if a["jurisdiction"] == "federal" else 0) + min(len(named), 3)
        scored.append(((1 if this_month else 0, direct, breadth, a["event_date"][:10], a["event_id"]), a, ahead))
    scored.sort(key=lambda x: x[0], reverse=True)
    out, per = [], {}
    for score, a, ahead in scored:
        if per.get(a["regulator"], 0) >= TEN_PER_REGULATOR:
            continue
        per[a["regulator"]] = per.get(a["regulator"], 0) + 1
        rd = reads.get(a["event_id"])
        out.append({"rank": len(out) + 1, "regulator": a["regulator"], "state": a["state"], "docket": a["docket_number"],
                    "date": a["event_date"][:10], "row_kind": a["row_kind"], "topic": a["topic"].replace(";", "; "),
                    "status_as_worded": a["status_as_worded"], "status_class": a["status_class"],
                    "title": a["document_title"] or a["proceeding_title"], "sentence": a["sentence"], "url": a["source_url"],
                    "page": a["page"], "grids": a["grids"], "read": rd["read"] if rd else None,
                    "read_model": rd["model_id"] if rd else None,
                    "this_month": bool(score[0]), "date_ahead": ahead[0].isoformat() if ahead else "",
                    "directness": score[1], "breadth": score[2], "table_license": lic, "id": a["event_id"]})
        if len(out) == TEN:
            break
    return out, len(pool)


def write_whole(path, obj):
    """The file written whole beside itself, then renamed over the old one (a reader never sees half a file)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, allow_nan=False)
        f.write("\n")
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the site's file of rules in motion for large loads")
    ap.add_argument("--in-dir", action="append", default=[], help="a directory of tables; may be given more than "
                    "once, the first that holds a table wins (default: warehouse/output)")
    ap.add_argument("--out-dir", help="a trial run: rules.json under this directory; nothing in site/data")
    ap.add_argument("--ten", help="also write the ten rules of the month to this file (JSON); no site file changes for it")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today, UTC): the day the 12 months are counted back from")
    args = ap.parse_args(argv)
    dirs = [os.path.abspath(d) for d in args.in_dir] or [os.path.join(ROOT, "warehouse", "output")]
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    obj = build(dirs, today)
    text = json.dumps(obj, ensure_ascii=False)
    if chr(0x2014) in text:
        raise RuntimeError("an em dash in the file: a row's own words hold one; it is not written")
    path = os.path.join(os.path.abspath(args.out_dir), "rules.json") if args.out_dir else SITE_FILE
    write_whole(path, obj)
    shown = {g: len(v["rows"]) for g, v in obj["grids"].items()}
    reads = sum(1 for v in obj["grids"].values() for r in v["rows"] if r["read"]) + sum(1 for r in obj["federal_all_grids"] if r["read"])
    print(f"rules.json: {path}")
    print(f"  rows by grid {shown}; Federal, all grids {len(obj['federal_all_grids'])}; row places with a read {reads}; "
          f"not on the page {obj['not_on_page']['count']}")
    for n in obj["notes"]:
        print(f"  note: {n}")
    if args.ten:
        rows, pool = ten_rules(dirs, today)
        write_whole(os.path.abspath(args.ten), {"as_of": today.isoformat(), "pool": pool, "rows": rows})
        print(f"  the ten: {len(rows)} rows from a pool of {pool} dockets in motion: {os.path.abspath(args.ten)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
