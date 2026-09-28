#!/usr/bin/env python3
"""Energy Digest and the Energy Roundup by email: render, and send through Resend when configured.

Energy Research Warehouse (ERW), session 19 (platform tool 25). The session prompt named this file
warehouse/news/email.py; that name shadows Python's standard email package for every script in
warehouse/news (score.py and brief.py failed to start with it present), so it is email_digest.py. Reads the brief the daily run
already wrote (docs/digest/latest.md, from warehouse/news/brief.py) or, with --roundup, the Energy
Roundup (docs/roundup/latest.md, from warehouse/news/roundup.py; "Energy Week" until session 23) and
renders a short email as plain text and HTML: the title, the top 5 stories (headline, why, first
source), the brief's numbers section as written (every number names its table), the Fun fact (daily,
session 23) or the Weekend stories and the Chart of the week (Roundup, session 23), and a link to the site.

    python warehouse/news/email_digest.py              # the daily digest
    python warehouse/news/email_digest.py --roundup    # the Energy Roundup (--weekly is the old name)
    python warehouse/news/email_digest.py --auto       # the daily run: the digest, Monday to Friday only

Session 23: the digest is a weekday email (no weekend issue); the Roundup is written and sent on
Sundays at 23:00 UTC by .github/workflows/roundup.yml, so --auto no longer sends it.

Nothing is written by a model here: every line comes from the brief's markdown. The rendered
email is always saved as docs/digest/email/<date>-daily.txt and .html (or <week>-roundup).
Sending: only when both RESEND_API_KEY and DIGEST_RECIPIENTS (comma-separated addresses) are
set, in the environment or .env. Then each recipient gets their own message (no address sees
another), from DIGEST_FROM (default "ERW Energy Digest <onboarding@resend.dev>", Resend's test
sender; a verified domain is needed to send to others). With either unset, nothing is sent and
the log says so. The subscribers table in Supabase (the site's /subscribe) is read only with EMAIL_SUBSCRIBERS=1,
which is off: sending to the list waits for double opt-in and a tokened unsubscribe (human ruling, session 21).
When it is on, each kind goes only to the subscribers who chose it (the daily or weekly opt-in, migration 006). Links point to
SITE_URL (the deployed site) when set, else to the brief's markdown on GitHub.
"""

import argparse
import datetime as dt
import html
import os
import posixpath
import re
import sys
import traceback

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

DIGEST = os.path.join(ROOT, "docs", "digest", "latest.md")
ROUNDUP = os.path.join(ROOT, "docs", "roundup", "latest.md")
OUT = os.path.join(ROOT, "docs", "digest", "email")
REPO = "https://github.com/SamuelEnrique/erw/blob/main"
RAW = "https://raw.githubusercontent.com/SamuelEnrique/erw/main"  # images in the email (the repository is public)
RESEND = "https://api.resend.com/emails"
SITE_DEFAULT = "https://erw-flame.vercel.app"  # the deployed site README.md links; SITE_URL overrides it
TOP_HEADS = ("## Top of the industry", "## The five stories of the week")
NUM_HEADS = ("## Numbers today", "## Numbers of the week")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
KINDS = {"daily": ("Energy Digest", "digest", DIGEST), "roundup": ("Energy Roundup", "roundup", ROUNDUP)}
SUB_COLUMN = {"daily": "daily", "roundup": "weekly"}  # the subscribers column (migration 006 named the Roundup opt-in weekly)


def env(name):
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            v = dotenv_values(os.path.join(ROOT, ".env")).get(name)
        except ImportError:
            v = None
    return (v or "").strip()


def section(lines, heads):
    """The lines under the first heading in heads, up to the next '## ' heading or '---'."""
    out, on = [], False
    for ln in lines:
        if ln.strip() in heads:
            on = True
            continue
        if on and (ln.startswith("## ") or ln.strip() == "---"):
            break
        if on:
            out.append(ln)
    return out


