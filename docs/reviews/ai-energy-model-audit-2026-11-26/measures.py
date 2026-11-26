"""Session 10221: /ai-energy, one rule changed at a time and each claim's size, from the page's own file
(site/data/ai_energy.json), the session's source rows (warehouse/sources/ai_energy_published/rows.csv) and the page's
own figure() as figure_probe.mjs ran it. Nothing here is a figure the page prints; these are the audit's measures.

    python measures.py <worktree root> <figure_probe.json> <out json>
"""
import csv
import json
import os
import re
import sys
from datetime import date

root, probe_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
F = json.load(open(os.path.join(root, "site", "data", "ai_energy.json"), encoding="utf-8"))
rows = F["rows"]
by = {r["event_id"]: r for r in rows}
M = {}

# 1. what the rows measure, by kind (the page's name says "per AI query"; its lead names a token)
def kind(m):
    if m.startswith(("energy per query", "energy per prompt", "energy per inference", "energy per 1,000 inferences")):
        return "per query, prompt or inference"
    if m.startswith("energy of a training run"):
        return "a training run"
    if m.startswith("energy of a fleet"):
        return "a fleet in a year"
    return "a deployment or a project's experiments"
kinds = {}
for r in rows:
    kinds.setdefault(kind(r["x_measures"]), []).append(r["event_id"])
M["by_kind"] = {k: len(v) for k, v in kinds.items()}
M["per_token_rows"] = [r["event_id"] for r in rows if "token" in (r["x_measures"] + r["x_subject"]).lower()]

# 2. the fleet rows: their boundary as the row words it, and (the audit's own arithmetic, never the page's) the average
#    draw in MW that a load forecaster would read from a year's energy
HOURS = {"2019": 8760, "2020": 8784, "2024": 8784, "fiscal year 2025": 8760}
fleet = []
for r in rows:
    if kind(r["x_measures"]) != "a fleet in a year":
        continue
    twh = r["x_value"] * {"TWh": 1, "MWh": 1e-6}[r["x_unit"]]
    per = next(k for k in HOURS if r["x_period"].startswith(k))
    fleet.append({"id": r["event_id"], "measures": r["x_measures"], "subject": r["x_subject"], "period": r["x_period"], "TWh": round(twh, 3),
                  "average MW": round(twh * 1e6 / HOURS[per]), "says United States": "United States" in (r["x_subject"] + r["x_basis"]) or " US " in (r["x_subject"] + r["x_basis"]),
                  "says AI's share": "share" in (r["x_subject"] + r["x_basis"]).lower()})
M["fleet_rows"] = fleet

# 3. the measure filter: as worded (each parenthesis its own measure) against grouped on the words before " ("
worded = sorted({r["x_measures"] for r in rows})
groups = {}
for r in rows:
    groups.setdefault(r["x_measures"].split(" (")[0], []).append(r["event_id"])
M["measures_offered"] = len(worded)
M["measures_grouped"] = len(groups)
M["grouped_rows"] = {k: len(v) for k, v in sorted(groups.items())}
M["fleet_filter_rows_as_worded"] = {m: sum(1 for r in rows if r["x_measures"] == m) for m in worded if m.startswith("energy of a fleet")}
M["training_filter_rows_as_worded"] = {m: sum(1 for r in rows if r["x_measures"] == m) for m in worded if m.startswith("energy of a training")}

# 4. one thing in two publications
nas_s, nas_p = by["ai_energy:strubell_2019_2"], by["ai_energy:patterson_2022_3"]
s_kwh, p_kwh = nas_s["x_value"], nas_p["x_value"] * 1000
M["nas"] = {"strubell subject": nas_s["x_subject"], "strubell kWh (times PUE)": s_kwh, "strubell measures": nas_s["x_measures"],
            "patterson 2022 subject": nas_p["x_subject"], "patterson 2022 kWh": p_kwh, "patterson measures": nas_p["x_measures"],
            "ratio": round(s_kwh / p_kwh, 2)}
ms_p = by["ai_energy:patterson_2022_2"]
ms_own_fy20 = float(by["ai_energy:microsoft_2026_1"]["x_printed"].split()[1].replace(",", ""))
M["microsoft_2020"] = {"patterson 2022 TWh (2020)": ms_p["x_value"], "fact sheet FY20 TWh (first number of its printed words)": ms_own_fy20 / 1e6,
                       "gap percent": round((ms_p["x_value"] - ms_own_fy20 / 1e6) / (ms_own_fy20 / 1e6) * 100, 2)}
