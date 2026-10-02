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
    python warehouse/redivis/upload.py t1 --allow-shrink t1   # upload t1 although it has fewer rows than last time

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

Session 28 (Ben Domingue's review, item 2, "silent history loss"): the draft is where
the rolling-window tables keep their history, so three gates stop it being lost quietly.
- --restore fails when a table that the manifest lists and restore_before_run matches is
  absent from the draft, or holds fewer rows than the manifest last recorded.
- An upload refuses to shrink a rolling-window table below the rows the manifest last
  recorded for it, unless --allow-shrink names the table.
- Existence is checked by fetching the table's metadata (table_meta), never by
  list_tables() alone, which in the IRW under-reported a large dataset by about half.
Tests: tests/test_redivis_gates.py, against a mocked client.

Session 28 (the review, item 3): uploads are routed by license. A table whose license in
coverage.csv is "public" goes to the public dataset (config.yaml: dataset); every other table
goes to a second, private dataset under the same owner (dataset_internal). Only a human creates
it, with no public access (--check-license --fix); an upload to it before then fails that table. push() refuses a non-public license for the public dataset,
--restore and --reconcile read each table from its own dataset, and --check-license fails when
any internal table is in the public dataset (checked by metadata, table by table) or the internal
dataset is not private. run_daily.sh runs it after every upload and fails the run on it.
    python warehouse/redivis/upload.py --check-license          # exit 1 on any internal table in the public dataset
    python warehouse/redivis/upload.py --check-license --fix    # a human, once: create the internal dataset, move them
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
MANIFEST_COLS = ["table", "data_sha256", "rows", "uploaded_at", "redivis_table", "dataset",
                 "migrated_to"]  # session 29: the consolidated table an old one moved into (kept, never removed)
MIGRATIONS = os.path.join(ROOT, "warehouse", "metadata", "table_migrations.csv")
PUBLIC, INTERNAL = CONFIG["dataset"], CONFIG["dataset_internal"]
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


def data_file(path, out):
    """Session 29: a table's header lines (without '# '), and its data (the column row onwards) copied to out,
    streamed: (header, rows, sha256 of the data, first column name). The same sha as sha(split_header()[1]),
    without holding the file as text (the ERCOT history is 0.65 GB) or as a frame."""
    import csv
    header, h, rows, first = [], hashlib.sha256(), 0, None
    with open(path, encoding="utf-8", newline="") as f, open(out, "w", encoding="utf-8", newline="") as o:
        started = False
        for line in f:
            if not started and line.startswith("#"):
                header.append(line.rstrip("\r\n")[1:].strip())
                continue
            if not started:
                first = next(csv.reader([line]))[0]
            started = True
            h.update(line.encode("utf-8"))
            o.write(line)
    with open(out, encoding="utf-8", newline="") as f:
        rows = sum(1 for _ in csv.reader(f)) - 1
    return header, rows, h.hexdigest(), first


def data_sha(path):
    """sha256 of a table's data (the column row onwards), streamed (session 29)."""
    h = hashlib.sha256()
    with open(path, encoding="utf-8", newline="") as f:
        started = False
        for line in f:
            if not started and line.startswith("#"):
                continue
            started = True
            h.update(line.encode("utf-8"))
    return h.hexdigest()


def migration_map():
    """{old table: new table} (session 29, warehouse/metadata/table_migrations.csv)."""
    if not os.path.exists(MIGRATIONS):
        return {}
    m = pd.read_csv(MIGRATIONS, dtype=str, keep_default_na=False)
    return dict(zip(m["old_table"], m["new_table"]))


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


def account():
    os.environ["REDIVIS_API_TOKEN"] = secret(CONFIG["token_env"])
    import redivis
    owner = secret(CONFIG["owner_env"])
    return redivis.user(owner) if CONFIG["owner_kind"] == "user" else redivis.organization(owner)


def open_draft(dataset=None, create=False):
    """A dataset's unreleased draft, created if the last version was released (red_up.push.open_draft).
    Session 28: dataset is PUBLIC (the default) or INTERNAL. The internal dataset is created, private
    (no public access), only when create is set, which only --check-license --fix does (a human):
    a scheduled run never creates a dataset. The public one must already exist."""
    name = dataset or PUBLIC
    acct = account()
    ds = acct.dataset(name)
    if not ds.exists():
        if name != INTERNAL:
            raise SystemExit(f"Redivis dataset {name} does not exist; create it on Redivis first")
        if not create:
            raise RuntimeError(f"the private Redivis dataset {name} does not exist yet; a human creates it with "
                               "python warehouse/redivis/upload.py --check-license --fix")
        ds.create(public_access_level="none",
                  description="Energy Research Warehouse (ERW): the tables licensed for internal use only "
                              "(warehouse/metadata/coverage.csv). Private: never shared, never released publicly.")
        log(f"created the private Redivis dataset {name} (no public access)")
    ds.create_next_version(if_not_exists=True)
    return acct.dataset(name, version="next")


def dataset_for(license_):
    """Session 28: "public" goes to the public dataset; anything else, blank included, to the internal one."""
    return PUBLIC if license_ == "public" else INTERNAL


class Drafts:
    """The drafts of both datasets, each opened once, when first needed."""

    def __init__(self, create_internal=False):
        self.open, self.create = {}, create_internal

    def __call__(self, name):
        if name not in self.open:
            self.open[name] = open_draft(name, create=self.create and name == INTERNAL)
        return self.open[name]


def rolling(name):
    """A rolling-window table: the daily run merges into it, so its history lives only in the stores (config.yaml)."""
    return any(re.match(p, name) for p in CONFIG["restore_before_run"])


def table_meta(ds, name):
    """The draft table's metadata, fetched by name (session 28): the properties, or None when Redivis
    answers 404. Any other error (a 5xx, throttling, the SDK's AttributeError that hides one) propagates,
    so an unanswered question is never read as "absent"."""
    import redivis
    try:
        return ds.table(name).get().properties
    except redivis.exceptions.NotFoundError:
        return None


def shrink_refusal(name, n_rows, man, allow):
    """Why uploading n_rows would lose history (session 28), or None: a rolling-window table may not
    go below the row count the manifest last recorded for it, unless --allow-shrink names it."""
    if not rolling(name) or name in allow or name not in man.index:
        return None
    last = str(man.loc[name, "rows"] or "")
    if last.isdigit() and n_rows < int(last):
        return (f"refused: {n_rows:,} rows would shrink the rolling-window table below the {int(last):,} rows "
                f"last uploaded ({man.loc[name, 'uploaded_at']}); if that is intended, --allow-shrink {name}")
    return None


def count_rows(table):
    import redivis
    ref = table.get().properties["qualifiedReference"]
    rows = redivis.query(f"select count(*) as n from `{ref}`").to_arrow_table(progress=False).to_pylist()
    return int(rows[0]["n"])


def push(ds, name, header, data_text, license_, events=False, dataset=PUBLIC, data_path=None, expected=None):
    """Replace one draft table with this data; return (expected, actual). Session 29: data_path (a file
    holding the data, column row first, which push removes) with its expected row count, instead of
    data_text, for a table too large to hold as text."""
    if dataset == PUBLIC and license_ != "public":  # session 28: never, whatever the caller asked
        raise RuntimeError(f"refused: license {license_!r} may not be uploaded to the public dataset {PUBLIC}")
    os.makedirs(TMP, exist_ok=True)
    tmp = os.path.join(TMP, f"{name}.csv")
    if data_path is None:
        expected = len(data_rows(data_text))
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(data_text if data_text.endswith("\n") else data_text + "\n")
    else:
        tmp = data_path
    if expected == 0:
        os.remove(tmp)
        raise RuntimeError("no data rows; an empty table is never uploaded")
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
        m = pd.read_csv(MANIFEST, dtype=str, keep_default_na=False)
        if "dataset" not in m.columns:  # before session 28 every table went to the public dataset
            m["dataset"] = PUBLIC
        if "migrated_to" not in m.columns:  # before session 29 no table had moved
            m["migrated_to"] = ""
        return m
    return pd.DataFrame(columns=MANIFEST_COLS)


def write_manifest(m):
    m = m.sort_values("table")[MANIFEST_COLS]
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    m.to_csv(MANIFEST, index=False, lineterminator="\n")


def tables_on_disk():
    return sorted(os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".csv"))


