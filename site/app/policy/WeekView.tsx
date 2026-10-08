"use client";
// Session 157: "What changed this week", the second view of /policy (in review). The regulatory actions of the last
// seven and thirty days, counted by agency and topic (a small chart that answers the mouse and the keyboard) and
// listed under it by agency, newest first: each with its date, its status as the source words it, the agency or
// regulator and its docket or document number as a link to the source document (the Register's summary or the
// document's own sentence on hover), its topics, and a one-line read marked as a model's. Filters by agency, topic,
// grid and large-load relevance. The window and every filter are in the address (lib/policyweek.ts: chosenOf,
// weekHref), so an address restores the view. The server reads and words the rows (lib/policyweekdata.ts); this file
// only chooses among them. MISO reads "paused while terms are reviewed" and shows no row. The face carries no method:
// a thing not held is a short placeholder with its reason on hover, and the method is the Method note
// (docs/methods/policy_monitor.md).
import { useState, type ReactNode } from "react";
import { Hover } from "@/components/demand/Hover";
import { dayWords } from "@/lib/rules";
import {
  NONE_WORDS, NO_READ, PAUSED_WORDS, PAUSE_WHY, WINDOWS, cellTip, countsOf, emptyWhy, groupsOf, paused, shownRows, weekHref, windowWhy,
  type Body, type Chosen, type Topic, type WeekRow,
} from "@/lib/policyweek";

/** Rows of a group shown before its fold. */
const SHOWN = 10;
const dotted = "cursor-help border-b border-dotted border-muted";

