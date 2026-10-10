"""Finding: "Who rescues whom" (session 174).

During the events the warehouse already holds (Winter Storm Uri, Winter Storm Elliott, the summer 2023 heat in ERCOT, the
August 2020 heat in CAISO), which balancing authorities flipped from importing to exporting, and which the other way. For
every balancing authority EIA-930 reports, the daily net interchange (exports minus imports, MWh a day, the sum over its
pairs of eia930_daily_interchange, where a positive value is power sent from the row's authority to its neighbour) is
averaged over the event's window and over its baseline, the same calendar days 364 and 728 days earlier (the events
method's baseline, docs/methods/events.md); the window itself comes from event_window_daily's header. EIA reports each
pair twice, once by each side, and the two reports disagree at times (on 2021-02-15 PJM reported 432,663 MWh to MISO and
MISO 178,851 MWh from PJM): a pair's flow here is the mean of its two sides where both are held, and the footnote says how
often the sides differ by more than a tenth. EIA's region rows (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN,
TEX, US48) are sums of authorities and are left out. An authority that
was a net importer on the baseline and a net exporter in the window "flipped to exporting"; the reverse "flipped to
importing"; the rest kept their sign.

Tables: eia930_daily_interchange (every pair, 2019 on, EIA's Eastern-time days), event_window_daily (the windows).
"""

import os
import re

import numpy as np
import pandas as pd

from findings_common import METHOD_URL, NoData, callout, do_destring, do_file, do_sentinels, fmt, now_iso, read_table, table_path

NAME = "who_rescues_whom"
TITLE = "WHO RESCUES WHOM"
KIND = "visual"
EVENTS = {
    "uri_2021": "Winter Storm Uri, February 2021",
    "elliott_2022": "Winter Storm Elliott, December 2022",
    "ercot_heat_2023": "the summer 2023 heat in ERCOT",
    "caiso_heat_2020": "the August 2020 heat wave in CAISO",
}
INPUTS = {
    "event": {"label": "Event", "default": "uri_2021", "choices": list(EVENTS), "words": EVENTS},
    "min_mwh": {"label": "Smallest daily flow counted (MWh a day)", "default": 1000, "choices": [0, 1000, 5000]},
}
TABLES = ["eia930_daily_interchange", "event_window_daily"]
CSV_NAME = "erw_2026_event_interchange_flips.csv"
GRID_OF = {"uri_2021": "erco", "elliott_2022": "pjm", "ercot_heat_2023": "erco", "caiso_heat_2020": "ciso"}
REGIONS = {"cal", "car", "cent", "fla", "mida", "midw", "ne", "nw", "ny", "se", "sw", "ten", "tex", "us48"}   # EIA's regions, not authorities
NAMES = {"erco": "ERCOT", "ciso": "CAISO", "pjm": "PJM", "miso": "MISO", "swpp": "SPP", "nyis": "NYISO", "isne": "ISO-NE",
         "bpat": "Bonneville", "tva": "TVA", "soco": "Southern", "duk": "Duke Carolinas", "cple": "Duke Progress East", "aeci": "AECI",
         "ldwp": "Los Angeles DWP", "azps": "Arizona Public Service", "srp": "Salt River Project", "nevp": "NV Energy", "pacw": "PacifiCorp West",
         "pace": "PacifiCorp East", "wacm": "WAPA Rocky Mountain", "psco": "Public Service Colorado", "fpl": "Florida Power & Light", "fpc": "Duke Florida",
         "banc": "BANC (Sacramento)", "iid": "Imperial Irrigation", "tepc": "Tucson Electric", "pnm": "PNM", "epe": "El Paso Electric", "cen": "CENACE (Mexico)",
         "cple": "Duke Progress East", "cplw": "Duke Progress West", "sc": "Santee Cooper", "scen": "Dominion SC", "aec": "PowerSouth", "lgee": "LG&E and KU",
         "ohms": "Ohio Valley", "ipco": "Idaho Power", "nwmt": "NorthWestern", "avrn": "Avangrid Renewables", "wauw": "WAPA Upper Great Plains West"}


def windows(in_dir):
    """The events' windows from event_window_daily's header: {event: (first day, last day)}."""
    p = table_path("event_window_daily", in_dir)
    text = ""
    with open(p, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line.startswith("# Events:") or line.startswith("#  ") or "window" in line:
                text += line
    out = {}
    for m in re.finditer(r"(\w+) \([^)]*\), window (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})", text):
        out[m.group(1)] = (m.group(2), m.group(3))
    if not out:
        raise NoData("event_window_daily's header names no window")
    return out


def days_between(a, b):
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(a, b, freq="D")]


