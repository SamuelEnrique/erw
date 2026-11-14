"""Read one public document for the large-load research pass, robots first, and keep its text with page marks.

Energy Research Warehouse (ERW), session 5300 (portable laptop, window P4). Used by the research subagents and by the
spot-check: the subagents read documents only through this script, so that every quote can be matched again against
the very text that was read, with no second request.

    python -I fetch_doc.py URL                    fetch (or reuse the cached copy), print where the text is
    python -I fetch_doc.py URL --grep REGEX       also print each matching line with its page, two lines around
    python -I fetch_doc.py URL --links [REGEX]    an HTML page: print its links (absolute), optionally filtered
    python -I fetch_doc.py URL --page N           print page N of a PDF's text (the whole text of an HTML page)

What it does:
- refuses a paused publisher (warehouse/metadata/paused_sources.csv: MISO, the Virginia SCC) and a host whose terms or
  answers bar this reader (Con Edison, Eversource, Duquesne Light), with no request;
- reads the host's robots.txt for the agent "ERW-research-reader" and for "*", and refuses a disallowed path;
- waits at least 3 seconds between two requests to the same host;
- saves the answer in its own new folder under runs/s5300/docs/<sha1 of the URL, 16>/ (raw file, meta.json);
- a PDF is turned into text with pdftotext twice: reading order (text.txt) and layout (layout.txt); pages are split by
  form feeds, and the page numbers printed are the PDF's own page order, starting at 1;
- an HTML page is turned into text (text.txt) by dropping tags, scripts and styles;
- a page that looks like a bot check (captcha, a challenge) is marked "blocked" and never retried with another agent.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import html.parser
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CACHE = os.path.join(ROOT, "runs", "s5300", "docs")
HOSTLOG = os.path.join(ROOT, "runs", "s5300", "hosts")
AGENT = "ERW-research-reader"
# This reader is driven by Claude, so a robots file that bars Anthropic's agents by name bars it too (session 2873:
# the NCUC's portal names ClaudeBot, anthropic-ai and Claude-Web).
AGENTS = (AGENT, "*", "ClaudeBot", "Claude-User", "Claude-Web", "Claude-SearchBot", "anthropic-ai")
UA = "Mozilla/5.0 (compatible; ERW-research-reader/1.0; public regulatory documents)"

# Never requested (paused publishers, and hosts whose terms or answers bar this reader; see the method notes).
REFUSED = {
    "scc.virginia.gov": "paused: the Virginia SCC's robots file disallows every automated request (paused_sources.csv)",
    "misoenergy.org": "paused: MISO's terms forbid automated access (paused_sources.csv)",
    "coned.com": "barred: Con Edison's terms bar automated reading (session 2921)",
    "conedison.com": "barred: Con Edison's terms bar automated reading (session 2921)",
    "eversource.com": "barred: Eversource's terms bar automated reading (session 2921)",
    "duquesnelight.com": "barred: Duquesne Light answers with a bot challenge (session 2921)",
    # session 5300: hosts whose terms bar robots or automated access, read once by this pass's subagents
    "entergy.com": "barred: the Entergy Corporation Site Terms bar robots, spiders and scrapers (session 5300)",
    "entergylouisiana.com": "barred: Entergy's Site Terms (session 5300)",
    "entergyarkansas.com": "barred: Entergy's Site Terms (session 5300)",
    "entergymississippi.com": "barred: Entergy's Site Terms (session 5300)",
    "entergytexas.com": "barred: Entergy's Site Terms (session 5300)",
    "entergyneworleans.com": "barred: Entergy's Site Terms (session 5300)",
    "entergynewsroom.com": "barred: Entergy's Site Terms (session 5300)",
    "dominionenergy.com": "barred: Dominion Energy's terms bar spiders, robots and automated programs (session 5300)",
    "pplelectric.com": "barred: PPL's terms of use bar automated access (session 5300)",
    "exeloncorp.com": "barred: Exelon's terms bar automated access, for its utilities' sites too (session 5300)",
    "comed.com": "barred: Exelon's terms (session 5300)",
    "peco.com": "barred: Exelon's terms (session 5300)",
    "bge.com": "barred: Exelon's terms (session 5300)",
    "pepco.com": "barred: Exelon's terms (session 5300)",
    "delmarva.com": "barred: Exelon's terms (session 5300)",
    "atlanticcityelectric.com": "barred: Exelon's terms (session 5300)",
    "fpl.com": "barred: NextEra Energy's terms of use bar bots and spiders (session 5300)",
    "nexteraenergy.com": "barred: NextEra Energy's terms of use (session 5300)",
    "centerpointenergy.com": "barred: CenterPoint's terms bar scrapers, robots, bots and spiders (session 5300)",
    "ameren.com": "barred: Ameren's terms forbid bots (session 5300)",
}

CHALLENGE = re.compile(
    r"(g-recaptcha|hcaptcha|cf-chl|challenge-platform|Just a moment\.\.\.|Attention Required! \| Cloudflare|"
    r"Request unsuccessful\. Incapsula|_Incapsula_Resource|Access Denied</title>|captcha)",
    re.I,
)


def key(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def host_of(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def refused(host: str) -> str | None:
    for h, why in REFUSED.items():
        if host == h or host.endswith("." + h):
            return why
    return None


def wait_host(host: str) -> None:
    os.makedirs(HOSTLOG, exist_ok=True)
    stamp = os.path.join(HOSTLOG, re.sub(r"[^a-z0-9.]", "_", host))
    if os.path.exists(stamp):
        try:
            last = float(open(stamp, encoding="utf-8").read().strip() or 0)
        except ValueError:
            last = 0.0
        gap = time.time() - last
        if gap < 3:
            time.sleep(3 - gap)
    with open(stamp, "w", encoding="utf-8") as f:
        f.write(str(time.time()))


def _context():
    """Certificates are verified by Windows' own verifier where truststore is installed (session 5300: Python's bundled
    store lacked the issuers of the Texas, Florida and Nevada commissions' certificates, which Windows completes from
    the certificate's own issuer link). Verification is never turned off: a name mismatch still fails."""
    try:
        import ssl
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        return None


