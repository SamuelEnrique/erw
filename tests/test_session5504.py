"""Session 5504 (chain 269, portable laptop window P1): scripts/price_years_rebuild.py, the price years rebuilt and
loaded in one command (data request rows 4 and 5, docs/state/data_requests_five_tools.md).

No network and no data write: the steps are stubbed. The tests hold the order of the steps and that each exit code is
read (a failure stops what follows, the lock is always released), the refusals (a code machine, a freeze), rule 8's
snapshot only when a page that reads the table is live, the comparison of the default windows, and the request row.
"""
import importlib.util
import json
import os
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("price_years_rebuild", os.path.join(ROOT, "scripts", "price_years_rebuild.py"))
pyr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pyr)


def row(entity, variable, ts, value, freq="P12M", retrieved="2026-11-14T12:00:00Z"):
    return {"entity": entity, "variable": variable, "ts_utc": ts, "value": str(value), "freq": freq, "retrieved_at": retrieved}


class Compare(unittest.TestCase):
    def test_the_watched_windows_first_and_what_moves(self):
        live = {("caiso:TH_SP15_GEN-APND", "battery_foresight_4h_last_12"): row("caiso:TH_SP15_GEN-APND", "battery_foresight_4h_last_12", "2025-10-01T00:00:00Z", 79.308307),
                ("ercot:HB_HUBAVG", "battery_foresight_4h_last_12"): row("ercot:HB_HUBAVG", "battery_foresight_4h_last_12", "2025-10-01T00:00:00Z", 81.40219),
                ("spp:SPPSOUTH_HUB", "datacenter_flat_da_last_12"): row("spp:SPPSOUTH_HUB", "datacenter_flat_da_last_12", "2025-10-01T00:00:00Z", 29.27)}
        built = {("caiso:TH_SP15_GEN-APND", "battery_foresight_4h_last_12"): row("caiso:TH_SP15_GEN-APND", "battery_foresight_4h_last_12", "2025-11-01T00:00:00Z", 79.804242),
                 ("ercot:HB_HUBAVG", "battery_foresight_4h_last_12"): row("ercot:HB_HUBAVG", "battery_foresight_4h_last_12", "2025-10-01T00:00:00Z", 81.40219),
                 ("spp:SPPSOUTH_HUB", "datacenter_flat_da_last_12"): row("spp:SPPSOUTH_HUB", "datacenter_flat_da_last_12", "2025-10-01T00:00:00Z", 29.27)}
        lines, moved = pyr.compare(live, built)
        self.assertEqual(moved, 1)
        self.assertEqual(lines[0], "caiso:TH_SP15_GEN-APND battery_foresight_4h_last_12: live 2025-10 +12m 79.31; built 2025-11 +12m 79.80  (moves)")
        self.assertEqual(lines[1], "ercot:HB_HUBAVG battery_foresight_4h_last_12: live 2025-10 +12m 81.40; built 2025-10 +12m 81.40")
        self.assertEqual(len(lines), 2)   # an unwatched window that does not move is not listed

    def test_a_window_on_one_side_only_moves(self):
        lines, moved = pyr.compare({}, {("ercot:LZ_NORTH", "datacenter_flat_rt_last_12"): row("ercot:LZ_NORTH", "datacenter_flat_rt_last_12", "2025-11-01T00:00:00Z", 34.071372)})
        self.assertEqual(moved, 1)
        self.assertIn("live not in the live set; built 2025-11 +12m 34.07  (moves)", lines[0])


