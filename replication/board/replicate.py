#!/usr/bin/env python3
"""ERW, the price board (/board): an independent replication of the figures of the page's file (session 7010, chain 301;
the done line's tool 17, docs/state/done_line_claims.md).

Written from docs/methods/price_board.md ("The columns of every row") and the page's public series files alone, not
from warehouse/derived/board_page.py. For every row of site/data/board.json that has its series under
site/public/board/s/<id>.json (the values the page's workbench draws, dated), it recomputes from that series:

  last          the newest value held and its date
  moves         the latest less the value held at least 1 (day), 7 (week), 30 (month) and 365 (year) days before, no
                more than 6 days older than that day (13 for a weekly row); YTD the latest less the last value held of
                the year before, as old at most; for a monthly (quarterly) row the calendar period: the month before,
                the same month (quarter) a year before, December (the fourth quarter) for YTD, and none where that
                period is not held; the percent beside a move where the file prints one (100 x the move over the base)
  avg7, avg30   the mean of the values held in the 7 and 30 days ending on the latest, and their count (daily rows)
  lo30, hi30    the lowest and highest of those 30 days (daily rows)
  avg365        the mean of the values held in the 365 days ending on the latest, its count and the latest less it,
                where 180 daily, 26 weekly, 9 monthly or 4 quarterly values are held
  range         the lowest and highest of those 365 days, their count, and where the latest sits (0 to 1)

and compares each with the file (a value printed to four decimals: a difference of 0.0001 or less is equal; a percent
printed to two: 0.01). A second part checks the power rows' daily means against the warehouse's own hourly tables
(--tables): a day's mean is the mean of a complete local day's hours, as the method says. Prints N of N.

    python replication/board/replicate.py [--site DIR] [--tables DIR]

Exit 0 when every figure is equal, 1 when one is not, 2 when the inputs cannot be read. Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BACK = {"D": {"d": 1, "w": 7, "m": 30, "y": 365}, "W": {"w": 7, "m": 30, "y": 365}}
SLACK = {"D": 6, "W": 13, "M": 31, "Q": 92}
MIN365 = {"D": 180, "W": 26, "M": 9, "Q": 4}


def day(s):
    return dt.date.fromisoformat(s[:10])


def series(path):
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    t0 = day(s["t0"])
    return [(t0 + dt.timedelta(days=int(d)), float(v)) for d, v in zip(s["d"], s["v"]) if v is not None]


def held_before(pts, target, slack):
    """The newest point on or before target, no older than target less slack days."""
    best = None
    for t, v in pts:
        if t <= target and t >= target - dt.timedelta(days=slack):
            best = (t, v)
    return best


def figures(pts, freq):
    out = {}
    if not pts:
        return out
    t, v = pts[-1]
    out["last"] = (t.isoformat(), v)
    moves = {}
    if freq in ("M", "Q"):
        # a monthly (quarterly) row's base is a calendar period: the month (quarter) before, the same month (quarter) a
        # year before, and for YTD the December (fourth quarter) of the year before; a period not held is no base
        size = 1 if freq == "M" else 3
        def period(d):
            return d.year, (d.month - 1) // size
        at = {period(d): (d, x) for d, x in pts}
        y, p_ = period(t)
        targets = {"y": (y - 1, p_), "ytd": (y - 1, (12 // size) - 1)}
        if freq == "M":
            targets["m"] = (y, p_ - 1) if p_ > 0 else (y - 1, 11)
        for k, key in targets.items():
            if key in at and key != (y, p_):
                b = at[key]
                moves[k] = (b[0].isoformat(), b[1], v - b[1])
    else:
        slack = SLACK.get(freq, 6)
        for k, n in BACK.get(freq, {}).items():
            b = held_before(pts, t - dt.timedelta(days=n), slack)
            if b:
                moves[k] = (b[0].isoformat(), b[1], v - b[1])
        b = held_before(pts, dt.date(t.year - 1, 12, 31), slack)
        if b:
            moves["ytd"] = (b[0].isoformat(), b[1], v - b[1])
    out["moves"] = moves

    def window(n):
        lo = t - dt.timedelta(days=n - 1)
        return [x for d, x in pts if lo <= d <= t]
    if freq == "D":
        for n in (7, 30):
            w = window(n)
            out[f"avg{n}"] = (sum(w) / len(w), len(w))
        w = window(30)
        out["lo30"], out["hi30"] = min(w), max(w)
    w = window(365)
    if len(w) >= MIN365.get(freq, 180):
        avg = sum(w) / len(w)
        out["avg365"] = (avg, len(w), v - avg)
        lo, hi = min(w), max(w)
        out["range"] = (lo, hi, len(w), (v - lo) / (hi - lo) if hi > lo else None)
    return out


TZ = {"ERCOT": "America/Chicago", "SPP": "America/Chicago", "MISO": "America/Chicago", "CAISO": "America/Los_Angeles"}


def daily_means(path, market_suffix):
    """{(market, entity): {local day: mean}} of the complete local days of an hourly or 15-minute hub price table: an
    hour is its one value (day-ahead) or the mean of its four 15-minute intervals when all four are held (real time);
    a day is the mean of its hours when every hour of the local day is held (24; 23 or 25 on the daylight saving days)."""
    import csv
    from collections import defaultdict
    from zoneinfo import ZoneInfo
    hours = defaultdict(lambda: defaultdict(list))
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(ln for ln in f if not ln.startswith("#")):
            if not r["market"].endswith(market_suffix) or r["value"] in ("", None):
                continue
            t = dt.datetime.fromisoformat(r["ts_utc"].replace("Z", "+00:00"))
            hours[(r["market"], r["entity"])][t.replace(minute=0, second=0)].append(float(r["value"]))
    out = {}
    for (market, ent), hs in hours.items():
        grid = market.split("_")[0].upper()
        tz = ZoneInfo(TZ.get(grid, "UTC"))
        per_day = defaultdict(list)
        for h, vals in hs.items():
            if market_suffix == "_rtm" and len(vals) != 4:
                continue
            per_day[h.astimezone(tz).date()].append(sum(vals) / len(vals))
        means = {}
        for d, vals in per_day.items():
            start = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
            nxt = dt.datetime.combine(d + dt.timedelta(days=1), dt.time(), tzinfo=tz)
            n_hours = round((nxt - start).total_seconds() / 3600)
            if len(vals) == n_hours:
                means[d] = sum(vals) / n_hours
        out[(market, ent)] = means
    return out


def compare(row, got, check):
    rid = row["id"]
    if "last" in got and "last" in row:
        check(f"{rid} last.t", got["last"][0], row["last"]["t"])
        check(f"{rid} last.v", got["last"][1], row["last"]["v"], 0.0001)
    for k, m in (row.get("moves") or {}).items():
        g = got.get("moves", {}).get(k)
        if m is None:     # the file holds no base for this move: the replication must find none either
            check(f"{rid} moves.{k} none", g and g[0], None)
            continue
        if g is None:
            check(f"{rid} moves.{k}", None, m.get("t"))
            continue
        check(f"{rid} moves.{k}.t", g[0], m["t"])
        check(f"{rid} moves.{k}.v", g[1], m["v"], 0.0001)
        check(f"{rid} moves.{k}.ch", g[2], m["ch"], 0.0002)
        if m.get("pct") is not None and g[1]:
            # the file's percent is of unrounded values, the series' values are printed to four decimals: the tolerance
            # is what that rounding can move the percent by, and 0.01 (its own last digit)
            pct = 100 * g[2] / g[1]
            tol = abs(pct) * (0.00005 / abs(g[1]) + (0.0001 / abs(g[2]) if g[2] else 0)) + 0.01
            check(f"{rid} moves.{k}.pct", pct, m["pct"], tol)
    for k in ("avg7", "avg30"):
        if row.get(k):
            g = got.get(k)
            check(f"{rid} {k}.v", g[0] if g else None, row[k]["v"], 0.0001)
            check(f"{rid} {k}.n", g[1] if g else None, row[k]["n"])
    for k in ("lo30", "hi30"):
        if row.get(k) is not None:
            check(f"{rid} {k}", got.get(k), row[k], 0.0001)
    if row.get("avg365"):
        g = got.get("avg365")
        check(f"{rid} avg365.v", g[0] if g else None, row["avg365"]["v"], 0.0001)
        check(f"{rid} avg365.n", g[1] if g else None, row["avg365"]["n"])
        check(f"{rid} avg365.ch", g[2] if g else None, row["avg365"]["ch"], 0.0002)
    if row.get("range"):
        g = got.get("range")
        check(f"{rid} range.lo", g[0] if g else None, row["range"]["lo"], 0.0001)
        check(f"{rid} range.hi", g[1] if g else None, row["range"]["hi"], 0.0001)
        check(f"{rid} range.n", g[2] if g else None, row["range"]["n"])
        if row["range"].get("pos") is not None:
            check(f"{rid} range.pos", g[3] if g else None, row["range"]["pos"], 0.0001)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The price board's replication")
    ap.add_argument("--site", default=os.path.join(ROOT, "site"))
    ap.add_argument("--show", type=int, default=40)
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"),
                    help="where iso_dam_hub_prices and iso_rtm_hub_prices are, for the second part")
    a = ap.parse_args(argv)
    try:
        with open(os.path.join(a.site, "data", "board.json"), encoding="utf-8") as f:
            board = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    n, misses, rows_read, no_series = 0, [], 0, 0

    def check(what, mine, theirs, tol=0.0):
        nonlocal n
        n += 1
        if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)) and not isinstance(mine, bool):
            ok = abs(float(mine) - float(theirs)) <= tol + 1e-9
        else:
            ok = mine == theirs
        if not ok:
            misses.append(f"{what}: replication {mine!r}, file {theirs!r}")

    for row in board["rows"]:
        p = os.path.join(a.site, "public", "board", "s", f"{row['id']}.json")
        if not os.path.exists(p):
            no_series += 1
            continue
        rows_read += 1
        compare(row, figures(series(p), row.get("freq", "D")), check)
    # part two: the power rows' series against the warehouse's hourly tables, every complete local day the tables hold
    days_checked = 0
    tables = {"da": ("iso_dam_hub_prices.csv", "_dam"), "rt": ("iso_rtm_hub_prices.csv", "_rtm")}
    for mk, (fname, suf) in tables.items():
        path = os.path.join(a.tables, fname)
        if not os.path.exists(path):
            continue
        means = daily_means(path, suf)
        for row in board["rows"]:
            tags = row.get("tags") or {}
            if row.get("group") != "power" or tags.get("market") != mk or not tags.get("grid"):
                continue
            key = (f"{tags['grid'].lower()}{suf}", f"{tags['grid'].lower()}:{row.get('code', '')}")
            p = os.path.join(a.site, "public", "board", "s", f"{row['id']}.json")
            if key not in means or not os.path.exists(p):
                continue
            ser = dict(series(p))
            for d, m in sorted(means[key].items()):
                if d in ser:
                    days_checked += 1
                    check(f"{row['id']} {d} daily mean from {fname}", m, ser[d], 0.0001)
    print(f"Part two: {days_checked:,} days of the power rows' series checked against the warehouse's hourly tables")
    print(f"The price board, from {a.site} (built {board['built']}): {rows_read:,} rows recomputed from their series; "
          f"{no_series} rows have no series file (placeholders and rows the page draws from another file)")
    for m in misses[:a.show]:
        print("  " + m)
    print(f"{n - len(misses):,} of {n:,} figures equal")
    return 0 if not misses else 1


if __name__ == "__main__":
    sys.exit(main())
