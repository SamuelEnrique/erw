#!/usr/bin/env python3
"""The daily chart of the Digest (session 232): one fact and its chart every weekday, chosen and drawn by code.

Energy Research Warehouse (ERW). Samuel's ruling of 12 October 2026: the daily chart in the Digest is fully automatic,
a fact and its chart, no approval. No model writes or chooses anything here. Method:
docs/methods/automated_analysis_scanner.md, "The daily chart in the Digest".

Two machines, because the histories are on one and the Digest is written on the other:

  the data machine   after every daily scan (findings_scanner.daily_request: the worker's, and run_data_machine.sh's)
                     the day's CANDIDATES are computed and published: every flag the scanner raised that day, ranked,
                     each with its finding card; then the watch list's changes of the latest period
                     (warehouse/analysis/watch.py), ranked, each as a card of the same form. They go to
                     runs/scanner/<date>/daily_chart.json and to the internal table public.daily_chart_candidates
                     (migration 030), one row a day.
  the runner         warehouse/news/brief.py asks for the day's candidates, chooses one, draws it
                     (card_image.render, 1200 x 880) to docs/digest/charts/<date>.png, keeps what it chose in
                     docs/digest/charts/<date>.json, and writes the section "ERW's Chart of the Day".

The rule, in order:
  1. The day's strongest scanner flag: records and first negative prices first, then by how far past its threshold
     (the flag's strength, in robust standard deviations of the series' own history), ties by the flag's id.
  2. A flag a Digest has already shown is not shown again (docs/digest/charts/*.json is the memory): a monthly record
     stays "fresh" to the scanner for weeks, and the Digest would otherwise print one chart every day.
  3. If the scanner flagged nothing that day, or nothing new: the watch list's largest change of the latest period,
     ranked by the share of the measure's own earlier changes it exceeds (warehouse/analysis/run.py's `change`), ties by
     the change in robust standard deviations; again never one already shown.
  4. If neither: no section, and the reason is logged, as the fun fact does.
Only public-licensed tables: a table whose license in coverage.csv is not public, or that license_status.csv marks
"license needed", is never a candidate; nor is a table or a series of a publisher held by a ruling (HELD: NYISO, SPP).

    python warehouse/analysis/findings/daily_chart.py --candidates --date 2026-10-13 [--no-publish]   # the data machine
    python warehouse/analysis/findings/daily_chart.py --section --date 2026-10-13                      # what brief.py runs
"""

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import findings_common as common  # noqa: E402

CHART_DIR = os.path.join(ROOT, "docs", "digest", "charts")
META_DIR = os.path.join(ROOT, "warehouse", "metadata")
TABLE = "daily_chart_candidates"
HEADING = "## ERW's Chart of the Day"
FIRST = ("record", "negative")          # the rules that come first, whatever their strength
MAX_FLAGS, MAX_WATCH = 25, 12           # the candidates published a day
# Session 267 (the brief of 14 October 2026): a record more than 25 percent past the old one waits a day. It is not
# shown on the run that first sees it; it is kept in docs/digest/charts/held.json and checked again on the next run (a
# later day): if the scan raises it again it may be shown then. A jump that large is as often a unit, a revision or a
# missing month as a record (13 October 2026 showed one 34 percent past the old record, 7 October's proof one 103).
RECORD_JUMP = 0.25
HELD_FILE = "held.json"
WATCH_MAX_AGE = {"week": 14, "month": 100}   # days since the period ended: older is not "the latest period"
# Roadmap, Rulings, 12 October 2026: "NYISO and SPP tables stay held until their licenses are answered." Their tables and
# their series in consolidated tables are never the Digest's chart until a person removes them from this line.
HELD = ("nyiso", "spp")
DEFAULT_WAIT = 420                      # seconds the Digest waits for today's candidates before using yesterday's
METHOD = "docs/methods/automated_analysis_scanner.md"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Plain names for the series that flag most often. A code that is not here is shown as the table writes it: a wrong
# name would be worse than a code. The exact series key is always printed beside the fact.
STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
          "DE": "Delaware", "DC": "the District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
          "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
          "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
          "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
          "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
          "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
          "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "US": "the United States",
          "NEW": "New England", "MAT": "the Middle Atlantic", "ENC": "the East North Central states", "WNC": "the West North Central states",
          "SAT": "the South Atlantic", "ESC": "the East South Central states", "WSC": "the West South Central states", "MTN": "the Mountain states",
          "PACC": "the Pacific contiguous states", "PACN": "the Pacific noncontiguous states"}
