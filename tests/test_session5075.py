"""Session 5075 (chain 243, portable laptop window P1): Automated Analysis's weekly run, end to end, as a dry run.

warehouse/analysis/run.py --out-dir <folder> runs the whole week (every template and watch line, the rule's choice,
the three charts, the caption, chart_of_the_week.json, results.json, the history, templates.json and tables.json) into
a folder outside the repository: no model is called, no status row is written, nothing under docs/ or warehouse/
moves. The tests here hold that (no network, no model). The run itself, on the live set's public tables, is
TheWholeWeekOnTheLiveSet: it runs when ERW_LIVE_TESTS=1 and the anon key is in the environment, and checks that the
files are the ones the site's build reads (site/scripts/build-content.mjs: a YYYY-Www folder with chart_of_the_week.json
and results.json), with every field the last published week carries.
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "docs", "analysis")


def engine():
    for p in ("warehouse/analysis", "warehouse/analysis/templates", "warehouse/news", "warehouse/connectors", "warehouse"):
        q = os.path.join(ROOT, *p.split("/"))
        if q not in sys.path:
            sys.path.insert(0, q)
    import run
    import templates
    return run, templates


def stamp(paths):
    """The modification time of every file under the given paths (what a run must not move)."""
    out = {}
    for p in paths:
        if os.path.isfile(p):
            out[p] = os.path.getmtime(p)
        for d, _, fs in os.walk(p):
            for f in fs:
                out[os.path.join(d, f)] = os.path.getmtime(os.path.join(d, f))
    return out


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.eng, cls.templates = engine()
        except Exception as exc:  # a machine without the engine's packages
            raise unittest.SkipTest(f"the analysis engine cannot be imported here: {exc!r}")

    def setUp(self):
        r = self.eng
        self.saved = (r.DOCS, r.HISTORY, r.INTERNAL, self.templates.load_all, r.ip.write_status)
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        r = self.eng
        r.DOCS, r.HISTORY, r.INTERNAL, self.templates.load_all, r.ip.write_status = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)


class TheFolder(Base):
    def test_a_folder_inside_the_repository_is_refused(self):
        with self.assertRaises(ValueError):
            self.eng.use_out_dir(os.path.join(ROOT, "runs", "x"))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.eng.main(["--out-dir", os.path.join(ROOT, "runs", "x")])

    def test_not_with_the_other_modes(self):
        for flag in ("--dry-run", "--gallery-only", "--tables-only"):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit, msg=flag):
                self.eng.main(["--out-dir", self.tmp, flag])

    def test_every_path_follows_the_folder_and_the_history_is_copied(self):
        here = self.eng.use_out_dir(self.tmp)
        self.assertEqual(here, os.path.abspath(self.tmp))
        for p in (self.eng.DOCS, self.eng.HISTORY, self.eng.INTERNAL):
            self.assertTrue(os.path.abspath(p).startswith(os.path.abspath(self.tmp)), p)
        source = os.path.join(ANALYSIS, "history.csv")
        if os.path.exists(source):
            with open(source, encoding="utf-8") as a, open(self.eng.HISTORY, encoding="utf-8") as b:
                self.assertEqual(a.read(), b.read())

    def test_a_failed_run_writes_its_log_in_the_folder_and_nothing_else(self):
        calls = []
        self.eng.ip.write_status = lambda *a, **k: calls.append(a)

        def no_tables():
            raise RuntimeError("no tables in this test")
        self.templates.load_all = no_tables
        before = stamp([ANALYSIS, os.path.join(ROOT, "warehouse", "metadata", "run_status.csv"), os.path.join(ROOT, "warehouse", "output")])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = self.eng.main(["--out-dir", self.tmp, "--no-gallery"])
        self.assertEqual(code, 1)
        self.assertEqual(calls, [])                                                  # no status row
        logs = [f for f in os.listdir(self.tmp) if f.startswith("analysis_") and f.endswith(".log")]
        self.assertEqual(len(logs), 1)
        with open(os.path.join(self.tmp, logs[0]), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("no tables in this test", text)
        self.assertIn("no status row (--out-dir", text)
        self.assertEqual(stamp([ANALYSIS, os.path.join(ROOT, "warehouse", "metadata", "run_status.csv"), os.path.join(ROOT, "warehouse", "output")]), before)

    def test_the_note_documents_the_dry_run(self):
        with open(os.path.join(ROOT, "docs", "methods", "automated_analysis.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("--out-dir", note)
        self.assertIn("tests/test_session5075.py", note)


@unittest.skipUnless(os.environ.get("ERW_LIVE_TESTS") == "1" and os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"),
                     "the whole week on the live set runs with ERW_LIVE_TESTS=1 and the anon key")
class TheWholeWeekOnTheLiveSet(Base):
    def test_the_week_is_made_end_to_end_in_the_folder(self):
        os.environ["ERW_BACKEND"] = "live"
        before = stamp([ANALYSIS, os.path.join(ROOT, "warehouse", "metadata", "run_status.csv")])
        with contextlib.redirect_stdout(io.StringIO()):
            code = self.eng.main(["--out-dir", self.tmp, "--no-gallery"])
        self.assertEqual(code, 0)
        self.assertEqual(stamp([ANALYSIS, os.path.join(ROOT, "warehouse", "metadata", "run_status.csv")]), before)
        docs = os.path.join(self.tmp, "docs", "analysis")
        weeks = [w for w in os.listdir(docs) if re.match(r"^\d{4}-W\d{2}$", w)]                 # build-content.mjs's test
        self.assertEqual(len(weeks), 1)
        week = os.path.join(docs, weeks[0])
        for f in ("chart_of_the_week.json", "results.json", "chart_email.png", "social_1200x627.png", "social_1080x1080.png"):
            self.assertGreater(os.path.getsize(os.path.join(week, f)), 0, f)
        with open(os.path.join(week, "chart_of_the_week.json"), encoding="utf-8") as f:
            cow = json.load(f)
        with open(os.path.join(week, "results.json"), encoding="utf-8") as f:
            res = json.load(f)
        self.assertEqual(res["picked"], cow["template"])
        self.assertEqual(cow["note_by"], "the finding and the template's own sentence")   # no model
        published = sorted(w for w in os.listdir(ANALYSIS) if re.match(r"^\d{4}-W\d{2}$", w))[-1]
        with open(os.path.join(ANALYSIS, published, "chart_of_the_week.json"), encoding="utf-8") as f:
            last = json.load(f)
        self.assertEqual(sorted(set(last) - set(cow)), [])                                     # every field the page reads
        social = os.listdir(os.path.join(docs, "social"))
        self.assertIn(f"{weeks[0]}_{cow['template']}_caption.txt", social)
        with open(os.path.join(docs, "history.csv"), encoding="utf-8") as f:
            self.assertIn(f"{weeks[0]},", f.read())


if __name__ == "__main__":
    unittest.main()
