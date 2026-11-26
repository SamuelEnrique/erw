"""Session 10235, the Digest audit: every number in the story items of the ten newest Digests and the three newest
Roundups, traced to the stored story text (news_stories.csv: title and summary as the feed gave them), and failing that
to the scorer's own fields (why, mw, price_mentioned, headline: a model's words, not the story's), and failing that to
nothing. The policy actions are traced to policy_actions.csv the same way (title and abstract or summary, then why).
Also each "reported on <date>" and "(<who>; <outlet>, <date>)" date against the story's stored event_date.

No ERW code is imported. A number is read with its unit word where it has one (billion, million, MW, GW, %, ...), and
two numbers agree when their values agree at the printed precision, scaled by the unit (USD 1.2 billion = $1,200 million;
1.2 GW = 1,200 MW).

Run: python r2_stories.py <output dir> <repo root> > r2_stories.out
"""
import csv
import os
import re
import sys
from collections import defaultdict

csv.field_size_limit(10 ** 9)
OUT, ROOT = sys.argv[1], sys.argv[2]
DIGESTS = ["2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-20", "2026-10-21", "2026-10-22",
           "2026-10-23", "2026-11-06", "2026-11-12"]
ROUNDUPS = ["2026-W43", "2026-W44", "2026-W45"]


