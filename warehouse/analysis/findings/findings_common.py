"""Automated Analysis findings (session 170): what every finding module shares.

Named findings_common since session 173: as common.py it clashed with warehouse/analysis/templates/common.py when the whole
test suite ran in one process (the templates' module was already imported under that name, and the findings read it).

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


# Session 11405 (wip/ready-held-out, on Samuel's ruling only): a grid held for a license (license_status.held_grids:
# NYISO, ISO-NE and MISO) has no figure on a card or in its download. The cards built on several grids' prices
# (batteries_lunch_grids, gas_sets_price, peak_hour_grids) printed NYISO's and ISO-NE's yearly statistics and their
# CSVs held every row of them; the impact study's default control was NYISO New York City. withhold() is applied to
# every card by run_finding.run before it is written.
HELD_WORDS = {"nyiso": ("NYISO", "New York"), "isone": ("ISO-NE", "New England"), "miso": ("MISO",)}
HELD_NOTE = "license needed (the publisher's terms ask for written permission, and none is recorded)"


def held_grid_codes():
    """The lower-case codes of the grids held for a license today (license_status.held_grids)."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
    import license_status as lstat
    code = {"NYISO": "nyiso", "ISO-NE": "isone", "MISO": "miso"}
    return {code[g] for g in lstat.held_grids() if g in code}


def _held_re(held):
    import re
    words = [w for g in sorted(held) for w in HELD_WORDS.get(g, ())]
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b") if words else None


CLAIM_KEYS = ("title", "subtitle", "why", "in_words")   # a claim: any sentence naming a held grid is left out


def _clean_text(s, rx, strict=False):
    """A part between semicolons (a data line of a footnote) that names a held grid and holds a digit is left out; with
    strict (a claim's words), the whole sentence that names a held grid. Other sentences stay as they are. A sentence
    ends at ! ? or at a full stop after a small letter, a digit, a bracket or a percent sign, before a capital (so
    "N.Y.C. (" is not an end); a claim's sentence is not cut at a semicolon, so no half of it is left standing."""
    import re
    if not isinstance(s, str) or rx is None or not rx.search(s):
        return s
    ends = r"(?<=[!?])\s+|(?<=[a-z0-9)%]\.)\s+(?=[A-Z])"
    parts = re.split(ends if strict else r"(?<=;)\s+|" + ends, s)
    kept = [p for p in parts if not (rx.search(p) and (strict or re.search(r"\d", p)))]
    return " ".join(kept)


def _names_held(d, held, rx):
    if not isinstance(d, dict):
        return False
    if str(d.get("grid", "")).lower() in held:
        return True
    for k in ("label", "name", "measure", "title", "words", "numbers_key", "key"):
        v = d.get(k)
        if isinstance(v, str) and ((rx is not None and rx.search(v)) or any(v.lower().startswith(g + "_") for g in held)):
            return True
    return False


def _strip(x, held, rx, strict=False):
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if k.lower() in held or any(k.lower().startswith(g + "_") for g in held):
                continue
            out[k] = _strip(v, held, rx, strict or k in CLAIM_KEYS)
        return out
    if isinstance(x, list):
        return [_strip(v, held, rx, strict) for v in x if not _names_held(v, held, rx)]
    return _clean_text(x, rx, strict)


