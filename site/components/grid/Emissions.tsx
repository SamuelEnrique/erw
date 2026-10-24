import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { daysAgo, series, type SeriesRow } from "@/lib/data";
import { shown, utc } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";
import { CaisoBreakNote } from "@/components/CaisoBreakNote";  // session 73

// Session 32 (Part B): carbon intensity per ISO, two blocks only: the latest hour per ISO, ranked, and the last 24
// hours as one chart. Every number is a value of carbon_intensity_hourly (derived from EIA's CO2 estimates,
// eia930_all_emissions, over EIA-930 generation and demand); the page computes nothing.
// Session 34: one more block, the monthly intensity since 2018-07 per ISO (carbon_intensity_monthly). Since session 34
// the denominators are the workbooks' own Demand and Net generation, so every table reaches back to 2018.
// Session 237: this file was app/emissions/page.tsx. /emissions redirects to the Clean view of the Grid tool (/grid,
// next.config.ts), which draws these three blocks as they were, the grid in view marked in the ranking.
import { lastDayFigures, type Fig } from "@/lib/gridKeys";  // session 1151
import { scrollRegion } from "@/lib/cells";  // session 1159: the last 24 hours' table scrolls in a frame a keyboard reaches, as ToolTable's
import { carbonLeftOut, carbonLeftOutMonths, monthRuns, CARBON_HYDRO_GAP } from "@/lib/carbonLeftOut";  // session 118
import { PanelFile } from "@/components/grid/PanelFile";  // session 1182: the last 24 hours' table, to download
import { gridHref } from "@/lib/gridtool";
import { GRID_ANCHOR, METHOD_CLEAN24 } from "@/lib/gridAnchors";  // session 1183: each panel's anchor; session 1184: its method
import { PanelMethod } from "@/components/grid/PanelMethod";  // session 1184: the line that links the panel's method
// Session 1415 (chain 107): the ranked table and the monthly since 2018 are named panels (grid_carbonrank_<grid>,
// grid_carbonmonth_<grid>), each with its anchor (EMISSIONS_ANCHOR), its file and its method (METHOD_EMISSIONS_BLOCKS,
// docs/methods/emissions.md); every figure keyed with its source on hover, the two figures of the monthly chart's note
// too (the months left out, the hours without hydro: keys on the committed site/data/carbon_left_out.json); a held ISO's
// place in the three blocks reads "license needed" (lib/gridHeld.ts heldCarbonRow; none is held today). The two charts
// answer a hover through TimeChart's own card: the hour (minute axis) or the month (x="month"), each ISO's value in
// kg CO2/MWh.
import { carbonMonthEnds, carbonRanked, carbonTip, type MonthEnds } from "@/lib/gridKeys";
import { heldCarbonRow } from "@/lib/gridHeld";
import { EMISSIONS_ANCHOR, METHOD_EMISSIONS_BLOCKS } from "@/lib/gridAnchors";
import { CARBON_LEFT_OUT_BUILT, CARBON_LEFT_OUT_FILE, CARBON_LEFT_OUT_NAME } from "@/lib/carbonLeftOut";
import { filecalcKey, leftOutCount } from "@/lib/mixViewCalc";

const T = "carbon_intensity_hourly";
const TM = "carbon_intensity_monthly"; // session 34
const METHOD = "/data/methods/emissions";
// session 118: EIA's CO2 estimates often run more than three days behind the clock. With a three-day window the two
// "now" sections said "no row in the last 3 days" while the table held hours four days old; the page looks back a week
const LOOK_BACK_DAYS = 7;
const ISOS = [
  { entity: "eia930:CISO", label: "CAISO", color: "var(--color-fuel-solar)" },
  { entity: "eia930:ERCO", label: "ERCOT", color: "accent" },
  { entity: "eia930:ISNE", label: "ISO-NE", color: "var(--color-fuel-gas)" },
  { entity: "eia930:MISO", label: "MISO", color: "var(--color-fuel-hydro)" },
  { entity: "eia930:NYIS", label: "NYISO", color: "var(--color-fuel-storage)" },
  { entity: "eia930:PJM", label: "PJM", color: "ink" },
  { entity: "eia930:SWPP", label: "SPP", color: "var(--color-fuel-coal)" },
];

function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 border border-rule px-1 text-xs text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}

