"""Session 10222 (chain 710, the supply audit, finding 5): the gas storage table's regions (EIA's five storage regions,
groups of states) share a name with the electricity regions of the section "The whole country" lower on the same page
(EIA's thirteen, groups of balancing authorities): the Midwest. The storage table's heading now says so on hover.
Words only.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def test_the_heading_carries_the_words():
    page = read("site", "app", "supply", "page.tsx")
    assert 'title={group.id === "gasstor" ? STORAGE_REGIONS : undefined}>{group.title}</h2>' in page
    assert "are the five storage regions of EIA's Weekly Natural Gas Storage Report, each a group of states." in page


def test_the_names_meet_on_one_page():
    with open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8") as f:
        storage = {r["at"] for r in json.load(f)["rows"] if r["group"] == "gasstor"}
    assert "Midwest" in storage
    country = read("site", "lib", "countryfiles.ts")   # the region names the section draws
    assert "Midwest" in country


def test_the_note_says_it():
    assert "**The storage regions are not the electricity regions (session 10222, the supply audit, finding 5).**" in read("docs", "methods", "supply_and_trade.md")
