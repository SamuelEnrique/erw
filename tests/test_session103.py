"""Session 103: known data faults.

The register and its table; the screening rule for impossible hours and the builders that call it; the general chat's
year grouping; and the reader question of session 95, settled: no builder reads a table with comment="#".
No network. The tests that read a table skip where the table is not on the machine.
"""
import csv
import glob
import json
import os
import re
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("warehouse/derived", "warehouse/connectors", "warehouse/supabase", "warehouse/chat", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, *p.split("/")))
import data_faults as df  # noqa: E402
import impossible_hours as ih  # noqa: E402
import iso_prices as ip  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def hours(values, start="2020-07-13T00:00:00Z"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="h"), dtype=float)


class TheRule(unittest.TestCase):
    def test_a_spike_a_zero_and_a_blank_are_not_used_and_a_ramp_is(self):
        d = hours([100, 104, 108, 180, 112, 116, 0, 120, np.nan, 128, 140, 154, 169, 180])
        s = ih.screen(d)
        self.assertTrue(np.isnan(s.iloc[3]))          # 180 between 108 and 112: more than a quarter from the four around it
        self.assertTrue(np.isnan(s.iloc[6]))          # zero
        self.assertTrue(np.isnan(s.iloc[8]))          # blank
        for i in (0, 1, 2, 4, 5, 7, 9, 10, 11, 12, 13):   # the rest, a ramp of a tenth an hour among them, are used as they are
            self.assertEqual(s.iloc[i], d.iloc[i], i)
        lo = ih.left_out(d)
        self.assertEqual(list(lo["reason"]), ["apart from the hours around it", "not above zero", "blank"])
        self.assertEqual(lo["value"].iloc[0], 180)

    def test_nothing_is_filled(self):
        d = hours([100, 100, 100, 300, 100, 100, 100])
        s = ih.screen(d)
        self.assertEqual(int(s.notna().sum()), 6)
        self.assertEqual(set(s.dropna()), {100.0})

    def test_a_good_hour_between_two_faulty_ones_is_left_out_with_them(self):
        # California's spring of 2019: 24,000 MW hours with 13,000 MW hours on both sides
        d = hours([24000, 24100, 13000, 24200, 13100, 24300, 24400])
        s = ih.screen(d)
        self.assertTrue(np.isnan(s.iloc[2]) and np.isnan(s.iloc[4]))
        self.assertTrue(np.isnan(s.iloc[3]), "the method note says this hour is lost with its neighbours")

    def test_it_is_the_rule_the_demand_table_had(self):
        import demand_growth as dg
        self.assertEqual(dg.JUMP, ih.JUMP)
        rng = np.random.default_rng(103)
        d = hours(list(20000 + 3000 * np.sin(np.arange(400) / 4) + rng.normal(0, 200, 400)))
        d.iloc[[50, 120, 121, 300]] = [60000, 0, np.nan, 900]
        v = d.where(d > 0)                                                   # session 97's own lines, kept here as the reference
        around = pd.concat([v.shift(k) for k in (-2, -1, 1, 2)], axis=1).median(axis=1)
        old = v.where(v.notna() & ~((v - around).abs() > 0.25 * around))
        pd.testing.assert_series_equal(dg.screened(d), old)
        pd.testing.assert_series_equal(ih.screen(d), old)

    def test_the_builders_that_read_hourly_demand_call_it(self):
        self.assertIn("return impossible_hours.screen(d, JUMP)", src("warehouse", "derived", "demand_growth.py"))
        self.assertIn('d["demand"] = impossible_hours.screen(d.set_index("ts")["demand"]).values', src("warehouse", "derived", "shoulder_hours.py"))
        self.assertIn('d["demand"] = impossible_hours.screen(d["demand"])', src("warehouse", "derived", "mix_profile.py"))
        note = src("docs", "methods", "impossible_hours.md")
        for t in ("cost_of_power_monthly", "ba_supply_monthly", "ai_power_regions"):   # read by a live page: stated as not applied
            self.assertIn(t, note)
            # session 118: the rule is now written into these builders and held there (impossible_hours.HELD): a held
            # builder writes what it wrote, so the table behind the live page is as it was
            self.assertIn(t, ih.HELD)
            self.assertFalse(ih.applies(t) and not os.environ.get("ERW_SCREEN_TRIAL"))


