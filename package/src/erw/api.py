"""Public functions of the erw client.

Energy Research Warehouse (ERW). Names mirror the IRW's Python package
(itemresponsewarehouse/Python-pkg) where they fit: info, list_tables, fetch,
filter, version. Every function reads through the active backend
(erw.backends), so the storage behind them can change without changing these.
"""

from typing import Dict, Iterable, List, Optional, Union

import pandas as pd

from .backends import Backend, LocalBackend
from .provenance import PUBLISHERS, parse_header

SECTORS = ["power", "gas", "oil", "products", "lng", "coal", "uranium", "carbon", "capacity",
           "metals", "equities", "news", "deals"]

_backend: Optional[Backend] = None

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
ISO_ALIASES = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
               "spp": "SPP", "isone": "ISO-NE", "iso-ne": "ISO-NE", "isne": "ISO-NE",
               "pjm": "PJM", "us48": "US48",
               # EIA-930 balancing authority codes
               "ciso": "CAISO", "erco": "ERCOT", "nyis": "NYISO", "swpp": "SPP"}


def get_backend() -> Backend:
    """The active backend; a LocalBackend on first use."""
    global _backend
    if _backend is None:
        _backend = LocalBackend()
    return _backend


def set_backend(backend: Union[Backend, str, None] = None) -> Backend:
    """Use another backend, or a LocalBackend on another directory (a path string).

    set_backend() with no argument resets to the default (ERW_DATA_DIR, else
    the repository's warehouse/output).
    """
    global _backend
    if backend is None:
        # session 10: ERW_BACKEND=redivis or supabase selects a remote backend
        from .remote import backend_from_env
        _backend = backend_from_env() or LocalBackend()
    elif isinstance(backend, str):
        _backend = LocalBackend(backend)
    else:
        _backend = backend
    return _backend


def _as_list(v) -> Optional[List[str]]:
    if v is None:
        return None
    if isinstance(v, str):
        return [v]
    return list(v)


def _utc(ts) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def list_tables() -> List[str]:
    """Names of every table the warehouse holds, sorted."""
    return get_backend().list_tables()


def coverage() -> pd.DataFrame:
    """The coverage table: one row per table (the ERW's metadata.csv).

    Columns: table, iso, market, n_nodes, interval, ts_min, ts_max, n_rows,
    source_report, last_run, validator_status, license, sector. ts_min and ts_max are the first
    and last interval starts in UTC.
    """
    cov = get_backend().coverage().copy()
    for c in ("ts_min", "ts_max", "last_run"):
        cov[c] = pd.to_datetime(cov[c], utc=True, errors="coerce")
    return cov


def _is_entities(df: pd.DataFrame) -> bool:
    return list(df.columns[:2]) == ["entity_id", "entity_type"]


def _read(name: str) -> pd.DataFrame:
    header, df = get_backend().read_table(name)
    if _is_entities(df):  # entities shape (session 8): numbers and dates typed, the rest strings
        for c in [c for c in df.columns if c in ("lat", "lon", "capacity_mw") or c.endswith("_mw")]:
            df[c] = pd.to_numeric(df[c].replace("", None), errors="raise").astype(float)
        for c in [c for c in df.columns if c == "status_date" or c.endswith("_date")]:
            df[c] = pd.to_datetime(df[c].replace("", None), format="%Y-%m-%d", errors="raise")
        if "retrieved_at" in df.columns:
            df["retrieved_at"] = pd.to_datetime(df["retrieved_at"], format=TS_FMT, utc=True)
    elif "event_id" in df.columns:  # events shape: event_date may be a date or a UTC time
        d = df["event_date"]
        df["event_date"] = pd.to_datetime(d.where(d.str.contains("T"), d + "T00:00:00Z"),
                                          format=TS_FMT, utc=True)
        for c in ("mw", "price", "significance", "ai_power_relevance"):
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].replace("", None), errors="coerce")
    else:
        df["value"] = pd.to_numeric(df["value"], errors="raise").astype(float)  # MW tables hold whole numbers
        df["ts_utc"] = pd.to_datetime(df["ts_utc"], format=TS_FMT, utc=True)
    meta = parse_header(header)
    meta["table"] = name
    meta["backend"] = get_backend().describe()
    df.attrs["erw"] = meta
    return df


