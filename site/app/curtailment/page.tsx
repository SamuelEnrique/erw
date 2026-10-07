import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Num } from "@/components/Num";
import { Related } from "@/components/Related";
import { SiteLink } from "@/components/SiteLink";
import { Term } from "@/components/Term";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import ercotJson from "@/data/curtailment/ercot.json";
import freeJson from "@/data/curtailment/free_energy.json";
import sharesJson from "@/data/curtailment/shares.json";
import worthJson from "@/data/curtailment/worth.json";
import profileJson from "@/data/curtailment_profile.json";
import {
  DURATIONS, GRIDS, MONTHLY, basisName, choiceOf, dayName, gridOf, link, monthName, periodShare, placeName, shareMarks, shareReason, two, whole,
  type Choice, type GridRow, type ShareGrid, type SharesFile,
} from "@/lib/curtailment";
import {
  CATS, FUELS, INPUT, REASONS, TABLE, battDay, batteryMonths, byHour, choice as periodChoice, hasBattery, hasCats, hourName, peakHour, periodName, periodOf, reasonCover,
  type CurtFile, type Row,
} from "@/lib/curtailmentv2";
import { daysAgo, series, type SeriesRow } from "@/lib/data";
import { count, price } from "@/lib/format";
import { FACE, ranked, type FreeFile } from "@/lib/freeenergy";
import { attempt } from "@/lib/supabase";
import { XY } from "./Charts";
import { Blank, FreeEnergy, N, Texas, Worth, freeChoice, type ErcotFile, type WorthFile } from "./Sections";

// Session 144: "Curtailment", one tool, one page, one address, in review (lib/release.ts), in the battery page's layout.
// It holds what /curtailment showed (every grid by day and by month, from the curtailment tables in Supabase) and what
// /curtailment/v2 showed (California by hour of the day, by month, by CAISO's reason, and against battery charging,
// from data/curtailment_profile.json); /curtailment/v2 redirects here (next.config.ts) and the two old pages are kept
// under app/_retired. New: every monthly share from data/curtailment/shares.json (one definition, no month reads "not
// computable"), Texas by hour for the days ERCOT's list held (ercot.json), "Where free energy is" (free_energy.json)
// and "What it is worth" (worth.json). The face says what each grid's number is in one line (FACE in
// lib/freeenergy.ts); every rule and every grid's own paragraph is in the Method note (docs/methods/curtailment.md). A
// figure that is not held is a short placeholder with its reason on hover. Every chart answers the mouse (Charts.tsx).
export const metadata: Metadata = { title: "Curtailment" };

const profile = profileJson as unknown as CurtFile;
const shares = sharesJson as unknown as SharesFile;
const free = freeJson as unknown as FreeFile;
const worth = worthJson as unknown as WorthFile;
const ercot = ercotJson as unknown as ErcotFile;
const METHOD = "/data/methods/curtailment";
const D = 86_400_000;
const exact = (v: number) => (Number.isInteger(v) ? count(v) : price(v));
const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
const sum = (rows: SeriesRow[], vars: string[]) => rows.filter((r) => vars.includes(r.variable)).reduce((a, r) => a + r.value, 0);
const LOCAL = "Turned down to relieve a congested line somewhere on the grid", SYSTEM = "Turned down because the whole system had more supply than it could use or export";

