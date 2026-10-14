"""Session 280: "What a datacenter pays" (/cost-of-power) reads its two new tables.

Energy Research Warehouse (ERW), the daytime chain of 14 October 2026. What is held here:
- "Will the power be there?" reads scarcity_hours_by_grid through lib/datacenter/answers.ts: at the grid's hub, the hours
  of the page's twelve months whose real-time price was at or above USD 1,000 per MWh and the hours the grid's own
  signal was in force, each beside the hours the table holds of it; only for the grids the table holds (ERCOT, CAISO);
  an hour with no row is not counted, an hour written twice once; every figure under a check key dc|<address>|sbg:...;
- "How soon?" lists every statement of large_load_public for the load's grid (the operator's, then the utilities' and
  others') and, for a grid in one state, those of other grids in that state, each with its date and its document's
  link, no quoted text, never a sum; each figure under dcll|<the row's grid>|row:<statement_id>:mw or :wait, a wait
  written with words before its number standing as written with no key;
- check-values recomputes both, and reads CAISO's address too;
- the download carries the hub counts.
Nothing here sets the environment, reads a table or makes a request.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(script):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
    if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


class TheHubCounts(unittest.TestCase):
    def test_counted_by_node(self):
        # ERCOT, six hours behind: 2025-10-01T06:00Z is the first hour of October in standard time; 2025-10-01T05:00Z is
        # September's last and is outside; one hour written twice; the own signal held for two hours only
        script = ("const A = await import('./lib/datacenter/answers.ts'); "
                  "const rows = [{ variable: 'rt_hour_ge_1000', ts_utc: '2025-10-01T05:00:00Z', value: 1 }, "
                  "{ variable: 'rt_hour_ge_1000', ts_utc: '2025-10-01T06:00:00Z', value: 1 }, { variable: 'rt_hour_ge_1000', ts_utc: '2025-10-01T06:00:00Z', value: 1 }, "
                  "{ variable: 'rt_hour_ge_1000', ts_utc: '2025-10-01T07:00:00Z', value: 0 }, { variable: 'rt_hour_ge_1000', ts_utc: '2025-11-30T23:00:00Z', value: 0 }, "
                  "{ variable: 'own_signal', ts_utc: '2025-10-01T06:00:00Z', value: 1 }, { variable: 'own_signal', ts_utc: '2025-10-02T06:00:00Z', value: 0 }]; "
                  "const g = A.byGrid(rows, ['2025-10', '2025-11'], 6, 'HB_HUBAVG'); "
                  "const a = { byGrid: g }; "
                  "console.log(JSON.stringify([g.rt, g.own, g.level, ['sbg:rt:hours','sbg:rt:held','sbg:own:hours','sbg:own:held','sbg:x:hours'].map((k) => A.statOf(a, k) ?? null), A.byGrid([], ['2025-10'], 6, 'x')]));")
        rt, own, level, stats, none = node(script)
        self.assertEqual(rt, {"hours": 1, "held": 3, "first": "2025-10-01", "last": "2025-11-30"})
        self.assertEqual(own, {"hours": 1, "held": 2, "first": "2025-10-01", "last": "2025-10-02"})
        self.assertEqual(level, 1000)
        self.assertEqual(stats, [1, 3, 1, 2, None])
        self.assertIsNone(none)

    def test_the_read_is_bounded_and_only_for_the_grids_held(self):
        lib = src("site", "lib", "datacenter", "answers.ts")
        self.assertIn('export const SBG_HUBS: Record<string, string> = { ercot: "HB_HUBAVG", caiso: "TH_SP15_GEN-APND" };', lib)
        self.assertIn('variable: "in.(rt_hour_ge_1000,own_signal)"', lib)
        self.assertIn("and: `(ts_utc.gte.${iso(Date.UTC(y, m, 1) + behind * 3600_000)},ts_utc.lt.${iso(Date.UTC(ly, lm, 1) + behind * 3600_000)})`", lib)
        self.assertIn('order: "ts_utc,variable"', lib)                       # a stable order across pages
        self.assertIn("if (SBG_HUBS[grid] && l12.length) {", lib)

    def test_the_page_sets_them_side_by_side(self):
        answers = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        self.assertIn("{a.byGrid ? <ByGridCounts a={a} f={f} /> : null}", answers)
        part = answers.split("function ByGridCounts", 1)[1].split("/** How clean", 1)[0]
        for k in ("sbg:rt:hours", "sbg:rt:held", "sbg:own:hours", "sbg:own:held"):
            self.assertIn(f'stat="{k}"', part, k)
        self.assertIn("From scarcity_hours_by_grid.", part)
        self.assertIn("Published until 4 December 2025 and no longer", answers.split("const OWN_WORDS", 1)[1].split("function ByGridCounts", 1)[0])
        route = src("site", "app", "cost-of-power", "tables.csv", "route.ts")
        self.assertIn('put(S, "hub_rt_ge_1000", "hours"', route)
        self.assertIn('put(S, "own_signal", "hours"', route)
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn('...(x.grid === "ercot" || x.grid === "caiso" ? ["scarcity_hours_by_grid"] : []), "large_load_public", ', page)


class TheStatementsListed(unittest.TestCase):
    def test_lists_and_row_figures_by_node(self):
        script = ("const S = await import('./lib/datacenter/statements.ts'); "
                  "const g = [{ event_date: '2026-09-17', parties: 'ERCOT', mw: 1400, source_url: 'u1', row_kind: 'mw', statement_id: 'a', entity_type: 'grid operator', grid: 'ercot', state: 'TX' }, "
                  "{ event_date: '2026-09-18', parties: 'Oncor', mw: null, source_url: 'u2', row_kind: 'wait', duration_as_stated: '18 to 24 months', statement_id: 'b', entity_type: 'utility', grid: 'ercot', state: 'TX' }, "
                  "{ event_date: '2026-09-19', parties: 'ERCOT', mw: 22000.5, source_url: 'u3', row_kind: 'mw', statement_id: 'c', entity_type: 'operator', grid: 'ercot', state: 'TX' }]; "
                  "const all = [...g, { event_date: '2026-08-01', parties: 'El Paso Electric', mw: 50, source_url: 'u4', row_kind: 'mw', statement_id: 'd', entity_type: 'utility', grid: 'none of the seven', state: 'TX' }, "
                  "{ event_date: '2026-08-02', parties: 'AEP', mw: 9, source_url: 'u5', row_kind: 'mw', statement_id: 'e', entity_type: 'utility', grid: 'more than one', state: 'OH, TX, VA' }, "
                  "{ event_date: '2026-08-03', parties: 'PG&E', mw: 7, source_url: 'u6', row_kind: 'mw', statement_id: 'f', entity_type: 'utility', grid: 'caiso', state: 'CA' }]; "
                  "const l = S.listsOf(g, all, 'ercot'); const p = S.listsOf(g, all, 'pjm'); "
                  "console.log(JSON.stringify([l.operator.map((r) => r.statement_id), l.others.map((r) => r.statement_id), l.state.map((r) => r.statement_id), p.state.length, "
                  "S.rowStat(all, 'row:c:mw'), S.rowStat(all, 'row:b:wait'), S.rowStat(all, 'row:b:mw') ?? null, S.rowStat(all, 'row:zz:mw') ?? null, S.rowStat(all, 'mws') ?? null]));")
        self.assertEqual(node(script), [["c", "a"], ["b"], ["e", "d"], 0, 22000.5, 18, None, None, None])

    def test_facts_with_a_link_no_quoted_text_never_a_sum(self):
        answers = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        part = answers.split("function StatedList", 1)[1].split("export function HowSoon", 1)[0]
        for words in ("const key = (r: Statement, k: \"mw\" | \"wait\") => `dcll|${r.grid ?? lists.grid}|row:${r.statement_id}:${k}`;",
                      '<a href={r.source_url} rel="noopener noreferrer">', "The figures are not added", "no quoted text",
                      '/^\\d/.test((r.duration_as_stated ?? "").trim())'):
            self.assertIn(words, part, words)
        for column in ("sentence", "quote:", "load_scope", "reduce("):
            self.assertNotIn(column, part, column)
        self.assertEqual(answers.count("<StatedList lists={lists} gridName={f.gridName} />"), 2)   # with each StatedLine
        self.assertNotIn("reduce(", src("site", "lib", "datacenter", "statements.ts"))
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("const allRows = GRID_STATE[M.x.grid] ? (await largeLoadStatements()) as unknown as Statement[] : [];", page)

    def test_check_values_recomputes_them(self):
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[2]?.startsWith("row:")) return S.rowStat(rows, p.slice(2).join("|"));', check)
        self.assertIn("statement_id:extra->>statement_id", check)
        self.assertIn('"/cost-of-power?grid=caiso",', check)


if __name__ == "__main__":
    unittest.main()
