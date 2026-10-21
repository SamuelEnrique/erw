"""Session 535 (chain 024, 21 October 2026): an R reader beside the Python and Stata readers of /api/download (roadmap v4
draft, tool 19). The route answers ?as=r with a base-R script that reads the same CSV from the site's address, prints its
provenance lines ("#") and loads the rows after them; the downloads line offers it beside the other two; the check of the
downloads line checks it the same way. Energy Research Warehouse (ERW).

No R interpreter was on the machine that wrote this (samueloldlaptop): the script is tested by its text here, rendered from
the route's own source. Where an Rscript is on PATH (or named by ERW_RSCRIPT), test_runs_in_r runs the rendered script on
a fixture CSV and reads what it prints; elsewhere that one test is skipped and says why."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


ROUTE = src("site", "app", "api", "download", "route.ts")
COMPONENT = src("site", "components", "tool", "TableDownloads.tsx")
CHECK = src("site", "scripts", "check-table-downloads.mjs")
ORIGIN = "https://erw.example.org"


def r_lines():
    """The R branch of readerText, its array's elements in order, as written in the route (JS strings or templates)."""
    body = ROUTE[ROUTE.index('  if (as === "r") {'):]
    body = body[body.index("return [") + len("return ["):body.index('].join("\\n");')]
    out = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        assert line.endswith(","), line
        out.append(line[:-1])
    return out


def render(table, origin=ORIGIN):
    """The R script the route answers for a table, rendered as the route renders it."""
    url = f"{origin}/api/download?table={table}"
    name = table if re.match(r"^[a-z]", table) else f"erw_{table}"
    lines = []
    for el in r_lines():
        if el.startswith("`"):
            self_ = el[1:-1]
            lines.append(self_.replace("${url}", url).replace("${name}", name).replace("${table}", table))
        else:
            lines.append(json.loads(el))   # a JS double-quoted string with \" and \\n escapes reads as JSON
    return "\n".join(lines)


