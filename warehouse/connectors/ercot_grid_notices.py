#!/usr/bin/env python3
"""ERCOT's grid notices: Energy Emergency Alerts, rotating outages, conservation appeals, watches and the control room's
operating notices (session 322, the owner's default of 19 October 2026 for the morning note's item 9).

Energy Research Warehouse (ERW) connector. ERCOT keeps no single public history of its notices, so two of its pages are
read, and each row names the one it came from:

    ercot:news_releases          https://www.ercot.com/news/releases?year=YYYY (2010 to the present) and each release
                                 whose title announces a grid condition: an EEA or emergency level, rotating outages, a
                                 conservation appeal (and its earlier names, Power Watch and Power Warning), a Voluntary
                                 Conservation Notice, a Weather Watch, or the update that ends one
    ercot:operations_messages    https://www.ercot.com/services/comm/mkt_notices/opsmessages?m=MM&y=YYYY, the control
                                 room's messages; ERCOT serves the last six months only (May 2026 on, read on 19 October
                                 2026; December 2022 answered with an empty list). The routine "Operational Information"
                                 and DC tie lines are left out; every Advisory, Watch, OCN, Emergency Notice and EEA is kept

ERCOT's market notice archive (/services/comm/mkt_notices/archives) reaches back three years only and carries market and
settlement notices, not operating conditions, so it is not read.

One row per notice and Central day it covers (as caiso_grid_emergencies: one row per notice and day). event_date: the
day covered; a release that names its days ("Monday, January 15", "through Sun., Feb. 6", "Thursday, August 20th through
Tuesday, August 25th, 2026") covers those, else the day it was issued. event_type: eea1, eea2, eea3, rotating_outages,
conservation_appeal, voluntary_conservation, weather_watch, power_watch, ocn_weather, ocn, advisory, watch,
emergency_notice, emergency_test, update (a release or message that ends or cancels a notice), statement (a release on the
grid's conditions that announces no notice). x_counts: yes when the notice is a
system-wide call on supply or demand, the kinds grid_stress_days counts as it counts CAISO's (EEA levels, rotating outages,
conservation appeals and notices, Power and Weather Watches, an OCN for extreme weather, and a release's update ending an
emergency, which says the emergency was in effect that day); no for a regional notice (the
Rio Grande Valley), an Advisory or Watch on the control room's own tools, a test, and an update. x_text: the notice's own
words (the release's title and first paragraph, or the message), not modified.

License: public. ERCOT's terms (https://www.ercot.com/help/terms, read 2 of warehouse/metadata/license_reads.csv, 12
October 2026): "The publicly available contents of this website may be used, reproduced, and redistributed, provided
that the contents are not modified and that you maintain all copyright and other notices contained in the contents". The
robots file (read 19 October 2026) disallows neither page.

    python warehouse/connectors/ercot_grid_notices.py --pull                 # the listings, new releases, six months
    python warehouse/connectors/ercot_grid_notices.py --from-raw DIR         # the pages saved in DIR, no request
"""

import argparse
import datetime as dt
import glob
import hashlib
import html
import os
import re
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "ercot_grid_notices"
BASE = "https://www.ercot.com"
RELEASES = BASE + "/news/releases"
OPS = BASE + "/services/comm/mkt_notices/opsmessages"
TERMS = BASE + "/help/terms"
TZ = "America/Chicago"
FIRST_YEAR = 2010
CEILING = 200  # requests a run
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}
# a release whose title says one of these is read; a forecast of the season, an app or a test of the system is not
TITLE = re.compile(r"conserv|emergency|weather|cold|heat|storm|hurricane|demand record|peak demand|grid conditions|\beea\b|power watch|power warning|weather watch|rotating outages|level [123]|"
                   r"tight grid conditions", re.I)
NOT_A_NOTICE = re.compile(r"emite|summer|energy saver|fanfare|to test emergency|minimum operating reserves|winter preparedness|"
                          r"expects tight reserves|expects another tight|reserve margin|prepares for potential|studies range|"
                          r"announces temporary", re.I)
