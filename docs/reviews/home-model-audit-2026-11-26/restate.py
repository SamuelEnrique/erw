"""Session 10236: the home page, the tour and the Thesis Builder restated from their own files, apart from the site's
code where a figure is computed (the rules are written again here from the method notes and the code's comments).

Run from the worktree root:  <venv python> runs/c10236/restate.py <main copy warehouse/output>
Reads, never writes, the main copy's tables. Writes runs/c10236/home_rows.json (the rows the drawing answers its
reads with) and prints every restated figure.
"""
import csv
import glob
import io
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.getcwd()
OUT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\lossa\Documents\erw\warehouse\output"
SITE = os.path.join(ROOT, "site")
rows_for_drawing = {}


def src(*p):
    return open(os.path.join(ROOT, *p), encoding="utf-8").read()


def table(name):
    """A warehouse CSV: its header comments and its rows (as dicts)."""
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    head = [ln for ln in lines if ln.startswith("#")]
    body = [ln for ln in lines if not ln.startswith("#")]
    return head, list(csv.DictReader(io.StringIO("\n".join(body))))


print("=" * 20, "THE TOUR")
tour = src("site", "lib", "tour.ts")
ruled = tour[tour.index("export const RULED_STOPS"):tour.index("export const NEW_STOPS")]
new = tour[tour.index("export const NEW_STOPS"):tour.index("export const STOPS")]
stop_re = re.compile(r'href: "([^"]+)", title: "([^"]+)", seconds: (\d+)(, landed: (true|false))?')
R = [(h, t, int(s), True) for h, t, s, _, _ in stop_re.findall(ruled)]
N = [(h, t, int(s), l == "true") for h, t, s, _, l in stop_re.findall(new)]
stops = R + [x for x in N if x[3]]
secs = sum(x[2] for x in stops)
print(f"ruled stops {len(R)}, new stops written {len(N)}, new landed {sum(1 for x in N if x[3])}; the path: {len(stops)} stops")
print(f"seconds {secs} = {secs / 60:.2f} minutes; rounded {round(secs / 60)} (JS Math.round of {secs / 60:.4f})")
for i, (h, t, s, _) in enumerate(stops, 1):
    print(f"  {i:2d}. {t} ({h}) {s} s")
lead = re.search(r"then the whole country: ([^\"]+)\"", src("site", "app", "tour", "page.tsx")).group(1)
print("the lead names after the seven:", lead)
named = {"its regions": "/grid", "a storm across it": "/events/elliott-2022", "demand": "/demand", "trade": "/supply", "the resource map": "/map?tab=resources"}
not_named = [t for h, t, s, l in N if l and h not in named.values()]
print(f"new stops the lead names: {len(named)}; new stops it does not name: {len(not_named)}: {not_named}")
pages = src("site", "lib", "pages.ts")
tl = re.search(r'href: "/tour", label: "The tour", line: "([^"]+)"', pages).group(1)
print("lib/pages.ts's line for /tour:", tl)
print("  'after the tour' sentence:", re.search(r"After the tour: the <Link href=\"/\">home page</Link> ([^,<]+)", src("site", "app", "tour", "page.tsx")).group(1))
home = src("site", "app", "page.tsx")
print("  the home page's sections (ToolSection titles and the strip):", re.findall(r'title="([^"]+)"', home), "| HOME_GROUPS:", re.search(r"const HOME_GROUPS = (\[[^\]]+\])", home).group(1))
print("  does app/page.tsx read lib/audience (the tools by who they are for)?", "lib/audience" in home)

print("-- the headings each stop's words quote, looked for in the site's source and the Digest's newest issue")
hd = re.findall(r'href: "([^"]+)"[^\n]*\n(?:[^\n]*\n){0,4}?\s*headings: \[([^\]]*)\]', tour)
allsrc = {}
for p in glob.glob(os.path.join(SITE, "app", "**", "*.tsx"), recursive=True) + glob.glob(os.path.join(SITE, "components", "**", "*.tsx"), recursive=True) + glob.glob(os.path.join(SITE, "lib", "**", "*.ts"), recursive=True):
    if os.sep + "tour" + os.sep in p or p.endswith("tour.ts"):
        continue
    allsrc[p] = open(p, encoding="utf-8").read()
latest = src("docs", "digest", "latest.md")
for href, hs in hd:
    for h in re.findall(r'"([^"]+)"', hs):
        hits = [os.path.relpath(p, SITE) for p, t in allsrc.items() if h in t or h.replace("'", "&apos;") in t]
        md = ("## " + h) in latest
        if not hits and not md:
            print(f"  {href}: \"{h}\" NOT in any page source and not a heading of docs/digest/latest.md")
        elif href == "/digest":
            print(f"  {href}: \"{h}\" in source: {hits[:2]}; a heading of latest.md: {md}")
