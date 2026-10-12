"""Session 190: "What a datacenter pays" (/cost-of-power), correctness. What is held to, beside the replication
(tests/test_session190_replication.py):

  the note     docs/methods/datacenter_pays_algorithm.md states the default case's figures and the flexible example's
               as the page's own library computes them from the page's own files (node; skipped where node is
               absent), while the page's last twelve months are still the ones it was written for; its worked table
               adds up by hand; it names its downloads and ends with its sign-off block;
  the page     links the note beside the Method note and offers the three downloads in its source line; its status
               in site/lib/release.ts is unchanged (review), the note's is review, and no page is live; the route
               check asks for the note's address;
  the tab      reads "What a datacenter pays" on all three pages of the cost of power (session 138's item, held back
               by the freeze of 3 to 7 October 2026);
  the run      the data machine's run exports the CSV again after it rebuilds the page's files, and commits it.

No request, no model call, no table of warehouse/output. The environment is read, never set."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
NOTE = os.path.join(ROOT, "docs", "methods", "datacenter_pays_algorithm.md")
WINDOW = ["2025-10", "2026-09"]
FILES = ["docs/methods/datacenter_pays_algorithm.md", "tests/test_session190.py", "archive/sessions/SESSION_190_REPORT.md", "site/app/cost-of-power/page.tsx",
         "site/app/cost-of-power/Tabs.tsx", "warehouse/run_data_machine.sh"]
_KEPT = {}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"),
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


# Session 199 (the owner's ruling of 11 October 2026): the note quotes the page's files built on 10 October 2026, and
# those files are rebuilt every day. Its figures are recomputed here, by the page's own library, from the inputs frozen
# for it (FROZEN, written by site/scripts/freeze-datacenter-note.mjs from that build): the months of a flat load as the
# library made them, and the hours of 2025 and 2026 a flexible load's figures need. Never from the day's files: on 11
# October the day's files gave USD 29.80 "if perfectly foreseen" where the note, rightly for its day, says 29.72. The
# Texas delivery charges are read in place: a session writes that file from the tariffs, no scheduled run does.
FROZEN = "docs/methods/figures/2026-10-10/datacenter_pays_inputs.json"
LIB_JS = """
import fs from "node:fs";
const L = await import("./lib/datacenter.ts");
const Z = JSON.parse(fs.readFileSync("../" + FROZEN, "utf-8"));
const INDEX = Z.index;
const D = JSON.parse(fs.readFileSync("./data/datacenter/texas_delivery.json", "utf-8"));
const x = L.inputsOf({}, INDEX);
const F = Z.years;
const FLAT = { run: "flat", n: 0, pct: 0, shift: 0 }, two = (v) => v.toFixed(2);
const ms = Z.months[`${x.region}/${x.buy}`], l12 = L.lastTwelve(ms), s = L.span(l12), w = L.last36(ms), bad = L.badMonth(w.months);
const hub = Z.months["HB_NORTH/rt"].filter((r) => r.m >= l12[0].m && r.m <= l12[11].m && r.complete), hs = L.span(hub);
const again = L.monthsOf(F, x.region, x.buy, FLAT).filter((r) => r.m >= `${F[1].year}-01`);
const same = JSON.stringify(again) === JSON.stringify(ms.filter((r) => r.m >= `${F[1].year}-01`));
const ranked = [...w.months].sort((a, b) => b.flat / b.held - a.flat / a.held || a.m.localeCompare(b.m));
const flex = (c, buy) => { const a = L.span(L.lastTwelve(L.monthsRuled(F, x.region, buy, c, "forecast").months)), b = L.span(L.lastTwelve(L.monthsRuled(F, x.region, buy, c, "hindsight").months));
  return { flat: two(a.flat), rule: two(a.per), saved: two(a.flat - a.per), down: a.down, energy: a.energy, cost: two(a.cost), seen: two(b.per), seenSaved: two(b.flat - b.per), seenDown: b.down,
    kept: Math.round(100 * (a.flat - a.per) / (b.flat - b.per)) }; };
