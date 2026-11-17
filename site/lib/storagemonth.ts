// Energy Research Warehouse (ERW) site, ruling alternative 1 of /storage (session 7727, 17 November 2026; branch
// wip/alt-storage-1, not a default on main): a month's total discharge by grid in the daily cycle panel, beside the newest
// day and the 30-day spark. From storage_daily_cycle's daily rows (each grid's local day, dated at 00:00 UTC): the newest
// calendar month whose every day is held, summed. A month with a day missing is not summed (nothing is filled). On main
// the panel gives the newest day and the 30-day spark only. No imports: Node runs this file as it is.

export type DayRow = { entity: string; variable: string; ts_utc: string; value: number };
export type MonthTotal = { month: string; mwh: number; days: number; perDay: number };

const daysIn = (month: string) => new Date(Date.UTC(Number(month.slice(0, 4)), Number(month.slice(5, 7)), 0)).getUTCDate();

/** The newest whole month's total of one variable for one entity, or null when no month of the rows is whole. */
export function monthTotal(rows: DayRow[], entity: string, variable = "mwh_discharged"): MonthTotal | null {
  const by = new Map<string, Map<string, number>>();
  for (const r of rows) {
    if (r.entity !== entity || r.variable !== variable || !Number.isFinite(r.value)) continue;
    const m = r.ts_utc.slice(0, 7), d = r.ts_utc.slice(0, 10);
    (by.get(m) ?? by.set(m, new Map()).get(m)!).set(d, r.value);
  }
  for (const m of [...by.keys()].sort().reverse()) {
    const days = by.get(m)!;
    if (days.size === daysIn(m)) {
      const mwh = [...days.values()].reduce((a, b) => a + b, 0);
      return { month: m, mwh, days: days.size, perDay: mwh / days.size };
    }
  }
  return null;
}