def merge_headers(drafts, names, lic, now, results):
    """Session 49 (--tables): each named table's header lines replace its own lines in its dataset's erw_headers draft
    table; every other table's lines stay as the draft holds them (a machine with older copies of other tables never
    overwrites their headers)."""
    for target in sorted({dataset_for(lic.get(n, "")) for n in names}):
        mine = [n for n in names if dataset_for(lic.get(n, "")) == target]
        label = HEADERS_TABLE + ("" if target == PUBLIC else f" ({target})")
        try:
            try:
                old = drafts(target).table(HEADERS_TABLE).to_pandas_dataframe(progress=False, dtype_backend="numpy")
                old = old[~old["table"].isin(mine)][["table", "line_no", "line"]]
            except Exception as exc:  # no erw_headers in this draft yet: start it with these tables
                log(f"{label}: none in the draft ({type(exc).__name__}); starting it with {mine}")
                old = pd.DataFrame(columns=["table", "line_no", "line"])
            new = [(n, i, line) for n in mine for i, line in enumerate(split_header(os.path.join(OUT, n + ".csv"))[0], 1)]
            h = pd.concat([old, pd.DataFrame(new, columns=["table", "line_no", "line"])], ignore_index=True)
            h["line_no"] = h["line_no"].astype(int)
            h = h.sort_values(["table", "line_no"])
            expected, actual = push(drafts(target), HEADERS_TABLE,
                                    [f"Provenance header lines of every ERW table in {target}, updated {now} for {', '.join(mine)}"],
                                    h.to_csv(index=False, lineterminator="\n"), "public" if target == PUBLIC else "internal",
                                    dataset=target)
            ok = expected == actual
            results.append((label, expected, actual, "" if ok else "row count mismatch"))
            log(f"{'ok  ' if ok else 'FAIL'} {label}: {expected:,} header lines ({len(new)} for {', '.join(mine)}), "
                f"Redivis count(*) {actual:,}")
        except Exception as exc:
            results.append((label, None, None, f"{type(exc).__name__}: {exc}"))
            log(f"FAIL {label}: {type(exc).__name__}: {exc}")


