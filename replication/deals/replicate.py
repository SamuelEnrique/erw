#!/usr/bin/env python3
"""ERW, the deal tracker (/deals, its views, and /deals/capital): the replication a reader can run (session 7404,
chain 303).

Written from the method note (docs/methods/deal_tracker.md) and the rows alone, not from the page's code: every count,
median, share and list of ten the views show is computed again here, in this file's own words, and set beside the
figure the page's own functions give on the same rows (site/scripts/deal-tracker-figures.mjs, run with node, or a file
of its output). A difference is inside the tolerance when it is at most half the last digit the page shows.

    python replication/deals/fetch_rows.py          # the rows, from the live set, into rows/ (not in git)
    python replication/deals/replicate.py           # N of N, or each difference named
    python replication/deals/replicate.py --write   # also writes page_figures.json and page_figures.csv
    python replication/deals/replicate.py --headline   # only the do-file's lines (replicate.do), from rows/deals_slim.csv

    --rows DIR      another folder of rows (default: this folder's rows/)
    --page FILE     the page's figures as a file (the JSON the node script prints) instead of running node
    --month YYYY-MM the month the page is drawn in (default: the month the rows were retrieved)

energy_deals is held ("license needed" since 21 October 2026), so the built page draws none of these figures to a
visitor; the page's figure here is what its functions compute on the rows, which is what it draws when the hold allows.
Exit 0 when every figure is inside its tolerance or its difference is one this file names (NAMED below), 1 when another
differs or a key is on one side only, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import json
import os
import re
import shutil
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")

# The note, section 6: the grid that serves most of a state; a state split between grids has none.
GRID_OF_STATE = {"TX": "ERCOT", "CA": "CAISO", "NY": "NYISO", **{s: "ISO-NE" for s in "CT ME MA NH RI VT".split()},
                 **{s: "PJM" for s in "PA NJ MD DE VA WV OH DC".split()}, **{s: "MISO" for s in "MN IA WI MI LA".split()},
                 **{s: "SPP" for s in "OK KS NE".split()}}
GRIDS = ["ERCOT", "CAISO", "PJM", "MISO", "SPP", "NYISO", "ISO-NE"]
# The note, section 2: the four types the panel names; every other type is "other". Tolling is a type no row has.
PANEL = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "acquisition", "tolling": "tolling"}
PANEL_ORDER = ["ppa", "offtake", "project_finance", "acquisition", "tolling", "other"]
# The note, section 2: a row extracted before the kinds existed takes its kind from its type.
KIND_OF_TYPE = {"ppa": "ppa", "offtake": "offtake", "project_finance": "project_finance", "m_and_a": "m_and_a", "debt": "capital", "equity_raise": "capital",
                "tax_equity": "capital", "joint_venture": "capital", "fuel_supply": "fuel_supply", "behind_the_meter": "behind_the_meter",
                "nuclear_restart": "nuclear_restart_uprate", "smr": "smr"}
KINDS = ["nuclear_restart_uprate", "smr", "behind_the_meter", "gas_buildout", "transmission", "storage", "compute_capacity", "ppa", "offtake", "project_finance",
         "m_and_a", "capital", "fuel_supply", "other"]
STAGES = ["rumored", "announced", "signed", "financed", "closed", "under_construction", "operating", "cancelled"]
STATUSES = ["rumored", "announced", "signed", "closed", "cancelled"]
SUPPLY_GROUPS = ["nuclear", "gas", "renewables_storage", "grid", "other"]

# A difference this file names instead of failing on: the key, and why the two sides are not the same thing.
NAMED = {
    "capital|n_rows": "the capital view's file (site/data/capital.json) carries the table's row count of the day it was built, 6 November 2026; "
                      "the replication counts the rows held now. The file is the data machine's to rebuild (deals faults row 24).",
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def num(v):
    if v is None or v == "":
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x and x not in (float("inf"), float("-inf")) else None


def js_round(x):
    """Round half up, as the page rounds a positive figure."""
    return int(x + 0.5)


def median3(xs):
    """A median needs three deals that state the figure."""
    return statistics.median(xs) if len(xs) >= 3 else None


class Deal:
    """One row of energy_deals, read as the note's sections 2 to 6 say."""

    def __init__(self, r):
        x = r.get("extra") or {}
        self.id = r["event_id"]
        self.date = r["event_date"][:10]
        self.month, self.year = self.date[:7], self.date[:4]
        self.quarter = f"{self.year}-Q{(int(self.date[5:7]) - 1) // 3 + 1}"
        self.type = x.get("deal_type") or ""
        self.panel = PANEL.get(self.type, "other")
        self.kind = x.get("kind") or KIND_OF_TYPE.get(self.type, "other")
        self.status = r.get("status") or ""
        self.stage = x.get("stage") or self.status
        self.buyer, self.seller = x.get("buyer") or "", x.get("seller") or ""
        self.others = [p.strip() for p in (x.get("other_parties") or "").split(";") if p.strip()]
        self.buyer_name, self.seller_name = x.get("buyer_name") or self.buyer, x.get("seller_name") or self.seller
        self.asset, self.technology = x.get("asset") or "", x.get("technology") or ""
        self.state = (x.get("state") or "").upper()
        # the tracker, the comparables and the AI view read the grid from the state alone (section 6); the table's own Grid
        # column reads a grid a story names first, which is in no keyed figure
        self.grid = GRID_OF_STATE.get(self.state, "")
        self.mw = num(r.get("mw"))
        self.usd_table = num(x.get("usd") if x.get("usd") not in (None, "") else x.get("dollars"))   # the table's column
        self.usd = num(x.get("dollars"))                                                            # the tracker's
        self.price = num(r.get("price"))                       # US dollars per MWh, the only unit a price is
        self.price_table = num(x.get("usd_per_mwh") if x.get("usd_per_mwh") not in (None, "") else r.get("price"))
        self.price_other, self.price_unit = num(x.get("price_value")), x.get("price_unit") or ""
        self.ai = str(x.get("ai_power") or "").lower() == "true"
        self.flags = [w for w in (x.get("flags") or "").split("; ") if w]
        self.sure = num(x.get("confidence"))
        self.storage = bool(re.search(r"batter|storage|\bbess\b", self.technology, re.I) or re.search(r"batter|energy storage|\bbess\b", self.asset, re.I))

    def tool6(self):
        """The four kinds master plan tool 6 names that the panel gathers under Other (section 2)."""
        text, out = f"{self.asset} | {self.technology}", []
        if self.type == "nuclear_restart" or re.search(r"\brestart|recommission|\breopen", text, re.I):
            out.append("nuclear_restart")
        if self.type == "smr" or re.search(r"\bsmrs?\b|small modular|micro-?reactor", text, re.I):
            out.append("smr")
        if (re.search(r"\bgas\b|natgas|natural gas", self.technology, re.I) and self.type not in ("m_and_a", "fuel_supply")
                and re.search(r"plant|turbine|generat|power station|peaker|combined[- ]cycle|\bccgt\b", self.asset, re.I)):
            out.append("gas")
        if self.type == "behind_the_meter" or re.search(r"behind[- ]the[- ]meter|co-?locat|\bon-?site\b", text, re.I):
            out.append("behind_the_meter")
        return out

    def supply(self):
        """The kind of supply (section 7): the first of these the kind or the technology's words say."""
        t = self.technology.lower()
        if self.kind in ("nuclear_restart_uprate", "smr") or re.search(r"nuclear|reactor|smr|fusion", t):
            return "nuclear"
        if self.kind == "gas_buildout" or re.search(r"\bgas\b|natural gas|lng|turbine", t):
            return "gas"
        if self.kind == "storage" or re.search(r"solar|wind|batter|storage|hydro|geotherm|renewable", t):
            return "renewables_storage"
        if self.kind == "compute_capacity":
            return "compute"
        if self.kind in ("ppa", "offtake", "behind_the_meter"):
            return "grid"
        if self.kind in ("capital", "m_and_a", "project_finance"):
            return "capital"
        return "other"


