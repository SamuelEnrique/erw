# Session 10206 (chain 710, part D): the price board's computed columns restated from the page's own files, written
# from docs/methods/price_board.md and docs/methods/trader_view.md, not from the builder (warehouse/derived/board_page.py)
# or the replication (replication/board/replicate.py). Standard library only. Reads site/data/board.json and the
# workbench's files (site/public/board/s/<id>.json, a row's series; site/public/board/h/<id>.json, a hub's hours).
# Never prints a held grid's value (NYISO, ISO-NE, MISO, PJM): their rows are counted, not shown.
#   python restate_board.py [part ...]   parts: rows hours spreads week
import collections
import datetime as dt
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site")
B = json.load(open(os.path.join(SITE, "data", "board.json"), encoding="utf-8"))
BUILT = dt.date.fromisoformat(B["built"][:10])
HELD = ("nyiso", "isone", "miso", "pjm")
PARTS = set(sys.argv[1:]) or {"rows", "hours", "spreads", "week"}
ROWS = {r["id"]: r for r in B["rows"]}
OK = [r for r in B["rows"] if r.get("status") == "ok"]
TOL = 0.00005 + 1e-9   # the file keeps 4 decimals


def day(s):
    return dt.date.fromisoformat(s[:10])


def series(rid):
    p = os.path.join(SITE, "public", "board", "s", rid + ".json")
    if not os.path.exists(p):
        return None
    f = json.load(open(p, encoding="utf-8"))
    t0 = day(f["t0"])
    return sorted((t0 + dt.timedelta(days=d), v) for d, v in zip(f["d"], f["v"]))