FUELS = {"ALL": "all fuels", "NG": "natural gas", "COW": "coal", "NUC": "nuclear", "HYC": "conventional hydro", "WND": "wind", "SUN": "solar",
         "GEO": "geothermal", "OOG": "other gases"}
SECTORS = {"ALL": "all sectors", "RES": "residential", "COM": "commercial", "IND": "industrial", "TRA": "transportation"}
CAISO_AS = {"nr": "non-spinning reserve", "sr": "spinning reserve", "ru": "regulation up", "rd": "regulation down"}


def plain_name(table, series, label):
    """A readable name for a series, where its codes are ones this file knows; else the label as the table writes it."""
    ent, var = str(series.get("entity", "")), str(series.get("variable", ""))
    p = ent.split(":")
    if table == "eia_state_generation_monthly" and len(p) == 4 and p[2] in STATES and p[3] in FUELS and var == "net_generation":
        return f"Net generation from {FUELS[p[3]]} in {STATES[p[2]]}" if p[3] != "ALL" else f"Net generation in {STATES[p[2]]}, all fuels"
    if table == "eia_retail_electricity_prices" and len(p) == 4 and p[2] in STATES and p[3] in SECTORS and var == "retail_price":
        return f"Retail electricity price in {STATES[p[2]]}, {SECTORS[p[3]]}"
    if table == "eia_retail_sales_monthly" and len(p) == 4 and p[2] in STATES and p[3] in SECTORS and var == "retail_sales":
        return f"Retail electricity sales in {STATES[p[2]]}, {SECTORS[p[3]]}"
    m = re.fullmatch(r"as_price_dam_(nr|sr|ru|rd)", var)
    if table == "caiso_as_prices" and m:
        return f"CAISO day-ahead {CAISO_AS[m.group(1)]} price ({p[-1]})"
    if table in ("eia_regional_retail_fuel_prices", "eia_retail_fuel_prices") and var == "retail_price" and series.get("node"):
        fuel = "Regular gasoline" if "_EPMR_" in ent else ("On-highway diesel" if "_EPD2D_" in ent else None)
        if fuel:
            return f"{fuel} retail price, {str(series['node']).title() if str(series['node']).isupper() else series['node']}"
    return label


def nd_for(v):
    a = abs(float(v))
    return 0 if a >= 10000 else (1 if a >= 100 else (2 if a >= 1 else 4))


def num(v, unit=""):
    """A number with its unit, as the scanner's cards write it."""
    t = common.fmt(float(v), nd_for(v))
    if unit.startswith("USD"):
        return f"USD {t}" + (f" per {unit.split('/', 1)[1]}" if "/" in unit else "")
    return f"{t} {unit}".strip()


def day_words(day, monthly=False):
    """'2026-07-01' as 'July 2026' for a monthly value, else '6 October 2026'."""
    y, m, d = (int(x) for x in str(day)[:10].split("-"))
    return f"{MONTHS[m - 1]} {y}" if monthly else f"{d} {MONTHS[m - 1]} {y}"


