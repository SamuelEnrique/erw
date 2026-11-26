"""ERW forecast (predict): the warehouse tables the forecast reads, as hourly panels.

Session 10600, chain 730 (lab-desktop's second window). Reads only: every table is read from the warehouse's output
folder (ERW_DATA_ROOT, by default this repository) by skipping the provenance header by count, never by the comment
character (tests/test_session103.py). Nothing here writes a warehouse table. A cache of each panel is kept under
ERW_PREDICT_CACHE (by default runs/predict_cache, not in git), keyed on the source files' size and modification time,
so that a second read of a gigabyte table takes seconds; the cache is a copy, never a source.

Places: `region-<code>` for EIA's thirteen regions of the lower 48 and `ba-<code>` for each balancing authority that
files demand, the code being EIA-930's in lower case (as in site/data/regions/forecast/).

The demand of a place is the demand the warehouse's demand pages show (warehouse/derived/region_files.py): a balancing
authority's own demand_mw of eia930_ba_demand_hourly; a region's sum of its demand-filing authorities, written for an
hour only when each active one holds it (region_files.region_demand). The operator's forecast is EIA-930's day-ahead
demand forecast as eia930_forecast_error_hourly sets it beside the demand (x_forecast_mw), the hours that table
screens out as filing errors left out (x_screened, docs/methods/forecast_error.md).
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.append(os.path.join(ROOT, "warehouse", "connectors"))
sys.path.append(os.path.join(ROOT, "warehouse", "derived"))
import iso_prices as ip  # noqa: E402

DATA_ROOT = os.environ.get("ERW_DATA_ROOT", ROOT)
OUT = os.path.join(DATA_ROOT, "warehouse", "output")
CACHE = os.environ.get("ERW_PREDICT_CACHE", os.path.join(ROOT, "runs", "predict_cache"))

REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]


def table_path(name):
    return os.path.join(OUT, name + ".csv")


def stamp(names):
    """A key of the source files' sizes and modification times: the cache is used only while every file is unchanged."""
    h = hashlib.sha256()
    for n in names:
        st = os.stat(table_path(n))
        h.update(f"{n}:{st.st_size}:{int(st.st_mtime)};".encode())
    return h.hexdigest()[:16]


