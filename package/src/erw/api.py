"""Public functions of the erw client.

Energy Research Warehouse (ERW). Names mirror the IRW's Python package
(itemresponsewarehouse/Python-pkg) where they fit: info, list_tables, fetch,
filter, version. Every function reads through the active backend
(erw.backends), so the storage behind them can change without changing these.
"""

import os
import re
import time
import warnings
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd

from . import counter, licenses
from .backends import Backend, ERWDataNotFound, ERWLicenseHeld, ERWLicenseWarning, LocalBackend
from .provenance import PUBLISHERS, parse_header

SECTORS = ["power", "gas", "oil", "products", "lng", "coal", "uranium", "carbon", "capacity",
           "metals", "equities", "news", "deals", "datacenters", "platform"]  # session 30: platform (operating tables)

_backend: Optional[Backend] = None
# Session 1001 (docs/methods/packages.md): the backends a call names (backend="local", "live", "redivis"), made once a
# session, and whether the session routes each table itself (backend "auto": ERW_BACKEND=auto, or no local tables and
# no ERW_DATA_DIR)
_instances: Dict[str, Backend] = {}
_auto = False
BACKENDS = ("auto", "local", "live", "redivis")
NO_DATA = ("No ERW data found. Set ERW_DATA_DIR to a directory of ERW tables (the warehouse/output folder of a clone of "
           "the erw repository), or ERW_LIVE_URL and ERW_LIVE_KEY for the live set, or REDIVIS_API_TOKEN for the "
           "Redivis dataset.")

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
ISO_ALIASES = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
               "spp": "SPP", "isone": "ISO-NE", "iso-ne": "ISO-NE", "isne": "ISO-NE",
               "pjm": "PJM", "us48": "US48",
               # EIA-930 balancing authority codes
               "ciso": "CAISO", "erco": "ERCOT", "nyis": "NYISO", "swpp": "SPP"}


def get_backend() -> Backend:
    """The active backend. On first use, the one ERW_BACKEND names (local, redivis or supabase), else a
    LocalBackend.

    Session 536: until then the first use always made a LocalBackend and ERW_BACKEND counted only in
    set_backend(), so an install from GitHub with ERW_BACKEND=supabase and no local tables failed at
    erw.info() with "No ERW data directory found", although the README and docs/guide.md say ERW_BACKEND picks
    the backend.
    """
    global _backend
    if _backend is None:
        _backend = _default_backend()
    return _backend


def _default_backend() -> Backend:
    """Session 1001: ERW_BACKEND's backend; else local files; else, when no local tables are found and ERW_DATA_DIR does
    not name a directory, the first of the live set and Redivis that answers, each table routed by fetch (auto)."""
    global _auto
    from .remote import backend_from_env
    _auto = False
    b = backend_from_env()
    if b == "auto":
        _auto = True
        return _first_available()
    if b is not None:
        return b
    if os.environ.get("ERW_DATA_DIR"):
        return LocalBackend()   # a directory named and not found is an error, never a quiet change of backend
    try:
        return LocalBackend()
    except ERWDataNotFound as local_error:
        _auto = True
        try:
            return _first_available(skip_local=True)
        except ERWDataNotFound as e:
            raise ERWDataNotFound(f"{local_error} {e}") from None


def _make(kind: str) -> Backend:
    """The backend a call names, made once a session."""
    if kind not in _instances:
        if kind == "local":
            _instances[kind] = LocalBackend()
        elif kind == "live":
            from .live import LiveBackend
            _instances[kind] = LiveBackend()
        elif kind == "redivis":
            from .remote import RedivisBackend
            _instances[kind] = RedivisBackend()
        else:
            raise ValueError(f"backend={kind!r}: use one of {', '.join(BACKENDS)}")
    return _instances[kind]


def _first_available(skip_local: bool = False) -> Backend:
    errors = []
    for kind in (("live", "redivis") if skip_local else ("local", "live", "redivis")):
        try:
            return _make(kind)
        except Exception as e:  # noqa: BLE001 - each reason is reported together below
            errors.append(f"{kind}: {e}")
    raise ERWDataNotFound(NO_DATA + " (" + "; ".join(errors) + ")")


def _live_covers(window: str, start) -> bool:
    """Session 1001: the live set holds the rows a fetch asks for: a table it keeps whole, or a window that starts within
    its last days less five (the live set keeps 35 days of prices; auto reads it for 30)."""
    if window in ("whole", "some rows"):
        return True
    m = re.match(r"^(\d+) days$", window or "")
    if not m or start is None:
        return False
    return _utc(start) >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=int(m.group(1)) - 5)


def _route(name: str, backend: Optional[str] = None, start=None) -> Backend:
    """The backend a table is read from: the one named; the session's; or, routed (auto), local files when the table's
    CSV is on disk, else the live set when it holds the window, else Redivis's latest release."""
    if backend is None:
        b = get_backend()
        if not _auto:
            return b
        backend = "auto"
    if backend != "auto":
        return _make(backend)
    cur = _current(name)
    try:
        loc = _make("local")
        if (loc.data_dir / f"{cur}.csv").is_file():
            return loc
    except ERWDataNotFound:
        pass
    if _live_covers(licenses.rows().get(cur, {}).get("live_window", ""), start):
        try:
            return _make("live")
        except Exception:  # noqa: BLE001 - no live set configured: Redivis below
            pass
    return _make("redivis")


