#!/usr/bin/env python3
"""The findings hunt of chain 502, family "events": the nine events of /events across all thirteen regions, session 8204.

Energy Research Warehouse (ERW). Plan: docs/reviews/findings-hunt-plan-2026-11-19.md. The /events pages read the
seven grids; here every one of EIA's thirteen regions is read over each event's window (docs/methods/events.md):
the window's highest hour of demand (its mean hour for COVID-19's spring) against the same calendar days of every
other year the hourly tables hold. Demand: the region's authorities summed by hour (hourly930.region_demand).

A claim is the event year against the mean of the other years; it is drafted only when it passes five tests:
    the extreme of the years held      the event year's figure is above (COVID-19: below) every other year's
    clear by a typical spread          its distance from the others' mean is at least 1.4826 times their median
                                       absolute deviation (their standard deviation when that is zero)
    sample large enough                each year compared holds 90 percent of the window's hours; four other years
    holds against the median           the distance from the others' median is at least half that from their mean
    not one hour                       the window's third-highest hour is at least 95 percent of its highest
                                       (COVID-19: the window holds at least 90 percent of its hours, as every year must)
No flow between regions is read here: event-time flows are the donor ledger the chain file leaves to Samuel.

    python warehouse/analysis/findings/deep/events.py --dry-run [--in-dir <warehouse/output>]
    python warehouse/analysis/findings/deep/events.py --load
"""

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)
import hourly930 as h  # noqa: E402  (sets builder.CHAIN to 502)
import builder  # noqa: E402
import findings_common as common  # noqa: E402
import hunt  # noqa: E402
import hunt_measures as hm  # noqa: E402

FAMILY = "events"
MIN_OTHER = 4
FULL = 0.9
PER_EVENT = 5
SIX = {"SE", "FLA", "CAR", "TEN", "NW", "SW"}
EVENTS = [  # key, year, first day, last day, the event in words, measure
    ("covid_2020", 2020, "03-01", "05-31", "the COVID-19 spring of 2020", "mean"),
    ("caiso_heat_2020", 2020, "08-10", "08-24", "the August 2020 West heat wave", "max"),
    ("uri_2021", 2021, "02-07", "02-24", "Winter Storm Uri", "max"),
    ("caiso_heat_2022", 2022, "08-31", "09-09", "the September 2022 West heat wave", "max"),
    ("elliott_2022", 2022, "12-19", "12-29", "Winter Storm Elliott", "max"),
    ("ercot_heat_2023", 2023, "08-01", "09-10", "the summer 2023 Texas heat", "max"),
    ("cold_2025", 2025, "01-17", "01-26", "the January 2025 cold", "max"),
    ("east_heat_2025", 2025, "06-20", "06-28", "the June 2025 eastern heat wave", "max"),
    ("cold_2026", 2026, "01-23", "02-02", "the late January 2026 cold", "max"),
]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
CTX = {}


def day_words(year, md):
    m, d = int(md[:2]), int(md[3:])
    return f"{d} {MONTHS[m - 1]} {year}"


def window_hours(year, a, b):
    d0 = dt.date(year, int(a[:2]), int(a[3:]))
    d1 = dt.date(year, int(b[:2]), int(b[3:]))
    return ((d1 - d0).days + 1) * 24


def series(in_dir):
    d = h.region_demand(in_dir)[["code", "ts_utc", "year", "demand_mw"]].copy()
    d["md"] = d["ts_utc"].str[5:10]
    d["day"] = d["ts_utc"].str[:10]
    return d


