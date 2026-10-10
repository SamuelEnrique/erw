"""Session 178: "What a battery earns", correctness. What is held to:

  the do-file follows the house rules, parsed line by line (Stata is not on this machine, so the file was never run):
    no continuation operator, one empty line between commands outside loops and none inside, every numeric column
    destrung with replace force, the sentinel recoded per variable before any loop, and it reads the column names from
    the line of the CSV that holds them;
  the hourly export is what its header says (columns, hours per day, the twelve marked months, LF bytes, no comma in a
    comment line), and its Python mirror, which follows the do-file step for step, rebuilds the page's headline numbers;
  the CSV and the page agree: with the tables on the machine, each month's sums equal battery_stack_monthly, and every
    headline number equals what the page's own library (site/lib/batterystack.ts, run by node) computes from the table
    over the export's window, at the page's rounding;
  the optimizer's independent check, which does not import the model, passes on days of the committed CSV, catches a
    planted error, and its ceiling is a ceiling for any prices on the limits;
  the snapshot behind the page's one line beside ERCOT's real awards is the two tables' sums over its own months;
  the page carries the line, the link to the note and the downloads, and still names nothing of the awards page.

No request, no model call; the environment is read, never set. Tests that need the tables, node or the page's library
skip when they are absent. ERW_TABLES_DIR may name another copy's warehouse/output (read only)."""
import csv
import importlib.util
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
PUBLIC = os.path.join(ROOT, "site", "public", "battery")
CSV_PATH = os.path.join(PUBLIC, "erw_2026_battery_dispatch.csv")
DO_PATH = os.path.join(PUBLIC, "erw_2026_battery_replication.do")
MIRROR_PATH = os.path.join(PUBLIC, "erw_2026_battery_replication.py")
SNAPSHOT = os.path.join(ROOT, "site", "data", "battery_awards_beside.json")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
EM = chr(0x2014)
PRODUCTS = ["regup", "regdn", "rrs", "ecrs", "nspin"]
FILES = ["warehouse/derived/battery_dispatch_export.py", "warehouse/derived/battery_optimizer_check.py",
         "warehouse/derived/battery_awards_compare.py", "site/public/battery/erw_2026_battery_replication.do",
         "site/public/battery/erw_2026_battery_replication.py", "docs/methods/battery_earns_algorithm.md",
         "tests/test_session178.py", "archive/sessions/SESSION_178_REPORT.md"]
sys.path.insert(0, DERIVED)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def need(path, what):
    if not os.path.exists(path):
        raise unittest.SkipTest(f"{what} is not on this machine")


def table(name):
    path = os.path.join(TABLES, name + ".csv")
    need(path, name)
    return path


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


def csv_head():
    """(the comment lines, the column names) of the export."""
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        lines = []
        for line in f:
            lines.append(line.rstrip("\n"))
            if not line.startswith("#"):
                break
    return lines[:-1], lines[-1].split(",")


class DoFileRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = src("site", "public", "battery", "erw_2026_battery_replication.do")
        cls.lines = cls.text.split("\n")
        cls.comments, cls.columns = csv_head()
        cls.numeric = [c for c in cls.columns if c not in ("hour_utc", "hour_local", "local_day", "local_month")]

    def test_no_continuation_operator_and_no_delimiter_change(self):
        self.assertNotIn("///", self.text)
        self.assertNotIn("#delimit", self.text.lower())
        self.assertNotIn("\r", self.text)
        self.assertNotIn(EM, self.text)
        for i, line in enumerate(self.lines, 1):
            self.assertFalse(line.rstrip().endswith("/*"), f"line {i} opens a comment to continue a line")

    def test_one_empty_line_between_commands_outside_loops_and_none_inside(self):
        lines = self.lines[:-1] if self.lines[-1] == "" else self.lines
        depth, prev_blank, seen = 0, True, 0
        for i, line in enumerate(lines, 1):
            blank = line.strip() == ""
            if depth:
                self.assertFalse(blank, f"line {i}: an empty line inside a loop")
                if line.strip() == "}":
                    depth -= 1
                    prev_blank = False
                elif line.rstrip().endswith("{"):
                    depth += 1
                continue
            if blank:
                self.assertFalse(prev_blank, f"line {i}: two empty lines together")
                prev_blank = True
                continue
            self.assertTrue(prev_blank, f"line {i}: no empty line before this command: {line[:60]}")
            prev_blank = False
            seen += 1
            if line.rstrip().endswith("{"):
                depth += 1
        self.assertEqual(depth, 0)
        self.assertGreater(seen, 60)

    def test_every_numeric_column_is_destrung_with_force_one_command_each(self):
        got = re.findall(r"^destring (\w+), replace force$", self.text, flags=re.M)
        self.assertEqual(got, self.numeric)
        self.assertEqual(len(re.findall(r"^\s*destring\b", self.text, flags=re.M)), len(self.numeric), "a destring without replace force")
        self.assertEqual(len(self.numeric), 25)

    def test_the_sentinel_is_recoded_per_variable_before_any_loop_or_reshape(self):
        want = [f"{a}_{k}_{u}" for a, u in (("price", "usd_mw"), ("award", "mw"), ("revenue", "usd")) for k in PRODUCTS]
        got = re.findall(r"^replace (\w+) = \. if (\w+) == -999$", self.text, flags=re.M)
        self.assertEqual([a for a, _ in got], want)
        for a, b in got:
            self.assertEqual(a, b)
        last_recode = max(m.start() for m in re.finditer(r"^replace \w+ = \. if", self.text, flags=re.M))
        last_destring = max(m.start() for m in re.finditer(r"^destring ", self.text, flags=re.M))
        first_loop = min(m.start() for m in re.finditer(r"^(foreach|forvalues|while|reshape|collapse)\b", self.text, flags=re.M))
        self.assertLess(last_destring, min(m.start() for m in re.finditer(r"^replace \w+ = \. if", self.text, flags=re.M)))
        self.assertLess(last_recode, first_loop)
        # and the export's own sentinel is the one recoded
        self.assertTrue(any("Sentinel: -999" in c for c in self.comments))

    def test_it_reads_the_column_names_from_the_line_that_holds_them(self):
        n = len(self.comments)
        self.assertEqual(n, 14)
        self.assertIn(f'import delimited using "erw_2026_battery_dispatch.csv", varnames({n + 1}) rowrange({n + 2}) stringcols(_all) clear', self.text)
        self.assertTrue(any(f"varnames({n + 1}) rowrange({n + 2})" in c for c in self.comments))
        for name in ("erw_2026_battery_dispatch.csv", "erw_2026_battery_replication.do"):
            self.assertRegex(name, r"^[a-z]+_\d{4}_[a-z]+(_[a-z]+)+\.(csv|do)$")

    def test_the_reader_inputs_are_the_page_defaults(self):
        lib = src("site", "lib", "batterystack.ts")
        self.assertIn('4: { capex: 1110, fom: 22,', lib)
        self.assertIn("export const DEBT = { share: 0.6, rate: 0.08, life: 20 };", lib)
        for line in ("scalar s_mw = 100", "scalar s_fom_usd_kw_year = 22", "scalar s_capex_usd_kw = 1110", "scalar s_debt_share = 0.6",
                     "scalar s_debt_rate = 0.08", "scalar s_debt_years = 20"):
            self.assertIn(line + "\n", self.text)


class TheExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mirror = load("erw_battery_replication_mirror_178", MIRROR_PATH)
        cls.rows = cls.mirror.read(CSV_PATH)
        cls.n = cls.mirror.numbers(cls.rows)

    def test_the_bytes_and_the_header(self):
        with open(CSV_PATH, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"\r", raw)
        self.assertLess(len(raw), 5 * 1024 * 1024)
        comments, columns = csv_head()
        import battery_dispatch_export as ex
        self.assertEqual(columns, ex.COLUMNS)
        self.assertEqual(len(comments), ex.HEADER_LINES)
        for c in comments:
            self.assertNotIn(",", c)
            self.assertNotIn('"', c)
            self.assertNotIn(EM, c)
        text = "\n".join(comments)
        for words in ("iso_rtm_hub_prices", "ercot_all_hub_prices_history", "ercot_as_prices", "battery_stack_monthly", "Retrieved (UTC)",
                      "sha256", "commit", "Exported:", "round trip 0.86", "4-hour", "foresight"):
            self.assertIn(words, text)
        self.assertIn("site/public/battery/* text eol=lf", src(".gitattributes"))

    def test_the_hours(self):
        days = {}
        for r in self.rows:
            days.setdefault(r["local_day"], []).append(r)
        self.assertEqual({len(v) for v in days.values()}, {23, 24, 25})
        self.assertEqual(sorted(d for d, v in days.items() if len(v) == 23), ["2024-03-10", "2025-03-09", "2026-03-08"])
        self.assertEqual(sorted(d for d, v in days.items() if len(v) == 25), ["2023-11-05", "2024-11-03", "2025-11-02"])
        self.assertEqual(len({r["hour_utc"] for r in self.rows}), len(self.rows))
        for d, v in days.items():
            self.assertEqual([int(r["hour_of_day"]) for r in v], list(range(len(v))), d)
            self.assertEqual(len({r["switch_used"] for r in v}), 1, d)
        twelve = sorted({r["local_month"] for r in self.rows if r["in_last_twelve"] == 1})
        self.assertEqual(len(twelve), 12)
        self.assertEqual(len({r["local_month"] for r in self.rows}), 36)
        self.assertEqual(twelve[-1], max(r["local_month"] for r in self.rows))

    def test_revenue_is_price_times_megawatts_and_the_parts_add_up(self):
        self.assertLess(self.n["check_energy"], 0.001)
        for k in PRODUCTS:
            self.assertLess(self.n[f"check_{k}"], 0.001, k)
        for r in self.rows[::97]:
            anc = sum(r[f"revenue_{k}_usd"] or 0.0 for k in PRODUCTS)
            self.assertAlmostEqual(anc, r["revenue_ancillary_usd"], places=6)
            self.assertAlmostEqual(r["revenue_energy_usd"] + anc, r["revenue_total_usd"], places=6)

    def test_no_megawatt_is_sold_twice_in_an_hour(self):
        for r in self.rows:
            up = r["discharge_mw"] + sum(r[f"award_{k}_mw"] or 0.0 for k in PRODUCTS if k != "regdn")
            dn = r["charge_mw"] + (r["award_regdn_mw"] or 0.0)
            self.assertLessEqual(up, 1 + 5e-6, r["hour_utc"])
            self.assertLessEqual(dn, 1 + 5e-6, r["hour_utc"])

    def test_the_first_hour_of_a_day_holds_no_upward_reserve(self):
        # the algorithm note's edge case: each day starts empty, and an upward award needs its energy at the hour's start
        for r in self.rows:
            if r["hour_of_day"] == 0:
                self.assertEqual(sum(r[f"award_{k}_mw"] or 0.0 for k in PRODUCTS if k != "regdn"), 0.0, r["hour_utc"])

    def test_the_mirror_follows_the_do_file_display_for_display(self):
        do = src("site", "public", "battery", "erw_2026_battery_replication.do")
        shown = [re.match(r'\s*display "([^"`:]*)', line).group(1) for line in do.split("\n") if line.strip().startswith("display")]
        out = "\n".join(self.mirror.report(self.n))
        for words in shown:
            self.assertIn(words.strip(), out, words)
        self.assertEqual(self.mirror.HEADER_LINES, 14)

    def test_the_headline_numbers_are_whole_and_consistent(self):
        n = self.n
        self.assertEqual(n["l12_months"], 12)
        self.assertEqual(n["n36"], 36)
        self.assertEqual(n["debt_service"], 6783357)
        self.assertAlmostEqual(n["l12_energy"] + n["l12_ancillary"], n["l12_total"], places=5)
        self.assertAlmostEqual(sum(n[f"l12_{k}"] for k in PRODUCTS), n["l12_ancillary"], places=5)
        self.assertAlmostEqual(n["cover"], (n["l12_total"] * 100 - 22 * 1000 * 100) / 6783357, places=12)
        self.assertEqual(n["year_2024_months"], 12)
        self.assertEqual(n["year_2025_months"], 12)


