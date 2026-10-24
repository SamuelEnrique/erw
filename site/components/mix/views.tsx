// Energy Research Warehouse (ERW) site, session 133: the views of the one energy mix page (/mix), drawn on the server.
//
// Each view is what one of the earlier pages showed (the average day, the duck curve year after year and the records
// of /mix/v2; /mix/clean; /mix/stress), or one of the views session 133 added (availability by source, wind and solar
// forecasts against actual, the long history by state). The numbers are read from the site's own files (lib/mixdata.ts)
// with the libraries those pages used; the charts are components/mix/Charts.tsx and answer the mouse. A grid selection
// of up to four applies to every per-grid chart: lines are laid over each other, stacked areas sit side by side. The
// page face carries no method: a missing figure is a short placeholder with its reason on hover, and the rest is in
// the Method note (docs/methods/generation_mix_hourly.md).
import Link from "next/link";
import type { ReactNode } from "react";
import { Bars, Heat, HourStack, Lines, type Series } from "@/components/mix/Charts";
import { Missing } from "@/components/mix/Now";
import { Num } from "@/components/Num";  // session 1166: the committed files' headline figures, keyed
import * as clean from "@/lib/clean";
import { LICENSE_NEEDED, licenseHeldRow, licenseTitle } from "@/lib/license";  // session 215
import { heldGridPrice } from "@/lib/gridHeld";  // session 1167
import * as mix from "@/lib/mix2";
import { CLEAN, FORECAST, HISTORY, MIX, PLUS, STRESS, type Hourly, type Slug } from "@/lib/mixdata";
import { DASHES, FUEL_COLOR, FUEL_WORDS, GRID_COLORS, HOURS, SEASON_NAMES, n0, n1, n2, ofPeak, peakOf, yearShade, type Choice } from "@/lib/mixpage";
import { STATES } from "@/lib/regions";
import * as stress from "@/lib/stress";
import * as GS from "@/lib/gridStress";  // session 1168: the four measures by year, their notes and what each is not
import { anchorOf, GRID_ANCHOR, METHOD_STRESS_CALM, METHOD_STRESS_GRIDS, METHOD_STRESS_RAMP, METHOD_STRESS_TIGHT } from "@/lib/gridAnchors";  // session 1183: each panel's anchor; session 1184: its method
import { SiteLink } from "@/components/SiteLink";  // session 1184: a link to a method passes the release gate
import { PanelMethod } from "@/components/grid/PanelMethod";  // session 1184: the line that links the panel's method
import { PanelFile, type FileOf } from "@/components/grid/PanelFile";  // session 1182: the stress tables, to download
import { CalcKey } from "@/components/mix/CalcKey";  // session 1413: the figures computed from the committed files' arrays, keyed
import * as MV from "@/lib/mixViewCalc";  // session 1413: the arithmetic that stood inline in the history and supply views
import { METHOD_MIX_VIEWS, mixViewAnchor } from "@/lib/gridAnchors";  // session 1413: the computed views' anchors and method

const nameOf = (g: Slug) => mix.GRIDS.find((x) => x.slug === g)!.name;
const NH = ({ why, words }: { why: string; words?: string }) => <Missing why={why} words={words} />;
const val = (v: number | null | undefined, f: (n: number) => string, why = "This figure is not in the table for this grid and period.") => (v === null || v === undefined ? <NH why={why} /> : <>{f(v)}</>);
const cols = (n: number) => (n <= 1 ? "" : "grid gap-4 lg:grid-cols-2");

// Session 1166 (chain 078): the views' headline figures, keyed. Each is a value of a committed file (lib/mixdata.ts),
// keyed fmt|<form>|file|<data file>|<path>: scripts/check-values.mjs reads the file in the repository and follows the
// path (scripts/check-file.mjs), holds the text to the value in the form (scripts/check-format.mjs), and, where the file
// is a build of a live-set table, compares the value with that table's row on a line of its own. The text is the page's
// own, written by the same functions as before (n0, n1, n2 and a sign); the tip names the table, the row and the file.
const FORM: Record<"n0" | "n1" | "n2" | "sn0" | "sn1" | "span", (x: number) => string> = {
  n0, n1, n2, sn0: (x) => `${x > 0 ? "+" : ""}${n0(x)}`, sn1: (x) => `${x > 0 ? "+" : ""}${n1(x)}`,
  span: (x) => stress.span(x),   // session 1168: a stretch of hours as days and hours ("4 days 5 hours"), as the stress tables write it
};
type Form = keyof typeof FORM;
function tipOf(file: string, at: string): string {
  const [kind, g] = file.replace(/\.json$/, "").split("/");
  const table = kind === "mix" ? (at.startsWith("records") ? "generation_mix_records" : "generation_mix_hourly_profile") : kind === "clean" ? "clean_energy_summary" : kind === "stress" ? "grid_stress_yearly" : null;
  return `${table ? `${table}, iso:${g}` : "warehouse/derived/mix_views.py"}: ${at} (the committed file site/data/${file})`;
}
/** A keyed figure: the value in its form, the key, the tip (a note first when the cell had one). */
function K({ v, form, file, at, note }: { v: number; form: Form; file: string; at: string; note?: string }) {
  return <span title={note ? `${note}\n${tipOf(file, at)}` : tipOf(file, at)} className="cursor-help border-b border-dotted border-muted"><Num check={`fmt|${form}|file|${file}|${at}`} raw={v}>{FORM[form](v)}</Num></span>;
}
/** As val, keyed: the value in its form with its unit after it, or the placeholder with its reason. */
const kv = (v: number | null | undefined, form: Form, file: string, at: string, unit = "", why = "This figure is not in the table for this grid and period.") =>
  (v === null || v === undefined ? <NH why={why} /> : <><K v={v} form={form} file={file} at={at} />{unit}</>);
const held1 = (p: Record<string, unknown> | null | undefined, k: string) => typeof p?.[k] === "number";
// Session 1413 (chain 107): the figures the views compute from a committed file's arrays (the duck curve by year, the
// average day's peak hours, the history by state, the availability means), keyed fmt|<form>|filecalc|<function>|<file>|<args>
// (components/mix/CalcKey.tsx, lib/mixViewCalc.ts): scripts/check-values.mjs applies the same function to the file in the
// repository (scripts/check-filecalc.mjs). As val, keyed: the value in its form with its unit after it, or the placeholder.
const kc = (v: number | null | undefined, form: Form, fn: MV.FilecalcFn, file: string, args: string[], unit = "", why = "This figure is not in the table for this grid and period.") =>
  (v === null || v === undefined ? <NH why={why} /> : <><CalcKey v={v} form={form} text={FORM[form](v)} fn={fn} file={file} args={args} />{unit}</>);
/** Session 1413: the line under a computed view's table that links its method (as the Grid panels' PanelMethod lines). */
const ViewMethod = () => <p className="mt-1 text-xs text-muted" data-grid-method="mix-views"><SiteLink href={METHOD_MIX_VIEWS}>Method: the computed views, keyed</SiteLink>.</p>;
/** Session 1413: a view's address, as the stress view writes its own (its view under the page's own key, then its words). */
const viewPage = (c: Choice, view: string, rest: string) => `${c.base?.href ?? "/mix"}${c.base ? "&" : "?"}${c.base && !c.base.viewKey ? "" : `${c.base?.viewKey ?? "view"}=${view}&`}${rest}`;
/** Session 1413: the provenance of a mix file's table, for its file. */
const mixTables = (g: Slug) => [`generation_mix_hourly_profile (warehouse/derived/mix_profile.py, docs/methods/generation_mix_hourly.md), as the committed file site/data/mix/${g}.json holds it (built ${MIX[g].built})`];
const plusTables = (g: Slug) => [`generation_mix_hourly_profile hours held (the energy mix's hours, warehouse/derived/mix_profile.py) over EIA-860M's installed nameplate capacity, by warehouse/derived/mix_views.py (docs/methods/generation_mix_hourly.md), as the committed file site/data/mixplus/${g}.json holds it (built ${PLUS[g].built})`];