def run_upload(names, include_metadata, allow_shrink=(), create_internal=False, only=False):
    import erw_validate
    drafts = Drafts(create_internal)
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
            del rep
            if name not in lic:
                raise RuntimeError("not in coverage.csv; run build_coverage.py first")
            # session 29: streamed, never the whole table as text or as a frame (the ERCOT history is 0.65 GB)
            os.makedirs(TMP, exist_ok=True)
            tmp = os.path.join(TMP, f"{name}.csv")
            header, n_rows, digest, first = data_file(path, tmp)
            why = shrink_refusal(name, n_rows, man, set(allow_shrink))
            if why:  # before push(), which deletes the draft table
                os.remove(tmp)
                raise RuntimeError(why)
            target = dataset_for(lic[name])
            expected, actual = push(drafts(target), name, header, None, lic[name], events=first == "event_id",
                                    dataset=target, data_path=tmp, expected=n_rows)
            ok = expected == actual
            results.append((name, expected, actual, "" if ok else "row count mismatch"))
            if ok:
                man.loc[name, ["data_sha256", "rows", "uploaded_at", "redivis_table", "dataset", "migrated_to"]] = [
                    digest, str(expected), now, name, target, ""]
            log(f"{'ok  ' if ok else 'FAIL'} {name}: CSV {expected:,} rows, Redivis count(*) {actual:,}"
                + ("" if target == PUBLIC else f" ({target})"))
        except Exception as exc:
            results.append((name, None, None, f"{type(exc).__name__}: {exc}"))
            log(f"FAIL {name}: {type(exc).__name__}: {exc}")
    if only:  # session 49, --tables: the named tables' header lines only, merged into the drafts' erw_headers
        merge_headers(drafts, [r[0] for r in results if not r[3]], lic, now, results)
    if include_metadata:
        # every header line of every table on disk, in full (descriptions stop at 2,000 characters)
        # session 28: each dataset gets the header lines of its own tables only
        for target in (PUBLIC, INTERNAL):
            hrows = []
            for name in tables_on_disk():
                if dataset_for(lic.get(name, "")) != target:
                    continue
                for i, line in enumerate(split_header(os.path.join(OUT, name + ".csv"))[0], 1):
                    hrows.append((name, i, line))
            if not hrows:
                continue
            hdata = pd.DataFrame(hrows, columns=["table", "line_no", "line"]).to_csv(index=False, lineterminator="\n")
            label = HEADERS_TABLE + ("" if target == PUBLIC else f" ({target})")
            try:
                expected, actual = push(drafts(target), HEADERS_TABLE,
                                        [f"Provenance header lines of every ERW table in {target}, uploaded {now}"],
                                        hdata, "public" if target == PUBLIC else "internal", dataset=target)
                ok = expected == actual
                results.append((label, expected, actual, "" if ok else "row count mismatch"))
                log(f"{'ok  ' if ok else 'FAIL'} {label}: {expected:,} header lines, Redivis count(*) {actual:,}")
            except Exception as exc:
                results.append((label, None, None, f"{type(exc).__name__}: {exc}"))
                log(f"FAIL {label}: {type(exc).__name__}: {exc}")
        for rname, rel in CONFIG["metadata_tables"].items():
            path = os.path.join(ROOT, rel)
            try:
                with open(path, encoding="utf-8") as f:
                    data = f.read()
                expected, actual = push(drafts(PUBLIC), rname, [f"ERW metadata file {rel}, uploaded {now}"], data,
                                        "public")
                ok = expected == actual
                results.append((rname, expected, actual, "" if ok else "row count mismatch"))
                log(f"{'ok  ' if ok else 'FAIL'} {rname} ({rel}): CSV {expected:,} rows, Redivis count(*) {actual:,}")
            except Exception as exc:
                results.append((rname, None, None, f"{type(exc).__name__}: {exc}"))
                log(f"FAIL {rname}: {type(exc).__name__}: {exc}")
    write_manifest(man.reset_index().rename(columns={"index": "table"}))
    failed = [r for r in results if r[3]]
    log(f"uploaded {len(results) - len(failed)} of {len(results)} tables to the drafts of "
        f"{PUBLIC} and {INTERNAL} (by license); nothing released")
    return 1 if failed else 0


