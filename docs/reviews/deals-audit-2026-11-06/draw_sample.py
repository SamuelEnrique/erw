"""Session 2231: the audit's sample. Deals: every fifth row of the newest 600 by extracted_at then event_date (the table
holds 529, so every fifth of all 529); facilities: every k-th row of the 163 to make 60. Each row with its stories'
title and summary and its evidence sentences, written as JSON for reading."""
import json, sys
import pandas as pd

O = "warehouse/output/"
OUT = sys.argv[1]
d = pd.read_csv(O + "energy_deals.csv", comment="#", low_memory=False, dtype=str).fillna("")
e = pd.read_csv(O + "energy_deals_evidence.csv", comment="#", low_memory=False, dtype=str).fillna("")
p = pd.read_csv(O + "datacenter_projects.csv", comment="#", low_memory=False, dtype=str).fillna("")
pe = pd.read_csv(O + "datacenter_projects_evidence.csv", comment="#", low_memory=False, dtype=str).fillna("")
s = pd.read_csv(O + "news_stories.csv", comment="#", low_memory=False, dtype=str,
                usecols=["event_id", "event_date", "source", "source_url", "title", "summary", "cluster_id"]).fillna("")
s = s.drop_duplicates("event_id").set_index("event_id")

d = d.sort_values(["extracted_at", "event_date", "event_id"], ascending=False).head(600).reset_index(drop=True)
ds = d.iloc[::5]
p = p.sort_values(["extracted_at", "first_story_at", "entity_id"], ascending=False).reset_index(drop=True)
k = len(p) / 60
ps = p.iloc[[int(i * k) for i in range(60)]]

def stories(ids):
    out = []
    for sid in [x for x in ids.split(";") if x]:
        if sid in s.index:
            r = s.loc[sid]
            out.append({"story_id": sid, "date": r.event_date[:10], "outlet": r.source, "url": r.source_url,
                        "title": r.title, "summary": r.summary[:1500], "cluster_id": r.cluster_id})
        else:
            out.append({"story_id": sid, "missing": True})
    return out

DF = ["event_id", "event_date", "deal_type", "buyer", "seller", "other_parties", "asset", "technology", "state", "country",
      "mw", "mwh", "dollars", "price", "price_value", "price_unit", "term_years", "status", "announced_date", "ai_power",
      "confidence", "n_stories"]
PF = ["entity_id", "name", "operator", "developer", "site_name", "state", "county", "city", "mw", "phase",
      "project_status", "planned_year", "power_source", "utility", "confidence", "first_story_at", "n_stories"]
deals = []
for i, (_, r) in enumerate(ds.iterrows(), 1):
    deals.append({"n": f"D{i:03d}", **{c: r[c] for c in DF},
                  "evidence": e.loc[e.deal_id == r.event_id, "evidence"].tolist(),
                  "stories": stories(r.story_ids)})
facs = []
for i, (_, r) in enumerate(ps.iterrows(), 1):
    facs.append({"n": f"F{i:03d}", **{c: r[c] for c in PF},
                 "evidence": pe.loc[pe.facility_id == r.entity_id, "evidence"].tolist(),
                 "stories": stories(r.story_ids)})
json.dump({"deals": deals, "facilities": facs}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(deals), "deals,", len(facs), "facilities;", sum(1 for x in deals for st in x["stories"] if st.get("missing")), "missing stories")