def set_backend(backend: Union[Backend, str, None] = None) -> Backend:
    """Use another backend, or a LocalBackend on another directory (a path string).

    set_backend() with no argument resets to the default (ERW_DATA_DIR, else
    the repository's warehouse/output).
    """
    global _backend, _MIGRATIONS, _auto
    _MIGRATIONS = None  # session 536: the map is read again for the new backend's data directory
    _instances.clear()  # session 1001: the backends a call names are made again, with the environment as it is now
    _VERSIONS.clear()
    licenses.reset()
    if backend is None:
        # session 10: ERW_BACKEND=redivis or supabase selects a remote backend
        _backend = _default_backend()
    elif isinstance(backend, str) and backend in BACKENDS:
        _auto = backend == "auto"   # session 1001: set_backend("live"), set_backend("auto")
        _backend = _first_available() if _auto else _make(backend)
    elif isinstance(backend, str):
        _auto = False
        _backend = LocalBackend(backend)
    else:
        _auto = False
        _backend = backend
    return _backend


# Session 29: 54 tables became 6 consolidated tables with the partition in a column (docs/datastandard.md,
# decision 28). The map is warehouse/metadata/table_migrations.csv; an old name keeps working through it, with a
# DeprecationWarning, until the first monthly release.
PARTITION_COLUMNS = ("market", "ba", "year")
_MIGRATIONS: Optional[Dict[str, Tuple[str, Dict[str, str]]]] = None


def _migrations_csv() -> Optional[Path]:
    env = os.environ.get("ERW_MIGRATIONS_CSV")
    if env:
        return Path(env)
    # session 536: beside the local tables, as coverage.csv and sources.csv are (<data dir>/../metadata). An install
    # from GitHub (not editable) lives outside the clone, so the search from this file below never reaches it, and
    # an old name such as ercot_dam_hub_prices failed with ERWDataNotFound when ERW_DATA_DIR named the tables.
    try:
        b = get_backend()
    except (FileNotFoundError, ValueError, ImportError):
        b = None
    if isinstance(b, LocalBackend):
        candidate = b.data_dir.parent / "metadata" / "table_migrations.csv"
        if candidate.is_file():
            return candidate
    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for parent in [base, *base.parents]:
            candidate = parent / "warehouse" / "metadata" / "table_migrations.csv"
            if candidate.is_file():
                return candidate
    return None


def migrations() -> Dict[str, Tuple[str, Dict[str, str]]]:
    """{old table: (consolidated table, {partition column: value})} (session 29)."""
    global _MIGRATIONS
    if _MIGRATIONS is None:
        path = _migrations_csv()
        _MIGRATIONS = {}
        if path is not None:
            m = pd.read_csv(path, dtype=str, keep_default_na=False)
            for r in m.to_dict("records"):
                _MIGRATIONS[r["old_table"]] = (
                    r["new_table"], dict(kv.split("=", 1) for kv in r["partition"].split(";") if kv))
    return _MIGRATIONS


def _current(name: str) -> str:
    """The table a name is read from today: itself, or the consolidated table an old name moved into."""
    return migrations().get(name, (name, {}))[0]


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


def coverage(table: Optional[str] = None, backend: Optional[str] = None) -> pd.DataFrame:
    """The coverage table: one row per table (the ERW's metadata.csv).

    Columns: table, iso, market, n_nodes, interval, ts_min, ts_max, n_rows,
    source_report, last_run, validator_status, license, sector, derived, and (session 28) tier,
    the provenance tier: source, derived or model_extracted (docs/datastandard.md). ts_min and
    ts_max are the first and last interval starts in UTC.

    Session 1001 (docs/methods/packages.md): `verdict`, the ERW's one word for the table's license (public, internal
    or unsettled; `license` stays the flag, public or internal), and `live_window`, what the live set keeps of it
    (whole, <N> days, some rows, none). With a table, its one row (an old name, its table's); an unknown table raises
    ERWDataNotFound. backend: the coverage of that backend (the session's when None).
    """
    b = get_backend() if backend in (None, "auto") else _make(backend)
    cov = b.coverage().copy()
    for c in ("ts_min", "ts_max", "last_run"):
        cov[c] = pd.to_datetime(cov[c], utc=True, errors="coerce")
    lic = licenses.rows()
    cov["verdict"] = cov["table"].map(lambda t: lic.get(t, {}).get("verdict", ""))
    cov["live_window"] = cov["table"].map(lambda t: lic.get(t, {}).get("live_window", ""))
    if table is None:
        return cov
    row = cov[cov["table"] == _current(table)].reset_index(drop=True)
    if row.empty:
        raise ERWDataNotFound(_not_found(table, list(cov["table"])))
    return row


