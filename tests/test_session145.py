"""Session 145: what a generator earns, one page (/cost-of-power/seller), and the capture price.

On a saved real week (tests/fixtures/session145: the price rows of ERCOT's West hub for the week from 1 June 2026, real
time and day-ahead, and the grid's hourly solar and wind generation of the same hours, cut from the warehouse's tables
by warehouse/derived/capture_price.py --fixture-dir) and on the site's own file (site/data/seller/capture.json):

  the generation-weighted price, by hand, equals the builder's month sums;
  a plant that generates the same in every hour captures the flat average exactly;
  the premium in dollars and in percent agree;
  a month under 95 percent of its hours writes no figure;
  MISO has no number;
  the builder's arithmetic and the page's (site/lib/capture.ts) agree on every figure of the file;
  the contract arithmetic equals the battery page's, and the combined figure is the sum of its two parts
    (site/scripts/test-capture.mjs, run here);
  one page: version 2's address redirects, its file is retired, the page face holds no method prose and no em dash,
    and the live battery page's files are not touched.
No network.
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures", "session145")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def rows(name):
    with open(os.path.join(FIX, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def node(args, stdin=None):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe] + args, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300, input=stdin)
    if r.returncode != 0 and ("ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    return r


def week():
    """The real week by hand, with no library: each hour's real-time price (the mean of its four quarter hours, only
    when all four are held), its day-ahead price, and the grid's solar and wind generation."""
    quarters, da = {}, {}
    for r in rows("prices_week.csv"):
        if r["side"] == "rtm":
            quarters.setdefault(r["ts_utc"][:13] + ":00:00Z", []).append(float(r["value"]))
        else:
            da[r["ts_utc"]] = float(r["value"])
    rt = {h: sum(q) / 4 for h, q in quarters.items() if len(q) == 4}
    gen = {r["ts_utc"]: {"solar": float(r["solar"]), "wind": float(r["wind"])} for r in rows("generation_week.csv")}
    return rt, da, gen


