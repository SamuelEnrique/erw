#!/usr/bin/env python3
"""ERW, the Grid tool's map: a cross-check against EIA's own published interchange (session 8606, chain 504).

The map draws the network's snapshot, which the warehouse builds from its table of Form EIA-930 interchange. EIA
publishes the same form through its open data API. This script reads, for the hour the map opens on, two of EIA's
series in two requests and sets the snapshot beside them:

- electricity/rto/interchange-data: each balancing authority's report of its flow to each neighbour. A pair's flow in
  the snapshot is the report of the authority whose code sorts first (positive: it exported to the other), or, where
  that authority filed nothing for the hour, the other's report with its sign turned. Each pair is compared with the
  first authority's report in EIA's series, and where EIA holds none, with the second's turned;
- electricity/rto/region-data, type TI: each authority's own total interchange (positive: it exported). The map's
  net exchange of a region is the sum of its pairs in the snapshot. The two need not be equal (a pair counts one
  side's report, the total is the authority's own), so the difference is written, and called the same within 1 MW.

EIA's period is the hour's end (crosscheck_regions.py found it so for the regions): the snapshot's hour starting
04:00 UTC is EIA's period T05.

    python replication/grid/crosscheck_map.py [--snapshot JSON] [--out CSV]

The key is read from the environment (EIA_API_KEY) or the repository's .env, is sent to api.eia.gov only, and is never
printed or written. Standard library only. Exit 1 when a request fails; nothing is filled.
"""
import argparse
import csv
import datetime as dt
import importlib.util
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


def sibling(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ask(route, params, k):
    """Every row of one route for one period, paged. Returns (rows, the address without the key)."""
    rows, offset = [], 0
    shown = API + route + "/data/?" + urllib.parse.urlencode(params)
    while True:
        url = shown + "&" + urllib.parse.urlencode([("offset", str(offset)), ("length", "5000"), ("api_key", k)])
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "erw-replication"}), timeout=120) as r:
                body = json.loads(r.read().decode("utf-8")).get("response", {})
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"EIA {route}: HTTP {e.code}") from None
        except urllib.error.URLError as e:
            raise RuntimeError(f"EIA {route}: {e.reason}") from None
        page = body.get("data", [])
        rows += page
        offset += len(page)
        if not page or offset >= int(body.get("total", 0) or 0):
            return rows, shown
        time.sleep(0.5)


def value(row):
    v = row.get("value")
    return None if v in (None, "") else float(v)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshot", default=os.path.join(HERE, "map_snapshot.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "crosscheck_map.csv"))
    a = ap.parse_args(argv)
    rep, regions = sibling("replicate_map"), sibling("crosscheck_regions")
    snap = rep.load(a.snapshot)
    assume = rep.load(os.path.join(HERE, "assumptions.json"))
    h, _, _ = rep.complete_hour(snap["hours"], snap["links"], int(assume["network_quiet_hours"]["value"]))
    if h is None:
        print("the snapshot holds no hour every reporting pair holds")
        return 1
    start = dt.datetime.strptime(snap["hours"][h], "%Y-%m-%dT%H:%M:%SZ")
    period = (start + dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    k = regions.key()
    retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        inter, inter_url = ask("interchange-data", [("frequency", "hourly"), ("data[0]", "value"), ("start", period), ("end", period)], k)
        time.sleep(0.5)
        total, total_url = ask("region-data", [("frequency", "hourly"), ("data[0]", "value"), ("facets[type][]", "TI"), ("start", period), ("end", period)], k)
    except RuntimeError as e:
        print("FAILED:", e)
        return 1
    report = {(r.get("fromba"), r.get("toba")): value(r) for r in inter}
    ti = {r.get("respondent"): value(r) for r in total}
    rows = []
    for l in snap["links"]:
        mine = l["mw"][h]
        first, second = report.get((l["a"], l["b"])), report.get((l["b"], l["a"]))
        if first is not None:
            eia, side = first, f"{l['a']}'s report"
        elif second is not None:
            eia, side = -second, f"{l['b']}'s report, its sign turned ({l['a']} filed nothing)"
        else:
            eia, side = None, "neither side in EIA's series for the hour"
        diff = None if mine is None or eia is None else float(mine) - eia
        rows.append({"what": "a pair's flow, MW (positive: the first exported to the second)", "which": f"{l['a']}-{l['b']}", "snapshot_mw": "not held" if mine is None else f"{float(mine):.0f}", "eia_mw": "not held" if eia is None else f"{eia:.0f}",
                     "eia_side": side, "difference_mw": "" if diff is None else f"{diff:.0f}", "same": "" if diff is None else ("yes" if abs(diff) <= 1 else "no"), "source_url": inter_url})
    for n in snap["nodes"]:
        net, ties = rep.net_of(snap["links"], n["id"], h)
        eia = ti.get(n["id"])
        mine = None if net is None else -net                      # the map's net imports, turned to EIA's sign (positive: exports)
        diff = None if mine is None or eia is None else mine - eia
        rows.append({"what": "an authority's net exchange over its pairs, MW (positive: it exported), beside its own total interchange", "which": n["id"], "snapshot_mw": "not held" if mine is None else f"{mine:.0f}", "eia_mw": "not held" if eia is None else f"{eia:.0f}",
                     "eia_side": f"{n['id']}'s own total interchange (TI); the snapshot's {ties} pairs", "difference_mw": "" if diff is None else f"{diff:.0f}", "same": "" if diff is None else ("yes" if abs(diff) <= 1 else "no"), "source_url": total_url})
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW, the Grid tool's map against EIA's published interchange for the hour the map opens on (replication/grid/crosscheck_map.py)\n")
        f.write("# Source: U.S. Energy Information Administration, Form EIA-930, open data API v2, electricity/rto/interchange-data and electricity/rto/region-data type TI (public domain)\n")
        f.write("# Source URL: each row's source_url (the key is not part of it)\n")
        f.write(f"# Retrieved: {retrieved}\n")
        f.write(f"# The snapshot: built {snap.get('built')}; its hour {snap['hours'][h]} is EIA's period {period} (the hour's end)\n")
        w = csv.DictWriter(f, fieldnames=["what", "which", "snapshot_mw", "eia_mw", "eia_side", "difference_mw", "same", "source_url"])
        w.writeheader()
        w.writerows(rows)
    print(f"retrieved {retrieved}; the snapshot's hour {snap['hours'][h]}, EIA's period {period}; {len(inter)} reports and {len(total)} totals read; {len(rows)} rows written to {os.path.relpath(a.out, ROOT)}")
    for what in ("a pair's flow", "an authority's net exchange"):
        mine = [r for r in rows if r["what"].startswith(what)]
        compared = [r for r in mine if r["same"]]
        yes = sum(1 for r in compared if r["same"] == "yes")
        one_side = sum(1 for r in mine if r["snapshot_mw"] == "not held" or r["eia_mw"] == "not held")
        print(f"{what}: {yes} of {len(compared)} the same to 1 MW; {one_side} not held on one side or both")
        for r in sorted((r for r in compared if r["same"] == "no"), key=lambda r: -abs(float(r["difference_mw"])))[:12]:
            print(f"  differs: {r['which']}: snapshot {r['snapshot_mw']}, EIA {r['eia_mw']} ({r['difference_mw']} MW; {r['eia_side']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