def claims(in_dir):
    d = series(in_dir)
    out = []
    for key, ey, a, b, name, how in EVENTS:
        w = d[(d["md"] >= a) & (d["md"] <= b)]
        for code, g in w.groupby("code"):
            vals = {}
            for y, s in g.groupby("year"):
                need = window_hours(y, a, b)
                if len(s) >= FULL * need:
                    vals[int(y)] = (float(s["demand_mw"].max() if how == "max" else s["demand_mw"].mean()), len(s))
            if ey not in vals:
                continue
            others = {y: v for y, v in vals.items() if y != ey}
            if len(others) < MIN_OTHER:
                continue
            ve, ov = vals[ey][0], np.array([v[0] for v in others.values()])
            mean_o, med_o = float(ov.mean()), float(np.median(ov))
            mad = 1.4826 * float(np.median(np.abs(ov - med_o)))
            spread = mad if mad > 0 else float(ov.std())
            gap = ve - mean_o
            ev = g[g["year"] == ey].sort_values("demand_mw", ascending=False)
            top3 = ev["demand_mw"].head(3).tolist()
            hi = how == "max"
            t = [{"name": "the extreme of the years held", "passed": bool(ve > ov.max()) if hi else bool(ve < ov.min()),
                  "words": f"{ey}'s figure is {common.fmt(ve, 0)} MW; the {'highest' if hi else 'lowest'} other year's is {common.fmt(float(ov.max() if hi else ov.min()), 0)} MW"},
                 {"name": "clear by a typical spread", "passed": bool(spread > 0 and abs(gap) >= spread),
                  "words": f"the distance from the other years' mean is {common.fmt(abs(gap), 0)} MW against a typical spread of {common.fmt(spread, 0)} MW"},
                 {"name": "sample large enough", "passed": len(others) >= MIN_OTHER,
                  "words": f"{len(others)} other years each hold at least {int(FULL * 100)} percent of the window's hours; {ey} holds {vals[ey][1]} of {window_hours(ey, a, b)}"},
                 {"name": "holds against the median", "passed": bool(np.sign(ve - med_o) == np.sign(gap) and abs(ve - med_o) >= 0.5 * abs(gap)),
                  "words": f"the distance from the other years' median is {common.fmt(abs(ve - med_o), 0)} MW"},
                 {"name": "not one hour", "passed": bool(len(top3) == 3 and top3[2] >= 0.95 * top3[0]) if hi else True,
                  "words": (f"the window's third-highest hour is {common.fmt(top3[2] / top3[0] * 100, 1)} percent of its highest" if hi and len(top3) == 3
                            else "a mean over the window's hours")}]
            out.append({"event": key, "event_year": ey, "a": a, "b": b, "name": name, "how": how, "code": code, "vals": vals, "ve": ve, "mean_o": mean_o,
                        "med_o": med_o, "spread": spread, "gap": gap, "strength": abs(gap) / spread if spread > 0 else 0.0, "tests": t,
                        "passed": all(x["passed"] for x in t), "peak_ts": ev["ts_utc"].iloc[0] if hi else None, "daily": _daily(g, ey, how)})
    return out


def _daily(g, ey, how):
    f = "max" if how == "max" else "mean"
    ev = g[g["year"] == ey].groupby("md")["demand_mw"].agg(f)
    ot = g[g["year"] != ey].groupby(["year", "md"])["demand_mw"].agg(f).groupby("md").mean()
    return [(md, float(ev.get(md, np.nan)), float(ot.get(md, np.nan))) for md in sorted(set(ev.index) | set(ot.index))]


# ---------------------------------------------------------------------------------------------------------------------
# the draft
# ---------------------------------------------------------------------------------------------------------------------
def words(code):
    return f"{h.REG[code]} (EIA's region)"


def sentence(c):
    hi = c["how"] == "max"
    others = sorted(y for y in c["vals"] if y != c["event_year"])
    pct = c["gap"] / c["mean_o"] * 100
    what = "highest hour of demand" if hi else "mean hour of demand"
    return (f"The {what} in {words(c['code'])} from {day_words(c['event_year'], c['a'])} to {day_words(c['event_year'], c['b'])}, the days /events gives to {c['name']}, "
            f"was {common.fmt(c['ve'], 0)} MW, {common.fmt(abs(pct), 1)} percent {'above' if pct > 0 else 'below'} the mean of the same days' "
            f"{'highest hours' if hi else 'mean hours'} in the other {len(others)} years held, {others[0]} to {others[-1]} ({common.fmt(c['mean_o'], 0)} MW).")


def slug(c):
    return f"{c['event'].replace('_', '-')}-{c['code'].lower()}"


def did_of(c):
    return "scan-deep-" + hashlib.sha1(f"events|{c['event']}|{c['code']}|{round(c['ve'], 3)}".encode("utf-8")).hexdigest()[:12]


LIMITS = ("EIA-930 demand as the authorities filed it, summed by region (an hour held only when every authority filing demand that month holds it); "
          "demand served during a load shed is load served, a floor on what was wanted; the same calendar days in UTC of the other years, not the "
          "weekday-aligned baseline of the /events pages.")


