"""Session 29 ruling: the daily workflow regenerates sources.csv after its pull from both copies."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "warehouse", "metadata"))
import merge_sources as M  # noqa: E402


def row(sid, tables, first, last, report="r"):
    return {"source": sid, "publisher": "p", "report": report, "report_url": "https://x", "document_list": "",
            "license": "public", "tables": tables, "first_seen": first, "last_seen": last}


def test_a_source_only_main_has_is_kept_and_shared_sources_are_merged():
    main = {"a:1": row("a:1", "t1", "2026-09-01", "2026-09-20"), "s:new": row("s:new", "t9", "2026-09-28", "2026-09-28")}
    run = {"a:1": row("a:1", "t2", "2026-09-05", "2026-09-29", report="newer"), "b:2": row("b:2", "t3", "2026-09-29", "2026-09-29")}
    out = M.merge(main, run).set_index("source")
    assert list(out.index) == ["a:1", "b:2", "s:new"]
    assert out.loc["a:1", "tables"] == "t1;t2"
    assert (out.loc["a:1", "first_seen"], out.loc["a:1", "last_seen"]) == ("2026-09-01", "2026-09-29")
    assert out.loc["a:1", "report"] == "newer"


def test_the_merge_of_a_registry_with_itself_is_the_registry(tmp_path):
    reg = os.path.join(os.path.dirname(__file__), "..", "warehouse", "metadata", "sources.csv")
    out = tmp_path / "out.csv"
    M.main([reg, reg, "--out", str(out)])
    a = pd.read_csv(reg, dtype=str, keep_default_na=False)
    b = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert a.sort_values("source").reset_index(drop=True).equals(b.sort_values("source").reset_index(drop=True))