const c = L.contractResult({ cost: s.cost, energy: s.energy }, x.mw, { share: 50, price: 30 });
console.log(JSON.stringify({ window: [l12[0].m, l12[11].m], built: INDEX.built, region: x.region, buy: x.buy, same, kept: again.length, frozen: [Z.built, Z.note, Z.case],
  held_years: F.map((f) => [f.year, Object.keys(f.regions), Object.keys(f.regions[x.region])]),
  months: l12.map((r) => [r.m, r.held, two(r.flat), two(r.flat / r.held)]), held: s.held, cost: two(s.cost), per: two(s.per), costText: L.usdShort(s.cost * x.mw), mwh: L.whole(s.energy * x.mw),
  gpu: L.gpuHour(s.per, x.gpu, x.pue).toFixed(4), gpus: L.whole(L.gpus(x.mw, x.gpu, x.pue)), hub: two(hs.flat), hubCost: two(hs.cost), above: two(s.flat - hs.flat),
  bad: [bad.m, two(bad.cost / bad.energy), L.usdShort(bad.cost * x.mw)], n36: w.months.length, top: ranked.slice(0, 4).map((r) => two(r.flat / r.held)), low: [ranked.at(-1).m, two(ranked.at(-1).flat / ranked.at(-1).held)],
  years: L.years(ms).map((r) => two(r.flat)), off100: flex({ run: "hours", n: 100, pct: 0, shift: 0 }, "rt"), off100da: flex({ run: "hours", n: 100, pct: 0, shift: 0 }, "da"),
  shift: flex({ run: "shift", n: 0, pct: 0, shift: 20 }, "rt"), shiftda: flex({ run: "shift", n: 0, pct: 0, shift: 20 }, "da"), k100: L.shedRank({ run: "hours", n: 100, pct: 0, shift: 0 }, 720),
  k5: L.shedRank({ run: "share", n: 0, pct: 5, shift: 0 }, 720), b5: [L.shedBudget({ run: "share", n: 0, pct: 5, shift: 0 }, 8760), L.shedBudget({ run: "share", n: 0, pct: 5, shift: 0 }, 8784)],
  contract: [Math.round(c.contracted), c.market.toFixed(2), c.total.toFixed(2), two(c.per)], tight: INDEX.grids.ercot.demand["2025"],
  tcrf: D.rows.filter((r) => (r.kind ?? "transmission") === "transmission" && /4CP\\s*kW/i.test(r.unit) && r.value > 0).map((r) => [r.utility, String(r.value), two(r.value * 12000 / 8760)]),
  matrix: D.matrix.filter((r) => r.quantity === "postage_stamp_rate" && r.matrix !== "B").map((r) => [r.year, r.value.toFixed(6), two(r.value * 1000 / 8760), r.status]) }));
