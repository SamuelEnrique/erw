// Energy Research Warehouse (ERW) site, session 150: Thesis Builder (/thesis), the data providers of the fetch stage.
//
// Session 135 wrote the stage for PitchBook alone (lib/thesis/pitchbook.ts, the format erw-pitchbook-1). This file lifts
// what is common into one interface and adds two providers beside it. A provider has: an id and a label, the request
// text it makes from a run, the format id it expects back, a reader (parser and validator) for what the person pastes,
// a mapping from its fields to the run's facts, and its terms line.
//
//   PitchBook    erw-pitchbook-1   the first provider. Its request text is the text the run itself wrote and saved
//                                  (never made again here), and a pasted answer is read by validatePitchbook of
//                                  lib/thesis/pitchbook.ts, which this session does not touch.
//   Harmonic     erw-harmonic-1    built on Harmonic's public documentation: the tool categories of its connector
//                                  (enrichment, search, lookup, saved searches) and its published data fields.
//   Crunchbase   erw-crunchbase-1  built on Crunchbase's public documentation: its connector's tool reference, its
//                                  data dictionary and the schema of an organization.
//
// No provider is ever called from here: a person copies the request into a Claude chat that holds the provider's
// connector under their own account, and pastes the answer back. Pure functions, no I/O, so a script can test them as
// they are (scripts/test-thesis-providers.mjs).
//
// THE RULE FOR A FIELD (Harmonic and Crunchbase). Only a field the provider's own documentation names is mapped, under
// the documented name and only when its value has the documented shape. Everything else that is pasted is kept exactly
// as given under "not_mapped", in its own nesting, and is never read as a fact. What is refused is a fault of the
// envelope, which is the ERW's own: a wrong format, another run, no date, no company list, a company with no name.
//
// THE RULE FOR A FACT. Every fact a provider's result adds carries the provider's id, the format, the time pasted and
// the hash of the pasted text. Where two providers give the same fact differently both are kept and the fact is marked
// as a disagreement: none is averaged, preferred or dropped. A record with no provider named is PitchBook's (every
// record written before this session is), read so in code: nothing stored is rewritten.
import { FORMAT as PB_FORMAT, LABEL as PB_LABEL, MAX_ADDITIONAL, MAX_COMPANIES, MAX_NAME, RECEIVED_NOTE as PB_NOTE, extractJson, validatePitchbook } from "./pitchbook";
import type { PbCompany, PitchbookPayload } from "./pitchbook";
import { arr, nameKey, num, pbFigures, str, whenWords } from "./view";

export type ProviderId = "pitchbook" | "harmonic" | "crunchbase";
export const PROVIDER_IDS: readonly ProviderId[] = ["pitchbook", "harmonic", "crunchbase"];
export const DEFAULT_PROVIDER: ProviderId = "pitchbook";

export type Json = null | boolean | number | string | Json[] | { [k: string]: Json };
type Obj = Record<string, unknown>;
const isObject = (v: unknown): v is Obj => typeof v === "object" && v !== null && !Array.isArray(v);
const absent = (v: unknown) => v === undefined || v === null;

// ---------------------------------------------------------------------------------------------------------------
// the documentation each format is built on (saved under runs/session150/docs/ with these hashes; the method note
// docs/methods/thesis_builder.md lists them again with what each field rests on)
// ---------------------------------------------------------------------------------------------------------------

export type DocRef = { id: string; title: string; url: string; retrieved: string; sha256: string };
export const DOCS: Record<string, DocRef> = {
  H1: { id: "H1", title: "Harmonic MCP Server, Getting Started Guide", url: "https://support.harmonic.ai/en/articles/12785899-harmonic-mcp-server-getting-started-guide", retrieved: "2026-10-08T00:06:33Z", sha256: "cb1904e354ffc95f39a93ba8d9c1cb51138cb56a2a180b911e8045fffaf43cee" },
  H2: { id: "H2", title: "Harmonic Data Fields", url: "https://support.harmonic.ai/en/articles/6480774-harmonic-data-fields", retrieved: "2026-10-08T00:08:20Z", sha256: "62fd92f7387a6a99a4573cab6deb3c30a2da96c647eb33cc41163089f23a2b3a" },
  HT: { id: "HT", title: "Harmonic Terms of Service", url: "https://harmonic.ai/legal/terms-of-service", retrieved: "2026-10-08T00:08:04Z", sha256: "6b8ce63d932543628efe82712bdd17d994a4c0ccd4568a1cbb00ed55114400cc" },
  C1: { id: "C1", title: "Crunchbase MCP, Tool Reference", url: "https://data.crunchbase.com/docs/tool-reference.md", retrieved: "2026-10-08T00:07:04Z", sha256: "afa2d923599440c7208563d11a1f3fc6edec6fcda9b642a2978e29b5e32fb7a1" },
  C2: { id: "C2", title: "Crunchbase Data Dictionary", url: "https://data.crunchbase.com/docs/data-dictionary.md", retrieved: "2026-10-08T00:07:55Z", sha256: "b12d902bbd7f8cf48a56cfd3b6e7c1d11bf844dc1985157af85c3e3f23ced7de" },
  C3: { id: "C3", title: "Crunchbase API reference, Lookup an Organization (Advanced Financials Package)", url: "https://data.crunchbase.com/reference/getorganization-2.md", retrieved: "2026-10-08T00:07:57Z", sha256: "0b3436ada397b5d474eefd1b43f425522ba522061d57d8f70912c6721195f08c" },
  CT: { id: "CT", title: "Crunchbase License Agreement", url: "https://data.crunchbase.com/docs/license-agreement.md", retrieved: "2026-10-08T00:07:10Z", sha256: "75fdb70887941ece822b8c693626bf2922b46fcd1f9c67ce007f172c246e2b64" },
};

// ---------------------------------------------------------------------------------------------------------------
// the terms line of each provider: the data is the person's own licensed copy, and the provider's own sentence on
// redistribution where its public terms page answered a plain request
// ---------------------------------------------------------------------------------------------------------------

const OWN = (label: string) => `${label} figures here are your own licensed copy: brought by you from your own account, shown to you, and not published, redistributed or kept in the public warehouse.`;
export const TERMS: Record<ProviderId, string> = {
  pitchbook: `${OWN("PitchBook")} PitchBook's public terms page was not read: it answered a plain request with HTTP 403 on 8 October 2026.`,
  harmonic: `${OWN("Harmonic")} Harmonic's Terms of Service (read 8 October 2026): "You will not (and will not allow anyone else to): [...] provide, sell, transfer, sublicense, lend, distribute, or otherwise allow others to access or use the Services or the data obtained through the Services;"`,
  crunchbase: `${OWN("Crunchbase")} Crunchbase's License Agreement (read 8 October 2026): "Except as otherwise expressly set forth herein, Licensee may not license, sublicense, sell, offer to sell, distribute or otherwise provide any Crunchbase data to any third parties."`,
};
const NOTE = (label: string) => `Figures as returned from ${label} through the user's own account; not checked by the ERW.`;

// ---------------------------------------------------------------------------------------------------------------
// the fields that are mapped, each with the kind of value its documentation states and the page that states it
// ---------------------------------------------------------------------------------------------------------------

/** text: a string. long: a string, cut at 1,200 characters. date: "YYYY", "YYYY-MM", "YYYY-MM-DD" or a timestamp.
 * count: a whole number, zero or more. amount: a finite number, zero or more. bool: true or false. texts: a list of
 * strings. id: a string or a whole number, kept as text. money, cbdate, ident, idents, link: Crunchbase's objects, as
 * its organization schema writes them. */
type Kind = "text" | "long" | "date" | "count" | "amount" | "bool" | "texts" | "id" | "money" | "cbdate" | "ident" | "idents" | "link";
export type Spec = readonly [path: string, kind: Kind, doc: string];

