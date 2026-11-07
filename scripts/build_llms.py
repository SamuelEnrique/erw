#!/usr/bin/env python3
"""Write the catalogue of package/llms.txt from the repository's record (session 3298, platform tool 15).

Energy Research Warehouse (ERW). package/llms.txt is the briefing for AI readers; the site serves it at /llms.txt
(site/scripts/build-content.mjs copies it into content/llms.json) and the chat reads it (warehouse/chat/ask.py). Its
sections 0 to 9 are written by sessions. Its last section, the catalogue, is written by this script and by nothing
else, between the two marker lines BEGIN and END below; a file without them gets them appended at its end:

  every public table (the package's license verdict `public`, package/src/erw/licenses.py) with its one-line
    description, unit, period, granularity, license, method note path and download address;
  every held table (any other verdict) by name, "license needed", no figure;
  the periodicals, Ask and the tools' pages, each with the question it answers (site/lib/pages.ts);
  the date of generation, and the newest last_run of warehouse/metadata/coverage.csv it was built from.

Where each cell comes from (all committed files; no table is read, no request is made, no model is called):
  table list, period, granularity    warehouse/metadata/coverage.csv (ts_min, ts_max, interval)
  verdict, live-set window           the package's license record, erw.licenses.build (coverage.csv, docs/licenses.md,
                                     license_status.csv, live_set.yaml): the same list erw/data/tables.csv ships
  publishers                         warehouse/metadata/sources.csv (the rows whose `tables` name the table)
  description                        the title line of the table's provenance header as the Redivis release records
                                     hold it (docs/redivis/release-v1-stanford/tables.csv, else release-v1/tables.csv);
                                     else the source report sources.csv names
  unit                               the units of the table's variables and columns in the same release records
  method note                        build_coverage.method_notes(), the rule docs/coverage.md's Method column uses
  download address                   /api/download on the site for a table in the live set, else the table in the
                                     Stanford Redivis dataset when redivis_uploads_stanford.csv records its upload

The chat's system prompt leaves the catalogue out (ask.py, BRIEFING): its tools list the tables, and the catalogue
would multiply each question's cost. tests/test_session3298.py fails when the catalogue is older than coverage.csv's
newest row; warehouse/metadata/build_coverage.py runs this script after every build, so whatever rebuilds coverage
rewrites the catalogue.

    python scripts/build_llms.py            write the catalogue into package/llms.txt
    python scripts/build_llms.py --check    exit 1 when the catalogue differs from what the record gives (the date
                                            line aside), 0 when it agrees
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LLMS = ROOT / "package" / "llms.txt"
META = ROOT / "warehouse" / "metadata"
BEGIN = "<!-- BEGIN catalogue: written by scripts/build_llms.py, never by hand -->"
END = "<!-- END catalogue -->"
SITE = "https://erw-flame.vercel.app"
REDIVIS = "https://stanford.redivis.com/datasets/b9wm-3hb080mtm"
GRAIN = {"PT5M": "5-minute", "PT15M": "15-minute", "PT30M": "30-minute", "PT1H": "hourly", "P1D": "daily",
         "P1W": "weekly", "P1M": "monthly", "P3M": "quarterly", "P1Y": "yearly", "snapshot": "a snapshot (entities)",
         "event": "events, one row each"}
DESC_MAX = 220
RESTORED = re.compile(r"^(Energy Research Warehouse \(ERW\): )?Rebuilt from the ERW archive")


def rows(path):
    if not path.is_file():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def clean(text):
    """One line, no em or en dash (rule 2), no bar or backtick to break the line."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    text = text.replace(chr(0x2014), ", ").replace(chr(0x2013), "-").replace("`", "'")
    return text


def short(text, n=DESC_MAX):
    text = clean(text)
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + " [...]"


def listing(items, n=4):
    items = [i for i in items if i]
    if len(items) <= n:
        return ", ".join(items)
    return ", ".join(items[:n]) + f" and {len(items) - n} more"


def day(ts):
    return (ts or "")[:10]


def verdicts():
    sys.path.insert(0, str(ROOT / "package" / "src"))
    from erw import licenses
    return {r["table"]: r for r in licenses.build(ROOT)}


def method_notes():
    sys.path.insert(0, str(ROOT / "warehouse" / "metadata"))
    import build_coverage
    return dict(build_coverage.method_notes())


def publishers():
    out = {}
    for r in rows(META / "sources.csv"):
        for t in (r.get("tables") or "").split(";"):
            t = t.strip()
            if t:
                out.setdefault(t, []).append(r)
    return out


def release_records():
    """{table: description} and {table: [units]} from the Stanford record first, then the owner's v1 record."""
    desc, units = {}, {}
    for d in ("release-v1-stanford", "release-v1"):
        base = ROOT / "docs" / "redivis" / d
        for r in rows(base / "tables.csv"):
            # a table rebuilt from the archive (warehouse/restore_tables.py) has a restore note as its first header
            # line, not a title: the source report stands in for it
            if r.get("description") and r["table"] not in desc and not RESTORED.match(r["description"]):
                desc[r["table"]] = r["description"]
        seen = {}
        for r in rows(base / "variables.csv"):
            u = (r.get("unit") or "").strip()
            if u:
                seen.setdefault(r["table"], [])
                if u not in seen[r["table"]]:
                    seen[r["table"]].append(u)
        for t, us in seen.items():
            units.setdefault(t, us)
    # the tables uploaded to the Stanford dataset (its draft until a person releases a version)
    stanford = {r["table"] for r in rows(META / "redivis_uploads_stanford.csv")}
    return desc, units, stanford


def pages():
    """[(group, href, label, line)] from site/lib/pages.ts, in its order."""
    text = (ROOT / "site" / "lib" / "pages.ts").read_text(encoding="utf-8")
    text = text.split("export const GROUPS", 1)[1].split("export const PAGES", 1)[0]
    s = r'"((?:[^"\\]|\\.)*)"'
    out, group = [], ""
    for ln in text.splitlines():
        g = re.match(r'^\s*label: ' + s + r',\s*$', ln)
        if g:
            group = g.group(1)
            continue
        for m in re.finditer(r'\{ href: ' + s + r', label: ' + s + r', line: ' + s, ln):
            href = m.group(1)
            out.append(("Ask" if href == "/ask" else group, href, m.group(2).replace('\\"', '"'),
                        m.group(3).replace('\\"', '"')))
    hrefs = len(re.findall(r'\{ href: "', text))
    if hrefs != len(out):
        raise SystemExit(f"build_llms FAILED: site/lib/pages.ts has {hrefs} page entries, {len(out)} read; "
                         "an entry whose fields are not in the order href, label, line needs this reader extended")
    return out


def catalogue(today):
    cov = rows(META / "coverage.csv")
    if not cov:
        raise SystemExit("build_llms FAILED: warehouse/metadata/coverage.csv is missing or empty")
    ver = verdicts()
    notes = method_notes()
    pubs = publishers()
    desc, units, stanford = release_records()
    newest = max(r["last_run"] for r in cov if r.get("last_run"))
    public = [r for r in cov if ver.get(r["table"], {}).get("verdict") == "public"]
    held = [r for r in cov if r not in public]

    out = [BEGIN, "", "## 10. Every table: the catalogue (generated)", "",
           f"Generated: {today} by scripts/build_llms.py from warehouse/metadata/coverage.csv (newest last_run: "
           f"{newest}), warehouse/metadata/sources.csv, the package's license record (erw/data/tables.csv), the "
           "Redivis release records (docs/redivis/) and site/lib/pages.ts. Not edited by hand. The chat's briefing "
           "leaves this section out; its list_tables tool reads the same record.",
           "",
           f"{len(cov)} tables: {len(public)} public, {len(held)} held. Spans and rows move daily: "
           "erw.coverage() gives today's.",
           "",
           "Each public line: table: description. Unit. Period (UTC days of the first and last interval). "
           "Granularity. License (verdict; publishers). Method note (path in the repository; \"none yet\" where no "
           "note names the table). Download: the site's /api/download for a table the live set holds (its window "
           "in brackets; the full history on Redivis), else the table in the Redivis dataset `datapages.erw` (Stanford, "
           f"{REDIVIS}; an unreleased draft until a person releases a version, read with the dataset's access), "
           "else none yet. A description cut short ends in [...]; the full title is the table's provenance header.",
           "",
           f"### 10.1 Public tables ({len(public)})", ""]
    for r in public:
        t = r["table"]
        v = ver[t]
        d = desc.get(t, "").replace("Energy Research Warehouse (ERW): ", "", 1)
        if not d:
            reports = [f"{s.get('publisher', '')}, {s.get('report', '')}".strip(", ") for s in pubs.get(t, [])]
            d = (listing(reports, 2) if reports else r.get("source_report", "")) + " (the source report)"
        unit = listing(units.get(t, []), 6) or "not recorded in the release records (read the table's unit column)"
        if r.get("ts_min") and r.get("ts_max"):
            period = f"{day(r['ts_min'])} to {day(r['ts_max'])}"
        else:
            period = "not dated"
        grain = GRAIN.get(r.get("interval", ""), r.get("interval", "") or "not recorded")
        who = listing(sorted({s.get("publisher", "") for s in pubs.get(t, [])}), 4) or v.get("publishers", "") \
            or "publisher not in sources.csv"
        note = notes.get(t)
        method = f"docs/{note}" if note else "none yet"
        live = v.get("live_window", "")
        if live and live != "none":
            dl = f"{SITE}/api/download?table={t} ({live})"
        elif t in stanford:
            dl = f"Redivis datapages.erw, table {t}"
        else:
            dl = "none yet (not in the live set, not yet uploaded to Redivis)"
        out.append(f"- `{t}`: {short(d).rstrip('.')}. Unit: {clean(unit)}. Period: {period}. Granularity: {grain}. "
                   f"License: public ({clean(who)}). Method: {method}. Download: {dl}.")
    out += ["", f"### 10.2 Held tables ({len(held)}): license needed, no figures", "",
            "Not served by the site, the live set or Redivis; erw.license(t) gives the reason in one sentence.", ""]
    out += [f"- `{r['table']}`: license needed ({ver.get(r['table'], {}).get('verdict') or 'not in the record'})"
            for r in held]
    pg = pages()
    out += ["", "### 10.3 The periodicals, Ask and the tools' pages", "",
            f"Every page of the site (site/lib/pages.ts), its address on {SITE} and the question it answers. "
            "Every page is in review (site/lib/release.ts): a visitor sees the in-review page until the owner opens it.",
            ""]
    order = ["News", "Ask"] + [g for g in dict.fromkeys(p[0] for p in pg) if g not in ("News", "Ask")]
    for g in order:
        items = [p for p in pg if p[0] == g]
        if not items:
            continue
        head = {"News": "The periodicals", "Ask": "Ask"}.get(g, f"The tools' pages, {g}")
        out += [f"{head}:"]
        out += [f"- {href} ({clean(label)}): {clean(line)}" for _, href, label, line in items]
        out += [""]
    out += [END]
    return "\n".join(out) + "\n"


def splice(text, block):
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        tail = rest.split(END, 1)[1]
        return head + block.rstrip("\n") + tail
    return text.rstrip("\n") + "\n\n" + block


def strip_date(text):
    return re.sub(r"^Generated: \S+ by", "Generated: <date> by", text, flags=re.M)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    old = LLMS.read_text(encoding="utf-8").replace("\r\n", "\n")
    new = splice(old, catalogue(now))
    if a.check:
        same = strip_date(old) == strip_date(new)
        print(f"package/llms.txt catalogue {'agrees with' if same else 'DIFFERS from'} the record"
              + ("" if same else ": run python scripts/build_llms.py"))
        return 0 if same else 1
    with open(LLMS, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    n_pub = new.split("### 10.1 Public tables (", 1)[1].split(")", 1)[0]
    n_held = new.split("### 10.2 Held tables (", 1)[1].split(")", 1)[0]
    print(f"wrote package/llms.txt's catalogue: {n_pub} public, {n_held} held, generated {now}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
