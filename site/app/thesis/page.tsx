import type { Metadata } from "next";
import { cookies } from "next/headers";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteLink } from "@/components/SiteLink";
import { PitchbookPanel, type ProviderReceived } from "@/components/thesis/PitchbookPanel";
import { ReportTabs } from "@/components/thesis/Report";
import { RunForm } from "@/components/thesis/RunForm";
import { RunWatch } from "@/components/thesis/RunWatch";
import { COOKIE } from "@/lib/release";
import { FORCED_MARK, FORCED_NOTE } from "@/lib/thesis/niche";
import { heldOf, notMapped, notMappedOf, type ProviderPayload } from "@/lib/thesis/providers";
import { getProviderResults, getRun, internalOk, listRuns } from "@/lib/thesis/server";
import type { Run, RunRow } from "@/lib/thesis/types";
import { METHOD, arr, choiceOf, hrefOf, str, whenWords } from "@/lib/thesis/view";

// Session 135: Thesis Builder as a tool of the site. One page, one address: a niche is typed, a run is queued, and the
// report the server writes is drawn here in tabs, with the PitchBook stage's request and answer. Internal: in review
// (lib/release.ts), never indexed, never cached, never exported. The release gate is a curtain and not security, so the
// page checks the internal view's cookie itself; without it the address is not found. A run is read from the database
// through functions that check the internal token (migration 024); the public key reads nothing of the table.
// Nothing on the page says how a report is made: that is the Method note's, one link. The whole state is in the address.
// Session 150: the stage of the data providers takes PitchBook, Harmonic or Crunchbase (lib/thesis/providers.ts). The
// person chooses the provider in the panel before copying the request; the answers of the two new providers are read
// beside the run (migration 025) and the run's own row is read exactly as before.
export const metadata: Metadata = { title: "Thesis Builder", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const STATUS: Record<string, string> = { queued: "Queued", running: "Running", done: "Done", failed: "Failed" };
const PB: Record<string, string> = { received: "received", pending: "pending", none: "not asked" };
const GAP = "cursor-help whitespace-nowrap border-b border-dotted border-muted text-[11px] italic text-muted";

function Runs({ runs, selected }: { runs: RunRow[]; selected: string | null }) {
  if (!runs.length) return <p className="text-sm text-muted" data-thesis-runs="0">No run yet.</p>;
  return (
    <div className="max-h-[22rem] overflow-auto border border-rule">
      <table className="w-full min-w-[820px] border-collapse text-sm" data-thesis-runs={runs.length}>
        <thead>
          <tr className="sticky top-0 border-b border-rule bg-panel text-[10px] uppercase tracking-wide text-muted">
            <th className="py-1 pl-2 pr-3 text-left font-normal">Niche</th><th className="pr-3 text-left font-normal">Stage</th><th className="pr-3 text-left font-normal">Geography</th>
            <th className="pr-3 text-left font-normal">Status</th><th className="pr-3 text-left font-normal">Requested</th><th className="pr-3 text-right font-normal">Companies</th><th className="pr-2 text-left font-normal">PitchBook</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => { const id = str(r?.run_id), on = id === selected, status = str(r?.status);
            return (
              <tr key={id} className={`border-b border-rule/70 ${on ? "bg-paper" : "bg-white"}`} data-run={id} data-status={status} aria-current={on ? "true" : undefined}>
                <th scope="row" className="max-w-[26rem] py-1 pl-2 pr-3 text-left font-normal">
                  <Link href={hrefOf({ run: id, tab: "scope" })} className={`text-ink underline decoration-rule underline-offset-2 hover:text-accent ${on ? "font-semibold" : ""}`} title="Open this run">{str(r?.niche)}</Link>
                </th>
                <td className="pr-3 text-xs">{str(r?.stage)}</td>
                <td className="pr-3 text-xs">{str(r?.geography)}</td>
                <td className="whitespace-nowrap pr-3" title={status === "failed" ? str(r?.note) : undefined}>{STATUS[status] ?? status}</td>
                <td className="whitespace-nowrap pr-3 text-xs tabular-nums text-muted">{whenWords(str(r?.requested_at))}</td>
                <td className="pr-3 text-right tabular-nums">{status === "done" && typeof r?.companies === "number" ? r.companies : <span className={GAP} title={status === "failed" ? "The run failed." : "The run has not finished."} data-missing="not_held">{status === "failed" ? "none" : "not yet"}</span>}</td>
                <td className="whitespace-nowrap pr-2 text-xs">{PB[str(r?.pitchbook)] ?? ""}</td>
              </tr>
            ); })}
        </tbody>
      </table>
    </div>
  );
}

