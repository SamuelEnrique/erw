// Session 57: the Texas severance refund finder's internal outputs (warehouse/derived/severance_screen.py), read on the
// server from the warehouse's output directory, where they exist only on a machine that built them: internal (the RRC
// grants no reuse in writing), never in git, the public database or a committed JSON. Like /severance/lease/real, the
// pages that read them answer 404 without the internal token.
import fs from "node:fs";

export type Totals = { leases: number; flags: number; months: number; base_tax: number; savings: number; with_savings: number };
export type Summary = {
  note: string; built: string; window: [string, string]; history_from: string; rules_version: string;
  dump: { newest: string; oil_extract: string; gas_extract: string };
  leases_screened: number; counties: number; total: Totals; by_rule: Record<string, Totals>;
  by_case?: Record<string, Totals>;
  by_county: ({ county: string } & Totals)[];
  by_operator: ({ operator_no: string; operator_name: string } & Totals)[];
  top_leases: { lease_id: string; savings: number; rules: string; county: string; operator_name: string; lease_name: string; code: string; months: number }[];
  cites: Record<string, { cite: string; source: { publisher: string; title: string; url: string }; code?: { cite: string; section: string; quote: string } }>;
  not_seen: Record<string, string[]>;
  prices: string;
};

// the path comes from the environment so the build does not trace (and bundle) the warehouse directory
export const outDir = () => process.env.ERW_OUTPUT_DIR || "../warehouse/output";
export const SUMMARY = "severance_screen_summary.json";
export const FLAGS = "severance_screen_flags.csv.gz";

export function readSummary(): Summary | null {
  const f = `${outDir()}/${SUMMARY}`;
  return fs.existsSync(f) ? (JSON.parse(fs.readFileSync(f, "utf8")) as Summary) : null;
}

/** The internal token check shared by the finder's page and its download: a token of 24 characters or more, equal. */
export function tokenOk(token: string | null | undefined): boolean {
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  return want.length >= 24 && token === want;
}

export const RULE_NAMES: Record<string, string> = {
  tx_lp_oil: "Low-producing oil lease credit (Exempt Type 11)",
  tx_lp_gas: "Low-producing gas well credit",
  tx_inactive: "Two-year inactive well exemption (oil Sec. 202.056(b); gas Type 16)",
};
