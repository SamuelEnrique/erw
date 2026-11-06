"use client";
// Session 3405 (chain 202): the Attention page's view. The file (data/attention.json) holds every number drawn here, as
// warehouse/derived/attention_index.py wrote it from the three tables: the weeks, the sectors, the places, one cell a
// (sector, place, week) with its stories, Attention Index, opposition stories, Friction Index and mean tone, the week's
// denominators, the kinds of opposition a cell holds, the places named, and the "rising" rows (this week's index against
// the mean of the four weeks before). The view chooses a sector, a place and a week and draws: the two indices over
// time (components/tool/SeriesChart.tsx), a map of the states for the chosen week (ECharts over us-atlas, as /map
// draws it), what rose this week, and the stories of the chosen cell (public/attention/stories/<monday>.json, fetched
// when opened). Nothing here computes an index: it looks values up. Colors are tokens.
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { baseStyle, token, useEChart } from "@/components/echarts";
import { Num } from "@/components/Num";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { HeadlineNumber, HeadlineRow, Tip, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { STATES } from "@/lib/regions";

export type AttentionFile = {
  built: string; note: string; weeks: string[]; sectors: string[]; geos: string[]; states: string[];
  denominators: number[][];              // [week_i, stories_week, stories_judged, stories_classified, stories_unsent_zero]
  cells: number[][];                     // [sector_i, geo_i, week_i, stories, attention_index, opposition_stories, friction_index, tone_mean]
  kinds: Record<string, Record<string, number>>;   // "sector_i|geo_i|week_i" -> kind -> count
  places: (string | number)[][];         // [sector_i, place, state, week_i, stories, opposition]
  rising: (string | number)[][];         // [week_i, "sector" | "state", sector_i or state code, this, mean_before, change]
  counts: { stories: number; opposition: number; weeks_with_stories: number };
  model: string[]; tables: string[];
};
type Story = { id: string; date: string; outlet: string; url: string; headline: string; sector: string; state: string; opposition: number; kind: string; tone: number; place: string };
type Cell = { stories: number; attention: number; opposition: number; friction: number; tone: number };

const SECTOR_NAME: Record<string, string> = {
  datacenters: "Data centers", transmission: "Transmission and grid", gas: "Natural gas", nuclear: "Nuclear", solar_wind: "Solar and wind",
  storage: "Storage", oil_lng: "Oil and LNG", energy: "All energy",
};
const KIND_NAME: Record<string, string> = {
  moratorium: "moratorium or ban", lawsuit: "lawsuit", protest: "protest", permit_denied: "permit denied", rate_case: "rate case",
  political_opposition: "political opposition", other_opposition: "other opposition",
};
const ATT = "attention_index_weekly", FRI = "friction_index_weekly";
const pct = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const tone = (v: number) => (v > 0 ? "+" : "") + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const day = (w: string) => w.slice(0, 10);
const NAME_TO_CODE: Record<string, string> = Object.fromEntries(Object.entries(STATES).map(([code, name]) => [name, code]));
const geoName = (g: string) => (g === "all" ? "every story" : g === "US" ? "the United States" : STATES[g.slice(3)] ?? g);
const select = "border border-rule bg-white px-2 py-1 text-sm";

export function AttentionView({ file: f, statesGeo }: { file: AttentionFile; statesGeo: unknown }) {
  // the week the page opens on: the latest with at least fifty classified stories (a feed dates a few stories after the
  // day they were read, so the very last week may hold one story), else the latest with any
  const lastWeekWithStories = useMemo(() => {
    const full = f.denominators.filter((d) => d[3] >= 50).map((d) => d[0]);
    return full.length ? Math.max(...full) : Math.max(...f.cells.map((c) => c[2]));
  }, [f]);
  const [sector, setSector] = useState(0);
  const [geo, setGeo] = useState("all");
  const [week, setWeek] = useState(lastWeekWithStories);
  const [measure, setMeasure] = useState<"attention" | "friction">("attention");
  const [onlyOpposition, setOnlyOpposition] = useState(false);
  const [stories, setStories] = useState<Record<string, Story[] | "loading" | "failed">>({});

  const cellOf = useMemo(() => {
    const m = new Map<string, Cell>();
    for (const c of f.cells) m.set(`${c[0]}|${c[1]}|${c[2]}`, { stories: c[3], attention: c[4], opposition: c[5], friction: c[6], tone: c[7] });
    return m;
  }, [f]);
  const denom = useMemo(() => new Map(f.denominators.map((d) => [d[0], { week: d[1], judged: d[2], classified: d[3], zero: d[4] }])), [f]);
  const gi = f.geos.indexOf(geo);
  const weeksWithStories = useMemo(() => {
    const s = new Set(f.cells.filter((c) => c[0] === sector && c[1] === gi).map((c) => c[2]));
    return f.weeks.map((w, i) => i).filter((i) => s.has(i));
  }, [f, sector, gi]);
  const cell = cellOf.get(`${sector}|${gi}|${week}`);
  const wk = f.weeks[week];
  const d = denom.get(week);
  const entity = `attention:${f.sectors[sector]}:${geo}`;
  const partial = (i: number) => { const x = denom.get(i); return !x || x.judged < x.week * 0.9 || i === f.weeks.length - 1; };

  // the charts' span: the weeks with a classified story, the first to the last (the weeks before the classification
  // reached are not zero, they are not yet read, so they are not drawn; the note under the chart says so)
  const span = useMemo(() => f.denominators.filter((d) => d[3] > 0).map((d) => d[0]).sort((a, b) => a - b), [f]);
  // the two series over the span: a week without a row is null (no story of the sector in that place)
  const series = useMemo(() => {
    const att: (number | null)[] = [], fri: (number | null)[] = [], n: number[] = [], opp: number[] = [];
    for (const i of span) {
      const c = cellOf.get(`${sector}|${gi}|${i}`);
      att.push(c ? c.attention : null); fri.push(c ? c.friction : null); n.push(c ? c.stories : 0); opp.push(c ? c.opposition : 0);
    }
    return { att, fri, n, opp };
  }, [span, cellOf, sector, gi]);
  const categories = useMemo(() => span.map((i) => ({ label: day(f.weeks[i]), partial: partial(i) })), [f, span]);  // eslint-disable-line react-hooks/exhaustive-deps
  const firstDrawn = span.length ? day(f.weeks[span[0]]) : "";

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
  const inCell = (s: Story) => {
    const sectorOk = f.sectors[sector] === "energy" ? s.sector !== "not_energy" : s.sector === f.sectors[sector];
    const geoOk = geo === "all" ? true : geo === "US" ? s.state !== "" || true : s.state === geo.slice(3);
    return sectorOk && geoOk && (!onlyOpposition || s.opposition === 1);
  };
  const list = Array.isArray(got) ? got.filter(inCell) : [];
  // "US" rows hold every story about the United States; the week file carries no us flag, so the list under "the United
  // States" shows the stories with a state and says so
  const usNote = geo === "US";

  // the map: the states' value for the chosen sector and week
  const mapValues = useMemo(() => {
    const out: { name: string; value: number; code: string; cell: Cell }[] = [];
    for (const st of f.states) {
      const c = cellOf.get(`${sector}|${f.geos.indexOf("US-" + st)}|${week}`);
      if (c) out.push({ name: STATES[st] ?? st, value: measure === "attention" ? c.attention : c.friction, code: st, cell: c });
    }
    return out;
  }, [f, cellOf, sector, week, measure]);
  const act = useRef({ setGeo });
  useEffect(() => { act.current = { setGeo }; }, []);
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
            if (!c) return `${p.name}: no story of ${SECTOR_NAME[f.sectors[sector]].toLowerCase()} named this state in the week of ${day(wk)}`;
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
        if (code && f.states.includes(code)) act.current.setGeo((g) => (g === "US-" + code ? "all" : "US-" + code));
      });
    },
    [mapValues, statesGeo, sector, wk, measure, f],
  );

  const rising = useMemo(() => {
    const rows = f.rising.filter((r) => r[0] === week);
    const sectors = rows.filter((r) => r[1] === "sector").map((r) => ({ name: SECTOR_NAME[f.sectors[r[2] as number]], sectorKey: f.sectors[r[2] as number], this: r[3] as number, before: r[4] as number, change: r[5] as number }))
      .filter((r) => r.name !== "All energy").sort((a, b) => b.change - a.change);
    const states = rows.filter((r) => r[1] === "state").map((r) => ({ name: STATES[r[2] as string] ?? (r[2] as string), code: r[2] as string, this: r[3] as number, before: r[4] as number, change: r[5] as number }))
      .sort((a, b) => b.change - a.change).slice(0, 8);
    const places = f.places.filter((p) => p[3] === week && (f.sectors[sector] === "energy" ? true : p[0] === sector))
      .map((p) => ({ place: p[1] as string, state: p[2] as string, stories: p[4] as number, opposition: p[5] as number }))
      .sort((a, b) => b.stories - a.stories || b.opposition - a.opposition).slice(0, 10);
    const kinds = Object.entries(f.kinds[`${sector}|${gi}|${week}`] ?? {}).sort((a, b) => b[1] - a[1]);
    return { sectors, states, places, kinds };
  }, [f, week, sector, gi]);

  return (
    <div data-attention-view="1">
      <div className="mb-4 flex flex-wrap items-end gap-4" data-attention-controls="1">
        <label className="text-xs text-muted">Sector<br />
          <select className={select} value={sector} onChange={(e) => setSector(Number(e.target.value))} data-attention-sector="1">
            {f.sectors.map((s, i) => <option key={s} value={i}>{SECTOR_NAME[s] ?? s}</option>)}
          </select></label>
        <label className="text-xs text-muted">Place<br />
          <select className={select} value={geo} onChange={(e) => setGeo(e.target.value)} data-attention-geo="1">
            <option value="all">Every story</option>
            <option value="US">United States</option>
            {f.states.map((s) => <option key={s} value={"US-" + s}>{STATES[s] ?? s}</option>)}
          </select></label>
        <label className="text-xs text-muted">Week of<br />
          <select className={select} value={week} onChange={(e) => setWeek(Number(e.target.value))} data-attention-week="1">
            {weeksWithStories.map((i) => <option key={i} value={i}>{day(f.weeks[i])}{partial(i) ? " (partly classified)" : ""}</option>)}
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

      <HeadlineRow>
        <HeadlineNumber label={`${SECTOR_NAME[f.sectors[sector]]}, ${geoName(geo)}, week of ${day(wk)}`} unit="stories"
          value={cell ? <Num check={`series|${ATT}|${entity}|stories|${wk}`} raw={cell.stories}>{whole(cell.stories)}</Num> : "none"}
          note={d ? `of ${whole(d.judged)} judged stories this week (${whole(d.classified)} classified, ${whole(d.zero)} scored 0 by the news scorer and not sent; ${whole(d.week)} held)` : undefined} />
        <HeadlineNumber label="Attention Index" unit="% of the week's judged stories"
          value={cell ? <Num check={`series|${ATT}|${entity}|attention_index|${wk}`} raw={cell.attention}>{pct(cell.attention)}</Num> : "none"} />
        <HeadlineNumber label="Friction Index" unit="% of these stories reporting opposition"
          value={cell ? <Num check={`series|${FRI}|${entity}|friction_index|${wk}`} raw={cell.friction}>{pct(cell.friction)}</Num> : "none"}
          note={cell ? `${whole(cell.opposition)} ${cell.opposition === 1 ? "story" : "stories"}${rising.kinds.length ? ": " + rising.kinds.map(([k, n]) => `${n} ${KIND_NAME[k] ?? k}`).join(", ") : ""}` : undefined} />
        <HeadlineNumber label="Tone" unit="mean, -1 to +1"
          value={cell ? <Num check={`series|${ATT}|${entity}|tone_mean|${wk}`} raw={cell.tone}>{tone(cell.tone)}</Num> : "none"}
          tip={<Tip id="attention-tone" label="what the tone is">The model&apos;s reading of each story&apos;s tone toward what it covers: -1 negative, 0 neutral or mixed, +1 positive, averaged over the cell&apos;s stories. The least reliable field of the classification (0.87 against the hand labels).</Tip>} />
      </HeadlineRow>

      <ToolSection title={`Attention Index over time: ${SECTOR_NAME[f.sectors[sector]]}, ${geoName(geo)}`} id="attention-over-time"
        note={`Percent of each week's judged stories, from the first classified week (${firstDrawn}); the weeks before it are not yet classified and are not drawn. A hatched week is partly classified (fewer than nine in ten of its stories judged) or the current one; its value is a share of the stories judged so far.`}>
        <SeriesChart id="attention-line" title="Attention Index" unit="%" kind="line" scale="linear" fmt={pct}
          categories={categories} series={[{ name: "Attention Index", color: "var(--color-accent)", values: series.att }]}
          says={(i) => `Week of ${day(f.weeks[span[i]])}: ${series.att[i] === null ? "no story" : `${pct(series.att[i] as number)} of the week's judged stories (${whole(series.n[i])} stories)`}`}
          partialWords="partly classified" />
      </ToolSection>
      <ToolSection title={`Friction Index over time: ${SECTOR_NAME[f.sectors[sector]]}, ${geoName(geo)}`} id="friction-over-time"
        note="Percent of the cell's stories that report opposition. A week with few stories swings widely; the hover gives the counts.">
        <SeriesChart id="friction-line" title="Friction Index" unit="%" kind="line" scale="linear" fmt={pct}
          categories={categories} series={[{ name: "Friction Index", color: "var(--chart-blue)", values: series.fri }]}
          says={(i) => `Week of ${day(f.weeks[span[i]])}: ${series.fri[i] === null ? "no story" : `${pct(series.fri[i] as number)} (${whole(series.opp[i])} of ${whole(series.n[i])} stories report opposition)`}`}
          partialWords="partly classified" />
      </ToolSection>

      <ToolSection title={`By state, week of ${day(wk)}: ${SECTOR_NAME[f.sectors[sector]]}`} id="attention-map"
        note="A state is colored where a story of the sector named it that week; the rest are blank. Click a state to choose it; the hover gives its counts.">
        <div ref={box} data-attention-map="1" style={{ width: "100%", height: 420 }} aria-label={`Map of the states' ${measure === "attention" ? "Attention" : "Friction"} Index, week of ${day(wk)}`} role="img" />
        {mapValues.length === 0 && <p className="text-sm text-muted" data-attention-map-empty="1">No story of this sector named a state in this week.</p>}
      </ToolSection>

      <ToolSection title={`What rose in the week of ${day(wk)}`} id="attention-rising"
        note="Each sector's and state's Attention Index this week against the mean of the four weeks before (a week without a row counts as zero). Places are the counties, cities and metros the week's stories named.">
        <div className="grid gap-6 md:grid-cols-3">
          {rising.sectors.length ? (
            <ToolTable caption="Sectors, every story" head={["Sector", "This week %", "Four weeks before %", "Change"]}
              rows={rising.sectors.map((r) => ({ key: r.name, cells: [r.name,
                <Num key="v" check={`series|${ATT}|attention:${r.sectorKey}:all|attention_index|${wk}`} raw={r.this}>{pct(r.this)}</Num>,
                pct(r.before), (r.change >= 0 ? "+" : "") + pct(r.change)] }))} minWidth={0} />
          ) : <p className="text-sm text-muted" data-attention-rising="sectors-none">No sector has a story this week.</p>}
          {rising.states.length ? (
            <ToolTable caption="States, all energy" head={["State", "This week %", "Four weeks before %", "Change"]}
              rows={rising.states.map((r) => ({ key: r.code, cells: [r.name,
                <Num key="v" check={`series|${ATT}|attention:energy:US-${r.code}|attention_index|${wk}`} raw={r.this}>{pct(r.this)}</Num>,
                pct(r.before), (r.change >= 0 ? "+" : "") + pct(r.change)] }))} minWidth={0} />
          ) : <p className="text-sm text-muted" data-attention-rising="states-none">No energy story named a state this week.</p>}
          {rising.places.length ? (
            <ToolTable caption={`Places named, ${SECTOR_NAME[f.sectors[sector]].toLowerCase()}`} head={["Place", "State", "Stories", "Reporting opposition"]}
              rows={rising.places.map((p) => ({ key: `${p.place}|${p.state}`, cells: [p.place, p.state, whole(p.stories), whole(p.opposition)] }))} minWidth={0} />
          ) : <p className="text-sm text-muted" data-attention-rising="places-none">No story of {SECTOR_NAME[f.sectors[sector]].toLowerCase()} named a county, city or metro this week.</p>}
        </div>
      </ToolSection>

      <ToolSection title={`The stories: ${SECTOR_NAME[f.sectors[sector]]}, ${geoName(geo)}, week of ${day(wk)}`} id="attention-stories"
        note={usNote ? "Under the United States the list shows the stories that named a state; the counts above include every story about the country." : "Each link opens the outlet's story. The headline is the warehouse's own one-line reading; the outlet's title is not republished."}>
        <label className="mb-2 block text-xs text-muted"><input type="checkbox" checked={onlyOpposition} onChange={(e) => setOnlyOpposition(e.target.checked)} /> only the stories reporting opposition</label>
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
      <p className="text-xs text-muted" data-attention-built={f.built}>{f.note}. Built {f.built.slice(0, 16).replace("T", " ")} UTC from {f.counts.stories.toLocaleString("en-US")} classified stories ({f.counts.opposition.toLocaleString("en-US")} reporting opposition) over {f.counts.weeks_with_stories} weeks; model {f.model.join(", ")}.</p>
    </div>
  );
}
