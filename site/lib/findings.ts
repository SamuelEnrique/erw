// Energy Research Warehouse (ERW) site, session 170: Automated Analysis findings. The cards are JSON files the engine
// wrote (warehouse/analysis/findings/run_finding.py) into data/findings/, read here at build; the downloads sit in
// public/findings/. The catalogue (data/findings/catalogue.json) says what a person may ask for on /analysis.
import fs from "node:fs";
import path from "node:path";
import type { ChartSpec } from "./findingchart";

export type Callout = { label: string; before: { period: string; text: string }; after: { period: string; text: string }; unit: string };
export type EffectRow = { measure: string; coef_per_gw: number; se: number; p: number; n: number; r2: number };
export type Card = {
  id: string; card_id: string; title: string; kind: "visual" | "econometric"; subtitle: string;
  params: Record<string, string | number>; inputs_words: Record<string, string>;
  chart: ChartSpec; callouts: Callout[]; why: string; footnote: string; numbers: Record<string, number | string | null>;
  effect_table?: { columns: string[]; rows: EffectRow[]; in_words: string };
  placeholders?: { grid: string; words: string; text: string }[];
  source_line: string; tables: string[]; computed_at: string; method: string;
  downloads: { csv: string; python: string; stata: string }; csv_sha256: string;
};
export type CatalogueInput = { label: string; default: string | number; choices: (string | number)[]; words: Record<string, string> };
export type CatalogueEntry = { id: string; title: string; kind: string; tables: string[]; inputs: Record<string, CatalogueInput> };

const DIR = path.join(process.cwd(), "data", "findings");
export const METHOD = "/data/methods/automated_analysis_findings";
export const ORDER = ["batteries_lunch", "gas_sets_price", "queue_divorce", "peak_hour_moved", "who_rescues_whom", "negative_prices_west", "batteries_curtailment"]; // session 174: four more

/** Every card file, the default cards first in the engine's order, then the cards with chosen inputs. */
export function loadCards(): Card[] {
  if (!fs.existsSync(DIR)) return [];
  const cards = fs.readdirSync(DIR)
    .filter((f) => f.endsWith(".json") && f !== "catalogue.json")
    .map((f) => JSON.parse(fs.readFileSync(path.join(DIR, f), "utf8")) as Card);
  const rank = (c: Card) => (ORDER.indexOf(c.id) + 1 || 99) + (c.card_id === c.id ? 0 : 0.5);
  return cards.sort((a, b) => rank(a) - rank(b) || a.card_id.localeCompare(b.card_id));
}

export function loadCard(cardId: string): Card | null {
  const f = path.join(DIR, `${cardId}.json`);
  if (!/^[a-z0-9_.-]+$/i.test(cardId) || !fs.existsSync(f)) return null;
  return JSON.parse(fs.readFileSync(f, "utf8")) as Card;
}

export function loadCatalogue(): CatalogueEntry[] {
  const f = path.join(DIR, "catalogue.json");
  return fs.existsSync(f) ? (JSON.parse(fs.readFileSync(f, "utf8")) as CatalogueEntry[]) : [];
}

/** The ISO week (YYYY-Www, UTC) the next Sunday Roundup is written for: the week that holds today, Monday to Sunday. */
export function roundupWeek(now = new Date()): string {
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
  const day = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - day);
  const y0 = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const w = Math.ceil(((d.getTime() - y0.getTime()) / 86400000 + 1) / 7);
  return `${d.getUTCFullYear()}-W${String(w).padStart(2, "0")}`;
}

/** A card's chosen inputs in human words: "ERCOT North Hub, from 2019", not "HB_NORTH". */
export function inputWords(card: Card): string {
  return Object.values(card.inputs_words).join(", ");
}

export { PARAM_WORDS, paramWords } from "./findingwords";
