"""Session 162: what a generator earns, deeper (/cost-of-power/seller).

On the site's own files, which hold real rows only (site/data/seller/hybrid.json: the main hub's day-ahead prices and
the fleet's output per MW over the last twelve months, ERCOT and CAISO; site/public/seller/prices/*.json: one calendar
year of day-ahead prices by hub; site/data/seller/capture.json):

  capture price times generation equals revenue: every hub, fuel, market and year of the capture table, and the
    hybrid's plants hour by hour;
  the co-optimized pair never earns less than the plant alone, on any day;
  state of charge, power, the interconnection limit and the one cycle a day hold in every hour;
  with a battery of zero size the pair is the plant;
  the two alone, added, are never below the pair;
  the page's function (site/lib/sellerhybrid.ts, its own simplex) and the builder's (scipy) agree on the page's own
    plants (site/scripts/test-hybrid.mjs, run here), and the file's figures are the builder's when solved again;
  the battery alone is the battery page's own daily program with no ancillary product, day for day;
  the price files are whole years of public hubs, never MISO or PJM; a profile is refused, never repaired;
  the profile box sends and stores nothing (the code holds no way to; a real browser proves it in
    site/scripts/check-seller-deeper.mjs); the page keeps what it showed and stays in review.
No network, no table: a machine without the warehouse's tables runs all of it.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELLER = os.path.join(ROOT, "site", "app", "cost-of-power", "seller")
PRICES = os.path.join(ROOT, "site", "public", "seller", "prices")
sh = np = None
FILE = CAPTURE = None


def setUpModule():
    global sh, np, FILE, CAPTURE
    for p in (os.path.join(ROOT, "warehouse", "derived"), os.path.join(ROOT, "warehouse", "connectors")):
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        import numpy
        import seller_hybrid
    except ImportError as e:  # a machine without the builder's libraries
        raise unittest.SkipTest(f"the builder cannot be imported here: {e}")
    sh, np = seller_hybrid, numpy
    with open(os.path.join(ROOT, "site", "data", "seller", "hybrid.json"), encoding="utf-8") as f:
        FILE = json.load(f)
    with open(os.path.join(ROOT, "site", "data", "seller", "capture.json"), encoding="utf-8") as f:
        CAPTURE = json.load(f)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(args):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe] + args, cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=600)
    if r.returncode != 0 and ("ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    return r


def days_of(g, fuel):
    """The held days of a fuel's twelve months: [(date, prices, output per MW)], as the page takes them."""
    price = np.array([np.nan if v is None else v for v in g["price"]])
    gen = np.array([np.nan if v is None else v for v in g[fuel]])
    months = g["fuels"][fuel]["months"]
    out = []
    for date, i0, T in g["days"]:
        if not (months[0] <= date[:7] <= months[-1]):
            continue
        p, q = price[i0:i0 + T], gen[i0:i0 + T]
        if np.isnan(p).any() or np.isnan(q).any():
            continue
        out.append((date, p, q))
    return out


