import type { Metadata } from "next";
import { AskErcotLink } from "@/components/AskErcotLink";
import Link from "next/link";
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { attempt } from "@/lib/supabase";
import { GRIDS, TABLE, checkKey, choices, completeMonths, dayKey, dayName, hourName, monthName, monthOf, opening, shown, view, type Row, type View } from "@/lib/shoulder";
import { shoulderRows } from "./read";

// Session 75: "The shoulder hours". Solar floods the middle of the day and demand peaks in the evening; how long is the
// stretch between them (this page calls it the evening shoulder, a term defined here, not an industry standard), how much
// of it does the battery fleet operating that month cover, and how many hours would it need to cover all of it? For
// ERCOT and CAISO, from shoulder_hours_monthly (warehouse/derived/shoulder_hours.py; docs/methods/shoulder_hours.md):
// every number is a row of that table with its check key, so the page does no arithmetic. In review (lib/release.ts).
// The panel's links point at this same page (another grid or month): plain next/link, as /storage/buildout's (the page
// is in review, so a gated link to it would render greyed in the server's HTML).
export const metadata: Metadata = { title: "The shoulder hours" };
export const revalidate = 3600;

const METHOD = "/data/methods/shoulder_hours";
const COLOR = { demand: "var(--color-ink)", net_load: "var(--color-accent)", solar: "var(--color-fuel-solar)", battery: "var(--color-fuel-storage)", covered: "var(--color-ink)" };

/** An hour of the day from the table, with its check key: "18:00" (check-values reads its leading value). */
function Hr({ row }: { row: Row | undefined }) {
  if (!row) return <span className="text-muted">not held</span>;
  return <Num check={checkKey(row)} raw={row.value}>{`${String(row.value).padStart(2, "0")}:00`}</Num>;
}

function V({ row, unit }: { row: Row | undefined; unit?: string }) {
  if (!row) return <span className="text-muted">not held</span>;
  return <><Num check={checkKey(row)} raw={row.value}>{shown(row.value)}</Num>{unit ? ` ${unit}` : ""}</>;
}

/** Session 80: a figure of a worst day; its row is dated the day, and so is its check key. */
function D({ row, hour }: { row: Row | undefined; hour?: boolean }) {
  if (!row) return <span className="text-muted">not held</span>;
  return <Num check={dayKey(row)} raw={row.value}>{hour ? `${String(row.value).padStart(2, "0")}:00` : shown(row.value)}</Num>;
}

