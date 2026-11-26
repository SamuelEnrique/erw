"""Announced datacenters: the evidence rows and the defaults they give /impact (chain 740, part B).

Reads warehouse/forecast/datacenter_announced_rows.json (transcribed by hand from public documents, each figure with
the document's words) and writes site/data/forecast/datacenter_announced.json: the rows, and for each ratio the tool
offers as a default its count, lowest, median and highest, with the rows that give the ends.

Checks, before anything is written (the script stops on the first failure):
  - each figure's `says` is inside its `quote`, and `says` parses to `value` (billion, million, gigawatts, megawatts);
  - with --verify-reads, each quote is inside the text kept of its request (runs/c740/reads/NNN_*.txt, lab-desktop),
    after curly quotes and spaces are made plain.

Dollars: each investment is put in 2025 dollars by the tool's deflator (site/data/forecast/deflator.json); a year the
index does not hold (2026) is taken as 2025 dollars, as the cross-check takes an unstated dollar year.

Usage: python warehouse/forecast/datacenter_announced.py [--verify-reads] [--check]   (--check writes nothing)
"""
import glob, json, os, re, statistics, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROWS = os.path.join(ROOT, "warehouse", "forecast", "datacenter_announced_rows.json")
OUT = os.path.join(ROOT, "site", "data", "forecast", "datacenter_announced.json")
DEFLATOR = os.path.join(ROOT, "site", "data", "forecast", "deflator.json")
READS = os.path.join(ROOT, "runs", "c740", "reads")

UNITS = {"billion": 1e9, "million": 1e6, "gigawatts": 1000.0, "gigawatt": 1000.0, "gw": 1000.0,
         "megawatts": 1.0, "megawatt": 1.0, "mw": 1.0}


def plain(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def parse_says(says):
    """The number a phrase states: '$10 billion' 1e10, '5 gigawatts' 5000 (MW), '7,500 construction jobs' 7500."""
    m = re.search(r"\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*([A-Za-z]+)?", says)
    if not m:
        raise ValueError(f"no number in {says!r}")
    n = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    return n * UNITS.get(unit, 1.0)


def check_figure(row_id, key, fig, reads_text):
    if fig is None:
        return
    for k in ("value", "says", "quote"):
        if k not in fig:
            raise SystemExit(f"{row_id}.{key}: no {k}")
    if plain(fig["says"]) not in plain(fig["quote"]):
        raise SystemExit(f"{row_id}.{key}: says {fig['says']!r} is not inside its quote")
    got = parse_says(fig["says"])
    if abs(got - fig["value"]) > 1e-9 * max(1.0, abs(got)):
        raise SystemExit(f"{row_id}.{key}: says {fig['says']!r} parses to {got}, value is {fig['value']}")
    if reads_text is not None and plain(fig["quote"]) not in reads_text:
        raise SystemExit(f"{row_id}.{key}: quote not found in the kept text of its request")


def read_text(request):
    paths = glob.glob(os.path.join(READS, f"{int(request):03d}_*.txt"))
    if not paths:
        raise SystemExit(f"request {request}: no kept text under {READS}")
    return plain(open(paths[0], encoding="utf-8").read())


def to_2025(value, year, index):
    y = str(year)
    if y not in index:
        return value  # 2026: taken as 2025 dollars
    return value * index["2025"] / index[y]


def stat(name, unit, pairs, how):
    """pairs: (row_id, ratio). Count, lowest, median, highest, and the rows at the ends."""
    if not pairs:
        return {"name": name, "unit": unit, "how": how, "n": 0}
    vals = sorted(pairs, key=lambda p: p[1])
    return {"name": name, "unit": unit, "how": how, "n": len(vals),
            "low": round(vals[0][1], 6), "low_row": vals[0][0],
            "median": round(statistics.median(v for _, v in vals), 6),
            "high": round(vals[-1][1], 6), "high_row": vals[-1][0],
            "rows": [p[0] for p in vals]}


def main(argv):
    verify = "--verify-reads" in argv
    data = json.load(open(ROWS, encoding="utf-8"))
    index = json.load(open(DEFLATOR, encoding="utf-8"))["index"]
    seen = set()
    for r in data["rows"]:
        if r["id"] in seen:
            raise SystemExit(f"{r['id']}: twice")
        seen.add(r["id"])
        text = read_text(r["doc"]["request"]) if verify else None
        for key in ("mw", "investment", "construction_jobs", "permanent_jobs", "wage"):
            check_figure(r["id"], key, r.get(key), text)
        if verify and r.get("incentive") and plain(r["incentive"]) not in text:
            raise SystemExit(f"{r['id']}.incentive: not found in the kept text")

    inv_mw, perm_mw, perm_bn, cons_bn = [], [], [], []
    for r in data["rows"]:
        inv = r.get("investment")
        inv25 = to_2025(inv["value"], inv["year"], index) if inv else None
        gen = r.get("investment_includes_generation", False)
        mw = r["mw"]["value"] if r.get("mw") else None
        perm = r.get("permanent_jobs")
        perm_ok = perm is not None and "kind not stated" not in perm["measure"]
        cons = r.get("construction_jobs")
        if inv25 and mw and not gen:
            inv_mw.append((r["id"], inv25 / mw / 1e6))
        if perm_ok and mw:
            perm_mw.append((r["id"], perm["value"] / mw))
        if perm_ok and inv25 and not gen:
            perm_bn.append((r["id"], perm["value"] / (inv25 / 1e9)))
        if cons and inv25 and not gen:
            cons_bn.append((r["id"], cons["value"] / (inv25 / 1e9)))

    out = {
        "about": "Announced datacenters and the defaults /impact offers a datacenter from them (docs/methods/forecast.md, the datacenter sections). Each row is one named project and one public document, every figure with the document's words. The defaults are medians over the rows that state both figures, each with its count, lowest and highest; a reader changes any of them. The MW of the rows measure different things (IT capacity, critical IT, critical grid capacity, power required), kept in each row; construction jobs are headcounts as announced (at peak where the document says so), never job-years.",
        "source": "warehouse/forecast/datacenter_announced_rows.json, transcribed by chain 740 (lab-desktop window 3) from the documents named in each row, read 2026-11-26 (runs/c740/probe/probe.csv requests on lab-desktop)",
        "built_by": "warehouse/forecast/datacenter_announced.py",
        "computed": data["read"],
        "dollars": "2025 dollars by the GDP implicit price deflator of deflator.json; a 2026 announcement is taken as 2025 dollars",
        "defaults": {
            "investment_per_mw": stat("Investment per MW", "USD million (2025) per MW", inv_mw,
                                      "investment over the MW the document states; rows whose investment includes power plants left out"),
            "permanent_jobs_per_mw": stat("Permanent jobs per MW", "jobs per MW", perm_mw,
                                          "permanent or operational jobs over the MW stated; jobs of a kind not stated left out"),
            "permanent_jobs_per_billion": stat("Permanent jobs per billion dollars", "jobs per USD billion (2025)", perm_bn,
                                               "permanent or operational jobs over the investment"),
            "construction_jobs_per_billion": stat("Construction jobs per billion dollars", "construction jobs (headcount as announced) per USD billion (2025)", cons_bn,
                                                  "construction jobs as announced over the investment; at peak or period not stated, as each row says"),
        },
        "rows": data["rows"],
    }
    if "--check" in argv:
        print(json.dumps(out["defaults"], indent=1))
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    for k, v in out["defaults"].items():
        print(k, v["n"], v.get("low"), v.get("median"), v.get("high"))
    print("wrote", os.path.relpath(OUT, ROOT), len(data["rows"]), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
