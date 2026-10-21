#!/usr/bin/env python3
"""Every figure of every Energy Digest, traced to the warehouse table it names (session 402).

Energy Research Warehouse (ERW). The Digest (docs/digest/<date>.md, written by warehouse/news/brief.py) is markdown; the
site gives each figure of its numbers section and of its chart of the day a check key (site/lib/digest.ts). This
script reads those keys as the site makes them (site/scripts/digest-figures.mjs, run with node), and recomputes each
figure from the warehouse, by the Digest's own rule:

    digest_dam    the mean of the operating day's hourly day-ahead prices (the ISO's local day; every hour held),
                  exact and rounded half up to cents, as brief.mean2
    digest_rt     the real-time price at its interval, to two decimals
    digest_fuel   the EIA spot close on its trading day, to two decimals
    digest_chart  the chart's value and old record at their periods in the chart's table; its other figures are the
                  record's own statistics (the scan's), checked by scripts/check-values.mjs against the record

and the fun facts drawn from the warehouse (warehouse/news/facts/items/<date>.json, kind "warehouse"): a fuel's lowest
or highest close, and a state's share of a fuel in its net generation, recomputed; any other fun fact was checked word
for word against its stored source when it was written (warehouse/news/funfact.py) and is listed as such.

    python scripts/check_digest.py                       # the local CSVs (warehouse/output), read only
    python scripts/check_digest.py --in-dir DIR          # the CSVs of another copy
    python scripts/check_digest.py --supabase            # the live set, with the anon key (read only; ISO prices
                                                         # are held there for 35 days)
    python scripts/check_digest.py --figures FILE        # figures already written by digest-figures.mjs

Each figure is one line: ok, FAIL (the warehouse holds the period and gives another value), or "not here" (the source
read does not hold the period: an old copy of the CSVs, or past the live set's window). Exit 1 when any figure fails,
or when no figure could be checked; 0 otherwise. Writes nothing.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DIGEST = os.path.join(ROOT, "docs", "digest")
FACTS = os.path.join(ROOT, "warehouse", "news", "facts", "items")
TZ = {"ERCOT": "America/Chicago", "CAISO": "America/Los_Angeles", "NYISO": "America/New_York", "MISO": "Etc/GMT+5",
      "SPP": "America/Chicago", "ISO-NE": "America/New_York"}   # brief.py MAIN_HUBS: MISO's day is EST, all year
PREFIX = {"ERCOT": "ercot", "CAISO": "caiso", "NYISO": "nyiso", "MISO": "miso", "SPP": "spp", "ISO-NE": "isone"}


def current(table):
    """A table consolidated in session 29 (warehouse/metadata/table_migrations.csv) is read from its new table."""
    m = re.fullmatch(r"(caiso|ercot|miso|spp)_(dam|rtm)_hub_prices", table)
    return f"iso_{m.group(2)}_hub_prices" if m else table


def mean2(values):
    """brief.mean2: exact on the values as written, rounded half up to cents."""
    vals = [Decimal(repr(float(v))) for v in values]
    return str((sum(vals) / len(vals)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def chart_text(v):
    """daily_chart.num without its unit: 0 decimals from 10,000, 1 from 100, 2 from 1, else 4."""
    a = abs(float(v))
    nd = 0 if a >= 10000 else (1 if a >= 100 else (2 if a >= 1 else 4))
    return f"{float(v):,.{nd}f}"


def iso_z(t):
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def day_bounds(day, tz):
    z = ZoneInfo(tz)
    d = datetime.strptime(day, "%Y-%m-%d")
    start = d.replace(tzinfo=z)
    end = (d + timedelta(days=1)).replace(tzinfo=z)
    # aware datetimes of one zone subtract as wall clocks: the hours are counted in UTC (25 on the day the clocks go back)
    return start, end, int(round((end.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds() / 3600))


# ---------------------------------------------------------------------------------------------------------------------
# the sources: the CSVs, or the live set
# ---------------------------------------------------------------------------------------------------------------------
class Csv:
    name = "csv"

    def __init__(self, in_dir):
        self.dir = in_dir
        self.cache = {}

    def describe(self):
        return f"the CSVs in {self.dir}"

    def _table(self, table):
        if table not in self.cache:
            import pandas as pd
            path = os.path.join(self.dir, f"{table}.csv")
            if not os.path.exists(path):
                self.cache[table] = None
            else:
                self.cache[table] = pd.read_csv(path, comment="#", usecols=["entity", "variable", "ts_utc", "value"],
                                                dtype={"entity": str, "variable": str, "ts_utc": str}, low_memory=False)
        return self.cache[table]

    def rows(self, table, entity, variable=None, ts=None, start=None, end=None):
        df = self._table(table)
        if df is None:
            return None
        df = df[df["entity"] == entity]
        if variable:
            df = df[df["variable"] == variable]
        if ts:
            df = df[df["ts_utc"] == ts]
        if start:
            df = df[(df["ts_utc"] >= start) & (df["ts_utc"] < end)]
        return [(r.ts_utc, float(r.value), r.variable) for r in df.itertuples()]


def env(name):
    if os.environ.get(name):
        return os.environ[name]
    for f in (os.path.join(SITE, ".env.local"), os.path.join(ROOT, ".env")):
        if os.path.exists(f):
            for line in open(f, encoding="utf-8"):
                m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
                if m and m.group(1) == name:
                    return m.group(2).strip().strip('"')
    raise SystemExit(f"check_digest: {name} is not set (environment, site/.env.local or .env)")


class Live:
    name = "supabase"

    def __init__(self):
        u = urllib.parse.urlparse(env("SUPABASE_URL"))
        self.origin = f"{u.scheme}://{u.netloc}"
        self.key = env("SUPABASE_ANON_KEY")

    def describe(self):
        return f"the Supabase live set at {self.origin} (anon key)"

    def _get(self, params):
        out = []
        for off in range(0, 100000, 1000):
            q = urllib.parse.urlencode({**params, "limit": "1000", "offset": str(off)})
            req = urllib.request.Request(f"{self.origin}/rest/v1/series?{q}", headers={"apikey": self.key, "Authorization": f"Bearer {self.key}"})
            for attempt in range(3):   # a statement timeout (HTTP 500) is tried twice more, after 1 and 3 s, as check-values does
                try:
                    with urllib.request.urlopen(req, timeout=60) as r:
                        page = json.loads(r.read().decode("utf-8"))
                    break
                except urllib.error.HTTPError as exc:
                    if exc.code != 500 or attempt == 2:
                        raise
                    time.sleep(1 if attempt == 0 else 3)
            out += page
            if len(page) < 1000:
                return out
        return out

    def rows(self, table, entity, variable=None, ts=None, start=None, end=None):
        p = {"select": "ts_utc,value,variable", "table_name": f"eq.{table}", "entity": f"eq.{entity}", "order": "variable,ts_utc"}
        if variable:
            p["variable"] = f"eq.{variable}"
        if ts:
            p["ts_utc"] = f"eq.{ts}"
        if start:
            p["and"] = f"(ts_utc.gte.{start},ts_utc.lt.{end})"
        got = self._get(p)
        return [(iso_z(datetime.fromisoformat(r["ts_utc"].replace("Z", "+00:00"))), float(r["value"]), r["variable"]) for r in got]


# ---------------------------------------------------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------------------------------------------------
def check_figure(src, date, f, chart):
    """(status, warehouse value or why): status ok, FAIL, not here or record."""
    p = f["key"].split("|")
    head = p[0]
    if head == "digest_dam":
        _, iso, table, node, day = p
        start, end, hours = day_bounds(day, TZ[iso])
        rows = src.rows(current(table), f"{PREFIX[iso]}:{node}", start=iso_z(start), end=iso_z(end))
        if rows is None:
            return "not here", f"{current(table)} is not held by {src.name}"
        by = {}
        for ts, v, var in rows:
            by.setdefault(var, []).append(v)
        full = [vs for vs in by.values() if len(vs) == hours]
        if len(full) != 1:
            return "not here", f"{max((len(v) for v in by.values()), default=0)} of {hours} hours of {day} held"
        got = mean2(full[0])
        return ("ok" if got == f["raw"] else "FAIL"), got
    if head == "digest_rt":
        _, table, node, variable, ts = p
        rows = src.rows(current(table), f["entity"], variable=variable, ts=ts)
        if rows is None:
            return "not here", f"{current(table)} is not held by {src.name}"
        if not rows:
            return "not here", f"no row at {ts}"
        got = f"{rows[0][1]:.2f}"
        return ("ok" if got == f["raw"] else "FAIL"), got
    if head == "digest_fuel":
        _, table, entity, day = p
        rows = src.rows(table, entity, ts=f"{day}T00:00:00Z")
        if rows is None:
            return "not here", f"{table} is not held by {src.name}"
        if not rows:
            return "not here", f"no close on {day}"
        got = f"{rows[0][1]:.2f}"
        return ("ok" if got == f["raw"] else "FAIL"), got
    if head == "digest_chart":
        k = p[3]
        at = {"value": chart.get("date"), "old_record": chart.get("old_record_date")}.get(k)
        if not at or not chart.get("entity"):
            return "record", "a statistic of the scan, held in the chart's record (docs/digest/charts/<date>.json)"
        rows = src.rows(current(f["table"]), chart["entity"], variable=chart.get("variable") or None, ts=f"{at[:10]}T00:00:00Z")
        if rows is None:
            return "not here", f"{f['table']} is not held by {src.name}"
        if not rows:
            return "not here", f"no row at {at[:10]}"
        v = rows[0][1]
        same = abs(v - float(f["raw"])) <= 1e-6 * max(1.0, abs(v)) and chart_text(v) == f["text"]
        return ("ok" if same else "FAIL"), f"{v} (written {chart_text(v)})"
    return "FAIL", f"unknown key {f['key']}"


FUEL_SPAN = re.compile(r"eia_fuel_spot_prices (eia:\w+): (min|max) (-?[\d.]+) \S+ on (\d{4}-\d{2}-\d{2})")
SHARE_SPAN = re.compile(r"state_generation_mix_monthly eia:([A-Z]{2}): (.+?) share of net generation ([\d.]+)% in (\d{4}), ([\d.]+)% in (\d{4})")


def check_fact(src, date):
    """The day's fun fact, where it is a warehouse number: [(status, what, value)]."""
    path = os.path.join(FACTS, f"{date}.json")
    md = open(os.path.join(DIGEST, f"{date}.md"), encoding="utf-8").read()
    if "## ERW's Fun Fact" not in md:
        return []
    if not os.path.exists(path):
        return [("not here", "fun fact", "no item in warehouse/news/facts/items/ for the day")]
    item = json.load(open(path, encoding="utf-8"))
    if item.get("fact") and item["fact"] not in md:
        return [("FAIL", "fun fact", "the Digest's fun fact is not its item's")]
    if item.get("kind") != "warehouse":
        return [("source", "fun fact", f"{item.get('kind')} fact, checked word for word against its stored source when written")]
    out = []
    for s in item.get("sources", []):
        span = s.get("span", "")
        m = FUEL_SPAN.search(span)
        if m and s.get("part") == "fact":
            entity, which, v, day = m.groups()
            rows = src.rows("eia_fuel_spot_prices", entity)
            if not rows:
                out.append(("not here", f"fun fact {entity} {which}", "eia_fuel_spot_prices not held"))
                continue
            best = (min if which == "min" else max)(rows, key=lambda r: r[1])
            got = (f"{best[1]:.2f}", best[0][:10])
            out.append(("ok" if got == (f"{float(v):.2f}", day) else "FAIL", f"fun fact {entity} {which} {v} on {day}", f"{got[0]} on {got[1]}"))
            continue
        m = SHARE_SPAN.search(span)
        if m:
            state, fuel, s0, y0, s1, y1 = m.groups()
            if not isinstance(src, Csv):
                out.append(("not here", f"fun fact {state} {fuel} share", "recomputed from the CSVs only (the whole table)"))
                continue
            df = src._table("state_generation_mix_monthly")
            if df is None:
                out.append(("not here", f"fun fact {state} {fuel} share", "state_generation_mix_monthly not held"))
                continue
            t = df[df["entity"] == f"eia:{state}"]
            got = []
            for y in (y0, y1):
                ty = t[t["ts_utc"].str.startswith(y)]
                share = 100 * ty[ty["variable"] == f"net_generation_{fuel.replace(' ', '_')}_mwh"]["value"].sum() / ty["value"].sum()
                got.append(f"{share:.1f}")
            out.append(("ok" if got == [s0, s1] else "FAIL", f"fun fact {state} {fuel} share {s0}% in {y0}, {s1}% in {y1}", f"{got[0]}%, {got[1]}%"))
            continue
        out.append(("source", f"fun fact ({s.get('part')})", f"checked against its stored copy {s.get('raw', '')} when written"))
    return out


