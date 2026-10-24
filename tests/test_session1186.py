"""Session 1186 (chain 091): the Grid pages under check-values, lighter, every result the same.

Energy Research Warehouse (ERW).

site/scripts/check-values.mjs recomputed some keys of the Grid pages with reads heavier than the page's own: the network
snapshot (about 2 MB) fetched once a key, a calc| key's operands and a fmt| key's inner key read again for each key that
names them, the same two series read for each of a pair of keys (fcerr, degday, netbal), the whole queue read for each
gridq| key, caiso_grid_emergencies read once an awe|days key, and one request a series| key where the page read the
range once. Each is now read once a page or once a run, and a page's series| keys of one table, entity and hour, and its
series_sum| and series_max| keys of one window, are read together, where the group's answer holds what each key's own
query would. site/scripts/check-values-cost.mjs measures it without a build (the pages drawn outside Next, on live answers
held in memory); site/scripts/test-check-values-light.mjs runs check-values on two pages of real rows. The method is
docs/methods/grid_network.md, section "The Grid pages under check-values, lighter (chain 091, 24 October 2026)".

    python -m unittest tests.test_session1186 -v
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
EM = chr(0x2014)
HEADING = "## The Grid pages under check-values, lighter (chain 091, 24 October 2026)"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING",
                         "CHECK_VALUES_PAGES", "CHECK_VALUES_RESUME", "CHECK_VALUES_WRITE_FLOOR", "CHECK_VALUES_LIGHT_SCRIPT")}


class TheLighterReads(unittest.TestCase):
    def test_one_recomputation_a_key_a_run(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn("function truth(check) {", c)
        self.assertIn("v = truthOf(check);", c)
        self.assertIn("async function truthOf(check) {", c)
        # a failed read is not kept: the next key that names it reads again
        self.assertIn("v.catch(() => { if (known.get(check) === v) known.delete(check); });", c)
        # session 1165's pinned operand loop, unchanged
        self.assertIn("for (const k of CALC.calcOperands(parts)) xs.push(Number(await truth(k)));", c)

    def test_the_snapshot_once_a_page(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn("storedOfPage = null;   // session 1186: each page reads the network snapshot in Storage afresh, once", c)
        self.assertIn("const res = await fetch(`${origin}/${N.NETWORK_OBJECT}`, { cache: \"no-store\" });", c)
        self.assertEqual(c.count("fetch(`${origin}/${N.NETWORK_OBJECT}`"), 1)
        self.assertIn("return res.ok ? { ok: true, json: await res.json() } : { ok: false, status: res.status };", c)
        self.assertIn("return K.nettieValue(check, [stored, committed].filter((s) => s && N.isSnapshot(s)));", c)
        self.assertIn("return K.netbalValue(check, snaps, gen, dem);", c)
        self.assertIn("erw-public/network/grid_network.json", c)

    def test_the_groups_keep_each_keys_own_answer(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn("pageBatches = planBatches([...onPage.keys()].filter((c) => !seen.has(c) && !truths.has(c)));", c)
        self.assertIn("if (g && g.length < 1000) {", c)
        self.assertIn("if (mine.length <= 1) return mine[0]?.value;", c)
        self.assertIn("return (await q(\"series\", params))[0]?.value;", c)
        self.assertIn('variable: variable.includes(",") ? `in.(${variable})` : `eq.${variable}`', c)
        self.assertIn("return null;   // the key's own query is sent instead", c)
        self.assertIn("keptRead(`gridq|${table}`", c)

    def test_the_note(self):
        n = src("docs", "methods", "grid_network.md")
        part = n[n.index(HEADING):]
        for w in ("Chain 091 in this note: session 1186.", "site/scripts/check-values-cost.mjs", "site/scripts/test-check-values-light.mjs",
                  "Decisions (chain 091, session 1186):", "a key that failed before fails"):
            self.assertIn(w, part, w)

    def test_the_fixture_is_real_rows(self):
        with open(os.path.join(SITE, "scripts", "fixtures", "caiso_queue_positions.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertIn("anon key", d["_note"])
        self.assertEqual(d["table"], "energy_projects")
        self.assertGreater(len(d["rows"]), 400)
        self.assertEqual({r["src"] for r in d["rows"]}, {"caiso_interconnection_queue"})

    def test_no_em_dash(self):
        for parts in (("site", "scripts", "check-values.mjs"), ("site", "scripts", "check-values-cost.mjs"), ("site", "scripts", "test-check-values-light.mjs"),
                      ("site", "scripts", "fixtures", "caiso_queue_positions.json"), ("docs", "methods", "grid_network.md"), ("tests", "test_session1186.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))


@unittest.skipUnless(NODE, "node is not on this machine")
class TheNodeTests(unittest.TestCase):
    def test_check_values_on_real_rows(self):
        r = subprocess.run([NODE, "scripts/test-check-values-light.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("8 tests passed", r.stdout)

    def test_the_cost_tools_pure_parts(self):
        code = ("import * as C from './scripts/check-values-cost.mjs';"
                "const a = [C.targetOf('/grid/ercot'), C.targetOf('/emissions'), C.targetOf('/mix?ba=erco&state=TX'), C.targetOf('/network'), C.targetOf('/storage'),"
                " C.kindOf('fmt|f1|calc|pct|a|b'), C.kindOf('series|t|e|v|h'),"
                " C.sameLines([{status:'ok',page:'/p',check:'k',rest:'Supabase 0.30000000000000004'}],[{status:'ok',page:'/p',check:'k',rest:'Supabase 0.3'}]).length,"
                " C.sameLines([{status:'ok',page:'/p',check:'k',rest:'Supabase 1'}],[{status:'FAIL',page:'/p',check:'k',rest:'Supabase 1'}]).length,"
                " C.perturbed('<span data-check=\"k\" data-raw=\"12\">').includes('data-raw=\"13.5\"')];"
                "console.log(JSON.stringify(a));")
        r = subprocess.run([NODE, "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120, env=node_env())
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1]),
                         ["/grid?grid=ercot", "/grid?view=clean", "/grid?view=mix&ba=erco&state=TX", "/grid?view=network", None, "calc", "series", 0, 1, True])


if __name__ == "__main__":
    unittest.main()
