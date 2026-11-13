"""Session 1893: session 1885's fault 1 on the generator page (docs/reviews/trader-path.md, "Walked 13 November 2026").

The fault, as session 1885 wrote it: "Generator page, steps 01 to 06: the headline mixes two twelve-month windows.
Revenue and coverage are 'Oct 2025 to Sep 2026', the capture card 'Nov 2025 to Oct 2026'; the spans table gives 23.20
against 32.10 for the same 'last twelve months' the card gives as 23.21 against 32.48; the capture chart says '2026, 10
months', the revenue chart '9 months'. Should: one window on the face (the model's months, or both moved together)."
Step 06 adds that the PPA results table's capture row read "real time, Nov 2025 to Oct 2026" beside the contract row's
"Oct 2025 to Sep 2026".

The fix, the first of the two the chain file offers: the capture file (data/seller/capture.json) holds months, so its
figures can be taken over the model's. Where it holds a month after the last month of the model's last twelve months,
every capture figure on the page takes its months up to that month (lib/capture.ts, upTo and cutHub; model.ts, capCut):
the card, the summary sentence, the results table's capture row (facts.capture.words), the capture chart and the table of
every hub, and tables.csv. Each figure's check key ends "@<that month>", and lib/capture.ts stat reads it, so
check-values recomputes the same months. Where the capture file ends first, nothing is cut and the card names both
windows in words (capWords). On the page data of this branch, ERCOT's hub average, real time, solar: 23.27 against
32.17, October 2025 to September 2026 (23.21 against 32.48, November 2025 to October 2026, before).

No network, no model, no browser. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SELLER = ("site", "app", "cost-of-power", "seller")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def node_ok():
    return bool(shutil.which("node")) and os.path.isdir(os.path.join(SITE, "node_modules", "typescript"))


def run_node(script):
    r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                       capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    return r


class TheCaptureLibraryCutsAtAMonth(unittest.TestCase):
    def test_the_library_holds_upTo_cutHub_and_the_key_reads_the_cut(self):
        s = src("site", "lib", "capture.ts")
        self.assertIn("export function upTo(months: Months | undefined, last: string | null | undefined): Months | undefined {", s)
        self.assertIn("return Object.fromEntries(Object.entries(months).filter(([m]) => m <= last));", s)
        self.assertIn("export function cutHub(h: Hub, last: string | null | undefined): Hub {", s)
        self.assertIn('const [base, last] = span.split("@");', s)
        self.assertIn("const months = upTo(h[market]?.[fuel], last);", s)
        self.assertIn("session 1885's fault 1", s)

    @unittest.skipUnless(node_ok(), "node or the site's packages are not here")
    def test_a_cut_takes_the_months_up_to_the_last_and_the_key_agrees(self):
        script = """
const C = await import('./lib/capture.ts');
// thirteen months, September 2025 to September 2026, each 720 hours at a flat 30 with generation 10 an hour, priced 20
const rec = (p) => [720, 720, 720 * 30, 7200, 7200 * p];
const months = {};
for (let i = 0; i < 14; i++) { const d = new Date(Date.UTC(2025, 8 + i, 1)); months[d.toISOString().slice(0, 7)] = rec(i === 13 ? 50 : 20); }
const h = { id: 'HB_X', entity: 'x:HB_X', rt: { basis: '', tables: [], first: '2025-09-01', last: '2026-10-31', hours: 0, solar: months } };
const file = { built: '', method: '', near: 0.95, tables: [], grids: { g: { name: 'G', tz: '', main: 'HB_X', workbook: '', generation: [], mix_first: '', mix_last: '', hubs: [h] } }, blank: {} };
const raw = C.twelve(h.rt.solar, 0.95), cut = C.twelve(C.cutHub(h, '2026-09').rt.solar, 0.95);
process.stdout.write(JSON.stringify({
  raw: [raw.from, raw.to, raw.price], cut: [cut.from, cut.to, cut.price],
  same: C.cutHub(h, '2026-10') === h, none: C.cutHub(h, null) === h, after: [C.after(h, '2026-09'), C.after(h, '2026-10')],
  keyRaw: C.stat(file, 'g', 'HB_X', 'rt', 'solar', 'l12', 'price'), keyCut: C.stat(file, 'g', 'HB_X', 'rt', 'solar', 'l12@2026-09', 'price'),
  yearRaw: C.stat(file, 'g', 'HB_X', 'rt', 'solar', '2026', 'price'), yearCut: C.stat(file, 'g', 'HB_X', 'rt', 'solar', '2026@2026-09', 'price'),
  monthsCut: C.years(C.cutHub(h, '2026-09').rt.solar, 0.95).at(-1).months, monthsRaw: C.years(h.rt.solar, 0.95).at(-1).months,
  untouched: Object.keys(h.rt.solar).length }));
"""
        r = run_node(script)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["raw"][:2], ["2025-11", "2026-10"])
        self.assertEqual(d["cut"], ["2025-10", "2026-09", 20])
        self.assertAlmostEqual(d["raw"][2], (11 * 20 + 50) / 12)
        self.assertTrue(d["same"])
        self.assertTrue(d["none"])
        self.assertEqual(d["after"], [True, False])
        self.assertAlmostEqual(d["keyRaw"], d["raw"][2])
        self.assertEqual(d["keyCut"], 20)
        self.assertEqual((d["monthsRaw"], d["monthsCut"]), (10, 9))
        self.assertNotEqual(d["yearRaw"], d["yearCut"])
        self.assertEqual(d["yearCut"], 20)
        # the file's own months are not changed by a cut
        self.assertEqual(d["untouched"], 14)

    @unittest.skipUnless(node_ok(), "node or the site's packages are not here")
    def test_on_the_page_data_the_capture_takes_the_models_window(self):
        script = """