def dash(v):
    return v if v != "" else "-"


def table(rows, month):
    """The first tab: every row of the table (the register's pairs are not folded here), the month's cells, the filters."""
    ds, out = [Deal(r) for r in rows], {}
    out["table|rows"] = len(ds)
    y, m = int(month[:4]), int(month[5:7])
    if not any(d.month == month for d in ds):                  # the start of a month with no deal yet: the month before
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    shown = f"{y}-{m:02d}"
    mine = [d for d in ds if d.month == shown]
    out[f"deals|month_count|{shown}"] = len(mine)
    out[f"deals|month_mw|{shown}"] = sum(d.mw for d in mine if d.mw is not None)
    out[f"table|month_with_mw|{shown}"] = sum(1 for d in mine if d.mw is not None)
    if mine:
        out[f"deals|month_ai_pct|{shown}"] = js_round(100 * sum(1 for d in mine if d.ai) / len(mine))
    out["table|filter|ai|yes"] = sum(1 for d in ds if d.ai)
    out["table|filter|ai|no"] = sum(1 for d in ds if not d.ai)
    # a price is disclosed where the row states US dollars per MWh, or a figure in another unit of energy or capacity
    out["table|filter|price|yes"] = sum(1 for d in ds if d.price_table is not None or (d.price_other is not None and re.search(r"mwh|kwh|mw-?month|mmbtu", d.price_unit, re.I)))
    out["table|filter|mw_from|500"] = sum(1 for d in ds if d.mw is not None and d.mw >= 500)
    for k in KINDS:
        out[f"table|filter|kind|{k}"] = sum(1 for d in ds if d.kind == k)
    for s in STAGES:
        out[f"table|filter|stage|{s}"] = sum(1 for d in ds if d.stage == s)
    out["table|filter|stage|none"] = sum(1 for d in ds if not d.stage)
    out["table|with_mw"] = sum(1 for d in ds if d.mw is not None)
    out["table|with_usd"] = sum(1 for d in ds if d.usd_table is not None)
    out["table|with_flags"] = sum(1 for d in ds if d.flags)
    sure = [d.sure for d in ds if d.sure is not None]
    if sure:
        out["table|sure_min"], out["table|sure_max"] = min(sure), max(sure)
    return out


