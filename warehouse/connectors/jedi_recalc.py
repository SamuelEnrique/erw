#!/usr/bin/env python3
"""JEDI's own formulas, evaluated for each location JEDI lists (session 345). The first step of jedi_multipliers.

Energy Research Warehouse (ERW). NLR's Jobs and Economic Development Impact (JEDI) models are Excel workbooks. Each is
saved with one project in one state, and holds the results of that one project only; the multipliers of every state
are in its hidden sheet "Multipliers", in jobs and dollars per million dollars of spending, not per MW. A per-MW figure
for a state is therefore what the workbook itself shows once its Project Location is that state. This script asks
the workbook's own formulas that question, with nothing else changed, through pycel (a reader of Excel formulas; no
Excel, no macro is run).

It refuses to write anything unless the workbook, recalculated with its saved inputs, reproduces every figure of its
own summary as it was saved (to one part in a billion). Each model's one setting besides the location that this
script makes is named in SETTINGS (the PV model's System Application set to its own "Utility" option, whose defaults
JEDI holds: the prompt asks for utility-scale solar).

pycel needs networkx below 2.7 and the repository's environment holds networkx 3 (mapclassify needs it), so this step
runs in an environment of its own, kept outside git:

    python -m venv .venv-jedi
    .venv-jedi\\Scripts\\python.exe -m pip install pycel openpyxl==3.0.10
    .venv-jedi\\Scripts\\python.exe -I warehouse/connectors/jedi_recalc.py      # writes warehouse/raw/nlr_jedi/recalc/*.json
    .venv\\Scripts\\python.exe warehouse/connectors/jedi_multipliers.py          # the table, from those files

It writes under warehouse/raw only (the evaluated cells, as JEDI's formulas give them), never warehouse/output, so it
takes no data lock. Python 3.12 and later removed ast.Str, which pycel 1.0b30 still calls: the two lines below the
imports give it back as ast.Constant, in this process only.
"""

import ast
import datetime as dt
import hashlib
import json
import os
import sys
import time

ast.Str = lambda *a, **k: ast.Constant(value=a[0] if a else k.get("s"))  # pycel 1.0b30 on Python 3.12+

import openpyxl  # noqa: E402
from pycel import ExcelCompiler  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RAW = os.path.join(ROOT, "warehouse", "raw", "nlr_jedi")
OUT = os.path.join(RAW, "recalc")

# technology -> the workbook, its summary sheet, the input cells, and where each result stands. Every row of `rows` is
# (phase, effect, the summary row, the words its column A must begin with); columns B, C and D are jobs, earnings and
# output. `scale` turns earnings and output into dollars (the summary states millions, or thousands for PV).
MODELS = {
    "land_based_wind": dict(
        file="01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm", summary="SummaryResults", location="ProjectData!B13",
        locations="ProjectData!O687:O738", scale=1e6,
        mw="SummaryResults!C4", mw_scale=1.0, mw_basis="nameplate MW", dollar_year="SummaryResults!C10",
        local=dict(construction=("SummaryResults!C12", "SummaryResults!C11"), operations=("SummaryResults!C15", "SummaryResults!C14")),
        rows=[("construction", "onsite", 28, "       Total"), ("construction", "supply_chain", 29, "     Turbine and Supply Chain"),
              ("construction", "induced", 30, "     Induced"), ("construction", "total", 31, "     Total Impacts"),
              ("operations", "onsite", 34, "     Onsite Labor"), ("operations", "supply_chain", 35, "     Local Revenue and Supply Chain"),
              ("operations", "induced", 36, "     Induced"), ("operations", "total", 37, "     Total Impacts")]),
    "utility_pv": dict(
        file="jedi-pv-model.xlsm", summary="SummaryResults", location="ProjectData!B12",
        locations="ProjectData!O758:O809", scale=1e3, settings={"ProjectData!B15": "Utility"},
        mw="SummaryResults!C6", mw_scale=1e-3, mw_basis="DC nameplate MW", dollar_year="SummaryResults!C12",
        local=dict(construction=("SummaryResults!C14", "SummaryResults!C13"), operations=("SummaryResults!C17", "SummaryResults!C16")),
        rows=[("construction", "onsite", 30, "     Subtotal"), ("construction", "supply_chain", 38, "     Subtotal"),
              ("construction", "induced", 39, "   Induced"), ("construction", "total", 40, "  Total Impacts"),
              ("operations", "onsite", 46, "     PV Project Labor"), ("operations", "supply_chain", 47, "   Local Revenue and Supply Chain"),
              ("operations", "induced", 48, "   Induced"), ("operations", "total", 49, "  Total Impacts")]),
    "natural_gas": dict(
        file="01d-jedi-ngas-model_rel-ng4-17-17.xlsm", summary="SummaryResults", location="ProjectData!B13",
        locations="name:Location", scale=1e6,
        mw="SummaryResults!C4", mw_scale=1.0, mw_basis="nameplate MW", dollar_year="SummaryResults!C13",
        local=dict(construction=("SummaryResults!C15", "SummaryResults!C14"), operations=("SummaryResults!C18", "SummaryResults!C17")),
        rows=[("construction", "onsite", 27, "     Project Development and Onsite"), ("construction", "supply_chain", 30, "     Power Generation and Supply Chain"),
              ("construction", "induced", 31, "     Induced"), ("construction", "total", 32, "     Total Impacts"),
              ("operations", "onsite", 35, "     Onsite Labor"), ("operations", "supply_chain", 36, "     Local Revenue and Supply Chain"),
              ("operations", "induced", 37, "     Induced"), ("operations", "total", 38, "     Total Impacts")]),
    "geothermal": dict(
        file="01d-jedi-geothermal-model-rel-gt12-23-16.xlsm", summary="Summary Results", location="ProjectData!B13",
        locations="name:Statelist", scale=1e6,
        mw="Summary Results!B7", mw_scale=1.0, mw_basis="nameplate MW (the model's 10 MW net output)", dollar_year="Summary Results!D6",
        local=dict(construction=("Summary Results!D8", "Summary Results!D7"), operations=("Summary Results!D11", "Summary Results!D10")),
        rows=[("construction", "onsite", 23, "     Project Development and Onsite"), ("construction", "supply_chain", 26, "     Turbine and Supply Chain"),
              ("construction", "induced", 27, "     Induced"), ("construction", "total", 28, "   Total Impacts"),
              ("operations", "onsite", 31, "     Onsite Labor"), ("operations", "supply_chain", 32, "     Local Revenue and Supply Chain"),
              ("operations", "induced", 33, "     Induced"), ("operations", "total", 34, "     Total Impacts")]),
}
MEASURES = (("jobs", "B"), ("earnings", "C"), ("output", "D"))
SKIP = {"MYCOUNTY", "MYREGION"}