def retrieved_of(name):
    """The table's own "Retrieved:" line (the first), for the provenance of every file built from it."""
    with open(table_path(name), encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line.startswith("# Retrieved:"):
                return line[len("# Retrieved:"):].strip()
    return None


def read(name, cols, filt=None):
    """A table's columns, header lines skipped by count (never by the comment character)."""
    p = table_path(name)
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, engine="pyarrow")
    fh.close()
    if filt is not None:
        d = d[filt(d)]
    if "ts_utc" in d:
        d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def cached(key, names, build):
    """build() -> DataFrame, kept as parquet under CACHE/<key>_<stamp>.parquet."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{key}_{stamp(names)}.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    df = build()
    df.to_parquet(path)
    return df


def reference():
    """EIA-930's reference table of balancing authorities, read through region_files with this module's data root."""
    import region_files as rp
    keep = rp.ROOT
    rp.ROOT = DATA_ROOT
    try:
        return rp.reference()
    finally:
        rp.ROOT = keep


def place_tz(place, ref):
    import region_files as rp
    kind, code = place.split("-", 1)
    code = code.upper()
    if kind == "region":
        return rp.REGION_TZ[code]
    r = ref.get(code)
    return rp.BA_TZ.get(code) or (r["tz"] if r and r["tz"] else "America/New_York")


def demand_panel():
    """Wide frame, index the UTC hour (start), one column a place: the demand the demand pages show, MW."""
    def build():
        import region_files as rp
        ref, _ = reference()
        ba = read("eia930_ba_demand_hourly", ["entity", "variable", "ts_utc", "value"], lambda d: d["variable"] == "demand_mw")
        cols = {}
        for r in REGIONS:
            s, _members = rp.region_demand(r, ref, ba)
            if len(s.dropna()):
                cols[f"region-{r.lower()}"] = s
        for e, g in ba.groupby("entity"):
            code = e.split(":", 1)[1]
            r = ref.get(code)
            if r is None or not r["us"] or r["generation_only"]:
                continue
            s = pd.Series(g["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"])).sort_index()
            s = s[~s.index.duplicated(keep="last")]
            cols[f"ba-{code.lower()}"] = s
        df = pd.DataFrame(cols)
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return cached("demand", ["eia930_ba_demand_hourly"], build)


def operator_panel():
    """Wide frame like demand_panel: the operator's day-ahead demand forecast (EIA-930), the screened hours left out."""
    def build():
        d = read("eia930_forecast_error_hourly", ["entity", "ts_utc", "x_level", "x_forecast_mw", "x_screened"])
        d = d[d["x_screened"].astype(str).isin(["0", "False", "false"])]
        cols = {}
        for (e, lvl), g in d.groupby(["entity", "x_level"]):
            code = e.split(":", 1)[1].lower()
            place = f"{'region' if lvl == 'region' else 'ba'}-{code}"
            s = pd.Series(g["x_forecast_mw"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"])).sort_index()
            cols[place] = s[~s.index.duplicated(keep="last")]
        df = pd.DataFrame(cols)
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return cached("operator", ["eia930_forecast_error_hourly"], build)


HUBS = {"ercot": "ercot:HB_NORTH", "spp": "spp:SPPNORTH_HUB", "caiso": "caiso:TH_SP15_GEN-APND"
}   # ERCOT, SPP and CAISO: "may be public" (warehouse/metadata/license_verdicts.csv). ISO-NE and NYISO need written permission: never read here
PRICE_TABLES = ["ercot_all_hub_prices_history", "iso_hub_prices_history_2018", "iso_hub_prices_history", "iso_dam_hub_prices"]


def price_panel():
    """Wide frame, index the UTC hour (start), one column a grid of HUBS: the hub's day-ahead price, USD/MWh. The
    tables are read oldest first and a later table's value for the same hour wins (the daily table over the history)."""
    def build():
        frames = []
        for order, t in enumerate(PRICE_TABLES):
            d = read(t, ["entity", "ts_utc", "value", "market"], lambda d: d["market"].astype(str).str.endswith("_dam") & d["entity"].isin(list(HUBS.values())))
            d["order"] = order
            frames.append(d[["entity", "ts", "value", "order"]])
        d = pd.concat(frames, ignore_index=True).sort_values(["entity", "ts", "order"])
        d = d.drop_duplicates(subset=["entity", "ts"], keep="last")
        inv = {v: k for k, v in HUBS.items()}
        cols = {}
        for e, g in d.groupby("entity"):
            cols[inv[e]] = pd.Series(g["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"]))
        df = pd.DataFrame(cols)
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
        df.index.name = "ts"
        return df
    return cached("price_" + "_".join(sorted(HUBS)), PRICE_TABLES, build)


def gas_series():
    """Henry Hub's daily spot price (eia_fuel_spot_prices, USD/MMBtu), indexed by its date."""
    d = read("eia_fuel_spot_prices", ["entity", "variable", "ts_utc", "value"], lambda d: (d["entity"] == "eia:henry_hub") & (d["variable"] == "spot_price"))
    s = pd.Series(d["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(d["ts"]).tz_convert("UTC").tz_localize(None).normalize())
    return s[~s.index.duplicated(keep="last")].sort_index().dropna()


def names():
    """{place: name}: EIA's names of the regions and the authorities (site/data/eia930_ba_names.json and the regions' files)."""
    out = {}
    p = os.path.join(ROOT, "site", "data", "eia930_ba_names.json")
    with open(p, encoding="utf-8") as f:
        doc = json.load(f)
    for code, row in doc.get("authorities", {}).items():
        out[f"ba-{code.lower()}"] = row.get("name")
    for r in REGIONS:
        q = os.path.join(ROOT, "site", "data", "regions", "demand", f"{r.lower()}.json")
        if os.path.exists(q):
            with open(q, encoding="utf-8") as f:
                out[f"region-{r.lower()}"] = json.load(f).get("name")
    return out


def utc_iso(t):
    return pd.Timestamp(t).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def finite(x):
    return x is not None and not (isinstance(x, float) and np.isnan(x))