class TheRoute(unittest.TestCase):
    def test_r_is_answered_after_the_same_checks_as_the_other_two(self):
        at = ROUTE.index('if (as === "r") return reader(table, as, new URL(req.url).origin);')
        self.assertGreater(at, ROUTE.index('if (as === "py" || as === "do") return reader(table, as, new URL(req.url).origin);'))
        self.assertGreater(at, ROUTE.index("is not in the site's live set"))
        self.assertGreater(at, ROUTE.index('const lim = await limited(req, "download", 60, 3600);'))
        self.assertGreater(at, ROUTE.index("if (licenseNeeded(table))"))
        self.assertIn('type Reader = "py" | "do" | "r";', ROUTE)
        # the same attachment header as the other two: erw_<table>.r
        self.assertIn('"Content-Disposition": `attachment; filename="erw_${table}.${as}"`', ROUTE)
        self.assertNotIn("export function readerText", ROUTE)

    def test_the_script_names_this_site_s_csv_and_the_table(self):
        r = render("ercot_as_prices")
        self.assertIn(f'URL <- "{ORIGIN}/api/download?table=ercot_as_prices"', r)
        self.assertIn("ercot_as_prices <- read.csv(", r)
        self.assertIn("print(dim(ercot_as_prices))", r)
        self.assertTrue(r.startswith("# Energy Research Warehouse (ERW): read the table ercot_as_prices"))
        # a name an R variable cannot take (none on 21 October 2026) is read into erw_<table>
        self.assertIn("erw_2x_test <- read.csv(", render("2x_test"))

    def test_base_r_only_and_nothing_installed(self):
        r = render("eia_fuel_spot_prices")
        for bad in ("library(", "require(", "install.packages", "::", "source(", "system(", "Sys.setenv", "download.file"):
            self.assertNotIn(bad, r, bad)
        code = "\n".join(l for l in r.splitlines() if not l.startswith("#"))
        calls = set(re.findall(r"([A-Za-z_][A-Za-z0-9_.]*)\(", code))
        # base and utils (utils is attached by Rscript and by R itself): startsWith is base R from 3.3.0
        allowed = {"options", "max", "getOption", "readLines", "startsWith", "length", "writeLines", "seq_len", "read.csv",
                   "seq_along", "print", "dim", "head"}
        self.assertEqual(calls - allowed, set(), calls)

    def test_it_skips_the_provenance_and_computes_nothing(self):
        r = render("eia_fuel_spot_prices")
        self.assertIn('while (n < length(lines) && startsWith(lines[n + 1L], "#")) n <- n + 1L', r)
        # the provenance printed, each line ended (cat(..., sep = "\n") left the last unended, and dim() printed on it)
        self.assertIn("writeLines(lines[seq_len(n)])", r)
        self.assertNotIn("cat(", r)
        # the rows after the provenance; seq_along(lines) > n, not lines[-seq_len(n)], which is empty when n is 0
        self.assertIn("read.csv(text = lines[seq_along(lines) > n]", r)
        self.assertNotIn("-seq_len", r)
        self.assertNotIn("comment.char", r)                         # a value that holds "#" is read whole
        self.assertIn('na.strings = ""', r)                         # the route writes a null as an empty cell
        self.assertIn("stringsAsFactors = FALSE", r)
        self.assertIn("check.names = FALSE", r)
        self.assertIn('readLines(URL, warn = FALSE, encoding = "UTF-8")', r)
        self.assertIn('old <- options(timeout = max(300, getOption("timeout")))', r)   # the largest table is some 340 reads
        self.assertIn("options(old)", r)
        code = "\n".join(l for l in r.splitlines() if not l.startswith("#"))
        for op in (" * ", " / ", "sum(", "mean(", "aggregate(", "round("):
            self.assertNotIn(op, code, op)

    def test_the_script_is_well_formed(self):
        r = render("eia_fuel_spot_prices")
        code = "\n".join(l for l in r.splitlines() if not l.startswith("#"))
        no_strings = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
        self.assertEqual(code.count('"') % 2, 0)
        for o, c in ("()", "[]", "{}"):
            self.assertEqual(no_strings.count(o), no_strings.count(c), o + c)
        self.assertTrue(r.endswith("\n") or r.endswith(")"), repr(r[-20:]))
        self.assertNotIn(DASH, r)
        self.assertNotIn("\t", r)

    @unittest.skipUnless(os.environ.get("ERW_RSCRIPT") or shutil.which("Rscript"),
                         "no R interpreter on this machine (no Rscript on PATH, ERW_RSCRIPT not set): the R reader is tested by its text")
    def test_runs_in_r(self):
        rscript = os.environ.get("ERW_RSCRIPT") or shutil.which("Rscript")
        d = tempfile.mkdtemp(prefix="erw-r-")
        csv_path = os.path.join(d, "t.csv").replace("\\", "/")
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            f.write("# source: a fixture\n# retrieved_at: 2026-10-21T00:00:00Z\n"
                    "entity,variable,ts_utc,value,source_url\n"
                    'a,x,2026-10-01T00:00:00Z,1.5,https://example.org/p#q\n'
                    'b,x,2026-10-01T00:00:00Z,,"https://example.org/a,b"\n')
        script = re.sub(r'^URL <- ".*"$', f'URL <- "{csv_path}"', render("fixture_table"), flags=re.M)
        path = os.path.join(d, "erw_fixture_table.r")
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        out = subprocess.run([rscript, "--vanilla", path], capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertTrue(out.stdout.startswith("# source: a fixture\n# retrieved_at:"), out.stdout)
        self.assertRegex(out.stdout, r"(?m)^\[1\] 2 5\r?$")
        self.assertIn("https://example.org/p#q", out.stdout)


class TheLineAndTheCheck(unittest.TestCase):
    def test_the_line_offers_r_beside_python_and_stata(self):
        c = COMPONENT
        self.assertEqual(c.count('data-download="r"'), 1)
        self.assertIn('<a href={`/api/download?table=${t}&as=r`} download data-download="r">R</a>', c)
        self.assertLess(c.index('data-download="stata"'), c.index('data-download="r"'))
        for kind in ('data-download="csv"', 'data-download="python"', 'data-download="stata"'):
            self.assertEqual(c.count(kind), 1, kind)

    def test_the_check_checks_r_the_same_way(self):
        self.assertIn('&amp;as=r"/g', CHECK)
        self.assertIn("JSON.stringify(csvs) === JSON.stringify(rs)", CHECK)
        self.assertIn('for (const as of ["py", "do", "r"])', CHECK)
        self.assertIn("CHECK_DOWNLOADS_RSCRIPT", CHECK)
        self.assertIn('execFileSync(rscript, ["--vanilla", f]', CHECK)

    def test_the_guide_and_the_briefing_say_so(self):
        guide = src("docs", "guide.md")
        self.assertIn("| R | `/api/download?table=<table>&as=r` |", guide)
        self.assertIn("the three readers every page's downloads line offers", guide)
        self.assertIn("not yet run against the route", guide)
        llms = re.sub(r"\s+", " ", src("package", "llms.txt"))
        self.assertIn("&as=r for a Python, Stata or base-R reader", llms)
        self.assertIn("&as=r for a Python, Stata or base-R reader", src("site", "lib", "chat", "spec.json").replace("\\n", " "))

    def test_no_em_dash_in_the_files_of_this_session(self):
        for parts in (("site", "app", "api", "download", "route.ts"), ("site", "components", "tool", "TableDownloads.tsx"),
                      ("site", "scripts", "check-table-downloads.mjs"), ("docs", "guide.md"), ("tests", "test_session535.py")):
            self.assertNotIn(DASH, src(*parts), parts)


if __name__ == "__main__":
    unittest.main()