def compute(params, in_dir=None):
    event = str(params.get("event", "uri_2021"))
    min_mwh = float(params.get("min_mwh", 1000))
    if event not in EVENTS:
        raise ValueError(f"no event named {event}")
    w = windows(in_dir)
    if event not in w:
        raise NoData(f"event_window_daily's header has no window for {event}")
    a, b = w[event]
    window = days_between(a, b)
    base = []
    for back in (364, 728):
        base += days_between(pd.Timestamp(a) - pd.Timedelta(days=back), pd.Timestamp(b) - pd.Timedelta(days=back))
    wanted = {d + "T00:00:00Z" for d in window + base}
    d = read_table("eia930_daily_interchange", in_dir, usecols=["ts_utc", "value", "ba", "x_to_ba"], keep=lambda c: c["ts_utc"].isin(wanted))
    if d.empty:
        raise NoData(f"eia930_daily_interchange holds none of {event}'s days")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["value"])
    d = d[~d["ba"].isin(REGIONS) & ~d["x_to_ba"].isin(REGIONS)]
    d["day"] = d["ts_utc"].str[:10]
    # each pair's flow, from a to b (a < b), as the mean of the two sides' reports where both are held: a's report of
    # a->b and the negative of b's report of b->a
    d["a"] = d[["ba", "x_to_ba"]].min(axis=1)
    d["b"] = d[["ba", "x_to_ba"]].max(axis=1)
    d["flow_ab"] = np.where(d["ba"] == d["a"], d["value"], -d["value"])
    pairs = d.groupby(["a", "b", "day"]).agg(flow=("flow_ab", "mean"), sides=("flow_ab", "size"), lo=("flow_ab", "min"), hi=("flow_ab", "max")).reset_index()
    both = pairs[pairs["sides"] >= 2]
    disagree = both[(both["hi"] - both["lo"]).abs() > 0.1 * both[["lo", "hi"]].abs().max(axis=1).clip(lower=1.0)]
    n_pair_days, n_both, n_disagree = int(len(pairs)), int(len(both)), int(len(disagree))
    a_side = pairs.rename(columns={"a": "ba"})[["ba", "day", "flow"]]
    b_side = pairs.rename(columns={"b": "ba"})[["ba", "day", "flow"]].assign(flow=lambda x: -x["flow"])
    net = pd.concat([a_side, b_side]).groupby(["ba", "day"], as_index=False)["flow"].sum().rename(columns={"flow": "value"})   # exports minus imports
    base_set, win_set = set(base), set(window)
    rows = []
    for ba, g in net.groupby("ba"):
        gb, gw = g[g["day"].isin(base_set)], g[g["day"].isin(win_set)]
        if gb.empty or gw.empty:
            continue
        nb, nw = float(gb["value"].mean()), float(gw["value"].mean())
        if abs(nb) < min_mwh and abs(nw) < min_mwh:
            flip = "small"
        elif nb < 0 <= nw:
            flip = "import_to_export"
        elif nb >= 0 > nw:
            flip = "export_to_import"
        else:
            flip = "same"
        rows.append({"event": event, "ba": ba, "name": NAMES.get(ba, ba.upper()), "baseline_net_mwh_day": nb, "event_net_mwh_day": nw,
                     "swing_mwh_day": nw - nb, "baseline_days": int(len(gb)), "event_days": int(len(gw)), "flip": flip,
                     "event_grid": int(ba == GRID_OF[event])})
    rows.sort(key=lambda r: -abs(r["swing_mwh_day"]))
    meta = {"event": event, "window": [a, b], "baseline_days": sorted(base), "n_window_days": len(window), "min_mwh": min_mwh,
            "n_rows_read": int(len(d)), "n_pair_days": n_pair_days, "n_pair_days_both_sides": n_both, "n_pair_days_disagree": n_disagree}
    return rows, meta


