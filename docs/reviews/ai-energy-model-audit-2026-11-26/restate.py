"""Session 10221: every figure and line /ai-energy's default view prints, restated from the page's own file
(site/data/ai_energy.json) by the rules of docs/methods/ai_energy_published.md ("The page") and the page's own words,
written without reading site/lib/aienergy.ts's functions, and set beside the page as the site's own code draws it
(draw_ai.mjs: <prefix>_default.html and <prefix>_views.json).

    python restate.py <worktree root> <draw prefix> <out json>

Exit 0 when every restated item equals the drawn one, 1 when one does not. Standard library only.
"""
import html as H
import json
import os
import re
import sys
from datetime import date

root, prefix, out = sys.argv[1], sys.argv[2], sys.argv[3]
F = json.load(open(os.path.join(root, "site", "data", "ai_energy.json"), encoding="utf-8"))
rows = F["rows"]
page = open(prefix + "_default.html", encoding="utf-8").read()
views = json.load(open(prefix + "_views.json", encoding="utf-8"))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def words_date(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return f"{MONTHS[m - 1]} {dd}, {y}"


def grouped(v):
    """The number as written in the shortest decimal that reads back as the same float (what a reader sees), grouped by
    thousands. Restated: Python's repr and JavaScript's String give the same shortest digits for these values."""
    if v is None:
        return ""
    s = repr(float(v))
    if "e" in s:
        raise ValueError(f"{v}: exponent form")
    i, _, d = s.partition(".")
    d = "" if d == "0" else d
    return f"{int(i):,}" + (f".{d}" if d else "")


checks, bad = [], 0


def check(name, mine, drawn):
    global bad
    ok = mine == drawn
    bad += 0 if ok else 1
    checks.append({"item": name, "restated": mine, "drawn": drawn, "equal": ok})


def fig(key):
    m = re.search(rf'data-fig="{re.escape(key)}"[^>]*>(.*?)</span>', page, re.S)
    return H.unescape(re.sub(r"<[^>]*>", "", m.group(1))) if m else None


# 1. the headline: figures, publications (distinct titles), peer-reviewed papers (publisher kind), the newest
titles = {r["x_title"] for r in rows}
peer = {r["x_title"] for r in rows if r["x_publisher_kind"] == "peer-reviewed paper"}
newest = sorted(rows, key=lambda r: r["event_date"], reverse=True)[0]
check("Figures", str(len(rows)), fig("h-figures"))
check("Publications", str(len(titles)), fig("h-publications"))
check("peer-reviewed note", f"{len(peer)} of them peer-reviewed papers", "2 of them peer-reviewed papers" if "2 of them peer-reviewed papers" in page else None)
check("Newest", words_date(newest["event_date"]), fig("h-newest"))
check("Newest note", f"{newest['parties']}: {newest['x_title']}", H.unescape(re.search(r'Newest.*?</span>.*?>([^<]*: [^<]*)<', page, re.S).group(1)) if "Newest" in page else None)
check("File built", F["built"][:10], re.search(r"File built (\d{4}-\d\d-\d\d)", page).group(1))

# 2. each figure: the number in its own unit, as the page's data-fig shows it
for r in rows:
    check(f"figure {r['event_id']}", f"{grouped(r['x_value'])} {r['x_unit']}", fig(f"v-{r['event_id']}"))

# 3. the default order: publisher A to Z, then date, ties in the file's order (the note; Decisions "order")
idx = {r["event_id"]: i for i, r in enumerate(rows)}
default = [r["event_id"] for r in sorted(rows, key=lambda r: (r["parties"], r["event_date"], idx[r["event_id"]]))]
check("default order", default, views["default"])
check("order publisher", default, views["sort=publisher"])
check("order measures", [r["event_id"] for r in sorted(rows, key=lambda r: (r["x_measures"], r["parties"], idx[r["event_id"]]))], views["sort=measures"])
check("order newest", [r["event_id"] for r in sorted(rows, key=lambda r: (-date.fromisoformat(r["event_date"]).toordinal(), idx[r["event_id"]]))], views["sort=newest"])
check("order oldest", [r["event_id"] for r in sorted(rows, key=lambda r: (r["event_date"], idx[r["event_id"]]))], views["sort=oldest"])

# 4. the measures the form offers, each once, A to Z, and each filter's rows (in the default order)
ms = sorted({r["x_measures"] for r in rows})
drawn_ms = [H.unescape(m) for m in re.findall(r'<option value="([^"]*)"', page)]
drawn_ms = [m for m in drawn_ms if m not in ("publisher", "measures", "newest", "oldest", "all")]
check("measures offered", ms, drawn_ms)
for m in ms:
    check(f"filter {m}", [i for i in default if next(r for r in rows if r["event_id"] == i)["x_measures"] == m], views.get(f"m={m}"))

# 5. the publishers' list: figures, publications, years
pub_lines = []
for p in sorted({r["parties"] for r in rows}):
    mine = [r for r in rows if r["parties"] == p]
    n_t = len({r["x_title"] for r in mine})
    years = []
    for r in mine:
        if r["event_date"][:4] not in years:
            years.append(r["event_date"][:4])
    pub_lines.append(f"{p}: {len(mine)} figure{'' if len(mine) == 1 else 's'} in {n_t} publication{'' if n_t == 1 else 's'} ({', '.join(years)})")
drawn_pub = [H.unescape(x) for x in re.findall(r"<li>([^<]*)</li>", page.split('data-ai-publishers="')[1].split("</ul>")[0])]
check("publishers list", pub_lines, drawn_pub)

# 6. each row's cells and hovers, in the default order
by = {r["event_id"]: r for r in rows}
trs = page.split("<tbody")[1].split("</tbody>")[0].split("<tr")[1:]
for tr, eid in zip(trs, views["default"]):
    r = by[eid]
    titles_ = [H.unescape(t) for t in re.findall(r'title="([^"]*)"', tr)]
    want = [f"Period: {r['x_period']}. Peer-reviewed: {r['x_peer_reviewed']}.",
            f"Basis: {r['x_basis']}. Source: {r['x_title']} ({r['source_url']}), page {r['x_page']}, as saved on {r['x_retrieved_at'][:10]} (sha256 {r['x_sha256'][:12]}).",
            f"Page {r['x_page']} of the publication, as saved; the ERW cut these words from its saved copy."]
    check(f"hovers {eid}", want, titles_)
    text = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", tr))).strip()
    cells = [r["parties"], r["x_publisher_kind"], r["x_title"], words_date(r["event_date"]) + (f"; {r['x_authors']}" if r["x_authors"] else ""),
             r["x_measures"], r["x_subject"], f"{grouped(r['x_value'])} {r['x_unit']}", "“" + r["x_printed"] + "”", f"(p. {r['x_page']})"]
    check(f"cells {eid}", True, all(c in text for c in cells))

# 7. the decisions fold: five, with their keys
check("decisions", ["as-printed", "no-sum", "order", "no-pair", "which-publications"], re.findall(r'data-decision="([^"]+)"', page))

res = {"page_file_built": F["built"], "rows": len(rows), "checks": len(checks), "unequal": bad, "items": checks}
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(checks)} items restated; {len(checks) - bad} equal; {bad} unequal")
for c in checks:
    if not c["equal"]:
        print("UNEQUAL", c["item"], "| restated:", c["restated"], "| drawn:", c["drawn"])
sys.exit(1 if bad else 0)
