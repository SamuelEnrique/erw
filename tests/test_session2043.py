"""Session 2043: the NRC's event notification reports.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nrc_event_reports.py on a raw file and a daily page built
here in the NRC's forms (made up for the test, not the NRC's): power reactor reports kept and the rest dropped, one row a
unit, the event's time turned to UTC from the zone the report names, a scram read from the scram code or from
50.72(b)(2)(iv)(B); a label not in the map, a zone not in the map and a report given twice with different contents
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2043 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nrc_event_reports as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def raw_line(**kw):
    r = {f: "" for f in N.RAW_FIELDS}
    r.update(kw)
    return "|".join(r[f] for f in N.RAW_FIELDS) + "|"


RAW = "\n".join(["|".join(N.RAW_FIELDS) + "|",
                 raw_line(**{"Event Desc": "Power Reactor", "En No": "100", "Site Name": "Plant A", "Unit Ind1": "1",
                             "Unit Ind2": "2", "Notification Dt": "07/13/2025", "Notification Time": "15:00:00",
                             "Event Dt": "07/13/2025", "Event Time": "14:18:00", "Time Zone": "CDT",
                             "Cfr Cd1": "50.72(b)(2)(iv)(B)", "Cfr Descr1": "RPS Actuation - Critical",
                             "Scram Code 1": "A/R", "Initial PWR 1": "100", "Current PWR 1": "0",
                             "Scram Code 2": "N", "Initial PWR 2": "100", "Current PWR 2": "100", "Initial RX Mode 2": "Power Operation"}),
                 raw_line(**{"Event Desc": "Agreement State", "En No": "101", "Event Dt": "07/13/2025", "Time Zone": "EDT"})]).encode()


def block(en, kind, labels, table=True):
    rows = "".join(f"<b>{k}:</b> {v}<br>" for k, v in labels)
    tab = ("<table><tr><th>Unit</th><th>SCRAM Code</th><th>RX Crit</th><th>Initial PWR</th><th>Initial RX Mode</th>"
           "<th>Current PWR</th><th>Current RX Mode</th></tr><tr><td>3</td><td>N</td><td>Y</td><td>75</td>"
           "<td>Power Operation</td><td>0</td><td>Hot Shutdown</td></tr></table>") if table else ""
    return (f'<div class="grid border" id="en{en}"><div class="th">{kind}</div><div class="th">Event Number: {en}</div>'
            f"<div>{rows}</div><div><b>Emergency Class:</b> Non Emergency<br>10 CFR Section:<br>50.72(b)(2)(iv)(B) - RPS Actuation - Critical</div>"
            f"</div>{tab}<b>Event Text</b><div class=\"border\">text</div>")


LAB = [("Facility", "Plant B"), ("Region", "4"), ("State", "LA"), ("Unit", "[3] [ ] [ ]"), ("RX Type", "[3] CE"),
       ("Notification Date", "10/17/2026"), ("Notification Time", "01:10 [ET]"), ("Event Date", "10/16/2026"),
       ("Event Time", "22:45 [CDT]"), ("Last Update Date", "10/17/2026")]
PAGE = "<p>EVENT NUMBERS</p>" + block("200", "Power Reactor", LAB) + block("201", "Agreement State", [("Rep Org", "x")], table=False)


class Build(unittest.TestCase):
    def test_raw(self):
        rows = N.raw_events(RAW, "u", "r")
        self.assertEqual([r["event_id"] for r in rows], ["nrc_en:100:1", "nrc_en:100:2"])
        a, b = rows
        self.assertEqual((a["event_date"], a["event_type"], a["x_initial_power_pct"], a["x_current_power_pct"]),
                         ("2025-07-13T19:18:00Z", "reactor_scram", "100", "0"))
        self.assertEqual(b["event_type"], "reactor_scram")  # reported under 50.72(b)(2)(iv)(B), though unit 2's code is N
        self.assertEqual((a["x_notification_utc"], b["x_initial_mode"]), ("2025-07-13T19:00:00Z", "Power Operation"))

    def test_page(self):
        rows = N.page_events(PAGE, "u", "r")
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["event_id"], r["event_date"], r["x_event_tz"], r["x_scram_code"], r["x_current_mode"]),
                         ("nrc_en:200:3", "2026-10-17T03:45:00Z", "CDT", "N", "Hot Shutdown"))
        self.assertEqual((r["x_cfr"], r["x_cfr_words"], r["x_notification_utc"]),
                         ("50.72(b)(2)(iv)(B)", "RPS Actuation - Critical", "2026-10-17T05:10:00Z"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            N.page_events("<p>EVENT NUMBERS</p>" + block("200", "Power Reactor", LAB + [("Mystery", "x")]), "u", "r")
        with self.assertRaises(RuntimeError):
            N.to_utc("2026-10-16", "22:45", "XST")
        a = N.page_events(PAGE, "u", "r")[0]
        b = dict(a, x_initial_power_pct="50")
        with self.assertRaises(RuntimeError):
            N.build([a, b])
        self.assertEqual(len(N.build([a, dict(a, x_read_from="raw_file")])), 1)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.NAME), "power;uranium")
        self.assertIn(N.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
