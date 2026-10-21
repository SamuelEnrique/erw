import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { render } from "@/lib/markdown";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";
import { lineUrl, WAITS, type Ledger, type LedgerGroup, type WaitReport } from "@/lib/waits";

// Session 188: what waits for Samuel (docs/machines.md, "Continuous work"). Every session report after the last one
// he answered, newest first: the rulings it leaves for him, each in the report's own words with the line it stands on,
// and a link to the report on GitHub. Read from the repository when the site is built (scripts/build-waits.mjs writes
// content/waits.json from archive/sessions/); nothing here is written by a model and nothing is reworded.
// Internal: no nav link, not indexed, never cached (next.config.ts gives every /internal address those headers), and
// behind the internal view exactly as /internal/findings is: the page answers 404 unless the browser holds the
// internal cookie (set by the form at /internal/open). It takes no token in its address. It reads no database and
// writes nothing: "the last one he answered" is a file in the repository that a person edits.
export const dynamic = "force-dynamic";

/** The page's name is sent only to the internal view: a visitor's 404 carries none of this page's words. */
export async function generateMetadata(): Promise<Metadata> {
  const inside = (process.env.INTERNAL_COSTS_TOKEN ?? "").length >= 24 && (await internalOk((await cookies()).get(COOKIE)?.value));
  return { ...(inside ? { title: "Waits for Samuel (internal)" } : {}), robots: { index: false, follow: false } };
}

const plural = (n: number, one: string, many: string) => `${n.toLocaleString("en-US")} ${n === 1 ? one : many}`;

function Item({ r, md, line, section }: { r: WaitReport; md: string; line: number; section: string }) {
  return (
    <li className="border-t border-rule py-3" data-wait-line={line}>
      <div className="prose-erw text-sm" style={{ overflowWrap: "anywhere" }} dangerouslySetInnerHTML={{ __html: render(md, r.path) }} />
      <p className="text-xs text-muted">
        Under &quot;{section}&quot;, <a className="underline" href={lineUrl(r, line)} rel="noreferrer">line {line}</a>
      </p>
    </li>
  );
}

function Report({ r }: { r: WaitReport }) {
  return (
    <section className="mb-10" data-wait-report={r.id} data-waits={r.waits.length}>
      <div className="mb-1 border-b border-rule pb-1">
        <h2 className="text-xl">Session {r.id}: {r.title}</h2>
      </div>
      <p className="text-xs text-muted">
        {r.date_words ?? "No date is written in the report"}, {plural(r.waits.length, "item waits", "items wait")},{" "}
        <a className="underline" href={r.url} rel="noreferrer" data-wait-link="1">the report on GitHub</a>
      </p>
      <ul className="mt-2">
        {r.waits.map((w) => <Item key={`w${w.line}`} r={r} md={w.md} line={w.line} section={w.section} />)}
      </ul>
      {r.decided.length > 0 ? (
        <details className="mt-2 border-t border-rule pt-2 text-sm" data-decided={r.decided.length}>
          <summary className="cursor-pointer text-muted">Decided without you in this session: {r.decided.length} (they do not wait; open to read them)</summary>
          <ul>
            {r.decided.map((d) => <Item key={`d${d.line}`} r={r} md={d.md} line={d.line} section={d.section} />)}
          </ul>
        </details>
      ) : null}
    </section>
  );
}

// Session 414: the ledger of one run of sessions, at the top of the page. Every item of a section for you listed once
// (an item a later report asks again is merged with it and keeps each report's link), under what it blocks, with the
// three the state notes rank highest by value first. The rules are fixed and in scripts/build-waits.mjs; each item says
// which rule placed it, why items were merged and where the notes rank it, so a person can read why and overrule it.
const NOTE_ORDER: Record<string, string> = { true: "the note ranks by value", false: "the note's list is numbered, not said to be by value" };

function Sep({ i }: { i: number }) {
  return i > 0 ? <>, </> : null;
}

