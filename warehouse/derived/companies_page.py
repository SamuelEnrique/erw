#!/usr/bin/env python3
"""The files the company pages read (/companies and /companies/<id>; sessions 3304 to 3306, chain 200).

Energy Research Warehouse (ERW). Reads company_directory, company_aliases and company_links (warehouse/derived/
companies.py) and the input tables' headers; writes site/data/companies/. No request, no model call, no data lock
(nothing under warehouse/output is written). Method: docs/methods/companies.md, "The pages".

    python warehouse/derived/companies_page.py                  # the files, from this repository's warehouse/output
    python warehouse/derived/companies_page.py --in-dir DIR     # read the tables from DIR (a worktree reads main's)
    python warehouse/derived/companies_page.py --out-dir DIR    # write the files under DIR

The hold (the owner's ruling of 12 October 2026, warehouse/metadata/license_status.csv): a link from a table whose
publisher asks for permission is held. Its row, its name and its figures are not in these files; only the count of a
company's held links by table is. A company named only in held tables is not listed; the index counts them. Every
figure here is computed from public links alone, so it may differ from company_directory's, which sums every link:
check_companies.py --pages recomputes each.

    index.json          the listed companies, one array a company (columns in "columns"), the filters' values, the
                        held tables and their counts, each input's source line
    c/<xx>.json         the companies whose id's sha1 starts with <xx> (256 files): each company's figures, its MW by
                        fuel, its MW by year, its names, its public links and its held counts
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import companies as C  # noqa: E402

OUT = os.path.join(ROOT, "site", "data", "companies")
FUELS = C.FUELS
INDEX_COLS = ["id", "name", "kind", "segment", "hq_state", "states", "grids", "n_plants", "plants_mw", "planned_mw",
              "n_queue", "queue_mw", "n_reactors", "n_policy_actions", "n_deals", "deals_mw", "n_facilities",
              "facilities_mw", "footprint_mw", "n_links", "aka", "first_seen", "last_seen"]
# a link as the shards hold it: the table and the rule are positions in index.json's "tables" and "rules"; the name as
# written is "" where it is the company's own name; the confidence is the rule's (companies.CONF)
LINK_COLS = ["link", "table", "row", "role", "name", "rule", "mw", "usd", "date", "fuel", "state", "grid", "detail"]
RULES = list(C.CONF)


def shard(cid):
    return hashlib.sha1(cid.encode("utf-8")).hexdigest()[:2]


def slug_of(cid):
    """The page's address part: company:eia-6452 -> eia-6452."""
    return cid.split(":", 1)[1]


def num(v):
    x = C.num(v)
    return 0.0 if x is None else x


def r1(x):
    return round(float(x), 1)


def source_line(path):
    """An input's 'Source:' header line, as its file states it (the page's hover)."""
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            m = re.match(r"#\s*Source:\s*(.*)", ln)
            if m:
                return m.group(1).strip()[:300]
    return ""


