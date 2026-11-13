#!/usr/bin/env python3
"""The whole suite in batches, each its own process, so a machine with 8 GB can run the gate (session 4000, chain 228).

Energy Research Warehouse (ERW). Roadmap item 1. The laptops' landing gates failed for memory (docs/state/
landing_request_oldlaptop.md row 9: two runs of `python -m unittest discover -s tests` on 8 GB, every failure a
MemoryError, a commitment-limit exit or a timeout; each failed module passed alone). One process holds every module it
has imported, and every cache a module filled, until the last of about 8,400 tests. This runs the same tests as
`unittest discover -s tests`, in the same order, but as a series of processes of at most --batch modules each, so the
memory of one batch is given back before the next begins:

    python scripts/suite_batches.py                    the suite, 40 modules a process (run from the checkout's root)
    python scripts/suite_batches.py --batch 25         smaller batches
    python scripts/suite_batches.py --alone tests/heavy_modules.txt    modules named there each run in a process alone
    python scripts/suite_batches.py --profile runs/suite_profile.csv  every module alone, its peak memory and time written

What it prints is what unittest prints, batch after batch, then the whole run's two summary lines in unittest's own
form ("Ran N tests in Xs", then "OK (skipped=K)" or "FAILED (failures=F, errors=E, skipped=K)"), so scripts/land_check.py
and scripts/suite_gate.py read it as they read one process. A batch that stops without its summary (a MemoryError, a
process stopped by the system) is run again one module a process, once; a module that still stops is written as
"ERROR: <module> (suite_batches.<module>)", which both readers count as a failing test.

Each batch's process mirrors discover: the checkout's root first on sys.path (as `python -m` puts the working folder),
then tests/ inserted before it, each module imported by its file's name and loaded with loadTestsFromModule (the
load_tests protocol honoured), run by TextTestRunner. Each prints its own peak memory on its last line
("suite_batches: peak MB ..."), and the run ends with the five heaviest batches.

Exit codes: 0 every test passed; 1 a test failed or errored, or a module stopped without a summary; 2 bad input.
Standard library only.
"""

import argparse
import csv
import fnmatch
import os
import re
import subprocess
import sys
import time

RAN = re.compile(r"^Ran (\d+) tests? in ([\d.]+)s")
VERDICT = re.compile(r"^(OK|FAILED)(?: \((.*)\))?\s*$")
PEAK = re.compile(r"^suite_batches: peak MB (\d+)")
COUNTS = ("failures", "errors", "skipped", "expected failures", "unexpected successes")
PATTERN = "test*.py"   # unittest discover's default


def modules(tests_dir, pattern=PATTERN):
    """The test modules discover would load from tests_dir, in its order (sorted file names), as importable names."""
    names = sorted(f for f in os.listdir(tests_dir) if fnmatch.fnmatch(f, pattern) and f.endswith(".py"))
    return [f[:-3] for f in names if f[:-3].isidentifier()]


def read_alone(path):
    """Module names, one a line ('#' starts a note), each to run in a process of its own."""
    if not path or not os.path.exists(path):
        return set()
    out = set()
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.split("#", 1)[0].strip()
            if ln:
                out.add(ln[:-3] if ln.endswith(".py") else ln.replace("tests.", "", 1) if ln.startswith("tests.") else ln)
    return out


def batches(mods, size, alone=()):
    """Consecutive runs of at most `size` modules, in order; a module of `alone` is a batch by itself."""
    out, cur = [], []
    for m in mods:
        if m in alone:
            if cur:
                out.append(cur)
                cur = []
            out.append([m])
            continue
        cur.append(m)
        if len(cur) >= max(1, size):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def parse(lines):
    """(tests run, seconds, {count: n}, peak MB) from one batch's output, or None when it printed no verdict."""
    ran = secs = None
    verdict = None
    peak = 0
    for ln in lines:
        m = RAN.match(ln)
        if m:
            ran, secs = int(m.group(1)), float(m.group(2))
        v = VERDICT.match(ln)
        if v:
            verdict = v
        p = PEAK.match(ln)
        if p:
            peak = int(p.group(1))
    if ran is None or verdict is None:
        return None
    counts = dict.fromkeys(COUNTS, 0)
    for part in (verdict.group(2) or "").split(","):
        if "=" in part:
            k, n = part.split("=", 1)
            if k.strip() in counts and n.strip().isdigit():
                counts[k.strip()] = int(n.strip())
    return ran, secs, counts, peak


def summary(ran, secs, counts):
    """unittest's own two closing lines for the whole run."""
    shown = [f"{k}={counts[k]}" for k in COUNTS if counts.get(k)]
    bad = counts.get("failures", 0) or counts.get("errors", 0) or counts.get("unexpected successes", 0)
    if bad:
        return [f"Ran {ran} tests in {secs:.3f}s", "", f"FAILED ({', '.join(shown)})"]
    return [f"Ran {ran} tests in {secs:.3f}s", "", "OK" + (f" ({', '.join(shown)})" if shown else "")]


def peak_mb():
    """This process's peak memory in MB: the peak working set on Windows, the maximum resident size elsewhere."""
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            c = PMC()
            c.cb = ctypes.sizeof(PMC)
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
            if psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
                return int(max(c.PeakWorkingSetSize, c.PeakPagefileUsage) / 2**20)
            return 0
        import resource
        r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(r / 2**20) if sys.platform == "darwin" else int(r / 1024)
    except Exception:  # a reading of memory never fails the run
        return 0