const N = (r?: SeriesRow) =>
  r ? <Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;

// session 1415: a figure's look when it carries its source on hover (as the last 24 hours' F)
const TIP = "cursor-help border-b border-dotted border-muted";
/** Session 1415: the ranked table's figure, N with its one-line source on hover (lib/gridKeys.ts carbonTip). */
const NT = (r: SeriesRow | undefined, what: string) => (r ? <span title={carbonTip(T, r, what)} className={TIP}>{N(r)}</span> : N(r));
/** Session 1415: a held ISO's place in a carbon block: the words, the publishers on hover (the tool's one look, session
 *  1159; PanelFile writes it "license needed"). */
function HeldPlace({ table, entity }: { table: string; entity: string }) {
  const h = heldCarbonRow(table, entity);
  return h ? <span data-license-held={table} className="text-muted" title={h.why}>{h.words}</span> : null;
}
const isHeld = (table: string) => (entity: string) => !!heldCarbonRow(table, entity);

function Monthly({ rows, grid }: { rows: SeriesRow[]; grid?: string }) {
  // session 118: a month computed on an impossible hour, and California's months without hydro, are not shown
  // (lib/carbonLeftOut.ts): the table behind this page is held as it is until a person approves the rebuilt one
  // session 1415: the rows chosen as they were here (lib/gridKeys.ts carbonMonthEnds), a held ISO set apart
  const ends = carbonMonthEnds(rows, ISOS.map((i) => i.entity), (r) => !carbonLeftOut(r.entity, r.variable, r.ts_utc), isHeld(TM));
  const out = carbonLeftOutMonths("intensity_generation");
  const lines: Line[] = ISOS.flatMap((i, k) => (ends[k].held ? [] : [{ label: i.label, color: i.color, points: ends[k].rows.map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value })) }]));
  const figs = monthFigs(ends);
  const { leftOut, hydro } = leftOutFigs();
  return (
    <>
      <LineChart lines={lines} unit="kg CO2/MWh" height={280} x="month" ariaLabel="Carbon intensity of generation per ISO, monthly since 2018" />  {/* session 416: x="month", so the axis reads 2018-07 to 2026-09, not 08-01 to 09-01 */}
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm tabular-nums">
        {ISOS.map((i, k) => {
          const { first, last, held } = ends[k];
          const f = figs[k];
          if (held) return <span key={i.entity} data-carbon-held={i.entity}>{i.label}: <HeldPlace table={TM} entity={i.entity} /></span>;
          return last && first && f ? (
            <span key={i.entity}>
              {i.label}: {f.first}{" "}
              <span className="text-xs text-muted">({first.ts_utc.slice(0, 7)})</span> to{" "}
              {f.last}{" "}
              <span className="text-xs text-muted">({last.ts_utc.slice(0, 7)})</span>
            </span>
          ) : null;
        })}
      </div>
      <p className="mt-1 text-xs text-muted">
        Intensity of generation, kg CO2/MWh: each month&apos;s CO2 over its net generation, for UTC months whose every day is
        complete; a month with a missing day is left out, so a line can have gaps. The first and the latest complete month
        per ISO are given in figures.
      </p>
      {out.length ? (
        <p className="mt-2 max-w-3xl border-l-2 border-accent bg-paper px-3 py-1.5 text-xs" data-carbon-left-out={out.length}>
          <strong>Left out of this chart: <F f={leftOut} /> months the table still holds.</strong>{" "}
          {ISOS.filter((i) => out.some((m) => m.entity === i.entity)).map((i, k, a) => (
            <span key={i.entity}>
              {i.label}: {monthRuns(out.filter((m) => m.entity === i.entity).map((m) => m.month))}
              {k < a.length - 1 ? "; " : ". "}
            </span>
          ))}
          California&apos;s months from October 2019 to July 2020 are computed on a file with no hydro in it (<F f={hydro} /> hours
          in a row, so the intensity reads high); the others hold an hour of net generation that did not happen, and
          a month&apos;s CO2 over such an hour is not that month&apos;s intensity. Nothing is corrected or filled: the months are not drawn. <Link href="/data/faults">Known data faults</Link>;{" "}
          <Link href="/data/methods/impossible_hours">the rule</Link>.
        </p>
      ) : null}
      {/* session 1415: the block's figures as a file, each ISO's first and latest month, and the note's two figures in its header */}
      <PanelFile of={{ panel: `grid_carbonmonth_${grid ?? "all"}`, title: "each ISO's first and latest complete month of carbon intensity of generation, since 2018", page: gridHref(grid ?? "us48", "clean"),
        tables: [`${TM} (derived from eia930_all_emissions, EIA's CO2 estimates, over the Demand and Net generation columns of the same EIA workbooks), kg CO2 per MWh`,
          `site/data/${CARBON_LEFT_OUT_NAME} (warehouse/derived/carbon_left_out.py, session 118: the months the chart leaves out)`],
        filter: "the seven ISOs' balancing authorities (eia930:CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP), variable intensity_generation, the months left out not counted",
        window: "Window: every UTC month the table holds whose every day is complete, from 2018-07, when EIA's CO2 estimates start",
        notes: ["Each month's value is drawn in the chart (and in its table, Chart | Table), not written here"],
        figures: out.length ? [{ label: "Months left out of the chart, intensity of generation", value: { check: leftOut.check, raw: leftOut.raw } },
          { label: "California's hours in a row without hydro", value: { check: hydro.check, raw: hydro.raw } }] : undefined }}
        columns={["ISO", "First complete month", "First, kg CO2/MWh", "Latest complete month", "Latest, kg CO2/MWh"]}
        rows={ISOS.map((i, k) => {
          const e = ends[k], f = figs[k];
          if (e.held) { const h = <HeldPlace table={TM} entity={i.entity} />; return [i.label, h, h, h, h]; }
          return e.first && e.last && f ? [i.label, e.first.ts_utc.slice(0, 7), f.first, e.last.ts_utc.slice(0, 7), f.last] : [i.label, "not held", "not held", "not held", "not held"];
        })} />
    </>
  );
}

