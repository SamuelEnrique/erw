// Energy Research Warehouse (ERW) site, session 156: the two switches of Ask ERCOT's speed, and where their default lives.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-ready.mjs). Session 148 built
// two changes behind server switches and left both off, because 98 of the 100 test questions passed with them on and
// the rule then was that a change is switched on only when all 100 pass:
//
//   ASK_RULE_PLAN       a plan made by rule: for a question of a known shape the read is written by code, and there is
//                       no reading turn by the model (lib/chat/plan.ts);
//   ASK_READER_EFFORT   the effort of the reading turn, the model call that decides what to read.
//
// THE OWNER'S RULING OF 8 OCTOBER 2026: "Ask ERCOT's two switches (ASK_RULE_PLAN=on, ASK_READER_EFFORT=low) are set."
// So both are now set BY DEFAULT, here, in SWITCH_DEFAULTS, and nowhere else: lib/chat/ask.ts asks rulePlanOn() and
// readerEffort() and holds no default of its own. The server variable still governs when it is set:
//
//   ASK_RULE_PLAN=off        no question is planned by rule (any value other than "on" is off);
//   ASK_READER_EFFORT=off    the reading turn is given the effort every other call has (any value that is not one of
//                            low, medium, high is ignored, as before); medium or high name another effort.
//
// A variable that is unset or empty is the default. No switch touches a ceiling (lib/chat/limits.ts).

export const SWITCH_DEFAULTS = { ASK_RULE_PLAN: "on", ASK_READER_EFFORT: "low" } as const;

type Env = Record<string, string | undefined>;
/** A server variable's value, or null when it is unset or empty: the default then holds. */
const given = (v: string | undefined): string | null => (v === undefined || v.trim() === "" ? null : v.trim());

/** Whether a question of a known shape is planned by rule: yes unless the server says otherwise. */
export function rulePlanOn(env: Env = process.env): boolean {
  return (given(env.ASK_RULE_PLAN) ?? SWITCH_DEFAULTS.ASK_RULE_PLAN) === "on";
}

/** The effort asked for the reading turn: the server's value when it gives one, else the default. The caller uses it
 * only when it is a setting the model takes (lib/chat/ask.ts, READER_EFFORTS): "off" is none of them. */
export function readerEffort(env: Env = process.env): string {
  return given(env.ASK_READER_EFFORT) ?? SWITCH_DEFAULTS.ASK_READER_EFFORT;
}
