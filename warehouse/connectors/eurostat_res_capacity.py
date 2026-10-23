#!/usr/bin/env python3
"""Eurostat's electricity production capacities for renewables and wastes (nrg_inf_epcrw): each European country's net
maximum capacity by fuel or technology, a year from 1990 (session 2123, chain 079: Europe's renewable capacity beside the
United States', in place of IRENA's statistics, which chain 068 took first).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eurostat_renewable_capacity_annual.csv,
from Eurostat's SDMX 2.1 dissemination API (no key): the data set as SDMX-CSV, and the SIEC codelist for the names of
the fuels and technologies:

    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epcrw?format=SDMX-CSV&compressed=false
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC

    entity      eurostat_epcrw:<Eurostat geo code>:<SIEC code> (R5100 solid biofuels, RA100 hydro, RA300 wind, RA410 solar
                thermal, RA420 solar photovoltaic and its size classes, W6000 wastes and the rest, as node names them)
    variable    net_capacity (CAP_NET_ELC), net_capacity_ac and net_capacity_dc (solar photovoltaic's alternating and
                direct current ratings, where the country reports them)
    unit        MW; ts_utc the year's 1 January; freq P1Y
    geo         the country's ISO 3166-1 alpha-2 code (Eurostat's EL is GR); blank for Eurostat's aggregates EU27_2020 and
                EA21, which are Eurostat's own totals, never a sum made here
    node        the SIEC code's English name
    x_*         Eurostat's geo code, SIEC code and plant technology code, the observation's flag and confidentiality status

Countries kept: the European Union's member states, EFTA's (Iceland, Liechtenstein, Norway) and the official candidate
countries (Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkey, Ukraine), with
the two EU aggregates. Eurostat's copyright notice allows reuse with acknowledgement, but data for other countries "may not
be reused for commercial purposes", so the United Kingdom and Kosovo (a potential candidate, not an official one) are left
out. Values as published, zeros kept; a blank value has no row; nothing is filled. A header not Eurostat's, a unit not
MW, a frequency not annual, a value that is not a number or a key given twice stops the run.

    python warehouse/connectors/eurostat_res_capacity.py [--offline] [--out-dir DIR]

Ceiling: two requests (the data and the codelist), reused from warehouse/raw/eurostat_res_capacity/ with --offline.
ec.europa.eu's robots file disallows the old /eurostat/SDMX/diss-web/rest/ and the search pages, not
/eurostat/api/dissemination/ (session 2123). License: Eurostat's copyright notice (session 2123): reuse of its statistical
data "for commercial or non-commercial purposes is authorised provided the source is acknowledged" (the Commission's
Decision of 12 December 2011); source: Eurostat.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback
import xml.etree.ElementTree as ET

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eurostat_renewable_capacity_annual"
CONNECTOR = "eurostat_res_capacity"
SOURCE = "eurostat:nrg_inf_epcrw"
PAGE = "https://ec.europa.eu/eurostat/databrowser/view/nrg_inf_epcrw/default/table"
URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_inf_epcrw?format=SDMX-CSV&compressed=false"
CODELIST = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC"
TERMS = "https://ec.europa.eu/eurostat/web/main/help/copyright-notice"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
HEADER = ["DATAFLOW", "LAST UPDATE", "freq", "siec", "plant_tec", "unit", "geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG",
          "CONF_STATUS"]
EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
      "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}
EFTA = {"CH", "IS", "LI", "NO"}
CANDIDATES = {"AL", "BA", "GE", "MD", "ME", "MK", "RS", "TR", "UA"}
AGGREGATES = {"EU27_2020", "EA21", "EA20", "EA19"}
KEPT = EU | EFTA | CANDIDATES | AGGREGATES
ISO = {"EL": "GR"}
VARIABLES = {"CAP_NET_ELC": "net_capacity", "CAP_NET_ELC_AC": "net_capacity_ac", "CAP_NET_ELC_DC": "net_capacity_dc"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_geo_code", "x_siec", "x_plant_tec", "x_flag", "x_conf_status"]


def names(xml_bytes):
    """The SIEC codelist's English names, {code: name}."""
    root = ET.fromstring(xml_bytes)
    out = {}
    for el in root.iter():
        if el.tag.endswith("}Code"):
            for n in el:
                if n.tag.endswith("}Name") and n.get("{http://www.w3.org/XML/1998/namespace}lang") == "en":
                    out[el.get("id")] = re.sub(r"\s+", " ", n.text or "").strip()
    if not out:
        raise RuntimeError("the SIEC codelist holds no English names")
    return out


