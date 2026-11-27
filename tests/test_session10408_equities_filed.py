"""Session 10408 (chain 720, part E): /equities on the SEC's company figures.

Since 27 November 2026 the equities page files hold 307 companies and what each filed with the SEC (the owner's ruling
of 26 November), with every share price still held ("license needed"). The page had been built while no company
existed. What the real files call for is pinned here: the chosen filed figure over every period a company filed, as
filed (nothing worked out from two filings); the newest period as one column for each length of period filed; the
energy price drawn as a chart of its own while no share price can carry it; the table's filter for filed figures; a
segment no SEC code fills. The Node test draws each from a fixture in the real files' shapes.

    python -m pytest tests/test_session10408_equities_filed.py
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
        r = subprocess.run([NODE, "--import", "./scripts/events-page-register.mjs", "scripts/test-equities-filed.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks of /equities on the filed figures")


class NothingIsWorkedOut(unittest.TestCase):
    """A point is a figure as filed. The library holds no subtraction of one filing from another."""

    def test_a_line_takes_only_rows_of_the_exact_length(self):
        lib = src("site", "lib", "equities.ts")
        self.assertIn('if (atEnd ? per === "12" && !/^10-K/.test(f.form ?? "") : f.months !== months) continue;', lib)
        self.assertIn("if (later(f, best.get(f.period_end)?.f)) best.set(f.period_end, { f, v });", lib)
        body = lib[lib.index("export function figureLine"):lib.index("export type NewestColumn")]
        self.assertNotIn(" - ", body)

    def test_the_choices_are_held_to_what_the_page_offers(self):
        lib = src("site", "lib", "equities.ts")
        self.assertIn('const fig = (FIGURES as readonly string[]).includes(figRaw ?? "") ? (figRaw as FigureKey) : FIGURE_DEFAULT;', lib)
        self.assertIn('const per = (PERIOD_KEYS as readonly string[]).includes(perRaw ?? "") ? (perRaw as PeriodKey) : PERIOD_DEFAULT;', lib)
        self.assertIn('export const PERIOD_KEYS = ["3", "12"] as const;', lib)

    def test_a_charted_figure_carries_its_key_into_the_file(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn('value={<span data-n={`eq|${k}|figure`}><Filed f={last.f} col={q.fig} slot={x.slot} colAt={x.at(q.fig)} /></span>}', view)
        self.assertIn('pfKey(fileOf(slot), ["quarterly", f.i, colAt])', view)


class AHeldPriceBesidePublicFilings(unittest.TestCase):
    def test_the_energy_price_is_drawn_alone_when_no_line_can_carry_it(self):
        view = src("site", "app", "equities", "view.tsx")
        self.assertIn("const priceAlone = alone || !slots.some((x) => isShown(x.series));", view)
        self.assertIn("<Prices prices={real} q={q} first={first} drawn={price} alone={priceAlone} />", view)

    def test_the_share_price_stays_a_blank(self):
        view = src("site", "app", "equities", "view.tsx")
        # the line's panel draws nothing of a series that is not shown: the blank and its reason
        self.assertIn("if (!s || !isShown(s)) {", view)
        self.assertIn('words={s ? blankWords(status, example) : "not held"}', view)

    def test_the_value_check_knows_a_filed_figure_in_millions(self):
        # window A's desk added the rule with the first real company files (session 10000): the figure above the
        # chart and the newest period's cells are keyed the same way, quarterly/<row>/<column 7 to 11>
        text = src("site", "scripts", "check-values.mjs")
        self.assertIn(r"const qm = /^pf\|equities\/series\/[^|]+\.json\|quarterly\/\d+\/(7|8|9|10|11)$/.exec(check);", text)


class TheFileCheckWalksTheNewChoices(unittest.TestCase):
    def test_each_line_is_computed_twice(self):
        text = src("site", "scripts", "check-equities-files.mjs")
        self.assertIn("the line differs from the file's rows read again", text)
        self.assertIn("the page draws ${n} periods, the file holds ${line.length}", text)


class Words(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "scripts", "test-equities-filed.mjs"), ("site", "app", "equities", "view.tsx"), ("site", "lib", "equities.ts"), ("site", "scripts", "check-equities-files.mjs")):
            self.assertNotIn(EM, src(*parts), parts[-1])
        self.assertNotIn(EM, src("tests", "test_session10408_equities_filed.py").replace("chr(0x2014)", ""))

    def test_no_advice(self):
        view = src("site", "app", "equities", "view.tsx").lower()
        for word in ("outperform", "underperform", "overweight", "undervalued"):
            self.assertNotIn(word, view)


if __name__ == "__main__":
    unittest.main()
