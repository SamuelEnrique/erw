"""Session 66: the home battery game v4.

Energy Research Warehouse (ERW). No network, no model, no database.
1. The solar shape builder (warehouse/derived/battery_solar.py), on small frames written here by hand (test data, never
   a warehouse row): each interval takes its hour's output over the installed nameplate, as reported; a level with an
   hour missing, an hour without a number or no installed capacity gets no shape and loses any older one; nothing is
   filled; prices and every other field stay as they are.
2. Any shape already in site/data/battery_levels.json is whole: one finite number per interval, each hour's value on
   its four intervals, and its source is stated.
3. Migration 019: the preset check allows "-v4" and the add-on words before it, keeps the v2 and v3 presets, refuses
   the rest, changes constraints only, and is the same for both tables.
4. The server's scorer agrees with lib/battery.ts under v4 (site/scripts/check-scorer.mjs calls lib/game.ts's scoreOn
   directly: no site, no post).
5. test-battery.mjs's v4 lines: the DP against brute force with rooftop solar, Part A's result and the multiple, the
   spike's label, the end screen's hour.
6. The page and the method say what the rules are (the penalty and why, the label, the add-on and its source), and no
   file of the session holds an em dash.

    python -m unittest tests.test_session66 -v
"""

import copy
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_solar as bs  # noqa: E402


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def toy_level(slug="toy", grid="ERCOT", start="2030-06-01T05:00:00Z", hours=3):
    """A toy level: `hours` hours of 15-minute intervals from `start` (test data)."""
    ts = pd.date_range(start, periods=hours * 4, freq="15min")
    return {"slug": slug, "date": "2030-06-01", "grid": grid, "ts_utc": [t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in ts],
            "price": [10.0 + i for i in range(hours * 4)], "title": "a toy day", "why": "test data"}


def toy_fuel(values, start="2030-06-01T05:00:00Z"):
    return pd.DataFrame({"sun": values}, index=pd.date_range(start, periods=len(values), freq="h"))


class Shape(unittest.TestCase):
    def test_each_interval_takes_its_hours_output_over_the_nameplate(self):
        shape, why = bs.shape_for(toy_level(), toy_fuel([0.0, 250.0, 1200.0]), 1000.0)
        self.assertEqual(why, "")
        self.assertEqual(shape, [0.0] * 4 + [0.25] * 4 + [1.2] * 4)  # above nameplate kept as reported

    def test_negative_hours_are_kept_as_reported(self):
        shape, _ = bs.shape_for(toy_level(), toy_fuel([-20.0, 0.0, 500.0]), 1000.0)
        self.assertEqual(shape[:4], [-0.02] * 4)

    def test_a_missing_hour_gives_no_shape(self):
        shape, why = bs.shape_for(toy_level(), toy_fuel([0.0, 250.0]), 1000.0)  # the third hour is not held
        self.assertIsNone(shape)
        self.assertIn("2030-06-01T07:00Z is not in the EIA-930 workbook", why)

    def test_an_hour_without_a_number_gives_no_shape(self):
        shape, why = bs.shape_for(toy_level(), toy_fuel([0.0, float("nan"), 500.0]), 1000.0)
        self.assertIsNone(shape)
        self.assertIn("2030-06-01T06:00Z has no solar generation", why)

    def test_no_installed_capacity_gives_no_shape(self):
        for cap in (0.0, None, -5.0):
            shape, why = bs.shape_for(toy_level(), toy_fuel([0.0, 250.0, 500.0]), cap)
            self.assertIsNone(shape)
            self.assertIn("no solar nameplate", why)

    def test_build_writes_whole_shapes_and_removes_the_rest(self):
        held = toy_level("held", "ERCOT")
        gap = dict(toy_level("gap", "CAISO"), solar=[9.0] * 12, solar_source="an older shape")  # CISO's frame lacks an hour
        other = toy_level("other", "PJM")
        before = copy.deepcopy([held, gap, other])
        frames = {"ERCO": toy_fuel([0.0, 250.0, 500.0]), "CISO": toy_fuel([0.0, 250.0])}
        asked = []

        def cap_of(ba, month):
            asked.append((ba, month))
            return 1000.0, ["2030-05"]

        log = bs.build([held, gap, other], lambda ba: (frames[ba], f"raw/{ba}.xlsx"), cap_of, "2030-07-01T00:00:00Z")
        self.assertEqual(held["solar"], [0.0] * 4 + [0.25] * 4 + [0.5] * 4)
        for part in ("EIA-930", "ERCO", "raw/ERCO.xlsx", "1,000.0 MW", "2030-06", "EIA-860M", "2030-05", "not one roof's", "2030-07-01T00:00:00Z"):
            self.assertIn(part, held["solar_source"])
        self.assertNotIn("solar", gap)          # the older shape is removed, not kept
        self.assertNotIn("solar_source", gap)
        self.assertNotIn("solar", other)
        self.assertEqual(asked, [("ERCO", "2030-06"), ("CISO", "2030-06")])  # the level's own month
        self.assertEqual(len(log), 3)
        self.assertIn("no shape", log[1])
        self.assertIn("unavailable", log[1])
        self.assertIn("no balancing authority for the grid PJM", log[2])
        for was, now in zip(before, [held, gap, other]):
            for k in ("slug", "date", "grid", "ts_utc", "price", "title", "why"):
                self.assertEqual(was[k], now[k])

    def test_the_builder_reads_the_seller_tabs_shape(self):
        b = src("warehouse", "derived", "battery_solar.py")
        for call in ("mr.workbook_of(ba)", "mr.fuel_hours(path)", "mr.read_gens()", 'mr.capacity(gens, ba, "SUN", month)'):
            self.assertIn(call, b)
        self.assertIn('GRID_BA = {"ERCOT": "ERCO", "CAISO": "CISO"}', b)
        self.assertIn("--dry-run", b)
        self.assertIn("--data-root", b)