class ThePair(unittest.TestCase):
    def test_the_file_is_the_builders_when_solved_again(self):
        """ERCOT and CAISO, solar and wind, a 4-hour battery of the plant's size: the twelve months solved again here
        with scipy give the file's plant, battery alone and pair."""
        for grid, g in FILE["grids"].items():
            for fuel in g["fuels"]:
                days = days_of(g, fuel)
                self.assertEqual(len(days), g["fuels"][fuel]["days"], (grid, fuel))
                limit = max(1.0, max(float(q.max()) for _, _, q in days))
                plant = add = alone = 0.0
                for _, p, q in days:
                    plant += float(p @ q)
                    add += sh.solve_day(p, q, 1.0, 4.0, limit)[0]
                    alone += sh.solve_day(p, np.zeros(len(p)), 1.0, 4.0, float("inf"))[0]
                c = next(k for k in g["check"] if k["fuel"] == fuel and k["hours"] == 4 and k["battery_mw_per_plant_mw"] == 1.0)
                for mine, theirs, what in ((plant, c["plant"], "plant"), (alone, c["battery"], "battery"), (plant + add, c["pair"], "pair")):
                    self.assertAlmostEqual(mine, theirs, delta=1e-6 * max(1.0, abs(theirs)), msg=(grid, fuel, what))

    def test_the_pair_is_never_below_the_plant_and_every_limit_holds(self):
        eta = math.sqrt(sh.RTE)
        for grid, g in FILE["grids"].items():
            for fuel in g["fuels"]:
                days = days_of(g, fuel)
                limit = max(1.0, max(float(q.max()) for _, _, q in days))
                for hours, power in ((2, 1.0), (8, 0.5)):
                    energy = power * hours
                    for date, p, q in days:
                        v, c, d = sh.solve_day(p, q, power, energy, limit)
                        where = (grid, fuel, hours, date)
                        self.assertGreaterEqual(v, -1e-7, where)                      # the pair is the plant plus v
                        soc = np.cumsum(eta * c - d / eta)
                        self.assertTrue((c >= -1e-7).all() and (c <= power + 1e-7).all() and (d >= -1e-7).all() and (d <= power + 1e-7).all(), where)
                        self.assertTrue((soc >= -1e-6).all() and (soc <= energy + 1e-6).all(), where)
                        self.assertTrue((q + d - c <= limit + 1e-6).all() and (c - d - q <= limit + 1e-6).all(), where)
                        self.assertLessEqual(float((d / eta).sum()), energy + 1e-6, where)  # one full cycle a day at most
                        self.assertTrue((np.minimum(c, d) <= 1e-6).all(), where)        # never both in one hour
                        self.assertTrue((d[p < 0] <= 1e-7).all(), where)                # no discharge below a price of zero

    def test_a_battery_of_zero_size_leaves_the_plant(self):
        g = FILE["grids"]["ercot"]
        for _, p, q in days_of(g, "solar")[:40]:
            v, c, d = sh.solve_day(p, q, 0.0, 0.0, 1.0)
            self.assertEqual((v, float(c.sum()), float(d.sum())), (0.0, 0.0, 0.0))

    def test_the_two_added_are_an_upper_bound_of_the_pair(self):
        for grid, g in FILE["grids"].items():
            for c in g["check"]:
                self.assertGreaterEqual(c["plant"] + c["battery"], c["pair"] - 1e-6, (grid, c["fuel"], c["hours"]))
                self.assertGreaterEqual(c["pair"], c["plant"] - 1e-6, (grid, c["fuel"], c["hours"]))
                self.assertLessEqual(c["from_plant"], c["charged"] + 1e-6)

    def test_the_battery_alone_is_the_battery_pages_program(self):
        """The battery page's daily program (warehouse/derived/battery_stack.py, solve_day) with no ancillary product,
        on the same days and prices: the same figure on every day without a price below zero, never below this
        copy's on a day with one (the page's program may discharge at a price below zero; this copy does not), and
        within 0.05 percent over the twelve months."""
        try:
            import battery_stack as bs
        except ImportError as e:
            raise unittest.SkipTest(f"the battery page's builder cannot be imported here: {e}")
        self.assertEqual(sh.RTE, bs.RTE)
        for grid, g in FILE["grids"].items():
            days = days_of(g, "solar")
            for hours in (2, 4, 8):
                mine = theirs = 0.0
                for date, p, _ in days[::3]:
                    a = sh.solve_day(p, np.zeros(len(p)), 1.0, float(hours), float("inf"))[0]
                    b = bs.solve_day(list(p), [], [], hours)["total"]
                    if (p >= 0).all():
                        self.assertAlmostEqual(a, b, delta=1e-6 * max(1.0, abs(b)), msg=(grid, hours, date))
                    else:
                        self.assertLessEqual(a, b + 1e-6, (grid, hours, date))
                    mine += a
                    theirs += b
                self.assertLessEqual(theirs - mine, 5e-4 * theirs, (grid, hours))

    def test_the_page_and_the_builder_agree(self):
        r = node(["scripts/test-hybrid.mjs"])
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("all passed", r.stdout)
        self.assertRegex(r.stdout, r"ok\s+1\. ercot: the page's function and the builder's agree")
        self.assertRegex(r.stdout, r"ok\s+1\. caiso: the page's function and the builder's agree")

    def test_the_library_has_no_imports(self):
        lib = src("site", "lib", "sellerhybrid.ts")
        self.assertIsNone(re.search(r"(?m)^\s*import\s", lib))   # Node runs it as it is, and so does the browser
        self.assertIn("export const RTE = 0.86", lib)


