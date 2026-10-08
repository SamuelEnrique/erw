// Energy Research Warehouse (ERW) site, session 156: three things the query does in one call.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-ready.mjs). Sessions 148 and 153
// found that the whole slow tail of Ask ERCOT, and every chart it lost, came from three things the query tool could not
// ask in one call. Each is now a form of the same tool (lib/chat/tools.ts, query), made with the database's existing
// interface: no function, no view and no migration was needed.
//
//   1. THE AVERAGE DAY BY HOUR: group_by "hour_of_day". 24 rows, "00" to "23", as one series.
//      - A table of hours or shorter steps (hourly demand, battery output): the rows of the period are read once and
//        grouped by the local hour of the day (tz). Each row carries the aggregation of that hour's rows, n (the rows)
//        and days (the local days behind it). An hour with fewer days than the period (the hour the clocks skip, a
//        day that is not whole) carries its own count; an hour with no row is absent and named. Nothing is filled.
//      - A table of months whose VARIABLES are the hours (avg_wind_mw_h00 to avg_wind_mw_h23): give the variable as
//        its stem ("avg_wind_mw_h"). The 24 variables are read in one request and returned as one series, with the
//        days the table itself counts behind them (its days_held, or a family of days beside the family of means).
//        Sessions 148 and 153 lost h13 and h24 here: the model read the 24 variables a few at a time.
//   2. A DATE COLUMN GROUPED BY YEAR: date_column names a column of an entities or events table that holds dates
//      (the queue's proposed_in_service_date); group_by year, month or day then groups by it, and start and end bound
//      it. With aggregation sum each row carries the megawatts (value) and the count of rows summed (n). A row whose
//      date is empty is counted apart and is in no group. h14 failed on this.
//   3. THE NEWEST DAY HELD: day "newest" (with end, the newest day before it). One small read finds the newest whole
//      day held for the table, entity and variable, and the query answers over that day, so a question about
//      "yesterday" is one call and not a search day by day (h03 and s12 took 5 to 10 model calls). A day is whole when
//      it holds every step its local day has (23, 24 or 25 hours of them); newer days that are not whole are named.
//
// The exported spec (lib/chat/spec.json, written by warehouse/chat/ask.py) is not touched: the three arguments are
// added to the schema the ERCOT profile shows the model (extendTools), and the guide below is appended to its prompt.
// The switch: ASK_FORMS=off on the server shows the model the tools as session 153 left them (the query tool itself
// still understands the arguments; nothing asks for them).

export const HOUR_OF_DAY = "hour_of_day";
export const NEWEST = "newest";
/** Session 161: the local calendar week now running, Monday to today, as one call (lib/chat/tools.ts, query). */
export const THIS_WEEK = "this_week";
/** The rows the read for "the newest day" asks for, newest first: one page. Two whole days of five-minute steps, a week
 * of fifteen-minute steps, four weeks of hours. */
export const NEWEST_READ = 700;
/** The same read on a table of days, months or years, where only the newest row's date is wanted (and whether the
 * filters name one series). */
export const NEWEST_READ_DATED = 50;
const HH = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, "0"));

/** Whether the panel shows the model the three forms: always, unless the server says ASK_FORMS=off. */
export function formsOffered(env: string | undefined = process.env.ASK_FORMS): boolean {
  return env !== "off";
}

/** The 24 variables of a family of hours, from its stem ("avg_wind_mw_h"), any one of its names ("avg_wind_mw_h07") or
 * the way a guide writes it ("avg_wind_mw_hNN", "avg_wind_mw_hHH"); null when the name is not of that form. `days`: the
 * family of day counts that stands beside a family of means (rt_mean_h00 has rt_days_h00), when the name has one. */
export function hourFamily(variable: string | undefined): { stem: string; names: string[]; days: string[] | null } | null {
  const m = /^(.*_h)(\d\d|NN|HH)?$/.exec(variable ?? "");
  if (!m) return null;
  const stem = m[1];
  const beside = /_mean_h$/.test(stem) ? stem.replace(/_mean_h$/, "_days_h") : null;
  return { stem, names: HH.map((h) => stem + h), days: beside ? HH.map((h) => beside + h) : null };
}

/** The steps an hour holds at a table's step ("PT1H" 1, "PT15M" 4, "PT5M" 12); null for a step that is not minutes or
 * hours dividing the hour, or when the rows do not share one step. */
export function stepsPerHour(freqs: (string | null | undefined)[]): number | null {
  const uniq = Array.from(new Set(freqs.filter((f): f is string => !!f)));
  if (uniq.length !== 1) return null;
  if (uniq[0] === "PT1H") return 1;
  const m = /^PT(\d+)M$/.exec(uniq[0]);
  if (!m) return null;
  const min = Number(m[1]);
  return min > 0 && 60 % min === 0 ? 60 / min : null;
}

