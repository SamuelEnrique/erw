"""The Stanford dataset through the Redivis backend must give the local files' answers (session 665, chain 043).

Energy Research Warehouse (ERW). Five public tables of the draft of Datapages's `erw:b9wm` (one derived, one entities,
one events, two series): fetch, coverage, sources and cite through RedivisBackend(owner="datapages", dataset="erw:b9wm",
owner_kind="organization") against LocalBackend, as test_backends.py does for the owner's account. news_index, the events
table of that file, is unsettled by its ERW verdict and not in the Stanford dataset; ercot_grid_notices stands in.

On 22 October 2026 Redivis refused every streamed read ("Cannot stream more than 100GB to external environments within a
30 day period", the token's user, since 15 October, session 305); the backend then reads the table's CSV export instead
(session 665), and two of the five tables were proven that way before the session's ceiling. The whole run:

    ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_stanford.py -v -m remote
"""

import pandas as pd
import pytest

import erw

pytestmark = pytest.mark.remote

FIVE = ["ercot_peak_premium_annual", "eia860m_retired_generators", "ercot_grid_notices", "eia_fuel_spot_prices",
        "eia_drilling_monthly"]
KEYS = {"ercot_peak_premium_annual": ["entity", "variable", "ts_utc"], "eia860m_retired_generators": ["entity_id"],
        "ercot_grid_notices": ["event_id"], "eia_fuel_spot_prices": ["entity", "variable", "ts_utc"],
        "eia_drilling_monthly": ["entity", "variable", "ts_utc"]}


@pytest.fixture(scope="module")
def stanford():
    try:
        b = erw.RedivisBackend(owner="datapages", dataset="erw:b9wm", owner_kind="organization")
        missing = [t for t in FIVE if t not in b.list_tables()]
        b.coverage()  # a read of rows: refused while Redivis's 30-day streaming cap stands
    except Exception as exc:
        pytest.skip(f"the Stanford draft is not readable here: {type(exc).__name__}: {str(exc)[:200]}")
    if missing:
        pytest.skip(f"the Stanford draft lacks {missing}")
    yield b
    erw.set_backend(erw.LocalBackend())


def _norm(df, name):
    d = df[sorted(df.columns)].sort_values(KEYS[name]).reset_index(drop=True)
    d.attrs = {}
    return d


@pytest.mark.parametrize("name", FIVE)
def test_fetch_matches_local(stanford, name):
    erw.set_backend(erw.LocalBackend())
    loc = erw.fetch(name)
    erw.set_backend(stanford)
    rem = erw.fetch(name)
    pd.testing.assert_frame_equal(_norm(rem, name), _norm(loc, name), check_dtype=False)
    assert rem.attrs["erw"]["header"] == loc.attrs["erw"]["header"]


@pytest.mark.parametrize("name", FIVE)
def test_cite_names_the_table(stanford, name):
    erw.set_backend(erw.LocalBackend())
    loc = erw.cite(name)
    erw.set_backend(stanford)
    rem = erw.cite(name)
    cut = " via the Energy Research Warehouse (ERW)"
    assert rem.split(cut)[0] == loc.split(cut)[0]
    assert f"table {name}" in rem


def test_filter_and_coverage_match_local(stanford):
    erw.set_backend(erw.LocalBackend())
    loc_cov = erw.coverage().set_index("table").loc[FIVE]
    loc_f = set(erw.filter(sector="oil")) & set(FIVE)
    erw.set_backend(stanford)
    pd.testing.assert_frame_equal(erw.coverage().set_index("table").loc[FIVE], loc_cov, check_dtype=False)
    assert set(erw.filter(sector="oil")) & set(FIVE) == loc_f
