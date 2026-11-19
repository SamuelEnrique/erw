// Energy Research Warehouse (ERW) site, chain 507 (session 8900): what the findings audit of 19 November 2026 found for one
// draft at /internal/findings: its verdict, its four checks with their reasons, whether it is already known and who
// printed it, its second route, the tables it rests on with their license, and its Stata and Python files. The sheet's
// forty also carry SheetHead: rank, reader, sentence, chart, the one thing that would make it wrong, and the do-file to
// read or save in one click. Words on hover only (the page standard); nothing here approves a draft.
import { Tip } from "@/components/tool/ToolPage";
import type { AuditRow } from "@/lib/findingaudit";
import { KNOWN_TIPS, VERDICT_TIPS } from "@/lib/findingauditwords";

const GH = "https://github.com/SamuelEnrique/erw/blob/main/";
const RAW = "https://raw.githubusercontent.com/SamuelEnrique/erw/main/";
const STATE_MARK: Record<string, string> = { passed: "passed", fixed: "fixed", "not checked": "not checked", withdrawn: "withdrawn", "failed in part": "failed in part" };
const tipId = (id: string, part: string) => `${id}-${part}`.replace(/[^a-z0-9-]/gi, "-");

/** A repository file: read on GitHub, or save from its raw address. */
function RepoFile({ label, path, id }: { label: string; path: string; id: string }) {
  const name = path.split("/").pop() ?? path;
  return (
    <span className="whitespace-nowrap" data-audit-file={id}>
      {label}: <a href={GH + path} className="underline" target="_blank" rel="noreferrer">read</a>{" "}
      <a href={RAW + path} className="underline" download={name} target="_blank" rel="noreferrer">save</a>
    </span>
  );
}

export function AuditPanel({ id, row }: { id: string; row: AuditRow | null }) {
  if (!row) {
    return (
      <p className="mb-2 text-xs" data-audit="none" data-audit-id={id}>
        Audit of 19 November 2026: <strong>not covered</strong><Tip label="not covered" id={tipId(id, "none")}>{VERDICT_TIPS.none}</Tip>
      </p>
    );
  }
  return (
    <div className="mb-3 border border-rule bg-panel p-2 text-xs" data-audit={row.verdict} data-audit-id={id} data-audit-known={row.known.state}>
      <p className="flex flex-wrap gap-x-4 gap-y-1">
        <span>Audit of 19 November 2026: <strong data-audit-verdict={row.verdict}>{row.verdict}</strong><Tip label="the verdict" id={tipId(id, "v")}>{VERDICT_TIPS[row.verdict]}</Tip></span>
        <span>Already known: <strong>{row.known.state}</strong><Tip label="already known" id={tipId(id, "k")}>{row.known.detail || KNOWN_TIPS[row.known.state]}</Tip></span>
        {row.route2 ? <span data-audit-route2={row.route2.state}>Second route: <strong>{row.route2.state}</strong><Tip label="second route" id={tipId(id, "r")}>{row.route2.detail}</Tip></span> : null}
        {row.changed ? <span data-audit-changed="1">Mended by the audit<Tip label="what the audit mended" id={tipId(id, "c")}>{row.changed}</Tip></span> : null}
      </p>
      {row.checks.length ? (
        <ol className="mt-2 grid grid-cols-1 gap-px border border-rule bg-rule sm:grid-cols-4" data-audit-checks={row.checks.length}>
          {row.checks.map((c, i) => (
            <li key={c.name} className="bg-paper px-2 py-1" data-audit-check={i + 1} data-audit-check-state={c.state}>
              {i + 1}. {c.name}: <strong>{STATE_MARK[c.state] ?? c.state}</strong><Tip label={c.name} id={tipId(id, `c${i + 1}`)}>{c.why || "No reason recorded."}</Tip>
            </li>
          ))}
        </ol>
      ) : null}
      <p className="mt-2 break-words" data-audit-tables={row.tables.length}>
        Tables:{" "}
        {row.tables.map((t, i) => (
          <span key={t.name}>{i ? "; " : ""}<span className="font-mono">{t.name}</span> ({t.license === "public" ? "public" : <span data-audit-license={t.license}>{t.license}</span>})</span>
        ))}
      </p>
      <p className="mt-1 flex flex-wrap gap-x-4 gap-y-1">
        <RepoFile label="Stata do-file" path={row.files.do} id={`${id}-do`} />
        <RepoFile label="Python" path={row.files.py} id={`${id}-py`} />
        <span>The draft: <a href={GH + row.files.md} className="underline" target="_blank" rel="noreferrer">read</a></span>
      </p>
    </div>
  );
}

/** The head of one of the sheet's forty: rank and reader, the sentence, the chart, the risk, and the do-file to read here
 * or save, both without leaving the page. The chart is the draft's own picture from the review list's file route. */
export function SheetHead({ id, row }: { id: string; row: AuditRow }) {
  const s = row.sheet;
  if (!s) return null;
  const name = row.files.do.split("/").pop() ?? "reproduce.do";
  const href = `data:text/plain;charset=utf-8,${encodeURIComponent(s.do_text)}`;
  const picture = `/internal/findings/file?id=${encodeURIComponent(id)}&name=${encodeURIComponent(`${id}_1200x627.png`)}&show=1`;
  return (
    <div className="mb-3 text-sm" data-sheet-rank={s.rank} data-sheet-id={id}>
      <p className="text-xs">
        <strong>Sheet, number {s.rank}</strong> of 40; reader: {s.reader}
        <Tip label="why it matters" id={tipId(id, "why")}>{s.why || "No line on why it matters."}</Tip>
      </p>
      <h3 className="mt-1 text-lg leading-snug">{row.title}</h3>
      <p className="mt-1" data-sheet-sentence={id}>{row.sentence}</p>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={picture} alt={`Chart: ${row.title}`} loading="lazy" className="mt-2 h-auto w-full max-w-xl border border-rule" data-sheet-chart={id} />
      <dl className="mt-2 grid grid-cols-1 gap-x-4 gap-y-1 text-xs sm:grid-cols-[10rem_1fr]">
        <dt>The figure</dt><dd data-sheet-figure={id}>{s.figure}</dd>
        <dt>Compared with</dt><dd>{s.compared}</dd>
        <dt>What would make it wrong</dt><dd data-sheet-risk={id}>{s.risk}</dd>
      </dl>
      <details className="mt-2 text-xs" data-sheet-do={id}>
        <summary className="cursor-pointer">
          Stata do-file, <span className="font-mono">{name}</span>: read here{" "}
          <a href={href} download={name} className="ml-2 underline" data-sheet-do-save={id}>save</a>
        </summary>
        <pre className="mt-1 max-h-96 overflow-auto whitespace-pre-wrap break-words border border-rule bg-paper p-2" data-sheet-do-text={id}>{s.do_text}</pre>
      </details>
    </div>
  );
}
