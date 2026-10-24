"""Session 1402 (chain 100): the hub's price beside the hourly mix.

Energy Research Warehouse (ERW).

For ERCOT, CAISO and SPP, whose hub prices are public (site/lib/license.ts), the Mix tab draws the hub's real-time price
(iso_rtm_hub_prices, an hour the mean of its four 15-minute prices, held only when all four are) for the hours of the
energy mix panel's 7-day chart, in a strip under the chart (a `strip` series of site/components/TimeChart.tsx), the
price on hover beside each fuel's MW; the panel grid_hubprice_<grid> writes the strip's figures, keyed by three new
kinds (series_hn, series_hmean, series_hmax) that site/scripts/check-values.mjs recomputes with the page's own function
(site/lib/hubPriceHourly.ts hubHourStat). The held, paused and hubless grids say why in one line. The method is
docs/methods/generation_mix_hourly.md, section "The hub's price beside the hourly mix (chain 100, 24 October 2026)".

    python -m unittest tests.test_session1402 -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react", "marked"))
EM = chr(0x2014)
HEADING = "## The hub's price beside the hourly mix (chain 100, 24 October 2026)"
FILES = [("site", "lib", "hubPriceHourly.ts"), ("site", "components", "grid", "HubPricePanel.tsx"),
         ("site", "scripts", "test-hub-price.mjs"), ("site", "scripts", "fixtures", "hub_price.json"),
         ("tests", "test_session1402.py"), ("archive", "sessions", "SESSION_1402_REPORT.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "GRID_FILES_OUT", "ERW_SIZES")}


class TheHubPrice(unittest.TestCase):
    def test_the_three_hubs_and_the_rule(self):
        lib = src("site", "lib", "hubPriceHourly.ts")
        for w in ('export const RT_HUB_TABLE = "iso_rtm_hub_prices";', 'entity: "ercot:HB_HUBAVG", variable: "spp_rtm"',
                  'entity: "caiso:TH_SP15_GEN-APND", variable: "lmp_rtm_15m_mean"', 'entity: "spp:SPPNORTH_HUB", variable: "lmp_rtm_15m_mean"',
                  "if (m.size === 4) out.push", "docs/methods/cost_of_power.md"):
            self.assertIn(w, lib)
        self.assertFalse([l for l in lib.splitlines() if l.startswith("import ")])   # pure: no import, so check-values loads it as it is

    def test_the_mix_view_reads_and_draws_it(self):
        v = src("site", "components", "grid", "MixView.tsx")
        self.assertIn("Promise.all(bas.map(hubRead)),", v)
        self.assertIn("hub={chartW ? hubStrip(hp) : undefined}", v)
        self.assertIn("<HubPricePanel grid={grid} label={b.label} i={i} read={hubR} hp={hp} alone={!chartW} />", v)
        self.assertIn("since: daysAgo(9)", v)
        p = src("site", "components", "grid", "HubPricePanel.tsx")
        for w in ('data-grid-panel={`grid_hubprice_${grid}`}', 'words="could not be read"', "<PanelFile ", "href={METHOD_HUB_PRICE}",
                  '"no hub of its own"', '"paused"', "licenseHeldRow(RT_HUB_TABLE, hub.entity, now)"):
            self.assertIn(w, p)
        self.assertEqual(p.count("check="), 1)

    def test_the_chart_strip_is_off_by_default(self):
        t = src("site", "components", "TimeChart.tsx")
        # the signature session 303 pins is unchanged; the strip is a field of the series
        self.assertIn('export function TimeChart({ series, unit, ariaLabel, height = 260, stack = false, x = "minute", mini = false, unit2 = "", refLines, share = false, marks }: Props) {', t)
        self.assertIn("strip?: boolean;", t)
        self.assertIn("const main = useMemo(() => (strip ? series.filter((s) => s !== strip) : series), [series, strip]);", t)
        self.assertIn("const SH = strip ? 92 : 0;", t)
        self.assertIn('data-chart-card-strip="1"', t)
        self.assertIn("strip?: TimeSeries;", src("site", "components", "StackedArea.tsx"))
        self.assertIn("hub?: TimeSeries }) {", src("site", "components", "mix", "Now.tsx"))

    def test_the_keys_are_recomputed_and_named(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "series_hn" || p[0] === "series_hmean" || p[0] === "series_hmax") {', cv)
        self.assertIn('return P.hubHourStat(rows, p[0].slice("series_h".length), start, end);', cv)
        self.assertIn("series_hn: [1, 2], series_hmean: [1, 2], series_hmax: [1, 2],", src("site", "scripts", "check-methods.mjs"))
        a = src("site", "lib", "gridAnchors.ts")
        self.assertIn('export const HUB_PRICE_ANCHOR = "hub-price";', a)
        self.assertIn('export const METHOD_HUB_PRICE = "/data/methods/generation_mix_hourly#the-hubs-price-beside-the-hourly-mix-chain-100-24-october-2026";', a)

    def test_the_method_section_and_its_decisions(self):
        n = src("docs", "methods", "generation_mix_hourly.md")
        self.assertIn(HEADING, n)
        sec = n.split(HEADING)[1].split("\n## ")[0]
        for w in ("Decisions (chain 100, session 1402):", "A strip under the chart, not a second axis.", "series_hn|iso_rtm_hub_prices|",
                  "series_hmean|iso_rtm_hub_prices|", "series_hmax|iso_rtm_hub_prices|", "grid_hubprice_<grid>", "`HUB_PRICE_ANCHOR`",
                  "`METHOD_HUB_PRICE`", "cost_of_power.md", "SPP North Hub", "CAISO's price is drawn alone"):
            self.assertIn(w, sec)
        # the older sections and their link targets stand
        for h in ("## The Mix tab's energy mix, keyed, hourly and by month (chain 077, 23 October 2026)",
                  "### The energy mix panel in chain 091 (sessions 1181 to 1186)", "## The figures on the page and their keys"):
            self.assertIn(h, n)
        self.assertLess(n.index(HEADING), n.index("## The figures on the page and their keys"))

    def test_the_older_tests_are_extended(self):
        t = src("tests", "test_session473.py")
        self.assertIn('"components/grid/HubPricePanel.tsx": 1,', t)
        self.assertIn("grid_hubprice_ercot", src("site", "scripts", "test-grid-files.mjs"))
        f = src("site", "scripts", "test-grid-failed-reads.mjs")
        self.assertIn("grid_hubprice_ercot (1402), iso_rtm_hub_prices", f)
        self.assertIn("|ask|hubprice)_|", f)

    def test_no_em_dash(self):
        for parts in FILES + [("site", "components", "TimeChart.tsx"), ("docs", "methods", "generation_mix_hourly.md")]:
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), parts)

    @unittest.skipUnless(NODE and MODULES, "node and site/node_modules are needed")
    def test_the_node_test_passes(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-hub-price.mjs"],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", env=node_env(), timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("pass 10", r.stdout)


if __name__ == "__main__":
    unittest.main()
