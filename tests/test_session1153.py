"""Session 1153 (chain 077): the network's gravity view, honest.

- every edge of the gravity shape (the line from the Lower 48 to a grid) is drawn only where the grid has a net figure
  in the window, and answers a hover with its MW, its share of the grid's generation and its window (the hour shown and
  the snapshot's refresh); a circle's hover card adds its generation (site/lib/networkGravity.ts, NetworkGravity.tsx);
- the note under the frame and the server panel grid_gravity_<grid> say the shape is drawn from EIA-930's public
  interchange and net generation only, for every grid, and name the one thing that is not (the color: CAISO's own
  generation for California since 16 December 2025, in carbon_intensity_hourly);
- the Gravity tab's grid picker carries the replay's day (net=day, t) from the address (site/lib/carry.ts,
  components/tool/CarryLink.tsx), and the server panel says it draws the live hour only;
- the rule, its sign and its scale are unchanged (rulings 1a, 2c, 6a): the node test runs them on typed cases.
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheShape(unittest.TestCase):
    def test_edges_only_with_a_figure_and_their_hover(self):
        g = src("site", "app", "network", "NetworkGravity.tsx")
        self.assertIn("{gravityEdges(lay).map((p) => (", g)
        self.assertNotIn("{lay.places.map((p) => (\n            <line", g)
        self.assertIn('data-gravity-edge={p.id}', g)
        self.assertIn('onPointerMove={hoverAt(p.id, "edge")}', g)
        self.assertIn('pointerEvents="stroke"', g)
        self.assertIn("gravityTip(hovered, at, hover.kind)", g)
        self.assertIn("data-gravity-hover-kind={hover.kind}", g)
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("at={{ hour: ts, refresh: snap.built }} pick={pick?.id ?? null}", n)

    def test_the_rule_is_unchanged(self):
        ts = src("site", "lib", "networkGravity.ts")
        self.assertIn("export const GRAVITY = { SIZE: 640, R_CENTER: 80, D_MID: 205, D_SPAN: 90, S_FULL: 0.25, R_MIN: 6, GAP: 4 };", ts)
        self.assertIn("pull = clamp(Math.sign(share) * Math.sqrt(Math.abs(share) / S_FULL), -1, 1)", ts)
        self.assertIn("const d = clamp(D_MID - D_SPAN * pull, R_CENTER + r + GAP, c - r - GAP);", ts)
        self.assertIn("sum += l.a === id ? -v : v;", ts)
        self.assertIn("export function gravityEdges(lay: GravityLayout): GravityPlace[]", ts)
        self.assertIn("return lay.places.filter((p) => p.net !== null);", ts)

    def test_the_face_says_public_interchange_only(self):
        g = src("site", "app", "network", "NetworkGravity.tsx")
        block = g[g.index('data-gravity-public="1"'):]
        for words in ("EIA-930&apos;s public interchange and net generation only, for every grid", "PJM, MISO, ISO-NE and NYISO",
                      "no grid operator&apos;s own table places or sizes a circle", "carbon_intensity_hourly", "for California since {caisoJoinDay()}"):
            self.assertIn(words, block)
        f = src("site", "components", "grid", "NetworkFigures.tsx")
        self.assertIn('data-gravity-public="1"', f)
        self.assertIn("no grid operator&apos;s own table is read", f)
        self.assertIn('data-gravity-window="live"', f)
        self.assertIn("no figure here is that day&apos;s", f)
        # the panel adds no figure: its count of F stays as session 1151 left it
        self.assertEqual(f.count("<F "), 10)

    def test_the_replayed_day_is_said(self):
        g = src("site", "app", "network", "NetworkGravity.tsx")
        self.assertIn("A replayed day stays in the address", g)


class ThePicker(unittest.TestCase):
    def test_the_gravity_tab_carries_the_day(self):
        page = src("site", "app", "grid", "page.tsx")
        self.assertIn('<ToolPicker label="Grid"', page)
        self.assertIn('const pickerCarry = view === "gravity" || view === "network" ? KEEP_DAY : undefined;', page)
        self.assertIn("carry={pickerCarry} />", page)
        self.assertEqual(page.count("<ToolPicker "), 1)
        carry = src("site", "lib", "carry.ts")
        self.assertIn('export const KEEP_DAY: Carry = { when: "net", is: "day", words: ["net", "t"] };', carry)
        self.assertNotIn("import ", carry)
        link = src("site", "components", "tool", "CarryLink.tsx")
        self.assertTrue(link.startswith('"use client";'))
        self.assertIn("useSearchParams()", link)
        self.assertIn("<SiteLink href={carryWords(href, search, carry)} {...rest} />", link)
        choose = src("site", "components", "tool", "Choose.tsx")
        self.assertIn("data-segments={label}", choose)
        self.assertIn("return carry\n          ? <CarryLink", choose)
        # without carry every picker draws the plain link, as before (the map's queue picker)
        self.assertIn(": <Link key={i.key} href={i.href}", choose)


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_gravity(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-gravity.mjs")], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("6 of 6 passed", r.stdout)


class NoEmDash(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "lib", "networkGravity.ts"), ("site", "app", "network", "NetworkGravity.tsx"), ("site", "app", "network", "Network.tsx"),
                      ("site", "lib", "carry.ts"), ("site", "components", "tool", "CarryLink.tsx"), ("site", "components", "tool", "Choose.tsx"),
                      ("site", "components", "grid", "NetworkFigures.tsx"), ("site", "app", "grid", "page.tsx"), ("site", "scripts", "test-gravity.mjs"),
                      ("tests", "test_session1153.py")):
            self.assertNotIn(EM, src(*parts), "/".join(parts))
        p = os.path.join(ROOT, "archive", "sessions", "SESSION_1153_REPORT.md")
        if os.path.exists(p):
            self.assertNotIn(EM, src("archive", "sessions", "SESSION_1153_REPORT.md"))


if __name__ == "__main__":
    unittest.main()
