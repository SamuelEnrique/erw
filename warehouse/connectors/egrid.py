#!/usr/bin/env python3
"""EPA eGRID: every US power plant's capacity, generation, emissions and emission rates, a data year (session 486, the
owner's instruction of 21 October 2026).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/egrid_power_plants.csv, from the U.S.
Environmental Protection Agency's Emissions & Generation Resource Integrated Database (eGRID), the plant sheet
(PLNT<yy>) of its newest workbook:

    page   https://www.epa.gov/egrid/download-data
    file   the newest egrid<year>_data*.xlsx the page links (not the _metric workbook: the same data in metric units)

    entity_id   egrid:<ORISPL>, the plant's DOE/EIA ORIS code (eia860.py's plants are eia860:<plant id>: the same number)
    entity_type plant; name PNAME; geo US-<state>; lat, lon LAT, LON; capacity_mw NAMEPCAP (nameplate, MW)
    status      empty: eGRID lists the plants of its data year and gives no status
    operator    the utility's name (UTLSRVNM)
    the rest    eGRID's own fields, each named for what it is with its unit, and eGRID's code in the column list below

eGRID's figures are EPA's: its emissions are measured (EPA's Clean Air Markets data) or estimated by EPA from fuel use and
emission factors, as eGRID's documentation says for each plant (the *_src fields are not taken); they are EPA's
published values, not filled by the ERW. A cell eGRID leaves blank is empty here. A plant code repeated stops the run.

    python warehouse/connectors/egrid.py

Ceiling: two requests (the page and the workbook; a workbook already in warehouse/raw/egrid/ is reused). License:
public (EPA: "Unless otherwise specified, ... data produced by the EPA is by default in the public domain", read in
session 311, record 55 of license_reads.csv; cite "U.S. EPA, eGRID<year>").
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "egrid_power_plants"
CONNECTOR = "egrid"
SOURCE = "epa:egrid"
PAGE = "https://www.epa.gov/egrid/download-data"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"]
# eGRID's code -> the ERW's column (units as eGRID's documentation gives them)
FIELDS = {
    "YEAR": "data_year", "ORISPL": "plant_id", "PSTATABB": "state", "CNTYNAME": "county", "FIPSST": "fips_state",
    "FIPSCNTY": "fips_county", "OPRNAME": "transmission_owner", "UTLSRVID": "utility_id", "SECTOR": "sector",
    "BACODE": "balancing_authority", "BANAME": "balancing_authority_name", "NERC": "nerc_region", "SUBRGN": "egrid_subregion",
    "ISORTO": "iso_rto", "NUMUNT": "units", "NUMGEN": "generators", "PLPRMFL": "primary_fuel", "PLFUELCT": "primary_fuel_category",
    "COALFLAG": "coal_flag", "CHPFLAG": "chp_flag", "CAPFAC": "capacity_factor", "PLHTIAN": "heat_input_mmbtu",
    "PLNGENAN": "net_generation_mwh", "PLNOXAN": "nox_tons", "PLSO2AN": "so2_tons", "PLCO2AN": "co2_tons",
    "PLCH4AN": "ch4_lbs", "PLN2OAN": "n2o_lbs", "PLCO2EQA": "co2e_tons", "PLHGAN": "hg_lbs",
    "PLNOXRTA": "nox_rate_lb_mwh", "PLSO2RTA": "so2_rate_lb_mwh", "PLCO2RTA": "co2_rate_lb_mwh", "PLC2ERTA": "co2e_rate_lb_mwh",
    "PLHTRT": "heat_rate_btu_kwh",
    "PLGENACL": "gen_coal_mwh", "PLGENAOL": "gen_oil_mwh", "PLGENAGS": "gen_gas_mwh", "PLGENANC": "gen_nuclear_mwh",
    "PLGENAHY": "gen_hydro_mwh", "PLGENABM": "gen_biomass_mwh", "PLGENAWI": "gen_wind_mwh", "PLGENASO": "gen_solar_mwh",
    "PLGENAGT": "gen_geothermal_mwh", "PLGENAOF": "gen_other_fossil_mwh", "PLGENAOP": "gen_other_purchased_mwh",
}
EXTRA_COLS = list(FIELDS.values())


def workbook_url(page_html):
    """The newest eGRID data workbook the page links, in short tons (not the _metric one), and its year."""
    links = set(re.findall(r'href="([^"]*egrid(\d{4})_data[^"]*\.xlsx)"', page_html, re.I))
    links = [(u, int(y)) for u, y in links if "metric" not in u.lower()]
    if not links:
        raise RuntimeError("the eGRID page links no egrid<year>_data workbook")
    year = max(y for _, y in links)
    pick = sorted(u for u, y in links if y == year)
    return (pick[-1] if pick[-1].startswith("http") else "https://www.epa.gov" + pick[-1]), year


def plants(frame, year, url, retrieved):
    """eGRID's plant sheet (its first row the long names, its second eGRID's codes) as the table's rows."""
    codes = [str(c) for c in frame.iloc[1].tolist()]
    d = frame.iloc[2:].copy()
    d.columns = codes
    missing = [c for c in ["ORISPL", "PNAME", "LAT", "LON", "NAMEPCAP", "UTLSRVNM"] + list(FIELDS) if c not in d.columns]
    if missing:
        raise RuntimeError(f"eGRID{year}'s plant sheet lacks {missing}")
    d = d[pd.to_numeric(d["ORISPL"], errors="coerce").notna()]
    oris = pd.to_numeric(d["ORISPL"]).astype(int)
    if oris.duplicated().any():
        raise RuntimeError(f"eGRID{year}: a plant code given twice: {sorted(oris[oris.duplicated()].unique())[:5]}")

    def text(c):
        return d[c].where(d[c].notna(), "").astype(str).str.strip()

    out = pd.DataFrame({
        "entity_id": "egrid:" + oris.astype(str), "entity_type": "plant", "name": text("PNAME"), "geo": "US-" + text("PSTATABB"),
        "lat": pd.to_numeric(d["LAT"], errors="coerce"), "lon": pd.to_numeric(d["LON"], errors="coerce"),
        "capacity_mw": pd.to_numeric(d["NAMEPCAP"], errors="coerce"), "status": "", "status_date": "",
        "operator": text("UTLSRVNM"), "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": f"eGRID{year}",
    })
    for code, col in FIELDS.items():
        out[col] = text(code) if d[code].dtype == object else d[code]
    out["plant_id"] = oris.astype(str)
    out["fips_state"] = text("FIPSST").str.zfill(2).where(text("FIPSST") != "", "")
    out["fips_county"] = text("FIPSCNTY").str.replace(r"\.0$", "", regex=True).str.zfill(3).where(text("FIPSCNTY") != "", "")
    return out.sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EPA eGRID: every US power plant, a data year")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, fresh=True, headers=UA)
        url, year = workbook_url(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, headers=UA, timeout=600)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a workbook (it starts {content[:20]!r})")
        sheet = f"PLNT{year % 100:02d}"
        t = plants(pd.read_excel(io.BytesIO(content), sheet, header=None), year, url, rec["retrieved_at"])
        header = [
            f"Energy Research Warehouse (ERW): EPA eGRID{year}, every US power plant's capacity, generation, emissions and emission rates (session 486)",
            "Shape: entities (docs/datastandard.md v0). entity_id egrid:<ORISPL> (the DOE/EIA plant code); entity_type plant; capacity_mw the nameplate capacity; status empty (eGRID gives none); operator the utility.",
            "Fields and eGRID's codes: " + "; ".join(f"{v} {k}" for k, v in FIELDS.items()) + ". Units as eGRID gives them: tons are short tons; rates lb/MWh; heat input MMBtu; heat rate Btu/kWh.",
            f"Plants: {len(t):,}; nameplate {t['capacity_mw'].sum():,.0f} MW; net generation {pd.to_numeric(t['net_generation_mwh'], errors='coerce').sum() / 1e6:,.1f} TWh. A blank cell in eGRID is empty here; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/egrid.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Environmental Protection Agency, Emissions & Generation Resource Integrated Database (eGRID{year}), plant sheet {sheet}, {PAGE}",
            f"  access: {url}",
            f'License: public (a work of the U.S. government; cite "U.S. EPA, eGRID{year}").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Environmental Protection Agency (EPA)",
                                    report="Emissions & Generation Resource Integrated Database (eGRID)", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"eGRID{year}: {len(t):,} plants"))
        print(f"{NAME}: eGRID{year}, {len(t):,} plants, {t['capacity_mw'].sum():,.0f} MW")
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
