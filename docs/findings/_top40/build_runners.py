"""Write run_top40.do and run_top10.do from the sheet of forty and the forty reproduce.do files.

Energy Research Warehouse (ERW), session 8905 (chain 590, 19 November 2026). The sheet is
docs/reviews/findings-shortlist-2026-11-19.md; each finding's do-file is named on its "For Samuel's Stata run" line.
The runner keeps Samuel's Stata rules: no line continuation, one empty line between commands outside loops and
none inside, and no string turned into a number (so no destring is needed).

Run from the repository's root:  python docs/findings/_top40/build_runners.py
A test (tests/test_session8905_top40_runner.py) checks the two .do files are what this script writes.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHEET = ROOT / "docs" / "reviews" / "findings-shortlist-2026-11-19.md"
HERE = ROOT / "docs" / "findings" / "_top40"

# The ten of the page docs/reviews/tonight-2026-11-19.md: the top of the sheet's order and every finding the audit
# found new, none that only repeats a publisher's own figure.
TOP10 = [1, 2, 3, 4, 10, 11, 14, 16, 17, 19]

# Short names for the table Stata prints at the end: no quotes, no apostrophes, at most 44 characters.
NAMES = {
    1: "Dominion zone, mean hour (MW)",
    2: "Virginia Power, commercial sales (TWh)",
    3: "ERCOT solar in tightest hours (pct)",
    4: "ERCOT West, midday price (pct of mean)",
    5: "ERCOT South hub, evening price (pct)",
    6: "ERCOT North hub, cheapest hour (hour)",
    7: "Omaha PPD, commercial sales (TWh)",
    8: "Canada to New York, mean flow (MW)",
    9: "New England, hours exporting (pct)",
    10: "CAISO batteries against peak (pct)",
    11: "ERCOT load factor (pct)",
    12: "US data center construction (USD bn)",
    13: "Virginia commercial electricity (TWh)",
    14: "US gas fleet heat rate (MMBtu per MWh)",
    15: "LNG share of US dry gas (pct)",
    16: "Henry Hub median daily move (pct)",
    17: "Gulf Coast gasoline crack (USD per bbl)",
    18: "Large-load minimum bill, median (pct)",
    19: "ERCOT CO2 per MWh (kg)",
    20: "ERCOT West, wide-spread days (pct)",
    21: "Texas, January 2026 cold peak (MW)",
    22: "Carolinas, Elliott peak (MW)",
    23: "US reactor uranium price (USD per lb)",
    24: "US-origin uranium share (pct)",
    25: "India coal consumption (million st)",
    26: "US power CO2 per MWh (kg)",
    27: "US-origin enrichment share (pct)",
    28: "Georgia and Alabama coal share (pct)",
    29: "Florida gas share (pct)",
    30: "Arizona and New Mexico solar share (pct)",
    31: "US commercial retail sales (TWh)",
    32: "Greece coal share (pct)",
    33: "Texas cooling degree days a day",
    34: "EU27 solar share (pct)",
    35: "Portugal net imports (pct)",
    36: "Finland wind share (pct)",
    37: "US share of world liquids (pct)",
    38: "US dry gas exports (bcf)",
    39: "US reactor fleet power level (pct)",
    40: "Indonesia coal exports (million st)",
}

NUM = r"(-?[\d,]*\.?\d+)"


def num(s):
    return float(s.replace(",", ""))


def findings():
    """Each finding of the sheet: number, do-file, the sheet's figures, the do-file's expected figures, its tables."""
    body = SHEET.read_text(encoding="utf-8").split("## The 40", 1)[1].split("\n## By family", 1)[0]
    out = []
    for block in re.split(r"^### (?=\d+\. )", body, flags=re.M)[1:]:
        n = int(block.split(".", 1)[0])
        do = re.search(r"For Samuel's Stata run:\*\* https://github\.com/SamuelEnrique/erw/blob/main/(\S+\.reproduce\.do)", block).group(1)
        fig = re.search(r"The figure:\*\* (.+)", block).group(1)
        text = (ROOT / do).read_text(encoding="utf-8")
        first = text.splitlines()[0]
        tables = sorted(set(re.findall(r'import delimited "([^"]+)"', text)))
        row = {"n": n, "do": do, "name": NAMES[n], "tables": tables, "expected_line": first}
        m = re.match(r"median %s, lowest %s, highest %s, filings %s" % (NUM, NUM, NUM, NUM), fig)
        if m:
            row.update(kind="summary", sheet_med=num(m.group(1)), sheet_min=num(m.group(2)), sheet_max=num(m.group(3)), sheet_n=num(m.group(4)))
            e = re.search(r"median %s; lowest %s; highest %s; filings %s" % (NUM, NUM, NUM, NUM), first)
            row.update(exp_med=num(e.group(1)), exp_min=num(e.group(2)), exp_max=num(e.group(3)), exp_n=num(e.group(4)))
        else:
            m = re.match(r"%s .*? in (\d{4}), against %s in (\d{4})" % (NUM, NUM), fig)
            row.update(kind="years", sheet1=num(m.group(1)), y1=int(m.group(2)), sheet0=num(m.group(3)), y0=int(m.group(4)))
            e = re.search(r"Expected: (\d{4}) %s, (\d{4}) %s, change %s" % (NUM, NUM, NUM), first)
            row.update(ey0=int(e.group(1)), exp0=num(e.group(2)), ey1=int(e.group(3)), exp1=num(e.group(4)), expchange=num(e.group(5)))
        out.append(row)
    return out


def g(v):
    """A number as Stata reads it, with no thousands separator."""
    return repr(float(v)) if not float(v).is_integer() else str(int(v))


def runner(rows, label, count_words):
    L = []
    add = L.append
    add("* %s: run the reproduce.do files of the findings sheet one after another and print one table." % label)
    add("")
    add("* Energy Research Warehouse (ERW), written by session 8905 (chain 590) on 19 November 2026 by docs/findings/_top40/build_runners.py. Read, not run: the machine that wrote it has no Stata. The README beside it says what to do if a line fails.")
    add("")
    add("* The sheet: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-shortlist-2026-11-19.md")
    add("")
    add("* Set this one line: the folder of your copy of the ERW repository (forward slashes).")
    add("")
    add('global erw "C:/Users/samuel/Documents/erw"')
    add("")
    add("* The folder that holds the tables' CSVs, variable names on the first line (README, step 2). Change it only if your CSVs are elsewhere.")
    add("")
    add('global tables "$erw/docs/findings/_top40/tables"')
    add("")
    add("set more off")
    add("")
    add("set linesize 200")
    add("")
    add("capture log close top")
    add("")
    add('log using "$tables/%s.log", replace text name(top)' % label)
    add("")
    add('cd "$tables"')
    add("")
    add("* %s, in the sheet's order. For each: its number on the sheet, a short name, its do-file, the two years, the sheet's two figures. Finding 18 is a summary (median, lowest, highest, filings) and is checked on all four." % count_words)
    add("")
    add("global n %d" % len(rows))
    add("")
    for i, r in enumerate(rows, 1):
        add("global num%d %d" % (i, r["n"]))
        add("")
        add('global name%d "%s"' % (i, r["name"]))
        add("")
        add('global f%d "%s"' % (i, r["do"]))
        add("")
        add('global kind%d "%s"' % (i, r["kind"]))
        add("")
        if r["kind"] == "years":
            add("global y0_%d %d" % (i, r["y0"]))
            add("")
            add("global y1_%d %d" % (i, r["y1"]))
            add("")
            add("global e0_%d %s" % (i, g(r["sheet0"])))
            add("")
            add("global e1_%d %s" % (i, g(r["sheet1"])))
            add("")
        else:
            add("global e0_%d %s" % (i, g(r["sheet_n"])))
            add("")
            add("global e1_%d %s" % (i, g(r["sheet_med"])))
            add("")
            add("global emin_%d %s" % (i, g(r["sheet_min"])))
            add("")
            add("global emax_%d %s" % (i, g(r["sheet_max"])))
            add("")
    add("* Each do-file in turn. A file that fails is caught and the next one runs. The figure Stata got is read from the data the do-file leaves in memory: its measure in the sheet's last year (and first year, for the change).")
    add("")
    add("* A match: the last year's figure and the change both within 0.5 percent of the change, the drafts' stated tolerance (for finding 18, each of its four figures within 0.5 percent of itself).")
    add("")
    add("forvalues i = 1/$n {")
    add('display as text _newline "{hline}" _newline "Finding ${num`i\'} of the sheet: ${name`i\'}" _newline "{hline}"')
    add("global got0_`i' = .")
    add("global got1_`i' = .")
    add('global res`i\' "no figure"')
    add('capture noisily do "$erw/${f`i\'}"')
    add("global rc`i' = _rc")
    add("if ${rc`i'} != 0 {")
    add('global res`i\' "failed, error ${rc`i\'}"')
    add("}")
    add('else if "${kind`i\'}" == "summary" {')
    add("capture summarize value, detail")
    add("if _rc == 0 {")
    add("global got0_`i' = r(N)")
    add("global got1_`i' = r(p50)")
    add('global res`i\' = cond(abs(r(p50) - ${e1_`i\'}) <= 0.005 * abs(${e1_`i\'}) & abs(r(min) - ${emin_`i\'}) <= 0.005 * abs(${emin_`i\'}) & abs(r(max) - ${emax_`i\'}) <= 0.005 * abs(${emax_`i\'}) & abs(r(N) - ${e0_`i\'}) <= 0.005 * abs(${e0_`i\'}), "match", "differs")')
    add("}")
    add("}")
    add("else {")
    add("capture summarize measure if year == ${y0_`i'}, meanonly")
    add("if _rc == 0 & r(N) == 1 {")
    add("global got0_`i' = r(mean)")
    add("}")
    add("capture summarize measure if year == ${y1_`i'}, meanonly")
    add("if _rc == 0 & r(N) == 1 {")
    add("global got1_`i' = r(mean)")
    add("}")
    add("if !missing(${got0_`i'}) & !missing(${got1_`i'}) {")
    add('global res`i\' = cond(abs(${got1_`i\'} - (${e1_`i\'})) <= 0.005 * abs(${e1_`i\'} - (${e0_`i\'})) & abs((${got1_`i\'} - (${got0_`i\'})) - (${e1_`i\'} - (${e0_`i\'}))) <= 0.005 * abs(${e1_`i\'} - (${e0_`i\'})), "match", "differs")')
    add("}")
    add("}")
    add("}")
    add("")
    add("* The table: the finding, the figure the sheet gives, the figure Stata got, and whether they match.")
    add("")
    add("clear")
    add("")
    add("set obs $n")
    add("")
    add("generate int number = .")
    add("")
    add('generate str44 finding = ""')
    add("")
    add("generate double sheet = .")
    add("")
    add("generate double stata = .")
    add("")
    add('generate str24 result = ""')
    add("")
    add("forvalues i = 1/$n {")
    add("replace number = ${num`i'} in `i'")
    add('replace finding = "${name`i\'}" in `i\'')
    add("replace sheet = ${e1_`i'} in `i'")
    add("replace stata = ${got1_`i'} in `i'")
    add('replace result = "${res`i\'}" in `i\'')
    add("}")
    add("")
    add("format sheet stata %14.6g")
    add("")
    add("list number finding sheet stata result, noobs separator(0) abbreviate(12)")
    add("")
    add('count if result == "match"')
    add("")
    add('display as result r(N) " of $n match within the stated tolerance of the drafts."')
    add("")
    add("log close top")
    return "\n".join(L) + "\n"


def main():
    rows = findings()
    assert [r["n"] for r in rows] == list(range(1, 41)), "the sheet must hold findings 1 to 40 in order"
    (HERE / "run_top40.do").write_text(runner(rows, "run_top40", "The forty"), encoding="utf-8", newline="\n")
    ten = [r for r in rows if r["n"] in TOP10]
    (HERE / "run_top10.do").write_text(runner(ten, "run_top10", "The ten of tonight's page"), encoding="utf-8", newline="\n")
    print("wrote run_top40.do (%d findings) and run_top10.do (%d)" % (len(rows), len(ten)))


if __name__ == "__main__":
    main()
