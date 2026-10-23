"""Remote backends for the erw client: Redivis (store of record) and Supabase (live set).

Energy Research Warehouse (ERW), session 10. Both implement the Backend
interface of erw.backends, so every public function (fetch, filter, coverage,
sources, cite, info) works unchanged. Select one with ERW_BACKEND:

    ERW_BACKEND=local      the CSV files (default)
    ERW_BACKEND=redivis    the Stanford dataset datapages.erw:b9wm, its latest released version (session 1001;
                           REDIVIS_API_TOKEN, from the environment or .env)
    ERW_BACKEND=live       the live set through its REST address with the anon key (erw.live, session 1001)
    ERW_BACKEND=auto       each table from local files, else the live set, else Redivis (docs/methods/packages.md)
    ERW_BACKEND=supabase   the Supabase live set (SUPABASE_URL with SUPABASE_SERVICE_KEY; or
                           with SUPABASE_ANON_KEY, public rows only, when ERW_SUPABASE_ROLE=anon)

Both return rows as the ERW's CSV text, like LocalBackend: Redivis infers column
types on upload, so values are written back in the ERW's form (timestamps as
YYYY-MM-DDTHH:MM:SSZ, dates as YYYY-MM-DD, nulls as ""). Provenance headers come
from the erw_headers table (Redivis) or the headers table (Supabase).
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .backends import COVERAGE_COLS, OPTIONAL_COVERAGE_COLS, SOURCE_COLS, Backend, ERWDataNotFound

REDIVIS_META = {"erw_headers", "erw_coverage", "erw_sources"}


def _secret(name: str, required: bool = True) -> str:
    v = os.environ.get(name)
    if not v:
        try:
            from dotenv import dotenv_values
            for parent in [Path.cwd(), *Path.cwd().parents, *Path(__file__).resolve().parents]:
                if (parent / ".env").is_file():
                    v = dotenv_values(parent / ".env").get(name)
                    break
        except ImportError:
            pass
    v = (v or "").strip()
    if required and not v:
        raise ERWDataNotFound(f"{name} is not set (environment or .env)")
    return v


def _as_text(df: pd.DataFrame, types: Dict[str, str]) -> pd.DataFrame:
    """Rows read from a typed store, back in the ERW's CSV text form."""
    out = pd.DataFrame(index=df.index)
    for c in df.columns:
        s, t = df[c], types.get(c, "string")
        if t == "dateTime" or pd.api.types.is_datetime64_any_dtype(s) and t != "date":
            v = pd.to_datetime(s, utc=True, errors="coerce")
            out[c] = v.dt.strftime("%Y-%m-%dT%H:%M:%SZ").fillna("")
        elif t == "date":
            v = pd.to_datetime(s, errors="coerce")
            out[c] = v.dt.strftime("%Y-%m-%d").fillna("")
        elif t == "integer":
            out[c] = s.map(lambda x: "" if pd.isna(x) else str(int(x)))
        elif t == "float":
            out[c] = s.map(lambda x: "" if pd.isna(x) else repr(float(x)))
        elif t == "boolean":
            out[c] = s.map(lambda x: "" if pd.isna(x) else ("true" if x else "false"))
        else:
            out[c] = s.map(lambda x: "" if x is None or (not isinstance(x, str) and pd.isna(x)) else str(x))
    return out


def _coverage_frame(cov: pd.DataFrame) -> pd.DataFrame:
    cov = cov.rename(columns={"table_name": "table"})
    for c in ("n_nodes", "n_rows"):
        cov[c] = cov[c].map(lambda x: int(float(x)) if str(x) != "" else 0)
    missing = [c for c in COVERAGE_COLS if c not in cov.columns]
    if missing:
        raise ValueError(f"coverage lacks columns {missing}")
    cols = COVERAGE_COLS + [c for c in OPTIONAL_COVERAGE_COLS if c in cov.columns]
    return cov[cols].sort_values("table").reset_index(drop=True)