export const HARMONIC_COMPANY: readonly Spec[] = [
  ["id", "id", "H2"], ["entity_urn", "text", "H2"], ["name", "text", "H2"], ["legal_name", "text", "H2"], ["description", "long", "H2"], ["short_description", "long", "H2"],
  ["website.url", "text", "H2"], ["website.domain", "text", "H2"], ["founding_date.date", "date", "H2"], ["founding_date.granularity", "text", "H2"],
  ["headcount", "count", "H2"], ["ownership_status", "text", "H2"], ["company_type", "text", "H2"], ["stage", "text", "H2"],
  ["location.location", "text", "H2"], ["location.city", "text", "H2"], ["location.state", "text", "H2"], ["location.country", "text", "H2"], ["headquarters", "text", "H2"],
  ["funding.funding_total", "amount", "H2"], ["funding.num_funding_rounds", "count", "H2"], ["funding.investors", "texts", "H2"], ["funding.last_funding_at", "date", "H2"],
  ["funding.last_funding_type", "text", "H2"], ["funding.last_funding_total", "amount", "H2"], ["funding.funding_stage", "text", "H2"],
  ["funding.valuation_info.amount", "amount", "H2"], ["funding.valuation_info.source", "text", "H2"],
  ["socials.linkedin.url", "text", "H2"], ["socials.crunchbase.url", "text", "H2"], ["socials.pitchbook.url", "text", "H2"],
];
/** A round of a company's funding_rounds (Harmonic's deal data, an add-on of its plans). */
export const HARMONIC_ROUND: readonly Spec[] = [
  ["entity_urn", "text", "H2"], ["announcement_date", "date", "H2"], ["funding_round_type", "text", "H2"], ["funding_amount", "amount", "H2"], ["funding_currency", "text", "H2"],
  ["valuation_info.amount", "amount", "H2"], ["post_money_valuation", "amount", "H2"], ["source_url", "text", "H2"], ["completion_status", "text", "H2"],
];
export const HARMONIC_ROUND_INVESTOR: readonly Spec[] = [["investor_name", "text", "H2"], ["is_lead", "bool", "H2"], ["entity_urn", "text", "H2"], ["investor_urn", "text", "H2"]];
export const HARMONIC_PERSON: readonly Spec[] = [
  ["id", "id", "H2"], ["entity_urn", "text", "H2"], ["full_name", "text", "H2"], ["first_name", "text", "H2"], ["last_name", "text", "H2"],
  ["linkedin_headline", "text", "H2"], ["socials.LINKEDIN.url", "text", "H2"],
];
export const HARMONIC_EXPERIENCE: readonly Spec[] = [
  ["title", "text", "H2"], ["department", "text", "H2"], ["company_name", "text", "H2"], ["is_current_position", "bool", "H2"], ["start_date", "date", "H2"], ["end_date", "date", "H2"],
];
export const HARMONIC_INVESTOR: readonly Spec[] = [
  ["id", "id", "H2"], ["entity_urn", "text", "H2"], ["type", "text", "H2"], ["aum_amount_usd", "amount", "H2"], ["check_size_min_usd", "amount", "H2"], ["check_size_max_usd", "amount", "H2"],
  ["investment_count", "count", "H2"], ["exit_count", "count", "H2"], ["num_portfolio_companies", "count", "H2"], ["most_recent_investment_date", "date", "H2"],
];

export const CRUNCHBASE_ORGANIZATION: readonly Spec[] = [
  ["identifier", "ident", "C3"], ["uuid", "text", "C2"], ["permalink", "text", "C2"], ["name", "text", "C2"], ["legal_name", "text", "C2"], ["short_description", "long", "C2"], ["description", "long", "C2"],
  ["founded_on", "cbdate", "C3"], ["num_employees_enum", "text", "C3"], ["funding_total", "money", "C3"], ["equity_funding_total", "money", "C3"],
  ["last_funding_at", "date", "C2"], ["last_funding_type", "text", "C2"], ["last_funding_total", "money", "C3"], ["funding_stage", "text", "C2"], ["num_funding_rounds", "count", "C2"],
  ["valuation", "money", "C3"], ["valuation_date", "date", "C2"], ["location_identifiers", "idents", "C3"], ["founder_identifiers", "idents", "C3"], ["investor_identifiers", "idents", "C3"],
  ["num_investors", "count", "C2"], ["num_lead_investors", "count", "C2"], ["operating_status", "text", "C2"], ["status", "text", "C2"], ["company_type", "text", "C2"],
  ["website_url", "text", "C2"], ["website", "link", "C3"], ["url", "text", "C1"],
];
export const CRUNCHBASE_ROUND: readonly Spec[] = [
  ["identifier", "ident", "C3"], ["announced_on", "date", "C3"], ["investment_type", "text", "C3"], ["money_raised", "money", "C3"], ["post_money_valuation", "money", "C3"],
  ["pre_money_valuation", "money", "C3"], ["lead_investor_identifiers", "idents", "C3"], ["investor_identifiers", "idents", "C3"], ["num_investors", "count", "C3"], ["url", "text", "C1"],
];
export const CRUNCHBASE_PERSON: readonly Spec[] = [
  ["identifier", "ident", "C3"], ["name", "text", "C3"], ["first_name", "text", "C3"], ["last_name", "text", "C3"], ["primary_job_title", "text", "C3"], ["linkedin", "link", "C3"], ["url", "text", "C1"],
];

const CAP_TEXT = 400, CAP_LONG = 1200, CAP_LIST = 60;
export const MAX_PEOPLE = 40, MAX_ROUNDS = 60, MAX_LISTS = 20, MAX_RESULTS = 100;
const DATE = /^\d{4}(?:-\d{2}(?:-\d{2}(?:[T ][0-9:.+\-Z]{0,24})?)?)?$/;
const words = (v: string, cap: number) => v.replace(/\s+/g, " ").trim().slice(0, cap);
const only = (o: Obj, keys: readonly string[]) => Object.keys(o).every((k) => keys.includes(k));
const IDENT_KEYS = ["value", "permalink", "uuid", "entity_def_id", "image_id", "location_type"] as const;

function ident(v: unknown): Json | undefined {
  if (!isObject(v) || !only(v, IDENT_KEYS) || typeof v.value !== "string" || !words(v.value, CAP_TEXT)) return undefined;
  const out: { [k: string]: Json } = {};
  for (const k of IDENT_KEYS) {
    if (absent(v[k])) continue;
    if (typeof v[k] !== "string") return undefined;
    out[k] = words(v[k] as string, CAP_TEXT);
  }
  return out;
}
/** The value of a documented field as it is kept, or undefined when it does not have the documented shape. */
function fit(v: unknown, kind: Kind): Json | undefined {
  switch (kind) {
    case "text": case "long": {
      if (typeof v !== "string") return undefined;
      const s = words(v, kind === "long" ? CAP_LONG : CAP_TEXT);
      return s || undefined;
    }
    case "date": return typeof v === "string" && DATE.test(v.trim()) ? v.trim() : undefined;
    case "count": return typeof v === "number" && Number.isInteger(v) && v >= 0 ? v : undefined;
    case "amount": return typeof v === "number" && Number.isFinite(v) && v >= 0 ? v : undefined;
    case "bool": return typeof v === "boolean" ? v : undefined;
    case "id": return typeof v === "string" && words(v, CAP_TEXT) ? words(v, CAP_TEXT) : typeof v === "number" && Number.isInteger(v) && v >= 0 ? String(v) : undefined;
    case "texts": {
      if (!Array.isArray(v) || v.length > CAP_LIST || !v.every((x) => typeof x === "string")) return undefined;
      const out = (v as string[]).map((x) => words(x, CAP_TEXT)).filter(Boolean);
      return out.length ? out : undefined;
    }
    case "money": {
      if (!isObject(v) || !only(v, ["value", "currency", "value_usd"])) return undefined;
      if (typeof v.value !== "number" || !Number.isFinite(v.value) || v.value < 0 || typeof v.currency !== "string" || !/^[A-Za-z]{3}$/.test(v.currency.trim())) return undefined;
      if (!absent(v.value_usd) && (typeof v.value_usd !== "number" || !Number.isFinite(v.value_usd) || v.value_usd < 0)) return undefined;
      return absent(v.value_usd) ? { value: v.value, currency: v.currency.trim().toUpperCase() } : { value: v.value, currency: v.currency.trim().toUpperCase(), value_usd: v.value_usd as number };
    }
    case "cbdate": {
      if (!isObject(v) || !only(v, ["value", "precision"]) || typeof v.precision !== "string" || !["none", "year", "month", "day"].includes(v.precision)) return undefined;
      if (absent(v.value)) return v.precision === "none" ? { precision: "none" } : undefined;
      return typeof v.value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v.value.trim()) ? { value: v.value.trim(), precision: v.precision } : undefined;
    }
    case "ident": return ident(v);
    case "idents": {
      if (!Array.isArray(v) || v.length > CAP_LIST) return undefined;
      const out = v.map(ident);
      return out.length && out.every((x) => x !== undefined) ? (out as Json[]) : undefined;
    }
    case "link": {
      if (!isObject(v) || !only(v, ["value", "label"]) || typeof v.value !== "string" || !words(v.value, CAP_TEXT)) return undefined;
      if (!absent(v.label) && typeof v.label !== "string") return undefined;
      return absent(v.label) ? { value: words(v.value, CAP_TEXT) } : { value: words(v.value, CAP_TEXT), label: words(v.label as string, CAP_TEXT) };
    }
  }
}

