"""Remote backends for the erw client: Redivis (store of record) and Supabase (live set).

Energy Research Warehouse (ERW), session 10. Both implement the Backend
interface of erw.backends, so every public function (fetch, filter, coverage,
sources, cite, info) works unchanged. Select one with ERW_BACKEND:

    ERW_BACKEND=local      the CSV files (default)
    ERW_BACKEND=redivis    the Redivis draft of energy_research_warehouse, all tables
                           (REDIVIS_API_TOKEN and REDIVIS_OWNER, from the environment or .env)
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


class RedivisBackend(Backend):
    """Reads the ERW from its Redivis dataset: the unreleased draft by default (all tables).

    version="next" is the draft the uploader writes; pass a released version tag
    (for example "v1.0") to read what the public reads.
    """

    name = "redivis"

    def __init__(self, owner: Optional[str] = None, dataset: str = "energy_research_warehouse",
                 version: str = "next"):
        os.environ.setdefault("REDIVIS_API_TOKEN", _secret("REDIVIS_API_TOKEN"))
        import redivis
        self.owner = owner or _secret("REDIVIS_OWNER")
        self.dataset_name, self.version_tag = dataset, version
        self.ds = redivis.user(self.owner).dataset(dataset, version=version)
        if not self.ds.exists():
            raise ERWDataNotFound(f"Redivis dataset {self.owner}.{dataset}:{version} does not exist")
        self._cache: Dict[str, pd.DataFrame] = {}

    def describe(self) -> str:
        return f"Redivis dataset {self.owner}.{self.dataset_name}, version {self.version_tag}"

    def _read(self, name: str) -> pd.DataFrame:
        if name not in self._cache:
            t = self.ds.table(name)
            if not t.exists():
                raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
            types = {v.name: (v.properties or {}).get("type") for v in t.list_variables()}
            df = t.to_pandas_dataframe(progress=False, dtype_backend="numpy")
            self._cache[name] = _as_text(df, types)
        return self._cache[name].copy()

    def list_tables(self) -> List[str]:
        return sorted(t.name for t in self.ds.list_tables() if t.name not in REDIVIS_META)

    def read_table(self, name: str) -> Tuple[List[str], pd.DataFrame]:
        df = self._read(name)
        h = self._read("erw_headers")
        h = h[h["table"] == name].copy()
        h["n"] = h["line_no"].astype(int)
        header = h.sort_values("n")["line"].tolist()
        return header, df.reset_index(drop=True)

    def coverage(self) -> pd.DataFrame:
        return _coverage_frame(self._read("erw_coverage"))

    def source_registry(self) -> pd.DataFrame:
        return self._read("erw_sources")[SOURCE_COLS].sort_values("source").reset_index(drop=True)

    def version(self) -> Dict[str, Optional[str]]:
        p = self.ds.get().properties
        v = p.get("version") or {}
        return {"backend": self.name, "dataset": p.get("qualifiedReference"),
                "version": v.get("tag"), "released": v.get("isReleased"),
                "data_commit": None,
                "note": "An unreleased Redivis draft is not citable; cite a released version."
                        if not v.get("isReleased") else None}


class SupabaseBackend(Backend):
    """Reads the ERW live set from Supabase (warehouse/supabase/live_set.yaml).

    role="service" uses SUPABASE_SERVICE_KEY and sees every row; role="anon" uses
    SUPABASE_ANON_KEY and, by row-level security, sees only public rows. Only the
    live set is here: whole tables for some, the last 90 days for ISO and EIA-930.
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
    ORDER = {"series": ["entity", "variable", "ts_utc"], "entities": ["entity_id"],
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
    """The backend ERW_BACKEND names: local (default), redivis or supabase."""
    kind = os.environ.get("ERW_BACKEND", "local").strip().lower()
    if kind == "redivis":
        return RedivisBackend()
    if kind == "supabase":
        return SupabaseBackend()
    if kind in ("", "local"):
        return None
    raise ValueError(f"ERW_BACKEND={kind!r}: use local, redivis or supabase")