def withhold(card, rows, held=None, recompute=None):
    """(card, rows) with every figure of a held grid taken out: rows whose grid is held; the card's numbers of a held
    grid left out, a held grid's code out of a list, and with recompute the numbers made again from the rows kept
    (recompute(rows): the finding's numbers_from_rows, so the card equals its download); a callout side that names a held grid reads
    "license needed"; any list element (a chart panel, a series, a row of estimates) that names a held grid left out;
    any key of a held grid elsewhere left out; a sentence that names a held grid with a figure in it left out. A card
    that names no held grid comes back as it was."""
    held = held_grid_codes() if held is None else set(held)
    rx = _held_re(held)
    n_rows = len(rows) if rows else 0
    rows = [r for r in rows if str(r.get("grid", "")).lower() not in held] if rows else rows
    if rx is None or not rx.search(json.dumps(card, default=str)) and not any(
            k.split("_", 1)[0] in held for k in (card.get("numbers") or {})):
        return card, rows
    card = dict(card)
    nums = dict(card.get("numbers") or {})
    if recompute is not None and rows and len(rows) != n_rows:
        # the card's numbers are those of its download, which holds no held grid's row; a number the rows kept give
        # again (to 1e-9) keeps the value the card printed, so the card's other figures do not drift in the last digit
        was, nums = nums, dict(recompute(rows))
        for k, v in nums.items():
            o = was.get(k)
            if isinstance(v, float) and isinstance(o, (int, float)) and not isinstance(o, bool) and abs(v - o) <= 1e-9 * max(1.0, abs(o)):
                nums[k] = o
    nums = {k: ([x for x in v if str(x).lower() not in held] if isinstance(v, list) else v)
            for k, v in nums.items() if k.split("_", 1)[0].lower() not in held}
    callouts = []
    for c in card.get("callouts") or []:
        c = json.loads(json.dumps(c, default=str))
        for side in ("before", "after"):
            if isinstance(c.get(side), dict) and (rx.search(c.get("label", "")) or rx.search(str(c[side].get("period", "")))):
                c[side]["text"] = "license needed"
        callouts.append(c)
    keep = ("numbers", "callouts", "csv_header", "placeholders")
    out = _strip({k: v for k, v in card.items() if k not in keep}, held, rx)
    out["numbers"], out["callouts"] = nums, callouts
    if "csv_header" in card:
        out["csv_header"] = [_clean_text(ln, rx) for ln in card["csv_header"]]
    if "placeholders" in card:
        ph = [dict(p) for p in card["placeholders"]]
        shown = {str(p.get("grid", "")).lower() for p in ph}
        blob = json.dumps(card.get("chart", {}), default=str)
        for g in sorted(held):
            if g not in shown and (f'"grid": "{g}"' in blob or any(w in blob for w in HELD_WORDS[g])):
                ph.append({"grid": g, "words": HELD_WORDS[g][0], "text": "license needed"})
        out["placeholders"] = ph
    blob = json.dumps(card, default=str)
    named = [HELD_WORDS[g][0] for g in sorted(held) if any(w in blob for w in HELD_WORDS[g]) or f'"{g}_' in blob]
    card = {k: out[k] for k in list(card.keys()) if k in out}
    note = f"{', '.join(named)}: {HELD_NOTE}; their figures are left out of this card and its data."
    if named and HELD_NOTE not in (card.get("footnote") or ""):
        card["footnote"] = ((card.get("footnote") or "").rstrip() + " " + note).strip()
    return card, rows


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def table_path(name, in_dir=None):
    p = os.path.join(in_dir or DEFAULT_IN_DIR, name + ".csv")
    if not os.path.exists(p):
        raise NoData(f"table {name} is not in {in_dir or DEFAULT_IN_DIR}")
    return p


# Session 258: what a finding read, so that a source line can name the tables whose rows it used and no other. None
# until a caller opens record_reads(); then every read_table call adds {"table", "rows", "groups"}: the rows it kept,
# and, for a table of prices by market, the timestamps kept for each (market, node). Nothing a finding computes
# changes: the note is taken after the rows are read, and read_table returns what it returned before.
READS = None


class record_reads:
    """`with record_reads() as reads:` around a finding's compute(): reads is the list of what each read_table call
    kept, in the order the finding read. Closed, the recording stops and the list stays with the caller."""

    def __enter__(self):
        global READS
        self._before, READS = READS, []
        return READS

    def __exit__(self, *exc):
        global READS
        READS = self._before
        return False


def _note_read(name, df):
    groups = None
    if "market" in df.columns and "ts_utc" in df.columns:
        cols = ["market", "node"] if "node" in df.columns else ["market"]
        groups = {}
        for key, g in df.groupby(cols, sort=False):
            key = key if isinstance(key, tuple) else (key,)
            groups[(str(key[0]), str(key[1]) if len(key) > 1 else "")] = set(g["ts_utc"])
    READS.append({"table": name, "rows": int(len(df)), "groups": groups})


def only_tables_read(card, reads):
    """Session 258: a card names only the tables whose rows its finding used. A table the finding asked for and kept
    no row of leaves the card's tables, its source line and its CSV header; a table that brought rows always stays.
    When a named table was not read through read_table at all, nothing can be said and the card is returned as it is.
    Returns (the card, the tables left out)."""
    tables = list(card.get("tables") or [])
    asked = {rd["table"] for rd in reads}
    if not tables or any(t not in asked for t in tables):
        return card, []
    kept = [t for t in tables if any(rd["table"] == t and rd["rows"] for rd in reads)]
    if kept == tables or not kept:
        return card, []
    old, new = ", ".join(tables), ", ".join(kept)
    card = dict(card)
    card["tables"] = kept
    card["source_line"] = card["source_line"].replace(old, new)
    if card.get("csv_header"):
        card["csv_header"] = [ln.replace(old, new) for ln in card["csv_header"]]
    return card, [t for t in tables if t not in kept]