/** Session 1415: each ISO's first and latest month, keyed as they were (series|carbon_intensity_monthly|...), each with
 *  its source on hover; null for an ISO held or with no month kept. */
function monthFigs(ends: MonthEnds<SeriesRow>[]) {
  return ends.map(({ first, last }) => (first && last ? {
    first: <span title={carbonTip(TM, first, "the first complete month")} className={TIP}><Num check={`series|${TM}|${first.entity}|${first.variable}|${first.ts_utc}`} raw={first.value}>{shown(first.value)}</Num></span>,
    last: <span title={carbonTip(TM, last, "the latest complete month")} className={TIP}><Num check={`series|${TM}|${last.entity}|${last.variable}|${last.ts_utc}`} raw={last.value}>{shown(last.value)}</Num></span>,
  } : null));
}

/** Session 1415: the two figures of the monthly chart's note, keyed on the committed site/data/carbon_left_out.json: the
 *  months left out of intensity_generation (filecalc|carbon_left_out_n, lib/mixViewCalc.ts leftOutCount, which is
 *  carbonLeftOutMonths' length) and California's hours without hydro (file|...|hydro_gap.hours). */
function leftOutFigs(): { leftOut: Fig; hydro: Fig } {
  return {
    leftOut: { check: `fmt|n0|${filecalcKey("carbon_left_out_n", CARBON_LEFT_OUT_NAME, ["intensity_generation"])}`, raw: leftOutCount(CARBON_LEFT_OUT_FILE, "intensity_generation"),
      tip: `site/data/${CARBON_LEFT_OUT_NAME} (warehouse/derived/carbon_left_out.py, built ${CARBON_LEFT_OUT_BUILT}): the months of ${TM}, intensity_generation, the chart leaves out (lib/mixViewCalc.ts leftOutCount)` },
    hydro: { check: `fmt|n0|file|${CARBON_LEFT_OUT_NAME}|hydro_gap.hours`, raw: CARBON_HYDRO_GAP.hours,
      tip: `site/data/${CARBON_LEFT_OUT_NAME}: hydro_gap.hours, California's hours from ${CARBON_HYDRO_GAP.first_hour} to ${CARBON_HYDRO_GAP.last_hour} computed on a file with no hydro` },
  };
}

// Session 1151 (chain 077): a figure of "The last 24 hours" with its one-line source as the hover tip
function F({ f }: { f: Fig }) {
  return <span title={f.tip} className="cursor-help border-b border-dotted border-muted"><Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num></span>;
}

