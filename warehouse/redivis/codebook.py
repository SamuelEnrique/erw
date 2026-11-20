#!/usr/bin/env python3
"""The codebook for Redivis: each table's description and each variable's label, as files the uploader reads
(chain 630, part D4). Nothing is released: a release is a person's click.

Energy Research Warehouse (ERW). Drawn from warehouse/metadata/variables/ (one file a table, and _shared.yaml):

    docs/redivis/codebook/tables.csv      table, description: what a row is, its keys, time, revisions, source,
                                          citation and method note, at most 2,000 characters (Redivis's limit)
    docs/redivis/codebook/variables.csv   table, name, label, description: the column's label (at most 250
                                          characters) and its unit, type, values and what an empty cell means

Usage:
    python warehouse/redivis/codebook.py write                 write the two files (no request)
    python warehouse/redivis/codebook.py check                 exit 1 when the files differ from the metadata
    python warehouse/redivis/codebook.py apply [--target stanford] [--tables a b] [--yes]
                                                               set the draft's descriptions and labels from the files;
                                                               without --yes it lists what it would set and sends
                                                               nothing. Under the data lock (a Redivis write).

warehouse/redivis/upload.py reads the files too: a table it creates takes the codebook's description, followed by
the provenance header as before, and a table whose upload it waits for takes the labels. Every upload deletes and
recreates its table, so the labels are set again after each one; `apply` sets them on the tables already there.
Only the public tables are written: internal tables never go to the public datasets.
"""
import argparse
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VARS = ROOT / "warehouse" / "metadata" / "variables"
OUT = ROOT / "docs" / "redivis" / "codebook"
DESC_MAX = 2000
LABEL_MAX = 250
VAR_DESC_MAX = 2000
EM = chr(0x2014)


def _clean(s):
    return ("" if s is None else str(s)).replace(EM, " - ").replace("\r", " ").replace("\n", " ").strip()


def _cut(s, n):
    s = _clean(s)
    return s if len(s) <= n else s[: n - 5].rstrip() + " [...]"


def _values(v):
    if not v:
        return ""
    if "list" in v:
        return "values: " + ", ".join(str(k) for k in list(v["list"])[:25])
    if "see" in v:
        return "values: see the table's variables"
    if "note" in v:
        return str(v["note"])
    parts = []
    if "lowest" in v:
        parts.append(f"lowest {v['lowest']}, highest {v['highest']}")
    if "earliest" in v:
        parts.append(f"earliest {v['earliest']}, latest {v['latest']}")
    if "examples" in v:
        parts.append("for example " + ", ".join(str(x) for x in v["examples"][:3]))
    if "distinct" in v:
        parts.append(f"{v['distinct']} distinct values")
    return "; ".join(parts)


def _public():
    with open(ROOT / "warehouse" / "metadata" / "coverage.csv", encoding="utf-8", newline="") as f:
        return {r["table"] for r in csv.DictReader(f) if r.get("license") == "public"}


def build():
    import yaml
    shared = yaml.safe_load((VARS / "_shared.yaml").read_text(encoding="utf-8"))["columns"]
    pub = _public()
    tables, variables = [], []
    for p in sorted(VARS.glob("*.yaml")):
        t = p.stem
        if t.startswith("_") or t not in pub:
            continue
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if not d.get("row"):
            continue  # nothing written yet: the uploader keeps the header as its description
        parts = [_clean(d["row"])]
        if d.get("keys"):
            parts.append("Keys: " + ", ".join(d["keys"]) + ".")
        if d.get("time"):
            parts.append("Time: " + _clean(d["time"]))
        if d.get("vintage_rule"):
            parts.append("Revisions: " + _clean(d["vintage_rule"]))
        parts.append(f"License: {d.get('license')}; tier: {d.get('tier')}.")
        for s in d.get("source") or []:
            parts.append("Source: " + _clean(s.get("name")) + (f" ({s['url']})" if s.get("url") else "") + ".")
        if d.get("cite"):
            parts.append("Cite as: " + _clean(d["cite"]))
        if d.get("method"):
            parts.append(f"Method note: https://github.com/SamuelEnrique/erw/blob/main/{d['method']}")
        parts.append(f"Codebook: https://github.com/SamuelEnrique/erw/blob/main/warehouse/metadata/variables/{t}.yaml")
        tables.append({"table": t, "description": _cut(" ".join(parts), DESC_MAX)})
        for c in d.get("columns") or []:
            if c.get("shared"):
                s = shared.get(c["name"], {})
                label = s.get("label", "")
                unit = s.get("unit", "")
                extra = c.get("particular") or ""
            else:
                label, unit, extra = c.get("label") or "", c.get("unit") or "", ""
            if not label:
                continue
            desc = []
            if extra:
                desc.append(f"Here: {_clean(extra)}.")
            if unit and unit != "none":
                desc.append(f"Unit: {unit}.")
            if c.get("type"):
                desc.append(f"Type: {c['type']}.")
            vt = _values(c.get("values"))
            if vt:
                desc.append(_clean(vt) + f" (read {(d.get('read') or {}).get('date')}).")
            if c.get("missing_meaning"):
                desc.append("An empty cell: " + _clean(c["missing_meaning"]) + ".")
            if c.get("source_name"):
                desc.append("The source's name: " + _clean(c["source_name"]) + ".")
            variables.append({"table": t, "name": c["name"], "label": _cut(label, LABEL_MAX),
                              "description": _cut(" ".join(desc), VAR_DESC_MAX)})
    return tables, variables


