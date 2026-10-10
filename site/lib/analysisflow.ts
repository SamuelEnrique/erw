// Energy Research Warehouse (ERW) site, session 182, part 4: step one of Automated Analysis's request flow, "what to
// analyze". One list: the analyses of the catalogue (each shown once in its current form, an earlier form of the same
// analysis kept as a choice of "Version"), the impact study, and the ten weekly chart templates folded in as analyses.
// Pure: no fs, no fetch, so the page, the node test and the browser check share it.
//
// What the list holds, and why. The catalogue (site/data/findings/catalogue.json) holds eleven analyses: the seven of
// sessions 170 and 174, the impact study of session 181, and session 182's three cards, which are new forms of three of
// the seven (two five-grid cards that supersede a single-grid card, and the hourly curtailment card beside the daily
// one). So the list shows seven findings, three of them with two versions (ten catalogue ids), the impact study (one
// id), and ten templates: eighteen entries, every catalogue id and every template in exactly one of them. A catalogue
// id this file does not name is listed on its own under its title, so a new analysis is never left out.
import type { CatalogueEntry } from "./findings";
import { PARAM_WORDS } from "./findingwords";

export type Tpl = { template: string; title: string; public: boolean; method: string; params: Record<string, { default: unknown; choices: unknown }>; tables: string[] };
export type Combo = { params: Record<string, unknown>; file: string | null; reason?: string };
export type GalleryEntry = { template: string; title: string; default: string; combos: Record<string, Combo> };
export type Version = { id: string; label: string };
export type FlowItem = { id: string; group: "findings" | "impact" | "templates"; name: string; versions: Version[]; template?: string; internal?: boolean };

export const GROUPS: { id: FlowItem["group"]; title: string; note: string }[] = [
  { id: "findings", title: "Findings", note: "A question put to the warehouse. Computed on request on the data machine, from the full histories." },
  { id: "impact", title: "Impact study", note: "Before and after an event, against a control series. Computed on request on the data machine." },
  { id: "templates", title: "Weekly chart templates", note: "Recomputed every week for every choice of their inputs. Shown at once: nothing waits in the queue." },
];

/** The seven findings in the page's order, each with its versions, the current one first. */
export const FINDINGS: { id: string; name: string; versions: Version[] }[] = [
  { id: "batteries_lunch", name: "Batteries and price spikes (Batteries ate their own lunch?)",
    versions: [{ id: "batteries_lunch_grids", label: "Five grids (current)" }, { id: "batteries_lunch", label: "One ERCOT hub (the earlier card)" }] },
  { id: "gas_sets_price", name: "How often gas sets the price (Gas sets the price less often?)", versions: [{ id: "gas_sets_price", label: "" }] },
  { id: "queue_divorce", name: "What became of interconnection requests (Till queue do us part)", versions: [{ id: "queue_divorce", label: "" }] },
  { id: "peak_hour_moved", name: "The hour of the day's highest price (The peak hour moved)",
    versions: [{ id: "peak_hour_grids", label: "Five grids (current)" }, { id: "peak_hour_moved", label: "ERCOT and CAISO, by hour (the earlier card)" }] },
  { id: "who_rescues_whom", name: "Flows between grids in an event (Who rescues whom)", versions: [{ id: "who_rescues_whom", label: "" }] },
  { id: "negative_prices_west", name: "Hours with a negative price, by hub (Negative prices march west)", versions: [{ id: "negative_prices_west", label: "" }] },
  { id: "batteries_curtailment", name: "Batteries and curtailment in CAISO (By how much do batteries cut curtailment)",
    versions: [{ id: "batteries_curtailment", label: "Day by day" }, { id: "batteries_curtailment_hourly", label: "Hour by hour" }] },
];
export const IMPACT = "impact_study";
/** The ten templates, in the order of warehouse/analysis/templates/__init__.py. */
export const TEMPLATES = ["peak_premium_block", "da_rt_spread_by_hour", "forecast_error", "curtailment_midday", "implied_heat_rate", "storage_evening_peak", "negative_price_hours",
  "deals_by_month", "datacenters_by_state", "chokepoint_transits"];
export const TEMPLATE_PREFIX = "template:";
/** The form an internal template's own code declares (chokepoint_transits.py: chart kind "line"). It is never drawn on
 *  the site, so the flow states its form and draws no example. */
export const INTERNAL_FORM: Record<string, "lines"> = { chokepoint_transits: "lines" };