function LedgerItem({ g, label }: { g: LedgerGroup; label: string }) {
  const many = g.asked.length > 1 || g.restated.length > 0;
  return (
    <li className="border-t border-rule py-3" data-ledger-item={g.id} data-block={g.block} data-sessions={g.sessions.join(" ")} data-first={g.first ? g.first.place : undefined}>
      {g.first ? (
        <p className="mb-1 text-xs font-semibold">
          {g.first.place} of the first three: item {g.first.rank} of{" "}
          <a className="underline" href={g.first.url} rel="noreferrer">{g.first.note}</a>, &quot;{g.first.heading}&quot;
        </p>
      ) : null}
      <div className="prose-erw text-sm" style={{ overflowWrap: "anywhere" }} dangerouslySetInnerHTML={{ __html: render(g.md, g.path) }} />
      <p className="text-xs text-muted" data-ledger-asked={g.asked.length}>
        Asked in{" "}
        {g.asked.map((a, i) => (
          <span key={`a${a.session}-${a.line}`}><Sep i={i} /><a className="underline" href={a.url} rel="noreferrer">session {a.session}, line {a.line}</a></span>
        ))}
        {g.restated.length > 0 ? (
          <>
            ; restated with another item in{" "}
            {g.restated.map((a, i) => (
              <span key={`r${a.session}-${a.line}`}><Sep i={i} /><a className="underline" href={a.url} rel="noreferrer">session {a.session}, line {a.line}</a></span>
            ))}
          </>
        ) : null}
        .{g.asked.length > 1 ? ` The words shown are session ${g.session}'s, the newest.` : ""}
      </p>
      <p className="text-xs text-muted" data-ledger-why={g.block_rule}>
        Under &quot;{label}&quot;: {g.block_said ? <>it says &quot;{g.block_said}&quot; (rule {g.block_rule}).</> : <>no rule of the four matched its words (rule {g.block_rule}).</>}{" "}
        {g.ranks.length > 0 ? (
          <>
            In the notes:{" "}
            {g.ranks.map((r, i) => (
              <span key={`n${r.note}-${r.rank}-${i}`}><Sep i={i} />item {r.rank} of <a className="underline" href={r.url} rel="noreferrer">{r.note}</a> ({NOTE_ORDER[`${r.by_value}`]}{r.best ? "" : "; that item speaks of another first"})</span>
            ))}
            .
          </>
        ) : (
          <>No note ranks it.</>
        )}
      </p>
      {many ? (
        <details className="mt-1 text-xs" data-ledger-merged={g.asked.length + g.restated.length}>
          <summary className="cursor-pointer text-muted">Why these are one item, and each report&apos;s own words</summary>
          <ul className="mt-1">
            {g.reasons.map((w, i) => <li key={`w${i}`} className="text-muted">{w}.</li>)}
          </ul>
          {[...g.asked, ...g.restated].map((a) => (
            <div key={`m${a.session}-${a.line}`} className="mt-2 border-t border-rule pt-1">
              <p className="text-muted">Session {a.session}, under &quot;{a.section}&quot;, <a className="underline" href={a.url} rel="noreferrer">line {a.line}</a>:</p>
              <div className="prose-erw text-sm" style={{ overflowWrap: "anywhere" }} dangerouslySetInnerHTML={{ __html: render(a.md, a.path) }} />
            </div>
          ))}
        </details>
      ) : null}
    </li>
  );
}

