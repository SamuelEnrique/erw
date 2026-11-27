#!/usr/bin/env python3
"""The page files of energy equities (session 10000, chain 701, part D4), by the contract docs/state/page_files_equities.md.

Energy Research Warehouse (ERW). Writes, from warehouse tables only (no request):

    site/data/equities/index.json          the segments, the companies and the indices (the lists)
    site/data/equities/board.json          the rows the price board's equities group shows, in the board's own row form
    site/data/equities/energy_prices.json  the energy prices set beside the equities, daily where the table is daily

Today the equity side holds nothing a page may show: SEC EDGAR, the one source of each company's industry code, share
count and statements, refuses the ERW's contact string, and no free source of daily share prices may be kept
(docs/reviews/equities-sources-2026-11-26.md). So the segments carry their names and the reason their rule cannot be
applied, the lists of companies and indices are empty, every board row is held with that reason, and no company or
index file is written. The energy prices are the warehouse's own:

    wti, brent, henry_hub   eia_fuel_spot_prices (EIA's daily spot prices), daily
    uranium                 imf_commodity_prices (IMF PCPS, PURAN), monthly, on its own dates
    cca_current             carb_auction_allowance_prices (CARB's quarterly auctions, current vintage), on its own dates
    ercot_hb_hubavg_da      ercot_hub_prices_daily (da_mean of ercot:HB_HUBAVG), daily
    caiso_sp15_da, caiso_np15_da   iso_hub_prices_history (caiso_dam), the mean of each complete Pacific day's 24 hours
                            (23 or 25 on the clock-change days); a day short of an hour is not written
    pjm, nyiso, isone, miso the grids docs/licenses.md holds or MISO's pause: a series with its status and no rows

Each daily series is written from 2016-01-01 (the contract's span is that of the longest shown equity series; none is
shown yet, so the last ten whole years and this one: a dated line of the contract says so).

    python warehouse/derived/equity_page_files.py [--out DIR]

Since 27 November 2026 (the owner's ruling gave the SEC a contact address): the segments carry the written rule and
their counts, and the companies and their filed statements come from equity_universe and
equity_fundamentals_quarterly (warehouse/connectors/sec_edgar.py), one series file a company under series/; share
prices and index levels stay held (no source a license allows).

Method: docs/methods/equities.md.
"""

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "site", "data", "equities")
METHOD = "docs/methods/equities.md"
CONTRACT = "docs/state/page_files_equities.md"
SINCE = "2016-01-01"
SEC_WHY = ("source needed: the segment rule reads each company's SEC industry code (SIC), and SEC EDGAR refuses the ERW's "
           "contact string (docs/reviews/equities-sources-2026-11-26.md); no company is put in a segment by judgment")
PRICE_WHY = ("license needed: no source found whose terms allow the ERW to keep daily share prices or index levels "
             "(docs/reviews/equities-sources-2026-11-26.md)")
SEGMENTS = [("integrated_oil_gas", "Integrated oil and gas"), ("exploration_production", "Exploration and production"),
            ("midstream_pipelines", "Midstream and pipelines"), ("refining", "Refining"), ("oilfield_services", "Oilfield services"),
            ("lng", "LNG"), ("coal", "Coal"), ("regulated_utilities", "Regulated electric and gas utilities"),
            ("independent_power", "Independent power producers"), ("nuclear_uranium", "Nuclear and uranium"), ("solar", "Solar"),
            ("wind", "Wind"), ("storage", "Storage"), ("hydrogen_fuel_cells", "Hydrogen and fuel cells"),
            ("grid_equipment", "Grid and electrical equipment")]
