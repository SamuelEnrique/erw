"""erw: a Python client for the Energy Research Warehouse (ERW).

The ERW is an open, harmonized energy data warehouse (in sustainability circles
"ERW" also means enhanced rock weathering; here it never does). Modeled on the
IRW's Python package, github.com/itemresponsewarehouse/Python-pkg.

    import erw
    erw.tables()                                   # every table, its shape, window and license verdict
    df = erw.fetch("eia_fuel_spot_prices", entity="eia:henry_hub", start="2025-01-01")
    df.attrs["erw"]["version_line"]                # what was read, from where, when
    erw.cite("eia_fuel_spot_prices")
    erw.license("eia_fuel_spot_prices")
    erw.standard("eia_fuel_spot_prices")
    df = erw.fetch("iso_dam_hub_prices", market="ercot_dam")
    df.attrs["erw"]["sources"]
    erw.filter(iso="ERCOT", market="rtm")
    erw.cite("iso_dam_hub_prices")

Session 536: the examples name today's tables; ercot_dam_hub_prices became the ercot_dam partition of
iso_dam_hub_prices in session 29 (warehouse/metadata/table_migrations.csv).
"""

__version__ = "0.1.0"

from .api import (  # noqa: E402
    cite,
    coverage,
    fetch,
    filter,
    get_backend,
    info,
    license,
    list_tables,
    migrations,
    requests,
    set_backend,
    sources,
    standard,
    tables,
    tier,
    version,
)
from .backends import Backend, ERWDataNotFound, ERWLicenseHeld, ERWLicenseWarning, LocalBackend  # noqa: E402
from .live import LiveBackend  # noqa: E402
from .remote import RedivisBackend, SupabaseBackend  # noqa: E402

# Session 1001 (docs/methods/packages.md): the six calls of the one specification are tables, coverage, fetch, cite,
# license and standard; requests counts the package's requests to Redivis and the live set.
__all__ = [
    "tables", "coverage", "fetch", "cite", "license", "standard", "requests",
    "info", "list_tables", "filter", "sources", "tier", "version", "migrations",
    "get_backend", "set_backend", "Backend", "LocalBackend", "ERWDataNotFound", "ERWLicenseHeld", "ERWLicenseWarning",
    "RedivisBackend", "SupabaseBackend", "LiveBackend",
]