def folded_deals(rows, pairs):
    """One deal where the register says two rows are one: the row marked duplicate leaves, where both rows are held."""
    ids = {r["event_id"] for r in rows}
    gone = {p["duplicate"] for p in pairs if p["ruling"] == "fold" and p["duplicate"] in ids and p["kept"] in ids}
    return [Deal(r) for r in rows if r["event_id"] not in gone], len(gone)


def tracker(ds, n_folded):
    out = {"tracker|deals": len(ds), "tracker|folded": n_folded}
    with_mw = [d for d in ds if d.mw is not None]
    out["tracker|with_mw"], out["tracker|mw"] = len(with_mw), sum(d.mw for d in with_mw)
    out["tracker|with_price"] = sum(1 for d in ds if d.price is not None)
    out["tracker|with_other_price"] = sum(1 for d in ds if d.price is None and d.price_other is not None)
    out["tracker|with_dollars"] = sum(1 for d in ds if d.usd is not None)
    for g in PANEL_ORDER:
        out[f"tracker|type|{g}"] = sum(1 for d in ds if d.panel == g)
    for k in ("nuclear_restart", "smr", "gas", "behind_the_meter"):
        out[f"tracker|kind|{k}"] = sum(1 for d in ds if k in d.tool6())
    techs = {}
    for d in ds:
        techs[d.technology] = techs.get(d.technology, 0) + 1
    for t, n in techs.items():
        out[f"tracker|technology|{t or 'not stated'}"] = n
    for g in GRIDS:
        out[f"tracker|grid|{g}"] = sum(1 for d in ds if d.grid == g)
    for y in {d.year for d in ds}:
        out[f"tracker|year|{y}"] = sum(1 for d in ds if d.year == y)
    for s in STATUSES:
        out[f"tracker|status|{s}"] = sum(1 for d in ds if d.status == s)
    out["tracker|view|storage"] = sum(1 for d in ds if d.storage)
    out["tracker|view|ai"] = sum(1 for d in ds if d.ai)
    names = {}
    for d in ds:                                               # a party named in two deals or more; a deal counts once a name
        for p in {n for n in [d.buyer, d.seller, *d.others] if n}:
            names[p] = names.get(p, 0) + 1
    for p, n in names.items():
        if n >= 2:
            out[f"tracker|party|{p}"] = n
    months = sorted(d.month for d in ds)
    if months:                                                 # every month from the first deal to the last, a month with none a zero
        y, m = int(months[0][:4]), int(months[0][5:7])
        while f"{y}-{m:02d}" <= months[-1]:
            k = f"{y}-{m:02d}"
            out[f"tracker|month|{k}"] = sum(1 for d in ds if d.month == k)
            y, m = (y, m + 1) if m < 12 else (y + 1, 1)
    out["tracker|with_state"] = sum(1 for d in ds if d.state)
    out["tracker|with_grid"] = sum(1 for d in ds if d.grid)
    return out


