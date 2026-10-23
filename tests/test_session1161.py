"""Session 1161: the Grid tool's steps of the trader path (docs/reviews/trader-path.md), walked on production for
chain 077's landing A and from the code for landing B (no build, no browser that evening).

Pins the new section's form (the three-page path's own form: Address, Does, Sees with check keys, the step's promise,
what a trader asks, the shots to take), its marks on the steps that wait for landing B's build, the walk's record of
production (docs/brand/review-1161/walk-1161-prod.json) against the figures the steps print, and that the three-page
path's sixteen steps are read as before. Read only: no build, no request.
"""

import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "trader-path.md")
REVIEW = os.path.join(ROOT, "docs", "brand", "review-1161")
HEAD = "## The Grid tool, `/grid` (session 1161, 23 October 2026)"
FOUND = "## What the Grid walk found"
FROM_CODE = "(from the code; to be walked on landing B's build)"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def section():
    doc = src("docs", "reviews", "trader-path.md")
    return doc.split(HEAD)[1].split("## The On.Energy walkthrough")[0]


def steps():
    s = section().split(FOUND)[0]
    return {m.group(1): b for m, b in zip(re.finditer(r"^### Grid step (\d\d): ", s, flags=re.M), re.split(r"^### Grid step \d\d: ", s, flags=re.M)[1:])}


class TheSection(unittest.TestCase):
    def test_the_section_stands_after_the_two_walks_and_before_on_energy(self):
        doc = src("docs", "reviews", "trader-path.md")
        self.assertEqual(doc.count(HEAD), 1)
        self.assertLess(doc.index("## Walked again on a build, 22 October 2026 (session 585)"), doc.index(HEAD))
        self.assertLess(doc.index(HEAD), doc.index(FOUND))
        self.assertLess(doc.index(FOUND), doc.index("## The On.Energy walkthrough"))
        self.assertNotIn(chr(0x2014), doc)

    def test_eleven_steps_17_to_27_in_the_files_form(self):
        st = steps()
        self.assertEqual(sorted(st), [f"{n}" for n in range(17, 28)])
        for n, b in st.items():
            self.assertRegex(b, r"- Address: `/grid", n)
            for w in ("- Does:", "- Sees", "- The step's promise:", "- A trader would ask:", "- Shots:"):
                self.assertIn(w, b, n)
            self.assertIn(f"docs/brand/review-1161/{n}-", b, n)
            self.assertIn("_1280.png", b, n)
            self.assertIn("_390.png", b, n)

    def test_the_three_page_paths_steps_are_still_its_own(self):
        doc = src("docs", "reviews", "trader-path.md")
        self.assertEqual(re.findall(r"^### Step (\d\d)", doc, flags=re.M), [f"{n:02d}" for n in range(1, 17)])

    def test_the_steps_of_landing_b_say_so_and_print_keys_not_values(self):
        st = steps()
        for n in ("19", "20", "21", "24"):
            self.assertIn(FROM_CODE, st[n].splitlines()[0], n)
        for n in ("19", "20", "22"):
            self.assertIn("The values for the build", st[n], n)
        for n in ("22", "25"):
            self.assertIn("from the code; to be walked on landing B's build", st[n], n)
        self.assertIn("series_sum|eia930_all_generation|net_generation_mw|2026-10-22T00:00:00Z|2026-10-23T00:00:00Z|eia930:ERCO", st["19"])
        self.assertIn("series_max|eia930_all_demand|demand_mw|2026-10-22T00:00:00Z|2026-10-23T00:00:00Z|eia930:ERCO", st["19"])
        self.assertIn("series_sum|scarcity_hours_by_grid|rt_hour_ge_1000|2026-09-01T06:00:00Z|2026-10-01T06:00:00Z|iso:ercot", st["20"])
        self.assertIn("awe|ndays|signal|2026-09-01|2026-09-30", st["22"])

    def test_the_findings_table_has_a_row_a_step_and_the_ruling_and_patch(self):
        f = section().split(FOUND)[1]
        for n in range(17, 28):
            self.assertIn(f"\n| {n} |", f)
        self.assertIn("the latest EIA has published", f)
        self.assertIn('view === "gravity" || view === "network"', f)
        self.assertIn("ercot_grid_notices", f)


class TheRecord(unittest.TestCase):
    """The production figures the steps print are those the walk read (walk-1161-prod.json)."""

    def setUp(self):
        with open(os.path.join(REVIEW, "walk-1161-prod.json"), encoding="utf-8") as fh:
            self.rec = {r["address"]: r for r in json.load(fh)["record"]}

    def fig(self, address, key):
        r = self.rec[address]
        for f in r["first"] + [x for p in r["panels"] for x in p["figures"]]:
            if f["key"] == key:
                return f["shown"]
        self.fail(f"{key} not on {address}")

    def test_every_address_answered_200_and_no_landing_b_panel_was_on_production(self):
        self.assertEqual(len(self.rec), 12)
        for a, r in self.rec.items():
            self.assertEqual(r["status"], 200, a)
            for p in r["panels"]:
                self.assertFalse(p["panel"].startswith(("grid_mix_", "grid_scarcity_", "grid_caisoalert_")), (a, p["panel"]))

    def test_the_printed_figures_are_the_records(self):
        st = steps()
        cases = [
            ("17", "/grid", "series|eia930_all_demand|eia930:US48|demand_mw|2026-10-22T23:00:00+00:00", "492,641"),
            ("18", "/grid?grid=ercot", "net|import|ERCO|2026-10-22T03:00:00Z", "350"),
            ("18", "/grid?grid=ercot", "net|lag|2026-10-22T03:00:00Z|2026-10-23T21:05:30Z", "42"),
            ("23", "/grid?grid=ercot&view=network", "net|tie|ERCO|SWPP|2026-10-22T03:00:00Z", "-352"),
            ("23", "/grid?grid=ercot&view=network", "netsnap|ERCO|demand_mw|2026-10-22T03:00:00Z", "53,405"),
            ("25", "/grid?grid=ercot&view=gravity&shape=gravity", "series|eia930_all_generation|eia930:US48|net_generation_mw|2026-10-22T03:00:00Z", "430,999"),
            ("26", "/grid?grid=ercot&view=clean", "series|carbon_intensity_hourly|eia930:ERCO|intensity_generation|2026-10-20T23:00:00+00:00", "342.29"),
        ]
        for n, address, key, shown in cases:
            self.assertEqual(self.fig(address, key), shown, key)
            self.assertIn(key, st[n], (n, key))
            self.assertIn(f"**{shown}**", st[n], (n, shown))

    def test_the_stored_answers_counts(self):
        ask = {a: next(p["text"] for p in r["panels"] if p["panel"].startswith("grid_ask_")) for a, r in self.rec.items()}
        self.assertIn("Five stored answers for ERCOT", ask["/grid?grid=ercot"])
        self.assertIn("Five stored answers for SPP", ask["/grid?grid=spp"])
        self.assertIn("Four stored answers for NYISO so far", ask["/grid?grid=nyiso"])
        self.assertIn("Three stored answers for the Lower 48 so far", ask["/grid"])

    def test_the_walk_keeps_no_token(self):
        for name in ("walk-1161.mjs", "walk-1161-prod.json"):
            t = src("docs", "brand", "review-1161", name)
            self.assertNotIn(chr(0x2014), t)
            self.assertNotRegex(t, r"erw_internal=|Set-Cookie:")
        self.assertIn('env("INTERNAL_COSTS_TOKEN")', src("docs", "brand", "review-1161", "walk-1161.mjs"))


if __name__ == "__main__":
    unittest.main()
