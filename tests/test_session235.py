"""Session 235: "What a generator earns" on the brand, the capture price back on the page, scenario B as a PPA.

What is held to (the owner's task of 12 October 2026):

  the page takes the brand as the battery page does: it wraps what it draws in <Brand noUsage>, and neither the page nor
    the pieces this session wrote hold a color literal; its charts are the brand's bar chart, colors by token;
  the capture price is inside "What did it earn?", as one chart and one table, drawn from the model the download's
    capture tables are written from; a solar or a wind plant's figures carry a check key (cap|...) that
    scripts/check-values.mjs recomputes from the capture file with lib/capture.ts;
  the two downloads stay;
  "Is it worth building?": one button makes scenario B a PPA, and the results table holds the breakeven PPA price, the
    contract price at which NPV is zero (lib/seller/finance.ts, mirrored here in Python to 1e-6);
  no default moved: both scenarios open as merchant;
  no em dash in anything the session wrote.
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
SELLER = ("site", "app", "cost-of-power", "seller")

WRITTEN = [
    SELLER + ("page.tsx",), SELLER + ("model.ts",), SELLER + ("SellerScenarios.tsx",),
    ("site", "components", "tool", "GroupedBars.tsx"), ("site", "lib", "seller", "finance.ts"), ("site", "lib", "capture.ts"),
    ("site", "scripts", "check-values.mjs"), ("site", "scripts", "check-seller-scenarios.mjs"), ("site", "scripts", "test-seller-finance.mjs"),
    ("site", "app", "tokens.css"), ("docs", "methods", "generator_earns_algorithm.md"), ("tests", "test_session235.py"),
    ("archive", "sessions", "SESSION_235_REPORT.md"), ("docs", "brand", "review-235", "README.md"),
]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def code(text):
    """A TypeScript source without its comments (a comment may name a color; the code may not)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines() if not line.strip().startswith("//"))


