"""Session 1020 (chain 071): the All grids replication counts its requests to the live set and prints the count on its
last line, so a chain session can set it beside its ceiling (session 1020's run made about 32 against a ceiling of 20,
counted after the fact). No request, no model call: the reader is given three pages of a fake answer."""
import importlib.util
import io
import json
import os
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("erw_replication_siting_1020", os.path.join(ROOT, "warehouse", "replication", "siting.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Answer(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class Counted(unittest.TestCase):
    def test_each_page_is_one_request(self):
        m = load()
        pages = [[{"v": i} for i in range(1000)], [{"v": i} for i in range(1000)], [{"v": 1}] * 5]
        seen = []

        def fake(req, timeout=None):
            seen.append(req.headers.get("Range"))
            return Answer(json.dumps(pages[len(seen) - 1]).encode())

        m.LIVE_REQUESTS[0] = 0
        with mock.patch.object(m.urllib.request, "urlopen", fake):
            rows = m.rest("https://example.invalid/rest/v1", "anon", "series", {"table_name": "eq.t"})
        self.assertEqual(len(rows), 2005)
        self.assertEqual(m.LIVE_REQUESTS[0], 3)
        self.assertEqual(seen, ["0-999", "1000-1999", "2000-2999"])

    def test_the_count_is_printed_last(self):
        with open(os.path.join(ROOT, "warehouse", "replication", "siting.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('print(f"{LIVE_REQUESTS[0]} requests to the live set")', s)
        self.assertLess(s.index("figures computed;"), s.index("requests to the live set\")"))


if __name__ == "__main__":
    unittest.main()