def numbered(lines, heads, n=5):
    """[(headline, sector, why, (source, url))] from a numbered list under one of heads."""
    items, cur = [], None
    for ln in section(lines, heads):
        m = re.match(r"^\d+\. \*\*(.+?)\*\*(?: \(([a-z ]+)[,)])?", ln)
        if m:
            cur = {"head": m.group(1), "sector": (m.group(2) or "").strip(), "why": "", "src": None}
            items.append(cur)
        elif cur is not None and ln.startswith("   ") and ln.strip():
            text = ln.strip()
            src = LINK.search(text.split("Sources:", 1)[1]) if "Sources:" in text else None
            cur["why"] = text.split("Sources:", 1)[0].strip()
            cur["src"] = (src.group(1), src.group(2)) if src else None
    return items[:n]


def top_stories(lines, n=5):
    return numbered(lines, TOP_HEADS, n)


def md_inline_text(s):
    s = IMAGE.sub(lambda m: m.group(1), s)
    s = LINK.sub(lambda m: f"{m.group(1)} ({m.group(2)})", s)
    return s.replace("**", "").replace("`", "")


def md_inline_html(s):
    s = html.escape(s, quote=False)
    s = LINK.sub(lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def site_links(s, site):
    """Links written for the site (/about, /analysis) made absolute for an email."""
    return re.sub(r"\]\((/[^)]*)\)", lambda m: f"]({site}{m.group(1)})", s)


def block(body, img_base="docs"):
    """A markdown block as (plain text lines, HTML): tables become rows, bullets stay bullets, an image
    becomes an <img> at img_base (session 23, the chart of the week)."""
    text, parts, table = [], [], []

    def flush():
        if not table:
            return
        head = [c.strip() for c in table[0].strip("|").split("|")]
        rows = [[c.strip() for c in r.strip("|").split("|")] for r in table[2:]]
        for r in rows:
            text.append("  " + "; ".join(f"{h}: {md_inline_text(c)}" for h, c in zip(head, r) if c))
        cells = lambda r, tag: "".join(f"<{tag} style=\"text-align:left;padding:2px 8px;border-bottom:1px solid #D9D2C3\">{md_inline_html(c)}</{tag}>" for c in r)  # noqa: E731
        parts.append("<table style=\"border-collapse:collapse;font-size:13px\"><tr>" + cells(head, "th") + "</tr>"
                     + "".join(f"<tr>{cells(r, 'td')}</tr>" for r in rows) + "</table>")
        table.clear()

    for ln in body:
        if ln.startswith("|"):
            table.append(ln)
            continue
        flush()
        if not ln.strip():
            continue
        im = IMAGE.fullmatch(ln.strip())
        if im:
            src = im.group(2)
            url = src if re.match(r"https?://", src) else f"{RAW}/{posixpath.normpath(img_base + '/' + src)}"
            text.append(f"[chart: {im.group(1)}] {url}")
            parts.append(f"<p style=\"margin:8px 0\"><img src=\"{html.escape(url)}\" alt=\"{html.escape(im.group(1))}\" "
                         "width=\"600\" style=\"max-width:100%;height:auto;border:1px solid #D9D2C3\"></p>")
            continue
        text.append(md_inline_text(ln))
        parts.append(f"<p style=\"margin:6px 0\">{md_inline_html(ln.lstrip('- '))}</p>" if not ln.startswith("- ")
                     else f"<p style=\"margin:2px 0 2px 12px\">&bull; {md_inline_html(ln[2:])}</p>")
    flush()
    return text, "\n".join(parts)


def numbers(lines):
    """The numbers section as (plain text lines, HTML)."""
    return block(section(lines, NUM_HEADS))


def story_list(stories):
    t, li = [], []
    for i, s in enumerate(stories, 1):
        t.append(f"{i}. {s['head']}")
        if s["why"]:
            t.append(f"   {md_inline_text(s['why'])}")
        if s["src"]:
            t.append(f"   {s['src'][0]}: {s['src'][1]}")
        li.append(f"<li style=\"margin:0 0 8px\"><strong>{html.escape(s['head'])}</strong><br>"
                  + (f"<span style=\"color:#6B665E\">{md_inline_html(s['why'])}</span><br>" if s["why"] else "")
                  + (f"<a href=\"{html.escape(s['src'][1])}\">{html.escape(s['src'][0])}</a>" if s["src"] else "") + "</li>")
    return t, ("<ol style=\"padding-left:20px;font-size:14px;font-family:system-ui,sans-serif\">" + "".join(li) + "</ol>")


H2 = "<h2 style=\"font-size:16px;margin:16px 0 8px\">{}</h2>"
SMALL = "<div style=\"font-size:13px;font-family:system-ui,sans-serif\">{}</div>"


def render(path, kind, stories=None, note=None):
    """(title, label, text, html). stories: the top stories to show (default: the brief's first five);
    note: a line under the stories heading (session 23: the topic filter says what it kept)."""
    lines = open(path, encoding="utf-8").read().splitlines()
    title = lines[0].lstrip("# ").strip()
    label = title.split(", ")[-1]
    site = env("SITE_URL").rstrip("/")
    name, rel, _ = KINDS[kind]
    page = f"{site}/{rel}/{label}" if site else f"{REPO}/docs/{rel}/{label}.md"
    how = f"{site or SITE_DEFAULT}/about#digest"  # session 21: the method is on /about#digest
    if stories is None:
        stories = top_stories(lines)
        if len(stories) < 5:
            raise RuntimeError(f"{path}: {len(stories)} top stories found, 5 needed")
    num_text, num_html = numbers(lines)
    if not num_text:
        raise RuntimeError(f"{path}: no numbers section")
    head = "Top 5 of the day" if kind == "daily" else "The five stories of the week"
    t, h = [title, ""], [f"<h1 style=\"font-size:22px;margin:0 0 12px\">{html.escape(title)}</h1>"]
    if kind == "roundup":  # session 23: the weekend's stories open the Roundup
        wk = numbered(lines, ("## Weekend",), 5)
        wt, wh = story_list(wk)
        t += ["Weekend", ""] + (wt or ["No scored story was published on the weekend."]) + [""]
        h += [H2.format("Weekend"), wh if wk else SMALL.format("<p>No scored story was published on the weekend.</p>")]
    st, sh = story_list(stories)
    t += [head, ""] + ([note, ""] if note else []) + st
    h += [H2.format(head)] + ([SMALL.format(f"<p style=\"color:#6B665E\">{html.escape(note)}</p>")] if note else []) + [sh]
    t += ["", "Numbers" if kind == "daily" else "Numbers of the week", ""] + num_text
    h += [H2.format("Numbers" if kind == "daily" else "Numbers of the week"), SMALL.format(num_html)]
    # session 23: the Fun fact (daily) and the Chart of the week (Roundup), as the brief wrote them
    for heading in ("## Chart of the week", "## Fun fact"):
        body = [site_links(x, site or SITE_DEFAULT) for x in section(lines, (heading,))]
        if any(x.strip() for x in body):
            bt, bh = block(body, img_base=f"docs/{rel}")
            t += ["", heading[3:], ""] + bt
            h += [H2.format(heading[3:]), SMALL.format(bh)]
    t += ["", f"The whole {name}: {page}", f"How this is made: {how}",
          "ERW, the live, citable record of the US energy system. Every number names the table it came from."]
    h.append(f"<p style=\"font-size:13px;font-family:system-ui,sans-serif;margin-top:16px\"><a href=\"{html.escape(page)}\">"
             f"The whole {name}</a>. <a href=\"{html.escape(how)}\">How this is made</a>. "
             "ERW, the live, citable record of the US energy system. Every number names the table it came from.</p>")
    body_html = ("<!doctype html><html><body style=\"margin:0;padding:16px;background:#F7F3EA;color:#2E2D29;"
                 "font-family:Georgia,serif\"><div style=\"max-width:640px;margin:0 auto\">" + "".join(h)
                 + "</div></body></html>")
    return title, label, "\n".join(t) + "\n", body_html


def subscribers(kind, log):
    """Session 21, ruling 7: the subscribers who chose this kind (daily, or weekly for the Roundup) on
    /subscribe, read with the service key (the anon key cannot read the table). Only when EMAIL_SUBSCRIBERS=1:
    sending to the list waits for double opt-in and a tokened unsubscribe (human ruling, session 21)."""
    if env("EMAIL_SUBSCRIBERS") != "1":
        return []
    import urllib.parse
    base = urllib.parse.urlparse(env("SUPABASE_URL"))
    key = env("SUPABASE_SERVICE_KEY")
    r = requests.get(f"{base.scheme}://{base.netloc}/rest/v1/subscribers", timeout=60,
                     params={"select": "email", SUB_COLUMN[kind]: "eq.true"},
                     headers={"apikey": key, "Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"subscribers: HTTP {r.status_code}: {ip.redact(r.text[:200])}")
    out = sorted({x["email"].strip().lower() for x in r.json()})
    log(f"  {kind}: {len(out)} subscribers chose it")
    return out


def send(subject, text, body_html, log, kind="daily"):
    key = env("RESEND_API_KEY")
    to = [a.strip() for a in env("DIGEST_RECIPIENTS").split(",") if a.strip()] + subscribers(kind, log)
    if not key or not to:
        missing = [n for n, v in (("RESEND_API_KEY", key), ("DIGEST_RECIPIENTS", to)) if not v]
        log(f"  not sent: {', '.join(missing)} not set; the rendered email is in docs/digest/email/")
        print(f"email: not sent ({', '.join(missing)} not set)")
        return 0, "not sent: " + ", ".join(missing) + " not set"
    sender = env("DIGEST_FROM") or "ERW Energy Digest <onboarding@resend.dev>"
    sent = 0
    for addr in dict.fromkeys(to):  # each recipient alone; duplicates once
        r = requests.post(RESEND, headers={"Authorization": f"Bearer {key}"}, timeout=60,
                          json={"from": sender, "to": [addr], "subject": subject, "text": text, "html": body_html})
        if r.status_code >= 300:
            raise RuntimeError(f"Resend HTTP {r.status_code}: {ip.redact(r.text[:200])}")
        sent += 1
        log(f"  sent to recipient {sent} of {len(to)} (Resend id {r.json().get('id', '?')})")
    return sent, f"sent to {sent} recipients"


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW email digest")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--roundup", "--weekly", dest="roundup", action="store_true",
                   help="the Energy Roundup instead of the daily digest (--weekly: its session 19 name)")
    g.add_argument("--auto", action="store_true", help="the daily digest, Monday to Friday (UTC) only")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_email_{run_id}.log"))
    kinds = ["roundup"] if args.roundup else ["daily"]
    if args.auto and dt.datetime.now(dt.timezone.utc).weekday() >= 5:
        msg = "no weekend issue: the daily digest is a Monday to Friday email; the Roundup is sent on Sundays"
        log(msg)
        print(f"news_email SKIPPED: {msg}")
        ip.write_status("news_email", run_id, [dict(table="email", market="daily", status="skipped", detail=msg)])
        log.close()
        return 0
    results = []
    for kind in kinds:
        try:
            title, label, text, body_html = render(KINDS[kind][2], kind)
            os.makedirs(OUT, exist_ok=True)
            for ext, content in (("txt", text), ("html", body_html)):
                with open(os.path.join(OUT, f"{label}-{kind}.{ext}"), "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)
            log(f"{kind}: rendered '{title}' to docs/digest/email/{label}-{kind}.txt and .html")
            n, detail = send(title, text, body_html, log, kind)
            results.append(dict(table="email", market=kind, status="ok", detail=f"{label}: {detail}"))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{kind} FAILED:\n{tb}")
            print(f"news_email {kind} FAILED: {last}", file=sys.stderr)
            results.append(dict(table="email", market=kind, status="failed", detail=last[:300]))
    ip.write_status("news_email" if kinds == ["daily"] else "news_email_roundup", run_id, results)
    log.close()
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