export async function EmissionsParts({ focus = null, grid }: { focus?: string | null; /** session 1151: the Grid tool's grid in view, which names the keyed panel under the chart */ grid?: string }) {
  const [got, monthly] = await Promise.all([
    attempt(() => series(T, { since: daysAgo(LOOK_BACK_DAYS) })),
    attempt(() => series(TM, { variable: "intensity_generation" })),
  ]);
  const rows = got.ok ? got.data : [];
  const of = (e: string, v: string) => rows.filter((r) => r.entity === e && r.variable === v).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  // session 1415: the rows ranked as they were here, moved to lib/gridKeys.ts carbonRanked; a held ISO set apart, never
  // ranked; and the ISOs the last 24 hours draw (a held one's place reads "license needed")
  const rank = carbonRanked(rows, ISOS.map((i) => i.entity), isHeld(T));
  const latest = rank.ranked.map((x) => ({ ...ISOS.find((i) => i.entity === x.entity)!, g: x.g, d: x.d }));
  const heldRank = ISOS.filter((i) => rank.held.includes(i.entity));
  const open = ISOS.filter((i) => !isHeld(T)(i.entity));
  const held24 = ISOS.filter((i) => isHeld(T)(i.entity));
  const newest = rows.length ? Math.max(...rows.map((r) => new Date(r.ts_utc).getTime())) : 0;
  const lines: Line[] = open.map((i) => ({
    label: i.label,
    color: i.color,
    points: of(i.entity, "intensity_generation")
      .filter((r) => new Date(r.ts_utc).getTime() > newest - 24 * 3_600_000)
      .map((r) => ({ t: new Date(r.ts_utc).getTime() / 1000, v: r.value })),
  }));
  return (
    <>
      <CaisoBreakNote />
      <p className="mb-5 max-w-3xl text-sm text-muted">
        How much CO2 each ISO&apos;s power carries, from EIA&apos;s hourly CO2 estimates for EIA-930. <Link href={METHOD}>Method</Link>.
      </p>

      <Section title="Carbon intensity now, ranked" aside={<Tier />}>
        {/* session 1415: a named panel with its anchor, its file and its method, its place kept on a failed read */}
        <div id={EMISSIONS_ANCHOR.rank} data-grid-panel={`grid_carbonrank_${grid ?? "all"}`}>
        {!got.ok ? (
          <NoData what="carbon intensity" reason={got.reason} />
        ) : latest.length === 0 && heldRank.length === 0 ? (
          <NoData what="carbon intensity" reason={`${T} has no row in the last ${LOOK_BACK_DAYS} days`} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[460px] text-sm tabular-nums">
              <thead>
                <tr className="border-b border-rule text-left text-xs text-muted">
                  <th className="py-0.5 font-normal">ISO, lowest first</th>
                  <th className="pr-2 font-normal">Latest hour (start, UTC)</th>
                  <th className="pr-2 text-right font-normal">Of generation, kg CO2/MWh</th>
                  <th className="pr-2 text-right font-normal">Of demand, kg CO2/MWh</th>
                </tr>
              </thead>
              <tbody>
                {latest.map((x, i) => (
                  <tr key={x.entity} className={`border-b border-rule ${x.entity === focus ? "bg-paper font-semibold" : ""}`} data-focus={x.entity === focus ? "1" : undefined}>
                    <td className="py-0.5 pr-2">
                      <span className="text-muted">{i + 1}.</span> {x.label}
                    </td>
                    <td className="pr-2 text-xs text-muted">{utc(x.g!.ts_utc)}</td>
                    <td className="pr-2 text-right font-semibold">{NT(x.g, "the latest hour")}</td>
                    <td className="pr-2 text-right">{NT(x.d, "the same hour")}</td>
                  </tr>
                ))}
                {heldRank.map((x) => (
                  <tr key={x.entity} className="border-b border-rule" data-carbon-held={x.entity}>
                    <td className="py-0.5 pr-2">{x.label}</td>
                    <td className="pr-2 text-xs text-muted">not ranked</td>
                    <td className="pr-2 text-right"><HeldPlace table={T} entity={x.entity} /></td>
                    <td className="pr-2 text-right"><HeldPlace table={T} entity={x.entity} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-1 text-xs text-muted">
              Of generation: the CO2 EIA estimates for the power made in the ISO, over its net generation. Of demand: the CO2 of
              the power used there, imports counted and exports taken out, over its demand; the two differ by trade. EIA
              publishes generation a day or more late, so the latest hour is not the current one. Hover a figure for its table, entity and hour.
            </p>
            {/* session 1415: the same figures as a file, each with its hour */}
            <PanelFile of={{ panel: `grid_carbonrank_${grid ?? "all"}`, title: "the seven ISOs' latest hour of carbon intensity, ranked lowest first by intensity of generation", page: gridHref(grid ?? "us48", "clean"),
              tables: [`${T} (derived from eia930_all_emissions, EIA's CO2 estimates, over the Demand and Net generation columns of the same EIA workbooks), kg CO2 per MWh`],
              filter: "the seven ISOs' balancing authorities (eia930:CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP): each one's latest hour of intensity_generation and the same hour's intensity_demand",
              window: `Window: each ISO's latest hour in the last ${LOOK_BACK_DAYS} days the table holds (hour start, UTC)` }}
              columns={["Rank", "ISO", "Latest hour (start, UTC)", "Of generation, kg CO2/MWh", "Of demand, kg CO2/MWh"]}
              rows={[...latest.map((x, i) => [String(i + 1), x.label, x.g.ts_utc, NT(x.g, "the latest hour"), NT(x.d, "the same hour")]),
                ...heldRank.map((x) => { const h = <HeldPlace table={T} entity={x.entity} />; return ["not ranked", x.label, h, h, h]; })]} />
          </div>
        )}
        <p className="mt-1 text-xs text-muted" data-grid-method="carbon-now"><Link href={METHOD_EMISSIONS_BLOCKS}>Method: the Clean tab&apos;s carbon blocks, keyed</Link>.</p>
        </div>
        <Cite tables={[T]} note="Derived from eia930_all_emissions (EIA's CO2 estimates) over the Demand and Net generation columns of the same EIA workbooks" />
      </Section>

      <Section title="The last 24 hours" aside={<Tier />}>
        {got.ok && newest ? (
          <>
            <LineChart lines={lines} unit="kg CO2/MWh" height={260} ariaLabel="Carbon intensity of generation per ISO, the last 24 hours" />
            {/* session 1151: the chart's headline figures, each a key of carbon_intensity_hourly with its source in the tip */}
            {/* session 1159 (the brand pass): the table alone scrolls, in a frame a keyboard reaches; its note stays in place; each ISO is its row's header, so it stays in view as the figures scroll */}
            {/* session 1183: the panel's anchor, on the element that holds it alone (lib/gridAnchors.ts) */}
            <div id={GRID_ANCHOR.clean24}>
            <div className="mt-3" data-grid-panel={`grid_clean24_${grid ?? "all"}`}>
              <div className="overflow-x-auto" {...scrollRegion("Latest, lowest and highest intensity of generation per ISO in the 24 hours drawn")}>
              <table className="w-full min-w-[520px] text-sm tabular-nums">
                <caption className="sr-only">Latest, lowest and highest intensity of generation per ISO in the 24 hours drawn</caption>
                <thead>
                  <tr className="border-b border-rule text-left text-xs text-muted">
                    <th className="py-0.5 font-normal">ISO</th>
                    <th className="pr-2 text-right font-normal">Latest hour, kg CO2/MWh</th>
                    <th className="pr-2 text-right font-normal">Lowest of the 24 hours</th>
                    <th className="pr-2 text-right font-normal">Highest of the 24 hours</th>
                  </tr>
                </thead>
                <tbody>
                  {lastDayFigures(rows, open.map((i) => i.entity), newest).map((d) => (
                    <tr key={d.entity} className={`border-b border-rule ${d.entity === focus ? "bg-paper font-semibold" : ""}`} data-focus={d.entity === focus ? "1" : undefined}>
                      <th scope="row" className="py-0.5 pr-2 text-left font-normal">{ISOS.find((i) => i.entity === d.entity)!.label}</th>
                      <td className="pr-2 text-right"><F f={d.latest} /> <span className="text-xs text-muted">{d.latest.ts.slice(11, 16)}</span></td>
                      <td className="pr-2 text-right"><F f={d.low} /> <span className="text-xs text-muted">{d.low.ts.slice(11, 16)}</span></td>
                      <td className="pr-2 text-right"><F f={d.high} /> <span className="text-xs text-muted">{d.high.ts.slice(11, 16)}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
              {/* session 1415: a held ISO's place (lib/gridHeld.ts heldCarbonRow; none is held today), its line not drawn in the chart */}
              {held24.length ? <p className="mt-1 text-sm" data-carbon-held="clean24">{held24.map((i, k) => <span key={i.entity}>{k ? "; " : ""}{i.label}: <HeldPlace table={T} entity={i.entity} /></span>)}.</p> : null}
              <p className="mt-1 text-xs text-muted">The hour beside each figure is its hour start, UTC. Hover a figure for its table, entity and hour.</p>
              {/* session 1182: the same figures as a file, each with its hour */}
              <PanelFile of={{ panel: `grid_clean24_${grid ?? "all"}`, title: "the latest, lowest and highest intensity of generation per ISO in the 24 hours drawn", page: gridHref(grid ?? "us48", "clean"),
                tables: [`${T} (derived from eia930_all_emissions, EIA's CO2 estimates, over EIA-930's net generation), kg CO2 per MWh`],
                filter: "the seven ISOs' balancing authorities (eia930:CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP), variable intensity_generation",
                window: `Window: the 24 hours to ${utc(new Date(newest).toISOString())} (hour start), the newest hour the table holds in the last ${LOOK_BACK_DAYS} days` }}
                columns={["ISO", "Latest hour, kg CO2/MWh", "Latest hour (start, UTC)", "Lowest of the 24 hours", "Lowest hour (start, UTC)", "Highest of the 24 hours", "Highest hour (start, UTC)"]}
                rows={[...lastDayFigures(rows, open.map((i) => i.entity), newest).map((d) => [ISOS.find((i) => i.entity === d.entity)!.label,
                  <F key="l" f={d.latest} />, d.latest.ts, <F key="lo" f={d.low} />, d.low.ts, <F key="hi" f={d.high} />, d.high.ts]),
                  ...held24.map((i) => { const h = <HeldPlace table={T} entity={i.entity} />; return [i.label, h, "", h, "", h, ""]; })]} />
              <PanelMethod at="clean24"><Link href={METHOD_CLEAN24}>Method: the Grid tool&apos;s panels, every figure keyed</Link></PanelMethod>
            </div>
            </div>
          </>
        ) : (
          // session 1181: the keyed panel's place says why it is not drawn (a failed read, or no row), under the panel's own name
          <div id={GRID_ANCHOR.clean24}>
          <div data-grid-panel={`grid_clean24_${grid ?? "all"}`} data-clean24-unread={got.ok ? "empty" : "failed"}>
            <NoData what="the last 24 hours" reason={got.ok ? `${T} has no row in the last ${LOOK_BACK_DAYS} days` : got.reason} />
            <PanelMethod at="clean24"><Link href={METHOD_CLEAN24}>Method: the Grid tool&apos;s panels, every figure keyed</Link></PanelMethod>
          </div>
          </div>
        )}
        <Cite tables={[T]} note={newest ? `Intensity of generation, hourly, the 24 hours to ${utc(new Date(newest).toISOString())} (hour start)` : undefined} />
      </Section>

      <Section title="Monthly since 2018" aside={<Tier />}>
        {/* session 1415: a named panel with its anchor, its file and its method, its place kept on a failed read */}
        <div id={EMISSIONS_ANCHOR.monthly} data-grid-panel={`grid_carbonmonth_${grid ?? "all"}`}>
        {monthly.ok && monthly.data.length ? (
          <Monthly rows={monthly.data} grid={grid} />
        ) : (
          <NoData what="the monthly intensity" reason={monthly.ok ? `${TM} returned no rows` : monthly.reason} />
        )}
        <p className="mt-1 text-xs text-muted" data-grid-method="carbon-monthly"><Link href={METHOD_EMISSIONS_BLOCKS}>Method: the Clean tab&apos;s carbon blocks, keyed</Link>.</p>
        </div>
        <Cite tables={[TM]} note="Derived from eia930_all_emissions over the Demand and Net generation columns of the same EIA workbooks, from 2018-07, when EIA's CO2 estimates start" />
      </Section>
    </>
  );
}
