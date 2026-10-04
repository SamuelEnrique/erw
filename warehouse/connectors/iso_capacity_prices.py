#!/usr/bin/env python3
"""Capacity prices across the markets that pay capacity apart from energy: PJM, NYISO, ISO-NE, MISO.

Energy Research Warehouse (ERW) connector, session 65 (docs/methods/capacity_and_ancillary.md). Writes one series
table, warehouse/output/iso_all_capacity_prices.csv, one row per market, zone, delivery period and auction, the
clearing price as published in its published unit. Nothing is converted in the table; the conversions to
USD/kW-month are in the methods doc.

    market           entity                     ts_utc (start of the delivery period)    freq  unit
    pjm_bra          pjm:<LDA>                  the delivery year's June 1               P1Y   USD/MW-day
    nyiso_icap_spot  nyiso:<locality>           the month's first day                    P1M   USD/kW-month
    isone_fca        isone:<zone as printed>    the commitment period's June 1           P1Y   USD/kW-month
    miso_pra         miso:Z1 ... Z10, miso:ERZ  the season's first day                   P3M   USD/MW-day

    variable   capacity_price; ISO-NE's auctions 8 and 9 paid new and existing resources apart and are
               capacity_price_new and capacity_price_existing
    x_auction     the auction as the publisher names it ("BRA 2026/2027", "Spot 05/2025", "FCA 16", "PRA 2025/26
                  Summer 2025")
    x_period_end  the delivery period's last day
    x_note        what the publisher says about the price ("floor price")
    x_license     the row's own license (the table is internal as a whole; see below)

    python warehouse/connectors/iso_capacity_prices.py                      # all four markets
    python warehouse/connectors/iso_capacity_prices.py --only nyiso         # one market (pjm, nyiso, isone, miso)
    python warehouse/connectors/iso_capacity_prices.py --out-dir C:/scratch # a trial run: nothing in warehouse/output
    python warehouse/connectors/iso_capacity_prices.py --offline            # from the raw files only, no request

The session 65 prompt calls the table `capacity_prices`. That name has two parts and the standard needs three with
the publisher first (Decision 19, the same finding as session 7), and partition keys are columns (Decision 28), so
it is iso_all_capacity_prices with the market in `market`. pjm_rpm_capacity_prices (session 7, the daily run's) is
left as it is; this table's PJM rows are read from the same workbook by the same parser
(warehouse/connectors/capacity_prices.py).

Sources, each the publisher's own posting:

  PJM     "RPM Resource Clearing Prices for all RPM Auctions held to date" workbook. Base Residual Auction, the
          headline product, the RTO and every LDA PJM modeled, every delivery year. A "**" cell (not modeled) is no
          row.
  NYISO   The ICAP market's public "View Spot Auction Summary" page, one request per month from 2018-01: the Price
          ($/kW-M) of NYCA, the G-J Locality, NYC and LI (UCAP basis). The external areas on the page are not kept.
  ISO-NE  The table "Results of the Annual Forward Capacity Auctions" on the Markets key-statistics page: every
          auction, the price cell as printed. A price printed without a zone is the system-wide price
          (isone:System-wide); a zone printed with its own price is its own row. A zone the cell does not print is
          not written: it is not filled from the system price.
  MISO    The Planning Resource Auction "Results Posting" of each planning year (PDF): the page "<Season> PRA
          Results by Zone", row ACP ($/MW-Day), zones 1 to 10 and the external zones (ERZ), each matched to its
          column by position. Seasonal auctions only, planning years 2024/25 on: the postings of 2021/22 to 2023/24
          are not in MISO's document list, the 2019 and 2020 postings are annual auctions with another layout and
          are not read, and the history table in the later postings merges cells, so it cannot be read reliably. Those years are reported as gaps, not estimated.

California has no capacity market and ERCOT is energy-only: neither has rows (the methods doc says why, and what a
person would need to do for the CPUC's resource adequacy price statistics).

License: internal as a whole (a table is internal if any of its sources is). Per row, x_license:
  PJM     internal. PJM's data license bars non-members from republishing (docs/price-sources.md, section 7).
  ISO-NE  internal. https://www.iso-ne.com/legal-privacy: "Any duplication of the Content or non-personal use may
          violate copyright, trademark, and other laws."
  MISO    internal. https://www.misoenergy.org/meet-miso/legal-and-privacy/: "You are not permitted to modify,
          publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of,
          distribute, publicly perform, publicly display or in any way exploit any of the materials or content".
  NYISO   public by the ERW's standing rule (docs/datastandard.md: every source but PJM), with a caution:
          https://www.nyiso.com/legal-notice grants no license ("Access to this Web site does not confer any
          license or ownership interest in either the form or content of the Web site"). A person decides whether
          NYISO's rows may be shown; until then the table is internal.

Never fill: a cell the publisher marks as not a price, a month whose page shows no auction, a zone a PDF row lacks,
is no row and a gap in the run's status. Ceiling: 5,000 rows (session 65 ruling); a pull that would pass it writes
nothing. Raw files stay in warehouse/raw/iso_capacity_prices/ and are not requested twice (iso_prices.fetch_raw).
"""

