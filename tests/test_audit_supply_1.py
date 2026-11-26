"""Session 10222 (chain 710, the supply audit, finding 1): California's gas burned for power on /supply is compared
across the change from EIA-930's hours to CAISO's own supply (16 December 2025), and EIA's California gas ran far above
CAISO's own in the years compared against. The page now says so on the hover of each crossing cell; no figure moves.

The words are checked in the page's code and the method note. The measure is checked on the audit's restated weeks
(docs/reviews/supply-model-audit-2026-11-26/burn_caiso.csv, EIA's side, and caiso_gas_own.csv, CAISO's own), where the
audit's evidence is in the checkout.
"""
import csv
import os
import re
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVIDENCE = os.path.join(ROOT, "docs", "reviews", "supply-model-audit-2026-11-26")


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def test_the_join_day_is_the_warehouse_join():
    lib = read("site", "lib", "supply.ts")
    join = re.search(r'^JOIN = "(\d{4}-\d{2}-\d{2})T08:00:00Z"', read("warehouse", "derived", "caiso_join.py"), re.M)
    assert join, "caiso_join.JOIN not found"
    # JOIN is midnight Pacific: its UTC day is the Pacific day the page names
    assert f'export const CAISO_JOIN_DAY = "{join.group(1)}";' in lib


def test_the_crossing_cells_carry_the_words():
    lib = read("site", "lib", "supply.ts")
    page = read("site", "app", "supply", "page.tsx")
    assert "export function joinWords(r: Row, base: string | null | undefined): string | null" in lib
    assert "so this comparison crosses a change of source." in lib
    assert "EIA's California natural gas ran about 30 percent above CAISO's own in 2024 and about 47 percent above it in 2025" in lib
    assert 'note={joinWords(r, r.year?.t)}' in page
    assert page.count("note={joinWords(r, null)}") == 1
    assert "const join = joinWords(row, null);" in page
    assert "joinWords" in page.split("export default")[0]


def test_the_note_says_it():
    note = read("docs", "methods", "supply_and_trade.md")
    assert "**California's comparisons cross a change of source (session 10222, the supply audit, finding 1).**" in note
    assert "30.5 percent above it in 2024 and 47.3 percent above it in 2025" in note


def test_eia_ran_above_caiso_own_in_2024_and_2025():
    eia_p, own_p = os.path.join(EVIDENCE, "burn_caiso.csv"), os.path.join(EVIDENCE, "caiso_gas_own.csv")
    if not (os.path.exists(eia_p) and os.path.exists(own_p)):
        return  # the audit's evidence is not in this checkout
    eia = {r["week_end"]: float(r["value"]) for r in csv.DictReader(open(eia_p, encoding="utf-8")) if r["fuel"] == "natural_gas"}
    own = {r["week_end"]: float(r["value"]) for r in csv.DictReader(open(own_p, encoding="utf-8"))}
    by = defaultdict(lambda: [0.0, 0.0])
    for w, v in eia.items():
        if w in own:
            by[w[:4]][0] += v
            by[w[:4]][1] += own[w]
    ratio = {y: a / b - 1 for y, (a, b) in by.items()}
    assert abs(ratio["2021"]) < 0.01 and abs(ratio["2022"]) < 0.01
    assert ratio["2024"] > 0.25 and ratio["2025"] > 0.40
    # the year before of the week ending 13 November 2026 (14 November 2025): EIA's against CAISO's own
    assert eia["2025-11-14"] > 1.25 * own["2025-11-14"]
