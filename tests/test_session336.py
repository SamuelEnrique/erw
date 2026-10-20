"""Session 336: the two red steps of 20 October that were in our code.

Energy Research Warehouse (ERW). The manual daily run 39344868297 finished green but wrote two failed rows of its own:

  1. The package test test_large_table_by_partition[nyiso_zone_load_hourly] ("assert (False)"). The runner rebuilds the
     held NYISO table from the archive each day (warehouse/restore_tables.py, session 305), whose note line ("Rebuilt
     from the ERW archive by warehouse/restore_tables.py (session 305), ...") the test's own_first_line did not set
     aside (it knew only restore.py's), and each rebuild stacked one more such line on the last (12, 13, 14, 15 header
     lines in the archive's run log, 15 to 20 October). The test sets aside any rebuild line; both rebuilders drop the
     run's own rebuild lines before adding theirs.
  2. eia930 at 00:26 UTC: EIA had not published the 23:00 hour of 19 October, and the five demand tables checked over
     the whole window wrote nothing. A demand table's window now ends at the last midnight EIA has published to, one
     day back at most (demand_window_end); the dry run replays an earlier run's raw answers at a simulated start.

The rows here are test fixtures, not data values. No network, no keys.

    python -m unittest tests.test_session336 -v
"""

import ast
import gzip
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import test_session305 as t305  # noqa: E402
import eia930 as E  # noqa: E402

R, rt = t305.R, t305.rt

# The first lines of nyiso_zone_load_hourly's header as the runner's run 20261020T011604Z archived it (read from the
# archive's run log in the bucket, 20 October 2026): three stacked rebuild lines, then the table's own.
RUNNER_HEADER = [
    "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261019T211146Z-github "
    "(2026-10-19T21:11:46Z); that run's own header of the table follows",
    "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261019T164654Z-github "
    "(2026-10-19T16:46:54Z); that run's own header of the table follows",
    "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261015T160515Z-github "
    "(2026-10-15T16:05:15Z); that run's own header of the table follows",
    "Energy Research Warehouse (ERW): NYISO, hourly load by zone, the integrated real-time actual load of its eleven "
    "load zones (P-58C, palIntegrated) (session 138)",
    "Retrieved: 20261010T150225Z (UTC) by warehouse/connectors/nyiso_zone_load.py",
]


def own_first_line():
    """The package test's own function, read from its file (importing the module would scan warehouse/output)."""
    path = os.path.join(ROOT, "package", "tests", "test_erw.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "own_first_line")
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), path, "exec"), ns)
    return ns["own_first_line"]


class TheHeaderTest(unittest.TestCase):
    def test_the_runners_header_of_20_october_passes(self):
        self.assertTrue(own_first_line()(RUNNER_HEADER))

    def test_restore_py_s_line_is_still_set_aside_and_a_header_of_rebuild_lines_alone_fails(self):
        f = own_first_line()
        self.assertTrue(f(["Rebuilt from the ERW archive by warehouse/archive/restore.py, as of run R (t); that run's "
                           "own header of the table follows", "Energy Research Warehouse (ERW): x"]))
        self.assertFalse(f(RUNNER_HEADER[:3]))
        self.assertFalse(f(["Restored from the Redivis draft (x) by scripts/sync.py", RUNNER_HEADER[3]]))


class StackedRuns(t305.Fixture):
    """The fixture's latest run (R2) archived with a header that already carries two rebuild lines."""
    def setUp(self):
        super().setUp()
        runs = pd.read_csv(io.BytesIO(gzip.decompress(self.bucket.get("_runs/2026-10/R2.csv.gz"))),
                           dtype=str, keep_default_na=False)
        runs.loc[runs["run_id"] == "R2", "header"] = "\n".join(RUNNER_HEADER[1:4])
        self.bucket.put("_runs/2026-10/R2.csv.gz", t305.gz_csv(runs), overwrite=True)
        R._BUCKET_RUNS.clear()

    def rebuild_lines(self, lines):
        return [h for h in lines if h.startswith("Rebuilt from the ERW archive by ")]


class TheRebuildersDoNotStack(StackedRuns):
    def test_restore_tables_writes_one_rebuild_line(self):
        s = self.sources(redivis=False)
        out = os.path.join(self.tmp, "tbl.csv")
        self.assertEqual(s.replay_sliced("tbl", s.latest("tbl"), out), 4)
        header = [x[2:].rstrip("\n") for x in open(out, encoding="utf-8") if x.startswith("# ")]
        self.assertEqual(len(self.rebuild_lines(header)), 1)
        self.assertIn("as of run R2", header[0])
        self.assertTrue(header[1].startswith("Energy Research Warehouse (ERW):"))
        self.assertTrue(own_first_line()(header))

    def test_restore_py_writes_one_rebuild_line(self):
        header, df, expected = R.rebuild("tbl", from_bucket=True, bucket=self.bucket)
        self.assertEqual((len(df), expected), (4, 4))
        self.assertEqual(len(self.rebuild_lines(header)), 1)
        self.assertTrue(header[1].startswith("Energy Research Warehouse (ERW):"))


