"""Energy Research Warehouse (ERW), session 7505 (chain 304): the replication of /cost-of-power/battery/awards.

Written from the method notes (docs/methods/battery_awards.md, which points to ercot_storage_dam_awards.md,
ercot_storage_dam_offers.md, ercot_storage_realtime.md and section 9 of battery_earns_algorithm.md) and the public
tables alone, not from the page's code. Standard library only. Three parts:

1. Every figure the page shows, recomputed from the five monthly tables the page reads, beside the figure the page's
   own functions give on the same rows (page_figures.json, written by site/scripts/battery-awards-figures.mjs). A figure
   passes when ours is within half the page's last shown digit.
2. The six cases of site/data/battery_awards_beside.json (the battery page's line beside ERCOT's real awards),
   recomputed from the same two monthly tables.
3. With --awards (and --sced, --hub): the monthly tables' own rows recomputed from ERCOT's disclosure, resource by
   resource and hour by hour (ercot_dam_esr_awards, ercot_sced_esr_hourly) and the real-time hub prices
   (ercot_all_hub_prices_history), so each figure is traced to ERCOT's files and not only to the derived tables.

    python replication/battery_awards/replicate.py --tables <dir of the warehouse's CSV tables>
        [--awards <ercot_dam_esr_awards.csv>] [--sced <ercot_sced_esr_hourly.csv>] [--hub <ercot_all_hub_prices_history.csv>]
        [--write]

Without --tables, parts 1 and 2 run on monthly_rows.csv beside this file: the rows of the five tables that the page
reads, copied by --write, so the replication runs on any copy of the repository. --write rewrites monthly_rows.csv,
page_figures.csv and source_rows.csv beside this file. Exit 0 when every figure passes, 1 when one
does not, 2 on bad input. Every table read here is public (ERCOT's terms, quoted in the tables' headers).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FLEET, MODEL, NODES = "ercot:esr_fleet", "ercot:HB_HUBAVG", "ercot:esr_nodes"
SERVICES = ["regup", "regdn", "rrs", "ecrs", "nspin"]
BANDS = [0, 25, 50, 100, 250, 1000]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# Differences the script knows of and names (key: reason); each is a numbered row of
# docs/reviews/battery-awards-faults-2026-11-16.md. Empty when every figure is inside half the last shown digit.
NAMED: dict[str, str] = {}
# Part 3's tolerance on a month's sum in US dollars. The table writes each sum to the cent and adds the services' rounded
# sums into the ancillary and the total; this script adds some 200,000 products a month in another order. On the first run
# 9 of 135 dollar sums stood 0.6 to 1.3 cents from the table's, on sums of USD 0.7 to 14.6 million, and every figure per
# MW (the figures the page reads) agreed to the table's fourth decimal. So a dollar sum agrees inside three cents.
CENTS = 0.03


ROWS = os.path.join(HERE, "monthly_rows.csv")   # the public rows the page reads, as --write copies them from the tables


def table(folder: str | None, name: str, entity: str) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    """One entity's rows of a series table: {month YYYY-MM: {variable: value}}, and the header's stamps. With no
    folder, from monthly_rows.csv beside this file."""
    out: dict[str, dict[str, float]] = defaultdict(dict)
    head: dict[str, str] = {}
    if folder is None:
        with open(ROWS, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["table"] == name and r["entity"] == entity:
                    out[r["ts_utc"][:7]][r["variable"]] = float(r["value"])
                    head["ts"] = r["ts_utc"][:10]
        return out, head
    with open(os.path.join(folder, name + ".csv"), encoding="utf-8", newline="") as f:
        lines = []
        for line in f:
            if line.startswith("#"):
                m = re.match(r"# Retrieved: (\S+)", line)
                if m and "retrieved" not in head:
                    head["retrieved"] = m.group(1)
                m = re.search(r"Operating days(?: held)?: (\d+)(?: matched)?, (\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)", line)
                if m and "first" not in head:
                    head["days"], head["first"], head["last"] = m.group(1), m.group(2), m.group(3)
                continue
            lines.append(line)
        for r in csv.DictReader(lines):
            if r["entity"] == entity and r["value"] != "":
                out[r["ts_utc"][:7]][r["variable"]] = float(r["value"])
                head["ts"] = r["ts_utc"][:10]
    return out, head


def held(g: dict[str, float] | None, need: list[str]) -> bool:
    return g is not None and all(k in g for k in need)


def whole(g: dict[str, float] | None, prefix: str = "") -> bool:
    return g is not None and prefix + "days_held" in g and g[prefix + "days_held"] == g.get(prefix + "days_in_month")


def page_figures(folder: str) -> tuple[dict[str, float], dict[str, str]]:
    """Every figure of the page, as the notes say it is computed. Keys as in page_figures.json."""
    A, _ = table(folder, "ercot_storage_dam_awards_monthly", FLEET)
    M, _ = table(folder, "battery_stack_monthly", MODEL)
    O, _ = table(folder, "ercot_storage_dam_offers_monthly", FLEET)
    T, _ = table(folder, "ercot_storage_rt_monthly", FLEET)
    B, bh = table(folder, "ercot_storage_node_basis", NODES)
    P = "dayahead_2h_"   # the model beside the awards: one 2-hour battery on the day-ahead schedule at the hub average
    f: dict[str, float] = {}
    w: dict[str, str] = {}

    # --- the head of the page: by month, by year, the share of hours with an energy award (battery_awards.md, sections 2 and 3)
    shown = [m for m in sorted(A) if held(A[m], ["days_held", "days_in_month", "revenue_energy_usd_per_mw", "revenue_ancillary_usd_per_mw", "revenue_total_usd_per_mw"])]
    for m in shown:
        a = A[m]
        f[f"month|{m}|days_held"], f[f"month|{m}|days_in_month"] = a["days_held"], a["days_in_month"]
        for k in ("resources", "mw"):
            if k in a:
                f[f"month|{m}|{k}"] = a[k]
        for k in ("energy", "ancillary", "total"):
            f[f"month|{m}|{k}_kw"] = a[f"revenue_{k}_usd_per_mw"] / 1000
        if m in M and P + "revenue_total_usd_per_mw" in M[m]:
            f[f"month|{m}|model_kw"] = M[m][P + "revenue_total_usd_per_mw"] / 1000
    for y in sorted({m[:4] for m in shown}):
        ms = [m for m in shown if m[:4] == y]
        full = [m for m in ms if whole(A[m])]
        f[f"year|{y}|days_held"] = sum(A[m]["days_held"] for m in ms)
        f[f"year|{y}|days_in_months"] = sum(A[m]["days_in_month"] for m in ms)
        for k in ("energy", "ancillary", "total"):
            f[f"year|{y}|{k}_kw"] = sum(A[m][f"revenue_{k}_usd_per_mw"] for m in ms) / 1000
        if full:
            awarded = sum(A[m]["revenue_total_usd_per_mw"] for m in full) / 1000
            f[f"year|{y}|awarded_whole_kw"] = awarded
            # the model stands beside the year only when it holds every one of those months whole
            if all(m in M and P + "revenue_total_usd_per_mw" in M[m] and whole(M[m], P) for m in full):
                model = sum(M[m][P + "revenue_total_usd_per_mw"] for m in full) / 1000
                f[f"year|{y}|model_whole_kw"] = model
                if model > 0:
                    f[f"year|{y}|share_of_model_pct"] = 100 * awarded / model
    both = [m for m in shown if A[m].get("resource_hours", 0) > 0 and "resource_hours_energy_award" in A[m]]
    if both:
        hours, hit = sum(A[m]["resource_hours"] for m in both), sum(A[m]["resource_hours_energy_award"] for m in both)
        f["share|energy_award_pct"], f["share|with_award"], f["share|resource_hours"] = 100 * hit / hours, hit, hours
    full = [m for m in shown if whole(A[m])]
    if full:
        n = A[full[-1]]
        w["newest|month"] = full[-1]
        if "resources" in n and "resources_with_award" in n:
            f["newest|resources_with_award"], f["newest|resources"] = n["resources_with_award"], n["resources"]

    # --- the offers section: the gap in three parts (ercot_storage_dam_offers.md, "The gap in three parts")
    need_o = ["days_held", "days_in_month", "mw", "limit_mwh", "limit_mwh_out", "limit_mwh_no_offer", "limit_mwh_no_offer_out", "limit_mwh_energy_offer", "limit_mwh_as_offer",
              "limit_mwh_award", "energy_offer_mwh", "energy_offer_mwh_at_clearing", "energy_sold_mwh", "as_offer_mwh", "as_award_mwh", "as_offer_mwh_unlisted"]
    need_o += [f"energy_offer_mwh_le_{b}" for b in BANDS] + [f"{s}_{k}" for s in SERVICES for k in ("offer_mwh", "offer_mwh_le_mcpc", "award_mwh", "unawarded_usd_per_mw")]
    need_a = ["revenue_total_usd_per_mw", "revenue_energy_usd_per_mw"] + [f"revenue_{s}_usd_per_mw" for s in SERVICES]
    need_m = [P + k for k in ["revenue_total_usd_per_mw", "revenue_energy_usd_per_mw", "discharged_mwh_per_mw"] + [f"revenue_{s}_usd_per_mw" for s in SERVICES]]
    first_offer = min(O) if O else None
    G = [m for m in sorted(A) if whole(A[m]) and first_offer and m >= first_offer and whole(O.get(m)) and whole(M.get(m), P)
         and held(A[m], need_a) and held(O[m], need_o) and held(M[m], need_m) and O[m]["mw"] > 0 and O[m]["limit_mwh"] > 0]
    if G:
        so = lambda k: sum(O[m][k] for m in G)                       # noqa: E731  a sum over the months
        per_mw = lambda k: sum(O[m][k] / O[m]["mw"] for m in G)      # noqa: E731  each month over its own MW, the months added
        days, lim = so("days_held"), so("limit_mwh")
        model = sum(M[m][P + "revenue_total_usd_per_mw"] for m in G) / 1000
        awards = sum(A[m]["revenue_total_usd_per_mw"] for m in G) / 1000
        gap = model - awards
        never = model * so("limit_mwh_no_offer") / lim               # an allocation: the model's average on the share that offered nothing
        e_model = sum(M[m][P + "revenue_energy_usd_per_mw"] for m in G)
        e_awards = sum(A[m]["revenue_energy_usd_per_mw"] for m in G)
        vm, va = sum(M[m][P + "discharged_mwh_per_mw"] for m in G) / days, per_mw("energy_sold_mwh") / days
        pm, pa = e_model / (vm * days), e_awards / (va * days)
        price = va * days * (pm - pa) / 1000
        rest = gap - never - price
        f["offers|model_kw"], f["offers|awards_kw"], f["offers|gap_kw"] = model, awards, gap
        for k, v in (("never", never), ("unawarded", rest), ("price", price)):
            f[f"offers|part|{k}_kw"], f[f"offers|part|{k}_share_pct"] = v, 100 * v / gap
        f["offers|no_offer_points"], f["offers|no_offer_out_points"] = 100 * so("limit_mwh_no_offer") / lim, 100 * so("limit_mwh_no_offer_out") / lim
        f["offers|awards_usd_per_mwh"], f["offers|model_usd_per_mwh"] = pa, pm
        f["offers|energy_offer_share_pct"] = 100 * so("limit_mwh_energy_offer") / lim
        f["offers|offered_mwh_per_mw_day"], f["offers|model_mwh_per_mw_day"] = per_mw("energy_offer_mwh") / days, vm
        f["offers|at_clearing_mwh_per_mw_day"], f["offers|sold_mwh_per_mw_day"] = per_mw("energy_offer_mwh_at_clearing") / days, va
        offered = so("energy_offer_mwh")
        f["offers|above_1000_pct"], f["offers|above_100_pct"] = 100 * (1 - so("energy_offer_mwh_le_1000") / offered), 100 * (1 - so("energy_offer_mwh_le_100") / offered)
        for b in BANDS + [None]:
            k, name = ("energy_offer_mwh", "any") if b is None else (f"energy_offer_mwh_le_{b}", f"le_{b}")
            f[f"offers|band|{name}|mwh_per_mw_day"], f[f"offers|band|{name}|share_pct"] = per_mw(k) / days, 100 * so(k) / offered
        of_offer = []
        for s in SERVICES:
            off, aw = so(f"{s}_offer_mwh"), so(f"{s}_award_mwh")
            a_kw = sum(A[m][f"revenue_{s}_usd_per_mw"] for m in G) / 1000
            m_kw = sum(M[m][P + f"revenue_{s}_usd_per_mw"] for m in G) / 1000
            of_offer.append(aw / off)
            f[f"offers|service|{s}|offer_share_pct"], f[f"offers|service|{s}|le_clearing_share_pct"] = 100 * off / lim, 100 * so(f"{s}_offer_mwh_le_mcpc") / lim
            f[f"offers|service|{s}|award_share_pct"], f[f"offers|service|{s}|award_of_offer_pct"] = 100 * aw / lim, 100 * aw / off
            f[f"offers|service|{s}|awards_kw"], f[f"offers|service|{s}|model_kw"], f[f"offers|service|{s}|gap_kw"] = a_kw, m_kw, m_kw - a_kw
            f[f"offers|service|{s}|unawarded_kw"] = so(f"{s}_unawarded_usd_per_mw") / 1000
        f["offers|award_of_offer_low_pct"], f["offers|award_of_offer_high_pct"] = 100 * min(of_offer), 100 * max(of_offer)
        f["offers|as_offer_share_of_limit_pct"], f["offers|as_award_share_of_limit_pct"] = 100 * so("as_offer_mwh") / lim, 100 * so("as_award_mwh") / lim
        w["offers|months"] = ",".join(G)

    # --- the real-time section (ercot_storage_realtime.md, "The month" and "One week at the nodes")
    R = [m for m in sorted(T) if held(T[m], ["days_held", "days_in_month", "revenue_da_usd_per_mw", "revenue_rt_deviation_hub_usd_per_mw", "revenue_market_hub_usd_per_mw"])]
    if R:
        f["rt|days_held"] = sum(T[m]["days_held"] for m in R)
        full = [m for m in R if whole(T[m])]
        model_ok = lambda m: m in M and P + "revenue_total_usd_per_mw" in M[m] and whole(M[m], P)   # noqa: E731
        if full:
            f["rt|whole|dayahead_kw"] = sum(T[m]["revenue_da_usd_per_mw"] for m in full) / 1000
            f["rt|whole|deviation_kw"] = abs(sum(T[m]["revenue_rt_deviation_hub_usd_per_mw"] for m in full)) / 1000   # the page writes "adds" or "takes off"
            f["rt|whole|market_kw"] = sum(T[m]["revenue_market_hub_usd_per_mw"] for m in full) / 1000
            if all(model_ok(m) for m in full):
                f["rt|whole|model_kw"] = sum(M[m][P + "revenue_total_usd_per_mw"] for m in full) / 1000
        for m in R:
            t = T[m]
            f[f"rt|month|{m}|days_held"], f[f"rt|month|{m}|days_in_month"] = t["days_held"], t["days_in_month"]
            if "mw" in t:
                f[f"rt|month|{m}|mw"] = t["mw"]
            f[f"rt|month|{m}|dayahead_kw"], f[f"rt|month|{m}|deviation_kw"] = t["revenue_da_usd_per_mw"] / 1000, t["revenue_rt_deviation_hub_usd_per_mw"] / 1000
            f[f"rt|month|{m}|market_kw"] = t["revenue_market_hub_usd_per_mw"] / 1000
            if whole(t) and model_ok(m):
                mk = M[m][P + "revenue_total_usd_per_mw"]
                f[f"rt|month|{m}|model_kw"] = mk / 1000
                if mk > 0:
                    f[f"rt|month|{m}|share_of_model_pct"] = 100 * t["revenue_market_hub_usd_per_mw"] / mk
            for k, name in (("rt_discharge_mwh", "discharged_mwh"), ("da_sold_mwh", "sold_mwh"), ("rt_charge_mwh", "charged_mwh"), ("da_bought_mwh", "bought_mwh")):
                if k in t:
                    f[f"rt|month|{m}|{name}"] = t[k]
            if t.get("rt_discharge_mwh", 0) > 0 and "da_sold_mwh" in t:
                f[f"rt|month|{m}|sold_of_discharged_pct"] = 100 * t["da_sold_mwh"] / t["rt_discharge_mwh"]
            if "da_node_minus_hub_sold" in t and "da_node_minus_hub_bought" in t:
                f[f"rt|month|{m}|node_less_hub_sold"], f[f"rt|month|{m}|node_less_hub_bought"] = t["da_node_minus_hub_sold"], t["da_node_minus_hub_bought"]
        if all(held(T[m], ["rt_discharge_mwh", "rt_charge_mwh", "da_sold_mwh", "da_bought_mwh"]) for m in R):
            st = lambda k: sum(T[m][k] for m in R)   # noqa: E731
            f["rt|energy|days"] = st("days_held")
            f["rt|energy|discharged_mwh"], f["rt|energy|sold_mwh"], f["rt|energy|charged_mwh"], f["rt|energy|bought_mwh"] = st("rt_discharge_mwh"), st("da_sold_mwh"), st("rt_charge_mwh"), st("da_bought_mwh")
            f["rt|energy|sold_of_discharged_pct"] = 100 * st("da_sold_mwh") / st("rt_discharge_mwh")
            f["rt|energy|discharged_mwh_per_mw_day"] = sum(T[m]["rt_discharge_mwh"] / T[m]["mw"] for m in R) / st("days_held")
            if all(held(T[m], ["intervals", "intervals_priced"]) for m in R) and st("intervals_priced") != st("intervals"):
                f["rt|energy|priced_share_pct"] = 100 * st("intervals_priced") / st("intervals")
        for s in SERVICES:
            if all(held(T[m], [f"as_rt_{s}_mwh", f"as_da_{s}_mwh", f"as_imbalance_{s}_mwh"]) for m in R):
                f[f"rt|as|{s}|real_time_mwh"], f[f"rt|as|{s}|day_ahead_mwh"] = sum(T[m][f"as_rt_{s}_mwh"] for m in R), sum(T[m][f"as_da_{s}_mwh"] for m in R)
                f[f"rt|as|{s}|imbalance_mwh"] = sum(T[m][f"as_imbalance_{s}_mwh"] for m in R)
    if B:
        b = next(iter(B.values()))
        w["basis|from"] = bh.get("ts", "")
        for k, name in (("nodes", "nodes"), ("nodes_with_spread", "nodes_with_spread"), ("whole_days", "whole_days"), ("spread_hub", "spread_hub"), ("spread_node_median", "spread_node_median"),
                        ("spread_node_p10", "spread_node_p10"), ("spread_node_p90", "spread_node_p90"), ("nodes_spread_above_hub", "nodes_spread_above_hub"), ("mean_abs_difference_median", "mean_abs_difference_median")):
            if k in b:
                f[f"basis|{name}"] = b[k]
    return f, w


def beside(folder: str) -> dict[str, float]:
    """The six cases of site/data/battery_awards_beside.json (battery_earns_algorithm.md, section 9): ancillary only, the
    months both tables hold whole, USD per kW of power and month."""
    A, _ = table(folder, "ercot_storage_dam_awards_monthly", FLEET)
    M, _ = table(folder, "battery_stack_monthly", MODEL)
    out: dict[str, float] = {}
    for strat in ("foresight", "dayahead"):
        for dur in (2, 4, 8):
            p = f"{strat}_{dur}h_"
            ms = [m for m in sorted(A) if whole(A[m]) and whole(M.get(m), p) and "revenue_ancillary_usd_per_mw" in A[m] and p + "revenue_ancillary_usd_per_mw" in M[m]]
            if not ms:
                continue
            fleet = sum(A[m]["revenue_ancillary_usd_per_mw"] for m in ms) / 1000 / len(ms)
            model = sum(M[m][p + "revenue_ancillary_usd_per_mw"] for m in ms) / 1000 / len(ms)
            c = f"beside|{strat}_{dur}h|"
            out[c + "months"], out[c + "fleet"], out[c + "model"], out[c + "ratio"] = len(ms), fleet, model, model / fleet
    return out


def copy_rows(folder: str) -> int:
    """monthly_rows.csv: the rows of the five public tables that the page and the beside file read, from the awards
    table's first month on, so the replication and the do-file run on a copy with no warehouse."""
    keep = {"ercot_storage_dam_awards_monthly": FLEET, "ercot_storage_dam_offers_monthly": FLEET, "ercot_storage_rt_monthly": FLEET,
            "ercot_storage_node_basis": NODES, "battery_stack_monthly": MODEL}
    first = min(table(folder, "ercot_storage_dam_awards_monthly", FLEET)[0])
    model = re.compile(r"^(dayahead_2h_(days_held|days_in_month|discharged_mwh_per_mw|revenue_\w+_usd_per_mw)|(foresight|dayahead)_[248]h_(days_held|days_in_month|revenue_ancillary_usd_per_mw))$")
    n = 0
    with open(ROWS, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, lineterminator="\n")
        wr.writerow(["table", "entity", "variable", "ts_utc", "value", "unit", "retrieved"])
        for name, entity in keep.items():
            stamp = table(folder, name, entity)[1].get("retrieved", "")
            with open(os.path.join(folder, name + ".csv"), encoding="utf-8", newline="") as g:
                rows = [r for r in csv.DictReader(line for line in g if not line.startswith("#"))
                        if r["entity"] == entity and r["value"] != "" and (name == "ercot_storage_node_basis" or r["ts_utc"][:7] >= first)
                        and (name != "battery_stack_monthly" or model.match(r["variable"]))]
            for r in sorted(rows, key=lambda r: (r["variable"], r["ts_utc"])):
                wr.writerow([name, entity, r["variable"], r["ts_utc"], r["value"], r["unit"], stamp])
                n += 1
    return n


