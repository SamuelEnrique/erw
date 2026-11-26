# Session 10233 (chain 710, part D): the data and methodology pages (/data, /data/faults, /data/licenses,
# /data/methods/<slug>, /data/standard) restated from the files they read, by the standard library and PyYAML only,
# written apart from the site's code and the loader. Reads, never writes, anything outside runs/c10233/.
#   python runs/c10233/restate.py <worktree> <main copy's warehouse/output> <out.json>
# Counts only: no row of a held table is printed.
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

import yaml

ROOT, OUTDIR, OUTJSON = sys.argv[1], sys.argv[2], sys.argv[3]
TODAY = "2026-11-26"
P = lambda *a: os.path.join(ROOT, *a)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


res = {}

# ---- 1. coverage.csv and the live catalogue as the loader would write it ------------------------------------------
cov = rows(P("warehouse", "metadata", "coverage.csv"))
res["coverage_tables"] = len(cov)
res["coverage_by_license"] = dict(Counter(r["license"] for r in cov))
res["coverage_by_tier"] = dict(Counter(r["tier"] for r in cov))
res["coverage_by_validator"] = dict(Counter(r["validator_status"] for r in cov))
live = yaml.safe_load(open(P("warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
full = live.get("full") or []
recent = (live.get("recent") or {}).get("tables") or []
chold = set(live.get("catalogue_hold") or [])
rhold = set(live.get("review_hold") or [])


def loaded(t):
    return any(re.match(p, t) for p in full) or any(re.match(p, t) for p in recent)


status = json.load(open(P("site", "data", "license_status.json"), encoding="utf-8"))
ST = status["tables"]
held_today = {t for t, r in ST.items() if r["status"] == "license needed" and TODAY >= r["from"]}

public = [r for r in cov if r["license"] == "public"]
listed, not_listed = [], Counter()
for r in public:
    t = r["table"]
    if t in chold:
        not_listed["catalogue_hold"] += 1
        continue
    flag = ("review" if t in rhold else "yes") if loaded(t) else "no"
    if flag == "review":
        not_listed["review_hold, loaded"] += 1
        continue
    listed.append(dict(r, in_live_set=flag))
res["public_tables"] = len(public)
res["listed"] = len(listed)
res["public_not_listed"] = dict(not_listed)
res["review_hold_not_loaded_but_listed"] = sorted(r["table"] for r in listed if r["table"] in rhold)
dl = Counter()
for r in listed:
    dl["held" if r["table"] in held_today else ("download" if r["in_live_set"] == "yes" else "redivis")] += 1
res["listed_download_cell"] = dict(dl)
res["listed_rows_sum"] = sum(int(r["n_rows"] or 0) for r in listed)
res["listed_ts_min"] = min(r["ts_min"] for r in listed if r["ts_min"])
res["listed_ts_max"] = max(r["ts_max"] for r in listed if r["ts_max"])
res["listed_ts_max_after_today"] = sorted((r["table"], r["ts_max"][:10]) for r in listed if r["ts_max"][:10] > TODAY)
res["listed_last_run_missing"] = sorted(r["table"] for r in listed if not r["last_run"])
lr = sorted(r["last_run"] for r in listed if r["last_run"])
res["listed_last_run_range"] = [lr[0], lr[-1]] if lr else None
res["listed_last_run_before_2026_11_01"] = sum(1 for x in lr if x < "2026-11-01")
res["listed_last_run_before_2026_10_01"] = sum(1 for x in lr if x < "2026-10-01")
res["listed_by_tier"] = dict(Counter(r["tier"] for r in listed))
res["listed_derived_yes"] = sum(1 for r in listed if r["derived"] == "yes")
res["listed_validator_not_pass"] = sorted((r["table"], r["validator_status"]) for r in listed if r["validator_status"] != "pass")
res["listed_held"] = sorted(r["table"] for r in listed if r["table"] in held_today)

# ---- 2. the packages' verdicts beside the License column (site/data/table_verdicts.json) --------------------------
verd = json.load(open(P("site", "data", "table_verdicts.json"), encoding="utf-8"))
vc = Counter()
for r in listed:
    v = (verd.get(r["table"]) or [""])[0]
    held = r["table"] in held_today
    vc[f"license cell {'license needed' if held else 'public'}; tools cell {'calls' if (not v or v == 'public') else 'Not public (' + v + ')'}"] += 1
res["listed_license_vs_tools"] = dict(vc)
res["listed_public_cell_but_not_public_verdict"] = sorted(
    (r["table"], verd[r["table"]][0]) for r in listed
    if r["table"] not in held_today and r["table"] in verd and verd[r["table"]][0] != "public")
res["listed_held_but_calls_offered"] = sorted(
    r["table"] for r in listed if r["table"] in held_today and (verd.get(r["table"]) or ["public"])[0] == "public")
res["listed_no_verdict"] = sorted(r["table"] for r in listed if r["table"] not in verd)

# ---- 3. Redivis: the release list against the Redivis link of a listed row ------------------------------------------
rel = {r["table"]: r for r in rows(P("docs", "redivis", "release-v1", "tables.csv"))}
res["release_v1_rows"] = len(rel)
res["release_v1_by_in_v1"] = dict(Counter(r["in_v1"] for r in rel.values()))
rc = Counter()
for r in listed:
    cell = "held" if r["table"] in held_today else ("download" if r["in_live_set"] == "yes" else "redivis")
    rc[f"{cell}; release list {rel[r['table']]['in_v1'] if r['table'] in rel else 'absent'}"] += 1
res["listed_cell_vs_release"] = dict(rc)
res["listed_not_in_release_list"] = sum(1 for r in listed if r["table"] not in rel)
stan = {r["table"]: r for r in rows(P("docs", "redivis", "release-v1-stanford", "tables.csv"))}
res["stanford_rows"] = len(stan)
res["listed_redivis_link_on_neither"] = sum(
    1 for r in listed if r["in_live_set"] == "no" and r["table"] not in held_today
    and (rel.get(r["table"], {}).get("in_v1") not in ("yes",)) and r["table"] not in stan)

# ---- 4. the license record: the csv, the site's json, the verdicts -------------------------------------------------
lcsv = {r["table"]: r for r in rows(P("warehouse", "metadata", "license_status.csv"))}
res["license_csv_rows"] = len(lcsv)
res["license_json_rows"] = len(ST)
diff = []
for t in sorted(set(lcsv) | set(ST)):
    a, b = lcsv.get(t), ST.get(t)
    if not a or not b:
        diff.append((t, "only in " + ("json" if b else "csv")))
        continue
    pa = [p.strip() for p in a["publishers"].split(";") if p.strip()]
    if a["status"] != b["status"] or a["from"] != b["from"] or pa != b["publishers"]:
        diff.append((t, "differs"))
res["license_csv_vs_json"] = diff
res["license_json_hold_values"] = dict(Counter(r.get("hold", "(none)") for r in ST.values()))
held_all = [t for t, r in ST.items() if r["status"] == "license needed"]
res["held_count"] = len(held_all)
res["held_from_file"] = status["from"]
res["held_from_days"] = dict(Counter(r["from"] for r in ST.values()))
bp = Counter(p for t in held_all for p in ST[t]["publishers"])
res["held_by_publisher"] = sorted(bp.items(), key=lambda x: (-x[1], x[0]))
covby = {r["table"]: r for r in cov}
res["held_coverage_license"] = dict(Counter(covby[t]["license"] if t in covby else "not in coverage" for t in held_all))
res["held_not_in_coverage"] = sorted(t for t in held_all if t not in covby)
res["held_internal_in_coverage"] = sorted(t for t in held_all if t in covby and covby[t]["license"] != "public")
res["held_on_data_page"] = sum(1 for t in held_all if t in {r["table"] for r in listed})
res["held_where"] = dict(Counter(
    "listed on /data" if t in {r["table"] for r in listed} else
    ("not in coverage" if t not in covby else ("internal in coverage" if covby[t]["license"] != "public" else
     ("catalogue_hold" if t in chold else "review_hold"))) for t in held_all))
# the verdicts, read as build-content.mjs bundles them (a note with an unquoted comma is joined back)
with open(P("warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
    rd = list(csv.reader(f))
head, body = rd[0], rd[1:]
V = []
for r in body:
    if len(r) < len(head):
        continue
    r = r[:len(head) - 1] + [",".join(r[len(head) - 1:])]
    V.append(dict(zip(head, r)))
today = [v for v in V if v["verdict"] == "may be public"]
res["verdict_rows"] = len(V)
res["verdicts"] = dict(Counter(v["verdict"] for v in V))
res["permissive_both"] = sum(1 for v in today if v["if_commercial"] == "may be public")
res["permissive_today_only"] = sum(1 for v in today if v["if_commercial"] != "may be public")
res["verdict_keys_duplicated"] = sorted(k for k, n in Counter(v["key"] for v in V).items() if n > 1)
for fp in ("docs/reviews/licenses/nyiso-permission-letter.md", "docs/reviews/licenses/miso-permission-letter.md",
           "docs/reviews/licenses/pjm-permission-letter.md", "docs/reviews/licenses/spp-permission-letter.md",
           "docs/reviews/isone-permission-email.md", "docs/licenses_costs.md", "docs/licenses.md"):
    res.setdefault("linked_files_exist", {})[fp] = os.path.exists(P(*fp.split("/")))

# ---- 5. sources.csv against the standard's license rule -------------------------------------------------------------
src = rows(P("warehouse", "metadata", "sources.csv"))
res["sources_rows"] = len(src)
res["sources_by_license"] = dict(Counter(r["license"] for r in src))
res["sources_internal_not_pjm"] = sum(1 for r in src if r["license"] == "internal" and "pjm" not in (r["source"] + r["publisher"]).lower())
res["sources_internal_pjm"] = sum(1 for r in src if r["license"] == "internal" and "pjm" in (r["source"] + r["publisher"]).lower())
internal_src_tables = defaultdict(list)
for r in src:
    if r["license"] == "internal":
        for t in [x.strip() for x in r["tables"].split(";") if x.strip()]:
            internal_src_tables[t].append(r["source"])
res["public_tables_with_an_internal_source"] = sorted(t for t in internal_src_tables if t in covby and covby[t]["license"] == "public")
res["public_listed_with_an_internal_source"] = sorted(t for t in internal_src_tables if t in {r["table"] for r in listed})
src_tables = {x.strip() for r in src for x in r["tables"].split(";") if x.strip()}
res["listed_tables_no_registry_source"] = sum(1 for r in listed if r["table"] not in src_tables)

# ---- 6. faults: the register restated against the site's copy -------------------------------------------------------
fy = yaml.safe_load(open(P("warehouse", "faults", "faults.yaml"), encoding="utf-8"))["faults"]
fj = json.load(open(P("site", "data", "data_faults.json"), encoding="utf-8"))
flat = lambda v: "" if v is None else str(v).strip()
ftables = sorted({t.strip() for f in fy for t in flat(f.get("tables")).split(";") if t.strip()})
res["faults_restated"] = dict(faults=len(fy), by_status=dict(Counter(flat(f["status"]) for f in fy)),
                              by_resolution=dict(Counter(flat(f["resolution"]) for f in fy)),
                              tables_touched=len(ftables), with_open=sum(1 for f in fy if flat(f.get("open"))))
res["faults_site_copy"] = dict(faults=fj["faults"], by_status=fj["by_status"], by_resolution=fj["by_resolution"],
                               tables_touched=fj["tables_touched"], with_open=fj["with_open"], built=fj["built"])
res["faults_row_fields_differ"] = sorted(
    f["id"] for f, j in zip(fy, fj["rows"])
    if flat(f["id"]) != j["id"] or flat(f["status"]) != j["status"] or flat(f["resolution"]) != j["resolution"]
    or flat(f.get("open")) != j["open"] or [t.strip() for t in flat(f.get("tables")).split(";") if t.strip()] != j["tables"])
res["faults_tables_not_in_coverage"] = sorted(t for t in ftables if t not in covby)
res["faults_tables_internal"] = sorted(t for t in ftables if t in covby and covby[t]["license"] != "public")
res["faults_tables_held"] = sorted(t for t in ftables if t in held_all)
res["faults_without_last_and_open"] = sum(1 for f in fy if not flat(f.get("last")))

# ---- 7. the method notes: the list, the links into it, the derived tables it should cover -------------------------
INTERNAL = {"thesis_builder", "digest_scoring", "roundup_selection", "forecast"}
mdir = P("docs", "methods")
notes = {f[:-3] for f in os.listdir(mdir) if f.endswith(".md")}
bundled = notes - INTERNAL
res["method_notes_md"] = len(notes)
res["method_notes_listed"] = len(bundled)
links = defaultdict(set)
pat = re.compile(r"/data/methods/([A-Za-z0-9_-]+)")
mdpat = re.compile(r"docs/methods/([A-Za-z0-9_-]+)\.md")
for base in ("site/app", "site/lib", "site/components", "site/data/site.json", "docs/methods", "docs/datastandard.md", "docs/licenses.md"):
    bp_ = P(*base.split("/"))
    files = [bp_] if os.path.isfile(bp_) else [os.path.join(d, f) for d, _, fs in os.walk(bp_) for f in fs
                                                if f.endswith((".ts", ".tsx", ".md", ".json"))]
    for fp in files:
        try:
            s = open(fp, encoding="utf-8").read()
        except Exception:
            continue
        rel_ = os.path.relpath(fp, ROOT).replace("\\", "/")
        for m in pat.finditer(s):
            links[m.group(1)].add(rel_)
        if rel_.startswith("docs/") or rel_.startswith("site/data"):
            for m in mdpat.finditer(s):
                links[m.group(1)].add(rel_ + " (md path)")
res["linked_slugs"] = len(links)
res["linked_slugs_missing"] = {k: sorted(v)[:6] for k, v in sorted(links.items()) if k not in notes}
res["linked_slugs_internal"] = {k: sorted(v)[:6] for k, v in sorted(links.items()) if k in INTERNAL}
texts = {n: open(os.path.join(mdir, n + ".md"), encoding="utf-8").read() for n in bundled}
derived = [r for r in listed if r["derived"] == "yes" or r["tier"] == "derived"]
nomethod = []
for r in derived:
    w = re.compile(r"(?<![a-z0-9_])" + re.escape(r["table"]) + r"(?![a-z0-9_])")
    if not any(w.search(s) for s in texts.values()):
        nomethod.append(r["table"])
res["listed_derived"] = len(derived)
res["listed_derived_no_note_names_it"] = sorted(nomethod)
res["listed_derived_tier_vs_flag"] = dict(Counter(f"derived={r['derived']} tier={r['tier']}" for r in derived))

# ---- 8. coverage.md against coverage.csv -------------------------------------------------------------------------
md = open(P("docs", "coverage.md"), encoding="utf-8").read().splitlines()
mdtables = [l.split("|")[1].strip().strip("`") for l in md if l.startswith("| ") and not l.startswith("| Table") and not l.startswith("|---")]
res["coverage_md_rows"] = len(mdtables)
res["coverage_md_vs_csv"] = dict(only_md=sorted(set(mdtables) - set(covby))[:10], only_csv=sorted(set(covby) - set(mdtables))[:10])

# ---- 9. the standard against the validator ------------------------------------------------------------------------
sys.path.insert(0, P("warehouse", "validate"))
import erw_validate as V_  # noqa: E402
std = open(P("docs", "datastandard.md"), encoding="utf-8").read()
units_line = next(l for l in std.splitlines() if l.startswith("- **Units.**"))
named = set(re.findall(r"`([^`]+)`", units_line))
res["units_validator"] = len(V_.UNITS)
res["units_in_units_bullet_not_validator"] = sorted(u for u in named if u not in V_.UNITS and not u.startswith("unit"))
res["units_validator_not_in_units_bullet"] = sorted(V_.UNITS - named)
res["units_validator_not_anywhere_in_standard"] = sorted(u for u in V_.UNITS if f"`{u}`" not in std)
res["standard_version_line"] = std.splitlines()[0]
res["redivis_cap_line"] = next(l for l in std.splitlines() if "caps a dataset at 1000 tables" in l)

# ---- 10. the tables on this machine: headers and first row against the general rules -------------------------------
REQ = {"series": ["entity", "variable", "ts_utc", "value"] + V_.RESERVED, "entities": V_.ENTITIES_COLS, "events": V_.EVENTS_COLS}
chk = Counter()
bad_x, bad_ns, no_ret, no_url, no_py = [], [], [], [], []
held_names = set(held_all)
for r in cov:
    t = r["table"]
    fp = os.path.join(OUTDIR, t + ".csv")
    if not os.path.isfile(fp):
        continue
    chk["on_disk"] += 1
    hdr, cols, first = [], None, None
    with open(fp, encoding="utf-8", errors="replace", newline="") as f:
        for line in f:
            if line.startswith("#"):
                hdr.append(line)
                continue
            if cols is None:
                cols = next(csv.reader([line]))
                continue
            first = next(csv.reader([line]))
            break
    if not cols:
        continue
    shape = "entities" if cols[:2] == ["entity_id", "entity_type"] else ("events" if "event_id" in cols else "series")
    chk[shape] += 1
    extra = [c for c in cols if c not in REQ[shape] and not c.startswith("x_")]
    if extra:
        bad_x.append(t)
    h = "".join(hdr)
    if not re.search(r"Retrieved", h):
        no_ret.append(t)
    if not re.search(r"https?://", h):
        no_url.append(t)
    if not re.search(r"\.py\b", h):
        no_py.append(t)
    if first and shape in ("series", "entities"):
        e = first[0]
        ns = e.split(":", 1)[0] if ":" in e else ""
        if ns != t.split("_", 1)[0]:
            bad_ns.append(t)
    chk[f"{shape} with extra columns not x_"] += 1 if extra else 0
res["disk"] = dict(chk)
res["disk_extra_not_x"] = len(bad_x)
res["disk_extra_not_x_by_license_public"] = sum(1 for t in bad_x if covby[t]["license"] == "public")
res["disk_header_no_retrieved"] = len(no_ret)
res["disk_header_no_url"] = len(no_url)
res["disk_header_no_connector"] = len(no_py)
res["disk_namespace_not_first_part"] = len(bad_ns)
res["disk_namespace_examples"] = sorted(t for t in bad_ns if t not in held_names)[:8]
res["names_over_40"] = sorted(r["table"] for r in cov if len(r["table"]) > 40)
res["series_names_under_3_parts"] = sorted(r["table"] for r in cov if r["interval"] not in ("snapshot", "event") and len(r["table"].split("_")) < 3)

json.dump(res, open(OUTJSON, "w", encoding="utf-8"), indent=1, default=str)
for k, v in res.items():
    s = json.dumps(v, default=str)
    print(f"{k}: {s if len(s) < 400 else s[:400] + ' ...'}")