def reproduce_py(c):
    m = "s['demand_mw'].max()" if c["how"] == "max" else "s['demand_mw'].mean()"
    body = (f"d = region_demand(sys.argv[1], '{c['code']}')\nd = d[(d['ts_utc'].str[5:10] >= '{c['a']}') & (d['ts_utc'].str[5:10] <= '{c['b']}')]\n"
            "for y, s in d.groupby('year'):\n"
            f"    need = (pd.Timestamp(f'{{y}}-{c['b']}') - pd.Timestamp(f'{{y}}-{c['a']}')).days * 24 + 24\n"
            f"    if len(s) >= {FULL} * need:\n        print(y, round(float({m}), 6), len(s))\n")
    what = (f"For each year held: the {'highest' if c['how'] == 'max' else 'mean'} hour of demand of {h.REG[c['code']]} from {c['a']} to {c['b']} (UTC days), "
            f"years holding at least {int(FULL * 100)} percent of the window's hours. The claim is {c['event_year']} against the mean of the other years.")
    return h.py_doc(c["event"], c["code"], ["eia930_ba_demand_hourly"], what) + h.PY_READ + h.PY_REGION_DEMAND + body


def reproduce_do(c):
    stat = "max" if c["how"] == "max" else "mean"
    lines = (h.do_head(c["event"], c["code"], ["eia930_ba_demand_hourly"]) + h.do_region_demand(c["code"]) +
             ["generate str5 md = substr(ts_utc, 6, 5)", f'keep if md >= "{c["a"]}" & md <= "{c["b"]}"',
              f'generate double need = 24 * (date(string(year) + "-{c["b"]}", "YMD") - date(string(year) + "-{c["a"]}", "YMD") + 1)',
              f"collapse ({stat}) measure = demand (count) n = demand (first) need = need, by(year)", f"keep if n >= {FULL} * need", "drop need",
              "sort year", "list year measure n, noobs"])
    return common.do_file(lines)