class CaptureTimesGenerationIsRevenue(unittest.TestCase):
    def test_every_hub_fuel_market_and_year(self):
        """The capture table's cells: the capture price (the builder's figure) times the generation weighed equals the
        sum of price x generation, to a cent in a million dollars."""
        import capture_price as cz
        cells = 0
        for iso, g in CAPTURE["grids"].items():
            self.assertNotIn(iso, ("miso", "pjm"))
            for h in g["hubs"]:
                for key in ("rt", "da"):
                    for fuel in ("solar", "wind"):
                        months = (h.get(key) or {}).get(fuel)
                        if not months:
                            continue
                        for y, (n, whole, f) in cz.years(months, CAPTURE["near"]).items():
                            if not f:
                                continue
                            revenue = sum(months[m][4] for m in months if m[:4] == y and cz.counted(months[m], CAPTURE["near"]))
                            self.assertAlmostEqual(f["price"] * f["mwh"], revenue, delta=1e-8 * max(1.0, abs(revenue)) + 0.01, msg=(iso, h["id"], key, fuel, y))
                            self.assertLessEqual(f["hours"], 8784)
                            cells += 1
        self.assertGreater(cells, 500)

    def test_the_hybrids_plants_hour_by_hour(self):
        for grid, g in FILE["grids"].items():
            for fuel in g["fuels"]:
                days = days_of(g, fuel)
                revenue = sum(float(p[t]) * float(q[t]) for _, p, q in days for t in range(len(p)))   # by hand, hour by hour
                energy = sum(float(v) for _, _, q in days for v in q)
                c = next(k for k in g["check"] if k["fuel"] == fuel)
                self.assertAlmostEqual(revenue, c["plant"], delta=1e-6 * abs(c["plant"]))
                self.assertAlmostEqual(energy, c["energy"], delta=1e-6 * abs(c["energy"]))
                self.assertAlmostEqual((c["plant"] / c["energy"]) * c["energy"], revenue, delta=1e-6 * abs(revenue))
                self.assertTrue(all((q >= 0).all() for _, _, q in days))                       # output is never below zero


class TheFiles(unittest.TestCase):
    def test_the_hybrid_file_holds_the_two_open_grids_and_no_paused_one(self):
        self.assertEqual(sorted(FILE["grids"]), ["caiso", "ercot"])
        self.assertEqual(sorted(FILE["years"]), ["caiso", "ercot", "isone", "nyiso", "spp"])
        self.assertNotIn("miso", json.dumps(FILE).lower())
        self.assertNotIn("pjm", json.dumps(FILE).lower())
        for grid, g in FILE["grids"].items():
            self.assertEqual(g["market"], "day-ahead")
            self.assertEqual(g["hub"], CAPTURE["grids"][grid]["main"])
            self.assertEqual(len(g["price"]), len(g["solar"]))
            self.assertEqual(len(g["price"]), len(g["wind"]))
            for fuel, f in g["fuels"].items():
                self.assertEqual(len(f["months"]), 12)
                self.assertGreaterEqual(f["days"], 0.9 * (f["days"] + f["left_out"]))
            for date, i0, T in g["days"]:
                self.assertIn(T, (23, 24, 25))
                self.assertLessEqual(i0 + T, len(g["price"]))

    def test_the_price_years_are_whole_years_of_public_main_hubs(self):
        on_disk = sorted(os.listdir(PRICES))
        listed = sorted(y["file"] for ys in FILE["years"].values() for y in ys)
        self.assertEqual(on_disk, listed)
        offsets = {"ercot": -6, "caiso": -8, "nyiso": -5, "isone": -5, "spp": -6}
        for name in on_disk:
            self.assertRegex(name, r"^(ercot|caiso|nyiso|isone|spp)_20\d\d\.json$")
            with open(os.path.join(PRICES, name), encoding="utf-8") as f:
                p = json.load(f)
            leap = p["year"] % 4 == 0 and (p["year"] % 100 != 0 or p["year"] % 400 == 0)
            self.assertEqual(p["hours"], 8784 if leap else 8760, name)
            self.assertEqual(len(p["price"]), p["hours"], name)
            self.assertEqual(sum(v is not None for v in p["price"]), p["held"], name)
            self.assertGreaterEqual(p["held"], 0.95 * p["hours"], name)
            self.assertEqual(p["hub"], CAPTURE["grids"][p["grid"]]["main"], name)
            self.assertEqual(p["market"], "day-ahead")
            self.assertEqual(p["utc_offset_hours"], offsets[p["grid"]])
            self.assertEqual(p["first_utc"], f"{p['year']}-01-01T{-p['utc_offset_hours']:02d}:00:00Z", name)
            self.assertTrue(all(v is None or isinstance(v, (int, float)) for v in p["price"]), name)
            self.assertTrue(p["tables"] and all(t in CAPTURE["tables"] for t in p["tables"]), name)   # the capture price's own public tables


