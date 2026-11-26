"""Session 10222 (chain 710, the supply audit, finding 2): NYISO's and ISO-NE's day-ahead cleared rows are held for a
license (the ERW holds the data and may not show it), but since the builder began writing their status itself
(session 7051) the page drew "licensed source needed", PJM's words for a source the ERW does not hold. Such a row now
reads "license needed", as the price board writes a held grid. Words only: neither row carries a figure.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def test_hold_rows_turns_a_held_licensed_row_into_held():
    lib = read("site", "lib", "supply.ts")
    assert 'if (g && r.status === "licensed" && /\\bheld\\b/i.test(r.note ?? "")) return { ...r, status: "held" };' in lib
    assert 'held: "license needed"' in lib and 'licensed: "licensed source needed"' in lib


def test_the_builder_writes_held_rows_with_a_note_that_says_held():
    b = read("warehouse", "derived", "supply_page.py")
    ls = read("warehouse", "metadata", "license_status.py")
    assert "Held, not shown, until a permission is recorded." in ls
    assert "held internal (its publisher's terms do not allow republishing): held, not shown." in b
    # PJM's own words say the ERW does not hold it, and do not say "held"
    pjm = re.search(r'"cleared\|PJM".*?"licensed", "([^"]+)"', b).group(1)
    assert not re.search(r"\bheld\b", pjm, re.I)


def test_the_page_file_holds_no_figure_in_a_held_row():
    with open(os.path.join(ROOT, "site", "data", "supply.json"), encoding="utf-8") as f:
        rows = {r["id"]: r for r in json.load(f)["rows"]}
    for rid in ("cleared-nyiso", "cleared-iso-ne"):
        r = rows.get(rid)
        if r is None:
            continue
        assert "last" not in r and "spark" not in r
        if r["status"] == "licensed":
            assert re.search(r"\bheld\b", r.get("note", ""), re.I), rid


def test_the_note_says_it():
    assert "**A held grid's row reads \"license needed\" (session 10222, the supply audit, finding 2).**" in read("docs", "methods", "supply_and_trade.md")