def _one(x):
    """A one-cell array as its value, as Excel reads it where a function wants a number; a larger array is an error."""
    while isinstance(x, (tuple, list)):
        if len(x) != 1:
            raise ValueError(f"an array of {len(x)} where one number is wanted")
        x = x[0]
    return x


def _ones(f):
    def g(*args):
        args = [_one(a) for a in args]
        for a in args:  # Excel passes an error on, and a text where a number is wanted is #VALUE!
            if isinstance(a, str):
                return a if a.startswith("#") else "#VALUE!"
        return f(*[0 if a is None else a for a in args])
    g.__name__, g.__doc__ = f.__name__, f.__doc__
    return g


@_ones
def ispmt(rate, per, nper, pv):
    """Excel's ISPMT, which pycel lacks and the PV model's utility financing uses: the interest of period `per` of a loan
    of `pv` repaid in `nper` equal parts of principal, as Excel defines it (pv * rate * (per / nper - 1)). Checked
    against Excel's own example: ISPMT(0.1/12, 1, 36, 8000000) is -64,814.81."""
    return pv * rate * (per / nper - 1)


def _pmt(rate, nper, pv, fv=0, typ=0):
    if rate == 0:
        return -(pv + fv) / nper
    g = (1 + rate) ** nper
    return -(fv + pv * g) * rate / ((1 + rate * typ) * (g - 1))


def _fv(rate, n, pmt, pv, typ=0):
    if rate == 0:
        return -(pv + pmt * n)
    g = (1 + rate) ** n
    return -(pv * g + pmt * (1 + rate * typ) / rate * (g - 1))


@_ones
def ipmt(rate, per, nper, pv, fv=0, typ=0):
    """Excel's IPMT (pycel lacks it): the interest part of payment `per` of an annuity. Checked against Excel's own
    examples: IPMT(0.1/12, 1, 36, 8000) is -66.67 and IPMT(0.1, 3, 3, 8000) is -292.45."""
    fv = fv or 0
    typ = 1 if typ else 0
    pmt = _pmt(rate, nper, pv, fv, typ)
    if typ == 1 and per == 1:
        return 0.0
    i = _fv(rate, per - 1, pmt, pv, typ) * rate
    return i / (1 + rate) if typ == 1 else i


