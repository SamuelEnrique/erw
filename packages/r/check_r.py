#!/usr/bin/env python3
"""Session 1005 (chain 070): the R package erw, checked where R is not installed.

Energy Research Warehouse (ERW), docs/methods/packages.md. R is not on the code machine, so this checks what can be
checked without it; the owner runs the three commands of the session's report in R:

  syntax      every R file's brackets balance outside strings and comments, and every string's escapes are R's
  namespace   NAMESPACE exports exactly the functions marked #' @export, each defined
  description DESCRIPTION has its fields, imports only utils, suggests testthat
  addresses   .erw_live_url, run by a small interpreter of the R it is written in (assignments, paste0, gsub and grepl
              with fixed = TRUE, nchar, length, as.integer, if and else, for), gives for each call of the fixtures the
              address the Python package requested for it, string for string

    python packages/r/check_r.py          exit 0 when every check passes, 1 otherwise
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE / "erw"
CALLS = PKG / "tests" / "testthat" / "fixtures" / "calls.json"
ESCAPES = set("ntrbafv0\\\"'`xuU")


def scan(text, name):
    """(problems, code with strings and comments blanked): brackets balance; escapes are R's."""
    problems, out, stack, i = [], [], [], 0
    pairs = {")": "(", "]": "[", "}": "{"}
    while i < len(text):
        ch = text[i]
        if ch == "#":
            j = text.find("\n", i)
            j = len(text) if j < 0 else j
            out.append(" " * (j - i))
            i = j
            continue
        if ch in "\"'`":
            q, j = ch, i + 1
            while j < len(text) and text[j] != q:
                if text[j] == "\\":
                    if j + 1 < len(text) and text[j + 1] not in ESCAPES:
                        problems.append(f"{name}: the escape \\{text[j + 1]} is not R's (line {text[:j].count(chr(10)) + 1})")
                    j += 1
                j += 1
            if j >= len(text):
                problems.append(f"{name}: a string never closed")
            out.append(q + " " * (j - i - 1) + q)
            i = j + 1
            continue
        if ch in "([{":
            stack.append((ch, text[:i].count("\n") + 1))
        elif ch in ")]}":
            if not stack or stack[-1][0] != pairs[ch]:
                problems.append(f"{name}: {ch} on line {text[:i].count(chr(10)) + 1} closes nothing it opened")
            else:
                stack.pop()
        out.append(ch)
        i += 1
    for ch, line in stack:
        problems.append(f"{name}: {ch} opened on line {line} is never closed")
    return problems, "".join(out)


def check_namespace():
    problems = []
    src = (PKG / "R" / "erw.R").read_text(encoding="utf-8")
    marked = re.findall(r"#' @export\n(\w+) <- function", src)
    defined = set(re.findall(r"^([.\w]+) <- function", src, re.M))
    ns = re.findall(r"^export\((\w+)\)", (PKG / "NAMESPACE").read_text(encoding="utf-8"), re.M)
    if sorted(ns) != sorted(marked):
        problems.append(f"NAMESPACE exports {sorted(ns)}, the source marks {sorted(marked)}")
    for f in ns:
        if f not in defined:
            problems.append(f"{f} is exported and not defined")
    for need in ("erw_tables", "erw_coverage", "erw_fetch", "erw_cite", "erw_license", "erw_standard"):
        if need not in ns:
            problems.append(f"{need} is not exported")
    return problems


def check_description():
    d = (PKG / "DESCRIPTION").read_text(encoding="utf-8")
    problems = []
    for field in ("Package", "Title", "Version", "Authors@R", "Description", "License", "Depends", "Imports", "Suggests"):
        if not re.search(rf"^{re.escape(field)}:", d, re.M):
            problems.append(f"DESCRIPTION: no {field}")
    imports = re.search(r"^Imports: (.*)$", d, re.M)
    if imports and imports.group(1).strip() not in ("utils", "utils, stats"):   # session 1014: stats (setNames), base R too
        problems.append(f"DESCRIPTION: imports {imports.group(1)}, not base R's utils and stats")
    if "testthat" not in d:
        problems.append("DESCRIPTION: testthat is not suggested")
    return problems


# --- a small interpreter of the R .erw_live_url is written in ----------------------------------------------------

TOKEN = re.compile(r'\s*(?:(?P<str>"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')|(?P<num>\d+L?)|(?P<op>==|!=|>=|<=|&&|\|\||[(),!<>=])|(?P<id>[.\w]+))')


def tokens(s):
    out, i = [], 0
    while i < len(s):
        m = TOKEN.match(s, i)
        if not m or m.end() == i:
            if s[i:].strip() == "":
                break
            raise ValueError(f"cannot read: {s[i:]}")
        i = m.end()
        for k in ("str", "num", "op", "id"):
            if m.group(k) is not None:
                out.append((k, m.group(k)))
    return out


def rstr(lit):
    body = lit[1:-1]
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), body)


def length(v):
    return 0 if v is None else (len(v) if isinstance(v, list) else 1)