# session 10000 (chain 701), after the owner's ruling of 26 November 2026 gave the SEC a contact address: the written rule
# (warehouse/connectors/sec_edgar.py SIC_SEGMENTS and NO_CODE, docs/methods/equities.md "The universe") in words
SEG_RULE = {
    "integrated_oil_gas": "SEC industry code 2911 (petroleum refining), which does not separate integrated companies from refiners: in both",
    "exploration_production": "SEC industry code 1311 (crude petroleum and natural gas)",
    "midstream_pipelines": "SEC industry codes 4610 (pipelines), 4922 (gas transmission), 4923 and 4924 (gas transmission and distribution; "
                           "gas distribution and the LNG exporters: in both segments)",
    "refining": "SEC industry code 2911 (petroleum refining), which does not separate refiners from integrated companies: in both",
    "oilfield_services": "SEC industry codes 1381, 1382 and 1389 (drilling, exploration and field services) and 3533 (field machinery)",
    "coal": "SEC industry codes 1220, 1221 and 1222 (coal mining)",
    "regulated_utilities": "SEC industry codes 4911 (electric services, also in independent power), 4923, 4924 (also in midstream), "
                           "4931, 4932 and 4939 (combined utilities)",
    "independent_power": "SEC industry codes 4911 (electric services, also in regulated utilities) and 4991 (cogeneration and small power)",
    "grid_equipment": "SEC industry codes 3612 (transformers) and 3613 (switchgear)",
}
NO_CODE = {
    "lng": "no SEC industry code is LNG alone: the exporters file under 4924 with the local gas distributors",
    "nuclear_uranium": "no SEC industry code is nuclear or uranium alone: uranium miners file under 1090 or 1400 with other ores, reactor owners under 4911",
    "solar": "no SEC industry code is solar alone: makers of cells and inverters file under 3674 with all semiconductors",
    "wind": "no SEC industry code is wind alone: turbine makers file under 3510, 3511 or 3600 with all engines and electrical equipment",
    "storage": "no SEC industry code is storage alone: 3690 holds batteries with consumer batteries and unrelated equipment",
    "hydrogen_fuel_cells": "no SEC industry code is hydrogen or fuel cells alone: 2810 holds the industrial gases with pigments, 3620 fuel cells with all electrical apparatus",
}
FUND_WHY = ("no us-gaap 10-Q or 10-K facts on EDGAR: a foreign filer's 20-F or 40-F (often IFRS) is not read, and some "
            "partnerships file other concepts (docs/methods/equities.md)")
SEC_SOURCE = ("U.S. Securities and Exchange Commission, EDGAR: each company's submissions and XBRL company facts, "
              "https://www.sec.gov/search-filings/edgar-application-programming-interfaces")
QCOLS = ["period_start", "period_end", "months", "fy", "fp", "form", "filed", "revenue", "net_income", "capex", "debt",
         "shares_outstanding", "accession", "url"]
LINE = {"revenue": "revenue", "net_income": "net_income", "capex": "capex", "long_term_debt_usd": "debt",
        "shares_outstanding": "shares_outstanding"}
HELD_GRIDS = [("pjm_western_hub_da", "PJM Western Hub, day-ahead", "license needed",
               "PJM's terms allow republication to members only (docs/licenses.md); held until a permission is recorded"),
              ("nyiso_zone_j_da", "NYISO New York City, day-ahead", "license needed",
               "NYISO's terms ask for written permission to republish (docs/licenses.md); none is recorded"),
              ("isone_mass_hub_da", "ISO-NE Mass Hub, day-ahead", "license needed",
               "ISO-NE's terms ask for written permission to republish (docs/licenses.md); none is recorded"),
              ("miso_indiana_hub_da", "MISO Indiana Hub, day-ahead", "paused",
               "MISO is paused since 4 October 2026: its terms forbid automated access (docs/methods/miso_pause.md)")]


def read(table, entity=None, variable=None):
    path = os.path.join(ip.OUT_DIR, table + ".csv")
    parts = []
    for ch in pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, chunksize=500_000):
        if entity is not None:
            ch = ch[ch["entity"] == entity]
        if variable is not None:
            ch = ch[ch["variable"] == variable]
        if len(ch):
            parts.append(ch)
    if not parts:
        raise RuntimeError(f"{table}: no rows of {entity} {variable}")
    return pd.concat(parts, ignore_index=True)


def by_day(df):
    """[(YYYY-MM-DD, value)] from a table's rows dated at a day's 00:00Z, oldest first."""
    s = sorted((t[:10], float(v)) for t, v in zip(df["ts_utc"], df["value"]) if v != "")
    return s