def _read_by_export(table, types: Dict[str, Optional[str]]) -> pd.DataFrame:
    """Session 665: a Redivis table read through its CSV export, as a frame of the stream's types. Errors propagate."""
    import tempfile
    d = tempfile.mkdtemp(prefix="erw-redivis-")
    path = table.download(os.path.join(d, "table.csv"), format="csv", overwrite=True, progress=False)
    path = path[0] if isinstance(path, list) else path
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    os.remove(path)
    for c, t in types.items():
        if c not in df.columns:
            continue
        if t == "dateTime":
            df[c] = pd.to_datetime(df[c].replace("", None), format="ISO8601", utc=True)
        elif t == "date":
            df[c] = pd.to_datetime(df[c].replace("", None), format="ISO8601")
    # numbers stay as the export wrote them (the uploaded CSV's own text), so _as_text must not retype them
    return df


STANFORD = ("datapages", "erw:b9wm", "organization")  # session 1001: Datapages's dataset, DOI 10.57761/4f55-6d55


class RedivisBackend(Backend):
    """Reads the ERW from its Redivis dataset.

    Session 1001 (docs/methods/packages.md): by default the Stanford dataset, `datapages.erw:b9wm`, at its latest
    released version, which any Redivis account can read and cite. version="next" reads the unreleased draft (its
    editors only; never citable); a tag ("v1.0") reads that version.
    """

    name = "redivis"

    def __init__(self, owner: Optional[str] = None, dataset: Optional[str] = None,
                 version: Optional[str] = None, owner_kind: Optional[str] = None):
        """Session 665 (chain 043): the Stanford dataset is an organization's, Datapages's `erw:b9wm`. ERW_REDIVIS_DATASET
        (owner.dataset, an organization's unless ERW_REDIVIS_OWNER_KIND=user) names another. Session 1001: with neither,
        the Stanford dataset (until then, the owner's account and energy_research_warehouse); the latest released
        version unless version= or ERW_REDIVIS_VERSION names one (until then, always the draft)."""
        os.environ.setdefault("REDIVIS_API_TOKEN", _secret("REDIVIS_API_TOKEN"))
        from . import counter
        counter.wrap_redivis()
        import redivis
        named = os.environ.get("ERW_REDIVIS_DATASET", "").strip()
        if dataset is None and named and "." in named:
            owner, dataset = owner or named.split(".", 1)[0], named.split(".", 1)[1]
            owner_kind = owner_kind or os.environ.get("ERW_REDIVIS_OWNER_KIND", "organization")
        if dataset is None and owner is None:
            owner, dataset, owner_kind = STANFORD
        dataset = dataset or "energy_research_warehouse"
        self.owner = owner or _secret("REDIVIS_OWNER")
        self.owner_kind = owner_kind or "user"
        version = version or os.environ.get("ERW_REDIVIS_VERSION", "").strip() or None
        self.dataset_name, self.version_tag = dataset, version or "latest release"
        account = redivis.organization(self.owner) if self.owner_kind == "organization" else redivis.user(self.owner)
        self.ds = account.dataset(dataset, version=version) if version else account.dataset(dataset)
        if not self.ds.exists():
            raise ERWDataNotFound(f"Redivis dataset {self.owner}.{dataset}:{self.version_tag} does not exist, or this "
                                  "token cannot read it")
        self._cache: Dict[str, pd.DataFrame] = {}
        self._version: Optional[Dict[str, Optional[str]]] = None

    def describe(self) -> str:
        return f"Redivis dataset {self.owner}.{self.dataset_name}, version {self.version_tag}"

    def _read(self, name: str) -> pd.DataFrame:
        if name not in self._cache:
            t = self.ds.table(name)
            if not t.exists():
                if name in REDIVIS_META:
                    v = self.version()
                    raise ERWDataNotFound(
                        f"{self.owner}.{self.dataset_name} version {v.get('version') or self.version_tag} holds no {name} "
                        "table: the ERW's first full release waits for its release on Redivis. An editor of the dataset "
                        "can read the draft with erw.RedivisBackend(version='next').")
                raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
            types = {v.name: (v.properties or {}).get("type") for v in t.list_variables()}
            try:
                df = t.to_pandas_dataframe(progress=False, dtype_backend="numpy")
            except Exception as exc:
                # session 665: Redivis refuses a stream once a user has streamed 100 GB in 30 days ("Cannot stream more
                # than 100GB ... Please use the export API instead"); the table is then read through its CSV export,
                # typed as the stream would have typed it (the uploader's read_frame does the same)
                if "Cannot stream more than" not in str(exc):
                    raise
                df = _read_by_export(t, types)
                types = {c: v for c, v in types.items() if v in ("dateTime", "date")}  # numbers are text already
            self._cache[name] = _as_text(df, types)
        return self._cache[name].copy()

    def list_tables(self) -> List[str]:
        return sorted(t.name for t in self.ds.list_tables() if t.name not in REDIVIS_META)

    def read_table(self, name: str) -> Tuple[List[str], pd.DataFrame]:
        df = self._read(name)
        return self.header(name), df.reset_index(drop=True)

    def header(self, name: str) -> List[str]:
        h = self._read("erw_headers")
        h = h[h["table"] == name].copy()
        h["n"] = h["line_no"].astype(int)
        return h.sort_values("n")["line"].tolist()

    def columns(self, name: str) -> List[str]:
        t = self.ds.table(name)
        if not t.exists():
            raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
        return [v.name for v in t.list_variables()]

    def titles(self) -> Dict[str, str]:
        h = self._read("erw_headers")
        h = h[h["line"].str.startswith("Energy Research Warehouse (ERW):")].copy()
        h["n"] = h["line_no"].astype(int)
        return {t: g.sort_values("n")["line"].iloc[0].split(":", 1)[1].strip() for t, g in h.groupby("table")}

    def coverage(self) -> pd.DataFrame:
        return _coverage_frame(self._read("erw_coverage"))

    def source_registry(self) -> pd.DataFrame:
        return self._read("erw_sources")[SOURCE_COLS].sort_values("source").reset_index(drop=True)

    def version(self) -> Dict[str, Optional[str]]:
        if self._version is None:
            p = self.ds.get().properties
            v = p.get("version") or {}
            released = bool(v.get("isReleased"))
            self._version = {"backend": self.name, "dataset": p.get("qualifiedReference"),
                             "version": v.get("tag"), "released": released,
                             "released_on": (v.get("releasedAt") or "")[:10] or None,
                             "doi": p.get("doi"), "data_commit": None,
                             "note": None if released else "An unreleased Redivis draft is not citable; cite a released version."}
        return dict(self._version)


