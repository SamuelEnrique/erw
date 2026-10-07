"""Session 140: "What a datacenter pays", finished (/cost-of-power, in review). The builder's new parts on saved real
samples (the hourly carbon-free share laid out by the hour of the year in standard time, never filled; the Texas
delivery rule of the owner's ruling; the Commission's matrix as printed), the forecast rule's node tests on the saved
real prices of session 138 (the rule never uses a price from the hour it decides), and the page's rules read from its
source. No request and no model call."""
import json
import os
import re
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import datacenter_page as dp  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session140")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Prices(unittest.TestCase):
    def test_the_two_histories_are_read_and_a_load_zone_is_a_region_with_its_hub(self):
        self.assertEqual(dp.TABLES[:4], ["iso_hub_prices_history", "ercot_all_hub_prices_history", "ercot_zone_prices_history", "iso_zone_prices_history"])
        # ISO-NE's zone history is internal and is not in the list read: read first and set aside, it would take ISO-NE's
        # hours from the public six-week tables and lose them
        self.assertEqual(dp.HELD_INTERNAL, ["isone_zone_prices_history"])
        self.assertNotIn("isone_zone_prices_history", dp.TABLES)
        self.assertIn("tables=[t for t in TABLES if t not in internal]", src("warehouse", "derived", "datacenter_page.py"))
        self.assertEqual(len(dp.TABLES), len(set(dp.TABLES)))
        self.assertEqual(sorted(dp.ZONES["ercot"]), ["LZ_AEN", "LZ_CPS", "LZ_HOUSTON", "LZ_LCRA", "LZ_NORTH", "LZ_RAYBN", "LZ_SOUTH", "LZ_WEST"])
        self.assertEqual({z: v["ref"] for z, v in dp.ZONES["ercot"].items() if v["ref"] != "HB_HUBAVG"},
                         {"LZ_NORTH": "HB_NORTH", "LZ_HOUSTON": "HB_HOUSTON", "LZ_SOUTH": "HB_SOUTH", "LZ_WEST": "HB_WEST"})
        self.assertEqual(dp.GRIDS["ercot"]["main"], "LZ_NORTH")   # the owner's ruling: a Texas load prices at its load zone

    def test_the_site_files_hold_the_load_zones_each_with_a_hub_held_beside_it(self):
        index = json.loads(src("site", "data", "datacenter", "index.json"))
        regions = {r["id"]: r for r in index["grids"]["ercot"]["regions"]}
        zones = [r for r in regions.values() if r.get("kind") == "zone"]
        self.assertEqual(len(zones), 8)
        for z in zones:
            self.assertIn(z["ref"], regions)             # the hub beside it is a region of the same file
            self.assertEqual(regions[z["ref"]]["kind"], "hub")
            self.assertIn("da", z)                       # day-ahead is held for all eight
            self.assertEqual("rt" in z, z["id"] in ("LZ_HOUSTON", "LZ_NORTH", "LZ_SOUTH", "LZ_WEST"))   # real time for the four competitive zones (the ceiling)
            self.assertTrue(z["da"]["first"].startswith("2015-01-01"))
        self.assertEqual(index["grids"]["ercot"]["main"], "LZ_NORTH")
        self.assertIn("ercot_zone_prices_history", index["tables"])
        self.assertEqual(sorted(index["blank"]), ["miso", "pjm"])      # MISO paused, PJM licensed: named, no number
        f = json.loads(src("site", "data", "datacenter", "ercot_2025.json"))
        z, h = f["regions"]["LZ_NORTH"]["rt"], f["regions"]["HB_NORTH"]["rt"]
        self.assertEqual((z["s"], len(z["v"])), (0, 8760))
        self.assertNotEqual(z["v"][:200], h["v"][:200])   # the zone's own prices, not the hub's


