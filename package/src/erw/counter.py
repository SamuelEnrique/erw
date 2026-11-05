"""Requests the package makes to Redivis and the live set, counted (session 1001, docs/methods/packages.md).

Energy Research Warehouse (ERW). erw.requests() returns the counts since the package was imported (or since
erw.requests(reset=True)), so a session can say how many requests it made. Redivis's requests are counted where its
client makes them (requests.request, wrapped once a Redivis backend is made); the live set's where this package makes
them (erw.live).
"""

from typing import Dict

_COUNTS: Dict[str, int] = {"redivis": 0, "live": 0}
_WRAPPED = False


def add(kind: str, n: int = 1) -> None:
    _COUNTS[kind] = _COUNTS.get(kind, 0) + n


def counts(reset: bool = False) -> Dict[str, int]:
    out = dict(_COUNTS)
    if reset:
        for k in _COUNTS:
            _COUNTS[k] = 0
    return out


def wrap_redivis() -> None:
    """Count every HTTP request whose address is Redivis's, whoever in this process makes it."""
    global _WRAPPED
    if _WRAPPED:
        return
    import requests
    inner = requests.request

    def counted(method, url, *args, **kwargs):
        if "redivis.com" in str(url):
            add("redivis")
        return inner(method, url, *args, **kwargs)

    requests.request = counted
    _WRAPPED = True