def decimals(shown: str) -> int:
    s = shown.replace(",", "")
    return len(s.split(".")[1]) if "." in s else 0


def compare(ours: dict[str, float], page: dict[str, str], digits: dict[str, int] | None = None) -> tuple[list[dict], int, int]:
    """Each figure of the page beside ours: inside half the page's last shown digit, or named."""
    rows, ok, named = [], 0, 0
    for k in sorted(set(ours) | set(page)):
        shown = page.get(k)
        mine = ours.get(k)
        if shown is None or mine is None:
            rows.append({"key": k, "page": shown if shown is not None else "", "ours": "" if mine is None else repr(mine), "difference": "", "verdict": "FAIL: on one side only"})
            continue
        d = digits[k] if digits and k in digits else decimals(str(shown))
        p = float(str(shown).replace(",", "").replace("+", ""))
        diff = mine - p
        inside = abs(diff) <= 0.5 * 10 ** (-d) + 1e-9
        verdict = "within half the last digit" if inside else (f"named: {NAMED[k]}" if k in NAMED else "FAIL")
        ok += inside
        named += (not inside) and k in NAMED
        rows.append({"key": k, "page": shown, "ours": f"{mine:.6f}".rstrip("0").rstrip("."), "difference": f"{diff:+.6f}", "verdict": verdict})
    return rows, ok, named