def caiso_daily(node):
    """The mean of each complete Pacific day of CAISO's day-ahead price at a node (iso_hub_prices_history)."""
    df = read("iso_hub_prices_history", entity=f"caiso:{node}")
    df = df[df["market"] == "caiso_dam"]
    t = pd.to_datetime(df["ts_utc"], utc=True)
    loc = t.dt.tz_convert("America/Los_Angeles")
    d = pd.DataFrame({"day": loc.dt.strftime("%Y-%m-%d"), "v": df["value"].astype(float), "t": t}).drop_duplicates("t")
    out = []
    for day, g in d.groupby("day"):
        start = pd.Timestamp(day).tz_localize("America/Los_Angeles")
        end = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize("America/Los_Angeles")
        hours = round((end - start).total_seconds() / 3600)   # 24; 23 or 25 on the clock-change days
        if len(g) == hours:
            out.append((day, float(round(g["v"].mean(), 4))))
    return out


def move(series, last_day, last_v, back):
    """The board's move: the value on the last day held on or before `back`, and the change to the last value."""
    prior = [(d, v) for d, v in series if d <= back]
    if not prior:
        return None
    d, v = prior[-1]
    ch = last_v - v
    return {"t": d, "v": v, "ch": round(ch, 4), "pct": round(ch / v * 100, 2) if v else None}


def moves(series):
    if not series:
        return {"d": None, "w": None, "m": None, "ytd": None, "y": None}
    last_d, last_v = series[-1]
    day = dt.date.fromisoformat(last_d)
    prev = series[-2][0] if len(series) > 1 else None

    def back_months(n):
        y, m = day.year, day.month - n
        while m < 1:
            y, m = y - 1, m + 12
        import calendar
        return dt.date(y, m, min(day.day, calendar.monthrange(y, m)[1])).isoformat()
    return {"d": move(series, last_d, last_v, prev) if prev else None,
            "w": move(series, last_d, last_v, (day - dt.timedelta(days=7)).isoformat()),
            "m": move(series, last_d, last_v, back_months(1)),
            "ytd": move(series, last_d, last_v, dt.date(day.year - 1, 12, 31).isoformat()),
            "y": move(series, last_d, last_v, back_months(12))}


