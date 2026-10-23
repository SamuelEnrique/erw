#!/usr/bin/env python3
"""Session 1003 (chain 070): erw.ado and erw.sthlp, checked where Stata is not installed.

Energy Research Warehouse (ERW), docs/methods/packages.md. Stata is not on the code machine, so this checks what can be
checked without it, and the owner runs the three commands of the session's report in Stata:

  structure   every `program define` has its `end`, the braces of each program balance, every `_erw_*` program called
              is defined and every one defined is called, no line continuation (`///`), no em or en dash
  style       the owner's Stata: one empty line between commands outside a block, none inside a block (a comment line
              belongs to the command under it)
  help        erw.sthlp has its sections, names the six subcommands and every option of `erw fetch`
  install     stata.toc names the package erw, and erw.pkg lists files that exist (session 1004)
  examples    examples.do in the same style, every erw call in it one of the six, no line continuation (session 1004)
  addresses   `_erw_live_url`, run by a small interpreter of the Stata it is written in (locals, `subinstr`, `if`,
              `foreach`, `strpos`, `strlen`), gives for each call of fixtures/calls.json the address the Python package
              requested for it, string for string

    python packages/stata/check_ado.py          exit 0 when every check passes, 1 otherwise
"""

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADO = HERE / "erw.ado"
HLP = HERE / "erw.sthlp"
TOC = HERE / "stata.toc"
PKG = HERE / "erw.pkg"
DO = HERE / "examples.do"
CALLS = HERE / "fixtures" / "calls.json"
SUBCOMMANDS = ("tables", "coverage", "fetch", "cite", "license", "standard")


def programs(text):
    """{name: [lines]} of each program's body, and the problems of the structure."""
    out, problems, name, body = {}, [], None, []
    for i, ln in enumerate(text.splitlines(), 1):
        s = ln.strip()
        m = re.match(r"^program define (\w+)", s)
        if m:
            if name:
                problems.append(f"line {i}: program {m.group(1)} begins inside program {name}")
            name, body = m.group(1), []
            continue
        if s == "end" and name:
            out[name] = body
            name = None
            continue
        if name:
            body.append(ln)
        elif s and not s.startswith("*"):
            problems.append(f"line {i}: a command outside any program: {s[:60]}")
    if name:
        problems.append(f"program {name} has no end")
    return out, problems


def check_structure(text, progs):
    problems = []
    if "///" in text:
        problems.append("a line continuation (///)")
    for ch, label in ((chr(0x2014), "em dash"), (chr(0x2013), "en dash")):
        if ch in text:
            problems.append(f"an {label}")
    for name, body in progs.items():
        depth = 0
        for ln in body:
            s = ln.strip()
            if s.endswith("{"):
                depth += 1
            if s == "}":
                depth -= 1
            if depth < 0:
                problems.append(f"{name}: a closing brace with no block")
        if depth != 0:
            problems.append(f"{name}: braces do not balance ({depth})")
    called = set(re.findall(r"(?<![\w])(_erw_\w+)", "\n".join("\n".join(b) for b in progs.values())))
    defined = {n for n in progs if n.startswith("_erw_")}
    for n in sorted(called - defined):
        problems.append(f"{n} is called and not defined")
    for n in sorted(defined - called):
        problems.append(f"{n} is defined and never called")
    return problems


def check_style(progs):
    """Outside a block: units (comment lines, then a command with its block) are separated by exactly one empty line,
    with none after `program define` or before `end`. Inside a block: no empty line."""
    problems = []
    for name, body in progs.items():
        depth, blank_run, first = 0, 0, True
        for k, ln in enumerate(body):
            s = ln.strip()
            if not s:
                if depth > 0:
                    problems.append(f"{name}: an empty line inside a block (body line {k + 1})")
                blank_run += 1
                continue
            if depth == 0:
                prev = next((b.strip() for b in reversed(body[:k]) if b.strip()), "")
                after_comment = prev.startswith("*") or prev.startswith("//")
                continuing = s.startswith("else")
                if first:
                    if blank_run:
                        problems.append(f"{name}: an empty line after program define")
                elif continuing:
                    if blank_run:
                        problems.append(f"{name}: an empty line before else (body line {k + 1})")
                elif after_comment and blank_run == 0:
                    pass
                elif blank_run != 1:
                    problems.append(f"{name}: {blank_run} empty lines before body line {k + 1} ({s[:40]})")
                first = False
            if s.endswith("{"):
                depth += 1
            if s == "}":
                depth -= 1
            blank_run = 0
        if body and not body[-1].strip():
            problems.append(f"{name}: an empty line before end")
    return problems