import argparse
import calendar
import datetime as dt
import html
import io
import json
import os
import re
import sys
import traceback
from html.parser import HTMLParser

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import capacity_prices as pjm_rpm  # noqa: E402  (the PJM workbook's parser, session 7)

NAME = "iso_all_capacity_prices"
CONNECTOR = "iso_capacity_prices"
CEILING = 5_000
COLS = ip.SERIES_COLS + ["x_auction", "x_period_end", "x_note", "x_license"]
PAUSE = 3
UA = {"User-Agent": "Mozilla/5.0 (ERW research warehouse)"}

NYISO_FIRST = "2018-01"
NYISO_BASE = "https://icappublic.nyiso.com/ucap"
NYISO_SEASONS = NYISO_BASE + "/rest/seasons/public"
NYISO_SPOT = NYISO_BASE + "/public/auc_view_spot_detail.do?seasonId={}&month={}%2F{}&display=Display"
NYISO_PAGE = NYISO_BASE + "/public/auc_view_spot_selection.do"
NYISO_LOCALITIES = ["NYCA", "G-J Locality", "NYC", "LI"]
NYISO_EXTERNAL = {"HQ", "IESO", "NE", "PJM"}

ISONE_PAGE = "https://www.iso-ne.com/about/key-stats/markets"
ISONE_GEO = "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"

MISO_PAGE = "https://www.misoenergy.org/planning/resource-adequacy2/resource-adequacy/"
MISO_POSTINGS = {  # planning year (its first calendar year): the Results Posting on MISO's document host
    2024: "https://cdn.misoenergy.org/2024%20PRA%20Results%20Posting%2020240425632665.pdf",
    2025: "https://cdn.misoenergy.org/2025%20PRA%20Results%20Posting%2020250529_Corrections694160.pdf",
    # the posting of 2026-04-28 was replaced by a corrected one on 2026-05-22; the first link now answers 403
    2026: "https://cdn.misoenergy.org/2026%20PRA%20Results%20Posting%2020260522%20-%20Corrections754715.pdf",
}
MISO_FIND = "https://www.misoenergy.org/api/find/Optics_Models_Find_RemoteHostedContentItem/_search"  # the page's own list
MISO_NOT_HELD = ("planning year 2023/24 (seasonal) and the annual auctions before it: MISO's document list holds no "
                 "Results Posting for 2021/22 to 2023/24, the 2019 and 2020 postings are annual with another layout "
                 "and are not read, and the history table in later postings merges cells")
MISO_ZONES = [f"Z{i}" for i in range(1, 11)]
SEASONS = {"Summer": (6, 1, 8), "Fall": (9, 1, 11), "Winter": (12, 1, 2), "Spring": (3, 1, 5)}  # start month, day, end month

SOURCES = {
    "pjm:rpm-clearing-price-summary": dict(publisher=ip.ISO_PUBLISHERS["pjm"], report=pjm_rpm.REPORT,
                                           report_url=pjm_rpm.PAGE, document_list=pjm_rpm.URL, license="internal"),
    "nyiso:icap-spot-auction": dict(publisher=ip.ISO_PUBLISHERS["nyiso"],
                                    report="ICAP Spot Market Auction Results (View Spot Auction Summary), UCAP",
                                    report_url=NYISO_PAGE, document_list=NYISO_SEASONS, license="public"),
    "isone:fca-results": dict(publisher=ip.ISO_PUBLISHERS["isone"],
                              report="Results of the Annual Forward Capacity Auctions (Markets key statistics)",
                              report_url=ISONE_PAGE, document_list=ISONE_PAGE, license="internal"),
    "miso:pra-results-posting": dict(publisher=ip.ISO_PUBLISHERS["miso"],
                                     report="Planning Resource Auction Results Posting, results by zone",
                                     report_url=MISO_PAGE, document_list=MISO_PAGE, license="internal"),
}