def energy_series():
    spot = "EIA's daily spot prices (eia_fuel_spot_prices; EIA names Refinitiv, an LSEG business, as their source), https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm"
    specs = [
        ("wti", "WTI crude oil, Cushing, spot", "USD/bbl", "D", "eia_fuel_spot_prices", "eia:wti_cushing", "spot_price", spot,
         lambda: by_day(read("eia_fuel_spot_prices", "eia:wti_cushing", "spot_price"))),
        ("brent", "Brent crude oil, Europe, spot", "USD/bbl", "D", "eia_fuel_spot_prices", "eia:brent", "spot_price", spot,
         lambda: by_day(read("eia_fuel_spot_prices", "eia:brent", "spot_price"))),
        ("henry_hub", "Henry Hub natural gas, spot", "USD/MMBtu", "D", "eia_fuel_spot_prices", "eia:henry_hub", "spot_price", spot,
         lambda: by_day(read("eia_fuel_spot_prices", "eia:henry_hub", "spot_price"))),
        ("ercot_hb_hubavg_da", "ERCOT Hub average, day-ahead, daily mean", "USD/MWh", "D", "ercot_hub_prices_daily", "ercot:HB_HUBAVG", "da_mean",
         "ERCOT, from the ERW's daily table of its hub prices (ercot_hub_prices_daily)",
         lambda: by_day(read("ercot_hub_prices_daily", "ercot:HB_HUBAVG", "da_mean"))),
        ("caiso_sp15_da", "CAISO SP15, day-ahead, daily mean", "USD/MWh", "D", "iso_hub_prices_history", "caiso:TH_SP15_GEN-APND", "caiso_dam",
         "CAISO OASIS day-ahead LMP (iso_hub_prices_history), the mean of each complete Pacific day", lambda: caiso_daily("TH_SP15_GEN-APND")),
        ("caiso_np15_da", "CAISO NP15, day-ahead, daily mean", "USD/MWh", "D", "iso_hub_prices_history", "caiso:TH_NP15_GEN-APND", "caiso_dam",
         "CAISO OASIS day-ahead LMP (iso_hub_prices_history), the mean of each complete Pacific day", lambda: caiso_daily("TH_NP15_GEN-APND")),
        ("uranium", "Uranium, monthly average", "USD/lb", "M", "imf_commodity_prices", "imf:PCPS:PURAN", "price",
         "International Monetary Fund, Primary Commodity Price System (imf_commodity_prices)",
         lambda: by_day(read("imf_commodity_prices", "imf:PCPS:PURAN", "price"))),
        ("cca_current", "California carbon allowance, quarterly auction settlement (current vintage)", "USD/t CO2e", "Q",
         "carb_auction_allowance_prices", "carb:current_auction", "settlement_price",
         "California Air Resources Board, auction settlement prices (carb_auction_allowance_prices)",
         lambda: by_day(read("carb_auction_allowance_prices", "carb:current_auction", "settlement_price"))),
    ]
    series, daily = [], {}
    for sid, label, unit, freq, table, entity, variable, source, get in specs:
        s = get()
        s = [(d, v) for d, v in s if d >= SINCE] if freq == "D" else s
        series.append({"id": sid, "label": label, "unit": unit, "freq": freq, "table": table, "entity": entity, "variable": variable,
                       "source": source, "license": "public", "status": "shown", "why": None,
                       "first": s[0][0] if s else None, "last": s[-1][0] if s else None,
                       "last_value": {"t": s[-1][0], "v": s[-1][1]} if s else None, "moves": moves(s)})
        daily[sid] = [[d, v] for d, v in s]
    for sid, label, status, why in HELD_GRIDS:
        series.append({"id": sid, "label": label, "unit": "USD/MWh", "freq": "D", "table": None, "entity": None, "variable": None,
                       "source": None, "license": "internal" if status == "license needed" else None, "status": status, "why": why,
                       "first": None, "last": None, "last_value": None, "moves": {"d": None, "w": None, "m": None, "ytd": None, "y": None}})
    return series, daily


