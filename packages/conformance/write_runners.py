#!/usr/bin/env python3
"""Session 1006 (chain 070): run_stata.do and run_r.R, written from conformance.json, so the three runners make the
same twenty calls and expect the same answers.

Energy Research Warehouse (ERW), docs/methods/packages.md. The Stata runner is in the owner's style (no line
continuation; one empty line between commands outside a block, none inside). Each runner prints one line a call and
the count that pass. Where a package says something another way (the clause that names where the rows came from, the
fetch time's clock), the runner compares what the specification fixes: the words before the clause, the refusal's
code and words.

    python packages/conformance/write_runners.py
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIA = " Via the Energy Research Warehouse (ERW), table "


def stata_time(s):
    return s.replace("T", " ").replace("Z", "")


def stata(calls):
    out = ["* Energy Research Warehouse (ERW): the Stata package against the conformance file (session 1006).",
           "* Written by packages/conformance/write_runners.py from conformance.json; needs erw installed and",
           "* global ERW_LIVE_URL and global ERW_LIVE_KEY set. Prints one line a call and the count that pass.",
           "", "version 16", "", "local pass 0", ""]
    for c in calls:
        a, e, n = c["args"], c["expect"], c["n"]
        if c["call"] == "fetch":
            opts = []
            for k in ("entity", "variable"):
                if a.get(k):
                    opts.append(f"{k}({' '.join(a[k])})")
            for k in ("start", "end"):
                if a.get(k):
                    opts.append(f"{k}({a[k]})")
            out += [f"erw fetch {a['table']}, {' '.join(opts)} backend(live) clear", ""]
            tvar = "ts_utc"
            out += [f"capture confirm variable event_date", "", "if _rc == 0 {", "    local tvar event_date", "}",
                    "else {", "    capture confirm variable ts_utc",
                    "    local tvar = cond(_rc == 0, \"ts_utc\", \"status_date\")", "}", ""]
            out += ["quietly summarize `tvar'", ""]
            if "status_date" not in tvar:
                pass
            first, last = stata_time(e["first"]), stata_time(e["last"])
            out += [f"local t0 = cond(\"`tvar'\" == \"status_date\", date(\"{first[:10]}\", \"YMD\"), "
                    f"clock(\"{first}\", \"YMDhms\"))", "",
                    f"local t1 = cond(\"`tvar'\" == \"status_date\", date(\"{last[:10]}\", \"YMD\"), "
                    f"clock(\"{last}\", \"YMDhms\"))", "",
                    f"local ok = (_N == {e['rows']}) & (r(min) == `t0') & (r(max) == `t1')", ""]
        elif c["call"] == "cite":
            head = e["before_clause"].split(VIA)[0]
            out += [f"erw cite {a['table']}", "", f"local ok = strpos(`\"`r(cite)'\"', `\"{head}{VIA}\"') == 1", ""]
        elif c["call"] == "license":
            out += [f"erw license {a['table']}", "",
                    f"local ok = (\"`r(verdict)'\" == \"{e['verdict']}\") & (`\"`r(words)'\"' == `\"{e['words']}\"')", ""]
        elif c["call"] == "refusal":
            out += [f"capture erw fetch {a['table']}, start(2026-10-20) backend(live) clear", "",
                    "local ok = (_rc == 498)", ""]
        elif c["call"] == "standard":
            out += [f"erw standard {a['table']}, backend(live) clear", "",
                    f"local ok = (\"`r(shape)'\" == \"{e['shape']}\") & (\"`r(key)'\" == \"{' '.join(e['key'])}\")", ""]
        elif c["call"] == "tables":
            out += ["erw tables, clear", "", "quietly count if verdict == \"public\"", "",
                    f"local ok = (_N == {e['tables']}) & (r(N) == {e['public']})", ""]
        label = a.get("table", "")
        out += [f"display as text cond(`ok', \"ok   \", \"FAIL \") + \"{n:02d} {c['call']} {label}\"", "",
                "local pass = `pass' + `ok'", ""]
    out += [f"display as text \"`pass' of {len(calls)} pass\""]
    return "\n".join(out) + "\n"


def rq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def r(calls):
    out = ["# Energy Research Warehouse (ERW): the R package against the conformance file (session 1006).",
           "# Written by packages/conformance/write_runners.py from conformance.json; needs the erw package and",
           "# ERW_LIVE_URL and ERW_LIVE_KEY in the environment. Prints one line a call and the count that pass.",
           "library(erw)", "pass <- 0L",
           "stamp <- function(t) format(t, \"%Y-%m-%dT%H:%M:%SZ\", tz = \"UTC\")",
           "report <- function(ok, label) {",
           "  cat(if (isTRUE(ok)) \"ok   \" else \"FAIL \", label, \"\\n\", sep = \"\")",
           "  pass <<- pass + isTRUE(ok)",
           "}"]
    for c in calls:
        a, e, n = c["args"], c["expect"], c["n"]
        label = rq(f"{n:02d} {c['call']} {a.get('table', '')}")
        if c["call"] == "fetch":
            args = [rq(a["table"])]
            for k in ("entity", "variable"):
                if a.get(k):
                    args.append(f"{k} = c({', '.join(rq(x) for x in a[k])})")
            for k in ("start", "end"):
                if a.get(k):
                    args.append(f"{k} = {rq(a[k])}")
            out += [f"d <- erw_fetch({', '.join(args)}, backend = \"live\")",
                    "t <- if (\"event_date\" %in% names(d)) d$event_date else if (\"ts_utc\" %in% names(d)) d$ts_utc "
                    "else as.POSIXct(d$status_date, tz = \"UTC\")",
                    f"report(nrow(d) == {e['rows']} && stamp(min(t)) == {rq(e['first'])} && "
                    f"stamp(max(t)) == {rq(e['last'])}, {label})"]
        elif c["call"] == "cite":
            head = e["before_clause"].split(VIA)[0]
            out += [f"report(startsWith(erw_cite({rq(a['table'])}), {rq(head + VIA)}), {label})"]
        elif c["call"] == "license":
            out += [f"l <- erw_license({rq(a['table'])})",
                    f"report(l$verdict == {rq(e['verdict'])} && l$words == {rq(e['words'])}, {label})"]
        elif c["call"] == "refusal":
            out += [f"m <- tryCatch({{erw_fetch({rq(a['table'])}, start = \"2026-10-20\", backend = \"live\"); \"\"}}, "
                    "error = function(e) conditionMessage(e))",
                    f"report(m == {rq(e['message'])}, {label})"]
        elif c["call"] == "standard":
            out += [f"s <- erw_standard({rq(a['table'])}, backend = \"live\")",
                    f"report(s$shape == {rq(e['shape'])} && identical(s$key, c({', '.join(rq(k) for k in e['key'])})), {label})"]
        elif c["call"] == "tables":
            out += ["t <- erw_tables()",
                    f"report(nrow(t) == {e['tables']} && sum(t$verdict == \"public\") == {e['public']}, {label})"]
    out += [f"cat(pass, \"of {len(calls)} pass\\n\")"]
    return "\n".join(out) + "\n"


def main():
    calls = json.loads((HERE / "conformance.json").read_text(encoding="utf-8"))["calls"]
    (HERE / "run_stata.do").write_text(stata(calls), encoding="utf-8", newline="\n")
    (HERE / "run_r.R").write_text(r(calls), encoding="utf-8", newline="\n")
    print("wrote run_stata.do and run_r.R")


if __name__ == "__main__":
    main()