def demand_rows(ba, start, hours, missing_last=0):
    """Hourly demand_mw and demand_forecast_mw rows of a BA as to_rows gives them, the last hours left out."""
    ts = pd.date_range(start, periods=hours - missing_last, freq="1h", tz="UTC")
    rows = []
    for var in ("demand_mw", "demand_forecast_mw"):
        rows.append(pd.DataFrame({"respondent": ba, "variable": var, "interval_start": ts, "value": 100.0,
                                  "source": "eia:electricity/rto/region-data", "source_url": "https://api.eia.gov/x",
                                  "retrieved_at": "2026-10-20T00:05:00Z"}))
    return pd.concat(rows, ignore_index=True)


class TheDemandWindow(unittest.TestCase):
    CLOCK = pd.Timestamp("2026-10-20T00:00:00Z")

    def test_the_window_ends_a_day_early_when_the_last_hour_is_not_published(self):
        rows = demand_rows("CISO", "2026-10-16T00:00:00Z", 96, missing_last=1)  # 23:00 of 19 October missing
        end = E.demand_window_end(rows, self.CLOCK, lambda m: None, "eia930_ciso_demand")
        self.assertEqual(end, pd.Timestamp("2026-10-19T00:00:00Z"))
        start = end - pd.Timedelta(days=3)
        E.build_table(rows, "ciso", start, end, lambda m: None, "eia930_ciso_demand", "t", "r", 3, write=False)

    def test_the_clock_window_on_the_same_rows_fails_as_the_runner_did(self):
        rows = demand_rows("CISO", "2026-10-16T00:00:00Z", 96, missing_last=1)
        with self.assertRaisesRegex(RuntimeError, "71 of 72 hours"):
            E.build_table(rows, "ciso", self.CLOCK - pd.Timedelta(days=3), self.CLOCK, lambda m: None,
                          "eia930_ciso_demand", "t", "r", 3, write=False)

    def test_a_published_last_hour_keeps_the_clocks_midnight(self):
        rows = demand_rows("CISO", "2026-10-16T00:00:00Z", 96)
        self.assertEqual(E.demand_window_end(rows, self.CLOCK, lambda m: None, "x"), self.CLOCK)

    def test_one_day_back_at_most_so_a_longer_lag_still_fails(self):
        rows = demand_rows("CISO", "2026-10-15T00:00:00Z", 96, missing_last=30)  # EIA a day and six hours behind
        end = E.demand_window_end(rows, self.CLOCK, lambda m: None, "x")
        self.assertEqual(end, pd.Timestamp("2026-10-19T00:00:00Z"))
        with self.assertRaisesRegex(RuntimeError, "incomplete data"):
            E.build_table(rows, "ciso", end - pd.Timedelta(days=3), end, lambda m: None, "eia930_ciso_demand", "t",
                          "r", 3, write=False)


def eia_json(rows):
    return json.dumps({"response": {"total": len(rows), "data": rows}})