export type Rec = { record: Record<string, Json>; not_mapped?: Record<string, Json> };
const copy = (v: unknown): Json => JSON.parse(JSON.stringify(v ?? null)) as Json;
const emptied = (o: unknown) => isObject(o) && Object.keys(o).length === 0;

/**
 * A record of a provider read against the documented fields: `record` holds each documented field that has its
 * documented shape, under its documented path; `rest` is the record as given without those fields, in its own
 * nesting, untouched. A null is no value: it is neither kept nor counted as not mapped.
 */
function take(given: unknown, specs: readonly Spec[]): { record: Record<string, Json>; rest: Obj } {
  const rest = (isObject(given) ? copy(given) : {}) as Obj;
  const record: Record<string, Json> = {};
  for (const [path, kind] of specs) {
    const keys = path.split(".");
    let at: unknown = rest;
    for (const k of keys) at = isObject(at) && Object.prototype.hasOwnProperty.call(at, k) ? at[k] : undefined;
    if (at === undefined) continue;
    const kept = at === null ? null : fit(at, kind);
    if (kept === undefined) continue;
    if (kept !== null) record[path] = kept;
    // the field leaves `rest`, and a parent left empty by it goes too
    const owners: Obj[] = [rest];
    let o: unknown = rest;
    for (const k of keys.slice(0, -1)) { o = (o as Obj)[k]; owners.push(o as Obj); }
    delete owners[owners.length - 1][keys[keys.length - 1]];
    for (let i = owners.length - 1; i > 0; i -= 1) if (emptied(owners[i])) delete owners[i - 1][keys[i - 1]];
  }
  return { record, rest };
}
const rec = (record: Record<string, Json>, rest: Obj): Rec => (Object.keys(rest).length ? { record, not_mapped: rest as Record<string, Json> } : { record });
const without = (o: Obj, ...keys: string[]): Obj => Object.fromEntries(Object.entries(o).filter(([k]) => !keys.includes(k)));
/** A list of records inside a record (rounds, people, experience): each read on its own. A list that is not one of
 * records, or is longer than its cap, stays where it is, as given. An empty list is no value. */
function takeList<R extends Rec>(owner: Obj, key: string, cap: number, read: (x: Obj) => R): R[] | undefined {
  const v = owner[key];
  if (Array.isArray(v) && !v.length) delete owner[key];
  if (!Array.isArray(v) || !v.length || v.length > cap || !v.every(isObject)) return undefined;
  delete owner[key];
  return (v as Obj[]).map(read);
}
/** The record under `key` of an entry, read against its fields. What is not mapped stays under `key`, as given; a
 * value that is not a record at all stays whole. */
function takeRecord(owner: Obj, key: string, specs: readonly Spec[]): { record: Record<string, Json>; rest: Obj | null } {
  const v = owner[key];
  if (!isObject(v)) {
    if (absent(v)) delete owner[key];
    return { record: {}, rest: null };
  }
  const t = take(v, specs);
  owner[key] = t.rest;
  return t;
}
/** Once the lists inside a record are read too: a record left with nothing leaves its entry. */
const settle = (owner: Obj, key: string) => { if (emptied(owner[key])) delete owner[key]; };

// ---------------------------------------------------------------------------------------------------------------
// what is stored for Harmonic and Crunchbase
// ---------------------------------------------------------------------------------------------------------------

export type PvRound = Rec & { investors?: Rec[] };
export type PvPerson = Rec & { experience?: Rec[] };
export type PvCompany = Rec & { name: string; found: boolean; why?: string; rounds?: PvRound[]; people?: PvPerson[] };
export type PvResult = Rec & { name: string };
export type PvList = { name: string; of: "companies" | "investors" | "people"; results: PvResult[] };
export type ProviderPayload = {
  format: string; provider: ProviderId; run_id: string; pulled_on: string; label: string; received_note: string;
  companies: PvCompany[]; additional_companies: PvCompany[]; lists: PvList[]; not_mapped?: Record<string, Json>;
};
export type AnyPayload = PitchbookPayload | ProviderPayload;
export type Read = { ok: true; payload: AnyPayload } | { ok: false; reason: string };

class Refused extends Error {}
const refuse = (reason: string): never => { throw new Refused(reason); };
const guarded = (f: () => AnyPayload): Read => {
  try { return { ok: true, payload: f() }; } catch (e) {
    if (e instanceof Refused) return { ok: false, reason: e.message };
    throw e;
  }
};
function day(v: unknown): string {
  if (typeof v !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(v.trim())) refuse('"pulled_on" is required: the day the figures were pulled, written "YYYY-MM-DD".');
  const s = (v as string).trim(), [y, m, d] = s.split("-").map(Number), t = new Date(Date.UTC(y, m - 1, d));
  if (y < 1900 || t.getUTCFullYear() !== y || t.getUTCMonth() !== m - 1 || t.getUTCDate() !== d) refuse('"pulled_on" is not a day of the calendar.');
  return s;
}
function nameOf(o: Obj, where: string): string {
  if (typeof o.name !== "string") refuse(`${where}.name is required and must be text.`);
  const name = words(o.name as string, MAX_NAME + 1);
  if (!name) refuse(`${where}.name is empty.`);
  if (name.length > MAX_NAME) refuse(`${where}.name is longer than ${MAX_NAME} characters.`);
  return name;
}
/** The envelope, which is the ERW's own and is checked strictly; the provider's records inside it are read by `entry`. */
function envelope(input: unknown, p: { id: ProviderId; label: string; format: string }, runId: string, known: readonly string[],
  entry: (o: Obj, name: string) => Omit<PvCompany, "name" | "found" | "why">, lists: (o: Obj) => PvList[]): ProviderPayload {
  if (!isObject(input)) refuse("The answer must be one JSON object.");
  const o = copy(input) as Obj;
  if (o.format !== p.format) refuse(`"format" must be "${p.format}".`);
  if (typeof o.run_id !== "string" || o.run_id !== runId) refuse('"run_id" is not the run this answer is submitted for.');
  const pulled = day(o.pulled_on);
  if (!Array.isArray(o.companies)) refuse('"companies" is required and must be a list.');
  const cs = o.companies as unknown[];
  if (cs.length > MAX_COMPANIES) refuse(`"companies" holds ${cs.length}; at most ${MAX_COMPANIES}.`);
  if (!absent(o.additional_companies) && !Array.isArray(o.additional_companies)) refuse('"additional_companies" must be a list.');
  const as = (o.additional_companies ?? []) as unknown[];
  if (as.length > MAX_ADDITIONAL) refuse(`"additional_companies" holds ${as.length}; at most ${MAX_ADDITIONAL}.`);
  const one = (v: unknown, where: string, additional: boolean): PvCompany => {
    if (!isObject(v)) refuse(`${where} must be an object.`);
    const c = v as Obj;
    const name = nameOf(c, where);
    if (typeof c.found !== "boolean") refuse(`${where}.found is required and must be true or false.`);
    const found = c.found as boolean;
    let why: string | undefined;
    if (additional) {
      why = typeof c.why === "string" ? words(c.why, CAP_TEXT) : "";
      if (!why) refuse(`${where}.why is required and must be text.`);
    }
    const given = without(c, "name", "found", ...(additional ? ["why"] : []));
    if (!found) return Object.keys(given).length ? { name, found, record: {}, not_mapped: given as Record<string, Json> } : { name, found, record: {} };
    const read = entry(given, name);
    return why ? { name, found, why, ...read } : { name, found, ...read };
  };
  const companies = cs.map((c, i) => one(c, `companies[${i}]`, false));
  const additional = as.map((c, i) => one(c, `additional_companies[${i}]`, true));
  const held = lists(o);
  const rest = Object.fromEntries(Object.entries(o).filter(([k]) => !["format", "run_id", "pulled_on", "companies", "additional_companies", ...known].includes(k)));
  const out: ProviderPayload = { format: p.format, provider: p.id, run_id: runId, pulled_on: pulled, label: p.label, received_note: NOTE(p.label), companies, additional_companies: additional, lists: held };
  if (Object.keys(rest).length) out.not_mapped = rest as Record<string, Json>;
  return out;
}
/** An entry once its parts are read: what is left of it, in its own nesting, is what was not mapped. */
const entryOf = (given: Obj, record: Record<string, Json>, people?: PvPerson[], rounds?: PvRound[]): Omit<PvCompany, "name" | "found" | "why"> => {
  const out: Omit<PvCompany, "name" | "found" | "why"> = { record };
  if (rounds) out.rounds = rounds;
  if (people) out.people = people;
  if (Object.keys(given).length) out.not_mapped = given as Record<string, Json>;
  return out;
};