def figures(path=None, now=None):
    if path:
        return json.load(open(path, encoding="utf-8"))
    cmd = ["node", "--no-warnings", "--import", "./scripts/alias-register.mjs", "scripts/digest-figures.mjs"] + (["--now", now] if now else [])
    r = subprocess.run(cmd, cwd=SITE, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(f"check_digest: digest-figures.mjs failed (exit {r.returncode}): {r.stderr.strip()[:400]}")
    return json.loads(r.stdout)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in-dir", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--supabase", action="store_true")
    ap.add_argument("--figures")
    ap.add_argument("--date", action="append", help="only these Digests (YYYY-MM-DD; repeat)")
    a = ap.parse_args(argv)
    src = Live() if a.supabase else Csv(a.in_dir)
    data = figures(a.figures)
    print(f"check_digest: {len(data['digests'])} Digests, read against {src.describe()}; holds of {data['holds_on']}")
    n = {"ok": 0, "FAIL": 0, "not here": 0, "record": 0, "source": 0}
    for date, d in sorted(data["digests"].items()):
        if a.date and date not in a.date:
            continue
        for f in d["figures"]:
            try:
                st, got = check_figure(src, date, f, d.get("chart") or {})
            except Exception as exc:   # a failed read is not a figure checked: said so, loudly
                st, got = "not here", f"read failed: {exc!r}"[:200]
            n[st] += 1
            print(f"{st:8} | {date} | {f['key']} | page {'license needed' if f['held'] else repr(f['text'])} (raw {f['raw']}) | warehouse {got}")
        try:
            facts = check_fact(src, date)
        except Exception as exc:
            facts = [("not here", "fun fact", f"read failed: {exc!r}"[:200])]
        for st, what, got in facts:
            n[st] += 1
            print(f"{st:8} | {date} | {what} | {got}")
    print(f"\n{n['ok']} ok, {n['FAIL']} FAILED, {n['not here']} not held by this source, {n['record']} from the chart's record, "
          f"{n['source']} fun facts checked against their stored sources when written")
    if n["FAIL"]:
        return 1
    if not n["ok"]:
        print("check_digest FAILED: no figure could be checked against this source")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
