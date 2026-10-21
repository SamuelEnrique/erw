"""Session 499: the row-level license, read by the site (chain 023, session 441's method).

A table the status file marks `hold: "row"` is read for its public rows only (lib/supabase.ts adds the filter on the
row's own license, `extra->>row_license`) and its held rows are counted, never shown; a table without the mark is held
whole, as on 21 October. The row's column is `row_license`, not the method's `license`: the live set's events and
entities already carry `license`, the table's tier (migration 001). And gridOfEntity reads an interconnection-queue id
("nyiso_queue:1630") as its grid's (session 467).
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "session499", "rows.json")

PROBE = r"""
import { readFileSync } from "node:fs";
const L = await import("@/lib/license");
const S = await import("@/lib/supabase");
const fx = JSON.parse(readFileSync(process.env.FX, "utf8"));
const on = new Date("2026-10-21T03:00:00Z");
const split = L.splitByRowLicense(fx.rows);
const out = {
  byRow: Object.fromEntries(Object.entries(fx.status).map(([k, v]) => [k, L.holdIsByRow(v)])),
  shown: split.shown.map((r) => r.event_id), held: split.held,
  heldEach: fx.rows.map((r) => L.rowLicenseHeld(r)),
  flat: [L.rowLicenseHeld({ row_license: "public" }), L.rowLicenseHeld({ row_license: "unsettled" }), L.rowLicenseHeld(null)],
  today: ["energy_deals", "datacenter_facilities", "datacenter_projects", "datacenter_operator_sites"].map((t) =>
    [t, L.licenseByRow(t), L.licenseByGrid(t), L.licenseHeldRow(t, null, on), L.licenseHeldRow(t, undefined, on)]),
  grid: ["nyiso_queue:1630", "ercot_queue:25INR0688", "isone_queue:65", "nyiso_load_queue:12", "miso_queue:J4296",
         "iso:isone", "isone:.H.INTERNAL_HUB", "datacenter:ercot_queue-25INR0688", "lbnl:APS:x", "texas_queue:1", "deal:abc"].map((e) => [e, L.gridOfEntity(e)]),
  pub: S.publicRowsQuery({ table_name: "eq.energy_deals", order: "event_date.desc" }),
  held_q: S.heldRowsQuery({ table_name: "eq.energy_deals" }),
  held_q_or: S.heldRowsQuery({ table_name: "eq.x", or: "(a.eq.1,b.eq.2)" }),
  values: L.ROW_LICENSES, column: L.ROW_LICENSE_COLUMN, filter: L.ROW_LICENSE_FILTER,
};
console.log(JSON.stringify(out));
"""


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class TheRowLicense(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dict(os.environ, FX=FIXTURE)
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", PROBE],
                           cwd=SITE, capture_output=True, text=True, timeout=120, env=env)
        if r.returncode != 0:
            raise AssertionError(f"node failed ({r.returncode}): {r.stderr[-800:]}")
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])
        with open(FIXTURE, encoding="utf-8") as f:
            cls.fx = json.load(f)

    def test_only_a_status_row_marked_row_is_held_by_row(self):
        self.assertEqual(self.out["byRow"], {"by_row": True, "whole": False, "marked_table": False})

    def test_the_fixture_shows_its_public_rows_and_counts_the_held(self):
        self.assertEqual(self.out["shown"], self.fx["expect"]["shown"])
        self.assertEqual(self.out["held"], self.fx["expect"]["held"])
        # a missing license holds the row, as "unsettled" and "license needed" do; case and spaces do not
        self.assertEqual(self.out["heldEach"], [False, False, False, True, True, True, True])
        self.assertEqual(self.out["flat"], [False, True, True])

    def test_today_the_four_tables_are_held_whole_as_before(self):
        # no status row carries the mark yet: nothing a visitor sees changes until the data machine writes it
        for t, by_row, by_grid, held_null, held_whole in self.out["today"]:
            self.assertFalse(by_row, t)
            self.assertFalse(by_grid, t)
            self.assertTrue(held_null, t)
            self.assertTrue(held_whole, t)
        status = json.loads(src("site", "data", "license_status.json"))
        self.assertFalse(any(v.get("hold") == "row" for v in status["tables"].values()))

    def test_queue_ids_are_their_grids(self):
        g = dict(self.out["grid"])
        self.assertEqual(g["nyiso_queue:1630"], "nyiso")
        self.assertEqual(g["ercot_queue:25INR0688"], "ercot")
        self.assertEqual(g["isone_queue:65"], "isone")
        self.assertEqual(g["nyiso_load_queue:12"], "nyiso")
        self.assertEqual(g["miso_queue:J4296"], "miso")
        self.assertEqual(g["iso:isone"], "isone")
        self.assertEqual(g["isone:.H.INTERNAL_HUB"], "isone")
        for e in ("datacenter:ercot_queue-25INR0688", "lbnl:APS:x", "texas_queue:1", "deal:abc"):
            self.assertEqual(g[e], "", e)

    def test_the_reader_asks_for_public_rows_and_counts_the_held(self):
        self.assertEqual(self.out["column"], "row_license")
        self.assertEqual(self.out["filter"], "extra->>row_license")
        self.assertEqual(self.out["values"], ["public", "license needed", "unsettled"])
        self.assertEqual(self.out["pub"], {"table_name": "eq.energy_deals", "order": "event_date.desc", "extra->>row_license": "eq.public"})
        self.assertEqual(self.out["held_q"]["or"], "(extra->>row_license.is.null,extra->>row_license.neq.public)")
        self.assertEqual(self.out["held_q_or"]["and"], "(or(a.eq.1,b.eq.2),or(extra->>row_license.is.null,extra->>row_license.neq.public))")
        self.assertNotIn("or", self.out["held_q_or"])

    def test_the_reader_filters_before_and_after_the_request(self):
        t = src("site", "lib", "supabase.ts")
        body = t[t.index("export async function restPaged"):t.index("async function restPages")]
        self.assertIn("if (hold.byRow)", body)
        self.assertIn("publicRowsQuery(query)", body)
        self.assertIn("!rowLicenseHeld(r as Record<string, unknown>)", body)
        # session 215's pins hold
        self.assertIn("licenseHold(query)", body)
        self.assertIn("throw new LicenseNeeded(tableOf(query))", body)
        self.assertIn("licenseHeldRow(t, (r as { entity?: string }).entity", body)

    def test_by_row_and_by_grid_are_never_both(self):
        t = src("site", "lib", "license.ts")
        body = t[t.index("export function licenseByGrid"):t.index("export const ROW_LICENSE_COLUMN")]
        self.assertIn("if (licenseByRow(table)) return false;", body)

    def test_no_em_dash(self):
        for p in (("site", "lib", "license.ts"), ("site", "lib", "supabase.ts"), ("tests", "test_session499.py"),
                  ("tests", "fixtures", "session499", "rows.json")):
            t = src(*p)
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)


if __name__ == "__main__":
    unittest.main()
