"""Session 182, parts (1) to (3): three finding cards.

(1) "Batteries ate their own lunch?" on five grids (batteries_lunch_grids), (2) "The peak hour moved" on five grids
(peak_hour_grids), (3) "By how much do batteries cut curtailment" by the hour for CAISO (batteries_curtailment_hourly),
and the correlation coefficient added to the daily card (batteries_curtailment).

What is proved here, from the committed files alone (no table, no network, no model call, no environment change):
every number on each card is recomputed from the card's own CSV download by the finding's own Python; the ERCOT panel
of card (1) equals the old ERCOT card number for number, and the ERCOT and CAISO numbers of card (2) equal the old card's;
every number in a callout, a paragraph or a grid's sentence is a number of the card; a grid's panel starts where its
prices start; MISO and PJM are placeholders and never data; the do-files obey the owner's rules and read their CSV past
its four comment lines; the CSV hashes are pinned and the files' line endings are fixed by .gitattributes; the renders
are there at both sizes; no em dash.
"""
import hashlib
import importlib
import json
import os
import re
import struct
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIND182 = os.path.join(ROOT, "warehouse", "analysis", "findings")
CARDS182 = os.path.join(ROOT, "site", "data", "findings")
DOWN182 = os.path.join(ROOT, "site", "public", "findings")
EM182 = chr(0x2014)
GRIDS182 = ["ercot", "caiso", "nyiso", "isone", "spp"]
NEW182 = ["batteries_lunch_grids", "peak_hour_grids", "batteries_curtailment_hourly"]
FILES182 = [f"warehouse/analysis/findings/{n}.py" for n in NEW182] + [
    "warehouse/analysis/findings/batteries_curtailment.py", "tests/test_session182.py", "site/components/analysis/MultiChart.tsx",
    "site/components/analysis/CardChart.tsx", "site/app/analysis/card/render.css", "site/lib/findings.ts",
    "docs/methods/automated_analysis_findings.md", "archive/sessions/SESSION_182_REPORT.md"]
# numbers a sentence may hold that are definitions, not results: thresholds, clock hours, the form's number, the count of parameters
CONSTANTS182 = {"0.001", "2021", "1,000", "1000", "250", "17", "00", "21", "59", "10", "15", "860", "930", "99.9", "99", "1", "90", "2024", "20", "300", "9", "5", "24"}


def mod182(name):
    if FIND182 not in sys.path:
        sys.path.insert(0, FIND182)
    return importlib.import_module(name)


