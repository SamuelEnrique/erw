#!/usr/bin/env python3
"""The company database's tracers and cross-checks (session 3303, chain 200; docs/methods/companies.md, "Tracers").

Energy Research Warehouse (ERW). Reads the three tables (company_directory, company_aliases, company_links) and their
inputs as held; writes nothing under warehouse/output, needs no lock, makes no request.

    python warehouse/derived/check_companies.py                       # the tracers; exit 1 on any failure
    python warehouse/derived/check_companies.py --crosscheck FILE.md  # also write the two cross-checks to FILE.md
    python warehouse/derived/check_companies.py --in-dir DIR           # read the tables from DIR
    python warehouse/derived/check_companies.py --pages site/data/companies   # also trace the page files (6)

The tracers (each a failure when it does not hold):
1. every link's input_row is a row of its input_table (its entity_id or event_id);
2. the link's name_as_written is in that row's column for the role (case and spacing aside), or, for a deal party
   written "X's Y", the row's column holds "X's Y";
3. every company of company_links is a row of company_directory and every directory row has a link;
4. the directory's counts and MW (n_deals, deals_mw, n_plants, plants_mw, the MW by fuel, owned_mw, planned_mw,
   n_facilities, facilities_mw, n_queue, queue_mw, n_reactors, n_policy_actions, n_links) recomputed here from the links
   alone, by code written apart from the builder's, equal the directory's to 0.1 MW;
5. every alias of company_aliases is a name_as_written of company_links for the same company, table and role.

The cross-checks (written, never applied; a difference is a question, not an error):
A. a utility's EIA-861 retail sales (Parts A and B, the newest year with at least 80% of the median year's utilities) against its EIA-860M operated capacity:
   sales / (capacity x 8,760 h), an implied use of its own fleet; above 1 it sells more than its fleet could make
   running all year (it buys power), near 0 it sells little at retail (a wholesale generator);
B. a developer's queue MW (ERCOT and NYISO, not withdrawn) against its deals' MW.
"""

import argparse
import os
import re
import sys
from collections import defaultdict

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
COL = {  # (table, role) -> the input column that holds the name
    ("energy_deals", "buyer"): "buyer", ("energy_deals", "seller"): "seller", ("energy_deals", "party"): "other_parties",
    ("datacenter_projects", "operator"): "operator", ("datacenter_projects", "developer"): "developer",
    ("datacenter_projects", "utility"): "utility", ("datacenter_facilities", "operator"): "operator",
    ("datacenter_facilities", "developer"): "developer", ("datacenter_facilities", "utility"): "utility",
    ("eia860m_operating_generators", "operator"): "operator", ("eia860m_planned_generators", "operator"): "operator",
    ("eia860_plants_annual", "operator"): "operator", ("eia860_generator_owners", "owner"): "name",
    ("eia861_utility_data", "utility"): "name", ("utility_service_territories", "service_territory"): "name",
    ("ercot_interconnection_queue", "interconnection_customer"): "operator",
    ("nyiso_interconnection_queue", "interconnection_customer"): "operator",
    ("policy_actions", "agency"): "parties", ("nrc_power_reactors", "licensee"): "x_licensee",
    ("nrc_power_reactors", "operator"): "operator", ("nrc_power_reactors", "parent"): "x_parent_company",
}
FIGURES = ["n_deals", "deals_mw", "n_plants", "plants_mw", "owned_mw", "planned_mw", "n_facilities", "facilities_mw",
           "n_queue", "queue_mw", "n_reactors", "n_policy_actions", "n_links", "mw_solar", "mw_wind", "mw_gas",
           "mw_coal", "mw_nuclear", "mw_hydro", "mw_storage", "mw_oil", "mw_geothermal", "mw_other"]


def read(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, low_memory=False)


