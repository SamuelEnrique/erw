"""erw.describe() and erw.variables() read the codebook (chain 630, part D)."""
import json

import pytest

import erw
from erw import codebook


def test_describe_fills_shared_columns_and_keeps_table_order():
    names = codebook.names()
    assert names, "no codebook entry found"
    t = "ba_supply_monthly" if "ba_supply_monthly" in names else names[0]
    d = erw.describe(t)
    assert d["table"] == t
    raw = codebook.raw(t)
    assert [c["name"] for c in d["columns"]] == [c["name"] for c in raw["columns"]]
    sh = codebook.shared()
    for c in d["columns"]:
        if c["shared"]:
            assert c["label"] == sh[c["name"]]["label"]
            assert c["unit"] == sh[c["name"]]["unit"]


def test_variables_is_one_row_a_column():
    t = codebook.names()[0]
    df = erw.variables(t)
    assert list(df.columns) == ["name", "label", "unit", "type", "values", "missing_meaning", "missing_cells",
                                "source_name", "shared"]
    assert list(df["name"]) == [c["name"] for c in codebook.raw(t)["columns"]]


def test_unknown_table_is_refused_by_name():
    with pytest.raises(erw.ERWDataNotFound):
        erw.describe("no_such_table_anywhere")


def test_values_text():
    assert codebook.values_text({"list": {"a": 1, "b": 2}}) == "a, b"
    assert codebook.values_text({"distinct": 9, "lowest": 1, "highest": 5}) == "1 to 5; 9 distinct"
    assert codebook.values_text(None) == ""


def test_shipped_copy_holds_public_tables_only(tmp_path, monkeypatch):
    # the installed package's copy: built from the clone's files, the public tables only
    import importlib.util
    from pathlib import Path
    root = Path(codebook.__file__).resolve().parents[3]
    tool = root / "package" / "tools" / "build_codebook.py"
    if not tool.is_file():
        pytest.skip("not a clone")
    spec = importlib.util.spec_from_file_location("build_codebook", tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    data = json.loads(mod.build())
    assert set(data["tables"]) <= mod.public()
    assert "ts_utc" in data["shared"]