def build(csv_text, siec_names, url, retrieved, vintage):
    t = pd.read_csv(io.StringIO(csv_text), dtype=str, keep_default_na=False)
    if list(t.columns) != HEADER:
        raise RuntimeError(f"the header is not Eurostat's SDMX-CSV: {list(t.columns)}")
    bad = sorted(set(t.unit) - {"MW"}) + sorted(set(t.freq) - {"A"}) + sorted(set(t.plant_tec) - set(VARIABLES))
    if bad:
        raise RuntimeError(f"a unit, frequency or plant technology not expected: {bad}")
    left = sorted(set(t.geo) - KEPT)
    t = t[t.geo.isin(KEPT)]
    rows = []
    for r in t.to_dict("records"):
        v = r["OBS_VALUE"].strip()
        if v == "":
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{r['geo']} {r['siec']} {r['TIME_PERIOD']}: not a number: {v!r}")
        if not re.fullmatch(r"\d{4}", r["TIME_PERIOD"]):
            raise RuntimeError(f"a period not a year: {r['TIME_PERIOD']!r}")
        geo = r["geo"]
        rows.append({"entity": f"eurostat_epcrw:{geo}:{r['siec']}", "variable": VARIABLES[r["plant_tec"]],
                     "ts_utc": f"{r['TIME_PERIOD']}-01-01T00:00:00Z", "value": value, "unit": "MW", "freq": "P1Y",
                     "geo": "" if geo in AGGREGATES else ISO.get(geo, geo), "market": "",
                     "node": siec_names.get(r["siec"], r["siec"]), "source": SOURCE, "source_url": url,
                     "retrieved_at": retrieved, "vintage": vintage, "x_geo_code": geo, "x_siec": r["siec"],
                     "x_plant_tec": r["plant_tec"], "x_flag": r["OBS_FLAG"].strip(), "x_conf_status": r["CONF_STATUS"].strip()})
    out = pd.DataFrame(rows, columns=COLS)
    twice = out[out.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return out.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True), left


def main(argv=None):
    ap = argparse.ArgumentParser(description="Eurostat nrg_inf_epcrw: renewable and waste capacity by European country")
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
        if not args.offline and (ip.paused("eurostat") or ip.paused_host("ec.europa.eu")):
            raise RuntimeError("Eurostat is paused (warehouse/metadata/paused_sources.csv): not requested")
        codes, _ = ip.fetch_raw(CONNECTOR, CODELIST, log, offline=args.offline, headers=UA, timeout=120)
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, headers=UA, timeout=300)
        text = content.decode("utf-8", errors="replace")
        updated = sorted(set(re.findall(r"^[^,]*,([^,]*),", text, re.M)) - {"LAST UPDATE"})
        t, left = build(text, names(codes), URL, rec.get("retrieved_at") or "", ip.vintage_of(rec))
        countries = sorted(set(t.x_geo_code) - AGGREGATES)
        header = [
            f"Energy Research Warehouse (ERW): Eurostat, electricity production capacities for renewables and wastes (nrg_inf_epcrw), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]}, {len(countries)} European countries and the EU aggregates (session 2123)",
            "Shape: series (docs/datastandard.md v0). entity eurostat_epcrw:<Eurostat geo code>:<SIEC code>; variable net_capacity, or net_capacity_ac and net_capacity_dc for solar photovoltaic's "
            "two ratings; unit MW; ts_utc the year's 1 January; freq P1Y; geo ISO alpha-2 (Eurostat's EL is GR), blank for Eurostat's own aggregates EU27_2020 and EA21; node the SIEC code's English name.",
            f"{len(t)} rows. Countries: {' '.join(countries)}. Left out by Eurostat's terms (data for countries outside the EU, EFTA and the official candidates may not be reused commercially): "
            f"{' '.join(left) or 'none'}. Values as published, zeros kept; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eurostat_res_capacity.py; the data retrieved {rec.get('retrieved_at') or ''}; Eurostat's last update {', '.join(updated)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Eurostat, Electricity production capacities for renewables and wastes (nrg_inf_epcrw), {PAGE}",
            f"  access: {URL}",
            f"  names: {CODELIST}",
            f"License: public with acknowledgement (Eurostat's copyright notice, {TERMS}). Cite: Eurostat, nrg_inf_epcrw. Eurostat bears no responsibility for this reshaping (the rows filtered by country and renamed, the values unchanged).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Eurostat (Statistical Office of the European Union)",
                                    report="Electricity production capacities for renewables and wastes (nrg_inf_epcrw)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {len(countries)} countries; left out {left}")
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
