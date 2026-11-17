"""Energy Research Warehouse (ERW), session 7531 (chain 304): the replication of /events and its nine event pages.

Written from the method notes (docs/methods/events.md, the tool as a reader meets it, which points to the table's note
docs/methods/event_study.md for the estimates) and the public table event_window_daily alone, not from the pages' code.
Standard library only. Four parts:

1. Every figure the ten pages print, recomputed in the pages' reading order from the rules the notes and the pages'
   own sentences state ("the highest hour of the window", "the deepest weekly drop", "on 2021-02-15"), beside the figure
   the page's own code gives on the same rows (page_figures.json, written by site/scripts/events-pages.mjs, which draws
   each page with the site's own components). A picked figure passes when it is the same row (entity, variable, day,
   event) and its value is within half the page's last shown digit; an estimate passes when ours, from our own
   least-squares fit with the HC1 covariance, is within half the page's last shown digit. The event study table's day
   counts and the lead sentence's days are compared too.
2. The table's comparison rows recomputed from its level rows (each day's value against the mean of its baseline days:
   the same calendar days of 2019 and 2020 for Uri, the same weekday 364 and 728 days earlier for the others; the weekly
   rows of COVID-19 over their seven days), so the percent the pages print is traced to the MW and MWh it is made of.
3. The estimates of the pages beside the table event_study_estimates, which the Python builder wrote (a third
   implementation of the same regression).
4. The pages' sentences that state a fact of the rows ("during the outages net generation stayed above that average",
   "the highest came later"), each checked as true or false on the rows, and CAISO's notices of September 2022 by day
   against caiso_grid_emergencies.

    python replication/events/replicate.py [--tables <dir of the warehouse's CSV tables>] [--write]

Without --tables the replication runs on window_rows.csv and notice_rows.csv beside this file (the rows of the two
public tables the pages read, copied by --write), so it runs on any copy of the repository. --write rewrites those two
files and page_figures.csv (one line a figure: page, key, the page's value, ours, the difference, pass). Exit 0 when
every figure passes, 1 when one does not, 2 on bad input.

The hold (session 7531's held-row fix): event_window_daily and event_study_estimates are "license needed", held by grid
for ISO-NE, MISO and NYISO (site/data/license_status.json). By the site's rule (licenseHeldRow and gridOfEntity in
site/lib/license.ts) a row whose entity is a deciding grid's ("isone:", "miso:", "nyiso:") is held; a row of no grid
("eia930:", "noaa:", "ercot:" is a grid that does not decide) is kept. Held rows are dropped as they are read, so nothing
here is computed from one; held figures of the pages are counted as "held, not recomputed here", never compared; and
--write copies no held row and no held figure into this folder (it writes the count instead, in the files' first line
and in page_figures.json's `heldFigures`). This is a public repository.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
T = "event_window_daily"
Z = 1.959963984540054          # the normal 97.5 percent point (event_study.md, "Inference")
TOL_REL = 1e-9                 # a design column kept when its part not explained by the columns before it is above this share of its length
WINDOWS = {                    # events.md and event_study.md: the event days, local dates inclusive
    "uri_2021": ("2021-02-07", "2021-02-24"), "covid_2020": ("2020-03-01", "2020-05-31"),
    "caiso_heat_2020": ("2020-08-10", "2020-08-24"), "caiso_heat_2022": ("2022-08-31", "2022-09-09"),
    "elliott_2022": ("2022-12-19", "2022-12-29"), "ercot_heat_2023": ("2023-08-01", "2023-09-10"),
    "cold_2025": ("2025-01-17", "2025-01-26"), "east_heat_2025": ("2025-06-20", "2025-06-28"),
    "cold_2026": ("2026-01-23", "2026-02-02"),
}
COVID_AFTER = "2020-03-22"     # the covid page: the first whole week after California's order of 2020-03-19
SIX = ["eia930:PJM", "eia930:MISO", "eia930:SWPP", "eia930:NYIS", "eia930:ISNE", "eia930:ERCO"]
STUDY_SIX = ["eia930:PJM", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:SWPP"]
HUB = "ercot:HB_HUBAVG"
FOUR_HUBS = ["miso:INDIANA.HUB", "nyiso:N.Y.C.", "isone:.H.INTERNAL_HUB", "spp:SPPNORTH_HUB"]
COVID_GRIDS = ["eia930:CISO", "eia930:ERCO", "eia930:ISNE", "eia930:MISO", "eia930:NYIS", "eia930:PJM", "eia930:SWPP", "eia930:US48"]
ENTITY_BA = lambda e: "erco" if e == HUB else e.split(":", 1)[1].lower()
# Each event page as its words describe it (events.md, "What the page reads"; the pages' own sentences). `grids` are the
# grids of the window sections, `hub` ERCOT's hub section, `hubs` the other hubs' section, `study` the event study
# block (its lead grid first in `primary`), `price` whether the block adds ERCOT's hub price.
PAGES = {
    "caiso-heat-2020": dict(event="caiso_heat_2020", grids=["eia930:CISO"], hub=None, hubs=[], study=["eia930:CISO"], primary="eia930:CISO", price=False),
    "caiso-heat-2022": dict(event="caiso_heat_2022", grids=["eia930:CISO"], hub=None, hubs=[], study=["eia930:CISO"], primary="eia930:CISO", price=False),
    "elliott-2022": dict(event="elliott_2022", grids=SIX, hub=HUB, hubs=[], study=STUDY_SIX, primary="eia930:PJM", price=True),
    "ercot-heat-2023": dict(event="ercot_heat_2023", grids=["eia930:ERCO"], hub=HUB, hubs=[], study=["eia930:ERCO"], primary="eia930:ERCO", price=True),
    "cold-2025": dict(event="cold_2025", grids=SIX, hub=HUB, hubs=FOUR_HUBS, study=STUDY_SIX, primary="eia930:PJM", price=True),
    "east-heat-2025": dict(event="east_heat_2025", grids=["eia930:PJM", "eia930:NYIS", "eia930:ISNE", "eia930:MISO"], hub=None,
                           hubs=["nyiso:N.Y.C.", "isone:.H.INTERNAL_HUB", "miso:INDIANA.HUB"], study=["eia930:PJM", "eia930:NYIS", "eia930:ISNE", "eia930:MISO"], primary="eia930:PJM", price=False),
    "cold-2026": dict(event="cold_2026", grids=SIX, hub=HUB, hubs=FOUR_HUBS, study=STUDY_SIX, primary="eia930:PJM", price=True),
}
# The index's nine cards: event, entity, variable, the highest or the lowest, over the window
CARDS = [("uri_2021", HUB, "rt_max", "max"), ("covid_2020", "eia930:US48", "demand_pct_vs_baseline_week", "min"),
         ("caiso_heat_2020", "eia930:CISO", "demand_max_pct_vs_baseline", "max"), ("caiso_heat_2022", "eia930:CISO", "demand_max_mw", "max"),
         ("elliott_2022", "eia930:PJM", "demand_max_mw", "max"), ("ercot_heat_2023", HUB, "rt_max", "max"),
         ("cold_2025", "eia930:PJM", "demand_max_mw", "max"), ("east_heat_2025", "eia930:PJM", "demand_max_mw", "max"),
         ("cold_2026", "eia930:PJM", "demand_max_mw", "max")]
NOTICE_NAMES = {"flex_alert": "Flex Alert", "rmo": "Restricted Maintenance Operations", "eea_watch": "EEA Watch", "eea1": "Energy Emergency Alert 1",
                "eea2": "Energy Emergency Alert 2", "eea3": "Energy Emergency Alert 3", "transmission_emergency": "Transmission Emergency"}
# Differences the script knows of and names (page|key: reason); each is a numbered row of
# docs/reviews/events-faults-2026-11-16.md. Empty when every figure is inside half the last shown digit.
NAMED: dict[str, str] = {}


# ------------------------------------------------------------------------------------------------------------ the hold
LICENSE_FILE = os.path.join(ROOT, "site", "data", "license_status.json")
GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}
GRID_NAMES = set(GRID_PREFIX.values())
ES_TABLE = "event_window_daily"   # an es| key's table (site/components/Num.tsx, KEY_TABLE)
HELD_NOTE = re.compile(r"held, not copied: (\d+)")


def grid_of_entity(entity: str | None) -> str:
    """site/lib/license.ts gridOfEntity: "isone:.H.INTERNAL_HUB" and "iso:isone" are ISO-NE's, "nyiso_queue:1630"
    NYISO's; "" when the entity names no grid ("eia930:NYIS", "noaa:...")."""
    m = re.match(r"^([a-z0-9_-]+):(.*)$", entity or "", re.I | re.S)
    if not m:
        return ""
    head = m.group(1).lower()
    if head in GRID_NAMES:
        return head
    q = re.match(r"^([a-z]+)_(?:load_)?queue$", head)
    if q and q.group(1) in GRID_NAMES:
        return q.group(1)
    if head == "iso" and m.group(2).lower() in GRID_NAMES:
        return m.group(2).lower()
    return ""