COUNTS = {"eea1", "eea2", "eea3", "rotating_outages", "conservation_appeal", "voluntary_conservation", "weather_watch",
          "power_watch", "ocn_weather"}
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                       "september", "october", "november", "december"], 1)}
MON = {m[:3]: i for m, i in MONTHS.items()} | {"sept": 9}
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def read_page(path):
    """A saved page's text: UTF-8, or Windows-1252 where ERCOT's page holds its bytes (an apostrophe as 0x92)."""
    b = open(path, "rb").read()
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def text_of(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def release_links(page):
    """[(address, title)] of a year's listing."""
    out = []
    for href, body in re.findall(r'<a[^>]+href="(/news/release/[^"]+)"[^>]*>(.*?)</a>', page, flags=re.S):
        t = text_of(body)
        if t and (href, t) not in out:
            out.append((href, t))
    return out


def wanted(title):
    return bool(TITLE.search(title)) and not NOT_A_NOTICE.search(title)


def release_day(href):
    """The day in a release's address: /news/release/2023-09-06-... or /news/release/01212026-..."""
    slug = href.rsplit("/", 1)[-1]
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", slug)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.match(r"(\d{2})(\d{2})(\d{4})", slug)
    if m:
        return dt.date(int(m[3]), int(m[1]), int(m[2]))
    raise ValueError(f"no day in {href}")


def release_body(page):
    """(title, its first two paragraphs) of a saved release page."""
    h = re.search(r"<h1[^>]*>(.*?)</h1>", page, flags=re.S)
    title = text_of(h.group(1)) if h else ""
    rest = page[h.end():] if h else page
    paras = [text_of(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", rest, flags=re.S)]
    paras = [p for p in paras if len(p) > 40]
    return title, " ".join(paras[:2])  # the first two paragraphs: the notice and what it covers


def named_days(text, issued):
    """The days a notice names, in the order written ([] when it names none). A "through" between two days covers each
    day between. A month and day without a year takes the year of issue (the next year when that would fall more than
    two months before the issue)."""
    found = []
    text = re.sub(r"^\(Austin, TX[^)]*\)\s*", "", text)  # the dateline is the day of issue, not a day covered
    text = re.sub(r"(?<=\. )\(Austin, TX[^)]*\)\s*", "", text)
    text = re.sub(r"\bAustin,\s*(TX,?\s*)?[A-Za-z]+\.?\s*\d{1,2},\s*\d{4}", "", text, flags=re.I)  # "AUSTIN, TX, Sept. 4, 2019"
    # "June 25 - 30", "January 20-23": a month's range of days, each day written out
    month = "|".join(sorted(list(MONTHS) + list(MON), key=len, reverse=True))
    text = re.sub(r"\b(" + month + r")\.?\s+(\d{1,2})\s*[-–—�]\s*(\d{1,2})\b",
                  lambda m: f"{m[1]} {m[2]} through {m[1]} {m[3]}", text, flags=re.I)
    pat = (r"(?:(" + "|".join(WEEKDAYS) + r")\.?,?\s+)?(" + "|".join(sorted(list(MONTHS) + list(MON), key=len, reverse=True))
           + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?")
    for m in re.finditer(pat, text, flags=re.I):
        mon = MONTHS.get(m[2].lower()) or MON.get(m[2].lower()[:4]) or MON.get(m[2].lower()[:3])
        year = int(m[4]) if m[4] else issued.year
        try:
            d = dt.date(year, mon, int(m[3]))
        except ValueError:
            continue
        if not m[4] and (issued - d).days > 60:
            d = d.replace(year=year + 1)
        found.append((m.start(), m.end(), d))
    if not found:
        return []
    days = [found[0][2]]
    if len(found) == 1 and re.search(r"\bthrough\b", text[:found[0][0]], flags=re.I) and 0 < (found[0][2] - issued).days <= 14:
        days = [issued + dt.timedelta(days=i) for i in range((found[0][2] - issued).days + 1)]  # "through Sun., Feb. 6"
    for (s0, e0, d0), (s1, e1, d1) in zip(found, found[1:]):
        if re.search(r"\bthrough\b|\bto\b|-", text[e0:s1], flags=re.I) and 0 < (d1 - d0).days <= 14:
            days += [d0 + dt.timedelta(days=i) for i in range(1, (d1 - d0).days + 1)]
        else:
            days.append(d1)
    return sorted(set(days))


def through_weekday(text, issued):
    """'through Tuesday' or 'through Sun.': the days from issue to that weekday (at most a week), or []."""
    m = re.search(r"through\s+(?:the\s+)?(" + "|".join(w[:3] for w in WEEKDAYS) + r")[a-z]*\.?", text, flags=re.I)
    if not m:
        return []
    want = [w[:3] for w in WEEKDAYS].index(m[1].lower()[:3])
    n = (want - issued.weekday()) % 7
    return [issued + dt.timedelta(days=i) for i in range(n + 1)]


def release_kind(title, para):
    """(event_type, region) from a release's own words."""
    t, both = title.lower(), f"{title} {para}".lower()
    region = "Rio Grande Valley" if re.search(r"rio grande valley|\bthe valley\b|valley area|in valley", t) else "ERCOT"
    if re.search(r"cancel|no longer in emergency|will end emergency|has exited|discontinues|thank|restored|ended|update: emergency", t):
        return "update", region
    if re.search(r"rotating outages", t) or re.search(r"\beea 3\b|eea3|level 3", t):
        return ("rotating_outages" if "rotating outages" in t else "eea3"), region
    if re.search(r"power watch|power warning", t):  # 2011's names; the body's mention of EEAs is a warning, not an alert
        return "power_watch", region
    if re.search(r"\beea ?2\b|level 2 emergency|energy emergency alert level 2", t):
        return "eea2", region
    # an EEA declared: in the title, or the first paragraph saying ERCOT issued, declared, entered or is in one
    if re.search(r"\beea ?1\b|level 1 emergency|energy emergency alert", t) or re.search(
            r"(issued|declared|entered|initiated|is in|moved into)[^.]{0,40}(energy emergency alert|\beea\b)", both):
        lvl = re.search(r"(?:eea|level)\s?([123])", both)
        return f"eea{lvl[1] if lvl else '1'}", region
    if "voluntary conservation" in t:
        return "voluntary_conservation", region
    if "weather watch" in t:
        return "weather_watch", region
    if re.search(r"no conservation appeal", t):
        return "statement", region
    if re.search(r"conserv", t):
        return "conservation_appeal", region
    asks = re.search(r"(ask|request|urg|appeal|call)\w*[^.]{0,60}conserv", both)
    declines = re.search(r"\b(not|no)\b[^.]{0,30}(ask|request|appeal|call)\w*[^.]{0,40}conserv", both)
    if asks and not declines:
        return "conservation_appeal", region
    # an Operating Condition Notice the release announces (16 December 2022: cold weather, 22 to 26 December)
    if re.search(r"operating condition notice|\bocn\b", both):
        weather = re.search(r"cold|freez|winter|heat|hot|temperature|hurricane|storm", both)
        return ("ocn_weather" if weather else "ocn"), region
    return "statement", region  # a release on the grid that announces no notice


def ops_rows(page):
    """[(when, message, notice type, status)] of a saved operations messages page."""
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, flags=re.S):
        tds = [text_of(td) for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
        if len(tds) >= 3 and re.match(r"[A-Z][a-z]{2} \d{1,2}, \d{4}", tds[0]):
            out.append((tds[0], tds[1], tds[2], tds[3] if len(tds) > 3 else ""))
    return out


def ops_kind(message, ntype):
    """event_type of a control-room message, or None for the routine lines left out."""
    t, m = ntype.lower(), message.lower()
    if t in ("operational information", "dc tie curtailment notice"):
        return None
    if m.startswith("ercot has cancelled the following notice"):
        return "update"
    if "test" in m and t == "emergency notice":
        return "emergency_test"
    if re.search(r"\beea ?([123])\b|energy emergency alert", m):
        lvl = re.search(r"\beea ?([123])\b|level ([123])", m)
        return f"eea{(lvl[1] or lvl[2]) if lvl else '1'}"
    if t == "ocn":
        return "ocn_weather" if re.search(r"extreme (hot|cold) weather|extreme (heat|cold)|winter storm|hot weather|cold weather", m) else "ocn"
    if t == "watch":
        return "watch"
    if t == "advisory":
        return "advisory"
    if t == "emergency notice":
        return "emergency_notice"
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_") or "notice"


def build(raw_dir, retrieved):
    """The table's rows from the pages saved in raw_dir (release listings releases_*.html, releases rel_<slug>.html,
    operations months ops_YYYY_MM.html; their addresses from manifest.csv)."""
    addr = {}
    man = os.path.join(raw_dir, "manifest.csv")
    if os.path.exists(man):
        for line in open(man, encoding="utf-8"):
            p = line.rstrip("\n").split(",", 5)
            if len(p) == 6:
                addr[p[4]] = p[5]
    rows = []
    for path in sorted(glob.glob(os.path.join(raw_dir, "rel_*.html"))):
        name = os.path.basename(path)
        href = "/news/release/" + name[4:-5]
        url = addr.get(name, BASE + href)
        issued = release_day(href)
        title, para = release_body(read_page(path))
        kind, region = release_kind(title, para)
        days = named_days(title, issued) or through_weekday(title, issued)
        if not days and kind in ("weather_watch", "voluntary_conservation", "conservation_appeal", "power_watch", "ocn_weather", "ocn"):
            days = [d for d in named_days(para, issued) if 0 <= (d - issued).days <= 14]  # the days the first paragraph names
        days = days or [issued]
        if kind in ("update", "statement"):
            days = [issued]
        for d in days:
            rows.append(dict(day=d, kind=kind, region=region, label=title, text=f"{title}. {para}"[:1000], issued=issued.isoformat(),
                             status="ended" if kind == "update" else "issued", source="ercot:news_releases", url=url))
    for path in sorted(glob.glob(os.path.join(raw_dir, "ops_*.html"))):
        name = os.path.basename(path)
        url = addr.get(name, OPS)
        for when, msg, ntype, status in ops_rows(read_page(path)):
            kind = ops_kind(msg, ntype)
            if kind is None:
                continue
            at = pd.Timestamp(dt.datetime.strptime(when, "%b %d, %Y %I:%M:%S %p")).tz_localize(TZ)
            issued = at.date()
            days = named_days(msg, issued) if kind in ("ocn_weather", "ocn", "watch") else []
            days = [d for d in days if 0 <= (d - issued).days <= 14] or [issued]
            if kind in ("update", "emergency_test"):
                days = [issued]
            for d in days:
                rows.append(dict(day=d, kind=kind, region="ERCOT", label=ntype, text=msg[:1000],
                                 issued=at.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ"), status=(status or "").lower() or "issued",
                                 source="ercot:operations_messages", url=url))
    df = pd.DataFrame(rows).drop_duplicates(["day", "kind", "text", "source"])
    key = lambda r: hashlib.sha1(f"{r['source']}|{r['url']}|{r['issued']}|{r['text']}".encode()).hexdigest()[:10]  # noqa: E731
    # an update that ends an emergency ("Level 1 emergency cancelled", "Energy Emergency Alert canceled") says the
    # emergency was in effect that day, so its day counts as the alert's own does
    ended = df["kind"].eq("update") & df["source"].eq("ercot:news_releases") & df["label"].str.contains(
        r"emergency|\bEEA\b", case=False, regex=True)
    counts = [("yes" if (r["kind"] in COUNTS or e) and r["region"] == "ERCOT" else "no") for (_, r), e in zip(df.iterrows(), ended)]
    out = pd.DataFrame({
        "event_id": [f"ercot_notice:{r['day']}:{r['kind']}:{key(r)}" for _, r in df.iterrows()],
        "event_date": df["day"].astype(str), "event_type": df["kind"], "parties": "ERCOT", "entity_ids": "", "mw": "", "price": "",
        "currency": "", "status": df["status"], "source": df["source"], "source_url": df["url"], "retrieved_at": retrieved,
        "x_label": df["label"], "x_region": df["region"], "x_issued_at": df["issued"], "x_counts": counts, "x_text": df["text"]})
    return out.sort_values(["event_date", "event_type", "event_id"]).reset_index(drop=True)


def pull(raw_dir, log, months=6):
    """The listings of every year, each wanted release not saved yet, and the last `months` months of operations
    messages, into raw_dir. Returns the number of requests."""
    os.makedirs(raw_dir, exist_ok=True)
    n = 0
    s = requests.Session()
    s.headers.update(UA)

    def get(url, name):
        nonlocal n
        if n >= CEILING:
            raise RuntimeError(f"the ceiling of {CEILING} requests a run is reached")
        r = s.get(url, timeout=60)
        n += 1
        if r.status_code != 200:
            raise RuntimeError(f"{url}: HTTP {r.status_code}")
        with open(os.path.join(raw_dir, name), "wb") as f:
            f.write(r.content)
        with open(os.path.join(raw_dir, "manifest.csv"), "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ},{r.status_code},{len(r.content)},"
                    f"{hashlib.sha256(r.content).hexdigest()},{name},{url}\n")
        return r.text

    today = dt.date.today()
    for y in range(today.year, FIRST_YEAR - 1, -1):
        page = get(f"{RELEASES}?year={y}", f"releases_{y}.html")
        for href, title in release_links(page):
            name = f"rel_{href.rsplit('/', 1)[-1]}.html"
            if wanted(title) and not os.path.exists(os.path.join(raw_dir, name)):
                get(BASE + href, name)
    first = (pd.Timestamp(today) - pd.DateOffset(months=months - 1)).replace(day=1)
    for m in pd.date_range(first, pd.Timestamp(today), freq="MS"):
        get(f"{OPS}?m={m.month:02d}&y={m.year}", f"ops_{m.year}_{m.month:02d}.html")
    log(f"  {n} requests to ERCOT")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's grid notices (session 322)")
    ap.add_argument("--pull", action="store_true", help="read ERCOT's pages into a new raw folder, then build")
    ap.add_argument("--from-raw", help="build from the pages saved in this folder; no request")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"ercot_grid_notices_{run_id}.log"))
    results = []
    try:
        if not (args.pull or args.from_raw):
            ap.error("--pull or --from-raw")
        if ip.paused("ercot"):
            raise RuntimeError(ip.pause_line("ercot"))
        raw = args.from_raw or os.path.join(ip.RAW_DIR, NAME, run_id)
        if args.pull:
            prev = sorted(glob.glob(os.path.join(ip.RAW_DIR, NAME, "*", "rel_*.html")))
            os.makedirs(raw, exist_ok=True)
            for p in prev:  # a release once read is not asked again
                dst = os.path.join(raw, os.path.basename(p))
                if not os.path.exists(dst):
                    with open(p, "rb") as f, open(dst, "wb") as g:
                        g.write(f.read())
            pull(raw, log)
        man = os.path.join(raw, "manifest.csv")
        retrieved = max((ln.split(",", 1)[0] for ln in open(man, encoding="utf-8")), default="") if os.path.exists(man) else ""
        out = build(raw, retrieved)
        if out.empty:
            raise RuntimeError(f"no notice read from {raw}")
        by = out.groupby(["source", "event_type"]).size()
        log("rows by source and type: " + "; ".join(f"{s} {t} {n}" for (s, t), n in by.items()))
        header = [
            "Energy Research Warehouse (ERW): ERCOT's grid notices, Energy Emergency Alerts, rotating outages, conservation appeals, "
            "watches and the control room's operating notices (session 322)",
            "Shape: events (docs/datastandard.md v0, decision 35). One row per notice and Central day it covers; event_type eea1 to "
            "eea3, rotating_outages, conservation_appeal, voluntary_conservation, weather_watch, power_watch, ocn_weather, ocn, "
            "advisory, watch, emergency_notice, emergency_test, update, statement. x_counts yes: a system-wide call on supply or demand, "
            "the kinds grid_stress_days counts. x_text: the notice's own words. x_issued_at: the day of a release, the UTC time "
            "of a control-room message. docs/methods/ercot_grid_notices.md",
            "Coverage: ERCOT's news releases from 2010 (each year's listing, and the releases whose title announces a grid "
            "condition); the control room's operations messages for the six months ERCOT serves (May 2026 on). No public "
            "history of the control room's messages before May 2026 is served, so an Advisory, Watch or OCN of an earlier "
            "day appears only where a news release announced it",
            f"Retrieved: {retrieved or run_id} (UTC) by warehouse/connectors/ercot_grid_notices.py",
            f"Run log: warehouse/output/logs/ercot_grid_notices_{run_id}.log",
            f"Raw files: {os.path.relpath(raw, ip.ROOT).replace(os.sep, '/')}/ (not in git; manifest.csv lists each page, "
            "its address, time and sha256)",
            f"Source: ercot:news_releases ERCOT, News Releases, {RELEASES}; ercot:operations_messages ERCOT, Operations "
            f"Messages, {OPS}",
            f"License: public. ERCOT's terms ({TERMS}): its public contents may be used, reproduced and redistributed, not "
            "modified, with its notices kept. Credit: Electric Reliability Council of Texas (ERCOT).",
        ]
        cols = list(out.columns)
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        old = None
        if os.path.exists(path):
            old = ip.read_series(path, cols)
            os.remove(path)
        if old is not None and not old.empty:  # the control room's months roll off ERCOT's page: rows once read are kept
            out = pd.concat([old[~old["event_id"].isin(out["event_id"])], out], ignore_index=True)
        ip.write_csv(out, NAME, header, log, cols=cols, key=["event_id"], time_col="event_date")
        ip.update_sources([dict(source="ercot:news_releases", publisher="Electric Reliability Council of Texas (ERCOT)",
                                report="News Releases (grid conditions: EEAs, conservation appeals, watches)", report_url=RELEASES,
                                document_list=RELEASES, license="public", tables=[NAME]),
                           dict(source="ercot:operations_messages", publisher="Electric Reliability Council of Texas (ERCOT)",
                                report="Operations Messages (the control room's notices)", report_url=OPS, document_list=OPS,
                                license="public", tables=[NAME])])
        msg = (f"{len(out)} rows, {out['event_date'].min()} to {out['event_date'].max()}; "
               f"{(out['x_counts'] == 'yes').sum()} count toward stress days on {out.loc[out['x_counts'] == 'yes', 'event_date'].nunique()} days")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
        print(f"ercot_grid_notices: {msg}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"ercot_grid_notices {NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("ercot_grid_notices", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