def last_day(year, month):
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


# ---------------------------------------------------------------------------
# PJM
# ---------------------------------------------------------------------------

def pull_pjm(log, offline):
    raw, rec = ip.fetch_raw(CONNECTOR, pjm_rpm.URL, log, offline=offline, fresh=True, pause=PAUSE, headers=UA)
    if raw[:2] != b"PK":
        raise RuntimeError("PJM workbook: the answer is not an xlsx file")
    cells, newest = pjm_rpm.parse(raw, log)
    rows = [dict(entity=f"pjm:{lda}", variable="capacity_price", ts_utc=f"{dy}-06-01T00:00:00Z", value=price,
                 unit="USD/MW-day", freq="P1Y", geo="US", market="pjm_bra", node=lda,
                 source="pjm:rpm-clearing-price-summary", source_url=rec["url"], retrieved_at=rec["retrieved_at"],
                 vintage=ip.vintage_of(rec), x_auction=f"BRA {dy}/{dy + 1}", x_period_end=f"{dy + 1}-05-31",
                 x_note="", x_license="internal") for dy, lda, price in cells]
    return rows, []


# ---------------------------------------------------------------------------
# NYISO
# ---------------------------------------------------------------------------

def nyiso_season_ids(raw):
    """{(type, first year): season id} from the ICAP application's public season list."""
    out = {}
    for r in json.loads(raw)["rows"]:
        m = re.match(r"^(Summer|Winter) (\d{4})(?:-\d{4})?$", r["description"])
        if not m:
            raise RuntimeError(f"NYISO season {r['description']!r}: not 'Summer YYYY' or 'Winter YYYY-YYYY'")
        out[(m.group(1), int(m.group(2)))] = r["id"]
    return out


def nyiso_season_of(year, month):
    """The capability period a month belongs to: Summer is May to October, Winter November to April."""
    if 5 <= month <= 10:
        return "Summer", year
    return "Winter", year if month >= 11 else year - 1


def parse_nyiso(page, year, month):
    """One month's spot auction page: ({locality: price}, posted time in UTC), or None when the page shows no
    auction for the month. Every locality on the page must carry a price."""
    text = page.decode("utf-8", "replace") if isinstance(page, bytes) else page
    want = f"{month:02d}/{year}"
    if not re.search(re.escape(want) + r"(?:&nbsp;|\s)+Spot Market Auction Results - UCAP", text):
        return None
    m = re.search(r"Posted Date:(?:&nbsp;|\s)*(\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} [AP]M)", text)
    if not m:
        raise RuntimeError(f"NYISO {want}: no Posted Date")
    posted = pd.Timestamp(dt.datetime.strptime(m.group(1), "%m/%d/%Y %I:%M %p")).tz_localize("America/New_York")
    blocks = re.split(r'<td colspan="2" class="inputLabel left noBorder">', text)[1:]
    prices = {}
    for b in blocks:
        name = html.unescape(re.sub(r"<[^>]+>", "", b.split("</td>", 1)[0])).strip()
        p = re.search(r"Price \(\$/kW-M\)\s*</td>\s*<td[^>]*>\s*\$([\d,]+\.\d{2})\s*</td>", b)
        if name in NYISO_LOCALITIES:
            if not p:
                raise RuntimeError(f"NYISO {want}: {name} has no Price ($/kW-M)")
            prices[name] = float(p.group(1).replace(",", ""))
        elif name not in NYISO_EXTERNAL and p:
            raise RuntimeError(f"NYISO {want}: unknown locality {name!r}")
    return prices, ip.utc_iso(posted)


