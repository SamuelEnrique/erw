"""Each table's license and live-set window, for license(), tables() and the held-table refusal.

Energy Research Warehouse (ERW), session 1001 (chain 070, docs/methods/packages.md). One row a table: the ERW's verdict
(public, internal or unsettled: docs/licenses.md, "Every table", session 378's rule), the "license needed" status and
its day (warehouse/metadata/license_status.csv), the publishers whose terms decide it (license_tables.csv), one
sentence a reader can act on, and the live set's window for it (warehouse/supabase/live_set.yaml).

Inside a clone of the repository these are read from the repository's own files, so they are as new as the checkout.
An installed package without the repository reads the copy shipped with it (erw/data/tables.csv), which
`python package/tools/build_tables.py` writes from the same files when the package is built.
"""

import csv
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

FIELDS = ["table", "verdict", "status", "status_from", "decided_by", "publishers", "words", "live_window"]
VERDICTS = ("public", "internal", "unsettled")
LICENSES_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md"

_ROWS: Optional[Dict[str, Dict[str, str]]] = None
_FROM: Optional[str] = None


def repo_root() -> Optional[Path]:
    """The clone this package runs in, if any: the folder holding docs/licenses.md and warehouse/metadata."""
    starts = [Path(__file__).resolve(), Path.cwd().resolve()]
    env = os.environ.get("ERW_DATA_DIR")
    if env:
        starts.insert(0, Path(env).expanduser().resolve())
    for base in starts:
        for parent in [base, *base.parents]:
            if (parent / "docs" / "licenses.md").is_file() and (parent / "warehouse" / "metadata" / "coverage.csv").is_file():
                return parent
    return None


def _md_rows(path: Path) -> Dict[str, List[str]]:
    """docs/licenses.md, section "Every table": {table: [cells]} (Table, Publishers, Verdict today, Decided by, Not read,
    Flag, Flag and verdict, If the ERW sells anything, ERW verdict)."""
    out, on = {}, False
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            on = ln.strip() == "## Every table"
            continue
        m = re.match(r"^\| `([a-z0-9_]+)` \|", ln) if on else None
        if m:
            out[m.group(1)] = [c.strip() for c in ln.strip().strip("|").split("|")]
    return out


def _csv(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def words(verdict: str, status: str, status_from: str, decided_by: str, not_read: str, today: str) -> str:
    """One sentence a reader can act on, from the license record's own cells."""
    if verdict == "public":
        return "Public: every publisher's terms the ERW read allow it to be shared, with credit to the publisher."
    if status == "license needed":
        who = decided_by or "a publisher"
        return (f"{who}'s terms ask for written permission, which the ERW has not recorded "
                f"(license needed since {status_from}).")
    if verdict == "internal":
        why = f" ({today})" if today and today != "may be public" else ""
        return f"The ERW holds it for its own use only{why}; it is never redistributed."
    who = re.sub(r";? and \d+ more$", " and others", not_read) if not_read else "a publisher"
    return f"The terms of {who} have not been read or settled, so the ERW does not redistribute it until they are."


def _live_rules(root: Path):
    try:
        import yaml
    except ImportError:
        return None
    path = root / "warehouse" / "supabase" / "live_set.yaml"
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def live_window(table: str, live) -> str:
    """'whole', '<N> days', 'some rows' or 'none', as warehouse/supabase/load.py's live_rule and live_set.yaml's select
    and catalogue_hold give it. A table held out of the public catalogue (catalogue_hold, review_hold) is 'none'."""
    if not live:
        return ""
    if table in set(live.get("catalogue_hold") or []) or table in set(live.get("review_hold") or []):
        return "none"
    sel = (live.get("select") or {}).get(table) or {}
    days = sel.get("days")
    if any(re.match(p, table) for p in live.get("full") or []):
        if days:
            return f"{days} days"
        return "some rows" if (sel.get("include") or sel.get("exclude")) else "whole"
    rec = live.get("recent") or {}
    if any(re.match(p, table) for p in rec.get("tables") or []):
        return f"{days or rec.get('days')} days"
    return "none"


def build(root: Path) -> List[Dict[str, str]]:
    """Every table of coverage.csv with its license row, from the repository's files."""
    meta = root / "warehouse" / "metadata"
    md = _md_rows(root / "docs" / "licenses.md")
    status = {r["table"]: r for r in _csv(meta / "license_status.csv")}
    pubs = {r["table"]: r["publishers"] for r in _csv(meta / "license_tables.csv")}
    live = _live_rules(root)
    out = []
    for c in _csv(meta / "coverage.csv"):
        t = c["table"]
        cells = md.get(t)
        verdict = cells[-1] if cells and cells[-1] in VERDICTS else ""
        if not verdict:   # a table the record has not reached yet: its flag, which a later read may tighten
            verdict = "internal" if c.get("license") == "internal" else "unsettled"
        s = status.get(t, {})
        st = s.get("status", "")
        decided = s.get("publishers", "") or (cells[3] if cells else "")
        out.append({"table": t, "verdict": verdict, "status": st, "status_from": s.get("from", "") if st else "",
                    "decided_by": decided, "publishers": pubs.get(t, ""),
                    "words": words(verdict, st, s.get("from", ""), decided, cells[4] if cells else "",
                                   cells[2] if cells else ""),
                    "live_window": live_window(t, live)})
    return out


def shipped_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "tables.csv"


def rows() -> Dict[str, Dict[str, str]]:
    """{table: row}: the clone's own record when the package runs in one, else the shipped copy."""
    global _ROWS, _FROM
    if _ROWS is None:
        root = repo_root()
        if root is not None:
            _ROWS, _FROM = {r["table"]: r for r in build(root)}, str(root)
        else:
            _ROWS, _FROM = {r["table"]: r for r in _csv(shipped_path())}, str(shipped_path())
    return _ROWS


def read_from() -> str:
    rows()
    return _FROM or ""


def reset() -> None:
    global _ROWS, _FROM
    _ROWS, _FROM = None, None


def write(path: Path, table_rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in sorted(table_rows, key=lambda r: r["table"]):
            w.writerow({k: r.get(k, "") for k in FIELDS})
