"""Session 536: the erw package in a clean environment.

Session 536 installed package/ into a new virtual environment outside the repository and ran every example of
package/README.md, docs/guide.md, package/llms.txt and the package docstring that needs no key (the local backend
and the Supabase anon backend; nothing of Redivis). Three faults came out, fixed in the package:

  1. get_backend() ignored ERW_BACKEND on first use: with ERW_BACKEND=supabase and no local tables, erw.info()
     stopped with "No ERW data directory found" (api.get_backend).
  2. An old table name (ercot_dam_hub_prices, the README's own example) failed in an install outside the clone:
     table_migrations.csv was looked for only above the package's file and the working directory, never beside
     the tables ERW_DATA_DIR names (api._migrations_csv).
  3. The Supabase backend dropped a series row's partition columns ba and event, so fetch("eia930_all_demand",
     ba="ciso") returned no rows there (remote.SupabaseBackend.read_table).
  4. Without pyarrow, which the package does not require, filter(variable=) and filter(node=) read every local
     table whole and cached nothing, though the README says the facts are kept on disk: about nine minutes a call
     on 198 tables in the new venv (api._local_columns).

The install test builds a wheel of package/ with this interpreter's setuptools (offline, no build isolation),
installs it with --no-index into a new venv in a temporary folder and runs the package there from a folder
outside the repository. The new venv has no pandas, so it borrows this interpreter's site-packages through
PYTHONPATH (no .pth of it is read, so this repository's editable erw is not seen; the test checks that erw is
imported from the new venv). ERW_PACKAGE_NETWORK_TEST=1 installs from PyPI instead, with nothing borrowed. A
machine that cannot make a venv or build the wheel skips, with the reason.
"""

import ast
import json
import os
import re
import shutil
import site
import subprocess
import sys
import sysconfig
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "package"
NETWORK = os.environ.get("ERW_PACKAGE_NETWORK_TEST") == "1"


def _clean_env(extra=None):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("ERW_", "SUPABASE_", "REDIVIS_", "PYTHON", "ANTHROPIC_", "VIRTUAL_ENV"))}
    env.update(extra or {})
    return env


