"""Session 49: the weekly vacuum, upload --tables, /deals at a month's start, interchange and the grid network, a year
of hub prices, the 2018 baseline and the weather rows, the temperature-controlled event study, and the RRC pilot.

Energy Research Warehouse (ERW). No network, no model, no database. Checks on warehouse tables run where the tables
are on this machine and are skipped otherwise (warehouse/output is not in git).

    python -m unittest tests.test_session49 -v
"""

import gzip
import io
import json
import os
import re
import subprocess
import sys
import unittest
import zipfile

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for d in ("connectors", "derived", "supabase"):
    sys.path.insert(0, os.path.join(ROOT, "warehouse", d))
OUT = os.path.join(ROOT, "warehouse", "output")
import eia930_interchange as interchange  # noqa: E402
import event_study as es  # noqa: E402
import grid_network as gn  # noqa: E402
import hub_history as hh  # noqa: E402
import noaa_isd  # noqa: E402
import rrc_production as rrc  # noqa: E402


def read(name):
    p = os.path.join(OUT, name + ".csv")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        n = sum(1 for line in f if line.startswith("#"))
    return pd.read_csv(p, skiprows=n, dtype=str, keep_default_na=False)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Part0(unittest.TestCase):
    def test_weekly_vacuum_workflow(self):
        w = src(".github", "workflows", "weekly-vacuum.yml")
        self.assertIn("cron:", w)
        self.assertIn("workflow_dispatch", w)
        self.assertIn("python warehouse/supabase/vacuum.py", w)
        self.assertIn("SUPABASE_DB_URL", w)
        self.assertNotIn("--force", w)
        v = src("warehouse", "supabase", "vacuum.py")
        self.assertIn("VACUUM (FULL, ANALYZE)", v)
        self.assertIn("pg_database_size", v)

    def test_upload_takes_named_tables(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "redivis", "upload.py"), "--help"],
                             capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("--tables", out.stdout)
        self.assertIn("def merge_headers(", src("warehouse", "redivis", "upload.py"))

    def test_deals_shows_the_previous_month_when_this_one_has_none(self):
        p = src("site", "app", "deals", "page.tsx")
        self.assertRegex(p, r"empty \? prev : current")
        self.assertIn("the month before", p)


