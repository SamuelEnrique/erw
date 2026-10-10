"""Session 183: What a generator earns, correctness (/cost-of-power/seller).

  the fix      choosing another hub or zone prices everything the model shows (revenue, the months, debt coverage, the
               stress days), not only the capture price and the contract: the page reads the model solved again with
               that hub's own price (site/data/seller/hubs, warehouse/derived/merchant_hubs.py), and writes the hub
               and the market beside the figure; the main hub keeps the page's snapshot
  one model    the builder of the hub files, run at each grid's main hub, is the snapshot month for month; a hub's
               months, hourly prices and Henry Hub are one hub's; at a hub the model's capture price is the capture
               file's to within the difference of the two weights (site/scripts/test-seller-hubs.mjs, run here)
  the note     docs/methods/generator_earns_algorithm.md states the default case's figures as the page's own library
               gives them, holds no placeholder and no em dash, and is a page in review
  nothing new  the model's own function is unchanged when no hub is given; the page stays in review
On the site's own files, which hold real rows only. No network and no table: a clean copy runs all of it.
"""
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUBS = os.path.join(ROOT, "site", "data", "seller", "hubs")
NOTE = os.path.join(ROOT, "docs", "methods", "generator_earns_algorithm.md")
EM_DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def node(args):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe] + args, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=600)
    if r.returncode != 0 and ("ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    return r


class TheHubFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load("site", "data", "seller", "hubs", "index.json")
        cls.capture = load("site", "data", "seller", "capture.json")
        cls.snap = load("site", "data", "merchant_snapshot.json")

    def test_every_public_grid_and_every_hub_but_the_main_one(self):
        self.assertEqual(sorted(self.index["grids"]), sorted(self.capture["grids"]))
        for iso, cg in self.capture["grids"].items():
            want = sorted(h["id"] for h in cg["hubs"] if h["id"] != cg["main"])
            self.assertEqual(sorted(self.index["grids"][iso]["hubs"]), want, iso)
            self.assertEqual(self.index["grids"][iso]["main"], cg["main"])

    def test_no_paused_or_licensed_grid(self):
        self.assertFalse({"miso", "pjm"} & set(self.index["grids"]))
        for g in self.index["grids"].values():
            for e in g["hubs"].values():
                self.assertFalse(any("miso" in t or "pjm" in t for t in e["tables"]), e["tables"])

    def test_each_file_is_there_and_is_its_hub(self):
        for iso, g in self.index["grids"].items():
            grid = load("site", "data", "seller", "hubs", *g["file"].split("/"))
            self.assertEqual(len(grid["hh"]), grid["hours"])
            names = set()
            for node_id, e in g["hubs"].items():
                self.assertNotIn(e["file"], names)
                names.add(e["file"])
                path = os.path.join(HUBS, *e["file"].split("/"))
                self.assertTrue(os.path.exists(path), e["file"])
                self.assertLess(os.path.getsize(path), 2_000_000, e["file"])
                self.assertIn(e["market"], ("rt", "da"))
            one = next(iter(g["hubs"].items()))
            hub = load("site", "data", "seller", "hubs", *one[1]["file"].split("/"))
            self.assertEqual(hub["id"], one[0])
            self.assertEqual(len(hub["price"]), grid["hours"])
            self.assertTrue(set(hub["months"]) <= set(grid["months"]))

    def test_the_builder_at_the_main_hub_is_the_snapshot(self):
        # written by the builder itself: its own months at the main hub, at real-time prices, beside the page's snapshot
        # A month is compared when both hold the same hours of it. Solar, wind and the batteries are equal to the
        # snapshot's rounding. The peaker differs in the months whose last days gained a Henry Hub price after the
        # snapshot was built (it took the last trading day's until then). New York's main hub is read from another
        # real-time table here (the zone history, hourly) than in the snapshot (the hub history, 15 minutes), so its
        # months are not held to the snapshot: the note says so, and the page keeps the snapshot at every main hub.
        self.assertEqual(self.index["snapshot_built"], self.snap["built"])
        for iso, g in self.index["grids"].items():
            self.assertTrue(g["check"], iso)
            if iso == "nyiso":
                self.assertEqual(g["check"]["solar"]["months"], 0)  # EIA-930 itemizes no solar for New York
                self.assertNotEqual(g["check_tables"], ["iso_hub_prices_history"])
                continue
            for asset, c in g["check"].items():
                self.assertGreaterEqual(c["months"], 12, (iso, asset))
                if asset == "peaker":
                    self.assertLessEqual(c["max_share"], 0.01, (iso, asset, c))
                else:
                    self.assertLessEqual(c["max_abs_usd_per_mw"], 0.0001, (iso, asset, c))

    def test_the_stress_days_are_ercots_alone(self):
        for iso, g in self.index["grids"].items():
            e = next(iter(g["hubs"].values()))
            hub = load("site", "data", "seller", "hubs", *e["file"].split("/"))
            self.assertEqual("stress" in hub, iso == "ercot", iso)
        west = load("site", "data", "seller", "hubs", "ercot", "hb_west.json")
        self.assertEqual(sorted(west["stress"]), ["elliott_2022", "ercot_heat_2023", "uri_2021"])
        self.assertEqual(west["market"], "rt")

    def test_the_page_library_on_the_files(self):
        r = node(["--import", "./scripts/alias-register.mjs", "scripts/test-seller-hubs.mjs"])
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("ok: ", r.stdout)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src("site", "app", "cost-of-power", "seller", "page.tsx")

    def test_everything_the_model_shows_is_priced_at_the_hub_chosen(self):
        p = self.page
        for want in ("const ms = months(priced, x);", "const st = stress(priced, x);", "const ms1 = months(priced, perMw);", "sentence({ grid: iso, asset: x.asset }, s, atHub ? at : undefined)"):
            self.assertIn(want, p)
        # nothing of the model is read from the main hub's snapshot but the battery beside the plant, which says so
        self.assertEqual(len(re.findall(r"months\(snap,", p)), 1)
        self.assertIn("const ms1Main = atHub ? months(snap, perMw) : ms1;", p)
        self.assertIn("ms1Main.find((p) => p.m === r.m)", p)
        self.assertNotIn("stress(snap", p)
        self.assertIn('data-hybrid-at="1"', p)

    def test_a_figure_never_stands_under_a_hub_it_was_not_priced_at(self):
        p = self.page
        self.assertIn('const at = atHub ? `${hubAt(hub.id)} (${HB.marketWords(he!.market)} prices)` : g.at;', p)
        self.assertIn('priced at <span data-stat="priced_at">{at}</span>', p)
        self.assertIn('data-hub-model="none"', p)
        self.assertIn("const key = atHub ? HB.hubKey(inputsKey(x), hub.id, he!.market) : inputsKey(x);", p)

    def test_the_hub_file_is_named_by_the_index_never_by_the_address(self):
        p = self.page
        self.assertIn("HUBS.grids[iso]?.hubs[hub.id]", p)
        self.assertIn("hubFile<HB.HubFile>(he.file)", p)
        self.assertNotRegex(p, r"hubFile<[^>]+>\(q\.")
        self.assertIn('"/cost-of-power/seller": ["./data/seller/hubs/**/*.json"]', src("site", "next.config.ts"))

    def test_the_note_and_the_downloads_are_linked(self):
        p = self.page
        self.assertIn('const ALGORITHM = "/data/methods/generator_earns_algorithm";', p)
        self.assertIn("Every number, step by step", p)
        for f in ("erw_2026_generator_hourly.csv", "erw_2026_generator_replication.do", "erw_2026_generator_replication.py"):
            self.assertIn(f"/seller/{f}", p)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "public", "seller", f)), f)

    def test_the_page_and_the_note_stay_in_review(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power/seller": "review"', rel)
        self.assertIn('"/data/methods/generator_earns_algorithm": "review"', rel)

    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (("site", "app", "cost-of-power", "seller", "page.tsx"), ("site", "lib", "sellerhubs.ts"), ("site", "lib", "seller2.ts"), ("site", "scripts", "test-seller-hubs.mjs"),
                      ("site", "scripts", "check-seller-face.mjs"), ("warehouse", "derived", "merchant_hubs.py"), ("warehouse", "derived", "merchant_revenue.py"),
                      ("docs", "methods", "generator_earns_algorithm.md"), ("tests", "test_session183.py")):
            self.assertNotIn(EM_DASH, src(*parts), "/".join(parts))


class TheModelIsUnchanged(unittest.TestCase):
    def test_the_models_function_takes_a_hub_only_when_given_one(self):
        for p in (os.path.join(ROOT, "warehouse", "derived"), os.path.join(ROOT, "warehouse", "connectors")):
            if p not in sys.path:
                sys.path.insert(0, p)
        try:
            import merchant_revenue as mr
        except ImportError as e:
            raise unittest.SkipTest(f"the builder cannot be imported here: {e}")
        sig = inspect.signature(mr.build_iso)
        self.assertEqual(list(sig.parameters)[:5], ["iso", "gens", "hh", "log", "left"])
        for k in ("price", "table", "fuel"):
            self.assertIsNone(sig.parameters[k].default)
        body = inspect.getsource(mr.build_iso)
        self.assertIn('if price is None:\n        df, table = cp.prices_of(iso, "rtm", log)\n        price = cp.hourly(df)', body)

    def test_the_hub_builder_solves_with_the_models_own_function(self):
        s = src("warehouse", "derived", "merchant_hubs.py")
        self.assertIn("mr.build_iso(iso, gens, hh, log, [], price=price", s)
        self.assertIn("cq.hourly_side(e, SIDE[mk])", s)
        self.assertNotIn("def battery_day", s)
        self.assertNotIn("requests", s)


class TheNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "generator_earns_algorithm.md")
        cls.snap = load("site", "data", "merchant_snapshot.json")
        cls.capture = load("site", "data", "seller", "capture.json")

    def test_it_holds_no_placeholder(self):
        for word in ("HUB_FIGURES", "REPLICATION\n", "TBD", "TODO"):
            self.assertNotIn(word, self.note)
        for head in ("## 1. The order of computation", "## 4. Every number on the page", "## 5. Another hub or zone", "## 6. Edge cases", "## 8. The replication", "## 10. What is left"):
            self.assertIn(head, self.note)

    def test_the_default_cases_figures_are_the_snapshots(self):
        months = self.snap["isos"]["ercot"]["months"]
        twelve = [f"2025-{m:02d}" for m in (10, 11, 12)] + [f"2026-{m:02d}" for m in range(1, 10)]
        kw = sum(months[m]["solar"]["revenue_per_mw"] for m in twelve) / 1000
        self.assertIn(f"USD {kw:.2f} per kW", self.note)
        three = sum(months[f"{y}-{m:02d}"]["solar"]["revenue_per_mw"] for y in (2023, 2024, 2025) for m in range(1, 13)) / 3000
        self.assertIn(f"{three:.2f}", self.note)
        ds = round(1375 * 1000 * 100 * 0.6 * (0.08 / (1 - 1.08 ** -35)))
        self.assertIn(f"{ds:,}", self.note)
        cover = (kw * 1000 * 100 - 12.5 * 1000 * 100) / ds
        self.assertIn(f"= {cover:.2f}", self.note)

    def test_the_default_cases_price_received_is_the_capture_files(self):
        hub = next(h for h in self.capture["grids"]["ercot"]["hubs"] if h["id"] == "HB_HUBAVG")
        twelve = [f"2025-{m:02d}" for m in (10, 11, 12)] + [f"2026-{m:02d}" for m in range(1, 10)]
        recs = [hub["rt"]["solar"][m] for m in twelve]
        price = sum(r[4] for r in recs) / sum(r[3] for r in recs)
        flat = sum(r[2] for r in recs) / sum(r[0] for r in recs)
        self.assertIn(f"{price:.2f} against {flat:.2f}", self.note)

    def test_the_route_check_reads_the_note_and_a_page_at_another_hub(self):
        s = src("site", "scripts", "check-routes.mjs")
        self.assertIn('"/data/methods/generator_earns_algorithm"', s)
        self.assertIn("hub=HB_WEST", s)


if __name__ == "__main__":
    unittest.main()