def _not_found(name: str, names: List[str]) -> str:
    """Session 1013: the sentence of errors.WORDS["not_found"], with the tables of a close name."""
    import difflib
    from . import errors
    return errors.say("not_found", table=name, near=errors.near(difflib.get_close_matches(name, names, n=3, cutoff=0.6)))


def tables(backend: Optional[str] = None) -> pd.DataFrame:
    """Session 1001 (docs/methods/packages.md): every table of the warehouse, one row each: table, shape (series,
    entities, events), interval, ts_min, ts_max, n_rows, verdict (public, internal, unsettled), in_live (yes or no) and
    title (its provenance header's first line, where the backend can say it without reading the rows). A table that is
    not public is listed with its verdict, so a reader learns that it exists and why it is not served."""
    b = get_backend() if backend in (None, "auto") else _make(backend)
    cov = coverage(backend=backend)
    try:
        titles = b.titles()
    except Exception:  # noqa: BLE001 - a title is a convenience; the table list stands without it
        titles = {}
    shape = cov["interval"].map(lambda i: "entities" if i == "snapshot" else ("events" if i == "event" else "series"))
    out = pd.DataFrame({"table": cov["table"], "shape": shape, "interval": cov["interval"], "ts_min": cov["ts_min"],
                        "ts_max": cov["ts_max"], "n_rows": cov["n_rows"], "verdict": cov["verdict"],
                        "in_live": cov["live_window"].map(lambda w: "yes" if w not in ("", "none") else "no"),
                        "title": cov["table"].map(lambda t: titles.get(t, ""))})
    return out.reset_index(drop=True)


def license(name: str) -> Dict:
    """Session 1001 (docs/methods/packages.md): the table's license. verdict (public, internal, unsettled: the ERW's one
    word, docs/licenses.md), status ("license needed" from status_from, or ""), decided_by (the publishers whose terms
    decide it), publishers (every publisher of the table), words (one sentence a reader can act on) and record (the
    license record read: the clone's files, or the copy shipped with the package)."""
    cur = _current(name)
    row = licenses.rows().get(cur)
    if row is None:
        raise ERWDataNotFound(_not_found(name, sorted(licenses.rows())))
    return {"table": cur, "verdict": row["verdict"], "status": row["status"], "status_from": row["status_from"],
            "decided_by": [x.strip() for x in row["decided_by"].split(";") if x.strip()],
            "publishers": [x.strip() for x in row["publishers"].split(";") if x.strip()],
            "words": row["words"], "record": licenses.read_from()}


# Session 1001: the column rules of docs/datastandard.md, by shape, for standard()
SHAPE_RULES = {
    "series": {"required": ["entity", "variable", "ts_utc", "value"],
               "reserved": ["unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"],
               "partition": ["ba", "year", "event"], "key": ["entity", "variable", "ts_utc"]},
    "entities": {"required": ["entity_id", "entity_type", "name", "source"],
                 "reserved": ["geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source_url",
                              "retrieved_at", "vintage"], "partition": [], "key": ["entity_id"]},
    "events": {"required": ["event_id", "event_date", "event_type", "source", "source_url"],
               "reserved": ["parties", "entity_ids", "mw", "price", "currency", "status"], "partition": [],
               "key": ["event_id"]},
}


def column_type(shape: str, column: str) -> str:
    """number, utc time, date or text: the one rule of docs/methods/packages.md, "The column types, by shape"."""
    if shape == "series":
        return {"value": "number", "ts_utc": "utc time"}.get(column, "text")
    if shape == "entities":
        if column in ("lat", "lon", "capacity_mw") or column.endswith("_mw"):
            return "number"
        if column == "status_date" or column.endswith("_date"):
            return "date"
        return "utc time" if column == "retrieved_at" else "text"
    if shape == "events":
        if column == "event_date":
            return "utc time"
        return "number" if column in ("mw", "price", "significance", "ai_power_relevance") else "text"
    return "text"


def shape_of(columns: List[str]) -> str:
    if list(columns[:4]) == ["entity", "variable", "ts_utc", "value"]:
        return "series"
    if list(columns[:2]) == ["entity_id", "entity_type"]:
        return "entities"
    if list(columns[:1]) == ["event_id"]:
        return "events"
    return "other"


def standard(name: str, backend: Optional[str] = None) -> Dict:
    """Session 1001 (docs/methods/packages.md): the table's shape and its columns, each with its type (number, utc time,
    date, text) and whether the data standard requires it (yes, reserved, partition, extra), in the table's own order,
    and its key. Read from the table's header row where the backend can (local files, the live set's catalogue,
    Redivis's variables), never from its rows."""
    cur = _current(name)
    b = _route(name, backend)
    cols = b.columns(cur)
    shape = shape_of(cols)
    rules = SHAPE_RULES.get(shape, {"required": [], "reserved": [], "partition": [], "key": []})

    def need(c):
        if c in rules["required"]:
            return "yes"
        if c in rules["reserved"]:
            return "reserved"
        return "partition" if c in rules["partition"] else "extra"
    key = list(rules["key"]) + (["vintage"] if shape == "series" and "vintage" in cols and _keeps_revisions(cur) else [])
    return {"table": cur, "shape": shape,
            "columns": [{"name": c, "type": column_type(shape, c), "required": need(c)} for c in cols],
            "key": key}