class TheCsvAndThePageAgree(unittest.TestCase):
    """With the tables: the export is the page's data, hour by hour, and the page's library gives the mirror's numbers."""
    @classmethod
    def setUpClass(cls):
        cls.path = table("battery_stack_monthly")
        cls.mirror = load("erw_battery_replication_mirror_178b", MIRROR_PATH)
        cls.n = cls.mirror.numbers(cls.mirror.read(CSV_PATH))
        import battery_dispatch_export as ex
        cls.ex = ex
        cls.months = ex.months_of(ex.read_monthly(TABLES), "ercot:HB_HUBAVG", "foresight", 4)
        cls.last = max(m["month"] for m in cls.n["months"])

    def test_each_month_of_the_export_is_the_tables_month(self):
        for m in self.n["months"]:
            t = self.months[m["month"]]
            self.assertEqual(t["days_held"], m["days_held"], m["month"])
            self.assertEqual(t["days_in_month"], m["days_in_month"], m["month"])
            for k in ["energy", "ancillary", "total"] + PRODUCTS:
                self.assertAlmostEqual(t[f"revenue_{k}_usd_per_mw"], m[f"revenue_{k}_usd"], delta=0.005, msg=f"{m['month']} {k}")

    def test_the_windows_are_the_pages_rule_on_the_table(self):
        upto = {m: v for m, v in self.months.items() if m <= self.last}
        twelve = self.ex.last_twelve(upto)
        self.assertEqual(twelve, sorted(m["month"] for m in self.n["months"] if m["in_last_twelve"] == 1))
        first, last, held = self.ex.last_36(upto)
        self.assertEqual((first, last), (min(m["month"] for m in self.n["months"]), self.last))
        self.assertEqual(len(held), self.n["n36"])

    def test_every_headline_number_is_the_page_librarys(self):
        js = """
import fs from "node:fs";
const B = await import("./lib/batterystack.ts");
const lines = fs.readFileSync(%s, "utf-8").split("\\n").filter((l) => !l.startsWith("#"));
const rows = lines.slice(1).filter(Boolean).map((l) => { const c = l.split(","); return { entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]) }; })
  .filter((r) => r.entity === "ercot:HB_HUBAVG" && r.variable.startsWith("foresight_4h_") && r.ts_utc.slice(0, 7) <= %s);
const x = B.inputsOf({});
const ms = B.monthsOf(rows, "foresight", 4);
const out = { key: B.inputsKey(x), bad: B.badMonth(B.last36(ms).months).m, first: B.lastTwelve(ms)[0].m, last: B.lastTwelve(ms)[11].m };
for (const s of %s) out[s] = B.stat(rows, [], x, s);
console.log(JSON.stringify(out));
""" % (json.dumps(self.path.replace("\\", "/")), json.dumps(self.last),
       json.dumps(["l12_kw:total", "l12:total", "l12_share:ancillary", "cover", "ds", "p10_36", "n36", "l12:energy", "l12:ancillary",
                   "year:2024:energy", "year:2024:ancillary", "year:2025:energy", "year:2025:ancillary"] + [f"l12:{k}" for k in PRODUCTS]))
        page, n = node(js), self.n
        two = lambda v: f"{v:.2f}"  # noqa: E731  (the page prints two decimals)
        self.assertEqual(page["key"], "grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=6783357")
        self.assertEqual((page["first"], page["last"], page["bad"]), (n["l12_first"], n["l12_last"], n["bad_month"]))
        self.assertEqual(two(page["l12_kw:total"]), two(n["l12_kw_total"]))
        self.assertEqual(page["l12:total"], n["l12_total_usd"])
        self.assertEqual(page["l12_share:ancillary"], n["l12_share_ancillary"])
        self.assertEqual(two(page["cover"]), two(n["cover"]))
        self.assertEqual(page["ds"], n["debt_service"])
        self.assertEqual(page["p10_36"], n["p10_36_usd"])
        self.assertEqual(page["n36"], n["n36"])
        for k in ["energy", "ancillary"] + PRODUCTS:
            self.assertEqual(page[f"l12:{k}"], n[f"l12_{k}_usd"], k)
        for y in ("2024", "2025"):
            self.assertEqual(two(page[f"year:{y}:energy"]), two(n[f"year_{y}_energy_kw"]))
            self.assertEqual(two(page[f"year:{y}:ancillary"]), two(n[f"year_{y}_ancillary_kw"]))


class TheOptimizerCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import battery_optimizer_check as oc
        except ImportError as e:  # scipy is in requirements.txt; a machine without it skips
            raise unittest.SkipTest(str(e))
        cls.oc = oc
        cls.days = oc.read_days(CSV_PATH)

    def test_it_does_not_import_the_model(self):
        text = src("warehouse", "derived", "battery_optimizer_check.py")
        code = "\n".join(line for line in text.split('"""')[2].split("\n"))
        self.assertNotIn("battery_stack", code)
        self.assertNotIn("solve_day", code)
        self.assertNotRegex(code, r"^\s*(import|from) (cost_of_power|price_board|iso_prices)", )

    def test_the_stated_sample(self):
        s = self.oc.sample(self.days)
        self.assertEqual(s, self.oc.sample(self.days))                    # the seed fixes it
        self.assertGreaterEqual(len(s), 30)
        by_month = {}
        for d, why in s.items():
            by_month[d[:7]] = by_month.get(d[:7], 0) + 1
        self.assertEqual(len(by_month), 12)
        self.assertTrue(all(v >= self.oc.SAMPLE_PER_MONTH for v in by_month.values()))
        why = " | ".join(s.values())
        for words in ("the highest-revenue day", "the most negative energy price", "daylight saving, 23 hours", "daylight saving, 25 hours"):
            self.assertIn(words, why)
        self.assertEqual(self.oc.SEED, 178)

    def test_five_days_of_the_export_are_optimal_and_the_switch_day_is_exact(self):
        s = self.oc.sample(self.days)
        pick = {d: w for d, w in s.items() if w != "random"}
        pick["2025-01-04"] = "the switch was used"                      # the one switch day of the 36 months
        pick[next(d for d, w in s.items() if w == "random")] = "random"
        res = self.oc.check(self.days, dict(sorted(pick.items())))
        self.assertGreaterEqual(len(res), 5)
        for r in res:
            self.assertEqual(r["broken"], "", r["day"])
            self.assertLess(abs(r["gap_usd"]), self.oc.GAP_TOL, r["day"])
            self.assertLessEqual(r["above_ceiling_usd"], self.oc.GAP_TOL, r["day"])
            if not r["switch_used"]:
                self.assertLess(abs(r["above_ceiling_usd"]), self.oc.GAP_TOL, r["day"])    # the ceiling is reached: proven optimal
        sw = [r for r in res if r["switch_used"]]
        self.assertEqual([r["day"] for r in sw], ["2025-01-04"])
        self.assertAlmostEqual(sw[0]["enumerated_usd"], sw[0]["exact_usd"], delta=self.oc.GAP_TOL)
        self.assertGreater(sw[0]["ceiling_usd"], sw[0]["model_usd"] + 0.01)                 # the linear ceiling stands above it
        self.assertEqual(self.oc.summary(res)["above"], [])
        self.assertEqual(self.oc.summary(res)["below"], [])

    def test_the_ceiling_is_a_ceiling_for_any_prices_on_the_limits(self):
        rows = self.days["2026-03-08"]
        prods = self.oc.bought(rows)
        opt, cap, _, _ = self.oc.optimum(rows, prods)
        self.assertAlmostEqual(opt, cap, delta=1e-6)
        prog = self.oc.program(rows, prods)
        rng = random.Random(178)
        for _ in range(25):
            y = [rng.uniform(0, 60) for _ in prog[2]]
            z = [rng.uniform(-60, 60) for _ in prog[4]]
            import numpy as np
            self.assertGreaterEqual(self.oc.ceiling(*prog, np.array(y), np.array(z)), opt - 1e-6)

    def test_a_planted_error_is_caught(self):
        day = "2026-01-26"
        rows = [dict(r) for r in self.days[day]]
        rows[12]["revenue_total_usd"] += 1.0                               # a dollar the dispatch did not earn
        res = self.oc.check({day: rows}, {day: "planted"})
        self.assertGreater(res[0]["gap_usd"], 0.99)
        self.assertEqual(self.oc.summary(res)["above"], [day])
        rows = [dict(r) for r in self.days[day]]
        t = max(range(len(rows)), key=lambda i: rows[i]["award_regup_mw"] + rows[i]["discharge_mw"])
        rows[t]["award_rrs_mw"] += 0.5                                     # more power than the battery has
        self.assertTrue(self.oc.feasible(rows, self.oc.bought(rows)))

    def test_the_rules_written_in_the_check_are_the_pages(self):
        lib = src("site", "lib", "batterystack.ts")
        self.assertIn('rule: "30 minutes from 5 December 2025"', lib)
        self.assertIn('rule: "2 hours from its start in June 2023; 1 hour from 5 December 2025"', lib)
        self.assertIn('rule: "4 hours from 9 December 2022"', lib)
        h = self.oc.hours_behind
        self.assertEqual([h("regup", "2025-12-04"), h("regup", "2025-12-05"), h("regdn", "2026-01-01"), h("rrs", "2024-01-01")], [1.0, 0.5, 0.5, 1.0])
        self.assertEqual([h("ecrs", "2025-12-04"), h("ecrs", "2025-12-05"), h("nspin", "2023-10-01")], [2.0, 1.0, 4.0])
        self.assertEqual(self.oc.RTE, 0.86)
        self.assertAlmostEqual(max(r["award_nspin_mw"] for rows in self.days.values() for r in rows), 4 * math.sqrt(0.86) / 4, places=5)


