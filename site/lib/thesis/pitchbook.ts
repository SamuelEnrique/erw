// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the PitchBook stage's answer.
//
// The owner pastes a run's request into a Claude chat that holds a PitchBook connector and pastes the answer back on
// /thesis; POST /api/thesis/pitchbook stores it under the run's one-time key. This file is the gate between the two:
// pure functions, no I/O, no imports, so a script can test them as they are (scripts/test-thesis-pitchbook.mjs).
//
//   readSubmission(body)             what a POST holds: { run_id, key, payload }, or the payload itself carrying "key"
//   validatePitchbook(payload, id)   the payload checked strictly against the format and written out again, labeled
//   extractJson(text)                the JSON object inside a pasted answer (bare, in a code fence, or with words around)
//
// The format, erw-pitchbook-1:
//   { "format": "erw-pitchbook-1", "run_id": string, "pulled_on": "YYYY-MM-DD",
//     "companies": [ Company ], "additional_companies": [ Company & { "why": string } ] }
//   Company = { "name": string, "found": boolean, "pitchbook_name"?, "hq"?, "founded_year"?, "description"?, "employees"?,
//     "financing_status"?, "last_round"?: { "date"?, "type"?, "size_usd_m"?, "post_valuation_usd_m"? },
//     "total_raised_usd_m"?, "investors"?, "lead_investors"?, "founders"? }
// Rules: an unknown key is refused at every level; null in an optional field is dropped; a string is trimmed and cut at
// its cap (a name over its cap is refused: it is what a company is matched by); a number must be finite and not below
// zero; a list over its cap is refused; a company with found false keeps only its name and found. What comes out
// carries the label "PitchBook" and the note of where the figures came from: no figure is stored without them.

export const FORMAT = "erw-pitchbook-1";
export const LABEL = "PitchBook";
export const RECEIVED_NOTE = "Figures as returned from PitchBook through the user's own account; not checked by the ERW.";
/** The largest request body the route reads, in bytes (400 KB). */
export const MAX_BODY = 400_000;
export const MAX_COMPANIES = 300;
export const MAX_ADDITIONAL = 100;
export const MAX_NAME = 120;
export const MAX_LIST = 40;
const MAX_TEXT = 400;
const MAX_SHORT = 200;

export type PbRound = { date?: string; type?: string; size_usd_m?: number; post_valuation_usd_m?: number };
export type PbCompany = {
  name: string; found: boolean; pitchbook_name?: string; hq?: string; founded_year?: number; description?: string; employees?: number;
  financing_status?: string; last_round?: PbRound; total_raised_usd_m?: number; investors?: string[]; lead_investors?: string[]; founders?: string[];
};
/** A company PitchBook found beyond the ones asked for, with why it belongs. `why` is absent only when found is false. */
export type PbAdditional = PbCompany & { why?: string };
export type PitchbookPayload = {
  format: typeof FORMAT; run_id: string; pulled_on: string; label: typeof LABEL; received_note: string;
  companies: PbCompany[]; additional_companies: PbAdditional[];
};
export type Checked = { ok: true; payload: PitchbookPayload } | { ok: false; reason: string };
export type Submission = { ok: true; run_id: string; key: string; payload: unknown } | { ok: false; reason: string };

class Refused extends Error {}
const refuse = (reason: string): never => { throw new Refused(reason); };
const isObject = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);
const absent = (v: unknown) => v === undefined || v === null;