def pull_nyiso(log, offline):
    raw, _ = ip.fetch_raw(CONNECTOR, NYISO_SEASONS, log, offline=offline, fresh=True, pause=PAUSE)
    ids = nyiso_season_ids(raw)
    now = pd.Timestamp.now(tz="America/New_York")
    months = pd.period_range(NYISO_FIRST, (now + pd.DateOffset(months=1)).strftime("%Y-%m"), freq="M")
    rows, gaps = [], []
    for p in months:
        y, mo = p.year, p.month
        season = nyiso_season_of(y, mo)
        if season not in ids:
            raise RuntimeError(f"NYISO: no season id for {season}")
        url = NYISO_SPOT.format(ids[season], f"{mo:02d}", y)
        future = (y, mo) > (now.year, now.month)
        got = None
        for fresh in (False, True):  # a saved page from before the auction was posted is fetched again
            page, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, fresh=fresh,
                                     pause=PAUSE)
            got = parse_nyiso(page, y, mo)
            if got or offline or not rec["cached"]:
                break
        if not got:
            if not future:
                gaps.append(f"nyiso {y}-{mo:02d}: the page shows no spot auction")
                log(f"  gap: NYISO {y}-{mo:02d}: no spot auction on the page")
            continue
        prices, posted = got
        for loc in NYISO_LOCALITIES:
            if loc not in prices:
                # the G-J Locality exists from May 2014; inside the window every month should print all four
                gaps.append(f"nyiso {y}-{mo:02d} {loc}: not on the page")
                log(f"  gap: NYISO {y}-{mo:02d}: {loc} not on the page")
                continue
            rows.append(dict(entity=f"nyiso:{loc}", variable="capacity_price", ts_utc=f"{y}-{mo:02d}-01T00:00:00Z",
                             value=prices[loc], unit="USD/kW-month", freq="P1M", geo="US-NY",
                             market="nyiso_icap_spot", node=loc, source="nyiso:icap-spot-auction",
                             source_url=rec["url"], retrieved_at=rec["retrieved_at"], vintage=posted,
                             x_auction=f"Spot {mo:02d}/{y}", x_period_end=last_day(y, mo), x_note="UCAP",
                             x_license="public"))
    return rows, gaps


# ---------------------------------------------------------------------------
# ISO-NE
# ---------------------------------------------------------------------------

