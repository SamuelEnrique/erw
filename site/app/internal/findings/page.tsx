import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { DraftReview } from "@/components/analysis/DraftReview";
import { FindingCard } from "@/components/analysis/FindingCard";
import { Section } from "@/components/Section";
import { VERDICTS, VERDICT_DOC } from "@/lib/findingverdicts";
import { COOKIE } from "@/lib/release";
import { listDrafts, STATE_WORDS, type Draft } from "@/lib/scanner";
import { internalOk } from "@/lib/thesis/server";

// Session 181: the scanner's review list (docs/methods/automated_analysis_scanner.md). Internal: no nav link, not
// indexed, never cached, and behind the internal view as /internal/usage is, with one difference: this page takes no
// token in its address. It answers 404 unless the browser holds the internal cookie (set by the form at
// /internal/open), and the database answers nothing unless the server's token equals the secret (scanner_drafts_list,
// migration 029). Each draft is a flag the scanner raised and the card computed for it by code: nothing here was
// written by a model, and nothing here is on /research until it is approved.
export const metadata: Metadata = { title: "Scanner drafts (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const day = (iso: string) => iso.slice(0, 10);

function fullCardWords(d: Draft): string {
  const f = d.card.scanner?.full_card;
  return f ? `queues the impact study on this series around ${d.flag_date} (window ${f.params.window} days, control ${String(f.params.control).replace(/_/g, " ")}), computed on the data machine`
    : "this series is not one the impact study knows, so the draft is marked and waits for a session to write the card";
}

// Session 233: what the weekly hunt prepared with a draft: its three tests, its files (the CSV, the Stata do-file, the
// Python mirror, the two LinkedIn pictures) and the caption computed from its numbers. Nothing here is posted anywhere:
// the files are downloaded by the person who rules on the draft, from /internal/findings/file (internal view only).
function HuntFiles({ id, hunt }: { id: string; hunt: NonNullable<Draft["card"]["hunt"]> }) {
  const href = (name: string, show = false) => `/internal/findings/file?id=${encodeURIComponent(id)}&name=${encodeURIComponent(name)}${show ? "&show=1" : ""}`;
  const label = (name: string) => name.endsWith(".csv") ? "data (CSV)" : name.endsWith(".do") ? "Stata do-file" : name.endsWith(".py") ? "Python mirror"
    : name.endsWith("_1200x627.png") ? "LinkedIn picture, 1200 x 627" : name.endsWith("_1080x1080.png") ? "LinkedIn picture, 1080 x 1080" : name.endsWith("_caption.txt") ? "caption (text)" : name;
  const pictures = hunt.files.filter((f) => f.endsWith(".png"));
  return (
    <div className="mt-3 border-t border-rule pt-3 text-sm" data-hunt-files={id}>
      <p className="text-xs text-muted">Pattern <span className="font-mono">{hunt.pattern}</span>, region {hunt.region_words}. Why it was drafted: {hunt.why}.</p>
      <ul className="mt-1 list-disc pl-5 text-xs" data-hunt-tests={hunt.tests.length}>
        {hunt.tests.map((t) => <li key={t.name}>{t.passed ? "Passed" : "Failed"}: {t.name}. {t.words}.</li>)}
      </ul>
      <p className="mt-2 flex flex-wrap items-center gap-3 text-xs" data-hunt-downloads={hunt.files.length}>
        <span className="text-muted">Files:</span>
        {hunt.files.map((f) => <a key={f} href={href(f)} download={f} data-hunt-file={f}>{label(f)}</a>)}
      </p>
      <div className="mt-2 flex flex-wrap gap-3">
        {pictures.map((f) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img key={f} src={href(f, true)} alt={label(f)} loading="lazy" className="max-h-56 w-auto border border-rule" data-hunt-picture={f} />
        ))}
      </div>
      <p className="mt-2 text-xs text-muted">Caption draft, computed from the numbers; nothing is posted by this page:</p>
      <pre className="mt-1 whitespace-pre-wrap border border-rule bg-panel p-2 text-xs" data-hunt-caption={id}>{hunt.caption}</pre>
    </div>
  );
}