def src182(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def card182(name):
    with open(os.path.join(CARDS182, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def close182(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return list(a) == list(b)
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    if isinstance(a, float) and np.isnan(a):
        return isinstance(b, float) and np.isnan(b)
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def rows182(name):
    common = mod182("findings_common")
    return common.read_rows_csv(os.path.join(DOWN182, card182(name)["downloads"]["csv"]))


def recomputed182(name):
    m = mod182(name)
    c = card182(name)
    got = m.numbers_from_rows(rows182(name), c["params"])
    return c, (got[0] if isinstance(got, tuple) else got)


def pool182(c):
    """Every way a number of the card may be printed: 0, 1 or 2 decimals, a fleet in GW, a period's parts."""
    common = mod182("findings_common")
    pool = set(CONSTANTS182)
    for k, v in c["numbers"].items():
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            for nd in (0, 1, 2, 3):
                pool.add(common.fmt(v, nd))
                pool.add(common.fmt(abs(v), nd))
            if k.endswith("_mw"):
                pool.add(common.fmt(v / 1000.0, 2))
        elif isinstance(v, str):
            pool.add(v)
            pool.update(v.split("-"))
    return pool | {p.replace(",", "") for p in pool}


def numbers_in182(text):
    return [x.rstrip(".,") for x in re.findall(r"\d[\d,]*\.?\d*", text)]


class Registered182(unittest.TestCase):
    def test_the_three_are_in_the_runner_the_catalogue_and_the_list(self):
        run_finding = mod182("run_finding")
        for n in NEW182:
            self.assertIn(n, run_finding.FINDINGS)
        cat = json.load(open(os.path.join(CARDS182, "catalogue.json"), encoding="utf-8"))
        self.assertEqual([c["id"] for c in cat], run_finding.FINDINGS)
        ts = src182("site", "lib", "findings.ts")
        self.assertIn('export const ORDER = ["batteries_lunch", "gas_sets_price", "queue_divorce", "peak_hour_moved", "who_rescues_whom", "negative_prices_west", "batteries_curtailment"];', ts,
                      "the list of session 174 stands as it was: session 182 added lines only")
        self.assertIn('export const SUPERSEDED: Record<string, string> = { batteries_lunch: "batteries_lunch_grids", peak_hour_moved: "peak_hour_grids" };', ts)
        self.assertIn('ORDER.splice(ORDER.indexOf("batteries_curtailment") + 1, 0, "batteries_curtailment_hourly");', ts)
        self.assertIn("ORDER.push(...Object.keys(SUPERSEDED));", ts)

    def test_the_old_cards_stay(self):
        # nothing a page shows is dropped: the single-grid cards are still cards, with their downloads and renders
        for old in ("batteries_lunch", "peak_hour_moved", "batteries_curtailment"):
            c = card182(old)
            for f in list(c["downloads"].values()) + [f"{old}_1080x1350.png", f"{old}_1600x900.png"]:
                self.assertTrue(os.path.exists(os.path.join(DOWN182, f)), f)
        self.assertEqual(card182("batteries_lunch_grids")["supersedes"], "batteries_lunch")
        self.assertEqual(card182("peak_hour_grids")["supersedes"], "peak_hour_moved")

    def test_each_module_declares_the_contract(self):
        for n in NEW182:
            m = mod182(n)
            self.assertEqual(m.NAME, n)
            self.assertEqual(m.TITLE, m.TITLE.upper())
            self.assertIn(m.KIND, ("visual", "econometric"))
            self.assertTrue(re.fullmatch(r"[a-z]+_\d{4}_[a-z]+(_[a-z]+)+\.csv", m.CSV_NAME), m.CSV_NAME)
            for k, spec in m.INPUTS.items():
                self.assertIn(spec["default"], spec["choices"], f"{n}.{k}")
            self.assertFalse([t for t in m.TABLES if "miso" in t or "pjm" in t], f"{n} reads no MISO or PJM table")


class EveryNumberIsReproduced182(unittest.TestCase):
    def test_lunch_grids(self):
        c, n = recomputed182("batteries_lunch_grids")
        self.assertGreater(len(c["numbers"]), 200)
        for k, v in c["numbers"].items():
            self.assertIn(k, n, k)
            self.assertTrue(close182(n[k], v), f"{k}: recomputed {n[k]!r}, card {v!r}")

    def test_peak_grids(self):
        c, n = recomputed182("peak_hour_grids")
        self.assertGreater(len(c["numbers"]), 150)
        for k, v in c["numbers"].items():
            self.assertIn(k, n, k)
            self.assertTrue(close182(n[k], v), f"{k}: recomputed {n[k]!r}, card {v!r}")

    def test_the_effect_tables_are_the_numbers(self):
        c = card182("batteries_lunch_grids")
        n = c["numbers"]
        self.assertEqual(len(c["effect_table"]["columns"]), 6)
        self.assertEqual(len(c["effect_table"]["rows"]), 5)
        for g, r in zip(GRIDS182, c["effect_table"]["rows"]):
            self.assertEqual(r["coef_per_gw"], n[f"{g}_reg_multiple_coef"], g)
            self.assertEqual(r["se"], n[f"{g}_reg_multiple_se"], g)
            self.assertEqual(r["p"], n[f"{g}_reg_multiple_p"], g)
            self.assertEqual(r["n"], n[f"{g}_reg_n"], g)
            self.assertEqual(r["r2"], n[f"{g}_reg_multiple_r2"], g)
        _, fits = mod182("batteries_lunch_grids").numbers_from_rows(rows182("batteries_lunch_grids"))
        for p in c["chart"]["panels"]:
            f = fits[p["grid"]]
            self.assertEqual(len(p["table"]), 3, p["grid"])
            for r, key in zip(p["table"], ("worst_interval_multiple", "hours_ge_1000", "hours_top1pct")):
                for a, b in ((r["coef_per_gw"], f[key]["coef"]), (r["se"], f[key]["se"]), (r["p"], f[key]["p"]), (r["r2"], f[key]["r2"])):
                    self.assertTrue(close182(a, b), (p["grid"], key, a, b))

    def test_the_chart_is_the_csv(self):
        for name, key_of in (("batteries_lunch_grids", lambda r: r["period"] if r["kind"] == "month" else None),
                             ("peak_hour_grids", lambda r: str(r["year"]) if r["hour"] == 0 else None)):
            c = card182(name)
            rows = rows182(name)
            x = c["chart"]["x"]
            for p in c["chart"]["panels"]:
                by = {key_of(r): r for r in rows if r["grid"] == p["grid"] and key_of(r) is not None}
                for m in c["chart"]["measures"]:
                    for xi, v in zip(x, p["values"][m["key"]]):
                        want = by[xi][m["key"]] if xi in by else None
                        if name == "peak_hour_grids" and xi in by and not by[xi]["n_days"]:
                            want = None
                        self.assertTrue(close182(v, want), (name, p["grid"], m["key"], xi, v, want))
                fleet_key = "battery_mw" if name == "batteries_lunch_grids" else "solar_mw_yearend"
                for xi, v in zip(x, p["fleet"]):
                    if v is not None:
                        self.assertTrue(close182(v, by[xi][fleet_key]), (name, p["grid"], xi))


class TheOldCardsAreReproduced182(unittest.TestCase):
    """The ERCOT panel of the five-grid lunch card is the old ERCOT card; the ERCOT and CAISO numbers of the five-grid
    peak hour card are the old card's. Compared with the committed old cards, which this session did not rewrite."""

    def test_lunch_ercot_equals_the_old_card(self):
        old, new = card182("batteries_lunch"), card182("batteries_lunch_grids")
        self.assertEqual(old["params"]["hub"], "HB_HUBAVG")
        self.assertGreater(len(old["numbers"]), 30)
        for k, v in old["numbers"].items():
            self.assertTrue(close182(new["numbers"][f"ercot_{k}"], v, 1e-12), f"{k}: new {new['numbers'][f'ercot_{k}']!r}, old {v!r}")
        panel = next(p for p in new["chart"]["panels"] if p["grid"] == "ercot")
        self.assertEqual(panel["single"]["x"], old["chart"]["x"])
        for a, b in zip(panel["single"]["series"], old["chart"]["series"]):
            self.assertEqual(len(a["values"]), len(b["values"]))
            for u, w in zip(a["values"], b["values"]):
                self.assertTrue(close182(u, w, 1e-12), (a["name"], u, w))
        for a, b in zip(panel["table"], old["effect_table"]["rows"]):
            for k in ("coef_per_gw", "se", "p", "n", "r2"):
                self.assertTrue(close182(a[k], b[k], 1e-12), (k, a[k], b[k]))
        for a, b in zip(panel["callouts"], old["callouts"]):
            self.assertEqual((a["before"], a["after"]), (b["before"], b["after"]))
        self.assertEqual(new["meta"]["grids"]["ercot"]["top1_threshold_usd_mwh"], old["meta"]["top1_threshold_usd_mwh"])

    def test_lunch_ercot_rows_equal_the_old_csv(self):
        common = mod182("findings_common")
        old = common.read_rows_csv(os.path.join(DOWN182, card182("batteries_lunch")["downloads"]["csv"]))
        new = {(r["period"], r["kind"]): r for r in rows182("batteries_lunch_grids") if r["grid"] == "ercot"}
        self.assertEqual(len(old), len(new))
        for r in old:
            n = new[(str(r["period"]), r["kind"])]
            for k, v in r.items():
                if k not in ("hub", "period", "kind"):
                    self.assertTrue(close182(n[k], v, 1e-12), (r["period"], k, n[k], v))

    def test_peak_ercot_and_caiso_equal_the_old_card(self):
        old, new = card182("peak_hour_moved"), card182("peak_hour_grids")
        self.assertGreater(len(old["numbers"]), 50)
        for k, v in old["numbers"].items():
            self.assertTrue(close182(new["numbers"][k], v, 1e-12), f"{k}: new {new['numbers'][k]!r}, old {v!r}")
        common = mod182("findings_common")
        old_rows = common.read_rows_csv(os.path.join(DOWN182, old["downloads"]["csv"]))
        new_rows = {(r["grid"], r["year"], r["hour"]): r for r in rows182("peak_hour_grids")}
        self.assertEqual(len(old_rows), 2 * 8 * 24)
        for r in old_rows:
            n = new_rows[(r["grid"], r["year"], r["hour"])]
            for k, v in r.items():
                self.assertTrue(close182(n[k], v, 1e-12), (r["grid"], r["year"], r["hour"], k))
        for g in ("ercot", "caiso"):
            self.assertEqual(new["meta"]["spans"][g], old["meta"]["spans"][g])


class TheWordsHoldOnlyCardNumbers182(unittest.TestCase):
    def check(self, name, text, pool, what):
        for x in numbers_in182(text):
            self.assertIn(x, pool, f"{name}: {x!r} in {what} is not a number of the card: {text[:160]!r}")

    def test_callouts_paragraph_subtitle_and_each_grids_words(self):
        for name in ("batteries_lunch_grids", "peak_hour_grids"):
            c = card182(name)
            pool = pool182(c)
            for co in c["callouts"]:
                for side in ("before", "after"):
                    self.check(name, co[side]["text"], pool, "a callout")
            self.check(name, c["why"], pool, "the paragraph")
            self.check(name, c["subtitle"], pool, "the subtitle")
            for p in c["chart"]["panels"]:
                self.check(name, p["in_words"], pool, f"{p['grid']}'s words")
                self.check(name, p["caveat"], pool, f"{p['grid']}'s caveat")
                for co in p["callouts"]:
                    for side in ("before", "after"):
                        self.check(name, co[side]["text"], pool, f"{p['grid']}'s callout")

    def test_causal_words_stay_within_the_design(self):
        for name in ("batteries_lunch_grids", "peak_hour_grids"):
            c = card182(name)
            words = " ".join([c["why"], c["subtitle"], c["footnote"]] + [p["in_words"] + p["caveat"] for p in c["chart"]["panels"]]).lower()
            for bad in ("caused", "because of batteries", "because of solar", "proves", "should buy", "we recommend"):
                self.assertNotIn(bad, words, (name, bad))
        self.assertIn("association", card182("batteries_lunch_grids")["footnote"])
        self.assertIn("does not separate", card182("peak_hour_grids")["why"])

    def test_the_headline_bends_to_the_data(self):
        lunch = mod182("batteries_lunch_grids")
        c = card182("batteries_lunch_grids")
        n = dict(c["numbers"])
        self.assertEqual(c["subtitle"], lunch.verdict(n))
        self.assertEqual(n["grids_reg_negative_sig"], ["ercot"], "the card as committed: only ERCOT's coefficient is negative and clear of zero")
        n["grids_reg_negative_sig"], n["grids_multiple_fell"] = [], []
        self.assertEqual(lunch.verdict(n), "No grid shows spikes shrinking with its fleet")
        peak = mod182("peak_hour_grids")
        c = card182("peak_hour_grids")
        n = dict(c["numbers"])
        self.assertEqual(c["subtitle"], peak.verdict(n))
        n["grids_evening_up_10"], n["grids_evening_down_10"] = [], []
        self.assertEqual(peak.verdict(n), "The dearest hour barely moved on any grid with two full years of prices")


class TheGridsAndThePlaceholders182(unittest.TestCase):
    def test_five_grids_and_two_placeholders_never_data(self):
        want = [{"grid": "miso", "words": "MISO", "text": "paused while terms are reviewed"}, {"grid": "pjm", "words": "PJM", "text": "licensed source needed"}]
        for name in ("batteries_lunch_grids", "peak_hour_grids"):
            c = card182(name)
            self.assertEqual(c["placeholders"], want, name)
            self.assertEqual([p["grid"] for p in c["chart"]["panels"]], GRIDS182, name)
            self.assertEqual(sorted({r["grid"] for r in rows182(name)}), sorted(GRIDS182), f"{name}: no MISO or PJM row in the download")
            self.assertFalse([k for k in c["numbers"] if k.startswith(("miso", "pjm"))], name)
        paused = src182("warehouse", "metadata", "paused_sources.csv")
        self.assertTrue(paused.splitlines()[1].startswith("miso,"), "MISO is paused: the card requests nothing of it")

    def test_a_panel_starts_where_its_prices_start(self):
        c = card182("batteries_lunch_grids")
        x = c["chart"]["x"]
        self.assertEqual(x[0], "2019-01")
        first = {}
        for p in c["chart"]["panels"]:
            vals = p["values"]["worst_interval_multiple"]
            first[p["grid"]] = x[next(i for i, v in enumerate(vals) if v is not None)]
            self.assertEqual(first[p["grid"]], p["first"])
        self.assertEqual(first, {"ercot": "2019-01", "caiso": "2024-09", "nyiso": "2019-01", "isone": "2024-09", "spp": "2024-09"})
        c = card182("peak_hour_grids")
        for p in c["chart"]["panels"]:
            vals = p["values"]["share_evening_pct"]
            y = c["chart"]["x"][next(i for i, v in enumerate(vals) if v is not None)]
            self.assertEqual(y, "2019" if p["grid"] in ("ercot", "nyiso") else "2024", p["grid"])

    def test_the_axes_are_stated_on_the_chart(self):
        for name in ("batteries_lunch_grids", "peak_hour_grids"):
            ch = card182(name)["chart"]
            self.assertEqual(ch["kind"], "multiples")
            self.assertIn("One timeline for every grid", ch["axis_note"])
            self.assertIn("Left axis", ch["axis_note"])
            self.assertIn("Right axis", ch["axis_note"])
            self.assertIn(ch["fleet_axis"], ("shared", "own"))
            self.assertIn(ch["measure_axis"], ("shared", "own"))
            self.assertIn("own scale" if ch["measure_axis"] == "own" else "one shared scale", ch["axis_note"].split("Right axis")[0])

    def test_the_fleet_is_said_exactly(self):
        f = card182("batteries_lunch_grids")["footnote"]
        for bit in ("prime mover BA", "balancing authority code (ERCO, CISO, NYIS, ISNE, SWPP)", "nameplate MW", "first operating month", "HC1",
                    "HB_HUBAVG", "TH_SP15_GEN-APND", "N.Y.C.", ".H.INTERNAL_HUB", "SPPNORTH_HUB", "hourly", "15-minute", "eia930_daily_demand"):
            self.assertIn(bit, f, bit)
        f = card182("peak_hour_grids")["footnote"]
        for bit in ("daylight saving", "Solar Photovoltaic", "ERCO, CISO, NYIS, ISNE, SWPP", "plants under 1 MW", "first hour on a tie"):
            self.assertIn(bit, f, bit)


class TheDownloads182(unittest.TestCase):
    def test_the_csv_hash_is_pinned_and_line_endings_are_fixed(self):
        attrs = src182(".gitattributes")
        for rule in ("site/public/findings/*.csv text eol=lf", "site/public/findings/*.py text eol=lf", "site/public/findings/*.do text eol=lf",
                     "site/data/findings/*.json text eol=lf"):
            self.assertIn(rule, attrs)
        for name in NEW182 + ["batteries_curtailment"]:
            c = card182(name)
            with open(os.path.join(DOWN182, c["downloads"]["csv"]), "rb") as f:
                raw = f.read()
            self.assertNotIn(b"\r\n", raw, name)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), c["csv_sha256"], name)

    def test_the_python_download_is_the_module(self):
        for name in NEW182 + ["batteries_curtailment"]:
            self.assertEqual(src182("site", "public", "findings", name + ".py"), src182("warehouse", "analysis", "findings", name + ".py"), name)

    def test_the_do_files_obey_the_rules_and_read_past_the_comment_lines(self):
        for name in NEW182:
            m = mod182(name)
            text = m.stata({})
            self.assertEqual(text, src182("site", "public", "findings", name + ".do"), name)
            self.assertNotIn("///", text, name)
            self.assertNotIn("/*", text, name)
            for b in text.strip().split("\n\n"):
                lines = b.splitlines()
                if len(lines) > 1:
                    self.assertTrue(lines[0].rstrip().endswith("{") and lines[-1].strip() == "}", f"{name}: a block of several lines that is not a loop: {b!r}")
                    self.assertNotIn("", [ln.strip() for ln in lines], f"{name}: an empty line inside a loop")
            destrung = re.findall(r"destring (\w+), replace force", text)
            self.assertTrue(destrung, name)
            for v in destrung:
                self.assertIn(f"replace {v} = . if {v} == -999", text, f"{name}: no sentinel recoding for {v}")
            if "foreach" in text:
                self.assertLess(text.rfind("== -999"), text.find("foreach"), f"{name}: sentinel recoding after a loop")
            # the CSV's names are on line 5 and its data from line 6: four comment lines stand above them
            self.assertIn(f'import delimited "{m.CSV_NAME}", varnames(5) rowrange(6) stringcols(_all) clear', text, name)
            with open(os.path.join(DOWN182, m.CSV_NAME), encoding="utf-8") as f:
                head = [next(f) for _ in range(6)]
            self.assertTrue(all(ln.startswith("# ") for ln in head[:4]), name)
            self.assertFalse(head[4].startswith("#"), name)
            names = head[4].strip().split(",")
            for v in destrung:
                self.assertIn(v, names, f"{name}: the do-file destrings {v}, which is not a column of the CSV")
            self.assertEqual(len(head[5].split(",")), len(names) if '"' not in head[5] else len(head[5].split(",")), name)

    def test_the_renders_are_there_at_both_sizes(self):
        for name in NEW182 + ["batteries_curtailment"]:
            for w, h in ((1080, 1350), (1600, 900)):
                p = os.path.join(DOWN182, f"{name}_{w}x{h}.png")
                self.assertTrue(os.path.exists(p), p)
                with open(p, "rb") as f:
                    head = f.read(24)
                self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", head[16:24]), (w, h), p)


class TheSite182(unittest.TestCase):
    def test_small_multiples_and_the_one_grid_view_kept_in_the_address(self):
        cc = src182("site", "components", "analysis", "CardChart.tsx")
        self.assertIn('kind === "multiples"', cc)
        mc = src182("site", "components", "analysis", "MultiChart.tsx")
        for bit in ("u.searchParams.set(spec.param, g)", "window.history.replaceState", "new URLSearchParams(window.location.search)", "axisPointer: { link: [{ xAxisIndex: \"all\" }] }",
                    "optionFor(spec)", "data-multi-pick", "spec.axis_note", "MIN_ROW"):
            self.assertIn(bit, mc, bit)
        self.assertEqual(card182("batteries_lunch_grids")["chart"]["param"], "lunch_grid")
        self.assertEqual(card182("peak_hour_grids")["chart"]["param"], "peak_grid")
        css = src182("site", "app", "analysis", "card", "render.css")
        self.assertIn('[data-finding-chart="multiples"]', css)

    def test_the_files_another_session_is_changing_were_not_touched(self):
        # note A of the session: the worker, /analysis's page and view, the request route, the daily run
        ts = src182("site", "app", "analysis", "page.tsx")
        self.assertNotIn("182", ts)
        self.assertNotIn("182", src182("warehouse", "analysis", "findings", "worker.py"))

    def test_no_em_dash_in_this_sessions_files(self):
        for rel in FILES182:
            p = os.path.join(ROOT, *rel.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM182, src182(*rel.split("/")), rel)
        for name in NEW182 + ["batteries_curtailment"]:
            self.assertNotIn(EM182, json.dumps(card182(name), ensure_ascii=False), name)
            self.assertNotIn(EM182, src182("site", "public", "findings", name + ".do"), name)


# ---- card (3): the hourly curtailment card, and the daily card's correlation coefficient ----
# (written by the session's second agent; constants are prefixed C3_)
C3_FINDINGS = os.path.join(ROOT, "warehouse", "analysis", "findings")
C3_CARDS = os.path.join(ROOT, "site", "data", "findings")
C3_DOWNLOADS = os.path.join(ROOT, "site", "public", "findings")
C3_EM = chr(0x2014)
C3_HOURLY = "batteries_curtailment_hourly"
C3_DAILY = "batteries_curtailment"
# the daily card's numbers as session 174 computed them (2026-10-10T03:09:20Z): session 182 adds r and changes none
C3_DAILY_BEFORE = {
    "n_days": 405, "n_months": 15, "first_day": "2025-08-24", "last_day": "2026-10-06", "mean_curtailed_mwh": 13827.347261728395,
    "mean_charging_mwh": 48649.05082304526, "mean_solar_mwh": 163596.91194246916, "median_charging_mwh": 50752.5,
    "curtailed_low_charging_days": 8281.147985221674, "curtailed_high_charging_days": 19401.002970297028, "n_low_days": 203, "n_high_days": 202,
    "max_charging_mwh": 62113.33333333333, "max_curtailed_mwh": 112882.332, "charging_coef": 699.2908372493285, "charging_se": 73.50883720322464,
    "charging_p": 1.7168781162371177e-19, "charging_r2": 0.09271130724477594, "charging_n": 405, "charging_solar_coef": 950.8745801428358,
    "charging_solar_se": 148.41020721763093, "charging_solar_p": 4.1542726256104106e-10, "charging_solar_r2": 0.10151166818627955, "charging_solar_n": 405,
    "charging_solar_month_coef": 1081.243519233697, "charging_solar_month_se": 171.64414403593116, "charging_solar_month_p": 8.113276032475439e-10,
    "charging_solar_month_r2": 0.6535875116005214, "charging_solar_month_n": 405, "solar_coef": -283.90584803443204, "solar_se": 53.69517638573132,
    "solar_p": 2.076676643443552e-07,
}
# the daily CSV's data lines (every line that is not a # comment), byte for byte as session 174 wrote them
C3_DAILY_ROWS_SHA256 = "b5984ef020b8d29b59d7010ccca4ae417a1ea6dabbac43a024cc53e13ae24837"
C3_IMPORT = 'import delimited "{csv}", varnames(5) rowrange(6) stringcols(_all) clear'


def c3_card(name):
    with open(os.path.join(C3_CARDS, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def c3_text(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def c3_module(name):
    if C3_FINDINGS not in sys.path:
        sys.path.insert(0, C3_FINDINGS)
    import importlib
    return importlib.import_module(name)


def c3_close(a, b, rel=1e-6):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    return abs(float(a) - float(b)) <= rel * max(1.0, abs(float(a)), abs(float(b)))


class C3TheHourlyCard(unittest.TestCase):
    """Every number on the hourly card equals what its own CSV download gives when the module reads it back."""

    @classmethod
    def setUpClass(cls):
        cls.common = c3_module("findings_common")
        cls.mod = c3_module(C3_HOURLY)
        cls.card = c3_card(C3_HOURLY)
        cls.csv = os.path.join(C3_DOWNLOADS, cls.card["downloads"]["csv"])
        cls.rows = cls.common.read_rows_csv(cls.csv)
        cls.a = cls.mod.analyse(cls.rows, cls.card["params"])
        cls.n = cls.a["numbers"]

    def test_every_number_is_reproduced_from_the_csv(self):
        self.assertEqual(set(self.mod.numbers_from_rows(self.rows, self.card["params"])), set(self.n))
        self.assertGreater(len(self.card["numbers"]), 150)
        for k, v in self.card["numbers"].items():
            self.assertIn(k, self.n, f"{k} is not recomputed")
            self.assertTrue(c3_close(self.n[k], v), f"{k}: recomputed {self.n[k]!r}, card {v!r}")
        self.assertEqual(set(self.n), set(self.card["numbers"]))

    def test_the_csv_is_the_hashed_download_with_four_comment_lines(self):
        with open(self.csv, "rb") as f:
            raw = f.read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.card["csv_sha256"])
        self.assertNotIn(b"\r", raw, "the hashed CSV keeps LF line endings (.gitattributes: site/public/findings/*.csv text eol=lf)")
        lines = raw.decode("utf-8").split("\n")
        self.assertTrue(all(ln.startswith("# ") for ln in lines[:4]))
        self.assertEqual(lines[4], ",".join(self.mod.COLUMNS), "line 5 holds the names, so the do-file's varnames(5) rowrange(6) is right")
        self.assertEqual(len(self.rows), self.card["numbers"]["n_hours"])
        self.assertEqual(self.card["meta"]["n_hours"], self.card["numbers"]["n_hours"])

    def test_the_callouts_print_the_numbers(self):
        f, n, c = self.common.fmt, self.n, self.card["callouts"]
        y1, yg = n["last_full_year"], n["gw_year"]
        self.assertEqual(len(c), 3)
        self.assertEqual(c[0]["before"]["text"], f(n[f"y{y1}_pred_charging_mw"], 0))
        self.assertEqual(c[0]["after"]["text"], f(n[f"y{y1}_obs_charging_mw"], 0))
        self.assertIn(str(y1), c[0]["label"])
        self.assertEqual(c[1]["before"]["text"], f(n["corr_curtailed_charging"], 2))
        self.assertEqual(c[1]["after"]["text"], f(n["charging_r2"], 2))
        self.assertEqual((c[1]["before"]["period"], c[1]["after"]["period"]), ("correlation r", "R2, charging alone"))
        self.assertEqual((c[2]["before"]["period"], c[2]["after"]["period"]), (str(yg), str(y1)))
        self.assertEqual(c[2]["before"]["text"], f(n[f"y{yg}_sat_curt_hours"], 0))
        self.assertEqual(c[2]["after"]["text"], f(n[f"y{y1}_sat_curt_hours"], 0))
        self.assertIn(f"{n['ceiling_pct']}%", c[2]["label"])

    def test_the_paragraph_prints_the_numbers(self):
        f, n, why = self.common.fmt, self.n, self.card["why"]
        y1, y2 = n["last_full_year"], n["last_year"]
        printed = [f(n["n_hours"], 0), n["first_day"], n["last_day"], f(n["charging_hours_pct"], 1), f(n["curtailed_mwh_in_charging_hours_pct"], 1),
                   f"r = {f(n['corr_curtailed_charging'], 2)}", f"R2 {f(n['charging_r2'], 2)}", f"R2 {f(n['netload_fe_r2'], 2)}",
                   f"predicts {f(n[f'y{y1}_pred_charging_mw'], 0)} MW", f"shows {f(n[f'y{y1}_obs_charging_mw'], 0)} MW",
                   f"{f(abs(n[f'y{y1}_resid_charging_mw']), 0)} MW {'above' if n[f'y{y1}_resid_charging_mw'] > 0 else 'below'}",
                   f"{f(n['resid_years_above'], 0)} of the {f(n['resid_years'], 0)} years and below it in {f(n['resid_years_below'], 0)}",
                   f"in {y2} to date it is {f(abs(n[f'y{y2}_resid_charging_mw']), 0)} MW {'above' if n[f'y{y2}_resid_charging_mw'] > 0 else 'below'}",
                   f"goes with {f(n['charging_coef'], 3)} MW", f"held fixed, {f(n['charging_netload_coef'], 3)};", f"too, {f(n['charging_netload_fe_coef'], 3)} (standard error {f(n['charging_netload_fe_se'], 3)}",
                   f"R2 {f(n['charging_netload_fe_r2'], 2)})", f"{n['ceiling_pct']} percent of its trailing 30-day maximum in {f(n[f'y{y1}_sat_hours'], 0)} hours",
                   f"{f(n[f'y{y1}_sat_curt_hours'], 0)} of them with curtailment still on", f"({f(n[f'y{y1}_sat_curt_mwh'], 0)} MWh, {f(n[f'y{y1}_sat_curt_share_pct'], 1)} percent of the year's)",
                   f"{f(n[f'y{y1}_peak_charging_mw'], 0)} MW, {f(n[f'y{y1}_peak_pct_fleet'], 1)} percent of that month's fleet"]
        for s in printed:
            self.assertIn(s, why, f"{s!r} is not in the paragraph")
        self.assertIn("p < 0.001" if n["charging_netload_fe_p"] < 0.001 else f"p = {n['charging_netload_fe_p']:.3f}", why)

    def test_the_effect_table_and_the_chart_are_the_numbers(self):
        n, t = self.n, self.card["effect_table"]
        self.assertEqual(len(t["columns"]), 6)
        self.assertEqual([r["measure"] for r in t["rows"]], ["charging alone", "charging, net load and its square held fixed", "charging, net load, hour of day and month held fixed"])
        for r, k in zip(t["rows"], ("charging", "charging_netload", "charging_netload_fe")):
            self.assertEqual(set(r), {"measure", "coef_per_gw", "se", "p", "n", "r2"})
            for col, key in (("coef_per_gw", f"{k}_coef"), ("se", f"{k}_se"), ("p", f"{k}_p"), ("n", f"{k}_n"), ("r2", f"{k}_r2")):
                self.assertTrue(c3_close(r[col], n[key]), f"{k}.{col}")
        ch = self.card["chart"]
        self.assertEqual(ch["kind"], "lines")
        self.assertIn('c.kind === "lines"', c3_text("site", "lib", "findingchart.ts"))
        self.assertEqual(ch["x"], [f"{h:02d}" for h in range(24)])
        for s, key in zip(ch["series"], ("curtailed", "pred", "charging")):
            self.assertEqual(len(s["values"]), 24)
            for got, want in zip(s["values"], self.a["by_hour"][key]):
                self.assertTrue(c3_close(got, want), s["name"])
        self.assertIn(str(n["last_full_year"]), ch["series"][0]["name"])

    def test_the_footnote_gives_every_year_of_the_ceiling_reading(self):
        f, foot = self.common.fmt, self.card["footnote"]
        self.assertEqual([r["year"] for r in self.card["by_year"]], [r["year"] for r in self.a["by_year"]])
        for got, r in zip(self.card["by_year"], self.a["by_year"]):
            for k, v in r.items():
                self.assertTrue(c3_close(got[k], v), f"{r['year']}.{k}")
            self.assertIn(f"{r['year']}: {f(r['sat_hours'], 0)} hours at the ceiling, {f(r['sat_curt_hours'], 0)} with curtailment on ({f(r['sat_curt_mwh'], 0)} MWh, "
                          f"{f(r['sat_curt_share_pct'], 1)} percent of the year's; rising in {f(r['sat_rising_hours'], 0)}), peak hour {f(r['peak_charging_mw'], 0)} MW", foot)
            self.assertLessEqual(r["sat_curt_hours"], r["sat_hours"])
            self.assertLessEqual(r["sat_rising_hours"], r["sat_curt_hours"])
            self.assertLessEqual(r["sat_hours"], r["charging_hours"])
        for s in ("cluster-robust by Pacific day", "Pearson correlation", "vce(cluster)", "month-of-sample dummies", "an association", "nothing is filled",
                  f"{f(self.n['clusters'], 0)} clusters", f"{f(self.n['n_hours'], 0)} hours on {f(self.n['n_days'], 0)} days",
                  f"coefficient is {f(self.n['before_curtailment_coef'], 3)} (standard error {f(self.n['before_curtailment_se'], 3)}"):
            self.assertIn(s, foot)

    def test_r_squared_is_the_charging_alone_fit_and_the_panel_is_whole_days(self):
        n = self.n
        self.assertAlmostEqual(n["corr_curtailed_charging"] ** 2, n["charging_r2"], places=9)
        self.assertAlmostEqual(n["corr_squared"], n["charging_r2"], places=9)
        cur = np.array([r["curtailed_mw"] for r in self.rows], float)
        chg = np.array([r["charging_mw"] for r in self.rows], float)
        self.assertAlmostEqual(float(np.corrcoef(cur, chg)[0, 1]), n["corr_curtailed_charging"], places=9)
        self.assertTrue((cur >= 0).all() and (chg >= 0).all())
        per_day = {}
        for r in self.rows:
            per_day[r["day"]] = per_day.get(r["day"], 0) + 1
        self.assertEqual(len(per_day), n["n_days"])
        self.assertTrue(set(per_day.values()) <= {23, 24, 25}, "a day in the panel holds all its hours")
        self.assertEqual(n["clusters"], n["n_days"])
        self.assertEqual(n["first_day"][:4], str(self.card["params"]["first_year"]))
        self.assertEqual(sum(r["hours"] for r in self.a["by_year"]), n["n_hours"])

    def test_the_cluster_robust_errors_are_the_formula_stated(self):
        # a small panel by hand: the sandwich with the clusters' summed scores and Stata's small-sample factor
        rng = np.random.default_rng(182)
        g = np.repeat(np.arange(12), 5)
        x = rng.normal(size=60)
        y = 2.0 + 0.5 * x + rng.normal(size=60) + np.repeat(rng.normal(size=12), 5)
        X = np.column_stack([np.ones(60), x])
        got = self.mod.ols_cluster(y, X, ["const", "x"], g)
        bread = np.linalg.inv(X.T @ X)
        beta = bread @ X.T @ y
        e = y - X @ beta
        meat = np.zeros((2, 2))
        for k in range(12):
            s = X[g == k].T @ e[g == k]
            meat += np.outer(s, s)
        V = (12 / 11) * (59 / 58) * bread @ meat @ bread
        self.assertAlmostEqual(got["coef"]["x"]["coef"], float(beta[1]), places=10)
        self.assertAlmostEqual(got["coef"]["x"]["se"], float(np.sqrt(V[1, 1])), places=10)
        self.assertEqual(got["clusters"], 12)

    def test_the_words_stay_within_the_design(self):
        c = self.card
        words = (c["why"] + " " + c["subtitle"] + " " + c["effect_table"]["in_words"]).lower()
        self.assertIn("association", words)
        self.assertNotIn("caused", words)
        self.assertNotIn("batteries cut curtailment by", words)
        self.assertIn("not what batteries prevent", c["why"])
        self.assertEqual(c["title"], c["title"].upper())
        self.assertEqual(c["kind"], "econometric")
        b, p = self.n["charging_netload_fe_coef"], self.n["charging_netload_fe_p"]
        if p < 0.05 and b < 0:
            self.assertIn("less curtailment", c["subtitle"])
            if self.n["resid_years_above"] and self.n["resid_years_below"]:
                self.assertIn("not in every year", c["subtitle"], "a sign that flips by year is said in the headline")
        elif p < 0.05:
            self.assertIn("more curtailment", c["subtitle"])
        else:
            self.assertIn("cannot pin", c["subtitle"])

    def test_the_downloads_are_the_module_and_its_do_file(self):
        c = self.card
        self.assertEqual(c["downloads"], {"csv": self.mod.CSV_NAME, "python": C3_HOURLY + ".py", "stata": C3_HOURLY + ".do"})
        self.assertEqual(c3_text("site", "public", "findings", C3_HOURLY + ".py"), c3_text("warehouse", "analysis", "findings", C3_HOURLY + ".py"))
        self.assertEqual(c3_text("site", "public", "findings", C3_HOURLY + ".do"), self.mod.stata(c["params"]))


class C3TheDailyCardKeepsItsNumbers(unittest.TestCase):
    """Session 182 adds the correlation coefficient to the daily card; no number it had moves."""

    @classmethod
    def setUpClass(cls):
        cls.common = c3_module("findings_common")
        cls.mod = c3_module(C3_DAILY)
        cls.card = c3_card(C3_DAILY)
        cls.csv = os.path.join(C3_DOWNLOADS, cls.card["downloads"]["csv"])

    def test_every_old_number_is_unchanged(self):
        n = self.card["numbers"]
        for k, v in C3_DAILY_BEFORE.items():
            self.assertEqual(n[k], v, k)
        self.assertEqual(set(n) - set(C3_DAILY_BEFORE), {"corr_curtailed_charging", "corr_squared"})
        self.assertEqual(self.card["computed_at"], "2026-10-10T03:09:20Z", "the rows were not recomputed")

    def test_the_rows_are_the_rows_session_174_wrote(self):
        with open(self.csv, "rb") as f:
            raw = f.read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.card["csv_sha256"])
        data = b"".join(ln for ln in raw.splitlines(keepends=True) if not ln.startswith(b"#"))
        self.assertEqual(hashlib.sha256(data).hexdigest(), C3_DAILY_ROWS_SHA256)
        head = [ln for ln in raw.decode("utf-8").split("\n") if ln.startswith("#")]
        self.assertEqual(len(head), 4)
        self.assertIn(f"Pearson r of curtailed_mwh with charging_mwh over these rows: {self.card['numbers']['corr_curtailed_charging']:.6f}", head[3])

    def test_r_is_reported_beside_r2(self):
        n, f = self.card["numbers"], self.common.fmt
        rows = self.common.read_rows_csv(self.csv)
        got = self.mod.numbers_from_rows(rows, self.card["params"])
        for k, v in n.items():
            self.assertTrue(c3_close(got[k], v), f"{k}: recomputed {got[k]!r}, card {v!r}")
        cu = np.array([r["curtailed_mwh"] for r in rows], float)
        ch = np.array([r["charging_mwh"] for r in rows], float)
        self.assertAlmostEqual(float(np.corrcoef(cu, ch)[0, 1]), n["corr_curtailed_charging"], places=9)
        self.assertAlmostEqual(n["corr_curtailed_charging"] ** 2, n["charging_r2"], places=9)
        self.assertAlmostEqual(n["corr_squared"], n["charging_r2"], places=9)
        self.assertIn(f"r = {f(n['corr_curtailed_charging'], 2)} (R2 {f(n['charging_r2'], 2)}, charging alone)", self.card["why"])
        self.assertIn(f"{f(n['corr_curtailed_charging'], 3)}; its square, {f(n['corr_squared'], 3)}, is the R2 of the charging-alone fit", self.card["footnote"])
        self.assertIn("HC1", self.card["footnote"])

    def test_the_downloads_are_the_module_and_its_do_file(self):
        self.assertEqual(c3_text("site", "public", "findings", C3_DAILY + ".py"), c3_text("warehouse", "analysis", "findings", C3_DAILY + ".py"))
        do = c3_text("site", "public", "findings", C3_DAILY + ".do")
        self.assertEqual(do, self.mod.stata(self.card["params"]))
        self.assertIn("correlate curtailed_mwh charging_mwh", do)


class C3TheDoFiles(unittest.TestCase):
    """The owner's rules, and the import that reads the CSV past its four comment lines."""

    def test_rules_and_the_import(self):
        for name in (C3_HOURLY, C3_DAILY):
            mod = c3_module(name)
            text = mod.stata({})
            self.assertEqual(text, c3_text("site", "public", "findings", name + ".do"), name)
            self.assertNotIn("///", text, name)
            self.assertNotIn("/*", text, name)
            self.assertNotIn(C3_EM, text, name)
            self.assertNotIn("\n\n\n", text, f"{name}: one empty line between commands, not two")
            for b in text.strip().split("\n\n"):
                lines = b.splitlines()
                if len(lines) > 1:
                    self.assertTrue(lines[0].rstrip().endswith("{") and lines[-1].strip() == "}", f"{name}: a multi-line block that is not a loop: {b!r}")
            self.assertIn(C3_IMPORT.format(csv=mod.CSV_NAME), text, f"{name}: the names are on line 5, the data from line 6")
            self.assertNotIn("varnames(1)", text, name)
            self.assertTrue(re.fullmatch(r"[a-z]+_\d{4}_[a-z]+(_[a-z]+)+\.csv", mod.CSV_NAME), mod.CSV_NAME)
            with open(os.path.join(C3_DOWNLOADS, mod.CSV_NAME), encoding="utf-8") as f:
                head = [next(f).rstrip("\n") for _ in range(6)]
            self.assertTrue(all(ln.startswith("#") for ln in head[:4]) and not head[4].startswith("#"), f"{name}: four comment lines, then the names")
            names = head[4].split(",")
            first = head[5].split(",")
            self.assertEqual(len(names), len(first))
            numeric = []
            for nm, v in zip(names, first):
                try:
                    float(v) if v != "" else None
                    numeric.append(nm)
                except ValueError:
                    pass
            destrung = re.findall(r"destring (\w+), replace force", text)
            self.assertEqual(sorted(destrung), sorted(numeric), f"{name}: every numeric column destrung with force")
            for v in destrung:
                self.assertIn(f"replace {v} = . if {v} == -999", text, f"{name}: no sentinel recoding for {v}")
            self.assertLess(text.rfind("== -999"), text.find("\nregress "), f"{name}: the sentinels are recoded before any estimate")
            self.assertLess(text.rfind("destring "), text.find("== -999"), f"{name}: every variable is destrung before the sentinels")

    def test_the_hourly_do_file_runs_the_card_s_estimates(self):
        text = c3_module(C3_HOURLY).stata({})
        for s in ("correlate curtailed_mw charging_mw", "regress curtailed_mw charging_mw, vce(cluster day_id)",
                  "regress curtailed_mw charging_mw net_load_gw net_load_gw2 i.hour i.month_id, vce(cluster day_id)",
                  "regress curtailed_mw net_load_gw net_load_gw2 i.hour i.month_id", "predict residual, residuals",
                  "charging_mw >= 0.90 * trail_max_charging_mw", "charging_mw >= 0.90 * fleet_mw",
                  "regress curtailed_mw charging_mw net_load_before_gw net_load_before_gw2 i.hour i.month_id, vce(cluster day_id)"):
            self.assertIn(s, text)
        self.assertIn("0.95 * trail_max_charging_mw", c3_module(C3_HOURLY).stata({"ceiling_pct": 95}))


class C3NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_card_three_s_files(self):
        for rel in (f"warehouse/analysis/findings/{C3_HOURLY}.py", f"warehouse/analysis/findings/{C3_DAILY}.py",
                    f"site/data/findings/{C3_HOURLY}.json", f"site/data/findings/{C3_DAILY}.json",
                    f"site/public/findings/{C3_HOURLY}.do", f"site/public/findings/{C3_DAILY}.do",
                    f"site/public/findings/{C3_HOURLY}.py", f"site/public/findings/{C3_DAILY}.py"):
            self.assertNotIn(C3_EM, c3_text(*rel.split("/")), rel)
        for name in ("erw_2026_caiso_curtailment_hourly.csv", "erw_2026_caiso_curtailment_batteries.csv"):
            with open(os.path.join(C3_DOWNLOADS, name), encoding="utf-8") as f:
                self.assertNotIn(C3_EM, "".join(next(f) for _ in range(5)), name)


if __name__ == "__main__":
    unittest.main()
