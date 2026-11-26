"""Audit of Automated Analysis (session 10204): the forty's claim and five tests re-done by hand from each draft's CSV.

An independent restatement (no import of hunt.py): full years, the first and last full year, the change, the five
tests, the strength (change over 1.4826 times the median absolute change between full years), and the p-value of a
straight line by ordinary least squares (written out, Student's t from math only through a series). Each set beside
the draft's own words in its .md (the strength, the typical move, the counts of test 1, the floor of test 3).

Run: python runs/a2_forty_tests.py <repo root>   (prints one CSV row a draft; exit 1 when a figure differs)
"""
import csv
import math
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEET = os.path.join(ROOT, "docs", "reviews", "findings-shortlist-2026-11-19.md")
THIS_YEAR = 2026


def drafts():
    text = open(SHEET, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^### (\d+)\. .*?docs/findings/([^ ]+?)\.reproduce\.do", text, re.M | re.S):
        out.append((int(m.group(1)), m.group(2)))
    return out


def read_csv(path):
    rows = [ln for ln in open(path, encoding="utf-8") if not ln.startswith("#")]
    return list(csv.DictReader(rows))


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def sgn(x):
    return (x > 0) - (x < 0)


def betainc_t_p(t, df):
    """Two-sided p of Student's t by numerical integration of the density (Simpson, fine grid)."""
    if df <= 0:
        return float("nan")
    t = abs(t)
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    f = lambda x: c * (1 + x * x / df) ** (-(df + 1) / 2)
    # p = 2 * (0.5 - integral 0..t)
    n = 20000
    h = t / n
    s = f(0) + f(t) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, n))
    return max(0.0, 2 * (0.5 - s * h / 3))


def ols_p(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    sse = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys))
    if n < 3:
        return None
    se = math.sqrt(sse / (n - 2) / sxx) if sse > 0 else 0.0
    return 0.0 if se == 0 else betainc_t_p(b / se, n - 2)


def claim(rows):
    ser = {}
    for r in rows:
        try:
            y, v, n = int(float(r["year"])), float(r["value"]), float(r["n_observations"])
        except (ValueError, KeyError, TypeError):
            continue
        if math.isnan(v) or math.isnan(n):
            continue
        ser.setdefault(y, (v, n))
    if not ser:
        return None
    most = max(n for _, n in ser.values())
    full = [y for y in sorted(ser) if y < THIS_YEAR and ser[y][1] >= 0.9 * most]
    if len(full) < 2:
        return None
    y0, y1 = full[0], full[-1]
    v0, v1 = ser[y0][0], ser[y1][0]
    ch = v1 - v0
    s = sgn(ch)
    held = sum(1 for y in full[1:] if sgn(ser[y][0] - v0) == s)
    t2 = len(full) >= 4 and sgn(v1 - ser[full[1]][0]) == s and sgn(ser[full[-2]][0] - v0) == s
    vals = [ser[y][0] for y in full]
    typ = 1.4826 * median([abs(b - a) for a, b in zip(vals, vals[1:])])
    strength = abs(ch) / typ if typ > 0 else 0.0
    remains = (v1 - ser[full[1]][0]) / ch if len(full) >= 3 else None
    return {"first_year": y0, "last_year": y1, "first": v0, "last": v1, "change": ch, "full": len(full), "held": held,
            "t2": t2, "n0": ser[y0][1], "n1": ser[y1][1], "typ": typ, "strength": strength, "remains": remains,
            "p_trend": ols_p([float(y) for y in full], vals), "full_years": full,
            "flag_years": sorted(int(float(r["year"])) for r in rows if str(r.get("full_year")) == "1")}


def md_numbers(md):
    g = lambda p: (re.search(p, md) or [None, None])[1]
    return {"strength": g(r"The change is ([\d.,]+) typical yearly moves"),
            "held": g(r"Holds in more than one year: (\d+) of"),
            "floor": g(r"the floor is ([\d,]+)\. Half"),
            "n0": g(r"Sample large enough: \d{4} holds ([\d,]+) and")}


def main():
    bad = 0
    print("no,slug,full_years,first_year,last_year,first,last,strength_here,strength_draft,held_here,held_draft,n_first,floor,"
          "remains,p_trend_ols,flags_match,passes_five_here")
    for no, slug in drafts():
        base = os.path.join(ROOT, "docs", "findings", slug)
        if not os.path.exists(base + ".csv"):
            print(f"{no},{slug},no csv")
            continue
        c = claim(read_csv(base + ".csv"))
        md = open(base + ".md", encoding="utf-8").read()
        m = md_numbers(md)
        if c is None:
            print(f"{no},{slug},no claim (an event or a summary, not a yearly claim)")
            continue
        sd = float(m["strength"].replace(",", "")) if m["strength"] else None
        ok_s = sd is None or abs(round(c["strength"], 2) - sd) < 0.006
        ok_h = m["held"] is None or int(m["held"]) == c["held"]
        flags = c["flag_years"] == c["full_years"]
        floor = float(m["floor"].replace(",", "")) if m["floor"] else None
        five = (c["held"] >= 2 and c["t2"] and (floor is None or min(c["n0"], c["n1"]) >= floor)
                and c["remains"] is not None and c["remains"] >= 0.5 and c["strength"] >= 1.0)
        if not (ok_s and ok_h and flags):
            bad += 1
        print(f"{no},{slug},{c['full']},{c['first_year']},{c['last_year']},{c['first']:.6g},{c['last']:.6g},{c['strength']:.4f},"
              f"{sd},{c['held']},{m['held']},{c['n0']:g},{floor},{c['remains'] if c['remains'] is None else round(c['remains'], 4)},"
              f"{c['p_trend'] if c['p_trend'] is None else round(c['p_trend'], 6)},{flags},{five}")
    print(f"differing: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
