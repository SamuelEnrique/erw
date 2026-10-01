#!/usr/bin/env python3
"""The grid network, refreshed every hour (session 54): the /network snapshot rebuilt from the last 48 hours of EIA-930
interchange and demand, uploaded as one JSON object to the public Supabase Storage bucket erw-public.

Energy Research Warehouse (ERW). Run by .github/workflows/hourly-network.yml on the hour:

    python warehouse/derived/network_hourly.py                     # pull, merge, upload
    python warehouse/derived/network_hourly.py --dry-run --out F   # pull and merge, write F, upload nothing
    python warehouse/derived/network_hourly.py --skip-if-busy      # the workflow: skip while the daily or weekly job runs

What it never does (approved by Samuel, session 54): write to the Supabase database, write to warehouse/output,
warehouse/metadata or anything else in git, or run while the daily or weekly job does (--skip-if-busy asks the GitHub API
before the pull and again before the upload, and exits 0 without uploading if either is queued or running). It
records success or failure in the job log only. If it fails, the object in Storage stays as it was and the page keeps
showing it, or the committed snapshot.

The merge, onto the previous snapshot:
- The base is the newer-built of two snapshots: the object in Storage (the last hourly run) and site/data/grid_network.json
  (built by the daily run, warehouse/derived/grid_network.py, committed). Its nodes, their fixed positions and names,
  and carbon intensity (refreshed daily, by the daily run) are kept as they are. The other snapshot only lends hours.
- The pull: interchange for the 48 hours ending at the API route's own newest period (it runs more than a day behind
  the clock, so 48 clock hours would hold only about 14 hours of it and leave a hole before them); demand for the last
  48 clock hours. About 16,000 interchange rows (some 337 reports an hour, both BAs of most pairs) and 330 demand rows.
- Links: the last 168 hours, ending at the newest complete hour. A pair-hour from this run's pull replaces the same
  pair-hour of the base; hours this run did not pull keep the base's value (or, where the base has none, the other
  snapshot's). The pair rule is the daily builder's (RULE): each pair once, read from the BA whose code sorts first,
  else from the other BA's report with the sign flipped. Pairs with a node outside the base's nodes are left out
  (positions never change between daily builds), and so are EIA's regions and country totals.
- The newest complete hour: the latest hour in which at least 90 percent as many pairs reported as in the median hour
  of the window. EIA's balancing authorities report at different speeds, so the last hours of a pull are partial;
  those hours wait for a later run, never shown half filled.
- Demand: the newest hour of each of the seven ISO BAs (EIA-930 region-data, type D), with the last 48 hours kept in
  demand_recent, so check-values can find the hour a cached page shows.
- Interchange volume per node is recomputed over the merged window.

Time: EIA's hourly period is the END of the hour in UTC (as eia930.py), so an hour's start is period minus one hour.
EIA's lag (docs/methods/grid_network.md): demand is published about one to two hours after the hour; the interchange
route of the API has run more than a day behind it (its endPeriod was 2026-09-30T07 at 2026-10-01 17:00 UTC).

Self-contained (requests only; python-dotenv if present), as the connectors are. Credentials: EIA_API_KEY, SUPABASE_URL,
SUPABASE_SERVICE_KEY (upload only), GITHUB_TOKEN and GITHUB_REPOSITORY (--skip-if-busy only), from the environment or
.env. The key is removed from every URL kept or printed.
"""

import argparse
import datetime as dt
import json
import os
import statistics
import sys
import time
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
COMMITTED = os.path.join(ROOT, "site", "data", "grid_network.json")
API = "https://api.eia.gov/v2/"
INTERCHANGE, REGION = "electricity/rto/interchange-data", "electricity/rto/region-data"
BUCKET, OBJECT = "erw-public", "network/grid_network.json"
HOURS, PULL_HOURS, FULL_SHARE = 168, 48, 0.9
ISO = {"CISO": "CAISO", "ERCO": "ERCOT", "ISNE": "ISO-NE", "MISO": "MISO", "NYIS": "NYISO", "PJM": "PJM", "SWPP": "SPP"}
REGIONS = {"CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NY", "NW", "SE", "SW", "TEN", "TEX", "US48", "CAN", "MEX"}
BUSY = ("daily-prices.yml", "weekly-vacuum.yml")  # the jobs this one never overlaps


