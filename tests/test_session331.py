"""Session 331 (the chain of 20 October 2026, night): /demand (its three views) and /curtailment finished to the five
tools' standard, lighter. The consumption view has its method note, the weather view its Reset, every view and the
curtailment page their tables to download (session 328's shared line), and the notes say what the pages draw today.
Energy Research Warehouse (ERW)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheDemandViews(unittest.TestCase):
    def test_each_view_offers_its_tables(self):
        page = src("site", "app", "demand", "page.tsx")
        self.assertIn('<TableDownloads tables={["eia_retail_sales_monthly", "eia_sector_energy_consumption_monthly"]} />', page)
        self.assertIn('<TableDownloads tables={view === "weather" ? ["eia930_demand_weather", "noaa_grid_weather_hourly", "noaa_grid_weather_stations"] : ["eia930_demand_growth"]} />', page)
        self.assertIn('const SALES = "eia_retail_sales_monthly";', src("site", "app", "consumption", "view.tsx"))
        self.assertIn('export const TABLE = "eia930_demand_growth";', src("site", "lib", "demandgrowth.ts"))
        self.assertIn('export const TABLE = "eia930_demand_weather";', src("site", "lib", "demandweather.ts"))

    def test_the_consumption_view_names_its_note(self):
        page = src("site", "app", "demand", "page.tsx")
        self.assertIn('<SiteLink href="/data/methods/consumption">Method, sources and gaps</SiteLink>', page)
        note = src("docs", "methods", "consumption.md")
        self.assertIn("at least 1,000,000 MWh (1 TWh)", note)
        self.assertIn("States that sold at least 1,000,000 MWh (1 TWh) to the sector in the earlier 12 months", src("site", "app", "consumption", "view.tsx"))

    def test_the_weather_panel_resets_to_the_defaults_choices_sets(self):
        w = src("site", "components", "demand", "Weather.tsx")
        self.assertIn('reset={{ href: "/demand?view=weather", defaults: `${FIGURES[0].name.toLowerCase()}, in ${lastWholeYear(file)}, the last whole year held.` }}', w)
        lib = src("site", "lib", "demandweather.ts")
        self.assertIn("const figure = FIGURES.find((x) => x.slug === q.figure) ?? FIGURES[0];", lib)
        self.assertIn("const year = q.year && ys.includes(q.year) ? q.year : lastWholeYear(f);", lib)


class TheCurtailmentPage(unittest.TestCase):
    def test_the_downloads_are_the_source_lines_tables(self):
        page = src("site", "app", "curtailment", "page.tsx")
        self.assertIn("  const srcTables: string[] = [...(g.daily ? [g.daily, MONTHLY] : [])", page)
        self.assertIn("<SourceLine tables={srcTables}", page)
        self.assertIn("<TableDownloads tables={srcTables} />", page)


class TheSharedChartLabels(unittest.TestCase):
    def test_bar_names_follow_the_unit_and_wrap_and_the_plot_starts_under_them(self):
        s = src("site", "components", "svgchart.tsx")
        self.assertIn("let bx = L + textWidth(unit) + 14, by = 11;", s)
        self.assertIn("if (bx + w > edge && bx > L + 4) { bx = L + 4; by += 14; }", s)
        self.assertIn("const TOP = small ? 6 : Math.max(24, (barNames.length ? barNames[barNames.length - 1].y : 0) + 13);", s)
        self.assertNotIn("x={L + 4 + j * (textWidth(s.name) + 14)} y={TOP - 6}", s)

    def test_the_heat_legend_is_measured_from_its_words(self):
        s = src("site", "components", "svgchart.tsx")
        # session 584: the same measure, its words through tw() (with a margin only where the legend takes two lines) and
        # the ramp's cells through `cell` (12 px, narrower only on its own line at a phone's width)
        self.assertIn("const x0 = L + span <= W - 4 ? L : 4, sx = x0 + tw(w0) + 8, hx = sx + 8 * cell + 6;", s)
        self.assertIn("const cell = split ? Math.max(6, Math.min(12, (W - 8 - tw(w0) - 8 - 6 - tw(w1)) / 8)) : 12;", s)
        self.assertNotIn("x={L + 110 + k * 12}", s)


class TheNotes(unittest.TestCase):
    def test_the_notes_say_what_the_pages_draw_today(self):
        self.assertIn("## Session 331 (20 October 2026): downloads and the third view's note", src("docs", "methods", "demand_growth.md"))
        self.assertIn("## Session 331 (20 October 2026): the Reset and the downloads", src("docs", "methods", "demand_weather.md"))
        self.assertIn("## The page as it stands (session 331, 20 October 2026)", src("docs", "methods", "curtailment.md"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "demand", "page.tsx"), ("site", "components", "demand", "Weather.tsx"), ("site", "app", "curtailment", "page.tsx"),
                      ("docs", "methods", "consumption.md"), ("docs", "methods", "demand_growth.md"), ("docs", "methods", "demand_weather.md"),
                      ("docs", "methods", "curtailment.md"), ("tests", "test_session331.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
