"""Session 7015 (chain 301): ERCOT's real-time hub history takes a Central day it lacks from the node table this machine
pulls from the same report (NP6-905-CD), whole days only. On 16 November 2026 the history lacked 15 October and 5 to
8 November 2026 (days the runner missed while ERCOT listed them), and the peak premium refused October. No request, no
model call."""
import datetime as dt
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import hub_history  # noqa: E402
import iso_prices as ip  # noqa: E402


def day_rows(day, hubs, source, skip=0):
    """Every quarter hour of a Central day, for each hub, less the last `skip` intervals."""
    start = pd.Timestamp(day).tz_localize("America/Chicago").tz_convert("UTC")
    end = pd.Timestamp(day + dt.timedelta(days=1)).tz_localize("America/Chicago").tz_convert("UTC")
    ts = list(pd.date_range(start, end, freq="15min", inclusive="left"))
    ts = ts[:len(ts) - skip] if skip else ts
    return pd.DataFrame([dict(entity=f"ercot:{h}", variable="spp_rtm", ts_utc=t.strftime("%Y-%m-%dT%H:%M:%SZ"), value=10.0,
                              unit="USD/MWh", freq="PT15M", geo="US-TX", market="ercot_rtm", node=h, source=source,
                              source_url=f"u-{source}", retrieved_at="r", vintage="") for t in ts for h in hubs])


def put(d, name, frame):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="") as f:
        f.write("# a stand-in\n")
        frame[ip.SERIES_COLS].to_csv(f, index=False, lineterminator="\n")


class TheFill(unittest.TestCase):
    def test_a_day_wholly_absent_is_taken_whole_and_no_other(self):
        hubs = ["HB_NORTH", "HB_WEST"]
        d1, d2, d3, d4 = (dt.date(2026, 10, 14), dt.date(2026, 10, 15), dt.date(2026, 10, 16), dt.date(2026, 11, 1))
        with tempfile.TemporaryDirectory() as d, mock.patch.object(ip, "OUT_DIR", d), \
                mock.patch.object(ip, "LOG_DIR", os.path.join(d, "logs")):
            os.makedirs(os.path.join(d, "logs"))
            # the history holds the 14th and part of the 16th; the live table nothing
            put(d, "ercot_rtm_hub_prices_2026", pd.concat([day_rows(d1, hubs, "hist"), day_rows(d3, hubs, "hist", skip=90)]))
            put(d, "iso_rtm_hub_prices", day_rows(d1, hubs, "live").iloc[:0])
            # the node table holds the 14th to the 16th whole, 1 November (25 hours) whole, and a hub the history lacks
            node = pd.concat([day_rows(x, hubs + ["HB_PAN"], "node") for x in (d1, d2, d3, d4)])
            node = node.assign(market="", node="sp", x_point_type="HU")
            with open(os.path.join(d, hub_history.NODE_TABLE + ".csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# a stand-in, # a hash inside a header line" + chr(10) + "# a second header line" + chr(10))
                node[ip.SERIES_COLS + ["x_point_type"]].to_csv(f, index=False, lineterminator=chr(10))   # its extra column
            log = ip.Log(os.path.join(d, "logs", "t.log"))
            n = hub_history.fill_from_nodes(log, "RUN")
            log.close()
            got = ip.read_series(os.path.join(d, "ercot_rtm_hub_prices_2026.csv"))
            days = pd.to_datetime(got["ts_utc"], utc=True).dt.tz_convert("America/Chicago").dt.date
            filled = got[got["source"] == "node"]
            self.assertEqual(sorted(set(days[got["source"] == "node"])), [d2, d4])   # the 16th is partly held: left alone
            self.assertEqual(n, len(filled))
            self.assertEqual(len(filled), 2 * 96 + 2 * 100)                           # 1 November has 25 hours
            self.assertEqual(set(filled["entity"]), {"ercot:HB_NORTH", "ercot:HB_WEST"})   # no hub the member lacks
            self.assertEqual(set(filled["market"]), {"ercot_rtm"})
            self.assertEqual(set(filled["node"]), {"HB_NORTH", "HB_WEST"})
            self.assertEqual(set(filled["source_url"]), {"u-node"})                    # each row keeps its own address
            self.assertEqual(len(got[got["source"] == "hist"]), 2 * 96 + 2 * 6)        # the held rows untouched
            with open(os.path.join(d, "ercot_rtm_hub_prices_2026.csv"), encoding="utf-8") as f:
                self.assertEqual(sum(1 for ln in f if ln.startswith("# " + hub_history.NODE_MARK)), 1)

    def test_an_incomplete_day_of_the_node_table_is_not_taken(self):
        hubs = ["HB_NORTH"]
        d2 = dt.date(2026, 10, 15)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(ip, "OUT_DIR", d), \
                mock.patch.object(ip, "LOG_DIR", os.path.join(d, "logs")):
            os.makedirs(os.path.join(d, "logs"))
            put(d, "ercot_rtm_hub_prices_2026", day_rows(dt.date(2026, 10, 14), hubs, "hist"))
            put(d, hub_history.NODE_TABLE, day_rows(d2, hubs, "node", skip=1))
            log = ip.Log(os.path.join(d, "logs", "t.log"))
            self.assertEqual(hub_history.fill_from_nodes(log, "RUN"), 0)
            log.close()

    def test_without_the_node_table_nothing_is_filled(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(ip, "OUT_DIR", d):
            log = mock.Mock()
            self.assertEqual(hub_history.fill_from_nodes(log, "RUN"), 0)

    def test_the_daily_step_calls_it_before_the_build(self):
        with open(os.path.join(ROOT, "warehouse", "connectors", "hub_history.py"), encoding="utf-8") as f:
            s = f.read()
        body = s[s.index("def append_ercot("):]
        self.assertLess(body.index("filled = fill_from_nodes(log, run_id)"), body.index('run(["build", "--family", ERCOT_HISTORY])'))


if __name__ == "__main__":
    unittest.main()
