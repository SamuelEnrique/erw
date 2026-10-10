"""Session 183: "What a generator earns", the replication of the default case (ERCOT, solar, 100 MW, the hub average).
What is held to:

  the do-file follows the house rules, parsed line by line (Stata is not on this machine, so the file was never run):
    no continuation operator, one empty line between commands outside loops and none inside, every numeric column
    destrung with replace force, the sentinel recoded per variable before any loop or collapse, every real-valued
    variable made as a double, and it reads the column names from the line of the CSV that holds them;
  the hourly export is what its header says (columns, rows, an unbroken run of hours, the local days, the twelve marked
    months, the sentinel, LF bytes, no comma in a comment line);
  the CSV and the page's two committed files agree: by the exporter's own check (each month of
    site/data/merchant_snapshot.json and of site/data/seller/capture.json, each hour's price), which also catches a
    planted error;
  the Python mirror, which follows the do-file step for step, rebuilds the page's headline numbers. The page's numbers
    are computed two ways and the mirror is held to both: in Python, directly from the two committed files with the
    formulas of site/lib/merchant.ts, site/lib/seller2.ts and site/lib/capture.ts (always run); and by node on those
    three files themselves, as tests/test_session107.py runs them (skipped where node is absent).

No request, no model call, no table of warehouse/output: everything here reads committed files. The environment is
read, never set. The exporter's own run needs the tables and is not repeated here (runs/session183/export.out); its
refusal to run without them is tested on an empty folder."""
import contextlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
PUBLIC = os.path.join(ROOT, "site", "public", "seller")
CSV_NAME, DO_NAME, MIRROR_NAME = "erw_2026_generator_hourly.csv", "erw_2026_generator_replication.do", "erw_2026_generator_replication.py"
CSV_PATH, DO_PATH, MIRROR_PATH = (os.path.join(PUBLIC, f) for f in (CSV_NAME, DO_NAME, MIRROR_NAME))
SNAPSHOT = os.path.join(ROOT, "site", "data", "merchant_snapshot.json")
CAPTURE = os.path.join(ROOT, "site", "data", "seller", "capture.json")
EM = chr(0x2014)
COLUMNS = ["hour_utc", "local_day", "local_month", "price_usd_mwh", "solar_mwh", "nameplate_mw", "in_last_twelve"]
TEXT_COLUMNS = ["hour_utc", "local_day", "local_month"]
HEADER_LINES, SENTINEL, ROWS = 16, -99999, 72384
DOUBLES = ["output_mwh_per_mw", "revenue_usd_per_mw", "capture_price_sum", "capture_mwh", "capture_usd", "revenue_usd", "cfads_usd", "cover",
           "cum_cfads_usd", "ttm_cover"]
FILES = ["warehouse/derived/generator_hourly_export.py", f"site/public/seller/{DO_NAME}", f"site/public/seller/{MIRROR_NAME}",
         f"site/public/seller/{CSV_NAME}", "tests/test_session183_replication.py", "runs/session183/REPLICATION.md"]
# the page's defaults for solar (site/lib/merchant.ts: DEFAULTS.solar, DEBT, DEFAULT_SIZE.solar), held to its text below
MW, CAPEX, LIFE, FOM, SHARE, RATE = 100, 1375, 35, 12.5, 0.6, 0.08
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
        mirror = load("erw_generator_replication_mirror_183", MIRROR_PATH)
        _KEPT["mirror"] = (mirror, mirror.numbers(mirror.read(CSV_PATH)))
    return _KEPT["mirror"]


def exporter():
    """The exporter, or a skip where its libraries (pandas, openpyxl, pyarrow) are not installed."""
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    try:
        import generator_hourly_export as ex
    except ImportError as e:
        raise unittest.SkipTest(f"the exporter's libraries are not on this machine: {e}")
    return ex


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"),
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


