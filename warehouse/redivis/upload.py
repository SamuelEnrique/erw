#!/usr/bin/env python3
"""Upload ERW tables to the Redivis draft of energy_research_warehouse (session 10).

Energy Research Warehouse (ERW). Modeled on the IRW's red_up
(github.com/ben-domingue/irw, src/red_up): one uploader, a validator gate, a
true replace, a count(*) proof, and never a release.

    python warehouse/redivis/upload.py --all            # every table in warehouse/output, plus metadata
    python warehouse/redivis/upload.py --changed        # only tables whose data changed since the last upload
    python warehouse/redivis/upload.py t1 t2            # these tables
    python warehouse/redivis/upload.py --reconcile      # count(*) of every Redivis table against its CSV
    python warehouse/redivis/upload.py --restore        # CI: download the rolling-window tables missing locally

Owner, dataset, numeric columns and the restore list come from
warehouse/redivis/config.yaml; the token from REDIVIS_API_TOKEN (.env or the
environment), never printed. Exit 1 if any table fails (upload, validator or
row count), 2 on bad input.

For each table:
1. The validator (warehouse/validate/erw_validate.py) must pass, or the table is
   not uploaded.
2. The provenance header (the leading '#' lines) is taken out of the file and
   becomes the table's description, with its license from coverage.csv. Only
   the header row and data rows are uploaded.
3. True replace: Redivis uploads append, so an existing draft table is deleted
   and recreated (red_up's finding: replace_on_conflict leaves rows inherited
   from a released version beside the new ones, doubling the table).
4. Proof: `select count(*)` against the draft table must equal the CSV's data
   rows, or the table is reported failed.
5. The dataset stays an unreleased draft. This script never releases a version;
   releasing is a human click (warehouse/redivis/README.md).
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
TMP = os.path.join(ROOT, "runs", "redivis")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
CONFIG = yaml.safe_load(open(os.path.join(HERE, "config.yaml"), encoding="utf-8"))
MANIFEST = os.path.join(ROOT, CONFIG["manifest"])
MANIFEST_COLS = ["table", "data_sha256", "rows", "uploaded_at", "redivis_table"]
DESC_MAX = 2000  # Redivis's limit on a table description (HTTP 400 above it)
HEADERS_TABLE = "erw_headers"  # every provenance header line of every table, in full


def secret(name):
    v = os.environ.get(name)
    if not v:
        from dotenv import dotenv_values
        v = (dotenv_values(os.path.join(ROOT, ".env")).get(name) or "").strip()
    if not v:
        raise SystemExit(f"{name} is not set (.env or environment); nothing uploaded")
    return v.strip()


def log(msg):
    print(msg, flush=True)


def split_header(path):
    """(header lines without '# ', data text starting at the column header row)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    n = 0
    while n < len(lines) and lines[n].startswith("#"):
        n += 1
    header = [ln[1:].strip() for ln in lines[:n]]
    return header, "\n".join(lines[n:])


def data_rows(data_text):
    df = pd.read_csv(io.StringIO(data_text), dtype=str, keep_default_na=False, na_values=[])
    return df


def sha(data_text):
    return hashlib.sha256(data_text.encode("utf-8")).hexdigest()


def licenses():
    cov = pd.read_csv(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), dtype=str,
                      keep_default_na=False)
    return dict(zip(cov["table"], cov["license"]))


def description(name, header, license_):
    lines = [f"ERW table {name}. License: {license_} (warehouse/metadata/coverage.csv; "
             "internal means licensed for internal use only, never for the public site).",
             "Provenance header of the ERW file (docs/datastandard.md):"] + header
    text = "\n".join(lines)
    if len(text) > DESC_MAX:
        note = f"\n[cut at {DESC_MAX:,} characters, Redivis's limit; every header line is in table {HEADERS_TABLE}]"
        text = text[:DESC_MAX - len(note)] + note
    return text


def open_draft():
    """The dataset's unreleased draft, created if the last version was released (red_up.push.open_draft)."""
    os.environ["REDIVIS_API_TOKEN"] = secret(CONFIG["token_env"])
    import redivis
    owner = secret(CONFIG["owner_env"])
    acct = redivis.user(owner) if CONFIG["owner_kind"] == "user" else redivis.organization(owner)
    ds = acct.dataset(CONFIG["dataset"])
    if not ds.exists():
        raise SystemExit(f"Redivis dataset {owner}.{CONFIG['dataset']} does not exist; create it on Redivis first")
    ds.create_next_version(if_not_exists=True)
    return acct.dataset(CONFIG["dataset"], version="next")


def count_rows(table):
    import redivis
    ref = table.get().properties["qualifiedReference"]
    rows = redivis.query(f"select count(*) as n from `{ref}`").to_arrow_table(progress=False).to_pylist()
    return int(rows[0]["n"])


