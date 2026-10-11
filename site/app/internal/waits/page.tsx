import type { Metadata } from "next";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { render } from "@/lib/markdown";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";
import { lineUrl, WAITS, type WaitReport } from "@/lib/waits";

// Session 188: what waits for Samuel (docs/machines.md, "Continuous work"). Every session report after the last one
// he answered, newest first: the rulings it leaves for him, each in the report's own words with the line it stands on,
// and a link to the report on GitHub. Read from the repository when the site is built (scripts/build-waits.mjs writes
// content/waits.json from archive/sessions/); nothing here is written by a model and nothing is reworded.
// Internal: no nav link, not indexed, never cached (next.config.ts gives every /internal address those headers), and
// behind the internal view exactly as /internal/findings is: the page answers 404 unless the browser holds the
// internal cookie (set by the form at /internal/open). It takes no token in its address. It reads no database and
// writes nothing: "the last one he answered" is a file in the repository that a person edits.
export const metadata: Metadata = { title: "Waits for Samuel (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

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

export default async function WaitsPage() {
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();

  const w = WAITS;
  const built = `${w.built_at.slice(0, 10)} ${w.built_at.slice(11, 16)} UTC`;
  if (w.unread) {
    return (
      <div data-waits="unread">
        <h1 className="mb-2 text-3xl">Waits for Samuel (internal)</h1>
        <p className="text-sm">The session reports could not be read when the site was built ({built}): {w.unread}. Nothing is listed, and nothing is known to wait or not to wait.</p>
      </div>
    );
  }
  const m = w.marker;
  return (
    <div className="max-w-3xl" data-waits="1" data-no-usage>
      <h1 className="mb-1 text-3xl">Waits for Samuel (internal)</h1>
      <p className="mb-3 text-sm text-muted">
        What the session reports leave for your ruling, newest first, each in the report&apos;s own words. A report with nothing waiting is not
        listed. Read from the repository when the site was built, {built}.
      </p>
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
  );
}
