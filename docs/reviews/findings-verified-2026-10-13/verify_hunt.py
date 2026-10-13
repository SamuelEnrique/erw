"""Session 252: verify the weekly hunt's drafts (rule "hunt") as they stand in public.scanner_drafts.

For each draft kept by fetch_drafts.py under runs/session252/drafts/<id>/:
  1. its own Python mirror is run on its own CSV (a subprocess), and what it prints is kept;
  2. the claim and the three tests are recomputed from the CSV by hunt.test_claim and compared, key by key and
     exactly, with what the draft stores (flag.claim, flag.tests, card.numbers), and the fact line and the caption
     are written again from those numbers and compared with the stored text, character by character;
  3. the CSV itself is rebuilt from today's warehouse tables by the finding's own compute and compared year by year;
  4. further tests the hunt does not run: the year-over-year steps, the rank correlation with the year, two-year
     ends, the claim without its first year, the year under way, and how much of the claim one year carries.
No row of the review list is written. Output: runs/session252/verify_hunt.json and one block a draft on the screen.
"""
import csv
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
import findings_common as common  # noqa: E402
import hunt  # noqa: E402
import run_finding  # noqa: E402

DRAFTS = os.path.join(ROOT, "runs", "session252", "drafts")
THIS_YEAR = 2026
PAT = {P["name"]: P for P in hunt.PATTERNS}
_cache = {}


def read_csv(path):
    rows = list(csv.DictReader(ln for ln in open(path, encoding="utf-8") if not ln.startswith("#")))
    return {r["year"]: (float(r["value"]), float(r["n_observations"])) for r in rows}, [r["year"] for r in rows if r["full_year"] == "1"]


def rebuild(P, region):
    """The region's series by year from today's tables, by the finding's own compute."""
    mod = run_finding.load(P["module"])
    params = run_finding.coerce(mod, {P["sweep"]: region} if P.get("sweep") else {})
    k = (P["module"], json.dumps(params, sort_keys=True, default=str))
    if k not in _cache:
        _cache[k] = mod.compute(params, common.DEFAULT_IN_DIR)
    rows, _ = _cache[k]
    return hunt.yearly(rows, P, region)


def ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def more_tests(series, full, c):
    s = 1 if c["change"] > 0 else -1
    vals = [series[y][0] for y in full]
    steps = [b - a for a, b in zip(vals, vals[1:])]
    out = {"steps_on_side": sum(1 for d in steps if d * s > 0), "steps": len(steps),
           "spearman_year": round(spearman([int(y) for y in full], vals), 4),
           "two_year_ends": (sum(vals[-2:]) / 2 - sum(vals[:2]) / 2) if len(vals) >= 4 else None}
    out["two_year_ends_same_side"] = None if out["two_year_ends"] is None else (out["two_year_ends"] * s > 0)
    # without the first year: the claim asked again from the second full year
    out["change_without_first_year"] = vals[-1] - vals[1] if len(vals) >= 3 else None
    out["share_of_claim_without_first_year"] = (out["change_without_first_year"] / c["change"]) if len(vals) >= 3 else None
    out["change_without_last_year"] = vals[-2] - vals[0] if len(vals) >= 3 else None
    out["share_of_claim_without_last_year"] = (out["change_without_last_year"] / c["change"]) if len(vals) >= 3 else None
    # is the last year the extreme of every full year on the claim's side, and the first year the other extreme
    out["last_is_extreme"] = vals[-1] == (max(vals) if s > 0 else min(vals))
    out["first_is_other_extreme"] = vals[0] == (min(vals) if s > 0 else max(vals))
    # the middle of the series: the median of the full years between the ends against the first year
    mid = sorted(vals[1:-1])
    out["median_between"] = (mid[len(mid) // 2] if len(mid) % 2 else (mid[len(mid) // 2 - 1] + mid[len(mid) // 2]) / 2) if mid else None
    under_way = [y for y in series if y not in full and int(y) == THIS_YEAR]
    if under_way:
        v, n = series[under_way[0]]
        out["year_under_way"] = {"year": under_way[0], "value": v, "n": n, "on_side_of_first": (v - vals[0]) * s > 0, "beyond_last": (v - vals[-1]) * s > 0}
    return out


def main():
    index = json.load(open(os.path.join(DRAFTS, "index.json"), encoding="utf-8"))
    results = []
    for x in index:
        if x["rule"] != "hunt":
            continue
        did = x["id"]
        d = os.path.join(DRAFTS, did)
        row = json.load(open(os.path.join(d, "row.json"), encoding="utf-8"))
        flag, card = row["flag"], row["card"]
        P = PAT[flag["pattern"]]
        region = flag["region"]
        res = {"id": did, "state": row["state"], "pattern": P["name"], "region": region, "words": card["hunt"]["region_words"], "strength": row["strength"],
               "fact": card["subtitle"], "module": P["module"], "tables": card["tables"], "problems": []}
        # 1. the draft's own mirror on its own CSV
        r = subprocess.run([sys.executable, f"{did}.py", f"{did}.csv"], cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        res["mirror_exit"], res["mirror_out"] = r.returncode, r.stdout.strip().splitlines()
        if r.returncode != 0:
            res["problems"].append(f"the mirror exited {r.returncode}: {r.stderr.strip()[:200]}")
        # 2. the claim from the CSV against what the draft stores
        series, full_csv = read_csv(os.path.join(d, f"{did}.csv"))
        c = hunt.test_claim(series, P, THIS_YEAR)
        if c is None:
            res["problems"].append("no claim can be computed from the CSV")
            results.append(res)
            continue
        if c["years"] != full_csv:
            res["problems"].append(f"the CSV marks {full_csv} as full; the rule gives {c['years']}")
        compared = 0
        for k, v in flag["claim"].items():
            compared += 1
            if c[k] != v:
                res["problems"].append(f"flag.claim.{k}: stored {v!r}, recomputed {c[k]!r}")
        for k, v in card["numbers"].items():
            mine = {"first_year": int(c["first_year"]), "last_year": int(c["last_year"]), "full_years": len(c["years"])}.get(k, c.get(k))
            compared += 1
            if mine != v:
                res["problems"].append(f"card.numbers.{k}: stored {v!r}, recomputed {mine!r}")
        for a, b in zip(flag["tests"], c["tests"]):
            compared += 2
            if a != b:
                res["problems"].append(f"test '{a['name']}': stored {a!r}, recomputed {b!r}")
        # The row's own value column is a database column beside the card: it is read back at 15 significant digits,
        # where the card and the flag (JSON) hold the number in full. Compared at the column's own precision, and said.
        res["row_value_column"] = {"stored": row["value"], "recomputed": c["change"], "equal_in_full": row["value"] == c["change"],
                                   "equal_at_15_digits": float(f"{row['value']:.15g}") == float(f"{c['change']:.15g}")}
        if not res["row_value_column"]["equal_at_15_digits"] or row["strength"] != c["strength"]:
            res["problems"].append(f"the row's value or strength: stored {row['value']!r}, {row['strength']!r}; recomputed {c['change']!r}, {c['strength']!r}")
        compared += 2
        # the mirror's own printed numbers
        m = re.match(r"claim: (\S+) in (\d{4}), (\S+) in (\d{4}); change (\S+)", res["mirror_out"][0]) if res["mirror_out"] else None
        if not m or (float(m.group(1)), m.group(2), float(m.group(3)), m.group(4), float(m.group(5))) != (c["first"], c["first_year"], c["last"], c["last_year"], c["change"]):
            res["problems"].append(f"the mirror's claim line does not equal the stored claim: {res['mirror_out'][:1]}")
        verdicts = [ln.rsplit(": ", 1)[-1] for ln in res["mirror_out"][1:4]]
        if verdicts != ["pass" if t["passed"] else "fail" for t in flag["tests"]]:
            res["problems"].append(f"the mirror's three verdicts {verdicts} differ from the stored tests")
        compared += 8
        # the words: the fact line and the caption written again from the numbers
        words = card["hunt"]["region_words"]
        if hunt.fact_of(P, words, c) != card["subtitle"]:
            res["problems"].append("the fact line written again from the numbers differs from the stored one")
        src = card["source_line"].replace(" Found by the weekly hunt.", "")
        if hunt.caption_of(P, words, c, src) != card["hunt"]["caption"]:
            res["problems"].append("the caption written again from the numbers differs from the stored one")
        if open(os.path.join(d, f"{did}_caption.txt"), encoding="utf-8").read().rstrip("\n") != card["hunt"]["caption"]:
            res["problems"].append("the caption file differs from the card's caption")
        compared += 3
        res["numbers_compared"] = compared
        res["claim"] = {k: c[k] for k in ("first_year", "last_year", "first", "last", "change", "direction", "years_held", "years_after", "typical_move", "strength", "n_first", "n_last", "passed")}
        res["tests"] = c["tests"]
        res["unit"], res["decimals"], res["label"] = P["unit"], P["decimals"], P["label"]
        res["series"] = {y: list(v) for y, v in series.items()}
        res["reproduced_from_own_csv"] = not res["problems"]
        # 3. the CSV from today's tables
        today = rebuild(P, region)
        diffs = []
        for y in sorted(set(series) | set(today)):
            a, b = series.get(y), today.get(y)
            if a is None or b is None or a[0] != b[0] or a[1] != b[1]:
                diffs.append({"year": y, "csv": a, "today": b, "full": y in c["years"]})
        res["today_diffs"] = diffs
        res["reproduced_from_tables_full_years"] = not any(d_["full"] for d_ in diffs)
        ct = hunt.test_claim(today, P, THIS_YEAR)
        res["today_claim"] = None if ct is None else {k: ct[k] for k in ("first_year", "last_year", "first", "last", "change", "passed", "strength")}
        # 4. further tests
        res["more"] = more_tests(series, c["years"], c)
        results.append(res)
        print(f"{did}  {P['name']} {region}: own CSV {'EXACT' if res['reproduced_from_own_csv'] else 'DIFFERS'} ({compared} values compared); "
              f"today's tables, full years {'EXACT' if res['reproduced_from_tables_full_years'] else 'DIFFER'} ({len(diffs)} year(s) differ in all); "
              f"tests {sum(1 for t in c['tests'] if t['passed'])} of 3; strength {c['strength']}")
        for p in res["problems"]:
            print(f"    PROBLEM: {p}")
        for d_ in diffs:
            print(f"    differs today, {d_['year']} ({'full' if d_['full'] else 'not full'}): csv {d_['csv']}, today {d_['today']}")
        print(f"    more: {json.dumps(res['more'], default=str)}")
    with open(os.path.join(ROOT, "runs", "session252", "verify_hunt.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=1, ensure_ascii=False, default=str)
        f.write("\n")
    bad = [r for r in results if r["problems"]]
    print(f"{len(results)} hunt drafts; {len(results) - len(bad)} reproduce exactly from their own CSV; {sum(1 for r in results if r.get('reproduced_from_tables_full_years'))} rebuild exactly from today's tables (full years)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
