import { AskErcotLink } from "@/components/AskErcotLink";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { InlineSpark } from "@/components/InlineSpark";
import { LineChart, type Line } from "@/components/LineChart";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { ShareBar } from "@/components/ShareBar";
import { StackedArea } from "@/components/StackedArea";
import type { SeriesRow } from "@/lib/data";
import { count, shown } from "@/lib/format";
import { FUELS, fuelName, fuelOf, type GridData } from "@/lib/grid";
import { gridHref } from "@/lib/gridtool";
import { DOCS, render, type GridConfig } from "@/lib/markdown";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";
import { Reliability } from "./Reliability";
import { CaisoBreakNote } from "@/components/CaisoBreakNote";  // session 73
import { CaisoMixWithheld } from "@/components/CaisoMixWithheld";  // session 118
import { carbonLeftOut, carbonLeftOutMonths, monthRuns } from "@/lib/carbonLeftOut";  // session 118
import { Missing } from "@/components/mix/Now";  // session 1167: "license needed", the tool's one look (session 1159)
import { heldQueue, type Held } from "@/lib/gridHeld";  // session 1167
import { licenseHeldRow, licenseTitle, LICENSE_NEEDED } from "@/lib/license";  // session 1167
import { PanelFile, type FileCell } from "@/components/grid/PanelFile";  // session 1420: each older block's figures, to download
import { heldBy } from "@/components/Num";  // session 1420: the datacenters' figures are held whole (lib/license.ts)
// session 1421: each older block's anchor and the section of its note that defines it (one constant a link, as session 1184)
import { METHOD_BATTERIES, METHOD_BUILDING_DATACENTERS, METHOD_BUILDING_QUEUE, METHOD_COST, METHOD_RIGHT_NOW, OLDER_ANCHOR } from "@/lib/gridAnchors";

// Session 35: "Ask your grid". One template, seven pages (docs/grids/grids.json), for a student in a first energy
// course: who runs the grid, where the power comes from now, what it costs, how clean it is, what is being built,
// what is different. Each block renders only when the warehouse holds this grid's rows; otherwise it says so in one
// line and names where EIA (or the ISO) publishes it. Every number is a row of a live-set table or a sum of rows,
// each with a check key that site/scripts/check-values.mjs recomputes. The written layer is docs/grids/<slug>.md.
// Session 237: this file was app/grid/[iso]/page.tsx, the seven grid pages. The Grid tool (/grid, lib/gridtool.ts) is the one
// page now; /grid/<iso> redirects to it (next.config.ts) and its blocks are drawn by the tool's views: GridNowParts in
// Now, GridMixParts in Mix, GridCleanParts in Clean. The Ask box is the tool's Ask view (components/grid/AskView.tsx).
// Nothing a grid page showed is dropped; each block is as it was.
// Session 1420 (chain 111): the older blocks that show a table of figures (Right now, Batteries, What it costs, What is
// being built) are named panels (grid_rightnow_<grid>, grid_batteries_<grid>, grid_cost_<grid>, grid_building_<grid>),
// each offering its figures as a file (components/grid/PanelFile.tsx, session 1182): the same figure nodes the block
// draws, its tables, filter, window and drawing time in the file's first lines. A held grid's block draws a held line
// and no figure, and offers no file; a held figure in a file is written "license needed" (Num's heldBy), never its value.
const UTC_HOUR = (ts: string) => `the hour starting ${ts.slice(0, 16).replace("T", " ")} UTC`;

const H = 3_600_000;
const EIA = (g: GridConfig) => `https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/balancing_authority/${g.entity.split(":")[1]}`;
const isoTs = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const local = (ts: string, tz: string, withDay = true) =>
  new Intl.DateTimeFormat("en-US", { timeZone: tz, ...(withDay ? { month: "short", day: "numeric" } : {}), hour: "numeric", minute: "2-digit", timeZoneName: "short" }).format(new Date(ts));
const localDay = (t: number, tz: string) => new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(t));

function Chip({ tier }: { tier: "source" | "derived" | "model_extracted" | "written" }) {
  const label = tier === "written" ? "written, cited" : TIER_LABEL[tier];
  const title = tier === "written" ? "Text written for this site, with its sources named; not data" : TIER_TITLE[tier];
  return (
    <Link href="/data/standard" title={title} className="ml-1 border border-rule px-1 text-xs text-muted no-underline">
      {label}
    </Link>
  );
}

/** The one line a block shows when the warehouse does not hold this grid's data. */
function NotYet({ what, where, href }: { what: string; where: string; href: string }) {
  return (
    <p className="border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
      <span className="font-semibold text-ink">Not in the warehouse yet:</span> {what}. {where}: <a href={href} className="break-all">{href}</a>.
    </p>
  );
}

/** Session 1167: a block of a grid held for a license, its words in the tool's one look, the publishers on hover. */
function HeldLine({ what, held }: { what: string; held: Held }) {
  return <p className="text-sm text-muted" role="status" data-grid-held={what}>{what}: <Missing why={held.why} words={held.words} /></p>;
}

/** Session 1411: a block whose read failed (lib/grid.ts load keeps the reason in d.errors), said in the tool's one look
 *  with session 1181's words, the table and the reason on hover; never "not in the warehouse yet", and no figure of it. */
function Unread({ what, table, reason }: { what: string; table: string; reason: string }) {
  return <p className="text-sm text-muted" role="status" data-grid-unread={table}>{what}: <Missing words="could not be read" why={`${table} could not be read just now: ${reason}`} /></p>;
}

