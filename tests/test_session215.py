"""Session 215: "license needed" on the remaining pages (the owner's ruling of 12 October 2026 on session 207's question 4).

From 20 October 2026 every page outside site/app/cost-of-power/ that reads one of the "license needed" tables shows the
catalogue's words, "license needed", in the place a number would have been. The hold reaches the pages in two ways:
lib/supabase.ts refuses a read of a held table (LicenseNeeded; attempt and required give its reason, and NoData draws
the words), and components/Num.tsx draws the words for a number whose check key names a held table. A table every
deciding publisher of which is a grid operator is held row by row, for that grid's rows, as the price board holds a grid
(session 207); any other held table is held whole. Before 20 October nothing a visitor sees changes.

These tests read the files as text (the site's TypeScript is not run here) and the status file's dates.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHelper(unittest.TestCase):
    def test_license_ts_offers_the_row_and_grid_rules(self):
        t = src("site", "lib", "license.ts")
        for name in ("licenseTitle", "licenseReason", "isLicenseReason", "licenseByGrid", "licenseHeldGrids", "gridOfEntity",
                     "licenseHeldRow", "licenseHeldGrid", "licenseGridTitle", "LICENSE_REASON", "LICENSE_TITLE_SUFFIX"):
            self.assertIn(f"export function {name}" if name[0].islower() and name not in ("licenseReason", "isLicenseReason") else name, t)
        # the words and the title are the catalogue's (app/data/page.tsx, session 207)
        self.assertIn('export const LICENSE_NEEDED = "license needed"', t)
        self.assertIn("the publisher's own page asks for permission; none is recorded yet", t)
        self.assertIn("the publisher's own page asks for permission; none is recorded yet", src("site", "app", "data", "page.tsx"))

    def test_the_grid_prefixes_are_the_python_sides_grids(self):
        t = src("site", "lib", "license.ts")
        for grid in ("ISO-NE", "MISO", "NYISO", "PJM", "SPP", "CAISO", "ERCOT"):
            self.assertIn(f'"{grid}"' if "-" in grid else f"{grid}:", t.replace(" ", ""))
        self.assertIn('GRIDS = {"CAISO", "ERCOT", "ISO-NE", "MISO", "NYISO", "PJM", "SPP"}', src("warehouse", "metadata", "license_status.py"))

    def test_the_status_file_switches_on_20_october(self):
        with open(os.path.join(ROOT, "site", "data", "license_status.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["from"], "2026-10-20")
        self.assertTrue(all(v["from"] == "2026-10-20" and v["status"] == "license needed" for v in d["tables"].values()))
        # the grid-decided tables and the whole-held ones both exist, so both rules are exercised
        grids = {"ISO-NE", "MISO", "NYISO", "PJM", "SPP", "CAISO", "ERCOT"}
        by_grid = [t for t, v in d["tables"].items() if set(v["publishers"]) <= grids]
        whole = [t for t, v in d["tables"].items() if not set(v["publishers"]) <= grids]
        self.assertIn("iso_dam_hub_prices", by_grid)
        self.assertIn("cost_of_power_monthly", by_grid)
        self.assertIn("energy_deals", whole)
        self.assertIn("datacenter_facilities", whole)


class TheReader(unittest.TestCase):
    def test_supabase_refuses_a_held_table_before_any_request(self):
        t = src("site", "lib", "supabase.ts")
        self.assertIn("export class LicenseNeeded extends DataError", t)
        self.assertIn('from "./license"', t)
        # the hold is decided before the first page is asked for, in the one reader every page uses
        body = t[t.index("export async function restPaged"):t.index("async function restPages")]
        self.assertIn("licenseHold(query)", body)
        self.assertIn("throw new LicenseNeeded(tableOf(query))", body)
        self.assertIn("licenseHeldRow(t, (r as { entity?: string }).entity", body)
        self.assertIn("if (licenseHold(query).throw) throw new LicenseNeeded(tableOf(query))", t)

    def test_required_does_not_fail_the_build_on_a_held_table(self):
        t = src("site", "lib", "supabase.ts")
        req = t[t.index("export async function required"):t.index("export async function rpc")]
        self.assertIn("if (e instanceof LicenseNeeded) return { ok: false, reason }", req)
        # and still throws on a failed read (session 90)
        self.assertIn("throw e instanceof DataError ? e : new DataError(reason)", req)

    def test_the_query_names_a_grid_by_entity_or_market(self):
        t = src("site", "lib", "supabase.ts")
        fn = t[t.index("function gridOfQuery"):t.index("function licenseHold")]
        self.assertIn('query.entity', fn)
        self.assertIn('query.market', fn)
        self.assertIn('e.startsWith("in.(")', fn)


class TheComponents(unittest.TestCase):
    def test_nodata_draws_the_words_for_a_license_reason(self):
        t = src("site", "components", "NoData.tsx")
        self.assertIn("isLicenseReason(reason)", t)
        self.assertIn("{LICENSE_NEEDED}", t)
        self.assertIn("data-license-held", t)
        # the ordinary block is as it was
        self.assertIn('<span className="font-semibold text-ink">no data</span>', t)

    def test_num_draws_the_words_and_drops_the_check_mark(self):
        t = src("site", "components", "Num.tsx")
        self.assertIn("export function heldBy(check: string)", t)
        self.assertIn('if (head === "latest_prices")', t)
        self.assertIn('if (head.startsWith("series")) table = p[1]', t)
        for k, v in (("deals", "energy_deals"), ("griddc", "datacenter_facilities"), ("bill", "cost_of_power_monthly"), ("es", "event_window_daily"), ("projects", "energy_projects")):
            self.assertIn(f'{k}: "{v}"', t)
        held = t[t.index("if (held) {"):t.index("return (\n    <span data-check")]
        self.assertIn("data-license-held={held.table}", held)
        self.assertNotIn("data-check", held)
        self.assertIn("{LICENSE_NEEDED}", held)

    def test_the_check_prefixes_num_knows_are_the_ones_the_pages_write(self):
        """Every check prefix a page outside cost-of-power writes for a held table is in Num's map or a series form."""
        # the keys of public tables need no map: storage (storage_capacity), awe (caiso_reliability_daily), the build-out's five
        known = {"deals", "event", "es", "griddc", "datacenters", "bill", "cop", "mr", "projects", "gridnews", "latest_prices", "catalogue", "storage",
                 "state_mw", "year_mw", "mw", "mwh", "iso_mw", "bs", "bsa", "awe",
                 # session 236: the datacenter page's answers (dc, session 228: the page's own price files and the public
                 # tables carbon_intensity_monthly, carbon_intensity_hourly, ercot_large_load_status and
                 # caiso_grid_emergencies) and its delivery charges (dcd: the site's own file of public tariff filings)
                 "dc", "dcd",
                 # session 235: the generator page's capture price and rate (cap: the site's own file data/seller/capture.json,
                 # recomputed by check-values from that file; whether the hubs of a grid whose price table is "license
                 # needed" from 20 October are held on this page too is listed for the owner's ruling in session 235's report)
                 "cap"}
        found = set()
        for dirpath, _, files in os.walk(os.path.join(ROOT, "site", "app")):
            if "_retired" in dirpath:
                continue
            for f in files:
                if f.endswith(".tsx"):
                    for m in re.finditer(r"check=\{?`([a-z_]+)\|", src(os.path.relpath(os.path.join(dirpath, f), ROOT))):
                        found.add(m.group(1))
        unknown = {p for p in found if not p.startswith("series") and p not in known}
        self.assertEqual(unknown, set(), f"check prefixes Num does not know: {sorted(unknown)}")


