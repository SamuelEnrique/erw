"""Session 1892: session 1885's fault 2 on the battery page (docs/reviews/trader-path.md, "Walked 13 November 2026").

The fault, as session 1885 wrote it: "Battery page, ERCOT, steps 07 to 10: the last twelve months still end September
2026 on 13 November, while CAISO's end October; months.csv marks ERCOT's 2026-10 'held: yes' with 29 of 31 days and 1
left out, the year chart and income table call 2026 '10 months' (66.39 per kW) and Price years '2026, 9 months held'
(60.19). Should: ... a month the headline treats as incomplete not labelled held (site code fix)."

The headline's rule is lastTwelve's (lib/batterystack.ts, session 195): the window ends with the newest held month that
is whole, every one of its days in the table, solved or left out. A month at 90 percent of its days that is not whole and
newer than every whole month was outside the headline yet held for every other reader. The fix: monthsOf passes its
months through settle, which makes that month not held, so the year chart and the income table (years), the averages,
the bad month's window, months.csv, the check keys and site/scripts/price-years.mjs (which writes the "Price years"
choice) all take the headline's months. months.csv says the waiting month's days in a '#' line beside its "held: no".
The numbers' source is unchanged.

No network, no model, no browser. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


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


# ERCOT's months as the live set held them on 13 November 2026, in shape: September 2025 to September 2026 whole, and
# October 2026 with 29 of 31 days solved and 1 left out (the foresight case), or 30 solved and none left out (day-ahead)
ROWS = """
const days = (y, m) => new Date(Date.UTC(y, m, 0)).getUTCDate();
const rows = (last) => {
  const out = [];
  const put = (y, m, held, left) => {
    const ts = `${y}-${String(m).padStart(2, "0")}-01T00:00:00Z`, pre = "foresight_4h_";
    for (const [k, v] of [["days_held", held], ["days_left_out", left], ["days_in_month", days(y, m)], ["revenue_total_usd_per_mw", 1000 * held], ["revenue_energy_usd_per_mw", 600 * held], ["revenue_ancillary_usd_per_mw", 400 * held]])
      out.push({ variable: pre + k, ts_utc: ts, value: v });
  };
  for (let i = 0; i < 25; i++) { const y = 2024 + Math.floor((8 + i) / 12), m = ((8 + i) % 12) + 1; put(y, m, days(y, m), 0); }
  if (last) put(2026, 10, last[0], last[1]);
  return out;
};
"""


class TheLibrarySettlesTheRunningMonth(unittest.TestCase):
    def test_monthsOf_passes_its_months_through_settle(self):
        s = src("site", "lib", "batterystack.ts")
        body = s[s.index("export function monthsOf("):s.index("export function settle(")]
        self.assertIn("return settle(out);", body)
        self.assertNotIn("\n  return out;\n}", body)
        settle = s[s.index("export function settle("):s.index("export const waiting")]
        self.assertIn("for (const r of ms) if (r.whole && r.m > lastWhole) lastWhole = r.m;", settle)
        self.assertIn("r.held && !r.whole && r.m > lastWhole ? { ...r, held: false } : r", settle)
        # the headline's own rule is unchanged: the newest held month that is whole ends the window
        self.assertIn("if (!r.held || !r.whole) continue;", s)
        self.assertIn("session 1885's fault 2", s)

    @unittest.skipUnless(node_ok(), "node or the site's packages are not here")
    def test_october_at_29_of_31_days_is_held_nowhere_and_the_year_has_nine_months(self):
        script = ROWS + """