class Levels(unittest.TestCase):
    def test_a_shape_in_the_levels_file_is_whole(self):
        with open(os.path.join(SITE, "data", "battery_levels.json"), encoding="utf-8") as f:
            levels = json.load(f)["levels"]
        self.assertEqual(len(levels), 7)
        for lv in levels:
            if "solar" not in lv:
                self.assertNotIn("solar_source", lv)
                continue
            s = lv["solar"]
            self.assertEqual(len(s), len(lv["price"]), lv["date"])
            self.assertTrue(all(isinstance(v, (int, float)) and math.isfinite(v) for v in s), lv["date"])
            hours = {}
            for ts, v in zip(lv["ts_utc"], s):
                hours.setdefault(ts[:13], set()).add(v)
            self.assertTrue(all(len(v) == 1 for v in hours.values()), f"{lv['date']}: an hour with two values")
            self.assertIn("EIA-930", lv["solar_source"])
            self.assertIn("EIA-860M", lv["solar_source"])


class Migration(unittest.TestCase):
    def setUp(self):
        self.sql = src("warehouse", "supabase", "migrations", "019_game_v4.sql")
        self.checks = re.findall(r"check \(preset ~ '([^']+)'\)", self.sql)

    def test_both_tables_take_the_same_check(self):
        self.assertEqual(len(self.checks), 2)
        self.assertEqual(self.checks[0], self.checks[1])
        for t in ("game_scores", "game_plays"):
            self.assertIn(f"alter table public.{t} drop constraint if exists {t}_preset_check;", self.sql)
            self.assertIn(f"alter table public.{t} add constraint {t}_preset_check", self.sql)

    def test_constraints_only(self):
        body = "\n".join(ln for ln in self.sql.splitlines() if not ln.startswith("--")).lower()
        for word in ("create table", "add column", "drop table", "grant ", "revoke ", "insert ", "update ", "delete "):
            self.assertNotIn(word, body)
        self.assertIn("NOT applied", self.sql)

    def test_what_the_check_takes_and_refuses(self):
        rx = re.compile(self.checks[0])
        for ok in ("normal:13.5-5-90-v4", "easy:20-10-92-v4", "hard:13.5-5-90-r20-d0.11-v4", "hard:13.5-5-90-r20-d0.11-solar-v4",
                   "hard:5-2.5-85-r30-d0.2-solar-v4", "hard:13.5-5-90-r20-d0.11-solar-wind-v4",  # a later add-on needs no new migration
                   "normal:13.5-5-90-v3", "hard:13.5-5-90-r20-d0.11-v3", "normal:13.5-5-90", "hard:13.5-5-90-r20-d0.11"):
            self.assertRegex(ok, rx)
        for bad in ("normal:13.5-5-90-v5", "normal:13.5-5-90-v4-v4", "normal:13.5-5-90-v3-v4", "hard:13.5-5-90-r20-d0.11-solar-v3",
                    "hard:13.5-5-90-r20-d0.11-solar", "hard:13.5-5-90-r20-d0.11-Solar-v4", "hard:13.5-5-90-r20-d0.11-sol4r-v4",
                    "insane:13.5-5-90-v4", "normal:13.5-5-90-v4 ", "normal:13.5-5-90--v4"):
            self.assertNotRegex(bad, rx)


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class Node(unittest.TestCase):
    def test_the_servers_scorer_agrees_with_the_library(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "scripts/check-scorer.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertIn("the server's scorer and lib/battery.ts agree under v4", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        for label in ("easy, the perfect plan", "normal, the perfect plan", "hard, the perfect plan", "hard, custom battery, the perfect plan", "toy hard with rooftop solar, the perfect plan",
                      "the server's score carries the lights-out charge"):
            self.assertIn(label, r.stdout)

    def test_the_v4_rules(self):
        r = subprocess.run(["node", "scripts/test-battery.mjs"], cwd=SITE, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertNotIn("FAIL", r.stdout)
        for label in ("ok   hard, default battery, rooftop solar, shape", "ok   hard, default battery, rooftop solar, flat", "ok   hard, 5 kWh, 2.5 kW, 85 percent, reserve 30, wear 0.20, rooftop solar, spike",
                      "ok   Part A: at ", "ok   Part A: LIGHTS_OUT.multiple is ", "ok   Part B: ", "ok   Part B: Game.tsx prints no played price outside the library's labeled text",
                      "ok   Part C: ", "ok   lights out costs money", "ok   every preset the game writes round trips", "ok   parsePreset(a v3 board) is readable", "ok   parsePreset(a v2 board) is readable"):
            self.assertIn(label, r.stdout)
        m = re.search(r"LIGHTS_OUT\.multiple is (\d+), the smallest whole multiple that achieves it \((\d+)\)", r.stdout)
        self.assertEqual(m.group(1), m.group(2))
        # the multiple the test found is the one the library holds and the method states
        self.assertIn(f"export const LIGHTS_OUT = {{ multiple: {m.group(1)} }};", src("site", "lib", "battery.ts"))
        self.assertIn(f"**{m.group(1)} times the price cap**", src("docs", "methods", "battery_game.md"))
        # no famous day ends in lights out under v4, on Hard or on Normal
        table = [ln for ln in r.stdout.splitlines() if ln.startswith("  v4, ")]
        self.assertEqual(len(table), 7)
        self.assertFalse([ln for ln in table if "lights_out" in ln])


class Words(unittest.TestCase):
    def test_the_library(self):
        b = src("site", "lib", "battery.ts")
        self.assertIn('export const RULES_VERSION = "v4";', b)
        self.assertIn('export const SPIKE_LABEL = "game rule, not a real price";', b)
        self.assertIn("export const SOLAR = { kw: 5 };", b)
        self.assertIn('throw new Error("rooftop solar: no solar shape for this day")', b)

    def test_the_page_says_the_rules(self):
        page = src("site", "app", "play", "battery", "page.tsx")
        self.assertIn("The game's rules (version 4)", page)
        self.assertIn("Lights out costs money (a game rule)", page)
        self.assertIn("a home without power in a grid emergency is the outcome the battery exists to prevent", page)
        self.assertIn("{LIGHTS_OUT.multiple} times the price cap", page)
        self.assertIn("not one roof&apos;s", page)
        self.assertIn("nothing is filled in", page)
        game = src("site", "app", "play", "battery", "Game.tsx")
        self.assertIn("function EndLines(", game)
        self.assertIn("<EndLines level={level} rules={result.rules} mine={result.mine} perfect={perfect} big />", game)          # the simple page
        self.assertIn("<EndLines level={level} rules={result.rules} mine={result.mine} perfect={perfect} big={false} />", game)  # the full game
        self.assertIn("The hour you lost the most was", game)
        self.assertIn("worstHour(level.price, mine, perfect, rules)", game)
        self.assertIn("Add-ons", game)
        self.assertIn("Not available for {level.date}: the warehouse holds no solar shape for this day, and the game never fills one in.", game)
        self.assertIn("A home without power in a grid emergency is the outcome the battery exists to prevent.", game)
        self.assertIn("addons: result.addons", game)   # the posted score carries the add-ons
        self.assertIn("settings, difficulty, addons })", game)

    def test_the_method(self):
        m = src("docs", "methods", "battery_game.md")
        self.assertIn("## Version 4 (session 66)", m)
        for part in ("game rule, not a real price", "Winter Storm Uri", "EIA-930", "EIA-860M", "warehouse/derived/battery_solar.py", "019_game_v4.sql",
                     "hard:13.5-5-90-r20-d0.11-solar-v4", "not one roof", "(v3 rules)"):
            self.assertIn(part, m)

    def test_no_em_dash(self):
        for p in (("site", "lib", "battery.ts"), ("site", "lib", "game.ts"), ("site", "lib", "levels.ts"), ("site", "app", "play", "battery", "Game.tsx"),
                  ("site", "app", "play", "battery", "page.tsx"), ("site", "app", "api", "play", "finish", "route.ts"), ("site", "app", "api", "play", "score", "route.ts"),
                  ("site", "app", "api", "play", "top", "route.ts"), ("site", "scripts", "test-battery.mjs"), ("site", "scripts", "check-scorer.mjs"),
                  ("site", "scripts", "alias-loader.mjs"), ("site", "scripts", "check-lights.mjs"), ("site", "scripts", "alias-register.mjs"), ("site", "scripts", "play-battery.mjs"),
                  ("warehouse", "derived", "battery_solar.py"), ("warehouse", "supabase", "migrations", "019_game_v4.sql"),
                  ("docs", "methods", "battery_game.md"), ("tests", "test_session66.py")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