class _Tables(HTMLParser):
    """Every table of a page as rows of cell texts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.row, self.cell, self.depth = [], None, None, 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
            self.depth += 1
        elif tag == "tr" and self.depth:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "sup" and self.cell is not None:
            self.cell.append("\x00")  # footnote marks are not part of the value

    def handle_endtag(self, tag):
        if tag == "table" and self.depth:
            self.depth -= 1
        elif tag in ("td", "th") and self.cell is not None and self.row is not None:
            text = re.sub(r"\x00[^\x01]*?\x01", "", "".join(self.cell))
            self.row.append(" ".join(text.replace("\x00", "").replace("\x01", "").split()))
            self.cell = None
        elif tag == "sup" and self.cell is not None:
            self.cell.append("\x01")
        elif tag == "tr" and self.row is not None and self.tables:
            self.tables[-1].append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


PRICE_TOKEN = re.compile(r"(?:(?P<zone>[A-Za-z][A-Za-z/\- ]*?)\s*:\s*)?\$(?P<price>\d+\.\d{3})(?:/(?P<kind>new|existing))?")


def parse_isone_cell(cell):
    """The clearing price cell as [(zone, variable, price, note)]. A price without a zone is the system-wide one; a
    price after '&' without its own zone belongs to the zone before it. Anything the grammar does not know fails."""
    out, zone, note = [], None, ""
    rest = cell
    if "(floor price)" in rest:
        note = "floor price"
    for m in PRICE_TOKEN.finditer(cell):
        z = m.group("zone")
        if z:
            zone = z.strip()
        elif zone is None or not cell[:m.start()].rstrip().endswith("&"):
            zone = "System-wide"
        var = "capacity_price" + (f"_{m.group('kind')}" if m.group("kind") else "")
        out.append((zone, var, float(m.group("price")), note if zone == "System-wide" else ""))
    rest = PRICE_TOKEN.sub("", cell).replace("(floor price)", "").replace("&", "")
    if rest.strip() or not out:
        raise RuntimeError(f"ISO-NE clearing price cell not understood: {cell!r} (left over: {rest.strip()!r})")
    if len({(z, v) for z, v, _, _ in out}) != len(out):
        raise RuntimeError(f"ISO-NE clearing price cell repeats a zone: {cell!r}")
    return out


def parse_isone(page):
    """[(fca, auction year, ccp start year, zone, variable, price, note)] from the key-statistics page."""
    t = _Tables()
    t.feed(page.decode("utf-8", "replace") if isinstance(page, bytes) else page)
    table = [tb for tb in t.tables if tb and any("Clearing Price" in c for c in tb[0]) and
             any("Auction" in c for c in tb[0])]
    if len(table) != 1:
        raise RuntimeError(f"ISO-NE page: {len(table)} tables with an Auction and a Clearing Price column, expected 1")
    head = table[0][0]
    col = [i for i, c in enumerate(head) if "Clearing Price" in c]
    if len(col) != 1 or "$/kW-month" not in head[col[0]]:
        raise RuntimeError(f"ISO-NE table header {head}: no single Clearing Price ($/kW-month) column")
    out, seen = [], []
    for row in table[0][1:]:
        m = re.match(r"^FCA (\d+) in (\d{4}) for CCP (\d{4})/(\d{4})$", row[0])
        if not m or len(row) != len(head):
            raise RuntimeError(f"ISO-NE table row not understood: {row}")
        fca, held, y0, y1 = (int(g) for g in m.groups())
        if y1 != y0 + 1:
            raise RuntimeError(f"ISO-NE FCA {fca}: commitment period {y0}/{y1}")
        seen.append(fca)
        for zone, var, price, note in parse_isone_cell(row[col[0]]):
            out.append((fca, held, y0, zone, var, price, note))
    if sorted(seen) != list(range(1, max(seen) + 1)) or max(seen) < 18:
        raise RuntimeError(f"ISO-NE table lists auctions {sorted(seen)}: not FCA 1 to at least 18, each once")
    return out


def pull_isone(log, offline):
    raw, rec = ip.fetch_raw(CONNECTOR, ISONE_PAGE, log, offline=offline, fresh=True, pause=PAUSE)
    rows = [dict(entity=f"isone:{zone}", variable=var, ts_utc=f"{y0}-06-01T00:00:00Z", value=price,
                 unit="USD/kW-month", freq="P1Y", geo=ISONE_GEO, market="isone_fca", node=zone,
                 source="isone:fca-results", source_url=rec["url"], retrieved_at=rec["retrieved_at"],
                 vintage=ip.vintage_of(rec), x_auction=f"FCA {fca}", x_period_end=f"{y0 + 1}-05-31", x_note=note,
                 x_license="internal") for fca, held, y0, zone, var, price, note in parse_isone(raw)]
    return rows, []


# ---------------------------------------------------------------------------
# MISO
# ---------------------------------------------------------------------------

SEASON_TITLE = re.compile(r"^(Summer|Fall|Winter|Spring) (\d{4})(?:[/-]\d{2,4})? PRA Results by Zone\b")
MONEY = re.compile(r"^\$?(\d{1,4}\.\d{2})$")  # the 2026 posting prints the dollar sign, the earlier ones do not
ZONE_LABEL = re.compile(r"^(Z(?:10|[1-9])|ERZ)[^A-Za-z0-9]?$")  # the 2026 posting hangs a footnote mark on ERZ


def parse_miso(raw, py):
    """[(season, start date, end date, zone, price)] from one Results Posting: the four '<Season> PRA Results by
    Zone' pages, the row ACP ($/MW-Day), each price matched to the zone column it sits under."""
    import pdfplumber
    out, seen = [], []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            title = next((SEASON_TITLE.match(line.strip()) for line in text.splitlines()
                          if SEASON_TITLE.match(line.strip())), None)
            if not title:
                continue
            season, year = title.group(1), int(title.group(2))
            words = page.extract_words()
            mid = lambda w: (w["x0"] + w["x1"]) / 2  # noqa: E731
            head = {}
            for w in words:
                zl = ZONE_LABEL.match(w["text"])
                if zl and zl.group(1) not in head:
                    head[zl.group(1)] = w
            if [z for z in MISO_ZONES + ["ERZ"] if z not in head]:
                raise RuntimeError(f"MISO {season} {year}: the zone header is not Z1 to Z10 and ERZ")
            tops = {round(head[z]["top"]) for z in head}
            if max(tops) - min(tops) > 3:
                raise RuntimeError(f"MISO {season} {year}: the zone labels are not on one line")
            acp = [w for w in words if w["text"] == "ACP" and w["top"] > head["Z1"]["top"]]
            if len(acp) != 1:
                raise RuntimeError(f"MISO {season} {year}: {len(acp)} ACP rows on the page, expected 1")
            y = (acp[0]["top"] + acp[0]["bottom"]) / 2
            near = [w for w in words if MONEY.match(w["text"]) and abs((w["top"] + w["bottom"]) / 2 - y) <= 16]
            # the prices sit on one text line; a cell that wraps (the external zones' "83.24-" over "91.60", a range)
            # puts a number on another line, and that number is not a price of the row
            under_z1 = [w for w in near if abs(mid(w) - mid(head["Z1"])) <= (mid(head["Z2"]) - mid(head["Z1"])) * 0.45]
            if len(under_z1) != 1:
                raise RuntimeError(f"MISO {season} {year}: {len(under_z1)} prices under Z1 near the ACP row")
            line = [w for w in near if abs(w["top"] - under_z1[0]["top"]) <= 2]
            step = (mid(head["Z10"]) - mid(head["Z1"])) / 9
            got = {}
            for w in line:
                z = min(head, key=lambda k: abs(mid(head[k]) - mid(w)))
                if abs(mid(head[z]) - mid(w)) > step * 0.45:
                    continue  # a number under the totals columns, not a zone
                if z in got:
                    raise RuntimeError(f"MISO {season} {year}: two prices under {z}")
                got[z] = float(MONEY.match(w["text"]).group(1))
            missing = [z for z in MISO_ZONES if z not in got]
            if missing:
                raise RuntimeError(f"MISO {season} {year}: no ACP under {missing}")
            sm, sd, em = SEASONS[season]
            if (season, year) != {"Summer": ("Summer", py), "Fall": ("Fall", py), "Winter": ("Winter", py),
                                  "Spring": ("Spring", py + 1)}[season]:
                raise RuntimeError(f"MISO planning year {py}/{py + 1}: unexpected page {season} {year}")
            end_year = year + 1 if season == "Winter" else year
            seen.append(season)
            for z in MISO_ZONES + ["ERZ"]:
                if z in got:  # the external zones' cell is sometimes a range, not one price: then no row
                    label = f"{season} {year}/{str(year + 1)[2:]}" if season == "Winter" else f"{season} {year}"
                    out.append((label, f"{year}-{sm:02d}-{sd:02d}", last_day(end_year, em), z, got[z]))
    if sorted(seen) != sorted(SEASONS):
        raise RuntimeError(f"MISO planning year {py}/{py + 1}: seasons found {seen}, expected each of {list(SEASONS)} once")
    return out