/** The average day, hour by hour: demand, net load, solar and battery output, the shoulder shaded. */
function DayChart({ v }: { v: View }) {
  const W = 760, H = 300, L = 62, R = 12, top = 16, bot = 34;
  const series: ("demand" | "net_load" | "solar" | "battery")[] = ["demand", "net_load", "solar", ...(v.hasBattery ? ["battery" as const] : [])];
  const vals = series.flatMap((s) => Array.from({ length: 24 }, (_, h) => v.hour(s, h)?.value ?? 0));
  const hi = Math.max(...vals) * 1.08, lo = Math.min(0, ...vals) * 1.08;
  const x = (h: number) => L + (h / 24) * (W - L - R);
  const y = (val: number) => top + ((hi - val) / (hi - lo)) * (H - top - bot);
  const step = [1000, 2000, 5000, 10000, 20000].find((s) => (hi - lo) / s <= 6) ?? 20000;
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);
  const s0 = v.get("shoulder_start_hour")?.value, s1 = v.get("shoulder_end_hour")?.value;
  const mean = v.get("net_load_mean_mw")?.value;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${v.grid.name}, the average day of ${monthName(v.month)}, MW by local hour`}>
      {s0 !== undefined && s1 !== undefined && s1 > s0 ? <rect x={x(s0)} y={top} width={x(s1) - x(s0)} height={H - top - bot} fill="var(--color-paper)" /> : null}
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{(t || 0).toLocaleString("en-US")}</text>
        </g>
      ))}
      {mean !== undefined ? <line x1={L} x2={W - R} y1={y(mean)} y2={y(mean)} stroke="var(--color-accent)" strokeDasharray="4 3" strokeWidth="1" /> : null}
      {series.map((s) => (
        <path key={s} d={Array.from({ length: 24 }, (_, h) => `${h ? "L" : "M"}${x(h + 0.5).toFixed(1)},${y(v.hour(s, h)?.value ?? 0).toFixed(1)}`).join(" ")}
          fill="none" stroke={COLOR[s]} strokeWidth={s === "net_load" ? 2.5 : 1.75}>
          <title>{`${s.replace("_", " ")}: ${Array.from({ length: 24 }, (_, h) => `${hourName(h)} ${Math.round(v.hour(s, h)?.value ?? 0).toLocaleString("en-US")}`).join(", ")} MW`}</title>
        </path>
      ))}
      {[0, 3, 6, 9, 12, 15, 18, 21, 24].map((h) => <text key={h} x={x(h)} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{hourName(h).replace("midnight", "24:00")}</text>)}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">MW, local time</text>
    </svg>
  );
}

/** By month since 2019: the shoulder's length and the hours the fleet covers. */
function MonthChart({ v }: { v: View }) {
  const W = 760, H = 240, L = 46, R = 12, top = 16, bot = 30;
  const pts = v.monthly;
  const hi = Math.max(8, ...pts.map((p) => Math.max(p.shoulder?.value ?? 0, p.covered?.value ?? 0))) * 1.05;
  const x = (i: number) => L + ((i + 0.5) / pts.length) * (W - L - R);
  const y = (val: number) => top + ((hi - val) / hi) * (H - top - bot);
  const line = (k: "shoulder" | "covered") => pts.map((p, i) => (p[k] ? `${i && pts[i - 1][k] ? "L" : "M"}${x(i).toFixed(1)},${y(p[k]!.value).toFixed(1)}` : "")).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${v.grid.name}: the evening shoulder's length and the hours the battery fleet covers, by month`}>
      {[0, 2, 4, 6, 8].filter((t) => t <= hi).map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.5 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      <path d={line("shoulder")} fill="none" stroke={COLOR.net_load} strokeWidth="2" />
      <path d={line("covered")} fill="none" stroke={COLOR.covered} strokeWidth="2" />
      {pts.map((p, i) => (p.month.endsWith("-01") ? <text key={p.month} x={x(i)} y={H - 10} textAnchor="middle" fontSize="11" fill="var(--color-muted)">{p.month.slice(0, 4)}</text> : null))}
      {pts.map((p, i) => <rect key={`t${p.month}`} x={x(i) - 3} y={top} width={6} height={H - top - bot} fill="transparent"><title>{`${monthName(p.month)}: shoulder ${p.shoulder ? shown(p.shoulder.value) : "not held"} hours; fleet covers ${p.covered ? shown(p.covered.value) : "not held"}`}</title></rect>)}
      <text x={L} y={11} fontSize="11" fill="var(--color-muted)">hours</text>
    </svg>
  );
}