def comparables(ds):
    out = {}
    for dim, of in (("type", lambda d: d.type), ("technology", lambda d: d.technology), ("grid", lambda d: d.grid), ("year", lambda d: d.year)):
        groups = {}
        for d in ds:
            groups.setdefault(of(d), []).append(d)
        for value, g in groups.items():
            v = dash(value)
            prices, mws = [d.price for d in g if d.price is not None], [d.mw for d in g if d.mw is not None]
            out[f"deals|comp_deals|{dim}|{v}"] = len(g)
            out[f"deals|comp_with_price|{dim}|{v}"] = len(prices)
            out[f"deals|comp_with_mw|{dim}|{v}"] = len(mws)
            if median3(prices) is not None:
                out[f"deals|comp_median_price|{dim}|{v}"] = median3(prices)
            if median3(mws) is not None:
                out[f"deals|comp_median_mw|{dim}|{v}"] = median3(mws)
    priced = [d for d in ds if d.type in ("ppa", "offtake") and d.price is not None]
    out["deals|priced"] = len(priced)
    for dim, of in (("technology", lambda d: d.technology), ("grid", lambda d: d.grid), ("year", lambda d: d.year)):
        groups = {}
        for d in priced:
            groups.setdefault(of(d), []).append(d.price)
        for value, ps in groups.items():
            v = dash(value)
            out[f"deals|price_count|{dim}|{v}"] = len(ps)
            if len(ps) >= 3:
                out[f"deals|price_median|{dim}|{v}"], out[f"deals|price_low|{dim}|{v}"], out[f"deals|price_high|{dim}|{v}"] = statistics.median(ps), min(ps), max(ps)
    return out


def ai_view(ds):
    ai, out = [d for d in ds if d.ai], {}
    out["deals|ai_tagged"] = len(ai)
    buyer = lambda d: d.buyer_name or d.buyer or d.seller_name or d.seller or ""
    for dim, of in (("buyer", buyer), ("supply", lambda d: d.supply()), ("grid", lambda d: d.grid), ("quarter", lambda d: d.quarter)):
        groups = {}
        for d in ai:
            groups.setdefault(of(d), []).append(d)
        for value, g in groups.items():
            v = dash(value)
            mws, usds = [d.mw for d in g if d.mw is not None], [d.usd for d in g if d.usd is not None]
            out[f"deals|ai_deals|{dim}|{v}"] = len(g)
            if mws:
                out[f"deals|ai_mw|{dim}|{v}"] = sum(mws)
            out[f"deals|ai_with_mw|{dim}|{v}"] = len(mws)
            if usds:
                out[f"deals|ai_usd|{dim}|{v}"] = sum(usds)
            out[f"deals|ai_with_usd|{dim}|{v}"] = len(usds)
    # the two lists of ten: power and infrastructure deals only (a capital deal is in the table's sums, not in the lists)
    listed = [d for d in ai if d.supply() != "capital"]
    for by, of in (("mw", lambda d: d.mw), ("usd", lambda d: d.usd)):
        top = sorted((d for d in listed if of(d) is not None), key=lambda d: (-of(d), d.id))[:10]
        for i, d in enumerate(top, 1):
            out[f"deals|ai_top_{by}|{i}"] = of(d)
    return out