# ----------------------------------------------------------------------------------------------------------------------
# Part 3: the monthly tables' rows from ERCOT's disclosure

def central_day(ts: str) -> str:
    """The Central prevailing day of a UTC stamp YYYY-MM-DDTHH:MM:SSZ (US rule: daylight time from the second Sunday of
    March at 08:00 UTC to the first Sunday of November at 07:00 UTC)."""
    t = dt.datetime(int(ts[:4]), int(ts[5:7]), int(ts[8:10]), int(ts[11:13]), int(ts[14:16]))
    y = t.year
    mar = dt.datetime(y, 3, 8) + dt.timedelta(days=(6 - dt.datetime(y, 3, 8).weekday()) % 7, hours=8)
    nov = dt.datetime(y, 11, 1) + dt.timedelta(days=(6 - dt.datetime(y, 11, 1).weekday()) % 7, hours=7)
    return (t - dt.timedelta(hours=5 if mar <= t < nov else 6)).strftime("%Y-%m-%d")


def data_rows(path: str):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def num(v: str) -> float | None:
    return None if v == "" else float(v)


def from_disclosure(folder: str, awards_path: str, sced_path: str | None, hub_path: str | None) -> list[dict]:
    A, ah = table(folder, "ercot_storage_dam_awards_monthly", FLEET)
    T, th = table(folder, "ercot_storage_rt_monthly", FLEET)
    a_first, a_last = ah["first"], ah["last"]        # the operating days the monthly table was built on
    t_first, t_last = th.get("first", "9999"), th.get("last", "0000")
    AS = {"regup": (["x_regup_award_mw"], "x_regup_mcpc"), "regdn": (["x_regdn_award_mw"], "x_regdn_mcpc"),
          "rrs": (["x_rrspfr_award_mw", "x_rrsffr_award_mw", "x_rrsufr_award_mw"], "x_rrs_mcpc"),
          "ecrs": (["x_ecrs_award_mw"], "x_ecrs_mcpc"), "nspin": (["x_nonspin_award_mw"], "x_nonspin_mcpc")}
    s: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))   # month -> sums
    hsl: dict[str, dict[str, float]] = defaultdict(dict)                       # month -> resource -> highest HSL
    awarded: dict[str, set] = defaultdict(set)
    days: dict[str, set] = defaultdict(set)
    da_net: dict[tuple[str, str], float] = {}                                  # (resource, hour) -> MW sold less bought, the matched days
    rs: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))  # the real-time table's day-ahead side
    for r in data_rows(awards_path):
        day = central_day(r["ts_utc"])
        in_a, in_t = a_first <= day <= a_last, t_first <= day <= t_last
        if not (in_a or in_t):
            continue
        m, e = day[:7], r["entity"]
        q, p = num(r["x_energy_award_mw"]), num(r["x_energy_price_usd_per_mwh"])
        any_award = False
        usd_as = 0.0
        if in_a:
            days[m].add(day)
            s[m]["resource_hours"] += 1
            hsl[m][e] = max(hsl[m].get(e, float("-inf")), float(r["value"]))
        if q is not None and q != 0:
            if p is None:
                raise SystemExit(f"an energy award without its price: {e} {r['ts_utc']}")
            any_award = True
            side = "sold" if q > 0 else "bought"
            if in_a:
                s[m]["resource_hours_energy_award"] += 1
                s[m][f"energy_{side}_mwh"] += abs(q)
                s[m][f"energy_{side}_usd"] += abs(q) * p
            if in_t:
                da_net[(e, r["ts_utc"])] = q
                rs[m][f"da_{side}_mwh"] += abs(q)
                rs[m]["da_energy_usd"] += q * p
        for k, (cols, price) in AS.items():
            mw = sum(num(r[c]) or 0.0 for c in cols)
            if mw:
                c = num(r[price])
                if c is None:
                    raise SystemExit(f"an ancillary award without its price: {e} {r['ts_utc']} {k}")
                any_award = True
                usd_as += mw * c
                if in_a:
                    s[m][f"revenue_{k}_usd"] += mw * c
                if in_t:
                    rs[m][f"as_da_{k}_mwh"] += mw
        if in_t:
            rs[m]["da_as_usd"] += usd_as
        if any_award and in_a:
            awarded[m].add(e)
    out: list[dict] = []

    def put(tab: str, m: str, var: str, ours: float, theirs: float | None, tol: float):
        d = None if theirs is None else ours - theirs
        out.append({"table": tab, "month": m, "variable": var, "table_value": "" if theirs is None else repr(theirs), "from_disclosure": f"{ours:.4f}".rstrip("0").rstrip("."),
                    "difference": "" if d is None else f"{d:+.4f}", "verdict": "not in the table" if d is None else ("agrees" if abs(d) <= tol else "DIFFERS")})

    for m in sorted(s):
        x, a = s[m], A.get(m, {})
        mw = sum(hsl[m].values())   # each resource's highest limit of the month, awarded or not
        energy = x["energy_sold_usd"] - x["energy_bought_usd"]
        anc = sum(x[f"revenue_{k}_usd"] for k in AS)
        for var, v, tol in [("days_held", len(days[m]), 0), ("resources", len(hsl[m]), 0), ("resources_with_award", len(awarded[m]), 0), ("resource_hours", x["resource_hours"], 0),
                            ("resource_hours_energy_award", x["resource_hours_energy_award"], 0), ("mw", mw, 0.051), ("energy_sold_mwh", x["energy_sold_mwh"], 0.051),
                            ("energy_bought_mwh", x["energy_bought_mwh"], 0.051), ("revenue_energy_usd", energy, CENTS), ("revenue_ancillary_usd", anc, CENTS),
                            ("revenue_total_usd", energy + anc, CENTS), ("revenue_energy_usd_per_mw", energy / mw, 0.00051), ("revenue_ancillary_usd_per_mw", anc / mw, 0.00051),
                            ("revenue_total_usd_per_mw", (energy + anc) / mw, 0.00051)] + [(f"revenue_{k}_usd", x[f"revenue_{k}_usd"], CENTS) for k in AS]:
            put("ercot_storage_dam_awards_monthly", m, var, v, a.get(var), tol)

    if sced_path:
        prices: dict[str, float] = {}
        if hub_path:
            with open(hub_path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("ercot:HB_HUBAVG,spp_rtm,2026") or line.startswith("ercot:HB_HUBAVG,spp_rtm,2025-12"):
                        c = line.split(",", 4)
                        prices[c[2]] = float(c[3])
        rt: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        rt_days: dict[str, set] = defaultdict(set)
        ASR = {"regup": ["x_as_regup_mwh"], "regdn": ["x_as_regdn_mwh"], "rrs": ["x_as_rrspfr_mwh", "x_as_rrsffr_mwh", "x_as_rrsufr_mwh"], "ecrs": ["x_as_ecrs_mwh"], "nspin": ["x_as_nspin_mwh"]}

        def quarters(ts: str) -> list[str]:
            return [f"{ts[:14]}{q:02d}:00Z" for q in (0, 15, 30, 45)]

        for r in data_rows(sced_path):
            day = central_day(r["ts_utc"])
            if not (t_first <= day <= t_last):
                continue
            m = day[:7]
            rt_days[m].add(day)
            rt[m]["rt_discharge_mwh"] += float(r["x_discharge_mwh"])
            rt[m]["rt_charge_mwh"] += float(r["x_charge_mwh"])
            for k, cols in ASR.items():
                rt[m][f"as_rt_{k}_mwh"] += sum(float(r[c] or 0) for c in cols)
            if prices:
                for q, ts in zip(("x_net_q1_mwh", "x_net_q2_mwh", "x_net_q3_mwh", "x_net_q4_mwh"), quarters(r["ts_utc"])):
                    rt[m]["intervals"] += 1
                    if ts in prices:
                        rt[m]["intervals_priced"] += 1
                        rt[m]["output_hub_usd"] += float(r[q]) * prices[ts]
        if prices:
            for (e, ts), q in da_net.items():   # the day-ahead position, settled back: a quarter of the hour's award at each interval's price
                m = central_day(ts)[:7]
                rt[m]["position_hub_usd"] += sum(q / 4 * prices[t] for t in quarters(ts) if t in prices)
        for m in sorted(rt):
            x, t, d = rt[m], T.get(m, {}), rs[m]
            mw = t.get("mw")
            rows = [("days_held", len(rt_days[m]), 0), ("rt_discharge_mwh", x["rt_discharge_mwh"], 0.0051), ("rt_charge_mwh", x["rt_charge_mwh"], 0.0051),
                    ("da_sold_mwh", d["da_sold_mwh"], 0.051), ("da_bought_mwh", d["da_bought_mwh"], 0.051)]
            rows += [(f"as_rt_{k}_mwh", x[f"as_rt_{k}_mwh"], 0.051) for k in ASR] + [(f"as_da_{k}_mwh", d[f"as_da_{k}_mwh"], 0.051) for k in ASR]
            if mw:
                rows.append(("revenue_da_usd_per_mw", (d["da_energy_usd"] + d["da_as_usd"]) / mw, 0.00051))
                if prices:
                    dev = x["output_hub_usd"] - x["position_hub_usd"]
                    rows += [("revenue_rt_deviation_hub_usd_per_mw", dev / mw, 0.00051), ("revenue_market_hub_usd_per_mw", (d["da_energy_usd"] + d["da_as_usd"] + dev) / mw, 0.00051)]
            for var, v, tol in rows:
                put("ercot_storage_rt_monthly", m, var, v, t.get(var), tol)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tables", help="the folder of the warehouse's CSV tables; without it, monthly_rows.csv beside this file (the same rows, copied by --write)")
    ap.add_argument("--awards", help="ercot_dam_esr_awards.csv (part 3)")
    ap.add_argument("--sced", help="ercot_sced_esr_hourly.csv (part 3)")
    ap.add_argument("--hub", help="ercot_all_hub_prices_history.csv, for the real-time hub prices (part 3)")
    ap.add_argument("--write", action="store_true", help="rewrite page_figures.csv and source_rows.csv")
    a = ap.parse_args()
    if a.tables and not os.path.isfile(os.path.join(a.tables, "ercot_storage_dam_awards_monthly.csv")):
        print(f"no ercot_storage_dam_awards_monthly.csv in {a.tables}", file=sys.stderr)
        return 2
    if (a.awards or a.write) and not a.tables:
        print("--awards and --write need --tables (the tables' headers hold the days they were built on)", file=sys.stderr)
        return 2
    if a.write:
        print(f"monthly_rows.csv: {copy_rows(a.tables)} rows of the five public tables")
    page = json.load(open(os.path.join(HERE, "page_figures.json"), encoding="utf-8"))
    ours, words = page_figures(a.tables)
    rows, ok, named = compare(ours, page["figures"])
    bad = [r for r in rows if r["verdict"].startswith("FAIL")]
    for r in rows:
        if not r["verdict"].startswith("within"):
            print(f"  {r['key']}: page {r['page']}, ours {r['ours']} ({r['verdict']})")
    for k in ("newest|month", "basis|from"):
        if words.get(k) != page["words"].get(k):
            print(f"  {k}: page {page['words'].get(k)!r}, ours {words.get(k)!r} (FAIL)")
            bad.append({"key": k})
    print(f"The page: {ok} of {len(rows)} figures within half the page's last shown digit, {named} named, {len(bad)} failed")

    snap = json.load(open(os.path.join(ROOT, "site", "data", "battery_awards_beside.json"), encoding="utf-8"))
    snap_page = {f"beside|{c}|{k}": str(v[k]) for c, v in snap["cases"].items() for k in ("months", "fleet", "model", "ratio")}
    b_rows, b_ok, b_named = compare(beside(a.tables), snap_page)
    b_bad = [r for r in b_rows if r["verdict"].startswith("FAIL")]
    for r in b_rows:
        if not r["verdict"].startswith("within"):
            print(f"  {r['key']}: file {r['page']}, ours {r['ours']} ({r['verdict']})")
    print(f"The file battery_awards_beside.json: {b_ok} of {len(b_rows)} figures within half the file's last digit, {b_named} named, {len(b_bad)} failed")

    src: list[dict] = []
    if a.awards:
        src = from_disclosure(a.tables, a.awards, a.sced, a.hub)
        differs = [r for r in src if r["verdict"] == "DIFFERS"]
        for r in differs:
            print(f"  {r['table']} {r['month']} {r['variable']}: table {r['table_value']}, from the disclosure {r['from_disclosure']} ({r['difference']})")
        months = sorted({r["month"] for r in src})
        print(f"The monthly tables from ERCOT's disclosure: {len(src) - len(differs)} of {len(src)} rows agree, {len(months)} months ({months[0]} to {months[-1]}), {len(differs)} differ")
        bad += differs
    if a.write:
        with open(os.path.join(HERE, "page_figures.csv"), "w", encoding="utf-8", newline="") as f:
            wr = csv.DictWriter(f, ["key", "page", "ours", "difference", "verdict"], lineterminator="\n")
            wr.writeheader()
            wr.writerows(rows + b_rows)
        if src:
            with open(os.path.join(HERE, "source_rows.csv"), "w", encoding="utf-8", newline="") as f:
                wr = csv.DictWriter(f, ["table", "month", "variable", "table_value", "from_disclosure", "difference", "verdict"], lineterminator="\n")
                wr.writeheader()
                wr.writerows(src)
    return 1 if bad or b_bad else 0


if __name__ == "__main__":
    sys.exit(main())