def numbers_from_rows(rows, params=None):
    to_exp = [r for r in rows if r["flip"] == "import_to_export"]
    to_imp = [r for r in rows if r["flip"] == "export_to_import"]
    grid = next((r for r in rows if r["event_grid"]), None)
    big_exp = max(to_exp, key=lambda r: r["event_net_mwh_day"], default=None)
    big_imp = min(to_imp, key=lambda r: r["event_net_mwh_day"], default=None)
    n = {"n_bas": len(rows), "n_to_export": len(to_exp), "n_to_import": len(to_imp), "n_same": sum(1 for r in rows if r["flip"] == "same"),
         "n_small": sum(1 for r in rows if r["flip"] == "small"),
         "grid_ba": grid["ba"] if grid else None, "grid_name": grid["name"] if grid else None,
         "grid_baseline": grid["baseline_net_mwh_day"] if grid else None, "grid_event": grid["event_net_mwh_day"] if grid else None,
         "grid_event_days": grid["event_days"] if grid else None, "grid_baseline_days": grid["baseline_days"] if grid else None,
         "big_exp_name": big_exp["name"] if big_exp else None, "big_exp_baseline": big_exp["baseline_net_mwh_day"] if big_exp else None,
         "big_exp_event": big_exp["event_net_mwh_day"] if big_exp else None,
         "big_imp_name": big_imp["name"] if big_imp else None, "big_imp_baseline": big_imp["baseline_net_mwh_day"] if big_imp else None,
         "big_imp_event": big_imp["event_net_mwh_day"] if big_imp else None,
         "biggest_swing_name": rows[0]["name"] if rows else None, "biggest_swing": rows[0]["swing_mwh_day"] if rows else None,
         "biggest_swing_baseline": rows[0]["baseline_net_mwh_day"] if rows else None, "biggest_swing_event": rows[0]["event_net_mwh_day"] if rows else None}
    for k in ("grid_baseline", "grid_event", "big_exp_baseline", "big_exp_event", "big_imp_baseline", "big_imp_event"):
        n[k + "_abs"] = abs(n[k]) if n[k] is not None else None   # the callouts print a flow without its sign and say the side in words
    return n


def flow_side(v):
    return "not held" if v is None else ("imported" if v < 0 else "exported")


def chart(rows, meta):
    shown = [r for r in rows if r["flip"] in ("import_to_export", "export_to_import") or r["event_grid"]][:14]
    x = [r["name"] for r in shown]
    return {"kind": "bars_free", "x": x, "x_label": f"Balancing authorities that flipped, and the event's grid; {EVENTS[meta['event']]}",
            "series": [{"name": "Baseline (same days, 1 and 2 years earlier)", "type": "bar", "unit": "MWh a day, net exports",
                        "values": [r["baseline_net_mwh_day"] for r in shown]},
                       {"name": f"The event, {meta['window'][0]} to {meta['window'][1]}", "type": "bar", "unit": "MWh a day, net exports",
                        "values": [r["event_net_mwh_day"] for r in shown]}],
            "y_left_label": "net exports, MWh a day (below zero: net imports)", "decimals": 0, "flip": [r["flip"] for r in shown]}


