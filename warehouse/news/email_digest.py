#!/usr/bin/env python3
"""Energy Digest and Energy Week by email: render, and send through Resend when configured.

Energy Research Warehouse (ERW), session 19 (platform tool 25). The session prompt named this file
warehouse/news/email.py; that name shadows Python's standard email package for every script in
warehouse/news (score.py and brief.py failed to start with it present), so it is email_digest.py. Reads the brief the daily run
already wrote (docs/digest/latest.md, from warehouse/news/brief.py) or, with --weekly, Energy
Week (docs/weekly/latest.md, from warehouse/news/weekly.py) and renders a short email as plain
text and HTML: the title, the top 5 stories (headline, why, first source), the brief's numbers
section as written (every number names its table), and a link to the site.

    python warehouse/news/email_digest.py              # the daily digest
    python warehouse/news/email_digest.py --weekly     # Energy Week
    python warehouse/news/email_digest.py --auto       # the daily run: the digest, and on Mondays (UTC)
                                                # Energy Week too if it was written in the last 24 hours

Nothing is written by a model here: every line comes from the brief's markdown. The rendered
email is always saved as docs/digest/email/<date>-daily.txt and .html (or <week>-weekly).
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
import re
import sys
import traceback

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

DIGEST = os.path.join(ROOT, "docs", "digest", "latest.md")
WEEKLY = os.path.join(ROOT, "docs", "weekly", "latest.md")
OUT = os.path.join(ROOT, "docs", "digest", "email")
REPO = "https://github.com/SamuelEnrique/erw/blob/main"
RESEND = "https://api.resend.com/emails"
SITE_DEFAULT = "https://erw-flame.vercel.app"  # the deployed site README.md links; SITE_URL overrides it
TOP_HEADS = ("## Top of the industry", "## The five stories of the week")
NUM_HEADS = ("## Numbers today", "## Numbers of the week")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


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


def top_stories(lines, n=5):
    """[(headline, why, (source, url))] from the brief's numbered list."""
    items, cur = [], None
    for ln in section(lines, TOP_HEADS):
        m = re.match(r"^\d+\. \*\*(.+?)\*\*", ln)
        if m:
            cur = {"head": m.group(1), "why": "", "src": None}
            items.append(cur)
        elif cur is not None and ln.startswith("   ") and ln.strip():
            text = ln.strip()
            src = LINK.search(text.split("Sources:", 1)[1]) if "Sources:" in text else None
            cur["why"] = text.split("Sources:", 1)[0].strip()
            cur["src"] = (src.group(1), src.group(2)) if src else None
    return items[:n]


def md_inline_text(s):
    s = LINK.sub(lambda m: f"{m.group(1)} ({m.group(2)})", s)
    return s.replace("**", "").replace("`", "")


