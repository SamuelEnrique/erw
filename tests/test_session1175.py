"""Session 1175 (chain 078): the network component, lighter on a phone.

The 3D shape's code (3d-force-graph with three.js) was already loaded only when its shape is drawn: two import() calls
in the network component's own effect, which returns unless the shape shown is the network, the browser draws WebGL
and the frame is within 200 px of the screen (sessions 180 and 428). This session proves it by a source scan of the
Grid page's import graph (site/scripts/test-network-split.mjs, the site's own TypeScript parser): no module the page
loads statically imports either library or a package built on them, and the Mix tab (the default) draws no network
component. While the scene's chunk is on its way the frame, the same box as before, says it is loading: a line laid
over the box as its sibling (the library empties the box when it draws), gone once the scene is built. No figure, no
check key and no promise of the method note moves.
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


class TheScene(unittest.TestCase):
    def test_its_libraries_load_in_its_effect_only(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn('const load = () => Promise.all([import("3d-force-graph"), import("three")])', n)
        self.assertEqual(n.count('import("three")'), 1)
        self.assertNotIn('from "three"', n)
        self.assertNotIn('from "3d-force-graph"', n)

    def test_the_frame_says_it_is_loading_and_keeps_its_box(self):
        n = src("site", "app", "network", "Network.tsx")
        self.assertIn("const [sceneReady, setSceneReady] = useState(false);", n)
        self.assertIn('<div className="relative min-w-0" data-scene={sceneReady ? "ready" : "loading"}>', n)
        self.assertIn("Loading the 3D network.", n)
        self.assertEqual(n.count('style={{ height: "min(72vh, 620px)", minHeight: 420 }}'), 1)
        self.assertIn("This browser cannot draw 3D (WebGL is not available), so the network is not shown.", n)

    def test_the_method_note_says_so(self):
        m = src("docs", "methods", "grid_network.md")
        self.assertIn("## The 3D scene's code, loaded when it is drawn (sessions 428 and 1175)", m)
        self.assertIn("site/scripts/test-network-split.mjs", m)

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    @unittest.skipUnless(os.path.exists(os.path.join(SITE, "node_modules", "typescript", "package.json")), "site/node_modules is not installed")
    def test_the_node_test(self):
        r = subprocess.run(["node", os.path.join("scripts", "test-network-split.mjs")], cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("7 tests passed", r.stdout)


class TheFiles(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in (("site", "app", "network", "Network.tsx"), ("site", "scripts", "test-network-split.mjs"),
                      ("docs", "methods", "grid_network.md"), ("tests", "test_session1175.py"),
                      ("archive", "sessions", "SESSION_1175_REPORT.md")):
            if os.path.exists(os.path.join(ROOT, *parts)):
                self.assertNotIn(EM, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