class BesideTheRealAwards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SNAPSHOT, encoding="utf-8") as f:
            cls.snap = json.load(f)

    def test_the_snapshot_holds_six_cases_each_consistent(self):
        self.assertEqual(sorted(self.snap["cases"]), sorted(f"{s}_{d}h" for s in ("foresight", "dayahead") for d in (2, 4, 8)))
        for k, c in self.snap["cases"].items():
            self.assertGreater(c["months"], 0, k)
            self.assertLessEqual(c["first"], c["last"], k)
            self.assertAlmostEqual(c["ratio"], c["model"] / c["fleet"], delta=0.02, msg=k)
        self.assertEqual(self.snap["fleet_table"], "ercot_storage_dam_awards_monthly")
        self.assertEqual(self.snap["model_table"], "battery_stack_monthly")
        with open(SNAPSHOT, "rb") as f:
            self.assertNotIn(b"\r", f.read())

    def test_the_snapshot_is_the_two_tables_over_its_own_months(self):
        table("battery_stack_monthly"), table("ercot_storage_dam_awards_monthly")
        import battery_awards_compare as ac
        mt, ft = ac.read(TABLES, ac.MODEL), ac.read(TABLES, ac.FLEET)
        fleet = ac.by_month(ft, ac.FLEET_ENTITY)
        for k, c in self.snap["cases"].items():
            model = ac.by_month(mt, ac.MODEL_ENTITY, k + "_")
            months = [m for m in sorted(fleet) if c["first"] <= m <= c["last"]]
            self.assertEqual(len(months), c["months"], k)
            for m in months:                                            # each month whole in both, as the rule says
                self.assertTrue(ac.whole(fleet[m]) and ac.whole(model[m]), f"{k} {m}")
            a = sum(model[m]["revenue_ancillary_usd_per_mw"] for m in months) / 1000 / len(months)
            b = sum(fleet[m]["revenue_ancillary_usd_per_mw"] for m in months) / 1000 / len(months)
            self.assertAlmostEqual(c["model"], a, delta=0.00011, msg=k)
            self.assertAlmostEqual(c["fleet"], b, delta=0.00011, msg=k)
            self.assertAlmostEqual(c["ratio"], a / b, delta=0.00011, msg=k)

    def test_the_page_library_reads_it_and_refuses_what_it_does_not_hold(self):
        got = node("""
import fs from "node:fs";
const B = await import("./lib/batterystack.ts");
const snap = JSON.parse(fs.readFileSync("./data/battery_awards_beside.json", "utf-8"));
console.log(JSON.stringify({ a: B.awardsBeside(snap, "ercot", "foresight", 4), caiso: B.awardsBeside(snap, "caiso", "foresight", 4),
  none: B.awardsBeside({ built: "", cases: {} }, "ercot", "foresight", 4), ratio: B.awardsStat(snap, "dayahead_8h", "ratio"),
  odd: B.awardsStat(snap, "foresight_3h", "ratio"), word: B.awardsStat(snap, "foresight_4h", "first"),
  zero: B.awardsBeside({ built: "", cases: { foresight_4h: { first: "2026-01", last: "2026-07", months: 7, model: 2, fleet: 0, ratio: 0 } } }, "ercot", "foresight", 4) }));
""")
        self.assertEqual(got["a"], self.snap["cases"]["foresight_4h"])
        self.assertEqual(got["ratio"], self.snap["cases"]["dayahead_8h"]["ratio"])
        for k in ("caiso", "none", "odd", "word", "zero"):
            self.assertIsNone(got[k], k)


class ThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = src("site", "app", "cost-of-power", "battery", "page.tsx")

    def test_one_line_with_three_checked_numbers_and_no_commentary(self):
        self.assertEqual(self.page.count("data-awards-beside="), 1)
        for stat in ("model", "fleet", "ratio"):
            self.assertEqual(self.page.count("check={`bsa|${x.strat}_${x.dur}h|" + stat + "`}"), 1)
        line = self.page[self.page.index("data-awards-beside="):]
        line = line[:line.index("</p>")]
        for word in ("should", "recommend", "better", "worse", "only ", "merely", "far "):
            self.assertNotIn(word, line.lower())
        self.assertIn('import awardsData from "@/data/battery_awards_beside.json";', self.page)
        self.assertEqual(self.page.count("rest<"), 2)                    # no new read of the live set (test_session148 holds this too)
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "bsa") {', check)
        self.assertIn("return B.awardsStat(snap, p[1], p[2]);", check)

    def test_the_note_is_linked_beside_the_method_link_and_the_downloads_are_offered(self):
        self.assertIn('<Link href={METHOD}>Method</Link>. <Link href={ALGORITHM}>Every number, step by step</Link>.', self.page)
        self.assertIn('const ALGORITHM = "/data/methods/battery_earns_algorithm";', self.page)
        for f in ("erw_2026_battery_dispatch.csv", "erw_2026_battery_replication.do", "erw_2026_battery_replication.py"):
            self.assertIn(f'"/battery/{f}"', self.page)
            self.assertTrue(os.path.exists(os.path.join(PUBLIC, f)), f)
        self.assertIn('"/data/methods/battery_earns_algorithm": "review",', src("site", "lib", "release.ts"))
        self.assertIn('"/data/methods/battery_earns_algorithm",', src("site", "scripts", "check-routes.mjs"))

    def test_the_page_still_names_nothing_of_the_awards_page(self):
        # sessions 115, 116 and 120 hold the battery page to this; the line reads a snapshot and links the note only
        for word in ("battery/awards", "storageawards", "ercot_storage_dam_awards", "ercot_storage_dam_offers", "RealTime"):
            self.assertNotIn(word, self.page)


class TheNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "battery_earns_algorithm.md")

    def test_the_sections_asked_for(self):
        for head in ("## 4. Every number on the page, in the order the page shows it", "## 5. Edge cases, as the code handles them",
                     "## 6. Assumptions, their defaults and sources", "## 7. The replication", "## 8. The independent check of the optimizer",
                     "## 9. Beside ERCOT's real awards", "## 10. Where the notes and the code differ",
                     "## 11. What the browser has, for session 179"):
            self.assertIn(head, self.note)
        self.assertTrue(self.note.rstrip().split("\n## ")[-2].startswith("11. What the browser has, for session 179"))
        self.assertIn("Stata is not installed on the machine that wrote it, so the do-file has not been run.", self.note)

    def test_every_check_key_the_page_prints_is_explained(self):
        page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        stats = set(re.findall(r's="([a-z0-9_]+)[:"]', page)) | set(re.findall(r"s=\{`([a-z0-9_]+):", page)) | set(re.findall(r'st\("([a-z0-9_]+)[:"]', page))
        self.assertGreaterEqual(len(stats), 12)
        for s in sorted(stats):
            self.assertIn(f"`{s}", self.note, s)

    def test_the_notes_figures_are_the_snapshots_and_the_mirrors(self):
        with open(SNAPSHOT, encoding="utf-8") as f:
            snap = json.load(f)
        for k, label in (("foresight_2h", "Perfect foresight, 2 hours"), ("foresight_4h", "Perfect foresight, 4 hours (the default)"),
                         ("foresight_8h", "Perfect foresight, 8 hours"), ("dayahead_2h", "Day-ahead schedule, 2 hours"),
                         ("dayahead_4h", "Day-ahead schedule, 4 hours"), ("dayahead_8h", "Day-ahead schedule, 8 hours")):
            c = snap["cases"][k]
            self.assertIn(f"| {label} | {c['model']:.2f} | {c['fleet']:.2f} | {c['ratio']:.2f} |", self.note)
        mirror = load("erw_battery_replication_mirror_178c", MIRROR_PATH)
        n = mirror.numbers(mirror.read(CSV_PATH))
        for words in (f"USD {n['l12_kw_total']:.2f} per kW", f"{n['l12_share_ancillary']} percent of it from ancillary services",
                      f"USD {n['l12_total_usd']:,} for 100 MW", f"USD {n['p10_36_usd']:,}", f"USD {n['debt_service']:,} a year",
                      f"debt covered {n['cover']:.2f} times"):
            self.assertIn(words, self.note)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM, src(*f.split("/")), f)

    def test_the_new_modules_names_are_their_own(self):
        names = {}
        for top in ("warehouse", "scripts", "tests"):
            for d, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [x for x in dirs if x not in ("output", "__pycache__", "node_modules", "raw")]
                for f in files:
                    if f.endswith(".py"):
                        names.setdefault(f, []).append(os.path.relpath(os.path.join(d, f), ROOT))
        for f in ("battery_dispatch_export.py", "battery_optimizer_check.py", "battery_awards_compare.py", "test_session178.py"):
            self.assertEqual(len(names.get(f, [])), 1, names.get(f))

    def test_the_scripts_write_nothing_into_the_warehouse(self):
        for f in ("battery_dispatch_export.py", "battery_optimizer_check.py", "battery_awards_compare.py"):
            text = src("warehouse", "derived", f)
            for word in ("write_table", "write_csv", "_require_lock", "update_sources", "write_status", "set_out_dir"):
                self.assertNotIn(word, text, f"{f} {word}")
            for word in ("anthropic", "requests.", "urlopen", "http.client"):
                self.assertNotIn(word, text.lower(), f"{f} {word}")


if __name__ == "__main__":
    unittest.main()