def env(name, required=True):
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            v = None
    if required and not v:
        raise SystemExit(f"{name} is not set (environment or .env)")
    return (v or "").strip().lstrip(".") if name == "EIA_API_KEY" else (v or "").strip()


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def origin(url):
    """The scheme and host of SUPABASE_URL: the secret may carry a path (/rest/v1), and Storage lives beside it. The
    dispatched run of session 54 failed here: /rest/v1/storage/v1/bucket reached PostgREST (PGRST125)."""
    u = urllib.parse.urlparse(url)
    return f"{u.scheme}://{u.netloc}"


def public_url(base):
    return f"{base}/storage/v1/object/public/{BUCKET}/{OBJECT}"


# ---------------------------------------------------------------- the pull

def eia(route, key, start, end, extra=()):
    """Every row of an EIA v2 route for the period-end hours [start, end], paged; the URLs, key removed."""
    rows, urls, offset = [], [], 0
    while True:
        params = [("api_key", key), ("frequency", "hourly"), ("data[0]", "value"), ("start", start), ("end", end),
                  ("sort[0][column]", "period"), ("sort[0][direction]", "asc"), ("offset", str(offset)), ("length", "5000"), *extra]
        for attempt in range(3):
            try:
                r = requests.get(API + route + "/data/", params=params, timeout=120)
                if r.status_code == 200:
                    break
                err = f"HTTP {r.status_code}: {r.text[:200]}"
            except requests.RequestException as e:
                err = type(e).__name__
            if attempt == 2:
                raise RuntimeError(f"EIA {route} offset {offset}: {err.replace(key, '<key>')}")
            time.sleep(5 * (attempt + 1))
        body = r.json()["response"]
        page = body.get("data", [])
        rows += page
        urls.append(r.url.replace(key, "<key>"))
        offset += len(page)
        if not page or offset >= int(body.get("total", 0)):
            if offset != int(body.get("total", 0)):
                raise RuntimeError(f"EIA {route}: got {offset} rows, the API reported {body.get('total')}")
            return rows, urls
        time.sleep(0.5)


def end_period(route, key):
    """The newest period the route holds (its metadata's endPeriod), as a datetime."""
    r = requests.get(API + route + "/", params={"api_key": key}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"EIA {route} metadata HTTP {r.status_code}")
    return dt.datetime.strptime(r.json()["response"]["endPeriod"], "%Y-%m-%dT%H").replace(tzinfo=dt.timezone.utc)


