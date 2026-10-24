// Energy Research Warehouse (ERW) site, session 1154 (chain 077): the scarcity hours, `grid_scarcity_<grid>`, on the
// Mix tab of the Grid tool, after the mix blocks and before "Generation mix, as a table". For ERCOT and CAISO, the
// latest 30 days scarcity_hours_by_grid holds (session 1150's decision: not the 30 days before today), as a strip by day
// (across) and hour of day in the grid's standard time (down), drawn by the shared HeatChart (components/svgchart.tsx):
// a cell for each held hour, filled where the real-time or the day-ahead hour was at or above USD 1,000 per MWh, a
// square where the grid's own signal was in force; the hover gives the hour, the variables at 1, the real-time
// intervals and the highest price of the hour (lib/scarcityStrip.ts). Under it the counts, each a check key. The other
// grids are not in the table: one line each says why (license needed, paused, or not yet held), and the Lower 48 links
// the two grids it holds. Every figure is a lib/scarcityStrip.ts figure: a key check-values recomputes and a one-line
// source in its hover tip.
// Session 1155: for CAISO, the days of the window with an Energy Emergency Alert or a Flex Alert in force
// (caiso_grid_emergencies, lib/caisoAlerts.ts alertDays) are marked on the day axis, a triangle under the day, each
// cell's hover naming the day's notices; the counts of alert days and restricted maintenance days (not alerts) keyed.
// Session 1174: for ERCOT, the days of the window with a call on supply or demand in ERCOT's notices (an EEA, a
// conservation appeal, a watch, an OCN for extreme weather: ercot_grid_notices, lib/ercotNotices.ts callDays) are marked
// the same way, each cell's hover naming the day's notices; the counts of call days and of days with a notice that is
// not a call keyed.
import { HeatChart } from "@/components/svgchart";
import { Missing } from "@/components/mix/Now";
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { ToolSection } from "@/components/tool/ToolPage";  // session 1159: the section title every panel of the chain draws
import { newest, renderTime } from "@/lib/data";
import { shown } from "@/lib/format";
import { ALERT_TABLE, alertDays, shortName, type AlertDays } from "@/lib/caisoAlerts";
import { NOTICE_TABLE, callDays, shortName as noticeName } from "@/lib/ercotNotices";
import { ercotNotices } from "@/lib/gridErcotNotices";
import { gridHref } from "@/lib/gridtool";
import { LICENSE_FROM, LICENSE_NEEDED, licenseHeldGrid } from "@/lib/license";
import { DAILY_PRICE_TABLE, RT_PRICE_TABLE, SCARCITY_GRIDS, SCARCITY_LEVEL, SCARCITY_TABLE, isScarcityGrid, scarcityStrip, windowOf, type Fig, type ScarcityGrid } from "@/lib/scarcityStrip";
import { gridNotices } from "@/lib/reliability";
import { HOURLY, attempt, rest } from "@/lib/supabase";

const METHOD = "/data/methods/scarcity_hours_by_grid";
const D = 86_400_000;
const LEVEL = `USD ${SCARCITY_LEVEL.toLocaleString("en-US")} per MWh`;
const dayName = (d: string) => new Date(`${d}T12:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
const utc = (ts: string) => `${ts.slice(0, 16).replace("T", " ")} UTC`;

/** A figure with its key and its one-line source as the hover tip. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>
    </span>
  );
}

/** A count of days of lib/caisoAlerts.ts, drawn as the panel's own figures (session 1155). */
const days = (f: AlertDays["signal"]): Fig => ({ check: f.check, raw: Number(f.raw), tip: f.tip });

/** Why a grid is not in the table, in the brand's words: the word on the face, the reason beside it. */
function notHeld(grid: string, label: string): { words: string; why: string } {
  if (grid === "pjm") return { words: LICENSE_NEEDED, why: `No PJM price is held, so ${SCARCITY_TABLE} cannot count PJM's hours at or above ${LEVEL}; PJM's own signal is not held as a table either.` };
  if (grid === "miso") return { words: "paused", why: `MISO's own files are paused since 4 October 2026 (its terms forbid automated access: docs/methods/miso_pause.md), so ${SCARCITY_TABLE} does not hold MISO.` };
  if (licenseHeldGrid(grid)) return { words: LICENSE_NEEDED, why: `${label}'s prices need a license from ${LICENSE_FROM} (warehouse/metadata/license_status.csv), so ${SCARCITY_TABLE} does not hold ${label}; its own signal, reserve shortage pricing, is not held as a table.` };
  return { words: "not in the table yet", why: `${label}'s hub prices are public, but ${SCARCITY_TABLE} does not yet hold ${label}: its own signal, reserve shortage pricing, is not held as a table, and the table counts a grid's price beside its own signal (adding a grid is one entry in the table's code).` };
}

