"""Session 3795 (chain 215): the per-reactor outages' daily step. eia_nuclear_outages_generator.py --new-days asks EIA,
fresh (never a saved page), only for the days after the held table's newest day, writes the held rows with the new
ones, stops when the first new day does not follow the held table, and writes nothing (no failure) when EIA has no new
day. The data machine's table block runs it daily, then nuclear_fleet_status on it.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""

import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia_nuclear_outages_generator as N  # noqa: E402

UNITS = {"capacity-units": "megawatts", "outage-units": "megawatts", "percentOutage-units": "percent"}


def rec(day, gen="1"):
    return dict(period=day, facility="46", facilityName="Browns Ferry", generator=gen, capacity="1254.7", outage="0", percentOutage="0", **UNITS)


class Answer:
    def __init__(self, days, url):
        self.status_code, self.url, self._days = 200, url, days

    def raise_for_status(self):
        pass

    def json(self):
        return {"response": {"total": str(len(self._days)), "data": [rec(d) for d in self._days]}}


class NewDays(unittest.TestCase):
    def run_new(self, held_days, new_days):
        held_dir = tempfile.mkdtemp()
        held = N.rows([rec(d) for d in held_days], "u", "2026-11-01T00:00:00Z")[N.ip.SERIES_COLS]
        with open(os.path.join(held_dir, N.NAME + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# a held table\n")
            held.to_csv(f, index=False, lineterminator="\n")
        asked = []

        def get(url, timeout=None):
            asked.append(url)
            return Answer(new_days, url)

        with mock.patch.object(N.ip, "OUT_DIR", held_dir), \
             mock.patch.object(N.ip, "load_key", return_value="k"), \
             mock.patch.object(N.ip, "raw_cached", side_effect=AssertionError("a saved page was read")), \
             mock.patch.object(N.requests, "get", side_effect=get), \
             mock.patch.object(N.time, "sleep"), \
             mock.patch.object(N.ip, "write_snapshot") as ws:
            rc = N.main(["--new-days", "--out-dir", tempfile.mkdtemp()])
        return rc, ws, asked

    def test_the_new_days_join_the_held_rows(self):
        rc, ws, asked = self.run_new(["2026-10-20", "2026-10-21"], ["2026-10-22", "2026-10-23"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(asked), 1)
        self.assertIn("start=2026-10-22", asked[0])
        t = ws.call_args[0][0]
        self.assertEqual(len(t), 12)                      # four days of one reactor, three variables
        self.assertEqual((t["ts_utc"].min()[:10], t["ts_utc"].max()[:10]), ("2026-10-20", "2026-10-23"))

    def test_a_gap_after_the_held_table_stops(self):
        rc, ws, _ = self.run_new(["2026-10-20", "2026-10-21"], ["2026-10-23"])
        self.assertEqual(rc, 1)
        ws.assert_not_called()

    def test_no_new_day_is_no_failure(self):
        rc, ws, asked = self.run_new(["2026-10-20", "2026-10-21"], [])
        self.assertEqual(rc, 0)
        self.assertEqual(len(asked), 1)
        ws.assert_not_called()


class TheBlock(unittest.TestCase):
    def test_daily_after_the_reactor_status_and_the_fleet_after_it(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine_tables.sh"), encoding="utf-8") as f:
            t = f.read()
        steps = t.split("TABLE_STEPS=(", 1)[1].split("\n)", 1)[0]
        a = steps.index('"dm_nrc_reactor_status|')
        b = steps.index('"dm_nuclear_outages_gen|eia_nuclear_outages_generator_daily|daily|warehouse/connectors/eia_nuclear_outages_generator.py --new-days"')
        c = steps.index('"dm_nuclear_fleet|nuclear_fleet_status|daily|warehouse/derived/nuclear_fleet_status.py"')
        self.assertLess(a, b)
        self.assertLess(b, c)

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_nuclear_outages_generator.py", "tests/test_session3795.py", "warehouse/run_data_machine_tables.sh"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                s = h.read()
            self.assertNotIn(chr(0x2014), s, f)
            self.assertNotIn(chr(0x2013), s, f)


if __name__ == "__main__":
    unittest.main()
