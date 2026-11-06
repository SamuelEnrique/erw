"""Session 1601 (chain 165): the board's power rows made complete.

Held here, on real rows cut from the old laptop's tables (tests/fixtures/board_1601/): ERCOT's load zones are rows of
the power group, after the hubs, each day a mean of the complete local day's hours with a real-time hour the mean of its
four 15-minute prices; every power row states its interval (its "basis"); ERCOT's node basis is summarized by class of
point, monthly, with a link to the node view; ERCOT's real-time adders are daily rows, and an adder that has ended is
drawn as no row; the capacity auctions are one placeholder each, naming the publisher and the hold; the page's hover
of a row's name carries the interval. No network, no model. Nothing here sets the environment at import.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIX = os.path.join(ROOT, "tests", "fixtures", "board_1601")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def raw(name):
    return pd.read_csv(os.path.join(FIX, name + ".csv"), comment="#")


class OnTheFixture(unittest.TestCase):
    """Run one of the builder's steps with its tables read from the fixture folder."""

    def setUp(self):
        self.bp = builder()
        self.saved, self.absent, self.intervals = self.bp.ip.OUT_DIR, list(self.bp.ABSENT), dict(self.bp.INTERVALS)
        self.bp.ip.OUT_DIR = FIX
        self.holidays = self.bp.pb.nerc_holidays(range(2024, 2028))

    def tearDown(self):
        self.bp.ip.OUT_DIR, self.bp.ABSENT[:] = self.saved, self.absent
        self.bp.INTERVALS.clear(); self.bp.INTERVALS.update(self.intervals)

    def rows(self, b):
        return {r["id"]: r for r in b.rows}


class TheLoadZones(OnTheFixture):
    def build(self):
        b = self.bp.Board()
        store = self.bp.hourly_store(lambda s: None, tables=["ercot_zone_prices_history"])
        self.bp.build_power(b, store, self.holidays, lambda s: None)
        return self.rows(b)

    def expected(self, entity, market, day):
        """The day's mean of complete hours, from the fixture's rows, by its own arithmetic."""
        t = raw("ercot_zone_prices_history")
        t = t[(t["entity"] == entity) & (t["market"] == market)].copy()
        t["ts"] = pd.to_datetime(t["ts_utc"], utc=True)
        t["hour"] = t["ts"].dt.floor("h")
        per = 4 if market.endswith("rtm") else 1
        h = t.groupby("hour")["value"].agg(["mean", "size"])
        h = h[h["size"] == per]["mean"]
        local = h.index.tz_convert("America/Chicago")
        vals = h[[d.date() == day for d in local]]
        self.assertEqual(len(vals), 24)
        return round(float(vals.mean()), 4)

    def test_the_zones_are_rows_with_their_days(self):
        rows = self.build()
        for rid in ("ercot-lz-houston-da", "ercot-lz-houston-rt", "ercot-lz-aen-da"):
            self.assertEqual(rows[rid]["status"], "ok", rid)
            self.assertEqual(rows[rid]["tags"]["scope"], "all")
        # the warehouse holds Austin Energy's zone in day-ahead only: its real-time row says so, with no figure
        self.assertEqual(rows["ercot-lz-aen-rt"]["status"], "not_held")
        self.assertNotIn("last", rows["ercot-lz-aen-rt"])
        self.assertEqual(rows["ercot-lz-houston-da"]["label"], "ERCOT Houston load zone")
        day = dt.date(2026, 10, 12)
        s ={r["id"]: r for r in [rows["ercot-lz-houston-da"], rows["ercot-lz-houston-rt"]]}
        self.assertEqual(s["ercot-lz-houston-da"]["last"]["t"], "2026-10-13")
        self.assertEqual(s["ercot-lz-houston-da"]["moves"]["d"]["v"], self.expected("ercot:LZ_HOUSTON", "ercot_dam", day))
        self.assertEqual(s["ercot-lz-houston-rt"]["moves"]["d"]["v"], self.expected("ercot:LZ_HOUSTON", "ercot_rtm", day))
        self.assertEqual(s["ercot-lz-houston-da"]["source"], self.bp.ZONE_SOURCE)
        self.assertIn("ercot-lz-houston-da-minus-rt", rows)
        self.assertIn("ercot-lz-houston-rt-battery", rows)

    def test_every_row_states_its_interval(self):
        rows = self.build()
        self.assertIn("each hour the hour's day-ahead price", rows["ercot-lz-houston-da"]["basis"])
        self.assertIn("the mean of the hour's 4 15-minute real-time prices", rows["ercot-lz-houston-rt"]["basis"])
        self.assertIn("24; 23 or 25 on the daylight saving days", rows["ercot-lz-houston-rt"]["basis"])
        self.assertTrue(rows["ercot-lz-houston-rt-battery"]["basis"].startswith("The highest less the lowest"))
        for r in rows.values():
            if r["status"] == "ok":
                self.assertTrue(r.get("basis"), r["id"])

    def test_the_hour_words_by_interval(self):
        self.bp.INTERVALS.update({("caiso:X", "rt"): ("PT15M", "lmp_rtm_15m_mean"), ("spp:X", "rt"): ("PT5M", "lmp_rtm"), ("isone:X", "rt"): ("PT1H", "lmp_rtm")})
        self.assertIn("each the mean of the 5-minute prices within it", self.bp.hour_words("caiso:X", "rt"))
        self.assertIn("12 5-minute", self.bp.hour_words("spp:X", "rt"))
        self.assertIn("publishes it by the hour", self.bp.hour_words("isone:X", "rt"))
        self.assertEqual(self.bp.hour_words("spp:X", "da"), "the hour's day-ahead price")

    def test_hubs_before_zones(self):
        idx = pd.date_range("2026-10-10T05:00:00Z", periods=72, freq="h")
        h = pd.Series(30.0, index=idx)
        store = {("ercot:LZ_AEN", "da"): h, ("ercot:HB_WEST", "da"): h, ("ercot:HB_HUBAVG", "da"): h}
        b = self.bp.Board()
        self.bp.build_power(b, store, self.holidays, lambda s: None)
        order = [r["id"] for r in b.rows if r["group"] == "power" and r["id"].startswith("ercot-") and r["id"].endswith("-da")]
        self.assertEqual(order, ["ercot-hb-hubavg-da", "ercot-hb-west-da", "ercot-lz-aen-da"])


