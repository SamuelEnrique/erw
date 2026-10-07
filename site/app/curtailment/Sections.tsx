// Energy Research Warehouse (ERW) site, session 144: three sections of the one curtailment page (/curtailment), drawn
// on the server from the site's own files: "Where free energy is" (data/curtailment/free_energy.json), "What it is
// worth" (worth.json) and Texas, the days held (ercot.json). Every number is a figure of a file, marked data-n so that
// scripts/check-curtailment.mjs can hold the page to the file; a figure a file does not hold is a short placeholder
// with the file's own reason on hover, never a number. The rules behind the figures are in the Method note
// (docs/methods/curtailment.md), not here.
import Link from "next/link";
import type { ReactNode } from "react";
import { ChartFrame, HeadlineNumber, HeadlineRow, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { GRIDS, basisName, dayName, link, monthName, placeName, two, usd, whole, type Choice } from "@/lib/curtailment";
import {
  batteryFill, cellText, hasGap, hourName, isHeld, ranked, shade, summaryPairs,
  type FreeFile, type Gap, type Held, type Loc, type NotHeld, type WindowName,
} from "@/lib/freeenergy";
import { Heat, XY } from "./Charts";

export const N = ({ k, children }: { k: string; children: string }) => <span data-n={k}>{children}</span>;
/** A figure that is not held: a few words, and the reason on hover. Never a number. */
export const Blank = ({ words = "not held yet", why }: { words?: string; why: string }) => (
  <span className="cursor-help text-muted underline decoration-dotted underline-offset-2" data-missing="1" title={why}>{words}</span>
);
const item = (on: boolean) => `no-underline ${on ? "font-semibold text-accent" : "text-ink hover:text-accent"}`;
const WINDOWS: { id: WindowName; label: string }[] = [{ id: "year", label: "Last twelve months" }, { id: "month", label: "Last month" }];
const COUNTED = "Hours priced under USD 5 per MWh. The hours below zero are among them: each hour is counted once.";

// ---- where free energy is ----------------------------------------------------------------------------------------

/** The place the section shows: the one the address names when the grid holds it, else the grid's place with the most
 * hours under USD 5 in the window (the last twelve months when two or more places hold them, else the last month). */
export function freeChoice(f: FreeFile, c: Choice): { win: WindowName; place: Loc | null } {
  const g = f.grids[c.grid];
  if (!g) return { win: "year", place: null };
  const win: WindowName = c.win ?? (ranked(g, "year").length >= 2 ? "year" : "month");
  const named = g.locations.find((l) => l.id === c.place);
  return { win, place: named ?? ranked(g, win)[0] ?? ranked(g, win === "year" ? "month" : "year")[0] ?? g.locations[0] ?? null };
}

function GapNumber({ g, k, label }: { g: Gap; k: string; label: string }) {
  return (
    <HeadlineNumber label={label} unit={hasGap(g) ? "USD per MWh" : undefined}
      value={hasGap(g) ? <N k={`gap|${k}`}>{two(g.gap)}</N> : <Blank why={g.missing} />}
      note={hasGap(g) ? <>{placeName(g.cheapest.id)} at <N k={`gap|${k}|cheapest`}>{two(g.cheapest.mean)}</N>, {placeName(g.dearest.id)} at <N k={`gap|${k}|dearest`}>{two(g.dearest.mean)}</N>: mean {basisName(g.basis)} price over the {whole(g.hours_common)} hours all {g.places.length} places hold.</> : undefined} />
  );
}

export function FreeEnergy({ file, c }: { file: FreeFile; c: Choice }) {
  const g = file.grids[c.grid];
  const { win, place } = freeChoice(file, c);
  const pairs = summaryPairs(file, "year"), last = summaryPairs(file, "month");
  const tw = file.compare.west_texas_houston, ca = file.compare.california_north_south;
  const why = (x: { zone?: { year: object }; hub?: { year: object } } | undefined) => { const p = (x?.hub?.year ?? x?.zone?.year) as { missing?: string } | undefined; return p?.missing ?? "the pair is not in the file"; };
  const endName = monthName(file.end_month);
  return (
    <ToolSection title="Where free energy is" id="free-energy">
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-free-summary="1">
        Over the twelve months to {endName},{" "}
        {pairs.texas ? <>the West Texas {pairs.texas.kind === "zone" ? "load zone" : "hub"} was priced under USD {file.threshold_usd_per_mwh} per MWh in <N k="pair|texas|west|under5">{whole(pairs.texas.west.under5)}</N> hours, <N k="pair|texas|west|negative">{whole(pairs.texas.west.negative)}</N> of them below zero, against Houston&apos;s <N k="pair|texas|houston|under5">{whole(pairs.texas.houston.under5)}</N></>
          : <>West Texas against Houston is <Blank why={why(tw)} /></>};{" "}
        {pairs.california ? <>California&apos;s south (SP15) had <N k="pair|california|south|under5">{whole(pairs.california.south.under5)}</N> such hours, <N k="pair|california|south|negative">{whole(pairs.california.south.negative)}</N> below zero, against the north&apos;s (NP15) <N k="pair|california|north|under5">{whole(pairs.california.north.under5)}</N></>
          : <>California north against south is <Blank why={why(ca)} /></>}.
        {last.texas && last.california ? <> In {endName} alone: West Texas <N k="pair|texas|west|month">{whole(last.texas.west.under5)}</N>, Houston <N k="pair|texas|houston|month">{whole(last.texas.houston.under5)}</N>; SP15 <N k="pair|california|south|month">{whole(last.california.south.under5)}</N>, NP15 <N k="pair|california|north|month">{whole(last.california.north.under5)}</N>.</> : null}
      </p>
      {!g || !place ? <p className="border border-rule bg-paper px-3 py-2 text-sm" role="status">No price of this grid is in the file.</p> : (
        <>
          <HeadlineRow>
            {(() => {
              const top = ranked(g, win)[0];
              return <HeadlineNumber label={`Most hours under USD ${file.threshold_usd_per_mwh}, ${win === "year" ? "last twelve months" : endName}`} unit={top ? "hours" : undefined}
                value={top ? <N k={`top|${win}`}>{whole(top.win.under5)}</N> : <Blank why="no place of this grid holds 95 percent of the window's hours" />}
                note={top ? <>{placeName(top.id)}, {g.name}: <N k={`top|${win}|negative`}>{whole(top.win.negative)}</N> of them below zero, of {whole(top.win.hours_held)} hours held, {basisName(top.win.basis)}.</> : undefined} />;
            })()}
            <GapNumber g={g.gap.year} k="year" label="Cheapest against dearest place, last twelve months" />
            <GapNumber g={g.gap.month} k="month" label={`Cheapest against dearest place, ${endName}`} />
          </HeadlineRow>

          <figure className="mb-10" data-schematic="1">
            <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
              <span className="font-serif text-xl text-accent">{g.name}: its hubs and zones, shaded by their hours under USD {file.threshold_usd_per_mwh}</span>
              <span className="flex gap-x-3 text-xs">{WINDOWS.map((w) => <Link key={w.id} href={link({ ...c, place: place.id, win: w.id }, "free-energy")} scroll={false} aria-current={w.id === win ? "true" : undefined} className={item(w.id === win)}>{w.label}</Link>)}</span>
            </figcaption>
            {(() => {
              const order = [...ranked(g, win), ...g.locations.filter((l) => l.kind !== "average" && !isHeld(l[win]))];
              const most = Math.max(0, ...ranked(g, win).map((l) => l.win.under5));
              return (
                <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-4 lg:grid-cols-6">
                  {order.map((l) => {
                    const w = l[win], held = isHeld(w), s = held ? shade((w as Held).under5, most) : 0;
                    const text = held ? `${placeName(l.id)}: ${whole((w as Held).under5)} hours under USD ${file.threshold_usd_per_mwh}, ${whole((w as Held).negative)} of them below zero, of ${whole((w as Held).hours_held)} held, ${basisName((w as Held).basis)}` : `${placeName(l.id)}: not held yet. ${(w as NotHeld).missing}`;
                    return (
                      <Link key={l.id} href={link({ ...c, place: l.id, win }, "free-energy")} scroll={false} title={text} data-tile={l.id} data-count={held ? (w as Held).under5 : ""} aria-current={l.id === place.id ? "true" : undefined}
                        className={`block border px-2 py-2 text-xs no-underline ${l.id === place.id ? "border-ink ring-1 ring-ink" : "border-rule"} ${held ? "" : "bg-paper text-muted"}`}
                        style={held ? { background: `rgba(140, 21, 21, ${(0.06 + 0.84 * s).toFixed(3)})`, color: s > 0.5 ? "#fff" : "var(--color-ink)" } : undefined}>
                        <span className="block font-semibold">{placeName(l.id)}</span>
                        <span className="block tabular-nums">{held ? `${whole((w as Held).under5)} hours` : "not held yet"}</span>
                      </Link>
                    );
                  })}
                </div>
              );
            })()}
            <p className="mt-2 max-w-3xl text-xs text-muted">A schematic, not a map: the tiles are in order of their count, not placed by geography. Choose a tile for its hours below.</p>
          </figure>

          <ChartFrame title={`${placeName(place.id)}: hours under USD ${file.threshold_usd_per_mwh}, by hour of the day and month`}
            note={<>{g.std_name}, {basisName(place.heat.basis)} prices.{" "}
              {place.heat.whole ? <><N k="heat|under5">{whole(place.heat.under5.flat().reduce((a, v) => a + v, 0))}</N> hours in all, <N k="heat|negative">{whole(place.heat.negative.flat().reduce((a, v) => a + v, 0))}</N> of them below zero.</>
                : <Blank words={`${whole(place.heat.hours_held)} of the twelve months' hours held`} why={isHeld(place.year) ? "part of the window is held" : (place.year as NotHeld).missing} />}</>}>
            <Heat id="free-heat" hours={Array.from({ length: 24 }, (_, h) => hourName(h))} months={file.year_months} most={Math.max(0, ...place.heat.under5.flat())}
              values={place.heat.held.map((row, m) => row.map((held, h) => (held ? place.heat.under5[m][h] : null)))}
              tips={place.heat.held.map((row, m) => row.map((_, h) => `${placeName(place.id)}. ${cellText(place.heat, file.year_months, m, h)}`))}
              label={`${g.name}, ${placeName(place.id)}: hours under USD ${file.threshold_usd_per_mwh} per MWh by hour of the day and month`} />
          </ChartFrame>

          <ToolTable minWidth={720} caption={`${g.name}: hours under USD ${file.threshold_usd_per_mwh} per MWh and below zero, by hub and zone`}
            head={["Hub or zone", <span key="a" title={COUNTED} className="cursor-help underline decoration-dotted">{endName}: under USD {file.threshold_usd_per_mwh}</span>, "below zero",
              <span key="b" title={COUNTED} className="cursor-help underline decoration-dotted">Twelve months: under USD {file.threshold_usd_per_mwh}</span>, "below zero", "Mean price, USD per MWh"]}
            rows={g.locations.map((l) => {
              const cells = (w: WindowName): ReactNode[] => { const x = l[w]; return isHeld(x) ? [<N key="u" k={`loc|${l.id}|${w}|under5`}>{whole(x.under5)}</N>, <N key="n" k={`loc|${l.id}|${w}|negative`}>{whole(x.negative)}</N>] : [<Blank key="u" why={x.missing} />, ""]; };
              const y = l.year, m = l.month;
              return { key: l.id, highlight: l.id === place.id, muted: l.kind === "average",
                cells: [<Link key="p" href={link({ ...c, place: l.id, win }, "free-energy")} scroll={false} className="text-ink" title={`${l.entity}, ${l.kind === "average" ? "an average of hubs" : l.kind}`}>{placeName(l.id)}</Link>, ...cells("month"), ...cells("year"),
                  isHeld(y) ? <span key="m" title="Last twelve months"><N k={`loc|${l.id}|year|mean`}>{two(y.mean)}</N></span> : isHeld(m) ? <span key="m" title={`${endName} only`}><N k={`loc|${l.id}|month|mean`}>{two(m.mean)}</N></span> : ""] };
            })} />
          <p className="mt-2 max-w-3xl text-xs text-muted">The other grids: {GRIDS.filter((x) => x.id !== c.grid).map((x, i) => <span key={x.id}>{i ? ", " : ""}{x.open ? <Link href={link({ grid: x.id, dur: c.dur }, "free-energy")} className="text-ink">{x.name}</Link> : <>{x.name} ({x.words})</>}</span>)}.</p>
        </>
      )}
    </ToolSection>
  );
}

// ---- what it is worth --------------------------------------------------------------------------------------------

type Dur = Record<string, number>;
type Val = {
  months?: number; hours?: number; hours_priced: number; hours_curtailed_priced: number; curtailed_mwh?: number; curtailed_mwh_priced: number; value_usd: number; usd_per_mwh_curtailed: number;
  share_mwh_negative_pct: number; share_mwh_under5_pct: number; price_all_hours_mean: number; price_curtailed_hours_mean: number; days_held?: number; days_in_month?: number;
  first_hour_priced?: string; last_hour_priced?: string;
};
type Side = { freq?: string; tables?: string[]; first_month_held?: string; months?: Record<string, Val>; years?: Record<string, Val>; window?: Val; missing?: string | Record<string, string> };
type Fleet = { battery_days_held?: number; fleet_peak_charging_mw?: number; fleet_charged_in_curtailed_hours_mwh: number; absorb_fleet_mwh: Dur; absorbable_pct_of_fleet_charged: Dur };
type Bat = { months?: number; days_held?: number; days_in_month?: number; curtailed_mwh: number; absorb_mwh_per_mw: Dur; fleet?: Fleet; fleet_missing?: string };
type WorthGrid = {
  name: string; whose: string; table: string; main_hub?: string; missing?: string; hubs?: Record<string, Record<string, Side>>;
  battery?: { months?: Record<string, Bat>; years?: Record<string, Bat>; window?: { days: number; first_day: string; last_day: string; below_hsl_mwh: number; absorb_mwh_per_mw: Dur }; fleet_missing?: string };
  hours_held?: number; below_hsl_mwh?: number; months_missing?: string; first_hour?: string; last_hour?: string;
};
export type WorthFile = { built: string; durations_hours: number[]; rules: Record<string, string>; grids: Record<string, WorthGrid>; blank: Record<string, { name: string; words: string }>; not_held: Record<string, string> };

/** The period the worth is shown for: the page's own when the hub's prices hold it, else the newest year they hold. */
export function worthPeriod(side: Side | undefined, period: string | null): string | null {
  if (!side?.years) return null;
  if (period && (period.length === 7 ? side.months?.[period] : side.years[period])) return period;
  return Object.keys(side.years).sort().at(-1) ?? null;
}
const valOf = (side: Side | undefined, p: string | null): Val | null => (!side || !p ? null : (p.length === 7 ? side.months?.[p] : side.years?.[p]) ?? null);
const batOf = (g: WorthGrid, p: string | null): Bat | null => (!p ? null : (p.length === 7 ? g.battery?.months?.[p] : g.battery?.years?.[p]) ?? null);
const daysOf = (g: WorthGrid, p: string): number => (p.length === 7 ? g.battery?.months?.[p]?.days_held ?? 0 : Object.entries(g.battery?.months ?? {}).filter(([m]) => m.startsWith(`${p}-`)).reduce((a, [, r]) => a + (r.days_held ?? 0), 0));
const MARKET: Record<string, string> = { rt: "real time", da: "day-ahead" };
const periodWords = (p: string) => (p.length === 7 ? monthName(p) : p);

function HubTable({ g, grid, pick, caption }: { g: WorthGrid; grid: string; pick: (s: Side) => Val | null; caption: string }) {
  const rows = Object.entries(g.hubs ?? {}).flatMap(([hub, sides]) => Object.entries(sides).map(([mk, side]) => ({ hub, mk, v: pick(side), side })));
  return (
    <ToolTable minWidth={760} caption={caption}
      head={["Hub and market", "Value, USD", "USD per MWh curtailed", <span key="n" title="Of the MWh with a price">In hours below zero, percent</span>, <span key="u" title={COUNTED}>In hours under USD 5, percent</span>,
        <span key="f" title="The mean price of the hours with any curtailment: what a flat load running only then paid">A flat load in those hours, USD per MWh</span>, <span key="a" title="The mean price of every hour held">In all hours</span>]}
      rows={rows.map(({ hub, mk, v, side }) => {
        const k = `worth|${grid}|${hub}|${mk}`;
        return v ? { key: `${hub}${mk}`, highlight: hub === g.main_hub && mk === "rt",
          cells: [<span key="h" title={`${whole(v.hours_curtailed_priced)} hours with a price`}>{placeName(hub)}, {MARKET[mk]}</span>, <N key="v" k={`${k}|value`}>{usd(v.value_usd)}</N>, <N key="p" k={`${k}|per`}>{two(v.usd_per_mwh_curtailed)}</N>, <N key="n" k={`${k}|neg`}>{two(v.share_mwh_negative_pct)}</N>,
            <N key="u" k={`${k}|under5`}>{two(v.share_mwh_under5_pct)}</N>, <N key="f" k={`${k}|flat`}>{two(v.price_curtailed_hours_mean)}</N>, <N key="a" k={`${k}|all`}>{two(v.price_all_hours_mean)}</N>] }
          : { key: `${hub}${mk}`, cells: [`${placeName(hub)}, ${MARKET[mk]}`], wide: <Blank why={typeof side.missing === "string" ? side.missing : "the hub's prices do not hold this period"} /> };
      })} />
  );
}

export function Worth({ file, c, estimate }: { file: WorthFile; c: Choice; estimate: string }) {
  const g = file.grids[c.grid];
  const dur = String(c.dur);
  const durLinks = <span className="flex gap-x-3 text-xs">{file.durations_hours.map((d) => <Link key={d} href={link({ ...c, dur: d as 2 | 4 | 8 }, "worth")} scroll={false} aria-current={d === c.dur ? "true" : undefined} className={item(d === c.dur)} data-dur={d}>{d} hours</Link>)}</span>;
  const caisoSide = file.grids.caiso?.hubs?.[file.grids.caiso.main_hub ?? ""]?.rt;
  const across = (
    <ToolTable minWidth={720} caption="What curtailed energy is worth, grid by grid" words
      head={["Grid", "Curtailed energy at the hub's prices", `A ${dur}-hour battery against what the fleet charged`]}
      rows={GRIDS.map((x) => {
        const w = file.grids[x.id];
        if (!x.open) return { key: x.id, muted: true, cells: [x.name], wide: <span data-blank={x.id}>{file.blank[x.id]?.words ?? x.words}</span> };
        if (x.id === "caiso" && w && caisoSide) {
          const p = worthPeriod(caisoSide, null)!, v = valOf(caisoSide, p)!, b = batOf(w, p);
          return { key: x.id, cells: [x.name, <span key="v" className="block text-left">USD <N k="across|caiso|value">{usd(v.value_usd)}</N> in {p}, <N k="across|caiso|per">{two(v.usd_per_mwh_curtailed)}</N> per MWh, at {placeName(w.main_hub ?? "")}</span>,
            <span key="b" className="block text-left">{b?.fleet ? <><N k={`across|caiso|share|${dur}`}>{two(b.fleet.absorbable_pct_of_fleet_charged[dur])}</N> percent, {p}</> : <Blank why={b?.fleet_missing ?? "the fleet is not held for this period"} />}</span>] };
        }
        if (x.id === "ercot" && w?.hubs) {
          const v = w.hubs[w.main_hub ?? ""]?.rt?.window;
          return { key: x.id, cells: [x.name, <span key="v" className="block text-left">{v ? <>USD <N k="across|ercot|value">{usd(v.value_usd)}</N> over {whole(v.hours_priced)} hours, <N k="across|ercot|per">{two(v.usd_per_mwh_curtailed)}</N> per MWh, at {placeName(w.main_hub ?? "")}: the ERW&apos;s estimate</> : <Blank why="no price is held for these hours" />}</span>,
            <span key="b" className="block text-left"><Blank why={w.battery?.fleet_missing ?? "no fleet figure is held"} /></span>] };
        }
        return { key: x.id, cells: [x.name], wide: <Blank words={w?.missing ? "not held yet" : "not held"} why={w?.missing ?? file.not_held[x.id] ?? "no hourly curtailment series is held"} /> };
      })} />
  );

  if (c.grid === "caiso" && g?.hubs && caisoSide) {
    const p = worthPeriod(caisoSide, c.period)!, v = valOf(caisoSide, p)!, b = batOf(g, p), days = daysOf(g, p);
    const ms = Object.keys(caisoSide.months ?? {}).sort();
    const fm = Object.keys(g.battery?.months ?? {}).sort().filter((m) => g.battery!.months![m].fleet);
    const fill = b ? batteryFill(b.absorb_mwh_per_mw[dur], c.dur, days) : null;
    return (
      <ToolSection title="What it is worth" id="worth">
        <HeadlineRow>
          <HeadlineNumber label={`Curtailed energy at ${placeName(g.main_hub ?? "")} prices, ${periodWords(p)}`} value={<>USD <N k="worth|value">{usd(v.value_usd)}</N></>}
            note={<>USD <N k="worth|per">{two(v.usd_per_mwh_curtailed)}</N> per MWh curtailed, over <N k="worth|mwh">{whole(v.curtailed_mwh_priced)}</N> MWh, each hour at its real-time price{v.months ? `, ${v.months} months` : ""}.</>} />
          <HeadlineNumber label="Curtailed in hours priced below zero" value={<N k="worth|neg">{two(v.share_mwh_negative_pct)}</N>} unit="percent"
            note={<><N k="worth|under5">{two(v.share_mwh_under5_pct)}</N> percent in hours under USD 5, the hours below zero among them.</>} />
          <HeadlineNumber label="A flat load in those hours paid" value={<N k="worth|flat">{two(v.price_curtailed_hours_mean)}</N>} unit="USD per MWh"
            note={<>Against <N k="worth|all">{two(v.price_all_hours_mean)}</N> in every hour of {periodWords(p)}: the mean price of the <N k="worth|hours">{whole(v.hours_curtailed_priced)}</N> hours with any curtailment.</>} />
        </HeadlineRow>
        <ChartFrame title={`Value of curtailed energy by month, at ${placeName(g.main_hub ?? "")} real-time prices`} legend={[{ label: "Value, USD", color: "var(--color-accent)" }, { label: "USD per MWh curtailed", color: "var(--color-ink)" }]}>
          <XY id="worth-months" x={ms} unit="USD" unit2="USD/MWh" label="California: the value of curtailed wind and solar by month at the hub's real-time prices"
            series={[{ name: "Value", color: "var(--color-accent)", values: ms.map((m) => caisoSide.months![m].value_usd), unit: "USD" },
              { name: "Per MWh curtailed", color: "var(--color-ink)", kind: "line", axis: 1, digits: 2, values: ms.map((m) => caisoSide.months![m].usd_per_mwh_curtailed), unit: "USD/MWh" }]}
            notes={ms.map((m) => `${two(caisoSide.months![m].share_mwh_negative_pct)} percent of it in hours below zero`)} dim={ms.map((m) => !(m === p || m.startsWith(`${p}-`)))} />
        </ChartFrame>
        <HubTable g={g} grid="caiso" pick={(s) => valOf(s, p)} caption={`California, ${periodWords(p)}: curtailed energy valued at each hub and market`} />

        <div className="mt-10" id="battery-rule">
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-x-6 border-b border-rule pb-1"><h3 className="font-serif text-lg text-accent">A battery of {dur} hours, against what the fleet charged</h3>{durLinks}</div>
          <HeadlineRow>
            <HeadlineNumber label={`A ${dur}-hour battery could have taken in, ${periodWords(p)}`} value={b ? <N k="bat|per_mw">{whole(b.absorb_mwh_per_mw[dur])}</N> : <Blank why="the period is not held" />} unit={b ? "MWh per MW" : undefined}
              note={b && fill !== null ? <><N k="bat|fill">{two(fill)}</N> percent of one full charge a day over the <N k="bat|days">{whole(days)}</N> days held.</> : undefined} />
            <HeadlineNumber label="The fleet charged in the curtailed hours" value={b?.fleet ? <N k="bat|fleet">{whole(b.fleet.fleet_charged_in_curtailed_hours_mwh)}</N> : <Blank why={b?.fleet_missing ?? "the fleet is not held for this period"} />} unit={b?.fleet ? "MWh" : undefined}
              note={b ? <>Curtailed in {periodWords(p)}: <N k="bat|curtailed">{whole(b.curtailed_mwh)}</N> MWh.</> : undefined} />
            <HeadlineNumber label={`What a ${dur}-hour fleet could have absorbed, as a share of that`} value={b?.fleet ? <N k="bat|share">{two(b.fleet.absorbable_pct_of_fleet_charged[dur])}</N> : <Blank why={b?.fleet_missing ?? "the fleet is not held for this period"} />} unit={b?.fleet ? "percent" : undefined}
              note={b?.fleet ? <><N k="bat|absorb">{whole(b.fleet.absorb_fleet_mwh[dur])}</N> MWh, at the fleet&apos;s own highest charging rate.</> : undefined} />
          </HeadlineRow>
          <ChartFrame title={`By month: curtailed, what a ${dur}-hour fleet could have absorbed, and what the fleet charged`}
            legend={[{ label: "Curtailed", color: "var(--color-fuel-solar)" }, { label: `A ${dur}-hour fleet could have absorbed`, color: "var(--color-accent)" }, { label: "The fleet charged in those hours", color: "var(--color-fuel-storage)" }]}>
            <XY id="battery-months" x={fm} unit="MWh" label={`California: curtailed energy, what a ${dur}-hour battery fleet could have absorbed and what the fleet charged in the curtailed hours, by month`}
              series={[{ name: "Curtailed", color: "var(--color-fuel-solar)", values: fm.map((m) => g.battery!.months![m].curtailed_mwh) },
                { name: `A ${dur}-hour fleet could have absorbed`, color: "var(--color-accent)", values: fm.map((m) => g.battery!.months![m].fleet!.absorb_fleet_mwh[dur]) },
                { name: "The fleet charged in those hours", color: "var(--color-fuel-storage)", values: fm.map((m) => g.battery!.months![m].fleet!.fleet_charged_in_curtailed_hours_mwh) }]}
              notes={fm.map((m) => `${two(g.battery!.months![m].fleet!.absorbable_pct_of_fleet_charged[dur])} percent of what the fleet charged`)} />
          </ChartFrame>
          <ToolTable minWidth={680} caption={`California, ${periodWords(p)}: a battery of 2, 4 or 8 hours against what the fleet charged`}
            head={["Battery", "Could have taken in, MWh per MW", "A fleet that size, MWh", "The fleet charged in those hours, MWh", "As a share, percent"]}
            rows={file.durations_hours.map((d) => ({ key: String(d), highlight: d === c.dur, cells: [`${d} hours`, b ? <N key="a" k={`bat|${d}|per_mw`}>{whole(b.absorb_mwh_per_mw[String(d)])}</N> : "",
              b?.fleet ? <N key="f" k={`bat|${d}|absorb`}>{whole(b.fleet.absorb_fleet_mwh[String(d)])}</N> : <Blank key="f" why={b?.fleet_missing ?? "not held"} />,
              b?.fleet ? <N key="c" k={`bat|${d}|fleet`}>{whole(b.fleet.fleet_charged_in_curtailed_hours_mwh)}</N> : "", b?.fleet ? <N key="s" k={`bat|${d}|share`}>{two(b.fleet.absorbable_pct_of_fleet_charged[String(d)])}</N> : ""] }))} />
        </div>
        <div className="mt-10"><h3 className="mb-3 border-b border-rule pb-1 font-serif text-lg text-accent">Grid by grid</h3>{across}</div>
      </ToolSection>
    );
  }

  if (c.grid === "ercot" && g?.hubs) {
    const v = g.hubs[g.main_hub ?? ""]?.rt?.window ?? null, bw = g.battery?.window;
    return (
      <ToolSection title="What it is worth" id="worth">
        <p className="mb-4 max-w-3xl text-sm" data-estimate="1">{estimate}{g.first_hour && g.last_hour ? ` The ${whole(g.hours_held ?? 0)} hours held, ${dayName(g.first_hour.slice(0, 10))} to ${dayName(g.last_hour.slice(0, 10))}.` : ""}</p>
        <HeadlineRow>
          <HeadlineNumber label={`Output below the limit at ${placeName(g.main_hub ?? "")} prices`} value={v ? <>USD <N k="worth|value">{usd(v.value_usd)}</N></> : <Blank why="no price is held for these hours" />}
            note={v ? <>USD <N k="worth|per">{two(v.usd_per_mwh_curtailed)}</N> per MWh over the <N k="worth|hours">{whole(v.hours_priced)}</N> of {whole(v.hours ?? 0)} hours with a real-time price.</> : undefined} />
          <HeadlineNumber label="A month's worth" value={<Blank why={g.months_missing ?? "no whole month is held"} />} />
          <HeadlineNumber label={`A ${dur}-hour battery could have taken in`} value={bw ? <N k="bat|per_mw">{whole(bw.absorb_mwh_per_mw[dur])}</N> : <Blank why="no whole day is held" />} unit={bw ? "MWh per MW" : undefined}
            note={bw ? <>Over the <N k="bat|days">{whole(bw.days)}</N> whole days held. Against what the fleet charged: <Blank why={g.battery?.fleet_missing ?? "no fleet figure is held"} />.</> : undefined} />
        </HeadlineRow>
        <div className="mb-3 flex justify-end">{durLinks}</div>
        <HubTable g={g} grid="ercot" pick={(s) => s.window ?? null} caption="Texas: output below the limit valued at each hub and market, over the hours held" />
        <div className="mt-10"><h3 className="mb-3 border-b border-rule pb-1 font-serif text-lg text-accent">Grid by grid</h3>{across}</div>
      </ToolSection>
    );
  }

  return (
    <ToolSection title="What it is worth" id="worth">
      <HeadlineRow>
        <HeadlineNumber label={`Curtailed energy at the hub's prices, ${g?.name ?? gridName(c.grid)}`} value={<Blank words={g?.missing ? "not held yet" : "not held"} why={g?.missing ?? file.not_held[c.grid] ?? "no hourly curtailment series is held"} />} />
        <HeadlineNumber label="A flat load in those hours" value={<Blank words={g?.missing ? "not held yet" : "not held"} why={g?.missing ?? file.not_held[c.grid] ?? "no hourly curtailment series is held"} />} />
        <HeadlineNumber label={`A ${dur}-hour battery against the fleet`} value={<Blank words={g?.missing ? "not held yet" : "not held"} why={g?.missing ?? file.not_held[c.grid] ?? "no hourly curtailment series is held"} />} />
      </HeadlineRow>
      <h3 className="mb-3 border-b border-rule pb-1 font-serif text-lg text-accent">Grid by grid</h3>{across}
    </ToolSection>
  );
}
const gridName = (id: string) => GRIDS.find((x) => x.id === id)?.name ?? id;

// ---- Texas: the days held ----------------------------------------------------------------------------------------

type Fig = { generation_mwh: number; hsl_mwh: number; below_hsl_mwh: number; above_hsl_mwh?: number; share_pct: number | null };
type Three = { wind: Fig; solar: Fig; both: Fig };
type Region = { id: string; entity: string; hours_held: number; generation_mwh: number; share_of_fuel_pct: number | null };
export type ErcotFile = {
  built: string; tables: string[]; near_hours: number; first_hour: string; last_hour: string; hours_held: number; first_day: string | null; last_day: string | null; whole_days: number;
  hours: { ts: string; local: string; wind_gen: number; wind_hsl: number; solar_gen: number; solar_hsl: number }[];
  days: Record<string, Three & { hours_held: number; hours_in_day: number; whole: boolean }>;
  window: Three; all_hours: Three;
  by_hour_of_day: { hour: number; hours: number; wind_below_mwh: number; wind_above_mwh: number; solar_below_mwh: number; solar_above_mwh: number }[];
  months: Record<string, { hours_held: number; hours_in_month: number; missing?: string; both?: Fig; wind?: Fig; solar?: Fig }>; month_reason: string;
  regions: Record<string, Region[]>; region_limit: string; region_reason: string;
  years: Record<string, { hours_in_year: number; wind_hours_held: number; wind_generation_mwh: number; solar_hours_held: number; solar_generation_mwh: number; whole: boolean }>; year_limit: string; year_reason: string;
  history: string; history_reason: string;
};
const twh = (mwh: number) => (mwh / 1e6).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const WIND = "var(--color-fuel-wind)", SOLAR = "var(--color-fuel-solar)";

export function Texas({ file, estimate }: { file: ErcotFile; estimate: string }) {
  const days = Object.keys(file.days).sort();
  return (
    <ToolSection title="Texas, hour by hour: the days held" id="texas">
      <p className="mb-4 max-w-3xl text-sm" data-estimate="1">{estimate}</p>
      <ChartFrame title="Output against the limit, by hour, MW" legend={[{ label: "Wind output", color: WIND }, { label: "Solar output", color: SOLAR }, { label: "The limit (dashed)", color: "var(--color-muted)" }]}
        note={<>US Central time. <N k="tx|hours">{whole(file.hours_held)}</N> hours held, {file.first_day ? dayName(file.first_day) : ""} to {file.last_day ? dayName(file.last_day) : ""}.</>}>
        <XY id="texas-hours" x={file.hours.map((h) => h.local.slice(5))} unit="MW" zoom label="ERCOT: system-wide wind and solar output against the High Sustained Limit, by hour"
          series={[{ name: "Wind limit", color: WIND, kind: "line", dash: true, values: file.hours.map((h) => h.wind_hsl) }, { name: "Wind output", color: WIND, kind: "line", values: file.hours.map((h) => h.wind_gen) },
            { name: "Solar limit", color: SOLAR, kind: "line", dash: true, values: file.hours.map((h) => h.solar_hsl) }, { name: "Solar output", color: SOLAR, kind: "line", values: file.hours.map((h) => h.solar_gen) }]}
          notes={file.hours.map((h) => `Below the limit: wind ${whole(Math.max(0, h.wind_hsl - h.wind_gen))} MW, solar ${whole(Math.max(0, h.solar_hsl - h.solar_gen))} MW`)} />
      </ChartFrame>
      <ChartFrame title="Below and above the limit, by hour of the day, MWh over the whole days held"
        legend={[{ label: "Wind below", color: WIND }, { label: "Solar below", color: SOLAR }, { label: "Solar above", color: "var(--color-not-reported)" }]}>
        <XY id="texas-pattern" x={file.by_hour_of_day.map((r) => hourName(r.hour))} unit="MWh" label="ERCOT: wind and solar output below and above the High Sustained Limit by hour of the day, over the whole days held"
          series={[{ name: "Wind below the limit", color: WIND, stack: "below", values: file.by_hour_of_day.map((r) => r.wind_below_mwh) }, { name: "Solar below the limit", color: SOLAR, stack: "below", values: file.by_hour_of_day.map((r) => r.solar_below_mwh) },
            { name: "Solar above the limit", color: "var(--color-not-reported)", stack: "above", values: file.by_hour_of_day.map((r) => r.solar_above_mwh) }]}
          notes={file.by_hour_of_day.map((r) => `${r.hours} hours of the day held`)} />
      </ChartFrame>
      <ToolTable minWidth={680} caption="ERCOT: wind and solar output below the High Sustained Limit by day, the ERW's estimate"
        head={["Day", "Wind below the limit, MWh", "Solar below the limit, MWh", "Both, percent of the limit", "Hours held"]}
        rows={[
          ...days.map((d) => { const r = file.days[d]; return { key: d, muted: !r.whole, cells: [dayName(d), <N key="w" k={`tx|${d}|wind`}>{whole(r.wind.below_hsl_mwh)}</N>, <N key="s" k={`tx|${d}|solar`}>{whole(r.solar.below_hsl_mwh)}</N>,
            r.both.share_pct === null ? <Blank key="p" why="the day holds no limit above nothing" /> : <N key="p" k={`tx|${d}|share`}>{two(r.both.share_pct)}</N>, `${r.hours_held} of ${r.hours_in_day}`] }; }),
          { key: "all", highlight: true, cells: [`The ${file.whole_days} whole days`, <N key="w" k="tx|window|wind">{whole(file.window.wind.below_hsl_mwh)}</N>, <N key="s" k="tx|window|solar">{whole(file.window.solar.below_hsl_mwh)}</N>,
            file.window.both.share_pct === null ? "" : <N key="p" k="tx|window|share">{two(file.window.both.share_pct)}</N>, ""] },
          ...Object.keys(file.months).sort().map((m) => { const r = file.months[m]; return r.both ? { key: m, cells: [monthName(m), <N key="w" k={`tx|${m}|wind`}>{whole(r.wind!.below_hsl_mwh)}</N>, <N key="s" k={`tx|${m}|solar`}>{whole(r.solar!.below_hsl_mwh)}</N>, r.both.share_pct === null ? "" : <N key="p" k={`tx|${m}|share`}>{two(r.both.share_pct)}</N>, `${whole(r.hours_held)} of ${whole(r.hours_in_month)}`] }
            : { key: m, cells: [monthName(m)], wide: <span data-month-missing={m}><Blank why={r.missing ?? "the month is not held"} /></span> }; }),
          { key: "history", cells: ["2016 to the first reading"], wide: <span data-history="1"><Blank words={file.history} why={file.history_reason} /></span> },
        ]} />

      <div className="mt-10 grid gap-8 md:grid-cols-2">
        {(["wind", "solar"] as const).map((f) => (
          <div key={f}>
            <ToolTable minWidth={320} caption={`ERCOT: ${f} output by ERCOT's own ${f} regions over the whole days held`}
              head={[`ERCOT's ${f} region`, "Output, MWh", `Share of ${f}, percent`, "Below the limit"]}
              rows={(file.regions[f] ?? []).map((r) => ({ key: r.id, cells: [r.id, <N key="g" k={`tx|region|${f}|${r.id}`}>{whole(r.generation_mwh)}</N>, r.share_of_fuel_pct === null ? "" : <N key="s" k={`tx|region|${f}|${r.id}|share`}>{two(r.share_of_fuel_pct)}</N>,
                <span key="l" data-region-limit={r.id}><Blank words={file.region_limit} why={file.region_reason} /></span>] }))} />
          </div>
        ))}
      </div>
      <div className="mt-10">
        <ToolTable minWidth={520} caption="ERCOT: wind and solar output by year, from ERCOT's yearly workbooks"
          head={["Year", "Wind output, TWh", "Solar output, TWh", "Below the limit"]}
          rows={Object.keys(file.years).sort().map((y) => { const r = file.years[y]; return { key: y, muted: !r.whole, cells: [<span key="y" title={`${whole(r.wind_hours_held)} of ${whole(r.hours_in_year)} hours held`}>{y}</span>, <N key="w" k={`tx|year|${y}|wind`}>{twh(r.wind_generation_mwh)}</N>, <N key="s" k={`tx|year|${y}|solar`}>{twh(r.solar_generation_mwh)}</N>,
            <span key="l" data-year-limit={y}><Blank words={file.year_limit} why={file.year_reason} /></span>] }; })} />
      </div>
    </ToolSection>
  );
}