print("  latest.md's headings:", re.findall(r"^## (.+)$", latest, re.M))
print("  latest.md's title:", re.search(r"^# (.+)$", latest, re.M).group(1))

print("-- the numbers the stops' words print, from their own files")
gr = src("site", "lib", "gridregions.ts")
regions = re.findall(r'\["([A-Z]+)", "[^"]+"\]', gr[gr.index("export const REGIONS"):gr.index("export type RegionCode")])
newr = re.findall(r'"([A-Z]+)"', re.search(r"NEW_REGIONS[^=]*= \[([^\]]+)\]", gr).group(1))
print(f"  /grid: regions {len(regions)} ('thirteen'); new regions {len(newr)} ('six of them new')")
ci = json.load(open(os.path.join(SITE, "data", "conditions", "index.json"), encoding="utf-8"))
print(f"  /conditions: events {len(ci['events'])} ('the nine events')")
dg = json.load(open(os.path.join(SITE, "data", "demand_growth.json"), encoding="utf-8"))
print(f"  /demand: base {dg['base']}, last whole year {dg['last_year']} ('year by year since 2019')")
print(f"  /states: first year offered {re.search(r'FROM_YEARS = \[\"(\d+)\"', src('site', 'app', 'states', 'page.tsx')).group(1)} ('since 2001')")
ai = json.load(open(os.path.join(SITE, "data", "ai_energy.json"), encoding="utf-8"))
air = ai.get("rows") or ai.get("figures") or []
print(f"  /ai-energy: rows {len(air)}; keys of the file {sorted(ai.keys())[:8]}")

print("=" * 20, "THE HOME PAGE")
cat = json.load(open(os.path.join(SITE, "data", "findings", "catalogue.json"), encoding="utf-8"))
cards = [p for p in glob.glob(os.path.join(SITE, "data", "findings", "*.json")) if not p.endswith("catalogue.json")]
print(f"Analysis: catalogue entries {len(cat)} (the home figure); their ids {[c['id'] for c in cat]}")
ids = [c["id"] for c in cat]
print(f"  card files in data/findings/ {len(cards)}; analysisflow's words: seven findings, three of them in two versions, and the impact study")

# Grid: ERCOT's newest hour of demand
h, rows = table("eia930_all_demand")
er = [r for r in rows if r["entity"] == "eia930:ERCO" and r["variable"] == "demand_mw"]
top = max(er, key=lambda r: r["ts_utc"])
v = float(top["value"])
print(f"Grid: ERCOT demand newest {top['ts_utc']} value {top['value']} -> printed {round(v):,} MW, note 'at {top['ts_utc'][11:16]} UTC on {top['ts_utc'][:10]}' ({len(er)} rows)")
rows_for_drawing["demand"] = [{k: top[k] for k in ("entity", "variable", "ts_utc", "value", "unit")}]

# the three fuels
h, rows = table("eia_fuel_spot_prices")
mk = json.load(open(os.path.join(SITE, "data", "markets.json"), encoding="utf-8"))
fu = mk["fuels"]
rows_for_drawing["fuels"] = {}
for e in fu["entities"]:
    xs = [r for r in rows if r["entity"] == e["entity"] and r["variable"] == fu["variable"]]
    t = max(xs, key=lambda r: r["ts_utc"])
    print(f"Fuel {e['label']}: newest {t['ts_utc'][:10]} {float(t['value']):,.2f} {t['unit']}")
    rows_for_drawing["fuels"][e["entity"]] = [{k: t[k] for k in ("entity", "variable", "ts_utc", "value", "unit")}]

# Infrastructure and Games: the batteries operating (nameplate MW), US and ERCOT
h, rows = table("storage_capacity")
retr = [x for x in h if x.startswith("# Retrieved")]
op = [r for r in rows if r["status"] == "operating"]
mw = lambda rs: round(sum(float(r["capacity_mw"] or 0) for r in rs) * 10) / 10
print(f"Infrastructure: operating units {len(op)}, {mw(op):,} MW (of {len(rows)} rows; {retr[0][2:] if retr else ''})")
tx = [r for r in op if r["iso"] == "ERCOT"]
print(f"Games: ERCOT operating units {len(tx)}, {mw(tx):,} MW")
es = Counter(r.get("eia_status", "") for r in op)
print(f"  the operating rows by EIA's own status code: {dict(es)}; MW not 'OP': {mw([r for r in op if r.get('eia_status') not in ('OP', '')]):,}")
print(f"  ERCOT's operating rows not 'OP': {sum(1 for r in tx if r.get('eia_status') not in ('OP', ''))} units, {mw([r for r in tx if r.get('eia_status') not in ('OP', '')]):,} MW")
rows_for_drawing["storage"] = [{"entity_id": r["entity_id"], "capacity_mw": float(r["capacity_mw"]) if r["capacity_mw"] else None, "status": r["status"], "state": r["state"], "iso": r["iso"],
                                "planned_year": r["planned_year"], "mwh": r["energy_capacity_mwh"], "vintage": r["vintage"]} for r in rows]

