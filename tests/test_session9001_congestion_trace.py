"""Session 9001, chain 601 part H: /congestion's table figures traced by check-values. Each figure of the two lists of
constraints and of the places' table renders through Num with a pf| key into site/data/conditions/congestion.json, so
site/scripts/check-values.mjs reads it again from the file on its own; the page is in check-values' list, and the
check's text rule writes the figure as the page does (USD/MWh to two decimals, a share to one with "%", sums whole).
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheCongestionPageIsTraced(unittest.TestCase):
    def test_every_table_figure_carries_a_page_file_key(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn('const PF = "conditions/congestion.json";', s)
        self.assertIn('<Num check={check} raw={v} source={src}>{fmt(v)}</Num>', s)
        for f in ["hours", "abs_mean", "abs_max", "cost", "lmp_mean", "congestion_mean", "congestion_share_pct",
                  "hours_congestion_up", "hours_congestion_down"]:
            self.assertIn(f'check={{at("{f}")}}', s, f)
        self.assertIn('pfKey(PF, ["constraints", op, "constraints", k, ...(year === ALL ? [] : ["by_year", year]), f]', s)
        self.assertIn('pfKey(PF, ["places", p.id.split(":")[0], { id: p.id }, "by_year", py, f])', s)

    def test_check_values_reads_the_page_and_writes_its_figures_as_the_page_does(self):
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('"/congestion", "/congestion?op=caiso&year=all",', cv)
        self.assertIn("const condOk = /^pf\\|conditions\\//.test(check)", cv)
        self.assertIn("const textOk = condOk ||", cv)
        page = src("site", "app", "congestion", "page.tsx")
        self.assertIn('const usd = (v: number) => `${v.toFixed(2)} USD/MWh`;', page)
        self.assertIn('const pct = (v: number) => `${v.toFixed(1)}%`;', page)
        self.assertIn('const whole = (v: number) => Math.round(v).toLocaleString("en-US");', page)


if __name__ == "__main__":
    unittest.main()
