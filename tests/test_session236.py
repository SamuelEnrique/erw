"""Session 236: "What a datacenter pays" (/cost-of-power) on the brand, for a buyer of power.

The owner's chain prompt of 12 October 2026: the brand; the four questions stay (what will it pay, will the power be
there, how clean, how soon); A and B compare two sites or two contracts; USD 1,000 per MWh stays the scarcity level for
every grid, stated on the page, with each grid's own signal as a second count where a table is held; the delivery
charges are one row a component in USD per MWh with the total, and the tariff lines go to the CSV.

  TheBrand         the page takes the brand through components/Brand.tsx and writes no color of its own
  TheQuestions     the four questions in their order, then the two of the decisions
  Scarcity         the level and its words; CAISO's notices as a second count; ERCOT's reserve adder as a second count, where it was published
  Delivery         lib/datacenter/delivery.ts against a second computation here, from the site's own file
  TwoSites         scenario B's own site: the address parameter, who reads it, who carries it
  TheNoteAndFiles  the method note's sections, the download's tables, the check key, and no em dash
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """A source file without its comments (line comments and JSX comments), for a search of what is drawn."""
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", text)


PAGE = ("site", "app", "cost-of-power", "page.tsx")
FACE = [PAGE, ("site", "app", "cost-of-power", "LoadAnswers.tsx"), ("site", "app", "cost-of-power", "LoadCharts.tsx"), ("site", "app", "cost-of-power", "LoadSiteB.tsx"),
        ("site", "app", "cost-of-power", "LoadScenarios.tsx"), ("site", "app", "cost-of-power", "LoadHeadline.tsx")]


class TheBrand(unittest.TestCase):
    def test_the_page_is_wrapped_in_the_brand_as_the_battery_page_is(self):
        page = src(*PAGE)
        self.assertIn('import { Brand } from "@/components/Brand";', page)
        self.assertEqual(page.count("<Brand noUsage>"), 1)
        self.assertLess(page.index("<Brand noUsage>"), page.index("<ToolPage>"))
        self.assertLess(page.index("</ToolPage>"), page.index("</Brand>"))
        self.assertIn("<Brand noUsage>", src("site", "app", "cost-of-power", "battery", "page.tsx"))

    def test_no_color_and_no_font_of_the_pages_own(self):
        for name in FACE:
            text = code(src(*name))
            self.assertEqual(re.findall(r"#[0-9A-Fa-f]{3,8}\b", text), [], "/".join(name))      # no color literal: the tokens only
            self.assertNotRegex(text, r"rgba?\(|hsl\(", "/".join(name))
            self.assertNotRegex(text, r"fontFamily|font-family", "/".join(name))
        page = src(*PAGE)
        for token in ('color: "var(--color-muted)"', 'color: "var(--color-accent)"', 'color: "var(--color-ink)"', '"var(--color-surface)"'):
            self.assertIn(token, page)                                                         # the legend and the view switch name tokens

    def test_the_chart_reads_the_tokens_at_its_own_box(self):
        chart = src("site", "app", "cost-of-power", "LoadCharts.tsx")
        self.assertIn('from "@/components/svgchart"', chart)   # session 317: the SVG chart draws in the tokens by name (var(--color-...)), at its own box by CSS
        self.assertEqual(len(re.findall(r'token\("(?:muted|accent|ink)", el\)', chart)), 4)
        lib = src("site", "components", "echarts.ts")
        # additive: without an element the token is read at the page's root, as every other chart reads it
        self.assertIn("export function token(name: string, from?: Element | null): string {", lib)
        self.assertIn("getComputedStyle(from ?? document.documentElement)", lib)
        self.assertIn('fontFamily: from ? getComputedStyle(from).fontFamily : "system-ui, sans-serif"', lib)

    def test_the_page_has_no_style_sheet_of_its_own(self):
        d = os.path.join(ROOT, "site", "app", "cost-of-power")
        self.assertEqual([f for f in os.listdir(d) if f.endswith(".css")], [])                 # the brand is app/tokens.css, the one file


class TheQuestions(unittest.TestCase):
    def test_the_four_questions_stay_in_their_order_then_the_two_of_the_decisions(self):
        page = src(*PAGE)
        titles = ['<ToolSection title="What will it pay?" id="pays">', '<ToolSection title="Will the power be there?" id="there">', '<ToolSection title="How clean?" id="clean">',
                  '<ToolSection title="How soon?" id="soon">', '<ToolSection title="Which option is better?" id="scenarios">', '<ToolSection title="What matters most" id="matters">']
        at = [page.index(t) for t in titles]
        self.assertEqual(at, sorted(at))
        self.assertEqual(re.findall(r'<ToolSection title="([^"]+)"', page), [re.search(r'title="([^"]+)"', t).group(1) for t in titles])

    def test_the_block_reads_as_two_sites_or_two_contracts(self):
        page = src(*PAGE)
        self.assertIn("<Sub>Scenarios A and B: two sites, or two contracts</Sub>", page)
        how = page.split('data-how-to-compare="1">', 1)[1].split("</p>", 1)[0]
        for words in ("To compare two sites, give scenario B a site of its own here", "To compare two contracts, give A and B a different contract share and price below", "sets B against A"):
            self.assertIn(words, how)
        self.assertLess(page.index("<Sub>Scenarios A and B: two sites, or two contracts</Sub>"), page.index("<LoadSiteB "))
        self.assertLess(page.index("<LoadSiteB "), page.index("<LoadScenarios "))
        self.assertIn("then two sites or two contracts side by side", page)                    # the lead


class Scarcity(unittest.TestCase):
    def test_one_level_for_every_grid_stated_where_the_count_stands(self):
        lib = src("site", "lib", "datacenter", "answers.ts")
        self.assertIn("export const SCARCITY_USD = 1000;", lib)                                 # the level did not move
        self.assertEqual(len(re.findall(r"SCARCITY_USD\s*=", lib)), 1)
        face = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        self.assertIn('export const LEVEL_WORDS = "USD 1,000 per MWh is the level for every grid:', face)
        self.assertIn('<span key="w" data-level-words="1">{LEVEL_WORDS}</span>', face)
        self.assertIn('<N key="h" pre={f.pre} stat="scarce:hours" a={a} />', face)             # the count beside it carries its check key

    def test_caisos_notices_are_a_second_count_with_check_keys(self):
        lib = src("site", "lib", "datacenter", "answers.ts")
        self.assertIn('table_name: "eq.caiso_grid_emergencies"', lib)
        self.assertIn('if (p[1] === "own") return a.notices.own ?', lib)
        face = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        self.assertIn('<span key="n" data-own-signal="count"><N pre={f.pre} stat="notices:count" a={a} /></span>', face)
        self.assertIn('<span key="n" data-own-signal="table"><N pre={f.pre} stat="notices:own:count" a={a} /></span>', face)
        self.assertIn("so this is not a count of none", face)                                  # a table that ends before the months is said
        self.assertIn("caiso_grid_emergencies", [r.split(",")[0] for r in src("warehouse", "metadata", "coverage.csv").splitlines()])

    def test_the_table_s_own_last_twelve_months(self):
        # elevenBefore: the month eleven months before a month label, as lib/datacenter/answers.ts computes it
        def eleven_before(m):
            t = int(m[:4]) * 12 + int(m[5:7]) - 1 - 11
            return f"{t // 12}-{t % 12 + 1:02d}"
        self.assertEqual([eleven_before(m) for m in ("2025-04", "2025-12", "2025-11", "2026-01")], ["2024-05", "2025-01", "2024-12", "2025-02"])
        lib = src("site", "lib", "datacenter", "answers.ts")
        self.assertIn("const y = Number(m.slice(0, 4)), k = Number(m.slice(5, 7)) - 1 - 11;", lib)
        self.assertIn('return `${Math.floor(t / 12)}-${String((t % 12) + 1).padStart(2, "0")}`;', lib)

    def test_ercots_own_signal_is_its_reserve_adder_counted_where_it_was_published(self):
        # after the hand-back: session 244 landed ercot_rtm_price_adders the same night (07:05 UTC on 13 October 2026), so
        # the line "is coming" went and the count stands: the hours the operating reserve demand curve's on-line adder
        # (the hour's mean) was at or above a stated level, over the part of the page's months the adder was published in
        lib = src("site", "lib", "datacenter", "answers.ts")
        self.assertIn("export const ADDER_USD = 100;", lib)
        self.assertIn('export const ADDER_TABLE = "ercot_rtm_price_adders", ADDER_VARIABLE = "rtorpa_mean", ADDER_ENTITY = "ercot:system";', lib)
        self.assertNotIn("rtrdpa", code(lib))                                                  # the reliability deployment adder is not read: nothing is spliced
        # both reads are bounded in time (an unbounded sort of the variable timed out on 13 October)
        self.assertEqual(lib.count("ts_utc: `gte.${iso("), 2)
        face = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        for words in ('<span key="n" data-own-signal="count"><N pre={f.pre} stat="adders:hours" a={a} /></span>', '<N pre={f.pre} stat="adders:held" a={a} />',
                      '<span key="n" data-own-signal="table"><N pre={f.pre} stat="adders:own:hours" a={a} /></span>', "at least USD ${a.adders.level} per MWh, in the part of these months it was published",
                      "published it until {dayWords(a.adders.last)} and no longer", "so it is not a count of the twelve months", "is another thing and is not counted", "Not the months of the price count above."):
            self.assertIn(words, face, words)
        self.assertNotIn("is coming", face)
        self.assertNotIn("coming: true", face)
        tables = [r.split(",")[0] for r in src("warehouse", "metadata", "coverage.csv").splitlines()[1:]]
        self.assertEqual([t for t in tables if re.search(r"ordc|adder", t)], ["ercot_rtm_price_adders"])
        # the table is loaded for pages in review (review_hold): the public key reads it, and no count a visitor sees names it
        live = src("warehouse", "supabase", "live_set.yaml")
        self.assertIn("  - '^ercot_rtm_price_adders$'", live)
        self.assertRegex(live.split("review_hold:", 1)[1], r"(?m)^  - ercot_rtm_price_adders\b")
        self.assertEqual(face.count('<span key="n" data-own-signal="none">not held</span>'), 3)   # CAISO with no notice, ERCOT with no hour of the adder, any other grid

    def test_the_adders_count_by_hand(self):
        # twelve months October 2025 to September 2026 in Central standard time (six hours behind UTC)
        l12 = [f"2025-{m:02d}" for m in (10, 11, 12)] + [f"2026-{m:02d}" for m in range(1, 10)]
        held = ["2025-10-01T05:00:00+00:00",    # 23:00 on 30 September: before the months
                "2025-10-01T06:00:00+00:00", "2025-12-05T04:00:00+00:00", "2025-12-05T05:00:00+00:00"]   # the last: 23:00 on 4 December
        high = ["2024-12-05T05:00:00+00:00",    # one hour before the 8,760 hours to the last hour held
                "2024-12-05T06:00:00+00:00", "2025-06-30T20:00:00+00:00", "2025-10-01T06:00:00+00:00"]
        want = {"level": 100, "hours": 1, "held": 3, "first": "2025-10-01", "last": "2025-12-04", "own": {"from": "2024-12-05", "to": "2025-12-04", "hours": 3}}
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        script = ("const R = await import('./lib/datacenter/answers.ts'); "
                  f"console.log(JSON.stringify([R.adders({json.dumps(held)}, {json.dumps(high)}, {json.dumps(l12)}, 6), R.adders({json.dumps(held[:1])}, {json.dumps(high)}, {json.dumps(l12)}, 6)]));")
        r = subprocess.run([exe, "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
        if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(got[0], want)
        self.assertIsNone(got[1])                                                              # no hour of the adder in the months: no count


def basis(unit):
    u = re.sub(r"\s+", "", unit.lower())
    if "kwh" in u:
        return "energy"
    if "4cp" in u:
        return "four_peak_demand"
    if "kw" in u or "kva" in u:
        return "billing_demand"
    if "customer" in u or "meter" in u or "esiid" in u:
        return "customer_month"
    return None


def per_mwh(row, mw):
    b = basis(row["unit"])
    if b is None:
        return None
    if b == "energy":
        return row["value"] * 1000
    if b == "customer_month":
        return row["value"] * 12 / (mw * 8760)
    return row["value"] * 12000 / 8760


def delivery(rows, utility, mw):
    out = {"transmission": 0.0, "distribution": 0.0, "other": 0.0}
    left = 0
    for r in rows:
        if r["utility"] != utility:
            continue
        kind = r.get("kind") if r.get("kind") in ("distribution", "other") else "transmission"
        if (r.get("applies") or "").strip().lower().startswith("conditional"):
            left += 1
            continue
        v = per_mwh(r, mw)
        if v is None:
            continue
        out[kind] += v
    out["total"] = out["transmission"] + out["distribution"] + out["other"]
    return out, left


class Delivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = json.loads(src("site", "data", "datacenter", "texas_delivery.json"))
        cls.rows = cls.file["rows"]
        cls.utilities = list(dict.fromkeys(r["utility"] for r in cls.rows))

    def test_every_unit_in_the_file_names_a_basis(self):
        self.assertEqual(len(self.rows), 40)  # session 307: TNMP's rider DCRF counted once
        self.assertEqual(self.utilities, ["Oncor", "CenterPoint Energy Houston Electric", "AEP Texas", "Texas-New Mexico Power"])
        self.assertEqual([r["unit"] for r in self.rows if basis(r["unit"]) is None], [])
        self.assertEqual(sum(1 for r in self.rows if (r.get("applies") or "").lower().startswith("conditional")), 3)

    def test_the_transmission_component_is_the_figure_the_page_stated_before(self):
        # until session 236: "The transmission factor alone, a flat load: USD 8.58 per MWh" (Oncor), 8.16 (AEP Texas)
        for utility, factor, shown in (("Oncor", 6.260839, "8.58"), ("AEP Texas", 5.956038, "8.16")):
            got, _ = delivery(self.rows, utility, 100)
            self.assertEqual(got["transmission"], factor * 12000 / 8760)
            self.assertEqual(f"{got['transmission']:.2f}", shown)

    def test_the_components_by_hand(self):
        got, left = delivery(self.rows, "Oncor", 100)
        # distribution: metering 321.63 and customer 258.80 an account a month; the system charge 0.331004 and the
        # recovery factor 0.010072 per kW a month
        self.assertAlmostEqual(got["distribution"], (321.63 + 258.80) * 12 / 876000 + (0.331004 + 0.010072) * 12000 / 8760, places=12)
        self.assertAlmostEqual(got["other"], (-0.182495 + 0.005241) * 12000 / 8760, places=12)
        self.assertAlmostEqual(got["total"], got["transmission"] + got["distribution"] + got["other"], places=12)
        self.assertEqual((left, f"{got['total']:.2f}"), (0, "8.81"))
        # a per-kWh credit that applies only to municipal accounts is left out of CenterPoint's sums
        got, left = delivery(self.rows, "CenterPoint Energy Houston Electric", 100)
        self.assertEqual(left, 1)
        self.assertEqual(f"{got['total']:.2f}", "7.67")

    def test_the_library_gives_the_same_figures(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        script = ("import fs from 'node:fs'; const D = await import('./lib/datacenter/delivery.ts'); "
                  "const f = JSON.parse(fs.readFileSync('data/datacenter/texas_delivery.json', 'utf-8')); const out = {}; "
                  "for (const mw of [100, 250, 0.5]) for (const u of D.utilitiesOf(f.rows)) { const d = D.deliveryOf(f.rows, u, mw); "
                  "out[mw + '|' + u] = { total: d.total, parts: Object.fromEntries(d.components.map((c) => [c.kind, c.perMwh])), left: d.conditional, unread: d.unread, "
                  "stat: D.deliveryStat(f.rows, mw, D.slugOf(u) + ':total'), slug: D.slugOf(u) }; } console.log(JSON.stringify(out));")
        r = subprocess.run([exe, "--input-type=module", "-e", script], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=120, encoding="utf-8")
        if r.returncode != 0 and ("Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr):
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(len(got), 12)
        for mw in (100, 250, 0.5):
            for u in self.utilities:
                mine, left = delivery(self.rows, u, mw)
                theirs = got[f"{mw}|{u}"]
                for k in ("transmission", "distribution", "other"):
                    self.assertAlmostEqual(theirs["parts"][k], mine[k], places=9, msg=f"{u} {k} {mw}")
                self.assertAlmostEqual(theirs["total"], mine["total"], places=9)
                self.assertEqual((theirs["left"], theirs["unread"]), (left, 0))
                self.assertAlmostEqual(theirs["stat"], mine["total"], delta=0.005 + 1e-9)          # the figure shown: to the cent
                self.assertAlmostEqual(theirs["stat"] * 100, round(theirs["stat"] * 100), places=6)
        self.assertEqual([got[f"100|{u}"]["slug"] for u in self.utilities], ["oncor", "centerpoint_energy_houston_electric", "aep_texas", "texas_new_mexico_power"])

    def test_the_page_draws_components_and_the_download_holds_the_tariff_lines(self):
        page = src(*PAGE)
        table = page.split("function DeliveryTable", 1)[1].split("const matrixTip", 1)[0]
        self.assertIn('<Num check={`dcd|${mw}|${slugOf(u)}:${what}`} raw={v}>{shown(v)}</Num>', table)
        self.assertIn('head={["Component", ...parts.map((d) => d.utility)]}', table)
        # session 265 (the owner's list of 14 October 2026: no added assumption): the highlighted total is the lines with no
        # condition; session 236's total stands below it, labelled with its two conditions (a power factor of 1, one meter)
        self.assertIn('{ key: "held", highlight: true, cells: ["Total delivery, the lines with no condition", ', table)
        self.assertIn('{ key: "total", cells: [<Hover key="l" ', table)
        self.assertNotIn("function DeliveryCell", page)
        for gone in ("value_as_written", ".charge", ".sentence", ".document"):                 # no tariff line is drawn by the table
            self.assertNotIn(gone, table, gone)
        route = src("site", "app", "cost-of-power", "tables.csv", "route.ts")
        for col in ('"schedule"', '"component"', '"rate_as_filed"', '"usd_per_mwh_flat_load"', '"document"', '"line_read"'):
            self.assertIn(col, route, col)
        self.assertIn('const D = "delivery";', route)
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "dcd") {', check)
        self.assertIn('return D.deliveryStat(file.rows, Number(p[1]), p.slice(2).join("|"));', check)


class TwoSites(unittest.TestCase):
    def test_bs_site_is_an_address_parameter_the_server_reads(self):
        fin = src("site", "lib", "datacenter", "finance.ts")
        self.assertIn('export const SITE_B = "bsite";', fin)
        self.assertIn("if (isScenarioParam(k) || k === SITE_B) out.push(", fin)                 # carried with the scenarios' own
        pattern = re.search(r'export const isScenarioParam = \(name: string\) => name === "v" \|\| /(.+?)/\.test\(name\);', fin).group(1)
        self.assertIsNone(re.match(pattern, "bsite"))                                           # not one the browser rewrites
        model = src("site", "app", "cost-of-power", "model.ts")
        self.assertIn("export function siteBOf(raw: string | undefined, x: Pick<Inputs, \"grid\" | \"region\">)", model)
        self.assertIn("if (!g || !g.regions.some((r) => r.id === region) || (grid === x.grid && region === x.region)) return null;", model)
        self.assertIn("const bSite = !failed && side ? siteBOf(q[SITE_B], x) : null;", model)
        # B's ways are computed as A's are: the same functions on that site's own files
        self.assertIn('const foreB: Ruled = bSite && sideB && !failedB ? monthsRuled(filesB, bSite.region, x.buy, x, "forecast") : none;', model)
        self.assertIn('monthsRuled(filesB, bSite.region, x.buy, altFlex, "forecast").months', model)
        self.assertIn("ways: [setsB[0] ? wayOf(setsB[0]) : null, setsB[1] ? wayOf(setsB[1]) : null]", model)

    def test_the_block_reads_bs_site_and_as_figures_do_not(self):
        block = src("site", "app", "cost-of-power", "LoadScenarios.tsx")
        self.assertIn('const siteOf = (f: Facts, p: View) => (p === "b" && f.b ? f.b : f);', block)
        self.assertIn("const w = wayOf(s[p], siteOf(f, p).ways);", block)
        self.assertIn("head={f.b ? `For ${f.size}: A at ${f.place}; B at ${f.b.place}` : `For ${f.size} at ${f.place}`}", block)
        head = src("site", "app", "cost-of-power", "LoadHeadline.tsx")
        self.assertNotRegex(head, r"\bf\.b[^a-z]")                                              # the headline is scenario A's, at A's site
        form = src("site", "app", "cost-of-power", "LoadSiteB.tsx")
        self.assertTrue(form.startswith('"use client";'))
        self.assertIn('<option value="">The same site as A: {aPlace}</option>', form)
        self.assertIn('method="get" action="/cost-of-power"', form)

    def test_the_three_answers_add_bs_site_under_its_own_check_key(self):
        model = src("site", "app", "cost-of-power", "model.ts")
        self.assertIn("const answersKeyB = bSite ? `grid=${bSite.grid}&region=${encodeURIComponent(bSite.region)}&buy=${x.buy}&run=${x.run}&n=${x.n}&pct=${x.pct}&shift=${x.shift}&mw=${x.mw}` : \"\";", model)
        face = src("site", "app", "cost-of-power", "LoadAnswers.tsx")
        for name in ("power", "clean", "soon"):
            self.assertEqual(face.count(f'data-answer-b-site="{name}"'), 1, name)
        self.assertIn('<N pre={b.f.pre} stat="scarce:hours" a={b.a} />', face)


class TheNoteAndFiles(unittest.TestCase):
    def test_the_method_note_holds_the_sessions_sections(self):
        note = src("docs", "methods", "datacenter_pays_algorithm.md")
        for words in ("### 4.18 Delivery charges in Texas, by component (session 236)", "### 4.19 Scenario B at a site of its own (session 236)",
                      "**The ruling, and each grid's own signal (session 236).**", "rate x 12 x 1,000 / 8,760", "a kVA is counted as a kW (a power factor of 1)",
                      "**ERCOT: its reserve adder** (session 236, after the hand-back", "`dc|<address>|adders:hours`", "`notices:own:count`", "`dcd|<MW>|<utility>:<transmission, distribution, other or total>`"):
            self.assertIn(words, note, words)
        self.assertLess(note.index("### 4.17 How soon? (session 228)"), note.index("### 4.18 Delivery charges in Texas"))
        self.assertLess(note.index("### 4.19 Scenario B at a site of its own"), note.index("### 4.12 The source line"))

    def test_the_download_names_its_two_new_tables(self):
        route = src("site", "app", "cost-of-power", "tables.csv", "route.ts")
        self.assertIn('const B = "scenario_b_site", fb = M.facts.b;', route)
        check = src("site", "scripts", "check-datacenter-scenarios.mjs")
        self.assertIn('"regions", "delivery", "scenario_b_site", "matrix", "ny_load"].includes(t))', check)
        self.assertIn("// 12 (session 236): the brand;", check)

    def test_the_page_stays_in_review(self):
        rel = src("site", "lib", "release.ts")
        self.assertIn('"/cost-of-power": "review",', rel)

    def test_no_em_dash_in_what_this_session_wrote(self):
        for name in FACE + [("site", "app", "cost-of-power", "model.ts"), ("site", "app", "cost-of-power", "tables.csv", "route.ts"), ("site", "lib", "datacenter", "delivery.ts"),
                            ("site", "lib", "datacenter", "answers.ts"), ("site", "lib", "datacenter", "finance.ts"), ("site", "components", "echarts.ts"),
                            ("site", "scripts", "check-values.mjs"), ("site", "scripts", "check-datacenter-scenarios.mjs"), ("site", "scripts", "check-datacenter-face.mjs"),
                            ("docs", "methods", "datacenter_pays_algorithm.md"), ("tests", "test_session236.py"), ("tests", "test_session138.py")]:
            self.assertNotIn(DASH, src(*name), "/".join(name))


if __name__ == "__main__":
    unittest.main()
