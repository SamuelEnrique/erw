#!/usr/bin/env python3
"""Which warehouse tables each page of the site reads, read from the page's own code (session 248; first written by
session 214 as runs/session214/page_tables.py for the launch list, now in the repository so that the license table
can be rebuilt).

Energy Research Warehouse (ERW). For each route of site/lib/pages.ts (plus the home page, Data and methods, About,
Terms, Privacy, the Digest, the Roundup and the seven grid pages): the page file under site/app, every module it
imports under site/lib, site/components and site/data (followed three levels deep), and the table names of
warehouse/metadata/coverage.csv that appear in the code the page reaches. A module's table names are attributed to its
top-level export blocks, so a page that imports two functions of lib/data.ts gets the tables of those two, not of the
whole file. A data file (JSON) a page imports counts for the tables it names in a "table" or "tables" key.

    python scripts/page_tables.py                 # one line a page
    python scripts/page_tables.py --json FILE     # the whole reading, as JSON

It reads names. A table named in a comment that the page does not read is left out (comments are stripped), a table
read through a name built at run time is missed, and a page whose reads go through an API route is not followed
there. scripts/licenses.py state uses it for "the pages each table darkens" and says so. Read only.
"""
import argparse
import csv
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
APP = os.path.join(SITE, "app")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
GRIDS = ("ercot", "caiso", "pjm", "nyiso", "isone", "miso", "spp")
FIRST = ["/", "/about", "/terms", "/privacy", "/data", "/data/methods", "/data/standard", "/data/faults", "/digest", "/roundup", "/subscribe"]
# modules whose table names say nothing about one page (the menu, the gate, the readers' plumbing, the words)
GENERIC = {"lib/pages.ts", "lib/release.ts", "lib/supabase.ts", "lib/format.ts", "lib/markdown.ts", "lib/glossary.ts", "lib/audience.ts", "lib/license.ts",
           "components/SiteLink.tsx", "components/Nav.tsx", "components/Section.tsx", "components/Num.tsx", "components/Cite.tsx",
           "components/NoData.tsx", "components/Related.tsx", "components/Internal.tsx", "components/Usage.tsx", "components/Term.tsx"}
IMPORT_RE = re.compile(r"""import\s+(?:type\s+)?(?:(\*\s+as\s+\w+)|(\w+)|\{([^}]*)\}|(\w+)\s*,\s*\{([^}]*)\})?\s*(?:from\s*)?["']([^"']+)["']""")
COMMENT_RE = re.compile(r"/\*[\s\S]*?\*/|(?<![:\"'])//[^\n]*")


def coverage_tables(path=COVERAGE):
    with open(path, encoding="utf-8", newline="") as f:
        return [r["table"] for r in csv.DictReader(f)]


def table_re(tables):
    return re.compile(r"(?<![a-z0-9_])(" + "|".join(sorted(map(re.escape, tables), key=len, reverse=True)) + r")(?![a-z0-9_])")


def resolve(spec, from_file, site=SITE):
    if spec.startswith("@/"):
        base = os.path.join(site, spec[2:])
    elif spec.startswith("."):
        base = os.path.normpath(os.path.join(os.path.dirname(from_file), spec))
    else:
        return None
    for cand in (base, base + ".ts", base + ".tsx", base + ".json", os.path.join(base, "index.ts"), os.path.join(base, "index.tsx")):
        if os.path.isfile(cand):
            return cand
    return None


def imports_of(path):
    with open(path, encoding="utf-8") as f:
        src = COMMENT_RE.sub("", f.read())
    out = []
    for m in IMPORT_RE.finditer(src):
        star, default, names, default2, names2, spec = m.groups()
        idents = set()
        if star:
            idents.add("*")
        for d in (default, default2):
            if d:
                idents.add(d)
        for n in (names, names2):
            for part in (n or "").split(","):
                part = re.sub(r"^type\s+", "", part.strip())
                if part:
                    idents.add(part.split(" as ")[0].strip())
        out.append((spec, idents))
    return src, out


def blocks(src):
    """{export name: text} for a module's top-level export blocks; '' holds what is not in any export."""
    out, cur, buf = {}, "", []
    for line in src.splitlines():
        m = re.match(r"^export\s+(?:default\s+)?(?:async\s+)?(?:function|const|let|var|class|type|interface|enum)\s+(\w+)", line)
        if m:
            out[cur] = out.get(cur, "") + "\n".join(buf) + "\n"
            cur, buf = m.group(1), [line]
        else:
            buf.append(line)
    out[cur] = out.get(cur, "") + "\n".join(buf)
    return out


# Session 214's rule for a data file a page imports: the tables it names in a "table" or "tables" key, and the tables
# its text mentions (board.json and supply.json name their tables in their sources' parentheses). Not the faults file,
# which names the tables that have faults; nor the site's own two files; and markets.json is the grid list, so its two
# price tables a grid count for /prices alone.
NOT_A_READ = ("data_faults.json", "site.json", "license_status.json")
ONLY_FOR = {"markets.json": "/prices"}


