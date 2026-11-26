# Session 10233: the second set of measures for the data pages' audit (one question a block), standard library and PyYAML.
#   python runs/c10233/measures.py <worktree> <main copy's warehouse/output> <restate.json> <out.json>
# Counts and table names only: no row of a held table is printed.
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from posixpath import normpath, join as pjoin, dirname as pdir

import yaml

ROOT, OUTDIR, RJ, OUTJSON = sys.argv[1:5]
P = lambda *a: os.path.join(ROOT, *a)
R = json.load(open(RJ, encoding="utf-8"))
TODAY = "2026-11-26"
csv.field_size_limit(10 ** 8)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


cov = {r["table"]: r for r in rows(P("warehouse", "metadata", "coverage.csv"))}
live = yaml.safe_load(open(P("warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
full, recent = live.get("full") or [], (live.get("recent") or {}).get("tables") or []
chold, rhold = set(live.get("catalogue_hold") or []), set(live.get("review_hold") or [])
loaded = lambda t: any(re.match(p, t) for p in full) or any(re.match(p, t) for p in recent)
ST = json.load(open(P("site", "data", "license_status.json"), encoding="utf-8"))["tables"]
held = {t for t, r in ST.items() if r["status"] == "license needed" and TODAY >= r["from"]}
listed = {t for t, r in cov.items() if r["license"] == "public" and t not in chold and not (loaded(t) and t in rhold)}
rel = {r["table"]: r for r in rows(P("docs", "redivis", "release-v1", "tables.csv"))}
stan = {r["table"]: r for r in rows(P("docs", "redivis", "release-v1-stanford", "tables.csv"))}
out = {}

# a. the faults register against the site's copy, by id
fy = {str(f["id"]).strip(): f for f in yaml.safe_load(open(P("warehouse", "faults", "faults.yaml"), encoding="utf-8"))["faults"]}
fj = {r["id"]: r for r in json.load(open(P("site", "data", "data_faults.json"), encoding="utf-8"))["rows"]}
flat = lambda v: "" if v is None else re.sub(r"\s+", " ", str(v)).strip()
dif = []
for k in sorted(set(fy) | set(fj)):
    a, b = fy.get(k), fj.get(k)
    if not a or not b:
        dif.append((k, "only one side"))
        continue
    for fld in ("title", "status", "resolution", "first", "last", "open", "evidence", "erw_does", "resolution_reason", "recorded_in"):
        if flat(a.get(fld)) != flat(b.get(fld)):
            dif.append((k, fld))
    if [t.strip() for t in flat(a.get("tables")).split(";") if t.strip()] != b["tables"]:
        dif.append((k, "tables"))
out["faults_by_id_differences"] = dif
out["faults_held_grid_publisher"] = sorted(k for k, f in fy.items() if re.search(r"NYISO|ISO-NE|ISO New England|MISO|New York Independent", flat(f["publisher"])))

# b. tier derived without the derived flag (the "(derived)" mark is drawn from the flag)
out["listed_tier_derived_flag_no"] = sorted(t for t in listed if cov[t]["tier"] == "derived" and cov[t]["derived"] != "yes")
out["all_tier_derived_flag_no"] = sum(1 for t, r in cov.items() if r["tier"] == "derived" and r["derived"] != "yes")
out["all_flag_yes_tier_not_derived"] = sorted((t, r["tier"]) for t, r in cov.items() if r["derived"] == "yes" and r["tier"] != "derived")[:12]
out["all_flag_yes_tier_not_derived_n"] = sum(1 for t, r in cov.items() if r["derived"] == "yes" and r["tier"] != "derived")

# c, d, g. the tables on this machine: header URL, entity namespace, row counts against coverage
nourl, ns, counts = [], [], []
for t, r in sorted(cov.items()):
    fp = os.path.join(OUTDIR, t + ".csv")
    if not os.path.isfile(fp):
        continue
    hdr, n, first, cols = [], 0, None, None
    big = os.path.getsize(fp) > 400 * 1024 * 1024
    with open(fp, encoding="utf-8", errors="replace", newline="") as f:
        lines = (l for l in f)
        for line in lines:
            if line.startswith("#"):
                hdr.append(line)
                continue
            cols = next(csv.reader([line]))
            break
        if cols is not None and t in listed and not big:
            rd = csv.reader(lines)
            for row in rd:
                if first is None:
                    first = row
                n += 1
            counts.append((t, int(r["n_rows"] or 0), n))
        elif cols is not None:
            try:
                first = next(csv.reader(lines))
            except StopIteration:
                first = None
    h = "".join(hdr)
    if not re.search(r"https?://", h):
        nourl.append((t, r["derived"], r["tier"], r["license"]))
    if first and cols and (cols[:2] == ["entity_id", "entity_type"] or "event_id" not in cols):
        e = first[0]
        if (e.split(":", 1)[0] if ":" in e else "") != t.split("_", 1)[0]:
            ns.append((t, e.split(":", 1)[0] if ":" in e else "(no namespace)"))
out["header_no_url"] = dict(n=len(nourl), by_derived=dict(Counter(x[1] for x in nourl)), by_tier=dict(Counter(x[2] for x in nourl)),
                            listed=sorted(x[0] for x in nourl if x[0] in listed), examples=[x[0] for x in nourl][:10])
out["namespace_not_first_part"] = dict(n=len(ns), by_ns=dict(Counter(x[1] for x in ns).most_common(12)),
                                       listed_public=sorted(x[0] for x in ns if x[0] in listed and x[0] not in held)[:15])
out["listed_rows_on_disk_vs_coverage"] = dict(compared=len(counts), equal=sum(1 for c in counts if c[1] == c[2]),
                                              differ=[c for c in counts if c[1] != c[2] and c[0] not in held],
                                              differ_held_n=sum(1 for c in counts if c[1] != c[2] and c[0] in held))

# e. a news story dated after the coverage build
ni = os.path.join(OUTDIR, "news_index.csv")
if os.path.isfile(ni):
    with open(ni, encoding="utf-8", newline="") as f:
        n_skip = 0
        pos = f.tell()
        for line in f:
            if line.startswith("#"):
                n_skip += 1
                continue
            break
    with open(ni, encoding="utf-8", newline="") as f:
        for _ in range(n_skip):
            f.readline()
        rr = list(csv.DictReader(f))
    fut = [r for r in rr if r["event_date"][:10] > TODAY]
    out["news_index_rows"] = len(rr)
    out["news_index_after_today"] = len(fut)
    out["news_index_after_today_dates"] = dict(Counter(r["event_date"][:10] for r in fut))
    out["news_index_max"] = max(r["event_date"] for r in rr)
out["coverage_news_index"] = {k: cov["news_index"][k] for k in ("ts_min", "ts_max", "n_rows", "last_run")}

# f. the Redivis links of listed rows not on the linked dataset, and the tables the Access section names
red = sorted(t for t in listed if t not in held and not loaded(t))
out["listed_redivis_links"] = len(red)
out["listed_redivis_not_on_old_dataset"] = [(t, rel.get(t, {}).get("in_v1", "absent"), "stanford " + stan.get(t, {}).get("in_v1", "absent"),
                                              rel.get(t, {}).get("reason", "")[:150]) for t in red if rel.get(t, {}).get("in_v1") != "yes"]
for t in ("ercot_all_hub_prices_history", "eia860m_operating_generators", "eia860m_planned_generators", "energy_deals", "news_index", "energy_projects"):
    c = cov.get(t, {})
    out.setdefault("access_tables", {})[t] = dict(license=c.get("license"), loaded=loaded(t), catalogue_hold=t in chold, held=t in held,
                                                   listed=t in listed, old_dataset=rel.get(t, {}).get("in_v1", "absent"),
                                                   stanford=stan.get(t, {}).get("in_v1", "absent"))

# h. the tables the rule for impossible values is written into but not applied to
HELD_RULE = ["carbon_intensity_hourly", "carbon_intensity_daily", "carbon_intensity_monthly", "cost_of_power_monthly", "cost_of_power_carbon",
             "ba_supply_monthly", "ai_power_regions", "caiso_reliability_daily", "event_window_daily"]
out["impossible_rule_not_applied"] = {t: dict(listed=t in listed, license_held=t in held, coverage=cov.get(t, {}).get("license", "absent")) for t in HELD_RULE}

# i. the public table with an internal source that /data does not list
src = rows(P("warehouse", "metadata", "sources.csv"))
out["internal_sources_of_public_tables"] = {t: sorted(r["source"] for r in src if r["license"] == "internal" and t in [x.strip() for x in r["tables"].split(";")])
                                            for t in ("nyiso_load_queue", "news_index", "energy_deals", "datacenter_projects")}
out["declared_license_header"] = {}
for t in ("news_index", "nyiso_load_queue"):
    fp = os.path.join(OUTDIR, t + ".csv")
    if os.path.isfile(fp):
        with open(fp, encoding="utf-8", errors="replace") as f:
            out["declared_license_header"][t] = [l.strip()[:160] for l in f if l.startswith("#") and "License" in l][:3]

# k. every link of a bundled method note, resolved as lib/markdown.ts resolves it
INTERNAL = {"thesis_builder", "digest_scoring", "roundup_selection", "forecast"}
mdir = P("docs", "methods")
notes = {f[:-3] for f in os.listdir(mdir) if f.endswith(".md")}
link_re = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
broken, to_internal, checked = defaultdict(list), defaultdict(list), 0
for n in sorted(notes - INTERNAL):
    s = open(os.path.join(mdir, n + ".md"), encoding="utf-8").read()
    s = re.sub(r"```.*?```", "", s, flags=re.S)
    for m in link_re.finditer(s):
        href = m.group(1)
        if re.match(r"^([a-z]+:|#)", href, re.I):
            continue
        checked += 1
        if href.startswith("/"):
            mm = re.match(r"^/data/methods/([\w-]+)", href)
            if mm and mm.group(1) not in notes:
                broken[n].append(href)
            elif mm and mm.group(1) in INTERNAL:
                to_internal[n].append(href)
            continue
        target = normpath(pjoin("docs/methods", href.split("#")[0]))
        if not target:
            continue
        mm = re.match(r"^docs/methods/([\w-]+)\.md$", target)
        if mm:
            if mm.group(1) not in notes:
                broken[n].append(href)
            elif mm.group(1) in INTERNAL:
                to_internal[n].append(href)
        elif not os.path.exists(P(*target.split("/"))):
            broken[n].append(href)
out["method_links_checked"] = checked
out["method_links_broken"] = dict(broken)
out["method_links_to_internal_notes"] = dict(to_internal)

# l. the /data page's own links into the methods and the standard
pg = open(P("site", "app", "data", "page.tsx"), encoding="utf-8").read()
out["data_page_method_links"] = {s: (s in notes and s not in INTERNAL) for s in re.findall(r"/data/methods/([\w-]+)", pg)}
fp_ = open(P("site", "app", "data", "faults", "page.tsx"), encoding="utf-8").read()
out["faults_page_method_links"] = {s: (s in notes and s not in INTERNAL) for s in re.findall(r"/data/methods/([\w-]+)", fp_)}
std = open(P("docs", "datastandard.md"), encoding="utf-8").read()
out["dictionary_markers"] = dict(shape_a=std.find("## Shape (a)") >= 0, decisions=std.find("## Decisions", std.find("## Shape (a)")) >= 0)

json.dump(out, open(OUTJSON, "w", encoding="utf-8"), indent=1, default=str)
for k, v in out.items():
    s = json.dumps(v, default=str)
    print(f"{k}: {s if len(s) < 700 else s[:700] + ' ...'}")