def build(c, out_dir, docs_root=None):
    import card_image
    did, s = did_of(c), slug(c)
    fact = sentence(c)
    others = sorted(y for y in c["vals"] if y != c["event_year"])
    tests_words = " ".join(f"{t['name'].capitalize()}: {t['words']} ({'passed' if t['passed'] else 'failed'})." for t in c["tests"])
    tables = ["eia930_ba_demand_hourly"]
    source_line = f"Source: the ERW table eia930_ba_demand_hourly, the authorities of {words(c['code'])} summed by hour; computed by warehouse/analysis/findings/deep/events.py ({c['event']})."
    files = [f"{did}.csv", f"{did}_reproduce.py", f"{did}_reproduce.do", f"{did}_1200x627.png", f"{did}_1080x1080.png", f"{did}_caption.txt"]
    days = [f"{c['event_year']}-{md}" for md, _, _ in c["daily"]]
    title = f"{c['name'].upper()}: {h.REG[c['code']].upper()}"
    stat = "highest hour" if c["how"] == "max" else "mean hour"
    pk = max(c["daily"], key=lambda r: (r[1] if not np.isnan(r[1]) else -1e18) * (1 if c["how"] == "max" else -1))
    card = {"id": "hunt_pattern", "card_id": did, "title": title, "kind": "visual", "subtitle": fact, "draft": True,
            "params": {"pattern": c["event"], "region": c["code"]}, "inputs_words": {"pattern": c["name"], "region": words(c["code"])},
            "chart": {"kind": "flag_line", "x": days, "x_label": f"the window's days; each day's {stat} of demand",
                      "series": [{"name": f"{c['event_year']}", "type": "line", "unit": "MW", "values": [common.round6(v) for _, v, _ in c["daily"]]},
                                 {"name": f"the other years' mean, {others[0]} to {others[-1]}", "type": "line", "unit": "MW", "values": [common.round6(v) for _, _, v in c["daily"]]}],
                      "mark": {"x": f"{c['event_year']}-{pk[0]}", "value": common.round6(pk[1]), "label": c["name"]},
                      "ref_lines": [], "y_left_label": "MW", "decimals": 0},
            "callouts": [common.callout("The event", f"other years' {stat}, mean", f"{common.fmt(c['mean_o'], 0)} MW", f"{c['event_year']}", f"{common.fmt(c['ve'], 0)} MW"),
                         common.callout("How large", "typical spread", f"{common.fmt(c['spread'], 0)} MW", "this gap, in those", common.fmt(c["strength"], 1)),
                         common.callout("The tests", "other years", f"{len(others)}", "tests passed", f"{sum(1 for t in c['tests'] if t['passed'])} of {len(c['tests'])}")],
            "why": "",
            "footnote": (f"A draft of the findings hunt (chain {builder.CHAIN}) on {common.now_iso()[:10]}; not reviewed. Event {c['event']}: {c['name']}, "
                         f"{c['a']} to {c['b']} {c['event_year']}. Region: {words(c['code'])}. {tests_words} Limits: {LIMITS} The claim states what the hours show; "
                         f"it does not say what caused it. Plan: {builder.METHOD}."),
            "numbers": {"event": c["ve"], "mean_other": c["mean_o"], "median_other": c["med_o"], "gap": c["gap"], "spread": c["spread"], "strength": c["strength"],
                        "event_year": c["event_year"], "other_years": others},
            "source_line": source_line, "tables": tables, "computed_at": common.now_iso(), "method": "https://github.com/SamuelEnrique/erw/blob/main/" + builder.METHOD,
            "scanner": {"version": builder.VERSION, "rule": "hunt", "date": f"{c['event_year']}-{c['b']}", "flag_id": did, "strength": c["strength"], "full_card": None},
            "hunt": {"pattern": c["event"], "module": "deep.events", "region": c["code"], "region_words": words(c["code"]), "why": "new: the findings hunt of chain 502, events",
                     "tests": c["tests"], "files": files, "measure": c["event"], "family": FAMILY, "chain": builder.CHAIN, "limits": LIMITS, "consequence": 3, "license": None}}
    caption = "\n".join([fact, "", f"Checked five ways before it was drafted: {tests_words}", "", f"Limits: {LIMITS}", "", source_line,
                         "Computed by the Energy Research Warehouse (ERW). A draft: not reviewed."])
    card["hunt"]["caption"] = caption
    first_o = others[0]
    head_py = (f"# Expected: {first_o} {common.round6(c['vals'][first_o][0])}, {c['event_year']} {common.round6(c['ve'])}, change {common.round6(c['ve'] - c['vals'][first_o][0])} (MW); "
               f"tolerance 0.5 percent of the change.\n# The claim: {c['event_year']} against the mean of the other years, {common.round6(c['mean_o'])} MW.\n")
    csv = [f"# Energy Research Warehouse (ERW): findings hunt (chain {builder.CHAIN}), event {c['event']}, region {c['code']} ({words(c['code'])})",
           f"# Computed {common.now_iso()} by warehouse/analysis/findings/deep/events.py; plan https://github.com/SamuelEnrique/erw/blob/main/{builder.METHOD}",
           f"# Rows: one per year held: the window's {stat} of demand (MW) from {c['a']} to {c['b']}, the hours it rests on, and whether it is the event year",
           "# Tables: eia930_ba_demand_hourly", "region,year,value,n_observations,event_year"]
    csv += [f"{c['code']},{y},{v!r},{n!r},{1 if y == c['event_year'] else 0}" for y, (v, n) in sorted(c["vals"].items())]
    head_do = "\n\n".join("* " + ln[2:] for ln in head_py.strip("\n").split("\n")) + "\n\n"
    texts = {files[0]: "\n".join(csv) + "\n", files[1]: head_py + reproduce_py(c), files[2]: head_do + reproduce_do(c), files[5]: caption + "\n"}
    os.makedirs(out_dir, exist_ok=True)
    stored = {}
    for name, text in texts.items():
        builder.check_text(text, name)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        stored[name] = {"kind": "text", "content": text}
    builder.check_text(json.dumps(card, ensure_ascii=False), did)
    for name, size in ((files[3], "linkedin_wide"), (files[4], "linkedin_square")):
        p = card_image.render(card, os.path.join(out_dir, name), size, fact=fact)
        with open(p, "rb") as f:
            stored[name] = {"kind": "png", "content": base64.b64encode(f.read()).decode("ascii")}
    flag = {"id": did, "rule": "hunt", "pattern": c["event"], "module": "deep.events", "region": c["code"], "deep_version": builder.VERSION,
            "claim": {"event_year": c["event_year"], "event": c["ve"], "mean_other": c["mean_o"], "gap": c["gap"], "values": {str(k): v[0] for k, v in c["vals"].items()}},
            "tests": c["tests"], "why": "new: the findings hunt of chain 502, events"}
    row = {"id": did, "flag_key": f"hunt|deep.events|{c['event']}|{c['code']}", "rule": "hunt", "table_name": tables[0],
           "series_key": f"pattern={c['event']}|region={c['code']}", "flag_date": f"{c['event_year']}-{c['b']}", "value": c["gap"], "strength": c["strength"],
           "scanner_version": builder.VERSION, "flag": flag, "card": card, "files": stored}
    with open(os.path.join(out_dir, did + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(row, f, indent=1, ensure_ascii=False, default=common.round6)
        f.write("\n")
    d = os.path.join(docs_root or builder.DOCS, FAMILY)
    os.makedirs(d, exist_ok=True)
    for src, dst in ((files[0], f"{s}.csv"), (files[1], f"{s}.reproduce.py"), (files[2], f"{s}.reproduce.do")):
        with open(os.path.join(d, dst), "w", encoding="utf-8", newline="\n") as f:
            f.write(texts[src])
    with open(os.path.join(out_dir, files[3]), "rb") as f, open(os.path.join(d, f"{s}.png"), "wb") as g:
        g.write(f.read())
    yrs = ", ".join(f"{y}: {common.fmt(v, 0)}" for y, (v, _) in sorted(c["vals"].items()))
    md = [f"# {c['name'].capitalize()}: {words(c['code'])}", "",
          f"Draft `{did}` of the findings hunt (chain {builder.CHAIN}), {common.now_iso()[:10]}. State: draft, not reviewed. Review at `/internal/findings`.", "",
          f"**The finding.** {fact}", "", f"![{c['name'].capitalize()}, {words(c['code'])}]({s}.png)", "",
          f"**The figure by year** (the window's {stat} of demand, MW): {yrs}.", "",
          f"**The tables and rows.** `eia930_ba_demand_hourly`; the authorities of {words(c['code'])} summed by hour, the hours from {c['a']} to {c['b']} of each year. "
          f"The yearly values: `{s}.csv`.", "",
          f"**Its strength.** The gap is {common.fmt(c['strength'], 2)} typical spreads of the other years. " + " ".join(f"{t['name'].capitalize()}: {t['words']}." for t in c["tests"]), "",
          f"**Its limits.** {LIMITS}", "",
          f"**Reproduce.** `python {s}.reproduce.py <eia930_ba_demand_hourly.csv>` and `do {s}.reproduce.do` (Stata) recompute every year's figure; each names "
          f"the expected values at its top, and the claim's mean of the other years.", ""]
    text = "\n".join(md)
    builder.check_text(text, s)
    with open(os.path.join(d, f"{s}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return row


def run(in_dir, dry_run=True, max_drafts=24, log=print):
    now = dt.datetime.now(dt.timezone.utc)
    out_dir = os.path.join(builder.OUT, now.strftime("%Y-%m-%d"), FAMILY)
    os.makedirs(out_dir, exist_ok=True)
    cs = claims(in_dir)
    # session 8204: at most PER_EVENT drafts an event, the six regions no page shows first, then by strength
    passing = sorted([c for c in cs if c["passed"]], key=lambda c: (c["code"] not in SIX, -c["strength"]))
    kept, per = [], {}
    for c in passing:
        if per.get(c["event"], 0) < PER_EVENT and len(kept) < max_drafts:
            kept.append(c)
            per[c["event"]] = per.get(c["event"], 0) + 1
    built = [build(c, out_dir, docs_root=os.path.join(out_dir, "docs") if dry_run else None) for c in kept]
    loaded = list(hunt.load_drafts(built, log)) if built and not dry_run else []
    summary = {"family": FAMILY, "claims": len(cs), "passed": len(passing), "drafts": [b["id"] for b in built], "loaded": loaded, "dry_run": dry_run,
               "results": [{"candidate": c["event"], "region": c["code"], "passed": c["passed"], "drafted": any(b["flag_key"].endswith(f"|{c['event']}|{c['code']}") for b in built),
                            "strength": c["strength"], "first": c["mean_o"], "last": c["ve"], "fact": sentence(c),
                            "reason": "; ".join(t["name"] for t in c["tests"] if not t["passed"])} for c in cs]}
    with open(os.path.join(out_dir, f"{FAMILY}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False, default=common.round6)
    log(f"events: {len(cs)} claims, {len(passing)} pass, {len(built)} drafts, {len(loaded)} loaded" + (" (dry run)" if dry_run else ""))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="The findings hunt of chain 502, family events")
    ap.add_argument("--in-dir", default=None)
    ap.add_argument("--max-drafts", type=int, default=24)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--load", action="store_true")
    a = ap.parse_args(argv)
    run(a.in_dir or common.DEFAULT_IN_DIR, dry_run=not a.load, max_drafts=a.max_drafts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
