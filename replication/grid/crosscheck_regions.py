#!/usr/bin/env python3
"""ERW, the Grid tool's thirteen regions: a cross-check against EIA's own published regional series (session 8606, chain 504).

The region tabs of /grid draw site/data/regions/mix/<region>.json, which the data machine sums from the balancing
authorities' rows of EIA's six-month files. EIA also publishes each region's own hourly series through its open data
API (Form EIA-930: electricity/rto/region-data for demand, net generation and total interchange, and
electricity/rto/fuel-type-data for net generation by energy source, with the region's code as respondent). This
script sets the two side by side for three hours of each region: the latest hour the file holds, the same hour
seven days earlier, and the hour of the file's 35 days in which "other" is lowest.

What is compared, each in MW:
- demand (EIA type D), net generation (NG) and net imports (EIA's total interchange TI with its sign turned);
- each of the page's eight sources against EIA's codes folded as the contract folds them
  (docs/state/page_files_regions.md): natural gas NG; coal COL; nuclear NUC; wind WND and WNB; solar SUN and SNB;
  hydro WAT and PS (pumped storage); storage BAT, OES and UES; other OIL, GEO, OTH and UNK;
- every energy source together: the sum of the file's eight sources against the sum of every code EIA returns.
The codes EIA returned for the hour are written out beside storage, other and the sum, so a reader can see what is in
the hour. The file's net generation is the sum of its eight sources; EIA's NG is the total the authorities report,
which need not equal the sum of EIA's own codes, so that row may differ where the sum of the sources does not.

EIA labels an hour by a period in UTC. Whether that label is the hour's start or its end is not assumed: both are
read (the file's hour H against EIA's periods H and H+1) and the output says which one demand agrees with.

Nothing is filled: a figure either side does not hold is written "not held" and is not compared. A request that fails
is printed with its status and the region is left out; the run then exits 1.

    python replication/grid/crosscheck_regions.py [--regions DIR] [--out CSV] [--only CAL,TEX]

The key is read from the environment (EIA_API_KEY) or from the repository's .env, is sent to api.eia.gov only, and is
never printed or written. Standard library only. EIA's data are in the public domain; api.eia.gov has no robots file
(it answers /robots.txt with HTTP 403, a missing key), as the ERW's method notes for its EIA connectors record.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
API = "https://api.eia.gov/v2/electricity/rto/"
# The contract's own folding of EIA's energy source codes into the page's eight (docs/state/page_files_regions.md,
# "Sources of generation"): hydro is hydropower with pumped storage; storage is battery, other and unknown energy
# storage; other is petroleum, geothermal, other and unknown; solar and wind include the "with integrated battery
# storage" columns.
ONE = {"natural_gas": ["NG"], "coal": ["COL"], "nuclear": ["NUC"], "wind": ["WND", "WNB"], "solar": ["SUN", "SNB"], "hydro": ["WAT", "PS"],
       "storage": ["BAT", "OES", "UES"], "other": ["OIL", "GEO", "OTH", "UNK"]}
SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]
PAUSE = 0.5


def key():
    k = os.environ.get("EIA_API_KEY")
    if k:
        return k.strip()
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(ROOT), "erw", ".env")      # a worktree beside the main checkout
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("EIA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no EIA_API_KEY in the environment or in .env")


def ask(route, respondent, facet, period, k):
    """Rows of one route for one respondent and one UTC period. Returns (rows, the address without the key)."""
    params = [("frequency", "hourly"), ("data[0]", "value"), ("facets[respondent][]", respondent), ("start", period), ("end", period), ("length", "200")]
    shown = API + route + "/data/?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(shown + "&" + urllib.parse.urlencode([("api_key", k)]), headers={"User-Agent": "erw-replication"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            body = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"EIA {route} {respondent} {period}: HTTP {e.code}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"EIA {route} {respondent} {period}: {e.reason}") from None
    rows = body.get("response", {}).get("data", [])
    out = {}
    for row in rows:
        v = row.get("value")
        out[row.get(facet)] = None if v in (None, "") else float(v)
    return out, shown


def hour_of(hours, i):
    t = dt.datetime.strptime(hours["start"], "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours=i * int(hours.get("step_hours", 1)))
    return t


def period(t):
    return t.strftime("%Y-%m-%dT%H")


def latest(hourly):
    """The page's rule: the newest hour of the file that holds a net generation."""
    ng = hourly.get("net_generation") or []
    for i in range(len(ng) - 1, -1, -1):
        if ng[i] is not None:
            return i
    return None