def header_lines(path):
    """The number of "#" lines at the top of a warehouse CSV (its provenance header), before the column names."""
    n = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def read_table(name, in_dir=None, usecols=None, keep=None, dtype=None):
    """A warehouse CSV (its # header skipped), in chunks, keeping the rows `keep(chunk)` selects. The whole ERCOT
    history is 3 million rows and 700 MB: one hub's real-time rows are read without holding the file."""
    p = table_path(name, in_dir)
    parts = []
    # session 3009: only the leading "#" lines are the header. comment="#" cut every line at its first "#", and a data
    # row with "#" inside a field (Berkeley Lab's queue: 1,581 project names such as "Solar #2") lost its later columns
    for ch in pd.read_csv(p, skiprows=header_lines(p), dtype=dtype or str, usecols=usecols, chunksize=CHUNK, keep_default_na=False):
        if keep is not None:
            ch = ch[keep(ch)]
        if len(ch):
            parts.append(ch)
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=usecols or [])
    if READS is not None:
        _note_read(name, df)
    return df


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
    # session 361: Newey-West errors beside HC1, for rows in time order (a month or a day after the one before): the
    # Bartlett kernel to NW_LAG(n) lags, with the same n / (n - k) as HC1 (Stata's `newey`). HC1 is unchanged and still
    # the card's figure; the new keys are added beside it.
    L = nw_lag(n)
    S = (X * e[:, None]).T @ (X * e[:, None])
    for j in range(1, L + 1):
        G = (X[j:] * e[j:, None]).T @ (X[:-j] * e[:-j, None])
        S += (1 - j / (L + 1)) * (G + G.T)
    V_nw = (n / (n - k)) * bread @ S @ bread
    se_nw = np.sqrt(np.maximum(np.diag(V_nw), 0))
    t_nw = beta / se_nw
    p_nw = 2 * stats.t.sf(np.abs(t_nw), n - k)
    return {"coef": {nm: {"coef": float(b), "se": float(s), "t": float(tt), "p": float(pp), "se_nw": float(sn), "t_nw": float(tn), "p_nw": float(pn)}
                     for nm, b, s, tt, pp, sn, tn, pn in zip(names, beta, se, t, p, se_nw, t_nw, p_nw)},
            "n": int(n), "k": int(k), "r2": r2, "se_kind": "HC1", "nw_lag": int(L)}


NW_RULE = "the Bartlett kernel to floor(4 (n / 100) ^ (2 / 9)) lags (Newey and West, 1994), with HC1's n / (n - k)"


def nw_lag(n):
    """Session 361: the Newey-West lag for n observations in time order, by Newey and West's (1994) rule of thumb."""
    return int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))


def bh_q(pvals):
    """Session 361: Benjamini-Hochberg q-values for a list of p-values (None stays None), in the list's order. A caveat
    on a round of claims, never a gate: q is the smallest false discovery rate at which the claim would be kept."""
    idx = [i for i, p in enumerate(pvals) if p is not None]
    m = len(idx)
    out = [None] * len(pvals)
    if not m:
        return out
    order = sorted(idx, key=lambda i: pvals[i])
    q, prev = [0.0] * m, 1.0
    for r in range(m, 0, -1):
        i = order[r - 1]
        prev = min(prev, pvals[i] * m / r)
        q[r - 1] = prev
    for r, i in enumerate(order):
        out[i] = min(1.0, q[r])
    return out


def trend_p(years, values):
    """Session 361: the p-value of a straight-line trend of a yearly series (ordinary least squares on the year, Student's
    t on n - 2 degrees of freedom). None under three years."""
    from scipy import stats
    if len(values) < 3:
        return None
    r = stats.linregress([float(y) for y in years], [float(v) for v in values])
    return float(r.pvalue)


def step_or_trend(years, values):
    """Session 361: a one-step fit (two levels, the break at the year that fits best, at least two years on each side)
    against a straight line, by the Bayesian information criterion (the step counts three parameters, the line two).
    None under four years. Returns {"step_better", "break_year", "before", "after", "bic_step", "bic_line", "words"}."""
    n = len(values)
    if n < 4:
        return None
    x = np.array([float(y) for y in years])
    v = np.array([float(a) for a in values])
    A = np.c_[np.ones(n), x]
    b = np.linalg.lstsq(A, v, rcond=None)[0]
    sse_line = float(((v - A @ b) ** 2).sum())
    best = None
    for k in range(2, n - 1):
        s = float(((v[:k] - v[:k].mean()) ** 2).sum() + ((v[k:] - v[k:].mean()) ** 2).sum())
        if best is None or s < best[0]:
            best = (s, k)
    sse_step, k = best
    bic = lambda sse, p: n * np.log(max(sse, 1e-12) / n) + p * np.log(n)  # noqa: E731
    bs, bl = float(bic(sse_step, 3)), float(bic(sse_line, 2))
    step = bs < bl
    first_after = str(years[k])
    words = (f"a step, not a trend: the years before {first_after} average {v[:k].mean():.4g} and the years from {first_after} {v[k:].mean():.4g}, "
             f"and two levels fit them better than a straight line" if step else "a trend: a straight line fits the years better than one step")
    return {"step_better": bool(step), "break_year": first_after, "before": float(v[:k].mean()), "after": float(v[k:].mean()),
            "bic_step": round(bs, 4), "bic_line": round(bl, 4), "words": words}


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
