"""Session 7504 (chain 304): What a battery saves a customer (/battery/customer) at the done line.

Energy Research Warehouse (ERW). No network, no model, no warehouse table: the page reads none.

- ThePageDrawn       site/scripts/test-battery-customer-page.mjs: the decisions block drawn to HTML, the calculator drawn
                     with numbers in its fields (a typed number printed as typed: the fault this session fixed), the
                     page as it opens.
- ThePromise         the calculator still imports only React and its arithmetic, and neither it nor the new block names a
                     way to send or store; the page still says what it said.
- TheReplication     replication/battery_customer/: the files are there, the page's figures are the committed ones, every
                     figure is inside its tolerance, the cases are cited, the do-file states what it should print.
- TheNote            docs/methods/battery_customer.md lists the page's choices and the figures the replication prints.

    python -m unittest tests.test_session7504_battery_customer -v
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "battery_customer")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def replicate(*args):
    r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py"), *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
    return r.returncode, r.stdout


def module():
    spec = importlib.util.spec_from_file_location("battery_customer_replicate_7504", os.path.join(REP, "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = lambda *a: subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", *a], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)  # noqa: E731
        cls.page = run("scripts/test-battery-customer-page.mjs")
        cls.figures = run("scripts/battery-customer-figures.mjs", "--check")

    def test_every_check_passes(self):
        self.assertEqual(self.page.returncode, 0, self.page.stdout[-3000:] + self.page.stderr[-1500:])
        self.assertNotIn("FAIL", self.page.stdout)
        m = re.search(r"(\d+) of (\d+) passed", self.page.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 30, self.page.stdout[-500:])

    def test_a_typed_number_is_printed_as_typed(self):
        self.assertRegex(self.page.stdout, r"(?m)^ok   a demand charge of 5\.36 is printed as \$5\.36 beside the \$536 it makes")
        self.assertRegex(self.page.stdout, r"(?m)^ok   a 13\.5 kWh battery is printed as 13\.5 kWh")
        self.assertRegex(self.page.stdout, r"(?m)^ok   whole numbers read as they did")

    def test_the_pages_figures_are_the_committed_ones(self):
        # the calculator drawn again gives the same 331 numbers as replication/battery_customer/page_figures.json
        self.assertEqual(self.figures.returncode, 0, self.figures.stdout[-3000:] + self.figures.stderr[-1500:])
        self.assertIn("page_figures: 331 figures, as committed", self.figures.stdout)
        self.assertNotIn("NOT READ", self.figures.stdout)


SENDERS = ["fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "EventSource", "localStorage", "sessionStorage", "indexedDB", "document.cookie",
           "useRouter", "useSearchParams", "usePathname", "router.", "<form", "action=", "window.open", "postMessage", "navigator.", "import("]


class ThePromise(unittest.TestCase):
    def test_the_calculator_still_imports_only_react_and_its_arithmetic(self):
        calc, lib = src("site", "app", "battery", "customer", "Calc.tsx"), src("site", "lib", "customerbattery.ts")
        self.assertEqual(re.findall(r'^import .* from "([^"]+)";', calc, re.M), ["react", "@/lib/customerbattery"])
        self.assertEqual(re.findall(r"^import ", lib, re.M), [])
        code = lambda s: "\n".join(ln for ln in s.splitlines() if not ln.strip().startswith("//"))  # noqa: E731
        for name, text in (("Calc.tsx", code(calc)), ("customerbattery.ts", code(lib)), ("Decisions.tsx", code(src("site", "app", "battery", "customer", "Decisions.tsx")))):
            for word in SENDERS:
                self.assertNotIn(word, text, f"{name} names {word}")

    def test_the_block_takes_nothing_from_the_reader(self):
        d = src("site", "app", "battery", "customer", "Decisions.tsx")
        for word in ('"use client"', "useState", "useEffect", "onChange", "onClick", "<input", "searchParams"):
            self.assertNotIn(word, d, word)
        self.assertEqual(d.count("href="), 1)                # the method note, and it does not prefetch
        self.assertIn('<Link href="/data/methods/battery_customer" prefetch={false}>', d)
        self.assertEqual(len(re.findall(r"\{ key: \"", d)), 10)
        self.assertNotIn("text-muted", d)                    # defaults and sources are in the tip (the page standard)
        self.assertNotIn("@/lib/decisions", d)               # not appended to the file other tools share

    def test_the_page_says_what_it_said_and_mounts_the_block(self):
        page = src("site", "app", "battery", "customer", "page.tsx")
        flat = " ".join(page.split())
        for words in ("This page uses your own numbers, not ERW data.", "Nothing you type is sent or stored.", "Source: none.", "<Brand noUsage>",
                      'export const dynamic = "force-static"', "<CustomerBatteryDecisions />", "What this assumes", "What it leaves out"):
            self.assertIn(words, flat)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/battery/customer":\s*"review"')     # no page opens to visitors
        m = re.search(r"export const NO_PREFETCH = \[(.*?)\];", src("site", "components", "SiteLink.tsx"))
        self.assertIn('"/battery/customer"', m.group(1))

    def test_a_typed_number_is_no_longer_rounded_in_the_calculator(self):
        calc = src("site", "app", "battery", "customer", "Calc.tsx")
        for old in ("usd(x.demandCharge)", "qty(x.batteryKw)", "qty(x.batteryKwh)", "qty(x.peakKw)", "qty(x.days)", "qty(x.peakHours, 1)", "${f.min} to ${qty(f.max)}"):
            self.assertNotIn(old, calc, old)
        for new in ("rate(x.demandCharge)", "typed(x.batteryKw)", "typed(x.batteryKwh)", "typed(x.peakKw)", "typed(x.days)", "typed(x.peakHours)", "range(f)"):
            self.assertIn(new, calc, new)


class TheReplication(unittest.TestCase):
    def test_the_files_are_there(self):
        for f in ("replicate.py", "replicate.do", "cases.json", "page_figures.json", "page_figures.csv"):
            self.assertTrue(os.path.exists(os.path.join(REP, f)), f)
        for f in ("battery-customer-figures.mjs", "test-battery-customer-page.mjs"):
            self.assertTrue(os.path.exists(os.path.join(SITE, "scripts", f)), f)

    def test_every_figure_is_inside_its_tolerance(self):
        code, out = replicate()
        self.assertEqual(code, 0, out[-2000:])
        self.assertIn("331 of 331 inside the tolerance, 12 cases; computed here and not shown by the page: 0; not replicated here: nothing", out)
        self.assertNotRegex(out, r"(?m) NO$")
        page = json.loads(src("replication", "battery_customer", "page_figures.json"))
        self.assertEqual(page["figures"], sum(len(c["figures"]) for c in page["cases"]))
        self.assertEqual(page["figures"], 331)
        self.assertEqual(len(src("replication", "battery_customer", "page_figures.csv").strip().splitlines()), 332)

    def test_a_wrong_figure_would_be_caught(self):
        # the comparison is not a formality: a page figure moved by one unit of its last digit is outside the tolerance
        m = module()
        cases, page = m.load("cases.json"), m.load("page_figures.json")
        fig = next(f for c in page["cases"] if c["id"] == "srp-e32-summer-peak" for f in c["figures"] if f["key"] == "sum_month")
        fig["value"] += 1
        rows, _extra = m.compare(cases, page)
        self.assertEqual([(r[0], r[1]) for r in rows if not r[5]], [("srp-e32-summer-peak", "sum_month")])

    def test_the_replications_arithmetic_on_hand_cases(self):
        m = module()
        base = {"peakKw": 500.0, "demandCharge": 18.0, "peakRate": 0.22, "offPeakRate": 0.09, "batteryKw": 200.0, "batteryKwh": 800.0, "peakHours": 4.0, "days": 22.0, "roundTrip": 85.0}
        s = m.saving(base)
        per_day = 800 * 0.22 - 800 / 0.85 * 0.09
        self.assertEqual((s["shaved"], s["limit"], s["demand"], s["demand_before"]), (200.0, "the battery's power", 3600.0, 9000.0))
        self.assertAlmostEqual(s["month"], 3600 + per_day * 22, places=9)
        self.assertAlmostEqual(s["year"], 12 * (3600 + per_day * 22), places=9)
        s = m.saving({**base, "batteryKwh": 400.0})
        self.assertEqual((s["shaved"], s["limit"]), (100.0, "the battery's energy"))
        s = m.saving({**base, "peakKw": 50.0})
        self.assertEqual((s["shaved"], s["limit"]), (50.0, "your peak itself"))
        s = m.saving({**base, "peakRate": 0.10, "batteryKwh": 1600.0})                     # moving energy does not pay
        self.assertFalse(s["shifts"])
        self.assertEqual(s["for_peak"], 800.0)
        self.assertAlmostEqual(s["energy"], (800 * 0.10 - 800 / 0.85 * 0.09) * 22, places=9)
        self.assertLess(s["energy"], 0)
        # a typed value is a number or it is nothing
        f = {k: (lo, hi, z) for k, lo, hi, z, _s in m.FIELDS}
        ok = [m.read_field(t, *f[k]) for k, t in (("peakKw", "1,200"), ("peakRate", ".5"), ("peakKw", "5."), ("demandCharge", "0"), ("roundTrip", " 86 "))]
        self.assertEqual(ok, [1200.0, 0.5, 5.0, 0.0, 86.0])
        bad = [m.read_field(t, *f[k]) for k, t in (("peakKw", ""), ("peakKw", "abc"), ("peakKw", "-5"), ("peakKw", "1e3"), ("peakKw", "0"), ("peakRate", "25"),
                                                    ("roundTrip", "0"), ("roundTrip", "101"), ("days", "32"), ("peakKw", "1.2.3"), ("peakKw", "."))]
        self.assertEqual(bad, [None] * 11)

    def test_the_cases_are_real_tariffs_each_cited(self):
        cases = json.loads(src("replication", "battery_customer", "cases.json"))["cases"]
        tariffs = [c for c in cases if c["kind"].startswith("tariff")]
        self.assertGreaterEqual(len(tariffs), 5)
        self.assertGreaterEqual(len({c["utility"] for c in tariffs}), 3)
        self.assertGreaterEqual(len({c["state"] for c in tariffs}), 3)
        for c in tariffs:
            for k in ("document", "url", "effective", "read_utc", "printed", "how_typed", "schedule"):
                self.assertTrue(c.get(k), (c["id"], k))
            self.assertRegex(c["read_utc"], r"^2026-11-16T\d\d:\d\d:\d\dZ$")
            # never a paused or forbidden host
            self.assertIsNone(re.search(r"misoenergy|scc\.virginia\.gov|sec\.gov|icc\.illinois\.gov|puc\.state\.oh\.us|duke-energy", c["url"]), c["id"])
        by = {c["id"]: c for c in cases}
        # what was typed is what the document prints
        for cid in ("seattle-md-city-tou", "seattle-md-downtown-tou", "seattle-lg-city"):
            p, t = by[cid]["printed"], by[cid]["typed"]
            self.assertEqual((float(t["demandCharge"]), float(t["peakRate"]), float(t["offPeakRate"])),
                             (p["peak_demand_usd_per_kw"], p["peak_energy_usd_per_kwh"], p["off_peak_energy_usd_per_kwh"]))
        for cid in ("srp-e32-summer-peak", "srp-e32-summer", "srp-e32-winter"):
            p, t = by[cid]["printed"], by[cid]["typed"]
            self.assertEqual((float(t["demandCharge"]), float(t["peakRate"]), float(t["offPeakRate"])),
                             (p["on_peak_demand_usd_per_kw"], p["on_peak_energy_usd_per_kwh"], p["off_peak_energy_usd_per_kwh"]))
        for cid in ("austin-sv2", "austin-sv3"):
            p, t = by[cid]["printed"], by[cid]["typed"]
            self.assertAlmostEqual(float(t["demandCharge"]), p["demand_usd_per_billed_kw"] + p["regulatory_usd_per_billed_kw"], places=9)
            energy = sum(p[k] for k in ("energy_usd_per_kwh", "power_supply_adjustment_usd_per_kwh", "customer_assistance_usd_per_kwh",
                                        "service_area_lighting_usd_per_kwh", "energy_efficiency_services_usd_per_kwh"))
            self.assertAlmostEqual(float(t["peakRate"]), energy, places=9)
            self.assertEqual(t["peakRate"], t["offPeakRate"])
        p, t = by["sce-tou-gs-2-b-2013-summer"]["printed"], by["sce-tou-gs-2-b-2013-summer"]["typed"]
        self.assertAlmostEqual(float(t["demandCharge"]), p["facility_demand_usd_per_kw"] + p["summer_on_peak_demand_usd_per_kw"], places=9)
        self.assertEqual(by["opens"]["typed"]["peakHours"], "2")
        # the browser proof's case is the one the proof types
        typed = re.search(r"const TYPED = (\{.*?\});", src("site", "scripts", "check-no-request.mjs")).group(1)
        self.assertEqual(json.loads(re.sub(r"(\w+):", r'"\1":', typed)), by["browser-proof"]["typed"])

    def test_the_do_file_states_what_it_should_print(self):
        code, out = replicate("--headline")
        self.assertEqual(code, 0)
        do = src("replication", "battery_customer", "replicate.do")
        lines = [ln for ln in out.strip().splitlines() if ln]
        self.assertEqual(len(lines), 5)
        for ln in lines:
            self.assertIn("*   " + ln, do, ln)
            self.assertIn('display "' + ln.rsplit(": ", 1)[0] + ': "', do, ln)
        # the nine numbers typed in the do-file are the cases'
        cases = {c["id"]: c["typed"] for c in json.loads(src("replication", "battery_customer", "cases.json"))["cases"]}
        m = module()
        for cid, _key, _words in m.HEADLINE:
            t = cases[cid]
            self.assertIn("saving " + " ".join(t[k] for k in ("peakKw", "demandCharge", "peakRate", "offPeakRate", "batteryKw", "batteryKwh", "peakHours", "days", "roundTrip")), do, cid)


class TheNote(unittest.TestCase):
    def test_the_notes_choices_are_the_pages(self):
        note = src("docs", "methods", "battery_customer.md")
        self.assertTrue(note.startswith("# What a battery saves a customer, as a reader meets it"))
        for head in ("## 1. The view", "## 2. The nine fields", "## 3. The arithmetic", "## 4. Every figure the page prints", "## 5. The choices that move a figure",
                     "## 6. What the choices do on real tariffs", "## 7. The cross-check (16 November 2026)", "## 8. The cases and the hosts read", "## 9. The replication",
                     "## 10. What the tool does not hold", "## 11. Tests"):
            self.assertIn(head, note)
        table = note.split("## 5. The choices that move a figure")[1].split("## 6.")[0]
        rows = [ln for ln in table.splitlines() if ln.startswith("| ") and not ln.startswith("| Choice") and not ln.startswith("|---")]
        self.assertEqual(len(rows), 10)
        self.assertIn("lists these 10", table)
        self.assertEqual(len(re.findall(r"\{ key: \"", src("site", "app", "battery", "customer", "Decisions.tsx"))), 10)

    def test_the_notes_figures_are_the_replications(self):
        note = src("docs", "methods", "battery_customer.md")
        self.assertIn("`331 of 331 inside the tolerance, 12 cases; computed here and not shown by the page: 0; not replicated here: nothing`", note)
        code, out = replicate("--seasons")
        self.assertEqual(code, 0)
        self.assertIn("the year by the plan's seasons: 8783.57", out)
        self.assertIn("twelve of srp-e32-summer-peak against the year by seasons: +52.3 percent", out)
        self.assertIn("twelve of srp-e32-winter against the year by seasons: -18.4 percent", out)
        for words in ("USD 8,783.57", "USD 13,376.42: 52.3 percent more", "USD 7,163.97: 18.4 percent less", "USD 1,114.70", "USD 743.05", "USD 597.00"):
            self.assertIn(words, note)
        self.assertIn("52 percent more than the year added by season", src("site", "app", "battery", "customer", "Decisions.tsx"))
        code, out = replicate("--crosscheck")
        self.assertEqual(code, 0)
        self.assertIn("demand saving 2561.90 against the tool's 3014.00", out)
        self.assertIn("sce-tou-gs-2-b-2013-summer: demand charge 30.14 USD per kW; shaved over battery power 1.00; demand saving 3014.00, energy saving 662.97, demand over energy 4.55", out)
        for words in ("USD 3,014.00", "USD 2,561.90", "USD 662.97", "0.94 to 2.06", "USD 23.24", "USD 767.50", "USD 114.52", "USD 4,555.00", "NREL/TP-5400-63162", "NREL/BR-6A20-68963"):
            self.assertIn(words, note)
        ratios = [float(x) for x in re.findall(r"demand over energy (\d+\.\d+)", out)]
        self.assertEqual((min(ratios), sorted(ratios)[-2], max(ratios)), (0.94, 2.06, 4.55))

    def test_no_long_dash_in_what_the_session_wrote(self):
        for parts in (("docs", "methods", "battery_customer.md"), ("docs", "reviews", "battery-customer-faults-2026-11-16.md"),
                      ("site", "app", "battery", "customer", "Decisions.tsx"), ("site", "app", "battery", "customer", "Calc.tsx"),
                      ("site", "app", "battery", "customer", "page.tsx"), ("site", "lib", "customerbattery.ts"),
                      ("site", "scripts", "battery-customer-figures.mjs"), ("site", "scripts", "test-battery-customer-page.mjs"),
                      ("replication", "battery_customer", "replicate.py"), ("replication", "battery_customer", "replicate.do"),
                      ("replication", "battery_customer", "cases.json"), ("replication", "battery_customer", "page_figures.json"),
                      ("tests", "test_session7504_battery_customer.py")):
            text = src(*parts)
            self.assertNotIn(chr(0x2014), text, parts[-1])
            self.assertNotIn(chr(0x2013), text, parts[-1])


if __name__ == "__main__":
    unittest.main()
