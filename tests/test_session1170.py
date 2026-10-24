"""Session 1170 (chain 078): the outside grids' demand in the replay, the Grid pack's blind spot 11.

When the address of /grid names a replayed day (net=day&t=<day>), the server panels draw that day's figures from the
replay's committed daily file (site/public/network/daily_<year>.json), keyed: on the Network tab (grid_network_<grid>,
components/grid/ReplayDay.tsx ReplayDayFigures) the demand, net exchange and ties of the balancing authority in the
address, BPAT as well as the seven ISO grids, "not held" where the file holds no demand; on the Gravity tab
(grid_gravity_<grid>, ReplayDayDemand) one line, the grid in view's demand, and that the shape still draws the live hour.
Keys: fmt|n0|file|public/network/daily_<year>.json|demand.<BA>.@<day> (session 1166's file| kind, scripts/check-file.mjs
reading site/public/network/ and the "@<day>" segment) and fmt|n0|netday|<export|import>|<BA>|<day>, netday|ties|<BA>|<day>
(a new kind, site/lib/gridReplay.ts netdayValue, run by check-values on the same file).
The node test: site/scripts/test-grid-replay.mjs.
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))
EM = chr(0x2014)
NEW = [("site", "lib", "gridReplay.ts"), ("site", "lib", "gridReplayFile.ts"), ("site", "components", "grid", "ReplayDay.tsx"),
       ("site", "scripts", "test-grid-replay.mjs"), ("tests", "test_session1170.py")]
CHANGED = [("site", "components", "grid", "NetworkFigures.tsx"), ("site", "components", "grid", "NetworkView.tsx"), ("site", "lib", "gridtool.ts"),
           ("site", "app", "grid", "page.tsx"), ("site", "next.config.ts"), ("site", "scripts", "check-file.mjs"), ("site", "scripts", "check-values.mjs"),
           ("site", "scripts", "check-methods.mjs"), ("docs", "methods", "grid_network_v3.md"), ("docs", "methods", "grid_network.md"),
           ("docs", "reviews", "packs", "grid.md")]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_env():
    return {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME")}


class TheAddress(unittest.TestCase):
    def test_the_page_passes_the_day_to_both_tabs(self):
        page = src("site", "app", "grid", "page.tsx")
        self.assertIn('<NetworkView keep={keep} node={p.node} grid={grid} day={p.day} />', page)
        self.assertIn('<NetworkView keep={keep} node={p.node} shape="gravity" grid={grid} day={p.day} />', page)
        t = src("site", "lib", "gridtool.ts")
        self.assertIn('const day = one(q.net) === "day" && t && /^\\d{4}-\\d{2}-\\d{2}$/.test(t) ? t : null;', t)

    def test_the_view_holds_the_day_to_the_replay_and_reads_the_file(self):
        v = src("site", "components", "grid", "NetworkView.tsx")
        self.assertIn("const shownDay = day ? clampDay(day, index) : null;", v)
        self.assertIn("read: readReplayYear(shownDay)", v)
        self.assertIn("replay={replay} node={node} />", v)
        self.assertIn('"/grid": ["./public/network/daily_*.json"]', src("site", "next.config.ts"))
        # the file is read from site/public/network/, and a failure is said, never filled
        f = src("site", "lib", "gridReplayFile.ts")
        self.assertIn('path.join(process.cwd(), "public", "network", `daily_${year}.json`)', f)
        self.assertIn("could not be read on the server", f)


class ThePanels(unittest.TestCase):
    def test_the_network_panel_draws_the_day_first_for_the_node(self):
        f = src("site", "components", "grid", "NetworkFigures.tsx")
        self.assertIn("const day = replay && node ? <ReplayDayFigures ask={replay} ba={node} name={nameOf(node)} /> : null;", f)
        net = f[f.index("export function NetworkFigures("):f.index("function Balance(")]
        # in both branches, the Lower 48's and a grid's, first in the panel
        self.assertEqual(net.count("{day}"), 2)
        for at in [m.start() for m in re.finditer(r"\{day\}", net)]:
            self.assertLess(net.rfind("data-grid-panel={panel}", 0, at), at)

    def test_the_gravity_panel_adds_one_line_and_keeps_its_words(self):
        f = src("site", "components", "grid", "NetworkFigures.tsx")
        g = f[f.index("export function GravityFigures"):]
        self.assertIn("{replay ? <ReplayDayDemand ask={replay} ba={grid.ba} label={grid.label} /> : null}", g)
        self.assertIn('data-gravity-window="live"', g)
        self.assertIn("no figure here is that day&apos;s", g)
        self.assertIn('data-gravity-window="day"', g)
        self.assertIn("the line under the table gives that day&apos;s demand", g)

    def test_the_components_key_every_figure_and_say_not_held(self):
        r = src("site", "components", "grid", "ReplayDay.tsx")
        self.assertIn("<Num check={f.check} raw={f.raw}>{f.text}</Num>", r)
        self.assertIn('<Missing words="not held"', r)
        self.assertIn("data-grid-replay-day={ba}", r)
        self.assertIn("data-gravity-day={ask.day}", r)
        self.assertIn("still draws the live hour: it is sized by net generation (ruling 1a)", r)
        k = src("site", "lib", "gridReplay.ts")
        self.assertIn("check: `fmt|n0|file|${file}|demand.${ba}.@${day}`", k)
        self.assertIn("check: `fmt|n0|netday|export|${ba}|${day}`", k)
        self.assertIn("check: `fmt|n0|netday|import|${ba}|${day}`", k)
        self.assertIn("check: `netday|ties|${ba}|${day}`", k)


class TheChecks(unittest.TestCase):
    def test_check_values_reads_the_replay_files(self):
        c = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "netday") {', c)
        self.assertIn("return R.netdayValue(check, dataFile(R.replayFileOf(day)));", c)
        self.assertIn("FILE.fileOnDisk(path.join(here, \"..\"), f)", c)
        f = src("site", "scripts", "check-file.mjs")
        self.assertIn("const REPLAY = /^public\\/network\\/daily_\\d{4}\\.json$/;", f)
        self.assertIn('if (key.startsWith("@")) {', f)

    def test_the_keys_are_named_in_the_note_the_page_links(self):
        n = src("docs", "methods", "grid_network.md")
        for w in ("file|public/network/daily_<year>.json|demand.<BA>.@<day>", "netday|export|<BA>|<day>", "netday|import|<BA>|<day>", "netday|ties|<BA>|<day>"):
            self.assertIn(w, n)
        v3 = src("docs", "methods", "grid_network_v3.md")
        self.assertIn("## The outside grids' demand in the replay (chain 078, 24 October 2026)", v3)
        self.assertIn("Decisions (chain 078, session 1170):", v3)

    def test_no_em_dash(self):
        for parts in NEW + CHANGED:
            self.assertNotIn(EM, src(*parts), "/".join(parts))


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_the_replay_on_the_committed_file(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-replay.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=300, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIsNotNone(re.search(r"^\S* ?pass 4", r.stdout, re.M), r.stdout[-1500:])


if __name__ == "__main__":
    unittest.main()