class Clean(unittest.TestCase):
    def test_the_hourly_share_is_laid_out_by_the_hour_of_the_year_in_standard_time_and_never_filled(self):
        # a real cut of clean_energy_hourly: ERCOT, 48 hours from 2025-03-08T00:00Z, across the spring clock change
        said = []
        dp.read_clean.__dict__.pop("_clean", None)
        years = dp.read_clean(FIX_DIR_AS_TABLE(), "ercot", 6, {}, said.append)
        dp.read_clean.__dict__.pop("_clean", None)
        self.assertEqual(sorted(years), [2025])
        arr = years[2025]
        self.assertEqual(len(arr), 8760)
        held = np.nonzero(~np.isnan(arr))[0]
        # 2025-03-08T00:00Z is 18:00 on 7 March in Central standard time: day 66 of the year, hour 18
        self.assertEqual((held.min(), held.max(), len(held)), (65 * 24 + 18, 65 * 24 + 18 + 47, 48))
        raw = pd.read_csv(os.path.join(FIX, "clean_energy_hourly_ercot_sample.csv"))
        self.assertEqual(float(arr[held.min()]), round(float(raw["value"].iloc[0]), 1))   # as held, to one decimal
        self.assertTrue(np.isnan(arr[held.min() - 1]) and np.isnan(arr[held.max() + 1]))  # an hour not held stays empty
        self.assertTrue(0 <= np.nanmin(arr) and np.nanmax(arr) <= 100)
        self.assertEqual(dp.read_clean(FIX_DIR_AS_TABLE(), "ercot", 6, {dp.CLEAN_TABLE: "internal"}, said.append), {})   # a table that is not public is not written

    def test_the_site_files_carry_the_share_for_each_grid(self):
        index = json.loads(src("site", "data", "datacenter", "index.json"))
        for g, v in index["grids"].items():
            f = json.loads(src("site", "data", "datacenter", f"{g}_{max(y for y in v['years'] if y < 2026)}.json"))
            self.assertIn("clean", f, g)
            vals = [x for x in f["clean"]["v"] if x is not None]
            self.assertTrue(len(vals) > 8000 and min(vals) >= 0 and max(vals) <= 100, g)


def FIX_DIR_AS_TABLE():
    """The sample under the table's own name, in a folder of its own (read_clean reads <dir>/clean_energy_hourly.csv)."""
    d = os.path.join(ROOT, "runs", "session140", "test_clean")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(FIX, "clean_energy_hourly_ercot_sample.csv"), encoding="utf-8") as a, open(os.path.join(d, f"{dp.CLEAN_TABLE}.csv"), "w", encoding="utf-8", newline="") as b:
        b.write("# a real cut of clean_energy_hourly for tests/test_session140.py\n")
        b.write(a.read())
    return d