def squash(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def f(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return 0.0
    return x if x == x else 0.0


def recompute(links):
    """The directory's figures from the links alone (written apart from companies.build)."""
    out = defaultdict(lambda: defaultdict(float))
    seen = defaultdict(set)
    for r in links.itertuples(index=False):
        c, t, row, role = r.company_id, r.input_table, r.input_row, r.role
        o = out[c]
        o["n_links"] += 1
        if t == "energy_deals":
            if (c, "deal", row) not in seen["d"]:
                seen["d"].add((c, "deal", row))
                o["n_deals"] += 1
                o["deals_mw"] += f(r.mw)
        elif t == "eia860m_operating_generators":
            seen["p"].add((c, r.detail))
            o["plants_mw"] += f(r.mw)
            o["mw_" + (r.fuel or "other")] += f(r.mw)
        elif t == "eia860m_planned_generators":
            o["planned_mw"] += f(r.mw)
        elif t == "eia860_generator_owners":
            o["owned_mw"] += f(r.mw)
        elif t == "datacenter_facilities" and role in ("operator", "developer"):
            if (c, row) not in seen["f"]:
                seen["f"].add((c, row))
                o["n_facilities"] += 1
                o["facilities_mw"] += f(r.mw)
        elif t in ("ercot_interconnection_queue", "nyiso_interconnection_queue"):
            if r.detail not in ("withdrawn", "Completed"):
                o["n_queue"] += 1
                o["queue_mw"] += f(r.mw)
        elif t == "policy_actions":
            if (c, row) not in seen["a"]:
                seen["a"].add((c, row))
                o["n_policy_actions"] += 1
        elif t == "nrc_power_reactors" and role in ("licensee", "operator"):
            if (c, row) not in seen["r"]:
                seen["r"].add((c, row))
                o["n_reactors"] += 1
    for c, d in seen["p"]:
        out[c]["n_plants"] += 1
    return out


def tracers(d, a, l, inputs):
    fails = []
    # 1 and 2: the row and the name
    for t, g in l.groupby("input_table"):
        src = inputs[t]
        key = "event_id" if "event_id" in src.columns else "entity_id"
        rows = src.set_index(key)
        missing = sorted(set(g["input_row"]) - set(rows.index))
        if missing:
            fails.append(f"1 {t}: {len(missing)} link rows not in the table, e.g. {missing[:3]}")
        bad = 0
        examples = []
        for r in g.itertuples(index=False):
            if r.input_row not in rows.index:
                continue
            col = COL.get((t, r.role))
            cell = squash(rows.at[r.input_row, col]) if col else ""
            if isinstance(cell, pd.Series):
                cell = squash(cell.iloc[0])
            if squash(r.name_as_written) not in cell:
                bad += 1
                if len(examples) < 3:
                    examples.append(f"{r.input_row} {r.role} {r.name_as_written!r} not in {cell[:80]!r}")
        if bad:
            fails.append(f"2 {t}: {bad} names not in their row's column, e.g. {examples}")
    # 3: the companies
    lc, dc = set(l["company_id"]), set(d["entity_id"])
    if lc - dc:
        fails.append(f"3 {len(lc - dc)} companies of the links are not in the directory")
    if dc - lc:
        fails.append(f"3 {len(dc - lc)} directory rows have no link")
    # 4: the figures
    rc = recompute(l)
    di = d.set_index("entity_id")
    for fig in FIGURES:
        got = pd.to_numeric(di[fig], errors="coerce").fillna(0)
        want = pd.Series({c: rc[c].get(fig, 0.0) for c in di.index})
        diff = (got - want).abs()
        tol = 0.11 if not fig.startswith("n_") else 0.0
        off = diff[diff > tol]
        if len(off):
            fails.append(f"4 {fig}: {len(off)} companies differ, e.g. {off.index[0]} {got[off.index[0]]} against {want[off.index[0]]}")
    # 5: the aliases
    k = set(zip(l["company_id"], l["name_as_written"], l["input_table"], l["role"]))
    ka = set(zip(a["company_id"], a["alias"], a["input_table"], a["role"]))
    if ka - k:
        fails.append(f"5 {len(ka - k)} aliases are not names of the links")
    if k - ka:
        fails.append(f"5 {len(k - ka)} names of the links have no alias row")
    return fails


def pages(l, pages_dir, lic):
    """Tracer 6 (session 3306): the page files (site/data/companies/) against the links. Each listed company's figures
    equal the public links' recomputed here; the listed companies are those with a public link; no held table's row is in
    a file."""
    import hashlib
    import json
    fails = []
    with open(os.path.join(pages_dir, "index.json"), encoding="utf-8") as fh:
        ix = json.load(fh)
    pub = l[l["input_table"].map(lambda t: lic.get(t) == "public")]
    want_ids = set(pub["company_id"])
    cols = ix["columns"]
    got_ids = {"company:" + r[cols.index("id")] for r in ix["rows"]}
    if got_ids != want_ids:
        fails.append(f"6 listed companies: {len(got_ids - want_ids)} without a public link, {len(want_ids - got_ids)} with one not listed")
    rc = recompute(pub)
    shards = {}
    for cid in sorted(got_ids & want_ids):
        key = hashlib.sha1(cid.encode("utf-8")).hexdigest()[:2]
        if key not in shards:
            with open(os.path.join(pages_dir, "c", key + ".json"), encoding="utf-8") as fh:
                shards[key] = json.load(fh)
        c = shards[key][cid.split(":", 1)[1]]
        for fig in FIGURES:
            if fig == "n_links" or (fig.startswith("mw_") and fig[3:] not in c["fuel"] and rc[cid].get(fig, 0) == 0):
                continue
            have = c["fuel"].get(fig[3:], 0.0) if fig.startswith("mw_") else c["figures"].get(fig)
            if have is None or abs(float(have) - rc[cid].get(fig, 0.0)) > (0.11 if not fig.startswith("n_") else 0):
                fails.append(f"6 {cid} {fig}: the file {have}, the public links {rc[cid].get(fig, 0.0)}")
        if len(c["links"]) != int(rc[cid].get("n_links", 0)):
            fails.append(f"6 {cid}: {len(c['links'])} links in the file, {int(rc[cid].get('n_links', 0))} public")
    held = [t for t in ix["tables"] if lic.get(t) != "public"]
    if sorted(held) != sorted(ix["held_tables"]):
        fails.append(f"6 the held tables: the file {ix['held_tables']}, the license status {held}")
    return fails


def crosschecks(d, l, inputs):
    """(the sales check rows, the queue and deals rows)."""
    sales = inputs["eia861_utility_sales"]
    s = sales[(sales["variable"] == "total_sales") & sales["x_part"].isin(["A", "B"])].copy()
    s["year"] = s["ts_utc"].str[:4]
    s["uid"] = s["x_utility_number"].map(lambda v: str(int(float(v))) if v else "")
    counts = s.groupby("year")["uid"].nunique()
    newest = max(y for y, n in counts.items() if n >= 0.8 * counts.median())  # the newest year near the usual count (a partial year is skipped)
    s = s[s["year"] == newest]
    by = s.groupby("uid")["value"].apply(lambda v: pd.to_numeric(v, errors="coerce").sum())
    di = d[d["eia_utility_id"] != ""].copy()
    di["cap"] = pd.to_numeric(di["plants_mw"], errors="coerce").fillna(0)
    di["sales_mwh"] = di["eia_utility_id"].map(by)
    both = di[(di["cap"] > 0) & di["sales_mwh"].notna() & (di["sales_mwh"] > 0)].copy()
    both["implied"] = both["sales_mwh"] / (both["cap"] * 8760)
    both = both.sort_values("cap", ascending=False)
    q = d.copy()
    for c in ("queue_mw", "deals_mw"):
        q[c] = pd.to_numeric(q[c], errors="coerce").fillna(0)
    qd = q[(q["queue_mw"] > 0) & (pd.to_numeric(q["n_deals"]) > 0)].sort_values("queue_mw", ascending=False)
    return newest, both, qd


def write_crosscheck(path, newest, both, qd):
    lines = ["# The company database's cross-checks", "",
             f"Written by `warehouse/derived/check_companies.py --crosscheck` (session 3303, chain 200). Checks, not corrections: nothing here changes a table. Method: `docs/methods/companies.md`, \"Cross-checks\".", "",
             f"## A. A utility's EIA-861 retail sales ({newest}) against its EIA-860M operated capacity", "",
             f"{len(both):,} companies have both: an EIA utility id with retail sales (Parts A and B of `eia861_utility_sales`, {newest}) and operating capacity in `eia860m_operating_generators` (`plants_mw`). The implied use is sales / (capacity x 8,760 h). Above 1, a company sells more at retail than its own fleet could make running every hour of the year: it buys power. Near 0, it sells little at retail: its plants sell at wholesale.", "",
             f"- Implied use above 1: {int((both['implied'] > 1).sum()):,}; from 0.2 to 1: {int(((both['implied'] >= 0.2) & (both['implied'] <= 1)).sum()):,}; below 0.2: {int((both['implied'] < 0.2).sum()):,}.",
             f"- Median {both['implied'].median():.2f}.", "",
             "The thirty with the most capacity:", "",
             "| Company | EIA id | Kind | Capacity MW | Retail sales MWh | Implied use |", "|---|---|---|---|---|---|"]
    for r in both.head(30).itertuples():
        lines.append(f"| {r.name} | {r.eia_utility_id} | {r.kind} | {r.cap:,.0f} | {r.sales_mwh:,.0f} | {r.implied:.2f} |")
    lines += ["", "The ten with the highest implied use (at least 50 MW of capacity):", "",
              "| Company | EIA id | Kind | Capacity MW | Retail sales MWh | Implied use |", "|---|---|---|---|---|---|"]
    for r in both[both["cap"] >= 50].sort_values("implied", ascending=False).head(10).itertuples():
        lines.append(f"| {r.name} | {r.eia_utility_id} | {r.kind} | {r.cap:,.0f} | {r.sales_mwh:,.0f} | {r.implied:.2f} |")
    lines += ["", "## B. A developer's queue MW against its deals' MW", "",
              f"{len(qd):,} companies hold both positions in the ERCOT or NYISO queue (not withdrawn, not completed) and deals in `energy_deals`. The two measure different things (a queue position is a request to connect; a deal's MW is what a story states), so neither is expected to equal the other; a company whose deals' MW far exceeds its queue MW in these two grids builds elsewhere or buys.", "",
              "| Company | Kind | Queue positions | Queue MW | Deals | Deals MW |", "|---|---|---|---|---|---|"]
    for r in qd.itertuples():
        lines.append(f"| {r.name} | {r.kind} | {r.n_queue} | {r.queue_mw:,.0f} | {r.n_deals} | {r.deals_mw:,.0f} |")
    if not len(qd):
        lines.append("| (none) | | | | | |")
    lines.append("")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description="The company database's tracers and cross-checks")
    ap.add_argument("--in-dir", default=OUT)
    ap.add_argument("--crosscheck", help="write the two cross-checks to this markdown file")
    ap.add_argument("--pages", help="also trace the page files in this folder (site/data/companies)")
    args = ap.parse_args(argv)
    d = read(os.path.join(args.in_dir, "company_directory.csv"))
    a = read(os.path.join(args.in_dir, "company_aliases.csv"))
    l = read(os.path.join(args.in_dir, "company_links.csv"))
    names = set(l["input_table"]) | {"eia861_utility_sales"}
    inputs = {t: read(os.path.join(args.in_dir, t + ".csv")) for t in names}
    fails = tracers(d, a, l, inputs)
    if args.pages:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import companies as C
        fails += pages(l, args.pages, C.licenses(sorted(set(l["input_table"]))))
    for x in fails:
        print("FAIL", x)
    print(f"tracers: {len(l):,} links, {len(d):,} companies, {len(a):,} aliases; {len(fails)} failures")
    if args.crosscheck:
        newest, both, qd = crosschecks(d, l, inputs)
        write_crosscheck(args.crosscheck, newest, both, qd)
        print(f"cross-checks: A {len(both):,} utilities ({newest}), B {len(qd):,} companies -> {args.crosscheck}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