def fact_from_flag(fl):
    """The flag's one-line fact, written by code from the flag's own numbers."""
    u, c, h = fl.get("unit", ""), fl["compared"], fl["history"]
    monthly = "monthly" in str(fl.get("statistic", ""))
    name = plain_name(fl["table"], fl["series"], fl["label"])
    when = day_words(fl["date"], monthly)
    on = "in" if monthly else "on"
    if fl["rule"] == "record":
        high = fl["direction"] == "high"
        # no count of the values before it: the flag counts the history before its fresh window, not before this point
        return (f"{name}: {num(fl['value'], u)} {on} {when}, the {'highest' if high else 'lowest'} {fl['statistic']} held since "
                f"{day_words(h['first'], monthly)}. The record until now was {num(c['old_record'], u)}, {on} {day_words(c['old_record_date'], monthly)}.")
    if fl["rule"] == "negative":
        return (f"{name}: {num(fl['value'], u)} on {when}, the first price below zero in the {common.fmt(c['prior_days_held'], 0)} days held "
                f"before it. The day's mean was {num(c['day_mean'], u)}.")
    if fl["rule"] == "spike":
        years = fl["threshold"]["config"]["spike_history_years"]
        return (f"{name}: {num(fl['value'], u)} {on} {when} ({fl['statistic']}), {common.fmt(c['multiple_of_percentile'], 1)} times the "
                f"99th percentile of its prior {years} years ({num(c['percentile_value'], u)}).")
    if fl["rule"] == "weekly":
        fall = fl["direction"] == "low"
        return (f"{name}: {'down' if fall else 'up'} {num(abs(c['change']), u)} in the week to {when}, from {num(c['week_before_mean'], u)} to "
                f"{num(c['week_mean'], u)}. No weekly {'fall' if fall else 'rise'} since {day_words(c['range_first'])} was as large: the largest was "
                f"{num(abs(c['range_low'] if fall else c['range_high']), u)}, in the week to {day_words(c['range_low_date'] if fall else c['range_high_date'])}.")
    return (f"{name} against {c['x_label']}: {num(c['y_mean_new'], u)} in the 7 days to {when}, where the fit of the year before gives "
            f"{num(c['y_expected_new'], u)}: {common.fmt(c['sigmas'], 1)} standard deviations of its 7-day gaps.")


# ---------------------------------------------------------------------------------------------------------------------
# which tables may be shown
# ---------------------------------------------------------------------------------------------------------------------
def _csv(path):
    import csv
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(ln for ln in f if not ln.startswith("#")))


def public_tables(meta_dir=None):
    """The tables a chart may read: license public in coverage.csv, not marked "license needed" in license_status.csv,
    and not a table of a publisher held by a ruling (HELD)."""
    meta_dir = meta_dir or META_DIR
    held = {r["table"] for r in _csv(os.path.join(meta_dir, "license_status.csv")) if r.get("status") == "license needed"}
    return {r["table"] for r in _csv(os.path.join(meta_dir, "coverage.csv"))
            if r.get("license") == "public" and str(r.get("iso", "")).lower() not in HELD} - held


def held_series(entity):
    """Is this series a held publisher's (a consolidated table holds several grids: the entity names the grid)?"""
    return str(entity).split(":")[0].lower() in HELD


# ---------------------------------------------------------------------------------------------------------------------
# the data machine: the day's candidates
# ---------------------------------------------------------------------------------------------------------------------
def rank(flags):
    """Records and first negatives first, then by how far past the threshold; ties by id."""
    return sorted(flags, key=lambda f: (0 if f["rule"] in FIRST else 1, -float(f["strength"]), f["id"]))


def from_flags(raised, card_of, meta_dir=None):
    """The scanner's flags of the day as candidates, ranked: [{source, key, rank, fact, table, series_key, flag, card}].
    card_of(flag) -> the flag's finding card (findings_scanner.flag_card)."""
    ok = public_tables(meta_dir)
    out = []
    for fl in rank(raised):
        if fl["table"] not in ok or held_series(fl["series"].get("entity", "")) or (fl["rule"] == "pair" and fl["compared"].get("x_table") not in ok):
            continue
        card = card_of(fl)
        flag = {k: v for k, v in fl.items() if not k.startswith("_")}
        out.append({"source": "scanner", "key": fl["id"], "rank": len(out) + 1, "fact": fact_from_flag(fl), "table": fl["table"],
                    "series_key": fl["series_key"], "flag": flag, "card": card})
        if len(out) >= MAX_FLAGS:
            break
    return out