def check_help(text, ado):
    problems = []
    for marker in ("syntax", "description", "install", "options", "held", "examples", "results", "citation"):
        if f"{{marker {marker}}}" not in text:
            problems.append(f"help: no section {marker}")
    for sub in SUBCOMMANDS:
        if f"{{cmd:erw {sub}}}" not in text:
            problems.append(f"help: erw {sub} is not in the syntax")
    m = re.search(r"program define _erw_fetch.*?\n\s*syntax ([^\n]+)", ado, re.S)
    opts = re.findall(r"([A-Za-z]+)\((?:string|integer[^)]*)\)", m.group(1)) if m else []
    for o in opts:
        if f"{{opt {o.lower()[:len(o)]}" not in text.lower() and f"opt {re.sub('[a-z]', '', o).lower()}" not in text.lower():
            if o.lower() not in text.lower():
                problems.append(f"help: the option {o.lower()} of erw fetch is not described")
    return problems


# --- a small interpreter of the Stata _erw_live_url is written in ------------------------------------------------

def expand(s, locs):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"`([A-Za-z_]\w*)'", lambda m: locs.get(m.group(1), ""), s)
    return s


def unquote(s):
    s = s.strip()
    return s[1:-1] if len(s) >= 2 and s[0] == '"' and s[-1] == '"' else s


def condition(c, locs):
    c = expand(c, locs).strip()
    m = re.fullmatch(r'"([^"]*)"\s*(==|!=)\s*"([^"]*)"', c)
    if m:
        return (m.group(1) == m.group(3)) == (m.group(2) == "==")
    m = re.fullmatch(r'strpos\("([^"]*)",\s*"([^"]*)"\)\s*(>|==)\s*(\d+)', c)
    if m:
        v = m.group(1).find(m.group(2)) + 1
        return v > int(m.group(4)) if m.group(3) == ">" else v == int(m.group(4))
    m = re.fullmatch(r'strlen\("([^"]*)"\)\s*==\s*(\d+)', c)
    if m:
        return len(m.group(1)) == int(m.group(2))
    raise ValueError(f"a condition the interpreter does not read: {c}")


def parse_block(lines, i=0):
    """[(statement, children)] until a closing brace."""
    out = []
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        if not s or s.startswith("*"):
            continue
        if s == "}":
            return out, i
        if s.endswith("{"):
            kids, i = parse_block(lines, i)
            out.append((s[:-1].strip(), kids))
        else:
            out.append((s, None))
    return out, i


def run(block, locs, result):
    k = 0
    while k < len(block):
        s, kids = block[k]
        k += 1
        if s.startswith("syntax "):
            continue
        if s.startswith("if "):
            chain = [(s[3:], kids)]
            while k < len(block) and block[k][0].startswith("else"):
                e, ek = block[k]
                k += 1
                chain.append((e[8:] if e.startswith("else if ") else None, ek))
            for cond, ck in chain:
                if cond is None or condition(cond, locs):
                    run(ck, locs, result)
                    break
            continue
        m = re.fullmatch(r"foreach (\w+) of local (\w+)", s)
        if m:
            for w in locs.get(m.group(2), "").split():
                locs[m.group(1)] = w
                run(kids, locs, result)
            continue
        m = re.fullmatch(r'local (\w+) : subinstr local (\w+) "([^"]*)" "([^"]*)", all', s)
        if m:
            locs[m.group(1)] = locs.get(m.group(2), "").replace(m.group(3), m.group(4))
            continue
        m = re.fullmatch(r"local (\w+) (.*)", s)
        if m:
            locs[m.group(1)] = expand(unquote(m.group(2)), locs)
            continue
        m = re.fullmatch(r"return local (\w+) (.*)", s)
        if m:
            result[m.group(1)] = expand(unquote(m.group(2)), locs)
            continue
        raise ValueError(f"a statement the interpreter does not read: {s}")


