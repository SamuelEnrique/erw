"""Session 93: the network, version 3 (replay, a shareable address, prices, trace the power), in review.

Energy Research Warehouse (ERW). The builder of the replay files (warehouse/derived/network_daily.py) on rows made
here and on the files as built; the parts of version 3 with no drawing in them (site/lib/networkV3.ts), run by node; and
that the live page passes nothing of it. The four additions in a real browser are site/scripts/check-network-v3.mjs,
which runs here when ERW_SITE_URL names a built site being served.

    python -m unittest tests.test_session93 -v
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import network_daily as nd  # noqa: E402

NET = os.path.join(SITE, "public", "network")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheReplayFiles(unittest.TestCase):
    def flows(self, rows):
        return pd.DataFrame([dict(fr=a, to=b, day=d, v=v, bad=bad) for a, b, d, v, bad in rows])

    def test_a_day_is_23_24_or_25_hours(self):
        self.assertEqual([nd.day_hours(d) for d in ("2021-02-15", "2021-03-14", "2021-11-07", "2024-02-29")], [24, 23, 25, 24])

    def test_a_pair_is_counted_once_and_a_flow_is_the_days_average_mw(self):
        f = self.flows([
            ("AAA", "BBB", "2021-01-01", 2400.0, False),    # the first by code reports: used as it is
            ("BBB", "AAA", "2021-01-01", -9999.0, False),   # the other side's report of the same day is not used
            ("BBB", "AAA", "2021-01-02", -480.0, False),    # only the other side reports: its sign flipped
            ("AAA", "BBB", "2021-01-04", 99999.0, True),    # screened out: blank, never drawn
            ("AAA", "BBB", "2021-03-14", 2300.0, False),    # a 23-hour day
        ])
        ci = pd.DataFrame([dict(ba="AAA", day="2021-01-01", value="412.345")])
        y = nd.build_year(2021, f, {"AAA", "BBB"}, ci, {"AAA": {"2021-01-02": 31.5}}, "2021-03-14")
        self.assertEqual(y["days"][0], "2021-01-01")
        self.assertEqual(y["days"][-1], "2021-03-14")
        self.assertEqual(len(y["links"]), 1)
        link = y["links"][0]
        self.assertEqual((link["a"], link["b"]), ("AAA", "BBB"))
        self.assertEqual(len(link["mw"]), len(y["days"]))
        self.assertEqual(link["mw"][:4], [100.0, 20.0, None, None])
        self.assertEqual(link["mw"][-1], 100.0)   # 2,300 MWh over 23 hours
        self.assertEqual(y["missing"], {"pair_days": len(y["days"]) - 4, "pair_days_from_other_side": 1, "pair_days_screened": 1, "demand_days_held": 0,
                                        "pair_days_confirmed": 0, "thin_days": 0})   # session 124: the days kept, and the days that hold few pairs   # session 109: the count of days with demand; none given here
        self.assertEqual(y["intensity"]["AAA"][0], 412.35)
        self.assertIsNone(y["intensity"]["AAA"][1])
        self.assertEqual(y["hub_prices"]["AAA"][1], 31.5)
        self.assertNotIn("BBB", y["hub_prices"])
        self.assertEqual(y["frame"], "day")

    def test_a_days_price_is_a_mean_only_when_every_hour_is_held(self):
        whole = pd.Series(range(24), index=pd.date_range("2021-06-01", periods=24, freq="h", tz="America/New_York").tz_convert("UTC"), dtype=float)
        short = pd.Series(range(20), index=pd.date_range("2021-06-02", periods=20, freq="h", tz="America/New_York").tz_convert("UTC"), dtype=float)
        p = nd.daily_prices({"ERCO": pd.concat([whole, short]), "NONE": pd.Series(dtype=float)})
        self.assertEqual(p, {"ERCO": {"2021-06-01": 11.5}})

    @unittest.skipUnless(os.path.exists(os.path.join(NET, "daily_index.json")), "the replay files are not built")
    def test_the_files_as_built(self):
        index = json.load(open(os.path.join(NET, "daily_index.json"), encoding="utf-8"))
        self.assertEqual(index["first"], "2019-01-01")
        self.assertEqual(list(index["years"]), [str(y) for y in range(2019, int(index["last"][:4]) + 1)])
        nodes = {n["id"] for n in json.load(open(os.path.join(SITE, "data", "grid_network.json"), encoding="utf-8"))["nodes"]}
        for y, meta in index["years"].items():
            f = json.load(open(os.path.join(NET, f"daily_{y}.json"), encoding="utf-8"))
            self.assertEqual(f["days"][0], f"{y}-01-01")
            self.assertEqual(len(f["days"]), meta["days"])
            self.assertEqual(len(set(f["days"])), len(f["days"]))
            for link in f["links"]:
                self.assertEqual(len(link["mw"]), len(f["days"]), f"{y} {link['a']}-{link['b']}")
                self.assertLess(link["a"], link["b"])
                self.assertTrue(link["a"] in nodes and link["b"] in nodes)
            for arr in list(f["intensity"].values()) + list(f["hub_prices"].values()):
                self.assertEqual(len(arr), len(f["days"]))
            self.assertNotIn("PJM", f["hub_prices"], "PJM's prices are internal")
            self.assertLess(os.path.getsize(os.path.join(NET, f"daily_{y}.json")), 600_000)
        self.assertEqual(json.load(open(os.path.join(NET, f"daily_{index['last'][:4]}.json"), encoding="utf-8"))["days"][-1], index["last"])

    @unittest.skipUnless(os.path.exists(os.path.join(ROOT, "warehouse", "output", "eia930_daily_interchange.csv")) and os.path.exists(os.path.join(NET, "daily_2021.json")),
                         "the daily interchange table or the replay files are not on this machine")
    def test_a_frame_is_the_tables_row(self):
        t = pd.read_csv(os.path.join(ROOT, "warehouse", "output", "eia930_daily_interchange.csv"), comment="#", usecols=["entity", "ts_utc", "value"], dtype=str)
        f = json.load(open(os.path.join(NET, "daily_2021.json"), encoding="utf-8"))
        i = f["days"].index("2021-02-15")
        for a, b in (("ERCO", "SWPP"), ("CISO", "BPAT"), ("MISO", "PJM")):
            p, q = sorted((a, b))
            row = t[(t["entity"] == f"eia930:{p}-{q}") & (t["ts_utc"].str[:10] == "2021-02-15")]
            link = [x for x in f["links"] if (x["a"], x["b"]) == (p, q)][0]
            self.assertEqual(len(row), 1, f"{p}-{q}")
            self.assertAlmostEqual(link["mw"][i], round(float(row["value"].iloc[0]) / 24, 1), places=1, msg=f"{p}-{q}")


class TheModel(unittest.TestCase):
    def test_the_address_holds_a_view_and_only_a_view(self):
        d = node("import * as n from './lib/networkV3.ts';"
                 "const s = { view: 'day', t: '2021-02-15', grid: 'ERCO', batteries: false, prices: true, trace: true };"
                 "const q = n.sharedQuery(s);"
                 "console.log(JSON.stringify({ q, back: n.parseShared(q), plain: n.sharedQuery(n.DEFAULT), empty: n.parseShared(''),"
                 " story: n.parseShared('?view=uri_2021&t=2021-02-15T12:00:00Z&batteries=1'),"
                 " odd: n.parseShared('?view=nonsense&t=yesterday&grid=%3Cscript%3E&prices=yes&trace=true'),"
                 " dayNoDate: n.parseShared('?view=day&t=2021-02-15T00:00:00Z'), hourInLive: n.parseShared('?t=2026-10-01T05:00:00Z&grid=CISO') }));")
        self.assertEqual(d["q"], "?view=day&t=2021-02-15&grid=ERCO&prices=1&trace=1")
        self.assertEqual(d["back"], {"view": "day", "t": "2021-02-15", "grid": "ERCO", "batteries": False, "prices": True, "trace": True})
        self.assertEqual(d["plain"], "")
        default = {"view": "live", "t": None, "grid": None, "batteries": False, "prices": False, "trace": False}
        self.assertEqual(d["empty"], default)
        self.assertEqual(d["odd"], default)
        self.assertEqual(d["dayNoDate"], default)
        self.assertEqual(d["story"], {**default, "view": "uri_2021", "t": "2021-02-15T12:00:00Z", "batteries": True})
        self.assertEqual(d["hourInLive"], {**default, "t": "2026-10-01T05:00:00Z", "grid": "CISO"})

    def test_a_day_is_held_to_the_replays_range_and_has_its_hours(self):
        d = node("import * as n from './lib/networkV3.ts'; const ix = { first: '2019-01-01', last: '2026-09-30' };"
                 "console.log(JSON.stringify({ a: n.clampDay('2021-02-15', ix), b: n.clampDay('2018-06-01', ix), c: n.clampDay('2030-01-01', ix), d: n.clampDay('not a day', ix), e: n.clampDay('2021-13-45', ix),"
                 " h: ['2021-02-15', '2021-03-14', '2021-11-07', '2024-02-29'].map(n.easternHours), f: n.dayFrame('2021-02-15') }));")
        self.assertEqual((d["a"], d["b"], d["c"], d["d"], d["e"]), ("2021-02-15", "2019-01-01", "2026-09-30", None, None))
        self.assertEqual(d["h"], [24, 23, 25, 24])
        self.assertEqual(d["h"], [nd.day_hours(x) for x in ("2021-02-15", "2021-03-14", "2021-11-07", "2024-02-29")])
        self.assertEqual(d["f"], "2021-02-15T12:00:00Z")

    def test_the_rings_weight_follows_the_price(self):
        d = node("import { priceWeight as w } from './lib/networkV3.ts';"
                 "console.log(JSON.stringify([w(null, 100), w(0, 100), w(-20, 100), w(25, 100), w(100, 100), w(400, 100), w(50, 0)]));")
        self.assertEqual(d, [None, 0, 0, 0.5, 1, 1, 0])

    def test_trace_the_power_two_steps(self):
        # G takes 300 from A and 100 from B over two frames, and sends 50 to C; A takes 200 from D and 100 from E and sends 300 to G
        d = node("import { trace, netInto } from './lib/networkV3.ts';"
                 "const links = [{ a: 'A', b: 'G', mw: [100, 200] }, { a: 'B', b: 'G', mw: [100, null] }, { a: 'C', b: 'G', mw: [-25, -25] },"
                 " { a: 'A', b: 'D', mw: [-100, -100] }, { a: 'A', b: 'E', mw: [-50, -50] }, { a: 'B', b: 'F', mw: [10, 10] }];"
                 "console.log(JSON.stringify({ t: trace(links, 0, 2, 'G'), day: trace(links, 0, 2, 'G', () => 24), one: trace(links, 1, 2, 'G'), none: trace(links, 0, 2, 'F'),"
                 " into: [...netInto(links, 0, 2, 'G', () => 1)] }));")
        t = d["t"]
        self.assertEqual((t["inMwh"], t["outMwh"], t["frames"]), (400, 50, 2))
        self.assertEqual([(r["id"], r["mwh"], r["share"]) for r in t["rows"]], [("A", 300, 75), ("B", 100, 25)])
        self.assertEqual(sum(r["share"] for r in t["rows"]), 100)
        a = t["rows"][0]
        self.assertEqual([(v["id"], v["mwh"]) for v in a["via"]], [("D", 200), ("E", 100)])
        self.assertAlmostEqual(sum(v["share"] for v in a["via"]), 100)
        self.assertEqual(t["rows"][1]["via"], [])           # B sends to F and takes from nobody
        self.assertEqual(t["rows"][1]["frames"], 1)          # one of its two frames was not reported
        for r in t["rows"]:
            self.assertNotIn("G", [v["id"] for v in r["via"]], "a grid is never its supplier's supplier")
        self.assertEqual(d["day"]["inMwh"], 400 * 24)        # a day's frame is its MW times its hours
        self.assertEqual([r["share"] for r in d["day"]["rows"]], [75, 25])
        self.assertEqual([(r["id"], r["mwh"]) for r in d["one"]["rows"]], [("A", 200)])
        # F takes from B, which takes from nobody: one supplier, nothing behind it
        self.assertEqual([(r["id"], r["mwh"], r["via"]) for r in d["none"]["rows"]], [("B", 20, [])])
        self.assertEqual(dict((k, v["mwh"]) for k, v in d["into"]), {"A": 300, "B": 100, "C": -50})


class TheLivePageIsAsItWas(unittest.TestCase):
    def test_the_live_page_passes_nothing_of_version_3(self):
        # session 168 (the owner's instruction of 8 October 2026): version 3 is the network page. The page that passed no
        # version 3 is kept, unrouted, in app/_retired/network-original; version 3's page stands at /network
        page = src("site", "app", "_retired", "network-original", "page.tsx")
        self.assertIn("<Network snap={snap} supply={supply} live={extras} />", page)
        self.assertNotIn("v3=", page)
        self.assertIn("pickSnapshot(await fetchHourly(HOURLY), committed)", page)
        v3 = src("site", "app", "network", "page.tsx")
        self.assertIn("<Network snap={snap} supply={supply} live={extras} v3={{ index, complete }} />", v3)   # session 124
        self.assertFalse(os.path.exists(os.path.join(SITE, "app", "network", "v3", "page.tsx")))
        self.assertIn('{ source: "/network/v3", destination: "/network", permanent: true }', src("site", "next.config.ts"))
        d = node("import { statusOf } from './lib/release.ts'; console.log(JSON.stringify([statusOf('/network'), statusOf('/network/v3')]));")
        # session 166 (the owner's instruction of 8 October 2026): the network page is in review; no page is live
        self.assertEqual(d, ["review", "review"])
        self.assertIn('"/network": "review"', src("site", "lib", "release.ts"))
        self.assertIn('"/network/v3": "review"', src("site", "lib", "release.ts"))   # its line stays: an address typed by hand never reads as a page with no status

    def test_everything_new_in_the_component_is_behind_the_prop(self):
        c = src("site", "app", "network", "Network.tsx")
        self.assertIn("v3?: { index: DailyIndex; complete?: Complete }", c)   # session 124: the newest complete hour comes with the prop
        # the controls, the address, the trace and the scene hook
        for gated in ("{v3 ? (\n          <span className=\"flex flex-wrap items-center gap-2\" data-replay=\"1\">", "{v3 ? (\n          <button type=\"button\" role=\"switch\" aria-checked={pricesOn}",
                      "{v3 ? (\n              <div className=\"mt-2 border-t border-rule pt-2\" data-trace=", "if (!v3) return;", "if (!v3 || !restored || playing) return;", "if (v3) (el as unknown as { __erwGraph?: unknown }).__erwGraph = g;"):
            self.assertIn(gated, c)
        # the price ring needs the switch, and only version 3 has the switch
        # session 124: a price is read through priceOf, which is the view's own price unless v3 is on and the hub is a paused publisher's
        self.assertIn("const w = pricesOn && n.id !== \"PJM\" ? priceWeight(priceOf(view, !!v3, n.id, hour), priceMax) : null;", c)
        self.assertEqual(c.count("setPricesOn("), 2)   # the switch and the restore from an address, both v3's
        # the words of the live page's panel and controls are the ones they were
        for kept in ("Watch:", "Live now", "California&apos;s evening", "Texas during Uri", "The June 2025 heat", "Batteries: {batteriesOn ? \"on\" : \"off\"}", "Who is supplying it, largest first",
                     "backgroundColor(\"#FBF8F2\")", "The color updates daily", ".nodeLabel((n: object) => (n as NetNode).name)"):
            self.assertIn(kept, c)

    def test_the_pages_reads_moved_and_did_not_change(self):
        data = src("site", "app", "network", "data.ts")
        for fn in ("export async function liveExtras(snap: Snapshot): Promise<LiveExtras>", "export async function supplyRows(ba: string): Promise<SupplyRow[]>", "export const ISO_BA"):
            self.assertIn(fn, data)
        self.assertIn('import { ISO_BA, liveExtras, supplyRows } from "./data";', src("site", "app", "network", "page.tsx"))

    def test_in_a_real_browser_where_a_built_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL names no served site (or node is absent): node site/scripts/check-network-v3.mjs <base>")
        r = subprocess.run([exe, "scripts/check-network-v3.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-2500:])
        self.assertNotIn("NOT PROVEN", r.stdout)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("tests/test_session93.py", "warehouse/derived/network_daily.py", "site/lib/networkV3.ts", "site/app/network/page.tsx", "site/app/network/data.ts",
                    "site/app/network/Network.tsx", "site/scripts/check-network-v3.mjs", "site/scripts/browser.mjs", "site/public/network/daily_index.json"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