function onlyKeys(o: Record<string, unknown>, allowed: readonly string[], where: string) {
  for (const k of Object.keys(o)) if (!allowed.includes(k)) refuse(`${where} holds a key the format does not have: "${k.slice(0, 40)}".`);
}
/** A string, trimmed and cut at its cap; an optional one that is null, absent or blank is dropped. */
function text(v: unknown, where: string, cap: number): string | undefined {
  if (absent(v)) return undefined;
  if (typeof v !== "string") refuse(`${where} must be text.`);
  const s = (v as string).replace(/\s+/g, " ").trim();
  return s ? s.slice(0, cap) : undefined;
}
function amount(v: unknown, where: string, whole = false, lo = 0, hi = Number.POSITIVE_INFINITY): number | undefined {
  if (absent(v)) return undefined;
  if (typeof v !== "number" || !Number.isFinite(v)) refuse(`${where} must be a finite number.`);
  const n = v as number;
  if (whole && !Number.isInteger(n)) refuse(`${where} must be a whole number.`);
  if (n < lo) refuse(lo === 0 ? `${where} must not be below zero.` : `${where} must be ${lo} or later.`);
  if (n > hi) refuse(`${where} must be ${hi} or earlier.`);
  return n;
}
function list(v: unknown, where: string): string[] | undefined {
  if (absent(v)) return undefined;
  if (!Array.isArray(v)) refuse(`${where} must be a list.`);
  const a = v as unknown[];
  if (a.length > MAX_LIST) refuse(`${where} holds ${a.length} names; at most ${MAX_LIST}.`);
  const out = a.map((x, i) => (typeof x === "string" ? text(x, `${where}[${i}]`, MAX_NAME) : refuse(`${where}[${i}] must be text.`))).filter((x): x is string => !!x);
  return out.length ? out : undefined;
}
/** A calendar day "YYYY-MM-DD"; with `partial`, also "YYYY-MM" and "YYYY". */
function day(v: unknown, where: string, partial: boolean): string | undefined {
  if (absent(v)) return undefined;
  const want = partial ? '"YYYY-MM-DD", "YYYY-MM" or "YYYY"' : '"YYYY-MM-DD"';
  if (typeof v !== "string") refuse(`${where} must be a date written ${want}.`);
  const s = (v as string).trim();
  const m = /^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$/.exec(s);
  if (!m || (!partial && !m[3])) refuse(`${where} must be a date written ${want}.`);
  const [y, mo, d] = [Number(m![1]), m![2] ? Number(m![2]) : 1, m![3] ? Number(m![3]) : 1];
  const t = new Date(Date.UTC(y, mo - 1, d));
  if (y < 1900 || t.getUTCFullYear() !== y || t.getUTCMonth() !== mo - 1 || t.getUTCDate() !== d) refuse(`${where} is not a day of the calendar.`);
  return s;
}

const COMPANY_KEYS = ["name", "found", "pitchbook_name", "hq", "founded_year", "description", "employees", "financing_status", "last_round", "total_raised_usd_m", "investors", "lead_investors", "founders"] as const;
const ROUND_KEYS = ["date", "type", "size_usd_m", "post_valuation_usd_m"] as const;

function company(v: unknown, where: string, thisYear: number, additional: boolean): PbCompany | PbAdditional {
  if (!isObject(v)) refuse(`${where} must be an object.`);
  const o = v as Record<string, unknown>;
  onlyKeys(o, additional ? [...COMPANY_KEYS, "why"] : COMPANY_KEYS, where);
  if (typeof o.name !== "string") refuse(`${where}.name is required and must be text.`);
  const name = (o.name as string).replace(/\s+/g, " ").trim();
  if (!name) refuse(`${where}.name is empty.`);
  if (name.length > MAX_NAME) refuse(`${where}.name is longer than ${MAX_NAME} characters.`);
  if (typeof o.found !== "boolean") refuse(`${where}.found is required and must be true or false.`);
  const found = o.found as boolean;
  // every field is checked, also on a company that was not found, so a wrong answer is refused and not quietly cut
  const c: PbCompany = { name, found };
  const put = <K extends keyof PbCompany>(k: K, val: PbCompany[K] | undefined) => { if (val !== undefined) c[k] = val; };
  put("pitchbook_name", text(o.pitchbook_name, `${where}.pitchbook_name`, MAX_SHORT));
  put("hq", text(o.hq, `${where}.hq`, MAX_SHORT));
  put("founded_year", amount(o.founded_year, `${where}.founded_year`, true, 1900, thisYear));
  put("description", text(o.description, `${where}.description`, MAX_TEXT));
  put("employees", amount(o.employees, `${where}.employees`, true));
  put("financing_status", text(o.financing_status, `${where}.financing_status`, MAX_NAME));
  if (!absent(o.last_round)) {
    if (!isObject(o.last_round)) refuse(`${where}.last_round must be an object.`);
    const r = o.last_round as Record<string, unknown>;
    onlyKeys(r, ROUND_KEYS, `${where}.last_round`);
    const round: PbRound = {};
    const date = day(r.date, `${where}.last_round.date`, true);
    const type = text(r.type, `${where}.last_round.type`, MAX_NAME);
    const size = amount(r.size_usd_m, `${where}.last_round.size_usd_m`);
    const post = amount(r.post_valuation_usd_m, `${where}.last_round.post_valuation_usd_m`);
    if (date !== undefined) round.date = date;
    if (type !== undefined) round.type = type;
    if (size !== undefined) round.size_usd_m = size;
    if (post !== undefined) round.post_valuation_usd_m = post;
    if (Object.keys(round).length) c.last_round = round;
  }
  put("total_raised_usd_m", amount(o.total_raised_usd_m, `${where}.total_raised_usd_m`));
  put("investors", list(o.investors, `${where}.investors`));
  put("lead_investors", list(o.lead_investors, `${where}.lead_investors`));
  put("founders", list(o.founders, `${where}.founders`));
  const kept: PbCompany = found ? c : { name, found };
  if (!additional) return kept;
  const why = typeof o.why === "string" ? text(o.why, `${where}.why`, MAX_TEXT) : undefined;
  if (!why) refuse(`${where}.why is required and must be text.`);
  return found ? { ...kept, why: why as string } : kept;
}

