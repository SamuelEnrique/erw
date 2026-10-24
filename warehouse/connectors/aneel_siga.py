#!/usr/bin/env python3
"""Brazil's generation plants, operating, under construction and not yet begun, from ANEEL's Sistema de Informacoes de
Geracao (SIGA) on its open data portal (session 2324, chain 108: in place of Ecuador, whose operator CENACE and
regulator ARCERNNR fail TLS certificate verification and whose open data portal refuses the reader).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/aneel_siga_plants.csv, from the SIGA
dataset's monthly CSV (semicolon separated, UTF-8, decimal commas), one request:

    https://dadosabertos.aneel.gov.br/dataset/6d90b77c-c5f5-4d81-bdec-7bc619494bb9/resource/11ec447d-698d-4ab8-977f-b424d5deee6a/download/siga-empreendimentos-geracao.csv

    entity_id    aneel_siga:<CodCEG>, ANEEL's unique code of a generation plant (GGG.FF.UF.999999-D.VV)
    entity_type  plant; name ANEEL's NomEmpreendimento
    geo          BR-<SigUFPrincipal>, the plant's main state; lat, lon ANEEL's approximate centroid, empty where ANEEL
                 gives 0 and 0 (465 plants in October 2026's file: a blank, not a place in Brazil)
    capacity_mw  the granted or registered capacity (MdaPotenciaOutorgadaKw) / 1,000; the capacity in operation
                 (MdaPotenciaFiscalizadaKw) is x_capacity_operating_mw and the physical guarantee x_physical_guarantee_mw
    status       DscFaseUsina: Operacao operating, Construcao under_construction, Construcao nao iniciada planned
                 (ANEEL's phase in x_phase)
    status_date  DatEntradaOperacao, the first unit's entry into operation, where ANEEL gives it
    x_*          ANEEL's other fields, as published (Portuguese)

The dataset is ANEEL's central generation register: it does not hold the distributed micro and mini generation
(MMGD), which ANEEL publishes as another dataset. ANEEL lists three plants twice, once for each of two grant types
with every other field the same; they are one row each, the grant types joined with ";". A header not ANEEL's, a phase
or type not in the map, a number not in ANEEL's form, a plant given twice with other fields differing or a dataset of
two generation dates stops the run.

    python warehouse/connectors/aneel_siga.py [--offline] [--out-dir DIR]

Ceiling: one request, reused from warehouse/raw/aneel_siga/ with --offline. dadosabertos.aneel.gov.br's robots file
disallows /api/, /revision/ and the datasets' history to every agent and asks a crawl delay of 10 seconds; it names no
AI agent (session 2324). License: the dataset's page names the Open Data Commons Open Database License (ODbL): use,
redistribution and adaptation allowed with attribution, a database adapted from it to be offered under the ODbL.
Cite: Agencia Nacional de Energia Eletrica (ANEEL), SIGA.
"""

import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "aneel_siga_plants"
CONNECTOR = "aneel_siga"
SOURCE = "aneel:siga"
PAGE = "https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel"
URL = ("https://dadosabertos.aneel.gov.br/dataset/6d90b77c-c5f5-4d81-bdec-7bc619494bb9/resource/"
       "11ec447d-698d-4ab8-977f-b424d5deee6a/download/siga-empreendimentos-geracao.csv")
HEAD = ["DatGeracaoConjuntoDados", "NomEmpreendimento", "IdeNucleoCEG", "CodCEG", "SigUFPrincipal", "SigTipoGeracao",
        "DscFaseUsina", "DscOrigemCombustivel", "DscFonteCombustivel", "DscTipoOutorga", "NomFonteCombustivel",
        "DatEntradaOperacao", "MdaPotenciaOutorgadaKw", "MdaPotenciaFiscalizadaKw", "MdaGarantiaFisicaKw",
        "IdcGeracaoQualificada", "NumCoordNEmpreendimento", "NumCoordEEmpreendimento", "DatInicioVigencia", "DatFimVigencia",
        "DscPropriRegimePariticipacao", "DscSubBacia", "DscMuninicpios"]
PHASES = {"Operação": "operating", "Construção": "under_construction", "Construção não iniciada": "planned"}
TYPES = {"UTN", "UTE", "UHE", "UFV", "PCH", "EOL", "CGU", "CGH"}
STATES = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
          "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["x_ceg", "x_generation_type", "x_phase", "x_fuel_origin", "x_fuel_source", "x_fuel_name", "x_grant_type",
         "x_capacity_operating_mw", "x_physical_guarantee_mw", "x_qualified_generation", "x_grant_start", "x_grant_end",
         "x_ownership", "x_sub_basin", "x_municipalities", "x_dataset_date"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}


def number(s, what):
    s = (s or "").strip()
    if s == "":
        return None
    if not re.fullmatch(r"-?\d*(,\d+)?", s) or s in ("-", ","):
        raise RuntimeError(f"{what}: a number not in ANEEL's form: {s!r}")
    return float(s.replace(",", "."))


def day(s, what):
    s = (s or "").strip()
    if s == "":
        return ""
    dt.date.fromisoformat(s)
    return s