class Expr:
    def __init__(self, toks, env):
        self.t, self.i, self.env = toks, 0, env

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self, want=None):
        tok = self.peek()
        if want and tok[1] != want:
            raise ValueError(f"expected {want}, found {tok}")
        self.i += 1
        return tok

    def parse(self):
        left = self.unary()
        while self.peek()[1] in ("==", "!=", ">", "<", ">=", "<="):
            op = self.take()[1]
            right = self.unary()
            left = {"==": left == right, "!=": left != right, ">": left > right, "<": left < right,
                    ">=": left >= right, "<=": left <= right}[op]
        return left

    def unary(self):
        if self.peek()[1] == "!":
            self.take()
            return not self.unary()
        return self.primary()

    def primary(self):
        kind, val = self.take()
        if kind == "str":
            return rstr(val)
        if kind == "num":
            return int(val.rstrip("L"))
        if val == "(":
            v = self.parse()
            self.take(")")
            return v
        if val in ("TRUE", "FALSE"):
            return val == "TRUE"
        if val == "NULL":
            return None
        if self.peek()[1] == "(":
            self.take("(")
            args, named = [], {}
            while self.peek()[1] != ")":
                if self.peek()[0] == "id" and self.i + 1 < len(self.t) and self.t[self.i + 1][1] == "=":
                    k = self.take()[1]
                    self.take("=")
                    named[k] = self.parse()
                else:
                    args.append(self.parse())
                if self.peek()[1] == ",":
                    self.take(",")
            self.take(")")
            return self.call(val, args, named)
        if val not in self.env:
            raise ValueError(f"an unknown name: {val}")
        return self.env[val]

    @staticmethod
    def call(f, a, named):
        if f == "paste0":
            return "".join(str(x) for x in a)
        if f == "gsub" and named.get("fixed"):
            return str(a[2]).replace(a[0], a[1])
        if f == "grepl" and named.get("fixed"):
            return a[0] in str(a[1])
        if f == "nchar":
            return len(str(a[0]))
        if f == "length":
            return length(a[0])
        if f == "as.integer":
            return int(a[0])
        raise ValueError(f"a function the interpreter does not read: {f}")


def function_body(src, name):
    m = re.search(rf"^{re.escape(name)} <- function\((.*?)\) \{{\n", src, re.M | re.S)
    start = m.end()
    depth, i = 1, start
    while depth:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return m.group(1), src[start:i - 1]


def statements(body):
    """[(kind, head, children, else_branch)] from the body's lines (one statement or brace a line)."""
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("#")]

    def block(k):
        out = []
        while k < len(lines):
            s = lines[k]
            k += 1
            if s == "}" or s.startswith("} else"):
                return out, k
            m = re.match(r"^if \((.*)\) \{$", s)
            if m:
                kids, k = block(k)
                node = ["if", m.group(1), kids, None]
                out.append(node)
                while k > 0 and lines[k - 1].startswith("} else"):
                    prev = lines[k - 1]
                    m2 = re.match(r"^\} else if \((.*)\) \{$", prev)
                    kids2, k = block(k)
                    branch = ["if", m2.group(1), kids2, None] if m2 else ["else", None, kids2, None]
                    node[3] = branch
                    node = branch
                continue
            m = re.match(r"^for \((\w+) in (\w+)\) \{$", s)
            if m:
                kids, k = block(k)
                out.append(["for", (m.group(1), m.group(2)), kids, None])
                continue
            out.append(["stmt", s, None, None])
        return out, k
    return block(0)[0]


def run(block, env):
    result = None
    for kind, head, kids, alt in block:
        if kind == "stmt":
            m = re.match(r"^([.\w]+) <- (.*)$", head)
            if m:
                env[m.group(1)] = Expr(tokens(m.group(2)), env).parse()
            else:
                result = Expr(tokens(head), env).parse()
        elif kind == "for":
            var, src = head
            for v in env.get(src) or []:
                env[var] = v
                run(kids, env)
        elif kind == "if":
            node = [kind, head, kids, alt]
            while node:
                if node[0] == "else" or Expr(tokens(node[1]), env).parse():
                    r = run(node[2], env)
                    result = r if r is not None else result
                    break
                node = node[3]
    return result


def r_url(src, call, shape):
    params, body = function_body(src, ".erw_live_url")
    env = {"table": call["table"], "base": "<ERW_LIVE_URL>", "shape": shape, "offset": 0, "limit": 1000,
           "entity": call.get("entity"), "variable": call.get("variable"), "start": call.get("start"),
           "end": call.get("end")}
    return run(statements(body), env)


def check_addresses():
    src = (PKG / "R" / "erw.R").read_text(encoding="utf-8")
    rec = json.loads(CALLS.read_text(encoding="utf-8"))
    problems, lines = [], []
    for c in rec["calls"]:
        head = (CALLS.parent / c["file"]).read_text(encoding="utf-8").splitlines()[0].split(",")
        cols = [x for x in head if x != "table_name"]
        shape = "entities" if cols[:2] == ["entity_id", "entity_type"] else ("events" if cols[0] == "event_id" else "series")
        got = r_url(src, c["call"], shape)
        ok = got == c["addresses"][0]
        lines.append(f"{'ok  ' if ok else 'DIFF'} {c['n']:02d} {c['call']['table']}")
        if not ok:
            problems.append(f"call {c['n']}: R {got} | Python {c['addresses'][0]}")
    return problems, lines


def main() -> int:
    problems = []
    for f in sorted(PKG.rglob("*.R")):
        text = f.read_text(encoding="utf-8")
        problems += scan(text, str(f.relative_to(PKG)))[0]
        if chr(0x2014) in text or chr(0x2013) in text:
            problems.append(f"{f.name}: an em or en dash")
    problems += check_namespace() + check_description()
    p, lines = check_addresses()
    problems += p
    for ln in lines:
        print(ln)
    print(f"{len(lines)} addresses compared; {len(problems)} problem(s)")
    for pr in problems:
        print("  " + pr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
