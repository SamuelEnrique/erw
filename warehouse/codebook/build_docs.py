#!/usr/bin/env python3
"""Write docs/codebook/: one document a family of tables and the index README.md (chain 630, part E).

Energy Research Warehouse (ERW). Drawn from warehouse/metadata/variables/ (the codebook's metadata, one file a table,
and _shared.yaml) and the family of each table in docs/reviews/codebook-plan-2026-11-20.csv; never written by hand.
Rerun it after the metadata changes:

    python warehouse/codebook/build_docs.py            write docs/codebook/*.md
    python warehouse/codebook/build_docs.py --check    exit 1 when a document differs from what the metadata gives

A table's document entry holds what a row is, its keys, time, revision rule, license, tier, source, citation and
method note, its columns (name, label, unit, type, values, what an empty cell means) and a series table's variables.
Only the tables coverage.csv flags public are written: an internal table is documented in its metadata file only.
No request is made.
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VARS = ROOT / "warehouse" / "metadata" / "variables"
OUT = ROOT / "docs" / "codebook"
PLAN = ROOT / "docs" / "reviews" / "codebook-plan-2026-11-20.csv"
NOT_DOC = "not documented by the source"
MAX_VARS = 300
EM = chr(0x2014)


def cell(v):
    s = "" if v is None else str(v)
    return s.replace("|", "\\|").replace("\n", " ").replace(EM, " - ")


def values_text(v):
    if not v:
        return ""
    if "list" in v:
        items = list(v["list"])
        return ", ".join(str(k) for k in items[:25])
    if "see" in v:
        return "see the variables below"
    if "note" in v:
        return str(v["note"])
    parts = []
    if "lowest" in v:
        parts.append(f"{v['lowest']} to {v['highest']}")
    if "earliest" in v:
        parts.append(f"{v['earliest']} to {v['latest']}")
    if "examples" in v:
        parts.append("for example " + ", ".join(str(x) for x in v["examples"][:3]))
    if "distinct" in v:
        parts.append(f"{v['distinct']} distinct")
    return "; ".join(parts)


def load_all():
    shared = yaml.safe_load((VARS / "_shared.yaml").read_text(encoding="utf-8"))["columns"]
    with open(ROOT / "warehouse" / "metadata" / "coverage.csv", encoding="utf-8", newline="") as f:
        cov = {r["table"]: r for r in csv.DictReader(f)}
    with open(PLAN, encoding="utf-8", newline="") as f:
        fam = {r["table"]: r["family"] for r in csv.DictReader(f)}
    docs = {}
    for p in sorted(VARS.glob("*.yaml")):
        if p.stem.startswith("_"):
            continue
        docs[p.stem] = yaml.safe_load(p.read_text(encoding="utf-8"))
    return shared, cov, fam, docs


def column_complete(c):
    if c.get("shared"):
        return True
    return bool(c.get("label")) and bool(c.get("unit"))


def table_complete(d):
    return bool(d.get("row")) and all(column_complete(c) for c in d.get("columns") or [])


def entry(t, d, shared):
    L = [f"### `{t}`", ""]
    L.append(cell(d.get("row") or "What a row is: not yet written.") + "")
    L.append("")
    facts = [f"Shape: {d.get('shape')}", "Keys: " + ", ".join(f"`{k}`" for k in d.get("keys") or [])]
    if d.get("keys_note"):
        facts.append(cell(d["keys_note"]))
    facts.append(f"License: {d.get('license')}; tier: {d.get('tier')}")
    rd = d.get("read") or {}
    facts.append(f"Rows read on {rd.get('date')}: {rd.get('rows')}")
    L.append(". ".join(facts) + ".")
    L.append("")
    if d.get("time"):
        L.append(f"- **Time:** {cell(d['time'])}")
    if d.get("vintage_rule"):
        L.append(f"- **Revisions:** {cell(d['vintage_rule'])}")
    for s in d.get("source") or []:
        L.append(f"- **Source:** {cell(s.get('name'))}" + (f" ({s['url']})" if s.get("url") else ""))
    if d.get("method"):
        L.append(f"- **Method note:** [`{d['method']}`](../methods/{Path(d['method']).name})")
    if d.get("cite"):
        L.append(f"- **Cite as:** {cell(d['cite'])}")
    L.append("")
    L.append("| Column | Label | Unit | Type | Values | Empty cells |")
    L.append("|---|---|---|---|---|---|")
    for c in d.get("columns") or []:
        if c.get("shared"):
            s = shared.get(c["name"], {})
            label = s.get("label", "")
            if c.get("particular"):
                label = f"{label}. Here: {c['particular']}"
            unit = s.get("unit", "")
            miss = c.get("missing_meaning") or ""
        else:
            label = c.get("label") or "not yet written"
            if c.get("source_name"):
                label = f"{label} (the source's name: {c['source_name']})"
            unit = c.get("unit") or ""
            miss = c.get("missing_meaning") or ""
        n = c.get("missing_cells")
        empt = f"{n}" + (f": {miss}" if miss and n else "")
        L.append(f"| `{c['name']}` | {cell(label)} | {cell(unit)} | {cell(c.get('type'))} | "
                 f"{cell(values_text(c.get('values')))} | {cell(empt)} |")
    L.append("")
    vs = d.get("variables") or []
    if vs:
        L.append(f"Variables ({len(vs)}" + (f"; the first {MAX_VARS} by name" if len(vs) > MAX_VARS else "") + "):")
        L.append("")
        L.append("| Variable | Label | Unit | Rows | First | Last |")
        L.append("|---|---|---|---|---|---|")
        for v in vs[:MAX_VARS]:
            lab = v.get("label") or (f"the source's label: {v['source_label']}" if v.get("source_label") else "")
            L.append(f"| `{cell(v['name'])}` | {cell(lab)} | {cell(v.get('unit'))} | {v.get('rows')} | "
                     f"{cell(v.get('first'))} | {cell(v.get('last'))} |")
        L.append("")
    if d.get("second_look"):
        L.append("Waiting for a second look: " + "; ".join(cell(x) for x in d["second_look"]) + ".")
        L.append("")
    return L


def counts(docs, public):
    n_tab = n_tab_done = n_col = n_col_done = n_notdoc = n_var = n_var_done = 0
    for t in public:
        d = docs.get(t)
        if not d:
            continue
        n_tab += 1
        n_tab_done += table_complete(d)
        for c in d.get("columns") or []:
            n_col += 1
            n_col_done += column_complete(c)
            if NOT_DOC in str(c.get("label") or "").lower():
                n_notdoc += 1
        for v in d.get("variables") or []:
            n_var += 1
            n_var_done += bool(v.get("label"))
            if NOT_DOC in str(v.get("label") or "").lower():
                n_notdoc += 1
    return n_tab, n_tab_done, n_col, n_col_done, n_var, n_var_done, n_notdoc


def two_meanings(docs, public):
    """Own column names (not in _shared.yaml) that two or more public tables label differently."""
    by = defaultdict(dict)
    for t in public:
        for c in (docs.get(t) or {}).get("columns") or []:
            if not c.get("shared") and c.get("label") and NOT_DOC not in str(c["label"]):
                by[c["name"]].setdefault(str(c["label"]).strip().rstrip("."), []).append(t)
    return {n: m for n, m in by.items() if len(m) > 1}


def render():
    shared, cov, fam, docs = load_all()
    public = sorted(t for t in docs if cov.get(t, {}).get("license") == "public")
    fams = defaultdict(list)
    for t in public:
        fams[fam.get(t) or docs[t].get("family") or "other_sources"].append(t)
    out = {}
    for f, ts in sorted(fams.items()):
        L = [f"# Codebook: {f}", ""]
        L.append("Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by "
                 "hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined "
                 "once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the "
                 "[index](README.md).")
        L.append("")
        shapes = defaultdict(int)
        tiers = defaultdict(int)
        for t in ts:
            shapes[docs[t].get("shape")] += 1
            tiers[docs[t].get("tier")] += 1
        done = sum(table_complete(docs[t]) for t in ts)
        L.append(f"**What the family holds.** {len(ts)} public tables ("
                 + ", ".join(f"{n} {s}" for s, n in sorted(shapes.items())) + "; tiers: "
                 + ", ".join(f"{n} {s}" for s, n in sorted(tiers.items())) + f"); {done} documented in full.")
        L.append("")
        for t in ts:
            L.append(f"- [`{t}`](#{t}): {cell(docs[t].get('row') or docs[t].get('header_title') or '')}")
        L.append("")
        for t in ts:
            L.extend(entry(t, docs[t], shared))
        out[f"{f}.md"] = "\n".join(L) + "\n"
    n_tab, n_tab_done, n_col, n_col_done, n_var, n_var_done, n_notdoc = counts(docs, public)
    tm = two_meanings(docs, public)
    R = ["# The ERW codebook", ""]
    R.append("What every public table of the Energy Research Warehouse holds: what a row is, and what each column and "
             "each variable means, its unit, the values it takes and what an empty cell means. Drawn from "
             "`warehouse/metadata/variables/` (one file a table) by `warehouse/codebook/build_docs.py`; never written "
             "by hand. The same metadata answers `erw.describe(table)` and `erw.variables(table)` in the Python "
             "package. Nothing in it is guessed: a label comes from the method note, the connector, the source's "
             "documentation or the data, and where none of them says, it reads \"not documented by the source\".")
    R.append("")
    R.append("## The counts")
    R.append("")
    R.append(f"- Public tables with a metadata file: {n_tab}; documented in full (what a row is, and every column's "
             f"label and unit): {n_tab_done}.")
    R.append(f"- Columns: {n_col}; documented: {n_col_done} (a shared column is documented once, below).")
    R.append(f"- Variables of the series tables (values of `variable`): {n_var}; labelled: {n_var_done}.")
    R.append(f"- Entries that read \"not documented by the source\": {n_notdoc}.")
    R.append(f"- Column names that two or more tables label differently (names that may mean two things): {len(tm)}.")
    R.append("")
    R.append("## The families")
    R.append("")
    R.append("| Family | Tables | Documented in full |")
    R.append("|---|---|---|")
    for f, ts in sorted(fams.items()):
        R.append(f"| [{f}]({f}.md) | {len(ts)} | {sum(table_complete(docs[t]) for t in ts)} |")
    R.append("")
    R.append("## The shared column names")
    R.append("")
    R.append("Defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml), in the data "
             "standard's words ([`docs/datastandard.md`](../datastandard.md)).")
    R.append("")
    R.append("| Column | Label | Type | Unit | Rule |")
    R.append("|---|---|---|---|---|")
    for n, s in shared.items():
        R.append(f"| `{n}` | {cell(s.get('label'))} | {cell(s.get('type'))} | {cell(s.get('unit'))} | {cell(s.get('rule'))} |")
    R.append("")
    out["README.md"] = "\n".join(R) + "\n"
    return out


def site_json():
    """site/data/codebook_methods.json: for each method note (its slug), the public tables it documents, each with
    its row and its columns as [name, label, unit, type, values], for the variables table of /data/methods/<slug>.
    Shared columns carry _shared.yaml's label and unit. Internal tables are never named on the site."""
    import json
    shared, cov, fam, docs = load_all()
    by = defaultdict(list)
    for t in sorted(docs):
        d = docs[t]
        if cov.get(t, {}).get("license") != "public" or not d.get("method"):
            continue
        cols = []
        for c in d.get("columns") or []:
            if c.get("shared"):
                s = shared.get(c["name"], {})
                label = s.get("label", "") + (f". Here: {c['particular']}" if c.get("particular") else "")
                unit = s.get("unit", "")
            else:
                label, unit = c.get("label") or "", c.get("unit") or ""
            cols.append([c["name"], label.replace(EM, " - "), unit, c.get("type") or "",
                         values_text(c.get("values")).replace(EM, " - ")])
        by[Path(d["method"]).stem].append({"table": t, "row": (d.get("row") or "").replace(EM, " - "),
                                           "read": (d.get("read") or {}).get("date") or "", "columns": cols})
    return json.dumps(dict(sorted(by.items())), ensure_ascii=False, separators=(",", ":")) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true")
    p.add_argument("--site", action="store_true", help="also write site/data/codebook_methods.json")
    a = p.parse_args(argv)
    if a.site:
        sp = ROOT / "site" / "data" / "codebook_methods.json"
        sp.write_text(site_json(), encoding="utf-8", newline="\n")
        print(f"wrote {sp} ({sp.stat().st_size // 1024} KB)")
    out = render()
    if a.check:
        bad = [n for n, text in out.items()
               if not (OUT / n).is_file() or (OUT / n).read_text(encoding="utf-8") != text]
        print(f"docs/codebook: {len(out)} documents, {len(bad)} differ" + (f": {bad[:10]}" if bad else ""))
        return 1 if bad else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for n, text in out.items():
        (OUT / n).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(out)} documents to docs/codebook/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