class Interchange(unittest.TestCase):
    def test_snapshot(self):
        p = os.path.join(ROOT, "site", "data", "grid_network.json")
        snap = json.load(open(p, encoding="utf-8"))
        self.assertEqual(len(snap["hours"]), gn.HOURS)
        ids = {n["id"] for n in snap["nodes"]}
        self.assertFalse(ids & gn.REGIONS, "EIA's regions and country totals are not nodes")
        self.assertTrue(set(gn.ISO) <= ids)
        for l in snap["links"]:
            self.assertLess(l["a"], l["b"], "each pair once, the code that sorts first as a")
            self.assertEqual(len(l["mw"]), gn.HOURS)
            self.assertIn(l["a"], ids)
            self.assertIn(l["b"], ids)
        for n in snap["nodes"]:
            self.assertTrue(all(np.isfinite([n["x"], n["y"], n["z"]])))
            self.assertEqual(n["demand_mw"] is not None, n["id"] in gn.ISO, n["id"])

    def test_layout_is_fixed_by_its_seed(self):
        codes = ["A", "B", "C", "D"]
        w = {("A", "B"): 1.0, ("B", "C"): 2.0, ("C", "D"): 1.0}
        a, b = gn.layout(codes, w, seed=42, steps=50), gn.layout(codes, w, seed=42, steps=50)
        self.assertEqual(json.dumps(a, sort_keys=True, default=str), json.dumps(b, sort_keys=True, default=str))

    def test_pair_rule_against_the_tables(self):
        links, inter = read("grid_network_links"), read("eia930_all_interchange")
        if links is None or inter is None:
            self.skipTest("tables not on this machine")
        inter["value"] = inter["value"].astype(float)
        by = inter.set_index(["entity", "ts_utc"])["value"]
        sample = links.sample(min(300, len(links)), random_state=1)
        for _, r in sample.iterrows():
            a, b = r["entity"].split(":")[1].split("-")
            self.assertLess(a, b)
            v = float(r["value"])
            if (f"eia930:{a}-{b}", r["ts_utc"]) in by.index:
                self.assertAlmostEqual(v, by[(f"eia930:{a}-{b}", r["ts_utc"])], places=6)
            else:
                self.assertAlmostEqual(v, -by[(f"eia930:{b}-{a}", r["ts_utc"])], places=6)

    def test_interchange_ceiling(self):
        t = read("eia930_all_interchange")
        if t is None:
            self.skipTest("table not on this machine")
        # Session 113: the ceiling was written as 150,000 rows for the table. That number is the ceiling of one pull
        # (session 42's prompt; eia930_interchange.CEILING, which counts the rows EIA reports before it pages), and
        # session 49's pull of 18 days fit it with 127,560 rows. Since then the daily run pulls the last 3 days and
        # merges them into the table's history, so the table grows by a UTC day each run (about 8,000 rows) and no
        # fixed number holds: it passed 150,000 with the daily run of 3 October 2026 (151,632 rows) and stood at
        # 159,144 after 4 October's (20 days, 341 pairs), with nothing wrong in it. What must hold is that a pull stays under its ceiling,
        # which the connector enforces, and that the table holds no more than its days explain: at most 350 pairs
        # of balancing authorities reporting 24 hours a day (EIA reported 341 on the fullest day held), so 8,400
        # rows for each UTC day held, and each pair's hour once.
        self.assertEqual(interchange.CEILING, 150_000)  # one pull, unchanged
        days = t["ts_utc"].str[:10]
        self.assertLessEqual(int(days.value_counts().max()), 8_400)
        self.assertLessEqual(len(t), 8_400 * days.nunique())
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())


class HubHistory(unittest.TestCase):
    def test_targets_are_the_approved_hubs(self):
        got = {iso: set(nodes) for iso, (_, nodes) in hh.TARGETS.items()}
        self.assertEqual(got, {"caiso": {"TH_SP15_GEN-APND", "TH_NP15_GEN-APND"}, "miso": {"INDIANA.HUB"}, "nyiso": {"N.Y.C."},
                               "isone": {".H.INTERNAL_HUB"}, "spp": {"SPPNORTH_HUB"}})
        self.assertEqual(hh.START, "2025-09-01")
        self.assertEqual(hh.CEILING, 1_500_000)

    def test_history_tables_stay_out_of_supabase(self):
        live = yaml.safe_load(open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8"))
        pats = []

        def walk(x):  # every table pattern in the file, a key or a value
            if isinstance(x, str):
                pats.append(x)
            elif isinstance(x, dict):
                for k, v in x.items():
                    walk(k)
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(live)
        regs = [re.compile(p) for p in pats if p.startswith("^")]
        self.assertTrue(any(r.search("cost_of_power_monthly") for r in regs), "the walk finds the live set's rules")
        for t in ("iso_hub_prices_history", "eia930_all_history", "noaa_isd_hourly", "eia930_all_interchange",
                  "grid_network_links", "rrc_lease_production_monthly"):
            self.assertFalse(any(r.search(t) for r in regs), f"{t} matches a live-set rule")

    def test_the_history_where_held(self):
        t = read("iso_hub_prices_history")
        if t is None:
            self.skipTest("table not on this machine")
        self.assertLessEqual(len(t), hh.CEILING)
        self.assertTrue(set(t["entity"]) <= hh.ENTITIES)
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())