const key = (t: string, r: SeriesRow) => `series|${t}|${r.entity}|${r.variable}|${r.ts_utc}`;
const N = ({ t, r }: { t: string; r?: SeriesRow }) => (r ? <Num check={key(t, r)} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">none</span>);
const latestOf = (rows: SeriesRow[], v: string) => rows.filter((r) => r.variable === v).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc)).at(-1);

// ------------------------------------------------------------------ 1. right now

function RightNow({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "eia930_all_demand";
  const rows = d.demand.filter((r) => r.variable === "demand_mw").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const last = rows.at(-1);
  if (!last) return <NotYet what={`${g.iso}'s hourly demand`} where="EIA publishes it in its Hourly Electric Grid Monitor" href={EIA(g)} />;
  const lt = Date.parse(last.ts_utc);
  const today = localDay(lt, g.tz);
  const so = rows.filter((r) => localDay(Date.parse(r.ts_utc), g.tz) === today);
  const weekAgo = rows.filter((r) => localDay(Date.parse(r.ts_utc) + 7 * 24 * H, g.tz) === today);
  const sameHour = rows.find((r) => Date.parse(r.ts_utc) === lt - 7 * 24 * H);
  const start = so[0].ts_utc, end = isoTs(lt + H);
  const peak = so.reduce((a, b) => (b.value > a.value ? b : a));
  const lines: Line[] = [
    { label: `${today} so far`, color: "accent", points: so.map((r) => ({ t: Date.parse(r.ts_utc) / 1000, v: r.value })) },
    { label: "Same day last week", color: "muted", points: weekAgo.map((r) => ({ t: (Date.parse(r.ts_utc) + 7 * 24 * H) / 1000, v: r.value })) },
  ];
  // session 1420: the day's highest hour, drawn once and filed
  const peakNum = <Num check={`series_max|${T}|demand_mw|${start}|${end}|${g.entity}`} raw={peak.value}>{shown(peak.value)}</Num>;
  const fileRows: FileCell[][] = [
    ["Demand in the latest hour EIA has published", UTC_HOUR(last.ts_utc), <N key="v" t={T} r={last} />, "MW"],
    ["The same hour a week earlier", UTC_HOUR(isoTs(lt - 7 * 24 * H)), sameHour ? <N key="v" t={T} r={sameHour} /> : "not held", "MW"],
    [`Highest hour so far on ${today} (${g.tz_label})`, UTC_HOUR(peak.ts_utc), peakNum, "MW"],
  ];
  return (
    <>
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <div className="text-sm">
          <div className="text-xs text-muted">Demand in the latest hour EIA has published ({local(last.ts_utc, g.tz)})</div>
          <div className="mb-2 text-3xl tabular-nums"><N t={T} r={last} /> <span className="text-sm text-muted">MW</span></div>
          <div className="text-xs text-muted">The same hour a week earlier</div>
          <div className="mb-2 tabular-nums">{sameHour ? <><N t={T} r={sameHour} /> MW</> : <span className="text-muted">not held</span>}</div>
          <div className="text-xs text-muted">Highest hour so far on {today} ({g.tz_label})</div>
          <div className="tabular-nums">
            {peakNum} MW at {local(peak.ts_utc, g.tz, false)}
          </div>
        </div>
        <div className="min-w-0">
          <LineChart lines={lines} unit="MW" height={220} ariaLabel={`${g.iso} hourly demand today so far and the same day last week`} />
        </div>
      </div>
      <p className="mt-1 text-xs text-muted">
        Demand is how much power customers use each hour. EIA publishes each grid&apos;s hourly demand an hour or so after the hour, so &quot;right now&quot;
        is the latest hour it has published. Last week&apos;s line is moved forward seven days so the two days line up.
      </p>
      <PanelFile of={{ panel: `grid_rightnow_${g.slug}`, title: `${g.iso}'s demand in the latest hour EIA has published, the same hour a week earlier and the day's highest hour so far`,
        page: gridHref(g.slug, "mix"), tables: [`${T} (EIA-930's hourly demand, MW; hour starts)`], filter: `${g.entity}: demand_mw`,
        window: `Window: ${today} so far (${g.tz_label}), the hours from ${start} to ${end} (UTC), and the same hour a week earlier`,
        notes: ["The two days' hourly demand (today so far, the same day last week) are drawn in the chart, not written here"] }}
        columns={["Figure", "Hour", "Value", "Unit"]} rows={fileRows} />
      <Cite tables={[T]} note="EIA-930 hourly demand, MW; hour starts" />
    </>
  );
}

// ------------------------------------------------------------------ 2. where the power comes from

function Power({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "eia930_all_generation";
  // session 118: EIA-930's generation for California is the series the faults register calls changed; it is not drawn
  if (g.iso === "CAISO") return <CaisoMixWithheld />;
  const fuelRows = d.gen.filter((r) => r.variable !== "net_generation_mw" && r.variable.startsWith("net_generation_"));
  const totals = d.gen.filter((r) => r.variable === "net_generation_mw");
  if (!fuelRows.length || !totals.length) return <NotYet what={`${g.iso}'s generation by fuel`} where="EIA publishes it in its Hourly Electric Grid Monitor" href={EIA(g)} />;
  const lastT = Math.max(...totals.map((r) => Date.parse(r.ts_utc)));
  const from24 = lastT - 23 * H;
  const x: number[] = [];
  for (let t = from24; t <= lastT; t += H) x.push(t);
  const byT = new Map<string, number>();
  for (const r of fuelRows) byT.set(`${fuelOf(r.variable)}|${Date.parse(r.ts_utc)}`, (byT.get(`${fuelOf(r.variable)}|${Date.parse(r.ts_utc)}`) ?? 0) + r.value);
  const present = FUELS.filter((f) => fuelRows.some((r) => fuelOf(r.variable) === f.key && Date.parse(r.ts_utc) >= from24));
  const layers = present.map((f) => ({ key: f.key, label: f.label, color: `var(--color-fuel-${f.key})`, values: x.map((t) => byT.get(`${f.key}|${t}`) ?? null) }));
  // the last 30 complete UTC days (24 hours of net generation each) to the latest complete one
  const hours = new Map<string, number>();
  for (const r of totals) hours.set(r.ts_utc.slice(0, 10), (hours.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const complete = Array.from(hours.entries()).filter(([, n]) => n === 24).map(([k]) => k).sort();
  const endDay = complete.at(-1);
  const end = endDay ? Date.parse(`${endDay}T00:00:00Z`) + 24 * H : lastT + H;
  const start = end - 30 * 24 * H;
  const inWin = (r: SeriesRow) => Date.parse(r.ts_utc) >= start && Date.parse(r.ts_utc) < end;
  const vars = Array.from(new Set(fuelRows.map((r) => r.variable))).sort();
  const sums = vars.map((v) => ({ v, mwh: fuelRows.filter((r) => r.variable === v && inWin(r)).reduce((a, r) => a + r.value, 0), n: fuelRows.filter((r) => r.variable === v && inWin(r)).length }))
    .filter((s) => s.n > 0).sort((a, b) => b.mwh - a.mwh);
  const total = totals.filter(inWin).reduce((a, r) => a + r.value, 0);
  const s0 = isoTs(start), s1 = isoTs(end);
  return (
    <>
      <div className="mb-1 text-xs text-muted">The last 24 hours EIA has published, by fuel, MW (hour starts, to {local(isoTs(lastT), g.tz)})</div>
      <StackedArea x={x} layers={layers} unit="MW" ariaLabel={`${g.iso} generation by fuel, the last 24 hours`} height={220} />
      <div className="mt-4 text-xs text-muted">
        The mix over 30 UTC days, {s0.slice(0, 10)} to {isoTs(end - 24 * H).slice(0, 10)}: <Num check={`series_sum|${T}|net_generation_mw|${s0}|${s1}|${g.entity}`} raw={total}>{shown(total)}</Num> MWh net
      </div>
      <ShareBar parts={FUELS.map((f) => ({ name: f.label, value: sums.filter((s) => fuelOf(s.v) === f.key).reduce((a, s) => a + s.mwh, 0), color: `var(--color-fuel-${f.key})` }))}
        unit="MWh" ariaLabel={`${g.iso} generation by fuel, 30 days`} file={`erw-${g.slug}-mix-30d`} />
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[360px] text-sm tabular-nums">
          <thead><tr className="border-b border-rule text-left text-xs text-muted"><th className="py-0.5 font-normal">Fuel (as EIA names it)</th><th className="pr-2 text-right font-normal">MWh, 30 days</th><th className="pr-2 text-right font-normal">Hours held</th></tr></thead>
          <tbody>
            {sums.map((s) => (
              <tr key={s.v} className="border-b border-rule">
                <td className="py-0.5 pr-2">{fuelName(s.v)}</td>
                <td className="pr-2 text-right"><Num check={`series_sum|${T}|${s.v}|${s0}|${s1}|${g.entity}`} raw={s.mwh}>{shown(s.mwh)}</Num></td>
                <td className="pr-2 text-right text-muted">{/* session 1166: the hours held, keyed (series_n, session 1154: the distinct hours of the rows) */}
                  <span title={`${T}, ${g.entity}, ${s.v}: the hours it holds from ${s0} to ${s1} (hour starts, UTC)`} className="cursor-help border-b border-dotted border-muted"><Num check={`series_n|${T}|${s.v}|${s0}|${s1}|${g.entity}`} raw={s.n}>{count(s.n)}</Num></span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-xs text-muted">
        Net generation: what the plants produce minus what they use themselves. Storage can be negative: batteries take power in when they charge.
        A fuel with fewer hours than the others is one EIA did not report for every hour.
      </p>
      <Cite tables={[T]} note="EIA-930 hourly net generation by fuel, MW; a day's hourly MW add up to its MWh" />
    </>
  );
}

// ------------------------------------------------------------------ 3. batteries

function Batteries({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "storage_daily_cycle";
  const dis = d.cycle.filter((r) => r.variable === "mwh_discharged").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const last = dis.at(-1);
  const at = (v: string) => (last ? d.cycle.find((r) => r.variable === v && r.ts_utc === last.ts_utc) : undefined);
  const by = (s: string[]) => d.units.filter((u) => s.includes(u.status ?? ""));
  const mw = (us: GridData["units"]) => Math.round(us.reduce((a, u) => a + (u.capacity_mw ?? 0), 0) * 10) / 10;
  const mwh = (us: GridData["units"]) => Math.round(us.filter((u) => u.mwh).reduce((a, u) => a + Number(u.mwh), 0) * 10) / 10;
  const op = by(["operating"]);
  // session 1420: the block's figures, drawn once each and filed
  const ph = at("peak_discharge_hour");
  const phNum = ph ? <Num check={key(T, ph)} raw={ph.value}>{String(ph.value)}</Num> : null;
  const opMw = <Num check={`storage|iso_mw|${g.iso}|operating`} raw={mw(op)}>{shown(mw(op))}</Num>;
  const opMwh = <Num check={`storage|iso_mwh|${g.iso}|operating`} raw={mwh(op)}>{shown(mwh(op))}</Num>;
  const ucMw = <Num check={`storage|iso_mw|${g.iso}|under_construction`} raw={mw(by(["under_construction"]))}>{shown(mw(by(["under_construction"])))}</Num>;
  const plMw = <Num check={`storage|iso_mw|${g.iso}|planned`} raw={mw(by(["planned"]))}>{shown(mw(by(["planned"])))}</Num>;
  const day = last ? `the day ${last.ts_utc.slice(0, 10)}` : "";
  const fileRows: FileCell[][] = [
    ...(last ? [["Discharged", day, <N key="v" t={T} r={last} />, "MWh"], ["Charged", day, <N key="v" t={T} r={at("mwh_charged")} />, "MWh"],
      ...(phNum ? [["The hour of most discharge", day, phNum, "hour starting, local time"]] : [])]
      : d.errors.cycle ? [["The daily battery cycle", "the latest complete day", "could not be read", ""]] : []),
    ...(d.units.length ? [["Operating battery units", "as EIA-860M lists them", opMw, "MW"], ["Operating battery units", "as EIA-860M lists them", opMwh, "MWh"],
      ["Battery units under construction", "as EIA-860M lists them", ucMw, "MW"], ["Planned battery units", "as EIA-860M lists them", plMw, "MW"]]
      : d.errors.units ? [["Battery units", "as EIA-860M lists them", "could not be read", ""]] : []),
  ];
  return (
    <>
      {last ? (
        <div className="mb-3 text-sm">
          <div className="text-xs text-muted">
            The latest complete day, {last.ts_utc.slice(0, 10)}{g.storage_source === "caiso" ? <>: CAISO&apos;s own data<Chip tier="derived" /></> : null}
          </div>
          <div className="flex flex-wrap gap-x-6 tabular-nums">
            <span>Discharged <N t={T} r={last} /> MWh</span>
            <span>Charged <N t={T} r={at("mwh_charged")} /> MWh</span>
            {phNum ? <span>Most discharge at {phNum}:00 local</span> : null}
          </div>
          <div className="mt-1 max-w-sm">
            <InlineSpark values={dis.slice(-30).map((r) => ({ t: r.ts_utc, v: r.value }))} label={`${g.iso} battery MWh discharged per day, last 30 days`} />
          </div>
          <Cite tables={[T]} note={g.storage_source === "caiso" ? "CAISO's rows from its own 5-minute Total batteries series (caiso_battery_storage), averaged to hours, complete Pacific days" : "From EIA-930's hourly battery net generation, complete local days"} />
        </div>
      ) : d.errors.cycle ? (
        // session 1411: the cycle's read failed: said so, never "EIA-930 has no battery series for this grid"
        <div className="mb-3"><Unread what={`${g.iso}'s daily battery cycle`} table={T} reason={d.errors.cycle} /></div>
      ) : (
        <NotYet what={`a daily battery cycle for ${g.iso}: EIA-930 has no battery series for this grid`} where="EIA publishes each grid's hourly generation by fuel" href={EIA(g)} />
      )}
      {d.units.length ? (
        <div className="text-sm tabular-nums">
          <div className="text-xs text-muted">Battery units in {g.iso}&apos;s footprint (EIA-860M, the unit&apos;s balancing authority)</div>
          <div className="flex flex-wrap gap-x-6">
            <span>Operating: {opMw} MW, {opMwh} MWh</span>
            <span>Under construction: {ucMw} MW</span>
            <span>Planned: {plMw} MW</span>
          </div>
          <p className="mt-1 text-xs text-muted">MW is how fast a battery can deliver power; MWh is how much energy it holds. EIA-860M gives MWh for operating units, not planned ones.</p>
          <Cite tables={["storage_capacity"]} note="Sums of the battery units whose balancing authority is this grid" />
        </div>
      ) : d.errors.units ? (
        // session 1411: the units' read failed: said so, never "not in the warehouse yet"
        <Unread what={`Battery units in ${g.iso}'s footprint`} table="storage_capacity" reason={d.errors.units} />
      ) : (
        <NotYet what={`battery units mapped to ${g.iso}`} where="EIA publishes the generator inventory, EIA-860M" href="https://www.eia.gov/electricity/data/eia860m/" />
      )}
      {last || d.units.length ? (
        <PanelFile of={{ panel: `grid_batteries_${g.slug}`, title: `${g.iso}'s battery cycle of the latest complete day and the battery units in its footprint`, page: gridHref(g.slug, "mix"),
          tables: [`${T} (${g.storage_source === "caiso" ? "CAISO's own 5-minute Total batteries series, averaged to hours, complete Pacific days" : "from EIA-930's hourly battery net generation, complete local days"})`,
            `storage_capacity (EIA-860M's battery units whose balancing authority is ${g.iso})`],
          filter: `${g.storage_entity ? `${g.storage_entity}: mwh_discharged, mwh_charged, peak_discharge_hour; ` : ""}storage_capacity: the units of ${g.iso}, summed by status (operating, under_construction, planned)`,
          window: `Window: ${last ? `the latest complete day, ${last.ts_utc.slice(0, 10)}` : "no day of the cycle drawn"}; the units as the live set holds them when the page was drawn`,
          notes: ["The last 30 days' discharge are drawn in the small chart, not written here", "EIA-860M gives MWh for operating units, not planned ones"] }}
          columns={["Figure", "Day", "Value", "Unit"]} rows={fileRows} />
      ) : null}
      <p className="mt-1 text-xs text-muted"><Link href={METHOD_BATTERIES}>Method</Link>.</p>
    </>
  );
}

// ------------------------------------------------------------------ 4. how clean

function Clean({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "carbon_intensity_hourly", TM = "carbon_intensity_monthly";
  const gen = d.ci.filter((r) => r.variable === "intensity_generation").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const last = gen.at(-1);
  // session 1411: the hourly read failed: said so, never "not in the warehouse yet"
  if (!last && d.errors.ci) return <Unread what={`${g.iso}'s carbon intensity, hourly`} table={T} reason={d.errors.ci} />;
  if (!last) return <NotYet what={`${g.iso}'s carbon intensity`} where="EIA publishes hourly CO2 estimates per grid in its Grid Monitor workbooks" href={EIA(g)} />;
  const dem = d.ci.find((r) => r.variable === "intensity_demand" && r.ts_utc === last.ts_utc);
  const lt = Date.parse(last.ts_utc);
  // session 118: a month computed on an impossible hour, and California's months without hydro, are not shown
  const m = d.monthly.filter((r) => !carbonLeftOut(r.entity, r.variable, r.ts_utc)).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const out = carbonLeftOutMonths("intensity_generation", g.entity);
  return (
    <>
      <div className="grid gap-6 lg:grid-cols-[18rem_1fr]">
        <div className="text-sm">
          <div className="text-xs text-muted">The latest hour EIA has estimated ({local(last.ts_utc, g.tz)})</div>
          <div className="text-3xl tabular-nums"><N t={T} r={last} /></div>
          <div className="mb-2 text-xs text-muted">kg of CO2 per MWh generated here</div>
          <div className="tabular-nums"><N t={T} r={dem} /> <span className="text-xs text-muted">kg CO2 per MWh used here (imports counted)</span></div>
        </div>
        <div className="min-w-0">
          <LineChart lines={[{ label: "Of generation", color: "accent", points: gen.filter((r) => Date.parse(r.ts_utc) > lt - 24 * H).map((r) => ({ t: Date.parse(r.ts_utc) / 1000, v: r.value })) }]}
            unit="kg CO2/MWh" height={180} ariaLabel={`${g.iso} carbon intensity, the last 24 hours`} />
        </div>
      </div>
      <Cite tables={[T]} note="EIA's hourly CO2 estimates over EIA's net generation and demand, the latest 24 hours" />
      {m.length ? (
        <div className="mt-3">
          <div className="text-xs text-muted">
            Monthly since 2018: <Num check={key(TM, m[0])} raw={m[0].value}>{shown(m[0].value)}</Num> in {m[0].ts_utc.slice(0, 7)},{" "}
            <Num check={key(TM, m.at(-1)!)} raw={m.at(-1)!.value}>{shown(m.at(-1)!.value)}</Num> in {m.at(-1)!.ts_utc.slice(0, 7)} (kg CO2 per MWh generated; months with a missing day are left out)
          </div>
          <LineChart lines={[{ label: "Of generation, monthly", color: "ink", points: m.map((r) => ({ t: Date.parse(r.ts_utc) / 1000, v: r.value })) }]} x="month" unit="kg CO2/MWh" height={180} ariaLabel={`${g.iso} carbon intensity by month since 2018`} />
          {out.length ? (
            <p className="mt-1 text-xs text-muted" data-carbon-left-out={out.length}>
              Left out of this line, though the table still holds them: {monthRuns(out.map((x) => x.month))}. Each rests on hours that did
              not happen or, in California from October 2019 to July 2020, on a file with no hydro in it:{" "}
              <Link href="/data/faults">known data faults</Link>.
            </p>
          ) : null}
          <Cite tables={[TM]} />
        </div>
      ) : d.errors.monthly ? (
        // session 1411: the monthly read failed: said so (the block drew nothing in its place)
        <div className="mt-3"><Unread what="Monthly since 2018" table={TM} reason={d.errors.monthly} /></div>
      ) : null}
      <p className="mt-1 text-xs text-muted">Carbon intensity is the CO2 released per MWh of electricity: lower is cleaner. <Link href="/data/methods/emissions">Method</Link>.</p>
    </>
  );
}

// ------------------------------------------------------------------ 5. what it costs

function Cost({ g, d }: { g: GridConfig; d: GridData }) {
  const T = "price_board_latest", TP = "price_board_peak_offpeak";
  if (!g.prices_public) return <NotYet what={`${g.iso}'s prices: ${(g.prices_note ?? "not public here").replace(/[.]$/, "")}`} where={`${g.iso} publishes them`} href={g.prices_url ?? "https://www.eia.gov/electricity/wholesale/"} />;
  // session 1167: a held grid's prices read "license needed" (the read is refused by lib/supabase.ts; until now the block said "not in the warehouse yet")
  if (g.hub && licenseHeldRow(T, g.hub.entity)) return <HeldLine what={`${g.iso}'s hub prices`} held={{ words: LICENSE_NEEDED, why: licenseTitle(T) }} />;
  // session 1411: the price board's read failed: said so, never "not in the warehouse yet"
  if (g.hub && !d.prices.length && d.errors.prices) return <Unread what={`${g.iso}'s hub prices`} table={T} reason={d.errors.prices} />;
  if (!g.hub || !d.prices.length) return <NotYet what={`${g.iso}'s hub prices`} where="EIA summarizes wholesale prices" href="https://www.eia.gov/electricity/wholesale/" />;
  const daMean = latestOf(d.prices, "da_latest_day_mean"), rtMean = latestOf(d.prices, "rt_latest_day_mean"), avg30 = latestOf(d.prices, "da_avg_30d");
  const daily = d.prices.filter((r) => r.variable === "da_daily_mean").sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const pk = latestOf(d.peak, "da_peak_mean");
  const off = pk ? d.peak.find((r) => r.variable === "da_offpeak_mean" && r.ts_utc === pk.ts_utc) : undefined;
  // session 1411: the peak and off-peak cells when price_board_peak_offpeak's read failed: "could not be read", never "none"
  const peakN = (r?: SeriesRow) => (d.errors.peak && !r ? <Missing words="could not be read" why={`${TP} could not be read just now: ${d.errors.peak}`} /> : <N t={TP} r={r} />);
  // session 1420: the block's five figures, as it draws them, to download
  const dayOfRow = (r?: SeriesRow) => (r ? `the day ${r.ts_utc.slice(0, 10)}` : "");
  const fileRows: FileCell[][] = [
    ["Day-ahead, the day's mean", dayOfRow(daMean), <N key="v" t={T} r={daMean} />, "USD per MWh"],
    ["Real-time, the day's mean", dayOfRow(rtMean), <N key="v" t={T} r={rtMean} />, "USD per MWh"],
    ["Day-ahead peak hours, mean", dayOfRow(pk), peakN(pk), "USD per MWh"],
    ["Day-ahead off-peak hours, mean", dayOfRow(pk), peakN(off), "USD per MWh"],
    ["Day-ahead daily mean, 30-day average", dayOfRow(avg30), <N key="v" t={T} r={avg30} />, "USD per MWh"],
  ];
  return (
    <>
      <div className="text-xs text-muted">{g.hub.label}, USD per MWh</div>
      <div className="mt-1 grid grid-cols-2 gap-px border border-rule bg-rule text-sm tabular-nums sm:grid-cols-4">
        <div className="bg-panel p-2"><div className="text-xs text-muted">Day-ahead, {daMean?.ts_utc.slice(0, 10)}</div><div className="text-xl"><N t={T} r={daMean} /></div></div>
        <div className="bg-panel p-2"><div className="text-xs text-muted">Real-time, {rtMean?.ts_utc.slice(0, 10)}</div><div className="text-xl"><N t={T} r={rtMean} /></div></div>
        <div className="bg-panel p-2"><div className="text-xs text-muted">Day-ahead peak, {pk?.ts_utc.slice(0, 10)}</div><div className="text-xl">{peakN(pk)}</div></div>
        <div className="bg-panel p-2"><div className="text-xs text-muted">Day-ahead off-peak, same day</div><div className="text-xl">{peakN(off)}</div></div>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
        <span className="text-xs text-muted">Day-ahead daily mean, 30 days (average <N t={T} r={avg30} />)</span>
        <span className="w-48"><InlineSpark values={daily.map((r) => ({ t: r.ts_utc, v: r.value }))} label={`${g.iso} day-ahead daily mean price, 30 days`} /></span>
      </div>
      <p className="mt-1 text-xs text-muted">
        Wholesale prices, what power plants are paid, not what a household pays. Day-ahead is the price agreed the day before; real-time is the price at
        the moment. Peak hours are the busy daytime hours of working days, as the price board&apos;s method defines them; off-peak is the rest. <Link href={METHOD_COST}>Method</Link>.
      </p>
      {daMean || rtMean || avg30 || pk || off ? <PanelFile of={{ panel: `grid_cost_${g.slug}`, title: `${g.hub.label}'s day-ahead and real-time daily means, its peak and off-peak means and the 30-day average, USD per MWh`, page: gridHref(g.slug, "mix"),
        tables: [`${T} (daily means of ${g.iso}'s own hourly prices)`, `${TP} (the day-ahead mean over peak and off-peak hours, as the price board's method defines them)`],
        filter: `${g.hub.entity}: da_latest_day_mean, rt_latest_day_mean, da_avg_30d; da_peak_mean, da_offpeak_mean`,
        window: "Window: the latest day each table holds, and the 30 days to it for the average",
        notes: ["The 30 days of day-ahead daily means (da_daily_mean) are drawn in the small chart, not written here"] }}
        columns={["Figure", "Day", "Value", "Unit"]} rows={fileRows} /> : null}
      <Cite tables={[T, TP]} note="Daily means of the ISO's own hourly prices" />
    </>
  );
}

// ------------------------------------------------------------------ 6. what is being built

function Building({ g, d }: { g: GridConfig; d: GridData }) {
  const states = Object.keys(g.states).sort();
  const dcMw = Math.round(d.dcs.reduce((a, x) => a + (x.capacity_mw ?? 0), 0) * 10) / 10;
  const dcN = d.dcs.length;
  // session 1420: the datacenters' two figures, drawn once each and filed; the queue's rows, drawn and filed
  const dcNum = <Num check={`griddc|${g.slug}|n`} raw={dcN}>{count(dcN)}</Num>;
  const dcMwNum = <Num check={`griddc|${g.slug}|mw`} raw={dcMw}>{shown(dcMw)}</Num>;
  let qRows: { key: string; cells: React.ReactNode[] }[] = [];
  let queue: React.ReactNode;
  if (!g.queue_table) {
    queue = <NotYet what={`${g.iso}'s interconnection queue`} where={`${g.iso} publishes it`} href={g.queue_url ?? "https://www.eia.gov/electricity/data/eia860m/"} />;
  } else if (heldQueue(g.queue_table)) {
    // session 1167: a held grid's queue positions are left out of the read (lib/grid.ts) and read "license needed" here
    queue = <HeldLine what={`${g.iso}'s interconnection queue`} held={heldQueue(g.queue_table)!} />;
  } else if (d.errors.queue) {
    // session 1181: the queue's read failed: said so in the tool's one look, never "not in the warehouse yet"
    queue = <p className="text-sm text-muted" role="status" data-grid-queue-unread={g.queue_table}>{g.iso}&apos;s interconnection queue: <Missing words="could not be read" why={`energy_projects (${g.queue_table}) could not be read just now: ${d.errors.queue}`} /></p>;
  } else if (!d.queue.length) {
    queue = <NotYet what={`${g.iso}'s interconnection queue in the live set`} where={`${g.iso} publishes it`} href="https://www.eia.gov/electricity/data/eia860m/" />;
  } else {
    const techs = Array.from(new Set(d.queue.map((q) => q.tech ?? "unknown")));
    const rows = techs.map((t) => {
      const a = d.queue.filter((q) => (q.tech ?? "unknown") === t && q.status === "active");
      return { t, n: a.length, mw: Math.round(a.reduce((s, q) => s + (q.capacity_mw ?? 0), 0) * 10) / 10, done: d.queue.filter((q) => (q.tech ?? "unknown") === t && q.status === "completed").length };
    }).filter((r) => r.n || r.done).sort((a, b) => b.mw - a.mw);
    const k = (s: string, t: string, what: string) => `gridq|${g.queue_table}|${s}|${t}|${what}`;
    qRows = rows.map((r) => ({ key: r.t, cells: [r.t.replace(/_/g, " "), <Num key="n" check={k("active", r.t, "n")} raw={r.n}>{count(r.n)}</Num>,
      <Num key="mw" check={k("active", r.t, "mw")} raw={r.mw}>{shown(r.mw)}</Num>, <Num key="done" check={k("completed", r.t, "n")} raw={r.done}>{count(r.done)}</Num>] }));
    queue = (
      <>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[420px] text-sm tabular-nums">
            <thead><tr className="border-b border-rule text-left text-xs text-muted"><th className="py-0.5 font-normal">Kind of project</th><th className="pr-2 text-right font-normal">Waiting (active)</th><th className="pr-2 text-right font-normal">Active MW</th><th className="pr-2 text-right font-normal">Completed</th></tr></thead>
            <tbody>
              {qRows.map((r) => (
                <tr key={r.key} className="border-b border-rule">
                  <td className="py-0.5 pr-2">{r.cells[0]}</td>
                  <td className="pr-2 text-right">{r.cells[1]}</td>
                  <td className="pr-2 text-right">{r.cells[2]}</td>
                  <td className="pr-2 text-right">{r.cells[3]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-1 text-xs text-muted">
          The interconnection queue is the waiting list of projects asking to connect to the grid; many never get built. Withdrawn projects are left out.
          Kinds are the ERW&apos;s grouping of the ISO&apos;s own fuel names. <Link href={METHOD_BUILDING_QUEUE}>Method</Link>.
        </p>
        <Cite tables={["energy_projects", g.queue_table]} note={`Queue positions of ${g.queue_table}, as energy_projects groups them`} />
      </>
    );
  }
  return (
    <>
      {queue}
      <div className="mt-4 text-sm">
        <div className="text-xs text-muted">Datacenter facilities mapped to {g.iso}<Chip tier="model_extracted" /></div>
        <div className="tabular-nums">
          {dcNum} facilities; {dcMwNum} MW where a source states it.{" "}
          <Link href="/datacenters" className="underline">All datacenters</Link>.
        </div>
        <p className="mt-1 text-xs text-muted">
          A facility from {g.iso}&apos;s interconnection queue, or whose utility is one of {g.iso}&apos;s, is counted here; any other is counted by its
          state, for the states wholly or mostly inside {g.iso} ({states.map((s) => g.states[s]).join(", ")}), so one there may be served by a
          neighboring grid. Many rows come from news stories read by a model: check each against its source.{" "}
          <Link href={METHOD_BUILDING_DATACENTERS}>Method</Link>.
        </p>
        <Cite tables={["datacenter_facilities"]} />
      </div>
      {/* session 1420: the queue's table and the datacenters' figures, to download, wherever the block draws a figure (the
          datacenters' are held whole today, so they are written "license needed"; a held queue is not drawn and not filed) */}
      {qRows.length || !heldBy(`griddc|${g.slug}|n`) ? (
        <PanelFile of={{ panel: `grid_building_${g.slug}`, title: `${g.iso}'s interconnection queue by kind of project, and the datacenter facilities mapped to it`, page: gridHref(g.slug, "mix"),
          tables: [...(qRows.length ? [`energy_projects (${g.queue_table}'s queue positions, as energy_projects groups them; withdrawn positions are left out)`] : []),
            "datacenter_facilities (facilities mapped to the grid; many rows come from news stories read by a model)"],
          filter: `${qRows.length ? `energy_projects: entity_id like ${(g.queue_table ?? "").replace(/_interconnection_queue$/, "_queue")}:*, status active and completed, by kind (technology_group); ` : ""}datacenter_facilities: the facilities from ${g.iso}'s queue or of its utilities, else of the states ${states.map((s) => g.states[s]).join(", ")}`,
          window: "Window: the live set as read when the page was drawn",
          notes: qRows.length ? [] : ["The queue's table is not drawn for this grid: the page says why"],
          figures: [{ label: `Datacenter facilities mapped to ${g.iso}`, value: dcNum }, { label: "Their MW, where a source states it", value: dcMwNum }] }}
          columns={["Kind of project", "Waiting (active)", "Active MW", "Completed"]} rows={qRows.map((r) => r.cells)} />
      ) : null}
    </>
  );
}

// ------------------------------------------------------------------ 7. in the news

function News({ g, d }: { g: GridConfig; d: GridData }) {
  const n = d.news.length;
  return (
    <>
      <div className="mb-2 text-sm">
        <Num check={`gridnews|${g.slug}|${d.newsSince}|n`} raw={n}>{count(n)}</Num> scored stories since {d.newsSince.slice(0, 10)} whose headline names{" "}
        {g.names.join(" or ")}{Object.keys(g.states).length ? ` or whose region is ${Object.values(g.states).join(", ")}` : ""}.
      </div>
      {n ? (
        <ul className="space-y-1 text-sm">
          {d.news.slice(0, 12).map((r) => (
            <li key={r.event_id}>
              <a href={r.source_url}>{r.extra?.headline || "(no headline)"}</a>{" "}
              <span className="text-xs text-muted">{r.source}, {r.event_date.slice(0, 10)}; significance {r.extra?.significance ?? ""}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted">No story in the last 14 days matched. <Link href="/digest">The Energy Digest</Link> has every day&apos;s news.</p>
      )}
      <p className="mt-1 text-xs text-muted">Headlines and scores are written by a model reading each story; the link goes to the outlet.</p>
      <Cite tables={["news_index"]} />
    </>
  );
}

// ------------------------------------------------------------------ the page

function Written({ md, slug }: { md: string; slug: string }) {
  return <div className="prose-erw max-w-3xl text-sm" dangerouslySetInnerHTML={{ __html: render(md, `docs/grids/${slug}.md`) }} />;
}

/** Session 237: a grid page's blocks that the Now view draws under its sentence and numbers, in the page's own order. */
export function GridNowParts({ g, d }: { g: GridConfig; d: GridData }) {
  const md = DOCS.grids[g.slug] ?? "";
  const parts = md.split(/\n(?=## )/).slice(1); // the five sections
  const first = parts[0] ?? "", rest = parts.slice(1).join("\n");
  return (
    <div data-grid-parts="now">
      {g.slug === "ercot" ? <AskErcotLink context={{ view: "/grid/ercot", title: "Your grid: ERCOT", settings: { grid: "ERCOT" } }} /> : null}
      {g.iso === "CAISO" ? <CaisoBreakNote kind="carbon" /> : null}
      <p className="mb-4 max-w-3xl text-sm text-muted">
        Who runs this grid, where its power comes from, what it costs, how clean it is, what is being built and what makes it different. Numbers come
        from the warehouse&apos;s tables, each with its source; the text is written for this page and cites its sources. Times are {g.tz_label} unless marked UTC.
        {" "}How it trades power with its neighbors: <Link href={gridHref(g.slug, "gravity")}>the exchange</Link> and <Link href={gridHref(g.slug, "network")}>the grid network</Link>.
      </p>

      {/* session 1420: the older blocks of figures are named panels, each with its file (Reliability names its own) */}
      {/* session 1421: each block's anchor on its own Section (lib/gridAnchors.ts OLDER_ANCHOR), inside its panel's element */}
      <div data-grid-panel={`grid_rightnow_${g.slug}`}><Section title="Right now: demand" id={OLDER_ANCHOR.rightNow} aside={<Chip tier="source" />}><RightNow g={g} d={d} />
        <p className="mt-1 text-xs text-muted" data-grid-method="right-now"><Link href={METHOD_RIGHT_NOW}>Method: &quot;Right now&quot; and the mix in that hour</Link>.</p>
      </Section></div>
      <Section title="Who runs this grid" aside={<Chip tier="written" />}>
        <Written md={first.replace(/^## [^\n]*\n/, "")} slug={g.slug} />
      </Section>
      <div data-grid-panel={`grid_batteries_${g.slug}`}><Section title="Batteries" id={OLDER_ANCHOR.batteries} aside={<><Chip tier="derived" /></>}><Batteries g={g} d={d} /></Section></div>
      <div data-grid-panel={`grid_cost_${g.slug}`}>
      <Section title="What it costs" id={OLDER_ANCHOR.cost} aside={<Chip tier="derived" />}>
        <Cost g={g} d={d} />
        {/* session 37: the cost-of-power model (PJM's prices are internal, so it has no PJM row) */}
        <p className="mt-2 text-sm">
          {g.slug === "pjm" ? "PJM's prices are internal, so the " : "What a large load pays for energy here, load-weighted by month and by hour of day: the "}
          <Link href="/cost-of-power">cost of power</Link>{g.slug === "pjm" ? " model has no PJM row." : "."}
        </p>
      </Section>
      </div>
      {/* session 58: California reliability v1, CAISO only */}
      {g.slug === "caiso" ? <Section id="reliability" title="Reliability" aside={<Chip tier="derived" />}><Reliability /></Section> : null}
      <div data-grid-panel={`grid_building_${g.slug}`}><Section title="What is being built" id={OLDER_ANCHOR.building} aside={<Chip tier="derived" />}><Building g={g} d={d} /></Section></div>
      <Section title="In the news" aside={<Chip tier="model_extracted" />}><News g={g} d={d} /></Section>

      <Section title={`About ${g.iso}`} aside={<Chip tier="written" />}>
        <Written md={rest} slug={g.slug} />
      </Section>
      {Object.keys(d.errors).length ? (
        <p className="text-xs text-muted">Reads that failed: {Object.entries(d.errors).map(([k, v]) => `${k}: ${v}`).join("; ")}</p>
      ) : null}
    </div>
  );
}

/** Session 237: a grid page's "Where the power comes from", drawn by the Mix view. */
export function GridMixParts({ g, d }: { g: GridConfig; d: GridData }) {
  return <Section title="Where the power comes from" aside={<Chip tier="source" />}><Power g={g} d={d} /></Section>;
}

/** Session 237: a grid page's "How clean", drawn by the Clean view. */
export function GridCleanParts({ g, d }: { g: GridConfig; d: GridData }) {
  return (
    <>
      {g.iso === "CAISO" ? <CaisoBreakNote kind="carbon" /> : null}
      <Section title="How clean" aside={<Chip tier="derived" />}><Clean g={g} d={d} /></Section>
    </>
  );
}
