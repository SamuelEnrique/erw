// Energy Research Warehouse (ERW) site, session 1403 (chain 100): the cleanest hours, live, `grid_cleanweek_<grid>`, on
// the Clean tab beside the committed "the cleanest hours of the average day" (components/mix/views.tsx CleanView, from
// site/data/clean/<grid>.json). The newest 7 local days of carbon_intensity_hourly (intensity_generation, kg CO2 per
// MWh of the grid's own generation) for the grid, in the committed view's shape: the hour of day across (local clock
// time in the committed file's time zone), the day down, drawn by the shared HeatChart with the hour, the day and the kg
// per MWh on hover (lib/cleanWeek.ts). Under it, keyed: the hours held, the week's cleanest and dirtiest hours and its
// mean; then a line setting the week against the committed average day of its month, in words (hours only). A grid
// whose hourly intensity is held reads "license needed" (lib/gridHeld.ts heldCarbon; no grid is held today). A failed
// read says "could not be read" (session 1181's rule). Its file (session 1182), anchor (1183) and method (1184).
import { HeatChart } from "@/components/svgchart";
import { Num } from "@/components/Num";
import { Missing } from "@/components/mix/Now";
import { PanelFile } from "@/components/grid/PanelFile";
import { SiteLink } from "@/components/SiteLink";
import { shown } from "@/lib/format";
import { gridHref } from "@/lib/gridtool";
import { cleanWeekAnchor, METHOD_CLEAN_WEEK } from "@/lib/gridAnchors";
import { heldCarbon } from "@/lib/gridHeld";
import { CAISO_JOIN, caisoJoinDay } from "@/lib/caisoJoin";
import { LICENSE_NEEDED, licenseHeldRow, licenseTitle } from "@/lib/license";
import { HOURS } from "@/lib/mixpage";
import * as clean from "@/lib/clean";
import { CARBON_TABLE, CLEAN_VARIABLE, UNIT, READ_DAYS, compareWords, dayLabel, dirtiestOf, hourWords, refMonth, utcName, type CleanWeek, type Fig } from "@/lib/cleanWeek";

type Read = { ok: true; data: unknown[] } | { ok: false; reason: string } | null;

/** A figure with its key and its one-line source as the hover tip. */
function F({ f }: { f: Fig }) {
  return (
    <span title={f.tip} className="cursor-help border-b border-dotted border-muted">
      <Num check={f.check} raw={f.raw}>{shown(f.raw)}</Num>
    </span>
  );
}

const monthWords = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });

/** The line under the figures: the week against the committed average day of its month, or why it is not set against it. */
function Compare({ grid, name, week, file, year }: { grid: string; name: string; week: CleanWeek; file: clean.GridFile; year: string | null }) {
  if (licenseHeldRow(clean.SUMMARY, `iso:${grid}`)) {
    return <p className="mb-1 max-w-3xl text-sm" data-cleanweek-compare="held">Against the committed average day: <Missing why={licenseTitle(clean.SUMMARY)} words={LICENSE_NEEDED} /> ({name}&apos;s committed figures of {clean.SUMMARY} are held, so the week is not set against them).</p>;
  }
  const m = refMonth(Object.keys(file.months), week.days[6], year);
  if (!m) return <p className="mb-1 max-w-3xl text-sm" data-cleanweek-compare="none">The committed build holds no {new Date(`${week.days[6]}T12:00:00Z`).toLocaleString("en-US", { month: "long", timeZone: "UTC" })} for {name}, so the week is not set against an average day.</p>;
  const cleanest = clean.cleanestOf(file, m);
  const words = compareWords(week, { month: m, cleanest, dirtiest: dirtiestOf(clean.dayOf(file, m)), hoursName: clean.hoursName(cleanest) });
  const join = grid === "caiso" && Date.parse(`${m}-01T00:00:00Z`) < Date.parse(CAISO_JOIN) && week.t0 >= Date.parse(CAISO_JOIN)
    ? ` California across the join of ${caisoJoinDay()} is two series: the week rests on CAISO's own supply by fuel, ${monthWords(m)}'s average day on EIA-930's.` : "";
  return <p className="mb-1 max-w-3xl text-sm" data-cleanweek-compare={m}>{words}{join} <span className="text-xs text-muted">The average day is ranked by carbon-free share (higher is cleaner), the week by kg CO2 per MWh (lower is cleaner): the hours compare, the figures do not.</span></p>;
}