@_ones
def ppmt(rate, per, nper, pv, fv=0, typ=0):
    """Excel's PPMT (pycel lacks it): the principal part, the payment less its interest. Checked against Excel's own
    examples: PPMT(0.1/12, 1, 24, 2000) is -75.62 and PPMT(0.08, 10, 10, 200000) is -27,598.05."""
    fv = fv or 0
    typ = 1 if typ else 0
    return _pmt(rate, nper, pv, fv, typ) - ipmt(rate, per, nper, pv, fv, typ)


@_ones
def exp(x):
    """Excel's EXP (pycel 1.0b30 has no EXP of its own)."""
    import math
    return math.exp(x)


def median(*args):
    """Excel's MEDIAN, which pycel lacks and the wind model's defaults use: the median of the numbers given, a range's
    text, blanks and logical values left out as Excel leaves them out of a reference."""
    nums = []

    def take(x):
        if isinstance(x, (tuple, list)):
            for y in x:
                take(y)
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            nums.append(float(x))
    take(args)
    if not nums:
        return "#NUM!"
    nums.sort()
    k = len(nums) // 2
    return nums[k] if len(nums) % 2 else (nums[k - 1] + nums[k]) / 2


def quote(ref):
    s, a = ref.split("!")
    return f"'{s}'!{a}" if " " in s else ref


def locations(wb, spec):
    """The model's own pull-down list of locations, as its cells hold them (trailing spaces kept)."""
    if spec.startswith("name:"):
        dn = wb.defined_names[spec[5:]]
        (sheet, rng), = list(dn.destinations)
        ws = wb[sheet]
    else:
        sheet, rng = spec.split("!")
        ws = wb[sheet]
    vals = [c.value for row in ws[rng.replace("$", "")] for c in row]
    return [v for v in vals if isinstance(v, str) and v.strip() and not v.startswith("=") and v.strip().upper() not in SKIP]


def cells(m):
    out = [m["mw"], m["dollar_year"]] + [r for pair in m["local"].values() for r in pair]
    for _, _, row, _ in m["rows"]:
        out += [f"{m['summary']}!{col}{row}" for _, col in MEASURES]
    return out


def local_names(xl, path):
    """Names scoped to one sheet (workbook.xml's definedName with a localSheetId), which pycel does not resolve: the
    wind model's DefaultData!R3 reads ProjectData!_xlnm.Print_Area, which ProjectData defines as its own $B$15 (the
    year of construction), and pycel gives #NAME? where Excel gives the year. Each such reference in a formula is
    written as the address the sheet itself defines, in memory only; a reference left unresolved stops the run.
    Returns the replacements made."""
    import re
    import zipfile
    x = zipfile.ZipFile(path).read("xl/workbook.xml").decode("utf-8")
    sheets = re.findall(r'<sheet [^>]*name="([^"]+)"', x)
    local = {}
    for m in re.finditer(r'<definedName name="([^"]+)"[^>]*localSheetId="(\d+)"[^>]*>([^<]+)</definedName>', x):
        local[(sheets[int(m.group(2))], m.group(1))] = m.group(3).replace("&apos;", "'")
    done = {}
    for ws in xl.excel.workbook.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not (isinstance(v, str) and v.startswith("=") and "_xlnm." in v):
                    continue
                for (sheet, name), target in local.items():
                    for form in (f"'{sheet}'!{name}", f"{sheet}!{name}"):
                        if form in v:
                            v = v.replace(form, target)
                            done[f"{ws.title}!{c.coordinate}"] = f"{sheet}!{name} -> {target}"
                if "_xlnm." in v:
                    raise RuntimeError(f"{ws.title}!{c.coordinate}: a sheet's own name is not resolved: {v[:120]}")
                c.value = v
    return done


def fresh(xl, m):
    """Every figure of `cells(m)` computed from the workbook's constants. pycel builds each formula cell holding the
    value the file saved, and computes a cell only when its value is None; a range read before its cells holds the
    saved values too. So every formula cell and range of the graph is emptied first, then the outputs are evaluated;
    a cell met for the first time on the way (an INDIRECT or OFFSET) arrives holding its saved value, so the pass is
    repeated until the graph stops growing."""
    for _ in range(6):
        n = len(xl.cell_map)
        for c in xl.cell_map.values():
            if type(c).__name__ == "_CellRange" or c.formula:
                c.value = None
        out = {ref: xl.evaluate(quote(ref)) for ref in cells(m)}
        if len(xl.cell_map) == n:
            return out
    raise RuntimeError("the graph kept growing after six passes")