def node(script):
    out = subprocess.run([NODE, "--input-type=module", "-e", script], cwd=SITE, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class TheBrand(unittest.TestCase):
    def test_the_page_wraps_what_it_draws_in_the_brand(self):
        page = src(*SELLER, "page.tsx")
        self.assertIn('import { Brand } from "@/components/Brand";', page)
        self.assertEqual(page.count("<Brand noUsage>"), 1)
        self.assertEqual(page.count("</Brand>"), 1)
        self.assertLess(page.index("<Brand noUsage>"), page.index("<ToolPage>"))
        self.assertLess(page.index("</ToolPage>"), page.index("</Brand>"))

    def test_no_color_literal_in_the_page_or_in_what_the_session_wrote(self):
        for path in (SELLER + ("page.tsx",), SELLER + ("model.ts",), SELLER + ("SellerScenarios.tsx",), ("site", "components", "tool", "GroupedBars.tsx")):
            text = code(src(*path))
            self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b(?![\w-])", text), path[-1])
            self.assertIsNone(re.search(r"rgba?\(", text), path[-1])

    def test_the_charts_are_the_brands_bar_chart_and_read_the_tokens(self):
        page, bars = src(*SELLER, "page.tsx"), src("site", "components", "tool", "GroupedBars.tsx")
        self.assertEqual(page.count("<GroupedBars "), 2)          # revenue by year, and the capture price
        self.assertNotIn("RevenueYears", code(page))                # the chart library's chart is not drawn here
        self.assertNotIn("legend=", code(page))                     # the series are named on the chart, no legend box
        for token in ("var(--color-accent)", "var(--color-ink)", "var(--color-muted)", "var(--color-rule)", "var(--color-surface)"):
            self.assertIn(token, bars)
        self.assertIn('data-direct-labels="1"', bars)
        self.assertIn('role="img"', bars)
        self.assertNotIn('"use client"', bars)                      # plain SVG from the server: no script

    def test_the_brand_file_gained_one_generic_rule(self):
        css = src("site", "app", "tokens.css")
        self.assertIn('.brand-a th[scope="row"] a,', css)
        self.assertNotIn("seller", css.lower())                     # a rule is for a kind of markup, never for a page


class TheCapturePrice(unittest.TestCase):
    def test_one_chart_and_one_table_inside_the_first_question(self):
        page = src(*SELLER, "page.tsx")
        q1, cap, q2 = page.index('data-question="1"'), page.index('<div id="capture" data-capture='), page.index('data-question="2"')
        self.assertLess(q1, cap)
        self.assertLess(cap, q2)
        block = page[cap:q2]
        self.assertEqual(block.count('<GroupedBars id="capture"'), 1)
        self.assertEqual(block[:block.index("data-months-csv")].count("<ToolTable "), 1)
        self.assertIn("What it earned per MWh against the hub average", block)
        self.assertIn('{ name: "Hub average", tone: "ink" }', block)
        self.assertIn("capView.rows.map", block)
        self.assertIn("capView.chart.map", block)

    def test_the_figures_carry_a_check_key_the_value_check_recomputes(self):
        page, check = src(*SELLER, "page.tsx"), src("site", "scripts", "check-values.mjs")
        self.assertIn("check={`cap|${iso}|${r.id}|${r.market}|${capView.fuel}|${span}|${what}`}", page)
        self.assertIn('if (p[0] === "cap") {', check)
        self.assertIn('"data", "seller", "capture.json"', check)
        self.assertIn("return C.stat(file, p[1], p[2], p[3], p[4], p[5], p[6]);", check)

    def test_the_page_and_the_download_are_one_arithmetic(self):
        model, route = src(*SELLER, "model.ts"), src(*SELLER, "tables.csv", "route.ts")
        view = model[model.index("const capView = "):model.index("// (b) the contract's twelve months")]
        for call in ("cap(h, fuel, m)", "yearCell(h[m]?.[fuel], y, NEAR)", "yearRows(mk)"):
            self.assertIn(call, view)
        for table in ("capture_last_twelve", "capture_by_year", "capture_hub_year"):
            self.assertIn(f'"{table}"', route)                      # the downloads stay
        page = src(*SELLER, "page.tsx")
        self.assertIn("MONTHS_CSV", page)
        self.assertGreaterEqual(page.count("${TABLES_CSV}${suffix}"), 1)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_key_is_the_capture_files_own_figure(self):
        got = node("""
          import fs from "node:fs";
          const C = await import("./lib/capture.ts");
          const file = JSON.parse(fs.readFileSync("data/seller/capture.json", "utf-8"));
          const out = [];
          for (const [grid, g] of Object.entries(file.grids)) for (const h of g.hubs) for (const m of ["rt", "da"]) for (const f of ["solar", "wind"]) {
            const t = C.twelve(h[m]?.[f], file.near);
            const y = C.yearCell(h[m]?.[f], "2025", file.near);
            out.push({ t: t ? [t.price, t.flat] : null, s: [C.stat(file, grid, h.id, m, f, "l12", "price"), C.stat(file, grid, h.id, m, f, "l12", "flat"), C.stat(file, grid, h.id, m, f, "l12", "rate")],
              y: y ? [y.price, y.flat] : null, sy: [C.stat(file, grid, h.id, m, f, "2025", "price"), C.stat(file, grid, h.id, m, f, "2025", "rate")] });
          }
          out.push({ bad: [C.stat(file, "ercot", "NOPE", "rt", "solar", "l12", "price"), C.stat(file, "ercot", "HB_HUBAVG", "xx", "solar", "l12", "price"), C.stat(file, "ercot", "HB_HUBAVG", "rt", "solar", "l12", "nope")] });
          console.log(JSON.stringify(out));
        """)
        self.assertEqual(got[-1]["bad"], [None, None, None])
        held = 0
        for r in got[:-1]:
            if r["t"] is None:
                self.assertEqual(r["s"], [None, None, None])
            else:
                held += 1
                price, flat = r["t"]
                self.assertEqual(r["s"][0], price)
                self.assertEqual(r["s"][1], flat)
                self.assertEqual(r["s"][2], (int((100 * price / flat) + 0.5) if 100 * price / flat >= 0 else -int(-(100 * price / flat) + 0.5)) if flat > 0 else None)
            if r["y"] is not None:
                self.assertEqual(r["sy"][0], r["y"][0])
        self.assertGreater(held, 30)


def crf(rate, years):
    return 1 / years if rate == 0 else rate / (1 - (1 + rate) ** -years)


def flows(a, rev, unit):
    """lib/seller/finance.ts, flows: per kW, the contract for the debt's years, the market on the rest."""
    dy = min(a["term"], a["life"])
    ds = a["capex"] * a["share"] / 100 * crf(a["rate"] / 100, dy)
    contract = a["cshare"] / 100 * a["cprice"] * unit
    out = [-a["capex"] * (1 - a["share"] / 100)]
    for t in range(1, a["life"] + 1):
        market = rev * (1 - a["deg"] / 100) ** (t - 1)
        income = contract + (1 - a["cshare"] / 100) * market if t <= dy else market
        out.append(income - a["fom"] - (ds if t <= dy else 0))
    return out


def npv(rate_pct, fl):
    return sum(v / (1 + rate_pct / 100) ** t for t, v in enumerate(fl))


def breakeven_ppa(a, rev, unit):
    """The contract price at which NPV is zero: -NPV at a price of 0 over the present value of a dollar of price."""
    share = a["cshare"] if a["cshare"] > 0 else 100
    at0 = npv(a["hurdle"], flows({**a, "cshare": share, "cprice": 0}, rev, unit))
    dy = min(a["term"], a["life"])
    per = sum(share / 100 * unit / (1 + a["hurdle"] / 100) ** t for t in range(1, dy + 1))
    return -at0 / per if per > 0 else None


CASES = [
    ({"capex": 1375, "share": 60, "rate": 8, "term": 35, "fom": 12.5, "deg": 0, "life": 35, "hurdle": 12, "cshare": 0, "cprice": 0}, 59.85, 2.58),
    ({"capex": 2100, "share": 60, "rate": 8, "term": 30, "fom": 32.25, "deg": 0, "life": 30, "hurdle": 12, "cshare": 40, "cprice": 25}, 110.0, 3.4),
    ({"capex": 1110, "share": 20, "rate": 8, "term": 10, "fom": 22, "deg": 2.6, "life": 20, "hurdle": 9.6, "cshare": 75, "cprice": 9}, 80.0, None),
    ({"capex": 1300, "share": 0, "rate": 8, "term": 30, "fom": 13.5, "deg": 0, "life": 30, "hurdle": 0, "cshare": 0, "cprice": 0}, 40.0, None),
]


@unittest.skipUnless(NODE, "node is not installed")
class TheBreakevenPpaPrice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node("""
          const F = await import("./lib/seller/finance.ts");
          const cases = %s;
          console.log(JSON.stringify({
            out: cases.map(([a, rev, e]) => { const c = e === null ? { kind: "toll", energyKw: 0 } : { kind: "energy", energyKw: e }; const p = F.breakevenPpa(a, rev, c); const b = F.asPpa(a, rev, c);
              return { p, at: F.npv(a.hurdle, F.flows({ ...a, cshare: F.ppaShare(a), cprice: p }, rev, c)), b, bnpv: b ? F.npv(b.hurdle, F.flows(b, rev, c)) : null }; }),
            defaults: F.defaultsOf({ capex: 1375, fom: 12.5, life: 35 }), keys: F.KEYS }));
        """ % json.dumps(CASES))

    def test_the_library_equals_the_python_mirror(self):
        for (a, rev, e), r in zip(CASES, self.got["out"]):
            want = breakeven_ppa(a, rev, 12 if e is None else e)
            self.assertAlmostEqual(r["p"], want, delta=1e-6)
            self.assertAlmostEqual(r["at"], 0, delta=1e-6)             # NPV is zero at the breakeven price

    def test_make_b_a_ppa_sets_two_assumptions_and_no_other(self):
        for (a, rev, e), r in zip(CASES, self.got["out"]):
            b = r["b"]
            whole = breakeven_ppa({**a, "cshare": 100}, rev, 12 if e is None else e)
            self.assertEqual(b["cshare"], 100)
            self.assertGreaterEqual(b["cprice"], whole - 1e-9)
            self.assertLess(b["cprice"] - whole, 0.01 + 1e-9)        # rounded up to the cent
            self.assertGreaterEqual(r["bnpv"], -1e-9)
            for k, v in a.items():
                if k not in ("cshare", "cprice"):
                    self.assertEqual(b[k], v)

    def test_no_default_moved(self):
        self.assertEqual(self.got["defaults"], {"capex": 1375, "share": 60, "rate": 8, "term": 35, "fom": 12.5, "deg": 0, "life": 35, "hurdle": 12, "cshare": 0, "cprice": 0, "ppa": 35, "itc": 0, "ptc": 0})   # session 264: the PPA term, its default the life; session 353: no tax credit
        self.assertEqual(len(self.got["keys"]), 13)   # session 264: eleven; session 353: thirteen

    def test_the_page_offers_it_and_shows_the_row(self):
        block = src(*SELLER, "SellerScenarios.tsx")
        self.assertIn('data-make-ppa="1"', block)
        self.assertIn("update({ ...s, b: ppa, view: \"b\" })", block)
        self.assertIn("no published price is held", block)
        rows = re.findall(r'^    row\("(\w+)"', block, flags=re.M)
        self.assertEqual(rows, ["revenue", "capture", "month", "coverage", "npv", "irr", "contract", "ppa", "battery"])
        self.assertIn('"Breakeven PPA price"', block)
        self.assertIn("the contract price at which NPV at the hurdle rate is zero", block)


class TheNoteAndTheWriting(unittest.TestCase):
    def test_the_method_note_says_what_the_page_draws_now(self):
        note = src("docs", "methods", "generator_earns_algorithm.md")
        for words in ("### 4.19 What it earned per MWh against the hub average: one chart and one table (session 235)",
                      "cap|<grid>|<hub>|<market>|<fuel>|<span>|<stat>", "The breakeven PPA price (session 235)", '"Make B a PPA" (session 235)', "Session 235: nine rows."):
            self.assertIn(words, note)

    def test_no_em_dash_in_what_the_session_wrote(self):
        for path in WRITTEN:
            full = os.path.join(ROOT, *path)
            if os.path.exists(full):
                self.assertNotIn(EM, src(*path), "/".join(path))


if __name__ == "__main__":
    unittest.main()