function Missing({ why, words }: { why: string; words: string }) {
  return <span className={`${dotted} italic text-muted`} title={why} data-missing="1">{words}</span>;
}
function Chip({ on, onClick, title, children, ...data }: { on: boolean; onClick: () => void; title?: string; children: ReactNode } & Record<`data-${string}`, string>) {
  return (
    <button type="button" aria-pressed={on} onClick={onClick} title={title} {...data} style={{ color: on ? "#fff" : "var(--color-ink)" }}
      className={`cursor-pointer border px-2 py-0.5 text-xs ${on ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>{children}</button>
  );
}
function Filter({ label, children, ...data }: { label: string; children: ReactNode } & Record<`data-${string}`, string>) {
  return (
    <div className="flex items-baseline gap-1" role="group" aria-label={label} {...data}>
      <span className="mr-1 w-14 shrink-0 text-xs uppercase tracking-wide text-muted">{label}</span>
      <div className="flex flex-wrap items-baseline gap-1">{children}</div>
    </div>
  );
}

function Row({ r, topics }: { r: WeekRow; topics: Map<string, Topic> }) {
  return (
    <tr className="border-b border-rule align-top" data-week-row={r.id} data-week-kind={r.kind} data-week-body={r.body} data-week-grids={r.allGrids ? "all" : r.grids.join(" ")} data-week-loads={r.largeLoad ? "1" : "0"}>
      <td className="whitespace-nowrap py-1.5 pr-3 font-mono text-xs" data-week-date={r.date}>{dayWords(r.date)}</td>
      <td className="break-words py-1.5 pr-3" data-week-status={r.status.stated ? "stated" : "class"}>
        {r.status.stated ? <span className="cursor-help" title={r.status.why}>{r.status.words}</span> : <Missing words={r.status.words} why={r.status.why} />}
      </td>
      <td className="break-words py-1.5 pr-3">
        <a href={r.link.href} title={r.link.tip} className="cursor-help" data-week-link={r.id} data-week-hover={r.link.hover}>{r.link.words}</a>
        {r.title ? <span className={`block text-xs text-muted ${r.titleWhy ? "cursor-help" : ""}`} title={r.titleWhy || undefined} data-week-title="1">{r.title}</span> : null}
      </td>
      <td className="py-1.5 pr-3 text-xs" data-week-topics={r.topics.map((t) => t.key).join(" ")}>
        {r.topics.length
          ? r.topics.map((t) => <span key={t.key} title={t.why} data-week-topic={t.key} className="mb-0.5 mr-1 inline-block cursor-help whitespace-nowrap border border-rule bg-white px-1">{topics.get(t.key)?.label ?? t.key}</span>)
          : <Missing words="none" why={r.kind === "action" ? "The written rule gives this action none of its four tags." : "The file states no topic for this row."} />}
      </td>
      <td className="py-1.5" data-week-read={r.read.line ? "model" : "none"}>
        {r.read.line
          ? <>{r.read.line} <span className="ml-1 inline-block cursor-help whitespace-nowrap border border-rule px-1 text-[10px] uppercase tracking-wide text-muted" title={r.read.why} data-week-mark="model">model&apos;s read</span></>
          : <Missing words={NO_READ} why={r.read.why} />}
      </td>
    </tr>
  );
}
function Rows({ rows, topics, caption }: { rows: WeekRow[]; topics: Map<string, Topic>; caption: string }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] table-fixed text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr className="border-b border-rule text-left text-xs text-muted">
            <th className="w-24 py-1 pr-3 font-normal">Date</th>
            <th className="w-40 py-1 pr-3 font-normal">Status</th>
            <th className="w-64 py-1 pr-3 font-normal">Agency and document</th>
            <th className="w-48 py-1 pr-3 font-normal">Topics</th>
            <th className="py-1 font-normal">What it would change</th>
          </tr>
        </thead>
        <tbody>{rows.map((r) => <Row key={r.id} r={r} topics={topics} />)}</tbody>
      </table>
    </div>
  );
}

export type WeekProps = {
  today: string; rows: WeekRow[]; bodies: Body[]; topics: Topic[]; grids: { key: string; name: string; why: string }[];
  dropped: number; droppedWhy: string; missing: { what: string; why: string }[];
  held: { actions: number; dockets: number; ruleVersion: string; docketsBuilt: string | null; docketsInFile: number };
  chosen: Chosen;
};

export function WeekView({ today, rows, bodies, topics, grids, dropped, droppedWhy, missing, held, chosen }: WeekProps) {
  const [c, setC] = useState<Chosen>(chosen);
  /** A choice changes the rows and the address together: the address always restores what is on the screen. */
  const choose = (next: Chosen) => { setC(next); window.history.replaceState(null, "", weekHref(next)); };
  const set = (part: Partial<Chosen>) => choose({ ...c, ...part });
  const byKey = new Map(topics.map((t) => [t.key, t]));
  const names = Object.fromEntries(grids.map((g) => [g.key, g.name]));
  const off = paused(c.grid);
  const shown = shownRows(rows, c, today);
  const groups = groupsOf(shown, bodies);
  const counts = countsOf(rows, c, today, bodies, topics);
  const any = c.agency || c.topic || c.grid || c.large;
  const tint = (n: number) => (n > 0 && counts.max > 0 ? `color-mix(in srgb, var(--color-accent) ${Math.round(8 + 42 * (n / counts.max))}%, white)` : "transparent");

  return (
    <div data-week="1" data-week-days={c.days} data-week-today={today} data-week-shown={shown.length} data-week-state={off ? "paused" : shown.length ? "shown" : "none"}>
      <div className="mb-4 flex flex-wrap items-center gap-x-4 gap-y-2">
        <div className="flex gap-1" role="group" aria-label="Window" data-week-window="1">
          {WINDOWS.map((d) => <Chip key={d} on={c.days === d} onClick={() => set({ days: d })} title={windowWhy(today, d)} data-week-window-choice={String(d)}>Last {d} days</Chip>)}
        </div>
        <span className="text-sm" data-week-count={shown.length}>
          {off ? null : <><span className={dotted} title={windowWhy(today, c.days)}>{shown.length} {shown.length === 1 ? "action" : "actions"}</span>{c.agency || c.topic ? <> of {counts.total}</> : null}</>}
        </span>
        {any ? <button type="button" className="cursor-pointer text-xs text-accent underline" onClick={() => choose({ ...c, agency: "", topic: "", grid: "", large: false })} data-week-clear="1">clear the filters</button> : null}
      </div>

      <div className="mb-5 space-y-1.5" data-week-filters="1">
        <Filter label="Agency" data-week-filter="agency">
          <Chip on={!c.agency} onClick={() => set({ agency: "" })} data-week-agency="">All</Chip>
          {bodies.map((b) => (
            <span key={b.key} className="inline-flex items-baseline gap-1" data-week-body-choice={b.key} data-week-refreshed={b.mark?.kind === "not refreshed" ? "0" : "1"}>
              <Chip on={c.agency === b.key} onClick={() => set({ agency: c.agency === b.key ? "" : b.key })} title={b.why} data-week-agency={b.key}>{b.label}</Chip>
              {b.mark ? <span className={`${dotted} text-[10px] italic text-muted`} title={b.mark.why} data-week-mark-refresh={b.mark.kind} data-week-mark-of={b.key}>{b.mark.words}</span> : null}
            </span>
          ))}
        </Filter>
        <Filter label="Topic" data-week-filter="topic">
          <Chip on={!c.topic} onClick={() => set({ topic: "" })} data-week-topic-choice="">All</Chip>
          {topics.length ? topics.map((t) => <Chip key={t.key} on={c.topic === t.key} onClick={() => set({ topic: c.topic === t.key ? "" : t.key })} title={t.why} data-week-topic-choice={t.key}>{t.label}</Chip>)
            : <span className="text-xs"><Missing words="not held yet" why="The tag rule and the topics of the docket rows are not in this page's files yet." /></span>}
        </Filter>
        <Filter label="Grid" data-week-filter="grid">
          <Chip on={!c.grid} onClick={() => set({ grid: "" })} data-week-grid="">All</Chip>
          {grids.length ? grids.map((g) => <Chip key={g.key} on={c.grid === g.key} onClick={() => set({ grid: c.grid === g.key ? "" : g.key })} title={paused(g.key) ? PAUSE_WHY : g.why} data-week-grid={g.key}>{g.name}</Chip>)
            : <span className="text-xs"><Missing words="not held yet" why="The file that says which grid an action is under is not in this page's files yet." /></span>}
        </Filter>
        <Filter label="Loads" data-week-filter="large">
          <Chip on={c.large} onClick={() => set({ large: !c.large })} title="Actions the written rule tags large loads, and the proceedings and orders of the large-load tables." data-week-large={c.large ? "1" : "0"}>Large loads only</Chip>
        </Filter>
      </div>

      {off ? (
        <p className="text-sm" data-week-paused="1"><Missing words={PAUSED_WORDS} why={PAUSE_WHY} /></p>
      ) : (
        <>
          <div className="mb-6" data-week-chart-frame="1">
            <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2 text-xs text-muted">
              <span>Actions by agency and topic, last {c.days} days</span>
              <span className={dotted} title="A count is the actions of that agency on that topic, for the window, the grid and the large-load choice above. An action with two topics counts under each. Darker is more. A click on a count lists those actions." data-hint="1">how to read</span>
            </div>
            {counts.lines.length ? (
              <Hover>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[820px] border-collapse text-xs" data-chart="week" data-week-chart-total={counts.total}>
                    <caption className="sr-only">Counts of actions by agency and topic, last {c.days} days</caption>
                    <thead>
                      <tr>
                        <th className="w-36 py-1 pr-2 text-left font-normal text-muted">Agency</th>
                        {topics.map((t) => (
                          <th key={t.key} className="px-1.5 py-1 align-bottom font-normal">
                            <button type="button" aria-pressed={c.topic === t.key} onClick={() => set({ topic: c.topic === t.key ? "" : t.key })} data-tip={`${t.label}: ${t.why}`} data-week-col={t.key}
                              className={`w-full cursor-pointer leading-tight ${c.topic === t.key ? "font-semibold text-accent" : "text-muted hover:text-accent"}`}>{t.label}</button>
                          </th>
                        ))}
                        <th className="px-1.5 py-1 align-bottom font-normal text-muted"><span data-tip="Actions with none of the eight topics.">No topic</span></th>
                        <th className="px-1.5 py-1 align-bottom font-normal text-muted">All</th>
                      </tr>
                    </thead>
                    <tbody>
                      {counts.lines.map((l) => (
                        <tr key={l.body.key} className="border-t border-rule" data-week-line={l.body.key}>
                          <th scope="row" className="py-1 pr-2 text-left font-normal">
                            <button type="button" aria-pressed={c.agency === l.body.key} onClick={() => set({ agency: c.agency === l.body.key ? "" : l.body.key })} data-tip={l.body.name}
                              className={`cursor-pointer text-left ${c.agency === l.body.key ? "font-semibold text-accent" : "text-ink hover:text-accent"}`}>{l.body.label}</button>
                          </th>
                          {topics.map((t, i) => {
                            const n = l.byTopic[i], on = c.agency === l.body.key && c.topic === t.key;
                            return (
                              <td key={t.key} className="p-0.5 text-center">
                                {n > 0 ? (
                                  <button type="button" aria-pressed={on} onClick={() => set(on ? { agency: "", topic: "" } : { agency: l.body.key, topic: t.key })} data-tip={cellTip(l, t, n, c.days)} data-week-cell={`${l.body.key}|${t.key}`} data-n={n}
                                    className={`block w-full cursor-pointer py-1 font-mono text-ink ${on ? "outline outline-2 outline-ink" : "hover:outline hover:outline-1 hover:outline-ink"}`} style={{ background: tint(n) }}>{n}</button>
                                ) : <span className="block py-1 font-mono text-muted opacity-40" data-tip={cellTip(l, t, 0, c.days)} data-week-cell={`${l.body.key}|${t.key}`} data-n="0">0</span>}
                              </td>
                            );
                          })}
                          <td className="p-0.5 text-center"><span className="block py-1 font-mono text-muted" data-tip={`${l.body.label}: ${l.none} with none of the eight topics in the last ${c.days} days`} data-week-cell={`${l.body.key}|`} data-n={l.none}>{l.none}</span></td>
                          <td className="p-0.5 text-center">
                            <button type="button" aria-pressed={c.agency === l.body.key && !c.topic} onClick={() => set({ agency: l.body.key, topic: "" })} data-tip={cellTip(l, null, l.total, c.days)} data-week-total={l.body.key} data-n={l.total}
                              className="block w-full cursor-pointer py-1 font-mono font-semibold text-ink hover:outline hover:outline-1 hover:outline-ink">{l.total}</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Hover>
            ) : <p className="text-sm" data-week-chart-empty="1"><Missing words={NONE_WORDS} why={emptyWhy({ ...c, agency: "", topic: "" }, today, bodies, topics, names)} /></p>}
          </div>

          {groups.length ? groups.map((g) => (
            <div key={g.body.key} className="mb-6" data-week-group={g.body.key} data-week-group-count={g.rows.length}>
              <h3 className="mb-1 font-serif text-lg text-accent"><span title={g.body.why} className="cursor-help">{g.body.name}</span> <span className="font-sans text-xs text-muted">{g.rows.length}</span></h3>
              <Rows rows={g.rows.slice(0, SHOWN)} topics={byKey} caption={`${g.body.name}: actions of the last ${c.days} days`} />
              {g.rows.length > SHOWN ? (
                <details className="border-b border-rule py-1.5" data-week-fold={g.body.key}>
                  <summary className="cursor-pointer text-sm text-accent">{g.rows.length - SHOWN} earlier</summary>
                  <div className="pt-2"><Rows rows={g.rows.slice(SHOWN)} topics={byKey} caption={`${g.body.name}: actions of the last ${c.days} days, earlier`} /></div>
                </details>
              ) : null}
            </div>
          )) : <p className="text-sm" data-week-empty="1"><Missing words={NONE_WORDS} why={emptyWhy(c, today, bodies, topics, names)} /></p>}
        </>
      )}

      <p className="mt-4 text-xs text-muted" data-week-foot="1">
        <span className={dotted} title={`Read for this page: ${held.actions} actions of the live table policy_actions and ${held.dockets} proceedings and orders of the site's file of dockets, all dated in the thirty days to ${dayWords(today) ?? today}.`}>{held.actions + held.dockets} held for thirty days</span>
        {held.docketsBuilt ? <>; <span className={dotted} title={`The file of proceedings and orders of FERC and the state commissions was built on ${dayWords(held.docketsBuilt) ?? held.docketsBuilt}; it holds ${held.docketsInFile} rows of every date.`}>dockets held {dayWords(held.docketsBuilt) ?? held.docketsBuilt}</span></> : null}
        {held.ruleVersion ? <>; <span className={dotted} title="The topics of an action are tags given by a written rule that code applies to its title, its summary and the first paragraph of its printed text. No model tags a row.">tag rule version {held.ruleVersion}</span></> : null}
        {dropped ? <>; <span data-week-dropped={dropped}><Missing words={`${dropped} held, not shown`} why={droppedWhy} /></span></> : null}
        {missing.map((m) => <span key={m.what} data-week-missing={m.what}>; {m.what}: <Missing words="not held yet" why={m.why} /></span>)}
      </p>
    </div>
  );
}
