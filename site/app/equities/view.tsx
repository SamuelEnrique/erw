// Energy Research Warehouse (ERW) site, session 10402 (chain 720, part D): what /equities draws, as one plain component
// so that a test can draw it to HTML without a build (the page adds the brand's frame and the table downloads).
//
// The analyzer of the price board's "Energy equities" group. A company, an index or a segment as a line over any
// window, with any energy price the files carry laid over it on its own axis; a segment's two weightings named plainly;
// a company's filed revenue, income, capital spending, debt and shares by period, each with its filing's address; two
// side by side; and every company by segment in one table that sorts and filters. Where the files hold a company's
// filed figures and its price is held, the filed figures are drawn and the price is a blank that says "license needed".
//
// Every figure is the page files' (lib/equitiesfiles.ts; contract docs/state/page_files_equities.md) and carries its
// key into its file. The page says what was published: no score, no signal, no view.
import type { ReactNode } from "react";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Hint } from "@/components/demand/Hint";
import { Num } from "@/components/Num";
import { SiteLink } from "@/components/SiteLink";
import { TimeChart, type TimeSeries } from "@/components/TimeChart";
import { ChartFrame, HeadlineNumber, InputPanel, SourceLine, ToolHeader, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import { dateWords, type Point } from "@/lib/board";
import { scrollRegion } from "@/lib/cells";
import {
  FREQ_WORDS, LIST_HEAD, MOVE_WORDS, NONE, STATEMENT, WINDOW_KEYS, blankWhy, blankWords, companiesOf, exact, filingsOf, heldWhy, hrefOf, isShown, levelWords, linesOf, millions, noStep, picksOf, pointsOf, pricePoints, queryOf,
  secUrl, segmentLabel, shortWhy, signedLevel, signedPct, windowLike, windowWords, windowed,
  type Choice, type EqCompany, type EqList, type EqMoves, type EqPrice, type EqPrices, type EqSeries, type Filing, type Query, type Sort,
} from "@/lib/equities";
// session 10405 (chain 720, part E): a company's last close, changes and market value, once the list carries them
import { companiesPriced, wholeWords } from "@/lib/equities";
// session 10408 (chain 720, part E): the SEC's filed figures over the periods filed, and the newest period's columns
import { AT_PERIOD_END, FIGURES, FIGURE_DEFAULT, PERIOD_DEFAULT, PERIOD_KEYS, PERIOD_WORDS, figureLine, figureUnit, figureWords, newestOf, type FigureKey, type NewestColumn } from "@/lib/equities";
import { equitiesList, equitiesPrices, equitiesSeries } from "@/lib/equitiesfiles";
import { pfKey } from "@/lib/pagefile";

type Raw = Record<string, string | string[] | undefined>;
type Slot = { mark: "a" | "b"; pick: Choice; series: EqSeries | null; company: EqCompany | null };
const TITLE = "Energy equities";
const fileOf = (slot: Slot) => `equities/${slot.pick.file}`;
const SORT_WORDS: Record<Sort, string> = { name: "Company", ticker: "Ticker", segment: "Segment", exchange: "Exchange", first: "First day", last: "Last day", filed: "Newest period filed" };

function Blank({ what, words, why, k }: { what: string; words: string; why: string; k: string }) {
  return (
    <div className="my-2 flex min-h-24 cursor-help items-center justify-center border border-dashed border-rule bg-panel px-3 py-4 text-center text-sm text-muted" title={why} data-eq-blank={k}>
      {what}: {words}
    </div>
  );
}
const NotHeld = ({ words = "not held", why }: { words?: string; why: string }) => <span className="cursor-help whitespace-nowrap text-muted" title={why} data-not-held="1">{words}</span>;
const pts = (p: Point[]): [number, number | null][] => p.map((x) => [x.t, x.v]);
const nameOf = (slot: Slot) => (slot.pick.kind === "company" ? `${slot.company?.ticker ?? slot.pick.id}, ${slot.company?.name ?? slot.series?.name ?? ""}`.replace(/, $/, "") : slot.pick.label.replace(/^[^:]+: /, ""));

/** The heading of a slot: its name, and on hover what it is and where it comes from. */
function Head({ slot, list }: { slot: Slot; list: EqList }) {
  const c = slot.company, s = slot.series;
  const segs = (slot.pick.kind === "company" ? c?.segments ?? [] : slot.pick.kind === "segment" ? s?.segments ?? [] : []).map((id) => list.segments.find((g) => g.id === id)).filter((g): g is NonNullable<typeof g> => !!g);
  const why = [
    slot.pick.kind === "company" && c ? `${c.name ?? c.ticker} (${c.ticker}${c.exchange ? `, ${c.exchange}` : ""}), SEC number ${c.cik ?? "not said"}${c.sic_label ? `, ${c.sic_label}` : ""}.` : "",
    slot.pick.kind === "index" ? (() => { const x = list.indices.find((i) => i.file === slot.pick.file); return x ? `${x.name ?? x.id}, published by ${x.publisher ?? "a publisher the file does not name"}${x.kind === "proxy" && x.proxy_for ? `; a published proxy for ${x.proxy_for}` : ""}.` : ""; })() : "",
    ...segs.map((g) => `Segment ${g.label}${g.n_companies !== null ? ` (${g.n_companies} companies)` : ""}${g.rule ? `: ${g.rule}` : ""}.`),
    c?.segments_note ? c.segments_note : "",
    s?.source ? `Source: ${s.source}` : "",
  ].filter(Boolean).join(" ");
  return (
    <h3 className="mb-2 font-serif text-xl text-accent" data-eq-slot={slot.mark}>
      <span className={why ? "cursor-help border-b border-dotted border-muted" : undefined} title={why || undefined}>{nameOf(slot)}</span>
      {segs.length && slot.pick.kind === "company" ? <span className="ml-2 font-sans text-sm text-ink">{segs.map((g) => g.label).join(", ")}</span> : null}
    </h3>
  );
}

/** The changes of a line over a day, a week, a month, the year to date and a year, as the file holds them. */
function movesCells(moves: EqMoves | undefined, file: string, path: string, name: string, unit: string): ReactNode[] {
  return MOVE_WORDS.map(([k, words]) => {
    const m = moves?.[k];
    if (!m) return <NotHeld key={k} why={`${name}: the day this change is measured from is not held (${words.toLowerCase()}).`} />;
    const v = m.pct ?? m.ch;
    return (
      <span key={k} title={`${name}, ${words.toLowerCase()}: ${signedLevel(m.ch)} ${unit} against ${levelWords(m.v)} on ${dateWords(m.t)}`} className="cursor-help whitespace-nowrap">
        <Num check={pfKey(file, [path, k, m.pct !== null ? "pct" : "ch"])} raw={v}>{m.pct !== null ? signedPct(m.pct) : signedLevel(m.ch)}</Num>
      </span>
    );
  });
}

/** The changes as one close table, so that the five of them are in view in half the page's width (two side by side at
 *  1280 px, and a phone): the look is ToolTable's, the cells stand closer, and a line that needs no name (a company's
 *  close, an index's level) has no first column. */
function MovesTable({ caption, rows }: { caption: string; rows: { key: string; name: string | null; cells: ReactNode[] }[] }) {
  const named = rows.some((r) => r.name !== null);
  return (
    <div className="overflow-x-auto" {...scrollRegion(caption)} data-eq-moves={rows.length}>
      <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: named ? 380 : 300 }}>
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr className="bg-accent text-white">
            {named ? <th scope="col" className="px-2 py-1.5 font-normal">Change over</th> : null}
            {MOVE_WORDS.map(([k, w]) => <th key={k} scope="col" className="px-2 py-1.5 text-right font-normal" title={named ? undefined : `The change over ${k === "ytd" ? "the year to date" : `a ${w.toLowerCase()}`}`}>{k === "ytd" ? <abbr title="Year to date" className="no-underline">YTD</abbr> : w}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} className="border-b border-rule">
              {named ? <th scope="row" className="px-2 py-1.5 font-normal">{r.name}</th> : null}
              {r.cells.map((c, i) => <td key={i} className="px-2 py-1.5 text-right">{c}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** One slot's line: its latest value, its changes, and the chart over the window with the energy price laid over. */
function LinePanel({ slot, list, q, price, prices }: { slot: Slot; list: EqList; q: Query; price: EqPrice | null; prices: EqPrices | null }) {
  const s = slot.series;
  const k = slot.mark;
  const example = list.example === true || s?.example === true;
  const what = slot.pick.kind === "company" ? "Share price" : slot.pick.kind === "index" ? "Index level" : "Segment line";
  if (!s || !isShown(s)) {
    const status = s?.status ?? slot.company?.price_status, why = s?.why ?? slot.company?.price_why;
    return (
      <div className="min-w-0" data-eq-line={k} data-eq-shown="0">
        <Head slot={slot} list={list} />
        <Blank what={`${what}, ${nameOf(slot)}`} words={s ? blankWords(status, example) : "not held"} why={s ? blankWhy(status, why, example) : `The file of this series (site/data/${fileOf(slot)}) is not on the site.`} k={`line|${k}`} />
      </div>
    );
  }
  const file = fileOf(slot);
  const lines = linesOf(s).map((l) => ({ ...l, all: pointsOf(s, l.col) })).filter((l) => l.all.length);
  if (!lines.length) {
    return <div className="min-w-0" data-eq-line={k} data-eq-shown="0"><Head slot={slot} list={list} /><Blank what={`${what}, ${nameOf(slot)}`} words="not held" why="The file is marked shown and holds no value in its daily rows." k={`line|${k}`} /></div>;
  }
  const first = lines[0];
  const win = windowed(first.all, q.win);
  const priceAll = price && isShown(price) ? pricePoints(prices, price.id) : [];
  const priceWin = windowLike(priceAll, q.win, first.all);
  const colors = ["accent", "series-3"];
  const series: TimeSeries[] = lines.map((l, i) => ({ name: l.name, color: colors[i] ?? "series-5", points: pts(windowLike(l.all, q.win, first.all)) }));
  if (price && priceWin.length) series.push({ name: price.label, color: "ink", dashed: true, y2: true, points: pts(priceWin) });
  const last = s.last, lastV = s.last_value_weight;
  const nDay = s.kind === "segment" ? (() => { const r = s.daily[s.daily.length - 1]; const n = r?.[s.daily_columns.indexOf("n")], nv = r?.[s.daily_columns.indexOf("n_value")]; return typeof n === "number" ? `${n} companies${typeof nv === "number" ? `, ${nv} of them with a public share count` : ""}, on the last day` : null; })() : null;
  const src = `${s.source ? `Source: ${s.source}. ` : ""}${lines.map((l) => `${l.name}: ${l.what}`).join(" ")}${price && priceWin.length ? ` ${price.label}, ${price.unit}: ${price.source ?? "the source is not named in the file"} (ERW table ${price.table ?? "not named"}); a ${price.freq === "M" ? "monthly" : price.freq === "W" ? "weekly" : "daily"} price, each value on its own date.` : ""}`;
  const priceHint = price && !priceWin.length
    ? <>, <Hint words={`${price.label}: ${isShown(price) ? "no value in this window" : blankWords(price.status, prices?.example === true)}`} why={isShown(price) ? `${price.label} holds ${price.first ?? "?"} to ${price.last ?? "?"}; the window drawn is ${win.length ? `${dateWords(new Date(win[0].t).toISOString().slice(0, 10))} to ${dateWords(new Date(win[win.length - 1].t).toISOString().slice(0, 10))}` : "empty"}.` : blankWhy(price.status, price.why, prices?.example === true)} /></>
    : null;
  return (
    <div className="min-w-0" data-eq-line={k} data-eq-shown="1" data-eq-points={win.length}>
      <Head slot={slot} list={list} />
      <div className="mb-4 grid gap-4 sm:grid-cols-2">
        <HeadlineNumber label={s.kind === "company" ? "Last close" : s.kind === "index" ? "Last level" : "Last, every company the same"} unit={last ? first.unit : undefined}
          value={last ? <Num check={pfKey(file, ["last", "v"])} raw={last.v} source={`${first.what} ${s.source ? `Source: ${s.source}` : ""}`}><span data-n={`eq|${k}|last`}>{levelWords(last.v)}</span></Num> : <span className="font-sans text-base"><NotHeld why="The file holds no latest value." /></span>}
          note={last ? dateWords(last.t) : undefined} />
        {s.kind === "segment" ? (
          <HeadlineNumber label="Last, larger companies count more" unit={lastV ? lines[1]?.unit ?? first.unit : undefined}
            value={lastV ? <Num check={pfKey(file, ["last_value_weight", "v"])} raw={lastV.v} source={lines[1]?.what}><span data-n={`eq|${k}|lastv`}>{levelWords(lastV.v)}</span></Num> : <span className="font-sans text-base"><NotHeld words={blankWords(s.held?.value_weight ? "license needed" : null)} why={s.held?.value_weight ?? "The file holds no latest value of the line weighted by market value."} /></span>}
            note={lastV ? `${dateWords(lastV.t)}${nDay ? `; ${nDay}` : ""}` : nDay ?? undefined} />
        ) : null}
      </div>
      <MovesTable caption={`${nameOf(slot)}: the change over a day, a week, a month, the year to date and a year`}
        rows={[{ key: "m", name: s.kind === "segment" ? "Every company the same" : null, cells: movesCells(s.moves, file, "moves", first.name, first.unit) },
          ...(s.kind === "segment" ? [{ key: "v", name: "Larger companies count more", cells: movesCells(s.moves_value_weight, file, "moves_value_weight", "Weighted by market value", lines[1]?.unit ?? first.unit) }] : [])]} />
      <div className="mt-4">
        <ChartFrame title={`${nameOf(slot)}: ${windowWords(q.win).toLowerCase() === "all" ? "every day held" : `the last ${windowWords(q.win).toLowerCase()}`}`} tip={<> <Hint words="source" why={src} />{priceHint}</>}>
          <TimeChart series={series} unit={first.unit} unit2={price && priceWin.length ? price.unit : ""} x="day" height={300}
            ariaLabel={`${nameOf(slot)}, ${lines.map((l) => l.name.toLowerCase()).join(" and ")}, ${first.unit}${price && priceWin.length ? `, with ${price.label} (${price.unit}) laid over it on its own axis` : ""}`} />
        </ChartFrame>
      </div>
    </div>
  );
}

const SHARES = "shares_outstanding";
/** A filed figure in millions, with the exact figure, its concept and its filing on hover, and its key into the file. */
function Filed({ f, col, slot, colAt }: { f: Filing; col: string; slot: Slot; colAt: number }) {
  const v = f[col as keyof Filing] as number | null;
  const s = slot.series!;
  if (v === null) return <NotHeld words="not filed" why={`Not filed for this exact period (${f.form ?? "form not said"}, ${f.period_start ?? "?"} to ${f.period_end}).`} />;
  return (
    <Num check={pfKey(fileOf(slot), ["quarterly", f.i, colAt])} raw={v}
      source={`${exact(v)} ${s.units?.[col] ?? (col === SHARES ? "shares" : "USD")}${s.concepts?.[col] ? `, ${s.concepts[col]}` : ""}. Filed on ${f.form ?? "a form the file does not say"}, ${f.filed ?? "day not said"}${f.accession ? `, accession ${f.accession}` : ""}${f.url ? `: ${f.url}` : ""}`}>{millions(v, col === SHARES)}</Num>
  );
}
const periodWords = (f: Filing) => `${f.months !== null ? `${f.months} months to ` : ""}${f.period_end}`;
const FilingLink = ({ f, children }: { f: Filing; children: ReactNode }) => (secUrl(f.url)
  ? <a href={secUrl(f.url)!} className="inline-block py-1.5 -my-1.5" title={`The filing on the SEC's site${f.accession ? `, accession ${f.accession}` : ""}: ${f.url}`} rel="noopener">{children}</a>
  : <span title={f.accession ? `Accession ${f.accession}` : undefined}>{children}</span>);
const endMs = (f: Filing) => Date.parse(`${f.period_end}T00:00:00Z`);

/** The companies chosen: the chosen figure of each over every period it filed (session 10408, on the SEC's figures),
 *  the newest period each filed side by side, then every period behind a fold. A company's share price may be held
 *  while its filed figures are public: this section is drawn either way. */
function FiledFigures({ slots, list, q }: { slots: Slot[]; list: EqList; q: Query }) {
  const cos = slots.filter((x) => x.pick.kind === "company");
  if (!cos.length) return null;
  const info = cos.map((slot) => {
    const s = slot.series, c = slot.company;
    const status = c?.fundamentals_status ?? "not held";
    const fs = s && s.example !== true && status === "shown" ? filingsOf(s) : [];
    return { slot, fs, newest: newestOf(fs), line: figureLine(fs, q.fig, q.per),
      held: fs.length ? null : { words: s ? blankWords(status === "shown" ? null : status, list.example === true || s.example === true) : "not held", why: s ? blankWhy(status === "shown" ? null : status, c?.fundamentals_why ?? (status === "shown" ? "The file holds no filed period." : null), list.example === true || s.example === true) : `The file of this company (site/data/${fileOf(slot)}) is not on the site.` }, at: (n: string) => (s?.quarterly_columns ?? []).indexOf(n) };
  });
  const words = figureWords(q.fig), unit = figureUnit(q.fig), atEnd = AT_PERIOD_END.includes(q.fig);
  const span = atEnd ? (q.per === "12" ? "at the end of each year reported" : "at the end of each period filed") : `${PERIOD_WORDS[q.per]} to each period end`;
  // the newest period's columns: one for each length of period a company's newest filing reports
  type NewestCell = { x: (typeof info)[number]; col: NewestColumn | null };
  const cols: NewestCell[] = info.flatMap((x): NewestCell[] => (x.held ? [{ x, col: null }] : x.newest.map((col) => ({ x, col }))));
  return (
    <ToolSection title="Filed figures" id="filed">
      <div data-eq-filed={cos.length}>
        <div className={info.length > 1 ? "mb-4 grid gap-6 xl:grid-cols-2" : "mb-4"}>
          {info.map((x) => {
            const k = x.slot.mark, name = nameOf(x.slot);
            if (x.held) return <div key={k} className="min-w-0" data-eq-figure={k} data-eq-points="0"><Blank what={`${words}, ${name}`} words={x.held.words} why={x.held.why} k={`figure|${k}`} /></div>;
            if (x.line.length < 2) {
              return (
                <div key={k} className="min-w-0" data-eq-figure={k} data-eq-points={x.line.length}>
                  <Blank what={`${words}, ${span}, ${name}`} words={x.line.length ? "one period filed" : "not filed"} k={`figure|${k}`}
                    why={x.line.length ? `${name} filed ${words.toLowerCase()} ${span} once, for ${periodWords(x.line[0].f)}: one figure is no line. It is in the table of every period filed, below.` : `${name} filed no ${words.toLowerCase()} ${span}. A figure is drawn for the period its filing reports, never worked out from two filings.`} />
                </div>
              );
            }
            const last = x.line[x.line.length - 1];
            const concept = x.slot.series?.concepts?.[q.fig];
            const src = `${x.slot.series?.source ? `Source: ${x.slot.series.source}. ` : ""}${words}${concept ? ` (${concept})` : ""}, ${span}, as ${name} filed it with the SEC: ${x.line.length} periods, ${x.line[0].f.period_end} to ${last.f.period_end}. A period not filed on its own has no point (a fourth quarter is most often filed inside the year's 12 months); a period filed twice shows the later filing's figure. Each period's filing opens from the table of every period filed, below.`;
            return (
              <div key={k} className="min-w-0" data-eq-figure={k} data-eq-points={x.line.length}>
                <div className="mb-3">
                  <HeadlineNumber label={`${words}, ${atEnd ? `at ${last.f.period_end}` : periodWords(last.f)}`} unit={unit}
                    value={<span data-n={`eq|${k}|figure`}><Filed f={last.f} col={q.fig} slot={x.slot} colAt={x.at(q.fig)} /></span>}
                    note={<FilingLink f={last.f}>{`${last.f.form ?? "Filed"}, ${last.f.filed ?? "day not said"}`}</FilingLink>} />
                </div>
                <ChartFrame title={`${name}: ${words.toLowerCase()}, ${span}`} tip={<> <Hint words="source" why={src} /></>}>
                  <TimeChart series={[{ name: words, color: k === "a" ? "accent" : "series-3", points: x.line.map((p) => [endMs(p.f), p.v / 1e6]) }]} unit={unit} x="month" height={260}
                    ariaLabel={`${name}: ${words.toLowerCase()}, ${span}, ${unit}, ${x.line.length} periods from ${x.line[0].f.period_end} to ${last.f.period_end}, as filed with the SEC`} />
                </ChartFrame>
              </div>
            );
          })}
        </div>
        {/* session 10414: a note the list carries on a company's filings while they are shown (a new registrant whose
            history starts late, a filer that stopped): said in the file's own words, under the company's figures */}
        {info.filter((x) => !x.held && x.slot.company?.fundamentals_status === "shown" && x.slot.company.fundamentals_why).map((x) => (
          <p key={x.slot.mark} className="mb-3 max-w-3xl text-sm" data-eq-filed-note={x.slot.pick.id}>A note on what {x.slot.company!.ticker} filed: {x.slot.company!.fundamentals_why}.</p>
        ))}
        <ToolTable minWidth={Math.max(420, 180 + cols.length * 150)} caption="The newest period each company filed, in USD million (shares in millions): one column for each length of period its newest filing reports"
          head={["Newest period filed", ...cols.map(({ x, col }) => <span key={`${x.slot.mark}${col?.months ?? ""}`} data-eq-newest={`${x.slot.mark}|${col ? col.months ?? "end" : "held"}`}>{x.slot.pick.id}{col ? <>, <FilingLink f={col.head}>{periodWords(col.head)}</FilingLink></> : null}</span>)]}
          rows={[
            { key: "form", cells: ["Form, day filed", ...cols.map(({ x, col }) => (col ? `${col.head.form ?? "not said"}, ${col.head.filed ?? "not said"}` : <NotHeld key={x.slot.mark} words={x.held!.words} why={x.held!.why} />))] },
            ...STATEMENT.map(([c, w, u]) => ({ key: c, cells: [<span key="w" title={`${u}${AT_PERIOD_END.includes(c as FigureKey) ? "; the figure at the period's end" : "; the sum over the period"}`} className="cursor-help">{w}</span>,
              ...cols.map(({ x, col }, i) => {
                if (!col) return <NotHeld key={i} words={x.held!.words} why={x.held!.why} />;
                const cell = col.cells[c as FigureKey];
                return <span key={i} data-n={`eq|${x.slot.mark}|filed|${c}${col === x.newest[0] ? "" : `|${col.months}`}`}><Filed f={cell?.f ?? { ...col.head, [c]: null }} col={c} slot={x.slot} colAt={x.at(c)} /></span>;
              })] })),
          ]} />
        {info.filter((x) => !x.held).map((x) => (
          <details key={x.slot.mark} className="mt-3 border-b border-rule py-2" data-eq-periods={x.slot.mark}>
            <summary className="cursor-pointer text-sm">{nameOf(x.slot)}: every period filed ({x.fs.length}), USD million</summary>
            <div className="pt-2">
              <ToolTable minWidth={720} caption={`${nameOf(x.slot)}: every period filed, newest first, in USD million (shares in millions); each period opens its filing`}
                head={["Period", "Form", "Filed", ...STATEMENT.map(([col, words, unit]) => <span key={col} title={`${unit}${x.slot.series?.concepts?.[col] ? `; ${x.slot.series.concepts[col]}` : ""}`} className="cursor-help">{words}</span>)]}
                rows={x.fs.map((f) => ({ key: `${f.i}`, cells: [<FilingLink key="p" f={f}>{periodWords(f)}</FilingLink>, f.form ?? "", f.filed ?? "", ...STATEMENT.map(([col]) => <Filed key={col} f={f} col={col} slot={x.slot} colAt={x.at(col)} />)] }))} />
            </div>
          </details>
        ))}
      </div>
    </ToolSection>
  );
}

/** Every company by segment: one table, filtered and sorted by the address. */
function Companies({ list, q, first }: { list: EqList; q: Query; first: string | null }) {
  const rows = companiesOf(list, q);
  // session 10405 (chain 720, part E): the last close, the five changes and the market value of each company, as the
  // list carries them since the contract's dated line of 26 November (data request 571). The columns are drawn only
  // when a company of the list holds one of them: a list with none is the table as it was. A figure's key names the
  // company by its position in the file's own list, whatever the order the table is in.
  const priced = companiesPriced(list.companies);
  const LIST = "equities/index.json";
  const pricedCells = (c: EqCompany): ReactNode[] => {
    const i = list.companies.indexOf(c);
    const heldWords = blankWords(c.price_status), heldWhy2 = blankWhy(c.price_status, c.price_why);
    const none = (key: string, what: string) => (c.price_status === "shown" ? <NotHeld key={key} why={`${c.ticker}: the list holds no ${what}.`} /> : <NotHeld key={key} words={heldWords} why={heldWhy2} />);
    return [
      c.last_close ? <span key="lc" title={`${c.ticker}: the close of ${dateWords(c.last_close.t)}, USD a share`} className="cursor-help whitespace-nowrap"><Num check={pfKey(LIST, ["companies", i, "last_close", "v"])} raw={c.last_close.v}>{levelWords(c.last_close.v)}</Num></span> : none("lc", "last close"),
      ...MOVE_WORDS.map(([k, words]) => {
        const m = c.moves?.[k];
        if (!m) return none(k, `change over ${words.toLowerCase()}`);
        return <span key={k} title={`${c.ticker}, ${words.toLowerCase()}: ${signedLevel(m.ch)} USD against ${levelWords(m.v)} on ${dateWords(m.t)}`} className="cursor-help whitespace-nowrap"><Num check={pfKey(LIST, ["companies", i, "moves", k, m.pct !== null ? "pct" : "ch"])} raw={m.pct ?? m.ch}>{m.pct !== null ? signedPct(m.pct) : signedLevel(m.ch)}</Num></span>;
      }),
      c.market_value ? <span key="mv" title={`${c.ticker}: the close of ${dateWords(c.market_value.t)} times the shares it last filed, USD`} className="cursor-help whitespace-nowrap"><Num check={pfKey(LIST, ["companies", i, "market_value", "v"])} raw={c.market_value.v}>{wholeWords(c.market_value.v)}</Num></span> : none("mv", "market value"),
    ];
  };
  // session 10414 (chain 720, part E): the newest period each company filed, as the list carries it since the contract's
  // dated line of 27 November (data requests 578 and 579): the period's end and form, opening the filing, and its
  // revenue in USD million with the months it covers. A list none of whose companies carries the field is the table
  // as it was. A company whose filings carry a note while shown (a new registrant, a filer that stopped) says so.
  const withNewest = list.companies.some((c) => c.newest_filed !== undefined);
  const filedCells = (c: EqCompany): ReactNode[] => {
    if (c.fundamentals_status !== "shown") return [<NotHeld key="f" words={blankWords(c.fundamentals_status)} why={blankWhy(c.fundamentals_status, c.fundamentals_why)} />];
    if (!withNewest) return ["shown"];
    const n = c.newest_filed, i = list.companies.indexOf(c);
    if (!n) return [<NotHeld key="f" words="none filed" why={`${c.ticker}: the list holds no newest period for this company.`} />];
    const words = `${n.period_end}${n.form ? `, ${n.form}` : ""}`;
    const note = c.fundamentals_why ? <span className="cursor-help text-muted" title={`A note on what ${c.ticker} filed: ${c.fundamentals_why}`} data-eq-filed-note-mark={c.id}> (note)</span> : null;
    const r = n.revenue;
    const span = r && r.months !== null ? `${r.months} months to ${n.period_end}` : `the period to ${n.period_end}`;
    // seen in a build at 1280 px: a column of its own for the revenue made the table wider than its frame, and the
    // figure had to be scrolled to. It is the cell's second line, with its unit and its months in words
    const revenue = r
      ? <span className="cursor-help whitespace-nowrap" title={`${c.ticker}: revenue filed for ${span}, ${exact(r.v)} USD${n.form ? `, on ${n.form}` : ""}${n.filed ? `, filed ${n.filed}` : ""}. Two companies' revenues compare only where the months are the same.`}><span className="text-muted">Revenue </span><Num check={pfKey(LIST, ["companies", i, "newest_filed", "revenue", "v"])} raw={r.v}>{millions(r.v)}</Num><span className="text-muted"> USD million{r.months !== null ? `, ${r.months} months` : ""}</span></span>
      : <NotHeld words="revenue not filed" why={`${c.ticker}: its newest filing (${words}) gives no revenue under the concept the ERW reads.`} />;
    return [
      <span key="f" className="block" data-eq-newest-of={c.id}>
        <span className="block whitespace-nowrap">{secUrl(n.url) ? <a href={secUrl(n.url)!} className="inline-block py-1 -my-1" rel="noopener" title={`The filing on the SEC's site${n.filed ? `, filed ${n.filed}` : ""}: ${n.url}`}>{words}</a> : <span title={n.filed ? `Filed ${n.filed}` : undefined}>{words}</span>}{note}</span>
        <span className="block">{revenue}</span>
      </span>,
    ];
  };
  const sortHead = (s: Sort) => {
    const on = q.sort === s;
    // session 10414: a period's sort opens newest first (then oldest first, then the list's own order) and says so in
    // days' words; every other sort is as it was (A to Z, then Z to A, then the list's own order)
    if (s === "filed") {
      const next = !on ? { sort: s, desc: true } : q.desc ? { sort: s, desc: false } : { sort: null, desc: false };
      return <SiteLink key={s} href={hrefOf(q, next, first, "#companies")} title={on ? (q.desc ? "Sorted newest first: press for oldest first" : "Sorted oldest first: press for the list's own order") : "Sort by the newest period filed, newest first"} data-eq-sort={s} className="inline-block py-1">{SORT_WORDS[s]}{on ? (q.desc ? " (newest first)" : " (oldest first)") : ""}</SiteLink>;
    }
    return <SiteLink key={s} href={hrefOf(q, { sort: on && q.desc ? null : s, desc: on && !q.desc }, first, "#companies")} title={on ? (q.desc ? "Sorted Z to A: press for the list's own order" : "Sorted A to Z: press for Z to A") : `Sort by ${SORT_WORDS[s].toLowerCase()}`} data-eq-sort={s} className="inline-block py-1">{SORT_WORDS[s]}{on ? (q.desc ? " (Z to A)" : " (A to Z)") : ""}</SiteLink>;
  };
  return (
    <ToolSection title="Every company" id="companies">
      <form method="get" action="/equities#companies" className="mb-3 flex flex-wrap items-end gap-3 bg-paper px-4 py-3 text-sm [&_label]:min-w-0 [&_label]:max-w-full [&_select]:max-w-full" data-eq-filter="1">
        {q.a && q.a !== first ? <input type="hidden" name="a" value={q.a} /> : null}
        {q.b ? <input type="hidden" name="b" value={q.b} /> : null}
        {q.p ? <input type="hidden" name="p" value={q.p} /> : null}
        {q.win !== "1y" ? <input type="hidden" name="win" value={q.win} /> : null}
        {q.fig !== FIGURE_DEFAULT ? <input type="hidden" name="fig" value={q.fig} /> : null}
        {q.per !== PERIOD_DEFAULT ? <input type="hidden" name="per" value={q.per} /> : null}
        {q.sort ? <input type="hidden" name="sort" value={q.sort} /> : null}
        {q.sort && q.desc ? <input type="hidden" name="dir" value="desc" /> : null}
        <AutoSubmitSelect name="seg" value={q.seg ?? ""} options={[{ value: "", label: "Every segment" }, ...list.segments.map((s) => ({ value: s.id, label: s.label }))]} label="Segment" />
        <label className="flex flex-col text-xs text-muted">Name, ticker or industry holds<input type="search" name="q" defaultValue={q.q} maxLength={60} className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" /></label>
        <label className="flex items-center gap-2 text-sm text-ink"><input type="checkbox" name="shown" value="1" defaultChecked={q.shown} />Share price shown</label>
        <label className="flex items-center gap-2 text-sm text-ink"><input type="checkbox" name="filed" value="1" defaultChecked={q.filed === true} />Filed figures shown</label>
        <button type="submit" className="border border-rule bg-white px-3 py-1 text-sm">Filter</button>
        <span className="text-sm" data-eq-count={`${rows.length}|${list.companies.length}`}>{rows.length.toLocaleString("en-US")} of {list.companies.length.toLocaleString("en-US")} companies</span>
      </form>
      <ToolTable words minWidth={(priced ? 1280 : 720) + (withNewest ? 60 : 0)} caption={`The listed energy companies${q.seg ? ` of ${segmentLabel(list, q.seg)}` : ""}: ${rows.length} of ${list.companies.length}${withNewest ? "; each with the newest period it filed and that period's revenue in USD million, with the months the period covers" : ""}`}
        head={[sortHead("name"), sortHead("ticker"), sortHead("exchange"), sortHead("segment"), "Industry", <span key="p">Share price: {sortHead("first")} to {sortHead("last")}</span>,
          ...(withNewest ? [sortHead("filed")] : ["Filed figures"]),
          ...(priced ? [<span key="lc" data-eq-priced="1">Last close, USD</span>, ...MOVE_WORDS.map(([k, words]) => <span key={k}>{words}</span>), <span key="mv" className="cursor-help" title="The last close times the shares the company last filed, in USD.">Market value, USD</span>] : [])]}
        rows={rows.map((c) => ({ key: c.id, cells: [
          <SiteLink key="n" href={hrefOf(q, { a: c.id }, first, "#line")} className="inline-block py-1 -my-1" title={`Draw ${c.ticker}${c.cik ? `; SEC number ${c.cik}` : ""}`}>{c.name ?? c.ticker}</SiteLink>,
          c.ticker, c.exchange ?? "",
          <span key="s" title={[...c.segments.map((id) => { const g = list.segments.find((x) => x.id === id); return g?.rule ? `${g.label}: ${g.rule}` : g?.label ?? id; }), c.segments_note ?? ""].filter(Boolean).join(" ")} className="cursor-help">{c.segments.map((id) => segmentLabel(list, id)).join(", ")}</span>,
          <span key="i" title={c.sic ? `SIC ${c.sic}` : undefined}>{c.sic_label ?? ""}</span>,
          c.price_status === "shown" ? `${c.first ?? "?"} to ${c.last ?? "?"}` : <NotHeld key="p" words={blankWords(c.price_status)} why={blankWhy(c.price_status, c.price_why)} />,
          ...filedCells(c),
          ...(priced ? pricedCells(c) : []),
        ] }))} />
    </ToolSection>
  );
}

/** The segments and the indices, each a link that draws it. A segment the list cannot yet fill says why (its rule's
 *  reason, the list's reason for its line); with no index in the list the place of the indices says why. */
function Segments({ list, q, first }: { list: EqList; q: Query; first: string | null }) {
  const picks = picksOf(list);
  const lineWhy = heldWhy(list, ["prices", "companies"]) || "The list names no line for this segment.";
  return (
    <ToolSection title="Segments and indices" id="segments">
      <div className="grid gap-6 xl:grid-cols-2" data-eq-segments={list.segments.length}>
        <div className="min-w-0">
          <ToolTable words minWidth={360} caption="The segments, each with the count of its companies and the rule that puts a company in it (on hover)" head={["Segment", "Companies", "Its line"]}
            rows={list.segments.map((s) => {
              const pick = picks.find((p) => p.kind === "segment" && (list.segment_series ?? []).some((x) => x.segment === s.id && x.file === p.file));
              const rule = s.rule ?? s.rule_why ?? null;
              return { key: s.id, cells: [<span key="l" title={rule ? (s.rule ? `The rule: ${rule}` : `No rule is applied yet. ${rule}`) : undefined} className={rule ? "cursor-help" : undefined}>{s.label}</span>,
                // session 10408: a segment no SEC industry code holds alone has no rule and so no company (the files of
                // 27 November): its count is the file's nought with the file's reason on hover, and opens no empty table
                s.n_companies === 0 && !s.rule && s.rule_why ? <span key="n" className="inline-block min-w-6 cursor-help py-0.5 text-center" title={`No company is placed in ${s.label}: ${s.rule_why}`} data-eq-no-rule={s.id}>0</span>
                : s.n_companies !== null ? <SiteLink key="n" href={hrefOf(q, { seg: s.id }, first, "#companies")} className="inline-block min-w-6 py-0.5 text-center" title={`The companies of ${s.label} in the table above`}>{s.n_companies.toLocaleString("en-US")}</SiteLink>
                  : <NotHeld key="n" words={shortWhy(s.rule_why ?? list.held?.companies)} why={s.rule_why ?? list.held?.companies ?? "The list holds no count for this segment."} />,
                pick ? <SiteLink key="d" href={hrefOf(q, { a: pick.id }, first, "#line")} className="inline-block py-0.5">Draw it</SiteLink> : <NotHeld key="d" words={shortWhy(list.held?.prices ?? list.held?.companies)} why={lineWhy} />] };
            })} />
        </div>
        <div className="min-w-0">
          {list.indices.length ? (
            <ToolTable words minWidth={360} caption="The energy indices and the published proxies that stand for them" head={["Index", "Publisher", "Days held"]}
              rows={list.indices.map((x) => {
                const pick = picks.find((p) => p.kind === "index" && p.file === x.file);
                return { key: x.id, cells: [pick && x.status === "shown" ? <SiteLink key="n" href={hrefOf(q, { a: pick.id }, first, "#line")} title={x.kind === "proxy" && x.proxy_for ? `A published proxy for ${x.proxy_for}` : undefined}>{x.name ?? x.id}</SiteLink> : <span key="n">{x.name ?? x.id}</span>,
                  x.publisher ?? "", x.status === "shown" ? `${x.first ?? "?"} to ${x.last ?? "?"}` : <NotHeld key="d" words={blankWords(x.status)} why={blankWhy(x.status, x.why)} />] };
              })} />
          ) : <Blank what="Energy indices" words={shortWhy(list.held?.indices)} why={list.held?.indices ?? "The list holds no index, and does not say why."} k="indices" />}
        </div>
      </div>
    </ToolSection>
  );
}

/** The energy prices the files carry: each with its latest value and its changes, and, where nothing else can be drawn
 *  over it, the chosen one as a line of its own. A held price is a row that says why. A change the series' step does
 *  not have (a monthly price over a day) says the step instead of repeating the month's figure. */
function Prices({ prices, q, first, drawn, alone }: { prices: EqPrices; q: Query; first: string | null; drawn: EqPrice | null; alone: boolean }) {
  const file = "equities/energy_prices.json";
  const all = drawn && isShown(drawn) ? pricePoints(prices, drawn.id) : [];
  const win = windowed(all, q.win);
  const at = drawn ? prices.series.indexOf(drawn) : -1;
  return (
    <ToolSection title="Energy prices" id="prices">
      {alone && drawn ? (isShown(drawn) && win.length ? (
        <div className="mb-4" data-eq-price={drawn.id} data-eq-points={win.length}>
          <div className="mb-4 grid gap-4 sm:grid-cols-2">
            <HeadlineNumber label={drawn.label} unit={drawn.last_value ? drawn.unit : undefined}
              value={drawn.last_value ? <Num check={pfKey(file, ["series", at, "last_value", "v"])} raw={drawn.last_value.v} source={`${drawn.source ?? "The source is not named in the file"} (ERW table ${drawn.table ?? "not named"}).`}><span data-n="eq|price|last">{levelWords(drawn.last_value.v)}</span></Num> : <span className="font-sans text-base"><NotHeld why="The file holds no latest value." /></span>}
              note={drawn.last_value ? dateWords(drawn.last_value.t, drawn.freq === "M" || drawn.freq === "Q" ? "M" : "D") : undefined} />
          </div>
          <ChartFrame title={`${drawn.label}: ${windowWords(q.win).toLowerCase() === "all" ? "every value held" : `the last ${windowWords(q.win).toLowerCase()}`}`} tip={<> <Hint words="source" why={`${drawn.source ?? "The source is not named in the file"} (ERW table ${drawn.table ?? "not named"}); a ${FREQ_WORDS[drawn.freq] ?? "daily"} price, each value on its own date, held ${drawn.first ?? "?"} to ${drawn.last ?? "?"}.`} /></>}>
            <TimeChart series={[{ name: drawn.label, color: "accent", points: pts(win) }]} unit={drawn.unit} x={drawn.freq === "M" || drawn.freq === "Q" ? "month" : "day"} height={300} ariaLabel={`${drawn.label}, ${drawn.unit}`} />
          </ChartFrame>
        </div>
      ) : <Blank what={drawn.label} words={isShown(drawn) ? "no value in this window" : blankWords(drawn.status, prices.example === true)} why={isShown(drawn) ? `${drawn.label} holds ${drawn.first ?? "?"} to ${drawn.last ?? "?"}.` : blankWhy(drawn.status, drawn.why, prices.example === true)} k={`price|${drawn.id}`} />) : null}
      <div data-eq-prices={prices.series.length}>
        <ToolTable minWidth={640} caption="The energy prices the files carry: the latest value of each and its change over a day, a week, a month, the year to date and a year, in percent"
          head={[alone ? "Price" : "Price (press one to lay it over)", "Latest, its date", ...MOVE_WORDS.map(([k, w]) => (k === "ytd" ? <abbr key={k} title="Year to date" className="no-underline">YTD</abbr> : w))]}
          rows={prices.series.map((x, i) => {
            const name = <SiteLink key="n" href={hrefOf(q, { p: x.id }, first, alone ? "#prices" : "#line")} title={x.source ? `${x.source}${x.table ? ` (ERW table ${x.table})` : ""}` : undefined} className="inline-block min-w-[12rem] py-0.5">{x.label}</SiteLink>;
            if (!isShown(x) || !x.last_value) return { key: x.id, highlight: drawn?.id === x.id, cells: [name], wide: <span className="cursor-help" title={blankWhy(x.status, x.why, prices.example === true)} data-eq-price-held={x.id}>{blankWords(isShown(x) ? null : x.status, prices.example === true)}</span> };
            // the unit stands after the value, small, as the price board writes a row's, and the value's date under it
            // (two columns fewer: the nine columns ran 147 px past the table's frame at 1280 px)
            return { key: x.id, highlight: drawn?.id === x.id, cells: [name,
              <span key="v" className="inline-block whitespace-nowrap">
                <span className="block"><Num check={pfKey(file, ["series", i, "last_value", "v"])} raw={x.last_value.v} source={`${x.source ?? ""}`}>{levelWords(x.last_value.v)}</Num><span className="ml-1 font-sans text-xs text-muted">{x.unit}</span></span>
                <span className="block cursor-help font-sans text-xs" title={`A ${FREQ_WORDS[x.freq] ?? "daily"} price; held ${x.first ?? "?"} to ${x.last ?? "?"}`}>{dateWords(x.last_value.t, x.freq === "M" || x.freq === "Q" ? "M" : "D")}</span>
              </span>,
              ...MOVE_WORDS.map(([k, w]) => {
                if (noStep(x.freq, k)) return <span key={k} className="cursor-help text-muted" title={`A ${FREQ_WORDS[x.freq]} price has no change over a ${w.toLowerCase()} of its own.`} data-eq-no-step={`${x.id}|${k}`}>{FREQ_WORDS[x.freq]}</span>;
                const m = x.moves?.[k];
                if (!m) return <NotHeld key={k} why={`${x.label}: the value this change is measured from is not held (${w.toLowerCase()}).`} />;
                return <span key={k} title={`${signedLevel(m.ch)} ${x.unit} against ${levelWords(m.v)} on ${dateWords(m.t, x.freq === "M" || x.freq === "Q" ? "M" : "D")}`} className="cursor-help whitespace-nowrap"><Num check={pfKey(file, ["series", i, "moves", k, m.pct !== null ? "pct" : "ch"])} raw={m.pct ?? m.ch}>{m.pct !== null ? signedPct(m.pct) : signedLevel(m.ch)}</Num></span>;
              })] };
          })} />
      </div>
    </ToolSection>
  );
}

export function EquitiesView({ query }: { query: Raw }) {
  const list = equitiesList();
  const prices = equitiesPrices();
  const picks = picksOf(list);
  const q = queryOf(query, list, prices);
  const first = picks[0]?.id ?? null;
  const lead = (
    <>The listed energy companies by segment, the energy indices, and the energy prices beside them: a line over any window, a company&apos;s filed figures, two side by side.{" "}
      <Hint words="What it is" why="Levels and plain changes, as published: closing prices and index levels from their sources, a company's figures from its own filings with the SEC, energy prices from the ERW's price tables. A segment's line is built by the ERW from its companies' prices by the written rule of the method note. No score, no signal and no view." />.</>
  );
  const header = (
    <ToolHeader title={TITLE} lead={lead}
      under={<p className="mt-2 text-xs text-muted" data-license-line="1">{list && list.example !== true ? `Files built ${list.built.slice(0, 10)}${list.last_day ? `; the newest trading day held is ${list.last_day}` : ""}.` : "No equities figure has been written yet."}</p>} />
  );
  if (!list || list.example === true) {
    return (
      <div data-equities="1" data-eq-state={list?.example === true ? "example" : "no-files"}>
        {header}
        <Blank what={TITLE} words="not built yet" k="files"
          why={list?.example === true ? "The equities files on the site are the contract's examples, every value empty: no figure has been written yet (docs/state/page_files_equities.md). Nothing is drawn until the data machine writes them." : "The equities page files (site/data/equities/) are not on the site yet. Nothing is drawn until they are."} />
      </div>
    );
  }
  const slots: Slot[] = [q.a, q.b].map((id, i) => {
    const pick = picks.find((p) => p.id === id);
    return pick ? { mark: i ? "b" : "a", pick, series: equitiesSeries(pick.file), company: pick.kind === "company" ? list.companies.find((c) => c.file === pick.file) ?? null : null } as Slot : null;
  }).filter((x): x is Slot => x !== null);
  const real = prices && prices.example !== true ? prices : null;
  // with nothing of the list to draw, the page opens on the first energy price the files show, as a line of its own
  const alone = !slots.length;
  // session 10408: and so it does when what is chosen has no line to lay a price over (a company whose share price is
  // held, which is every company of the files of 27 November): the energy price keeps its own chart, under the
  // company's blank and its filed figures, as it had before the companies were in the files
  const priceAlone = alone || !slots.some((x) => isShown(x.series));
  const anyCompany = slots.some((x) => x.pick.kind === "company");
  // what the page opens on, for the words beside "Reset to the defaults": the list's first thing, with a price laid
  // over only if that thing has a line, and a filed figure only if it is a company
  const opens = picks[0] ? { name: picks[0].label.replace(/^[^:]+: /, ""), line: slots[0]?.pick.id === picks[0].id ? isShown(slots[0].series) : isShown(equitiesSeries(picks[0].file)), company: picks[0].kind === "company" } : null;
  const price = real ? real.series.find((x) => x.id === (q.p ?? (priceAlone ? real.series.find((s) => isShown(s))?.id : undefined))) ?? null : null;
  const options = picks.map((p) => ({ value: p.id, label: p.label }));
  const priceOptions = (real?.series ?? []).map((x) => ({ value: x.id, label: `${x.label} (${x.status === "shown" ? x.unit : blankWords(x.status)})` }));
  const tables = [...new Set([...(list.tables ?? []), ...(price?.table ? [price.table] : [])])];
  // session 10407 (the browser read of 26 November, row EQ1): the blank's face takes its words from the first reason
  // the list holds of the prices, the companies and the indices, and its hover gave the reasons in another order, so
  // the face read "license needed" over a hover that began "source needed". One order for both: the hover begins with
  // the reason the face names, then gives the others.
  const nothing = heldWhy(list, ["prices", "companies", "indices"]) || "The list holds no company, index or segment line, and does not say why.";
  return (
    <div data-equities="1" data-eq-state="files" data-eq-window={q.win} data-eq-picks={picks.length}>
      {header}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,16rem)_minmax(0,1fr)]">
        <div className="min-w-0 lg:sticky lg:top-2 lg:self-start">
          <InputPanel title="Choices" reset={{ href: "/equities", defaults: !opens ? "the first energy price the files show, the last year" : `${opens.name} alone, ${opens.line ? "no price laid over" : "the first energy price the files show"}, the last year${opens.company ? `, ${figureWords(FIGURE_DEFAULT).toLowerCase()} by ${PERIOD_WORDS[PERIOD_DEFAULT]}` : ""}` }}>
            <form method="get" action="/equities" className="flex flex-col gap-3 text-sm [&_label]:min-w-0 [&_label]:max-w-full [&_select]:w-full [&_select]:max-w-full" data-eq-form="1">
              {alone ? null : <AutoSubmitSelect name="a" value={slots[0].pick.id} options={options} label="A: a segment, an index or a company" />}
              {alone ? null : <AutoSubmitSelect name="b" value={q.b ?? NONE} options={[{ value: NONE, label: "None" }, ...options.filter((o) => o.value !== slots[0].pick.id)]} label="B, side by side" />}
              {priceAlone
                ? <AutoSubmitSelect name="p" value={price?.id ?? NONE} options={priceOptions.length ? priceOptions : [{ value: NONE, label: "None" }]} label="Energy price" />
                : <AutoSubmitSelect name="p" value={q.p ?? NONE} options={[{ value: NONE, label: "None" }, ...priceOptions]} label="Energy price laid over" />}
              <AutoSubmitSelect name="win" value={q.win} options={WINDOW_KEYS.map((w) => ({ value: w, label: windowWords(w) }))} label={anyCompany && priceAlone ? "Window of the price" : "Window"} />
              {anyCompany ? <AutoSubmitSelect name="fig" value={q.fig} options={FIGURES.map((f) => ({ value: f, label: figureWords(f) }))} label="Filed figure" /> : q.fig !== FIGURE_DEFAULT ? <input type="hidden" name="fig" value={q.fig} /> : null}
              {anyCompany ? <AutoSubmitSelect name="per" value={q.per} options={PERIOD_KEYS.map((p) => ({ value: p, label: PERIOD_WORDS[p] }))} label="Its periods" /> : q.per !== PERIOD_DEFAULT ? <input type="hidden" name="per" value={q.per} /> : null}
              {q.filed ? <input type="hidden" name="filed" value="1" /> : null}
              {q.seg ? <input type="hidden" name="seg" value={q.seg} /> : null}
              {q.q ? <input type="hidden" name="q" value={q.q} /> : null}
              {q.shown ? <input type="hidden" name="shown" value="1" /> : null}
              {q.sort ? <input type="hidden" name="sort" value={q.sort} /> : null}
              {q.sort && q.desc ? <input type="hidden" name="dir" value="desc" /> : null}
              <button type="submit" className="self-start border border-rule bg-white px-3 py-1 text-sm">Show</button>
            </form>
          </InputPanel>
        </div>
        <div className="min-w-0">
          <ToolSection title="The line" id="line">
            {alone
              ? <Blank what="Companies, indices and segment lines" words={shortWhy(list.held?.prices ?? list.held?.companies ?? list.held?.indices)} why={nothing} k="line|none" />
              : <div className={slots.length > 1 ? "grid gap-6 xl:grid-cols-2" : ""}>{slots.map((x) => <LinePanel key={x.mark} slot={x} list={list} q={q} price={price} prices={prices} />)}</div>}
          </ToolSection>
          <FiledFigures slots={slots} list={list} q={q} />
          {real ? <Prices prices={real} q={q} first={first} drawn={price} alone={priceAlone} /> : null}
          {list.companies.length ? <Companies list={list} q={q} first={first} /> : (
            <ToolSection title="Every company" id="companies">
              <Blank what="The listed energy companies" words={shortWhy(list.held?.companies)} why={list.held?.companies ?? "The list holds no company, and does not say why."} k="companies" />
            </ToolSection>
          )}
          <Segments list={list} q={q} first={first} />
          <ToolSection title="Downloads" id="downloads">
            <ul className="list-none space-y-1 p-0 text-sm" data-eq-downloads="1">
              {slots.map((x) => (
                <li key={x.mark} data-eq-download={x.pick.id}>{nameOf(x)}, day by day:{" "}
                  <a href={`/equities/rows?id=${encodeURIComponent(x.pick.id)}`} download data-download="csv">CSV</a>,{" "}
                  <a href={`/equities/rows/python?id=${encodeURIComponent(x.pick.id)}`} download data-download="python">Python</a>,{" "}
                  <a href={`/equities/rows/stata?id=${encodeURIComponent(x.pick.id)}`} download data-download="stata">Stata</a>
                  {x.pick.kind === "company" ? <>; the figures it filed:{" "}
                    <a href={`/equities/filed?id=${encodeURIComponent(x.pick.id)}`} download data-download="csv">CSV</a>,{" "}
                    <a href={`/equities/filed/python?id=${encodeURIComponent(x.pick.id)}`} download data-download="python">Python</a>,{" "}
                    <a href={`/equities/filed/stata?id=${encodeURIComponent(x.pick.id)}`} download data-download="stata">Stata</a></> : null}</li>
              ))}
              {list.companies.length ? (
                <li data-eq-download="list">Every company, with its segment and what is held ({LIST_HEAD.length} columns):{" "}
                  <a href="/equities/list" download data-download="csv">CSV</a>,{" "}
                  <a href="/equities/list/python" download data-download="python">Python</a>,{" "}
                  <a href="/equities/list/stata" download data-download="stata">Stata</a></li>
              ) : null}
              <li><SiteLink href="/board#equities" className="inline-block py-0.5">The price board&apos;s energy equities group</SiteLink></li>
            </ul>
          </ToolSection>
          {tables.length ? <SourceLine tables={tables} note={list.method ? <>Method: <a href={`/data/methods/${list.method.replace(/^docs\/methods\//, "").replace(/\.md$/, "")}`}>the method note</a>.</> : undefined} /> : null}
        </div>
      </div>
    </div>
  );
}

/** The tables the page's files were built from, and the energy prices' own, for the page's table downloads. */
export function tablesOf(): string[] {
  const list = equitiesList();
  if (!list || list.example === true) return [];
  const prices = equitiesPrices();
  return [...new Set([...(list.tables ?? []), ...(prices && prices.example !== true ? prices.series.map((x) => x.table).filter((t): t is string => !!t) : [])])];
}