meta_series = [float(x.replace(",", "")) for x in by["ai_energy:meta_2025_1"]["x_printed"].split()[3:]]
ms_series = [float(x.replace(",", "")) for x in by["ai_energy:microsoft_2026_1"]["x_printed"].split()[1:]]
M["series_in_the_printed_words"] = {"meta data centers 2020 to 2024 MWh": meta_series, "meta 2024 over 2020": round(meta_series[-1] / meta_series[0], 2),
                                    "microsoft FY20 to FY25 MWh": ms_series, "microsoft FY25 over FY20": round(ms_series[-1] / ms_series[0], 2)}

# 5. the digits shown against the digits printed
probe = json.load(open(probe_path, encoding="utf-8"))
digits = []
for p in probe["rows"]:
    r = by[p["id"]]
    toks = re.findall(r"\d[\d,]*\.?\d*(?:\s*[x×]\s*10\s*[−-]\s*\d+)?", r["x_printed"])
    match = None
    for t in toks:
        t2 = t.replace(",", "")
        sci = re.match(r"([\d.]+)\s*[x×]\s*10\s*[−-]\s*(\d+)", t2)
        v = float(sci.group(1)) * 10 ** -int(sci.group(2)) if sci else float(t2)
        if abs(v - r["x_value"]) < 1e-9 * max(1, abs(r["x_value"])):
            match = t.strip()
    shown = p["shown"].replace(",", "")
    same = match is not None and match.replace(",", "") == shown
    digits.append({"id": p["id"], "printed": match, "shown": p["shown"], "same digits": same})
M["value_in_printed_words"] = sum(1 for d in digits if d["printed"] is not None)
M["digits_differ"] = [d for d in digits if not d["same digits"]]
M["figure_probes"] = probe["probes"]

# 6. dates the publication does not print
M["dates_not_printed_by_the_publication"] = sorted({r["x_title"] for r in rows if "the date is" in r["x_basis"]})
M["newest_rests_on"] = sorted(rows, key=lambda r: r["event_date"], reverse=True)[0]["x_basis"]

# 7. vintage
today = date(2026, 11, 26)
tr = [r for r in rows if kind(r["x_measures"]) == "a training run"]
newest_tr = max(tr, key=lambda r: r["event_date"])
M["training_rows_dates"] = sorted({r["event_date"] for r in tr})
M["newest_training_figure"] = {"id": newest_tr["event_id"], "date": newest_tr["event_date"], "years before 2026-11-26": round((today - date.fromisoformat(newest_tr["event_date"])).days / 365.25, 2)}
M["per_query_rows_dates"] = sorted({r["event_date"] for r in rows if kind(r["x_measures"]) == "per query, prompt or inference"})

# 8. peer review and the publisher kind
M["peer_reviewed_by_rule"] = sorted({r["x_title"] for r in rows if r["x_publisher_kind"] == "peer-reviewed paper"})
M["publisher_kind_values"] = sorted({r["x_publisher_kind"] for r in rows})
M["peer_paper_publishers"] = sorted({r["parties"] for r in rows if r["x_publisher_kind"] == "peer-reviewed paper"})

# 9. estimates of another maker's model: does the row's basis say so (the note's Limits: "x_basis says so")
est = []
for eid in ("ai_energy:strubell_2019_1", "ai_energy:strubell_2019_2", "ai_energy:patterson_2021_5"):
    r = by[eid]
    est.append({"id": eid, "subject": r["x_subject"], "basis": r["x_basis"],
                "basis names another maker": any(w in r["x_basis"] for w in ("Google", "OpenAI", "So et al", "another"))})
M["estimates_of_another_model"] = est

# 10. the page file against the session's source rows
src = list(csv.DictReader(open(os.path.join(root, "warehouse", "sources", "ai_energy_published", "rows.csv"), encoding="utf-8")))
pairs = {"date": "event_date", "publisher": "parties", "url": "source_url", "publisher_kind": "x_publisher_kind", "peer_reviewed": "x_peer_reviewed",
         "title": "x_title", "authors": "x_authors", "page": "x_page", "printed": "x_printed", "unit": "x_unit", "measures": "x_measures",
         "subject": "x_subject", "period": "x_period", "basis": "x_basis"}
diff = []
for s in src:
    r = by.get(f"ai_energy:{s['id']}")
    if r is None:
        diff.append(f"{s['id']}: not in the page file")
        continue
    for a, b in pairs.items():
        if s[a] != r[b]:
            diff.append(f"{s['id']}: {a}")
    if float(s["value"]) != r["x_value"]:
        diff.append(f"{s['id']}: value")
M["source_rows"] = len(src)
M["source_against_page_file"] = diff or "equal"

json.dump(M, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(M, ensure_ascii=False, indent=1))
