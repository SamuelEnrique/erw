"""Session 413: four competitors read against coverage (docs/reviews/competitors/2026-10-20.md).

The review is a document; these tests hold it to the session's rules: no em or en dash, the request log contiguous and
within the ceiling of 40, every marker cited defined in the sources table, every ERW table named in backticks a table
of coverage.csv (or a listed other name), and no recommendation words.
"""

import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOC = os.path.join(ROOT, "docs", "reviews", "competitors", "2026-10-20.md")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
CEILING = 40


# Names in backticks that are not ERW tables: Ask the Grid's dataset ids and MCP tools, column names, table-name
# prefixes and fragments, and the library and package names.
NOT_ERW_TABLES = {
    "_daily", "_monthly", "_planned_", "_retired_generators_all", "aeso_wind_forecast_7day", "bpa_outage_plans",
    "bpa_path_flows", "caiso_", "caiso_curtailment", "caiso_lmp_rtd_5m", "caiso_storage_live", "cenace_nodal_prices",
    "da_rt_spread_max_usd", "da_rt_spread_mean_usd", "describe_data", "eia860_operating_generators", "eia861_sales",
    "eia923_plant_fuel_monthly", "eia_ng_spot_prices_daily", "eia_wholesale_electricity_daily", "ercot_",
    "ercot_crr_auction_results", "ercot_lmp_by_bus", "ercot_sced_system_lambda", "erw", "fred_series",
    "get_asset_intelligence", "get_asset_profile", "get_congestion_path", "get_live_grid_status", "gridstatus",
    "hifld_substations", "hifld_transmission_lines", "hours_rt_over_da_50", "ieso_lmp_system", "isone_",
    "isone_fcm_mra", "miso_", "miso_rt_lmp_5min", "nifc_incidents", "noaa_hrrr_conus", "nrcs_snotel_daily", "nyiso_",
    "nyiso_outage_schedule", "osm_power_plants", "pjm_da_hrl_lmps", "pjm_rt_hrl_lmps", "pjm_transmission_outages",
    "pjm_very_short_load_frcst", "query_data", "query_grid_assets", "retrieved_at", "search_data", "source",
    "source_url", "spp_binding_constraints_rt_5m", "spp_lmp_by_bus", "spp_wind_forecast_short_term",
    "tva_reservoir_forecasts", "usgs_water_continuous",
}


def _doc():
    with open(DOC, encoding="utf-8") as f:
        return f.read()


def _section(text, start, end):
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def _coverage_tables():
    with open(COVERAGE, encoding="utf-8") as f:
        return {r["table"] for r in csv.DictReader(line for line in f if not line.startswith("#"))}


class TheReview(unittest.TestCase):
    def test_no_dashes(self):
        text = _doc()
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn(chr(0x2013), text)

    def test_request_log_contiguous_and_within_ceiling(self):
        log = _section(_doc(), "### 7.2 Every request", "### 7.3")
        numbers = [int(m) for m in re.findall(r"^\| (\d+) \| \d\d:\d\d:\d\d \|", log, flags=re.M)]
        self.assertTrue(numbers)
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))
        self.assertLessEqual(len(numbers), CEILING)
        self.assertIn(f"Requests in all: {len(numbers)} of a ceiling of {CEILING}.", log)

    def test_every_address_is_one_of_the_four(self):
        log = _section(_doc(), "### 7.2 Every request", "### 7.3")
        hosts = set(re.findall(r"`https://([^/`]+)/", log))
        allowed = {"askthegrid.com", "www.gridstatus.io", "docs.gridstatus.io", "www.yesenergy.com",
                   "www.enverus.com", "enverus.com"}
        self.assertTrue(hosts)
        self.assertLessEqual(hosts, allowed)

    def test_every_marker_is_defined(self):
        text = _doc()
        defined = set(re.findall(r"^\| ([AGYV]\d+) \|", _section(text, "### 7.1", "### 7.2"), flags=re.M))
        cited = set(re.findall(r"\[([AGYV]\d+)\]", text))
        self.assertTrue(cited)
        self.assertEqual(cited - defined, set())

    def test_no_robots_disallowed_path_requested(self):
        log = _section(_doc(), "### 7.2 Every request", "### 7.3")
        for path in ("/api/", "/account", "/login", "/signup", "/alerts", "/settings"):
            self.assertNotIn("askthegrid.com" + path, log)
        self.assertNotIn("?", "".join(re.findall(r"`https://askthegrid\.com[^`]*`", log)))

    def test_no_enverus_page_beyond_robots(self):
        log = _section(_doc(), "### 7.2 Every request", "### 7.3")
        for address in re.findall(r"`(https://(?:www\.)?enverus\.com[^`]*)`", log):
            self.assertTrue(address.endswith("/robots.txt"), address)

    def test_erw_tables_named_exist(self):
        text = _doc()
        tables = _coverage_tables()
        unknown = set(re.findall(r"`([a-z0-9_]+)`", text)) - tables - NOT_ERW_TABLES
        self.assertEqual(unknown, set(), "named in backticks but neither a coverage.csv table nor a listed other name")

    def test_no_recommendation(self):
        text = _doc().lower()
        for word in ("we recommend", "should cut", "should drop", "recommend cutting"):
            self.assertNotIn(word, text)


if __name__ == "__main__":
    unittest.main()
