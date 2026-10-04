"""Energy Research Warehouse (ERW): the project map's file, version 2 (session 105).

  python warehouse/derived/project_map.py            # site/data/map_v2.json, from the two EIA-860M tables on this machine

Every operating and planned generating unit of EIA's monthly inventory (Form EIA-860M), batteries among them, as the
page /map/v2 reads it: one compact column per field, a unit per position. It makes no request and writes no warehouse
table: the units are the rows of eia860m_operating_generators and eia860m_planned_generators, unchanged. A site file,
like the network's replay files, built by hand when a new month of the inventory is in the warehouse.

Fields of a unit: name (the plant's), state, grid (the seven ISOs by EIA's balancing authority code; every other
balancing authority, and a blank one, is "outside the seven ISOs"), technology group (the inventory's eleven; a
battery is the storage group's units whose prime mover is BA), status (operating, under construction, planned), MW
(nameplate, capacity_mw), the year it began or is planned to begin operating, latitude and longitude as EIA gives them.
Nothing is estimated and no unit is left out: a unit with no technology group is "not stated".
"""
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

TABLES = ("eia860m_operating_generators", "eia860m_planned_generators")
SITE_FILE = os.path.join(ROOT, "site", "data", "map_v2.json")
GRIDS = [("ERCO", "ercot", "ERCOT"), ("CISO", "caiso", "CAISO"), ("PJM", "pjm", "PJM"), ("MISO", "miso", "MISO"), ("SWPP", "spp", "SPP"),
         ("NYIS", "nyiso", "NYISO"), ("ISNE", "isone", "ISO-NE")]
OUTSIDE = ("outside", "Outside the seven ISOs")
TECHS = [("solar", "Solar"), ("wind", "Wind"), ("battery", "Batteries"), ("storage", "Other storage"), ("natural_gas", "Natural gas"), ("nuclear", "Nuclear"),
         ("coal", "Coal"), ("hydro", "Hydro"), ("petroleum", "Petroleum"), ("biomass", "Biomass"), ("geothermal", "Geothermal"), ("other", "Other"),
         ("unknown", "Not stated")]
STATUSES = [("operating", "Operating"), ("under_construction", "Under construction"), ("planned", "Planned")]


def read(name, out=None):
    path = os.path.join(out or ip.OUT_DIR, name + ".csv")
    return pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)


def units(out=None):
    """Every unit of the two tables, one frame, with the map's fields."""
    op, pl = read(TABLES[0], out), read(TABLES[1], out)
    op["year"] = op["operating_year"]
    pl["year"] = pl["planned_operation_date"].str[:4]
    d = pd.concat([op, pl], ignore_index=True)
    code = {c: slug for c, slug, _ in GRIDS}
    d["grid"] = d["balancing_authority"].map(code).fillna(OUTSIDE[0])
    known = {t for t, _ in TECHS}
    d["tech"] = d["technology_group"].where(d["technology_group"].isin(known), "unknown")
    d.loc[(d["technology_group"] == "storage") & (d["prime_mover"] == "BA"), "tech"] = "battery"
    d["mw"] = pd.to_numeric(d["capacity_mw"], errors="coerce")
    d["lat"] = pd.to_numeric(d["lat"], errors="coerce")
    d["lon"] = pd.to_numeric(d["lon"], errors="coerce")
    if d["mw"].isna().any() or not set(d["status"]) <= {s for s, _ in STATUSES}:
        raise ValueError("a unit has no MW, or a status the map does not know")
    return d


def build(out=None):
    d = units(out).sort_values(["mw", "entity_id"], ascending=[False, True]).reset_index(drop=True)
    vintages = sorted(set(d["vintage"]))
    if len(vintages) != 1:
        raise ValueError(f"the two tables are of different months: {vintages}")
    names = sorted(set(d["name"]))
    name_i = {n: i for i, n in enumerate(names)}
    states = sorted(set(d["state"]))
    grids = [slug for _, slug, _ in GRIDS] + [OUTSIDE[0]]
    techs = [t for t, _ in TECHS]
    statuses = [s for s, _ in STATUSES]
    located = d["lat"].notna() & d["lon"].notna()
    return {
        "tables": list(TABLES), "vintage": vintages[0], "retrieved": d["retrieved_at"].max(), "source_url": d["source_url"].iloc[0],
        "built": ip.utc_iso(pd.Timestamp.now(tz="UTC")),
        "grids": [{"slug": slug, "name": name} for _, slug, name in GRIDS] + [{"slug": OUTSIDE[0], "name": OUTSIDE[1]}],
        "techs": [{"slug": t, "name": n} for t, n in TECHS], "statuses": [{"slug": s, "name": n} for s, n in STATUSES],
        "states": states, "names": names,
        "counts": {"units": int(len(d)), "operating": int((d["status"] == "operating").sum()), "under_construction": int((d["status"] == "under_construction").sum()),
                   "planned": int((d["status"] == "planned").sum()), "batteries": int((d["tech"] == "battery").sum()),
                   "without_balancing_authority": int((d["balancing_authority"] == "").sum()), "under_1_mw": int((d["mw"] < 1).sum()),
                   "without_coordinates": int((~located).sum()), "without_year": int((d["year"] == "").sum()), "mw": round(float(d["mw"].sum()), 1)},
        # one column a field, a unit a position, largest first
        "n": [name_i[x] for x in d["name"]], "s": [states.index(x) for x in d["state"]], "g": [grids.index(x) for x in d["grid"]],
        "t": [techs.index(x) for x in d["tech"]], "st": [statuses.index(x) for x in d["status"]], "mw": [round(float(x), 1) for x in d["mw"]],
        "y": [int(x) if x.isdigit() else 0 for x in d["year"]],
        "la": [None if pd.isna(x) else round(float(x), 4) for x in d["lat"]], "lo": [None if pd.isna(x) else round(float(x), 4) for x in d["lon"]],
    }


def main():
    f = build()
    with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(f, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    c = f["counts"]
    print(f"map_v2.json: {c['units']:,} units of EIA-860M {f['vintage']} ({c['operating']:,} operating, {c['under_construction']:,} under construction, "
          f"{c['planned']:,} planned; {c['batteries']:,} batteries), {c['mw']:,.1f} MW; {os.path.getsize(SITE_FILE):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