def identity(m, r):
    """JEDI's own sum: the total of each phase and measure is its onsite, supply chain and induced lines."""
    bad = []
    for phase in ("construction", "operations"):
        rows = {e: row for ph, e, row, _ in m["rows"] if ph == phase}
        for meas, col in MEASURES:
            v = {e: r[f"{m['summary']}!{col}{row}"] for e, row in rows.items()}
            if any(not isinstance(x, (int, float)) for x in v.values()):
                bad.append((phase, meas, "not a number", v))
                continue
            parts = v["onsite"] + v["supply_chain"] + v["induced"]
            if abs(parts - v["total"]) > 1e-6 * max(1.0, abs(v["total"])):
                bad.append((phase, meas, parts, v["total"]))
    return bad


def run(tech, m, log):
    path = os.path.join(RAW, m["file"])
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    cached = openpyxl.load_workbook(path, read_only=True, data_only=True)
    plain = openpyxl.load_workbook(path, read_only=False, data_only=False)
    for phase, effect, row, words in m["rows"]:
        label = cached[m["summary"]][f"A{row}"].value or ""
        if not label.startswith(words):
            raise RuntimeError(f"{m['file']}: {m['summary']}!A{row} reads {label!r}, not {words!r}: the layout has changed")
    saved_loc = cached[m["location"].split("!")[0]][m["location"].split("!")[1]].value
    t = time.time()
    xl = ExcelCompiler(filename=path, plugins=["__main__"])
    names = local_names(xl, path)
    if names:
        log(f"{tech}: a sheet's own name resolved in {len(names)} formulas: {sorted(set(names.values()))}")
    for ref in cells(m):          # the graph of every output, with the saved values
        xl.evaluate(quote(ref))
    # 1. the saved project, computed from the constants, must give the saved figures
    got = fresh(xl, m)
    bad = []
    for ref, v in got.items():
        s, a = ref.split("!")
        cv = cached[s][a].value
        if isinstance(cv, (int, float)) and not (isinstance(v, (int, float)) and abs(v - cv) <= 1e-9 * max(1.0, abs(cv))):
            bad.append((ref, cv, v))
    if bad:
        raise RuntimeError(f"{m['file']}: computed with its saved inputs, {len(bad)} figures differ from the saved ones, "
                           f"first {bad[0]}: nothing written")
    log(f"{tech}: {len(got)} cells of the saved project ({saved_loc!r}) computed from the constants, every one as saved; "
        f"{len(xl.cell_map)} cells in the graph")
    # 2. the model's own settings, then every location, each computed afresh
    settings = m.get("settings", {})
    for ref, v in settings.items():
        xl.set_value(quote(ref), v)
    locs = locations(plain, m["locations"])
    res, errors = {}, {}
    for loc in locs:
        xl.set_value(quote(m["location"]), loc)
        r = fresh(xl, m)
        err = {ref: v for ref, v in r.items() if isinstance(v, str) and v.startswith("#")}
        if err:  # JEDI's own answer at this location is an Excel error (the gas model's #DIV/0! for DC): kept as that
            errors[loc] = err
            continue
        res[loc] = r
        broken = identity(m, res[loc])
        if broken:
            raise RuntimeError(f"{m['file']} at {loc!r}: a total is not the sum of its lines, {broken[0]}: nothing written")
    log(f"{tech}: {len(locs)} locations in {time.time() - t:.0f} s; every total the sum of its three lines"
        + (f"; JEDI gives an Excel error at {len(errors)}: {sorted(errors)}" if errors else ""))
    return dict(technology=tech, file=m["file"], sha256=sha, saved_location=saved_loc, settings=settings,
                local_names=names, reproduced_cells=len(got), graph_cells=len(xl.cell_map), locations=locs, results=res, errors=errors,
                about=f"JEDI's formulas in {m['file']} computed by pycel from the workbook's constants with Project Location "
                      f"({m['location']}) set to each location of the model's own list and nothing else changed"
                      + (f" but {settings}" if settings else ""))


def main():
    os.makedirs(OUT, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = []

    def log(s):
        lines.append(s)
        print(s, flush=True)

    rc = 0
    only = set(sys.argv[1:])
    for tech, m in MODELS.items():
        if only and tech not in only:
            continue
        try:
            d = run(tech, m, log)
            d["evaluated_at"] = stamp
            with open(os.path.join(OUT, f"{tech}.json"), "w", encoding="utf-8", newline="\n") as f:
                json.dump(d, f, indent=1, default=str)
        except Exception as exc:  # one model failing leaves the others
            log(f"{tech} FAILED, no file written: {type(exc).__name__}: {exc}")
            rc = 1
    with open(os.path.join(OUT, "recalc.log"), "a", encoding="utf-8") as f:
        f.write(f"# {stamp}\n" + "\n".join(lines) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
