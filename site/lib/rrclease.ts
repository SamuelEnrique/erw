// Session 49: "Load a real lease" (/severance/lease/real, behind the internal token). The Railroad Commission of
// Texas's monthly production by lease, the warehouse's internal table rrc_lease_production_monthly (one Permian county,
// warehouse/connectors/rrc_production.py), turned into the lease tool's file: one row per month, the lease as one
// well. Pure functions and type imports only, so Node runs this file as it is (site/scripts/test-lease.mjs).
import type { COLUMNS } from "./lease";

export type RrcRow = {
  entity: string; variable: string; ts_utc: string; value: number; lease_name: string; operator_name: string;
  operator_no: string; field_name: string; district: string; oil_gas_code: string; wells: number; county: string;
};
export type RrcLease = {
  entity: string; name: string; operator: string; operatorNo: string; field: string; district: string; code: string;
  wells: number; county: string; months: Record<string, { oil_bbl?: number; casinghead_gas_mcf?: number; gas_mcf?: number; condensate_bbl?: number }>;
};

/** Parse the table's CSV text (the leading # header lines skipped): one RrcLease per entity. */
export function parseRrc(text: string): { header: string[]; leases: Map<string, RrcLease> } {
  const lines = text.split(/\r?\n/);
  const header = lines.filter((l) => l.startsWith("#")).map((l) => l.replace(/^#\s?/, ""));
  const body = lines.filter((l) => l && !l.startsWith("#"));
  const cols = splitCsv(body[0]);
  const ix = (c: string) => {
    const i = cols.indexOf(c);
    if (i < 0) throw new Error(`rrc_lease_production_monthly: no column ${c}`);
    return i;
  };
  const I = { e: ix("entity"), v: ix("variable"), t: ix("ts_utc"), val: ix("value"), n: ix("x_lease_name"), o: ix("x_operator_name"),
    on: ix("x_operator_no"), f: ix("x_field_name"), d: ix("x_district"), c: ix("x_oil_gas_code"), w: ix("x_wells"), cty: ix("x_county") };
  const leases = new Map<string, RrcLease>();
  for (const line of body.slice(1)) {
    const r = splitCsv(line);
    const e = r[I.e];
    let l = leases.get(e);
    if (!l) {
      l = { entity: e, name: r[I.n], operator: r[I.o], operatorNo: r[I.on], field: r[I.f], district: r[I.d], code: r[I.c],
        wells: Number(r[I.w]), county: r[I.cty], months: {} };
      leases.set(e, l);
    }
    const m = r[I.t].slice(0, 7);
    (l.months[m] ??= {})[r[I.v] as "oil_bbl"] = Number(r[I.val]);
  }
  return { header, leases };
}

/** One CSV line, RFC 4180 quoting (the table quotes names that hold commas or quotes). */
export function splitCsv(line: string): string[] {
  const out: string[] = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (q) {
      if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') q = false;
      else cur += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { out.push(cur); cur = ""; }
    else cur += ch;
  }
  out.push(cur);
  return out;
}

/** The lease tool's file for one lease: state TX, the lease as one well (well_id its RRC id), each month's volumes.
 * gas_mcf is the gas well's gas, or an oil lease's casinghead gas (gas produced with the oil, in the tool's gas column); prices
 * are left blank, so the tool uses the warehouse's monthly WTI and Henry Hub means; well_type oil or gas from the
 * RRC's oil or gas lease code. Nothing else is known from the table, so the other columns are blank. */
export function leaseCsv(l: RrcLease, columns: typeof COLUMNS): string {
  // the columns are passed in (lib/lease's COLUMNS), so this file keeps type imports only and Node runs it as it is
  const col = (c: string) => columns.indexOf(c as (typeof columns)[number]);
  const rows = Object.keys(l.months).sort().map((m) => {
    const v = l.months[m];
    const cells: string[] = columns.map(() => "");
    cells[col("state")] = "TX";
    cells[col("well_id")] = l.entity.replace(/^rrc:/, "RRC-");
    cells[col("month")] = m;
    const gas = (v.gas_mcf ?? 0) + (v.casinghead_gas_mcf ?? 0);
    if (v.oil_bbl !== undefined) cells[col("oil_bbl")] = String(v.oil_bbl);
    if (v.gas_mcf !== undefined || v.casinghead_gas_mcf !== undefined) cells[col("gas_mcf")] = String(gas);
    if (v.condensate_bbl !== undefined) cells[col("condensate_bbl")] = String(v.condensate_bbl);
    cells[col("well_type")] = l.code === "G" ? "gas" : "oil";
    return cells.join(",");
  });
  return [`# RRC lease ${l.entity.replace(/^rrc:/, "")}: ${l.name.replaceAll(",", " ")}, ${l.operator.replaceAll(",", " ")} (rrc_lease_production_monthly, internal)`,
    columns.join(","), ...rows].join("\n");
}