class ThePage(unittest.TestCase):
    def test_the_three_new_blocks_and_everything_kept(self):
        page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        for part in ('id="hub-years"', 'id="profile"', 'id="hybrid"', "<SellerHubYears", "<SellerProfile", 'data-hybrid2="pair"', 'data-hybrid2="plant"', 'data-hybrid2="battery"', 'data-hybrid2="added"',
                     "Added, not co-optimized: upper bound", "an upper bound for a schedule made the day before",
                     # what session 145 showed, still here
                     'id="capture"', 'id="capture-years"', 'id="spans"', 'id="contract"', 'id="months"', 'id="coverage"', 'data-hybrid="plant"', 'data-hybrid="battery"', 'data-hybrid="combined"',
                     "combined(plantTotal", "not modeled for this grid", "<PremiumYears", "<RevenueYears", "<MonthlyRevenue", "<CoverageLine", "<ContractResult", "freeEnergyHref(iso, hub.id)"):
            self.assertIn(part, page, part)
        rel = src("site", "lib", "release.ts")
        self.assertRegex(rel, r'"/cost-of-power/seller":\s*"review"')
        self.assertRegex(rel, r'"/cost-of-power/battery":\s*"live"')

    def test_the_profile_box_has_no_way_to_send_or_store(self):
        box = src("site", "app", "cost-of-power", "seller", "SellerProfile.tsx")
        code = re.sub(r"(?m)^\s*//.*$", "", box)
        self.assertIn('"use client"', box)
        self.assertIn("Computed on this device. Nothing you paste or upload is sent or stored.", box)
        for word in ("localStorage", "sessionStorage", "document.cookie", "indexedDB", "sendBeacon", "XMLHttpRequest", "WebSocket", "useRouter", "URLSearchParams", "history.", "<form", "method:", "body:", " name="):
            self.assertNotIn(word, code, word)
        fetches = re.findall(r"fetch\(([^)]*)\)", code)
        self.assertEqual(len(fetches), 1)                                  # one request: the static price file, by grid and year
        self.assertIn("`/seller/prices/${grid}_${year}.json`", fetches[0])
        self.assertIn('credentials: "omit"', fetches[0])
        self.assertIn("new FileReader()", code)                            # a file is read on the device

    def test_no_method_prose_on_the_new_faces(self):
        for f in ("SellerProfile.tsx", "SellerHubYears.tsx"):
            body = re.sub(r"(?m)^\s*//.*$", "", src("site", "app", "cost-of-power", "seller", f))
            body = re.sub(r'title=(?:"[^"]*"|\{`[^`]*`\}|\{[A-Za-z_.]+\})', "", body)
            body = re.sub(r"const (?:accepted|title|share|left|[a-z]+Why)\b[^;]*;", "", body, flags=re.S)
            body = body.replace("Added, not co-optimized: upper bound", "")   # the owner's label
            self.assertNotRegex(body, r"(?i)upper bound|merchant only|does not tell|how it is measured|not a site|limitation|cannot see|assum", f)

    def test_the_method_note_holds_the_three_methods(self):
        note = src("docs", "methods", "cost_of_power.md")
        for words in ("## Session 162", "an upper bound for a schedule made the day before", "Added, not co-optimized", "at most one full cycle a day", "no discharge in an hour priced below zero",
                      "the plant's capacity, or its highest hour", "Capture price by hub and year", "hours held of the year", "Your plant's profile", "8,784", "local standard time",
                      "Nothing is sent and nothing is stored", "exactly one column"):
            self.assertIn(words, note, words)

    def test_no_em_dash(self):
        for rel in ("site/lib/sellerhybrid.ts", "site/lib/capture.ts", "site/app/cost-of-power/seller/page.tsx", "site/app/cost-of-power/seller/SellerProfile.tsx", "site/app/cost-of-power/seller/SellerHubYears.tsx",
                    "site/scripts/test-hybrid.mjs", "site/scripts/check-seller-deeper.mjs", "site/scripts/check-seller.mjs", "warehouse/derived/seller_hybrid.py", "docs/methods/cost_of_power.md",
                    "tests/test_session162.py", "site/data/seller/hybrid.json"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
