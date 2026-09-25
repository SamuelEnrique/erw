"""Tests of the erw client against the real tables in warehouse/output.

Energy Research Warehouse (ERW). No fixtures are invented: every assertion is
about the committed tables, docs/coverage.md and warehouse/metadata/coverage.csv.

    python -m pytest package/tests -v
"""

import re
from pathlib import Path

import pandas as pd
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
MD_ROWS = coverage_md_rows()


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
                                 "validator_status"]
    assert sorted(cov["table"]) == TABLES
    assert str(cov["ts_min"].dtype).startswith("datetime64") and cov["ts_min"].dt.tz is not None
    assert (cov["validator_status"] == "pass").all()


def test_coverage_md_lists_every_table():
    assert sorted(MD_ROWS) == TABLES


@pytest.mark.parametrize("name", TABLES)
def test_fetch_row_count_matches_coverage_md(name):
    df = erw.fetch(name)
    assert len(df) == MD_ROWS[name]


@pytest.mark.parametrize("name", TABLES)
def test_fetch_types_and_provenance(name):
    df = erw.fetch(name)
    assert list(df.columns[:4]) == ["entity", "variable", "ts_utc", "value"]
    assert str(df["ts_utc"].dtype) == "datetime64[ns, UTC]"
    assert df["value"].dtype == float
    assert not df.duplicated(["entity", "variable", "ts_utc"]).any()
    meta = df.attrs["erw"]
    assert meta["table"] == name
    assert meta["title"] and meta["retrieved"] and meta["run_log"]
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
    assert erw.filter(iso="ercot") == ercot
    assert erw.filter(iso="ERCOT", market="dam") == ["ercot_dam_hub_prices"]
    assert erw.filter(market="ercot_rtm") == ["ercot_rtm_hub_prices"]
    assert set(erw.filter(market="rtm")) == set(cov.loc[cov["market"].str.endswith("_rtm"), "table"])
    assert erw.filter(variable="spp_rtm") == ["ercot_rtm_hub_prices"]
    assert erw.filter(node="HB_NORTH") == ercot
    assert erw.filter(node="ercot:HB_NORTH") == ercot
    assert erw.filter(iso=["ERCOT", "NYISO"], node="N.Y.C.") == sorted(
        cov.loc[cov["iso"] == "NYISO", "table"])
    assert erw.filter(start="2000-01-01", end="2000-01-02") == []
    last = cov["ts_max"].max()
    assert set(erw.filter(start=last)) == set(cov.loc[cov["ts_max"] >= last, "table"])
    assert erw.filter() == TABLES


@pytest.mark.parametrize("name", TABLES)
def test_sources_names_reports_and_every_row_url(name):
    s = erw.sources(name)
    df = erw.fetch(name)
    assert s["table"] == name
    assert {r["source"] for r in s["reports"]} == set(df["source"]) | {
        r["source"] for r in df.attrs["erw"]["sources"]}
    assert s["source_urls"] == sorted(set(df["source_url"]))
    assert all(u.startswith("http") for u in s["source_urls"])


@pytest.mark.parametrize("name", TABLES)
def test_cite_names_the_iso_the_table_and_the_commit(name):
    c = erw.cite(name)
    org = name.split("_")[0]
    publisher = {"ercot": "Electric Reliability Council of Texas", "caiso": "California",
                 "nyiso": "New York", "miso": "Midcontinent", "spp": "Southwest Power Pool",
                 "isone": "ISO New England"}[org]
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

        def version(self):
            calls.append("version")
            return {"backend": self.name, "data_commit": None}

        def describe(self):
            return "wrapped local files"

    erw.set_backend(Wrapped())
    name = TABLES[0]
    assert erw.list_tables() == TABLES
    assert len(erw.fetch(name)) == MD_ROWS[name]
    assert name in erw.filter(iso=name.split("_")[0])
    assert erw.sources(name)["table"] == name
    assert "Energy Research Warehouse (ERW)" in erw.cite(name)
    assert erw.version()["backend"] == "wrapped"
    assert {"list_tables", "read_table", "coverage", "version"} <= set(calls)