# Economics: the default battery's last twelve months per kW, from the method (docs/methods/battery_stack.md):
# a month counts when its revenue is held and at least 90 percent of its days are solved; the window ends with the newest
# month whose every day is in the table (solved or left out) and whose eleven months before it all count
h, rows = table("battery_stack_monthly")
pre = "foresight_4h_"
by = defaultdict(dict)
keep = []
for r in rows:
    if r["entity"] == "ercot:HB_HUBAVG" and r["variable"].startswith(pre):
        by[r["ts_utc"][:7]][r["variable"][len(pre):]] = float(r["value"])
        keep.append({k: r[k] for k in ("variable", "ts_utc", "value")})
rows_for_drawing["stack"] = keep
months = []
for m in sorted(by):
    v = by[m]
    dh, dm, lo = v.get("days_held", 0), v.get("days_in_month", 0), v.get("days_left_out", 0)
    has = "revenue_total_usd_per_mw" in v
    months.append({"m": m, "held": has and dm > 0 and dh / dm >= 0.9 - 1e-9, "whole": dm > 0 and dh + lo >= dm, "total": v.get("revenue_total_usd_per_mw")})
last_whole = max((x["m"] for x in months if x["whole"]), default="")
for x in months:
    if x["held"] and not x["whole"] and x["m"] > last_whole:
        x["held"] = False
bym = {x["m"]: x for x in months}


def back(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    y += mo // 12
    return f"{y:04d}-{mo % 12 + 1:02d}"


win = None
for x in reversed(months):
    if x["held"] and x["whole"]:
        tw = [bym.get(back(x["m"], k)) for k in range(12)]
        if all(t and t["held"] for t in tw):
            win = list(reversed(tw))
            break
if win:
    tot = sum(t["total"] for t in win) / 1000
    print(f"Economics: window {win[0]['m']} to {win[-1]['m']}, USD {tot:.2f} per kW (the strategy is perfect foresight, 'foresight'; {len(keep)} rows)")
else:
    print("Economics: no window")

print("-- today's chart and the Digest")
charts = sorted(p for p in glob.glob(os.path.join(ROOT, "docs", "digest", "charts", "*.json")) if re.search(r"\d{4}-\d{2}-\d{2}\.json$", p))
c = json.load(open(charts[-1], encoding="utf-8"))
print(f"  newest chart record {os.path.basename(charts[-1])}: date {c['date']}, table {c['table']}, source {c.get('source')}")
print(f"  fact: {c['fact']}")
print(f"  'Drawn by code from the scanner's strongest flag of the day' against its record's why: {c.get('why', '')[:160]}")
print(f"  latest.md has '## Top of the industry': {'## Top of the industry' in latest}")
title = re.search(r"^# (.+)$", latest, re.M).group(1)
print(f"  the home's title cleaner (removes \"ERW's Energy Digest, \" or \"Energy Digest, \") leaves: {re.sub(r'^(?:ERW.s )?Energy Digest,\s*', '', title)!r}")
opening = next((s.strip() for s in latest.split("\n") if s.strip() and not s.strip().startswith("#")), "")
print(f"  the opening line printed: {opening!r}")
wm = latest[latest.index("## What moved"):latest.index("## More")]
print(f"  the newest issue's 'What moved': {len(re.findall(r'^(?:\d+\.|-)\s', wm, re.M))} list items; 'More': {len(re.findall(r'^(?:\d+\.|-)\s', latest[latest.index('## More'):latest.index('## ERW' + chr(39) + 's Chart')], re.M))} list items")
issues = sorted(os.path.basename(p)[:10] for p in glob.glob(os.path.join(ROOT, "docs", "digest", "2026-*.md")))
print(f"  newest issues: {issues[-4:]}; days from the newest to 2026-11-26: 14")
old = src("docs", "digest", "2026-11-06.md")
sect = old[old.index("## Top of the industry"):old.index("## By sector")]
items = re.findall(r"^\d+\.\s(.+)$", sect, re.M)[:5]
nums = [re.findall(r"\$?\d[\d,.]*\s?(?:billion|million|GW|MW|percent|%)?", i) for i in items]
print(f"  in the last issue of the old form (2026-11-06), the first five stories carry {sum(len(n) for n in nums)} numbers, e.g. {[n for n in nums if n][:2]}")
json.dump(rows_for_drawing, open(os.path.join(ROOT, "runs", "c10236", "home_rows.json"), "w", encoding="utf-8"))
print("home_rows.json written")
