"""Session 297: the battery's finance model, passes 2 to 4 (the chain prompt of 19 October 2026). What is held to:

  six more assumptions (the investment tax credit, the degradation method with its fade, augmentation and
    augmentation cost, the stress repeats), each at a default that moves nothing: the finance library's defaults,
    letters and choices, and the hand cases that prove the credit at year 0, the fade with and without augmentation,
    the augmentation cost in its years, and the repeats;
  the page: the fields under Financing with the degradation method as a sub-group, the stress control in the second
    question, the context (the peak event and the hours) handed to every figure, no judging word;
  the stress-day rule is written (docs/methods/battery_stress_days.md) and the methods note states the formulas and
    what each setting does to NPV at the default case; check-values reads the page at one non-default setting each;
  no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
FILES = [
    "site/lib/battery/finance.ts", "site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/Scenarios.tsx",
    "site/app/cost-of-power/battery/Settings.tsx", "site/scripts/test-battery-finance.mjs", "site/scripts/check-battery-scenarios.mjs", "site/scripts/check-values.mjs",
    "docs/methods/battery_earns_algorithm.md", "docs/methods/battery_stress_days.md", "tests/test_session297.py",
]
NEW = ["itc", "method", "fade", "aug", "augcost", "stress"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(expr):
    script = f"const F = await import('./lib/battery/finance.ts'); process.stdout.write(JSON.stringify({expr}));"
    try:
        out = subprocess.run(["node", "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise unittest.SkipTest(f"node did not answer: {exc}")
    if out.returncode != 0:
        raise AssertionError(out.stderr[-800:])
    return json.loads(out.stdout)


class TheLibrary(unittest.TestCase):
    def test_eighteen_keys_six_new_with_their_letters_and_idle_defaults(self):
        lib = src("site", "lib", "battery", "finance.ts")
        self.assertIn('export const KEYS: Key[] = ["capex", "share", "rate", "term", "fom", "rte", "cycles", "deg", "life", "hurdle", "itc", "method", "fade", "aug", "augcost", "stress", "cshare", "cprice"];', lib)
        self.assertIn("export const OPTIONS: Partial<Record<Key, number[]>> = { method: [0, 1], aug: [0, 3, 5, 7, 10] };", lib)
        for k, letter in (("itc", "i"), ("method", "o"), ("fade", "g"), ("aug", "m"), ("augcost", "k"), ("stress", "x")):
            self.assertIn(f'  {k}: {{ key: "{k}", letter: "{letter}"', lib, k)
        v = node_eval("await (async () => { const d = F.defaultsOf({ capex: 1110, fom: 22 }); const ctx = { peak: 3105.51, hours: 4 }; return { d, same: JSON.stringify(F.flows(d, 81.4, ctx)) === JSON.stringify(F.flows(d, 81.4)), keys: F.sensitivityKeys(d).length, withFade: F.sensitivityKeys({ ...d, method: 1 }).length }; })()")
        self.assertEqual({k: v["d"][k] for k in NEW}, {"itc": 0, "method": 0, "fade": 2.6, "aug": 0, "augcost": 241, "stress": 0})
        self.assertTrue(v["same"])
        self.assertEqual((v["keys"], v["withFade"]), (10, 13))

    def test_the_credit_the_fade_and_the_repeats_by_hand(self):
        v = node_eval("""await (async () => {
          const d = F.defaultsOf({ capex: 1000, fom: 10 });
          const z = { ...d, share: 60, rate: 0, term: 10, life: 10, hurdle: 0, deg: 0 };
          const ctx = { peak: 500, hours: 4 };
          const f0 = F.flows({ ...z, itc: 30 }, 100, ctx)[0];
          const fade = { ...z, method: 1, fade: 10, aug: 0 };
          const aug = { ...z, method: 1, fade: 10, aug: 5, augcost: 100 };
          return { f0, r3: F.revenueInYear(fade, 100, 3, ctx), r6aug: F.revenueInYear(aug, 100, 6, ctx), cost5: F.augmentationCost(aug, 5, ctx), cost10: F.augmentationCost(aug, 10, ctx),
            cost4: F.augmentationCost(aug, 4, ctx), st: F.revenueInYear({ ...z, stress: 2 }, 100, 1, ctx), sum: F.npv(0, F.flows({ ...z, stress: 2 }, 100, ctx)) - F.npv(0, F.flows(z, 100, ctx)),
            noPeak: F.revenueInYear({ ...z, stress: 2 }, 100, 1, {}), cover: F.coverage({ ...z, stress: 2 }, 100) === F.coverage(z, 100) };
        })()""")
        self.assertAlmostEqual(v["f0"], -400 + 300)
        self.assertAlmostEqual(v["r3"], 100 * 0.9 ** 2)
        self.assertAlmostEqual(v["r6aug"], 100)
        self.assertAlmostEqual(v["cost5"], (1 - 0.9 ** 5) * 4 * 100)
        self.assertEqual(v["cost10"], 0)       # the last year: no augmentation
        self.assertEqual(v["cost4"], 0)
        self.assertAlmostEqual(v["st"], 100 + 2 * 500 / 10)
        self.assertAlmostEqual(v["sum"], 1000)
        self.assertEqual(v["noPeak"], 100)
        self.assertTrue(v["cover"])

    def test_the_hand_cases_pass(self):
        try:
            out = subprocess.run(["node", "scripts/test-battery-finance.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise unittest.SkipTest(f"node did not answer: {exc}")
        self.assertEqual(out.returncode, 0, out.stdout[-1500:])
        self.assertIn("the credit is taken at year 0 only", out.stdout)
        self.assertIn("augmentation every 5 years restores the capacity in years 6, 11 and 16", out.stdout)


class ThePage(unittest.TestCase):
    def test_the_fields_the_sub_group_and_the_stress_control(self):
        sc = src("site", "app", "cost-of-power", "battery", "Scenarios.tsx")
        self.assertIn('const fields: Field[] = KEYS.filter((k) => k !== "stress").map((k) => {', sc)
        self.assertIn('{ key: "degradation", title: "Degradation and augmentation", keys: ["method", "fade", "aug", "augcost"] }', sc)
        self.assertIn("function StressRepeats({ peak }: { peak: Peak })", sc)
        self.assertIn('data-stress-repeats={s.view}', sc)
        self.assertIn('data-assumption="stress"', sc)
        self.assertIn("<StressRepeats peak={peak} />", sc)
        for words in ("resultOf(a, kw, ctx)", "flows(a, kw, ctx)", "projection(a, kw, ctx)", "resultOf(y, rev.l12, ctx)", "v.measure, ctx)"):
            self.assertIn(words, sc, words)
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertIn("const peakEvent = events.length ? events.reduce((a, e) => (e.total > a.total ? e : a)) : null;", page)
        self.assertIn("peak={peak} hours={x.dur}", page)
        self.assertIsNone(re.search(r"\bworst\b", (sc + page).lower()))

    def test_check_values_reads_one_non_default_setting_each(self):
        cv = src("site", "scripts", "check-values.mjs")
        for addr in ("/cost-of-power/battery?ai=30", "/cost-of-power/battery?ao=1", "/cost-of-power/battery?ao=1&am=5", "/cost-of-power/battery?ax=2"):
            self.assertIn(f'"{addr}"', cv, addr)


class TheNotes(unittest.TestCase):
    def test_the_stress_day_rule_and_the_formulas(self):
        rule = src("docs", "methods", "battery_stress_days.md")
        for words in ("98th percentile of the daily means of the 365 days before it", "caiso_grid_emergencies", "Days at most three days apart are **one event**", "Not applied yet", "uri_2021"):
            self.assertIn(words, rule, words)
        # session 322: the table now exists (ERCOT's releases and control-room messages); the rule names it since
        self.assertIn("ercot_grid_notices", rule)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", "ercot_grid_notices.py")))
        note = src("docs", "methods", "battery_earns_algorithm.md")
        self.assertIn("#### Session 297: the tax credit, the fade method with augmentation, and the stress repeats", note)
        for words in ("`F_0 = -capex x (1 - share) + capex x itc`", "`(1 - (1 - fade)^aug) x hours x augcost`", "`stress x peak / life`", "USD -697.80 to -364.80", "-768.12", "-613.19", "+583.43"):
            self.assertIn(words, note, words)
        self.assertIn("| The fade method at the ATB's convention (session 297)", note)
        self.assertIn("battery_stress_days.md", note)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    sys.exit(unittest.main())