def _csv_text(rows, fields):
    import io
    b = io.StringIO()
    w = csv.DictWriter(b, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return b.getvalue()


def texts():
    tables, variables = build()
    return {"tables.csv": _csv_text(tables, ["table", "description"]),
            "variables.csv": _csv_text(variables, ["table", "name", "label", "description"])}


_LOADED = None


def _load():
    global _LOADED
    if _LOADED is None:
        desc, labels = {}, {}
        tp, vp = OUT / "tables.csv", OUT / "variables.csv"
        if tp.is_file():
            with open(tp, encoding="utf-8", newline="") as f:
                desc = {r["table"]: r["description"] for r in csv.DictReader(f)}
        if vp.is_file():
            with open(vp, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    labels.setdefault(r["table"], {})[r["name"]] = (r["label"], r["description"])
        _LOADED = (desc, labels)
    return _LOADED


def description_for(table):
    """The codebook's description of the table, or None where none is written (upload.py then uses the header)."""
    return _load()[0].get(table)


def labels_for(table):
    """{column: (label, description)} for the table, {} where none is written."""
    return _load()[1].get(table, {})


def set_labels(rtable, table):
    """Set the labels and descriptions of one Redivis table's variables from the files; return how many were set."""
    labels = labels_for(table)
    n = 0
    if not labels:
        return 0
    for v in rtable.list_variables():
        name = v.properties.get("name")
        if name in labels:
            label, desc = labels[name]
            if v.properties.get("label") != label or (v.properties.get("description") or "") != desc:
                try:
                    v.update(label=label, description=desc)
                    n += 1
                except Exception as exc:  # noqa: BLE001 - one refused label is printed; the others go on
                    print(f"{table}.{name}: label refused ({type(exc).__name__}: {str(exc)[:160]})", flush=True)
    return n


def apply(target, only, yes):
    sys.path.insert(0, str(ROOT / "warehouse" / "redivis"))
    sys.path.insert(0, str(ROOT / "warehouse"))
    import upload
    desc, labels = _load()
    names = sorted(set(desc) | set(labels))
    if only:
        names = [t for t in names if t in set(only)]
    if not yes:
        print(f"would set the descriptions of {sum(t in desc for t in names)} tables and the labels of "
              f"{sum(len(labels.get(t, {})) for t in names)} variables in the {target or 'default'} draft, for the "
              "tables the draft holds; nothing sent (add --yes)")
        return 0
    import lock
    lock.require(what="the Redivis codebook labels")
    if target:
        upload.use_target(target)
    ds = upload.open_draft()
    present = {t.properties["name"] for t in ds.list_tables()}
    done_t = done_v = 0
    for t in names:
        if t not in present:
            continue
        rt = ds.table(t)
        if t in desc and (rt.get().properties.get("description") or "") != desc[t]:
            rt.update(description=desc[t])
            done_t += 1
        done_v += set_labels(rt, t)
    print(f"set {done_t} table descriptions and {done_v} variable labels in the draft of "
          f"{target or 'the default dataset'}; nothing released")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("what", choices=["write", "check", "apply"])
    p.add_argument("--target", default="")
    p.add_argument("--tables", nargs="*", default=[])
    p.add_argument("--yes", action="store_true")
    a = p.parse_args(argv)
    if a.what == "apply":
        return apply(a.target, a.tables, a.yes)
    out = texts()
    if a.what == "check":
        bad = [n for n, text in out.items() if not (OUT / n).is_file() or (OUT / n).read_text(encoding="utf-8") != text]
        print(f"docs/redivis/codebook: {len(bad)} of {len(out)} files differ from the metadata" + (f": {bad}" if bad else ""))
        return 1 if bad else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for n, text in out.items():
        (OUT / n).write_text(text, encoding="utf-8", newline="\n")
    t, v = build()
    print(f"wrote docs/redivis/codebook/: {len(t)} table descriptions, {len(v)} variable labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