CTX = _context()


def get(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout, context=CTX)


def robots_verdict(url: str) -> tuple[bool, str]:
    parts = urllib.parse.urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    wait_host(host_of(url))
    try:
        with get(robots_url, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
        body = ""
    except Exception as e:  # network error: do not read the document
        return False, f"robots.txt not readable ({type(e).__name__}: {e}); not read"
    if code in (401, 403):
        return False, f"robots.txt answered {code}: treated as disallow all"
    if code >= 400:
        return True, f"robots.txt answered {code}: no robots file, allowed"
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(body.splitlines())
    # A server may treat paths without regard to case (session 5304: capitol.texas.gov disallows /TLODOCS/, and the
    # reader had fetched /tlodocs/). A path is refused when the rule bars it in its own case, upper case or lower case.
    # The rule paths and the address are compared once as written and once both lower-cased, so an Allow line keeps
    # its force (assets.centerpointenergy.com: Disallow: / with Allow: /api/public/) and a Disallow line written in
    # capitals still bars the same path in small letters.
    lowered = urllib.robotparser.RobotFileParser()
    lowered.parse([re.sub(r"(?i)^(\s*(?:dis)?allow\s*:\s*)(.*)$", lambda m: m.group(1) + m.group(2).lower(), ln)
                   for ln in body.splitlines()])
    parts = urllib.parse.urlsplit(url)
    low_url = urllib.parse.urlunsplit(parts._replace(path=parts.path.lower()))
    barred = [a for a in AGENTS if not (rp.can_fetch(a, url) and lowered.can_fetch(a, low_url))]
    ok = not barred
    named = [ln.strip() for ln in body.splitlines() if re.match(r"(?i)user-agent:\s*\S", ln.strip())]
    agents = ", ".join(n.split(":", 1)[1].strip() for n in named)[:300]
    if ok:
        return True, f"robots.txt {code}: allowed for {', '.join(AGENTS)}; agents named: {agents}"
    return False, f"robots.txt {code}: DISALLOWED for {', '.join(barred)}; agents named: {agents}"


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._atext: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in ("p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "td", "th"):
            self.out.append("\n")
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._atext = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._atext).split())))
            self._href = None

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)
            if self._href is not None:
                self._atext.append(data)


def html_text(raw: bytes, charset: str | None):
    s = raw.decode(charset or "utf-8", "replace")
    p = _Text()
    p.feed(s)
    text = "".join(p.out)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip() + "\n", p.links