const B = await import('./lib/batterystack.ts');
const out = {};
for (const [name, last] of [["foresight", [29, 1]], ["dayahead", [30, 0]], ["whole", [30, 1]], ["none", null]]) {
  const ms = B.monthsOf(rows(last), "foresight", 4);
  const l12 = B.lastTwelve(ms), y26 = B.years(ms).find((y) => y.y === "2026");
  out[name] = { oct: ms.find((r) => r.m === "2026-10") ?? null, waiting: ms.filter(B.waiting).map((r) => r.m),
    from: l12[0].m, to: l12[11].m, months26: y26.months, l12: B.stat(rows(last), [], B.inputsOf({}), "l12_kw:total"),
    yr26: B.stat(rows(last), [], B.inputsOf({}), "yr_kw:2026:total"), to36: B.last36(ms).to, held: ms.filter((r) => r.held).length };
}
process.stdout.write(JSON.stringify(out));
"""
        r = run_node(script)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        for name in ("foresight", "dayahead"):
            o = d[name]
            # the month is in the table at 90 percent, not whole, and not held
            self.assertFalse(o["oct"]["held"], name)
            self.assertFalse(o["oct"]["whole"], name)
            self.assertEqual(o["waiting"], ["2026-10"], name)
            # the headline ends September 2026, and so does every other figure: the year chart and the income table
            # count nine months of 2026, the bad month's 36 months end September, as many months are held as without it
            self.assertEqual((o["from"], o["to"]), ("2025-10", "2026-09"), name)
            self.assertEqual(o["months26"], 9, name)
            self.assertEqual(o["to36"], "2026-09", name)
            self.assertEqual(o["held"], d["none"]["held"], name)
            self.assertEqual(o["l12"], d["none"]["l12"], name)
        # the moment October is whole it is held, the window moves to it and 2026 has ten months, as before
        w = d["whole"]
        self.assertTrue(w["oct"]["held"])
        self.assertEqual(w["waiting"], [])
        self.assertEqual((w["from"], w["to"]), ("2025-11", "2026-10"))
        self.assertEqual(w["months26"], 10)
        self.assertEqual(w["held"], d["none"]["held"] + 1)

    @unittest.skipUnless(node_ok(), "node or the site's packages are not here")
    def test_a_month_older_than_a_whole_month_stays_held_as_the_headline_counts_it(self):
        script = ROWS + """
const B = await import('./lib/batterystack.ts');
// June 2026 at 28 of 30 days solved and none left out, inside the window: the headline counts it, and so does the rest
const rs = rows([31, 0]).map((r) => r.ts_utc.startsWith("2026-06") && r.variable === "foresight_4h_days_held" ? { ...r, value: 28 } : r);
const ms = B.monthsOf(rs, "foresight", 4);
const jun = ms.find((r) => r.m === "2026-06"), l12 = B.lastTwelve(ms);
process.stdout.write(JSON.stringify({ held: jun.held, whole: jun.whole, inWindow: l12.some((r) => r.m === "2026-06"), to: l12[11].m,
  months26: B.years(ms).find((y) => y.y === "2026").months }));
"""
        r = run_node(script)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d, {"held": True, "whole": False, "inWindow": True, "to": "2026-10", "months26": 10})


class TheDownloadSaysTheSame(unittest.TestCase):
    def test_months_csv_states_the_rule_and_names_the_waiting_month(self):
        s = src("site", "app", "cost-of-power", "battery", "months.csv", "route.ts")
        self.assertIn("monthsOf, waiting, type Inputs", s)
        self.assertIn("or a later month's are (the running month waits until it is whole, as the page's last twelve months do)", s)
        self.assertIn("...ms.filter(waiting).map((r) => `# ${r.m}: ${r.daysHeld} of ${r.daysInMonth} days solved and ${r.daysOut} left out, not yet whole", s)
        # the held column is the library's held, the one the headline's months come from
        self.assertIn('r.held ? "yes" : "no"', s)

    def test_the_chart_and_the_income_table_read_years_of_the_same_months(self):
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        self.assertIn("const ms: Month[] = monthsOf(rows, asked.strat, asked.dur);", page)
        self.assertIn("const ys = years(ms);", page)
        inc = src("site", "app", "cost-of-power", "battery", "Income.tsx")
        self.assertIn("const held = useMemo(() => years(ms), [ms]);", inc)

    def test_the_method_says_so(self):
        m = src("docs", "methods", "battery_earns_algorithm.md")
        self.assertIn("**A month at 90 percent that is not whole (session 1892).**", m)

    def test_no_dash_in_the_files_written(self):
        for p in (("site", "lib", "batterystack.ts"), ("site", "app", "cost-of-power", "battery", "months.csv", "route.ts"),
                  ("docs", "methods", "battery_earns_algorithm.md"), ("site", "scripts", "test-decisions-195.mjs"), ("tests", "test_session1892.py")):
            s = src(*p)
            self.assertEqual(s.count(chr(0x2014)) + s.count(chr(0x2013)), 0, "/".join(p))


if __name__ == "__main__":
    unittest.main()
