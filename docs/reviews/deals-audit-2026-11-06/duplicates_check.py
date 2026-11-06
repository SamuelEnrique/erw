"""Session 2231: duplicates in the stored tables. Deals: pairs deal_parties.same_deal finds (strict) and pairs that share
two party names, either order, within 30 days whatever the type (loose); the register's pairs. Facilities: pairs with
the same operator (or developer) and the same city or county in the same state."""
import itertools, sys
import pandas as pd
sys.path.insert(0, "warehouse/deals")
import deal_parties as dp

d = pd.read_csv("warehouse/output/energy_deals.csv", comment="#", dtype=str).fillna("")
reg = pd.read_csv("warehouse/deals/duplicates.csv", dtype=str).fillna("")
folded = set(reg.duplicate_event_id)
rows = d.to_dict("records")
strict, loose = [], []
for a, b in itertools.combinations(rows, 2):
    if a["event_id"] in folded or b["event_id"] in folded:
        continue
    if dp.same_deal(a, b):
        strict.append((a, b)); continue
    pa = [x for x in (a["buyer"], a["seller"]) if x]
    pb = [x for x in (b["buyer"], b["seller"]) if x]
    if len(pa) == 2 and len(pb) == 2:
        if ((dp.same_party(pa[0], pb[0]) and dp.same_party(pa[1], pb[1])) or
                (dp.same_party(pa[0], pb[1]) and dp.same_party(pa[1], pb[0]))):
            da, db = pd.Timestamp(a["event_date"][:10]), pd.Timestamp(b["event_date"][:10])
            if abs((da - db).days) <= 30:
                loose.append((a, b))
# same story feeding two deals with the same buyer
shared = []
for a, b in itertools.combinations(rows, 2):
    sa, sb = set(a["story_ids"].split(";")), set(b["story_ids"].split(";"))
    if sa & sb and a["deal_type"] == b["deal_type"] and dp.same_party(a["buyer"] or "-", b["buyer"] or "+"):
        shared.append((a, b))
def show(t, pairs):
    print(f"\n{t}: {len(pairs)}")
    for a, b in pairs[:40]:
        print(f"  {a['event_id']} {a['event_date'][:10]} {a['deal_type']} {a['buyer']} / {a['seller']} | {a['asset'][:40]} | {a['dollars']} {a['mw']}")
        print(f"  {b['event_id']} {b['event_date'][:10]} {b['deal_type']} {b['buyer']} / {b['seller']} | {b['asset'][:40]} | {b['dollars']} {b['mw']}")
show("strict same_deal pairs (not in the register)", strict)
show("same two parties within 30 days, any type", loose)
show("same story, type and buyer", shared)
print("\nregister:", reg.ruling.value_counts().to_dict())

p = pd.read_csv("warehouse/output/datacenter_projects.csv", comment="#", dtype=str).fillna("")
fp = []
for a, b in itertools.combinations(p.to_dict("records"), 2):
    oa, ob = a["operator"] or a["developer"], b["operator"] or b["developer"]
    if not oa or not ob or not dp.same_party(oa, ob):
        continue
    if a["state"] and a["state"] == b["state"] and ((a["city"] and a["city"] == b["city"]) or (a["county"] and a["county"] == b["county"])):
        fp.append((a, b))
    elif a["site_name"] and dp.same_party(a["site_name"], b["site_name"] or "+"):
        fp.append((a, b))
print(f"\nfacility pairs, same operator and same place or site: {len(fp)}")
for a, b in fp:
    print(f"  {a['entity_id']} {a['first_story_at'][:10]} {a['operator'] or a['developer']} | {a['site_name']} | {a['city']} {a['county']} {a['state']} | {a['mw']}")
    print(f"  {b['entity_id']} {b['first_story_at'][:10]} {b['operator'] or b['developer']} | {b['site_name']} | {b['city']} {b['county']} {b['state']} | {b['mw']}")
