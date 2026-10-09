"use client";

// Session 167: the project map, one page. The reader's choices (kind, grid, technology, status, state, size), every
// list a multi-select with "Select all" and "Clear", kept in the address; the summary sentence and the totals by status
// of what is chosen; the map with hover, a click on a state that chooses it, a click on a unit that opens its card; the
// table by technology of what is chosen. Everything is computed in the browser from the page's own copy of the tables
// (data/map.json, lib/projectmap.ts); nothing is asked of a server, the card included.
import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { geoAlbersUsa } from "d3-geo";
import { baseStyle, token, useEChart } from "@/components/echarts";
import { InputPanel, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { STATES } from "@/lib/regions";
import {
  COLOR, COLOR_KEY, EVERYTHING, KIND, cardOf, clickState, dateOf, one, optionsOf, parseChoice, queryOf, select, sizeOf, tidy, toggle, totals, whole,
  type Choice, type Filter, type MapFile,
} from "@/lib/projectmap";

const NAME_TO_CODE: Record<string, string> = Object.fromEntries(Object.entries(STATES).map(([code, name]) => [name, code]));
const never = () => () => {};
/** Point size in pixels: area grows with MW, clamped for legibility (the older maps' rule). */
const size = (mw: number | null) => Math.min(18, Math.max(3, 2 + Math.sqrt(Math.max(mw ?? 0, 0)) * 0.2));
// us-atlas's albers files are drawn with geoAlbersUsa().scale(1300).translate([487.5, 305]) on a 975 x 610 plane; the
// rows use the same projection, so they sit on the state outlines (as both earlier versions did)
const projection = geoAlbersUsa().scale(1300).translate([487.5, 305]);
const HEAVY = new Set(["u", "v", "ts"]);   // EIA's statuses under construction: the heavier ring
const KIND_WORD = ["Generating units", "Generating units", "Queue positions", "Datacenters"];

const and = (words: string[]) => (words.length < 2 ? words.join("") : `${words.slice(0, -1).join(", ")} and ${words.at(-1)}`);

export function ProjectMap({ file: f, statesGeo }: { file: MapFile; statesGeo: unknown }) {
  // the choice: what the address says until the reader changes it; every change is written back to the address
  const search = useSyncExternalStore(never, () => window.location.search, () => "");
  const fromAddress = useMemo(() => parseChoice(search, f), [search, f]);
  const [own, setOwn] = useState<Choice | null>(null);
  const choice = own ?? fromAddress;
  const change = useCallback((fn: (c: Choice) => Choice) => setOwn((prev) => fn(prev ?? fromAddress)), [fromAddress]);
  useEffect(() => {
    if (own) window.history.replaceState(window.history.state, "", `${window.location.pathname}${queryOf(own, f)}${window.location.hash}`);
  }, [own, f]);
  const [card, setCard] = useState<number | null>(null);

  const xy = useMemo(() => {
    const x: (number | null)[] = [], y: (number | null)[] = [];
    for (let i = 0; i < f.k.length; i++) {
      const p = f.la[i] === null || f.lo[i] === null ? null : projection([f.lo[i] as number, f.la[i] as number]);
      x.push(p ? Math.round(p[0] * 10) / 10 : null);
      y.push(p ? Math.round(p[1] * 10) / 10 : null);
    }
    return { x, y };
  }, [f]);
  const picked = useMemo(() => select(f, choice), [f, choice]);
  const sum = useMemo(() => totals(f, picked), [f, picked]);
  const drawn = useMemo(() => picked.filter((i) => xy.x[i] !== null), [picked, xy]);
  const kindOn = (k: number) => choice.kind === null || choice.kind.includes(k);

  // the chart's handlers read the newest setters through refs (the chart is built once and redrawn)
  const act = useRef({ change, setCard });
  useEffect(() => { act.current = { change, setCard }; }, [change]);
  const chosenStates = choice.state;
  const box = useEChart(
    (chart, lib) => {
      lib.registerMap("erw-us-one", statesGeo);
      const st = baseStyle();
      const panel = token("panel"), paper = token("paper"), rule = token("rule"), ink = token("ink"), muted = token("muted"), accent = token("accent");
      const color = f.techs.map((t) => token(`var(${COLOR[t.slug] ?? "--color-fuel-other"})`));
      const byKind = f.kinds.map(() => [] as number[]);
      for (const i of drawn) byKind[f.k[i]].push(i);
      const series = f.kinds.map((k, ki) => ({
        name: k.name, type: "scatter", coordinateSystem: "geo", progressive: 4000, emphasis: { scale: 1.6 },
        data: byKind[ki].map((i) => {
          const c = color[f.t[i]];
          if (ki === KIND.datacenter) return { value: [xy.x[i], xy.y[i], i], symbol: "diamond", symbolSize: 9, itemStyle: { color: panel, borderColor: ink, borderWidth: 1.2, opacity: 0.95 } };
          if (ki === KIND.queue) return { value: [xy.x[i], xy.y[i], i], symbol: "triangle", symbolSize: size(f.mw[i]) + 2, itemStyle: { color: "rgba(0,0,0,0)", borderColor: c, borderWidth: 1, opacity: 0.85 } };
          if (ki === KIND.planned) return { value: [xy.x[i], xy.y[i], i], symbol: "emptyCircle", symbolSize: size(f.mw[i]), itemStyle: { color: c, borderColor: c, borderWidth: HEAVY.has(f.statuses[f.st[i]].slug) ? 1.6 : 1, opacity: 0.9 } };
          return { value: [xy.x[i], xy.y[i], i], symbol: "circle", symbolSize: size(f.mw[i]), itemStyle: { color: c, borderColor: panel, borderWidth: 0.4, opacity: 0.78 } };
        }),
      }));
      const chosen = (chosenStates ?? []).map((s) => STATES[f.states[s]]).filter(Boolean);
      chart.setOption({
        animation: false, textStyle: st.textStyle,
        toolbox: { ...st.toolbox("erw-project-map"), feature: { restore: { title: "Reset zoom" }, saveAsImage: st.toolbox("erw-project-map").feature.saveAsImage } },
        tooltip: {
          ...st.tooltip, trigger: "item",
          formatter: (p: { componentType: string; name?: string; value?: number[] }) => {
            if (p.componentType === "geo") return `${p.name}: click to choose it, click again to take it away`;
            const i = (p.value as number[])[2];
            const kind = f.k[i], mw = f.mw[i];
            const name = (f.names[f.n[i]] || f.id[i]).replace(/</g, "&lt;");
            const what = kind === KIND.datacenter ? "Datacenter" : f.techs[f.t[i]].name;
            const st2 = f.statuses[f.st[i]].name;
            const grid = f.grids[f.g[i]];
            return `<div style="max-width:17rem;white-space:normal"><strong>${name}</strong><br/>`
              + `${what}, ${mw === null ? "MW not stated" : `${one(mw)} MW${kind === KIND.queue ? " requested" : ""}`}<br/>`
              + `<span style="color:${muted}">${kind === KIND.queue ? "Queue position, " : ""}${st2}, ${f.states[f.s[i]] || "state not stated"}${grid.slug === "none" ? "" : `, ${grid.name}`}${f.d[i] ? `, ${dateOf(f.d[i])}` : ""}. Click for its card.</span></div>`;
          },
        },
        geo: {
          map: "erw-us-one", roam: true, scaleLimit: { min: 1, max: 20 }, projection: { project: (p: number[]) => p, unproject: (p: number[]) => p },
          top: 24, bottom: 4, left: 4, right: 4, itemStyle: { areaColor: paper, borderColor: rule, borderWidth: 0.7 }, emphasis: { itemStyle: { areaColor: panel }, label: { show: false } },
          select: { disabled: true }, tooltip: { show: true },
          regions: chosen.map((name) => ({ name, itemStyle: { areaColor: panel, borderColor: accent, borderWidth: 1.5 } })),
        },
        series,
      }, true);
      chart.off("click");
      chart.on("click", (p) => {
        if (p.componentType === "series") { act.current.setCard((p.value as number[])[2]); return; }
        if (p.componentType !== "geo") return;
        const code = NAME_TO_CODE[p.name as string];
        const s = code ? f.states.indexOf(code) : -1;
        if (s >= 0) act.current.change((c) => ({ ...c, state: clickState(c.state, s, f.states.length) }));
      });
    },
    [drawn, chosenStates, xy, f, statesGeo],
  );

  const cardBox = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (card !== null && cardBox.current && window.innerWidth < 1024) cardBox.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [card]);

  const set = (which: Filter, list: number[] | null) => change((c) => ({ ...c, [which]: tidy(list, optionsOf(f, which).length) }));
  const reset = () => { setOwn({ ...EVERYTHING }); setCard(null); };
  const sized = sizeOf(choice.min, -1) >= 0 || sizeOf(choice.max, -1) >= 0;
  const notDrawn = picked.length - drawn.length;
  const queueOn = kindOn(KIND.queue);

  return (
    <div className="grid gap-8 lg:grid-cols-[260px_minmax(0,1fr)]">
      <aside>
        <InputPanel title="Choose" note={<>The map, the totals and the table follow these choices, and the address keeps them, so a view can be shared. Nothing you choose leaves this page.</>}>
          <Multi which="kind" label="Kind" names={f.kinds.map((k) => k.name)} list={choice.kind} set={set} open />
          <Multi which="grid" label="Grid" names={f.grids.map((g) => g.name)} list={choice.grid} set={set} />
          <Multi which="tech" label="Technology" names={f.techs.map((t) => t.name)} list={choice.tech} set={set} />
          <Multi which="status" label="Status" names={f.statuses.map((s) => s.name)} list={choice.status} set={set}
            shown={f.statuses.map((s) => kindOn(s.kind))} groups={f.statuses.map((s) => KIND_WORD[s.kind])} />
          <Multi which="state" label="State (or click one on the map)" names={f.states.map((s) => s || "Not stated")} list={choice.state} set={set} columns
            titles={f.states.map((s) => STATES[s] ?? "No state in the source")} />
          <div className="mt-3 text-xs uppercase tracking-wide text-muted">Size, MW</div>
          <div className="mt-1 flex items-center gap-2 text-sm">
            <input className="w-20 border border-rule bg-white px-2 py-1" inputMode="decimal" placeholder="from" aria-label="Smallest size, MW" value={choice.min}
              onChange={(e) => { const v = e.target.value; change((c) => ({ ...c, min: v })); }} data-map-choice="min" />
            <span className="text-muted">to</span>
            <input className="w-20 border border-rule bg-white px-2 py-1" inputMode="decimal" placeholder="to" aria-label="Largest size, MW" value={choice.max}
              onChange={(e) => { const v = e.target.value; change((c) => ({ ...c, max: v })); }} data-map-choice="max" />
          </div>
          <button type="button" onClick={reset} className="mt-4 border border-rule bg-white px-3 py-1 text-sm hover:text-accent" data-map-reset="1">Reset</button>
        </InputPanel>
      </aside>

      <div className="min-w-0">
        <p className="mb-6 max-w-3xl text-lg leading-relaxed" data-map-summary="1">
          <Sentence f={f} choice={choice} sum={sum} sized={sized} />
        </p>
        <div className="mb-10 space-y-5" data-map-totals="1">
          {[0, 2, 3].map((group) => {
            const tiles = f.statuses.map((s, i) => ({ s, t: sum.byStatus[i] })).filter(({ s, t }) => t.rows > 0 && (group === 0 ? s.kind <= KIND.planned : s.kind === group));
            if (!tiles.length) return null;
            return (
              <div key={group}>
                <h3 className="mb-2 text-xs uppercase tracking-wide text-muted">{group === 0 ? "Generating units, by EIA's status" : group === KIND.queue ? "Queue positions, by status (MW requested)" : "Datacenters, by status (MW where stated)"}</h3>
                <div className="grid grid-cols-2 gap-x-5 gap-y-4 sm:grid-cols-3 xl:grid-cols-4">
                  {tiles.map(({ s, t }) => (
                    <Tile key={s.slug} label={s.name} value={<span data-map-total={s.slug}>{t.withMw ? whole(t.mw) : "not stated"}</span>} unit={t.withMw ? "MW" : undefined}
                      note={s.kind === KIND.queue ? count(t.rows, "position") : s.kind === KIND.datacenter ? <>{count(t.rows, "facility", "facilities")}, {t.withMw ? `MW stated at ${whole(t.withMw)}` : "no MW stated"}</> : count(t.rows, "unit")} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <ToolSection title="The map" id="map"
          note={<>Drag to move, scroll or pinch to zoom, hover for a row, click a unit for its card, click a state to choose it.{notDrawn ? <> {whole(notDrawn)} of the rows chosen have no place on the drawing (Puerto Rico, or no location in the source); they are in the totals and the table.</> : null}</>}>
          <div ref={box} role="img" aria-label={`Map of ${whole(drawn.length)} rows chosen`} className="w-full border border-rule bg-panel"
            style={{ aspectRatio: "975 / 640", minHeight: 240 }} data-map-drawn={drawn.length} />
          <Key f={f} picked={picked} />
          {queueOn && f.held.length ? (
            <ul className="mt-1 text-xs text-muted" data-map-held="1">
              {f.held.map((h) => (
                <li key={h.grid} title={`${h.name}'s queue positions are not drawn or counted on this map: ${h.words}. The Method note says why.`}>
                  <span className="border-b border-dotted border-muted">{h.name} queue positions: {h.words}</span>
                </li>
              ))}
            </ul>
          ) : null}
          <div ref={cardBox} className="mt-4">
            <UnitCard f={f} i={card} close={() => setCard(null)} />
          </div>
        </ToolSection>

        <ByTechnology f={f} sum={sum} kindOn={kindOn} />
      </div>
    </div>
  );
}

const count = (n: number, word: string, words = `${word}s`) => `${whole(n)} ${n === 1 ? word : words}`;

/** A total by status: version 2's headline number, smaller, so that a status for each of EIA's codes fits a phone. */
function Tile({ label, value, unit, note }: { label: string; value: ReactNode; unit?: string; note: ReactNode }) {
  return (
    <div className="border-t-2 border-accent pt-1.5">
      <div className="text-[11px] uppercase leading-snug tracking-wide text-muted">{label}</div>
      <div className="mt-0.5 font-serif text-xl tabular-nums text-ink sm:text-2xl">{value}{unit ? <span className="ml-1 font-sans text-xs text-muted">{unit}</span> : null}</div>
      <div className="text-xs leading-snug text-muted">{note}</div>
    </div>
  );
}

/** One list of the panel: every option a checkbox, with "Select all" and "Clear". Folded, its summary says how much is chosen. */
function Multi({ which, label, names, list, set, open, shown, groups, columns, titles }: {
  which: Filter; label: string; names: string[]; list: number[] | null; set: (w: Filter, l: number[] | null) => void; open?: boolean;
  shown?: boolean[]; groups?: string[]; columns?: boolean; titles?: string[];
}) {
  const said = list === null ? "all" : list.length === 0 ? "none" : list.length === 1 ? names[list[0]] : `${list.length} of ${names.length}`;
  const on = (i: number) => list === null || list.includes(i);
  const items: ReactNode[] = [];
  let group = "";
  names.forEach((name, i) => {
    if (shown && !shown[i]) return;
    if (groups && groups[i] !== group) {
      group = groups[i];
      items.push(<li key={`g-${group}`} className="col-span-full mt-1 text-[11px] uppercase tracking-wide text-muted">{group}</li>);
    }
    items.push(
      <li key={i}>
        <label className="flex items-start gap-1.5 py-0.5 text-sm normal-case tracking-normal text-ink" title={titles?.[i]}>
          <input type="checkbox" className="mt-1" checked={on(i)} onChange={() => set(which, toggle(list, i, names.length))} data-map-option={`${which}|${i}`} />
          <span>{name}</span>
        </label>
      </li>,
    );
  });
  return (
    <details className="mt-3 border-t border-rule pt-2" open={open} data-map-filter={which}>
      <summary className="cursor-pointer text-xs uppercase tracking-wide text-muted">
        {label}: <span className="normal-case tracking-normal text-ink" data-map-said={which}>{said}</span>
      </summary>
      <div className="mt-1 flex gap-3 text-xs">
        <button type="button" className="underline hover:text-accent" onClick={() => set(which, null)} data-map-all={which}>Select all</button>
        <button type="button" className="underline hover:text-accent" onClick={() => set(which, [])} data-map-clear={which}>Clear</button>
      </div>
      <ul className={columns ? "mt-1 grid max-h-56 grid-cols-3 gap-x-2 overflow-y-auto" : "mt-1"}>{items}</ul>
    </details>
  );
}

function Sentence({ f, choice, sum, sized }: { f: MapFile; choice: Choice; sum: ReturnType<typeof totals>; sized: boolean }) {
  if (sum.rows === 0) return <>Nothing on this map matches these choices.</>;
  const grids = choice.grid === null ? "every grid" : choice.grid.length === 1 ? f.grids[choice.grid[0]].name : `${whole(choice.grid.length)} grids`;
  const states = choice.state === null ? "every state" : choice.state.length === 1 ? (STATES[f.states[choice.state[0]]] ?? "no state stated") : `${whole(choice.state.length)} states`;
  const narrowed = [choice.tech !== null ? "technologies" : "", choice.status !== null ? "statuses" : "", sized ? "sizes" : ""].filter(Boolean);
  const [op, pl, q, dc] = sum.byKind;
  const units = op.rows + pl.rows;
  const unitWord = op.rows && pl.rows ? "generating units" : op.rows ? "operating units" : "planned units";
  const parts: ReactNode[] = [];
  if (units) parts.push(<span key="u"><strong>{whole(units)}</strong> {unitWord} of EIA&apos;s inventory of {f.vintage}, <strong>{whole(op.mw + pl.mw)} MW</strong></span>);
  if (q.rows) parts.push(<span key="q"><strong>{whole(q.rows)}</strong> queue positions, <strong>{whole(q.mw)} MW</strong> requested</span>);
  if (dc.rows) parts.push(<span key="d"><strong>{whole(dc.rows)}</strong> datacenters, {dc.withMw ? <><strong>{whole(dc.mw)} MW</strong> stated at {whole(dc.withMw)} of them</> : <>no MW stated</>}</span>);
  return (
    <>
      In {grids} and {states}{narrowed.length ? `, of the ${and(narrowed)} chosen` : ""}, the map holds{" "}
      {parts.map((p, i) => <span key={i}>{i ? (i === parts.length - 1 ? "; and " : "; ") : ""}{p}</span>)}.
    </>
  );
}

/** The plain key of the marks: what a shape and a color mean, for what is chosen. It toggles nothing. */
function Key({ f, picked }: { f: MapFile; picked: number[] }) {
  const kinds = new Set<number>(), hues = new Set<string>();
  for (const i of picked) { kinds.add(f.k[i]); if (f.k[i] !== KIND.datacenter) hues.add(COLOR[f.techs[f.t[i]].slug] ?? "--color-fuel-other"); }
  const mark = (shape: string) => (
    <svg aria-hidden="true" width="12" height="12" viewBox="0 0 12 12" className="inline-block align-middle">
      {shape === "dot" ? <circle cx="6" cy="6" r="4.5" fill="currentColor" /> : shape === "ring" ? <circle cx="6" cy="6" r="4.2" fill="none" stroke="currentColor" strokeWidth="1.2" />
        : shape === "heavy" ? <circle cx="6" cy="6" r="4" fill="none" stroke="currentColor" strokeWidth="2" /> : shape === "triangle" ? <path d="M6 1.5 L10.5 10 L1.5 10 Z" fill="none" stroke="currentColor" strokeWidth="1.1" />
          : <path d="M6 1 L11 6 L6 11 L1 6 Z" fill="white" stroke="currentColor" strokeWidth="1.2" />}
    </svg>
  );
  return (
    <div className="mt-2 text-xs" data-map-key="1">
      <ul className="flex flex-wrap gap-x-4 gap-y-1">
        {kinds.has(KIND.operating) ? <li className="inline-flex items-center gap-1.5">{mark("dot")}operating unit</li> : null}
        {kinds.has(KIND.planned) ? <li className="inline-flex items-center gap-1.5">{mark("ring")}planned unit</li> : null}
        {kinds.has(KIND.planned) ? <li className="inline-flex items-center gap-1.5">{mark("heavy")}planned, under construction</li> : null}
        {kinds.has(KIND.queue) ? <li className="inline-flex items-center gap-1.5">{mark("triangle")}queue position, at its county&apos;s point</li> : null}
        {kinds.has(KIND.datacenter) ? <li className="inline-flex items-center gap-1.5">{mark("diamond")}datacenter</li> : null}
        <li className="text-muted">size: MW</li>
      </ul>
      <ul className="mt-1 flex flex-wrap gap-x-4 gap-y-1">
        {COLOR_KEY.filter((c) => hues.has(c.color)).map((c) => (
          <li key={c.color} className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: `var(${c.color})` }} />{c.label}</li>
        ))}
      </ul>
    </div>
  );
}

/** Version 1's card (session 16), read from the page's own file. */
function UnitCard({ f, i, close }: { f: MapFile; i: number | null; close: () => void }) {
  if (i === null) {
    return (
      <aside className="border border-dashed border-rule bg-paper p-3 text-sm text-muted" data-map-card="empty">
        Click a unit on the map for its card: name, capacity, status, operator or developer, date and the table it comes from.
      </aside>
    );
  }
  const c = cardOf(f, i);
  return (
    <aside className="border border-rule bg-paper p-3 text-sm" aria-live="polite" data-map-card={c.id}>
      <div className="mb-1 flex items-start justify-between gap-2">
        <h3 className="font-serif text-lg leading-tight" data-card-name="1">{c.name}</h3>
        <button type="button" onClick={close} className="px-1 text-muted hover:text-accent" aria-label="Close">x</button>
      </div>
      <div className="mb-2 break-all font-mono text-xs text-muted">{c.id}</div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
        {c.rows.map((r) => (
          <div key={r.key} className="contents">
            <dt className="text-xs text-muted">{r.label}</dt>
            <dd className="min-w-0 break-words" data-card-field={r.key}>{r.table ? <a href={`/data#${r.value}`} className="font-mono underline">{r.value}</a> : r.value}</dd>
          </div>
        ))}
      </dl>
      {c.stories.length ? (
        <div className="mt-2 text-xs" data-card-field="stories">
          Stories:{" "}
          {c.stories.map((u, k) => <a key={u} href={u} className="mr-2 underline" rel="noreferrer" target="_blank">{k + 1}</a>)}
        </div>
      ) : null}
      <p className="mt-2 text-xs text-muted" data-card-field="read_from">
        Read from the ERW table <code className="font-mono">{c.table}</code>{c.vintage ? `, vintage ${c.vintage}` : ""}, in the page&apos;s own copy built {c.built.slice(0, 10)}.
      </p>
    </aside>
  );
}

/** Version 1's table (session 16): count and MW by technology group and kind, now of what is chosen. Datacenters have no
 *  technology; they are not in it. */
function ByTechnology({ f, sum, kindOn }: { f: MapFile; sum: ReturnType<typeof totals>; kindOn: (k: number) => boolean }) {
  const kinds = [KIND.operating, KIND.planned, KIND.queue].filter((k) => kindOn(k));
  const rows = f.techs.map((t, ti) => ({ t, cells: kinds.map((k) => sum.byTech[ti][k]) })).filter((r) => r.t.slug !== "datacenter" && r.cells.some((c) => c.rows > 0));
  const head: ReactNode[] = ["Technology group"];
  for (const k of kinds) head.push(<span key={`n${k}`}>{f.kinds[k].name}</span>, <span key={`m${k}`}>{k === KIND.queue ? "MW requested" : "MW"}</span>);
  return (
    <ToolSection title="By technology" id="by-technology">
      {rows.length ? (
        <ToolTable caption="Count and MW by technology group and kind, of what is chosen" minWidth={kinds.length > 2 ? 640 : 420} head={head}
          rows={rows.map((r) => ({
            key: r.t.slug,
            cells: [
              <span key="t" className="inline-flex items-center gap-2"><span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: `var(${COLOR[r.t.slug] ?? "--color-fuel-other"})` }} />{r.t.name}</span>,
              ...r.cells.flatMap((c, j) => [
                <span key={`n${j}`} data-tech-count={`${r.t.slug}|${f.kinds[kinds[j]].slug}`}>{c.rows ? whole(c.rows) : <span className="text-muted">0</span>}</span>,
                <span key={`m${j}`} className="text-muted">{c.rows ? whole(c.mw) : ""}</span>,
              ]),
            ],
          }))} />
      ) : (
        <p className="text-sm text-muted" data-tech-none="1">No generating unit or queue position is chosen.</p>
      )}
    </ToolSection>
  );
}