def md_inline_html(s):
    s = html.escape(s, quote=False)
    s = LINK.sub(lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def numbers(lines):
    """The numbers section as (plain text lines, HTML): tables become rows, bullets stay bullets."""
    body = section(lines, NUM_HEADS)
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
        text.append(md_inline_text(ln))
        parts.append(f"<p style=\"margin:6px 0\">{md_inline_html(ln.lstrip('- '))}</p>" if not ln.startswith("- ")
                     else f"<p style=\"margin:2px 0 2px 12px\">&bull; {md_inline_html(ln[2:])}</p>")
    flush()
    return text, "\n".join(parts)


def render(path, kind):
    lines = open(path, encoding="utf-8").read().splitlines()
    title = lines[0].lstrip("# ").strip()
    label = title.split(", ")[-1]
    site = env("SITE_URL").rstrip("/")
    rel = "digest" if kind == "daily" else "weekly"
    page = f"{site}/{rel}/{label}" if site else f"{REPO}/docs/{rel}/{label}.md"
    how = f"{site or SITE_DEFAULT}/about#digest"  # session 21: the method is on /about#digest
    stories = top_stories(lines)
    if len(stories) < 5:
        raise RuntimeError(f"{path}: {len(stories)} top stories found, 5 needed")
    num_text, num_html = numbers(lines)
    if not num_text:
        raise RuntimeError(f"{path}: no numbers section")
    head = "Top 5 of the day" if kind == "daily" else "The five stories of the week"
    t = [title, "", head, ""]
    for i, s in enumerate(stories, 1):
        t.append(f"{i}. {s['head']}")
        if s["why"]:
            t.append(f"   {md_inline_text(s['why'])}")
        if s["src"]:
            t.append(f"   {s['src'][0]}: {s['src'][1]}")
    t += ["", "Numbers" if kind == "daily" else "Numbers of the week", ""] + num_text
    t += ["", f"The whole {'digest' if kind == 'daily' else 'brief'}: {page}",
          f"How this is made: {how}",
          "ERW, the live, citable record of the US energy system. Every number names the table it came from."]
    li = "".join(
        f"<li style=\"margin:0 0 8px\"><strong>{html.escape(s['head'])}</strong><br>"
        + (f"<span style=\"color:#6B665E\">{md_inline_html(s['why'])}</span><br>" if s["why"] else "")
        + (f"<a href=\"{html.escape(s['src'][1])}\">{html.escape(s['src'][0])}</a>" if s["src"] else "") + "</li>"
        for s in stories)
    h = (f"<!doctype html><html><body style=\"margin:0;padding:16px;background:#F7F3EA;color:#2E2D29;"
         f"font-family:Georgia,serif\"><div style=\"max-width:640px;margin:0 auto\">"
         f"<h1 style=\"font-size:22px;margin:0 0 12px\">{html.escape(title)}</h1>"
         f"<h2 style=\"font-size:16px;margin:16px 0 8px\">{head}</h2><ol style=\"padding-left:20px;font-size:14px;"
         f"font-family:system-ui,sans-serif\">{li}</ol>"
         f"<h2 style=\"font-size:16px;margin:16px 0 8px\">{'Numbers' if kind == 'daily' else 'Numbers of the week'}</h2>"
         f"<div style=\"font-size:13px;font-family:system-ui,sans-serif\">{num_html}</div>"
         f"<p style=\"font-size:13px;font-family:system-ui,sans-serif;margin-top:16px\"><a href=\"{html.escape(page)}\">"
         f"The whole {'digest' if kind == 'daily' else 'brief'}</a>. <a href=\"{html.escape(how)}\">How this is made</a>. "
         "ERW, the live, citable record of the US energy system. Every number names the table it came from.</p>"
         "</div></body></html>")
    return title, label, "\n".join(t) + "\n", h


def subscribers(kind, log):
    """Session 21, ruling 7: the subscribers who chose this kind (daily or weekly) on /subscribe, read with
    the service key (the anon key cannot read the table). Only when EMAIL_SUBSCRIBERS=1: sending to the list
    waits for double opt-in and a tokened unsubscribe (human ruling, session 21), so it is off by default."""
    if env("EMAIL_SUBSCRIBERS") != "1":
        return []
    import urllib.parse
    base = urllib.parse.urlparse(env("SUPABASE_URL"))
    key = env("SUPABASE_SERVICE_KEY")
    r = requests.get(f"{base.scheme}://{base.netloc}/rest/v1/subscribers", timeout=60,
                     params={"select": "email", kind: "eq.true"}, headers={"apikey": key, "Authorization": f"Bearer {key}"})
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
    g.add_argument("--weekly", action="store_true", help="Energy Week instead of the daily digest")
    g.add_argument("--auto", action="store_true", help="the daily digest, and Energy Week on Mondays if new")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"news_email_{run_id}.log"))
    kinds = ["weekly"] if args.weekly else ["daily"]
    if args.auto and dt.datetime.now(dt.timezone.utc).weekday() == 0 and os.path.exists(WEEKLY):
        age = dt.datetime.now().timestamp() - os.path.getmtime(WEEKLY)
        if age < 86400:
            kinds.append("weekly")
        else:
            log(f"Monday, but docs/weekly/latest.md is {age / 3600:.0f} hours old; Energy Week not sent again")
    results = []
    for kind in kinds:
        try:
            title, label, text, body_html = render(DIGEST if kind == "daily" else WEEKLY, kind)
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
    ip.write_status("news_email", run_id, results)
    log.close()
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