def table_or_none(table):
    path = os.path.join(ip.OUT_DIR, table + ".csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def num(v):
    if v in ("", None):
        return None
    f = float(v)
    return int(f) if f.is_integer() else f


def quarterly(f):
    """A company's rows of equity_fundamentals_quarterly as the contract's quarterly rows: each filing's own period (the
    newest period end in that filing), one row a period length, newest first; the instants of that end on each."""
    if f is None or f.empty:
        return [], {}
    f = f[f["variable"] != "shares_outstanding_cover"].copy()   # the cover's date is not the period's: not a row here
    own = f.groupby("x_accession")["ts_utc"].transform("max")
    f = f[f["ts_utc"] == own]
    f["line"] = f["variable"].str.replace(r"_\d+m_usd$", "", regex=True)
    out, concepts = [], {}
    for line, g in f.sort_values("vintage").groupby("line"):
        concepts[LINE.get(line, line)] = g["x_concept"].iloc[-1]
    for (acc, end), g in f.groupby(["x_accession", "ts_utc"]):
        inst = {LINE[r["line"]]: num(r["value"]) for _, r in g[g["x_months"] == ""].iterrows() if r["line"] in LINE}
        dur = g[g["x_months"] != ""]
        first = g.iloc[0]
        base = {"period_end": end[:10], "fy": num(first["x_fy"]), "fp": first["x_fp"] or None, "form": first["x_form"],
                "filed": first["vintage"][:10], "accession": acc, "url": first["source_url"]}
        groups = list(dur.groupby(["x_months", "x_period_start"])) or [((None, None), None)]
        for (m, start), d in groups:
            row = {**base, "period_start": start, "months": num(m) if m else None,
                   "revenue": None, "net_income": None, "capex": None, "debt": inst.get("debt"),
                   "shares_outstanding": inst.get("shares_outstanding")}
            if d is not None:
                for _, r in d.iterrows():
                    if r["line"] in LINE:
                        row[LINE[r["line"]]] = num(r["value"])
            out.append([row[c] for c in QCOLS])
    out.sort(key=lambda r: (r[1], r[6] or "", r[2] or 0), reverse=True)
    return out, concepts


def later(a, b):
    """True when quarterly row a was filed after b (the filing day, then the accession), as lib/equities.ts later()."""
    i_f, i_a = QCOLS.index("filed"), QCOLS.index("accession")
    return b is None or (a[i_f] or "", a[i_a] or "") > (b[i_f] or "", b[i_a] or "")


def newest_filed(q):
    """Done-line request 578: the newest period end a company filed and its figures, by the page's own rule
    (site/lib/equities.ts newestOf): each statement line the figure for the shortest period to that end (a 10-Q's 3
    months where filed, else its year to date, months saying which), debt and shares at that end; where a period was
    filed twice, the later filing's figure. None when nothing is filed."""
    if not q:
        return None
    ix = {c: i for i, c in enumerate(QCOLS)}
    end = max(r[ix["period_end"]] for r in q)
    rows = [r for r in q if r[ix["period_end"]] == end]
    head = None
    for r in rows:
        if later(r, head):
            head = r
    out = {"period_end": end, "form": head[ix["form"]], "filed": head[ix["filed"]], "url": head[ix["url"]]}
    for col in ("revenue", "net_income", "capex"):
        best = None
        for r in rows:
            if r[ix[col]] is None or r[ix["months"]] is None:
                continue
            if best is None or r[ix["months"]] < best[ix["months"]] or (r[ix["months"]] == best[ix["months"]] and later(r, best)):
                best = r
        out[col] = {"months": best[ix["months"]], "v": best[ix[col]]} if best else None
    for col in ("debt", "shares_outstanding"):
        best = None
        for r in rows:
            if r[ix[col]] is not None and later(r, best):
                best = r
        out[col] = best[ix[col]] if best else None
    return out


def shown_why(q, built, first_filed=None):
    """Done-line request 579 (2) and (3): a note while the statements are shown, by two written rules: the newest filing
    is more than two years old (a filer that stopped), or the filed history under this SEC number starts within two
    years (a new registrant: a predecessor's filings under another number are not read)."""
    if not q:
        return None
    ix = {c: i for i, c in enumerate(QCOLS)}
    newest, oldest = max(r[ix["period_end"]] for r in q), min(r[ix["period_end"]] for r in q)
    two_years = (dt.date.fromisoformat(built[:10]) - dt.timedelta(days=730)).isoformat()
    if newest < two_years:
        return (f"the newest 10-Q or 10-K on EDGAR is for the period to {newest}: the company has filed neither since "
                "(docs/methods/equities.md)")
    if oldest >= two_years:
        # part F, a reader's case: a subsidiary of a joint filing (Consumers Energy, Pacific Gas and Electric, Entergy
        # Arkansas) has filed its own 10-Qs and 10-Ks for years, yet its own XBRL facts start lately: not a new registrant
        if first_filed and first_filed < two_years:
            return (f"the company has filed 10-Qs and 10-Ks under this SEC number since the period to {first_filed}, but its "
                    f"own XBRL facts start with the period to {oldest}: the earlier statements were filed jointly, tagged "
                    "under the parent's SEC number, which is not read for it (docs/methods/equities.md)")
        if first_filed is None:
            return (f"the filed statements under this SEC number start with the period to {oldest}: a new registrant, or a "
                    "company whose earlier statements were tagged under a parent's SEC number; neither is read "
                    "(docs/methods/equities.md)")
        return (f"the filed history under this SEC number starts with the period to {oldest}: a new registrant, and any "
                "predecessor's filings under another SEC number are not read (docs/methods/equities.md)")
    bad = not_adding_up(q)
    if bad:
        return (f"the filed periods do not add up for the period to {bad}: a year to date less the one before is not the quarter "
                "filed (a change of concept between filings, a restatement inside a filing, or a successor's period); each "
                "row is as filed (docs/methods/equities.md)")
    return None


def months_back(end, m):
    """The month end m months before a period end (YYYY-MM-DD)."""
    import calendar
    y, mo = int(end[:4]), int(end[5:7]) - m
    while mo < 1:
        y, mo = y - 1, mo + 12
    return f"{y:04d}-{mo:02d}-{calendar.monthrange(y, mo)[1]:02d}"


def not_adding_up(q, quarters=4, tol=0.01):
    """Done-line request 581: the newest period end, among the company's newest four quarter ends, where a filed year to
    date less the year to date of the quarter before differs from the quarter filed by more than tol (revenue or net
    income, the later filing where a period was filed twice); None when they agree or cannot be compared."""
    ix = {c: i for i, c in enumerate(QCOLS)}
    best = {}
    for r in q:
        if r[ix["months"]] is None:
            continue
        k = (r[ix["period_end"]], r[ix["months"]])
        if k not in best or later(r, best[k]):
            best[k] = r
    ends = sorted({e for e, m in best if m == 3}, reverse=True)[:quarters]
    for end in ends:
        for m in (6, 9, 12):
            ytd, prev, qtr = best.get((end, m)), best.get((months_back(end, 3), m - 3)), best.get((end, 3))
            if not (ytd and prev and qtr):
                continue
            for col in ("revenue", "net_income"):
                a, b, c = ytd[ix[col]], prev[ix[col]], qtr[ix[col]]
                if a is None or b is None or c is None:
                    continue
                if abs((a - b) - c) > tol * max(abs(c), 1):
                    return end
    return None


def first_filed_periods(ciks, raw=None):
    """{cik: the earliest report date of the company's own 10-Q and 10-K filings marked XBRL}, from the SEC's bulk
    submissions file the connector keeps (warehouse/raw/sec_edgar/submissions_<day>.zip; no request), read by the
    connector's own rule (sec_edgar.own_filings); None when that file is not on this machine."""
    import zipfile
    raw = raw or os.path.join(ROOT, "warehouse", "raw", "sec_edgar")
    zips = sorted(f for f in os.listdir(raw) if f.startswith("submissions_") and f.endswith(".zip")) if os.path.isdir(raw) else []
    if not zips:
        return None
    import sec_edgar
    out = {}
    with zipfile.ZipFile(os.path.join(raw, zips[-1])) as zf:
        for cik in ciks:
            dates = [d for d in sec_edgar.own_filings(cik, zf).values() if d]
            out[cik] = min(dates) if dates else ""
    return out


def company_files(built, universe, fund, first=None):
    """index.json's companies and one series file a company (prices null with their reason, the statements as filed).
    first: {cik: first own 10-Q or 10-K period} (first_filed_periods), for the note of a company whose facts start lately."""
    companies, files = [], {}
    by_cik = {k: g for k, g in fund.groupby("entity")} if fund is not None and len(fund) else {}
    held_cols = {c: PRICE_WHY for c in ("close", "adj_close", "volume", "market_value")}
    for _, r in universe.sort_values("ticker").iterrows():
        tk = r["ticker"].upper()
        q, concepts = quarterly(by_cik.get(r["entity_id"]))
        ff = None if first is None else first.get(r["cik"], "")
        fpath = f"series/{tk}.json"
        companies.append({"id": tk, "cik": r["cik"], "name": r["name"], "ticker": r["ticker"], "exchange": r["exchange"],
                          "sic": r["sic"], "sic_label": r["sic_label"], "segments": r["segments"].split(";"),
                          "segments_note": r["segments_note"] or None, "directory_id": r["directory_id"] or None,
                          "price_status": "license needed", "price_why": PRICE_WHY,
                          "fundamentals_status": "shown" if q else "source needed",
                          "fundamentals_why": shown_why(q, built, ff) if q else FUND_WHY, "newest_filed": newest_filed(q),
                          "first": None, "last": None, "file": fpath})
        files[fpath] = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT, "license": "public",
                        "id": tk, "kind": "company", "name": r["name"], "cik": r["cik"], "ticker": r["ticker"],
                        "exchange": r["exchange"], "segments": r["segments"].split(";"), "status": "license needed",
                        "why": PRICE_WHY, "source": SEC_SOURCE,
                        "units": {"close": "USD/share", "adj_close": "USD/share", "volume": "shares", "market_value": "USD",
                                  "revenue": "USD", "net_income": "USD", "capex": "USD", "debt": "USD",
                                  "shares_outstanding": "shares"},
                        "held": held_cols, "daily_columns": ["day", "close", "adj_close", "volume", "market_value"], "daily": [],
                        "last": None, "last_value_weight": None,
                        "moves": {"d": None, "w": None, "m": None, "ytd": None, "y": None},
                        "quarterly_columns": QCOLS, "quarterly": q, "concepts": concepts,
                        "fundamentals_why": shown_why(q, built, ff) if q else FUND_WHY}
    return companies, files