async function stripOf(g: ScarcityGrid) {
  const top = await newest(SCARCITY_TABLE, g.entity, "rt_hour_ge_1000");
  if (!top) return null;
  const w = windowOf(top.ts_utc, g.behind);
  const span = `(ts_utc.gte.${w.start},ts_utc.lt.${w.end})`;
  const [rows, prices, daily, notices, ercot] = await Promise.all([
    rest<{ variable: string; ts_utc: string; value: number }>("series", { select: "variable,ts_utc,value", table_name: `eq.${SCARCITY_TABLE}`, entity: `eq.${g.entity}`, and: span, order: "ts_utc,variable" }, HOURLY),
    attempt(() => rest<{ ts_utc: string; value: number }>("series", { select: "ts_utc,value", table_name: `eq.${RT_PRICE_TABLE}`, entity: `eq.${g.price.entity}`, variable: `eq.${g.price.variable}`, and: span, order: "ts_utc" }, HOURLY)),
    g.daily ? attempt(() => rest<{ ts_utc: string; value: number }>("series", { select: "ts_utc,value", table_name: `eq.${DAILY_PRICE_TABLE}`, entity: `eq.${g.daily!.entity}`, variable: `eq.${g.daily!.variable}`,
      and: `(ts_utc.gte.${w.days[0]}T00:00:00Z,ts_utc.lte.${w.days[w.days.length - 1]}T00:00:00Z)`, order: "ts_utc" }, HOURLY)) : Promise.resolve(null),
    // session 1155: CAISO's notices, the same read as the Reliability section above (lib/reliability.ts, one request)
    g.slug === "caiso" ? attempt(() => gridNotices()) : Promise.resolve(null),
    // session 1174: ERCOT's notices, the same read as the state line above (lib/gridErcotNotices.ts, one request)
    g.slug === "ercot" ? attempt(() => ercotNotices()) : Promise.resolve(null),
  ]);
  const s = scarcityStrip(g, { rows, prices: prices.ok ? prices.data : [], daily: daily && daily.ok ? daily.data : [], newest: top.ts_utc });
  const alerts = notices && notices.ok ? alertDays(notices.data, w.days) : null;
  if (alerts) {
    // each cell of an alert day names the day's notices in its hover
    for (const [d, ts] of alerts.byDay) {
      const j = w.days.indexOf(d);
      if (j >= 0) for (const row of s.tips) row[j] = `${row[j]} CAISO's notices that Pacific day (${ALERT_TABLE}): ${ts.map(shortName).join(", ")}.`;
    }
  }
  const calls = ercot && ercot.ok ? callDays(ercot.data, w.days) : null;
  if (calls) {
    // session 1174: each cell of a call day names the day's notices in its hover
    for (const [d, ts] of calls.byDay) {
      const j = w.days.indexOf(d);
      if (j >= 0) for (const row of s.tips) row[j] = `${row[j]} ERCOT's notices that Central day (${NOTICE_TABLE}): ${ts.map(noticeName).join(", ")}.`;
    }
  }
  return {
    s, alerts, calls,
    failed: [...(prices.ok ? [] : [`${RT_PRICE_TABLE}: ${prices.reason}`]), ...(daily && !daily.ok ? [`${DAILY_PRICE_TABLE}: ${daily.reason}`] : []),
      ...(notices && !notices.ok ? [`${ALERT_TABLE}: ${notices.reason}`] : []), ...(ercot && !ercot.ok ? [`${NOTICE_TABLE}: ${ercot.reason}`] : [])],
  };
}

