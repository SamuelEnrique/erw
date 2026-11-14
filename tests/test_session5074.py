"""Session 5074 (chain 243, portable laptop window P1): the Python replication's parity with every Stata do-file of the
five tools, so that Samuel's Stata run confirms what is already shown here rather than unblocking it.

- The three decision tools (battery, generator, datacenter): each do-file has a Python mirror beside it
  (site/public/<page>/erw_2026_<tool>_replication.py, "step for step"). The mirror is run on the page's public file;
  every figure of replication/<tool>/page_figures.json (each a check-values key, or a scenario figure named) is read
  from the mirror's own printed line and meets the page within its tolerance; every such line is a `display` of the
  public do-file and of replication/<tool>/replicate.do, with the same number of decimals and the same thousands
  separator; and the values each replicate.do states in its header as the mirror's output are what the mirror prints.
- Research (replication/analysis/): every figure replicate.py computes is set by replicate.do from a scalar it defines,
  for the same card and field, and every figure replicate.do sets is one the page prints.
- The Grid (replication/grid/): every network and gravity figure is computed by replicate.py on the committed snapshot
  and meets the page's figure; every family of check keys the page prints (net|tie, net|export, ..., the carbon series)
  is built by replicate.do; every Ask figure is stated by replicate_ask.do with the page's value and tolerance.
No network, no model, no Stata.
"""
import importlib.util
import io
import json
import os
import re
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISPLAY = re.compile(r'display "([^"]*?): "\s*(?:%(\d+)\.(\d+)f(c?))?')


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def module(name, *parts):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def segments(line):
    """A printed line "label: v1, words: v2" as (label, [the leading token of each value segment])."""
    parts = line.split(": ")
    return parts[0], [p.split(",")[0].strip() if not re.match(r"-?[\d,]+(\.\d+)?$", p.strip()) else p.strip() for p in parts[1:]]


def number(token):
    return float(token.replace(",", ""))


def displays(do_text):
    """Every `display` of a do-file as a pattern of the whole line it prints: its quoted words as they stand (a local
    macro inside them matches a word), anything between them (a scalar, a format and a value) as a value; with the
    format of a display that prints one value after its label (decimals, thousands separator), else None."""
    out = []
    for raw in do_text.splitlines():
        s = re.sub(r"^if .+? (?=display )", "", raw.strip())   # "if s_irr != . display ..." prints as a display
        if not s.startswith("display "):
            continue
        words = re.findall(r'"([^"]*)"', s)
        if not words:
            continue
        parts = []
        for w in words:
            p = re.escape(w).replace(r"\`", "`").replace(r"\'", "'")
            parts.append(re.sub(r"`\w+'", r"[^,:]+", p))
        rest = s[len("display "):]
        ends_with_value = not rest.rstrip().endswith('"')
        pattern = "(.+?)".join(parts) + ("(.+)" if ends_with_value else "")
        one = DISPLAY.match(s)
        fmt = None
        if one and len(words) == 1 and one.group(3):
            fmt = (int(one.group(3)), one.group(4) == "c")
        out.append((re.compile(pattern + r"$"), words[0], fmt))
    return out


