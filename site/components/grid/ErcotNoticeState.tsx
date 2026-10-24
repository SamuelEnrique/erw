// Energy Research Warehouse (ERW) site, session 1174 (chain 078): ERCOT's notices, tied into the Grid tool as CAISO's
// alerts are (session 1155, CaisoAlertState.tsx). At the top of the Mix tab for ERCOT (/grid?grid=ercot),
// `grid_ercotnotice_ercot`: whether a call on supply or demand (an Energy Emergency Alert, a conservation appeal, a watch,
// an Operating Condition Notice for extreme weather) is in force today (the Central day the page was drawn), else the
// last day of each kind; the notices that are not calls named apart; the table's newest notice and the day the ERW last
// read ERCOT's pages beside it, so "none today" is never said past what the table holds; and the links to the notice
// days on the scarcity strip and on the monthly mix. Every date and count is a lib/ercotNotices.ts figure: an ercotn|
// key scripts/check-values.mjs recomputes, and a one-line source in its hover tip. The rows are
// lib/gridErcotNotices.ts ercotNotices(), the same read as the strip and the monthly mix (one request).
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ToolSection } from "@/components/tool/ToolPage";
import { renderTime } from "@/lib/data";
import { noticeState, shortName, type DayNotices, type Fig } from "@/lib/ercotNotices";
import { count } from "@/lib/format";
import { ercotNotices } from "@/lib/gridErcotNotices";
import { gridHref } from "@/lib/gridtool";
import { attempt } from "@/lib/supabase";
import { PanelFile, type FileCell } from "@/components/grid/PanelFile";  // session 1182: the state line's days and counts, to download