class Hold:
    """The site's hold on a table's rows on the day (site/lib/license.ts licenseHeldRow), read from the status file."""

    def __init__(self, path: str = LICENSE_FILE, today: str | None = None):
        with open(path, encoding="utf-8") as f:
            self.tables = json.load(f)["tables"]
        self.today = today or dt.datetime.now(dt.timezone.utc).date().isoformat()

    def row(self, table: str, entity: str | None) -> bool:
        r = self.tables.get(table)
        if not r or r.get("status") != "license needed" or self.today < r.get("from", ""):
            return False
        if r.get("hold") == "row":
            return False   # a table held by row is read for its public rows only; none of the replication's tables is one
        who = r.get("publishers", [])
        if not (who and all(p in GRID_PREFIX for p in who)):
            return True    # held whole
        g = grid_of_entity(entity)
        return bool(g) and any(GRID_PREFIX[p] == g for p in who)

    def key(self, check: str) -> bool:
        """A page figure held: the figure of a held row, judged by the row rule on the key's entity (series|<table>|
        <entity>|... and es|<event>|<entity>|..., whose table is event_window_daily). A figure of no grid's entity is
        kept, as its row is."""
        p = check.split("|")
        table = p[1] if p[0].startswith("series") and len(p) > 2 else ES_TABLE if p[0] == "es" and len(p) > 2 else ""
        return bool(table) and self.row(table, p[2])


def held_note(path: str) -> int:
    """The count of held rows a copy beside this file says it left out (its first line, written by --write)."""
    try:
        with open(path, encoding="utf-8") as f:
            m = HELD_NOTE.search(f.readline())
        return int(m.group(1)) if m else 0
    except OSError:
        return 0


# ---------------------------------------------------------------------------------------------------------------- rows
def read_csv(path: str) -> tuple[list[dict], str]:
    stamp, lines = "", []
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if line.startswith("#"):
                m = re.match(r"# Retrieved: (\S+)", line)
                if m and not stamp:
                    stamp = m.group(1)
                continue
            lines.append(line)
    return list(csv.DictReader(lines)), stamp


class Rows:
    """event_window_daily as {event: [row]}, each row {entity, variable, d (YYYY-MM-DD), ts, value, freq, ba}."""

    def __init__(self, raw: list[dict]):
        self.by_event: dict[str, list[dict]] = defaultdict(list)
        for r in raw:
            self.by_event[r["event"]].append({"entity": r["entity"], "variable": r["variable"], "ts": r["ts_utc"], "d": r["ts_utc"][:10],
                                              "value": float(r["value"]), "freq": r.get("freq", ""), "ba": r.get("ba", "")})
        for ev in self.by_event:
            self.by_event[ev].sort(key=lambda r: (r["entity"], r["variable"], r["ts"]))

    def of(self, event, entity=None, variable=None):
        return [r for r in self.by_event.get(event, []) if (entity is None or r["entity"] == entity) and (variable is None or r["variable"] == variable)]

    def at(self, event, entity, variable, d):
        return next((r for r in self.of(event, entity, variable) if r["d"] == d), None)

    def pick(self, event, entity, variable, how, keep):
        """The highest or the lowest row whose day passes `keep`, the first of equal values in day order."""
        best = None
        for r in self.of(event, entity, variable):
            if not keep(r["d"]):
                continue
            if best is None or (r["value"] > best["value"] if how == "max" else r["value"] < best["value"]):
                best = r
        return best


def key_of(r: dict, event: str) -> str:
    return f"series|{T}|{r['entity']}|{r['variable']}|{r['ts']}|{event}"


# ------------------------------------------------------------------------------------------------------- least squares
def dow(d: str) -> int:
    return dt.date.fromisoformat(d).weekday()  # Monday 0