class Weather(unittest.TestCase):
    def test_parse_drops_missing_and_suspect(self):
        text = ('"STATION","DATE","REPORT_TYPE","NAME","TMP","DEW"\n'
                '"72259003927","2021-02-15T06:53:00","FM-15","DFW","-0189,5","-0244,5"\n'
                '"72259003927","2021-02-15T07:53:00","FM-15","DFW","+9999,9","-0250,1"\n'
                '"72259003927","2021-02-15T08:53:00","FM-15","DFW","-0200,3","+9999,9"\n')
        obs, n, name = noaa_isd.parse(text, "DFW")
        self.assertEqual(n, 3)
        self.assertEqual(name, "DFW")
        t = obs[obs["variable"] == "temperature_f"]["value"].tolist()
        d = obs[obs["variable"] == "dew_point_f"]["value"].tolist()
        self.assertEqual(t, [round(-18.9 * 9 / 5 + 32, 2)])  # 9999 missing and quality 3 (erroneous) dropped
        self.assertEqual(d, [round(-24.4 * 9 / 5 + 32, 2), round(-25.0 * 9 / 5 + 32, 2)])

    def test_plan_puts_primary_stations_first(self):
        jobs = noaa_isd.plan()
        prim = [noaa_isd.STATIONS[c][3] for c, *_ in jobs]
        self.assertEqual(prim, sorted(prim, reverse=True))
        self.assertEqual(len(jobs), len({(c, s, e) for c, s, e, _ in jobs}))

    def test_weather_rows_where_held(self):
        t = read("event_window_daily")
        if t is None:
            self.skipTest("table not on this machine")
        w = t[t["entity"].str.startswith("noaa:")]
        self.assertGreater(len(w), 0)
        p = w.pivot_table(index=["entity", "event", "ts_utc"], columns="variable", values="value", aggfunc="first").astype(float)
        mid = (p["temp_max_f"] + p["temp_min_f"]) / 2
        self.assertTrue(np.allclose(p["hdd_65f"], np.maximum(0, 65 - mid), atol=1e-3))
        self.assertTrue(np.allclose(p["cdd_65f"], np.maximum(0, mid - 65), atol=1e-3))
        self.assertTrue((p["temp_min_f"] <= p["temp_mean_f"] + 1e-9).all() and (p["temp_mean_f"] <= p["temp_max_f"] + 1e-9).all())
        cov = t[(t["event"] == "covid_2020") & (t["entity"] == "eia930:PJM") & (t["variable"] == "demand_mwh")]
        self.assertTrue(cov["ts_utc"].str.startswith("2018-").any(), "COVID-19's 2018 baseline is restored")

    def test_noaa_ceiling(self):
        p = os.path.join(OUT, "noaa_isd_hourly.csv")
        if not os.path.exists(p):
            self.skipTest("table not on this machine")
        line = next(l for l in open(p, encoding="utf-8") if l.startswith("# Rows returned"))
        n = int(re.search(r"Rows returned: ([\d,]+)", line).group(1).replace(",", ""))
        self.assertLessEqual(n, noaa_isd.CEILING)


def temp_panel(seed=3, effect=10.0, beta=4.0):
    rng = np.random.default_rng(seed)
    dates, y, ev, Z = [], [], [], []
    for yr in (2019, 2020, 2021):
        for k in range(30):
            d = pd.Timestamp(yr, 7, 1 + k)
            hot = (yr == 2021) * 6.0
            cdd = 10 + 5 * rng.random() + hot
            dates.append(d.strftime("%Y-%m-%d"))
            ev.append(yr == 2021)
            Z.append([0.0, 0.0, cdd, cdd ** 2])  # hdd and its square are zero in July: dropped
            y.append(100 + 2 * d.dayofweek + beta * cdd + (effect if yr == 2021 else 0.0))
    return dates, np.array(y), ev, np.array(Z)


