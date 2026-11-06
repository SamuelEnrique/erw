"""Session 1191 (chain 089): the site's license hold and MISO's pause, for the Python chat (warehouse/chat/tools.py).

Energy Research Warehouse (ERW). The decisions of site/lib/license.ts (licenseNeeded, licenseByGrid, licenseByRow,
licenseHeldRow, gridOfEntity) and of site/lib/chat/tools.ts (misoOwn, heldGridOf, MISO_PAUSED), read from the same
file, site/data/license_status.json, so the two loops hold the same rows. The tools apply them only with ASK_HOLD=on
(read at each call): the site holds what it shows a visitor; whether the CLI, the owner's own reader of the
warehouse, holds them by default is for Samuel to rule (chain 089's session 1191 report). Pure: no network.
"""
import datetime as dt
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STATUS_PATH = os.path.join(ROOT, "site", "data", "license_status.json")
LICENSE_NEEDED = "license needed"
LICENSE_TITLE_SUFFIX = "the publisher's own page asks for permission; none is recorded yet"
ROW_LICENSE_COLUMN = "row_license"
GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}
GRID_NAME = {v: k for k, v in GRID_PREFIX.items()}
MISO_PAUSED = ("MISO is paused while its terms are reviewed (since 4 October 2026): this site shows no figure of MISO's own data. "
               "State no MISO figure: answer with not_in_warehouse true and say that MISO is 'paused while terms are reviewed'")
_status = None


def on(env=None):
    """Whether the tools hold what the site holds: ASK_HOLD=on."""
    return (os.environ if env is None else env).get("ASK_HOLD") == "on"


def tables():
    global _status
    if _status is None:
        with open(STATUS_PATH, encoding="utf-8") as f:
            _status = json.load(f)["tables"]
    return _status


def utc_day(now=None):
    return (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%d")


def license_needed(table, now=None):
    r = tables().get(table)
    return bool(r) and r.get("status") == LICENSE_NEEDED and utc_day(now) >= r.get("from", "")


def publishers(table):
    return list((tables().get(table) or {}).get("publishers") or [])


def title(table):
    who = publishers(table)
    return f"{'; '.join(who) if who else table}: {LICENSE_TITLE_SUFFIX}"


def by_row(table):
    return (tables().get(table) or {}).get("hold") == "row"


def by_grid(table):
    if by_row(table):
        return False
    who = publishers(table)
    return bool(who) and all(p in GRID_PREFIX for p in who)


def grid_name(prefix):
    return GRID_NAME.get(str(prefix).lower(), prefix)


def grid_prefix(name):
    return GRID_PREFIX.get(name) or (name.lower() if isinstance(name, str) and name.lower() in GRID_NAME else "")


def grid_of_entity(entity):
    if not entity or not isinstance(entity, str):
        return ""
    m = re.match(r"^([a-z0-9_-]+):(.*)$", entity, re.I | re.S)
    if not m:
        return ""
    head = m.group(1).lower()
    if head in GRID_NAME:
        return head
    q = re.match(r"^([a-z]+)_(?:load_)?queue$", head)
    if q and q.group(1) in GRID_NAME:
        return q.group(1)
    if head == "iso" and m.group(2).lower() in GRID_NAME:
        return m.group(2).lower()
    return ""


def held_row(table, entity=None, whole=False, now=None):
    """As licenseHeldRow: `whole` asks about the table whole (the site's entity undefined)."""
    if not license_needed(table, now):
        return False
    if by_row(table):
        return whole
    if not by_grid(table):
        return True
    if whole or entity is None:
        return True
    g = grid_of_entity(entity)
    return bool(g) and any(GRID_PREFIX.get(p) == g for p in publishers(table))


def miso_own(v):
    return isinstance(v, str) and re.match(r"^miso[:_]", v, re.I) is not None


def held_whole(table, now=None):
    """A table the site's chat refuses by name: held, and not by grid (tableInfo)."""
    return license_needed(table, now) and not by_grid(table)


def scope_grid(scope):
    if not scope:
        return ""
    if scope.get("market_prefix"):
        return grid_of_entity(f"{scope['market_prefix']}:x")
    return grid_prefix(scope.get("iso") or "")


def held_grid_of(table, entity=None, scope=None, now=None):
    """As heldGridOf: the grid whose held rows a query asks for, "" for none; MISO raises its pause (ValueError, the
    tools turn it into their own error)."""
    if not license_needed(table, now) or not by_grid(table):
        return ""
    g = grid_of_entity(entity) or ("" if entity else scope_grid(scope))
    if g == "miso":
        raise ValueError(MISO_PAUSED)
    return g if g and held_row(table, f"{g}:x", now=now) else ""