def _engine():
    """warehouse/analysis/run.py by its path (its name, `run`, is too common to import by name): `change`, `finding`."""
    name = "erw_analysis_run"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "warehouse", "analysis", "run.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


def robust_z(delta, earlier):
    import numpy as np
    x = np.asarray([float(v) for v in earlier], float)
    if not len(x):
        return 0.0
    s = 1.4826 * float(np.median(np.abs(x - np.median(x)))) or float(np.std(x))
    return round(abs(float(delta) - float(np.median(x))) / s, 4) if s > 0 else 0.0


def watch_card(spec, res, ch, method):
    """A watch line's change as a card of the scanner's form: the series, its newest period marked, the period it is
    compared with as the reference line, three callouts, and the line's own method as the footnote."""
    eng = _engine()
    hl = res["headline"]
    seq = eng.ordered(hl)
    shown = seq[-(104 if spec["by"] == "week" else 60):]
    weekly = spec["by"] == "week"
    x = [p[:10] if weekly else p for p, _ in shown]
    one, two = eng.finding(hl, ch, spec["compare"])
    n = len(ch["earlier"])
    bigger = sum(1 for v in ch["earlier"] if abs(v) >= abs(ch["delta"]))
    prev_words = "a year earlier" if spec["compare"] == "year" else ("the week before" if weekly else "the month before")
    u = spec["unit"]
    val = lambda v: f"{eng.shown(v)} {u}"   # noqa: E731
    end = str(eng.period_end(hl["period"]))
    card = {"id": "watch_change", "card_id": f"watch-{spec['name']}-{end}", "title": spec["title"].upper(), "kind": "visual", "subtitle": one,
            "params": {"measure": spec["name"], "period": hl["period"]}, "inputs_words": {"table": spec["table"], "period": hl["period"]},
            "chart": {"kind": "flag_line", "x": x, "x_label": ("week starting (Monday, UTC)" if weekly else "month") + "; the newest complete period is marked",
                      "series": [{"name": spec["label"], "type": "line", "unit": u, "values": [common.round6(v) for _, v in shown]}],
                      "mark": {"x": x[-1], "value": common.round6(hl["value"]), "label": "the newest complete period"},
                      "ref_lines": [{"name": prev_words, "value": common.round6(ch["prev_value"])}], "y_left_label": u, "decimals": nd_for(hl["value"])},
            "callouts": [common.callout("The newest period", prev_words, val(ch["prev_value"]), hl["period"][-10:] if weekly else eng.month_words(hl["period"]), val(hl["value"])),
                         common.callout("The change", "change", f"{'+' if ch['delta'] > 0 else '-'}{eng.shown(abs(ch['delta']))} {u}",
                                        f"of the {n} moves before it, as large", common.fmt(bigger, 0)),
                         common.callout("History held", "first period", seq[0][0][:10] if weekly else seq[0][0], "periods", common.fmt(len(seq), 0))],
            "why": "", "footnote": method, "numbers": {"value": hl["value"], "prev_value": ch["prev_value"], "delta": ch["delta"], "earlier": n,
                                                      "as_large": bigger, "periods": len(seq), "score": ch["score"]},
            "source_line": res["source_line"], "tables": [spec["table"]], "computed_at": common.now_iso(),
            "method": "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD}
    return card, (one + (" " + two if two else "")).strip()


def watch_candidates(now=None, meta_dir=None, log=None, fetch=None):
    """The watch list's changes of the latest period, largest first: the share of the measure's own earlier changes
    the newest one exceeds, ties by the change in robust standard deviations of the earlier ones. A measure whose
    table is not on the machine, is not public, or whose newest period is old or unchanged is left out."""
    import pandas as pd
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
    import watch
    eng = _engine()
    now = pd.Timestamp.now(tz="UTC") if now is None else pd.Timestamp(now)
    now = now.tz_localize("UTC") if now.tzinfo is None else now.tz_convert("UTC")
    ok = public_tables(meta_dir)
    say = log or (lambda m: None)
    out = []
    for spec in watch.WATCH:
        ents = spec["entity"] if isinstance(spec["entity"], (list, tuple)) else [spec["entity"]]
        if spec["table"] not in ok or any(held_series(e) for e in ents):
            continue
        try:
            t = watch.WatchTemplate(spec)
            ps = watch.periods((fetch or watch.fetch)(spec["table"]), spec, now)
            if len(ps) < 3:
                continue
            res = t.result(ps)
            ch = eng.change(res["headline"], spec["compare"])
            if not ch or ch["score"] is None or ch["delta"] == 0 or len(ch["earlier"]) < eng.MIN_HISTORY:
                continue
            age = (now.date() - eng.period_end(res["headline"]["period"])).days
            if age > WATCH_MAX_AGE[spec["by"]]:
                continue
            card, fact = watch_card(spec, res, ch, t.METHOD)
            vs = spec["variable"] if isinstance(spec["variable"], (list, tuple)) else [spec["variable"]]
            out.append({"source": "watch", "key": f"watch|{spec['name']}|{res['headline']['period']}", "fact": fact, "table": spec["table"],
                        "series_key": f"entity={'+'.join(ents)}|variable={'+'.join(vs)}", "score": ch["score"],
                        "z": robust_z(ch["delta"], ch["earlier"]), "period": res["headline"]["period"], "card": card})
        except watch.NoData as exc:
            say(f"  watch {spec['name']}: not on this machine ({str(exc)[:80]})")
        except Exception as exc:
            say(f"  watch {spec['name']}: left out ({type(exc).__name__}: {str(exc)[:100]})")
    out.sort(key=lambda c: (-c["score"], -c["z"], c["key"]))
    for i, c in enumerate(out[:MAX_WATCH], 1):
        c["rank"] = i
    return out[:MAX_WATCH]


def supabase():
    sys.path.insert(0, os.path.join(ROOT, "warehouse"))
    import lock
    url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    u = urllib.parse.urlparse(url)
    return f"{u.scheme}://{u.netloc}/rest/v1/{TABLE}", {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def publish(day, candidates, scanner_version="", machine="", post=None):
    """One row a day, replaced by a later scan of the same day. Returns True when it was written."""
    import requests
    sb = supabase()
    if sb is None:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not on this machine")
    base, h = sb
    row = {"day": day, "computed_at": common.now_iso(), "machine": machine, "scanner_version": scanner_version, "candidates": candidates}
    r = (post or requests.post)(base, params={"on_conflict": "day"}, data=json.dumps(row, default=common.round6, allow_nan=False),
                                headers={**h, "Prefer": "return=minimal,resolution=merge-duplicates"}, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} {r.text[:160]}")
    return True


def publish_day(day, flag_candidates, out_dir=None, scanner_version="", log=print, now=None, do_publish=True):
    """What findings_scanner.daily_request calls after a scan: add the watch list's candidates, keep the day's file,
    publish. Never raises: a scan is not failed by its chart candidates. Returns the count published (0 when not)."""
    import socket
    try:
        if now is None and day < dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"):
            now = day + "T23:59:59"                      # a scan of a past day: the watch list as that day saw it
        watch_c = watch_candidates(now=now, log=log)
    except Exception as exc:
        log(f"daily chart: the watch list could not be read ({type(exc).__name__}: {str(exc)[:120]})")
        watch_c = []
    cands = list(flag_candidates) + watch_c
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "daily_chart.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"day": day, "computed_at": common.now_iso(), "scanner_version": scanner_version, "candidates": cands}, f, indent=1,
                      ensure_ascii=False, default=common.round6)
            f.write("\n")
    if not do_publish:
        log(f"daily chart: {len(flag_candidates)} flag(s) and {len(watch_c)} watch change(s) for {day}, kept and not published")
        return 0
    try:
        publish(day, cands, scanner_version, socket.gethostname())
        log(f"daily chart: {len(flag_candidates)} flag(s) and {len(watch_c)} watch change(s) published for {day}")
        return len(cands)
    except Exception as exc:
        log(f"daily chart: the candidates of {day} were NOT published ({type(exc).__name__}: {str(exc)[:160]})")
        return 0


# ---------------------------------------------------------------------------------------------------------------------
# the Digest: read, choose, draw, write
# ---------------------------------------------------------------------------------------------------------------------
def read_candidates(day, wait=0, log=print, get=None, sleep=time.sleep, clock=time.time):
    """(row, why) for the Digest of `day`: today's candidates, waited for up to `wait` seconds (the worker takes the
    runner's request within a minute and scans for about three); else yesterday's, the newest scan before the day's
    run. None when neither is there or the table cannot be read."""
    sb = supabase()
    if sb is None:
        return None, "SUPABASE_URL or SUPABASE_SERVICE_KEY is not on this machine"
    import requests
    base, h = sb
    before = (dt.date.fromisoformat(day) - dt.timedelta(days=1)).isoformat()
    deadline = clock() + max(0, wait)
    while True:
        try:
            r = (get or requests.get)(base, params={"day": f"in.({day},{before})", "select": "day,computed_at,machine,scanner_version,candidates",
                                                    "order": "day.desc", "limit": "2"}, headers=h, timeout=60)
        except Exception as exc:
            return None, f"{type(exc).__name__}: {str(exc)[:120]}"
        if r.status_code != 200:
            return None, f"HTTP {r.status_code} {str(getattr(r, 'text', ''))[:120]}"
        rows = r.json()
        today = next((x for x in rows if x["day"] == day), None)
        if today is not None:
            return today, f"the scan of {day} (computed {today['computed_at']})"
        if clock() >= deadline:
            break
        sleep(min(20, max(1, deadline - clock())))
    if rows:
        return rows[0], f"the scan of {rows[0]['day']} (computed {rows[0]['computed_at']}): the scan of {day} was not there after {int(wait)} seconds"
    return None, f"no candidates for {day} or {before} in {TABLE}"


def used_keys(chart_dir=None, but=None):
    """The keys of the charts a Digest has shown: docs/digest/charts/<date>.json, but for a proof (a render made to
    show the rule on past days, never printed in a Digest) and but for the day `but` (a second writing of that day's
    Digest, or its shadow copy, chooses as the first did)."""
    chart_dir = chart_dir or CHART_DIR
    out = set()
    if not os.path.isdir(chart_dir):
        return out
    for f in os.listdir(chart_dir):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", f) and f != f"{but}.json":
            try:
                with open(os.path.join(chart_dir, f), encoding="utf-8") as fh:
                    d = json.load(fh)
            except (OSError, ValueError):
                continue
            if d.get("key") and not d.get("proof"):
                out.add(d["key"])
    return out


def record_jump(c):
    """How far a scanner record is past the old record, as a share of the old record's size (0.34 is 34 percent); None
    for anything that is not a record or does not hold both numbers. A record past an old record of zero is infinite."""
    fl = c.get("flag") or {}
    if c.get("source") != "scanner" or fl.get("rule") != "record":
        return None
    try:
        v, old = float(fl["value"]), float((fl.get("compared") or {})["old_record"])
    except (KeyError, TypeError, ValueError):
        return None
    if old == 0:
        return 0.0 if v == 0 else float("inf")
    return abs(v - old) / abs(old)


def must_wait(c, waited):
    """The guard (session 267): a record more than RECORD_JUMP past the old one, not held on an earlier run, waits."""
    j = record_jump(c)
    return j is not None and j > RECORD_JUMP and c["key"] not in waited


def held_before(day, chart_dir=None):
    """The keys the guard held on a run of a day before `day` (docs/digest/charts/held.json): they may be shown now."""
    try:
        with open(os.path.join(chart_dir or CHART_DIR, HELD_FILE), encoding="utf-8") as f:
            held = json.load(f)
    except (OSError, ValueError):
        return set()
    return {k for k, v in held.items() if isinstance(v, dict) and str(v.get("held_on", "")) < str(day)}


def keep_held(day, candidates, used, waited, chart_dir=None):
    """Writes the records the guard holds on this run to held.json (the first day each was held is kept); their keys."""
    now = [c for c in candidates if c["key"] not in used and must_wait(c, waited)]
    if not now:
        return []
    path = os.path.join(chart_dir or CHART_DIR, HELD_FILE)
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f)
    except (OSError, ValueError):
        held = {}
    for c in now:
        if c["key"] not in held:
            j = record_jump(c)
            held[c["key"]] = {"held_on": day, "table": c.get("table", ""), "series_key": c.get("series_key", ""),
                              "value": c["flag"]["value"], "old_record": c["flag"]["compared"]["old_record"],
                              "jump_pct": None if j == float("inf") else round(100 * j, 1), "fact": c.get("fact", "")}
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(held, f, indent=1, ensure_ascii=False, sort_keys=True, default=common.round6)
        f.write("\n")
    return [c["key"] for c in now]


