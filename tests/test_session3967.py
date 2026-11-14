"""Session 3967 (chain 278): PortWatch's retries outlast ArcGIS Online's per-minute quota.

On 14 November 2026 the daily run's `portwatch` step failed: the third page of the Strait of Hormuz answered HTTP 429
("API calls quota exceeded") on four tries within 30 seconds, the shared waits of 5, 10 and 15 seconds. The quota is
counted per minute, so the connector now waits 20, 40 and 60 seconds between tries. No network: the service is a fake.
"""
import importlib.util
import os
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def portwatch():
    spec = importlib.util.spec_from_file_location("portwatch_3967", os.path.join(ROOT, "warehouse", "connectors", "portwatch.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Fake:
    def __init__(self, body):
        self.status_code, self._body, self.url = 200, body, "https://services9.arcgis.com/fake/query"

    def json(self):
        return self._body


QUOTA = {"error": {"code": 429, "message": "Unable to perform query. Too many requests.",
                   "details": ["API calls quota exceeded (6012 request units)"]}}
PAGE = {"features": [{"attributes": {"portid": "chokepoint6", "date": 1_700_000_000_000, "n_total": 50}}],
        "exceededTransferLimit": False}


class TheRetries(unittest.TestCase):
    def setUp(self):
        self.pw = portwatch()
        self.waits = []

    def run_with(self, answers):
        it = iter(answers)
        with mock.patch.object(self.pw.requests, "get", side_effect=lambda *a, **k: Fake(next(it))), \
                mock.patch.object(self.pw.ip.time, "sleep", side_effect=self.waits.append), \
                mock.patch.object(self.pw.ip, "pull_deadline", return_value=None):
            return self.pw.fetch("chokepoint6", lambda *a: None)

    def test_three_quota_answers_then_the_page(self):
        df = self.run_with([QUOTA, QUOTA, QUOTA, PAGE])
        self.assertEqual(len(df), 1)
        self.assertEqual(self.waits, [20, 40, 60])
        # the fourth try comes two minutes after the first: past the quota's minute
        self.assertGreaterEqual(sum(self.waits), 60)

    def test_four_quota_answers_still_fail_loudly(self):
        with self.assertRaises(RuntimeError) as e:
            self.run_with([QUOTA] * 4)
        self.assertIn("failed after 4 attempts", str(e.exception))
        self.assertIn("429", str(e.exception))

    def test_the_wait_is_the_connectors_own(self):
        self.assertEqual(self.pw.RETRY_WAIT, 20)
        self.assertEqual(self.pw.ip.RETRIES, 4)


if __name__ == "__main__":
    unittest.main()
