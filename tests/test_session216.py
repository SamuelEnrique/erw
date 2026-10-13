"""Session 216: four small rulings (the owner's chain prompt of 12 October 2026, evening).

1. ercot_large_load_queue: ERCOT publishes no request-level large-load list (a known gap by design since session 17).
   On GitHub's runner the connector's watch is recorded as skipped with the reason, as the other known gaps are since
   session 206, not as a failed step every Monday; anywhere else the failure stands.
2. Session 206's questions 1 and 5: the other model steps stay on Sonnet; the shadow scorer stays. No change.
3. docs/tooling.md says the tools are on both machines, chrome-devtools-mcp proven on the old laptop only.
4. queue/todo/005 is in queue/done/ with one line why (session 206 did the CARB half; NYISO's queue stays held).
"""
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import ercot_large_load as ell  # noqa: E402
import iso_prices as ip  # noqa: E402


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class FakeLog:
    def __init__(self, path):
        self.path = path
        self.lines = []

    def __call__(self, s):
        self.lines.append(s)

    def close(self):
        pass


class FakeResponse:
    status_code = 200
    text = "<html><body><p>Large Load Integration</p><a href='/files/docs/form.xlsx'>Interconnection Request Form</a></body></html>"
    content = b""


class TheWatchAsASkip(unittest.TestCase):
    """The connector's main, with ERCOT's page stubbed to one that links no status report or queue."""

    def run_main(self, on_runner):
        tmp = tempfile.mkdtemp()
        written = []
        saved = (ell.ip.with_retries, ell.ip.write_status, ell.ip.Log, ell.ip.RAW.open, ell.ip.LOG_DIR, ell.ip.on_runner, ell.ip.update_sources)
        try:
            ell.ip.with_retries = lambda name, fn, log, **kw: FakeResponse()
            ell.ip.write_status = lambda connector, run_id, rows: written.extend(rows)
            ell.ip.Log = FakeLog
            ell.ip.RAW.open = lambda *a, **k: None
            ell.ip.LOG_DIR = tmp
            ell.ip.on_runner = lambda: on_runner
            ell.ip.update_sources = lambda *a, **k: None
            out, err = io.StringIO(), io.StringIO()
            so, se = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = out, err
            try:
                code = ell.main()
            finally:
                sys.stdout, sys.stderr = so, se
            return code, written, out.getvalue(), err.getvalue()
        finally:
            (ell.ip.with_retries, ell.ip.write_status, ell.ip.Log, ell.ip.RAW.open, ell.ip.LOG_DIR, ell.ip.on_runner, ell.ip.update_sources) = saved

    def test_on_the_runner_the_gap_is_a_skip(self):
        code, written, out, err = self.run_main(on_runner=True)
        self.assertEqual(code, ip.skip_exit())
        self.assertEqual(len(written), 1)
        self.assertEqual(written[0]["status"], "skipped")
        self.assertIn("a known gap on the GitHub runner since 2026-09-27", written[0]["detail"])
        self.assertIn("ERCOT publishes no request-level large-load list", written[0]["detail"])
        self.assertIn("ercot_large_load ercot_large_load_queue SKIPPED: a known gap", out)
        self.assertNotIn("FAILED", err)

    def test_off_the_runner_the_failure_stands(self):
        code, written, out, err = self.run_main(on_runner=False)
        self.assertEqual(code, 1)
        self.assertEqual(written[0]["status"], "failed")
        self.assertIn("iso_prices.SourceGap: ERCOT publishes no request-level large-load list", written[0]["detail"])
        self.assertIn("FAILED, no output file written", err)

    def test_the_gap_is_still_in_the_file(self):
        g = ip.known_gap("ercot_large_load_queue")
        self.assertIsNotNone(g)
        self.assertEqual(g["since"], "2026-09-27")


class TheOtherRulings(unittest.TestCase):
    def test_the_model_steps_and_the_shadow_scorer_are_unchanged(self):
        score = src("warehouse", "news", "score.py")
        self.assertIn('NEWS_SCORE_MODEL = "claude-haiku-4-5"', score)
        self.assertIn("def pick_model", score)  # the other steps' Sonnet
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "news", "shadow.py")))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "config", "shadow.yaml")))

    def test_tooling_says_both_machines_and_where_the_browser_tool_is_proven(self):
        t = src("docs", "tooling.md")
        self.assertIn("**They are on both machines**", t)
        self.assertIn("`lab-desktop` (the data machine, session 207)", t)
        self.assertIn("**chrome-devtools-mcp is proven on the old laptop only:**", t)
        self.assertNotIn("**They are on one machine.**", t)

    def test_task_005_is_done_with_its_reason(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "queue", "todo", "005-data-refresh-runner-blocked.md")))
        done = src("queue", "done", "005-data-refresh-runner-blocked.md")
        self.assertIn("## Report (session 216, 13 October 2026)", done)
        self.assertIn("NYISO's queue workbook is not pulled", done)
        self.assertIn("SESSION_206_REPORT.md", done)


if __name__ == "__main__":
    unittest.main()