def _venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _all_names():
    tree = ast.parse((PKG / "src" / "erw" / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "__all__" for t in node.targets):
            return set(ast.literal_eval(node.value))
    raise AssertionError("no __all__ in erw/__init__.py")


class CleanInstall(unittest.TestCase):
    """package/ installed into a new venv, run from outside the repository."""

    tmp = None

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="erw536_"))
        venv = cls.tmp / "venv"
        try:
            p = subprocess.run([sys.executable, "-m", "venv", str(venv)], capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.SubprocessError) as e:
            raise unittest.SkipTest(f"cannot create a virtual environment on this machine: {e}")
        cls.py = _venv_python(venv)
        if p.returncode != 0 or not cls.py.is_file():
            raise unittest.SkipTest("cannot create a virtual environment on this machine: "
                                    + (p.stderr.strip().splitlines() or ["no python in it"])[-1])
        src = cls.tmp / "package"
        shutil.copytree(PKG, src, ignore=shutil.ignore_patterns("build", "*.egg-info", "__pycache__", ".pytest_cache"))
        cls.extra_env = {}
        if NETWORK:
            p = subprocess.run([str(cls.py), "-m", "pip", "install", "-q", str(src)], capture_output=True,
                               text=True, timeout=1200)
            if p.returncode != 0:
                raise AssertionError("pip install from PyPI failed: " + p.stderr[-2000:])
            return
        try:
            import setuptools  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("this interpreter has no setuptools to build the wheel offline "
                                    "(ERW_PACKAGE_NETWORK_TEST=1 installs from PyPI)")
        wheels = cls.tmp / "wheels"
        p = subprocess.run([sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-index",
                            "--no-build-isolation", "-w", str(wheels), str(src)],
                           capture_output=True, text=True, timeout=600, cwd=str(cls.tmp))
        built = sorted(wheels.glob("erw-*.whl")) if wheels.is_dir() else []
        if p.returncode != 0 or not built:
            raise unittest.SkipTest("cannot build the wheel offline here: "
                                    + (p.stderr.strip().splitlines() or ["no wheel written"])[-1])
        p = subprocess.run([str(cls.py), "-m", "pip", "install", "-q", "--no-index", "--no-deps", str(built[0])],
                           capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise AssertionError("pip install of the wheel failed: " + p.stderr[-2000:])
        # pandas from this interpreter: its site-packages through PYTHONPATH (a .pth there is not read)
        paths = [sysconfig.get_paths()["purelib"], sysconfig.get_paths()["platlib"], *site.getsitepackages()]
        if any((Path(d) / "erw" / "__init__.py").is_file() for d in paths):
            raise unittest.SkipTest("this interpreter has erw installed as files (not editable), which PYTHONPATH "
                                    "would put before the new venv's (ERW_PACKAGE_NETWORK_TEST=1 installs from PyPI)")
        cls.extra_env = {"PYTHONPATH": os.pathsep.join(dict.fromkeys(paths))}

    @classmethod
    def tearDownClass(cls):
        if cls.tmp is not None:
            shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_py(self, code, env=None):
        work = self.tmp / "work"
        work.mkdir(exist_ok=True)
        p = subprocess.run([str(self.py), "-c", code], capture_output=True, text=True, timeout=600,
                           cwd=str(work), env=_clean_env({**self.extra_env, **(env or {})}))
        return p

    def test_imports_from_the_new_environment(self):
        p = self.run_py("import erw, json; print(json.dumps({'file': erw.__file__, 'all': erw.__all__, "
                        "'version': erw.__version__}))")
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout.strip().splitlines()[-1])
        self.assertTrue(Path(out["file"]).resolve().is_relative_to(self.tmp.resolve()), out["file"])
        self.assertEqual(set(out["all"]), _all_names())
        self.assertEqual(out["version"], "0.1.0")

    def test_no_data_says_how_to_point_it(self):
        p = self.run_py("import erw\nerw.info()\n")
        self.assertEqual(p.returncode, 1)
        self.assertIn("ERWDataNotFound", p.stderr)
        self.assertIn("ERW_DATA_DIR", p.stderr)

    def test_erw_backend_counts_on_first_use(self):
        # fault 1: before session 536 this raised ERWDataNotFound (a LocalBackend), never reading ERW_BACKEND
        p = self.run_py("import erw\nerw.info()\n", {"ERW_BACKEND": "nowhere"})
        self.assertEqual(p.returncode, 1)
        self.assertIn("ERW_BACKEND='nowhere': use local, redivis or supabase", p.stderr)

    def test_migrations_beside_the_data_directory(self):
        # fault 2: the map beside the tables, as coverage.csv and sources.csv are
        data = self.tmp / "data"
        (data / "output").mkdir(parents=True, exist_ok=True)
        (data / "metadata").mkdir(exist_ok=True)
        shutil.copy(ROOT / "warehouse" / "metadata" / "table_migrations.csv", data / "metadata")
        p = self.run_py("import erw, json\nm = erw.migrations()\n"
                        "print(json.dumps({'path': str(erw.api._migrations_csv()), "
                        "'old': m.get('ercot_dam_hub_prices')}))\n", {"ERW_DATA_DIR": str(data / "output")})
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout.strip().splitlines()[-1])
        self.assertEqual(Path(out["path"]).resolve(), (data / "metadata" / "table_migrations.csv").resolve())
        self.assertEqual(out["old"], ["iso_dam_hub_prices", {"market": "ercot_dam"}])

    def test_a_committed_table_reads_and_cites(self):
        # energy_deals is one of the tables kept in git (warehouse/output, CLAUDE.md), with coverage.csv and sources.csv
        p = self.run_py("import erw\ndf = erw.fetch('energy_deals')\nprint(len(df) > 0, erw.tier('energy_deals'))\n"
                        "print(erw.cite('energy_deals'))\n",
                        {"ERW_DATA_DIR": str(ROOT / "warehouse" / "output")})
        self.assertEqual(p.returncode, 0, p.stderr)
        first = p.stdout.splitlines()[0]
        self.assertEqual(first, "True model_extracted")
        self.assertIn("energy_deals", p.stdout)


class SupabasePartitions(unittest.TestCase):
    """Fault 3, with no network: the backend's reader fed rows as the live set's series table returns them."""

    def test_ba_and_event_are_kept(self):
        # the row is the live set's own (read with the anon key in session 536): eia930:CISO demand_forecast_mw
        code = r'''
import json, erw
from erw.remote import SupabaseBackend
b = object.__new__(SupabaseBackend)
b.role, b.url, b._cache = "anon", "https://example.invalid", {}
cols = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source",
        "source_url", "retrieved_at", "vintage", "ba"]
cat = [{"table_name": "eia930_all_demand", "in_live_set": "yes", "interval": "PT1H", "columns": json.dumps(cols)}]
row = {"table_name": "eia930_all_demand", "entity": "eia930:CISO", "variable": "demand_forecast_mw",
       "ts_utc": "2026-09-16T16:00:00+00:00", "value": 25099.0, "unit": "MW", "freq": "PT1H", "geo": "US-CA",
       "market": None, "node": None, "source": "eia:electricity/rto/region-data", "source_url": "",
       "retrieved_at": None, "vintage": None, "license": "public", "ba": "ciso", "event": None}
def select(table, **eq):
    return {"catalogue": cat, "series": [row], "headers": []}[table]
b._select = select
h, df = b.read_table("eia930_all_demand")
print(json.dumps({"cols": list(df.columns), "ba": df["ba"].tolist(), "value": df["value"].tolist()}))
'''
        env = dict(os.environ, PYTHONPATH=str(PKG / "src"))
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300, env=env,
                           cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout.strip().splitlines()[-1])
        self.assertEqual(out["cols"][-1], "ba")
        self.assertEqual(out["ba"], ["ciso"])
        self.assertEqual(out["value"], ["25099.0"])