// ---- Harmonic, erw-harmonic-1
function harmonicPerson(x: Obj): PvPerson {
  const { record, rest } = take(x, HARMONIC_PERSON);
  const experience = takeList<Rec>(rest, "experience", 80, (e) => { const t = take(e, HARMONIC_EXPERIENCE); return rec(t.record, t.rest); });
  return experience ? { ...rec(record, rest), experience } : rec(record, rest);
}
/** A Harmonic company record under `key` of its owner, with the rounds of its funding_rounds. */
function harmonicCompany(owner: Obj, key: string): { record: Record<string, Json>; rounds?: PvRound[] } {
  const { record, rest } = takeRecord(owner, key, HARMONIC_COMPANY);
  if (!rest) return { record };
  const rounds = takeList<PvRound>(rest, "funding_rounds", MAX_ROUNDS, (r) => {
    const t = take(r, HARMONIC_ROUND);
    const investors = takeList<Rec>(t.rest, "investors", CAP_LIST, (i) => { const u = take(i, HARMONIC_ROUND_INVESTOR); return rec(u.record, u.rest); });
    return investors ? { ...rec(t.record, t.rest), investors } : rec(t.record, t.rest);
  });
  settle(owner, key);
  return rounds ? { record, rounds } : { record };
}
const HARMONIC_OF = ["companies", "investors", "people"] as const;
function harmonicLists(o: Obj): PvList[] {
  if (absent(o.saved_searches)) return [];
  if (!Array.isArray(o.saved_searches)) refuse('"saved_searches" must be a list.');
  const ls = o.saved_searches as unknown[];
  if (ls.length > MAX_LISTS) refuse(`"saved_searches" holds ${ls.length}; at most ${MAX_LISTS}.`);
  return ls.map((l, i) => {
    const where = `saved_searches[${i}]`;
    if (!isObject(l)) refuse(`${where} must be an object.`);
    const s = l as Obj;
    const name = nameOf(s, where);
    if (typeof s.of !== "string" || !(HARMONIC_OF as readonly string[]).includes(s.of)) refuse(`${where}.of must be "companies", "investors" or "people".`);
    const of = s.of as PvList["of"];
    if (!Array.isArray(s.results)) refuse(`${where}.results is required and must be a list.`);
    const rs = s.results as unknown[];
    if (rs.length > MAX_RESULTS) refuse(`${where}.results holds ${rs.length}; at most ${MAX_RESULTS}.`);
    const results = rs.map((r, j) => {
      if (!isObject(r)) refuse(`${where}.results[${j}] must be an object.`);
      const x = r as Obj;
      const n = nameOf(x, `${where}.results[${j}]`);
      const other = without(x, "name");
      let record: Record<string, Json>;
      if (of === "companies") record = takeRecord(other, "record", HARMONIC_COMPANY).record;      // a result's rounds are not read: they stay as given
      else record = takeRecord(other, "record", of === "people" ? HARMONIC_PERSON : HARMONIC_INVESTOR).record;
      settle(other, "record");
      return Object.keys(other).length ? { name: n, record, not_mapped: other as Record<string, Json> } : { name: n, record };
    });
    return { name, of, results };
  });
}
export function validateHarmonic(input: unknown, runId: string): Read {
  return guarded(() => envelope(input, PROVIDERS.harmonic, runId, ["saved_searches"], (given) => {
    const c = harmonicCompany(given, "company");
    const people = takeList<PvPerson>(given, "people", MAX_PEOPLE, harmonicPerson);
    return entryOf(given, c.record, people, c.rounds);
  }, harmonicLists));
}

// ---- Crunchbase, erw-crunchbase-1
export function validateCrunchbase(input: unknown, runId: string): Read {
  return guarded(() => envelope(input, PROVIDERS.crunchbase, runId, [], (given) => {
    const { record } = takeRecord(given, "organization", CRUNCHBASE_ORGANIZATION);
    settle(given, "organization");
    let people: PvPerson[] | undefined, rounds: PvRound[] | undefined;
    if (isObject(given.cards)) {
      const cards = given.cards as Obj;
      people = takeList<PvPerson>(cards, "founders", MAX_PEOPLE, (x) => { const t = take(x, CRUNCHBASE_PERSON); return rec(t.record, t.rest); });
      rounds = takeList<PvRound>(cards, "raised_funding_rounds", MAX_ROUNDS, (x) => { const t = take(x, CRUNCHBASE_ROUND); return rec(t.record, t.rest); });
      settle(given, "cards");
    }
    return entryOf(given, record, people, rounds);
  }, () => []));
}

// ---------------------------------------------------------------------------------------------------------------
// the request text each provider makes from a run
// ---------------------------------------------------------------------------------------------------------------

/** What a request is made from: the run, and the request the run itself saved (the companies to ask for and the
 * discovery search). The saved request names no provider: it is the one session 135 wrote for PitchBook. */
export type RequestRun = {
  run_id: string; niche: string;
  request: { companies?: { name?: string; website?: string }[] | null; discover?: { keywords?: string[] | null; hq?: string } | null; paste_text?: string } | null;
};
const FENCE = "```";
const listed = (run: RequestRun) => arr(run.request?.companies).map((c, i) => `${i + 1}. ${str(c?.name)}${str(c?.website) ? ` (${str(c?.website)})` : ""}`).join("\n");
const keywords = (run: RequestRun) => arr(run.request?.discover?.keywords).map(str).filter(Boolean).map((k) => `'${k}'`).join(", ");
const hq = (run: RequestRun) => str(run.request?.discover?.hq) || "any";

function harmonicRequest(run: RequestRun): string {
  return `You have a Harmonic connector. Please pull the following from Harmonic for an ERW Thesis Builder run and answer with ONE JSON code block in the exact format below, and nothing else after it.

Run: ${run.run_id}
Niche: ${run.niche}

A. Company enrichment. For each company in this list, find it in Harmonic with the connector's search or lookup tools (by its website domain where one is given, otherwise by name), then use the connector's enrichment tools to get the company's record. Return, under Harmonic's own field names and as Harmonic returns them:
   - name, legal_name, short_description (or description), website
   - founding_date, headcount, stage, ownership_status, company_type
   - location (city, state, country), or headquarters
   - funding: funding_total, num_funding_rounds, investors, last_funding_at, last_funding_type, last_funding_total, funding_stage, valuation_info
   - funding_rounds, where your Harmonic plan includes deal data: announcement_date, funding_round_type, funding_amount, funding_currency, investors (investor_name, is_lead), valuation_info

${listed(run)}

B. People. For each company found, return the people Harmonic associates with it, founders and the chief executive first, at most 10 a company, each as Harmonic's person record: full_name, and from experience the entry at this company (title, company_name, is_current_position).

C. Search. Then search Harmonic for companies this list is missing: keywords ${keywords(run)}; headquarters: ${hq(run)}; private companies founded 2012 or later. Return up to 25 that are not in the list above, as "additional_companies", each with "why": the words of the search that matched, and its company record as in A.

D. Saved searches. If I name saved searches of mine below, use the connector's saved search tools to get their results and return up to 25 results of each under "saved_searches", saying whether the search is of companies, investors or people. If I name none, leave "saved_searches" out.
   My saved searches to use: (write their names here, or leave this line as it is)

Rules: report only what Harmonic returns. If Harmonic has no record of a company, return it with "found": false and nothing else. Copy field names and values as Harmonic gives them: do not rename, convert, round or compute a field. Leave out any field Harmonic does not return; do not estimate, and do not fill a field from memory or from the web. Use read-only tools only: create or change nothing in Harmonic (no list, no custom field).

Format:
${FENCE}json
{
  "format": "${PROVIDERS.harmonic.format}",
  "run_id": "${run.run_id}",
  "pulled_on": "YYYY-MM-DD",
  "companies": [
    {
      "name": "the name exactly as in the list above",
      "found": true,
      "company": {
        "name": "the name Harmonic uses",
        "legal_name": "the legal name",
        "short_description": "one line",
        "website": { "url": "https://www.example.com" },
        "founding_date": { "date": "2019-01-01", "granularity": "as Harmonic gives it" },
        "headcount": 25,
        "stage": "as Harmonic gives it",
        "ownership_status": "as Harmonic gives it",
        "location": { "city": "City", "state": "State", "country": "Country" },
        "funding": {
          "funding_total": 20100000,
          "num_funding_rounds": 2,
          "investors": ["Investor One", "Investor Two"],
          "last_funding_at": "2025-03-01",
          "last_funding_type": "as Harmonic gives it",
          "last_funding_total": 12500000
        }
      },
      "people": [
        { "full_name": "First Founder", "experience": [ { "title": "as Harmonic gives it", "company_name": "the name Harmonic uses", "is_current_position": true } ] }
      ]
    },
    { "name": "a company Harmonic does not hold", "found": false }
  ],
  "additional_companies": [
    { "name": "A company not in the list", "found": true, "why": "search: ...", "company": { "name": "A company not in the list", "headcount": 8 } }
  ],
  "saved_searches": [
    { "name": "the saved search's name in Harmonic", "of": "companies", "results": [ { "name": "a result's name", "record": { "name": "a result's name" } } ] }
  ]
}
${FENCE}`;
}