def _keeps_revisions(name: str) -> bool:
    """A series table whose key includes vintage: the data standard says so where a table keeps more than one revision;
    the package cannot tell without the rows, so it says so only for the tables whose header says it."""
    return False


def requests(reset: bool = False) -> Dict[str, int]:
    """Session 1001: the requests this package has made to Redivis and the live set since it was imported (or since
    the last reset)."""
    return counter.counts(reset)


def _is_entities(df: pd.DataFrame) -> bool:
    return list(df.columns[:2]) == ["entity_id", "entity_type"]


def _backend_read(name: str, where: Optional[Dict[str, str]], b: Optional[Backend] = None,
                  filters: Optional[List[Tuple[str, str]]] = None):
    b = b or get_backend()
    if where and isinstance(b, LocalBackend):
        return b.read_table(name, where=where)
    if filters is not None:  # session 1001: the live set filters on the server (filters are made for it alone)
        header, df = b.read_table(name, filters=filters + [(c, f"eq.{v}") for c, v in (where or {}).items()])
    else:
        header, df = b.read_table(name)
    for c, v in (where or {}).items():
        df = df[df[c] == str(v)] if c in df.columns else df.iloc[0:0]
    return header, df.reset_index(drop=True)


def _read(name: str, where: Optional[Dict[str, str]] = None, b: Optional[Backend] = None,
          filters: Optional[List[Tuple[str, str]]] = None) -> pd.DataFrame:
    """One table as typed frame. Session 29: where={partition column: value} keeps one partition; an old table
    name is read from its consolidated table (DeprecationWarning), with its own columns and header. Session 1001: b,
    the backend it is read from (the session's when None); filters, the live set's server-side filters."""
    b = b or get_backend()
    moved = migrations().get(name)
    if moved is not None and name not in set(b.list_tables()):
        new, part = moved
        warnings.warn(f"erw: table {name!r} is now part of {new!r} (session 29, "
                      f"docs/migrations/2026-09-29-consolidation.md); reading {new} where "
                      + ", ".join(f"{k}={v}" for k, v in part.items())
                      + ". Old names work until the first monthly release.", DeprecationWarning, stacklevel=3)
        header, df = _backend_read(new, {**part, **(where or {})}, b)
        added = [c for c in part if c != "market"]
        df = df.drop(columns=[c for c in added if c in df.columns])
        block = [h.split(": ", 1)[1] for h in header if h.startswith(f"Member {name}: ")]
        block = [h for h in block if not h.endswith("(its rows; its own provenance header follows)")]
        header = block or header
        return _typed(name, header, df, migrated_to=new, b=b)
    header, df = _backend_read(name, where, b, filters)
    return _typed(name, header, df, b=b)


def _typed(name: str, header: List[str], df: pd.DataFrame, migrated_to: Optional[str] = None,
           b: Optional[Backend] = None) -> pd.DataFrame:
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
    if migrated_to:
        meta["migrated_to"] = migrated_to
    meta["backend"] = (b or get_backend()).describe()
    df.attrs["erw"] = meta
    return df


def _subset(df: pd.DataFrame, start=None, end=None, node=None, variable=None) -> pd.DataFrame:
    attrs = df.attrs
    events = "event_id" in df.columns
    if _is_entities(df):
        return _subset_entities(df, start, end, node, variable)
    t = df["event_date"] if events else df["ts_utc"]
    keep = pd.Series(True, index=df.index)
    if start is not None:
        keep &= t >= _utc(start)
    if end is not None:
        keep &= t < _utc(end)
    nodes = _as_list(node)
    if nodes:
        keep &= df["source"].isin(nodes) if events else (
            (df["node"].isin(nodes) if "node" in df.columns else False) | df["entity"].isin(nodes))
    variables = _as_list(variable)  # session 1001: variable, or an events table's event_type
    if variables:
        keep &= df["event_type" if events else "variable"].isin(variables)
    out = df[keep].reset_index(drop=True)
    out.attrs = attrs
    if start is not None or end is not None or nodes or variables:
        sub = {"start": start, "end": end, "node": nodes}
        if variables:
            sub["variable"] = variables
        out.attrs["erw"] = dict(attrs["erw"], subset=sub)
    return out


def _subset_entities(df: pd.DataFrame, start=None, end=None, node=None, variable=None) -> pd.DataFrame:
    """Entities: start/end select on status_date (rows without one are dropped when either
    is given); node selects entity_id values (or names, as the source writes them); session 1001: variable selects
    entity_type values."""
    attrs = df.attrs
    keep = pd.Series(True, index=df.index)
    variables = _as_list(variable)
    if variables:
        keep &= df["entity_type"].isin(variables)
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
    if start is not None or end is not None or nodes or variables:
        sub = {"start": start, "end": end, "node": nodes}
        if variables:
            sub["variable"] = variables
        out.attrs["erw"] = dict(attrs["erw"], subset=sub)
    return out