/** Step one's list: the findings, the impact study, the templates. */
export function flowList(catalogue: CatalogueEntry[], templates: Tpl[]): FlowItem[] {
  const have = new Set(catalogue.map((c) => c.id));
  const named = new Set<string>([IMPACT]);
  const items: FlowItem[] = [];
  for (const f of FINDINGS) {
    const versions = f.versions.filter((v) => have.has(v.id));
    f.versions.forEach((v) => named.add(v.id));
    if (versions.length) items.push({ id: f.id, group: "findings", name: f.name, versions });
  }
  for (const c of catalogue) if (!named.has(c.id)) items.push({ id: c.id, group: "findings", name: c.title, versions: [{ id: c.id, label: "" }] });
  if (have.has(IMPACT)) items.push({ id: IMPACT, group: "impact", name: "Impact of an event on a series", versions: [{ id: IMPACT, label: "" }] });
  const order = (t: Tpl) => (TEMPLATES.indexOf(t.template) + 1) || 99;
  for (const t of [...templates].sort((a, b) => order(a) - order(b))) {
    items.push({ id: `${TEMPLATE_PREFIX}${t.template}`, group: "templates", name: t.title, versions: [], template: t.template, internal: !t.public });
  }
  return items;
}

/** Words for a template's input names and values: "Balancing authority", "ERCOT", "Strait of Hormuz". */
export const TEMPLATE_WORDS: Record<string, string> = {
  window: "Window (days)", months: "Months", top: "States shown", ba: "Balancing authority", ai_power: "Deals counted", chokepoint: "Chokepoint", vessels: "Vessels",
  erco: "ERCOT", ciso: "CAISO", isne: "ISO-NE", nyis: "NYISO", swpp: "SPP", us48: "Lower 48 states",
  chokepoint6: "Strait of Hormuz", chokepoint1: "Suez Canal", chokepoint2: "Panama Canal", n_tanker: "tankers", n_total: "all vessels",
};
export const nameWords = (k: string) => TEMPLATE_WORDS[k] ?? PARAM_WORDS[k] ?? k;
export const valueWords = (k: string, v: string) => (k === "ai_power" ? (v === "all" ? "All deals" : "AI power deals only") : TEMPLATE_WORDS[v] ?? PARAM_WORDS[v] ?? v);

/** The names of a template's inputs, in the order the weekly run wrote them. */
export const inputNames = (g: GalleryEntry | undefined) => (g ? Object.keys(Object.values(g.combos)[0]?.params ?? {}) : []);

/** The choices of one input given the inputs before it (a hub depends on the grid). Choices that hold a chart come
 *  first; a choice with no chart for any later input is kept and marked, because the weekly run tried it and says why. */
export function inputChoices(g: GalleryEntry, names: string[], params: Record<string, string>, p: string): { value: string; held: boolean }[] {
  const before = names.slice(0, names.indexOf(p));
  const seen = new Map<string, boolean>();
  for (const c of Object.values(g.combos)) {
    if (!before.every((b) => String(c.params[b]) === params[b])) continue;
    const v = String(c.params[p]);
    seen.set(v, (seen.get(v) ?? false) || Boolean(c.file));
  }
  const all = [...seen.entries()].map(([value, held]) => ({ value, held }));
  return [...all.filter((c) => c.held), ...all.filter((c) => !c.held)];
}

/** The chosen inputs made valid: an input whose value is not a choice takes the first choice that holds a chart. When
 *  one input was just changed (`changed`), each input after it keeps its value only if that value holds a chart under
 *  the new choice (ERCOT's North Hub is no hub of CAISO), else it takes the first that does. A choice that holds no
 *  chart can still be picked by hand, and the page then says why the weekly run wrote none. */
export function validParams(g: GalleryEntry, wanted: Record<string, string>, changed?: string): Record<string, string> {
  const names = inputNames(g);
  const at = changed ? names.indexOf(changed) : -1;
  const out: Record<string, string> = {};
  names.forEach((p, k) => {
    const cs = inputChoices(g, names, out, p);
    const keep = cs.find((c) => c.value === wanted[p]);
    out[p] = keep && (keep.held || at < 0 || k <= at) ? wanted[p] : cs[0]?.value ?? "";
  });
  return out;
}
export const defaultParams = (g: GalleryEntry): Record<string, string> =>
  validParams(g, Object.fromEntries(Object.entries(g.combos[g.default]?.params ?? {}).map(([k, v]) => [k, String(v)])));
export const comboOf = (g: GalleryEntry, params: Record<string, string>): Combo | undefined =>
  Object.values(g.combos).find((c) => Object.keys(c.params).every((n) => String(c.params[n]) === params[n]));