function crunchbaseRequest(run: RequestRun): string {
  return `You have a Crunchbase connector. Please pull the following from Crunchbase for an ERW Thesis Builder run and answer with ONE JSON code block in the exact format below, and nothing else after it.

Run: ${run.run_id}
Niche: ${run.niche}

A. Company profiles. For each company in this list, resolve it to its Crunchbase organization (the connector's entity resolution tool, by its website domain where one is given, otherwise by name), then retrieve its profile (the connector's entity lookup tool). Never guess an identifier. Return, under Crunchbase's own field ids and as Crunchbase returns them:
   - fields: identifier, legal_name, short_description, website_url, founded_on, num_employees_enum, status, operating_status, location_identifiers
   - fields: funding_total, num_funding_rounds, last_funding_at, last_funding_type, last_funding_total, funding_stage, valuation, valuation_date
   - fields: founder_identifiers, investor_identifiers, num_investors, num_lead_investors, and the profile's url
   - cards: founders (identifier, primary_job_title) and raised_funding_rounds (announced_on, investment_type, money_raised, post_money_valuation, lead_investor_identifiers, investor_identifiers)

${listed(run)}

B. Search. Then search Crunchbase organizations for companies this list is missing (the connector's search tools): keywords ${keywords(run)}; headquarters: ${hq(run)}; private companies founded 2012 or later. Return up to 25 that are not in the list above, as "additional_companies", each with "why": the words or the Crunchbase category that matched, and its organization fields as in A.

Rules: report only what Crunchbase returns. If Crunchbase has no record of a company, return it with "found": false and nothing else. Copy field ids and values as Crunchbase gives them: a money field stays the object Crunchbase returns (value, currency, value_usd), a date stays as returned; do not rename, convert, round or compute a field. Leave out any field Crunchbase does not return; do not estimate, and do not fill a field from memory or from the web. Use read-only tools only: create or change no Crunchbase list.

Format:
${FENCE}json
{
  "format": "${PROVIDERS.crunchbase.format}",
  "run_id": "${run.run_id}",
  "pulled_on": "YYYY-MM-DD",
  "companies": [
    {
      "name": "the name exactly as in the list above",
      "found": true,
      "organization": {
        "identifier": { "value": "the name Crunchbase uses", "permalink": "the-permalink", "entity_def_id": "organization" },
        "legal_name": "the legal name",
        "short_description": "one line",
        "website_url": "https://www.example.com",
        "founded_on": { "value": "2019-01-01", "precision": "year" },
        "num_employees_enum": "c_00011_00050",
        "status": "operating",
        "location_identifiers": [ { "value": "City" }, { "value": "State" }, { "value": "Country" } ],
        "funding_total": { "value": 20100000, "currency": "USD", "value_usd": 20100000 },
        "num_funding_rounds": 2,
        "last_funding_at": "2025-03-01",
        "last_funding_type": "series_a",
        "last_funding_total": { "value": 12500000, "currency": "USD", "value_usd": 12500000 },
        "funding_stage": "early_stage_venture",
        "founder_identifiers": [ { "value": "First Founder" } ],
        "investor_identifiers": [ { "value": "Investor One" }, { "value": "Investor Two" } ],
        "url": "the profile link Crunchbase returns"
      },
      "cards": {
        "founders": [ { "identifier": { "value": "First Founder" }, "primary_job_title": "as Crunchbase gives it" } ],
        "raised_funding_rounds": [ { "announced_on": "2025-03-01", "investment_type": "series_a", "money_raised": { "value": 12500000, "currency": "USD", "value_usd": 12500000 }, "lead_investor_identifiers": [ { "value": "Investor One" } ] } ]
      }
    },
    { "name": "a company Crunchbase does not hold", "found": false }
  ],
  "additional_companies": [
    { "name": "A company not in the list", "found": true, "why": "search: ...", "organization": { "identifier": { "value": "A company not in the list" }, "num_funding_rounds": 1 } }
  ]
}
${FENCE}`;
}

// ---------------------------------------------------------------------------------------------------------------
// the providers
// ---------------------------------------------------------------------------------------------------------------

export type Provider = {
  id: ProviderId; label: string; format: string;
  /** The line a figure's label shows on hover: whose copy the data is, and the provider's own sentence on redistribution. */
  terms: string;
  /** The note stored with an answer: where the figures came from. */
  received_note: string;
  /** The text to paste into a Claude chat that holds this provider's connector; "" when the run holds nothing to ask. */
  requestText: (run: RequestRun) => string;
  /** A pasted answer, parsed already, checked against the provider's format and written out again, labeled. */
  read: (input: unknown, runId: string, thisYear?: number) => Read;
};
export const PROVIDERS: Record<ProviderId, Provider> = {
  pitchbook: {
    id: "pitchbook", label: PB_LABEL, format: PB_FORMAT, terms: TERMS.pitchbook, received_note: PB_NOTE,
    // the text the run wrote and saved, as it is: an erw-pitchbook-1 request is never made again here
    requestText: (run) => str(run.request?.paste_text),
    read: (input, runId, thisYear) => validatePitchbook(input, runId, thisYear),
  },
  harmonic: {
    id: "harmonic", label: "Harmonic", format: "erw-harmonic-1", terms: TERMS.harmonic, received_note: NOTE("Harmonic"),
    requestText: (run) => (arr(run.request?.companies).length ? harmonicRequest(run) : ""),
    read: (input, runId) => validateHarmonic(input, runId),
  },
  crunchbase: {
    id: "crunchbase", label: "Crunchbase", format: "erw-crunchbase-1", terms: TERMS.crunchbase, received_note: NOTE("Crunchbase"),
    requestText: (run) => (arr(run.request?.companies).length ? crunchbaseRequest(run) : ""),
    read: (input, runId) => validateCrunchbase(input, runId),
  },
};
export const providerList = (): Provider[] => PROVIDER_IDS.map((id) => PROVIDERS[id]);
/**
 * Session 158, the owner's ruling of 8 October 2026: a provider whose answers are not kept, with the plain words said
 * of it. An answer of such a provider is refused before anything of the pasted text is read (checkPaste below, and
 * POST /api/thesis/provider before it), nothing of it is stored, and the choice on /thesis shows the provider as not
 * yet available with these words on hover. The provider's format, request text and reader stay as they are, so that
 * a ruling can open it again by removing its line here. The server's list says the same (warehouse/thesis/providers.py,
 * NOT_KEPT). PitchBook and Harmonic are as they were.
 */
