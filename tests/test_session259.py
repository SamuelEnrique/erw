"""Session 259: no raw file under warehouse/output is in git, and the tests leave none behind.

Energy Research Warehouse (ERW). Sessions 237 and 238's landing (11c833a3) committed 35 files named
warehouse/output/raw/madeup_as_prices/<run>/manifest.csv: each a header line and no row, written by the made-up source
of tests/test_session85.py whenever the whole suite ran in one process. Two faults made them, and one let them in:

- tests/test_session114_part2.py put the output paths back with iso_prices.set_out_dir(the old OUT_DIR), which leaves
  RAW_DIR (and METADATA_DIR and STATUS_DIR) under warehouse/output for every test that runs after it;
- tests/test_session85.py ran its made-up source with --out-dir, and the runner keeps RAW_DIR whatever --out-dir says;
- warehouse/output/raw/ was not ignored, so a `git add` of a folder took the residue with it.

Samuel's ruling (the chain of 13 October 2026): remove the 35 files, and a test keeps them out. This is that test.
"""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))

RAW_UNDER_OUTPUT = "warehouse/output/raw"
MADE_UP = "madeup_as_prices"


def git(*args):
    """(exit code, output) of a git command in the repository, or (None, "") where git cannot be run."""
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    return r.returncode, r.stdout


def runs_of(folder):
    """The run folders of the made-up source under a raw folder (an absent folder holds none)."""
    d = os.path.join(folder, MADE_UP)
    return set(os.listdir(d)) if os.path.isdir(d) else set()


class InGit(unittest.TestCase):
    """What git holds, and what it would refuse."""

    def setUp(self):
        code, out = git("rev-parse", "--is-inside-work-tree")
        if code != 0 or out.strip() != "true":
            self.skipTest("not a git checkout")

    def test_no_file_under_the_output_raw_folder_is_tracked(self):
        code, out = git("ls-files", "--", RAW_UNDER_OUTPUT)
        self.assertEqual(code, 0)
        self.assertEqual(out.split(), [], "raw files under warehouse/output are in git: `git rm --cached` them")

    def test_no_file_of_the_made_up_source_is_tracked_anywhere(self):
        code, out = git("ls-files")
        self.assertEqual(code, 0)
        self.assertEqual([p for p in out.splitlines() if f"/{MADE_UP}/" in p], [])

    def test_the_folder_is_ignored(self):
        code, _ = git("check-ignore", "-q", f"{RAW_UNDER_OUTPUT}/{MADE_UP}/20261005T022808Z/manifest.csv")
        self.assertEqual(code, 0, f"{RAW_UNDER_OUTPUT}/ is not ignored: .gitignore has lost its line")
        with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as f:
            self.assertIn(RAW_UNDER_OUTPUT + "/", [ln.strip() for ln in f])


class NoResidue(unittest.TestCase):
    """The made-up source of tests/test_session85.py writes nothing into the repository, wherever RAW_DIR points."""

    def test_the_made_up_source_leaves_no_run_folder(self):
        try:
            import iso_prices as ip
            import test_session85
        except ImportError as exc:  # a machine without the connectors' libraries: the suite there cannot write them either
            self.skipTest(f"the connectors cannot be imported here ({exc})")
        output_raw = os.path.join(ROOT, "warehouse", "output", "raw")
        store_raw = os.path.join(ROOT, "warehouse", "raw")
        keep = ip.RAW_DIR
        try:
            for pointed in (store_raw, output_raw):    # as a fresh process has it, and as a leaking test left it
                ip.RAW_DIR = pointed
                before = (runs_of(store_raw), runs_of(output_raw))
                suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_session85.Run)
                self.assertGreaterEqual(suite.countTestCases(), 2)
                with open(os.devnull, "w", encoding="utf-8") as quiet:
                    result = unittest.TextTestRunner(stream=quiet, verbosity=0).run(suite)
                self.assertTrue(result.wasSuccessful(), result.failures + result.errors)
                self.assertEqual(ip.RAW_DIR, pointed)                               # put back as it was found
                self.assertEqual((runs_of(store_raw), runs_of(output_raw)), before, f"a run folder was written with RAW_DIR at {pointed}")
        finally:
            ip.RAW_DIR = keep

    def test_the_cleanup_that_left_the_raw_folder_under_output_is_gone(self):
        with open(os.path.join(HERE, "test_session114_part2.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("addCleanup(ip.set_out_dir", src)
        self.assertEqual(src.count("redirected(self, tmp)"), 3)


if __name__ == "__main__":
    unittest.main()