def push(ds, name, header, data_text, license_, events=False):
    """Replace one draft table with this data; return (expected, actual)."""
    df = data_rows(data_text)
    expected = len(df)
    if expected == 0:
        raise RuntimeError("no data rows; an empty table is never uploaded")
    os.makedirs(TMP, exist_ok=True)
    tmp = os.path.join(TMP, f"{name}.csv")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(data_text if data_text.endswith("\n") else data_text + "\n")
    table = ds.table(name)
    if table.exists():
        table.delete()  # the only true replace (see the module docstring)
        table = ds.table(name)
    table = table.create(description=description(name, header, license_))
    try:
        with open(tmp, "rb") as fh:
            table.upload(f"{name}.csv").create(
                fh, type="delimited", delimiter=",",
                has_header_row=True, has_quoted_newlines=True, null_markers=[""],
                remove_on_fail=True, wait_for_finish=True, raise_on_fail=True, progress=False)
    except Exception:
        try:
            table.delete()  # never leave an empty table in the draft
        except Exception:
            pass
        raise
    finally:
        os.remove(tmp)
    return expected, count_rows(table)


def read_manifest():
    if os.path.exists(MANIFEST):
        return pd.read_csv(MANIFEST, dtype=str, keep_default_na=False)
    return pd.DataFrame(columns=MANIFEST_COLS)


def write_manifest(m):
    m = m.sort_values("table")[MANIFEST_COLS]
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    m.to_csv(MANIFEST, index=False, lineterminator="\n")


def tables_on_disk():
    return sorted(os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".csv"))


def run_upload(names, include_metadata):
    import erw_validate
    ds = open_draft()
    lic = licenses()
    man = read_manifest().set_index("table")
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    for name in names:
        path = os.path.join(OUT, name + ".csv")
        try:
            rep = erw_validate.validate(path)
            if rep["errors"]:
                raise RuntimeError(f"validator blocked it: {rep['errors'][0]['check']}: {rep['errors'][0]['detail'][:200]}")
            header, data = split_header(path)
            if name not in lic:
                raise RuntimeError("not in coverage.csv; run build_coverage.py first")
            expected, actual = push(ds, name, header, data, lic[name],
                                    events=list(data_rows(data).columns[:1]) == ["event_id"])
            ok = expected == actual
            results.append((name, expected, actual, "" if ok else "row count mismatch"))
            if ok:
                man.loc[name, ["data_sha256", "rows", "uploaded_at", "redivis_table"]] = [
                    sha(data), str(expected), now, name]
            log(f"{'ok  ' if ok else 'FAIL'} {name}: CSV {expected:,} rows, Redivis count(*) {actual:,}")
        except Exception as exc:
            results.append((name, None, None, f"{type(exc).__name__}: {exc}"))
            log(f"FAIL {name}: {type(exc).__name__}: {exc}")
    if include_metadata:
        # every header line of every table on disk, in full (descriptions stop at 2,000 characters)
        hrows = []
        for name in tables_on_disk():
            for i, line in enumerate(split_header(os.path.join(OUT, name + ".csv"))[0], 1):
                hrows.append((name, i, line))
        hdata = pd.DataFrame(hrows, columns=["table", "line_no", "line"]).to_csv(index=False, lineterminator="\n")
        try:
            expected, actual = push(ds, HEADERS_TABLE, [f"Provenance header lines of every ERW table, uploaded {now}"],
                                    hdata, "public")
            ok = expected == actual
            results.append((HEADERS_TABLE, expected, actual, "" if ok else "row count mismatch"))
            log(f"{'ok  ' if ok else 'FAIL'} {HEADERS_TABLE}: {expected:,} header lines, Redivis count(*) {actual:,}")
        except Exception as exc:
            results.append((HEADERS_TABLE, None, None, f"{type(exc).__name__}: {exc}"))
            log(f"FAIL {HEADERS_TABLE}: {type(exc).__name__}: {exc}")
        for rname, rel in CONFIG["metadata_tables"].items():
            path = os.path.join(ROOT, rel)
            try:
                with open(path, encoding="utf-8") as f:
                    data = f.read()
                expected, actual = push(ds, rname, [f"ERW metadata file {rel}, uploaded {now}"], data, "public")
                ok = expected == actual
                results.append((rname, expected, actual, "" if ok else "row count mismatch"))
                log(f"{'ok  ' if ok else 'FAIL'} {rname} ({rel}): CSV {expected:,} rows, Redivis count(*) {actual:,}")
            except Exception as exc:
                results.append((rname, None, None, f"{type(exc).__name__}: {exc}"))
                log(f"FAIL {rname}: {type(exc).__name__}: {exc}")
    write_manifest(man.reset_index().rename(columns={"index": "table"}))
    failed = [r for r in results if r[3]]
    log(f"uploaded {len(results) - len(failed)} of {len(results)} tables to the draft of "
        f"{CONFIG['dataset']}; nothing released")
    return 1 if failed else 0


def changed_tables():
    man = read_manifest().set_index("table")
    out = []
    for name in tables_on_disk():
        _, data = split_header(os.path.join(OUT, name + ".csv"))
        if name not in man.index or man.loc[name, "data_sha256"] != sha(data):
            out.append(name)
    return out


