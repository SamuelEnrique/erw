#!/usr/bin/env python3
"""Serbia's balance of electricity, a year: primary production by renewable source, imports, exports, production by
plant type, own use by branch, losses and final consumption by sector, as the Statistical Office of the Republic of
Serbia (SORS) gives them in table 1, "Balance of Electricity", of its bulletin "Energy Balances, 2024" (final data,
February 2026) (session 2525, chain 123: a source of the session's own choosing; the ERW held Serbia only in Eurostat's
and EIA's international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/sors_serbia_electricity_annual.csv, from one
PDF (no key):

    https://publikacije.stat.gov.rs/G2026/pdf/G20265730.pdf

The table's GWh page (page 20) is read line by line: a row's Serbian label, then four cells (solar photovoltaic, wind,
hydro, electricity total), "-" for none and a decimal comma. The section rows (primary production, the input to
transformation, production by transformation, own use in the energy sector, final consumption for energy purposes)
set the variable of the plant or branch rows under them.

    entity      sors:rs:<item>: total; a plant type (hydro, wind, solar, thermal, chp, autoproducers, pumped_storage);
                an energy-sector branch (district_heating, oil_gas_extraction, refineries, coal_mines, coal_processing,
                other); a final sector (industry, construction, transport, households, agriculture, other_consumers)
    variable    primary_production (by source, from the first three columns); imports, exports, gross_available,
                transformation_input, gross_production, own_use, losses, available_final, final_consumption
                (from the electricity column)
    unit        MWh (SORS's GWh times 1,000); ts_utc 2024-01-01; freq P1Y; geo RS
    node        the row's Serbian label

A row of a label not in the map stops the run, as does a page without the table, a row of another width, a figure of
another form, or a key given twice. Rows of only "-" are not written. Nothing is filled. The TJ and Mtoe pages, and the
other energy products' tables, are not taken.

    python warehouse/connectors/sors_serbia_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/sors_energy_balances/ and reused unless --fresh; --offline asks
nothing. publikacije.stat.gov.rs has no robots file (session 2525). License: public. SORS's copyright page: "Files and
statistical data from this website may be downloaded, reproduced, distributed, shared, and used for commercial and
non-commercial purposes (unless otherwise indicated), provided that any changes to the data are clearly indicated and
the Statistical Office of the Republic of Serbia (SORS) is cited as the source of the original data."
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "sors_serbia_electricity_annual"
CONNECTOR = "sors_energy_balances"
SOURCE = "sors:energy_balances_2024"
HOST = "publikacije.stat.gov.rs"
URL = "https://publikacije.stat.gov.rs/G2026/pdf/G20265730.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEAR = "2024"
TITLE = "Биланс електричне енергије, 2024."
CITATION = "Statistical Office of the Republic of Serbia (SORS), Energy Balances, 2024 (final data), table 1, Balance of Electricity in 2024"
# a section row: (variable, item); the rows under it (until the next section row) take its variable
SECTIONS = {"Утрошак за производњу енергије": ("transformation_input", "total"),
            "Производња енергије трансформацијом": ("gross_production", "total"),
            "Сопствена потрошња у енергетском сектору": ("own_use", "total"),
            "Финална потрошња за енергетске сврхе": ("final_consumption", "total")}
SINGLE = {"Увоз": ("imports", "total"), "Извоз": ("exports", "total"), "Укупно расположива енергија": ("gross_available", "total"),
          "Губици": ("losses", "total"), "Енергија расположива за финалну потрошњу": ("available_final", "total")}
ITEMS = {"Хидроелектране": "hydro", "Ветроелектране": "wind", "Соларне електране": "solar", "Термоелектране": "thermal",
         "Термоелектране-топлане (ТЕ-ТО)": "chp", "Енергане": "autoproducers", "Пумпање-реверзибилне хидроелектране": "pumped_storage",
         "Топлане": "district_heating", "Екстракција нафте и гаса": "oil_gas_extraction", "Рафинерије": "refineries",
         "Рудници угља": "coal_mines", "Прерада угља": "coal_processing", "Остали": "other",
         "Индустрија": "industry", "Грађевинарство": "construction", "Саобраћај": "transport", "Домаћинства": "households",
         "Пољопривреда": "agriculture", "Остали потрошачи": "other_consumers"}
# rows of the balance the table always prints and this table does not take (all "-" for electricity, or not a flow of it)
SKIP = {"Салдо залиха", "Складишта за међународни бродски саобраћај", "Укупна домаћа потрошња", "Међународни авио превоз",
        "Укупно снабдевање енергијом", "Петрохемија", "За намешавање са фосилним бензином, дизелом, керозином", "Размењени производи",
        "Интерна размена производа", "Враћено из петрохемије", "Висока пећ", "Ћумуране и реторте", "Произвођачи дрвних пелета",
        "Произвођачи дрвних брикета", "Финална потрошња за неенергетске сврхе", "од тога за хемијску индустрију", "Статистичка разлика"}
PRIMARY = "Примарна производња енергије"
SOURCES = ["solar", "wind", "hydro"]
X_COLS = ["x_label"]


def norm(label):
    """The label as the map holds it: footnote marks dropped, the Latin E some rows begin with read as Cyrillic."""
    label = re.sub(r"\d\)$", "", label.strip()).strip()
    return ("Е" + label[1:]) if label.startswith("E") else label


def num(cell):
    if cell == "-":
        return None
    if not re.fullmatch(r"\d+(,\d+)?", cell):
        raise RuntimeError(f"not a figure: {cell!r}")
    return float(cell.replace(",", "."))


def parse_text(text, base):
    if TITLE not in text or "GWh" not in text:
        raise RuntimeError("the GWh page of table 1 not found")
    rows, seen, section = [], set(), None

    def add(item, var, gwh, label):
        key = (item, var)
        if key in seen:
            raise RuntimeError(f"{key} given twice")
        seen.add(key)
        rows.append(dict(entity=f"sors:rs:{item}", variable=var, ts_utc=f"{YEAR}-01-01T00:00:00Z", value=round(gwh * 1000, 3), unit="MWh",
                         freq="P1Y", geo="RS", market="", node=label, **base, x_label=label))

    started = False
    for ln in text[text.index(TITLE):].splitlines():
        m = re.match(r"^(.*?)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$", ln.strip())
        if not m or not re.fullmatch(r"-|\d+(,\d+)?", m.group(5)):
            if started and ln.startswith("1)"):
                break
            continue
        label = norm(m.group(1))
        cells = [m.group(i) for i in range(2, 6)]
        if label == PRIMARY:
            started = True
            for src, c in zip(SOURCES, cells[:3]):
                v = num(c)
                if v is not None:
                    add(src, "primary_production", v, f"{label} ({src})")
            continue
        if not started:
            continue
        elec = num(cells[3])
        if label in SECTIONS:
            section = SECTIONS[label][0]
            if elec is not None:
                add(SECTIONS[label][1], section, elec, label)
        elif label in SINGLE:
            section = None
            if elec is not None:
                add(SINGLE[label][1], SINGLE[label][0], elec, label)
        elif label in ITEMS:
            if section is None:
                raise RuntimeError(f"a row before its section: {label!r}")
            if elec is not None:
                add(ITEMS[label], section, elec, label)
        elif label in SKIP:
            if elec is not None and label not in ("Укупна домаћа потрошња", "Укупно снабдевање енергијом"):
                raise RuntimeError(f"a row this table does not take holds a figure: {label!r} {cells[3]}")
        else:
            raise RuntimeError(f"a row not in the map: {label!r}")
    t = pd.DataFrame(rows)
    if t.empty or not (t.variable == "final_consumption").any():
        raise RuntimeError("no final consumption in the table")
    return t


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [pg.extract_text() or "" for pg in pdf.pages]
    found = [p for p in pages if TITLE in p and "GWh" in p and "Губици" in p]
    if len(found) != 1:
        raise RuntimeError(f"the GWh page of table 1 found {len(found)} times")
    return parse_text(found[0], base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SORS: Serbia's balance of electricity, 2024")
    ap.add_argument("--offline", action="store_true", help="the saved bulletin only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the bulletin again")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity"]).reset_index(drop=True)
        v = {(e, x): y for e, x, y in zip(t.entity, t.variable, t.value)}
        head = [
            "Energy Research Warehouse (ERW): Statistical Office of the Republic of Serbia (SORS), Energy Balances, 2024 (final data), table 1, "
            "Serbia's balance of electricity in 2024 (session 2525)",
            "Shape: series (docs/datastandard.md v0). entity sors:rs:<item> (total, a plant type, an energy-sector branch, a final sector, a renewable "
            "source); variable primary_production, imports, exports, gross_available, transformation_input, gross_production, own_use, losses, "
            "available_final, final_consumption; unit MWh (SORS's GWh times 1,000); ts_utc 2024-01-01; freq P1Y; geo RS; node SORS's Serbian label.",
            f"{len(t)} rows; gross production {v[('sors:rs:total', 'gross_production')] / 1e6:.2f} TWh, final consumption "
            f"{v[('sors:rs:total', 'final_consumption')] / 1e6:.2f} TWh, imports {v[('sors:rs:total', 'imports')] / 1e6:.2f} and exports "
            f"{v[('sors:rs:total', 'exports')] / 1e6:.2f} TWh. Rows of only - are not written; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/sors_serbia_electricity.py; the bulletin retrieved {base['retrieved_at']}; last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: public. SORS's copyright page: files and statistical data may be downloaded, reproduced, distributed, shared and used for "
            "commercial and non-commercial purposes, with any change indicated and SORS cited as the source of the original data. The figures here "
            f"are SORS's, scaled from GWh to MWh. Cite: {CITATION}.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistical Office of the Republic of Serbia (SORS)",
                                    report="Energy Balances, 2024 (final data), table 1: Balance of Electricity in 2024", report_url=URL,
                                    document_list="https://www.stat.gov.rs/en-us/", license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
