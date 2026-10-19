"""Session 265: "What a datacenter pays" (/cost-of-power), deep: the chain of 14 October 2026.

Energy Research Warehouse (ERW). What is held here:
- the delivery table states only what the tariffs state (the owner's list of 14 October 2026): a line billed per kVA
  (a power factor the tariff does not state) or per meter or ESI ID (a count of meters it does not state) is
  conditional, as is a line the tariff applies only to some loads; the first total sums only the lines with no
  condition and says so; session 236's total stands below it, labelled with its two conditions; the three lines the
  tariffs apply only to some loads are named under the table and are in neither total;
- the library's figures by hand, from the site's own file, and by node where node reads TypeScript;
- the cost of capital is labelled "a generator's WACC, Lazard" and stays an editable field at 9.6;
- a value of the address outside its bounds is brought inside them and the panel says so (the size, the hours, the
  shares, each scenario's assumptions; a grid or region not held);
- "Will the power be there?" keeps today's read: scarcity_hours_by_grid is not in the live set on 14 October 2026;
- session 265b: "How soon?" reads large_load_public (public by the owner's ruling of 14 October 2026, landed by session
  272) through lib/largeloadpublic.ts: counts, the newest wait as written and the newest megawatt figure, each with its
  document's link, never a sum, every number under a check key dcll|<grid>|<stat>;
- the review pack exists and the old note is gone; the README row points at the pack;
- the replication files keep the page's defaults; the carbon file's hourly window is the live set's.
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


def rows():
    return json.loads(src("site", "data", "datacenter", "texas_delivery.json"))["rows"]


def condition(r):
    """The library's conditionOf, by hand."""
    if (r.get("applies") or "").strip().lower().startswith("conditional"):
        return "tariff"
    u = r["unit"].lower().replace(" ", "")
    if "kva" in u:
        return "power_factor"
    if "meter" in u or "esiid" in u:
        return "meters"
    return None


def per_mwh(r, mw):
    u = r["unit"].lower().replace(" ", "")
    if "kwh" in u:
        return r["value"] * 1000
    if "4cp" in u or "kw" in u or "kva" in u:
        return r["value"] * 12000 / 8760
    if "customer" in u or "meter" in u or "esiid" in u:
        return r["value"] * 12 / (mw * 8760)
    return None


def totals(utility, mw):
    held = total = 0.0
    assumed = 0
    for r in rows():
        if r["utility"] != utility or condition(r) == "tariff":
            continue
        v = per_mwh(r, mw)
        if v is None:
            continue
        total += v
        if condition(r) is None:
            held += v
        else:
            assumed += 1
    return held, total, assumed