def changed_tables():
    """Tables whose data changed since their last upload, or whose license now routes them to
    another dataset (session 28)."""
    man = read_manifest().set_index("table")
    lic = licenses()
    out = []
    for name in tables_on_disk():
        if name not in man.index or man.loc[name, "data_sha256"] != data_sha(os.path.join(OUT, name + ".csv")) \
                or man.loc[name, "dataset"] != dataset_for(lic.get(name, "")):
            out.append(name)
    return out


def reconcile():
    """count(*) of every Redivis draft table against its CSV (data rows), each in its own dataset."""
    drafts = Drafts()
    lic = licenses()
    ds = drafts(PUBLIC)
    rows, bad = [], 0
    names = tables_on_disk()
    for name in names + list(CONFIG["metadata_tables"]):
        if name in CONFIG["metadata_tables"]:
            with open(os.path.join(ROOT, CONFIG["metadata_tables"][name]), encoding="utf-8") as f:
                expected = len(data_rows(f.read()))
        else:
            import csv
            with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
                expected = sum(1 for _ in csv.reader(ln for ln in f if not ln.startswith("#"))) - 1
        t = drafts(PUBLIC if name in CONFIG["metadata_tables"] else dataset_for(lic.get(name, ""))).table(name)
        actual = count_rows(t) if t.exists() else None
        ok = actual == expected
        bad += not ok
        rows.append((name, expected, actual, "match" if ok else "MISMATCH"))
        log(f"{'match   ' if ok else 'MISMATCH'} {name}: CSV {expected:,}, Redivis {actual if actual is None else f'{actual:,}'}")
    extra = sorted({t.name for t in ds.list_tables()} - {n for n in names if dataset_for(lic.get(n, "")) == PUBLIC}
                   - set(CONFIG["metadata_tables"]) - {HEADERS_TABLE})
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
    """Download, from the Redivis draft, each rolling-window table that is missing locally.

    Session 28: the tables expected are those the manifest lists (redivis_uploads.csv) that
    restore_before_run matches, plus any such table list_tables() shows. Each is checked by its
    metadata, whether or not a local copy exists. One that is absent from the draft, or has fewer
    rows than the manifest last recorded, fails the restore, so the run stops before a short
    window could be uploaded over the lost history."""
    out_dir = out_dir or OUT
    drafts = Drafts()
    lic = licenses()
    man = read_manifest().set_index("table")
    # session 29: a table consolidated into another (migrated_to, table_migrations.csv) is never restored: its
    # rows come back inside the consolidated table, and warehouse/consolidate.py split writes it for the connectors
    moved = set(migration_map()) | {n for n in man.index if man.loc[n, "migrated_to"]}
    homes = {dataset_for(lic.get(n, "")) for n in man.index if rolling(n) and n not in moved} | {PUBLIC}
    listed = {t.name for d in sorted(homes) for t in drafts(d).list_tables()}
    expected = sorted(n for n in ({n for n in man.index if rolling(n)} | {n for n in listed if rolling(n)})
                      if n not in moved)
    got, failed = 0, 0
    # session 46: a restored file keeps its provenance header, read back from the draft's erw_headers table (every
    # header line of every table, as last uploaded). Daily run 13 failed on policy_reads, whose connector rewrites its
    # header only when it reads something new: on a day with nothing new the placeholder line stayed, with no source
    # or run log. The placeholder is still written, after the lines, and alone when erw_headers has none for a table.
    header_lines = {}

    def lines_of(ds, dataset, name):
        if dataset not in header_lines:
            try:
                h = ds.table(HEADERS_TABLE).to_pandas_dataframe(progress=False, dtype_backend="numpy")
                header_lines[dataset] = {t: [str(x) for x in g.sort_values("line_no")["line"]] for t, g in h.groupby("table")}
                log(f"read {len(h):,} header lines from {HEADERS_TABLE} ({dataset})")
            except Exception as exc:  # the rows still restore; the header falls back to the placeholder alone
                header_lines[dataset] = {}
                log(f"WARNING: could not read {HEADERS_TABLE} ({dataset}): {type(exc).__name__}: {exc}")
        # an earlier restore's placeholder line, uploaded with its table, is never carried forward as a header line
        return [x for x in header_lines[dataset].get(name, []) if not x.startswith("Restored from the Redivis draft")]

    for name in expected:
        try:
            dataset = dataset_for(lic.get(name, ""))
            ds = drafts(dataset)  # session 28: each table from its own dataset
            meta = table_meta(ds, name)
            if meta is None:
                raise RuntimeError(f"absent from the draft, though {CONFIG['manifest']} records an upload of "
                                   f"{man.loc[name, 'rows'] if name in man.index else '?'} rows; restore it from "
                                   "the archive (warehouse/archive/) before the next run")
            last = str(man.loc[name, "rows"]) if name in man.index else ""
            have = meta.get("numRows")
            if last.isdigit() and have is not None and int(have) < int(last):
                raise RuntimeError(f"the draft holds {int(have):,} rows, fewer than the {int(last):,} last uploaded")
            if os.path.exists(os.path.join(out_dir, name + ".csv")):
                continue
            df = as_erw_text(ds.table(name).to_pandas_dataframe(progress=False, dtype_backend="numpy"))
            if have is not None and len(df) != int(have):
                raise RuntimeError(f"downloaded {len(df):,} rows, but the draft's metadata says {int(have):,}")
            path = os.path.join(out_dir, name + ".csv")
            kept = lines_of(ds, dataset, name)
            with open(path, "w", encoding="utf-8", newline="") as f:
                for line in kept:
                    f.write(f"# {line}\n")
                f.write(f"# Restored from the Redivis draft of {CONFIG['dataset']} by warehouse/redivis/upload.py "
                        f"--restore{' with the header lines above, from ' + HEADERS_TABLE if kept else ''}; the "
                        f"connector rewrites this header when it merges\n")
                df.to_csv(f, index=False, lineterminator="\n")
            got += 1
            log(f"restored {name}: {len(df):,} rows")
        except Exception as exc:
            failed += 1
            log(f"FAIL restore {name}: {type(exc).__name__}: {exc}")
    log(f"restored {got} tables, {failed} failed (checked {len(expected)} rolling-window tables by their metadata)")
    return 1 if failed else 0