export const NOT_KEPT: Partial<Record<ProviderId, string>> = { crunchbase: "Crunchbase answers are not kept until its terms are ruled on" };
/** The sentence shown for a provider whose answers are not kept, or null for one whose answers are. */
export const notKept = (id: ProviderId): string | null => (NOT_KEPT[id] ? `${NOT_KEPT[id]}.` : null);
/** The words of the short mark beside such a provider in the choice on /thesis. */
export const NOT_KEPT_MARK = "not yet available";
export const isProviderId = (v: unknown): v is ProviderId => typeof v === "string" && (PROVIDER_IDS as readonly string[]).includes(v);
/** The provider a format id belongs to, or null. */
export const providerOfFormat = (format: unknown): Provider | null => providerList().find((p) => p.format === format) ?? null;
/**
 * The provider of a stored record (a request, an answer). A record that names its provider is that provider's; one
 * that names only a format is that format's; one that names neither was written before session 150 and is
 * PitchBook's. This is how an old record is read: nothing stored is rewritten.
 */
export function providerOf(record: unknown): ProviderId {
  if (isObject(record)) {
    if (isProviderId(record.provider)) return record.provider;
    const p = providerOfFormat(record.format);
    if (p) return p.id;
  }
  return "pitchbook";
}

/** Is this the format of the provider chosen? null when it is; otherwise the plain words for the page: which format
 * the answer was given in, whose it is, and which the provider chosen takes. */
export function formatFault(chosen: ProviderId, given: unknown): string | null {
  const p = PROVIDERS[chosen];
  if (given === p.format) return null;
  const other = providerOfFormat(given);
  // session 158: an answer of a provider whose answers are not kept is not to be pasted under another provider either
  if (other && notKept(other.id)) return notKept(other.id);
  if (other) return `This answer is in the format "${other.format}", ${other.label}'s. The provider chosen is ${p.label}, which takes "${p.format}". Choose ${other.label} above, or paste ${p.label}'s answer.`;
  return `This answer names ${typeof given === "string" && given.trim() ? `the format "${given.trim().slice(0, 40)}"` : "no format"}. The provider chosen is ${p.label}, which takes "${p.format}".`;
}
export type Pasted = { ok: true; provider: ProviderId; payload: AnyPayload; key: string | null } | { ok: false; reason: string };
/**
 * A pasted answer read for the provider chosen: the JSON found in the text, its format checked against the provider
 * chosen before anything else, then the provider's own reader. A format of another provider is said plainly, with
 * both names. A "key" beside the fields (PitchBook's one-time key) is taken out and handed back, never stored.
 * Session 158: for a provider whose answers are not kept (NOT_KEPT) the answer is refused with the plain words, before
 * the pasted text is looked at.
 */
export function checkPaste(chosen: ProviderId, pasted: string, runId: string, thisYear?: number): Pasted {
  const p = PROVIDERS[chosen];
  const held = notKept(chosen);
  if (held) return { ok: false, reason: held };          // session 158: refused before the pasted text is read at all
  const got = extractJson(pasted);
  if (!got.ok) return { ok: false, reason: got.reason };
  const { key: inside, ...payload } = got.value as Obj;
  const fault = formatFault(chosen, payload.format);
  if (fault) return { ok: false, reason: fault };
  const r = p.read(payload, runId, thisYear);
  if (!r.ok) return r;
  return { ok: true, provider: chosen, payload: r.payload, key: typeof inside === "string" && inside.trim() ? inside.trim() : null };
}

// ---------------------------------------------------------------------------------------------------------------
// the run's facts: which provider supplied each figure
// ---------------------------------------------------------------------------------------------------------------

/** Where a figure came from: the provider, the format, when its answer was pasted and the hash of the pasted text
 * (null where a record written before session 150 does not hold it). */
export type Stamp = { provider: ProviderId; format: string; pasted_at: string | null; sha256: string | null };
/** A provider's answer as a run holds it. */
export type Held = Stamp & { payload: AnyPayload };
/** A row of the store of provider results (migration 025); `payload` is null for PitchBook, whose answer is on the run's row. */
export type ProviderRow = { provider?: string | null; format?: string | null; pasted_at?: string | null; pasted_sha256?: string | null; payload?: unknown };

export const FACTS = [
  ["listed_as", "Listed as"], ["legal_name", "Legal name"], ["total_raised", "Total raised"], ["last_round", "Last round"], ["last_round_leads", "Lead investors of the last round"],
  ["post_valuation", "Post-money valuation"], ["valuation", "Valuation, announced or estimated"], ["financing_status", "Financing status"], ["ownership_status", "Ownership status"],
  ["funding_stage", "Funding stage"], ["status", "Status"], ["hq", "Headquarters"], ["founded_year", "Founded"], ["employees", "Employees"], ["founders", "Founders"], ["people", "People"],
  ["lead_investors", "Lead investors"], ["investors", "Investors"], ["top_investors", "Top five investors"], ["description", "Description"], ["website", "Website"], ["rounds", "Funding rounds"], ["profile", "Profile"],
] as const;
export type FactId = (typeof FACTS)[number][0];
const FACT_LABEL = Object.fromEntries(FACTS) as Record<FactId, string>;
const FACT_AT = Object.fromEntries(FACTS.map(([id], i) => [id, i])) as Record<FactId, number>;

/** What two providers' values of one fact are compared by. A fact with no `cmp` is shown beside the others and never
 * marked: prose and lists that the providers define differently. */
export type Cmp = { k: "money"; v: number } | { k: "year"; v: number } | { k: "count"; v: number } | { k: "range"; lo: number; hi: number | null }
  | { k: "text"; v: string } | { k: "names"; v: string[] } | { k: "round"; date: string; amount: number | null };
export type Fact = Stamp & {
  fact: FactId; label: string; value: string;
  /** The provider's own field or fields the value was read from. */
  field: string;
  /** A short remark for the hover, where the documentation leaves something open. */
  note?: string;
  cmp?: Cmp;
};

const flat = (s: string) => s.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, " ").trim();
const names = (list: string[]) => [...new Set(list.map(flat).filter(Boolean))].sort();
/** Do two values of one fact differ? null when they are not of a kind that can be compared. */
export function differs(a: Cmp | undefined, b: Cmp | undefined): boolean | null {
  if (!a || !b) return null;
  if (a.k === "count" && b.k === "range") return a.v < b.lo || (b.hi !== null && a.v > b.hi);
  if (a.k === "range" && b.k === "count") return differs(b, a);
  if (a.k !== b.k) return null;
  switch (a.k) {
    case "money": return Math.round(a.v) !== Math.round((b as typeof a).v);
    case "year": case "count": return a.v !== (b as typeof a).v;
    case "range": return a.lo !== (b as typeof a).lo || a.hi !== (b as typeof a).hi;
    case "text": return flat(a.v) !== flat((b as typeof a).v);
    case "names": return a.v.join("|") !== (b as typeof a).v.join("|");
    case "round": {
      const o = b as typeof a, n = Math.min(a.date.length, o.date.length);
      if (n >= 4 && a.date.slice(0, n) !== o.date.slice(0, n)) return true;
      if (a.amount !== null && o.amount !== null) return Math.round(a.amount) !== Math.round(o.amount);
      return n >= 4 ? false : null;
    }
  }
}

const usd = (v: number) => (v >= 1_000_000 ? `USD ${num(v / 1_000_000)} million` : `USD ${num(v)}`);
const T = (v: Json | undefined): string => (typeof v === "string" ? v : "");
const N = (v: Json | undefined): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);
const day10 = (v: Json | undefined) => T(v).slice(0, 10);
const yearOf = (v: string) => (/^\d{4}/.test(v) ? Number(v.slice(0, 4)) : null);
type Raw = Omit<Fact, keyof Stamp | "label">;
const put = (out: Raw[], fact: FactId, field: string, value: string | null | undefined, cmp?: Cmp, note?: string) => {
  if (!value) return;
  const f: Raw = { fact, value, field };
  if (cmp) f.cmp = cmp;
  if (note) f.note = note;
  out.push(f);
};
const latest = (rounds: PvRound[] | undefined, dateField: string): PvRound | null =>
  arr(rounds).filter((r) => T(r.record[dateField])).sort((a, b) => (T(a.record[dateField]) < T(b.record[dateField]) ? 1 : -1))[0] ?? null;