def pull(key, now):
    """The last PULL_HOURS hours of interchange (every pair) and demand (the seven ISO BAs). Interchange: the 48 hours
    ending at the route's own newest period, not at the clock, since the route runs more than a day behind the clock
    and 48 clock hours would leave hours between the daily snapshot and this pull empty. Demand: the 48 clock hours."""
    xe = min(end_period(INTERCHANGE, key), now + dt.timedelta(hours=1))
    x, xu = eia(INTERCHANGE, key, (xe - dt.timedelta(hours=PULL_HOURS - 1)).strftime("%Y-%m-%dT%H"), xe.strftime("%Y-%m-%dT%H"))
    start = (now - dt.timedelta(hours=PULL_HOURS - 1)).strftime("%Y-%m-%dT%H")
    end = (now + dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    d, du = eia(REGION, key, start, end, [("facets[type][]", "D")] + [("facets[respondent][]", c) for c in sorted(ISO)])
    return x, d, xu + du


def hour_of(period):
    """EIA's period (the hour's end, UTC) to the hour's start, ISO."""
    return iso(dt.datetime.strptime(period, "%Y-%m-%dT%H").replace(tzinfo=dt.timezone.utc) - dt.timedelta(hours=1))


def pair_flows(rows, nodes):
    """{(a, b): {hour: mw}} by the pair rule, for pairs whose BAs are both nodes; and the pairs left out."""
    pick, out = {}, set()
    for r in rows:
        if r.get("value") is None:
            continue
        f, t = r["fromba"].upper(), r["toba"].upper()
        if f in REGIONS or t in REGIONS or f == t:
            continue
        a, b = sorted((f, t))
        if a not in nodes or b not in nodes:
            out.add((a, b))
            continue
        v = float(r["value"]) * (1 if f == a else -1)
        h = hour_of(r["period"])
        if f == a or (a, b, h) not in pick:  # the first BA's report wins
            pick[(a, b, h)] = v
    flows = {}
    for (a, b, h), v in pick.items():
        flows.setdefault((a, b), {})[h] = v
    return flows, out


def newest_full_hour(flows):
    """The latest hour in which at least FULL_SHARE of the median hour's number of pairs reported, or None."""
    per = {}
    for f in flows.values():
        for h in f:
            per[h] = per.get(h, 0) + 1
    if not per:
        return None, per
    med = statistics.median(per.values())
    full = [h for h, n in per.items() if n >= FULL_SHARE * med]
    return (max(full) if full else None), per


def demand_of(rows):
    """{BA: {hour: MW}} from region-data type D."""
    out = {}
    for r in rows:
        if r.get("value") is not None and r["respondent"] in ISO and r.get("type") == "D":
            out.setdefault(r["respondent"], {})[hour_of(r["period"])] = float(r["value"])
    return out


# ---------------------------------------------------------------- the merge

def as_map(snap):
    """{(a, b): {hour: mw}} from a snapshot's links."""
    return {(l["a"], l["b"]): {h: v for h, v in zip(snap["hours"], l["mw"]) if v is not None} for l in snap.get("links", [])}


def merge(base, other, flows, newest, demand, built, meta=None):
    """The new snapshot: base's nodes and positions unchanged, the last HOURS hours of links ending at newest (each
    pair-hour from flows, else base, else other), node volumes recomputed, ISO demand from demand where pulled."""
    end = parse(newest) + dt.timedelta(hours=1)
    start = end - dt.timedelta(hours=HOURS)
    hours = [iso(start + dt.timedelta(hours=i)) for i in range(HOURS)]
    old, lend = as_map(base), as_map(other) if other else {}
    ids = {n["id"] for n in base["nodes"]}
    links = []
    for p in sorted(set(old) | set(lend) | set(flows)):
        if p[0] not in ids or p[1] not in ids:
            continue
        f, o, l = flows.get(p, {}), old.get(p, {}), lend.get(p, {})
        mw = [round(f[h], 1) if h in f else o.get(h, l.get(h)) for h in hours]
        if any(v is not None for v in mw):
            links.append(dict(a=p[0], b=p[1], mw=mw))
    vol = {i: 0.0 for i in ids}
    for l in links:
        v = sum(abs(x) for x in l["mw"] if x is not None)
        vol[l["a"]] += v
        vol[l["b"]] += v
    nodes = []
    for n in base["nodes"]:
        n = dict(n, volume_mwh=round(vol[n["id"]], 1))
        d = demand.get(n["id"])
        if d:
            last = max(d)
            n.update(demand_mw=d[last], demand_ts=last, demand_src="hourly", demand_recent={h: d[h] for h in sorted(d)})
        nodes.append(n)
    snap = {k: v for k, v in base.items() if k not in ("nodes", "links", "hours", "window", "built")}
    snap.update(built=built, window=[iso(start), iso(end)], hours=hours, newest_hour=newest, refresh="hourly",
                base_built=base["built"], nodes=nodes, links=links, **(meta or {}))
    return snap


def check(snap, base):
    """Refuse a snapshot that is not whole: the same nodes at the same positions, 168 contiguous hours, every link 168
    long, and most pairs reporting in the newest hour."""
    assert len(snap["hours"]) == HOURS, "hours"
    assert all(parse(b) - parse(a) == dt.timedelta(hours=1) for a, b in zip(snap["hours"], snap["hours"][1:])), "hours not contiguous"
    pos = lambda s: [(n["id"], n["x"], n["y"], n["z"]) for n in s["nodes"]]  # noqa: E731
    assert pos(snap) == pos(base), "nodes or positions changed"
    assert all(len(l["mw"]) == HOURS for l in snap["links"]), "a link is not 168 hours long"
    last = sum(l["mw"][-1] is not None for l in snap["links"])
    assert last >= 100, f"only {last} pairs in the newest hour"
    return last


# ---------------------------------------------------------------- GitHub and Storage

def busy():
    """The daily or weekly job's run in progress or queued, or None. Needs GITHUB_TOKEN and GITHUB_REPOSITORY."""
    token, repo = env("GITHUB_TOKEN"), env("GITHUB_REPOSITORY")
    for wf in BUSY:
        for status in ("in_progress", "queued", "waiting", "pending"):
            r = requests.get(f"https://api.github.com/repos/{repo}/actions/workflows/{wf}/runs", params={"status": status, "per_page": 1},
                             headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=30)
            r.raise_for_status()
            runs = r.json().get("workflow_runs", [])
            if runs:
                return f"{wf} run {runs[0]['id']} is {status}"
    return None


def read_storage(base):
    """The object in the public bucket, or None (absent or unreachable)."""
    try:
        r = requests.get(public_url(base), timeout=30, headers={"Cache-Control": "no-cache"})
        return r.json() if r.status_code == 200 else None
    except (requests.RequestException, ValueError):
        return None


def upload(base, key, body):
    h = {"Authorization": f"Bearer {key}", "apikey": key}
    r = requests.get(f"{base}/storage/v1/bucket/{BUCKET}", headers=h, timeout=30)
    if r.status_code != 200:
        r = requests.post(f"{base}/storage/v1/bucket", headers=h, json={"id": BUCKET, "name": BUCKET, "public": True}, timeout=30)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"creating bucket {BUCKET}: HTTP {r.status_code} {r.text[:200]}")
        print(f"created the public storage bucket {BUCKET}")
    elif not r.json().get("public"):
        raise RuntimeError(f"bucket {BUCKET} is not public")
    r = requests.post(f"{base}/storage/v1/object/{BUCKET}/{OBJECT}", data=body,
                      headers={**h, "Content-Type": "application/json", "x-upsert": "true", "Cache-Control": "max-age=60"}, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"upload: HTTP {r.status_code} {r.text[:200]}")