async function Strip({ g }: { g: ScarcityGrid }) {
  const read = await attempt(() => stripOf(g));
  if (!read.ok) return <Missing why={`${SCARCITY_TABLE} could not be read just now: ${read.reason}`} words="working on it" />;
  if (!read.data) return <Missing why={`${SCARCITY_TABLE} holds no hour of ${g.label}.`} />;
  const { s, alerts: caiso, calls, failed } = read.data;
  // the day marks: CAISO's alert days, or ERCOT's call days (session 1174); one grid a strip
  const alerts = caiso ?? calls;
  const w = s.window;
  const ago = Math.floor((renderTime() - (Date.parse(s.newest) + 3_600_000)) / D);
  const label = `${g.label}: the hours at or above ${LEVEL}, ${dayName(w.days[0])} to ${dayName(w.days[w.days.length - 1])}, by day and hour of day (${g.zone})`;
  return (
    <div data-scarcity-grid={g.slug} data-scarcity-window={`${w.start}/${w.end}`}>
      <p className="mb-2 max-w-3xl text-sm">
        The latest 30 days {SCARCITY_TABLE} holds for {g.label}: {dayName(w.days[0])} to {dayName(w.days[w.days.length - 1])}, by day (across) and hour of day in {g.zoneName} (down), as the method counts its hours.
        The table&apos;s newest hour starts {utc(s.newest)}, {ago} {ago === 1 ? "day" : "days"} before this page was drawn: it is rebuilt each month on the data machine, so these are not the 30 days before today.
        A filled cell is an hour whose real-time or day-ahead price at {g.hub} was at or above {LEVEL}; a square marks an hour of the grid&apos;s own signal ({g.own}). Hover a cell for its hour, its variables and its highest price.
      </p>
      <HeatChart id={`scarcity-${g.slug}`} rows={s.rows} cols={s.cols} cells={s.cells} tips={s.tips} marks={s.marks} colMarks={alerts?.cols} unit="" lo={0} hi={1} label={label}
        legend={["held, below USD 1,000", "at or above USD 1,000"]} />
      <p className="mt-1 text-xs text-muted" data-scarcity-marks={s.marks.length}>
        <span className="mr-1 inline-block h-2 w-2 align-middle" style={{ background: "var(--color-ink)" }} aria-hidden="true" />
        the grid&apos;s own signal in force ({g.own}){s.own ? "" : `: not held for these days (${g.ownMissing})`}.
      </p>
      {g.slug === "caiso" ? (
        <p className="mt-1 text-xs text-muted" data-scarcity-alert-days={caiso ? caiso.cols.length : "unread"}>
          <svg width="10" height="8" className="mr-1 inline-block align-middle" aria-hidden="true"><path d="M1 7L9 7L5 1Z" fill="var(--color-ink)" /></svg>
          {caiso ? <>
            under a day: an Energy Emergency Alert or a Flex Alert in force that Pacific day ({ALERT_TABLE}; the notice&apos;s Pacific day set on the
            same date of the strip&apos;s standard-time days): <F f={days(caiso.signal)} /> days of these 30{caiso.cols.length ? ` (${[...caiso.byDay.keys()].join(", ")})` : ""}.
            {" "}Restricted maintenance, not an alert and not marked: <F f={days(caiso.rmoFig)} /> days{caiso.rmo.length ? ` (${caiso.rmo.join(", ")})` : ""}{caiso.tx.length ? `; a transmission emergency, not an alert, on ${caiso.tx.join(", ")}` : ""}.
            {" "}<SiteLink href={`${gridHref("caiso", "mix")}#caiso-alerts`}>CAISO&apos;s alerts today</SiteLink>.
          </> : <>under a day: an alert day; {ALERT_TABLE} could not be read just now{failed.length ? ` (${failed.filter((x) => x.startsWith(ALERT_TABLE)).join("; ")})` : ""}.</>}
        </p>
      ) : null}
      {g.slug === "ercot" ? (
        <p className="mt-1 text-xs text-muted" data-scarcity-notice-days={calls ? calls.cols.length : "unread"}>
          <svg width="10" height="8" className="mr-1 inline-block align-middle" aria-hidden="true"><path d="M1 7L9 7L5 1Z" fill="var(--color-ink)" /></svg>
          {calls ? <>
            under a day: a call on supply or demand in ERCOT&apos;s notices that Central day (an Energy Emergency Alert, a conservation appeal, a watch or an
            OCN for extreme weather; {NOTICE_TABLE}, the notice&apos;s Central day set on the same date of the strip&apos;s standard-time days): <F f={days(calls.call)} /> days
            of these 30{calls.cols.length ? ` (${[...calls.byDay.keys()].join(", ")})` : ""}.
            {" "}A notice that is not a call (an Advisory on the control room&apos;s own tools, a test), not marked: <F f={days(calls.otherFig)} /> days{calls.other.length ? ` (${calls.other.join(", ")})` : ""}.
            {" "}<SiteLink href={`${gridHref("ercot", "mix")}#ercot-notices`}>ERCOT&apos;s notices today</SiteLink>.
          </> : <>under a day: a notice day; {NOTICE_TABLE} could not be read just now{failed.length ? ` (${failed.filter((x) => x.startsWith(NOTICE_TABLE)).join("; ")})` : ""}.</>}
        </p>
      ) : null}
      <ul className="mt-3 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-scarcity-counts={g.slug}>
        {s.rt ? <li>Real time: <F f={s.rt.hours} /> of <F f={s.rt.held} /> hours held at or above {LEVEL} (the hour&apos;s mean at {g.hub}); <F f={s.rt.intervals} /> 15-minute intervals at or above it.</li> : <li>Real time: no hour of these days is held.</li>}
        {s.da ? <li>Day ahead: <F f={s.da.hours} /> of <F f={s.da.held} /> hours held at or above {LEVEL}.</li> : <li>Day ahead: no hour of these days is held.</li>}
        {s.own ? <li>The grid&apos;s own signal ({g.own}): <F f={s.own.hours} /> of <F f={s.own.held} /> hours held.</li> : <li>The grid&apos;s own signal: not held for these days ({g.ownMissing}).</li>}
        {s.rtMax ? <li>Highest 15-minute real-time price at {g.hub} the live set holds for these days: USD <F f={s.rtMax} /> per MWh ({RT_PRICE_TABLE}, from {utc(s.rtMax.from)}: the live set keeps about 35 days of 15-minute prices).</li>
          : <li>No 15-minute price of these days is in the live set ({RT_PRICE_TABLE} keeps about 35 days){failed.length ? `: ${failed.join("; ")}` : ""}.</li>}
        {s.dayMax ? <li>Highest real-time price of ERCOT&apos;s local days {dayName(w.days[0])} to {dayName(w.days[w.days.length - 1])} at {g.hub}: USD <F f={s.dayMax} /> per MWh ({DAILY_PRICE_TABLE}).</li> : null}
      </ul>
      <p className="mt-2 text-xs text-muted" data-scarcity-source="1">
        Level: {LEVEL}, docs/methods/scarcity_hours_by_grid.md; prices: {g.label}. An hour without a row is not held, not a zero. <SiteLink href={METHOD}>Method: each grid&apos;s own scarcity signal</SiteLink>
      </p>
    </div>
  );
}

/** Session 1154: the scarcity hours of the grid in view. */
export async function ScarcityPanel({ grid, label }: { grid: string; label: string }) {
  return (
    <div data-grid-panel={`grid_scarcity_${grid}`}>
      <ToolSection title={grid === "us48" ? "The scarcity hours, by grid" : `${label}: the scarcity hours, last 30 days held`} id="scarcity">
        {isScarcityGrid(grid) ? <Strip g={SCARCITY_GRIDS[grid]} />
          : grid === "us48" ? (
            <p className="max-w-3xl text-sm" data-scarcity-us48="1">
              {SCARCITY_TABLE} is by grid, and it holds two: <SiteLink href={`${gridHref("ercot", "mix")}#scarcity`}>ERCOT&apos;s scarcity hours</SiteLink> and <SiteLink href={`${gridHref("caiso", "mix")}#scarcity`}>CAISO&apos;s</SiteLink>.
            </p>
          ) : (() => { const n = notHeld(grid, label); return <p className="max-w-3xl text-sm" data-scarcity-held={n.words}>{label}: <Missing why={n.why} words={n.words} /> <span className="text-xs text-muted">{n.why}</span></p>; })()}
      </ToolSection>
    </div>
  );
}