/** A figure with its key and its one-line source as the hover tip: a day as written (YYYY-MM-DD), a count whole. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{typeof f.raw === "number" ? count(f.raw) : f.raw}</Num>
    </span>
  );
}

const MIX = gridHref("ercot", "mix");
const MONTH = gridHref("ercot", "mix", { mixp: "month" });
const types = (d: DayNotices) => d.types.map(shortName).join(", ");
const regions = (d: DayNotices) => (d.regions.length && d.regions.some((r) => r !== "ERCOT") ? `, ${d.regions.join("; ")}` : "");

/** Session 1174: the state line of ERCOT's notices, for the ERCOT view of the Mix tab. */
export async function ErcotNoticeState() {
  const read = await attempt(() => ercotNotices());
  return (
    <div data-grid-panel="grid_ercotnotice_ercot">
      <ToolSection title="ERCOT's notices: today" id="ercot-notices">
        {!read.ok ? <p className="text-sm text-muted">ERCOT&apos;s notices could not be read just now: {read.reason}</p> : (() => {
          const s = noticeState(read.data, renderTime());
          if (!s.newest) return <p className="text-sm text-muted">ercot_grid_notices holds no notice on or before {s.today}.</p>;
          return (
            <div className="max-w-3xl text-sm" data-ercotnotice-today={s.today} data-ercotnotice-covered={s.covered ? "1" : "0"}>
              <p className="mb-2" data-ercotnotice-state={s.covered ? (s.todayCalls.length ? "in-force" : "none") : "not-held"}>
                {s.covered
                  ? s.todayCalls.length
                    ? <><strong>In force today</strong>, {s.today} (Central): {s.todayCalls.map(shortName).join(", ")}.</>
                    : <><strong>No Energy Emergency Alert, conservation appeal or watch today</strong>, {s.today} (Central), in ERCOT&apos;s notices.</>
                  : <><strong>Today, {s.today} (Central), is not held yet:</strong> the table holds ERCOT&apos;s notices to <F f={s.newest} />
                    {s.read ? <>, read from ERCOT&apos;s pages on <F f={s.read} /> (UTC)</> : null}, so whether a notice is in force today is not said here.</>}
                {" "}
                {s.lastCall
                  ? <>The last day with a call on supply or demand: <F f={s.lastCall.fig} /> ({types(s.lastCall)}).</>
                  : <>No call on supply or demand is held.</>}
                {" "}Days with one in {s.year}, as held: <F f={s.callDays} />.
              </p>
              <ul className="mb-2 list-disc space-y-0.5 pl-5" data-ercotnotice-kinds={s.kinds.filter((k) => k.last).length}>
                {s.kinds.map((k) => (
                  <li key={k.kind} data-ercotnotice-kind={k.kind}>
                    The last day with {k.name}: {k.last ? <><F f={k.last.fig} /> ({types(k.last)}{regions(k.last)})</> : "none held"}.
                  </li>
                ))}
              </ul>
              <p className="mb-2" data-ercotnotice-not-calls="1">
                Not calls, named apart:{" "}
                {s.lastOther
                  ? <>the control room&apos;s Advisories and Watches on its own tools, tests, statements and notices for the Rio Grande Valley only, last on <F f={s.lastOther.fig} /> ({types(s.lastOther)}{regions(s.lastOther)}), on <F f={s.otherDays} /> days in {s.year}.</>
                  : <>none is held.</>}
              </p>
              <p className="mb-1" data-ercotnotice-links="1">
                The notice days on <Link href={`${MIX}#scarcity`}>the scarcity strip</Link>, and by month on <Link href={`${MONTH}#hourly`}>the monthly mix</Link>.
              </p>
              {/* session 1182: the days and counts above as a file, one a row, exactly those the lines draw */}
              <PanelFile of={{ panel: "grid_ercotnotice_ercot", title: "ERCOT's notices: today, the last day of each kind, and the notices that are not calls", page: `${MIX}#ercot-notices`,
                tables: ["ercot_grid_notices (ERCOT's news releases since 2011 and its control room's operations messages since May 2026: one row per notice and Central day it covers)"],
                filter: "every notice the table holds; a call is a system-wide call on supply or demand (an Energy Emergency Alert, a conservation appeal, a watch, an OCN for extreme weather)",
                window: `Window: every day the table holds, to ${s.today} (Central), the day the page was drawn; the year counted is ${s.year}` }}
                columns={["What", "Day or count", "Notices"]}
                rows={([
                  ["Today (Central)", s.today, s.covered ? (s.todayCalls.length ? s.todayCalls.map(shortName).join(", ") : "no Energy Emergency Alert, conservation appeal or watch") : "not held yet"],
                  ...(s.covered ? [] : [["The newest day the table holds", s.newest, ""], ...(s.read ? [["Read from ERCOT's pages on (UTC)", s.read, ""]] : [])]),
                  ["The last day with a call on supply or demand", s.lastCall ? s.lastCall.fig : "none held", s.lastCall ? types(s.lastCall) : ""],
                  [`Days with one in ${s.year}, as held`, s.callDays, ""],
                  ...s.kinds.map((k) => [`The last day with ${k.name}`, k.last ? k.last.fig : "none held", k.last ? `${types(k.last)}${regions(k.last)}` : ""]),
                  ["A notice that is not a call: the last day", s.lastOther ? s.lastOther.fig : "none held", s.lastOther ? `${types(s.lastOther)}${regions(s.lastOther)}` : ""],
                  ...(s.lastOther ? [[`Days with a notice that is not a call in ${s.year}`, s.otherDays, ""]] : []),
                ] as FileCell[][])} />
              <p className="text-xs text-muted">
                ercot_grid_notices (Electric Reliability Council of Texas, ERCOT: its news releases since 2011 and its control room&apos;s operations messages,
                which ERCOT serves for six months, since May 2026): one row per notice and Central day it covers. Before May 2026 a notice is held only where a
                news release announced it, so a day may have had one the table does not hold. A call is a system-wide call on supply or demand, as
                grid_stress_days counts it. <Link href="/data/methods/ercot_grid_notices">Method: ERCOT&apos;s grid notices</Link>
              </p>
            </div>
          );
        })()}
      </ToolSection>
    </div>
  );
}