def total_mb():
    """The machine's physical memory in MB, or 0 when it cannot be read."""
    try:
        if os.name == "nt":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS()
            m.dwLength = ctypes.sizeof(MS)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return int(m.ullTotalPhys / 2**20)
            return 0
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo") as f:
                for ln in f:
                    if ln.startswith("MemTotal:"):
                        return int(ln.split()[1]) // 1024
        if sys.platform == "darwin":
            out = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()
            return int(out) // 2**20 if out.isdigit() else 0
    except Exception:
        return 0
    return 0


def worker(names, tests_dir):
    """One batch, as discover would run it: exit 0 when it passed, 1 when not."""
    import importlib
    import unittest
    root = os.getcwd()
    sys.path[0] = root                       # as `python -m unittest` puts the working folder first
    sys.path.insert(0, os.path.abspath(tests_dir))   # as discover inserts its top-level folder
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for n in names:
        try:
            mod = importlib.import_module(n)
        except unittest.SkipTest as e:       # as discover: a module that raises SkipTest is one skipped test
            suite.addTest(unittest.loader._make_skipped_test(n, e, unittest.TestSuite))
            continue
        except BaseException:                # as discover: a module that cannot be imported is one failing test
            suite.addTest(unittest.loader._make_failed_import_test(n, unittest.TestSuite)[0])
            continue
        suite.addTests(loader.loadTestsFromModule(mod, pattern=PATTERN))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    sys.stdout.flush()
    sys.stderr.write(f"suite_batches: peak MB {peak_mb()}\n")
    sys.stderr.flush()
    return 0 if result.wasSuccessful() else 1


def run_batch(names, tests_dir, out, env=None, timeout=None):
    """One batch in its own process, its output (both streams) written to `out` as it comes; (exit, lines, seconds)."""
    argv = [sys.executable, os.path.abspath(__file__), "--worker", "--tests", tests_dir, *names]
    t0 = time.time()
    buf = []
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env,
                         text=True, encoding="utf-8", errors="replace")
    try:
        for ln in p.stdout:
            out.write(ln)
            buf.append(ln.rstrip("\n"))
        code = p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        code = None
    out.flush()
    return code, buf, time.time() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--batch", type=int, default=40, help="modules a process (default 40)")
    ap.add_argument("--tests", default="tests", help="the tests folder (default tests)")
    ap.add_argument("--alone", help="a file of module names, each run in a process alone")
    ap.add_argument("--profile", help="run every module alone and write module, tests, seconds and peak MB to this CSV")
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("names", nargs="*", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.worker:
        return worker(a.names, a.tests)
    if not os.path.isdir(a.tests):
        print(f"suite_batches: no folder {a.tests} here (run from the checkout's root)", file=sys.stderr)
        return 2
    mods = modules(a.tests)
    if a.names:
        mods = [m for m in mods if m in set(a.names)]
    size = 1 if a.profile else a.batch
    plan = batches(mods, size, read_alone(a.alone))
    print(f"suite_batches: {len(mods)} modules in {len(plan)} processes (at most {size} modules each); machine memory "
          f"{total_mb()} MB", flush=True)
    total, secs, counts, heavy, lost, prof = 0, 0.0, dict.fromkeys(COUNTS, 0), [], [], []
    out = sys.stdout
    for i, names in enumerate(plan, 1):
        code, lines, took = run_batch(names, a.tests, out)
        got = parse(lines)
        if got is None and len(names) > 1:    # stopped without a summary: each of its modules again, alone, once
            print(f"suite_batches: batch {i} ({names[0]} to {names[-1]}) stopped without a summary (exit {code}); "
                  f"its {len(names)} modules run again one a process", flush=True)
            for n in names:
                c2, l2, t2 = run_batch([n], a.tests, out)
                g2 = parse(l2)
                if g2 is None:
                    lost.append((n, c2))
                    continue
                total, secs = total + g2[0], secs + g2[1]
                for k in COUNTS:
                    counts[k] += g2[2][k]
                heavy.append((g2[3], n))
            continue
        if got is None:
            lost.append((names[0], code))
            continue
        total, secs = total + got[0], secs + got[1]
        for k in COUNTS:
            counts[k] += got[2][k]
        heavy.append((got[3], names[0] if len(names) == 1 else f"{names[0]} to {names[-1]}"))
        if a.profile:
            prof.append((names[0], got[0], round(took, 1), got[3]))
    for n, c in lost:
        print("=" * 70)
        print(f"ERROR: {n} (suite_batches.{n})")
        print("-" * 70)
        print(f"the module's process stopped without unittest's summary (exit {c}): a MemoryError, a stop by the system, "
              f"or a crash; run it alone: python -m unittest discover -s {a.tests} -p {n}.py")
    counts["errors"] += len(lost)
    print("-" * 70)
    for ln in summary(total, secs, counts):
        print(ln)
    top = sorted(heavy, reverse=True)[:5]
    print("suite_batches: the heaviest processes: " + "; ".join(f"{n} {mb} MB" for mb, n in top), flush=True)
    if a.profile:
        os.makedirs(os.path.dirname(os.path.abspath(a.profile)), exist_ok=True)
        with open(a.profile, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["module", "tests", "seconds", "peak_mb"])
            w.writerows(sorted(prof, key=lambda r: -r[3]))
    bad = counts["failures"] or counts["errors"] or counts["unexpected successes"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