/**
 * A PitchBook answer checked against erw-pitchbook-1 and written out again with its label. `runId` is the run the
 * request names; the payload must name the same one. `thisYear` is the latest founding year accepted.
 */
export function validatePitchbook(input: unknown, runId: string, thisYear: number = new Date().getUTCFullYear()): Checked {
  try {
    if (!isObject(input)) refuse("The answer must be one JSON object.");
    const o = input as Record<string, unknown>;
    onlyKeys(o, ["format", "run_id", "pulled_on", "companies", "additional_companies"], "The answer");
    if (o.format !== FORMAT) refuse(`"format" must be "${FORMAT}".`);
    if (typeof o.run_id !== "string" || o.run_id !== runId) refuse('"run_id" is not the run this answer is submitted for.');
    const pulled = day(o.pulled_on, '"pulled_on"', false);
    if (!pulled) refuse('"pulled_on" is required: the day the figures were pulled, written "YYYY-MM-DD".');
    if (!Array.isArray(o.companies)) refuse('"companies" is required and must be a list.');
    const cs = o.companies as unknown[];
    if (cs.length > MAX_COMPANIES) refuse(`"companies" holds ${cs.length}; at most ${MAX_COMPANIES}.`);
    if (!absent(o.additional_companies) && !Array.isArray(o.additional_companies)) refuse('"additional_companies" must be a list.');
    const as = (o.additional_companies ?? []) as unknown[];
    if (as.length > MAX_ADDITIONAL) refuse(`"additional_companies" holds ${as.length}; at most ${MAX_ADDITIONAL}.`);
    return {
      ok: true,
      payload: {
        format: FORMAT, run_id: runId, pulled_on: pulled as string, label: LABEL, received_note: RECEIVED_NOTE,
        companies: cs.map((c, i) => company(c, `companies[${i}]`, thisYear, false)),
        additional_companies: as.map((c, i) => company(c, `additional_companies[${i}]`, thisYear, true)),
      },
    };
  } catch (e) {
    if (e instanceof Refused) return { ok: false, reason: e.message };
    throw e;
  }
}

/**
 * What a POST to /api/thesis/pitchbook holds. Two forms are read: { run_id, key, payload }, and the payload itself with
 * a "key" beside its fields (an answer pasted whole). The key is taken out of the payload before it is checked.
 */
export function readSubmission(body: unknown): Submission {
  if (!isObject(body)) return { ok: false, reason: "Send one JSON object: { run_id, key, payload }." };
  let payload: unknown, key: unknown, run: unknown;
  if ("payload" in body) {
    const extra = Object.keys(body).find((k) => !["run_id", "key", "payload"].includes(k));
    if (extra) return { ok: false, reason: `The request holds a key it does not have: "${extra.slice(0, 40)}".` };
    payload = body.payload;
    key = body.key;
    run = body.run_id;
    if (isObject(payload)) {
      const { key: inside, ...rest } = payload;
      if (inside !== undefined) payload = rest;
      if (absent(key)) key = inside;
      if (absent(run)) run = rest.run_id;
    }
  } else {
    const { key: inside, ...rest } = body;
    payload = rest;
    key = inside;
    run = rest.run_id;
  }
  if (!isObject(payload)) return { ok: false, reason: "The answer must be one JSON object." };
  if (typeof run !== "string" || !/^[A-Za-z0-9_-]{1,80}$/.test(run)) return { ok: false, reason: "The run this answer is for is not named." };
  if (typeof key !== "string" || !key.trim() || key.length > 200) return { ok: false, reason: "The key is missing." };
  return { ok: true, run_id: run, key: key.trim(), payload };
}

/** The JSON object in a pasted answer: the text itself, the inside of a code fence, or from its first brace to its last. */
export function extractJson(pasted: string): { ok: true; value: unknown } | { ok: false; reason: string } {
  const s = pasted.trim();
  if (!s) return { ok: false, reason: "Nothing was pasted." };
  const fence = /```(?:json)?\s*([\s\S]*?)```/i.exec(s);
  const a = s.indexOf("{"), b = s.lastIndexOf("}");
  for (const t of [s, fence ? fence[1].trim() : "", a >= 0 && b > a ? s.slice(a, b + 1) : ""]) {
    if (!t) continue;
    try {
      const v: unknown = JSON.parse(t);
      if (isObject(v)) return { ok: true, value: v };
    } catch { /* not this reading of the text */ }
  }
  return { ok: false, reason: "No JSON object could be read in the pasted text." };
}
