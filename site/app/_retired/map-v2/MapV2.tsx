"use client";

// Session 105: the project map, version 2. The reader's choices (grid, technology, status, size), the map, the totals
// of what is selected, the queue's active capacity for the same grid beside them, and a table of the selected units.
// Everything is computed in the browser from the page's own copy of EIA's inventory; nothing is asked of a server.
import { useMemo, useState } from "react";
import { baseStyle, token, useEChart } from "@/components/echarts";
import { HeadlineNumber, HeadlineRow, InputPanel, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { COLOR, EVERY, one, queueRows, select, sizeOf, totals, whole, type MapData, type QueueViews } from "@/lib/map2";

const SHOWN = 50;   // rows of the table shown at first, largest first

/** Point size in pixels: area grows with MW, clamped for legibility (the older map's rule). */
const size = (mw: number) => Math.min(18, Math.max(3, 2 + Math.sqrt(Math.max(mw, 0)) * 0.2));

export function MapV2({ data, queue, queueVintage }: { data: MapData; queue: QueueViews; queueVintage: string }) {
  const [grid, setGrid] = useState(-1);
  const [tech, setTech] = useState(-1);
  const [status, setStatus] = useState(-1);
  const [min, setMin] = useState("");
  const [max, setMax] = useState("");
  const [all, setAll] = useState(false);

  const picked = useMemo(() => select(data, { grid, tech, status, min: sizeOf(min, EVERY.min), max: sizeOf(max, EVERY.max) }), [data, grid, tech, status, min, max]);
  const sum = useMemo(() => totals(data, picked), [data, picked]);
  const drawn = useMemo(() => picked.filter((i) => data.x[i] !== null), [data, picked]);
  const gridSlug = grid < 0 ? "all" : data.grids[grid].slug;
  const techSlug = tech < 0 ? "all" : data.techs[tech].slug;
  const qrows = useMemo(() => queueRows(queue, gridSlug, techSlug), [queue, gridSlug, techSlug]);
  const where = grid < 0 ? "every grid" : data.grids[grid].name;
  const what = tech < 0 ? "units of every technology" : `${data.techs[tech].name.toLowerCase()} units`;
  const which = status < 0 ? "operating and planned" : data.statuses[status].name.toLowerCase();

  const box = useEChart(
    (chart, lib) => {
      lib.registerMap("erw-us-v2", data.statesGeo as unknown);
      const st = baseStyle();
      const panel = token("panel"), paper = token("paper"), rule = token("rule"), ink = token("ink"), muted = token("muted");
      const color = data.techs.map((t) => token(`var(${COLOR[t.slug]})`));
      // one series a status: a dot for operating, a ring for under construction and for planned
      const series = data.statuses.map((s, si) => ({
        name: s.name, type: "scatter", coordinateSystem: "geo", progressive: 4000,
        symbol: si === 0 ? "circle" : "emptyCircle", itemStyle: { color: si === 0 ? ink : muted }, emphasis: { scale: 1.6 },
        data: drawn.filter((i) => data.st[i] === si).map((i) => ({
          value: [data.x[i], data.y2[i], i], symbol: si === 0 ? "circle" : "emptyCircle", symbolSize: size(data.mw[i]),
          itemStyle: si === 0 ? { color: color[data.t[i]], borderColor: panel, borderWidth: 0.4, opacity: 0.78 }
            : { color: color[data.t[i]], borderColor: color[data.t[i]], borderWidth: si === 1 ? 1.6 : 1, opacity: 0.9 },
        })),
      }));
      chart.setOption({
        animation: false, textStyle: st.textStyle,
        toolbox: { ...st.toolbox("erw-project-map-v2"), feature: { restore: { title: "Reset zoom" }, saveAsImage: st.toolbox("erw-project-map-v2").feature.saveAsImage } },
        legend: { top: 0, left: 0, right: 70, textStyle: { color: ink, fontSize: 11 } },
        tooltip: {
          ...st.tooltip, trigger: "item",
          formatter: (p: { componentType: string; name?: string; value?: number[] }) => {
            if (p.componentType === "geo") return `${p.name}`;
            const i = (p.value as number[])[2];
            return `<div style="max-width:17rem;white-space:normal"><strong>${data.names[data.n[i]].replace(/</g, "&lt;")}</strong><br/>`
              + `${data.techs[data.t[i]].name}, ${one(data.mw[i])} MW<br/>`
              + `<span style="color:${muted}">${data.statuses[data.st[i]].name}, ${data.states[data.s[i]]}, ${data.grids[data.g[i]].name}${data.y[i] ? `, ${data.y[i]}` : ""}</span></div>`;
          },
        },
        geo: {
          map: "erw-us-v2", roam: true, scaleLimit: { min: 1, max: 20 }, projection: { project: (p: number[]) => p, unproject: (p: number[]) => p },
          top: 30, bottom: 4, itemStyle: { areaColor: paper, borderColor: rule, borderWidth: 0.7 }, emphasis: { itemStyle: { areaColor: panel }, label: { show: false } },
          select: { disabled: true }, tooltip: { show: true },
        },
        series,
      }, true);
    },
    [drawn, data],
  );

  const sel = "mt-1 w-full border border-rule bg-white px-2 py-1 text-sm";
  const rows = all ? picked : picked.slice(0, SHOWN);
  return (
    <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
      <aside>
        <InputPanel title="Choose" note={<>The map, the totals and the table below follow these four choices. Nothing you choose leaves this page.</>}>
          <label className="block text-xs uppercase tracking-wide text-muted">Grid
            <select className={sel} value={grid} onChange={(e) => setGrid(Number(e.target.value))} data-map-choice="grid">
              <option value={-1}>Every grid</option>
              {data.grids.map((g, i) => <option key={g.slug} value={i}>{g.name}</option>)}
            </select>
          </label>
          <label className="mt-3 block text-xs uppercase tracking-wide text-muted">Technology
            <select className={sel} value={tech} onChange={(e) => setTech(Number(e.target.value))} data-map-choice="tech">
              <option value={-1}>Every technology</option>
              {data.techs.map((t, i) => <option key={t.slug} value={i}>{t.name}</option>)}
            </select>
          </label>
          <label className="mt-3 block text-xs uppercase tracking-wide text-muted">Status
            <select className={sel} value={status} onChange={(e) => setStatus(Number(e.target.value))} data-map-choice="status">
              <option value={-1}>Operating and planned</option>
              {data.statuses.map((s, i) => <option key={s.slug} value={i}>{s.name}</option>)}
            </select>
          </label>
          <div className="mt-3 text-xs uppercase tracking-wide text-muted">Size, MW</div>
          <div className="mt-1 flex items-center gap-2 text-sm">
            <input className="w-20 border border-rule bg-white px-2 py-1" inputMode="decimal" placeholder="from" aria-label="Smallest size, MW" value={min} onChange={(e) => setMin(e.target.value)} data-map-choice="min" />
            <span className="text-muted">to</span>
            <input className="w-20 border border-rule bg-white px-2 py-1" inputMode="decimal" placeholder="to" aria-label="Largest size, MW" value={max} onChange={(e) => setMax(e.target.value)} data-map-choice="max" />
          </div>
        </InputPanel>
      </aside>

      <div className="min-w-0">
        <p className="mb-6 max-w-3xl text-lg leading-relaxed" data-map-summary="1">
          {sum.units === 0
            ? <>No unit of the inventory matches these choices.</>
            : <>In {where}, EIA&apos;s inventory of {data.vintage} holds <strong>{whole(sum.units)}</strong> {which} {what}{sizeOf(min, -1) >= 0 || sizeOf(max, -1) >= 0 ? " of the size chosen" : ""}, <strong>{whole(sum.mw)} MW</strong> in all.</>}
        </p>
        <HeadlineRow>
          {data.statuses.map((s, i) => (
            <HeadlineNumber key={s.slug} label={s.name} value={<span data-map-total={s.slug}>{whole(sum.byStatus[i].mw)}</span>} unit="MW" note={<>{whole(sum.byStatus[i].units)} units</>} />
          ))}
        </HeadlineRow>

        <ToolSection title="The map" id="map"
          note={<>A dot is an operating unit; a ring is one under construction (the heavier ring) or planned. Its color is its technology and its size grows with its MW. Drag to move, scroll to zoom, hover for a unit.
            {picked.length !== drawn.length ? <> {whole(picked.length - drawn.length)} of the selected units are in Puerto Rico, which this map does not draw; they are in the totals and the table.</> : null}</>}>
          <div ref={box} role="img" aria-label={`Map of ${whole(drawn.length)} generating units`} style={{ width: "100%", height: 520 }} data-map-drawn={drawn.length} />
          <ul className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs">
            {data.techs.filter((t, i) => picked.some((p) => data.t[p] === i)).map((t) => (
              <li key={t.slug} className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: `var(${COLOR[t.slug]})` }} />{t.name}</li>
            ))}
          </ul>
        </ToolSection>

        <ToolSection title="Beside it: the interconnection queue" id="queue"
          note={<>Requests still active in the interconnection queues, from Berkeley Lab and GridTracker&apos;s Queued Up data file, {queueVintage}. A different source with its own regions and its own technologies: a request is not a plant, most are withdrawn, and the two columns are not added. The rows that answer to the technology chosen are marked.</>}>
          <ToolTable caption="Active requests in the interconnection queue" minWidth={520} head={["", "Active requests", "Active MW"]}
            rows={qrows.map((r) => ({
              key: `${r.region}|${r.slug}`, highlight: r.marked,
              cells: [<span key="n">{qrows.some((x) => x.region !== r.region) ? `${r.region}: ` : ""}{r.tech}</span>,
                r.requests === null ? <span key="r" className="text-muted">none in the file</span> : whole(r.requests),
                r.mw === null ? <span key="m" className="text-muted">none in the file</span> : <span key="m" data-queue-mw={`${r.region}|${r.slug}`}>{whole(r.mw)}</span>],
            }))} />
        </ToolSection>

        <ToolSection title="What is selected" id="table"
          note={<>{picked.length > rows.length ? <>The {whole(rows.length)} largest of {whole(picked.length)} are shown. </> : null}One row a generating unit; a plant with several units has several rows. Year: the year it began operating, or the year it is planned to.</>}>
          <ToolTable caption="The selected units, largest first" minWidth={720} words head={["Plant", "State", "Grid", "Technology", "Status", "MW", "Year"]}
            rows={rows.map((i) => ({
              key: String(i),
              cells: [data.names[data.n[i]], data.states[data.s[i]], data.grids[data.g[i]].name, data.techs[data.t[i]].name, data.statuses[data.st[i]].name, one(data.mw[i]), data.y[i] ? String(data.y[i]) : "not stated"],
            }))} />
          {picked.length > SHOWN ? (
            <button type="button" className="mt-2 border border-rule bg-white px-3 py-1 text-sm underline" onClick={() => setAll((v) => !v)}>
              {all ? `Show the ${SHOWN} largest` : `Show all ${whole(picked.length)}`}
            </button>
          ) : null}
        </ToolSection>
      </div>
    </div>
  );
}