function pitchbookFacts(c: PbCompany): Raw[] {
  const ID: Record<string, FactId> = { pitchbook_name: "listed_as", total_raised: "total_raised", last_round: "last_round", post_valuation: "post_valuation", financing_status: "financing_status",
    hq: "hq", founded_year: "founded_year", employees: "employees", founders: "founders", lead_investors: "lead_investors", investors: "investors", description: "description" };
  const n = (v: unknown) => (typeof v === "number" && Number.isFinite(v) ? v : null);
  const cmp: Partial<Record<string, Cmp>> = {};
  if (n(c.total_raised_usd_m) !== null) cmp.total_raised = { k: "money", v: c.total_raised_usd_m! * 1e6 };
  if (c.last_round?.date || n(c.last_round?.size_usd_m) !== null) cmp.last_round = { k: "round", date: str(c.last_round?.date), amount: n(c.last_round?.size_usd_m) === null ? null : c.last_round!.size_usd_m! * 1e6 };
  if (n(c.last_round?.post_valuation_usd_m) !== null) cmp.post_valuation = { k: "money", v: c.last_round!.post_valuation_usd_m! * 1e6 };
  if (c.hq) cmp.hq = { k: "text", v: c.hq };
  if (n(c.founded_year) !== null) cmp.founded_year = { k: "year", v: c.founded_year! };
  if (n(c.employees) !== null) cmp.employees = { k: "count", v: c.employees! };
  if (arr(c.founders).length) cmp.founders = { k: "names", v: names(arr(c.founders)) };
  if (arr(c.investors).length) cmp.investors = { k: "names", v: names(arr(c.investors)) };
  // the figures and their words are the ones the page has shown since session 135 (view.pbFigures), unchanged
  return pbFigures(c).map((f) => (cmp[f.id] ? { fact: ID[f.id], value: f.value, field: f.id, cmp: cmp[f.id] } : { fact: ID[f.id], value: f.value, field: f.id }));
}

const NO_CURRENCY = "Harmonic's documentation does not state the currency of this field; the number is shown as given.";
function harmonicFacts(c: PvCompany): Raw[] {
  const r = c.record, out: Raw[] = [];
  if (T(r.name) && nameKey(r.name) !== nameKey(c.name)) put(out, "listed_as", "name", T(r.name));
  put(out, "legal_name", "legal_name", T(r.legal_name));
  const total = N(r["funding.funding_total"]);
  if (total !== null) put(out, "total_raised", "funding.funding_total", num(total), { k: "money", v: total }, NO_CURRENCY);
  const at = day10(r["funding.last_funding_at"]), size = N(r["funding.last_funding_total"]);
  const kind = T(r["funding.last_funding_type"]) || T(r["funding.funding_stage"]);
  put(out, "last_round", "funding.last_funding_type, funding.last_funding_at, funding.last_funding_total", [kind, at ? whenWords(at) : "", size === null ? "" : num(size)].filter(Boolean).join(", "),
    at || size !== null ? { k: "round", date: at, amount: size } : undefined, size === null ? undefined : NO_CURRENCY);
  const last = latest(c.rounds, "announcement_date");
  const leads = arr(last?.investors).filter((i) => i.record.is_lead === true).map((i) => T(i.record.investor_name)).filter(Boolean);
  put(out, "last_round_leads", "funding_rounds.investors (is_lead, investor_name)", leads.join(", "), leads.length ? { k: "names", v: names(leads) } : undefined);
  const post = N(last?.record["valuation_info.amount"]);
  if (post !== null) put(out, "post_valuation", "funding_rounds.valuation_info.amount", usd(post), { k: "money", v: post });
  const val = N(r["funding.valuation_info.amount"]);
  if (val !== null) put(out, "valuation", "funding.valuation_info.amount", usd(val), undefined, T(r["funding.valuation_info.source"]) ? `Source, as Harmonic gives it: ${T(r["funding.valuation_info.source"])}.` : undefined);
  put(out, "ownership_status", "ownership_status", T(r.ownership_status));
  put(out, "funding_stage", "stage", T(r.stage));
  const place = [T(r["location.city"]), T(r["location.state"]), T(r["location.country"])].filter(Boolean).join(", ") || T(r["location.location"]) || T(r.headquarters);
  put(out, "hq", "location.city, location.state, location.country (else location.location, else headquarters)", place, place ? { k: "text", v: place } : undefined);
  const founded = yearOf(T(r["founding_date.date"]));
  if (founded !== null) put(out, "founded_year", "founding_date.date", String(founded), { k: "year", v: founded });
  const heads = N(r.headcount);
  if (heads !== null) put(out, "employees", "headcount", num(heads), { k: "count", v: heads });
  const own = new Set([nameKey(c.name), nameKey(r.name)].filter(Boolean));
  const people = arr(c.people).map((p) => {
    const here = arr(p.experience).filter((e) => own.has(nameKey(e.record.company_name)));
    const role = here.find((e) => e.record.is_current_position === true) ?? here[0];
    return { name: T(p.record.full_name), title: T(role?.record.title) };
  }).filter((p) => p.name);
  const founders = people.filter((p) => /founder/i.test(p.title)).map((p) => p.name);
  put(out, "founders", "people: full_name, where experience.title at this company holds the word founder", founders.join(", "), founders.length ? { k: "names", v: names(founders) } : undefined);
  put(out, "people", "people: full_name, experience.title", people.slice(0, 10).map((p) => (p.title ? `${p.name} (${p.title})` : p.name)).join(", "));
  const inv = Array.isArray(r["funding.investors"]) ? (r["funding.investors"] as Json[]).map(T).filter(Boolean) : [];
  put(out, "investors", "funding.investors", inv.join(", "), inv.length ? { k: "names", v: names(inv) } : undefined);
  put(out, "description", T(r.short_description) ? "short_description" : "description", (T(r.short_description) || T(r.description)).slice(0, CAP_TEXT));
  put(out, "website", "website.url", T(r["website.url"]));
  const rounds = N(r["funding.num_funding_rounds"]);
  if (rounds !== null) put(out, "rounds", "funding.num_funding_rounds", num(rounds));
  return out;
}

type Money = { value: number; currency: string; value_usd?: number };
const money = (v: Json | undefined): Money | null => (isObject(v) && typeof v.value === "number" && typeof v.currency === "string" ? (v as unknown as Money) : null);
const moneyUsd = (m: Money | null): number | null => (!m ? null : typeof m.value_usd === "number" ? m.value_usd : m.currency === "USD" ? m.value : null);
const moneyWords = (m: Money | null): string => (!m ? "" : moneyUsd(m) !== null ? usd(moneyUsd(m)!) : `${num(m.value)} ${m.currency}`);
const identName = (v: Json | undefined): string => (isObject(v) ? T(v.value as Json) : "");
const identNames = (v: Json | undefined): string[] => (Array.isArray(v) ? v.map(identName).filter(Boolean) : []);
/** "c_00011_00050" is 11 to 50 and "c_10001_max" is 10,001 or more, as the schema of num_employees_enum lists them. */
function headRange(code: string): { lo: number; hi: number | null } | null {
  const m = /^c_(\d+)_(\d+|max)$/.exec(code);
  return m ? { lo: Number(m[1]), hi: m[2] === "max" ? null : Number(m[2]) } : null;
}
function crunchbaseFacts(c: PvCompany): Raw[] {
  const r = c.record, out: Raw[] = [];
  const shown = identName(r.identifier) || T(r.name);
  if (shown && nameKey(shown) !== nameKey(c.name)) put(out, "listed_as", "identifier.value", shown);
  put(out, "legal_name", "legal_name", T(r.legal_name));
  const total = money(r.funding_total);
  put(out, "total_raised", "funding_total", moneyWords(total), moneyUsd(total) === null ? undefined : { k: "money", v: moneyUsd(total)! });
  const at = day10(r.last_funding_at), size = money(r.last_funding_total);
  put(out, "last_round", "last_funding_type, last_funding_at, last_funding_total", [T(r.last_funding_type), at ? whenWords(at) : "", moneyWords(size)].filter(Boolean).join(", "),
    at || moneyUsd(size) !== null ? { k: "round", date: at, amount: moneyUsd(size) } : undefined);
  const last = latest(c.rounds, "announced_on");
  const leads = identNames(last?.record.lead_investor_identifiers);
  put(out, "last_round_leads", "raised_funding_rounds.lead_investor_identifiers", leads.join(", "), leads.length ? { k: "names", v: names(leads) } : undefined);
  const val = money(r.valuation);
  put(out, "post_valuation", "valuation", moneyWords(val), moneyUsd(val) === null ? undefined : { k: "money", v: moneyUsd(val)! }, T(r.valuation_date) ? `As of ${whenWords(day10(r.valuation_date))}, as Crunchbase gives it.` : undefined);
  put(out, "funding_stage", "funding_stage", T(r.funding_stage));
  put(out, "status", T(r.status) ? "status" : "operating_status", T(r.status) || T(r.operating_status));
  const place = identNames(r.location_identifiers).join(", ");
  put(out, "hq", "location_identifiers", place, place ? { k: "text", v: place } : undefined);
  const f = isObject(r.founded_on) ? r.founded_on : null;
  const founded = f && f.precision !== "none" ? yearOf(T(f.value as Json)) : null;
  if (founded !== null) put(out, "founded_year", "founded_on", String(founded), { k: "year", v: founded });
  const range = headRange(T(r.num_employees_enum));
  if (range) put(out, "employees", "num_employees_enum", range.hi === null ? `${num(range.lo)} or more` : `${num(range.lo)} to ${num(range.hi)}`, { k: "range", ...range });
  const card = arr(c.people).map((p) => ({ name: identName(p.record.identifier) || T(p.record.name), title: T(p.record.primary_job_title) })).filter((p) => p.name);
  const founders = identNames(r.founder_identifiers).length ? identNames(r.founder_identifiers) : card.map((p) => p.name);
  put(out, "founders", identNames(r.founder_identifiers).length ? "founder_identifiers" : "cards.founders", founders.join(", "), founders.length ? { k: "names", v: names(founders) } : undefined);
  put(out, "people", "cards.founders: identifier, primary_job_title", card.slice(0, 10).map((p) => (p.title ? `${p.name} (${p.title})` : p.name)).join(", "));
  put(out, "top_investors", "investor_identifiers", identNames(r.investor_identifiers).join(", "), undefined, "The top five investors by Crunchbase Rank, as Crunchbase defines this field.");
  put(out, "description", T(r.short_description) ? "short_description" : "description", (T(r.short_description) || T(r.description)).slice(0, CAP_TEXT));
  put(out, "website", T(r.website_url) ? "website_url" : "website", T(r.website_url) || (isObject(r.website) ? T(r.website.value as Json) : ""));
  const rounds = N(r.num_funding_rounds);
  if (rounds !== null) put(out, "rounds", "num_funding_rounds", num(rounds));
  put(out, "profile", "url", T(r.url));
  return out;
}