export default async function Shoulder({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const read = await attempt(shoulderRows);
  const rows = read.ok ? read.data : [];
  const months: Record<string, string[]> = Object.fromEntries(GRIDS.map((g) => [g.slug,
    [...new Set(rows.filter((r) => r.entity === g.entity && r.variable === "days_held").map((r) => monthOf(r.ts_utc)))].sort()]));
  // session 90: with no month named the page opens on the latest month that holds every figure, not on the newest
  // (whose fleet EIA has not published yet); the panel still lists every month held, and says which are incomplete
  const complete: Record<string, string[]> = Object.fromEntries(GRIDS.map((g) => [g.slug, completeMonths(rows, g)]));
  const { grid, month } = choices(q, months, complete);
  const later = month ? (months[grid.slug] ?? []).filter((m) => m > month && !(complete[grid.slug] ?? []).includes(m)) : [];
  const v = month ? view(rows, grid, month) : null;
  const toMidnight = v?.get("shoulder_runs_to_midnight")?.value === 1;
  const toMidnight2 = v?.get("shoulder2_runs_to_midnight")?.value === 1;
  const worstNeeded = v?.year.get("year_worst10_mean_shoulder_hours_needed");
  const href = (g: string, m: string) => `/shoulder?grid=${g}&month=${m}`;
  const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
  const years = [...new Set((months[grid.slug] ?? []).map((m) => m.slice(0, 4)))];
  return (
    <ToolPage>
      <ToolHeader title="The shoulder hours"
        lead={<>Solar floods the middle of the day and demand peaks in the evening. Between them is a stretch this page calls the evening shoulder (its term,
          defined below, not an industry standard): how long it lasts, how much of it the batteries operating that month cover, and how many hours they would need
          to cover all of it. California and Texas, on the average day of each month and on the ten worst days of each year. See also <SiteLink href="/cost-of-power/battery">what a battery earns</SiteLink>,{" "}
          <SiteLink href="/storage/buildout">the storage build-out</SiteLink> and <SiteLink href="/curtailment">curtailment</SiteLink>.</>} />
      {grid.slug === "ercot" && month ? <AskErcotLink context={{ view: "/shoulder", title: "The shoulder hours", settings: { grid: "ERCOT", month } }} /> : null}
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose" note={grid.note}>
            <nav aria-label="Grid" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              {GRIDS.map((g) => <div key={g.slug}><Link href={href(g.slug, opening(months[g.slug] ?? [], complete[g.slug] ?? []) ?? "")} aria-current={g.slug === grid.slug ? "true" : undefined} className={item(g.slug === grid.slug)}>{g.name}</Link></div>)}
            </nav>
            <nav aria-label="Month" className="text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Month</div>
              {years.map((y) => (
                <div key={y} className="mb-1.5 flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
                  <span className="w-9 text-xs text-muted">{y}</span>
                  {(months[grid.slug] ?? []).filter((m) => m.startsWith(y)).map((m) => (
                    <Link key={m} href={href(grid.slug, m)} aria-current={m === month ? "true" : undefined} className={`text-xs ${item(m === month)}`}>{m.slice(5)}</Link>
                  ))}
                </div>
              ))}
              {!q.month && later.length ? <p className="mt-2 text-xs text-muted" data-opening={month ?? ""}>Opened on {monthName(month!)}, the latest month that holds every figure. {later.map(monthName).join(" and ")} {later.length === 1 ? "is" : "are"} held,
                but not every figure of {later.length === 1 ? "it" : "them"} yet (EIA publishes the battery fleet a month or two behind).</p> : null}
            </nav>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!read.ok || !v ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status"><span className="font-semibold">no data</span> for the shoulder hours: {read.ok ? `${TABLE} holds no month for ${grid.name}` : read.reason}</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                In {monthName(v.month)}, {grid.by}{grid.short}&apos;s evening shoulder lasted <V row={v.get("shoulder_hours")} /> hours, from <Hr row={v.get("shoulder_start_hour")} /> to{" "}
                <Hr row={v.get("shoulder_end_hour")} />{toMidnight ? " (midnight)" : ""}; its batteries could run <V row={v.get("fleet_hours")} /> hours at full power, covering <V row={v.get("shoulder_hours_covered")} /> of them.{" "}
                To deliver all of the shoulder&apos;s energy above the mean they would need <V row={v.get("shoulder_hours_needed")} /> hours on the average day{worstNeeded
                  ? <>, and <V row={worstNeeded} /> on the ten worst days of {v.year.year}.</>
                  : v.worst.length ? <>; on the ten worst days of {v.year.year} the fleet is not held for every day, so no figure is given.</> : <>; the worst days of {v.year.year} are not held for {grid.name}.</>}
              </p>
              <HeadlineRow>
                <HeadlineNumber label="The evening shoulder" value={<V row={v.get("shoulder_hours")} />} unit="hours"
                  note={<><Hr row={v.get("shoulder_start_hour")} /> to <Hr row={v.get("shoulder_end_hour")} />{toMidnight ? ", cut at midnight: net load stays above its daily mean" : ""}. <V row={v.get("shoulder_mwh_above_mean")} unit="MWh" /> of net load above the day&apos;s mean.</>} />
                <HeadlineNumber label="Hours the battery fleet covers" value={<V row={v.get("shoulder_hours_covered")} />} unit="hours"
                  note={<><V row={v.get("fleet_mw")} unit="MW" /> holding <V row={v.get("fleet_mwh")} unit="MWh" />. At that power, all of the shoulder&apos;s MWh above the mean would take <V row={v.get("shoulder_hours_needed")} unit="hours" />.</>} />
                <HeadlineNumber label="The midday surplus" value={<V row={v.get("midday_surplus_mwh")} />} unit="MWh"
                  note={<>Net load below its daily mean for <V row={v.get("midday_surplus_hours")} /> hours around its low at <Hr row={v.get("midday_low_hour")} />.{v.get("curtailed_mwh_per_day") ? <> Curtailed: <V row={v.get("curtailed_mwh_per_day")} unit="MWh a day" /> (CAISO&apos;s own count).</> : <> Curtailment is not held for {grid.name}.</>}</>} />
              </HeadlineRow>

              <ToolSection title="The average day">
                <ChartFrame title={`${grid.name}, ${monthName(v.month)}: MW by local hour`}
                  legend={[{ label: "Demand", color: COLOR.demand }, { label: "Net load (demand less solar and wind)", color: COLOR.net_load }, { label: "Solar", color: COLOR.solar },
                    ...(v.hasBattery ? [{ label: "Batteries (positive discharging)", color: COLOR.battery }] : [])]}
                  note={<>The shaded band is the evening shoulder; the dashed line is net load&apos;s daily mean. Each hour is the mean of that hour over the month&apos;s <V row={v.get("days_held")} /> complete days.{v.hasBattery ? null : <> Battery output is not held for {grid.name} this month.</>}</>}>
                  <DayChart v={v} />
                </ChartFrame>
              </ToolSection>

              <ToolSection title="By month since 2019">
                <ChartFrame title="The shoulder's length and the hours the fleet covers, hours" legend={[{ label: "Evening shoulder", color: COLOR.net_load }, { label: "Hours the fleet covers", color: COLOR.covered }]}
                  note="The fleet covers the smaller of the shoulder's length and its own duration (its MWh over its MW). Hover for each month.">
                  <MonthChart v={v} />
                </ChartFrame>
              </ToolSection>

              <ToolSection title="A shoulder that ends inside the evening, and the worst days" id="worst"
                note={<>The second measure is the run of hours around the evening&apos;s highest net load in which net load is above the midpoint between its daily mean and that peak. The worst days are the ten complete days of the year with the most evening shoulder energy above the day&apos;s own mean; a day of 23 or 25 hours is not ranked.</>}>
                <HeadlineRow>
                  <HeadlineNumber label="The shoulder, second measure" value={<V row={v.get("shoulder2_hours")} />} unit="hours"
                    note={<><Hr row={v.get("shoulder2_start_hour")} /> to <Hr row={v.get("shoulder2_end_hour")} />{toMidnight2 ? ", still above the midpoint at midnight" : ""}, on the average day of {monthName(v.month)}. <V row={v.get("shoulder2_mwh_above_midpoint")} unit="MWh" /> above the midpoint.</>} />
                  <HeadlineNumber label="Hours needed, second measure" value={<V row={v.get("shoulder2_hours_needed")} />} unit="hours"
                    note={<>At the fleet&apos;s power, to deliver the energy above the midpoint. The evening peak is <V row={v.get("evening_peak_mw")} unit="MW" /> at <Hr row={v.get("evening_peak_hour")} />.</>} />
                  <HeadlineNumber label={`The ten worst days of ${v.year.year}`} value={<V row={v.year.get("year_worst10_mean_shoulder_hours_needed")} />} unit="hours needed"
                    note={<>Against <V row={v.year.get("year_mean_shoulder_hours_needed")} /> on the year&apos;s average day. Ranked among <V row={v.year.get("year_days_ranked")} /> complete days; the batteries ran <V row={v.year.get("year_worst10_mean_battery_hours")} /> hours at rated power in those shoulders.</>} />
                </HeadlineRow>
                {v.worst.length === 0 ? (
                  <p className="max-w-3xl border border-rule bg-paper px-3 py-2 text-sm" data-worst="none">The worst days of {v.year.year} are not held for {grid.name}: the table has no ranked day for it.</p>
                ) : (
                  <ToolTable caption={`${grid.name}: the ten days of ${v.year.year} with the largest evening shoulder`} minWidth={760}
                    head={["Rank", "Day", "Above its mean, MWh", "Shoulder, h", "From", "Needed, h", "Second measure, h", "Needed (second), h", "Batteries discharged, MWh", "Batteries ran, h"]}
                    rows={v.worst.map((w) => ({
                      key: w.day,
                      cells: [<D key="r" row={w.get("worst_rank")} />, dayName(w.day), <D key="e" row={w.get("day_shoulder_mwh_above_mean")} />, <D key="h" row={w.get("day_shoulder_hours")} />,
                        <D key="s" row={w.get("day_shoulder_start_hour")} hour />, <D key="n" row={w.get("day_shoulder_hours_needed")} />, <D key="h2" row={w.get("day_shoulder2_hours")} />,
                        <D key="n2" row={w.get("day_shoulder2_hours_needed")} />, <D key="b" row={w.get("day_battery_discharge_mwh")} />, <D key="bh" row={w.get("day_battery_hours")} />],
                    }))} />
                )}
              </ToolSection>

              <ToolSection title="By year" note="Each year: the mean over its months held of the average day's figures; the fleet as at the year's last month that has one (EIA's inventory is published a month or two behind).">
                <ToolTable caption="The shoulder hours by year" minWidth={640}
                  head={["Year", "Months", "Shoulder, h", "Above mean, MWh", "Midday surplus, MWh", "Fleet, MW", "Fleet, h", "Covered, h", "Needed, h"]}
                  rows={v.years.map((y) => ({
                    key: y.year,
                    cells: [y.year, <V key="m" row={y.get("year_months_held")} />, <V key="s" row={y.get("year_mean_shoulder_hours")} />,
                      <V key="e" row={y.get("year_mean_shoulder_mwh_above_mean")} />, <V key="ms" row={y.get("year_mean_midday_surplus_mwh")} />, <V key="f" row={y.get("year_end_fleet_mw")} />,
                      <V key="fh" row={y.get("year_end_fleet_hours")} />, <V key="c" row={y.get("year_mean_shoulder_hours_covered")} />, <V key="n" row={y.get("year_mean_shoulder_hours_needed")} />],
                  }))} />
                <div className="mt-6">
                  <ToolTable caption="By year: the second measure and the ten worst days" minWidth={640}
                    head={["Year", "Shoulder (second), h", "Needed (second), h", "Days ranked", "Worst ten: above mean, MWh", "Worst ten: needed, h", "Worst ten: needed (second), h", "Worst ten: batteries ran, h"]}
                    rows={v.years.map((y) => ({
                      key: `w${y.year}`,
                      cells: [y.year, <V key="s2" row={y.get("year_mean_shoulder2_hours")} />, <V key="n2" row={y.get("year_mean_shoulder2_hours_needed")} />, <V key="d" row={y.get("year_days_ranked")} />,
                        <V key="we" row={y.get("year_worst10_mean_shoulder_mwh_above_mean")} />, <V key="wn" row={y.get("year_worst10_mean_shoulder_hours_needed")} />,
                        <V key="wn2" row={y.get("year_worst10_mean_shoulder2_hours_needed")} />, <V key="wb" row={y.get("year_worst10_mean_battery_hours")} />],
                    }))} />
                </div>
              </ToolSection>

              <div className="mb-8 border-t border-rule">
                <Fold title="The definitions, exactly as computed">
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                    <li><strong>The average day:</strong> for each local hour, the mean over the month&apos;s complete days (every hour of demand, solar and wind held) of EIA-930&apos;s hourly demand, solar (SUN and SNB), wind (WND and WNB) and battery output. A month with fewer than 90 percent of its days complete is not shown.</li>
                    <li><strong>Net load:</strong> demand less solar and wind.</li>
                    <li><strong>The midday surplus:</strong> the run of hours around net load&apos;s lowest hour in which net load is below its daily mean; its MWh are the sum, over those hours, of the mean less net load.</li>
                    <li><strong>The evening shoulder:</strong> from the first hour after solar&apos;s highest hour in which solar is below half of that highest value, to the first hour, after net load has risen above its daily mean, in which net load is back at or below that mean. If net load stays above the mean to midnight, the shoulder ends at midnight and the page says so. Its MWh are the sum, over its hours, of net load less the mean.</li>
                    <li><strong>The fleet:</strong> the batteries operating that month in EIA&apos;s monthly generator inventory (EIA-860M), their MW and MWh. Its hours are its MWh over its MW. <em>Hours covered</em> is the smaller of the shoulder&apos;s length and the fleet&apos;s hours; <em>hours needed</em> is the shoulder&apos;s MWh above the mean over the fleet&apos;s MW.</li>
                    <li><strong>The second measure:</strong> the run of hours around the evening&apos;s highest net load (the highest from the shoulder&apos;s start to midnight) in which net load is above the midpoint between its daily mean and that peak; its MWh are the sum, over those hours, of net load less the midpoint. Hours covered and hours needed are computed against it as against the first.</li>
                    <li><strong>The worst days:</strong> each complete day of 24 local hours is measured as the average day is, on its own hours and against its own mean. The ten with the most shoulder energy above the mean in each local year are ranked. <em>Hours needed</em> on a day is its shoulder energy over the fleet&apos;s MW of that month; where the month&apos;s fleet is not published yet it is not given, and the year&apos;s figure is the mean over all ten or is not given. <em>Batteries discharged</em> is the fleet&apos;s output in the shoulder&apos;s hours, where every hour of the day holds it; <em>batteries ran</em> is that over the fleet&apos;s MW.</li>
                    <li><strong>California, EIA-930:</strong> {GRIDS[1].note}</li>
                    <li><strong>California, CAISO&apos;s own data:</strong> {GRIDS[2].note}</li>
                  </ul>
                </Fold>
                <Fold title="What this cannot see">
                  <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                    <li><strong>More than ten days a year.</strong> The worst days here are ranked by one measure, shoulder energy above the day&apos;s mean. A cloudy week or a calm evening that is hard for another reason is not singled out, and several bad days in a row are counted one by one.</li>
                    <li><strong>The transmission grid and local constraints.</strong> The figures are whole-grid; a battery in the wrong place cannot serve load behind a congested line.</li>
                    <li><strong>Capacity accreditation.</strong> What a grid counts a battery as for reliability is its own rule, not its MWh over its MW.</li>
                    <li><strong>Everything else that serves the shoulder:</strong> gas, imports, hydro and demand response. The arithmetic asks only what the batteries alone could cover.</li>
                    <li><strong>The mean is a choice.</strong> A shoulder measured against another level (the evening peak&apos;s half, say) would be shorter; the definition is this page&apos;s.</li>
                  </ul>
                </Fold>
              </div>
            </>
          )}
        </div>
      </div>
      <SourceLine tables={[TABLE, "storage_buildout_monthly", "caiso_battery_storage", "caiso_curtailment_daily", "caiso_fuel_supply"]}
        note={<>Derived by the ERW from EIA Form EIA-930 hourly demand and generation by energy source (the per-BA workbooks), CAISO&apos;s supply by fuel and EIA-860M. <SiteLink href={METHOD}>Method</SiteLink>.</>} />
    </ToolPage>
  );
}
