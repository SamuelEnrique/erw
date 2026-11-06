#!/usr/bin/env python3
"""Every reproduce.do of the findings hunt read against its reproduce.py and the owner's Stata rules (chain 164, session 3021).

Energy Research Warehouse (ERW). This machine has no Stata; the owner runs the files. What a reader can check is
checked for every draft of docs/findings/<family>/:

    expected     the "* Expected:" line at the top names the same years, figures and change as the Python script's
    rules        no line continuation (/// or /*); one empty line between commands outside a loop (do_file's form: no
                 block holds two lines, these files have no loop); every import reads every column as a string
                 (stringcols(_all)) and every destring says force
    by           no gsort with a descending key before a by (gsort does not mark the data as sorted for by; session
                 3021 rewrote six kinds of file to bysort on a negated variable)
    leftovers    no brace left from the code that wrote the file
    the end      the file lists year, measure and n, the figures the Python script prints

    python warehouse/analysis/findings/deep/check_do.py

Exit 0 every file holds; 1 one or more do not.
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "docs", "findings"))


def problems(do, py):
    out = []
    head_do = next((ln for ln in do.split("\n")[:2] if ln.startswith("* Expected:")), None)
    head_py = next((ln for ln in py.split("\n")[:2] if ln.startswith("# Expected:")), None)
    if not head_do or not head_py or head_do[1:] != head_py[1:]:
        out.append("the expected line is not the Python script's")
    if "///" in do or "/*" in do:
        out.append("a line continuation or a block comment")
    blocks = do.strip("\n").split("\n\n")
    if any("\n" in b for b in blocks):
        out.append("a block holds two lines")
    for b in blocks:
        if b.startswith("import delimited") and ("stringcols(_all)" not in b or "varnames(1)" not in b):
            out.append("an import that does not read every column as a string")
        if b.startswith("destring") and not b.rstrip().endswith("replace force"):
            out.append("a destring without force")
    if re.search(r"^gsort .*-", do, re.M):
        out.append("gsort with a descending key")
    if re.search(r"[{}]", do.replace("{this file}", "")):
        out.append("a brace left from the code")
    if not do.rstrip().endswith("list year measure n, noobs"):
        out.append("it does not end by listing year, measure and n")
    if "destring" not in do:
        out.append("no destring at all")
    return out


def main():
    bad, n = 0, 0
    for do_path in sorted(glob.glob(os.path.join(DOCS, "*", "*.reproduce.do"))):
        n += 1
        py_path = do_path[:-3] + ".py"
        p = problems(open(do_path, encoding="utf-8").read(), open(py_path, encoding="utf-8").read() if os.path.exists(py_path) else "")
        if p:
            bad += 1
            print(f"FAIL {os.path.relpath(do_path, DOCS)}: {'; '.join(p)}")
    print(f"{n - bad} of {n} do-files hold")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
