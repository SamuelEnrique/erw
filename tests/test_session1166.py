"""Session 1166 (chain 078): the Clean tab and the Mix tab's last unkeyed figures.

Keyed, each with a one-line source in its tip, no figure's text moved:
- the Mix tab's "Yesterday" (site/components/grid/Conditions.tsx): the forecast's miss at the peak in MW and in percent
  (fmt|pm0| and fmt|f1| over calc|diff and a new calc op diffpct), the day's mean absolute miss and its hours (a new
  kind fcerr|mape and fcerr|hours), the degree days (a new kind degday|cdd and degday|hdd); the arithmetic moved, as it
  was, to site/lib/gridYesterday.ts, which check-values imports;
- the mix table's fuel shares (Conditions.tsx MixTable): fmt|f1|calc|pct over two series_sum keys of the day's rows;
- "Hours held" (site/components/grid/YourGrid.tsx): series_n (session 1154);
- the count of CAISO's notices and the newest day (site/components/grid/Reliability.tsx): awe|rows|any, awe|newest|any;
- the energy mix views and "How clean, and when" (site/components/mix/views.tsx), drawn from committed files: a new kind
  file|<data file>|<path> (site/scripts/check-file.mjs) behind fmt|<form>| (site/scripts/check-format.mjs), recomputed
  from the file in the repository; where the file is a build of a live-set row, check-values compares it with that row
  on a line of its own.
The node test (site/scripts/test-grid-file-keys.mjs) draws the views and recomputes every key from the files.
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
NEW = [("site", "lib", "gridYesterday.ts"), ("site", "scripts", "check-format.mjs"), ("site", "scripts", "check-file.mjs"),
       ("site", "scripts", "test-grid-file-keys.mjs"), ("site", "scripts", "fixtures", "grid_yesterday.json"), ("tests", "test_session1166.py")]
CHANGED = [("site", "components", "grid", "Conditions.tsx"), ("site", "components", "grid", "YourGrid.tsx"), ("site", "components", "grid", "Reliability.tsx"),
           ("site", "components", "mix", "views.tsx"), ("site", "lib", "caisoAlerts.ts"), ("site", "scripts", "check-values.mjs"),
           ("site", "scripts", "check-calc.mjs"), ("site", "scripts", "check-methods.mjs"), ("docs", "methods", "generation_mix_hourly.md"),
           ("docs", "methods", "grid_stress.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheDatabaseFigures(unittest.TestCase):
    def test_yesterday_keys_the_miss_the_mean_miss_and_the_degree_days(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn("<F check={`fmt|pm0|calc|diff|${dk}|${fk}`} raw={peak.value - fAtPeak}", c)
        self.assertIn("<F check={`fmt|f1|calc|diffpct|${dk}|${fk}`} raw={((peak.value - fAtPeak) / peak.value) * 100}", c)
        self.assertIn("<F check={`fmt|f1|fcerr|mape|${dayWin}`} raw={mape}", c)
        self.assertIn("<F check={`fcerr|hours|${dayWin}`} raw={paired}", c)
        self.assertIn("<F check={`fmt|f1|degday|cdd|nws:${r.ba.station}|${x.day}`} raw={x.mean - BASE_F}", c)
        self.assertIn("<F check={`fmt|f1|degday|hdd|nws:${r.ba.station}|${x.day}`} raw={BASE_F - x.mean}", c)
        # the text is the page's own, as it was: the sign, then the size; one decimal; "% over N hours"
        self.assertIn('{peak.value - fAtPeak >= 0 ? "+" : "−"}{count(Math.abs(peak.value - fAtPeak))}</F> MW (', c)
        self.assertIn("{(((peak.value - fAtPeak) / peak.value) * 100).toFixed(1)}</F>% of demand)", c)
        self.assertIn("{mape.toFixed(1)}</F>% over{\" \"}", c)
        self.assertIn("<>CDD <F", c)
        self.assertIn("<>HDD <F", c)
        # the arithmetic moved, as it stood, into lib/gridYesterday.ts
        self.assertIn('const { mape, hours: paired } = forecastMiss(dem, dayRows.filter((x) => x.variable === "demand_forecast_mw"));', c)
        self.assertIn("dd.push({ day, ...dayMean(h) });", c)
        y = src("site", "lib", "gridYesterday.ts")
        self.assertIn("const mape = pairs.length ? (100 * pairs.reduce((a, x) => a + Math.abs(x.value - fc.get(x.ts_utc)!) / x.value, 0)) / pairs.length : null;", y)
        self.assertIn("return mean >= BASE_F ? { kind: \"cdd\", value: mean - BASE_F } : { kind: \"hdd\", value: BASE_F - mean };", y)
        self.assertNotIn("import ", y)

    def test_the_mix_table_keys_each_share_as_two_sums_of_the_day(self):
        c = src("site", "components", "grid", "Conditions.tsx")
        self.assertIn("{by.has(f.key) ? <><F check={shareKey(r, f.key)} raw={(by.get(f.key)! / total) * 100} tip={shareTip(r, f.key)}>{((by.get(f.key)! / total) * 100).toFixed(1)}</F>%</> : \"\"}", c)
        self.assertIn("return `fmt|f1|calc|pct|series_sum~${GEN}~${groupVars(r, fuel).join(\",\")}~${s0}~${s1}~${r.ba.entity}|series_sum~${GEN}~net_generation_mw~${s0}~${s1}~${r.ba.entity}`;", c)

    def test_hours_held_and_the_notice_count(self):
        g = src("site", "components", "grid", "YourGrid.tsx")
        self.assertIn("<Num check={`series_n|${T}|${s.v}|${s0}|${s1}|${g.entity}`} raw={s.n}>{count(s.n)}</Num>", g)
        r = src("site", "components", "grid", "Reliability.tsx")
        self.assertIn('<Num check="awe|rows|any" raw={notices.length}>{count(notices.length)}</Num>', r)
        self.assertIn('<Num check="awe|newest|any" raw={lastNotice.event_date.slice(0, 10)}>{lastNotice.event_date.slice(0, 10)}</Num>', r)
        a = src("site", "lib", "caisoAlerts.ts")
        self.assertIn('if (p[1] === "rows" && p.length === 3) return rows.filter((r) => inGroup(r.event_type, p[2])).length;', a)
        self.assertIn('if (p[1] === "newest" && p.length === 3) return lastDay(rows, p[2], "9999-12-31");', a)


class TheChecker(unittest.TestCase):
    def test_check_values_knows_the_new_kinds(self):
        v = src("site", "scripts", "check-values.mjs")
        for k in ('if (p[0] === "fmt") {', 'if (p[0] === "file") {', 'if (p[0] === "fcerr") {', 'if (p[0] === "degday") {',
                  'if (p[0] === "awe" && (p[1] === "rows" || p[1] === "newest")) {'):
            self.assertIn(k, v)
        # a fmt| figure's text is the recomputed value in its form, and nothing else
        self.assertIn("const textHolds = fp ? text === FMT.formText(fp.form, t) : textOk;", v)
        self.assertIn("let pass = t !== undefined && t !== null && same && textHolds;", v)
        # a file's figure against its table, on a line of its own, counted apart
        self.assertIn('out.lines.push(`${eq ? "same" : "DIFF"} | ${page} | ${check} | the file\'s ${t}', v)
        self.assertIn("committed files against their live-set tables:", v)
        self.assertIn("ARITY.diffpct = 2;", src("site", "scripts", "check-calc.mjs"))

    def test_check_methods_names_the_new_kinds(self):
        m = src("site", "scripts", "check-methods.mjs")
        self.assertIn('if (head === "fmt" && p.length >= 3) return figures(p.slice(2).join("|"));', m)
        self.assertIn('return [{ kind: "family", table: "file", measure, id: `file| ${shape(measure)}` }];', m)

    def test_the_method_notes_hold_the_keys(self):
        for note, words in ((("docs", "methods", "generation_mix_hourly.md"), ("fcerr|", "degday|", "file|", "fmt|", "awe|rows|any", "chain 078, 24 October 2026")),
                            (("docs", "methods", "grid_stress.md"), ("file|stress/", "grid_stress_yearly", "chain 078, 24 October 2026"))):
            t = src(*note)
            for w in words:
                self.assertIn(w, t, (note, w))


class TheViews(unittest.TestCase):
    def test_one_keyed_figure_writes_every_key_of_the_views(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertEqual(v.count("check="), 1)
        self.assertIn("<Num check={`fmt|${form}|file|${file}|${at}`} raw={v}>{FORM[form](v)}</Num>", v)
        # a held grid's cells in the clean view's table of the seven grids stay as they were
        self.assertIn("cf = `clean/${g}.json`, y = `years.${year}`, key = !held(g);", v)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), parts)


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-file-keys.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIsNotNone(re.search(r"^\S* ?pass 1[2-9]", r.stdout, re.M), r.stdout[-1500:])


if __name__ == "__main__":
    unittest.main()
