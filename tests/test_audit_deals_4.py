"""Audit of the energy deal tracker, finding 4 (session 10215, docs/reviews/deals-model-audit-2026-11-26.md): the tracker's
fold "How a deal gets here" says "AI power shows the deals the model tagged as power or infrastructure for AI or
datacenters". The tag is the AI-power rule (decision 8, the AI view's lead, the table's column tip): a named AI lab,
hyperscaler, datacenter operator or AI-load buyer is a party, or the load is a datacenter; it does not say the asset is
power. On the rows of 12 November 2026, 160 of the 212 tagged deals (folded) name no energy word in their technology or
asset; 75 are of the kind capital and 29 compute capacity.

1. Through the page's library (site/lib/deals2.ts, run by Node): the "AI power" click keeps the tagged rows whatever their
   kind ("True" and "true" one flag), a funding round among them. Passes on main.
2. The fix on this branch, words only: the fold says what the rule tags and that most tagged deals name no power asset.
   Fails on main."""
import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIB = "file:///" + os.path.join(ROOT, "site", "lib", "deals2.ts").replace("\\", "/")
JS = """
const D = await import(%s);
const r = (id, type, tag) => D.toDeal({ event_id: id, event_date: "2026-10-01T00:00:00Z", status: null, mw: null, price: null, currency: null, parties: null,
  source: "s", source_url: "u", extra: { deal_type: type, ai_power: tag } });
const all = [r("raise", "equity_raise", "True"), r("ppa", "ppa", "true"), r("plain", "ppa", "false")];
const x = D.inputsOf({ view: "ai" }, all);
console.log(JSON.stringify(D.select(all, x).map((d) => [d.id, d.kind])));
""" % json.dumps(LIB)


def flat(s):
    return " ".join(s.split())


class TheAiTagInTheTrackersFold(unittest.TestCase):
    def test_the_ai_click_keeps_every_tagged_kind(self):
        out = subprocess.run(["node", "--input-type=module"], input=JS, capture_output=True, text=True, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(sorted(json.loads(out.stdout.strip().splitlines()[-1])), [["ppa", "ppa"], ["raise", "capital"]])

    def test_the_fold_says_what_the_rule_tags(self):
        with open(os.path.join(ROOT, "site", "app", "deals", "v2", "view.tsx"), encoding="utf-8") as f:
            v2 = flat(f.read())
        self.assertNotIn("tagged as power or infrastructure for AI or datacenters", v2)
        self.assertIn("<li><strong>AI power</strong> shows the deals the AI-power rule tags: a named AI lab, hyperscaler, datacenter operator or "
                      "AI-load buyer is a party, or the load the deal serves is a datacenter. The tag says who is in the deal or what it serves, not "
                      "that its asset is power: a funding round, a financing or an acquisition of an AI company is tagged too, and most tagged deals "
                      "name no power asset (the decisions below, item 8).</li>", v2)


if __name__ == "__main__":
    unittest.main()
