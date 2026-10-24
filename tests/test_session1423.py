"""Session 1423 (chain 111): the network component's words against its server panels.

- the side panel's MW words (site/lib/networkSide.ts, from site/app/network/Network.tsx, their arithmetic unchanged):
  in the live week a MW is written as the server panel grid_network_<grid> writes it (lib/format.ts shown), a net of
  exactly zero reads as an export, a story and a replayed day as before (whole MW);
- the gravity shape's cards (site/lib/networkGravity.ts gravityTip with shown, NetworkGravity.tsx) write the generation,
  the net import and the share as grid_gravity_<grid> writes them (two decimals where not whole);
- site/scripts/test-network-words.mjs compares every MW the component would write with the panels' figure for the same
  tie and hour, on the committed snapshot, for the seven ISO grids and the Lower 48.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheWordsAreThePanels(unittest.TestCase):
    def test_the_component_draws_through_the_pure_words(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('from "@/lib/networkSide";', n)
        self.assertIn("const mwOf = sideFormat(view.kind, shown, fmt);", n)
        self.assertIn("{sideNetLabel(netImport, unit)}", n)
        self.assertIn('sideTieWords(t.imp, mwOf, view.kind === "live")', n)
        # the lines older tests pin stay as they were (sessions 54, 109, 124)
        self.assertIn("const openHour = v3?.complete && v3.complete.index >= 0 ? v3.complete.index : snap.hours.length - 1;", n)
        self.assertIn("isDayView && demandNow && Math.round(t.imp) !== 0", n)
        side = src("site", "lib", "networkSide.ts")
        self.assertNotIn("import {", side)  # type imports only: Node runs it as it is
        self.assertIn('return `Net ${net > 0 ? "imports" : "exports"} this ${unit}`;', side)
        self.assertIn("gravityTip(hovered, at, hover.kind, shown)", src("site", "app", "network", "NetworkGravity.tsx"))

    def test_no_em_dash(self):
        for parts in (("site", "lib", "networkSide.ts"), ("site", "lib", "networkGravity.ts"), ("site", "app", "network", "Network.tsx"),
                      ("site", "app", "network", "NetworkGravity.tsx"), ("site", "scripts", "test-network-words.mjs")):
            self.assertNotIn(chr(0x2014), src(*parts), parts)

    def test_the_words_equal_the_panels(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-network-words.mjs")], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("8 tests passed", r.stdout)


if __name__ == "__main__":
    unittest.main()