def card(rows, params, meta):
    n = numbers_from_rows(rows, params)
    ev = meta["event"]
    words = EVENTS[ev]
    if n["n_to_export"] == 0 and n["n_to_import"] == 0:
        sub = f"Nobody changed sides: no authority flipped during {words}"
    elif n["n_to_export"] >= n["n_to_import"]:
        sub = f"{n['n_to_export']} authorities turned exporter during {words}, {n['n_to_import']} turned importer"
    else:
        sub = f"More authorities turned to importing than to exporting during {words}"
    g_base, g_ev = n["grid_baseline"], n["grid_event"]
    grid_words = ""
    if g_base is not None:
        side = "a net importer" if g_ev < 0 else "a net exporter"
        grid_words = (f"{n['grid_name']} itself went from {fmt(g_base, 0)} MWh a day on the baseline to {fmt(g_ev, 0)} in the window "
                      f"({side} during the event; positive is net export). ")
    exp_words = (f"The largest new exporter was {n['big_exp_name']}: {fmt(n['big_exp_baseline'], 0)} MWh a day on the baseline, {fmt(n['big_exp_event'], 0)} in the window. "
                 if n["big_exp_name"] else "")
    imp_words = (f"The largest new importer was {n['big_imp_name']}: {fmt(n['big_imp_baseline'], 0)} on the baseline, {fmt(n['big_imp_event'], 0)} in the window. "
                 if n["big_imp_name"] else "")
    why = (f"Of the {fmt(n['n_bas'], 0)} balancing authorities with flows on both the window and its baseline, {fmt(n['n_to_export'], 0)} flipped from net importing to "
           f"net exporting during {words} and {fmt(n['n_to_import'], 0)} the other way; {fmt(n['n_same'], 0)} kept their sign and {fmt(n['n_small'], 0)} moved under "
           f"{fmt(meta['min_mwh'], 0)} MWh a day both ways. {grid_words}{exp_words}{imp_words}The biggest swing of all was {n['biggest_swing_name']}'s, "
           f"{fmt(n['biggest_swing'], 0)} MWh a day. A flip says who sent power the other way when it was scarce; it does not say why, and a tie-line's limit, a "
           "neighbour's own emergency or a scheduled outage can each move a sign.")
    foot = (f"Data: eia930_daily_interchange, EIA-930's daily interchange by pair of balancing authorities (EIA's Eastern-time days; a positive value is "
            f"power from the row's authority to its neighbour), {fmt(meta['n_rows_read'], 0)} rows read; EIA's region rows (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, "
            f"NY, SE, SW, TEN, TEX, US48) left out. A pair's flow on a day is the mean of its two sides' reports where both are held ({fmt(meta['n_pair_days'], 0)} "
            f"pair-days, {fmt(meta['n_pair_days_both_sides'], 0)} with both sides, {fmt(meta['n_pair_days_disagree'], 0)} of those with the sides more than a tenth apart); "
            f"an authority's day is the sum over its pairs (exports minus imports). Window: {meta['window'][0]} to {meta['window'][1]} ({meta['n_window_days']} days), from event_window_daily's header "
            f"(docs/methods/events.md). Baseline: the same calendar days 364 and 728 days earlier, {len(meta['baseline_days'])} days, averaged where held. "
            f"Flip: the sign of the baseline mean against the sign of the window mean; an authority under {fmt(meta['min_mwh'], 0)} MWh a day on both is "
            "'small'. Every authority with days on both sides is a row; the chart shows the flipped ones and the event's grid, largest swing first, at most 14.")
    return {
        "id": NAME, "title": TITLE, "kind": KIND, "subtitle": sub,
        "params": {"event": ev, "min_mwh": meta["min_mwh"]},
        "inputs_words": {"event": words, "min_mwh": f"{fmt(meta['min_mwh'], 0)} MWh a day"},
        "chart": chart(rows, meta),
        "callouts": [
            callout("Authorities that flipped", "to exporting", f"{fmt(n['n_to_export'], 0)}", "to importing", f"{fmt(n['n_to_import'], 0)}"),
            callout(f"{n['grid_name']} net flow, MWh a day", "baseline", f"{fmt(n['grid_baseline_abs'], 0)} {flow_side(g_base)}", "the event", f"{fmt(n['grid_event_abs'], 0)} {flow_side(g_ev)}"),
            callout(f"Largest new exporter: {n['big_exp_name'] or 'none'}", "baseline", f"{fmt(n['big_exp_baseline_abs'], 0)} {flow_side(n['big_exp_baseline'])}",
                    "the event", f"{fmt(n['big_exp_event_abs'], 0)} {flow_side(n['big_exp_event'])}"),
        ],
        "why": why, "footnote": foot, "numbers": n,
        "source_line": "Source: EIA-930 (Hourly Electric Grid Monitor), daily interchange; ERW tables " + ", ".join(TABLES) + ".",
        "tables": TABLES, "computed_at": now_iso(), "method": METHOD_URL,
        "csv_header": [f"Energy Research Warehouse (ERW): finding {NAME}, {TITLE}", f"Computed {now_iso()} by warehouse/analysis/findings/{NAME}.py; method {METHOD_URL}",
                       "Rows: one per balancing authority: mean net exports (MWh a day) over the baseline days and over the event's window, the swing, the days held, "
                       "and the flip (import_to_export, export_to_import, same, small)",
                       "Sources: " + ", ".join(TABLES)],
    }


def stata(params):
    V = ["baseline_net_mwh_day", "event_net_mwh_day", "swing_mwh_day", "baseline_days", "event_days", "event_grid"]
    return do_file([
        f"* ERW finding {NAME}: {TITLE}. Reproduces the card's counts and flows from {CSV_NAME}.",
        "clear all",
        f'import delimited "{CSV_NAME}", varnames(1) stringcols(_all) clear',
        *do_destring(V),
        *do_sentinels(V),
        "gsort -swing_mwh_day",
        "tab flip",
        ["foreach v in baseline_net_mwh_day event_net_mwh_day {",
         "    tabstat `v', by(flip) statistics(mean min max n) format(%12.0f)",
         "}"],
        "list name baseline_net_mwh_day event_net_mwh_day flip if flip != \"same\" & flip != \"small\", noobs",
    ])


SOURCE_PATH = os.path.abspath(__file__)
