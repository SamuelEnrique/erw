// Energy Research Warehouse (ERW) site, session 157: what "What changed this week" reads (/policy?view=week, in review).
//
//   the live set    policy_actions of the last thirty days and policy_reads, through lib/supabase.ts (the anon key), as
//                   the page's first view reads them, with the fields the tag rule needs (the abstract and, once the
//                   table's next load holds them, the first paragraph and the recheck);
//   five site files data/policy/: tag_rules.json (the one tag rule), action_tags.json (the tags the warehouse's run gave,
//                   with the printed text they rest on), grids.json (which grid sees an action), state_rules.json (the
//                   proceedings and orders of FERC and the state commissions) and refresh.json (each regulator's list,
//                   whether it is refreshed, and why not). The warehouse writes them whole
//                   (warehouse/derived/policy_monitor_site.py); this file only reads them, when a request asks, so a
//                   file that is not there yet is a short placeholder on the page and never a failed build.
// No model is called and nothing is written. What the page does with the rows is lib/policyweek.ts.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import { HOURLY, attempt, rest } from "./supabase";
import {
  actionRow, bodiesOf, chipsOf, dayOf, docketRow, droppedTip, gridsOfAction, inWindow, sinceDay, tagAction, topicsOf, uniteTags,
  type Action, type ActionRead, type ActionTagsFile, type Body, type Dropped, type GridsFile, type RefreshFile, type StateFile, type TagChip, type TagRules, type Topic, type WeekRow,
} from "./policyweek";

/** The longest window the view offers, in days: the rows read. */
export const LONGEST = 30;

type Kept = { stamp: string; value: unknown; error: string | null };
const kept = new Map<string, Kept>();
/** A site file as JSON, or null with the reason. Read again only when the file on disk has changed. */
function siteFile<T>(at: string, isIt: (v: unknown) => boolean): { file: T | null; error: string | null } {
  let stamp: string;
  try { const s = fs.statSync(at); stamp = `${s.mtimeMs}:${s.size}`; } catch { return { file: null, error: "not there" }; }
  const had = kept.get(at);
  if (had && had.stamp === stamp) return { file: had.value as T | null, error: had.error };
  let value: unknown = null, error: string | null = null;
  try {
    value = JSON.parse(fs.readFileSync(at, "utf8"));
    if (!isIt(value)) { value = null; error = "not of the shape the page reads"; }
  } catch (e) { value = null; error = (e as Error).message; }
  kept.set(at, { stamp, value, error });
  return { file: value as T | null, error };
}
const obj = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);

/** The rule file and the file of the tags the warehouse's run gave: read by both views. */
const rulesFile = () => siteFile<TagRules>(path.join(process.cwd(), "data", "policy", "tag_rules.json"), (v) => obj(v) && obj(v.tags) && Array.isArray(v.fields_matched) && obj(v.municipal) && obj(v.agencies_in_scope));
const tagsFile = () => siteFile<ActionTagsFile>(path.join(process.cwd(), "data", "policy", "action_tags.json"), (v) => obj(v) && obj(v.tags));

/** The rule that tags nothing: what stands in when the rule file is not there. */
const NO_RULES: TagRules = { version: "", fields_matched: [], strip: [], agencies_in_scope: { federal: [], state: [] }, action_types_in_scope: [], municipal: { terms: [] }, tags: {} };

export type WeekData = {
  /** today, a UTC day: the windows count back from it */
  today: string;
  /** the rows of the last thirty days, of both kinds, already worded */
  rows: WeekRow[];
  bodies: Body[]; topics: Topic[]; grids: { key: string; name: string; why: string }[];
  /** rows held in the window that the view does not show, each with why */
  dropped: Dropped[];
  /** the hover of their count */
  droppedWhy: string;
  /** a read or a file that is not there: what, and the reason for its hover */
  missing: { what: string; why: string }[];
  held: { actions: number; dockets: number; ruleVersion: string; docketsBuilt: string | null; docketsInFile: number };
};