class TemperatureSpec(unittest.TestCase):
    def test_recovers_the_effect_net_of_temperature(self):
        dates, y, ev, Z = temp_panel()
        plain = es.estimate(dates, y, ev)["pooled"]["estimate"]
        temp = es.estimate(dates, y, ev, Z=Z)["pooled"]["estimate"]
        self.assertAlmostEqual(temp, 10.0, places=6)
        self.assertGreater(plain, 25.0, "without the weather terms the hotter event year's heat counts as effect")

    def test_dependent_columns_dropped(self):
        X = np.array([[1, 0, 2, 1], [1, 0, 2, 2], [1, 0, 2, 3]], dtype=float)
        Xk, names = es.drop_empty(X, ["a", "zero", "twice_a", "b"])
        self.assertEqual(names, ["a", "b"])

    def test_trend_row(self):
        dates, y, ev, _ = temp_panel(beta=0.0)
        r = es.estimate(dates, y, ev, trend=True)["pooled"]
        self.assertAlmostEqual(r["estimate"], 10.0, places=6)

    def test_table_where_held(self):
        t = read("event_study_estimates")
        if t is None:
            self.skipTest("table not on this machine")
        self.assertEqual(set(t["x_spec"]), {"dow_year_mean_v1", "dow_year_temp_v1", "dow_trend_v1"})
        pt = t[t["variable"].str.endswith("_effect_pooled_temp")]
        self.assertTrue((pt["x_spec"] == "dow_year_temp_v1").all() and len(pt) > 0)
        self.assertFalse(((t["entity"] == "eia930:US48") & (t["x_spec"] == "dow_year_temp_v1")).any(), "no station for the Lower 48")


class RRC(unittest.TestCase):
    def test_terms_make_it_internal(self):
        s = src("warehouse", "connectors", "rrc_production.py")
        self.assertIn('license="internal"', s)
        self.assertEqual(rrc.CEILING, 500_000)
        self.assertEqual(rrc.PERMIAN, {"08", "7C", "8A"})

    def test_county_lines_keeps_only_the_county(self):
        head = "OIL_GAS_CODE}DISTRICT_NO}LEASE_NO}COUNTY_NAME\n"
        body = ["O}10}1}MARTIN\n", "O}10}2}MIDLAND\n", "O}10}3}MARTIN\r\n", "O}10}4}NOT MARTIN X\n"]
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr(rrc.TABLE, head + "".join(body))
        logged = []
        h, kept, n = rrc.county_lines(zipfile.ZipFile(buf), "MARTIN", logged.append)
        self.assertEqual(h.decode(), head)
        self.assertEqual([k.decode().split("}")[2] for k in kept], ["1", "3"])
        self.assertEqual(n, 4)

    def test_products_by_lease_type(self):
        self.assertEqual([v for _, v, _ in rrc.PRODUCTS["O"]], ["oil_bbl", "casinghead_gas_mcf"])
        self.assertEqual([v for _, v, _ in rrc.PRODUCTS["G"]], ["gas_mcf", "condensate_bbl"])

    def test_table_where_held(self):
        t = read("rrc_lease_production_monthly")
        if t is None:
            self.skipTest("table not on this machine")
        self.assertLessEqual(len(t), rrc.CEILING)
        self.assertEqual(t["ts_utc"].str[:7].nunique(), 24)
        self.assertEqual(set(t["x_county"]), {"MARTIN"})
        self.assertFalse(t.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertTrue((t["x_wells"].astype(int) >= 1).all())
        lines = [l for l in open(os.path.join(OUT, "rrc_lease_production_monthly.csv"), encoding="utf-8") if l.startswith("#")]
        self.assertTrue(any(l.startswith("# License: internal") for l in lines))

    def test_the_real_lease_route_is_behind_the_token(self):
        p = src("site", "app", "severance", "lease", "real", "page.tsx")
        self.assertIn("INTERNAL_COSTS_TOKEN", p)
        self.assertIn("notFound()", p)
        self.assertIn("robots: { index: false", p)
        self.assertNotIn("supabase", p.split("export default")[0].lower().replace('import { attempt } from "@/lib/supabase";', ""))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "data", "rrc_lease_production_monthly.json")))


if __name__ == "__main__":
    unittest.main()