function LedgerSection({ L }: { L: Ledger | undefined }) {
  if (!L) return null;
  if (L.error || !L.counts || !L.groups || !L.blocks || !L.rules) {
    return (
      <section className="mb-10 border border-rule bg-panel p-3 text-sm" data-ledger="error">
        <h2 className="mb-1 text-xl">Sessions {L.from} to {L.to}: each ruling once</h2>
        <p>{L.error ?? "The ledger was not written when the site was built."} The reports are listed one by one below.</p>
      </section>
    );
  }
  const c = L.counts;
  const blocks = L.blocks;
  const rules = L.rules;
  const groups = L.groups;
  const label = (k: string) => blocks.find((b) => b.key === k)?.label ?? k;
  const first = groups.filter((g) => g.first).sort((a, b) => (a.first?.place ?? 0) - (b.first?.place ?? 0));
  const rankedNote = L.notes_read?.find((n) => n.lists.some((l) => l.by_value));
  const quiet = L.quiet ?? [];
  const silent = L.silent ?? [];
  return (
    <section className="mb-12" data-ledger="1" data-ledger-from={L.from} data-ledger-to={L.to}>
      <h2 className="mb-1 text-xl">Sessions {L.from} to {L.to}: each ruling once</h2>
      <p className="mb-3 text-sm text-muted">
        Every item of a section for your ruling in these reports, listed once: where a later report asks the same thing again, the two are one item
        with a link to each. Placed under what it blocks, by fixed rules that each item names. The reports are listed one by one further down.
      </p>
      <div className="mb-3 grid grid-cols-3 gap-px border border-rule bg-rule">
        <div className="bg-panel p-3"><div className="text-xs text-muted">Items waiting</div><div className="text-2xl tabular-nums" data-ln="items">{c.items}</div></div>
        <div className="bg-panel p-3"><div className="text-xs text-muted">Lines in the reports</div><div className="text-2xl tabular-nums" data-ln="lines">{c.lines}</div><div className="text-xs text-muted">{c.merged} merged</div></div>
        <div className="bg-panel p-3"><div className="text-xs text-muted">Reports read</div><div className="text-2xl tabular-nums" data-ln="reports">{c.reports}</div><div className="text-xs text-muted">of {L.to - L.from + 1} sessions</div></div>
      </div>
      <p className="mb-2 text-sm" data-ln-blocks="1">
        {blocks.map((b, i) => (
          <span key={b.key}><Sep i={i} />{b.label}: <span className="tabular-nums" data-ln-block={b.key}>{c.by_block[b.key] ?? 0}</span></span>
        ))}
        .
      </p>
      <p className="mb-6 text-xs text-muted" data-ln-held={L.held?.length ?? 0}>
        Read when the site was built: the reports of sessions {L.held_words || "none"}.{" "}
        {L.missing ? <>Not yet in <span className="font-mono">archive/sessions/</span>: {L.missing}; a report that lands joins this list at the next build.</> : <>Every session of the run has its report.</>}
        {L.answered_to ? <> Reports up to session {L.answered_to} are marked answered and are not read.</> : null}
      </p>

      <h3 className="mb-1 text-lg">First: the three the notes rank highest</h3>
      {first.length === 0 ? (
        <p className="mb-6 text-sm" data-ledger-first="0">
          No note under <span className="font-mono">docs/state/</span> ranks these items by value, so none is put first: this page does not make a rank up.
        </p>
      ) : (
        <>
          <p className="mb-1 text-xs text-muted" data-ledger-first={first.length}>
            Taken from the notes that say their list is ranked by value, newest first{rankedNote ? <> (the newest is <a className="underline" href={rankedNote.url} rel="noreferrer">{rankedNote.file}</a>)</> : null}, in
            each note&apos;s own order, each item once.{first.length < 3 ? ` Only ${first.length}: no other item of this run is ranked by a note that says its order is by value.` : ""}
          </p>
          <ul className="mb-6">{first.map((g) => <LedgerItem key={g.id} g={g} label={label(g.block)} />)}</ul>
        </>
      )}

      {blocks.map((b) => {
        const rest = groups.filter((g) => g.block === b.key && !g.first);
        const above = (c.by_block[b.key] ?? 0) - rest.length;
        return (
          <div key={b.key} className="mb-6" data-ledger-block={b.key}>
            <h3 className="text-lg">{b.label} ({c.by_block[b.key] ?? 0}{above > 0 ? `, of which ${above} above` : ""})</h3>
            <p className="text-xs text-muted">{b.says}.</p>
            {rest.length === 0 ? <p className="mt-1 text-sm">Nothing {above > 0 ? "more " : ""}under this heading.</p> : <ul className="mt-1">{rest.map((g) => <LedgerItem key={g.id} g={g} label={b.label} />)}</ul>}
          </div>
        );
      })}

      {quiet.length + silent.length > 0 ? (
        <p className="mb-4 text-xs text-muted" data-ledger-quiet={quiet.length + silent.length}>
          Not listed:{" "}
          {quiet.map((q, i) => (
            <span key={`q${q.session}`}><Sep i={i} /><a className="underline" href={`${q.url}?plain=1#L${q.lines[0].line}`} rel="noreferrer">session {q.session}</a> ({q.lines.map((x) => x.why).filter((x, k, a) => a.indexOf(x) === k).join("; ")})</span>
          ))}
          {silent.length > 0 ? (
            <>
              {quiet.length > 0 ? "; and, with no section for your ruling, " : "with no section for your ruling, "}
              {silent.map((s, i) => <span key={`s${s.session}`}><Sep i={i} /><a className="underline" href={s.url} rel="noreferrer">session {s.session}</a></span>)}
            </>
          ) : null}
          .
        </p>
      ) : null}

      <details className="text-xs" data-ledger-rules="1">
        <summary className="cursor-pointer text-muted">The rules, as the build applied them</summary>
        <div className="mt-2 space-y-2 text-muted" style={{ overflowWrap: "anywhere" }}>
          <p>
            <strong>What is read.</strong> Every item of a section headed for you (&quot;For Samuel&apos;s ruling&quot; and the like) in the reports of sessions {L.from} to {L.to}.
            An item that says there is nothing new is not listed, nor one that only sends the reader to another list (<span className="font-mono">{rules.pointer}</span>).
          </p>
          <p>
            <strong>One item, not two.</strong> Two items of different reports are one when they match one subject (
            {rules.subjects.map((s, i) => <span key={s.label}><Sep i={i} />{s.label}: <span className="font-mono">{s.re}</span></span>)}); or when one names the
            other&apos;s session and they share at least {rules.named.words} words, {Math.round(rules.named.share * 100)} percent of the shorter&apos;s; or when they share
            at least {rules.same.words} words, {Math.round(rules.same.share * 100)} percent of the shorter&apos;s. Words are compared without case, markup, short and common
            words, or a plural&apos;s s. An item that matches two items of another report restates both: it is kept beside each, and they stay two.
          </p>
          <p><strong>What it blocks.</strong> The first of these rules that the item&apos;s words match places it (the words of every merged report are read):</p>
          <ol className="list-decimal pl-5">
            {rules.block.map((r) => <li key={r.n}>{label(r.block)}: <span className="font-mono">{r.re}</span></li>)}
          </ol>
          <p>
            <strong>The rank.</strong> The notes of <span className="font-mono">docs/state/</span> written since the run began, with a list headed &quot;Waiting for you&quot; or
            &quot;What waits for Samuel&quot;. A list ranks by value only when its heading or its first line says so (<span className="font-mono">{rules.by_value}</span>); a
            numbered list that does not is shown beside each item and puts nothing first. A note&apos;s item speaks of a ledger item when they match one subject, or
            it names the item&apos;s session and they share {rules.note.named} words, or they share {rules.note.words} words, {Math.round(rules.note.share * 100)} percent
            of the shorter&apos;s. Notes read:{" "}
            {(L.notes_read ?? []).map((n, i) => (
              <span key={n.file}><Sep i={i} /><a className="underline" href={n.url} rel="noreferrer">{n.file}</a> ({n.lists.map((l) => `"${l.heading}", ${l.items} items${l.by_value ? ", by value" : ""}`).join("; ")})</span>
            ))}
            .
          </p>
          <p>These are words read by fixed rules: an item can be placed or merged wrongly. The report is the record.</p>
        </div>
      </details>
    </section>
  );
}

