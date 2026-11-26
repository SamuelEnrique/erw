"""Session 10222 (chain 710, the supply audit, finding 1, the figure; not for landing): what California's gas burned
for power and the seven grids' total would read if California were CAISO's own supply throughout, beside what the page
reads (EIA-930's hours before 16 December 2025, CAISO's own from it).

The test passes on main where the audit's evidence is in the checkout (docs/reviews/supply-model-audit-2026-11-26/:
burn_caiso.csv, EIA's California weeks restated from EIA-930's workbook; caiso_gas_own.csv, CAISO's own weeks restated
from caiso_fuel_supply_history and caiso_fuel_supply) and the page file holds the week ending 13 November 2026. It shows
the size of the effect; it changes nothing. For the owner: default, left as it is.
"""
import csv
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVIDENCE = os.path.join(ROOT, "docs", "reviews", "supply-model-audit-2026-11-26")


def weeks(name, fuel=None):
    path = os.path.join(EVIDENCE, name)
    if not os.path.exists(path):
        return None
    return {r["week_end"]: float(r["value"]) for r in csv.DictReader(open(path, encoding="utf-8")) if fuel is None or r.get("fuel") == fuel}


def rows():
    with open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)["rows"]}


def test_california_like_for_like():
    eia, own = weeks("burn_caiso.csv", "natural_gas"), weeks("caiso_gas_own.csv")
    r = rows().get("burn-caiso-natural-gas")
    if eia is None or own is None or not r or r.get("status") != "ok" or r["last"]["t"] != "2026-11-13":
        return
    v0, base = r["last"]["v"], r["year"]["t"]
    assert base == "2025-11-14"
    assert abs(r["year"]["v"] - eia[base]) < 1e-3              # the page's year before is EIA's week
    page_pct = 100 * (v0 - r["year"]["v"]) / r["year"]["v"]
    own_pct = 100 * (v0 - own[base]) / own[base]
    assert round(page_pct, 1) == -22.8                           # what the page prints
    assert round(own_pct, 1) == 0.8                              # on CAISO's own figures throughout
    five = ["2025-11-14", "2024-11-15", "2023-11-17", "2022-11-18", "2021-11-19"]
    avg_own = sum(own[w] for w in five) / 5
    assert abs(r["avg5"]["v"] - sum(eia[w] for w in five) / 5) < 1e-3
    assert round(avg_own, 2) == 1.73 and round(r["avg5"]["v"], 2) == 1.89


def test_the_total_like_for_like():
    eia, own = weeks("burn_caiso.csv", "natural_gas"), weeks("caiso_gas_own.csv")
    r = rows().get("burn-all-natural-gas")
    if eia is None or own is None or not r or r.get("status") != "ok" or r["last"]["t"] != "2026-10-30":
        return
    v0, yv, base = r["last"]["v"], r["year"]["v"], r["year"]["t"]
    alt = yv - eia[base] + own[base]
    assert round(100 * (v0 - yv) / yv, 2) == 3.49
    assert round(100 * (v0 - alt) / alt, 2) == 6.46


def test_the_week_of_the_join_is_built_on_both_sources():
    own = weeks("caiso_gas_own.csv")
    r = rows().get("burn-caiso-natural-gas")
    if own is None or not r or r.get("status") != "ok":
        return
    spark = dict(zip(r["spark"]["t"], r["spark"]["v"]))
    if "2025-12-19" not in spark:
        return
    # the week of 13 to 19 December 2025: three days of EIA's hours and four of CAISO's own in the page's value
    assert spark["2025-12-19"] > own["2025-12-19"] + 0.15