def figures(links):
    """A company's public figures from its public links (the rules of companies.build, on fewer rows)."""
    f = defaultdict(float)
    plants, planned, deals, fac, queue, reactors, policy, owned, counties = (set() for _ in range(9))
    by_fuel = defaultdict(float)
    years = defaultdict(lambda: [0.0, 0.0, 0.0])
    quarters = defaultdict(lambda: [0, 0.0, 0.0])
    for l in links:
        t, mw, y = l["input_table"], num(l["mw"]), (l["date"] or "")[:4]
        if t == "eia860m_operating_generators":
            plants.add(l["detail"])
            f["n_generators"] += 1
            f["plants_mw"] += mw
            by_fuel[l["fuel"] or "other"] += mw
            if y:
                years[y][0] += mw
        elif t == "eia860m_planned_generators":
            planned.add(l["detail"])
            f["planned_mw"] += mw
            if y:
                years[y][1] += mw
        elif t == "eia860_generator_owners":
            owned.add(l["input_row"])
            f["owned_mw"] += mw
        elif t in ("ercot_interconnection_queue", "nyiso_interconnection_queue"):
            if l["detail"] not in ("withdrawn", "Completed"):
                queue.add(l["input_row"])
                f["queue_mw"] += mw
                if y:
                    years[y][2] += mw
        elif t == "energy_deals" and l["input_row"] not in deals:
            deals.add(l["input_row"])
            f["deals_mw"] += mw
            f["deals_usd"] += num(l["usd"])
            if y:
                q = f"{y}Q{(int(l['date'][5:7]) - 1) // 3 + 1}"
                quarters[q][0] += 1
                quarters[q][1] += mw
                quarters[q][2] += num(l["usd"])
        elif t == "datacenter_facilities" and l["role"] in ("operator", "developer") and l["input_row"] not in fac:
            fac.add(l["input_row"])
            f["facilities_mw"] += mw
        elif t == "nrc_power_reactors" and l["role"] in ("licensee", "operator") and l["input_row"] not in reactors:
            reactors.add(l["input_row"])
            f["reactors_mw"] += mw
        elif t == "policy_actions":
            policy.add(l["input_row"])
        elif t == "utility_service_territories":
            counties.add((l["state"], l["detail"]))
    out = dict(n_plants=len(plants), n_generators=int(f["n_generators"]), plants_mw=r1(f["plants_mw"]),
               n_owned_generators=len(owned), owned_mw=r1(f["owned_mw"]), n_planned_plants=len(planned),
               planned_mw=r1(f["planned_mw"]), n_queue=len(queue), queue_mw=r1(f["queue_mw"]), n_deals=len(deals),
               deals_mw=r1(f["deals_mw"]), deals_usd=round(f["deals_usd"]), n_facilities=len(fac),
               facilities_mw=r1(f["facilities_mw"]), n_reactors=len(reactors), reactors_mw=r1(f["reactors_mw"]),
               n_policy_actions=len(policy), n_counties=len(counties))
    out["footprint_mw"] = r1(out["plants_mw"] + out["owned_mw"] + out["planned_mw"] + out["queue_mw"]
                             + out["facilities_mw"] + out["deals_mw"])
    fuel = {k: r1(by_fuel.get(k, 0.0)) for k in FUELS if by_fuel.get(k, 0.0)}
    yr = [[y, r1(a), r1(b), r1(c)] for y, (a, b, c) in sorted(years.items())]
    qt = [[q, n, r1(mw), round(usd)] for q, (n, mw, usd) in sorted(quarters.items())]
    return out, fuel, yr, qt


def no_dash(text):
    """CLAUDE.md rule 2: no em or en dash in a file of the repository. A source name that holds one (the NRC writes
    "Northern States Power Company", an en dash, "Minnesota") is written with a hyphen in the page files; the tables keep
    it as written."""
    return text.replace(chr(0x2014), "-").replace(chr(0x2013), "-")