def prev_month(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 - k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def page_numbers():
    """The default page's numbers in Python, directly from the two committed files, with the page's formulas:
    lib/merchant.ts (inputsOf, months, summary, ttm, stat), lib/seller2.ts (lastTwelve, years, lastThreeYears, spanOf)
    and lib/capture.ts (counted, lastTwelve, figure)."""
    if "page" in _KEPT:
        return _KEPT["page"]
    with open(SNAPSHOT, encoding="utf-8") as f:
        snap = json.load(f)
    with open(CAPTURE, encoding="utf-8") as f:
        cap = json.load(f)
    s, near = snap["isos"]["ercot"], snap["defaults"]["near"]
    ds = math.floor(CAPEX * 1000 * SHARE * (RATE / (1 - (1 + RATE) ** -LIFE)) * MW + 0.5)          # Math.round(debtPerMw(k) * mw)
    ms = []
    for m, r in sorted(s["months"].items()):
        a = r.get("solar")
        if not a:
            continue
        revenue = a["revenue_per_mw"] * MW
        cfads = revenue - (FOM * 1000 * MW) / 12
        ms.append(dict(m=m, held=a["hours"] / r["him"] >= near - 1e-9, per_mw=a["revenue_per_mw"], revenue=revenue, cfads=cfads, dscr=cfads / (ds / 12),
                       hours=a["hours"], him=r["him"], energy=a["energy_per_mw"]))
    by = {r["m"]: r for r in ms}
    held = [r for r in ms if r["held"]]
    ranked = sorted(held, key=lambda r: (r["revenue"], r["m"]))
    rank = lambda p: ranked[max(0, math.ceil(p * len(ranked)) - 1)]  # noqa: E731
    ttm = []
    for r in held:
        twelve = [by.get(prev_month(r["m"], k)) for k in range(12)]
        if all(t and t["held"] for t in twelve):
            ttm.append((r["m"], sum(t["cfads"] for t in twelve) / ds))
    l12 = None
    for r in reversed(ms):
        twelve = [by.get(prev_month(r["m"], k)) for k in range(12)]
        if r["held"] and all(t and t["held"] for t in twelve):
            l12 = twelve[::-1]
            break
    years = {}
    for r in held:
        years.setdefault(r["m"][:4], []).append(r)
    full = sorted(y for y, v in years.items() if len(v) == 12)
    want = [str(int(full[-1]) - k) for k in (2, 1, 0)] if full else []
    three = want if full and all(y in full for y in want) else None
    span = lambda rows, n: sum(r["per_mw"] for r in rows) / n / 1000  # noqa: E731
    hub = next(h for h in cap["grids"]["ercot"]["hubs"] if h["id"] == cap["grids"]["ercot"]["main"])
    months, cnear = hub["rt"]["solar"], cap["near"]
    counted = lambda rec: rec[0] >= cnear * rec[1] - 1e-9  # noqa: E731
    c12 = None
    for m in sorted(months, reverse=True):
        twelve = [prev_month(m, k) for k in range(11, -1, -1)]
        if all(t in months and counted(months[t]) for t in twelve):
            c12 = twelve
            break
    n, sp, g, pg = (sum(months[m][i] for m in c12) for i in (0, 2, 3, 4))
    price, flat = pg / g, sp / n
    _KEPT["page"] = dict(
        snap=snap, cap=cap, months=ms, cap_months=months, ds=ds, key_hub=hub["id"],
        l12=[r["m"] for r in l12], l12_kw=span(l12, 1), three=three, three_kw=span([r for r in held if r["m"][:4] in three], 3) if three else None,
        full=full, every_kw=span([r for r in held if r["m"][:4] in full], len(full)) if full else None,
        c12=c12, price=price, flat=flat, premium=price - flat, pct=100 * (price - flat) / flat, cap_hours=n,
        n=len(held), first=held[0]["m"], last=held[-1]["m"], median=rank(0.5), p10=rank(0.1), worst=ranked[:3],
        annual=sum(r["revenue"] for r in held) / len(held) * 12, under1=sum(1 for r in held if r["dscr"] < 1), under125=sum(1 for r in held if r["dscr"] < 1.25),
        ttm=ttm, ttm_last=ttm[-1][1], ttm_min=min(v for _, v in ttm), ttm_under1=sum(1 for _, v in ttm if v < 1), ttm_under125=sum(1 for _, v in ttm if v < 1.25))
    return _KEPT["page"]


two = lambda v: f"{v:.2f}"  # noqa: E731  (the page prints two decimals)
one = lambda v: f"{v:.1f}"  # noqa: E731


class DoFileRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = src("site", "public", "seller", DO_NAME)
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
        self.assertGreater(seen, 90)
        self.assertEqual(loops, 2)                                       # so the rule for the inside of a loop is exercised
        self.assertFalse(lines[-1].strip() == "", "the file ends with two empty lines")

    def test_every_numeric_column_is_destrung_with_force_one_command_each(self):
        got = re.findall(r"^destring (\w+), replace force$", self.text, flags=re.M)
        self.assertEqual(got, self.numeric)
        self.assertEqual(len(re.findall(r"^\s*destring\b", self.text, flags=re.M)), len(self.numeric), "a destring without replace force")
        self.assertEqual(self.numeric, ["price_usd_mwh", "solar_mwh", "nameplate_mw", "in_last_twelve"])
        # the three text columns are read as text and never destrung
        for c in TEXT_COLUMNS:
            self.assertNotRegex(self.text, rf"destring {c}\b")

    def test_the_sentinel_is_recoded_per_variable_before_any_loop_or_collapse(self):
        got = re.findall(r"^replace (\w+) = \. if (\w+) == (-\d+)$", self.text, flags=re.M)
        self.assertEqual(got, [("solar_mwh", "solar_mwh", str(SENTINEL))])
        recode = self.text.index("replace solar_mwh = . if")
        last_destring = max(m.start() for m in re.finditer(r"^destring ", self.text, flags=re.M))
        first_loop = min(m.start() for m in re.finditer(r"^(foreach|forvalues|while|reshape|collapse)\b", self.text, flags=re.M))
        first_use = min(m.start() for m in re.finditer(r"^(gen|egen|quietly|display)\b", self.text, flags=re.M))
        self.assertLess(last_destring, recode)
        self.assertLess(recode, first_loop)
        self.assertLess(recode, first_use)
        # the export's own sentinel is the one recoded, and solar_mwh is the one column that holds it
        self.assertTrue(any(f"Sentinel: {SENTINEL} in solar_mwh" in c and "No other column holds a sentinel" in c for c in self.comments))

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
        # Stata's gen makes a float (seven digits) unless told otherwise: a float month would lose the cents
        for v in DOUBLES:
            self.assertRegex(self.text, rf"(?m)^gen double {v} = ", v)
        made = re.findall(r"(?m)^gen (?:double )?(\w+) = ", self.text)
        whole = [v for v in made if v not in DOUBLES]
        self.assertEqual(whole, ["model_hour", "ym", "capture_hour", "hours_in_month", "held", "capture_counted", "calendar_year", "full_year", "streak"])
        self.assertIn("collapse (sum) revenue_usd_per_mw energy_mwh_per_mw = output_mwh_per_mw hours = model_hour capture_hours = capture_hour "
                      "capture_price_sum capture_mwh capture_usd (max) in_last_twelve, by(ym)", self.text)

    def test_the_reader_inputs_are_the_page_defaults(self):
        lib = src("site", "lib", "merchant.ts")
        self.assertIn(f"solar: {{ capex: {CAPEX}, life: {LIFE}, fom: {FOM},", lib)
        self.assertIn(f"export const DEBT = {{ share: {SHARE}, rate: {RATE} }};", lib)
        self.assertIn(f"solar: {{ mw: {MW}, mwh: 0 }}", lib)
        self.assertIn('const iso = q.iso && q.iso in ISO_NAMES ? q.iso : "ercot";', lib)
        self.assertIn('const asset = (q.asset && q.asset in ASSET_NAMES ? q.asset : "solar") as Asset;', lib)
        for line in (f"scalar s_mw = {MW}", f"scalar s_fom_usd_kw_year = {FOM}", f"scalar s_capex_usd_kw = {CAPEX}", f"scalar s_debt_share = {SHARE}",
                     f"scalar s_debt_rate = {RATE}", f"scalar s_debt_years = {LIFE}"):
            self.assertIn(line + "\n", self.text)
        mirror, _ = mirror_numbers()
        self.assertEqual((mirror.MW, mirror.FOM_USD_KW_YEAR, mirror.CAPEX_USD_KW, mirror.DEBT_SHARE, mirror.DEBT_RATE, mirror.DEBT_YEARS),
                         (MW, FOM, CAPEX, SHARE, RATE, LIFE))

    def test_the_rules_of_a_month_are_the_two_builders(self):
        snap, cap = page_numbers()["snap"], page_numbers()["cap"]
        self.assertEqual((snap["defaults"]["near"], cap["near"]), (0.9, 0.95))
        self.assertIn("gen held = hours / hours_in_month >= 0.9 - 1e-9 & energy_mwh_per_mw > 0\n", self.text)
        self.assertIn("gen capture_counted = capture_hours >= 0.95 * hours_in_month - 1e-9\n", self.text)
        self.assertIn("gen capture_hour = solar_mwh < . & price_usd_mwh < . & ym >= tm(2019m1)\n", self.text)
        self.assertIn("gen double capture_mwh = max(0, solar_mwh) if capture_hour == 1\n", self.text)
        self.assertIn('FIRST = "2019-01"', src("warehouse", "derived", "mix_profile.py"))
        self.assertIn("NEAR = 0.95 ", src("warehouse", "derived", "capture_price.py"))
        self.assertIn('d["g"] = d["g"].clip(lower=0)', src("warehouse", "derived", "capture_price.py"))
        self.assertIn('h["solar"] = np.where(h["sun_mw"] > 0, h["sun"] / h["sun_mw"], np.nan)', src("warehouse", "derived", "merchant_revenue.py"))

    def test_the_mirror_follows_the_do_file_display_for_display(self):
        mirror, n = mirror_numbers()
        shown = [re.match(r'\s*display "([^"`:]*)', line).group(1) for line in self.lines if line.strip().startswith("display")]
        out = mirror.report(n)
        self.assertEqual(len(shown), 27)                                  # 26 lines and the loop's one, which prints three
        self.assertEqual(len(out), 29)
        at = 0
        for words in shown:                                               # the same lines in the same order
            found = next((i for i in range(at, len(out)) if out[i].startswith(words.strip())), None)
            self.assertIsNotNone(found, words)
            at = found
        self.assertEqual(mirror.HEADER_LINES, HEADER_LINES)
        self.assertEqual(mirror.SENTINEL, SENTINEL)
        self.assertEqual(mirror.NUMERIC, self.numeric)


class TheExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comments, cls.columns, cls.lines = csv_text()
        cls.rows = [line.split(",") for line in cls.lines]

    def test_the_bytes_the_header_and_the_row_count(self):
        with open(CSV_PATH, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertLess(len(raw), 5 * 1024 * 1024)
        self.assertEqual(self.columns, COLUMNS)
        self.assertEqual(len(self.comments), HEADER_LINES)
        self.assertEqual(len(self.rows), ROWS)
        self.assertTrue(all(len(r) == len(COLUMNS) for r in self.rows))
        for c in self.comments:
            self.assertTrue(c.startswith("# "))
            self.assertNotIn(",", c)
            self.assertNotIn('"', c)
            self.assertNotIn(EM, c)
        text = "\n".join(self.comments)
        for words in ("iso_rtm_hub_prices", "ercot_all_hub_prices_history", "eia860m_operating_generators", "eia860m_retired_generators", "_ERCO.xlsx",
                      "Retrieved (UTC)", "sha256", "Exported:", "HB_HUBAVG", "Adjusted SUN Gen", "merchant_snapshot.json", "capture.json", "one flag is kept",
                      "one column of each is kept", f"({ROWS} rows)", "License: public"):
            self.assertIn(words, text)

    def test_the_gitattributes_keep_the_three_files_lf(self):
        attributes = src(".gitattributes")
        for f in (CSV_NAME, DO_NAME, MIRROR_NAME):
            self.assertIn(f"site/public/seller/{f} text eol=lf\n", attributes)
            with open(os.path.join(PUBLIC, f), "rb") as fh:
                self.assertNotIn(b"\r", fh.read(), f)

    def test_the_exporter_writes_these_columns(self):
        ex = exporter()
        self.assertEqual(ex.COLUMNS, COLUMNS)
        self.assertEqual((ex.HEADER_LINES, ex.SENTINEL, ex.CSV_NAME), (HEADER_LINES, SENTINEL, CSV_NAME))
        self.assertEqual((ex.GRID, ex.ASSET, ex.HUB, ex.SIDE, ex.MARKET), ("ercot", "solar", "HB_HUBAVG", "rtm", "rt"))

    def test_the_hours_run_unbroken_from_the_first_to_the_last(self):
        first = datetime(2018, 7, 1, 5, tzinfo=timezone.utc)
        for i in (0, 1, 1000, ROWS // 2, ROWS - 2, ROWS - 1):
            self.assertEqual(self.rows[i][0], (first + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.assertEqual(self.rows[-1][0], "2026-10-03T04:00:00Z")
        hours = [r[0] for r in self.rows]
        self.assertEqual(hours, sorted(hours))
        self.assertEqual(len(set(hours)), ROWS)                          # sorted, distinct, and as many as the span holds: no hour is missing
        self.assertEqual(int((datetime(2026, 10, 3, 4, tzinfo=timezone.utc) - first).total_seconds() // 3600) + 1, ROWS)

    def test_the_local_day_and_month_are_central_time(self):
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo("America/Chicago")
        except Exception as e:  # no time zone data on this machine
            raise unittest.SkipTest(str(e))
        for r in self.rows[::37] + self.rows[-30:]:
            local = datetime.strptime(r[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(tz)
            self.assertEqual((r[1], r[2]), (local.strftime("%Y-%m-%d"), local.strftime("%Y-%m")), r[0])
        days = {}
        for r in self.rows:
            self.assertEqual(r[1][:7], r[2])
            days[r[1]] = days.get(r[1], 0) + 1
        self.assertEqual(sorted(d for d, n in days.items() if n == 23), [f"{y}-03-{d:02d}" for y, d in
                         ((2019, 10), (2020, 8), (2021, 14), (2022, 13), (2023, 12), (2024, 10), (2025, 9), (2026, 8))])
        self.assertEqual(sorted(d for d, n in days.items() if n == 25), [f"{y}-11-{d:02d}" for y, d in
                         ((2018, 4), (2019, 3), (2020, 1), (2021, 7), (2022, 6), (2023, 5), (2024, 3), (2025, 2))])
        self.assertEqual(set(days.values()), {23, 24, 25})               # the first and the last local day are whole too
        self.assertEqual((min(days), max(days)), ("2018-07-01", "2026-10-02"))

    def test_the_values(self):
        months, blank = {}, 0
        for hour, day, month, price, solar, nameplate, flag in self.rows:
            self.assertIn(flag, ("0", "1"))
            p, s, mw = float(price), float(solar), float(nameplate)
            self.assertNotEqual(p, SENTINEL)
            self.assertGreater(mw, 0)
            if s == SENTINEL:
                blank += 1
            else:
                self.assertGreaterEqual(s, 0)                            # no hour of the fleet below zero in this file
                self.assertEqual(s, int(s))                              # EIA reports whole MWh
            self.assertAlmostEqual(p * 400, round(p * 400), places=6)    # the mean of four prices of two decimals
            m = months.setdefault(month, dict(nameplate=set(), flags=set()))
            m["nameplate"].add(nameplate)
            m["flags"].add(flag)
        self.assertEqual(blank, 72)
        self.assertTrue(any(f"is blank ({blank} hours)" in c for c in self.comments))
        self.assertEqual(len(months), 100)
        self.assertEqual((min(months), max(months)), ("2018-07", "2026-10"))
        self.assertTrue(all(len(m["nameplate"]) == 1 and len(m["flags"]) == 1 for m in months.values()))
        self.assertEqual(sorted(m for m, v in months.items() if v["flags"] == {"1"}), [prev_month("2026-09", k) for k in range(11, -1, -1)])
        plates = [float(next(iter(months[m]["nameplate"]))) for m in sorted(months)]
        self.assertEqual((plates[0], plates[-1]), (1571.1, 32759.8))

    def test_the_exporter_refuses_to_run_without_the_tables_and_writes_nothing(self):
        ex = exporter()
        with tempfile.TemporaryDirectory() as tmp:
            out, said = os.path.join(tmp, "trial.csv"), io.StringIO()
            with contextlib.redirect_stdout(said):
                code = ex.main(["--in-dir", os.path.join(tmp, "no_tables"), "--out", out])
            self.assertEqual(code, 0)
            self.assertIn("generator_hourly_export SKIPPED: input tables not on this machine", said.getvalue())
            self.assertEqual(os.listdir(tmp), [])


class TheCsvAndThePagesFilesAgree(unittest.TestCase):
    """The exporter's own check, on the committed CSV and the page's two committed files: no table is needed."""
    @classmethod
    def setUpClass(cls):
        cls.ex = exporter()
        cls.lines = csv_text()[2]
        cls.facts = cls.ex.page_facts()

    def test_every_month_and_every_hour_agrees(self):
        bad, months = self.ex.agree(self.lines, self.facts)
        self.assertEqual(bad, [])
        self.assertEqual(len(months), 100)
        self.assertEqual(sum(1 for m in months.values() if m["cap_n"]), 94)
        self.assertEqual(self.facts["l12"], self.facts["c12"])           # one flag serves both

    def test_the_tolerances_are_the_two_files_rounding(self):
        ex = self.ex
        self.assertLess(ex.TOL_MODEL, 0.000051)                          # half a unit of the snapshot's fourth decimal
        self.assertLess(ex.TOL_CENT, 0.00501)                            # half a cent
        self.assertLess(ex.TOL_MWH, 0.0501)                              # half a tenth of a MWh
        self.assertLess(ex.TOL_PRICE, 0.00501)
        self.assertIn("return float(Decimal(repr(float(v))).quantize(Decimal(\"0.0001\"), rounding=ROUND_HALF_UP))", src("warehouse", "derived", "price_board.py"))
        self.assertIn("round(float(r.sp), 2), round(float(r.g), 1), round(float(r.pg), 2)]", src("warehouse", "derived", "capture_price.py"))
        self.assertIn('s["price"] = [None if pd.isna(v) else round(float(v), 2) for v in hp["p"]]', src("warehouse", "derived", "merchant_revenue.py"))

    def test_the_do_files_rule_for_the_hours_in_a_month_is_the_two_files(self):
        s, cap = self.facts["s"], self.facts["cap_months"]
        for m, r in s["months"].items():
            self.assertEqual(self.ex.rule_hours_in_month(m), r["him"], m)
        for m, rec in cap.items():
            self.assertEqual(self.ex.rule_hours_in_month(m), rec[1], m)

    def test_a_planted_error_is_caught(self):
        lines = list(self.lines)
        i = next(k for k, line in enumerate(lines) if line.startswith("2026-06-15T18:00:00Z,"))
        cells = lines[i].split(",")
        self.assertGreater(float(cells[4]), 0)                           # the fleet is generating at noon
        cells[3] = f"{float(cells[3]) + 1:.4f}"                          # a dollar the hub did not pay
        lines[i] = ",".join(cells)
        bad, _ = self.ex.agree(lines, self.facts)
        said = " | ".join(bad)
        for words in ("model 2026-06 revenue_per_mw", "capture 2026-06 sum of prices", "capture 2026-06 sum of price x generation",
                      "hour 2026-06-15T18:00:00Z"):
            self.assertIn(words, said)
        # a row left out, a blank filled, and a month marked that is not one of the twelve
        k = next(k for k in range(500, len(self.lines)) if f",{SENTINEL}," not in self.lines[k])
        bad, _ = self.ex.agree(self.lines[:k] + self.lines[k + 1:], self.facts)
        self.assertTrue(any("hours" in b for b in bad) and any(b.startswith("hour ") for b in bad))
        j = next(k for k, line in enumerate(self.lines) if f",{SENTINEL}," in line and line[21:28] >= "2019-01")
        filled = list(self.lines)
        filled[j] = filled[j].replace(f",{SENTINEL},", ",0,")
        bad, _ = self.ex.agree(filled, self.facts)
        self.assertTrue(any("hours" in b for b in bad), bad)
        marked = [line[:-1] + "1" if line[21:28] == "2025-09" else line for line in self.lines]
        bad, _ = self.ex.agree(marked, self.facts)
        self.assertTrue(any(b.startswith("in_last_twelve marks") for b in bad))


class TheMirrorAndThePage(unittest.TestCase):
    """The mirror's numbers beside the page's, computed in Python from the two committed files (page_numbers)."""
    @classmethod
    def setUpClass(cls):
        cls.mirror, cls.n = mirror_numbers()
        cls.page = page_numbers()

    def test_each_month_of_the_mirror_is_the_snapshots_month(self):
        want = {r["m"]: r for r in self.page["months"]}
        self.assertEqual(sorted(want), [m["ym"] for m in self.n["months"]])
        for m in self.n["months"]:
            w = want[m["ym"]]
            self.assertEqual(m["revenue_usd_per_mw"], w["per_mw"], m["ym"])          # after the same rounding: the same number
            self.assertEqual(m["hours"], w["hours"], m["ym"])
            self.assertEqual(m["hours_in_month"], w["him"], m["ym"])
            self.assertEqual(m["held"], w["held"], m["ym"])
            self.assertAlmostEqual(m["energy_mwh_per_mw"], w["energy"], delta=0.000051, msg=m["ym"])

    def test_each_month_of_the_mirror_is_the_capture_files_month(self):
        cap, near = self.page["cap_months"], self.page["cap"]["near"]
        got = {m["ym"]: m for m in self.n["months"] if m["capture_hours"]}
        self.assertEqual(sorted(got), sorted(cap))
        for k, rec in cap.items():
            m = got[k]
            self.assertEqual((m["capture_hours"], m["hours_in_month"]), (rec[0], rec[1]), k)
            self.assertEqual(m["capture_counted"], rec[0] >= near * rec[1] - 1e-9, k)
            self.assertAlmostEqual(m["capture_price_sum"], rec[2], delta=0.005001, msg=k)
            self.assertAlmostEqual(m["capture_mwh"], rec[3], delta=0.050001, msg=k)
            self.assertAlmostEqual(m["capture_usd"], rec[4], delta=0.005001, msg=k)

    def test_the_first_headline_number_and_the_long_run_averages(self):
        n, p = self.n, self.page
        self.assertEqual([n["l12_first"], n["l12_last"]], [p["l12"][0], p["l12"][-1]])
        self.assertEqual(n["l12_months"], 12)
        self.assertEqual((n["three_from"], n["last_full_year"], n["three_months"]), (int(p["three"][0]), int(p["three"][2]), 36))
        self.assertEqual((n["full_years"], n["first_full_year"], n["last_full_year"]), (len(p["full"]), int(p["full"][0]), int(p["full"][-1])))
        for mine, theirs in ((n["l12_kw"], p["l12_kw"]), (n["three_kw"], p["three_kw"]), (n["every_kw"], p["every_kw"])):
            self.assertAlmostEqual(mine, theirs, delta=1e-9)
            self.assertEqual(two(mine), two(theirs))
        self.assertEqual([two(n["l12_kw"]), two(n["three_kw"]), two(n["every_kw"])], ["59.85", "102.24", "130.80"])

    def test_the_price_received(self):
        n, p = self.n, self.page
        self.assertEqual(p["key_hub"], "HB_HUBAVG")
        self.assertEqual(p["c12"], p["l12"])                              # the capture price's twelve months are the model's
        self.assertEqual((n["capture_months"], n["capture_hours"]), (12, p["cap_hours"]))
        # the page adds up months rounded to the cent (and the generation to a tenth of a MWh); the mirror adds the hours
        for mine, theirs in ((n["price_received"], p["price"]), (n["flat_average"], p["flat"]), (n["difference"], p["premium"])):
            self.assertAlmostEqual(mine, theirs, delta=1e-5)
            self.assertEqual(two(mine), two(theirs))
        self.assertAlmostEqual(n["difference_pct"], p["pct"], delta=1e-4)
        self.assertEqual(one(n["difference_pct"]), one(p["pct"]))
        self.assertEqual([two(n["price_received"]), two(n["flat_average"]), two(n["difference"]), one(n["difference_pct"])], ["23.27", "32.17", "-8.90", "-27.7"])

    def test_the_debt_and_its_coverage(self):
        n, p = self.n, self.page
        self.assertEqual(n["debt_service"], p["ds"])
        self.assertEqual(n["debt_service"], 7078769)
        self.assertAlmostEqual(n["cover"], p["ttm_last"], delta=1e-9)
        self.assertAlmostEqual(n["newest_window_cover"], p["ttm_last"], delta=1e-9)
        self.assertEqual(n["newest_window"], p["ttm"][-1][0])
        self.assertEqual((n["windows"], n["ttm_under1"], n["ttm_under125"]), (len(p["ttm"]), p["ttm_under1"], p["ttm_under125"]))
        self.assertAlmostEqual(n["ttm_min"], p["ttm_min"], delta=1e-9)
        self.assertEqual([two(n["cover"]), two(n["ttm_min"])], ["0.67", "0.65"])
        windows = {m["ym"]: m["ttm_cover"] for m in n["months"] if m["ttm_cover"] is not None}
        self.assertEqual(sorted(windows), [m for m, _ in p["ttm"]])
        for m, v in p["ttm"]:
            self.assertAlmostEqual(windows[m], v, delta=1e-9, msg=m)

    def test_month_by_month(self):
        n, p = self.n, self.page
        self.assertEqual((n["n"], n["first_held"], n["last_held"]), (p["n"], p["first"], p["last"]))
        self.assertEqual((n["under1"], n["under125"]), (p["under1"], p["under125"]))
        self.assertAlmostEqual(n["annual_mean"], p["annual"], delta=1e-6)
        self.assertEqual((n["median_month"], n["p10_month"]), (p["median"]["m"], p["p10"]["m"]))
        self.assertAlmostEqual(n["median_usd"], p["median"]["revenue"], delta=1e-6)
        self.assertAlmostEqual(n["p10_usd"], p["p10"]["revenue"], delta=1e-6)
        self.assertEqual([m for m, _ in n["worst"]], [r["m"] for r in p["worst"]])
        for (_, v), r in zip(n["worst"], p["worst"]):
            self.assertAlmostEqual(v, r["revenue"], delta=1e-6)
        self.assertEqual((n["n"], n["under1"], n["under125"], n["windows"], n["ttm_under1"], n["ttm_under125"]), (99, 62, 71, 88, 33, 36))

    def test_the_lines_the_mirror_prints(self):
        out = self.mirror.report(self.n)
        for line in ("the last twelve months: 2025-10 to 2026-09", "revenue, last twelve months, USD per kW: 59.85",
                     "the last three full years: 2023 to 2025, months held in them: 36",
                     "long-run average of the last three full years, USD per kW a year: 102.24", "full years held: 7, 2019 to 2025",
                     "long-run average of every full year held, USD per kW a year: 130.80", "hours used for the capture price: 8736",
                     "price received, weighted by generation, USD per MWh: 23.27", "flat average over the same hours, USD per MWh: 32.17",
                     "difference, USD per MWh: -8.90", "difference, percent of the flat average: -27.7", "annual debt payments, USD: 7,078,769",
                     "debt coverage, last twelve months, times: 0.67", "the newest twelve-month window ends 2026-09, coverage, times: 0.67",
                     "twelve-month windows: 88", "lowest twelve-month coverage, times: 0.65", "twelve-month windows under 1.0 times: 33",
                     "twelve-month windows under 1.25 times: 36", "months held: 99, 2018-07 to 2026-09",
                     "months held that covered less than 1.0 times: 62", "months held that covered less than 1.25 times: 71",
                     "the year's average, twelve times the mean month, USD for 100 MW: 12,216,826.39",
                     "median month: 2018-09, USD for 100 MW: 550,484.85", "10th-percentile month, nearest rank: 2020-12, USD for 100 MW: 240,213.49",
                     "worst month 1: 2024-02, USD for 100 MW: 139,298.97", "worst month 2: 2026-02, USD for 100 MW: 148,707.24",
                     "worst month 3: 2023-02, USD for 100 MW: 175,323.73"):
            self.assertIn(line, out)

    def test_the_mirror_reads_nothing_but_the_csv_and_the_standard_library(self):
        text = src("site", "public", "seller", MIRROR_NAME)
        imports = sorted(set(re.findall(r"(?m)^(?:import|from) (\w+)", text)))
        self.assertEqual(imports, ["calendar", "csv", "math", "os", "sys"])
        for word in ("merchant_snapshot", "capture.json", "urlopen", "requests", "subprocess"):
            self.assertNotIn(word, text)


class ThePagesOwnLibrary(unittest.TestCase):
    """The same numbers from node on site/lib/merchant.ts, seller2.ts and capture.ts and the two committed files."""
    @classmethod
    def setUpClass(cls):
        cls.lib = node("""
import fs from "node:fs";
const M = await import("./lib/merchant.ts");
const S = await import("./lib/seller2.ts");
const C = await import("./lib/capture.ts");
const snap = JSON.parse(fs.readFileSync("./data/merchant_snapshot.json", "utf-8"));
const cap = JSON.parse(fs.readFileSync("./data/seller/capture.json", "utf-8"));
const x = M.inputsOf({});
const ms = M.months(snap, x), sm = M.summary(ms), t = M.ttm(ms, x.ds);
const s = S.spans(M.months(snap, { ...x, mw: 1, mwh: 0, ds: 0, fom: 0 }));
const hub = C.hubOf(cap, x.iso, undefined);
const out = { key: M.inputsKey(x), hub: hub.id, spans: s, sentence: S.sentence({ grid: x.iso, asset: x.asset }, s), capture: C.twelve(hub.rt.solar, cap.near),
  first: sm.first, last: sm.last, median: sm.median.m, p10: sm.p10.m, worst: sm.worst.map((r) => r.m), windows: t.length, newest: t.at(-1).m, stat: {} };
for (const k of ["n", "median", "p10", "worst:0", "worst:1", "worst:2", "ds", "under1", "under125", "ttm_last", "ttm_min", "ttm_under1", "ttm_under125", "annual_mean"]) out.stat[k] = M.stat(snap, x, k);
console.log(JSON.stringify(out));
""")
        cls.mirror, cls.n = mirror_numbers()

    def test_the_default_case_is_the_one_exported(self):
        self.assertEqual(self.lib["key"], "iso=ercot&asset=solar&mw=100&mwh=0&ds=7078769&hr=10.725&vom=4.25&fom=12.5")
        self.assertEqual(self.lib["hub"], "HB_HUBAVG")

    def test_the_spans_and_the_sentence(self):
        n, s = self.n, self.lib["spans"]
        self.assertEqual((s["twelve"]["from"], s["twelve"]["to"]), (n["l12_first"], n["l12_last"]))
        self.assertEqual(s["threeYears"], [str(n["three_from"] + k) for k in range(3)])
        self.assertEqual(s["everyYears"], [str(y) for y in range(n["first_full_year"], n["last_full_year"] + 1)])
        self.assertEqual(len(s["everyYears"]), n["full_years"])
        for mine, theirs in ((n["l12_kw"], s["twelve"]["revenue_kw"]), (n["three_kw"], s["three"]["revenue_kw"]), (n["every_kw"], s["every"]["revenue_kw"])):
            self.assertAlmostEqual(mine, theirs, delta=1e-9)
            self.assertEqual(two(mine), two(theirs))
        self.assertEqual(self.lib["sentence"], f"Over the last twelve months, Oct 2025 to Sep 2026, a merchant solar plant in ERCOT priced at the hub average "
                         f"earned USD {two(n['l12_kw'])} per kW. The long-run average of {n['three_from']} to {n['last_full_year']} was USD {two(n['three_kw'])} a year, "
                         f"and of the {n['full_years']} full years held ({n['first_full_year']} to {n['last_full_year']}) USD {two(n['every_kw'])}.")

    def test_the_price_received(self):
        n, c = self.n, self.lib["capture"]
        self.assertEqual((c["from"], c["to"], c["hours"]), (n["l12_first"], n["l12_last"], n["capture_hours"]))
        for mine, theirs in ((n["price_received"], c["price"]), (n["flat_average"], c["flat"]), (n["difference"], c["premium"])):
            self.assertAlmostEqual(mine, theirs, delta=1e-5)
            self.assertEqual(two(mine), two(theirs))
        self.assertEqual(one(n["difference_pct"]), one(c["pct"]))

    def test_the_debt_the_coverage_and_the_months(self):
        n, st = self.n, self.lib["stat"]
        for mine, k in ((n["debt_service"], "ds"), (n["n"], "n"), (n["under1"], "under1"), (n["under125"], "under125"), (n["ttm_under1"], "ttm_under1"),
                        (n["ttm_under125"], "ttm_under125")):
            self.assertEqual(mine, st[k], k)
        self.assertEqual((n["windows"], n["newest_window"]), (self.lib["windows"], self.lib["newest"]))
        self.assertEqual((n["first_held"], n["last_held"]), (self.lib["first"], self.lib["last"]))
        for mine, k in ((n["cover"], "ttm_last"), (n["newest_window_cover"], "ttm_last"), (n["ttm_min"], "ttm_min")):
            self.assertAlmostEqual(mine, st[k], delta=1e-9, msg=k)
            self.assertEqual(two(mine), two(st[k]), k)
        self.assertEqual((n["median_month"], n["p10_month"], [m for m, _ in n["worst"]]), (self.lib["median"], self.lib["p10"], self.lib["worst"]))
        for mine, k in ((n["median_usd"], "median"), (n["p10_usd"], "p10"), (n["annual_mean"], "annual_mean"), (n["worst"][0][1], "worst:0"),
                        (n["worst"][1][1], "worst:1"), (n["worst"][2][1], "worst:2")):
            self.assertAlmostEqual(mine, st[k], delta=1e-6, msg=k)
            self.assertEqual(two(mine), two(st[k]), k)


class House(unittest.TestCase):
    def test_no_em_dash_in_what_was_written(self):
        for f in FILES:
            p = os.path.join(ROOT, *f.split("/"))
            if os.path.exists(p):
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
        for f in ("generator_hourly_export.py", "test_session183_replication.py", MIRROR_NAME):
            self.assertEqual(len(names.get(f, [])), 1, names.get(f))

    def test_the_exporter_writes_nothing_into_the_warehouse_and_asks_no_one(self):
        text = src("warehouse", "derived", "generator_hourly_export.py")
        for word in ("write_table", "write_csv", "_require_lock", "update_sources", "write_status", "set_out_dir", "subprocess"):
            self.assertNotIn(word, text, word)
        for word in ("anthropic", "requests.", "urlopen", "http.client"):
            self.assertNotIn(word, text.lower(), word)
        # it reuses the two builders' own functions and holds none of their arithmetic
        for call in ("mr.build_iso(", "mr.read_gens()", "cx.read_one(", "cx.hourly_side(", "cx.mix_hours(", "cx.readable(", "cx.last_twelve("):
            self.assertIn(call, text, call)
        self.assertEqual(os.path.basename(os.path.dirname(os.path.abspath(CSV_PATH))), "seller")


if __name__ == "__main__":
    unittest.main()