def pull_miso(log, offline):
    rows = []
    gaps = [f"miso: {MISO_NOT_HELD}"]
    for py, url in sorted(MISO_POSTINGS.items()):
        try:
            raw, rec = ip.fetch_raw(CONNECTOR, url, log, offline=offline, pause=PAUSE)
        except ip.SourceGap as exc:
            gaps.append(f"miso planning year {py}/{py + 1}: {exc}")
            log(f"  gap: MISO {py}/{py + 1}: {exc}")
            continue
        if raw[:5] != b"%PDF-":
            raise RuntimeError(f"MISO {py}: the answer is not a PDF")
        cells = parse_miso(raw, py)
        erz = {c[0] for c in cells if c[3] == "ERZ"}
        for s in sorted({c[0] for c in cells} - erz):
            gaps.append(f"miso {s} ERZ: the posting prints no single price for the external zones")
        for label, start, end, zone, price in cells:
            rows.append(dict(entity=f"miso:{zone}", variable="capacity_price", ts_utc=f"{start}T00:00:00Z",
                             value=price, unit="USD/MW-day", freq="P3M", geo="US", market="miso_pra", node=zone,
                             source="miso:pra-results-posting", source_url=rec["url"],
                             retrieved_at=rec["retrieved_at"], vintage=ip.vintage_of(rec),
                             x_auction=f"PRA {py}/{str(py + 1)[2:]} {label}", x_period_end=end, x_note="",
                             x_license="internal"))
        log(f"  MISO {py}/{py + 1}: {len(cells)} prices")
    return rows, gaps


