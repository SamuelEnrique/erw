#!/usr/bin/env python3
"""The license table for the public day: every table public, "license needed" or internal, and the pages each one
darkens (session 248).

Energy Research Warehouse (ERW). Written from files, no figure typed:

    warehouse/metadata/coverage.csv          every table and its flag (public or internal)
    warehouse/metadata/license_status.csv    the tables flagged public whose publisher asks for permission (session
                                             207; `python scripts/licenses.py status` writes it)
    warehouse/metadata/license_tables.csv    each table's publishers
    the site's own code                      which tables each page reads (scripts/page_tables.py)

    python scripts/license_state.py                 # docs/state/licenses_<the day>.md, and three new keys of
                                                    # site/data/license_status.json ("all", "internal_tables", "pages":
                                                    # an internal table is counted there, never named)
    python scripts/license_state.py --check         # exit 1 when either file is not what the four sources give

A table's status, one of three:
    internal         coverage flags it internal: it is in no public dataset, no download and no page a visitor reads
    license needed   flagged public, its publisher's own page asks for permission or a license, and no permission is
                     recorded: from the day, the site writes "license needed" where its numbers would be
    public           everything else, a table with a recorded permission among them

How a table darkens a page (site/lib/license.ts, session 215): a held table whose deciding publishers are all grid
operators is held row by row, for the rows of those grids, and the page keeps its other grids ("by grid"); any other
held table is held whole. A page is "dark" when every table it reads is held or internal, "partly" when some are.

The pages are read from the code as it stands on the branch this runs on. The reading is of names (see
scripts/page_tables.py for what it can miss); the page's own code decides what a visitor sees.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import page_tables  # noqa: E402

META = os.path.join(ROOT, "warehouse", "metadata")
COVERAGE, STATUS, TABLES = (os.path.join(META, f) for f in ("coverage.csv", "license_status.csv", "license_tables.csv"))
SITE_STATUS = os.path.join(ROOT, "site", "data", "license_status.json")
RELEASE = os.path.join(ROOT, "site", "lib", "release.ts")
PUBLIC, NEEDED, INTERNAL = "public", "license needed", "internal"
GRIDS = {"CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP"}
WHOLE, BY_GRID = "whole", "by grid"
# the pages site/lib/pages.ts does not list with a label
NAMES = {"/": "Home", "/about": "About", "/terms": "Terms", "/privacy": "Privacy", "/data": "Data and methods", "/data/standard": "The data standard",
         "/data/faults": "Known faults in source data", "/digest": "The Energy Digest", "/roundup": "The Roundup", "/subscribe": "Subscribe"}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def day_words(day):
    d = dt.date.fromisoformat(day)
    return f"{d.day} {d:%B %Y}"


def table_status(coverage=COVERAGE, status=STATUS, tables=TABLES):
    """{table: {status, publishers (the deciding ones of a held table), all_publishers, hold (whole or by grid), from,
    permission, flag (coverage's), sector}} for every table of coverage."""
    held = {r["table"]: r for r in rows(status)}
    pubs = {r["table"]: [p for p in r["publishers"].split("; ") if p] for r in rows(tables)}
    out = {}
    for r in rows(coverage):
        t = r["table"]
        h = held.get(t)
        deciding = [p for p in (h or {}).get("publishers", "").split("; ") if p]
        if r["license"] != PUBLIC:
            st = INTERNAL
        elif h and h["status"] == NEEDED:
            st = NEEDED
        else:
            st = PUBLIC
        out[t] = {"status": st, "publishers": deciding if st == NEEDED else [], "all_publishers": pubs.get(t, []),
                  "hold": (BY_GRID if deciding and all(p in GRIDS for p in deciding) else WHOLE) if st == NEEDED else "",
                  "from": (h or {}).get("from", "") if st == NEEDED else "", "permission": (h or {}).get("permission", ""),
                  "flag": r["license"], "sector": r.get("sector", "")}
    return out


def release(path=RELEASE):
    """{route: live or review} as site/lib/release.ts lists them."""
    import re
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
    except OSError:
        return {}
    return {m.group(1): m.group(2) for m in re.finditer(r'^\s*"(/[^"]*)":\s*"(live|review)"', src, re.M)}


def page_rows(status, pages):
    """[{route, label, tables, needed, internal, public, dark}] for every page that has a page file."""
    out = []
    for route, v in pages.items():
        if "error" in v:
            continue
        ts = [t for t in page_tables.tables_of(v) if t in status]
        need = [t for t in ts if status[t]["status"] == NEEDED]
        internal = [t for t in ts if status[t]["status"] == INTERNAL]
        open_ = [t for t in ts if status[t]["status"] == PUBLIC]
        # dark: every table the page reads is held whole (or internal). A table held by grid keeps its other grids'
        # rows, so a page that reads one is partly dark, however many of its tables are held
        by_grid = [t for t in need if status[t]["hold"] == BY_GRID]
        dark = "none" if not need else ("all" if not open_ and not by_grid else "part")
        out.append({"route": route, "label": v.get("label", "") or NAMES.get(route, route), "tables": ts, "needed": need, "internal": internal, "public": open_,
                    "dark": dark})
    return out


def build(coverage=COVERAGE, status=STATUS, tables=TABLES, site=page_tables.SITE):
    st = table_status(coverage, status, tables)
    pages = page_tables.read(site, coverage)
    pr = page_rows(st, pages)
    reads = {}
    for p in pr:
        for t in p["tables"]:
            reads.setdefault(t, []).append(p["route"])
    return st, pr, reads


def site_keys(st, pr, reads):
    """The two keys this adds to site/data/license_status.json. "tables" (session 207) is left as it is: the site's
    reader (site/lib/license.ts) reads that key and no other.

    This file names no internal table. tests/test_session149.py holds one internal table's name out of every file
    under site/ (session 248's first build put it here and that test said so); some pages do name the internal tables
    they read behind the internal view, but a data file that every page's reader imports is no place to add 33 more
    names. So "all" holds the public and the "license needed" tables by name and the internal ones as a count, and a
    page's internal tables are a count too. Their names are in the document under docs/state/."""
    return {
        "all": {t: {"status": v["status"], **({"hold": v["hold"], "publishers": v["publishers"]} if v["status"] == NEEDED else {}), "pages": sorted(reads.get(t, []))}
                for t, v in sorted(st.items()) if v["status"] != INTERNAL},
        "internal_tables": sum(1 for v in st.values() if v["status"] == INTERNAL),
        "pages": {p["route"]: {"label": p["label"], "dark": p["dark"], "license_needed": p["needed"], "internal": len(p["internal"]), "public": len(p["public"])}
                  for p in pr if p["tables"]},
    }


def document(st, pr, reads, day, written, branch=""):
    n = {s: sum(1 for v in st.values() if v["status"] == s) for s in (PUBLIC, NEEDED, INTERNAL)}
    whole = sorted(t for t, v in st.items() if v["hold"] == WHOLE)
    by_grid = sorted(t for t, v in st.items() if v["hold"] == BY_GRID)
    dark = [p for p in pr if p["dark"] == "all"]
    part = [p for p in pr if p["dark"] == "part"]
    unread_needed = sorted(t for t, v in st.items() if v["status"] == NEEDED and not reads.get(t))
    deciders = {}
    for t, v in st.items():
        for p in v["publishers"]:
            deciders.setdefault(p, []).append(t)
    rel = release()
    L = []
    w = L.append
    w(f"# The license table for {day_words(day)}")
    w("")
    w(f"Energy Research Warehouse (ERW), session 248. Written by `python scripts/license_state.py` on {written} from four sources and nothing typed: "
      "`warehouse/metadata/coverage.csv` (every table and its flag), `warehouse/metadata/license_status.csv` (the tables flagged public whose publisher "
      "asks for permission, session 207), `warehouse/metadata/license_tables.csv` (each table's publishers) and the site's own code (which tables each "
      "page reads, `scripts/page_tables.py`" + (f", as it stood on `{branch}`" if branch else "") + "). `python scripts/license_state.py --check` says whether it still agrees with them.")
    w("")
    w("## Read these first")
    w("")
    w(f"- **{len(st)} tables: {n[PUBLIC]} public, {n[NEEDED]} \"license needed\", {n[INTERNAL]} internal.**")
    w(f"- **From {day_words(day)} a \"license needed\" table shows those words on the site in place of its numbers,** unless a permission is recorded in its row of "
      "`warehouse/metadata/license_status.csv` (the columns `permission` and `permission_ref`, filled by a person). Nothing changes before that day. The public day moved "
      "from 20 to 21 October by the ruling of 12 October 2026, night (`docs/roadmap.md`); this session moved the status file's day with it.")
    w(f"- **{len(dark)} pages go dark and {len(part)} go partly dark.** Dark: every table the page reads is held whole. Partly: some of its tables are held, or a table "
      "is held for some grids' rows only, and the page keeps the rest.")
    w(f"- **{len(by_grid)} of the {n[NEEDED]} tables are held by grid, not whole:** their deciding publishers are grid operators, so the rows of those grids read "
      f"\"license needed\" and the other grids' rows stay. The other {len(whole)} are held whole.")
    w("- **Who decides:** " + "; ".join(f"{p} ({len(ts)} tables)" for p, ts in sorted(deciders.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:8])
      + (f"; and {len(deciders) - 8} more publishers" if len(deciders) > 8 else "") + ".")
    w("- **A recorded permission turns a table back on by itself:** write the permission into the table's row, run `python scripts/licenses.py status` and this script, and land.")
    w("")
    w("## The pages that go dark or partly dark")
    w("")
    w("\"In review\" is the page's line in `site/lib/release.ts` today: a page in review shows a visitor the in-review page whatever its tables are, so the license shows only once the page is opened.")
    w("")
    w("| Page | Route | Today | Dark | License needed (whole) | License needed (by grid) | Internal, never shown | Tables it keeps |")
    w("|---|---|---|---|---|---|---|---|")

    def names(ts):
        return ", ".join(f"`{t}`" for t in ts) or ""
    for p in sorted(dark + part, key=lambda p: (p["dark"] != "all", p["route"])):
        nw = [t for t in p["needed"] if st[t]["hold"] == WHOLE]
        ng = [t for t in p["needed"] if st[t]["hold"] == BY_GRID]
        w(f"| {p['label'] or p['route']} | `{p['route']}` | {rel.get(p['route'], 'review')} | {'all of it' if p['dark'] == 'all' else 'partly'} | {names(nw)} | "
          + "; ".join(f"`{t}` ({', '.join(st[t]['publishers'])})" for t in ng) + f" | {names(p['internal'])} | {len(p['public'])} |")
    w("")
    w("## The pages no license touches")
    w("")
    clear = [p for p in pr if p["dark"] == "none"]
    w(", ".join(f"`{p['route']}`" + (f" ({len(p['tables'])})" if p["tables"] else "") for p in sorted(clear, key=lambda p: p["route"]))
      + ". The number is the tables the page reads; a page without one reads no table.")
    w("")
    w("## Every \"license needed\" table")
    w("")
    w("| Table | Held | Deciding publishers | From | Pages that read it |")
    w("|---|---|---|---|---|")
    for t in sorted(t for t, v in st.items() if v["status"] == NEEDED):
        v = st[t]
        w(f"| `{t}` | {v['hold']} | {'; '.join(v['publishers'])} | {v['from']} | {', '.join(f'`{r}`' for r in sorted(reads.get(t, []))) or 'no page reads it by name'} |")
    if unread_needed:
        w("")
        w(f"- {len(unread_needed)} of them are read by no page by name: {names(unread_needed)}. They are held in the data catalogue (`/data`) and for `/ask`.")
    w("")
    w("## Every internal table")
    w("")
    w("Internal by coverage's flag: in no public dataset, no download, and behind the internal view where a page reads it.")
    w("")
    w("| Table | Publishers | Pages that name it |")
    w("|---|---|---|")
    for t in sorted(t for t, v in st.items() if v["status"] == INTERNAL):
        w(f"| `{t}` | {'; '.join(st[t]['all_publishers'])} | {', '.join(f'`{r}`' for r in sorted(reads.get(t, []))) or ''} |")
    w("")
    w("## Every public table")
    w("")
    w("| Table | Publishers | Pages that read it |")
    w("|---|---|---|")
    for t in sorted(t for t, v in st.items() if v["status"] == PUBLIC):
        v = st[t]
        w(f"| `{t}`" + (" (permission recorded)" if v["permission"] else "") + f" | {'; '.join(v['all_publishers'])} | {', '.join(f'`{r}`' for r in sorted(reads.get(t, []))) or ''} |")
    w("")
    w("## What this table cannot say")
    w("")
    w("- **It reads names in code.** A table a page reads through a name built when the page runs is missed; a table named in a page's data file counts as read. "
      "The page's own code, through `site/lib/license.ts`, decides what a visitor sees.")
    w("- **A verdict is a session's reading of a publisher's sentence** (`docs/licenses.md`), not legal advice.")
    w("- **`/ask` and the data catalogue read every table of the live set,** so each held table is held there too, whether or not a page is listed for it.")
    w("")
    return "\n".join(L)


def write(day=None, check=False, out_doc=None, site_status=SITE_STATUS, branch="", written=None):
    with open(site_status, encoding="utf-8") as f:
        site = json.load(f)
    day = day or site["from"]
    st, pr, reads = build()
    doc_path = out_doc or os.path.join(ROOT, "docs", "state", f"licenses_{day}.md")
    if check and os.path.exists(doc_path):
        with open(doc_path, encoding="utf-8") as f:
            head = f.read(600)
        import re
        m = re.search(r"on (\d{4}-\d{2}-\d{2}) from four sources", head)
        written = m.group(1) if m else written
        m = re.search(r"as it stood on `([^`]+)`", head)
        branch = m.group(1) if m else branch
    written = written or dt.datetime.now(dt.timezone.utc).date().isoformat()
    text = document(st, pr, reads, day, written, branch)
    new_site = dict(site, **site_keys(st, pr, reads))
    if check:
        bad = []
        try:
            with open(doc_path, encoding="utf-8") as f:
                if f.read() != text:
                    bad.append(f"{os.path.relpath(doc_path, ROOT)} is not what the four sources give today")
        except OSError:
            bad.append(f"{os.path.relpath(doc_path, ROOT)} is not there")
        if site != new_site:
            bad.append(f"{os.path.relpath(site_status, ROOT)}: its keys \"all\", \"internal_tables\" and \"pages\" are not what the four sources give today")
        for b in bad:
            print(b)
        print(f"{len(st)} tables, {len(pr)} pages; {len(bad)} problems")
        return 1 if bad else 0
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    with open(doc_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(site_status, "w", encoding="utf-8", newline="\n") as f:
        json.dump(new_site, f, indent=1)
        f.write("\n")
    n = {s: sum(1 for v in st.values() if v["status"] == s) for s in (PUBLIC, NEEDED, INTERNAL)}
    print(f"{os.path.relpath(doc_path, ROOT)} and {os.path.relpath(site_status, ROOT)}: {len(st)} tables ({n[PUBLIC]} public, {n[NEEDED]} license needed, "
          f"{n[INTERNAL]} internal); {sum(1 for p in pr if p['dark'] == 'all')} pages dark, {sum(1 for p in pr if p['dark'] == 'part')} partly")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="the license table for the public day: every table's status and the pages it darkens (session 248)")
    ap.add_argument("--check", action="store_true", help="exit 1 when the document or the site's file is not what the sources give")
    ap.add_argument("--branch", default="", help="the branch whose page code is read, for the document's first paragraph")
    a = ap.parse_args(argv)
    return write(check=a.check, branch=a.branch)


if __name__ == "__main__":
    sys.exit(main())