def json_tables(path, tables, route=""):
    """The tables a data file stands for, by the rule above."""
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read(4_000_000)
        d = json.loads(text) if len(text) < 4_000_000 else {}
    except (OSError, ValueError):
        return set()
    named = set()
    for k in ("table", "tables", "table_name", "tables_read"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str):
            named.add(v)
        elif isinstance(v, list):
            named.update(x for x in v if isinstance(x, str))
    named &= set(tables)
    if name in NOT_A_READ or (name in ONLY_FOR and route != ONLY_FOR[name]):
        return named
    return named | set(table_re(tables).findall(text))


def walk(page_file, tables, depth=3, site=SITE, route="", root_idents=None):
    """{table: [the files of the site it was found in]} for the code a page reaches. Session 502: `root_idents`, when
    given, reads only those top-level exports of the first file (a component a page's view draws), as an imported
    module's are read; the default reads the whole file, as before."""
    rx = table_re(tables)
    found, seen = {}, set()

    def rel(p):
        return os.path.relpath(p, site).replace("\\", "/")

    def visit(path, idents, d):
        key = rel(path)
        if (key, frozenset(idents)) in seen or d < 0:
            return
        seen.add((key, frozenset(idents)))
        if path.endswith(".json"):
            for t in json_tables(path, tables, route):
                found.setdefault(t, set()).add(key)
            return
        src, imps = imports_of(path)
        if key in GENERIC and d < depth:
            return
        if (d == depth and root_idents is None) or "*" in idents or not idents:
            text = src
        else:
            b = blocks(src)
            text = b.get("", "") + "".join(b.get(i, "") for i in idents)
        for t in rx.findall(text):
            found.setdefault(t, set()).add(key)
        for spec, ids in imps:
            tgt = resolve(spec, path, site)
            if tgt:
                visit(tgt, ids, d - 1)

    visit(page_file, set(root_idents) if root_idents else {"*"}, depth)
    return {t: sorted(v) for t, v in sorted(found.items())}


def page_file_of(route, app=APP):
    r = route.split("?")[0].strip("/")
    cands = [os.path.join(app, r, "page.tsx")]
    parts = r.split("/") if r else []
    parent = os.path.join(app, *parts[:-1]) if parts else app
    if parts and os.path.isdir(parent):
        cands += [os.path.join(parent, dyn, "page.tsx") for dyn in sorted(os.listdir(parent)) if dyn.startswith("[")]
    return next((c for c in cands if os.path.isfile(c)), None)


def declared(site=SITE):
    """{route: {label, tables}} as site/lib/pages.ts declares them, and the seven grid pages."""
    with open(os.path.join(site, "lib", "pages.ts"), encoding="utf-8") as f:
        src = f.read()
    out = {}
    for m in re.finditer(r'href:\s*"([^"]+)",\s*label:\s*"([^"]+)",\s*line:\s*"(?:[^"\\]|\\.)*",\s*tables:\s*"([^"]*)"', src):
        out[m.group(1)] = {"label": m.group(2), "tables": m.group(3)}
    for g in GRIDS:
        out.setdefault(f"/grid/{g}", {"label": f"Grid: {g.upper()}", "tables": ""})
    return out


def read(site=SITE, coverage=COVERAGE):
    """{route: {label, page_file, tables: {table: [files]}, declared: [tables the menu's line names]}}; a route with no
    page file has "error"."""
    tables = coverage_tables(coverage)
    dec = declared(site)
    app = os.path.join(site, "app")
    out = {}
    for r in FIRST + [r for r in dec if r not in FIRST]:
        pf = page_file_of(r, app)
        if not pf:
            out[r] = {"label": dec.get(r, {}).get("label", ""), "error": "no page file"}
            continue
        words = dec.get(r, {}).get("tables", "")
        named = sorted(set(table_re(tables).findall(words))) if words else []      # the names the menu's line gives, where they are tables
        out[r] = {"label": dec.get(r, {}).get("label", ""), "page_file": os.path.relpath(pf, site).replace("\\", "/"),
                  "tables": walk(pf, tables, site=site, route=r), "declared": named}
    return out


def tables_of(page):
    """Every table a page's reading names: found in its code, or declared for it in the menu."""
    return sorted(set(page.get("tables", {})) | set(page.get("declared", [])))


def main(argv=None):
    ap = argparse.ArgumentParser(description="which warehouse tables each page of the site reads (session 248)")
    ap.add_argument("--json", help="write the whole reading to this file")
    a = ap.parse_args(argv)
    out = read()
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=1)
            f.write("\n")
    for r, v in out.items():
        print(f"{r}: {v['error']}" if "error" in v else f"{r}: {', '.join(tables_of(v)) or 'no table'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