export type DayCount = { day: string; rows: number; of: number | null; whole: boolean | null };
/** The newest whole day among rows given newest first. `dayOf` gives a row's local day; `stepsIn` the steps a whole
 * local day holds (null when the table's step is not known). `cut`: the read came back full, so its oldest day may be
 * cut short and is not judged. Returns every day seen, newest first, and the one to answer for: the newest whole day,
 * or, when none of the days read is whole, the newest day with whole false (null when no step is known): never a day
 * made whole by filling. */
export function newestWholeDay(times: string[], dayOf: (t: string) => string, stepsIn: (day: string) => number | null, cut: boolean): { days: DayCount[]; pick: DayCount | null } {
  const counts = new Map<string, number>();
  for (const t of times) { const d = dayOf(t); counts.set(d, (counts.get(d) ?? 0) + 1); }
  let days = Array.from(counts.keys()).sort().reverse().map((day) => {
    const of = stepsIn(day), rows = counts.get(day)!;
    return { day, rows, of, whole: of === null ? null : rows === of };
  });
  if (cut && days.length > 1) days = days.slice(0, -1);
  return { days, pick: days.find((d) => d.whole === true) ?? days[0] ?? null };
}

/** The group a date as a column writes it belongs to: "2028" for year, "2028-06" for month, "2028-06-01" for day. The
 * date is taken as written (a date column holds the source's own dates: no time zone moves it). null when the value
 * does not begin with a date, or for a group a date cannot give (an hour). */
export function dateLabel(value: string | null | undefined, group: string): string | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})(?![\d])/.exec(String(value ?? "").trim());
  if (!m) return null;
  return group === "year" ? m[1] : group === "month" ? `${m[1]}-${m[2]}` : group === "day" ? `${m[1]}-${m[2]}-${m[3]}` : null;
}
/** The columns of a table whose name says they hold a date. */
export const dateColumns = (columns: string[]): string[] => columns.filter((c) => /(^|_)date$/.test(c));

type Tool = { name: string; description?: string; input_schema: Record<string, unknown> };
const MORE = {
  date_column: { type: "string", description: "Entities and events tables only: a column of the table that holds dates (for example proposed_in_service_date, queue_date). group_by year, month or day then groups by this column, and start and end bound it (plain dates). Rows whose date is empty are counted apart." },
  day: { type: "string", enum: [NEWEST, THIS_WEEK], description: "Series tables only. \"this_week\": the local calendar week now running, Monday to today (in tz): give no start and no end; the result is over the days of it that are held and its week block lists them, and when none is held yet it is over the newest seven days held. \"newest\": answer over the newest whole day held for this table, entity and variable (in tz); give no start. With end, the newest whole day before end: for \"yesterday\" give end as today's date. On a table of days, months or years it is the newest row's date. The result's newest block says which day was read." },
};
const GROUP_MORE = ` Or "${HOUR_OF_DAY}" (series tables): the average day, 24 rows "00" to "23" by the local hour (tz), each with n (rows) and days (the days behind it); on a table of months whose variables are the hours (names ending _h00 to _h23) give variable as the stem ("avg_wind_mw_h").`;
const TOOL_MORE = ` Three more forms, each one call: group_by "${HOUR_OF_DAY}" (the average day by hour, 24 rows as one series); date_column (group an entities or events table by a date column, by year, month or day); day "${NEWEST}" (the newest whole day held).`;

function extended(schema: Record<string, unknown>): Record<string, unknown> {
  const props = (schema.properties ?? {}) as Record<string, Record<string, unknown>>;
  const group = props.group_by ? { ...props.group_by, description: `${String(props.group_by.description ?? "")}${GROUP_MORE}` } : props.group_by;
  return { ...schema, properties: { ...props, ...(group ? { group_by: group } : {}), ...MORE } };
}
/** The tools as the model is shown them: query, and the two queries of compare, with the three arguments added. Every
 * other tool, and everything else of these two, is as it was. Nothing is changed in place. */
export function extendTools<T extends Tool>(tools: T[]): T[] {
  return tools.map((t) => {
    if (t.name === "query") return { ...t, description: `${t.description ?? ""}${TOOL_MORE}`, input_schema: extended(t.input_schema) };
    if (t.name === "compare") {
      const props = (t.input_schema.properties ?? {}) as Record<string, Record<string, unknown>>;
      return { ...t, input_schema: { ...t.input_schema, properties: { ...props, ...(props.a ? { a: extended(props.a) } : {}), ...(props.b ? { b: extended(props.b) } : {}) } } };
    }
    return t;
  });
}

/** What the model is told of the three forms: appended to the profile's system prompt when they are offered. `pages`:
 * whether the four pages' tables are offered too (lib/chat/pagefiles.ts): two of the families of hours are theirs. */
