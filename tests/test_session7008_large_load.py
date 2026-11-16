"""Session 7008 (chain 301, goal 2): the large-load waits brought current, their summary that names no request, and the
utilities' dated queue totals.

Energy Research Warehouse (ERW). On rows written here (MADE UP: no such requests or utilities): the summary counts each
label apart, gives the range of medians only over the measured requests and only where five or more are measured, in
months of 30.4375 days with the days beside, names no request and gives no megawatt, and carries each publisher's
verdict; the totals keep a figure as printed, dated by its own words where they print a full date, and leave out a
pointer, "not published", a "no figure published" and a held row; Bonneville's fixed address is asked on every pull,
and Alberta's months published between two pulls are taken. No network, no data lock.

    python -m unittest tests.test_session7008_large_load -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for part in ("connectors", "derived"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", part))
import large_load_research as LR  # noqa: E402
import large_load_wait_summary as S  # noqa: E402


def wait(i, label, lo, hi, pub="Bonneville Power Administration", interval="request to energized"):
    return dict(entity=pub, interval=interval, request_id=f"L{i}", request_name=f"Project {i}", mw="250",
                label=label, days_at_least=str(lo) if lo is not None else "", days_at_most=str(hi) if hi is not None else "",
                last_copy_date="2026-11-16")


class Summary(unittest.TestCase):
    def test_counts_medians_and_nothing_named(self):
        rows = [wait(i, "measured", 100 * i, 200 * i) for i in range(1, 6)] + [wait(9, "lower bound", 900, None),
                                                                           wait(10, "upper bound", None, 50)]
        s = S.summarize(rows, "2026-11-16T10:00:00Z")
        v = {r.variable: r for r in s.itertuples()}
        self.assertEqual((v["requests"].value, v["measured"].value, v["lower_bounds"].value, v["upper_bounds"].value),
                         ("7", "5", "1", "1"))
        self.assertEqual((v["median_at_least"].x_days, v["median_at_most"].x_days), (300.0, 600.0))
        self.assertEqual(v["median_at_least"].unit, "month")
        self.assertAlmostEqual(v["median_at_least"].value, round(300 / 30.4375, 2))
        self.assertEqual(v["requests"].x_license, "internal")
        text = s.to_csv(index=False)
        self.assertNotIn("Project 1", text)
        self.assertNotIn("L1", text)
        self.assertNotIn("250", text.replace("2026", ""))

    def test_fewer_than_five_measured_gives_no_median(self):
        s = S.summarize([wait(i, "measured", 10, 20) for i in range(4)], "2026-11-16T10:00:00Z")
        self.assertNotIn("median_at_least", set(s["variable"]))

    def test_every_publisher_has_a_verdict_with_its_words(self):
        for pub, (lic, geo, words) in S.VERDICTS.items():
            self.assertIn(lic, ("public", "internal"))
            self.assertTrue(words)


class Totals(unittest.TestCase):
    def rows(self):
        base = dict(group="g", state="TX", iso_region="ERCOT", source_title="t", date_read="2026-11-13", license_basis="b",
                    internal_fields="", license="public", source_url="https://example.gov/doc.pdf", queue_size_cite="p. 3")
        return pd.DataFrame([
            dict(base, row_id="a-01", utility="Alpha Electric", queue_size="795 requests in the queue at September 30, 2026"),
            dict(base, row_id="a-02", utility="Alpha Electric", queue_size="see row: Rate Schedule X"),
            dict(base, row_id="b-01", utility="Beta Power", queue_size="not published"),
            dict(base, row_id="c-01", utility="Gamma Co", queue_size="No single queue figure published. Gamma serves 88 buildings"),
            dict(base, row_id="d-01", utility="Delta Co", queue_size="about 22 GW of inquiries", license="internal"),
            dict(base, row_id="e-01", utility="Epsilon", queue_size="1.7 GW pipeline"),
        ])

    def test_figures_dates_and_holds(self):
        out, held = LR.totals_rows(self.rows())
        self.assertEqual(list(out["x_row_id"]), ["a-01", "e-01"])
        a = out.iloc[0]
        self.assertEqual((a["event_date"], a["x_date_kind"]), ("2026-09-30", "the figure's own date"))
        self.assertEqual(out.iloc[1]["x_date_kind"], "date read")
        self.assertEqual(len(held), 1)
        self.assertIn("d-01", held[0])

    def test_as_of(self):
        self.assertEqual(LR.as_of("adjustments to PJM (29 September 2026), signed"), "2026-09-29")
        self.assertEqual(LR.as_of("in 2026"), "")


class ThePulls(unittest.TestCase):
    def test_bonneville_is_asked_every_pull_and_alberta_takes_the_months_between(self):
        src = open(os.path.join(ROOT, "warehouse", "connectors", "large_load_waits.py"), encoding="utf-8").read()
        bpa = src[src.index('if on("bpa"):'):src.index('if on("aeso"):')]
        self.assertNotIn("not asked for again", bpa)
        self.assertIn("m > min(held_months)", src)


if __name__ == "__main__":
    unittest.main()
