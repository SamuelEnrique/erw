"""Session 10409 (chain 720, part E): /forecast draws what the forecast's page files gained on 27 November 2026.

The desktop's second window (chain 730, sessions 10602 and 10603) added to the contract (docs/state/page_files_predict.md,
the dated lines of 27 November): in each place file's demand series, the operator's filing checked by month
(`operator_filing`), a separate line with the weather forecast (`with_weather_forecast`) and net demand (`net_demand`);
in every shown series, the band's record (`band_coverage`); and the file `wind_solar.json`. The page gives each a view
(site/app/forecast/lines.tsx, placed by view.tsx; the shapes and pure functions in site/lib/predictlines.ts). The Node
test draws each from a fixture.

    python -m pytest tests/test_session10409_forecast_lines.py
"""
import os
import re
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


class TheSeparateLineIsNeverTheForecast(unittest.TestCase):
    """The contract: with_weather_forecast is a separate line, never the ERW forecast, and below 30 days the page says
    too few days to judge."""

    def test_the_line_is_in_no_chart(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        body = lines[lines.index("export function WeatherForecastLine"):lines.index("// ---- The band")]
        self.assertNotIn("CategoryChart", body)
        self.assertNotIn("ChartFrame", body)
        self.assertIn("(a separate line, not the {LABEL})", body)
        self.assertIn('{few ? ", too few days to judge" : ""}', body)

    def test_its_name_is_not_the_models(self):
        lib = src("site", "lib", "predictlines.ts")
        self.assertIn('export const WEATHER_FORECAST_LABEL = "With the weather forecast";', lib)
        self.assertIn('w.status === "too_few_days"', lib)


class TheFilingCheckSaysWhatTheContractAsks(unittest.TestCase):
    def test_flagged_months_are_said_not_to_be_the_operators_own(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        self.assertIn("In those months the filed forecast is not the operator&apos;s own forecast.", lines)
        self.assertIn('pfKey(file, [...path, "sound_last_2_years", metric, m])', lines)
        # the sentence and the two rows are drawn only where a month is flagged
        self.assertIn("{flagged !== null && flagged > 0 ? (", lines)


class EveryFigureCarriesItsKey(unittest.TestCase):
    def test_the_keys_name_the_files_own_paths(self):
        lines = src("site", "app", "forecast", "lines.tsx")
        for key in ('pfKey(file, ["series", "demand", "net_demand", "tomorrow", x.i, netCol])',
                    'pfKey(WS_FILE, ["places", entry?.pi ?? 0, "fuels", fuel, ...rest])',
                    'pfKey(file, ["series", s, "band_coverage", ...rest])',
                    'pfKey(file, [...path, "all", metric, m])'):
            self.assertIn(key, lines)

    def test_the_value_check_reads_the_new_megawatts_whole(self):
        text = src("site", "scripts", "check-values.mjs")
        rule = re.search(r"const predictLinesWhole = /(.+?)/\.test\(check\)", text).group(1).replace("\\/", "/")
        whole = ("pf|predict/region-tex.json|series/demand/net_demand/tomorrow/3/2",
                 "pf|predict/region-tex.json|series/demand/net_demand/last_2_years/mae_mw/erw",
                 "pf|predict/region-tex.json|series/demand/operator_filing/sound_last_2_years/mae/operator",
                 "pf|predict/region-tex.json|series/demand/with_weather_forecast/tomorrow/17/2",
                 "pf|predict/region-tex.json|series/demand/with_weather_forecast/all/mae/with_weather_forecast",
                 "pf|predict/wind_solar.json|places/12/fuels/wind/tomorrow/0/2",
                 "pf|predict/wind_solar.json|places/12/fuels/solar/summary/backtest/mae_mw/yesterday")
        for key in whole:
            self.assertRegex(key, rule)
        # a percent, a count of hours and a price keep the forms the check already knows
        for key in ("pf|predict/region-tex.json|series/demand/net_demand/last_2_years/nmae_pct/erw",
                    "pf|predict/region-tex.json|series/demand/net_demand/last_2_years/hours",
                    "pf|predict/region-tex.json|series/demand/operator_filing/sound_last_2_years/mape/erw",
                    "pf|predict/region-tex.json|series/demand/operator_filing/months/3/2",
                    "pf|predict/region-tex.json|series/demand/band_coverage/inside_pct",
                    "pf|predict/wind_solar.json|places/12/fuels/wind/band_coverage/inside_pct",
                    "pf|predict/region-tex.json|series/price/tomorrow/3/2"):
            self.assertNotRegex(key, rule)

    def test_the_rule_stands_on_a_line_of_its_own(self):
        text = src("site", "scripts", "check-values.mjs")
        self.assertIn("if (!pass && predictLinesWhole && t !== undefined && t !== null && same) pass = true;", text)


class TheViewsAreAdditions(unittest.TestCase):
    def test_the_page_places_each_view_and_moves_nothing(self):
        view = src("site", "app", "forecast", "view.tsx")
        for call in ("<NetDemand key={x.mark} slot={x} ws={windSolar} metric={metric} />", "<WindSolarDay key={x.mark} slot={x} ws={windSolar} asked={q.day} />",
                     "<FilingCheck key={x.mark} slot={x} scores={scores} metric={metric} />", "<WeatherForecastLine key={x.mark} slot={x} scores={scores} metric={metric} />",
                     "<BandCheck key={x.mark} slot={x} s={q.s} ws={windSolar} />"):
            self.assertIn(call, view)
        # what the page drew before stands in the order it had
        order = [view.index(s) for s in ('<ToolSection title="Tomorrow" id="tomorrow">', "<Tomorrow key={x.mark}", 'data-fc-ahead-block="1"', '<ToolSection title="How it has done" id="record">',
                                         "<PastDay key={x.mark}", "<ReportCard slots={slots}", '<ToolSection title="Every place" id="places">', '<ToolSection title="Downloads" id="downloads">')]
        self.assertEqual(order, sorted(order))

    def test_the_wind_and_solar_file_is_read_by_the_one_reader(self):
        files = src("site", "lib", "predictfiles.ts")
        self.assertIn('export const predictWindSolar = () => readPredict<WindSolarFile>("wind_solar.json");', files)
        self.assertNotIn("node:fs", src("site", "lib", "predictlines.ts"))
        self.assertNotIn("node:fs", src("site", "app", "forecast", "lines.tsx"))


class Words(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "app", "forecast", "lines.tsx"), ("site", "lib", "predictlines.ts"), ("site", "scripts", "test-forecast-lines.mjs")):
            self.assertNotIn(EM, src(*parts), parts[-1])
        self.assertNotIn(EM, src("tests", "test_session10409_forecast_lines.py").replace("chr(0x2014)", ""))

    def test_no_advice(self):
        lines = src("site", "app", "forecast", "lines.tsx").lower()
        for word in ("outperform", "should buy", "should sell", "so what"):
            self.assertNotIn(word, lines)


if __name__ == "__main__":
    unittest.main()