class Decision:
    page = tool = ""
    DAILY = False   # True when the public file moves with the data machine's daily run (the datacenter's)
    ALIASES = {}    # a mirror line's label -> the do-file's label for the same figure
    MAP = {}   # check key (or scenario figure) -> (the mirror line's label, a prefix of its second segment or None, the value's segment)

    @classmethod
    def setUpClass(cls):
        m = module(f"mirror_{cls.tool}", "site", "public", cls.page, f"erw_2026_{cls.tool}_replication.py")
        path = os.path.join(ROOT, "site", "public", cls.page, m.CSV_NAME)
        if not os.path.exists(path):
            raise unittest.SkipTest("the public file is not in this copy")
        buf = io.StringIO()
        with redirect_stdout(buf):   # as the mirror's own __main__ runs it
            rows = m.read(path)
            n = m.numbers(rows)
            carbon_name = getattr(m, "CARBON_NAME", None)
            if carbon_name:
                n["rows"] = rows
                carbon_path = os.path.join(os.path.dirname(path), carbon_name)
                if os.path.exists(carbon_path):
                    n.update(m.carbon(carbon_path, n))
            lines = list(m.report(n))
        cls.lines = [l for l in lines if ": " in l]
        cls.figs = json.loads(read("replication", cls.tool, "page_figures.json"))["figures"]
        cls.public_do = read("site", "public", cls.page, f"erw_2026_{cls.tool}_replication.do")
        cls.rep_do = read("replication", cls.tool, "replicate.do")

    def line(self, label, second):
        for l in self.lines:
            lab, vals = segments(l)
            if lab == label and (second is None or (vals and l.split(": ")[1].startswith(second))):
                return l, vals
        self.fail(f"the mirror prints no line {label!r}")

    def test_every_page_figure_is_a_mirror_line(self):
        self.assertEqual({f["key"] for f in self.figs}, set(self.MAP))
        for f in self.figs:
            label, second, k = self.MAP[f["key"]]
            _, vals = self.line(label, second)
            got = number(vals[k - 1])
            self.assertAlmostEqual(got, f["page"], delta=f["tolerance"] + 1e-9, msg=(self.tool, f["key"], got))

    def test_every_mirror_line_is_a_display_of_both_do_files(self):
        public, rep = displays(self.public_do), displays(self.rep_do)
        self.assertGreaterEqual(len(self.lines), 20, self.tool)
        for l in self.lines:
            label = l.split(": ")[0]
            if label in self.ALIASES:   # the do-file's words for the same figure, its own comment saying why
                l = self.ALIASES[label] + ": " + l.split(": ", 1)[1].split(",")[0]
            hits = [d for d in public if d[0].match(l)]
            self.assertTrue(hits, (self.tool, l[:90]))
            self.assertTrue([d for d in rep if d[0].match(l)], (self.tool, l[:90], "replicate.do"))
            fmt = next((d[2] for d in hits if d[2]), None)
            value = l.split(": ", 1)[1]
            if fmt and l.count(": ") == 1 and re.match(r"-?[\d,]+(\.\d+)?$", value):
                dec, comma = fmt
                shown = len(value.split(".")[1]) if "." in value else 0
                self.assertEqual(shown, dec, (self.tool, l[:90]))
                if abs(number(value)) >= 1000:
                    self.assertEqual("," in value, comma, (self.tool, l[:90]))

    def test_the_do_files_expected_values_are_the_mirrors(self):
        stated = [l[1:].strip() for l in self.rep_do.splitlines() if l.startswith("*   ") and ": " in l]
        self.assertGreaterEqual(len(stated), 5, self.tool)
        labels = {l.split(": ")[0] for l in self.lines}
        for s in stated:
            if self.DAILY:   # the public file moves with the data machine's daily run: the header's values are of their day
                self.assertIn(s.split(": ")[0], labels, (self.tool, s[:90]))
            else:
                self.assertIn(s, self.lines, (self.tool, s[:90]))


class Battery(Decision, unittest.TestCase):
    page, tool = "battery", "battery"
    MAP = {
        "bs|l12_kw:total": ("last twelve months, all streams, USD per kW", None, 1),
        "bs|l12:total": ("last twelve months, total, USD for 100 MW", None, 1),
        "bs|l12:energy": ("last twelve months, energy, USD for 100 MW", None, 1),
        "bs|l12:ancillary": ("last twelve months, ancillary, USD for 100 MW", None, 1),
        "bs|l12:regup": ("last twelve months, regup, USD for 100 MW", None, 1),
        "bs|l12:regdn": ("last twelve months, regdn, USD for 100 MW", None, 1),
        "bs|l12:rrs": ("last twelve months, rrs, USD for 100 MW", None, 1),
        "bs|l12:ecrs": ("last twelve months, ecrs, USD for 100 MW", None, 1),
        "bs|l12:nspin": ("last twelve months, nspin, USD for 100 MW", None, 1),
        "bs|l12_share:ancillary": ("share from ancillary services, percent", None, 1),
        "scenario A's debt payment": ("annual debt payments, USD", None, 1),
        "bs|cover": ("debt coverage, last twelve months, times", None, 1),
        "scenario A's NPV": ("scenario A, NPV at the hurdle rate, USD per kW", None, 1),
        "scenario A's IRR": ("scenario A, IRR, percent a year", None, 1),
        "scenario A's breakeven toll": ("scenario A, breakeven toll, USD per kW-month", None, 1),
        "scenario A's merchant tail": ("scenario A, merchant tail, years", None, 1),
        "bs|p10_36": ("a bad month", None, 2),
        "bs|n36": ("months held of the 36", None, 1),
        "bs|year:2024:energy": ("calendar year 2024, months held", None, 2),
        "bs|year:2024:ancillary": ("calendar year 2024, months held", None, 3),
        "bs|year:2025:energy": ("calendar year 2025, months held", None, 2),
        "bs|year:2025:ancillary": ("calendar year 2025, months held", None, 3),
    }