class SupabaseBackend(Backend):
    """Reads the ERW live set from Supabase (warehouse/supabase/live_set.yaml).

    role="service" uses SUPABASE_SERVICE_KEY and sees every row; role="anon" uses
    SUPABASE_ANON_KEY and, by row-level security, sees only public rows. Only the
    live set is here: whole tables for some, the last 35 days for ISO and EIA-930 (session 36C; 90 before).
    """

    name = "supabase"
    PAGE = 1000
    SHAPE_COLS = {
        "series": ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node",
                   "source", "source_url", "retrieved_at", "vintage"],
        "entities": ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
                     "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"],
        "events": ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price",
                   "currency", "status", "source", "source_url"],
    }
    SERIES_PARTITION = ["ba", "event"]  # session 536: as warehouse/supabase/load.py writes them
    TYPES = {"ts_utc": "dateTime", "retrieved_at": "dateTime", "event_date": "dateTime",
             "status_date": "date", "value": "float", "lat": "float", "lon": "float",
             "capacity_mw": "float", "mw": "float", "price": "float"}

    def __init__(self, role: Optional[str] = None):
        import urllib.parse
        from supabase import create_client
        self.role = role or os.environ.get("ERW_SUPABASE_ROLE", "service")
        key = _secret("SUPABASE_ANON_KEY" if self.role == "anon" else "SUPABASE_SERVICE_KEY")
        u = urllib.parse.urlparse(_secret("SUPABASE_URL"))
        self.url = f"{u.scheme}://{u.netloc}"
        self.client = create_client(self.url, key)
        self._cache: Dict[str, pd.DataFrame] = {}

    def describe(self) -> str:
        return f"Supabase live set at {self.url} ({self.role} key)"

    # Each table's key, the order pages are read in (session 13): without an ORDER BY,
    # Postgres does not promise the same row order on every request, so paging by range
    # could repeat some rows and skip others (seen as a flaky 27,702-row fetch).
    ORDER = {"series": ["entity", "variable", "ts_utc", "event"], "entities": ["entity_id"],  # event: session 36C
             "events": ["event_id"], "catalogue": ["table_name"], "sources": ["source"],
             "headers": ["line_no"], "latest_prices": ["entity", "variable"]}

    def _select(self, table: str, **eq) -> List[dict]:
        rows, start = [], 0
        while True:
            q = self.client.table(table).select("*")
            for k, v in eq.items():
                q = q.eq(k, v)
            for c in self.ORDER.get(table, []):
                q = q.order(c)
            batch = q.range(start, start + self.PAGE - 1).execute().data
            rows += batch
            if len(batch) < self.PAGE:
                return rows
            start += self.PAGE

    def _catalogue(self) -> pd.DataFrame:
        if "_catalogue" not in self._cache:
            cat = pd.DataFrame(self._select("catalogue"))
            if cat.empty:
                raise ERWDataNotFound(f"no catalogue rows readable in {self.describe()}")
            self._cache["_catalogue"] = cat
        return self._cache["_catalogue"].copy()

    def list_tables(self) -> List[str]:
        cat = self._catalogue()
        return sorted(cat.loc[cat["in_live_set"] == "yes", "table_name"])

    def read_table(self, name: str) -> Tuple[List[str], pd.DataFrame]:
        if name not in self.list_tables():
            raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
        if name not in self._cache:
            interval = self._catalogue().set_index("table_name").loc[name, "interval"]
            shape = "entities" if interval == "snapshot" else ("events" if interval == "event" else "series")
            rows = self._select(shape, table_name=name)
            cols = self.SHAPE_COLS[shape]
            # a live-set table can hold no rows (an ERCOT yearly table outside the 90-day window)
            df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols + ["extra"])
            extra = pd.DataFrame(df["extra"].tolist()) if "extra" in df and len(df) else pd.DataFrame(index=df.index)
            # session 536: a series row's partition columns (ba, event: warehouse/supabase/load.py SERIES_PARTITION,
            # migrations 009 and 011) are columns of the series table, not keys of extra. They were dropped here, so
            # fetch("eia930_all_demand", ba="ciso") on this backend returned no rows and every ba read "".
            if shape == "series":
                cols = cols + [c for c in self.SERIES_PARTITION if c in df.columns]
            body = _as_text(df[cols], self.TYPES)
            full = pd.concat([body, extra.fillna("").astype(str)], axis=1)
            # exactly the table's own columns in CSV order (catalogue.columns, migration 003):
            # drops standard columns the table does not use, restores its empty own columns
            cols_json = self._catalogue().set_index("table_name").get("columns", pd.Series(dtype=object)).get(name)
            if isinstance(cols_json, str) and cols_json:
                order = json.loads(cols_json)
                full = full.reindex(columns=order, fill_value="")
            self._cache[name] = full
        hdr = pd.DataFrame(self._select("headers", table_name=name))
        header = hdr.sort_values("line_no")["line"].tolist() if len(hdr) else []
        return header, self._cache[name].copy()

    def columns(self, name: str) -> List[str]:
        cat = self._catalogue().set_index("table_name")
        if name not in cat.index:
            raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
        cols_json = cat.get("columns", pd.Series(dtype=object)).get(name)
        return json.loads(cols_json) if isinstance(cols_json, str) and cols_json else []

    def coverage(self) -> pd.DataFrame:
        cat = self._catalogue()
        cat = _as_text(cat, {"ts_min": "dateTime", "ts_max": "dateTime", "last_run": "dateTime"})
        return _coverage_frame(cat)

    def source_registry(self) -> pd.DataFrame:
        reg = _as_text(pd.DataFrame(self._select("sources")), {})
        return reg[SOURCE_COLS].sort_values("source").reset_index(drop=True)

    def version(self) -> Dict[str, Optional[str]]:
        return {"backend": self.name, "data_commit": None, "role": self.role,
                "note": "The live set is derived from the ERW tables and rebuilt daily; cite Redivis."}


def backend_from_env():
    """The backend ERW_BACKEND names: local (default), live, redivis or supabase; "auto" for per-table routing."""
    kind = os.environ.get("ERW_BACKEND", "local").strip().lower()
    if kind == "redivis":
        return RedivisBackend()
    if kind == "supabase":
        return SupabaseBackend()
    if kind == "live":  # session 1001: the live set through its REST address, anon key
        from .live import LiveBackend
        return LiveBackend()
    if kind in ("", "local"):
        return None
    if kind == "auto":
        return "auto"
    raise ValueError(f"ERW_BACKEND={kind!r}: use local, live, redivis, supabase or auto")