def charts(ds):
    out = {}
    group = lambda d: d.supply() if d.supply() in ("nuclear", "gas", "renewables_storage", "grid") else "other"
    for q in sorted({d.quarter for d in ds}):
        in_q = [d for d in ds if d.quarter == q]
        for g in SUPPLY_GROUPS:
            out[f"deals|chart_mw|{q}|{g}"] = sum(d.mw for d in in_q if d.mw is not None and group(d) == g)
        out[f"deals|chart_mw|{q}|without"] = sum(1 for d in in_q if d.mw is None)
        all_mw = sum(d.mw for d in in_q if d.mw is not None)
        ai_mw = sum(d.mw for d in in_q if d.mw is not None and d.ai)
        if all_mw > 0:
            out[f"deals|chart_ai|{q}|share"] = js_round(1000 * ai_mw / all_mw) / 10
        out[f"deals|chart_ai|{q}|ai_mw"], out[f"deals|chart_ai|{q}|all_mw"] = ai_mw, all_mw
    for d in ds:
        if d.type in ("ppa", "offtake") and d.price is not None:
            out[f"deals|chart_price|{d.id}|price"] = d.price
    # the counterparties with the most MW stated: a deal counts once for each of its buyer and its seller
    mw, stating = {}, {}
    for d in ds:
        for name in {n.strip() for side in (d.buyer_name, d.seller_name) for n in side.split("; ") if n.strip()}:
            if d.mw is not None:
                mw[name] = mw.get(name, 0) + d.mw
                stating[name] = stating.get(name, 0) + 1
    return out, mw


def top_parties(mw, shown):
    """The ten with the most MW. Where the tenth and the eleventh are equal the page's order of names decides, so the
    names the page chose are taken when their megawatts are the ten largest."""
    ranked = sorted(mw.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) <= 10:
        return {f"deals|chart_party|{n}|mw": v for n, v in ranked}
    floor = ranked[9][1]
    sure = {n: v for n, v in ranked if v > floor}
    tied = [n for n, v in ranked if v == floor]
    theirs = [k.split("|")[2] for k in shown if k.startswith("deals|chart_party|")]
    pick = [n for n in tied if n in theirs][: 10 - len(sure)]
    pick += [n for n in tied if n not in pick][: 10 - len(sure) - len(pick)]
    return {f"deals|chart_party|{n}|mw": mw[n] for n in [*sure, *pick]}


def tolerance(key, value):
    """Half the last digit the page shows for the figure."""
    if key.startswith(("deals|ai_usd|", "deals|ai_top_usd|")):      # US dollars in words: two decimals of a million, a billion or a trillion
        v = abs(value or 0)
        return 0.005 * (1e12 if v >= 1e12 else 1e9 if v >= 1e9 else 1e6 if v >= 1e6 else 1)
    if key.endswith("|share") and key.startswith("deals|chart_ai|"):
        return 0.05                                                 # one decimal of a percent
    if key.startswith(("deals|month_", "table|", "capital|")) or "_deals|" in key or "|with_" in key or key.startswith(("tracker|", "deals|ai_tagged", "deals|priced", "deals|price_count")):
        return 0.005 if key in ("tracker|mw",) else 0.5             # a count, or a figure shown whole
    return 0.005                                                    # megawatts, a median or a price, shown to two decimals


