"""Storage backends for the erw client.

Energy Research Warehouse (ERW). The public functions in erw.api talk only to
the `Backend` interface below, so a Redivis backend can be added later without
changing them. Today there is one implementation, `LocalBackend`, which reads
the standard CSVs in a directory: by default the repository's
warehouse/output, or wherever the ERW_DATA_DIR environment variable points.
"""

import glob
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

COVERAGE_COLS = ["table", "iso", "market", "n_nodes", "interval", "ts_min", "ts_max",
                 "n_rows", "source_report", "last_run", "validator_status"]


class ERWDataNotFound(FileNotFoundError):
    """The data directory, or a table in it, does not exist."""


class Backend(ABC):
    """What any ERW storage backend must provide.

    A backend returns raw material: table names, a table's provenance header
    lines and its rows as strings, the coverage table, and a version record.
    Parsing, filtering and citation live in erw.api and are shared.
    """

    name = "abstract"

    @abstractmethod
    def list_tables(self) -> List[str]:
        """Table names, sorted, without file extensions."""

    @abstractmethod
    def read_table(self, name: str) -> Tuple[List[str], pd.DataFrame]:
        """(header comment lines without the leading '# ', rows with every column as str)."""

    @abstractmethod
    def coverage(self) -> pd.DataFrame:
        """One row per table, columns COVERAGE_COLS."""

    @abstractmethod
    def version(self) -> Dict[str, Optional[str]]:
        """Identify the exact data being read (for local: the git commit)."""

    @abstractmethod
    def describe(self) -> str:
        """One line saying where the data comes from."""


def _default_data_dir() -> Path:
    env = os.environ.get("ERW_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()
    # editable install inside the repository: package/src/erw/backends.py
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "warehouse" / "output"
        if candidate.is_dir():
            return candidate
    # otherwise look upward from the working directory
    for parent in [Path.cwd(), *Path.cwd().parents]:
        candidate = parent / "warehouse" / "output"
        if candidate.is_dir():
            return candidate
    raise ERWDataNotFound(
        "No ERW data directory found. Set ERW_DATA_DIR to a directory of ERW tables "
        "(the warehouse/output folder of a clone of the erw repository).")


class LocalBackend(Backend):
    """Reads the ERW's standard CSV files from a directory on disk."""

    name = "local"

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir).resolve() if data_dir else _default_data_dir()
        if not self.data_dir.is_dir():
            raise ERWDataNotFound(f"ERW data directory does not exist: {self.data_dir}")
        self._cache: Dict[str, Tuple[float, List[str], pd.DataFrame]] = {}

    def describe(self) -> str:
        return f"local files in {self.data_dir}"

    def _path(self, name: str) -> Path:
        path = self.data_dir / f"{name}.csv"
        if not path.is_file():
            raise ERWDataNotFound(
                f"No ERW table named {name!r} in {self.data_dir}. "
                f"Available: {', '.join(self.list_tables())}")
        return path

    def list_tables(self) -> List[str]:
        return sorted(Path(p).stem for p in glob.glob(str(self.data_dir / "*.csv")))

    def read_table(self, name: str) -> Tuple[List[str], pd.DataFrame]:
        path = self._path(name)
        mtime = path.stat().st_mtime
        hit = self._cache.get(name)
        if hit and hit[0] == mtime:
            return list(hit[1]), hit[2].copy()
        header = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                header.append(line.rstrip("\r\n")[1:].lstrip(" ") if line.startswith("# ")
                              else line.rstrip("\r\n")[1:])
        # never comment="#": it would cut every URL that contains one
        df = pd.read_csv(path, skiprows=len(header), dtype=str, keep_default_na=False,
                         na_values=[], encoding="utf-8")
        self._cache[name] = (mtime, header, df)
        return list(header), df.copy()

    def _coverage_csv(self) -> Path:
        env = os.environ.get("ERW_COVERAGE_CSV")
        if env:
            return Path(env)
        return self.data_dir.parent / "metadata" / "coverage.csv"

    def coverage(self) -> pd.DataFrame:
        path = self._coverage_csv()
        if path.is_file():
            cov = pd.read_csv(path, dtype={"table": str})
            missing = [c for c in COVERAGE_COLS if c not in cov.columns]
            if missing:
                raise ValueError(f"{path} lacks coverage columns {missing}")
            return cov[COVERAGE_COLS]
        raise ERWDataNotFound(
            f"No coverage table at {path}. Build it with "
            "`python warehouse/metadata/build_coverage.py`, or set ERW_COVERAGE_CSV.")

    def _git(self, *args: str) -> Optional[str]:
        try:
            out = subprocess.run(["git", "-C", str(self.data_dir), *args], capture_output=True,
                                 text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return out.stdout.strip() if out.returncode == 0 else None

    def version(self) -> Dict[str, Optional[str]]:
        data_commit = self._git("log", "-1", "--format=%H", "--", ".")
        record = {
            "backend": self.name,
            "data_dir": str(self.data_dir),
            "data_commit": data_commit,
            "data_commit_date": self._git("log", "-1", "--format=%cI", "--", "."),
            "head_commit": self._git("rev-parse", "HEAD"),
            "dirty": None,
            "note": None,
        }
        if data_commit is None:
            record["note"] = ("The data directory is not in a git repository (or git is not "
                              "installed), so no commit identifies this data.")
        else:
            status = self._git("status", "--porcelain", "--", ".")
            record["dirty"] = bool(status)
            if status:
                record["note"] = ("The data directory has uncommitted changes, so the files "
                                  "differ from data_commit.")
        return record
