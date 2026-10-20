"""Session 377: a day's health file keeps its "## Root causes" section when warehouse/health.py summary writes it again
(the daily run writes yesterday's file; a session may have added the causes before it), and the reliability documents
the session wrote: the root causes of 6 to 20 October, and the draft alert policy in docs/machines.md."""

import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import health  # noqa: E402

ROWS = [{"at": "2026-10-20T00:26:00+00:00", "workflow": "daily prices", "run_id": "1", "step": "eia930",
         "status": "failed", "reason": "eia930 FAILED: boom"}]


class Kept(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def write(self, rows=ROWS):
        with mock.patch.object(health, "write_days", lambda *a, **k: None):
            path, _ = health.summary("2026-10-20", out_dir=self.d, rows=rows)
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_no_section_is_written_from_nothing(self):
        self.assertNotIn(health.ROOT_CAUSES, self.write())

    def test_the_section_survives_a_rewrite(self):
        first = self.write()
        causes = health.ROOT_CAUSES + "\n\n- 00:26 UTC, eia930: the cause, fixed by session 336.\n"
        with open(os.path.join(self.d, "2026-10-20-health.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(first + "\n" + causes)
        again = self.write(ROWS + [dict(ROWS[0], at="2026-10-20T02:17:00+00:00", step="generation_mix")])
        self.assertIn("**2 failures**", again)
        self.assertEqual(again.count(health.ROOT_CAUSES), 1)
        self.assertTrue(again.endswith(causes))

    def test_a_section_in_the_middle_is_kept_alone(self):
        text = self.write() + "\n" + health.ROOT_CAUSES + "\n\n- one\n\n## Later\n\n- not the causes\n"
        with open(os.path.join(self.d, "2026-10-20-health.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        self.assertEqual(health.kept_causes(os.path.join(self.d, "2026-10-20-health.md")),
                         health.ROOT_CAUSES + "\n\n- one\n")


class StorageFull(unittest.TestCase):
    """Redivis's free storage full (20 October: ercot_all_hub_prices_history's stores, dm_ercot_hub_append_stores) is a
    skip, as session 305 made the export cap one: the table waits in the archive."""

    def setUp(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
        import upload
        self.up = upload

    def test_the_answer_is_read(self):
        exc = RuntimeError("APIError: [400 invalid_request] This import would cause your account to exceed its free storage "
                           "allotment of 10GB.\nTotal storage after this import would be 10.1GB.")
        self.assertTrue(self.up.storage_full(exc))
        self.assertFalse(self.up.capped(exc))
        self.assertFalse(self.up.storage_full(RuntimeError("HTTP 500")))

    def test_the_upload_loop_skips_it(self):
        with open(self.up.__file__, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("if storage_full(exc):", src)
        self.assertIn("r[3] not in (CAP_SKIP, STORAGE_SKIP)", src)
        self.assertIn('print(f"upload SKIPPED: {STORAGE_SKIP}', src)


class Documents(unittest.TestCase):
    def test_every_day_with_a_failure_has_its_causes(self):
        d = os.path.join(ROOT, "queue", "summary")
        for day in range(6, 21):
            p = os.path.join(d, f"2026-10-{day:02d}-health.md")
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8") as f:
                text = f.read()
            if "## Failures (failed twice)" in text:
                self.assertIn(health.ROOT_CAUSES, text, p)

    def test_the_draft_alert_policy(self):
        with open(os.path.join(ROOT, "docs", "machines.md"), encoding="utf-8") as f:
            text = f.read()
        i = text.find("### One alert policy, draft for Samuel's ruling")
        self.assertGreater(i, 0)
        j = text.find("\n## ", i + 1)
        section = text[i:j if j > 0 else len(text)]
        self.assertIn("draft for Samuel's ruling", section)
        rules = [ln for ln in section.splitlines() if re.match(r"\d+\. ", ln)]
        self.assertTrue(1 <= len(rules) <= 10, rules)


if __name__ == "__main__":
    unittest.main()