def _subset(df: pd.DataFrame, start=None, end=None, node=None) -> pd.DataFrame:
    attrs = df.attrs
    events = "event_id" in df.columns
    if _is_entities(df):
        return _subset_entities(df, start, end, node)
    t = df["event_date"] if events else df["ts_utc"]
    keep = pd.Series(True, index=df.index)
    if start is not None:
        keep &= t >= _utc(start)
    if end is not None:
        keep &= t < _utc(end)
    nodes = _as_list(node)
    if nodes:
        keep &= df["source"].isin(nodes) if events else (df["node"].isin(nodes) | df["entity"].isin(nodes))
    out = df[keep].reset_index(drop=True)
    out.attrs = attrs
    if start is not None or end is not None or nodes:
        out.attrs["erw"] = dict(attrs["erw"], subset={"start": start, "end": end, "node": nodes})
    return out


def _subset_entities(df: pd.DataFrame, start=None, end=None, node=None) -> pd.DataFrame:
    """Entities: start/end select on status_date (rows without one are dropped when either
    is given); node selects entity_id values (or names, as the source writes them)."""
    attrs = df.attrs
    keep = pd.Series(True, index=df.index)
    d = df["status_date"].dt.tz_localize("UTC") if "status_date" in df else None
    if start is not None:
        keep &= d.notna() & (d >= _utc(start)) if d is not None else False
    if end is not None:
        keep &= d.notna() & (d < _utc(end)) if d is not None else False
    nodes = _as_list(node)
    if nodes:
        keep &= df["entity_id"].isin(nodes) | df["name"].isin(nodes)
    out = df[keep].reset_index(drop=True)
    out.attrs = attrs
    if start is not None or end is not None or nodes:
        out.attrs["erw"] = dict(attrs["erw"], subset={"start": start, "end": end, "node": nodes})
    return out