const isLegacy = (p: AnyPayload): p is PitchbookPayload => providerOf(p) === "pitchbook";
const stampOf = (h: Held): Stamp => ({ provider: h.provider, format: h.format, pasted_at: h.pasted_at, sha256: h.sha256 });
const stamped = (h: Held, raw: Raw[]): Fact[] => raw.map((f) => ({ ...f, label: FACT_LABEL[f.fact], ...stampOf(h) }));
/** The facts one company of one provider's answer holds, each stamped. A company PitchBook lists under another name
 * shows that name with PitchBook's own words ("Listed as"), as it has since session 135. */
export function factsOfCompany(h: Held, c: PbCompany | PvCompany | null | undefined): Fact[] {
  if (!c || !c.found) return [];
  if (isLegacy(h.payload)) return stamped(h, pitchbookFacts(c as PbCompany));
  return stamped(h, h.provider === "harmonic" ? harmonicFacts(c as PvCompany) : crunchbaseFacts(c as PvCompany));
}
/** The company of an answer that was asked for under this name (an answer's "name" is the name asked). */
export function companyIn(h: Held, name: unknown): PbCompany | PvCompany | null {
  const k = nameKey(name);
  if (!k) return null;
  // session 155: the two providers' company lists are one list here; cast before arr(), whose one type argument cannot be a union of two arrays (the build's type check failed on it, and Vercel's deployment of 41c3115 with it)
  return arr(h.payload.companies as (PbCompany | PvCompany)[] | null | undefined).find((c) => nameKey(c?.name) === k) ?? null;
}
/** Every fact every provider holds for one company, in the order of FACTS and then of the providers. */
export function factsFor(held: Held[], name: unknown): Fact[] {
  const at = (p: ProviderId) => PROVIDER_IDS.indexOf(p);
  return held.flatMap((h) => factsOfCompany(h, companyIn(h, name))).sort((a, b) => FACT_AT[a.fact] - FACT_AT[b.fact] || at(a.provider) - at(b.provider));
}
/** The facts two or more providers give differently. Both values stay in `facts`: this only names the facts to mark. */
export function disagreements(facts: Fact[]): Set<FactId> {
  const out = new Set<FactId>();
  for (let i = 0; i < facts.length; i += 1) {
    for (let j = i + 1; j < facts.length; j += 1) {
      const a = facts[i], b = facts[j];
      if (a.fact === b.fact && a.provider !== b.provider && differs(a.cmp, b.cmp) === true) out.add(a.fact);
    }
  }
  return out;
}

const sha = (v: unknown) => (typeof v === "string" && /^[0-9a-f]{64}$/.test(v) ? v : null);
/**
 * The answers a run holds, PitchBook's first. PitchBook's answer is on the run's own row, as session 135 stored it:
 * it names no provider and is read as PitchBook's; its time is the row's, and the hash of its pasted text is the one
 * the store of provider results holds for it, or null (an answer stored before session 150, or sent straight to the
 * route by a chat). The others come from the store of provider results.
 */
export function heldOf(run: { pitchbook?: PitchbookPayload | null; pitchbook_received_at?: string | null; providers?: ProviderRow[] | null }): Held[] {
  const rows = arr(run.providers).filter(isObject) as ProviderRow[];
  const out: Held[] = [];
  if (run.pitchbook && typeof run.pitchbook === "object") {
    const row = rows.find((r) => providerOf(r) === "pitchbook");
    out.push({ provider: "pitchbook", format: PB_FORMAT, pasted_at: str(row?.pasted_at) || run.pitchbook_received_at || null, sha256: sha(row?.pasted_sha256), payload: run.pitchbook });
  }
  for (const id of PROVIDER_IDS) {
    if (id === "pitchbook") continue;
    const row = rows.find((r) => r.provider === id && isObject(r.payload) && Array.isArray((r.payload as Obj).companies));
    if (row) out.push({ provider: id, format: PROVIDERS[id].format, pasted_at: str(row.pasted_at) || null, sha256: sha(row.pasted_sha256), payload: row.payload as ProviderPayload });
  }
  return out;
}

/** Do two JSON values hold the same, whatever the order of their keys? (A database hands an object's keys back in an
 * order of its own.) */
export function sameJson(a: unknown, b: unknown): boolean {
  const canon = (v: unknown): unknown => (Array.isArray(v) ? v.map(canon) : isObject(v) ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canon(v[k])])) : v);
  return JSON.stringify(canon(a)) === JSON.stringify(canon(b));
}

/** The names of the fields an answer kept under "not_mapped", as dotted paths (a list is one field). */
export function notMapped(v: unknown, prefix = ""): string[] {
  if (!isObject(v)) return prefix ? [prefix] : [];
  const keys = Object.keys(v);
  if (!keys.length) return prefix ? [prefix] : [];
  return keys.flatMap((k) => notMapped(v[k], prefix ? `${prefix}.${k}` : k));
}
/** Every field one company of an answer kept as given and did not use, across its record, its people and its rounds. */
export function notMappedOf(c: PvCompany | null | undefined): string[] {
  if (!c) return [];
  const inner = (list: Rec[] | undefined, at: string) => arr(list).flatMap((x) => notMapped(x.not_mapped).map((p) => `${at}.${p}`));
  const all = [...notMapped(c.not_mapped), ...inner(c.people, "people"), ...arr(c.people).flatMap((p) => inner(p.experience, "people.experience")),
    ...inner(c.rounds, "rounds"), ...arr(c.rounds).flatMap((r) => inner(r.investors, "rounds.investors"))];
  return [...new Set(all)].sort();
}
/** One line for the hover of a provider's label: where the figures came from, whose copy they are, and their stamp. */
export function hoverOf(s: Stamp): string {
  const p = PROVIDERS[s.provider];
  const when = s.pasted_at ? ` Pasted ${whenWords(s.pasted_at)}.` : "";
  const hash = s.sha256 ? ` Hash of the pasted text: ${s.sha256.slice(0, 12)}.` : " Hash of the pasted text: not held.";
  return `${p.received_note} ${p.terms} Format ${s.format}.${when}${hash}`;
}
