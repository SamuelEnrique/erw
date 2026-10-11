"""Check docs/positioning.md (session 189): the ERW beside Grid Status and Electricity Maps.

What is held to, and what a failure means:

  1. no em dash in the document, in the session report or in this file;
  2. every address (http...) in the document stands in a table of section 8;
  3. every source marker ([G4], [E3], [L1]) used in the text has a row in section 8;
  4. every repository pointer in backticks exists: a path is a file or folder of this repository, a site address is a
     line of site/lib/release.ts, a table name is a row of warehouse/metadata/coverage.csv; a backticked word that is
     none of these and is not in the short list below fails, so that nothing is left unchecked;
  5. every repository file cited in sections 1 to 7 stands in section 8.4;
  6. the dependency as the document states it: exactly three files of the repository import the gridstatus library,
     requirements.txt pins the version the document names, and no code names the hosted Grid Status service or
     Electricity Maps;
  7. the dated statements (with --strict a failure, without it a note): every page is in review, and the table counts;
  8. when the session's saved copies are on the machine (runs/session189/pages, which git ignores): every quoted
     passage is found in a saved copy or in a cited repository file, and every short hash in section 8.1 is the
     hash of its copy. Without the copies this part is skipped and said.

No request and no model call. Exit 0: all held. Exit 1: something failed. Exit 2: the document is missing.

    python scripts/check_positioning.py [--strict]
"""
import csv
import hashlib
import html
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOC = os.path.join(ROOT, "docs", "positioning.md")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_189_REPORT.md")
PAGES = os.path.join(ROOT, "runs", "session189", "pages")
EM = chr(0x2014)

# Backticked words that are not pointers into this repository: names of the two companies' software and paths, the
# data standard's column names, a status word and a function of the package.
NOT_POINTERS = {"gridstatus", "gridstatusio", "review", "source", "source_url", "retrieved_at", "erw.cite()",
                "/past", "/past-range", "/history", "/latest", "/forecast", "/auth", "/locales"}
# Paths that are real but not in git: the installed library, and the session's saved copies.
NOT_IN_GIT = ("gridstatus-0.36.0.dist-info/", "runs/session189/")
# Section 8.1's rows whose copy was kept, and the file each was kept as.
COPIES = {"G2": "gs_llms.txt", "G4": "gs_docs_llms.txt", "G5": "gs_welcome.md", "G6": "gs_api_start.md",
          "G7": "gs_rate_limits.md", "G8": "gs_catalog.md", "G9": "gs_insights.md", "G10": "gs_snowflake.md",
          "G11": "gs_readme.md", "E2": "em_home.html", "E3": "em_pricing.html", "E4": "em_data.html",
          "E5": "em_methodology.html", "E6": "em_api.html", "E7": "em_readme.md", "E8": "em_app_robots.txt",
          "E9": "em_help_robots.txt"}
CODE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".mjs", ".sh", ".ps1", ".yml", ".yaml", ".toml", ".cfg", ".json")
IMPORTERS = {"warehouse/connectors/iso_prices.py", "warehouse/connectors/latest_prices.py",
             "warehouse/connectors/iso_queues.py"}

failures, notes = [], []


def fail(msg):
    failures.append(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def flat(text):
    """Text as one line: tags out, entities read, curly quotation marks straight, one space between words."""
    text = re.sub(r"<[^>]*>", " ", text)
    text = html.unescape(text)
    for a, b in ((chr(0x2019), "'"), (chr(0x2018), "'"), (chr(0x201C), '"'), (chr(0x201D), '"'), (chr(0xA0), " ")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text)


def tracked():
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True, check=True).stdout
        return [l for l in out.splitlines() if l]
    except Exception:
        found = []
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".next", ".venv", "runs", "__pycache__")]
            for f in files:
                found.append(os.path.relpath(os.path.join(base, f), ROOT).replace(os.sep, "/"))
        return found


def library_text():
    """The installed gridstatus distribution's METADATA and LICENSE, or nothing when it is not installed."""
    try:
        from importlib import metadata
        dist = metadata.distribution("gridstatus")
        return " ".join(["version %s" % dist.version, dist.read_text("METADATA") or "", dist.read_text("licenses/LICENSE") or ""])
    except Exception:
        return ""


