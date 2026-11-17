#!/usr/bin/env python3
"""ERW, ruling impact for /cost-of-power/battery/awards (session 7574, 17 November 2026).

The four lines marked "Changes a figure" under the awards page in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). The page's own rules are replication/battery_awards/replicate.py (imported): its page_figures() is
run on the public rows of replication/battery_awards/monthly_rows.csv as they are, with the 4-hour model put in the
2-hour model's place (line 1), and on one month at a time (line 2). Node spreads from warehouse/output/ercot_storage_node_basis.csv.

    .venv/Scripts/python.exe runs/ruling_impact/battery-awards_impact.py
"""
import csv
import importlib.util
import os
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "battery_awards", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)
_table = rep.table
OUT = os.path.join(ROOT, "warehouse", "output")   # the tables themselves: monthly_rows.csv holds only the 2-hour model in full


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.1f}%"


def with_model(prefix):
    """table() with the model of `prefix` (e.g. dayahead_4h_) put where the page reads dayahead_2h_."""
    def t(folder, name, entity):
        out, head = _table(folder, name, entity)
        if name == "battery_stack_monthly":
            out = {m: {**{k: v for k, v in g.items() if not k.startswith("dayahead_2h_")},
                       **{"dayahead_2h_" + k[len(prefix):]: v for k, v in g.items() if k.startswith(prefix)}} for m, g in out.items()}
        return out, head
    return t


def only_month(month):
    def t(folder, name, entity):
        out, head = _table(folder, name, entity)
        if name in ("ercot_storage_dam_awards_monthly", "ercot_storage_dam_offers_monthly", "battery_stack_monthly"):
            out = {m: g for m, g in out.items() if m == month}
        return out, head
    return t


base, _ = rep.page_figures(OUT)

# ---- line 1: a second column for the 4-hour battery
print("== line 1: 'The model's' column, one 2-hour battery on the day-ahead schedule (default), beside a 4-hour one (day-ahead, and with foresight)")
alt = {}
for prefix in ("dayahead_4h_", "foresight_4h_", "foresight_2h_"):
    rep.table = with_model(prefix)
    alt[prefix], _ = rep.page_figures(OUT)
rep.table = _table
months = sorted({k.split("|")[1] for k in base if k.startswith("month|") and k.endswith("|model_kw")})
for m in months:
    a = base[f"month|{m}|model_kw"]
    parts = [f"{p[:-1]} {alt[p].get(f'month|{m}|model_kw', float('nan')):.2f} ({pct(a, alt[p].get(f'month|{m}|model_kw', 0))})" for p in alt]
    print(f"{m}: awards {base[f'month|{m}|total_kw']:.2f}; model 2h day-ahead {a:.2f}; " + "; ".join(parts))
for y in sorted({k.split("|")[1] for k in base if k.startswith("year|") and k.endswith("model_whole_kw")}):
    a, s = base[f"year|{y}|model_whole_kw"], base[f"year|{y}|share_of_model_pct"]
    print(f"year {y}: model {a:.2f} USD/kW, awards' share {s:.1f}%; " + "; ".join(
        f"{p[:-1]} model {alt[p][f'year|{y}|model_whole_kw']:.2f} ({pct(a, alt[p][f'year|{y}|model_whole_kw'])}), share {alt[p][f'year|{y}|share_of_model_pct']:.1f}% ({alt[p][f'year|{y}|share_of_model_pct'] - s:+.1f} points)"
        for p in alt))
for k in ("offers|model_kw", "offers|gap_kw", "offers|part|never_kw", "offers|part|unawarded_kw", "offers|part|price_kw", "offers|five|model_kw_month", "offers|five|ratio", "rt|whole|model_kw"):
    if k in base:
        print(f"{k}: 2h {base[k]:.2f}; " + "; ".join(f"{p[:-1]} {alt[p].get(k, float('nan')):.2f} ({pct(base[k], alt[p].get(k, 0))})" for p in alt))

# ---- line 2: the gap's three parts for each month
print("\n== line 2: the gap between the model and the awards in three parts, over the months together (default) and for each month")
G = base.get("offers|model_kw") and rep.page_figures.__code__  # noqa: F841
print(f"together: model {base['offers|model_kw']:.2f}, awards {base['offers|awards_kw']:.2f}, gap {base['offers|gap_kw']:.2f}; "
      + "; ".join(f"{k} {base[f'offers|part|{k}_kw']:.2f} ({base[f'offers|part|{k}_share_pct']:.1f}%)" for k in ("never", "unawarded", "price")))
_, w = rep.page_figures(OUT)
for m in sorted(set(_table(OUT, "ercot_storage_dam_offers_monthly", rep.FLEET)[0])):
    rep.table = only_month(m)
    f, _ = rep.page_figures(OUT)
    rep.table = _table
    if "offers|gap_kw" not in f:
        print(f"{m}: not whole in the three tables, no parts")
        continue
    print(f"{m}: model {f['offers|model_kw']:.2f}, awards {f['offers|awards_kw']:.2f}, gap {f['offers|gap_kw']:.2f}; "
          + "; ".join(f"{k} {f[f'offers|part|{k}_kw']:.2f} ({f[f'offers|part|{k}_share_pct']:.1f}%, together {base[f'offers|part|{k}_share_pct']:.1f}%)" for k in ("never", "unawarded", "price")))

# ---- line 3: two durations of one fleet
print("\n== line 3: the fleet's duration in the decisions tip, the monitor's (default) and the EIA's beside it")
E, _ = _table(OUT, rep.INVENTORY, rep.INVENTORY_ENTITY)
print(f"the monitor: 31,500 MWh over 17,000 MW = {31500 / 17000:.2f} hours (Potomac Economics, June 2026; the tip says 'about 1.9')")
for m in sorted(E):
    if "battery_operating_mwh_per_mw" in E[m] and m >= "2025-12":
        print(f"   EIA-860M {m}: {E[m]['battery_operating_mwh_per_mw']:.2f} MWh per MW, {E[m].get('battery_operating_mw', float('nan')):,.1f} MW")

# ---- line 4: an A and B of two settlement points
print("\n== line 4: an A and B of two settlement points from ercot_storage_node_basis")
spreads = {}
with open(os.path.join(ROOT, "warehouse", "output", "ercot_storage_node_basis.csv"), encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(l for l in fh if not l.startswith("#")):
        if r["variable"] == "spread_node" and r["value"]:
            spreads[r["entity"]] = float(r["value"])
        if r["entity"] == "ercot:esr_nodes" and r["variable"] in ("spread_hub", "spread_node_median", "spread_node_p10", "spread_node_p90", "nodes_with_spread"):
            print(f"   the page's {r['variable']}: {r['value']} (week of {r['ts_utc'][:10]})")
v = sorted(spreads.values())
print(f"points with a spread: {len(v)}; lowest {v[0]:.2f}, highest {v[-1]:.2f}, median {statistics.median(v):.2f} USD/MWh: an A and B adds two cells the reader picks; no figure that stands moves")
