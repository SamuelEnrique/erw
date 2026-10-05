import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import {
  ENTITY, MODEL_ENTITY, MODEL_GAP_VARIABLES, MODEL_TABLE, MODEL_VARIABLES, OFFERS_TABLE, OFFER_VARIABLES, TABLE, VARIABLES, MODEL_PREFIX, energyAwardShare, gapOf, kw, monthName, monthsOf, newestComplete, perKw,
  shortMonth, span, summary, whole, years,
  type Month, type Row,
} from "@/lib/storageawards";
import { BASIS_ENTITY, BASIS_TABLE, BASIS_VARIABLES, RT_ENTITY, RT_TABLE, RT_VARIABLES, basisOf, rtMonthsOf } from "@/lib/storagerealtime";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { CostTabs } from "../../Tabs";
import { OFFERS_METHOD, OffersSection } from "./Offers";
import { RT_METHOD, RealTimeSection } from "./RealTime";

// Session 115: what Texas's storage resources were awarded day-ahead, in the battery page's layout. It reads
// ercot_storage_dam_awards_monthly (warehouse/derived, from ERCOT's 60-Day DAM Disclosure Reports, the file
// 60d_DAM_ESR_Data) and, for the column labeled as the model's, the day-ahead schedule of a 2-hour battery from
// battery_stack_monthly. Every figure is computed by lib/storageawards.ts from those rows; nothing is scaled or filled.
// The page says first what the awards are not: day-ahead awards only, a floor on market revenue. The model's figure is
// set beside the awards only over months the table holds whole. In review (lib/release.ts); the live battery page
// (../page.tsx) is as it was and does not link here.
// Session 116: one more section (./Offers.tsx), what the fleet offered day-ahead and the gap to the model's figure in
// three parts, from ercot_storage_dam_offers_monthly and the model's rows for the same months. When that table cannot
// be read the section says so and every section above it is as it was.
// Session 120: the real-time side (./RealTime.tsx), from ercot_storage_rt_monthly and ercot_storage_node_basis: what
// the fleet did in real time beside its day-ahead awards, real time valued at the hub average's price and said to be.
// It states first what it still leaves out. When its tables cannot be read it says so and every section above is as it was.
export const metadata: Metadata = { title: "What Texas's batteries were awarded day-ahead", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/ercot_storage_dam_awards";
const ENERGY = "#8C1515", ANCILLARY = "#2E2D29";  // cardinal and Stanford black, as on the battery page

async function fleetRows(): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${TABLE}`, entity: `eq.${ENTITY}`,
    variable: `in.(${VARIABLES.join(",")})`, order: "variable,ts_utc" }, HOURLY);
}
async function modelRows(): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${MODEL_TABLE}`, entity: `eq.${MODEL_ENTITY}`,
    variable: `in.(${MODEL_VARIABLES.join(",")})`, order: "variable,ts_utc" }, HOURLY);
}
async function offerRows(): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${OFFERS_TABLE}`, entity: `eq.${ENTITY}`,
    variable: `in.(${OFFER_VARIABLES.join(",")})`, order: "variable,ts_utc" }, HOURLY);
}
async function realTimeRows(): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${RT_TABLE}`, entity: `eq.${RT_ENTITY}`,
    variable: `in.(${RT_VARIABLES.join(",")})`, order: "variable,ts_utc" }, HOURLY);
}
async function basisRows(): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${BASIS_TABLE}`, entity: `eq.${BASIS_ENTITY}`,
    variable: `in.(${BASIS_VARIABLES.join(",")})`, order: "variable,ts_utc" }, HOURLY);
}
/** The model's rows the offers section sets beside the offers: from the offers table's first month on. */
async function modelGapRows(from: string): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${MODEL_TABLE}`, entity: `eq.${MODEL_ENTITY}`,
    variable: `in.(${MODEL_GAP_VARIABLES.join(",")})`, ts_utc: `gte.${from}`, order: "variable,ts_utc" }, HOURLY);
}

/** Day-ahead awards by month, USD per kW, stacked: energy net of charging, then ancillary services. A month whose days
 * are not all held is hatched, and is the held days' sum only. */
