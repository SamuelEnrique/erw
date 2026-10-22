"""Session 702: the load profiles' math on the All grids tab (docs/methods/siting.md). On a fixture year of hourly
prices, through lib/datacenter.ts's own functions: a datacenter and heavy industry pay the flat price; flexible compute
is off at or above its strike and in ERCOT's four peak intervals; an electrolyzer runs in the cheapest share of hours
at its load factor, or below a strike given; each counts the hours it was off. Checked against the same arithmetic done
here in Python. The all-in rule draws only when each part is held or zero by design. No request, no model call."""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


PRICES = [float(i % 24 + 10) for i in range(8760)]
PRICES[100], PRICES[200] = 2000.0, 1500.0
PEAK_HOUR = 181 * 24 + 17          # 1 July 2025, 17:00 in the fixture's time (0 hours behind UTC)
PEAK_TS = "2025-07-01T17:15:00Z"

SCRIPT = """
const S = await import('./lib/siting.ts');
const L = await import('./lib/datacenter.ts');
const dc = { monthsRuled: L.monthsRuled, lastTwelve: L.lastTwelve, span: L.span, years: L.years, expand: L.expand, monthsOfYear: L.monthsOfYear, monthStarts: L.monthStarts };
const prices = Array.from({ length: 8760 }, (_, i) => (i %% 24) + 10); prices[100] = 2000; prices[200] = 1500;
const file = { grid: 'ercot', year: 2025, hours: 8760, built: '', regions: { A: { da: { s: 0, v: prices } } } };
const f = { index: { grids: { ercot: { std_hours_behind_utc: 0, regions: [{ id: 'A' }], main: 'A', years: [2025] } }, blank: {} }, nodes: { nodes: [] }, years: () => [file] };
const cp = { table: 't', built: '', note: '', summers: [{ year: 2025, intervals: [{ ts: '%s', local: '', mw: 1 }] }] };
const out = {};
const run = (name, x) => { const t = S.profileTwelve(dc, f, 'ercot', 'A', x, cp); out[name] = t; };
run('datacenter', { profile: 'datacenter', lf: 0.9, strike: null });
run('industry', { profile: 'industry', lf: 0.8, strike: null });
run('flexible', { profile: 'flexible', lf: 0.9, strike: 1000 });
run('flexible_low', { profile: 'flexible', lf: 0.9, strike: 30 });
run('electrolyzer', { profile: 'electrolyzer', lf: 0.5, strike: null });
run('electrolyzer_strike', { profile: 'electrolyzer', lf: 0.5, strike: 20 });
run('never', { profile: 'electrolyzer', lf: 0.5, strike: 5 });
out.allin = [S.allIn({ energy: { v: 30 }, transmission: { v: 0, zero: 'z' }, capacity: { v: 2 } }), S.allIn({ energy: { v: 30 }, transmission: { missing: 'not held' }, capacity: { v: 0 } })];
out.key = S.profileKey({ profile: 'electrolyzer', lf: 0.55, strike: null });
out.back = S.profileOfKey(out.key);
process.stdout.write(JSON.stringify(out));
""" % PEAK_TS


def run():
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


def mean(v):
    return sum(v) / len(v)


class Profiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = run()

    def test_datacenter_and_industry_pay_the_flat_price(self):
        for k in ("datacenter", "industry"):
            t = self.o[k]
            self.assertAlmostEqual(t["per"], mean(PRICES), places=9)
            self.assertEqual((t["run"], t["lost"], t["held"]), (8760, 0, 8760))
        self.assertEqual((self.o["datacenter"]["from"], self.o["datacenter"]["to"]), ("2025-01", "2025-12"))

    def test_flexible_is_off_at_the_strike_and_at_the_peak(self):
        t = self.o["flexible"]
        keep = [v for i, v in enumerate(PRICES) if v < 1000 and i != PEAK_HOUR]
        self.assertAlmostEqual(t["per"], mean(keep), places=9)
        self.assertEqual((t["lost"], t["peaks"]), (3, 1))
        low = self.o["flexible_low"]
        keep = [v for i, v in enumerate(PRICES) if v < 30 and i != PEAK_HOUR]
        self.assertAlmostEqual(low["per"], mean(keep), places=9)
        self.assertEqual(low["lost"], 8760 - len(keep))

    def test_electrolyzer_runs_in_the_cheapest_share_or_below_a_strike(self):
        t = self.o["electrolyzer"]
        strike = sorted(PRICES)[round(0.5 * 8760) - 1]
        keep = [v for v in PRICES if v <= strike]
        self.assertEqual(t["strike"], strike)
        self.assertAlmostEqual(t["per"], mean(keep), places=9)
        self.assertEqual(t["lost"], 8760 - len(keep))
        s = self.o["electrolyzer_strike"]
        keep = [v for v in PRICES if v < 20]
        self.assertAlmostEqual(s["per"], mean(keep), places=9)
        self.assertEqual(s["run"], len(keep))
        self.assertIsNone(self.o["never"]["per"])   # NaN in JSON is null: it never runs at USD 5

    def test_all_in_draws_only_when_every_part_is_held_or_zero_by_design(self):
        self.assertEqual(self.o["allin"][0], {"v": 32})
        self.assertEqual(self.o["allin"][1], {"missing": "transmission: not held"})

    def test_the_key_names_the_inputs_and_reads_back(self):
        self.assertEqual(self.o["key"], "profile=electrolyzer&lf=0.55&strike=row")
        self.assertEqual(self.o["back"], {"profile": "electrolyzer", "lf": 0.55, "strike": None})


class Page(unittest.TestCase):
    def test_the_tab_draws_and_check_values_reads_the_profiles(self):
        v = src("site", "app", "cost-of-power", "AllGridsView.tsx")
        self.assertIn("check={`allgrids|energy|${r.id}|da|${k}`}", v)
        self.assertIn("check={`allgrids|lost|${r.id}|${k}`}", v)
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('"/cost-of-power?view=allgrids&profile=flexible", "/cost-of-power?view=allgrids&profile=electrolyzer", "/cost-of-power?view=allgrids&profile=industry"', cv)
        self.assertIn('data-allgrids-strike="1"', src("site", "app", "cost-of-power", "AllGridsForm.tsx"))

    def test_the_4cp_file_is_the_table_s_intervals(self):
        cp = json.loads(src("site", "data", "siting", "ercot_4cp.json"))
        self.assertEqual(cp["table"], "ercot_4cp_intervals")
        self.assertEqual(sum(len(s["intervals"]) for s in cp["summers"]), 28)
        self.assertTrue(all(len(s["intervals"]) == 4 for s in cp["summers"]))

    def test_no_em_dash(self):
        for p in [("site", "lib", "siting.ts"), ("site", "app", "cost-of-power", "AllGridsView.tsx"), ("site", "app", "cost-of-power", "AllGridsForm.tsx")]:
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