def fetch(name: Union[str, Iterable[str]], start=None, end=None,
          node: Union[str, Iterable[str], None] = None, market: Optional[str] = None,
          ba: Optional[str] = None, year: Union[str, int, None] = None, *,
          entity: Union[str, Iterable[str], None] = None, variable: Union[str, Iterable[str], None] = None,
          backend: Optional[str] = None) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
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

    Session 29, the consolidated tables (docs/migrations/2026-09-29-consolidation.md):
    market, ba, year : keep one partition, e.g. ``fetch("eia930_all_demand", ba="ciso")``,
                 ``fetch("iso_trader_daily", market="ercot")``,
                 ``fetch("ercot_all_hub_prices_history", market="ercot_rtm", year=2024)``.
                 A local table is then read in chunks, never whole.
    An old table name (``eia930_ciso_demand``) still works, with a DeprecationWarning, until the
    first monthly release: it returns the old table's rows, columns and header.

    Session 1001 (docs/methods/packages.md):
    entity     : the same as node (the specification's name); both may be given.
    variable   : keep these variables (series), entity types (entities) or event types (events).
    backend    : "auto", "local", "live" or "redivis" for this call; None, the session's (ERW_BACKEND or set_backend;
                 auto when no local tables are found). A table whose ERW verdict is not public is refused on the live
                 set and the Stanford dataset (ERWLicenseHeld, the license's words) and read with an ERWLicenseWarning
                 from local files. ``df.attrs["erw"]["version_line"]`` says what was read: the backend and version, the
                 ERW commit, the fetch time and the rows.
    """
    where = {k: str(v) for k, v in (("market", market), ("ba", ba), ("year", year)) if v is not None}
    nodes = (_as_list(node) or []) + (_as_list(entity) or [])
    nodes = nodes or None
    if isinstance(name, str):
        return _fetch_one(name, start, end, nodes, variable, where, backend)
    return {n: _fetch_one(n, start, end, nodes, variable, where, backend) for n in list(name)}


class ERWBadWindow(ValueError):
    """Session 1056 (chain 072): a start or end that is not a date, or a start not before the end; raised before any
    request, with one sentence that says what to write."""


def _check_window(start, end):
    from .errors import say
    ts = {}
    for side, v in (("start", start), ("end", end)):
        if v is None:
            continue
        try:
            ts[side] = _utc(v)
        except (ValueError, TypeError):
            raise ERWBadWindow(say("bad_date", side=side, value=v)) from None
    if len(ts) == 2 and ts["start"] >= ts["end"]:
        raise ERWBadWindow(say("bad_window", start=start, end=end))


def _fetch_one(name, start, end, nodes, variable, where, backend):
    _check_window(start, end)
    b = _route(name, backend, start)
    lic = _license_check(name, b)
    from .live import LiveBackend
    if isinstance(b, LiveBackend) and licenses.rows().get(_current(name), {}).get("live_window") == "none":
        from .errors import say
        raise ERWDataNotFound(say("not_live", table=name))   # session 1056: an ERW table, not in the live set
    filters = None
    from .live import LiveBackend, series_filters
    if isinstance(b, LiveBackend) and name not in migrations():
        shape = _live_shape(b, name)
        filters = series_filters(nodes, variable, start, end, shape)
    df = _subset(_read(name, where or None, b, filters), start, end, nodes, variable)
    if df.empty and (start is not None or end is not None):
        _empty_window(name, start, end)
    meta = dict(df.attrs["erw"])
    if where:
        meta["partition"] = where
    fetched = pd.Timestamp.now(tz="UTC").strftime(TS_FMT)
    meta["fetched"] = fetched
    meta["license"] = lic
    meta["version_line"] = _version_line(name, b, fetched, len(df))
    df.attrs["erw"] = meta
    return df


class ERWEmptyWindow(UserWarning):
    """Session 1013: a window of a table with no rows in it; the frame is returned, empty, with this sentence."""


def _empty_window(name, start, end):
    from .errors import say
    span = ("", "")
    try:
        row = coverage(name).iloc[0]
        span = tuple(t.strftime(TS_FMT) if pd.notna(t) else "?" for t in (row["ts_min"], row["ts_max"]))
    except Exception:  # noqa: BLE001 - the sentence without the table's span
        span = ("?", "?")
    s = _utc(start).strftime(TS_FMT) if start is not None else "the first row"
    e = _utc(end).strftime(TS_FMT) if end is not None else "the last row"
    warnings.warn(ERWEmptyWindow(say("empty_window", table=name, start=s, end=e, ts_min=span[0], ts_max=span[1])),
                  stacklevel=4)


def _live_shape(b, name: str) -> str:
    interval = b._catalogue().set_index("table_name").loc[_current(name), "interval"] if _current(name) in set(
        b._catalogue()["table_name"]) else ""
    return "entities" if interval == "snapshot" else ("events" if interval == "event" else "series")


def _serves_publicly(b: Backend) -> bool:
    """The backends where the ERW itself serves a table to the public: the live set, and the Stanford dataset."""
    name = getattr(b, "name", "")
    if name == "live":
        return True
    if name == "redivis":
        from .remote import STANFORD
        return (getattr(b, "owner", None), getattr(b, "dataset_name", None)) == STANFORD[:2]
    if name == "supabase":
        return getattr(b, "role", "") == "anon"
    return False


def refusal(name: str) -> str:
    """Session 1001: the words a held table is refused with (docs/methods/packages.md, "What a held table does")."""
    lic = license(name)
    from .errors import say   # session 1013: the one wording, errors.WORDS["held"]
    return say("held", table=name, verdict=lic["verdict"], words=lic["words"], url=licenses.LICENSES_URL)


def _license_check(name: str, b: Backend) -> Dict:
    row = licenses.rows().get(_current(name))
    if row is None:
        return {}
    lic = license(name)
    if lic["verdict"] != "public":
        if _serves_publicly(b):
            raise ERWLicenseHeld(refusal(name))
        warnings.warn(ERWLicenseWarning(f"{name} is not public ({lic['verdict']}): {lic['words']} Read from "
                                        f"{b.describe()}, the reader's own copy under its own license."), stacklevel=4)
    return lic


_VERSIONS: Dict[int, Tuple[float, Dict]] = {}


def _version_of(b: Backend) -> Dict:
    """The backend's version record, kept a minute (a local one asks git each time)."""
    hit = _VERSIONS.get(id(b))
    if hit and time.monotonic() - hit[0] < 60:
        return hit[1]
    try:
        v = dict(b.version())
    except Exception as e:  # noqa: BLE001 - the version line says it is unknown
        v = {"note": f"version unknown: {e}"}
    _VERSIONS[id(b)] = (time.monotonic(), v)
    return v


def _redivis_ref(b: Backend) -> str:
    """'datapages.erw:b9wm': the owner, the dataset, as Redivis names them."""
    return f"{getattr(b, 'owner', '')}.{getattr(b, 'dataset_name', '')}"


def _version_line(name: str, b: Backend, fetched: str, n: int) -> str:
    """ERW <table>: <backend> <version>; ERW commit <12 or unknown>; fetched <time>; <n> rows."""
    v = _version_of(b)
    kind = getattr(b, "name", "")
    if kind == "local":
        where = "local files"
    elif kind == "live":
        where = "the live set"
    elif kind == "redivis":
        where = (f"Redivis {_redivis_ref(b)} {v.get('version')}" if v.get("released")
                 else f"Redivis {_redivis_ref(b)} draft (not citable)")
    else:
        where = b.describe()
    commit = (v.get("data_commit") or "")[:12] or "unknown"
    return f"ERW {name}: {where}; ERW commit {commit}; fetched {fetched}; {n} rows"


def _local_columns(name: str) -> Optional[pd.DataFrame]:
    """Session 33: for a local table, only the columns _table_facts needs, streamed with pyarrow, so filter() never
    holds a large table (the ERCOT history, eia930_all_emissions) whole. None for any other backend or a moved name.

    Session 536: pyarrow is not a dependency of the package, and without it this returned None, so filter(variable=)
    and filter(node=) read every table whole and kept nothing on disk (about nine minutes a call on 198 tables in a
    new venv). Without pyarrow the same columns are now read in pandas chunks and cached the same way."""
    b = get_backend()
    if not isinstance(b, LocalBackend) or name in migrations():
        return None
    try:
        import pyarrow as pa
        import pyarrow.csv as pcsv
    except ImportError:
        pa = pcsv = None
    path = b._path(name)
    with open(path, encoding="utf-8") as f:
        skip = 0
        for line in f:
            if not line.startswith("#"):
                cols = line.strip().split(",")
                break
            skip += 1
    want = [c for c in ("entity_id", "entity_type", "name", "status", "event_id", "event_type", "source", "variable",
                        "node", "entity") if c in cols]
    cached = _facts_cache_read(path, want)
    if cached is not None:
        return cached
    before = os.stat(path)  # the file as it was when the scan began: the cache is keyed on it
    seen = {c: set() for c in want}
    if pa is None:
        # never comment="#" (it would cut a value holding one); every cell as written, an empty one ""
        for chunk in pd.read_csv(path, skiprows=skip, usecols=want, dtype=str, keep_default_na=False, na_values=[],
                                 encoding="utf-8", chunksize=250_000):
            for c in want:
                seen[c] |= set(chunk[c])
        _facts_cache_write(path, seen, before)
        return seen
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=skip, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=want,
                                                               column_types={c: pa.string() for c in want}))
    for batch in reader:
        for c in want:
            seen[c] |= set(batch.column(c).to_pylist())
    _facts_cache_write(path, seen, before)
    return seen


