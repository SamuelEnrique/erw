"""Session 1191 (chain 089): the Python chat holds what the site holds, with ASK_HOLD=on (warehouse/chat/license_hold.py).

Held here, on the saved rows of session 320's four held-grid questions (tests/fixtures/session1112/held_reads.json):
asked for a held grid's rows, the Python query tool names the grid, says "license needed", states none of its figures and
gives the same query's figure for each public grid, the public figures the fixture's; a compare with a held side
answers; MISO's rows are refused with the pause's words; without ASK_HOLD the tools read as they did. And the hold's
decisions (which table is held, whole or by grid, which entity's rows, which grid a scoped chat's query asks for) are the
site's own, site/lib/license.ts and site/lib/chat/tools.ts run under node, over every table of the status file.
No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import license_hold  # noqa: E402
import tools  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "session1112", "held_reads.json")
ENTITIES = ["isone:.H.INTERNAL_HUB", "nyiso:N.Y.C.", "miso:INDIANA.HUB", "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND",
            "spp:SPPNORTH_HUB", "pjm:WESTERN HUB", "iso:nyiso", "iso:ercot", "nyiso_queue:1630", "eia:henry_hub", "eia930:MISO"]
SCOPES = [None, "ercot", "caiso", "nyiso", "isone", "spp"]


def fixture():
    with open(FIX, encoding="utf-8") as f:
        return json.load(f)


class Frames:
    """The fixture's rows as the tools' frames, the backend never asked."""

    def __enter__(self):
        fx = fixture()
        self.saved = dict(tools._frames), tools._backend_ready, tools.SCOPE
        tools._frames.clear()
        tools._backend_ready = True
        cov = pd.DataFrame([{"table": c["table_name"], "source_report": c["source_report"], "license": c["license"],
                             "tier": c.get("tier"), "last_run": pd.NaT, "ts_min": c.get("ts_min"), "ts_max": c.get("ts_max")} for c in fx["catalogue"]])
        tools._frames["_coverage"] = cov
        rows = pd.DataFrame(fx["rows"])
        for t, df in rows.groupby("table_name"):
            df = df.drop(columns=["table_name"]).reset_index(drop=True)
            df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
            df["freq"] = "P1M"
            tools._frames[t] = df
        self.patch = mock.patch.object(tools.erw, "version", return_value={"backend": "fixture"})
        self.patch.start()
        self.cite = mock.patch.object(tools.erw, "cite", return_value="fixture")
        self.cite.start()
        return fx

    def __exit__(self, *exc):
        self.patch.stop()
        self.cite.stop()
        tools._frames.clear()
        tools._frames.update(self.saved[0])
        tools._backend_ready, tools.SCOPE = self.saved[1], self.saved[2]
        tools._cites.clear()


def ask(q, **extra):
    return tools.run("query", {"table": q["table"], "aggregation": "mean", "entity": q["entity"], "variable": q["variable"],
                               "start": q["start"], "end": q["end"], **extra})


class TheHeldGrids(unittest.TestCase):
    def test_each_question_names_the_grid_and_gives_the_public_grids(self):
        with Frames() as fx, mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            for qid, q in fx["questions"].items():
                out, err = ask(q)
                self.assertFalse(err, (qid, out))
                self.assertTrue(out["held"], qid)
                grid = {"isone": "ISO-NE", "nyiso": "NYISO"}[q["entity"].split(":")[0]]
                self.assertEqual(out["grid"], grid, qid)
                self.assertEqual(out["grid_license"], "license needed")
                self.assertIn("State no figure of " + grid, out["note"])
                got = {r["entity"]: r["value"] for r in out["public_grids"]}
                self.assertEqual({k: round(v, 4) for k, v in got.items()}, q["public"], qid)
                held = [r for r in fx["rows"] if r["entity"] == q["entity"] and r["variable"] == q["variable"] and r["table_name"] == q["table"]]
                self.assertTrue(held, qid)
                self.assertNotIn(repr(held[0]["value"]), json.dumps(out, default=str), qid)

    def test_a_compare_with_a_held_side_answers(self):
        with Frames() as fx, mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            q = fx["questions"]["g08"]
            a = {k: q[k] for k in ("table", "entity", "variable", "start", "end")}
            out, err = tools.run("compare", {"a": {**a, "aggregation": "mean"}, "b": {**a, "entity": "ercot:HB_HUBAVG", "aggregation": "mean"}})
            self.assertFalse(err, out)
            self.assertTrue(out["a"]["held"])
            self.assertNotIn("difference_b_minus_a", out)

    def test_miso_is_refused_with_the_pause(self):
        with Frames() as fx, mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            q = dict(fx["questions"]["d05"], entity="miso:INDIANA.HUB")
            out, err = ask(q)
            self.assertTrue(err)
            self.assertEqual(out["error"], license_hold.MISO_PAUSED)

    def test_the_held_rows_are_left_out_of_a_read(self):
        with Frames() as fx, mock.patch.dict(os.environ, {"ASK_HOLD": "on"}):
            q = fx["questions"]["d05"]
            out, err = tools.run("query", {"table": q["table"], "aggregation": "mean", "variable": q["variable"], "start": q["start"],
                                           "end": q["end"], "group_by": "entity"})
            self.assertFalse(err, out)
            self.assertEqual({r["entity"].split(":")[0] for r in out["result"]}, {"caiso", "ercot", "spp"})

    def test_without_the_switch_the_tools_read_as_before(self):
        with Frames() as fx, mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ASK_HOLD", None)
            q = fx["questions"]["g07"]
            out, err = ask(q)
            self.assertFalse(err, out)
            self.assertNotIn("held", out)
            self.assertEqual(out["rows_matched"], 1)


class TheSitesDecisions(unittest.TestCase):
    def test_the_same_as_the_sites_functions(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        if not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("the site's packages are not installed in this copy")
        tables = sorted(license_hold.tables())
        script = (
            "const L = await import('./lib/license.ts');\n"
            "const T = await import('./lib/chat/tools.ts');\n"
            f"const tables = {json.dumps(tables)}, ents = {json.dumps(ENTITIES)}, scopes = {json.dumps(SCOPES)};\n"
            "const out = {};\n"
            "for (const t of tables) {\n"
            "  const r = { needed: L.licenseNeeded(t), byGrid: L.licenseByGrid(t), whole: L.licenseHeldRow(t), rows: {}, grid: {} };\n"
            "  for (const e of ents) r.rows[e] = L.licenseHeldRow(t, e);\n"
            "  for (const s of scopes) for (const e of [undefined, ...ents]) {\n"
            "    let g; try { g = T.heldGridOf({ table: t, entity: e }, s ? T.scopeOf(s) : null); } catch (x) { g = 'PAUSED'; }\n"
            "    r.grid[`${s ?? ''}|${e ?? ''}`] = g;\n"
            "  }\n"
            "  out[t] = r;\n"
            "}\n"
            "console.log(JSON.stringify(out));\n")
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0 and "Unknown file extension" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        site = json.loads(r.stdout.strip().splitlines()[-1])
        for t in tables:
            s = site[t]
            self.assertEqual(license_hold.license_needed(t), s["needed"], t)
            self.assertEqual(license_hold.by_grid(t), s["byGrid"], t)
            self.assertEqual(license_hold.held_row(t, whole=True), s["whole"], t)
            for e in ENTITIES:
                self.assertEqual(license_hold.held_row(t, e), s["rows"][e], (t, e))
            for slug in SCOPES:
                scope = tools.GRIDS[slug] if slug else None
                for e in [None, *ENTITIES]:
                    try:
                        g = license_hold.held_grid_of(t, e, scope)
                    except ValueError:
                        g = "PAUSED"
                    self.assertEqual(g, s["grid"][f"{slug or ''}|{e or ''}"], (t, slug, e))


if __name__ == "__main__":
    unittest.main()
