"""Session 7613 (portable-laptop): read an ERW table from Redivis (the warehouse of record) for the ruling impact scripts,
cached under runs/ruling_impact/cache/ (never warehouse/output). Read-only. No model call.

    from redivis_read import table
    df, where = table("generator_pipeline_by_grid")      # the draft ("next") if this token can read it, else the release
"""
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).resolve().parent / "cache"
sys.path.insert(0, str(ROOT / "package" / "src"))


def _env():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() in ("REDIVIS_API_TOKEN", "REDIVIS_OWNER"):
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def table(name: str, version: str = "next"):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{name}.{version}.csv"
    meta = CACHE / f"{name}.{version}.where.txt"
    if f.exists() and meta.exists():
        return pd.read_csv(f, dtype=str, keep_default_na=False), meta.read_text(encoding="utf-8")
    _env()
    from erw.remote import RedivisBackend
    b = RedivisBackend(version=version)
    df = b._read(name)
    where = b.describe()
    df.to_csv(f, index=False)
    meta.write_text(where, encoding="utf-8")
    return df, where


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    df, where = table(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "next")
    print(where, len(df), "rows")
    print(list(df.columns))
    print(df.head(3).to_string()[:2000])
