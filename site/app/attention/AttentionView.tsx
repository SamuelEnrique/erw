"use client";
// Session 3405 (chain 202): the Attention page's view. The file (data/attention.json) holds every number drawn here, as
// warehouse/derived/attention_index.py wrote it from the three tables: the weeks, the sectors, the places, one cell a
// (sector, place, week) with its stories, Attention Index, opposition stories, Friction Index and mean tone, the week's
// denominators, the kinds of opposition a cell holds, the places named, and the "rising" rows (this week's index against
// the mean of the four weeks before). The view chooses a sector, a place and a week and draws: the two indices over
// time (components/tool/SeriesChart.tsx), a map of the states for the chosen week (ECharts over us-atlas, as /map
// draws it), what rose this week, and the stories of the chosen cell (public/attention/stories/<monday>.json, fetched
// when opened). Nothing here computes an index: it looks values up. Colors are tokens.
//
// Session 1880 (docs/reviews/attention-faults-2026-11-11.md): the choosing and filtering moved to lib/attention.ts,
// tested by scripts/test-attention-view.mjs. The list under the United States is the stories that name a state, counted
// against the cell (row 1); no week after the build's week is offered (row 3); the week that holds the build is hatched
// and says "to <the build's day>" (row 4); the week moves to the cell's latest when the cell lacks it (row 5); a missing
// cell is one line (row 6); every figure carries its key and its source as a hover (row 8); the map has a Chart | Table
// toggle, the table keyed (row 9); a sector, state or place of "What rose" opens its stories (row 10); the places under
// All energy are summed by place (row 11); the charts' hover card gives the counts (row 12); at lg the inputs stand in
// a column left of the results (row 13).
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { baseStyle, token, useEChart } from "@/components/echarts";
import { Num } from "@/components/Num";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { HeadlineNumber, HeadlineRow, Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import {
  ATT, FRI, KIND_NAME, SECTOR_NAME, builtDay, cellWeeks, chooseWeek, day, fileKey, fileSource, geoWords, hasUsFlag, holdsBuild, inCell,
  isPartial, mapRows, noCellLine, openingWeek, pct, placeKey, placeSource, placesOf, risingKey, risingOf, risingSource, seriesKey,
  seriesSource, spanOf, weekOptions, weekWords, whole, type AttentionFile, type Cell, type Place, type Story,
} from "@/lib/attention";
import { STATES } from "@/lib/regions";

export type { AttentionFile } from "@/lib/attention";

const tone = (v: number) => (v > 0 ? "+" : "") + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const NAME_TO_CODE: Record<string, string> = Object.fromEntries(Object.entries(STATES).map(([code, name]) => [name, code]));
const geoName = (g: string) => geoWords(g, STATES);
const select = "border border-rule bg-white px-2 py-1 text-sm lg:w-full";
const rowButton = "text-left underline decoration-dotted underline-offset-2 hover:text-accent";

export function AttentionView({ file: f, statesGeo }: { file: AttentionFile; statesGeo: unknown }) {
  // the week the page opens on: the latest with at least fifty classified stories, none after the build's week
  const opening = useMemo(() => openingWeek(f), [f]);
  const [sector, setSector] = useState(0);
  const [geo, setGeo] = useState("all");
  const [week, setWeek] = useState(opening);
  const [measure, setMeasure] = useState<"attention" | "friction">("attention");
  const [onlyOpposition, setOnlyOpposition] = useState(false);
  const [place, setPlace] = useState<Place | null>(null);
  const [mapTable, setMapTable] = useState(false);
  const [stories, setStories] = useState<Record<string, Story[] | "loading" | "failed">>({});

  const cellOf = useMemo(() => {
    const m = new Map<string, Cell>();
    for (const c of f.cells) m.set(`${c[0]}|${c[1]}|${c[2]}`, { stories: c[3], attention: c[4], opposition: c[5], friction: c[6], tone: c[7] });
    return m;
  }, [f]);
  const denom = useMemo(() => new Map(f.denominators.map((d) => [d[0], { week: d[1], judged: d[2], classified: d[3], zero: d[4] }])), [f]);
  const gi = f.geos.indexOf(geo);
  const sectorKey = f.sectors[sector];
  const sectorName = SECTOR_NAME[sectorKey] ?? sectorKey;
  const energyIndex = f.sectors.indexOf("energy");
  // rows 3 and 5: the cell's weeks, none after the build's week; the chosen week moves to the cell's latest when the
  // cell lacks it (a cell with no week keeps it, marked "no story" in the picker)
  const weeksWithStories = useMemo(() => cellWeeks(f, sector, gi), [f, sector, gi]);
  const [weeksSeen, setWeeksSeen] = useState(weeksWithStories);
  if (weeksSeen !== weeksWithStories) { setWeeksSeen(weeksWithStories); setWeek(chooseWeek(weeksWithStories, week)); }
  const cell = cellOf.get(`${sector}|${gi}|${week}`);
  const wk = f.weeks[week];
  const d = denom.get(week);
  const entity = `attention:${sectorKey}:${geo}`;
  // a figure of a warehouse table, keyed and with its source as its hover (row 8)
  const S = (table: string, ent: string, variable: string, raw: number, text: string, w = wk) => (
    <Num check={seriesKey(table, ent, variable, w)} raw={raw} source={seriesSource(f.built, table, ent, variable, w)}>{text}</Num>
  );

  // the charts' span: the weeks with a classified story, the first to the last, and none after the build's week (the
  // weeks before the classification reached are not zero, they are not yet read, so they are not drawn)
  const span = useMemo(() => spanOf(f), [f]);
  // the two series over the span: a week without a row is null (no story of the sector in that place)
  const series = useMemo(() => {
    const att: (number | null)[] = [], fri: (number | null)[] = [], n: number[] = [], opp: number[] = [];
    for (const i of span) {
      const c = cellOf.get(`${sector}|${gi}|${i}`);
      att.push(c ? c.attention : null); fri.push(c ? c.friction : null); n.push(c ? c.stories : 0); opp.push(c ? c.opposition : 0);
    }
    return { att, fri, n, opp };
  }, [span, cellOf, sector, gi]);
  const categories = useMemo(() => span.map((i) => ({ label: day(f.weeks[i]), partial: isPartial(f, i) })), [f, span]);
  const firstDrawn = span.length ? day(f.weeks[span[0]]) : "";
  const weekTo = (i: number) => (holdsBuild(f, i) ? ` (to ${builtDay(f.built)})` : "");

  // the stories of the chosen week, fetched once a week is opened
  const load = useCallback((w: string) => {
    const key = day(w);
    setStories((s) => (s[key] ? s : { ...s, [key]: "loading" }));
    fetch(`/attention/stories/${key}.json`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((j: { columns: string[]; rows: (string | number)[][] }) => {
        const rows = j.rows.map((r) => Object.fromEntries(j.columns.map((c, i) => [c, r[i]])) as unknown as Story);
        setStories((s) => ({ ...s, [key]: rows }));
      })
      .catch(() => setStories((s) => ({ ...s, [key]: "failed" })));
  }, []);
  useEffect(() => { if (wk && !stories[day(wk)]) load(wk); }, [wk, stories, load]);
  const got = stories[day(wk ?? "")];
  // row 1: under the United States, the week file's us flag when it carries one, else the stories that name a state
  const list = Array.isArray(got) ? got.filter((s) => inCell(s, sectorKey, geo, onlyOpposition, place)) : [];
  const usPartial = geo === "US" && Array.isArray(got) && !hasUsFlag(got);

  // rows 10 and 13: a row of "What rose" opens its stories
  const toStories = () => requestAnimationFrame(() => document.getElementById("attention-stories")?.scrollIntoView({ block: "start" }));
  const openCell = (si: number, g: string) => { setSector(si); setGeo(g); setPlace(null); toStories(); };
  const openPlace = (p: Place) => { setGeo("all"); setPlace(p); toStories(); };

  // the map: the states' value for the chosen sector and week
  const mapValues = useMemo(() => {
    const out: { name: string; value: number; code: string; cell: Cell }[] = [];
    for (const st of f.states) {
      const c = cellOf.get(`${sector}|${f.geos.indexOf("US-" + st)}|${week}`);
      if (c) out.push({ name: STATES[st] ?? st, value: measure === "attention" ? c.attention : c.friction, code: st, cell: c });
    }
    return out;
  }, [f, cellOf, sector, week, measure]);
  const act = useRef({ setGeo, setPlace });
  useEffect(() => { act.current = { setGeo, setPlace }; }, []);
  const box = useEChart(
    (chart, lib) => {
      lib.registerMap("erw-us-one", statesGeo);
      const st = baseStyle();
      const paper = token("paper"), panel = token("panel"), rule = token("rule"), accent = token("accent"), muted = token("muted");
      const max = Math.max(0.1, ...mapValues.map((v) => v.value));
      chart.setOption({
        animation: false, textStyle: st.textStyle,
        tooltip: {
          ...st.tooltip, trigger: "item",
          formatter: (p: { name?: string; data?: { cell?: Cell; code?: string } }) => {
            const c = p.data?.cell;
            if (!c) return `${p.name}: no story of ${sectorName.toLowerCase()} named this state in the week of ${day(wk)}`;
            return `<div style="max-width:17rem;white-space:normal"><strong>${p.name}</strong>, week of ${day(wk)}<br/>${whole(c.stories)} ${c.stories === 1 ? "story" : "stories"}, Attention Index ${pct(c.attention)}<br/>`
              + `${whole(c.opposition)} reporting opposition, Friction Index ${pct(c.friction)}<br/><span style="color:${muted}">Click the state to choose it.</span></div>`;
          },
        },
        visualMap: {
          min: 0, max, calculable: false, orient: "horizontal", left: 4, bottom: 0, itemWidth: 10, itemHeight: 120,
          text: [measure === "attention" ? `Attention Index ${pct(max)}` : `Friction Index ${pct(max)}`, "0"], textStyle: { color: muted, fontSize: 11 },
          inRange: { color: [paper, accent] },
        },
        series: [{
          type: "map", map: "erw-us-one", roam: false, projection: { project: (p: number[]) => p, unproject: (p: number[]) => p },
          top: 8, bottom: 28, left: 4, right: 4,
          itemStyle: { areaColor: paper, borderColor: rule, borderWidth: 0.7 }, emphasis: { itemStyle: { areaColor: panel }, label: { show: false } },
          select: { disabled: true }, label: { show: false },
          data: mapValues,
        }],
      }, true);
      chart.off("click");
      chart.on("click", (p) => {
        const code = NAME_TO_CODE[p.name as string];
        if (code && f.states.includes(code)) { act.current.setPlace(null); act.current.setGeo((g) => (g === "US-" + code ? "all" : "US-" + code)); }
      });
    },
    [mapValues, statesGeo, sector, wk, measure, f],
  );
  const mapTableRows = useMemo(() => mapRows(f, sector, week, measure), [f, sector, week, measure]);

  const rising = useMemo(() => {
    const r = risingOf(f, week);
    return { sectors: r.sectors, states: r.states.slice(0, 8), places: placesOf(f, week, sector).slice(0, 10), kinds: Object.entries(f.kinds[`${sector}|${gi}|${week}`] ?? {}).sort((a, b) => b[1] - a[1]) };
  }, [f, week, sector, gi]);
  const signed = (v: number) => (v >= 0 ? "+" : "");
  const R = (kind: "sector" | "state", key: string, field: "mean_before" | "change", raw: number) => (
    <>{field === "change" ? signed(raw) : ""}<Num check={risingKey(wk, kind, key, field)} raw={raw} source={risingSource(f.built, wk, kind, key, field)}>{pct(raw)}</Num></>
  );
  const P = (p: Place, field: "stories" | "opposition", raw: number) => (
    <Num check={placeKey(wk, sectorKey, p, field)} raw={raw} source={placeSource(f.built, wk, sectorKey, p, field)}>{whole(raw)}</Num>
  );
  const F = (field: "stories" | "opposition" | "weeks_with_stories") => (
    <Num check={fileKey(field)} raw={f.counts[field]} source={fileSource(f.built, field)}>{whole(f.counts[field])}</Num>
  );
  const mapToggle = (
    <span className="inline-grid grid-cols-2 border border-muted text-xs" role="group" aria-label="The states: map or table" data-attention-map-toggle="1">
      {([["chart", "Chart"], ["table", "Table"]] as const).map(([k, label], i) => (
        <button key={k} type="button" aria-pressed={mapTable === (k === "table")} data-show={k} onClick={() => setMapTable(k === "table")}
          className={`px-2.5 py-0.5 ${i ? "border-l border-muted" : ""} ${mapTable === (k === "table") ? "bg-ink text-white" : "bg-white text-ink"}`}>{label}</button>
      ))}
    </span>
  );

  return (
    <div data-attention-view="1" className="lg:grid lg:grid-cols-[13rem_minmax(0,1fr)] lg:gap-8" data-attention-layout="1">
      <div className="mb-4 flex flex-wrap items-end gap-4 lg:sticky lg:top-2 lg:mb-0 lg:flex-col lg:items-stretch lg:self-start" data-attention-controls="1">
        <label className="text-xs text-muted">Sector<br />
          <select className={select} value={sector} onChange={(e) => { setSector(Number(e.target.value)); setPlace(null); }} data-attention-sector="1">
            {f.sectors.map((s, i) => <option key={s} value={i}>{SECTOR_NAME[s] ?? s}</option>)}
          </select></label>
        <label className="text-xs text-muted">Place<br />
          <select className={select} value={geo} onChange={(e) => { setGeo(e.target.value); setPlace(null); }} data-attention-geo="1">
            <option value="all">Every story</option>
            <option value="US">United States</option>
            {f.states.map((s) => <option key={s} value={"US-" + s}>{STATES[s] ?? s}</option>)}
          </select></label>
        <label className="text-xs text-muted">Week of<br />
          <select className={select} value={week} onChange={(e) => { setWeek(Number(e.target.value)); setPlace(null); }} data-attention-week="1">
            {weekOptions(weeksWithStories, week).map(({ i, none }) => <option key={i} value={i}>{day(f.weeks[i])}{weekWords(f, i)}{none ? " (no story)" : ""}</option>)}
          </select></label>
        <div className="text-xs text-muted">Map shows<br />
          <span className="inline-flex border border-rule" role="group" aria-label="Measure">
            {(["attention", "friction"] as const).map((m) => (
              <button key={m} type="button" onClick={() => setMeasure(m)} aria-pressed={measure === m} data-attention-measure={m}
                className={`px-2 py-1 text-sm ${measure === m ? "bg-accent text-white" : "bg-white text-ink"}`}>{m === "attention" ? "Attention Index" : "Friction Index"}</button>
            ))}
          </span>
        </div>
      </div>

      <div className="min-w-0" data-attention-results="1">
      {cell ? (
        <HeadlineRow>
          <HeadlineNumber label={`${sectorName}, ${geoName(geo)}, week of ${day(wk)}${weekTo(week)}`} unit="stories"
            value={S(ATT, entity, "stories", cell.stories, whole(cell.stories))}
            note={d ? <>of {S(ATT, "attention:corpus:all", "stories_judged", d.judged, whole(d.judged))} judged stories this week ({S(ATT, "attention:corpus:all", "stories_classified", d.classified, whole(d.classified))} classified, {S(ATT, "attention:corpus:all", "stories_unsent_zero", d.zero, whole(d.zero))} scored 0 by the news scorer and not sent; {S(ATT, "attention:corpus:all", "stories_week", d.week, whole(d.week))} held)</> : undefined} />
          <HeadlineNumber label="Attention Index" unit="% of the week's judged stories"
            value={S(ATT, entity, "attention_index", cell.attention, pct(cell.attention))} />
          <HeadlineNumber label="Friction Index" unit="% of these stories reporting opposition"
            value={S(FRI, entity, "friction_index", cell.friction, pct(cell.friction))}
            note={<>{S(FRI, entity, "opposition_stories", cell.opposition, whole(cell.opposition))} {cell.opposition === 1 ? "story" : "stories"}{rising.kinds.length ? ": " : ""}{rising.kinds.map(([k, n], j) => <span key={k}>{j ? ", " : ""}{S(FRI, entity, `kind_${k}`, n, whole(n))} {KIND_NAME[k] ?? k}</span>)}</>} />
          <HeadlineNumber label="Tone" unit="mean, -1 to +1"
            value={S(ATT, entity, "tone_mean", cell.tone, tone(cell.tone))}
            tip={<Tip id="attention-tone" label="what the tone is">The model&apos;s reading of each story&apos;s tone toward what it covers: -1 negative, 0 neutral or mixed, +1 positive, averaged over the cell&apos;s stories. The least reliable field of the classification (0.87 against the hand labels).</Tip>} />
        </HeadlineRow>
      ) : (
        <p className="mb-10 font-serif text-xl text-ink" data-attention-none="1">{noCellLine(sectorKey, geo, wk, STATES)}</p>
      )}

      <ToolSection title={`Attention Index over time: ${sectorName}, ${geoName(geo)}`} id="attention-over-time"
        note={`Percent of each week's judged stories, from the first classified week (${firstDrawn}); the weeks before it are not yet classified and are not drawn. A hatched week is partly classified (fewer than nine in ten of its stories judged) or the current one; its value is a share of the stories judged so far.`}>
        <SeriesChart id="attention-line" title="Attention Index" unit="%" kind="line" scale="linear" fmt={pct}
          categories={categories} series={[{ name: "Attention Index", color: "var(--color-accent)", values: series.att }]}
          says={(i) => `Week of ${day(f.weeks[span[i]])}${weekTo(span[i])}: ${series.att[i] === null ? "no story" : `${pct(series.att[i] as number)} of the week's judged stories (${whole(series.n[i])} stories)`}`}
          saysOnCard partialWords="Partly classified or not over" />
      </ToolSection>
      <ToolSection title={`Friction Index over time: ${sectorName}, ${geoName(geo)}`} id="friction-over-time"
        note="Percent of the cell's stories that report opposition. A week with few stories swings widely; the hover gives the counts.">
        <SeriesChart id="friction-line" title="Friction Index" unit="%" kind="line" scale="linear" fmt={pct}
          categories={categories} series={[{ name: "Friction Index", color: "var(--chart-blue)", values: series.fri }]}
          says={(i) => `Week of ${day(f.weeks[span[i]])}${weekTo(span[i])}: ${series.fri[i] === null ? "no story" : `${pct(series.fri[i] as number)} (${whole(series.opp[i])} of ${whole(series.n[i])} stories report opposition)`}`}
          saysOnCard partialWords="Partly classified or not over" />
      </ToolSection>

      <ToolSection title={`By state, week of ${day(wk)}: ${sectorName}`} id="attention-map"
        note="A state is colored where a story of the sector named it that week; the rest are blank. Click a state to choose it; the hover gives its counts.">
        <div className="mb-2 flex justify-end">{mapToggle}</div>
        <div ref={box} data-attention-map="1" className={mapTable ? "hidden" : ""} style={{ width: "100%", height: 420 }} aria-label={`Map of the states' ${measure === "attention" ? "Attention" : "Friction"} Index, week of ${day(wk)}`} role="img" />
        {mapTable && mapTableRows.length > 0 && (
          <div data-attention-map-table={mapTableRows.length}>
            <ToolTable caption={`The states, ${sectorName.toLowerCase()}, week of ${day(wk)}`} head={["State", "Stories", "Attention Index %", "Reporting opposition", "Friction Index %"]}
              rows={mapTableRows.map((r) => {
                const ent = `attention:${sectorKey}:US-${r.code}`;
                return { key: r.code, cells: [
                  <button key="s" type="button" className={rowButton} onClick={() => openCell(sector, "US-" + r.code)} data-attention-open={`state:${r.code}`}>{STATES[r.code] ?? r.code}</button>,
                  S(ATT, ent, "stories", r.cell.stories, whole(r.cell.stories)), S(ATT, ent, "attention_index", r.cell.attention, pct(r.cell.attention)),
                  S(FRI, ent, "opposition_stories", r.cell.opposition, whole(r.cell.opposition)), S(FRI, ent, "friction_index", r.cell.friction, pct(r.cell.friction))] };
              })} minWidth={0} />
          </div>
        )}
        {mapValues.length === 0 && <p className="text-sm text-muted" data-attention-map-empty="1">No story of this sector named a state in this week.</p>}
      </ToolSection>

      <ToolSection title={`What rose in the week of ${day(wk)}`} id="attention-rising"
        note="Each sector's and state's Attention Index this week against the mean of the four weeks before (a week without a row counts as zero). Places are the counties, cities and metros the week's stories named.">
        <div className="grid gap-6 md:grid-cols-3">
          {rising.sectors.length ? (
            <ToolTable caption="Sectors, every story" head={["Sector", "This week %", "Four weeks before %", "Change"]}
              rows={rising.sectors.map((r) => ({ key: r.key, cells: [
                <button key="s" type="button" className={rowButton} onClick={() => openCell(r.index, "all")} data-attention-open={`sector:${r.key}`}>{SECTOR_NAME[r.key] ?? r.key}</button>,
                S(ATT, `attention:${r.key}:all`, "attention_index", r.this, pct(r.this)),
                R("sector", r.key, "mean_before", r.before), R("sector", r.key, "change", r.change)] }))} minWidth={0} />
          ) : <p className="text-sm text-muted" data-attention-rising="sectors-none">No sector has a story this week.</p>}
          {rising.states.length ? (
            <ToolTable caption="States, all energy" head={["State", "This week %", "Four weeks before %", "Change"]}
              rows={rising.states.map((r) => ({ key: r.key, cells: [
                <button key="s" type="button" className={rowButton} onClick={() => openCell(energyIndex, "US-" + r.key)} data-attention-open={`state:${r.key}`}>{STATES[r.key] ?? r.key}</button>,
                S(ATT, `attention:energy:US-${r.key}`, "attention_index", r.this, pct(r.this)),
                R("state", r.key, "mean_before", r.before), R("state", r.key, "change", r.change)] }))} minWidth={0} />
          ) : <p className="text-sm text-muted" data-attention-rising="states-none">No energy story named a state this week.</p>}
          {rising.places.length ? (
            <ToolTable caption={`Places named, ${sectorName.toLowerCase()}`} head={["Place", "State", "Stories", "Reporting opposition"]}
              rows={rising.places.map((p) => ({ key: `${p.place}|${p.state}`, cells: [
                <button key="p" type="button" className={rowButton} onClick={() => openPlace({ place: p.place, state: p.state })} data-attention-open={`place:${p.place}|${p.state}`}>{p.place}</button>,
                p.state, P(p, "stories", p.stories), P(p, "opposition", p.opposition)] }))} minWidth={0} />
          ) : <p className="text-sm text-muted" data-attention-rising="places-none">No story of {sectorName.toLowerCase()} named a county, city or metro this week.</p>}
        </div>
      </ToolSection>

      <ToolSection title={`The stories: ${sectorName}, ${place ? `${place.place}${place.state ? `, ${place.state}` : ""}` : geoName(geo)}, week of ${day(wk)}`} id="attention-stories"
        note={usPartial && cell
          ? <><span data-attention-list-count={list.length}>{whole(list.length)}</span> of the cell&apos;s {onlyOpposition ? <>{S(FRI, entity, "opposition_stories", cell.opposition, whole(cell.opposition))} stories reporting opposition</> : <>{S(ATT, entity, "stories", cell.stories, whole(cell.stories))} stories</>}: the ones that name a state.</>
          : "Each link opens the outlet's story. The headline is the warehouse's own one-line reading; the outlet's title is not republished."}>
        <div className="mb-2 flex flex-wrap items-center gap-4 text-xs text-muted">
          <label><input type="checkbox" checked={onlyOpposition} onChange={(e) => setOnlyOpposition(e.target.checked)} /> only the stories reporting opposition</label>
          {place && <button type="button" className="border border-rule px-1.5 py-0.5 text-ink" onClick={() => setPlace(null)} data-attention-place-clear="1">Place: {place.place}{place.state ? `, ${place.state}` : ""} (clear)</button>}
        </div>
        {got === "loading" || got === undefined ? <p className="text-sm text-muted">Loading the week&apos;s stories.</p>
          : got === "failed" ? <p className="text-sm text-muted" data-attention-stories="failed">The week&apos;s stories could not be read.</p>
          : list.length === 0 ? <p className="text-sm text-muted" data-attention-stories="0">No story in this cell.</p>
          : (
            <ol className="space-y-1 text-sm" data-attention-stories={list.length}>
              {list.slice(0, 200).map((s) => (
                <li key={s.id}>
                  <span className="text-muted">{s.date}</span> <a href={s.url} rel="noopener">{s.headline || `A ${s.outlet} story of ${s.date} (no ERW headline yet)`}</a> <span className="text-muted">({s.outlet}{s.state ? `, ${s.state}` : ""}{s.place ? `, ${s.place}` : ""})</span>
                  {s.opposition === 1 && <span className="ml-1 border border-rule px-1 text-xs" data-attention-kind={s.kind}>{KIND_NAME[s.kind] ?? s.kind}</span>}
                </li>
              ))}
              {list.length > 200 && <li className="text-muted">and {whole(list.length - 200)} more in the table attention_story_links</li>}
            </ol>
          )}
      </ToolSection>
      <p className="text-xs text-muted" data-attention-built={f.built}>{f.note}. Built {f.built.slice(0, 16).replace("T", " ")} UTC from {F("stories")} classified stories ({F("opposition")} reporting opposition) over {F("weeks_with_stories")} weeks; model {f.model.join(", ")}.</p>
      </div>
    </div>
  );
}