class ThePages(unittest.TestCase):
    def test_the_ask_tools_refuse_a_whole_held_table_by_name(self):
        t = src("site", "lib", "chat", "tools.ts")
        self.assertIn('from "@/lib/license"', t)
        self.assertIn("if (licenseNeeded(name) && !licenseByGrid(name)) throw new ToolError", t)

    def test_the_mix_and_curtailment_pages_hold_a_grid(self):
        v = src("site", "components", "mix", "views.tsx")
        self.assertIn('licenseHeldRow(CLEAN_TABLE, `iso:${g}`)', v)
        self.assertIn('const CLEAN_TABLE = "clean_energy_summary"', v)
        c = src("site", "app", "curtailment", "page.tsx")
        self.assertIn("licenseHeldGrid(c.grid)", c)
        self.assertIn("priceTableOf(c.grid)", c)

    def test_the_cost_of_power_pages_are_untouched(self):
        """The chain's rule: nothing under site/app/cost-of-power/ is edited (the old laptop rebuilds those pages)."""
        for dirpath, _, files in os.walk(os.path.join(ROOT, "site", "app", "cost-of-power")):
            for f in files:
                if f.endswith(".tsx"):
                    self.assertNotIn("session 215", src(os.path.relpath(os.path.join(dirpath, f), ROOT)))


if __name__ == "__main__":
    unittest.main()