export default async function WaitsPage() {
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();

  const w = WAITS;
  const built = `${w.built_at.slice(0, 10)} ${w.built_at.slice(11, 16)} UTC`;
  if (w.unread) {
    return (
      <Brand noUsage>
      <div data-waits="unread">
        <h1 className="mb-2 text-3xl">Waits for Samuel (internal)</h1>
        <p className="text-sm">The session reports could not be read when the site was built ({built}): {w.unread}. Nothing is listed, and nothing is known to wait or not to wait.</p>
      </div>
      </Brand>
    );
  }
  const m = w.marker;
  return (
    <Brand noUsage>
    <div className="max-w-3xl" data-waits="1" data-no-usage>
      <h1 className="mb-1 text-3xl">Waits for Samuel (internal)</h1>
      <p className="mb-3 text-sm text-muted">
        What the session reports leave for your ruling, newest first, each in the report&apos;s own words. A report with nothing waiting is not
        listed. Read from the repository when the site was built, {built}.
      </p>
      <LedgerSection L={w.ledger} />
      <h2 className="mb-2 text-xl">Report by report</h2>
      {m.error ? (
        <p className="mb-5 border border-rule bg-panel p-2 text-sm" role="status" data-marker="unread">
          The file <span className="font-mono">{m.path}</span> could not be read ({m.error}), so every report is listed. It holds two lines:{" "}
          <span className="font-mono">last_answered: 186</span> and <span className="font-mono">on: 2026-10-11</span>.
        </p>
      ) : (
        <p className="mb-5 border border-rule bg-panel p-2 text-sm" data-marker={m.last ?? ""}>
          Listed: the reports after session {m.last}, the last one marked as answered{m.on ? ` (on ${m.on})` : ""}. When you have answered a
          report, write its number on the line <span className="font-mono">last_answered:</span> of the file{" "}
          <a className="underline" href={`${w.repo}/blob/main/${m.path}`} rel="noreferrer"><span className="font-mono">{m.path}</span></a>, commit
          and push: this page is rebuilt with the site, and that report and every one before it leave the list.
        </p>
      )}
      <div className="mb-8 grid grid-cols-3 gap-px border border-rule bg-rule">
        <div className="bg-panel p-3"><div className="text-xs text-muted">Reports since</div><div className="text-2xl tabular-nums" data-n="after">{w.counts.after}</div></div>
        <div className="bg-panel p-3"><div className="text-xs text-muted">With something waiting</div><div className="text-2xl tabular-nums" data-n="listed">{w.counts.listed}</div></div>
        <div className="bg-panel p-3"><div className="text-xs text-muted">Items waiting</div><div className="text-2xl tabular-nums" data-n="items">{w.counts.items}</div></div>
      </div>
      {w.reports.length === 0 ? <p className="mb-8 text-sm" data-waits-none="1">Nothing waits in the reports after session {m.last ?? "the first"}.</p> : null}
      {w.reports.map((r) => <Report key={r.id} r={r} />)}
      {w.decided_only.length > 0 ? (
        <p className="mb-8 text-xs text-muted" data-decided-only={w.decided_only.length}>
          Not listed, because nothing in them waits (each holds decisions made without you, which you may overrule):{" "}
          {w.decided_only.map((d, i) => (
            <span key={d.id}>{i > 0 ? ", " : ""}<a className="underline" href={d.url} rel="noreferrer">session {d.id}</a> ({d.count})</span>
          ))}.
        </p>
      ) : null}
      <p className="text-xs text-muted">
        An item is listed when its section is headed for you (&quot;For Samuel&apos;s ruling&quot;, &quot;To finish (Samuel)&quot;, &quot;Open questions&quot; and the
        like) or when the item says so itself (&quot;your ruling&quot;, &quot;your approval&quot;, &quot;Rule on ...&quot;). The rule is in{" "}
        <span className="font-mono">site/scripts/build-waits.mjs</span>; it reads words, so it can list a line that no longer waits and miss one
        worded another way. The report is the record.
      </p>
    </div>
    </Brand>
  );
}
