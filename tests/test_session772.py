"""Session 772 (chain 064): the node list filtered by class (storage, wind, solar, gas, other, mixed), kept in the address
(ncls), beside the name filter; the count line and the download say which. No request, no model call."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ClassFilter(unittest.TestCase):
    def test_the_list_filters_by_class_and_keeps_it(self):
        n = src("site", "app", "cost-of-power", "AllGridsNodes.tsx")
        self.assertIn('data-node-class="1"', n)
        self.assertIn('q.set("ncls", cl)', n)
        self.assertIn("(!cl || r.cls === cl)", n)
        self.assertIn("class ${cl}", n)
        self.assertIn('cls={q.ncls ?? ""}', src("site", "app", "cost-of-power", "AllGridsView.tsx"))
        self.assertIn('"/cost-of-power?view=allgrids&rows=nodes&ncls=storage&nsort=swing&ndir=desc"', src("site", "scripts", "check-values.mjs"))


if __name__ == "__main__":
    unittest.main()