class Delivery(unittest.TestCase):
    def row(self, **over):
        r = {"event_id": "e1", "source": "oncor:retail_delivery_tariff", "rate_class": "Transmission Service", "schedule": "6.1.1.1.7 Transmission Service", "charge_name": "Distribution System Charge",
             "amount": "0.331004", "value_as_written": "$ 0.331004", "unit_as_written": "per Distribution System billing kW", "effective_date_as_written": "June 1, 2026",
             "document_title": "Tariff for Retail Delivery Service", "source_url": "https://example.org/tariff.pdf", "page": "80", "sentence": "Distribution System Charge $ 0.331004 per Distribution System billing kW",
             "figures_in_sentence": "1"}
        r.update(over)
        return r

    def review(self, **over):
        v = {"event_id": "e1", "kind": "distribution", "column_checked": True, "header_words": "", "applies_to_a_for_profit_datacenter": "yes", "why": "the tariff calls it a distribution system charge"}
        v.update(over)
        return v

    def test_a_row_is_shown_only_when_reviewed_with_its_unit_its_column_and_its_customer(self):
        d = pd.DataFrame([
            self.row(),
            self.row(event_id="e2", charge_name="Not reviewed"),
            self.row(event_id="e3", charge_name="No unit", unit_as_written=""),
            self.row(event_id="e4", charge_name="Many columns, not checked", figures_in_sentence="9"),
            self.row(event_id="e5", charge_name="Many columns, checked", figures_in_sentence="9"),
            self.row(event_id="e6", charge_name="A non-profit rate"),
            self.row(event_id="e7", source="someone:else"),
        ])
        review = [self.review(), self.review(event_id="e3"), self.review(event_id="e4", column_checked=False), self.review(event_id="e5", header_words="the 9th of 9 columns, Transmission Service", kind="transmission"),
                  self.review(event_id="e6", applies_to_a_for_profit_datacenter="no: the For Profit column prints 0.000000")]
        rows, left = dp.delivery_rows(d, review)
        self.assertEqual([r["charge"] for r in rows], ["Many columns, checked", "Distribution System Charge"])   # transmission before distribution
        self.assertEqual(left, {"not the transmission-voltage class, or not reviewed": 1, "no unit printed": 1, "column not checked": 1, "another customer's rate": 1})
        self.assertIn("checked against the printed header", rows[0]["column"])
        for r in rows:
            self.assertTrue(r["sentence"] and r["page"] and r["url"] and r["effective"] and r["document"])
            self.assertIn("public regulatory filing", r["terms"])
            self.assertEqual(r["value_as_written"], "$ 0.331004")   # as the tariff prints it

    def test_the_review_names_every_row_shown_and_nothing_is_computed_in_the_file(self):
        review = json.loads(src("warehouse", "derived", "texas_delivery_review.json"))["rows"]
        self.assertEqual(len(review), 45)
        self.assertEqual({r["kind"] for r in review}, {"transmission", "distribution", "other"})
        f = json.loads(src("site", "data", "datacenter", "texas_delivery.json"))
        self.assertEqual(len(f["rows"]), 41)
        for u in ("Oncor", "CenterPoint Energy Houston Electric", "AEP Texas", "Texas-New Mexico Power"):
            kinds = {r["kind"] for r in f["rows"] if r["utility"] == u}
            self.assertTrue({"transmission", "distribution"} <= kinds, u)   # transmission and distribution apart, for each utility
        self.assertNotIn("per_mwh", json.dumps(f))   # the per-MWh figure is computed on the page, in its own row, from the printed factor

    def test_the_commissions_matrix_is_as_printed_and_2026_is_not_called_approved(self):
        f = json.loads(src("site", "data", "datacenter", "texas_delivery.json"))
        m = f["matrix"]
        self.assertEqual(len(m), 45)   # three matrices (2025; 2026 A and B) by three statewide figures and three for each of four utilities
        rate = {(r["year"], r["matrix"]): r for r in m if r["quantity"] == "postage_stamp_rate"}
        self.assertEqual((rate[("2025", "")]["value"], rate[("2025", "")]["status"]), (68.547301, "approved"))
        self.assertEqual((rate[("2026", "A")]["value"], rate[("2026", "A")]["status"]), (75.52727, "filed"))
        for r in m:
            self.assertTrue(r["sentence"] and r["url"].startswith("https://interchange.puc.texas.gov/") and r["page"] and r["document"] and r["filed"], r["quantity"])
            self.assertIn(re.sub(r"[^0-9.]", "", r["value_as_written"]).rstrip("."), re.sub(r"[ ,]", "", r["sentence"]), r["quantity"])   # the figure stands in its line
            self.assertEqual(r["status"], "approved" if r["year"] == "2025" else "filed")
        self.assertEqual({r["scope"] for r in m}, {"ERCOT", "Oncor", "CenterPoint Energy Houston Electric", "AEP Texas", "Texas-New Mexico Power"})
        self.assertEqual(f["license"], "internal")