/** By day and by month, from the curtailment tables (what /curtailment showed), with the shares of shares.json. */
function DaysAndMonths({ g, monthly, daily, sg }: { g: GridRow; monthly: SeriesRow[]; daily: SeriesRow[]; sg: ShareGrid | undefined }) {
  const parts = g.parts ?? [];
  const months = Array.from(new Set([...monthly.map((r) => r.ts_utc.slice(0, 7)), ...Object.keys(sg?.months ?? {})])).sort();
  const days = Array.from(new Set(daily.map((r) => r.ts_utc))).sort().slice(-90);
  const byMonth = new Map(monthly.map((r) => [`${r.variable}|${r.ts_utc.slice(0, 7)}`, r]));
  const byDay = new Map(daily.map((r) => [`${r.variable}|${r.ts_utc}`, r.value]));
  const d0 = days.length ? Date.parse(days[0]) : 0, d1 = days.length ? Date.parse(days[days.length - 1]) + D : 0;
  const lastDays = daily.filter((r) => Date.parse(r.ts_utc) >= d0);
  const tableMonths = Array.from(new Set(monthly.map((r) => r.ts_utc.slice(0, 7)))).sort().slice(-13).reverse();
  const estimate = g.id === "ercot";
  // Texas: the days' share is the estimate's own, below the limit over the limit (the daily table holds both)
  const hsl = sum(lastDays, ["solar_hsl_mwh", "wind_hsl_mwh"]), below = sum(lastDays, ["solar_below_hsl_mwh", "wind_below_hsl_mwh"]);
  const shareCell = (m: string): ReactNode => {
    if (estimate) { const r = ercot.months[m]; return r?.both?.share_pct != null ? <N k={`share|${m}`}>{two(r.both.share_pct)}</N> : <Blank why={r?.missing ?? ercot.month_reason} />; }
    const r = sg?.months[m];
    return r ? <span title={`${whole(r.days_held)} of ${r.days_in_month} days. Output: ${shares.basis_words[r.basis] ?? r.basis}`}><N k={`share|${m}`}>{two(r.share_pct)}</N></span> : <Blank why={sg ? shareReason(sg, m) : "no output is held for this grid"} />;
  };
  return (
    <>
      <ToolSection title="By day" id="days">
        {days.length >= 2 ? (
          <>
            <ChartFrame title={`${g.name}, the last ${days.length} days, MWh`} legend={parts.map(([, label, color]) => ({ label, color }))} note="The grid's local operating days.">
              <XY id="days" x={days.map((t) => t.slice(0, 10))} unit="MWh" label={`${g.name} by day, ${days[0].slice(0, 10)} to ${days[days.length - 1].slice(0, 10)}`}
                series={parts.map(([v, label, color]) => ({ name: label, color, stack: "a", values: days.map((t) => byDay.get(`${v}|${t}`) ?? null) }))} />
            </ChartFrame>
            <p className="-mt-6 mb-10 text-sm" data-days-total="1">
              Total over these days:{" "}
              {parts.map(([v, label], i) => {
                const tot = sum(lastDays, [v]);
                return <span key={v}>{i > 0 ? "; " : ""}{label.toLowerCase()} <Num check={`series_esum|${g.daily}|${g.entity}|${v}|${iso(d0)}|${iso(d1)}`} raw={tot}>{exact(tot)}</Num> MWh</span>;
              })}
              {estimate && hsl > 0 ? <>; <span data-days-share="1">{((100 * below) / hsl).toFixed(2)}</span> percent of the limit</> : null}.
            </p>
          </>
        ) : <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">{g.name}, by day: <Blank why={`${g.daily} holds ${days.length} day in the live set`} /></p>}
      </ToolSection>

      <ToolSection title="By month" id="months">
        {months.length >= 2 ? (
          <ChartFrame title={`${g.name}, by month, MWh${sg ? ", and the share of available output" : ""}`} legend={[...parts.map(([, label, color]) => ({ label, color })), ...(sg ? [{ label: "Share of available output, percent", color: "var(--color-ink)" }] : [])]}>
            <XY id="months" x={months} unit="MWh" unit2="percent" zoom label={`${g.name} by month, ${months[0]} to ${months[months.length - 1]}`}
              series={[...parts.map(([v, label, color]) => ({ name: label, color, stack: "a", values: months.map((m) => byMonth.get(`${v}|${m}`)?.value ?? null) })),
                ...(sg ? [{ name: "Share of available output", color: "var(--color-ink)", kind: "line" as const, axis: 1 as const, digits: 2, unit: "percent", values: months.map((m) => sg.months[m]?.share_pct ?? null) }] : [])]}
              notes={months.map((m) => (sg && !sg.months[m] ? `Share not held yet: ${shareReason(sg, m)}` : !byMonth.has(`${parts[0]?.[0]}|${m}`) && sg?.months[m] ? `Curtailed over the ${sg.months[m].days_held} days held: ${whole(sg.months[m].curtailed_mwh)} MWh` : null))} />
          </ChartFrame>
        ) : (
          <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-months="none">{g.name}, a whole month: <Blank why={estimate ? ercot.month_reason : `${MONTHLY} holds no complete month for ${g.entity} yet`} /></p>
        )}
        {sg ? (() => {
          const marks = shareMarks(sg);
          return marks ? (
            <p className="mb-4 max-w-3xl text-sm" data-share-line="1">
              Share of available output: <N k="share|last">{two(sg.months[marks.last].share_pct)}</N> percent in {monthName(marks.last)}; the highest month held is {monthName(marks.highest)}, <N k="share|highest">{two(sg.months[marks.highest].share_pct)}</N> percent.{" "}
              <N k="share|months">{whole(sg.months_with_share)}</N> months have a share{Object.keys(sg.missing).length ? <>; {whole(Object.keys(sg.missing).length)} are <Blank why={Object.values(sg.missing)[0]} /></> : null}.
            </p>
          ) : null;
        })() : null}
        {tableMonths.length ? (
          <ToolTable minWidth={560} caption={`${g.name}: the last ${tableMonths.length} complete months`}
            head={["Month", ...parts.map(([, label]) => `${label}, MWh`), estimate ? "Share of the limit, percent" : "Share of available output, percent"]}
            rows={tableMonths.map((m) => ({ key: m, cells: [m, ...parts.map(([v]) => { const r = byMonth.get(`${v}|${m}`); return r ? <Num key={v} check={`series|${MONTHLY}|${g.entity}|${v}|${r.ts_utc}`} raw={r.value}>{exact(r.value)}</Num> : ""; }), shareCell(m)] }))} />
        ) : null}
        {estimate ? <p className="mt-3 text-sm">{Object.keys(ercot.months).sort().map((m, i) => <span key={m} data-month-missing={m}>{i ? "; " : ""}{monthName(m)}: {shareCell(m)}</span>)}.</p> : null}
      </ToolSection>
    </>
  );
}

/** California from CAISO's five-minute record (what /curtailment/v2 showed): by hour of the day, by reason, against the batteries. */
function California({ c, period, r }: { c: Choice; period: string; r: Row }) {
  const label = periodName(period);
  const months = Object.keys(profile.months).sort();
  const bm = batteryMonths(profile);
  // the batteries are compared by month: the period's own month, or for a year the newest month of it that holds them
  const battMonth = period.length === 7 ? (hasBattery(r) ? period : null) : bm.filter((m) => m.startsWith(period)).at(-1) ?? null;
  const br = battMonth ? profile.months[battMonth] : null;
  const dim = months.map((m) => !(m === period || m.slice(0, 4) === period));
  const s = byHour(r, "solar"), w = byHour(r, "wind");
  const reasonOf = (m: string, k: string) => (profile.months[m][`curtailed_solar_${k}_mwh`] ?? 0) + (profile.months[m][`curtailed_wind_${k}_mwh`] ?? 0);
  return (
    <>
      <ToolSection title="By hour of the day" id="hours">
        <ChartFrame title={`California, ${label}, MWh`} legend={FUELS.map((f) => ({ label: f.label, color: f.color }))} note="Pacific time; each bar is the period's total in that hour of the day.">
          <XY id="hours" x={s.map((_, h) => hourName(h))} unit="MWh" label={`California, ${label}: wind and solar curtailed by local hour of the day, MWh`}
            series={[{ name: "Solar", color: FUELS[0].color, stack: "a", values: s }, { name: "Wind", color: FUELS[1].color, stack: "a", values: w }]} />
        </ChartFrame>
      </ToolSection>

      <ToolSection title="By reason" id="reason">
        <ChartFrame title="By CAISO's reason, by month, MWh" legend={REASONS.map((x) => ({ label: x.label, color: x.color }))}>
          <XY id="months-reason" x={months} unit="MWh" zoom dim={dim} label={`California: wind and solar curtailed by month since ${profile.first.slice(0, 4)}, by CAISO's reason, MWh`}
            series={REASONS.map((x) => ({ name: x.label, color: x.color, stack: "a", values: months.map((m) => reasonOf(m, x.key)) }))}
            notes={months.map((m) => `${whole(profile.months[m].days_held)} of ${whole(profile.months[m].days_in_month)} days held`)} />
        </ChartFrame>
        <ToolTable minWidth={620} caption={`California, ${label}: curtailment by fuel and by CAISO's reason, MWh`}
          head={["", <span key="l" title={LOCAL} className="cursor-help underline decoration-dotted">Local congestion</span>, <span key="s" title={SYSTEM} className="cursor-help underline decoration-dotted">System-wide oversupply</span>, "No reason published", "All"]}
          rows={FUELS.map((f) => ({ key: f.key, cells: [f.label, ...REASONS.map((x) => <N key={x.key} k={`reason|${f.key}|${x.key}`}>{whole(r[`curtailed_${f.key}_${x.key}_mwh`] ?? 0)}</N>), <N key="all" k={`reason|${f.key}|all`}>{whole(r[`curtailed_${f.key}_mwh`])}</N>] }))} />
        {hasCats(r) ? (
          <div className="mt-6" data-cats="1">
            <ToolTable minWidth={620} caption={`California, ${label}: curtailment by CAISO's category, MWh`}
              head={["From 2026, CAISO also says how", ...FUELS.map((f) => `${f.label}, MWh`)]}
              rows={CATS.map((k) => ({ key: k.key, cells: [<span key="l">{k.label}<span className="block text-xs text-muted">{k.what}</span></span>, ...FUELS.map((f) => <N key={f.key} k={`cat|${f.key}|${k.key}`}>{whole(r[`curtailed_${f.key}_${k.key}_mwh`] ?? 0)}</N>)] }))} />
          </div>
        ) : null}
      </ToolSection>

      <ToolSection title="Against battery charging, in the same hours" id="batteries">
        {br && battMonth ? (
          <>
            {period !== battMonth ? <p className="mb-3 max-w-3xl text-sm" data-battery-month={battMonth}>Shown for {periodName(battMonth)}, the newest month of {label} with the batteries. Other months: {bm.map((m, i) => <span key={m}>{i ? ", " : ""}<Link href={link({ ...c, period: m }, "batteries")} className={item(m === battMonth)}>{m}</Link></span>)}.</p> : null}
            <HeadlineRow>
              <HeadlineNumber label={`Curtailed, ${periodName(battMonth)}`} value={<N k="batt|curtailed">{whole(br.curtailed_mwh_battery_days)}</N>} unit="MWh" note={<>Wind and solar, over the <N k="batt|days">{whole(br.battery_days_held)}</N> days both tables hold.</>} />
              <HeadlineNumber label="Taken in by the batteries" value={<N k="batt|charging">{whole(br.battery_charging_mwh)}</N>} unit="MWh" note={<>Over the same days, at every hour.</>} />
              <HeadlineNumber label="Curtailed while they charged" value={br.curtailed_while_charging_share_pct !== undefined ? <N k="batt|while">{two(br.curtailed_while_charging_share_pct)}</N> : <Blank why="no hour of the month has both figures" />} unit="percent" note={<>Of the curtailed MWh, the share in hours in which the batteries took in more than they gave back.</>} />
            </HeadlineRow>
            <ChartFrame title={`The average day of ${periodName(battMonth)}, MW`} legend={[{ label: "Wind and solar curtailed", color: "var(--color-fuel-solar)" }, { label: "Battery charging", color: "var(--color-fuel-storage)" }]} note="Pacific time.">
              <XY id="battery" x={battDay(br).map((p) => hourName(p.hour))} unit="MW" label={`California, ${periodName(battMonth)}: the average day's wind and solar curtailment and battery charging by local hour, MW`}
                series={[{ name: "Wind and solar curtailed", color: "var(--color-fuel-solar)", kind: "area", values: battDay(br).map((p) => p.curtailed) }, { name: "Battery charging", color: "var(--color-fuel-storage)", kind: "line", values: battDay(br).map((p) => p.charging) }]} />
            </ChartFrame>
          </>
        ) : <p className="border border-rule bg-paper px-3 py-2 text-sm" data-battery="none">{label}: <Blank why="CAISO's battery output is in the warehouse from late August 2025" />. Months with the batteries: {bm.map((m, i) => <span key={m}>{i ? ", " : ""}<Link href={link({ ...c, period: m }, "batteries")} className="text-ink">{m}</Link></span>)}.</p>}
      </ToolSection>
    </>
  );
}

export default async function CurtailmentPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const q = Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined]));
  const c = choiceOf(q);
  const g = gridOf(c.grid);
  const sg = shares.grids[c.grid];
  const fg = free.grids[c.grid];
  const period = periodChoice(q, profile);           // California's period: a year or a month the five-minute record holds
  const r = periodOf(profile, period)!;
  const fc = freeChoice(free, c);
  const keep: Choice = { ...c, period: c.grid === "caiso" && q.period === period ? period : null, place: fc.place && c.place === fc.place.id ? c.place : null };
  const [monthly, daily] = g.daily
    ? await Promise.all([attempt(() => series(MONTHLY, { entity: g.entity })), attempt(() => series(g.daily!, { entity: g.entity, since: daysAgo(100) }))])
    : [null, null];
  const months = Object.keys(profile.months).sort();
  const years = [...new Set(months.map((m) => m.slice(0, 4)))];
  const face = FACE[c.grid];
  const marks = sg ? shareMarks(sg) : null;
  const top = fg ? ranked(fg, fc.win)[0] : undefined;
  const cheap = top ? <>Its place with the most hours under USD {free.threshold_usd_per_mwh} {fc.win === "year" ? "in the last twelve months" : `in ${monthName(free.end_month)}`} is {placeName(top.id)}, with <N k="sum|cheap">{whole(top.win.under5)}</N>.</> : null;

  return (
    <ToolPage>
      <ToolHeader title="Curtailment"
        lead={<>When there is more wind and sun than the grid can take, the operator turns plants down: curtailment. Wind and solar output that could have been produced and was not, by day, month and hour, at <Term t="CAISO" first /> and <Term t="SPP" first /> since 2014
          and at <Term t="ERCOT" first /> for the days held; where power is priced near nothing, by hub and zone; and what the curtailed energy was worth. <SiteLink href={METHOD}>Method</SiteLink>. See also <SiteLink href="/mix">the energy mix</SiteLink> and <SiteLink href="/cost-of-power/battery">what a battery earns</SiteLink>.</>} />
      <div className="grid gap-8 lg:grid-cols-[250px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="Choose">
            <nav aria-label="Grid" className="mb-4 text-sm">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted">Grid</div>
              {GRIDS.map((x) => (x.open
                ? <div key={x.id} data-grid={x.id} data-open="1"><Link href={link({ grid: x.id, dur: c.dur })} aria-current={x.id === c.grid ? "true" : undefined} className={item(x.id === c.grid)}>{x.name}</Link></div>
                : <div key={x.id} data-grid={x.id} data-open="0" className="text-muted">{x.name} <span className="text-xs">{x.words}</span></div>))}
            </nav>
            {c.grid === "caiso" ? (
              <nav aria-label="Period" className="mb-4 text-sm">
                <div className="mb-1 text-xs uppercase tracking-wide text-muted">Period, California by the hour</div>
                {years.map((y) => (
                  <div key={y} className="mb-1.5 flex flex-wrap items-baseline gap-x-1.5 gap-y-0.5">
                    {profile.years[y] ? <Link href={link({ ...keep, period: y })} aria-current={period === y ? "true" : undefined} className={`w-9 text-xs ${item(period === y)}`}>{y}</Link> : <span className="w-9 text-xs text-muted">{y}</span>}
                    {months.filter((m) => m.startsWith(y)).map((m) => <Link key={m} href={link({ ...keep, period: m })} aria-current={m === period ? "true" : undefined} className={`text-xs ${item(m === period)}`}>{m.slice(5)}</Link>)}
                  </div>
                ))}
                {profile.days_not_held.length ? <p className="mt-2 text-xs"><Blank words={`${profile.days_not_held.length} day${profile.days_not_held.length === 1 ? "" : "s"} not held`} why={`${profile.days_not_held.join(", ")}: CAISO's report for the day could not be read whole`} /></p> : null}
              </nav>
            ) : null}
            {c.grid === "caiso" || c.grid === "ercot" ? (
              <nav aria-label="Battery" className="text-sm">
                <div className="mb-1 text-xs uppercase tracking-wide text-muted">Battery</div>
                <div className="flex gap-x-3">{DURATIONS.map((d) => <Link key={d} href={link({ ...keep, dur: d })} aria-current={d === c.dur ? "true" : undefined} className={item(d === c.dur)}>{d} hours</Link>)}</div>
              </nav>
            ) : null}
          </InputPanel>
        </aside>

        <div className="min-w-0">
          <p className="mb-3 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
            {c.grid === "caiso" ? (() => {
              const peak = peakHour(r), cover = reasonCover(r), ps = sg ? periodShare(sg, period) : null;
              const bm = batteryMonths(profile), battMonth = period.length === 7 ? (hasBattery(r) ? period : null) : bm.filter((m) => m.startsWith(period)).at(-1) ?? null, br = battMonth ? profile.months[battMonth] : null;
              return (
                <>In {periodName(period)}, California curtailed <N k="sum|solar">{whole(r.curtailed_solar_mwh)}</N> MWh of solar and <N k="sum|wind">{whole(r.curtailed_wind_mwh)}</N> MWh of wind{ps ? <>, <N k="sum|share">{two(ps.share)}</N> percent of its available wind and solar output</> : null}, more in the hour from {hourName(peak.hour)} than in any other.{" "}
                  {cover === "none" ? <>CAISO published no reason for it then.</> : <><N k="sum|local">{whole(r.curtailed_solar_local_mwh + r.curtailed_wind_local_mwh)}</N> MWh was for local congestion and <N k="sum|system">{whole(r.curtailed_solar_system_mwh + r.curtailed_wind_system_mwh)}</N> MWh for system-wide oversupply{cover === "part" ? ", with no reason published for the rest" : ""}.</>}{" "}
                  {br && br.curtailed_while_charging_share_pct !== undefined ? <>In {periodName(battMonth!)}, <N k="sum|while">{two(br.curtailed_while_charging_share_pct)}</N> percent of it fell in hours in which the batteries were already charging.</> : null}</>
              );
            })() : c.grid === "spp" && sg && marks ? (
              <>In {monthName(marks.last)}, SPP curtailed <N k="sum|curtailed">{whole(sg.months[marks.last].curtailed_mwh)}</N> MWh of wind and solar, <N k="sum|share">{two(sg.months[marks.last].share_pct)}</N> percent of its available output; its highest month held is {monthName(marks.highest)}, at <N k="sum|highest">{two(sg.months[marks.highest].share_pct)}</N> percent. {cheap}</>
            ) : c.grid === "ercot" ? (
              <>Over the {ercot.whole_days} days held, {ercot.first_day ? dayName(ercot.first_day) : ""} to {ercot.last_day ? dayName(ercot.last_day) : ""}, Texas wind and solar output stood <N k="sum|below">{whole(ercot.window.both.below_hsl_mwh)}</N> MWh below the limit the plants reported, <N k="sum|share">{two(ercot.window.both.share_pct ?? 0)}</N> percent of it: <N k="sum|wind">{two(ercot.window.wind.share_pct ?? 0)}</N> percent for wind and <N k="sum|solar">{two(ercot.window.solar.share_pct ?? 0)}</N> for solar. {cheap}</>
            ) : (
              <>{g.name}: no curtailment figure is in the ERW. {cheap}</>
            )}
          </p>
          <p className="mb-6 max-w-3xl text-sm" data-face={c.grid}>{face?.line}</p>

          {c.grid === "caiso" ? (() => {
            const peak = peakHour(r), cover = reasonCover(r);
            const days = period.length === 7 ? <><N k="days_held">{whole(r.days_held)}</N> of {whole(r.days_in_month)} days</> : <><N k="days_held">{whole(r.days_held)}</N> of {whole(r.days_in_period)} days, {r.months} months</>;
            const ps = sg ? periodShare(sg, period) : null;
            return (
              <>
                <HeadlineRow>
                  <HeadlineNumber label="Solar curtailed" value={<N k="head|solar">{whole(r.curtailed_solar_mwh)}</N>} unit="MWh" note={<>Over {days}.</>} />
                  <HeadlineNumber label="Wind curtailed" value={<N k="head|wind">{whole(r.curtailed_wind_mwh)}</N>} unit="MWh" note={<>The hour with the most, wind and solar: {hourName(peak.hour)} (<N k="head|peak_solar">{whole(peak.solar)}</N> MWh of solar, <N k="head|peak_wind">{whole(peak.wind)}</N> of wind in the period).</>} />
                  <HeadlineNumber label="For local congestion" value={cover === "none" ? <Blank words="not published" why="CAISO's file gives a reason from 2022" /> : <N k="head|local">{whole(r.curtailed_solar_local_mwh + r.curtailed_wind_local_mwh)}</N>} unit={cover === "none" ? undefined : "MWh"}
                    note={cover === "none" ? undefined : <>System-wide oversupply: <N k="head|system">{whole(r.curtailed_solar_system_mwh + r.curtailed_wind_system_mwh)}</N> MWh.{cover === "part" ? <> No reason published: <N k="head|unspecified">{whole(r.curtailed_solar_unspecified_mwh + r.curtailed_wind_unspecified_mwh)}</N> MWh.</> : null}</>} />
                </HeadlineRow>
                <HeadlineRow>
                  <HeadlineNumber label={`Share of available output, ${periodName(period)}`} value={ps ? <N k="head|share">{two(ps.share)}</N> : <Blank why={sg ? shareReason(sg, period) : "no share is held"} />} unit={ps ? "percent" : undefined}
                    note={ps ? <>Curtailed over curtailed plus CAISO&apos;s own wind and solar output{period.length === 4 ? `, the ${ps.months} months of ${period} with a share` : ""}.</> : undefined} />
                  <HeadlineNumber label="The highest month held" value={marks && sg ? <N k="head|highest">{two(sg.months[marks.highest].share_pct)}</N> : <Blank why="no share is held" />} unit="percent" note={marks ? <>{monthName(marks.highest)}. <Link href={link({ ...keep, period: marks.highest })} className="text-ink">Open that month</Link>.</> : undefined} />
                  <HeadlineNumber label={`Hours under USD ${free.threshold_usd_per_mwh}, ${top ? placeName(top.id) : "California"}`} value={top ? <N k="head|cheap">{whole(top.win.under5)}</N> : <Blank why="no place holds the window" />} unit={top ? "hours" : undefined}
                    note={top ? <>{fc.win === "year" ? "The last twelve months" : monthName(free.end_month)}, {basisName(top.win.basis)}. <a href="#free-energy" className="text-ink">Where free energy is</a>.</> : undefined} />
                </HeadlineRow>
              </>
            );
          })() : c.grid === "spp" && sg && marks ? (
            <HeadlineRow>
              <HeadlineNumber label={`Share of available output, ${monthName(marks.last)}`} value={<N k="head|share">{two(sg.months[marks.last].share_pct)}</N>} unit="percent" note={<>Over {whole(sg.months[marks.last].days_held)} of {sg.months[marks.last].days_in_month} days.</>} />
              <HeadlineNumber label="Curtailed that month" value={<N k="head|curtailed">{whole(sg.months[marks.last].curtailed_mwh)}</N>} unit="MWh" note={<>Wind and solar, SPP&apos;s balancing authority area.</>} />
              <HeadlineNumber label="The highest month held" value={<N k="head|highest">{two(sg.months[marks.highest].share_pct)}</N>} unit="percent" note={<>{monthName(marks.highest)}.{sg.not_covered ? <> SPP&apos;s western area: <Blank words="no share" why={Object.values(sg.not_covered)[0]} />.</> : null}</>} />
            </HeadlineRow>
          ) : c.grid === "ercot" ? (
            <HeadlineRow>
              <HeadlineNumber label={`Below the limit, the ${ercot.whole_days} days held`} value={<N k="head|below">{whole(ercot.window.both.below_hsl_mwh)}</N>} unit="MWh" note={<>Wind <N k="head|wind">{whole(ercot.window.wind.below_hsl_mwh)}</N>, solar <N k="head|solar">{whole(ercot.window.solar.below_hsl_mwh)}</N>.</>} />
              <HeadlineNumber label="As a share of the limit" value={<N k="head|share">{two(ercot.window.both.share_pct ?? 0)}</N>} unit="percent" note={(() => { const best = Object.entries(ercot.days).filter(([, d]) => d.whole && d.both.share_pct !== null).sort((a, b) => (b[1].both.share_pct ?? 0) - (a[1].both.share_pct ?? 0))[0]; return best ? <>The highest day: {dayName(best[0])}, <N k="head|highest">{two(best[1].both.share_pct ?? 0)}</N> percent.</> : undefined; })()} />
              <HeadlineNumber label="A whole month" value={<Blank why={Object.values(ercot.months).find((m) => m.missing)?.missing ?? ercot.month_reason} />} note={<>Before the first reading: <Blank words={ercot.history} why={ercot.history_reason} />.</>} />
            </HeadlineRow>
          ) : (
            <HeadlineRow>
              <HeadlineNumber label={`Curtailed, ${g.name}`} value={<Blank words="not in the ERW" why={face?.line ?? ""} />} />
              <HeadlineNumber label="Share of available output" value={<Blank words="not in the ERW" why={face?.line ?? ""} />} />
              <HeadlineNumber label={`Most hours under USD ${free.threshold_usd_per_mwh}`} value={top ? <N k="head|cheap">{whole(top.win.under5)}</N> : <Blank why="no place holds the window" />} unit={top ? "hours" : undefined} note={top ? <>{placeName(top.id)}, {fc.win === "year" ? "the last twelve months" : monthName(free.end_month)}.</> : undefined} />
            </HeadlineRow>
          )}

          {g.daily && monthly && daily ? (
            !monthly.ok || !daily.ok
              ? <p className="mb-10 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number of it is shown: {!monthly.ok ? monthly.reason : !daily.ok ? daily.reason : ""}</p>
              : <DaysAndMonths g={g} monthly={monthly.data} daily={daily.data} sg={sg} />
          ) : null}
          {c.grid === "caiso" ? <California c={keep} period={period} r={r} /> : null}
          {c.grid === "ercot" ? <Texas file={ercot} estimate={FACE.ercot.line} /> : null}

          <FreeEnergy file={free} c={keep} />
          <Worth file={worth} c={{ ...keep, period: c.grid === "caiso" ? period : null }} estimate={FACE.ercot.line} />

          <ToolSection title="What each grid's number is" id="whose">
            <ToolTable caption="What each grid's number is" words minWidth={560} head={["Grid", "Its number"]}
              rows={GRIDS.map((x) => ({ key: x.id, highlight: x.id === c.grid, muted: !x.open, cells: [x.name, <span key="l" className="block text-left" data-whose={x.id}>{FACE[x.id]?.line}</span>] }))} />
          </ToolSection>

          <div className="mb-8 border-t border-rule">
            {sg ? (
              <Fold title={`Every month's share, ${g.name}`}>
                <ToolTable minWidth={620} caption={`${g.name}: the share of available wind and solar output curtailed, every month`}
                  head={["Month", "Curtailed, MWh", "Wind and solar output, MWh", "Share, percent", "Days held"]}
                  rows={[...Object.keys(sg.months), ...Object.keys(sg.missing)].sort().reverse().map((m) => { const x = sg.months[m]; return x
                    ? { key: m, cells: [<span key="m" title={`Output: ${shares.basis_words[x.basis] ?? x.basis}`}>{m}</span>, whole(x.curtailed_mwh), whole(x.output_mwh), <span key="s" data-share-month={m}>{two(x.share_pct)}</span>, `${x.days_held} of ${x.days_in_month}`] }
                    : { key: m, muted: true, cells: [m], wide: <span data-share-missing={m}><Blank why={sg.missing[m]} /></span> }; })} />
              </Fold>
            ) : null}
            {c.grid === "caiso" ? (
              <Fold title="By month, from the five-minute record">
                <ChartFrame title={`Wind and solar curtailed, by month since ${profile.first.slice(0, 4)}, MWh`} legend={FUELS.map((f) => ({ label: f.label, color: f.color }))}>
                  <XY id="months-fuel" x={months} unit="MWh" zoom dim={months.map((m) => !(m === period || m.slice(0, 4) === period))} label={`California: wind and solar curtailed by month since ${profile.first.slice(0, 4)}, by fuel, MWh`}
                    series={FUELS.map((f) => ({ name: f.label, color: f.color, stack: "a", values: months.map((m) => profile.months[m][`curtailed_${f.key}_mwh`] ?? 0) }))}
                    notes={months.map((m) => `${whole(profile.months[m].days_held)} of ${whole(profile.months[m].days_in_month)} days held`)} />
                </ChartFrame>
              </Fold>
            ) : null}
          </div>
          <SourceLine tables={[...(g.daily ? [g.daily, MONTHLY] : []), ...(c.grid === "caiso" ? [TABLE, INPUT, "caiso_battery_storage"] : []), ...(c.grid === "ercot" ? ercot.tables : []), ...(fc.place ? [...new Set(Object.values((fc.place as unknown as { tables: Record<string, string[]> }).tables).flat())] : [])]}
            note={<>Data: California ISO, Production and curtailments data, the Daily Renewable Report and Today&apos;s Outlook; Southwest Power Pool, VER Curtailments; ERCOT, Wind and Solar Power Production; EIA-930; each grid&apos;s public prices. Credit: California ISO. Built {profile.built.slice(0, 10)} (California by the hour), {shares.built.slice(0, 10)} (shares), {free.built.slice(0, 10)} (prices), {worth.built.slice(0, 10)} (worth), {ercot.built.slice(0, 10)} (Texas). This page is in review.</>} />
          <Related href="/curtailment" />
        </div>
      </div>
    </ToolPage>
  );
}