def reconcile():
    """count(*) of every Redivis draft table against its CSV (data rows)."""
    ds = open_draft()
    rows, bad = [], 0
    names = tables_on_disk()
    for name in names + list(CONFIG["metadata_tables"]):
        if name in CONFIG["metadata_tables"]:
            with open(os.path.join(ROOT, CONFIG["metadata_tables"][name]), encoding="utf-8") as f:
                expected = len(data_rows(f.read()))
        else:
            expected = len(data_rows(split_header(os.path.join(OUT, name + ".csv"))[1]))
        t = ds.table(name)
        actual = count_rows(t) if t.exists() else None
        ok = actual == expected
        bad += not ok
        rows.append((name, expected, actual, "match" if ok else "MISMATCH"))
        log(f"{'match   ' if ok else 'MISMATCH'} {name}: CSV {expected:,}, Redivis {actual if actual is None else f'{actual:,}'}")
    extra = sorted({t.name for t in ds.list_tables()} - set(names) - set(CONFIG["metadata_tables"])
                   - {HEADERS_TABLE})
    if extra:
        log(f"Redivis tables with no CSV here: {extra}")
    total_csv = sum(r[1] for r in rows)
    total_rv = sum(r[2] or 0 for r in rows)
    log(f"reconciled {len(rows)} tables: {len(rows) - bad} match, {bad} mismatch; "
        f"rows CSV {total_csv:,}, Redivis {total_rv:,}")
    os.makedirs(os.path.join(ROOT, "runs"), exist_ok=True)
    pd.DataFrame(rows, columns=["table", "csv_rows", "redivis_rows", "result"]).to_csv(
        os.path.join(ROOT, "runs", "redivis_reconcile.csv"), index=False)
    return 1 if bad else 0


def as_erw_text(df):
    """A frame read from Redivis back to the ERW's CSV text form: Redivis infers types on
    upload (ts_utc, retrieved_at as dateTime, value as float), so datetimes are written as
    ISO 8601 UTC with a Z, dates as YYYY-MM-DD, and nulls as empty strings."""
    out = pd.DataFrame(index=df.index)
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_datetime64_any_dtype(s):
            out[c] = s.dt.strftime("%Y-%m-%dT%H:%M:%SZ").fillna("")
        elif s.dtype == object and len(s.dropna()) and hasattr(s.dropna().iloc[0], "isoformat") \
                and not hasattr(s.dropna().iloc[0], "hour"):
            out[c] = s.map(lambda v: "" if pd.isna(v) else v.isoformat())
        elif pd.api.types.is_float_dtype(s):
            out[c] = s.map(lambda v: "" if pd.isna(v) else repr(float(v)))
        else:
            out[c] = s.astype(object).where(s.notna(), "").astype(str)
    return out


def restore(out_dir=None):
    """Download, from the Redivis draft, each rolling-window table that is missing locally."""
    out_dir = out_dir or OUT
    pats = [re.compile(p) for p in CONFIG["restore_before_run"]]
    ds = open_draft()
    got, failed = 0, 0
    for t in ds.list_tables():
        name = t.name
        if not any(p.match(name) for p in pats) or os.path.exists(os.path.join(out_dir, name + ".csv")):
            continue
        try:
            df = as_erw_text(t.to_pandas_dataframe(progress=False, dtype_backend="numpy"))
            path = os.path.join(out_dir, name + ".csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(f"# Restored from the Redivis draft of {CONFIG['dataset']} by warehouse/redivis/upload.py "
                        f"--restore; the connector rewrites this header when it merges\n")
                df.to_csv(f, index=False, lineterminator="\n")
            got += 1
            log(f"restored {name}: {len(df):,} rows")
        except Exception as exc:
            failed += 1
            log(f"FAIL restore {name}: {type(exc).__name__}: {exc}")
    log(f"restored {got} tables, {failed} failed")
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Redivis uploader (draft only, never releases)")
    ap.add_argument("tables", nargs="*")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--all", action="store_true")
    g.add_argument("--changed", action="store_true")
    g.add_argument("--reconcile", action="store_true")
    g.add_argument("--restore", action="store_true")
    ap.add_argument("--out-dir", help="--restore only: write here instead of warehouse/output (tests)")
    args = ap.parse_args(argv)
    if args.reconcile:
        return reconcile()
    if args.restore:
        return restore(args.out_dir)
    if args.all:
        names = tables_on_disk()
    elif args.changed:
        names = changed_tables()
        log(f"tables changed since their last upload: {len(names)}")
    else:
        names = args.tables
        missing = [n for n in names if not os.path.exists(os.path.join(OUT, n + ".csv"))]
        if missing or not names:
            ap.error(f"no such table(s) in warehouse/output: {missing or 'none given'}")
    return run_upload(names, include_metadata=bool(names) or args.all)


if __name__ == "__main__":
    sys.exit(main())
