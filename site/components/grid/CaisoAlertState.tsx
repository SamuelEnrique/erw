// Energy Research Warehouse (ERW) site, session 1155 (chain 077): CAISO's alerts, tied into the Grid tool. At the top of
// the Mix tab for CAISO (/grid?grid=caiso), `grid_caisoalert_caiso`: whether an Energy Emergency Alert or a Flex Alert is
// in force today (the Pacific day the page was drawn), else the last day one was, with its type; restricted maintenance
// and transmission emergencies named apart (they are not alerts, as docs/methods/scarcity_hours_by_grid.md says); the
// table's newest notice beside it, so "no alert today" is never said past what the table holds; and the links to the
// Flex Alert scorecard (/grid/caiso/alerts) and to the alert days on the scarcity strip. Every date and count is a
// lib/caisoAlerts.ts figure: an awe| key scripts/check-values.mjs recomputes, and a one-line source in its hover tip.
// The rows are lib/reliability.ts gridNotices(), the same read as the Reliability section below (one request).
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolSection } from "@/components/tool/ToolPage";
import { ALERT_TABLE, alertState, shortName, type DayNotices, type Fig } from "@/lib/caisoAlerts";
import { renderTime } from "@/lib/data";
import { count } from "@/lib/format";
import { gridHref } from "@/lib/gridtool";
import { gridNotices } from "@/lib/reliability";
import { attempt } from "@/lib/supabase";
import { CAISO_HOLDS, wholeRead } from "@/lib/gridReads";  // session 1181

/** A figure with its key and its one-line source as the hover tip: a day as written (YYYY-MM-DD), a count whole. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{typeof f.raw === "number" ? count(f.raw) : f.raw}</Num>
    </span>
  );
}

const MIX = gridHref("caiso", "mix");
const types = (d: DayNotices) => d.types.map(shortName).join(", ");
const regions = (d: DayNotices) => (d.regions.length ? `, ${d.regions.join("; ")}` : "");

/** Session 1155: the state line of CAISO's alerts, for the CAISO view of the Mix tab. */
export async function CaisoAlertState() {
  // session 1181: the whole table answering no row is a failed read, never "no alert today" (lib/gridReads.ts wholeRead)
  const read = (await wholeRead(ALERT_TABLE, CAISO_HOLDS, attempt(() => gridNotices())))!;
  return (
    <div data-grid-panel="grid_caisoalert_caiso">
      <ToolSection title="CAISO's alerts: today" id="caiso-alerts">
        {!read.ok ? <p className="text-sm text-muted">CAISO&apos;s notices could not be read just now: {read.reason}</p> : (() => {
          const s = alertState(read.data, renderTime());
          if (!s.newest) return <p className="text-sm text-muted">caiso_grid_emergencies holds no notice on or before {s.today}.</p>;
          return (
            <div className="max-w-3xl text-sm" data-caisoalert-today={s.today} data-caisoalert-covered={s.covered ? "1" : "0"}>
              <p className="mb-2" data-caisoalert-state={s.covered ? (s.todayAlerts.length ? "in-force" : "none") : "not-held"}>
                {s.covered
                  ? s.todayAlerts.length
                    ? <><strong>In force today</strong>, {s.today} (Pacific): {s.todayAlerts.map(shortName).join(", ")}.</>
                    : <><strong>No Energy Emergency Alert or Flex Alert today</strong>, {s.today} (Pacific), in CAISO&apos;s notices.</>
                  : <><strong>Today, {s.today} (Pacific), is not held yet:</strong> the table holds CAISO&apos;s notices to <F f={s.newest} />, the newest day in the
                    report as last read, so whether an alert is in force today is not said here.</>}
                {" "}
                {s.lastSignal
                  ? <>The last day with an Energy Emergency Alert or a Flex Alert in force: <F f={s.lastSignal.fig} /> ({types(s.lastSignal)}{regions(s.lastSignal)}).</>
                  : <>No Energy Emergency Alert or Flex Alert is held.</>}
                {s.lastFlex && s.lastFlex.day !== s.lastSignal?.day ? <> The last Flex Alert: <F f={s.lastFlex.fig} />.</> : null}
                {" "}Days with one in {s.year}, as held: <F f={s.signalDays} />.
              </p>
              <p className="mb-2" data-caisoalert-not-alerts="1">
                Not alerts, named apart:{" "}
                {s.lastRmo ? <>restricted maintenance operations (plants asked to put off maintenance), last on <F f={s.lastRmo.fig} />{regions(s.lastRmo)}, on <F f={s.rmoDays} /> days in {s.year};</> : <>no restricted maintenance is held;</>}{" "}
                {s.lastTx ? <>a transmission emergency (local), last on <F f={s.lastTx.fig} />{regions(s.lastTx)}.</> : <>no transmission emergency is held.</>}
              </p>
              <p className="mb-1" data-caisoalert-links="1">
                <Link href="/grid/caiso/alerts">The Flex Alert scorecard</Link>: every alert day since July 2018 set against a weather-and-calendar model of
                demand, the cut in MW with its interval, and its wholesale value. The alert days on <Link href={`${MIX}#scarcity`}>the scarcity strip</Link>, and every
                notice since 1998 in <Link href={`${MIX}#reliability`}>Reliability</Link>.
              </p>
              <p className="text-xs text-muted">
                caiso_grid_emergencies (California ISO, Grid Emergencies History Report): one row per notice type, region and Pacific day; an alert is an
                Energy Emergency Alert (EEA Watch, EEA 1 to 3) or a Flex Alert (before May 2022 also Alert, Warning and the stage emergencies), as the
                scarcity table&apos;s own signal counts them. <Link href="/data/methods/california_reliability">Method: California reliability</Link>
              </p>
            </div>
          );
        })()}
      </ToolSection>
    </div>
  );
}
