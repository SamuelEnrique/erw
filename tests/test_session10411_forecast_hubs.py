"""Session 10411 (chain 720, part E): /forecast reads the contract's lines of session 10603 (27 November 2026).

The desktop's second window added, on its branch `wip/c730-predict-v4` (docs/state/page_files_predict.md, the dated
lines of session 10603): 35 more balancing authorities; four more hubs of the real-time price and, for every hub, the
backtest from 2016 scored by year (`long_backtest`); a file `price_hubs.json` with the day-ahead price forecast at those
hubs; and, in answer to this window's requests 11 and 12, `shown_for` in the wind and solar file, `tomorrow_held` where
a day is not forecast, and each file's own words for its cuts (`cuts`; `cuts_price` in the score file).

The page reads them before the files are on main: a file without a field is drawn as it was. The Node test draws each
from a fixture; `site/scripts/check-forecast-files.mjs` draws the real files, each other hub of a grid whole.

    python -m pytest tests/test_session10411_forecast_hubs.py
"""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_what_a_reader_sees(self):
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-forecast-lines.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of the forecast's lines of 27 November")


class TheEntryAPlaceIsShown(unittest.TestCase):
    """`shown_for`: the wind and solar entry a place shows is the one that names it (grid-caiso for ba-ciso)."""

    def test_the_join_reads_shown_for_and_falls_back_only_in_a_file_without_it(self):
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn("const lists = places.some((p) => Array.isArray(p.shown_for));", lib)
        self.assertIn("const pi = lists ? places.findIndex((p) => (p.shown_for ?? []).includes(place)) : places.findIndex((p) => p.place === (named ?? place));", lib)

    def test_a_place_with_no_net_demand_can_show_wind_and_solar(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        self.assertIn("const entry = ser ? windSolarFor(ws, slot.place.place, net?.wind_solar_place) : null;", lines)
        self.assertIn("if (!ser || (!net && !entry)) return part === \"chart\" ?", lines)
        # the old join, by the net demand's name alone, is gone from the views
        self.assertNotIn("windSolarOf(", lines)

    def test_net_demands_own_reason_comes_first(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        self.assertIn("net?.tomorrow_held ?? fuels.map((x) => x.f?.tomorrow_held).find(Boolean) ?? null;", lines)


class MoreHubs(unittest.TestCase):
    def test_one_block_draws_either_market_with_keys_into_its_own_file(self):
        rt = src("site", "app", "forecast", "realtime.tsx")
        self.assertIn('type Market = "rt" | "dah";', rt)
        self.assertIn('const key = (...rest: (string | number)[]) => pfKey(file, ["hubs", hi, ...rest]);', rt)
        self.assertIn('<PriceBlock market="dah" k="hub"', rt)
        self.assertIn('<PriceBlock market="rt" k="hub"', rt)
        # the day-ahead price is beside the real-time forecast only: the comparator, never an ERW method
        self.assertIn('rt: { what: "the real-time price", other: "day_ahead"', rt)
        self.assertIn('dah: { what: "the day-ahead price", other: null', rt)

    def test_a_hub_is_drawn_only_when_the_files_list_it_for_a_place_chosen(self):
        rt = src("site", "app", "forecast", "realtime.tsx")
        self.assertIn("const drawn = chosen && offered.includes(chosen) ? chosen : null;", rt)
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn("return [...new Set(ids.filter((id) => id !== own && gridOfHub(id) === grid))];", lib)
        predict = src("site", "lib", "predict.ts")
        self.assertIn("export const HUB_FORM = /^[a-z0-9-]{1,24}:[A-Za-z0-9_.-]{1,48}$/;", predict)
        self.assertIn('const hub = s === "price" && hubRaw && HUB_FORM.test(hubRaw) ? hubRaw : null;', predict)

    def test_the_section_is_its_own_component_and_the_pages_four_stand(self):
        view = src("site", "app", "forecast", "view.tsx")
        self.assertEqual(view.count("<ToolSection title="), 4)
        self.assertIn('{q.s === "price" ? <MoreHubsSection slots={slots} hubs={priceHubs} rt={rtPrice} scores={scores} metric={metric} asked={q.day} chosen={q.hub ?? null} hrefOf={(hub) => hrefOf(q, { hub }, "#hubs")} /> : null}', view)
        self.assertIn('<ToolSection title="More hubs" id="hubs">', src("site", "app", "forecast", "realtime.tsx"))
        self.assertLess(view.index("<RealTimeSection"), view.index("<MoreHubsSection"))
        self.assertLess(view.index("<MoreHubsSection"), view.index('<ToolSection title="Every place" id="places">'))

    def test_the_new_file_is_read_by_the_one_reader(self):
        files = src("site", "lib", "predictfiles.ts")
        self.assertIn('export const predictPriceHubs = () => readPredict<PriceHubsFile>("price_hubs.json");', files)
        self.assertNotIn("node:fs", src("site", "app", "forecast", "realtime.tsx"))


class TheHubsDownload(unittest.TestCase):
    """A hub's day-ahead forecast as a CSV with a Python and a Stata reader, as the page's other views have."""

    def test_the_route_takes_only_a_hub_the_file_lists(self):
        route = src("site", "app", "forecast", "hub-price", "route.ts")
        self.assertIn('const hub = file && file.example !== true ? file.hubs.find((h) => h.hub === u.searchParams.get("hub")) : undefined;', route)
        self.assertIn("if (!file || !hub) return new Response(", route)
        for kind in ("python", "stata"):
            text = src("site", "app", "forecast", "hub-price", kind, "route.ts")
            self.assertIn("const url = new URL(`/forecast/hub-price?hub=${encodeURIComponent(hub.hub)}`, req.url).toString();", text)
            self.assertNotIn("node:fs", text)

    def test_the_routes_are_in_the_sites_lists(self):
        listed = src("tests", "test_session5160.py")
        for sub in ("", "python/", "stata/"):
            self.assertIn(f'"app/forecast/hub-price/{sub}route.ts"', listed)
        self.assertIn('"/forecast/hub-price": ["./data/predict/price_hubs.json"], "/forecast/hub-price/*": ["./data/predict/price_hubs.json"] },', src("site", "next.config.ts"))

    def test_a_day_with_no_forecast_has_no_row_and_the_header_says_why(self):
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn("export function hubCsv(hub: PriceHub, file: PriceHubsFile, url: string): string {", lib)
        self.assertIn("...(hub.tomorrow_held ? [`# tomorrow: no row. ${hub.tomorrow_held}`] : []),", lib)


class TheBacktestByYear(unittest.TestCase):
    def test_each_year_and_the_whole_span_carry_their_keys(self):
        rt = src("site", "app", "forecast", "realtime.tsx")
        self.assertIn('key("long_backtest", "by_year", i, metric, m)', rt)
        self.assertIn('key("long_backtest", "all", metric, m)', rt)
        self.assertIn('key("long_backtest", "band_coverage_pct")', rt)


class ACutsWords(unittest.TestCase):
    """Request 12: for a price the ten days are those of the highest price hour; the score file's `cuts` names them by
    demand and is not quoted for a price."""

    def test_a_price_is_named_by_the_price(self):
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn('top10: "The ten days with the highest price hour"', lib)
        view = src("site", "app", "forecast", "view.tsx")
        self.assertIn('const cutWords = (cut: string) => (s === "price" ? PRICE_CUT_WORDS[cut] : undefined) ?? CUT_WORDS[cut] ?? cut;', view)
        self.assertIn('(s === "price" ? scores?.cuts_price?.[cut] ?? (cut === "top10" || cut === "spike" ? undefined : scores?.cuts?.[cut]) : scores?.cuts?.[cut])', view)

    def test_a_files_own_words_are_the_hover(self):
        rt = src("site", "app", "forecast", "realtime.tsx")
        self.assertIn("The file's words on this cut: ${cutWords[cut]}.", rt)
        self.assertIn("cuts={hubs.cuts ?? scores?.cuts_price ?? null}", rt)
        self.assertIn("cuts={rt.cuts ?? null}", rt)


class TheFileCheckDrawsEachHub(unittest.TestCase):
    def test_the_hubs_are_found_from_the_files_and_drawn_whole(self):
        text = src("site", "scripts", "check-forecast-files.mjs")
        self.assertIn('const html = renderToStaticMarkup(h(ForecastView, { query: { a: p.place, s: "price", m, hub } }));', text)
        self.assertIn("the hub is offered by the files and is not drawn", text)


class Words(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "app", "forecast", "realtime.tsx"), ("site", "app", "forecast", "lines.tsx"), ("site", "lib", "predictlines.ts"), ("site", "scripts", "check-forecast-files.mjs")):
            self.assertNotIn(EM, src(*parts), parts[-1])
        self.assertNotIn(EM, src("tests", "test_session10411_forecast_hubs.py").replace("chr(0x2014)", ""))


if __name__ == "__main__":
    unittest.main()