import fs from 'node:fs';
const C = await import('./lib/capture.ts'); const M = await import('./lib/merchant.ts'); const S = await import('./lib/seller2.ts');
const F = JSON.parse(fs.readFileSync('data/seller/capture.json', 'utf-8')); const snap = JSON.parse(fs.readFileSync('data/merchant_snapshot.json', 'utf-8'));
const out = [];
for (const iso of ['ercot', 'caiso']) for (const asset of ['solar', 'wind']) {
  const x = M.inputsOf({ iso, asset }); const ms1 = M.months(snap, { ...x, mw: 1, mwh: 0, ds: 0, fom: 0 }); const s = S.spans(ms1);
  if (!s.twelve) continue;
  const g = F.grids[iso], h = g.hubs.find((h) => h.id === g.main);
  const cut = g.hubs.some((k) => C.after(k, s.twelve.to)) ? s.twelve.to : null;
  const ch = C.cutHub(h, cut);
  const m = ch.rt && C.twelve(ch.rt[asset], F.near) ? 'rt' : 'da';
  const t = C.twelve(ch[m][asset], F.near);
  out.push({ iso, asset, model: [s.twelve.from, s.twelve.to], cap: t ? [t.from, t.to] : null, cut,
    key: t ? C.stat(F, iso, h.id, m, asset, cut ? `l12@${cut}` : 'l12', 'price') === t.price : null,
    y: [S.years(ms1).at(-1).y, S.years(ms1).at(-1).months], cy: (() => { const y = C.years(ch[m][asset], F.near).at(-1); return [y.y, y.months]; })() });
}
process.stdout.write(JSON.stringify(out));
"""
        r = run_node(script)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(r.stdout)
        self.assertGreaterEqual(len(rows), 2)
        for o in rows:
            what = f"{o['iso']} {o['asset']}"
            if o["cut"]:
                # the capture file held months after the model's: cut, the card's window is the revenue's
                self.assertEqual(o["cap"], o["model"], what)
                self.assertTrue(o["key"], what)
                # the capture chart's newest year counts no month the revenue chart does not
                if o["cy"][0] == o["y"][0]:
                    self.assertLessEqual(o["cy"][1], o["y"][1], what)
            # else the capture file ends first: the card names both windows (capWords)


class ThePageAndTheDownloadUseTheCut(unittest.TestCase):
    def test_the_model_cuts_at_the_models_last_month(self):
        m = src(*SELLER, "model.ts")
        self.assertIn("const capCut = fuel && s.twelve && cg.hubs.some((h) => after(h, s.twelve!.to)) ? s.twelve.to : null;", m)
        self.assertIn("const capHubs = cg.hubs.map((h) => cutHub(h, capCut));", m)
        self.assertIn("const capHub = capHubs.find((h) => h.id === hub.id) ?? hub;", m)
        self.assertIn("const capSpan = (span: string) => (capCut ? `${span}@${capCut}` : span);", m)
        self.assertIn("const mk: Market = marketOf(capHub);", m)
        self.assertIn("const mine = fuel ? cap(capHub, fuel, mk) : null;", m)
        self.assertIn("captureYears(capHub[m]?.[f], NEAR)", m)
        self.assertIn('const l12 = { solar: cap(capHub, "solar", m), wind: cap(capHub, "wind", m) };', m)
        view = m[m.index("const capView = "):m.index("// (b) the contract's twelve months")]
        self.assertIn("for (const h of capHubs) for (const k of Object.keys(h[marketOf(h)]?.[fuel] ?? {}))", view)
        self.assertIn("const rows: CapRow[] = capHubs.map((h) => {", view)
        self.assertIn("const window = fuel ? captureTwelve(capHub[mk]?.[fuel], NEAR) : null;", m)
        # the results table's capture row and the card read one string; both windows in words only when they still differ
        self.assertIn("words: capWords } : null", m)
        self.assertIn("; the revenue's twelve months are ${shortMonth(s.twelve.from)} to ${shortMonth(s.twelve.to)}", m)

    def test_the_page_keys_the_cut_and_writes_the_one_window(self):
        p = src(*SELLER, "page.tsx")
        self.assertIn("${capView.fuel}|${capSpan(span)}|${what}`", p)
        self.assertIn('|${capSpan("l12")}|${what}`;', p)
        self.assertIn("percent</>}; {capWords}</> : null} />", p)
        self.assertNotIn("{shortMonth(mine.from)} to {shortMonth(mine.to)}", p)
        self.assertNotIn("why(hub, fuel, mk)", p)
        self.assertEqual(p.count("why(capHub, fuel, mk)"), 2)
        # the results table's row is the facts' words (SellerScenarios.tsx, unchanged)
        self.assertIn("note: `a capture rate of ${num(f.capture.ratio, 1)} percent of USD ${num(f.capture.flat)}; ${f.capture.words}` }", src(*SELLER, "SellerScenarios.tsx"))

    def test_tables_csv_takes_the_same_hubs(self):
        t = src(*SELLER, "tables.csv", "route.ts")
        self.assertIn("for (const h of capHubs) {", t)
        self.assertIn("why(capHub, fu, m)", t)
        self.assertIn("take the capture file's months up to ${capCut}, the last month of the model's last twelve months", t)

    def test_no_dash_in_the_files_written(self):
        for p in (("site", "lib", "capture.ts"), SELLER + ("model.ts",), SELLER + ("page.tsx",), SELLER + ("tables.csv", "route.ts"),
                  ("tests", "test_session1893.py"), ("tests", "test_session264.py")):
            s = src(*p)
            self.assertEqual(s.count(chr(0x2014)) + s.count(chr(0x2013)), 0, "/".join(p))


if __name__ == "__main__":
    unittest.main()
