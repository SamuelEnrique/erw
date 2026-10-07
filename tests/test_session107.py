"""Session 107: the seller's tab, version 2 (/cost-of-power/seller/v2, in review).

Session 145: version 2 is folded into /cost-of-power/seller and its address redirects there. Its page file is kept,
unrouted, under site/app/_retired/seller-v2; the spans of site/lib/seller2.ts are the one page's now, and the battery
(energy alone, the model's 4-hour battery) is one of its assets. The tests below read the retired file and the one page.

The spans (the last twelve months, the two long-run averages) recomputed here from the live tab's own snapshot and set
against site/lib/seller2.ts; the rules of a span on months made for the test; the page in review with its own line in
the release list; the live tab untouched. No network.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STDIN = "JSON.parse(await new Promise((done) => { let s = ''; process.stdin.on('data', (d) => { s += d; }); process.stdin.on('end', () => done(s)); }))"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js, stdin=None):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180, input=stdin)
    if r.returncode != 0:
        if "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr or "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def prev(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def by_hand(snap, grid, asset):
    """The three spans from the snapshot, the long way: revenue per kW a year, and the months of the last twelve."""
    s = snap["isos"][grid]
    near = snap["defaults"]["near"]
    if asset == "battery":   # session 145: the battery is the model's 4-hour battery, held by its days
        import calendar
        held = {m: r["battery_4h"] for m, r in s["months"].items() if "battery_4h" in r and r["battery_4h"]["hours"] / calendar.monthrange(int(m[:4]), int(m[5:7]))[1] >= near - 1e-9}
    else:
        held = {m: r[asset] for m, r in s["months"].items() if asset in r and r[asset]["hours"] / r["him"] >= near - 1e-9}
    twelve = None
    for m in sorted(held, reverse=True):
        if all(prev(m, k) in held for k in range(12)):
            twelve = [prev(m, k) for k in range(11, -1, -1)]
            break
    full = sorted(y for y in {m[:4] for m in held} if sum(1 for m in held if m[:4] == y) == 12)
    three = full[-3:] if len(full) >= 3 and [int(y) for y in full[-3:]] == list(range(int(full[-1]) - 2, int(full[-1]) + 1)) else None
    rev = lambda months: sum(held[m]["revenue_per_mw"] for m in months) / 1000   # noqa: E731
    return {"twelve": (rev(twelve), twelve[0], twelve[-1]) if twelve else None,
            "three": rev([m for m in held if m[:4] in three]) / 3 if three else None,
            "every": rev([m for m in held if m[:4] in full]) / len(full) if full else None, "full": full}


class TheSpans(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snap = json.loads(src("site", "data", "merchant_snapshot.json"))
        cls.got = node("const b = await import('./lib/seller2.ts'); const fs = (await import('node:fs')).default; const snap = JSON.parse(fs.readFileSync('data/merchant_snapshot.json', 'utf8'));"
                       "const out = {}; for (const g of b.GRIDS) for (const a of b.ASSETS) { const c = { grid: g.id, asset: a.id }; const ms = b.monthsOf(snap, c); const s = b.spans(ms);"
                       " out[g.id + '|' + a.id] = { s, sentence: b.sentence(c, s), held: ms.filter((r) => r.held).length, years: b.years(ms) }; } console.log(JSON.stringify(out));")

    def test_every_view_equals_the_snapshot_added_up_by_hand(self):
        n = 0
        for key, g in self.got.items():
            grid, asset = key.split("|")
            want = by_hand(self.snap, grid, asset)
            s = g["s"]
            if want["twelve"] is None:
                self.assertIsNone(s["twelve"], key)
            else:
                self.assertAlmostEqual(s["twelve"]["revenue_kw"], want["twelve"][0], places=6, msg=key)
                self.assertEqual((s["twelve"]["from"], s["twelve"]["to"], s["twelve"]["months"]), (want["twelve"][1], want["twelve"][2], 12), key)
                n += 1
            for span, k in (("three", "three"), ("every", "every")):
                if want[k] is None:
                    self.assertIsNone(s[span], (key, span))
                else:
                    self.assertAlmostEqual(s[span]["revenue_kw"], want[k], places=6, msg=(key, span))
            self.assertEqual(s["everyYears"], want["full"], key)
        self.assertGreaterEqual(n, 10)                          # the views with twelve months in a row (a grid with a gap in its prices has none)

    def test_only_texas_has_a_long_run_average_today(self):
        for key, g in self.got.items():
            grid = key.split("|")[0]
            if g["held"] == 0:
                continue
            self.assertEqual(g["s"]["three"] is not None, grid == "ercot", key)
        self.assertIn("The long-run average of 2023 to 2025 was USD", self.got["ercot|solar"]["sentence"])
        self.assertIn("There is no long-run average yet.", self.got["caiso|solar"]["sentence"])
        self.assertIn("a margin over fuel of USD", self.got["ercot|peaker"]["sentence"])

    def test_new_york_has_no_solar_and_says_so(self):
        self.assertEqual(self.got["nyiso|solar"]["held"], 0)
        self.assertIsNone(self.got["nyiso|solar"]["sentence"])
        page = src("site", "app", "_retired", "seller-v2", "page.tsx")
        self.assertIn("so no number is shown", page)

    def test_miso_is_not_shown_and_the_page_says_why(self):
        self.assertNotIn("miso|solar", self.got)
        out = node("const b = await import('./lib/seller2.ts'); console.log(JSON.stringify({ g: b.GRIDS.map((x) => x.id), p: b.PAUSED.words, c: b.choiceOf({ iso: 'miso', asset: 'battery' }) }));")
        self.assertEqual(out["g"], ["ercot", "caiso", "nyiso", "spp", "isone"])
        self.assertIn("paused since 4 October 2026", out["p"])
        self.assertEqual(out["c"], {"grid": "ercot", "asset": "battery"})  # MISO is not a choice of the page; session 145: the battery is


class TheRules(unittest.TestCase):
    def spans(self, months):
        return node(f"const b = await import('./lib/seller2.ts'); const ms = {STDIN}; const s = b.spans(ms); console.log(JSON.stringify({{ s, years: b.years(ms) }}));", stdin=json.dumps(months))

    def month(self, m, revenue=1000.0, held=True, energy=100.0, capture=20.0, flat=25.0):
        return {"m": m, "held": held, "share": 1.0 if held else 0.5, "revenue": revenue, "energy": energy, "capture": capture, "flat": flat, "rate": 80.0, "cfads": revenue, "dscr": None}

    def test_a_month_missing_breaks_the_twelve_and_the_year(self):
        ms = [self.month(f"2024-{i:02d}") for i in range(1, 13)] + [self.month(f"2025-{i:02d}", held=(i != 6)) for i in range(1, 13)] + [self.month(f"2026-{i:02d}") for i in range(1, 4)]
        out = self.spans(ms)
        s = out["s"]
        self.assertEqual(s["everyYears"], ["2024"])            # 2025 lacks June; 2026 is three months
        self.assertIsNone(s["three"])
        self.assertEqual((s["twelve"]["from"], s["twelve"]["to"]), ("2024-06", "2025-05"))   # the newest twelve held in a row end at the gap
        self.assertEqual([(y["y"], y["months"], y["complete"]) for y in out["years"]], [("2024", 12, True), ("2025", 11, False), ("2026", 3, False)])
        self.assertAlmostEqual(s["twelve"]["revenue_kw"], 12.0)
        self.assertAlmostEqual(s["twelve"]["capture"], 20.0)
        self.assertAlmostEqual(s["twelve"]["rate"], 80.0)

    def test_a_long_run_average_is_a_year_not_a_sum(self):
        ms = [self.month(f"{y}-{i:02d}", revenue=1000.0 * (y - 2020)) for y in (2021, 2022, 2023, 2024) for i in range(1, 13)]
        s = self.spans(ms)["s"]
        self.assertEqual(s["threeYears"], ["2022", "2023", "2024"])
        self.assertAlmostEqual(s["three"]["revenue_kw"], (24 + 36 + 48) / 3)      # USD per kW a year
        self.assertAlmostEqual(s["every"]["revenue_kw"], (12 + 24 + 36 + 48) / 4)
        self.assertEqual(s["three"]["years"], 3)
        self.assertAlmostEqual(s["three"]["energy"], 1200.0)                      # MWh per MW a year


class ThePage(unittest.TestCase):
    def test_in_review_with_its_own_line_and_the_live_tab_untouched(self):
        rel = src("site", "lib", "release.ts")
        self.assertRegex(rel, r'"/cost-of-power/seller/v2":\s*"review"')          # without it the page would take the live tab's status
        self.assertRegex(rel, r'"/cost-of-power/seller":\s*"review"')            # session 126: the tab itself went to review on 5 October 2026 (the owner's instruction)
        out = node("const r = await import('./lib/release.ts'); console.log(JSON.stringify([r.statusOf('/cost-of-power/seller/v2'), r.statusOf('/cost-of-power/seller/v2?iso=caiso'), r.statusOf('/cost-of-power/seller')]));")
        self.assertEqual(out, ["review", "review", "review"])
        page = src("site", "app", "_retired", "seller-v2", "page.tsx")
        for piece in ("ToolPage", "ToolHeader", "InputPanel", "HeadlineRow", "ChartFrame", "ToolSection", "ToolTable", "Fold", "SourceLine"):
            self.assertIn(f"<{piece}", page)
        self.assertIn("Last twelve months", page)
        self.assertEqual(page.count("Long-run average, a year"), 2)                # both averages are labeled as long-run averages
        self.assertIn("Incomplete year", page)
        one = src("site", "app", "cost-of-power", "seller", "page.tsx")   # session 145: the one page holds the same pieces
        for piece in ("ToolPage", "ToolHeader", "InputPanel", "HeadlineRow", "ChartFrame", "ToolSection", "ToolTable", "Fold", "SourceLine"):
            self.assertIn(f"<{piece}", one)
        self.assertEqual(one.count("Long-run average, a year"), 2)
        self.assertIn("Incomplete year", one)
        self.assertIn('{ source: "/cost-of-power/seller/v2", destination: "/cost-of-power/seller", permanent: true }', src("site", "next.config.ts"))
        r = subprocess.run(["git", "log", "--format=%s", "-1", "--", "site/app/cost-of-power/seller/page.tsx", "site/lib/merchant.ts", "site/data/merchant_snapshot.json"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertNotIn("Session 107", r.stdout)

    def test_no_em_dash(self):
        for rel in ("site/lib/seller2.ts", "site/app/_retired/seller-v2/page.tsx", "site/app/cost-of-power/seller/page.tsx", "tests/test_session107.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
