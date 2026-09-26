"""Remote backends must give the same answers as the local files (session 10).

Energy Research Warehouse (ERW). For five tables (one derived, one entities,
one events, two series), erw.fetch, filter, coverage, sources and cite through
RedivisBackend and SupabaseBackend must match LocalBackend. A backend whose
credentials are missing, or whose store is not reachable or not loaded, is
skipped with the reason; it never passes silently.

    python -m pytest package/tests/test_backends.py -v
"""

import pandas as pd
import pytest

import erw
from erw.api import _read

FIVE = ["ercot_peak_premium_annual",     # derived
        "eia860m_retired_generators",    # entities
        "news_index",                    # events
        "eia_fuel_spot_prices",          # series
        "fred_daily_spot_prices"]        # series
KEYS = {"ercot_peak_premium_annual": ["entity", "variable", "ts_utc"],
        "eia860m_retired_generators": ["entity_id"],
        "news_index": ["event_id"],
        "eia_fuel_spot_prices": ["entity", "variable", "ts_utc"],
        "fred_daily_spot_prices": ["entity", "variable", "ts_utc"]}


def _remote(kind):
    try:
        b = erw.RedivisBackend() if kind == "redivis" else erw.SupabaseBackend()
        missing = [t for t in FIVE if t not in b.list_tables()]
    except Exception as exc:
        pytest.skip(f"{kind} backend not available: {type(exc).__name__}: {str(exc)[:200]}")
    if missing:
        pytest.skip(f"{kind} backend lacks {missing} (not loaded)")
    return b


@pytest.fixture(scope="module", params=["redivis", "supabase"])
def remote(request):
    b = _remote(request.param)
    yield b
    erw.set_backend(erw.LocalBackend())


def _local():
    return erw.set_backend(erw.LocalBackend())


def _norm(df, name):
    d = df.copy()
    d = d[sorted(d.columns)].sort_values(KEYS[name]).reset_index(drop=True)
    d.attrs = {}
    return d


@pytest.mark.parametrize("name", FIVE)
def test_fetch_matches_local(remote, name):
    _local()
    loc = erw.fetch(name)
    erw.set_backend(remote)
    rem = erw.fetch(name)
    assert set(rem.columns) == set(loc.columns)
    pd.testing.assert_frame_equal(_norm(rem, name), _norm(loc, name), check_dtype=False)
    assert rem.attrs["erw"]["header"] == loc.attrs["erw"]["header"]


def test_coverage_matches_local(remote):
    _local()
    loc = erw.coverage().set_index("table").loc[FIVE]
    erw.set_backend(remote)
    rem = erw.coverage().set_index("table").loc[FIVE]
    pd.testing.assert_frame_equal(rem, loc, check_dtype=False)


@pytest.mark.parametrize("name", FIVE)
def test_sources_and_cite_match_local(remote, name):
    _local()
    s_loc, c_loc = erw.sources(name), erw.cite(name)
    erw.set_backend(remote)
    s_rem, c_rem = erw.sources(name), erw.cite(name)
    assert s_rem["reports"] == s_loc["reports"]
    assert s_rem["source_urls"] == s_loc["source_urls"]
    # the citation of the source and table is identical; the closing words name the
    # data version, which differs by design (a git commit locally, a Redivis version remotely)
    cut = " via the Energy Research Warehouse (ERW)"
    assert c_rem.split(cut)[0] == c_loc.split(cut)[0]
    assert f"table {name}" in c_rem


@pytest.mark.parametrize("query", [dict(sector="oil"), dict(sector="power"), dict(license="public"),
                                   dict(variable="spot_price"), dict(start="2026-01-01")])
def test_filter_matches_local_on_the_five(remote, query):
    _local()
    loc = set(erw.filter(**query)) & set(FIVE)
    erw.set_backend(remote)
    rem = set(erw.filter(**query)) & set(FIVE)
    assert rem == loc