/** Everything the view shows, for the render at `now`. */
export async function weekData(now: number): Promise<WeekData> {
  const today = dayOf(now), since = sinceDay(today, LONGEST);
  const rulesAt = rulesFile();
  const tagsAt = tagsFile();
  const gridsAt = siteFile<GridsFile>(path.join(process.cwd(), "data", "policy", "grids.json"), (v) => obj(v) && Array.isArray(v.grids));
  const stateAt = siteFile<StateFile>(path.join(process.cwd(), "data", "policy", "state_rules.json"), (v) => obj(v) && Array.isArray(v.rows));
  const refreshAt = siteFile<RefreshFile>(path.join(process.cwd(), "data", "policy", "refresh.json"), (v) => obj(v) && Array.isArray(v.regulators));
  const missing: WeekData["missing"] = [];
  const note = (what: string, name: string, error: string | null) => { if (error) missing.push({ what, why: error === "not there" ? `The site's file ${name} is not in this page's files yet.` : `The site's file ${name} could not be read: ${error}.` }); };
  note("the tag rule", "data/policy/tag_rules.json", rulesAt.error);
  note("the tags of the printed text", "data/policy/action_tags.json", tagsAt.error);
  note("the grids", "data/policy/grids.json", gridsAt.error);
  note("the proceedings and orders of FERC and the state commissions", "data/policy/state_rules.json", stateAt.error);
  note("the regulators' lists", "data/policy/refresh.json", refreshAt.error);
  const rules = rulesAt.file ?? NO_RULES;

  const fields = ["agency", "action_type", "title", "abstract", "docket", "fr_document_number", "why", "model_id", "first_paragraph", "model_recheck", "model_rechecked_at"];
  const [a, r] = await Promise.all([
    attempt(() => rest<Action>("events", { select: ["event_id", "event_date", "status", "source_url", ...fields.map((k) => `${k}:extra->>${k}`)].join(","), table_name: "eq.policy_actions", event_date: `gte.${since}`, order: "event_date.desc,event_id" }, HOURLY, 10_000)),
    attempt(() => rest<ActionRead>("events", { select: ["action_event_id", "plain_read", "model_id", "recheck", "rechecked_at"].map((k) => `${k}:extra->>${k}`).join(","), table_name: "eq.policy_reads", order: "event_id" }, HOURLY, 10_000)),
  ]);
  if (!a.ok) missing.push({ what: "the actions of the live set", why: `The table policy_actions could not be read: ${a.reason}` });
  if (!r.ok) missing.push({ what: "the impact reads", why: `The table policy_reads could not be read: ${r.reason}` });
  const actions = a.ok ? a.data : [];
  const reads = new Map((r.ok ? r.data : []).map((x) => [x.action_event_id, x]));

  const stateRows = (stateAt.file?.rows ?? []).filter((s) => obj(s) && inWindow(String(s.date ?? ""), today, LONGEST));
  const bodies = bodiesOf(refreshAt.file, [...new Set(actions.map((x) => (x.agency ?? "").trim()).filter(Boolean))]);
  const topics = topicsOf(rules, stateAt.file?.topics ?? []);
  const rows: WeekRow[] = [], dropped: Dropped[] = [];
  let nActions = 0, nDockets = 0;
  for (const x of actions) {
    const first = (x.first_paragraph ?? "").trim() || (tagsAt.file?.first_paragraph?.[x.event_id] ?? "");
    const read = { ...x, first_paragraph: first || null };
    const hits = uniteTags(tagAction(read, rules), tagsAt.file?.tags?.[x.event_id], rules);
    const under = gridsAt.file ? gridsOfAction(read, hits, gridsAt.file, rules) : { grids: [], all: true };
    const got = actionRow(read, reads.get(x.event_id), hits, under, bodies, topics, rules);
    if (got.row) { rows.push(got.row); nActions += 1; } else if (got.dropped) dropped.push(got.dropped);
  }
  for (const s of stateRows) {
    const got = docketRow(s, bodies, topics, rules);
    if (got.row) { rows.push(got.row); nDockets += 1; } else if (got.dropped) dropped.push(got.dropped);
  }
  const grids = (gridsAt.file?.grids ?? []).filter((g) => obj(g) && typeof g.key === "string" && typeof g.name === "string")
    .map((g) => ({ key: g.key, name: g.name, why: `Actions and dockets that name ${g.name}, and those that name no grid operator.` }));
  return {
    today, rows, bodies, topics, grids, dropped, droppedWhy: dropped.length ? droppedTip(dropped, rules) : "", missing,
    held: { actions: nActions, dockets: nDockets, ruleVersion: rules.version, docketsBuilt: (stateAt.file?.built_at_utc ?? "").slice(0, 10) || null, docketsInFile: stateAt.file?.rows?.length ?? 0 },
  };
}

// ---- the first view's tags (session 164) -------------------------------------------------------------------------------

/** What the first view reads of an action to tag it: the fields the table's own read holds. */
export type TaggedRow = { event_id: string; agency?: string | null; action_type?: string | null; title?: string | null; docket?: string | null };
export type AllTags = {
  /** the rule's tags, as the filter's choices */
  topics: Topic[];
  /** each tagged action's chips, by event id; an action with no tag is not in it */
  chips: Record<string, TagChip[]>;
  ruleVersion: string;
  /** a file that is not there: what, and the reason for its hover */
  missing: { what: string; why: string }[];
};
/** The tags of every action the first view lists: the one rule file applied to each row as read, united with the tags
 * the warehouse's run gave from the printed text (data/policy/action_tags.json). No request, no model. */
export function allTags(rows: TaggedRow[]): AllTags {
  const rulesAt = rulesFile();
  const tagsAt = tagsFile();
  const missing: AllTags["missing"] = [];
  const note = (what: string, name: string, error: string | null) => { if (error) missing.push({ what, why: error === "not there" ? `The site's file ${name} is not in this page's files yet.` : `The site's file ${name} could not be read: ${error}.` }); };
  note("the tag rule", "data/policy/tag_rules.json", rulesAt.error);
  note("the tags of the printed text", "data/policy/action_tags.json", tagsAt.error);
  const rules = rulesAt.file ?? NO_RULES;
  const topics = topicsOf(rules, []);
  const chips: Record<string, TagChip[]> = {};
  for (const x of rows) {
    const read = { ...x, first_paragraph: tagsAt.file?.first_paragraph?.[x.event_id] ?? null };
    const mine = chipsOf(uniteTags(tagAction(read, rules), tagsAt.file?.tags?.[x.event_id], rules), topics, rules);
    if (mine.length) chips[x.event_id] = mine;
  }
  return { topics, chips, ruleVersion: rules.version, missing };
}
