"""Session 2958 (chain 157): the All grids tab's Headroom column draws the grid's active interconnection queue from
iso_queue_snapshot_summary, keyed allgrids|queue|<row>, written whole, for CAISO, ERCOT and SPP; ISO-NE's, MISO's and
NYISO's queues are held for a license and read "license needed". No request, no model call."""
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheQueueLine(unittest.TestCase):
    def test_the_file(self):
        q = json.loads(src("site", "data", "siting", "headroom.json"))["queue"]
        self.assertEqual(q["table"], "iso_queue_snapshot_summary")
        self.assertEqual(sorted(q["grids"]), ["caiso", "ercot", "spp"])
        self.assertEqual(sorted(q["held"]), ["isone", "miso", "nyiso"])
        self.assertEqual(q["grids"]["ercot"]["active_mw"], 298606.0)

    def test_the_page_and_the_key(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("allgrids|queue|${r.id}", v)
        self.assertIn("data-headroom-queue=", v)
        s = src("site", "lib", "siting.ts")
        self.assertIn('p[1] === "queue"', s)
        self.assertIn('words: "license needed"', s)
        self.assertIn(r"(^allgrids\|queue\|)", src("site", "scripts", "check-values.mjs"))

    def test_the_replication(self):
        spec = importlib.util.spec_from_file_location("repl_2958", os.path.join(ROOT, "warehouse", "replication", "siting.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        rows = [{"entity": "iso_queue:ercot:solar", "variable": "active_mw", "value": "10.5", "x_grid": "ercot"},
                {"entity": "iso_queue:ercot:wind", "variable": "active_mw", "value": "4.5", "x_grid": "ercot"},
                {"entity": "iso_queue:ercot", "variable": "entered_mw", "value": "99", "x_grid": "ercot"}]
        self.assertEqual(m.queue_figures(rows, ["ercot:HB_HUBAVG", "nyiso:N.Y.C."]), {"allgrids|queue|ercot:HB_HUBAVG": 15.0})


if __name__ == "__main__":
    unittest.main()
