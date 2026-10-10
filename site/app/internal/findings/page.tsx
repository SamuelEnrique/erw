import type { Metadata } from "next";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { DraftReview } from "@/components/analysis/DraftReview";
import { FindingCard } from "@/components/analysis/FindingCard";
import { Section } from "@/components/Section";
import { COOKIE } from "@/lib/release";
import { listDrafts, STATE_WORDS, type Draft } from "@/lib/scanner";
import { internalOk } from "@/lib/thesis/server";

// Session 181: the scanner's review list (docs/methods/automated_analysis_scanner.md). Internal: no nav link, not
// indexed, never cached, and behind the internal view as /internal/usage is, with one difference: this page takes no
// token in its address. It answers 404 unless the browser holds the internal cookie (set by the form at
// /internal/open), and the database answers nothing unless the server's token equals the secret (scanner_drafts_list,
// migration 029). Each draft is a flag the scanner raised and the card computed for it by code: nothing here was
// written by a model, and nothing here is on /analysis until it is approved.
export const metadata: Metadata = { title: "Scanner drafts (internal)", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const day = (iso: string) => iso.slice(0, 10);

function fullCardWords(d: Draft): string {
  const f = d.card.scanner?.full_card;
  return f ? `queues the impact study on this series around ${d.flag_date} (window ${f.params.window} days, control ${String(f.params.control).replace(/_/g, " ")}), computed on the data machine`
    : "this series is not one the impact study knows, so the draft is marked and waits for a session to write the card";
}

function DraftBlock({ d }: { d: Draft }) {
  return (
    <div className="border border-rule p-3" data-draft-id={d.id} data-draft-rule={d.rule} data-draft-strength={d.strength}>
      <p className="mb-2 text-xs text-muted">
        Raised {day(d.raised_at)} by scanner {d.scanner_version}; rule {d.rule}; strength {d.strength.toLocaleString("en-US", { maximumFractionDigits: 2 })}; table{" "}
        <span className="font-mono">{d.table_name}</span>; flagged {d.flag_date}
      </p>
      <FindingCard card={d.card} roundup={false} />
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
      <div data-drafts="unread">
        <h1 className="mb-2 text-3xl">Scanner drafts (internal)</h1>
        <p className="text-sm">The review list could not be read: {(e as Error).message.slice(0, 160)}. Until migration 029 is applied there is no list.</p>
      </div>
    );
  }
  const open = drafts.filter((d) => d.state === "draft" || d.state === "full_card_asked");
  const ruled = drafts.filter((d) => d.state === "approved" || d.state === "dismissed");
  const count = (s: Draft["state"]) => drafts.filter((d) => d.state === s).length;
  return (
    <div data-drafts={drafts.length}>
      <h1 className="mb-1 text-3xl">Scanner drafts (internal)</h1>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        What the daily scanner flagged, newest and strongest first. Each draft is a chart, callouts and a method footnote computed by code from the
        flag: no paragraph, no model. Approve puts the card on /analysis, marked as the scanner&apos;s; Dismiss keeps it off for good; Ask for a
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
  );
}
