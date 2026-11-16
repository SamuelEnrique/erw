#!/usr/bin/env python3
"""ERW, the company database (/companies and /companies/<id>): an independent replication of every figure the page
files show (session 7005, chain 301, goal 4).

Written from docs/methods/companies.md and the tables alone, not from warehouse/derived/companies_page.py. It reads the
page's files (site/data/companies/index.json and the 256 shards under c/) and, for each listed company, recomputes its
figures from its public rows of company_links with every MW, date, county and status taken from the input table's own
row (EIA-860M's nameplate, EIA-860's percent owned, the ERCOT queue's capacity and status, the NRC's capacity, EIA-861's
service territories), by the method's rules:

  plants_mw, n_plants, n_generators   operating generators in EIA-860M: nameplate summed; EIA plant ids; generators
  owned_mw, n_owned_generators        EIA-860 owner rows: the generator's EIA-860M nameplate times the percent owned
  planned_mw, n_planned_plants        EIA-860M planned generators: nameplate summed; EIA plant ids
  queue_mw, n_queue                   queue positions neither withdrawn nor completed: capacity summed
  reactors_mw, n_reactors             NRC reactors it is licensee or operator of: capacity summed, each reactor once
  n_policy_actions, n_counties        policy actions it is a party to; service territory counties (state, county)
  n_deals, deals_mw, deals_usd, n_facilities, facilities_mw   from public rows only (zero while their tables are held)
  footprint_mw                        plants, owned, planned, queue, facilities and deals MW summed
  n_links                             its public links

A held table's row is never counted (the link's license column, set from warehouse/metadata/license_status.csv). Each
figure is compared with the shard's and, where the index carries it, with the index's (rounded to 0.1 MW, so a
difference of 0.05 or less is equal). Prints N of N and each difference.

    python replication/companies/replicate.py [--tables DIR] [--site DIR]

Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
csv.field_size_limit(10 ** 9)

FIGS = ["n_plants", "n_generators", "plants_mw", "n_owned_generators", "owned_mw", "n_planned_plants", "planned_mw",
        "n_queue", "queue_mw", "n_deals", "deals_mw", "deals_usd", "n_facilities", "facilities_mw", "n_reactors",
        "reactors_mw", "n_policy_actions", "n_counties", "footprint_mw"]


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def num(v):
    try:
        x = float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return x if x == x else None


def inputs(tables):
    """The input rows by id, the fields this replication reads."""
    op = {r["entity_id"]: r for r in rows(os.path.join(tables, "eia860m_operating_generators.csv"))}
    nameplate = {(r["plant_id"].split(".")[0], r["generator_id"].strip()): num(r["nameplate_mw"]) for r in op.values()}
    pl = {r["entity_id"]: r for r in rows(os.path.join(tables, "eia860m_planned_generators.csv"))}
    own = {r["entity_id"]: r for r in rows(os.path.join(tables, "eia860_generator_owners.csv"))}
    q = {r["entity_id"]: r for r in rows(os.path.join(tables, "ercot_interconnection_queue.csv"))}
    nrc = {r["entity_id"]: r for r in rows(os.path.join(tables, "nrc_power_reactors.csv"))}
    ter = {r["entity_id"]: r for r in rows(os.path.join(tables, "utility_service_territories.csv"))}
    return op, nameplate, pl, own, q, nrc, ter


def figures(links, inp):
    """A company's figures from its public links, each value read from the input table's row."""
    op, nameplate, pl, own, q, nrc, ter = inp
    f = defaultdict(float)
    plants, planned, gens, owned, queue, reactors, policy, counties, deals, fac = (set() for _ in range(10))
    for l in links:
        t, rid = l["input_table"], l["input_row"]
        if t == "eia860m_operating_generators":
            r = op[rid]
            plants.add(r["plant_id"].split(".")[0])
            gens.add(rid)
            f["plants_mw"] += num(r["nameplate_mw"]) or 0
        elif t == "eia860m_planned_generators":
            r = pl[rid]
            planned.add(r["plant_id"].split(".")[0])
            f["planned_mw"] += num(r["nameplate_mw"]) or 0
        elif t == "eia860_generator_owners":
            r = own[rid]
            owned.add(rid)
            mw, pct = nameplate.get((r["x_plant_code"].split(".")[0], r["x_generator_id"].strip())), num(r["x_percent_owned"])
            if mw is not None and pct is not None:
                f["owned_mw"] += mw * pct
        elif t == "ercot_interconnection_queue":
            r = q[rid]
            if not r["withdrawn_date"] and r["iso_status"] not in ("Withdrawn", "Completed"):
                queue.add(rid)
                f["queue_mw"] += num(r["capacity_mw"]) or 0
        elif t == "nrc_power_reactors" and l["role"] in ("licensee", "operator") and rid not in reactors:
            reactors.add(rid)
            f["reactors_mw"] += num(nrc[rid]["capacity_mw"]) or 0
        elif t == "policy_actions":
            policy.add(rid)
        elif t == "utility_service_territories":
            r = ter[rid]
            counties.add((r["x_state"], r["x_county"]))
        elif t == "energy_deals" and rid not in deals:
            deals.add(rid)
            f["deals_mw"] += num(l["mw"]) or 0
            f["deals_usd"] += num(l["usd"]) or 0
        elif t == "datacenter_facilities" and l["role"] in ("operator", "developer") and rid not in fac:
            fac.add(rid)
            f["facilities_mw"] += num(l["mw"]) or 0
    out = dict(n_plants=len(plants), n_generators=len(gens), plants_mw=f["plants_mw"], n_owned_generators=len(owned),
               owned_mw=f["owned_mw"], n_planned_plants=len(planned), planned_mw=f["planned_mw"], n_queue=len(queue),
               queue_mw=f["queue_mw"], n_deals=len(deals), deals_mw=f["deals_mw"], deals_usd=f["deals_usd"],
               n_facilities=len(fac), facilities_mw=f["facilities_mw"], n_reactors=len(reactors),
               reactors_mw=f["reactors_mw"], n_policy_actions=len(policy), n_counties=len(counties))
    out["footprint_mw"] = sum(round(out[k], 1) for k in ("plants_mw", "owned_mw", "planned_mw", "queue_mw",
                                                          "facilities_mw", "deals_mw"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The company database's replication")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    a = ap.parse_args(argv)
    data = os.path.join(a.site, "data", "companies")
    try:
        with open(os.path.join(data, "index.json"), encoding="utf-8") as f:
            ix = json.load(f)
        shards = {}
        for name in os.listdir(os.path.join(data, "c")):
            with open(os.path.join(data, "c", name), encoding="utf-8") as f:
                shards.update(json.load(f))
        by = defaultdict(list)
        for l in rows(os.path.join(a.tables, "company_links.csv")):
            if l["license"] == "public":
                by[l["company_id"].split(":", 1)[1]].append(l)
        inp = inputs(a.tables)
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    cols = ix["columns"]
    n = bad = 0
    misses = []
    listed = {r[cols.index("id")]: dict(zip(cols, r)) for r in ix["rows"]}
    if set(listed) != set(shards):
        misses.append(f"index and shards list different companies: {len(set(listed) ^ set(shards))}")
    for cid, row in listed.items():
        mine = by.get(cid, [])
        try:
            got = figures(mine, inp)
        except KeyError as exc:
            misses.append(f"{cid}: a link's row is not in its table ({exc})")
            bad += 1
            continue
        got["n_links"] = len(mine)
        sh = shards.get(cid, {}).get("figures", {})
        for k in FIGS:
            if k in sh:
                n += 1
                if abs(float(got[k]) - float(sh[k])) > (0.051 if k.endswith("_mw") or k == "deals_usd" else 0):
                    bad += 1
                    misses.append(f"{cid} shard {k}: replication {got[k]:.3f}, file {sh[k]}")
        for k in cols:
            if k in got:
                n += 1
                if abs(float(got[k]) - float(row[k])) > (0.051 if k.endswith("_mw") else 0):
                    bad += 1
                    misses.append(f"{cid} index {k}: replication {got[k]:.3f}, file {row[k]}")
        # the shard's public links are exactly the company's public rows
        n += 1
        if len(shards.get(cid, {}).get("links", [])) != len(mine):
            bad += 1
            misses.append(f"{cid} links: replication {len(mine)}, shard {len(shards.get(cid, {}).get('links', []))}")
    # a company named only in held tables is not listed: every public link's company is
    n += 1
    unlisted = sorted(set(by) - set(listed))
    if unlisted:
        bad += 1
        misses.append(f"{len(unlisted)} companies with public links are not listed, e.g. {unlisted[:3]}")
    print(f"The company database, from {a.tables} and {data} (built {ix['built']}): {len(listed):,} companies listed")
    for m in misses[:60]:
        print("  " + m)
    print(f"{n - bad:,} of {n:,} figures equal")
    return 0 if not bad and not misses else 1


if __name__ == "__main__":
    sys.exit(main())