class TheDeliveryTable(unittest.TestCase):
    def test_the_conditions_by_hand(self):
        got = {}
        for r in rows():
            got.setdefault(r["utility"], []).append(condition(r))
        self.assertEqual(got["Oncor"].count(None), 9)
        self.assertEqual(got["AEP Texas"].count("tariff"), 1)
        self.assertEqual(sum(c == "tariff" for cs in got.values() for c in cs), 3)        # the three named under the table
        self.assertGreater(got["CenterPoint Energy Houston Electric"].count("power_factor"), 0)
        self.assertGreater(got["Texas-New Mexico Power"].count("meters"), 0)

    def test_the_totals_by_hand(self):
        # Oncor and AEP Texas bill per kW, per kWh and per retail customer: the two totals are one figure
        for u, shown in (("Oncor", "8.81"), ("AEP Texas", "8.39")):
            held, total, assumed = totals(u, 100)
            self.assertEqual((assumed, f"{held:.2f}", f"{total:.2f}"), (0, shown, shown), u)
        # CenterPoint and Texas-New Mexico Power: session 236's totals only with the two conditions
        for u, shown in (("CenterPoint Energy Houston Electric", "7.67"), ("Texas-New Mexico Power", "7.09")):  # session 307: 7.10 before the rider DCRF was counted once
            held, total, assumed = totals(u, 100)
            self.assertGreater(assumed, 0, u)
            self.assertEqual(f"{total:.2f}", shown, u)

    def test_the_library_gives_the_same_figures(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        script = ("import fs from 'node:fs'; const D = await import('./lib/datacenter/delivery.ts'); "
                  "const f = JSON.parse(fs.readFileSync('data/datacenter/texas_delivery.json', 'utf-8')); const out = {}; "
                  "for (const mw of [1, 100, 1000]) for (const u of D.utilitiesOf(f.rows)) { const d = D.deliveryOf(f.rows, u, mw); "
                  "out[mw + '|' + u] = { held: d.held, total: d.total, assumed: d.assumed, stat: D.deliveryStat(f.rows, mw, D.slugOf(u) + ':held') }; } "
                  "out.conds = f.rows.map((r) => D.conditionOf(r)); console.log(JSON.stringify(out));")
        r = subprocess.run([exe, "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
        if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got["conds"], [condition(x) for x in rows()])
        for mw in (1, 100, 1000):
            for u in {x["utility"] for x in rows()}:
                held, total, assumed = totals(u, mw)
                theirs = got[f"{mw}|{u}"]
                self.assertAlmostEqual(theirs["held"], held, places=9)
                self.assertAlmostEqual(theirs["total"], total, places=9)
                self.assertEqual(theirs["assumed"], assumed)
                self.assertAlmostEqual(theirs["stat"], round(held * 100) / 100, places=9)

    def test_the_page_labels_the_conditions_and_the_sum_says_so(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        table = page.split("function DeliveryTable", 1)[1].split("const matrixTip", 1)[0]
        for words in ("Delivery charges in Texas, as the tariffs state them, USD per MWh",
                      "Total delivery, the lines with no condition",
                      "Total with the conditional lines: a power factor of 1, one meter",
                      "so a figure resting on either is marked conditional and is left out of the first total",
                      "In neither total, because the tariff applies them only to some loads: ",
                      'data-delivery-conditional="1">conditional</span>', 'fig(d.utility, "held")'):
            self.assertIn(words, table, words)
        self.assertIn("function linesTip(utility: string, kind: string): string {", page)        # each figure names its lines
        self.assertIn("function conditionalLines(): string[] {", page)
        self.assertIn("Wholesale transmission, all of ERCOT: the Commission's rate to the wires utilities, not a line of a retail tariff", page)
        lib = src("site", "lib", "datacenter", "delivery.ts")
        self.assertIn('export type Condition = "tariff" | "power_factor" | "meters" | null;', lib)
        self.assertIn('const v = what === "total" ? d.total : what === "held" ? d.held : d.components.find((c) => c.kind === what)?.perMwh;', lib)


class TheCostOfCapital(unittest.TestCase):
    def test_the_label_and_the_field(self):
        fin = src("site", "lib", "datacenter", "finance.ts")
        self.assertIn('hurdle: { key: "hurdle", letter: "h", label: "Cost of capital: a generator\'s WACC, Lazard", unit: "percent a year", min: 0, max: 40,', fin)
        self.assertIn("export const LIFE = 20, HURDLE = 9.6;", fin)
        self.assertIn('"hurdle"', fin.split("export const KEYS: Key[] = ", 1)[1].split(";", 1)[0])   # still one of the editable fields


class OutsideItsBounds(unittest.TestCase):
    def test_the_line_says_what_is_used(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("function outsideOf(q: Record<string, string | undefined>, x: Inputs, gridName: string = x.grid.toUpperCase()): string[] {", page)
        self.assertIn('data-clamped="1">{outsideOf(q, x, g?.name).join(" ")}</p>', page)
        for words in ('is outside ${lo} to ${hi}${unit}, so ${v < lo ? lo : hi} is used.', 'is not a number, so the default is used.',
                      'is not held here, so ${gridName} is shown.', 'is not held for this grid, so ${x.region} is shown.'):
            self.assertIn(words, page, words)
        for name in ('one("mw", ', 'one("n", ', 'one("pct", ', 'one("shift", ', "one(`${side}${f.letter}`, "):
            self.assertIn(name, page, name)

    def test_the_plural_of_the_months_without_carbon(self):
        answers = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        self.assertIn('${l.of - l.months === 1 ? "has" : "have"} no intensity in the table and ${l.of - l.months === 1 ? "is" : "are"} left out', answers)


class TodaysReadsKept(unittest.TestCase):
    def test_the_scarcity_table_is_read_by_the_answers_only(self):
        # session 280: scarcity_hours_by_grid is in the live set (session 278 read it there) and "Will the power be
        # there?" reads it, through lib/datacenter/answers.ts; the page's model does not read it itself
        self.assertIn('export const SBG_TABLE = "scarcity_hours_by_grid"', src("site", "lib", "datacenter", "answers.ts"))
        self.assertNotIn("scarcity_hours_by_grid", src("site", "app", "cost-of-power", "model.ts"))


class HowSoonReadsThePublicStatements(unittest.TestCase):
    """Session 265b: large_load_public, public by the owner's ruling of 14 October 2026 (session 272), on "How soon?"."""

    def test_the_page_reads_it_through_session_272s_helper(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn('import { largeLoadStatements } from "@/lib/largeloadpublic";', page)
        # session 280: the grid's rows are read once and both counted and listed
        self.assertIn("const gridRows = (await largeLoadStatements(M.x.grid)) as unknown as Statement[];", page)
        self.assertIn("stated = { s: statedOf(gridRows), grid: M.x.grid };", page)
        self.assertIn("<HowSoon a={M.answers.data} f={M.answerFacts} rules={M.rules} b={siteB} stated={stated} lists={lists} />", page)

    def test_facts_with_a_link_and_no_quoted_text(self):
        answers = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        line = answers.split("function StatedLine", 1)[1].split("/** Session 280: every statement", 1)[0].split("export function HowSoon", 1)[0]  # session 280: its list follows
        for words in ("<Num check={`dcll|${grid}|${stat}`} raw={v}>", '<a href={r.source_url} rel="noopener noreferrer">',
                      "The figures are not added", 'data-answer-stated="1"', 'data-answer-stated="failed"'):
            self.assertIn(words, line, words)
        for column in ("sentence", "quote", "load_scope"):                              # no document's words
            self.assertNotIn(column, line, column)
        self.assertEqual(answers.count("<StatedLine stated={stated} gridName={f.gridName} />"), 2)
        self.assertIn("publishes no regular report of large load waiting or energized that the warehouse holds", answers)

    def test_the_counts_and_the_check_key(self):
        lib = src("site", "lib", "datacenter", "statements.ts")
        for name in ('case "statements"', 'case "entities"', 'case "documents"', 'case "waits"', 'case "mws"', 'case "mw:newest"', 'case "wait:newest"'):
            self.assertIn(name, lib, name)
        self.assertNotIn("reduce(", lib)                                                # never a sum across rows
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "dcll") {', check)
        self.assertIn('table_name: "eq.large_load_public", "extra->>grid": `eq.${p[1]}`', check)

    def test_the_figures_by_node(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        script = ("const S = await import('./lib/datacenter/statements.ts'); "
                  "const rows = [{ event_date: '2026-09-18', parties: 'A', mw: null, source_url: 'u1', row_kind: 'wait', duration_as_stated: '60 days' }, "
                  "{ event_date: '2026-09-17', parties: 'B', mw: 1400, source_url: 'u2', row_kind: 'mw' }, { event_date: '2026-09-17', parties: 'B', mw: 22000, source_url: 'u2', row_kind: 'mw' }, "
                  "{ event_date: '2026-01-01', parties: 'C', mw: null, source_url: 'u3', row_kind: 'wait', duration_as_stated: 'several years' }]; "
                  "const s = S.statedOf(rows); console.log(JSON.stringify(['statements','entities','documents','waits','mws','mw:newest','wait:newest'].map((k) => S.statedStat(s, k) ?? null).concat([S.leadingNumber('18 to 24 months'), S.leadingNumber('several years'), s.newest])));")
        r = subprocess.run([exe, "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
        if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1]), [4, 3, 3, 2, 2, 22000, 60, 18, None, "2026-09-18"])


class ThePack(unittest.TestCase):
    def test_the_pack_replaces_the_note(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "reviews", "packs", "datacenter.md")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "docs", "howitworks", "datacenter.md")))
        readme = src("docs", "howitworks", "README.md")
        self.assertIn("| What a datacenter pays | `/cost-of-power` | [the review pack](../reviews/packs/datacenter.md) |", readme)
        pack = src("docs", "reviews", "packs", "datacenter.md")
        self.assertEqual(pack.count(chr(0x2014)), 0)
        self.assertIn("do erw_2026_datacenter_replication.do", pack)

    def test_the_replication_keeps_the_pages_defaults(self):
        py = src("site", "public", "datacenter", "erw_2026_datacenter_replication.py")
        self.assertIn("MW, GPU_KW, PUE = 100, 1.3, 1.56", py)
        self.assertIn("SCARCITY_USD = 1000.0", py)
        lib = src("site", "lib", "datacenter.ts")
        self.assertIn("export const DEFAULTS = { mw: 100, n: 100, pct: 5, shift: 20, gpu: ASSUMED.gpu.value, pue: ASSUMED.pue.value };", lib)
        self.assertIn("gpu: { value: 1.3,", lib)
        self.assertIn("pue: { value: 1.56,", lib)
        carbon = src("site", "public", "datacenter", "erw_2026_datacenter_carbon.csv")
        self.assertIn("its rolling window of 430 days (session 245; 35 until then)", carbon.split("\n")[2])
        self.assertEqual(carbon.count(chr(0x2014)), 0)


if __name__ == "__main__":
    unittest.main()