"""


def library():
    if "lib" not in _KEPT:
        _KEPT["lib"] = node(f"const FROZEN = {json.dumps(FROZEN)};" + LIB_JS)
    return _KEPT["lib"]


def thousands(text):
    """A figure of the library as the note writes it: 23207.95 as 23,207.95."""
    return f"{float(text):,.2f}"


class TheNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "datacenter_pays_algorithm.md")

    def test_it_is_written_for_sign_off_and_names_its_downloads(self):
        n = self.note
        self.assertTrue(n.startswith("# What a datacenter pays: every number, step by step\n"))
        self.assertIn("Written for sign-off. Page: `/cost-of-power`.", n)
        for f in ("erw_2026_datacenter_hourly.csv", "erw_2026_datacenter_replication.do", "erw_2026_datacenter_replication.py"):
            self.assertIn(f"(/datacenter/{f})", n)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "site", "public", "datacenter", f)), f)
        self.assertIn("**It has never been run: Stata is not on this machine.**", n)
        self.assertNotIn(EM, n)
        heads = re.findall(r"(?m)^## (.+)$", n)
        self.assertEqual(heads, ["1. The order of computation", "2. The reader's inputs", "3. The price of an hour", "4. Every number on the page, in the order the page shows it",
                                 "5. A load that is not flat", "6. Edge cases, as the code handles them", "7. Assumptions, their defaults and sources", "8. The replication",
                                 "9. Where the notes and the code differ", "10. What is left, for your ruling", "11. Findings of this session", "Sign-off", "Checks"])
        block = n.split("## Sign-off", 1)[1].split("## Checks", 1)[0]
        for line in ("- Signed off by:", "- Date:", "- Items of section 10 ruled, and how:"):
            self.assertIn(line, block)
        # every headline number has its own part, in page order
        order = [n.index(h) for h in ("### 4.2 The summary sentence", "### 4.3 Headline 1", "### 4.4 Headline 2", "### 4.5 Headline 3", "### 4.6 The chart",
                                      "### 4.7 Will the power be there", "### 4.8 How clean", "### 4.9 How soon", "### 4.10 With your contract")]
        self.assertEqual(order, sorted(order))
        self.assertEqual(len(re.findall(r"(?m)^\d+\. \*\*", n.split("## 6. Edge cases", 1)[1].split("## 7.", 1)[0])), 20)
        self.assertEqual(len(re.findall(r"(?m)^\| \d+ \|", n.split("## 10. What is left", 1)[1].split("## 11.", 1)[0])), 16)

    def test_the_worked_table_adds_up_by_hand(self):
        rows = re.findall(r"(?m)^\| (20\d\d-\d\d) \| (\d+) \| ([\d,]+\.\d\d) \| (\d+\.\d\d) \|$", self.note)
        self.assertEqual(len(rows), 12)
        hours, usd = sum(int(r[1]) for r in rows), sum(float(r[2].replace(",", "")) for r in rows)
        for m, h, s, per in rows:
            self.assertEqual(f"{float(s.replace(',', '')) / int(h):.2f}", per, m)
        total = re.search(r"(?m)^\| \*\*Twelve months\*\* \| \*\*([\d,]+)\*\* \| \*\*([\d,]+\.\d\d)\*\* \| \*\*(\d+\.\d\d)\*\* \|$", self.note)
        self.assertEqual((int(total.group(1).replace(",", "")), total.group(2), total.group(3)), (hours, f"{usd:,.2f}", f"{usd / hours:.2f}"))
        self.assertIn(f"{usd:,.2f} / {hours:,} = {usd / hours:.4f}", self.note)
        self.assertIn(f"USD {usd * 100:,.0f}", self.note)
        # the per GPU-hour arithmetic and the GPU count, as the note works them
        self.assertIn(f"{usd / hours:.4f} x 1.3 x 1.56 / 1,000 = {usd / hours * 1.3 * 1.56 / 1000:.6f}", self.note)
        self.assertIn(f"100,000 / 2.028 = {100000 / 2.028:,.0f}", self.note)

    def test_the_frozen_inputs_are_the_notes_and_small(self):
        n = self.note
        # the note says which day's files it quotes, and names the file that keeps what its figures need of them
        self.assertIn("With the page's files built on 10 October 2026 the page shows:", n)
        self.assertIn(f"`{FROZEN}`", n)
        self.assertEqual(FROZEN.split("/")[3], "2026-10-10")
        with open(os.path.join(ROOT, *FROZEN.split("/")), encoding="utf-8") as f:
            text = f.read()
        z = json.loads(text)
        self.assertEqual((z["built"][:10], z["note"], z["index"]["built"]), ("2026-10-10", "docs/methods/datacenter_pays_algorithm.md", z["built"]))
        self.assertEqual(z["case"], {"grid": "ercot", "region": "LZ_NORTH", "buy": "rt", "hub": "HB_NORTH", "last_twelve": WINDOW})
        self.assertLess(len(text), 300000)                       # kilobytes: the twelve files of the grid hold 15 MB
        self.assertNotIn(EM, text)
        # the default case alone: one zone, its months, and the hours of the two calendar years the twelve months lie in
        self.assertEqual(sorted(z["months"]), ["HB_NORTH/rt", "LZ_NORTH/rt"])
        self.assertEqual([m["m"] for m in z["months"]["HB_NORTH/rt"]], [f"2025-{k:02d}" for k in (10, 11, 12)] + [f"2026-{k:02d}" for k in range(1, 10)])
        self.assertEqual([(f["year"], list(f["regions"]), sorted(f["regions"]["LZ_NORTH"])) for f in z["years"]],
                         [(2024, ["LZ_NORTH"], ["da"]), (2025, ["LZ_NORTH"], ["da", "rt"]), (2026, ["LZ_NORTH"], ["da", "rt"])])
        tail = z["years"][0]["regions"]["LZ_NORTH"]["da"]
        self.assertEqual((tail["s"], len(tail["v"])), (8784 - 720, 720))            # the 30 days before 2025, for the rule's first thresholds
        script = src("site", "scripts", "freeze-datacenter-note.mjs")
        self.assertIn("if (whole !== kept) throw new Error(", script)               # the kept hours gave the whole files' figures, or nothing was written
        self.assertNotIn(EM, script)

    def test_its_figures_are_the_librarys_on_the_files_it_quotes(self):
        lib = library()
        # the frozen inputs are the note's own window, and their hours give their months (node; skipped where node is absent)
        self.assertEqual(lib["window"], WINDOW)
        self.assertEqual((lib["region"], lib["buy"], lib["built"][:10]), ("LZ_NORTH", "rt", "2026-10-10"))
        self.assertTrue(lib["same"])
        self.assertEqual(lib["kept"], 22)                         # January 2025 to October 2026
        n = self.note
        for m, held, flat, per in lib["months"]:
            self.assertIn(f"| {m} | {held} | {thousands(flat)} | {per} |", n)
        for words in (f"USD {lib['per']} per MWh over the last twelve months (October 2025 to September 2026), USD {lib['costText']} for {lib['mwh']} MWh",
                      f"a bad month of USD {lib['bad'][1]} per MWh (August 2026, of {lib['n36']} months)", f"USD {lib['gpu']} per GPU-hour, {lib['gpus']} GPUs",
                      f"the hub beside the zone (`HB_NORTH`) at USD {lib['hub']}, so the zone is {lib['above']} above its hub",
                      f"`HB_NORTH` {thousands(lib['hubCost'])} / {lib['held']:,} = {lib['hub']}; {lib['per']} - {lib['hub']} = {lib['above']} above",
                      f"January 2026 ({lib['top'][0]}), September 2026 ({lib['top'][1]}), April 2026 ({lib['top'][2]}), **August 2026 ({lib['top'][3]})**",
                      f"The cheapest of the 36 was February 2024 ({lib['low'][1]})", f'shown "{lib["bad"][2]}"'):
            self.assertIn(words, n)
        self.assertEqual((lib["bad"][0], lib["low"][0]), ("2026-08", "2024-02"))
        y = lib["years"]
        self.assertIn(f"Default: {y[0]} (2015), {', '.join(y[1:6])}, {y[6]} (2021, Winter Storm Uri), {', '.join(y[7:10])}, {y[10]} (2025), and {y[11]} for the nine months of 2026.", n)
        self.assertIn("| By year, 2015 to 2026 | " + ", ".join(y) + " | the same |", n)
        f, d, s, sd = lib["off100"], lib["off100da"], lib["shift"], lib["shiftda"]
        for words in (f"The page shows USD {f['rule']} per MWh, {f['saved']} less than a flat load, and USD {f['seen']} \"if perfectly foreseen\" ({f['seenSaved']} less).",
                      f"hold {f['down']} hours off, all of 2026 (none of October to December 2025): cost {thousands(f['cost'])} over {f['energy']:,.0f} MWh = **{f['rule']}** per MWh, against {f['flat']} flat: {f['saved']} less.",
                      f"**Foreseen:** {f['seenDown']} hours off in the same twelve months", f"**{f['seen']}**, {f['seenSaved']} less. \"The rule kept {f['kept']} percent of it.\"",
                      f"Bought day-ahead: {d['rule']} against {d['flat']} flat; foreseen {d['seen']}. Shifting 20 percent, real time: {s['rule']}, foreseen {s['seen']}; bought day-ahead: {sd['rule']} both"):
            self.assertIn(words, n)
        self.assertEqual(sd["rule"], sd["seen"])
        self.assertEqual((lib["k100"], lib["k5"], lib["b5"]), (8, 36, [438, 439]))
        self.assertIn("round(8.22) = 8. For 5 percent: 36.", n)
        self.assertIn("438 for 5 percent (439 in a leap year)", n)
        c = lib["contract"]
        self.assertIn(f"0.5 x 876,000 x 30 = {c[0]:,}; 0.5 x 29,546,505 = {float(c[1]):,.2f}; together USD {float(c[2]):,.2f}, or {c[3]} per MWh against {lib['per']}", n)
        t = lib["tight"]
        self.assertIn(f"Default: 2025, peak {t['peak_mw']:,.0f} MW, {t['tight_hours']} tight hours.", n)
        tcrf = {u: (v, per) for u, v, per in lib["tcrf"]}
        self.assertIn(f"Oncor {tcrf['Oncor'][0]} gives {tcrf['Oncor'][1]}; AEP Texas {tcrf['AEP Texas'][0]} gives {tcrf['AEP Texas'][1]}", n)
        self.assertEqual(sorted(tcrf), ["AEP Texas", "Oncor"])
        m = {y: (v, per, status) for y, v, per, status in lib["matrix"]}
        self.assertIn(f"{m['2025'][0]} gives {m['2025'][1]} (2025, approved); {m['2026'][0]} gives {m['2026'][1]} (2026, filed, not approved)", n)
        self.assertEqual((m["2025"][2], m["2026"][2]), ("approved", "filed"))

    def test_it_states_the_code_rules_it_describes(self):
        lib, builder, reader = src("site", "lib", "datacenter.ts"), src("warehouse", "derived", "datacenter_page.py"), src("warehouse", "derived", "price_compare.py")
        for words in ("export const NEAR = 0.95;", "export const PRIOR_DAYS = 30;", "if (g < span30 || prior.length < NEAR * span30) { out.push(null); continue; }",
                      "return Math.min(held, Math.max(1, Math.round(q * held)));", "export const shedBudget = (x: Flex, hours: number) => Math.round(shedShare(x) * hours);",
                      "const k = Math.min(held.length, Math.round(x.run === \"hours\" ? (x.n * held.length) / p.length : (x.pct / 100) * held.length));",
                      "return sorted.length ? sorted[Math.max(0, Math.ceil(0.1 * sorted.length) - 1)] : null;", "const to = (lastTwelve(ms)?.[11] ?? done[done.length - 1]).m, from = prev(to, 35);",
                      "export const gpuHour = (perMwh: number, gpuKw: number, pue: number) => (perMwh * gpuKw * pue) / 1000;"):
            self.assertIn(words, lib)
        for words in ("TIGHT = 0.95", "NEAR_DEMAND = 0.95", 'FIRST = "2015-01-01"', "vals = np.round(h.values.astype(float), 2)", "return np.where(np.isnan(new), old, new)",
                      'HELD_INTERNAL = ["isone_zone_prices_history"]', '"ercot": dict(name="ERCOT", std=6, main="LZ_NORTH"'):
            self.assertIn(words, builder)
        for words in ("return g.mean()[g.size() == 4]", 'x = x.sort_values("rank").drop_duplicates(["entity", "side", "freq", "ts"], keep="first")', 'DAM_VARS = {"lmp_dam", "spp_dam"}'):
            self.assertIn(words, reader)
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("two((tcrf.value * 12000) / 8760)", page)
        self.assertIn("two((r.value * 1000) / 8760)", page)
        # the finding of section 11: the two budgets of a year held in part are as the note says they are
        self.assertIn("let left = cap ? shedBudget(x, pay[y].length) : Infinity;", lib)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src("site", "app", "cost-of-power", "page.tsx")

    def test_the_lead_links_the_note_and_the_source_line_offers_the_three_downloads(self):
        p = self.page
        self.assertIn('const ALGORITHM = "/data/methods/datacenter_pays_algorithm";', p)
        self.assertIn("<Link href={METHOD}>Method note</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.</>}", p)
        for f in ("erw_2026_datacenter_hourly.csv", "erw_2026_datacenter_replication.do", "erw_2026_datacenter_replication.py"):
            self.assertIn(f'"/datacenter/{f}"', p)
        self.assertIn('The default case hour by hour: <a href={HOURLY_CSV} download data-download="csv">CSV</a>, <a href={DO_FILE} download data-download="do">Stata do-file</a>, '
                      '<a href={MIRROR} download data-download="py">Python mirror</a>.', p)
        self.assertEqual(p.count("download data-download="), 3)

    def test_the_status_is_unchanged_and_the_note_is_in_review(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power": "review",', rel)
        self.assertIn('"/data/methods/datacenter_pays_algorithm": "review"', rel)
        self.assertEqual(re.findall(r'"(/[^"]*)": "live"', rel), [])
        self.assertIn('"/data/methods/datacenter_pays_algorithm"', src("site", "scripts", "check-routes.mjs"))

    def test_the_three_tabs_read_alike(self):
        tabs = src("site", "app", "cost-of-power", "Tabs.tsx")
        self.assertIn('{tab("/cost-of-power", LABEL, active === "buy")}', tabs)
        self.assertEqual(tabs.count('LABEL = "What a datacenter pays"'), 1)
        self.assertNotIn('"What power costs to buy"', tabs.split("const LABEL", 1)[1])
        for page in (("site", "app", "cost-of-power", "page.tsx"), ("site", "app", "cost-of-power", "seller", "page.tsx"), ("site", "app", "cost-of-power", "battery", "page.tsx")):
            self.assertIn("<CostTabs active=", src(*page), page[-2])


class TheDataMachinesRun(unittest.TestCase):
    def test_it_exports_the_csv_after_the_files_are_final_and_commits_it(self):
        text = src("warehouse", "run_data_machine.sh")
        step = 'soft_step dm_datacenter_export "$PYTHON" warehouse/derived/datacenter_hourly_export.py'
        self.assertIn(step, text)
        self.assertGreater(text.index(step), text.index('soft_step dm_datacenter_page "$PYTHON" warehouse/derived/datacenter_page.py'))
        self.assertGreater(text.index(step), text.index("put_back dm_datacenter_page site/data/datacenter"))
        self.assertGreater(text.index(step), text.index("page_test dm_test_datacenter test-datacenter-rule.mjs site/data/datacenter"))
        self.assertLess(text.index(step), text.index("# ---- 4. the commit"))
        paths = text.split("PAGE_PATHS=(", 1)[1].split(")", 1)[0]
        self.assertIn("site/public/datacenter/erw_2026_datacenter_hourly.csv", paths)
        # no workflow runs the exporter: the runner's Saturday build adds hours of other regions and of the hubs' newest days
        for name in os.listdir(os.path.join(ROOT, ".github", "workflows")):
            self.assertNotIn("datacenter_hourly_export", src(".github", "workflows", name), name)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_was_written(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            self.assertTrue(os.path.exists(p), f)
            with open(p, encoding="utf-8") as fh:
                self.assertNotIn(EM, fh.read(), f)

    def test_the_report_is_in_the_chains_shape(self):
        r = src("archive", "sessions", "SESSION_190_REPORT.md")
        for head in ("## Read these first", "## What to review", "## What is left, item by item", "## Decisions made without you", "## Pulls and spend", "## Checks run",
                     "## Numbers on the page, before and after", "## Landing"):
            self.assertIn(head + "\n", r)
        first = r.split("## Read these first", 1)[1].split("\n## ", 1)[0]
        self.assertLessEqual(len(re.findall(r"(?m)^- ", first)), 5)
        self.assertIn("https://erw-flame.vercel.app/cost-of-power", r)


if __name__ == "__main__":
    unittest.main()