class TheCapturePrice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pandas as pd
            import capture_price as cp
        except ImportError as e:
            raise unittest.SkipTest(f"the builder's libraries are not on this machine: {e}")
        cls.pd, cls.cp = pd, cp
        cls.rt, cls.da, cls.gen = week()

    def series(self, d):
        return self.pd.Series(list(d.values()), index=self.pd.to_datetime(list(d.keys()), utc=True)).sort_index()

    def test_the_week_is_whole(self):
        self.assertEqual((len(self.rt), len(self.da), len(self.gen)), (168, 168, 168))

    def test_the_generation_weighted_price_by_hand(self):
        pc = sys.modules["price_compare"]
        raw = [r for r in rows("prices_week.csv") if r["side"] == "rtm"]
        quarter = self.pd.Series([float(r["value"]) for r in raw], index=self.pd.to_datetime([r["ts_utc"] for r in raw], utc=True)).sort_index()
        hourly = pc.hourly(quarter, "PT15M")                       # the reader's own rule for an hour of real time
        self.assertEqual(len(hourly), 168)
        for name, price in (("rt", hourly), ("da", self.series(self.da))):
            by_hand_price = self.rt if name == "rt" else self.da
            for fuel in ("solar", "wind"):
                g = self.series({h: v[fuel] for h, v in self.gen.items()})
                got = self.cp.month_sums(price, g, "America/Chicago")
                self.assertEqual(list(got), ["2026-06"])
                n, him, sp, sg, spg = got["2026-06"]
                hand_pg = sum(by_hand_price[h] * self.gen[h][fuel] for h in self.gen)
                hand_g = sum(self.gen[h][fuel] for h in self.gen)
                hand_p = sum(by_hand_price[h] for h in self.gen)
                self.assertEqual((n, him), (168, 720))
                self.assertAlmostEqual(spg / sg, hand_pg / hand_g, places=6, msg=f"{name} {fuel}")
                self.assertAlmostEqual(sp / n, hand_p / 168, places=4)
                f = self.cp.figure([got["2026-06"]])
                self.assertAlmostEqual(f["price"], hand_pg / hand_g, places=6)
                self.assertAlmostEqual(f["premium"], hand_pg / hand_g - hand_p / 168, places=4)
        # the week's own numbers, so a change of the sample is seen: solar at the West hub earned less than the flat average
        solar = self.cp.figure([self.cp.month_sums(hourly, self.series({h: v["solar"] for h, v in self.gen.items()}), "America/Chicago")["2026-06"]])
        self.assertAlmostEqual(solar["price"], 28.4221, places=3)
        self.assertAlmostEqual(solar["flat"], 36.3651, places=3)

    def test_the_same_generation_in_every_hour_captures_the_flat_average(self):
        price = self.series(self.rt)
        flat = self.pd.Series(250.0, index=price.index)
        f = self.cp.figure(list(self.cp.month_sums(price, flat, "America/Chicago").values()))
        self.assertAlmostEqual(f["price"], f["flat"], places=9)
        self.assertAlmostEqual(f["premium"], 0.0, places=9)
        self.assertAlmostEqual(f["price"], sum(self.rt.values()) / 168, places=4)

    def test_dollars_and_percent_agree(self):
        price = self.series(self.rt)
        for fuel in ("solar", "wind"):
            f = self.cp.figure(list(self.cp.month_sums(price, self.series({h: v[fuel] for h, v in self.gen.items()}), "America/Chicago").values()))
            self.assertAlmostEqual(f["premium"], f["price"] - f["flat"], places=12)
            self.assertAlmostEqual(f["pct"], 100 * f["premium"] / f["flat"], places=12)
            self.assertEqual(f["pct"] < 0, f["premium"] < 0)

    def test_a_month_under_95_percent_writes_no_figure(self):
        months = self.cp.month_sums(self.series(self.rt), self.series({h: v["wind"] for h, v in self.gen.items()}), "America/Chicago")
        self.assertFalse(self.cp.counted(months["2026-06"]))          # one week of June: 168 of 720 hours
        self.assertIsNone(self.cp.last_twelve(months))
        self.assertEqual(self.cp.years(months), {})
        self.assertTrue(self.cp.counted([684, 720, 0, 0, 0]))
        self.assertFalse(self.cp.counted([683, 720, 0, 0, 0]))
        full = {f"{y}-{m:02d}": [720, 720, 720 * 30.0, 7200.0, 7200 * 25.0] for y in (2024, 2025) for m in range(1, 13)}
        full["2025-06"] = [600, 720, 600 * 30.0, 6000.0, 6000 * 25.0]
        self.assertEqual(self.cp.last_twelve(full)[-1], "2025-05")     # the newest twelve in a row end before the short month
        n, whole, f = self.cp.years(full)["2025"]
        self.assertEqual((n, whole, f["hours"]), (11, False, 11 * 720))  # its counted months only: nothing scaled up

    def test_an_hour_without_a_price_or_generation_is_in_neither_sum(self):
        idx = self.pd.to_datetime(["2026-06-01T05:00:00Z", "2026-06-01T06:00:00Z", "2026-06-01T07:00:00Z", "2026-06-01T08:00:00Z"], utc=True)
        price = self.pd.Series([10.0, 20.0, float("nan"), 40.0], index=idx).dropna()
        gen = self.pd.Series([1.0, float("nan"), 5.0, -3.0], index=idx).dropna()
        n, _, sp, g, pg = self.cp.month_sums(price, gen, "America/Chicago")["2026-06"]
        self.assertEqual((n, sp, g, pg), (2, 50.0, 1.0, 10.0))        # generation below zero weighs nothing and stays in the flat average

    def test_miso_has_no_number(self):
        self.assertNotIn("miso", self.cp.GRIDS)
        self.assertEqual(self.cp.BLANK["miso"]["words"], "paused while terms are reviewed")
        self.assertEqual(self.cp.BLANK["pjm"]["words"], "licensed source needed")
        f = json.loads(src("site", "data", "seller", "capture.json"))
        self.assertEqual(sorted(f["grids"]), ["caiso", "ercot", "isone", "nyiso", "spp"])
        self.assertEqual(f["blank"], {"miso": {"name": "MISO", "words": "paused while terms are reviewed"}, "pjm": {"name": "PJM", "words": "licensed source needed"}})
        text = json.dumps(f["grids"])
        self.assertNotRegex(text, r"(?i)miso:|INDIANA|\.HUB\"")
        self.assertIn("paused(", src("warehouse", "derived", "capture_price.py"))   # the pause list is asked before a grid is read


class TheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = json.loads(src("site", "data", "seller", "capture.json"))

    def test_every_month_is_within_its_month_and_names_its_tables(self):
        self.assertEqual(self.f["near"], 0.95)
        seen = 0
        for g in self.f["grids"].values():
            self.assertIn(g["main"], [h["id"] for h in g["hubs"]])
            for h in g["hubs"]:
                for side in ("rt", "da"):
                    if side not in h:
                        continue
                    self.assertTrue(h[side]["tables"] and set(h[side]["tables"]) <= set(self.f["tables"]))
                    for fuel in ("solar", "wind"):
                        for m, r in h[side].get(fuel, {}).items():
                            seen += 1
                            self.assertTrue(0 < r[0] <= r[1] and r[1] in (672, 696, 719, 720, 721, 743, 744, 745) and r[3] >= 0, (h["id"], side, fuel, m, r))
        self.assertGreater(seen, 3000)

    def test_the_builder_and_the_page_agree_on_every_figure(self):
        try:
            import capture_price as cp
        except ImportError as e:
            raise unittest.SkipTest(f"the builder's libraries are not on this machine: {e}")
        js = ("const C = await import('./lib/capture.ts'); const fs = (await import('node:fs')).default; const F = JSON.parse(fs.readFileSync('data/seller/capture.json', 'utf8')); const out = {};"
              "for (const [g, G] of Object.entries(F.grids)) for (const h of G.hubs) for (const m of ['rt', 'da']) for (const f of C.FUELS) { const s = C.twelve(h[m]?.[f], F.near);"
              " out[[g, h.id, m, f].join('|')] = { s, y: C.years(h[m]?.[f], F.near).map((r) => [r.y, r.months, r.whole, r.f ? r.f.premium : null]) }; } console.log(JSON.stringify(out));")
        r = node(["--input-type=module", "-e", js])
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        page = json.loads(r.stdout.strip().splitlines()[-1])
        twelve = 0
        for g, G in self.f["grids"].items():
            for h in G["hubs"]:
                for side in ("rt", "da"):
                    for fuel in ("solar", "wind"):
                        months = h.get(side, {}).get(fuel, {})
                        t = cp.last_twelve(months) if months else None
                        mine = cp.figure([months[m] for m in t]) if t else None
                        theirs = page["|".join([g, h["id"], side, fuel])]
                        self.assertEqual(mine is None, theirs["s"] is None, (g, h["id"], side, fuel))
                        if mine:
                            twelve += 1
                            self.assertEqual((theirs["s"]["from"], theirs["s"]["to"]), (t[0], t[-1]))
                            for k in ("price", "flat", "premium", "pct"):
                                self.assertAlmostEqual(mine[k], theirs["s"][k], places=9)
                        ys = cp.years(months) if months else {}
                        self.assertEqual([[y, n, whole, None if fg is None else round(fg["premium"], 9)] for y, (n, whole, fg) in ys.items()],
                                         [[y, n, whole, None if p is None else round(p, 9)] for y, n, whole, p in theirs["y"]])
        self.assertGreaterEqual(twelve, 40)

    def test_the_main_hubs_hold_their_last_twelve_months(self):
        try:
            import capture_price as cp
        except ImportError as e:
            raise unittest.SkipTest(f"the builder's libraries are not on this machine: {e}")
        for grid, side in (("ercot", "rt"), ("caiso", "rt"), ("spp", "rt"), ("isone", "da")):
            G = self.f["grids"][grid]
            h = next(x for x in G["hubs"] if x["id"] == G["main"])
            for fuel in ("solar", "wind"):
                t = cp.last_twelve(h[side][fuel])
                self.assertIsNotNone(t, (grid, side, fuel))
                f = cp.figure([h[side][fuel][m] for m in t])
                self.assertTrue(0 < f["price"] < 500 and 0 < f["flat"] < 500 and f["hours"] >= 0.95 * 8760)
        ny = next(x for x in self.f["grids"]["nyiso"]["hubs"] if x["id"] == "N.Y.C.")
        self.assertIsNone(cp.figure(list(ny["da"]["solar"].values())))     # EIA-930 itemizes no solar for New York: nothing to weigh by


