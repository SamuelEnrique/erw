"""Session 3889 (chain 227): the board's spark spreads, implied heat rates and Henry Hub's row are taken or kept together
by the scheduled refresh (warehouse/derived/page_keep.py, BOARD_TOGETHER).

On 12 and 13 November 2026 the daily run's board_tests step refused the runner's board: the runner kept the ERCOT hub's
day-ahead, spark and heat rows as they were (its histories are shorter) and took Henry Hub's row from the new build, so
the board's newest spark spread (22.2287) was no longer its hub less 7 x its gas (22.4387; tests 1118 and 1139), and
the whole board was put back as committed. A spread takes the newest gas day up to 4 days back, so a new gas day changes
spread values already held: such rows are one build's rows. No network, no warehouse table.
"""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import page_keep as pk  # noqa: E402


def row(rid, status="ok", t="2026-11-12", group="spark"):
    r = dict(id=rid, group=group, status=status, source=0)
    if status == "ok":
        r["last"] = dict(t=t, v=1.0)
    return r


def body(rows, mark):
    for r in rows:
        r["mark"] = mark
    return dict(groups=[dict(id="power"), dict(id="gas"), dict(id="spark")], sources=["src"], rows=rows)


GAS = "eia-henry-hub-spot"


class TheSetIsOneBuild(unittest.TestCase):
    def merge(self, old, new, n_old, n_new):
        return pk.merge_rows(old, new, lambda i: n_old.get(i), lambda i: n_new.get(i), lambda s: None, together=pk.board_together)

    def twelfth_of_november(self):
        """The runner's case: ERCOT's rows short in the new build, Henry Hub and the other hubs whole and newer."""
        ids = [("ercot-hb-hubavg-da", "power"), (GAS, "gas"), ("ercot-hb-hubavg-spark", "spark"), ("ercot-hb-hubavg-heat", "spark"),
               ("caiso-th-sp15-gen-apnd-da", "power"), ("caiso-th-sp15-gen-apnd-spark", "spark"), ("ercot-hb-hubavg-da-minus-rt", "power")]
        old = body([row(i, t="2026-11-11", group=g) for i, g in ids] + [row("miso-spark", t="2026-10-01")], "held")
        new = body([row(i, t="2026-11-12", group=g) for i, g in ids] + [row("miso-spark", status="paused")], "built")
        n_old = {i: 2867 for i, _ in ids}
        n_new = dict(n_old, **{"ercot-hb-hubavg-da": 78, "ercot-hb-hubavg-spark": 78, "ercot-hb-hubavg-heat": 78})
        return self.merge(old, new, n_old, n_new)

    def test_a_kept_spread_keeps_henry_hub_and_every_other_spread(self):
        rows, _, kept, taken = self.twelfth_of_november()
        by = {r["id"]: r["mark"] for r in rows}
        for rid in (GAS, "ercot-hb-hubavg-spark", "ercot-hb-hubavg-heat", "caiso-th-sp15-gen-apnd-spark"):
            self.assertEqual(by[rid], "held", rid)
        why = dict(kept)
        self.assertIn("one build's rows together", why[GAS])
        self.assertIn("one build's rows together", why["caiso-th-sp15-gen-apnd-spark"])
        self.assertEqual(why["ercot-hb-hubavg-spark"], "the new build's history is shorter (78 points against 2867)")

    def test_the_hubs_prices_and_same_day_rows_are_still_chosen_alone(self):
        rows, _, kept, taken = self.twelfth_of_november()
        by = {r["id"]: r["mark"] for r in rows}
        self.assertEqual(by["caiso-th-sp15-gen-apnd-da"], "built")
        self.assertEqual(by["ercot-hb-hubavg-da-minus-rt"], "built")
        self.assertEqual(by["ercot-hb-hubavg-da"], "held")       # its own shorter history, as before
        self.assertIn("caiso-th-sp15-gen-apnd-da", taken)

    def test_a_pause_is_still_taken(self):
        rows, _, kept, taken = self.twelfth_of_november()
        self.assertEqual({r["id"]: r for r in rows}["miso-spark"]["status"], "paused")
        self.assertIn("miso-spark", taken)

    def test_a_whole_new_build_is_taken_whole(self):
        ids = [(GAS, "gas"), ("ercot-hb-hubavg-spark", "spark"), ("ercot-hb-hubavg-heat", "spark")]
        old = body([row(i, t="2026-11-11", group=g) for i, g in ids], "held")
        new = body([row(i, t="2026-11-12", group=g) for i, g in ids], "built")
        n = {i: 2867 for i, _ in ids}
        rows, _, kept, taken = self.merge(old, new, n, n)
        self.assertEqual({r["mark"] for r in rows}, {"built"})
        self.assertEqual(kept, [])

    def test_a_kept_henry_hub_keeps_the_spreads(self):
        ids = [(GAS, "gas"), ("ercot-hb-hubavg-spark", "spark")]
        old = body([row(i, t="2026-11-12", group=g) for i, g in ids], "held")
        new = body([row(GAS, t="2026-11-10", group="gas"), row("ercot-hb-hubavg-spark", t="2026-11-12")], "built")
        n = {i: 2867 for i, _ in ids}
        rows, _, kept, taken = self.merge(old, new, n, n)
        self.assertEqual({r["id"]: r["mark"] for r in rows}, {GAS: "held", "ercot-hb-hubavg-spark": "held"})

    def test_the_supply_page_has_no_set(self):
        old = body([row(GAS, t="2026-11-11", group="gas"), row("ercot-hb-hubavg-spark", t="2026-11-11")], "held")
        new = body([row(GAS, t="2026-11-12", group="gas"), row("ercot-hb-hubavg-spark", t="2026-11-12")], "built")
        rows, _, kept, taken = pk.merge_rows(old, new, lambda i: {"ercot-hb-hubavg-spark": 100}.get(i, 10),
                                             lambda i: {"ercot-hb-hubavg-spark": 10}.get(i, 10), lambda s: None)
        self.assertEqual({r["id"]: r["mark"] for r in rows}, {GAS: "built", "ercot-hb-hubavg-spark": "held"})

    def test_the_set_is_named_once(self):
        sets = pk.board_together(["eia-henry-hub-spot", "ercot-hb-hubavg-spark", "nyiso-n-y-c-heat", "ercot-hb-hubavg-dark",
                                  "ercot-hb-hubavg-da"])
        self.assertEqual(sets, [{"eia-henry-hub-spot", "ercot-hb-hubavg-spark", "nyiso-n-y-c-heat"}])