class TheRegister(unittest.TestCase):
    def setUp(self):
        self.faults = df.read_register()
        self.tables = set(pd.read_csv(df.COVERAGE, dtype=str, keep_default_na=False)["table"])
        self.sources = set(pd.read_csv(df.SOURCES, dtype=str, keep_default_na=False)["source"])

    def test_it_is_sound(self):
        self.assertEqual(df.check(self.faults, self.tables, self.sources), [])
        self.assertGreaterEqual(len(self.faults), 24)

    def test_the_faults_the_chain_named_are_there(self):
        ids = {f["id"] for f in self.faults}
        for want in ("eia930_ciso_generation_break", "eia930_ciso_hours_one_hour_late", "eia930_ciso_no_hydro", "eia930_pjm_impossible_demand_hours",
                     "eia930_nyiso_zero_demand_hours", "eia930_interchange_impossible_pair_days"):
            self.assertIn(want, ids)
        by = {f["id"]: f for f in self.faults}
        self.assertEqual((by["eia930_ciso_generation_break"]["first"], by["eia930_ciso_generation_break"]["last"]), ("2025-12-16", ""))
        self.assertEqual((by["eia930_ciso_hours_one_hour_late"]["first"], by["eia930_ciso_hours_one_hour_late"]["last"]), ("2023-11-01", "2025-12-02"))
        self.assertIn("2,159,056 MWh on 2026-07-21", " ".join(by["eia930_interchange_impossible_pair_days"]["evidence"].split()))
        self.assertIn("none in 2020", by["eia930_nyiso_zero_demand_hours"]["dates_note"])

    def test_the_check_catches_a_bad_entry(self):
        good = dict(self.faults[0])
        for change, word in (({"status": "fixed"}, "status"), ({"tables": "no_such_table"}, "not a table"), ({"first": "2026-13-01"}, "not a date"),
                             ({"source": "nobody:nothing"}, "source registry"), ({"evidence": ""}, "no evidence"), ({"first": "2026-01-02", "last": "2026-01-01"}, "after last")):
            bad = df.check([{**good, **change}], self.tables, self.sources)
            self.assertTrue(any(word in b for b in bad), (change, bad))
        self.assertTrue(any("used twice" in b for b in df.check([good, good], self.tables, self.sources)))

    def test_the_table_is_the_register_row_for_row(self):
        t = df.rows_of(self.faults, "2026-10-04T00:00:00Z", "2026-10-04")
        self.assertEqual(list(t.columns), df.EVENT_COLS + df.EXTRA)
        self.assertEqual(len(t), len(self.faults))
        self.assertTrue(t["event_id"].is_unique)
        r = t.set_index("event_id").loc["data_fault:eia930_ciso_hours_one_hour_late"]
        self.assertEqual((r["event_date"], r["x_first"], r["x_last"], r["status"], r["event_type"]), ("2023-11-01", "2023-11-01", "2025-12-02", "corrected", "data_fault"))
        self.assertIn("shoulder_hours_monthly", r["entity_ids"].split(";"))
        undated = t[t["x_first"] == ""]
        self.assertTrue((undated["event_date"] == "2026-10-04").all())       # the day the register recorded it
        self.assertTrue((undated["x_dates_note"] != "").all())
        self.assertFalse(t.astype(str).apply(lambda c: c.str.contains("\n")).any().any())   # one line a field

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, df.NAME + ".csv")), "known_data_faults is not on this machine")
    def test_the_table_on_disk_and_the_sites_copy_agree(self):
        path = os.path.join(OUT, df.NAME + ".csv")
        t = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
        site = json.loads(src("site", "data", "data_faults.json"))
        self.assertEqual(site["faults"], len(t))
        self.assertEqual({r["id"] for r in site["rows"]}, {e.split(":", 1)[1] for e in t["event_id"]})
        self.assertEqual(sum(site["by_status"].values()), len(t))
        by = t.set_index("event_id")
        for r in site["rows"]:
            row = by.loc["data_fault:" + r["id"]]
            self.assertEqual((r["evidence"], r["erw_does"], r["status"], ";".join(r["tables"])), (row["x_evidence"], row["x_erw_does"], row["status"], row["entity_ids"]))

    def test_the_page_reads_the_copy_and_is_in_review(self):
        page = src("site", "app", "data", "faults", "page.tsx")
        self.assertIn('import faultsJson from "@/data/data_faults.json"', page)
        for word in ("Evidence", "Tables it touches", "What the ERW does", "Still open", "Recorded in"):
            self.assertIn(word, page)
        self.assertRegex(src("site", "lib", "release.ts"), r'"/data/faults":\s*"review"')
        import load
        self.assertIn(df.NAME, load.LIVE["review_hold"])
        self.assertIn(df.SOURCE, load.LIVE["sources_hold"])
        self.assertEqual(load.live_rule(df.NAME), ("full", None))