# Session 34: the distinct values _local_columns streams from a local file, cached on disk so filter(node=...) does not
# scan the 0.7 GB ERCOT history on every call. One JSON file per data file, under ERW_CACHE_DIR (default
# ~/.cache/erw/facts), valid only while the data file's modification time (ns) and size are those recorded; any change
# to the file makes the next call scan it again. ERW_FACTS_CACHE=0 turns the cache off.
def _facts_cache_path(path: Path) -> Optional[Path]:
    if os.environ.get("ERW_FACTS_CACHE", "1") == "0":
        return None
    import hashlib
    root = Path(os.environ.get("ERW_CACHE_DIR") or Path.home() / ".cache" / "erw") / "facts"
    key = hashlib.sha256(str(Path(path).resolve()).encode("utf-8")).hexdigest()[:24]
    return root / f"{Path(path).stem}_{key}.json"


def _facts_cache_read(path: Path, want: List[str]) -> Optional[Dict]:
    import json
    cp = _facts_cache_path(path)
    if cp is None or not cp.exists():
        return None
    try:
        st = os.stat(path)
        c = json.loads(cp.read_text(encoding="utf-8"))
        if c["mtime_ns"] != st.st_mtime_ns or c["size"] != st.st_size or sorted(c["columns"]) != sorted(want):
            return None
        return {k: set(v) for k, v in c["columns"].items()}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _facts_cache_write(path: Path, seen: Dict, st: os.stat_result) -> None:
    import json
    cp = _facts_cache_path(path)
    if cp is None:
        return
    try:
        now = os.stat(path)
        if (now.st_mtime_ns, now.st_size) != (st.st_mtime_ns, st.st_size):
            return  # the file changed while it was scanned: not cached
        cp.parent.mkdir(parents=True, exist_ok=True)
        tmp = cp.with_suffix(".tmp")
        tmp.write_text(json.dumps({"path": str(path), "mtime_ns": st.st_mtime_ns, "size": st.st_size,
                                   "columns": {k: sorted(v) for k, v in seen.items()}}), encoding="utf-8")
        os.replace(tmp, cp)
    except OSError:  # a read-only home: the facts are still returned, only not kept
        pass