class TheNetworksDemand(unittest.TestCase):
    """The Grid tool's replication (replication/grid/replicate.py network) draws each grid's demand in the hour shown as
    the page's demandAt does: on 13 November 2026 the daily run's snapshot held demand at the hour shown, the page drew
    six demand figures the replication did not, test 3703 failed in the push guard and the daily commit was refused.
    Here the committed snapshot is given demand at its hour shown, both ways the page keys it, and every figure of the
    page's own code (node) must be in the replication and agree."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        import json
        import shutil
        import tempfile
        snap_path = os.path.join(ROOT, "site", "data", "grid_network.json")
        if not os.path.exists(snap_path) or shutil.which("node") is None:
            raise unittest.SkipTest("the snapshot or node is not here")
        rep = os.path.join(ROOT, "replication", "grid")

        def module(name, file):
            spec = importlib.util.spec_from_file_location(name, os.path.join(rep, file))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
        cls.r, cls.b = module("replicate_grid_3889", "replicate.py"), module("figures_grid_3889", "figures_of_the_page.py")
        with open(os.path.join(rep, "assumptions.json"), encoding="utf-8") as f:
            cls.a = json.load(f)
        with open(snap_path, encoding="utf-8") as f:
            snap = json.load(f)
        hour = cls.r.network(snap, {}, cls.a)[0]
        for n in snap["nodes"]:
            if n["id"] in ("ERCO", "PJM"):        # the daily run's way: the node's demand at the hour shown
                n.update(demand_mw=50000.5, demand_ts=hour, demand_src=None)
                n.pop("demand_recent", None)
            elif n["id"] == "CISO":               # the hourly refresh's way: its recent demand, keyed netsnap|
                n.update(demand_src="hourly", demand_recent={hour: 25000.0}, demand_ts=hour, demand_mw=25000.0)
        cls.tmp = tempfile.mkdtemp(prefix="erw3889_")
        cls.path = os.path.join(cls.tmp, "grid_network.json")
        with open(cls.path, "w", encoding="utf-8") as f:
            json.dump(snap, f)
        cls.hour = hour
        cls.page = cls.b.network_group(cls.path, os.path.join(ROOT, "no-tables-here"))
        cls.mine = cls.r.network(snap, {}, cls.a)[3]

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_page_draws_the_demand_both_ways(self):
        checks = {f["check"] for f in self.page["figures"]}
        self.assertIn(f"series|eia930_all_demand|eia930:ERCO|demand_mw|{self.hour}", checks)
        self.assertIn(f"netsnap|CISO|demand_mw|{self.hour}", checks)

    def test_every_figure_of_the_page_is_replicated_and_agrees(self):
        figs = [f for f in self.page["figures"] if f["tab"] in ("network", "gravity")]
        self.assertEqual([f["check"] for f in figs if f["check"] not in self.mine], [])
        self.assertEqual([f["check"] for f in figs if abs(self.mine[f["check"]] - f["raw"]) > 1e-9], [])


if __name__ == "__main__":
    unittest.main()
