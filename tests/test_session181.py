"""Session 181: Automated Analysis, discovery. The scanner's five rules on small made-up series this test writes (one
case each that must flag and one that must not), the guards against known faults, the thresholds file read and
documented, a draft card's numbers equal to the flag's, the impact study's arithmetic and its Newey-West errors
against a case worked by hand, the refusals, the migration's text, the daily steps, the site's files. The worker and
the registration scripts are tested in tests/test_session181_worker.py. No request, no model call, nothing set at
import; the tests that need the warehouse's tables skip where they are absent."""
import csv
import datetime as dt
import importlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FINDINGS = os.path.join(ROOT, "warehouse", "analysis", "findings")
if FINDINGS not in sys.path:
    sys.path.insert(0, FINDINGS)
import findings_common as common  # noqa: E402
import findings_scanner as scanner  # noqa: E402
import impact_study  # noqa: E402
import run_finding  # noqa: E402

SCAN_DATE = "2026-10-10"
LAST = dt.date(2026, 10, 7)            # the newest settled day (two settle days before the scan)
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"]
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session181", "drafts.json")
OWN = [("warehouse", "analysis", "findings", "findings_scanner.py"), ("warehouse", "analysis", "findings", "impact_study.py"), ("warehouse", "config", "scanner.yaml"),
       ("warehouse", "supabase", "migrations", "029_scanner_drafts.sql"), ("warehouse", "supabase", "rollbacks", "029_scanner_drafts.sql"),
       ("docs", "methods", "automated_analysis_scanner.md"), ("docs", "methods", "automated_analysis_findings.md"), ("archive", "sessions", "SESSION_181_REPORT.md"),
       ("site", "app", "internal", "findings", "page.tsx"), ("site", "app", "internal", "findings", "state", "route.ts"), ("site", "app", "internal", "findings", "approved", "route.ts"),
       ("site", "components", "analysis", "DraftReview.tsx"), ("site", "components", "analysis", "ImpactForm.tsx"), ("site", "components", "analysis", "ScannerFound.tsx"),
       ("site", "components", "analysis", "FindingCard.tsx"), ("site", "lib", "scanner.ts"), ("site", "lib", "discoverychart.ts"), ("site", "app", "analysis", "page.tsx"),
       ("site", "components", "analysis", "RequestCard.tsx"), ("site", "components", "analysis", "RequestForm.tsx"), ("site", "app", "api", "analysis", "route.ts"),
       ("site", "scripts", "findings-stub.mjs"), ("site", "scripts", "check-internal-findings.mjs"), ("tests", "test_session181.py"),
       ("site", "data", "findings", "impact_study.json"), ("site", "public", "findings", "impact_study.do"), ("tests", "fixtures", "session181", "drafts.json")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def days_back(n, last=LAST):
    return [last - dt.timedelta(days=n - 1 - i) for i in range(n)]


def daily_rows(entity, variable, values, unit="MW", last=LAST, market="", source="test:source"):
    return [[entity, variable, f"{d.isoformat()}T00:00:00Z", repr(float(v)), unit, "P1D", "", market, "", source, "", "2026-10-09T00:00:00Z", ""]
            for d, v in zip(days_back(len(values), last), values)]


class World:
    """A made-up warehouse in a temporary folder: tables, coverage.csv, the pause list, the gaps and the faults."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="erw181_")
        self.out, self.meta = os.path.join(self.dir, "output"), os.path.join(self.dir, "metadata")
        os.makedirs(self.out)
        os.makedirs(self.meta)
        self.cov, self.gaps, self.faults = [], [], []
        self.paused = [("miso", r"(?i)^miso:|misoenergy\.org")]

    def table(self, name, rows, license="public", interval="P1D", tier="source"):
        with open(os.path.join(self.out, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# a made-up table for tests/test_session181.py\n")
            w = csv.writer(f, lineterminator="\n")
            w.writerow(COLS)
            w.writerows(rows)
        self.cov.append([name, license, interval, tier])

    def scan(self, **over):
        for name, head, rows in (("coverage.csv", ["table", "license", "interval", "tier"], self.cov), ("known_gaps.csv", ["table", "reason"], self.gaps),
                                 ("paused_sources.csv", ["scope", "match"], self.paused)):
            with open(os.path.join(self.meta, name), "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(head)
                w.writerows(rows)
        with open(os.path.join(self.out, "known_data_faults.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["event_id", "event_date", "entity_ids", "x_first", "x_last"])
            w.writerows(self.faults)
        cfg = scanner.load_config()
        cfg.update(over)
        return scanner.scan(self.out, cfg, SCAN_DATE, self.meta, log=lambda m: None)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def wave(n, base=100.0, amp=5.0, seed=1):
    r = np.random.RandomState(seed)
    return base + amp * np.sin(np.arange(n) / 9.0) + r.uniform(-1, 1, n)


def rules(flags, entity=None):
    return sorted(f["rule"] for f in flags if entity is None or f["series"]["entity"] == entity)


class TheFiveRules(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.close()

    def test_record_flags_a_record_that_had_stood_and_not_a_young_or_a_climbing_series(self):
        hi = wave(1300)
        hi[-1] = 150.0                                    # above every earlier day, which top out near 106
        lo = wave(1300, seed=2)
        lo[-1] = 40.0
        quiet = wave(1300, seed=3)                        # its newest day is inside its history
        young = wave(300, seed=4)
        young[-1] = 150.0                                 # a record, of a series too young to count
        climb = np.arange(1300) * 0.5 + wave(1300, amp=0.1, seed=5)   # a record every day: none had stood
        hair = wave(1300, seed=6)
        hair[-1] = hair[:-1].max() + 0.01                 # a record by a hair
        self.w.table("made_up_daily", daily_rows("t:high", "level", hi) + daily_rows("t:low", "level", lo) + daily_rows("t:quiet", "level", quiet)
                     + daily_rows("t:young", "level", young) + daily_rows("t:climb", "level", climb) + daily_rows("t:hair", "level", hair))
        flags, suppressed, drafts, summary = self.w.scan()
        rec = {f["series"]["entity"]: f for f in flags if f["rule"] == "record"}
        self.assertEqual(sorted(rec), ["t:high", "t:low"])
        f = rec["t:high"]
        self.assertEqual((f["date"], f["value"], f["direction"]), ("2026-10-07", 150.0, "high"))
        self.assertAlmostEqual(f["threshold"]["value"], float(hi[:-1].max()))
        self.assertEqual(f["compared"]["old_record"], f["threshold"]["value"])
        self.assertEqual(rec["t:low"]["direction"], "low")
        # reproducible: the table, the series key, the dates, the values, the threshold and the scanner's version
        for k in ("table", "series_key", "date", "value", "threshold", "history", "scanner_version", "scan_date", "window"):
            self.assertIn(k, f)
        self.assertEqual(f["scanner_version"], str(scanner.load_config()["version"]))
        self.assertEqual(f["threshold"]["config"]["record_min_points"], scanner.load_config()["record_min_points"]["daily"])
        self.assertEqual(summary["tables_scanned"], 1)

    def test_negative_flags_the_first_price_below_zero_in_a_year_and_not_a_hub_that_had_one(self):
        first = np.abs(wave(400, base=30, seed=1)) + 1
        first[-1] = -5.0
        again = np.abs(wave(400, base=30, seed=2)) + 1
        again[-100] = -3.0
        again[-1] = -5.0
        never = np.abs(wave(400, base=30, seed=3)) + 1
        not_price = wave(400, base=3, amp=4, seed=4)       # a spread crosses zero: not a price at a hub
        not_price[-1] = -5.0
        self.w.table("made_up_prices", daily_rows("hub:FIRST", "lmp_dam", first, "USD/MWh") + daily_rows("hub:AGAIN", "lmp_dam", again, "USD/MWh")
                     + daily_rows("hub:NEVER", "lmp_dam", never, "USD/MWh") + daily_rows("hub:FIRST", "da_rt_spread_mean", not_price, "USD/MWh"))
        flags = self.w.scan()[0]
        neg = [f for f in flags if f["rule"] == "negative"]
        self.assertEqual([(f["series"]["entity"], f["series"]["variable"], f["date"], f["value"]) for f in neg], [("hub:FIRST", "lmp_dam", "2026-10-07", -5.0)])
        self.assertEqual(neg[0]["compared"]["prior_days_held"], 365)
        self.assertIsNone(neg[0]["compared"]["last_negative_before"])

    def test_spike_flags_twice_the_99th_percentile_and_not_less(self):
        spike = np.abs(wave(900, base=30, seed=1))
        spike[-1] = 120.0
        mild = np.abs(wave(900, base=30, seed=2))
        mild[-1] = 50.0
        signed = wave(900, base=0, amp=30, seed=3)          # a signed quantity: a multiple of it says nothing
        signed[-1] = 200.0
        self.w.table("made_up_spikes", daily_rows("s:spike", "load", spike) + daily_rows("s:mild", "load", mild) + daily_rows("s:signed", "net", signed))
        flags = self.w.scan()[0]
        sp = [f for f in flags if f["rule"] == "spike"]
        self.assertEqual([f["series"]["entity"] for f in sp], ["s:spike"])
        cfg = scanner.load_config()
        prior = spike[:-8]                                  # the days before the fresh window (30 September on: eight days held)
        p99 = float(np.percentile(prior, cfg["spike_percentile"]))
        self.assertAlmostEqual(sp[0]["compared"]["percentile_value"], p99)
        self.assertAlmostEqual(sp[0]["threshold"]["value"], cfg["spike_multiple"] * p99)
        self.assertGreater(sp[0]["value"], sp[0]["threshold"]["value"])

    def test_weekly_flags_a_change_outside_its_range_and_not_one_inside(self):
        jump = wave(1500, base=100, amp=2, seed=1)
        jump[-7:] += 40.0
        flat = wave(1500, base=100, amp=2, seed=2)
        self.w.table("made_up_weeks", daily_rows("w:jump", "level", jump) + daily_rows("w:flat", "level", flat))
        flags = self.w.scan()[0]
        wk = [f for f in flags if f["rule"] == "weekly"]
        self.assertEqual([f["series"]["entity"] for f in wk], ["w:jump"])
        c = wk[0]["compared"]
        self.assertAlmostEqual(c["change"], float(jump[-7:].mean() - jump[-14:-7].mean()))
        self.assertGreater(c["change"], c["range_high"])
        self.assertEqual(wk[0]["window"], ["2026-09-24", "2026-10-07"])

    def test_pair_flags_two_series_that_parted_and_not_two_that_did_not(self):
        r = np.random.RandomState(7)
        x = 30 + 10 * np.sin(np.arange(420) / 11.0) + r.uniform(-1, 1, 420)
        parted = 2 * x + 5 + r.uniform(-1, 1, 420)
        parted[-7:] += 40.0
        together = 2 * x + 5 + r.uniform(-1, 1, 420)
        loose = r.uniform(0, 100, 420)                      # never moved with x: not tested at all
        loose[-7:] += 500.0
        rows = (daily_rows("ercot:HB_A", "da_mean", x, "USD/MWh") + daily_rows("ercot:HB_B", "da_mean", parted, "USD/MWh")
                + daily_rows("ercot:HB_C", "da_mean", together, "USD/MWh") + daily_rows("ercot:HB_D", "da_mean", loose, "USD/MWh"))
        self.w.table("ercot_hub_prices_daily", rows)
        flags = self.w.scan()[0]
        pr = [f for f in flags if f["rule"] == "pair"]
        got = {(f["series"]["entity"], f["compared"]["x_series_key"].split("|")[0]) for f in pr}
        self.assertIn(("ercot:HB_A", "entity=ercot:HB_B"), got)     # y is the first of the pair by its key
        self.assertNotIn(("ercot:HB_A", "entity=ercot:HB_C"), got)
        self.assertFalse(any("HB_D" in f["flag_key"] and f["compared"]["r2"] < scanner.load_config()["pair_min_r2"] for f in pr))
        f = next(f for f in pr if f["flag_key"].endswith("entity=ercot:HB_B|variable=da_mean|market=|node=|freq=P1D"))
        self.assertGreater(f["compared"]["sigmas"], scanner.load_config()["pair_break_sigmas"])
        self.assertGreaterEqual(f["compared"]["r2"], scanner.load_config()["pair_min_r2"])
        self.assertEqual(f["window"][1], "2026-10-07")


class TheGuards(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.close()

    def record(self, entity="t:high", last=LAST, n=1300, source="test:source", unit="MW"):
        v = wave(n)
        v[-1] = 150.0
        return daily_rows(entity, "level", v, unit=unit, last=last, source=source)

    def test_a_paused_publisher_is_never_flagged(self):
        self.w.table("made_up_daily", self.record("miso:ILLINOIS.HUB") + self.record("t:other", source="https://www.misoenergy.org/x") + self.record("t:high"))
        flags, _, _, summary = self.w.scan()
        self.assertEqual({f["series"]["entity"] for f in flags}, {"t:high"})
        self.assertEqual(summary["paused"], 2)
        self.assertIn("record", rules(flags))

    def test_a_known_fault_suppresses_the_flag_and_keeps_it_named(self):
        self.w.table("made_up_daily", self.record())
        other = wave(1300, seed=9)
        other[-1] = 160.0
        self.w.table("made_up_other", daily_rows("t:clean", "level", other))
        self.w.faults.append(["data_fault:made_up", "2026-10-01", "made_up_daily;another_table", "2026-10-01", ""])
        flags, suppressed, drafts, summary = self.w.scan()
        self.assertEqual({f["table"] for f in flags}, {"made_up_other"})
        self.assertEqual({(f["table"], f["suppressed_by"]) for f in suppressed}, {("made_up_daily", "data_fault:made_up")})
        self.assertNotIn("made_up_daily", {d["table_name"] for d in drafts})
        self.assertEqual(summary["flags_suppressed_by_known_faults"], len(suppressed))
        self.assertGreaterEqual(len(suppressed), 1)
        # a fault whose dates ended before the flag does not suppress it; one without dates covers the table whole
        self.assertIsNone(scanner.fault_for([("f", {"t"}, "2020-01-01", "2020-12-31")], "t", "2026-10-07", "2026-10-07"))
        self.assertEqual(scanner.fault_for([("f", {"t"}, None, None)], "t", "2026-10-07", "2026-10-07"), "f")

    def test_a_known_gap_an_internal_table_and_a_forecast_are_not_scanned(self):
        self.w.table("made_up_gap", self.record())
        self.w.gaps.append(["made_up_gap", "the runner cannot refresh it"])
        self.w.table("made_up_internal", self.record(), license="internal")
        self.w.table("made_up_forecast_hourly", self.record())
        self.w.table("made_up_snapshot", self.record(), interval="snapshot")
        flags, _, _, summary = self.w.scan()
        self.assertEqual(flags, [])
        not_scanned = {x["table"]: x["reason"] for x in summary["not_scanned"]}
        self.assertEqual(set(not_scanned), {"made_up_gap", "made_up_forecast_hourly", "made_up_snapshot"})   # the internal one is not a public table at all
        self.assertIn("known gap", not_scanned["made_up_gap"])

    def test_a_revised_or_partial_newest_day_is_not_evaluated(self):
        # yesterday's value is not settled (two settle days): the record on it is not raised
        self.w.table("made_up_daily", self.record("t:late", last=dt.date(2026, 10, 9)))
        # a sub-daily series whose newest day holds 3 of its 24 hours: the day is left out
        rows = []
        r = np.random.RandomState(3)
        for i, d in enumerate(days_back(1200)):
            hours = 24 if d != LAST else 3
            for h in range(hours):
                v = 9999.0 if d == LAST else 100 + 5 * math.sin(i / 9.0) + r.uniform(-1, 1)
                rows.append(["t:hourly", "level", f"{d.isoformat()}T{h:02d}:00:00Z", repr(v), "MW", "PT1H", "", "", "", "test:source", "", "", ""])
        self.w.table("made_up_hourly", rows, interval="PT1H")
        self.assertEqual(self.w.scan()[0], [])
        # the same record two days earlier is raised: the guard is the settle days, not the series
        self.w.table("made_up_daily", self.record("t:late", last=LAST))
        self.assertIn("record", rules(self.w.scan()[0]))

    def test_a_month_still_open_is_not_a_record_low(self):
        months = [dt.date(2001 + i // 12, i % 12 + 1, 1) for i in range((2026 - 2001) * 12 + 10)]    # January 2001 to October 2026
        v = wave(len(months), base=500, amp=30)
        v[-1] = 40.0                                         # October 2026 holds ten days: a partial month
        rows = [["m:x", "energy", f"{d.isoformat()}T00:00:00Z", repr(float(x)), "MWh", "P1M", "", "", "", "test:source", "", "", ""] for d, x in zip(months, v)]
        self.w.table("made_up_monthly", rows, interval="P1M")
        self.assertEqual(self.w.scan()[0], [])
        v[-2] = 40.0                                         # September 2026 is whole: that one is a record low
        rows = [["m:x", "energy", f"{d.isoformat()}T00:00:00Z", repr(float(x)), "MWh", "P1M", "", "", "", "test:source", "", "", ""] for d, x in zip(months, v)]
        self.w.table("made_up_monthly", rows, interval="P1M")
        flags = self.w.scan()[0]
        self.assertEqual([(f["rule"], f["date"], f["direction"]) for f in flags], [("record", "2026-09-01", "low")])

    def test_a_unit_change_is_not_scanned_and_a_source_change_cuts_the_history(self):
        v = wave(1300)
        v[-1] = 150.0
        rows = daily_rows("t:units", "level", v)
        for r in rows[:600]:
            r[4] = "kW"                                      # the unit changed on the way
        self.w.table("made_up_units", rows)
        rows = daily_rows("t:source", "level", v)
        for r in rows[:900]:
            r[9] = "test:old_report"                         # the source changed 400 days ago: 400 days are not enough for a record
        self.w.table("made_up_source", rows)
        flags, _, _, summary = self.w.scan()
        self.assertEqual([f for f in flags if f["rule"] == "record"], [])
        self.assertEqual((summary["unit_change"], summary["source_change"]), (1, 1))

    def test_a_derived_table_that_repeats_its_source_is_one_flag(self):
        self.w.table("made_up_source_table", self.record("a:x"), tier="source")
        self.w.table("made_up_derived_table", self.record("b:x"), tier="derived")
        flags, _, _, summary = self.w.scan()
        self.assertEqual({f["table"] for f in flags}, {"made_up_source_table"})
        self.assertEqual(summary["repeats_of_a_source_table"], len(flags))      # each flag of the source table had its repeat


class TheVolume(unittest.TestCase):
    def flag(self, i, rule="record", table="t", entity=None, strength=1.0):
        return {"id": f"scan-{rule}-{i:012x}", "flag_key": f"{rule}|{table}|e{i}", "rule": rule, "table": table, "series": {"entity": entity or f"e{i}"}, "strength": strength}

    def test_the_cap_takes_the_strongest_first_within_the_limits(self):
        cfg = scanner.load_config()
        flags = [self.flag(i, table=f"t{i}", strength=i) for i in range(40)]
        got = scanner.cap_drafts(flags, {**cfg, "max_drafts_per_rule": 99})
        self.assertEqual(len(got), cfg["max_drafts_per_day"])
        self.assertEqual([f["strength"] for f in got], sorted([f["strength"] for f in flags], reverse=True)[:cfg["max_drafts_per_day"]])
        self.assertEqual(len(scanner.cap_drafts([self.flag(i, strength=i) for i in range(40)], cfg)), cfg["max_drafts_per_table"])
        self.assertEqual(len(scanner.cap_drafts([self.flag(i, table=f"t{i}") for i in range(40)], cfg)), cfg["max_drafts_per_rule"])
        same_entity = [self.flag(i, table="t", entity="one", strength=i) for i in range(5)]
        self.assertEqual([f["strength"] for f in scanner.cap_drafts(same_entity, cfg)], [4])

    def test_an_open_draft_and_a_flag_raised_before_are_not_raised_again(self):
        drafts = [{"id": "scan-record-aaaaaaaaaaaa", "flag_key": "record|t|a"}, {"id": "scan-record-bbbbbbbbbbbb", "flag_key": "record|t|b"},
                  {"id": "scan-record-cccccccccccc", "flag_key": "record|t|c"}, {"id": "scan-record-dddddddddddd", "flag_key": "record|t|d"}]
        existing = [{"id": "scan-record-aaaaaaaaaaaa", "flag_key": "record|t|a", "state": "dismissed"},      # the same flag, dismissed: never again
                    {"id": "scan-record-000000000000", "flag_key": "record|t|b", "state": "draft"},          # an open draft of the same series
                    {"id": "scan-record-111111111111", "flag_key": "record|t|c", "state": "approved"}]       # ruled on: a new date may be raised
        self.assertEqual([d["id"] for d in scanner.new_rows(drafts, existing)], ["scan-record-cccccccccccc", "scan-record-dddddddddddd"])

    def test_a_dry_run_load_sends_nothing(self):
        lines = []
        with mock.patch.dict(sys.modules, {"requests": None}):          # an import of requests would fail: none is made
            n = scanner.load_drafts([{"id": "scan-record-aaaaaaaaaaaa", "rule": "record", "table_name": "t", "flag_date": "2026-10-07", "strength": 1.0}], dry_run=True, log=lines.append)
        self.assertEqual(n, 0)
        self.assertIn("nothing was sent", lines[-1])


class TheThresholdsFile(unittest.TestCase):
    def test_every_key_is_commented_read_and_in_the_method_note(self):
        text = src("warehouse", "config", "scanner.yaml")
        cfg = scanner.load_config()
        code = src("warehouse", "analysis", "findings", "findings_scanner.py")
        note = src("docs", "methods", "automated_analysis_scanner.md")
        lines = text.splitlines()
        for key in cfg:
            i = next(i for i, ln in enumerate(lines) if ln.startswith(key + ":"))
            j = i - 1
            while j >= 0 and lines[j].strip() and not lines[j].startswith("#") and not re.match(r"^[a-z_]+:", lines[j]):
                j -= 1                                       # a nested value of the key above
            self.assertTrue(any(ln.startswith("#") for ln in lines[max(0, i - 12):i]), f"{key}: no comment above it")
            self.assertTrue(f'"{key}"' in code or f"'{key}'" in code, f"{key}: in the thresholds file and never read by the scanner")
            self.assertIn(f"`{key}`", note, f"{key}: not explained in the Method note")
        for used in set(re.findall(r'cfg\[\"([a-z_]+)\"\]', code)) | set(re.findall(r'cfg\.get\(\"([a-z_]+)\"', code)):
            self.assertIn(used, cfg, f"{used}: read by the scanner and not in the thresholds file")
        self.assertEqual(text.count("\nversion:"), 1)
        # no threshold is a number written in the scanner's rules: the rules compare with cfg values only
        body = code[code.index("def rule_record"):code.index("SINGLE_RULES")]
        self.assertNotRegex(body, r"(spike_multiple|pair_break_sigmas|record_min_margin_sigmas)\s*=\s*\d")

    def test_the_tables_come_from_coverage_not_from_a_list(self):
        code = src("warehouse", "analysis", "findings", "findings_scanner.py")
        self.assertIn('read_meta_csv(os.path.join(meta_dir, "coverage.csv"))', code)
        self.assertIn('r.get("license") != "public"', code)
        self.assertNotIn("anthropic", code.lower())


@unittest.skipUnless(os.path.exists(FIXTURE), "the first run's drafts are not in the repository")
class TheDraftCards(unittest.TestCase):
    """The drafts of the first run (10 October 2026), as the loader would write them: each card's numbers are the flag's."""

    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf-8") as f:
            cls.drafts = json.load(f)

    def test_each_card_is_computed_from_its_flag(self):
        self.assertGreaterEqual(len(self.drafts), 3)
        for d in self.drafts:
            fl, card = d["flag"], d["card"]
            want = scanner.numbers_from_flag(fl)
            self.assertEqual(set(card["numbers"]), set(want), d["id"])
            for k, v in want.items():
                self.assertAlmostEqual(card["numbers"][k], v, places=5, msg=f"{d['id']}: {k}")
            self.assertEqual((card["card_id"], card["scanner"]["flag_id"], card["scanner"]["rule"], card["scanner"]["date"]), (d["id"], fl["id"], fl["rule"], fl["date"]))
            self.assertRegex(d["id"], r"^scan-[a-z]+-[0-9a-f]{12}$")
            for k in ("table", "series_key", "date", "value", "threshold", "scanner_version", "window", "history"):
                self.assertIn(k, fl, f"{d['id']}: the flag does not store {k}")

    def test_every_callout_number_is_a_number_of_the_flag(self):
        for d in self.drafts:
            fl = d["flag"]
            vals = [v for v in scanner.numbers_from_flag(fl).values() if isinstance(v, (int, float))] + [v for v in fl["threshold"]["config"].values() if isinstance(v, (int, float))]
            pool = set()
            for v in vals:
                pool |= {common.fmt(abs(float(v)), nd).replace(",", "") for nd in (0, 1, 2, 4)}
            for co in d["card"]["callouts"]:
                for side in ("before", "after"):
                    text = co[side]["text"]
                    if re.fullmatch(r"\d{4}-\d{2}-\d{2}|none held", text):
                        continue                             # a date of the flag
                    for x in re.findall(r"\d[\d,]*\.?\d*", text):
                        self.assertIn(x.replace(",", ""), pool, f"{d['id']}: callout number {x!r} in {text!r} is not a number of the flag")

    def test_a_draft_is_a_chart_callouts_and_a_footnote_and_no_paragraph(self):
        for d in self.drafts:
            c = d["card"]
            self.assertIs(c["draft"], True)
            self.assertEqual(c["why"], "")
            self.assertNotIn("downloads", c)
            self.assertIn(len(c["callouts"]), (2, 3))
            self.assertEqual(c["chart"]["kind"], "flag_line")
            self.assertGreater(len(c["chart"]["x"]), 10)
            self.assertEqual(len(c["chart"]["x"]), len(c["chart"]["series"][0]["values"]))
            if d["rule"] in ("record", "spike", "negative"):
                self.assertEqual(c["chart"]["mark"]["x"], d["flag_date"])
                self.assertAlmostEqual(c["chart"]["mark"]["value"], d["flag"]["value"], places=5)
                self.assertEqual(c["chart"]["x"][-1], d["flag_date"])
            foot = c["footnote"]
            for needle in (d["table_name"], d["flag"]["series_key"], "observations", "years", "Rule: " + d["rule"], "threshold crossed", "version " + d["scanner_version"], "not reviewed"):
                self.assertIn(needle, foot, d["id"])
            for k, v in d["flag"]["threshold"]["config"].items():
                self.assertIn(f"{k} = {v}", foot, d["id"])

    def test_the_first_run_kept_within_its_caps(self):
        cfg = scanner.load_config()
        self.assertLessEqual(len(self.drafts), cfg["max_drafts_per_day"])
        self.assertEqual([d["strength"] for d in self.drafts], sorted((d["strength"] for d in self.drafts), reverse=True))
        self.assertEqual(len({d["id"] for d in self.drafts}), len(self.drafts))
        self.assertEqual(len({(d["rule"], d["table_name"], d["flag"]["series"]["entity"]) for d in self.drafts}), len(self.drafts))

    def test_the_backtest_draft_is_the_scanners_own(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "session181", "draft_backtest_uri.json"), encoding="utf-8") as f:
            (d,) = json.load(f)
        self.assertEqual((d["rule"], d["flag"]["scan_date"], d["flag"]["series"]["entity"], d["flag"]["series"]["variable"]), ("pair", "2021-02-22", "ercot:HB_NORTH", "rt_mean"))
        self.assertEqual(d["card"]["numbers"], json.loads(json.dumps(scanner.numbers_from_flag(d["flag"]), default=common.round6)))
        self.assertEqual(d["card"]["scanner"]["full_card"], {"finding": "impact_study", "params": {"series": "ercot_north_rt", "control": "nyiso_nyc_rt", "event": "date", "year": 2021, "month": 2, "day": 20, "window": 14}})
        self.assertEqual(len(d["card"]["chart"]["series"]), 2)                 # the series and what the year's fit expects
        self.assertEqual(d["card"]["chart"]["mark_area"]["to"], "2021-02-20")

    def test_a_full_card_names_an_analysis_of_the_engine_or_nothing(self):
        for d in self.drafts:
            full = d["card"]["scanner"]["full_card"]
            self.assertTrue(full is None or (full["finding"] == "impact_study" and full["params"]["series"] in impact_study.SERIES and full["params"]["event"] == "date"))
        fl = {"table": "ercot_hub_prices_daily", "series": {"entity": "ercot:HB_NORTH", "variable": "rt_mean"}, "date": "2026-10-07"}
        self.assertEqual(scanner.full_card_for(fl), {"finding": "impact_study", "params": {"series": "ercot_north_rt", "control": "nyiso_nyc_rt", "event": "date", "year": 2026, "month": 10, "day": 7, "window": 14}})
        self.assertIsNone(scanner.full_card_for({"table": "eia_fuel_spot_prices", "series": {"entity": "eia:henry_hub", "variable": "spot_price"}, "date": "2026-10-07"}))   # no control in its unit
        self.assertIsNone(scanner.full_card_for({"table": "caiso_as_prices", "series": {"entity": "caiso:AS_CAISO_EXP", "variable": "as_price_dam_nr"}, "date": "2026-10-06"}))


class NeweyWestByHand(unittest.TestCase):
    """y = 1, 3, 2, 6 with after = 0, 0, 1, 1. By hand: a = 2, b = 2, residuals -1, 1, -2, 2; (X'X)^-1 = [[.5, -.5], [-.5, 1]];
    S0 = [[10, 8], [8, 8]]; with one lag (weight 1/2) the lag-1 sum G + G' = [[-14, -10], [-10, -8]], so S = [[3, 3], [3, 4]];
    V = (4 / 2) (X'X)^-1 S (X'X)^-1 = [[0.5, -1], [-1, 3.5]]. With no lag V = [[1, -1], [-1, 5]], which is HC1."""
    Y = [1.0, 3.0, 2.0, 6.0]
    X = [[1.0, 0.0], [1.0, 0.0], [1.0, 1.0], [1.0, 1.0]]

    def test_one_lag(self):
        beta, se, e = impact_study.newey_west(self.Y, self.X, 1)
        np.testing.assert_allclose(beta, [2.0, 2.0], atol=1e-12)
        np.testing.assert_allclose(e, [-1.0, 1.0, -2.0, 2.0], atol=1e-12)
        np.testing.assert_allclose(se, [math.sqrt(0.5), math.sqrt(3.5)], atol=1e-12)

    def test_no_lag_is_hc1(self):
        beta, se, _ = impact_study.newey_west(self.Y, self.X, 0)
        np.testing.assert_allclose(se, [1.0, math.sqrt(5.0)], atol=1e-12)
        hc1 = common.ols_hc1(self.Y, self.X, ["a", "b"])
        np.testing.assert_allclose(se, [hc1["coef"]["a"]["se"], hc1["coef"]["b"]["se"]], atol=1e-12)

    def test_against_the_sums_written_out(self):
        r = np.random.RandomState(11)
        n, L = 40, 3
        after = (np.arange(n) >= 20).astype(float)
        y = 5 + 3 * after + np.cumsum(r.normal(0, 1, n)) * 0.3
        X = np.column_stack([np.ones(n), after])
        beta, se, e = impact_study.newey_west(y, X, L)
        S = np.zeros((2, 2))
        for t in range(n):
            for s_ in range(n):
                lag = abs(t - s_)
                if lag <= L:
                    S += (1 - lag / (L + 1)) * e[t] * e[s_] * np.outer(X[t], X[s_])
        B = np.linalg.inv(X.T @ X)
        np.testing.assert_allclose(se, np.sqrt(np.diag(n / (n - 2) * B @ S @ B)), rtol=1e-10)

    def test_the_lag_rule(self):
        self.assertEqual([impact_study.newey_lags(n) for n in (10, 14, 28, 56, 100, 112)], [2, 2, 3, 3, 4, 4])
        self.assertEqual(impact_study.newey_lags(28), int(math.floor(4 * (28 / 100) ** (2 / 9))))


def made_up_daily(values_by_key):
    """impact_study.daily replaced: {series key: {day: value}} by the spec's words."""
    by_words = {impact_study.SERIES[k]["words"]: v for k, v in values_by_key.items()}
    return lambda spec, in_dir=None: dict(by_words[spec["words"]])


def series_days(first, n, f):
    d0 = dt.date.fromisoformat(first)
    return {(d0 + dt.timedelta(days=i)).isoformat(): float(f(i)) for i in range(n)}


class TheImpactStudy(unittest.TestCase):
    P = {"series": "ercot_north_rt", "control": "nyiso_nyc_rt", "event": "date", "year": 2024, "month": 5, "day": 15, "window": 14}

    def compute(self, y, c, **over):
        with mock.patch.object(impact_study, "daily", made_up_daily({"ercot_north_rt": y, "nyiso_nyc_rt": c, "henry_hub": c, "ercot_north_da": c})):
            p = {**self.P, **over}
            rows, meta = impact_study.compute(p)
            return rows, meta, impact_study.card(rows, p, meta)

    def test_the_arithmetic(self):
        # the series is 20 before 15 May 2024 and 50 after; the control is 30 and 35, each with a wobble that averages out
        wob = lambda i: (1 if i % 2 else -1)  # noqa: E731
        y = series_days("2024-03-01", 120, lambda i: (20 if i < 75 else 50) + wob(i))
        c = series_days("2024-03-01", 120, lambda i: (30 if i < 75 else 35) + 2 * wob(i))
        rows, meta, card = self.compute(y, c)
        n = card["numbers"]
        self.assertEqual((n["n_pre"], n["n_post"], n["reg_n"], n["reg_lags"]), (14, 14, 28, 3))
        self.assertAlmostEqual(n["series_pre"], 20.0)
        self.assertAlmostEqual(n["series_post"], 50.0)
        self.assertAlmostEqual(n["control_change"], 5.0)
        self.assertAlmostEqual(n["did"], 25.0)
        self.assertAlmostEqual(n["reg_did"], n["did"], places=9)       # the regression's b is the difference in differences
        self.assertAlmostEqual(n["reg_const"], n["series_pre"] - n["control_pre"], places=9)
        win = [r for r in rows if r["in_window"]]
        beta, se, _ = impact_study.newey_west([r["diff"] for r in win], [[1.0, r["after"]] for r in win], 3)
        self.assertAlmostEqual(n["reg_did_se"], se[1], places=12)
        self.assertEqual(len([r for r in rows if r["period"] == "lead"]), 28)
        self.assertEqual(rows[0]["day"], "2024-04-03")                  # three windows before the date
        self.assertEqual(rows[-1]["day"], "2024-05-28")

    def test_every_number_on_the_card_is_the_computed_output(self):
        y = series_days("2024-03-01", 120, lambda i: 20 + 3 * math.sin(i) + (30 if i >= 75 else 0))
        c = series_days("2024-03-01", 120, lambda i: 30 + 2 * math.cos(i))
        rows, meta, card = self.compute(y, c)
        n = impact_study.numbers_from_rows(rows)
        self.assertEqual(card["numbers"], n)
        f2 = lambda v: common.fmt(v, 2)  # noqa: E731
        texts = [co[s]["text"] for co in card["callouts"] for s in ("before", "after")]
        self.assertEqual(texts, [f2(n["series_pre"]), f2(n["series_post"]), f2(n["control_pre"]), f2(n["control_post"]), f"{f2(n['did_abs'])} higher", f2(n["reg_did_se"])])
        rows_t = card["effect_table"]["rows"]
        self.assertEqual((rows_t[0]["coef_per_gw"], rows_t[0]["se"], rows_t[0]["p"], rows_t[0]["n"]), (n["reg_did"], n["reg_did_se"], n["reg_did_p"], n["reg_n"]))
        self.assertEqual((rows_t[2]["coef_per_gw"], rows_t[2]["se"]), (n["pre_slope"], n["pre_slope_se"]))
        words = card["why"]
        self.assertEqual(words, card["effect_table"]["in_words"])
        for v in (n["series_post"], n["series_pre"], n["series_change"], n["control_pre"], n["control_post"], n["control_change"], n["did"], n["reg_did_se"]):
            self.assertIn(f"USD {f2(abs(v))} per MWh", words)
        self.assertIn("In the 14 days from 15 May 2024", words)
        self.assertIn(f"Newey-West, {n['reg_lags']} lags, {n['reg_n']} days", words)
        # the parallel movement is shown, not asserted: a second chart of the days before the date
        pre = card["more_charts"][0]["spec"]
        self.assertEqual(len(pre["x"]), 42)
        self.assertTrue(all(d < "2024-05-15" for d in pre["x"]))
        self.assertEqual(card["chart"]["mark_area"]["from"], "2024-05-15")
        self.assertEqual(card["kind"], "econometric")

    def test_the_sentence_carries_no_cause(self):
        y = series_days("2024-03-01", 120, lambda i: 20 + (30 if i >= 75 else 0) + math.sin(i))
        c = series_days("2024-03-01", 120, lambda i: 30 + math.cos(i))
        _, _, card = self.compute(y, c)
        text = (card["why"] + " " + card["subtitle"]).lower()
        for word in ("caused", "because", "due to", "led to", "drove", "thanks to", "as a result", "impact of"):
            self.assertNotIn(word, text)
        self.assertIn("it does not say what produced it", text)
        self.assertIn("more than 1.96 standard errors from zero", text)
        quiet = series_days("2024-03-01", 120, lambda i: 20 + 5 * math.sin(i * 1.7))
        _, _, card = self.compute(quiet, c)
        self.assertIn("no difference beyond the error", card["why"])

    def test_the_refusals_say_what_is_missing_and_draw_nothing(self):
        y = series_days("2024-03-01", 120, lambda i: 20 + math.sin(i))
        c = series_days("2024-03-01", 120, lambda i: 30 + math.cos(i))
        cases = [({"control": "ercot_north_rt"}, "The control is the series itself"),
                 ({"control": "henry_hub"}, "not a quantity"),
                 ({"year": 2023, "month": 2, "day": 31}, "does not exist"),
                 ({"year": 2019, "month": 1, "day": 1}, "is outside what"),
                 ({"year": 2024, "month": 6, "day": 27}, "Too few days to compare: 14 before 27 June 2024 and 2 from it"),
                 ({"control": "ercot_north_da"}, None)]
        for over, needle in cases:
            cc = y if over.get("control") == "ercot_north_da" else c       # a control equal to the series on every day
            rows, meta, card = self.compute(y, cc, **over)
            self.assertEqual(rows, [], over)
            self.assertIn(needle or "equals the series on every one", card["refusal"], over)
            self.assertEqual((card["chart"]["kind"], card["callouts"], card["numbers"], card["why"]), ("none", [], {}, ""), over)
            self.assertNotIn("effect_table", card)
            self.assertNotIn("more_charts", card)

    def test_it_is_an_analysis_of_the_engine_with_declared_inputs(self):
        self.assertIn("impact_study", run_finding.FINDINGS)
        self.assertEqual(run_finding.FINDINGS[:7], ["batteries_lunch", "gas_sets_price", "queue_divorce", "peak_hour_moved", "who_rescues_whom", "negative_prices_west", "batteries_curtailment"])
        self.assertEqual((impact_study.NAME, impact_study.KIND), ("impact_study", "econometric"))
        self.assertEqual(list(impact_study.INPUTS), ["series", "control", "event", "year", "month", "day", "window"])
        for k, spec in impact_study.INPUTS.items():
            self.assertIn(spec["default"], spec["choices"], k)
        self.assertEqual(run_finding.coerce(impact_study, {"window": "28"})["window"], 28)
        with self.assertRaises(ValueError):
            run_finding.coerce(impact_study, {"series": "something_else"})
        self.assertEqual(run_finding.card_id("impact_study", {"event": "date", "year": 2024}, impact_study), "impact_study__event-date")
        self.assertIn('ORDER.push("impact_study")', src("site", "lib", "findings.ts"))
        cat = json.loads(src("site", "data", "findings", "catalogue.json"))
        self.assertEqual(cat[-1]["id"], "impact_study")
        self.assertEqual(cat[-1]["inputs"]["series"]["words"]["ercot_north_rt"], "ERCOT North Hub real-time price")
        # the Roundup's runner is not made to restore the series' tables
        self.assertEqual(impact_study.TABLES, ["event_window_daily"])

    def test_the_do_file_reads_past_the_comment_lines(self):
        text = impact_study.stata({})
        self.assertIn('import delimited "erw_2026_impact_event_control.csv", varnames(5) rowrange(6) stringcols(_all) clear', text)
        self.assertIn("newey diff after, lag(`lags')", text)
        self.assertIn("local lags = floor(4 * (_N / 100)^(2 / 9))", text)
        self.assertEqual(impact_study.csv_name({"event": "date", "year": 2024, "month": 5}), "erw_2026_impact_event_control__event-date.csv")
        self.assertIn('"erw_2026_impact_event_control__event-date.csv"', impact_study.stata({"event": "date"}))

    def test_the_committed_card_is_reproduced_from_its_csv(self):
        card = json.loads(src("site", "data", "findings", "impact_study.json"))
        path = os.path.join(ROOT, "site", "public", "findings", card["downloads"]["csv"])
        with open(path, encoding="utf-8") as f:
            head = [next(f) for _ in range(5)]
        self.assertTrue(all(h.startswith("#") for h in head[:4]) and head[4].startswith("day,t,period,after,in_window,series_value,control_value,diff"))
        self.assertTrue(all("," not in h for h in head[:4]), "a comma in a comment line: the do-file reads the names from line 5")
        n = impact_study.numbers_from_rows(common.read_rows_csv(path), card["params"])
        self.assertEqual(set(n), set(card["numbers"]))
        for k, v in card["numbers"].items():
            if v is None:
                self.assertIsNone(n[k])
            else:
                self.assertAlmostEqual(n[k], v, places=6, msg=k)
        self.assertEqual(card["params"]["event"], "uri_2021")
        self.assertEqual((card["numbers"]["n_pre"], card["numbers"]["n_post"]), (14, 14))
        self.assertEqual(src("site", "public", "findings", "impact_study.py"), src("warehouse", "analysis", "findings", "impact_study.py"))
        self.assertEqual(src("site", "public", "findings", "impact_study.do"), impact_study.stata({}))

    def test_the_events_are_the_ones_the_warehouse_holds(self):
        p = os.path.join(common.DEFAULT_IN_DIR, "event_window_daily.csv")
        if not os.path.exists(p):
            self.skipTest("event_window_daily is not on this machine")
        head = ""
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                head += line
        held = dict(re.findall(r"(\w+) \([^)]*\), window (\d{4}-\d{2}-\d{2}) to", head))
        for k, (_, first) in impact_study.EVENTS.items():
            self.assertEqual(held.get(k), first, k)


class TheMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = src("warehouse", "supabase", "migrations", "029_scanner_drafts.sql")
        cls.rb = src("warehouse", "supabase", "rollbacks", "029_scanner_drafts.sql")

    def test_the_table_is_internal(self):
        self.assertIn("create table if not exists public.scanner_drafts", self.sql)
        self.assertIn("alter table public.scanner_drafts enable row level security;", self.sql)
        self.assertIn("revoke all on public.scanner_drafts from public, anon, authenticated;", self.sql)
        self.assertNotIn("create policy", self.sql.lower())
        self.assertNotRegex(self.sql.lower(), r"grant\s+(select|insert|update|delete|all)")
        self.assertIn("check (state in ('draft', 'approved', 'dismissed', 'full_card_asked'))", self.sql)
        for col in ("state_at", "state_history", "request_id", "flag ", "card ", "scanner_version", "flag_key"):
            self.assertIn(col, self.sql)

    def test_the_functions_check_the_token_as_028_does(self):
        fns = re.findall(r"create or replace function public\.(\w+)\(p_token text", self.sql)
        self.assertEqual(fns, ["scanner_drafts_list", "scanner_draft_set_state", "analysis_request_card"])
        self.assertEqual(self.sql.count("if not erw_private.site_token_ok(p_token) then"), 3)
        self.assertEqual(self.sql.count("raise exception 'not authorized' using errcode = '42501';"), 3)
        self.assertEqual(self.sql.count("security definer set search_path = ''"), 3)
        self.assertEqual(len(re.findall(r"revoke all on function public\.\w+\([^)]*\) from public;", self.sql)), 3)
        self.assertEqual(len(re.findall(r"grant execute on function public\.\w+\([^)]*\) to anon, authenticated;", self.sql)), 3)
        # the request's card is a read of migration 027's table: nothing of that table is altered here
        self.assertNotIn("alter table public.analysis_requests", self.sql)
        self.assertRegex(self.sql, r"function public\.analysis_request_card\(p_token text, p_id text\)\s+returns jsonb language plpgsql stable")
        self.assertIn("order by r.raised_day desc, r.strength desc", self.sql)          # newest and strongest first
        self.assertIn("state_history = state_history || jsonb_build_array(", self.sql)  # each change with its time
        self.assertIn("p_id !~ '^scan-[a-z]+-[0-9a-f]{12}$'", self.sql)

    def test_the_rollback_and_the_verifier(self):
        self.assertIn("drop table if exists public.scanner_drafts;", self.rb)
        self.assertIn("drop function if exists public.scanner_draft_set_state(text, text, text, text);", self.rb)
        self.assertIn("drop function if exists public.scanner_drafts_list(text, text, integer);", self.rb)
        self.assertIn("drop function if exists public.analysis_request_card(text, text);", self.rb)
        self.assertNotIn("analysis_requests;", self.rb)                     # migration 027's table is never dropped here
        self.assertNotIn("rollback", " ".join(os.listdir(os.path.join(ROOT, "warehouse", "supabase", "migrations"))))
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
        spec = importlib.util.spec_from_file_location("s181_verify_rls", os.path.join(ROOT, "warehouse", "supabase", "verify_rls.py"))
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        self.assertEqual(v.EXPECTED["scanner_drafts"], "blocked")
        self.assertIn(("scanner_drafts_list", {}), v.TOKEN_FUNCTIONS)
        self.assertIn("analysis_request_card", [f for f, _ in v.TOKEN_FUNCTIONS])

    def test_the_stub_follows_the_sql(self):
        stub = src("site", "scripts", "findings-stub.mjs")
        for fn in ("scanner_drafts_list", "scanner_draft_set_state", "analysis_request", "analysis_request_card"):
            self.assertIn(fn, stub)
        self.assertIn('code: "42501"', stub)
        self.assertIn('reason: "no such draft"', stub)
        self.assertIn("/^scan-[a-z]+-[0-9a-f]{12}$/", stub)


class TheDailyStep(unittest.TestCase):
    def test_it_is_a_soft_step_in_both_daily_runs_and_never_a_model_step(self):
        sh = src("warehouse", "run_daily.sh")
        self.assertIn('soft_step scanner_request "$PYTHON" warehouse/analysis/findings/findings_scanner.py --request', sh)
        self.assertNotRegex(sh, r"model_step\s+scanner")
        self.assertGreater(sh.index("soft_step scanner_request"), sh.index(". warehouse/soft_step.sh"))
        dm = src("warehouse", "run_data_machine.sh")
        self.assertIn('soft_step dm_scanner "$PYTHON" warehouse/analysis/findings/findings_scanner.py --daily', dm)
        code = src("warehouse", "analysis", "findings", "findings_scanner.py")
        self.assertNotIn("api.anthropic.com", code)
        self.assertNotRegex(code, r"^\s*(import|from) anthropic", )

    def test_without_its_inputs_it_skips_with_the_reason(self):
        lines = []
        with mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75"}), mock.patch.object(scanner, "supabase", lambda: None):
            self.assertEqual(scanner.request_scan(log=lines.append), 75)
        self.assertIn("scanner_request SKIPPED", lines[-1])
        lines = []
        with mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75", "GITHUB_ACTIONS": "true"}):
            self.assertEqual(scanner.daily_scan(log=lines.append), 75)
        self.assertIn("scanner SKIPPED", lines[-1])
        empty = tempfile.mkdtemp(prefix="erw181_empty_")
        try:
            lines = []
            with mock.patch.dict(os.environ, {"ERW_SKIP_EXIT": "75", "GITHUB_ACTIONS": ""}):
                self.assertEqual(scanner.daily_scan(empty, log=lines.append), 75)
            self.assertIn("the price histories are not on this machine", lines[-1])
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_the_worker_runs_the_scan_and_the_impact_study(self):
        w = src("warehouse", "analysis", "findings", "worker.py")
        self.assertIn('SCANNER = "scanner_daily"', w)
        self.assertEqual(scanner.REQUEST_FINDING, "scanner_daily")
        self.assertIn("daily_request", w)
        self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", "test_session181_worker.py")))
        for f in ("register_findings_worker.ps1", "unregister_findings_worker.ps1", "queue_analysis_request.py"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "scripts", f)), f)


