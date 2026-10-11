"""Session 190: "What a datacenter pays" (/cost-of-power), the replication of the default case (ERCOT, the North load
zone, a flat load of 100 MW, bought in real time). What is held to:

  the do-file follows the house rules, parsed line by line (Stata is not on this machine, so the file was never run):
    no continuation operator, one empty line between commands outside loops and none inside, every numeric column
    destrung with replace force, the sentinel recoded per variable before any loop or collapse, every real-valued
    variable made as a double, and it reads the column names from the line of the CSV that holds them;
  the hourly export is what its header says (columns, an unbroken run of hours, the month of each hour in Central
    standard time, the twelve marked months, the sentinel, LF bytes, no comma in a comment line);
  the CSV and the page's own files agree, hour by hour and month by month: by the exporter's own check, which also
    catches a planted error. This is the alarm: when the page's files gain or change an hour of the default case the
    CSV must be exported again (python warehouse/derived/datacenter_hourly_export.py; no table, no lock);
  the Python mirror, which follows the do-file step for step, rebuilds the page's headline numbers. The page's numbers
    are computed two ways and the mirror is held to both: in Python from the page's files (the exporter's port of
    site/lib/datacenter.ts), always; and by node on site/lib/datacenter.ts itself (skipped where node is absent);
  the flexible load a second time: the rule and the load "if perfectly foreseen", written again in Python from
    docs/methods/datacenter_pays_algorithm.md section 5, on the CSV's two price columns alone, beside node on the
    page's library, for eight loads (skipped where node is absent);
  where the price tables are on the machine (ERW_TABLES_DIR or ERW_TABLES names another copy's warehouse/output, read
    only; else this copy's), every hour of the CSV against them. Skipped on a machine without them, as GitHub's runner.

No figure is pinned here but under the window it was written for: the data machine's run exports the CSV again when
the page's files move, and what is held is that the CSV, the mirror, the page's files and the page's library agree.
No request, no model call. The environment is read, never set."""
import calendar
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
PUBLIC = os.path.join(ROOT, "site", "public", "datacenter")
CSV_NAME, DO_NAME, MIRROR_NAME = "erw_2026_datacenter_hourly.csv", "erw_2026_datacenter_replication.do", "erw_2026_datacenter_replication.py"
CSV_PATH, DO_PATH, MIRROR_PATH = (os.path.join(PUBLIC, f) for f in (CSV_NAME, DO_NAME, MIRROR_NAME))
TABLES = os.environ.get("ERW_TABLES_DIR") or os.environ.get("ERW_TABLES") or os.path.join(ROOT, "warehouse", "output")
EM = chr(0x2014)
COLUMNS = ["hour_utc", "std_month", "rt_usd_mwh", "da_usd_mwh", "hub_rt_usd_mwh", "in_last_twelve"]
TEXT_COLUMNS = ["hour_utc", "std_month"]
PRICE_COLUMNS = ["rt_usd_mwh", "da_usd_mwh", "hub_rt_usd_mwh"]
HEADER_LINES, SENTINEL = 15, -99999
DOUBLES = ["rt_usd_per_mw", "da_usd_per_mw", "hub_usd_per_mw", "rt_usd_mwh_month", "year_usd_per_mw", "year_hours"]
FILES = ["warehouse/derived/datacenter_hourly_export.py", f"site/public/datacenter/{DO_NAME}", f"site/public/datacenter/{MIRROR_NAME}",
         f"site/public/datacenter/{CSV_NAME}", "tests/test_session190_replication.py", "site/scripts/check-datacenter-face.mjs"]
MW, GPU_KW, PUE = 100, 1.3, 1.56
# the window this session wrote its figures for; a figure is pinned only while the page's files still stand on it
WINDOW = ("2025-10", "2026-09")
_KEPT = {}


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def load(name, path):
    """A module from its file, with no bytecode written beside it: the mirror sits in site/public, which the site serves."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    kept = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = kept
    return mod


def exporter():
    if "ex" not in _KEPT:
        _KEPT["ex"] = load("datacenter_hourly_export_190", os.path.join(DERIVED, "datacenter_hourly_export.py"))
    return _KEPT["ex"]


def facts():
    if "facts" not in _KEPT:
        _KEPT["facts"] = exporter().page_facts()
    return _KEPT["facts"]


def csv_text():
    """(the comment lines, the column names, the data lines) of the export, read once."""
    if "csv" not in _KEPT:
        with open(CSV_PATH, encoding="utf-8", newline="") as f:
            lines = f.read().split("\n")
        n = next(i for i, line in enumerate(lines) if not line.startswith("#"))
        _KEPT["csv"] = (lines[:n], lines[n].split(","), [line for line in lines[n + 1:] if line])
    return _KEPT["csv"]


def mirror_numbers():
    if "mirror" not in _KEPT:
        mirror = load("erw_datacenter_replication_mirror_190", MIRROR_PATH)
        _KEPT["mirror"] = (mirror, mirror.numbers(mirror.read(CSV_PATH)))
    return _KEPT["mirror"]


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"),
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


def prev_month(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def js_round(v):
    """JavaScript's Math.round: a half goes up."""
    return math.floor(v + 0.5)


def js_two(v):
    """The page's two(): two decimals. (Python formats the same double; a tie at the third decimal is not met here.)"""
    return f"{v:,.2f}"


def js_short(v):
    """The page's usdShort()."""
    t = lambda x: f"{x:,.2f}".rstrip("0").rstrip(".")  # noqa: E731
    if abs(v) >= 1e9:
        return f"{t(v / 1e9)} billion"
    if abs(v) >= 1e6:
        return f"{t(v / 1e6)} million"
    return f"{js_round(v):,}"


def on_the_window():
    return tuple(facts()["l12"][i] for i in (0, -1)) == WINDOW


class DoFileRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = src("site", "public", "datacenter", DO_NAME)
        cls.lines = cls.text.split("\n")
        cls.comments, cls.columns, _ = csv_text()
        cls.numeric = [c for c in cls.columns if c not in TEXT_COLUMNS]

    def test_no_continuation_operator_and_no_delimiter_change(self):
        self.assertNotIn("///", self.text)
        self.assertNotIn("#delimit", self.text.lower())
        self.assertNotIn("\r", self.text)
        self.assertNotIn(EM, self.text)
        for i, line in enumerate(self.lines, 1):
            self.assertFalse(line.rstrip().endswith("/*"), f"line {i} opens a comment to continue a line")

    def test_one_empty_line_between_commands_outside_loops_and_none_inside(self):
        lines = self.lines[:-1] if self.lines[-1] == "" else self.lines
        depth, prev_blank, seen, loops = 0, True, 0, 0
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
                loops += 1
        self.assertEqual(depth, 0)
        self.assertGreater(seen, 80)
        self.assertEqual(loops, 2)                                       # so the rule for the inside of a loop is exercised
        self.assertFalse(lines[-1].strip() == "", "the file ends with two empty lines")

    def test_every_numeric_column_is_destrung_with_force_one_command_each(self):
        got = re.findall(r"^destring (\w+), replace force$", self.text, flags=re.M)
        self.assertEqual(got, self.numeric)
        self.assertEqual(len(re.findall(r"^\s*destring\b", self.text, flags=re.M)), len(self.numeric), "a destring without replace force")
        self.assertEqual(self.numeric, PRICE_COLUMNS + ["in_last_twelve"])
        for c in TEXT_COLUMNS:                                            # the two text columns are read as text and never destrung
            self.assertNotRegex(self.text, rf"destring {c}\b")

    def test_the_sentinel_is_recoded_per_variable_before_any_loop_or_collapse(self):
        got = re.findall(r"^replace (\w+) = \. if (\w+) == (-\d+)$", self.text, flags=re.M)
        self.assertEqual(got, [(c, c, str(SENTINEL)) for c in PRICE_COLUMNS])      # one command a variable, each naming itself
        last_recode = max(m.start() for m in re.finditer(r"^replace \w+ = \. if ", self.text, flags=re.M))
        first_recode = min(m.start() for m in re.finditer(r"^replace \w+ = \. if ", self.text, flags=re.M))
        last_destring = max(m.start() for m in re.finditer(r"^destring ", self.text, flags=re.M))
        first_loop = min(m.start() for m in re.finditer(r"^(foreach|forvalues|while|reshape|collapse)\b", self.text, flags=re.M))
        first_use = min(m.start() for m in re.finditer(r"^(gen|egen|quietly|display)\b", self.text, flags=re.M))
        self.assertLess(last_destring, first_recode)
        self.assertLess(last_recode, first_loop)
        self.assertLess(last_recode, first_use)
        # the export's own sentinel is the one recoded, and the three price columns are the ones that can hold it
        self.assertTrue(any(f"Sentinel: {SENTINEL} in rt_usd_mwh or da_usd_mwh or hub_rt_usd_mwh" in c for c in self.comments))

    def test_it_reads_the_column_names_from_the_line_that_holds_them(self):
        n = len(self.comments)
        self.assertEqual(n, HEADER_LINES)
        self.assertIn(f'import delimited using "{CSV_NAME}", varnames({n + 1}) rowrange({n + 2}) stringcols(_all) clear', self.text)
        self.assertNotIn("varnames(1)", self.text)
        self.assertTrue(any(f"varnames({n + 1}) rowrange({n + 2})" in c for c in self.comments))
        self.assertIn(f"* The file has {n} comment lines; the column names are on line {n + 1} and the hours start on line {n + 2}.", self.text)
        for name in (CSV_NAME, DO_NAME):
            self.assertRegex(name, r"^[a-z]+_\d{4}_[a-z]+(_[a-z]+)+\.(csv|do)$")

    def test_it_says_at_the_top_that_it_has_not_been_run(self):
        top = "\n".join(self.lines[:8])
        self.assertIn("This do-file has not been run: Stata is not installed on the machine that wrote it.", top)

    def test_every_real_valued_variable_is_a_double(self):
        # Stata's gen makes a float (seven digits) unless told otherwise: a float sum of a year's prices would lose the cents
        for v in DOUBLES:
            self.assertRegex(self.text, rf"(?m)^e?gen double {v} = ", v)
        made = re.findall(r"(?m)^e?gen (?:double )?(\w+) = ", self.text)
        whole = [v for v in made if v not in DOUBLES]
        self.assertEqual(whole, ["ym", "rt_hour", "da_hour", "hub_hour", "hours_due", "rt_counted", "da_counted", "hub_counted", "calendar_year", "year_months"])
        self.assertIn("collapse (sum) rt_usd_per_mw da_usd_per_mw hub_usd_per_mw rt_hours = rt_hour da_hours = da_hour hub_hours = hub_hour "
                      "(max) in_last_twelve, by(ym)", self.text)

    def test_the_reader_inputs_and_the_rule_of_a_month_are_the_pages(self):
        lib = src("site", "lib", "datacenter.ts")
        self.assertIn(f'gpu: {{ value: {GPU_KW}, unit: "kW per GPU"', lib)
        self.assertIn(f"pue: {{ value: {PUE}, unit:", lib)
        self.assertIn(f"export const DEFAULTS = {{ mw: {MW}, n: 100, pct: 5, shift: 20, gpu: ASSUMED.gpu.value, pue: ASSUMED.pue.value }};", lib)
        self.assertIn("export const NEAR = 0.95;", lib)
        self.assertIn("r.complete = r.held >= NEAR * r.due;", lib)
        self.assertIn('const run = (Object.keys(RUNS) as Run[]).includes(q.run as Run) ? (q.run as Run) : "flat";', lib)
        self.assertIn('const buy: Buy = q.buy === "da" ? "da" : "rt";', lib)
        for line in (f"scalar s_mw = {MW}", f"scalar s_gpu_kw = {GPU_KW}", f"scalar s_pue = {PUE}", "gen hours_due = 24 * day(dofm(ym + 1) - 1)",
                     "gen rt_counted = rt_hours >= 0.95 * hours_due", "gsort -rt_usd_mwh_month ym", "scalar s_bad_rank = max(1, ceil(0.1 * _N))",
                     "keep if rt_counted == 1 & ym >= s_l12_last - 35 & ym <= s_l12_last"):
            self.assertIn(line + "\n", self.text)
        mirror, _ = mirror_numbers()
        self.assertEqual((mirror.MW, mirror.GPU_KW, mirror.PUE, mirror.NEAR), (MW, GPU_KW, PUE, 0.95))
        ex = exporter()
        self.assertEqual((ex.GRID, ex.REGION, ex.BUY, ex.MW, ex.GPU_KW, ex.PUE, ex.NEAR), ("ercot", "LZ_NORTH", "rt", MW, GPU_KW, PUE, 0.95))
        self.assertEqual(facts()["grid"]["main"], "LZ_NORTH")             # the page's default region, by its own index
        self.assertEqual(facts()["ref"], "HB_NORTH")

    def test_the_mirror_follows_the_do_file_display_for_display(self):
        mirror, n = mirror_numbers()
        shown = [re.match(r'\s*display "([^"`:]*)', line).group(1) for line in self.lines if line.strip().startswith("display")]
        out = mirror.report(n)
        self.assertEqual(len(shown), 19)                                  # 18 lines and the loop's one, which prints one a year
        self.assertEqual(len(out), 18 + len(n["years"]))
        at = 0
        for words in shown:                                               # the same lines in the same order
            found = next((i for i in range(at, len(out)) if out[i].startswith(words.strip())), None)
            self.assertIsNotNone(found, words)
            at = found
        self.assertEqual(mirror.HEADER_LINES, HEADER_LINES)
        self.assertEqual(mirror.SENTINEL, SENTINEL)
        self.assertEqual(mirror.NUMERIC, self.numeric)
        self.assertEqual(mirror.RECODED, PRICE_COLUMNS)


class TheExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comments, cls.columns, cls.lines = csv_text()
        cls.rows = [line.split(",") for line in cls.lines]

    def test_the_bytes_the_header_and_the_columns(self):
        with open(CSV_PATH, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertLess(len(raw), 6 * 1024 * 1024)
        self.assertEqual(self.columns, COLUMNS)
        self.assertEqual(len(self.comments), HEADER_LINES)
        self.assertTrue(all(len(r) == len(COLUMNS) for r in self.rows))
        for c in self.comments:
            self.assertTrue(c.startswith("# "))
            self.assertNotIn(",", c)
            self.assertNotIn('"', c)
            self.assertNotIn(EM, c)
        text = "\n".join(self.comments)
        for words in ("ercot_zone_prices_history", "ercot_all_hub_prices_history", "NP4-180-ER", "NP6-785-ER", "Last run (UTC) of each table", "sha256", "Exported:",
                      "LZ_NORTH", "HB_NORTH", "site/data/datacenter/index.json", f"({len(self.rows)} rows)", "License: public", "US Central standard time",
                      "No table is read at export", "docs/methods/datacenter_pays_algorithm.md"):
            self.assertIn(words, text)

    def test_the_gitattributes_keep_the_three_files_lf(self):
        attributes = src(".gitattributes")
        for f in (CSV_NAME, DO_NAME, MIRROR_NAME):
            self.assertIn(f"site/public/datacenter/{f} text eol=lf\n", attributes)
            with open(os.path.join(PUBLIC, f), "rb") as fh:
                self.assertNotIn(b"\r", fh.read(), f)

    def test_the_exporter_writes_these_columns(self):
        ex = exporter()
        self.assertEqual(ex.COLUMNS, COLUMNS)
        self.assertEqual((ex.HEADER_LINES, ex.SENTINEL, ex.CSV_NAME), (HEADER_LINES, SENTINEL, CSV_NAME))
        self.assertEqual(os.path.abspath(ex.OUT), os.path.abspath(CSV_PATH))

    def test_the_hours_run_unbroken_and_each_month_is_central_standard_time(self):
        first = datetime.strptime(self.rows[0][0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        self.assertEqual(self.rows[0][0], "2015-01-01T06:00:00Z")         # hour 0 of 2015 in Central standard time
        n = len(self.rows)
        for i in sorted({0, 1, 1000, n // 2, n - 2, n - 1} | set(range(0, n, 997))):
            t = first + timedelta(hours=i)
            self.assertEqual(self.rows[i][0], t.strftime("%Y-%m-%dT%H:%M:%SZ"))
            self.assertEqual(self.rows[i][1], (t - timedelta(hours=6)).strftime("%Y-%m"), self.rows[i][0])     # no daylight saving shift, summer or winter
        hours = [r[0] for r in self.rows]
        self.assertEqual(hours, sorted(hours))
        self.assertEqual(len(set(hours)), n)                              # sorted, distinct, and as many as the span holds: no hour is missing
        last = datetime.strptime(self.rows[-1][0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        self.assertEqual(int((last - first).total_seconds() // 3600) + 1, n)
        # every whole month holds its calendar hours, 24 a day
        per = {}
        for r in self.rows:
            per[r[1]] = per.get(r[1], 0) + 1
        months = sorted(per)
        for m in months[:-1]:
            self.assertEqual(per[m], 24 * calendar.monthrange(int(m[:4]), int(m[5:7]))[1], m)

    def test_the_values_and_the_flag(self):
        months, missing = {}, {c: 0 for c in PRICE_COLUMNS}
        for hour, month, rt, da, hub, flag in self.rows:
            self.assertIn(flag, ("0", "1"))
            for c, v in zip(PRICE_COLUMNS, (rt, da, hub)):
                x = float(v)
                if x == SENTINEL:
                    missing[c] += 1
                else:
                    self.assertAlmostEqual(x * 100, round(x * 100), places=6, msg=hour)      # to the cent
            months.setdefault(month, set()).add(flag)
        self.assertTrue(all(len(v) == 1 for v in months.values()))        # a month is marked whole or not at all
        marked = sorted(m for m, v in months.items() if v == {"1"})
        self.assertEqual(len(marked), 12)
        self.assertEqual(marked, [prev_month(marked[-1], k) for k in range(11, -1, -1)])       # twelve months in a row
        self.assertEqual(marked, facts()["l12"])                          # and they are the page's
        said = next(c for c in self.comments if c.startswith("# Sentinel"))
        self.assertIn(f"({missing['rt_usd_mwh']} and {missing['da_usd_mwh']} and {missing['hub_rt_usd_mwh']} hours in this file)", said)
        self.assertEqual(float(self.rows[0][2]) != SENTINEL and float(self.rows[-1][2]) != SENTINEL, True)   # the window is the zone's first to last hour held

    def test_the_exporter_skips_without_the_pages_files_and_writes_nothing(self):
        import contextlib
        import io
        import tempfile
        ex = exporter()
        with tempfile.TemporaryDirectory() as tmp:
            out, said = os.path.join(tmp, "trial.csv"), io.StringIO()
            with contextlib.redirect_stdout(said):
                code = ex.main(["--site-dir", os.path.join(tmp, "no_files"), "--out", out])
            self.assertEqual(code, 0)
            self.assertIn("datacenter_hourly_export SKIPPED: the page's files are not under", said.getvalue())
            self.assertEqual(os.listdir(tmp), [])

    def test_a_run_that_changes_no_hour_leaves_the_file_as_it_is(self):
        import contextlib
        import io
        import tempfile
        ex = exporter()
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, CSV_NAME)
            shutil.copyfile(CSV_PATH, out)
            said = io.StringIO()
            with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
                code = ex.main(["--out", out])
            self.assertEqual(code, 0, said.getvalue())
            self.assertIn("unchanged (the page's files hold the same hours); left as it is", said.getvalue(),
                          "the page's files moved since the CSV was exported: run python warehouse/derived/datacenter_hourly_export.py and commit the CSV")
            with open(out, "rb") as a, open(CSV_PATH, "rb") as b:
                self.assertEqual(a.read(), b.read())


class TheCsvAndThePagesFilesAgree(unittest.TestCase):
    """The exporter's own check, on the committed CSV and the page's own committed files: no table is needed."""
    AGAIN = "the page's files and the CSV differ: run python warehouse/derived/datacenter_hourly_export.py (no table, no lock) and commit the CSV"

    @classmethod
    def setUpClass(cls):
        cls.ex = exporter()
        cls.lines = csv_text()[2]
        cls.facts = facts()

    def test_every_hour_and_every_month_agrees(self):
        bad, months = self.ex.agree(self.lines, self.facts)
        self.assertEqual(bad, [], self.AGAIN)
        held = [r for r in self.facts["months"]["rt"]]
        self.assertEqual(sorted(months), [r["m"] for r in held])          # every month the page holds of the zone, and no other

    def test_a_planted_error_is_caught(self):
        lines = list(self.lines)
        i = next(k for k, line in enumerate(lines) if line.split(",")[1] == self.facts["l12"][5])
        cells = lines[i].split(",")
        cells[2] = self.ex.fmt(float(cells[2]) + 1)                       # a dollar the zone did not pay
        lines[i] = ",".join(cells)
        bad, _ = self.ex.agree(lines, self.facts)
        said = " | ".join(bad)
        self.assertIn(f"hour {cells[0]} rt", said)
        self.assertIn(f"month {cells[1]} rt sum of prices", said)
        # a row left out; a price blanked; a month marked that is not one of the twelve; the hub's price in the zone's place
        k = len(self.lines) // 2
        bad, _ = self.ex.agree(self.lines[:k] + self.lines[k + 1:], self.facts)
        self.assertTrue(any(b.startswith("hours: ") for b in bad) and any("the rows hold no such hour" in b for b in bad), bad)
        blanked = list(self.lines)
        c = blanked[k].split(",")
        c[3] = str(SENTINEL)
        blanked[k] = ",".join(c)
        bad, _ = self.ex.agree(blanked, self.facts)
        self.assertTrue(any(" da: the row holds" in b for b in bad) and any(" da hours: " in b for b in bad), bad)
        before = prev_month(self.facts["l12"][0], 1)
        marked = [line[:-1] + "1" if line.split(",")[1] == before else line for line in self.lines]
        bad, _ = self.ex.agree(marked, self.facts)
        self.assertTrue(any(b.startswith("in_last_twelve marks") for b in bad))
        swapped = [",".join([c[0], c[1], c[4], c[3], c[2], c[5]]) for c in (line.split(",") for line in self.lines)]
        bad, _ = self.ex.agree(swapped, self.facts)
        self.assertTrue(any(" rt: the row holds" in b for b in bad) and any(" hub: the row holds" in b for b in bad))

    def test_the_tables_behind_the_case_are_public(self):
        runs = self.ex.last_runs(["ercot_zone_prices_history", "ercot_all_hub_prices_history", "iso_rtm_hub_prices"])
        for t, (last_run, lic, report) in runs.items():
            self.assertEqual(lic, "public", t)
            self.assertRegex(last_run, r"^\d{4}-\d\d-\d\dT")
        self.assertIn("ercot:NP6-785-ER", runs["ercot_zone_prices_history"][2])


class TheMirrorAndThePage(unittest.TestCase):
    """The mirror's numbers beside the page's, computed in Python from the page's files (the exporter's page_facts)."""
    @classmethod
    def setUpClass(cls):
        cls.mirror, cls.n = mirror_numbers()
        cls.facts = facts()

    def test_each_month_of_the_mirror_is_the_pages_month(self):
        for k in ("rt", "da", "hub"):
            want = {r["m"]: r for r in self.facts["months"][k]}
            inner = [m for m in self.n["months"] if m["ym"] not in (self.n["months"][0]["ym"], self.n["months"][-1]["ym"]) or k == "rt"]
            for m in inner:
                w = want[m["ym"]]
                self.assertEqual((m[f"{k}_hours"], m["hours_due"], m[f"{k}_counted"]), (w["held"], w["due"], w["complete"]), (k, m["ym"]))
                self.assertAlmostEqual(m[f"{k}_usd_per_mw"], w["flat"], delta=1e-6, msg=(k, m["ym"]))

    def test_the_first_headline_number(self):
        n, f = self.n, self.facts
        self.assertEqual([n["l12_first"], n["l12_last"]], [f["l12"][0], f["l12"][-1]])
        self.assertEqual((n["l12_months"], n["l12_hours"]), (12, f["s12"]["held"]))
        self.assertAlmostEqual(n["l12_usd_per_mw"], f["s12"]["cost"], delta=1e-6)
        self.assertAlmostEqual(n["l12_usd_mwh"], f["s12"]["per"], delta=1e-9)
        self.assertEqual(js_two(n["l12_usd_mwh"]), js_two(f["s12"]["per"]))
        self.assertEqual(js_short(n["l12_usd"]), js_short(f["s12"]["cost"] * MW))
        self.assertEqual(n["l12_mwh"], f["s12"]["held"] * MW)

    def test_the_gpu_hour_the_hub_and_day_ahead(self):
        n, f = self.n, self.facts
        self.assertAlmostEqual(n["gpu_hour"], f["s12"]["per"] * GPU_KW * PUE / 1000, delta=1e-12)
        self.assertAlmostEqual(n["gpus"], MW * 1000 / (GPU_KW * PUE), delta=1e-9)
        self.assertIsNotNone(f["hub12"])
        self.assertEqual(n["hub_months"], 12)
        self.assertAlmostEqual(n["hub_usd_mwh"], f["hub12"]["per"], delta=1e-9)
        self.assertAlmostEqual(n["zone_less_hub"], f["s12"]["per"] - f["hub12"]["per"], delta=1e-9)
        self.assertIsNotNone(f["da12"], "the zone's day-ahead last twelve months are no longer the real-time ones: the do-file's day-ahead line needs a word")
        self.assertEqual(n["da_months"], 12)
        self.assertAlmostEqual(n["da_usd_mwh"], f["da12"]["per"], delta=1e-9)

    def test_the_bad_month_and_the_years(self):
        n, f = self.n, self.facts
        w, bad = f["w36"], f["bad"]
        self.assertEqual((n["w36_months"], n["w36_first"], n["w36_last"]), (len(w["months"]), w["months"][0]["m"], w["to"]))
        self.assertEqual(n["bad_rank"], max(1, math.ceil(0.1 * len(w["months"]))))
        self.assertEqual(n["bad_month"], bad["m"])
        self.assertAlmostEqual(n["bad_usd_mwh"], bad["flat"] / bad["held"], delta=1e-9)
        self.assertAlmostEqual(n["bad_usd"], bad["flat"] * MW, delta=1e-4)
        rt = f["months"]["rt"]
        self.assertEqual((n["months_held"], n["first_held"], n["last_held"]), (len(rt), rt[0]["m"], rt[-1]["m"]))
        self.assertEqual(n["months_counted"], sum(1 for r in rt if r["complete"]))
        for y in n["years"]:
            done = [r for r in rt if r["m"].startswith(str(y["year"])) and r["complete"]]
            self.assertEqual(y["months"], len(done), y["year"])
            self.assertAlmostEqual(y["usd_mwh"], sum(r["flat"] for r in done) / sum(r["held"] for r in done), delta=1e-9, msg=y["year"])

    def test_the_lines_the_mirror_prints_on_the_window_it_was_written_for(self):
        if not on_the_window():
            raise unittest.SkipTest(f"the page's last twelve months are {facts()['l12'][0]} to {facts()['l12'][-1]}, no longer {WINDOW[0]} to {WINDOW[1]}: "
                                    "the figures of 11 October 2026 are not pinned (the mirror is still held to the page above)")
        out = self.mirror.report(self.n)
        for line in ("the last twelve months: 2025-10 to 2026-09", "months in the last twelve that count: 12", "hours held in the last twelve months: 8760",
                     "market energy, a flat load, last twelve months, USD per MWh: 33.73", "cost for 100 MW, USD: 29,546,505",
                     "energy for 100 MW, MWh: 876,000", "power per GPU-hour, USD: 0.0684", "GPUs that 100 MW powers: 49,310",
                     "months of the twelve that count at the hub: 12", "the hub beside it, a flat load, USD per MWh: 32.51",
                     "the load zone less its hub, USD per MWh: 1.22", "months of the twelve that count day-ahead: 12",
                     "bought day-ahead, a flat load, the same twelve months, USD per MWh: 35.33",
                     "year 2015: months that count 12, a flat load, USD per MWh: 24.04", "year 2021: months that count 12, a flat load, USD per MWh: 150.61",
                     "year 2025: months that count 12, a flat load, USD per MWh: 32.66", "year 2026: months that count 9, a flat load, USD per MWh: 34.02",
                     "months that count of the 36: 36, 2023-10 to 2026-09", "a bad month, nearest rank 4: 2026-08, USD per MWh: 37.88",
                     "the bad month's cost for 100 MW, USD: 2,818,474"):
            self.assertIn(line, out)
        self.assertEqual(len(out), 30)

    def test_the_mirror_reads_nothing_but_the_csv_and_the_standard_library(self):
        text = src("site", "public", "datacenter", MIRROR_NAME)
        imports = sorted(set(re.findall(r"(?m)^(?:import|from) (\w+)", text)))
        self.assertEqual(imports, ["calendar", "csv", "math", "os", "sys"])
        for word in ("index.json", "site/data", "urlopen", "requests", "subprocess"):
            self.assertNotIn(word, text)


PAGE_JS = """
import fs from "node:fs";
const L = await import("./lib/datacenter.ts");
const INDEX = JSON.parse(fs.readFileSync("./data/datacenter/index.json", "utf-8"));
const x = L.inputsOf({}, INDEX);
const F = INDEX.grids[x.grid].years.map((y) => JSON.parse(fs.readFileSync(`./data/datacenter/${x.grid}_${y}.json`, "utf-8")));
const FLAT = { run: "flat", n: 0, pct: 0, shift: 0 };
const region = INDEX.grids[x.grid].regions.find((r) => r.id === x.region);
const fore = L.monthsRuled(F, x.region, x.buy, x, "forecast"), ms = fore.months, l12 = L.lastTwelve(ms), s12 = L.span(l12), w36 = L.last36(ms), bad = L.badMonth(w36.months);
const refM = L.monthsOf(F, region.ref, x.buy, FLAT).filter((r) => r.m >= l12[0].m && r.m <= l12[11].m && r.complete);
const da12 = L.lastTwelve(L.monthsOf(F, x.region, "da", FLAT));
const out = { x, hrefDefault: L.hrefOf(x), ref: region.ref, l12: [l12[0].m, l12[11].m], s12, perText: L.two(s12.per), costText: L.usdShort(s12.cost * x.mw), mwhText: L.whole(s12.energy * x.mw),
  gpuHour: L.gpuHour(s12.per, x.gpu, x.pue), gpus: L.gpus(x.mw, x.gpu, x.pue), w36: { n: w36.months.length, first: w36.months[0].m, to: w36.to }, bad: { m: bad.m, per: bad.cost / bad.energy, cost: bad.cost },
  ref12: refM.length === 12 ? L.span(refM) : null, da12: da12 ? { from: da12[0].m, to: da12[11].m, ...L.span(da12) } : null,
  years: L.years(ms).map((r) => ({ y: r.y, months: r.months, complete: r.complete, flat: r.flat })), monthsHeld: ms.length, counted: ms.filter((r) => r.complete).length };
const CASES = __CASES__;
out.cases = CASES.map(([buy, c]) => { const r = {};
  for (const rule of ["forecast", "hindsight"]) { const m = L.monthsRuled(F, x.region, buy, c, rule).months, t = L.lastTwelve(m), s = L.span(t);
    r[rule] = { l12: [t[0].m, t[11].m], per: s.per, flat: s.flat, down: s.down, energy: s.energy, cost: s.cost, years: L.years(m).map((y) => ({ y: y.y, per: y.per, down: y.down, energy: y.energy })) }; }
  return r; });
console.log(JSON.stringify(out));
"""
# the flexible loads rebuilt a second time: (the market bought, how the load runs)
CASES = [("rt", dict(run="hours", n=100, pct=0, shift=0)), ("da", dict(run="hours", n=100, pct=0, shift=0)), ("rt", dict(run="share", n=0, pct=5, shift=0)),
         ("da", dict(run="share", n=0, pct=5, shift=0)), ("rt", dict(run="shift", n=0, pct=0, shift=20)), ("da", dict(run="shift", n=0, pct=0, shift=20)),
         ("rt", dict(run="hours", n=500, pct=0, shift=0)), ("rt", dict(run="shift", n=0, pct=0, shift=33))]


def library():
    if "lib" not in _KEPT:
        _KEPT["lib"] = node(PAGE_JS.replace("__CASES__", json.dumps(CASES)))
    return _KEPT["lib"]


class ThePagesOwnLibrary(unittest.TestCase):
    """The same numbers from node on site/lib/datacenter.ts and the page's own files."""
    @classmethod
    def setUpClass(cls):
        cls.lib = library()
        cls.mirror, cls.n = mirror_numbers()

    def test_the_default_case_is_the_one_exported(self):
        x = self.lib["x"]
        self.assertEqual((x["grid"], x["region"], x["run"], x["buy"], x["mw"], x["gpu"], x["pue"]), ("ercot", "LZ_NORTH", "flat", "rt", MW, GPU_KW, PUE))
        self.assertEqual(self.lib["hrefDefault"], "/cost-of-power?grid=ercot&region=LZ_NORTH&mw=100&run=flat&buy=rt")
        self.assertEqual(self.lib["ref"], "HB_NORTH")

    def test_the_headline_numbers(self):
        n, lib = self.n, self.lib
        self.assertEqual([n["l12_first"], n["l12_last"]], lib["l12"])
        self.assertEqual((n["l12_months"], n["l12_hours"]), (lib["s12"]["months"], lib["s12"]["held"]))
        for mine, theirs in ((n["l12_usd_mwh"], lib["s12"]["per"]), (n["l12_usd_mwh"], lib["s12"]["flat"]), (n["gpu_hour"], lib["gpuHour"]), (n["gpus"], lib["gpus"]),
                             (n["bad_usd_mwh"], lib["bad"]["per"]), (n["hub_usd_mwh"], lib["ref12"]["flat"]), (n["da_usd_mwh"], lib["da12"]["flat"])):
            self.assertAlmostEqual(mine, theirs, delta=1e-9)
        self.assertAlmostEqual(n["l12_usd_per_mw"], lib["s12"]["cost"], delta=1e-6)
        # as the page prints them
        self.assertEqual(js_two(n["l12_usd_mwh"]), lib["perText"])
        self.assertEqual(js_short(n["l12_usd"]), lib["costText"])
        self.assertEqual(f"{n['l12_mwh']:,.0f}", lib["mwhText"])
        self.assertEqual((n["bad_month"], n["w36_months"], n["w36_first"], n["w36_last"]), (lib["bad"]["m"], lib["w36"]["n"], lib["w36"]["first"], lib["w36"]["to"]))
        self.assertEqual([lib["da12"]["from"], lib["da12"]["to"]], lib["l12"])
        self.assertEqual((n["months_held"], n["months_counted"]), (lib["monthsHeld"], lib["counted"]))

    def test_the_years(self):
        self.assertEqual([y["year"] for y in self.n["years"]], [int(y["y"]) for y in self.lib["years"]])
        for mine, theirs in zip(self.n["years"], self.lib["years"]):
            self.assertEqual(mine["months"], theirs["months"])
            self.assertAlmostEqual(mine["usd_mwh"], theirs["flat"], delta=1e-9)
            self.assertEqual(js_two(mine["usd_mwh"]), js_two(theirs["flat"]))


# ---------------------------------------------------------------------------------------------------------------------
# The flexible load a second time, from docs/methods/datacenter_pays_algorithm.md section 5 and the CSV alone. Written
# for this test; it shares no line with site/lib/datacenter.ts.
# ---------------------------------------------------------------------------------------------------------------------

def csv_years():
    """{year: (real-time prices, day-ahead prices)} by the hour of the year in standard time, None where not held; the
    CSV begins at hour 0 of its first year and runs unbroken, so an hour's place is its count within its year."""
    if "years" in _KEPT:
        return _KEPT["years"]
    out = {}
    for line in csv_text()[2]:
        _hour, month, rt, da, _hub, _flag = line.split(",")
        y = int(month[:4])
        a = out.setdefault(y, ([], []))
        a[0].append(None if float(rt) == SENTINEL else float(rt))
        a[1].append(None if float(da) == SENTINEL else float(da))
    for y, (rt, da) in out.items():
        n = 8784 if calendar.isleap(y) else 8760
        rt.extend([None] * (n - len(rt)))
        da.extend([None] * (n - len(da)))
    _KEPT["years"] = out
    return out


def second_rule(pay, da, c):
    """Section 5.1: the weights of each year under the rule. pay, da: {year: hourly list}, consecutive years."""
    years = sorted(pay)
    w = {y: [0.0 if v is None else 1.0 for v in pay[y]] for y in years}
    if c["run"] == "shift":
        h = 24 * min(50, max(0, c["shift"])) / 100
        full, part = int(math.floor(h)), h - math.floor(h)
        for y in years:
            for d in range(0, len(da[y]) - 23, 24):
                day = range(d, d + 24)
                if any(da[y][i] is None or pay[y][i] is None for i in day):
                    continue
                order = sorted(day, key=lambda i: (-da[y][i], i))            # dearest day-ahead hour first
                for j in range(full):
                    w[y][order[j]] -= 1
                    w[y][order[23 - j]] += 1
                if part > 0:
                    w[y][order[full]] -= part
                    w[y][order[23 - full]] += part
        return w
    q = min(1.0, c["n"] / 8760) if c["run"] == "hours" else min(1.0, c["pct"] / 100)
    flat_da, start = [], {}
    for y in years:
        start[y] = len(flat_da)
        flat_da.extend(da[y])
    for y in years:
        left = js_round(q * len(pay[y]))                                     # the year's budget
        for d in range(0, len(da[y]) - 23, 24):
            g = start[y] + d
            prior = [v for v in flat_da[max(0, g - 720):g] if v is not None]
            if g < 720 or len(prior) < 0.95 * 720 or q <= 0:
                continue                                                     # not decided: the load runs
            k = min(len(prior), max(1, js_round(q * len(prior))))
            threshold = sorted(prior, reverse=True)[k - 1]
            if left <= 0:
                continue
            over = sorted((i for i in range(d, d + 24) if da[y][i] is not None and da[y][i] >= threshold and pay[y][i] is not None), key=lambda i: (-da[y][i], i))
            for i in over[:left]:
                w[y][i] = 0.0
            left -= min(left, len(over))
    return w


def second_foreseen(pay, c):
    """Section 5.2: the weights of each year with the hours chosen knowing the year's prices."""
    w = {}
    for y, p in pay.items():
        w[y] = [0.0 if v is None else 1.0 for v in p]
        held = [i for i, v in enumerate(p) if v is not None]
        if c["run"] == "shift":
            h = 24 * min(50, max(0, c["shift"])) / 100
            full, part = int(math.floor(h)), h - math.floor(h)
            for d in range(0, len(p) - 23, 24):
                if any(p[i] is None for i in range(d, d + 24)):
                    continue
                order = sorted(range(d, d + 24), key=lambda i: (-p[i], i))
                for j in range(full):
                    w[y][order[j]] -= 1
                    w[y][order[23 - j]] += 1
                if part > 0:
                    w[y][order[full]] -= part
                    w[y][order[23 - full]] += part
            continue
        k = min(len(held), js_round(c["n"] * len(held) / len(p) if c["run"] == "hours" else c["pct"] / 100 * len(held)))
        for i in sorted(held, key=lambda i: (-p[i], i))[:k]:
            w[y][i] = 0.0
    return w


def second_months(pay, w):
    """Section 4.1: one record a month held."""
    out = []
    for y in sorted(pay):
        at = 0
        for mo in range(1, 13):
            due = 24 * calendar.monthrange(y, mo)[1]
            r = dict(m=f"{y}-{mo:02d}", due=due, held=0, cost=0.0, flat=0.0, energy=0.0, down=0)
            for i in range(at, at + due):
                v = pay[y][i]
                if v is None:
                    continue
                r["held"] += 1
                r["flat"] += v
                r["cost"] += v * w[y][i]
                r["energy"] += w[y][i]
                r["down"] += 1 if w[y][i] == 0 else 0
            at += due
            r["counted"] = r["held"] >= 0.95 * due
            if r["held"]:
                out.append(r)
    return out


def second_twelve(ms):
    by = {r["m"]: r for r in ms}
    for r in reversed(ms):
        twelve = [by.get(prev_month(r["m"], k)) for k in range(11, -1, -1)]
        if all(t and t["counted"] for t in twelve):
            return twelve
    return None


def second_span(ms):
    cost, energy, held, flat = (sum(r[k] for r in ms) for k in ("cost", "energy", "held", "flat"))
    return dict(per=cost / energy if energy else None, flat=flat / held if held else None, down=sum(r["down"] for r in ms), energy=energy, cost=cost)


class TheFlexibleLoadASecondTime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = library()
        years = csv_years()
        cls.pay = {"rt": {y: v[0] for y, v in years.items()}, "da": {y: v[1] for y, v in years.items()}}

    def test_the_rule_and_the_foreseen_load_agree_with_the_library_hour_for_hour_in_effect(self):
        self.assertEqual(len(CASES), 8)
        for (buy, c), theirs in zip(CASES, self.lib["cases"]):
            pay, da = self.pay[buy], self.pay["da"]
            for name, w in (("forecast", second_rule(pay, da, c)), ("hindsight", second_foreseen(pay, c))):
                ms = second_months(pay, w)
                t = second_twelve(ms)
                mine, want = second_span(t), theirs[name]
                what = f"{buy} {c} {name}"
                self.assertEqual([t[0]["m"], t[-1]["m"]], want["l12"], what)
                self.assertEqual(mine["down"], want["down"], what)           # the same number of hours off in the twelve months
                self.assertAlmostEqual(mine["energy"], want["energy"], delta=1e-6, msg=what)
                self.assertAlmostEqual(mine["per"], want["per"], delta=1e-9, msg=what)
                self.assertAlmostEqual(mine["flat"], want["flat"], delta=1e-9, msg=what)
                for y in want["years"]:                                      # and in every calendar year held
                    done = [r for r in ms if r["m"].startswith(y["y"]) and r["counted"]]
                    s = second_span(done)
                    self.assertEqual(s["down"], y["down"], (what, y["y"]))
                    self.assertAlmostEqual(s["per"], y["per"], delta=1e-9, msg=(what, y["y"]))

    def test_the_rule_reads_no_price_of_the_hour_it_decides(self):
        # every real-time price replaced: the hours the rule turns the load off in do not move (it decides on day-ahead)
        c = CASES[0][1]
        w = second_rule(self.pay["rt"], self.pay["da"], c)
        other = {y: [None if v is None else 1000.0 - v for v in p] for y, p in self.pay["rt"].items()}
        w2 = second_rule(other, self.pay["da"], c)
        self.assertEqual(w, w2)
        self.assertGreater(sum(1 for y in w for i, v in enumerate(w[y]) if v == 0 and self.pay["rt"][y][i] is not None), 1000)

    def test_the_rule_is_never_off_in_more_hours_of_a_year_than_named(self):
        for buy, c in CASES:
            if c["run"] == "shift":
                continue
            w = second_rule(self.pay[buy], self.pay["da"], c)
            for y, p in self.pay[buy].items():
                off = sum(1 for i, v in enumerate(w[y]) if v == 0 and p[i] is not None)
                self.assertLessEqual(off, js_round((c["n"] / 8760 if c["run"] == "hours" else c["pct"] / 100) * len(p)), (buy, c, y))

    def test_the_example_of_the_note_on_the_window_it_was_written_for(self):
        if not on_the_window():
            raise unittest.SkipTest("the page's last twelve months moved: the note's example of 11 October 2026 is not pinned")
        rule, seen = self.lib["cases"][0]["forecast"], self.lib["cases"][0]["hindsight"]
        self.assertEqual((js_two(rule["flat"]), js_two(rule["per"]), rule["down"], js_two(seen["per"]), seen["down"]), ("33.73", "31.46", 100, "29.72", 109))
        self.assertEqual(js_round(100 * (rule["flat"] - rule["per"]) / (seen["flat"] - seen["per"])), 57)


class TheTables(unittest.TestCase):
    """Every hour of the CSV against the price tables, where they are on the machine (read only)."""
    def test_every_hour_is_the_tables_own(self):
        need = ["ercot_zone_prices_history", "ercot_all_hub_prices_history", "iso_rtm_hub_prices"]
        missing = [t for t in need if not os.path.exists(os.path.join(TABLES, t + ".csv"))]
        if missing:
            raise unittest.SkipTest(f"the price tables are not on this machine ({', '.join(missing)}); ERW_TABLES_DIR names another copy's warehouse/output")
        said = []
        wrong = exporter().check_tables(csv_text()[2], facts(), TABLES, said.append)
        self.assertEqual(wrong, 0, "\n".join(said))
        self.assertEqual(len(said), 3)
        for line in said:
            self.assertIn("differing by more than half a cent 0;", line)
            self.assertIn("in the tables only 0;", line)
        self.assertIn(f"hours in both {len(csv_text()[2]):,};", said[0])       # every hour of the zone's real-time price was compared


class House(unittest.TestCase):
    def test_no_em_dash_in_what_was_written(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            self.assertTrue(os.path.exists(p), f)
            with open(p, encoding="utf-8") as fh:
                self.assertNotIn(EM, fh.read(), f)

    def test_the_new_modules_names_are_their_own(self):
        names = {}
        for top in ("warehouse", "scripts", "tests", os.path.join("site", "public")):
            for d, dirs, files in os.walk(os.path.join(ROOT, top)):
                dirs[:] = [x for x in dirs if x not in ("output", "__pycache__", "node_modules", "raw")]
                for f in files:
                    if f.endswith(".py"):
                        names.setdefault(f, []).append(os.path.relpath(os.path.join(d, f), ROOT))
        for f in ("datacenter_hourly_export.py", "test_session190_replication.py", "test_session190.py", MIRROR_NAME):
            self.assertEqual(len(names.get(f, [])), 1, names.get(f))

    def test_the_exporter_writes_nothing_into_the_warehouse_and_asks_no_one(self):
        text = src("warehouse", "derived", "datacenter_hourly_export.py")
        for word in ("write_table", "write_csv", "_require_lock", "update_sources", "write_status", "set_out_dir", "subprocess", "import pandas", "import numpy"):
            self.assertNotIn(word, text, word)
        for word in ("anthropic", "requests.", "urlopen", "http.client"):
            self.assertNotIn(word, text.lower(), word)
        imports = sorted(set(re.findall(r"(?m)^import (\w+)", text)))
        self.assertEqual(imports, ["argparse", "csv", "datetime", "hashlib", "json", "math", "os", "sys"])    # the standard library: it runs on any machine
        self.assertNotRegex(text, r"(?m)^from \w+ import ")
        self.assertEqual(os.path.basename(os.path.dirname(os.path.abspath(CSV_PATH))), "datacenter")


if __name__ == "__main__":
    unittest.main()