def build(in_dir, out_dir, lic=None, now=None):
    read = C.read_table
    d = read(os.path.join(in_dir, "company_directory.csv"))
    a = read(os.path.join(in_dir, "company_aliases.csv"))
    l = read(os.path.join(in_dir, "company_links.csv"))
    tables = sorted(set(l["input_table"]))
    lic = lic or C.licenses(tables)
    held_tables = sorted(t for t in tables if lic.get(t) != "public")
    sources = {t: source_line(os.path.join(in_dir, t + ".csv")) for t in tables}
    links_by = defaultdict(list)
    for r in l.to_dict("records"):
        links_by[r["company_id"]].append(r)
    alias_by = defaultdict(list)
    for r in a.to_dict("records"):
        if lic.get(r["input_table"]) == "public":
            alias_by[r["company_id"]].append(r)
    rows, shards = [], defaultdict(dict)
    held_only = 0
    held_counts = Counter()
    kinds, segments, states, grids = Counter(), Counter(), Counter(), Counter()
    for c in d.to_dict("records"):
        cid = c["entity_id"]
        mine = links_by[cid]
        pub = [x for x in mine if lic.get(x["input_table"]) == "public"]
        held = Counter(x["input_table"] for x in mine if lic.get(x["input_table"]) != "public")
        held_counts.update(held)
        if not pub:
            held_only += 1
            continue
        fig, fuel, yr, qt = figures(pub)
        st = Counter(x["state"] for x in pub if len(x["state"]) == 2 and x["input_table"] != "policy_actions")
        gr = sorted({g for x in pub for g in str(x["grid"]).split(";") if g})
        dates = sorted(x["date"] for x in pub if x["date"])
        names = sorted({x["alias"] for x in alias_by[cid]} - {c["name"]})
        st_list = [s for s, _ in st.most_common()]
        row = dict(id=slug_of(cid), name=c["name"], kind=c["kind"], segment=c["segment"],
                   hq_state=c["hq_state"], states=";".join(st_list), grids=";".join(gr), **fig,
                   n_links=len(pub), aka=" | ".join(names[:6]), first_seen=dates[0] if dates else "",
                   last_seen=dates[-1] if dates else "")
        rows.append(row)
        kinds[c["kind"]] += 1
        if c["segment"]:
            segments[c["segment"]] += 1
        for s in st_list:
            states[s] += 1
        for g in gr:
            grids[g] += 1
        parent_slug = slug_of(c["parent_id"]) if c.get("parent_id") else ""
        detail = dict(id=slug_of(cid), entity_id=cid, name=c["name"], kind=c["kind"], kind_basis=c["kind_basis"],
                      segment=c["segment"], segment_basis=c["segment_basis"], parent=c["parent"],
                      parent_id=parent_slug, parent_basis=c["parent_basis"], eia_utility_id=c["eia_utility_id"],
                      hq_state=c["hq_state"], hq_basis=c["hq_basis"], states=st_list, grids=gr,
                      first_seen=row["first_seen"], last_seen=row["last_seen"], figures=fig, fuel=fuel, years=yr,
                      quarters=qt, held=dict(sorted(held.items())), min_confidence=min(float(x["confidence"]) for x in pub),
                      names=[[x["alias"], x["input_table"], x["role"], int(x["n_rows"]), x["match_rule"]]
                             for x in sorted(alias_by[cid], key=lambda x: (x["input_table"], x["alias"]))],
                      links=[[x["entity_id"].split(":", 1)[1], tables.index(x["input_table"]), x["input_row"], x["role"],
                              "" if x["name_as_written"] == c["name"] else x["name_as_written"],
                              RULES.index(x["match_rule"]), x["mw"], x["usd"], x["date"], x["fuel"], x["state"],
                              x["grid"], x["detail"]]
                             for x in sorted(pub, key=lambda x: (x["input_table"], x["date"], x["input_row"]))])
        shards[shard(cid)][detail["id"]] = detail
    rows.sort(key=lambda r: (-r["footprint_mw"], -r["n_links"], r["id"]))
    shown_cols = [c for c in INDEX_COLS
                  if not (c in ("n_deals", "deals_mw") and "energy_deals" in held_tables)
                  and not (c in ("n_facilities", "facilities_mw") and "datacenter_facilities" in held_tables)]
    built = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = dict(built=built, method="docs/methods/companies.md", tables=tables, held_tables=held_tables,
                 held_links=dict(sorted(held_counts.items())), held_only=held_only, n_directory=len(d),
                 n_listed=len(rows), sources=sources, columns=shown_cols, link_columns=LINK_COLS, rules=RULES, confidence=C.CONF,
                 kinds=dict(kinds.most_common()), segments=dict(segments.most_common()),
                 states=dict(sorted(states.items())), grids=dict(sorted(grids.items())),
                 rows=[[r[c] for c in shown_cols] for r in rows])
    os.makedirs(os.path.join(out_dir, "c"), exist_ok=True)
    for name in os.listdir(os.path.join(out_dir, "c")):
        if name.endswith(".json"):
            os.remove(os.path.join(out_dir, "c", name))
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(no_dash(json.dumps(index, ensure_ascii=False, separators=(",", ":"))))
    for k, v in shards.items():
        with open(os.path.join(out_dir, "c", f"{k}.json"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(no_dash(json.dumps(dict(sorted(v.items())), ensure_ascii=False, separators=(",", ":"))))
    return index, shards


def main(argv=None):
    ap = argparse.ArgumentParser(description="The company pages' files")
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--out-dir", default=OUT)
    args = ap.parse_args(argv)
    index, shards = build(args.in_dir, args.out_dir)
    size = sum(os.path.getsize(os.path.join(args.out_dir, "c", f)) for f in os.listdir(os.path.join(args.out_dir, "c")))
    print(f"companies pages: {index['n_listed']:,} companies listed of {index['n_directory']:,} "
          f"({index['held_only']:,} named only in held tables: {', '.join(index['held_tables'])}); "
          f"{len(shards)} shards, {size / 1e6:.1f} MB; index {os.path.getsize(os.path.join(args.out_dir, 'index.json')) / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