class ReadTable(unittest.TestCase):
    def test_the_header_is_skipped_and_the_proof_line_read(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "price_years_by_window.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("# Energy Research Warehouse (ERW): the price years\n# Proof of the default window, to the cent: battery ercot foresight_4h: equal\n")
                f.write("entity,variable,ts_utc,value,freq\nercot:HB_HUBAVG,battery_foresight_4h_last_12,2025-10-01T00:00:00Z,81.40219,P12M\n")
            t = pyr.read_table(p)
            self.assertEqual(t[("ercot:HB_HUBAVG", "battery_foresight_4h_last_12")]["value"], "81.40219")
            self.assertEqual(pyr.header_line(p, "Proof of the default window"), "Proof of the default window, to the cent: battery ercot foresight_4h: equal")


class LiveRows(unittest.TestCase):
    def test_pages_until_short_and_the_anon_key_only(self):
        seen = []

        def fetch(req):
            seen.append(req)
            n = len(seen)
            return [{"entity": f"e{n}-{i}", "variable": "x_last_12", "ts_utc": "2025-11-01T00:00:00Z", "value": 1, "freq": "P12M"} for i in range(1000 if n == 1 else 3)]
        with mock.patch.object(pyr, "env", side_effect=lambda k: {"SUPABASE_URL": "https://abc.supabase.co/x", "SUPABASE_ANON_KEY": "anon"}.get(k)):
            out = pyr.live_rows(fetch=fetch)
        self.assertEqual(len(seen), 2)
        self.assertEqual(len(out), 1003)
        self.assertTrue(seen[0].full_url.startswith("https://abc.supabase.co/rest/v1/series?"))
        self.assertIn("table_name=eq.price_years_by_window", seen[0].full_url)
        self.assertIn("offset=1000", seen[1].full_url)
        self.assertEqual(seen[0].get_header("Apikey"), "anon")
        src = open(os.path.join(ROOT, "scripts", "price_years_rebuild.py"), encoding="utf-8").read()
        self.assertNotIn("SUPABASE_SERVICE_KEY", src)


class Apply(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.codes = {}

    def fake_run(self, cmd, label):
        self.calls.append(label)
        return self.codes.get(label, 0)

    def patched(self, role="data", live=(), rows=None, built=None):
        rows = rows if rows is not None else {}
        return [mock.patch.object(pyr, "run", side_effect=self.fake_run), mock.patch.object(pyr, "role", return_value=role),
                mock.patch.object(pyr, "live_pages", return_value=list(live)), mock.patch.object(pyr, "live_rows", return_value=rows),
                mock.patch.object(pyr, "read_table", return_value=built or {})]

    def go(self, **kw):
        ps = self.patched(**kw)
        for p in ps:
            p.start()
        try:
            return pyr.apply("py", "snaps")
        finally:
            for p in ps:
                p.stop()

    def test_a_code_machine_is_refused_before_any_step(self):
        self.assertEqual(self.go(role="code"), 2)
        self.assertEqual(self.calls, [])

    def test_a_freeze_refuses_before_the_lock(self):
        self.codes["the freeze"] = 1
        self.assertEqual(self.go(), 2)
        self.assertEqual(self.calls, ["the freeze"])

    def test_the_steps_in_order_and_the_lock_released(self):
        k = ("caiso:TH_SP15_GEN-APND", "battery_foresight_4h_last_12")
        built = {k: row(*k, "2025-11-01T00:00:00Z", 79.804242)}
        future = {k: row(*k, "2025-11-01T00:00:00Z", 79.804242, retrieved="2999-01-01T00:00:00Z")}
        self.assertEqual(self.go(rows=future, built=built), 0)
        self.assertEqual(self.calls, ["the freeze", "the data lock", "the build", "the validator", "the coverage row", "the load", "the lock released"])

    def test_a_failed_step_stops_what_follows_and_the_lock_is_still_released(self):
        self.codes["the validator"] = 1
        self.assertEqual(self.go(), 1)
        self.assertEqual(self.calls, ["the freeze", "the data lock", "the build", "the validator", "the lock released"])

    def test_a_load_that_does_not_read_back_is_not_proven(self):
        k = ("ercot:LZ_NORTH", "datacenter_flat_rt_last_12")
        built = {k: row(*k, "2025-11-01T00:00:00Z", 34.071372)}
        old = {k: row(*k, "2025-10-01T00:00:00Z", 33.728887, retrieved="2026-10-20T09:08:39Z")}
        self.assertEqual(self.go(rows=old, built=built), 1)

    def test_a_live_page_takes_rule_8_s_snapshot_before_and_after(self):
        k = ("ercot:HB_HUBAVG", "generator_solar_last_12")
        built = {k: row(*k, "2025-10-01T00:00:00Z", 59.852265)}
        rows = {k: row(*k, "2025-10-01T00:00:00Z", 59.852265, retrieved="2999-01-01T00:00:00Z")}
        self.assertEqual(self.go(live=["/cost-of-power/seller"], rows=rows, built=built), 0)
        self.assertEqual(self.calls[1], "the snapshot before")
        self.assertEqual(self.calls[-2:], ["the snapshot after", "the comparison"])


class TheRepository(unittest.TestCase):
    def test_no_economics_page_is_live_today(self):
        self.assertEqual(pyr.live_pages(), [])

    def test_the_steps_name_real_files_and_the_table_is_in_the_live_set(self):
        for rel in (("warehouse", "derived", "price_years.py"), ("warehouse", "validate", "erw_validate.py"), ("warehouse", "metadata", "build_coverage.py"),
                    ("warehouse", "supabase", "load.py"), ("warehouse", "lock.py"), ("scripts", "freeze.py"), ("site", "scripts", "snapshot-live.mjs")):
            self.assertTrue(os.path.exists(os.path.join(ROOT, *rel)), rel)
        live = open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8").read()
        self.assertIn("'^price_years_by_window$'", live)
        self.assertNotIn("'^price_years_by_window$'", live.split("union_by_key:", 1)[1].split("\n\n", 1)[0])

    def test_the_request_row(self):
        req = open(os.path.join(ROOT, "docs", "state", "data_requests_five_tools.md"), encoding="utf-8").read()
        self.assertRegex(req, r"\n\| 5 \| `price_years_by_window`[^\n]*`python scripts/price_years_rebuild.py --apply`[^\n]*\| 2026-11-14 \(session 5504\) \| requested")

    def test_no_dash(self):
        for rel in (("scripts", "price_years_rebuild.py"), ("tests", "test_session5504.py"), ("docs", "state", "data_requests_five_tools.md")):
            text = open(os.path.join(ROOT, *rel), encoding="utf-8").read()
            self.assertNotIn(chr(0x2014), text, rel)
            self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