def choose(candidates, used, day=None, waited=None):
    """(candidate, why) by the rule: the strongest scanner flag not shown before; else the watch list's largest change
    not shown before; else (None, the reason). The same day's own file never blocks its choice (a rerun).
    Session 267: a record more than 25 percent past the old one is passed over unless its key is in `waited` (held on
    an earlier run: held_before); the why says how many were held."""
    waited = set() if waited is None else set(waited)
    flags = [c for c in candidates if c.get("source") == "scanner"]
    watch_c = [c for c in candidates if c.get("source") == "watch"]
    held = [c["key"] for c in flags if c["key"] not in used and must_wait(c, waited)]
    note = (f"; {len(held)} record(s) more than {round(100 * RECORD_JUMP)} percent past the old one held a day by the guard"
            if held else "")
    for c in flags:
        if c["key"] not in used and c["key"] not in held:
            return c, (f"the strongest of the scanner's {len(flags)} flag(s) of the day that no Digest has shown "
                       f"(rank {c.get('rank', '?')}; rule {c['flag']['rule']}, strength {c['flag']['strength']})" + note)
    for c in watch_c:
        if c["key"] not in used:
            return c, ((f"the scanner flagged nothing" if not flags else f"all {len(flags)} of the scanner's flags were shown before or held")
                       + f": the watch list's largest change of the latest period not shown before (rank {c.get('rank', '?')}, "
                       f"larger than {c['score']} percent of its own earlier changes)" + note)
    return None, (("the scanner flagged nothing and the watch list has no change" if not candidates
                   else f"every candidate ({len(flags)} flag(s), {len(watch_c)} watch change(s)) was shown in an earlier Digest or held")
                  + note)


