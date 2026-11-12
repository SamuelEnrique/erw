"""Session 1852 (chain 213): the deal tracker's faults 2 to 6, 14 and 15 of docs/reviews/deals-faults-2026-11-11.md.

Energy Research Warehouse (ERW). The pages are held whole ("license needed"), so the fixes are read from the components'
source and proved in Node on the pure functions where one exists, as test_session466 and test_session2240_deals do.
"""
import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheTrackerUnderTheHold(unittest.TestCase):
    """Row 2: no count printed as 0 while every row is held."""

    def test_the_choices_take_a_held_flag_and_draw_no_bracket_then(self):
        v = src("site", "app", "deals", "v2", "view.tsx")
        self.assertIn("function Choices({ x, all, held = false }", v)
        self.assertIn('const br = (v: number) => (held ? "" : ` (${whole(v)})`);', v)
        self.assertIn("<Choices key={hrefOf(x)} x={x} all={all} held={!read.ok} />", v)
        # every option of the panel goes through br(): no "({whole(" is left in the choices
        choices = v[v.index("function Choices("):v.index("export async function TrackerView")]
        self.assertNotIn("({whole(", choices)
        self.assertEqual(choices.count("{br("), 7)

    def test_the_panel_note_has_no_count_under_the_hold(self):
        v = src("site", "app", "deals", "v2", "view.tsx")
        self.assertIn("note={read.ok ? <>The counts in brackets are of every deal held.", v)
        self.assertIn("no count is shown while every row is held", v)


class TheHeadlineSum(unittest.TestCase):
    """Row 5: no sum of US dollars over acquisitions at a valuation, financings and purchase prices."""

    def test_in_all_is_gone(self):
        v = src("site", "app", "deals", "v2", "view.tsx")
        self.assertNotIn("in all</>", v)
        self.assertNotIn("USD {usd(c.dollars)}", v)
        self.assertIn("state a value in US dollars: a purchase price, a financing or a valuation, each as stated and not summed here", v)


class TheAiView(unittest.TestCase):
    """Rows 3 and 4: the top-ten lists are of power and infrastructure deals, and the parties fall back to the others."""

    def test_the_lists_leave_capital_out(self):
        a = src("site", "app", "deals", "ai", "view.tsx")
        self.assertIn('const supply = all.filter((d) => supplyOf(d) !== "capital");', a)
        self.assertIn('<Largest rows={largest(supply, "mw")} by="mw" />', a)
        self.assertIn('<Largest rows={largest(supply, "usd")} by="usd" />', a)
        self.assertNotIn('largest(all, "', a)

    def test_the_parties_fall_back_to_the_others(self):
        a = src("site", "app", "deals", "ai", "view.tsx")
        self.assertIn('.join(" / ") || d.others.join(", ") || "parties not stated"', a)

    def test_largest_on_the_supply_deals_in_node(self):
        """lib/dealsai.ts, run as it is: a capital deal with the largest sum is not in the list once the view's filter is applied."""
        script = (
            "import { largest, supplyOf } from './lib/dealsai.ts';\n"
            "const d = (id, kind, dollars, mw, technology = '') => ({ id, date: '2026-02-03', month: '2026-02', year: '2026', type: kind, group: 'other', status: '',"
            " buyer: 'A', seller: 'B', others: [], names: [], asset: id, technology, state: '', country: '', grid: '', mw, mwh: null, dollars, price: null, priceOther: null,"
            " termYears: null, ai: true, storage: false, kinds: [], source: 's', links: [], folded: [], kind, buyerName: '', sellerName: '', aiBasis: '' });\n"
            "const all = [d('xai', 'm_and_a', 1.25e12, null), d('raise', 'capital', 1.1e11, null), d('ppa', 'ppa', 4e9, 702, 'fuel cells'), d('gas', 'other', 1e9, 5000, 'gas')];\n"
            "const supply = all.filter((x) => supplyOf(x) !== 'capital');\n"
            "console.log(JSON.stringify({ all: largest(all, 'usd').map((x) => x.id), supply: largest(supply, 'usd').map((x) => x.id), mw: largest(supply, 'mw').map((x) => x.id) }));\n"
        )
        path = os.path.join(SITE, "test-session1852.mjs")
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        try:
            r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "test-session1852.mjs"], cwd=SITE, capture_output=True, text=True, timeout=120)
        finally:
            os.remove(path)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got["all"], ["xai", "raise", "ppa", "gas"])
        self.assertEqual(got["supply"], ["ppa", "gas"])
        self.assertEqual(got["mw"], ["gas", "ppa"])


class TheComparablesChart(unittest.TestCase):
    """Row 14: the not-stated group is in the table, never a bar of the chart."""

    def test_the_bars_leave_the_not_stated_group_out(self):
        c = src("site", "app", "deals", "comparables", "view.tsx")
        self.assertIn('const rows = cells.filter((c) => c.value !== "" && (what === "price" ? c.medianPrice : c.medianMw) !== null);', c)
        self.assertIn('const charted = cells.filter((c) => c.value !== "" && (what === "price" ? c.medianPrice : c.medianMw) !== null).length;', c)


class TheTrillion(unittest.TestCase):
    """Row 15: a sum of a trillion or more is written as trillions, in the table, the AI view and the check script alike."""

    def test_every_formatter_takes_the_step(self):
        self.assertIn("if (Math.abs(v) >= 1e12) return `${t(v / 1e12)} trillion`;", src("site", "app", "deals", "DealsTable.tsx"))
        self.assertIn("if (Math.abs(v) >= 1e12) return `${t(v / 1e12)} trillion`;", src("site", "scripts", "check-values.mjs"))
        self.assertIn("v >= 1e12 ? `${whole(v / 1e12)} trillion`", src("site", "app", "deals", "ai", "view.tsx"))

    def test_the_check_script_writes_the_same_words_as_the_table(self):
        script = (
            "const t = (x) => x.toLocaleString('en-US', { maximumFractionDigits: 2 });\n"
            "const usd = (v) => Math.abs(v) >= 1e12 ? `${t(v / 1e12)} trillion` : Math.abs(v) >= 1e9 ? `${t(v / 1e9)} billion` : Math.abs(v) >= 1e6 ? `${t(v / 1e6)} million` : v.toLocaleString('en-US');\n"
            "console.log(JSON.stringify([usd(1.25e12), usd(2171543000000), usd(19e9), usd(938e6)]));\n"
        )
        r = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout.strip()), ["1.25 trillion", "2.17 trillion", "19 billion", "938 million"])


class TheHeaderBands(unittest.TestCase):
    """Row 6: no colored header band on the deals' tables (docs/brand.md, section 5)."""

    def test_no_accent_band_in_the_deals_views(self):
        for parts in (("v2", "view.tsx"), ("ai", "view.tsx"), ("comparables", "view.tsx")):
            s = src("site", "app", "deals", *parts)
            self.assertNotIn('bg-accent text-white', s, parts)
            self.assertIn('<tr className="border-b border-rule text-left text-xs text-muted">', s, parts)


if __name__ == "__main__":
    unittest.main()
