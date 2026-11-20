"""Session 8905 (chain 590): the Stata runners of the sheet of forty, held to the sheet and to the do-files they call.

No Stata on the machine that wrote them: these tests read the files, they do not run Stata.
"""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs" / "findings" / "_top40"


def _load(name):
    spec = importlib.util.spec_from_file_location("c590_" + name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BR = _load("build_runners")


def test_runners_are_what_the_builder_writes():
    rows = BR.findings()
    assert [r["n"] for r in rows] == list(range(1, 41))
    want40 = BR.runner(rows, "run_top40", "The forty")
    want10 = BR.runner([r for r in rows if r["n"] in BR.TOP10], "run_top10", "The ten of tonight's page")
    assert (HERE / "run_top40.do").read_text(encoding="utf-8") == want40
    assert (HERE / "run_top10.do").read_text(encoding="utf-8") == want10


def test_sheet_figures_within_the_drafts_tolerance_of_each_do_file():
    for r in BR.findings():
        if r["kind"] == "summary":
            for k in ("med", "min", "max", "n"):
                assert abs(r["sheet_" + k] - r["exp_" + k]) <= 0.005 * abs(r["exp_" + k]), (r["n"], k)
            continue
        assert (r["y0"], r["y1"]) == (r["ey0"], r["ey1"]), r["n"]
        tol = 0.005 * abs(r["expchange"])
        assert abs(r["sheet1"] - r["exp1"]) <= tol, r["n"]
        assert abs(r["sheet0"] - r["exp0"]) <= tol, r["n"]


def test_each_do_file_leaves_what_the_runner_reads():
    for r in BR.findings():
        lines = [x for x in (ROOT / r["do"]).read_text(encoding="utf-8").splitlines() if x.strip()]
        assert "clear all" in lines, r["n"]
        if r["kind"] == "years":
            assert lines[-1] == "list year measure n, noobs", r["n"]
        else:
            assert "summarize value, detail" in lines, r["n"]
        text = "\n".join(lines)
        assert not re.search(r"^\s*(exit|cd |log |program )", text, re.M), r["n"]


def test_samuels_stata_rules():
    for name in ("run_top40.do", "run_top10.do"):
        lines = (HERE / name).read_text(encoding="utf-8").split("\n")
        assert "///" not in "\n".join(lines)
        depth = 0
        prev_blank = True
        for i, line in enumerate(lines[:-1]):
            if depth > 0:
                assert line.strip(), "%s line %d: an empty line inside a loop" % (name, i + 1)
            else:
                if line.strip():
                    assert prev_blank, "%s line %d: no empty line before a command outside a loop" % (name, i + 1)
                else:
                    assert not prev_blank or i == 0, "%s line %d: two empty lines" % (name, i + 1)
            depth += line.count("{") - line.count("}") if not line.startswith("display") else 0
            prev_blank = not line.strip()
        assert depth == 0
        assert chr(0x2014) not in "\n".join(lines)


def test_strip_copy_drops_only_the_leading_hash_lines(tmp_path):
    SH = _load("strip_hash_lines")
    src = tmp_path / "t.csv"
    src.write_text("# source: EIA\n# retrieved 2026\nentity,value\na,#1\n#b,2\n", encoding="utf-8")
    n = SH.strip_copy(src, tmp_path / "out.csv")
    assert n == 2
    assert (tmp_path / "out.csv").read_text(encoding="utf-8") == "entity,value\na,#1\n#b,2\n"


def test_the_ten_are_on_the_sheet_and_none_repeats_a_publisher():
    assert len(BR.TOP10) == 10 and set(BR.TOP10) <= set(range(1, 41))
    assert not set(BR.TOP10) & {23, 24, 27, 31, 32, 34}
