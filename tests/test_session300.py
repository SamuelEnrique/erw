"""Session 300: the home page (the owner's ruling of 18 October 2026, from mockup A; the chain prompt of 19 October).
What is held to:

  top to bottom: the one line; the "right now" strip (the latest wholesale price per grid with its hour, from
    latest_prices, and Henry Hub, WTI and Brent with their dates, each figure a link to /board and nothing else from
    the board); today's chart with its sentence; the five top-level groups (Economics, Grid, Infrastructure, Analysis,
    Games), each with one line and one live number; the latest Digest, its first five stories;
  every figure is a Num with its table (a key the value checker knows), and a figure the live set lacks is "no data";
  every read goes through `required`, so the page is never cached with a failed read (session 90's rule);
  the page takes the brand through the wrapper and the shared components only; it stays in review;
  the value checker computes the findings count from the library's catalogue; the floor of "/" stands;
  the review folder carries the before and after; no em dash in any file the session wrote.

No request, no model call; the environment is read, never set."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)
FILES = ["site/app/page.tsx", "site/scripts/check-values.mjs", "docs/brand/review-300/README.md", "tests/test_session300.py",
         "tests/test_session53.py", "tests/test_session90.py", "tests/test_session102.py", "tests/test_session241b.py"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def visible(text):
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


class TheOrder(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "page.tsx")

    def test_the_one_line_then_the_strip_the_chart_the_groups_the_digest(self):
        p = self.page
        self.assertIn('<ToolHeader crumb="Energy Research Warehouse" title="The live, citable record of the US energy system." />', p)
        order = ["<ToolHeader ", "<RightNow />", "<TodayChart />", "<Groups N={N} />", "<Digest />", "<SourceLine "]
        idx = [p.index(x) for x in order]
        self.assertEqual(idx, sorted(idx))

    def test_the_brand_and_the_shared_components_only(self):
        p = self.page
        self.assertIn('import { Brand } from "@/components/Brand";', p)
        self.assertEqual(len(re.findall(r"<Brand(?: noUsage)?>", p)), 1)
        self.assertIn("<ToolPage>", p)
        self.assertNotRegex(visible(p), r"#[0-9a-fA-F]{3,6}\b")          # no color of its own: the tokens only
        self.assertNotIn("font-family", visible(p))
        self.assertIn('"/": "review"', src("site", "lib", "release.ts"))

    def test_every_read_is_required(self):
        p = self.page
        self.assertNotRegex(p, r"\battempt\(")
        for reader in ("required(latestPrices)", "required(storageUnits)", 'required(() => newest("eia930_all_demand", "eia930:ERCO", "demand_mw"))',
                       "required(() => newest(f.table, e.entity, f.variable))", "required(() => rest<BS.Row>("):
            self.assertIn(reader, p)
        self.assertIn("export const revalidate = 900", p)


class TheStrip(unittest.TestCase):
    def test_each_figure_is_a_num_linking_the_board_and_nothing_else_of_the_board(self):
        p = src("site", "app", "page.tsx")
        fig = p[p.index("function Figure("):p.index("async function RightNow(")]
        self.assertIn('<Link href="/board" className="block bg-panel px-3 py-2 no-underline" gate="plain" data-home-figure={label}>', fig)
        strip = p[p.index("async function RightNow("):p.index("function TodayChart(")]
        self.assertIn("<Num check={`latest_prices|${p.entity}|${p.variable}|${p.ts_utc}`} raw={p.value}>{price(p.value)}</Num>", strip)
        self.assertIn("<Num check={`series|${f.table}|${e.entity}|${f.variable}|newest`} raw={r.data.value}>{price(r.data.value)}</Num>", strip)
        self.assertIn("real time, the interval from ${utc(p.ts_utc)}", strip)       # the hour
        self.assertIn("daily spot, ${day(r.data.ts_utc)}", strip)                   # the date
        self.assertIn("<NoData reason={latest.ok ? `latest_prices has no row for ${m.main}` : latest.reason} />", strip)
        self.assertNotIn("Sparkline", p)                                            # nothing else from the board
        self.assertNotIn("moves", strip.lower().replace("with its moves", ""))
        with open(os.path.join(SITE, "data", "markets.json"), encoding="utf-8") as f:
            m = json.load(f)
        self.assertEqual([e["entity"] for e in m["fuels"]["entities"]], ["eia:henry_hub", "eia:wti_cushing", "eia:brent"])


class TheGroupsAndTheChart(unittest.TestCase):
    def test_the_five_groups_each_with_a_line_and_one_live_number(self):
        p = src("site", "app", "page.tsx")
        self.assertIn('const HOME_GROUPS = ["Economics", "Grid", "Infrastructure", "Analysis", "Games"];', p)
        for g in ("Economics", "Grid", "Infrastructure", "Analysis", "Games"):
            self.assertTrue(re.search(rf'^  {g}: "[^"]{{40,}}",$', p, re.M), g)     # one line each, written for the page
        for key in ("{`bs|${BS.inputsKey(bx)}|l12_kw:total`}", '"series|eia930_all_demand|eia930:ERCO|demand_mw|newest"', '"storage|mw|operating"',
                    '"findings|count"', '"storage|iso_mw|ERCOT|operating"'):
            self.assertIn(f"<Num check={key}", p)
        self.assertIn('<NoData reason="the table was read and holds no row for this figure" />', p)
        self.assertIn("<Link href={g.pages[0].href}", p)     # the group's first page; the sub-tools are the menu's
        pages = src("site", "lib", "pages.ts")
        for g in ("Economics", "Grid", "Infrastructure", "Analysis", "Games"):
            self.assertIn(f'label: "{g}",', pages)

    def test_todays_chart_is_the_digests_chart_of_the_day_with_its_sentence(self):
        p = src("site", "app", "page.tsx")
        self.assertIn("const today = days.length ? (DOCS.digest_charts ?? {})[days[0]] : null;", p)
        self.assertIn('<p className="lead-fact" data-today-fact="1">{today.fact}</p>', p)
        self.assertIn("<img src={`/digest-charts/${today.image}`}", p)
        self.assertIn('data-today-chart="none"', p)

    def test_the_digest_is_five_stories(self):
        p = src("site", "app", "page.tsx")
        self.assertIn("const items = topItems(DOCS.latest, 5);", p)
        self.assertIn('<ol className="prose-erw list-decimal pl-5" data-home-stories={items.length}>', p)


class TheChecks(unittest.TestCase):
    def test_the_value_checker_counts_the_findings_from_the_catalogue(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "findings" && p[1] === "count") {', cv)
        self.assertIn('JSON.parse(fs.readFileSync(path.join(here, "..", "data", "findings", "catalogue.json"), "utf-8")).length', cv)
        with open(os.path.join(SITE, "scripts", "check-values-floor.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["floor"]["/"], 10)
        with open(os.path.join(SITE, "data", "findings", "catalogue.json"), encoding="utf-8") as f:
            self.assertGreater(len(json.load(f)), 0)

    def test_the_review_folder(self):
        folder = os.path.join(ROOT, "docs", "brand", "review-300")
        shots = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
        self.assertEqual(shots, ["after_home_1280.png", "after_home_390.png", "before_home_1280.png", "before_home_390.png"])

    def test_no_em_dash_in_any_file_the_session_wrote(self):
        for f in FILES:
            self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