function MonthBars({ ms }: { ms: Month[] }) {
  const W = 760, H = 300, L = 54, R = 10, top = 26, bot = 46;
  const up = (r: Month) => Math.max(0, perKw(r.energy)) + Math.max(0, perKw(r.ancillary));
  const down = (r: Month) => Math.min(0, perKw(r.energy)) + Math.min(0, perKw(r.ancillary));
  const hi = (Math.max(0, ...ms.map(up)) || 1) * 1.15;
  const lo = Math.min(0, ...ms.map(down)) * 1.15;
  const step = [0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 50].find((s) => (hi - lo) / s <= 6) ?? 100;
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(Math.round(t * 100) / 100);
  const y = (v: number) => top + ((hi - v) / (hi - lo)) * (H - top - bot);
  const bw = (W - L - R) / ms.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Day-ahead awards by month, USD per kW, stacked: energy net of charging and ancillary services">
      <defs>
        <pattern id="aw-hatch-e" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill={ENERGY} /></pattern>
        <pattern id="aw-hatch-a" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill={ANCILLARY} /></pattern>
      </defs>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke={t === 0 ? "#2E2D29" : "#D9D2C3"} strokeWidth={t === 0 ? 1 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="#6B665E">{t}</text>
        </g>
      ))}
      <text x={L - 46} y={14} fontSize="11" fill="#6B665E">USD per kW</text>
      {ms.map((r, i) => {
        const e = perKw(r.energy), a = perKw(r.ancillary);
        const x0 = L + i * bw + bw * 0.18, w = bw * 0.64;
        const segs: { v0: number; v1: number; fill: string; line: string }[] = [];
        let u = 0, d = 0;
        for (const [v, solid, hatch] of [[e, ENERGY, "url(#aw-hatch-e)"], [a, ANCILLARY, "url(#aw-hatch-a)"]] as [number, string, string][]) {
          if (v >= 0) { segs.push({ v0: u, v1: u + v, fill: r.complete ? solid : hatch, line: solid }); u += v; }
          else { segs.push({ v0: d + v, v1: d, fill: r.complete ? solid : hatch, line: solid }); d += v; }
        }
        return (
          <g key={r.m} data-awards-bar={r.m}>
            {segs.map((s, k) => (s.v1 === s.v0 ? null
              : <rect key={k} x={x0} width={w} y={y(s.v1)} height={Math.max(0.5, y(s.v0) - y(s.v1))} fill={s.fill} stroke={r.complete ? "none" : s.line} strokeWidth={r.complete ? 0 : 0.75} />))}
            <text x={x0 + w / 2} y={y(u) - 6} textAnchor="middle" fontSize="11" fill="#2E2D29">{kw(r.total)}</text>
            <text x={x0 + w / 2} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="#2E2D29">{shortMonth(r.m)}</text>
            {!r.complete ? <text x={x0 + w / 2} y={H - bot + 30} textAnchor="middle" fontSize="10" fill="#6B665E">{r.daysHeld} of {r.daysInMonth} days</text> : null}
            <title>{`${monthName(r.m)}: energy ${kw(r.energy)}, ancillary services ${kw(r.ancillary)} USD per kW awarded day-ahead${r.complete ? "" : ` (${r.daysHeld} of ${r.daysInMonth} days held)`}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

const notHeld = <span className="text-muted">not held</span>;

export default async function Awards() {
  const [read, readModel, readOffers, readRt, readBasis] = await Promise.all([attempt(fleetRows), attempt(modelRows), attempt(offerRows), attempt(realTimeRows), attempt(basisRows)]);
  const rtMonths = readRt.ok ? rtMonthsOf(readRt.data, readModel.ok ? readModel.data : [], MODEL_PREFIX) : [];
  const offers = readOffers.ok ? readOffers.data : [];
  const firstOffer = offers.reduce((a, r) => (a === "" || r.ts_utc < a ? r.ts_utc : a), "");
  const readGapModel = firstOffer ? await attempt(() => modelGapRows(firstOffer)) : null;
  const gap = read.ok && readOffers.ok && readGapModel?.ok ? gapOf(read.data, offers, readGapModel.data) : null;
  const offersUnread = !readOffers.ok ? readOffers.reason : readGapModel && !readGapModel.ok ? `the model's rows for the same months: ${readGapModel.reason}` : null;
  const ms = monthsOf(read.ok ? read.data : [], readModel.ok ? readModel.data : []);
  const ys = years(ms);
  const newest = newestComplete(ms);
  const sentence = summary(ms);
  const share = energyAwardShare(ms);

  return (
    <ToolPage>
      <ToolHeader
        title="What Texas's batteries were awarded day-ahead"
        crumb={<CostTabs active="battery" />}
        lead={<span data-awards-not="1"><strong>What this is not.</strong> These are day-ahead awards only: no real-time settlement, no deployment energy, no contracts. So this is a floor on
          market revenue and not what any battery earned. It is what ERCOT&apos;s storage resources were awarded in the day-ahead market, each award at the price ERCOT printed beside it, 60 days after the day. <Link href={METHOD}>Method</Link>.</span>}
      />
      <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
        <aside>
          <InputPanel title="What is counted" note={<>The model of what one battery could make from these markets is on <Link href="/cost-of-power/battery">the battery page</Link>. This page changes nothing there.</>}>
            <ul className="list-disc space-y-1.5 pl-4 text-sm">
              <li><strong>The fleet.</strong> Every Energy Storage Resource in ERCOT&apos;s file for the month, one that was out or testing included.</li>
              <li><strong>MW.</strong> The sum of each resource&apos;s highest limit (its High Sustained Limit) in the month.</li>
              <li><strong>Energy.</strong> Each hour&apos;s awarded MW times the day-ahead price at the resource&apos;s own settlement point. A purchase, which is charging, is taken off.</li>
              <li><strong>Ancillary services.</strong> Each award times that service&apos;s clearing price for capacity.</li>
              <li><strong>Per kW.</strong> The month&apos;s sum over the fleet&apos;s MW. A resource with no award adds nothing to the sum and is still counted in the MW.</li>
              <li><strong>Missing days.</strong> Nothing is filled for a day that is not held. A month whose days are not all held is marked partial and is the held days&apos; sum only.</li>
            </ul>
          </InputPanel>
        </aside>

        <div className="min-w-0">
          {!read.ok ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-awards-state="unread">The table could not be read, so no number is shown: {read.reason}</p>
          ) : !ms.length ? (
            <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status" data-awards-state="not-loaded">The table <code className="font-mono">{TABLE}</code> is not loaded in the site&apos;s database, so no number is shown.</p>
          ) : (
            <>
              <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-awards-summary="1">
                {sentence ?? `No month is held whole yet, so there is no monthly figure to state: ${ms.map((r) => `${monthName(r.m)} holds ${r.daysHeld} of ${r.daysInMonth} days`).join("; ")}.`}
              </p>

              <ChartFrame title="Day-ahead awards by month, USD per kW"
                legend={[{ label: "Energy, net of charging", color: ENERGY }, { label: "Ancillary services", color: ANCILLARY }, { label: "Partial month", color: ANCILLARY, hatch: true }]}
                note={<>Day-ahead awards only, per kW of the fleet&apos;s MW: a floor on market revenue, with no real-time settlement, no deployment energy and no contracts in it. A hatched month does not hold all of its days and shows the held days&apos; sum, never a scaled one.</>}>
                <MonthBars ms={ms} />
              </ChartFrame>

              <ToolSection title="By month" note={<>The last column is the model&apos;s, not ERCOT&apos;s: the battery page&apos;s day-ahead schedule for one 2-hour battery at the hub average, for the whole month.
                Beside a partial month it covers more days than the awards do, and the two are not to be compared.{readModel.ok ? "" : ` The model's table could not be read: ${readModel.reason}`}</>}>
                <ToolTable caption="Day-ahead awards by month" minWidth={760}
                  head={["Month", "Days held", "Resources", "MW", "Energy, USD per kW", "Ancillary services, USD per kW", "Total awarded, USD per kW",
                    <>The model&apos;s<span className="mt-0.5 block text-xs opacity-80">2-hour battery, day-ahead schedule, USD per kW</span></>]}
                  rows={[...ms].reverse().map((r) => ({
                    key: r.m, muted: !r.complete,
                    cells: [
                      <span key="m" data-awards-month={r.m}>{monthName(r.m)}{r.complete ? null : <span className="block text-xs">partial</span>}</span>,
                      `${r.daysHeld} of ${r.daysInMonth}`,
                      r.resources === null ? notHeld : whole(r.resources),
                      r.mw === null ? notHeld : whole(r.mw),
                      kw(r.energy), kw(r.ancillary),
                      <span key="t" data-awards-total={r.m} data-awards-raw={r.total}>{kw(r.total)}</span>,
                      r.model === null ? notHeld : <span key="x" data-awards-model={r.m} data-awards-raw={r.model.total}>{kw(r.model.total)}{r.complete && r.model.whole ? null : <span className="block text-xs text-muted">{r.model.whole ? "whole month" : "the model's month is partial"}</span>}</span>,
                    ],
                  }))} />
              </ToolSection>

              <ToolSection title="By year" note={<>A year&apos;s figure is the sum of its months&apos; figures per kW, over the days held; no partial month is scaled up. The model&apos;s figure stands beside the awards only over the
                months held whole, the same months for both. It is the model&apos;s: one 2-hour battery scheduled against day-ahead prices, on <Link href="/cost-of-power/battery">the battery page</Link>.</>}>
                <ToolTable caption="Day-ahead awards by year" minWidth={820}
                  head={["Year", "Days held", "Energy, USD per kW", "Ancillary services, USD per kW", "Total awarded, USD per kW", "Months held whole",
                    <>Awarded over them<span className="mt-0.5 block text-xs opacity-80">USD per kW</span></>,
                    <>The model&apos;s, same months<span className="mt-0.5 block text-xs opacity-80">2-hour battery, day-ahead schedule, USD per kW</span></>,
                    "Awards as a share of the model's"]}
                  rows={ys.map((r) => ({
                    key: r.y,
                    cells: [
                      <span key="y" data-awards-year={r.y}>{r.y}</span>,
                      `${r.daysHeld} of ${r.daysInMonths}`,
                      kw(r.energy), kw(r.ancillary), kw(r.total),
                      r.completeMonths.length ? span(r.completeMonths) : "none",
                      r.awardsComplete === null ? <span key="a" className="text-muted">no month held whole</span> : kw(r.awardsComplete),
                      r.modelComplete === null ? <span key="x" className="text-muted">not set beside it: {r.noModel}</span> : <span key="x" data-awards-model-year={r.y} data-awards-raw={r.modelComplete}>{kw(r.modelComplete)}</span>,
                      r.modelComplete === null || r.awardsComplete === null || r.modelComplete <= 0 ? "" : `${Math.round((r.awardsComplete / r.modelComplete) * 100)}%`,
                    ],
                  }))} />
              </ToolSection>

              <ToolSection title="Why the two differ">
                <div className="max-w-3xl space-y-2 text-sm">
                  <p>The model&apos;s figure is one 2-hour battery scheduled without error against the day-ahead prices of the hub average, every hour of every day, with every offer cleared.
                    The awards are what the whole fleet took day-ahead: batteries of every duration, each at its own settlement point, with a resource that was out or testing still counted in the MW.</p>
                  {share ? (
                    <p data-awards-share="1">Across the months held, a storage resource held a day-ahead energy award in {(share.share * 100).toFixed(1)} percent of its hours
                      ({whole(share.withAward)} of {whole(share.hours)} resource-hours). Whatever it did in the other hours is not in this table: real time is another report.</p>
                  ) : null}
                  {newest && newest.resources !== null && newest.resourcesWithAward !== null ? (
                    <p>In {monthName(newest.m)}, {whole(newest.resourcesWithAward)} of the {whole(newest.resources)} resources held a day-ahead award of any kind.</p>
                  ) : null}
                  <p>So the distance between the two columns is not a measure of the model&apos;s error. The real-time side would have to be added before the two could be compared.</p>
                  <p>It is added, with real-time energy at the hub average&apos;s price and not at each battery&apos;s own node, in <a href="#real-time" className="underline">the last section</a>.</p>
                  <p>How much of that distance is capacity that offered nothing day-ahead, how much was offered and not awarded, and how much is price is in <a href="#offers" className="underline">the next section</a>.</p>
                </div>
              </ToolSection>

              <OffersSection gap={gap} unread={offersUnread} loaded={offers.length > 0} />

              <RealTimeSection months={rtMonths} basis={readBasis.ok ? basisOf(readBasis.data) : null} unread={readRt.ok ? null : readRt.reason} basisUnread={readBasis.ok ? null : readBasis.reason} />
            </>
          )}
        </div>
      </div>
      <SourceLine tables={[TABLE, MODEL_TABLE, OFFERS_TABLE, RT_TABLE, BASIS_TABLE]}
        note={<>The first table is derived by the ERW from ERCOT&apos;s 60-Day DAM Disclosure Reports (NP3-966-ER), the file 60d_DAM_ESR_Data, which ERCOT posts 60 days after each operating day; the second is the battery page&apos;s model. <Link href={METHOD}>Method</Link>.
          The third is derived from the same file&apos;s offer curves and from 60d_DAM_ESR_ASOffers. <Link href={OFFERS_METHOD}>Method</Link>.
          The fourth and fifth are derived from ERCOT&apos;s 60-Day SCED Disclosure Reports (NP3-965-ER), the file 60d_ESR_Data_in_SCED, and from its real-time Settlement Point Prices at Resource Nodes, Hubs
          and Load Zones (NP6-905-CD). <Link href={RT_METHOD}>Method</Link>.</>} />
    </ToolPage>
  );
}
