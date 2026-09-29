"""erw: a Python client for the Energy Research Warehouse (ERW).

The ERW is an open, harmonized energy data warehouse (in sustainability circles
"ERW" also means enhanced rock weathering; here it never does). Modeled on the
IRW's Python package, github.com/itemresponsewarehouse/Python-pkg.

    import erw
    erw.info()
    df = erw.fetch("ercot_dam_hub_prices")
    df.attrs["erw"]["sources"]
    erw.filter(iso="ERCOT", market="rtm")
    erw.cite("ercot_dam_hub_prices")
"""

__version__ = "0.1.0"

from .api import (  # noqa: E402
    cite,
    coverage,
    fetch,
    filter,
    get_backend,
    info,
    list_tables,
    migrations,
    set_backend,
    sources,
    tier,
    version,
)
from .backends import Backend, ERWDataNotFound, LocalBackend  # noqa: E402
from .remote import RedivisBackend, SupabaseBackend  # noqa: E402

__all__ = [
    "info", "list_tables", "coverage", "fetch", "filter", "sources", "cite", "tier", "version", "migrations",
    "get_backend", "set_backend", "Backend", "LocalBackend", "ERWDataNotFound",
    "RedivisBackend", "SupabaseBackend",
]