def office_text(raw: bytes):
    """A .docx or .xlsx answer as text, read in memory from its XML (nothing is extracted to disk; a member over 50 MB
    uncompressed is refused). A .docx's pages are split at Word's own page marks (its last rendered page breaks and
    hard page breaks), so a page number is Word's last layout of the file. Each .xlsx sheet is one page, a row a line."""
    import io
    import re as _re
    import xml.etree.ElementTree as ET
    import zipfile
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()

    def member(name):
        info = z.getinfo(name)
        if info.file_size > 50_000_000:
            raise ValueError(f"{name} is {info.file_size} bytes uncompressed")
        return z.read(name)

    FF, NL, TAB = chr(12), chr(10), chr(9)
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    if "word/document.xml" in names:
        root = ET.fromstring(member("word/document.xml"))
        out = []
        for para in root.iter(W + "p"):
            line = []
            for el in para.iter():
                if el.tag == W + "lastRenderedPageBreak" or (el.tag == W + "br" and el.get(W + "type") == "page"):
                    line.append(FF)
                elif el.tag == W + "t" and el.text:
                    line.append(el.text)
                elif el.tag == W + "tab":
                    line.append(" ")
            out.append("".join(line))
        text = NL.join(out)
        while NL + FF in text or FF + NL in text:
            text = text.replace(NL + FF, FF).replace(FF + NL, FF)
        return "docx", text
    if "xl/workbook.xml" in names:
        S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        shared = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(member("xl/sharedStrings.xml")).iter(S + "si"):
                shared.append("".join(t.text or "" for t in si.iter(S + "t")))
        pages = []
        sheets = sorted(n for n in names if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"))
        for name in sheets:
            lines = []
            for row in ET.fromstring(member(name)).iter(S + "row"):
                cells = []
                for c in row.iter(S + "c"):
                    v = c.find(S + "v")
                    if v is None or v.text is None:
                        isv = c.find(S + "is")
                        cells.append("".join(t.text or "" for t in isv.iter(S + "t")) if isv is not None else "")
                    elif c.get("t") == "s":
                        cells.append(shared[int(v.text)] if v.text.isdigit() and int(v.text) < len(shared) else v.text)
                    else:
                        cells.append(v.text)
                lines.append(TAB.join(cells))
            pages.append("[" + name + "]" + NL + NL.join(lines))
        return "xlsx", FF.join(pages)
    raise ValueError("a zip file that is neither .docx nor .xlsx")


def fetch(url: str) -> dict:
    d = os.path.join(CACHE, key(url))
    meta_path = os.path.join(d, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8"))
        saved = os.path.join(d, "original.html")
        if meta.get("kind") == "html" and os.path.exists(saved):
            raw = open(saved, "rb").read()
            if raw[:2] == b"PK":
                # an office file the first reader kept as a page (before session 5300 read .docx): read again from the
                # saved bytes, with no new request
                os.replace(saved, os.path.join(d, "original.zip"))
                try:
                    kind, text = office_text(raw)
                    meta.update(kind=kind, pages=text.count(chr(12)) + 1, status="ok", reread_from_saved=True)
                    meta.pop("reason", None)
                    open(os.path.join(d, "text.txt"), "w", encoding="utf-8").write(text)
                except Exception as e:
                    meta.update(status="no_text", reason=f"office file not readable: {type(e).__name__}: {e}")
                json.dump(meta, open(meta_path, "w", encoding="utf-8"), indent=1)
        meta["cached"] = True
        return meta
    host = host_of(url)
    why = refused(host)
    if why:
        return {"url": url, "status": "refused", "reason": why}
    ok, verdict = robots_verdict(url)
    if not ok:
        return {"url": url, "status": "refused", "reason": verdict}
    wait_host(host)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    try:
        with get(url) as r:
            raw = r.read()
            final = r.geturl()
            code = r.status
            ctype = r.headers.get("Content-Type", "")
            charset = r.headers.get_content_charset()
    except urllib.error.HTTPError as e:
        return {"url": url, "status": "error", "reason": f"HTTP {e.code}", "robots": verdict}
    except Exception as e:
        return {"url": url, "status": "error", "reason": f"{type(e).__name__}: {e}", "robots": verdict}
    os.makedirs(d, exist_ok=True)
    is_pdf = raw[:5] == b"%PDF-" or ("pdf" in ctype.lower() and raw[:2] != b"PK")
    is_office = raw[:2] == b"PK" and not is_pdf
    meta = {
        "url": url,
        "final_url": final,
        "http": code,
        "content_type": ctype,
        "retrieved_at": now.isoformat().replace("+00:00", "Z"),
        "date_read": now.date().isoformat(),
        "robots": verdict,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "kind": "pdf" if is_pdf else "html",
        "status": "ok",
    }
    if is_pdf:
        rawp = os.path.join(d, "original.pdf")
        open(rawp, "wb").write(raw)
        for mode, name in ((None, "text.txt"), ("-layout", "layout.txt")):
            cmd = ["pdftotext", "-enc", "UTF-8"] + ([mode] if mode else []) + [rawp, os.path.join(d, name)]
            subprocess.run(cmd, check=False, capture_output=True)
        t = open(os.path.join(d, "text.txt"), encoding="utf-8", errors="replace").read() if os.path.exists(
            os.path.join(d, "text.txt")) else ""
        meta["pages"] = t.count("\f") + (0 if t.endswith("\f") else 1) if t else 0
        if len(t.strip()) < 200:
            meta["status"] = "no_text"
            meta["reason"] = "the PDF has no text layer pdftotext can read (a scan?)"
    elif is_office:
        open(os.path.join(d, "original.zip"), "wb").write(raw)
        try:
            kind, text = office_text(raw)
            meta["kind"] = kind
            open(os.path.join(d, "text.txt"), "w", encoding="utf-8").write(text)
            meta["pages"] = text.count(chr(12)) + 1
            if len(text.strip()) < 100:
                meta["status"] = "no_text"
                meta["reason"] = "the office file holds almost no text"
        except Exception as e:  # a file the reader cannot open is recorded, never guessed at
            meta["status"] = "no_text"
            meta["reason"] = f"office file not readable: {type(e).__name__}: {e}"
    else:
        open(os.path.join(d, "original.html"), "wb").write(raw)
        text, links = html_text(raw, charset)
        open(os.path.join(d, "text.txt"), "w", encoding="utf-8").write(text)
        absl = [(urllib.parse.urljoin(final, h), t) for h, t in links if h and not h.startswith(("javascript:", "mailto:", "#"))]
        json.dump(absl, open(os.path.join(d, "links.json"), "w", encoding="utf-8"), indent=0)
        meta["pages"] = 1
        if CHALLENGE.search(raw[:20000].decode("utf-8", "replace")) and len(text) < 3000:
            meta["status"] = "blocked"
            meta["reason"] = "the answer looks like a bot check; not retried with another agent"
    json.dump(meta, open(meta_path, "w", encoding="utf-8"), indent=1)
    meta["cached"] = False
    return meta


def pages_of(d: str) -> list[str]:
    t = open(os.path.join(d, "text.txt"), encoding="utf-8", errors="replace").read()
    return t.split("\f")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--grep")
    ap.add_argument("--links", nargs="?", const="")
    ap.add_argument("--page", type=int)
    ap.add_argument("--context", type=int, default=2)
    a = ap.parse_args()
    meta = fetch(a.url)
    d = os.path.join(CACHE, key(a.url))
    shown = {k: meta.get(k) for k in ("url", "final_url", "status", "reason", "http", "kind", "pages", "date_read",
                                      "retrieved_at", "robots", "cached") if meta.get(k) is not None}
    print(json.dumps(shown, indent=1))
    if meta.get("status") not in ("ok",):
        return 2
    print("text:", os.path.join(d, "text.txt"))
    if a.page:
        pg = pages_of(d)
        if 1 <= a.page <= len(pg):
            print(f"=== page {a.page} of {len(pg)} ===")
            print(pg[a.page - 1])
        else:
            print(f"no page {a.page}; the text has {len(pg)}")
    if a.grep:
        rx = re.compile(a.grep, re.I)
        for i, page in enumerate(pages_of(d), 1):
            lines = page.splitlines()
            for j, ln in enumerate(lines):
                if rx.search(ln):
                    lo, hi = max(0, j - a.context), min(len(lines), j + a.context + 1)
                    print(f"--- p.{i} line {j + 1}")
                    print("\n".join(lines[lo:hi]))
    if a.links is not None and meta.get("kind") == "html":
        links = json.load(open(os.path.join(d, "links.json"), encoding="utf-8"))
        rx = re.compile(a.links, re.I) if a.links else None
        for u, t in links:
            if rx is None or rx.search(u) or rx.search(t):
                print(f"{t[:90]} | {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