def table(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


stories = table("news_stories")
by_url = defaultdict(list)
by_cluster = defaultdict(list)
for r in stories:
    for u in (r["source_url"], r.get("google_news_url", ""), r.get("url_resolved", "")):
        if u:
            by_url[u].append(r)
    if r.get("cluster_id"):
        by_cluster[r["cluster_id"]].append(r)
policy = table("policy_actions")
pol_url = defaultdict(list)
for r in policy:
    pol_url[r["source_url"]].append(r)
POL_TEXT = [c for c in ("title", "abstract", "summary", "action", "body") if c in policy[0]]

SCALE = {"trillion": 1e6, "tn": 1e6, "billion": 1e3, "bn": 1e3, "b": 1e3, "million": 1.0, "mn": 1.0, "mm": 1.0, "m": 1.0,
         "thousand": 1e-3, "k": 1e-3}
NUMU = re.compile(r"(?<![\w.])(\$|US\$|USD ?|C\$|CAD ?|EUR ?|€|£|GBP ?|A\$|AUD ?)?(-?\d[\d,]*(?:\.\d+)?)(?![\d])\s?"
                  r"(trillion|billion|million|thousand|bn|mn|mm|tn|B|M|k|GW|MW|kW|GWh|MWh|kWh|TWh|%|percent|bcf|Bcf|mtpa|barrels|bpd|b/d)?\b", re.I)


def nums(text):
    """(printed string, value, decimals, kind, scaled value) for each number; kind money, cap, energy, pct or bare."""
    out = []
    text = re.sub(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?Z?)?", " ", text)      # dates are checked apart
    for m in NUMU.finditer(text):
        cur, n, unit = m.group(1), m.group(2), (m.group(3) or "")
        # a hyphen glued to a letter before the digits is a name (EIA-930, BWRX-300, CPAR-3)
        if m.start(2) >= 2 and text[m.start(2) - 1] == "-" and text[m.start(2) - 2].isalpha():
            continue
        if m.start(2) >= 1 and text[m.start(2) - 1].isalpha():
            continue
        try:
            v = float(n.replace(",", ""))
        except ValueError:
            continue
        d = len(n.split(".")[1]) if "." in n else 0
        u = unit.lower()
        if cur or (u in ("trillion", "billion", "million", "bn", "mn", "mm", "tn") and cur is not None):
            kind, sv = "money", v * SCALE.get(u, 1e-6) if u else v / 1e6
        elif u in ("gw",):
            kind, sv = "cap", v * 1000
        elif u in ("mw",):
            kind, sv = "cap", v
        elif u in ("kw",):
            kind, sv = "cap", v / 1000
        elif u in ("twh", "gwh", "mwh", "kwh"):
            kind, sv = "energy", v * {"twh": 1e6, "gwh": 1e3, "mwh": 1, "kwh": 1e-3}[u]
        elif u in ("%", "percent"):
            kind, sv = "pct", v
        elif u in ("trillion", "billion", "million", "thousand", "bn", "mn", "tn"):
            kind, sv = "count", v * SCALE[u]
        else:
            kind, sv = "bare", v
        out.append((m.group(0).strip(), v, d, kind, sv))
    return out


def agrees(p, pool):
    """Whether printed number p is in the pool: same kind and scaled value at p's precision, or (bare) any number's
    magnitude at p's precision, as the check reads it."""
    _, v, d, kind, sv = p
    tol = 0.5 * 10 ** (-d)
    for q in pool:
        if kind in ("money", "cap", "energy", "count") and q[3] == kind:
            # the scaled values agree at the printed precision of p in its own unit
            ratio = sv / v if v else 1
            if abs(q[4] - sv) <= tol * abs(ratio) + 1e-9:
                return True
        elif kind in ("pct",) and q[3] in ("pct", "bare") and abs(q[1] - v) <= tol + 1e-9:
            return True
        elif kind == "bare" and abs(abs(q[1]) - abs(v)) <= tol + 1e-9:
            return True
    return False


def bare_agrees(p, pool):
    """The check's own reading: the number's magnitude anywhere in the pool, its unit ignored."""
    _, v, d, _, _ = p
    return any(abs(abs(q[1]) - abs(v)) <= 0.5 * 10 ** (-d) + 1e-9 for q in pool)


LINK = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")


def items_of(md):
    """The story items: (section, text without links, urls). A numbered item takes its continuation lines."""
    out, sec, cur = [], "", None
    for l in md.split("\n"):
        if l.startswith("#"):
            sec = l.strip("# ").strip()
            if cur:
                out.append(cur)
                cur = None
            continue
        if re.match(r"^\d+\. ", l) or l.startswith("- "):
            if cur:
                out.append(cur)
            cur = [sec, l]
        elif cur and l.startswith("   ") and l.strip():
            cur.append(l.strip())
        else:
            if cur:
                out.append(cur)
                cur = None
    if cur:
        out.append(cur)
    res = []
    for it in out:
        sec, body = it[0], re.sub(r"^(?:\d+\.|-) ", "", " ".join(it[1:]))
        urls = [u for _, u in LINK.findall(body)]
        if not urls:
            continue
        text = LINK.sub(" ", body)
        res.append((sec, text, urls))
    return res


SKIP_SEC = re.compile(r"Numbers|Fun Fact|Chart of|Tables|opening number$|^The numbers$|Next week", re.I)

grand = defaultdict(int)
problems = []
for kind, names in (("digest", DIGESTS), ("roundup", ROUNDUPS)):
    for name in names:
        path = os.path.join(ROOT, "docs", "digest" if kind == "digest" else "roundup", name + ".md")
        md = open(path, encoding="utf-8").read()
        cnt = defaultdict(int)
        for sec, text, urls in items_of(md):
            if SKIP_SEC.search(sec):
                continue
            rows = [r for u in urls for r in by_url.get(u, [])]
            prow = [r for u in urls for r in pol_url.get(u, [])]
            clusters = {r["cluster_id"] for r in rows if r.get("cluster_id")}
            allrows = {r["event_id"]: r for r in rows}
            for c in clusters:
                for r in by_cluster[c]:
                    allrows[r["event_id"]] = r
            story_txt = " ".join(f"{r['title']} {r['summary']}" for r in allrows.values())
            story_txt += " " + " ".join(" ".join(r.get(c, "") for c in POL_TEXT) for r in prow)
            model_txt = " ".join(f"{r.get('why', '')} {r.get('mw', '')} MW {r.get('price_mentioned', '')} {r.get('headline', '')}" for r in allrows.values())
            model_txt += " " + " ".join(r.get("why", "") for r in prow)
            sp, mp = nums(story_txt), nums(model_txt)
            if not rows and not prow:
                cnt["items with no stored story"] += 1
                problems.append((name, sec, "NO STORY ROW", text[:160], ""))
                continue
            cnt["items"] += 1
            # dates the item gives as the story's
            for dm in re.finditer(r"(?:reported on|, )(\d{4}-\d{2}-\d{2})\b", text):
                dates = sorted({r["event_date"][:10] for r in allrows.values()})
                if dates and dm.group(1) not in dates:
                    problems.append((name, sec, "DATE", dm.group(1), f"stored event dates {dates}; {text[:120]}"))
            for p in nums(text):
                if p[1] in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) and p[3] == "bare" and re.match(rf"^\s*(?:- )?{int(p[1])}\. ", text):
                    pass
                cnt["numbers"] += 1
                if agrees(p, sp):
                    cnt["in the story text, unit and scale agreeing"] += 1
                elif bare_agrees(p, sp):
                    cnt["in the story text only as a bare number (unit or scale differs)"] += 1
                    problems.append((name, sec, "UNIT", p[0], text[:200] + " || STORY: " + story_txt[:600] + " || MODEL: " + model_txt[:300]))
                elif agrees(p, mp) or bare_agrees(p, mp):
                    cnt["only in the scorer's fields (a model's words)"] += 1
                    problems.append((name, sec, "MODEL ONLY", p[0], text[:200] + " || STORY: " + story_txt[:600] + " || MODEL: " + model_txt[:300]))
                else:
                    cnt["in no stored text"] += 1
                    problems.append((name, sec, "NOWHERE", p[0], text[:200]))
        print(f"{name}: " + "; ".join(f"{k} {v}" for k, v in cnt.items()))
        for k, v in cnt.items():
            grand[k] += v
print("\nALL: " + "; ".join(f"{k} {v}" for k, v in grand.items()))
print("\nTO READ BY HAND (issue | section | kind | number | the item):")
for p in problems:
    print(" | ".join(p))