class TheNodeBasis(OnTheFixture):
    def test_a_row_a_class_with_the_link(self):
        b = self.bp.Board()
        self.bp.build_nodes(b, lambda s: None)
        rows = self.rows(b)
        self.assertEqual(sorted(rows), ["ercot-nodes-all-basis-p50", "ercot-nodes-storage-basis-p50"])
        t = raw("node_basis_summary")
        for cls in ("all", "storage"):
            r, g = rows[f"ercot-nodes-{cls}-basis-p50"], t[t["variable"] == f"dam_{cls}_basis_p50"].sort_values("ts_utc")
            self.assertEqual((r["status"], r["freq"], r["group"], r["unit"]), ("ok", "M", "power", "USD/MWh"))
            self.assertEqual((r["last"]["t"], r["last"]["v"]), (g["ts_utc"].iloc[-1][:10], round(float(g["value"].iloc[-1]), 4)))
            self.assertEqual(r["link"], {"href": "/cost-of-power", "words": "node view"})
            self.assertEqual(r["tags"], {"grid": "ERCOT", "market": "da", "scope": "all"})
            self.assertIn("less HB_HUBAVG's", r["basis"])


class TheAdders(OnTheFixture):
    def test_rtrdpa_drawn_and_the_ended_adder_not(self):
        b = self.bp.Board()
        self.bp.build_adders(b, self.holidays, lambda s: None)
        rows = self.rows(b)
        self.assertEqual(sorted(rows), ["ercot-system-rtrdpa"])
        r = rows["ercot-system-rtrdpa"]
        t = raw("ercot_rtm_price_adders")
        t = t[t["variable"] == "rtrdpa_mean"].copy()
        t["local"] = pd.to_datetime(t["ts_utc"], utc=True).dt.tz_convert("America/Chicago").dt.date
        full = t.groupby("local")["value"].agg(["mean", "size"])
        full = full[full["size"] == 24]
        self.assertEqual(r["last"]["t"], max(full.index).isoformat())
        self.assertEqual(r["last"]["v"], round(float(full["mean"].iloc[-1]), 4))
        self.assertEqual((r["tags"]["market"], r["code"], r["source"]), ("rt", "RTRDPA", self.bp.ADDER_SOURCE))
        self.assertIn("rtrdpa_mean", r["basis"])


class TheCapacityRows(unittest.TestCase):
    def test_one_row_an_auction(self):
        bp = builder()
        self.assertEqual([c[0] for c in bp.CAPACITY], ["capacity", "capacity|nyiso", "capacity|isone", "capacity|miso"])
        for key, label, grid, status, unit, note in bp.CAPACITY:
            self.assertIn(grid, label)
            self.assertIn(status, ("licensed", "paused"))
            self.assertIn("MISO" if grid == "MISO" else grid, note)
        with open(os.path.join(DERIVED, "board_page.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('for key, label, grid, status, unit, note in CAPACITY:', src)
        self.assertNotIn('"Capacity prices (PJM, NYISO, ISO-NE, MISO)"', src)


class ThePage(unittest.TestCase):
    def test_the_name_hover_carries_the_interval(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        script = ("const b = await import('./lib/board.ts');"
                  "process.stdout.write(JSON.stringify([b.nameTitle({ code: 'LZ_HOUSTON', basis: 'A daily mean.', source: 0 }, ['ERCOT']), b.nameTitle({}, [])]));")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), ["Code: LZ_HOUSTON\nInterval: A daily mean.\nSource: ERCOT", None])

    def test_the_link_is_drawn_and_does_not_open_the_workbench(self):
        with open(os.path.join(SITE, "components", "board", "BoardView.tsx"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("data-row-link={row.id}", src)
        self.assertIn("onClick={(e) => e.stopPropagation()} data-row-link", src)
        self.assertIn("title={nameTitle(row, file.sources)}", src)


if __name__ == "__main__":
    unittest.main()
