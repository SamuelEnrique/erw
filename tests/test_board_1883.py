"""Session 1883: the price board read on the real board.json of 12 November 2026 (docs/reviews/board-audit-2026-11-06.md,
rows 41 to 45).

- Row 41: at 390 px the page scrolled sideways, the held line's screen-reader words (an absolutely placed sr-only span)
  outside their table's scrolling box; the box is now their containing block (`relative overflow-x-auto`).
- Row 42: a closed group's head showed a stale figure with no mark; it prints "stale" beside its date, from closeAge.
- Row 43: the 30-day low to high cell was empty on every weekly, monthly and quarterly row; it says the step.
- Row 44: a region inside a container of the same name (the board's group section) was named "..., 2 of 2"; it takes a
  name of its own ("..., table") and every other page counts as before (components/ScrollRegions.tsx, shared).
- Row 45: check-board.mjs's usage line names alias-register.mjs, which runs it.

No network, no model, no browser. Nothing here sets the environment at import.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def view():
    return src("site", "components", "board", "BoardView.tsx")


def group_table():
    s = view()
    return s[s.index("function GroupTable("):s.index("const WEEK_COLS")]


def node_ok():
    return shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules", "typescript"))


class Row41TheHeldWordsStayInTheirBox(unittest.TestCase):
    def test_the_scroll_box_is_positioned_and_holds_the_sr_only_words(self):
        g = group_table()
        box = g.index('<div className="relative overflow-x-auto">')
        sr = g.index('<span className="sr-only">: {heldNote(grid)}</span>')
        self.assertLess(box, sr)
        self.assertEqual(g.count('className="overflow-x-auto"'), 0)
        # the box closes after the held lines' table, so the span's containing block is the box
        self.assertLess(sr, g.index("</table>"))


class Row42AStaleHeadIsMarked(unittest.TestCase):
    def test_the_head_prints_stale_from_close_age(self):
        g = group_table()
        self.assertIn("const leadAge = lead ? closeAge(lead, file.built) : null;", g)
        head = g[g.index("data-lead={group.id}"):]
        head = head[:head.index("</>}>")]
        self.assertIn("leadAge?.stale ?", head)
        self.assertIn("data-lead-stale={group.id}>stale</span>", head)
        self.assertIn("title={leadAge.words}", head)
        # the figure's mark is unchanged, so check-board.mjs's fold check still reads it
        self.assertIn('data-n={`fold|${group.id}|last`}', head)

    @unittest.skipUnless(node_ok(), "node or the site's packages are not here")
    def test_the_lead_of_a_stale_group_is_stale(self):
        script = ("const b = await import('./lib/board.ts');"
                  "const row = (id, t) => ({ id, group: 'heating', label: id, at: '', code: id, unit: 'USD/gal', freq: 'D', tags: {}, status: 'ok', source: 0, last: { t, v: 2.5 } });"
                  "const file = { built: '2026-11-12T17:48:19Z', sources: ['x'], groups: [{ id: 'heating', title: 'Heating', filters: [] }],"
                  " rows: [row('old', '2026-10-19'), row('new', '2026-11-11')], week: [], spikes: [] };"
                  "const lead = b.leadRow(file, file.groups[0]);"
                  "const fresh = { ...file, rows: [row('new', '2026-11-11')] };"
                  "process.stdout.write(JSON.stringify({ id: lead.id, stale: b.closeAge(lead, file.built).stale,"
                  " freshStale: b.closeAge(b.leadRow(fresh, fresh.groups[0]), file.built).stale }));")
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        got = json.loads(r.stdout)
        self.assertEqual(got["id"], "old")
        self.assertTrue(got["stale"])
        self.assertFalse(got["freshStale"])


class Row43TheLowToHighCellSaysItsStep(unittest.TestCase):
    def test_a_row_with_no_30_day_range_says_its_step_or_not_held(self):
        g = view()
        cell = g[g.index("{row.lo30 !== undefined ?"):]
        cell = cell[:cell.index("</td>")]
        self.assertIn('row.freq && row.freq !== "D" ? <span title={`A ${FREQ_WORDS[row.freq]} series has no 30-day low and high.`} data-lo30-step={row.id}>{FREQ_WORDS[row.freq]}</span>', cell)
        self.assertIn(">not held yet</span>", cell)
        self.assertNotIn(": null}", cell)

    @unittest.skipUnless(node_ok(), "node or the site's packages are not here")
    def test_every_step_has_a_word(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e",
                            "const b = await import('./lib/board.ts'); process.stdout.write(JSON.stringify(b.FREQ_WORDS));"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr)
        words = json.loads(r.stdout)
        for k, w in (("W", "weekly"), ("M", "monthly"), ("Q", "quarterly")):
            self.assertEqual(words[k], w)


# ScrollRegions.tsx transpiled by the site's TypeScript and run on stand-in elements, as tests/test_session583.py does
PROBE = r"""
const ts = (await import("typescript")).default;
const fs = await import("node:fs");
let code = ts.transpileModule(fs.readFileSync("components/ScrollRegions.tsx", "utf-8"),
  { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
code = code.replace(/^import .*$/gm, "").replace(/^"use client";/m, "");
code = "const usePathname = () => '/'; const useEffect = () => {};\n" + code;
const M = await import("data:text/javascript;base64," + Buffer.from(code).toString("base64"));
function el(label, ours, opts = {}) {
  const attrs = new Map([["aria-label", label]]);
  const kids = opts.kids ?? [];
  const e = { tagName: opts.tag ?? "DIV", dataset: Object.assign(ours ? { scrollLabel: "1" } : {}),
    getAttribute: (k) => attrs.has(k) ? attrs.get(k) : null, setAttribute: (k, v) => attrs.set(k, v), label: () => attrs.get("aria-label") };
  if (opts.container) e.contains = (o) => kids.includes(o);
  return e;
}
const run = (els) => { M.uniqueNames({ querySelectorAll: () => els }); return els.map((e) => e.label()); };
const box = el("Power, by hub and zone", true);
const section = el("Power, by hub and zone", false, { container: true, kids: [box] });
const two = [el("Gas", true), el("Gas", true)];
const gas = el("Gas", false, { container: true, kids: two });
const pre = el("Install", true, { tag: "PRE" });
const out = {
  board: run([section, box]),
  again: run([section, box]),
  twoInside: run([gas, ...two]),
  code: run([el("Install", false, { container: true, kids: [pre] }), pre]),
  apart: run([el("Reliability", true, { container: true }), el("Reliability", true, { container: true })]),
  standIns: run([el("Access", false), el("Access", true)]),
};
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(node_ok(), "node or the site's node_modules is not installed")
class Row44ARegionInsideItsNamesake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run(["node", "--input-type=module", "-e", PROBE], cwd=SITE, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-1500:])
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])

    def test_the_boards_table_is_not_counted_with_its_section(self):
        self.assertEqual(self.out["board"], ["Power, by hub and zone", "Power, by hub and zone, table"])

    def test_a_second_pass_keeps_the_name(self):
        self.assertEqual(self.out["again"], ["Power, by hub and zone", "Power, by hub and zone, table"])

    def test_two_tables_inside_one_section_are_counted_between_them(self):
        self.assertEqual(self.out["twoInside"], ["Gas", "Gas, table, 1 of 2", "Gas, table, 2 of 2"])

    def test_a_block_of_code_is_called_code(self):
        self.assertEqual(self.out["code"], ["Install", "Install, code"])

    def test_regions_side_by_side_count_as_before(self):
        self.assertEqual(self.out["apart"], ["Reliability, 1 of 2", "Reliability, 2 of 2"])
        self.assertEqual(self.out["standIns"], ["Access", "Access, 2 of 2"])


class Row45TheUsageLineRuns(unittest.TestCase):
    def test_the_usage_line_names_alias_register(self):
        head = src("site", "scripts", "check-board.mjs").replace(chr(13), "").split(chr(10) + "import ", 1)[0]
        usage = [ln for ln in head.splitlines() if "scripts/check-board.mjs" in ln]
        self.assertEqual(len(usage), 1, usage)
        self.assertIn("node --import ./scripts/alias-register.mjs scripts/check-board.mjs [base-url]", usage[0])
        self.assertIsNone(re.search(r"node --import \./scripts/alias-loader\.mjs scripts/check-board", head))
        self.assertTrue(os.path.isfile(os.path.join(SITE, "scripts", "alias-register.mjs")))


if __name__ == "__main__":
    unittest.main()