export function CleanWeekPanel({ grid, name, i, read, week, file, year }: {
  grid: string;
  name: string;
  /** the grid's place among the grids of the page (its anchor) */
  i: number;
  /** the read of the grid's rows, or null when none was made (a held grid) */
  read: Read;
  /** the week's cells and figures, or null when no local day of the read is whole */
  week: CleanWeek | null;
  /** the committed file the view beside it draws */
  file: clean.GridFile;
  /** the year the committed view shows */
  year: string | null;
}) {
  const id = cleanWeekAnchor(i, grid);
  const panel = `grid_cleanweek_${grid}`;
  const method = <p className="mt-1 text-xs text-muted" data-grid-method="clean-week"><SiteLink href={METHOD_CLEAN_WEEK}>Method: the cleanest hours, live</SiteLink>.</p>;
  const held = heldCarbon(grid);
  if (held) {
    return (
      <div id={id} className="mb-2" data-grid-panel={panel}>
        <p className="max-w-3xl text-sm" data-cleanweek-held={held.words}>{name}, the last 7 days of {CARBON_TABLE}: <Missing why={held.why} words={held.words} /></p>
      </div>
    );
  }
  if (!read || !read.ok) {
    return (
      <div id={id} className="mb-2" data-grid-panel={panel}>
        <p className="max-w-3xl text-sm" data-cleanweek-unread={CARBON_TABLE}>{name}, the last 7 days of {CARBON_TABLE}: <Missing words="could not be read" why={`${CARBON_TABLE} could not be read just now: ${read ? read.reason : "no read"}`} />.</p>
        {method}
      </div>
    );
  }
  if (!week || !week.min || !week.max || !week.mean) {
    return (
      <div id={id} className="mb-2" data-grid-panel={panel}>
        <p className="max-w-3xl text-sm" data-cleanweek-none="1">{name}, the last 7 days of {CARBON_TABLE}: no local day of the last {READ_DAYS} holds all its hours, so no 7 days are drawn.</p>
        {method}
      </div>
    );
  }
  const days = `${dayLabel(week.days[0])} to ${dayLabel(week.days[6])} (${week.tz.replace("_", " ")} clock time; ${utcName(week.t0)} to ${utcName(week.t1)})`;
  return (
    <div id={id} className="mb-2" data-grid-panel={panel}>
      <div data-chart="heat">
        <HeatChart id={`erw-grid-cleanweek-${grid}`} rows={week.days.map(dayLabel)} cols={HOURS} cells={week.cells} tips={week.tips} unit={UNIT}
          label={`${name}, carbon intensity of generation by local hour, ${days}`} marks={[week.min.at]} legend={["cleaner", "dirtier"]} />
      </div>
      <p className="mb-1 max-w-3xl text-sm" data-cleanweek-figures="1">
        {days}: <F f={week.n} /> of {week.of} hours held. The week&apos;s cleanest hour <F f={week.min.fig} /> {UNIT}, {hourWords(week.min.t, week.tz)}, marked; its dirtiest <F f={week.max.fig} /> {UNIT}, {hourWords(week.max.t, week.tz)}; the mean of the hours held <F f={week.mean} /> {UNIT}.
      </p>
      <Compare grid={grid} name={name} week={week} file={file} year={year} />
      <p className="mb-1 text-xs text-muted">Each cell is one hour of {CARBON_TABLE} ({week.entity}, {CLEAN_VARIABLE}: the CO2 of the power made in the grid over its net generation), darker where dirtier; a hatched cell is not held. Hover a cell for its hour, its day and its kg per MWh.</p>
      <PanelFile of={{ panel, title: `${name}: the cleanest and dirtiest hours of the last 7 days, carbon intensity of generation`, page: gridHref(grid, "clean"),
        tables: [`${CARBON_TABLE} (derived from EIA's hourly CO2 estimates for EIA-930 over EIA-930's net generation: docs/methods/emissions.md), ${CLEAN_VARIABLE}, kg CO2 per MWh`],
        filter: `${week.entity}, ${CLEAN_VARIABLE}: each hour once`,
        window: `Window: ${days}, the 7 local days to the newest local day whose hours are all held`,
        notes: [`The window holds ${week.of} hours; the hours' own values are drawn in the chart, not written here`] }}
        columns={["Figure", "Value", "Unit"]}
        rows={[
          ["Hours held", <F key="n" f={week.n} />, "hours"],
          [`Cleanest hour, from ${utcName(week.min.t)}`, <F key="lo" f={week.min.fig} />, UNIT],
          [`Dirtiest hour, from ${utcName(week.max.t)}`, <F key="hi" f={week.max.fig} />, UNIT],
          ["Mean of the hours held", <F key="m" f={week.mean} />, UNIT],
        ]} />
      {method}
    </div>
  );
}
