"""Session 88: what a battery saves a customer (/battery/customer, in review).

Energy Research Warehouse (ERW). The page reads no ERW table: it is arithmetic on what the reader types, in the reader's
browser. These tests cover the arithmetic (site/lib/customerbattery.ts, run by node), and the claim that nothing typed is
sent or stored, three ways:
    in the code     the calculator and its arithmetic name no way to send or store anything, and import nothing but
                    React and each other
    in node         the arithmetic runs a thousand times with every sending function replaced by a counter: none is called
    in a browser    site/scripts/check-no-request.mjs types into the built page in a real browser and counts its requests;
                    it runs where a built site is being served (the workflow's site step, and by hand), and here when
                    ERW_SITE_URL names such a server

    python -m unittest tests.test_session88 -v
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


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


BASE = "{ peakKw: 500, demandCharge: 18, peakRate: 0.22, offPeakRate: 0.09, batteryKw: 200, batteryKwh: 800, peakHours: 4, days: 22, roundTrip: 85 }"


class Arithmetic(unittest.TestCase):
    def test_the_saving_is_the_peak_shaved_and_the_energy_shifted(self):
        d = node(f"import * as c from './lib/customerbattery.ts'; const s = c.saving({BASE});"
                 "console.log(JSON.stringify({ s, usd: [c.usd(s.monthSaved), c.usd(-12.6), c.usd(0.4)], qty: [c.qty(1234.56, 1), c.qty(800)] }));")
        s = d["s"]
        self.assertEqual((s["shavedKw"], s["limit"], s["demandSaved"], s["demandBefore"]), (200, "power", 3600, 9000))
        self.assertEqual(s["dischargedKwh"], 800)
        self.assertAlmostEqual(s["chargedKwh"], 800 / 0.85, places=6)
        per_day = 800 * 0.22 - 800 / 0.85 * 0.09
        self.assertAlmostEqual(s["shiftPerDay"], per_day, places=6)
        self.assertTrue(s["shifts"])
        self.assertAlmostEqual(s["energySaved"], per_day * 22, places=6)
        self.assertAlmostEqual(s["monthSaved"], 3600 + per_day * 22, places=6)
        self.assertAlmostEqual(s["yearSaved"], 12 * (3600 + per_day * 22), places=6)
        self.assertEqual(s["hours"], 4)
        self.assertEqual(d["usd"], ["$5,608", "-$13", "$0"])
        self.assertEqual(d["qty"], ["1,234.6", "800"])

    def test_what_limits_the_peak_shaved(self):
        d = node("import * as c from './lib/customerbattery.ts';"
                 f"const b = {BASE};"
                 "console.log(JSON.stringify([c.saving({ ...b, batteryKwh: 400 }), c.saving({ ...b, peakKw: 50 }), c.saving({ ...b, peakHours: 1 })]"
                 ".map((s) => [s.shavedKw, s.limit, s.demandSaved])));")
        self.assertEqual(d, [[100, "energy", 1800], [50, "peak", 900], [200, "power", 3600]])

    def test_when_shifting_does_not_pay_the_battery_runs_for_the_peak_only_and_the_loss_is_counted(self):
        d = node("import * as c from './lib/customerbattery.ts';"
                 f"console.log(JSON.stringify(c.saving({{ ...{BASE}, peakRate: 0.10, batteryKwh: 1600 }})));")
        self.assertFalse(d["shifts"])
        self.assertLess(d["shiftPerDay"], 0)
        self.assertEqual(d["cyclesForPeak"], 800)                          # 200 kW through a 4 hour peak, not the whole 1,600 kWh
        cost = (800 * 0.10 - 800 / 0.85 * 0.09) * 22
        self.assertAlmostEqual(d["energySaved"], cost, places=6)
        self.assertLess(d["energySaved"], 0)                               # a cost, shown as one: never rounded up to nothing
        self.assertAlmostEqual(d["monthSaved"], 3600 + cost, places=6)
        self.assertAlmostEqual(d["breakEvenRate"], 0.09 / 0.85, places=9)

    def test_a_field_is_a_number_or_it_is_nothing(self):
        d = node("import * as c from './lib/customerbattery.ts';"
                 "const f = Object.fromEntries(c.FIELDS.map((x) => [x.key, x]));"
                 "const t = (k, v) => c.read(v, f[k]);"
                 "console.log(JSON.stringify({"
                 "ok: [t('peakKw', '1,200'), t('peakRate', '0.25'), t('peakRate', '.5'), t('peakKw', '5.'), t('demandCharge', '0'), t('roundTrip', ' 86 ')],"
                 "bad: [t('peakKw', ''), t('peakKw', 'abc'), t('peakKw', '-5'), t('peakKw', '1e3'), t('peakKw', '12abc'), t('peakKw', '0'), t('peakRate', '25'),"
                 " t('roundTrip', '0'), t('roundTrip', '101'), t('days', '32'), t('peakKw', 'NaN'), t('peakKw', 'Infinity')],"
                 "none: c.readAll({}), some: c.readAll({ peakKw: '500', peakHours: '2', days: '21', roundTrip: '86' }),"
                 "starts: Object.fromEntries(c.FIELDS.filter((x) => x.start).map((x) => [x.key, x.start])) }));")
        self.assertEqual(d["ok"], [1200, 0.25, 0.5, 5, 0, 86])
        self.assertEqual(d["bad"], [None] * 12)
        self.assertEqual(d["none"], {"ok": False, "missing": ["peakKw", "demandCharge", "peakRate", "offPeakRate", "batteryKw", "batteryKwh", "peakHours", "days", "roundTrip"]})
        self.assertEqual(d["some"]["missing"], ["demandCharge", "peakRate", "offPeakRate", "batteryKw", "batteryKwh"])
        # the six fields that are the reader's bill and battery start empty: no number is assumed for them
        self.assertEqual(d["starts"], {"peakHours": "2", "days": "21", "roundTrip": "86"})


SENDERS = ["fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "EventSource", "localStorage", "sessionStorage", "indexedDB", "document.cookie",
           "useRouter", "useSearchParams", "usePathname", "router.", "<form", "action=", "href=", "window.open", "postMessage", "navigator.", "import("]


class NothingIsSent(unittest.TestCase):
    def test_the_calculator_and_its_arithmetic_name_no_way_to_send_or_store(self):
        calc, lib = src("site", "app", "battery", "customer", "Calc.tsx"), src("site", "lib", "customerbattery.ts")
        code = lambda s: "\n".join(ln for ln in s.splitlines() if not ln.strip().startswith("//"))  # noqa: E731
        for name, text in (("Calc.tsx", code(calc)), ("customerbattery.ts", code(lib))):
            for word in SENDERS:
                self.assertNotIn(word, text, f"{name} names {word}")
        self.assertEqual(re.findall(r'^import .* from "([^"]+)";', calc, re.M), ["react", "@/lib/customerbattery"])
        self.assertEqual(re.findall(r"^import ", lib, re.M), [])                # the arithmetic imports nothing
        self.assertIn('"use client"', calc.splitlines()[0])

    def test_the_arithmetic_calls_no_sending_function(self):
        d = node("""