class TheSite(unittest.TestCase):
    def test_the_review_page_is_behind_the_cookie_with_no_token_in_an_address(self):
        page = src("site", "app", "internal", "findings", "page.tsx")
        self.assertIn("internalOk((await cookies()).get(COOKIE)?.value)", page)
        self.assertIn("notFound()", page)
        self.assertNotIn("searchParams", page)
        self.assertNotIn("sp.token", page)
        self.assertIn('robots: { index: false, follow: false }', page)
        self.assertIn('export const dynamic = "force-dynamic"', page)
        self.assertIn("<FindingCard card={d.card} roundup={false} />", page)

    def test_the_state_route_is_guarded_as_session_177s_are(self):
        route = src("site", "app", "internal", "findings", "state", "route.ts")
        order = [route.index(x) for x in ("if (!sameOrigin(req)) return hidden();", "if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();",
                                          'if (!typed(req, "json"))', 'await limited(req, "findings_state"')]
        self.assertEqual(order, sorted(order))
        self.assertIn("export async function POST", route)
        self.assertNotIn("export async function GET", route)
        self.assertNotIn("searchParams", route)
        self.assertIn('"Cache-Control": "no-store", "X-Robots-Tag": "noindex"', route)
        self.assertIn('rpc<{ ok: boolean; reason?: string; id?: string }>("analysis_request"', route)
        approved = src("site", "app", "internal", "findings", "approved", "route.ts")
        self.assertIn('listDrafts("approved")', approved)
        self.assertIn("internalOk(req.cookies.get(COOKIE)?.value)", approved)
        lib = src("site", "lib", "scanner.ts")
        self.assertIn('import "server-only";', lib)
        self.assertIn('"scanner_drafts_list"', lib)
        self.assertIn('"scanner_draft_set_state"', lib)

    def test_approved_drafts_and_the_impact_form_are_on_analysis(self):
        page = src("site", "app", "analysis", "page.tsx")
        self.assertIn('<Section title="Found by the scanner">', page)
        self.assertIn("<ScannerFound />", page)
        self.assertIn("<ImpactForm entry={impact} />", page)
        self.assertIn("export const revalidate = 3600;", page)                 # the page is the static page it was
        found = src("site", "components", "analysis", "ScannerFound.tsx")
        self.assertIn('fetch("/internal/findings/approved"', found)
        self.assertIn("found={`flagged ${d.flag_date}, approved ${d.approved_at}`}", found)
        card = src("site", "components", "analysis", "FindingCard.tsx")
        self.assertIn("Found by the scanner, {found}", card)
        self.assertIn("Draft: raised by the scanner, not reviewed", card)
        self.assertIn("data-refusal", card)
        form = src("site", "components", "analysis", "ImpactForm.tsx")
        for k in ('select("series"', 'select("control"', 'select("event"', 'select("window"', 'data-impact-reset="1"', 'type="date"'):
            self.assertIn(k, form)
        self.assertIn('finding: entry.id', form)
        release = src("site", "lib", "release.ts")
        self.assertRegex(release, r'"/analysis": "review"')
        self.assertIn('path.startsWith("/internal/")', release)

    def test_a_requests_card_is_read_where_it_was_asked(self):
        route = src("site", "app", "api", "analysis", "route.ts")
        self.assertIn('rpc<unknown | null>("analysis_request_card", { p_token: token(), p_id: id })', route)
        self.assertLess(route.index("export async function GET"), route.index('searchParams.get("id")'))
        self.assertLess(route.index("if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();", route.index("export async function GET")), route.index('searchParams.get("id")'))
        rc = src("site", "components", "analysis", "RequestCard.tsx")
        self.assertIn("fetch(`/api/analysis?id=${encodeURIComponent(requestId)}`", rc)
        self.assertIn("<FindingCard card={card} roundup={false} files={false} />", rc)
        for k in ('data-download="csv"', 'data-download="python"', 'data-download="stata"'):
            self.assertIn(k, rc)
        self.assertIn("<RequestCard key={shown} requestId={shown} />", src("site", "components", "analysis", "RequestForm.tsx"))
        self.assertIn("<RequestCard key={asked} requestId={asked} wait />", src("site", "components", "analysis", "ImpactForm.tsx"))
        # the card carries what the downloads are made from: its rows are the CSV's rows, its do-file the engine's
        card = json.loads(src("site", "data", "findings", "impact_study.json"))
        rows = common.read_rows_csv(os.path.join(ROOT, "site", "public", "findings", card["downloads"]["csv"]))
        self.assertEqual(len(card["rows"]), len(rows))
        for a, b in zip(card["rows"], rows):
            self.assertEqual(list(a), list(b))
            for k in a:
                if isinstance(a[k], float) or isinstance(b[k], float):
                    self.assertAlmostEqual(a[k], b[k], places=6)
                else:
                    self.assertEqual(a[k], b[k])
        self.assertEqual(card["do_file"], impact_study.stata({}))
        self.assertEqual(card["csv_name"], card["downloads"]["csv"])

    def test_the_chart_kind_is_interactive(self):
        chart = src("site", "lib", "discoverychart.ts")
        self.assertIn('tooltip: { trigger: "axis"', chart)
        self.assertIn("markPoint", chart)
        self.assertIn('if (c.kind === "flag_line" || c.kind === "none") return discoveryOption(c);', src("site", "lib", "findingchart.ts"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_this_session_wrote(self):
        for parts in OWN:
            p = os.path.join(ROOT, *parts)
            if not os.path.exists(p):
                continue
            self.assertNotIn(chr(8212), src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