def library_own_servers():
    """Lines of the installed gridstatus library's code (its tests left out) that name a Grid Status host, as
    'file:line'. None when the library is not installed. The document says the library asks the grid operators and
    the EIA, never Grid Status's own servers."""
    try:
        from importlib import util
        spec = util.find_spec("gridstatus")
        base = os.path.dirname(spec.origin)
    except Exception:
        return None
    hits = []
    for folder, dirs, names in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("tests", "__pycache__")]
        for name in names:
            if not name.endswith(".py"):
                continue
            path = os.path.join(folder, name)
            try:
                lines = read(path).splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(lines, 1):
                if re.search(r"gridstatus\.(io|com)", line, flags=re.I):
                    hits.append("%s:%d" % (os.path.relpath(path, base).replace(os.sep, "/"), i))
    return hits


def main():
    strict = "--strict" in sys.argv[1:]
    if not os.path.isfile(DOC):
        print("docs/positioning.md is not there")
        return 2
    doc = read(DOC)
    cut = doc.index("\n## 8. Sources")
    body, sources = doc[:cut], doc[cut:]
    cited_files = sources[sources.index("### 8.4"):]

    # 1. no em dash
    for path in (DOC, REPORT, os.path.abspath(__file__)):
        if os.path.isfile(path) and EM in read(path):
            fail("an em dash in %s" % os.path.relpath(path, ROOT))
    if not os.path.isfile(REPORT):
        notes.append("the session report is not written yet, so it was not scanned for an em dash")

    # 2. every address is in section 8
    urls_all = set(re.findall(r"https?://[^\s`|)\]]+", doc))
    urls_sources = set(re.findall(r"https?://[^\s`|)\]]+", sources))
    for u in sorted(urls_all - urls_sources):
        fail("an address outside section 8: %s" % u)

    # 3. every marker has a row
    rows = set(re.findall(r"^\| ([GEL]\d+) \|", sources, flags=re.M))
    used = set(re.findall(r"\[([GEL]\d+)\]", body))
    for m in sorted(used - rows):
        fail("marker [%s] has no row in section 8" % m)
    for m in sorted(rows - used):
        notes.append("row %s of section 8 is cited nowhere in the text" % m)

    # 4. every backticked pointer exists
    release = read(os.path.join(ROOT, "site", "lib", "release.ts"))
    pages = dict(re.findall(r'^\s*"(/[^"]*)":\s*"(live|review)"', release, flags=re.M))
    with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
        coverage = list(csv.DictReader(f))
    tables = {r["table"] for r in coverage}
    paths_in_body = set()
    for tick in sorted(set(re.findall(r"`([^`]+)`", doc))):
        if tick in NOT_POINTERS or tick.startswith("http") or re.fullmatch(r"[0-9a-f]{12}", tick):
            continue
        if tick.startswith(NOT_IN_GIT):
            continue
        if tick.startswith("/"):
            if tick not in pages:
                fail("site address %s is not a line of site/lib/release.ts" % tick)
            continue
        if "/" in tick or re.search(r"\.(md|txt|py|ts|csv|yml)$", tick):
            if not os.path.exists(os.path.join(ROOT, tick)):
                fail("path %s does not exist" % tick)
            if "`%s`" % tick in body:
                paths_in_body.add(tick)
            continue
        if re.fullmatch(r"[a-z0-9]+(_[a-z0-9]+)+", tick):
            if tick not in tables:
                fail("table %s is not a row of warehouse/metadata/coverage.csv" % tick)
            continue
        fail("a backticked word that is no path, address or table, and is not in the list: %s" % tick)

    # 5. every cited file is in section 8.4
    for p in sorted(paths_in_body):
        if "`%s`" % p not in cited_files:
            fail("%s is cited in the text and missing from section 8.4" % p)

    # 6. the dependency
    files = tracked()
    me = "scripts/check_positioning.py"
    importers, hosted = set(), []
    for rel in files:
        if not rel.endswith(CODE_SUFFIXES) and not re.fullmatch(r"requirements[^/]*\.txt", rel):
            continue
        if rel == me or rel.startswith("site/node_modules/"):
            continue
        try:
            text = read(os.path.join(ROOT, rel))
        except (OSError, UnicodeDecodeError):
            continue
        if rel.endswith(".py") and re.search(r"^\s*(import gridstatus\b|from gridstatus\b)", text, flags=re.M):
            importers.add(rel)
        if re.search(r"gridstatusio|api\.gridstatus\.io|electricity ?maps", text, flags=re.I):
            hosted.append(rel)
    if importers != IMPORTERS:
        fail("the files importing gridstatus are %s, and the document names %s" % (sorted(importers), sorted(IMPORTERS)))
    for rel in hosted:
        fail("code names the hosted Grid Status service or Electricity Maps: %s" % rel)
    pin = re.search(r"^gridstatus==(\S+)", read(os.path.join(ROOT, "requirements.txt")), flags=re.M)
    if not pin or ("version %s" % pin.group(1)) not in doc:
        fail("requirements.txt pins gridstatus %s and the document does not name that version" % (pin.group(1) if pin else "nothing"))
    own = library_own_servers()
    if own is None:
        notes.append("the gridstatus library is not installed for this Python: its code was not searched for Grid Status's own servers")
    for hit in own or []:
        fail("the installed gridstatus library names one of Grid Status's own servers: %s" % hit)

    # 7. the dated statements
    dated = []
    live = sorted(p for p, s in pages.items() if s == "live")
    if live:
        dated.append("the document says every page is in review; site/lib/release.ts now has live: %s" % ", ".join(live))
    n, pub = len(coverage), sum(1 for r in coverage if r["license"] == "public")
    said = re.search(r"lists (\d+) tables: (\d+) public and (\d+) internal", doc)
    if not said:
        fail("the sentence with the table counts is not in the document")
    elif (int(said.group(1)), int(said.group(2)), int(said.group(3))) != (n, pub, n - pub):
        dated.append("the document says %s tables, %s public, %s internal; coverage.csv now has %d, %d, %d"
                     % (said.group(1), said.group(2), said.group(3), n, pub, n - pub))
    for d in dated:
        (fail if strict else notes.append)("dated: " + d)

    # 8. quotations and hashes, when the saved copies are here
    if os.path.isdir(PAGES):
        hay = []
        for name in sorted(os.listdir(PAGES)):
            if name.endswith((".md", ".txt", ".html")):
                with open(os.path.join(PAGES, name), encoding="utf-8", errors="replace") as f:
                    hay.append(flat(f.read()))
        for p in sorted(set(re.findall(r"`([^`]+)`", cited_files))):
            full = os.path.join(ROOT, p)
            if os.path.isfile(full) and not p.endswith(".csv"):
                hay.append(flat(read(full)))
        hay.append(flat(read(os.path.join(ROOT, "docs", "platform-tools.md"))))
        lib = library_text()
        if lib:
            hay.append(flat(lib))
        else:
            notes.append("the gridstatus library is not installed for this Python: its license text was not read")
        quotes = []
        for line in body.splitlines():
            if line.count('"') % 2:
                fail("a line with an odd number of quotation marks: %s" % line[:80])
                continue
            quotes += [q for q in re.findall(r'"([^"]*)"', flat(line)) if q.strip()]
        missing = [q for q in quotes if not any(q in h or q.rstrip(".,;") in h for h in hay)
                   and not (not lib and "James Max Kanter" in q)]
        for q in missing:
            fail("a quotation found in no saved copy and no cited file: %r" % q)
        notes.append("quotations checked against the saved copies and the cited files: %d, not found: %d" % (len(quotes), len(missing)))
        for m, name in sorted(COPIES.items()):
            row = re.search(r"^\| %s \|.*\| `([0-9a-f]{12})` \|\s*$" % m, sources, flags=re.M)
            path = os.path.join(PAGES, name)
            if not row or not os.path.isfile(path):
                fail("row %s of section 8.1 has no hash, or its copy %s is not on the machine" % (m, name))
                continue
            with open(path, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()[:12]
            if h != row.group(1):
                fail("row %s: the document says %s and the copy is %s" % (m, row.group(1), h))
    else:
        notes.append("the saved copies (runs/session189/pages) are not on this machine: quotations and hashes not checked")

    for n_ in notes:
        print("note: " + n_)
    for f_ in failures:
        print("FAIL: " + f_)
    print("positioning check: %d failed, %d notes%s" % (len(failures), len(notes), ", strict" if strict else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
