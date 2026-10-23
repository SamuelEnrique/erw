"""Session 1042 (chain 072): the replication of the All grids tab compares ERCOT's reserve margin as the builder writes
it, rounded to six decimals (siting_page.reserve_margins); unrounded, the run against production failed it on a
difference below a millionth. No request, no model call."""
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplication(unittest.TestCase):
    def test_the_margin_is_rounded_as_the_builder_writes_it(self):
        m = load("repl_siting_1042", "warehouse", "replication", "siting.py")
        with open(os.path.join(ROOT, "site", "data", "siting", "headroom.json"), encoding="utf-8") as f:
            as_of = json.load(f)["reserve"]["as_of"]
        y = int(as_of[:4])
        got = m.reserve_figures(ROOT, [{"ts_utc": f"{y + 1}-06-01T00:00:00Z", "value": "11.42838337265"}])
        self.assertEqual(got, {"allgrids|reservemargin|ercot:HB_HUBAVG": 11.428383})


if __name__ == "__main__":
    unittest.main()
