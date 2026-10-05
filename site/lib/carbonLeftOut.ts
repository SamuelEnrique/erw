import file from "@/data/carbon_left_out.json";

// Session 118: the months of carbon_intensity_monthly a page must not show. The three carbon tables are behind a live
// page, so the rule for impossible values (docs/methods/impossible_hours.md) is in their builder and held until a
// person approves the numbers it moves. Until then the table still carries months computed on an impossible hour of
// demand or of net generation, and California's months without hydro. warehouse/derived/carbon_left_out.py lists them
// from the same rule; a page in review leaves them out and says so. When the hold is lifted the table no longer holds
// those months and the list is empty by itself.

export type LeftOutMonth = { entity: string; ba: string; variable: string; month: string; why: string; hours_total: number };
type File = {
  table: string; built: string; held: string[];
  hydro_gap: { entity: string; first_hour: string; last_hour: string; hours: number };
  rule: { jump: number; range: number[] };
  months: LeftOutMonth[];
};
const F = file as unknown as File;

export const CARBON_HYDRO_GAP = F.hydro_gap;
export const CARBON_LEFT_OUT_BUILT = F.built;

const KEYS = new Set(F.months.map((m) => `${m.entity}|${m.variable}|${m.month}`));

/** True when the month of this row (ts_utc: its first day) is one the rule leaves out for this entity and variable. */
export function carbonLeftOut(entity: string, variable: string, tsUtc: string): boolean {
  return KEYS.has(`${entity}|${variable}|${tsUtc.slice(0, 7)}`);
}

/** The months left out for one variable, optionally of one entity, oldest first. */
export function carbonLeftOutMonths(variable: string, entity?: string): LeftOutMonth[] {
  return F.months.filter((m) => m.variable === variable && (!entity || m.entity === entity)).sort((a, b) => a.entity.localeCompare(b.entity) || a.month.localeCompare(b.month));
}

/** "2019-10 to 2020-01, 2020-03" : a list of months with runs of consecutive months folded. */
export function monthRuns(months: string[]): string {
  const next = (m: string) => {
    const [y, mo] = m.split("-").map(Number);
    return mo === 12 ? `${y + 1}-01` : `${y}-${String(mo + 1).padStart(2, "0")}`;
  };
  const out: string[] = [];
  const sorted = [...new Set(months)].sort();
  for (let i = 0; i < sorted.length; ) {
    let j = i;
    while (j + 1 < sorted.length && sorted[j + 1] === next(sorted[j])) j++;
    out.push(j > i ? `${sorted[i]} to ${sorted[j]}` : sorted[i]);
    i = j + 1;
  }
  return out.join(", ");
}