class Generator(Decision, unittest.TestCase):
    page, tool = "seller", "generator"
    MAP = {
        "ms|G|twelve|revenue": ("revenue, last twelve months, USD per kW", None, 1),
        "ms|G|three|revenue": ("long-run average of the last three full years, USD per kW a year", None, 1),
        "ms|G|every|revenue": ("long-run average of every full year held, USD per kW a year", None, 1),
        "cap|ercot|HB_HUBAVG|rt|solar|l12|price": ("price received, weighted by generation, USD per MWh", None, 1),
        "cap|ercot|HB_HUBAVG|rt|solar|l12|flat": ("flat average over the same hours, USD per MWh", None, 1),
        "cap|ercot|HB_HUBAVG|rt|solar|l12|rate": ("capture rate, percent of the flat average", None, 1),
        "mr|G|ds": ("annual debt payments, USD", None, 1),
        "mr|G|ttm_last": ("debt coverage, last twelve months, times", None, 1),
        "ms|G|twelve|energy": ("energy sold, last twelve months, MWh per MW", None, 1),
        "scenario A's contract price": ("contract price at which coverage reaches 1.25 times, USD per MWh", None, 1),
        "scenario A's NPV": ("NPV at the hurdle rate, USD million for 100 MW", None, 1),
        "scenario A's breakeven PPA price": ("breakeven PPA price, the whole of the energy for the PPA term, USD per MWh", None, 1),
        "scenario A's worst month": ("worst month 1", None, 2),
    }