export function Chips({ label, items }: { label: string; items: { key: string; label: string; href: string; on: boolean; title?: string; off?: boolean }[] }) {
  return (
    <div className="flex flex-wrap items-center gap-1 text-xs" role="group" aria-label={label}>
      <span className="mr-1 text-muted">{label}</span>
      {items.map((i) => i.off
        ? <span key={i.key} title={i.title} data-chip-off={`${label}:${i.key}`} className="cursor-help border border-rule/60 px-1.5 py-px text-muted">{i.label}</span>
        : <Link key={i.key} href={i.href} scroll={false} aria-current={i.on ? "true" : undefined} title={i.title} data-chip={`${label}:${i.key}`} style={{ color: i.on ? "var(--color-surface)" : "var(--color-ink)" }}
            className={`border px-1.5 py-px no-underline ${i.on ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{i.label}</Link>)}
    </div>
  );
}
function Block({ title, children, id }: { title: string; children: ReactNode; id?: string }) {
  return <section id={id} className="mb-8"><h2 className="mb-2 border-b border-accent pb-0.5 font-serif text-lg text-accent">{title}</h2>{children}</section>;
}
function Card({ title, children }: { title: string; children: ReactNode }) {
  return <div className="min-w-0"><h3 className="mb-1 text-sm font-semibold">{title}</h3>{children}</div>;
}
function Table({ head, rows, caption, file }: { head: ReactNode[]; rows: { key: string; cells: ReactNode[]; on?: boolean }[]; caption: string;
  /** session 1182: the table offered as a file, from the same cells (components/grid/PanelFile.tsx) */ file?: FileOf }) {
  if (file) return <><Table head={head} rows={rows} caption={caption} /><PanelFile of={file} columns={head} rows={rows.map((r) => r.cells)} /></>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm tabular-nums">
        <caption className="sr-only">{caption}</caption>
        <thead><tr className="border-b border-rule text-xs text-muted">{head.map((h, i) => <th key={i} className={`py-1 pr-3 font-normal ${i ? "text-right" : "text-left"}`}>{h}</th>)}</tr></thead>
        <tbody>{rows.map((r) => <tr key={r.key} className={`border-b border-rule/60 ${r.on ? "bg-paper" : ""}`}>{r.cells.map((c, i) => (i ? <td key={i} className="py-1 pr-3 text-right">{c}</td> : <th key={i} scope="row" className="py-1 pr-3 text-left font-normal">{c}</th>))}</tr>)}</tbody>
      </table>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// the average day: generation by fuel by hour, for any month or year since 2019
// ---------------------------------------------------------------------------------------------------------------------

/** The lines a factor draws beside the mix, for one grid and period (a month or a year), or the reason there are none. */
function factorLines(g: Slug, c: Choice, period: string, demand: (number | null)[] | undefined): { lines: Series[]; unit2?: string; missing?: { words: string; why: string } } {
  if (c.factor === "none") return { lines: [] };
  const f = PLUS[g].factors;
  const at = (h: Hourly) => (period.length === 7 ? h.months[period] : h.years[period]) as number[] | undefined;
  const gone = (h: Hourly, what: string) => ({ lines: [], missing: h.status === "paused" ? { words: "paused while terms are reviewed", why: h.note ?? "" } : h.status === "licensed" ? { words: "licensed source needed", why: h.note ?? "" }
    : { words: "not held yet", why: `${what} is not held for ${nameOf(g)} in ${mix.periodName(period)}: a period is drawn when every hour of the day holds enough days.` } });
  if (c.factor === "price") {
    // session 1167: a held grid's hub price (the file's copy of iso_hub_prices_history, lib/gridHeld.ts) reads "license
    // needed" in place of its lines; a paused grid's file holds none and keeps its words
    const hp = f.price_da.status === "paused" ? null : heldGridPrice(g);
    if (hp) return { lines: [], missing: hp };
    const da = at(f.price_da), rt = at(f.price_rt);
    if (!da && !rt) return gone(f.price_da, "The hub price");
    return { unit2: "USD/MWh", lines: [...(da ? [{ name: "Price, day-ahead", color: "var(--color-ink)", values: da, axis: 1 as const, dash: "dashed" as const, unit: "USD/MWh" }] : []),
      ...(rt ? [{ name: "Price, real time", color: "var(--color-ink)", values: rt, axis: 1 as const, dash: "dotted" as const, unit: "USD/MWh" }] : [])] };
  }
  if (c.factor === "demand") return demand ? { unit2: "MW", lines: [{ name: "Demand", color: "var(--color-ink)", values: demand, axis: 1, dash: "dashed", unit: "MW" }] } : gone(f.carbon, "Demand");
  const pick = c.factor === "temperature" ? [f.temperature, "Temperature", "degrees F"] as const : c.factor === "carbon" ? [f.carbon, "Carbon intensity of generation", "kg CO2/MWh"] as const : [f.net_imports, "Net imports", "MW"] as const;
  const v = at(pick[0]);
  return v ? { unit2: pick[2], lines: [{ name: pick[1], color: "var(--color-ink)", values: v, axis: 1, dash: "dashed", unit: pick[2] }] } : gone(pick[0], pick[1]);
}

export function DayView({ c }: { c: Choice }) {
  const period = c.period ?? MIX[c.grids[0]].upto;
  const held = c.grids.map((g) => ({ g, file: MIX[g], p: mix.periodOf(MIX[g], period) }));
  const unit = c.norm === "peak" ? "% of peak demand" : "MW";
  const sources = mix.SOURCES.filter((s) => held.some((h) => h.p && mix.sourcesIn(h.p).some((x) => x.key === s.key)));
  // session 1413: the two tables, to download (components/grid/PanelFile.tsx), each from the cells it draws
  const dayFile = (part: string, title: string): FileOf => ({ panel: "grid_mixday_all", part, title, page: viewPage(c, "day", `grids=${c.grids.join(",")}&period=${period}`),
    tables: c.grids.flatMap(mixTables), filter: `iso:<grid> for ${c.grids.join(", ")}`, window: `Window: ${mix.periodName(period)}, its average day by local hour`,
    notes: ["A month is written when at least 90 percent of its days are complete, a year when at most one month is missing; an hour of the day is local time."] });
  return (
    <>
      <Block title={`Generation by fuel, by hour: the average day of ${mix.periodName(period)}`} id="day">
        <div className={cols(held.length)}>
          {held.map(({ g, p }) => {
            if (!p) return <Card key={g} title={nameOf(g)}><NH why={`${nameOf(g)} holds no ${mix.periodName(period)}: a month is written when at least 90 percent of its days are complete, a year when at most one month is missing.`} /></Card>;
            const peak = c.norm === "peak" ? peakOf(p.avg.demand) : null;
            const scale = (v: (number | null)[]) => (c.norm === "peak" ? ofPeak(v, peak) : v);
            const fl = factorLines(g, c, period, undefined);
            return (
              <Card key={g} title={`${nameOf(g)}${p.side === "caiso" ? ", from CAISO's own data" : ""}`}>
                <HourStack x={HOURS} unit={unit} unit2={fl.unit2} name={`erw-mix-${g}-${period}`} label={`${nameOf(g)}, ${mix.periodName(period)}, local hour`}
                  layers={mix.sourcesIn(p).map((s) => ({ name: s.label, color: s.color, values: scale(p.avg[s.key] ?? []) }))}
                  lines={[...(c.factor === "demand" || !p.avg.demand ? [] : [{ name: "Demand", color: "var(--color-ink)", values: scale(p.avg.demand), width: 2 }]),
                    ...(c.factor === "demand" && p.avg.demand ? [{ name: "Demand", color: "var(--color-ink)", values: scale(p.avg.demand), width: 2.4 }] : []), ...fl.lines]} />
                {fl.missing ? <p className="mt-1 text-xs">Factor: <NH why={fl.missing.why} words={fl.missing.words} /></p> : null}
              </Card>
            );
          })}
        </div>
      </Block>
      <Block title={`Shares of generation by source, ${mix.periodName(period)}`} id={mixViewAnchor("dayShares", 0, "")}>
        <Table caption="Shares of generation by source" file={dayFile("shares", `shares of generation by source, ${mix.periodName(period)}`)} head={["Source", ...held.flatMap(({ g }) => [`${nameOf(g)}, share`, `${nameOf(g)}, MWh`])]}
          rows={sources.map((s) => ({ key: s.key, cells: [<span key="n"><span className="mr-1.5 inline-block h-2.5 w-2.5" style={{ background: s.color }} />{s.label}</span>,
            ...held.flatMap(({ g, p }) => { const sh = p ? mix.shares(p).find((x) => x.key === s.key) : undefined; const at = `${period.length === 7 ? "months" : "years"}.${period}`;
              return [held1(p, `${s.key}_share_pct`) ? kv(sh?.share, "n1", `mix/${g}.json`, `${at}.${s.key}_share_pct`, "%") : val(sh?.share, (v) => `${n1(v)}%`),
                held1(p, `${s.key}_mwh`) ? kv(sh?.mwh, "n0", `mix/${g}.json`, `${at}.${s.key}_mwh`) : val(sh?.mwh, n0)]; })] }))} />
        <ViewMethod />
      </Block>
      <Block title="Solar and wind at their peak hour of the average day" id={mixViewAnchor("dayPeak", 0, "")}>
        <Table caption="Largest source, and solar and wind at their peak" file={dayFile("peak", `the largest source, and solar and wind at their peak hour of the average day, ${mix.periodName(period)}`)} head={["Grid", "Largest source", "Its share", "Solar, share", "Solar at its peak, MW", "Hour", "Wind, share", "Wind at its peak, MW", "Hour", "Days held"]}
          rows={held.map(({ g, p }) => {
            if (!p) return { key: g, cells: [nameOf(g), ...Array.from({ length: 9 }, (_, i) => <NH key={i} why={`${nameOf(g)} holds no ${mix.periodName(period)}.`} />)] };
            const sh = mix.shares(p), top = sh[0], sol = mix.highest(p.avg.solar ?? []), wnd = mix.highest(p.avg.wind ?? []);
            const share = (k: string) => sh.find((x) => x.key === k)?.share;
            const at = `${period.length === 7 ? "months" : "years"}.${period}`, file = `mix/${g}.json`;
            const ks = (k: string) => (held1(p, `${k}_share_pct`) ? kv(share(k), "n1", file, `${at}.${k}_share_pct`, "%") : val(share(k), (v) => `${n1(v)}%`));
            // session 1413: solar and wind at their peak, keyed by the function that finds them (lib/mix2.ts highest); the hours stay words
            return { key: g, cells: [nameOf(g), top.label, held1(p, `${top.key}_share_pct`) ? <>{kv(top.share, "n1", file, `${at}.${top.key}_share_pct`)}%</> : `${n1(top.share)}%`, ks("solar"), kc(sol && sol.value > 0 ? sol.value : null, "n0", "day_peak", file, [period, "solar"], "", "The grid's file reports no solar output."), sol && sol.value > 0 ? mix.hourName(sol.hour) : "",
              ks("wind"), kc(wnd && wnd.value > 0 ? wnd.value : null, "n0", "day_peak", file, [period, "wind"], "", "The grid's file reports no wind output."), wnd && wnd.value > 0 ? mix.hourName(wnd.hour) : "", held1(p, "days_held") ? kv(p.days_held, "n0", file, `${at}.days_held`) : n0(p.days_held)] };
          })} />
        <ViewMethod />
      </Block>
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// year after year: net load by hour (the duck curve), and solar, one calendar month across the years
// ---------------------------------------------------------------------------------------------------------------------

export function DuckView({ c }: { c: Choice }) {
  const cal = c.cal ?? "04";
  const per = c.grids.map((g) => ({ g, ys: mix.acrossYears(MIX[g], cal) }));
  const common = per.map((x) => new Set(x.ys.map((y) => y.year))).reduce((a, b) => new Set([...a].filter((y) => b.has(y))));
  const year = c.year && common.has(c.year) ? c.year : [...common].sort().at(-1) ?? null;
  const unit = c.norm === "peak" ? "% of peak demand" : "MW";
  const peakFor = (g: Slug, y: string) => peakOf(mix.periodOf(MIX[g], `${y}-${cal}`)?.avg.demand);
  return (
    <>
      {per.length > 1 ? (
        <Block title={`Net load by hour, the grids together: ${mix.calName(cal)}${year ? ` ${year}` : ""}`} id="together">
          {year ? <Lines x={HOURS} unit={unit} name={`erw-mix-duck-${cal}-${year}`} label={`Net load, ${mix.calName(cal)} ${year}, local hour`}
            series={per.map(({ g, ys }, i) => { const y = ys.find((q) => q.year === year)!; return { name: nameOf(g), color: GRID_COLORS[i], values: c.norm === "peak" ? ofPeak(y.net, peakFor(g, year)) : y.net, width: 2 }; })} />
            : <NH why={`No year holds ${mix.calName(cal)} for every grid chosen.`} />}
        </Block>
      ) : null}
      <Block title={`Net load by hour, ${mix.calName(cal)}, year after year`} id="years">
        <div className={cols(per.length)}>
          {per.map(({ g, ys }) => {
            if (!ys.length) return <Card key={g} title={nameOf(g)}><NH why={`${nameOf(g)} holds no ${mix.calName(cal)} in any year.`} /></Card>;
            const last = ys[ys.length - 1];
            const fl = factorLines(g, c, `${last.year}-${cal}`, mix.periodOf(MIX[g], `${last.year}-${cal}`)?.avg.demand);
            return (
              <Card key={g} title={nameOf(g)}>
                <Lines x={HOURS} unit={unit} unit2={fl.unit2} name={`erw-mix-duck-${g}-${cal}`} label={`${nameOf(g)}, net load, ${mix.calName(cal)}, local hour`}
                  series={[...ys.map((y, i) => ({ name: y.year, color: yearShade(i, ys.length), values: c.norm === "peak" ? ofPeak(y.net, peakFor(g, y.year)) : y.net, width: i === ys.length - 1 ? 2.4 : 1.3 })),
                    ...fl.lines.map((l) => ({ ...l, name: `${l.name}, ${last.year}` }))]} />
                {fl.missing ? <p className="mt-1 text-xs">Factor: <NH why={fl.missing.why} words={fl.missing.words} /></p> : null}
              </Card>
            );
          })}
        </div>
      </Block>
      <Block title={`Solar by hour, ${mix.calName(cal)}, year after year`}>
        <div className={cols(per.length)}>
          {per.map(({ g, ys }) => {
            const sun = ys.filter((y) => y.solarPeak && y.solarPeak.value > 0);
            return (
              <Card key={g} title={nameOf(g)}>
                {sun.length ? <Lines x={HOURS} unit={unit} zero name={`erw-mix-solar-${g}-${cal}`} label={`${nameOf(g)}, solar, ${mix.calName(cal)}, local hour`}
                  series={sun.map((y, i) => ({ name: y.year, color: yearShade(i, sun.length), values: c.norm === "peak" ? ofPeak(y.solar, peakFor(g, y.year)) : y.solar, width: i === sun.length - 1 ? 2.4 : 1.3 }))} />
                  : <NH why={`${nameOf(g)}'s file reports no solar output in ${mix.calName(cal)}.`} />}
              </Card>
            );
          })}
        </div>
      </Block>
      {per.map(({ g, ys }, i) => {
        // session 1413: each figure of the table keyed by the function that computes it from the file (lib/mix2.ts
        // acrossYears), the days held by the file's own value (file|); the hours stay words. The table, to download
        const file = `mix/${g}.json`;
        const yk = (fn: MV.FilecalcFn, y: mix.DuckYear, v: number | null | undefined, why?: string) => kc(v, "n0", fn, file, [cal, y.year], "", why);
        return (
        <Block key={g} title={`${nameOf(g)}: ${mix.calName(cal)} by year`} id={mixViewAnchor("duckYears", i, g)}>
          <Table caption={`${nameOf(g)}, ${mix.calName(cal)} by year`} head={["Year", "Solar at its peak, MW", "Hour", "Net load's midday low, MW", "Hour", "Net load's evening high, MW", "Hour", "The ramp between them, MW", "Days held"]}
            file={{ panel: `grid_duck_${g}`, title: `${nameOf(g)}: ${mix.calName(cal)} by year`, page: viewPage(c, "duck", `grids=${c.grids.join(",")}&cal=${cal}`), tables: mixTables(g),
              filter: `iso:${g}, ${mix.calName(cal)} of each year`, window: `Window: ${mix.calName(cal)} of the years ${ys[0]?.year ?? ""} to ${ys.at(-1)?.year ?? ""}, each month's average day by local hour (${MIX[g].tz})`,
              notes: ["Net load is demand less wind and solar, hour by hour; its midday low is from 09:00 to 16:00, its evening high from 16:00; the ramp is given when the low comes first."] }}
            rows={ys.map((y) => ({ key: y.year, on: y.year === year, cells: [y.year, yk("duck_solar_peak", y, y.solarPeak && y.solarPeak.value > 0 ? y.solarPeak.value : null, "The grid's file reports no solar output."), y.solarPeak && y.solarPeak.value > 0 ? mix.hourName(y.solarPeak.hour) : "",
              yk("duck_low", y, y.low?.value), y.low ? mix.hourName(y.low.hour) : "", yk("duck_evening", y, y.evening?.value), y.evening ? mix.hourName(y.evening.hour) : "", yk("duck_ramp", y, y.ramp),
              held1(MIX[g].months[y.month], "days_held") ? kv(y.days, "n0", file, `months.${y.month}.days_held`) : n0(y.days)] }))} />
          <ViewMethod />
        </Block>
        );
      })}
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// the records
// ---------------------------------------------------------------------------------------------------------------------

export function RecordsView({ c }: { c: Choice }) {
  return (
    <>
      {c.grids.map((g) => {
        const file = MIX[g], plus = PLUS[g];
        const years = Object.keys(plus.records).filter((y) => y !== "all").sort();
        const year = c.year && years.includes(c.year) ? c.year : years.at(-1)!;
        const when = (ts: string, kind: string) => (kind === "day" ? new Date(`${ts}T12:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }) : mix.localHour(ts, file.tz));
        // session 1166: each record's file and the paths of its two figures, for their keys
        const share = mix.RECORD_ROWS.map((r) => ({ key: r.variable, label: r.label, unit: r.unit, all: mix.recordOf(file, r.variable, "all"), yr: mix.recordOf(file, r.variable, year), kind: "hour",
          src: `mix/${g}.json`, atAll: `records[variable=${r.variable},period=all].value`, atYr: `records[variable=year_${r.variable},period=${year}].value` }));
        const extra = (plus.records.all ?? []).map((r) => ({ key: r.key, label: r.label, unit: r.unit === "pct" ? "percent of generation" : r.unit, kind: r.kind,
          src: `mixplus/${g}.json`, atAll: `records.all[key=${r.key}].value`, atYr: `records.${year}[key=${r.key}].value`,
          all: { value: r.value, ts_utc: r.at }, yr: (plus.records[year] ?? []).find((x) => x.key === r.key) ? { value: plus.records[year].find((x) => x.key === r.key)!.value, ts_utc: plus.records[year].find((x) => x.key === r.key)!.at } : undefined }));
        const why = "The grid's file reports nothing to rank for this record (a source it does not report, or no hour that passes the tests).";
        return (
          <Block key={g} title={`${nameOf(g)}: the records`}>
            <Table caption={`${nameOf(g)}, records`} head={["Record", "Unit", `Since ${file.first.slice(0, 4)}`, "When, local time", `In ${year}`, "When, local time"]}
              rows={[...share, ...extra].map((r) => { const form: Form = r.unit === "hours" || r.unit === "MW" || r.unit === "MWh" ? "n0" : "n1";
                return { key: r.key, cells: [r.label, r.unit, kv(r.all?.value, form, r.src, r.atAll, "", why), r.all ? when(r.all.ts_utc, r.kind) : "",
                  kv(r.yr?.value, form, r.src, r.atYr, "", why), r.yr ? when(r.yr.ts_utc, r.kind) : ""] }; })} />
          </Block>
        );
      })}
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// how clean, and when
// ---------------------------------------------------------------------------------------------------------------------

export function CleanView({ c, live }: { c: Choice;
  /** session 1403: the Grid tool's live week beside each grid's cleanest hours (components/grid/CleanWeekPanel.tsx), given
   *  the grid and the year in view; none elsewhere, so the view is drawn as before where no caller passes it */
  live?: (g: Slug, year: string) => ReactNode }) {
  const first = CLEAN[c.grids[0]];
  const year = c.year && c.grids.some((g) => CLEAN[g].years[c.year!]) ? c.year : clean.defaultYear(first) ?? clean.yearsOf(first).at(-1)!;
  const years = [...new Set(c.grids.flatMap((g) => clean.yearsOf(CLEAN[g])))].sort();
  const notWritten = (g: Slug) => `${nameOf(g)}'s ${year} is not written: a year needs at most one month missing, and a month 90 percent of its days.`;
  // session 215: the clean files are the site's copy of clean_energy_summary, held by grid from 20 October 2026
  // (lib/license.ts): a held grid's cells and blocks read "license needed", as a number of it would on the catalogue,
  // in the page's own placeholder (Missing: the words, the reason on hover; this page's face carries no block of prose)
  const CLEAN_TABLE = "clean_energy_summary";
  const held = (g: Slug) => licenseHeldRow(CLEAN_TABLE, `iso:${g}`);
  const LW = () => <NH why={licenseTitle(CLEAN_TABLE)} words={LICENSE_NEEDED} />;
  return (
    <>
      <Block title="Carbon-free share of generation, by year" id="clean">
        <Bars x={years} unit="% of generation" name="erw-mix-carbon-free" label="Carbon-free share of generation"
          series={c.grids.filter((g) => !held(g)).map((g) => ({ name: nameOf(g), color: GRID_COLORS[c.grids.indexOf(g)], values: years.map((y) => clean.get(CLEAN[g].years[y], "carbon_free_share_pct")) }))} />
        <Table caption="Carbon-free share and hours" head={["Grid", `Carbon-free share, ${year}`, "For a flat load", "Hours at least 50% carbon-free", "At least 75%", "At least 90%", "Months held"]}
          rows={c.grids.map((g) => { const f = CLEAN[g]; if (held(g)) return { key: g, cells: [nameOf(g), ...Array.from({ length: 6 }, (_, i) => <LW key={i} />)] };
            if (!f.years[year]) return { key: g, cells: [nameOf(g), ...Array.from({ length: 6 }, (_, i) => <NH key={i} why={notWritten(g)} />)] };
            const v = clean.yearView(f, year), cf = `clean/${g}.json`, y = `years.${year}`;
            return { key: g, cells: [nameOf(g), kv(v.share, "n1", cf, `${y}.carbon_free_share_pct`, "%"), kv(v.flat, "n1", cf, `${y}.carbon_free_share_flat_pct`, "%"), ...f.levels.map((l) => kv(v.ge[l], "n1", cf, `${y}.hours_cf_ge${l}_pct`, "%")), `${v.months ?? 0} of ${v.due ?? 12}`] }; })} />
      </Block>
      {c.grids.map((g) => {
        const f = CLEAN[g];
        // session 1403: the live week is of carbon_intensity_hourly, public for every grid, so it stands under a held or
        // unwritten year too (its own line says when the committed day it is set against is held)
        const week = live ? <Block title={`${nameOf(g)}: the cleanest hours of the last 7 days held`}>{live(g, year)}</Block> : null;
        if (held(g)) return week ? <div key={g}><Block title={`${nameOf(g)}, ${year}`}><LW /></Block>{week}</div> : <Block key={g} title={`${nameOf(g)}, ${year}`}><LW /></Block>;
        if (!f.years[year]) return week ? <div key={g}><Block title={`${nameOf(g)}, ${year}`}><NH why={notWritten(g)} /></Block>{week}</div> : <Block key={g} title={`${nameOf(g)}, ${year}`}><NH why={notWritten(g)} /></Block>;
        const v = clean.yearView(f, year), months = clean.monthsOf(f, year);
        return (
          <div key={g}>
            <Block title={`${nameOf(g)}: an annual clean purchase against the hours, ${year}`}>
              <Table caption="Annual against hourly matching" head={["Purchase, share of annual load", ...f.shapes.flatMap((s) => [`${clean.SHAPE_NAME[s]}: energy met in its own hour`, "Hours met in full"])]}
                rows={f.purchases.map((p) => ({ key: String(p), on: p === 100, cells: [`${p}%`, ...f.shapes.flatMap((s) => [val(v.match[s]?.[p]?.energy, (x) => `${n1(x)}%`), val(v.match[s]?.[p]?.hours, (x) => `${n1(x)}%`)])] }))} />
            </Block>
            <Block title={`${nameOf(g)}: the cleanest hours of the average day, ${year}`}>
              <Heat rows={months.map((m) => clean.monthName(m))} cols={HOURS} unit="% carbon-free" name={`erw-mix-clean-${g}-${year}`} label={`${nameOf(g)}, carbon-free share of generation, ${year}`}
                cells={months.map((m) => clean.dayOf(f, m))} marks={months.flatMap((m, r) => clean.cleanestOf(f, m).map((h): [number, number] => [r, h]))} />
              <Table caption="The cleanest hours by month" head={["Month", "The four cleanest hours", "Share in the cleanest hour", "Share in the dirtiest hour", "The month's share"]}
                rows={months.map((m) => { const d = clean.dayOf(f, m).filter((x): x is number => x !== null); return { key: m, cells: [clean.monthName(m), clean.hoursName(clean.cleanestOf(f, m)), d.length ? `${n1(Math.max(...d))}%` : "", d.length ? `${n1(Math.min(...d))}%` : "",
                  val(clean.get(f.months[m], "carbon_free_share_pct"), (x) => `${n1(x)}%`)] }; })} />
            </Block>
            {week}
            <Block title={`${nameOf(g)}: moving a flat load into the cleanest hours`}>
              <Table caption="Moving load into the cleanest hours" head={["Year", "Flat load, kg CO2/MWh", ...f.shifts.map((s) => `${s}% moved: carbon`), "Days", "Flat load, USD/MWh", ...f.shifts.map((s) => `${s}% moved: cost`), "Days priced"]}
                rows={clean.yearsOf(f).reverse().map((y) => { const w = clean.yearView(f, y); const noPrice = f.no_price ?? "No hub price is held for this grid in this year.";
                  return { key: y, on: y === year, cells: [y, val(w.carbon.flat, n1), ...f.shifts.map((s) => val(w.carbon.change[s], (x) => `${x > 0 ? "+" : ""}${n1(x)}%`)), val(w.carbon.days, n0),
                    w.cost.flat === null ? <NH key="c" why={noPrice} words={/paused/.test(noPrice) ? "paused while terms are reviewed" : /PJM/.test(noPrice) ? "licensed source needed" : "not held yet"} /> : n2(w.cost.flat),
                    ...f.shifts.map((s) => val(w.cost.change[s], (x) => `${x > 0 ? "+" : ""}${n1(x)}%`, noPrice)), val(w.cost.days, n0, noPrice)] }; })} />
            </Block>
          </div>
        );
      })}
      <Block title={`The seven grids, ${year}`}>
        <Table caption="The seven grids" head={["Grid", "Months held", "Carbon-free share", "Hours at least half carbon-free", "100% purchase: energy met in its hour", "20% moved: carbon", "20% moved: cost"]}
          rows={clean.GRIDS.map((g) => { const f = CLEAN[g];
            // session 1167 (the standing rule, lib/license.ts): a held grid's cells read "license needed", as every other block of the view
            if (held(g)) return { key: g, on: c.grids.includes(g), cells: [nameOf(g), ...Array.from({ length: 6 }, (_, i) => <LW key={i} />)] };
            if (!f.years[year]) return { key: g, cells: [nameOf(g), ...Array.from({ length: 6 }, (_, i) => <NH key={i} why={notWritten(g)} />)] };
            const v = clean.yearView(f, year); const noPrice = f.no_price ?? "No hub price is held for this grid in this year.";
            // session 1166: keyed for the grids not held (session 1167: a held grid no longer reaches this line)
            const cf = `clean/${g}.json`, y = `years.${year}`, key = !held(g);
            const kp = (x: number | null | undefined, at: string, form: Form = "n1") => (key ? kv(x, form, cf, `${y}.${at}`, "%") : val(x, (z) => `${FORM[form](z)}%`));
            return { key: g, on: c.grids.includes(g), cells: [nameOf(g), `${v.months ?? 0} of ${v.due ?? 12}`, kp(v.share, "carbon_free_share_pct"), kp(v.ge[50], "hours_cf_ge50_pct"), kp(v.match.mix?.[100]?.energy, "match_mix_100_energy_pct"),
              kp(v.carbon.change[20], "shift20_carbon_change_pct", "sn1"), v.cost.change[20] === null || v.cost.change[20] === undefined
                ? <NH key="p" why={noPrice} words={/paused/.test(noPrice) ? "paused while terms are reviewed" : /PJM/.test(noPrice) ? "licensed source needed" : "not held yet"} /> : kp(v.cost.change[20]!, "shift20_cost_change_pct", "sn1")] }; })} />
      </Block>
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// how hard the system works
// ---------------------------------------------------------------------------------------------------------------------

/** The NRC's reactor status as the note on nuclear's row. */
function nuclearNote(g: Slug, year: string, season = "all"): string {
  const n = PLUS[g].nuclear[year]?.[season];
  if (!n) return "The NRC's daily reactor status is not held for this grid and period.";
  const low = n.low.length ? ` Most days below half power: ${n.low.map(([u, d]) => `${u} (${d})`).join(", ")}.` : " No reactor spent a day below half power.";
  return `NRC daily status, ${n.days} days: ${n.units} reactors in this grid, mean power ${n1(n.mean_pct)}% of licensed power.${low}`;
}

export function StressView({ c }: { c: Choice }) {
  const first = STRESS[c.grids[0]];
  const year = c.year && c.grids.some((g) => STRESS[g].years[c.year!]) ? c.year : stress.defaultYear(first) ?? stress.yearsOf(first).at(-1)!;
  const years = [...new Set(c.grids.flatMap((g) => stress.yearsOf(STRESS[g])))].sort();
  const g1 = (g: Slug, y: string, k: string) => (STRESS[g].years[y] ? stress.get(STRESS[g], y, k) : null);
  const why = "The year is not in this grid's table: its hours were not held.";
  // session 1168: each chart's hover carries the year's figures behind its points and what the figure is not; a link
  // under it opens the method note's line (docs/methods/grid_stress.md, "What each chart is not (session 1168)")
  const files = c.grids.map((g) => STRESS[g]);
  const not = (m: GS.Measure) => <p className="mt-1 text-xs text-muted"><Link href={GS.STRESS_METHOD} title={GS.NOT[m]} data-stress-not={m} className="cursor-help">What this chart is not</Link></p>;
  // session 1182: each table's file names its table, its grid, its years and the committed file it is read from
  // the page's address, as the view's links write it (lib/mixpage.ts, the stress view's own words: its grids and year)
  const page = `${c.base?.href ?? "/mix"}${c.base ? "&" : "?"}${c.base && !c.base.viewKey ? "" : `${c.base?.viewKey ?? "view"}=stress&`}grids=${c.grids.join(",")}&year=${year}`;
  const stressFile = (g: Slug, part: string, title: string, window: string): FileOf => ({ panel: `grid_stress_${g}`, part, title: `${nameOf(g)}: ${title}`, page,
    tables: [`grid_stress_yearly (derived: warehouse/derived/grid_stress.py, docs/methods/grid_stress.md), as the committed file site/data/stress/${g}.json holds it (built ${STRESS[g].built})`],
    filter: `iso:${g}, by year`, window, notes: ["A year marked to date is not a whole year; a stretch of hours is written in hours."] });
  return (
    <>
      <Block title="The largest evening ramp of each year, as a share of peak demand" id="stress">
        {c.grids.length === 1
          ? <Bars x={years} unit="% of peak demand" name="erw-mix-ramp" label={`${nameOf(c.grids[0])}, largest evening ramp`} notes={GS.notesOf(files, years, GS.rampNote)} tip={GS.NOT.ramp}
              series={[{ name: "In one hour", color: "var(--color-accent)", values: years.map((y) => g1(c.grids[0], y, "evening_ramp_max_share_of_peak_pct")) },
                { name: "Over three hours", color: "var(--color-ink)", values: years.map((y) => g1(c.grids[0], y, "evening_ramp_3h_max_share_of_peak_pct")) }]} />
          : <div className="grid gap-4 lg:grid-cols-2">
              <Card title="In one hour"><Lines x={years} unit="% of peak demand" zero name="erw-mix-ramp-1h" label="Largest evening ramp in one hour" notes={GS.notesOf(files, years, GS.rampNote)} tip={GS.NOT.ramp} series={c.grids.map((g, i) => ({ name: nameOf(g), color: GRID_COLORS[i], values: years.map((y) => g1(g, y, "evening_ramp_max_share_of_peak_pct")), width: 2 }))} /></Card>
              <Card title="Over three hours"><Lines x={years} unit="% of peak demand" zero name="erw-mix-ramp-3h" label="Largest evening ramp over three hours" notes={GS.notesOf(files, years, GS.rampNote)} tip={GS.NOT.ramp} series={c.grids.map((g, i) => ({ name: nameOf(g), color: GRID_COLORS[i], values: years.map((y) => g1(g, y, "evening_ramp_3h_max_share_of_peak_pct")), width: 2 }))} /></Card>
            </div>}
        {not("ramp")}
      </Block>
      <Block title="The lowest net load of each year, as a share of peak demand" id="stress-netload">
        <Lines x={years} unit="% of peak demand" zero name="erw-mix-netload" label={c.grids.length === 1 ? `${nameOf(c.grids[0])}, lowest net load` : "Lowest net load"} notes={GS.notesOf(files, years, GS.netLoadNote)} tip={GS.NOT.netload}
          series={c.grids.map((g, i) => ({ name: c.grids.length === 1 ? "Lowest net load" : nameOf(g), color: GRID_COLORS[i], values: GS.valuesOf(STRESS[g], years, "net_load_min_share_of_peak_pct"), width: 2, digits: 1 }))} />
        {not("netload")}
      </Block>
      {c.grids.map((g, i) => {
        const f = STRESS[g], ys = stress.yearsOf(f).reverse();
        const whenOf = (y: string, k: string) => { const t = stress.at(f, y, k); return t ? stress.when(t, f.tz) : ""; };
        return (
          <div key={g}>
            <Block title={`${nameOf(g)}: the evening ramp and the lowest net load, by year`} id={anchorOf("stressRamp", i, g)}>
              <Table caption="Evening ramp and lowest net load" file={stressFile(g, "ramp", "the evening ramp and the lowest net load, by year", `Window: the years ${ys.at(-1)} to ${ys[0]}, each its own year (hours in ${f.tz})`)} head={["Year", "Peak demand, MW", "Largest ramp in one hour, MW", "Share of peak", "When it started", "Largest over three hours, MW", "Lowest net load, MW", "Share of peak", "When", "Hours held"]}
                rows={ys.map((y) => { const sk = (k: string, form: Form, unit = "") => kv(stress.get(f, y, k), form, `stress/${g}.json`, `years.${y}.${k}`, unit);
                  return { key: y, on: y === year, cells: [`${y}${stress.wholeYear(f, y) ? "" : " to date"}`, sk("peak_demand_mw", "n0"), sk("evening_ramp_max_mw_per_h", "n0"), sk("evening_ramp_max_share_of_peak_pct", "n1", "%"),
                  whenOf(y, "evening_ramp_max_mw_per_h"), sk("evening_ramp_3h_max_mw", "n0"), sk("net_load_min_mw", "n0"), sk("net_load_min_share_of_peak_pct", "n1", "%"), whenOf(y, "net_load_min_mw"),
                  sk("hours_held", "n0")] }; })} />
              <PanelMethod at="stressRamp"><SiteLink href={METHOD_STRESS_RAMP}>Method: the views&apos; figures, keyed from the committed files</SiteLink></PanelMethod>
            </Block>
            <Block title={`${nameOf(g)}: what each fuel gave in the ${f.tight} tightest hours, ${year}`} id={anchorOf("stressTight", i, g)}>
              {(() => { const ly = stress.yearsOf(f), tl = GS.tightLines(f, ly); return tl.length ? <>
                <Lines x={ly} unit="% of installed capacity" zero name={`erw-mix-tight-${g}`} label={`${nameOf(g)}, output in the ${f.tight} tightest hours as a share of installed capacity, by year`} notes={ly.map((y) => GS.tightNote(f, y))} tip={GS.NOT.tight}
                  series={tl.map((l) => ({ name: l.name, color: FUEL_COLOR[l.fuel] ?? "var(--color-muted)", values: l.values, width: 2, digits: 1 }))} />
                {not("tight")}</> : null; })()}
              {f.years[year] ? <Table caption="Fuels in the tightest hours" file={stressFile(g, `tight_${year}`, `what each fuel gave in the ${f.tight} tightest hours, ${year}`, `Window: ${year}, the year's ${f.tight} tightest hours`)} head={["Fuel", "Mean output, MW", "Installed capacity, MW", "Output as a share of installed capacity"]}
                rows={stress.fuelRows(f, year).map((r) => { const fk = (k: string, form: Form, v: number | null, unit = "") => kv(v, form, `stress/${g}.json`, `years.${year}.${k}`, unit, r.why ?? why);
                  return { key: r.fuel, cells: [r.fuel === "nuclear" ? <span key="n" className="cursor-help border-b border-dotted border-muted" title={nuclearNote(g, year)}>{r.name}</span> : r.name,
                  fk(`tight_${r.fuel}_mw`, "n0", r.mw), fk(`capacity_${r.fuel}_mw`, "n0", r.capacity), fk(`tight_${r.fuel}_share_of_capacity_pct`, "n1", r.share, "%")] }; })} /> : <NH why={why} />}
              <PanelMethod at="stressTight"><SiteLink href={METHOD_STRESS_TIGHT}>Method: the large tables, keyed whole</SiteLink></PanelMethod>
            </Block>
            <Block title={`${nameOf(g)}: dark, calm stretches, by year`} id={anchorOf("stressCalm", i, g)}>
              {(() => { const ly = stress.yearsOf(f); return <>
                <Lines x={ly} unit="hours" zero name={`erw-mix-calm-${g}`} label={`${nameOf(g)}, the longest dark, calm stretch of each year`} notes={ly.map((y) => GS.calmNote(f, y))} tip={GS.NOT.calm}
                  series={[{ name: "The longest stretch", color: "var(--color-accent)", values: GS.valuesOf(f, ly, "calm_longest_hours"), width: 2, digits: 0 }]} />
                {not("calm")}</>; })()}
              <Table caption="Dark, calm stretches" file={stressFile(g, "calm", "dark, calm stretches, by year", `Window: the years ${ys.at(-1)} to ${ys[0]}, each its own year (hours in ${f.tz}); wind and solar below ${f.calm_pct}% of capacity`)} head={["Year", `Hours with wind and solar below ${f.calm_pct}% of capacity`, "Stretches of a day or more", "The longest", "It began", "Energy missing, MWh", "Battery fleet, MW", "Battery fleet, MWh", "Hours at full power to cover it", "Times the fleet's energy"]}
                rows={ys.map((y) => { const nb = "No battery fleet is held for this grid in that month.";
                  const ck = (k: string, form: Form, w?: string) => kv(stress.get(f, y, k), form, `stress/${g}.json`, `years.${y}.${k}`, "", w);
                  return { key: y, on: y === year, cells: [y, ck("calm_hours", "n0"), ck("calm_stretches_ge24h", "n0"), stress.get(f, y, "calm_longest_hours") === null ? <NH key="s" why={why} /> : ck("calm_longest_hours", "span"),
                  whenOf(y, "calm_longest_hours"), ck("calm_longest_missing_mwh", "n0"), ck("calm_longest_fleet_mw", "n0", nb),
                  ck("calm_longest_fleet_mwh", "n0", nb), ck("calm_longest_fleet_full_power_hours", "n1", nb),
                  ck("calm_longest_fleet_energy_multiples", "n1", nb)] }; })} />
              <PanelMethod at="stressCalm"><SiteLink href={METHOD_STRESS_CALM}>Method: the large tables, keyed whole</SiteLink></PanelMethod>
            </Block>
          </div>
        );
      })}
      <Block title={`The seven grids, ${year}`} id={GRID_ANCHOR.stressGrids}>
        <Table caption="The seven grids" file={{ panel: "grid_stress_all", part: year, title: `the seven grids, ${year}`, page,
          tables: ["grid_stress_yearly (derived: warehouse/derived/grid_stress.py, docs/methods/grid_stress.md), as the committed files site/data/stress/<grid>.json hold it"],
          filter: `iso:<grid> for the seven ISO grids, the year ${year}`, window: `Window: ${year}` }} head={["Grid", "Largest evening ramp, share of peak", "Over three hours", "Lowest net load, share of peak", "Wind in the tightest hours, share of capacity", "Solar in the tightest hours, share of capacity", "Longest dark, calm stretch"]}
          rows={stress.GRIDS.map((g) => { const f = STRESS[g]; const k = (name: string) => (f.years[year] ? stress.get(f, year, name) : null);
            const sk = (name: string, w: string) => kv(k(name), "n1", `stress/${g}.json`, `years.${year}.${name}`, "%", w);
            return { key: g, on: c.grids.includes(g), cells: [nameOf(g), sk("evening_ramp_max_share_of_peak_pct", why), sk("evening_ramp_3h_max_share_of_peak_pct", why), sk("net_load_min_share_of_peak_pct", why),
              sk("tight_wind_share_of_capacity_pct", "The grid's file reports no wind for this year, or the year is not held."), sk("tight_solar_share_of_capacity_pct", "The grid's file reports no solar for this year, or the year is not held."),
              k("calm_longest_hours") === null ? <NH key="s" why={why} /> : kv(k("calm_longest_hours"), "span", `stress/${g}.json`, `years.${year}.calm_longest_hours`)] }; })} />
        <PanelMethod at="stressGrids"><SiteLink href={METHOD_STRESS_GRIDS}>Method: the views&apos; figures, keyed from the committed files</SiteLink></PanelMethod>
      </Block>
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// availability by source: output as a share of installed capacity
// ---------------------------------------------------------------------------------------------------------------------

export function SupplyView({ c }: { c: Choice }) {
  const years = [...new Set(c.grids.flatMap((g) => Object.keys(PLUS[g].availability)))].sort();
  const year = c.year && years.includes(c.year) ? c.year : years.filter((y) => c.grids.every((g) => PLUS[g].availability[y]?.[c.season])).at(-2) ?? years.at(-1)!;
  const season = SEASON_NAMES.find(([k]) => k === c.season)![1];
  const fuels = PLUS[c.grids[0]].av_fuels;
  const series: Series[] = c.grids.flatMap((g, i) => fuels.flatMap((f) => { const v = PLUS[g].availability[year]?.[c.season]?.[f];
    return v ? [{ name: `${FUEL_WORDS[f]}${c.grids.length > 1 ? `, ${nameOf(g)}` : ""}`, color: FUEL_COLOR[f], values: v, dash: DASHES[i], width: 2 }] : []; }));
  const tightYears = [...new Set(c.grids.flatMap((g) => stress.yearsOf(STRESS[g])))].sort();
  const months = (g: Slug) => Object.keys(PLUS[g].capacity.natural_gas ?? PLUS[g].capacity.wind ?? {}).sort();
  return (
    <>
      <Block title={`Output as a share of installed capacity, by hour: ${season.toLowerCase()}, ${year}`} id="supply">
        {series.length ? <Lines x={HOURS} unit="% of installed capacity" zero height={360} name={`erw-mix-availability-${year}-${c.season}`} label={`Output as a share of installed capacity, ${season.toLowerCase()} ${year}, local hour`} series={series} />
          : <NH why={`No grid chosen holds ${season.toLowerCase()} ${year}: a season needs at least 60 held hours in every hour of the day.`} />}
        {/* session 1413: the mean, lowest and highest hour keyed by the functions that compute them (lib/mixViewCalc.ts,
            the arithmetic as it stood here); the table, to download, and its method */}
        <div id={mixViewAnchor("supplyMean", 0, "")}>
        <Table caption="Mean availability" head={["Source", ...c.grids.map((g) => `${nameOf(g)}, mean of the day`), ...c.grids.map((g) => `${nameOf(g)}, lowest hour`), ...c.grids.map((g) => `${nameOf(g)}, highest hour`)]}
          file={{ panel: "grid_supply_all", part: "mean", title: `output as a share of installed capacity: the mean, lowest and highest hour, ${season.toLowerCase()} ${year}`, page: viewPage(c, "supply", `grids=${c.grids.join(",")}&year=${year}&season=${c.season}`),
            tables: c.grids.flatMap(plusTables), filter: `iso:<grid> for ${c.grids.join(", ")}, each source`, window: `Window: ${season.toLowerCase()} ${year}, the 24 local hours of the day`,
            notes: ["Availability is a source's output (not below zero) over its installed nameplate MW that month, by local hour; a season needs at least 60 held hours in every hour of the day."] }}
          rows={fuels.map((f) => { const vs = c.grids.map((g) => MV.availOf(PLUS[g], year, c.season, f)); const no = "The grid's file does not report this source in this period, or no installed capacity is held for it.";
            const ak = (fn: MV.FilecalcFn, i: number, x: number | null) => kc(x, "n1", fn, `mixplus/${c.grids[i]}.json`, [year, c.season, f], "%", no);
            return { key: f, cells: [f === "nuclear" ? <span key="n" className="cursor-help border-b border-dotted border-muted" title={c.grids.map((g) => `${nameOf(g)}: ${nuclearNote(g, year, c.season)}`).join("\n")}>{FUEL_WORDS[f]}</span> : FUEL_WORDS[f],
              ...vs.map((v, i) => ak("avail_mean", i, MV.availMean(v))), ...vs.map((v, i) => ak("avail_min", i, MV.availMin(v))), ...vs.map((v, i) => ak("avail_max", i, MV.availMax(v)))] }; })} />
        <ViewMethod />
        </div>
      </Block>
      {c.grids.map((g, gi) => {
        const f = STRESS[g];
        // session 1413: the table (keyed by session 1166) to download, its anchor and its method, as the stress view's
        return (
          <Block key={g} title={`${nameOf(g)}: output as a share of installed capacity in each year's ${f.tight} tightest hours`} id={mixViewAnchor("supplyTight", gi, g)}>
            <Table caption="Availability in the tightest hours" head={["Source", ...tightYears]}
              file={{ panel: `grid_supply_${g}`, part: "tight", title: `${nameOf(g)}: output as a share of installed capacity in each year's ${f.tight} tightest hours`, page: viewPage(c, "supply", `grids=${c.grids.join(",")}&year=${year}&season=${c.season}`),
                tables: [`grid_stress_yearly (derived: warehouse/derived/grid_stress.py, docs/methods/grid_stress.md), as the committed file site/data/stress/${g}.json holds it (built ${f.built})`],
                filter: `iso:${g}, by year, each source`, window: `Window: the years ${tightYears[0] ?? ""} to ${tightYears.at(-1) ?? ""}, each year's ${f.tight} tightest hours` }}
              rows={["natural_gas", "coal", "nuclear", "wind", "solar", "hydro_storage"].map((fuel) => ({ key: fuel, cells: [FUEL_WORDS[fuel], ...tightYears.map((y) => {
                const v = f.years[y] ? stress.get(f, y, `tight_${fuel}_share_of_capacity_pct`) : null;
                if (v === null) return <NH key={y} why="The grid's file does not report this source in that year, the year is not held, or no installed capacity is held for it." />;
                // session 1166: keyed; nuclear's cell keeps the NRC's note first in its tip
                return <span key={y}><K v={v} form="n1" file={`stress/${g}.json`} at={`years.${y}.tight_${fuel}_share_of_capacity_pct`} note={fuel === "nuclear" ? nuclearNote(g, y) : undefined} />%</span>; })] }))} />
            <ViewMethod />
          </Block>
        );
      })}
      <Block title="Installed capacity by source, by month">
        <div className={cols(c.grids.length)}>
          {c.grids.map((g) => { const ms = months(g); const cap = PLUS[g].capacity;
            return <Card key={g} title={nameOf(g)}><HourStack x={ms} unit="MW" name={`erw-mix-capacity-${g}`} label={`${nameOf(g)}, installed nameplate capacity`} lines={[]}
              layers={["nuclear", "coal", "natural_gas", "hydro", "wind", "solar", "storage"].filter((k) => cap[k]).map((k) => ({ name: FUEL_WORDS[k], color: FUEL_COLOR[k], values: ms.map((m) => cap[k][m] ?? null) }))} /></Card>; })}
        </div>
      </Block>
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// wind and solar: forecast against actual
// ---------------------------------------------------------------------------------------------------------------------

const NO_FORECAST: [string, string, string][] = [
  ["NYISO", "not held yet", "No wind or solar forecast file was found on NYISO's public server when session 133 looked (6 October 2026)."],
  ["ISO-NE", "not held yet", "ISO-NE's seven-day wind forecast files answered HTTP 403 to a request that was not a signed-in browser (6 October 2026): not open in a usable form."],
  ["SPP", "working on it", "SPP's resource forecast was not found at the public file addresses tried (HTTP 404, 6 October 2026); its file list needs a second look."],
  ["MISO", "paused while terms are reviewed", "MISO's terms forbid automated access to its site; its pulls are paused."],
  ["PJM", "licensed source needed", "PJM publishes its data under a license and an account the ERW does not hold."],
];

/** Session 168: the grid of each row of "The other grids", for "Select grids". */
const NO_FORECAST_SLUG: Record<string, string> = { NYISO: "nyiso", "ISO-NE": "isone", SPP: "spp", MISO: "miso", PJM: "pjm" };

export function ForecastView({ c }: { c: Choice }) {
  const src = c.src;
  // session 168: the view opens with every grid (c.shown); once grids are chosen, only theirs are drawn
  const others = NO_FORECAST.filter(([name]) => (c.shown as string[]).includes(NO_FORECAST_SLUG[name]));
  return (
    <>
      {Object.entries(FORECAST.grids).filter(([slug]) => (c.shown as string[]).includes(slug)).map(([slug, g]) => {
        const s = g.sources[src];
        if (!s) return <Block key={slug} title={`${g.name}: ${src} forecast against actual`}><NH why={`No hour of ${g.name} holds both a ${src} forecast and its actual output yet.`} /></Block>;
        const months = Object.keys(s.months).sort();
        const local = (t: string) => new Date(t).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: g.tz });
        return (
          <div key={slug}>
            <Block title={`${g.name}: ${src}, forecast a day ahead against actual, by hour of the day`} id={`forecast-${slug}`}>
              <p className="mb-1 text-xs text-muted"><K v={s.all.n} form="n0" file="mix_forecast.json" at={`grids.${slug}.sources.${src}.all.n`} /> hours, {local(s.first)} to {local(s.last)}</p>
              <Lines x={HOURS} unit="MW" zero name={`erw-mix-forecast-${slug}-${src}`} label={`${g.name} ${src}, local hour`}
                series={[{ name: "Actual, mean", color: "var(--color-accent)", values: s.hours.map((h) => h?.actual ?? null), width: 2.2 }, { name: "Forecast, mean", color: "var(--color-fuel-gas)", values: s.hours.map((h) => h?.forecast ?? null), width: 2 },
                  { name: "Mean absolute error", color: "var(--color-ink)", values: s.hours.map((h) => h?.mae ?? null), dash: "dashed" }, { name: "Mean error (forecast less actual)", color: "var(--color-muted)", values: s.hours.map((h) => h?.bias ?? null), dash: "dotted" }]} />
            </Block>
            <Block title={`${g.name}: ${src} forecast error by month`}>
              {months.length > 1 ? <Bars x={months} unit="MW" name={`erw-mix-forecast-months-${slug}-${src}`} label={`${g.name} ${src}, month`}
                series={[{ name: "Mean absolute error", color: "var(--color-accent)", values: months.map((m) => s.months[m].mae) }, { name: "Mean error (forecast less actual)", color: "var(--color-ink)", values: months.map((m) => s.months[m].bias) }]} /> : null}
              {months.length > 1 ? <Heat rows={months} cols={HOURS} unit="MW mean absolute error" name={`erw-mix-forecast-heat-${slug}-${src}`} label={`${g.name} ${src}, mean absolute error`} cells={months.map((m) => s.months[m].mae_by_hour)} /> : null}
              <Table caption="Forecast error by month" head={["Month", "Hours", "Actual, mean MW", "Forecast, mean MW", "Mean error, MW", "Mean absolute error, MW", "Error as a share of mean actual"]}
                rows={[...months].reverse().map((m) => { const r = s.months[m]; const at = `grids.${slug}.sources.${src}.months.${m}`;
                  const fk = (x: number, f: string, form: Form = "n0") => <K v={x} form={form} file="mix_forecast.json" at={`${at}.${f}`} />;
                  return { key: m, cells: [m, fk(r.n, "n"), fk(r.actual, "actual"), fk(r.forecast, "forecast"), fk(r.bias, "bias", "sn0"), fk(r.mae, "mae"), r.actual > 0 ? `${n1((100 * r.mae) / r.actual)}%` : ""] }; })} />
            </Block>
          </div>
        );
      })}
      {others.length ? (
        <Block title="The other grids">
          <Table caption="Grids with no forecast held" head={["Grid", "Wind and solar forecast"]} rows={others.map(([name, words, why]) => ({ key: name, cells: [name, <NH key="w" why={why} words={words} />] }))} />
        </Block>
      ) : null}
    </>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// since 2001: net generation by state and fuel, by year
// ---------------------------------------------------------------------------------------------------------------------

export function HistoryView({ c }: { c: Choice }) {
  const states = c.states.filter((s) => HISTORY.states[s]);
  const fuels = ["coal", "natural_gas", "nuclear", "wind", "solar", "hydro", "other_renewables", "oil_and_other"];
  const whole = (s: string) => Object.keys(HISTORY.states[s]).filter((y) => HISTORY.states[s][y].months === 12).sort();
  const years = [...new Set(states.flatMap(whole))].sort();
  const total = (s: string, y: string) => MV.historyTotal(HISTORY, s, y);   // session 1413: the sum as it stood here, in lib/mixViewCalc.ts
  const at = (s: string, y: string, f: string) => { const r = HISTORY.states[s][y]; if (!r || r.months !== 12 || r[f] === undefined) return null; return c.norm === "peak" ? Math.round((1000 * r[f]) / total(s, y)) / 10 : Math.round(r[f] / 1e5) / 10; };
  const unit = c.norm === "peak" ? "% of the state's generation" : "million MWh a year";
  const marks = [years[0], "2010", "2020", years.at(-1)!].filter((y, i, a) => y && a.indexOf(y) === i && years.includes(y));
  return (
    <>
      <Block title={`Net generation by fuel, by year since ${HISTORY.first}`} id="history">
        <Lines x={years} unit={unit} zero height={380} name="erw-mix-history" label="Net generation by fuel, year"
          series={states.flatMap((s, i) => fuels.filter((f) => years.some((y) => (at(s, y, f) ?? 0) > 0)).map((f) => ({ name: `${FUEL_WORDS[f]}${states.length > 1 ? `, ${STATES[s] ?? s}` : ""}`, color: FUEL_COLOR[f], values: years.map((y) => at(s, y, f)), dash: DASHES[i], width: f === "coal" || f === "natural_gas" ? 2.4 : 1.4 })))} />
      </Block>
      {states.map((s, i) => (
        // session 1413: each share and each million MWh keyed by the function that computes it from the file (lib/mixViewCalc.ts
        // historyCell, the arithmetic as it stood here); the table, to download, its anchor and its method
        <Block key={s} title={`${STATES[s] ?? s}: shares of net generation`} id={mixViewAnchor("historyShares", i, s.toLowerCase())}>
          <Table caption={`${STATES[s] ?? s}, shares by fuel`} head={["Fuel", ...marks.flatMap((y) => [`${y}, share`, `${y}, million MWh`])]}
            file={{ panel: `grid_history_${s.toLowerCase()}`, title: `${STATES[s] ?? s}: shares of net generation`, page: viewPage(c, "history", `states=${states.join(",")}`),
              tables: [`state_generation_mix_monthly (EIA-923) added up by calendar year, state and fuel group, as the committed file site/data/mix_history.json holds it (warehouse/derived/mix_views.py, built ${HISTORY.built})`],
              filter: `${s}, each fuel group`, window: `Window: the years ${marks.join(", ")}, each a calendar year of twelve months`, notes: ["A share is of the sum of the state's fuel groups in the year; million MWh is the year's net generation over one million."] }}
            rows={HISTORY.fuels.filter((f) => marks.some((y) => (HISTORY.states[s][y]?.[f] ?? 0) !== 0)).map((f) => ({ key: f, cells: [<span key="n"><span className="mr-1.5 inline-block h-2.5 w-2.5" style={{ background: FUEL_COLOR[f] }} />{FUEL_WORDS[f] ?? f}</span>,
              ...marks.flatMap((y) => { const h = MV.historyCell(HISTORY, s, y, f), no = "EIA lists no generation of this fuel in this state that year.";
                return [kc(h.share, "n1", "hist_share", "mix_history.json", [s, y, f], "%", no), kc(h.mwh, "n1", "hist_mwh", "mix_history.json", [s, y, f], "", no)]; })] }))} />
          <ViewMethod />
        </Block>
      ))}
    </>
  );
}
