"""Session 10222 (chain 710, the supply audit, finding 3): the page's head reads "normal for the season", and the
five-year average is that only for a series with a season and no trend. The column's head now says on hover what the
average is and where it is not the season (production and positioning: a trend; New York's and SPP's oil burned for
power: a change of level within the five years). Words only.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def test_the_head_carries_the_words():
    page = read("site", "app", "supply", "page.tsx")
    assert '<th className="pr-3 text-right font-normal" title={FIVE_YEARS} data-head="avg5">Five-year average</th>' in page
    assert "It stands for normal at this point of the year only for a series with a season and no trend." in page
    assert "it measures the five years' trend, not the season" in page
    assert 'const METHOD = "/data/methods/supply_and_trade";' in page


def test_the_note_says_it():
    note = read("docs", "methods", "supply_and_trade.md")
    assert "**Where the five-year average is not the season (session 10222, the supply audit, finding 3).**" in note


def test_the_file_shows_a_trend_and_a_change_of_level():
    with open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8") as f:
        rows = {r["id"]: r for r in json.load(f)["rows"]}
    pm = rows.get("eia-ngmppm")
    if pm and pm.get("status") == "ok" and pm.get("avg5") and pm.get("year"):
        # production: far further above its five-year average than above the year before
        assert pm["avg5"]["pct"] > 2 * pm["year"]["pct"] > 0
    ny = rows.get("burn-nyiso-oil")
    if ny and ny.get("status") == "ok" and ny.get("avg5"):
        # a change of level: the five years run from near zero to far above the latest
        assert ny["avg5"]["lo"] < 0.1 and ny["avg5"]["hi"] > 10 and ny["last"]["v"] < 0.1
