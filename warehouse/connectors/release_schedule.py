#!/usr/bin/env python3
"""The release schedules of the weekly reports the Supply and trade page reads (session 134).

Energy Research Warehouse (ERW). Three weekly reports, each with a standing day and time and, for EIA's two, a
published list of the weeks a holiday moves:

    wpsr    EIA Weekly Petroleum Status Report        Wednesday 10:30 a.m. Eastern   https://www.eia.gov/petroleum/supply/weekly/schedule.php
    wngsr   EIA Weekly Natural Gas Storage Report     Thursday 10:30 a.m. Eastern    https://ir.eia.gov/ngs/schedule.html
    cot     CFTC Commitments of Traders               Friday 3:30 p.m. Eastern       https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm

    python warehouse/connectors/release_schedule.py          # reads EIA's two schedule pages; writes the file

It writes warehouse/metadata/release_schedule.json: for each report its standing rule, its page, and the exceptions
read from the page (the alternate release date, its day and time, and the holiday named). The CFTC's page is drawn by
a script and lists no dates in its text, so the CFTC's rule stands alone and the file says so. This is a schedule, not
a table of the warehouse: nothing here is a measurement. warehouse/derived/supply_page.py works out each report's next
date from it. Two requests a run; no row of any ceiling.
"""

import datetime as dt
import html
import json
import os
import re
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "metadata", "release_schedule.json")
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}
DATE = r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}"
DAY = r"(?:Monday|Tuesday|Wednesday|Thursday|Friday)"
TIME = r"\d{1,2}:\d{2} [ap]\.m\."
REPORTS = [
    dict(id="wpsr", name="Weekly Petroleum Status Report", publisher="EIA", weekday=2, time="10:30", page="https://www.eia.gov/petroleum/supply/weekly/schedule.php",
         covers="the week ending the Friday before"),
    dict(id="wngsr", name="Weekly Natural Gas Storage Report", publisher="EIA", weekday=3, time="10:30", page="https://ir.eia.gov/ngs/schedule.html", covers="the week ending the Friday before"),
    dict(id="cot", name="Commitments of Traders", publisher="CFTC", weekday=4, time="15:30", page="https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm",
         covers="positions as of the Tuesday before"),
]


def text_of(page):
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def iso(words):
    return dt.datetime.strptime(words, "%B %d, %Y").date().isoformat()


def clock(words):
    """ "12:00 p.m." as "12:00", "1:00 p.m." as "13:00"."""
    h, m = map(int, words.split(" ")[0].split(":"))
    if words.endswith("p.m.") and h != 12:
        h += 12
    return f"{h:02d}:{m:02d}"


def exceptions(report, text):
    """The alternate release dates a schedule page lists: [{date, day, time, holiday, week_ending?}]."""
    out = []
    if report == "wpsr":       # data for week ending | alternate release date | day | time | holiday
        for a, b, day, time, holiday in re.findall(rf"({DATE}) ({DATE}) ({DAY}) ({TIME}) ([A-Za-z'’. ]+? Day|[A-Za-z'’.]+)(?= |$)", text):
            out.append(dict(week_ending=iso(a), date=iso(b), day=day, time=clock(time), holiday=holiday.strip()))
    else:                      # alternate release date | day | time | holiday
        for b, day, time, holiday in re.findall(rf"({DATE})(?: - \(Updated\))? ({DAY}) ({TIME}) ([A-Za-z'’. ]+?)(?= {DATE}| EIA -|$)", text):
            out.append(dict(date=iso(b), day=day, time=clock(time), holiday=holiday.strip()))
    return out


def main():
    got = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    reports = []
    for r in REPORTS:
        item = dict(r, exceptions=[], read="the standing rule alone")
        if r["publisher"] == "EIA":
            try:
                page = requests.get(r["page"], headers=UA, timeout=60)
                page.raise_for_status()
                item["exceptions"] = exceptions(r["id"], text_of(page.content.decode("utf-8", errors="replace")))
                item["read"] = f"the page's holiday table, {len(item['exceptions'])} alternate dates"
            except Exception as exc:       # the schedule is a convenience: the rule stands when the page cannot be read, and the file says so
                item["read"] = f"the standing rule alone: the page could not be read ({str(exc)[:80]})"
        else:
            item["read"] = "the standing rule alone: the CFTC's page lists no dates in its text. A federal holiday in the week can move the release"
        reports.append(item)
        print(f"{r['id']}: {item['read']}")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(retrieved_at=got, timezone="America/New_York", reports=reports), f, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