def fetch(name: Union[str, Iterable[str]], start=None, end=None,
          node: Union[str, Iterable[str], None] = None
          ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Fetch one table as a DataFrame, or several as a dict of name -> DataFrame.

    Series tables: `value` is float and `ts_utc` a timezone-aware UTC timestamp
    marking the START of each interval. Events tables (e.g. news_stories):
    `event_date` is a UTC timestamp (a bare date becomes midnight UTC) and
    `mw`, `price`, `significance`, `ai_power_relevance` are numbers (NaN when
    empty). Entities tables (session 8: EIA-860M generators, ISO queues):
    `lat`, `lon`, `capacity_mw` and every `*_mw` column are floats (NaN when
    empty), `status_date` and every `*_date` column a date (NaT when empty),
    `retrieved_at` a UTC timestamp. Every other column is a string, as written. The
    table's provenance header is parsed into ``df.attrs["erw"]``: title,
    window, forward_dam_days, retrieved, run_log, raw_files, file_summary,
    sources (report, report_url, document_list), notes, and the verbatim
    header lines. An unknown name raises ERWDataNotFound.

    Optional subsetting of rows (session 5 ruling):
    start, end : keep intervals starting in [start, end); strings or
                 timestamps, naive values read as UTC.
    node       : keep these nodes (as the ISO writes them) or entities
                 (``"ercot:HB_NORTH"``, ``"eia930:CISO"``); a string or a list.
                 For an events table, these sources (outlets). For an entities
                 table, these entity_id values or names; start and end then
                 select on status_date.
    The subset is recorded in ``df.attrs["erw"]["subset"]``.
    """
    if isinstance(name, str):
        return _subset(_read(name), start, end, node)
    return {n: _subset(_read(n), start, end, node) for n in list(name)}


def _table_facts(name: str) -> Dict:
    df = _read(name)
    if _is_entities(df):  # variable matches entity_type or status; node an entity_id or name
        return {"variables": set(df["entity_type"]) | set(df["status"].dropna()) if "status" in df
                else set(df["entity_type"]), "nodes": set(df["name"]), "entities": set(df["entity_id"])}
    if "event_id" in df.columns:
        return {"variables": set(df["event_type"]), "nodes": set(df["source"]), "entities": set()}
    return {"variables": set(df["variable"]),
            "nodes": set(df["node"]) if "node" in df else set(df["entity"]),
            "entities": set(df["entity"])}


def filter(iso: Union[str, Iterable[str], None] = None,
           market: Union[str, Iterable[str], None] = None,
           variable: Union[str, Iterable[str], None] = None,
           node: Union[str, Iterable[str], None] = None,
           start=None, end=None, license: Optional[str] = None,
           sector: Union[str, Iterable[str], None] = None) -> List[str]:
    """Names of the tables that match every argument given.

    iso      : "ERCOT", "ercot", "ISO-NE", "isone", ... (any of a list)
    market   : "dam" or "rtm", or a full market id such as "ercot_dam"
    variable : e.g. "lmp_dam", "spp_rtm", "lmp_rtm_15m_mean"
    node     : a node exactly as the ISO writes it ("HB_NORTH", "N.Y.C."),
               or a namespaced entity ("ercot:HB_NORTH")
    start, end : the table has at least one interval starting in [start, end).
               Strings or timestamps; naive values are read as UTC.
    license  : "public" or "internal" (the public site filters on "public")
    sector   : any of power, gas, oil, products, lng, coal, uranium, carbon,
               capacity, metals, equities, news (coverage.csv column sector; a
               table can have several). An unknown sector raises ValueError.
    """
    cov = coverage()
    keep = pd.Series(True, index=cov.index)
    if license is not None:
        keep &= cov["license"] == license
    sectors = [s.lower() for s in _as_list(sector) or []]
    if sectors:
        unknown = sorted(set(sectors) - set(SECTORS))
        if unknown:
            raise ValueError(f"unknown sector {unknown}; sectors are {SECTORS}")
        keep &= cov["sector"].map(lambda v: bool(set(v.split(";")) & set(sectors)))
    isos = _as_list(iso)
    if isos:
        wanted = {ISO_ALIASES.get(i.lower(), i.upper()) for i in isos}
        keep &= cov["iso"].isin(wanted)
    markets = _as_list(market)
    if markets:
        m = [x.lower() for x in markets]
        keep &= cov["market"].map(lambda v: any(v == x or v.endswith("_" + x) for x in m))
    if start is not None:
        keep &= cov["ts_max"] >= _utc(start)
    if end is not None:
        keep &= cov["ts_min"] < _utc(end)
    names = cov.loc[keep, "table"].tolist()
    variables, nodes = _as_list(variable), _as_list(node)
    if variables or nodes:
        # matching on variables or nodes reads each table, so only tables this backend
        # holds are considered (the Supabase live set holds a subset of the catalogue)
        held = set(get_backend().list_tables())
        out = []
        for n in names:
            if n not in held:
                continue
            facts = _table_facts(n)
            if variables and not facts["variables"] & set(variables):
                continue
            if nodes and not (facts["nodes"] | facts["entities"]) & set(nodes):
                continue
            out.append(n)
        names = out
    return sorted(names)


def sources(name: str) -> Dict:
    """Where a table's numbers come from: the source reports and every file URL.

    Returns a dict with table, reports (one entry per source report: source,
    report, report_url, document_list where known), source_urls (every distinct
    source_url in the rows), n_source_urls, retrieved, run_log, raw_files.
    """
    df = _read(name)
    meta = df.attrs["erw"]
    # the durable registry (warehouse/metadata/sources.csv) first: it keeps every
    # report any run used, which a merged file's latest header may not describe
    reg = get_backend().source_registry().set_index("source")
    header = {s["source"]: s for s in meta["sources"]}
    reports = []
    for sid in sorted(set(df["source"]) | set(header)):
        if sid in reg.index:
            r = reg.loc[sid]
            reports.append({"source": sid, "publisher": r["publisher"] or None,
                            "report": r["report"] or None, "report_url": r["report_url"] or None,
                            "document_list": r["document_list"] or None, "license": r["license"]})
        else:
            h = header.get(sid, {})
            reports.append({"source": sid, "publisher": None, "report": h.get("report"),
                            "report_url": h.get("report_url"),
                            "document_list": h.get("document_list"), "license": None})
    urls = sorted(set(df["source_url"]))
    return {"table": name, "reports": reports, "source_urls": urls, "n_source_urls": len(urls),
            "retrieved": meta["retrieved"], "run_log": meta["run_log"],
            "raw_files": meta["raw_files"]}


def cite(name: str) -> str:
    """A citation for the ISO report(s) a table was built from, plus the ERW table.

    The data belong to the ISO that published them; cite the ISO report, and the
    ERW table and data commit as the route by which you obtained it.
    """
    src = sources(name)
    ver = version()
    cov = coverage().set_index("table")
    parts = []
    outlets = []
    for r in src["reports"]:
        if ":" not in r["source"]:
            # a news outlet (events tables): cited by name, listed once below
            outlets.append(r.get("publisher") or r["source"])
            continue
        org = r["source"].split(":", 1)[0]
        report_id = r["source"].split(":", 1)[1]
        publisher = r.get("publisher") or PUBLISHERS.get(org, org.upper())
        title = f"{report_id}{': ' + r['report'] if r.get('report') else ''}"
        url = f" {r['report_url']}." if r.get("report_url") else ""
        parts.append(f"{publisher}. {title}.{url}")
    if outlets:
        parts.append(f"News stories from {len(outlets)} outlets: {', '.join(sorted(set(outlets)))}; "
                     "each row links its story.")
    retrieved = ""
    if name in cov.index and pd.notna(cov.loc[name, "last_run"]):
        retrieved = f" Retrieved {cov.loc[name, 'last_run']:%Y-%m-%d}"
    commit = ver.get("data_commit")
    via = (f"{retrieved} via the Energy Research Warehouse (ERW), table {name}"
           f"{', data commit ' + commit[:12] if commit else ''}.")
    return " ".join(parts) + via


def version() -> Dict[str, Optional[str]]:
    """Identify the data being read.

    For the local backend: data_commit is the git commit that last changed the
    data directory, data_commit_date its time, head_commit the checkout's HEAD,
    and dirty whether the directory holds uncommitted changes.
    """
    from . import __version__
    record = dict(get_backend().version())
    record["package_version"] = __version__
    return record


def info(name: Optional[str] = None, quiet: bool = False) -> Dict:
    """Summarise the warehouse, or one table if a name is given. Prints unless quiet."""
    if name is not None:
        df = fetch(name)
        meta = df.attrs["erw"]
        if _is_entities(df):
            d = {"table": name, "title": meta["title"], "rows": len(df), "shape": "entities",
                 "entity_types": sorted(set(df["entity_type"])),
                 "status": {k: int(v) for k, v in df["status"].value_counts().items()} if "status" in df else {},
                 "capacity_mw": float(df["capacity_mw"].sum()) if "capacity_mw" in df else None,
                 "vintage": sorted(set(df["vintage"])) if "vintage" in df else [],
                 "sources": sorted(set(df["source"])),
                 "license": coverage().set_index("table").loc[name, "license"], "notes": meta["notes"]}
            if not quiet:
                print(f"{name}: {d['title']}")
                print(f"  {d['rows']} entities ({', '.join(d['entity_types'])}), vintage "
                      f"{', '.join(d['vintage'])}, license {d['license']}")
            return d
        if "event_id" in df.columns:
            d = {"table": name, "title": meta["title"], "rows": len(df), "shape": "events",
                 "event_types": sorted(set(df["event_type"])), "sources": sorted(set(df["source"])),
                 "event_date_min": df["event_date"].min(), "event_date_max": df["event_date"].max(),
                 "license": coverage().set_index("table").loc[name, "license"], "notes": meta["notes"]}
            if not quiet:
                print(f"{name}: {d['title']}")
                print(f"  {d['rows']} events from {len(d['sources'])} sources, "
                      f"{d['event_date_min']} to {d['event_date_max']} (UTC), license {d['license']}")
            return d
        d = {"table": name, "title": meta["title"], "rows": len(df),
             "variables": sorted(set(df["variable"])),
             "nodes": sorted(n for n in set(df["node"]) if n) or sorted(set(df["entity"])),
             "license": coverage().set_index("table").loc[name, "license"],
             "ts_min": df["ts_utc"].min(), "ts_max": df["ts_utc"].max(),
             "freq": sorted(set(df["freq"])), "unit": sorted(set(df["unit"])),
             "sources": [s["source"] for s in meta["sources"]],
             "window": meta["window"], "forward_dam_days": meta["forward_dam_days"],
             "notes": meta["notes"]}
        if not quiet:
            print(f"{name}: {d['title']}")
            print(f"  {d['rows']} rows, {len(d['nodes'])} nodes, {d['ts_min']} to {d['ts_max']} "
                  f"(interval starts, UTC), freq {', '.join(d['freq'])}, unit {', '.join(d['unit'])}")
            print(f"  sources: {', '.join(d['sources'])}")
        return d
    cov = coverage()
    ver = version()
    d = {"backend": get_backend().describe(), "n_tables": len(cov),
         "n_rows": int(cov["n_rows"].sum()), "isos": sorted(cov["iso"].unique()),
         "markets": sorted(cov["market"].unique()), "ts_min": cov["ts_min"].min(),
         "ts_max": cov["ts_max"].max(), "data_commit": ver.get("data_commit"),
         "tables_blocked": cov.loc[~cov["validator_status"].astype(str).str.startswith("pass"),
                                   "table"].tolist()}
    if not quiet:
        print("Energy Research Warehouse (ERW)")
        print(f"  {d['n_tables']} tables, {d['n_rows']:,} rows, {len(d['isos'])} ISOs: "
              f"{', '.join(d['isos'])}")
        print(f"  {d['ts_min']} to {d['ts_max']} (interval starts, UTC)")
        print(f"  data: {d['backend']}; commit {(d['data_commit'] or 'unknown')[:12]}")
    return d