def check_license(fix=False):
    """Session 28: exit 1 when any table licensed other than public is in the public dataset's draft,
    or the internal dataset is not private. Each internal table is looked up by its metadata (not
    list_tables() alone); every table list_tables() shows in the public draft must be public or a
    metadata table. With fix (a human, once): each internal table found in the public draft is
    uploaded to the internal dataset, its count(*) checked, and only then deleted from the public one."""
    lic = licenses()
    drafts = Drafts()
    pub = drafts(PUBLIC)
    internal = sorted(n for n, l in lic.items() if dataset_for(l) == INTERNAL)
    found = [n for n in internal if table_meta(pub, n) is not None]
    allowed = {n for n, l in lic.items() if l == "public"} | set(CONFIG["metadata_tables"]) | {HEADERS_TABLE}
    # session 29: a table consolidated into a public table stays in the draft until --remove-migrated removes it
    allowed |= {old for old, new in migration_map().items() if lic.get(new) == "public"}
    unknown = sorted({t.name for t in pub.list_tables()} - allowed - set(found))
    bad = 0
    for n in found:
        log(f"FAIL {n}: license {lic[n]!r}, but the table is in the public dataset {PUBLIC}")
    for n in unknown:
        log(f"FAIL {n}: in the public dataset {PUBLIC} but not a public table in coverage.csv")
    bad += len(found) + len(unknown)
    acct = account()
    idx = acct.dataset(INTERNAL)
    if not idx.exists():
        log(f"note: the private dataset {INTERNAL} does not exist yet (--fix creates it)")
    else:
        level = idx.get().properties.get("publicAccessLevel")
        if level != "none":
            bad += 1
            log(f"FAIL the internal dataset {INTERNAL} has public access {level!r}; it must be 'none'")
    if fix and (found or unknown):
        moved = [n for n in found + unknown if n in lic and dataset_for(lic[n]) == INTERNAL
                 and os.path.exists(os.path.join(OUT, n + ".csv"))]
        if run_upload(moved, include_metadata=False, create_internal=True) != 0:
            log("fix stopped: an upload to the internal dataset failed; nothing deleted from the public dataset")
            return 1
        idd = open_draft(INTERNAL)
        for n in moved:
            expected = len(data_rows(split_header(os.path.join(OUT, n + ".csv"))[1]))
            if table_meta(idd, n) is None or count_rows(idd.table(n)) != expected:
                log(f"fix: {n} not confirmed in {INTERNAL}; left in the public dataset")
                continue
            pub.table(n).delete()
            log(f"moved {n}: {expected:,} rows in {INTERNAL}, deleted from the draft of {PUBLIC}")
        return check_license(fix=False)
    log(f"license check: {len(internal)} internal tables, {len(found)} in the public dataset, "
        f"{len(unknown)} unknown tables there; {'FAILED' if bad else 'ok'}")
    return 1 if bad else 0


