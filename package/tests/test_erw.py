"""Tests of the erw client against the real tables in warehouse/output.

Energy Research Warehouse (ERW). No fixtures are invented: every assertion is
about the committed tables, docs/coverage.md and warehouse/metadata/coverage.csv.

    python -m pytest package/tests -v
"""

import re
from pathlib import Path

import pandas as pd
import collections
import functools

import pytest

import erw

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "warehouse" / "output"
COVERAGE_MD = ROOT / "docs" / "coverage.md"


def coverage_md_rows():
    """{table: rows} from the markdown table in docs/coverage.md."""
    lines = [ln for ln in COVERAGE_MD.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    t_col, r_col = header.index("Table"), header.index("Rows")
    out = {}
    for ln in lines[2:]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        out[cells[t_col].strip("`")] = int(cells[r_col].replace(",", ""))
    return out


TABLES = sorted(p.stem for p in OUTPUT.glob("*.csv"))
# Session 29: the ERCOT history is one table of about three million rows. The per-table tests below read every
# table whole, twice or more; this one is tested by partition instead (test_ercot_history_tables_are_complete_years,
# test_old_names_work_through_the_map), so a laptop never holds it whole several times over.
HISTORY = "ercot_all_hub_prices_history"


def _is_events(name):
    with open(OUTPUT / f"{name}.csv", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return line.startswith("event_id,")
    return False


def _is_entities(name):
    with open(OUTPUT / f"{name}.csv", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return line.startswith("entity_id,entity_type,")
    return False


EVENT_TABLES = [t for t in TABLES if _is_events(t)]
ENTITY_TABLES = [t for t in TABLES if _is_entities(t)]
SERIES_TABLES = [t for t in TABLES if t not in EVENT_TABLES and t not in ENTITY_TABLES]
# session 29: ERCOT's prices are in the consolidated tables (iso_*_hub_prices, the history)
ERCOT_DAM = sorted(t for t in ("iso_dam_hub_prices", HISTORY) if t in TABLES)
ERCOT_RTM = sorted(t for t in ("iso_rtm_hub_prices", HISTORY) if t in TABLES)
MD_ROWS = coverage_md_rows()
# Session 33: every table over 200,000 rows (the ERCOT history, eia930_all_emissions) is tested by partition
# (test_large_table_by_partition: ba, or market and year), never loaded whole, so the suite fits a laptop and the
# workflow's test step stays fast. The per-table tests below take the other tables.
LARGE_ROWS = 200_000
LARGE = sorted(t for t in TABLES if MD_ROWS.get(t, 0) > LARGE_ROWS or t == HISTORY)
PER_TABLE = [t for t in TABLES if t not in LARGE]


@pytest.fixture(autouse=True)
def default_backend():
    erw.set_backend()
    yield
    erw.set_backend()


def test_list_tables_is_every_output_file():
    assert erw.list_tables() == TABLES
    assert len(TABLES) >= 1


def test_coverage_has_one_row_per_table_and_the_documented_columns():
    cov = erw.coverage()
    assert list(cov.columns) == ["table", "iso", "market", "n_nodes", "interval", "ts_min",
                                 "ts_max", "n_rows", "source_report", "last_run",
                                 "validator_status", "license", "sector", "derived", "tier"]  # tier: session 28
    assert set(cov["license"]) <= {"public", "internal"}
    assert sorted(cov["table"]) == TABLES
    assert str(cov["ts_min"].dtype).startswith("datetime64") and cov["ts_min"].dt.tz is not None
    assert (cov["validator_status"] == "pass").all()


def test_coverage_md_lists_every_table():
    assert sorted(MD_ROWS) == TABLES


@pytest.mark.parametrize("name", PER_TABLE)
def test_fetch_row_count_matches_coverage_md(name):
    df = erw.fetch(name)
    assert len(df) == MD_ROWS[name]


@pytest.mark.parametrize("name", [t for t in SERIES_TABLES if t not in LARGE])
def test_fetch_types_and_provenance(name):
    df = erw.fetch(name)
    assert list(df.columns[:4]) == ["entity", "variable", "ts_utc", "value"]
    assert str(df["ts_utc"].dtype) == "datetime64[ns, UTC]"
    assert df["value"].dtype == float
    assert not df.duplicated(["entity", "variable", "ts_utc"]).any()
    meta = df.attrs["erw"]
    assert meta["table"] == name
    # session 29: a derived table (the trader view's snapshots) names its inputs, not a connector run log
    derived = erw.coverage().set_index("table").loc[name, "derived"] == "yes"
    assert meta["title"] and meta["retrieved"] and (meta["run_log"] or derived)
    assert meta["sources"] and all(s["source"] in set(df["source"]) or s["report_url"]
                                   for s in meta["sources"])
    assert meta["header"][0].startswith("Energy Research Warehouse (ERW):")


def test_fetch_list_returns_dict():
    names = TABLES[:3]
    got = erw.fetch(names)
    assert isinstance(got, dict) and list(got) == names
    assert all(len(got[n]) == MD_ROWS[n] for n in names)


def test_fetch_unknown_table_fails_loudly():
    with pytest.raises(erw.ERWDataNotFound):
        erw.fetch("no_such_table_prices")


def test_filter_by_iso_market_variable_node_and_time():
    cov = erw.coverage()
    ercot = sorted(cov.loc[cov["iso"] == "ERCOT", "table"])
    # session 29: a consolidated table lists its members' ISOs and markets, separated by ";"
    has = lambda col, f: cov[col].map(lambda v: any(f(p) for p in str(v).split(";")))  # noqa: E731
    assert erw.filter(iso="ercot") == sorted(cov.loc[has("iso", lambda p: p == "ERCOT"), "table"])
    # session 30: the price board's derived tables (price_board_*) carry the markets they are computed from
    board = lambda m: [t for t in cov["table"] if t.startswith("price_board_")  # noqa: E731
                       and m in str(cov.set_index("table").loc[t, "market"]).split(";")]
    assert erw.filter(iso="ERCOT", market="dam") == sorted(ERCOT_DAM + board("ercot_dam"))  # the live DAM table, history
    # the live table, the history and the derived peak-premium tables (session 9), and the price board's (session 30)
    assert erw.filter(market="ercot_rtm") == sorted(ERCOT_RTM + [t for t in TABLES if t.startswith("ercot_peak_premium_")]
                                                    + board("ercot_rtm"))
    assert set(erw.filter(market="rtm")) == set(cov.loc[has("market", lambda p: p.endswith("_rtm")), "table"])
    assert erw.filter(variable="spp_rtm") == ERCOT_RTM
    ercot_prices = sorted(cov.loc[has("market", lambda p: p.startswith("ercot_")), "table"])
    # session 30: two price board tables hold each ISO's main hub only (HB_HUBAVG), not every hub
    ercot_prices = [t for t in ercot_prices if t not in ("price_board_peak_offpeak", "price_board_spreads")]
    # session 29: the price tables, and the derived tables computed from them per hub (the trader view)
    derived = set(cov.loc[cov["derived"] == "yes", "table"])
    for n in ("HB_NORTH", "ercot:HB_NORTH"):
        got = erw.filter(node=n)
        assert set(ercot_prices) <= set(got) and set(got) - set(ercot_prices) <= derived
    nyc = erw.filter(iso=["ERCOT", "NYISO"], node="N.Y.C.")
    want = set(cov.loc[has("market", lambda p: p.startswith("nyiso_")), "table"])
    assert want <= set(nyc) and set(nyc) - want <= derived
    eia_ciso = sorted(t for t in ("eia930_all_demand", "eia930_all_generation") if t in TABLES)  # session 29
    got = set(erw.filter(node="eia930:CISO"))  # session 29: also the snapshot of every BA's latest hours
    # session 32: the CO2 estimates and the carbon intensity tables name each BA too
    also = {"eia930_generation_latest"} | {t for t in TABLES if t.startswith(("eia930_all_", "carbon_intensity_"))}
    assert set(eia_ciso) <= got and got - set(eia_ciso) <= also
    assert set(eia_ciso) <= set(erw.filter(iso="caiso"))
    spot = [t for t in ("eia_fuel_spot_prices", "eia_product_spot_prices", "fred_daily_spot_prices")
            if t in TABLES]
    if spot:
        assert erw.filter(variable="spot_price") == spot
    assert erw.filter(start="1900-01-01", end="1900-01-02") == []  # before any table starts (imports: 1920)
    last = cov["ts_max"].max()
    assert set(erw.filter(start=last)) == set(cov.loc[cov["ts_max"] >= last, "table"])
    assert erw.filter() == TABLES


@pytest.mark.parametrize("name", PER_TABLE)
def test_sources_names_reports_and_every_row_url(name):
    s = erw.sources(name)
    df = erw.fetch(name)
    assert s["table"] == name
    assert {r["source"] for r in s["reports"]} == set(df["source"]) | {
        r["source"] for r in df.attrs["erw"]["sources"]}
    assert s["source_urls"] == sorted(set(df["source_url"]))
    assert all(u.startswith("http") for u in s["source_urls"])


@pytest.mark.parametrize("name", [t for t in SERIES_TABLES if t not in LARGE])
def test_cite_names_the_iso_the_table_and_the_commit(name):
    c = erw.cite(name)
    org = name.split("_")[0]
    derived = erw.coverage().set_index("table").loc[name, "derived"] == "yes"
    members = sorted(o for o, (n, _) in erw.migrations().items() if n == name)
    org = members[0].split("_")[0] if members else org  # session 29: a consolidated table, its first member's publisher
    publisher = "Energy Research Warehouse (ERW), derived" if derived else {
                 "ercot": "Electric Reliability Council of Texas", "caiso": "California",
                 "nyiso": "New York", "miso": "Midcontinent", "spp": "Southwest Power Pool",
                 "isone": "ISO New England", "pjm": "PJM",
                 "eia930": "Energy Information Administration",
                 "eia": "Energy Information Administration",
                 "carb": "California Air Resources Board",
                 "rggi": "Regional Greenhouse Gas Initiative",
                 "fred": "Federal Reserve Bank of St. Louis",
                 "portwatch": "International Monetary Fund",
                 "weather": "National Weather Service"}[org]  # session 29: derived tables and weather
    assert publisher in c and name in c and "Energy Research Warehouse (ERW)" in c
    commit = erw.version()["data_commit"]
    assert commit and commit[:12] in c


def test_version_reports_the_data_commit():
    v = erw.version()
    assert v["backend"] == "local"
    assert re.fullmatch(r"[0-9a-f]{40}", v["data_commit"])
    assert v["package_version"] == erw.__version__
    assert Path(v["data_dir"]) == OUTPUT.resolve()


def test_info_summary_and_table(capsys):
    d = erw.info()
    assert d["n_tables"] == len(TABLES)
    assert d["n_rows"] == sum(MD_ROWS.values())
    assert "Energy Research Warehouse (ERW)" in capsys.readouterr().out
    t = erw.info(TABLES[0], quiet=True)
    assert t["rows"] == MD_ROWS[TABLES[0]]
    assert capsys.readouterr().out == ""


def test_erw_data_dir_env_is_used(monkeypatch):
    monkeypatch.setenv("ERW_DATA_DIR", str(OUTPUT))
    erw.set_backend()
    assert erw.get_backend().data_dir == OUTPUT.resolve()
    monkeypatch.setenv("ERW_DATA_DIR", str(OUTPUT / "no_such_dir"))
    with pytest.raises(erw.ERWDataNotFound):
        erw.set_backend()


def test_public_functions_only_use_the_backend_interface():
    """A new backend needs only the Backend methods: here, one wrapping the local files."""
    calls = []

    class Wrapped(erw.Backend):
        name = "wrapped"

        def __init__(self):
            self.inner = erw.LocalBackend(str(OUTPUT))

        def list_tables(self):
            calls.append("list_tables")
            return self.inner.list_tables()

        def read_table(self, name):
            calls.append("read_table")
            return self.inner.read_table(name)

        def coverage(self):
            calls.append("coverage")
            return self.inner.coverage()

        def source_registry(self):
            calls.append("source_registry")
            return self.inner.source_registry()

        def version(self):
            calls.append("version")
            return {"backend": self.name, "data_commit": None}

        def describe(self):
            return "wrapped local files"

    erw.set_backend(Wrapped())
    # a table whose name starts with its ISO (session 30: the first table by name, api_cost_ledger, has none)
    name = next(t for t in TABLES if t.split("_")[0] in ("caiso", "ercot", "isone", "miso", "nyiso", "spp", "pjm"))
    assert erw.list_tables() == TABLES
    assert len(erw.fetch(name)) == MD_ROWS[name]
    assert name in erw.filter(iso=name.split("_")[0])
    assert erw.sources(name)["table"] == name
    assert "Energy Research Warehouse (ERW)" in erw.cite(name)
    assert erw.version()["backend"] == "wrapped"
    assert {"list_tables", "read_table", "coverage", "version", "source_registry"} <= set(calls)


# --- session 5 rulings -------------------------------------------------------

def test_fetch_subsets_rows_by_time_and_node():
    full = erw.fetch("ercot_rtm_hub_prices")
    t0 = full["ts_utc"].min() + pd.Timedelta(days=2)
    t1 = t0 + pd.Timedelta(days=1)
    sub = erw.fetch("ercot_rtm_hub_prices", start=t0, end=t1, node="HB_NORTH")
    expected = full[(full["ts_utc"] >= t0) & (full["ts_utc"] < t1) & (full["node"] == "HB_NORTH")]
    assert len(sub) == len(expected) == 96  # one day of 15-minute intervals, one hub
    assert set(sub["node"]) == {"HB_NORTH"}
    assert sub.attrs["erw"]["subset"]["node"] == ["HB_NORTH"]
    both = erw.fetch("ercot_rtm_hub_prices", node=["ercot:HB_NORTH", "HB_WEST"])
    assert set(both["node"]) == {"HB_NORTH", "HB_WEST"}
    naive = erw.fetch("ercot_rtm_hub_prices", start=t0.tz_convert(None), end=t1.tz_convert(None))
    assert len(naive) == len(full[(full["ts_utc"] >= t0) & (full["ts_utc"] < t1)])
    many = erw.fetch(["ercot_dam_hub_prices", "ercot_rtm_hub_prices"], node="HB_WEST")
    assert all(set(d["node"]) == {"HB_WEST"} for d in many.values())


def test_license_column_and_filter():
    cov = erw.coverage()
    public = sorted(cov.loc[cov["license"] == "public", "table"])
    internal = sorted(cov.loc[cov["license"] == "internal", "table"])
    assert erw.filter(license="public") == public
    assert erw.filter(license="internal") == internal
    # the rule: a license the table declares in its header ("License: public|internal")
    # wins; otherwise a table is internal exactly when one of its sources is internal
    reg = erw.get_backend().source_registry().set_index("source")["license"]
    for t in TABLES:
        srcs, header = _sources_and_header(t)  # session 33: a large table by partition
        declared = [h.split(":", 1)[1].strip().split(".")[0].split()[0]
                    for h in header if h.startswith("License:")]
        expect = declared[0] if declared else (
            "internal" if any(reg[s] == "internal" for s in srcs) else "public")
        assert cov.set_index("table").loc[t, "license"] == expect, t
    if "news_index" in TABLES:
        assert cov.set_index("table").loc["news_index", "license"] == "public"
        assert cov.set_index("table").loc["news_stories", "license"] == "internal"
    assert all(not t.startswith("pjm_") for t in public)


@pytest.mark.parametrize("name", EVENT_TABLES)
def test_events_table_types_subset_and_provenance(name):
    df = erw.fetch(name)
    assert list(df.columns[:3]) == ["event_id", "event_date", "event_type"]
    assert str(df["event_date"].dtype) == "datetime64[ns, UTC]"
    assert df["event_id"].is_unique
    assert df["source_url"].str.startswith("http").all()
    meta = df.attrs["erw"]
    assert meta["header"][0].startswith("Energy Research Warehouse (ERW):") and meta["run_log"]
    t1 = df["event_date"].max()
    t0 = t1 - pd.Timedelta(hours=6)
    sub = erw.fetch(name, start=t0, end=t1 + pd.Timedelta(seconds=1))
    assert len(sub) == ((df["event_date"] >= t0) & (df["event_date"] <= t1)).sum()
    outlet = df["source"].iloc[0]
    assert set(erw.fetch(name, node=outlet)["source"]) == {outlet}
    assert name in erw.filter(variable=df["event_type"].iloc[0])
    if "significance" in df.columns:
        s = df["significance"].dropna()
        assert s.between(0, 10).all()
    c = erw.cite(name)
    assert "Energy Research Warehouse (ERW)" in c and name in c


def test_source_registry_covers_every_source_in_every_table():
    reg = erw.get_backend().source_registry()
    assert reg["source"].is_unique
    registered = set(reg["source"])
    for name in TABLES:
        assert _sources_and_header(name)[0] <= registered, name  # session 33: a large table by partition


def test_cite_names_every_report_even_from_earlier_runs():
    """The gap session 4 found: rows kept from an earlier run keep their report's title."""
    df = erw.fetch("ercot_rtm_hub_prices")
    reg = erw.get_backend().source_registry().set_index("source")
    c = erw.cite("ercot_rtm_hub_prices")
    for sid in set(df["source"]):
        assert reg.loc[sid, "report"] and reg.loc[sid, "report"] in c
    assert all(r["report"] for r in erw.sources("ercot_rtm_hub_prices")["reports"])


# --- session 7: the price board ---------------------------------------------

SECTORS = list(erw.api.SECTORS)  # session 29: the package's list (deals and datacenters since sessions 15 and 16)

# table -> (units, freqs, license, sectors, entity prefix); every session 7 table
PRICE_BOARD = {
    "eia_product_spot_prices": ({"USD/gal"}, {"P1D"}, "public", "products", "eia:EER_"),
    "eia_retail_fuel_prices": ({"USD/gal"}, {"P1W"}, "public", "products", "eia:EM"),
    "eia_petroleum_trade_weekly": ({"kbbl/d"}, {"P1W"}, "public", "oil;products", "eia:W"),
    "eia_petroleum_stocks_weekly": ({"kbbl"}, {"P1W"}, "public", "oil;products", "eia:W"),
    "eia_lng_exports_monthly": ({"MMcf", "USD/Mcf"}, {"P1M"}, "public", "lng", "eia:NGM_EPG0_"),
    "pjm_rpm_capacity_prices": ({"USD/MW-day"}, {"P1Y"}, "internal", "capacity", "pjm:"),
    "carb_auction_allowance_prices": ({"USD/tCO2", "count"}, {"P3M"}, "internal", "carbon", "carb:"),
    "rggi_auction_allowance_prices": ({"USD/short_ton", "count"}, {"P3M"}, "internal", "carbon", "rggi:"),
    "fred_daily_spot_prices": ({"USD/bbl", "USD/MMBtu"}, {"P1D"}, "public", "oil;gas", "fred:"),
    "fred_imf_commodity_prices": ({"USD/MMBtu", "USD/t", "USD/lb"}, {"P1M"}, "internal",
                                  "gas;lng;coal;uranium;metals", "fred:"),
    # session 8
    "eia_crude_first_purchase_prices": ({"USD/bbl"}, {"P1M"}, "public", "oil", "eia:F00"),
    "eia_crude_imports_by_country": ({"kbbl/d"}, {"P1M"}, "public", "oil", "eia:"),
    "eia_padd_crude_pipeline_flows": ({"kbbl"}, {"P1M"}, "public", "oil", "eia:MCRMP"),
    "eia_retail_electricity_prices": ({"USD/MWh"}, {"P1M"}, "public", "power", "eia:retail_price:"),
    "portwatch_chokepoint_transits": ({"count", "dwt"}, {"P1D"}, "internal", "oil;lng", "portwatch:chokepoint"),
}


def test_every_price_board_table_is_present():
    assert set(PRICE_BOARD) <= set(TABLES)


@pytest.mark.parametrize("name", sorted(PRICE_BOARD))
def test_price_board_table_units_freq_license_sector(name):
    units, freqs, license_, sectors, prefix = PRICE_BOARD[name]
    df = erw.fetch(name)
    assert set(df["unit"]) == units
    assert set(df["freq"]) == freqs
    assert df["entity"].str.startswith(prefix).all()
    assert (df["ts_utc"].dt.strftime("%H:%M:%S") == "00:00:00").all()
    row = erw.coverage().set_index("table").loc[name]
    assert row["license"] == license_ and row["sector"] == sectors
    assert name in erw.filter(sector=sectors.split(";")[0])


def test_price_board_spot_checks_against_the_sources():
    """Values read by hand from the source files on 2026-09-25."""
    def one(name, entity, variable, ts):
        df = erw.fetch(name)
        v = df[(df["entity"] == entity) & (df["variable"] == variable)
               & (df["ts_utc"] == pd.Timestamp(ts, tz="UTC"))]["value"]
        assert len(v) == 1, (name, entity, ts)
        return float(v.iloc[0])
    if "pjm_rpm_capacity_prices" in TABLES:  # PJM workbook: RTO 2007/08 $40.80, 2028/29 $325.00
        assert one("pjm_rpm_capacity_prices", "pjm:RTO", "capacity_price_usd_per_mw_day", "2007-06-01") == 40.8
        assert one("pjm_rpm_capacity_prices", "pjm:RTO", "capacity_price_usd_per_mw_day", "2028-06-01") == 325.0
    if "rggi_auction_allowance_prices" in TABLES:  # RGGI: Auction 1 $3.07, Auction 73 $37.65
        assert one("rggi_auction_allowance_prices", "rggi:current_auction", "clearing_price", "2008-09-25") == 3.07
        assert one("rggi_auction_allowance_prices", "rggi:current_auction", "clearing_price", "2026-09-09") == 37.65
    if "carb_auction_allowance_prices" in TABLES:  # CARB PDF: August 2026 current $32.48, advance $32.75
        assert one("carb_auction_allowance_prices", "carb:current_auction", "settlement_price", "2026-08-01") == 32.48
        assert one("carb_auction_allowance_prices", "carb:advance_auction", "settlement_price", "2026-08-01") == 32.75


def test_sector_filter():
    cov = erw.coverage()
    assert all(set(v.split(";")) <= set(SECTORS) for v in cov["sector"])
    for s in SECTORS:
        want = sorted(cov.loc[cov["sector"].map(lambda v: s in v.split(";")), "table"])
        assert erw.filter(sector=s) == want, s
    assert erw.filter(sector=["carbon", "capacity"]) == sorted(
        erw.filter(sector="carbon") + erw.filter(sector="capacity"))
    iso_prices = [t for t in TABLES if re.match(r"^[a-z]+_(dam|rtm)_", t)]
    assert set(iso_prices) <= set(erw.filter(sector="power"))
    # session 29: the policy tables (session 24) are in the news sector too
    assert {t for t in TABLES if t.startswith("news_")} <= set(erw.filter(sector="news"))
    assert erw.filter(sector="equities") == []  # no equities table yet (archive/sessions/SESSION_7_REPORT.md)
    with pytest.raises(ValueError):
        erw.filter(sector="crypto")


# --- session 8: entities, ERCOT history, monthly series ----------------------

ENTITY_STATUS = {"operating", "planned", "under_construction", "retired", "withdrawn", "active",
                 "completed", "suspended", ""}
QUEUES = {"ercot", "caiso", "nyiso", "miso", "spp", "isone"}


def test_every_session8_entities_table_is_present():
    want = {"eia860m_operating_generators", "eia860m_planned_generators", "eia860m_retired_generators"}
    want |= {f"{i}_interconnection_queue" for i in QUEUES}
    assert want <= set(ENTITY_TABLES)


@pytest.mark.parametrize("name", ENTITY_TABLES)
def test_entities_table_types_provenance_and_rules(name):
    df = erw.fetch(name)
    assert list(df.columns[:2]) == ["entity_id", "entity_type"]
    assert df["entity_id"].is_unique and df["entity_id"].str.contains(":").all()
    assert len(df) == MD_ROWS[name]
    assert df["lat"].dtype == float and df["capacity_mw"].dtype == float
    assert df["lat"].dropna().between(-90, 90).all() and df["lon"].dropna().between(-180, 180).all()
    assert str(df["status_date"].dtype).startswith("datetime64")
    assert set(df["status"].fillna("")) <= ENTITY_STATUS
    assert df["source_url"].str.startswith("http").all()
    meta = df.attrs["erw"]
    row = erw.coverage().set_index("table").loc[name]
    # session 29: derived and model-extracted entities tables (datacenters, companies) have no connector run log
    assert meta["header"][0].startswith("Energy Research Warehouse (ERW):") and (meta["run_log"] or row["tier"] != "source")
    sectors = row["sector"].split(";")
    assert row["interval"] == "snapshot" and set(sectors) <= {"power", "datacenters", "deals"} and row["license"] == "public"
    assert name in erw.filter(sector=sectors[0])
    one = df["entity_id"].iloc[0]
    assert erw.fetch(name, node=one)["entity_id"].tolist() == [one]
    c = erw.cite(name)
    assert "Energy Research Warehouse (ERW)" in c and name in c
    assert erw.info(name, quiet=True)["shape"] == "entities"


def test_eia860m_tables_one_vintage_and_the_right_statuses():
    op, pl, rt = (erw.fetch(f"eia860m_{k}_generators") for k in ("operating", "planned", "retired"))
    vintages = set(op["vintage"]) | set(pl["vintage"]) | set(rt["vintage"])
    assert len(vintages) == 1 and re.fullmatch(r"\d{4}-\d{2}", vintages.pop())
    assert set(op["status"]) == {"operating"} and set(op["eia_status"]) <= {"OP", "SB", "OA", "OS"}
    assert set(pl["status"]) <= {"planned", "under_construction"}
    assert set(rt["status"]) == {"retired"}
    year = int(op["vintage"].iloc[0][:4])
    assert set(rt["retirement_date"].dt.year) <= {year, year - 1}
    assert (op["entity_type"] == "generator").all()
    assert not (set(op["entity_id"]) & set(pl["entity_id"]))  # a generator is in one inventory
    # a label wherever EIA gives the code (EIA leaves a few technologies blank)
    for code, label in (("technology", "technology_group"), ("prime_mover", "prime_mover_label"),
                        ("energy_source", "energy_source_label")):
        assert ((op[code] == "") | (op[label] != "")).all(), code


@pytest.mark.parametrize("iso", sorted(QUEUES))
def test_queue_harmonized_status_keeps_the_iso_status(iso):
    df = erw.fetch(f"{iso}_interconnection_queue")
    assert set(df["status"].fillna("")) <= {"active", "withdrawn", "completed", "suspended", ""}
    # the ISO's own status is kept beside the harmonized one, and maps one way
    pairs = df.groupby("iso_status")["status"].nunique()
    assert (pairs <= 1).all()
    assert len(df) > 1000
    # a withdrawn position's status_date is its withdrawn date, where the ISO gives one
    w = df[(df["status"] == "withdrawn") & df["withdrawn_date"].notna()]
    assert (w["status_date"] == w["withdrawn_date"]).all()


def test_ercot_history_tables_are_complete_years():
    """35,040 quarter hours per hub per year (35,136 in a leap year); 8,760 or 8,784 hours."""
    hubs = {"HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HOUSTON", "HB_BUSAVG", "HB_HUBAVG"}
    this_year = pd.Timestamp.now(tz="America/Chicago").year
    # session 29: one table, ercot_all_hub_prices_history, partitioned by market and year (operating year)
    _needs(HISTORY)
    # session 33: the rows per (market, year, node) and the last interval per (market, year), from one streamed pass
    sc = _scan(HISTORY)
    for m in ("rtm", "dam"):
        years = sorted(int(y) for (mk, y) in sc["counts"] if mk == f"ercot_{m}")
        assert years[0] == 2015 and years[-1] == this_year
        live = erw.fetch(f"iso_{m}_hub_prices", market=f"ercot_{m}")
        for y in years:
            leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
            n = (35136 if leap else 35040) if m == "rtm" else (8784 if leap else 8760)
            per = {node: c for (mk, yr, node), c in sc["nodes"].items() if mk == f"ercot_{m}" and yr == str(y)}
            assert set(per) == hubs
            if y < this_year:
                assert all(c == n for c in per.values()), (m, y, per)
            else:  # the current year stops where the live table starts
                last = pd.Timestamp(sc["last"][(f"ercot_{m}", str(y))])
                assert last < live["ts_utc"].min()
                step = pd.Timedelta("15min" if m == "rtm" else "1h")
                assert last + step == live["ts_utc"].min()


def test_old_names_work_through_the_map():
    """Session 29: an old table name reads its rows from the consolidated table, with its own columns and header,
    and a DeprecationWarning, until the first monthly release (docs/migrations/2026-09-29-consolidation.md)."""
    for old, new, part in (("eia930_ciso_demand", "eia930_all_demand", {"ba": "ciso"}),
                           ("ercot_trader_daily", "iso_trader_daily", {"market": "ercot"}),
                           ("ercot_rtm_hub_prices", "iso_rtm_hub_prices", {"market": "ercot_rtm"})):
        with pytest.warns(DeprecationWarning, match=new):
            o = erw.fetch(old)
        n = erw.fetch(new, **part)
        assert len(o) == len(n) > 0
        assert "ba" not in o.columns and o.attrs["erw"]["migrated_to"] == new
        assert o.attrs["erw"]["title"] and o.attrs["erw"]["title"] != n.attrs["erw"]["title"]
        assert "formerly " + old in erw.cite(old)
    assert old not in erw.list_tables() and new in erw.list_tables()


# --- session 9: derived tables -----------------------------------------------

DERIVED = ["ercot_peak_premium_annual", "ercot_peak_premium_monthly"]
# the human's thesis values for HB_HUBAVG (archive/sessions/SESSION_9_PROMPT.md), 2015 and 2025
THESIS = {"all_median": (20.49, 25.68), "all_p999": (583.96, 311.80),
          "peak_iqr": (7.64, 34.12), "midday_min": (-3.98, -18.25)}


def test_derived_tables_flag_license_and_inputs():
    cov = erw.coverage().set_index("table")
    assert set(cov["derived"]) <= {"yes", "no"}
    # session 29: the peak premium was the first derived table; every derived table names its inputs
    assert set(DERIVED) <= set(cov.index[cov["derived"] == "yes"])
    for name in [n for n in cov.index[cov["derived"] == "yes"] if n in TABLES]:
        header = erw.fetch(name).attrs["erw"]["header"]
        assert any(h.startswith("Derived from:") for h in header), name
        assert "Energy Research Warehouse (ERW), derived" in erw.cite(name)
    for name in [d for d in DERIVED if d in TABLES]:  # session 29: absent on the GitHub runner
        df = erw.fetch(name)
        header = df.attrs["erw"]["header"]
        inputs = [t.strip() for h in header if h.startswith("Derived from:")
                  for t in h.split(":", 1)[1].split(";")]
        assert "ercot_rtm_hub_prices" in inputs and "ercot_rtm_hub_prices_2015" in inputs
        # session 29: an input named by its old name is read as the consolidated table it moved into
        want = "internal" if any(cov.loc[erw.api._current(t), "license"] == "internal" for t in inputs) else "public"
        assert cov.loc[name, "license"] == want == "public"
        assert set(df["source"]) == {"erw:ercot_peak_premium"}
        assert df["source_url"].str.endswith("docs/methods/ercot_peak_premium.md").all()
        assert set(df["entity"]) == {f"ercot:{h}" for h in ("HB_NORTH", "HB_SOUTH", "HB_WEST",
                                                              "HB_HOUSTON", "HB_BUSAVG", "HB_HUBAVG")}
        assert "Energy Research Warehouse (ERW), derived" in erw.cite(name)


def _layout(name):
    path = OUTPUT / f"{name}.csv"
    with open(path, encoding="utf-8") as f:
        skip, header = 0, []
        for line in f:
            if not line.startswith("#"):
                cols = line.strip().split(",")
                break
            header.append(line[1:].strip())
            skip += 1
    return path, skip, cols, header


@functools.lru_cache(maxsize=None)
def _scan(name):
    """Session 33: one streamed pass over a large table, reading only the columns the tests need: the rows per
    partition (ba, or market and year, or market), the row sources, whether every source_url is http, and for a table
    partitioned by year the rows per (market, year, node) and the last ts_utc per (market, year). Cached: each large
    file is read once per test session, never whole."""
    import pyarrow as pa
    import pyarrow.csv as pcsv
    path, skip, cols, header = _layout(name)
    keys = ["ba"] if "ba" in cols else (["market", "year"] if "year" in cols else ["market"])
    extra = ["node", "ts_utc"] if "year" in keys else []
    want = keys + ["source", "source_url"] + extra
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=skip, block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=want,
                                                               column_types={c: pa.string() for c in want}))
    counts, nodes, last, sources, bad_url = collections.Counter(), collections.Counter(), {}, set(), 0
    for batch in reader:
        df = batch.to_pandas()
        counts.update({(k if isinstance(k, tuple) else (k,)): v for k, v in df.groupby(keys).size().items()})
        sources |= set(df["source"])
        bad_url += int((~df["source_url"].str.startswith("http")).sum())
        if extra:
            nodes.update(df.groupby(["market", "year", "node"]).size().to_dict())
            for k, v in df.groupby(["market", "year"])["ts_utc"].max().items():
                last[k] = max(last.get(k, v), v)
        del df
    return {"keys": keys, "counts": dict(counts), "sources": sources, "bad_url": bad_url, "nodes": dict(nodes),
            "last": last, "header": header}


def _partitions(name):
    """Session 33: the partitions of a large table, [{column: value}], from one streamed pass (_scan)."""
    sc = _scan(name)
    return [dict(zip(sc["keys"], k)) for k in sorted(sc["counts"])]


@pytest.mark.parametrize("name", LARGE)
def test_large_table_by_partition(name):
    """Session 33: what the per-table tests check, without loading the table whole: the rows of every partition add
    up to coverage's count, every source is registered and every source_url is http (one streamed pass), and the first
    and last partitions, read through erw.fetch, have the series shape, UTC times, float values, unique keys and the
    ERW's provenance header."""
    _needs(name)
    sc = _scan(name)
    assert sum(sc["counts"].values()) == MD_ROWS[name]
    assert sc["bad_url"] == 0
    assert sc["sources"] <= set(erw.get_backend().source_registry()["source"])
    parts = _partitions(name)
    for p in (parts[0], parts[-1]):
        df = erw.fetch(name, **p)
        assert len(df) == sc["counts"][tuple(p[k] for k in sc["keys"])], p
        assert list(df.columns[:4]) == ["entity", "variable", "ts_utc", "value"]
        assert str(df["ts_utc"].dtype) == "datetime64[ns, UTC]"
        assert df["value"].dtype == float
        assert not df.duplicated(["entity", "variable", "ts_utc"]).any(), p
        meta = df.attrs["erw"]
        assert meta["header"][0].startswith("Energy Research Warehouse (ERW):") and meta["retrieved"]
        del df


def _sources_and_header(name):
    """Session 33: (the set of row sources, the header lines) of a table; a large table from one streamed pass."""
    if name not in LARGE:
        df = erw.fetch(name)
        return set(df["source"]), df.attrs["erw"]["header"]
    sc = _scan(name)
    return sc["sources"], sc["header"]


def _needs(*names):
    """Session 29: the GitHub runner never holds the ERCOT yearly history or the tables derived from it."""
    missing = [n for n in names if n not in TABLES]
    if missing:
        pytest.skip(f"not in this machine's warehouse/output: {missing}")


def test_peak_premium_reproduces_the_thesis_values():
    _needs("ercot_peak_premium_annual")
    df = erw.fetch("ercot_peak_premium_annual", node="HB_HUBAVG")
    for var, (v2015, v2025) in THESIS.items():
        for year, want in ((2015, v2015), (2025, v2025)):
            got = df[(df["variable"] == var) & (df["ts_utc"] == pd.Timestamp(f"{year}-01-01", tz="UTC"))]["value"]
            assert len(got) == 1 and round(float(got.iloc[0]), 2) == want, (var, year, got.tolist())


def test_peak_premium_structure():
    _needs("ercot_peak_premium_annual", "ercot_peak_premium_monthly")
    a = erw.fetch("ercot_peak_premium_annual")
    m = erw.fetch("ercot_peak_premium_monthly")
    assert set(a["freq"]) == {"P1Y"} and set(m["freq"]) == {"P1M"}
    assert set(a["unit"]) == {"USD/MWh", "ratio", "count"}
    years = sorted(a["ts_utc"].dt.year.unique())
    assert years[0] == 2015 and years == list(range(2015, years[-1] + 1))
    n = a[(a["variable"] == "n_intervals") & (a["ts_utc"].dt.year < years[-1])]
    leap = n["ts_utc"].dt.year.map(lambda y: y % 4 == 0)
    assert (n["value"] == leap.map({True: 35136.0, False: 35040.0})).all()
    # the worst-interval multiple is p99.9 over median, as the method doc defines it
    w = a.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value")
    assert ((w["worst_interval_multiple"] - w["all_p999"] / w["all_median"]).abs() < 1e-4).all()
    assert ((w["peak_iqr"] - (w["peak_q3"] - w["peak_q1"])).abs() < 1e-4).all()
    # monthly intervals add up to the annual count for every complete year
    mm = m[m["variable"] == "n_intervals"].assign(year=lambda d: d["ts_utc"].dt.year)
    tot = mm.groupby(["entity", "year"])["value"].sum()
    for (ent, ts), v in n.set_index(["entity", "ts_utc"])["value"].items():
        assert tot[(ent, ts.year)] == v


def test_tier_column_cite_and_info():
    """Session 28: every table has a provenance tier, and cite() and info() carry it."""
    cov = erw.coverage()
    assert "tier" in cov.columns
    assert set(cov["tier"]) <= {"source", "derived", "model_extracted"} and (cov["tier"] != "").all()
    by = cov.set_index("table")["tier"]
    for name in by.index:
        assert erw.tier(name) == by[name]
        assert erw.cite(name).endswith(f"Provenance tier: {by[name]} ({erw.api.TIER_NOTE[by[name]]}).")
    if "energy_deals" in by.index:
        assert by["energy_deals"] == "model_extracted"
    if "ercot_dam_hub_prices" in by.index:
        assert by["ercot_dam_hub_prices"] == "source"
    assert erw.info(quiet=True)["tiers"] == {k: int(v) for k, v in cov["tier"].value_counts().items()}