class TheDryRun(unittest.TestCase):
    """main() --dry-run --now --raw over a raw folder built here: no request, no file outside its scratch folder."""
    DIRS = ("OUT_DIR", "LOG_DIR", "RAW_DIR", "METADATA_DIR", "STATUS_DIR")

    def setUp(self):
        self.dirs = {k: getattr(E.ip, k) for k in self.DIRS}  # --out-dir moves iso_prices' folders: put them back
        self.tmp = tempfile.mkdtemp()
        self.raw = os.path.join(self.tmp, "raw")
        os.makedirs(self.raw)
        periods = [f"{t:%Y-%m-%dT%H}" for t in pd.date_range("2026-10-15T01:00:00Z", "2026-10-20T00:00:00Z", freq="1h")]
        region = [dict(period=p, respondent="CISO", type=t, value="100") for p in periods for t in ("D", "DF", "NG")]
        fuel = [dict(period=p, respondent="CISO", fueltype="SUN", value="10") for p in periods]
        files = [("1_region", "region-data", eia_json(region)), ("2_error", "region-data", "<HTML>Error</HTML>"),
                 ("3_again", "region-data", eia_json(region[:5])), ("4_fuel", "fuel-type-data", eia_json(fuel))]
        with open(os.path.join(self.raw, "manifest.csv"), "w", encoding="utf-8") as m:
            m.write("retrieved_at,status,bytes,sha256,last_modified,file,url\n")
            for name, route, body in files:
                with open(os.path.join(self.raw, name), "w", encoding="utf-8") as f:
                    f.write(body)
                m.write(f'"2026-10-20T00:05:00Z","200","1","x","","{name}",'
                        f'"https://api.eia.gov/v2/electricity/rto/{route}/data/?api_key=REDACTED"\n')

    def tearDown(self):
        for k, v in self.dirs.items():
            setattr(E.ip, k, v)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_replay_takes_each_row_once_and_cuts_at_the_period_given(self):
        df = E.raw_rows(self.raw, "region-data", ["CISO"], list(E.REGION_TYPES), "2026-10-16T01", "2026-10-20T00",
                        "2026-10-19T23")
        self.assertFalse(df.duplicated(["respondent", "type", "period"]).any())
        self.assertEqual(df["period"].max(), "2026-10-19T23")
        self.assertEqual(len(df), 3 * 95)

    def test_a_simulated_0005_start_writes_the_demand_table_with_the_window_a_day_early(self):
        out = os.path.join(self.tmp, "out")
        before = set(os.listdir(os.path.join(ROOT, "warehouse", "output")))
        code = E.main(["--dry-run", "--days", "3", "--ba", "ciso", "--now", "2026-10-20T00:05:00Z", "--raw", self.raw,
                       "--raw-through", "2026-10-19T23", "--out-dir", out])
        self.assertEqual(code, 0)
        self.assertEqual(set(os.listdir(os.path.join(ROOT, "warehouse", "output"))), before)
        self.assertFalse([f for f in os.listdir(out) if f.endswith(".csv")])
        text = open(os.path.join(out, "logs", os.listdir(os.path.join(out, "logs"))[0]), encoding="utf-8").read()
        self.assertIn("eia930_ciso_demand: EIA has published demand_mw to 2026-10-19T23:00:00Z", text)
        self.assertIn("dry run: eia930_ciso_demand would write 144 rows, 2026-10-16T00:00:00Z to 2026-10-18T23:00:00Z",
                      text)

    def test_now_and_raw_need_the_dry_run(self):
        with self.assertRaises(SystemExit):
            E.main(["--now", "2026-10-20T00:05:00Z"])


class ThePublisherFigure(unittest.TestCase):
    """Session 316's script asked EIA for the column "retail_sales", the ERW's variable; EIA's column is "sales"
    (eia_series.py), and EIA answered HTTP 400 on 20 October."""
    def test_a_retail_sales_draft_asks_eias_sales_column(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import publisher_figure as pf
        route, q, data = pf.request_of("eia_retail_sales_monthly", {"entity": "eia:retail_sales:IN:COM"}, "2026-07-01")
        self.assertEqual((route, data), ("electricity/retail-sales", "sales"))
        self.assertIn(("data[0]", "sales"), q)
        self.assertEqual(pf.request_of("eia_retail_sales_monthly", {"entity": "eia:customers:DC:IND"}, "2026-07-01")[2],
                         "customers")
        self.assertEqual(pf.convert(1234.5, "million kilowatt hours"), (1234500.0, "MWh"))

    def test_eia_not_answering_is_a_skip_and_a_refused_request_a_failure(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import publisher_figure as pf
        from unittest import mock

        class Resp:
            def __init__(self, status, body=None):
                self.status_code, self.body = status, body or []

            def json(self):
                return self.body

            def raise_for_status(self):
                pass
        draft = {"id": "d1", "rule": "record", "table_name": "eia_retail_sales_monthly", "flag_date": "2026-07-01",
                 "flag": {"series": {"entity": "eia:retail_sales:IN:COM", "freq": "P1M"}, "value": 1.0}, "card": {}}
        env = {"SUPABASE_URL": "https://x.supabase.co", "SUPABASE_SERVICE_KEY": "k", "EIA_API_KEY": "e"}
        for status, want in ((504, pf.SKIP), (400, 1)):
            def get(url, params=None, headers=None, timeout=None, _s=status):
                return Resp(200, [draft]) if "scanner_drafts" in url else Resp(_s)
            with mock.patch("requests.get", get), mock.patch("lock.env", lambda k: env.get(k)), \
                    mock.patch("builtins.print"):
                self.assertEqual(pf.main([]), want, status)


class TheWiring(unittest.TestCase):
    def test_the_daily_step_runs_the_connector_without_a_simulated_clock(self):
        text = open(os.path.join(ROOT, "warehouse", "run_daily.sh"), encoding="utf-8").read()
        self.assertIn('pull eia930 "$PYTHON" warehouse/connectors/eia930.py --days "$DAYS"\n', text)

    def test_the_data_machine_reads_the_publishers_figure_after_its_scan(self):
        text = open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8").read()
        scan = text.index('soft_step dm_scanner "$PYTHON" warehouse/analysis/findings/findings_scanner.py --daily')
        fig = text.index('soft_step dm_publisher_figure "$PYTHON" warehouse/analysis/findings/publisher_figure.py\n')
        self.assertLess(scan, fig)


if __name__ == "__main__":
    unittest.main()