def page_figures(rows_dir, month, page_file):
    if page_file:
        return load(page_file)
    node = shutil.which("node")
    if not node:
        raise OSError("node is not installed: pass --page with the JSON site/scripts/deal-tracker-figures.mjs prints")
    got = subprocess.run([node, os.path.join("scripts", "deal-tracker-figures.mjs"), rows_dir, month], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
    if got.returncode != 0:
        raise OSError("the page's functions did not run: " + got.stderr.strip()[-400:])
    return json.loads(got.stdout)


def headline(rows_dir):
    """The do-file's lines (replicate.do), step for step on the same CSV: the mirror a reader without Stata runs."""
    with open(os.path.join(rows_dir, "deals_slim.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    kept = [r for r in rows if r["folded_duplicate"] != "1"]
    mws = [float(r["mw"]) for r in kept if r["mw"] != ""]
    lines = [("1. deals held, the register's folded pairs counted once", len(kept)),
             ("2. deals that state a size in MW", len(mws)),
             ("3. megawatts stated by them", sum(mws)),
             ("4. deals that state a value in US dollars", sum(1 for r in kept if r["dollars"] != "")),
             ("5. deals tagged AI power", sum(1 for r in kept if r["ai_power"] == "true")),
             ("6. deals that state a price in US dollars per MWh", sum(1 for r in kept if r["usd_per_mwh"] != ""))]
    by = {}
    for r in kept:
        k = (r["date"][:4], r["kind"] or "other")
        n, w, m = by.get(k, (0, 0, 0.0))
        by[k] = (n + 1, w + (1 if r["mw"] != "" else 0), m + (float(r["mw"]) if r["mw"] != "" else 0.0))
    return lines, by


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # names with accents print the same on every machine
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rows", default=os.path.join(HERE, "rows"))
    ap.add_argument("--page")
    ap.add_argument("--month")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--headline", action="store_true", help="only the do-file's lines, from the CSV it reads")
    a = ap.parse_args(argv[1:])
    rows_dir = os.path.abspath(a.rows)
    if a.headline:
        try:
            lines, by = headline(rows_dir)
        except (OSError, ValueError, KeyError) as exc:
            print(f"the inputs could not be read: {exc}")
            return 2
        for words, value in lines:
            print(f"{words}: {value:,.2f}".replace(".00", "") if isinstance(value, float) else f"{words}: {value:,}")
        print("by year and kind: deals, deals stating MW, MW stated")
        for (year, kind), (n, w, m) in sorted(by.items()):
            print(f"  {year} {kind}: {n}, {w}, {m:,.2f}".replace(".00", ""))
        return 0
    try:
        stamp = load(os.path.join(rows_dir, "retrieved.json"))
        month = a.month or stamp["retrieved_at"][:7]
        rows = load(os.path.join(rows_dir, "energy_deals.json"))
        pairs = load(os.path.join(SITE, "data", "deal_duplicates.json"))["pairs"]
        page = page_figures(rows_dir, month, a.page)
        shown = page["figures"]
        mine = table(rows, month)
        ds, n_folded = folded_deals(rows, pairs)
        mine.update(tracker(ds, n_folded))
        mine.update(comparables(ds))
        mine.update(ai_view(ds))
        chart, party_mw = charts(ds)
        mine.update(chart)
        mine.update(top_parties(party_mw, shown))
        mine["capital|n_rows"] = len(rows)                      # the capital view under the hold: the table's row count alone
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    lines, bad, named = [], 0, 0
    for key in sorted(set(mine) | set(shown)):
        got, want = mine.get(key), shown.get(key)
        if got is None or want is None:
            lines.append((key, got, want, None, "NO: " + ("page only" if got is None else "replication only")))
            bad += 1
            continue
        diff = float(got) - float(want)
        if abs(diff) <= tolerance(key, want) + 1e-9:
            lines.append((key, got, want, diff, "yes"))
        elif key in NAMED:
            lines.append((key, got, want, diff, "named: " + NAMED[key]))
            named += 1
        else:
            lines.append((key, got, want, diff, "NO"))
            bad += 1
    print(f"The deal tracker, {len(rows)} rows of energy_deals as the live set served them at {stamp['retrieved_at']} "
          f"(newest deal {stamp.get('newest_deal', '')}); the page drawn in {month}")
    print("figure | replication | the page's functions | difference | inside the tolerance")
    fmt = lambda v: "none" if v is None else (f"{v:,.4f}" if isinstance(v, float) and not float(v).is_integer() else f"{int(v):,}")
    for key, got, want, diff, state in lines:
        print(f"{key} | {fmt(got)} | {fmt(want)} | {'' if diff is None else f'{diff:+.4f}'} | {state}")
    print(f"{len(lines) - bad - named} of {len(lines)} inside the tolerance; {named} named; {bad} not explained")
    print("not replicated here: the words of the table (each deal's own row); the capital view's sums by quarter, segment and kind of company, "
          "which its file does not hold while the table is held")
    if a.write:
        figures = [{"key": k, "page": w, "replication": g, "tolerance": tolerance(k, w), **({"named": NAMED[k]} if s.startswith("named") else {})} for k, g, w, _, s in lines]
        with open(os.path.join(HERE, "page_figures.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"tool": "/deals", "retrieved_at": stamp["retrieved_at"], "newest_deal": stamp.get("newest_deal", ""), "month": month, "rows": len(rows),
                       "source": stamp["source"],
                       "note": "the page's figure is what its own functions compute on the live set's rows (site/scripts/deal-tracker-figures.mjs); "
                               "energy_deals is held (license needed), so the built page draws none of them to a visitor",
                       "figures": figures}, f, indent=1)
            f.write("\n")
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# ERW, the deal tracker: every figure of the pages on the live set's rows of {stamp['retrieved_at']} (replication/deals/replicate.py --write)\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["key", "page", "replication", "tolerance"])
            for x in figures:
                w.writerow([x["key"], x["page"], x["replication"], x["tolerance"]])
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