let calls = 0;
const trap = () => { calls += 1; throw new Error('a request was attempted'); };
globalThis.fetch = trap;
globalThis.XMLHttpRequest = class { constructor() { trap(); } };
globalThis.WebSocket = class { constructor() { trap(); } };
globalThis.EventSource = class { constructor() { trap(); } };
Object.defineProperty(globalThis, 'navigator', { value: { sendBeacon: trap }, configurable: true });
const c = await import('./lib/customerbattery.ts');
let n = 0;
for (let i = 1; i <= 1000; i += 1) {
  const text = { peakKw: String(100 + i), demandCharge: String(5 + (i % 30)), peakRate: (0.05 + (i % 40) / 100).toFixed(2), offPeakRate: (0.03 + (i % 9) / 100).toFixed(2),
    batteryKw: String(10 + i), batteryKwh: String(20 + 3 * i), peakHours: String(1 + (i % 6)), days: String(i % 32), roundTrip: String(60 + (i % 41)) };
  const r = c.readAll(text);
  if (r.ok) { const s = c.saving(r.x); c.usd(s.monthSaved); c.qty(s.shavedKw, 1); n += 1; }
}
console.log(JSON.stringify({ calls, n }));
""")
        self.assertEqual(d["calls"], 0)
        self.assertGreater(d["n"], 900)

    def test_the_page_is_static_reads_no_table_and_says_so_plainly(self):
        page = src("site", "app", "battery", "customer", "page.tsx")
        self.assertIn('export const dynamic = "force-static"', page)
        for word in ("supabase", "searchParams", "@/lib/data", "cookies(", "headers("):
            self.assertNotIn(word, "\n".join(ln for ln in page.splitlines() if not ln.strip().startswith("//")), word)
        flat = " ".join(page.split())
        self.assertIn("This page uses your own numbers, not ERW data.", flat)
        self.assertIn("Nothing you type is sent or stored.", flat)
        self.assertIn("Source: none.", flat)
        self.assertIn("robots: { index: false, follow: false }", page)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/battery/customer":\s*"review"')

    def test_the_pages_shared_links_do_not_prefetch(self):
        # the browser proof caught this: with prefetch on, the footer's links fetched their routes when the result made the
        # page taller. Nothing typed was in those requests, but the page says no request, so on this page the links do not prefetch
        link = src("site", "components", "SiteLink.tsx")
        m = re.search(r"export const NO_PREFETCH = \[(.*?)\];", link)
        self.assertIn('"/battery/customer"', m.group(1))

    def test_the_browser_proof_is_part_of_the_sites_checks(self):
        script = src("site", "scripts", "check-no-request.mjs")
        for word in ("Network.requestWillBeSent", "Network.webSocketCreated", "Input.insertText", "localStorage", "document.cookie", "location.href"):
            self.assertIn(word, script)
        self.assertIn("node scripts/check-no-request.mjs http://localhost:3049", src(".github", "workflows", "code-branch.yml"))

    def test_in_a_real_browser_where_a_built_site_is_served(self):
        base = os.environ.get("ERW_SITE_URL")
        exe = shutil.which("node")
        if not base or not exe:
            self.skipTest("ERW_SITE_URL does not name a served build of the site (the workflow's site step runs the proof)")
        r = subprocess.run([exe, "scripts/check-no-request.mjs", base], cwd=SITE, capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-1500:])
        self.assertIn("passed: typing into the page made no request and stored nothing", r.stdout)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for rel in ("site/app/battery/customer/page.tsx", "site/app/battery/customer/Calc.tsx", "site/lib/customerbattery.ts",
                    "site/scripts/check-no-request.mjs", "tests/test_session88.py"):
            self.assertNotIn(chr(0x2014), src(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
