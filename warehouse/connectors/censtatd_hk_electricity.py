#!/usr/bin/env python3
"""Hong Kong's electricity: local consumption by type of user a month, and generation, imports, exports, industry own
use and losses a quarter, from the Census and Statistics Department's Hong Kong Energy Statistics (session
2323, chain 108: in place of Thailand, whose sources the ERW cannot use: EPPO's website policy forbids distributing its
content and scripted access, data.go.th refuses the reader, EGAT publishes graphs only).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/censtatd_hk_electricity.csv, from C&SD's
web table API, listed on DATA.GOV.HK, one request a table:

    https://www.censtatd.gov.hk/api/get.php?id=915-91201&lang=en&full_series=1
        Monthly statistics on consumption of electricity and gas by type of users (the months only; the years are
        their sums, and town gas is not taken)
    https://www.censtatd.gov.hk/api/get.php?id=915-91203&lang=en&full_series=1
        Electricity production, imports, exports, and consumption (the quarters only; the years are their sums)

    entity    censtatd:915-91201 or censtatd:915-91203, the table
    variable  91201: consumption_total, consumption_domestic, consumption_commercial, consumption_industrial,
              consumption_street_lighting, exports_mainland
              91203: local_consumption, local_generation, imports_mainland, exports_mainland,
              industry_own_use_and_losses (a quarter)
    unit      MWh: C&SD's terajoules times 1,000,000 / 3,600 (1 TJ = 277.78 MWh, an exact factor)
    ts_utc    the period's first day at 00:00:00Z (a quarter's period is its last month, YYYYMM); freq P1M or P3M;
              geo HK; node Hong Kong

Local consumption excludes industry own use and losses (the power companies' own use and transformation and
distribution losses) and the exports to the Chinese Mainland (C&SD's notes). The months come from CLP Power and HK
Electric. C&SD notes that some March 2023 consumption is in April 2023 (delayed billing); it is kept as published. A
cell C&SD marks "-" (not applicable: the exports before they began) has no row; nothing is filled. A status not
success, a series or user type not in the map, a unit not terajoules, a period not of its frequency's form, a value
that is not a number or a key given twice stops the run.

    python warehouse/connectors/censtatd_hk_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests, reused from warehouse/raw/censtatd_hk_electricity/ with --offline. www.censtatd.gov.hk's robots
file allows every path to every agent and names ClaudeBot, anthropic-ai and Claude-Web to allow them (session 2323).
License: DATA.GOV.HK's terms of use: "You are allowed to browse, download, distribute, reproduce, hyperlink to, and
print the Data for both commercial and non-commercial purposes on a free-of-charge basis", on condition that the
source is identified, the Government's ownership acknowledged and DATA.GOV.HK attributed. Cite: Census and Statistics
Department, Hong Kong Energy Statistics (DATA.GOV.HK).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "censtatd_hk_electricity"
CONNECTOR = "censtatd_hk_electricity"
SOURCE = "censtatd:hong_kong_energy_statistics"
PAGE = "https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-915-91201"
URL = "https://www.censtatd.gov.hk/api/get.php?id={t}&lang=en&full_series=1"
TABLES = ("915-91201", "915-91203")
MONTHLY = {("ELEC_LOCAL", ""): "consumption_total", ("ELEC_LOCAL", "1"): "consumption_domestic",
           ("ELEC_LOCAL", "2"): "consumption_commercial", ("ELEC_LOCAL", "3"): "consumption_industrial",
           ("ELEC_LOCAL", "4"): "consumption_street_lighting", ("ELE_EX_CHN", None): "exports_mainland"}
SKIPPED = {"GASC_LOCAL"}   # town gas, not electricity
QUARTERLY = {"ELEC_LOCAL": "local_consumption", "ELE_GEN_LOCAL": "local_generation", "ELE_IM_CHN": "imports_mainland",
          "ELE_EX_CHN": "exports_mainland", "ELE_IND_OWN": "industry_own_use_and_losses"}
TJ_TO_MWH = 1e6 / 3600.0
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage"]


def period_start(freq, period):
    if freq == "Y" and re.fullmatch(r"\d{4}", period):
        return f"{period}-01-01T00:00:00Z", "P1Y"
    if freq in ("M", "Q") and re.fullmatch(r"\d{6}", period):
        y, m = int(period[:4]), int(period[4:])
        if freq == "Q":
            if m not in (3, 6, 9, 12):
                raise RuntimeError(f"a quarter not ending in March, June, September or December: {period}")
            m -= 2
        if not 1 <= m <= 12:
            raise RuntimeError(f"a month out of range: {period}")
        return f"{y}-{m:02d}-01T00:00:00Z", "P1M" if freq == "M" else "P3M"
    raise RuntimeError(f"a period not of its frequency's form: {freq} {period!r}")


def table_rows(table, text, url, retrieved, vintage):
    j = json.loads(text)
    status = (j.get("header") or {}).get("status") or {}
    if status.get("code") != 0:
        raise RuntimeError(f"{url}: C&SD's status is not success: {status}")
    out = []
    for r in j["dataSet"]:
        sv, freq = r.get("sv"), r.get("freq")
        if table == "915-91201":
            if sv in SKIPPED or freq == "Y":
                continue
            user = r.get("USER_TYPE")
            key = (sv, None if sv == "ELE_EX_CHN" else ("" if user is None else str(user)))
            if key not in MONTHLY:
                raise RuntimeError(f"{url}: a series or user type not in the map: {sv} {user!r}")
            var = MONTHLY[key]
        else:
            if freq == "Y":
                continue
            if sv not in QUARTERLY:
                raise RuntimeError(f"{url}: a series not in the map: {sv!r}")
            var = QUARTERLY[sv]
        if r.get("svDesc") != "Terajoule":
            raise RuntimeError(f"{url}: {sv}: a unit not terajoules: {r.get('svDesc')!r}")
        ts, f = period_start(freq, str(r.get("period")))
        if r.get("sd_value") == "-":
            continue
        try:
            value = float(r.get("figure")) * TJ_TO_MWH
        except (TypeError, ValueError):
            raise RuntimeError(f"{url}: {sv} {r.get('period')}: not a number: {r.get('figure')!r}")
        out.append({"entity": f"censtatd:{table}", "variable": var, "ts_utc": ts, "value": value, "unit": "MWh", "freq": f,
                    "geo": "HK", "market": "", "node": "Hong Kong", "source": SOURCE, "source_url": url,
                    "retrieved_at": retrieved, "vintage": vintage})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc", "freq"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) given at two frequencies")
    return t.sort_values(["entity", "variable", "freq", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="C&SD: Hong Kong's electricity consumption, generation, imports and exports")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        if not args.offline and (ip.paused("censtatd") or ip.paused_host("www.censtatd.gov.hk")):
            raise RuntimeError("C&SD is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for table in TABLES:
            url = URL.format(t=table)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
            rows += table_rows(table, content.decode("utf-8-sig"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((table, rec.get("retrieved_at") or ""))
        t = finish(rows)
        m = t[t.freq == "P1M"]
        header = [
            f"Energy Research Warehouse (ERW): Census and Statistics Department (C&SD), Hong Kong Energy Statistics, electricity: consumption by type of user a month {m.ts_utc.min()[:7]} to {m.ts_utc.max()[:7]}; "
            f"generation, imports, exports, own use and losses a quarter (session 2323)",
            "Shape: series (docs/datastandard.md v0). entity censtatd:915-91201 (consumption_total, consumption_domestic, consumption_commercial, consumption_industrial, consumption_street_lighting, exports_mainland; a month) "
            "or censtatd:915-91203 (local_consumption, local_generation, imports_mainland, exports_mainland, industry_own_use_and_losses; a quarter); unit MWh (C&SD's terajoules times 1,000,000/3,600); "
            "ts_utc the period's first day; freq P1M or P3M; geo HK. The years C&SD gives are the sums of these and are not taken. Local consumption excludes the power companies' own use, losses and the exports to the Chinese Mainland.",
            f"{len(t)} rows, {t.variable.nunique()} variables. A cell C&SD marks not applicable has no row; nothing is filled. Some March 2023 consumption is in April 2023 (C&SD: delayed billing).",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/censtatd_hk_electricity.py; the tables retrieved " + "; ".join(f"{k} {r}" for k, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Census and Statistics Department, Hong Kong Energy Statistics, tables 915-91201 and 915-91203 (figures from CLP Power and HK Electric), listed on DATA.GOV.HK, {PAGE}",
            f"  access: {URL.format(t='915-91201')} and {URL.format(t='915-91203')}",
            "License: public, DATA.GOV.HK's terms of use (commercial and non-commercial use free of charge, with the source identified and attributed). Cite: Census and Statistics Department, Hong Kong Energy Statistics (DATA.GOV.HK).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Census and Statistics Department, Hong Kong (C&SD)",
                                    report="Hong Kong Energy Statistics, tables 915-91201 (monthly consumption of electricity by type of user) and 915-91203 (electricity production, imports, exports and consumption)",
                                    report_url=PAGE, document_list=" ".join(URL.format(t=x) for x in TABLES),
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
