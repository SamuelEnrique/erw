"""The live set through its REST address, with the anon key: the backend `live` of docs/methods/packages.md.

Energy Research Warehouse (ERW), session 1001 (chain 070). The same rows SupabaseBackend reads, through the address
the Stata and R packages call (PostgREST, `<ERW_LIVE_URL>/rest/v1/<table>`), with the standard library only, so the
`supabase` client is not needed. Row-level security returns public rows only. Filters (entity, variable, a window)
are sent to the server, so a fetch of one hub's last week is a request or two, not the table's whole window.

    ERW_LIVE_URL    the project's address (SUPABASE_URL is read when it is not set; a trailing /rest/v1/ is dropped)
    ERW_LIVE_KEY    the anon key (SUPABASE_ANON_KEY is read when it is not set)
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .backends import ERWDataNotFound
from .remote import SupabaseBackend, _as_text, _secret
from . import counter

PAGE = 1000


class LiveBackend(SupabaseBackend):
    """The live set read with the anon key through its REST address (docs/methods/packages.md, backend `live`)."""

    name = "live"

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None, timeout: float = 60.0):
        url = url or _secret("ERW_LIVE_URL", required=False) or _secret("SUPABASE_URL", required=False)
        key = key or _secret("ERW_LIVE_KEY", required=False) or _secret("SUPABASE_ANON_KEY", required=False)
        if not url or not key:
            raise ERWDataNotFound("The live set needs its address and key: set ERW_LIVE_URL and ERW_LIVE_KEY "
                                  "(the ERW gives them on request; the site reads them on its server only).")
        u = urllib.parse.urlparse(url.strip())
        self.url = f"{u.scheme}://{u.netloc}"
        self.key = key.strip()
        self.role = "anon"
        self.timeout = timeout
        self._cache: Dict[str, pd.DataFrame] = {}

    def describe(self) -> str:
        return "the live set (anon key)"

    def _get(self, table: str, params: List[Tuple[str, str]]) -> List[dict]:
        req = urllib.request.Request(live_url(self.url, table, params),
                                     headers={"apikey": self.key, "Authorization": f"Bearer {self.key}",
                                              "Accept": "application/json"})
        counter.add("live")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise ERWDataNotFound(f"the live set answered HTTP {e.code} for {table}: {body}") from None
        except urllib.error.URLError as e:
            raise ConnectionError(f"The live set could not be reached ({e.reason}); check the network and "
                                  "ERW_LIVE_URL.") from None

    def _select(self, table: str, filters: Optional[List[Tuple[str, str]]] = None, **eq) -> List[dict]:
        rows, start = [], 0
        while True:
            batch = self._get(table, page_params(table, filters, start, **eq))
            rows += batch
            if len(batch) < PAGE:
                return rows
            start += PAGE

    def read_table(self, name: str, filters: Optional[List[Tuple[str, str]]] = None) -> Tuple[List[str], pd.DataFrame]:
        """The table's rows, with optional PostgREST filters on its shape table (`entity=in.(...)`,
        `ts_utc=gte....`), applied by the server."""
        if name not in self.list_tables():
            raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
        cat = self._catalogue().set_index("table_name")
        interval = cat.loc[name, "interval"]
        shape = "entities" if interval == "snapshot" else ("events" if interval == "event" else "series")
        key = name + "|" + json.dumps(filters or [])
        if key not in self._cache:
            rows = self._select(shape, filters=filters, table_name=name)
            cols = self.SHAPE_COLS[shape]
            df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols + ["extra"])
            extra = pd.DataFrame(df["extra"].tolist()) if "extra" in df and len(df) else pd.DataFrame(index=df.index)
            if shape == "series":
                cols = cols + [c for c in self.SERIES_PARTITION if c in df.columns]
            body = _as_text(df[[c for c in cols if c in df.columns]].reindex(columns=cols), self.TYPES)
            full = pd.concat([body, extra.fillna("").astype(str)], axis=1)
            cols_json = cat.get("columns", pd.Series(dtype=object)).get(name)
            if isinstance(cols_json, str) and cols_json:
                full = full.reindex(columns=json.loads(cols_json), fill_value="")
            self._cache[key] = full
        hdr = pd.DataFrame(self._select("headers", table_name=name))
        header = hdr.sort_values("line_no")["line"].tolist() if len(hdr) else []
        return header, self._cache[key].copy()

    def columns(self, name: str) -> List[str]:
        cat = self._catalogue().set_index("table_name")
        if name not in cat.index:
            raise ERWDataNotFound(f"No ERW table named {name!r} in {self.describe()}")
        cols_json = cat.get("columns", pd.Series(dtype=object)).get(name)
        return json.loads(cols_json) if isinstance(cols_json, str) and cols_json else []

    def titles(self) -> Dict[str, str]:
        """{table: its header's title}, from the headers table's lines that begin the ERW's title."""
        rows = self._select("headers", filters=[("line", "like.Energy Research Warehouse (ERW):*")])
        out = {}
        for r in sorted(rows, key=lambda r: (r["table_name"], int(r["line_no"]))):
            out.setdefault(r["table_name"], r["line"].split(":", 1)[1].strip())
        return out

    def version(self) -> Dict[str, Optional[str]]:
        return {"backend": self.name, "data_commit": None, "role": "anon",
                "note": "The live set is derived from the ERW tables and rebuilt daily; cite Redivis."}


def page_params(table: str, filters: Optional[List[Tuple[str, str]]] = None, offset: int = 0,
                **eq) -> List[Tuple[str, str]]:
    """The query of one page of a read, in the order the package sends it: select, the equalities (table_name), the
    filters, the order, the limit and the offset. Session 1003: the Stata and R packages send the same."""
    base = [("select", "*")] + [(k, f"eq.{v}") for k, v in eq.items()] + list(filters or [])
    order = SupabaseBackend.ORDER.get(table, [])
    if order:
        base.append(("order", ",".join(order)))
    return base + [("limit", str(PAGE)), ("offset", str(offset))]


def live_url(base: str, table: str, params: List[Tuple[str, str]]) -> str:
    """The address of one request to the live set (session 1003: pure, so another package's addresses can be compared
    with it): `<base>/rest/v1/<table>?<query>`, the query encoded as urllib encodes it, with , . ( ) : * left as they are."""
    return f"{base}/rest/v1/{table}?{urllib.parse.urlencode(params, safe=',.():*')}"


def _utc_text(ts) -> str:
    t = pd.Timestamp(ts)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def series_filters(entity=None, variable=None, start=None, end=None, shape="series") -> List[Tuple[str, str]]:
    """PostgREST filters for a fetch: entity or node, variable, and a UTC window, by shape."""
    def lst(v):
        vals = [v] if isinstance(v, str) else list(v)
        return "in.(" + ",".join('"' + str(x).replace('"', '\\"') + '"' for x in vals) + ")"
    f: List[Tuple[str, str]] = []
    if shape == "series":
        t, ent, var = "ts_utc", "entity", "variable"
    elif shape == "events":
        t, ent, var = "event_date", "source", "event_type"
    else:
        t, ent, var = "status_date", "entity_id", "entity_type"
    if entity is not None:
        vals = [entity] if isinstance(entity, str) else list(entity)
        if shape != "series":
            f.append((ent, lst(vals)))
        elif all(":" in v for v in vals):
            f.append(("entity", lst(vals)))
        elif not any(":" in v for v in vals):
            f.append(("node", lst(vals)))   # a node as the ISO writes it (HB_NORTH); a mix is filtered after the read
    if variable is not None:
        f.append((var, lst(variable)))
    if start is not None:
        f.append((t, "gte." + _utc_text(start)))
    if end is not None:
        f.append((t, "lt." + _utc_text(end)))
    return f