def design(dates, event, years_base, pooled, Zx=None):
    """The regressors of event_study.md, "Specification": intercept, [the window indicator], six weekday indicators
    (Monday the reference), the baseline years coded to sum to zero (the event days take none), [the weather terms]."""
    names = ["intercept"] + (["pooled"] if pooled else []) + [f"dow{k}" for k in range(1, 7)]
    contrast = years_base[:-1] if len(years_base) >= 2 else []
    names += [f"year{y}" for y in contrast]
    if Zx:
        names += [f"z{j}" for j in range(len(Zx[0]))]
    last = years_base[-1] if years_base else None
    X = []
    for i, d in enumerate(dates):
        yr, w = int(d[:4]), dow(d)
        row = [1.0]
        if pooled:
            row.append(1.0 if event[i] else 0.0)
        row += [1.0 if w == k else 0.0 for k in range(1, 7)]
        for y in contrast:
            row.append(0.0 if event[i] else (1.0 if yr == y else 0.0) - (1.0 if yr == last else 0.0))
        if Zx:
            row += list(Zx[i])
        X.append(row)
    return X, names


def keep_columns(X, names):
    """Drop a column that is all zero or a linear combination of the columns kept before it (event_study.md: greedy
    Gram-Schmidt in column order, relative tolerance 1e-9)."""
    keep, basis = [], []
    for j in range(len(names)):
        v = [r[j] for r in X]
        norm = math.sqrt(sum(x * x for x in v))
        if norm == 0:
            continue
        r = v[:]
        for q in basis:
            c = sum(a * b for a, b in zip(q, r))
            r = [x - c * y for x, y in zip(r, q)]
        rn = math.sqrt(sum(x * x for x in r))
        if rn > TOL_REL * norm:
            keep.append(j)
            basis.append([x / rn for x in r])
    return [[row[j] for j in keep] for row in X], [names[j] for j in keep], keep


