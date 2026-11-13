#!/usr/bin/env python3
"""A verdict confirmed against the publisher's current page (chain 229, session 4101: the licensing sweep, roadmap item 5).

Energy Research Warehouse (ERW). docs/licenses.md rests on one read of each publisher's terms page, most of them made
in October 2026. This script checks a verdict again against a page read now, and records what it found, without a
sentence ever being typed by hand:

    python scripts/license_confirm.py robots N --path /legal/terms        # read N is a robots file: may the page be asked?
    python scripts/license_confirm.py find KEY N                           # is KEY's quoted sentence on read N's page?
    python scripts/license_confirm.py cut N --grep copyright reproduce     # read N's sentences that hold a word, numbered
    python scripts/license_confirm.py confirm KEY N --note "..."           # write a row of license_confirmations.csv
    python scripts/license_confirm.py verdict KEY N --pick 7 --verdict "may be public" --if-commercial "may be public"
                                          [--contact ...] [--price ...] [--note ...] [--replace]
                                                                           # KEY's verdict, its sentence cut from read N

The reads themselves are made by scripts/license_read.py, one request a label: a re-read takes a new label, as
"<publisher>, current terms (session 4101)", and the host's robots file is read first as its own row of the record.
The bytes are kept outside git (--keep), as license_read.py keeps them; this script finds a read's folder by its
number under the folders it is given (--pages, any number of them).

A confirmation row says: the publisher's key, the new read's number and time, whether the verdict's sentence is on
the new page word for word (after the page's markup is taken away and runs of space are made one), the verdict
before and after, and a note. A sentence no longer on the page is never confirmed: the row says "changed", and the
verdict is cut again from the new page (verdict ... --replace) or the publisher waits for a session that does.

robots answers for the ERW's own agent and for every agent a host may name to refuse Anthropic's crawlers
(ClaudeBot, anthropic-ai, Claude-User, Claude-SearchBot), and prints the file's rules with its comments taken away.
A refusal for any of them is a refusal: the page is not asked.

Nothing here asks the network, writes data, or changes coverage.csv.
"""

import argparse
import csv
import datetime as dt
import glob
import html
import io
import os
import re
import sys
import urllib.robotparser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
META = os.path.join(ROOT, "warehouse", "metadata")
READS = os.path.join(META, "license_reads.csv")
VERDICTS = os.path.join(META, "license_verdicts.csv")
CONFIRMATIONS = os.path.join(META, "license_confirmations.csv")
CONF_COLS = ["key", "read", "read_at", "sentence", "verdict_before", "verdict_after", "session", "note"]
VERDICT_COLS = ["key", "read", "sentence", "verdict", "if_commercial", "contact", "price", "note"]
FOUR = ("may be public", "needs written permission", "needs a paid license", "forbidden")
AGENTS = ("ERW-connector", "ClaudeBot", "anthropic-ai", "Claude-User", "Claude-SearchBot")
DEFAULT_PAGES = [os.path.join(ROOT, "runs", "license_reads"), os.path.join(os.path.dirname(ROOT), "erw-w3-work", "license_reads"),
                 os.path.join(os.path.dirname(ROOT), "erw", "runs", "license_reads")]
SESSION = os.environ.get("ERW_SESSION", "")


def rows(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path, cols, data):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in data:
            w.writerow({c: r.get(c, "") for c in cols})


def read_row(n, reads=None):
    for r in reads if reads is not None else rows(READS):
        if r["n"] == str(n):
            return r
    raise SystemExit(f"no read {n} in {READS}")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:50]


def page_path(n, pages, reads=None):
    """The saved bytes of read n: <a pages folder>/<n, two digits or more>_<slug of the publisher>/page.bin."""
    r = read_row(n, reads)
    name = f"{int(n):02d}_{slug(r['publisher'])}"
    for base in pages:
        p = os.path.join(base, name, "page.bin")
        if os.path.exists(p):
            return p
        hits = glob.glob(os.path.join(base, "*", name, "page.bin"))
        if hits:
            return hits[0]
    raise SystemExit(f"read {n}'s page is not under {pages} (looked for {name}/page.bin)")


def text_of(raw, content_type=""):
    """The words of a saved page: a PDF's text, or an HTML page without its scripts, styles and tags; runs of space one."""
    if raw[:5] == b"%PDF-" or "pdf" in (content_type or ""):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            t = "\n".join((p.extract_text() or "") for p in pdf.pages)
    else:
        s = raw.decode("utf-8", errors="replace")
        if (content_type or "").startswith("text/plain"):
            # a plain text file (a README, a robots file): a reStructuredText link `words <address>`__ keeps its words
            t = re.sub(r"`([^`<]+?)\s*<[^>]*>`_{1,2}", r"\1", s)
        elif "<" in s and ">" in s:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(s, "lxml")
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()
            t = soup.get_text(" ")
        else:
            t = s
    return norm(html.unescape(t))