def file_rows(text, retrieved, vintage):
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    if not rows or [h.strip() for h in rows[0]] != HEAD:
        raise RuntimeError(f"the header is not SIGA's: {rows[0] if rows else None}")
    out = []
    for r in rows[1:]:
        if not r or not "".join(r).strip():
            continue
        if len(r) != len(HEAD):
            raise RuntimeError(f"a row of {len(r)} fields, not {len(HEAD)}: {r[:4]}")
        a = dict(zip(HEAD, (x.strip() for x in r)))
        ceg = a["CodCEG"]
        if a["DscFaseUsina"] not in PHASES:
            raise RuntimeError(f"{ceg}: a phase not in the map: {a['DscFaseUsina']!r}")
        if a["SigTipoGeracao"] not in TYPES:
            raise RuntimeError(f"{ceg}: a generation type not in the map: {a['SigTipoGeracao']!r}")
        if a["SigUFPrincipal"] not in STATES:
            raise RuntimeError(f"{ceg}: a state not in the map: {a['SigUFPrincipal']!r}")
        kw = lambda c: None if number(a[c], f"{ceg} {c}") is None else number(a[c], f"{ceg} {c}") / 1000.0
        lat, lon = number(a["NumCoordNEmpreendimento"], f"{ceg} lat"), number(a["NumCoordEEmpreendimento"], f"{ceg} lon")
        if lat == 0 and lon == 0:   # session 2324: ANEEL's blank, a point in the Gulf of Guinea, not a place in Brazil
            lat = lon = None
        out.append(dict(entity_id=f"aneel_siga:{ceg}", entity_type="plant", name=a["NomEmpreendimento"],
                        geo=f"BR-{a['SigUFPrincipal']}", lat=lat, lon=lon, capacity_mw=kw("MdaPotenciaOutorgadaKw"),
                        status=PHASES[a["DscFaseUsina"]], status_date=day(a["DatEntradaOperacao"], ceg), operator="",
                        source=SOURCE, source_url=URL, retrieved_at=retrieved, vintage=vintage,
                        x_ceg=ceg, x_generation_type=a["SigTipoGeracao"], x_phase=a["DscFaseUsina"],
                        x_fuel_origin=a["DscOrigemCombustivel"], x_fuel_source=a["DscFonteCombustivel"],
                        x_fuel_name=a["NomFonteCombustivel"], x_grant_type=a["DscTipoOutorga"],
                        x_capacity_operating_mw=kw("MdaPotenciaFiscalizadaKw"), x_physical_guarantee_mw=kw("MdaGarantiaFisicaKw"),
                        x_qualified_generation=a["IdcGeracaoQualificada"], x_grant_start=day(a["DatInicioVigencia"], ceg),
                        x_grant_end=day(a["DatFimVigencia"], ceg), x_ownership=a["DscPropriRegimePariticipacao"],
                        x_sub_basin=a["DscSubBacia"], x_municipalities=a["DscMuninicpios"],
                        x_dataset_date=day(a["DatGeracaoConjuntoDados"], ceg)))
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=ENTITY_COLS + EXTRA)
    if t.x_dataset_date.nunique() != 1:
        raise RuntimeError(f"more than one generation date: {sorted(t.x_dataset_date.unique())}")
    keep = []
    for eid, g in t.groupby("entity_id", sort=False):
        if len(g) > 1:
            rest = [c for c in t.columns if c != "x_grant_type"]
            if g[rest].astype(str).nunique().max() > 1:
                raise RuntimeError(f"{eid} given twice with other fields differing")
            row = g.iloc[0].copy()
            row["x_grant_type"] = ";".join(dict.fromkeys(g.x_grant_type))
            keep.append(row)
        else:
            keep.append(g.iloc[0])
    return pd.DataFrame(keep)[ENTITY_COLS + EXTRA].sort_values("entity_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ANEEL SIGA: Brazil's generation plants")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
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
        if not args.offline and (ip.paused("aneel") or ip.paused_host("dadosabertos.aneel.gov.br")):
            raise RuntimeError("ANEEL is paused (warehouse/metadata/paused_sources.csv): not requested")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        raw = file_rows(content.decode("utf-8-sig"), rec.get("retrieved_at") or "", ip.vintage_of(rec))
        t = finish(raw)
        op = t[t.status == "operating"]
        header = [
            f"Energy Research Warehouse (ERW): ANEEL (Agencia Nacional de Energia Eletrica), SIGA, Brazil's generation plants as of {t.x_dataset_date.iloc[0]} (session 2324)",
            "Shape: entities (docs/datastandard.md v0). entity_id aneel_siga:<CodCEG>; entity_type plant; name ANEEL's; geo BR-<main state>; lat, lon ANEEL's approximate centroid; "
            "capacity_mw the granted or registered capacity (kW / 1,000); status operating, under_construction or planned from ANEEL's phase; status_date the first unit's entry into operation; "
            "x_capacity_operating_mw the capacity in operation; x_* ANEEL's other fields (Portuguese, as published).",
            f"{len(t)} plants ({len(raw)} rows of ANEEL's: three plants are listed under two grant types, one row each here); {len(op)} operating with "
            f"{op.x_capacity_operating_mw.sum():,.0f} MW in operation; {int(t.lat.isna().sum())} plants without coordinates (ANEEL's 0 and 0). Central generation only: the distributed micro and mini generation is another ANEEL dataset. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/aneel_siga.py; the file retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Agencia Nacional de Energia Eletrica (ANEEL), SIGA - Sistema de Informacoes de Geracao da ANEEL (open data portal), {PAGE}",
            f"  access: {URL}",
            "License: public, the Open Data Commons Open Database License (ODbL) named on the dataset's page: attribution, and a database adapted from it offered under the ODbL. Cite: ANEEL, SIGA.",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Agencia Nacional de Energia Eletrica (ANEEL)",
                                    report="SIGA - Sistema de Informacoes de Geracao da ANEEL (generation plants, open data portal, monthly CSV)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} plants"))
        print(f"{NAME}: {len(t)} plants")
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
