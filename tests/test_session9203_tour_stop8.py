"""Session 9203 (chain 620, the desktop's second window, 20 November 2026): the tour's eighth stop says where the map is.

Energy Research Warehouse (ERW). Stop 8 ("Every region of the grid") said: "open its network view for the map; then
read "Ask" at the foot of the page". Walked on production at 1280 and 390 px (`runs/c620w2/b_tour.mjs`), the Network
tab of /grid?region=ten opens on the 3D network (the owner's standing ruling: the free-floating 3D look kept), with no
area of the map drawn; the map is one press further, on Map (60 areas drawn). And on a wide screen "Ask" is a panel
beside the tool, at the top, not at the foot of the page. The stop now names the press and where "Ask" stands.

Held here, on the source: the stop's words, the Map button's name on the network page, and the Ask panel as an aside in
the tool's second column. No default moves: the network still opens on the 3D view. Nothing here makes a request.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheWordsOnTheSource(unittest.TestCase):
    def setUp(self):
        self.tour = src("site", "lib", "tour.ts")
        m = re.search(r'title: "Every region of the grid".*?look: "((?:[^"\\]|\\.)*)"', self.tour, re.S)
        self.assertIsNotNone(m, "stop 8 is in site/lib/tour.ts")
        self.look = m.group(1)

    def test_the_stop_names_the_press_on_map(self):
        self.assertIn("then press Map for the map", self.look)
        self.assertNotIn("open its network view for the map", self.look)

    def test_the_stop_says_where_ask_stands(self):
        self.assertNotIn("at the foot of the page", self.look)
        self.assertIn("beside the tool on a wide screen and under it on a phone", self.look)

    def test_the_map_button_and_the_ask_panel_are_as_the_words_say(self):
        net = src("site", "app", "network", "Network.tsx")
        self.assertRegex(net, r'\["map",\s*"Map"\]|data-shape=\{k\}', "the network page draws its shape buttons, Map among them")
        self.assertIn('"Map"', net)
        region = src("site", "app", "grid", "RegionTool.tsx")
        self.assertRegex(region, r'<aside className="min-w-0 lg:border-l lg:border-rule lg:pl-6" aria-label="Ask"', "Ask is the second column on a wide screen")

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.look)


@unittest.skipUnless(NODE, "node is not installed")
class TheStopAsTheSiteReadsIt(unittest.TestCase):
    def test_the_stop_still_opens_the_tool_and_quotes_only_ask(self):
        r = subprocess.run([NODE, "--input-type=module", "-e", "import { STOPS } from './lib/tour.ts'; console.log(JSON.stringify(STOPS));"],
                           cwd=SITE, capture_output=True, text=True, timeout=60, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        stops = json.loads(r.stdout.strip().splitlines()[-1])
        s = next(x for x in stops if x["title"] == "Every region of the grid")
        self.assertEqual(s["href"], "/grid")
        self.assertEqual(s["headings"], ["Ask"])
        self.assertEqual(re.findall(r'"([^"]+)"', s["look"]), ["Ask"])


if __name__ == "__main__":
    unittest.main()
