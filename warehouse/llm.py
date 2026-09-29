"""The one way ERW code calls the Anthropic API, and the cost ledger every call writes to.

Energy Research Warehouse (ERW), session 30 (Part B1). Every script that calls a Claude model builds its
client here:

    import llm
    client = llm.client("news_score", log)       # the step, as the ledger names it
    resp = client.messages.create(...)             # the SDK's own call, unchanged

client() returns the Anthropic SDK's client wrapped so that messages.create records one row in
warehouse/output/api_cost_ledger.csv per call: run_id, session, step, model, input_tokens,
cached_input_tokens (cache reads), cache_write_tokens, output_tokens, web_searches, usd, ts_utc, the
request id and the date of the prices used. Everything else (models.list, the SDK's errors) is the SDK's.

Prices: warehouse/config/model_prices.yaml, the one place they live, with its date. A model not in it is
recorded with usd empty and a warning, never guessed.

The ledger is internal (never public): an events table, one row per call, license internal
(docs/methods/api_cost_ledger.md). It is written call by call, so a run that fails halfway still records
what it spent.

Environment:
  ERW_SESSION        the session number when a Claude Code session runs a step ("30"); unset, the ledger
                     says "daily" on GitHub and "local" elsewhere.
  ERW_RUN_ID         the run id to record (default: this process's start, YYYYMMDDTHHMMSSZ).
  ERW_SPEND_CAP_USD  a cap for the session: before each call, if the ledger's total for ERW_SESSION has
                     reached it, the call is refused (SpendCapReached) and nothing is sent.
  ERW_LEDGER         0 turns the ledger off (tests); the calls still go through.
"""

import datetime as dt
import os
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "api_cost_ledger"
PRICES_FILE = os.path.join(HERE, "config", "model_prices.yaml")
COLS = ["event_id", "event_date", "event_type", "currency", "source", "source_url", "run_id", "session", "step",
        "model", "input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "web_searches",
        "usd", "ts_utc", "prices_as_of", "request_id"]
SOURCE = "anthropic:messages-usage"
SOURCE_URL = "https://docs.anthropic.com/en/api/messages"
_START = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
_LOCK = threading.Lock()
_PRICES = None
_REGISTERED = False
REGISTRY = {"source": SOURCE, "publisher": "Anthropic", "report": "Messages API response usage (tokens per call)",
            "report_url": SOURCE_URL, "document_list": "https://docs.anthropic.com/en/docs/about-claude/pricing",
            "license": "internal", "tables": [NAME]}


class SpendCapReached(RuntimeError):
    """The session's ledger total reached ERW_SPEND_CAP_USD; no further model call is made."""


def prices():
    """{'as_of': date, 'models': {model: {input, output, cache_write_5m, cache_write_1h, cache_read}}, ...}."""
    global _PRICES
    if _PRICES is None:
        import yaml
        with open(PRICES_FILE, encoding="utf-8") as f:
            _PRICES = yaml.safe_load(f)
        _PRICES["as_of"] = str(_PRICES["as_of"])
    return _PRICES


def price_pair(model):
    """(input, output) USD per million tokens, or None: the pair the older cost lines use."""
    p = prices()["models"].get(model)
    return (p["input"], p["output"]) if p else None


def usage_numbers(usage):
    """The token counts of a response's usage, as plain ints (cache writes split by TTL where the API says)."""
    g = lambda o, k: int(getattr(o, k, 0) or 0)  # noqa: E731
    cw = g(usage, "cache_creation_input_tokens")
    cc = getattr(usage, "cache_creation", None)
    cw_1h = g(cc, "ephemeral_1h_input_tokens") if cc is not None else 0
    stu = getattr(usage, "server_tool_use", None)
    return {"input": g(usage, "input_tokens"), "output": g(usage, "output_tokens"),
            "cache_read": g(usage, "cache_read_input_tokens"), "cache_write": cw, "cache_write_1h": min(cw_1h, cw),
            "web_searches": g(stu, "web_search_requests") if stu is not None else 0}


def usd(model, n):
    """The cost of one call's usage numbers (usage_numbers) at the configured prices, or None."""
    cfg = prices()
    p = cfg["models"].get(model)
    if p is None:
        return None
    cw_5m = n["cache_write"] - n["cache_write_1h"]
    tokens = (n["input"] * p["input"] + n["output"] * p["output"] + n["cache_read"] * p["cache_read"]
              + cw_5m * p["cache_write_5m"] + n["cache_write_1h"] * p["cache_write_1h"]) / 1e6
    return tokens + n.get("web_searches", 0) * cfg.get("web_search_per_1k", 0) / 1000


def uncached_usd(model, n):
    """What the same call would have cost with no caching: every cached token billed as plain input."""
    m = dict(n, input=n["input"] + n["cache_read"] + n["cache_write"], cache_read=0, cache_write=0, cache_write_1h=0)
    return usd(model, m)


def session():
    s = os.environ.get("ERW_SESSION", "").strip()
    if s:
        return s
    return "daily" if os.environ.get("GITHUB_ACTIONS") == "true" else "local"


def ledger_path():
    return os.path.join(ip.OUT_DIR, NAME + ".csv")


def read_ledger():
    import pandas as pd
    path = ledger_path()
    if not os.path.exists(path):
        return pd.DataFrame(columns=COLS)
    return ip.read_series(path, COLS)


def session_total(name=None):
    """USD recorded in the ledger for one session (default: this process's)."""
    import pandas as pd
    df = read_ledger()
    df = df[df["session"] == (name or session())]
    return float(pd.to_numeric(df["usd"], errors="coerce").fillna(0).sum())