class FactsWithoutPyarrow(unittest.TestCase):
    """Fault 4: without pyarrow (not a dependency) filter(variable=, node=) read every table whole and cached nothing."""

    CODE = r'''
import json, sys
if sys.argv[1] == "block":
    sys.modules["pyarrow"] = None  # import pyarrow raises ImportError, as in a new venv
import erw
from erw import api
s = api._local_columns("energy_deals")
print(json.dumps({"none": s is None, "cols": sorted(s) if s else [], "n": {k: len(v) for k, v in (s or {}).items()},
                  "types": sorted(s["event_type"]) if s else []}))
'''

    def run_one(self, mode, cache):
        env = dict(os.environ, PYTHONPATH=str(PKG / "src"), ERW_DATA_DIR=str(ROOT / "warehouse" / "output"),
                   ERW_CACHE_DIR=str(cache), ERW_FACTS_CACHE="1")
        p = subprocess.run([sys.executable, "-c", self.CODE, mode], capture_output=True, text=True, timeout=300,
                           env=env, cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout.strip().splitlines()[-1])

    def test_streamed_and_cached_without_pyarrow(self):
        with tempfile.TemporaryDirectory() as d:
            out = self.run_one("block", Path(d) / "a")
            self.assertFalse(out["none"])
            self.assertIn("event_type", out["cols"])
            self.assertTrue(out["types"])
            self.assertEqual(len(list((Path(d) / "a" / "facts").glob("energy_deals_*.json"))), 1)
            again = self.run_one("block", Path(d) / "a")  # read from the cache
            self.assertEqual(again, out)

    def test_pandas_and_pyarrow_read_the_same_facts(self):
        try:
            import pyarrow.csv  # noqa: F401
        except Exception as e:  # noqa: BLE001 (ImportError, or this machine's Application Control block)
            self.skipTest(f"pyarrow cannot be imported here, so the two readers are not compared: {e}")
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_one("pyarrow", Path(d) / "b"), self.run_one("block", Path(d) / "a"))


class Documents(unittest.TestCase):
    """The documents name only functions the package has, and today's tables in their examples."""

    DOCS = [PKG / "README.md", ROOT / "docs" / "guide.md", PKG / "llms.txt", PKG / "src" / "erw" / "__init__.py"]

    def test_every_called_function_exists(self):
        names = _all_names() | {"api", "remote", "backends"}
        for path in self.DOCS:
            called = set(re.findall(r"\berw\.([a-z_]+)\(", path.read_text(encoding="utf-8")))
            self.assertTrue(called, path)
            self.assertEqual(called - names, set(), path)

    def test_examples_use_current_names(self):
        old = {line.split(",", 1)[0] for line in
               (ROOT / "warehouse" / "metadata" / "table_migrations.csv").read_text(encoding="utf-8").splitlines()[1:]
               if line and not line.startswith("#")}
        self.assertIn("ercot_dam_hub_prices", old)
        readme = (PKG / "README.md").read_text(encoding="utf-8")
        example = readme.split("## Example", 1)[1].split("```python", 1)[1].split("```", 1)[0]
        init = (PKG / "src" / "erw" / "__init__.py").read_text(encoding="utf-8").split('"""', 2)[1]
        init_code = "\n".join(l for l in init.splitlines() if l.startswith("    "))
        for text in (example, init_code):
            used = set(re.findall(r'erw\.(?:fetch|cite|info|sources|tier)\("([a-z0-9_]+)"', text))
            self.assertTrue(used)
            self.assertEqual(used & old, set(), text)

    def test_readme_says_erw_backend_counts_on_first_use(self):
        readme = (PKG / "README.md").read_text(encoding="utf-8")
        self.assertIn("picks one on first use", readme)
        self.assertIn("ERW_SUPABASE_ROLE=anon", readme)
        # package/llms.txt is also the chat's system prompt (site/lib/chat/spec.json, tests 58 and 92): left as it was


if __name__ == "__main__":
    unittest.main()