def build(built):
    tables = ["equity_universe", "equity_prices_daily", "equity_fundamentals_quarterly", "equity_index_daily"]
    universe = table_or_none("equity_universe")
    fund = table_or_none("equity_fundamentals_quarterly")
    first = first_filed_periods(list(universe["cik"])) if universe is not None else None
    companies, cfiles = company_files(built, universe, fund, first) if universe is not None else ([], {})
    n = {i: sum(1 for c in companies if i in c["segments"]) for i, _ in SEGMENTS}
    segs = []
    for i, l in SEGMENTS:
        if universe is None:
            segs.append({"id": i, "label": l, "rule": None, "rule_why": SEC_WHY, "n_companies": None})
        else:
            segs.append({"id": i, "label": l, "rule": SEG_RULE.get(i), "rule_why": NO_CODE.get(i), "n_companies": n[i]})
    index = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT, "license": "public", "tables": tables,
             "last_day": None, "segments": segs, "companies": companies, "indices": [], "segment_series": [],
             "held": {"companies": SEC_WHY if universe is None else None, "indices": PRICE_WHY, "prices": PRICE_WHY}}
    rows = []
    for i, l in SEGMENTS:
        for w, wl in (("equal", "equal weight"), ("value", "weighted by market value")):
            note = f"{SEC_WHY}; and {PRICE_WHY}" if universe is None else (PRICE_WHY if i in SEG_RULE else f"{NO_CODE[i]}; and {PRICE_WHY}")
            rows.append({"id": f"equities-segment-{i}-{w}", "group": "equities", "label": f"{l} ({wl})", "unit": "index, first day = 100",
                         "tags": {"kind": "segment", "weighting": w}, "status": "not_held", "note": note,
                         "file": None})
    board = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT,
             "group": {"id": "equities", "title": "Energy equities",
                       "filters": [{"key": "kind", "label": "Show", "options": [["all", "Segments and indices"], ["segment", "Segments"],
                                                                               ["index", "Indices"]], "default": "all"}]},
             "sources": [], "rows": rows}
    series, daily = energy_series()
    prices = {"built": built, "example": False, "method": METHOD, "contract": CONTRACT, "since": SINCE, "series": series, "daily": daily}
    return {"index.json": index, "board.json": board, "energy_prices.json": prices, **cfiles}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The equities page files (docs/state/page_files_equities.md)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = build(built)
    os.makedirs(a.out, exist_ok=True)
    for name, obj in files.items():
        path = os.path.join(a.out, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(path + ".tmp", path)
    p = files["energy_prices.json"]
    shown = [s for s in p["series"] if s["status"] == "shown"]
    co = files["index.json"]["companies"]
    print(f"equity pages: {len(files['index.json']['segments'])} segments, {len(co)} companies "
          f"({sum(1 for c in co if c['fundamentals_status'] == 'shown')} with statements), 0 indices (held), "
          f"{len(files['board.json']['rows'])} board rows held; energy prices {len(shown)} shown, "
          f"{len(p['series']) - len(shown)} held; built {built}")
    for s in shown:
        print(f"  {s['id']}: {s['first']} to {s['last']}, {len(p['daily'][s['id']])} points, last {s['last_value']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