def norm(s):
    for code, plain in ((0xA0, " "), (0x2019, "'"), (0x2018, "'"), (0x201C, '"'), (0x201D, '"')):
        s = s.replace(chr(code), plain)
    for code in (0x200B, 0x200C, 0x200D, 0xFEFF):
        s = s.replace(chr(code), "")
    s = re.sub(r"\s+", " ", s)
    return re.sub(r" ([.,;:!?)])", r"\1", s).replace("( ", "(").strip()


def sentences(text):
    """The page's sentences: cut at a full stop, a question or an exclamation mark followed by a space and a capital,
    a digit or an opening quote."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])|\s+\*\s+(?=[A-Z])", text)   # a bullet ("* The ...") starts one too
    return [p.strip() for p in parts if len(p.strip()) > 2]


def robots(n, path, pages, out=print):
    """0: every agent may fetch path; 1: some agent is refused (the page is not asked); 2: the file could not be read."""
    r = read_row(n)
    if not r["outcome"].startswith("read"):
        if r["http_status"] in ("404", "410"):
            out(f"read {n}: no robots file (HTTP {r['http_status']}): every agent may fetch")
            return 0
        if r["http_status"] == "200" and r["bytes"] == "0":
            out(f"read {n}: an empty robots file (HTTP 200, 0 bytes): every agent may fetch")
            return 0
        out(f"read {n}: the robots file was not read ({r['outcome']}): treated as a refusal")
        return 2
    raw = open(page_path(n, pages), "rb").read().decode("utf-8", errors="replace")
    lines = [ln.split("#", 1)[0].rstrip() for ln in raw.splitlines()]
    out("rules (comments taken away):")
    for ln in lines:
        if ln.strip():
            out("  " + ln.strip())
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(lines)
    named = sorted({ln.split(":", 1)[1].strip() for ln in lines if ln.lower().startswith("user-agent")})
    bad = [a for a in AGENTS if not rp.can_fetch(a, path)]
    for a in AGENTS:
        out(f"{a}: {'may fetch' if a not in bad else 'REFUSED'} {path}")
    named_ai = [a for a in named if re.search(r"(?i)claude|anthropic|\bai\b|gpt|ccbot", a)]
    if named_ai:
        out(f"agents named that concern AI crawlers: {', '.join(named_ai)}")
    delay = rp.crawl_delay("ERW-connector") or rp.crawl_delay("*")
    if delay:
        out(f"crawl delay: {delay} s")
    return 1 if bad else 0


def find(key, n, pages, out=print):
    v = {r["key"]: r for r in rows(VERDICTS)}.get(key)
    if v is None:
        raise SystemExit(f"no verdict for {key!r} in {VERDICTS}")
    r = read_row(n)
    text = text_of(open(page_path(n, pages), "rb").read(), r["content_type"])
    s = norm(v["sentence"])
    if not s:
        out(f"{key}: its verdict quotes no sentence (read {v['read'] or 'none'}); nothing to find")
        return None
    miss = [q for q in pieces(s) if q not in text]
    hit = not miss
    out(f"{key}: the sentence of read {v['read']} is {'ON' if hit else 'NOT on'} read {n}'s page ({len(text)} characters)"
        + ("" if hit else f"; first piece missing: {miss[0][:160]!r}"))
    return hit


def pieces(s):
    """A quoted sentence's pieces: a verdict may join passages of one page with "[...]" or put a note in brackets
    ("[The site's footer:]"); each passage of more than 15 characters must be on the page word for word."""
    parts = re.split(r"\[[^\]]*\]|\.\.\.|" + chr(0x2026), s)
    return [q.strip(" \"'") for q in parts if len(q.strip(" \"'")) > 15]


def cut(n, words, pages, out=print):
    r = read_row(n)
    sents = sentences(text_of(open(page_path(n, pages), "rb").read(), r["content_type"]))
    rx = re.compile("|".join(re.escape(w) for w in words), re.I) if words else None
    for i, s in enumerate(sents):
        if rx is None or rx.search(s):
            out(f"[{i}] {s[:1200]}")
    return sents


def confirm(key, n, note="", session=None, pages=None, out=print):
    session = SESSION if session is None else session
    verdicts = {r["key"]: r for r in rows(VERDICTS)}
    v = verdicts.get(key)
    if v is None:
        raise SystemExit(f"no verdict for {key!r}")
    r = read_row(n)
    hit = find(key, n, pages, out=lambda *_: None) if v["sentence"] else None
    state = "on the page" if hit else ("no sentence quoted" if hit is None else "changed: not on the page")
    data = [c for c in rows(CONFIRMATIONS) if not (c["key"] == key and c["read"] == str(n))]
    data.append(dict(key=key, read=str(n), read_at=r["read_at"], sentence=state, verdict_before=v["verdict"],
                     verdict_after=v["verdict"] if hit or hit is None else "", session=session, note=note))
    write_rows(CONFIRMATIONS, CONF_COLS, data)
    out(f"{key}: read {n}, sentence {state}; verdict {v['verdict']}" + ("" if hit or hit is None else ": NOT confirmed; cut again with verdict --replace"))
    return state


def verdict(key, n, pick, value, if_commercial, contact="", price="", note="", replace=False, pages=None, out=print):
    if value not in FOUR or if_commercial not in FOUR:
        raise SystemExit(f"a verdict is one of {FOUR}")
    r = read_row(n)
    if str(pick) == "none":
        # no page could be read (a refusal by robots, an HTTP error): no sentence, never public, and the note says so
        if value == FOUR[0] or not note.startswith("NOT READ"):
            raise SystemExit("a verdict with no sentence is never 'may be public', and its note begins 'NOT READ'")
        sentence = ""
    else:
        if not r["outcome"].startswith("read"):
            raise SystemExit(f"read {n} was not read ({r['outcome']}): no sentence can be cut from it")
        sents = sentences(text_of(open(page_path(n, pages), "rb").read(), r["content_type"]))
        picks = [int(p) for p in str(pick).split("+")]
        sentence = sents[picks[0]]
        for a, b in zip(picks, picks[1:]):          # passages that are not next to each other are joined with "[...]"
            sentence += (" " if b == a + 1 else " [...] ") + sents[b]
    data = rows(VERDICTS)
    old = next((x for x in data if x["key"] == key), None)
    if old and not replace:
        raise SystemExit(f"{key} has a verdict (read {old['read']}): pass --replace to cut it again from read {n}")
    row = dict(key=key, read=str(n), sentence=sentence, verdict=value, if_commercial=if_commercial, contact=contact, price=price, note=note)
    if old:
        before = old["verdict"]
        data = [row if x["key"] == key else x for x in data]
    else:
        before = ""
        data.append(row)
    write_rows(VERDICTS, VERDICT_COLS, data)
    if old:
        conf = [c for c in rows(CONFIRMATIONS) if not (c["key"] == key and c["read"] == str(n))]
        conf.append(dict(key=key, read=str(n), read_at=r["read_at"], sentence="cut again from this page", verdict_before=before,
                         verdict_after=value, session=SESSION, note=note))
        write_rows(CONFIRMATIONS, CONF_COLS, conf)
    out(f"{key}: verdict {value} (if sold: {if_commercial}) from read {n}, sentence [{pick}]: {sentence[:300]}")
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description="A verdict confirmed against the publisher's current page (session 4101)")
    ap.add_argument("--pages", action="append", help="a folder of saved reads (license_read.py's --keep); may repeat")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("robots"); a.add_argument("n"); a.add_argument("--path", required=True)
    a = sub.add_parser("find"); a.add_argument("key"); a.add_argument("n")
    a = sub.add_parser("cut"); a.add_argument("n"); a.add_argument("--grep", nargs="*", default=[])
    a = sub.add_parser("confirm"); a.add_argument("key"); a.add_argument("n"); a.add_argument("--note", default="")
    a = sub.add_parser("verdict"); a.add_argument("key"); a.add_argument("n"); a.add_argument("--pick", required=True)
    a.add_argument("--verdict", required=True); a.add_argument("--if-commercial", required=True)
    a.add_argument("--contact", default=""); a.add_argument("--price", default=""); a.add_argument("--note", default="")
    a.add_argument("--replace", action="store_true")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pages = a.pages or DEFAULT_PAGES
    if a.cmd == "robots":
        return robots(a.n, a.path, pages)
    if a.cmd == "find":
        hit = find(a.key, a.n, pages)
        return 0 if hit else 1
    if a.cmd == "cut":
        cut(a.n, a.grep, pages)
        return 0
    if a.cmd == "confirm":
        state = confirm(a.key, a.n, a.note, pages=pages)
        return 0 if not state.startswith("changed") else 1
    verdict(a.key, a.n, a.pick, a.verdict, a.if_commercial, a.contact, a.price, a.note, a.replace, pages=pages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