class TheReaderQuestion(unittest.TestCase):
    """Session 95: pandas' comment="#" cuts a row short at a "#" in it (one inside a quoted field is spared). Settled in
    session 103."""

    def test_comment_hash_loses_columns_and_counting_the_header_does_not(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "t.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("# a provenance line\n# another, with a # in it\nentity_id,name,status,source_url\n")
                f.write('q:1,Plain Plant,active,https://example.org/a\nq:2,Muscatine Plant #1,planned,https://example.org/b\nq:3,"Hill AFB, Bldg #737",retired,https://example.org/c#part\n')
            cut = pd.read_csv(path, comment="#", dtype=str, keep_default_na=False)
            self.assertEqual(len(cut), 3)                                  # no row is lost: columns are, without a word
            self.assertEqual(list(cut["status"]), ["active", "", "retired"])   # a "#" inside quotes is spared; a bare one cuts the row
            self.assertEqual(cut["name"].iloc[1], "Muscatine Plant ")
            self.assertEqual(cut["source_url"].iloc[2], "https://example.org/c")   # and an address loses its fragment
            self.assertEqual(ip.header_rows(path), 2)
            whole = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
            self.assertEqual(list(whole["status"]), ["active", "planned", "retired"])
            self.assertEqual(whole["name"].iloc[2], "Hill AFB, Bldg #737")
            self.assertEqual(whole["source_url"].iloc[2], "https://example.org/c#part")

    def test_no_builder_reader_or_loader_reads_a_table_with_comment_hash(self):
        pattern = re.compile(r'read_csv\([^\n]*comment\s*=\s*["\']#["\']')
        found = []
        for folder in ("warehouse/derived", "warehouse/connectors", "warehouse/supabase", "warehouse/metadata", "warehouse/chat", "warehouse/redivis",
                       "warehouse/archive", "warehouse/news", "package/src/erw", "scripts"):
            for f in glob.glob(os.path.join(ROOT, *folder.split("/"), "*.py")):
                with open(f, encoding="utf-8") as fh:
                    for i, line in enumerate(fh, 1):
                        if pattern.search(line):
                            found.append(f"{os.path.relpath(f, ROOT)}:{i}")
        self.assertEqual(found, [], 'read a table with skiprows=ip.header_rows(path), never with comment="#"')

    def test_the_analyses_that_still_use_it_read_tables_without_a_hash(self):
        # warehouse/analysis holds one-off analyses, each of a past session, left as they were run. The tables they read
        # with comment="#" must hold no "#" in a data row; checked on the tables that are on this machine
        pattern = re.compile(r'read_csv\(([^\n]*?),\s*comment="#"')
        named = set()
        for f in glob.glob(os.path.join(ROOT, "warehouse", "analysis", "*.py")):
            for m in pattern.finditer(src(os.path.relpath(f, ROOT))):
                for t in re.findall(r'"([a-z0-9_]+)\.csv"|"([a-z0-9_]+)"\s*\+\s*"\.csv"', m.group(1)):
                    named.add(t[0] or t[1])
        self.assertTrue(named)
        checked = 0
        for t in sorted(named):
            path = os.path.join(OUT, t + ".csv")
            if not os.path.exists(path):
                continue
            n = ip.header_rows(path)
            with open(path, "rb") as fh:
                for i, line in enumerate(fh):
                    if i > n:
                        self.assertNotIn(b"#", line, f"{t} holds a # in a data row and warehouse/analysis reads it with comment=\"#\"")
            checked += 1
        if not checked:
            self.skipTest("none of those tables is on this machine")


class TheYearGrouping(unittest.TestCase):
    """Session 92 found it under Ask ERCOT and fixed it there: a monthly table grouped by year in a time zone lost each
    year's January. Session 103: the general chat groups a row of a day or longer by its own label too."""

    def test_both_chats_group_a_dated_row_by_its_own_label(self):
        py = src("warehouse", "chat", "tools.py")
        self.assertIn('keys = _group_keys(sel, shape, tcol, group_by, "UTC" if dated else tz)', py)
        ts = src("site", "lib", "chat", "tools.ts")
        self.assertIn('tzKey(r.t, dated ? "UTC" : tz, g)', ts)
        self.assertNotIn("dated && scope?.dated_groups", ts)

    @unittest.skipUnless(os.path.exists(os.path.join(OUT, "carbon_intensity_monthly.csv")), "carbon_intensity_monthly is not on this machine")
    def test_the_general_chat_keeps_each_january_in_its_year(self):
        import tools
        tools.set_scope(None)
        tools._frames.clear()
        q = dict(table="carbon_intensity_monthly", entity="eia930:ERCO", variable="intensity_generation", aggregation="count", group_by="year")
        chicago = {r["year"]: r["count"] for r in tools.query(**{**q, "tz": "America/Chicago"})["result"]}
        utc = {r["year"]: r["count"] for r in tools.query(**{**q, "tz": "UTC"})["result"]}
        self.assertEqual(chicago, utc)                  # before session 103 each year's January was counted in the year before
        total = tools.query(**{k: v for k, v in q.items() if k != "group_by"})["result"][0]["count"]
        self.assertEqual(sum(chicago.values()), total)


if __name__ == "__main__":
    unittest.main()
