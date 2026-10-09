"""Automated Analysis findings (session 170): what every finding module shares.

Energy Research Warehouse (ERW). A finding is a module in this folder that declares

    NAME      the finding's id (a slug)
    TITLE     the section title in capitals, as on the thesis's peak premium panel
    KIND      "visual" (trend, map, distribution) or "econometric" (event study, before and after with controls,
              fixed-effects regression with standard errors, shown as a table with the effect in plain words)
    INPUTS    {name: {"label", "default", "choices"}}: what a person picks on /analysis
    TABLES    the warehouse tables it reads
    compute(params, in_dir) -> (rows, meta): rows is the finding's data table (a list of dicts, the CSV download);
              meta holds what the rows alone cannot say (the source line, the terms quoted, the fit's design)
    card(rows, params, meta) -> the card: every number on it computed from rows, so that a test can read the CSV
              download back and prove the card (numbers_from_rows is that proof)
    stata(params) -> the do-file text, written to the owner's rules (see do_file below)

Tables are read from the warehouse's output directory (ERW_DATA_DIR, else warehouse/output of this checkout). A
table that is not there raises NoData, and the caller says so: nothing is filled in.
"""

import datetime as dt
import hashlib
import io
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_IN_DIR = os.environ.get("ERW_DATA_DIR") or os.path.join(ROOT, "warehouse", "output")
METHOD = "docs/methods/automated_analysis_findings.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/" + METHOD
CHUNK = 400_000


class NoData(Exception):
    """A table the finding reads is not on this machine (the runner has none; a working copy has none)."""


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def table_path(name, in_dir=None):
    p = os.path.join(in_dir or DEFAULT_IN_DIR, name + ".csv")
    if not os.path.exists(p):
        raise NoData(f"table {name} is not in {in_dir or DEFAULT_IN_DIR}")
    return p


def read_table(name, in_dir=None, usecols=None, keep=None, dtype=None):
    """A warehouse CSV (its # header skipped), in chunks, keeping the rows `keep(chunk)` selects. The whole ERCOT
    history is 3 million rows and 700 MB: one hub's real-time rows are read without holding the file."""
    p = table_path(name, in_dir)
    parts = []
    for ch in pd.read_csv(p, comment="#", dtype=dtype or str, usecols=usecols, chunksize=CHUNK, keep_default_na=False):
        if keep is not None:
            ch = ch[keep(ch)]
        if len(ch):
            parts.append(ch)
    if not parts:
        return pd.DataFrame(columns=usecols or [])
    return pd.concat(parts, ignore_index=True)


def to_utc(s):
    return pd.to_datetime(s, format="%Y-%m-%dT%H:%M:%SZ", utc=True)


def pct(v, p):
    return float(np.percentile(v, p))  # numpy's default, linear: the peak premium method's percentile


def ols_hc1(y, X, names):
    """Ordinary least squares with HC1 (heteroskedasticity-robust) standard errors, as Stata's `regress, vce(robust)`.
    Returns {name: {coef, se, t, p}} with n, k, r2. p from Student's t on n - k degrees of freedom (scipy)."""
    from scipy import stats
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n, k = X.shape
    bread = np.linalg.inv(X.T @ X)
    beta = bread @ X.T @ y
    e = y - X @ beta
    meat = (X * (e ** 2)[:, None]).T @ X
    V = (n / (n - k)) * bread @ meat @ bread
    se = np.sqrt(np.diag(V))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), n - k)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float((e ** 2).sum()) / ss_tot if ss_tot > 0 else float("nan")
    return {"coef": {nm: {"coef": float(b), "se": float(s), "t": float(tt), "p": float(pp)}
                     for nm, b, s, tt, pp in zip(names, beta, se, t, p)},
            "n": int(n), "k": int(k), "r2": r2, "se_kind": "HC1"}


def round6(x):
    if x is None:
        return None
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return None
    return round(float(x), 6)


def fmt(x, nd=1):
    """A number as the card prints it: thousands separated, nd decimals, no trailing noise."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "not held"
    if nd == 0:
        return f"{x:,.0f}"
    return f"{x:,.{nd}f}"


def callout(label, before_label, before, after_label, after, unit=""):
    """A before-and-after box: 'Daily spread: USD 8 in 2015, USD 34 in 2025'."""
    return {"label": label, "before": {"period": before_label, "text": before}, "after": {"period": after_label, "text": after}, "unit": unit}


def write_card(card, rows, py_source_path, do_text, out_dir, finding_id, csv_name):
    """The card's JSON, its CSV download, its Python and its do-file, into out_dir. Every number of the card is in
    card["numbers"], keyed, so that a test can compare it with numbers_from_rows."""
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, csv_name)
    df = pd.DataFrame(rows)
    buf = io.StringIO()
    for ln in card["csv_header"]:
        buf.write("# " + ln + "\n")
    df.to_csv(buf, index=False, lineterminator="\n")
    with open(csv_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(buf.getvalue())
    with open(py_source_path, encoding="utf-8") as f:
        py = f.read()
    with open(os.path.join(out_dir, finding_id + ".py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(py)
    with open(os.path.join(out_dir, finding_id + ".do"), "w", encoding="utf-8", newline="\n") as f:
        f.write(do_text)
    card = dict(card)
    card["downloads"] = {"csv": csv_name, "python": finding_id + ".py", "stata": finding_id + ".do"}
    card["csv_sha256"] = hashlib.sha256(buf.getvalue().encode("utf-8")).hexdigest()
    with open(os.path.join(out_dir, finding_id + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(card, f, indent=1, ensure_ascii=False, default=round6)
        f.write("\n")
    return os.path.join(out_dir, finding_id + ".json")


def read_rows_csv(path):
    """The CSV download read back, numbers as numbers, blanks as None (for the reproduction test)."""
    d = pd.read_csv(path, comment="#", keep_default_na=True)
    return d.astype(object).where(pd.notna(d), None).to_dict("records")


def do_file(lines):
    """A Stata do-file to the owner's rules: no line continuation operators; one empty line between commands outside a
    loop and none inside; every variable destrung with force; per-variable sentinel recoding before any reshape loop;
    file names like study_year_topic_word.csv. `lines` is a list of commands; a list inside it is a loop block whose
    commands are written without empty lines between them."""
    out = []
    for item in lines:
        if isinstance(item, list):
            out.append("\n".join(item))
        else:
            out.append(item)
    text = "\n\n".join(out) + "\n"
    assert "///" not in text and "/*" not in text, "no line continuation in a do-file"
    return text


def do_destring(variables):
    return [f"destring {v}, replace force" for v in variables]


def do_sentinels(variables, sentinel=-999):
    return [f"replace {v} = . if {v} == {sentinel}" for v in variables]