def remove_migrated(dry_run=False):
    """Session 29: remove from the Redivis drafts the tables consolidated into others (table_migrations.csv), a
    human's command. Per family it first checks, in the draft, that the consolidated table holds the old tables'
    rows: its count(*) equals the sum of the old tables' counts, or, when the consolidated table has grown since
    (the daily run adds days to it, never to the old tables), every old row's key is in it (a join per old table,
    whose count must equal the old table's). It refuses to remove anything if any family fails a check, and
    prints each table it removes. The manifest keeps every old line (migrated_to), so the history gate's counts
    survive."""
    import redivis
    fams = {}
    for old, new in migration_map().items():
        fams.setdefault(new, []).append(old)
    lic = licenses()
    man = read_manifest().set_index("table")
    drafts = Drafts()
    plan, bad = [], 0
    keys = "entity, variable, ts_utc"
    for new, olds in fams.items():
        ds_new = drafts(dataset_for(lic.get(new, "")))
        meta = table_meta(ds_new, new)
        if meta is None:
            log(f"REFUSE {new}: the consolidated table is not in the draft of {dataset_for(lic.get(new, ''))}")
            bad += 1
            continue
        n_new = count_rows(ds_new.table(new))
        ref_new = meta["qualifiedReference"]
        present, counts = [], {}
        for old in olds:
            home = man.loc[old, "dataset"] if old in man.index and man.loc[old, "dataset"] else PUBLIC
            om = table_meta(drafts(home), old)
            if om is None:
                log(f"  {old}: already absent from {home}")
                continue
            counts[old] = count_rows(drafts(home).table(old))
            present.append((old, home, om["qualifiedReference"]))
        if not present:
            log(f"ok   {new}: {n_new:,} rows; no old table left to remove")
            continue
        total = sum(counts.values())
        if n_new == total:
            log(f"ok   {new}: count(*) {n_new:,} = the sum of its {len(present)} old tables' counts {total:,}")
        elif n_new > total:
            missing = {}
            for old, _, ref_old in present:
                got = redivis.query(f"select count(*) as n from `{ref_old}` o join `{ref_new}` n using ({keys})") \
                    .to_arrow_table(progress=False).to_pylist()[0]["n"]
                if int(got) != counts[old]:
                    missing[old] = counts[old] - int(got)
            if missing:
                log(f"REFUSE {new}: {n_new:,} rows, and old rows missing from it: {missing}")
                bad += 1
                continue
            log(f"ok   {new}: count(*) {n_new:,}, more than the old tables' {total:,} (days added since the migration); "
                f"every old row's key is in it (one join per old table)")
        else:
            log(f"REFUSE {new}: count(*) {n_new:,}, fewer than the {total:,} rows of its old tables")
            bad += 1
            continue
        plan += [(old, home, counts[old], new) for old, home, _ in present]
    if bad:
        log(f"remove-migrated refused: {bad} famil{'y' if bad == 1 else 'ies'} failed a check; nothing removed")
        return 1
    if dry_run:
        for old, home, n, new in plan:
            log(f"would remove {old} ({n:,} rows, in {new}) from {home}")
        log(f"dry run: would remove {len(plan)} tables; nothing removed")
        return 0
    for old, home, n, new in plan:
        drafts(home).table(old).delete()
        log(f"removed {old} ({n:,} rows, now in {new}) from the draft of {home}")
    log(f"remove-migrated: removed {len(plan)} tables; the manifest keeps their lines (migrated_to)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW Redivis uploader (draft only, never releases)")
    ap.add_argument("tables", nargs="*")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--all", action="store_true")
    g.add_argument("--changed", action="store_true")
    g.add_argument("--reconcile", action="store_true")
    g.add_argument("--restore", action="store_true")
    g.add_argument("--tables", nargs="+", metavar="TABLE", dest="only_tables",
                   help="session 49: upload these tables only, each to its own dataset by license, and merge their "
                        "header lines into erw_headers; no other table, header or metadata table is touched")
    g.add_argument("--check-license", action="store_true",
                   help="exit 1 if any internal table is in the public dataset (session 28)")
    g.add_argument("--remove-migrated", action="store_true",
                   help="session 29, a human's command: remove the tables consolidated into others from the drafts, "
                        "after checking every family; nothing is removed on any mismatch")
    ap.add_argument("--out-dir", help="--restore only: write here instead of warehouse/output (tests)")
    ap.add_argument("--allow-shrink", action="append", default=[], metavar="TABLE",
                    help="upload this rolling-window table although it has fewer rows than last recorded (session 28)")
    ap.add_argument("--fix", action="store_true",
                    help="--check-license only: move internal tables out of the public dataset (a human, once)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list the tables that would be uploaded, upload nothing (session 14, CI tests)")
    args = ap.parse_args(argv)
    if args.reconcile:
        return reconcile()
    if args.restore:
        return restore(args.out_dir)
    if not (args.check_license and not args.fix):  # session 59: writing to Redivis is a data write, under the data lock
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        import lock
        lock.require(what="the Redivis upload")
    if args.check_license:
        return check_license(args.fix)
    if args.remove_migrated:
        return remove_migrated(args.dry_run)
    if args.only_tables:
        missing = [n for n in args.only_tables if not os.path.exists(os.path.join(OUT, n + ".csv"))]
        if missing:
            ap.error(f"no such table(s) in warehouse/output: {missing}")
        if args.dry_run:
            log(f"dry run, nothing uploaded; --tables would upload {', '.join(args.only_tables)} and merge their header lines")
            return 0
        return run_upload(args.only_tables, include_metadata=False, allow_shrink=args.allow_shrink, only=True)
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
    if args.dry_run:
        man = read_manifest().set_index("table")
        for n in names:  # session 28: the shrink gate, reported without uploading
            import csv
            with open(os.path.join(OUT, n + ".csv"), encoding="utf-8", newline="") as f:
                n_rows = sum(1 for _ in csv.reader(ln for ln in f if not ln.startswith("#"))) - 1
            why = shrink_refusal(n, n_rows, man, set(args.allow_shrink))
            if why:
                log(f"would refuse {n}: {why}")
        log(f"dry run, nothing uploaded; would upload {len(names)} tables"
            + (f" and the metadata tables: {chr(44).join(names)}" if names else ""))
        return 0
    return run_upload(names, include_metadata=bool(names) or args.all, allow_shrink=args.allow_shrink)


if __name__ == "__main__":
    sys.exit(main())