def hourly(hid):
    p = os.path.join(SITE, "public", "board", "h", hid + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


class Gap:
    """The largest gap and the count of figures compared, by kind."""

    def __init__(self):
        self.n = collections.Counter()
        self.bad = collections.Counter()
        self.worst = {}
        self.examples = collections.defaultdict(list)
        self.public = collections.Counter()

    def add(self, kind, mine, theirs, rid, tol=TOL):
        self.n[kind] += 1
        if mine is None or theirs is None:
            ok = mine is None and theirs is None
            g = 0.0 if ok else math.inf
        else:
            g = abs(mine - theirs)
            ok = g <= tol
        if g > self.worst.get(kind, (-1, ""))[0]:
            self.worst[kind] = (g, rid)
        if not ok:
            self.bad[kind] += 1
            if not rid.startswith(HELD):
                self.public[kind] += 1
            if len(self.examples[kind]) < 4 and not (rid.startswith(HELD) and self.public[kind] == 0 and self.bad[kind] > 1):
                shown = rid.startswith(HELD)
                self.examples[kind].append(f"{rid}: mine {'held' if shown else mine} file {'held' if shown else theirs}")

    def report(self, title):
        print(f"--- {title}: {sum(self.n.values())} figures compared, {sum(self.bad.values())} differ ({sum(self.public.values())} of them on public rows)")
        for k in sorted(self.n):
            w = self.worst.get(k, (0, ""))
            print(f"  {k:28s} {self.n[k]:6d} compared, {self.bad[k]:4d} differ ({self.public[k]} public), largest gap {w[0]:.6g} ({'a held row' if w[1].startswith(HELD) else w[1]})")
            for e in self.examples.get(k, []):
                print("      " + e)


# ---------------------------------------------------------------------------------------------------------------------
# Part 1: a row's figures from its series file, by the note's table "The columns of every row"
MIN_YEAR = {"D": 180, "W": 26, "M": 9, "Q": 4}


def newest_between(pts, lo, hi):
    best = None
    for d, v in pts:
        if lo <= d <= hi:
            best = (d, v)
    return best


def add_months(d, k):
    y, m = divmod(d.year * 12 + d.month - 1 + k, 12)
    return dt.date(y, m + 1, 1)


def restated(pts, freq):
    L, v0 = pts[-1]
    at = dict(pts)

    def back(n):   # the newest value at least n days before, no more than 6 days older than that
        return newest_between(pts, L - dt.timedelta(days=n + 6), L - dt.timedelta(days=n))

    def cal(k):    # a monthly or quarterly row: the same calendar period k months before
        d = add_months(L, k)
        return (d, at[d]) if d in at else None

    out = {}
    if freq == "D":
        mv = {"d": back(1), "w": back(7), "m": back(30), "y": back(365)}
    elif freq == "W":
        target = L - dt.timedelta(days=364)
        near = [(abs((d - target).days), d, v) for d, v in pts if abs((d - target).days) <= 3]
        near.sort()
        mv = {"d": None, "w": back(7), "m": back(30), "y": (near[0][1], near[0][2]) if near else None}
    elif freq == "M":
        mv = {"d": None, "w": None, "m": cal(-1), "y": cal(-12)}
    else:
        mv = {"d": None, "w": None, "m": None, "y": cal(-12)}
    # YTD: the last value of the year before, no older than the step's slack before 31 December
    dec31 = dt.date(L.year - 1, 12, 31)
    floor = {"D": dec31 - dt.timedelta(days=6), "W": dec31 - dt.timedelta(days=13), "M": dt.date(L.year - 1, 12, 1), "Q": dt.date(L.year - 1, 10, 1)}[freq]
    mv["ytd"] = newest_between(pts, floor, dec31)
    out["moves"] = {k: (None if b is None else {"t": b[0], "v": b[1], "ch": v0 - b[1], "pct": (100 * (v0 - b[1]) / b[1]) if b[1] > 0 else None}) for k, b in mv.items()}
    year = [v for d, v in pts if L - dt.timedelta(days=365) < d <= L]
    if len(year) >= MIN_YEAR[freq]:
        lo, hi = min(year), max(year)
        out["range"] = {"lo": lo, "hi": hi, "n": len(year), "pos": (v0 - lo) / (hi - lo) if hi > lo else None}
        out["avg365"] = {"v": sum(year) / len(year), "n": len(year), "ch": v0 - sum(year) / len(year)}
    if freq == "D":
        for n in (7, 30):
            w = [v for d, v in pts if L - dt.timedelta(days=n) < d <= L]
            out[f"avg{n}"] = {"v": sum(w) / len(w), "n": len(w)}
            if n == 30:
                out["lo30"], out["hi30"] = min(w), max(w)
    span = {"D": L - dt.timedelta(days=90), "W": L - dt.timedelta(days=365)}.get(freq)
    if span is None:
        start = add_months(L, -35 if freq == "M" else -33)
        out["spark"] = [(d, v) for d, v in pts if d >= start]
    else:
        out["spark"] = [(d, v) for d, v in pts if d > span]
    return out


def part_rows():
    g = Gap()
    seen = collections.Counter()
    ends = []
    for r in OK:
        pts = series(r["id"])
        if pts is None:
            seen["no series file"] += 1
            continue
        last = day(r["last"]["t"])
        if pts[-1][0] != last:
            ends.append((r["id"], last, pts[-1][0], len(pts)))
        pts = [p for p in pts if p[0] <= last]
        if not pts or pts[-1][0] != last:
            seen["row's latest not in its series file"] += 1
            continue
        seen["restated"] += 1
        x = restated(pts, r["freq"])
        rid = r["id"]
        g.add("latest", pts[-1][1], r["last"]["v"], rid)
        for k in ("d", "w", "m", "y", "ytd"):
            mine, file = x["moves"].get(k), (r.get("moves") or {}).get(k)
            if mine is None or file is None:
                g.add(f"move {k}: held or not", 0.0 if mine is None else 1.0, 0.0 if file is None else 1.0, rid, tol=0)
                continue
            g.add(f"move {k}: base date", 0.0, float((mine["t"] - day(file["t"])).days), rid, tol=0)
            g.add(f"move {k}: change", mine["ch"], file["ch"], rid, tol=2 * TOL)
            if file.get("pct") is not None and not r.get("formula") and r["unit"] not in ("USD/MWh", "USD/MW-hour", "percent"):
                g.add(f"move {k}: percent shown", mine["pct"], file["pct"], rid, tol=0.005 + 1e-9)
        for k in ("avg7", "avg30", "avg365"):
            mine, file = x.get(k), r.get(k)
            if (mine is None) != (file is None):
                g.add(f"{k}: drawn or not", 0.0 if mine is None else 1.0, 0.0 if file is None else 1.0, rid, tol=0)
            elif mine:
                g.add(f"{k}: mean", mine["v"], file["v"], rid)
                g.add(f"{k}: count", mine["n"], file["n"], rid, tol=0)
                if k == "avg365":
                    g.add("avg365: latest less mean", mine["ch"], file["ch"], rid, tol=2 * TOL)
        if "lo30" in r:
            g.add("30-day low", x.get("lo30"), r["lo30"], rid)
            g.add("30-day high", x.get("hi30"), r["hi30"], rid)
        if (x.get("range") is None) != (r.get("range") is None):
            g.add("range: drawn or not", 0.0 if x.get("range") is None else 1.0, 0.0 if r.get("range") is None else 1.0, rid, tol=0)
        elif x.get("range"):
            for k in ("lo", "hi", "n"):
                g.add(f"range {k}", x["range"][k], r["range"][k], rid, tol=0 if k == "n" else TOL)
            if r["range"].get("pos") is not None:
                g.add("range position", x["range"]["pos"], r["range"]["pos"], rid, tol=0.00005 + 1e-9)
        sp = r.get("spark")
        if sp:
            t0 = day(sp["t0"])
            theirs = [(t0 + dt.timedelta(days=d), v) for d, v in zip(sp["d"], sp["v"])]
            g.add("trend: points the same", 0.0, 0.0 if [d for d, _ in theirs] == [d for d, _ in x["spark"]] else 1.0, rid, tol=0)
    print("rows:", dict(seen))
    print(f"rows whose series file ends on another day than the row's latest: {len(ends)}")
    for rid, last, end, n in ends[:12]:
        print(f"   {rid}: row's latest {last}, series file ends {end} ({n} points)")
    g.report("Part 1, each row's figures from its own series file")
    return ends


# ---------------------------------------------------------------------------------------------------------------------
# Part 2: the power rows from the hours (site/public/board/h): daily means of complete local days, on-peak and off-peak
# (hours beginning 06:00 to 21:59 local, Monday to Friday, CAISO Monday to Saturday, NERC holidays off-peak), the battery
# spread (the day's highest hour less its lowest) and the day's extremes. The hours in the file are rounded to the cent.

def nerc_holidays(y):
    def nth(month, weekday, n):
        d = dt.date(y, month, 1)
        d += dt.timedelta(days=(weekday - d.weekday()) % 7)
        return d + dt.timedelta(days=7 * (n - 1))

    def last(month, weekday):
        d = dt.date(y, month + 1, 1) - dt.timedelta(days=1)
        return d - dt.timedelta(days=(d.weekday() - weekday) % 7)

    out = set()
    for d in (dt.date(y, 1, 1), last(5, 0), dt.date(y, 7, 4), nth(9, 0, 1), nth(11, 3, 4), dt.date(y, 12, 25)):
        out.add(d + dt.timedelta(days=1) if d.weekday() == 6 else d)
    return out


HOLI = {}


def on_peak(local, iso):
    y = local.year
    if y not in HOLI:
        HOLI[y] = nerc_holidays(y)
    last_day = 5 if iso == "caiso" else 4
    return local.weekday() <= last_day and 6 <= local.hour <= 21 and local.date() not in HOLI[y]


def days_of(h, market):
    """{local date: [(utc hour, local datetime, value)]} for the complete local days of one market."""
    tz = ZoneInfo(h["tz"])
    vals = h.get(market) or []
    by = collections.defaultdict(list)
    for i, v in enumerate(vals):
        utc = dt.datetime.fromtimestamp((h["t0"] + i) * 3600, tz=dt.timezone.utc)
        loc = utc.astimezone(tz)
        by[loc.date()].append((utc, loc, v))
    out = {}
    for d, hs in by.items():
        start = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
        nxt = d + dt.timedelta(days=1)
        end = dt.datetime(nxt.year, nxt.month, nxt.day, tzinfo=tz)
        want = round((end.astimezone(dt.timezone.utc) - start.astimezone(dt.timezone.utc)).total_seconds() / 3600)
        if len(hs) == want and all(v is not None for _, _, v in hs):
            out[d] = hs
    return out


def part_hours():
    g = Gap()
    pkdiff = collections.Counter()
    for r in OK:
        if r["group"] != "power" or not r.get("hourly"):
            continue
        h = hourly(r["hourly"])
        if h is None:
            continue
        iso = r["id"].split("-")[0]
        market = r["tags"].get("market")
        tz = ZoneInfo(h["tz"])
        # the on-peak flags of the file against the rule written again
        if market == "da":
            for i in range(h["n"]):
                loc = dt.datetime.fromtimestamp((h["t0"] + i) * 3600, tz=dt.timezone.utc).astimezone(tz)
                mine = on_peak(loc, iso)
                pkdiff["hours"] += 1
                if mine != (h["pk"][i] == "1"):
                    pkdiff["differ"] += 1
                    if pkdiff["differ"] <= 3:
                        print(f"   on-peak flag differs: {r['hourly']} {loc.isoformat()} file {h['pk'][i]}")
        days = days_of(h, market)
        pts = series(r["id"]) or []
        file_daily = dict(pts)
        rid = r["id"]
        for d, hs in days.items():
            if d in file_daily and d >= min(days):
                g.add("daily mean, to the cent", sum(v for *_, v in hs) / len(hs), file_daily[d], rid, tol=0.005 + 1e-9)
                g.add("daily mean, to 4 decimals", sum(v for *_, v in hs) / len(hs), file_daily[d], rid, tol=TOL)
        held_days = sorted(file_daily)
        missing = [d for d in days if d not in file_daily and held_days and held_days[0] <= d <= held_days[-1]]
        extra = [d for d in file_daily if d >= min(days, default=dt.date(2100, 1, 1)) and d <= max(days, default=dt.date(1900, 1, 1)) and d not in days]
        g.add("complete days the file lacks", 0.0, float(len(missing)), rid, tol=0)
        g.add("file days not complete in hours", 0.0, float(len(extra)), rid, tol=0)
        # peak, off-peak, peak less off, battery: against their own rows' series files
        for suffix, fn in (("-peak", "peak"), ("-offpeak", "off"), ("-peak-less-off", "less"), ("-battery", "bat")):
            sid = rid + suffix
            if sid not in ROWS or ROWS[sid].get("status") != "ok":
                continue
            other = dict(series(sid) or [])
            for d, hs in days.items():
                pk = [v for _, loc, v in hs if on_peak(loc, iso)]
                off = [v for _, loc, v in hs if not on_peak(loc, iso)]
                if fn == "peak":
                    mine = sum(pk) / len(pk) if pk else None
                elif fn == "off":
                    mine = sum(off) / len(off) if off else None
                elif fn == "less":
                    mine = (sum(pk) / len(pk) - sum(off) / len(off)) if pk and off else None
                else:
                    mine = max(v for *_, v in hs) - min(v for *_, v in hs)
                if d in other:
                    g.add(f"{fn}: day's figure, to the cent", mine, other[d], sid, tol=0.005 + 1e-9)
                elif mine is not None and other and min(other) <= d <= max(other):
                    g.add(f"{fn}: a day the file lacks", 0.0, 1.0, sid, tol=0)
        # the day's extremes and the week's and month's peak hour and hours above
        e = r.get("ext")
        if e:
            ed = day(e["t"])
            if ed in days:
                hs = days[ed]
                hi = max(hs, key=lambda x: x[2])
                lo = min(hs, key=lambda x: x[2])
                g.add("ext: day's high", hi[2], e["hi"]["v"], rid, tol=0.005)
                g.add("ext: day's low", lo[2], e["lo"]["v"], rid, tol=0.005)
                g.add("ext: high's local hour", 0.0, 0.0 if hi[1].strftime("%H:%M") == e["hi"]["local"] or hi[2] == e["hi"]["v"] else 1.0, rid, tol=0)
                g.add("ext: hours", float(len(hs)), float(e["hours"]), rid, tol=0)
                for k, n in (("w", 7), ("m", 30)):
                    x = e.get(k)
                    if not x:
                        continue
                    win = [d for d in days if ed - dt.timedelta(days=n) < d <= ed]
                    allh = [v for d in win for *_, v in days[d]]
                    g.add(f"ext {k}: complete days", float(len(win)), float(x["days"]), rid, tol=0)
                    g.add(f"ext {k}: hours", float(len(allh)), float(x["hours"]), rid, tol=0)
                    g.add(f"ext {k}: peak hour", max(allh), x["peak"]["v"], rid, tol=0.005)
                    for th in ("100", "250", "1000"):
                        g.add(f"ext {k}: hours above {th}", float(sum(1 for v in allh if v > float(th))), float(x["above"][th]), rid, tol=0)
            else:
                g.add("ext: its day complete in the hours", 0.0, 1.0, rid, tol=0)
    print(f"on-peak flags: {pkdiff['hours']} hours read, {pkdiff['differ']} differ from the rule written again")
    g.report("Part 2, the power rows from the hours")


# ---------------------------------------------------------------------------------------------------------------------
# Part 3: the spreads, each from its input rows' series files

def find_input(value, when, groups, unit=None):
    """The ok row of the given groups whose series holds `value` on `when` (to 4 decimals)."""
    hits = []
    for r in OK:
        if r["group"] not in groups or (unit and r["unit"] != unit):
            continue
        pts = dict(series(r["id"]) or [])
        if when in pts and abs(pts[when] - value) <= TOL:
            hits.append(r["id"])
    return hits


def part_spreads():
    g = Gap()
    notes = []
    hh = dict(series("eia-henry-hub-spot") or [])
    HR, CHR, BACK = B["heat_rate"], B["coal_heat_rate"], B["gas_back_days"]
    for r in OK:
        rid, grp = r["id"], r["group"]
        file = dict(series(rid) or [])
        if not file:
            continue
        if grp == "hubspread":
            a, b = r["code"].split(" less ")
            m = r["tags"]["market"]
            ida = [x["id"] for x in OK if x["group"] == "power" and x["code"] == a and x["tags"].get("market") == m]
            idb = [x["id"] for x in OK if x["group"] == "power" and x["code"] == b and x["tags"].get("market") == m]
            if not ida or not idb:
                notes.append(f"{rid}: an input row is not on the board")
                continue
            sa, sb = dict(series(ida[0])), dict(series(idb[0]))
            for d, v in file.items():
                if d in sa and d in sb:
                    g.add("hub spread", sa[d] - sb[d], v, rid, tol=2 * TOL)
                else:
                    g.add("hub spread: a day an input lacks", 0.0, 1.0, rid, tol=0)
            both = [d for d in sa if d in sb and d >= min(file) and d <= max(file)]
            g.add("hub spread: input days it lacks", 0.0, float(sum(1 for d in both if d not in file)), rid, tol=0)
        elif grp == "spark" and r["freq"] == "D":
            hub = r["id"].rsplit("-", 1)[0] + "-da"
            da = dict(series(hub) or [])
            kind = r["id"].rsplit("-", 1)[1]
            for d, v in file.items():
                gd = next((d - dt.timedelta(days=k) for k in range(0, BACK + 1) if d - dt.timedelta(days=k) in hh), None)
                if d not in da or gd is None:
                    g.add(f"{kind}: a day an input lacks", 0.0, 1.0, rid, tol=0)
                    continue
                mine = da[d] - HR * hh[gd] if kind == "spark" else da[d] / hh[gd]
                g.add(f"{kind}", mine, v, rid, tol=2 * TOL)
            lacks = [d for d in da if d >= min(file) and any(d - dt.timedelta(days=k) in hh for k in range(BACK + 1)) and d not in file]
            g.add(f"{kind}: days it could hold and lacks", 0.0, float(len(lacks)), rid, tol=0)
            if lacks and not rid.startswith(HELD):
                notes.append(f"{rid}: {len(lacks)} days with a day-ahead mean and a gas price within {BACK} days are not in the row, newest {max(lacks)}")
        elif grp == "spark" and r["freq"] == "M":
            hub = r["id"].rsplit("-", 1)[0] + "-da"
            da = series(hub) or []
            coal_ids = find_input(r["inputs"]["coal"], day(r["inputs"]["coal_t"]), {"plantfuel"})
            if not coal_ids:
                notes.append(f"{rid}: the coal row is not found")
                continue
            coal = dict(series(coal_ids[0]))
            months = collections.defaultdict(list)
            for d, v in da:
                months[dt.date(d.year, d.month, 1)].append(v)
            for m, v in file.items():
                nd = (add_months(m, 1) - m).days
                if m in coal and len(months.get(m, [])) == nd:
                    g.add("dark", sum(months[m]) / nd - CHR * coal[m], v, rid, tol=2 * TOL)
                else:
                    g.add("dark: a month an input lacks", 0.0, 1.0, rid, tol=0)
        elif r.get("inputs") and "crude" in r["inputs"]:
            i, t = r["inputs"], day(r["inputs"]["t"])
            crude = find_input(i["crude"], t, {"crude"}, "USD/bbl")
            if "gasoline" in i:
                gas = find_input(i["gasoline"], t, {"products"}, "USD/gal")
                dsl = find_input(i["diesel"], t, {"products"}, "USD/gal")
                ins = (gas, dsl, crude)
            else:
                ins = (find_input(i["product"], t, {"products"}, "USD/gal"), crude)
            if any(len(x) != 1 for x in ins):
                notes.append(f"{rid}: its inputs are not one row each: {ins}")
                continue
            ss = [dict(series(x[0])) for x in ins]
            for d, v in file.items():
                if all(d in s for s in ss):
                    mine = (2 * ss[0][d] + ss[1][d]) * 42 / 3 - ss[2][d] if len(ss) == 3 else ss[0][d] * 42 - ss[1][d]
                    g.add("crack", mine, v, rid, tol=2 * TOL)
                else:
                    g.add("crack: a day an input lacks", 0.0, 1.0, rid, tol=0)
            notes.append(f"{rid}: inputs {', '.join(x[0] for x in ins)}")
        elif grp in ("da_rt",) or rid.endswith("-da-minus-rt"):
            base = rid[: -len("-da-minus-rt")]
            da, rt = dict(series(base + "-da") or []), dict(series(base + "-rt") or [])
            for d, v in file.items():
                if d in da and d in rt:
                    g.add("day-ahead minus real time", da[d] - rt[d], v, rid, tol=2 * TOL)
                else:
                    g.add("da less rt: a day an input lacks", 0.0, 1.0, rid, tol=0)
        elif rid == "erw-brent-minus-wti" or (r.get("formula") and "Brent" in r["label"] and "WTI" in r["label"]):
            br, wt = dict(series("eia-brent-spot") or []), dict(series("eia-wti-cushing-spot") or [])
            for d, v in file.items():
                if d in br and d in wt:
                    g.add("Brent less WTI", br[d] - wt[d], v, rid, tol=2 * TOL)
            notes.append(f"{rid}: Brent less WTI restated")
        elif grp == "gasspreads":
            notes.append(f"{rid}: formula {r.get('formula', '')[:120]}")
    for n in notes:
        print("  " + n)
    g.report("Part 3, the spreads from their inputs")


# ---------------------------------------------------------------------------------------------------------------------
# Part 4: the week table, from the hours (trader_view.md: daily measures, then the latest 7 operating days holding each)

def part_week():
    g = Gap()
    hh = dict(series("eia-henry-hub-spot") or [])
    words = []
    for w in B["week"]:
        if w["hub"].startswith(HELD):
            continue
        h = hourly(w["hub"])
        if h is None:
            words.append(f"{w['hub']}: no hourly file")
            continue
        iso = w["hub"].split("-")[0]
        if os.environ.get("WEEK_PEAK") == "5x16":   # trader_view.md's block: weekdays in every grid, CAISO's Saturday off-peak
            iso = "all grids 5x16"
        da, rt = days_of(h, "da"), days_of(h, "rt")
        if da:
            words.append(f"{w['hub']}: the hours' last complete day-ahead day {max(da)}, real time {max(rt) if rt else None}")
        daily = collections.defaultdict(dict)
        for d, hs in da.items():
            vals = [v for *_, v in hs]
            daily["da_mean_usd"][d] = sum(vals) / len(vals)
            pk = [v for _, loc, v in hs if on_peak(loc, iso)]
            off = [v for _, loc, v in hs if not on_peak(loc, iso)]
            if pk:
                daily["da_onpeak_mean_usd"][d] = sum(pk) / len(pk)
            daily["da_offpeak_mean_usd"][d] = sum(off) / len(off)
            gd = next((d - dt.timedelta(days=k) for k in range(0, 5) if d - dt.timedelta(days=k) in hh), None)
            if gd is not None:
                daily["implied_heat_rate"][d] = daily["da_mean_usd"][d] / hh[gd]
        for d, hs in rt.items():
            if d in da:
                dv = {u: v for u, _, v in da[d]}
                diffs = [v - dv[u] for u, _, v in hs if u in dv]
                if len(diffs) == len(hs):
                    daily["da_rt_spread_mean_usd"][d] = sum(v for *_, v in hs) / len(hs) - daily["da_mean_usd"][d]
                    daily["max"][d] = max(diffs)
                    daily["h50"][d] = sum(1 for x in diffs if x > 50)
        for k, m in w.get("means", {}).items():
            s = daily.get(k, {})
            end = day(m["end"])
            ds = sorted(d for d in s if d <= end)[-14:]
            last7, prev7 = ds[-7:], ds[-14:-7]
            if not last7 or last7[-1] != end:
                g.add(f"week {k}: its end held", 0.0, 1.0, w["hub"], tol=0)
                continue
            mine = sum(s[d] for d in last7) / 7
            g.add(f"week {k}: mean, to the cent", mine, m["v"], w["hub"], tol=0.005 + 1e-9)
            g.add(f"week {k}: mean, to 4 decimals", mine, m["v"], w["hub"], tol=TOL)
            span = (last7[-1] - last7[0]).days + 1
            if span != 7:
                words.append(f"{w['hub']} {k}: the 7 values run over {span} calendar days ({last7[0]} to {last7[-1]})")
            if m.get("ch") is not None and len(prev7) == 7:
                g.add(f"week {k}: change on the 7 before", mine - sum(s[d] for d in prev7) / 7, m["ch"], w["hub"], tol=0.01)
        if w.get("max_spread"):
            end = day(w["max_spread"]["end"])
            ds = [d for d in daily["max"] if end - dt.timedelta(days=7) < d <= end]
            if len(ds) == 7:
                g.add("week largest RT minus DA hour", max(daily["max"][d] for d in ds), w["max_spread"]["v"], w["hub"], tol=0.01)
                g.add("week hours RT over DA + 50", float(sum(daily["h50"][d] for d in ds)), w["hours50"]["v"], w["hub"], tol=0)
        if w.get("vol"):
            s = daily["da_mean_usd"]
            end = day(w["vol"]["t"])
            ds = [end - dt.timedelta(days=k) for k in range(30, -1, -1)]
            if all(d in s for d in ds):
                ch = [s[ds[i + 1]] - s[ds[i]] for i in range(30)]
                mu = sum(ch) / 30
                g.add("week 30-day volatility", math.sqrt(sum((c - mu) ** 2 for c in ch) / 29), w["vol"]["v"], w["hub"], tol=0.005)
            else:
                g.add("week 30-day volatility: 31 days held", 0.0, 1.0, w["hub"], tol=0)
            later = [e for e in sorted(s) if e > end]
            ok31 = [e for e in later if all(e - dt.timedelta(days=k) in s for k in range(31))]
            if ok31:
                words.append(f"{w['hub']}: volatility dated {end}, but the hours hold 31 whole days to {ok31[-1]}")
    for x in words[:40]:
        print("  " + x)
    print(f"  ({len(words)} lines of words)")
    g.report("Part 4, the week table from the hours")


if __name__ == "__main__":
    if "rows" in PARTS:
        part_rows()
    if "hours" in PARTS:
        part_hours()
    if "spreads" in PARTS:
        part_spreads()
    if "week" in PARTS:
        part_week()