def _table_facts(name: str) -> Dict:
    s = _local_columns(name)
    if s is not None:  # the same facts as below, from the streamed columns
        if "entity_type" in s and "entity_id" in s:
            return {"variables": s["entity_type"] | s.get("status", set()), "nodes": s["name"],
                    "entities": s["entity_id"]}
        if "event_id" in s:
            return {"variables": s["event_type"], "nodes": s["source"], "entities": set()}
        return {"variables": s["variable"], "nodes": s["node"] if "node" in s else s["entity"],
                "entities": s["entity"]}
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
        # session 29: a consolidated table lists its members' ISOs, separated by ";"
        keep &= cov["iso"].map(lambda v: bool(set(str(v).split(";")) & wanted))
    markets = _as_list(market)
    if markets:
        m = [x.lower() for x in markets]
        keep &= cov["market"].map(lambda v: any(p == x or p.endswith("_" + x)
                                                 for p in str(v).split(";") for x in m))  # session 29: ";"-joined
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


TIER_NOTE = {  # session 28: docs/datastandard.md, "Provenance tiers"
    "source": "as the publisher published it, reshaped only",
    "derived": "computed by the ERW from other tables, method in docs/methods/",
    "model_extracted": "at least one field was written by a model reading the sources, not published by them; "
                       "check a number against its linked source before relying on it",
}


def tier(name: str) -> Optional[str]:
    """The table's provenance tier (session 28): source, derived or model_extracted; None when the
    coverage being read predates the tier column."""
    cov = coverage()
    name = name if name in set(cov["table"]) else _current(name)  # session 29: an old name
    if "tier" not in cov.columns or name not in set(cov["table"]):
        return None
    t = cov.set_index("table").loc[name, "tier"]
    return t if isinstance(t, str) and t else None


def cite(name: str, backend: Optional[str] = None) -> str:
    """The citation line of docs/methods/packages.md, in warehouse/redivis/release_v1.py's words:

        <publishers>. <reports>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset
        `datapages.erw`, version <tag> (released <date>).

    The publishers and reports are the source registry's entries that name the table (sources.csv, its `tables`
    column), or, for a consolidated table, any of its old members (table_migrations.csv). The last clause is where the rows were read: a released Redivis version, the
    live set with its fetch time, or local files with the ERW commit. Session 1001; until then the citation was
    "Retrieved <date> via the Energy Research Warehouse (ERW), table <table>, data commit <12>." with the provenance
    tier (now in coverage() and tier()).
    """
    cur = _current(name)
    b = _route(name, backend) if backend not in (None,) else get_backend()
    if _auto and backend is None:
        try:
            b = _route(name, "auto")
        except Exception:  # noqa: BLE001 - the session's backend below
            b = get_backend()
    reg = b.source_registry()
    # a consolidated table (session 29) is named in the registry by its old members: their entries are its own
    wanted = {cur, name} if cur != name else {cur} | {o for o, (n, _) in migrations().items() if n == cur}
    reps = [r for r in reg.to_dict("records")
            if wanted & {x.strip() for x in re.split(r"[;,]", str(r.get("tables", ""))) if x.strip()}]
    fallback = licenses.rows().get(cur, {}).get("publishers", "")
    names = sorted({r["publisher"] for r in reps if r.get("publisher")}) or ([fallback] if fallback else [])
    reports = sorted({r["report"] for r in reps if r.get("report")})
    head = "; ".join(names) if names else "Energy Research Warehouse (ERW)"
    rep_ = (" " + "; ".join(reports) + ".") if reports else ""
    table = f"`{cur}`" + (f" (formerly {name})" if cur != name else "")
    return f"{head}.{rep_} Via the Energy Research Warehouse (ERW), table {table}, {_cite_clause(b)}."