def how_words(c):
    if c["source"] == "scanner":
        return ("Chosen by rule, not by a person or a model: the strongest flag of the day's scan that no Digest has shown "
                f"(rule: {c['flag']['rule']}; {common.fmt(float(c['flag']['strength']), 2)} robust standard deviations past its threshold).")
    return ("Chosen by rule, not by a person or a model: the scanner had no new flag, so this is the watch list's largest change of the latest period "
            + ("(larger than every one of the measure's own earlier changes)." if float(c["score"]) >= 100
               else f"(larger than {common.fmt(float(c['score']), 1)} percent of the measure's own earlier changes)."))


def markdown(day, c):
    """The section's lines. The image sits beside the Digest (docs/digest/charts/<date>.png)."""
    alt = c["fact"].replace("[", "(").replace("]", ")")
    series = ", ".join(part for part in str(c["series_key"]).split("|") if part and not part.endswith("="))
    return ["", HEADING, "", f"![{alt}](charts/{day}.png)", "", c["fact"], "",
            f"Table `{c['table']}`, series `{series}`: [the table and its download](/data#{c['table']}). {how_words(c)} "
            f"[How the chart is chosen](/data/methods/automated_analysis_scanner)."]


def section(day, log=print, chart_dir=None, wait=None, local_watch=True, candidates=None, proof=False, used=None, waited=None):
    """The Digest's section for `day`: [] when there is nothing to show (the reason is logged). Writes the picture and
    the record of the choice. candidates: given (a test, a proof) instead of read. waited: the keys the guard held on an
    earlier run (session 267; by default read from chart_dir's held.json); the records it holds now are written there."""
    chart_dir = chart_dir or CHART_DIR
    try:
        why_source = "given"
        if candidates is None:
            wait = DEFAULT_WAIT if wait is None else wait
            row, why_source = read_candidates(day, wait, log)
            candidates = (row or {}).get("candidates") or []
            if row is None and local_watch:
                log(f"  daily chart: {why_source}; trying the watch list on this machine's own tables")
                candidates = watch_candidates(log=log)
                why_source = "the watch list on this machine (no candidates from the data machine)"
        used = (used_keys(chart_dir, but=day) if used is None else set(used))   # a rerun of the day chooses as it did the first time
        own = os.path.join(chart_dir, f"{day}.json")
        waited = held_before(day, chart_dir) if waited is None else set(waited)
        c, why = choose(candidates, used, day, waited)
        for k in ([] if proof else keep_held(day, candidates, used, waited, chart_dir)):   # a proof holds nothing
            log(f"  daily chart: {k} held a day (a record more than {round(100 * RECORD_JUMP)} percent past the old one)")
        if c is None:
            log(f"  daily chart: {why} ({why_source}); section omitted")
            return []
        import card_image
        png = card_image.render(c["card"], os.path.join(chart_dir, f"{day}.png"), "digest", fact=c["fact"])
        record = {"date": day, "source": c["source"], "key": c["key"], "fact": c["fact"], "table": c["table"], "series_key": c["series_key"],
                  "why": why, "candidates_from": why_source, "title": c["card"]["title"], "numbers": c["card"].get("numbers", {}),
                  "image": os.path.basename(png), "rendered_at": common.now_iso(), "method": METHOD}
        if c["source"] == "scanner":
            record["flag"] = c["flag"]
        if proof:
            record["proof"] = True
        with open(own, "w", encoding="utf-8", newline="\n") as f:
            json.dump(record, f, indent=1, ensure_ascii=False, default=common.round6)
            f.write("\n")
        log(f"  daily chart: {c['key']} ({c['source']}); {why}; {why_source}")
        return markdown(day, c)
    except Exception as exc:
        log(f"  daily chart: omitted ({type(exc).__name__}: {str(exc)[:200]})")
        return []


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the Digest's daily chart (session 232)")
    ap.add_argument("--date", help="YYYY-MM-DD (default today, UTC)")
    ap.add_argument("--candidates", action="store_true", help="the data machine: print the day's candidates from runs/scanner/<date>/daily_chart.json")
    ap.add_argument("--section", action="store_true", help="what brief.py runs: choose, draw, print the section")
    ap.add_argument("--wait", type=int, default=0, help="with --section: seconds to wait for the day's candidates")
    a = ap.parse_args(argv)
    day = a.date or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    if a.candidates:
        p = os.path.join(ROOT, "runs", "scanner", day, "daily_chart.json")
        if not os.path.exists(p):
            print(f"no candidates kept for {day} ({p})")
            return 1
        with open(p, encoding="utf-8") as f:
            for c in json.load(f)["candidates"]:
                print(f"{c['source']:8} {c.get('rank', ''):>3} {c['key']}\n         {c['fact']}")
        return 0
    if a.section:
        lines = section(day, wait=a.wait)
        print("\n".join(lines) if lines else "no section")
        return 0
    ap.error("--candidates or --section")


if __name__ == "__main__":
    sys.exit(main())