def invert(A):
    n = len(A)
    M = [list(map(float, A[i])) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        if abs(piv) < 1e-12:
            raise ValueError("singular design")
        M[c] = [x / piv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [row[n:] for row in M]


def ols_hc1(X, y):
    n, k = len(X), len(X[0])
    xtx = [[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)]
    xi = invert(xtx)
    xty = [sum(r[i] * yy for r, yy in zip(X, y)) for i in range(k)]
    b = [sum(xi[i][j] * xty[j] for j in range(k)) for i in range(k)]
    e = [yy - sum(a * bb for a, bb in zip(r, b)) for r, yy in zip(X, y)]
    meat = [[sum(r[i] * r[j] * ee * ee for r, ee in zip(X, e)) for j in range(k)] for i in range(k)]
    mul = lambda P, Q: [[sum(P[i][m] * Q[m][j] for m in range(len(Q))) for j in range(len(Q[0]))] for i in range(len(P))]
    V = [[v * n / (n - k) for v in row] for row in mul(mul(xi, meat), xi)]
    s2 = sum(ee * ee for ee in e) / (n - k)
    return b, V, s2


def study(dates, y, event, Zx=None):
    """Each event day's effect (its value less the baseline-only fit, se sqrt(s2 + x'Vx)) and the pooled effect (the
    window indicator's coefficient, HC1), as event_study.md defines them."""
    years_base = sorted({int(d[:4]) for d, e in zip(dates, event) if not e})
    X, names = design(dates, event, years_base, False, Zx)
    Xb, _, keep = keep_columns([r for r, e in zip(X, event) if not e], names)
    b, V, s2 = ols_hc1(Xb, [v for v, e in zip(y, event) if not e])
    days = []
    for r, d, v, e in zip(X, dates, y, event):
        if not e:
            continue
        x = [r[j] for j in keep]
        cf = sum(a * bb for a, bb in zip(x, b))
        q = sum(x[i] * sum(V[i][j] * x[j] for j in range(len(x))) for i in range(len(x)))
        se = math.sqrt(s2 + q)
        days.append({"day": d, "est": v - cf, "lo": v - cf - Z * se, "hi": v - cf + Z * se, "cf": cf})
    Xp, names_p = design(dates, event, years_base, True, Zx)
    Xp, names_p, _ = keep_columns(Xp, names_p)
    bp, Vp, _ = ols_hc1(Xp, y)
    j = names_p.index("pooled")
    se = math.sqrt(Vp[j][j])
    return {"days": days, "est": bp[j], "lo": bp[j] - Z * se, "hi": bp[j] + Z * se, "cf": sum(d["cf"] for d in days) / len(days), "n": len(y)}


def series_study(rows: Rows, event, entity, variable, weather=None):
    lo, hi = WINDOWS[event]
    xs = [r for r in rows.of(event, entity, variable) if r["freq"] in ("", "P1D")]
    xs.sort(key=lambda r: r["d"])
    if weather is not None:
        xs = [r for r in xs if r["d"] in weather]
    dates = [r["d"] for r in xs]
    Zx = [[weather[d][0], weather[d][0] ** 2, weather[d][1], weather[d][1] ** 2] for d in dates] if weather is not None else None
    return study(dates, [r["value"] for r in xs], [lo <= d <= hi for d in dates], Zx)


def grid_weather(rows: Rows, event, ba):
    """The grid's degree days by local day: the mean over the event's station rows whose ba is the grid's
    (event_study.md, "Temperature-controlled specification"); a day needs both hdd_65f and cdd_65f."""
    h, c = defaultdict(list), defaultdict(list)
    for r in rows.of(event):
        if not r["entity"].startswith("noaa:") or r["ba"] != ba:
            continue
        if r["variable"] == "hdd_65f":
            h[r["d"]].append(r["value"])
        elif r["variable"] == "cdd_65f":
            c[r["d"]].append(r["value"])
    return {d: (sum(h[d]) / len(h[d]), sum(c[d]) / len(c[d])) for d in h if d in c}


# ------------------------------------------------------------------------------------------------- the pages' figures
class Expect:
    """The figures one page should print, in its reading order: (key, value)."""

    def __init__(self):
        self.items: list[tuple[str, float]] = []

    def row(self, r, event):
        if r is not None:
            self.items.append((key_of(r, event), r["value"]))

    def es(self, event, entity, variable, term, field, v):
        self.items.append((f"es|{event}|{entity}|{variable}|{term}|{field}", v))


def expect_study(x: Expect, rows: Rows, event, grids, primary, price, counts):
    want = [(g, "demand_mwh") for g in grids] + ([(HUB, "rt_mean")] if price else [])
    res = []
    for entity, variable in want:
        s = series_study(rows, event, entity, variable)
        w = grid_weather(rows, event, ENTITY_BA(entity))
        t = series_study(rows, event, entity, variable, w) if w else None
        res.append((entity, variable, s, t))
    lead = next(r for r in res if r[0] == primary and r[1] == "demand_mwh")
    e, v, s, t = lead
    x.es(event, e, v, "pooled", "est", s["est"]); x.es(event, e, v, "pooled", "lo", s["lo"]); x.es(event, e, v, "pooled", "hi", s["hi"])
    x.es(event, e, v, "pooled", "pct", s["est"] / s["cf"] * 100); x.es(event, e, v, "pooled", "cf", s["cf"])
    if t:
        x.es(event, e, v, "pooled_temp", "est", t["est"]); x.es(event, e, v, "pooled_temp", "lo", t["lo"]); x.es(event, e, v, "pooled_temp", "hi", t["hi"])
        if math.copysign(1, t["est"]) == math.copysign(1, s["est"]) and abs(t["est"]) <= abs(s["est"]):
            x.es(event, e, v, "weather_share", "pct", (1 - t["est"] / s["est"]) * 100)
    for entity, variable, s2, t2 in res:
        x.es(event, entity, variable, "pooled", "est", s2["est"]); x.es(event, entity, variable, "pooled", "lo", s2["lo"]); x.es(event, entity, variable, "pooled", "hi", s2["hi"])
        x.es(event, entity, variable, "pooled", "pct", s2["est"] / s2["cf"] * 100)
        if t2:
            x.es(event, entity, variable, "pooled_temp", "est", t2["est"]); x.es(event, entity, variable, "pooled_temp", "lo", t2["lo"]); x.es(event, entity, variable, "pooled_temp", "hi", t2["hi"])
        counts.append((event, entity, variable, s2["n"]))
    for d in s["days"]:
        x.es(event, e, v, f"day|{d['day']}", "est", d["est"]); x.es(event, e, v, f"day|{d['day']}", "lo", d["lo"]); x.es(event, e, v, f"day|{d['day']}", "hi", d["hi"])
    return res, len(s["days"])


def expect_window(x: Expect, rows: Rows, slug, p, after):
    ev = p["event"]
    lo, hi = WINDOWS[ev]
    inw = lambda d: lo <= d <= hi
    after(x, rows, ev, inw)
    for g in p["grids"]:
        h = rows.pick(ev, g, "demand_max_pct_vs_baseline", "max", inw)
        x.row(h, ev)
        x.row(rows.at(ev, g, "demand_max_mw", h["d"]) if h else None, ev)
        x.row(rows.pick(ev, g, "demand_max_mw", "max", inw), ev)
        x.row(rows.pick(ev, g, "intensity_generation", "max", inw), ev)
    if p["hub"]:
        for var in ("rt_max", "rt_mean", "da_max"):
            x.row(rows.pick(ev, p["hub"], var, "max", inw), ev)
    for h in p["hubs"]:
        for var in ("rt_max", "rt_mean", "da_max"):
            x.row(rows.pick(ev, h, var, "max", inw), ev)


# Each page's own sentence under its first chart ("after"), in its order, as its words name the figures
def after_caiso2020(x, rows, ev, inw):
    E = "eia930:CISO"
    x.row(rows.at(ev, E, "demand_max_pct_vs_baseline", "2020-08-14"), ev); x.row(rows.at(ev, E, "demand_max_pct_vs_baseline", "2020-08-15"), ev)
    x.row(rows.pick(ev, E, "demand_max_pct_vs_baseline", "max", inw), ev)


def after_caiso2022(x, rows, ev, inw):
    E = "eia930:CISO"
    x.row(rows.pick(ev, E, "demand_max_mw", "max", inw), ev); x.row(rows.pick(ev, E, "demand_max_pct_vs_baseline", "max", inw), ev)
    x.row(rows.at(ev, E, "demand_max_pct_vs_baseline", "2022-09-06"), ev)


def after_elliott(x, rows, ev, inw):
    x.row(rows.pick(ev, "eia930:PJM", "demand_max_mw", "max", inw), ev); x.row(rows.pick(ev, "eia930:ISNE", "demand_max_pct_vs_baseline", "max", inw), ev)
    x.row(rows.pick(ev, "eia930:SWPP", "demand_max_mw", "max", inw), ev); x.row(rows.at(ev, "eia930:SWPP", "demand_max_mw", "2022-12-23"), ev)


def after_ercot2023(x, rows, ev, inw):
    x.row(rows.at(ev, "eia930:ERCO", "demand_max_mw", "2023-09-06"), ev); x.row(rows.pick(ev, "eia930:ERCO", "demand_max_mw", "max", inw), ev)
    x.row(rows.pick(ev, HUB, "rt_max", "max", inw), ev)


def after_cold2025(x, rows, ev, inw):
    x.row(rows.pick(ev, "eia930:PJM", "demand_max_mw", "max", inw), ev); x.row(rows.pick(ev, "eia930:MISO", "demand_max_mw", "max", inw), ev)
    x.row(rows.pick(ev, "eia930:PJM", "demand_max_pct_vs_baseline", "max", inw), ev)


def after_east2025(x, rows, ev, inw):
    x.row(rows.pick(ev, "eia930:PJM", "demand_max_mw", "max", inw), ev); x.row(rows.pick(ev, "eia930:NYIS", "demand_max_pct_vs_baseline", "max", inw), ev)
    x.row(rows.pick(ev, "eia930:ISNE", "demand_max_pct_vs_baseline", "max", inw), ev)


def after_cold2026(x, rows, ev, inw):
    x.row(rows.pick(ev, "eia930:PJM", "demand_max_mw", "max", inw), ev); x.row(rows.pick(ev, "eia930:ERCO", "demand_max_mw", "max", inw), ev)
    x.row(rows.pick(ev, "eia930:PJM", "demand_max_pct_vs_baseline", "max", inw), ev)


AFTER = {"caiso-heat-2020": after_caiso2020, "caiso-heat-2022": after_caiso2022, "elliott-2022": after_elliott, "ercot-heat-2023": after_ercot2023,
         "cold-2025": after_cold2025, "east-heat-2025": after_east2025, "cold-2026": after_cold2026}


def expect_all(rows: Rows):
    out, counts, leads = {}, {}, {}
    x = Expect()
    for ev, ent, var, how in CARDS:
        # the COVID-19 card reads from the week of 2020-03-22 on, as its event page does (session 7531, fault 3)
        lo, hi = (COVID_AFTER, WINDOWS[ev][1]) if ev == "covid_2020" else WINDOWS[ev]
        x.row(rows.pick(ev, ent, var, how, lambda d: lo <= d <= hi), ev)
    out["index"] = x.items
    # Uri: the event year against 2019 and 2020 on the same calendar days (events.md, "The first event")
    x, c = Expect(), []
    ev = "uri_2021"
    y21 = lambda d: d.startswith("2021")
    yb = lambda d: d[:4] in ("2019", "2020")
    x.row(rows.pick(ev, HUB, "rt_max", "max", y21), ev); x.row(rows.pick(ev, HUB, "rt_max", "max", yb), ev)
    x.row(rows.pick(ev, "eia930:ERCO", "demand_min_mw", "min", y21), ev); x.row(rows.at(ev, "eia930:ERCO", "demand_min_mw", "2021-02-15"), ev)
    x.row(rows.pick(ev, "eia930:ERCO", "net_generation_mwh_day_change", "min", y21), ev)
    x.row(rows.pick(ev, "eia930:ERCO", "net_generation_mwh_vs_baseline", "min", y21), ev)
    x.row(rows.pick(ev, "eia930:ERCO", "intensity_generation", "max", y21), ev)
    _, leads["uri-2021"] = expect_study(x, rows, ev, ["eia930:ERCO"], "eia930:ERCO", True, c)
    out["uri-2021"], counts["uri-2021"] = x.items, c
    # COVID-19: each grid's deepest weekly drop, and the deepest from the week of 2020-03-22 on when its week differs
    x, c = Expect(), []
    ev = "covid_2020"
    for g in COVID_GRIDS:
        deep = rows.pick(ev, g, "demand_pct_vs_baseline_week", "min", lambda d: True)
        after = rows.pick(ev, g, "demand_pct_vs_baseline_week", "min", lambda d: d >= COVID_AFTER)
        x.row(deep, ev)
        if deep and after and deep["d"] != after["d"]:
            x.row(after, ev)
    # the block's table lists the Lower 48 first, then the seven grids in the order of the window sections
    _, leads["covid-2020"] = expect_study(x, rows, ev, ["eia930:US48"] + COVID_GRIDS[:-1], "eia930:US48", True, c)
    out["covid-2020"], counts["covid-2020"] = x.items, c
    for slug, p in PAGES.items():
        x, c = Expect(), []
        expect_window(x, rows, slug, p, AFTER[slug])
        _, leads[slug] = expect_study(x, rows, p["event"], p["study"], p["primary"], p["price"], c)
        out[slug], counts[slug] = x.items, c
    return out, counts, leads


def half_digit(shown: str) -> float:
    s = shown.replace(",", "").strip()
    return 0.5 * 10 ** -len(s.split(".")[1]) if "." in s else 0.5


# -------------------------------------------------------------------------------------- part 2: the comparison rows
def baseline_days(event: str, d: str) -> list[str]:
    day = dt.date.fromisoformat(d)
    if event == "uri_2021":  # the same calendar days of 2019 and 2020
        return [day.replace(year=2019).isoformat(), day.replace(year=2020).isoformat()]
    return [(day - dt.timedelta(days=364)).isoformat(), (day - dt.timedelta(days=728)).isoformat()]


def check_comparisons(rows: Rows):
    """Each *_vs_baseline row recomputed from the level rows of its day and its held baseline days."""
    level = {"demand_mwh_vs_baseline": ("demand_mwh", "mwh"), "demand_pct_vs_baseline": ("demand_mwh", "pct"),
             "demand_max_mw_vs_baseline": ("demand_max_mw", "mwh"), "demand_max_pct_vs_baseline": ("demand_max_mw", "pct"),
             "net_generation_mwh_vs_baseline": ("net_generation_mwh", "mwh")}
    n = bad = 0
    misses = []
    for ev, rs in rows.by_event.items():
        idx = {(r["entity"], r["variable"], r["d"]): r["value"] for r in rs if r["freq"] in ("", "P1D")}
        for r in rs:
            if r["variable"] in level and r["freq"] in ("", "P1D"):
                src, kind = level[r["variable"]]
                base = [idx[(r["entity"], src, b)] for b in baseline_days(ev, r["d"]) if (r["entity"], src, b) in idx]
                day = idx.get((r["entity"], src, r["d"]))
                if not base or day is None:
                    misses.append((ev, r["entity"], r["variable"], r["d"], "no level rows")); bad += 1; n += 1
                    continue
                m = sum(base) / len(base)
                ours = day - m if kind == "mwh" else (day / m - 1) * 100
                n += 1
                if abs(ours - r["value"]) > max(0.006, 1e-6 * abs(r["value"])):
                    bad += 1; misses.append((ev, r["entity"], r["variable"], r["d"], f"table {r['value']} ours {ours:.4f}"))
            elif r["variable"] in ("demand_mwh_vs_baseline_week", "demand_pct_vs_baseline_week"):
                start = dt.date.fromisoformat(r["d"])
                days = [(start + dt.timedelta(days=i)).isoformat() for i in range(7)]
                cur = [idx.get((r["entity"], "demand_mwh", d)) for d in days]
                base = []
                for d in days:
                    bs = [idx.get((r["entity"], "demand_mwh", b)) for b in baseline_days(ev, d)]
                    base.append([b for b in bs if b is not None])
                n += 1
                if None in cur or any(not b for b in base):
                    bad += 1; misses.append((ev, r["entity"], r["variable"], r["d"], "a day of the week not held")); continue
                # the week's baseline is the sum over its seven days of each day's held baseline mean
                bsum = sum(sum(b) / len(b) for b in base)
                ours = sum(cur) - bsum if r["variable"].startswith("demand_mwh") else (sum(cur) / bsum - 1) * 100
                if abs(ours - r["value"]) > max(0.006, 1e-6 * abs(r["value"])):
                    bad += 1; misses.append((ev, r["entity"], r["variable"], r["d"], f"table {r['value']} ours {ours:.4f}"))
            elif r["variable"] in ("demand_mwh_day_change", "net_generation_mwh_day_change"):
                src = r["variable"].replace("_day_change", "")
                prev = (dt.date.fromisoformat(r["d"]) - dt.timedelta(days=1)).isoformat()
                a, b = idx.get((r["entity"], src, r["d"])), idx.get((r["entity"], src, prev))
                n += 1
                if a is None or b is None or abs((a - b) - r["value"]) > 0.006:
                    bad += 1; misses.append((ev, r["entity"], r["variable"], r["d"], f"table {r['value']}"))
    return n, bad, misses


# --------------------------------------------------------------------------------------- part 3: the builder's table
def check_builder(est_rows: list[dict], rows: Rows):
    """The pooled estimates of each event, grid and outcome against event_study_estimates (x_spec dow_year_mean_v1 and
    dow_year_temp_v1), the field est, lo and hi, relative 1e-6 or 0.001 absolute. `est_rows` comes with its held rows
    already dropped (main), as `rows` does."""
    want = {}
    for r in est_rows:
        m = re.match(r"(demand_mwh|rt_mean)_effect_pooled(_temp)?$", r["variable"])
        if m:
            want[(r["event"], r["entity"], m.group(1), bool(m.group(2)))] = (float(r["value"]), float(r["x_ci_low"]), float(r["x_ci_high"]))
    n = bad = 0
    misses = []
    for (ev, ent, var, temp), (v, lo, hi) in sorted(want.items()):
        if ev not in WINDOWS:
            continue
        w = grid_weather(rows, ev, ENTITY_BA(ent)) if temp else None
        if temp and not w:
            continue
        s = series_study(rows, ev, ent, var, w)
        for a, b in ((s["est"], v), (s["lo"], lo), (s["hi"], hi)):
            n += 1
            if abs(a - b) > max(1e-3, 1e-6 * abs(b)):
                bad += 1; misses.append((ev, ent, var, temp, a, b))
    return n, bad, misses


# ----------------------------------------------------------------------------------- part 4: the pages' sentences
def statements(rows: Rows, notices: list[dict], texts: dict[str, str]):
    """Each sentence of the pages that states a fact of the rows: (page, the words, true or false, what the rows say)."""
    out = []
    g = lambda ev, e, v, d: rows.at(ev, e, v, d)
    # Uri
    ev = "uri_2021"
    low = rows.pick(ev, "eia930:ERCO", "demand_min_mw", "min", lambda d: d.startswith("2021"))
    out.append(("uri-2021", "Lowest hour of demand served in the window ... after the storm", low["d"] > "2021-02-20", f"{low['value']:.0f} MW on {low['d']}"))
    outage = [g(ev, "eia930:ERCO", "net_generation_mwh_vs_baseline", f"2021-02-{d}") for d in ("15", "16", "17", "18")]
    out.append(("uri-2021", "during the outages [15 to 18 February] net generation stayed above that average", all(r and r["value"] > 0 for r in outage),
                ", ".join(f"{r['d']} {r['value']:+,.1f}" for r in outage if r)))
    above = [g(ev, "eia930:ERCO", "demand_mwh_vs_baseline", f"2021-02-{d:02d}") for d in range(9, 21)]
    out.append(("uri-2021 (events.md)", "Demand served stayed above the 2019 and 2020 baseline on every day from 2021-02-09 to 2021-02-20", all(r and r["value"] > 0 for r in above),
                f"{sum(1 for r in above if r and r['value'] > 0)} of 12 days above"))
    # CAISO 2020
    ev = "caiso_heat_2020"
    hi = rows.pick(ev, "eia930:CISO", "demand_max_pct_vs_baseline", "max", lambda d: "2020-08-10" <= d <= "2020-08-24")
    out.append(("caiso-heat-2020", "Not on the outage days ... the highest came later", hi["d"] > "2020-08-15", f"{hi['value']:.2f} percent on {hi['d']}"))
    # Elliott
    ev = "elliott_2022"
    inw = lambda d: "2022-12-19" <= d <= "2022-12-29"
    pjm = rows.pick(ev, "eia930:PJM", "demand_max_mw", "max", inw)
    out.append(("elliott-2022", "PJM's highest hour in EIA's data agrees with the report's \"about 136,000 MW\" on Dec. 23", pjm["d"] == "2022-12-23" and abs(pjm["value"] - 136000) / 136000 < 0.01,
                f"{pjm['value']:,.0f} MW on {pjm['d']}, {100 * (pjm['value'] / 136000 - 1):+.2f} percent"))
    spp = rows.pick(ev, "eia930:SWPP", "demand_max_mw", "max", inw)
    out.append(("elliott-2022", "SPP's highest hour of the window is on 2022-12-22 (00:00 UTC on Dec. 23)", spp["d"] == "2022-12-22", f"{spp['value']:,.0f} MW on {spp['d']}"))
    ne = rows.pick(ev, "eia930:ISNE", "demand_max_pct_vs_baseline", "max", inw)
    mx = max(rows.pick(ev, e, "demand_max_pct_vs_baseline", "max", inw)["value"] for e in SIX)
    out.append(("elliott-2022", "ISO-NE barely moved (the least of the six grids against the baseline)", all(rows.pick(ev, e, "demand_max_pct_vs_baseline", "max", inw)["value"] >= ne["value"] for e in SIX),
                f"ISO-NE at most {ne['value']:.2f} percent; the six at most {mx:.2f}"))
    # ERCOT 2023
    ev = "ercot_heat_2023"
    inw = lambda d: "2023-08-01" <= d <= "2023-09-10"
    top = rows.pick(ev, "eia930:ERCO", "demand_max_mw", "max", inw)
    rt = rows.pick(ev, HUB, "rt_max", "max", inw)
    out.append(("ercot-heat-2023", "The emergency [2023-09-06] did not come on the day of the highest demand", top["d"] != "2023-09-06", f"highest hour {top['value']:,.0f} MW on {top['d']}"))
    out.append(("ercot-heat-2023", "The price tells the emergency: the highest 15-minute real-time price of the window came on the emergency's day", rt["d"] == "2023-09-06", f"{rt['value']:,.2f} USD/MWh on {rt['d']}"))
    d6 = g(ev, "eia930:ERCO", "demand_max_mw", "2023-09-06")
    out.append(("ercot-heat-2023", "On 2023-09-06 EIA's highest hour was ... beside the 82,705 MW ERCOT announced that evening as its September record (events.md: 13 MW under it)", abs(d6["value"] - 82705) <= 13,
                f"{d6['value']:,.0f} MW, {d6['value'] - 82705:+,.0f} MW"))
    # session 7531, fault 4: ERCOT's release of 14 September 2023 raised the September record twice inside the window
    d7, d8 = g(ev, "eia930:ERCO", "demand_max_mw", "2023-09-07"), g(ev, "eia930:ERCO", "demand_max_mw", "2023-09-08")
    out.append(("ercot-heat-2023", "ERCOT's later September records (83,911 MW on 7 September, 84,182 MW on 8 September) stand above the 82,705 MW of 6 September in EIA's hours too",
                d7["value"] > d6["value"] and d8["value"] > d7["value"], f"EIA {d7['value']:,.0f} MW on 7 September, {d8['value']:,.0f} MW on 8 September"))
    # The pages chosen from the data: the highest hour of each grid inside the window on the days the framing names
    def peak_days(ev, lo, hi, named):
        inw = lambda d: lo <= d <= hi
        got = {e: rows.pick(ev, e, "demand_max_mw", "max", inw)["d"] for e in named}
        return all(got[e] in named[e] for e in named), "; ".join(f"{e.split(':')[1]} {got[e]}" for e in named)
    ok, why = peak_days("cold_2025", "2025-01-17", "2025-01-26", {e: ("2025-01-21", "2025-01-22") for e in ("eia930:PJM", "eia930:MISO", "eia930:NYIS", "eia930:ISNE")})
    out.append(("cold-2025", "PJM, MISO, NYISO and ISO-NE each served their highest winter hour of demand on January 21 or 22, 2025 (inside the window)", ok, why))
    ok, why = peak_days("east_heat_2025", "2025-06-20", "2025-06-28", {e: ("2025-06-23", "2025-06-24") for e in ("eia930:PJM", "eia930:NYIS", "eia930:ISNE")})
    out.append(("east-heat-2025", "PJM, NYISO and ISO-NE each served their highest hour of demand on June 23 or 24, 2025 (inside the window)", ok, why))
    ok, why = peak_days("cold_2026", "2026-01-23", "2026-02-02", {"eia930:ERCO": ("2026-01-26",), "eia930:SWPP": ("2026-01-26",), "eia930:ISNE": ("2026-01-25",),
                                                                   "eia930:MISO": ("2026-01-27",), "eia930:PJM": ("2026-01-29",)})
    out.append(("cold-2026", "ERCOT and SPP on 26 January 2026, ISO-NE on 25 January, MISO on 27 January and PJM on 29 January (inside the window)", ok, why))
    # CAISO's notices of September 2022, by day, against the page's list
    days = defaultdict(list)
    for n in notices:
        d = n["event_date"][:10]
        if "2022-08-31" <= d <= "2022-09-09" and n["event_type"] not in days[d]:
            days[d].append(n["event_type"])
    page = texts.get("caiso-heat-2022", "")
    listed = {m.group(1): set(m.group(2).split(", ")) for m in re.finditer(r"^(\d{4}-\d\d-\d\d) ?: (.+)$", page, re.M)
              if "|" not in m.group(2)}
    shown = (listed == {d: {NOTICE_NAMES.get(t, t) for t in ts} for d, ts in days.items()}) if page else None
    out.append(("caiso-heat-2022", "CAISO's notices, day by day (each day and its types as caiso_grid_emergencies holds them)", shown,
                f"{len(days)} days: " + "; ".join(f"{d} {'+'.join(ts)}" for d, ts in sorted(days.items()))))
    return out


# ---------------------------------------------------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tables", help="the folder of the warehouse's CSV tables (event_window_daily.csv, event_study_estimates.csv, caiso_grid_emergencies.csv)")
    ap.add_argument("--figures", default=os.path.join(HERE, "page_figures.json"))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.tables:
            raw, stamp = read_csv(os.path.join(a.tables, T + ".csv"))
            notices, nstamp = read_csv(os.path.join(a.tables, "caiso_grid_emergencies.csv"))
            est_path = os.path.join(a.tables, "event_study_estimates.csv")
            est_rows, estamp = read_csv(est_path) if os.path.exists(est_path) else ([], "")
        else:
            raw, stamp = read_csv(os.path.join(HERE, "window_rows.csv"))
            notices, nstamp = read_csv(os.path.join(HERE, "notice_rows.csv"))
            est_rows, estamp = read_csv(os.path.join(HERE, "estimate_rows.csv"))
        with open(a.figures, encoding="utf-8") as f:
            fig = json.load(f)
        hold = Hold()
    except (OSError, KeyError, ValueError) as e:
        print(f"bad input: {e}", file=sys.stderr)
        return 2
    # the hold: held rows are dropped as they are read; a copy beside this file says how many it left out
    w_path = os.path.join(a.tables, T + ".csv") if a.tables else os.path.join(HERE, "window_rows.csv")
    e_path = os.path.join(a.tables, "event_study_estimates.csv") if a.tables else os.path.join(HERE, "estimate_rows.csv")
    kept = [r for r in raw if not hold.row(T, r["entity"])]
    held_w = len(raw) - len(kept) + (0 if a.tables else held_note(w_path))
    raw = kept
    kept = [r for r in est_rows if not hold.row("event_study_estimates", r["entity"])]
    held_e =len([r for r in est_rows if "_effect_pooled" in r["variable"] and hold.row("event_study_estimates", r["entity"])]) + (0 if a.tables else held_note(e_path))
    est_rows = kept
    rows = Rows(raw)
    print(f"event_window_daily retrieved {stamp or '(the copy beside this file)'}: {len(raw)} rows kept, {held_w} held (license needed, by grid: ISO-NE, MISO, NYISO); "
          f"page figures drawn on the table retrieved {fig['tables'].get(T)}")

    # part 1
    want, counts, leads = expect_all(rows)
    lines, n, bad, held_f = [], 0, 0, 0
    for slug, items in want.items():
        page = fig["pages"][slug]
        got_all = page["figures"]
        got = [g for g in got_all if not hold.key(g["check"])]
        # a held figure is counted, not compared: the page's own count (heldFigures, written by --write) and any held
        # figure still in an older figures file
        held_here = page.get("heldFigures", 0) + len(got_all) - len(got)
        held_f += held_here
        page["figures"], page["heldFigures"] = got, held_here
        items = [(k, v) for k, v in items if not hold.key(k)]
        if len(got) != len(items):
            print(f"  {slug}: the page prints {len(got)} figures, the notes' rules give {len(items)}")
        for i in range(max(len(got), len(items))):
            g = got[i] if i < len(got) else None
            k, v = items[i] if i < len(items) else ("", float("nan"))
            n += 1
            tol = half_digit(g["shown"]) if g else 0.5
            same_key = g is not None and g["check"] == k
            diff = (v - g["raw"]) if g else float("nan")
            ok = same_key and abs(diff) <= tol
            named = NAMED.get(f"{slug}|{k}")
            if not ok and not named:
                bad += 1
                print(f"  MISS {slug} #{i + 1}: page {g['check'] if g else '-'} = {g['shown'] if g else '-'}; ours {k} = {v}")
            lines.append({"page": slug, "n": i + 1, "key": g["check"] if g else k, "page_value": g["raw"] if g else "", "shown": g["shown"] if g else "",
                          "ours": round(v, 6) if v == v else "", "difference": round(diff, 6) if diff == diff else "", "half_last_digit": tol,
                          "pass": "yes" if ok else ("named" if named else "no")})
        # the event study table's days and the lead sentence's days
        if slug in counts:
            st = fig["pages"][slug]["study"]
            page_counts = [(r["event"], r["entity"], r["variable"], r["days"]) for r in st["rows"]]
            n += len(counts[slug]) + 1
            for c in counts[slug]:
                if c not in page_counts:
                    bad += 1; print(f"  MISS {slug}: days {c} not in the page's table {page_counts}")
            if st["leadDays"] != leads[slug]:
                bad += 1; print(f"  MISS {slug}: the lead sentence says {st['leadDays']} days, the window holds {leads[slug]}")
            lines.append({"page": slug, "n": "days", "key": "study table days and lead days", "page_value": json.dumps([c[3] for c in page_counts] + [st["leadDays"]]),
                          "shown": "", "ours": json.dumps([c[3] for c in counts[slug]] + [leads[slug]]), "difference": "", "half_last_digit": "", "pass": "yes"})
    print(f"part 1, the pages' figures: {n - bad} of {n} pass (named {sum(1 for l in lines if l['pass'] == 'named')}); "
          f"held, not recomputed here: {held_f} (figures of ISO-NE's, MISO's and NYISO's rows)")

    # part 2
    n2, bad2, misses2 = check_comparisons(rows)
    print(f"part 2, the table's comparison rows recomputed from its level rows: {n2 - bad2} of {n2}")
    for m in misses2[:20]:
        print("  ", *m)

    # part 3
    if est_rows:
        n3, bad3, misses3 = check_builder(est_rows, rows)
        print(f"part 3, the pooled estimates against event_study_estimates (retrieved {estamp}): {n3 - bad3} of {n3}; "
              f"held, not recomputed here: {held_e} estimates ({3 * held_e} figures)")
        for m in misses3[:20]:
            print("  ", *m)
    else:
        n3 = bad3 = 0
        print("part 3: event_study_estimates not given")

    # part 4
    # the day lists as the page prints them (events-pages.mjs keeps each "YYYY-MM-DD : ..." line in page_figures.json)
    texts = {slug: "\n".join(p.get("lines", [])) for slug, p in fig["pages"].items()}
    st = statements(rows, notices, texts)
    print("part 4, the pages' sentences on the rows:")
    for page, words, ok, why in st:
        print(f"  {'TRUE ' if ok else 'FALSE' if ok is False else 'n/a  '} {page}: {words} [{why}]")

    if a.write:
        # raw and est_rows hold no held row (dropped above); the held figures are out of `fig` and `lines`
        assert not any(hold.row(T, r["entity"]) for r in raw) and not any(hold.row("event_study_estimates", r["entity"]) for r in est_rows)
        assert not any(hold.key(g["check"]) for p in fig["pages"].values() for g in p["figures"]) and not any(hold.key(str(l["key"])) for l in lines)
        why = "license needed, held by grid for ISO-NE, MISO and NYISO: site/data/license_status.json, site/lib/license.ts licenseHeldRow"
        keep = ["entity", "variable", "ts_utc", "value", "freq", "ba", "event"]
        with open(os.path.join(HERE, "window_rows.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# The rows of event_window_daily (public, docs/methods/events.md), copied by replicate.py --write (session 7531); held, not copied: {held_w} rows ({why})\n# Retrieved: {stamp}\n")
            w = csv.writer(f, lineterminator="\n"); w.writerow(keep)
            for r in sorted(raw, key=lambda r: (r["event"], r["entity"], r["variable"], r["ts_utc"])):
                w.writerow([r[k] for k in keep])
        nk = ["event_id", "event_date", "event_type"]
        with open(os.path.join(HERE, "notice_rows.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# The rows of caiso_grid_emergencies of 2022-08-31 to 2022-09-09 (public, CAISO's Grid Emergencies History Report), copied by replicate.py --write\n# Retrieved: {nstamp}\n")
            w = csv.writer(f, lineterminator="\n"); w.writerow(nk)
            for r in notices:
                if "2022-08-31" <= r["event_date"][:10] <= "2022-09-09":
                    w.writerow([r[k] for k in nk])
        ek = ["entity", "variable", "ts_utc", "value", "event", "x_ci_low", "x_ci_high", "x_n", "x_spec"]
        with open(os.path.join(HERE, "estimate_rows.csv"), "w", encoding="utf-8", newline="") as f:
            f.write(f"# The pooled rows of event_study_estimates (public, docs/methods/event_study.md), copied by replicate.py --write; held, not copied: {held_e} rows ({why})\n# Retrieved: {estamp}\n")
            w = csv.writer(f, lineterminator="\n"); w.writerow(ek)
            for r in est_rows:
                if "_effect_pooled" in r["variable"]:
                    w.writerow([r[k] for k in ek])
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(lines[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(lines)
        with open(os.path.join(HERE, "statements.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n"); w.writerow(["page", "words", "true", "the rows"])
            for page, words, ok, rows_say in st:
                w.writerow([page, words, "yes" if ok else "no" if ok is False else "not read", rows_say])
        # the figures file without its held figures, each page's count of them in heldFigures (set in part 1)
        if os.path.abspath(a.figures) == os.path.join(HERE, "page_figures.json"):
            with open(a.figures, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(fig, indent=1, ensure_ascii=False) + "\n")
        print("wrote window_rows.csv, notice_rows.csv, estimate_rows.csv, page_figures.csv, statements.csv and page_figures.json (held rows and figures counted, not copied)")
    return 0 if bad == 0 and bad2 == 0 and bad3 == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