def _cite_clause(b: Backend) -> str:
    kind = getattr(b, "name", "")
    v = _version_of(b)
    if kind == "redivis":
        ref = _redivis_ref(b).split(":")[0]
        if not v.get("released"):
            return f"Redivis dataset `{ref}`, an unreleased draft (not citable; cite a released version)"
        when = f" (released {v['released_on']})" if v.get("released_on") else ""
        return f"Redivis dataset `{ref}`, version {v.get('version')}{when}"
    if kind == "live":
        return f"the live set, fetched {pd.Timestamp.now(tz='UTC').strftime(TS_FMT)}"
    commit = v.get("data_commit")
    if kind == "local":
        return f"ERW commit {commit[:12]}" if commit else "local files (no ERW commit identifies them)"
    return f"{b.describe()}" + (f", ERW commit {commit[:12]}" if commit else "")


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
                 "license": coverage().set_index("table").loc[_current(name), "license"], "tier": tier(name),
                 "notes": meta["notes"]}
            if not quiet:
                print(f"{name}: {d['title']}")
                print(f"  {d['rows']} entities ({', '.join(d['entity_types'])}), vintage "
                      f"{', '.join(d['vintage'])}, license {d['license']}, tier {d['tier']}")
            return d
        if "event_id" in df.columns:
            d = {"table": name, "title": meta["title"], "rows": len(df), "shape": "events",
                 "event_types": sorted(set(df["event_type"])), "sources": sorted(set(df["source"])),
                 "event_date_min": df["event_date"].min(), "event_date_max": df["event_date"].max(),
                 "license": coverage().set_index("table").loc[_current(name), "license"], "tier": tier(name),
                 "notes": meta["notes"]}
            if not quiet:
                print(f"{name}: {d['title']}")
                print(f"  {d['rows']} events from {len(d['sources'])} sources, "
                      f"{d['event_date_min']} to {d['event_date_max']} (UTC), license {d['license']}, tier {d['tier']}")
            return d
        d = {"table": name, "title": meta["title"], "rows": len(df),
             "variables": sorted(set(df["variable"])),
             "nodes": sorted(n for n in set(df["node"]) if n) or sorted(set(df["entity"])),
             "license": coverage().set_index("table").loc[_current(name), "license"], "tier": tier(name),
             "ts_min": df["ts_utc"].min(), "ts_max": df["ts_utc"].max(),
             "freq": sorted(set(df["freq"])), "unit": sorted(set(df["unit"])),
             "sources": [s["source"] for s in meta["sources"]],
             "window": meta["window"], "forward_dam_days": meta["forward_dam_days"],
             "notes": meta["notes"]}
        if not quiet:
            print(f"{name}: {d['title']}")
            print(f"  {d['rows']} rows, {len(d['nodes'])} nodes, {d['ts_min']} to {d['ts_max']} "
                  f"(interval starts, UTC), freq {', '.join(d['freq'])}, unit {', '.join(d['unit'])}")
            print(f"  sources: {', '.join(d['sources'])}; tier {d['tier']}")
        return d
    cov = coverage()
    ver = version()
    d = {"backend": get_backend().describe(), "n_tables": len(cov),
         "n_rows": int(cov["n_rows"].sum()), "isos": sorted(cov["iso"].unique()),
         "markets": sorted(cov["market"].unique()), "ts_min": cov["ts_min"].min(),
         "ts_max": cov["ts_max"].max(), "data_commit": ver.get("data_commit"),
         "tables_blocked": cov.loc[~cov["validator_status"].astype(str).str.startswith("pass"),
                                   "table"].tolist(),
         "tiers": ({k: int(v) for k, v in cov["tier"].value_counts().items()} if "tier" in cov.columns else {})}
    if not quiet:
        print("Energy Research Warehouse (ERW)")
        print(f"  {d['n_tables']} tables, {d['n_rows']:,} rows, {len(d['isos'])} ISOs: "
              f"{', '.join(d['isos'])}")
        print(f"  {d['ts_min']} to {d['ts_max']} (interval starts, UTC)")
        print(f"  data: {d['backend']}; commit {(d['data_commit'] or 'unknown')[:12]}")
        if d["tiers"]:
            print("  provenance tiers: " + ", ".join(f"{k} {v}" for k, v in sorted(d["tiers"].items())))
    return d
