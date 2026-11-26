"""Audit of the severance tool, finding 3 (session 10207, docs/reviews/severance-model-audit-2026-11-26.md): the Lease tab
prices any month since January 2023, and taxes every month of a file at the rates the rules file holds today
(site/lib/lease.ts calls site/lib/severance.ts compute with the one rules file; the month sets only the default price and
the Texas certified period). Louisiana's gas rate, 15.14 cents per Mcf, is the rate for July 2026 to June 2027, and the
rules file's own quote says it is "adjusted annually on July first".

1. Through the page's libraries (run by Node): a Louisiana gas well's January 2024 month and its August 2026 month are
   both taxed at 15.14 cents an Mcf. Passes on main.
2. The fix on this branch, words only: the tab's lead and the method note say every month is taxed at today's rates.
   Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL = lambda *p: "file:///" + os.path.join(ROOT, *p).replace("\\", "/")  # noqa: E731
RULES = os.path.join(ROOT, "site", "data", "severance_rules.json")
JS = """
const S = await import(process.argv[1]);
const L = await import(process.argv[2]);
const fs = await import("node:fs");
const rules = JSON.parse(fs.readFileSync(process.argv[3], "utf-8"));
const row = (m) => L.COLUMNS.map((c) => ({ state: "LA", well_id: "AUDIT-LA-GAS", month: m, gas_mcf: "10000", gas_price: "3.00", well_type: "gas" })[c] ?? "").join(",");
const text = [L.COLUMNS.join(","), row("2024-01"), row("2026-08")].join("\\n");
const parsed = L.parseLease(text, rules);
const a = L.analyzeLease(rules, { compute: S.compute, creditPct: S.creditPct }, parsed.rows, { prices: { oil: {}, gas: {} }, ticks: {} });
console.log(JSON.stringify(a.lines.filter((l) => l.product === "gas").map((l) => [l.month, l.base])));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class OneDatesRulesForEveryMonth(unittest.TestCase):
    def test_a_2024_month_takes_the_fiscal_2027_gas_rate(self):
        out = subprocess.run(["node", "--input-type=module", "-e", JS, URL("site", "lib", "severance.ts"), URL("site", "lib", "lease.ts"), RULES],
                             capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        lines = dict(json.loads(out.stdout.strip().splitlines()[-1]))
        self.assertEqual(set(lines), {"2024-01", "2026-08"})
        self.assertAlmostEqual(lines["2024-01"], 1514.0, places=6)       # 10,000 Mcf x 15.14 cents
        self.assertAlmostEqual(lines["2026-08"], 1514.0, places=6)
        gas = json.loads(src("site", "data", "severance_rules.json"))["states"]["LA"]["products"]["gas"]["base"][0]
        self.assertEqual(gas["effective"], "2026-07-01 to 2027-06-30")
        self.assertIn("adjusted annually on July first", gas["quote2"])

    def test_the_tab_says_which_months_rates(self):
        self.assertIn("Every month of a file is taxed at the rates the rules file holds today: Louisiana&apos;s gas rate and horizontal well shares for July 2026 to",
                      src("site", "app", "severance", "lease", "view.tsx"))
        self.assertIn("only Texas&apos;s certified", src("site", "app", "severance", "lease", "view.tsx"))
        self.assertIn("**Which month's rates.** Every month of a file is taxed at the rates the rules file holds today", src("docs", "methods", "severance.md"))


if __name__ == "__main__":
    unittest.main()