def stata_url(body, call, shape):
    block, _ = parse_block(body)
    locs = {"table": call["table"], "base": "<ERW_LIVE_URL>", "shape": shape, "offset": "0", "limit": "1000",
            "entity": " ".join(call.get("entity", [])), "variable": " ".join(call.get("variable", [])),
            "start": call.get("start", ""), "end": call.get("end", ""),
            "market": call.get("market", ""), "ba": call.get("ba", ""), "year": str(call.get("year", ""))}
    result = {}
    run(block, locs, result)
    return result.get("url", "")


def check_addresses(progs):
    problems, lines = [], []
    rec = json.loads(CALLS.read_text(encoding="utf-8"))
    with open(ROOT / "warehouse" / "metadata" / "coverage.csv", encoding="utf-8") as f:
        interval = {r["table"]: r["interval"] for r in csv.DictReader(f)}
    for c in rec["calls"]:
        call = c["call"]
        i = interval.get(call["table"], "")
        shape = "entities" if i == "snapshot" else ("events" if i == "event" else "series")
        got = stata_url(progs["_erw_live_url"], call, shape)
        want = c["addresses"][0]
        ok = got == want
        lines.append(f"{'ok  ' if ok else 'DIFF'} {c['n']:02d} {call['table']}")
        if not ok:
            problems.append(f"call {c['n']}: Stata {got} | Python {want}")
    return problems, lines


def check_install():
    problems = []
    toc = TOC.read_text(encoding="utf-8").splitlines()
    if not toc or toc[0] != "v 3" or not any(ln.startswith("p erw ") for ln in toc):
        problems.append("stata.toc: no 'v 3' first line or no 'p erw' line")
    pkg = PKG.read_text(encoding="utf-8").splitlines()
    files = [ln[2:].strip() for ln in pkg if ln.startswith("f ")]
    if not pkg or pkg[0] != "v 3" or not files:
        problems.append("erw.pkg: no 'v 3' first line or no file")
    for f in files:
        if not (HERE / f).is_file():
            problems.append(f"erw.pkg lists {f}, which does not exist")
    for need in ("erw.ado", "erw.sthlp"):
        if need not in files:
            problems.append(f"erw.pkg does not list {need}")
    return problems


def check_do(text):
    problems = []
    if "///" in text:
        problems.append("examples.do: a line continuation (///)")
    for ch in (chr(0x2014), chr(0x2013)):
        if ch in text:
            problems.append("examples.do: an em or en dash")
    body = [ln for ln in text.splitlines()]
    start = next((i for i, ln in enumerate(body) if ln.strip() and not ln.strip().startswith("*")), 0)
    problems += [p.replace("examples", "examples.do", 1) for p in check_style({"examples": body[start:]})]
    for sub in re.findall(r"^\s*erw (\w+)", text, re.M):
        if sub not in SUBCOMMANDS:
            problems.append(f"examples.do: erw {sub} is not one of the six")
    return problems


def main() -> int:
    ado = ADO.read_text(encoding="utf-8")
    progs, problems = programs(ado)
    problems += check_structure(ado, progs)
    problems += check_style(progs)
    problems += check_help(HLP.read_text(encoding="utf-8"), ado)
    problems += check_install()
    problems += check_do(DO.read_text(encoding="utf-8"))
    p, lines = check_addresses(progs)
    problems += p
    for ln in lines:
        print(ln)
    print(f"{len(progs)} programs; {len(lines)} addresses compared; {len(problems)} problem(s)")
    for pr in problems:
        print("  " + pr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