export function formsGuide(pages = true): string {
  const theirs = pages ? ', "rt_mean_h" (cost_of_power_hourly_profile, entity "ercot:HB_HUBAVG": the average real-time price at each local hour), "curtailed_solar_mwh_h" and "curtailed_wind_mwh_h" (caiso_curtailment_profile, entity "caiso:ISO")' : "";
  return `

THREE THINGS THE QUERY DOES IN ONE CALL (session 156). Use them: each replaces several calls and several turns. These lines add to the rules above and govern where they differ.
- THE AVERAGE DAY BY HOUR: group_by "${HOUR_OF_DAY}". The result is 24 rows, "00" to "23", one series you can name in series (form "chart"). Never read the hours a few at a time, and never with group_by variable.
  - A table of hours (eia930_all_demand, eia930_all_generation, eia930_all_storage, the hub prices hour by hour): give entity, variable, tz "America/Chicago" and the period (start and end); aggregation mean gives the mean of each local hour, with n (the rows) and days (the days behind the hour). Say the period and that the hours are local. These tables hold about 35 days on this site: "an average day" is the days held unless a period is named.
  - A table of months whose variables are the hours: give variable as the stem, without the hour: "avg_wind_mw_h", "avg_solar_mw_h", "avg_storage_mw_h", "avg_demand_mw_h" (generation_mix_hourly_profile, entity "iso:ercot"), "avg_battery_mw_h", "avg_net_load_mw_h" (shoulder_hours_monthly, entity "iso:ercot"), "cf_share_pct_h" (clean_energy_summary, entity "iso:ercot")${theirs}. Give the month as start and end (one month: its own rows, the table's average day of that month), or day "${NEWEST}" for the newest month held; over several months the result is the mean of the months' values and says so. Each row carries days, the table's own count of days behind it.
  - For how the batteries charge and discharge across the hours of a day: shoulder_hours_monthly, variable "avg_battery_mw_h", entity "iso:ercot", day "${NEWEST}" (negative is charging, positive discharging), or eia930_all_storage by "${HOUR_OF_DAY}" over the days held. For wind, solar or demand across the hours of an average day: generation_mix_hourly_profile with the stem and day "${NEWEST}".
- A DATE COLUMN BY YEAR: date_column. On an entities or events table, group_by "year" (or "month", "day") groups by the table's status or event date, which the queue tables leave empty. Name the date column instead: ercot_interconnection_queue has queue_date and proposed_in_service_date (the date a project plans to come online); with aggregation "sum" each year's row gives the megawatts (value) and the count of projects (n) in one call. Its where values: status "active" or "completed"; fuel_technology "Other - Battery Energy Storage", "Solar - Photovoltaic Solar", "Wind - Wind Turbine" (call describe_table for the gas kinds). For battery capacity in the queue by the year it plans to come online: table ercot_interconnection_queue, aggregation "sum", date_column "proposed_in_service_date", group_by "year", where {"status": "active", "fuel_technology": "Other - Battery Energy Storage"}. Rows with no date are counted in the result and are in no year: say so when there are any.
- THE NEWEST DAY HELD: day "${NEWEST}". For yesterday, today, now, the latest day or "this morning" on a table of hours or of days, do not search day by day and do not count rows: give day "${NEWEST}" and no start, with tz "America/Chicago" on a table of hours, and end set to the day after the day asked (for "yesterday": end is today's date, so the day read is yesterday when it is held and whole, and otherwise the newest whole day before it; for "the latest" or "now": no end). It works with every aggregation and with group_by "hour" (a day hour by hour) or "${HOUR_OF_DAY}". The result's newest block says which day was read, whether it is whole, the newest row held and the newer days that are not whole: when the day read is not the day asked, say first that the day asked is not held whole and which day you give. Always give entity and variable with it.

TWO MORE, EACH ONE CALL (session 161). These lines add to the rules above and govern where they differ.
- THIS WEEK: day "${THIS_WEEK}". For "this week" or "so far this week" on a table of hours or of days, do not try one start after another and do not search for the days held: give day "${THIS_WEEK}", no start and no end, with tz "America/Chicago" on a table of hours, and always entity and variable. The week is the local calendar week now running, Monday to today. The result is over the days of that week that are held, and its week block lists every day with its rows: days_held, days_not_held, and days_held_in_part for a day that holds some of its rows. Answer from this one result and call nothing more for it: say which days of the week are held and give the figure for those days. When no day of this week is held yet (week.held false) the result is over the newest seven local days held instead (week.period_read): say first that this week is not held yet, then give that figure and the days it covers. It works with every aggregation, alone or with group_by "day" or "hour".
- GENERATION BY FUEL OVER A STRETCH OF DAYS (the past seven days, the last two weeks): never one call for each fuel, and never the hours themselves. One call gives every fuel: table eia930_all_generation, entity "eia930:ERCO", no variable, aggregation "mean", group_by "variable", tz "America/Chicago", start and end as plain dates. Each row is one fuel's mean output over the period in MW (the mean of its hourly readings), with n, the hours held; net_generation_mw is the total and net_generation_battery_mw is the batteries' net output (negative when they charged more than they discharged). For how the total moved day by day, one more call rolled up by day: the same table, variable "net_generation_mw", group_by "day". Name the day-by-day result first in series (form "chart") and the fuels' result second, give the fuels in words from the first call, and say which days the period holds (time_span). Do not query a fuel again on its own.`;
}
