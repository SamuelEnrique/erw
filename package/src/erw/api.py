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

_backend: Optional[Backend] = None

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
ISO_ALIASES = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
               "spp": "SPP", "isone": "ISO-NE", "iso-ne": "ISO-NE", "isne": "ISO-NE"}


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
        _backend = LocalBackend()
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
    source_report, last_run, validator_status. ts_min and ts_max are the first
    and last interval starts in UTC.
    """
    cov = get_backend().coverage().copy()
    for c in ("ts_min", "ts_max", "last_run"):
        cov[c] = pd.to_datetime(cov[c], utc=True, errors="coerce")
    return cov


def _read(name: str) -> pd.DataFrame:
    header, df = get_backend().read_table(name)
    df["value"] = pd.to_numeric(df["value"], errors="raise")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], format=TS_FMT, utc=True)
    meta = parse_header(header)
    meta["table"] = name
    meta["backend"] = get_backend().describe()
    df.attrs["erw"] = meta
    return df


def fetch(name: Union[str, Iterable[str]]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Fetch one table as a DataFrame, or several as a dict of name -> DataFrame.

    `value` is float and `ts_utc` a timezone-aware UTC timestamp marking the
    START of each interval. Every other column is a string, as written. The
    table's provenance header is parsed into ``df.attrs["erw"]``: title,
    window, forward_dam_days, retrieved, run_log, raw_files, file_summary,
    sources (report, report_url, document_list), notes, and the verbatim
    header lines. An unknown name raises ERWDataNotFound.
    """
    if isinstance(name, str):
        return _read(name)
    names = list(name)
    return {n: _read(n) for n in names}


def _table_facts(name: str) -> Dict:
    df = _read(name)
    return {"variables": set(df["variable"]),
            "nodes": set(df["node"]) if "node" in df else set(df["entity"]),
            "entities": set(df["entity"])}


def filter(iso: Union[str, Iterable[str], None] = None,
           market: Union[str, Iterable[str], None] = None,
           variable: Union[str, Iterable[str], None] = None,
           node: Union[str, Iterable[str], None] = None,
           start=None, end=None) -> List[str]:
    """Names of the tables that match every argument given.

    iso      : "ERCOT", "ercot", "ISO-NE", "isone", ... (any of a list)
    market   : "dam" or "rtm", or a full market id such as "ercot_dam"
    variable : e.g. "lmp_dam", "spp_rtm", "lmp_rtm_15m_mean"
    node     : a node exactly as the ISO writes it ("HB_NORTH", "N.Y.C."),
               or a namespaced entity ("ercot:HB_NORTH")
    start, end : the table has at least one interval starting in [start, end).
               Strings or timestamps; naive values are read as UTC.
    """
    cov = coverage()
    keep = pd.Series(True, index=cov.index)
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
        out = []
        for n in names:
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
    reports = [dict(s) for s in meta["sources"]]
    known = {r["source"] for r in reports}
    for sid in sorted(set(df["source"]) - known):
        # rows kept from an earlier run can name a report this run's header does not
        reports.append({"source": sid, "report": None, "report_url": None})
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
    for r in src["reports"]:
        org = r["source"].split(":", 1)[0]
        report_id = r["source"].split(":", 1)[1]
        publisher = PUBLISHERS.get(org, org.upper())
        title = f"{report_id}{': ' + r['report'] if r.get('report') else ''}"
        url = f" {r['report_url']}." if r.get("report_url") else ""
        parts.append(f"{publisher}. {title}.{url}")
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
        d = {"table": name, "title": meta["title"], "rows": len(df),
             "variables": sorted(set(df["variable"])), "nodes": sorted(set(df["node"])),
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
