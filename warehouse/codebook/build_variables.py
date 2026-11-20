#!/usr/bin/env python3
"""Write warehouse/metadata/variables/<table>.yaml, one file a table: the codebook's metadata (chain 630, part B).

Energy Research Warehouse (ERW). A table's file holds two kinds of field:

- read fields, which this script writes from the table itself and its record: the columns as the file's header row
  holds them, each column's type, the values it takes (the list where it is short, the lowest and highest held where
  it is a number or a time), its empty cells, the series' variables with their units, rows and spans, whether the
  key is unique, the header's own title and shape lines, the license and tier of coverage.csv, the source lines, the
  method note and the citation. Each read is dated (read.date).
- written fields, which a person or a session writes from the method note, the connector, the source's documentation
  or the data, and this script never changes: row, time, vintage_rule, and for each column label, unit, missing
  meaning, source_name and documented_by, and for each variable its label. A written field this script finds
  in a hand file (--apply) is merged in; nothing else touches it.

A column defined in _shared.yaml is marked shared: true and holds only what is particular to the table.

Usage:
    python warehouse/codebook/build_variables.py --tables a b          read these tables and write their files
    python warehouse/codebook/build_variables.py --family eia930       the tables of one family of the plan
    python warehouse/codebook/build_variables.py --group 1             the plan's group 1 (public, read by the site)
    python warehouse/codebook/build_variables.py --apply hand.yaml     merge written fields, no table read
    python warehouse/codebook/build_variables.py ... --no-read         rewrite record fields only, keep the last read

The data directory is ERW_DATA, else warehouse/output. Files there are read, never written. No request is made.
An em dash in a publisher's value is written as " - " (the repository holds no em dash, CLAUDE.md rule 2).
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
VARS = ROOT / "warehouse" / "metadata" / "variables"
PLAN = ROOT / "docs" / "reviews" / "codebook-plan-2026-11-20.csv"
DATA = Path(os.environ.get("ERW_DATA", str(ROOT / "warehouse" / "output")))
SHORT = 25          # a column of at most this many distinct values is listed whole
TRACK = 5000        # distinct values tracked before a column is called many-valued
MAX_VARIABLES = 3000
CHUNK = 400_000
EM = chr(0x2014)
RE_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
RE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RE_INT = re.compile(r"[+-]?\d+")
WRITTEN_TABLE = ["row", "time", "vintage_rule", "keys_note", "second_look"]
WRITTEN_COLUMN = ["label", "unit", "missing_meaning", "source_name", "documented_by", "particular"]
SHAPE_KEYS = {"series": ["entity", "variable", "ts_utc"], "entities": ["entity_id"], "events": ["event_id"]}


def clean(v):
    if isinstance(v, str):
        return v.replace(EM, " - ")
    if isinstance(v, list):
        return [clean(x) for x in v]
    if isinstance(v, dict):
        return {clean(k): clean(x) for k, x in v.items()}
    return v


def shared_names():
    d = yaml.safe_load(open(VARS / "_shared.yaml", encoding="utf-8"))
    return set(d["columns"])


def header_of(path):
    lines, first = [], None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if line.startswith("#"):
                lines.append(line[1:].strip())
                continue
            first = line
            break
    return lines, next(csv.reader([first])) if first else []


def shape_of(cols):
    if cols[:4] == ["entity", "variable", "ts_utc", "value"]:
        return "series"
    if cols[:2] == ["entity_id", "entity_type"]:
        return "entities"
    if cols[:1] == ["event_id"]:
        return "events"
    return "other"


class Col:
    def __init__(self):
        self.empty = 0
        self.held = 0
        self.distinct = {}       # value -> rows, while at most TRACK
        self.many = False
        self.kinds = {"integer", "number", "utc time", "date", "boolean"}
        self.lo = None
        self.hi = None
        self.examples = []

    def add(self, s):
        e = s == ""
        self.empty += int(e.sum())
        ne = s[~e]
        if ne.empty:
            return
        self.held += len(ne)
        if not self.many:
            vc = ne.value_counts()
            for k, n in vc.items():
                self.distinct[k] = self.distinct.get(k, 0) + int(n)
            if len(self.distinct) > TRACK:
                self.many = True
                self.examples = sorted(self.distinct)[:5]
                self.distinct = {}
            uniq = vc.index.to_series()
        else:
            uniq = None
        if self.kinds & {"integer", "number"}:
            num = pd.to_numeric(ne, errors="coerce")
            if num.isna().any():
                self.kinds -= {"integer", "number"}
            else:
                lo, hi = float(num.min()), float(num.max())
                self.lo = lo if self.lo is None else min(self.lo, lo)
                self.hi = hi if self.hi is None else max(self.hi, hi)
                if "integer" in self.kinds:
                    u = uniq if uniq is not None else pd.Series(ne.unique())
                    if not u.str.fullmatch(RE_INT.pattern).all():
                        self.kinds.discard("integer")
        for k, rx in (("utc time", RE_UTC), ("date", RE_DATE)):
            if k in self.kinds:
                u = uniq if uniq is not None else pd.Series(ne.unique())
                if not u.str.fullmatch(rx.pattern).all():
                    self.kinds.discard(k)
        if "boolean" in self.kinds:
            u = uniq if uniq is not None else pd.Series(ne.unique())
            if not u.isin(["true", "false", "True", "False"]).all():
                self.kinds.discard("boolean")
        if not (self.kinds & {"integer", "number"}):
            lo, hi = ne.min(), ne.max()
            if isinstance(self.lo, float) or isinstance(self.hi, float):
                self.lo = self.hi = None
            self.lo = lo if self.lo is None else min(self.lo, lo)
            self.hi = hi if self.hi is None else max(self.hi, hi)

    def kind(self):
        if self.held == 0:
            return "empty"
        for k in ("boolean", "integer", "number", "utc time", "date"):
            if k in self.kinds:
                return k
        return "text"

    def values(self):
        k = self.kind()
        out = {}
        if k == "empty":
            return {"note": "no cell holds a value"}
        n = len(self.distinct)
        if not self.many and n <= SHORT:
            keys = sorted(self.distinct, key=float) if k in ("integer", "number") else sorted(self.distinct)
            out["list"] = {str(v): self.distinct[v] for v in keys}
            return out
        out["distinct"] = f"more than {TRACK}" if self.many else n
        if k in ("integer", "number"):
            out["lowest"] = int(self.lo) if k == "integer" else self.lo
            out["highest"] = int(self.hi) if k == "integer" else self.hi
        elif k in ("utc time", "date"):
            out["earliest"], out["latest"] = self.lo, self.hi
        else:
            ex = self.examples if self.many else sorted(self.distinct)[:5]
            out["examples"] = [str(x) for x in ex]
        return out


def read_table(path, cols, shape):
    nhead = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            nhead += 1
    stats = {c: Col() for c in cols}
    var = {}
    hashes, vhashes = [], []
    key = [c for c in SHAPE_KEYS.get(shape, []) if c in cols]
    vkey = key + ["vintage"] if (shape == "series" and "vintage" in cols) else []
    rows = 0
    for chunk in pd.read_csv(path, skiprows=nhead, dtype=str, keep_default_na=False, na_values=[],
                             encoding="utf-8", chunksize=CHUNK):
        rows += len(chunk)
        for c in cols:
            stats[c].add(chunk[c])
        if key:
            hashes.append(pd.util.hash_pandas_object(chunk[key], index=False).to_numpy())
        if vkey:
            vhashes.append(pd.util.hash_pandas_object(chunk[vkey], index=False).to_numpy())
        if shape == "series":
            g = chunk.groupby("variable", sort=False)
            agg = g.agg(rows=("variable", "size"), first=("ts_utc", "min"), last=("ts_utc", "max"))
            units = chunk.groupby(["variable", "unit"], sort=False).size()
            labels = chunk.groupby(["variable", "x_label"], sort=False).size() if "x_label" in cols else None
            for v, r in agg.iterrows():
                d = var.setdefault(v, {"rows": 0, "first": r["first"], "last": r["last"], "units": {},
                                       "labels": {}})
                d["rows"] += int(r["rows"])
                d["first"] = min(d["first"], r["first"])
                d["last"] = max(d["last"], r["last"])
            for (v, u), n in units.items():
                var[v]["units"][u] = var[v]["units"].get(u, 0) + int(n)
            if labels is not None:
                for (v, lab), n in labels.items():
                    if len(var[v]["labels"]) < 3:
                        var[v]["labels"][lab] = var[v]["labels"].get(lab, 0) + int(n)
    dup = vdup = None
    if hashes:
        h = np.concatenate(hashes)
        dup = int(len(h) - len(np.unique(h)))
    if vhashes and dup:
        h = np.concatenate(vhashes)
        vdup = int(len(h) - len(np.unique(h)))
    return rows, stats, var, key, (dup, vdup)


def source_lines(header):
    out = []
    for ln in header:
        if ln.startswith("Source:"):
            text = ln[len("Source:"):].strip()
            urls = re.findall(r"https?://\S+", text)
            name = text
            # the address is taken out of the words only where it ends the line; inside a sentence it stays
            if urls and text.rstrip().endswith(urls[-1]):
                name = text.rstrip()[: -len(urls[-1])]
            out.append({"name": clean(name.strip().rstrip(",;:").strip()), "url": urls[-1].rstrip(".,;)") if urls else ""})
    return out


def method_note(table, header):
    notes = {p.stem for p in (ROOT / "docs" / "methods").glob("*.md")}
    if table in notes:
        return f"docs/methods/{table}.md"
    named = re.findall(r"docs/methods/([a-z0-9_\-]+)\.md", " ".join(header))
    for n in named:
        if n in notes:
            return f"docs/methods/{n}.md"
    best, score = None, 0
    for p in sorted((ROOT / "docs" / "methods").glob("*.md")):
        k = len(re.findall(r"\b" + re.escape(table) + r"\b", p.read_text(encoding="utf-8", errors="replace")))
        if k > score:
            best, score = f"docs/methods/{p.stem}.md", k
    return best or ""


_CITES = None


def citation(table):
    global _CITES
    if _CITES is None:
        sys.path.insert(0, str(ROOT / "package" / "src"))
        import erw
        erw.set_backend(str(DATA))
        _CITES = erw
    via = " Via the Energy Research Warehouse (ERW), table "
    try:
        return _CITES.cite(table).split(via)[0] + via + f"`{table}`."
    except Exception as exc:  # noqa: BLE001 - recorded, never invented
        return f"not built: {type(exc).__name__}"


def coverage():
    with open(ROOT / "warehouse" / "metadata" / "coverage.csv", encoding="utf-8", newline="") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


def plan():
    with open(PLAN, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load(table):
    p = VARS / f"{table}.yaml"
    if p.is_file():
        return yaml.safe_load(open(p, encoding="utf-8")) or {}
    return {}


def save(table, doc):
    p = VARS / f"{table}.yaml"
    text = yaml.safe_dump(clean(doc), sort_keys=False, allow_unicode=True, width=120, default_flow_style=False)
    head = (f"# The codebook's metadata of table {table} (warehouse/codebook/build_variables.py; chain 630).\n"
            "# Read fields are rewritten from the table by the script; written fields (row, time, vintage_rule,\n"
            "# label, unit, missing_meaning, source_name, documented_by, particular) are kept. Shared column names\n"
            "# are defined in _shared.yaml.\n")
    p.write_text(head + text, encoding="utf-8", newline="\n")


def build(table, fam, cov, shared, do_read=True):
    old = load(table)
    path = DATA / f"{table}.csv"
    header, cols = header_of(path)
    shape = shape_of(cols)
    c = cov.get(table, {})
    doc = {"table": table, "family": fam, "shape": shape}
    for k in WRITTEN_TABLE[:3]:
        doc[k] = old.get(k)
    doc["keys"] = SHAPE_KEYS.get(shape, [])
    if old.get("keys_note"):
        doc["keys_note"] = old["keys_note"]
    doc["license"] = c.get("license", "")
    doc["tier"] = c.get("tier", "")
    doc["interval"] = c.get("interval", "")
    doc["source"] = source_lines(header)
    doc["cite"] = citation(table)
    doc["method"] = method_note(table, header)
    title = header[0] if header else ""
    title = re.sub(r"^Energy Research Warehouse \(ERW\):\s*", "", title)
    doc["header_title"] = title
    doc["header_shape"] = next((ln for ln in header if ln.startswith("Shape:")), "")
    if do_read:
        rows, stats, var, key, (dup, vdup) = read_table(path, cols, shape)
        doc["read"] = {"date": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"), "rows": rows,
                       "key_duplicates": dup}
        if vdup is not None:
            doc["read"]["key_duplicates_with_vintage"] = vdup
            if vdup == 0:
                doc["keys"] = SHAPE_KEYS["series"] + ["vintage"]
    else:
        doc["read"] = old.get("read", {})
        doc["keys"] = old.get("keys", doc["keys"])
        stats, var = None, None
    oldcols = {x["name"]: x for x in old.get("columns", []) or []}
    out = []
    for name in cols:
        o = oldcols.get(name, {})
        e = {"name": name}
        if name in shared:
            e["shared"] = True
            if o.get("particular"):
                e["particular"] = o["particular"]
        else:
            for k in ("label", "unit"):
                e[k] = o.get(k)
        if stats is not None:
            s = stats[name]
            e["type"] = s.kind()
            e["values"] = {"see": "variables"} if (shape == "series" and name == "variable") else s.values()
            e["missing_cells"] = s.empty
        else:
            for k in ("type", "values", "missing_cells"):
                e[k] = o.get(k)
        for k in ("missing_meaning", "source_name", "documented_by"):
            if name in shared and k == "documented_by":
                continue
            if o.get(k) is not None or name not in shared:
                e[k] = o.get(k)
        out.append(e)
    doc["columns"] = out
    if shape == "series":
        oldvars = {x["name"]: x for x in old.get("variables", []) or []}
        if var is not None:
            vs = []
            for v in sorted(var)[:MAX_VARIABLES]:
                d = var[v]
                ent = {"name": v, "label": oldvars.get(v, {}).get("label"),
                       "unit": "; ".join(sorted(d["units"])), "rows": d["rows"], "first": d["first"], "last": d["last"]}
                if d["labels"]:
                    ent["source_label"] = "; ".join(sorted(d["labels"]))
                vs.append(ent)
            doc["variables"] = vs
            if len(var) > MAX_VARIABLES:
                doc["variables_note"] = f"{len(var)} variables; the first {MAX_VARIABLES} by name are listed"
        else:
            doc["variables"] = old.get("variables", [])
    doc["second_look"] = old.get("second_look")
    save(table, doc)
    return doc


def apply(hand_path):
    hand = yaml.safe_load(open(hand_path, encoding="utf-8")) or {}
    n = 0
    for table, h in hand.items():
        doc = load(table)
        if not doc:
            print(f"apply: {table} has no file yet; read it first")
            continue
        for k in WRITTEN_TABLE:
            if k in h:
                doc[k] = h[k]
        cols = {x["name"]: x for x in doc.get("columns", [])}
        for name, fields in (h.get("columns") or {}).items():
            if name not in cols:
                print(f"apply: {table}.{name} is not a column of the table")
                continue
            for k, v in fields.items():
                if k not in WRITTEN_COLUMN:
                    raise SystemExit(f"apply: {table}.{name}: {k} is not a written field")
                cols[name][k] = v
        vars_ = {x["name"]: x for x in doc.get("variables", []) or []}
        for v, lab in (h.get("variables") or {}).items():
            if v in vars_:
                vars_[v]["label"] = lab
            else:
                print(f"apply: {table}: variable {v} is not held")
        # keep the order of the keys of a built file
        order = ["table", "family", "shape", "row", "time", "vintage_rule", "keys", "keys_with_revisions",
                 "keys_note"]
        doc = {**{k: doc[k] for k in order if k in doc}, **{k: v for k, v in doc.items() if k not in order}}
        save(table, doc)
        n += 1
    print(f"applied written fields to {n} tables")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tables", nargs="*", default=[])
    p.add_argument("--family", nargs="*", default=[])
    p.add_argument("--group", default="")
    p.add_argument("--apply", default="")
    p.add_argument("--no-read", action="store_true")
    a = p.parse_args(argv)
    if a.apply:
        apply(a.apply)
        return 0
    pl = plan()
    fam = {r["table"]: r["family"] for r in pl}
    names = list(a.tables)
    names += [r["table"] for r in pl if r["family"] in a.family]
    if a.group:
        names += [r["table"] for r in pl if r["group"].startswith(a.group)]
    cov, shared = coverage(), shared_names()
    VARS.mkdir(parents=True, exist_ok=True)
    fails = 0
    for t in dict.fromkeys(names):
        t0 = dt.datetime.now()
        try:
            d = build(t, fam.get(t, ""), cov, shared, do_read=not a.no_read)
            print(f"{t}: {len(d['columns'])} columns, {d['read'].get('rows')} rows, "
                  f"{len(d.get('variables') or [])} variables, {(dt.datetime.now() - t0).seconds} s", flush=True)
        except Exception as exc:  # noqa: BLE001 - one table's failure is named, the others go on
            fails += 1
            print(f"{t}: FAILED {type(exc).__name__}: {exc}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