// Session 267: the verdict of 13 October 2026 beside each draft, as the verification wrote it (site/lib/findingverdicts.ts).
// Words only: it rules on nothing, and a draft raised after that evening reads "no verdict".
function VerdictLine({ id }: { id: string }) {
  const v = VERDICTS[id];
  if (!v) return <p className="mb-2 text-xs text-muted" data-draft-verdict="none">Verdict of 13 October 2026: no verdict (raised after the verification).</p>;
  return (
    <p className="mb-2 text-xs" data-draft-verdict={v.verdict}>
      <span className="text-muted">Verdict of 13 October 2026 (session {v.by}{v.by === "251" ? ", by session 252's rule" : ""}; block {v.block} of <span className="font-mono">{VERDICT_DOC}</span>): </span>
      <strong>{v.verdict}</strong>. {v.reason}
    </p>
  );
}

function DraftBlock({ d }: { d: Draft }) {
  return (
    <div className="border border-rule p-3" data-draft-id={d.id} data-draft-rule={d.rule} data-draft-strength={d.strength} data-draft-verdict-of={VERDICTS[d.id]?.verdict ?? "none"}>
      <p className="mb-2 text-xs text-muted">
        Raised {day(d.raised_at)} by {d.rule === "hunt" ? "the weekly hunt" : "scanner"} {d.scanner_version}; rule {d.rule}; strength {d.strength.toLocaleString("en-US", { maximumFractionDigits: 2 })}; table{" "}
        <span className="font-mono">{d.table_name}</span>; flagged {d.flag_date}
      </p>
      <VerdictLine id={d.id} />
      <FindingCard card={d.card} roundup={false} />
      {d.card.hunt ? <HuntFiles id={d.id} hunt={d.card.hunt} /> : null}
      <DraftReview id={d.id} state={d.state} history={d.state_history ?? []} requestId={d.request_id} fullCard={fullCardWords(d)} />
    </div>
  );
}

export default async function FindingsReviewPage() {
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();

  let drafts: Draft[];
  try {
    drafts = await listDrafts();
  } catch (e) {
    return (
      <Brand>
      <div data-drafts="unread">
        <h1 className="mb-2 text-3xl">Scanner drafts (internal)</h1>
        <p className="text-sm">The review list could not be read: {(e as Error).message.slice(0, 160)}. Until migration 029 is applied there is no list.</p>
      </div>
      </Brand>
    );
  }
  const open = drafts.filter((d) => d.state === "draft" || d.state === "full_card_asked");
  const ruled = drafts.filter((d) => d.state === "approved" || d.state === "dismissed");
  const count = (s: Draft["state"]) => drafts.filter((d) => d.state === s).length;
  return (
    <Brand>
    <div data-drafts={drafts.length}>
      <h1 className="mb-1 text-3xl">Scanner drafts (internal)</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        What the daily scanner flagged, newest and strongest first. Each draft is a chart, callouts and a method footnote computed by code from the
        flag: no paragraph, no model. Approve puts the card on /research, marked as the scanner&apos;s; Dismiss keeps it off for good; Ask for a
        full card queues an analysis or marks the draft for a session. Every ruling is kept with its time.
      </p>
      <div className="mb-8 grid grid-cols-2 gap-px border border-rule bg-rule sm:grid-cols-4">
        {(["draft", "full_card_asked", "approved", "dismissed"] as const).map((s) => (
          <div key={s} className="bg-panel p-3"><div className="text-xs text-muted">{STATE_WORDS[s]}</div><div className="text-2xl tabular-nums" data-n={s}>{count(s)}</div></div>
        ))}
      </div>
      <Section title="Waiting for a ruling" aside={`${open.length}`}>
        {open.length === 0 ? <p className="text-sm text-muted" data-open-drafts="0">No draft waits.</p> : (
          <div className="flex flex-col gap-8" data-open-drafts={open.length}>{open.map((d) => <DraftBlock key={d.id} d={d} />)}</div>
        )}
      </Section>
      <Section title="Ruled" aside={`${ruled.length}`}>
        {ruled.length === 0 ? <p className="text-sm text-muted" data-ruled-drafts="0">Nothing has been ruled on yet.</p> : (
          <div className="flex flex-col gap-8" data-ruled-drafts={ruled.length}>{ruled.map((d) => <DraftBlock key={d.id} d={d} />)}</div>
        )}
      </Section>
    </div>
    </Brand>
  );
}
