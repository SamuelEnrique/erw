// Energy Research Warehouse (ERW) site, session 83: the contracts page's read. ferc_eqr_contracts is an internal table:
// row-level security hides it from the anon key, and two database functions (migration 020) answer only with the
// internal token, which this server holds as INTERNAL_COSTS_TOKEN and never sends to a browser. Without the token on
// the server, or with one the database does not accept, nothing is read and the page says so.
import "server-only";
import { DataError, rpc } from "@/lib/supabase";
import type { Contract, Summary } from "@/lib/contracts";

function token(): string {
  const t = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (t.length < 24) throw new DataError("this server holds no internal token (INTERNAL_COSTS_TOKEN)");
  return t;
}

export async function contractSummary(): Promise<Summary> {
  return rpc<Summary>("internal_eqr_summary", { p_token: token() });
}

export async function contractRows(from: string, to: string): Promise<Contract[]> {
  return rpc<Contract[]>("internal_eqr_contracts", { p_token: token(), p_from: from, p_to: to, p_limit: "5000" });
}
