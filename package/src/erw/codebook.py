"""The codebook: what each table's row is and what each of its columns means (chain 630, part D).

Energy Research Warehouse (ERW). Every table has a metadata file, warehouse/metadata/variables/<table>.yaml, and the
column names many tables share are defined once in warehouse/metadata/variables/_shared.yaml. Inside a clone of the
repository these files are read directly; an installed package without the repository reads the copy shipped with
it (erw/data/codebook.json, the public tables only), which `python package/tools/build_codebook.py` writes from the
same files when the package is built.

    erw.describe("ba_supply_monthly")     # the table: its row, keys, time, revisions, license, source, citation,
                                          # method note, and every column and variable with its meaning
    erw.variables("ba_supply_monthly")    # one row a column: name, label, unit, type, values, missing

"Variables" is the word Redivis and the codebook use for a table's columns. A series table's `variable` column
names what was measured; the values it takes, each with its unit, are describe(table)["variables"].
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from . import licenses

_SHARED: Optional[Dict[str, Dict]] = None
_SHIPPED: Optional[Dict] = None


def _dir() -> Optional[Path]:
    root = licenses.repo_root()
    if root is not None and (root / "warehouse" / "metadata" / "variables" / "_shared.yaml").is_file():
        return root / "warehouse" / "metadata" / "variables"
    return None


def shipped_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "codebook.json"


def _shipped() -> Dict:
    global _SHIPPED
    if _SHIPPED is None:
        p = shipped_path()
        _SHIPPED = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {"shared": {}, "tables": {}}
    return _SHIPPED


def _yaml(path: Path) -> Dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def shared() -> Dict[str, Dict]:
    """The shared column names, each with its label, type, unit, shapes, rule and missing meaning."""
    global _SHARED
    if _SHARED is None:
        d = _dir()
        _SHARED = _yaml(d / "_shared.yaml")["columns"] if d else _shipped().get("shared", {})
    return _SHARED


def names() -> List[str]:
    """The tables that have a metadata file."""
    d = _dir()
    if d:
        return sorted(p.stem for p in d.glob("*.yaml") if not p.stem.startswith("_"))
    return sorted(_shipped().get("tables", {}))


def raw(table: str) -> Optional[Dict]:
    """The table's metadata file as written (shared columns not yet filled in), or None."""
    d = _dir()
    if d:
        p = d / f"{table}.yaml"
        return _yaml(p) if p.is_file() else None
    return _shipped().get("tables", {}).get(table)


def _merged_column(c: Dict, sh: Dict[str, Dict]) -> Dict:
    out = {"name": c["name"], "shared": bool(c.get("shared"))}
    if c.get("shared") and c["name"] in sh:
        s = sh[c["name"]]
        out["label"] = s.get("label")
        out["unit"] = s.get("unit")
        out["rule"] = s.get("rule")
        if c.get("particular"):
            out["particular"] = c["particular"]
        out["missing_meaning"] = c.get("missing_meaning") or s.get("missing")
    else:
        out["label"] = c.get("label")
        out["unit"] = c.get("unit")
        out["missing_meaning"] = c.get("missing_meaning")
    out["type"] = c.get("type")
    out["values"] = c.get("values")
    out["missing_cells"] = c.get("missing_cells")
    out["source_name"] = c.get("source_name")
    out["documented_by"] = c.get("documented_by") or ("docs/datastandard.md" if out["shared"] else None)
    return out


def describe(table: str) -> Dict:
    """The table's codebook entry, with each shared column's definition filled in from _shared.yaml."""
    d = raw(table)
    if d is None:
        from .backends import ERWDataNotFound
        raise ERWDataNotFound(f"no codebook entry for {table!r}; erw.codebook.names() lists the {len(names())} there are")
    sh = shared()
    out = {k: v for k, v in d.items() if k not in ("columns", "variables")}
    out["columns"] = [_merged_column(c, sh) for c in d.get("columns") or []]
    if d.get("variables") is not None:
        out["variables"] = d.get("variables")
    return out


def values_text(v) -> str:
    """One line for a column's values: the list where it is short, else the lowest and highest held."""
    if not v:
        return ""
    if "list" in v:
        return ", ".join(str(k) for k in v["list"])
    if "see" in v:
        return f"see {v['see']}"
    if "note" in v:
        return str(v["note"])
    parts = []
    if "lowest" in v:
        parts.append(f"{v['lowest']} to {v['highest']}")
    if "earliest" in v:
        parts.append(f"{v['earliest']} to {v['latest']}")
    if "examples" in v:
        parts.append("e.g. " + ", ".join(str(x) for x in v["examples"][:3]))
    if "distinct" in v:
        parts.append(f"{v['distinct']} distinct")
    return "; ".join(parts)


def variables(table: str):
    """One row a column of the table: name, label, unit, type, values, missing_meaning, missing_cells, source_name,
    shared. A pandas DataFrame in the table's own column order."""
    import pandas as pd
    cols = describe(table)["columns"]
    rows = [{"name": c["name"], "label": c.get("label"), "unit": c.get("unit"), "type": c.get("type"),
             "values": values_text(c.get("values")), "missing_meaning": c.get("missing_meaning"),
             "missing_cells": c.get("missing_cells"), "source_name": c.get("source_name"), "shared": c["shared"]}
            for c in cols]
    return pd.DataFrame(rows, columns=["name", "label", "unit", "type", "values", "missing_meaning", "missing_cells",
                                       "source_name", "shared"])