class Datacenter(Decision, unittest.TestCase):
    page, tool = "datacenter", "datacenter"
    DAILY = True
    # The do-file counts the carbon file's hours and takes the price as held throughout the window (its comment says
    # so); the mirror checks each hour against the prices. The test below holds the two counts and means equal.
    ALIASES = {"hours of the hourly window the price and the intensity are both held": "hours of the hourly window"}

    def test_the_hourly_window_as_the_do_file_counts_it(self):
        import csv
        path = os.path.join(ROOT, "site", "public", "datacenter", "erw_2026_datacenter_carbon.csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(l for l in f if not l.startswith("#")))
        kg = [float(r["kg_co2_per_mwh"]) for r in rows if r["kind"] == "hour" and r["kg_co2_per_mwh"] not in ("", None)]
        _, hours = self.line("hours of the hourly window the price and the intensity are both held", None)
        _, mean = self.line("a flat load's own hours over them, kg CO2 per MWh (the grid's mean)", None)
        self.assertEqual(len(kg), int(number(hours[0])))
        self.assertAlmostEqual(sum(kg) / len(kg), number(mean[0]), delta=0.005)

    MAP = {
        "a|price, l12_per": ("market energy, a flat load, last twelve months, USD per MWh", None, 1),
        "a|bill": ("cost for 100 MW, USD", None, 1),
        "a|gpu": ("power per GPU-hour, USD", None, 1),
        "the page's text": ("GPUs that 100 MW powers", None, 1),
        "l12_per on ?buy=da": ("bought day-ahead, a flat load, the same twelve months, USD per MWh", None, 1),
        "a|bad": ("a bad month, nearest rank 4", None, 2),
        "dc|...|scarce:hours": ("hours of the last twelve months at or above USD 1000 per MWh", None, 1),
        "dc|...|scarce:flat_usd": ("what a flat load of 100 MW paid in them, USD", None, 1),
        "dc|...|co2:l12:kg:flat": ("this load's carbon, last twelve months at the grid's monthly average, kg CO2 per MWh", None, 1),
        "dc|...|co2:l12:tonnes:flat": ("tonnes of CO2 a year for 100 MW", None, 1),
        "dc|...|co2:window:hours": ("hours of the hourly window the price and the intensity are both held", None, 1),
        "dc|...|co2:window:flat": ("a flat load's own hours over them, kg CO2 per MWh (the grid's mean)", None, 1),
        "series|price_years_by_window|ercot:LZ_NORTH|datacenter_flat_rt_year_2016": ("year 2016", "months that count", 2),
        "series|price_years_by_window|ercot:LZ_NORTH|datacenter_flat_rt_year_2021": ("year 2021", "months that count", 2),
    }


class Analysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (os.path.isdir(os.path.join(ROOT, "site", "public", "findings")) and os.path.isdir(os.path.join(ROOT, "site", "data", "findings"))):
            raise unittest.SkipTest("the findings' downloads are not in this copy")
        try:
            import pandas  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("pandas is not installed")
        r = module("replicate_analysis_5074", "replication", "analysis", "replicate.py")
        b = module("figures_of_the_page_5074", "replication", "analysis", "figures_of_the_page.py")
        a = r.load_json(os.path.join(ROOT, "replication", "analysis", "assumptions.json"))
        committed = r.load_json(os.path.join(ROOT, "replication", "analysis", "page_figures.json"))
        cls.page = json.loads(b.build(committed["written_for_day"])[0])
        csv_base, week_base = r.default_bases()
        cls.rows = r.compare(r.compute(csv_base, week_base, cls.page, a), cls.page)
        cls.do = read("replication", "analysis", "replicate.do")
        cls.sets = {(c, f): s for s, c, f in re.findall(r'replace replication = scalar\((\w+)\) if card == "(\w+)" & field == "(\w+)"', cls.do)}

    def test_every_figure_python_computes_the_do_file_sets(self):
        # the week's chart changes every week: replicate.py computes it from the week's file, and the do-file says so
        computed = {(f["card"], f["field"]) for f, status, _, _ in self.rows if status == "yes" and f["card"] != "chart_of_the_week"}
        self.assertGreaterEqual(len(computed), 60)
        self.assertEqual(sorted(computed - set(self.sets)), [])
        self.assertIn('"not computed here (the week\'s chart: replicate.py)" if card == "chart_of_the_week"', self.do)

    def test_every_scalar_the_do_file_sets_is_defined_before_the_comparison(self):
        head = self.do[: self.do.index("the comparison with the page")]
        for (card, field), s in self.sets.items():
            self.assertRegex(head, rf"\bscalar (define )?{s}\b", (card, field, s))

    def test_every_figure_the_do_file_sets_is_one_the_page_prints(self):
        page = {(f["card"], f["field"]) for f in self.page["figures"]}
        self.assertEqual(sorted(set(self.sets) - page), [])


class Grid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = module("replicate_grid_5074", "replication", "grid", "replicate.py")
        cls.a = json.loads(read("replication", "grid", "assumptions.json"))
        cls.committed = json.loads(read("replication", "grid", "page_figures.json"))
        snap = json.loads(read("replication", "grid", "snapshot.json"))
        _, _, _, cls.mine = cls.r.network(snap, {}, cls.a)
        cls.do = read("replication", "grid", "replicate.do")
        cls.ask_do = read("replication", "grid", "replicate_ask.do")

    def test_every_network_figure_is_computed_by_python_and_meets_the_page(self):
        figs = [f for f in self.committed["figures"] if f["group"] in ("network", "gravity") and not f["held"]]
        self.assertGreaterEqual(len(figs), 40)
        for f in figs:
            self.assertIn(f["check"], self.mine, f["check"])
            self.assertAlmostEqual(self.mine[f["check"]], f["raw"], delta=f["tolerance"] + 1e-9, msg=f["check"])

    def test_every_family_of_keys_is_built_by_the_do_file(self):
        families = {"|".join(f["check"].split("|")[:2]) for f in self.committed["figures"] if f["group"] != "ask"}
        built = set(re.findall(r'check = "(\w+\|\w+)', self.do))
        self.assertEqual(sorted(families - built), [])

    def test_every_ask_figure_is_stated_by_the_ask_do_file(self):
        """A plain query is rebuilt in Stata with the page's value and tolerance; a grouped query or a compare is said
        to be replicate.py's, and a held table "license needed", each on its own comment line."""
        asks = [f for f in self.committed["figures"] if f["group"] == "ask"]
        self.assertGreaterEqual(len(asks), 60)
        stated = 0
        for f in asks:
            block = "|".join(f["check"].split("|")[:3])
            if re.search(r"^\* " + re.escape(block) + r": (.*replicate\.py only|license needed.*not computed)$", self.ask_do, re.M):
                self.assertNotIn(f'display "{f["check"]}: ', self.ask_do, f["check"])
                continue
            stated += 1
            line = re.search(re.escape(f'display "{f["check"]}: the answer states ') + r".*", self.ask_do)
            self.assertIsNotNone(line, f["check"])
            line = line.group(0)
            tol = float(re.search(r"<= ([0-9.e-]+),", line).group(1))
            self.assertAlmostEqual(tol, f["tolerance"], delta=1e-6, msg=f["check"])
            value = re.search(r"min\(abs\(abs\(v_value\) - ([-0-9.e]+)\)", line).group(1)
            self.assertAlmostEqual(float(value), abs(float(f["raw"])), delta=1e-9, msg=f["check"])
        self.assertGreaterEqual(stated, 24)


if __name__ == "__main__":
    unittest.main()
