"""Window D's data request 52: site/data/companies/ rebuilt from the tables of 26 November against the files of 16 November
(runs/c701/companies_old/). Reports: companies listed and held-only, held links by table, the top 10 by footprint, the
double count the audit names (the index's own fields), and how many companies' operating, planned or queue MW move by 1 MW
or more. Counts only."""
import json

new = json.load(open("site/data/companies/index.json", encoding="utf-8"))
old = json.load(open("runs/c701/companies_old/index.json", encoding="utf-8"))
cols = new["columns"]
print("columns:", cols)
print("built", old["built"], "->", new["built"])
print("listed", old["n_listed"], "->", new["n_listed"], "| directory", old["n_directory"], "->", new["n_directory"],
      "| held only", old["held_only"], "->", new["held_only"])
print("held links by table:", {k: (old["held_links"].get(k), v) for k, v in new["held_links"].items()})
ix = {c: i for i, c in enumerate(cols)}
mw_cols = [c for c in cols if "mw" in c.lower()]
print("MW columns:", mw_cols)
fp = next((c for c in cols if "footprint" in c.lower()), None) or (mw_cols[-1] if mw_cols else None)
rows = sorted(new["rows"], key=lambda r: -(r[ix[fp]] or 0))
print(f"top 10 by {fp}:")
for r in rows[:10]:
    print("  ", r[ix["id"]], r[ix["name"]] if "name" in ix else r[1], r[ix[fp]])
o = {r[ix["id"]]: r for r in old["rows"]}
moved = {c: 0 for c in mw_cols}
anym = 0
for r in new["rows"]:
    p = o.get(r[ix["id"]])
    if p is None:
        continue
    hit = False
    for c in mw_cols:
        if abs((r[ix[c]] or 0) - (p[ix[c]] or 0)) >= 1:
            moved[c] += 1
            hit = True
    anym += hit
print("companies whose MW moved by 1 MW or more, by column:", moved, "| any:", anym, "| new ids:", len(set(r[ix["id"]] for r in new["rows"]) - set(o)),
      "| ids gone:", len(set(o) - set(r[ix["id"]] for r in new["rows"])))
dc = {k: new[k] for k in new if "double" in k.lower() or "overlap" in k.lower()}
print("double count fields in the index:", dc or "none named so")