def at(hourly, name, i):
    v = hourly.get(name)
    return None if not v or i >= len(v) or v[i] is None else float(v[i])


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--regions", default=os.path.join(ROOT, "site", "data", "regions"))
    ap.add_argument("--out", default=os.path.join(HERE, "crosscheck_regions.csv"))
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    k = key()
    with open(os.path.join(a.regions, "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    only = {c.strip().upper() for c in a.only.split(",") if c.strip()}
    rows, failed, retrieved = [], [], dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for region in index["regions"]:
        code = region["code"]
        if only and code not in only:
            continue
        with open(os.path.join(a.regions, "mix", code.lower() + ".json"), encoding="utf-8") as f:
            mix = json.load(f)
        hourly = mix.get("hourly")
        i = latest(hourly) if hourly else None
        if i is None:
            print(f"{code}: the file holds no hour with a net generation; left out")
            continue
        other = hourly.get("other") or []
        low = min((x for x in range(len(other)) if other[x] is not None), key=lambda x: other[x], default=None)
        for which, j in (("the latest hour held", i), ("seven days earlier", i - 168), ("the file's lowest hour of other", low)):
            if j is None:
                continue
            if j < 0:
                continue
            t = hour_of(hourly["hours"], j)
            try:
                got = {}
                for shift in (0, 1):
                    p = period(t + dt.timedelta(hours=shift))
                    got[shift] = (ask("region-data", code, "type", p, k), ask("fuel-type-data", code, "fueltype", p, k))
                    time.sleep(PAUSE)
            except RuntimeError as e:
                print("FAILED:", e)
                failed.append(f"{code} {period(t)}")
                continue
            file_fig = {"demand": at(hourly, "demand", j), "net_generation": at(hourly, "net_generation", j), "net_imports": at(hourly, "net_imports", j)}
            for s in SOURCES:
                file_fig[s] = at(hourly, s, j)
            held = [file_fig[s] for s in SOURCES if file_fig[s] is not None]
            file_fig["all_sources"] = sum(held) if held else None
            for shift in (0, 1):
                (reg, reg_url), (fuel, fuel_url) = got[shift]
                eia = {"demand": reg.get("D"), "net_generation": reg.get("NG"), "net_imports": None if reg.get("TI") is None else -reg["TI"]}
                for s, cs in ONE.items():
                    part = [fuel[c] for c in cs if fuel.get(c) is not None]
                    eia[s] = sum(part) if part else None                 # a source none of whose codes EIA returns is not held, never zero
                vals = [v for v in fuel.values() if v is not None]
                eia["all_sources"] = sum(vals) if vals else None
                codes = "; ".join(f"{c} {fuel[c]:,.0f}" for c in sorted(fuel) if fuel[c] is not None)
                for fig in ["demand", "net_generation", "net_imports"] + SOURCES + ["all_sources"]:
                    f_v, e_v = file_fig[fig], eia[fig]
                    diff = None if f_v is None or e_v is None else f_v - e_v
                    rows.append({"region": code, "which": which, "file_hour_utc": t.strftime("%Y-%m-%dT%H:00Z"), "eia_period_utc": period(t + dt.timedelta(hours=shift)), "eia_period_is": "the hour's start" if shift == 0 else "the hour's end",
                                 "figure": fig, "file_mw": "not held" if f_v is None else f"{f_v:.0f}", "eia_mw": "not held" if e_v is None else f"{e_v:.0f}", "difference_mw": "" if diff is None else f"{diff:.0f}",
                                 "same": "" if diff is None else ("yes" if abs(diff) <= 1 else "no"), "eia_codes_in_the_hour": codes if fig in ("all_sources", "storage", "other") else "",
                                 "source_url": (fuel_url if fig in ONE or fig == "all_sources" else reg_url)})
    # which reading of EIA's period does demand agree with
    tally = {}
    for r in rows:
        if r["figure"] == "demand" and r["same"]:
            tally.setdefault(r["eia_period_is"], [0, 0])
            tally[r["eia_period_is"]][0 if r["same"] == "yes" else 1] += 1
    best = max(tally, key=lambda x: tally[x][0]) if tally else None
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW, the Grid tool's thirteen regions against EIA's published regional series (replication/grid/crosscheck_regions.py)\n")
        f.write("# Source: U.S. Energy Information Administration, Form EIA-930, open data API v2, electricity/rto/region-data and electricity/rto/fuel-type-data (public domain)\n")
        f.write("# Source URL: each row's source_url (the key is not part of it)\n")
        f.write(f"# Retrieved: {retrieved}\n")
        f.write(f"# The file: site/data/regions/mix/<region>.json, built {index.get('built', 'not said')}\n")
        f.write(f"# EIA's period read both ways; demand agrees as: {json.dumps(tally)}\n")
        w = csv.DictWriter(f, fieldnames=["region", "which", "file_hour_utc", "eia_period_utc", "eia_period_is", "figure", "file_mw", "eia_mw", "difference_mw", "same", "eia_codes_in_the_hour", "source_url"])
        w.writeheader()
        w.writerows(rows)
    print(f"retrieved {retrieved}; {len(rows)} rows written to {os.path.relpath(a.out, ROOT)}")
    print("EIA's period read both ways; demand agrees as:", json.dumps(tally))
    if best:
        mine = [r for r in rows if r["eia_period_is"] == best and r["same"]]
        yes = sum(1 for r in mine if r["same"] == "yes")
        print(f"reading EIA's period as {best}: {yes} of {len(mine)} compared figures the same to 1 MW")
        for r in mine:
            if r["same"] == "no":
                print(f"  differs: {r['region']} {r['file_hour_utc']} {r['figure']}: file {r['file_mw']}, EIA {r['eia_mw']} ({r['difference_mw']} MW)")
    if failed:
        print("requests that failed:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