class TheNodeTest(unittest.TestCase):
    def test_the_arithmetic_of_the_page(self):
        r = node(["scripts/test-capture.mjs"])
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        for words in ("the contract arithmetic equals the battery page's", "the combined figure is the solar plant's revenue plus the battery's", "captures the flat average", "MISO has no number", "counts for nothing"):
            self.assertIn(words, r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_the_library_has_no_imports(self):
        lib = src("site", "lib", "capture.ts")
        self.assertNotRegex(lib, r"(?m)^\s*import\s")
        self.assertNotIn("require(", lib)


class OnePage(unittest.TestCase):
    def test_version_two_redirects_and_its_file_is_retired(self):
        cfg = src("site", "next.config.ts")
        self.assertIn('{ source: "/cost-of-power/seller/v2", destination: "/cost-of-power/seller", permanent: true }', cfg)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "app", "cost-of-power", "seller", "v2")))
        for kept in ("seller-v2", "seller-original"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "app", "_retired", kept, "page.tsx")), kept)
        rel = src("site", "lib", "release.ts")
        self.assertRegex(rel, r'"/cost-of-power/seller":\s*"review"')
        self.assertRegex(rel, r'"/cost-of-power/seller/v2":\s*"review"')
        self.assertRegex(rel, r'"/cost-of-power/battery":\s*"live"')

    def test_the_page_has_every_part(self):
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        for piece in ("ToolPage", "ToolHeader", "InputPanel", "HeadlineRow", "ChartFrame", "ToolSection", "ToolTable", "Fold", "SourceLine", "ContractProvider", "ContractInputs", "ContractResult",
                      "PremiumYears", "RevenueYears", "MonthlyRevenue", "CoverageLine", "SellerForm", "CostTabs"):
            self.assertIn(f"<{piece}", page, piece)
        for part in ('id="capture"', 'id="capture-years"', 'id="spans"', 'id="contract"', 'id="hybrid"', 'id="months"', 'id="coverage"', "freeEnergyHref(iso, hub.id)", "B.stat(read.data, [], bx, \"l12:total\")",
                     "combined(plantTotal", "stress_total", "ttm_under125", "over_nameplate", "data-seller2={`twelve|${id}`}"):
            self.assertIn(part, page, part)
        charts = src("site", "app", "cost-of-power", "seller", "SellerCharts.tsx")
        self.assertEqual(charts.count("tooltip: {"), 4)                 # each of the four charts answers the mouse
        self.assertNotIn("<svg", page)                                   # no static drawing is left on the page
        contract = src("site", "app", "cost-of-power", "seller", "SellerContract.tsx")
        self.assertIn('import { contractResult, usdShort } from "@/lib/datacenter";', contract)   # the arithmetic already written, not a third
        self.assertNotRegex(contract, r"<form|name=|fetch\(|localStorage|sessionStorage|document\.cookie|router")

    def test_no_method_prose_on_the_face_and_all_of_it_in_the_note(self):
        files = [src("site", "app", "cost-of-power", "seller", f) for f in ("page.tsx", "SellerForm.tsx", "SellerContract.tsx")]
        import re
        for text in files:
            body = re.sub(r"(?m)^\s*//.*$", "", text)                    # the code's own comments are not the face
            body = re.sub(r'(?:why|title)=(?:"[^"]*"|\{`[^`]*`\}|\{[A-Za-z_.]+\})', "", body)   # a reason on hover is allowed
            body = re.sub(r"const (?:COMBINED|PJM_WHY|contractWhy|threeWhy|everyWhy|twelveWhy|RULES|DA_PLANT|DA_BATTERY|DA_PAIR|DA_ADDED|KEPT)\b[^;]*;", "", body, flags=re.S)
            # session 162: the owner's words of 9 October 2026 keep the added figure "as a labeled upper bound", so that one
            # label stands on the face; every other use of the words is still method prose
            body = body.replace("Added, not co-optimized: upper bound", "")
            self.assertNotRegex(body, r"(?i)upper bound|merchant only|does not tell|how it is measured|how a lender should read|not a site|limitation|cannot see")
        note = src("docs", "methods", "cost_of_power.md")
        for words in ("Merchant only.", "How a lender should read the page", "The battery is an upper bound", "The hub, not your node", "Gas is Henry Hub", "It is the fleet's shape, not a site's",
                      "Why this figure and the model's capture price differ", "Combined** is the two revenues added, and nothing else", "no shared interconnection limit", "does not charge from the plant's own output",
                      "paused while terms are reviewed", "licensed source needed", "at least 95 percent of the month's hours", "#free-energy"):
            self.assertIn(words, note, words)

    def test_the_live_battery_page_is_not_touched(self):
        r = subprocess.run(["git", "diff", "--name-only", "origin/main", "--", "site/app/cost-of-power/battery", "site/app/cost-of-power/Tabs.tsx", "site/lib/batterystack.ts", "site/components/tool",
                            "site/components/echarts.ts", "site/app/network", "site/app/storage", "site/data/battery_stack_review.json", "site/scripts/snapshot-live.mjs"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            raise unittest.SkipTest("origin/main is not known to this copy")
        self.assertEqual(r.stdout.strip(), "")

    def test_no_em_dash(self):
        for rel in ("site/lib/capture.ts", "site/app/cost-of-power/seller/page.tsx", "site/app/cost-of-power/seller/SellerForm.tsx", "site/app/cost-of-power/seller/SellerContract.tsx",
                    "site/app/cost-of-power/seller/SellerCharts.tsx", "site/scripts/test-capture.mjs", "site/scripts/check-seller.mjs", "warehouse/derived/capture_price.py",
                    "docs/methods/cost_of_power.md", "tests/test_session145.py", "site/data/seller/capture.json", "tests/fixtures/session145/prices_week.csv", "tests/fixtures/session145/generation_week.csv"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