/** What the panel says of each answer of Harmonic or Crunchbase the run holds. */
function received(run: Run): ProviderReceived[] {
  return heldOf(run).filter((h) => h.provider !== "pitchbook").map((h) => {
    const p = h.payload as ProviderPayload;
    const all = [...arr(p.companies), ...arr(p.additional_companies)];
    const fields = [...notMapped(p.not_mapped), ...all.flatMap((c) => notMappedOf(c)), ...arr(p.lists).flatMap((l) => arr(l?.results).flatMap((r) => notMapped(r?.not_mapped)))];
    return { provider: h.provider, pulled_on: str(p.pulled_on), pasted_at: h.pasted_at, found: arr(p.companies).filter((c) => c?.found).length, asked: arr(p.companies).length,
      more: arr(p.additional_companies).filter((c) => c?.found).length, lists: arr(p.lists).length, not_mapped: fields.length };
  });
}

function Selected({ run, choice }: { run: Run; choice: ReturnType<typeof choiceOf> }) {
  const status = str(run.status);
  const report = run.report && typeof run.report === "object" ? run.report : null;
  return (
    <section className="mt-7" aria-label="The selected run" data-thesis-run={run.run_id} data-status={status}>
      <header className="mb-3 border-b border-rule pb-2">
        <h2 className="font-serif text-2xl text-accent">{str(run.niche)}
          {/* session 169: a run started with "Run anyway" on a niche the gate refused is flagged on its report */}
          {report?.gate?.forced === true ? <>{" "}<span className="cursor-help whitespace-nowrap rounded-sm border border-accent px-1 align-middle font-sans text-[10px] font-semibold uppercase tracking-wide text-accent" title={FORCED_NOTE} data-thesis-forced="1">{FORCED_MARK}</span></> : null}
        </h2>
        <p className="mt-0.5 text-xs text-muted">
          {[str(run.stage), str(run.geography)].filter(Boolean).join(", ")}{str(run.stage) || str(run.geography) ? " | " : ""}
          {STATUS[status] ?? status} | requested {whenWords(str(run.requested_at))}
          {run.finished_at ? ` | finished ${whenWords(str(run.finished_at))}` : run.started_at ? ` | started ${whenWords(str(run.started_at))}` : ""}
          {report?.built ? ` | report built ${whenWords(str(report.built))}` : ""}
        </p>
      </header>
      {status === "queued" || status === "running" ? <RunWatch runId={run.run_id} status={status} /> : null}
      {status === "failed" ? (
        <div className="mb-4 border border-accent bg-panel px-3 py-2 text-sm" role="alert" data-thesis-failed="1">
          <p className="font-semibold">The run failed.</p>
          {str(run.note) ? <p className="mt-0.5">{str(run.note)}</p> : null}
        </div>
      ) : null}
      {status === "done" ? <PitchbookPanel runId={run.run_id} niche={str(run.niche)} request={run.pitchbook_request ?? null} pitchbookKey={run.pitchbook_key ?? null} pitchbook={run.pitchbook ?? null} receivedAt={run.pitchbook_received_at ?? null} others={received(run)} /> : null}
      {report ? <ReportTabs run={run} choice={choice} /> : status === "done" ? <p className="text-sm text-muted" data-thesis-empty="1">This run holds no report.</p> : null}
    </section>
  );
}

export default async function Thesis({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  if (!(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();
  const choice = choiceOf(await searchParams);

  let runs: RunRow[] | null = null;
  try {
    runs = arr(await listRuns());
  } catch (e) {
    console.error(`[erw] thesis: the runs could not be read: ${(e as Error).message}`);
  }
  let run: Run | null = null;
  let unread = false;
  if (choice.run) {
    try {
      const got = await getRun(choice.run);
      run = got && typeof got === "object" && typeof got.run_id === "string" ? got : null;
    } catch (e) {
      unread = true;
      console.error(`[erw] thesis: the run could not be read: ${(e as Error).message}`);
    }
    if (run && run.status === "done") {
      // the answers of the providers beside PitchBook, kept beside the run. A database that does not hold their
      // store yet (migration 025) answers with an error: the run is then shown as it always was, PitchBook's alone.
      try {
        run = { ...run, providers: arr(await getProviderResults(run.run_id)) };
      } catch (e) {
        console.error(`[erw] thesis: the providers' answers could not be read: ${(e as Error).message}`);
      }
    }
  }

  return (
    <div className="border border-rule bg-white px-3 py-4 text-ink sm:px-5" data-thesis="1">
      <header className="mb-4 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-2">
        <h1 className="font-serif text-3xl text-accent">Thesis Builder</h1>
        <p className="text-xs text-muted"><SiteLink href={METHOD}>Method note</SiteLink>{" | "}<span>internal</span></p>
      </header>

      <section className="mb-6" aria-label="Ask for a run">
        <RunForm />
      </section>

      <section aria-label="Runs">
        <h2 className="mb-1 text-xs uppercase tracking-wide text-muted">Runs</h2>
        {runs ? <Runs runs={runs} selected={choice.run} /> : <p className="text-sm" role="alert" data-thesis-unread="1">Runs could not be read.</p>}
      </section>

      {run ? <Selected run={run} choice={choice} />
        : choice.run ? <p className="mt-6 text-sm" role="alert" data-thesis-norun="1">{unread ? "This run could not be read." : "No run is held under this address."}</p>
        : null}
    </div>
  );
}