PULLS = {"pjm": pull_pjm, "nyiso": pull_nyiso, "isone": pull_isone, "miso": pull_miso}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: capacity prices, PJM, NYISO, ISO-NE, MISO")
    ap.add_argument("--only", action="append", choices=sorted(PULLS), help="pull this market only (repeatable)")
    ap.add_argument("--out-dir", help="write the table, log, registry and status under this directory instead of "
                    "the repository (raw files stay in warehouse/raw)")
    ap.add_argument("--offline", action="store_true", help="read the raw files only; make no request")
    a = ap.parse_args(argv)
    raw_dir = ip.RAW_DIR
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
        ip.RAW_DIR = raw_dir  # source documents are kept once, in warehouse/raw, whatever the output directory
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results, rows, done = [], [], []
    for market in a.only or sorted(PULLS):  # one market at a time; a market that fails writes none of its rows
        if ip.paused(market):  # session 89: no request; the market's rows in the table are kept by the merge writer
            log(f"{market}: {ip.pause_line(market)}")
            print(f"{CONNECTOR} {market} {ip.pause_line(market)}")
            results.append(dict(table=NAME, market=market, status="skipped", detail=ip.pause_line(market)[:300]))
            continue
        try:
            log(f"{market}:")
            r, gaps = PULLS[market](log, a.offline)
            if not r:
                raise RuntimeError("no rows parsed")
            rows += r
            done.append(market)
            log(f"  {market}: {len(r)} rows")
            results.append(dict(table=NAME, market=market, status="ok", detail=f"{len(r)} rows"))
            results += [dict(table=NAME, market=market, status="gap", detail=g[:300]) for g in gaps]
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{NAME} {market} FAILED, none of its rows written:\n{tb}")
            print(f"{CONNECTOR} {market} FAILED, none of its rows written: {last}", file=sys.stderr)
            results.append(dict(table=NAME, market=market, status="failed", detail=last[:300]))
    try:
        if rows:
            s = pd.DataFrame(rows)[COLS].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
            if len(s) > CEILING:
                raise RuntimeError(f"{len(s)} rows would pass the ceiling of {CEILING}; nothing written")
            counts = s.groupby("market").size().to_dict()
            header = [
                "Energy Research Warehouse (ERW): capacity prices, PJM Base Residual Auction, NYISO ICAP spot "
                "auction, ISO-NE Forward Capacity Auction, MISO Planning Resource Auction",
                "Shape: series (docs/datastandard.md v0), partition column market. One row per market, zone, delivery "
                "period and auction; value is the clearing price as published, in the unit column's unit (USD/MW-day "
                "or USD/kW-month); nothing is converted. ts_utc is the first day of the delivery period, "
                "x_period_end its last.",
                "Markets in this run: " + "; ".join(f"{m} {n} rows" for m, n in sorted(counts.items())) + "."
                + "".join(f" Paused, its rows kept from its last pull: {m} ({ip.paused(m)['reason']}, since "
                          f"{ip.paused(m)['paused_on']})." for m in sorted(PULLS) if ip.paused(m)),
                "Not in the table: ERCOT (energy-only: no capacity price exists), California (no capacity market; "
                "the CPUC's resource adequacy price statistics are not pulled), PJM's incremental auctions, NYISO's "
                "strip and monthly auctions, ISO-NE's reconfiguration auctions, MISO planning years before 2024/25.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/iso_capacity_prices.py",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; each run's manifest.csv lists each file and URL)",
            ] + [f"Source: {sid} {v['publisher']}, {v['report']}, {v['report_url']}" for sid, v in SOURCES.items()
                 if sid.split(":")[0] in done] + [
                "License: internal. PJM's, ISO-NE's and MISO's terms do not allow republishing; x_license gives each "
                "row's own license (NYISO public by the ERW's standing rule; its terms grant no license in writing).",
                "Method: docs/methods/capacity_and_ancillary.md",
            ]
            ip.write_csv(s, NAME, header, log, cols=COLS)
            ip.update_sources([dict(source=sid, tables=[NAME], **v) for sid, v in SOURCES.items()
                               if sid.split(":")[0] in done])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    failures = sum(r["status"] == "failed" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"{CONNECTOR} run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
