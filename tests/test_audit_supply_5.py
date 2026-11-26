"""Session 10222 (chain 710, the supply audit, finding 4): the production rows' source line read "Short-Term Energy
Outlook, history only", though the newest months the table keeps are EIA's estimates and move with each Outlook (up to
3.94 percent between two monthly copies). The builder's source words now say so; they reach the page at the next build
of site/data/supply.json. Words only.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


WORDS = "EIA, Short-Term Energy Outlook, without its forecast months: the newest months are EIA's estimates, revised each month (eia_basin_production_monthly)"


def test_the_builder_says_it():
    b = read("warehouse", "derived", "supply_page.py")
    assert WORDS in b
    assert "Short-Term Energy Outlook, history only" not in b


def test_the_page_still_finds_the_table_in_the_words():
    # the page lists the tables to download from the bracketed names of the sources (app/supply/page.tsx, TABLES)
    assert re.findall(r"\(([a-z0-9]+(?:_[a-z0-9]+)+)\)", WORDS) == ["eia_basin_production_monthly"]
    # the source keeps its place among the file's sorted sources (between CFTC's and EIA's gas trade)
    assert "CFTC" < WORDS < "EIA, U.S. natural gas"


def test_the_connector_keeps_the_forecast_out():
    c = read("warehouse", "connectors", "eia_supply.py")
    assert re.search(r"^HISTORY_LAG = 3\b", c, re.M)


def test_the_note_says_it():
    assert "**The newest months move each month (session 10222, the supply audit, finding 4).**" in read("docs", "methods", "supply_and_trade.md")
