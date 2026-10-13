"""The license status of the tables flagged public whose publisher asks for permission (session 207).

Energy Research Warehouse (ERW). warehouse/metadata/license_status.csv is written by `python scripts/licenses.py
status` from the licensing sweep's verdicts (docs/licenses.md): one row per table flagged public whose publisher's own
sentence asks for written permission or a paid license. The owner's ruling of 12 October 2026: from `from` (2026-10-21
since session 248: the public day moved from 20 October by the ruling of that night, docs/roadmap.md) such a table
shows "license needed" on the site, as PJM's prices do, unless a permission is recorded in its row (the columns
permission and permission_ref, filled by a person). Nothing changes before that day.

This module is the one reader of the file for the builders (the price board, warehouse/derived/board_page.py); the
site reads site/data/license_status.json through site/lib/license.ts, written by the same command.

    needed("iso_hub_prices_history")          True from the day in its row while no permission is recorded
    held_grids()                              {"ISO-NE", "MISO", "NYISO"}: the grids among the deciding publishers
"""
import csv
import datetime as dt
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILE = os.path.join(ROOT, "warehouse", "metadata", "license_status.csv")
NEEDED = "license needed"
GRIDS = {"CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP"}


def rows(path=None):
    path = path or FILE
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def today_utc():
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def needed(table, today=None, path=None):
    """True when the table's status is 'license needed' and today (UTC, YYYY-MM-DD) is on or after its `from` day."""
    today = today or today_utc()
    for r in rows(path):
        if r["table"] == table:
            return r["status"] == NEEDED and today >= r["from"]
    return False


def needed_tables(today=None, path=None):
    today = today or today_utc()
    return {r["table"] for r in rows(path) if r["status"] == NEEDED and today >= r["from"]}


def held_publishers(today=None, path=None):
    """The publishers whose sentence decides a table that is 'license needed' today."""
    today = today or today_utc()
    out = set()
    for r in rows(path):
        if r["status"] == NEEDED and today >= r["from"]:
            out |= {p for p in r["publishers"].split("; ") if p}
    return out


def held_grids(today=None, path=None):
    """The grid operators among them: a page that shows a grid's prices shows 'license needed' for these."""
    return held_publishers(today, path) & GRIDS


def note(publisher):
    """The words a held row carries, in the voice of PJM's (board_page.PJM_NOTE)."""
    return (f"{publisher}'s own terms ask for written permission to republish its data (docs/licenses.md), and none is "
            "recorded yet (warehouse/metadata/license_status.csv). Held, not shown, until a permission is recorded.")