class Rule(unittest.TestCase):
    def test_the_forecast_rule_on_the_saved_real_samples(self):
        exe = "node"
        r = subprocess.run([exe, "scripts/test-datacenter-rule.mjs"], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        out = r.stdout
        self.assertNotIn("FAIL", out)
        self.assertGreaterEqual(out.count("\nok  "), 40)
        # the owner's test: the forecast rule never uses a price from the hour it decides
        for line in ("with every real-time price replaced by another number, no decision of 4 loads changes",
                     "the thresholds of that day and of every day before are unchanged",
                     "changing one hour's day-ahead price changes no decision of any day before it",
                     "the first 150 days' decisions are the same with every later price, day-ahead and real time, replaced by another number"):
            self.assertEqual(out.count(line), 2, line)   # in the calm year and in the year of Winter Storm Uri

    def test_the_rule_is_the_pages_figure_and_foresight_stands_beside_it(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn('monthsRuled(files, x.region, x.buy, x, "forecast")', page)
        self.assertIn('monthsRuled(files, x.region, x.buy, x, "hindsight")', page)
        self.assertIn('const FORESEEN = "if perfectly foreseen"', page)
        self.assertIn('data-stat="l12_saved_foreseen"', page)
        self.assertRegex(page, r'let ms: Month\[\] = fore\.months')   # the headline's months are the rule's
        lib = src("site", "lib", "datacenter.ts")
        body = lib.split("export function ruleWeights", 1)[1].split("\n}\n", 1)[0]
        self.assertNotRegex(body, r"pay\[y\]\[i\]\s*[<>]=?\s*[a-z0-9]")   # no price of the market paid in is compared with anything
        self.assertEqual(len(re.findall(r"pay\[y\]\[i\] !== null", body)), 2)   # of it the rule reads only whether the hour is held
        self.assertIn("export const PRIOR_DAYS = 30", lib)

    def test_the_rule_is_stated_on_hover_and_not_on_the_face(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        # the rule's words come from the library and are passed to a hover; the page's own text holds none of them
        self.assertIn("const rule = ruleWords(x)", page)
        self.assertIn("<Hover key=\"h\" why={rule}>", page)
        for words in ("prior 30 days", "dearest hourly day-ahead price", "upper bound", "with hindsight"):
            self.assertNotIn(words, re.sub(r'title=\{`[^`]*`\}|title="[^"]*"|const FORESEEN_WHY = "[^"]*"|//[^\n]*', "", page), words)


class Page(unittest.TestCase):
    def test_new_yorks_load_in_line_is_nyisos_own_list(self):
        q = json.loads(src("site", "data", "nyiso_load_queue.json"))
        in_line = [r for r in q["rows"] if r["in_line"]]
        self.assertEqual((len(in_line), q["total"]["requests"]), (53, 53))
        self.assertAlmostEqual(sum(r["mw"] for r in in_line), q["total"]["mw"], places=6)
        self.assertAlmostEqual(sum(z["mw"] for z in q["zones"]), q["total"]["mw"], places=6)
        self.assertFalse([r for r in in_line if re.search(r"withdrawn|in service", r["status"], re.I)])
        self.assertEqual(len(q["zones"]), 11)
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn('import nyLoadJson from "@/data/nyiso_load_queue.json"', page)
        self.assertIn("NYLOAD.rows.filter((r) => r.in_line)", page)
        self.assertNotIn("developer", page.lower())   # no request's developer is shown
        self.assertNotIn("developer", json.dumps(q["rows"]).lower())

    def test_the_loads_own_hours_against_clean_generation(self):
        page = src("site", "app", "cost-of-power", "page.tsx")
        self.assertIn("cleanShare(expandSeries(cFile.clean, cFile.hours), cP, cW)", page)
        self.assertIn('data-stat="own_clean"', page)
        self.assertNotIn("This load's own hours are not matched against them yet", page)

    def test_the_page_is_locked_and_the_three_live_pages_are_untouched(self):
        release = src("site", "lib", "release.ts")
        self.assertRegex(release, r'"/cost-of-power":\s*"review"')
        tracked = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "origin/main", "--", "site/app/cost-of-power/battery", "site/app/cost-of-power/Tabs.tsx", "site/app/network",
                                  "site/app/storage", "site/lib/batterystack.ts"], capture_output=True, text=True).stdout.split()
        self.assertEqual(tracked, [])   # nothing the three live pages are made of is changed by this session

    def test_the_refresh_and_the_holds(self):
        daily = src("warehouse", "run_daily.sh")
        self.assertIn('run_other nyiso_load_queue "$PYTHON" warehouse/connectors/nyiso_load_queue.py --pull --write', daily)
        self.assertIn("site/data/nyiso_load_queue.json", src(".github", "workflows", "daily-prices.yml"))
        hold = src("warehouse", "supabase", "live_set.yaml").split("catalogue_hold:", 1)[1]
        for t in ("ercot_zone_prices_history", "iso_zone_prices_history", "isone_zone_prices_history", "nyiso_load_queue", "texas_transmission_matrix"):
            self.assertIn(f"- {t}", hold)
        self.assertIn("- puct:transmission_charge_matrix", src("warehouse", "supabase", "live_set.yaml").split("sources_hold:", 1)[1])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in (("site", "app", "cost-of-power", "page.tsx"), ("site", "app", "cost-of-power", "LoadCharts.tsx"), ("site", "app", "cost-of-power", "LoadForm.tsx"),
                      ("site", "lib", "datacenter.ts"), ("site", "lib", "datacenterdata.ts"), ("site", "scripts", "test-datacenter-rule.mjs"), ("site", "scripts", "rule-gap.mjs"),
                      ("site", "scripts", "check-datacenter.mjs"), ("warehouse", "derived", "datacenter_page.py"), ("warehouse", "derived", "texas_delivery_review.json"),
                      ("docs", "methods", "datacenter_cost.md"), ("warehouse", "connectors", "ercot_zone_prices.py"), ("warehouse", "connectors", "zone_price_history.py"),
                      ("warehouse", "connectors", "nyiso_load_queue.py"), ("warehouse", "connectors", "texas_transmission_matrix.py"), ("site", "data", "nyiso_load_queue.json"),
                      ("site", "data", "datacenter", "texas_delivery.json")):
            self.assertNotIn(chr(0x2014), src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