# ---------------------------------------------------------------- the run

def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the grid network, refreshed hourly (session 54)")
    ap.add_argument("--dry-run", action="store_true", help="upload nothing")
    ap.add_argument("--out", help="also write the snapshot here")
    ap.add_argument("--skip-if-busy", action="store_true", help="exit 0 without uploading while the daily or weekly job runs")
    a = ap.parse_args(argv)
    t0 = time.time()
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    built = iso(dt.datetime.now(dt.timezone.utc).replace(microsecond=0))
    if a.skip_if_busy and (b := busy()):
        print(f"network_hourly: skipped, {b}; nothing pulled or uploaded")
        return 0
    sb = origin(env("SUPABASE_URL"))
    with open(COMMITTED, encoding="utf-8") as f:
        committed = json.load(f)
    stored = read_storage(sb)
    base, other = (stored, committed) if stored and stored.get("built", "") > committed["built"] else (committed, stored)
    print(f"base: {'Storage' if base is stored else 'the committed snapshot'}, built {base['built']}, newest hour {base['hours'][-1]}"
          f"{'' if stored else '; no object in Storage yet'}")
    key = env("EIA_API_KEY")
    x, d, urls = pull(key, now)
    flows, left = pair_flows(x, {n["id"] for n in base["nodes"]})
    newest, per = newest_full_hour(flows)
    demand = demand_of(d)
    eia_last = max((r["period"] for r in x), default=None)
    print(f"pulled {len(x)} interchange rows (newest EIA period {eia_last}) and {len(d)} demand rows; {len(flows)} pairs; "
          f"{len(left)} pairs with a BA outside the snapshot's nodes left out")
    if newest is None:
        raise SystemExit("network_hourly FAILED: no interchange in the last 48 hours; nothing uploaded")
    late = sorted(h for h in per if h > newest)
    print(f"newest complete hour {newest} ({per[newest]} pairs); later partial hours left for a later run: "
          + (", ".join(f"{h} ({per[h]})" for h in late) or "none"))
    if newest < base["hours"][-1]:
        newest = base["hours"][-1]  # never move the window back
    meta = dict(pull=dict(interchange_rows=len(x), demand_rows=len(d), eia_interchange_end=eia_last,
                          demand_newest={c: max(v) for c, v in sorted(demand.items())}, urls=urls))
    snap = merge(base, other, flows, newest, demand, built, meta)
    last = check(snap, base)
    body = json.dumps(snap, separators=(",", ":")).encode("utf-8")
    print(f"snapshot: {len(snap['nodes'])} nodes, {len(snap['links'])} links, window {snap['window'][0]} to {snap['window'][1]}, "
          f"{last} pairs in the newest hour, {len(body) / 1024:.0f} KB")
    if a.out:
        with open(a.out, "wb") as f:
            f.write(body)
    if a.dry_run:
        print("dry run: nothing uploaded")
    elif a.skip_if_busy and (b := busy()):
        print(f"network_hourly: skipped before the upload, {b}; nothing uploaded")
    else:
        upload(sb, env("SUPABASE_SERVICE_KEY"), body)
        print(f"uploaded {public_url(sb).split('/storage/')[1]}")
    print(f"network_hourly: ok in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # the job log is the record: one line, the key never in it
        k = os.environ.get("EIA_API_KEY") or ""
        msg = f"{type(e).__name__}: {e}"
        print(f"network_hourly FAILED: {msg.replace(k, '<key>') if k else msg}", file=sys.stderr)
        sys.exit(1)