HEADER = [
    "Anthropic API cost ledger of the Energy Research Warehouse (ERW): one row per Messages API call made by "
    "ERW code (session 30, Part B1).",
    f"Source: {SOURCE}, the usage block of each Messages API response ({SOURCE_URL}): input, output, "
    "cache read and cache write tokens and web searches, as Anthropic reported them per call.",
    "usd: computed by warehouse/llm.py from those counts at the prices in warehouse/config/model_prices.yaml "
    "(its date is prices_as_of); empty when a model has no configured price. Method: docs/methods/api_cost_ledger.md.",
    "License: internal. Operating costs of the ERW, never shown on the public site or in the public Redivis dataset.",
    "Written by warehouse/llm.py, one row per call, at the time of the call.",
]


def record(step, model, resp_usage, request_id, log=None):
    """Append one call to the ledger; returns the row."""
    import pandas as pd
    n = usage_numbers(resp_usage)
    cost = usd(model, n)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_id = os.environ.get("ERW_RUN_ID", "").strip() or _START
    row = {"event_id": f"anthropic:{request_id or run_id + ':' + step + ':' + now}", "event_date": now,
           "event_type": "api_call", "currency": "USD", "source": SOURCE, "source_url": SOURCE_URL,
           "run_id": run_id, "session": session(), "step": step, "model": model,
           "input_tokens": str(n["input"]), "cached_input_tokens": str(n["cache_read"]),
           "cache_write_tokens": str(n["cache_write"]), "output_tokens": str(n["output"]),
           "web_searches": str(n["web_searches"]), "usd": "" if cost is None else f"{cost:.6f}", "ts_utc": now,
           "prices_as_of": prices()["as_of"], "request_id": request_id or ""}
    if cost is None:
        msg = f"llm: model {model} has no price in {os.path.relpath(PRICES_FILE, ROOT)}; ledger usd left empty"
        sys.stderr.write(msg + "\n")
        if log:
            log(msg)
    if os.environ.get("ERW_LEDGER", "1") == "0":
        return row
    global _REGISTERED
    with _LOCK:
        if not _REGISTERED:  # the source registry names the ledger's source, internal (once per process)
            ip.update_sources([REGISTRY])
            _REGISTERED = True
        quiet = log or (lambda m: None)
        stdout, sys.stdout = sys.stdout, open(os.devnull, "w")  # write_csv prints a summary line per write
        try:
            ip.write_csv(pd.DataFrame([row], columns=COLS), NAME, HEADER, quiet, cols=COLS, key=["event_id"],
                         time_col="event_date")
        finally:
            sys.stdout.close()
            sys.stdout = stdout
    return row


def check_cap():
    """Refuse a call once the session's ledger total reached ERW_SPEND_CAP_USD (when set)."""
    cap = os.environ.get("ERW_SPEND_CAP_USD", "").strip()
    if cap:
        spent = session_total()
        if spent >= float(cap):
            raise SpendCapReached(f"session {session()} has spent USD {spent:.4f}, at or over the cap "
                                  f"USD {float(cap):.2f} (ERW_SPEND_CAP_USD); no further model call")


class _Stream:
    """messages.stream(...), recorded in the ledger when the stream ends with its final message."""

    def __init__(self, owner, manager, model):
        self._owner, self._manager, self._model, self._stream = owner, manager, model, None

    def __enter__(self):
        self._stream = self._manager.__enter__()
        return self._stream

    def __exit__(self, *exc):
        if exc[0] is None:
            msg = self._stream.get_final_message()
            o = self._owner
            o.calls.append(record(o.step, getattr(msg, "model", None) or self._model, msg.usage,
                                  getattr(msg, "_request_id", None) or getattr(self._stream, "request_id", None),
                                  o.log))
        return self._manager.__exit__(*exc)


class _Messages:
    def __init__(self, owner):
        self._owner = owner
        self._inner = owner._client.messages

    def create(self, **kwargs):
        o = self._owner
        check_cap()
        resp = self._inner.create(**kwargs)
        row = record(o.step, getattr(resp, "model", None) or kwargs.get("model", ""), resp.usage,
                     getattr(resp, "_request_id", None), o.log)
        o.calls.append(row)
        return resp

    def stream(self, **kwargs):
        check_cap()
        return _Stream(self._owner, self._inner.stream(**kwargs), kwargs.get("model", ""))

    def __getattr__(self, name):  # count_tokens, batches, stream: the SDK's own
        return getattr(self._inner, name)


class LedgerClient:
    """The Anthropic client, with messages.create recorded in the ledger. .calls holds this client's rows."""

    def __init__(self, client, step, log=None):
        self._client, self.step, self.log, self.calls = client, step, log, []
        self.messages = _Messages(self)

    def __getattr__(self, name):
        return getattr(self._client, name)

    def spent(self):
        return sum(float(r["usd"] or 0) for r in self.calls)


def client(step, log=None, api_key=None, max_retries=None):
    """The one construction of the Anthropic client in ERW code (session 30). step names the ledger's step;
    max_retries, when given, replaces the SDK's default of 2 automatic retries."""
    import anthropic
    key = api_key or ip.load_key("ANTHROPIC_API_KEY", log)
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is empty")
    extra = {} if max_retries is None else {"max_retries": max_retries}
    return LedgerClient(anthropic.Anthropic(api_key=key, **extra), step, log)


def wrap(inner, step, log=None):
    """Wrap an already built client (a test's fake, for instance) so its calls are recorded too."""
    return inner if isinstance(inner, LedgerClient) else LedgerClient(inner, step, log)
