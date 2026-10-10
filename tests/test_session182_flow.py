"""Session 182, part 4: one flow for requests on /analysis (what to analyze, how to show it), and the template
gallery retired into it.

The rules live in the site's TypeScript (site/lib/analysisflow.ts, site/lib/chartforms.ts). site/scripts/
test-analysis-flow.mjs prints them as JSON for the committed cards and the weekly gallery; this module reads that
print and checks it against a Python statement of the same rules, so a change of a rule on one side fails here.
No network, no model call, no table needed: the cards and the gallery are in the repository.
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT_FLOW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM_FLOW = chr(0x2014)
FILES_FLOW = [
    "site/lib/analysisflow.ts", "site/lib/chartforms.ts", "site/components/analysis/RequestFlow.tsx", "site/components/analysis/FormPicker.tsx",
    "site/components/analysis/FormChart.tsx", "site/components/analysis/FlowHost.tsx", "site/components/analysis/RequestForm.tsx", "site/components/analysis/ImpactForm.tsx",
    "site/components/analysis/FindingCard.tsx", "site/app/analysis/page.tsx", "site/app/analysis/card/[id]/page.tsx",
    "site/app/_retired/analysis-gallery/AnalysisGallery.tsx", "site/scripts/test-analysis-flow.mjs", "site/scripts/check-analysis-flow.mjs",
    "site/scripts/check-analysis.mjs", "docs/methods/automated_analysis_findings.md", "tests/test_session182_flow.py",
]
TEN = ["peak_premium_block", "da_rt_spread_by_hour", "forecast_error", "curtailment_midday", "implied_heat_rate", "storage_evening_peak",
       "negative_price_hours", "deals_by_month", "datacenters_by_state", "chokepoint_transits"]
# the form each chart kind of a card declares: the default of an analysis that draws that kind
NATIVE_FLOW = {"line_with_fleet": "lines", "lines": "lines", "flag_line": "lines", "grouped_bar": "bars", "bars_free": "bars",
               "stacked_bar_pct": "stacked", "scatter": "points", "multiples": "multiples"}
# what each committed card is offered, the default first (docs/methods/automated_analysis_findings.md states the same)
OFFERED = {
    "batteries_lunch_grids": ["multiples", "lines"], "batteries_lunch": ["lines", "multiples"], "gas_sets_price": ["bars", "lines", "multiples"],
    "queue_divorce": ["stacked", "bars", "multiples"], "peak_hour_grids": ["multiples", "lines", "bars"], "peak_hour_moved": ["lines", "bars", "multiples"],
    "who_rescues_whom": ["bars", "multiples"], "negative_prices_west": ["lines", "bars", "multiples"], "batteries_curtailment": ["points"],
    "batteries_curtailment_hourly": ["lines", "bars", "multiples"], "impact_study": ["lines", "bars", "multiples"],
}
# the form the weekly run draws each public template in: the default of the template as an analysis
TEMPLATE_DEFAULT = {"peak_premium_block": "bars", "da_rt_spread_by_hour": "bars", "forecast_error": "lines", "curtailment_midday": "points",
                    "implied_heat_rate": "lines", "storage_evening_peak": "lines", "negative_price_hours": "bars", "deals_by_month": "stacked",
                    "datacenters_by_state": "stacked"}
ORDER_FLOW = ["lines", "bars", "stacked", "multiples", "points"]


def text_flow(*parts):
    with open(os.path.join(ROOT_FLOW, *parts), encoding="utf-8") as f:
        return f.read()


def fit_flow(s):
    """The fit rule, stated again in Python: the forms that can honestly show a chart of this shape, the default first."""
    if not s["native"]:
        return []
    if s["pairs"] or s["fixed"]:
        return [s["native"]]
    fit = {
        "lines": s["ordered"] and s["positions"] >= 2 and (s["oneUnit"] or s["native"] == "lines"),
        "bars": s["oneUnit"] and s["positions"] <= 31,
        "stacked": s["whole"],
        "multiples": 2 <= s["series"] <= 6,
        "points": False,
    }
    fit[s["native"]] = True
    return [s["native"]] + [f for f in ORDER_FLOW if f != s["native"] and fit[f]]


_RULES = {}


def rules_flow():
    if "v" not in _RULES:
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, os.path.join("scripts", "test-analysis-flow.mjs"), "--json"], cwd=os.path.join(ROOT_FLOW, "site"),
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        _RULES["v"] = json.loads(r.stdout)
    return _RULES["v"]


class StepOneHoldsEverything(unittest.TestCase):
    def test_every_analysis_of_the_catalogue_is_in_the_list_once(self):
        r = rules_flow()
        catalogue = json.loads(text_flow("site", "data", "findings", "catalogue.json"))
        ids = [v["id"] for i in r["items"] for v in i["versions"]]
        self.assertEqual(sorted(ids), sorted(c["id"] for c in catalogue))
        self.assertEqual(len(catalogue), 11)
        findings = [i for i in r["items"] if i["group"] == "findings"]
        self.assertEqual(len(findings), 7)
        self.assertEqual([i["id"] for i in r["items"] if i["group"] == "impact"], ["impact_study"])
        self.assertEqual(len(r["items"]), 18)
        # the three analyses with two versions, the current one first
        two = {i["id"]: [v["id"] for v in i["versions"]] for i in findings if len(i["versions"]) > 1}
        self.assertEqual(two, {"batteries_lunch": ["batteries_lunch_grids", "batteries_lunch"], "peak_hour_moved": ["peak_hour_grids", "peak_hour_moved"],
                               "batteries_curtailment": ["batteries_curtailment", "batteries_curtailment_hourly"]})

    def test_the_superseded_cards_are_a_version_and_the_current_form_comes_first(self):
        r = rules_flow()
        ts = text_flow("site", "lib", "findings.ts")
        sup = dict(re.findall(r'(\w+): "(\w+)"', re.search(r"SUPERSEDED: Record<string, string> = \{([^}]*)\}", ts).group(1)))
        self.assertEqual(sup, {"batteries_lunch": "batteries_lunch_grids", "peak_hour_moved": "peak_hour_grids"})
        by_id = {i["id"]: [v["id"] for v in i["versions"]] for i in r["items"]}
        for old, new in sup.items():
            self.assertEqual(by_id[old][0], new, old)
            self.assertIn(old, by_id[old])

    def test_the_ten_templates_are_analyses_in_the_weekly_runs_order(self):
        r = rules_flow()
        init = text_flow("warehouse", "analysis", "templates", "__init__.py")
        order = re.findall(r'"(\w+)"', re.search(r"ORDER = \[(.*?)\]", init, re.S).group(1))
        self.assertEqual(order, TEN)
        t = [i for i in r["items"] if i["group"] == "templates"]
        self.assertEqual([i["template"] for i in t], TEN)
        self.assertEqual([i["template"] for i in t if i.get("internal")], ["chokepoint_transits"])
        declared = {x["template"]: x for x in json.loads(text_flow("docs", "analysis", "templates.json"))["templates"]}
        for i in t:
            self.assertTrue(os.path.exists(os.path.join(ROOT_FLOW, "warehouse", "analysis", "templates", i["template"] + ".py")), i["template"])
            self.assertEqual(i["name"], declared[i["template"]]["title"])
        self.assertEqual(r["templates_order"], TEN)


class TheFormsAndTheDefault(unittest.TestCase):
    def test_five_forms_each_with_what_it_shows_and_what_it_fits(self):
        r = rules_flow()
        self.assertEqual([f["id"] for f in r["forms"]], ORDER_FLOW)
        for f in r["forms"]:
            self.assertTrue(f["name"] and f["shows"] and f["fits"], f["id"])
        self.assertEqual(r["native"], NATIVE_FLOW)
        self.assertEqual((r["max_bar_positions"], r["max_panels"]), (31, 6))

    def test_the_default_of_each_analysis_is_the_form_its_own_kind_declares(self):
        r = rules_flow()
        seen = set()
        for c in r["cards"]:
            if c["kind"] == "none":
                self.assertEqual(c["forms"], [])
                continue
            self.assertEqual(c["forms"][0], NATIVE_FLOW[c["kind"]], c["card_id"])
            seen.add(c["card_id"])
        self.assertTrue(set(OFFERED) <= seen, sorted(set(OFFERED) - seen))

    def test_each_analysis_is_offered_only_the_forms_that_fit(self):
        r = rules_flow()
        for c in r["cards"]:
            self.assertEqual(c["forms"], fit_flow(c["shape"]), c["card_id"])
            if c["card_id"] in OFFERED:
                self.assertEqual(c["forms"], OFFERED[c["card_id"]], c["card_id"])
        # a regression of points is not bars, and series in three units are not paired on one axis
        self.assertEqual(OFFERED["batteries_curtailment"], ["points"])
        self.assertNotIn("bars", OFFERED["batteries_lunch"])
        self.assertNotIn("lines", OFFERED["queue_divorce"])      # technologies are not an ordered axis
        self.assertNotIn("lines", OFFERED["who_rescues_whom"])   # nor are balancing authorities

    def test_each_templates_default_is_the_form_the_weekly_run_drew(self):
        r = rules_flow()
        self.assertEqual({t["template"]: t["forms"][0] for t in r["templates"]}, TEMPLATE_DEFAULT)
        for t in r["templates"]:
            self.assertEqual(t["forms"], fit_flow(t["shape"]), t["template"])
        by = {t["template"]: t["forms"] for t in r["templates"]}
        self.assertEqual(by["curtailment_midday"], ["points"])
        self.assertEqual(by["storage_evening_peak"], ["lines", "multiples"])   # two units: never paired on one axis
        self.assertEqual(r["internal_form"], {"chokepoint_transits": "lines"})
        self.assertIn('chart = {"kind": "line"', text_flow("warehouse", "analysis", "templates", "chokepoint_transits.py"))

    def test_the_rules_own_test_passes(self):
        exe = shutil.which("node")
        if not exe:
            raise unittest.SkipTest("node is not on this machine")
        r = subprocess.run([exe, os.path.join("scripts", "test-analysis-flow.mjs")], cwd=os.path.join(ROOT_FLOW, "site"), capture_output=True, text=True, timeout=300, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        self.assertNotIn("FAIL", r.stdout)


class NothingOfTheGalleryIsLost(unittest.TestCase):
    def test_every_template_every_input_and_every_weekly_file_is_reachable(self):
        r = rules_flow()
        index = json.loads(text_flow("docs", "analysis", "gallery", "index.json"))
        self.assertEqual([g["template"] for g in index["templates"]], TEN[:9])
        by = {t["template"]: t for t in r["templates"]}
        for g in index["templates"]:
            combos = list(g["combos"].values())
            t = by[g["template"]]
            self.assertEqual((t["combos"], t["held"]), (len(combos), sum(1 for c in combos if c["file"])), g["template"])
            self.assertTrue(t["file"], g["template"])                                    # the default inputs hold a chart
            for name in t["names"]:                                                      # every value the gallery offered is a choice
                self.assertEqual(t["choices"][name], sorted({str(c["params"][name]) for c in combos}), (g["template"], name))
            for c in combos:
                if c["file"]:
                    self.assertTrue(os.path.exists(os.path.join(ROOT_FLOW, "docs", "analysis", "gallery", *c["file"].split("/"))), c["file"])
        flow = text_flow("site", "components", "analysis", "RequestFlow.tsx")
        for bit in ("fetch(`/analysis-files/gallery/${file}`)", "cur.chart.facts.map", "cur.chart.source_line", "tpl.method", "data-template-input={p}", "(not held)", "combo.reason"):
            self.assertIn(bit, flow, bit)

    def test_the_gallery_component_is_retired_and_nothing_uses_it(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT_FLOW, "site", "components", "AnalysisGallery.tsx")))
        retired = text_flow("site", "app", "_retired", "analysis-gallery", "AnalysisGallery.tsx")
        self.assertIn("export function AnalysisGallery", retired)
        for base, _dirs, files in os.walk(os.path.join(ROOT_FLOW, "site")):
            if "node_modules" in base or ".next" in base or "_retired" in base:
                continue
            for f in files:
                if f.endswith((".ts", ".tsx")):
                    with open(os.path.join(base, f), encoding="utf-8") as h:
                        self.assertNotIn("AnalysisGallery }", h.read(), os.path.join(base, f))

    def test_the_page_holds_the_flow_and_drops_nothing_else(self):
        page = text_flow("site", "app", "analysis", "page.tsx")
        self.assertNotIn('<Section title="Template gallery">', page)
        self.assertNotIn('<Section title="Ask for a finding">', page)
        for bit in ("<RequestFlow catalogue={catalogue} templates={a.templates} gallery={a.gallery.templates}", "impactForm={impact ? <ImpactForm entry={impact} /> : null}",
                    "<RequestForm catalogue={catalogue} listOnly />", "<ScannerFound />", '<Section title="Archive: the chart of each week">', "This week&apos;s chart",
                    "!(c.id in SUPERSEDED)", "data-superseded={old.card_id}", "export const revalidate = 3600;"):
            self.assertIn(bit, page, bit)
        # the gallery was a section of /analysis, never an address of its own: no redirect, and the page stays in review
        self.assertRegex(text_flow("site", "lib", "release.ts"), r'"/analysis": "review"')
        self.assertNotIn("gallery", text_flow("site", "next.config.ts"))

    def test_the_weekly_run_still_writes_what_the_flow_reads(self):
        run = text_flow("warehouse", "analysis", "run.py")
        self.assertIn('gdir = os.path.join(DOCS, "gallery")', run)
        self.assertIn("docs/analysis/gallery/<template>/<params>.json and gallery/index.json", run)
        build = text_flow("site", "scripts", "build-content.mjs")
        self.assertIn('path.join(analysisDir, "gallery", "index.json")', build)


class WhatARequestCarries(unittest.TestCase):
    def test_the_form_travels_in_the_address_and_the_queue_is_as_it_was(self):
        route = text_flow("site", "app", "api", "analysis", "route.ts")
        self.assertNotIn("form", route.split("export async function POST")[1].split("export async function GET")[0].replace("format", ""))
        self.assertIn("for (const [k, inp] of Object.entries(entry.inputs))", route)
        flow = text_flow("site", "components", "analysis", "RequestFlow.tsx")
        for bit in ('put("analysis", item.id)', 'put("form", form && form !== def ? form : null)', 'put("request", request || null)', "window.history.replaceState",
                    'body: JSON.stringify({ kind: "run", finding: entry.id, params })', "<FormScope.Provider value={form ?? null}>", "<RequestCard key={request} requestId={request} wait />"):
            self.assertIn(bit, flow, bit)
        chart = text_flow("site", "components", "analysis", "FormChart.tsx")
        self.assertIn("u.searchParams.set(addressKey, f)", chart)
        self.assertIn("form === def ? <CardChart spec={spec} label={label} height={height} />", chart)   # the default form is the drawing it was
        self.assertIn('<FindingCard card={c} formKey="form" />', text_flow("site", "app", "analysis", "card", "[id]", "page.tsx"))
        card = text_flow("site", "components", "analysis", "FindingCard.tsx")
        self.assertIn("addressKey={formKey ?? `form.${card.card_id}`}", card)
        # the renderer's frame keeps the card's own drawing and markup (render.css reads the chart's siblings): the photographs do not change
        self.assertIn("? <CardChart spec={card.chart} label={card.title} height={420} />", card)

    def test_the_impact_studys_form_is_hosted_by_the_flow(self):
        form = text_flow("site", "components", "analysis", "ImpactForm.tsx")
        self.assertIn("const host = useContext(FlowHost);", form)
        self.assertIn("{host?.between ?? null}", form)
        self.assertIn("host?.onAsked(j.id)", form)
        self.assertLess(form.index("{host?.between ?? null}"), form.index('data-impact-submit="1"'))   # the picker stands before Ask
        flow = text_flow("site", "components", "analysis", "RequestFlow.tsx")
        self.assertIn("<FlowHost.Provider value={host}>{impactForm}</FlowHost.Provider>", flow)
        self.assertIn("between: item.id === IMPACT ? stepTwo : null", flow)

    def test_a_later_template_input_follows_an_earlier_one(self):
        lib = text_flow("site", "lib", "analysisflow.ts")
        self.assertIn("out[p] = keep && (keep.held || at < 0 || k <= at) ? wanted[p] : cs[0]?.value ?? \"\";", lib)
        self.assertIn("validParams(g, { ...tparams, [k]: v }, k)", text_flow("site", "components", "analysis", "RequestFlow.tsx"))

    def test_the_page_says_how_a_request_waits_and_that_a_template_does_not(self):
        flow = text_flow("site", "components", "analysis", "RequestFlow.tsx")
        self.assertIn("When the machine is", flow)
        self.assertIn("the request stays queued with the time it was asked", flow)
        self.assertIn("the chart is shown at once and no request is queued", flow)
        self.assertNotIn("data-request-submit", flow.split("{isTpl && !item.internal ? (")[1])   # a template has no Ask button


class TheWordsAndThePhone(unittest.TestCase):
    def test_the_preselected_form_is_called_a_default_and_nothing_is_advised(self):
        self.assertIn("Default for this analysis", text_flow("site", "components", "analysis", "FormPicker.tsx"))
        for rel in ("site/components/analysis/RequestFlow.tsx", "site/components/analysis/FormPicker.tsx", "site/components/analysis/FormChart.tsx",
                    "site/lib/analysisflow.ts", "site/app/analysis/page.tsx"):
            src = text_flow(*rel.split("/"))
            for word in ("ecommended", "you should", "we suggest", "best form", "better form", "ought to"):
                self.assertNotIn(word, src, (rel, word))
        note = text_flow("docs", "methods", "automated_analysis_findings.md")
        self.assertIn("## The request flow and the chart forms", note)
        self.assertIn("**The default rule.**", note)
        self.assertIn("**The fit rule: which forms are offered.**", note)

    def test_the_picker_is_usable_with_a_thumb(self):
        picker = text_flow("site", "components", "analysis", "FormPicker.tsx")
        self.assertIn("grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5", picker)
        self.assertGreaterEqual(picker.count("min-h-[44px]"), 2)
        for bit in ('data-form-prev="1"', 'data-form-next="1"', 'data-form-reset="1"', "aria-pressed={f === value}"):
            self.assertIn(bit, picker, bit)

    def test_no_em_dash_in_this_parts_files(self):
        for rel in FILES_FLOW:
            p = os.path.join(ROOT_FLOW, *rel.split("/"))
            if os.path.exists(p):
                self.assertNotIn(EM_FLOW, text_flow(*rel.split("/")), rel)


if __name__ == "__main__":
    unittest.main()
